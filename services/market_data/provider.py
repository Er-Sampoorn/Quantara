"""
QUANTARA Market Data Provider Interface
Provider-agnostic abstract base interface for real-time and historical market feeds.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
from packages.domain.models import Candle, Instrument, Quote, Tick


class MarketDataProvider(ABC):
    """Abstract interface for pluggable market data sources (Synthetic, Alpaca, Polygon, Yahoo)."""

    @abstractmethod
    async def get_instruments(self) -> List[Instrument]:
        """List all supported instruments."""
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> Quote:
        """Fetch latest top-of-book quote for symbol."""
        pass

    @abstractmethod
    async def get_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        """Fetch latest quotes for multiple symbols."""
        pass

    @abstractmethod
    async def get_historical_bars(
        self,
        symbol: str,
        timeframe: str = "1D",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 300,
    ) -> List[Candle]:
        """Fetch historical candlestick series."""
        pass

    @abstractmethod
    async def get_ticks(self, symbol: str, limit: int = 50) -> List[Tick]:
        """Fetch recent trade ticks."""
        pass
