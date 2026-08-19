"""
QUANTARA Monte Carlo Trade Simulation Engine
Bootstraps historical trade returns to generate risk distributions, probability of profit, and drawdown percentiles.
"""

from __future__ import annotations
from typing import Dict, List
import numpy as np
from packages.domain.models import MonteCarloSimulationResult, Trade


class MonteCarloEngine:
    """Simulates alternate sequences of trades to evaluate tail risks and ruin probabilities."""

    @classmethod
    def simulate(
        cls,
        trades: List[Trade],
        initial_capital: float = 100_000.0,
        num_simulations: int = 1000,
        sample_path_count: int = 10,
    ) -> MonteCarloSimulationResult:
        if not trades:
            return MonteCarloSimulationResult(
                simulations_count=num_simulations,
                confidence_intervals={"drawdown": {"5%": 0.0, "50%": 0.0, "95%": 0.0}},
                probability_of_profit=0.5,
                probability_of_ruin=0.0,
                median_ending_equity=initial_capital,
                worst_case_drawdown=0.0,
                sample_equity_curves=[]
            )

        trade_pnls = np.array([t.pnl for t in trades], dtype=float)
        n_trades = len(trade_pnls)
        
        ending_equities: List[float] = []
        max_drawdowns: List[float] = []
        sample_curves: List[List[float]] = []

        np.random.seed(42)

        for sim_idx in range(num_simulations):
            # Resample with replacement
            sampled_pnls = np.random.choice(trade_pnls, size=n_trades, replace=True)
            equity_path = np.zeros(n_trades + 1)
            equity_path[0] = initial_capital
            
            for i, pnl in enumerate(sampled_pnls):
                equity_path[i + 1] = max(0.0, equity_path[i] + pnl)

            peak = np.maximum.accumulate(equity_path)
            dd_pct = np.max((peak - equity_path) / peak) if np.max(peak) > 0 else 0.0

            ending_equities.append(float(equity_path[-1]))
            max_drawdowns.append(float(dd_pct))

            if sim_idx < sample_path_count:
                sample_curves.append([round(float(val), 2) for val in equity_path])

        ending_arr = np.array(ending_equities)
        dd_arr = np.array(max_drawdowns)

        prob_profit = float(np.mean(ending_arr > initial_capital))
        prob_ruin = float(np.mean(ending_arr < initial_capital * 0.50))  # 50% capital loss ruin threshold

        confidence_intervals = {
            "ending_equity": {
                "5%": round(float(np.percentile(ending_arr, 5)), 2),
                "50%": round(float(np.percentile(ending_arr, 50)), 2),
                "95%": round(float(np.percentile(ending_arr, 95)), 2),
            },
            "max_drawdown_pct": {
                "5%": round(float(np.percentile(dd_arr, 5)), 4),
                "50%": round(float(np.percentile(dd_arr, 50)), 4),
                "95%": round(float(np.percentile(dd_arr, 95)), 4),
            }
        }

        return MonteCarloSimulationResult(
            simulations_count=num_simulations,
            confidence_intervals=confidence_intervals,
            probability_of_profit=round(prob_profit, 4),
            probability_of_ruin=round(prob_ruin, 4),
            median_ending_equity=round(float(np.median(ending_arr)), 2),
            worst_case_drawdown=round(float(np.max(dd_arr)), 4),
            sample_equity_curves=sample_curves
        )
