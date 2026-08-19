# QUANTARA REST API & WebSocket Reference

Base URL: `http://localhost:8000/api/v1`
WebSocket URL: `ws://localhost:8000/ws`

## Core Endpoints

### 1. Market Data
- `GET /api/v1/markets/instruments`: List supported instruments.
- `GET /api/v1/markets/quotes`: Batch real-time quotes.
- `GET /api/v1/markets/{symbol}/candles`: Historical OHLCV bars.
- `GET /api/v1/markets/{symbol}/analysis`: Technical indicators & detected regime.

### 2. Signal Fusion
- `GET /api/v1/signals`: Active fused signal feed.
- `GET /api/v1/signals/{symbol}`: Deep factor decomposition for asset.

### 3. Strategies & DSL
- `GET /api/v1/strategies`: List registered strategies.
- `POST /api/v1/strategies/compile-nl`: Natural language to strategy compiler.
- `POST /api/v1/strategies/validate`: Validate Strategy DSL AST.

### 4. Backtesting & Optimization
- `POST /api/v1/backtests/run`: Execute event-driven backtest.
- `POST /api/v1/optimization/run`: Bayesian parameter optimization.
- `POST /api/v1/optimization/walk-forward`: Chronological Walk-Forward validation.
- `POST /api/v1/optimization/monte-carlo`: 1,000x - 10,000x trade bootstrapping.

### 5. Multi-Agent AI & Copilot
- `POST /api/v1/ai/analyze/{symbol}`: Run 5 specialist research agents + synthesis thesis.
- `POST /api/v1/ai/copilot/chat`: Grounded quantitative AI copilot chat.

### 6. Portfolio & Risk
- `GET /api/v1/portfolio`: Current portfolio valuation and open positions.
- `POST /api/v1/portfolio/optimize`: Markowitz / Risk Parity allocation optimizer.
- `GET /api/v1/risk/status`: Risk hard-gate status and circuit breaker state.
- `POST /api/v1/risk/circuit-breaker/reset`: Manual circuit breaker reset.

### 7. Execution & Orders
- `GET /api/v1/orders`: Historical and active orders.
- `POST /api/v1/orders`: Submit idempotent order through pre-trade risk gate.
- `DELETE /api/v1/orders/{id}`: Cancel open order.
