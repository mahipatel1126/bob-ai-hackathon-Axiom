"""Tests for idle fleet detection and asset classification."""

import pytest
from src.ai.fleet import classify_fleet_asset, detect_idle_fleet, filter_suitable_vehicles
from src.ai.schemas import (
    CargoType,
    FleetAsset,
    FleetAvailability,
    FleetStatus,
    Shipment,
    VehicleType,
)


@pytest.fixture
def fleet_roster():
    return [
        FleetAsset(
            vehicle_id="V1-IDLE",
            vehicle_type=VehicleType.REEFER_TRUCK,
            capacity_kg=3500.0,
            current_location="Mumbai",
            availability=FleetAvailability.AVAILABLE,
            current_utilization=0.08,
            temperature_capability=True,
            min_temp_capable=-15.0,
            max_temp_capable=10.0,
        ),
        FleetAsset(
            vehicle_id="V2-UNDERUTIL",
            vehicle_type=VehicleType.BOX_TRUCK,
            capacity_kg=4000.0,
            current_location="Pune",
            availability=FleetAvailability.AVAILABLE,
            current_utilization=0.35,
        ),
        FleetAsset(
            vehicle_id="V3-ACTIVE",
            vehicle_type=VehicleType.REEFER_TRUCK,
            capacity_kg=5000.0,
            current_location="Delhi",
            availability=FleetAvailability.IN_USE,
            current_utilization=0.92,
        ),
        FleetAsset(
            vehicle_id="V4-MAINT",
            vehicle_type=VehicleType.FLATBED,
            capacity_kg=10000.0,
            current_location="Chennai",
            availability=FleetAvailability.MAINTENANCE,
            current_utilization=0.0,
        ),
    ]


def test_detect_idle_fleet_classification(fleet_roster):
    res = detect_idle_fleet(fleet_roster)
    assert res.total_assets == 4
    assert res.idle_count == 1
    assert len(res.idle_vehicles) == 1
    assert res.idle_vehicles[0].vehicle_id == "V1-IDLE"
    assert len(res.underutilized_vehicles) == 1
    assert res.underutilized_vehicles[0].vehicle_id == "V2-UNDERUTIL"
    assert len(res.active_vehicles) == 1
    assert len(res.unavailable_vehicles) == 1


def test_filter_suitable_vehicles_pharma(fleet_roster):
    pharma_shipment = Shipment(
        shipment_id="SHP-PHARMA",
        origin="Mumbai",
        destination="Pune",
        delivery_deadline="2026-09-15T10:00:00",
        cargo_type=CargoType.PHARMA,
        temperature_required=True,
        required_min_temperature=2.0,
        required_max_temperature=8.0,
        weight_kg=2000.0,
    )
    suitable, rejections = filter_suitable_vehicles(pharma_shipment, fleet_roster)
    assert len(suitable) == 1
    assert suitable[0].vehicle_id == "V1-IDLE"
    assert len(rejections) == 3


def test_filter_dry_heavy_shipment(fleet_roster):
    heavy_dry_shipment = Shipment(
        shipment_id="SHP-DRY",
        origin="Pune",
        destination="Mumbai",
        delivery_deadline="2026-09-15T10:00:00",
        cargo_type=CargoType.DRY,
        temperature_required=False,
        weight_kg=3800.0,
    )
    suitable, rejections = filter_suitable_vehicles(heavy_dry_shipment, fleet_roster)
    # V2 has 4000kg capacity, V1 has 3500kg (too small), V3 in use, V4 maint
    suitable_ids = [v.vehicle_id for v in suitable]
    assert "V2-UNDERUTIL" in suitable_ids
    assert "V1-IDLE" not in suitable_ids
