"""
QUANTARA Risk Engine & Hard Gate API Router
"""

from __future__ import annotations
from typing import Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from packages.domain.models import RiskRule
from packages.risk.engine import default_risk_engine
from services.execution_engine.lifecycle import default_execution_engine

router = APIRouter(prefix="/risk", tags=["Risk"])


class CircuitBreakerRequest(BaseModel):
    reason: str = "Manual override circuit breaker trigger"


@router.get("/status")
async def get_risk_status():
    portfolio = await default_execution_engine.broker.get_account()
    return {
        "circuit_breaker_tripped": default_risk_engine.circuit_breaker_tripped,
        "circuit_breaker_reason": default_risk_engine.circuit_breaker_reason,
        "max_position_size_pct": default_risk_engine.max_position_size_pct,
        "max_portfolio_leverage": default_risk_engine.max_portfolio_leverage,
        "daily_loss_limit_pct": default_risk_engine.daily_loss_limit_pct,
        "max_drawdown_limit_pct": default_risk_engine.max_drawdown_limit_pct,
        "max_open_positions": default_risk_engine.max_open_positions,
        "current_drawdown_pct": portfolio.drawdown_pct,
        "current_leverage": portfolio.leverage,
        "open_positions_count": len(portfolio.positions),
        "hard_gate_active": True,
    }


@router.post("/circuit-breaker/trip")
async def trip_breaker(req: CircuitBreakerRequest):
    default_risk_engine.trip_circuit_breaker(req.reason)
    return {"status": "TRIPPED", "reason": req.reason}


@router.post("/circuit-breaker/reset")
async def reset_breaker():
    default_risk_engine.reset_circuit_breaker()
    return {"status": "RESET", "circuit_breaker_tripped": False}
