import React, { createContext, useContext, useState } from 'react';
import { Shipment } from '../types/shipment';
import { Disruption } from '../types/disruption';
import { FleetAsset } from '../types/fleet';
import { RouteRecommendation } from '../types/route';
import { ColdChainTelemetry } from '../types/coldChain';
import { mockShipments } from '../mock/shipmentsData';
import { mockDisruptions } from '../mock/disruptionsData';
import { mockFleetAssets } from '../mock/fleetData';
import { mockRouteRecommendations } from '../mock/routeData';
import { mockColdChainData } from '../mock/coldChainData';

export type DemoStep = 1 | 2 | 3 | 4 | 5 | 6;

export interface DemoStepInfo {
  step: DemoStep;
  label: string;
  shortDesc: string;
}

export const DEMO_STEPS: DemoStepInfo[] = [
  { step: 1, label: 'Normal Baseline', shortDesc: 'Baseline supply chain monitoring' },
  { step: 2, label: 'Disruption Event', shortDesc: 'Mumbai JNPT Port strike breaks out' },
  { step: 3, label: 'At-Risk Isolation', shortDesc: 'SHP-1001 flagged with IoT thermal excursion' },
  { step: 4, label: 'Route Divert', shortDesc: 'Alternate corridor to Hazira Port generated' },
  { step: 5, label: 'Fleet Redeploy', shortDesc: 'TRUCK-204 idle reefer matched for rendezvous' },
  { step: 6, label: 'Copilot Decision', shortDesc: 'IBM Bob synthesizes final operational action' },
];

interface DemoContextType {
  currentStep: DemoStep;
  setStep: (step: DemoStep) => void;
  nextStep: () => void;
  prevStep: () => void;
  resetDemo: () => void;
  selectedShipmentId: string;
  setSelectedShipmentId: (id: string) => void;
  activeDisruptions: Disruption[];
  shipments: Shipment[];
  fleetAssets: FleetAsset[];
  routeRecommendation: RouteRecommendation | null;
  coldChainData: ColdChainTelemetry | null;
  rerouteApproved: boolean;
  assetAssigned: boolean;
  approveReroute: () => void;
  assignFleetAsset: () => void;
  copilotOpen: boolean;
  setCopilotOpen: (open: boolean) => void;
}

const DemoContext = createContext<DemoContextType | undefined>(undefined);

export const DemoProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentStep, setCurrentStep] = useState<DemoStep>(2); // Default to Step 2 (Active disruption) for immediate impact
  const [selectedShipmentId, setSelectedShipmentId] = useState<string>('SHP-1001');
  const [rerouteApproved, setRerouteApproved] = useState<boolean>(false);
  const [assetAssigned, setAssetAssigned] = useState<boolean>(false);
  const [copilotOpen, setCopilotOpen] = useState<boolean>(false);

  const setStep = (step: DemoStep) => {
    setCurrentStep(step);
    if (step >= 3) {
      setSelectedShipmentId('SHP-1001');
    }
    if (step >= 6) {
      setCopilotOpen(true);
    }
  };

  const nextStep = () => {
    if (currentStep < 6) {
      setStep((currentStep + 1) as DemoStep);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setStep((currentStep - 1) as DemoStep);
    }
  };

  const resetDemo = () => {
    setCurrentStep(1);
    setSelectedShipmentId('SHP-1001');
    setRerouteApproved(false);
    setAssetAssigned(false);
    setCopilotOpen(false);
  };

  const approveReroute = () => {
    setRerouteApproved(true);
  };

  const assignFleetAsset = () => {
    setAssetAssigned(true);
  };

  // Derive state according to demo step
  const activeDisruptions = currentStep === 1 ? [] : mockDisruptions;

  const shipments = currentStep === 1
    ? mockShipments.map((s) => ({
        ...s,
        risk_level: 'LOW' as const,
        risk_score: 18,
        delay_probability: 0.05,
        estimated_delay_hours: 0.2,
        status: 'IN_TRANSIT' as const,
        recommended_action: 'Nominal corridor transit.',
        temperature_current: s.is_cold_chain ? 4.5 : undefined,
      }))
    : mockShipments.map((s) => {
        if (s.shipment_id === 'SHP-1001' && rerouteApproved && assetAssigned) {
          return {
            ...s,
            status: 'REROUTED' as const,
            risk_level: 'LOW' as const,
            risk_score: 22,
            delay_probability: 0.1,
            estimated_delay_hours: 4.5,
            recommended_action: 'Rerouted to Hazira Port with TRUCK-204 reefer backup.',
          };
        }
        return s;
      });

  const fleetAssets = mockFleetAssets.map((asset) => {
    if (asset.asset_id === 'TRUCK-204' && assetAssigned) {
      return {
        ...asset,
        status: 'ASSIGNED' as const,
        recommended_assignment: 'DISPATCHED: Rendezvous en route to Vadodara Toll Plaza',
      };
    }
    return asset;
  });

  const routeRecommendation = mockRouteRecommendations[selectedShipmentId] || null;
  const coldChainData = mockColdChainData[selectedShipmentId] || null;

  return (
    <DemoContext.Provider
      value={{
        currentStep,
        setStep,
        nextStep,
        prevStep,
        resetDemo,
        selectedShipmentId,
        setSelectedShipmentId,
        activeDisruptions,
        shipments,
        fleetAssets,
        routeRecommendation,
        coldChainData,
        rerouteApproved,
        assetAssigned,
        approveReroute,
        assignFleetAsset,
        copilotOpen,
        setCopilotOpen,
      }}
    >
      {children}
    </DemoContext.Provider>
  );
};

export const useDemo = () => {
  const context = useContext(DemoContext);
  if (!context) {
    throw new Error('useDemo must be used within a DemoProvider');
  }
  return context;
};
