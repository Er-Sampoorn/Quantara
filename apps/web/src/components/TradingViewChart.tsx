"use client";

import React, { useState } from "react";
import {
  Area,
  Bar,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface CandleItem {
  timestamp: string | Date;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  vwap?: number;
}

interface TradingChartProps {
  data: CandleItem[];
  symbol: string;
  timeframe?: string;
  showIndicators?: boolean;
}

export const TradingViewChart: React.FC<TradingChartProps> = ({
  data,
  symbol,
  timeframe = "1D",
  showIndicators = true,
}) => {
  const [chartType, setChartType] = useState<"candle" | "area">("candle");

  if (!data || data.length === 0) {
    return (
      <div className="h-80 w-full flex items-center justify-center border border-slate-800 rounded-lg bg-slate-900/40 text-slate-500 font-mono text-xs">
        Loading real-time candlestick series for {symbol}...
      </div>
    );
  }

  // Format data for chart display
  const chartData = data.map((d, idx) => {
    const isUp = d.close >= d.open;
    const dateStr = typeof d.timestamp === "string" ? d.timestamp.slice(5, 10) : new Date(d.timestamp).toISOString().slice(5, 10);
    return {
      date: dateStr,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
      volume: d.volume,
      vwap: d.vwap || d.close,
      isUp,
      // Bar range representation for candlesticks
      bodyBottom: Math.min(d.open, d.close),
      bodyHeight: Math.max(0.2, Math.abs(d.close - d.open)),
    };
  });

  const minPrice = Math.min(...chartData.map((d) => d.low)) * 0.98;
  const maxPrice = Math.max(...chartData.map((d) => d.high)) * 1.02;

  return (
    <div className="w-full flex flex-col bg-[#0c1222] border border-slate-800/80 rounded-lg p-3">
      {/* Chart Header Controls */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/60 mb-2">
        <div className="flex items-center gap-3">
          <span className="font-mono font-bold text-sm text-slate-100">{symbol}</span>
          <span className="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
            {timeframe}
          </span>
          <span className="text-xs font-mono text-slate-400">
            LAST: <span className="font-bold text-slate-200">${chartData[chartData.length - 1]?.close.toFixed(2)}</span>
          </span>
        </div>

        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-0.5 rounded text-xs font-mono">
          <button
            onClick={() => setChartType("candle")}
            className={`px-2 py-0.5 rounded ${chartType === "candle" ? "bg-cyan-500/20 text-cyan-300 font-semibold" : "text-slate-400 hover:text-slate-200"}`}
          >
            Bars
          </button>
          <button
            onClick={() => setChartType("area")}
            className={`px-2 py-0.5 rounded ${chartType === "area" ? "bg-cyan-500/20 text-cyan-300 font-semibold" : "text-slate-400 hover:text-slate-200"}`}
          >
            Line
          </button>
        </div>
      </div>

      {/* Main Candlestick / Area Chart */}
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10, fontFamily: "monospace" }} />
            <YAxis
              domain={[minPrice, maxPrice]}
              stroke="#64748b"
              tick={{ fontSize: 10, fontFamily: "monospace" }}
              orientation="right"
              tickFormatter={(v) => `$${v.toFixed(0)}`}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const p = payload[0].payload;
                  return (
                    <div className="bg-[#0f172a] border border-slate-700 p-2 rounded shadow-lg text-xs font-mono">
                      <div className="text-slate-400 mb-1">{p.date}</div>
                      <div className="grid grid-cols-2 gap-x-3 gap-y-0.5">
                        <span className="text-slate-400">Open:</span> <span className="text-slate-200">${p.open.toFixed(2)}</span>
                        <span className="text-slate-400">High:</span> <span className="text-slate-200">${p.high.toFixed(2)}</span>
                        <span className="text-slate-400">Low:</span> <span className="text-slate-200">${p.low.toFixed(2)}</span>
                        <span className="text-slate-400">Close:</span> <span className={p.isUp ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>${p.close.toFixed(2)}</span>
                        <span className="text-slate-400">Vol:</span> <span className="text-slate-300">{Number(p.volume).toLocaleString()}</span>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />

            {chartType === "area" ? (
              <Area type="monotone" dataKey="close" stroke="#06b6d4" fill="url(#colorCyan)" strokeWidth={2} />
            ) : (
              <>
                <Line type="monotone" dataKey="close" stroke="#06b6d4" dot={false} strokeWidth={1.5} />
                <Line type="monotone" dataKey="vwap" stroke="#f59e0b" dot={false} strokeWidth={1} strokeDasharray="3 3" />
              </>
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Sub Volume Bar Chart */}
      <div className="h-20 w-full mt-2 pt-2 border-t border-slate-800/60">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
            <XAxis dataKey="date" hide />
            <YAxis stroke="#64748b" tick={{ fontSize: 9, fontFamily: "monospace" }} orientation="right" tickFormatter={(v) => `${(v / 1e6).toFixed(0)}M`} />
            <Bar dataKey="volume" fill="#334155" opacity={0.7} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
