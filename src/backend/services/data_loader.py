"""Data loader service for Chain Guard AI demo datasets."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..config import DATA_DIR
from ..models import (
    Shipment,
    Disruption,
    FleetAsset,
    TelemetryReading,
    CarrierOption,
    RouteAlternative,
)


def _load_json_file(filename: str) -> Any:
    """Read and parse a JSON dataset safely without mutating original file."""
    file_path = DATA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found at {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# --- Raw Dictionary Accessors ---

def get_shipments() -> List[Dict[str, Any]]:
    """Retrieve all raw shipment records."""
    return _load_json_file("shipments.json")


def get_shipment_by_id(shipment_id: str) -> Optional[Dict[str, Any]]:
    """Lookup a single shipment by its ID."""
    for s in get_shipments():
        if s.get("shipment_id") == shipment_id:
            return s
    return None


def get_disruptions(active_only: bool = False) -> List[Dict[str, Any]]:
    """Retrieve all disruption records, optionally filtering by active status."""
    disruptions = _load_json_file("disruptions.json")
    if active_only:
        return [d for d in disruptions if d.get("is_active", True)]
    return disruptions


def get_disruption_by_id(disruption_id: str) -> Optional[Dict[str, Any]]:
    """Lookup a single disruption by its ID."""
    for d in get_disruptions():
        if d.get("disruption_id") == disruption_id:
            return d
    return None


def get_fleet_assets(idle_only: bool = False, reefer_only: bool = False) -> List[Dict[str, Any]]:
    """Retrieve fleet assets with optional filters for idle status or reefer capability."""
    assets = _load_json_file("fleet.json")
    if idle_only:
        assets = [a for a in assets if a.get("status") == "IDLE" and a.get("is_available", True)]
    if reefer_only:
        assets = [a for a in assets if a.get("reefer_capability", {}).get("is_reefer", False)]
    return assets


def get_fleet_asset_by_id(asset_id: str) -> Optional[Dict[str, Any]]:
    """Lookup a single fleet asset by its ID."""
    for a in get_fleet_assets():
        if a.get("asset_id") == asset_id:
            return a
    return None


def get_telemetry(shipment_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve telemetry streams, optionally filtered by shipment ID."""
    telemetry = _load_json_file("telemetry.json")
    if shipment_id:
        return [t for t in telemetry if t.get("shipment_id") == shipment_id]
    return telemetry


def get_carriers() -> List[Dict[str, Any]]:
    """Retrieve available freight carrier service options."""
    data = _load_json_file("carriers_routes.json")
    return data.get("carriers", [])


def get_route_alternatives(shipment_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve alternative bypass routes, optionally filtered by target shipment ID."""
    data = _load_json_file("carriers_routes.json")
    routes = data.get("route_alternatives", [])
    if shipment_id:
        return [r for r in routes if r.get("target_shipment_id") == shipment_id]
    return routes


# --- Domain Model Deserializers ---

def get_shipment_models() -> List[Shipment]:
    """Retrieve all shipments deserialized as domain models."""
    return [Shipment.from_dict(s) for s in get_shipments()]


def get_disruption_models(active_only: bool = False) -> List[Disruption]:
    """Retrieve all disruptions deserialized as domain models."""
    return [Disruption.from_dict(d) for d in get_disruptions(active_only=active_only)]


def get_fleet_models(idle_only: bool = False, reefer_only: bool = False) -> List[FleetAsset]:
    """Retrieve fleet assets deserialized as domain models."""
    return [FleetAsset.from_dict(a) for a in get_fleet_assets(idle_only=idle_only, reefer_only=reefer_only)]


def get_telemetry_models(shipment_id: Optional[str] = None) -> List[TelemetryReading]:
    """Retrieve telemetry streams deserialized as domain models."""
    return [TelemetryReading.from_dict(t) for t in get_telemetry(shipment_id=shipment_id)]


def get_carrier_models() -> List[CarrierOption]:
    """Retrieve carrier options deserialized as domain models."""
    return [CarrierOption.from_dict(c) for c in get_carriers()]


def get_route_alternative_models(shipment_id: Optional[str] = None) -> List[RouteAlternative]:
    """Retrieve route alternatives deserialized as domain models."""
    return [RouteAlternative.from_dict(r) for r in get_route_alternatives(shipment_id=shipment_id)]
