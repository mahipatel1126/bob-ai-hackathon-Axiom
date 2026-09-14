"""Tests for cold-chain excursion detection and severity classification."""

from datetime import datetime, timedelta
import pytest
from src.ai.cold_chain import analyze_temperature_readings
from src.ai.schemas import (
    CargoType,
    Shipment,
    TemperatureReading,
    TemperatureSeverity,
)


@pytest.fixture
def pharma_shipment():
    return Shipment(
        shipment_id="SHP-PHARMA-COLD",
        origin="Hyderabad",
        destination="Chennai",
        delivery_deadline=datetime(2026, 9, 15, 12, 0, 0),
        cargo_type=CargoType.PHARMA,
        temperature_required=True,
        required_min_temperature=2.0,
        required_max_temperature=8.0,
    )


def test_normal_in_spec_readings(pharma_shipment):
    now = datetime(2026, 9, 14, 12, 0, 0)
    readings = [
        TemperatureReading(
            timestamp=now - timedelta(minutes=i * 10),
            temperature=4.5,
            required_min_temperature=2.0,
            required_max_temperature=8.0,
        )
        for i in range(10)
    ]
    res = analyze_temperature_readings(pharma_shipment, readings)
    assert res.is_compliant is True
    assert res.has_excursions is False
    assert res.overall_severity == TemperatureSeverity.NORMAL
    assert len(res.events) == 0


def test_warning_excursion(pharma_shipment):
    now = datetime(2026, 9, 14, 12, 0, 0)
    # 8.8°C is 0.8°C above 8.0°C (under warning delta 1.5°C)
    readings = [
        TemperatureReading(
            timestamp=now - timedelta(minutes=15),
            temperature=4.5,
        ),
        TemperatureReading(
            timestamp=now - timedelta(minutes=10),
            temperature=8.8,
        ),
        TemperatureReading(
            timestamp=now - timedelta(minutes=5),
            temperature=4.5,
        ),
    ]
    res = analyze_temperature_readings(pharma_shipment, readings)
    assert res.is_compliant is False
    assert res.has_excursions is True
    assert res.overall_severity == TemperatureSeverity.WARNING
    assert len(res.events) == 1
    assert res.events[0].max_deviation_celsius == pytest.approx(0.8, 0.05)


def test_critical_excursion(pharma_shipment):
    now = datetime(2026, 9, 14, 12, 0, 0)
    # Severe temperature breach reaching 14.5°C for 2 hours
    readings = [
        TemperatureReading(
            timestamp=now - timedelta(minutes=120 - (i * 20)),
            temperature=14.5,
            required_min_temperature=2.0,
            required_max_temperature=8.0,
        )
        for i in range(7)
    ]
    res = analyze_temperature_readings(pharma_shipment, readings)
    assert res.is_compliant is False
    assert res.overall_severity == TemperatureSeverity.CRITICAL
    assert len(res.events) == 1
    assert res.events[0].duration_minutes >= 100.0
    assert any("IMMEDIATE ACTION" in r for r in res.recommendations)


def test_missing_telemetry_for_cold_chain(pharma_shipment):
    res = analyze_temperature_readings(pharma_shipment, [])
    assert res.is_compliant is False
    assert res.overall_severity == TemperatureSeverity.WARNING
    assert "No temperature telemetry" in res.explanation
