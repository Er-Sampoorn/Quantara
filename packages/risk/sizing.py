"""
QUANTARA Position Sizing Models
Deterministic mathematical position sizing algorithms with hard risk bounds.
"""

from __future__ import annotations
import math
from typing import Optional
from packages.domain.models import PositionSizingType


class PositionSizer:
    """Calculates order quantity based on account equity, price, and risk parameters."""

    @staticmethod
    def calculate_quantity(
        sizing_type: PositionSizingType,
        portfolio_equity: float,
        current_price: float,
        risk_per_trade_pct: float = 0.01,  # 1% equity risk
        stop_loss_price: Optional[float] = None,
        atr_value: Optional[float] = None,
        atr_multiplier: float = 2.0,
        win_rate: float = 0.55,
        win_loss_ratio: float = 1.5,
        fixed_capital: float = 5_000.0,
        fixed_quantity: float = 100.0,
        max_position_equity_pct: float = 0.20,  # Max 20% equity in single asset
    ) -> float:
        if current_price <= 0 or portfolio_equity <= 0:
            return 0.0

        max_allowed_shares = (portfolio_equity * max_position_equity_pct) / current_price

        if sizing_type == PositionSizingType.FIXED_QUANTITY:
            raw_qty = fixed_quantity

        elif sizing_type == PositionSizingType.FIXED_CAPITAL:
            raw_qty = fixed_capital / current_price

        elif sizing_type == PositionSizingType.RISK_PERCENTAGE:
            if stop_loss_price is not None and stop_loss_price > 0 and stop_loss_price != current_price:
                risk_per_share = abs(current_price - stop_loss_price)
                dollar_risk = portfolio_equity * risk_per_trade_pct
                raw_qty = dollar_risk / risk_per_share
            else:
                # Default 2% stop distance
                dollar_risk = portfolio_equity * risk_per_trade_pct
                raw_qty = dollar_risk / (current_price * 0.02)

        elif sizing_type == PositionSizingType.VOLATILITY_ATR:
            if atr_value is not None and atr_value > 0:
                dollar_risk = portfolio_equity * risk_per_trade_pct
                risk_per_share = atr_value * atr_multiplier
                raw_qty = dollar_risk / risk_per_share
            else:
                raw_qty = (portfolio_equity * risk_per_trade_pct) / (current_price * 0.02)

        elif sizing_type == PositionSizingType.KELLY_CRITERION:
            # Half-Kelly Formula: f* = 0.5 * (p - (1-p)/b)
            p = max(0.01, min(0.99, win_rate))
            b = max(0.1, win_loss_ratio)
            kelly_f = (p * (b + 1.0) - 1.0) / b
            half_kelly = max(0.0, kelly_f * 0.5)
            # Bound Kelly fraction between 0.5% and 10%
            bounded_f = min(0.10, max(0.005, half_kelly))
            raw_qty = (portfolio_equity * bounded_f) / current_price

        else:
            raw_qty = (portfolio_equity * 0.02) / current_price

        # Cap at maximum allowed shares
        final_qty = max(1.0, min(raw_qty, max_allowed_shares))
        return math.floor(final_qty)
