import { apiClient } from './api/client';
import { Shipment } from '../types/shipment';
import { mockShipments } from '../mock/shipmentsData';

export const shipmentService = {
  async getShipments(): Promise<Shipment[]> {
    return apiClient<Shipment[]>('/shipments', {}, mockShipments);
  },

  async getShipmentById(id: string): Promise<Shipment | null> {
    const found = mockShipments.find((s) => s.shipment_id === id) || null;
    return apiClient<Shipment | null>(`/shipments/${id}`, {}, found);
  },

  async getAtRiskShipments(): Promise<Shipment[]> {
    const atRisk = mockShipments.filter((s) => s.risk_level === 'CRITICAL' || s.risk_level === 'HIGH');
    return apiClient<Shipment[]>('/shipments/at-risk', {}, atRisk);
  },
};
