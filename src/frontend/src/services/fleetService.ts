import { apiClient } from './api/client';
import { FleetAsset } from '../types/fleet';
import { mockFleetAssets } from '../mock/fleetData';

export const fleetService = {
  async getFleetAssets(): Promise<FleetAsset[]> {
    const res = await apiClient<any>('/fleet/assets', {}, mockFleetAssets);
    if (Array.isArray(res)) return res;
    if (res && Array.isArray(res.assets)) return res.assets;
    return mockFleetAssets;
  },

  async getRecommendedAssets(shipmentId: string): Promise<FleetAsset[]> {
    const recommended = mockFleetAssets.filter(
      (a) => a.is_recommended || a.recommended_shipment_id === shipmentId
    );
    const res = await apiClient<any>(`/fleet/recommendations?shipment_id=${shipmentId}`, {}, recommended);
    if (Array.isArray(res)) return res;
    if (res && Array.isArray(res.candidates)) return res.candidates;
    return recommended;
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

