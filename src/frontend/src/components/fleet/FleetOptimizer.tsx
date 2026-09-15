import React from 'react';
import { Truck, Snowflake, CheckCircle2, AlertCircle, MapPin, Gauge, Fuel, Zap, ArrowUpRight } from 'lucide-react';
import { useDemo } from '../../context/DemoContext';
import { FleetAsset } from '../../types/fleet';

export const FleetOptimizer: React.FC = () => {
  const { fleetAssets, selectedShipmentId, assetAssigned, assignFleetAsset } = useDemo();

  const idleAssets = fleetAssets.filter((a) => a.status === 'IDLE');
  const inTransitAssets = fleetAssets.filter((a) => a.status === 'IN_TRANSIT');
  const maintenanceAssets = fleetAssets.filter((a) => a.status === 'MAINTENANCE');
  const assignedAssets = fleetAssets.filter((a) => a.status === 'ASSIGNED');

  return (
    <div className="bg-[#0c1324] border border-slate-800 rounded-xl overflow-hidden p-4 lg:p-5 flex flex-col space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-blue-500/10 text-cyan-400 border border-blue-500/30">
            <Truck className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-tight text-white uppercase font-mono">
                Fleet Utilisation & Dynamic Redeployment Engine
              </h2>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                {fleetAssets.length} TOTAL ASSETS
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">
              Autonomous asset-cargo matching based on thermal compatibility, payload capacity, and intercept ETA.
            </p>
          </div>
        </div>

        {/* Fleet Distribution Summary */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="px-2.5 py-1 rounded bg-slate-800 text-slate-300">
            {idleAssets.length} Idle
          </span>
          <span className="px-2.5 py-1 rounded bg-blue-950/60 text-blue-300 border border-blue-800/60">
            {inTransitAssets.length} En Route
          </span>
          {assignedAssets.length > 0 && (
            <span className="px-2.5 py-1 rounded bg-emerald-950 text-emerald-300 border border-emerald-700">
              {assignedAssets.length} Redeployed
            </span>
          )}
          <span className="px-2.5 py-1 rounded bg-amber-950/60 text-amber-300 border border-amber-800/60">
            {maintenanceAssets.length} Maint
          </span>
        </div>
      </div>

      {/* Highlighted Recommended Asset: TRUCK-204 */}
      {fleetAssets
        .filter((a) => a.is_recommended)
        .map((asset) => {
          return (
            <div
              key={asset.asset_id}
              className={`rounded-xl border p-4.5 transition-all ${
                assetAssigned
                  ? 'bg-gradient-to-r from-emerald-950/30 via-[#0d172a] to-[#0d172a] border-emerald-500/60 shadow-[0_0_20px_rgba(16,185,129,0.15)]'
                  : 'bg-gradient-to-r from-cyan-950/30 via-[#0d172a] to-[#0d172a] border-cyan-500/60 shadow-[0_0_20px_rgba(6,182,212,0.15)]'
              }`}
            >
              <div className="flex flex-wrap items-start justify-between gap-3 pb-3 border-b border-slate-800/80">
                <div className="flex items-start gap-3">
                  <div className={`p-2.5 rounded-xl ${
                    assetAssigned ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
                  }`}>
                    <Zap className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-base font-bold font-mono text-white">
                        {asset.asset_id}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 uppercase">
                        AI Matched (98% Compatibility)
                      </span>
                      {asset.temperature_capable && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30 flex items-center gap-1">
                          <Snowflake className="w-3 h-3" />
                          DUAL-TEMP REEFER
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-300 mt-1 font-medium">
                      {asset.asset_type}
                    </div>
                  </div>
                </div>

                {/* Dispatch Trigger Button */}
                <div>
                  {assetAssigned ? (
                    <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-mono font-bold">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span>DISPATCHED TO VADODARA</span>
                    </div>
                  ) : (
                    <button
                      onClick={assignFleetAsset}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs transition-all shadow-[0_0_15px_rgba(16,185,129,0.3)]"
                    >
                      <Truck className="w-4 h-4" />
                      <span>Deploy TRUCK-204 to {selectedShipmentId}</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Asset Telemetry & Status Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3 text-xs font-mono">
                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">CURRENT LOCATION</span>
                  <span className="text-slate-200 font-sans font-medium flex items-center gap-1 mt-0.5">
                    <MapPin className="w-3 h-3 text-cyan-400" />
                    Ahmedabad Hub (Sanand)
                  </span>
                </div>
                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">AVAILABLE CAPACITY</span>
                  <span className="text-slate-200 font-bold mt-0.5 block">{asset.available_capacity} (Payload Match)</span>
                </div>
                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">THERMAL ENVELOPE</span>
                  <span className="text-cyan-400 font-bold mt-0.5 block">-25.0°C to +15.0°C</span>
                </div>
                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">INTERCEPT ETA</span>
                  <span className="text-emerald-400 font-bold mt-0.5 block">{asset.eta_to_rendezvous_hours}h to Vadodara</span>
                </div>
              </div>

              {/* Operational Recommendation Reason */}
              <div className="mt-3 bg-slate-900/60 p-3 rounded-lg border border-slate-800 text-xs">
                <div className="flex items-center gap-1.5 text-cyan-400 font-mono font-semibold text-[11px] mb-1">
                  <Gauge className="w-3.5 h-3.5" />
                  OPERATIONAL REDEPLOYMENT RATIONALE
                </div>
                <p className="text-slate-200 leading-relaxed font-sans">
                  {asset.recommendation_reason}
                </p>
                <div className="mt-2 pt-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-[11px] text-slate-300 font-mono">
                  <span>Assigned Driver: {asset.driver_name}</span>
                  <span>Fuel: {asset.current_fuel_percent}% • Compressor: Standby Active at 4.0°C</span>
                </div>
              </div>
            </div>
          );
        })}

      {/* Complete Fleet Availability List */}
      <div>
        <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-2.5">
          Other Fleet Assets in Western Regional Corridor
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
          {fleetAssets
            .filter((a) => !a.is_recommended)
            .map((asset) => {
              const isIdle = asset.status === 'IDLE';
              return (
                <div
                  key={asset.asset_id}
                  className="bg-slate-900/50 border border-slate-800/90 rounded-lg p-3 flex items-start justify-between gap-3 text-xs"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-slate-200">{asset.asset_id}</span>
                      <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono font-semibold ${
                        isIdle ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400'
                      }`}>
                        {asset.status}
                      </span>
                      {asset.temperature_capable ? (
                        <span className="text-[10px] font-mono text-cyan-400 flex items-center gap-0.5">
                          <Snowflake className="w-2.5 h-2.5" /> Reefer
                        </span>
                      ) : (
                        <span className="text-[10px] font-mono text-slate-400">Dry Van</span>
                      )}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1 font-sans">{asset.asset_type}</div>
                    <div className="text-[11px] text-slate-300 font-mono mt-0.5 flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-slate-400" />
                      {asset.location}
                    </div>
                  </div>

                  <div className="text-right shrink-0">
                    <span className="font-mono text-slate-300 font-bold">{asset.available_capacity}</span>
                    <div className="text-[10px] text-slate-400 mt-1 font-mono">
                      Score: {asset.compatibility_score}%
                    </div>
                  </div>
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
};
