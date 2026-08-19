"""
QUANTARA Backtesting API Router
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from packages.backtesting.engine import BacktestEngine
from packages.domain.models import BacktestResult, StrategyRiskConfig
from packages.strategies.base import BaseStrategy
from packages.strategies.registry import StrategyRegistry
from services.market_data.synthetic import default_market_provider
from services.strategy_engine.compiler import DynamicCompiledStrategy
from apps.api.routers.strategies import STRATEGIES_STORE

router = APIRouter(prefix="/backtests", tags=["Backtests"])


class BacktestRunRequest(BaseModel):
    strategy_id: Optional[str] = None
    strategy_type: Optional[str] = "sma_crossover"
    symbol: str = "AAPL"
    timeframe: str = "1D"
    initial_capital: float = 100_000.0
    parameters: Optional[Dict[str, Any]] = None
    risk_config: Optional[StrategyRiskConfig] = None


# Backtest results cache
BACKTESTS_STORE: Dict[str, BacktestResult] = {}


@router.post("/run", response_model=BacktestResult)
async def run_backtest(req: BacktestRunRequest):
    candles = await default_market_provider.get_historical_bars(req.symbol, timeframe=req.timeframe, limit=365)
    if not candles:
        raise HTTPException(status_code=400, detail=f"No candle data found for {req.symbol}")

    # Build Strategy
    if req.strategy_id and req.strategy_id in STRATEGIES_STORE:
        spec = STRATEGIES_STORE[req.strategy_id]
        if spec.entry_rules:
            strategy_inst: BaseStrategy = DynamicCompiledStrategy(spec)
        else:
            strategy_inst = StrategyRegistry.create_strategy(
                strategy_type=req.strategy_type or "sma_crossover",
                strategy_id=spec.id,
                name=spec.name,
                symbol=req.symbol,
                parameters=req.parameters or spec.parameters,
                risk_config=req.risk_config or spec.risk_config
            )
    else:
        strategy_inst = StrategyRegistry.create_strategy(
            strategy_type=req.strategy_type or "sma_crossover",
            strategy_id=f"strat_{uuid.uuid4().hex[:8]}",
            name=f"{req.strategy_type.upper()} ({req.symbol})",
            symbol=req.symbol,
            parameters=req.parameters or {},
            risk_config=req.risk_config
        )

    engine = BacktestEngine(initial_capital=req.initial_capital)
    result = engine.run(strategy_inst, candles, timeframe=req.timeframe)
    BACKTESTS_STORE[result.id] = result
    return result


@router.get("", response_model=List[BacktestResult])
async def list_backtests():
    # If empty, run a default backtest for immediate presentation
    if not BACKTESTS_STORE:
        candles = await default_market_provider.get_historical_bars("AAPL", limit=300)
        strat = StrategyRegistry.create_strategy(
            strategy_type="sma_crossover",
            strategy_id="demo_sma_aapl",
            name="SMA Crossover (AAPL)",
            symbol="AAPL",
            parameters={"fast_period": 10, "slow_period": 30}
        )
        engine = BacktestEngine(initial_capital=100_000.0)
        res = engine.run(strat, candles)
        BACKTESTS_STORE[res.id] = res

    return list(BACKTESTS_STORE.values())


@router.get("/{backtest_id}", response_model=BacktestResult)
async def get_backtest(backtest_id: str):
    if backtest_id not in BACKTESTS_STORE:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return BACKTESTS_STORE[backtest_id]
