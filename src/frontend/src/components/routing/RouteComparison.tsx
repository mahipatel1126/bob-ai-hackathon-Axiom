import React from 'react';
import { RouteSchematicMap } from './RouteSchematicMap';
import { useDemo } from '../../context/DemoContext';
import { Navigation, Clock, DollarSign, ArrowRight, ShieldCheck, AlertTriangle, CheckCircle2, ChevronRight, Truck } from 'lucide-react';

export const RouteComparison: React.FC = () => {
  const { routeRecommendation, selectedShipmentId, rerouteApproved, approveReroute } = useDemo();

  if (!routeRecommendation) {
    return (
      <div className="bg-[#0c1324] border border-slate-800 rounded-xl p-6 text-center">
        <Navigation className="w-8 h-8 text-slate-400 mx-auto mb-2" />
        <p className="text-xs text-slate-300">
          Select an at-risk shipment to inspect dynamic reroute optimization.
        </p>
      </div>
    );
  }

  const { current_route, recommended_route, alternative_carrier, original_carrier, estimated_delay_hours, hours_saved, estimated_cost, cost_delta, reason } = routeRecommendation;

  return (
    <div className="bg-[#0c1324] border border-slate-800 rounded-xl overflow-hidden flex flex-col space-y-4 p-4 lg:p-5">
      {/* Header with Title and Approval Status */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
            <Navigation className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-tight text-white uppercase font-mono">
                Dynamic Reroute & Alternative Carrier Recommendation
              </h2>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                {selectedShipmentId}
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">
              Automated multi-factor corridor analysis evaluating delay risk, cold-storage availability, and cost.
            </p>
          </div>
        </div>

        {/* Action Button */}
        <div>
          {rerouteApproved ? (
            <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-mono font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>REROUTE AUTHORIZED</span>
            </div>
          ) : (
            <button
              onClick={approveReroute}
              className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
            >
              <span>Authorize Hazira Reroute</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Schematic Map Visualization */}
      <RouteSchematicMap routeData={routeRecommendation} shipmentId={selectedShipmentId} />

      {/* 3-Column Tactical Comparison Matrix: Current Route -> Disruption -> Recommended Alternative */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
        {/* Box 1: CURRENT ROUTE */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs font-mono mb-2">
              <span className="text-slate-400 uppercase font-semibold">1. Current Scheduled Route</span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-red-500/20 text-red-300 font-bold">BLOCKED</span>
            </div>
            <h3 className="text-xs font-bold text-white font-mono">{current_route.name}</h3>
            <div className="space-y-1.5 mt-3 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Carrier:</span>
                <span className="text-slate-200 font-mono font-medium">{original_carrier}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Distance:</span>
                <span className="text-slate-200 font-mono">{current_route.distance_km} km</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Expected Delay:</span>
                <span className="text-red-400 font-mono font-bold">+42.0 hours</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Corridor:</span>
                <span className="text-slate-200 font-mono">{current_route.corridor}</span>
              </div>
            </div>
          </div>
          <div className="mt-3 pt-2.5 border-t border-slate-800 text-[11px] text-red-300/90 font-medium">
            Bottleneck: {current_route.bottleneck_point}
          </div>
        </div>

        {/* Box 2: DISRUPTION IMPACT BOTTLENECK */}
        <div className="bg-red-950/20 border border-red-500/40 rounded-xl p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs font-mono mb-2">
              <span className="text-red-400 uppercase font-semibold">2. Disruption Bottleneck</span>
              <AlertTriangle className="w-4 h-4 text-red-400 animate-pulse" />
            </div>
            <h3 className="text-xs font-bold text-red-200 font-mono">JNPT Port Terminal Dock Strike</h3>
            <p className="text-xs text-slate-300 mt-2 leading-relaxed">
              Berths 2-5 are non-operational. Over 3,800 containers stranded. Trucks queued along NH348 face severe demurrage, extreme heat exposure, and lack of reefer charging outlets.
            </p>
          </div>
          <div className="mt-3 pt-2.5 border-t border-red-500/20 text-xs font-mono text-red-300 flex items-center justify-between">
            <span>SPOILAGE RISK:</span>
            <span className="font-bold">CRITICAL (1.8h window)</span>
          </div>
        </div>

        {/* Box 3: RECOMMENDED ROUTE & ALTERNATIVE CARRIER */}
        <div className="bg-gradient-to-br from-emerald-950/30 to-slate-900/80 border border-emerald-500/50 rounded-xl p-4 flex flex-col justify-between shadow-[0_0_15px_rgba(16,185,129,0.1)]">
          <div>
            <div className="flex items-center justify-between text-xs font-mono mb-2">
              <span className="text-emerald-400 uppercase font-semibold">3. Recommended Alternative</span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/40">OPTIMIZED</span>
            </div>
            <h3 className="text-xs font-bold text-white font-mono">{recommended_route.name}</h3>
            <div className="space-y-1.5 mt-3 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Alternative Carrier:</span>
                <span className="text-cyan-300 font-mono font-bold">{alternative_carrier}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Distance:</span>
                <span className="text-slate-200 font-mono">{recommended_route.distance_km} km (-250 km)</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Revised Delay:</span>
                <span className="text-emerald-400 font-mono font-bold">+{estimated_delay_hours}h (-{hours_saved}h saved)</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Est. Cost:</span>
                <span className="text-slate-200 font-mono">${estimated_cost} (+${cost_delta} delta)</span>
              </div>
            </div>
          </div>
          <div className="mt-3 pt-2.5 border-t border-emerald-500/20 text-xs font-mono text-emerald-300 flex items-center justify-between">
            <span>RISK REDUCTION:</span>
            <span className="font-bold">{routeRecommendation.risk_reduction_percent}% MITIGATED</span>
          </div>
        </div>
      </div>

      {/* Reason for Recommendation */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-3.5 text-xs">
        <span className="font-mono text-slate-400 uppercase font-semibold block mb-1">
          OPERATIONAL JUSTIFICATION
        </span>
        <p className="text-slate-200 leading-relaxed font-sans">
          {reason}
        </p>
      </div>
    </div>
  );
};
