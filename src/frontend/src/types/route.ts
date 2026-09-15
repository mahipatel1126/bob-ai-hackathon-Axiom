export interface RouteWaypoint {
  name: string;
  lat?: number;
  lng?: number;
  status: 'CLEARED' | 'BOTTLENECK' | 'DIVERT_POINT' | 'DESTINATION' | 'ORIGIN';
  description?: string;
}

export interface RouteDetail {
  name: string;
  corridor: string;
  waypoints: RouteWaypoint[];
  distance_km: number;
  est_transit_hours: number;
  bottleneck_point?: string;
  toll_cost_usd: number;
}

export interface RouteRecommendation {
  shipment_id: string;
  current_route: RouteDetail;
  recommended_route: RouteDetail;
  alternative_carrier: string;
  original_carrier: string;
  estimated_delay_hours: number;
  hours_saved: number;
  estimated_cost: number;
  cost_delta: number;
  reason: string;
  risk_reduction_percent: number;
  approved?: boolean;
}
