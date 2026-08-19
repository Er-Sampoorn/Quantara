"""
QUANTARA Markets & Market Data API Router
"""

from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from packages.domain.models import Candle, Instrument, Quote, Tick
from packages.indicators.technical import TechnicalIndicators
from packages.ml.regime import MarketRegimeEngine
from services.anomaly_engine.detector import MarketAnomalyDetector
from services.market_data.synthetic import default_market_provider
import pandas as pd

router = APIRouter(prefix="/markets", tags=["Markets"])


@router.get("/instruments", response_model=List[Instrument])
async def list_instruments():
    return await default_market_provider.get_instruments()


@router.get("/quotes")
async def get_quotes(symbols: Optional[str] = Query(None, description="Comma-separated symbols")):
    sym_list = [s.strip().upper() for s in symbols.split(",")] if symbols else ["AAPL", "MSFT", "NVDA", "SPY", "QQQ", "TSLA", "BTC/USD", "ETH/USD"]
    return await default_market_provider.get_quotes(sym_list)


@router.get("/{symbol}/quote", response_model=Quote)
async def get_quote(symbol: str):
    return await default_market_provider.get_quote(symbol)


@router.get("/{symbol}/candles", response_model=List[Candle])
async def get_candles(
    symbol: str,
    timeframe: str = "1D",
    limit: int = Query(300, ge=10, le=1000)
):
    return await default_market_provider.get_historical_bars(symbol, timeframe=timeframe, limit=limit)


@router.get("/{symbol}/ticks", response_model=List[Tick])
async def get_ticks(symbol: str, limit: int = Query(50, ge=10, le=200)):
    return await default_market_provider.get_ticks(symbol, limit=limit)


@router.get("/{symbol}/analysis")
async def get_market_analysis(symbol: str):
    sym = symbol.upper()
    quote = await default_market_provider.get_quote(sym)
    candles = await default_market_provider.get_historical_bars(sym, limit=100)
    
    if not candles:
        raise HTTPException(status_code=404, detail=f"No data available for {sym}")
        
    df = pd.DataFrame([{"close": c.close, "high": c.high, "low": c.low, "volume": c.volume} for c in candles])
    regime = MarketRegimeEngine.classify_regime(df, sym)
    anomalies = MarketAnomalyDetector.scan_candles(sym, candles)
    
    indicators = TechnicalIndicators.compute_all_indicators(
        df["high"].values, df["low"].values, df["close"].values, df["volume"].values
    )
    
    latest_ind = {k: round(float(v[-1]), 4) if not pd.isna(v[-1]) else None for k, v in indicators.items()}
    
    return {
        "symbol": sym,
        "quote": quote,
        "regime": regime,
        "indicators": latest_ind,
        "anomalies": anomalies,
    }
