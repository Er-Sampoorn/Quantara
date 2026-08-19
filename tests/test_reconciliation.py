import asyncio
from packages.brokers.paper import PaperBroker
from packages.domain.models import Position, OrderSide
from services.reconciliation_engine.reconciler import ReconciliationEngine


def test_reconciliation_detects_position_and_cash_discrepancies():
    async def _run():
        broker = PaperBroker(initial_cash=100_000.0)
        await broker.connect()

        # Internal state with simulated out-of-sync position
        internal_positions = {
            "AAPL": Position(
                symbol="AAPL",
                quantity=50.0,
                entry_price=150.0,
                current_price=150.0,
                market_value=7500.0,
                unrealized_pnl=0.0,
                unrealized_pnl_pct=0.0,
                side=OrderSide.BUY
            )
        }
        internal_cash = 90_000.0  # Broker has $100,000, mismatch is $10,000

        report = await ReconciliationEngine.reconcile(internal_positions, internal_cash, broker)

        assert not report.is_healthy
        assert len(report.issues) >= 2  # One cash discrepancy, one position mismatch
        assert any(i.issue_type == "CASH_DISCREPANCY" for i in report.issues)
        assert any(i.issue_type == "POSITION_MISMATCH" for i in report.issues)

    asyncio.run(_run())
