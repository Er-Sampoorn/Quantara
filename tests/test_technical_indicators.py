import numpy as np
import pytest
from packages.indicators.technical import TechnicalIndicators


def test_sma_calculation():
    data = [10.0, 11.0, 12.0, 13.0, 14.0]
    res = TechnicalIndicators.sma(data, period=3)
    assert np.isnan(res[0])
    assert np.isnan(res[1])
    assert np.isclose(res[2], 11.0)
    assert np.isclose(res[3], 12.0)
    assert np.isclose(res[4], 13.0)


def test_rsi_calculation():
    # Consistent upward prices should produce RSI near 100
    up_prices = np.linspace(100, 200, 30)
    rsi_up = TechnicalIndicators.rsi(up_prices, period=14)
    assert not np.isnan(rsi_up[-1])
    assert rsi_up[-1] > 80.0

    # Consistent downward prices should produce RSI near 0
    down_prices = np.linspace(200, 100, 30)
    rsi_down = TechnicalIndicators.rsi(down_prices, period=14)
    assert not np.isnan(rsi_down[-1])
    assert rsi_down[-1] < 20.0


def test_bollinger_bands():
    prices = np.array([100.0 + (i % 5) for i in range(40)])
    upper, mid, lower, pct_b = TechnicalIndicators.bollinger_bands(prices, period=20, num_std=2.0)
    
    assert not np.isnan(upper[-1])
    assert not np.isnan(mid[-1])
    assert not np.isnan(lower[-1])
    assert upper[-1] > mid[-1] > lower[-1]
