import { apiClient } from './api/client';
import { Disruption } from '../types/disruption';
import { mockDisruptions } from '../mock/disruptionsData';

export const disruptionService = {
  async getActiveDisruptions(): Promise<Disruption[]> {
    const res = await apiClient<any>('/disruptions/active', {}, mockDisruptions);
    if (Array.isArray(res)) return res;
    if (res && Array.isArray(res.disruptions)) return res.disruptions;
    return mockDisruptions;
  },

  async getDisruptionById(id: string): Promise<Disruption | null> {
    const found = mockDisruptions.find((d) => d.disruption_id === id) || null;
    const res = await apiClient<any>(`/disruptions/${id}`, {}, found);
    if (res && res.disruption) return res.disruption;
    return res || found;
  },
};

