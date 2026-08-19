"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useTerminalStore } from "@/lib/store";
import { Compass, Filter, Search, Sparkles, TrendingUp } from "lucide-react";

export default function ScreenerPage() {
  const { setSelectedSymbol } = useTerminalStore();
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Filters
  const [minRsi, setMinRsi] = useState(30);
  const [maxRsi, setMaxRsi] = useState(70);
  const [selectedRegime, setSelectedRegime] = useState("");
  const [nlQuery, setNlQuery] = useState("");

  const handleFilter = async () => {
    setLoading(true);
    try {
      if (nlQuery.trim()) {
        const res = await api.runNLScreener(nlQuery);
        setResults(res.matches || []);
      } else {
        const queryParams = new URLSearchParams();
        if (minRsi) queryParams.append("min_rsi", String(minRsi));
        if (maxRsi) queryParams.append("max_rsi", String(maxRsi));
        if (selectedRegime) queryParams.append("regime", selectedRegime);

        const data = await api.runScreener(queryParams.toString());
        setResults(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleFilter();
  }, []);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
          <Compass className="w-5 h-5 text-cyan-400" />
          MULTI-FACTOR ASSET SCREENER
        </h1>
        <p className="text-xs text-slate-400">
          Filter thousands of instruments across technical momentum, valuation multiples, volume z-scores, and market regimes.
        </p>
      </div>

      {/* Filter Bar & Natural Language Query Box */}
      <div className="terminal-panel p-4 space-y-3">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400 absolute left-3 top-3" />
            <input
              type="text"
              value={nlQuery}
              onChange={(e) => setNlQuery(e.target.value)}
              placeholder="Natural Language Screen: e.g. 'Find high momentum assets with RSI > 50 in bull regime'..."
              className="w-full bg-slate-900 border border-slate-800 rounded pl-9 pr-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 font-mono"
            />
          </div>
          <button
            onClick={handleFilter}
            disabled={loading}
            className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono font-bold text-xs px-4 py-2 rounded transition-all"
          >
            {loading ? "Scanning..." : "Run Screen"}
          </button>
        </div>

        {/* Sliders and Selects */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 font-mono text-xs pt-1 border-t border-slate-800/80">
          <div>
            <label className="block text-slate-400 mb-1">RSI Range: {minRsi} - {maxRsi}</label>
            <div className="flex items-center gap-2">
              <input
                type="range"
                min="0"
                max="100"
                value={minRsi}
                onChange={(e) => setMinRsi(Number(e.target.value))}
                className="w-full accent-cyan-400"
              />
              <input
                type="range"
                min="0"
                max="100"
                value={maxRsi}
                onChange={(e) => setMaxRsi(Number(e.target.value))}
                className="w-full accent-cyan-400"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-400 mb-1">Market Regime</label>
            <select
              value={selectedRegime}
              onChange={(e) => setSelectedRegime(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:outline-none"
            >
              <option value="">All Regimes</option>
              <option value="BULL">BULL</option>
              <option value="BEAR">BEAR</option>
              <option value="BREAKOUT">BREAKOUT</option>
              <option value="HIGH_VOLATILITY">HIGH_VOLATILITY</option>
              <option value="SIDEWAYS">SIDEWAYS</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results Table */}
      <div className="terminal-panel p-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
          <span className="font-mono text-xs font-bold text-slate-200">
            SCREENER MATCHES ({results.length} ASSETS)
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-slate-800">
                <th className="pb-2">Symbol</th>
                <th className="pb-2">Price</th>
                <th className="pb-2">24h Chg</th>
                <th className="pb-2">Regime</th>
                <th className="pb-2">RSI(14)</th>
                <th className="pb-2">P/E Ratio</th>
                <th className="pb-2">YoY Growth</th>
                <th className="pb-2 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {results.map((r) => (
                <tr key={r.symbol} className="hover:bg-slate-800/30">
                  <td className="py-2.5 font-bold text-cyan-300">{r.symbol}</td>
                  <td className="py-2.5 text-slate-200">${Number(r.price).toFixed(2)}</td>
                  <td className={`py-2.5 font-semibold ${r.change_24h_pct >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                    {r.change_24h_pct >= 0 ? "+" : ""}{(r.change_24h_pct * 100).toFixed(2)}%
                  </td>
                  <td className="py-2.5 text-slate-300">
                    <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">
                      {r.regime}
                    </span>
                  </td>
                  <td className="py-2.5 text-slate-300">{r.rsi_14}</td>
                  <td className="py-2.5 text-slate-400">{r.pe_ratio ? `${r.pe_ratio}x` : "---"}</td>
                  <td className="py-2.5 text-emerald-400 font-medium">
                    {r.revenue_growth_yoy ? `+${(r.revenue_growth_yoy * 100).toFixed(0)}%` : r.growth_yoy ? `+${(r.growth_yoy * 100).toFixed(0)}%` : "---"}
                  </td>
                  <td className="py-2.5 text-right">
                    <button
                      onClick={() => setSelectedSymbol(r.symbol)}
                      className="text-[11px] text-cyan-400 hover:underline font-bold"
                    >
                      Select Asset
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
