"""Fleet utilisation and asset redeployment service for Chain Guard AI.

Identifies available and idle fleet assets, evaluates geographic proximity
and capacity/thermal compatibility, and produces ranked redeployment candidates.
"""

from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timezone

from . import data_loader
from .disruption_service import calculate_haversine_distance
from ..models import (
    Coordinates,
    FleetAsset,
    RedeploymentRequest,
    RedeploymentUrgency,
    RedeploymentStatus,
    Location,
)


def get_idle_fleet_assets(reefer_only: bool = False) -> List[Dict[str, Any]]:
    """Retrieve all idle and available fleet assets."""
    return data_loader.get_fleet_assets(idle_only=True, reefer_only=reefer_only)


def find_redeployment_candidates_for_shipment(
    shipment_id: str,
    max_search_radius_km: float = 600.0,
) -> List[Dict[str, Any]]:
    """Find and rank idle fleet assets capable of rescuing or supporting an affected shipment.

    Evaluates:
    - Distance from asset's current location to distressed shipment
    - Weight & volume capacity sufficiency
    - Refrigeration compatibility (if shipment requires cold-chain)
    """
    shipment = data_loader.get_shipment_by_id(shipment_id)
    if not shipment:
        raise ValueError(f"Shipment {shipment_id} not found.")

    # Target location: current GPS if available, else origin/destination
    target_coord: Optional[Coordinates] = None
    if shipment.get("current_location"):
        target_coord = Coordinates.from_dict(shipment["current_location"])
    elif shipment.get("origin", {}).get("coordinates"):
        target_coord = Coordinates.from_dict(shipment["origin"]["coordinates"])

    if not target_coord:
        return []

    cargo_weight = shipment.get("cargo", {}).get("weight_kg", 0.0)
    cargo_volume = shipment.get("cargo", {}).get("volume_cbm", 0.0)
    temp_req = shipment.get("temperature_requirement", {})
    requires_cold_chain = temp_req.get("is_required", False)

    idle_assets = get_idle_fleet_assets()
    candidates: List[Dict[str, Any]] = []

    for asset in idle_assets:
        asset_loc_dict = asset.get("current_location", {})
        asset_coords_dict = asset_loc_dict.get("coordinates")
        if not asset_coords_dict:
            continue

        asset_coord = Coordinates.from_dict(asset_coords_dict)
        distance = calculate_haversine_distance(asset_coord, target_coord)

        if distance > max_search_radius_km:
            continue

        # Capacity evaluation
        weight_cap = asset.get("weight_capacity_kg", 0.0)
        vol_cap = asset.get("volume_capacity_cbm", 0.0)
        capacity_match = weight_cap >= cargo_weight and (vol_cap == 0.0 or vol_cap >= cargo_volume)

        # Reefer evaluation
        reefer_info = asset.get("reefer_capability", {})
        asset_has_reefer = reefer_info.get("is_reefer", False)
        
        reefer_match = True
        if requires_cold_chain:
            reefer_match = asset_has_reefer
            # Check temp range coverage if specified
            req_min = temp_req.get("min_temp_c")
            cooling_min = reefer_info.get("min_cooling_temp_c")
            if req_min is not None and cooling_min is not None:
                if cooling_min > req_min:
                    reefer_match = False

        # Build candidate score and reasoning
        # Prioritize matching reefer + capacity, sorted by distance
        is_fully_compatible = capacity_match and reefer_match

        priority = "LOW"
        if is_fully_compatible:
            if requires_cold_chain:
                priority = "CRITICAL" if distance <= 150.0 else "HIGH"
            else:
                priority = "HIGH" if distance <= 200.0 else "MEDIUM"
        elif capacity_match and not reefer_match and not requires_cold_chain:
            priority = "MEDIUM"

        reasons = []
        if distance <= 100.0:
            reasons.append(f"Immediate proximity ({distance:.1f} km away at {asset_loc_dict.get('name', 'Depot')})")
        else:
            reasons.append(f"Located {distance:.1f} km away at {asset_loc_dict.get('name', 'Depot')}")

        if capacity_match:
            reasons.append(f"Payload capacity verified ({weight_cap:,.0f} kg capacity vs {cargo_weight:,.0f} kg cargo)")
        else:
            reasons.append(f"Insufficient weight capacity ({weight_cap:,.0f} kg vs {cargo_weight:,.0f} kg needed)")

        if requires_cold_chain:
            if reefer_match:
                reasons.append(f"Cold-chain compliant (equipped with {reefer_info.get('backup_power_hours', 48)}h backup power)")
            else:
                reasons.append("Non-refrigerated asset (cannot support cold-chain cargo)")

        candidates.append({
            "shipment_id": shipment_id,
            "asset_id": asset.get("asset_id"),
            "asset_name": asset.get("asset_name"),
            "asset_type": asset.get("asset_type"),
            "current_location": asset_loc_dict,
            "distance_km": distance,
            "capacity_match": capacity_match,
            "reefer_match": reefer_match,
            "is_fully_compatible": is_fully_compatible,
            "priority": priority,
            "reason": "; ".join(reasons) + ".",
            "available_driver": asset.get("driver_assigned", "Standby Driver Pool"),
        })

    # Sort candidates: fully compatible first, then highest priority, then shortest distance
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    candidates.sort(
        key=lambda c: (
            0 if c["is_fully_compatible"] else 1,
            priority_order.get(c["priority"], 4),
            c["distance_km"],
        )
    )

    return candidates


def create_redeployment_dispatch(
    asset_id: str,
    target_shipment_id: str,
    urgency: str = "HIGH",
    reason: str = "Disruption recovery asset redeployment",
) -> Dict[str, Any]:
    """Generate a formal asset redeployment dispatch record."""
    asset = data_loader.get_fleet_asset_by_id(asset_id)
    if not asset:
        raise ValueError(f"Asset {asset_id} not found.")

    shipment = data_loader.get_shipment_by_id(target_shipment_id)
    if not shipment:
        raise ValueError(f"Shipment {target_shipment_id} not found.")

    origin_loc = asset.get("current_location", {})
    dest_loc = {
        "name": f"Rescue Point for {target_shipment_id}",
        "city": shipment.get("origin", {}).get("city", "Transit Zone"),
        "country": shipment.get("origin", {}).get("country", "USA"),
        "coordinates": shipment.get("current_location"),
        "facility_type": "INTERCEPT_POINT",
    }

    req_id = f"RDP-{uuid.uuid4().hex[:6].upper()}"
    return {
        "request_id": req_id,
        "asset_id": asset_id,
        "asset_name": asset.get("asset_name"),
        "target_shipment_id": target_shipment_id,
        "origin_location": origin_loc,
        "target_location": dest_loc,
        "urgency": urgency.upper(),
        "status": "DISPATCHED",
        "reason": reason,
        "driver_assigned": asset.get("driver_assigned"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
