"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useTerminalStore } from "@/lib/store";
import { SignalBadge } from "@/components/Widgets";
import { AlertTriangle, CheckCircle2, ChevronRight, HelpCircle, Layers, ShieldCheck, Zap } from "lucide-react";

export default function SignalsPage() {
  const { setSelectedSymbol } = useTerminalStore();
  const [signals, setSignals] = useState<any[]>([]);
  const [selectedSignal, setSelectedSignal] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSignals = async () => {
      try {
        const data = await api.getSignals();
        setSignals(data);
        if (data.length > 0) {
          setSelectedSignal(data[0]);
        }
      } catch (err) {
        console.error("Failed to load signals:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSignals();
  }, []);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
          <Zap className="w-5 h-5 text-cyan-400" />
          SIGNAL FUSION & EXPLAINABLE AI RADAR
        </h1>
        <p className="text-xs text-slate-400">
          Synthesizes Technical, Fundamental, Sentiment, Quant, ML Regime, and Risk models into transparent, reproducible signals.
        </p>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Signal List (1 col) */}
        <div className="space-y-2.5">
          {signals.map((sig) => {
            const isSelected = selectedSignal?.symbol === sig.symbol;
            return (
              <div
                key={sig.symbol}
                onClick={() => {
                  setSelectedSignal(sig);
                  setSelectedSymbol(sig.symbol);
                }}
                className={`terminal-panel p-3.5 cursor-pointer transition-all ${
                  isSelected ? "border-cyan-500/50 bg-slate-900/90" : "hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-sm text-slate-100">{sig.symbol}</span>
                    <span className="text-[10px] font-mono text-slate-500">{sig.timeframe}</span>
                  </div>
                  <SignalBadge direction={sig.direction} confidence={sig.confidence} />
                </div>

                <div className="text-xs font-mono text-slate-300 line-clamp-1 mb-2">
                  {sig.reason_codes?.[0] || "Multi-modal model convergence"}
                </div>

                <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 border-t border-slate-800/80 pt-2">
                  <span>Score: <strong className={sig.signal_score > 0 ? "text-emerald-400" : "text-rose-400"}>{sig.signal_score > 0 ? "+" : ""}{sig.signal_score}</strong></span>
                  <span>Target: <strong>${sig.target_price?.toFixed(2) || "---"}</strong></span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected Signal Explainability Deep Dive (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          {selectedSignal ? (
            <div className="terminal-panel p-4 space-y-4">
              {/* Signal Top Card */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <div className="flex items-center gap-3">
                    <h2 className="text-xl font-mono font-bold text-slate-100">{selectedSignal.symbol}</h2>
                    <SignalBadge direction={selectedSignal.direction} confidence={selectedSignal.confidence} />
                  </div>
                  <div className="text-xs font-mono text-slate-400 mt-1">
                    Timestamp: {new Date(selectedSignal.timestamp).toUTCString()} | Source: {selectedSignal.source}
                  </div>
                </div>

                <div className="text-right font-mono">
                  <div className="text-[11px] text-slate-400">TARGET / STOP</div>
                  <div className="text-sm font-bold text-slate-200">
                    <span className="text-emerald-400">${selectedSignal.target_price?.toFixed(2)}</span> / <span className="text-rose-400">${selectedSignal.stop_loss_price?.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              {/* Component Factor Breakdown */}
              <div>
                <h3 className="text-xs font-mono font-bold text-slate-300 mb-2 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-cyan-400" />
                  FACTOR CONTRIBUTION BREAKDOWN
                </h3>

                <div className="space-y-2">
                  {selectedSignal.components?.map((comp: any, idx: number) => {
                    const pct = Math.abs(comp.score) * 100;
                    const isPositive = comp.score >= 0;
                    return (
                      <div key={idx} className="p-2.5 rounded bg-slate-900/50 border border-slate-800">
                        <div className="flex items-center justify-between text-xs font-mono mb-1">
                          <span className="font-bold text-slate-200 uppercase">{comp.name} ({comp.weight * 100}%)</span>
                          <span className={isPositive ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                            {isPositive ? "+" : ""}{comp.score.toFixed(2)} (Contribution: {comp.contribution > 0 ? "+" : ""}{comp.contribution.toFixed(3)})
                          </span>
                        </div>
                        <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden mb-1.5">
                          <div
                            className={`h-full ${isPositive ? "bg-emerald-400" : "bg-rose-400"}`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <div className="text-[11px] text-slate-400 font-mono">{comp.reason}</div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Reason Codes & Risk Factors */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                <div className="p-3 rounded bg-emerald-500/5 border border-emerald-500/20">
                  <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-emerald-400 mb-2">
                    <CheckCircle2 className="w-4 h-4" />
                    SUPPORTING REASONS
                  </div>
                  <ul className="space-y-1 text-xs font-mono text-slate-300">
                    {selectedSignal.reason_codes?.map((r: string, idx: number) => (
                      <li key={idx} className="flex items-center gap-1.5">
                        <span className="w-1 h-1 rounded-full bg-emerald-400" />
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="p-3 rounded bg-rose-500/5 border border-rose-500/20">
                  <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-rose-400 mb-2">
                    <AlertTriangle className="w-4 h-4" />
                    RISK CONSIDERATIONS
                  </div>
                  <ul className="space-y-1 text-xs font-mono text-slate-300">
                    {selectedSignal.risk_factors && selectedSignal.risk_factors.length > 0 ? (
                      selectedSignal.risk_factors.map((r: string, idx: number) => (
                        <li key={idx} className="flex items-center gap-1.5">
                          <span className="w-1 h-1 rounded-full bg-rose-400" />
                          <span>{r}</span>
                        </li>
                      ))
                    ) : (
                      <li className="text-slate-500">No elevated risk penalties detected.</li>
                    )}
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <div className="terminal-panel p-8 text-center text-slate-500 font-mono text-xs">
              Select a signal on the left to inspect explainability components.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
