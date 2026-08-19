"use client";

import React from "react";
import { ArrowDownRight, ArrowUpRight, ShieldCheck, ShieldAlert } from "lucide-react";

export const MetricCard: React.FC<{
  title: string;
  value: string | number;
  change?: string | number;
  isPositive?: boolean;
  subtext?: string;
}> = ({ title, value, change, isPositive, subtext }) => {
  return (
    <div className="terminal-panel p-3.5 flex flex-col justify-between">
      <div className="text-[11px] font-mono uppercase text-slate-400 font-medium mb-1">
        {title}
      </div>
      <div className="flex items-baseline justify-between">
        <div className="font-mono text-xl font-bold text-slate-100">{value}</div>
        {change !== undefined && (
          <div
            className={`flex items-center text-xs font-mono font-semibold ${
              isPositive ? "text-emerald-400" : "text-rose-400"
            }`}
          >
            {isPositive ? (
              <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />
            ) : (
              <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
            )}
            {change}
          </div>
        )}
      </div>
      {subtext && <div className="text-[10px] font-mono text-slate-500 mt-1">{subtext}</div>}
    </div>
  );
};

export const SignalBadge: React.FC<{ direction: string; confidence?: number }> = ({
  direction,
  confidence,
}) => {
  const dir = direction.toUpperCase();
  const isBuy = dir === "BUY";
  const isSell = dir === "SELL";

  const colorClass = isBuy
    ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/30"
    : isSell
    ? "bg-rose-500/15 text-rose-300 border-rose-500/30"
    : "bg-slate-800 text-slate-300 border-slate-700";

  return (
    <div className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-xs font-mono font-bold ${colorClass}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${isBuy ? "bg-emerald-400" : isSell ? "bg-rose-400" : "bg-slate-400"}`} />
      <span>{dir}</span>
      {confidence !== undefined && (
        <span className="text-[10px] opacity-80 font-normal">({(confidence * 100).toFixed(0)}%)</span>
      )}
    </div>
  );
};

export const RegimeIndicator: React.FC<{ regime: string; confidence?: number }> = ({
  regime,
  confidence,
}) => {
  const reg = regime.toUpperCase();
  const isBull = reg === "BULL" || reg === "BREAKOUT" || reg === "RECOVERY";
  const isBear = reg === "BEAR" || reg === "PANIC";

  const badgeColor = isBull
    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
    : isBear
    ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
    : "bg-amber-500/10 text-amber-400 border-amber-500/30";

  return (
    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded border text-xs font-mono font-bold ${badgeColor}`}>
      <span>REGIME: {reg}</span>
      {confidence !== undefined && (
        <span className="text-[10px] opacity-75 font-normal">{(confidence * 100).toFixed(0)}% CONF</span>
      )}
    </div>
  );
};

export const RiskBadge: React.FC<{ isSafe: boolean; label?: string }> = ({ isSafe, label }) => {
  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-xs font-mono ${
        isSafe
          ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/20"
          : "bg-rose-500/15 text-rose-300 border-rose-500/30"
      }`}
    >
      {isSafe ? <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> : <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />}
      <span className="font-semibold">{label || (isSafe ? "RISK GATE PASSED" : "CIRCUIT BREAKER")}</span>
    </div>
  );
};
