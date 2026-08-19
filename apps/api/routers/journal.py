"""
QUANTARA Automated AI Trade Journal API Router
"""

from __future__ import annotations
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter
from packages.domain.models import JournalEntry, RegimeType

router = APIRouter(prefix="/journal", tags=["Journal"])

JOURNAL_STORE: List[JournalEntry] = [
    JournalEntry(
        id="jrn_1",
        trade_id="trd_demo_1",
        symbol="NVDA",
        strategy_name="RSI Mean Reversion (NVDA)",
        pnl=1420.50,
        pnl_pct=0.071,
        regime=RegimeType.BREAKOUT,
        execution_quality_score=0.96,
        slippage_cost=12.40,
        rule_compliance=True,
        ai_post_mortem="Exemplary trade execution. Position entered immediately after RSI broke back above 30 in alignment with positive hardware demand. Exit triggered cleanly at target level without emotional hesitation.",
        lessons_learned=["Breakout regime supports letting winners run to take-profit band", "Slippage was minimal (< 2 bps)"],
        tags=["WINNER", "RSI", "DISCIPLINED"]
    ),
    JournalEntry(
        id="jrn_2",
        trade_id="trd_demo_2",
        symbol="AAPL",
        strategy_name="SMA Trend Alpha (AAPL)",
        pnl=890.00,
        pnl_pct=0.038,
        regime=RegimeType.BULL,
        execution_quality_score=0.92,
        slippage_cost=8.10,
        rule_compliance=True,
        ai_post_mortem="Golden cross entry followed cleanly. Position sized conservatively via ATR volatility model. Trade closed on scheduled profit target.",
        lessons_learned=["SMA 10/30 crossover captured clean trending leg"],
        tags=["TREND", "BULL"]
    ),
    JournalEntry(
        id="jrn_3",
        trade_id="trd_demo_3",
        symbol="TSLA",
        strategy_name="Bollinger Band Volatility Reversal (TSLA)",
        pnl=-410.00,
        pnl_pct=-0.021,
        regime=RegimeType.HIGH_VOLATILITY,
        execution_quality_score=0.98,
        slippage_cost=15.00,
        rule_compliance=True,
        ai_post_mortem="Controlled loss. Stop-loss was strictly honored at 2.1% drawdown, preventing a potential -8% adverse trend continuation. High volatility regime produced rapid whipsaw.",
        lessons_learned=["Tight stop-loss prevented major capital drawdown in High Volatility regime"],
        tags=["CONTROLLED_LOSS", "RISK_PRESERVED"]
    )
]


@router.get("", response_model=List[JournalEntry])
async def list_journal_entries():
    return JOURNAL_STORE


@router.get("/{journal_id}", response_model=JournalEntry)
async def get_journal_entry(journal_id: str):
    for j in JOURNAL_STORE:
        if j.id == journal_id:
            return j
    return JOURNAL_STORE[0]
