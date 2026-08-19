"""
QUANTARA AI Multi-Agent Intelligence & Copilot API Router
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from packages.domain.models import MultiAgentResearchReport
from services.ai_engine.agents import ResearchSynthesizerAgent
from services.ai_engine.copilot import AICopilot

router = APIRouter(prefix="/ai", tags=["AI Intelligence"])


class CopilotQueryRequest(BaseModel):
    query: str
    symbol: Optional[str] = "AAPL"
    context: Optional[Dict[str, Any]] = None


@router.post("/analyze/{symbol}", response_model=MultiAgentResearchReport)
async def analyze_symbol_multi_agent(symbol: str):
    """Executes 5 specialist research agents (Market, Fundamental, Sentiment, Quant, Risk) and synthesizer."""
    return await ResearchSynthesizerAgent.synthesize(symbol.upper())


@router.post("/copilot/chat")
async def copilot_chat(req: CopilotQueryRequest):
    """Answers user quantitative questions grounded directly in real stored data."""
    return await AICopilot.process_query(req.query, req.symbol, req.context)
