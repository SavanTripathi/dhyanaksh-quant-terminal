import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.domain.models import TradePlanModel
from app.api.v1.router import router as api_v1_router
from app.engine.batch_scanner import BatchScannerEngine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Automatically initialize SQLite tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 2. Check if DB has trade plans; if not or stale, trigger non-blocking initial scan
    async def auto_seed_scan():
        await asyncio.sleep(1.0)
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(func.count(TradePlanModel.id)))
            count = res.scalar() or 0
            if count == 0:
                scanner = BatchScannerEngine()
                await scanner.execute_batch_scan(db, lookback_days=180, min_achievements=2)

    asyncio.create_task(auto_seed_scan())
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Institutional Supply and Demand Multi-Timeframe Zone Scanner with Strict Fresh Spatial Overlap (Achievements > 1)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "Welcome to HTF-Zone-Scanner-Terminal API",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
