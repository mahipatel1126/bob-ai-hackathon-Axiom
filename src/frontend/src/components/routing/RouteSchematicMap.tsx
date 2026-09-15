import React from 'react';
import { RouteRecommendation } from '../../types/route';
import { MapPin, Navigation, ShieldCheck, AlertOctagon, ArrowRight, Truck } from 'lucide-react';

interface RouteSchematicMapProps {
  routeData: RouteRecommendation | null;
  shipmentId: string;
}

export const RouteSchematicMap: React.FC<RouteSchematicMapProps> = ({ routeData, shipmentId }) => {
  if (!routeData) {
    return (
      <div className="h-64 flex items-center justify-center bg-slate-950/60 rounded-xl border border-slate-800 text-xs text-slate-400">
        No active schematic route calculated for {shipmentId}
      </div>
    );
  }

  return (
    <div className="bg-[#080e1d] border border-slate-800/90 rounded-xl p-4 relative overflow-hidden">
      {/* Schematic Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 mb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <Navigation className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            Western Corridor Multi-Modal Transit Schematic
          </span>
        </div>
        <div className="flex items-center gap-3 text-[11px] font-mono">
          <span className="flex items-center gap-1.5 text-red-400">
            <span className="w-2.5 h-1 bg-red-500 rounded inline-block" /> Current (Blocked)
          </span>
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2.5 h-1 bg-emerald-400 rounded inline-block" /> Recommended Divert
          </span>
        </div>
      </div>

      {/* SVG Tactical Schematic Map */}
      <div className="relative w-full h-[220px] bg-slate-950/70 rounded-lg border border-slate-800/70 p-2 overflow-hidden">
        {/* Background Grid Pattern */}
        <div className="absolute inset-0 bg-command-grid opacity-60 pointer-events-none" />

        <svg viewBox="0 0 700 200" className="w-full h-full">
          <defs>
            {/* Gradients */}
            <linearGradient id="blockedLine" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#38bdf8" />
              <stop offset="40%" stopColor="#f59e0b" />
              <stop offset="70%" stopColor="#ef4444" />
              <stop offset="100%" stopColor="#b91c1c" />
            </linearGradient>

            <linearGradient id="divertLine" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#38bdf8" />
              <stop offset="50%" stopColor="#10b981" />
              <stop offset="100%" stopColor="#059669" />
            </linearGradient>

            <filter id="glow-green" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="glow" />
              <feComposite in="SourceGraphic" in2="glow" operator="over" />
            </filter>
            
            <filter id="glow-red" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="glow" />
              <feComposite in="SourceGraphic" in2="glow" operator="over" />
            </filter>
          </defs>

          {/* Current Stalled Route (Upper / Original Track) */}
          <path
            d="M 60 100 L 220 100 L 380 100 L 520 100 L 640 100"
            fill="none"
            stroke="url(#blockedLine)"
            strokeWidth="3"
            strokeDasharray="6,4"
            opacity="0.75"
          />

          {/* Recommended Divert Track (Branching Southwest to Hazira) */}
          <path
            d="M 220 100 C 260 100, 300 155, 380 155 L 530 155"
            fill="none"
            stroke="url(#divertLine)"
            strokeWidth="4"
            filter="url(#glow-green)"
          />

          {/* Node 1: Origin (Ahmedabad) */}
          <g transform="translate(60, 100)">
            <circle r="9" fill="#0369a1" stroke="#38bdf8" strokeWidth="2.5" />
            <circle r="3.5" fill="#ffffff" />
            <text x="0" y="-16" textAnchor="middle" fill="#e2e8f0" fontSize="10.5" fontFamily="monospace" fontWeight="bold">
              Ahmedabad
            </text>
            <text x="0" y="22" textAnchor="middle" fill="#94a3b8" fontSize="8.5" fontFamily="monospace">
              ORIGIN [Departed]
            </text>
          </g>

          {/* Node 2: Vadodara Intercept & Transshipment (Rendezvous point with TRUCK-204) */}
          <g transform="translate(220, 100)">
            <circle r="12" fill="#0f172a" stroke="#06b6d4" strokeWidth="2.5" />
            <circle r="4.5" fill="#06b6d4" className="animate-ping" />
            <circle r="4" fill="#38bdf8" />
            <text x="0" y="-18" textAnchor="middle" fill="#38bdf8" fontSize="10.5" fontFamily="monospace" fontWeight="bold">
              Vadodara Interchange
            </text>
            <text x="0" y="24" textAnchor="middle" fill="#22d3ee" fontSize="8.5" fontFamily="monospace">
              ⚡ TRUCK-204 Rendezvous
            </text>
          </g>

          {/* Node 3: Bharuch / Divert Junction */}
          <g transform="translate(380, 100)">
            <circle r="7" fill="#1e293b" stroke="#f59e0b" strokeWidth="2" />
            <text x="0" y="-14" textAnchor="middle" fill="#cbd5e1" fontSize="9" fontFamily="monospace">
              Bharuch / Narmada
            </text>
            <text x="0" y="19" textAnchor="middle" fill="#f59e0b" fontSize="8" fontFamily="monospace">
              Divert Split
            </text>
          </g>

          {/* Node 4: Surat Expressway Bypass on Current Path */}
          <g transform="translate(520, 100)">
            <circle r="7" fill="#1e293b" stroke="#ef4444" strokeWidth="2" />
            <text x="0" y="-14" textAnchor="middle" fill="#94a3b8" fontSize="9" fontFamily="monospace">
              Surat / Vapi
            </text>
          </g>

          {/* Node 5: JNPT Port Strike Zone (Blocked Destination) */}
          <g transform="translate(640, 100)">
            <circle r="13" fill="#7f1d1d" stroke="#ef4444" strokeWidth="2.5" filter="url(#glow-red)" />
            <text x="0" y="4" textAnchor="middle" fill="#ffffff" fontSize="11" fontWeight="bold">✕</text>
            <text x="0" y="-20" textAnchor="middle" fill="#f87171" fontSize="10.5" fontFamily="monospace" fontWeight="bold">
              JNPT Mumbai Port
            </text>
            <text x="0" y="26" textAnchor="middle" fill="#ef4444" fontSize="8.5" fontFamily="monospace" fontWeight="bold">
              STRIKE BLOCKED (+42h)
            </text>
          </g>

          {/* Node 6: Recommended Destination (Hazira Adani Port Terminal) */}
          <g transform="translate(530, 155)">
            <circle r="12" fill="#064e3b" stroke="#10b981" strokeWidth="2.5" filter="url(#glow-green)" />
            <circle r="4" fill="#a7f3d0" />
            <text x="0" y="-18" textAnchor="middle" fill="#34d399" fontSize="11" fontFamily="monospace" fontWeight="bold">
              Hazira Adani Port CFS
            </text>
            <text x="0" y="22" textAnchor="middle" fill="#10b981" fontSize="8.5" fontFamily="monospace" fontWeight="bold">
              RECOMMENDED (5.2h / Green Corridor)
            </text>
          </g>
        </svg>
      </div>

      {/* Corridor Transition Callout */}
      <div className="mt-3 flex flex-wrap items-center justify-between gap-3 text-xs bg-slate-900/60 p-2.5 rounded-lg border border-slate-800 font-mono">
        <div className="flex items-center gap-2">
          <span className="text-slate-400">CORRIDOR REASSIGNMENT:</span>
          <span className="text-slate-300">NH48 Mumbai Gate 4</span>
          <ArrowRight className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-emerald-400 font-bold">SH-6 Adani Hazira Container Berth</span>
        </div>
        <div className="text-emerald-400 font-bold">
          ⚡ 37.5 HOURS TRANSIT SAVED
        </div>
      </div>
    </div>
  );
};
