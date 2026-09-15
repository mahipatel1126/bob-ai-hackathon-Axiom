import { Disruption } from '../types/disruption';

export const mockDisruptions: Disruption[] = [
  {
    disruption_id: 'DIS-2026-MUMBAI-01',
    type: 'Port Terminal Strike & Container Congestion',
    location: 'JNPT Port (Nhava Sheva), Navi Mumbai',
    severity: 'CRITICAL',
    start_time: '2026-09-14T06:00:00Z',
    expected_duration_hours: 72,
    affected_shipments_count: 5,
    affected_shipment_ids: ['SHP-1001', 'SHP-1004', 'SHP-1007', 'SHP-1012', 'SHP-1015'],
    description: 'Indefinite dockworker strike and crane operator walkout at Jawaharlal Nehru Port Trust (JNPT). Marine berths 2-5 blocked with over 48h container backlogs. Access highway NH348 heavily stalled.',
    status: 'ACTIVE',
    is_simulated: true,
    impact_radius_km: 55,
    reported_source: 'JNPT Port Operations Feed (Simulated Event)',
  },
  {
    disruption_id: 'DIS-2026-DELHI-02',
    type: 'Monsoon Flash Flooding & Highway Closure',
    location: 'NH44 Corridor, Sonipat Bypass, Haryana',
    severity: 'MEDIUM',
    start_time: '2026-09-14T14:30:00Z',
    expected_duration_hours: 18,
    affected_shipments_count: 2,
    affected_shipment_ids: ['SHP-1009', 'SHP-1022'],
    description: 'Heavy rainfall runoff caused waterlogging on lanes 1-3. Commercial freight diverted through Western Peripheral Expressway with +3.5h delay.',
    status: 'MONITORING',
    is_simulated: true,
    impact_radius_km: 25,
    reported_source: 'National Highway Authority Telemetry (Simulated)',
  },
];
