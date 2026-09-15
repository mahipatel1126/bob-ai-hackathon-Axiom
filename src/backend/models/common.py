"""Common value objects and geometric representations."""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class Coordinates:
    """Geographic coordinates (latitude, longitude)."""
    latitude: float
    longitude: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Coordinates":
        return cls(
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
        )


@dataclass
class Location:
    """Supply chain node location (port, depot, warehouse, customer site)."""
    name: str
    city: str
    country: str
    coordinates: Optional[Coordinates] = None
    facility_type: Optional[str] = None  # e.g., "PORT", "WAREHOUSE", "AIRPORT", "DEPOT"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.coordinates:
            d["coordinates"] = self.coordinates.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Location":
        coords_raw = data.get("coordinates")
        coords = None
        if coords_raw:
            coords = Coordinates.from_dict(coords_raw) if isinstance(coords_raw, dict) else coords_raw
        return cls(
            name=data["name"],
            city=data["city"],
            country=data["country"],
            coordinates=coords,
            facility_type=data.get("facility_type"),
        )
