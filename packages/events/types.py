"""
QUANTARA Strongly Typed Domain Events
CloudEvent compatible schema with correlation and causation tracking.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class EventType(str, Enum):
    # Market Data Events
    MARKET_DATA_RECEIVED = "market.data.received"
    CANDLE_CLOSED = "market.candle.closed"
    ORDER_BOOK_UPDATED = "market.orderbook.updated"
    
    # Intelligence & Signal Events
    FEATURE_COMPUTED = "intelligence.feature.computed"
    REGIME_CHANGED = "intelligence.regime.changed"
    ANOMALY_DETECTED = "intelligence.anomaly.detected"
    NEWS_RECEIVED = "intelligence.news.received"
    SIGNAL_GENERATED = "intelligence.signal.generated"
    
    # Risk Events
    RISK_CHECK_PASSED = "risk.check.passed"
    RISK_CHECK_FAILED = "risk.check.failed"
    CIRCUIT_BREAKER_TRIGGERED = "risk.circuit_breaker.triggered"
    
    # Order & Execution Events
    ORDER_CREATED = "execution.order.created"
    ORDER_SUBMITTED = "execution.order.submitted"
    ORDER_ACCEPTED = "execution.order.accepted"
    ORDER_REJECTED = "execution.order.rejected"
    ORDER_PARTIALLY_FILLED = "execution.order.partially_filled"
    ORDER_FILLED = "execution.order.filled"
    ORDER_CANCELLED = "execution.order.cancelled"
    
    # Position & Portfolio Events
    POSITION_OPENED = "portfolio.position.opened"
    POSITION_UPDATED = "portfolio.position.updated"
    POSITION_CLOSED = "portfolio.position.closed"
    PORTFOLIO_REBALANCED = "portfolio.rebalanced"
    
    # Strategy & Research Events
    STRATEGY_DEPLOYED = "strategy.deployed"
    STRATEGY_STOPPED = "strategy.stopped"
    BACKTEST_STARTED = "research.backtest.started"
    BACKTEST_COMPLETED = "research.backtest.completed"
    OPTIMIZATION_STARTED = "research.optimization.started"
    OPTIMIZATION_COMPLETED = "research.optimization.completed"
    
    # Broker & System Events
    BROKER_CONNECTED = "broker.connected"
    BROKER_DISCONNECTED = "broker.disconnected"
    RECONCILIATION_COMPLETED = "system.reconciliation.completed"
    RECONCILIATION_ISSUE_DETECTED = "system.reconciliation.issue"
    SYSTEM_ALERT = "system.alert"


class DomainEvent(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "quantara.core"
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    causation_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    schema_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value if isinstance(self.event_type, Enum) else self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "payload": self.payload,
            "schema_version": self.schema_version,
        }
