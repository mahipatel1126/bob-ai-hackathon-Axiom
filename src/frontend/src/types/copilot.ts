import { RiskLevel } from './shipment';

export interface StructuredRecommendation {
  priority: RiskLevel;
  shipment_id: string;
  reason: string;
  recommended_action: string;
  alternative_route?: string;
  fleet_asset_assigned?: string;
  expected_delay_saved_hours?: number;
  operational_impact?: string;
}

export interface CopilotMessage {
  id: string;
  sender: 'USER' | 'BOB';
  timestamp: string;
  content: string;
  structured_recommendation?: StructuredRecommendation;
  suggested_actions?: string[];
  is_thinking?: boolean;
}
