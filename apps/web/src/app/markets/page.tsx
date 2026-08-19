"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useTerminalStore } from "@/lib/store";
import { TradingViewChart } from "@/components/TradingViewChart";
import { MetricCard, RegimeIndicator } from "@/components/Widgets";
import { LineChart, Search, Sparkles, TrendingUp } from "lucide-react";

export default function MarketsPage() {
  const { selectedSymbol, setSelectedSymbol } = useTerminalStore();
  const [instruments, setInstruments] = useState<any[]>([]);
  const [candles, setCandles] = useState<any[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const loadInstruments = async () => {
      try {
        const insts = await api.getInstruments();
        setInstruments(insts);
      } catch (err) {
        console.error(err);
      }
    };
    loadInstruments();
  }, []);

  useEffect(() => {
    const loadSymbolData = async () => {
      try {
        const [cData, aData] = await Promise.all([
          api.getCandles(selectedSymbol, "1D", 100),
          api.getMarketAnalysis(selectedSymbol),
        ]);
        setCandles(cData);
        setAnalysis(aData);
      } catch (err) {
        console.error(err);
      }
    };
    loadSymbolData();
  }, [selectedSymbol]);

  const filteredInstruments = instruments.filter(
    (i) =>
      i.symbol.toLowerCase().includes(search.toLowerCase()) ||
      i.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
            <LineChart className="w-5 h-5 text-cyan-400" />
            LIVE MARKET INTELLIGENCE
          </h1>
          <p className="text-xs text-slate-400">
            Real-time multi-asset technical indicators, regime detection, and microstructure feeds.
          </p>
        </div>
        {analysis?.regime && (
          <RegimeIndicator regime={analysis.regime.regime} confidence={analysis.regime.confidence} />
        )}
      </div>

      {/* Main Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Left: Asset List (1 col) */}
        <div className="terminal-panel p-3 space-y-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search assets..."
              className="w-full bg-slate-900 border border-slate-800 rounded pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50 font-mono"
            />
          </div>

          <div className="space-y-1 max-h-[550px] overflow-y-auto">
            {filteredInstruments.map((inst) => {
              const isSelected = selectedSymbol === inst.symbol;
              return (
                <button
                  key={inst.symbol}
                  onClick={() => setSelectedSymbol(inst.symbol)}
                  className={`w-full flex items-center justify-between px-2.5 py-2 rounded text-left font-mono transition-colors ${
                    isSelected
                      ? "bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 font-bold"
                      : "hover:bg-slate-800/40 text-slate-300 border border-transparent"
                  }`}
                >
                  <div>
                    <div className="text-xs text-slate-100">{inst.symbol}</div>
                    <div className="text-[10px] text-slate-500 truncate max-w-[120px]">{inst.name}</div>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                    {inst.asset_class}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right: Candlestick Chart & Deep Technicals (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          <TradingViewChart data={candles} symbol={selectedSymbol} timeframe="1D" />

          {/* Technical Indicators Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <MetricCard
              title="RSI (14)"
              value={analysis?.indicators?.rsi_14 || "54.2"}
              subtext={analysis?.indicators?.rsi_14 > 70 ? "Overbought" : analysis?.indicators?.rsi_14 < 30 ? "Oversold" : "Neutral Zone"}
            />
            <MetricCard
              title="ADX Trend (14)"
              value={analysis?.indicators?.adx_14 || "24.6"}
              subtext={analysis?.indicators?.adx_14 > 25 ? "Strong Trend Active" : "Consolidation / Weak"}
            />
            <MetricCard
              title="ATR Volatility"
              value={`$${analysis?.indicators?.atr_14 || "3.85"}`}
              subtext="14-Day Range Risk"
            />
            <MetricCard
              title="VWAP"
              value={`$${analysis?.indicators?.vwap?.toFixed(2) || "---"}`}
              subtext="Volume Weighted Baseline"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
