import os
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "production_scanner.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH.replace(os.sep, '/')}"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def init_db():
    """Initializes all database tables asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for DB sessions in background tasks and CLI scripts."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency for DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
