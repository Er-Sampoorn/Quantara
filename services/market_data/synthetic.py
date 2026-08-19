"""
QUANTARA Synthetic Deterministic Market Data Provider
Generates realistic financial OHLCV candlestick time series using Geometric Brownian Motion with stochastic volatility.
"""

from __future__ import annotations
import math
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import numpy as np
from packages.domain.models import AssetClass, Candle, Instrument, OrderSide, Quote, Tick
from services.market_data.provider import MarketDataProvider


class SyntheticDataProvider(MarketDataProvider):
    """
    Deterministic market data provider.
    Enables full local platform functionality, backtesting, and paper trading without external API keys.
    """

    DEMO_INSTRUMENTS: List[Instrument] = [
        Instrument(symbol="AAPL", name="Apple Inc.", asset_class=AssetClass.EQUITY, exchange="NASDAQ", sector="Technology"),
        Instrument(symbol="MSFT", name="Microsoft Corp.", asset_class=AssetClass.EQUITY, exchange="NASDAQ", sector="Technology"),
        Instrument(symbol="NVDA", name="NVIDIA Corporation", asset_class=AssetClass.EQUITY, exchange="NASDAQ", sector="Semiconductors"),
        Instrument(symbol="SPY", name="SPDR S&P 500 ETF Trust", asset_class=AssetClass.ETF, exchange="NYSE", sector="Broad Market"),
        Instrument(symbol="QQQ", name="Invesco QQQ Trust", asset_class=AssetClass.ETF, exchange="NASDAQ", sector="Technology ETF"),
        Instrument(symbol="TSLA", name="Tesla Inc.", asset_class=AssetClass.EQUITY, exchange="NASDAQ", sector="Consumer Cyclical"),
        Instrument(symbol="BTC/USD", name="Bitcoin / USD", asset_class=AssetClass.CRYPTO, exchange="CRYPTO", sector="Cryptocurrency"),
        Instrument(symbol="ETH/USD", name="Ethereum / USD", asset_class=AssetClass.CRYPTO, exchange="CRYPTO", sector="Cryptocurrency"),
    ]

    BASE_PRICES: Dict[str, float] = {
        "AAPL": 220.0,
        "MSFT": 440.0,
        "NVDA": 125.0,
        "SPY": 550.0,
        "QQQ": 480.0,
        "TSLA": 215.0,
        "BTC/USD": 65000.0,
        "ETH/USD": 3400.0,
    }

    VOLATILITIES: Dict[str, float] = {
        "AAPL": 0.22,
        "MSFT": 0.20,
        "NVDA": 0.45,
        "SPY": 0.14,
        "QQQ": 0.18,
        "TSLA": 0.50,
        "BTC/USD": 0.60,
        "ETH/USD": 0.65,
    }

    def __init__(self, seed: int = 42):
        self.seed = seed
        self._cache: Dict[str, List[Candle]] = {}
        self._generate_initial_history()

    def _generate_initial_history(self) -> None:
        """Pre-generate 365 days of realistic daily OHLCV candles for all demo symbols."""
        np.random.seed(self.seed)
        end_date = datetime.now(timezone.utc).replace(hour=16, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=365)

        for sym, base_price in self.BASE_PRICES.items():
            annual_vol = self.VOLATILITIES.get(sym, 0.25)
            daily_vol = annual_vol / math.sqrt(252)
            drift = 0.10 / 252  # 10% annual upward drift

            candles: List[Candle] = []
            curr_price = base_price * 0.85  # start slightly lower a year ago
            curr_date = start_date

            while curr_date <= end_date:
                # Skip weekends for equities and ETFs
                if sym not in ["BTC/USD", "ETH/USD"] and curr_date.weekday() >= 5:
                    curr_date += timedelta(days=1)
                    continue

                # Brownian motion with jump diffusion
                shock = np.random.normal(0, 1)
                jump = np.random.choice([0, 1], p=[0.97, 0.03]) * np.random.normal(0, 0.03)
                ret = drift + daily_vol * shock + jump
                
                open_p = curr_price
                close_p = max(1.0, open_p * (1.0 + ret))
                intra_vol = abs(ret) + (daily_vol * 0.5)
                high_p = max(open_p, close_p) * (1.0 + abs(np.random.normal(0, intra_vol * 0.6)))
                low_p = min(open_p, close_p) * (1.0 - abs(np.random.normal(0, intra_vol * 0.6)))
                volume = float(np.random.lognormal(14.0, 0.5)) if "USD" not in sym else float(np.random.lognormal(11.0, 0.8))

                candles.append(Candle(
                    symbol=sym,
                    timeframe="1D",
                    open=round(float(open_p), 2),
                    high=round(float(high_p), 2),
                    low=round(float(low_p), 2),
                    close=round(float(close_p), 2),
                    volume=round(float(volume), 0),
                    vwap=round(float((open_p + high_p + low_p + close_p) / 4.0), 2),
                    timestamp=curr_date
                ))
                curr_price = close_p
                curr_date += timedelta(days=1)

            self._cache[sym] = candles

    async def get_instruments(self) -> List[Instrument]:
        return self.DEMO_INSTRUMENTS

    async def get_quote(self, symbol: str) -> Quote:
        sym = symbol.upper()
        candles = self._cache.get(sym)
        if candles:
            last_candle = candles[-1]
            prev_candle = candles[-2] if len(candles) > 1 else last_candle
            last_p = last_candle.close
            chg = last_p - prev_candle.close
            chg_pct = (chg / prev_candle.close) if prev_candle.close > 0 else 0.0
            
            spread = max(0.01, round(last_p * 0.0004, 2))
            return Quote(
                symbol=sym,
                bid_price=round(last_p - spread / 2.0, 2),
                bid_size=150,
                ask_price=round(last_p + spread / 2.0, 2),
                ask_size=200,
                last_price=round(last_p, 2),
                volume_24h=last_candle.volume,
                change_24h=round(chg, 2),
                change_24h_pct=round(chg_pct, 4),
                high_24h=last_candle.high,
                low_24h=last_candle.low,
                timestamp=datetime.now(timezone.utc)
            )

        base_p = self.BASE_PRICES.get(sym, 100.0)
        return Quote(
            symbol=sym,
            bid_price=round(base_p * 0.9998, 2),
            bid_size=100,
            ask_price=round(base_p * 1.0002, 2),
            ask_size=100,
            last_price=round(base_p, 2),
            timestamp=datetime.now(timezone.utc)
        )

    async def get_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        res = {}
        for s in symbols:
            res[s.upper()] = await self.get_quote(s)
        return res

    async def get_historical_bars(
        self,
        symbol: str,
        timeframe: str = "1D",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 300,
    ) -> List[Candle]:
        sym = symbol.upper()
        if sym not in self._cache:
            # Generate on the fly if unseen symbol
            self._cache[sym] = self._cache["AAPL"]  # fallback clone
        
        all_bars = self._cache[sym]
        filtered = all_bars
        if start:
            filtered = [b for b in filtered if b.timestamp >= start]
        if end:
            filtered = [b for b in filtered if b.timestamp <= end]
            
        return filtered[-limit:]

    async def get_ticks(self, symbol: str, limit: int = 50) -> List[Tick]:
        quote = await self.get_quote(symbol)
        now = datetime.now(timezone.utc)
        ticks: List[Tick] = []
        for i in range(limit):
            t_time = now - timedelta(seconds=i * 2)
            noise = (np.random.random() - 0.5) * (quote.last_price * 0.001)
            p = round(quote.last_price + noise, 2)
            qty = float(np.random.randint(10, 500))
            side = OrderSide.BUY if noise >= 0 else OrderSide.SELL
            ticks.append(Tick(symbol=symbol.upper(), price=p, quantity=qty, side=side, timestamp=t_time))
        ticks.reverse()
        return ticks


# Global default synthetic provider instance
default_market_provider = SyntheticDataProvider()
