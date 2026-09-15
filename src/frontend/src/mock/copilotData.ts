import { CopilotMessage } from '../types/copilot';

export const presetCopilotQueries: { query: string; response: CopilotMessage }[] = [
  {
    query: 'Why is SHP-1001 critical?',
    response: {
      id: 'bob-resp-1',
      sender: 'BOB',
      timestamp: 'Just now',
      content: 'Shipment SHP-1001 is at immediate risk of total cargo loss ($420,000 value). It is experiencing a dual-hazard failure: IoT sensors confirm an ongoing cold-chain temperature excursion (10.4°C vs 8.0°C maximum threshold for 42 minutes) due to degraded reefer refrigeration, while its primary destination (JNPT Port) is gridlocked by an indefinite dockworker strike (+42 hour queue).',
      structured_recommendation: {
        priority: 'CRITICAL',
        shipment_id: 'SHP-1001',
        reason: 'Temperature excursion (10.4°C > 8.0°C limit) compounded by JNPT Port strike gridlock',
        recommended_action: 'Authorize immediate rendezvous at Vadodara with idle refrigerated TRUCK-204 and divert to Hazira Adani Port.',
        alternative_route: 'Adani Hazira CFS Terminal via SH-6 (285 km, 5.2h)',
        fleet_asset_assigned: 'TRUCK-204 (18T Dual-Temp Reefer, Ahmedabad Hub)',
        expected_delay_saved_hours: 37.5,
        operational_impact: 'Eliminates 37.5h delay, preserves 100% vaccine viability, prevents $420k loss.',
      },
      suggested_actions: [
        'Dispatch TRUCK-204 to Vadodara Toll Plaza',
        'Issue Route Divert Order to Hazira Port',
        'Notify ColdExpress Logistics Lead',
      ],
    },
  },
  {
    query: 'Which shipments are most at risk?',
    response: {
      id: 'bob-resp-2',
      sender: 'BOB',
      timestamp: 'Just now',
      content: 'Based on multi-factor risk inference (disruption proximity, cargo perishability, contract SLA penalty), 5 shipments are affected by the Mumbai JNPT Port Strike. Highest priority is SHP-1001 (Risk Score: 96/100, CRITICAL), followed by SHP-1004 (Auto ECUs, Risk 82) and SHP-1015 (Pharma API, Risk 81).',
      structured_recommendation: {
        priority: 'CRITICAL',
        shipment_id: 'SHP-1001',
        reason: 'Perishable pharma biologics trapped on congested NH48 corridor',
        recommended_action: 'Prioritize intervention on SHP-1001 immediately before reefer failure breaches irreversible 12°C ceiling.',
        operational_impact: 'Intervention protects highest-value and highest-liability asset in transit.',
      },
      suggested_actions: [
        'Inspect SHP-1001 telemetry',
        'Hold SHP-1004 at Talegaon ICD',
        'Review fleet availability',
      ],
    },
  },
  {
    query: 'How should we respond to the current disruption?',
    response: {
      id: 'bob-resp-3',
      sender: 'BOB',
      timestamp: 'Just now',
      content: 'JNPT Port (Nhava Sheva) dock strike has paralyzed Berths 2 through 5 with an estimated 72-hour operational outage. Recommending a two-pronged operational strategy: 1) Active dynamic rerouting of all perishable and high-priority cargo to Adani Hazira Container Terminal; 2) Staging non-perishable freight (Auto ECUs & Textiles) at inland dry ports (Talegaon ICD) to avoid highway demurrage.',
      structured_recommendation: {
        priority: 'HIGH',
        shipment_id: 'CORRIDOR-WEST',
        reason: 'Indefinite dockworker strike at primary container gateway',
        recommended_action: 'Activate Secondary Maritime Gateway Protocol: Divert Gujarat & North corridor freight to Hazira Port.',
        operational_impact: 'Mitigates an aggregate of 180+ hours in vehicle demurrage across active fleet.',
      },
      suggested_actions: [
        'Execute Hazira Gateway Diversion Protocol',
        'Notify Maritime Customs Brokers',
        'Deploy idle reefer assets',
      ],
    },
  },
  {
    query: 'Which idle fleet assets should we redeploy?',
    response: {
      id: 'bob-resp-4',
      sender: 'BOB',
      timestamp: 'Just now',
      content: 'Optimizer matched TRUCK-204 (18-ton Heavy Rigid Reefer) currently IDLE at the Ahmedabad Logistics Hub. It has pre-chilled dual compressors operating at 4.0°C and a qualified L3 cold-chain driver on standby. It is positioned only 74 km from the Vadodara Expressway intercept point.',
      structured_recommendation: {
        priority: 'HIGH',
        shipment_id: 'SHP-1001',
        reason: 'Optimal proximity, temperature capability (-25°C to 15°C), and immediate availability',
        recommended_action: 'Dispatch TRUCK-204 to rendezvous with SHP-1001 at Vadodara Toll Plaza for transshipment.',
        fleet_asset_assigned: 'TRUCK-204',
        expected_delay_saved_hours: 37.5,
        operational_impact: 'Resolves active temperature excursion within 72 minutes of arrival.',
      },
      suggested_actions: [
        'Confirm TRUCK-204 Dispatch Order',
        'Send GPS Rendezvous to Driver Rajesh Sharma',
      ],
    },
  },
  {
    query: 'Is any cold-chain shipment in danger?',
    response: {
      id: 'bob-resp-5',
      sender: 'BOB',
      timestamp: 'Just now',
      content: 'ALERT: SHP-1001 (Covax-Bio Vaccine Vials) is currently in CRITICAL EXCURSION. IoT sensor IOT-TEMP-GUJ-9021 reports 10.4°C (Safe limit: 2.0°C - 8.0°C) with peak temperature reaching 11.1°C. Excursion has persisted for 42 minutes with an estimated 1.8 hours remaining before irreversible spoilage occurs.',
      structured_recommendation: {
        priority: 'CRITICAL',
        shipment_id: 'SHP-1001',
        reason: 'Thermal excursion exceeding 8.0°C regulatory envelope',
        recommended_action: 'Immediate transshipment to backup reefer TRUCK-204 at Vadodara Interchange.',
        fleet_asset_assigned: 'TRUCK-204',
        operational_impact: 'Prevents total degradation of 25,000 vaccine doses.',
      },
      suggested_actions: [
        'View Live Cold-Chain Telemetry Graph',
        'Initiate Emergency Transshipment Protocol',
      ],
    },
  },
  {
    query: "What's the recommended route for SHP-1001?",
    response: {
      id: 'bob-resp-6',
      sender: 'BOB',
      timestamp: 'Just now',
      content: 'The optimal rerouting corridor diverts SHP-1001 off the NH48 Golden Quadrilateral at Bharuch onto State Highway 6 directly to the Hazira Adani Port Container Terminal. Distance is 285 km (transit time 5.2 hours) compared to 535 km (+42 hour strike backlog) via the original JNPT route.',
      structured_recommendation: {
        priority: 'CRITICAL',
        shipment_id: 'SHP-1001',
        reason: 'JNPT Port entrance blocked; Hazira Port offers immediate berths & cold storage',
        recommended_action: 'Approve Hazira Dynamic Divert via BlueDart ColdExpress Maritime Feeder.',
        alternative_route: 'Adani Hazira CFS Terminal (285 km)',
        expected_delay_saved_hours: 37.5,
        operational_impact: 'Reduces delay from +42h to +4.5h, saving 37.5 hours and preserving cargo.',
      },
      suggested_actions: [
        'Approve Route Change',
        'Send Turn-by-Turn Waypoints to Vehicle GPS',
      ],
    },
  },
];
