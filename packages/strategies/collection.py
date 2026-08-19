"""
QUANTARA Built-in Quantitative Trading Strategies
Production collection of 12 deterministic strategies across momentum, mean reversion, trend, breakout, and statistical arbitrage.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import numpy as np
from packages.domain.models import Candle, Signal, SignalComponent, SignalDirection
from packages.indicators.technical import TechnicalIndicators
from packages.strategies.base import BaseStrategy


# =========================================================================
# 1. SMA Crossover Strategy
# =========================================================================
class SMACrossoverStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.fast_period = int(self.get_parameter("fast_period", 10))
        self.slow_period = int(self.get_parameter("slow_period", 30))
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) <= self.slow_period:
            return None

        closes = df["close"].values
        sma_fast = TechnicalIndicators.sma(closes, self.fast_period)
        sma_slow = TechnicalIndicators.sma(closes, self.slow_period)

        curr_fast, prev_fast = sma_fast[-1], sma_fast[-2]
        curr_slow, prev_slow = sma_slow[-1], sma_slow[-2]

        if np.isnan(curr_fast) or np.isnan(curr_slow) or np.isnan(prev_fast) or np.isnan(prev_slow):
            return None

        # Golden Cross: Fast crosses above Slow
        if prev_fast <= prev_slow and curr_fast > curr_slow:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.BUY,
                confidence=0.82,
                signal_score=0.75,
                strategy_id=self.strategy_id,
                reason_codes=["SMA_GOLDEN_CROSS"],
                components=[
                    SignalComponent(name="technical", score=0.85, weight=1.0, contribution=0.85, reason=f"SMA {self.fast_period} crossed above SMA {self.slow_period}")
                ]
            )
        # Death Cross: Fast crosses below Slow
        elif prev_fast >= prev_slow and curr_fast < curr_slow:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.SELL,
                confidence=0.82,
                signal_score=-0.75,
                strategy_id=self.strategy_id,
                reason_codes=["SMA_DEATH_CROSS"],
                components=[
                    SignalComponent(name="technical", score=-0.85, weight=1.0, contribution=-0.85, reason=f"SMA {self.fast_period} crossed below SMA {self.slow_period}")
                ]
            )
        return None


# =========================================================================
# 2. EMA Crossover Strategy
# =========================================================================
class EMACrossoverStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.fast_period = int(self.get_parameter("fast_period", 9))
        self.slow_period = int(self.get_parameter("slow_period", 21))
        self.trend_filter_period = int(self.get_parameter("trend_filter_period", 200))
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) <= max(self.slow_period, 30):
            return None

        closes = df["close"].values
        ema_fast = TechnicalIndicators.ema(closes, self.fast_period)
        ema_slow = TechnicalIndicators.ema(closes, self.slow_period)

        if np.isnan(ema_fast[-1]) or np.isnan(ema_slow[-1]) or np.isnan(ema_fast[-2]) or np.isnan(ema_slow[-2]):
            return None

        if ema_fast[-2] <= ema_slow[-2] and ema_fast[-1] > ema_slow[-1]:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.BUY,
                confidence=0.85,
                signal_score=0.80,
                strategy_id=self.strategy_id,
                reason_codes=["EMA_BULLISH_CROSS"],
                components=[
                    SignalComponent(name="technical", score=0.80, weight=1.0, contribution=0.80, reason=f"EMA {self.fast_period} crossed above EMA {self.slow_period}")
                ]
            )
        elif ema_fast[-2] >= ema_slow[-2] and ema_fast[-1] < ema_slow[-1]:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.SELL,
                confidence=0.85,
                signal_score=-0.80,
                strategy_id=self.strategy_id,
                reason_codes=["EMA_BEARISH_CROSS"],
                components=[
                    SignalComponent(name="technical", score=-0.80, weight=1.0, contribution=-0.80, reason=f"EMA {self.fast_period} crossed below EMA {self.slow_period}")
                ]
            )
        return None


# =========================================================================
# 3. RSI Mean Reversion Strategy
# =========================================================================
class RSIMeanReversionStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.rsi_period = int(self.get_parameter("rsi_period", 14))
        self.oversold_threshold = float(self.get_parameter("oversold_threshold", 30.0))
        self.overbought_threshold = float(self.get_parameter("overbought_threshold", 70.0))
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) <= self.rsi_period + 5:
            return None

        rsi_vals = TechnicalIndicators.rsi(df["close"].values, self.rsi_period)
        curr_rsi, prev_rsi = rsi_vals[-1], rsi_vals[-2]

        if np.isnan(curr_rsi) or np.isnan(prev_rsi):
            return None

        # Buy when RSI bounces back above oversold
        if prev_rsi <= self.oversold_threshold and curr_rsi > self.oversold_threshold:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.BUY,
                confidence=0.88,
                signal_score=0.85,
                strategy_id=self.strategy_id,
                reason_codes=["RSI_OVERSOLD_REBOUND"],
                components=[
                    SignalComponent(name="technical", score=0.88, weight=1.0, contribution=0.88, reason=f"RSI bounced above {self.oversold_threshold} (Current: {curr_rsi:.1f})")
                ]
            )
        # Sell when RSI drops below overbought
        elif prev_rsi >= self.overbought_threshold and curr_rsi < self.overbought_threshold:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.SELL,
                confidence=0.88,
                signal_score=-0.85,
                strategy_id=self.strategy_id,
                reason_codes=["RSI_OVERBOUGHT_PULLBACK"],
                components=[
                    SignalComponent(name="technical", score=-0.88, weight=1.0, contribution=-0.88, reason=f"RSI dropped below {self.overbought_threshold} (Current: {curr_rsi:.1f})")
                ]
            )
        return None


# =========================================================================
# 4. MACD Momentum Strategy
# =========================================================================
class MACDMomentumStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.fast_period = int(self.get_parameter("fast_period", 12))
        self.slow_period = int(self.get_parameter("slow_period", 26))
        self.signal_period = int(self.get_parameter("signal_period", 9))
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) <= self.slow_period + self.signal_period:
            return None

        macd, signal, hist = TechnicalIndicators.macd(df["close"].values, self.fast_period, self.slow_period, self.signal_period)
        
        if np.isnan(macd[-1]) or np.isnan(signal[-1]) or np.isnan(macd[-2]) or np.isnan(signal[-2]):
            return None

        # MACD Bullish Cross
        if macd[-2] <= signal[-2] and macd[-1] > signal[-1]:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.BUY,
                confidence=0.80,
                signal_score=0.76,
                strategy_id=self.strategy_id,
                reason_codes=["MACD_BULLISH_CROSS"],
                components=[
                    SignalComponent(name="technical", score=0.76, weight=1.0, contribution=0.76, reason="MACD line crossed above signal line")
                ]
            )
        elif macd[-2] >= signal[-2] and macd[-1] < signal[-1]:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.SELL,
                confidence=0.80,
                signal_score=-0.76,
                strategy_id=self.strategy_id,
                reason_codes=["MACD_BEARISH_CROSS"],
                components=[
                    SignalComponent(name="technical", score=-0.76, weight=1.0, contribution=-0.76, reason="MACD line crossed below signal line")
                ]
            )
        return None


# =========================================================================
# 5. Bollinger Bands Mean Reversion Strategy
# =========================================================================
class BollingerMeanReversionStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.period = int(self.get_parameter("period", 20))
        self.num_std = float(self.get_parameter("num_std", 2.0))
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) <= self.period:
            return None

        upper, middle, lower, pct_b = TechnicalIndicators.bollinger_bands(df["close"].values, self.period, self.num_std)
        curr_price = candle.close

        if np.isnan(lower[-1]) or np.isnan(upper[-1]):
            return None

        # Buy on Lower Band bounce
        if curr_price <= lower[-1]:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.BUY,
                confidence=0.83,
                signal_score=0.82,
                strategy_id=self.strategy_id,
                reason_codes=["BOLLINGER_LOWER_BAND_TOUCH"],
                components=[
                    SignalComponent(name="technical", score=0.82, weight=1.0, contribution=0.82, reason=f"Price {curr_price:.2f} touched lower Bollinger band {lower[-1]:.2f}")
                ]
            )
        # Exit or Short on Upper Band touch
        elif curr_price >= upper[-1]:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.SELL,
                confidence=0.83,
                signal_score=-0.82,
                strategy_id=self.strategy_id,
                reason_codes=["BOLLINGER_UPPER_BAND_TOUCH"],
                components=[
                    SignalComponent(name="technical", score=-0.82, weight=1.0, contribution=-0.82, reason=f"Price {curr_price:.2f} reached upper Bollinger band {upper[-1]:.2f}")
                ]
            )
        return None


# =========================================================================
# 6. VWAP Intraday Strategy
# =========================================================================
class VWAPIntradayStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) < 15:
            return None

        vwap_vals = TechnicalIndicators.vwap(df["high"].values, df["low"].values, df["close"].values, df["volume"].values)
        curr_vwap, prev_vwap = vwap_vals[-1], vwap_vals[-2]
        curr_close, prev_close = df["close"].values[-1], df["close"].values[-2]

        if prev_close <= prev_vwap and curr_close > curr_vwap:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.BUY,
                confidence=0.81,
                signal_score=0.74,
                strategy_id=self.strategy_id,
                reason_codes=["VWAP_CROSSOVER_ABOVE"],
                components=[
                    SignalComponent(name="technical", score=0.74, weight=1.0, contribution=0.74, reason="Price crossed above cumulative VWAP")
                ]
            )
        elif prev_close >= prev_vwap and curr_close < curr_vwap:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.SELL,
                confidence=0.81,
                signal_score=-0.74,
                strategy_id=self.strategy_id,
                reason_codes=["VWAP_CROSSOVER_BELOW"],
                components=[
                    SignalComponent(name="technical", score=-0.74, weight=1.0, contribution=-0.74, reason="Price crossed below cumulative VWAP")
                ]
            )
        return None


# =========================================================================
# 7. Donchian Channel Breakout Strategy (Turtle Trading)
# =========================================================================
class DonchianBreakoutStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.lookback = int(self.get_parameter("lookback", 20))
        self.exit_lookback = int(self.get_parameter("exit_lookback", 10))
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) <= self.lookback + 1:
            return None

        highs = df["high"].values
        lows = df["low"].values
        closes = df["close"].values

        highest_high = np.max(highs[-self.lookback - 1 : -1])
        lowest_low = np.min(lows[-self.exit_lookback - 1 : -1])

        if closes[-1] > highest_high:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.BUY,
                confidence=0.89,
                signal_score=0.88,
                strategy_id=self.strategy_id,
                reason_codes=["DONCHIAN_20_DAY_BREAKOUT"],
                components=[
                    SignalComponent(name="technical", score=0.88, weight=1.0, contribution=0.88, reason=f"New {self.lookback}-period high breakout")
                ]
            )
        elif closes[-1] < lowest_low:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.SELL,
                confidence=0.89,
                signal_score=-0.88,
                strategy_id=self.strategy_id,
                reason_codes=["DONCHIAN_10_DAY_EXIT"],
                components=[
                    SignalComponent(name="technical", score=-0.88, weight=1.0, contribution=-0.88, reason=f"Broke below {self.exit_lookback}-period low")
                ]
            )
        return None


# =========================================================================
# 8. Trend Following ADX Strategy
# =========================================================================
class TrendFollowingADXStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.adx_period = int(self.get_parameter("adx_period", 14))
        self.adx_threshold = float(self.get_parameter("adx_threshold", 25.0))
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) <= self.adx_period * 2 + 5:
            return None

        adx, p_di, m_di = TechnicalIndicators.adx(df["high"].values, df["low"].values, df["close"].values, self.adx_period)
        if np.isnan(adx[-1]) or np.isnan(p_di[-1]) or np.isnan(m_di[-1]):
            return None

        # Strong bullish trend
        if adx[-1] > self.adx_threshold and p_di[-1] > m_di[-1] and p_di[-2] <= m_di[-2]:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.BUY,
                confidence=0.86,
                signal_score=0.82,
                strategy_id=self.strategy_id,
                reason_codes=["STRONG_ADX_BULLISH_TREND"],
                components=[
                    SignalComponent(name="technical", score=0.82, weight=1.0, contribution=0.82, reason=f"ADX at {adx[-1]:.1f} with +DI crossing above -DI")
                ]
            )
        elif adx[-1] > self.adx_threshold and m_di[-1] > p_di[-1] and m_di[-2] <= p_di[-2]:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.SELL,
                confidence=0.86,
                signal_score=-0.82,
                strategy_id=self.strategy_id,
                reason_codes=["STRONG_ADX_BEARISH_TREND"],
                components=[
                    SignalComponent(name="technical", score=-0.82, weight=1.0, contribution=-0.82, reason=f"ADX at {adx[-1]:.1f} with -DI crossing above +DI")
                ]
            )
        return None


# =========================================================================
# 9. Dual Momentum Strategy
# =========================================================================
class DualMomentumStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.lookback = int(self.get_parameter("lookback", 60))
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) <= self.lookback:
            return None

        closes = df["close"].values
        abs_momentum = (closes[-1] - closes[-self.lookback]) / closes[-self.lookback]

        if abs_momentum > 0.05:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.BUY,
                confidence=0.80,
                signal_score=min(0.95, abs_momentum * 2.0),
                strategy_id=self.strategy_id,
                reason_codes=["DUAL_MOMENTUM_POSITIVE"],
                components=[
                    SignalComponent(name="technical", score=0.80, weight=1.0, contribution=0.80, reason=f"Positive absolute momentum: {abs_momentum*100:.1f}%")
                ]
            )
        elif abs_momentum < -0.05:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.SELL,
                confidence=0.80,
                signal_score=max(-0.95, abs_momentum * 2.0),
                strategy_id=self.strategy_id,
                reason_codes=["DUAL_MOMENTUM_NEGATIVE"],
                components=[
                    SignalComponent(name="technical", score=-0.80, weight=1.0, contribution=-0.80, reason=f"Negative absolute momentum: {abs_momentum*100:.1f}%")
                ]
            )
        return None


# =========================================================================
# 10. Volatility Breakout Strategy (ATR Expansion)
# =========================================================================
class VolatilityBreakoutStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.atr_period = int(self.get_parameter("atr_period", 14))
        self.atr_multiplier = float(self.get_parameter("atr_multiplier", 1.8))
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) <= self.atr_period + 2:
            return None

        atr_vals = TechnicalIndicators.atr(df["high"].values, df["low"].values, df["close"].values, self.atr_period)
        curr_atr = atr_vals[-1]
        prev_close = df["close"].values[-2]
        curr_close = df["close"].values[-1]

        if np.isnan(curr_atr):
            return None

        if curr_close > prev_close + self.atr_multiplier * curr_atr:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.BUY,
                confidence=0.84,
                signal_score=0.85,
                strategy_id=self.strategy_id,
                reason_codes=["VOLATILITY_EXPANSION_UP"],
                components=[
                    SignalComponent(name="technical", score=0.85, weight=1.0, contribution=0.85, reason=f"Price broke upwards by > {self.atr_multiplier}x ATR")
                ]
            )
        elif curr_close < prev_close - self.atr_multiplier * curr_atr:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.SELL,
                confidence=0.84,
                signal_score=-0.85,
                strategy_id=self.strategy_id,
                reason_codes=["VOLATILITY_EXPANSION_DOWN"],
                components=[
                    SignalComponent(name="technical", score=-0.85, weight=1.0, contribution=-0.85, reason=f"Price broke downwards by > {self.atr_multiplier}x ATR")
                ]
            )
        return None


# =========================================================================
# 11. Statistical Arbitrage Pairs Strategy (Spread Z-score)
# =========================================================================
class StatisticalArbitragePairsStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.z_entry_threshold = float(self.get_parameter("z_entry_threshold", 2.0))
        self.z_exit_threshold = float(self.get_parameter("z_exit_threshold", 0.5))
        self.window = int(self.get_parameter("window", 30))
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) <= self.window:
            return None

        closes = df["close"].values
        rolling_mean = np.mean(closes[-self.window:])
        rolling_std = np.std(closes[-self.window:]) if np.std(closes[-self.window:]) > 0 else 1.0
        z_score = (closes[-1] - rolling_mean) / rolling_std

        if z_score <= -self.z_entry_threshold:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.BUY,
                confidence=0.87,
                signal_score=0.84,
                strategy_id=self.strategy_id,
                reason_codes=["STAT_ARB_ZSCORE_OVERSOLD"],
                components=[
                    SignalComponent(name="quant", score=0.84, weight=1.0, contribution=0.84, reason=f"Spread Z-score {z_score:.2f} <= -{self.z_entry_threshold}")
                ]
            )
        elif z_score >= self.z_entry_threshold:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.SELL,
                confidence=0.87,
                signal_score=-0.84,
                strategy_id=self.strategy_id,
                reason_codes=["STAT_ARB_ZSCORE_OVERBOUGHT"],
                components=[
                    SignalComponent(name="quant", score=-0.84, weight=1.0, contribution=-0.84, reason=f"Spread Z-score {z_score:.2f} >= {self.z_entry_threshold}")
                ]
            )
        return None


# =========================================================================
# 12. Multi-Factor Fusion Strategy
# =========================================================================
class MultiFactorFusionStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) < 35:
            return None

        closes = df["close"].values
        highs = df["high"].values
        lows = df["low"].values
        volumes = df["volume"].values

        rsi = TechnicalIndicators.rsi(closes, 14)[-1]
        ema_20 = TechnicalIndicators.ema(closes, 20)[-1]
        sma_50 = TechnicalIndicators.sma(closes, 50)[-1]
        adx, p_di, m_di = TechnicalIndicators.adx(highs, lows, closes, 14)
        curr_adx = adx[-1] if not np.isnan(adx[-1]) else 20.0

        score = 0.0
        reasons = []

        # Trend Factor
        if closes[-1] > ema_20 > sma_50:
            score += 0.35
            reasons.append("BULLISH_TREND_ALIGNMENT")
        elif closes[-1] < ema_20 < sma_50:
            score -= 0.35
            reasons.append("BEARISH_TREND_ALIGNMENT")

        # Momentum Factor
        if 40 < rsi < 65 and p_di[-1] > m_di[-1]:
            score += 0.35
            reasons.append("HEALTHY_MOMENTUM_EXPANSION")
        elif rsi > 75 or (rsi < 40 and m_di[-1] > p_di[-1]):
            score -= 0.35
            reasons.append("EXHAUSTION_OR_BEARISH_MOMENTUM")

        # Trend Strength
        if curr_adx > 22:
            score *= 1.2
            reasons.append("CONFIRMED_TREND_STRENGTH")

        score = float(np.clip(score, -1.0, 1.0))

        if score >= 0.50:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.BUY,
                confidence=0.88,
                signal_score=score,
                strategy_id=self.strategy_id,
                reason_codes=reasons,
                components=[
                    SignalComponent(name="technical", score=score, weight=0.6, contribution=score * 0.6, reason="Multi-factor confluence bullish"),
                    SignalComponent(name="quant", score=0.8, weight=0.4, contribution=0.32, reason="Trend strength confirmed")
                ]
            )
        elif score <= -0.50:
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.SELL,
                confidence=0.88,
                signal_score=score,
                strategy_id=self.strategy_id,
                reason_codes=reasons,
                components=[
                    SignalComponent(name="technical", score=score, weight=0.6, contribution=score * 0.6, reason="Multi-factor confluence bearish"),
                    SignalComponent(name="quant", score=-0.8, weight=0.4, contribution=-0.32, reason="Trend breakdown confirmed")
                ]
            )
        return None
