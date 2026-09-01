-- 1. Master Equity Universe
CREATE TABLE IF NOT EXISTS master_instruments (
    symbol TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    exchange TEXT DEFAULT 'NSE',
    sector TEXT,
    market_cap REAL,
    is_nifty500 INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    last_synced_at TIMESTAMP
);

-- 2. Canonical Partitioned Candle Store
CREATE TABLE IF NOT EXISTS equity_candles (
    symbol TEXT NOT NULL,
    exchange TEXT DEFAULT 'NSE',
    timeframe TEXT NOT NULL, -- '1D', '1W', '1M', '3M', '125M', '75M'
    candle_timestamp INTEGER NOT NULL, -- Epoch Unix Seconds (UTC)
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume INTEGER NOT NULL,
    is_adjusted INTEGER DEFAULT 1,
    PRIMARY KEY (symbol, exchange, timeframe, candle_timestamp),
    FOREIGN KEY (symbol) REFERENCES master_instruments(symbol) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_candles_lookup 
ON equity_candles(symbol, timeframe, candle_timestamp DESC);

-- 3. Deterministic Zone Cache & Explainability Record
CREATE TABLE IF NOT EXISTS zone_analytics_store (
    symbol TEXT NOT NULL,
    exchange TEXT DEFAULT 'NSE',
    timeframe TEXT NOT NULL,
    zone_type TEXT NOT NULL, -- 'DEMAND' or 'SUPPLY'
    proximal_price REAL NOT NULL,
    distal_price REAL NOT NULL,
    leg_in_time INTEGER,
    base_start_time INTEGER,
    base_end_time INTEGER,
    leg_out_time INTEGER,
    gtf_score REAL NOT NULL,
    freshness_score REAL NOT NULL,
    departure_score REAL NOT NULL,
    time_at_base_score REAL NOT NULL,
    curve_location REAL NOT NULL,
    algorithm_version TEXT NOT NULL,
    explanation_json TEXT NOT NULL,
    last_calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, exchange, timeframe, algorithm_version)
);

-- 4. Screener Execution Audit Log
CREATE TABLE IF NOT EXISTS sync_audit_log (
    run_id TEXT PRIMARY KEY,
    sync_date TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    total_universe INTEGER,
    success_count INTEGER,
    failure_count INTEGER,
    failed_symbols TEXT,
    status TEXT NOT NULL
);
