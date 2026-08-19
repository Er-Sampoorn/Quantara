import pytest
from packages.domain.models import Order, OrderSide, OrderType, Portfolio, Position
from packages.risk.engine import RiskEngine


def test_risk_gate_blocks_excessive_position_size():
    risk_engine = RiskEngine(max_position_size_pct=0.20)  # Max 20% allocation

    portfolio = Portfolio(
        user_id="test_user",
        cash=100_000.0,
        equity=100_000.0,
        positions={}
    )

    # Order requesting $30,000 (30% allocation) -> MUST BE REJECTED
    order = Order(
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=150.0  # 150 * $200 = $30,000
    )

    evaluation = risk_engine.evaluate_order(order, portfolio, current_market_price=200.0)
    assert not evaluation.approved
    assert any("MAX_POSITION_SIZE" in r.rule_name and not r.passed for r in evaluation.evaluations)


def test_risk_circuit_breaker_stops_all_orders():
    risk_engine = RiskEngine()
    risk_engine.trip_circuit_breaker("Emergency drawdown threshold exceeded")

    portfolio = Portfolio(user_id="test_user", cash=100_000.0, equity=100_000.0)
    order = Order(symbol="AAPL", side=OrderSide.BUY, order_type=OrderType.MARKET, quantity=1.0)

    evaluation = risk_engine.evaluate_order(order, portfolio, current_market_price=100.0)
    assert not evaluation.approved
    assert "CIRCUIT_BREAKER_CHECK" in evaluation.evaluations[0].rule_name
