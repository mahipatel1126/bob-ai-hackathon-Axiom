"""Explainable multi-factor shipment risk scoring engine."""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from src.ai.config import AIConfig, DEFAULT_CONFIG
from src.ai.schemas import (
    ColdChainAnalysisResult,
    DisruptionImpactResult,
    ImpactLevel,
    PriorityLevel,
    RiskLevel,
    RiskScoreResult,
    Shipment,
    ShipmentStatus,
    TemperatureSeverity,
)


def calculate_shipment_risk(
    shipment: Shipment,
    disruption_impact: Optional[DisruptionImpactResult] = None,
    cold_chain_status: Optional[ColdChainAnalysisResult] = None,
    current_time: Optional[datetime] = None,
    config: Optional[AIConfig] = None,
) -> RiskScoreResult:
    """Calculate an explainable 0-100 risk score for a shipment.
    
    Factors Evaluated:
    1. Disruption Severity & Direct Impact (Weight ~ 0.30)
    2. Route Exposure & Delay Magnitude (Weight ~ 0.20)
    3. Delivery Deadline Pressure / ETA Slack (Weight ~ 0.20)
    4. Cargo Priority & Value (Weight ~ 0.15)
    5. Cold-Chain Temperature Sensitivity & Excursions (Weight ~ 0.15)
    """
    cfg = config or DEFAULT_CONFIG
    w = cfg.risk_weights
    t = cfg.risk_thresholds

    # Terminal state check
    if shipment.status == ShipmentStatus.DELIVERED:
        return RiskScoreResult(
            shipment_id=shipment.shipment_id,
            score=0.0,
            risk_level=RiskLevel.LOW,
            contributing_factors={
                "disruption_severity": 0.0,
                "route_exposure": 0.0,
                "deadline_pressure": 0.0,
                "cargo_priority": 0.0,
                "cold_chain_sensitivity": 0.0,
            },
            factor_explanations={
                "status": "Shipment has already been successfully delivered."
            },
            explanation="Risk is 0 (LOW) because the shipment has already reached its final destination.",
            mitigation_urgency=PriorityLevel.LOW,
        )

    # 1. Disruption Severity Sub-score (0 to 100)
    disruption_sub = 0.0
    disruption_text = "No active disruption intersecting route."
    if disruption_impact and disruption_impact.affected:
        level_map = {
            ImpactLevel.CRITICAL: 100.0,
            ImpactLevel.HIGH: 75.0,
            ImpactLevel.MEDIUM: 45.0,
            ImpactLevel.LOW: 20.0,
            ImpactLevel.NONE: 0.0,
        }
        disruption_sub = level_map.get(disruption_impact.impact_level, 0.0)
        disruption_text = (
            f"Impact level is {disruption_impact.impact_level.value} due to active disruption "
            f"'{disruption_impact.disruption_id}' impacting points: {', '.join(disruption_impact.intersecting_locations)}."
        )

    # 2. Route Exposure & Delay Sub-score (0 to 100)
    delay_hours = disruption_impact.estimated_delay_hours if disruption_impact else 0.0
    if delay_hours >= 12.0:
        exposure_sub = 100.0
    elif delay_hours >= 6.0:
        exposure_sub = 75.0
    elif delay_hours >= 2.0:
        exposure_sub = 45.0
    elif delay_hours > 0:
        exposure_sub = 20.0
    else:
        exposure_sub = 0.0
    exposure_text = f"Projected delay is {delay_hours:.1f} hours across transit corridor."

    # 3. Deadline Pressure Sub-score (0 to 100)
    now = current_time or datetime.now(timezone.utc).replace(tzinfo=None)
    try:
        slack_hours = (shipment.delivery_deadline - now).total_seconds() / 3600.0
        # If remaining time is less than ETA + estimated delay
        required_time = shipment.eta_hours_remaining + delay_hours
        buffer = slack_hours - required_time
        if buffer < -4.0:
            deadline_sub = 100.0
            deadline_text = f"Severe deadline breach expected! Deficit is {abs(buffer):.1f} hours."
        elif buffer < 0.0:
            deadline_sub = 80.0
            deadline_text = f"Projected to miss deadline by {abs(buffer):.1f} hours."
        elif buffer < 4.0:
            deadline_sub = 55.0
            deadline_text = f"Tight delivery buffer remaining ({buffer:.1f}h slack)."
        elif buffer < 12.0:
            deadline_sub = 25.0
            deadline_text = f"Moderate buffer remaining ({buffer:.1f}h slack)."
        else:
            deadline_sub = 5.0
            deadline_text = f"Ample delivery window buffer ({buffer:.1f}h slack)."
    except Exception:
        deadline_sub = 20.0
        deadline_text = "Standard delivery window timeline assumed."

    # 4. Cargo Priority Sub-score (0 to 100)
    priority_map = {
        PriorityLevel.CRITICAL: 100.0,
        PriorityLevel.HIGH: 70.0,
        PriorityLevel.MEDIUM: 40.0,
        PriorityLevel.LOW: 15.0,
    }
    priority_sub = priority_map.get(shipment.priority, 40.0)
    # Scale slightly if high commercial value
    if shipment.value_inr > 500000:
        priority_sub = min(100.0, priority_sub + 15.0)
    priority_text = f"Cargo priority is {shipment.priority.value} (Cargo type: {shipment.cargo_type.value}, Value: INR {shipment.value_inr:,.0f})."

    # 5. Cold Chain Sensitivity & Excursions Sub-score (0 to 100)
    cold_chain_sub = 0.0
    if shipment.temperature_required:
        if cold_chain_status and cold_chain_status.has_excursions:
            sev_map = {
                TemperatureSeverity.CRITICAL: 100.0,
                TemperatureSeverity.MAJOR: 80.0,
                TemperatureSeverity.WARNING: 50.0,
                TemperatureSeverity.NORMAL: 15.0,
            }
            cold_chain_sub = sev_map.get(cold_chain_status.overall_severity, 50.0)
            cold_chain_text = (
                f"Temperature excursion detected: Severity is {cold_chain_status.overall_severity.value} "
                f"with {len(cold_chain_status.events)} excursion incident(s)."
            )
        else:
            cold_chain_sub = 20.0  # Base sensitivity for active cold chain
            cold_chain_text = f"Temperature-controlled cargo ({shipment.required_min_temperature}°C to {shipment.required_max_temperature}°C) currently within safe bounds."
    else:
        cold_chain_sub = 0.0
        cold_chain_text = "Standard dry cargo (no temperature control required)."

    # Composite Weighted Calculation
    # Normalizing weights if cold chain is not required to prevent diluting score
    effective_w_cc = w.cold_chain_sensitivity if shipment.temperature_required else 0.0
    weight_sum = w.disruption_severity + w.route_exposure + w.deadline_pressure + w.cargo_priority + effective_w_cc
    
    norm_w_dis = w.disruption_severity / weight_sum
    norm_w_exp = w.route_exposure / weight_sum
    norm_w_dl = w.deadline_pressure / weight_sum
    norm_w_pri = w.cargo_priority / weight_sum
    norm_w_cc = effective_w_cc / weight_sum

    raw_score = (
        disruption_sub * norm_w_dis +
        exposure_sub * norm_w_exp +
        deadline_sub * norm_w_dl +
        priority_sub * norm_w_pri +
        cold_chain_sub * norm_w_cc
    )

    final_score = round(max(0.0, min(100.0, raw_score)), 1)

    # Classify Risk Level
    if final_score <= t.low_max:
        risk_level = RiskLevel.LOW
        mitigation_urgency = PriorityLevel.LOW
    elif final_score <= t.medium_max:
        risk_level = RiskLevel.MEDIUM
        mitigation_urgency = PriorityLevel.MEDIUM
    elif final_score <= t.high_max:
        risk_level = RiskLevel.HIGH
        mitigation_urgency = PriorityLevel.HIGH
    else:
        risk_level = RiskLevel.CRITICAL
        mitigation_urgency = PriorityLevel.CRITICAL

    # Narrative explanation
    factors_summary = []
    if disruption_sub >= 45:
        factors_summary.append("active corridor disruption")
    if deadline_sub >= 55:
        factors_summary.append("strict delivery timeline risk")
    if cold_chain_sub >= 50:
        factors_summary.append("temperature excursion alert")
    if priority_sub >= 70:
        factors_summary.append(f"high-priority {shipment.cargo_type.value} cargo")

    if factors_summary:
        explanation = (
            f"Risk score is {final_score:.1f}/100 ({risk_level.value}) driven by "
            f"{', '.join(factors_summary)}."
        )
    else:
        explanation = (
            f"Risk score is {final_score:.1f}/100 ({risk_level.value}) as shipment is operating "
            f"within standard transit safety and timeline parameters."
        )

    return RiskScoreResult(
        shipment_id=shipment.shipment_id,
        score=final_score,
        risk_level=risk_level,
        contributing_factors={
            "disruption_severity": round(disruption_sub, 1),
            "route_exposure": round(exposure_sub, 1),
            "deadline_pressure": round(deadline_sub, 1),
            "cargo_priority": round(priority_sub, 1),
            "cold_chain_sensitivity": round(cold_chain_sub, 1),
        },
        factor_explanations={
            "disruption_severity": disruption_text,
            "route_exposure": exposure_text,
            "deadline_pressure": deadline_text,
            "cargo_priority": priority_text,
            "cold_chain_sensitivity": cold_chain_text,
        },
        explanation=explanation,
        mitigation_urgency=mitigation_urgency,
    )
