# ChainGuard AI — Supply Chain Operations Command Center (Frontend + UI)

Welcome to the frontend subsystem of **ChainGuard AI**, built for the L2 Supply Chain Disruption Assistant & Fleet Utilisation Optimizer hackathon project.

**Team Ownership:** Person 3 (Frontend + UI)  
**Branch:** `feature/frontend-dashboard`  
**Frontend Root:** `src/frontend/`

---

## 🚀 Quickstart: How to Run the Frontend

### Prerequisites
- Node.js (v18+ or v20+)
- npm (v9+)

### Installation & Launch
```bash
# 1. Navigate to the frontend directory
cd src/frontend

# 2. Install dependencies (if not already installed)
npm install

# 3. Start local development server (with Hot Module Replacement)
npm run dev

# 4. Open in browser
# http://localhost:3000
```

### Production Build
```bash
cd src/frontend
npm run build
# Compiles TypeScript and builds optimized static assets to src/frontend/dist/
```

To preview the production bundle:
```bash
npm run preview
```

---

## 🛠️ Technology Stack
- **Framework:** [React 18](https://react.dev/) + [TypeScript 5](https://www.typescriptlang.org/)
- **Build Tooling:** [Vite 5](https://vitejs.dev/) (Sub-second cold start, instant HMR)
- **Styling & Theme:** [Tailwind CSS](https://tailwindcss.com/) with a mission-critical tactical dark palette (`command-950` deep slate, high-contrast severity accents: Red `#EF4444`, Amber `#F59E0B`, Emerald `#10B981`, Cyan `#06B6D4`)
- **Iconography:** [Lucide React](https://lucide.dev/)
- **Visualizations:** Custom lightweight SVG schematic corridor routing maps & IoT thermal line chart telemetry (zero heavy GIS bloat, instant rendering)

---

## 📂 Frontend Architecture & Folder Structure

```
src/frontend/
├── dist/                              # Production build artifacts
├── node_modules/                      # Installed npm dependencies
├── public/                            # Static public assets
├── index.html                         # HTML5 shell
├── package.json                       # Scripts and frontend dependencies
├── tsconfig.json                      # Strict TypeScript compiler options
├── tsconfig.node.json                 # Vite node compiler config
├── vite.config.ts                     # Vite build & server configuration
├── tailwind.config.js                 # Custom tactical command center theme
├── postcss.config.js                  # PostCSS plugins (Tailwind, Autoprefixer)
├── README.md                          # Frontend architecture & integration guide (This file)
└── src/
    ├── main.tsx                       # React DOM entrypoint
    ├── App.tsx                        # Master Command Center dashboard layout
    ├── index.css                      # Global styles, fonts, and tactical animations
    │
    ├── types/                         # Strongly-typed data contracts
    │   ├── shipment.ts                # Shipment models & severity levels
    │   ├── disruption.ts              # Active disruption & blast radius models
    │   ├── fleet.ts                   # Fleet asset telemetry & compatibility models
    │   ├── route.ts                   # Rerouting corridor alternatives & cost deltas
    │   ├── coldChain.ts               # IoT temperature excursion & safe band models
    │   ├── copilot.ts                 # IBM Bob queries & structured recommendations
    │   └── kpi.ts                     # Executive operational summary KPIs
    │
    ├── mock/                          # Isolated mock data layer (Demo Scenario)
    │   ├── disruptionsData.ts         # Mumbai JNPT Port Strike & Highway floodings
    │   ├── shipmentsData.ts           # SHP-1001 (Critical Vaccine) & fleet shipments
    │   ├── fleetData.ts               # TRUCK-204 (Idle reefer in Ahmedabad) & assets
    │   ├── routeData.ts               # Ahmedabad -> Hazira Adani Port divert
    │   ├── coldChainData.ts           # 10.4°C thermal excursion telemetry points
    │   ├── copilotData.ts             # Pre-configured structured Bob responses
    │   └── kpiData.ts                 # Real-time aggregated metric counts
    │
    ├── services/                      # Decoupled API abstraction layer
    │   ├── api/
    │   │   └── client.ts              # Universal client with toggleable mock/live mode
    │   ├── disruptionService.ts       # Disruption querying endpoints
    │   ├── shipmentService.ts         # Shipment matrix endpoints
    │   ├── fleetService.ts            # Fleet scheduling & assignment endpoints
    │   ├── coldChainService.ts        # IoT telemetry & excursion endpoints
    │   ├── routeService.ts            # Dynamic corridor optimization endpoints
    │   └── copilotService.ts          # IBM Bob Operations Copilot API
    │
    ├── context/
    │   └── DemoContext.tsx            # Interactive 1-click Demo Story Stepper state
    │
    └── components/
        ├── layout/
        │   ├── Header.tsx             # Command Center header, live UTC clock, stepper
        │   └── KpiBar.tsx             # 5 core operational telemetry KPI cards
        ├── disruptions/
        │   └── DisruptionPanel.tsx    # Active disruptions & gate closure alerts
        ├── shipments/
        │   ├── ShipmentRiskTable.tsx  # High-density shipment prioritization table
        │   └── ShipmentDetailModal.tsx# Detailed shipment telemetry inspector
        ├── routing/
        │   ├── RouteComparison.tsx    # Current vs Alternative route comparison
        │   └── RouteSchematicMap.tsx  # SVG schematic corridor visualization
        ├── fleet/
        │   └── FleetOptimizer.tsx     # Fleet availability & TRUCK-204 deployment
        ├── coldchain/
        │   └── ColdChainMonitor.tsx   # IoT thermal excursion gauge & SVG history
        └── copilot/
            ├── BobCopilotPanel.tsx    # IBM Bob Operations Copilot slide-out drawer
            └── StructuredAnswer.tsx   # Actionable directive operational answer card
```

---

## 🎬 Demo Story Walkthrough (For Hackathon Judges)

The application includes an **interactive scenario stepper** in the top navigation bar to showcase the entire end-to-end incident lifecycle:

1. **Step 1: Normal Baseline**  
   All freight corridors are nominal. Status is green, zero disruptions, normal cold-chain temperatures (4.5°C).
2. **Step 2: Disruption Event (Mumbai Port Strike)**  
   Indefinite dockworker strike at Jawaharlal Nehru Port Trust (JNPT) causes berths 2–5 closure and >48h queues. 5 shipments flagged at risk.
3. **Step 3: At-Risk Isolation (`SHP-1001`)**  
   High-value pharma vaccine `SHP-1001` ($420,000 value) en route to JNPT is flagged **CRITICAL**. IoT sensor reports active temperature excursion at **10.4°C** (safe limit: 2.0–8.0°C) with degraded reefer unit.
4. **Step 4: Route Divert (Hazira Port)**  
   System generates dynamic corridor divert off NH48 at Bharuch to **Adani Hazira Container Terminal** via BlueDart ColdExpress. Saves **37.5 hours** of transit delay.
5. **Step 5: Fleet Redeployment (`TRUCK-204`)**  
   Optimizer identifies **TRUCK-204** (18-ton pre-chilled reefer at 4.0°C, idle in Ahmedabad). Operator executes 1-click dispatch to rendezvous at Vadodara Toll Plaza.
6. **Step 6: Copilot Decision (IBM Bob)**  
   IBM Bob Copilot synthesizes multi-factor operational reasoning into a structured directive card detailing root cause, exact transshipment actions, and cargo preservation outcome.

---

## 🔌 Backend & AI Integration Guide (Person 1 & Person 2)

### Switching from Mock Data to Live Backend
By default, the frontend runs in mock mode using realistic simulation data.  
To connect to Person 1's backend or Person 2's AI service:

1. Create a `.env.local` file inside `src/frontend/`:
```env
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://localhost:8000/api
```
2. Restart Vite (`npm run dev`).

### Expected Backend API Contracts

#### 1. Active Disruptions: `GET /api/disruptions/active`
```json
[
  {
    "disruption_id": "DIS-2026-MUMBAI-01",
    "type": "Port Terminal Strike & Container Congestion",
    "location": "JNPT Port (Nhava Sheva), Navi Mumbai",
    "severity": "CRITICAL",
    "start_time": "2026-09-14T06:00:00Z",
    "expected_duration_hours": 72,
    "affected_shipments_count": 5,
    "affected_shipment_ids": ["SHP-1001", "SHP-1004"],
    "description": "Dockworker walkout at JNPT. Berths 2-5 blocked.",
    "status": "ACTIVE",
    "is_simulated": true
  }
]
```

#### 2. Shipments: `GET /api/shipments`
```json
[
  {
    "shipment_id": "SHP-1001",
    "origin": "Ahmedabad Logistics Park",
    "destination": "JNPT Port (Nhava Sheva), Mumbai",
    "cargo_type": "Temperature-Sensitive Vaccines (Covax-Bio, 2-8°C)",
    "cargo_value": 420000,
    "risk_score": 96,
    "risk_level": "CRITICAL",
    "delay_probability": 0.94,
    "estimated_delay_hours": 42,
    "recommended_action": "Emergency Reroute to Hazira Port + Intercept with TRUCK-204",
    "current_location": "En-route NH48, near Bharuch",
    "carrier": "TransCold Freight Lines",
    "is_cold_chain": true,
    "temperature_current": 10.4,
    "temperature_min": 2.0,
    "temperature_max": 8.0,
    "status": "CRITICAL"
  }
]
```

#### 3. Route Recommendation: `GET /api/routing/recommendations/{shipment_id}`
```json
{
  "shipment_id": "SHP-1001",
  "current_route": {
    "name": "Corridor NH48 South: Ahmedabad to JNPT Mumbai",
    "corridor": "NH48 National Golden Quadrilateral",
    "distance_km": 535,
    "est_transit_hours": 11.5,
    "bottleneck_point": "JNPT Port Gate 4 (BLOCKED - 48h+ queue)",
    "toll_cost_usd": 820
  },
  "recommended_route": {
    "name": "Dynamic Divert: Bharuch/Vadodara to Hazira Adani Port CFS",
    "corridor": "State Highway 6 & Hazira Port Expressway",
    "distance_km": 285,
    "est_transit_hours": 5.2,
    "bottleneck_point": "None (Green Corridor Flagged)",
    "toll_cost_usd": 480
  },
  "alternative_carrier": "BlueDart ColdExpress / Hazira Marine Feeder",
  "original_carrier": "TransCold Freight Lines",
  "estimated_delay_hours": 4.5,
  "hours_saved": 37.5,
  "estimated_cost": 1450,
  "cost_delta": 630,
  "reason": "JNPT Port strike has paralyzed berths. Divert to Adani Hazira Container Terminal bypasses congestion.",
  "risk_reduction_percent": 84
}
```

#### 4. Fleet Assets: `GET /api/fleet/assets`
```json
[
  {
    "asset_id": "TRUCK-204",
    "asset_type": "Heavy Rigid Dual-Temp Reefer (Thermo King)",
    "location": "Ahmedabad Logistics Hub",
    "status": "IDLE",
    "available_capacity": "18 ton",
    "capacity_tons": 18,
    "temperature_capable": true,
    "temp_range_min": -25.0,
    "temp_range_max": 15.0,
    "availability": "IMMEDIATE",
    "is_recommended": true,
    "recommended_assignment": "Intercept SHP-1001 at Vadodara Toll Plaza",
    "recommended_shipment_id": "SHP-1001",
    "recommendation_reason": "Pre-chilled reefer box at 4.0°C positioned 74 km from intercept.",
    "compatibility_score": 98,
    "driver_name": "Rajesh Sharma",
    "current_fuel_percent": 94,
    "eta_to_rendezvous_hours": 1.2
  }
]
```

#### 5. Cold-Chain IoT Telemetry: `GET /api/cold-chain/telemetry/{shipment_id}`
```json
{
  "shipment_id": "SHP-1001",
  "cargo_description": "Covax-Bio Ultra-Sensitive Vaccines",
  "sensor_id": "IOT-TEMP-GUJ-9021",
  "temperature": 10.4,
  "allowed_min": 2.0,
  "allowed_max": 8.0,
  "excursion_minutes": 42,
  "peak_temperature": 11.1,
  "severity": "CRITICAL",
  "action": "Urgent Transshipment to Backup Reefer TRUCK-204 at Vadodara",
  "time_to_critical_hours": 1.8,
  "reefer_unit_status": "DEGRADED",
  "battery_level_percent": 88,
  "telemetry_history": [
    { "timestamp": "10:00 UTC", "time_label": "-60m", "temp": 4.5, "ambient_temp": 34.2, "status": "NORMAL" },
    { "timestamp": "11:00 UTC", "time_label": "Current", "temp": 10.4, "ambient_temp": 36.6, "status": "EXCURSION" }
  ]
}
```

#### 6. IBM Bob Operations Copilot: `POST /api/copilot/query`
**Request Payload:**
```json
{
  "query": "Why is SHP-1001 critical?",
  "context_shipment_id": "SHP-1001"
}
```
**Response Format:**
```json
{
  "id": "bob-resp-1",
  "sender": "BOB",
  "timestamp": "Just now",
  "content": "Shipment SHP-1001 is at immediate risk due to temperature excursion...",
  "structured_recommendation": {
    "priority": "CRITICAL",
    "shipment_id": "SHP-1001",
    "reason": "Temperature excursion (10.4°C) + JNPT Port strike",
    "recommended_action": "Rendezvous at Vadodara with TRUCK-204 and divert to Hazira Adani Port.",
    "alternative_route": "Adani Hazira CFS Terminal (285 km)",
    "fleet_asset_assigned": "TRUCK-204",
    "expected_delay_saved_hours": 37.5,
    "operational_impact": "Saves 37.5h delay, prevents $420k loss."
  },
  "suggested_actions": [
    "Dispatch TRUCK-204 to Vadodara Toll Plaza",
    "Issue Route Divert Order to Hazira Port"
  ]
}
```

---

## 🔒 Compliance & Integrity Safeguards
- **Protected Files:** No modifications made to `src/backend/`, `src/ai/`, `.github/workflows/`, or `submission.yaml`.
- **Git Branch:** Work restricted entirely to `feature/frontend-dashboard`.
- **Secrets / Environment:** No secrets or private credentials embedded in frontend code.
