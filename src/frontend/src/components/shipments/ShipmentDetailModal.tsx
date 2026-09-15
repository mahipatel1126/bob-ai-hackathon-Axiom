import React from 'react';
import { X, ShieldAlert, MapPin, Clock, DollarSign, Truck, AlertTriangle, Snowflake, CheckCircle2 } from 'lucide-react';
import { Shipment } from '../../types/shipment';

interface ShipmentDetailModalProps {
  shipment: Shipment | null;
  onClose: () => void;
  onSelectForReroute?: (shipmentId: string) => void;
}

export const ShipmentDetailModal: React.FC<ShipmentDetailModalProps> = ({
  shipment,
  onClose,
  onSelectForReroute,
}) => {
  if (!shipment) return null;

  const isCritical = shipment.risk_level === 'CRITICAL';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-[#0b1222] border border-slate-800 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl">
        {/* Modal Header */}
        <div className="p-4 sm:p-5 border-b border-slate-800 flex items-center justify-between bg-[#0e1629]">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${
              isCritical ? 'bg-red-500/20 text-red-400 border border-red-500/40' : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
            }`}>
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold font-mono text-white">{shipment.shipment_id}</span>
                <span className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-full ${
                  isCritical ? 'bg-red-500 text-white animate-pulse' : 'bg-amber-500/20 text-amber-300'
                }`}>
                  {shipment.risk_level}
                </span>
                {shipment.is_cold_chain && (
                  <span className="text-xs font-mono font-medium px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center gap-1">
                    <Snowflake className="w-3 h-3" />
                    COLD CHAIN
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">{shipment.cargo_type}</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-5 space-y-4 max-h-[75vh] overflow-y-auto">
          {/* Key Metric Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
              <span className="text-[11px] font-mono text-slate-400 block">CARGO VALUE</span>
              <span className="text-base font-bold font-mono text-white">${shipment.cargo_value.toLocaleString()}</span>
            </div>
            <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
              <span className="text-[11px] font-mono text-slate-400 block">RISK SCORE</span>
              <span className="text-base font-bold font-mono text-red-400">{shipment.risk_score} / 100</span>
            </div>
            <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
              <span className="text-[11px] font-mono text-slate-400 block">DELAY PROBABILITY</span>
              <span className="text-base font-bold font-mono text-amber-400">{Math.round(shipment.delay_probability * 100)}%</span>
            </div>
            <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
              <span className="text-[11px] font-mono text-slate-400 block">ESTIMATED DELAY</span>
              <span className="text-base font-bold font-mono text-red-400">+{shipment.estimated_delay_hours}h</span>
            </div>
          </div>

          {/* Current Corridor Info */}
          <div className="bg-slate-900/50 p-3.5 rounded-lg border border-slate-800 text-xs space-y-2">
            <div className="flex items-center justify-between text-slate-400 font-mono">
              <span>ORIGIN:</span>
              <span className="text-slate-200 font-sans font-medium">{shipment.origin}</span>
            </div>
            <div className="flex items-center justify-between text-slate-400 font-mono">
              <span>DESTINATION:</span>
              <span className="text-slate-200 font-sans font-medium">{shipment.destination}</span>
            </div>
            <div className="flex items-center justify-between text-slate-400 font-mono">
              <span>CARRIER:</span>
              <span className="text-slate-200 font-sans font-medium">{shipment.carrier}</span>
            </div>
            <div className="flex items-center justify-between text-slate-400 font-mono">
              <span>LAST TELEMETRY GPS:</span>
              <span className="text-cyan-400 font-sans font-medium">{shipment.current_location}</span>
            </div>
          </div>

          {/* Temperature Excursion Alert (if Cold Chain) */}
          {shipment.is_cold_chain && shipment.temperature_current && (
            <div className="bg-red-950/30 border border-red-500/50 rounded-lg p-3.5 flex items-start gap-3">
              <div className="p-2 rounded bg-red-500/20 text-red-400 shrink-0">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-red-400 font-mono uppercase">
                  Active Cold-Chain Excursion
                </h4>
                <p className="text-xs text-red-200 leading-relaxed">
                  Cargo requires <span className="font-mono font-bold text-white">2.0°C – 8.0°C</span>. Current reading is <span className="font-mono font-bold text-red-300">{shipment.temperature_current}°C</span>. Degraded compressor unit in primary transport vehicle.
                </p>
              </div>
            </div>
          )}

          {/* Recommended Action Box */}
          <div className="bg-cyan-950/20 border border-cyan-500/40 rounded-lg p-3.5">
            <span className="text-[11px] font-mono uppercase text-cyan-400 font-bold block mb-1">
              AI Decision Recommendation
            </span>
            <p className="text-xs text-slate-200 leading-relaxed font-medium">
              {shipment.recommended_action}
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-[#0e1629] flex items-center justify-end gap-2.5">
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 transition-colors"
          >
            Close
          </button>
          {onSelectForReroute && (
            <button
              onClick={() => {
                onSelectForReroute(shipment.shipment_id);
                onClose();
              }}
              className="px-4 py-1.5 rounded-lg text-xs font-semibold text-slate-950 bg-cyan-400 hover:bg-cyan-300 transition-colors shadow-sm"
            >
              Focus in Route Optimizer
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
