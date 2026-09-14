"""Cold-chain IoT temperature excursion monitoring and regulatory severity engine."""

from datetime import datetime
from typing import List, Optional
from src.ai.config import AIConfig, DEFAULT_CONFIG
from src.ai.schemas import (
    CargoType,
    ColdChainAnalysisResult,
    ExcursionEvent,
    Shipment,
    TemperatureReading,
    TemperatureSeverity,
)


def analyze_temperature_readings(
    shipment: Shipment,
    readings: List[TemperatureReading],
    config: Optional[AIConfig] = None,
) -> ColdChainAnalysisResult:
    """Audit IoT temperature telemetry stream, detect excursions, and classify compliance severity.
    
    Excursion Criteria:
    - Temperature < required_min_temperature OR Temperature > required_max_temperature
    - Group consecutive violating readings into distinct excursion events with duration.
    
    Severity Classification:
    - NORMAL: 100% compliant, all readings within envelope.
    - WARNING: Minor deviation (<= 1.5°C) for short duration (<= 30 mins).
    - MAJOR: Significant deviation (1.5°C - 4.0°C) or prolonged excursion (30 - 90 mins).
    - CRITICAL: Severe deviation (> 4.0°C), prolonged excursion (> 90 mins), or repeated excursions for high-risk Pharma.
    """
    cfg = config or DEFAULT_CONFIG
    t = cfg.cold_chain_thresholds

    if not shipment.temperature_required and not readings:
        return ColdChainAnalysisResult(
            shipment_id=shipment.shipment_id,
            readings_count=0,
            has_excursions=False,
            events=[],
            overall_severity=TemperatureSeverity.NORMAL,
            is_compliant=True,
            mean_temperature=0.0,
            min_temperature=0.0,
            max_temperature=0.0,
            recommendations=["No temperature monitoring required for standard dry cargo."],
            explanation="Dry cargo shipment: Cold-chain monitoring not applicable.",
        )

    if not readings:
        return ColdChainAnalysisResult(
            shipment_id=shipment.shipment_id,
            readings_count=0,
            has_excursions=False,
            events=[],
            overall_severity=TemperatureSeverity.WARNING,
            is_compliant=False,
            mean_temperature=0.0,
            min_temperature=0.0,
            max_temperature=0.0,
            recommendations=["Verify IoT sensor battery and connectivity on transport vehicle."],
            explanation="Warning: No temperature telemetry received for active cold-chain shipment.",
        )

    # Sort chronological
    sorted_readings = sorted(readings, key=lambda r: r.timestamp)
    
    req_min = shipment.required_min_temperature if shipment.required_min_temperature is not None else 2.0
    req_max = shipment.required_max_temperature if shipment.required_max_temperature is not None else 8.0

    temps = [r.temperature for r in sorted_readings]
    min_temp = min(temps)
    max_temp = max(temps)
    mean_temp = sum(temps) / len(temps)

    # Detect Excursion Intervals
    events: List[ExcursionEvent] = []
    current_segment: List[TemperatureReading] = []
    excursion_counter = 1

    for reading in sorted_readings:
        is_violating = (reading.temperature < req_min) or (reading.temperature > req_max)
        if is_violating:
            current_segment.append(reading)
        else:
            if current_segment:
                events.append(_create_excursion_event(
                    shipment, current_segment, excursion_counter, req_min, req_max, t
                ))
                excursion_counter += 1
                current_segment = []

    # Final ongoing segment
    if current_segment:
        events.append(_create_excursion_event(
            shipment, current_segment, excursion_counter, req_min, req_max, t, is_ongoing=True
        ))

    has_excursions = len(events) > 0
    
    # Determine Overall Severity
    if not has_excursions:
        overall_severity = TemperatureSeverity.NORMAL
        is_compliant = True
        explanation = (
            f"All {len(readings)} telemetry readings maintained strictly within required "
            f"temperature envelope ({req_min:.1f}°C to {req_max:.1f}°C). Mean: {mean_temp:.1f}°C."
        )
        recommendations = ["Continue standard transit protocol. Cold-chain integrity verified."]
    else:
        # Get highest severity among events
        sev_rank = {
            TemperatureSeverity.CRITICAL: 3,
            TemperatureSeverity.MAJOR: 2,
            TemperatureSeverity.WARNING: 1,
            TemperatureSeverity.NORMAL: 0,
        }
        max_event_sev = max((e.severity for e in events), key=lambda s: sev_rank[s])
        
        # Escalate to CRITICAL if multiple separate excursions occur on Pharma cargo
        if len(events) >= 2 and shipment.cargo_type == CargoType.PHARMA:
            overall_severity = TemperatureSeverity.CRITICAL
        else:
            overall_severity = max_event_sev

        is_compliant = (overall_severity == TemperatureSeverity.NORMAL)

        total_excursion_duration = sum(e.duration_minutes for e in events)
        max_deviation = max(e.max_deviation_celsius for e in events)

        explanation = (
            f"Temperature excursion detected ({overall_severity.value}) across {len(events)} event(s). "
            f"Total excursion duration: {total_excursion_duration:.0f} mins. "
            f"Maximum deviation: {max_deviation:.1f}°C outside safe threshold ({req_min}°C-{req_max}°C). "
            f"Temperature peaked at {max_temp:.1f}°C (low: {min_temp:.1f}°C)."
        )

        recommendations = _generate_cold_chain_recommendations(
            shipment, overall_severity, events, max_deviation
        )

    return ColdChainAnalysisResult(
        shipment_id=shipment.shipment_id,
        readings_count=len(readings),
        has_excursions=has_excursions,
        events=events,
        overall_severity=overall_severity,
        is_compliant=is_compliant,
        mean_temperature=round(mean_temp, 2),
        min_temperature=round(min_temp, 2),
        max_temperature=round(max_temp, 2),
        recommendations=recommendations,
        explanation=explanation,
    )


def _create_excursion_event(
    shipment: Shipment,
    segment: List[TemperatureReading],
    event_idx: int,
    req_min: float,
    req_max: float,
    thresholds,
    is_ongoing: bool = False,
) -> ExcursionEvent:
    """Build an ExcursionEvent record from contiguous violating readings."""
    start_time = segment[0].timestamp
    end_time = segment[-1].timestamp
    
    # Calculate duration
    duration_mins = max(5.0, (end_time - start_time).total_seconds() / 60.0)
    # If only 1 reading, assume at least 10 minutes interval
    if len(segment) == 1:
        duration_mins = 10.0

    temps = [r.temperature for r in segment]
    min_t = min(temps)
    max_t = max(temps)

    # Max delta outside envelope
    delta_high = max(0.0, max_t - req_max)
    delta_low = max(0.0, req_min - min_t)
    max_delta = max(delta_high, delta_low)

    # Severity classification
    if max_delta > thresholds.major_temp_delta or duration_mins > thresholds.major_duration_mins:
        severity = TemperatureSeverity.CRITICAL
    elif max_delta > thresholds.warning_temp_delta or duration_mins > thresholds.warning_duration_mins:
        severity = TemperatureSeverity.MAJOR
    else:
        severity = TemperatureSeverity.WARNING

    # Pharma cargo has zero tolerance for high temperature excursions
    if shipment.cargo_type == CargoType.PHARMA and max_delta >= 2.0:
        severity = TemperatureSeverity.CRITICAL

    ongoing_str = " (Ongoing)" if is_ongoing else ""
    explanation = (
        f"Excursion #{event_idx}{ongoing_str}: Temp reached {max_t:.1f}°C (deviation: +{max_delta:.1f}°C) "
        f"for {duration_mins:.0f} minutes. Classification: {severity.value}."
    )

    return ExcursionEvent(
        excursion_id=f"EXC-{shipment.shipment_id}-{event_idx:02d}",
        target_id=shipment.shipment_id,
        start_time=start_time,
        end_time=end_time,
        duration_minutes=round(duration_mins, 1),
        min_recorded_temp=round(min_t, 2),
        max_recorded_temp=round(max_t, 2),
        required_min=req_min,
        required_max=req_max,
        max_deviation_celsius=round(max_delta, 2),
        severity=severity,
        is_ongoing=is_ongoing,
        explanation=explanation,
    )


def _generate_cold_chain_recommendations(
    shipment: Shipment,
    severity: TemperatureSeverity,
    events: List[ExcursionEvent],
    max_deviation: float,
) -> List[str]:
    """Generate operational and regulatory action steps based on excursion severity."""
    actions = []
    if severity == TemperatureSeverity.CRITICAL:
        actions.append("IMMEDIATE ACTION: Dispatch nearest backup reefer truck for cargo transfer.")
        actions.append("Trigger automated QA regulatory hold notification for Quality Assurance inspection upon arrival.")
        actions.append("Inspect vehicle refrigeration unit / compressor for mechanical failure.")
    elif severity == TemperatureSeverity.MAJOR:
        actions.append("Alert driver immediately to verify cooling thermostat settings and door seals.")
        actions.append("Prioritize expedited routing to nearest cold-storage hub to prevent product degradation.")
        actions.append("Log temperature excursion data logger records for mandatory audit trail.")
    else:  # WARNING
        actions.append("Issue advisory alert to driver to monitor reefer dashboard temperature.")
        actions.append("Verify pre-cooling status during intermediate transit checkpoints.")

    return actions
