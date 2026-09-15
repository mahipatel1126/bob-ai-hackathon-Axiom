import { apiClient } from './api/client';
import { ColdChainTelemetry } from '../types/coldChain';
import { mockColdChainData } from '../mock/coldChainData';

export const coldChainService = {
  async getTelemetry(shipmentId: string): Promise<ColdChainTelemetry | null> {
    const data = mockColdChainData[shipmentId] || null;
    const res = await apiClient<any>(`/cold-chain/telemetry/${shipmentId}`, {}, data);
    return res || data;
  },

  async getAllAlerts(): Promise<ColdChainTelemetry[]> {
    const alerts = Object.values(mockColdChainData).filter(
      (item) => item.severity === 'CRITICAL' || item.severity === 'WARNING'
    );
    const res = await apiClient<any>('/cold-chain/alerts', {}, alerts);
    if (Array.isArray(res)) return res;
    if (res && Array.isArray(res.excursions)) return res.excursions;
    return alerts;
  },
};

