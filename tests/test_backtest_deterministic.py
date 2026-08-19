import pytest
from datetime import datetime, timedelta, timezone
from packages.backtesting.engine import BacktestEngine
from packages.domain.models import Candle
from packages.strategies.registry import StrategyRegistry


def generate_test_candles(count: int = 150):
    candles = []
    base_time = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    price = 100.0
    for i in range(count):
        price = price + (1.0 if i % 2 == 0 else -0.5)
        c = Candle(
            symbol="TEST_ASSET",
            timeframe="1D",
            open=price,
            high=price + 2.0,
            low=price - 1.0,
            close=price + 0.5,
            volume=10000.0,
            timestamp=base_time + timedelta(days=i)
        )
        candles.append(c)
    return candles


def test_backtest_determinism():
    candles = generate_test_candles(100)
    
    strat1 = StrategyRegistry.create_strategy(
        strategy_type="sma_crossover",
        strategy_id="strat_det_1",
        name="SMA Det Test 1",
        symbol="TEST_ASSET",
        parameters={"fast_period": 5, "slow_period": 15}
    )
    
    strat2 = StrategyRegistry.create_strategy(
        strategy_type="sma_crossover",
        strategy_id="strat_det_2",
        name="SMA Det Test 2",
        symbol="TEST_ASSET",
        parameters={"fast_period": 5, "slow_period": 15}
    )

    engine = BacktestEngine(initial_capital=100_000.0)
    res1 = engine.run(strat1, candles)
    res2 = engine.run(strat2, candles)

    # Determinism verification: both runs must produce identical metrics & final equity
    assert res1.final_equity == res2.final_equity
    assert res1.metrics.total_return == res2.metrics.total_return
    assert res1.metrics.sharpe_ratio == res2.metrics.sharpe_ratio
    assert len(res1.trades) == len(res2.trades)
