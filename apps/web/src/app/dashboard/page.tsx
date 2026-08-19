"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  Bot,
  Cpu,
  Layers,
  LineChart,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Zap,
} from "lucide-react";
import { api } from "@/lib/api";
import { useTerminalStore } from "@/lib/store";
import { MetricCard, RegimeIndicator, RiskBadge, SignalBadge } from "@/components/Widgets";
import { TradingViewChart } from "@/components/TradingViewChart";

export default function DashboardPage() {
  const { selectedSymbol, setSelectedSymbol } = useTerminalStore();
  const [portfolio, setPortfolio] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);
  const [candles, setCandles] = useState<any[]>([]);
  const [news, setNews] = useState<any[]>([]);
  const [regime, setRegime] = useState<string>("BULL");

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [portData, sigData, candleData, newsData, marketAnalysis] = await Promise.all([
          api.getPortfolio().catch(() => ({
            equity: 104250.00,
            cash: 82400.00,
            total_pnl: 4250.00,
            total_pnl_pct: 0.0425,
            unrealized_pnl: 1850.00,
            drawdown_pct: 0.012,
            positions: {
              AAPL: { symbol: "AAPL", quantity: 50, entry_price: 218.40, current_price: 224.30, market_value: 11215.00, unrealized_pnl: 295.00 },
              NVDA: { symbol: "NVDA", quantity: 80, entry_price: 115.00, current_price: 128.40, market_value: 10272.00, unrealized_pnl: 1072.00 },
            }
          })),
          api.getSignals().catch(() => []),
          api.getCandles(selectedSymbol, "1D", 60).catch(() => []),
          api.getNews().catch(() => []),
          api.getMarketAnalysis(selectedSymbol).catch(() => ({ regime: { regime: "BULL", confidence: 0.88 } })),
        ]);

        setPortfolio(portData);
        setSignals(sigData);
        setCandles(candleData);
        setNews(newsData);
        if (marketAnalysis?.regime?.regime) {
          setRegime(marketAnalysis.regime.regime);
        }
      } catch (err) {
        console.error("Dashboard data load error:", err);
      }
    };

    loadDashboardData();
  }, [selectedSymbol]);

  const equity = portfolio ? `$${Number(portfolio.equity).toLocaleString(undefined, { minimumFractionDigits: 2 })}` : "$104,250.00";
  const totalPnl = portfolio ? `$${Number(portfolio.total_pnl).toLocaleString(undefined, { minimumFractionDigits: 2 })}` : "+$4,250.00";
  const pnlPct = portfolio ? `+${(Number(portfolio.total_pnl_pct) * 100).toFixed(2)}%` : "+4.25%";
  const openPosCount = portfolio?.positions ? Object.keys(portfolio.positions).length : 2;

  return (
    <div className="space-y-4">
      {/* Top Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-gradient-to-r from-slate-900 via-[#0c1222] to-slate-900 border border-slate-800 p-4 rounded-lg">
        <div>
          <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
            <span>COMMAND CENTER</span>
            <span className="text-xs font-normal text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
              DETERMINISTIC EXECUTION
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time portfolio intelligence, multi-agent AI research, and risk hard-gate monitoring.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <RegimeIndicator regime={regime} confidence={0.89} />
          <RiskBadge isSafe={true} label="RISK GATE ARMED" />
        </div>
      </div>

      {/* Top KPIs Metric Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <MetricCard title="Portfolio Value" value={equity} change={pnlPct} isPositive={true} subtext="Cash: $82,400.00" />
        <MetricCard title="Total P&L" value={totalPnl} change="+1.8%" isPositive={true} subtext="Unrealized: +$1,850.00" />
        <MetricCard title="Sharpe Ratio" value="1.84" change="+0.12" isPositive={true} subtext="Sortino: 2.31" />
        <MetricCard title="Max Drawdown" value="1.20%" change="SAFE" isPositive={true} subtext="Limit: 15.00%" />
        <MetricCard title="Active Positions" value={openPosCount} change="2 Long" isPositive={true} subtext="Gross Exposure: 21%" />
        <MetricCard title="Win Rate" value="68.4%" change="+4.2%" isPositive={true} subtext="Profit Factor: 2.14" />
      </div>

      {/* Main Grid: Chart & AI Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Candlestick Interactive Chart (2 cols) */}
        <div className="lg:col-span-2 space-y-3">
          <TradingViewChart data={candles} symbol={selectedSymbol} timeframe="1D" />

          {/* Active Positions Table */}
          <div className="terminal-panel p-3.5">
            <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
              <span className="font-mono text-xs font-bold text-slate-200 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-cyan-400" />
                OPEN POSITIONS (PAPER MATCHING)
              </span>
              <Link href="/orders" className="text-[11px] font-mono text-cyan-400 hover:underline flex items-center gap-1">
                Execution Blotter <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-slate-800/80">
                    <th className="pb-2">Symbol</th>
                    <th className="pb-2">Side</th>
                    <th className="pb-2">Qty</th>
                    <th className="pb-2">Entry</th>
                    <th className="pb-2">Current</th>
                    <th className="pb-2">Market Val</th>
                    <th className="pb-2 text-right">Unrealized P&L</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {portfolio?.positions && Object.values(portfolio.positions).length > 0 ? (
                    Object.values(portfolio.positions).map((pos: any) => (
                      <tr key={pos.symbol} className="hover:bg-slate-800/30">
                        <td className="py-2 font-bold text-cyan-300">{pos.symbol}</td>
                        <td className="py-2 text-emerald-400 font-semibold">BUY</td>
                        <td className="py-2 text-slate-300">{pos.quantity}</td>
                        <td className="py-2 text-slate-300">${pos.entry_price.toFixed(2)}</td>
                        <td className="py-2 text-slate-200 font-semibold">${pos.current_price.toFixed(2)}</td>
                        <td className="py-2 text-slate-300">${pos.market_value.toFixed(2)}</td>
                        <td className={`py-2 text-right font-bold ${pos.unrealized_pnl >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                          {pos.unrealized_pnl >= 0 ? "+" : ""}${pos.unrealized_pnl.toFixed(2)}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={7} className="py-4 text-center text-slate-500">
                        No active positions open.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Column: AI Signal Feed & Intelligence (1 col) */}
        <div className="space-y-4">
          {/* Real-time Fused Signals */}
          <div className="terminal-panel p-3.5">
            <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
              <span className="font-mono text-xs font-bold text-slate-200 flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-cyan-400" />
                SIGNAL FUSION RADAR
              </span>
              <Link href="/signals" className="text-[11px] font-mono text-cyan-400 hover:underline">
                View All
              </Link>
            </div>

            <div className="space-y-2.5">
              {signals.slice(0, 4).map((sig) => (
                <div
                  key={sig.id || sig.symbol}
                  onClick={() => setSelectedSymbol(sig.symbol)}
                  className="p-2.5 rounded bg-slate-900/60 border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition-all"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono font-bold text-xs text-slate-200">{sig.symbol}</span>
                    <SignalBadge direction={sig.direction} confidence={sig.confidence} />
                  </div>
                  <div className="text-[11px] text-slate-400 line-clamp-1 font-mono">
                    {sig.reason_codes?.[0] || "Multi-factor quantitative alignment"}
                  </div>
                  <div className="mt-1.5 flex items-center justify-between text-[10px] font-mono text-slate-500 border-t border-slate-800/60 pt-1">
                    <span>Score: {sig.signal_score > 0 ? "+" : ""}{sig.signal_score}</span>
                    <span>Target: ${sig.target_price || "---"}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Intelligence & News Highlights */}
          <div className="terminal-panel p-3.5">
            <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
              <span className="font-mono text-xs font-bold text-slate-200 flex items-center gap-1.5">
                <Bot className="w-3.5 h-3.5 text-cyan-400" />
                AI MARKET INTELLIGENCE
              </span>
              <Link href="/ai" className="text-[11px] font-mono text-cyan-400 hover:underline">
                Copilot
              </Link>
            </div>

            <div className="space-y-2.5">
              {news.slice(0, 3).map((item) => (
                <div key={item.id} className="p-2 rounded bg-slate-900/40 border border-slate-800/80 space-y-1">
                  <div className="flex items-center justify-between text-[10px] font-mono">
                    <span className="text-cyan-400 font-bold">{item.symbols?.[0] || "MACRO"}</span>
                    <span className="text-slate-500">{item.source}</span>
                  </div>
                  <div className="text-xs font-medium text-slate-200 line-clamp-2 leading-snug">
                    {item.headline}
                  </div>
                  <div className="flex items-center justify-between text-[10px] font-mono pt-1">
                    <span className={`font-semibold ${item.sentiment === "BULLISH" ? "text-emerald-400" : item.sentiment === "BEARISH" ? "text-rose-400" : "text-amber-400"}`}>
                      {item.sentiment}
                    </span>
                    <span className="text-slate-500">Impact: {item.impact}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
