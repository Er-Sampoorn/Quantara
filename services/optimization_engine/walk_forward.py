"""
QUANTARA Walk-Forward Validation Engine
Rolling chronological in-sample / out-of-sample window validation with Walk-Forward Efficiency (WFE).
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple
import numpy as np
from packages.backtesting.engine import BacktestEngine
from packages.domain.models import Candle
from packages.strategies.registry import StrategyRegistry


class WalkForwardEngine:
    """
    Executes chronological sliding window train/test splits.
    Guarantees out-of-sample testing without look-ahead contamination.
    """

    @classmethod
    def evaluate(
        cls,
        strategy_type: str,
        symbol: str,
        candles: List[Candle],
        parameter_grid: Dict[str, List[Any]],
        num_splits: int = 4,
        train_ratio: float = 0.70,
    ) -> Dict[str, Any]:
        if len(candles) < 100:
            raise ValueError("Insufficient candle history for walk-forward validation (requires >= 100 bars).")

        sorted_candles = sorted(candles, key=lambda c: c.timestamp)
        n = len(sorted_candles)
        window_size = int(n / num_splits)
        
        in_sample_sharpes: List[float] = []
        out_sample_sharpes: List[float] = []
        split_reports: List[Dict[str, Any]] = []

        backtester = BacktestEngine()

        for i in range(num_splits):
            start_idx = i * int(window_size * 0.5)
            end_idx = min(n, start_idx + window_size)
            split_candles = sorted_candles[start_idx:end_idx]
            if len(split_candles) < 30:
                continue

            split_point = int(len(split_candles) * train_ratio)
            train_candles = split_candles[:split_point]
            test_candles = split_candles[split_point:]

            if not train_candles or not test_candles:
                continue

            # In-Sample Optimization / Best parameter selection
            best_params = {}
            best_is_sharpe = -999.0

            # Test basic parameter combinations
            keys = list(parameter_grid.keys())
            param_vals = [parameter_grid[k] for k in keys]
            combinations = [dict(zip(keys, v)) for v in param_vals] if param_vals else [{}]

            for p in combinations[:5]:
                strat = StrategyRegistry.create_strategy(
                    strategy_type=strategy_type,
                    strategy_id=f"wf_is_{i}",
                    name=f"WF IS Split {i}",
                    symbol=symbol,
                    parameters=p
                )
                is_res = backtester.run(strat, train_candles)
                if is_res.metrics.sharpe_ratio > best_is_sharpe:
                    best_is_sharpe = is_res.metrics.sharpe_ratio
                    best_params = p

            # Out-of-Sample Evaluation with chosen parameters
            oos_strat = StrategyRegistry.create_strategy(
                strategy_type=strategy_type,
                strategy_id=f"wf_oos_{i}",
                name=f"WF OOS Split {i}",
                symbol=symbol,
                parameters=best_params
            )
            oos_res = backtester.run(oos_strat, test_candles)
            oos_sharpe = oos_res.metrics.sharpe_ratio

            in_sample_sharpes.append(max(0.01, best_is_sharpe))
            out_sample_sharpes.append(oos_sharpe)

            split_reports.append({
                "split": i + 1,
                "train_range": f"{train_candles[0].timestamp.strftime('%Y-%m-%d')} to {train_candles[-1].timestamp.strftime('%Y-%m-%d')}",
                "test_range": f"{test_candles[0].timestamp.strftime('%Y-%m-%d')} to {test_candles[-1].timestamp.strftime('%Y-%m-%d')}",
                "in_sample_sharpe": round(float(best_is_sharpe), 2),
                "out_of_sample_sharpe": round(float(oos_sharpe), 2),
                "out_of_sample_return_pct": oos_res.metrics.total_return_pct,
                "chosen_parameters": best_params,
            })

        mean_is = float(np.mean(in_sample_sharpes)) if in_sample_sharpes else 1.0
        mean_oos = float(np.mean(out_sample_sharpes)) if out_sample_sharpes else 0.0
        wfe = round(float(mean_oos / mean_is) if mean_is > 0 else 0.0, 3)

        is_robust = wfe >= 0.55

        return {
            "strategy_type": strategy_type,
            "symbol": symbol,
            "walk_forward_efficiency": wfe,
            "mean_in_sample_sharpe": round(mean_is, 2),
            "mean_out_sample_sharpe": round(mean_oos, 2),
            "is_robust": is_robust,
            "splits": split_reports,
            "verdict": "Strategy passes Walk-Forward Robustness Test (WFE >= 0.55)" if is_robust else "Warning: Strategy exhibits out-of-sample decay / potential curve-fitting",
        }
