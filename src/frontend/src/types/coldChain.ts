export type ColdChainSeverity = 'NORMAL' | 'WARNING' | 'HIGH' | 'CRITICAL';

export interface TelemetryPoint {
  timestamp: string;
  time_label: string;
  temp: number;
  ambient_temp: number;
  status: 'NORMAL' | 'WARNING' | 'EXCURSION';
}

export interface ColdChainTelemetry {
  shipment_id: string;
  cargo_description: string;
  sensor_id: string;
  temperature: number; // Current reading
  allowed_min: number; // e.g. 2.0°C
  allowed_max: number; // e.g. 8.0°C
  excursion_minutes: number;
  peak_temperature: number;
  severity: ColdChainSeverity;
  action: string;
  time_to_critical_hours: number;
  reefer_unit_status: 'FAILED' | 'DEGRADED' | 'OPERATIONAL' | 'STANDBY';
  telemetry_history: TelemetryPoint[];
  battery_level_percent: number;
  last_ping: string;
}
