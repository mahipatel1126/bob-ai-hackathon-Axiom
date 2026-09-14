"""Data and domain models for Chain Guard AI."""

from .common import Coordinates, Location
from .shipment import (
    Shipment,
    ShipmentStatus,
    CargoType,
    CargoInfo,
    TemperatureRequirement,
    RoutePoint,
)
from .disruption import (
    Disruption,
    DisruptionType,
    DisruptionSeverity,
)
from .fleet import (
    FleetAsset,
    AssetType,
    AssetStatus,
    ReeferCapability,
)
from .cold_chain import (
    TelemetryReading,
    ExcursionRecord,
    ExcursionSeverity,
    ComplianceStatus,
)
from .recommendation import (
    RouteAlternative,
    CarrierOption,
    RerouteRecommendation,
    RedeploymentRequest,
    TransportMode,
    RecommendationStatus,
    RedeploymentUrgency,
    RedeploymentStatus,
)

__all__ = [
    # Common
    "Coordinates",
    "Location",
    # Shipment
    "Shipment",
    "ShipmentStatus",
    "CargoType",
    "CargoInfo",
    "TemperatureRequirement",
    "RoutePoint",
    # Disruption
    "Disruption",
    "DisruptionType",
    "DisruptionSeverity",
    # Fleet
    "FleetAsset",
    "AssetType",
    "AssetStatus",
    "ReeferCapability",
    # Cold Chain
    "TelemetryReading",
    "ExcursionRecord",
    "ExcursionSeverity",
    "ComplianceStatus",
    # Recommendations & Optimization interfaces
    "RouteAlternative",
    "CarrierOption",
    "RerouteRecommendation",
    "RedeploymentRequest",
    "TransportMode",
    "RecommendationStatus",
    "RedeploymentUrgency",
    "RedeploymentStatus",
]
