"""
QUANTARA Multi-Factor Screener API Router
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
from services.ai_engine.tools import FinancialTools
from services.market_data.synthetic import SyntheticDataProvider, default_market_provider

router = APIRouter(prefix="/screener", tags=["Screener"])


class ScreenerFilterRequest(BaseModel):
    min_rsi: Optional[float] = None
    max_rsi: Optional[float] = None
    regime: Optional[str] = None
    min_growth_yoy: Optional[float] = None
    max_pe: Optional[float] = None
    min_volume: Optional[float] = None
    natural_language_query: Optional[str] = None


@router.get("/run")
async def run_screener(
    min_rsi: Optional[float] = Query(None),
    max_rsi: Optional[float] = Query(None),
    regime: Optional[str] = Query(None),
    min_growth: Optional[float] = Query(None),
):
    symbols = ["AAPL", "MSFT", "NVDA", "SPY", "QQQ", "TSLA", "BTC/USD", "ETH/USD"]
    results = []

    for sym in symbols:
        summary = await FinancialTools.get_market_summary(sym)
        fund = FinancialTools.get_fundamental_metrics(sym)
        
        # Apply filters
        if min_rsi is not None and summary["rsi_14"] < min_rsi:
            continue
        if max_rsi is not None and summary["rsi_14"] > max_rsi:
            continue
        if regime is not None and summary["regime"].upper() != regime.upper():
            continue
        if min_growth is not None and fund.get("revenue_growth_yoy", 0) < min_growth:
            continue

        results.append({
            "symbol": sym,
            "price": summary["last_price"],
            "change_24h_pct": summary["change_24h_pct"],
            "regime": summary["regime"],
            "rsi_14": summary["rsi_14"],
            "adx_14": summary["adx_14"],
            "volatility": summary["volatility"],
            "pe_ratio": fund.get("pe_ratio"),
            "revenue_growth_yoy": fund.get("revenue_growth_yoy"),
            "profit_margin": fund.get("profit_margin"),
        })

    return results


@router.post("/query")
async def run_natural_language_screen(req: ScreenerFilterRequest):
    # If natural language query provided, parse conditions
    min_rsi = req.min_rsi
    if req.natural_language_query:
        nl = req.natural_language_query.lower()
        if "momentum" in nl:
            min_rsi = 50.0

    symbols = ["AAPL", "MSFT", "NVDA", "SPY", "QQQ", "TSLA"]
    matches = []
    for s in symbols:
        summary = await FinancialTools.get_market_summary(s)
        fund = FinancialTools.get_fundamental_metrics(s)
        if min_rsi and summary["rsi_14"] < min_rsi:
            continue
        matches.append({
            "symbol": s,
            "price": summary["last_price"],
            "change_24h_pct": summary["change_24h_pct"],
            "regime": summary["regime"],
            "rsi_14": summary["rsi_14"],
            "pe_ratio": fund.get("pe_ratio"),
            "growth_yoy": fund.get("revenue_growth_yoy"),
        })
    return {"matches": matches, "query": req.natural_language_query}
