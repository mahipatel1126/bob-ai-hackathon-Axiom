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
        if path == "/api/overview" and method == "GET":
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
        if path == "/api/shipments" and method == "GET":
            return 200, {"shipments": data_loader.get_shipments()}

        # /api/shipments/{shipment_id}/disruptions
        match = re.match(r"^/api/shipments/([^/]+)/disruptions$", path)
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
        match = re.match(r"^/api/shipments/([^/]+)$", path)
        if match and method == "GET":
            shipment_id = match.group(1)
            shipment = data_loader.get_shipment_by_id(shipment_id)
            if not shipment:
                return 404, {"error": f"Shipment '{shipment_id}' not found."}
            return 200, {"shipment": shipment}

        # 4. Disruptions
        if path == "/api/disruptions" and method == "GET":
            active_only = query_params.get("active_only", "true").lower() in ("true", "1")
            return 200, {"disruptions": data_loader.get_disruptions(active_only=active_only)}

        if path == "/api/disruptions/affected-shipments" and method == "GET":
            affected = disruption_service.get_affected_shipments()
            return 200, {
                "total_affected": len(affected),
                "affected_shipments": affected,
            }

        # 5. Rerouting & Carrier Alternatives
        match = re.match(r"^/api/reroute/([^/]+)$", path)
        if match and method == "GET":
            shipment_id = match.group(1)
            try:
                rec = reroute_service.generate_reroute_recommendation(shipment_id)
                return 200, rec
            except ValueError as ve:
                return 404, {"error": str(ve)}

        # 6. Fleet Management & Redeployment
        if path == "/api/fleet" and method == "GET":
            idle_only = query_params.get("idle_only", "false").lower() in ("true", "1")
            reefer_only = query_params.get("reefer_only", "false").lower() in ("true", "1")
            assets = data_loader.get_fleet_assets(idle_only=idle_only, reefer_only=reefer_only)
            return 200, {"assets": assets}

        if path == "/api/fleet/redeployment" and method == "GET":
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

        if path == "/api/fleet/redeployment" and method == "POST":
            if not body:
                return 400, {"error": "JSON payload required."}
            asset_id = body.get("asset_id")
            target_shipment_id = body.get("target_shipment_id")
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
                return 201, dispatch
            except ValueError as ve:
                return 404, {"error": str(ve)}

        # 7. Cold-Chain Monitoring
        if path == "/api/cold-chain/excursions" and method == "GET":
            excursions = cold_chain_service.get_all_excursions()
            return 200, {
                "active_excursions_count": len(excursions),
                "excursions": excursions,
            }

        match = re.match(r"^/api/cold-chain/([^/]+)/audit$", path)
        if match and method == "GET":
            shipment_id = match.group(1)
            try:
                audit = cold_chain_service.generate_compliance_audit(shipment_id)
                return 200, audit
            except ValueError as ve:
                return 404, {"error": str(ve)}

        match = re.match(r"^/api/cold-chain/([^/]+)$", path)
        if match and method == "GET":
            shipment_id = match.group(1)
            try:
                report = cold_chain_service.analyze_shipment_cold_chain(shipment_id)
                return 200, report
            except ValueError as ve:
                return 404, {"error": str(ve)}

        # 8. IBM Bob & Incident Intelligence
        match = re.match(r"^/api/bob/incident-summary/([^/]+)$", path)
        if match and method == "GET":
            shipment_id = match.group(1)
            try:
                briefing = default_bob_client.generate_incident_briefing(shipment_id)
                return 200, briefing
            except ValueError as ve:
                return 404, {"error": str(ve)}

        match = re.match(r"^/api/bob/briefing/([^/]+)$", path)
        if match and method == "GET":
            shipment_id = match.group(1)
            try:
                briefing = default_bob_client.generate_disruption_briefing(shipment_id)
                return 200, briefing
            except ValueError as ve:
                return 404, {"error": str(ve)}

        # Route Not Found
        return 404, {"error": f"Endpoint '{path}' with method '{method}' not found."}

    except Exception as e:
        return 500, {
            "error": "Internal server processing error.",
            "details": str(e),
        }
