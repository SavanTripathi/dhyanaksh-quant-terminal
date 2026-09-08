"""
Global Pytest Fixture Configuration.
Initializes and refreshes tables before running async tests in an isolated test database.
"""
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core import database
from app.core.database import Base
import app.domain.models  # Ensure all models are registered

TEST_DB_PATH = os.path.join(database.BASE_DIR, "test_scanner.db")
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH.replace(os.sep, '/')}"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
database.engine = test_engine
database.AsyncSessionLocal.configure(bind=test_engine)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with database.engine.begin() as conn:
        # Drop all tables first to ensure schema changes (like lifecycle_state) are cleanly migrated
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()
