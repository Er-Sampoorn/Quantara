"""
QUANTARA Broker Connectivity & Live Trading Safeguards API Router
"""

from __future__ import annotations
import os
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from packages.brokers.alpaca import AlpacaBrokerAdapter
from packages.brokers.paper import PaperBroker
from packages.domain.models import ExecutionMode
from packages.shared.crypto import default_vault
from services.execution_engine.lifecycle import default_execution_engine

router = APIRouter(prefix="/brokers", tags=["Brokers"])


class ConnectBrokerRequest(BaseModel):
    broker_type: str = "paper"  # paper, alpaca
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    paper_mode: bool = True


class LiveTradingToggleRequest(BaseModel):
    enable_live_trading: bool
    confirmation_phrase: str  # Must match 'I UNDERSTAND THE FINANCIAL RISKS'


@router.get("/status")
async def get_broker_status():
    is_conn = await default_execution_engine.broker.is_connected()
    return {
        "active_broker": default_execution_engine.broker.__class__.__name__,
        "is_connected": is_conn,
        "live_trading_enabled": default_execution_engine.live_trading_enabled,
        "execution_mode": "LIVE" if default_execution_engine.live_trading_enabled else "PAPER",
    }


@router.post("/connect")
async def connect_broker(req: ConnectBrokerRequest):
    if req.broker_type.lower() == "alpaca":
        adapter = AlpacaBrokerAdapter(
            api_key=req.api_key,
            secret_key=req.secret_key,
            paper=req.paper_mode
        )
        await adapter.connect()
        default_execution_engine.broker = adapter
        return {
            "success": True,
            "broker": "AlpacaBrokerAdapter",
            "paper_mode": req.paper_mode,
            "message": "Alpaca broker adapter connected successfully."
        }
    else:
        paper = PaperBroker()
        await paper.connect()
        default_execution_engine.broker = paper
        return {
            "success": True,
            "broker": "PaperBroker",
            "paper_mode": True,
            "message": "Paper matching simulator active."
        }


@router.post("/live-mode")
async def toggle_live_trading(req: LiveTradingToggleRequest):
    if req.enable_live_trading:
        if req.confirmation_phrase != "I UNDERSTAND THE FINANCIAL RISKS":
            raise HTTPException(
                status_code=400,
                detail="Confirmation phrase mismatch. You must explicitly type: 'I UNDERSTAND THE FINANCIAL RISKS'."
            )
        default_execution_engine.live_trading_enabled = True
        return {"live_trading_enabled": True, "status": "LIVE_TRADING_ACTIVE"}
    else:
        default_execution_engine.live_trading_enabled = False
        return {"live_trading_enabled": False, "status": "LIVE_TRADING_DISABLED"}
