"""Incident and executive summary service for Chain Guard AI.

Consolidates shipment tracking, disruption detection, rerouting options,
fleet redeployment candidates, and cold-chain compliance into an executive briefing.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from . import data_loader
from . import disruption_service
from . import reroute_service
from . import fleet_service
from . import cold_chain_service


def build_incident_summary(shipment_id: str) -> Dict[str, Any]:
    """Synthesize a complete cross-functional incident dossier for an affected shipment.

    Answers:
    1. What happened? (Active disruption & geospatial impact)
    2. Which shipment is affected? (Shipment & cargo metadata)
    3. Why is it affected? (Specific proximity/waypoint intersection)
    4. How severe is the risk? (Severity & urgency rating)
    5. What route/carrier alternatives exist? (Optimized alternatives & tradeoffs)
    6. Which fleet assets can be redeployed? (Compatible idle assets nearby)
    7. Is there a cold-chain compliance issue? (Telemetry breach analysis & FDA/WHO status)
    8. What action is recommended? (Synthesized operational response)
    """
    shipment = data_loader.get_shipment_by_id(shipment_id)
    if not shipment:
        raise ValueError(f"Shipment {shipment_id} not found.")

    # 1. Disruption Matching
    disruption_impacts = disruption_service.get_disruptions_for_shipment(shipment_id)
    primary_disruption = disruption_impacts[0] if disruption_impacts else None

    # 2. Reroute Alternatives
    reroute_rec = reroute_service.generate_reroute_recommendation(
        shipment_id=shipment_id,
        disruption_id=primary_disruption.get("disruption_id") if primary_disruption else None,
    )

    # 3. Fleet Redeployment Candidates
    redeployment_candidates = fleet_service.find_redeployment_candidates_for_shipment(shipment_id)
    best_fleet_asset = redeployment_candidates[0] if redeployment_candidates else None

    # 4. Cold-Chain Compliance Assessment
    cold_chain_report = cold_chain_service.analyze_shipment_cold_chain(shipment_id)

    # 5. Composite Risk & Urgency
    disruption_severity = primary_disruption.get("disruption_severity", "NONE") if primary_disruption else "NONE"
    cold_chain_severity = cold_chain_report.get("severity", "NORMAL")

    if disruption_severity == "CRITICAL" or cold_chain_severity == "CRITICAL":
        overall_risk = "CRITICAL"
        recommended_priority = "P1_IMMEDIATE_ACTION"
    elif disruption_severity == "HIGH" or cold_chain_severity in ("MAJOR", "MODERATE"):
        overall_risk = "HIGH"
        recommended_priority = "P2_ELEVATED_RESPONSE"
    elif disruption_severity == "MEDIUM" or cold_chain_severity == "MINOR":
        overall_risk = "MEDIUM"
        recommended_priority = "P3_MONITOR_AND_PREPARE"
    else:
        overall_risk = "LOW"
        recommended_priority = "P4_ROUTINE"

    # 6. Synthesize Executive Narrative
    narrative_paragraphs = []
    
    cargo_name = shipment.get("cargo", {}).get("product_name", "Cargo")
    carrier = shipment.get("carrier", "Carrier")
    origin = shipment.get("origin", {}).get("name", "Origin")
    dest = shipment.get("destination", {}).get("name", "Destination")

    if primary_disruption:
        narrative_paragraphs.append(
            f"Shipment {shipment_id} ({cargo_name}) in transit from {origin} to {dest} via {carrier} "
            f"is actively impacted by {primary_disruption.get('disruption_title')}. "
            f"{primary_disruption.get('impact_reason')}"
        )
    else:
        narrative_paragraphs.append(
            f"Shipment {shipment_id} ({cargo_name}) is currently in transit from {origin} to {dest} "
            f"with no active route disruptions identified."
        )

    if cold_chain_report.get("is_cold_chain"):
        if cold_chain_report.get("excursion_detected"):
            narrative_paragraphs.append(
                f"COLD-CHAIN ALERT: A {cold_chain_report.get('severity')} thermal deviation has been detected. "
                f"Cargo observed temperatures reached {cold_chain_report.get('max_temperature_c')}°C "
                f"(Permitted envelope: {cold_chain_report.get('target_range')}). "
                f"Regulatory Status: {cold_chain_report.get('compliance_status')}."
            )
        else:
            narrative_paragraphs.append(
                f"Cold-chain integrity confirmed. Cargo temperature remains strictly within "
                f"regulatory envelope ({cold_chain_report.get('target_range')})."
            )

    if reroute_rec.get("recommended_route_id"):
        narrative_paragraphs.append(
            f"RECOMMENDED REROUTE: {reroute_rec.get('rationale')} "
            f"Estimated delay saved: {reroute_rec.get('delay_hours_saved')} hours."
        )

    if best_fleet_asset:
        narrative_paragraphs.append(
            f"REDEPLOYMENT ASSET: {best_fleet_asset.get('asset_name')} ({best_fleet_asset.get('asset_type')}) "
            f"is currently idle {best_fleet_asset.get('distance_km'):.1f} km away at "
            f"{best_fleet_asset.get('current_location', {}).get('name')}. {best_fleet_asset.get('reason')}"
        )

    return {
        "incident_id": f"INC-{shipment_id}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "shipment": {
            "shipment_id": shipment_id,
            "status": shipment.get("status"),
            "cargo_name": cargo_name,
            "cargo_type": shipment.get("cargo", {}).get("cargo_type"),
            "carrier": carrier,
            "origin": shipment.get("origin"),
            "destination": shipment.get("destination"),
            "current_location": shipment.get("current_location"),
            "eta": shipment.get("eta"),
        },
        "disruption": primary_disruption,
        "cold_chain": cold_chain_report,
        "reroute_recommendation": reroute_rec,
        "redeployment_candidates": redeployment_candidates,
        "executive_assessment": {
            "overall_risk_level": overall_risk,
            "action_priority": recommended_priority,
            "narrative_summary": " ".join(narrative_paragraphs),
            "primary_action_required": cold_chain_report.get("recommended_action") if cold_chain_report.get("excursion_detected") else reroute_rec.get("rationale"),
        },
    }
