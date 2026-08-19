"use client";

import React, { useState } from "react";
import { api } from "@/lib/api";
import { useTerminalStore } from "@/lib/store";
import { SignalBadge } from "@/components/Widgets";
import {
  Bot,
  CheckCircle2,
  Cpu,
  Layers,
  LineChart,
  MessageSquare,
  PieChart,
  Send,
  ShieldCheck,
  Sparkles,
  TrendingUp,
} from "lucide-react";

export default function AIAssistantPage() {
  const { selectedSymbol, setSelectedSymbol } = useTerminalStore();
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Copilot Chat
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; text: string }>>([
    {
      role: "assistant",
      text: "Quantara AI Multi-Agent Copilot active. Ask quantitative research questions or trigger comprehensive multi-agent synthesis on any asset.",
    },
  ]);
  const [inputQuery, setInputQuery] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const data = await api.analyzeSymbolAI(selectedSymbol);
      setReport(data);
    } catch (err: any) {
      alert("AI Analysis Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputQuery.trim() || chatLoading) return;

    const userMsg = inputQuery;
    setInputQuery("");
    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
    setChatLoading(true);

    try {
      const res = await api.copilotChat(userMsg, selectedSymbol);
      setMessages((prev) => [...prev, { role: "assistant", text: res.content }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Error connecting to AI intelligence services." },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
            <Bot className="w-5 h-5 text-cyan-400" />
            MULTI-AGENT FINANCIAL RESEARCH SYSTEM
          </h1>
          <p className="text-xs text-slate-400">
            Specialized autonomous agents: Market Analyst, Fundamental Analyst, Sentiment Analyst, Quant Analyst, Risk Analyst, and Synthesizer.
          </p>
        </div>

        <button
          onClick={handleGenerateReport}
          disabled={loading}
          className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono font-bold text-xs px-4 py-2 rounded flex items-center gap-1.5 transition-all shadow-lg"
        >
          <Sparkles className="w-3.5 h-3.5" />
          {loading ? "Synthesizing 5 Agents..." : `Synthesize Thesis for ${selectedSymbol}`}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left 2 Cols: 5 Specialist Agent Report */}
        <div className="lg:col-span-2 space-y-4">
          {report ? (
            <div className="space-y-4">
              {/* Executive Synthesis Banner */}
              <div className="terminal-panel p-4 border-cyan-500/30 bg-slate-900/90 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-base text-slate-100">{report.symbol} SYNTHESIS</span>
                    <SignalBadge direction={report.overall_direction} confidence={report.overall_confidence} />
                  </div>
                  <div className="text-xs font-mono text-cyan-400 font-bold">
                    Target: ${report.actionable_levels?.take_profit} | Stop: ${report.actionable_levels?.stop_loss}
                  </div>
                </div>
                <p className="text-xs font-mono text-slate-200 leading-relaxed">{report.executive_summary}</p>
                <div className="text-[11px] font-mono text-slate-400 bg-slate-950 p-2.5 rounded border border-slate-800">
                  <strong>THESIS:</strong> {report.synthesis_thesis}
                </div>
              </div>

              {/* 5 Specialist Sub-Agent Panels */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {/* 1. Market Analyst */}
                <div className="terminal-panel p-3 space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-mono font-bold text-cyan-300">
                    <span className="flex items-center gap-1.5"><LineChart className="w-3.5 h-3.5" /> MARKET ANALYST</span>
                    <span className="text-[10px] text-emerald-400">{report.market_analyst.stance}</span>
                  </div>
                  <div className="text-xs font-medium text-slate-200">{report.market_analyst.headline}</div>
                  <ul className="text-[11px] font-mono text-slate-400 space-y-1">
                    {report.market_analyst.key_findings?.map((f: string, i: number) => (
                      <li key={i}>• {f}</li>
                    ))}
                  </ul>
                </div>

                {/* 2. Fundamental Analyst */}
                <div className="terminal-panel p-3 space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-mono font-bold text-cyan-300">
                    <span className="flex items-center gap-1.5"><PieChart className="w-3.5 h-3.5" /> FUNDAMENTAL ANALYST</span>
                    <span className="text-[10px] text-emerald-400">{report.fundamental_analyst.stance}</span>
                  </div>
                  <div className="text-xs font-medium text-slate-200">{report.fundamental_analyst.headline}</div>
                  <ul className="text-[11px] font-mono text-slate-400 space-y-1">
                    {report.fundamental_analyst.key_findings?.map((f: string, i: number) => (
                      <li key={i}>• {f}</li>
                    ))}
                  </ul>
                </div>

                {/* 3. Sentiment Analyst */}
                <div className="terminal-panel p-3 space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-mono font-bold text-cyan-300">
                    <span className="flex items-center gap-1.5"><MessageSquare className="w-3.5 h-3.5" /> SENTIMENT ANALYST</span>
                    <span className="text-[10px] text-emerald-400">{report.sentiment_analyst.stance}</span>
                  </div>
                  <div className="text-xs font-medium text-slate-200">{report.sentiment_analyst.headline}</div>
                  <ul className="text-[11px] font-mono text-slate-400 space-y-1">
                    {report.sentiment_analyst.key_findings?.map((f: string, i: number) => (
                      <li key={i}>• {f}</li>
                    ))}
                  </ul>
                </div>

                {/* 4. Quant Analyst */}
                <div className="terminal-panel p-3 space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-mono font-bold text-cyan-300">
                    <span className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5" /> QUANT ANALYST</span>
                    <span className="text-[10px] text-emerald-400">{report.quant_analyst.stance}</span>
                  </div>
                  <div className="text-xs font-medium text-slate-200">{report.quant_analyst.headline}</div>
                  <ul className="text-[11px] font-mono text-slate-400 space-y-1">
                    {report.quant_analyst.key_findings?.map((f: string, i: number) => (
                      <li key={i}>• {f}</li>
                    ))}
                  </ul>
                </div>

                {/* 5. Risk Analyst */}
                <div className="terminal-panel p-3 space-y-1.5 md:col-span-2">
                  <div className="flex items-center justify-between text-xs font-mono font-bold text-cyan-300">
                    <span className="flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> RISK ANALYST</span>
                    <span className="text-[10px] text-emerald-400">PASSED</span>
                  </div>
                  <div className="text-xs font-medium text-slate-200">{report.risk_analyst.headline}</div>
                  <ul className="text-[11px] font-mono text-slate-400 space-y-1">
                    {report.risk_analyst.key_findings?.map((f: string, i: number) => (
                      <li key={i}>• {f}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <div className="terminal-panel p-12 text-center text-slate-500 font-mono text-xs space-y-3">
              <Bot className="w-10 h-10 mx-auto text-cyan-500/40" />
              <div>Click "Synthesize Thesis for {selectedSymbol}" above to run all 5 specialist AI research agents.</div>
            </div>
          )}
        </div>

        {/* Right 1 Col: Conversational Copilot Chat */}
        <div className="terminal-panel p-3.5 flex flex-col h-[580px]">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-2 mb-2 font-mono text-xs font-bold text-slate-200">
            <Bot className="w-4 h-4 text-cyan-400" />
            AI RESEARCH COPILOT
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 font-mono text-xs">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`p-2.5 rounded ${
                  m.role === "user"
                    ? "bg-cyan-500/10 border border-cyan-500/20 text-cyan-200 ml-4"
                    : "bg-slate-900/80 border border-slate-800 text-slate-300 mr-4"
                }`}
              >
                <div className="text-[10px] text-slate-500 font-bold mb-1 uppercase">
                  {m.role === "user" ? "You" : "Quantara Agent"}
                </div>
                <div className="whitespace-pre-wrap leading-relaxed">{m.text}</div>
              </div>
            ))}
            {chatLoading && (
              <div className="text-[11px] text-slate-500 font-mono italic animate-pulse">
                Querying quantitative datastores...
              </div>
            )}
          </div>

          {/* Input Form */}
          <form onSubmit={handleSendMessage} className="pt-2 border-t border-slate-800 flex gap-2">
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder="Ask about regimes, backtest metrics..."
              className="flex-1 bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 font-mono"
            />
            <button
              type="submit"
              disabled={chatLoading}
              className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 p-2 rounded transition-colors"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
