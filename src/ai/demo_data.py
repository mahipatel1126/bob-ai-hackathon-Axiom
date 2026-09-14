"""Deterministic demonstration dataset for L2 Supply Chain Disruption & Fleet Optimizer.

NOTE: All records in this module are SIMULATED DEMO DATA created for local testing,
benchmarking, and hackathon presentation. They are NOT live operational feeds.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from src.ai.schemas import (
    CargoType,
    CarrierOption,
    Disruption,
    DisruptionSeverity,
    DisruptionType,
    FleetAsset,
    FleetAvailability,
    FleetStatus,
    PriorityLevel,
    RouteOption,
    Shipment,
    ShipmentStatus,
    TemperatureReading,
    VehicleType,
)


def get_base_time() -> datetime:
    """Fixed deterministic timestamp for reproducible scenario testing."""
    return datetime(2026, 9, 14, 10, 0, 0)


# ---------------------------------------------------------------------------
# Demo Scenario 1: Normal shipment with no disruption
# ---------------------------------------------------------------------------
def get_scenario_1_normal_shipment() -> Tuple[Shipment, List[Disruption], List[RouteOption], List[CarrierOption]]:
    """Scenario 1: Standard dry shipment, clear transit route, nominal risk."""
    now = get_base_time()
    shipment = Shipment(
        shipment_id="SHP-IN-101",
        origin="Pune",
        destination="Bengaluru",
        route=["Pune", "Satara", "Kolhapur", "Belagavi", "Hubballi", "Tumakuru", "Bengaluru"],
        carrier="Apex Logistics Express",
        priority=PriorityLevel.LOW,
        delivery_deadline=now + timedelta(hours=36),
        cargo_type=CargoType.DRY,
        temperature_required=False,
        weight_kg=2500.0,
        volume_cbm=12.0,
        value_inr=150000.0,
        status=ShipmentStatus.IN_TRANSIT,
        current_location="Kolhapur",
        eta_hours_remaining=16.0,
    )
    disruptions: List[Disruption] = []
    routes = [
        RouteOption(
            route_id="RT-S1-MAIN",
            name="NH 48 Pune-Bengaluru Golden Corridor",
            waypoints=["Kolhapur", "Belagavi", "Hubballi", "Bengaluru"],
            distance_km=620.0,
            estimated_time_hours=12.5,
            estimated_cost=22000.0,
            risk_score=5.0,
            disruption_exposure=0.0,
        )
    ]
    carriers = [
        CarrierOption(
            carrier_id="CAR-01",
            name="Apex Express",
            available_capacity_kg=5000.0,
            estimated_cost=22000.0,
            reliability_score=0.95,
            estimated_delivery_hours=12.5,
            temperature_capable=False,
        )
    ]
    return shipment, disruptions, routes, carriers


# ---------------------------------------------------------------------------
# Scenario 2: Shipment affected by severe weather/corridor disruption
# ---------------------------------------------------------------------------
def get_scenario_2_weather_disrupted_shipment() -> Tuple[Shipment, List[Disruption], List[RouteOption], List[CarrierOption]]:
    """Scenario 2: Industrial freight facing severe cyclonic flooding on Mumbai-Surat highway."""
    now = get_base_time()
    shipment = Shipment(
        shipment_id="SHP-IN-202",
        origin="Mumbai",
        destination="Delhi",
        route=["Mumbai", "Thane", "Vapi", "Surat", "Vadodara", "Ahmedabad", "Jaipur", "Delhi"],
        carrier="National Freight Corp",
        priority=PriorityLevel.HIGH,
        delivery_deadline=now + timedelta(hours=24),
        cargo_type=CargoType.DRY,
        temperature_required=False,
        weight_kg=8500.0,
        volume_cbm=35.0,
        value_inr=950000.0,
        status=ShipmentStatus.IN_TRANSIT,
        current_location="Thane",
        eta_hours_remaining=20.0,
    )
    disruptions = [
        Disruption(
            disruption_id="DIS-WEATHER-202",
            type=DisruptionType.FLOOD,
            location="Surat",
            region="Gujarat South Corridor",
            severity=DisruptionSeverity.CRITICAL,
            start_time=now - timedelta(hours=2),
            estimated_duration_hours=18.0,
            affected_routes=["NH48-Surat-Vadodara", "Vapi-Surat"],
            affected_locations=["Surat", "Vapi", "Navsari"],
            description="Severe waterlogging and bridge closure on Western NH48 corridor due to heavy monsoon downpour.",
            delay_impact_hours=14.0,
        )
    ]
    routes = [
        RouteOption(
            route_id="RT-202-PRIMARY",
            name="NH48 Coastal Corridor (Direct via Surat)",
            waypoints=["Thane", "Vapi", "Surat", "Vadodara", "Ahmedabad", "Delhi"],
            distance_km=1420.0,
            estimated_time_hours=22.0,
            estimated_cost=45000.0,
            risk_score=90.0,
            disruption_exposure=0.65,
        ),
        RouteOption(
            route_id="RT-202-BYPASS-INDORE",
            name="Eastern Bypass via Nashik & Indore (NH52/NH47)",
            waypoints=["Thane", "Nashik", "Dhule", "Indore", "Gwalior", "Agra", "Delhi"],
            distance_km=1480.0,
            estimated_time_hours=24.0,
            estimated_cost=48500.0,
            risk_score=10.0,
            disruption_exposure=0.0,
            notes="Completely circumvents flooded South Gujarat zone.",
        ),
    ]
    carriers = [
        CarrierOption(
            carrier_id="CAR-MAHA-02",
            name="Western Central Transporters",
            available_capacity_kg=12000.0,
            estimated_cost=49000.0,
            reliability_score=0.92,
            estimated_delivery_hours=24.0,
            temperature_capable=False,
        )
    ]
    return shipment, disruptions, routes, carriers


# ---------------------------------------------------------------------------
# Scenario 3: High-priority pharma shipment at risk of deadline breach
# ---------------------------------------------------------------------------
def get_scenario_3_high_priority_pharma() -> Tuple[Shipment, List[Disruption], List[RouteOption], List[CarrierOption]]:
    """Scenario 3: Critical oncology vaccines needing strict 2°C-8°C temp control with tight 10h deadline."""
    now = get_base_time()
    shipment = Shipment(
        shipment_id="SHP-PHARMA-303",
        origin="Hyderabad",
        destination="Chennai",
        route=["Hyderabad", "Nalgonda", "Guntur", "Nellore", "Chennai"],
        carrier="MediChain Bio-Logistics",
        priority=PriorityLevel.CRITICAL,
        delivery_deadline=now + timedelta(hours=10),
        cargo_type=CargoType.PHARMA,
        temperature_required=True,
        required_min_temperature=2.0,
        required_max_temperature=8.0,
        weight_kg=1200.0,
        volume_cbm=4.0,
        value_inr=3500000.0,
        status=ShipmentStatus.IN_TRANSIT,
        current_location="Nalgonda",
        eta_hours_remaining=8.5,
    )
    disruptions = [
        Disruption(
            disruption_id="DIS-ROAD-303",
            type=DisruptionType.ACCIDENT,
            location="Nellore",
            region="AP Coastal Corridor",
            severity=DisruptionSeverity.HIGH,
            start_time=now - timedelta(hours=1),
            estimated_duration_hours=6.0,
            affected_routes=["NH16-Nellore"],
            affected_locations=["Nellore", "Gudur"],
            description="Multi-vehicle tanker accident blocking southbound lanes on NH16.",
            delay_impact_hours=5.5,
        )
    ]
    routes = [
        RouteOption(
            route_id="RT-303-NH16",
            name="NH16 Coastal Express (via Nellore)",
            waypoints=["Nalgonda", "Guntur", "Nellore", "Chennai"],
            distance_km=560.0,
            estimated_time_hours=8.5,
            estimated_cost=28000.0,
            risk_score=85.0,
            disruption_exposure=0.50,
        ),
        RouteOption(
            route_id="RT-303-KADAPA",
            name="Inland Bypass via Kurnool & Kadapa (NH40)",
            waypoints=["Nalgonda", "Kurnool", "Kadapa", "Tirupati", "Chennai"],
            distance_km=620.0,
            estimated_time_hours=9.2,
            estimated_cost=31500.0,
            risk_score=15.0,
            disruption_exposure=0.0,
        ),
    ]
    carriers = [
        CarrierOption(
            carrier_id="CAR-REEFER-01",
            name="CryoLogistics India",
            available_capacity_kg=3000.0,
            estimated_cost=32000.0,
            reliability_score=0.98,
            estimated_delivery_hours=9.0,
            temperature_capable=True,
            rating=4.9,
        )
    ]
    return shipment, disruptions, routes, carriers


# ---------------------------------------------------------------------------
# Scenario 4 & 5: Fleet asset test cases (Suitable vs Unsuitable)
# ---------------------------------------------------------------------------
def get_scenario_4_and_5_fleet_assets() -> List[FleetAsset]:
    """Scenario 4 & 5: Fleet assets with diverse utilization, location, and reefer specs."""
    return [
        # Suitable for Pharma (Scenario 4 match)
        FleetAsset(
            vehicle_id="FLT-REEFER-01",
            vehicle_type=VehicleType.REEFER_TRUCK,
            capacity_kg=3500.0,
            capacity_cbm=14.0,
            current_location="Hyderabad",
            availability=FleetAvailability.AVAILABLE,
            current_utilization=0.10,  # IDLE
            temperature_capability=True,
            min_temp_capable=-20.0,
            max_temp_capable=15.0,
            cost_per_km=28.0,
            driver_name="Rajesh Kumar",
            status=FleetStatus.IDLE,
        ),
        # Unsuitable for Pharma (Dry box truck, no reefer - Scenario 5 match)
        FleetAsset(
            vehicle_id="FLT-BOX-02",
            vehicle_type=VehicleType.BOX_TRUCK,
            capacity_kg=5000.0,
            capacity_cbm=22.0,
            current_location="Hyderabad",
            availability=FleetAvailability.AVAILABLE,
            current_utilization=0.05,  # IDLE
            temperature_capability=False,
            cost_per_km=22.0,
            driver_name="Sunil Sharma",
            status=FleetStatus.IDLE,
        ),
        # Unsuitable due to low capacity (Small van)
        FleetAsset(
            vehicle_id="FLT-VAN-03",
            vehicle_type=VehicleType.VAN,
            capacity_kg=800.0,
            capacity_cbm=4.0,
            current_location="Pune",
            availability=FleetAvailability.AVAILABLE,
            current_utilization=0.12,  # IDLE
            temperature_capability=False,
            cost_per_km=15.0,
            driver_name="Amit Shinde",
            status=FleetStatus.IDLE,
        ),
        # Active vehicle at high utilization
        FleetAsset(
            vehicle_id="FLT-REEFER-04",
            vehicle_type=VehicleType.REEFER_TRUCK,
            capacity_kg=4000.0,
            capacity_cbm=16.0,
            current_location="Chennai",
            availability=FleetAvailability.IN_USE,
            current_utilization=0.90,  # ACTIVE
            temperature_capability=True,
            min_temp_capable=-18.0,
            max_temp_capable=10.0,
            cost_per_km=30.0,
            status=FleetStatus.ACTIVE,
        ),
        # Maintenance asset
        FleetAsset(
            vehicle_id="FLT-MAINT-05",
            vehicle_type=VehicleType.REEFER_TRUCK,
            capacity_kg=5000.0,
            capacity_cbm=20.0,
            current_location="Hyderabad",
            availability=FleetAvailability.MAINTENANCE,
            current_utilization=0.0,
            temperature_capability=True,
            cost_per_km=28.0,
            status=FleetStatus.UNAVAILABLE,
        ),
    ]


# ---------------------------------------------------------------------------
# Scenario 6: Normal Cold-Chain Telemetry (Compliant 2°C - 8°C)
# ---------------------------------------------------------------------------
def get_scenario_6_normal_cold_chain_readings(shipment_id: str = "SHP-PHARMA-303") -> List[TemperatureReading]:
    """Scenario 6: 12 consecutive hours of stable, in-spec temperature telemetry (4.1°C to 4.8°C)."""
    now = get_base_time()
    readings = []
    normal_temps = [4.2, 4.3, 4.1, 4.5, 4.4, 4.6, 4.5, 4.3, 4.4, 4.7, 4.8, 4.5]
    for i, t in enumerate(normal_temps):
        readings.append(TemperatureReading(
            reading_id=f"READ-NORM-{i:03d}",
            shipment_id=shipment_id,
            timestamp=now - timedelta(minutes=(len(normal_temps) - i) * 30),
            temperature=t,
            required_min_temperature=2.0,
            required_max_temperature=8.0,
            ambient_temperature=32.0,
            humidity_percent=55.0,
            battery_level_percent=92.0 - (i * 0.5),
        ))
    return readings


# ---------------------------------------------------------------------------
# Scenario 7: Warning Cold-Chain Excursion (Short minor breach)
# ---------------------------------------------------------------------------
def get_scenario_7_warning_cold_chain_readings(shipment_id: str = "SHP-PHARMA-303") -> List[TemperatureReading]:
    """Scenario 7: Brief minor excursion during loading/docking door opening (peaking at 9.2°C for 20 mins)."""
    now = get_base_time()
    readings = []
    # Profile: Nominal -> Small transient spike -> Return to nominal
    temp_profile = [4.5, 4.6, 5.0, 7.8, 8.8, 9.2, 8.5, 6.2, 4.8, 4.5]
    for i, t in enumerate(temp_profile):
        readings.append(TemperatureReading(
            reading_id=f"READ-WARN-{i:03d}",
            shipment_id=shipment_id,
            timestamp=now - timedelta(minutes=(len(temp_profile) - i) * 15),
            temperature=t,
            required_min_temperature=2.0,
            required_max_temperature=8.0,
            ambient_temperature=35.0,
            humidity_percent=60.0,
            battery_level_percent=88.0,
        ))
    return readings


# ---------------------------------------------------------------------------
# Scenario 8: Critical Cold-Chain Excursion (Sustained compressor failure)
# ---------------------------------------------------------------------------
def get_scenario_8_critical_cold_chain_readings(shipment_id: str = "SHP-PHARMA-303") -> List[TemperatureReading]:
    """Scenario 8: Severe sustained temperature excursion reaching 14.8°C over 2 hours due to cooling failure."""
    now = get_base_time()
    readings = []
    # Profile: Rapid climb from 5°C up to 14.8°C and staying elevated
    temp_profile = [4.5, 6.0, 8.5, 10.2, 12.0, 13.5, 14.8, 14.5, 14.2, 14.6]
    for i, t in enumerate(temp_profile):
        readings.append(TemperatureReading(
            reading_id=f"READ-CRIT-{i:03d}",
            shipment_id=shipment_id,
            timestamp=now - timedelta(minutes=(len(temp_profile) - i) * 20),
            temperature=t,
            required_min_temperature=2.0,
            required_max_temperature=8.0,
            ambient_temperature=38.0,
            humidity_percent=70.0,
            battery_level_percent=45.0,
        ))
    return readings


# ---------------------------------------------------------------------------
# Loader & Demo Runner
# ---------------------------------------------------------------------------
def get_all_demo_scenarios() -> Dict[str, dict]:
    """Retrieve full suite of all 8 simulated test scenarios."""
    s1_shp, s1_dis, s1_rt, s1_car = get_scenario_1_normal_shipment()
    s2_shp, s2_dis, s2_rt, s2_car = get_scenario_2_weather_disrupted_shipment()
    s3_shp, s3_dis, s3_rt, s3_car = get_scenario_3_high_priority_pharma()
    fleet = get_scenario_4_and_5_fleet_assets()

    return {
        "scenario_1": {
            "title": "Scenario 1: Normal Dry Shipment (Nominal)",
            "shipment": s1_shp,
            "disruptions": s1_dis,
            "routes": s1_rt,
            "carriers": s1_car,
            "readings": [],
        },
        "scenario_2": {
            "title": "Scenario 2: Severe Weather / Flood Corridor Disruption",
            "shipment": s2_shp,
            "disruptions": s2_dis,
            "routes": s2_rt,
            "carriers": s2_car,
            "readings": [],
        },
        "scenario_3": {
            "title": "Scenario 3: High-Priority Pharma Shipment at Deadline Risk",
            "shipment": s3_shp,
            "disruptions": s3_dis,
            "routes": s3_rt,
            "carriers": s3_car,
            "readings": get_scenario_6_normal_cold_chain_readings(s3_shp.shipment_id),
        },
        "scenario_4_and_5_fleet": {
            "title": "Scenario 4 & 5: Idle vs Unsuitable Fleet Assets",
            "fleet": fleet,
        },
        "scenario_6_cold_chain_normal": {
            "title": "Scenario 6: Normal Compliant Cold-Chain Telemetry",
            "readings": get_scenario_6_normal_cold_chain_readings(),
        },
        "scenario_7_cold_chain_warning": {
            "title": "Scenario 7: Warning Cold-Chain Excursion (Transient spike)",
            "readings": get_scenario_7_warning_cold_chain_readings(),
        },
        "scenario_8_cold_chain_critical": {
            "title": "Scenario 8: Critical Cold-Chain Excursion (Compressor breakdown)",
            "readings": get_scenario_8_critical_cold_chain_readings(),
        },
    }
