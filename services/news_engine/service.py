"""
QUANTARA News Intelligence Engine
Ingestion, entity extraction, sentiment scoring, and impact classification.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from packages.domain.models import NewsImpact, NewsItem, SentimentLabel


class NewsEngine:
    """Manages news intelligence feeds and NLP sentiment extraction."""

    _DEMO_NEWS: List[NewsItem] = [
        NewsItem(
            id="news_1",
            headline="NVIDIA Announces Next-Generation Blackwell Ultra Architecture With Massive Compute Leaps",
            summary="NVIDIA unveiled its next-gen enterprise GPU architecture with enhanced tensor cores, projecting 4x throughput in large model inference.",
            source="Financial Times",
            symbols=["NVDA", "QQQ"],
            sectors=["Semiconductors", "Technology"],
            sentiment=SentimentLabel.BULLISH,
            sentiment_score=0.92,
            impact=NewsImpact.CRITICAL,
            confidence=0.95,
            published_at=datetime.now(timezone.utc) - timedelta(minutes=24)
        ),
        NewsItem(
            id="news_2",
            headline="Apple Services Revenue Hits All-Time Record of $24.2B, Gross Margin Reaches 46.2%",
            summary="Apple's high-margin services division accelerated subscription growth, cushioning slight hardware cyclicality.",
            source="Bloomberg",
            symbols=["AAPL"],
            sectors=["Technology", "Consumer Electronics"],
            sentiment=SentimentLabel.BULLISH,
            sentiment_score=0.84,
            impact=NewsImpact.HIGH,
            confidence=0.91,
            published_at=datetime.now(timezone.utc) - timedelta(hours=2)
        ),
        NewsItem(
            id="news_3",
            headline="Federal Reserve Holds Interest Rates Steady, Highlights Progress on Core Inflation",
            summary="Federal Open Market Committee maintains policy rate target range while updating macroeconomic dot-plot projections.",
            source="Reuters",
            symbols=["SPY", "QQQ"],
            sectors=["Broad Market", "Financials"],
            sentiment=SentimentLabel.NEUTRAL,
            sentiment_score=0.15,
            impact=NewsImpact.HIGH,
            confidence=0.88,
            published_at=datetime.now(timezone.utc) - timedelta(hours=4)
        ),
        NewsItem(
            id="news_4",
            headline="Microsoft Azure Expands Multi-Region AI Supercomputing Clusters for Enterprise Workloads",
            summary="Cloud commercial bookings expand 29% as enterprise clients migrate proprietary LLM workloads to Azure AI Foundry.",
            source="Wall Street Journal",
            symbols=["MSFT"],
            sectors=["Technology", "Cloud Computing"],
            sentiment=SentimentLabel.BULLISH,
            sentiment_score=0.88,
            impact=NewsImpact.HIGH,
            confidence=0.93,
            published_at=datetime.now(timezone.utc) - timedelta(hours=6)
        ),
        NewsItem(
            id="news_5",
            headline="Tesla Accelerates Full Self-Driving Version Deployment and Commercial Robotaxi Pilot",
            summary="Tesla prepares next regulatory filings for autonomous fleet operations across selected metropolitan markets.",
            source="CNBC",
            symbols=["TSLA"],
            sectors=["Automotive", "AI"],
            sentiment=SentimentLabel.NEUTRAL,
            sentiment_score=0.40,
            impact=NewsImpact.MEDIUM,
            confidence=0.80,
            published_at=datetime.now(timezone.utc) - timedelta(hours=8)
        )
    ]

    @classmethod
    def get_latest_news(cls, symbol: Optional[str] = None, limit: int = 10) -> List[NewsItem]:
        if symbol:
            sym = symbol.upper()
            filtered = [n for n in cls._DEMO_NEWS if sym in n.symbols or "SPY" in n.symbols]
            return filtered[:limit]
        return cls._DEMO_NEWS[:limit]

    @classmethod
    def ingest_article(
        cls,
        headline: str,
        summary: str,
        source: str,
        symbols: List[str]
    ) -> NewsItem:
        # Simple sentiment classification
        text = f"{headline} {summary}".lower()
        bullish_words = ["surge", "record", "growth", "boost", "profit", "beat", "expansion", "upward"]
        bearish_words = ["drop", "plunge", "decline", "loss", "miss", "recession", "lawsuit", "investigation"]

        pos_count = sum(1 for w in bullish_words if w in text)
        neg_count = sum(1 for w in bearish_words if w in text)

        if pos_count > neg_count:
            sentiment = SentimentLabel.BULLISH
            score = min(0.95, 0.4 + pos_count * 0.15)
        elif neg_count > pos_count:
            sentiment = SentimentLabel.BEARISH
            score = max(-0.95, -0.4 - neg_count * 0.15)
        else:
            sentiment = SentimentLabel.NEUTRAL
            score = 0.0

        impact = NewsImpact.HIGH if any(w in text for w in ["fed", "rate", "earnings", "ceo", "record"]) else NewsImpact.MEDIUM

        item = NewsItem(
            id=f"news_{uuid.uuid4().hex[:8]}",
            headline=headline,
            summary=summary,
            source=source,
            symbols=[s.upper() for s in symbols],
            sentiment=sentiment,
            sentiment_score=score,
            impact=impact,
            confidence=0.85,
            published_at=datetime.now(timezone.utc)
        )
        cls._DEMO_NEWS.insert(0, item)
        return item
