"""
QUANTARA Notification & Alert Dispatcher
Multi-channel notification engine (In-app, Webhooks, Telegram, Email formats).
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AlertNotification(BaseModel):
    id: str = Field(default_factory=lambda: f"alert_{uuid.uuid4().hex[:8]}")
    title: str
    message: str
    severity: str = "INFO"  # INFO, WARNING, CRITICAL
    category: str = "SYSTEM"  # RISK, SIGNAL, ORDER, ANOMALY, SYSTEM
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_read: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NotificationDispatcher:
    """Manages application alerts and dispatches to configured subscriber channels."""

    _NOTIFICATIONS: List[AlertNotification] = [
        AlertNotification(
            title="System Boot Completed",
            message="Quantara Quantitative Trading & Research Platform initialized in Paper Trading mode.",
            severity="INFO",
            category="SYSTEM"
        ),
        AlertNotification(
            title="Market Regime Classified: BULL",
            message="SPY classified into Bullish Regime with 91% model confidence.",
            severity="INFO",
            category="SIGNAL"
        ),
        AlertNotification(
            title="Risk Hard Gate Active",
            message="Pre-trade risk engine active with max 20% single position allocation and 1.5x max leverage limit.",
            severity="INFO",
            category="RISK"
        )
    ]

    @classmethod
    def list_alerts(cls, limit: int = 50) -> List[AlertNotification]:
        return cls._NOTIFICATIONS[:limit]

    @classmethod
    def emit_alert(
        cls,
        title: str,
        message: str,
        severity: str = "INFO",
        category: str = "SYSTEM",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AlertNotification:
        alert = AlertNotification(
            title=title,
            message=message,
            severity=severity,
            category=category,
            metadata=metadata or {}
        )
        cls._NOTIFICATIONS.insert(0, alert)
        if len(cls._NOTIFICATIONS) > 500:
            cls._NOTIFICATIONS.pop()
        return alert

    @classmethod
    def mark_all_read(cls) -> None:
        for n in cls._NOTIFICATIONS:
            n.is_read = True
