import { apiClient } from './api/client';
import { Shipment } from '../types/shipment';
import { mockShipments } from '../mock/shipmentsData';

export const shipmentService = {
  async getShipments(): Promise<Shipment[]> {
    const res = await apiClient<any>('/shipments', {}, mockShipments);
    if (Array.isArray(res)) return res;
    if (res && Array.isArray(res.shipments)) return res.shipments;
    return mockShipments;
  },

  async getShipmentById(id: string): Promise<Shipment | null> {
    const found = mockShipments.find((s) => s.shipment_id === id) || null;
    const res = await apiClient<any>(`/shipments/${id}`, {}, found);
    if (res && res.shipment) return res.shipment;
    return res || found;
  },

  async getAtRiskShipments(): Promise<Shipment[]> {
    const atRisk = mockShipments.filter((s) => s.risk_level === 'CRITICAL' || s.risk_level === 'HIGH');
    const res = await apiClient<any>('/shipments/at-risk', {}, atRisk);
    if (Array.isArray(res)) return res;
    if (res && Array.isArray(res.at_risk_shipments)) return res.at_risk_shipments;
    return atRisk;
  },
};

