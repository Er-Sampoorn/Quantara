"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { MetricCard, RiskBadge } from "@/components/Widgets";
import { AlertOctagon, CheckCircle2, Lock, RotateCcw, ShieldAlert, ShieldCheck } from "lucide-react";

export default function RiskPage() {
  const [riskStatus, setRiskStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadRisk = async () => {
    try {
      const data = await api.getRiskStatus();
      setRiskStatus(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadRisk();
  }, []);

  const handleResetBreaker = async () => {
    setLoading(true);
    try {
      await api.resetCircuitBreaker();
      await loadRisk();
    } catch (err: any) {
      alert("Error resetting circuit breaker: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-cyan-400" />
            DETERMINISTIC PRE-TRADE RISK HARD GATE
          </h1>
          <p className="text-xs text-slate-400">
            Hard validation boundary. Every simulated or live order is evaluated against hard risk parameters before broker submission.
          </p>
        </div>

        <RiskBadge isSafe={!riskStatus?.circuit_breaker_tripped} />
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard
          title="Circuit Breaker"
          value={riskStatus?.circuit_breaker_tripped ? "TRIPPED" : "ARMED"}
          isPositive={!riskStatus?.circuit_breaker_tripped}
          subtext={riskStatus?.circuit_breaker_reason || "All systems nominal"}
        />
        <MetricCard
          title="Max Single Allocation"
          value={`${((riskStatus?.max_position_size_pct || 0.20) * 100).toFixed(0)}%`}
          isPositive={true}
          subtext="Per-asset equity cap"
        />
        <MetricCard
          title="Max Portfolio Leverage"
          value={`${riskStatus?.max_portfolio_leverage || 1.5}x`}
          isPositive={true}
          subtext="Current: 1.0x"
        />
        <MetricCard
          title="Max Drawdown Limit"
          value={`${((riskStatus?.max_drawdown_limit_pct || 0.15) * 100).toFixed(0)}%`}
          isPositive={true}
          subtext="Hard Circuit Threshold"
        />
      </div>

      {/* Risk Rules Verification Matrix */}
      <div className="terminal-panel p-4 space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2">
          <span className="font-mono text-xs font-bold text-slate-200">
            ACTIVE PRE-TRADE RISK VERIFICATION GATES
          </span>
          {riskStatus?.circuit_breaker_tripped && (
            <button
              onClick={handleResetBreaker}
              disabled={loading}
              className="bg-rose-500 hover:bg-rose-400 text-white font-mono font-bold text-xs px-3 py-1 rounded flex items-center gap-1.5 transition-all"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Circuit Breaker
            </button>
          )}
        </div>

        <div className="space-y-2">
          {[
            { name: "Single Asset Exposure Gate", limit: "20.0% of Portfolio Equity", desc: "Prevents overconcentration in single ticker symbols", status: "PASS" },
            { name: "Gross Leverage Limit", limit: "1.50x Total Exposure", desc: "Guarantees account cannot exceed borrowing safety limits", status: "PASS" },
            { name: "Daily Loss Circuit Breaker", limit: "4.0% Max 24-hour Drawdown", desc: "Freezes new order submission if daily losses exceed threshold", status: "PASS" },
            { name: "Max Concurrently Open Positions", limit: "15 Open Positions", desc: "Limits open inventory operational risk", status: "PASS" },
            { name: "Slippage & Liquidity Protection", limit: "50 bps Max Spread", desc: "Rejects market orders during illiquid spread spikes", status: "PASS" },
          ].map((rule, idx) => (
            <div key={idx} className="p-3 rounded bg-slate-900/60 border border-slate-800 flex items-center justify-between font-mono text-xs">
              <div className="space-y-0.5">
                <div className="text-slate-100 font-bold flex items-center gap-2">
                  <Lock className="w-3.5 h-3.5 text-cyan-400" />
                  {rule.name}
                </div>
                <div className="text-[11px] text-slate-500">{rule.desc}</div>
              </div>
              <div className="text-right">
                <div className="text-cyan-300 font-semibold">{rule.limit}</div>
                <div className="text-emerald-400 text-[10px] font-bold flex items-center justify-end gap-1">
                  <CheckCircle2 className="w-3 h-3" /> ACTIVE GATE
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
