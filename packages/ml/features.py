"""
QUANTARA ML Feature Engineering Pipeline
Constructs stationary, normalized, leak-free feature vectors for quantitative modeling.
"""

from __future__ import annotations
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from packages.indicators.technical import TechnicalIndicators


class FeaturePipeline:
    """Computes technical, price, and volume features with strict chronological separation."""

    @staticmethod
    def extract_features(
        df_candles: pd.DataFrame,
        benchmark_returns: Optional[pd.Series] = None
    ) -> pd.DataFrame:
        """
        Expects df_candles with columns: ['timestamp', 'open', 'high', 'low', 'close', 'volume'].
        Returns a DataFrame indexed by timestamp with derived feature columns.
        """
        df = df_candles.copy()
        if "timestamp" in df.columns:
            df.set_index("timestamp", inplace=True)
        df.sort_index(inplace=True)

        close = df["close"].values
        high = df["high"].values
        low = df["low"].values
        volume = df["volume"].values

        features = pd.DataFrame(index=df.index)

        # 1. Price Returns
        features["returns_1"] = df["close"].pct_change(1)
        features["returns_5"] = df["close"].pct_change(5)
        features["returns_20"] = df["close"].pct_change(20)
        features["log_returns"] = np.log(df["close"] / df["close"].shift(1))

        # 2. Volatility Features
        features["volatility_20"] = features["returns_1"].rolling(window=20).std() * np.sqrt(252)
        features["atr_14"] = TechnicalIndicators.atr(high, low, close, 14)
        features["atr_pct"] = features["atr_14"] / close

        # 3. Technical Oscillators & Trends
        features["rsi_14"] = TechnicalIndicators.rsi(close, 14)
        macd, sig, hist = TechnicalIndicators.macd(close)
        features["macd_hist"] = hist
        
        _, _, _, pct_b = TechnicalIndicators.bollinger_bands(close, 20, 2.0)
        features["bb_pct_b"] = pct_b
        
        adx, p_di, m_di = TechnicalIndicators.adx(high, low, close, 14)
        features["adx"] = adx
        features["di_spread"] = p_di - m_di

        # 4. Moving Average Ratios (Stationary relative to price)
        sma_20 = TechnicalIndicators.sma(close, 20)
        sma_50 = TechnicalIndicators.sma(close, 50)
        sma_200 = TechnicalIndicators.sma(close, 200)
        
        features["dist_sma_20"] = (close - sma_20) / sma_20
        features["dist_sma_50"] = (close - sma_50) / sma_50
        features["dist_sma_200"] = (close - sma_200) / sma_200
        features["sma_20_50_ratio"] = sma_20 / sma_50

        # 5. Volume Features
        vol_mean_20 = df["volume"].rolling(window=20).mean()
        vol_std_20 = df["volume"].rolling(window=20).std().replace(0, 1e-6)
        features["rvol_20"] = df["volume"] / vol_mean_20
        features["volume_zscore"] = (df["volume"] - vol_mean_20) / vol_std_20

        # 6. Price Range / Structure Features
        features["hl_range_pct"] = (df["high"] - df["low"]) / df["close"]
        features["gap_pct"] = (df["open"] - df["close"].shift(1)) / df["close"].shift(1)

        # 7. Benchmark Beta (if available)
        if benchmark_returns is not None:
            aligned_bench = benchmark_returns.reindex(features.index).fillna(0)
            cov = features["returns_1"].rolling(60).cov(aligned_bench)
            var = aligned_bench.rolling(60).var().replace(0, 1e-6)
            features["rolling_beta"] = cov / var
        else:
            features["rolling_beta"] = 1.0

        return features
