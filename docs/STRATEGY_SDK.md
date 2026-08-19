# QUANTARA Strategy SDK & Natural Language DSL Guide

## BaseStrategy Lifecycle Contract

All strategies inherit from `BaseStrategy` and implement the following lifecycle hooks:

```python
from packages.strategies.base import BaseStrategy
from packages.domain.models import Candle, Signal, SignalDirection

class CustomMomentumStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.fast_period = int(self.get_parameter("fast_period", 10))
        self.slow_period = int(self.get_parameter("slow_period", 30))
        self.is_initialized = True

    def on_bar(self, candle: Candle) -> Optional[Signal]:
        self._append_bar(candle)
        df = self.get_dataframe()
        if len(df) < self.slow_period:
            return None
            
        # Strategy logic here...
        return Signal(
            symbol=candle.symbol,
            direction=SignalDirection.BUY,
            confidence=0.85,
            signal_score=0.80,
            strategy_id=self.strategy_id,
            reason_codes=["CUSTOM_MOMENTUM_ENTRY"]
        )
```

## Built-in Production Strategies
1. `SMACrossoverStrategy`
2. `EMACrossoverStrategy`
3. `RSIMeanReversionStrategy`
4. `MACDMomentumStrategy`
5. `BollingerMeanReversionStrategy`
6. `VWAPIntradayStrategy`
7. `DonchianBreakoutStrategy`
8. `TrendFollowingADXStrategy`
9. `DualMomentumStrategy`
10. `VolatilityBreakoutStrategy`
11. `StatisticalArbitragePairsStrategy`
12. `MultiFactorFusionStrategy`

## Natural Language Strategy DSL
Quantara translates natural language queries into validated Strategy DSL AST:

```json
{
  "name": "RSI Reversal with Trend Filter",
  "symbol": "AAPL",
  "entry_rules": [
    { "indicator": "RSI", "operator": "crosses_above", "value": 30, "period": 14 },
    { "indicator": "EMA", "operator": "price_above", "period": 200 }
  ],
  "exit_rules": [
    { "indicator": "RSI", "operator": "greater_than", "value": 70, "period": 14 }
  ],
  "risk_config": {
    "risk_per_trade": 0.01,
    "stop_loss_pct": 0.02,
    "take_profit_pct": 0.05
  }
}
```
