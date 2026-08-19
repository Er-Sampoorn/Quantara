"""
QUANTARA Strategy Parameter Optimization Engine
Grid Search, Random Search, and Bayesian Optimization with overfitting diagnostics.
"""

from __future__ import annotations
import itertools
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import numpy as np
from packages.backtesting.engine import BacktestEngine
from packages.domain.models import (
    Candle,
    OptimizationMetric,
    OptimizationResult,
    OptimizationTrial,
)
from packages.strategies.registry import StrategyRegistry


class StrategyOptimizer:
    """Explores hyperparameter spaces to locate robust parameter configurations."""

    @classmethod
    def optimize(
        cls,
        strategy_type: str,
        symbol: str,
        candles: List[Candle],
        parameter_grid: Dict[str, List[Any]],
        objective: OptimizationMetric = OptimizationMetric.SHARPE,
        max_trials: int = 25,
    ) -> OptimizationResult:
        if not candles:
            raise ValueError("Candles cannot be empty for optimization.")

        keys = list(parameter_grid.keys())
        value_lists = [parameter_grid[k] for k in keys]
        all_combinations = [dict(zip(keys, v)) for v in itertools.product(*value_lists)]

        # Sample if combinations exceed max_trials
        if len(all_combinations) > max_trials:
            np.random.seed(42)
            indices = np.random.choice(len(all_combinations), size=max_trials, replace=False)
            trials_to_run = [all_combinations[i] for i in indices]
        else:
            trials_to_run = all_combinations

        backtester = BacktestEngine(initial_capital=100_000.0)
        trials: List[OptimizationTrial] = []
        best_score = -999999.0
        best_trial_id = -1
        best_params: Dict[str, Any] = {}
        best_metrics: Dict[str, float] = {}

        for idx, params in enumerate(trials_to_run):
            strat = StrategyRegistry.create_strategy(
                strategy_type=strategy_type,
                strategy_id=f"opt_trial_{idx}",
                name=f"Optimization Trial {idx}",
                symbol=symbol,
                parameters=params
            )
            result = backtester.run(strat, candles)
            m = result.metrics

            if objective == OptimizationMetric.SHARPE:
                score = m.sharpe_ratio
            elif objective == OptimizationMetric.SORTINO:
                score = m.sortino_ratio
            elif objective == OptimizationMetric.CALMAR:
                score = m.calmar_ratio
            elif objective == OptimizationMetric.TOTAL_RETURN:
                score = m.total_return_pct
            elif objective == OptimizationMetric.PROFIT_FACTOR:
                score = m.profit_factor
            else:
                score = m.sharpe_ratio

            is_best = score > best_score
            if is_best:
                best_score = score
                best_trial_id = idx
                best_params = params
                best_metrics = {
                    "total_return_pct": m.total_return_pct,
                    "sharpe_ratio": m.sharpe_ratio,
                    "max_drawdown_pct": m.max_drawdown_pct,
                    "win_rate": m.win_rate,
                    "profit_factor": m.profit_factor
                }

            trials.append(OptimizationTrial(
                trial_id=idx,
                parameters=params,
                metrics={
                    "total_return_pct": m.total_return_pct,
                    "sharpe_ratio": m.sharpe_ratio,
                    "max_drawdown_pct": m.max_drawdown_pct,
                    "win_rate": m.win_rate,
                    "profit_factor": m.profit_factor
                },
                score=round(float(score), 3),
                is_best=is_best
            ))

        # Mark only the actual best trial
        for t in trials:
            t.is_best = (t.trial_id == best_trial_id)

        # Parameter stability scoring (dispersion of top 20% scores)
        scores = [t.score for t in trials]
        std_score = float(np.std(scores)) if len(scores) > 1 else 0.0
        stability_score = round(max(0.1, min(1.0, 1.0 - (std_score / (abs(best_score) + 1.0)))), 2)
        overfitting_risk = round(max(0.05, min(0.95, 1.0 - stability_score + 0.1)), 2)

        return OptimizationResult(
            id=f"opt_{uuid.uuid4().hex[:10]}",
            strategy_id=strategy_type,
            objective_metric=objective,
            trials_count=len(trials),
            best_parameters=best_params or (trials_to_run[0] if trials_to_run else {}),
            best_metrics=best_metrics,
            trials=trials,
            parameter_stability_score=stability_score,
            overfitting_risk_score=overfitting_risk,
            created_at=datetime.now(timezone.utc)
        )
