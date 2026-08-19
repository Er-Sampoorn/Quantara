"""
QUANTARA Technical Indicator Library
High-performance, pure-Python & numpy mathematical implementations with strict zero look-ahead bias.
"""

from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple, Union
import numpy as np


class TechnicalIndicators:
    """Vectorized and streaming technical analysis indicators."""

    @staticmethod
    def sma(values: Union[List[float], np.ndarray], period: int = 14) -> np.ndarray:
        """Simple Moving Average."""
        arr = np.asarray(values, dtype=float)
        if len(arr) < period:
            return np.full_like(arr, np.nan)
        weights = np.ones(period) / period
        res = np.convolve(arr, weights, mode='valid')
        padding = np.full(period - 1, np.nan)
        return np.concatenate((padding, res))

    @staticmethod
    def ema(values: Union[List[float], np.ndarray], period: int = 14) -> np.ndarray:
        """Exponential Moving Average."""
        arr = np.asarray(values, dtype=float)
        if len(arr) == 0:
            return np.array([])
        if len(arr) < period:
            return np.full_like(arr, np.nan)
        
        alpha = 2.0 / (period + 1.0)
        ema_arr = np.full_like(arr, np.nan)
        
        # Initialize first valid EMA with SMA of first period elements
        first_valid_idx = period - 1
        ema_arr[first_valid_idx] = np.mean(arr[:period])
        
        for i in range(period, len(arr)):
            ema_arr[i] = alpha * arr[i] + (1.0 - alpha) * ema_arr[i - 1]
            
        return ema_arr

    @staticmethod
    def rsi(closes: Union[List[float], np.ndarray], period: int = 14) -> np.ndarray:
        """Relative Strength Index (Wilder's Smoothing)."""
        arr = np.asarray(closes, dtype=float)
        if len(arr) <= period:
            return np.full_like(arr, np.nan)
            
        deltas = np.diff(arr)
        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)
        
        rsi_arr = np.full_like(arr, np.nan)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            rsi_arr[period] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi_arr[period] = 100.0 - (100.0 / (1.0 + rs))
            
        for i in range(period + 1, len(arr)):
            gain = gains[i - 1]
            loss = losses[i - 1]
            
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period
            
            if avg_loss == 0:
                rsi_arr[i] = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi_arr[i] = 100.0 - (100.0 / (1.0 + rs))
                
        return rsi_arr

    @staticmethod
    def macd(
        closes: Union[List[float], np.ndarray],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Moving Average Convergence Divergence (MACD, Signal Line, Histogram)."""
        arr = np.asarray(closes, dtype=float)
        fast_ema = TechnicalIndicators.ema(arr, fast_period)
        slow_ema = TechnicalIndicators.ema(arr, slow_period)
        
        macd_line = fast_ema - slow_ema
        
        # Calculate signal line over valid MACD points
        valid_mask = ~np.isnan(macd_line)
        signal_line = np.full_like(macd_line, np.nan)
        
        if np.sum(valid_mask) >= signal_period:
            valid_macd = macd_line[valid_mask]
            sig = TechnicalIndicators.ema(valid_macd, signal_period)
            signal_line[valid_mask] = sig
            
        hist = macd_line - signal_line
        return macd_line, signal_line, hist

    @staticmethod
    def bollinger_bands(
        closes: Union[List[float], np.ndarray],
        period: int = 20,
        num_std: float = 2.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Bollinger Bands (Upper, Middle, Lower, %B)."""
        arr = np.asarray(closes, dtype=float)
        middle = TechnicalIndicators.sma(arr, period)
        
        upper = np.full_like(arr, np.nan)
        lower = np.full_like(arr, np.nan)
        pct_b = np.full_like(arr, np.nan)
        
        for i in range(period - 1, len(arr)):
            window = arr[i - period + 1 : i + 1]
            std = np.std(window, ddof=0)
            mid = middle[i]
            upper[i] = mid + num_std * std
            lower[i] = mid - num_std * std
            
            band_width = upper[i] - lower[i]
            if band_width > 0:
                pct_b[i] = (arr[i] - lower[i]) / band_width
            else:
                pct_b[i] = 0.5
                
        return upper, middle, lower, pct_b

    @staticmethod
    def atr(
        highs: Union[List[float], np.ndarray],
        lows: Union[List[float], np.ndarray],
        closes: Union[List[float], np.ndarray],
        period: int = 14
    ) -> np.ndarray:
        """Average True Range."""
        h = np.asarray(highs, dtype=float)
        l = np.asarray(lows, dtype=float)
        c = np.asarray(closes, dtype=float)
        
        n = len(c)
        if n < 2:
            return np.full(n, np.nan)
            
        tr = np.zeros(n)
        tr[0] = h[0] - l[0]
        
        for i in range(1, n):
            tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
            
        atr_arr = np.full(n, np.nan)
        if n >= period:
            atr_arr[period - 1] = np.mean(tr[:period])
            for i in range(period, n):
                atr_arr[i] = (atr_arr[i - 1] * (period - 1) + tr[i]) / period
                
        return atr_arr

    @staticmethod
    def vwap(
        highs: Union[List[float], np.ndarray],
        lows: Union[List[float], np.ndarray],
        closes: Union[List[float], np.ndarray],
        volumes: Union[List[float], np.ndarray]
    ) -> np.ndarray:
        """Volume Weighted Average Price (Cumulative)."""
        h = np.asarray(highs, dtype=float)
        l = np.asarray(lows, dtype=float)
        c = np.asarray(closes, dtype=float)
        v = np.asarray(volumes, dtype=float)
        
        typical_price = (h + l + c) / 3.0
        cum_tp_v = np.cumsum(typical_price * v)
        cum_v = np.cumsum(v)
        
        with np.errstate(divide='ignore', invalid='ignore'):
            res = np.where(cum_v > 0, cum_tp_v / cum_v, typical_price)
        return res

    @staticmethod
    def obv(closes: Union[List[float], np.ndarray], volumes: Union[List[float], np.ndarray]) -> np.ndarray:
        """On-Balance Volume."""
        c = np.asarray(closes, dtype=float)
        v = np.asarray(volumes, dtype=float)
        
        n = len(c)
        if n == 0:
            return np.array([])
            
        obv_arr = np.zeros(n)
        obv_arr[0] = v[0]
        
        for i in range(1, n):
            if c[i] > c[i - 1]:
                obv_arr[i] = obv_arr[i - 1] + v[i]
            elif c[i] < c[i - 1]:
                obv_arr[i] = obv_arr[i - 1] - v[i]
            else:
                obv_arr[i] = obv_arr[i - 1]
                
        return obv_arr

    @staticmethod
    def adx(
        highs: Union[List[float], np.ndarray],
        lows: Union[List[float], np.ndarray],
        closes: Union[List[float], np.ndarray],
        period: int = 14
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Average Directional Index (ADX, +DI, -DI)."""
        h = np.asarray(highs, dtype=float)
        l = np.asarray(lows, dtype=float)
        c = np.asarray(closes, dtype=float)
        n = len(c)
        
        if n < period * 2:
            nan_arr = np.full(n, np.nan)
            return nan_arr, nan_arr, nan_arr
            
        up_move = np.zeros(n)
        down_move = np.zeros(n)
        plus_dm = np.zeros(n)
        minus_dm = np.zeros(n)
        
        for i in range(1, n):
            up_move[i] = h[i] - h[i - 1]
            down_move[i] = l[i - 1] - l[i]
            
            if up_move[i] > down_move[i] and up_move[i] > 0:
                plus_dm[i] = up_move[i]
            else:
                plus_dm[i] = 0
                
            if down_move[i] > up_move[i] and down_move[i] > 0:
                minus_dm[i] = down_move[i]
            else:
                minus_dm[i] = 0
                
        atr_vals = TechnicalIndicators.atr(h, l, c, period)
        
        plus_di = np.full(n, np.nan)
        minus_di = np.full(n, np.nan)
        dx = np.full(n, np.nan)
        adx_arr = np.full(n, np.nan)
        
        # Smoothed DM
        smooth_plus_dm = np.zeros(n)
        smooth_minus_dm = np.zeros(n)
        
        smooth_plus_dm[period] = np.sum(plus_dm[1:period + 1])
        smooth_minus_dm[period] = np.sum(minus_dm[1:period + 1])
        
        for i in range(period, n):
            if i > period:
                smooth_plus_dm[i] = smooth_plus_dm[i - 1] - (smooth_plus_dm[i - 1] / period) + plus_dm[i]
                smooth_minus_dm[i] = smooth_minus_dm[i - 1] - (smooth_minus_dm[i - 1] / period) + minus_dm[i]
                
            if not np.isnan(atr_vals[i]) and atr_vals[i] > 0:
                plus_di[i] = 100.0 * (smooth_plus_dm[i] / (atr_vals[i] * period))
                minus_di[i] = 100.0 * (smooth_minus_dm[i] / (atr_vals[i] * period))
                
                di_sum = plus_di[i] + minus_di[i]
                if di_sum > 0:
                    dx[i] = 100.0 * abs(plus_di[i] - minus_di[i]) / di_sum
                    
        # ADX is smoothed DX
        valid_dx_start = period * 2 - 1
        if n > valid_dx_start:
            valid_dx = dx[period:valid_dx_start + 1]
            adx_arr[valid_dx_start] = np.nanmean(valid_dx)
            for i in range(valid_dx_start + 1, n):
                if not np.isnan(dx[i]):
                    adx_arr[i] = (adx_arr[i - 1] * (period - 1) + dx[i]) / period
                    
        return adx_arr, plus_di, minus_di

    @staticmethod
    def stochastic(
        highs: Union[List[float], np.ndarray],
        lows: Union[List[float], np.ndarray],
        closes: Union[List[float], np.ndarray],
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Stochastic Oscillator (%K, %D)."""
        h = np.asarray(highs, dtype=float)
        l = np.asarray(lows, dtype=float)
        c = np.asarray(closes, dtype=float)
        n = len(c)
        
        pct_k = np.full(n, np.nan)
        for i in range(k_period - 1, n):
            highest_high = np.max(h[i - k_period + 1 : i + 1])
            lowest_low = np.min(l[i - k_period + 1 : i + 1])
            denom = highest_high - lowest_low
            if denom > 0:
                pct_k[i] = 100.0 * (c[i] - lowest_low) / denom
            else:
                pct_k[i] = 50.0
                
        pct_d = TechnicalIndicators.sma(pct_k, d_period)
        return pct_k, pct_d

    @staticmethod
    def compute_all_indicators(
        highs: Union[List[float], np.ndarray],
        lows: Union[List[float], np.ndarray],
        closes: Union[List[float], np.ndarray],
        volumes: Union[List[float], np.ndarray]
    ) -> Dict[str, np.ndarray]:
        """Compute a full dictionary of standard indicators for feature extraction."""
        c = np.asarray(closes, dtype=float)
        h = np.asarray(highs, dtype=float)
        l = np.asarray(lows, dtype=float)
        v = np.asarray(volumes, dtype=float)
        
        macd_line, macd_sig, macd_hist = TechnicalIndicators.macd(c)
        bb_upper, bb_mid, bb_lower, bb_pct_b = TechnicalIndicators.bollinger_bands(c)
        adx_val, p_di, m_di = TechnicalIndicators.adx(h, l, c)
        stoch_k, stoch_d = TechnicalIndicators.stochastic(h, l, c)
        
        return {
            "sma_20": TechnicalIndicators.sma(c, 20),
            "sma_50": TechnicalIndicators.sma(c, 50),
            "sma_200": TechnicalIndicators.sma(c, 200),
            "ema_9": TechnicalIndicators.ema(c, 9),
            "ema_21": TechnicalIndicators.ema(c, 21),
            "ema_50": TechnicalIndicators.ema(c, 50),
            "rsi_14": TechnicalIndicators.rsi(c, 14),
            "macd": macd_line,
            "macd_signal": macd_sig,
            "macd_hist": macd_hist,
            "bb_upper": bb_upper,
            "bb_middle": bb_mid,
            "bb_lower": bb_lower,
            "bb_pct_b": bb_pct_b,
            "atr_14": TechnicalIndicators.atr(h, l, c, 14),
            "vwap": TechnicalIndicators.vwap(h, l, c, v),
            "obv": TechnicalIndicators.obv(c, v),
            "adx_14": adx_val,
            "plus_di": p_di,
            "minus_di": m_di,
            "stoch_k": stoch_k,
            "stoch_d": stoch_d,
        }
