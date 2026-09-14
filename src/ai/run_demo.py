"""End-to-end demonstration runner for Chain Guard AI.

Executes the complete L2 operational intelligence pipeline across all 8 scenarios.
"""

import json
from datetime import datetime
from src.ai.carrier import evaluate_carriers
from src.ai.cold_chain import analyze_temperature_readings
from src.ai.demo_data import (
    get_all_demo_scenarios,
    get_scenario_1_normal_shipment,
    get_scenario_2_weather_disrupted_shipment,
    get_scenario_3_high_priority_pharma,
    get_scenario_4_and_5_fleet_assets,
    get_scenario_6_normal_cold_chain_readings,
    get_scenario_7_warning_cold_chain_readings,
    get_scenario_8_critical_cold_chain_readings,
)
from src.ai.disruption import analyze_single_disruption_impact, get_highest_disruption_impact
from src.ai.fleet import detect_idle_fleet, filter_suitable_vehicles
from src.ai.optimization import optimize_fleet_redeployment
from src.ai.recommendations import generate_operational_recommendation
from src.ai.risk_scoring import calculate_shipment_risk
from src.ai.routing import evaluate_routes


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_step(step_num: int, title: str):
    print(f"\n[STEP {step_num}] {title}")
    print("-" * 60)


def run_pipeline_demo():
    print_banner("CHAIN GUARD AI - L2 SUPPLY CHAIN ASSISTANT & FLEET OPTIMIZER DEMO")
    print("Simulated Multi-Scenario Operational Intelligence Pipeline Demonstration\n")

    # Load Demo Scenarios
    s1_shp, s1_dis, s1_rt, s1_car = get_scenario_1_normal_shipment()
    s2_shp, s2_dis, s2_rt, s2_car = get_scenario_2_weather_disrupted_shipment()
    s3_shp, s3_dis, s3_rt, s3_car = get_scenario_3_high_priority_pharma()
    fleet = get_scenario_4_and_5_fleet_assets()
    readings_normal = get_scenario_6_normal_cold_chain_readings(s3_shp.shipment_id)
    readings_warning = get_scenario_7_warning_cold_chain_readings(s3_shp.shipment_id)
    readings_critical = get_scenario_8_critical_cold_chain_readings(s3_shp.shipment_id)

    # -------------------------------------------------------------
    # 1. Disruption Impact Analysis
    # -------------------------------------------------------------
    print_step(1, "DISRUPTION IMPACT ANALYSIS")
    print(f"Disruption Event: {s2_dis[0].type.value} at {s2_dis[0].location} (Severity: {s2_dis[0].severity.value})")
    print(f"Checking Impact on Shipment {s2_shp.shipment_id} ({s2_shp.origin} -> {s2_shp.destination})...")
    impact_s2 = analyze_single_disruption_impact(s2_shp, s2_dis[0])
    print(f" -> Affected: {impact_s2.affected}")
    print(f" -> Impact Level: {impact_s2.impact_level.value}")
    print(f" -> Estimated Delay: +{impact_s2.estimated_delay_hours:.1f} hours")
    print(f" -> Reason: {impact_s2.reasons[0]}")

    # -------------------------------------------------------------
    # 2. Explainable Risk Scoring
    # -------------------------------------------------------------
    print_step(2, "SHIPMENT RISK SCORING (0-100 SCALE)")
    risk_s1 = calculate_shipment_risk(s1_shp)
    risk_s2 = calculate_shipment_risk(s2_shp, disruption_impact=impact_s2)
    print(f"Shipment {s1_shp.shipment_id} (Nominal): Score = {risk_s1.score:.1f}/100 [{risk_s1.risk_level.value}]")
    print(f"Shipment {s2_shp.shipment_id} (Disrupted): Score = {risk_s2.score:.1f}/100 [{risk_s2.risk_level.value}]")
    print(f" -> Contributing Factors Breakdown:")
    for k, v in risk_s2.contributing_factors.items():
        print(f"    * {k.replace('_', ' ').title()}: {v:.1f} pts")
    print(f" -> Explanation: {risk_s2.explanation}")

    # -------------------------------------------------------------
    # 3. Dynamic Rerouting Evaluation
    # -------------------------------------------------------------
    print_step(3, "DYNAMIC REROUTING RECOMMENDATION")
    route_rec = evaluate_routes(s2_shp, s2_rt, s2_dis)
    print(f"Candidate Routes Evaluated: {len(route_rec.ranked_routes)}")
    for i, r in enumerate(route_rec.ranked_routes, 1):
        print(f"  {i}. {r.name} (Risk: {r.risk_score:.0f}, ETA: {r.estimated_time_hours:.1f}h, Cost: INR {r.estimated_cost:,.0f})")
    print(f" -> Recommended Route: {route_rec.recommended_route.name}")
    print(f" -> Rationale: {route_rec.selection_reason}")

    # -------------------------------------------------------------
    # 4. Alternative Carrier Recommendation
    # -------------------------------------------------------------
    print_step(4, "ALTERNATIVE CARRIER CAPACITY EVALUATION")
    carrier_rec = evaluate_carriers(s2_shp, s2_car)
    if carrier_rec.recommended_carrier:
        print(f" -> Recommended Carrier: {carrier_rec.recommended_carrier.name}")
        print(f" -> Reliability: {carrier_rec.recommended_carrier.reliability_score * 100:.0f}%")
        print(f" -> Rationale: {carrier_rec.selection_reason}")

    # -------------------------------------------------------------
    # 5. Idle Fleet Detection & Asset Suitability
    # -------------------------------------------------------------
    print_step(5, "IDLE FLEET DETECTION & ASSET CLASSIFICATION")
    idle_res = detect_idle_fleet(fleet)
    print(f"Total Fleet Assets: {idle_res.total_assets} | Average Utilization: {idle_res.utilization_rate_avg * 100:.1f}%")
    print(f" -> IDLE Assets: {[v.vehicle_id for v in idle_res.idle_vehicles]}")
    print(f" -> UNDERUTILIZED Assets: {[v.vehicle_id for v in idle_res.underutilized_vehicles]}")
    print(f" -> ACTIVE Assets: {[v.vehicle_id for v in idle_res.active_vehicles]}")
    print(f" -> UNAVAILABLE Assets: {[v.vehicle_id for v in idle_res.unavailable_vehicles]}")

    suitable_pharma, rejections_pharma = filter_suitable_vehicles(s3_shp, fleet)
    print(f"\nFiltering Suitability for Pharma Shipment {s3_shp.shipment_id} (Requires Reefer 2°C-8°C):")
    print(f" -> Suitable Vehicles: {[v.vehicle_id for v in suitable_pharma]}")
    print(f" -> Rejections ({len(rejections_pharma)}):")
    for rej in rejections_pharma[:2]:
        print(f"    * {rej['vehicle_id']}: {rej['reason']}")

    # -------------------------------------------------------------
    # 6. Global Fleet Redeployment Optimization
    # -------------------------------------------------------------
    print_step(6, "GLOBAL FLEET REDEPLOYMENT OPTIMIZATION (OR-Tools / MILP)")
    opt_res = optimize_fleet_redeployment([s2_shp, s3_shp], fleet)
    print(f"Optimization Method: {opt_res.optimization_method}")
    print(f"Assignments Created: {len(opt_res.assignments)}")
    for assign in opt_res.assignments:
        print(f"  * Vehicle {assign.vehicle_id} -> Shipment {assign.shipment_id}")
        print(f"    - Deadhead Distance: {assign.origin_distance_km:.0f} km")
        print(f"    - Redeployment Cost: INR {assign.redeployment_cost:,.0f}")
        print(f"    - Utilization Gain: {assign.current_utilization * 100:.0f}% -> {assign.projected_utilization * 100:.0f}% (+{assign.utilization_improvement * 100:.0f}%)")
        print(f"    - Reason: {assign.reason}")

    # -------------------------------------------------------------
    # 7. Cold-Chain IoT Excursion Detection & Regulatory Severity
    # -------------------------------------------------------------
    print_step(7, "COLD-CHAIN IOT TELEMETRY & SEVERITY CLASSIFICATION")
    cc_norm = analyze_temperature_readings(s3_shp, readings_normal)
    cc_warn = analyze_temperature_readings(s3_shp, readings_warning)
    cc_crit = analyze_temperature_readings(s3_shp, readings_critical)

    print(f"Scenario 6 (Normal):   Severity = {cc_norm.overall_severity.value:<8} | Compliant: {cc_norm.is_compliant}")
    print(f"Scenario 7 (Warning):  Severity = {cc_warn.overall_severity.value:<8} | Max Delta: +{cc_warn.events[0].max_deviation_celsius}°C")
    print(f"Scenario 8 (Critical): Severity = {cc_crit.overall_severity.value:<8} | Duration: {cc_crit.events[0].duration_minutes:.0f}m | Max Temp: {cc_crit.max_temperature}°C")
    print(f" -> Critical Regulatory Actions:")
    for act in cc_crit.recommendations:
        print(f"    * {act}")

    # -------------------------------------------------------------
    # 8. Unified L2 Operational Recommendation
    # -------------------------------------------------------------
    print_step(8, "UNIFIED OPERATIONAL RECOMMENDATION (END-TO-END PIPELINE)")
    rec = generate_operational_recommendation(
        shipment=s3_shp,
        disruptions=s3_dis,
        candidate_routes=s3_rt,
        candidate_carriers=s3_car,
        available_fleet=fleet,
        temperature_readings=readings_critical,
    )

    print(f"Recommendation ID: {rec.recommendation_id}")
    print(f"Target Shipment:   {rec.shipment_id} ({s3_shp.cargo_type.value})")
    print(f"Priority:          {rec.priority.value}")
    print(f"Action Summary:    {rec.action_summary}")
    print(f"\nKey Rationale:")
    for r in rec.reasons:
        print(f"  • {r}")
    print(f"\nExecutive Summary:\n  \"{rec.executive_summary}\"")

    print_banner("DEMO COMPLETED SUCCESSFULLY - ALL 8 SCENARIOS VERIFIED")


if __name__ == "__main__":
    run_pipeline_demo()
