"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Cpu, Layers, Play, Plus, Sliders, Zap } from "lucide-react";

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStrategies = async () => {
      try {
        const data = await api.getStrategies();
        setStrategies(data);
      } catch (err) {
        console.error("Failed to load strategies:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStrategies();
  }, []);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
            <Layers className="w-5 h-5 text-cyan-400" />
            STRATEGY REGISTRY & CATALOG
          </h1>
          <p className="text-xs text-slate-400">
            Deterministic quantitative strategies configured for backtesting, paper simulation, and live execution.
          </p>
        </div>

        <Link
          href="/strategy-lab"
          className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono font-bold text-xs px-3.5 py-2 rounded flex items-center gap-1.5 transition-all"
        >
          <Plus className="w-3.5 h-3.5" />
          Create New Strategy (NL)
        </Link>
      </div>

      {/* Strategies Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {strategies.map((strat) => (
          <div key={strat.id} className="terminal-panel p-4 flex flex-col justify-between space-y-3">
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                  {strat.symbol}
                </span>
                <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">
                  {strat.timeframe || "1D"}
                </span>
              </div>

              <h3 className="font-mono font-bold text-sm text-slate-100 mb-1">{strat.name}</h3>
              <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                {strat.description || "Quantitative multi-condition algorithmic strategy."}
              </p>
            </div>

            {/* Parameters */}
            <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800/80 text-[11px] font-mono text-slate-400 space-y-1">
              <div className="text-slate-500 text-[10px] uppercase font-bold">Parameters</div>
              <div className="grid grid-cols-2 gap-1 text-slate-300">
                {Object.entries(strat.parameters || {}).map(([k, v]) => (
                  <div key={k} className="truncate">
                    {k}: <span className="text-cyan-300">{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2 pt-1">
              <Link
                href={`/backtests`}
                className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono font-semibold py-2 rounded flex items-center justify-center gap-1.5 transition-colors border border-slate-700"
              >
                <Play className="w-3.5 h-3.5 fill-current text-emerald-400" />
                Backtest
              </Link>
              <Link
                href="/strategy-lab"
                className="px-3 py-2 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded border border-slate-800 transition-colors"
                title="Edit Strategy"
              >
                <Sliders className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
