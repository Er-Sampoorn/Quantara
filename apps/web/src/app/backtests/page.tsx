"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { MetricCard } from "@/components/Widgets";
import {
  Area,
  BarChart3,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ArrowRight, Download, Layers, Play, RotateCcw } from "lucide-react";

export default function BacktestsPage() {
  const [backtests, setBacktests] = useState<any[]>([]);
  const [selectedResult, setSelectedResult] = useState<any>(null);
  const [running, setRunning] = useState(false);

  // Form controls
  const [strategyType, setStrategyType] = useState("sma_crossover");
  const [symbol, setSymbol] = useState("AAPL");
  const [capital, setCapital] = useState(100000);

  const loadBacktests = async () => {
    try {
      const data = await api.getBacktests();
      setBacktests(data);
      if (data.length > 0) {
        setSelectedResult(data[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadBacktests();
  }, []);

  const handleRunBacktest = async () => {
    setRunning(true);
    try {
      const res = await api.runBacktest({
        strategy_type: strategyType,
        symbol: symbol,
        timeframe: "1D",
        initial_capital: capital,
      });
      setSelectedResult(res);
      await loadBacktests();
    } catch (err: any) {
      alert("Backtest run error: " + err.message);
    } finally {
      setRunning(false);
    }
  };

  const chartData = selectedResult?.equity_curve?.map((ep: any) => ({
    date: typeof ep.timestamp === "string" ? ep.timestamp.slice(0, 10) : new Date(ep.timestamp).toISOString().slice(0, 10),
    equity: ep.equity,
    drawdown: ep.drawdown_pct * 100,
  })) || [];

  const m = selectedResult?.metrics;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-cyan-400" />
            EVENT-DRIVEN BACKTEST STUDIO
          </h1>
          <p className="text-xs text-slate-400">
            Strict deterministic simulation with tick-level order matching, fee models, slippage, and zero look-ahead bias.
          </p>
        </div>

        {selectedResult?.reproducibility_hash && (
          <span className="text-[10px] font-mono text-slate-400 bg-slate-900 border border-slate-800 px-2 py-1 rounded">
            HASH: <strong className="text-cyan-400">{selectedResult.reproducibility_hash}</strong>
          </span>
        )}
      </div>

      {/* Backtest Configuration Bar */}
      <div className="terminal-panel p-3.5 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3 font-mono text-xs">
          <div>
            <label className="block text-[10px] text-slate-400 mb-0.5">Strategy</label>
            <select
              value={strategyType}
              onChange={(e) => setStrategyType(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded px-2.5 py-1 text-slate-200 focus:outline-none"
            >
              <option value="sma_crossover">SMA Crossover</option>
              <option value="ema_crossover">EMA Crossover</option>
              <option value="rsi_mean_reversion">RSI Mean Reversion</option>
              <option value="macd_momentum">MACD Momentum</option>
              <option value="bollinger_mean_reversion">Bollinger Band Reversion</option>
              <option value="multi_factor_fusion">Multi-Factor Fusion</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-slate-400 mb-0.5">Symbol</label>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded px-2.5 py-1 text-slate-200 focus:outline-none"
            >
              <option value="AAPL">AAPL</option>
              <option value="NVDA">NVDA</option>
              <option value="MSFT">MSFT</option>
              <option value="SPY">SPY</option>
              <option value="TSLA">TSLA</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-slate-400 mb-0.5">Initial Capital ($)</label>
            <input
              type="number"
              value={capital}
              onChange={(e) => setCapital(Number(e.target.value))}
              className="bg-slate-900 border border-slate-800 rounded px-2.5 py-1 text-slate-200 w-28 focus:outline-none"
            />
          </div>
        </div>

        <button
          onClick={handleRunBacktest}
          disabled={running}
          className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-mono font-bold text-xs px-4 py-2 rounded flex items-center gap-1.5 transition-all shadow-lg"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          {running ? "Simulating..." : "Run Backtest"}
        </button>
      </div>

      {/* Metrics Row */}
      {m && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          <MetricCard title="Total Return" value={`$${m.total_return.toLocaleString()}`} change={`${(m.total_return_pct * 100).toFixed(2)}%`} isPositive={m.total_return >= 0} />
          <MetricCard title="CAGR" value={`${(m.cagr * 100).toFixed(2)}%`} isPositive={m.cagr >= 0} subtext="Compounded Annual" />
          <MetricCard title="Sharpe Ratio" value={m.sharpe_ratio.toFixed(2)} isPositive={m.sharpe_ratio >= 1.0} subtext={`Sortino: ${m.sortino_ratio.toFixed(2)}`} />
          <MetricCard title="Max Drawdown" value={`${(m.max_drawdown_pct * 100).toFixed(2)}%`} change={`-$${m.max_drawdown.toLocaleString()}`} isPositive={false} subtext={`Calmar: ${m.calmar_ratio.toFixed(2)}`} />
          <MetricCard title="Win Rate" value={`${(m.win_rate * 100).toFixed(1)}%`} change={`${m.winning_trades}W / ${m.losing_trades}L`} isPositive={m.win_rate >= 0.5} subtext={`Trades: ${m.total_trades}`} />
          <MetricCard title="Profit Factor" value={m.profit_factor.toFixed(2)} isPositive={m.profit_factor >= 1.5} subtext={`Expectancy: $${m.expectancy.toFixed(0)}`} />
        </div>
      )}

      {/* Equity & Drawdown Chart */}
      <div className="terminal-panel p-4 space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2">
          <span className="font-mono text-xs font-bold text-slate-200">
            PORTFOLIO EQUITY CURVE (USD)
          </span>
          <span className="text-xs font-mono text-slate-400">
            Final Equity: <strong className="text-cyan-400">${selectedResult?.final_equity?.toLocaleString()}</strong>
          </span>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10, fontFamily: "monospace" }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 10, fontFamily: "monospace" }} domain={["auto", "auto"]} tickFormatter={(v) => `$${v.toLocaleString()}`} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const p = payload[0].payload;
                    return (
                      <div className="bg-[#0f172a] border border-slate-700 p-2 rounded text-xs font-mono">
                        <div>Date: {p.date}</div>
                        <div className="text-cyan-400 font-bold">Equity: ${p.equity.toLocaleString()}</div>
                        <div className="text-rose-400">Drawdown: -{p.drawdown.toFixed(2)}%</div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Area type="monotone" dataKey="equity" stroke="#06b6d4" fill="url(#colorCyan)" strokeWidth={2} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Trade Blotter Log */}
      <div className="terminal-panel p-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
          <span className="font-mono text-xs font-bold text-slate-200">
            SIMULATED TRADE EXECUTION LOG ({selectedResult?.trades?.length || 0} TRADES)
          </span>
        </div>

        <div className="overflow-x-auto max-h-60 overflow-y-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-slate-800/80">
                <th className="pb-2">Side</th>
                <th className="pb-2">Entry Date</th>
                <th className="pb-2">Entry $</th>
                <th className="pb-2">Exit Date</th>
                <th className="pb-2">Exit $</th>
                <th className="pb-2">Qty</th>
                <th className="pb-2 text-right">P&L ($)</th>
                <th className="pb-2 text-right">Return</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {selectedResult?.trades && selectedResult.trades.length > 0 ? (
                selectedResult.trades.map((t: any, idx: number) => {
                  const isWin = t.pnl > 0;
                  return (
                    <tr key={idx} className="hover:bg-slate-800/30">
                      <td className="py-2 text-emerald-400 font-bold">{t.side}</td>
                      <td className="py-2 text-slate-400">{t.entry_time ? String(t.entry_time).slice(0, 10) : "---"}</td>
                      <td className="py-2 text-slate-300">${t.entry_price.toFixed(2)}</td>
                      <td className="py-2 text-slate-400">{t.exit_time ? String(t.exit_time).slice(0, 10) : "---"}</td>
                      <td className="py-2 text-slate-300">${t.exit_price.toFixed(2)}</td>
                      <td className="py-2 text-slate-400">{t.quantity}</td>
                      <td className={`py-2 text-right font-bold ${isWin ? "text-emerald-400" : "text-rose-400"}`}>
                        {isWin ? "+" : ""}${t.pnl.toFixed(2)}
                      </td>
                      <td className={`py-2 text-right font-semibold ${isWin ? "text-emerald-400" : "text-rose-400"}`}>
                        {isWin ? "+" : ""}{(t.pnl_pct * 100).toFixed(2)}%
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={8} className="py-4 text-center text-slate-500">
                    No trades simulated in this period.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
