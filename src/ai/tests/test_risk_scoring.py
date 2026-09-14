"""Tests for multi-factor explainable risk scoring."""

from datetime import datetime, timedelta
import pytest
from src.ai.config import AIConfig
from src.ai.risk_scoring import calculate_shipment_risk
from src.ai.schemas import (
    CargoType,
    ColdChainAnalysisResult,
    DisruptionImpactResult,
    ExcursionEvent,
    ImpactLevel,
    PriorityLevel,
    RiskLevel,
    Shipment,
    ShipmentStatus,
    TemperatureSeverity,
)


@pytest.fixture
def base_time():
    return datetime(2026, 9, 14, 12, 0, 0)


def test_nominal_risk_score(base_time):
    shipment = Shipment(
        shipment_id="SHP-LOW-RISK",
        origin="Pune",
        destination="Mumbai",
        route=["Pune", "Lonavala", "Navi Mumbai", "Mumbai"],
        priority=PriorityLevel.LOW,
        delivery_deadline=base_time + timedelta(hours=48),
        cargo_type=CargoType.DRY,
        status=ShipmentStatus.IN_TRANSIT,
        eta_hours_remaining=4.0,
    )
    res = calculate_shipment_risk(shipment, current_time=base_time)
    assert res.score <= 29.0
    assert res.risk_level == RiskLevel.LOW
    assert "status" in res.factor_explanations or "disruption_severity" in res.contributing_factors


def test_critical_risk_score_with_disruption_and_deadline(base_time):
    shipment = Shipment(
        shipment_id="SHP-CRIT-RISK",
        origin="Mumbai",
        destination="Delhi",
        route=["Mumbai", "Surat", "Delhi"],
        priority=PriorityLevel.CRITICAL,
        delivery_deadline=base_time + timedelta(hours=5),
        cargo_type=CargoType.PHARMA,
        temperature_required=True,
        required_min_temperature=2.0,
        required_max_temperature=8.0,
        status=ShipmentStatus.IN_TRANSIT,
        eta_hours_remaining=6.0,
        value_inr=1500000.0,
    )
    impact = DisruptionImpactResult(
        shipment_id=shipment.shipment_id,
        affected=True,
        disruption_id="DIS-FLOOD",
        impact_level=ImpactLevel.CRITICAL,
        reasons=["Direct corridor hit"],
        estimated_delay_hours=12.0,
        intersecting_locations=["Surat"],
    )
    cold_chain = ColdChainAnalysisResult(
        shipment_id=shipment.shipment_id,
        readings_count=5,
        has_excursions=True,
        overall_severity=TemperatureSeverity.CRITICAL,
        is_compliant=False,
        explanation="Temp reached 14°C",
    )

    res = calculate_shipment_risk(
        shipment=shipment,
        disruption_impact=impact,
        cold_chain_status=cold_chain,
        current_time=base_time,
    )
    assert res.score >= 80.0
    assert res.risk_level == RiskLevel.CRITICAL
    assert res.mitigation_urgency == PriorityLevel.CRITICAL
    assert len(res.explanation) > 10


def test_delivered_shipment_has_zero_risk(base_time):
    shipment = Shipment(
        shipment_id="SHP-DONE",
        origin="Pune",
        destination="Mumbai",
        delivery_deadline=base_time,
        status=ShipmentStatus.DELIVERED,
    )
    res = calculate_shipment_risk(shipment, current_time=base_time)
    assert res.score == 0.0
    assert res.risk_level == RiskLevel.LOW
    assert res.mitigation_urgency == PriorityLevel.LOW


def test_explainable_contributing_factors(base_time):
    shipment = Shipment(
        shipment_id="SHP-EXP",
        origin="Delhi",
        destination="Agra",
        priority=PriorityLevel.HIGH,
        delivery_deadline=base_time + timedelta(hours=10),
        status=ShipmentStatus.IN_TRANSIT,
        eta_hours_remaining=3.0,
    )
    res = calculate_shipment_risk(shipment, current_time=base_time)
    assert "disruption_severity" in res.contributing_factors
    assert "route_exposure" in res.contributing_factors
    assert "deadline_pressure" in res.contributing_factors
    assert "cargo_priority" in res.contributing_factors
    assert "cold_chain_sensitivity" in res.contributing_factors
