"""
QUANTARA Broker Abstraction Interface
Standard interface for Paper, Alpaca, Interactive Brokers, and generic broker execution.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List, Optional
from packages.domain.models import Order, OrderStatus, Portfolio, Position, Quote


class BrokerAdapter(ABC):
    """Abstract Broker Interface to isolate strategy and execution engines from broker APIs."""

    @abstractmethod
    async def connect(self) -> bool:
        """Establish session or WebSocket connection with broker."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully terminate connection."""
        pass

    @abstractmethod
    async def get_account(self) -> Portfolio:
        """Fetch current portfolio, balances, buying power, and realized P&L."""
        pass

    @abstractmethod
    async def get_positions(self) -> Dict[str, Position]:
        """Fetch all currently open positions."""
        pass

    @abstractmethod
    async def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """Retrieve historical and active orders."""
        pass

    @abstractmethod
    async def place_order(self, order: Order) -> Order:
        """Submit a new order to the broker."""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> Order:
        """Cancel an open order."""
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> Quote:
        """Fetch real-time top-of-book quote."""
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """Return connectivity status."""
        pass
