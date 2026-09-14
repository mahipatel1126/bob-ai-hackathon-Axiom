"""Disruption matching service for Chain Guard AI.

Identifies active disruptions intersecting shipment routes, corridors,
and current transit locations using deterministic geospatial proximity.
"""

import math
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from . import data_loader
from ..models import (
    Shipment,
    Disruption,
    Coordinates,
    DisruptionSeverity,
)

# Mean Earth radius in kilometers
EARTH_RADIUS_KM: float = 6371.0


def calculate_haversine_distance(coord1: Coordinates, coord2: Coordinates) -> float:
    """Calculate the great-circle distance between two points on Earth in kilometers."""
    lat1 = math.radians(coord1.latitude)
    lon1 = math.radians(coord1.longitude)
    lat2 = math.radians(coord2.latitude)
    lon2 = math.radians(coord2.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
    )
    # Clamp value to avoid domain errors with floating point precision
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return round(EARTH_RADIUS_KM * c, 2)


@dataclass
class DisruptionImpact:
    """Detailed impact assessment linking a disruption to a shipment."""
    shipment_id: str
    disruption_id: str
    disruption_title: str
    disruption_type: str
    disruption_severity: str
    affected_location: str
    impact_distance_km: float
    impact_radius_km: float
    impact_reason: str
    risk_level: str
    urgency: str
    carrier: str
    cargo_type: str
    is_cold_chain: bool
    shipment_status: str
    current_coordinates: Optional[Dict[str, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_shipment_against_disruption(
    shipment: Shipment,
    disruption: Disruption,
) -> Optional[DisruptionImpact]:
    """Evaluate whether a single shipment is impacted by a disruption.

    Checks:
    1. Proximity of the shipment's current location to the disruption epicenter.
    2. Proximity of upcoming route waypoints to the disruption epicenter.
    3. Proximity of destination/origin facilities.
    """
    if not disruption.is_active or disruption.center_coordinates is None:
        return None

    disruption_center = disruption.center_coordinates
    radius = disruption.impact_radius_km
    min_distance = float("inf")
    match_reason = ""
    affected_loc_name = disruption.region_name

    # Priority 1: Check Current GPS Location
    if shipment.current_location is not None:
        dist_cur = calculate_haversine_distance(shipment.current_location, disruption_center)
        if dist_cur <= radius:
            min_distance = dist_cur
            match_reason = (
                f"Current location ({shipment.current_location.latitude}, {shipment.current_location.longitude}) "
                f"is {dist_cur:.1f} km from disruption epicenter (within {radius:.1f} km radius)."
            )

    # Priority 2: Check Route Waypoints (prioritizing upcoming ones)
    for wp in shipment.route_waypoints:
        if wp.coordinates is None:
            continue
        dist_wp = calculate_haversine_distance(wp.coordinates, disruption_center)
        if dist_wp <= radius and dist_wp < min_distance:
            min_distance = dist_wp
            status_desc = "Traversed" if wp.is_passed else "Upcoming scheduled"
            match_reason = (
                f"{status_desc} waypoint '{wp.name}' is {dist_wp:.1f} km "
                f"from disruption epicenter (within {radius:.1f} km radius)."
            )
            affected_loc_name = f"{wp.name} ({disruption.region_name})"

    # Priority 3: Check Destination Facility
    if shipment.destination and shipment.destination.coordinates:
        dist_dest = calculate_haversine_distance(shipment.destination.coordinates, disruption_center)
        if dist_dest <= radius and dist_dest < min_distance:
            min_distance = dist_dest
            match_reason = (
                f"Destination facility '{shipment.destination.name}' is {dist_dest:.1f} km "
                f"from disruption epicenter (within {radius:.1f} km radius)."
            )
            affected_loc_name = shipment.destination.name

    # If no points fell within the disruption's impact radius, the shipment is not affected
    if min_distance > radius:
        return None

    # Compute risk and urgency rating
    # Cold-chain sensitive cargo in a disrupted corridor gets immediate urgency
    is_cold_chain = (
        shipment.temperature_requirement is not None
        and shipment.temperature_requirement.is_required
    )

    sev_str = (
        disruption.severity.value
        if isinstance(disruption.severity, DisruptionSeverity)
        else str(disruption.severity)
    )

    if sev_str == "CRITICAL":
        risk_level = "CRITICAL"
        urgency = "IMMEDIATE" if is_cold_chain else "HIGH"
    elif sev_str == "HIGH":
        risk_level = "HIGH"
        urgency = "HIGH" if is_cold_chain else "MEDIUM"
    elif sev_str == "MEDIUM":
        risk_level = "MEDIUM"
        urgency = "MEDIUM"
    else:
        risk_level = "LOW"
        urgency = "LOW"

    cur_coords = None
    if shipment.current_location:
        cur_coords = {
            "latitude": shipment.current_location.latitude,
            "longitude": shipment.current_location.longitude,
        }

    dtype_str = disruption.type.value if hasattr(disruption.type, "value") else str(disruption.type)
    cstatus_str = shipment.status.value if hasattr(shipment.status, "value") else str(shipment.status)
    ctype_str = shipment.cargo.cargo_type.value if hasattr(shipment.cargo.cargo_type, "value") else str(shipment.cargo.cargo_type)

    return DisruptionImpact(
        shipment_id=shipment.shipment_id,
        disruption_id=disruption.disruption_id,
        disruption_title=disruption.title,
        disruption_type=dtype_str,
        disruption_severity=sev_str,
        affected_location=affected_loc_name,
        impact_distance_km=min_distance,
        impact_radius_km=radius,
        impact_reason=match_reason,
        risk_level=risk_level,
        urgency=urgency,
        carrier=shipment.carrier,
        cargo_type=ctype_str,
        is_cold_chain=is_cold_chain,
        shipment_status=cstatus_str,
        current_coordinates=cur_coords,
    )


def get_affected_shipments(
    shipments: Optional[List[Shipment]] = None,
    disruptions: Optional[List[Disruption]] = None,
) -> List[Dict[str, Any]]:
    """Identify all shipments impacted by currently active disruptions.

    Returns a structured list of disruption impact assessments.
    """
    if shipments is None:
        shipments = data_loader.get_shipment_models()
    if disruptions is None:
        disruptions = data_loader.get_disruption_models(active_only=True)

    impacts: List[Dict[str, Any]] = []

    for shipment in shipments:
        for disruption in disruptions:
            impact = evaluate_shipment_against_disruption(shipment, disruption)
            if impact is not None:
                impacts.append(impact.to_dict())

    return impacts


def get_disruptions_for_shipment(
    shipment_id: str,
    shipments: Optional[List[Shipment]] = None,
    disruptions: Optional[List[Disruption]] = None,
) -> List[Dict[str, Any]]:
    """Answer 'Which active disruptions currently affect this shipment?' for a specific shipment ID."""
    if shipments is None:
        shipments = data_loader.get_shipment_models()
    if disruptions is None:
        disruptions = data_loader.get_disruption_models(active_only=True)

    # Locate the target shipment
    target_shipment = next((s for s in shipments if s.shipment_id == shipment_id), None)
    if not target_shipment:
        return []

    shipment_impacts: List[Dict[str, Any]] = []
    for disruption in disruptions:
        impact = evaluate_shipment_against_disruption(target_shipment, disruption)
        if impact is not None:
            shipment_impacts.append(impact.to_dict())

    return shipment_impacts
