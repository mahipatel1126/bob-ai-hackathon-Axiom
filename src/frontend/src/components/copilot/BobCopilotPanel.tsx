import React, { useState } from 'react';
import { MessageSquareCode, Send, Sparkles, X, Bot, User, ArrowRight, ShieldCheck, RefreshCw } from 'lucide-react';
import { useDemo } from '../../context/DemoContext';
import { CopilotMessage } from '../../types/copilot';
import { StructuredAnswer } from './StructuredAnswer';
import { copilotService } from '../../services/copilotService';
import { presetCopilotQueries } from '../../mock/copilotData';

export const BobCopilotPanel: React.FC = () => {
  const { copilotOpen, setCopilotOpen, selectedShipmentId, approveReroute, assignFleetAsset } = useDemo();
  const [messages, setMessages] = useState<CopilotMessage[]>([
    {
      id: 'welcome',
      sender: 'BOB',
      timestamp: '05:54 UTC',
      content: 'ChainGuard Operations Copilot (IBM Bob) online. I am actively monitoring active disruptions, thermal telemetry, and fleet positioning. Click any scenario prompt below or enter an operational query.',
      suggested_actions: [
        'Why is SHP-1001 critical?',
        'Which idle fleet assets should we redeploy?',
        'What\'s the recommended route for SHP-1001?',
      ],
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const quickPrompts = [
    'Why is SHP-1001 critical?',
    'Which shipments are most at risk?',
    'How should we respond to the current disruption?',
    'Which idle fleet assets should we redeploy?',
    'Is any cold-chain shipment in danger?',
    'What\'s the recommended route for SHP-1001?',
  ];

  const handleSend = async (queryText: string) => {
    if (!queryText.trim() || isLoading) return;

    const userMsg: CopilotMessage = {
      id: `user-${Date.now()}`,
      sender: 'USER',
      timestamp: 'Just now',
      content: queryText,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setIsLoading(true);

    try {
      const response = await copilotService.askBob(queryText, selectedShipmentId);
      setMessages((prev) => [...prev, response]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          sender: 'BOB',
          timestamp: 'Just now',
          content: 'Error communicating with AI Copilot service. Please check network connectivity.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleActionClick = (actionText: string) => {
    if (actionText.includes('TRUCK-204') || actionText.includes('Deploy') || actionText.includes('Dispatch')) {
      assignFleetAsset();
    }
    if (actionText.includes('Route') || actionText.includes('Hazira') || actionText.includes('Divert')) {
      approveReroute();
    }
    handleSend(actionText);
  };

  if (!copilotOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[480px] lg:w-[540px] bg-[#090e1c] border-l border-slate-800 shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
      {/* Drawer Header */}
      <div className="p-4 border-b border-slate-800 bg-[#0d1428] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-br from-blue-600/30 to-cyan-500/30 border border-cyan-500/40 text-cyan-400">
            <MessageSquareCode className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-white font-mono flex items-center gap-1.5">
                <span>IBM Bob</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                  Operations Copilot
                </span>
              </h3>
            </div>
            <p className="text-[11px] text-slate-400">
              Autonomous Supply Chain Reasoning & Decision Support
            </p>
          </div>
        </div>

        <button
          onClick={() => setCopilotOpen(false)}
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Suggested Quick Prompts */}
      <div className="p-3 bg-[#0b1122] border-b border-slate-800/80 overflow-x-auto">
        <span className="text-[10px] font-mono font-bold uppercase text-slate-400 block mb-1.5">
          Tactical Operational Queries:
        </span>
        <div className="flex gap-1.5 overflow-x-auto pb-1">
          {quickPrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(prompt)}
              className="text-[11px] whitespace-nowrap px-2.5 py-1 rounded-md bg-slate-800/80 hover:bg-cyan-950/60 text-slate-300 hover:text-cyan-300 border border-slate-700/60 hover:border-cyan-500/50 transition-all font-medium shrink-0"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Message History Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => {
          const isUser = msg.sender === 'USER';
          return (
            <div
              key={msg.id}
              className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              {!isUser && (
                <div className="w-7 h-7 rounded-lg bg-cyan-950 border border-cyan-700/60 text-cyan-400 flex items-center justify-center shrink-0 mt-0.5">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div className={`max-w-[85%] rounded-xl p-3.5 text-xs font-sans ${
                isUser
                  ? 'bg-cyan-600 text-white font-medium ml-8'
                  : 'bg-slate-900 border border-slate-800 text-slate-200'
              }`}>
                {/* Header info */}
                <div className="flex items-center justify-between gap-3 text-[10px] font-mono text-slate-400 mb-1">
                  <span>{isUser ? 'OPERATOR' : 'IBM BOB COPILOT'}</span>
                  <span>{msg.timestamp}</span>
                </div>

                {/* Body text */}
                <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>

                {/* Structured Recommendation Card */}
                {msg.structured_recommendation && (
                  <StructuredAnswer
                    recommendation={msg.structured_recommendation}
                    onExecuteAction={handleActionClick}
                  />
                )}

                {/* Suggested Follow-up Actions */}
                {msg.suggested_actions && msg.suggested_actions.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-slate-800/80">
                    <span className="text-[10px] font-mono text-slate-400 uppercase font-semibold block mb-1.5">
                      Suggested Actions:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.suggested_actions.map((act, i) => (
                        <button
                          key={i}
                          onClick={() => handleActionClick(act)}
                          className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 hover:text-white text-[11px] font-medium border border-slate-700 transition-colors flex items-center gap-1"
                        >
                          <span>{act}</span>
                          <ArrowRight className="w-3 h-3 text-cyan-400" />
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {isUser && (
                <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 flex items-center justify-center shrink-0 mt-0.5">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          );
        })}

        {isLoading && (
          <div className="flex gap-3 items-center text-xs text-cyan-400 font-mono">
            <div className="w-7 h-7 rounded-lg bg-cyan-950 border border-cyan-800 text-cyan-400 flex items-center justify-center">
              <Bot className="w-4 h-4 animate-spin" />
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 flex items-center gap-2">
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Bob is evaluating multi-factor risk models and transit paths...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Box */}
      <div className="p-3.5 border-t border-slate-800 bg-[#0c1326]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(inputQuery);
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask Bob about disruptions, SHP-1001, reroutes, or idle fleet..."
            className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-500 font-sans"
          />
          <button
            type="submit"
            disabled={!inputQuery.trim() || isLoading}
            className="p-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 disabled:opacity-40 text-slate-950 font-bold transition-all shadow-sm"
            title="Submit query"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <div className="mt-1.5 flex items-center justify-between text-[10px] text-slate-500 font-mono">
          <span>Targeting Context: {selectedShipmentId}</span>
          <span>IBM watsonx Reasoning Engine</span>
        </div>
      </div>
    </div>
  );
};
