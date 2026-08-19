"""
QUANTARA System Observability, Health Checks, Alerts, & Audit Logs API Router
"""

from __future__ import annotations
import os
import platform
import time
from datetime import datetime, timezone
from typing import Any, Dict, List
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from packages.events.bus import default_event_bus
from services.execution_engine.lifecycle import default_execution_engine
from services.news_engine.service import NewsEngine
from services.notification_engine.dispatcher import AlertNotification, NotificationDispatcher

router = APIRouter(prefix="/system", tags=["System"])

START_TIME = time.time()


@router.get("/health")
async def health_check():
    uptime = time.time() - START_TIME
    broker_conn = await default_execution_engine.broker.is_connected()
    return {
        "status": "HEALTHY",
        "service": "Quantara API Gateway",
        "uptime_seconds": round(uptime, 2),
        "broker_connected": broker_conn,
        "live_trading_enabled": default_execution_engine.live_trading_enabled,
        "system_time": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
    }


@router.get("/alerts", response_model=List[AlertNotification])
async def list_alerts():
    return NotificationDispatcher.list_alerts()


@router.post("/alerts/read-all")
async def mark_alerts_read():
    NotificationDispatcher.mark_all_read()
    return {"status": "SUCCESS"}


@router.get("/news")
async def get_system_news():
    return NewsEngine.get_latest_news(limit=10)


@router.get("/events")
async def list_domain_events():
    return [e.to_dict() for e in default_event_bus.get_history(limit=50)]


@router.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics():
    """Prometheus Scraper metrics endpoint."""
    uptime = time.time() - START_TIME
    orders_count = len(default_execution_engine.orders)
    events_count = len(default_event_bus._history)

    metrics_text = f"""# HELP quantara_uptime_seconds Total uptime in seconds
# TYPE quantara_uptime_seconds gauge
quantara_uptime_seconds {uptime:.2f}

# HELP quantara_orders_total Total processed orders
# TYPE quantara_orders_total counter
quantara_orders_total {orders_count}

# HELP quantara_domain_events_total Total published domain events
# TYPE quantara_domain_events_total counter
quantara_domain_events_total {events_count}

# HELP quantara_circuit_breaker_active Circuit breaker status (1=Tripped, 0=Normal)
# TYPE quantara_circuit_breaker_active gauge
quantara_circuit_breaker_active {1 if default_execution_engine.risk_engine.circuit_breaker_tripped else 0}
"""
    return metrics_text
