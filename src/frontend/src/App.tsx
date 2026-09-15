import React, { useState } from 'react';
import { DemoProvider, useDemo } from './context/DemoContext';
import { Header } from './components/layout/Header';
import { KpiBar } from './components/layout/KpiBar';
import { DisruptionPanel } from './components/disruptions/DisruptionPanel';
import { ShipmentRiskTable } from './components/shipments/ShipmentRiskTable';
import { RouteComparison } from './components/routing/RouteComparison';
import { FleetOptimizer } from './components/fleet/FleetOptimizer';
import { ColdChainMonitor } from './components/coldchain/ColdChainMonitor';
import { BobCopilotPanel } from './components/copilot/BobCopilotPanel';
import { ShipmentDetailModal } from './components/shipments/ShipmentDetailModal';
import { Shipment } from './types/shipment';
import { AlertOctagon, ArrowRight, Activity, Terminal, Shield } from 'lucide-react';

const DashboardContent: React.FC = () => {
  const { selectedShipmentId, shipments, setCopilotOpen } = useDemo();
  const [inspectModalShipment, setInspectModalShipment] = useState<Shipment | null>(null);

  const activeShipment = shipments.find((s) => s.shipment_id === selectedShipmentId);

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-white">
      {/* 1. Header with Operational Status & Demo Stepper */}
      <Header />

      {/* Main Command Center Body */}
      <main className="flex-1 max-w-[1720px] w-full mx-auto px-4 lg:px-6 py-5 space-y-5">
        {/* 2. Executive KPI Summary Bar */}
        <KpiBar />

        {/* 3. Top Row: Active Disruptions & Alerts */}
        <section>
          <DisruptionPanel />
        </section>

        {/* 4. Shipment Risk Matrix Table */}
        <section>
          <ShipmentRiskTable onOpenDetailModal={(shipment) => setInspectModalShipment(shipment)} />
        </section>

        {/* 5. Split Section: Focused Analysis for Selected Shipment (SHP-1001) */}
        <section className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
              <h2 className="text-sm font-bold tracking-tight text-white uppercase font-mono">
                Active Incident Resolution: {selectedShipmentId}
              </h2>
              {activeShipment && (
                <span className="text-xs text-slate-400 font-sans hidden sm:inline">
                  — {activeShipment.cargo_type} ({activeShipment.origin} → {activeShipment.destination})
                </span>
              )}
            </div>
            <button
              onClick={() => setCopilotOpen(true)}
              className="text-xs font-mono font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
            >
              <span>Ask Bob to analyze this incident</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-12 gap-5">
            {/* Route Rerouting Optimization (7 Cols) */}
            <div className="xl:col-span-7">
              <RouteComparison />
            </div>

            {/* Cold Chain IoT Telemetry Monitor (5 Cols) */}
            <div className="xl:col-span-5">
              <ColdChainMonitor />
            </div>
          </div>
        </section>

        {/* 6. Fleet Utilisation & Autonomous Asset Redeployment */}
        <section>
          <FleetOptimizer />
        </section>
      </main>

      {/* Operations Center Status Footer */}
      <footer className="border-t border-slate-800/80 bg-[#080d1a] py-3 px-4 lg:px-6 text-xs text-slate-500 font-mono flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-slate-400">
            <Shield className="w-3.5 h-3.5 text-cyan-400" />
            <span>ChainGuard AI v1.0</span>
          </span>
          <span>•</span>
          <span>PERSON 3: Frontend + UI Command Center</span>
          <span>•</span>
          <span className="text-emerald-400 font-medium">Demo Mode Active (Clean API Abstraction Layer)</span>
        </div>
        <div className="flex items-center gap-3">
          <span>Target Endpoints: /api/disruptions, /api/shipments, /api/routing, /api/fleet, /api/cold-chain, /api/copilot</span>
        </div>
      </footer>

      {/* Modals and Sidebars */}
      <ShipmentDetailModal
        shipment={inspectModalShipment}
        onClose={() => setInspectModalShipment(null)}
      />

      <BobCopilotPanel />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <DemoProvider>
      <DashboardContent />
    </DemoProvider>
  );
};

export default App;
