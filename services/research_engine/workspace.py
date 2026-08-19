"""
QUANTARA Research Workspace Manager
Manages quantitative research notebooks, saved queries, market notes, and multi-asset workspaces.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from packages.domain.models import ResearchWorkspace


class ResearchWorkspaceService:
    """In-memory and persisted storage for quantitative research sessions."""

    _WORKSPACES: Dict[str, ResearchWorkspace] = {
        "ws_momentum_alpha": ResearchWorkspace(
            id="ws_momentum_alpha",
            title="Cross-Asset Momentum & Volatility Regimes",
            description="Investigating lead-lag relationships in mega-cap technology and broad ETFs under high volatility regimes.",
            symbols=["AAPL", "NVDA", "MSFT", "QQQ"],
            notes="Initial observations: Dual momentum outperforms during trending bull regimes with ADX > 25. Need to stress-test with 2022 rate hike regimes.",
            saved_queries=[
                {"name": "Tech Momentum Screen", "filter": "RSI > 50 and Price > EMA50"}
            ],
            linked_strategies=["sma_crossover", "dual_momentum"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
        "ws_mean_reversion": ResearchWorkspace(
            id="ws_mean_reversion",
            title="Statistical Mean Reversion in Overbought Equities",
            description="Analyzing bounce probability on RSI < 30 and lower Bollinger band touch across S&P 500 components.",
            symbols=["SPY", "TSLA", "AAPL"],
            notes="Mean reversion strategies show elevated Sharpe in Sideways and Low Volatility regimes. Avoid entries during Panic regimes.",
            saved_queries=[],
            linked_strategies=["rsi_mean_reversion", "bollinger_mean_reversion"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    }

    @classmethod
    def list_workspaces(cls) -> List[ResearchWorkspace]:
        return list(cls._WORKSPACES.values())

    @classmethod
    def get_workspace(cls, workspace_id: str) -> Optional[ResearchWorkspace]:
        return cls._WORKSPACES.get(workspace_id)

    @classmethod
    def create_workspace(
        cls,
        title: str,
        description: str,
        symbols: List[str],
        notes: str = "",
    ) -> ResearchWorkspace:
        ws_id = f"ws_{uuid.uuid4().hex[:8]}"
        ws = ResearchWorkspace(
            id=ws_id,
            title=title,
            description=description,
            symbols=[s.upper() for s in symbols],
            notes=notes,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        cls._WORKSPACES[ws_id] = ws
        return ws

    @classmethod
    def update_workspace(
        cls,
        workspace_id: str,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        symbols: Optional[List[str]] = None,
    ) -> Optional[ResearchWorkspace]:
        if workspace_id not in cls._WORKSPACES:
            return None
        ws = cls._WORKSPACES[workspace_id]
        if title:
            ws.title = title
        if notes is not None:
            ws.notes = notes
        if symbols:
            ws.symbols = [s.upper() for s in symbols]
        ws.updated_at = datetime.now(timezone.utc)
        return ws
