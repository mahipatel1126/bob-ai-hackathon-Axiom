"""Configuration and threshold definitions for Chain Guard AI."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RiskScoringWeights:
    """Configurable weights for multi-factor shipment risk scoring (sums to 1.0)."""
    disruption_severity: float = 0.30
    route_exposure: float = 0.20
    deadline_pressure: float = 0.20
    cargo_priority: float = 0.15
    cold_chain_sensitivity: float = 0.15


@dataclass
class RiskThresholds:
    """Thresholds for classifying 0-100 risk score into operational risk levels."""
    low_max: float = 29.0
    medium_max: float = 59.0
    high_max: float = 79.0
    # 80.0 to 100.0 is CRITICAL


@dataclass
class FleetUtilizationThresholds:
    """Thresholds for asset utilization classification."""
    idle_max: float = 0.15          # < 15% is IDLE
    underutilized_max: float = 0.50 # 15% - 50% is UNDERUTILIZED
    active_max: float = 0.85        # 50% - 85% is ACTIVE
    # > 85% is HIGH_UTILIZATION / ACTIVE


@dataclass
class ColdChainThresholds:
    """Thresholds for temperature excursion severity classification."""
    # Deviation beyond required bounds (in degrees Celsius)
    warning_temp_delta: float = 1.5    # <= 1.5°C over/under
    major_temp_delta: float = 4.0      # <= 4.0°C over/under
    # Excursion duration in minutes
    warning_duration_mins: float = 30.0
    major_duration_mins: float = 90.0
    # > 4.0°C delta or > 90 mins excursion is CRITICAL


@dataclass
class OptimizationWeights:
    """Weights for fleet redeployment matching objective function."""
    distance_weight: float = 0.35      # Minimize redeployment travel distance
    cost_weight: float = 0.25          # Minimize total redeployment cost
    utilization_gain_weight: float = 0.20  # Maximize idle fleet utilization gain
    risk_priority_weight: float = 0.20     # Prioritize high & critical risk shipments


@dataclass
class AIConfig:
    """Master configuration container for Chain Guard AI modules."""
    risk_weights: RiskScoringWeights = field(default_factory=RiskScoringWeights)
    risk_thresholds: RiskThresholds = field(default_factory=RiskThresholds)
    fleet_thresholds: FleetUtilizationThresholds = field(default_factory=FleetUtilizationThresholds)
    cold_chain_thresholds: ColdChainThresholds = field(default_factory=ColdChainThresholds)
    opt_weights: OptimizationWeights = field(default_factory=OptimizationWeights)
    
    # General parameters
    default_currency: str = "INR"
    distance_unit: str = "km"
    log_level: str = "INFO"


# Global default configuration instance
DEFAULT_CONFIG = AIConfig()
