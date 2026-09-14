"""Tests for alternative carrier ranking and capacity allocation."""

from datetime import datetime, timedelta
import pytest
from src.ai.carrier import evaluate_carriers
from src.ai.schemas import (
    CargoType,
    CarrierOption,
    Shipment,
)


@pytest.fixture
def pharma_shipment():
    return Shipment(
        shipment_id="SHP-PHARMA-01",
        origin="Hyderabad",
        destination="Chennai",
        delivery_deadline=datetime(2026, 9, 15, 12, 0, 0),
        cargo_type=CargoType.PHARMA,
        temperature_required=True,
        required_min_temperature=2.0,
        required_max_temperature=8.0,
        weight_kg=2000.0,
    )


@pytest.fixture
def candidate_carriers():
    return [
        CarrierOption(
            carrier_id="CAR-DRY-FAST",
            name="Rapid Express",
            available_capacity_kg=5000.0,
            estimated_cost=20000.0,
            reliability_score=0.95,
            estimated_delivery_hours=8.0,
            temperature_capable=False,  # Lacks reefer
        ),
        CarrierOption(
            carrier_id="CAR-REEFER-RELIABLE",
            name="CryoLogistics Safe",
            available_capacity_kg=3000.0,
            estimated_cost=26000.0,
            reliability_score=0.98,
            estimated_delivery_hours=9.0,
            temperature_capable=True,
        ),
        CarrierOption(
            carrier_id="CAR-SMALL-REEFER",
            name="Micro Cold Carrier",
            available_capacity_kg=1000.0,  # Too small for 2000kg
            estimated_cost=15000.0,
            reliability_score=0.90,
            estimated_delivery_hours=8.5,
            temperature_capable=True,
        ),
    ]


def test_carrier_ranking_and_temperature_compliance(pharma_shipment, candidate_carriers):
    res = evaluate_carriers(pharma_shipment, candidate_carriers)
    assert res.recommended_carrier is not None
    assert res.recommended_carrier.carrier_id == "CAR-REEFER-RELIABLE"
    assert len(res.rejected_carriers) == 2  # CAR-DRY-FAST and CAR-SMALL-REEFER rejected


def test_no_valid_carrier(pharma_shipment):
    dry_carrier = [
        CarrierOption(
            carrier_id="CAR-DRY-ONLY",
            name="Dry Carrier Inc",
            available_capacity_kg=5000.0,
            estimated_cost=18000.0,
            reliability_score=0.90,
            estimated_delivery_hours=10.0,
            temperature_capable=False,
        )
    ]
    res = evaluate_carriers(pharma_shipment, dry_carrier)
    assert res.recommended_carrier is None
    assert len(res.rejected_carriers) == 1


def test_empty_carrier_list(pharma_shipment):
    res = evaluate_carriers(pharma_shipment, [])
    assert res.recommended_carrier is None
    assert len(res.ranked_carriers) == 0
