# Chain Guard AI — AI & Optimization Layer (Person 2)

**L2 Supply Chain Disruption Assistant & Fleet Utilisation Optimizer**

---

## 1. Purpose

The `src/ai` module is the intelligence and mathematical optimization backbone of Chain Guard AI. It provides transparent, explainable decision support for real-time supply chain operations. 

When external hazards (storms, port congestion, road accidents) occur, this module:
1. Determines which shipments in transit are physically or temporally impacted.
2. Calculates an explainable 0–100 risk score and urgency level.
3. Reroutes shipments around active hazard corridors.
4. Dynamically evaluates backup 3PL carriers based on capacity, reliability, and cold-chain compliance.
5. Identifies idle or underutilized internal fleet vehicles.
6. Solves a global Mixed-Integer Linear Programming (MILP) optimization to redeploy idle fleet assets to at-risk shipments.
7. Audits cold-chain IoT temperature telemetry, identifying excursion duration, peak delta, and regulatory severity.
8. Synthesizes a unified, executive-level operational action package.

---

## 2. Architecture

```
                               ┌───────────────────────────┐
                               │  Disruptions & Shipments  │
                               └─────────────┬─────────────┘
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
       ┌──────────────────────────────┐              ┌──────────────────────────────┐
       │  Disruption Impact Engine    │              │   Cold-Chain Telemetry Audit │
       │  (Corridor & Temporal Match) │              │   (Excursion & Severity)     │
       └──────────────┬───────────────┘              └──────────────┬───────────────┘
                      │                                             │
                      └──────────────────────┬──────────────────────┘
                                             ▼
                              ┌─────────────────────────────┐
                              │ Explainable Risk Scoring    │
                              │ (Multi-Factor 0-100 Engine) │
                              └──────────────┬──────────────┘
                                             │
          ┌──────────────────────────────────┼──────────────────────────────────┐
          ▼                                  ▼                                  ▼
┌──────────────────┐               ┌───────────────────┐              ┌───────────────────┐
│ Dynamic Reroute  │               │ Backup 3PL Carrier│              │ Fleet Optimization│
│ Evaluation       │               │ Capacity Match    │              │ (OR-Tools MILP)   │
└─────────┬────────┘               └─────────┬─────────┘              └─────────┬─────────┘
          │                                  │                                  │
          └──────────────────────────────────┼──────────────────────────────────┘
                                             ▼
                           ┌──────────────────────────────────┐
                           │ Unified Operational Action       │
                           │ Recommendation (L2 Action Pack)  │
                           └──────────────────────────────────┘
```

---

## 3. Component Directory Structure

```
src/ai/
├── __init__.py            # Main package exports
├── schemas.py             # Typed Pydantic v2 domain schemas (Inputs & Outputs)
├── models.py              # Schema re-exports for easy accessibility
├── config.py              # Configurable thresholds, weights, and scoring matrices
├── disruption.py          # Disruption impact detection and corridor intersection
├── risk_scoring.py        # 0-100 explainable multi-factor shipment risk scoring
├── routing.py             # Candidate route evaluation and disruption avoidance ranking
├── carrier.py             # Alternative carrier ranking and constraint checking
├── fleet.py               # Fleet asset categorization (Idle/Underutilized) & suitability
├── cold_chain.py          # IoT temperature excursion detection & regulatory classification
├── optimization.py        # Global fleet redeployment matching (OR-Tools / Greedy Heuristic)
├── recommendations.py     # Unified L2 operational action synthesizer
├── demo_data.py           # 8 deterministic test scenarios (Simulated demo dataset)
├── run_demo.py            # End-to-end interactive CLI demo runner
├── README.md              # Technical and integration documentation
└── tests/                 # Complete unit test suite
    ├── __init__.py
    ├── test_disruption.py
    ├── test_risk_scoring.py
    ├── test_routing.py
    ├── test_carrier.py
    ├── test_fleet.py
    ├── test_cold_chain.py
    ├── test_optimization.py
    ├── test_recommendations.py
    └── test_demo_data.py
```

---

## 4. Input Schemas

All inputs are strongly typed Pydantic models in `src.ai.schemas`:

| Model | Key Fields | Description |
| :--- | :--- | :--- |
| `Shipment` | `shipment_id`, `origin`, `destination`, `route`, `priority`, `delivery_deadline`, `cargo_type`, `temperature_required`, `required_min_temperature`, `required_max_temperature`, `weight_kg`, `value_inr`, `status` | Active shipment entity |
| `Disruption` | `disruption_id`, `type`, `location`, `region`, `severity`, `start_time`, `estimated_duration_hours`, `affected_routes`, `affected_locations`, `delay_impact_hours` | Hazard / disruption event |
| `FleetAsset` | `vehicle_id`, `vehicle_type`, `capacity_kg`, `current_location`, `availability`, `current_utilization`, `temperature_capability`, `min_temp_capable`, `max_temp_capable`, `cost_per_km` | Fleet vehicle asset telemetry |
| `TemperatureReading` | `reading_id`, `shipment_id`, `vehicle_id`, `timestamp`, `temperature`, `required_min_temperature`, `required_max_temperature` | IoT cold-chain telemetry record |
| `RouteOption` | `route_id`, `name`, `waypoints`, `distance_km`, `estimated_time_hours`, `estimated_cost`, `risk_score`, `disruption_exposure` | Candidate alternative route |
| `CarrierOption` | `carrier_id`, `name`, `available_capacity_kg`, `estimated_cost`, `reliability_score`, `estimated_delivery_hours`, `temperature_capable` | Candidate 3PL carrier |

---

## 5. Output Schemas

| Model | Key Fields | Description |
| :--- | :--- | :--- |
| `DisruptionImpactResult` | `shipment_id`, `affected`, `impact_level`, `reasons`, `estimated_delay_hours`, `intersecting_locations` | Disruption impact evaluation |
| `RiskScoreResult` | `shipment_id`, `score` (0-100), `risk_level` (LOW/MEDIUM/HIGH/CRITICAL), `contributing_factors`, `factor_explanations`, `explanation`, `mitigation_urgency` | Explainable risk assessment |
| `RouteRecommendationResult`| `recommended_route`, `ranked_routes`, `selection_reason`, `score_breakdown` | Ranked rerouting options |
| `CarrierRecommendationResult`| `recommended_carrier`, `ranked_carriers`, `selection_reason`, `rejected_carriers` | Ranked carriers & rejection notes |
| `IdleFleetResult` | `idle_vehicles`, `underutilized_vehicles`, `active_vehicles`, `unavailable_vehicles`, `utilization_rate_avg` | Fleet classification summary |
| `FleetOptimizationResult` | `assignments` (list of `FleetAssignment`), `unassigned_shipments`, `unused_vehicles`, `total_redeployment_cost`, `average_utilization_improvement` | Global fleet redeployment plan |
| `ColdChainAnalysisResult` | `has_excursions`, `events` (list of `ExcursionEvent`), `overall_severity`, `is_compliant`, `mean_temperature`, `recommendations` | Cold-chain audit & compliance |
| `OperationalRecommendation`| `recommendation_id`, `shipment_id`, `action_summary`, `priority`, `reasons`, `impact_analysis`, `risk_assessment`, `route_recommendation`, `carrier_recommendation`, `fleet_assignment`, `cold_chain_status`, `executive_summary` | **Unified L2 Action Recommendation** |

---

## 6. Risk Scoring Methodology

The 0–100 shipment risk score uses a transparent multi-factor weighted decision model:

$$\text{Risk Score} = \sum_{i} w_i \times S_i$$

### Factor Weights:
- **Disruption Severity ($w=0.30$):** Impact level from active disruptions (Critical: 100, High: 75, Medium: 45, Low: 20).
- **Route Exposure & Delay ($w=0.20$):** Projected delay magnitude (12+ hrs: 100 pts, 6-12 hrs: 75 pts, 2-6 hrs: 45 pts).
- **Deadline Pressure / Slack ($w=0.20$):** Time buffer deficit against required ETA ($<0$ buffer: 80–100 pts).
- **Cargo Priority & Commercial Value ($w=0.15$):** Cargo criticality (Critical Pharma/Chemical: 100 pts, High: 70 pts).
- **Cold-Chain Excursion Sensitivity ($w=0.15$):** Active excursion severity on temperature-sensitive cargo.

### Risk Level Tiers (Configurable in `config.py`):
- `0.0 – 29.0`: **LOW**
- `30.0 – 59.0`: **MEDIUM**
- `60.0 – 79.0`: **HIGH**
- `80.0 – 100.0`: **CRITICAL**

*Every calculation produces both numerical weights and narrative explanations for Person 3's UI.*

---

## 7. Optimization Methodology

The fleet redeployment optimizer matches idle or underutilized internal assets to high-risk shipments.

### Formulation:
- **Objective:** Maximize total operational benefit:
$$\max \sum_{i \in \text{Shipments}} \sum_{j \in \text{Fleet}} \text{BenefitScore}(i, j) \cdot x_{i,j}$$
- **Constraints:**
  1. $\sum_{j} x_{i,j} \le 1 \quad \forall i$ (Each shipment receives at most one assigned vehicle)
  2. $\sum_{i} x_{i,j} \le 1 \quad \forall j$ (Each vehicle is assigned to at most one shipment)
  3. Physical Capacity: $\text{VehicleCapacity}_j \ge \text{ShipmentWeight}_i$
  4. Temperature Envelope: If temperature required, vehicle must be a certified reefer covering the $[\text{MinTemp}_i, \text{MaxTemp}_i]$ envelope.
  5. Availability: Vehicle must not be in maintenance or reserved status.
- **Solvers:** Implemented using **Google OR-Tools SCIP MILP Solver** with a deterministic **Greedy Multi-Objective Heuristic** fallback.

---

## 8. Cold-Chain Severity Methodology

IoT temperature telemetry is evaluated against the shipment's required envelope ($T_{\min}$ to $T_{\max}$):
- **Contiguous Excursion Segmentation:** Violated readings are grouped into discrete events with measured duration (minutes) and peak deviation ($\Delta T = |T_{\text{actual}} - T_{\text{boundary}}|$).
- **Severity Classification:**
  - `NORMAL`: All readings within bounds ($2^\circ\text{C} - 8^\circ\text{C}$).
  - `WARNING`: Minor excursion ($\Delta T \le 1.5^\circ\text{C}$) for $\le 30\text{ mins}$.
  - `MAJOR`: Moderate excursion ($\Delta T \le 4.0^\circ\text{C}$) or duration $30 - 90\text{ mins}$.
  - `CRITICAL`: Severe excursion ($\Delta T > 4.0^\circ\text{C}$), sustained duration $> 90\text{ mins}$, or repeated spikes on Pharma vaccines.
- **Action Generation:** Automatically suggests corrective SOPs (e.g. "Dispatch backup reefer", "Trigger QA Regulatory Quarantine").

---

## 9. Demo Data Scenarios

Deterministic scenarios in `src.ai.demo_data` for standalone execution:

1. **Scenario 1:** Normal dry shipment (Pune $\to$ Bengaluru, 0 disruptions, Low risk).
2. **Scenario 2:** Severe weather disruption (Mumbai $\to$ Delhi, Surat Floods, Critical risk, reroute recommended).
3. **Scenario 3:** High-priority Pharma vaccine shipment with tight 10h deadline.
4. **Scenario 4:** Suitable idle reefer vehicle stationed nearby in Hyderabad.
5. **Scenario 5:** Unsuitable dry box truck rejected for cold-chain cargo due to missing reefer unit.
6. **Scenario 6:** Compliant cold-chain telemetry ($4.1^\circ\text{C} - 4.8^\circ\text{C}$).
7. **Scenario 7:** Warning cold-chain excursion ($9.2^\circ\text{C}$ transient loading spike).
8. **Scenario 8:** Critical cold-chain excursion ($14.8^\circ\text{C}$ sustained compressor failure).

---

## 10. How to Run the Demo

Execute the interactive command-line demonstration:

```bash
# Run from repository root:
python -m src.ai.run_demo
```

---

## 11. How to Run Unit Tests

Execute the complete pytest suite:

```bash
# Run all unit tests
python -m pytest

# Run with verbose output and coverage
python -m pytest -v src/ai/tests/
```

---

## 12. Backend Integration Guide (For Person 1)

Person 1 can directly import and call the high-level API without configuring external web services:

```python
from src.ai import (
    generate_operational_recommendation,
    generate_batch_recommendations,
    Shipment,
    Disruption,
    FleetAsset,
    TemperatureReading,
    RouteOption,
    CarrierOption,
)

# In your FastAPI / Flask router or Celery task:
@app.post("/api/v1/recommendations/evaluate")
def evaluate_shipment_endpoint(payload: ShipmentPayload):
    # Convert ORM models to Pydantic domain models:
    shipment = Shipment(**payload.shipment_dict)
    disruptions = [Disruption(**d) for d in payload.active_disruptions]
    candidate_routes = [RouteOption(**r) for r in payload.routes]
    fleet = [FleetAsset(**f) for f in payload.available_fleet]
    readings = [TemperatureReading(**t) for t in payload.recent_readings]

    # Call AI Engine directly:
    recommendation = generate_operational_recommendation(
        shipment=shipment,
        disruptions=disruptions,
        candidate_routes=candidate_routes,
        available_fleet=fleet,
        temperature_readings=readings,
    )

    # Return dict / JSON directly to frontend or store in DB:
    return recommendation.model_dump(mode="json")
```

### Expected Input Fields from Backend:
- **Shipments:** `shipment_id`, `origin`, `destination`, `route`, `priority`, `delivery_deadline`, `cargo_type`, `temperature_required`, `weight_kg`.
- **Disruptions:** `disruption_id`, `type`, `location`, `severity`, `affected_locations`, `delay_impact_hours`.
- **Fleet Assets:** `vehicle_id`, `vehicle_type`, `capacity_kg`, `current_location`, `current_utilization`, `temperature_capability`.
- **Temperature Readings:** `timestamp`, `temperature`, `required_min_temperature`, `required_max_temperature`.

---

## 13. Frontend Integration Guide (For Person 3)

The AI module produces clean, UI-ready JSON matching Person 3's dashboard widgets:

```json
{
  "recommendation_id": "REC-SHP-PHARMA-303-E59B65",
  "shipment_id": "SHP-PHARMA-303",
  "priority": "CRITICAL",
  "action_summary": "Reroute via 'Inland Bypass via Kurnool & Kadapa' and dispatch backup Reefer FLT-REEFER-01 from Hyderabad.",
  "risk_assessment": {
    "score": 89.0,
    "risk_level": "CRITICAL",
    "contributing_factors": {
      "disruption_severity": 100.0,
      "route_exposure": 75.0,
      "deadline_pressure": 80.0,
      "cargo_priority": 100.0,
      "cold_chain_sensitivity": 100.0
    },
    "explanation": "Risk score is 89.0/100 (CRITICAL) driven by active corridor disruption, strict delivery timeline risk, temperature excursion alert, high-priority PHARMA cargo."
  },
  "route_recommendation": {
    "recommended_route": {
      "route_id": "RT-303-KADAPA",
      "name": "Inland Bypass via Kurnool & Kadapa (NH40)",
      "distance_km": 620.0,
      "estimated_time_hours": 9.2,
      "estimated_cost": 31500.0,
      "risk_score": 0.0
    },
    "selection_reason": "Selected 'Inland Bypass' because it completely bypasses active disruption zones."
  },
  "cold_chain_status": {
    "overall_severity": "CRITICAL",
    "is_compliant": false,
    "events": [
      {
        "duration_minutes": 140.0,
        "max_deviation_celsius": 6.8,
        "max_recorded_temp": 14.8,
        "severity": "CRITICAL"
      }
    ],
    "recommendations": [
      "IMMEDIATE ACTION: Dispatch nearest backup reefer truck for cargo transfer."
    ]
  },
  "executive_summary": "Shipment SHP-PHARMA-303 (PHARMA) is assessed at Risk Score 89.0/100 (CRITICAL)..."
}
```

---

## 14. Important Limitations & Assumptions

1. **Decision Support (Not Autonomous Dispatch):** This AI module produces recommendations for human dispatcher review (L2 Supply Chain Assistant).
2. **Prototype Routing & Distance Estimation:** Inter-city distances use standard highway network distance matrices; integration with live mapping APIs (e.g. Google Maps / OpenStreetMap) can be connected by Person 1 later.
3. **Simulated Datasets:** The demo scenarios provide realistic, deterministic data for validation and hackathon demonstrations; they are not live IoT streams.
4. **Regulatory Classification:** Cold-chain compliance thresholds align with standard Good Distribution Practice (GDP) 2°C–8°C guidelines for cold-chain pharmaceuticals but do not constitute legal/customs certifications.
