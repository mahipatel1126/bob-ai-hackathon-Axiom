"""Disruption domain models."""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict, Any, List

from .common import Coordinates


class DisruptionType(str, Enum):
    """Class of disruption affecting supply chain networks."""
    WEATHER = "WEATHER"
    PORT_CONGESTION = "PORT_CONGESTION"
    GEOPOLITICAL = "GEOPOLITICAL"
    LABOUR_STRIKE = "LABOUR_STRIKE"
    INFRASTRUCTURE_CLOSURE = "INFRASTRUCTURE_CLOSURE"
    CUSTOMS_DELAY = "CUSTOMS_DELAY"
    EQUIPMENT_FAILURE = "EQUIPMENT_FAILURE"


class DisruptionSeverity(str, Enum):
    """Impact severity level of a disruption."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Disruption:
    """Disruption incident impacting supply chain routes or nodes."""
    disruption_id: str
    title: str
    type: DisruptionType
    severity: DisruptionSeverity
    region_name: str
    center_coordinates: Coordinates
    impact_radius_km: float
    description: str
    is_active: bool = True
    start_time: Optional[str] = None
    estimated_end_time: Optional[str] = None
    source: Optional[str] = None
    affected_corridors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "disruption_id": self.disruption_id,
            "title": self.title,
            "type": self.type.value if isinstance(self.type, DisruptionType) else self.type,
            "severity": self.severity.value if isinstance(self.severity, DisruptionSeverity) else self.severity,
            "region_name": self.region_name,
            "center_coordinates": self.center_coordinates.to_dict(),
            "impact_radius_km": self.impact_radius_km,
            "description": self.description,
            "is_active": self.is_active,
            "start_time": self.start_time,
            "estimated_end_time": self.estimated_end_time,
            "source": self.source,
            "affected_corridors": self.affected_corridors,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Disruption":
        coords_raw = data["center_coordinates"]
        coords = Coordinates.from_dict(coords_raw) if isinstance(coords_raw, dict) else coords_raw
        dtype = DisruptionType(data["type"]) if isinstance(data["type"], str) else data["type"]
        sev = DisruptionSeverity(data["severity"]) if isinstance(data["severity"], str) else data["severity"]
        return cls(
            disruption_id=data["disruption_id"],
            title=data.get("title", data["disruption_id"]),
            type=dtype,
            severity=sev,
            region_name=data["region_name"],
            center_coordinates=coords,
            impact_radius_km=float(data.get("impact_radius_km", 50.0)),
            description=data["description"],
            is_active=data.get("is_active", True),
            start_time=data.get("start_time"),
            estimated_end_time=data.get("estimated_end_time"),
            source=data.get("source"),
            affected_corridors=data.get("affected_corridors", []),
        )
