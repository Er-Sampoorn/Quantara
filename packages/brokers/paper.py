"""
QUANTARA Deterministic Paper Broker
In-memory simulated matching engine with customizable fees, slippage, and position tracking.
"""

from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
from packages.brokers.base import BrokerAdapter
from packages.domain.models import (
    ExecutionMode,
    Fill,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    Portfolio,
    Position,
    Quote,
)


class PaperBroker(BrokerAdapter):
    """
    Production-grade paper trading broker simulator.
    Uses realistic slippage, commissions ($0.005/share or flat), and synchronous/asynchronous fill resolution.
    """

    def __init__(
        self,
        initial_cash: float = 100_000.0,
        commission_per_share: float = 0.005,
        min_commission: float = 1.0,
        slippage_bps: float = 3.0,  # 3 basis points
    ):
        self.cash: float = initial_cash
        self.initial_cash: float = initial_cash
        self.commission_per_share = commission_per_share
        self.min_commission = min_commission
        self.slippage_bps = slippage_bps
        
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.fills: List[Fill] = []
        self.quotes: Dict[str, Quote] = {}
        self._is_connected: bool = True
        self._lock = asyncio.Lock()

    async def connect(self) -> bool:
        self._is_connected = True
        return True

    async def disconnect(self) -> None:
        self._is_connected = False

    async def is_connected(self) -> bool:
        return self._is_connected

    def set_mock_quote(self, quote: Quote) -> None:
        """Update live quote price cache for simulated executions."""
        self.quotes[quote.symbol] = quote
        # Update unrealized P&L on positions
        if quote.symbol in self.positions:
            pos = self.positions[quote.symbol]
            current_price = quote.last_price
            pos.current_price = current_price
            pos.market_value = pos.quantity * current_price
            if pos.side == OrderSide.BUY:
                pos.unrealized_pnl = (current_price - pos.entry_price) * pos.quantity
            else:
                pos.unrealized_pnl = (pos.entry_price - current_price) * pos.quantity
            pos.unrealized_pnl_pct = (pos.unrealized_pnl / (pos.entry_price * pos.quantity)) if pos.entry_price > 0 else 0.0
            pos.updated_at = datetime.now(timezone.utc)

    async def get_account(self) -> Portfolio:
        async with self._lock:
            equity = self.cash
            unrealized_pnl = 0.0
            for pos in self.positions.values():
                equity += pos.market_value
                unrealized_pnl += pos.unrealized_pnl

            total_pnl = equity - self.initial_cash
            total_pnl_pct = (total_pnl / self.initial_cash) if self.initial_cash > 0 else 0.0

            return Portfolio(
                user_id="default_paper_user",
                name="Quantara Paper Portfolio",
                cash=round(self.cash, 2),
                initial_balance=round(self.initial_cash, 2),
                equity=round(equity, 2),
                unrealized_pnl=round(unrealized_pnl, 2),
                realized_pnl=round(total_pnl - unrealized_pnl, 2),
                total_pnl=round(total_pnl, 2),
                total_pnl_pct=round(total_pnl_pct, 4),
                drawdown_pct=0.0,
                positions=dict(self.positions),
                execution_mode=ExecutionMode.PAPER,
                updated_at=datetime.now(timezone.utc)
            )

    async def get_positions(self) -> Dict[str, Position]:
        async with self._lock:
            return dict(self.positions)

    async def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        async with self._lock:
            if status:
                return [o for o in self.orders.values() if o.status == status]
            return list(self.orders.values())

    async def get_quote(self, symbol: str) -> Quote:
        if symbol in self.quotes:
            return self.quotes[symbol]
        # Return sensible default quote if symbol not yet populated
        return Quote(
            symbol=symbol,
            bid_price=100.0,
            bid_size=100,
            ask_price=100.05,
            ask_size=100,
            last_price=100.0,
            timestamp=datetime.now(timezone.utc)
        )

    async def place_order(self, order: Order) -> Order:
        async with self._lock:
            # Idempotency check: if order already exists, return current state
            if order.id in self.orders:
                return self.orders[order.id]

            self.orders[order.id] = order
            order.status = OrderStatus.SUBMITTED
            order.updated_at = datetime.now(timezone.utc)

            # Resolve execution price with slippage
            quote = await self.get_quote(order.symbol)
            base_price = quote.ask_price if order.side == OrderSide.BUY else quote.bid_price
            slippage_factor = 1.0 + (self.slippage_bps / 10000.0 if order.side == OrderSide.BUY else -self.slippage_bps / 10000.0)
            exec_price = base_price * slippage_factor

            # Limit order check
            if order.order_type == OrderType.LIMIT and order.limit_price is not None:
                if order.side == OrderSide.BUY and exec_price > order.limit_price:
                    order.status = OrderStatus.ACCEPTED
                    return order
                elif order.side == OrderSide.SELL and exec_price < order.limit_price:
                    order.status = OrderStatus.ACCEPTED
                    return order

            # Commission calculation
            commission = max(self.min_commission, order.quantity * self.commission_per_share)
            cost = (exec_price * order.quantity) + commission

            # Cash availability check for BUY
            if order.side == OrderSide.BUY and self.cash < cost:
                order.status = OrderStatus.REJECTED
                order.rejection_reason = f"Insufficient cash for simulated order: required ${cost:.2f}, available ${self.cash:.2f}"
                order.updated_at = datetime.now(timezone.utc)
                return order

            # Execute Fill
            fill = Fill(
                order_id=order.id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=round(exec_price, 4),
                fee=round(commission, 4),
                slippage=round(abs(exec_price - base_price) * order.quantity, 4),
                timestamp=datetime.now(timezone.utc)
            )
            self.fills.append(fill)

            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            order.average_fill_price = round(exec_price, 4)
            order.fees = round(commission, 4)
            order.updated_at = datetime.now(timezone.utc)

            # Update cash and position
            if order.side == OrderSide.BUY:
                self.cash -= cost
                if order.symbol in self.positions:
                    pos = self.positions[order.symbol]
                    new_qty = pos.quantity + order.quantity
                    new_entry = ((pos.quantity * pos.entry_price) + (order.quantity * exec_price)) / new_qty
                    pos.quantity = new_qty
                    pos.entry_price = new_entry
                    pos.current_price = exec_price
                    pos.market_value = new_qty * exec_price
                    pos.updated_at = datetime.now(timezone.utc)
                else:
                    self.positions[order.symbol] = Position(
                        symbol=order.symbol,
                        quantity=order.quantity,
                        entry_price=exec_price,
                        current_price=exec_price,
                        market_value=order.quantity * exec_price,
                        unrealized_pnl=0.0,
                        unrealized_pnl_pct=0.0,
                        side=OrderSide.BUY,
                        opened_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc)
                    )
            elif order.side == OrderSide.SELL:
                self.cash += (exec_price * order.quantity) - commission
                if order.symbol in self.positions:
                    pos = self.positions[order.symbol]
                    if pos.quantity <= order.quantity:
                        # Position closed
                        pos.realized_pnl += (exec_price - pos.entry_price) * pos.quantity
                        del self.positions[order.symbol]
                    else:
                        pos.quantity -= order.quantity
                        pos.market_value = pos.quantity * exec_price
                        pos.realized_pnl += (exec_price - pos.entry_price) * order.quantity
                        pos.updated_at = datetime.now(timezone.utc)

            return order

    async def cancel_order(self, order_id: str) -> Order:
        async with self._lock:
            if order_id not in self.orders:
                raise ValueError(f"Order {order_id} not found.")
            order = self.orders[order_id]
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
                return order
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.now(timezone.utc)
            return order
