"""
QUANTARA Signals & Signal Fusion API Router
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from packages.domain.models import Signal
from services.signal_engine.fusion import SignalFusionEngine

router = APIRouter(prefix="/signals", tags=["Signals"])

CACHED_SIGNALS: List[Signal] = []


@router.get("", response_model=List[Signal])
async def list_signals(symbols: Optional[str] = Query(None)):
    global CACHED_SIGNALS
    sym_list = [s.strip().upper() for s in symbols.split(",")] if symbols else ["AAPL", "NVDA", "MSFT", "SPY", "TSLA", "BTC/USD"]
    
    signals: List[Signal] = []
    for s in sym_list:
        sig = await SignalFusionEngine.generate_fused_signal(s)
        signals.append(sig)
        
    CACHED_SIGNALS = signals
    return signals


@router.get("/{symbol}", response_model=Signal)
async def get_signal_for_symbol(symbol: str):
    return await SignalFusionEngine.generate_fused_signal(symbol.upper())


@router.post("/analyze/{symbol}", response_model=Signal)
async def trigger_signal_analysis(symbol: str):
    return await SignalFusionEngine.generate_fused_signal(symbol.upper())
