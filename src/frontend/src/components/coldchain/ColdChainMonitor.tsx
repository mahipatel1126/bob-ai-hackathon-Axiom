import React from 'react';
import { Snowflake, AlertTriangle, Battery, Wifi, Activity, ShieldAlert, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useDemo } from '../../context/DemoContext';

export const ColdChainMonitor: React.FC = () => {
  const { coldChainData, selectedShipmentId } = useDemo();

  if (!coldChainData) {
    return (
      <div className="bg-[#0c1324] border border-slate-800 rounded-xl p-6 text-center">
        <Snowflake className="w-8 h-8 text-slate-400 mx-auto mb-2" />
        <h3 className="text-sm font-semibold text-slate-200">No Cold-Chain Telemetry Required</h3>
        <p className="text-xs text-slate-300 mt-1 max-w-sm mx-auto">
          Shipment {selectedShipmentId} is classified as ambient dry freight and does not require thermal monitoring.
        </p>
      </div>
    );
  }

  const isCritical = coldChainData.severity === 'CRITICAL';
  const isWarning = coldChainData.severity === 'WARNING';

  return (
    <div className={`rounded-xl border p-4 lg:p-5 flex flex-col space-y-4 transition-all ${
      isCritical
        ? 'bg-gradient-to-br from-red-950/30 via-[#0c1324] to-[#0c1324] border-red-500/50 shadow-[0_0_20px_rgba(239,68,68,0.15)]'
        : 'bg-[#0c1324] border-slate-800'
    }`}>
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className={`p-2 rounded-lg ${
            isCritical ? 'bg-red-500/20 text-red-400 border border-red-500/40' : 'bg-cyan-500/10 text-cyan-400'
          }`}>
            <Snowflake className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-tight text-white uppercase font-mono">
                Cold-Chain IoT Telemetry & Thermal Integrity
              </h2>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-cyan-400 border border-slate-700">
                {coldChainData.shipment_id}
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">
              {coldChainData.cargo_description}
            </p>
          </div>
        </div>

        {/* Sensor Status Pill */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="flex items-center gap-1 text-slate-400">
            <Wifi className="w-3.5 h-3.5 text-emerald-400" />
            {coldChainData.sensor_id}
          </span>
          <span className="text-slate-400">•</span>
          <span className="flex items-center gap-1 text-slate-400">
            <Battery className="w-3.5 h-3.5 text-cyan-400" />
            {coldChainData.battery_level_percent}%
          </span>
          <span className="text-slate-400">•</span>
          <span className={`px-2.5 py-1 rounded font-bold uppercase tracking-wider ${
            isCritical
              ? 'bg-red-500 text-white animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.4)]'
              : 'bg-emerald-500/20 text-emerald-300'
          }`}>
            {coldChainData.severity}: EXCURSION
          </span>
        </div>
      </div>

      {/* Primary Telemetry Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* Current Temperature Reading */}
        <div className={`p-3.5 rounded-xl border flex flex-col justify-between ${
          isCritical ? 'bg-red-950/40 border-red-500/60' : 'bg-slate-900/80 border-slate-800'
        }`}>
          <span className="text-[11px] font-mono text-slate-400 uppercase font-semibold">Current Temperature</span>
          <div className="flex items-baseline gap-2 my-1">
            <span className={`text-3xl font-bold font-mono tracking-tight ${
              isCritical ? 'text-red-400 animate-pulse' : 'text-slate-100'
            }`}>
              {coldChainData.temperature}°C
            </span>
          </div>
          <span className="text-[11px] font-mono text-red-300">
            ▲ +2.4°C above upper limit
          </span>
        </div>

        {/* Allowed Range */}
        <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/80 flex flex-col justify-between">
          <span className="text-[11px] font-mono text-slate-400 uppercase font-semibold">Required Safe Envelope</span>
          <div className="flex items-baseline gap-1 my-1">
            <span className="text-2xl font-bold font-mono text-emerald-400">
              {coldChainData.allowed_min} – {coldChainData.allowed_max}°C
            </span>
          </div>
          <span className="text-[11px] font-mono text-slate-300">
            WHO Good Distribution Practice
          </span>
        </div>

        {/* Excursion Duration */}
        <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/80 flex flex-col justify-between">
          <span className="text-[11px] font-mono text-slate-400 uppercase font-semibold">Excursion Duration</span>
          <div className="flex items-baseline gap-1 my-1">
            <span className="text-2xl font-bold font-mono text-amber-400">
              {coldChainData.excursion_minutes} min
            </span>
          </div>
          <span className="text-[11px] font-mono text-slate-300">
            Peak Recorded: <strong className="text-red-400">{coldChainData.peak_temperature}°C</strong>
          </span>
        </div>

        {/* Critical Time Remaining */}
        <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/80 flex flex-col justify-between">
          <span className="text-[11px] font-mono text-slate-400 uppercase font-semibold">Spoilage Window</span>
          <div className="flex items-baseline gap-1 my-1">
            <span className="text-2xl font-bold font-mono text-red-400">
              {coldChainData.time_to_critical_hours} hrs
            </span>
          </div>
          <span className="text-[11px] font-mono text-red-300">
            Reefer Unit: <strong>{coldChainData.reefer_unit_status}</strong>
          </span>
        </div>
      </div>

      {/* Visual Temperature Sensor Graph (SVG) */}
      <div className="bg-[#080d19] border border-slate-800 rounded-xl p-3.5">
        <div className="flex items-center justify-between text-xs font-mono pb-2 mb-2 border-b border-slate-800/80">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            60-Minute Real-Time Thermal Trajectory
          </span>
          <div className="flex items-center gap-3 text-[11px]">
            <span className="text-emerald-400 flex items-center gap-1">
              <span className="w-2.5 h-1.5 bg-emerald-500/40 border border-emerald-500 rounded-sm inline-block" />
              Safe Band (2–8°C)
            </span>
            <span className="text-red-400 flex items-center gap-1">
              <span className="w-2.5 h-1 bg-red-500 rounded-sm inline-block" />
              Core Sensor (°C)
            </span>
          </div>
        </div>

        {/* SVG Thermal Line Chart */}
        <div className="w-full h-36 relative">
          <svg viewBox="0 0 600 120" className="w-full h-full overflow-visible">
            {/* Safe zone background band (2°C to 8°C) */}
            {/* Scale: 0°C = y:110, 14°C = y:10 => height per deg = 100 / 14 = 7.14 px */}
            {/* 2°C = 110 - (2 * 7.14) = 95.7 */}
            {/* 8°C = 110 - (8 * 7.14) = 52.8 */}
            {/* Band height = 95.7 - 52.8 = 42.9 */}
            <rect x="50" y="53" width="530" height="43" fill="#10b981" fillOpacity="0.12" stroke="#10b981" strokeDasharray="3,3" strokeWidth="1" />
            <text x="55" y="65" fill="#34d399" fontSize="8" fontFamily="monospace">MAX LIMIT: 8.0°C</text>
            <text x="55" y="92" fill="#34d399" fontSize="8" fontFamily="monospace">MIN LIMIT: 2.0°C</text>

            {/* Critical Excursion Threshold (10.0°C) line */}
            <line x1="50" y1="38" x2="580" y2="38" stroke="#ef4444" strokeWidth="1" strokeDasharray="4,2" opacity="0.6" />
            <text x="490" y="34" fill="#f87171" fontSize="8" fontFamily="monospace">CRITICAL: 10.0°C</text>

            {/* Grid Lines */}
            <line x1="50" y1="110" x2="580" y2="110" stroke="#1e293b" strokeWidth="1" />
            <line x1="50" y1="10" x2="50" y2="110" stroke="#1e293b" strokeWidth="1" />

            {/* Temperature Points & Curve */}
            {/* 
              Points:
              -60m: 4.5°C -> x: 60, y: 78
              -50m: 5.2°C -> x: 140, y: 73
              -40m: 7.9°C -> x: 220, y: 53.5
              -30m: 8.8°C -> x: 300, y: 47
              -20m: 10.2°C -> x: 380, y: 37
              -10m: 11.1°C -> x: 460, y: 30.7
              Current: 10.4°C -> x: 550, y: 35.7
            */}
            <path
              d="M 60 78 L 140 73 L 220 54 L 300 47 L 380 37 L 460 31 L 550 36"
              fill="none"
              stroke="#ef4444"
              strokeWidth="2.5"
            />

            {/* Circle markers */}
            {[
              { x: 60, y: 78, val: '4.5°' },
              { x: 140, y: 73, val: '5.2°' },
              { x: 220, y: 54, val: '7.9°' },
              { x: 300, y: 47, val: '8.8°' },
              { x: 380, y: 37, val: '10.2°' },
              { x: 460, y: 31, val: '11.1°' },
              { x: 550, y: 36, val: '10.4°' },
            ].map((pt, i) => (
              <g key={i} transform={`translate(${pt.x}, ${pt.y})`}>
                <circle r="4" fill={pt.y < 53 ? '#ef4444' : '#10b981'} stroke="#080d19" strokeWidth="1.5" />
                <text x="0" y="-8" textAnchor="middle" fill="#f1f5f9" fontSize="8" fontFamily="monospace" fontWeight="bold">
                  {pt.val}
                </text>
              </g>
            ))}

            {/* X-axis labels */}
            <text x="60" y="118" textAnchor="middle" fill="#64748b" fontSize="8" fontFamily="monospace">-60m</text>
            <text x="140" y="118" textAnchor="middle" fill="#64748b" fontSize="8" fontFamily="monospace">-50m</text>
            <text x="220" y="118" textAnchor="middle" fill="#64748b" fontSize="8" fontFamily="monospace">-40m</text>
            <text x="300" y="118" textAnchor="middle" fill="#64748b" fontSize="8" fontFamily="monospace">-30m</text>
            <text x="380" y="118" textAnchor="middle" fill="#64748b" fontSize="8" fontFamily="monospace">-20m</text>
            <text x="460" y="118" textAnchor="middle" fill="#64748b" fontSize="8" fontFamily="monospace">-10m</text>
            <text x="550" y="118" textAnchor="middle" fill="#38bdf8" fontSize="8" fontFamily="monospace" fontWeight="bold">NOW</text>
          </svg>
        </div>
      </div>

      {/* Recommended Remediation & Prototype Classification Disclaimer */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3 text-xs space-y-2">
        <div className="flex items-start gap-2">
          <ShieldAlert className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-mono text-[11px] font-bold text-red-400 uppercase">
              Immediate Thermal Containment Directive:
            </span>
            <p className="text-slate-200 mt-0.5 leading-relaxed font-sans font-medium">
              {coldChainData.action}
            </p>
          </div>
        </div>

        {/* Regulatory disclaimer */}
        <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-300 font-mono flex items-center justify-between">
          <span>CLASSIFICATION SOURCE: ChainGuard AI Predictive Risk Engine (Prototype Demonstration Model)</span>
          <span className="text-slate-300">Sensor Firmware v3.4.1</span>
        </div>
      </div>
    </div>
  );
};
