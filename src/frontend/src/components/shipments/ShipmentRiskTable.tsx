import React, { useState } from 'react';
import { ShieldAlert, ArrowRight, DollarSign, Clock, Snowflake, CheckCircle2, ChevronRight, Eye } from 'lucide-react';
import { useDemo } from '../../context/DemoContext';
import { Shipment, RiskLevel } from '../../types/shipment';

interface ShipmentRiskTableProps {
  onOpenDetailModal?: (shipment: Shipment) => void;
}

export const ShipmentRiskTable: React.FC<ShipmentRiskTableProps> = ({ onOpenDetailModal }) => {
  const { shipments, selectedShipmentId, setSelectedShipmentId } = useDemo();
  const [filter, setFilter] = useState<'ALL' | 'CRITICAL' | 'COLD_CHAIN'>('ALL');

  const filteredShipments = shipments.filter((s) => {
    if (filter === 'CRITICAL') return s.risk_level === 'CRITICAL';
    if (filter === 'COLD_CHAIN') return s.is_cold_chain;
    return true;
  });

  const getRiskBadge = (level: RiskLevel) => {
    switch (level) {
      case 'CRITICAL':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-red-500 text-white shadow-[0_0_10px_rgba(239,68,68,0.5)] animate-pulse">
            CRITICAL
          </span>
        );
      case 'HIGH':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-mono font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40">
            HIGH
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-mono font-semibold bg-yellow-500/20 text-yellow-300 border border-yellow-500/40">
            MEDIUM
          </span>
        );
      case 'LOW':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-mono font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
            LOW
          </span>
        );
    }
  };

  return (
    <div className="bg-[#0c1324] border border-slate-800 rounded-xl overflow-hidden flex flex-col">
      {/* Table Header Controls */}
      <div className="p-4 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 bg-[#0d1527]">
        <div className="flex items-center gap-2.5">
          <ShieldAlert className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-bold tracking-tight text-white uppercase font-mono">
            Shipment Risk Matrix & Delay Forecast
          </h2>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
            {filteredShipments.length} SHIPMENTS
          </span>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1 text-xs font-mono">
          <button
            onClick={() => setFilter('ALL')}
            className={`px-2.5 py-1 rounded transition-colors ${
              filter === 'ALL' ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            ALL
          </button>
          <button
            onClick={() => setFilter('CRITICAL')}
            className={`px-2.5 py-1 rounded transition-colors flex items-center gap-1 ${
              filter === 'CRITICAL' ? 'bg-red-500 text-white font-bold' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-red-400" />
            CRITICAL ONLY
          </button>
          <button
            onClick={() => setFilter('COLD_CHAIN')}
            className={`px-2.5 py-1 rounded transition-colors flex items-center gap-1 ${
              filter === 'COLD_CHAIN' ? 'bg-cyan-600 text-white font-bold' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            <Snowflake className="w-3 h-3" />
            COLD CHAIN
          </button>
        </div>
      </div>

      {/* Responsive Table Body */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800/80 bg-slate-900/60 font-mono text-[11px] text-slate-400 uppercase tracking-wider">
              <th className="py-2.5 px-3.5">Shipment ID</th>
              <th className="py-2.5 px-3">Corridor (Origin → Dest)</th>
              <th className="py-2.5 px-3">Cargo Details</th>
              <th className="py-2.5 px-3">Value</th>
              <th className="py-2.5 px-3">Risk Score</th>
              <th className="py-2.5 px-3">Delay Risk</th>
              <th className="py-2.5 px-3">Est. Delay</th>
              <th className="py-2.5 px-3">Recommended Operational Action</th>
              <th className="py-2.5 px-3 text-right">Inspect</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50 font-sans">
            {filteredShipments.map((shipment) => {
              const isSelected = selectedShipmentId === shipment.shipment_id;
              const isCritical = shipment.risk_level === 'CRITICAL';
              return (
                <tr
                  key={shipment.shipment_id}
                  onClick={() => setSelectedShipmentId(shipment.shipment_id)}
                  className={`cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-cyan-950/40 border-l-4 border-l-cyan-400 text-white'
                      : isCritical
                      ? 'bg-red-950/20 hover:bg-red-950/30 border-l-4 border-l-red-500'
                      : 'hover:bg-slate-800/50 border-l-4 border-l-transparent text-slate-200'
                  }`}
                >
                  {/* Shipment ID & Cold Chain Icon */}
                  <td className="py-3 px-3.5 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-cyan-400 text-xs">
                        {shipment.shipment_id}
                      </span>
                      {shipment.is_cold_chain && (
                        <span
                          className={`p-1 rounded ${
                            shipment.temperature_current && shipment.temperature_current > (shipment.temperature_max || 8)
                              ? 'bg-red-500/30 text-red-300 border border-red-500/40 animate-pulse'
                              : 'bg-cyan-500/20 text-cyan-300'
                          }`}
                          title={shipment.is_cold_chain ? `Cold-Chain: ${shipment.temperature_current}°C` : ''}
                        >
                          <Snowflake className="w-3 h-3" />
                        </span>
                      )}
                    </div>
                    <div className="text-[10px] text-slate-300 font-mono mt-0.5">
                      {shipment.carrier}
                    </div>
                  </td>

                  {/* Corridor */}
                  <td className="py-3 px-3">
                    <div className="flex items-center gap-1 text-slate-200 font-medium">
                      <span className="truncate max-w-[110px]" title={shipment.origin}>{shipment.origin.split(' ')[0]}</span>
                      <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
                      <span className="truncate max-w-[110px]" title={shipment.destination}>{shipment.destination.split(' ')[0]}</span>
                    </div>
                    <div className="text-[10px] text-slate-300 font-mono mt-0.5 truncate max-w-[180px]">
                      {shipment.current_location}
                    </div>
                  </td>

                  {/* Cargo */}
                  <td className="py-3 px-3">
                    <div className="text-slate-200 font-medium truncate max-w-[180px]" title={shipment.cargo_type}>
                      {shipment.cargo_type}
                    </div>
                    {shipment.temperature_current && (
                      <div className={`text-[10px] font-mono mt-0.5 ${
                        shipment.temperature_current > (shipment.temperature_max || 8) ? 'text-red-400 font-bold' : 'text-cyan-400'
                      }`}>
                        Current Temp: {shipment.temperature_current}°C (Limit: {shipment.temperature_min}-{shipment.temperature_max}°C)
                      </div>
                    )}
                  </td>

                  {/* Value */}
                  <td className="py-3 px-3 font-mono text-slate-300 whitespace-nowrap">
                    ${shipment.cargo_value.toLocaleString()}
                  </td>

                  {/* Risk Score & Level */}
                  <td className="py-3 px-3 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <div className="w-10 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-full ${
                            shipment.risk_score > 80
                              ? 'bg-red-500'
                              : shipment.risk_score > 50
                              ? 'bg-amber-500'
                              : 'bg-emerald-500'
                          }`}
                          style={{ width: `${shipment.risk_score}%` }}
                        />
                      </div>
                      <span className="font-mono font-bold text-xs">
                        {shipment.risk_score}
                      </span>
                    </div>
                    <div className="mt-1">
                      {getRiskBadge(shipment.risk_level)}
                    </div>
                  </td>

                  {/* Delay Prob */}
                  <td className="py-3 px-3 font-mono">
                    <span className={`font-semibold ${shipment.delay_probability > 0.7 ? 'text-red-400' : 'text-slate-300'}`}>
                      {Math.round(shipment.delay_probability * 100)}%
                    </span>
                  </td>

                  {/* Est Delay */}
                  <td className="py-3 px-3 font-mono whitespace-nowrap">
                    <span className={`font-bold flex items-center gap-1 ${
                      shipment.estimated_delay_hours > 20 ? 'text-red-400' : 'text-amber-400'
                    }`}>
                      <Clock className="w-3 h-3" />
                      +{shipment.estimated_delay_hours}h
                    </span>
                  </td>

                  {/* Action recommendation */}
                  <td className="py-3 px-3">
                    <div className={`text-xs max-w-[280px] line-clamp-2 ${
                      isCritical ? 'text-red-300 font-medium' : 'text-slate-300'
                    }`} title={shipment.recommended_action}>
                      {shipment.recommended_action}
                    </div>
                  </td>

                  {/* View Button */}
                  <td className="py-3 px-3 text-right whitespace-nowrap">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedShipmentId(shipment.shipment_id);
                        if (onOpenDetailModal) {
                          onOpenDetailModal(shipment);
                        }
                      }}
                      className="p-1.5 rounded-md hover:bg-slate-700/80 text-slate-400 hover:text-cyan-300 transition-colors inline-flex items-center"
                      title="Inspect full shipment telemetry"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
