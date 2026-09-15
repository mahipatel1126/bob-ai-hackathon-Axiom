import { apiClient } from './api/client';
import { FleetAsset } from '../types/fleet';
import { mockFleetAssets } from '../mock/fleetData';

export const fleetService = {
  async getFleetAssets(): Promise<FleetAsset[]> {
    return apiClient<FleetAsset[]>('/fleet/assets', {}, mockFleetAssets);
  },

  async getRecommendedAssets(shipmentId: string): Promise<FleetAsset[]> {
    const recommended = mockFleetAssets.filter(
      (a) => a.is_recommended || a.recommended_shipment_id === shipmentId
    );
    return apiClient<FleetAsset[]>(`/fleet/recommendations?shipment_id=${shipmentId}`, {}, recommended);
  },

  async assignAsset(assetId: string, shipmentId: string): Promise<{ success: boolean; message: string }> {
    return apiClient<{ success: boolean; message: string }>(
      '/fleet/assign',
      {
        method: 'POST',
        body: JSON.stringify({ asset_id: assetId, shipment_id: shipmentId }),
      },
      {
        success: true,
        message: `Asset ${assetId} dispatched successfully to intercept ${shipmentId} at Vadodara Toll Plaza. Driver acknowledged.`,
      }
    );
  },
};
