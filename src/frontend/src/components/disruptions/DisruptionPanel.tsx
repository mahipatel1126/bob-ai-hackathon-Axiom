import React from 'react';
import { AlertTriangle, Clock, MapPin, Anchor, Flame, ExternalLink } from 'lucide-react';
import { useDemo } from '../../context/DemoContext';

export const DisruptionPanel: React.FC = () => {
  const { activeDisruptions, setSelectedShipmentId, selectedShipmentId } = useDemo();

  if (activeDisruptions.length === 0) {
    return (
      <div className="bg-[#0c1324] border border-slate-800 rounded-xl p-5 text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-400 mb-3 border border-emerald-500/20">
          <AlertTriangle className="w-5 h-5 text-emerald-400" />
        </div>
        <h3 className="text-sm font-semibold text-slate-200">Zero Active Disruptions Reported</h3>
        <p className="text-xs text-slate-300 mt-1 max-w-md mx-auto">
          All multi-modal logistics corridors, container ports, and national highway networks operating within nominal tolerances.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
          <h2 className="text-sm font-bold tracking-tight text-white uppercase font-mono flex items-center gap-2">
            Active Disruptions & Gate Closures
            <span className="text-[11px] font-mono font-normal px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
              {activeDisruptions.length} DETECTED
            </span>
          </h2>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 uppercase font-semibold">
          Simulated Demonstration Data
        </span>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {activeDisruptions.map((disruption) => {
          const isCritical = disruption.severity === 'CRITICAL';
          return (
            <div
              key={disruption.disruption_id}
              className={`rounded-xl border p-4 transition-all ${
                isCritical
                  ? 'bg-gradient-to-r from-red-950/30 via-[#0d1527] to-[#0d1527] border-red-500/50 shadow-[0_0_20px_rgba(239,68,68,0.12)]'
                  : 'bg-[#0d1527] border-slate-800'
              }`}
            >
              {/* Top Row: Title, ID, Severity */}
              <div className="flex flex-wrap items-start justify-between gap-2 pb-2.5 border-b border-slate-800/80">
                <div className="flex items-start gap-2.5">
                  <div className={`p-2 rounded-lg mt-0.5 ${
                    isCritical ? 'bg-red-500/20 text-red-400 border border-red-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                  }`}>
                    {disruption.type.toLowerCase().includes('port') ? (
                      <Anchor className="w-5 h-5" />
                    ) : (
                      <Flame className="w-5 h-5" />
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-cyan-400">
                        {disruption.disruption_id}
                      </span>
                      <span className="text-slate-400 text-xs">•</span>
                      <span className="text-xs font-semibold text-white">
                        {disruption.type}
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-1">
                      <MapPin className="w-3.5 h-3.5 text-red-400 shrink-0" />
                      <span className="text-slate-200 font-medium">{disruption.location}</span>
                      {disruption.impact_radius_km && (
                        <span className="text-slate-300 font-mono text-[11px]">
                          ({disruption.impact_radius_km} km blast radius)
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`text-xs font-mono font-bold px-2.5 py-1 rounded-md uppercase tracking-wider ${
                    isCritical
                      ? 'bg-red-500 text-white shadow-[0_0_10px_rgba(239,68,68,0.4)] animate-pulse'
                      : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                  }`}>
                    {disruption.severity}
                  </span>
                </div>
              </div>

              {/* Description body */}
              <p className="text-xs text-slate-300 mt-2.5 leading-relaxed font-sans">
                {disruption.description}
              </p>

              {/* Metadata details row */}
              <div className="flex flex-wrap items-center justify-between gap-3 mt-3 pt-2.5 border-t border-slate-800/60 text-xs font-mono">
                <div className="flex items-center gap-4 text-slate-400">
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-slate-300" />
                    <span>OUTAGE DURATION:</span>
                    <span className="text-slate-200 font-semibold">{disruption.expected_duration_hours}h EXPECTED</span>
                  </div>
                  <div className="hidden sm:flex items-center gap-1.5">
                    <span>STATUS:</span>
                    <span className="text-emerald-400 font-semibold">{disruption.status}</span>
                  </div>
                </div>

                {/* Affected Shipments Chips */}
                <div className="flex items-center gap-1.5">
                  <span className="text-slate-300 text-[11px] font-mono">AFFECTED SHIPMENTS:</span>
                  <div className="flex items-center gap-1">
                    {disruption.affected_shipment_ids.map((shpId) => {
                      const isSelected = selectedShipmentId === shpId;
                      const isShp1001 = shpId === 'SHP-1001';
                      return (
                        <button
                          key={shpId}
                          onClick={() => setSelectedShipmentId(shpId)}
                          className={`px-2 py-0.5 rounded text-[11px] font-mono font-semibold transition-all flex items-center gap-1 ${
                            isSelected
                              ? 'bg-cyan-500 text-slate-950 shadow-[0_0_8px_rgba(6,182,212,0.5)]'
                              : isShp1001
                              ? 'bg-red-500/30 text-red-300 border border-red-500/50 hover:bg-red-500/40'
                              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                          }`}
                        >
                          <span>{shpId}</span>
                          {isShp1001 && <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-ping" />}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
