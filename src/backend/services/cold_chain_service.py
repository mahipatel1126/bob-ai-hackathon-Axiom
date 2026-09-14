"""Cold-chain telemetry processing and excursion classification service.

Evaluates IoT sensor streams against thermal envelope requirements,
computes thermal deviations, and classifies regulatory severity
in accordance with FDA 21 CFR Part 211 and WHO GDP standards.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from . import data_loader
from ..models import (
    ExcursionSeverity,
    ComplianceStatus,
)


def _parse_iso_timestamp(ts_str: str) -> datetime:
    """Safely parse ISO 8601 timestamp string into datetime."""
    try:
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1] + "+00:00"
        return datetime.fromisoformat(ts_str)
    except Exception:
        return datetime.now(timezone.utc)


def analyze_shipment_cold_chain(shipment_id: str) -> Dict[str, Any]:
    """Process all telemetry readings for a shipment and evaluate regulatory compliance.

    Computes:
    - Temperature min/max/mean
    - Excursion detection (readings outside allowed limits)
    - Cumulative breach duration
    - Regulatory compliance classification (FDA 21 CFR 211 / WHO GDP)
    - Actionable corrective recommendations
    """
    shipment = data_loader.get_shipment_by_id(shipment_id)
    if not shipment:
        raise ValueError(f"Shipment {shipment_id} not found.")

    temp_req = shipment.get("temperature_requirement", {})
    is_cold_chain = temp_req.get("is_required", False)

    telemetry = data_loader.get_telemetry(shipment_id=shipment_id)

    # If non-refrigerated cargo with no thermal envelope, return standard status
    if not is_cold_chain:
        return {
            "shipment_id": shipment_id,
            "cargo_name": shipment.get("cargo", {}).get("product_name", "General Freight"),
            "is_cold_chain": False,
            "temperature_requirement": None,
            "readings_count": len(telemetry),
            "excursion_detected": False,
            "severity": ExcursionSeverity.NORMAL.value,
            "compliance_status": ComplianceStatus.COMPLIANT.value,
            "regulatory_framework": "N/A (Standard Freight)",
            "min_temperature_c": None,
            "max_temperature_c": None,
            "mean_temperature_c": None,
            "excursion_events": [],
            "recommended_action": "Routine dry freight handling.",
        }

    min_limit = float(temp_req.get("min_temp_c", 2.0))
    max_limit = float(temp_req.get("max_temp_c", 8.0))
    target_temp = temp_req.get("target_temp_c", (min_limit + max_limit) / 2.0)
    tolerance_minutes = int(temp_req.get("tolerance_duration_minutes", 30))

    if not telemetry:
        return {
            "shipment_id": shipment_id,
            "cargo_name": shipment.get("cargo", {}).get("product_name"),
            "is_cold_chain": True,
            "temperature_requirement": temp_req,
            "readings_count": 0,
            "excursion_detected": False,
            "severity": ExcursionSeverity.NORMAL.value,
            "compliance_status": ComplianceStatus.COMPLIANT.value,
            "regulatory_framework": "FDA 21 CFR 211 / WHO GDP",
            "min_temperature_c": None,
            "max_temperature_c": None,
            "mean_temperature_c": None,
            "excursion_events": [],
            "recommended_action": "Telemetry awaiting initial sensor sync.",
        }

    # Sort telemetry by timestamp
    telemetry_sorted = sorted(telemetry, key=lambda t: t.get("timestamp", ""))

    temps = [t.get("temperature_c", 0.0) for t in telemetry_sorted]
    min_observed = min(temps)
    max_observed = max(temps)
    mean_observed = round(sum(temps) / len(temps), 2)

    # Detect out-of-range readings and cluster into excursion events
    excursion_events: List[Dict[str, Any]] = []
    current_excursion_readings: List[Dict[str, Any]] = []

    for reading in telemetry_sorted:
        t_val = reading.get("temperature_c", 0.0)
        is_out_of_spec = t_val < min_limit or t_val > max_limit

        if is_out_of_spec:
            current_excursion_readings.append(reading)
        else:
            if current_excursion_readings:
                # Close out current excursion
                event = _build_excursion_event(
                    current_excursion_readings, min_limit, max_limit
                )
                excursion_events.append(event)
                current_excursion_readings = []

    if current_excursion_readings:
        event = _build_excursion_event(
            current_excursion_readings, min_limit, max_limit
        )
        excursion_events.append(event)

    # Determine overall severity & regulatory classification
    total_breach_minutes = sum(e["duration_minutes"] for e in excursion_events)
    highest_temp = max_observed
    lowest_temp = min_observed

    # Classification logic based on FDA 21 CFR 211 & WHO Good Distribution Practice guidelines
    if not excursion_events:
        severity = ExcursionSeverity.NORMAL.value
        compliance_status = ComplianceStatus.COMPLIANT.value
        recommended_action = "Temperature within optimal specifications. Continue standard monitoring."
    elif (
        total_breach_minutes > 90
        or highest_temp >= 15.0
        or (min_limit >= 0.0 and lowest_temp <= 0.0)  # Freezing event on liquid biologics
    ):
        severity = ExcursionSeverity.CRITICAL.value
        compliance_status = ComplianceStatus.NON_COMPLIANT_QUARANTINE.value
        recommended_action = (
            "CRITICAL THERMAL BREACH: Immediate quarantine mandatory upon arrival "
            "per FDA 21 CFR 211 / WHO GDP. Do not release cargo for clinical/commercial use. "
            "Initiate immediate quality assurance investigation and asset redeployment."
        )
    elif total_breach_minutes > tolerance_minutes or highest_temp >= 10.0:
        severity = ExcursionSeverity.MODERATE.value
        compliance_status = ComplianceStatus.WARNING.value
        recommended_action = (
            "SUSTAINED EXCURSION: Cargo requires secondary temperature stability review. "
            "Inspect container insulation, verify backup generator, and flag for QA inspection at destination."
        )
    else:
        severity = ExcursionSeverity.MINOR.value
        compliance_status = ComplianceStatus.WARNING.value
        recommended_action = (
            "MINOR TRANSIENT EXCURSION: Deviation within allowable thermal tolerance window. "
            "Continue close continuous telemetry monitoring."
        )

    return {
        "shipment_id": shipment_id,
        "cargo_name": shipment.get("cargo", {}).get("product_name", "Refrigerated Cargo"),
        "cargo_type": shipment.get("cargo", {}).get("cargo_type"),
        "is_cold_chain": True,
        "target_range": f"{min_limit:.1f}°C to {max_limit:.1f}°C",
        "target_min_temp_c": min_limit,
        "target_max_temp_c": max_limit,
        "readings_count": len(telemetry_sorted),
        "min_temperature_c": min_observed,
        "max_temperature_c": max_observed,
        "mean_temperature_c": mean_observed,
        "excursion_detected": len(excursion_events) > 0,
        "total_excursion_duration_minutes": total_breach_minutes,
        "severity": severity,
        "compliance_status": compliance_status,
        "regulatory_framework": "FDA 21 CFR 211 / WHO Good Distribution Practice (GDP)",
        "recommended_action": recommended_action,
        "excursion_events": excursion_events,
        "latest_reading": telemetry_sorted[-1] if telemetry_sorted else None,
    }


def _build_excursion_event(
    readings: List[Dict[str, Any]],
    min_limit: float,
    max_limit: float,
) -> Dict[str, Any]:
    """Helper to synthesize consecutive out-of-range sensor readings into an excursion event."""
    start_ts_str = readings[0].get("timestamp", "")
    end_ts_str = readings[-1].get("timestamp", "")

    start_dt = _parse_iso_timestamp(start_ts_str)
    end_dt = _parse_iso_timestamp(end_ts_str)

    # Compute span; if only 1 reading, assume at least 15 min sampling window
    duration = max(15.0, round((end_dt - start_dt).total_seconds() / 60.0, 1))

    temps = [r.get("temperature_c", 0.0) for r in readings]
    peak_deviation = 0.0
    for t in temps:
        if t > max_limit:
            peak_deviation = max(peak_deviation, t - max_limit)
        elif t < min_limit:
            peak_deviation = max(peak_deviation, min_limit - t)

    return {
        "start_time": start_ts_str,
        "end_time": end_ts_str,
        "duration_minutes": duration,
        "readings_count": len(readings),
        "min_temp_c": min(temps),
        "max_temp_c": max(temps),
        "mean_temp_c": round(sum(temps) / len(temps), 2),
        "max_deviation_c": round(peak_deviation, 2),
        "breach_direction": "ABOVE_MAX" if max(temps) > max_limit else "BELOW_MIN",
    }


def get_all_excursions() -> List[Dict[str, Any]]:
    """Scan all cold-chain shipments and return those with active or logged excursions."""
    shipments = data_loader.get_shipments()
    excursion_reports: List[Dict[str, Any]] = []

    for s in shipments:
        is_cold = s.get("temperature_requirement", {}).get("is_required", False)
        if is_cold:
            report = analyze_shipment_cold_chain(s["shipment_id"])
            if report.get("excursion_detected"):
                excursion_reports.append(report)

    return excursion_reports


def generate_compliance_audit(shipment_id: str) -> Dict[str, Any]:
    """Produce an audit-ready regulatory inspection dossier for quality assurance teams."""
    analysis = analyze_shipment_cold_chain(shipment_id)
    shipment = data_loader.get_shipment_by_id(shipment_id) or {}

    return {
        "audit_id": f"AUDIT-GDP-{shipment_id}",
        "shipment_id": shipment_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "regulatory_standards": [
            "FDA 21 CFR Part 211 (Current Good Manufacturing Practice for Finished Pharmaceuticals)",
            "WHO Annex 5: Good Distribution Practices for Pharmaceutical Products",
            "EU GDP Guidelines (2013/C 343/01)",
        ],
        "cargo_profile": {
            "name": analysis.get("cargo_name"),
            "category": analysis.get("cargo_type"),
            "carrier": shipment.get("carrier"),
            "route": f"{shipment.get('origin', {}).get('name')} -> {shipment.get('destination', {}).get('name')}",
        },
        "thermal_specification": {
            "target_envelope": analysis.get("target_range"),
            "min_permitted_c": analysis.get("target_min_temp_c"),
            "max_permitted_c": analysis.get("target_max_temp_c"),
        },
        "findings": {
            "excursion_detected": analysis.get("excursion_detected"),
            "total_breach_minutes": analysis.get("total_excursion_duration_minutes"),
            "maximum_temperature_recorded_c": analysis.get("max_temperature_c"),
            "minimum_temperature_recorded_c": analysis.get("min_temperature_c"),
            "mean_temperature_recorded_c": analysis.get("mean_temperature_c"),
            "severity": analysis.get("severity"),
            "compliance_classification": analysis.get("compliance_status"),
        },
        "disposition_recommendation": analysis.get("recommended_action"),
        "excursion_events": analysis.get("excursion_events"),
        "electronic_signature_required": analysis.get("severity") in ("MODERATE", "CRITICAL"),
    }
