"""
QUANTARA Market Data Quality & Integrity Validator
Validates OHLCV feeds to eliminate bad ticks, chronological inversions, and data corruption.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from packages.domain.models import Candle


class DataQualityValidator:
    """Validates candlestick series before execution or feature engineering."""

    @staticmethod
    def validate_candles(candles: List[Candle]) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        now = datetime.now(timezone.utc)
        
        if not candles:
            return False, ["Candle list is completely empty."]

        seen_timestamps = set()
        prev_time = None

        for idx, c in enumerate(candles):
            # 1. Non-negative / Non-zero Prices
            if c.open <= 0 or c.high <= 0 or c.low <= 0 or c.close <= 0:
                errors.append(f"Row {idx} ({c.timestamp}): Contains non-positive price (O:{c.open}, H:{c.high}, L:{c.low}, C:{c.close})")

            # 2. OHLC Logical Hierarchy (High >= Open, High >= Close, High >= Low, Low <= Open, Low <= Close)
            if c.high < c.low or c.high < c.open or c.high < c.close or c.low > c.open or c.low > c.close:
                errors.append(f"Row {idx} ({c.timestamp}): Invalid OHLC hierarchy (O:{c.open}, H:{c.high}, L:{c.low}, C:{c.close})")

            # 3. Non-negative Volume
            if c.volume < 0:
                errors.append(f"Row {idx} ({c.timestamp}): Volume cannot be negative ({c.volume})")

            # 4. Duplicate Timestamps
            if c.timestamp in seen_timestamps:
                errors.append(f"Row {idx}: Duplicate timestamp detected ({c.timestamp})")
            seen_timestamps.add(c.timestamp)

            # 5. Chronological Order
            if prev_time and c.timestamp < prev_time:
                errors.append(f"Row {idx}: Chronological inversion ({c.timestamp} < {prev_time})")
            prev_time = c.timestamp

            # 6. Future Timestamp check
            if c.timestamp > now:
                errors.append(f"Row {idx}: Future timestamp detected ({c.timestamp} > {now})")

        is_valid = len(errors) == 0
        return is_valid, errors
