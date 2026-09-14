"""Carrier evaluation and dynamic capacity recommendation engine."""

from typing import Dict, List, Optional
from src.ai.config import AIConfig, DEFAULT_CONFIG
from src.ai.schemas import (
    CarrierOption,
    CarrierRecommendationResult,
    Shipment,
)


def evaluate_carriers(
    shipment: Shipment,
    candidate_carriers: List[CarrierOption],
    config: Optional[AIConfig] = None,
) -> CarrierRecommendationResult:
    """Evaluate and rank carrier alternatives for an at-risk shipment.
    
    Filters:
    1. Capacity fit: Carrier available capacity must exceed shipment weight.
    2. Cold-chain capability: If shipment requires temperature control, carrier must support it.
    
    Ranking Score (Higher is Better):
    - Reliability Score (0.0 to 1.0 * 40 pts)
    - Transit Time Speed (Normalized vs baseline * 30 pts)
    - Cost Efficiency (Normalized cost * 20 pts)
    - Quality Rating (1 to 5 scale * 10 pts)
    """
    if not candidate_carriers:
        return CarrierRecommendationResult(
            shipment_id=shipment.shipment_id,
            recommended_carrier=None,
            ranked_carriers=[],
            selection_reason="No candidate carriers were provided for evaluation.",
            rejected_carriers=[],
        )

    valid_carriers: List[CarrierOption] = []
    rejected_carriers: List[Dict[str, str]] = []

    # Filter candidates
    for c in candidate_carriers:
        # Check Capacity
        if c.available_capacity_kg < shipment.weight_kg:
            rejected_carriers.append({
                "carrier_id": c.carrier_id,
                "carrier_name": c.name,
                "reason": (
                    f"Insufficient capacity ({c.available_capacity_kg:,.0f} kg available vs "
                    f"{shipment.weight_kg:,.0f} kg required)."
                )
            })
            continue

        # Check Cold-Chain requirement
        if shipment.temperature_required and not c.temperature_capable:
            rejected_carriers.append({
                "carrier_id": c.carrier_id,
                "carrier_name": c.name,
                "reason": "Carrier lacks certified active temperature-controlled fleet capability for cold chain."
            })
            continue

        valid_carriers.append(c)

    if not valid_carriers:
        return CarrierRecommendationResult(
            shipment_id=shipment.shipment_id,
            recommended_carrier=None,
            ranked_carriers=[],
            selection_reason=(
                f"None of the {len(candidate_carriers)} candidate carriers met operational requirements "
                f"(Capacity/Cold-Chain compliance)."
            ),
            rejected_carriers=rejected_carriers,
        )

    # Score valid candidates
    min_cost = min((c.estimated_cost for c in valid_carriers), default=1.0)
    min_time = min((c.estimated_delivery_hours for c in valid_carriers), default=1.0)

    scored_carriers = []
    for c in valid_carriers:
        reliability_pts = c.reliability_score * 40.0
        time_pts = (min_time / max(1.0, c.estimated_delivery_hours)) * 30.0
        cost_pts = (min_cost / max(1.0, c.estimated_cost)) * 20.0
        rating_pts = (min(5.0, c.rating) / 5.0) * 10.0

        total_score = reliability_pts + time_pts + cost_pts + rating_pts
        scored_carriers.append((total_score, c))

    # Sort descending by score (best first)
    scored_carriers.sort(key=lambda x: x[0], reverse=True)
    ranked_carriers = [c for _, c in scored_carriers]
    best_carrier = ranked_carriers[0]

    # Generate rationale
    temp_note = " with verified cold-chain capability" if shipment.temperature_required else ""
    selection_reason = (
        f"Recommended '{best_carrier.name}' (ID: {best_carrier.carrier_id}){temp_note} due to high "
        f"reliability ({best_carrier.reliability_score * 100:.0f}%), available payload capacity "
        f"({best_carrier.available_capacity_kg:,.0f} kg), estimated transit time of "
        f"{best_carrier.estimated_delivery_hours:.1f}h, and competitive cost of INR {best_carrier.estimated_cost:,.0f}."
    )

    return CarrierRecommendationResult(
        shipment_id=shipment.shipment_id,
        recommended_carrier=best_carrier,
        ranked_carriers=ranked_carriers,
        selection_reason=selection_reason,
        rejected_carriers=rejected_carriers,
    )
