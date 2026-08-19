"""
QUANTARA Database Initial Seed Script
Populates demo users, instruments, strategies, and initializes database tables.
"""

from __future__ import annotations
import asyncio
import hashlib
from database.connection import Base, engine, async_session_factory
from database.schemas.models import InstrumentModel, StrategyModel, UserModel
from services.market_data.synthetic import SyntheticDataProvider


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


async def seed_database():
    print("[INFO] Checking database initialization...")
    if engine and async_session_factory:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session_factory() as session:
            from sqlalchemy import select
            res = await session.execute(select(UserModel))
            existing_users = res.scalars().all()
            if existing_users:
                print("[INFO] Database already initialized with users.")
                return

            print("[INFO] Seeding demo users...")
            admin_user = UserModel(
                id="usr_admin",
                email="admin@quantara.io",
                hashed_password=hash_password("Quantara2026!"),
                full_name="Quant Administrator",
                role="ADMIN",
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            print("[SUCCESS] Database tables and demo user initialized!")
    else:
        # Sync SQLite fallback
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        sync_eng = create_engine("sqlite:///./quantara.db", echo=False)
        Base.metadata.create_all(sync_eng)
        Session = sessionmaker(bind=sync_eng)
        with Session() as session:
            if not session.query(UserModel).first():
                admin_user = UserModel(
                    id="usr_admin",
                    email="admin@quantara.io",
                    hashed_password=hash_password("Quantara2026!"),
                    full_name="Quant Administrator",
                    role="ADMIN",
                    is_active=True
                )
                session.add(admin_user)
                session.commit()
                print("[SUCCESS] Sync SQLite Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
