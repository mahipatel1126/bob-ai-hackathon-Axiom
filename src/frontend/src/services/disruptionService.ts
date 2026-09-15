import { apiClient } from './api/client';
import { Disruption } from '../types/disruption';
import { mockDisruptions } from '../mock/disruptionsData';

export const disruptionService = {
  async getActiveDisruptions(): Promise<Disruption[]> {
    return apiClient<Disruption[]>('/disruptions/active', {}, mockDisruptions);
  },

  async getDisruptionById(id: string): Promise<Disruption | null> {
    const found = mockDisruptions.find((d) => d.disruption_id === id) || null;
    return apiClient<Disruption | null>(`/disruptions/${id}`, {}, found);
  },
};
