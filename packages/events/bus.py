"""
QUANTARA Event Bus
Asynchronous in-memory event bus with subscriber handlers, filtering, and Redis stream fallback.
"""

from __future__ import annotations
import asyncio
import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set
from packages.events.types import DomainEvent, EventType

logger = logging.getLogger("quantara.event_bus")

EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]


class EventBus:
    def __init__(self, name: str = "QuantaraEventBus"):
        self.name = name
        self._subscribers: Dict[EventType, List[EventHandler]] = {}
        self._global_subscribers: List[EventHandler] = []
        self._processed_events: Set[str] = set()
        self._lock = asyncio.Lock()
        self._history: List[DomainEvent] = []
        self._max_history = 1000

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe a handler to a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
            logger.debug(f"Subscribed {handler.__name__} to {event_type.value}")

    def subscribe_all(self, handler: EventHandler) -> None:
        """Subscribe a handler to all events on the bus."""
        if handler not in self._global_subscribers:
            self._global_subscribers.append(handler)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event to all subscribers idempotently."""
        async with self._lock:
            # Idempotency check
            if event.event_id in self._processed_events:
                logger.warning(f"Duplicate event detected and ignored: {event.event_id}")
                return
            self._processed_events.add(event.event_id)
            if len(self._processed_events) > 10000:
                self._processed_events.clear()

            # Record history
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history.pop(0)

        # Notify specific type subscribers
        handlers = list(self._subscribers.get(event.event_type, []))
        # Add global subscribers
        handlers.extend(self._global_subscribers)

        for handler in handlers:
            try:
                # Run handler asynchronously
                asyncio.create_task(self._safe_execute_handler(handler, event))
            except Exception as e:
                logger.error(f"Error dispatching event {event.event_type.value} to handler {handler}: {e}")

    async def _safe_execute_handler(self, handler: EventHandler, event: DomainEvent) -> None:
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Handler {handler.__name__} failed processing {event.event_type.value}: {e}", exc_info=True)

    def get_history(self, limit: int = 100, event_type: Optional[EventType] = None) -> List[DomainEvent]:
        if event_type:
            filtered = [e for e in self._history if e.event_type == event_type]
            return filtered[-limit:]
        return self._history[-limit:]

    def clear(self) -> None:
        self._subscribers.clear()
        self._global_subscribers.clear()
        self._processed_events.clear()
        self._history.clear()


# Global Singleton Bus Instance
default_event_bus = EventBus()
