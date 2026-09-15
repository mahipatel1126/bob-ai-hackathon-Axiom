# Chain Guard AI — API Contracts & Integration Guide 🛡️📡

This document outlines the REST API contracts, data models, and integration interfaces for **Person 2 (AI/Optimization Lead)** and **Person 3 (Frontend Dashboard Lead)**.

---

## 🌐 Base URL & Server Configuration

- **Local Endpoint:** `http://localhost:8000`
- **Default Port:** `8000` (Configurable via `PORT` environment variable or `--port <port>`)
- **Content-Type:** `application/json`
- **CORS Support:** Full cross-origin support enabled (`*`) with pre-flight `OPTIONS` handling for frontend client libraries (Axios, Fetch, React/Next.js).

---

## 📋 REST API Endpoints Overview

| Method | Path | Description | Typical Consumer |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Service health and runtime status | Ops / Frontend |
| `GET` | `/api/overview` | KPI metric aggregations for dashboard | Person 3 (Frontend) |
| `GET` | `/api/shipments` | List all tracked shipments | Person 3 (Frontend) |
| `GET` | `/api/shipments/{shipment_id}` | Retrieve details for a single shipment | Person 3 (Frontend) |
| `GET` | `/api/shipments/{shipment_id}/disruptions` | Disruption impacts specific to this shipment | Person 2 & 3 |
| `GET` | `/api/disruptions` | List all tracked disruption incidents | Person 3 (Frontend) |
| `GET` | `/api/disruptions/affected-shipments` | All shipments intersecting active disruption zones | Person 2 & 3 |
| `GET` | `/api/reroute/{shipment_id}` | Candidate routes, carriers & AI/fallback recommendation | Person 2 & 3 |
| `GET` | `/api/fleet` | Query available & idle fleet assets | Person 3 (Frontend) |
| `GET` | `/api/fleet/redeployment?shipment_id={id}` | Proximity & capacity matched idle asset redeployment | Person 2 & 3 |
| `POST` | `/api/fleet/redeployment` | Dispatch a redeployment order | Person 3 (Frontend) |
| `GET` | `/api/cold-chain/{shipment_id}` | Thermal telemetry analysis & compliance status | Person 3 (Frontend) |
| `GET` | `/api/cold-chain/{shipment_id}/audit` | FDA 21 CFR 211 / WHO GDP compliance dossier | Person 3 (Frontend) |
| `GET` | `/api/cold-chain/excursions` | List all shipments with detected temperature breaches | Person 3 (Frontend) |
| `GET` | `/api/bob/incident-summary/{shipment_id}` | Consolidated executive incident briefing | Person 3 & Demo |

---

## 🔍 Detailed Endpoint Documentation

### 1. System Health & Overview

#### `GET /api/health`
Returns runtime connectivity and IBM Bob connection state.
```json
{
  "status": "healthy",
  "service": "Chain Guard AI Backend",
  "version": "1.0.0",
  "mode": "offline_demo_ready",
  "bob_connected": false
}
```

#### `GET /api/overview`
Returns high-level KPI counts for the executive dashboard overview cards.
```json
{
  "total_shipments": 5,
  "active_disruptions": 3,
  "affected_shipments_count": 4,
  "idle_fleet_assets": 4,
  "active_temperature_excursions": 2,
  "system_status": "DISRUPTIONS_ACTIVE"
}
```

---

### 2. Disruption Detection & Impact Matching

#### `GET /api/disruptions/affected-shipments`
Evaluates active disruptions against shipment corridors and GPS waypoints via great-circle Haversine calculations.

**Example Response:**
```json
{
  "total_affected": 4,
  "affected_shipments": [
    {
      "shipment_id": "SHP-1002",
      "disruption_id": "DIS-2026-001",
      "disruption_title": "Winter Storm Nova - Midwest Severe Blizzard & Road Closures",
      "disruption_type": "WEATHER",
      "disruption_severity": "CRITICAL",
      "affected_location": "Chicago I-80 West Gate (Midwest Great Lakes Corridor)",
      "impact_distance_km": 41.73,
      "impact_radius_km": 250.0,
      "impact_reason": "Upcoming scheduled waypoint 'Chicago I-80 West Gate' is 41.7 km from disruption epicenter (within 250.0 km radius).",
      "risk_level": "CRITICAL",
      "urgency": "IMMEDIATE",
      "carrier": "Apex Pharma Trans",
      "cargo_type": "PHARMACEUTICALS",
      "is_cold_chain": true,
      "shipment_status": "DISRUPTED",
      "current_coordinates": {
        "latitude": 41.681,
        "longitude": -86.32
      }
    }
  ]
}
```

---

### 3. Rerouting & Carrier Alternatives

#### `GET /api/reroute/{shipment_id}`
Returns candidate routes, carriers, and a recommendation package.

**Example Response:**
```json
{
  "recommendation_id": "REC-DET-0AD8A9",
  "shipment_id": "SHP-1002",
  "disruption_id": "DIS-2026-001",
  "source": "deterministic_backend_fallback",
  "original_route_summary": "Standard transit via Apex Pharma Trans",
  "recommended_route_id": "RTE-ALT-AIR-02",
  "recommended_carrier_id": "CARRIER-EXP-01",
  "rationale": "[Deterministic Fallback] Selected 'Critical BioPharma Air Cargo Airlift (IND -> DEN)' bypassing disruption area with risk score 0.04. Assigned carrier 'Vanguard Critical Express Air & Expedited' (AIR) based on 98% reliability rating.",
  "delay_hours_saved": 19.0,
  "cost_delta_usd": 3300.0,
  "optimization_score": 0.88,
  "status": "PENDING_APPROVAL",
  "alternatives": [...],
  "carrier_options": [...]
}
```

---

### 4. Fleet Utilisation & Redeployment

#### `GET /api/fleet/redeployment?shipment_id={shipment_id}`
Ranks idle fleet assets by proximity, payload capacity, and cold-chain/reefer compatibility.

**Example Response:**
```json
{
  "shipment_id": "SHP-1002",
  "candidates_count": 3,
  "candidates": [
    {
      "shipment_id": "SHP-1002",
      "asset_id": "FLT-REEFER-01",
      "asset_name": "ThermoKing SmartReefer Pro 40",
      "asset_type": "REEFER_TRUCK",
      "current_location": {
        "name": "Gary Inland Logistics Depot",
        "city": "Gary",
        "country": "USA",
        "coordinates": { "latitude": 41.5934, "longitude": -87.3465 }
      },
      "distance_km": 85.9,
      "capacity_match": true,
      "reefer_match": true,
      "is_fully_compatible": true,
      "priority": "CRITICAL",
      "reason": "Immediate proximity (85.9 km away at Gary Inland Logistics Depot); Payload capacity verified (19,500 kg capacity vs 1,150 kg cargo); Cold-chain compliant (equipped with 72.0h backup power).",
      "available_driver": "Marcus Vance (Active / Standby)"
    }
  ]
}
```

#### `POST /api/fleet/redeployment`
Issues a formal asset dispatch order.

**Request Body:**
```json
{
  "asset_id": "FLT-REEFER-01",
  "target_shipment_id": "SHP-1002",
  "urgency": "HIGH",
  "reason": "Emergency reefer backup dispatch"
}
```
**Response (201 Created):**
```json
{
  "request_id": "RDP-4190CD",
  "asset_id": "FLT-REEFER-01",
  "target_shipment_id": "SHP-1002",
  "status": "DISPATCHED",
  "driver_assigned": "Marcus Vance (Active / Standby)",
  "created_at": "2026-09-15T00:30:00Z"
}
```

---

### 5. Cold-Chain IoT Telemetry & Regulatory Excursions

#### `GET /api/cold-chain/{shipment_id}`
Processes IoT time-series readings against FDA 21 CFR 211 / WHO GDP thresholds.

**Example Response:**
```json
{
  "shipment_id": "SHP-1005",
  "cargo_name": "Pediatric Critical Vaccines & Insulin Formulations",
  "is_cold_chain": true,
  "target_range": "2.0°C to 8.0°C",
  "readings_count": 7,
  "min_temperature_c": 4.0,
  "max_temperature_c": 18.2,
  "mean_temperature_c": 10.71,
  "excursion_detected": true,
  "total_excursion_duration_minutes": 150.0,
  "severity": "CRITICAL",
  "compliance_status": "NON_COMPLIANT_QUARANTINE",
  "regulatory_framework": "FDA 21 CFR 211 / WHO Good Distribution Practice (GDP)",
  "recommended_action": "CRITICAL THERMAL BREACH: Immediate quarantine mandatory upon arrival per FDA 21 CFR 211 / WHO GDP. Do not release cargo for clinical/commercial use. Initiate immediate quality assurance investigation and asset redeployment.",
  "excursion_events": [...]
}
```

---

### 6. IBM Bob & Executive Incident Intelligence

#### `GET /api/bob/incident-summary/{shipment_id}`
Consolidates disruption impact, rerouting, fleet candidates, and cold-chain status into an executive decision briefing.

**Example Response:**
```json
{
  "incident_id": "INC-SHP-1002",
  "shipment_id": "SHP-1002",
  "briefing_title": "ChainGuard Incident Briefing: mRNA Oncology Therapeutics & Clinical Trials (SHP-1002)",
  "source": "local_fallback_engine",
  "bob_connected": false,
  "is_simulated": true,
  "executive_summary": "Shipment SHP-1002 (mRNA Oncology Therapeutics & Clinical Trials) in transit from Boston BioPharma Gate 2 to Denver Hospital Receiving via Apex Pharma Trans is actively impacted by Winter Storm Nova - Midwest Severe Blizzard & Road Closures. Upcoming scheduled waypoint 'Chicago I-80 West Gate' is 41.7 km from disruption epicenter (within 250.0 km radius). COLD-CHAIN ALERT: A MINOR thermal deviation has been detected. Cargo observed temperatures reached 8.7°C (Permitted envelope: 2.0°C to 8.0°C). Regulatory Status: WARNING. RECOMMENDED REROUTE: [Deterministic Fallback] Selected 'Critical BioPharma Air Cargo Airlift (IND -> DEN)' bypassing disruption area with risk score 0.04. Assigned carrier 'Vanguard Critical Express Air & Expedited' (AIR) based on 98% reliability rating. Estimated delay saved: 19.0 hours. REDEPLOYMENT ASSET: ThermoKing SmartReefer Pro 40 (REEFER_TRUCK) is currently idle 85.9 km away at Gary Inland Logistics Depot.",
  "risk_assessment": {
    "risk_level": "CRITICAL",
    "urgency": "IMMEDIATE",
    "cold_chain_severity": "MINOR",
    "compliance_status": "WARNING"
  },
  "recommended_actions": [
    {
      "action_type": "CORRIDOR_REROUTE",
      "directive": "Execute bypass route 'RTE-ALT-AIR-02'.",
      "delay_avoided_hours": 19.0
    },
    {
      "action_type": "ASSET_REDEPLOYMENT",
      "directive": "Dispatch standby asset FLT-REEFER-01 (ThermoKing SmartReefer Pro 40)."
    }
  ]
}
```

---

## 🤖 Person 2 (AI & Optimization) Integration Contract

Person 2 can connect their AI route optimization model using **either** of the following two simple options:

### Option A: Direct Function Hook Registration
In `src/ai/route_optimizer` or during startup, import `reroute_service` and register your optimization function:

```python
from src.backend.services.reroute_service import register_ai_route_optimizer

def my_ai_optimizer(ai_input: dict) -> dict:
    shipment = ai_input["shipment"]
    disruption = ai_input["disruption"]
    candidate_routes = ai_input["candidate_routes"]
    candidate_carriers = ai_input["candidate_carriers"]
    constraints = ai_input["constraints"]

    # Person 2 optimization logic (OR-Tools, Heuristics, ML)
    best_route = candidate_routes[0]
    best_carrier = candidate_carriers[0]

    return {
        "recommended_route_id": best_route["route_id"],
        "recommended_carrier_id": best_carrier["carrier_id"],
        "reasoning": "AI model selected lowest transit risk avoiding snow storm.",
        "score": 0.96,
        "delay_hours_saved": 14.5,
        "cost_delta_usd": 250.0,
    }

register_ai_route_optimizer(my_ai_optimizer)
```

### Option B: Auto-Discovered Module Function
Implement a function named `optimize_route(input_dict: dict) -> dict` inside [`src/ai/route_optimizer/__init__.py`](file:///d:/Supply%20Chain%20Disruption%20Assistant/chain-guard-ai/src/ai/route_optimizer/__init__.py). The backend will automatically discover and invoke it if present.

---

## 🎨 Person 3 (Frontend Dashboard) Integration Contract

1. **Base URL:** Connect client applications to `http://localhost:8000/api`.
2. **CORS:** All routes return `Access-Control-Allow-Origin: *`. No local proxy or server-side rewrite required.
3. **Core Workflow for Dashboard:**
   - Call `/api/overview` on initial load for top stat cards.
   - Call `/api/disruptions/affected-shipments` to display map markers with coordinates and urgency badges (`CRITICAL`, `HIGH`, `MEDIUM`).
   - Call `/api/reroute/{id}` and `/api/fleet/redeployment?shipment_id={id}` when clicking on a distressed shipment.
   - Call `/api/cold-chain/{id}` to plot temperature time-series graphs and display regulatory compliance badges (`FDA 21 CFR 211 / WHO GDP`).
   - Call `/api/bob/incident-summary/{id}` to show the executive incident briefing modal.
