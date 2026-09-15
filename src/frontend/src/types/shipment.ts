export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type ShipmentStatus = 'IN_TRANSIT' | 'AT_RISK' | 'CRITICAL' | 'REROUTED' | 'DELIVERED';

export interface Shipment {
  shipment_id: string;
  origin: string;
  destination: string;
  cargo_type: string;
  cargo_value: number;
  risk_score: number; // 0 - 100
  risk_level: RiskLevel;
  delay_probability: number; // 0 - 1.0 (or percentage)
  estimated_delay_hours: number;
  recommended_action: string;
  // Operational telemetry
  current_location: string;
  carrier: string;
  eta_original: string;
  eta_revised: string;
  is_cold_chain: boolean;
  disruption_id?: string;
  status: ShipmentStatus;
  temperature_current?: number;
  temperature_min?: number;
  temperature_max?: number;
}
