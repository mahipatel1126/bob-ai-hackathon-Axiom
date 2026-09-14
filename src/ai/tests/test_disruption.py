"""Tests for disruption impact analysis."""

from datetime import datetime, timedelta
import pytest
from src.ai.disruption import (
    analyze_disruptions,
    analyze_single_disruption_impact,
    get_highest_disruption_impact,
)
from src.ai.schemas import (
    CargoType,
    Disruption,
    DisruptionSeverity,
    DisruptionType,
    ImpactLevel,
    PriorityLevel,
    Shipment,
    ShipmentStatus,
)


@pytest.fixture
def base_time():
    return datetime(2026, 9, 14, 12, 0, 0)


@pytest.fixture
def sample_shipment(base_time):
    return Shipment(
        shipment_id="SHP-TEST-01",
        origin="Mumbai",
        destination="Delhi",
        route=["Mumbai", "Surat", "Vadodara", "Ahmedabad", "Jaipur", "Delhi"],
        priority=PriorityLevel.HIGH,
        delivery_deadline=base_time + timedelta(hours=20),
        cargo_type=CargoType.DRY,
        status=ShipmentStatus.IN_TRANSIT,
        eta_hours_remaining=15.0,
    )


@pytest.fixture
def active_disruption(base_time):
    return Disruption(
        disruption_id="DIS-TEST-FLOOD",
        type=DisruptionType.FLOOD,
        location="Surat",
        severity=DisruptionSeverity.CRITICAL,
        start_time=base_time - timedelta(hours=1),
        estimated_duration_hours=12.0,
        affected_routes=["NH48-Surat"],
        affected_locations=["Surat"],
        description="Flash floods blocking NH48 near Surat",
        delay_impact_hours=10.0,
    )


def test_affected_shipment_detected(sample_shipment, active_disruption, base_time):
    res = analyze_single_disruption_impact(sample_shipment, active_disruption, current_time=base_time)
    assert res.affected is True
    assert res.disruption_id == "DIS-TEST-FLOOD"
    assert res.impact_level in (ImpactLevel.HIGH, ImpactLevel.CRITICAL)
    assert "Surat" in res.intersecting_locations
    assert len(res.reasons) > 0
    assert res.estimated_delay_hours > 0


def test_unaffected_shipment(base_time):
    shipment = Shipment(
        shipment_id="SHP-UNAFFECTED",
        origin="Bengaluru",
        destination="Chennai",
        route=["Bengaluru", "Hosur", "Vellore", "Chennai"],
        delivery_deadline=base_time + timedelta(hours=24),
        status=ShipmentStatus.IN_TRANSIT,
    )
    disruption = Disruption(
        disruption_id="DIS-KOLKATA",
        type=DisruptionType.PORT_CONGESTION,
        location="Kolkata",
        severity=DisruptionSeverity.HIGH,
        start_time=base_time,
        affected_locations=["Kolkata", "Haldia"],
    )
    res = analyze_single_disruption_impact(shipment, disruption, current_time=base_time)
    assert res.affected is False
    assert res.impact_level == ImpactLevel.NONE
    assert res.estimated_delay_hours == 0.0


def test_delivered_shipment_ignored(sample_shipment, active_disruption, base_time):
    sample_shipment.status = ShipmentStatus.DELIVERED
    res = analyze_single_disruption_impact(sample_shipment, active_disruption, current_time=base_time)
    assert res.affected is False
    assert res.impact_level == ImpactLevel.NONE


def test_get_highest_disruption_impact_multiple(sample_shipment, active_disruption, base_time):
    minor_disruption = Disruption(
        disruption_id="DIS-MINOR",
        type=DisruptionType.ROAD_CLOSURE,
        location="Jaipur",
        severity=DisruptionSeverity.LOW,
        start_time=base_time,
        estimated_duration_hours=2.0,
        affected_locations=["Jaipur"],
        delay_impact_hours=1.0,
    )
    highest = get_highest_disruption_impact(
        sample_shipment, [minor_disruption, active_disruption], current_time=base_time
    )
    assert highest.disruption_id == "DIS-TEST-FLOOD"
    assert highest.impact_level == ImpactLevel.CRITICAL


def test_empty_disruptions_list(sample_shipment):
    res = get_highest_disruption_impact(sample_shipment, [])
    assert res.affected is False
    assert res.impact_level == ImpactLevel.NONE
