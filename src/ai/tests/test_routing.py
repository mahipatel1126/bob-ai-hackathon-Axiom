"""Tests for rerouting evaluation engine."""

from datetime import datetime, timedelta
import pytest
from src.ai.routing import evaluate_routes
from src.ai.schemas import (
    Disruption,
    DisruptionSeverity,
    DisruptionType,
    RouteOption,
    Shipment,
)


@pytest.fixture
def sample_shipment():
    return Shipment(
        shipment_id="SHP-ROUTE-01",
        origin="Mumbai",
        destination="Delhi",
        delivery_deadline=datetime(2026, 9, 15, 12, 0, 0),
        status="IN_TRANSIT",
    )


@pytest.fixture
def candidate_routes():
    return [
        RouteOption(
            route_id="RT-DIRECT-SURAT",
            name="NH48 Coastal Corridor",
            waypoints=["Mumbai", "Surat", "Vadodara", "Delhi"],
            distance_km=1420.0,
            estimated_time_hours=22.0,
            estimated_cost=40000.0,
            risk_score=0.0,
            disruption_exposure=0.0,
        ),
        RouteOption(
            route_id="RT-INLAND-INDORE",
            name="NH52 Inland Corridor via Indore",
            waypoints=["Mumbai", "Nashik", "Indore", "Delhi"],
            distance_km=1480.0,
            estimated_time_hours=24.0,
            estimated_cost=44000.0,
            risk_score=0.0,
            disruption_exposure=0.0,
        ),
    ]


@pytest.fixture
def active_disruption():
    return [
        Disruption(
            disruption_id="DIS-SURAT",
            type=DisruptionType.FLOOD,
            location="Surat",
            severity=DisruptionSeverity.CRITICAL,
            affected_locations=["Surat"],
        )
    ]


def test_route_ranking_avoids_disruption(sample_shipment, candidate_routes, active_disruption):
    res = evaluate_routes(sample_shipment, candidate_routes, active_disruption)
    assert res.recommended_route is not None
    assert res.recommended_route.route_id == "RT-INLAND-INDORE"
    assert "Indore" in res.recommended_route.name
    assert len(res.ranked_routes) == 2
    assert "Selected" in res.selection_reason


def test_empty_candidate_routes(sample_shipment):
    res = evaluate_routes(sample_shipment, [])
    assert res.recommended_route is None
    assert len(res.ranked_routes) == 0
    assert "No alternative" in res.selection_reason


def test_route_evaluation_without_disruptions(sample_shipment, candidate_routes):
    res = evaluate_routes(sample_shipment, candidate_routes, [])
    assert res.recommended_route is not None
    # Without disruptions, faster / lower cost route is favored
    assert res.recommended_route.route_id == "RT-DIRECT-SURAT"
