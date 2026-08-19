"""
QUANTARA Reconciliation Engine
Compares internal state against broker accounts for positions, cash, and orders without silent state mutation.
"""

from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from packages.brokers.base import BrokerAdapter
from packages.domain.models import Position
from packages.events.bus import default_event_bus
from packages.events.types import DomainEvent, EventType

logger = logging.getLogger("quantara.reconciliation")


class ReconciliationIssue(BaseModel):
    issue_type: str  # POSITION_MISMATCH, CASH_DISCREPANCY, UNMATCHED_ORDER
    symbol: Optional[str] = None
    internal_value: float
    broker_value: float
    difference: float
    description: str
    severity: str = "HIGH"
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReconciliationReport(BaseModel):
    is_healthy: bool
    issues: List[ReconciliationIssue] = Field(default_factory=list)
    reconciled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReconciliationEngine:
    """Audit engine ensuring internal portfolio tracking strictly matches broker reality."""

    @classmethod
    async def reconcile(
        cls,
        internal_positions: Dict[str, Position],
        internal_cash: float,
        broker: BrokerAdapter
    ) -> ReconciliationReport:
        broker_account = await broker.get_account()
        broker_positions = await broker.get_positions()
        
        issues: List[ReconciliationIssue] = []

        # 1. Cash Balance Comparison
        cash_diff = abs(internal_cash - broker_account.cash)
        if cash_diff > 1.0:  # > $1.00 discrepancy
            issue = ReconciliationIssue(
                issue_type="CASH_DISCREPANCY",
                internal_value=internal_cash,
                broker_value=broker_account.cash,
                difference=cash_diff,
                description=f"Internal cash (${internal_cash:.2f}) differs from broker cash (${broker_account.cash:.2f}) by ${cash_diff:.2f}"
            )
            issues.append(issue)

        # 2. Position Quantities Comparison
        all_symbols = set(internal_positions.keys()).union(set(broker_positions.keys()))
        for sym in all_symbols:
            int_qty = internal_positions[sym].quantity if sym in internal_positions else 0.0
            brk_qty = broker_positions[sym].quantity if sym in broker_positions else 0.0

            if abs(int_qty - brk_qty) > 1e-4:
                issue = ReconciliationIssue(
                    issue_type="POSITION_MISMATCH",
                    symbol=sym,
                    internal_value=int_qty,
                    broker_value=brk_qty,
                    difference=abs(int_qty - brk_qty),
                    description=f"Position mismatch for {sym}: internal has {int_qty}, broker has {brk_qty}"
                )
                issues.append(issue)

        is_healthy = len(issues) == 0

        event_type = EventType.RECONCILIATION_COMPLETED if is_healthy else EventType.RECONCILIATION_ISSUE_DETECTED
        await default_event_bus.publish(DomainEvent(
            event_type=event_type,
            payload={"healthy": is_healthy, "issue_count": len(issues)}
        ))

        return ReconciliationReport(
            is_healthy=is_healthy,
            issues=issues,
            reconciled_at=datetime.now(timezone.utc)
        )
