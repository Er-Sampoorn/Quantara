"""
QUANTARA SQLAlchemy Database Models
Relational schema definitions for Users, Market Data, Strategies, Backtests, Portfolios, Orders, and Audits.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from database.connection import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False, default="Trader")
    role = Column(String(32), default="USER", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class InstrumentModel(Base):
    __tablename__ = "instruments"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    asset_class = Column(String(32), nullable=False)
    exchange = Column(String(64), default="NASDAQ")
    currency = Column(String(16), default="USD")
    sector = Column(String(64), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CandleModel(Base):
    __tablename__ = "candles"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(32), nullable=False, index=True)
    timeframe = Column(String(16), default="1D", nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    vwap = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)


class StrategyModel(Base):
    __tablename__ = "strategies"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    symbol = Column(String(32), nullable=False)
    timeframe = Column(String(16), default="1D")
    strategy_type = Column(String(64), nullable=False)
    parameters = Column(JSON, default=dict)
    risk_config = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    author_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class BacktestRunModel(Base):
    __tablename__ = "backtest_runs"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_id = Column(String(64), nullable=False, index=True)
    strategy_name = Column(String(255), nullable=False)
    symbol = Column(String(32), nullable=False)
    timeframe = Column(String(16), default="1D")
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_equity = Column(Float, nullable=False)
    metrics = Column(JSON, nullable=False)
    equity_curve = Column(JSON, nullable=False)
    parameters = Column(JSON, default=dict)
    reproducibility_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_order_id = Column(String(64), unique=True, nullable=False)
    symbol = Column(String(32), nullable=False, index=True)
    side = Column(String(16), nullable=False)
    order_type = Column(String(32), nullable=False)
    quantity = Column(Float, nullable=False)
    limit_price = Column(Float, nullable=True)
    stop_price = Column(Float, nullable=True)
    status = Column(String(32), nullable=False, index=True)
    filled_quantity = Column(Float, default=0.0)
    average_fill_price = Column(Float, default=0.0)
    fees = Column(Float, default=0.0)
    strategy_id = Column(String(64), nullable=True)
    execution_mode = Column(String(16), default="PAPER")
    idempotency_key = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    action = Column(String(64), nullable=False, index=True)
    actor_id = Column(String(64), nullable=True)
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(64), nullable=True)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
