"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BarChart3,
  Bot,
  Compass,
  Cpu,
  FileSpreadsheet,
  FolderKanban,
  Layers,
  LayoutDashboard,
  LineChart,
  PieChart,
  Radio,
  ScrollText,
  Settings,
  ShieldAlert,
  Sparkles,
  Zap,
} from "lucide-react";

const NAV_ITEMS = [
  { label: "Command Center", href: "/dashboard", icon: LayoutDashboard },
  { label: "Live Markets", href: "/markets", icon: LineChart },
  { label: "Signal Fusion", href: "/signals", icon: Zap, badge: "LIVE" },
  { label: "Strategy Lab", href: "/strategy-lab", icon: Cpu, badge: "DSL" },
  { label: "Strategies", href: "/strategies", icon: Layers },
  { label: "Backtest Studio", href: "/backtests", icon: BarChart3 },
  { label: "Optimization", href: "/optimization", icon: Sparkles },
  { label: "Multi-Agent AI", href: "/ai", icon: Bot, badge: "5 AGENTS" },
  { label: "Quant Screener", href: "/screener", icon: Compass },
  { label: "Portfolio Risk", href: "/portfolio", icon: PieChart },
  { label: "Hard Risk Gate", href: "/risk", icon: ShieldAlert },
  { label: "Execution Blotter", href: "/orders", icon: Activity },
  { label: "AI Trade Journal", href: "/journal", icon: ScrollText },
  { label: "Research Studio", href: "/research", icon: FolderKanban },
  { label: "Brokers & Feeds", href: "/brokers", icon: Radio },
  { label: "System Health", href: "/system", icon: Settings },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#0c1222] border-r border-slate-800/80 flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="h-14 border-b border-slate-800/80 px-4 flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 font-mono font-bold text-sm">
              Q
            </div>
            <span className="font-mono font-bold text-base tracking-wider text-slate-100">
              QUANTARA<span className="text-cyan-400 text-xs ml-1">AI</span>
            </span>
          </Link>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            PAPER
          </span>
        </div>

        {/* Navigation Links */}
        <div className="py-3 px-2 overflow-y-auto max-h-[calc(100vh-140px)] space-y-0.5">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-semibold"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? "text-cyan-400" : "text-slate-400"}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[9px] font-mono font-semibold px-1 py-0.2 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </div>
      </div>

      {/* Footer System Status */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-900/40">
        <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>CORE READY</span>
          </div>
          <span className="text-slate-500">v1.0.0</span>
        </div>
      </div>
    </aside>
  );
};
