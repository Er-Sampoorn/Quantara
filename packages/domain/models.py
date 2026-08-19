"""
QUANTARA Domain Models & Schemas
Core typed domain entities and enumerations for the entire platform.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# Enumerations
# ==========================================

class AssetClass(str, Enum):
    EQUITY = "EQUITY"
    ETF = "ETF"
    CRYPTO = "CRYPTO"
    FOREX = "FOREX"
    FUTURES = "FUTURES"
    INDEX = "INDEX"


class MarketSession(str, Enum):
    PRE_MARKET = "PRE_MARKET"
    REGULAR = "REGULAR"
    AFTER_HOURS = "AFTER_HOURS"
    CLOSED = "CLOSED"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"


class TimeInForce(str, Enum):
    GTC = "GTC"  # Good Till Cancelled
    DAY = "DAY"  # Day order
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    RISK_CHECK = "RISK_CHECK"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class SignalDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    SHORT = "SHORT"
    COVER = "COVER"
    HOLD = "HOLD"


class RegimeType(str, Enum):
    BULL = "BULL"
    BEAR = "BEAR"
    SIDEWAYS = "SIDEWAYS"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    BREAKOUT = "BREAKOUT"
    PANIC = "PANIC"
    RECOVERY = "RECOVERY"


class NewsImpact(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SentimentLabel(str, Enum):
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"


class PositionSizingType(str, Enum):
    FIXED_QUANTITY = "FIXED_QUANTITY"
    FIXED_CAPITAL = "FIXED_CAPITAL"
    RISK_PERCENTAGE = "RISK_PERCENTAGE"
    VOLATILITY_ATR = "VOLATILITY_ATR"
    KELLY_CRITERION = "KELLY_CRITERION"


class OptimizationMetric(str, Enum):
    SHARPE = "SHARPE"
    SORTINO = "SORTINO"
    CALMAR = "CALMAR"
    TOTAL_RETURN = "TOTAL_RETURN"
    PROFIT_FACTOR = "PROFIT_FACTOR"
    MIN_DRAWDOWN = "MIN_DRAWDOWN"


class ExecutionMode(str, Enum):
    BACKTEST = "BACKTEST"
    PAPER = "PAPER"
    LIVE = "LIVE"


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


# ==========================================
# Market Data Models
# ==========================================

class Instrument(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    name: str
    asset_class: AssetClass
    exchange: str = "NASDAQ"
    currency: str = "USD"
    price_precision: int = 2
    quantity_precision: int = 4
    min_quantity: float = 1.0
    tick_size: float = 0.01
    sector: Optional[str] = None
    industry: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Quote(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    symbol: str
    bid_price: float
    bid_size: float
    ask_price: float
    ask_size: float
    last_price: float
    volume_24h: float = 0.0
    change_24h: float = 0.0
    change_24h_pct: float = 0.0
    high_24h: float = 0.0
    low_24h: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Tick(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    symbol: str
    price: float
    quantity: float
    side: Optional[OrderSide] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Candle(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    symbol: str
    timeframe: str  # 1m, 5m, 15m, 1h, 1D
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: Optional[float] = None
    timestamp: datetime


# ==========================================
# Technical & Regime Models
# ==========================================

class MarketRegimeState(BaseModel):
    symbol: str
    regime: RegimeType
    confidence: float = Field(ge=0.0, le=1.0)
    volatility: float
    trend_strength: float
    supporting_features: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AnomalyEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    anomaly_type: str  # VOLUME_SPIKE, PRICE_SHOCK, VOLATILITY_BURST, SPREAD_WIDENING
    severity: NewsImpact
    z_score: float
    current_value: float
    baseline_value: float
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NewsItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    headline: str
    summary: str
    source: str
    symbols: List[str] = Field(default_factory=list)
    sectors: List[str] = Field(default_factory=list)
    sentiment: SentimentLabel
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    impact: NewsImpact
    confidence: float = Field(ge=0.0, le=1.0)
    url: Optional[str] = None
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==========================================
# Signal Models & Explainability
# ==========================================

class SignalComponent(BaseModel):
    name: str  # technical, fundamental, sentiment, quant, ml, regime, risk
    score: float = Field(ge=-1.0, le=1.0)
    weight: float = Field(ge=0.0, le=1.0)
    contribution: float
    reason: str


class Signal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    direction: SignalDirection
    confidence: float = Field(ge=0.0, le=1.0)
    signal_score: float = Field(ge=-1.0, le=1.0)
    target_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    timeframe: str = "1D"
    components: List[SignalComponent] = Field(default_factory=list)
    reason_codes: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    strategy_id: Optional[str] = None
    source: str = "SIGNAL_FUSION_ENGINE"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==========================================
# Strategy & DSL Models
# ==========================================

class StrategyRule(BaseModel):
    indicator: str
    operator: str  # crosses_above, crosses_below, greater_than, less_than, price_above, price_below
    value: Optional[Union[float, str]] = None
    period: Optional[int] = None
    params: Dict[str, Any] = Field(default_factory=dict)


class StrategyRiskConfig(BaseModel):
    risk_per_trade: float = 0.01
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    max_drawdown_limit: float = 0.15
    sizing_type: PositionSizingType = PositionSizingType.RISK_PERCENTAGE


class StrategySpec(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    symbol: str
    symbols: List[str] = Field(default_factory=list)
    timeframe: str = "1h"
    entry_rules: List[StrategyRule] = Field(default_factory=list)
    exit_rules: List[StrategyRule] = Field(default_factory=list)
    risk_config: StrategyRiskConfig = Field(default_factory=StrategyRiskConfig)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    author_id: Optional[str] = None
    version: int = 1
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==========================================
# Risk Management Models
# ==========================================

class RiskRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    rule_type: str  # MAX_POSITION_SIZE, MAX_LEVERAGE, DAILY_LOSS_LIMIT, MAX_DRAWDOWN, CIRCUIT_BREAKER
    threshold_value: float
    is_hard_gate: bool = True
    is_enabled: bool = True


class RiskCheckResult(BaseModel):
    passed: bool
    rule_name: str
    requested_value: float
    threshold_value: float
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RiskEvaluation(BaseModel):
    approved: bool
    evaluations: List[RiskCheckResult] = Field(default_factory=list)
    rejected_reasons: List[str] = Field(default_factory=list)
    recommended_quantity: Optional[float] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==========================================
# Order & Execution Models
# ==========================================

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_order_id: str = Field(default_factory=lambda: f"ord_{uuid.uuid4().hex[:12]}")
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    status: OrderStatus = OrderStatus.CREATED
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    fees: float = 0.0
    strategy_id: Optional[str] = None
    execution_mode: ExecutionMode = ExecutionMode.PAPER
    rejection_reason: Optional[str] = None
    idempotency_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Fill(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    fee: float = 0.0
    slippage: float = 0.0
    broker_fill_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Position(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    realized_pnl: float = 0.0
    side: OrderSide = OrderSide.BUY
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    opened_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Portfolio(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str = "Primary Quantitative Portfolio"
    cash: float = 100_000.0
    initial_balance: float = 100_000.0
    equity: float = 100_000.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    drawdown_pct: float = 0.0
    positions: Dict[str, Position] = Field(default_factory=dict)
    leverage: float = 1.0
    execution_mode: ExecutionMode = ExecutionMode.PAPER
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Trade(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    strategy_id: Optional[str] = None
    side: OrderSide
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_pct: float
    entry_time: datetime
    exit_time: datetime
    fees: float = 0.0
    slippage: float = 0.0
    holding_period_seconds: float = 0.0
    entry_reason: Optional[str] = None
    exit_reason: Optional[str] = None
    regime_at_entry: Optional[RegimeType] = None


class JournalEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trade_id: str
    symbol: str
    strategy_name: str
    pnl: float
    pnl_pct: float
    regime: RegimeType
    execution_quality_score: float = 1.0  # 0 to 1
    slippage_cost: float = 0.0
    rule_compliance: bool = True
    ai_post_mortem: str
    lessons_learned: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==========================================
# Backtest & Optimization Results
# ==========================================

class BacktestMetrics(BaseModel):
    total_return: float
    total_return_pct: float
    cagr: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    win_rate: float
    loss_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    average_win: float
    average_loss: float
    expectancy: float
    recovery_factor: float
    annualized_volatility: float
    var_95: float
    cvar_95: float
    beta: float = 1.0
    alpha: float = 0.0
    max_consecutive_losses: int = 0


class EquityPoint(BaseModel):
    timestamp: datetime
    equity: float
    cash: float
    drawdown_pct: float
    benchmark_equity: Optional[float] = None


class BacktestResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    strategy_id: str
    strategy_name: str
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_equity: float
    metrics: BacktestMetrics
    equity_curve: List[EquityPoint] = Field(default_factory=list)
    trades: List[Trade] = Field(default_factory=list)
    monthly_returns: Dict[str, float] = Field(default_factory=dict)
    regime_breakdown: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    reproducibility_hash: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OptimizationTrial(BaseModel):
    trial_id: int
    parameters: Dict[str, Any]
    metrics: Dict[str, float]
    score: float
    is_best: bool = False


class OptimizationResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    strategy_id: str
    objective_metric: OptimizationMetric
    trials_count: int
    best_parameters: Dict[str, Any]
    best_metrics: Dict[str, float]
    trials: List[OptimizationTrial] = Field(default_factory=list)
    parameter_stability_score: float = 0.0
    overfitting_risk_score: float = 0.0
    walk_forward_efficiency: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MonteCarloSimulationResult(BaseModel):
    simulations_count: int
    confidence_intervals: Dict[str, Dict[str, float]]  # e.g., "drawdown": {"5%": -0.05, "50%": -0.12, "95%": -0.22}
    probability_of_profit: float
    probability_of_ruin: float
    median_ending_equity: float
    worst_case_drawdown: float
    sample_equity_curves: List[List[float]] = Field(default_factory=list)


# ==========================================
# AI Multi-Agent & Research Models
# ==========================================

class AgentInsight(BaseModel):
    agent_name: str  # Market, Fundamental, Sentiment, Quant, Risk
    headline: str
    stance: SignalDirection  # BUY, SELL, HOLD
    confidence: float
    key_findings: List[str]
    supporting_metrics: Dict[str, Any] = Field(default_factory=dict)


class MultiAgentResearchReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    executive_summary: str
    overall_direction: SignalDirection
    overall_confidence: float
    market_analyst: AgentInsight
    fundamental_analyst: AgentInsight
    sentiment_analyst: AgentInsight
    quant_analyst: AgentInsight
    risk_analyst: AgentInsight
    synthesis_thesis: str
    actionable_levels: Dict[str, float] = Field(default_factory=dict)  # entry, stop_loss, target
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResearchWorkspace(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    symbols: List[str] = Field(default_factory=list)
    notes: str = ""
    saved_queries: List[Dict[str, Any]] = Field(default_factory=list)
    linked_backtests: List[str] = Field(default_factory=list)
    linked_strategies: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
