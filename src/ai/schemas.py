"""Data models and schemas for Chain Guard AI."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PriorityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CargoType(str, Enum):
    DRY = "DRY"
    PERISHABLE = "PERISHABLE"
    PHARMA = "PHARMA"
    CHEMICAL = "CHEMICAL"
    HAZARDOUS = "HAZARDOUS"
    ELECTRONICS = "ELECTRONICS"


class ShipmentStatus(str, Enum):
    CREATED = "CREATED"
    IN_TRANSIT = "IN_TRANSIT"
    DELAYED = "DELAYED"
    AT_RISK = "AT_RISK"
    REROUTED = "REROUTED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class DisruptionType(str, Enum):
    WEATHER = "WEATHER"
    PORT_CONGESTION = "PORT_CONGESTION"
    ROAD_CLOSURE = "ROAD_CLOSURE"
    STRIKE = "STRIKE"
    MECHANICAL = "MECHANICAL"
    CUSTOMS_DELAY = "CUSTOMS_DELAY"
    ACCIDENT = "ACCIDENT"
    FLOOD = "FLOOD"


class DisruptionSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ImpactLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FleetAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"
    RESERVED = "RESERVED"


class FleetStatus(str, Enum):
    IDLE = "IDLE"
    UNDERUTILIZED = "UNDERUTILIZED"
    ACTIVE = "ACTIVE"
    UNAVAILABLE = "UNAVAILABLE"


class VehicleType(str, Enum):
    VAN = "VAN"
    REEFER_TRUCK = "REEFER_TRUCK"
    FLATBED = "FLATBED"
    BOX_TRUCK = "BOX_TRUCK"
    CONTAINER_CARRIER = "CONTAINER_CARRIER"


class TemperatureSeverity(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"


# ---------------------------------------------------------------------------
# Core Entities (Input Schemas)
# ---------------------------------------------------------------------------

class Shipment(BaseModel):
    """Shipment data model representing goods in transit."""
    shipment_id: str
    origin: str
    destination: str
    route: List[str] = Field(
        default_factory=list,
        description="Ordered list of transit corridors/waypoints (e.g. ['Mumbai', 'Nashik', 'Indore', 'Delhi'])"
    )
    carrier: str = "In-House Logistics"
    priority: PriorityLevel = PriorityLevel.MEDIUM
    delivery_deadline: datetime
    cargo_type: CargoType = CargoType.DRY
    temperature_required: bool = False
    required_min_temperature: Optional[float] = None
    required_max_temperature: Optional[float] = None
    weight_kg: float = 1000.0
    volume_cbm: float = 5.0
    value_inr: float = 100000.0
    status: ShipmentStatus = ShipmentStatus.IN_TRANSIT
    current_location: Optional[str] = None
    eta_hours_remaining: float = 12.0


class Disruption(BaseModel):
    """External supply chain disruption event."""
    disruption_id: str
    type: DisruptionType
    location: str
    region: Optional[str] = None
    severity: DisruptionSeverity
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    estimated_duration_hours: float = 8.0
    affected_routes: List[str] = Field(
        default_factory=list,
        description="Corridors or route segment tags affected"
    )
    affected_locations: List[str] = Field(
        default_factory=list,
        description="Specific cities, waypoints, or hubs impacted"
    )
    description: str = "Active supply chain disruption"
    delay_impact_hours: float = 6.0


class FleetAsset(BaseModel):
    """Fleet vehicle / asset telemetry and capacity."""
    vehicle_id: str
    vehicle_type: VehicleType
    capacity_kg: float
    capacity_cbm: float = 20.0
    current_location: str
    availability: FleetAvailability = FleetAvailability.AVAILABLE
    current_utilization: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Current utilization fraction from 0.0 to 1.0"
    )
    temperature_capability: bool = False
    min_temp_capable: Optional[float] = None
    max_temp_capable: Optional[float] = None
    cost_per_km: float = 25.0
    driver_name: Optional[str] = None
    status: FleetStatus = FleetStatus.IDLE


class TemperatureReading(BaseModel):
    """IoT cold-chain telemetry record."""
    reading_id: Optional[str] = None
    shipment_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    temperature: float
    required_min_temperature: float = 2.0
    required_max_temperature: float = 8.0
    ambient_temperature: Optional[float] = 28.0
    humidity_percent: Optional[float] = 60.0
    battery_level_percent: Optional[float] = 95.0


class RouteOption(BaseModel):
    """Candidate route alternative for rerouting."""
    route_id: str
    name: str
    waypoints: List[str] = Field(default_factory=list)
    distance_km: float
    estimated_time_hours: float
    estimated_cost: float
    risk_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Estimated disruption exposure score 0-100"
    )
    disruption_exposure: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Fraction of route affected by disruption (0.0 to 1.0)"
    )
    road_condition_score: float = 0.85
    toll_charges: float = 500.0
    notes: Optional[str] = None


class CarrierOption(BaseModel):
    """Alternative 3PL or partner carrier for dynamic capacity allocation."""
    carrier_id: str
    name: str
    available_capacity_kg: float
    estimated_cost: float
    reliability_score: float = Field(
        default=0.90,
        ge=0.0,
        le=1.0,
        description="Historical on-time & safety score (0.0 to 1.0)"
    )
    estimated_delivery_hours: float
    temperature_capable: bool = False
    rating: float = 4.5
    contact_phone: Optional[str] = None


# ---------------------------------------------------------------------------
# Output / Result Schemas
# ---------------------------------------------------------------------------

class DisruptionImpactResult(BaseModel):
    """Result of analyzing disruption impact on a shipment."""
    shipment_id: str
    affected: bool
    disruption_id: Optional[str] = None
    impact_level: ImpactLevel = ImpactLevel.NONE
    reasons: List[str] = Field(default_factory=list)
    estimated_delay_hours: float = 0.0
    intersecting_locations: List[str] = Field(default_factory=list)


class RiskScoreResult(BaseModel):
    """Explainable multi-factor shipment risk assessment."""
    shipment_id: str
    score: float = Field(..., ge=0.0, le=100.0, description="Risk score 0-100")
    risk_level: RiskLevel
    contributing_factors: Dict[str, float] = Field(
        default_factory=dict,
        description="Weighted sub-scores for each risk component"
    )
    factor_explanations: Dict[str, str] = Field(
        default_factory=dict,
        description="Human-readable explanation for each factor"
    )
    explanation: str
    mitigation_urgency: PriorityLevel


class RouteRecommendationResult(BaseModel):
    """Ranked route recommendations with explicit rationale."""
    shipment_id: str
    recommended_route: Optional[RouteOption] = None
    ranked_routes: List[RouteOption] = Field(default_factory=list)
    selection_reason: str
    score_breakdown: Dict[str, float] = Field(default_factory=dict)


class CarrierRecommendationResult(BaseModel):
    """Ranked carrier recommendations with capacity & compliance checks."""
    shipment_id: str
    recommended_carrier: Optional[CarrierOption] = None
    ranked_carriers: List[CarrierOption] = Field(default_factory=list)
    selection_reason: str
    rejected_carriers: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of rejected carriers with rejection reasons"
    )


class IdleFleetResult(BaseModel):
    """Detection and categorization of fleet assets."""
    idle_vehicles: List[FleetAsset] = Field(default_factory=list)
    underutilized_vehicles: List[FleetAsset] = Field(default_factory=list)
    active_vehicles: List[FleetAsset] = Field(default_factory=list)
    unavailable_vehicles: List[FleetAsset] = Field(default_factory=list)
    total_assets: int = 0
    idle_count: int = 0
    utilization_rate_avg: float = 0.0
    explanation: str = ""


class FleetAssignment(BaseModel):
    """Optimal assignment of an idle/underutilized asset to an at-risk shipment."""
    vehicle_id: str
    vehicle_type: VehicleType
    shipment_id: str
    origin_distance_km: float
    redeployment_cost: float
    current_utilization: float
    projected_utilization: float
    utilization_improvement: float
    benefit_score: float
    reason: str


class FleetOptimizationResult(BaseModel):
    """Global optimization result for fleet redeployment."""
    assignments: List[FleetAssignment] = Field(default_factory=list)
    unassigned_shipments: List[str] = Field(default_factory=list)
    unused_vehicles: List[str] = Field(default_factory=list)
    total_redeployment_cost: float = 0.0
    average_utilization_improvement: float = 0.0
    optimization_method: str = "Greedy Heuristic / Mixed Integer Linear Program"
    explanation: str = ""


class ExcursionEvent(BaseModel):
    """Cold-chain temperature violation segment."""
    excursion_id: str
    target_id: str = Field(description="Shipment or Vehicle ID")
    start_time: datetime
    end_time: datetime
    duration_minutes: float
    min_recorded_temp: float
    max_recorded_temp: float
    required_min: float
    required_max: float
    max_deviation_celsius: float
    severity: TemperatureSeverity
    is_ongoing: bool = False
    explanation: str


class ColdChainAnalysisResult(BaseModel):
    """Complete cold-chain temperature telemetry audit and severity classification."""
    shipment_id: str
    readings_count: int
    has_excursions: bool
    events: List[ExcursionEvent] = Field(default_factory=list)
    overall_severity: TemperatureSeverity = TemperatureSeverity.NORMAL
    is_compliant: bool = True
    mean_temperature: float = 0.0
    min_temperature: float = 0.0
    max_temperature: float = 0.0
    recommendations: List[str] = Field(default_factory=list)
    explanation: str


class OperationalRecommendation(BaseModel):
    """Unified L2 Operational Intelligence Action Package."""
    recommendation_id: str
    shipment_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    action_summary: str
    priority: PriorityLevel
    reasons: List[str] = Field(default_factory=list)
    impact_analysis: DisruptionImpactResult
    risk_assessment: RiskScoreResult
    route_recommendation: Optional[RouteRecommendationResult] = None
    carrier_recommendation: Optional[CarrierRecommendationResult] = None
    fleet_assignment: Optional[FleetAssignment] = None
    cold_chain_status: Optional[ColdChainAnalysisResult] = None
    executive_summary: str