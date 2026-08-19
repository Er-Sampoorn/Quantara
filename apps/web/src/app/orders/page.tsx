"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useTerminalStore } from "@/lib/store";
import { Activity, CheckCircle2, Play, Plus, RefreshCw, XCircle } from "lucide-react";

export default function OrdersPage() {
  const { selectedSymbol, executionMode } = useTerminalStore();
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Quick order submit state
  const [symbol, setSymbol] = useState(selectedSymbol);
  const [side, setSide] = useState<"BUY" | "SELL">("BUY");
  const [qty, setQty] = useState(10);
  const [orderType, setOrderType] = useState("MARKET");
  const [submitting, setSubmitting] = useState(false);

  const loadOrders = async () => {
    try {
      const data = await api.getOrders();
      setOrders(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadOrders();
  }, []);

  const handlePlaceOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.submitOrder({
        symbol: symbol.toUpperCase(),
        side: side,
        quantity: qty,
        order_type: orderType,
        execution_mode: executionMode,
      });
      await loadOrders();
    } catch (err: any) {
      alert("Order submission error: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancelOrder = async (orderId: string) => {
    try {
      await api.cancelOrder(orderId);
      await loadOrders();
    } catch (err: any) {
      alert("Cancellation error: " + err.message);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-slate-100 flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            EXECUTION ORDER BLOTTER
          </h1>
          <p className="text-xs text-slate-400">
            Idempotent order state lifecycle: CREATED → RISK_CHECK → SUBMITTED → FILLED.
          </p>
        </div>

        <button
          onClick={loadOrders}
          className="px-3 py-1.5 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-xs font-mono text-slate-300 rounded flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left Column: Quick Manual Order Ticket */}
        <div className="terminal-panel p-4 space-y-3">
          <h2 className="font-mono text-xs font-bold text-slate-200 border-b border-slate-800 pb-2 flex items-center gap-1.5">
            <Plus className="w-3.5 h-3.5 text-cyan-400" />
            MANUAL ORDER TICKET ({executionMode})
          </h2>

          <form onSubmit={handlePlaceOrder} className="space-y-3 font-mono text-xs">
            <div>
              <label className="block text-slate-400 mb-1">Symbol</label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-cyan-500/50"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setSide("BUY")}
                className={`py-2 rounded font-bold transition-all ${
                  side === "BUY" ? "bg-emerald-500 text-slate-950 font-bold" : "bg-slate-900 text-slate-400"
                }`}
              >
                BUY / LONG
              </button>
              <button
                type="button"
                onClick={() => setSide("SELL")}
                className={`py-2 rounded font-bold transition-all ${
                  side === "SELL" ? "bg-rose-500 text-white font-bold" : "bg-slate-900 text-slate-400"
                }`}
              >
                SELL / SHORT
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-slate-400 mb-1">Quantity</label>
                <input
                  type="number"
                  value={qty}
                  onChange={(e) => setQty(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Order Type</label>
                <select
                  value={orderType}
                  onChange={(e) => setOrderType(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none"
                >
                  <option value="MARKET">MARKET</option>
                  <option value="LIMIT">LIMIT</option>
                  <option value="STOP">STOP</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className={`w-full py-2.5 rounded font-bold text-xs mt-2 transition-all ${
                side === "BUY" ? "bg-emerald-500 hover:bg-emerald-400 text-slate-950" : "bg-rose-500 hover:bg-rose-400 text-white"
              }`}
            >
              {submitting ? "Routing..." : `Submit ${side} Order`}
            </button>
          </form>
        </div>

        {/* Right 2 Cols: Orders Table */}
        <div className="lg:col-span-2 terminal-panel p-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
            <span className="font-mono text-xs font-bold text-slate-200">
              HISTORICAL & ACTIVE ORDERS ({orders.length})
            </span>
          </div>

          <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-slate-800">
                  <th className="pb-2">Order ID</th>
                  <th className="pb-2">Symbol</th>
                  <th className="pb-2">Side</th>
                  <th className="pb-2">Qty</th>
                  <th className="pb-2">Fill Price</th>
                  <th className="pb-2">Status</th>
                  <th className="pb-2 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {orders.map((ord) => (
                  <tr key={ord.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 text-slate-400 text-[10px]">{ord.id?.slice(0, 10)}...</td>
                    <td className="py-2.5 font-bold text-cyan-300">{ord.symbol}</td>
                    <td className={`py-2.5 font-bold ${ord.side === "BUY" ? "text-emerald-400" : "text-rose-400"}`}>
                      {ord.side}
                    </td>
                    <td className="py-2.5 text-slate-200">{ord.quantity}</td>
                    <td className="py-2.5 text-slate-300">
                      {ord.average_fill_price > 0 ? `$${ord.average_fill_price.toFixed(2)}` : "---"}
                    </td>
                    <td className="py-2.5">
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                          ord.status === "FILLED"
                            ? "bg-emerald-500/15 text-emerald-400"
                            : ord.status === "REJECTED"
                            ? "bg-rose-500/15 text-rose-400"
                            : "bg-cyan-500/15 text-cyan-400"
                        }`}
                      >
                        {ord.status}
                      </span>
                    </td>
                    <td className="py-2.5 text-right">
                      {ord.status !== "FILLED" && ord.status !== "CANCELLED" && (
                        <button
                          onClick={() => handleCancelOrder(ord.id)}
                          className="text-rose-400 hover:underline text-[11px]"
                        >
                          Cancel
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
