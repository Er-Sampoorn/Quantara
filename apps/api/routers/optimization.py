"""
QUANTARA Optimization, Walk-Forward, & Monte Carlo API Router
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from packages.backtesting.engine import BacktestEngine
from packages.domain.models import (
    MonteCarloSimulationResult,
    OptimizationMetric,
    OptimizationResult,
)
from packages.strategies.registry import StrategyRegistry
from services.market_data.synthetic import default_market_provider
from services.optimization_engine.monte_carlo import MonteCarloEngine
from services.optimization_engine.optimizer import StrategyOptimizer
from services.optimization_engine.walk_forward import WalkForwardEngine

router = APIRouter(prefix="/optimization", tags=["Optimization"])


class OptimizationRunRequest(BaseModel):
    strategy_type: str = "sma_crossover"
    symbol: str = "AAPL"
    parameter_grid: Dict[str, List[Any]] = {
        "fast_period": [5, 10, 15, 20],
        "slow_period": [20, 30, 40, 50]
    }
    objective: OptimizationMetric = OptimizationMetric.SHARPE
    max_trials: int = 16


class WalkForwardRequest(BaseModel):
    strategy_type: str = "sma_crossover"
    symbol: str = "AAPL"
    parameter_grid: Dict[str, List[Any]] = {
        "fast_period": [5, 10, 15],
        "slow_period": [20, 30, 40]
    }
    num_splits: int = 4


class MonteCarloRequest(BaseModel):
    strategy_type: str = "sma_crossover"
    symbol: str = "AAPL"
    num_simulations: int = 1000


@router.post("/run", response_model=OptimizationResult)
async def run_optimization(req: OptimizationRunRequest):
    candles = await default_market_provider.get_historical_bars(req.symbol, limit=300)
    if not candles:
        raise HTTPException(status_code=400, detail="Insufficient candles")
    
    result = StrategyOptimizer.optimize(
        strategy_type=req.strategy_type,
        symbol=req.symbol,
        candles=candles,
        parameter_grid=req.parameter_grid,
        objective=req.objective,
        max_trials=req.max_trials
    )
    return result


@router.post("/walk-forward")
async def run_walk_forward(req: WalkForwardRequest):
    candles = await default_market_provider.get_historical_bars(req.symbol, limit=365)
    if len(candles) < 100:
        raise HTTPException(status_code=400, detail="Requires >= 100 bars for walk-forward validation")

    return WalkForwardEngine.evaluate(
        strategy_type=req.strategy_type,
        symbol=req.symbol,
        candles=candles,
        parameter_grid=req.parameter_grid,
        num_splits=req.num_splits
    )


@router.post("/monte-carlo", response_model=MonteCarloSimulationResult)
async def run_monte_carlo(req: MonteCarloRequest):
    candles = await default_market_provider.get_historical_bars(req.symbol, limit=365)
    strat = StrategyRegistry.create_strategy(
        strategy_type=req.strategy_type,
        strategy_id="mc_seed_strat",
        name="MC Seed Strategy",
        symbol=req.symbol
    )
    engine = BacktestEngine(initial_capital=100_000.0)
    bt_res = engine.run(strat, candles)

    return MonteCarloEngine.simulate(
        trades=bt_res.trades,
        initial_capital=100_000.0,
        num_simulations=req.num_simulations
    )
