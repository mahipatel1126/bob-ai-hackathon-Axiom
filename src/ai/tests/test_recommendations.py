"""Tests for unified operational recommendation pipeline."""

from datetime import datetime, timedelta
import pytest
from src.ai.recommendations import (
    generate_batch_recommendations,
    generate_operational_recommendation,
)
from src.ai.schemas import (
    CargoType,
    CarrierOption,
    Disruption,
    DisruptionSeverity,
    DisruptionType,
    FleetAsset,
    FleetAvailability,
    PriorityLevel,
    RiskLevel,
    RouteOption,
    Shipment,
    ShipmentStatus,
    TemperatureReading,
    VehicleType,
)


@pytest.fixture
def base_time():
    return datetime(2026, 9, 14, 10, 0, 0)


def test_end_to_end_operational_recommendation(base_time):
    shipment = Shipment(
        shipment_id="SHP-E2E-01",
        origin="Mumbai",
        destination="Delhi",
        route=["Mumbai", "Surat", "Vadodara", "Delhi"],
        priority=PriorityLevel.CRITICAL,
        delivery_deadline=base_time + timedelta(hours=14),
        cargo_type=CargoType.PHARMA,
        temperature_required=True,
        required_min_temperature=2.0,
        required_max_temperature=8.0,
        weight_kg=2000.0,
        status=ShipmentStatus.IN_TRANSIT,
        current_location="Mumbai",
        eta_hours_remaining=12.0,
    )

    disruptions = [
        Disruption(
            disruption_id="DIS-FLOOD-SURAT",
            type=DisruptionType.FLOOD,
            location="Surat",
            severity=DisruptionSeverity.CRITICAL,
            start_time=base_time - timedelta(hours=1),
            estimated_duration_hours=12.0,
            affected_locations=["Surat"],
            delay_impact_hours=10.0,
        )
    ]

    candidate_routes = [
        RouteOption(
            route_id="RT-DIRECT-SURAT",
            name="NH48 Coastal Corridor",
            waypoints=["Mumbai", "Surat", "Vadodara", "Delhi"],
            distance_km=1420.0,
            estimated_time_hours=22.0,
            estimated_cost=40000.0,
            risk_score=90.0,
            disruption_exposure=0.70,
        ),
        RouteOption(
            route_id="RT-INLAND-INDORE",
            name="NH52 Inland Corridor via Indore",
            waypoints=["Mumbai", "Nashik", "Indore", "Delhi"],
            distance_km=1480.0,
            estimated_time_hours=24.0,
            estimated_cost=44000.0,
            risk_score=5.0,
            disruption_exposure=0.0,
        ),
    ]

    available_fleet = [
        FleetAsset(
            vehicle_id="FLT-MUMBAI-REEFER",
            vehicle_type=VehicleType.REEFER_TRUCK,
            capacity_kg=3500.0,
            current_location="Mumbai",
            availability=FleetAvailability.AVAILABLE,
            current_utilization=0.10,
            temperature_capability=True,
            min_temp_capable=-10.0,
            max_temp_capable=10.0,
        )
    ]

    readings = [
        TemperatureReading(
            timestamp=base_time - timedelta(minutes=i * 10),
            temperature=4.5,
            required_min_temperature=2.0,
            required_max_temperature=8.0,
        )
        for i in range(6)
    ]

    rec = generate_operational_recommendation(
        shipment=shipment,
        disruptions=disruptions,
        candidate_routes=candidate_routes,
        available_fleet=available_fleet,
        temperature_readings=readings,
        current_time=base_time,
    )

    assert rec.shipment_id == "SHP-E2E-01"
    assert rec.priority in (PriorityLevel.HIGH, PriorityLevel.CRITICAL)
    assert rec.risk_assessment.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
    assert rec.route_recommendation is not None
    assert rec.route_recommendation.recommended_route.route_id == "RT-INLAND-INDORE"
    assert rec.fleet_assignment is not None
    assert rec.fleet_assignment.vehicle_id == "FLT-MUMBAI-REEFER"
    assert rec.cold_chain_status.is_compliant is True
    assert len(rec.reasons) >= 2
    assert "Reroute" in rec.action_summary or "Dispatch" in rec.action_summary or "Assign" in rec.action_summary


def test_batch_recommendations(base_time):
    s1 = Shipment(
        shipment_id="SHP-BATCH-1",
        origin="Pune",
        destination="Mumbai",
        delivery_deadline=base_time + timedelta(hours=24),
        priority=PriorityLevel.LOW,
    )
    s2 = Shipment(
        shipment_id="SHP-BATCH-2",
        origin="Mumbai",
        destination="Delhi",
        route=["Mumbai", "Surat", "Delhi"],
        delivery_deadline=base_time + timedelta(hours=10),
        priority=PriorityLevel.HIGH,
    )
    disruptions = [
        Disruption(
            disruption_id="DIS-SURAT",
            type=DisruptionType.FLOOD,
            location="Surat",
            severity=DisruptionSeverity.CRITICAL,
            affected_locations=["Surat"],
        )
    ]
    recs = generate_batch_recommendations(
        shipments=[s1, s2],
        disruptions=disruptions,
        current_time=base_time,
    )
    assert len(recs) == 2
    assert recs[0].risk_assessment.risk_level == RiskLevel.LOW
    assert recs[1].risk_assessment.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
