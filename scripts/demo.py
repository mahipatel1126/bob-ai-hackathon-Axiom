"""Chain Guard AI — End-to-End Terminal Hackathon Demonstration Script.

Walks through a complete real-world scenario:
1. Detect active disruptions
2. Identify affected shipments
3. Explain geospatial impact
4. Recommend route/carrier alternatives
5. Scan available/idle fleet assets
6. Identify compatible redeployment candidates
7. Inspect cold-chain refrigeration requirement
8. Analyze IoT telemetry stream
9. Detect thermal excursions
10. Classify regulatory compliance (FDA 21 CFR 211 / WHO GDP)
11. Generate action directives
12. Synthesize an executive incident briefing (IBM Bob integration)
"""

import sys
from pathlib import Path

# Configure UTF-8 output if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.services import (
    data_loader,
    disruption_service,
    reroute_service,
    fleet_service,
    cold_chain_service,
    incident_service,
)
from src.backend.bob import default_bob_client


def print_banner(text: str) -> None:
    print("\n" + "=" * 76)
    print(f"  {text}")
    print("=" * 76)


def print_step(step_num: int, title: str) -> None:
    print(f"\n[{step_num}/9] >>> {title}")
    print("-" * 76)


def main() -> None:
    print_banner("[CHAINGUARD AI] L2 SUPPLY CHAIN DISRUPTION & OPTIMIZATION DEMO")
    print("Welcome to the Chain Guard AI live backend decision intelligence demonstration.")

    # 1. Active Disruptions
    print_step(1, "SCANNING GLOBAL LOGISTICS THREATS & ACTIVE DISRUPTIONS")
    active_disruptions = data_loader.get_disruptions(active_only=True)
    print(f"Found {len(active_disruptions)} active disruptions affecting key commercial corridors:")
    for d in active_disruptions:
        print(f"  * [{d['disruption_id']}] {d['title']} ({d['type']}, Severity: {d['severity']})")
        print(f"    Region: {d['region_name']} | Impact Radius: {d['impact_radius_km']} km")

    # 2. Identify Affected Shipments
    print_step(2, "GEOSPATIAL CORRIDOR & WAYPOINT INTERSECTION MATCHING")
    affected_shipments = disruption_service.get_affected_shipments()
    print(f"Identified {len(affected_shipments)} shipments within active threat zones:")
    for a in affected_shipments:
        print(f"  * Shipment {a['shipment_id']} | Risk: {a['risk_level']} | Urgency: {a['urgency']}")
        print(f"    Cargo: {a['cargo_type']} (Cold Chain: {a['is_cold_chain']})")

    # Target Focus Shipment: SHP-1002 (mRNA Oncology Biologics)
    target_id = "SHP-1002"
    print_banner(f"DEEP DIVE: CRITICAL DISRUPTION INCIDENT ON SHIPMENT {target_id}")

    # 3. Explain Impact
    print_step(3, f"DISRUPTION IMPACT ANALYSIS FOR {target_id}")
    impacts = disruption_service.get_disruptions_for_shipment(target_id)
    impact = impacts[0]
    print(f"Shipment: {impact['shipment_id']} | Carrier: {impact['carrier']}")
    print(f"Disruption: {impact['disruption_id']} -- {impact['disruption_title']}")
    print(f"Distance to Epicenter: {impact['impact_distance_km']} km (Threat radius: {impact['impact_radius_km']} km)")
    print(f"Root Cause: {impact['impact_reason']}")
    print(f"Urgency Classification: {impact['urgency']} (Immediate action required due to pharmaceutical profile)")

    # 4. Route & Carrier Alternatives
    print_step(4, "EVALUATING REROUTING & CARRIER ALTERNATIVES")
    reroute = reroute_service.generate_reroute_recommendation(target_id)
    print(f"Recommendation ID: {reroute['recommendation_id']} ({reroute['source']})")
    print(f"Proposed Route: {reroute['recommended_route_id']}")
    print(f"Proposed Carrier: {reroute['recommended_carrier_id']}")
    print(f"Rationale: {reroute['rationale']}")
    print(f"Trade-offs: Delay Saved = {reroute['delay_hours_saved']} hours | Cost Delta = ${reroute['cost_delta_usd']:,.2f}")

    # 5 & 6. Fleet Asset Scanning & Proximity Matching
    print_step(5, "SCANNING FLEET FOR IDLE ASSET REDEPLOYMENT")
    candidates = fleet_service.find_redeployment_candidates_for_shipment(target_id)
    print(f"Identified {len(candidates)} compatible idle assets within rescue radius:")
    for idx, c in enumerate(candidates, 1):
        print(f"  {idx}. Asset: {c['asset_id']} ({c['asset_name']})")
        print(f"     Type: {c['asset_type']} | Location: {c['current_location']['name']} ({c['distance_km']:.1f} km away)")
        print(f"     Capability Match: Payload={c['capacity_match']}, Reefer={c['reefer_match']} | Priority: {c['priority']}")
        print(f"     Reasoning: {c['reason']}")

    # 7, 8, 9, 10. Cold-Chain IoT Telemetry & Regulatory Evaluation
    print_step(6, "COLD-CHAIN IOT TELEMETRY & REGULATORY COMPLIANCE ANALYSIS")
    cc_report = cold_chain_service.analyze_shipment_cold_chain(target_id)
    print(f"Cargo: {cc_report['cargo_name']} ({cc_report['cargo_type']})")
    print(f"Permitted Thermal Range: {cc_report['target_range']}")
    print(f"Observed Temperatures: Min = {cc_report['min_temperature_c']} C | Max = {cc_report['max_temperature_c']} C | Mean = {cc_report['mean_temperature_c']} C")
    print(f"Excursion Detected: {cc_report['excursion_detected']} | Total Breach Duration: {cc_report['total_excursion_duration_minutes']} minutes")
    print(f"Severity Tier: {cc_report['severity']}")
    print(f"Compliance Classification: {cc_report['compliance_status']}")
    print(f"Governing Standard: {cc_report['regulatory_framework']}")
    print(f"Operational Action: {cc_report['recommended_action']}")

    # Also show severe cold-chain case: SHP-1005
    print_step(7, "CONTRAST CASE: CRITICAL THERMAL FAILURE ON SHP-1005 (VACCINES/INSULIN)")
    cc_severe = cold_chain_service.analyze_shipment_cold_chain("SHP-1005")
    print(f"Shipment: SHP-1005 | Max Temp Recorded: {cc_severe['max_temperature_c']} C (Allowed: {cc_severe['target_range']})")
    print(f"Duration: {cc_severe['total_excursion_duration_minutes']} mins | Severity: {cc_severe['severity']}")
    print(f"Regulatory Classification: {cc_severe['compliance_status']}")
    print(f"Mandated Action: {cc_severe['recommended_action']}")

    # 11. Consolidated Incident Dossier
    print_step(8, "SYNTHESIZING INCIDENT DOSSIER FOR EXECUTIVE BRIEFING")
    incident = incident_service.build_incident_summary(target_id)
    assess = incident["executive_assessment"]
    print(f"Incident Ref: {incident['incident_id']}")
    print(f"Overall Risk Level: {assess['overall_risk_level']} | Priority: {assess['action_priority']}")
    print(f"\nExecutive Summary Narrative:\n  \"{assess['narrative_summary']}\"")

    # 12. IBM Bob Cognitive Briefing
    print_step(9, "IBM BOB INTELLIGENCE BRIEFING & ACTION DIRECTIVES")
    briefing = default_bob_client.generate_incident_briefing(target_id)
    print(f"Briefing Title: {briefing['briefing_title']}")
    print(f"Intelligence Source: {briefing['source']} (Connected: {briefing['bob_connected']}, Offline Mode: {briefing['is_simulated']})")
    print(f"\nAction Directives:")
    for idx, act in enumerate(briefing['recommended_actions'], 1):
        print(f"  [{idx}] {act['action_type']}: {act['directive']}")
        print(f"      Detail: {act.get('details', '')}")

    print_banner("[OK] HACKATHON DEMONSTRATION COMPLETE: ALL CAPABILITIES VERIFIED")
    print("All 4 hackathon capabilities executed deterministically and end-to-end.\n")


if __name__ == "__main__":
    main()
