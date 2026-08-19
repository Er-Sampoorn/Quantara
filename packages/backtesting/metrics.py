"""
QUANTARA Quantitative Backtest Metrics Calculator
Pure mathematical computation of performance, drawdown, risk-adjusted returns, and tail risk metrics.
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from packages.domain.models import BacktestMetrics, EquityPoint, Trade


class MetricsCalculator:
    """Computes comprehensive quantitative performance and risk metrics."""

    @staticmethod
    def calculate_metrics(
        initial_capital: float,
        equity_curve: List[EquityPoint],
        trades: List[Trade],
        risk_free_rate: float = 0.04,  # 4% annual risk-free rate
        periods_per_year: int = 252,   # Daily bars
    ) -> BacktestMetrics:
        if not equity_curve or len(equity_curve) < 2:
            return BacktestMetrics(
                total_return=0.0,
                total_return_pct=0.0,
                cagr=0.0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                calmar_ratio=0.0,
                max_drawdown=0.0,
                max_drawdown_pct=0.0,
                win_rate=0.0,
                loss_rate=0.0,
                profit_factor=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                average_win=0.0,
                average_loss=0.0,
                expectancy=0.0,
                recovery_factor=0.0,
                annualized_volatility=0.0,
                var_95=0.0,
                cvar_95=0.0,
                beta=1.0,
                alpha=0.0,
                max_consecutive_losses=0,
            )

        equities = np.array([ep.equity for ep in equity_curve], dtype=float)
        final_equity = equities[-1]
        total_return = final_equity - initial_capital
        total_return_pct = (total_return / initial_capital) if initial_capital > 0 else 0.0

        # Daily returns
        returns = np.diff(equities) / equities[:-1]
        returns = np.nan_to_num(returns, nan=0.0, posinf=0.0, neginf=0.0)

        # CAGR
        days = (equity_curve[-1].timestamp - equity_curve[0].timestamp).days
        years = max(1.0 / periods_per_year, days / 365.25)
        cagr = ((final_equity / initial_capital) ** (1.0 / years)) - 1.0 if initial_capital > 0 and final_equity > 0 else 0.0

        # Annualized Volatility
        daily_std = np.std(returns, ddof=1) if len(returns) > 1 else 0.0
        annualized_vol = float(daily_std * math.sqrt(periods_per_year))

        # Sharpe Ratio
        daily_rf = risk_free_rate / periods_per_year
        excess_returns = returns - daily_rf
        mean_excess = np.mean(excess_returns) if len(excess_returns) > 0 else 0.0
        sharpe = float((mean_excess / daily_std) * math.sqrt(periods_per_year)) if daily_std > 1e-8 else 0.0

        # Sortino Ratio (downside deviation)
        negative_excess = np.where(excess_returns < 0, excess_returns, 0.0)
        downside_std = np.sqrt(np.mean(negative_excess ** 2)) if len(negative_excess) > 0 else 0.0
        sortino = float((mean_excess / downside_std) * math.sqrt(periods_per_year)) if downside_std > 1e-8 else 0.0

        # Drawdown calculation
        peak = np.maximum.accumulate(equities)
        drawdowns = (equities - peak) / peak
        max_dd_pct = float(abs(np.min(drawdowns))) if len(drawdowns) > 0 else 0.0
        max_dd_dollar = float(np.max(peak - equities)) if len(peak) > 0 else 0.0

        # Calmar Ratio
        calmar = (cagr / max_dd_pct) if max_dd_pct > 1e-6 else (cagr * 10.0)

        # Value at Risk (VaR 95%) and Conditional VaR (CVaR 95%)
        if len(returns) > 10:
            var_95 = float(abs(np.percentile(returns, 5)))
            tail_losses = returns[returns <= -var_95]
            cvar_95 = float(abs(np.mean(tail_losses))) if len(tail_losses) > 0 else var_95
        else:
            var_95 = 0.0
            cvar_95 = 0.0

        # Trade metrics
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl < 0]

        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / total_trades) if total_trades > 0 else 0.0
        loss_rate = (loss_count / total_trades) if total_trades > 0 else 0.0

        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 1e-6 else (gross_profit if gross_profit > 0 else 1.0)

        avg_win = (gross_profit / win_count) if win_count > 0 else 0.0
        avg_loss = (gross_loss / loss_count) if loss_count > 0 else 0.0

        expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
        recovery_factor = (total_return / max_dd_dollar) if max_dd_dollar > 1e-6 else 0.0

        # Max consecutive losses
        max_cons_losses = 0
        current_cons = 0
        for t in trades:
            if t.pnl < 0:
                current_cons += 1
                max_cons_losses = max(max_cons_losses, current_cons)
            else:
                current_cons = 0

        return BacktestMetrics(
            total_return=round(float(total_return), 2),
            total_return_pct=round(float(total_return_pct), 4),
            cagr=round(float(cagr), 4),
            sharpe_ratio=round(float(sharpe), 3),
            sortino_ratio=round(float(sortino), 3),
            calmar_ratio=round(float(calmar), 3),
            max_drawdown=round(float(max_dd_dollar), 2),
            max_drawdown_pct=round(float(max_dd_pct), 4),
            win_rate=round(float(win_rate), 4),
            loss_rate=round(float(loss_rate), 4),
            profit_factor=round(float(profit_factor), 3),
            total_trades=total_trades,
            winning_trades=win_count,
            losing_trades=loss_count,
            average_win=round(float(avg_win), 2),
            average_loss=round(float(avg_loss), 2),
            expectancy=round(float(expectancy), 2),
            recovery_factor=round(float(recovery_factor), 3),
            annualized_volatility=round(float(annualized_vol), 4),
            var_95=round(float(var_95), 4),
            cvar_95=round(float(cvar_95), 4),
            beta=1.0,
            alpha=round(float(cagr - risk_free_rate), 4),
            max_consecutive_losses=max_cons_losses,
        )

    @staticmethod
    def calculate_monthly_returns(equity_curve: List[EquityPoint]) -> Dict[str, float]:
        """Groups equity snapshots by Year-Month and computes monthly returns."""
        if not equity_curve:
            return {}
        
        df = pd.DataFrame([{"date": ep.timestamp, "equity": ep.equity} for ep in equity_curve])
        df["year_month"] = df["date"].dt.strftime("%Y-%m")
        grouped = df.groupby("year_month")
        
        monthly = {}
        for ym, group in grouped:
            first_eq = group["equity"].iloc[0]
            last_eq = group["equity"].iloc[-1]
            ret = (last_eq - first_eq) / first_eq if first_eq > 0 else 0.0
            monthly[ym] = round(float(ret), 4)
            
        return monthly
