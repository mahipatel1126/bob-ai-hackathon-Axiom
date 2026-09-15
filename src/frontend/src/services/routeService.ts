import { apiClient } from './api/client';
import { RouteRecommendation } from '../types/route';
import { mockRouteRecommendations } from '../mock/routeData';

export const routeService = {
  async getRouteRecommendation(shipmentId: string): Promise<RouteRecommendation | null> {
    const data = mockRouteRecommendations[shipmentId] || null;
    return apiClient<RouteRecommendation | null>(`/routing/recommendations/${shipmentId}`, {}, data);
  },

  async approveReroute(shipmentId: string): Promise<{ success: boolean; message: string }> {
    return apiClient<{ success: boolean; message: string }>(
      `/routing/approve/${shipmentId}`,
      { method: 'POST' },
      {
        success: true,
        message: `Reroute for ${shipmentId} approved. Dynamic dispatch issued to BlueDart ColdExpress for Adani Hazira Port entry.`,
      }
    );
  },
};
