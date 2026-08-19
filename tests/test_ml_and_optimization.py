import pandas as pd
import numpy as np
import pytest
from packages.domain.models import PositionSizingType, RegimeType
from packages.ml.regime import MarketRegimeEngine
from packages.risk.sizing import PositionSizer
from services.optimization_engine.monte_carlo import MonteCarloEngine
from services.optimization_engine.walk_forward import WalkForwardEngine
from tests.test_backtest_deterministic import generate_test_candles


def test_market_regime_classification():
    # Construct upward trending price data
    closes = np.linspace(100, 180, 60)
    highs = closes + 2.0
    lows = closes - 1.0
    volumes = np.full(60, 50000.0)

    df = pd.DataFrame({"close": closes, "high": highs, "low": lows, "volume": volumes})
    state = MarketRegimeEngine.classify_regime(df, "TEST_ASSET")

    assert state.regime in [RegimeType.BULL, RegimeType.BREAKOUT, RegimeType.RECOVERY]
    assert state.confidence >= 0.50


def test_position_sizing_models():
    equity = 100_000.0
    price = 200.0

    # 1. Fixed Quantity
    qty_fixed = PositionSizer.calculate_quantity(PositionSizingType.FIXED_QUANTITY, equity, price, fixed_quantity=50)
    assert qty_fixed == 50

    # 2. Risk Percentage with Stop Loss (1% risk on $100k = $1000 risk. Stop at 190 -> $10 risk/share -> 100 shares)
    qty_risk = PositionSizer.calculate_quantity(
        PositionSizingType.RISK_PERCENTAGE,
        equity,
        price,
        risk_per_trade_pct=0.01,
        stop_loss_price=190.0
    )
    assert qty_risk == 100

    # 3. Half-Kelly sizing
    qty_kelly = PositionSizer.calculate_quantity(
        PositionSizingType.KELLY_CRITERION,
        equity,
        price,
        win_rate=0.60,
        win_loss_ratio=2.0
    )
    assert qty_kelly > 0


def test_walk_forward_and_monte_carlo():
    candles = generate_test_candles(150)

    wf_res = WalkForwardEngine.evaluate(
        strategy_type="sma_crossover",
        symbol="TEST_ASSET",
        candles=candles,
        parameter_grid={"fast_period": [5, 10], "slow_period": [20, 30]},
        num_splits=3
    )
    assert "walk_forward_efficiency" in wf_res
    assert len(wf_res["splits"]) >= 2
