"""Chain Guard AI - Operational Intelligence and Fleet Optimization Package.

L2 Supply Chain Disruption Assistant & Fleet Utilisation Optimizer.
"""

from src.ai.carrier import evaluate_carriers
from src.ai.cold_chain import analyze_temperature_readings
from src.ai.config import AIConfig, DEFAULT_CONFIG
from src.ai.demo_data import (
    get_all_demo_scenarios,
    get_scenario_1_normal_shipment,
    get_scenario_2_weather_disrupted_shipment,
    get_scenario_3_high_priority_pharma,
    get_scenario_4_and_5_fleet_assets,
    get_scenario_6_normal_cold_chain_readings,
    get_scenario_7_warning_cold_chain_readings,
    get_scenario_8_critical_cold_chain_readings,
)
from src.ai.disruption import (
    analyze_disruptions,
    analyze_single_disruption_impact,
    get_highest_disruption_impact,
)
from src.ai.fleet import (
    classify_fleet_asset,
    detect_idle_fleet,
    filter_suitable_vehicles,
)
from src.ai.models import (
    CargoType,
    CarrierOption,
    CarrierRecommendationResult,
    ColdChainAnalysisResult,
    Disruption,
    DisruptionImpactResult,
    DisruptionSeverity,
    DisruptionType,
    ExcursionEvent,
    FleetAsset,
    FleetAssignment,
    FleetAvailability,
    FleetOptimizationResult,
    FleetStatus,
    ImpactLevel,
    OperationalRecommendation,
    PriorityLevel,
    RiskLevel,
    RiskScoreResult,
    RouteOption,
    RouteRecommendationResult,
    Shipment,
    ShipmentStatus,
    TemperatureReading,
    TemperatureSeverity,
    VehicleType,
)
from src.ai.optimization import optimize_fleet_redeployment
from src.ai.recommendations import (
    generate_batch_recommendations,
    generate_operational_recommendation,
)
from src.ai.risk_scoring import calculate_shipment_risk

__all__ = [
    # Config
    "AIConfig",
    "DEFAULT_CONFIG",
    # Enums
    "PriorityLevel",
    "CargoType",
    "ShipmentStatus",
    "DisruptionType",
    "DisruptionSeverity",
    "ImpactLevel",
    "RiskLevel",
    "FleetAvailability",
    "FleetStatus",
    "VehicleType",
    "TemperatureSeverity",
    # Core Schemas
    "Shipment",
    "Disruption",
    "FleetAsset",
    "TemperatureReading",
    "RouteOption",
    "CarrierOption",
    # Result Schemas
    "DisruptionImpactResult",
    "RiskScoreResult",
    "RouteRecommendationResult",
    "CarrierRecommendationResult",
    "IdleFleetResult",
    "FleetAssignment",
    "FleetOptimizationResult",
    "ExcursionEvent",
    "ColdChainAnalysisResult",
    "OperationalRecommendation",
    # AI Engine Functions
    "analyze_single_disruption_impact",
    "analyze_disruptions",
    "get_highest_disruption_impact",
    "calculate_shipment_risk",
    "evaluate_routes",
    "evaluate_carriers",
    "classify_fleet_asset",
    "detect_idle_fleet",
    "filter_suitable_vehicles",
    "analyze_temperature_readings",
    "optimize_fleet_redeployment",
    "generate_operational_recommendation",
    "generate_batch_recommendations",
    # Demo Data Loaders
    "get_all_demo_scenarios",
    "get_scenario_1_normal_shipment",
    "get_scenario_2_weather_disrupted_shipment",
    "get_scenario_3_high_priority_pharma",
    "get_scenario_4_and_5_fleet_assets",
    "get_scenario_6_normal_cold_chain_readings",
    "get_scenario_7_warning_cold_chain_readings",
    "get_scenario_8_critical_cold_chain_readings",
]
