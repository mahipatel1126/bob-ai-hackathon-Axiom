"""Disruption impact analysis engine for supply chain operations."""

from datetime import datetime, timezone
from typing import List, Optional
from src.ai.schemas import (
    Disruption,
    DisruptionImpactResult,
    DisruptionSeverity,
    ImpactLevel,
    Shipment,
    ShipmentStatus,
)


def _normalize_name(name: str) -> str:
    """Normalize string for fuzzy/case-insensitive location matching."""
    return name.strip().lower()


def analyze_single_disruption_impact(
    shipment: Shipment,
    disruption: Disruption,
    current_time: Optional[datetime] = None
) -> DisruptionImpactResult:
    """Evaluate whether and how a single disruption impacts a given shipment.
    
    Checks:
    1. Origin / Destination match with disruption location/region
    2. Route waypoint intersections with disruption affected routes or locations
    3. Temporal overlap between disruption duration and shipment transit window
    4. Severity-based delay projection
    """
    if shipment.status in (ShipmentStatus.DELIVERED, ShipmentStatus.CANCELLED):
        return DisruptionImpactResult(
            shipment_id=shipment.shipment_id,
            affected=False,
            disruption_id=disruption.disruption_id,
            impact_level=ImpactLevel.NONE,
            reasons=[f"Shipment is already in {shipment.status.value} state."],
            estimated_delay_hours=0.0,
            intersecting_locations=[],
        )

    reasons: List[str] = []
    intersecting_locations: List[str] = []
    
    # 1. Location Matching
    all_shipment_points = [shipment.origin, shipment.destination] + list(shipment.route)
    if shipment.current_location:
        all_shipment_points.append(shipment.current_location)
        
    normalized_points = {_normalize_name(p) for p in all_shipment_points if p}
    
    disruption_points = [disruption.location] + list(disruption.affected_locations)
    if disruption.region:
        disruption_points.append(disruption.region)
    normalized_disruptions = {_normalize_name(p) for p in disruption_points if p}

    # Intersections
    direct_hits = normalized_points.intersection(normalized_disruptions)
    for hit in direct_hits:
        # Map back to readable original casing
        matched = next((p for p in all_shipment_points if _normalize_name(p) == hit), hit)
        intersecting_locations.append(matched)

    # 2. Corridor / Route Segment matching
    corridor_hits = []
    for aff_route in disruption.affected_routes:
        aff_norm = _normalize_name(aff_route)
        for wp in shipment.route:
            if aff_norm in _normalize_name(wp) or _normalize_name(wp) in aff_norm:
                corridor_hits.append(wp)
    if corridor_hits:
        intersecting_locations.extend([c for c in corridor_hits if c not in intersecting_locations])

    # 3. Temporal overlap check
    now = current_time or datetime.now(timezone.utc).replace(tzinfo=None)
    # Check deadline proximity
    is_time_critical = False
    try:
        hours_to_deadline = (shipment.delivery_deadline - now).total_seconds() / 3600.0
        if hours_to_deadline <= disruption.estimated_duration_hours + 4.0:
            is_time_critical = True
    except Exception:
        hours_to_deadline = shipment.eta_hours_remaining

    # 4. Synthesize impact
    is_affected = len(intersecting_locations) > 0

    if is_affected:
        reasons.append(
            f"Route or endpoint intersects disruption zone at [{', '.join(intersecting_locations)}] "
            f"due to {disruption.type.value} ({disruption.description})."
        )
        if is_time_critical:
            reasons.append(
                f"Disruption duration ({disruption.estimated_duration_hours:.1f}h) directly threatens "
                f"delivery deadline (buffer remaining: {max(0.0, hours_to_deadline):.1f}h)."
            )

        # Determine Impact Level based on Disruption Severity & Criticality
        if disruption.severity == DisruptionSeverity.CRITICAL or (disruption.severity == DisruptionSeverity.HIGH and is_time_critical):
            impact_level = ImpactLevel.CRITICAL
            estimated_delay = max(disruption.delay_impact_hours, disruption.estimated_duration_hours * 0.8)
        elif disruption.severity == DisruptionSeverity.HIGH or is_time_critical:
            impact_level = ImpactLevel.HIGH
            estimated_delay = max(disruption.delay_impact_hours * 0.75, 4.0)
        elif disruption.severity == DisruptionSeverity.MEDIUM:
            impact_level = ImpactLevel.MEDIUM
            estimated_delay = max(disruption.delay_impact_hours * 0.5, 2.0)
        else:
            impact_level = ImpactLevel.LOW
            estimated_delay = 1.0
    else:
        impact_level = ImpactLevel.NONE
        estimated_delay = 0.0
        reasons.append(f"Shipment path does not intersect disruption '{disruption.disruption_id}' ({disruption.location}).")

    return DisruptionImpactResult(
        shipment_id=shipment.shipment_id,
        affected=is_affected,
        disruption_id=disruption.disruption_id if is_affected else None,
        impact_level=impact_level,
        reasons=reasons,
        estimated_delay_hours=round(estimated_delay, 1),
        intersecting_locations=intersecting_locations,
    )


def analyze_disruptions(
    shipment: Shipment,
    disruptions: List[Disruption],
    current_time: Optional[datetime] = None
) -> List[DisruptionImpactResult]:
    """Analyze impact of all active disruptions against a shipment."""
    return [
        analyze_single_disruption_impact(shipment, d, current_time)
        for d in disruptions
    ]


def get_highest_disruption_impact(
    shipment: Shipment,
    disruptions: List[Disruption],
    current_time: Optional[datetime] = None
) -> DisruptionImpactResult:
    """Retrieve the primary (highest severity) disruption impact for a shipment."""
    if not disruptions:
        return DisruptionImpactResult(
            shipment_id=shipment.shipment_id,
            affected=False,
            disruption_id=None,
            impact_level=ImpactLevel.NONE,
            reasons=["No active disruptions reported in the network."],
            estimated_delay_hours=0.0,
            intersecting_locations=[],
        )

    all_results = analyze_disruptions(shipment, disruptions, current_time)
    
    # Priority order for impact levels
    severity_rank = {
        ImpactLevel.CRITICAL: 4,
        ImpactLevel.HIGH: 3,
        ImpactLevel.MEDIUM: 2,
        ImpactLevel.LOW: 1,
        ImpactLevel.NONE: 0,
    }
    
    ranked = sorted(
        all_results,
        key=lambda r: (severity_rank.get(r.impact_level, 0), r.estimated_delay_hours),
        reverse=True
    )
    
    # Return the worst impact if any affected, else the first NONE result
    affected = [r for r in ranked if r.affected]
    if affected:
        return affected[0]
    return ranked[0]
