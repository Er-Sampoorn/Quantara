# QUANTARA System Architecture

Quantara is an institutional-grade, event-driven quantitative trading, AI research, and execution platform.

## High-Level Architecture Diagram

```mermaid
graph TD
    User([Trader / Quant]) --> Web[Next.js Quantitative Terminal]
    Web -->|REST / WebSocket| Gateway[FastAPI API Gateway]
    
    subgraph Core Engines
        Gateway --> StratEng[Strategy & DSL Engine]
        Gateway --> BacktestEng[Event-Driven Backtester]
        Gateway --> OptEng[Bayesian & Walk-Forward Optimizer]
        Gateway --> SignalEng[Signal Fusion Engine]
        Gateway --> AIEng[Multi-Agent AI Research]
        Gateway --> RiskEng[Pre-Trade Risk Hard Gate]
        Gateway --> ExecEng[Execution & Order Lifecycle]
    end

    subgraph Data & Event Layer
        Bus[(Async Event Bus / Redis Streams)]
        MktData[Market Data Provider / Synthetic Generator]
        DB[(TimescaleDB / PostgreSQL)]
    end

    subgraph Execution Adapters
        RiskEng -->|Approved Orders Only| BrokerRouter[Broker Router]
        BrokerRouter --> Paper[PaperBroker Matching Engine]
        BrokerRouter --> Alpaca[Alpaca Broker Adapter]
    end

    MktData --> Bus
    Bus --> StratEng
    StratEng --> SignalEng
    SignalEng --> RiskEng
    ExecEng --> DB
```

## Architectural Principles

1. **Deterministic Computation**: Given historical data and parameters, strategies and backtests always produce identical, reproducible results.
2. **Zero Look-Ahead Bias**: Event-driven backtester feeds bars chronologically one by one.
3. **Pre-Trade Risk Hard Gate**: AI agents cannot place orders directly. All orders must pass deterministic risk checks.
4. **Broker Abstraction**: Strategies execute identical logic across Backtest, Paper, and Live modes.
5. **Zero External Dependency Mode**: Fully functional with deterministic synthetic market data generator without requiring paid API keys.
