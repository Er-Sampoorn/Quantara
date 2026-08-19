"""
QUANTARA Orders & Execution Blotter API Router
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from packages.domain.models import (
    ExecutionMode,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
)
from services.execution_engine.lifecycle import default_execution_engine

router = APIRouter(prefix="/orders", tags=["Orders"])


class SubmitOrderRequest(BaseModel):
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType = OrderType.MARKET
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    strategy_id: Optional[str] = None
    execution_mode: ExecutionMode = ExecutionMode.PAPER
    idempotency_key: Optional[str] = None


@router.get("", response_model=List[Order])
async def list_orders():
    return default_execution_engine.get_all_orders()


@router.post("", response_model=Order)
async def submit_order(req: SubmitOrderRequest):
    try:
        order = await default_execution_engine.submit_order(
            symbol=req.symbol,
            side=req.side,
            quantity=req.quantity,
            order_type=req.order_type,
            limit_price=req.limit_price,
            stop_price=req.stop_price,
            strategy_id=req.strategy_id,
            execution_mode=req.execution_mode,
            idempotency_key=req.idempotency_key
        )
        return order
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{order_id}", response_model=Order)
async def cancel_order(order_id: str):
    try:
        return await default_execution_engine.cancel_order(order_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
