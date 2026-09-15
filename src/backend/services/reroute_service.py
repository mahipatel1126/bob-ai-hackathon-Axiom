"""Reroute and carrier alternative service for Chain Guard AI.

Provides route and carrier alternatives for disrupted shipments,
with a clean integration contract for Person 2's AI optimizer
and a reliable deterministic fallback for local execution.
"""

from typing import List, Dict, Any, Optional, Callable
import uuid
from datetime import datetime, timezone

from . import data_loader
from . import disruption_service
from ..models import (
    Shipment,
    RouteAlternative,
    CarrierOption,
    RerouteRecommendation,
    RecommendationStatus,
    TransportMode,
)

# Optional hook for Person 2's AI route optimizer module
_AI_ROUTE_OPTIMIZER_HOOK: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None


def register_ai_route_optimizer(optimizer_fn: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
    """Allow Person 2 to register their AI/ML optimization function dynamically.

    Expected input structure:
    {
        "shipment": dict,
        "disruption": dict or None,
        "candidate_routes": list of dicts,
        "candidate_carriers": list of dicts,
        "constraints": dict
    }

    Expected output structure:
    {
        "recommended_route_id": str,
        "recommended_carrier_id": str,
        "reasoning": str,
        "score": float,
        "delay_hours_saved": float,
        "cost_delta_usd": float
    }
    """
    global _AI_ROUTE_OPTIMIZER_HOOK
    _AI_ROUTE_OPTIMIZER_HOOK = optimizer_fn


def find_route_alternatives(shipment_id: str) -> List[Dict[str, Any]]:
    """Retrieve all available alternative transit routes for a shipment."""
    routes = data_loader.get_route_alternatives(shipment_id=shipment_id)
    # If no shipment-specific routes are stored, return general alternatives
    if not routes:
        routes = data_loader.get_route_alternatives()
    return routes


def find_carrier_alternatives(transport_mode: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve available alternative carriers, optionally filtered by transport mode."""
    carriers = data_loader.get_carriers()
    if transport_mode:
        carriers = [c for c in carriers if c.get("transport_mode") == transport_mode]
    return carriers


def generate_reroute_recommendation(
    shipment_id: str,
    disruption_id: Optional[str] = None,
    use_ai: bool = True,
) -> Dict[str, Any]:
    """Generate a rerouting recommendation for an impacted shipment.

    If Person 2's AI optimizer is available (either registered or in src.ai),
    delegates to AI. Otherwise, executes a deterministic heuristic fallback.
    """
    shipment_dict = data_loader.get_shipment_by_id(shipment_id)
    if not shipment_dict:
        raise ValueError(f"Shipment {shipment_id} not found.")

    # Find associated disruption if not provided
    if not disruption_id:
        active_disruptions = disruption_service.get_disruptions_for_shipment(shipment_id)
        if active_disruptions:
            disruption_id = active_disruptions[0]["disruption_id"]
        else:
            disruption_id = "NO_ACTIVE_DISRUPTION"

    disruption_dict = data_loader.get_disruption_by_id(disruption_id) if disruption_id != "NO_ACTIVE_DISRUPTION" else None
    candidate_routes = find_route_alternatives(shipment_id)
    candidate_carriers = find_carrier_alternatives()

    # Step 1: Check for registered AI optimizer hook or src.ai module
    ai_result = None
    if use_ai:
        if _AI_ROUTE_OPTIMIZER_HOOK is not None:
            try:
                ai_input = {
                    "shipment": shipment_dict,
                    "disruption": disruption_dict,
                    "candidate_routes": candidate_routes,
                    "candidate_carriers": candidate_carriers,
                    "constraints": {
                        "is_cold_chain": shipment_dict.get("temperature_requirement", {}).get("is_required", False),
                        "max_acceptable_delay_hours": 12.0,
                    },
                }
                ai_result = _AI_ROUTE_OPTIMIZER_HOOK(ai_input)
            except Exception as e:
                ai_result = None
        else:
            # Attempt to auto-import Person 2's optimizer if present
            try:
                from ...ai.route_optimizer import optimize_route  # type: ignore
                ai_input = {
                    "shipment": shipment_dict,
                    "disruption": disruption_dict,
                    "candidate_routes": candidate_routes,
                    "candidate_carriers": candidate_carriers,
                }
                ai_result = optimize_route(ai_input)
            except (ImportError, AttributeError):
                ai_result = None

    # Step 2: Use AI result if present
    if ai_result and isinstance(ai_result, dict):
        rec_id = f"REC-AI-{uuid.uuid4().hex[:6].upper()}"
        return {
            "recommendation_id": rec_id,
            "shipment_id": shipment_id,
            "disruption_id": disruption_id,
            "source": "person_2_ai_optimizer",
            "original_route_summary": f"Standard transit via {shipment_dict.get('carrier', 'primary carrier')}",
            "recommended_route_id": ai_result.get("recommended_route_id"),
            "recommended_carrier_id": ai_result.get("recommended_carrier_id"),
            "rationale": ai_result.get("reasoning", "Optimized by ChainGuard AI optimizer."),
            "delay_hours_saved": float(ai_result.get("delay_hours_saved", 0.0)),
            "cost_delta_usd": float(ai_result.get("cost_delta_usd", 0.0)),
            "optimization_score": float(ai_result.get("score", 0.95)),
            "status": "PENDING_APPROVAL",
            "alternatives": candidate_routes,
            "carrier_options": candidate_carriers,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    # Step 3: Deterministic Fallback Logic (clearly labeled)
    # Pick route with lowest risk score
    recommended_route = None
    if candidate_routes:
        recommended_route = min(candidate_routes, key=lambda r: r.get("risk_score", 1.0))

    # Pick carrier matching route transport mode with highest reliability
    target_mode = recommended_route.get("transport_mode", "ROAD") if recommended_route else "ROAD"
    matching_carriers = [c for c in candidate_carriers if c.get("transport_mode") == target_mode and c.get("capacity_available", True)]
    
    if matching_carriers:
        recommended_carrier = max(matching_carriers, key=lambda c: c.get("reliability_score", 0.0))
    elif candidate_carriers:
        recommended_carrier = max(candidate_carriers, key=lambda c: c.get("reliability_score", 0.0))
    else:
        recommended_carrier = None

    # Calculate tradeoffs
    baseline_hours = 24.0
    alt_hours = recommended_route.get("estimated_transit_hours", 18.0) if recommended_route else 18.0
    delay_saved = max(0.0, round(baseline_hours - alt_hours, 1))
    
    cost_delta = 0.0
    if recommended_route:
        cost_delta = round(recommended_route.get("estimated_cost_usd", 4000.0) - 3500.0, 2)

    rec_id = f"REC-DET-{uuid.uuid4().hex[:6].upper()}"
    route_name = recommended_route.get("route_name", "Alternative Bypass") if recommended_route else "Direct Route"
    carrier_name = recommended_carrier.get("carrier_name", "Primary Carrier") if recommended_carrier else "Standard Fleet"

    rationale = (
        f"[Deterministic Fallback] Selected '{route_name}' bypassing disruption area "
        f"with risk score {recommended_route.get('risk_score', 0.1) if recommended_route else 0.1:.2f}. "
        f"Assigned carrier '{carrier_name}' ({target_mode}) based on {recommended_carrier.get('reliability_score', 0.9) * 100:.0f}% reliability rating."
        if recommended_carrier else f"[Deterministic Fallback] Route selected: {route_name}."
    )

    return {
        "recommendation_id": rec_id,
        "shipment_id": shipment_id,
        "disruption_id": disruption_id,
        "source": "deterministic_backend_fallback",
        "original_route_summary": f"Standard transit via {shipment_dict.get('carrier', 'primary carrier')}",
        "recommended_route_id": recommended_route.get("route_id") if recommended_route else None,
        "recommended_carrier_id": recommended_carrier.get("carrier_id") if recommended_carrier else None,
        "rationale": rationale,
        "delay_hours_saved": delay_saved,
        "cost_delta_usd": cost_delta,
        "optimization_score": 0.88,
        "status": "PENDING_APPROVAL",
        "alternatives": candidate_routes,
        "carrier_options": candidate_carriers,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
