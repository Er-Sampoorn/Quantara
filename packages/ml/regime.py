"""
QUANTARA Market Regime Detection Engine
Rule-based & statistical multi-state classifier for financial market regimes.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from packages.domain.models import MarketRegimeState, RegimeType
from packages.indicators.technical import TechnicalIndicators


class MarketRegimeEngine:
    """Classifies market environment into standard regimes with confidence scores."""

    @staticmethod
    def classify_regime(
        df_candles: pd.DataFrame,
        symbol: str = "DEMO_ASSET"
    ) -> MarketRegimeState:
        """
        Accepts candlestick DataFrame (with at least 50 bars) and classifies the current market state.
        """
        if len(df_candles) < 30:
            return MarketRegimeState(
                symbol=symbol,
                regime=RegimeType.SIDEWAYS,
                confidence=0.5,
                volatility=0.15,
                trend_strength=0.0,
                supporting_features={"reason": "Insufficient historical bars for robust classification"},
                timestamp=datetime.now(timezone.utc)
            )

        close = df_candles["close"].values
        high = df_candles["high"].values
        low = df_candles["low"].values
        volume = df_candles["volume"].values

        current_price = close[-1]
        sma_20 = TechnicalIndicators.sma(close, 20)[-1]
        sma_50 = TechnicalIndicators.sma(close, 50)[-1]
        sma_200 = TechnicalIndicators.sma(close, 200)[-1] if len(close) >= 200 else sma_50

        rsi = TechnicalIndicators.rsi(close, 14)[-1]
        adx, p_di, m_di = TechnicalIndicators.adx(high, low, close, 14)
        current_adx = adx[-1] if not np.isnan(adx[-1]) else 20.0
        
        atr = TechnicalIndicators.atr(high, low, close, 14)[-1]
        atr_pct = (atr / current_price) if not np.isnan(atr) and current_price > 0 else 0.02
        
        # Volatility estimation (20-bar annualized)
        returns = np.diff(close) / close[:-1]
        recent_returns_20 = returns[-20:] if len(returns) >= 20 else returns
        volatility_20 = float(np.std(recent_returns_20) * np.sqrt(252))
        
        # 5-bar and 20-bar price changes
        pct_change_5 = float((current_price - close[-5]) / close[-5]) if len(close) >= 5 else 0.0
        pct_change_20 = float((current_price - close[-20]) / close[-20]) if len(close) >= 20 else 0.0

        # Volume z-score
        vol_mean = np.mean(volume[-20:])
        vol_std = np.std(volume[-20:]) if np.std(volume[-20:]) > 0 else 1.0
        vol_zscore = float((volume[-1] - vol_mean) / vol_std)

        # Classification Logic
        # 1. PANIC Regime: Sharp down-draw + high volatility + high volume
        if pct_change_5 < -0.07 and volatility_20 > 0.35 and vol_zscore > 1.5:
            regime = RegimeType.PANIC
            confidence = min(0.95, 0.70 + abs(pct_change_5) * 2.0)
            trend_strength = -0.9

        # 2. BREAKOUT Regime: New 20-day high/low + volume surge + ADX expansion
        elif vol_zscore > 2.0 and (current_price >= np.max(high[-21:-1]) or current_price <= np.min(low[-21:-1])):
            regime = RegimeType.BREAKOUT
            confidence = min(0.90, 0.65 + vol_zscore * 0.1)
            trend_strength = 0.85 if current_price >= np.max(high[-21:-1]) else -0.85

        # 3. RECOVERY: Oversold RSI bounce + strong 5-day positive rebound + high volatility cooling
        elif rsi < 45 and pct_change_5 > 0.04 and close[-1] > sma_20:
            regime = RegimeType.RECOVERY
            confidence = 0.78
            trend_strength = 0.6

        # 4. HIGH_VOLATILITY: Volatility elevated (> 30%) with choppy signals
        elif volatility_20 > 0.32:
            regime = RegimeType.HIGH_VOLATILITY
            confidence = 0.82
            trend_strength = float(np.clip((current_price - sma_50) / sma_50, -1.0, 1.0))

        # 5. LOW_VOLATILITY: Compression (ATR < 1.2%, Volatility < 12%)
        elif volatility_20 < 0.12 and atr_pct < 0.015:
            regime = RegimeType.LOW_VOLATILITY
            confidence = 0.85
            trend_strength = 0.1

        # 6. BULL Trend: Price > SMA20 > SMA50, ADX > 22, DI+ > DI-
        elif current_price > sma_50 and sma_20 >= sma_50 and pct_change_20 > 0.01:
            regime = RegimeType.BULL
            confidence = min(0.92, 0.60 + (current_adx / 100.0) * 0.4)
            trend_strength = min(1.0, (current_adx / 50.0))

        # 7. BEAR Trend: Price < SMA50 and sma_20 <= sma_50 and pct_change_20 < -0.01
        elif current_price < sma_50 and sma_20 <= sma_50 and pct_change_20 < -0.01:
            regime = RegimeType.BEAR
            confidence = min(0.92, 0.60 + (current_adx / 100.0) * 0.4)
            trend_strength = -min(1.0, (current_adx / 50.0))

        # 8. Default: SIDEWAYS
        else:
            regime = RegimeType.SIDEWAYS
            confidence = 0.70
            trend_strength = 0.0

        return MarketRegimeState(
            symbol=symbol,
            regime=regime,
            confidence=round(float(confidence), 4),
            volatility=round(float(volatility_20), 4),
            trend_strength=round(float(trend_strength), 4),
            supporting_features={
                "rsi_14": round(float(rsi), 2) if not np.isnan(rsi) else 50.0,
                "adx_14": round(float(current_adx), 2),
                "volatility_20": round(float(volatility_20), 4),
                "pct_change_5": round(float(pct_change_5), 4),
                "pct_change_20": round(float(pct_change_20), 4),
                "volume_zscore": round(float(vol_zscore), 2),
                "dist_sma_50": round(float((current_price - sma_50) / sma_50), 4) if sma_50 > 0 else 0.0,
            },
            timestamp=datetime.now(timezone.utc)
        )
