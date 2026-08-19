"""
QUANTARA Strategies Package
"""

from packages.strategies.base import BaseStrategy
from packages.strategies.registry import StrategyRegistry
from packages.strategies.collection import (
    SMACrossoverStrategy,
    EMACrossoverStrategy,
    RSIMeanReversionStrategy,
    MACDMomentumStrategy,
    BollingerMeanReversionStrategy,
    VWAPIntradayStrategy,
    DonchianBreakoutStrategy,
    TrendFollowingADXStrategy,
    DualMomentumStrategy,
    VolatilityBreakoutStrategy,
    StatisticalArbitragePairsStrategy,
    MultiFactorFusionStrategy,
)

__all__ = [
    "BaseStrategy",
    "StrategyRegistry",
    "SMACrossoverStrategy",
    "EMACrossoverStrategy",
    "RSIMeanReversionStrategy",
    "MACDMomentumStrategy",
    "BollingerMeanReversionStrategy",
    "VWAPIntradayStrategy",
    "DonchianBreakoutStrategy",
    "TrendFollowingADXStrategy",
    "DualMomentumStrategy",
    "VolatilityBreakoutStrategy",
    "StatisticalArbitragePairsStrategy",
    "MultiFactorFusionStrategy",
]
