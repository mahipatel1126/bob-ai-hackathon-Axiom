"""Fleet asset domain models."""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict, Any

from .common import Location, Coordinates


class AssetType(str, Enum):
    """Categorization of transportation assets."""
    TRUCK = "TRUCK"
    REEFER_TRUCK = "REEFER_TRUCK"
    CARGO_VESSEL = "CARGO_VESSEL"
    SPRINTER_VAN = "SPRINTER_VAN"
    REEFER_CONTAINER = "REEFER_CONTAINER"
    AIRCRAFT = "AIRCRAFT"


class AssetStatus(str, Enum):
    """Operational status of an asset."""
    IDLE = "IDLE"
    EN_ROUTE = "EN_ROUTE"
    MAINTENANCE = "MAINTENANCE"
    ASSIGNED = "ASSIGNED"


@dataclass
class ReeferCapability:
    """Refrigeration specs for cold-chain compliant assets."""
    is_reefer: bool = False
    min_cooling_temp_c: Optional[float] = None
    max_cooling_temp_c: Optional[float] = None
    backup_power_hours: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReeferCapability":
        return cls(
            is_reefer=data.get("is_reefer", False),
            min_cooling_temp_c=data.get("min_cooling_temp_c"),
            max_cooling_temp_c=data.get("max_cooling_temp_c"),
            backup_power_hours=data.get("backup_power_hours"),
        )


@dataclass
class FleetAsset:
    """Physical transportation or container asset in the fleet."""
    asset_id: str
    asset_name: str
    asset_type: AssetType
    current_location: Location
    status: AssetStatus
    weight_capacity_kg: float
    volume_capacity_cbm: float
    reefer_capability: ReeferCapability = field(default_factory=ReeferCapability)
    is_available: bool = True
    available_from: Optional[str] = None
    home_depot: Optional[str] = None
    driver_assigned: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_name": self.asset_name,
            "asset_type": self.asset_type.value if isinstance(self.asset_type, AssetType) else self.asset_type,
            "current_location": self.current_location.to_dict(),
            "status": self.status.value if isinstance(self.status, AssetStatus) else self.status,
            "weight_capacity_kg": self.weight_capacity_kg,
            "volume_capacity_cbm": self.volume_capacity_cbm,
            "reefer_capability": self.reefer_capability.to_dict(),
            "is_available": self.is_available,
            "available_from": self.available_from,
            "home_depot": self.home_depot,
            "driver_assigned": self.driver_assigned,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FleetAsset":
        atype = AssetType(data["asset_type"]) if isinstance(data["asset_type"], str) else data["asset_type"]
        status = AssetStatus(data["status"]) if isinstance(data["status"], str) else data["status"]
        loc = Location.from_dict(data["current_location"]) if isinstance(data["current_location"], dict) else data["current_location"]
        reefer_raw = data.get("reefer_capability", {})
        reefer = ReeferCapability.from_dict(reefer_raw) if isinstance(reefer_raw, dict) else (reefer_raw or ReeferCapability())
        return cls(
            asset_id=data["asset_id"],
            asset_name=data.get("asset_name", data["asset_id"]),
            asset_type=atype,
            current_location=loc,
            status=status,
            weight_capacity_kg=float(data["weight_capacity_kg"]),
            volume_capacity_cbm=float(data.get("volume_capacity_cbm", 0.0)),
            reefer_capability=reefer,
            is_available=data.get("is_available", True),
            available_from=data.get("available_from"),
            home_depot=data.get("home_depot"),
            driver_assigned=data.get("driver_assigned"),
        )
