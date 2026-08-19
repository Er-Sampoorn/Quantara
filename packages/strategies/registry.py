"""
QUANTARA Strategy Registry
Factory and catalog for strategy registration and instantiation.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Type
from packages.domain.models import StrategyRiskConfig
from packages.strategies.base import BaseStrategy
from packages.strategies.collection import (
    BollingerMeanReversionStrategy,
    DonchianBreakoutStrategy,
    DualMomentumStrategy,
    EMACrossoverStrategy,
    MACDMomentumStrategy,
    MultiFactorFusionStrategy,
    RSIMeanReversionStrategy,
    SMACrossoverStrategy,
    StatisticalArbitragePairsStrategy,
    TrendFollowingADXStrategy,
    VolatilityBreakoutStrategy,
    VWAPIntradayStrategy,
)


class StrategyRegistry:
    _strategies: Dict[str, Type[BaseStrategy]] = {
        "sma_crossover": SMACrossoverStrategy,
        "ema_crossover": EMACrossoverStrategy,
        "rsi_mean_reversion": RSIMeanReversionStrategy,
        "macd_momentum": MACDMomentumStrategy,
        "bollinger_mean_reversion": BollingerMeanReversionStrategy,
        "vwap_intraday": VWAPIntradayStrategy,
        "donchian_breakout": DonchianBreakoutStrategy,
        "trend_following_adx": TrendFollowingADXStrategy,
        "dual_momentum": DualMomentumStrategy,
        "volatility_breakout": VolatilityBreakoutStrategy,
        "statistical_arbitrage_pairs": StatisticalArbitragePairsStrategy,
        "multi_factor_fusion": MultiFactorFusionStrategy,
    }

    @classmethod
    def register(cls, name: str, strategy_class: Type[BaseStrategy]) -> None:
        cls._strategies[name.lower()] = strategy_class

    @classmethod
    def get_strategy_class(cls, name: str) -> Optional[Type[BaseStrategy]]:
        return cls._strategies.get(name.lower())

    @classmethod
    def list_available_strategies(cls) -> List[str]:
        return list(cls._strategies.keys())

    @classmethod
    def create_strategy(
        cls,
        strategy_type: str,
        strategy_id: str,
        name: str,
        symbol: str,
        symbols: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        risk_config: Optional[StrategyRiskConfig] = None,
    ) -> BaseStrategy:
        klass = cls._strategies.get(strategy_type.lower())
        if not klass:
            # Fallback to SMA crossover
            klass = SMACrossoverStrategy
        
        instance = klass(
            strategy_id=strategy_id,
            name=name,
            symbol=symbol,
            symbols=symbols,
            parameters=parameters or {},
            risk_config=risk_config,
        )
        instance.initialize()
        return instance
