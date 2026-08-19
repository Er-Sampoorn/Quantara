"""
QUANTARA API Gateway & Real-Time WebSocket Server
Main FastAPI application entry point.
"""

from __future__ import annotations
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import List, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from apps.api.auth import router as auth_router
from apps.api.routers.ai import router as ai_router
from apps.api.routers.backtests import router as backtests_router
from apps.api.routers.brokers import router as brokers_router
from apps.api.routers.journal import router as journal_router
from apps.api.routers.markets import router as markets_router
from apps.api.routers.optimization import router as optimization_router
from apps.api.routers.orders import router as orders_router
from apps.api.routers.portfolio import router as portfolio_router
from apps.api.routers.research import router as research_router
from apps.api.routers.risk import router as risk_router
from apps.api.routers.screener import router as screener_router
from apps.api.routers.signals import router as signals_router
from apps.api.routers.strategies import router as strategies_router
from apps.api.routers.system import router as system_router
from database.seeds.seed_data import seed_database
from packages.events.bus import default_event_bus
from packages.events.types import DomainEvent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("quantara.api")


# ==========================================
# WebSocket Connection Manager
# ==========================================
class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")

    async def broadcast_json(self, data: dict):
        if not self.active_connections:
            return
        dead_connections = set()
        for conn in list(self.active_connections):
            try:
                await conn.send_json(data)
            except Exception:
                dead_connections.add(conn)
        for dead in dead_connections:
            self.active_connections.discard(dead)


ws_manager = WebSocketManager()


async def on_domain_event(event: DomainEvent):
    """Forward internal domain events to all connected WebSocket clients in real-time."""
    await ws_manager.broadcast_json({
        "type": event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type),
        "payload": event.payload,
        "timestamp": event.timestamp.isoformat()
    })


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize and Seed Database
    logger.info("Initializing Quantara backend services...")
    try:
        await seed_database()
    except Exception as e:
        logger.warning(f"Database seed notice: {e}")

    # Subscribe WebSocket forwarder to global event bus
    default_event_bus.subscribe_all(on_domain_event)
    logger.info("Quantara API Gateway fully operational.")
    yield
    logger.info("Shutting down Quantara API Gateway...")


app = FastAPI(
    title="QUANTARA — AI Quantitative Trading & Research Platform",
    description="Deterministic quantitative execution, multi-agent AI research, and risk management API Gateway.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API Routers under /api/v1
app.include_router(auth_router, prefix="/api/v1")
app.include_router(markets_router, prefix="/api/v1")
app.include_router(signals_router, prefix="/api/v1")
app.include_router(strategies_router, prefix="/api/v1")
app.include_router(backtests_router, prefix="/api/v1")
app.include_router(optimization_router, prefix="/api/v1")
app.include_router(portfolio_router, prefix="/api/v1")
app.include_router(risk_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(journal_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(screener_router, prefix="/api/v1")
app.include_router(research_router, prefix="/api/v1")
app.include_router(brokers_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "platform": "QUANTARA",
        "version": "1.0.0",
        "documentation": "/docs",
        "api_v1": "/api/v1",
        "websocket": "/ws",
        "status": "OPERATIONAL"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send initial handshake message
        await websocket.send_json({
            "type": "connection.established",
            "message": "Connected to Quantara Live Event Stream",
            "channels": ["market.quote", "signal.generated", "execution.order.filled", "risk.circuit_breaker.triggered"]
        })
        while True:
            # Keep connection alive and listen for client subscriptions or heartbeats
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
