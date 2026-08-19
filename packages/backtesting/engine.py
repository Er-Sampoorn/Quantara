"""
QUANTARA Event-Driven Backtesting Engine
Deterministic chronological backtest runner with realistic fees, slippage, and position tracking.
"""

from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from packages.backtesting.metrics import MetricsCalculator
from packages.domain.models import (
    BacktestMetrics,
    BacktestResult,
    Candle,
    EquityPoint,
    ExecutionMode,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    Portfolio,
    Position,
    PositionSizingType,
    SignalDirection,
    Trade,
)
from packages.risk.engine import RiskEngine
from packages.risk.sizing import PositionSizer
from packages.strategies.base import BaseStrategy


class BacktestEngine:
    """
    Event-driven deterministic backtest simulator.
    Ensures zero look-ahead bias by strictly feeding candles one-by-one in chronological order.
    """

    def __init__(
        self,
        initial_capital: float = 100_000.0,
        commission_per_share: float = 0.005,
        min_commission: float = 1.0,
        slippage_bps: float = 3.0,
        risk_engine: Optional[RiskEngine] = None,
    ):
        self.initial_capital = initial_capital
        self.commission_per_share = commission_per_share
        self.min_commission = min_commission
        self.slippage_bps = slippage_bps
        self.risk_engine = risk_engine or RiskEngine()

    def run(
        self,
        strategy: BaseStrategy,
        candles: List[Candle],
        timeframe: str = "1D",
    ) -> BacktestResult:
        if not candles:
            raise ValueError("Cannot run backtest with empty candle series.")

        # Sort strictly chronologically
        sorted_candles = sorted(candles, key=lambda c: c.timestamp)
        symbol = sorted_candles[0].symbol
        start_date = sorted_candles[0].timestamp
        end_date = sorted_candles[-1].timestamp

        # Initialize portfolio state
        cash: float = self.initial_capital
        position: Optional[Position] = None
        open_trade: Optional[Dict] = None

        trades: List[Trade] = []
        equity_curve: List[EquityPoint] = []
        peak_equity: float = self.initial_capital

        strategy.initialize()

        for candle in sorted_candles:
            curr_price = candle.close
            
            # 1. Update existing open position value
            if position:
                position.current_price = curr_price
                position.market_value = position.quantity * curr_price
                position.unrealized_pnl = (curr_price - position.entry_price) * position.quantity
                position.unrealized_pnl_pct = (position.unrealized_pnl / (position.entry_price * position.quantity)) if position.entry_price > 0 else 0.0

            # 2. Compute current total equity
            current_pos_val = position.market_value if position else 0.0
            total_equity = cash + current_pos_val
            peak_equity = max(peak_equity, total_equity)
            dd_pct = (peak_equity - total_equity) / peak_equity if peak_equity > 0 else 0.0

            equity_curve.append(EquityPoint(
                timestamp=candle.timestamp,
                equity=round(total_equity, 2),
                cash=round(cash, 2),
                drawdown_pct=round(dd_pct, 4)
            ))

            # 3. Feed bar into strategy
            signal = strategy.on_bar(candle)

            if not signal:
                continue

            # Build mock portfolio state for risk verification
            pos_dict = {symbol: position} if position else {}
            portfolio_state = Portfolio(
                user_id="backtest_user",
                cash=cash,
                initial_balance=self.initial_capital,
                equity=total_equity,
                unrealized_pnl=position.unrealized_pnl if position else 0.0,
                drawdown_pct=dd_pct,
                positions=pos_dict,
                execution_mode=ExecutionMode.BACKTEST,
                updated_at=candle.timestamp
            )

            # 4. Process BUY Signal
            if signal.direction == SignalDirection.BUY and position is None:
                # Position Sizing
                target_qty = PositionSizer.calculate_quantity(
                    sizing_type=strategy.risk_config.sizing_type,
                    portfolio_equity=total_equity,
                    current_price=curr_price,
                    risk_per_trade_pct=strategy.risk_config.risk_per_trade,
                    stop_loss_price=signal.stop_loss_price
                )

                if target_qty <= 0:
                    continue

                order = Order(
                    symbol=symbol,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    quantity=target_qty,
                    strategy_id=strategy.strategy_id,
                    execution_mode=ExecutionMode.BACKTEST,
                    created_at=candle.timestamp
                )

                # Risk Gate Check
                risk_eval = self.risk_engine.evaluate_order(order, portfolio_state, curr_price)
                if not risk_eval.approved:
                    continue

                # Simulate execution with slippage and commission
                slippage_mult = 1.0 + (self.slippage_bps / 10000.0)
                exec_price = curr_price * slippage_mult
                commission = max(self.min_commission, target_qty * self.commission_per_share)
                cost = (exec_price * target_qty) + commission

                if cash >= cost:
                    cash -= cost
                    position = Position(
                        symbol=symbol,
                        quantity=target_qty,
                        entry_price=exec_price,
                        current_price=exec_price,
                        market_value=target_qty * exec_price,
                        unrealized_pnl=0.0,
                        unrealized_pnl_pct=0.0,
                        side=OrderSide.BUY,
                        opened_at=candle.timestamp,
                        updated_at=candle.timestamp
                    )
                    open_trade = {
                        "symbol": symbol,
                        "side": OrderSide.BUY,
                        "entry_price": exec_price,
                        "quantity": target_qty,
                        "entry_time": candle.timestamp,
                        "entry_reason": signal.reason_codes[0] if signal.reason_codes else "STRATEGY_BUY",
                        "fees": commission,
                        "slippage": (exec_price - curr_price) * target_qty
                    }

            # 5. Process SELL Signal (Exit Position)
            elif signal.direction == SignalDirection.SELL and position is not None:
                slippage_mult = 1.0 - (self.slippage_bps / 10000.0)
                exec_price = curr_price * slippage_mult
                commission = max(self.min_commission, position.quantity * self.commission_per_share)
                revenue = (exec_price * position.quantity) - commission

                cash += revenue
                pnl = (exec_price - position.entry_price) * position.quantity - (open_trade["fees"] + commission) if open_trade else 0.0
                pnl_pct = pnl / (position.entry_price * position.quantity) if position.entry_price > 0 else 0.0

                holding_seconds = (candle.timestamp - open_trade["entry_time"]).total_seconds() if open_trade else 0.0

                trade = Trade(
                    symbol=symbol,
                    strategy_id=strategy.strategy_id,
                    side=OrderSide.BUY,
                    entry_price=round(position.entry_price, 4),
                    exit_price=round(exec_price, 4),
                    quantity=position.quantity,
                    pnl=round(pnl, 2),
                    pnl_pct=round(pnl_pct, 4),
                    entry_time=open_trade["entry_time"] if open_trade else candle.timestamp,
                    exit_time=candle.timestamp,
                    fees=round(open_trade["fees"] + commission if open_trade else commission, 2),
                    slippage=round(open_trade["slippage"] + (curr_price - exec_price) * position.quantity if open_trade else 0.0, 2),
                    holding_period_seconds=holding_seconds,
                    entry_reason=open_trade["entry_reason"] if open_trade else "ENTRY",
                    exit_reason=signal.reason_codes[0] if signal.reason_codes else "STRATEGY_EXIT"
                )
                trades.append(trade)
                position = None
                open_trade = None

        # Calculate final metrics
        metrics = MetricsCalculator.calculate_metrics(self.initial_capital, equity_curve, trades)
        monthly_returns = MetricsCalculator.calculate_monthly_returns(equity_curve)

        # Generate unique reproducibility hash
        raw_hash_str = f"{strategy.strategy_id}:{symbol}:{start_date.isoformat()}:{end_date.isoformat()}:{json.dumps(strategy.parameters, sort_keys=True)}"
        repro_hash = hashlib.sha256(raw_hash_str.encode()).hexdigest()[:16]

        final_equity = equity_curve[-1].equity if equity_curve else self.initial_capital

        return BacktestResult(
            strategy_id=strategy.strategy_id,
            strategy_name=strategy.name,
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            final_equity=final_equity,
            metrics=metrics,
            equity_curve=equity_curve,
            trades=trades,
            monthly_returns=monthly_returns,
            parameters=dict(strategy.parameters),
            reproducibility_hash=repro_hash,
            created_at=datetime.now(timezone.utc)
        )
