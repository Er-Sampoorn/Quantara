"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Bot, CheckCircle2, MessageSquare, ScrollText, Sparkles, Tag, TrendingUp } from "lucide-react";

export default function JournalPage() {
  const [entries, setEntries] = useState<any[]>([]);

  useEffect(() => {
    const loadJournal = async () => {
      try {
        const data = await api.getJournal();
        setEntries(data);
      } catch (err) {
        console.error(err);
      }
    };
    loadJournal();
  }, []);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
          <ScrollText className="w-5 h-5 text-cyan-400" />
          AUTOMATED AI TRADE JOURNAL & POST-MORTEM LOG
        </h1>
        <p className="text-xs text-slate-400">
          Autonomous post-trade psychological and execution review: Did execution follow rules? Was slippage controlled? What can be improved?
        </p>
      </div>

      {/* Journal Entries Feed */}
      <div className="space-y-3">
        {entries.map((entry) => {
          const isWin = entry.pnl >= 0;
          return (
            <div key={entry.id} className="terminal-panel p-4 space-y-3">
              {/* Entry Header */}
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-2">
                <div className="flex items-center gap-3">
                  <span className="font-mono font-bold text-base text-slate-100">{entry.symbol}</span>
                  <span className="text-xs font-mono text-cyan-400">{entry.strategy_name}</span>
                  <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                    Regime: {entry.regime}
                  </span>
                </div>

                <div className="flex items-center gap-3 font-mono">
                  <div className="text-right">
                    <div className="text-[10px] text-slate-500">REALIZED P&L</div>
                    <div className={`text-sm font-bold ${isWin ? "text-emerald-400" : "text-rose-400"}`}>
                      {isWin ? "+" : ""}${entry.pnl.toFixed(2)} ({(entry.pnl_pct * 100).toFixed(1)}%)
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Post Mortem Review */}
              <div className="p-3 rounded bg-slate-900/80 border border-slate-800 space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-cyan-400">
                  <Bot className="w-4 h-4" />
                  AI QUANTITATIVE POST-MORTEM REVIEW
                </div>
                <p className="text-xs font-mono text-slate-300 leading-relaxed">
                  {entry.ai_post_mortem}
                </p>
              </div>

              {/* Lessons Learned & Tags */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs font-mono">
                <div className="flex items-center gap-2">
                  <span className="text-slate-500 text-[11px]">LESSONS:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {entry.lessons_learned?.map((lesson: string, idx: number) => (
                      <span key={idx} className="bg-slate-900 border border-slate-800 text-slate-300 px-2 py-0.5 rounded text-[11px]">
                        {lesson}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-1">
                  {entry.tags?.map((t: string, idx: number) => (
                    <span key={idx} className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                      #{t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
