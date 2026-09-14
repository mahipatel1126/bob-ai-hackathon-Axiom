"""Shipment domain models."""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any

from .common import Location, Coordinates


class ShipmentStatus(str, Enum):
    """Lifecycle status of a shipment."""
    PENDING = "PENDING"
    IN_TRANSIT = "IN_TRANSIT"
    DELAYED = "DELAYED"
    DISRUPTED = "DISRUPTED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class CargoType(str, Enum):
    """Categorization of freight."""
    PHARMACEUTICALS = "PHARMACEUTICALS"
    PERISHABLE_FOOD = "PERISHABLE_FOOD"
    ELECTRONICS = "ELECTRONICS"
    CHEMICALS = "CHEMICALS"
    GENERAL_FREIGHT = "GENERAL_FREIGHT"


@dataclass
class TemperatureRequirement:
    """Thermal envelope specifications for sensitive cargo."""
    is_required: bool = False
    min_temp_c: Optional[float] = None
    max_temp_c: Optional[float] = None
    target_temp_c: Optional[float] = None
    tolerance_duration_minutes: int = 30  # Duration threshold before excursion alert

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemperatureRequirement":
        return cls(
            is_required=data.get("is_required", False),
            min_temp_c=data.get("min_temp_c"),
            max_temp_c=data.get("max_temp_c"),
            target_temp_c=data.get("target_temp_c"),
            tolerance_duration_minutes=data.get("tolerance_duration_minutes", 30),
        )


@dataclass
class CargoInfo:
    """Cargo package and product specifications."""
    product_name: str
    cargo_type: CargoType
    weight_kg: float
    volume_cbm: Optional[float] = None
    value_usd: Optional[float] = None
    is_hazardous: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["cargo_type"] = self.cargo_type.value if isinstance(self.cargo_type, CargoType) else self.cargo_type
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CargoInfo":
        cargo_type = data["cargo_type"]
        if isinstance(cargo_type, str):
            cargo_type = CargoType(cargo_type)
        return cls(
            product_name=data["product_name"],
            cargo_type=cargo_type,
            weight_kg=float(data["weight_kg"]),
            volume_cbm=data.get("volume_cbm"),
            value_usd=data.get("value_usd"),
            is_hazardous=data.get("is_hazardous", False),
        )


@dataclass
class RoutePoint:
    """Waypoint along a transit corridor."""
    name: str
    coordinates: Coordinates
    estimated_arrival: Optional[str] = None
    actual_arrival: Optional[str] = None
    is_passed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["coordinates"] = self.coordinates.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoutePoint":
        coords_raw = data["coordinates"]
        coords = Coordinates.from_dict(coords_raw) if isinstance(coords_raw, dict) else coords_raw
        return cls(
            name=data["name"],
            coordinates=coords,
            estimated_arrival=data.get("estimated_arrival"),
            actual_arrival=data.get("actual_arrival"),
            is_passed=data.get("is_passed", False),
        )


@dataclass
class Shipment:
    """Core shipment entity representing freight in transit."""
    shipment_id: str
    origin: Location
    destination: Location
    carrier: str
    status: ShipmentStatus
    cargo: CargoInfo
    temperature_requirement: TemperatureRequirement = field(default_factory=TemperatureRequirement)
    route_waypoints: List[RoutePoint] = field(default_factory=list)
    current_location: Optional[Coordinates] = None
    eta: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shipment_id": self.shipment_id,
            "origin": self.origin.to_dict(),
            "destination": self.destination.to_dict(),
            "carrier": self.carrier,
            "status": self.status.value if isinstance(self.status, ShipmentStatus) else self.status,
            "cargo": self.cargo.to_dict(),
            "temperature_requirement": self.temperature_requirement.to_dict(),
            "route_waypoints": [wp.to_dict() for wp in self.route_waypoints],
            "current_location": self.current_location.to_dict() if self.current_location else None,
            "eta": self.eta,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Shipment":
        origin = Location.from_dict(data["origin"]) if isinstance(data["origin"], dict) else data["origin"]
        destination = Location.from_dict(data["destination"]) if isinstance(data["destination"], dict) else data["destination"]
        status = ShipmentStatus(data["status"]) if isinstance(data["status"], str) else data["status"]
        cargo = CargoInfo.from_dict(data["cargo"]) if isinstance(data["cargo"], dict) else data["cargo"]
        
        temp_req_raw = data.get("temperature_requirement")
        temp_req = TemperatureRequirement.from_dict(temp_req_raw) if isinstance(temp_req_raw, dict) else (temp_req_raw or TemperatureRequirement())
        
        waypoints_raw = data.get("route_waypoints", [])
        waypoints = [RoutePoint.from_dict(wp) if isinstance(wp, dict) else wp for wp in waypoints_raw]
        
        cur_loc_raw = data.get("current_location")
        cur_loc = Coordinates.from_dict(cur_loc_raw) if isinstance(cur_loc_raw, dict) else cur_loc_raw
        
        return cls(
            shipment_id=data["shipment_id"],
            origin=origin,
            destination=destination,
            carrier=data["carrier"],
            status=status,
            cargo=cargo,
            temperature_requirement=temp_req,
            route_waypoints=waypoints,
            current_location=cur_loc,
            eta=data.get("eta"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
