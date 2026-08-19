"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useTerminalStore } from "@/lib/store";
import { CheckCircle2, Lock, Radio, ShieldAlert, Wifi } from "lucide-react";

export default function BrokersPage() {
  const { executionMode, setExecutionMode } = useTerminalStore();
  const [brokerStatus, setBrokerStatus] = useState<any>(null);
  const [confirmationPhrase, setConfirmationPhrase] = useState("");
  const [loading, setLoading] = useState(false);

  const loadBroker = async () => {
    try {
      const data = await api.getBrokerStatus();
      setBrokerStatus(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadBroker();
  }, []);

  const handleToggleLive = async (enable: boolean) => {
    setLoading(true);
    try {
      await api.toggleLiveTrading(enable, confirmationPhrase);
      setExecutionMode(enable ? "LIVE" : "PAPER");
      await loadBroker();
      setConfirmationPhrase("");
      alert(`Live trading ${enable ? "ENABLED" : "DISABLED"}`);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
          <Radio className="w-5 h-5 text-cyan-400" />
          BROKER ADAPTERS & EXECUTION MODE
        </h1>
        <p className="text-xs text-slate-400">
          Manage PaperBroker matching simulator and external broker connections (Alpaca Markets).
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Paper Broker Card */}
        <div className="terminal-panel p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-mono text-sm font-bold text-slate-100">PaperBroker (Built-in Simulator)</span>
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              ACTIVE & SAFE
            </span>
          </div>
          <p className="text-xs font-mono text-slate-400 leading-relaxed">
            Deterministic internal matching engine simulating tick fills, commissions ($0.005/share), and 3 bps slippage models. Zero financial risk.
          </p>
        </div>

        {/* Alpaca Broker Adapter */}
        <div className="terminal-panel p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-mono text-sm font-bold text-slate-100">Alpaca Markets Adapter</span>
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              SANDBOX READY
            </span>
          </div>
          <p className="text-xs font-mono text-slate-400 leading-relaxed">
            Direct integration with Alpaca REST/WebSocket endpoints. Secrets encrypted via AES-GCM vault.
          </p>
        </div>
      </div>

      {/* Live Trading Guardrail Gate */}
      <div className="terminal-panel p-4 border-rose-500/30 bg-slate-900/90 space-y-3">
        <div className="flex items-center gap-2 text-rose-400 font-mono font-bold text-sm">
          <ShieldAlert className="w-5 h-5" />
          LIVE TRADING SAFETY GUARDRAIL
        </div>
        <p className="text-xs font-mono text-slate-300">
          Live trading is strictly disabled by default. Enabling live trading allows approved orders to execute real capital with the connected broker.
        </p>

        {!brokerStatus?.live_trading_enabled ? (
          <div className="space-y-2 pt-2 border-t border-slate-800 font-mono text-xs">
            <label className="block text-slate-400">
              Type <strong className="text-rose-400">I UNDERSTAND THE FINANCIAL RISKS</strong> to enable live trading:
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={confirmationPhrase}
                onChange={(e) => setConfirmationPhrase(e.target.value)}
                placeholder="I UNDERSTAND THE FINANCIAL RISKS"
                className="flex-1 bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-slate-100 focus:outline-none focus:border-rose-500"
              />
              <button
                onClick={() => handleToggleLive(true)}
                disabled={loading || confirmationPhrase !== "I UNDERSTAND THE FINANCIAL RISKS"}
                className="bg-rose-500 hover:bg-rose-400 disabled:opacity-40 text-white font-bold px-4 py-1.5 rounded transition-all"
              >
                Enable Live Trading
              </button>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between pt-2 border-t border-slate-800">
            <span className="text-xs font-mono text-rose-400 font-bold">● LIVE TRADING IS CURRENTLY ACTIVE</span>
            <button
              onClick={() => handleToggleLive(false)}
              className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-mono text-xs font-bold px-3 py-1.5 rounded"
            >
              Disable Live Trading (Safe Mode)
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
