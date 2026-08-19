"""
QUANTARA Strategy DSL Parser & Validator
Validates JSON AST strategy definitions and ensures safe rule specifications.
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple
from packages.domain.models import PositionSizingType, StrategyRiskConfig, StrategyRule, StrategySpec


class StrategyDSLValidator:
    """Validates structural correctness of Strategy DSL definitions."""

    SUPPORTED_INDICATORS = {
        "RSI", "SMA", "EMA", "MACD", "BOLLINGER", "ATR", "VWAP", "ADX", "STOCHASTIC", "PRICE", "VOLUME"
    }

    SUPPORTED_OPERATORS = {
        "crosses_above", "crosses_below", "greater_than", "less_than", "equals",
        "price_above", "price_below", "price_touch_lower", "price_touch_upper"
    }

    @classmethod
    def validate_spec(cls, spec_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        if not spec_data.get("name"):
            errors.append("Strategy name cannot be empty.")
        if not spec_data.get("symbol") and not spec_data.get("symbols"):
            errors.append("Strategy must target at least one symbol.")

        # Validate Entry Rules
        entry_rules = spec_data.get("entry_rules", [])
        if not entry_rules:
            errors.append("Strategy must contain at least one entry rule.")
        for idx, rule in enumerate(entry_rules):
            ind = rule.get("indicator", "").upper()
            op = rule.get("operator", "")
            if ind not in cls.SUPPORTED_INDICATORS:
                errors.append(f"Entry rule {idx}: Unsupported indicator '{ind}'. Supported: {cls.SUPPORTED_INDICATORS}")
            if op not in cls.SUPPORTED_OPERATORS:
                errors.append(f"Entry rule {idx}: Unsupported operator '{op}'. Supported: {cls.SUPPORTED_OPERATORS}")

        # Validate Exit Rules
        exit_rules = spec_data.get("exit_rules", [])
        if not exit_rules:
            errors.append("Strategy must contain at least one exit rule.")
        for idx, rule in enumerate(exit_rules):
            ind = rule.get("indicator", "").upper()
            op = rule.get("operator", "")
            if ind not in cls.SUPPORTED_INDICATORS:
                errors.append(f"Exit rule {idx}: Unsupported indicator '{ind}'.")
            if op not in cls.SUPPORTED_OPERATORS:
                errors.append(f"Exit rule {idx}: Unsupported operator '{op}'.")

        # Validate Risk Config
        risk = spec_data.get("risk_config", {})
        risk_per_trade = risk.get("risk_per_trade", 0.01)
        if risk_per_trade <= 0 or risk_per_trade > 0.10:
            errors.append(f"Risk per trade ({risk_per_trade}) must be between 0.001 (0.1%) and 0.10 (10%).")

        is_valid = len(errors) == 0
        return is_valid, errors
