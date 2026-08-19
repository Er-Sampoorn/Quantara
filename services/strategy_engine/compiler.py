"""
QUANTARA Natural Language Strategy Compiler & Dynamic Strategy Runtime
Translates plain English trading logic into validated JSON AST specifications and executable strategy instances.
"""

from __future__ import annotations
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from packages.domain.models import (
    Candle,
    PositionSizingType,
    Signal,
    SignalComponent,
    SignalDirection,
    StrategyRiskConfig,
    StrategyRule,
    StrategySpec,
)
from packages.indicators.technical import TechnicalIndicators
from packages.strategies.base import BaseStrategy
from services.strategy_engine.dsl import StrategyDSLValidator


class NaturalLanguageStrategyParser:
    """
    Parses natural language strategy descriptions into structured StrategySpec AST.
    Deterministic rule-based NLP parser with regex and pattern matching.
    """

    @classmethod
    def parse(cls, prompt: str, target_symbol: str = "AAPL") -> StrategySpec:
        text = prompt.lower()
        
        entry_rules: List[StrategyRule] = []
        exit_rules: List[StrategyRule] = []
        risk_per_trade = 0.01
        stop_loss_pct = 0.02
        take_profit_pct = 0.04

        # Extract Risk Percentage
        risk_match = re.search(r"risk\s*([0-9.]+)\s*%", text)
        if risk_match:
            risk_per_trade = float(risk_match.group(1)) / 100.0

        # Extract Stop Loss
        sl_match = re.search(r"stop\s*loss\s*(?:of|at)?\s*([0-9.]+)\s*%", text)
        if sl_match:
            stop_loss_pct = float(sl_match.group(1)) / 100.0

        # Extract Take Profit
        tp_match = re.search(r"take\s*profit\s*(?:of|at)?\s*([0-9.]+)\s*%", text)
        if tp_match:
            take_profit_pct = float(tp_match.group(1)) / 100.0

        # 1. Check RSI conditions
        if "rsi" in text:
            # RSI Crosses Above / Below / Oversold
            rsi_cross_above = re.search(r"rsi\s*(?:crosses|crosses\s*above|>|greater\s*than)\s*([0-9]+)", text)
            rsi_cross_below = re.search(r"rsi\s*(?:crosses\s*below|<|less\s*than)\s*([0-9]+)", text)
            
            if rsi_cross_above:
                val = float(rsi_cross_above.group(1))
                entry_rules.append(StrategyRule(indicator="RSI", operator="crosses_above", value=val, period=14))
            elif rsi_cross_below:
                val = float(rsi_cross_below.group(1))
                entry_rules.append(StrategyRule(indicator="RSI", operator="less_than", value=val, period=14))
            elif "oversold" in text:
                entry_rules.append(StrategyRule(indicator="RSI", operator="crosses_above", value=30.0, period=14))

            # RSI Exit conditions
            rsi_exit = re.search(r"exit\s*when\s*rsi\s*(?:reaches|is\s*above|>|>=)\s*([0-9]+)", text)
            if rsi_exit:
                exit_rules.append(StrategyRule(indicator="RSI", operator="greater_than", value=float(rsi_exit.group(1)), period=14))
            elif "overbought" in text:
                exit_rules.append(StrategyRule(indicator="RSI", operator="greater_than", value=70.0, period=14))

        # 2. Check Moving Average conditions
        if "ema" in text or "sma" in text:
            ema_match = re.search(r"price\s*is\s*above\s*ema\s*([0-9]+)", text)
            if ema_match:
                period = int(ema_match.group(1))
                entry_rules.append(StrategyRule(indicator="EMA", operator="price_above", period=period))
            
            sma_cross = re.search(r"sma\s*([0-9]+)\s*crosses\s*above\s*sma\s*([0-9]+)", text)
            if sma_cross:
                fast_p = int(sma_cross.group(1))
                slow_p = int(sma_cross.group(2))
                entry_rules.append(StrategyRule(indicator="SMA", operator="crosses_above", period=fast_p, params={"slow_period": slow_p}))
                exit_rules.append(StrategyRule(indicator="SMA", operator="crosses_below", period=fast_p, params={"slow_period": slow_p}))

        # 3. Check MACD conditions
        if "macd" in text:
            if "cross" in text or "bullish" in text:
                entry_rules.append(StrategyRule(indicator="MACD", operator="crosses_above", period=12, params={"slow": 26, "signal": 9}))
                exit_rules.append(StrategyRule(indicator="MACD", operator="crosses_below", period=12, params={"slow": 26, "signal": 9}))

        # 4. Check Bollinger conditions
        if "bollinger" in text:
            if "lower" in text:
                entry_rules.append(StrategyRule(indicator="BOLLINGER", operator="price_touch_lower", period=20, params={"std": 2.0}))
            if "upper" in text:
                exit_rules.append(StrategyRule(indicator="BOLLINGER", operator="price_touch_upper", period=20, params={"std": 2.0}))

        # Defaults if under-specified
        if not entry_rules:
            entry_rules.append(StrategyRule(indicator="RSI", operator="crosses_above", value=30.0, period=14))
        if not exit_rules:
            exit_rules.append(StrategyRule(indicator="RSI", operator="greater_than", value=70.0, period=14))

        strategy_name = f"NL Generated ({target_symbol}): {prompt[:40]}..."
        
        return StrategySpec(
            id=f"strat_nl_{uuid.uuid4().hex[:8]}",
            name=strategy_name,
            description=prompt,
            symbol=target_symbol,
            symbols=[target_symbol],
            timeframe="1D",
            entry_rules=entry_rules,
            exit_rules=exit_rules,
            risk_config=StrategyRiskConfig(
                risk_per_trade=risk_per_trade,
                stop_loss_pct=stop_loss_pct,
                take_profit_pct=take_profit_pct,
                sizing_type=PositionSizingType.RISK_PERCENTAGE
            ),
            parameters={
                "nl_prompt": prompt,
                "parsed_indicators": [r.indicator for r in entry_rules + exit_rules]
            }
        )


class DynamicCompiledStrategy(BaseStrategy):
    """
    Executes compiled StrategySpec rules against streaming candlestick series.
    """

    def __init__(self, spec: StrategySpec):
        super().__init__(
            strategy_id=spec.id,
            name=spec.name,
            symbol=spec.symbol,
            symbols=spec.symbols,
            parameters=spec.parameters,
            risk_config=spec.risk_config,
        )
        self.spec = spec

    def initialize(self) -> None:
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) < 30:
            return None

        closes = df["close"].values
        highs = df["high"].values
        lows = df["low"].values
        volumes = df["volume"].values
        curr_price = candle.close

        # Evaluate Entry Rules (All must be True for BUY)
        entry_satisfied = True
        entry_reasons = []

        for rule in self.spec.entry_rules:
            ind = rule.indicator.upper()
            op = rule.operator
            val = float(rule.value) if rule.value is not None else 0.0
            period = rule.period or 14

            if ind == "RSI":
                rsi_arr = TechnicalIndicators.rsi(closes, period)
                if np.isnan(rsi_arr[-1]) or np.isnan(rsi_arr[-2]):
                    entry_satisfied = False
                    break
                if op == "crosses_above" and not (rsi_arr[-2] <= val and rsi_arr[-1] > val):
                    entry_satisfied = False
                elif op == "less_than" and not (rsi_arr[-1] < val):
                    entry_satisfied = False
                elif op == "greater_than" and not (rsi_arr[-1] > val):
                    entry_satisfied = False
                else:
                    entry_reasons.append(f"RSI({period}) condition ({op} {val}) met")

            elif ind == "EMA":
                ema_arr = TechnicalIndicators.ema(closes, period)
                if np.isnan(ema_arr[-1]):
                    entry_satisfied = False
                    break
                if op == "price_above" and not (curr_price > ema_arr[-1]):
                    entry_satisfied = False
                elif op == "price_below" and not (curr_price < ema_arr[-1]):
                    entry_satisfied = False
                else:
                    entry_reasons.append(f"Price vs EMA({period}) satisfied")

            elif ind == "SMA":
                slow_period = rule.params.get("slow_period", 30)
                fast_sma = TechnicalIndicators.sma(closes, period)
                slow_sma = TechnicalIndicators.sma(closes, slow_period)
                if np.isnan(fast_sma[-1]) or np.isnan(slow_sma[-1]) or np.isnan(fast_sma[-2]) or np.isnan(slow_sma[-2]):
                    entry_satisfied = False
                    break
                if op == "crosses_above" and not (fast_sma[-2] <= slow_sma[-2] and fast_sma[-1] > slow_sma[-1]):
                    entry_satisfied = False
                else:
                    entry_reasons.append(f"SMA({period}) crossed above SMA({slow_period})")

            elif ind == "BOLLINGER":
                upper, mid, lower, _ = TechnicalIndicators.bollinger_bands(closes, period, rule.params.get("std", 2.0))
                if np.isnan(lower[-1]):
                    entry_satisfied = False
                    break
                if op == "price_touch_lower" and not (curr_price <= lower[-1]):
                    entry_satisfied = False
                else:
                    entry_reasons.append(f"Price touched lower Bollinger band")

        if entry_satisfied and entry_reasons:
            stop_price = curr_price * (1.0 - self.risk_config.stop_loss_pct)
            target_price = curr_price * (1.0 + self.risk_config.take_profit_pct)
            return Signal(
                symbol=candle.symbol,
                direction=SignalDirection.BUY,
                confidence=0.85,
                signal_score=0.80,
                target_price=round(target_price, 2),
                stop_loss_price=round(stop_price, 2),
                strategy_id=self.strategy_id,
                reason_codes=entry_reasons,
                components=[
                    SignalComponent(name="dsl_compiler", score=0.85, weight=1.0, contribution=0.85, reason="; ".join(entry_reasons))
                ]
            )

        # Evaluate Exit Rules (Any met -> SELL)
        for rule in self.spec.exit_rules:
            ind = rule.indicator.upper()
            op = rule.operator
            val = float(rule.value) if rule.value is not None else 0.0
            period = rule.period or 14

            if ind == "RSI":
                rsi_arr = TechnicalIndicators.rsi(closes, period)
                if not np.isnan(rsi_arr[-1]) and op == "greater_than" and rsi_arr[-1] >= val:
                    return Signal(
                        symbol=candle.symbol,
                        direction=SignalDirection.SELL,
                        confidence=0.85,
                        signal_score=-0.80,
                        strategy_id=self.strategy_id,
                        reason_codes=[f"Exit triggered: RSI >= {val}"],
                        components=[
                            SignalComponent(name="dsl_compiler", score=-0.85, weight=1.0, contribution=-0.85, reason=f"RSI exceeded exit threshold {val}")
                        ]
                    )
            elif ind == "BOLLINGER":
                upper, _, _, _ = TechnicalIndicators.bollinger_bands(closes, period, 2.0)
                if not np.isnan(upper[-1]) and op == "price_touch_upper" and curr_price >= upper[-1]:
                    return Signal(
                        symbol=candle.symbol,
                        direction=SignalDirection.SELL,
                        confidence=0.85,
                        signal_score=-0.80,
                        strategy_id=self.strategy_id,
                        reason_codes=["Exit triggered: Upper Bollinger Band touch"],
                        components=[
                            SignalComponent(name="dsl_compiler", score=-0.85, weight=1.0, contribution=-0.85, reason="Upper Bollinger band reached")
                        ]
                    )

        return None


class StrategyCompiler:
    """End-to-end compiler from Natural Language / AST to executable strategy."""

    @classmethod
    def compile_from_prompt(cls, prompt: str, symbol: str = "AAPL") -> Tuple[StrategySpec, BaseStrategy]:
        spec = NaturalLanguageStrategyParser.parse(prompt, symbol)
        is_valid, errors = StrategyDSLValidator.validate_spec(spec.model_dump())
        if not is_valid:
            raise ValueError(f"Strategy validation failed: {', '.join(errors)}")
        
        executable = DynamicCompiledStrategy(spec)
        return spec, executable
