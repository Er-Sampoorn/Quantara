"""
QUANTARA Strategies & Natural Language Strategy Builder API Router
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from packages.domain.models import StrategySpec
from packages.strategies.registry import StrategyRegistry
from services.strategy_engine.compiler import NaturalLanguageStrategyParser, StrategyCompiler
from services.strategy_engine.dsl import StrategyDSLValidator

router = APIRouter(prefix="/strategies", tags=["Strategies"])


class NLStrategyRequest(BaseModel):
    prompt: str
    symbol: str = "AAPL"


class ValidateDSLRequest(BaseModel):
    spec: Dict[str, Any]


# In-memory store for active strategies
STRATEGIES_STORE: Dict[str, StrategySpec] = {
    "strat_sma_cross_aapl": StrategySpec(
        id="strat_sma_cross_aapl",
        name="SMA Trend Alpha (AAPL)",
        description="Fast (10) and Slow (30) Simple Moving Average crossover strategy on Apple Inc.",
        symbol="AAPL",
        symbols=["AAPL"],
        timeframe="1D",
        parameters={"fast_period": 10, "slow_period": 30}
    ),
    "strat_rsi_reversion_nvda": StrategySpec(
        id="strat_rsi_reversion_nvda",
        name="RSI Mean Reversion (NVDA)",
        description="Oversold rebound strategy triggering when 14-period RSI recovers above 30.",
        symbol="NVDA",
        symbols=["NVDA"],
        timeframe="1D",
        parameters={"rsi_period": 14, "oversold_threshold": 30.0, "overbought_threshold": 70.0}
    ),
    "strat_bollinger_spy": StrategySpec(
        id="strat_bollinger_spy",
        name="Bollinger Band Volatility Reversal (SPY)",
        description="Mean-reverting volatility band strategy trading statistical excursions.",
        symbol="SPY",
        symbols=["SPY"],
        timeframe="1D",
        parameters={"period": 20, "num_std": 2.0}
    ),
    "strat_multi_fusion_msft": StrategySpec(
        id="strat_multi_fusion_msft",
        name="Multi-Factor Fusion (MSFT)",
        description="Multi-factor synthesis strategy combining moving average trends, RSI momentum, and ADX strength.",
        symbol="MSFT",
        symbols=["MSFT"],
        timeframe="1D",
        parameters={}
    )
}


@router.get("", response_model=List[StrategySpec])
async def list_strategies():
    return list(STRATEGIES_STORE.values())


@router.get("/templates")
async def list_templates():
    return StrategyRegistry.list_available_strategies()


@router.get("/{strategy_id}", response_model=StrategySpec)
async def get_strategy(strategy_id: str):
    if strategy_id not in STRATEGIES_STORE:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return STRATEGIES_STORE[strategy_id]


@router.post("", response_model=StrategySpec)
async def create_strategy(spec: StrategySpec):
    if not spec.id:
        spec = spec.model_copy(update={"id": f"strat_{uuid.uuid4().hex[:8]}"})
    STRATEGIES_STORE[spec.id] = spec
    return spec


@router.post("/compile-nl", response_model=StrategySpec)
async def compile_natural_language_strategy(req: NLStrategyRequest):
    """
    Translates plain-English prompts into structured, validated StrategySpec AST.
    e.g. 'Buy when RSI crosses above 30 and price is above EMA 200. Exit when RSI reaches 70. Risk 1% per trade.'
    """
    try:
        spec, _ = StrategyCompiler.compile_from_prompt(req.prompt, req.symbol)
        STRATEGIES_STORE[spec.id] = spec
        return spec
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate")
async def validate_strategy_dsl(req: ValidateDSLRequest):
    is_valid, errors = StrategyDSLValidator.validate_spec(req.spec)
    return {"valid": is_valid, "errors": errors}


@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: str):
    if strategy_id in STRATEGIES_STORE:
        del STRATEGIES_STORE[strategy_id]
        return {"success": True, "message": f"Strategy {strategy_id} deleted"}
    raise HTTPException(status_code=404, detail="Strategy not found")
