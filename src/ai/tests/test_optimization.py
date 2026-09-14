"""Tests for fleet redeployment optimization engine."""

from datetime import datetime, timedelta
import pytest
from src.ai.optimization import optimize_fleet_redeployment
from src.ai.schemas import (
    CargoType,
    FleetAsset,
    FleetAvailability,
    PriorityLevel,
    Shipment,
    VehicleType,
)


@pytest.fixture
def urgent_shipments():
    return [
        Shipment(
            shipment_id="SHP-URGENT-01",
            origin="Mumbai",
            destination="Delhi",
            delivery_deadline=datetime(2026, 9, 15, 12, 0, 0),
            priority=PriorityLevel.CRITICAL,
            cargo_type=CargoType.PHARMA,
            temperature_required=True,
            required_min_temperature=2.0,
            required_max_temperature=8.0,
            weight_kg=2500.0,
            current_location="Mumbai",
        ),
        Shipment(
            shipment_id="SHP-URGENT-02",
            origin="Pune",
            destination="Bengaluru",
            delivery_deadline=datetime(2026, 9, 15, 12, 0, 0),
            priority=PriorityLevel.HIGH,
            cargo_type=CargoType.DRY,
            weight_kg=4000.0,
            current_location="Pune",
        ),
    ]


@pytest.fixture
def available_fleet():
    return [
        FleetAsset(
            vehicle_id="FLT-REEFER-MUMBAI",
            vehicle_type=VehicleType.REEFER_TRUCK,
            capacity_kg=3500.0,
            current_location="Mumbai",
            availability=FleetAvailability.AVAILABLE,
            current_utilization=0.10,
            temperature_capability=True,
            min_temp_capable=-10.0,
            max_temp_capable=10.0,
            cost_per_km=25.0,
        ),
        FleetAsset(
            vehicle_id="FLT-BOX-PUNE",
            vehicle_type=VehicleType.BOX_TRUCK,
            capacity_kg=5000.0,
            current_location="Pune",
            availability=FleetAvailability.AVAILABLE,
            current_utilization=0.20,
            cost_per_km=20.0,
        ),
        FleetAsset(
            vehicle_id="FLT-STANDBY-CHENNAI",
            vehicle_type=VehicleType.BOX_TRUCK,
            capacity_kg=6000.0,
            current_location="Chennai",
            availability=FleetAvailability.AVAILABLE,
            current_utilization=0.05,
            cost_per_km=22.0,
        ),
    ]


def test_fleet_redeployment_matching(urgent_shipments, available_fleet):
    res = optimize_fleet_redeployment(urgent_shipments, available_fleet)
    assert len(res.assignments) == 2
    
    # Check that Mumbai reefer matched Pharma in Mumbai
    sh1_assign = next(a for a in res.assignments if a.shipment_id == "SHP-URGENT-01")
    assert sh1_assign.vehicle_id == "FLT-REEFER-MUMBAI"
    assert sh1_assign.utilization_improvement > 0

    # Check that Pune box truck matched dry shipment in Pune
    sh2_assign = next(a for a in res.assignments if a.shipment_id == "SHP-URGENT-02")
    assert sh2_assign.vehicle_id == "FLT-BOX-PUNE"


def test_empty_shipments(available_fleet):
    res = optimize_fleet_redeployment([], available_fleet)
    assert len(res.assignments) == 0
    assert len(res.unused_vehicles) == len(available_fleet)


def test_empty_fleet(urgent_shipments):
    res = optimize_fleet_redeployment(urgent_shipments, [])
    assert len(res.assignments) == 0
    assert len(res.unassigned_shipments) == len(urgent_shipments)
