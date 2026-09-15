import React from 'react';
import { StructuredRecommendation } from '../../types/copilot';
import { ShieldAlert, AlertTriangle, CheckCircle, Navigation, Truck, ArrowRight, Zap } from 'lucide-react';

interface StructuredAnswerProps {
  recommendation: StructuredRecommendation;
  onExecuteAction?: (actionText: string) => void;
}

export const StructuredAnswer: React.FC<StructuredAnswerProps> = ({ recommendation, onExecuteAction }) => {
  const isCritical = recommendation.priority === 'CRITICAL';

  return (
    <div className={`mt-3 rounded-xl border p-4 font-sans text-xs transition-all ${
      isCritical
        ? 'bg-red-950/20 border-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.12)]'
        : 'bg-slate-900/80 border-cyan-500/40'
    }`}>
      {/* Tactical Badge Bar */}
      <div className="flex items-center justify-between pb-2 mb-2.5 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-slate-400 uppercase font-bold">OPERATIONAL DIRECTIVE</span>
          <span className="text-slate-400">•</span>
          <span className="font-mono font-bold text-cyan-400">{recommendation.shipment_id}</span>
        </div>
        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${
          isCritical ? 'bg-red-500 text-white animate-pulse' : 'bg-amber-500/20 text-amber-300'
        }`}>
          PRIORITY: {recommendation.priority}
        </span>
      </div>

      {/* Structured Fields */}
      <div className="space-y-2 text-xs">
        <div>
          <span className="text-slate-400 font-mono text-[11px] block font-semibold">ROOT CAUSE / TRIGGER:</span>
          <p className="text-slate-200 mt-0.5 leading-relaxed">{recommendation.reason}</p>
        </div>

        <div>
          <span className="text-cyan-400 font-mono text-[11px] block font-semibold">RECOMMENDED OPERATIONAL ACTION:</span>
          <p className="text-slate-100 font-medium mt-0.5 leading-relaxed bg-slate-950/60 p-2 rounded border border-slate-800">
            {recommendation.recommended_action}
          </p>
        </div>

        {recommendation.alternative_route && (
          <div className="flex items-center gap-1.5 text-slate-300 font-mono text-[11px]">
            <Navigation className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <span className="text-slate-400">Reroute:</span>
            <span className="text-emerald-400 font-semibold">{recommendation.alternative_route}</span>
          </div>
        )}

        {recommendation.fleet_asset_assigned && (
          <div className="flex items-center gap-1.5 text-slate-300 font-mono text-[11px]">
            <Truck className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <span className="text-slate-400">Matched Asset:</span>
            <span className="text-cyan-300 font-semibold">{recommendation.fleet_asset_assigned}</span>
          </div>
        )}

        {recommendation.operational_impact && (
          <div className="pt-2 border-t border-slate-800/80 text-[11px] text-emerald-400 font-medium flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>{recommendation.operational_impact}</span>
          </div>
        )}
      </div>
    </div>
  );
};
