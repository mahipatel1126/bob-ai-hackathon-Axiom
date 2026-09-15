import { apiClient } from './api/client';
import { CopilotMessage } from '../types/copilot';
import { presetCopilotQueries } from '../mock/copilotData';

export const copilotService = {
  async askBob(query: string, contextShipmentId?: string): Promise<CopilotMessage> {
    // Search preset matching queries
    const match = presetCopilotQueries.find(
      (item) => item.query.toLowerCase().trim() === query.toLowerCase().trim()
    );

    let fallbackResponse: CopilotMessage;

    if (match) {
      fallbackResponse = match.response;
    } else {
      // Dynamic fallback response based on keywords
      const lower = query.toLowerCase();
      if (lower.includes('shp-1001') || lower.includes('vaccine') || lower.includes('cold')) {
        fallbackResponse = presetCopilotQueries[0].response;
      } else if (lower.includes('truck') || lower.includes('fleet') || lower.includes('redeploy') || lower.includes('asset')) {
        fallbackResponse = presetCopilotQueries[3].response;
      } else if (lower.includes('route') || lower.includes('reroute') || lower.includes('hazira')) {
        fallbackResponse = presetCopilotQueries[5].response;
      } else if (lower.includes('mumbai') || lower.includes('port') || lower.includes('strike') || lower.includes('disruption')) {
        fallbackResponse = presetCopilotQueries[2].response;
      } else {
        fallbackResponse = {
          id: `bob-${Date.now()}`,
          sender: 'BOB',
          timestamp: 'Just now',
          content: `ChainGuard Operations Copilot analyzed your inquiry regarding "${query}". The system is currently prioritizing the JNPT Mumbai Port Strike and temperature excursion on SHP-1001. Recommended action is immediate reroute to Hazira Port and dispatching TRUCK-204 from Ahmedabad.`,
          structured_recommendation: {
            priority: 'HIGH',
            shipment_id: contextShipmentId || 'SHP-1001',
            reason: 'Active supply chain disruption in Western Transit Corridor',
            recommended_action: 'Review recommended route and authorize fleet redeployment in the command center.',
            operational_impact: 'Prevents demurrage delays and mitigates perishable cargo spoilage risk.',
          },
          suggested_actions: [
            'Inspect SHP-1001 Details',
            'View Route Comparison',
            'Redeploy TRUCK-204',
          ],
        };
      }
    }

    return apiClient<CopilotMessage>(
      '/copilot/query',
      {
        method: 'POST',
        body: JSON.stringify({ query, context_shipment_id: contextShipmentId }),
      },
      fallbackResponse
    );
  },
};
