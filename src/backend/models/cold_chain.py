"""Cold-chain monitoring and excursion domain models."""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict, Any

from .common import Coordinates


class ExcursionSeverity(str, Enum):
    """Classification of thermal deviation severity."""
    NORMAL = "NORMAL"
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    CRITICAL = "CRITICAL"


class ComplianceStatus(str, Enum):
    """Regulatory and quality assurance compliance classification."""
    COMPLIANT = "COMPLIANT"
    WARNING = "WARNING"
    NON_COMPLIANT_QUARANTINE = "NON_COMPLIANT_QUARANTINE"
    PRODUCT_REJECTED = "PRODUCT_REJECTED"


@dataclass
class TelemetryReading:
    """Time-series sensor reading captured during transit."""
    shipment_id: str
    timestamp: str
    temperature_c: float
    asset_id: Optional[str] = None
    humidity_pct: Optional[float] = None
    ambient_temp_c: Optional[float] = None
    battery_level_pct: Optional[float] = None
    door_opened: Optional[bool] = False
    location: Optional[Coordinates] = None
    sensor_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shipment_id": self.shipment_id,
            "timestamp": self.timestamp,
            "temperature_c": self.temperature_c,
            "asset_id": self.asset_id,
            "humidity_pct": self.humidity_pct,
            "ambient_temp_c": self.ambient_temp_c,
            "battery_level_pct": self.battery_level_pct,
            "door_opened": self.door_opened,
            "location": self.location.to_dict() if self.location else None,
            "sensor_id": self.sensor_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelemetryReading":
        loc_raw = data.get("location")
        loc = Coordinates.from_dict(loc_raw) if loc_raw and isinstance(loc_raw, dict) else loc_raw
        return cls(
            shipment_id=data["shipment_id"],
            timestamp=data["timestamp"],
            temperature_c=float(data["temperature_c"]),
            asset_id=data.get("asset_id"),
            humidity_pct=data.get("humidity_pct"),
            ambient_temp_c=data.get("ambient_temp_c"),
            battery_level_pct=data.get("battery_level_pct"),
            door_opened=data.get("door_opened", False),
            location=loc,
            sensor_id=data.get("sensor_id"),
        )


@dataclass
class ExcursionRecord:
    """Logged temperature violation event with regulatory severity scoring."""
    record_id: str
    shipment_id: str
    start_time: str
    end_time: Optional[str]
    duration_minutes: float
    target_min_temp_c: float
    target_max_temp_c: float
    min_temp_observed_c: float
    max_temp_observed_c: float
    mean_temp_c: float
    severity: ExcursionSeverity
    compliance_status: ComplianceStatus
    regulatory_framework: str = "FDA 21 CFR 211 / WHO GDP"
    corrective_action_required: str = ""
    is_acknowledged: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "shipment_id": self.shipment_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_minutes": self.duration_minutes,
            "target_min_temp_c": self.target_min_temp_c,
            "target_max_temp_c": self.target_max_temp_c,
            "min_temp_observed_c": self.min_temp_observed_c,
            "max_temp_observed_c": self.max_temp_observed_c,
            "mean_temp_c": self.mean_temp_c,
            "severity": self.severity.value if isinstance(self.severity, ExcursionSeverity) else self.severity,
            "compliance_status": self.compliance_status.value if isinstance(self.compliance_status, ComplianceStatus) else self.compliance_status,
            "regulatory_framework": self.regulatory_framework,
            "corrective_action_required": self.corrective_action_required,
            "is_acknowledged": self.is_acknowledged,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExcursionRecord":
        sev = ExcursionSeverity(data["severity"]) if isinstance(data["severity"], str) else data["severity"]
        comp = ComplianceStatus(data["compliance_status"]) if isinstance(data["compliance_status"], str) else data["compliance_status"]
        return cls(
            record_id=data["record_id"],
            shipment_id=data["shipment_id"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            duration_minutes=float(data["duration_minutes"]),
            target_min_temp_c=float(data["target_min_temp_c"]),
            target_max_temp_c=float(data["target_max_temp_c"]),
            min_temp_observed_c=float(data["min_temp_observed_c"]),
            max_temp_observed_c=float(data["max_temp_observed_c"]),
            mean_temp_c=float(data["mean_temp_c"]),
            severity=sev,
            compliance_status=comp,
            regulatory_framework=data.get("regulatory_framework", "FDA 21 CFR 211 / WHO GDP"),
            corrective_action_required=data.get("corrective_action_required", ""),
            is_acknowledged=data.get("is_acknowledged", False),
        )
