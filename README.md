# HTF-Zone-Scanner-Terminal
Institutional Multi-Timeframe Supply & Demand Zone Scanner with Strict Fresh Spatial Overlap Engine for Indian Markets (NSE Equities).

## Core Capabilities
- **Timeframes Supported**:
  - Higher Timeframes (HTF): `3M` (Quarterly), `1M` (Monthly), `1W` (Weekly)
  - Execution & Intermediate Timeframes: `1D` (Daily), `125M` (125-Minute), `75M` (75-Minute)
- **Session-Aware Candle Aggregation**: Strictly adheres to the 375-minute Indian trading day (09:15 - 15:30 IST).
- **Institutional Supply & Demand Formations**:
  - Demand: DBR (Drop-Base-Rally), RBR (Rally-Base-Rally)
  - Supply: RBD (Rally-Base-Drop), DBD (Drop-Base-Drop)
  - Basing consolidation vs ERC institutional departure strength calculations.
- **Strict Freshness Evaluator**: Rejects any zone that has been penetrated or pierced by subsequent candle low/high.
- **Spatial Overlap Confluence Engine**: Computes 1D geometric range intersections across timeframes and filters strictly for **Achievements > 1** (Tier 2 and Tier 3 setups).

## Project Structure
```
HTF-Zone-Scanner-Terminal/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── router.py             # FastAPI routes (/api/v1/scan, /api/v1/health)
│   ├── core/
│   │   ├── config.py                 # Pydantic Settings
│   │   └── database.py               # Async SQLAlchemy engine & session factory
│   ├── domain/
│   │   ├── enums.py                  # Timeframe, ZoneDirection, FreshnessStatus, ZoneStructure
│   │   ├── models.py                 # SQLAlchemy ORM models (Instrument, Candle, Zone, OverlapCluster)
│   │   └── schemas.py                # Pydantic validation schemas
│   ├── engine/
│   │   ├── aggregator.py             # NSE session candle resampler (75M, 125M, 1D, 1W, 1M, 3M)
│   │   ├── zone_detector.py          # Institutional Supply/Demand zone detector
│   │   ├── freshness.py              # Strict freshness & penetration evaluator
│   │   ├── spatial_overlap.py        # Geometric price-interval overlap & Achievements > 1 calculator
│   │   └── pipeline.py               # Scanner orchestrator
│   └── main.py                       # FastAPI application factory & lifespan
├── tests/
│   ├── test_engine.py                # Unit tests for core engine
│   └── test_pipeline_api.py          # Integration tests for API
└── requirements.txt
```

## Running the API & Tests

### Run Tests
```bash
python -m pytest tests/ -v
```

### Run Server
```bash
uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/api/v1/health`
- Scanner Endpoint: `POST http://127.0.0.1:8000/api/v1/scan`
