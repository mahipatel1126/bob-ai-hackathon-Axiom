import React, { useState, useEffect } from 'react';
import { Shield, Radio, Activity, RefreshCw, ChevronRight, MessageSquareCode, Play, RotateCcw } from 'lucide-react';
import { useDemo, DEMO_STEPS } from '../../context/DemoContext';

export const Header: React.FC = () => {
  const { currentStep, setStep, resetDemo, copilotOpen, setCopilotOpen } = useDemo();
  const [time, setTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toUTCString().replace('GMT', 'UTC'));
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="border-b border-slate-800 bg-[#0b1120]/95 backdrop-blur sticky top-0 z-40">
      {/* Top Banner & Command Identification */}
      <div className="max-w-[1720px] mx-auto px-4 lg:px-6 py-2.5 flex flex-wrap items-center justify-between gap-4">
        {/* Brand & System Title */}
        <div className="flex items-center gap-3.5">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-600/30 border border-cyan-500/40 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.25)]">
            <Shield className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse border-2 border-[#0b1120]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                <span>ChainGuard</span>
                <span className="text-cyan-400 font-mono text-sm px-1.5 py-0.5 rounded bg-cyan-950/70 border border-cyan-800/60 font-semibold">AI</span>
              </h1>
              <span className="text-xs px-2 py-0.5 rounded-full font-mono font-medium border bg-slate-800/80 text-slate-300 border-slate-700">
                v1.0-DEMO
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium tracking-wide">
              Supply Chain Operations Command Center
            </p>
          </div>
        </div>

        {/* Operational Status & Telemetry Heartbeat */}
        <div className="flex items-center gap-6 text-xs font-mono">
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-md bg-slate-900/90 border border-slate-800 text-slate-300">
            <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span className="text-slate-400">TELEMETRY:</span>
            <span className="text-emerald-400 font-semibold">ONLINE (38 SENSORS ACTIVE)</span>
          </div>

          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-md bg-slate-900/90 border border-slate-800 text-slate-300">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400">CLOCK:</span>
            <span className="text-slate-200">{time || '2026-09-15 05:54:00 UTC'}</span>
          </div>

          {/* Bob Copilot Quick Trigger */}
          <button
            onClick={() => setCopilotOpen(!copilotOpen)}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-md font-sans text-xs font-semibold transition-all border shadow-sm ${
              copilotOpen
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500 shadow-[0_0_12px_rgba(6,182,212,0.3)]'
                : 'bg-gradient-to-r from-blue-600/30 to-cyan-600/30 text-cyan-200 hover:text-white border-cyan-500/40 hover:border-cyan-400'
            }`}
          >
            <MessageSquareCode className="w-4 h-4 text-cyan-400" />
            <span>IBM Bob Copilot</span>
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          </button>
        </div>
      </div>

      {/* Demo Story Scenario Stepper Bar */}
      <div className="border-t border-slate-800/80 bg-[#070d1a]/95 px-4 lg:px-6 py-2 overflow-x-auto">
        <div className="max-w-[1720px] mx-auto flex items-center justify-between gap-3 min-w-[960px]">
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-bold uppercase tracking-wider font-mono text-cyan-400/90 flex items-center gap-1.5">
              <Play className="w-3 h-3 text-cyan-400" />
              Demo Scenario:
            </span>
            <span className="text-xs font-medium text-slate-300 bg-slate-800/90 px-2 py-0.5 rounded border border-slate-700/60">
              Mumbai JNPT Port Strike & Reefer Rescue
            </span>
          </div>

          {/* Stepper buttons */}
          <div className="flex items-center gap-1">
            {DEMO_STEPS.map((s) => {
              const isActive = currentStep === s.step;
              const isPassed = currentStep > s.step;
              return (
                <button
                  key={s.step}
                  onClick={() => setStep(s.step)}
                  className={`px-2.5 py-1 rounded text-xs font-medium transition-all flex items-center gap-1.5 border ${
                    isActive
                      ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400/60 shadow-[0_0_8px_rgba(6,182,212,0.25)] font-semibold'
                      : isPassed
                      ? 'bg-slate-900/60 text-slate-300 border-slate-800 hover:border-slate-700'
                      : 'bg-slate-900/30 text-slate-400 border-slate-800/50 hover:border-slate-700 hover:text-slate-300'
                  }`}
                  title={s.shortDesc}
                >
                  <span className={`w-4 h-4 rounded-full text-[10px] flex items-center justify-center font-mono ${
                    isActive ? 'bg-cyan-500 text-slate-950 font-bold' : isPassed ? 'bg-slate-700 text-slate-200' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {s.step}
                  </span>
                  <span>{s.label}</span>
                  {s.step < 6 && <ChevronRight className="w-3 h-3 text-slate-400" />}
                </button>
              );
            })}
          </div>

          {/* Reset Demo Button */}
          <button
            onClick={resetDemo}
            className="flex items-center gap-1 px-2.5 py-1 rounded text-xs text-slate-300 hover:text-slate-200 bg-slate-800/60 hover:bg-slate-800 border border-slate-700/50 transition-colors"
            title="Reset scenario to initial state"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Reset Demo</span>
          </button>
        </div>
      </div>
    </header>
  );
};
