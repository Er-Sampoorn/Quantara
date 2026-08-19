"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import {
  ArrowRight,
  CheckCircle2,
  Cpu,
  FileCode,
  Play,
  Sparkles,
  Wand2,
} from "lucide-react";

export default function StrategyLabPage() {
  const router = useRouter();
  const [prompt, setPrompt] = useState(
    "Buy when RSI crosses above 30 while price is above EMA 200. Exit when RSI reaches 70. Risk 1% per trade."
  );
  const [symbol, setSymbol] = useState("AAPL");
  const [compiledSpec, setCompiledSpec] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [validationResult, setValidationResult] = useState<any>(null);

  const handleCompile = async () => {
    setLoading(true);
    try {
      const spec = await api.compileNLStrategy(prompt, symbol);
      setCompiledSpec(spec);
      const val = await api.validateDSL(spec);
      setValidationResult(val);
    } catch (err: any) {
      alert("Compilation error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBacktest = async () => {
    if (!compiledSpec) return;
    try {
      const res = await api.runBacktest({
        strategy_id: compiledSpec.id,
        symbol: compiledSpec.symbol,
        timeframe: compiledSpec.timeframe,
        initial_capital: 100000,
      });
      router.push(`/backtests/${res.id}`);
    } catch (err: any) {
      alert("Backtest failed: " + err.message);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
          <Cpu className="w-5 h-5 text-cyan-400" />
          STRATEGY LAB & NATURAL LANGUAGE COMPILER
        </h1>
        <p className="text-xs text-slate-400">
          Transform natural language trading rules into validated Strategy DSL AST specifications and executable strategies.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left Column: Natural Language Input & Controls */}
        <div className="terminal-panel p-4 space-y-4">
          <div>
            <label className="block text-xs font-mono font-bold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Wand2 className="w-3.5 h-3.5 text-cyan-400" />
              NATURAL LANGUAGE STRATEGY SPECIFICATION
            </label>
            <textarea
              rows={4}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. Buy when RSI crosses above 30 and price is above EMA 200. Exit when RSI reaches 70. Risk 1% per trade."
              className="w-full bg-slate-900 border border-slate-800 rounded p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 font-mono leading-relaxed"
            />
          </div>

          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            <div>
              <label className="block text-slate-400 mb-1">Target Symbol</label>
              <select
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500/50"
              >
                <option value="AAPL">AAPL (Apple)</option>
                <option value="NVDA">NVDA (NVIDIA)</option>
                <option value="MSFT">MSFT (Microsoft)</option>
                <option value="SPY">SPY (S&P 500 ETF)</option>
                <option value="TSLA">TSLA (Tesla)</option>
              </select>
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Execution Timeframe</label>
              <select className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500/50">
                <option value="1D">1D (Daily Bars)</option>
                <option value="1h">1h (Hourly Bars)</option>
                <option value="15m">15m (Intraday)</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-2 pt-2">
            <button
              onClick={handleCompile}
              disabled={loading}
              className="flex-1 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono font-bold text-xs py-2.5 rounded transition-all flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              {loading ? "Compiling..." : "Compile to Strategy DSL"}
            </button>
          </div>

          {/* Prompt Presets */}
          <div className="border-t border-slate-800/80 pt-3">
            <span className="text-[11px] font-mono text-slate-500 block mb-2">QUICK PRESET PROMPTS</span>
            <div className="space-y-1.5">
              {[
                "Buy when RSI crosses above 30 while price is above EMA 200. Exit when RSI reaches 70. Risk 1% per trade.",
                "Buy when SMA 10 crosses above SMA 30. Exit when SMA 10 crosses below SMA 30. Stop loss 3%.",
                "Buy when price touches lower Bollinger band. Exit when price reaches upper Bollinger band. Take profit 4%.",
              ].map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => setPrompt(preset)}
                  className="w-full text-left p-2 rounded bg-slate-900/60 hover:bg-slate-800/60 text-[11px] font-mono text-slate-300 transition-colors truncate block"
                >
                  {preset}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Compiled AST & DSL Diagnostics */}
        <div className="terminal-panel p-4 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-mono text-xs font-bold text-slate-200 flex items-center gap-1.5">
              <FileCode className="w-3.5 h-3.5 text-cyan-400" />
              COMPILED STRATEGY DSL (JSON AST)
            </span>
            {validationResult?.valid && (
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> VALIDATED
              </span>
            )}
          </div>

          {compiledSpec ? (
            <div className="space-y-3">
              <pre className="bg-slate-950 p-3 rounded border border-slate-800 text-[11px] font-mono text-cyan-300 max-h-80 overflow-y-auto leading-relaxed">
                {JSON.stringify(compiledSpec, null, 2)}
              </pre>

              <div className="flex items-center gap-2 pt-2">
                <button
                  onClick={handleBacktest}
                  className="flex-1 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-mono font-bold text-xs py-2.5 rounded transition-all flex items-center justify-center gap-2"
                >
                  <Play className="w-4 h-4 fill-current" />
                  Run Backtest Simulation
                </button>
                <button
                  onClick={() => router.push("/optimization")}
                  className="px-4 py-2.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono font-bold border border-slate-700 transition-all"
                >
                  Optimize
                </button>
              </div>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-500 font-mono text-xs space-y-2">
              <FileCode className="w-8 h-8 opacity-40" />
              <span>Enter a prompt on the left and click "Compile" to view Strategy AST.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
