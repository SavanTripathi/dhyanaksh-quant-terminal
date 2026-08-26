"""
Global Pytest Fixture Configuration.
Initializes and refreshes tables before running async tests.
"""
import pytest
import pytest_asyncio
from app.core.database import engine, Base
import app.domain.models  # Ensure all models are registered


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        # Drop all tables first to ensure schema changes (like lifecycle_state) are cleanly migrated
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
