import { apiClient } from './api/client';
import { ColdChainTelemetry } from '../types/coldChain';
import { mockColdChainData } from '../mock/coldChainData';

export const coldChainService = {
  async getTelemetry(shipmentId: string): Promise<ColdChainTelemetry | null> {
    const data = mockColdChainData[shipmentId] || null;
    return apiClient<ColdChainTelemetry | null>(`/cold-chain/telemetry/${shipmentId}`, {}, data);
  },

  async getAllAlerts(): Promise<ColdChainTelemetry[]> {
    const alerts = Object.values(mockColdChainData).filter(
      (item) => item.severity === 'CRITICAL' || item.severity === 'WARNING'
    );
    return apiClient<ColdChainTelemetry[]>('/cold-chain/alerts', {}, alerts);
  },
};
