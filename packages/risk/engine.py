"""
QUANTARA Risk Engine & Pre-Trade Hard Gate
Deterministic risk evaluation preventing unauthorized or dangerous trade execution.
"""

from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from packages.domain.models import (
    Order,
    OrderSide,
    Portfolio,
    RiskCheckResult,
    RiskEvaluation,
    RiskRule,
)
from packages.events.bus import default_event_bus
from packages.events.types import DomainEvent, EventType

logger = logging.getLogger("quantara.risk_engine")


class RiskEngine:
    """
    Deterministic Risk Gate.
    All orders (Backtest, Paper, or Live) must receive an APPROVED evaluation before submission.
    """

    def __init__(
        self,
        max_position_size_pct: float = 0.20,      # Max 20% of portfolio equity in a single asset
        max_portfolio_leverage: float = 1.5,       # Max 1.5x total exposure
        daily_loss_limit_pct: float = 0.04,        # Circuit breaker if down > 4% in a single day
        max_drawdown_limit_pct: float = 0.15,      # Circuit breaker if drawdown > 15%
        max_open_positions: int = 15,              # Max concurrent open positions
    ):
        self.max_position_size_pct = max_position_size_pct
        self.max_portfolio_leverage = max_portfolio_leverage
        self.daily_loss_limit_pct = daily_loss_limit_pct
        self.max_drawdown_limit_pct = max_drawdown_limit_pct
        self.max_open_positions = max_open_positions
        
        self.circuit_breaker_tripped: bool = False
        self.circuit_breaker_reason: Optional[str] = None
        self.custom_rules: List[RiskRule] = []

    def trip_circuit_breaker(self, reason: str) -> None:
        self.circuit_breaker_tripped = True
        self.circuit_breaker_reason = reason
        logger.critical(f"RISK CIRCUIT BREAKER TRIPPED: {reason}")

    def reset_circuit_breaker(self) -> None:
        self.circuit_breaker_tripped = False
        self.circuit_breaker_reason = None
        logger.info("Risk Circuit Breaker manually reset.")

    def evaluate_order(
        self,
        order: Order,
        portfolio: Portfolio,
        current_market_price: float
    ) -> RiskEvaluation:
        """
        Deterministic pre-trade verification.
        Returns a RiskEvaluation with approved=True/False and detailed rule diagnostics.
        """
        results: List[RiskCheckResult] = []
        rejections: List[str] = []

        now = datetime.now(timezone.utc)
        order_cost = order.quantity * current_market_price
        equity = max(1.0, portfolio.equity)

        # 1. Check Circuit Breaker
        if self.circuit_breaker_tripped:
            reason = f"Global risk circuit breaker active: {self.circuit_breaker_reason}"
            rejections.append(reason)
            results.append(RiskCheckResult(
                passed=False,
                rule_name="CIRCUIT_BREAKER_CHECK",
                requested_value=1.0,
                threshold_value=0.0,
                message=reason,
                timestamp=now
            ))
            return RiskEvaluation(approved=False, evaluations=results, rejected_reasons=rejections, timestamp=now)

        # 2. Maximum Drawdown Check
        if portfolio.drawdown_pct >= self.max_drawdown_limit_pct:
            reason = f"Portfolio drawdown {portfolio.drawdown_pct*100:.1f}% exceeds max allowed {self.max_drawdown_limit_pct*100:.1f}%"
            self.trip_circuit_breaker(reason)
            rejections.append(reason)
            results.append(RiskCheckResult(
                passed=False,
                rule_name="MAX_DRAWDOWN_LIMIT",
                requested_value=portfolio.drawdown_pct,
                threshold_value=self.max_drawdown_limit_pct,
                message=reason,
                timestamp=now
            ))

        # 3. Maximum Open Positions Count (only applies to opening new symbols)
        if order.side == OrderSide.BUY and order.symbol not in portfolio.positions:
            current_positions_count = len(portfolio.positions)
            if current_positions_count >= self.max_open_positions:
                reason = f"Maximum open positions limit reached ({current_positions_count}/{self.max_open_positions})"
                rejections.append(reason)
                results.append(RiskCheckResult(
                    passed=False,
                    rule_name="MAX_OPEN_POSITIONS",
                    requested_value=float(current_positions_count + 1),
                    threshold_value=float(self.max_open_positions),
                    message=reason,
                    timestamp=now
                ))
            else:
                results.append(RiskCheckResult(
                    passed=True,
                    rule_name="MAX_OPEN_POSITIONS",
                    requested_value=float(current_positions_count),
                    threshold_value=float(self.max_open_positions),
                    message="Open positions count within limits",
                    timestamp=now
                ))

        # 4. Maximum Position Size Limit
        if order.side == OrderSide.BUY:
            existing_pos_val = portfolio.positions[order.symbol].market_value if order.symbol in portfolio.positions else 0.0
            new_total_val = existing_pos_val + order_cost
            new_pos_pct = new_total_val / equity
            
            if new_pos_pct > self.max_position_size_pct:
                reason = f"Order position size {new_pos_pct*100:.1f}% exceeds max single-asset allocation {self.max_position_size_pct*100:.1f}%"
                rejections.append(reason)
                results.append(RiskCheckResult(
                    passed=False,
                    rule_name="MAX_POSITION_SIZE",
                    requested_value=new_pos_pct,
                    threshold_value=self.max_position_size_pct,
                    message=reason,
                    timestamp=now
                ))
            else:
                results.append(RiskCheckResult(
                    passed=True,
                    rule_name="MAX_POSITION_SIZE",
                    requested_value=new_pos_pct,
                    threshold_value=self.max_position_size_pct,
                    message="Position sizing within risk parameters",
                    timestamp=now
                ))

        # 5. Maximum Total Portfolio Leverage
        if order.side == OrderSide.BUY:
            current_gross_exposure = sum(p.market_value for p in portfolio.positions.values())
            new_gross_exposure = current_gross_exposure + order_cost
            new_leverage = new_gross_exposure / equity

            if new_leverage > self.max_portfolio_leverage:
                reason = f"New portfolio leverage {new_leverage:.2f}x exceeds maximum permitted leverage {self.max_portfolio_leverage:.2f}x"
                rejections.append(reason)
                results.append(RiskCheckResult(
                    passed=False,
                    rule_name="MAX_PORTFOLIO_LEVERAGE",
                    requested_value=new_leverage,
                    threshold_value=self.max_portfolio_leverage,
                    message=reason,
                    timestamp=now
                ))
            else:
                results.append(RiskCheckResult(
                    passed=True,
                    rule_name="MAX_PORTFOLIO_LEVERAGE",
                    requested_value=new_leverage,
                    threshold_value=self.max_portfolio_leverage,
                    message="Portfolio leverage within safety boundaries",
                    timestamp=now
                ))

        is_approved = len(rejections) == 0
        return RiskEvaluation(
            approved=is_approved,
            evaluations=results,
            rejected_reasons=rejections,
            recommended_quantity=order.quantity if is_approved else None,
            timestamp=now
        )


# Global Singleton Risk Gate
default_risk_engine = RiskEngine()
