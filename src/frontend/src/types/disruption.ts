export type DisruptionSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type DisruptionStatus = 'ACTIVE' | 'MONITORING' | 'RESOLVED';

export interface Disruption {
  disruption_id: string;
  type: string;
  location: string;
  severity: DisruptionSeverity;
  start_time: string;
  expected_duration_hours: number;
  affected_shipments_count: number;
  affected_shipment_ids: string[];
  description: string;
  status: DisruptionStatus;
  is_simulated: boolean;
  impact_radius_km?: number;
  reported_source?: string;
}
