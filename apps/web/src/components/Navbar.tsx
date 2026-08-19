"use client";

import React, { useEffect, useState } from "react";
import { Command, Search, Shield, Wifi } from "lucide-react";
import { useTerminalStore } from "@/lib/store";
import { api } from "@/lib/api";

const TICKER_SYMBOLS = ["SPY", "QQQ", "AAPL", "NVDA", "MSFT", "TSLA", "BTC/USD"];

export const Navbar: React.FC = () => {
  const { toggleCommandPalette, selectedSymbol, setSelectedSymbol } = useTerminalStore();
  const [quotes, setQuotes] = useState<Record<string, any>>({});
  const [currentTime, setCurrentTime] = useState<string>("");

  useEffect(() => {
    const fetchTicker = async () => {
      try {
        const data = await api.getQuotes(TICKER_SYMBOLS.join(","));
        setQuotes(data);
      } catch (err) {
        // Fallback demo prices if backend not yet running
        const fallback: Record<string, any> = {
          SPY: { last_price: 552.10, change_24h_pct: 0.0042 },
          QQQ: { last_price: 484.50, change_24h_pct: 0.0085 },
          AAPL: { last_price: 224.30, change_24h_pct: 0.0125 },
          NVDA: { last_price: 128.40, change_24h_pct: 0.0340 },
          MSFT: { last_price: 442.80, change_24h_pct: 0.0055 },
          TSLA: { last_price: 218.20, change_24h_pct: -0.0120 },
          "BTC/USD": { last_price: 66400.00, change_24h_pct: 0.0210 },
        };
        setQuotes(fallback);
      }
    };

    fetchTicker();
    const interval = setInterval(fetchTicker, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toUTCString().slice(17, 25) + " UTC");
    };
    updateTime();
    const tInterval = setInterval(updateTime, 1000);
    return () => clearInterval(tInterval);
  }, []);

  return (
    <header className="h-14 border-b border-slate-800/80 bg-[#090d16]/95 backdrop-blur px-4 flex items-center justify-between sticky top-0 z-30">
      {/* Real-time Ticker Bar */}
      <div className="flex items-center gap-4 overflow-x-auto no-scrollbar max-w-3xl">
        {TICKER_SYMBOLS.map((sym) => {
          const q = quotes[sym];
          const price = q ? Number(q.last_price).toFixed(sym.includes("USD") ? 0 : 2) : "---";
          const chg = q ? (q.change_24h_pct * 100).toFixed(2) : "0.00";
          const isPos = q ? q.change_24h_pct >= 0 : true;

          return (
            <button
              key={sym}
              onClick={() => setSelectedSymbol(sym)}
              className={`flex items-center gap-1.5 font-mono text-xs px-2 py-1 rounded transition-colors ${
                selectedSymbol === sym ? "bg-cyan-500/15 border border-cyan-500/30 text-cyan-300" : "hover:bg-slate-800/60 text-slate-300"
              }`}
            >
              <span className="font-bold text-slate-200">{sym}</span>
              <span>${price}</span>
              <span className={`text-[10px] font-semibold ${isPos ? "text-emerald-400" : "text-rose-400"}`}>
                {isPos ? "+" : ""}{chg}%
              </span>
            </button>
          );
        })}
      </div>

      {/* Right Controls: Command Palette & System Clock */}
      <div className="flex items-center gap-3">
        <button
          onClick={toggleCommandPalette}
          className="flex items-center gap-2 bg-slate-900 border border-slate-700/80 hover:border-cyan-500/50 px-3 py-1.5 rounded-md text-xs text-slate-400 hover:text-slate-200 transition-all font-mono"
        >
          <Search className="w-3.5 h-3.5 text-cyan-400" />
          <span>Search or Command...</span>
          <kbd className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-400 border border-slate-700">
            Ctrl K
          </kbd>
        </button>

        <div className="h-4 w-px bg-slate-800" />

        <div className="flex items-center gap-2 font-mono text-xs text-slate-400">
          <Wifi className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-[11px]">{currentTime || "LIVE"}</span>
        </div>
      </div>
    </header>
  );
};
