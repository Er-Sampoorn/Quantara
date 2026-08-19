"""
QUANTARA Portfolio Optimization & Asset Allocation Engine
Mathematical implementations of Risk Parity, Mean-Variance Markowitz, Minimum Variance, and Volatility Targeting.
"""

from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


class PortfolioOptimizer:
    """Calculates optimal asset allocations according to classic and modern portfolio theory."""

    @staticmethod
    def calculate_covariance_matrix(returns_df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        clean_df = returns_df.dropna()
        symbols = list(clean_df.columns)
        cov_matrix = clean_df.cov().values * 252.0  # Annualized covariance
        return cov_matrix, symbols

    @staticmethod
    def equal_weight(symbols: List[str]) -> Dict[str, float]:
        """Equal Weight Allocation."""
        n = len(symbols)
        if n == 0:
            return {}
        w = 1.0 / n
        return {s: round(w, 4) for s in symbols}

    @staticmethod
    def inverse_volatility(returns_df: pd.DataFrame) -> Dict[str, float]:
        """Allocates inversely proportional to asset volatility."""
        clean_df = returns_df.dropna()
        if clean_df.empty:
            return {}
        
        vols = clean_df.std() * np.sqrt(252)
        inv_vols = 1.0 / vols.replace(0, 1e-4)
        weights = inv_vols / inv_vols.sum()
        return {s: round(float(w), 4) for s, w in zip(clean_df.columns, weights)}

    @staticmethod
    def minimum_variance(returns_df: pd.DataFrame) -> Dict[str, float]:
        """Global Minimum Variance Portfolio."""
        cov, symbols = PortfolioOptimizer.calculate_covariance_matrix(returns_df)
        n = len(symbols)
        if n == 0:
            return {}
        if n == 1:
            return {symbols[0]: 1.0}

        try:
            inv_cov = np.linalg.pinv(cov)
            ones = np.ones(n)
            w = np.dot(inv_cov, ones) / np.dot(ones, np.dot(inv_cov, ones))
            # Bound long-only weights [0, 1]
            w = np.maximum(0, w)
            w = w / np.sum(w)
            return {s: round(float(weight), 4) for s, weight in zip(symbols, w)}
        except Exception:
            return PortfolioOptimizer.equal_weight(symbols)

    @staticmethod
    def max_sharpe(
        returns_df: pd.DataFrame,
        risk_free_rate: float = 0.04
    ) -> Dict[str, float]:
        """Maximum Sharpe Ratio Portfolio (Tangency Portfolio)."""
        clean_df = returns_df.dropna()
        symbols = list(clean_df.columns)
        n = len(symbols)
        if n == 0:
            return {}
        if n == 1:
            return {symbols[0]: 1.0}

        mean_returns = clean_df.mean().values * 252.0
        cov, _ = PortfolioOptimizer.calculate_covariance_matrix(returns_df)

        try:
            excess_returns = mean_returns - risk_free_rate
            inv_cov = np.linalg.pinv(cov)
            w = np.dot(inv_cov, excess_returns)
            # Long-only clamp
            w = np.maximum(0, w)
            if np.sum(w) > 0:
                w = w / np.sum(w)
            else:
                return PortfolioOptimizer.equal_weight(symbols)
            return {s: round(float(weight), 4) for s, weight in zip(symbols, w)}
        except Exception:
            return PortfolioOptimizer.equal_weight(symbols)

    @staticmethod
    def risk_parity(returns_df: pd.DataFrame, max_iter: int = 100) -> Dict[str, float]:
        """Equal Risk Contribution (Risk Parity) using iterative convergence."""
        cov, symbols = PortfolioOptimizer.calculate_covariance_matrix(returns_df)
        n = len(symbols)
        if n == 0:
            return {}
        if n == 1:
            return {symbols[0]: 1.0}

        # Initialize with inverse volatility
        vols = np.sqrt(np.diag(cov))
        inv_vols = 1.0 / np.where(vols == 0, 1e-4, vols)
        w = inv_vols / np.sum(inv_vols)

        target_risk = 1.0 / n
        learning_rate = 0.05

        for _ in range(max_iter):
            port_vol = np.sqrt(np.dot(w.T, np.dot(cov, w)))
            if port_vol == 0:
                break
            marginal_risk = np.dot(cov, w) / port_vol
            risk_contrib = (w * marginal_risk) / port_vol
            error = risk_contrib - target_risk
            
            if np.max(np.abs(error)) < 1e-4:
                break
                
            w = w - learning_rate * error
            w = np.maximum(1e-4, w)
            w = w / np.sum(w)

        return {s: round(float(weight), 4) for s, weight in zip(symbols, w)}
