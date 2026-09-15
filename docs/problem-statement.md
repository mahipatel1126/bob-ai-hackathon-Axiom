# Chain Guard AI — Problem Statement 🛡️

**Hackathon Challenge:** L2 Supply Chain Disruption Assistant & Fleet Utilisation Optimizer  
**Competition:** IBM Bob AI Innovation Hackathon 2026  
**Platform:** Chain Guard AI  

---

## 1. Executive Summary

Global and regional supply chains operate in highly dynamic, volatile environments. Severe meteorological events, sudden port congestion, labor strikes, infrastructural accidents, and regulatory compliance breaches routinely trigger cascading disruptions across multi-modal freight networks.

Concurrently, commercial fleet capacity remains unevenly and inefficiently utilized. Substantial percentages of long-haul and regional transport fleets sit idle or operate on deadhead return routes with empty cargo holds.

When unforeseen disruptions strike, human operations teams are hampered by fragmented telemetry, delayed incident alerts, and slow manual decision-making. In high-stakes cold-chain logistics—such as pharmaceutical biologics and life-saving vaccines—even minor delays or thermal excursions can result in total cargo destruction, regulatory penalties, and critical shortages at destination health facilities.

---

## 2. Core Operational Vulnerabilities

### A. Reactive Disruption Awareness & Cascade Delays
- **Corridor Bottlenecks:** Active weather hazards (floods, blizzards) or labor stoppages (port strikes) are often recognized only after trucks enter affected corridors, causing demurrage fees and multi-day delays.
- **Geographic Blindspots:** Lack of spatial corridor evaluation means operations teams fail to project whether a disruption 200 km ahead intersects upcoming waypoints.

### B. Unexplainable & Subjective Risk Prioritization
- Without systematic multi-factor risk scoring, dispatchers treat all delayed shipments equally, rather than prioritizing high-value, temperature-sensitive, or life-critical loads under strict delivery deadlines.
- "Black-box" predictive tools provide risk flags without explainable factor breakdowns (disruption severity, exposure percentage, deadline pressure, cargo priority, and thermal sensitivity), reducing operator trust.

### C. Fleet Sub-Optimization & Asset Mismatches
- While primary haulers become stranded in bottlenecked corridors, standby fleet assets at nearby logistics hubs remain idle due to lack of real-time spatial matching.
- Ad-hoc redeployment frequently leads to catastrophic equipment mismatches—such as assigning non-refrigerated dry box trucks to temperature-sensitive pharmaceutical loads, or choosing vehicles with insufficient payload capacity.

### D. Cold-Chain Degradation & Regulatory Non-Compliance
- Perishable biologics, oncology therapeutics, and vaccines require strict temperature ranges (typically **2.0°C to 8.0°C**).
- Thermal excursions caused by refrigeration unit failures or extended transit delays must be analyzed against strict regulatory standards (**FDA 21 CFR Part 211** and **WHO Good Distribution Practice**).
- Operations teams lack automated audit trail generation, contiguous excursion duration calculations, and immediate emergency SOP triggers (e.g. backup reefer dispatch, regulatory hold).

### E. Disconnected Operations Decision Support
- Logistics managers must reconcile data across isolated telematics providers, carrier rate sheets, weather feeds, and regulatory checklists.
- Operational decision-making lacks an intelligent, load-bearing copilot capable of synthesizing these disparate data streams into decisive, compliant, and optimized action directives.

---

## 3. Targeted Solution Objectives

Chain Guard AI solves this challenge through an integrated, enterprise-grade operations control platform that demonstrates:

1. **Active Disruption Impact Detection:** Deterministic great-circle Haversine geospatial proximity analysis linking active disruptions to upcoming shipment routes and GPS waypoints.
2. **Explainable 0–100 Risk Scoring:** Transparent multi-factor risk indexing (disruption severity, corridor exposure, deadline pressure, cargo priority, cold-chain sensitivity).
3. **Dynamic Route & Carrier Optimization:** Intelligent ranking of alternative bypass routes and carriers evaluated on safety, transit time, cost delta, and carrier reliability.
4. **Autonomous Fleet Redeployment:** Mixed-Integer Linear Programming (MILP via Google OR-Tools / SCIP) matching idle fleet assets by proximity, payload, and refrigeration capability.
5. **IoT Cold-Chain Telemetry & Regulatory Severity Classification:** Time-series thermal stream processing classifying infractions into `NORMAL`, `WARNING`, `MAJOR`, and `CRITICAL` with automated FDA/WHO compliance audit generation.
6. **IBM Bob Operations Copilot:** Genuine, load-bearing operations copilot providing structured briefings, contextual explanations, and actionable execution directives.
