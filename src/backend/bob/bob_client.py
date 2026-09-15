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
        # Clean external caller using standard urllib.request
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
