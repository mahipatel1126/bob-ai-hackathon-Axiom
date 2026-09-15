# Chain Guard AI — Solution Overview 🛡️🚀

**Platform Name:** CHAIN GUARD AI  
**Subtitle:** AI-Powered Supply Chain Risk Intelligence & Fleet Optimization  
**Hackathon:** IBM Bob AI Innovation Hackathon 2026  

---

## 1. Value Proposition

**Chain Guard AI** transforms reactive supply chain management into a proactive, intelligent, autonomous operations control tower. By synthesizing geospatial disruption tracking, multi-factor risk scoring, algorithmic route/carrier ranking, Mixed-Integer Linear Programming (MILP) fleet redeployment, and IoT cold-chain telemetry analysis with an **IBM Bob Operations Copilot**, Chain Guard AI empowers logistics teams to resolve high-stakes disruptions before they escalate into catastrophic operational or financial losses.

---

## 2. Core Functional Pillars

```
                     ┌────────────────────────────────────────────────────────┐
                     │                 CHAIN GUARD AI PLATFORM                 │
                     └────────────────────────────────────────────────────────┘
                                                  │
         ┌──────────────────┬─────────────────────┼─────────────────────┬──────────────────┐
         │                  │                     │                     │                  │
         ▼                  ▼                     ▼                     ▼                  ▼
┌──────────────────┐┌──────────────────┐┌──────────────────┐┌──────────────────┐┌──────────────────┐
│   Geospatial     ││   Explainable    ││  Dynamic Route & ││  Fleet Util. &   ││ Cold-Chain IoT & │
│   Disruption     ││   Risk Scoring   ││  Carrier Ranking ││  OR-Tools MILP   ││  Regulatory SOP  │
│   Detection      ││   (0-100 Index)  ││   Optimization   ││   Redeployment   ││  Classification  │
└──────────────────┘└──────────────────┘└──────────────────┘└──────────────────┘└──────────────────┘
         │                  │                     │                     │                  │
         └──────────────────┴─────────────────────┼─────────────────────┴──────────────────┘
                                                  │
                                                  ▼
                                ┌────────────────────────────────────┐
                                │     IBM BOB OPERATIONS COPILOT     │
                                │   Contextual Tactical Reasoning    │
                                └────────────────────────────────────┘
                                                  │
                                                  ▼
                                ┌────────────────────────────────────┐
                                │     DISPATCH & EXECUTIVE ACTION    │
                                └────────────────────────────────────┘
```

---

## 3. Detailed Component Capabilities

### 1. Geospatial Disruption Matching (`src/backend/services/disruption_service.py` & `src/ai/disruption.py`)
- Evaluates active meteorological, strike, accident, and infrastructural disruption zones against freight corridors.
- Calculates great-circle Haversine distances to current vehicle GPS coordinates, traversed waypoints, and upcoming scheduled waypoints.
- Flags affected shipments with deterministic proximity metrics and impact reasons.

### 2. Multi-Factor Explainable Risk Scoring (`src/ai/risk_scoring.py`)
- Calculates a bounded **0 to 100 Risk Score** using transparent, weighted factor breakdowns:
  - **Disruption Severity Factor:** Baseline severity of intersecting hazards (up to 100.0 pts).
  - **Route Exposure Factor:** Percentage of route waypoints exposed to hazard zones.
  - **Deadline Pressure Factor:** Margin between remaining transit hours and delivery deadline.
  - **Cargo Priority & Value Factor:** Criticality weighting (Pharma / Hazardous / High-Value Electronics).
  - **Cold-Chain Sensitivity Factor:** Thermal vulnerability of payload.
- Provides human-readable narrative explanations justifying why each risk score was assigned.

### 3. Dynamic Rerouting & Carrier Optimization (`src/ai/routing.py` & `src/ai/carrier.py`)
- Generates and ranks alternative bypass routes using multi-objective trade-off scoring:
  - Disruption Risk Penalty (50% weight)
  - Transit Time Ratio (30% weight)
  - Financial Cost Ratio (20% weight)
- Evaluates alternative carrier networks on historical reliability ratings (e.g. 92%–98%), verified payload capacity, and refrigeration capabilities.

### 4. Mathematical Fleet Redeployment Optimization (`src/ai/optimization.py`)
- Uses **Google OR-Tools Mixed-Integer Linear Programming (SCIP Solver)** to solve global fleet reassignment.
- Strict operational constraints:
  - **Cold-Chain Guarantee:** Temperature-sensitive shipments can ONLY be assigned to certified reefer trucks.
  - **Payload Sufficiency:** Vehicle capacity must strictly exceed cargo weight and volume.
  - **Proximity & Deadhead Cost:** Minimizes deadhead relocation distance and operational relocation costs.
  - **Deterministic Heuristic Fallback:** Built-in fallback ensuring continuous availability even in constrained environments.

### 5. IoT Cold-Chain Monitoring & Regulatory Compliance (`src/ai/cold_chain.py` & `src/backend/services/cold_chain_service.py`)
- Processes time-series temperature sensor streams against permitted envelopes (e.g., 2.0°C to 8.0°C).
- Identifies contiguous violation clusters, peak thermal deltas, and total breach durations.
- Classifies excursions according to **FDA 21 CFR Part 211** and **WHO Good Distribution Practice (GDP)**:
  - `NORMAL`: Compliant within approved envelope.
  - `WARNING`: Transient minor temperature spike within thermal tolerance.
  - `MAJOR`: Sustained excursion requiring QA review.
  - `CRITICAL`: Severe breach requiring immediate cargo quarantine and emergency reefer rescue.
- Automatically generates formal QA audit dossiers.

### 6. IBM Bob Operations Copilot (`src/backend/bob/bob_client.py` & `src/frontend/src/components/copilot/BobCopilotPanel.tsx`)
- Genuine, load-bearing AI copilot embedded into the operations workflow.
- Receives structured operational context (disruptions, thermal telemetry, route options, fleet availability).
- Provides articulate, actionable decision briefings in response to operator inquiries (e.g., "Why is SHP-1002 critical?", "Which idle reefer should we redeploy?").
- Returns structured action directives with one-click execution triggers (e.g., "Approve Alternate Reroute", "Dispatch Standby Reefer").

---

## 4. Demonstrable End-to-End Workflow

1. **Disruption Emerges:** A critical flood/storm/strike closes a primary transit corridor.
2. **Impact Detection:** Chain Guard AI detects that high-priority shipment `SHP-1002` intersects the hazard zone.
3. **Risk Escalation:** Risk score escalates to `CRITICAL` with explainable factor breakdown.
4. **Alternative Route Selected:** System calculates bypass route `RTE-ALT-AIR-02`, saving 19.0 hours of delay.
5. **Carrier Match:** Reliable carrier option is evaluated and recommended.
6. **Fleet Rescue:** Standby reefer `FLT-REEFER-01` is identified 85.9 km away and redeployed.
7. **Cold-Chain Audit:** Telemetry breach is analyzed and classified under FDA/WHO regulations.
8. **Copilot Synthesis:** IBM Bob synthesizes the entire operational incident and provides an executive action plan.
9. **Dispatch Execution:** Operations manager approves reroute and asset dispatch directly from the command center.

---

## 5. Data Provenance & Transparency Standards

Every data point in Chain Guard AI is explicitly labeled to maintain absolute operational credibility:
- `BACKEND DATA`: Retrieved from verified database/server endpoints.
- `AI PREDICTION`: Output of optimization algorithms (OR-Tools, risk engine).
- `SIMULATED / DEMO DATA`: Deterministic dataset for reproducible hackathon demonstration.
- `IBM BOB RESPONSE`: Contextual reasoning generated by IBM Bob / watsonx integration.
