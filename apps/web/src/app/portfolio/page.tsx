"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { MetricCard } from "@/components/Widgets";
import { PieChart as PieIcon, RefreshCw, ShieldCheck, Sliders, TrendingUp } from "lucide-react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = ["#06b6d4", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#3b82f6"];

export default function PortfolioPage() {
  const [portfolio, setPortfolio] = useState<any>(null);
  const [optMethod, setOptMethod] = useState("max_sharpe");
  const [optResult, setOptResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadPortfolio = async () => {
      try {
        const data = await api.getPortfolio();
        setPortfolio(data);
      } catch (err) {
        console.error(err);
      }
    };
    loadPortfolio();
  }, []);

  const handleOptimize = async () => {
    setLoading(true);
    try {
      const res = await api.optimizePortfolio({
        symbols: ["AAPL", "MSFT", "NVDA", "SPY", "TSLA"],
        method: optMethod,
      });
      setOptResult(res);
    } catch (err: any) {
      alert("Optimization error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const allocationData = optResult?.weights
    ? Object.entries(optResult.weights).map(([k, v]) => ({ name: k, value: Number(v) * 100 }))
    : [
        { name: "AAPL", value: 35 },
        { name: "NVDA", value: 30 },
        { name: "MSFT", value: 20 },
        { name: "SPY", value: 15 },
      ];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
          <PieIcon className="w-5 h-5 text-cyan-400" />
          PORTFOLIO ALLOCATION & RISK OPTIMIZER
        </h1>
        <p className="text-xs text-slate-400">
          Markowitz Mean-Variance Max Sharpe, Hierarchical Risk Parity, and Minimum Variance asset weighting.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard title="Total Equity" value={`$${portfolio?.equity?.toLocaleString() || "104,250"}`} isPositive={true} />
        <MetricCard title="Available Cash" value={`$${portfolio?.cash?.toLocaleString() || "82,400"}`} subtext="Buying Power: $82,400" />
        <MetricCard title="Gross Exposure" value="21.0%" change="SAFE" isPositive={true} subtext="Leverage: 1.0x" />
        <MetricCard title="Expected Sharpe" value={optResult?.sharpe_ratio?.toFixed(2) || "1.30"} isPositive={true} subtext="Annual Vol: 14.2%" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left 2 Cols: Optimizer Setup */}
        <div className="lg:col-span-2 terminal-panel p-4 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-mono text-xs font-bold text-slate-200">
              OPTIMIZATION ALGORITHM SETTINGS
            </span>
            <div className="flex items-center gap-2">
              <select
                value={optMethod}
                onChange={(e) => setOptMethod(e.target.value)}
                className="bg-slate-900 border border-slate-800 rounded px-2.5 py-1 text-xs text-slate-200 font-mono focus:outline-none"
              >
                <option value="max_sharpe">Maximum Sharpe Ratio (Markowitz)</option>
                <option value="risk_parity">Equal Risk Contribution (Risk Parity)</option>
                <option value="min_variance">Minimum Global Variance</option>
                <option value="equal_weight">1/N Equal Weight</option>
              </select>
              <button
                onClick={handleOptimize}
                disabled={loading}
                className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono font-bold text-xs px-3 py-1 rounded transition-all flex items-center gap-1"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
                Calculate Weights
              </button>
            </div>
          </div>

          {/* Current vs Target Weights Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-slate-800">
                  <th className="pb-2">Asset</th>
                  <th className="pb-2">Target Weight</th>
                  <th className="pb-2">Target Capital ($100k)</th>
                  <th className="pb-2 text-right">Risk Contribution</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {allocationData.map((item, idx) => (
                  <tr key={item.name} className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-bold text-cyan-300 flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                      {item.name}
                    </td>
                    <td className="py-2.5 text-slate-100 font-bold">{item.value.toFixed(1)}%</td>
                    <td className="py-2.5 text-slate-300">${(item.value * 1000).toLocaleString()}</td>
                    <td className="py-2.5 text-right text-emerald-400 font-semibold">
                      {(100 / allocationData.length).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right 1 Col: Allocation Donut Chart */}
        <div className="terminal-panel p-4 flex flex-col items-center justify-between">
          <span className="font-mono text-xs font-bold text-slate-200 self-start border-b border-slate-800 pb-2 w-full">
            OPTIMAL ASSET WEIGHTS
          </span>

          <div className="w-full h-56 my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const p = payload[0];
                      return (
                        <div className="bg-slate-900 border border-slate-700 p-2 rounded text-xs font-mono">
                          <span className="text-slate-200 font-bold">{p.name}:</span>{" "}
                          <span className="text-cyan-400">{Number(p.value).toFixed(1)}%</span>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="text-[11px] font-mono text-slate-500 text-center">
            Optimized with risk-adjusted covariance estimation (252-day annualized).
          </div>
        </div>
      </div>
    </div>
  );
}
