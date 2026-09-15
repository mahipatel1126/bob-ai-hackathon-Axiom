export type FleetAssetStatus = 'IDLE' | 'IN_TRANSIT' | 'MAINTENANCE' | 'ASSIGNED';
export type FleetAvailability = 'IMMEDIATE' | 'WITHIN_2_HOURS' | 'SCHEDULED' | 'UNAVAILABLE';

export interface FleetAsset {
  asset_id: string;
  asset_type: string;
  location: string;
  status: FleetAssetStatus;
  available_capacity: string; // e.g., "18 ton"
  capacity_tons: number;
  temperature_capable: boolean;
  temp_range_min?: number;
  temp_range_max?: number;
  availability: FleetAvailability;
  is_recommended?: boolean;
  recommended_assignment?: string;
  recommended_shipment_id?: string;
  recommendation_reason?: string;
  compatibility_score?: number; // 0 - 100
  driver_name?: string;
  current_fuel_percent?: number;
  eta_to_rendezvous_hours?: number;
}
