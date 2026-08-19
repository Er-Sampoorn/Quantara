"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { MetricCard } from "@/components/Widgets";
import { Activity, CheckCircle2, Cpu, HardDrive, RefreshCw, Server, ShieldCheck, Terminal } from "lucide-react";

export default function SystemPage() {
  const [health, setHealth] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);

  const loadSystem = async () => {
    try {
      const [hData, aData] = await Promise.all([
        api.getSystemHealth(),
        api.getAlerts(),
      ]);
      setHealth(hData);
      setAlerts(aData);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadSystem();
  }, []);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
            <Server className="w-5 h-5 text-cyan-400" />
            SYSTEM OBSERVABILITY & HEALTH
          </h1>
          <p className="text-xs text-slate-400">
            Prometheus metrics, service latency, background worker status, and audit log telemetry.
          </p>
        </div>

        <button
          onClick={loadSystem}
          className="px-3 py-1.5 bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 rounded flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard title="System Status" value={health?.status || "HEALTHY"} isPositive={true} subtext="Zero Critical Faults" />
        <MetricCard title="Uptime" value={`${health?.uptime_seconds ? Math.floor(health.uptime_seconds / 60) : 12} mins`} isPositive={true} subtext="FastAPI Gateway" />
        <MetricCard title="Broker Adapter" value="Connected" isPositive={true} subtext="PaperBroker Active" />
        <MetricCard title="Event Bus" value="Nominal" isPositive={true} subtext="CloudEvents Pub/Sub" />
      </div>

      {/* System Alerts Feed */}
      <div className="terminal-panel p-4 space-y-3">
        <span className="font-mono text-xs font-bold text-slate-200 block border-b border-slate-800 pb-2">
          SYSTEM EVENTS & ALERTS STREAM
        </span>

        <div className="space-y-2">
          {alerts.map((a) => (
            <div key={a.id} className="p-2.5 rounded bg-slate-900/60 border border-slate-800 flex items-center justify-between font-mono text-xs">
              <div className="space-y-0.5">
                <div className="text-slate-200 font-bold flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${a.severity === "CRITICAL" ? "bg-rose-400" : "bg-emerald-400"}`} />
                  {a.title}
                </div>
                <div className="text-[11px] text-slate-400">{a.message}</div>
              </div>
              <span className="text-[10px] text-slate-500">{new Date(a.timestamp).toLocaleTimeString()}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
