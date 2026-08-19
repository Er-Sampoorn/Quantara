"""
QUANTARA Database Engine & Session Management
SQLAlchemy 2.0 engine supporting TimescaleDB / PostgreSQL with dynamic fallback.
"""

from __future__ import annotations
import os
from typing import AsyncGenerator
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quantara.db")

Base = declarative_base()

try:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    # If standard postgres url provided, rewrite to asyncpg driver if available
    async_db_url = DATABASE_URL
    if async_db_url.startswith("postgresql://"):
        async_db_url = async_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif async_db_url.startswith("postgres://"):
        async_db_url = async_db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif async_db_url.startswith("sqlite:///"):
        # Check if aiosqlite is available
        try:
            import aiosqlite
            async_db_url = async_db_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        except ImportError:
            pass

    if "sqlite+aiosqlite" in async_db_url or "postgresql+asyncpg" in async_db_url:
        engine = create_async_engine(
            async_db_url,
            echo=False,
            future=True,
            pool_pre_ping=True if "sqlite" not in async_db_url else False,
        )
        async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    else:
        # Fallback dummy/sync compatibility wrapper
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        sync_engine = create_engine("sqlite:///./quantara.db", echo=False)
        sync_session_factory = sessionmaker(bind=sync_engine, expire_on_commit=False)
        engine = None
        async_session_factory = None
except Exception:
    engine = None
    async_session_factory = None


async def get_db_session() -> AsyncGenerator[Any, None]:
    """FastAPI Dependency for database sessions."""
    if async_session_factory:
        async with async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    else:
        yield None
