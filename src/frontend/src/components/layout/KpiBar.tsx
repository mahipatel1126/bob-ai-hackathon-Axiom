import React from 'react';
import { AlertTriangle, AlertOctagon, Truck, Snowflake, ShieldAlert, TrendingUp } from 'lucide-react';
import { useDemo } from '../../context/DemoContext';

export const KpiBar: React.FC = () => {
  const { currentStep, shipments, activeDisruptions, fleetAssets, coldChainData } = useDemo();

  // Compute dynamic KPI metrics based on current state
  const activeDisruptionsCount = activeDisruptions.length;
  const atRiskCount = shipments.filter((s) => s.risk_level === 'HIGH' || s.risk_level === 'CRITICAL').length;
  const criticalCount = shipments.filter((s) => s.risk_level === 'CRITICAL').length;
  
  const totalFleet = fleetAssets.length;
  const activeOrAssigned = fleetAssets.filter((a) => a.status === 'IN_TRANSIT' || a.status === 'ASSIGNED').length;
  const idleCount = fleetAssets.filter((a) => a.status === 'IDLE').length;
  const fleetUtilisationPercent = Math.round((activeOrAssigned / totalFleet) * 100);

  const coldChainAlertsCount = coldChainData && coldChainData.severity === 'CRITICAL' ? 1 : 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3.5 mb-5">
      {/* 1. Active Disruptions */}
      <div className={`p-3.5 rounded-xl border backdrop-blur transition-all ${
        activeDisruptionsCount > 0
          ? 'bg-red-950/20 border-red-500/40 shadow-[0_0_15px_rgba(239,68,68,0.12)]'
          : 'bg-slate-900/60 border-slate-800'
      }`}>
        <div className="flex items-center justify-between text-xs font-mono mb-2">
          <span className="text-slate-400 uppercase tracking-wider font-semibold">Active Disruptions</span>
          <AlertTriangle className={`w-4 h-4 ${activeDisruptionsCount > 0 ? 'text-red-400 animate-pulse' : 'text-slate-400'}`} />
        </div>
        <div className="flex items-baseline justify-between">
          <span className={`text-2xl font-bold font-mono tracking-tight ${activeDisruptionsCount > 0 ? 'text-red-400' : 'text-slate-200'}`}>
            {activeDisruptionsCount}
          </span>
          <span className={`text-[11px] font-mono px-2 py-0.5 rounded-md font-semibold ${
            activeDisruptionsCount > 0 ? 'bg-red-500/20 text-red-300 border border-red-500/30' : 'bg-emerald-500/10 text-emerald-400'
          }`}>
            {activeDisruptionsCount > 0 ? '1 CRITICAL (JNPT)' : 'NORMAL'}
          </span>
        </div>
        <div className="text-[11px] text-slate-300 mt-1.5 flex items-center gap-1 font-sans">
          <span>{activeDisruptionsCount > 0 ? 'JNPT Port Strike (72h Outage)' : 'Corridors clear'}</span>
        </div>
      </div>

      {/* 2. At-Risk Shipments */}
      <div className={`p-3.5 rounded-xl border backdrop-blur transition-all ${
        atRiskCount > 0
          ? 'bg-amber-950/20 border-amber-500/40 shadow-[0_0_15px_rgba(245,158,11,0.12)]'
          : 'bg-slate-900/60 border-slate-800'
      }`}>
        <div className="flex items-center justify-between text-xs font-mono mb-2">
          <span className="text-slate-400 uppercase tracking-wider font-semibold">At-Risk Shipments</span>
          <ShieldAlert className={`w-4 h-4 ${atRiskCount > 0 ? 'text-amber-400' : 'text-slate-400'}`} />
        </div>
        <div className="flex items-baseline justify-between">
          <span className={`text-2xl font-bold font-mono tracking-tight ${atRiskCount > 0 ? 'text-amber-400' : 'text-slate-200'}`}>
            {atRiskCount}
          </span>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-300 border border-amber-500/20 font-semibold">
            {atRiskCount > 0 ? `OF ${shipments.length} MONITORED` : 'NOMINAL'}
          </span>
        </div>
        <div className="text-[11px] text-slate-300 mt-1.5 font-sans truncate">
          {atRiskCount > 0 ? 'Western freight corridor impacted' : 'All ETAs on schedule'}
        </div>
      </div>

      {/* 3. Critical Shipments */}
      <div className={`p-3.5 rounded-xl border backdrop-blur transition-all relative overflow-hidden ${
        criticalCount > 0
          ? 'bg-gradient-to-br from-red-950/40 to-slate-900/80 border-red-500/60 shadow-[0_0_20px_rgba(239,68,68,0.2)]'
          : 'bg-slate-900/60 border-slate-800'
      }`}>
        {criticalCount > 0 && (
          <div className="absolute top-0 right-0 w-12 h-12 bg-red-500/10 rounded-full blur-xl pointer-events-none" />
        )}
        <div className="flex items-center justify-between text-xs font-mono mb-2">
          <span className="text-slate-400 uppercase tracking-wider font-semibold">Critical Shipments</span>
          <AlertOctagon className={`w-4 h-4 ${criticalCount > 0 ? 'text-red-400 animate-radar' : 'text-slate-400'}`} />
        </div>
        <div className="flex items-baseline justify-between">
          <span className={`text-2xl font-bold font-mono tracking-tight ${criticalCount > 0 ? 'text-red-400' : 'text-slate-200'}`}>
            {criticalCount}
          </span>
          <span className={`text-[11px] font-mono px-2 py-0.5 rounded-md font-bold uppercase tracking-wider ${
            criticalCount > 0 ? 'bg-red-500 text-white animate-pulse' : 'bg-emerald-500/10 text-emerald-400'
          }`}>
            {criticalCount > 0 ? 'ACTION REQ' : 'SECURE'}
          </span>
        </div>
        <div className="text-[11px] text-red-300 mt-1.5 font-sans font-medium flex items-center gap-1">
          {criticalCount > 0 ? 'SHP-1001: Pharma Vaccines' : 'Zero critical excursions'}
        </div>
      </div>

      {/* 4. Fleet Utilisation */}
      <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur">
        <div className="flex items-center justify-between text-xs font-mono mb-2">
          <span className="text-slate-400 uppercase tracking-wider font-semibold">Fleet Utilisation</span>
          <Truck className="w-4 h-4 text-cyan-400" />
        </div>
        <div className="flex items-baseline justify-between">
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-bold font-mono tracking-tight text-white">
              {fleetUtilisationPercent}%
            </span>
            <span className="text-xs text-slate-300 font-mono">({idleCount} idle)</span>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-semibold flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            OPTIMAL
          </span>
        </div>
        {/* Visual utilisation progress bar */}
        <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2.5 overflow-hidden">
          <div
            className="bg-gradient-to-r from-blue-500 to-cyan-400 h-full rounded-full transition-all duration-500"
            style={{ width: `${fleetUtilisationPercent}%` }}
          />
        </div>
      </div>

      {/* 5. Cold-Chain Alerts */}
      <div className={`p-3.5 rounded-xl border backdrop-blur transition-all ${
        coldChainAlertsCount > 0
          ? 'bg-blue-950/30 border-cyan-500/50 shadow-[0_0_15px_rgba(6,182,212,0.15)]'
          : 'bg-slate-900/60 border-slate-800'
      }`}>
        <div className="flex items-center justify-between text-xs font-mono mb-2">
          <span className="text-slate-400 uppercase tracking-wider font-semibold">Cold-Chain Alerts</span>
          <Snowflake className={`w-4 h-4 ${coldChainAlertsCount > 0 ? 'text-cyan-400 animate-spin' : 'text-slate-400'}`} style={{ animationDuration: '6s' }} />
        </div>
        <div className="flex items-baseline justify-between">
          <span className={`text-2xl font-bold font-mono tracking-tight ${coldChainAlertsCount > 0 ? 'text-cyan-400' : 'text-slate-200'}`}>
            {coldChainAlertsCount}
          </span>
          <span className={`text-[11px] font-mono px-2 py-0.5 rounded-md font-bold ${
            coldChainAlertsCount > 0 ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'bg-emerald-500/10 text-emerald-400'
          }`}>
            {coldChainAlertsCount > 0 ? '10.4°C EXCURSION' : 'STABLE'}
          </span>
        </div>
        <div className="text-[11px] text-cyan-300 mt-1.5 font-sans truncate font-medium">
          {coldChainAlertsCount > 0 ? 'Sensor IOT-TEMP-9021 Alert' : 'All sensor streams in 2-8°C envelope'}
        </div>
      </div>
    </div>
  );
};
