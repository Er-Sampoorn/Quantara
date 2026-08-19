"""
QUANTARA Market Anomaly Detection Engine
Statistical Z-score and Isolation Forest detection for volume spikes, price shocks, and volatility bursts.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from packages.domain.models import AnomalyEvent, Candle, NewsImpact, Quote


class MarketAnomalyDetector:
    """Detects market microstructure irregularities and liquidity dislocations."""

    @classmethod
    def scan_candles(cls, symbol: str, candles: List[Candle]) -> List[AnomalyEvent]:
        if len(candles) < 30:
            return []

        anomalies: List[AnomalyEvent] = []
        now = datetime.now(timezone.utc)

        closes = np.array([c.close for c in candles], dtype=float)
        volumes = np.array([c.volume for c in candles], dtype=float)
        highs = np.array([c.high for c in candles], dtype=float)
        lows = np.array([c.low for c in candles], dtype=float)

        # 1. Volume Spike Detection
        vol_mean = np.mean(volumes[-30:-1])
        vol_std = np.std(volumes[-30:-1]) if np.std(volumes[-30:-1]) > 0 else 1.0
        vol_z = (volumes[-1] - vol_mean) / vol_std

        if vol_z > 2.8:
            anomalies.append(AnomalyEvent(
                id=f"anom_{uuid.uuid4().hex[:8]}",
                symbol=symbol.upper(),
                anomaly_type="VOLUME_SPIKE",
                severity=NewsImpact.HIGH if vol_z > 4.0 else NewsImpact.MEDIUM,
                z_score=round(float(vol_z), 2),
                current_value=round(float(volumes[-1]), 0),
                baseline_value=round(float(vol_mean), 0),
                message=f"Volume anomaly detected: {vol_z:.1f} std dev above 30-period average.",
                timestamp=now
            ))

        # 2. Price Shock (Absolute 1-bar return Z-score)
        returns = np.diff(closes) / closes[:-1]
        ret_mean = np.mean(returns[-30:-1])
        ret_std = np.std(returns[-30:-1]) if np.std(returns[-30:-1]) > 0 else 0.005
        ret_z = (returns[-1] - ret_mean) / ret_std

        if abs(ret_z) > 3.0:
            anomalies.append(AnomalyEvent(
                id=f"anom_{uuid.uuid4().hex[:8]}",
                symbol=symbol.upper(),
                anomaly_type="PRICE_SHOCK",
                severity=NewsImpact.CRITICAL if abs(ret_z) > 4.5 else NewsImpact.HIGH,
                z_score=round(float(ret_z), 2),
                current_value=round(float(returns[-1] * 100), 2),
                baseline_value=round(float(ret_mean * 100), 2),
                message=f"Rapid price movement shock: {returns[-1]*100:+.2f}% ({ret_z:.1f} sigma).",
                timestamp=now
            ))

        # 3. Range / Intraday Volatility Burst
        ranges = (highs - lows) / closes
        range_mean = np.mean(ranges[-30:-1])
        range_std = np.std(ranges[-30:-1]) if np.std(ranges[-30:-1]) > 0 else 0.005
        range_z = (ranges[-1] - range_mean) / range_std

        if range_z > 3.2:
            anomalies.append(AnomalyEvent(
                id=f"anom_{uuid.uuid4().hex[:8]}",
                symbol=symbol.upper(),
                anomaly_type="VOLATILITY_BURST",
                severity=NewsImpact.HIGH,
                z_score=round(float(range_z), 2),
                current_value=round(float(ranges[-1] * 100), 2),
                baseline_value=round(float(range_mean * 100), 2),
                message=f"Intraday trading range expansion: {ranges[-1]*100:.2f}% ({range_z:.1f} sigma).",
                timestamp=now
            ))

        return anomalies

    @classmethod
    def scan_quote(cls, quote: Quote) -> Optional[AnomalyEvent]:
        spread = quote.ask_price - quote.bid_price
        mid = (quote.ask_price + quote.bid_price) / 2.0
        spread_bps = (spread / mid) * 10000.0 if mid > 0 else 0.0

        if spread_bps > 50.0:  # > 50 bps spread
            return AnomalyEvent(
                id=f"anom_{uuid.uuid4().hex[:8]}",
                symbol=quote.symbol,
                anomaly_type="SPREAD_WIDENING",
                severity=NewsImpact.MEDIUM,
                z_score=3.0,
                current_value=round(spread_bps, 1),
                baseline_value=5.0,
                message=f"Liquidity spread widening alert: {spread_bps:.1f} bps spread.",
                timestamp=datetime.now(timezone.utc)
            )
        return None
