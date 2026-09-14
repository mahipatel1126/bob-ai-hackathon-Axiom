"""Dynamic route evaluation and rerouting recommendation engine."""

from typing import Dict, List, Optional
from src.ai.config import AIConfig, DEFAULT_CONFIG
from src.ai.schemas import (
    Disruption,
    RouteOption,
    RouteRecommendationResult,
    Shipment,
)


def _calculate_route_disruption_exposure(
    route: RouteOption,
    disruptions: List[Disruption]
) -> float:
    """Calculate the disruption exposure fraction (0.0 to 1.0) of a candidate route."""
    if not disruptions:
        return 0.0

    all_disruption_locs = set()
    for d in disruptions:
        all_disruption_locs.add(d.location.strip().lower())
        if d.region:
            all_disruption_locs.add(d.region.strip().lower())
        for loc in d.affected_locations:
            all_disruption_locs.add(loc.strip().lower())

    if not route.waypoints:
        return route.disruption_exposure

    hits = 0
    for wp in route.waypoints:
        if wp.strip().lower() in all_disruption_locs:
            hits += 1

    exposure_by_waypoints = hits / max(1, len(route.waypoints))
    return max(exposure_by_waypoints, route.disruption_exposure)


def evaluate_routes(
    shipment: Shipment,
    candidate_routes: List[RouteOption],
    disruptions: Optional[List[Disruption]] = None,
    config: Optional[AIConfig] = None,
) -> RouteRecommendationResult:
    """Evaluate and rank candidate routes for a shipment under active disruption conditions.
    
    Ranking Score (Lower is Better):
    - Disruption Risk Penalty (0-100 * 0.45)
    - Transit Time Factor (hours * 10 * 0.30)
    - Financial Cost Factor (normalized cost * 0.25)
    """
    if not candidate_routes:
        return RouteRecommendationResult(
            shipment_id=shipment.shipment_id,
            recommended_route=None,
            ranked_routes=[],
            selection_reason="No alternative candidate routes were provided for evaluation.",
            score_breakdown={},
        )

    disruptions_list = disruptions or []
    
    scored_routes = []
    min_cost = min((r.estimated_cost for r in candidate_routes), default=1.0)
    min_time = min((r.estimated_time_hours for r in candidate_routes), default=1.0)

    for route in candidate_routes:
        exposure = _calculate_route_disruption_exposure(route, disruptions_list)
        # Update route risk score based on active disruption exposure
        if disruptions_list:
            effective_risk = exposure * 100.0
        else:
            effective_risk = route.risk_score
        
        # Normalized metrics (cost ratio, time ratio)
        cost_ratio = route.estimated_cost / max(1.0, min_cost)
        time_ratio = route.estimated_time_hours / max(1.0, min_time)

        # Composite Penalty Score (Lower is better)
        # Risk is heavily penalized to avoid sending vehicles into active hazard zones
        penalty_score = (
            effective_risk * 0.50 +
            (time_ratio * 30.0) * 0.30 +
            (cost_ratio * 20.0) * 0.20
        )

        # Create updated route copy with calculated metrics
        evaluated_route = route.model_copy(
            update={
                "risk_score": round(effective_risk, 1),
                "disruption_exposure": round(exposure, 2),
            }
        )
        scored_routes.append((penalty_score, evaluated_route))

    # Sort routes by penalty score ascending (best first)
    scored_routes.sort(key=lambda x: x[0])
    ranked_routes = [r for _, r in scored_routes]
    best_route = ranked_routes[0]
    best_penalty = scored_routes[0][0]

    # Generate explainable selection reason
    if best_route.risk_score < 15.0:
        risk_desc = "completely bypasses active disruption zones"
    elif best_route.risk_score < 40.0:
        risk_desc = "significantly minimizes exposure to disruption corridors"
    else:
        risk_desc = "provides the least disruptive available path"

    selection_reason = (
        f"Selected '{best_route.name}' (ID: {best_route.route_id}) because it {risk_desc} "
        f"with an estimated transit time of {best_route.estimated_time_hours:.1f}h ({best_route.distance_km:.0f} km) "
        f"and projected cost of INR {best_route.estimated_cost:,.0f}."
    )

    if len(ranked_routes) > 1:
        runner_up = ranked_routes[1]
        selection_reason += (
            f" Outperformed alternative '{runner_up.name}' by providing lower disruption risk "
            f"({best_route.risk_score:.0f} vs {runner_up.risk_score:.0f})."
        )

    score_breakdown = {
        r.route_id: round(score, 2)
        for score, r in scored_routes
    }

    return RouteRecommendationResult(
        shipment_id=shipment.shipment_id,
        recommended_route=best_route,
        ranked_routes=ranked_routes,
        selection_reason=selection_reason,
        score_breakdown=score_breakdown,
    )
