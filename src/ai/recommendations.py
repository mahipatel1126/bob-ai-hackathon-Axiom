"""Unified operational recommendation pipeline for L2 Supply Chain Disruption & Fleet Assistant."""

from datetime import datetime, timezone
import uuid
from typing import Dict, List, Optional
from src.ai.cold_chain import analyze_temperature_readings
from src.ai.config import AIConfig, DEFAULT_CONFIG
from src.ai.carrier import evaluate_carriers
from src.ai.disruption import get_highest_disruption_impact
from src.ai.optimization import optimize_fleet_redeployment
from src.ai.risk_scoring import calculate_shipment_risk
from src.ai.routing import evaluate_routes
from src.ai.schemas import (
    CarrierOption,
    CarrierRecommendationResult,
    ColdChainAnalysisResult,
    Disruption,
    DisruptionImpactResult,
    FleetAsset,
    FleetAssignment,
    OperationalRecommendation,
    PriorityLevel,
    RiskLevel,
    RiskScoreResult,
    RouteOption,
    RouteRecommendationResult,
    Shipment,
    TemperatureReading,
    TemperatureSeverity,
)


def generate_operational_recommendation(
    shipment: Shipment,
    disruptions: Optional[List[Disruption]] = None,
    candidate_routes: Optional[List[RouteOption]] = None,
    candidate_carriers: Optional[List[CarrierOption]] = None,
    available_fleet: Optional[List[FleetAsset]] = None,
    temperature_readings: Optional[List[TemperatureReading]] = None,
    current_time: Optional[datetime] = None,
    config: Optional[AIConfig] = None,
) -> OperationalRecommendation:
    """Generate a single unified, explainable L2 operational recommendation for a shipment.
    
    Pipeline Steps:
    1. Disruption Impact Analysis
    2. Cold-Chain Excursion & Severity Audit
    3. Multi-Factor Explainable Risk Scoring
    4. Route Evaluation & Alternative Rerouting
    5. Alternative Carrier Capacity Evaluation
    6. Fleet Redeployment Optimization
    7. Unified Operational Synthesis & Executive Action
    """
    cfg = config or DEFAULT_CONFIG
    now = current_time or datetime.now(timezone.utc).replace(tzinfo=None)
    disruptions_list = disruptions or []
    rec_id = f"REC-{shipment.shipment_id}-{uuid.uuid4().hex[:6].upper()}"

    # 1. Disruption Analysis
    impact = get_highest_disruption_impact(shipment, disruptions_list, current_time=now)

    # 2. Cold-Chain Analysis
    cold_chain_res: Optional[ColdChainAnalysisResult] = None
    if shipment.temperature_required or (temperature_readings and len(temperature_readings) > 0):
        cold_chain_res = analyze_temperature_readings(shipment, temperature_readings or [], cfg)

    # 3. Risk Assessment
    risk = calculate_shipment_risk(
        shipment=shipment,
        disruption_impact=impact,
        cold_chain_status=cold_chain_res,
        current_time=now,
        config=cfg,
    )

    # 4. Route Evaluation
    route_rec: Optional[RouteRecommendationResult] = None
    if candidate_routes:
        route_rec = evaluate_routes(shipment, candidate_routes, disruptions_list, cfg)

    # 5. Carrier Recommendation
    carrier_rec: Optional[CarrierRecommendationResult] = None
    if candidate_carriers:
        carrier_rec = evaluate_carriers(shipment, candidate_carriers, cfg)

    # 6. Fleet Redeployment
    fleet_assignment: Optional[FleetAssignment] = None
    if available_fleet and risk.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
        opt_res = optimize_fleet_redeployment([shipment], available_fleet, cfg)
        if opt_res.assignments:
            fleet_assignment = opt_res.assignments[0]

    # 7. Action Synthesis
    action_parts: List[str] = []
    reasons: List[str] = []

    # Priority determination
    op_priority = risk.mitigation_urgency
    if cold_chain_res and cold_chain_res.overall_severity == TemperatureSeverity.CRITICAL:
        op_priority = PriorityLevel.CRITICAL

    # Compose Action Summary & Explanations
    if impact.affected:
        reasons.append(
            f"Active disruption '{impact.disruption_id}' threatens transit timeline (+{impact.estimated_delay_hours:.1f}h delay)."
        )
    
    if cold_chain_res and cold_chain_res.has_excursions:
        reasons.append(
            f"Cold-chain temperature excursion detected ({cold_chain_res.overall_severity.value}, max deviation: {cold_chain_res.events[0].max_deviation_celsius}°C)."
        )

    if route_rec and route_rec.recommended_route:
        # Check if recommended route avoids disruption
        if route_rec.recommended_route.risk_score < 30.0:
            action_parts.append(f"Reroute via '{route_rec.recommended_route.name}'")
            reasons.append(f"Recommended route bypasses hazard corridor ({route_rec.recommended_route.distance_km:.0f} km, {route_rec.recommended_route.estimated_time_hours:.1f}h).")
        else:
            action_parts.append(f"Proceed with monitored alternative '{route_rec.recommended_route.name}'")

    if fleet_assignment:
        action_parts.append(f"dispatch backup {fleet_assignment.vehicle_type.value} ({fleet_assignment.vehicle_id}) from {fleet_assignment.origin_distance_km:.0f}km away")
        reasons.append(f"Idle fleet asset {fleet_assignment.vehicle_id} redeployed (+{fleet_assignment.utilization_improvement * 100:.0f}% utilization gain).")
    elif carrier_rec and carrier_rec.recommended_carrier:
        action_parts.append(f"allocate overflow volume to carrier '{carrier_rec.recommended_carrier.name}'")
        reasons.append(f"Partner carrier '{carrier_rec.recommended_carrier.name}' selected with {carrier_rec.recommended_carrier.reliability_score * 100:.0f}% reliability.")

    if not action_parts:
        if risk.risk_level == RiskLevel.LOW:
            action_summary = "Maintain current transit schedule. Nominal operating conditions."
            reasons.append("No active disruptions or temperature excursions detected on current route.")
        else:
            action_summary = "Monitor shipment closely and alert local dispatch supervisor."
            reasons.append("Risk elevated but no alternative route or fleet asset is currently available.")
    else:
        action_summary = " and ".join(action_parts).capitalize() + "."

    # Executive narrative summary
    executive_summary = (
        f"Shipment {shipment.shipment_id} ({shipment.cargo_type.value}, {shipment.origin} -> {shipment.destination}) "
        f"is assessed at Risk Score {risk.score:.1f}/100 ({risk.risk_level.value}). "
        f"Primary Recommendation: {action_summary} "
        f"Action Priority: {op_priority.value}."
    )

    return OperationalRecommendation(
        recommendation_id=rec_id,
        shipment_id=shipment.shipment_id,
        timestamp=now,
        action_summary=action_summary,
        priority=op_priority,
        reasons=reasons,
        impact_analysis=impact,
        risk_assessment=risk,
        route_recommendation=route_rec,
        carrier_recommendation=carrier_rec,
        fleet_assignment=fleet_assignment,
        cold_chain_status=cold_chain_res,
        executive_summary=executive_summary,
    )


def generate_batch_recommendations(
    shipments: List[Shipment],
    disruptions: Optional[List[Disruption]] = None,
    candidate_routes_map: Optional[Dict[str, List[RouteOption]]] = None,
    candidate_carriers_map: Optional[Dict[str, List[CarrierOption]]] = None,
    available_fleet: Optional[List[FleetAsset]] = None,
    temperature_readings_map: Optional[Dict[str, List[TemperatureReading]]] = None,
    current_time: Optional[datetime] = None,
    config: Optional[AIConfig] = None,
) -> List[OperationalRecommendation]:
    """Execute end-to-end intelligence analysis for multiple shipments with global fleet optimization."""
    cfg = config or DEFAULT_CONFIG
    disruptions_list = disruptions or []
    routes_map = candidate_routes_map or {}
    carriers_map = candidate_carriers_map or {}
    readings_map = temperature_readings_map or {}

    # 1. First Pass: Analyze individual risk for each shipment
    preliminary_data = []
    at_risk_shipments: List[Shipment] = []

    for shp in shipments:
        impact = get_highest_disruption_impact(shp, disruptions_list, current_time)
        readings = readings_map.get(shp.shipment_id, [])
        cc_res = analyze_temperature_readings(shp, readings, cfg) if (shp.temperature_required or readings) else None
        risk = calculate_shipment_risk(shp, impact, cc_res, current_time, cfg)
        
        if risk.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            at_risk_shipments.append(shp)

        preliminary_data.append((shp, impact, cc_res, risk))

    # 2. Global Fleet Optimization across all at-risk shipments
    fleet_assignments_map: Dict[str, FleetAssignment] = {}
    if available_fleet and at_risk_shipments:
        opt_result = optimize_fleet_redeployment(at_risk_shipments, available_fleet, cfg)
        for assignment in opt_result.assignments:
            fleet_assignments_map[assignment.shipment_id] = assignment

    # 3. Final Assembly
    recommendations: List[OperationalRecommendation] = []
    for shp, impact, cc_res, risk in preliminary_data:
        routes = routes_map.get(shp.shipment_id, [])
        carriers = carriers_map.get(shp.shipment_id, [])
        readings = readings_map.get(shp.shipment_id, [])

        route_rec = evaluate_routes(shp, routes, disruptions_list, cfg) if routes else None
        carrier_rec = evaluate_carriers(shp, carriers, cfg) if carriers else None
        fleet_assign = fleet_assignments_map.get(shp.shipment_id)

        # Single recommendation assembly
        rec = generate_operational_recommendation(
            shipment=shp,
            disruptions=disruptions_list,
            candidate_routes=routes,
            candidate_carriers=carriers,
            available_fleet=available_fleet,
            temperature_readings=readings,
            current_time=current_time,
            config=cfg,
        )
        # Override fleet assignment with global optimal match if available
        if fleet_assign:
            rec = rec.model_copy(update={"fleet_assignment": fleet_assign})

        recommendations.append(rec)

    return recommendations
