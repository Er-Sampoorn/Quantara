"""
QUANTARA Research Workspaces API Router
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from packages.domain.models import ResearchWorkspace
from services.research_engine.workspace import ResearchWorkspaceService

router = APIRouter(prefix="/research", tags=["Research"])


class CreateWorkspaceRequest(BaseModel):
    title: str
    description: str
    symbols: List[str]
    notes: Optional[str] = ""


class UpdateWorkspaceRequest(BaseModel):
    title: Optional[str] = None
    notes: Optional[str] = None
    symbols: Optional[List[str]] = None


@router.get("/workspaces", response_model=List[ResearchWorkspace])
async def list_workspaces():
    return ResearchWorkspaceService.list_workspaces()


@router.get("/workspaces/{workspace_id}", response_model=ResearchWorkspace)
async def get_workspace(workspace_id: str):
    ws = ResearchWorkspaceService.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws


@router.post("/workspaces", response_model=ResearchWorkspace)
async def create_workspace(req: CreateWorkspaceRequest):
    return ResearchWorkspaceService.create_workspace(
        title=req.title,
        description=req.description,
        symbols=req.symbols,
        notes=req.notes or ""
    )


@router.patch("/workspaces/{workspace_id}", response_model=ResearchWorkspace)
async def update_workspace(workspace_id: str, req: UpdateWorkspaceRequest):
    ws = ResearchWorkspaceService.update_workspace(
        workspace_id=workspace_id,
        title=req.title,
        notes=req.notes,
        symbols=req.symbols
    )
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws
