"""Idle fleet detection, classification, and vehicle suitability engine."""

from typing import Dict, List, Optional, Tuple
from src.ai.config import AIConfig, DEFAULT_CONFIG
from src.ai.schemas import (
    FleetAsset,
    FleetAvailability,
    FleetStatus,
    IdleFleetResult,
    Shipment,
    VehicleType,
)


def classify_fleet_asset(asset: FleetAsset, config: Optional[AIConfig] = None) -> FleetStatus:
    """Classify an individual fleet asset based on operational status and utilization."""
    cfg = config or DEFAULT_CONFIG
    t = cfg.fleet_thresholds

    if asset.availability in (FleetAvailability.MAINTENANCE, FleetAvailability.RESERVED):
        return FleetStatus.UNAVAILABLE

    if asset.availability == FleetAvailability.IN_USE:
        return FleetStatus.ACTIVE

    # When marked AVAILABLE, categorize based on utilization rate
    if asset.current_utilization <= t.idle_max:
        return FleetStatus.IDLE
    elif asset.current_utilization <= t.underutilized_max:
        return FleetStatus.UNDERUTILIZED
    elif asset.current_utilization <= t.active_max:
        return FleetStatus.ACTIVE
    else:
        return FleetStatus.ACTIVE


def detect_idle_fleet(
    fleet: List[FleetAsset],
    config: Optional[AIConfig] = None,
) -> IdleFleetResult:
    """Analyze the complete fleet roster and classify assets into utilization tiers."""
    cfg = config or DEFAULT_CONFIG
    
    idle_list: List[FleetAsset] = []
    underutilized_list: List[FleetAsset] = []
    active_list: List[FleetAsset] = []
    unavailable_list: List[FleetAsset] = []

    total_util = 0.0

    for asset in fleet:
        status = classify_fleet_asset(asset, cfg)
        updated_asset = asset.model_copy(update={"status": status})
        
        if status == FleetStatus.IDLE:
            idle_list.append(updated_asset)
        elif status == FleetStatus.UNDERUTILIZED:
            underutilized_list.append(updated_asset)
        elif status == FleetStatus.ACTIVE:
            active_list.append(updated_asset)
        else:
            unavailable_list.append(updated_asset)

        total_util += asset.current_utilization

    total_count = len(fleet)
    avg_util = (total_util / total_count) if total_count > 0 else 0.0

    explanation = (
        f"Fleet Roster Analysis: {total_count} total assets. "
        f"{len(idle_list)} IDLE (<15% utilization), "
        f"{len(underutilized_list)} UNDERUTILIZED (15-50%), "
        f"{len(active_list)} ACTIVE, "
        f"{len(unavailable_list)} UNAVAILABLE (Maintenance/Reserved). "
        f"Fleet average utilization is {avg_util * 100:.1f}%."
    )

    return IdleFleetResult(
        idle_vehicles=idle_list,
        underutilized_vehicles=underutilized_list,
        active_vehicles=active_list,
        unavailable_vehicles=unavailable_list,
        total_assets=total_count,
        idle_count=len(idle_list),
        utilization_rate_avg=round(avg_util, 3),
        explanation=explanation,
    )


def filter_suitable_vehicles(
    shipment: Shipment,
    fleet: List[FleetAsset],
    config: Optional[AIConfig] = None,
) -> Tuple[List[FleetAsset], List[Dict[str, str]]]:
    """Filter fleet assets to identify vehicles physically and operationally capable of handling a shipment.
    
    Requirements:
    1. Status: Must be IDLE or UNDERUTILIZED (or AVAILABLE).
    2. Capacity: Vehicle payload capacity >= shipment weight.
    3. Cold-Chain Compliance: If shipment requires temp control, vehicle must have reefer capability and cover temp range.
    """
    suitable: List[FleetAsset] = []
    rejections: List[Dict[str, str]] = []

    for asset in fleet:
        # Check availability
        if asset.availability in (FleetAvailability.MAINTENANCE, FleetAvailability.RESERVED):
            rejections.append({
                "vehicle_id": asset.vehicle_id,
                "reason": f"Vehicle is unavailable ({asset.availability.value})."
            })
            continue

        if asset.current_utilization >= 0.85:
            rejections.append({
                "vehicle_id": asset.vehicle_id,
                "reason": f"Vehicle is already at high utilization ({asset.current_utilization * 100:.0f}%)."
            })
            continue

        # Check weight payload capacity
        if asset.capacity_kg < shipment.weight_kg:
            rejections.append({
                "vehicle_id": asset.vehicle_id,
                "reason": (
                    f"Payload capacity insufficient ({asset.capacity_kg:,.0f} kg vs "
                    f"{shipment.weight_kg:,.0f} kg required)."
                )
            })
            continue

        # Check volume capacity if specified
        if shipment.volume_cbm > 0 and asset.capacity_cbm < shipment.volume_cbm:
            rejections.append({
                "vehicle_id": asset.vehicle_id,
                "reason": (
                    f"Volume capacity insufficient ({asset.capacity_cbm:.1f} CBM vs "
                    f"{shipment.volume_cbm:.1f} CBM required)."
                )
            })
            continue

        # Check Cold-Chain capabilities
        if shipment.temperature_required:
            if not asset.temperature_capability or asset.vehicle_type != VehicleType.REEFER_TRUCK:
                rejections.append({
                    "vehicle_id": asset.vehicle_id,
                    "reason": "Non-refrigerated asset cannot service temperature-controlled cargo."
                })
                continue

            # Check temperature envelope
            if shipment.required_min_temperature is not None and asset.min_temp_capable is not None:
                if asset.min_temp_capable > shipment.required_min_temperature:
                    rejections.append({
                        "vehicle_id": asset.vehicle_id,
                        "reason": (
                            f"Vehicle cooling floor ({asset.min_temp_capable}°C) cannot reach required "
                            f"minimum ({shipment.required_min_temperature}°C)."
                        )
                    })
                    continue

            if shipment.required_max_temperature is not None and asset.max_temp_capable is not None:
                if asset.max_temp_capable < shipment.required_max_temperature:
                    rejections.append({
                        "vehicle_id": asset.vehicle_id,
                        "reason": (
                            f"Vehicle cooling ceiling ({asset.max_temp_capable}°C) cannot meet required "
                            f"maximum ({shipment.required_max_temperature}°C)."
                        )
                    })
                    continue

        suitable.append(asset)

    return suitable, rejections
