"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Activity,
  Bot,
  Compass,
  Cpu,
  LineChart,
  PieChart,
  Search,
  ShieldAlert,
  Sparkles,
  Zap,
} from "lucide-react";
import { useTerminalStore } from "@/lib/store";

const ACTIONS = [
  { label: "Analyze AAPL with AI Multi-Agent", icon: Bot, path: "/ai?symbol=AAPL" },
  { label: "Analyze NVDA with AI Multi-Agent", icon: Bot, path: "/ai?symbol=NVDA" },
  { label: "Open Strategy Lab (NL Builder)", icon: Cpu, path: "/strategy-lab" },
  { label: "Run Walk-Forward Optimization", icon: Sparkles, path: "/optimization" },
  { label: "Run Quant Momentum Screener", icon: Compass, path: "/screener" },
  { label: "View Signal Fusion Feed", icon: Zap, path: "/signals" },
  { label: "Check Hard Risk Gate Status", icon: ShieldAlert, path: "/risk" },
  { label: "Review Portfolio Allocation", icon: PieChart, path: "/portfolio" },
  { label: "Open Execution Order Blotter", icon: Activity, path: "/orders" },
  { label: "View Live Candlestick Charts", icon: LineChart, path: "/markets" },
];

export const CommandPalette: React.FC = () => {
  const router = useRouter();
  const { isCommandPaletteOpen, setCommandPaletteOpen } = useTerminalStore();
  const [query, setQuery] = useState("");

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setCommandPaletteOpen(!isCommandPaletteOpen);
      }
      if (e.key === "Escape" && isCommandPaletteOpen) {
        setCommandPaletteOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isCommandPaletteOpen, setCommandPaletteOpen]);

  if (!isCommandPaletteOpen) return null;

  const filtered = ACTIONS.filter((a) =>
    a.label.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (path: string) => {
    setCommandPaletteOpen(false);
    setQuery("");
    router.push(path);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-start justify-center pt-24">
      <div className="w-full max-w-xl bg-[#0f172a] border border-slate-700 rounded-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3 border-b border-slate-800 bg-slate-900/60">
          <Search className="w-4 h-4 text-cyan-400 mr-3" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a symbol, strategy, or action..."
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none font-mono"
            autoFocus
          />
          <kbd className="text-[10px] font-mono bg-slate-800 px-1.5 py-0.5 rounded text-slate-400 border border-slate-700">
            ESC
          </kbd>
        </div>

        {/* Action Items List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.map((item, idx) => {
            const Icon = item.icon;
            return (
              <button
                key={idx}
                onClick={() => handleSelect(item.path)}
                className="w-full flex items-center justify-between px-3 py-2.5 rounded-md text-xs text-slate-300 hover:text-cyan-300 hover:bg-cyan-500/10 border border-transparent hover:border-cyan-500/20 text-left transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 text-cyan-400" />
                  <span className="font-medium">{item.label}</span>
                </div>
                <span className="text-[10px] font-mono text-slate-500">JUMP</span>
              </button>
            );
          })}
          {filtered.length === 0 && (
            <div className="py-8 text-center text-xs text-slate-500 font-mono">
              No matching commands found.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
