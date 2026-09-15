export interface KPIStats {
  active_disruptions: number;
  at_risk_shipments: number;
  critical_shipments: number;
  fleet_utilisation_percent: number;
  cold_chain_alerts: number;
  total_shipments_monitored: number;
  total_fleet_assets: number;
  idle_fleet_assets: number;
  reefer_assets_available: number;
  avg_delay_mitigation_hours: number;
}
