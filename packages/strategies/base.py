"""
QUANTARA Base Strategy Interface
Deterministic strategy lifecycle contract for Backtest, Paper, and Live execution.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import pandas as pd
from packages.domain.models import (
    Candle,
    Order,
    OrderSide,
    Position,
    Quote,
    Signal,
    SignalDirection,
    StrategyRiskConfig,
    Tick,
)


class BaseStrategy(ABC):
    """
    Abstract Base Class for all Quantara quantitative trading strategies.
    Ensures identical business logic is executed across Backtesting, Paper Trading, and Live Execution.
    """

    def __init__(
        self,
        strategy_id: str,
        name: str,
        symbol: str,
        symbols: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        risk_config: Optional[StrategyRiskConfig] = None,
    ):
        self.strategy_id = strategy_id
        self.name = name
        self.symbol = symbol
        self.symbols = symbols or [symbol]
        self.parameters = parameters or {}
        self.risk_config = risk_config or StrategyRiskConfig()
        
        # State tracking
        self.bars: Dict[str, List[Candle]] = {s: [] for s in self.symbols}
        self.positions: Dict[str, Position] = {}
        self.is_initialized: bool = False

    @abstractmethod
    def initialize(self) -> None:
        """Initialize indicator buffers and parameter configurations."""
        pass

    @abstractmethod
    def on_bar(self, candle: Candle) -> Optional[Signal]:
        """
        Invoked deterministically when a new historical or real-time candlestick closes.
        Returns a Signal or None.
        """
        pass

    def on_tick(self, tick: Tick) -> Optional[Signal]:
        """Optional hook for high-frequency tick processing."""
        return None

    def on_market_data(self, quote: Quote) -> Optional[Signal]:
        """Optional hook for orderbook quote updates."""
        return None

    def on_order_update(self, order: Order) -> None:
        """Hook called on order status transition."""
        pass

    def on_position_update(self, position: Position) -> None:
        """Hook called when a position is opened, updated, or closed."""
        self.positions[position.symbol] = position

    def shutdown(self) -> None:
        """Cleanup resources on strategy stop."""
        self.is_initialized = False

    def update_parameters(self, new_params: Dict[str, Any]) -> None:
        """Dynamically update strategy hyperparameters."""
        self.parameters.update(new_params)
        self.initialize()

    def get_parameter(self, key: str, default: Any = None) -> Any:
        return self.parameters.get(key, default)

    def _append_bar(self, candle: Candle) -> None:
        if candle.symbol not in self.bars:
            self.bars[candle.symbol] = []
        self.bars[candle.symbol].append(candle)
        # Keep sliding memory window
        if len(self.bars[candle.symbol]) > 1000:
            self.bars[candle.symbol].pop(0)

    def get_dataframe(self, symbol: Optional[str] = None) -> pd.DataFrame:
        sym = symbol or self.symbol
        candle_list = self.bars.get(sym, [])
        if not candle_list:
            return pd.DataFrame()
        
        data = [
            {
                "timestamp": c.timestamp,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
            }
            for c in candle_list
        ]
        df = pd.DataFrame(data)
        df.sort_values("timestamp", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
