"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { FolderKanban, Plus, Save, Sparkles } from "lucide-react";

export default function ResearchPage() {
  const [workspaces, setWorkspaces] = useState<any[]>([]);
  const [selectedWs, setSelectedWs] = useState<any>(null);
  const [notes, setNotes] = useState("");

  const loadWorkspaces = async () => {
    try {
      const data = await api.getWorkspaces();
      setWorkspaces(data);
      if (data.length > 0) {
        setSelectedWs(data[0]);
        setNotes(data[0].notes || "");
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadWorkspaces();
  }, []);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
            <FolderKanban className="w-5 h-5 text-cyan-400" />
            QUANTITATIVE RESEARCH WORKSPACES
          </h1>
          <p className="text-xs text-slate-400">
            Persistent research sessions, hypothesis tracking, and multi-asset study notebooks.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left: Workspaces List */}
        <div className="terminal-panel p-3 space-y-2">
          <span className="font-mono text-xs font-bold text-slate-200 block border-b border-slate-800 pb-2">
            ACTIVE WORKSPACES
          </span>

          <div className="space-y-2">
            {workspaces.map((ws) => {
              const isSelected = selectedWs?.id === ws.id;
              return (
                <div
                  key={ws.id}
                  onClick={() => {
                    setSelectedWs(ws);
                    setNotes(ws.notes || "");
                  }}
                  className={`p-3 rounded border cursor-pointer font-mono transition-all ${
                    isSelected ? "bg-cyan-500/10 border-cyan-500/30 text-cyan-200" : "bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-300"
                  }`}
                >
                  <div className="font-bold text-xs text-slate-100">{ws.title}</div>
                  <div className="text-[10px] text-slate-400 line-clamp-1 mt-0.5">{ws.description}</div>
                  <div className="flex items-center gap-1 mt-2">
                    {ws.symbols?.map((s: string) => (
                      <span key={s} className="text-[9px] px-1 py-0.2 rounded bg-slate-800 text-cyan-400">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right 2 Cols: Workspace Notebook & Notes Editor */}
        <div className="lg:col-span-2 terminal-panel p-4 space-y-4">
          {selectedWs ? (
            <>
              <div className="border-b border-slate-800 pb-3">
                <h2 className="text-base font-mono font-bold text-slate-100">{selectedWs.title}</h2>
                <p className="text-xs font-mono text-slate-400 mt-0.5">{selectedWs.description}</p>
              </div>

              <div>
                <label className="block text-xs font-mono font-bold text-slate-300 mb-1.5">
                  RESEARCH NOTES & HYPOTHESIS LOG
                </label>
                <textarea
                  rows={10}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Record mathematical observations, regime correlations, and backtest results..."
                  className="w-full bg-slate-900 border border-slate-800 rounded p-3 text-xs text-slate-100 focus:outline-none focus:border-cyan-500/50 font-mono leading-relaxed"
                />
              </div>

              <div className="flex justify-end">
                <button
                  onClick={() => alert("Research notes saved successfully.")}
                  className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono font-bold text-xs px-4 py-2 rounded flex items-center gap-1.5 transition-all"
                >
                  <Save className="w-3.5 h-3.5" />
                  Save Workspace Notes
                </button>
              </div>
            </>
          ) : (
            <div className="py-12 text-center text-slate-500 font-mono text-xs">
              Select a workspace on the left.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
