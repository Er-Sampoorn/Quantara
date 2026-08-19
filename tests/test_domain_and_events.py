import asyncio
from packages.domain.models import Instrument, AssetClass, Order, OrderSide, OrderType, OrderStatus
from packages.events.bus import EventBus
from packages.events.types import DomainEvent, EventType


def test_domain_models_creation():
    inst = Instrument(
        symbol="AAPL",
        name="Apple Inc.",
        asset_class=AssetClass.EQUITY,
        exchange="NASDAQ"
    )
    assert inst.symbol == "AAPL"
    assert inst.asset_class == AssetClass.EQUITY

    order = Order(
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100.0
    )
    assert order.status == OrderStatus.CREATED
    assert order.quantity == 100.0


def test_event_bus_pub_sub_and_idempotency():
    async def _run():
        bus = EventBus("TestBus")
        received_events = []

        async def handler(event: DomainEvent):
            received_events.append(event)

        bus.subscribe(EventType.ORDER_CREATED, handler)

        event1 = DomainEvent(
            event_type=EventType.ORDER_CREATED,
            payload={"order_id": "ord_1", "symbol": "AAPL"}
        )
        
        # Publish once
        await bus.publish(event1)
        await asyncio.sleep(0.05)
        assert len(received_events) == 1

        # Publish identical event (idempotency check)
        await bus.publish(event1)
        await asyncio.sleep(0.05)
        assert len(received_events) == 1  # Should ignore duplicate event_id

    asyncio.run(_run())
