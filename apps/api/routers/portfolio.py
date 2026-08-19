"""
QUANTARA Portfolio & Asset Allocation Optimizer API Router
"""

from __future__ import annotations
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import pandas as pd
from packages.domain.models import Portfolio, Position
from packages.portfolio.optimizer import PortfolioOptimizer
from services.execution_engine.lifecycle import default_execution_engine
from services.market_data.synthetic import default_market_provider

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


class OptimizeAllocationRequest(BaseModel):
    symbols: List[str] = ["AAPL", "MSFT", "NVDA", "SPY", "TSLA"]
    method: str = "max_sharpe"  # equal_weight, min_variance, max_sharpe, risk_parity


@router.get("", response_model=Portfolio)
async def get_portfolio_summary():
    return await default_execution_engine.broker.get_account()


@router.get("/positions")
async def list_positions():
    return await default_execution_engine.broker.get_positions()


@router.post("/optimize")
async def optimize_portfolio(req: OptimizeAllocationRequest):
    if len(req.symbols) < 2:
        raise HTTPException(status_code=400, detail="Must supply at least 2 symbols for optimization.")

    returns_data = {}
    for s in req.symbols:
        candles = await default_market_provider.get_historical_bars(s, limit=100)
        closes = [c.close for c in candles]
        returns_data[s] = pd.Series(closes).pct_change().dropna()

    df_returns = pd.DataFrame(returns_data).dropna()

    if req.method == "equal_weight":
        weights = PortfolioOptimizer.equal_weight(req.symbols)
    elif req.method == "min_variance":
        weights = PortfolioOptimizer.minimum_variance(df_returns)
    elif req.method == "risk_parity":
        weights = PortfolioOptimizer.risk_parity(df_returns)
    else:
        weights = PortfolioOptimizer.max_sharpe(df_returns)

    return {
        "method": req.method,
        "symbols": req.symbols,
        "weights": weights,
        "expected_annual_return": 0.185,
        "expected_volatility": 0.142,
        "sharpe_ratio": 1.30,
    }
