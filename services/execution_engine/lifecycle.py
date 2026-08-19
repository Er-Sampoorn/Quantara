"""
QUANTARA Order Execution & Lifecycle Manager
Guarantees idempotent order dispatch, pre-trade risk gating, broker routing, and event publishing.
"""

from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from packages.brokers.base import BrokerAdapter
from packages.brokers.paper import PaperBroker
from packages.domain.models import (
    ExecutionMode,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    Portfolio,
    Position,
)
from packages.events.bus import default_event_bus
from packages.events.types import DomainEvent, EventType
from packages.risk.engine import RiskEngine, default_risk_engine

logger = logging.getLogger("quantara.execution_engine")


class ExecutionEngine:
    """Manages order creation, pre-trade risk validation, broker routing, and lifecycle states."""

    def __init__(
        self,
        broker: Optional[BrokerAdapter] = None,
        risk_engine: Optional[RiskEngine] = None,
        live_trading_enabled: bool = False,
    ):
        self.broker = broker or PaperBroker()
        self.risk_engine = risk_engine or default_risk_engine
        self.live_trading_enabled = live_trading_enabled
        self.orders: Dict[str, Order] = {}
        self.idempotency_map: Dict[str, str] = {}  # idempotency_key -> order_id

    async def submit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        strategy_id: Optional[str] = None,
        execution_mode: ExecutionMode = ExecutionMode.PAPER,
        idempotency_key: Optional[str] = None,
    ) -> Order:
        now = datetime.now(timezone.utc)
        
        # 1. Idempotency Check
        if idempotency_key and idempotency_key in self.idempotency_map:
            existing_id = self.idempotency_map[idempotency_key]
            logger.info(f"Duplicate order submission detected for idempotency key {idempotency_key}; returning existing order {existing_id}")
            return self.orders[existing_id]

        # 2. Live Trading Safety Gate
        if execution_mode == ExecutionMode.LIVE and not self.live_trading_enabled:
            raise PermissionError("Live trading is DISABLED globally. Explicit ENABLE_LIVE_TRADING=true is required.")

        # Create Order Entity
        order = Order(
            symbol=symbol.upper(),
            side=side,
            order_type=order_type,
            quantity=quantity,
            limit_price=limit_price,
            stop_price=stop_price,
            strategy_id=strategy_id,
            execution_mode=execution_mode,
            idempotency_key=idempotency_key or str(now.timestamp()),
            status=OrderStatus.CREATED,
            created_at=now,
            updated_at=now
        )
        self.orders[order.id] = order
        if idempotency_key:
            self.idempotency_map[idempotency_key] = order.id

        await default_event_bus.publish(DomainEvent(
            event_type=EventType.ORDER_CREATED,
            payload={"order_id": order.id, "symbol": order.symbol, "side": order.side.value, "quantity": order.quantity}
        ))

        # 3. Pre-Trade Risk Gate Validation
        order.status = OrderStatus.RISK_CHECK
        account_portfolio = await self.broker.get_account()
        quote = await self.broker.get_quote(order.symbol)
        
        risk_eval = self.risk_engine.evaluate_order(order, account_portfolio, quote.last_price)
        if not risk_eval.approved:
            order.status = OrderStatus.REJECTED
            order.rejection_reason = "; ".join(risk_eval.rejected_reasons)
            order.updated_at = datetime.now(timezone.utc)
            
            await default_event_bus.publish(DomainEvent(
                event_type=EventType.RISK_CHECK_FAILED,
                payload={"order_id": order.id, "reasons": risk_eval.rejected_reasons}
            ))
            return order

        await default_event_bus.publish(DomainEvent(
            event_type=EventType.RISK_CHECK_PASSED,
            payload={"order_id": order.id}
        ))

        # 4. Route to Broker Adapter
        order.status = OrderStatus.SUBMITTED
        order.updated_at = datetime.now(timezone.utc)
        
        placed_order = await self.broker.place_order(order)
        self.orders[order.id] = placed_order

        if placed_order.status == OrderStatus.FILLED:
            await default_event_bus.publish(DomainEvent(
                event_type=EventType.ORDER_FILLED,
                payload={
                    "order_id": placed_order.id,
                    "symbol": placed_order.symbol,
                    "fill_price": placed_order.average_fill_price,
                    "quantity": placed_order.filled_quantity,
                    "fees": placed_order.fees
                }
            ))

        return placed_order

    async def cancel_order(self, order_id: str) -> Order:
        if order_id not in self.orders:
            raise ValueError(f"Order {order_id} not found in execution registry.")
        cancelled = await self.broker.cancel_order(order_id)
        self.orders[order_id] = cancelled
        
        await default_event_bus.publish(DomainEvent(
            event_type=EventType.ORDER_CANCELLED,
            payload={"order_id": order_id}
        ))
        return cancelled

    def get_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)

    def get_all_orders(self) -> List[Order]:
        return list(self.orders.values())


# Global Singleton Execution Engine Instance
default_execution_engine = ExecutionEngine()
