"""IBM Bob / watsonx integration adapter for Chain Guard AI.

Provides disruption briefings, executive risk intelligence, and corrective
action recommendations. Operates with live IBM Bob/watsonx credentials if provided,
or seamlessly falls back to a deterministic local intelligence engine for offline execution.
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from ..services import incident_service


class BobClient:
    """Client adapter interface for IBM Bob and watsonx cognitive services."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("BOB_API_KEY") or os.getenv("WATSONX_API_KEY")
        self.endpoint = endpoint or os.getenv("BOB_API_ENDPOINT") or os.getenv("WATSONX_ENDPOINT")
        self.project_id = project_id or os.getenv("BOB_PROJECT_ID")
        self.has_credentials = bool(self.api_key and self.endpoint)

    def is_connected(self) -> bool:
        """Check whether live IBM Bob credentials are configured."""
        return self.has_credentials

    def generate_incident_briefing(self, shipment_id: str) -> Dict[str, Any]:
        """Generate an end-to-end incident briefing and executive action plan."""
        summary = incident_service.build_incident_summary(shipment_id)

        if self.has_credentials:
            try:
                return self._call_external_bob(summary)
            except Exception as e:
                # Log error and safely degrade to local fallback
                fallback = self._generate_local_fallback(summary)
                fallback["connection_error"] = str(e)
                return fallback
        else:
            return self._generate_local_fallback(summary)

    def generate_disruption_briefing(self, shipment_id: str) -> Dict[str, Any]:
        """Generate specifically the disruption impact section of the briefing."""
        full_briefing = self.generate_incident_briefing(shipment_id)
        return {
            "shipment_id": shipment_id,
            "briefing_type": "disruption_analysis",
            "source": full_briefing["source"],
            "disruption": full_briefing.get("disruption"),
            "situation_analysis": full_briefing.get("situation_analysis"),
            "risk_assessment": full_briefing.get("risk_assessment"),
        }

    def generate_corrective_actions(self, shipment_id: str) -> Dict[str, Any]:
        """Generate actionable mitigation and dispatch directives."""
        full_briefing = self.generate_incident_briefing(shipment_id)
        return {
            "shipment_id": shipment_id,
            "briefing_type": "action_directives",
            "source": full_briefing["source"],
            "action_priority": full_briefing.get("action_priority"),
            "recommended_actions": full_briefing.get("recommended_actions"),
            "dispatch_order_prepared": full_briefing.get("dispatch_order_prepared"),
        }

    def ask_bob(self, query: str, context_shipment_id: Optional[str] = None) -> Dict[str, Any]:
        """Process an operational inquiry from a logistics operator and return a load-bearing briefing."""
        # 1. Identify target shipment from context or query text
        target_id = context_shipment_id
        if not target_id:
            # Check for known shipment patterns in query
            all_shipments = data_loader.get_shipments()
            for s in all_shipments:
                sid = s.get("shipment_id", "")
                if sid.lower() in query.lower():
                    target_id = sid
                    break
        
        # Default to highest priority distressed shipment if not specified
        if not target_id:
            affected = disruption_service.get_affected_shipments()
            if affected:
                target_id = affected[0].get("shipment_id", "SHP-1002")
            else:
                target_id = "SHP-1002"

        # 2. If live IBM watsonx / Bob credentials exist, execute live cognitive call
        if self.has_credentials:
            try:
                summary = incident_service.build_incident_summary(target_id)
                summary["user_query"] = query
                return self._call_external_bob(summary)
            except Exception as e:
                return self._synthesize_conversational_response(query, target_id, error=str(e))
        else:
            return self._synthesize_conversational_response(query, target_id)

    def _synthesize_conversational_response(
        self, query: str, shipment_id: str, error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synthesize a structured conversational response using deterministic AI engine state."""
        try:
            summary = incident_service.build_incident_summary(shipment_id)
        except Exception:
            summary = {}

        shipment = summary.get("shipment", {})
        disruption = summary.get("disruption")
        cold_chain = summary.get("cold_chain", {})
        reroute = summary.get("reroute_recommendation", {})
        fleet_candidates = summary.get("redeployment_candidates", [])
        exec_assess = summary.get("executive_assessment", {})

        q_lower = query.lower()
        now_str = datetime.now(timezone.utc).strftime("%H:%M UTC")

        # Contextual response logic
        content_parts = []
        structured_rec = None
        suggested_actions = []

        if "why" in q_lower or "critical" in q_lower or "risk" in q_lower:
            content_parts.append(
                f"Incident Analysis for {shipment_id} ({shipment.get('cargo_name', 'Cargo')}):"
            )
            if disruption:
                content_parts.append(
                    f"• Obstruction: {disruption.get('disruption_title')} ({disruption.get('disruption_severity')}). {disruption.get('impact_reason')}"
                )
            if cold_chain.get("excursion_detected"):
                content_parts.append(
                    f"• Thermal Breach: Peak temperature {cold_chain.get('max_temperature_c')}°C exceeds {cold_chain.get('target_range')} threshold ({cold_chain.get('severity')} severity). Cumulative excursion: {cold_chain.get('total_excursion_duration_minutes')} mins."
                )
            
            structured_rec = {
                "priority": "CRITICAL" if exec_assess.get("overall_risk_level") == "CRITICAL" else "HIGH",
                "shipment_id": shipment_id,
                "reason": disruption.get("disruption_title", "Transit hazard") if disruption else "Cold chain breach",
                "recommended_action": f"Execute corridor bypass via '{reroute.get('recommended_route_id', 'Alternative Route')}' and enforce destination quarantine review.",
                "operational_impact": f"Saves {reroute.get('delay_hours_saved', 0.0)}h in transit delay and mitigates temperature excursion.",
            }
            suggested_actions = [
                f"Inspect {shipment_id} Audit Dossier",
                "Approve Alternate Reroute",
                "Dispatch Standby Reefer",
            ]

        elif "route" in q_lower or "reroute" in q_lower or "corridor" in q_lower:
            route_id = reroute.get("recommended_route_id", "ALT-01")
            delay_saved = reroute.get("delay_hours_saved", 0.0)
            content_parts.append(
                f"Routing Optimization Analysis for {shipment_id}: {reroute.get('rationale', 'Alternative bypass route evaluated.')}"
            )
            content_parts.append(
                f"Projected impact: Avoids active hazard corridor, saving {delay_saved} hours of transit delay."
            )
            structured_rec = {
                "priority": "HIGH",
                "shipment_id": shipment_id,
                "reason": "Active corridor disruption avoidance",
                "recommended_action": f"Authorize dispatch order via {route_id}.",
                "operational_impact": f"Estimated transit savings: {delay_saved}h.",
            }
            suggested_actions = [
                "Authorize Reroute Order",
                "Notify Receiving Facility",
                "View Route Comparison Map",
            ]

        elif "fleet" in q_lower or "redeploy" in q_lower or "truck" in q_lower or "asset" in q_lower or "idle" in q_lower:
            if fleet_candidates:
                top_asset = fleet_candidates[0]
                content_parts.append(
                    f"Fleet Redeployment Recommendation: Standby asset {top_asset.get('asset_id')} ({top_asset.get('asset_name')}) is currently IDLE at {top_asset.get('current_location', {}).get('name', 'Depot')}, {top_asset.get('distance_km'):.1f} km away."
                )
                content_parts.append(
                    f"Compatibility verified: Weight capacity {top_asset.get('capacity_match')} | Cold-chain compliant {top_asset.get('reefer_match')}. Assigned standby driver: {top_asset.get('available_driver')}."
                )
                structured_rec = {
                    "priority": "HIGH",
                    "shipment_id": shipment_id,
                    "reason": "Refrigeration backup and cargo rescue dispatch",
                    "recommended_action": f"Issue autonomous redeployment order for {top_asset.get('asset_id')}.",
                    "operational_impact": "Prevents product degradation and maintains customer SLA.",
                }
                suggested_actions = [
                    f"Dispatch {top_asset.get('asset_id')}",
                    "View Driver Telemetry",
                    "Acknowledge Fleet Alert",
                ]
            else:
                content_parts.append("Fleet analysis: All nearby fleet assets are currently deployed or undergoing maintenance.")
                structured_rec = {
                    "priority": "MEDIUM",
                    "shipment_id": shipment_id,
                    "reason": "No proximate idle assets within 600km radius",
                    "recommended_action": "Request 3PL secondary carrier spot quote.",
                    "operational_impact": "Ensures continuity through external carrier network.",
                }

        elif "cold" in q_lower or "temp" in q_lower or "telemetry" in q_lower or "excursion" in q_lower:
            content_parts.append(
                f"Thermal Telemetry & Compliance Review for {shipment_id}: Recorded max temperature of {cold_chain.get('max_temperature_c', 'N/A')}°C vs specification {cold_chain.get('target_range', '2-8°C')}."
            )
            content_parts.append(
                f"Regulatory Classification: {cold_chain.get('compliance_status', 'COMPLIANT')} ({cold_chain.get('regulatory_framework', 'FDA 21 CFR 211')}). Directive: {cold_chain.get('recommended_action', 'Continue standard monitoring.')}"
            )
            structured_rec = {
                "priority": "CRITICAL" if cold_chain.get("severity") == "CRITICAL" else "HIGH",
                "shipment_id": shipment_id,
                "reason": f"Thermal integrity excursion ({cold_chain.get('severity')})",
                "recommended_action": cold_chain.get("recommended_action", "Enforce QA quarantine hold."),
                "operational_impact": "Prevents adulterated biologics from clinical distribution.",
            }
            suggested_actions = [
                f"Generate FDA 21 CFR 211 Audit Dossier",
                "Enforce Quarantine Hold",
                "Dispatch Backup Reefer",
            ]

        else:
            content_parts.append(
                f"Operations Copilot Intelligence Briefing: Monitoring active supply chain network state. Current focus on {shipment_id} ({shipment.get('cargo_name', 'Biologics')})."
            )
            if disruption:
                content_parts.append(f"Primary transit hazard: {disruption.get('disruption_title')}.")
            content_parts.append(f"Executive assessment: {exec_assess.get('narrative_summary', 'All corridors actively monitored.')}")
            structured_rec = {
                "priority": exec_assess.get("overall_risk_level", "MEDIUM"),
                "shipment_id": shipment_id,
                "reason": "Network disruption and risk containment",
                "recommended_action": exec_assess.get("primary_action_required", "Review active recommendations."),
                "operational_impact": "Maintains network-wide supply chain resilience.",
            }
            suggested_actions = [
                "Review Critical Shipments",
                "View Disruption Map",
                "Optimize Fleet Allocation",
            ]

        return {
            "id": f"bob-{datetime.now(timezone.utc).timestamp()}",
            "sender": "BOB",
            "timestamp": now_str,
            "source": "ibm_bob_local_engine",
            "bob_connected": False,
            "is_simulated": True,
            "content": "\n\n".join(content_parts),
            "structured_recommendation": structured_rec,
            "suggested_actions": suggested_actions,
            "context_shipment_id": shipment_id,
        }

    def _generate_local_fallback(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic local briefing generator mimicking IBM Bob reasoning."""
        shipment = summary.get("shipment", {})
        disruption = summary.get("disruption")
        cold_chain = summary.get("cold_chain", {})
        reroute = summary.get("reroute_recommendation", {})
        fleet_candidates = summary.get("redeployment_candidates", [])
        exec_assess = summary.get("executive_assessment", {})

        shipment_id = shipment.get("shipment_id", "UNKNOWN")
        cargo_name = shipment.get("cargo_name", "Freight")
        risk_level = exec_assess.get("overall_risk_level", "MEDIUM")

        # Synthesize situation breakdown
        situation = []
        if disruption:
            situation.append(
                f"Active disruption '{disruption.get('disruption_title')}' ({disruption.get('disruption_type')}, "
                f"Severity: {disruption.get('disruption_severity')}) is obstructing the transit corridor. "
                f"{disruption.get('impact_reason')}"
            )
        else:
            situation.append("No active external route disruptions detected.")

        if cold_chain.get("is_cold_chain"):
            if cold_chain.get("excursion_detected"):
                situation.append(
                    f"Thermal stability breach detected: recorded max temperature of {cold_chain.get('max_temperature_c')}°C "
                    f"exceeded permitted {cold_chain.get('target_range')} range. Cumulative breach duration: "
                    f"{cold_chain.get('total_excursion_duration_minutes')} minutes."
                )
            else:
                situation.append("Cold chain integrity is intact; all sensor streams report within approved envelope.")

        # Synthesize actionable directives
        actions = []
        if reroute.get("recommended_route_id"):
            actions.append({
                "action_type": "CORRIDOR_REROUTE",
                "directive": f"Execute bypass route '{reroute.get('recommended_route_id')}'.",
                "details": reroute.get("rationale"),
                "delay_avoided_hours": reroute.get("delay_hours_saved"),
            })

        if fleet_candidates:
            top_asset = fleet_candidates[0]
            actions.append({
                "action_type": "ASSET_REDEPLOYMENT",
                "directive": f"Dispatch standby asset {top_asset.get('asset_id')} ({top_asset.get('asset_name')}).",
                "details": (
                    f"Asset is idle {top_asset.get('distance_km'):.1f} km away with verified capacity "
                    f"and reefer capability. {top_asset.get('reason')}"
                ),
                "assigned_driver": top_asset.get("available_driver"),
            })

        if cold_chain.get("excursion_detected"):
            actions.append({
                "action_type": "REGULATORY_QUARANTINE_HOLD",
                "directive": "Enforce regulatory quarantine hold upon destination arrival.",
                "details": cold_chain.get("recommended_action"),
                "regulatory_standard": cold_chain.get("regulatory_framework"),
            })

        return {
            "incident_id": summary.get("incident_id"),
            "shipment_id": shipment_id,
            "briefing_title": f"ChainGuard Incident Briefing: {cargo_name} ({shipment_id})",
            "source": "local_fallback_engine",
            "bob_connected": False,
            "is_simulated": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "executive_summary": exec_assess.get("narrative_summary"),
            "risk_assessment": {
                "risk_level": risk_level,
                "urgency": disruption.get("urgency", "MEDIUM") if disruption else "LOW",
                "cold_chain_severity": cold_chain.get("severity", "NORMAL"),
                "compliance_status": cold_chain.get("compliance_status", "COMPLIANT"),
            },
            "situation_analysis": situation,
            "action_priority": exec_assess.get("action_priority"),
            "recommended_actions": actions,
            "dispatch_order_prepared": len(fleet_candidates) > 0,
            "disruption": disruption,
            "reroute_option": {
                "route_id": reroute.get("recommended_route_id"),
                "carrier_id": reroute.get("recommended_carrier_id"),
                "estimated_delay_saved": reroute.get("delay_hours_saved"),
            } if reroute else None,
        }

    def _call_external_bob(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a real API call to IBM Bob / watsonx when credentials are provided."""
        import urllib.request
        import urllib.error

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "project_id": self.project_id,
            "task": "logistics_disruption_briefing",
            "incident_data": summary,
        }

        req = urllib.request.Request(
            url=self.endpoint,  # type: ignore
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=10.0) as response:
            result_data = json.loads(response.read().decode("utf-8"))
            return {
                "incident_id": summary.get("incident_id"),
                "shipment_id": summary.get("shipment", {}).get("shipment_id"),
                "source": "ibm_bob_watsonx_live",
                "bob_connected": True,
                "is_simulated": False,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "response": result_data,
            }


# Default global instance
default_bob_client = BobClient()

