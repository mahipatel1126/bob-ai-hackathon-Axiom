"""REST API routing and controller logic for Chain Guard AI."""

import json
import re
from typing import Dict, Any, Tuple, Optional
from urllib.parse import parse_qs, urlparse

from ..services import (
    data_loader,
    disruption_service,
    reroute_service,
    fleet_service,
    cold_chain_service,
    incident_service,
)
from ..bob import default_bob_client


def route_request(
    method: str,
    raw_path: str,
    body: Optional[Dict[str, Any]] = None,
) -> Tuple[int, Dict[str, Any]]:
    """Route an incoming HTTP request to the corresponding service handler.

    Returns:
        (status_code, response_dict)
    """
    parsed = urlparse(raw_path)
    path = parsed.path.rstrip("/")
    if not path:
        path = "/"
    query_params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

    method = method.upper()

    # Pre-flight CORS handling
    if method == "OPTIONS":
        return 200, {"status": "ok"}

    try:
        # 1. System & Health
        if path in ("/api/health", "/health", "/") and method == "GET":
            return 200, {
                "status": "healthy",
                "service": "Chain Guard AI Backend",
                "version": "1.0.0",
                "mode": "offline_demo_ready",
                "bob_connected": default_bob_client.is_connected(),
            }

        # 2. Executive Overview / Dashboard KPIs
        if path in ("/api/overview", "/overview") and method == "GET":
            shipments = data_loader.get_shipments()
            disruptions = data_loader.get_disruptions(active_only=True)
            affected = disruption_service.get_affected_shipments()
            idle_fleet = fleet_service.get_idle_fleet_assets()
            excursions = cold_chain_service.get_all_excursions()

            return 200, {
                "total_shipments": len(shipments),
                "active_disruptions": len(disruptions),
                "affected_shipments_count": len(affected),
                "idle_fleet_assets": len(idle_fleet),
                "active_temperature_excursions": len(excursions),
                "system_status": "DISRUPTIONS_ACTIVE" if affected else "OPTIMAL",
            }

        # 3. Shipments
        if path in ("/api/shipments", "/shipments") and method == "GET":
            return 200, {"shipments": data_loader.get_shipments()}

        # /api/shipments/at-risk
        if path in ("/api/shipments/at-risk", "/shipments/at-risk") and method == "GET":
            affected = disruption_service.get_affected_shipments()
            return 200, {"at_risk_shipments": affected}

        # /api/shipments/{shipment_id}/disruptions
        match = re.match(r"^(?:/api)?/shipments/([^/]+)/disruptions$", path)
        if match and method == "GET":
            shipment_id = match.group(1)
            shipment = data_loader.get_shipment_by_id(shipment_id)
            if not shipment:
                return 404, {"error": f"Shipment '{shipment_id}' not found."}
            disruptions = disruption_service.get_disruptions_for_shipment(shipment_id)
            return 200, {
                "shipment_id": shipment_id,
                "disruptions_count": len(disruptions),
                "disruptions": disruptions,
            }

        # /api/shipments/{shipment_id}
        match = re.match(r"^(?:/api)?/shipments/([^/]+)$", path)
        if match and method == "GET":
            shipment_id = match.group(1)
            shipment = data_loader.get_shipment_by_id(shipment_id)
            if not shipment:
                return 404, {"error": f"Shipment '{shipment_id}' not found."}
            return 200, {"shipment": shipment}

        # 4. Disruptions
        if path in ("/api/disruptions", "/disruptions", "/api/disruptions/active", "/disruptions/active") and method == "GET":
            active_only = query_params.get("active_only", "true").lower() in ("true", "1")
            return 200, {"disruptions": data_loader.get_disruptions(active_only=active_only)}

        if path in ("/api/disruptions/affected-shipments", "/disruptions/affected-shipments") and method == "GET":
            affected = disruption_service.get_affected_shipments()
            return 200, {
                "total_affected": len(affected),
                "affected_shipments": affected,
            }

        # POST /api/analyze-disruption
        if path in ("/api/analyze-disruption", "/analyze-disruption") and method == "POST":
            shipment_id = (body or {}).get("shipment_id")
            if shipment_id:
                impacts = disruption_service.get_disruptions_for_shipment(shipment_id)
                return 200, {"shipment_id": shipment_id, "impacts": impacts, "affected": len(impacts) > 0}
            affected = disruption_service.get_affected_shipments()
            return 200, {"total_affected": len(affected), "affected_shipments": affected}

        # POST /api/risk-score
        if path in ("/api/risk-score", "/risk-score") and method == "POST":
            shipment_id = (body or {}).get("shipment_id", "SHP-1002")
            summary = incident_service.build_incident_summary(shipment_id)
            return 200, {
                "shipment_id": shipment_id,
                "risk_assessment": summary.get("executive_assessment", {}),
                "disruption": summary.get("disruption"),
                "cold_chain": summary.get("cold_chain"),
            }

        # 5. Rerouting & Carrier Alternatives
        match = re.match(r"^(?:/api)?(?:/routing/recommendations|/reroute)/([^/]+)$", path)
        if match and method == "GET":
            shipment_id = match.group(1)
            try:
                rec = reroute_service.generate_reroute_recommendation(shipment_id)
                return 200, rec
            except ValueError as ve:
                return 404, {"error": str(ve)}

        match = re.match(r"^(?:/api)?/routing/approve/([^/]+)$", path)
        if match and method == "POST":
            shipment_id = match.group(1)
            return 200, {
                "success": True,
                "shipment_id": shipment_id,
                "message": f"Reroute order for {shipment_id} authorized and dispatched.",
            }

        if path in ("/api/reroute", "/reroute") and method == "POST":
            shipment_id = (body or {}).get("shipment_id", "SHP-1002")
            try:
                rec = reroute_service.generate_reroute_recommendation(shipment_id)
                return 200, rec
            except ValueError as ve:
                return 404, {"error": str(ve)}

        if path in ("/api/carrier-recommendation", "/carrier-recommendation") and method == "POST":
            carriers = reroute_service.find_carrier_alternatives()
            return 200, {"recommended_carriers": carriers}

        # 6. Fleet Management & Redeployment
        if path in ("/api/fleet", "/fleet", "/api/fleet/assets", "/fleet/assets") and method == "GET":
            idle_only = query_params.get("idle_only", "false").lower() in ("true", "1")
            reefer_only = query_params.get("reefer_only", "false").lower() in ("true", "1")
            assets = data_loader.get_fleet_assets(idle_only=idle_only, reefer_only=reefer_only)
            return 200, {"assets": assets}

        if path in ("/api/fleet/redeployment", "/fleet/redeployment", "/api/fleet/recommendations", "/fleet/recommendations") and method == "GET":
            shipment_id = query_params.get("shipment_id")
            if not shipment_id:
                return 400, {"error": "Query parameter 'shipment_id' is required for fleet redeployment matching."}
            try:
                candidates = fleet_service.find_redeployment_candidates_for_shipment(shipment_id)
                return 200, {
                    "shipment_id": shipment_id,
                    "candidates_count": len(candidates),
                    "candidates": candidates,
                }
            except ValueError as ve:
                return 404, {"error": str(ve)}

        if path in ("/api/fleet/redeployment", "/fleet/redeployment", "/api/fleet-redeployment", "/fleet-redeployment", "/api/fleet/assign", "/fleet/assign") and method == "POST":
            if not body:
                return 400, {"error": "JSON payload required."}
            asset_id = body.get("asset_id")
            target_shipment_id = body.get("target_shipment_id") or body.get("shipment_id")
            urgency = body.get("urgency", "HIGH")
            reason = body.get("reason", "Disruption mitigation asset dispatch")

            if not asset_id or not target_shipment_id:
                return 400, {"error": "'asset_id' and 'target_shipment_id' are required fields."}

            try:
                dispatch = fleet_service.create_redeployment_dispatch(
                    asset_id=asset_id,
                    target_shipment_id=target_shipment_id,
                    urgency=urgency,
                    reason=reason,
                )
                return 201, {
                    "success": True,
                    "message": f"Asset {asset_id} dispatched to support {target_shipment_id}.",
                    "dispatch": dispatch,
                }
            except ValueError as ve:
                return 404, {"error": str(ve)}

        # 7. Cold-Chain Monitoring
        if path in ("/api/cold-chain/excursions", "/cold-chain/excursions", "/api/cold-chain/alerts", "/cold-chain/alerts") and method == "GET":
            excursions = cold_chain_service.get_all_excursions()
            return 200, {
                "active_excursions_count": len(excursions),
                "excursions": excursions,
            }

        match = re.match(r"^(?:/api)?/cold-chain/([^/]+)/audit$", path)
        if match and method == "GET":
            shipment_id = match.group(1)
            try:
                audit = cold_chain_service.generate_compliance_audit(shipment_id)
                return 200, audit
            except ValueError as ve:
                return 404, {"error": str(ve)}

        match = re.match(r"^(?:/api)?(?:/cold-chain/telemetry|/cold-chain)/([^/]+)$", path)
        if match and method == "GET":
            shipment_id = match.group(1)
            try:
                report = cold_chain_service.analyze_shipment_cold_chain(shipment_id)
                return 200, report
            except ValueError as ve:
                return 404, {"error": str(ve)}

        if path in ("/api/cold-chain/analyze", "/cold-chain/analyze", "/api/cold-chain", "/cold-chain") and method == "POST":
            shipment_id = (body or {}).get("shipment_id", "SHP-1005")
            try:
                report = cold_chain_service.analyze_shipment_cold_chain(shipment_id)
                return 200, report
            except ValueError as ve:
                return 404, {"error": str(ve)}

        # 8. Unified Operations & Recommendations
        if path in ("/api/operations/recommendation", "/operations/recommendation") and method == "POST":
            shipment_id = (body or {}).get("shipment_id", "SHP-1002")
            try:
                summary = incident_service.build_incident_summary(shipment_id)
                return 200, summary
            except ValueError as ve:
                return 404, {"error": str(ve)}

        # 9. IBM Bob & Incident Intelligence
        match = re.match(r"^(?:/api)?/bob/incident-summary/([^/]+)$", path)
        if match and method == "GET":
            shipment_id = match.group(1)
            try:
                briefing = default_bob_client.generate_incident_briefing(shipment_id)
                return 200, briefing
            except ValueError as ve:
                return 404, {"error": str(ve)}

        match = re.match(r"^(?:/api)?/bob/briefing/([^/]+)$", path)
        if match and method == "GET":
            shipment_id = match.group(1)
            try:
                briefing = default_bob_client.generate_disruption_briefing(shipment_id)
                return 200, briefing
            except ValueError as ve:
                return 404, {"error": str(ve)}

        if path in ("/api/copilot/query", "/copilot/query") and method == "POST":
            query_str = (body or {}).get("query", "")
            context_id = (body or {}).get("context_shipment_id")
            result = default_bob_client.ask_bob(query=query_str, context_shipment_id=context_id)
            return 200, result

        # Route Not Found
        return 404, {"error": f"Endpoint '{path}' with method '{method}' not found."}

    except Exception as e:
        return 500, {
            "error": "Internal server processing error.",
            "details": str(e),
        }
