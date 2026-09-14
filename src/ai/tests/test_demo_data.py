"""Tests for simulated demo dataset integrity and loading."""

from src.ai.demo_data import (
    get_all_demo_scenarios,
    get_scenario_1_normal_shipment,
    get_scenario_2_weather_disrupted_shipment,
    get_scenario_3_high_priority_pharma,
    get_scenario_4_and_5_fleet_assets,
    get_scenario_6_normal_cold_chain_readings,
    get_scenario_7_warning_cold_chain_readings,
    get_scenario_8_critical_cold_chain_readings,
)


def test_scenario_loaders():
    s1_shp, s1_dis, s1_rt, s1_car = get_scenario_1_normal_shipment()
    assert s1_shp.shipment_id == "SHP-IN-101"
    assert len(s1_dis) == 0

    s2_shp, s2_dis, s2_rt, s2_car = get_scenario_2_weather_disrupted_shipment()
    assert s2_shp.shipment_id == "SHP-IN-202"
    assert len(s2_dis) == 1
    assert len(s2_rt) == 2

    s3_shp, s3_dis, s3_rt, s3_car = get_scenario_3_high_priority_pharma()
    assert s3_shp.cargo_type.value == "PHARMA"
    assert s3_shp.temperature_required is True

    fleet = get_scenario_4_and_5_fleet_assets()
    assert len(fleet) == 5

    r6 = get_scenario_6_normal_cold_chain_readings()
    assert len(r6) == 12

    r7 = get_scenario_7_warning_cold_chain_readings()
    assert len(r7) == 10

    r8 = get_scenario_8_critical_cold_chain_readings()
    assert len(r8) == 10


def test_get_all_demo_scenarios():
    scenarios = get_all_demo_scenarios()
    assert "scenario_1" in scenarios
    assert "scenario_2" in scenarios
    assert "scenario_3" in scenarios
    assert "scenario_4_and_5_fleet" in scenarios
    assert "scenario_6_cold_chain_normal" in scenarios
    assert "scenario_7_cold_chain_warning" in scenarios
    assert "scenario_8_cold_chain_critical" in scenarios
