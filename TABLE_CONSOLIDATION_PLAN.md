# BigQuery Table Consolidation Plan

## Executive Summary

Based on the database audit (December 5, 2025), the current database has:
- **140 tables** across 8 categories
- **7.5M rows** / **2.35 GB** total
- **26 empty tables** that should be removed
- **Significant duplication** (e.g., stocks_historical_daily and v2_stocks_historical_daily with identical row counts)

This plan consolidates 140 tables into **7 unified tables** + **3 support tables**.

---

## Current State Analysis

### Tables by Category

| Category | Current Tables | Total Rows | Avg Rows/Table | % of Data |
|----------|---------------|------------|----------------|-----------|
| Stocks | 35 | 4,118,838 | 117,681 | 54.8% |
| ETFs | 15 | 1,356,436 | 90,429 | 18.1% |
| Crypto | 30 | 925,126 | 30,838 | 12.3% |
| Forex | 16 | 448,862 | 28,054 | 6.0% |
| Commodities | 15 | 411,142 | 27,409 | 5.5% |
| Indices | 15 | 235,141 | 15,676 | 3.1% |
| Other | 12 | 15,606 | 1,300 | 0.2% |
| Bonds | 2 | 1,532 | 766 | 0.0% |

### Issues Identified

1. **Duplicate Tables**: Multiple versions exist (v2_, _v2, historical_, etc.)
2. **Empty Tables**: 26 tables with 0 rows
3. **Fragmented Timeframes**: Separate tables for daily, hourly, 5min, weekly
4. **Inconsistent Naming**: Mix of snake_case conventions

---

## Target State: Unified Schema

### 7 Asset Tables (Partitioned + Clustered)

```sql
-- Template for all asset tables
CREATE TABLE `cryptobot-462709.crypto_trading_data.{asset_type}_unified` (
    -- Identifiers
    symbol STRING NOT NULL,
    timeframe STRING NOT NULL,  -- 'weekly', 'daily', 'hourly', '5min'

    -- Time (Partition Key)
    datetime TIMESTAMP NOT NULL,

    -- OHLCV Data
    open FLOAT64,
    high FLOAT64,
    low FLOAT64,
    close FLOAT64,
    volume INT64,

    -- Calculated Fields
    price_change FLOAT64,
    price_change_pct FLOAT64,
    range_hl FLOAT64,

    -- Trend Indicators
    sma_20 FLOAT64,
    sma_50 FLOAT64,
    sma_200 FLOAT64,
    ema_12 FLOAT64,
    ema_26 FLOAT64,
    ema_50 FLOAT64,

    -- Momentum Indicators
    rsi FLOAT64,
    macd FLOAT64,
    macd_signal FLOAT64,
    macd_histogram FLOAT64,
    stoch_k FLOAT64,
    stoch_d FLOAT64,
    williams_r FLOAT64,
    roc FLOAT64,
    momentum FLOAT64,

    -- Volatility Indicators
    atr FLOAT64,
    bollinger_upper FLOAT64,
    bollinger_middle FLOAT64,
    bollinger_lower FLOAT64,

    -- Trend Strength
    adx FLOAT64,
    plus_di FLOAT64,
    minus_di FLOAT64,

    -- Volume Indicators
    obv INT64,
    pvo FLOAT64,

    -- Other Oscillators
    cci FLOAT64,
    ppo FLOAT64,
    ultimate_osc FLOAT64,
    awesome_osc FLOAT64,
    kama FLOAT64,
    trix FLOAT64,

    -- Metadata
    exchange STRING,
    currency STRING,
    country STRING,
    data_source STRING DEFAULT 'twelvedata',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(datetime)
CLUSTER BY symbol, timeframe
OPTIONS (
    description = '{Asset Type} unified data - all timeframes',
    require_partition_filter = true
);
```

### Tables to Create

| New Table | Replaces | Estimated Rows |
|-----------|----------|----------------|
| `stocks_unified` | 35 stock tables | ~4.1M |
| `crypto_unified` | 30 crypto tables | ~925K |
| `etfs_unified` | 15 ETF tables | ~1.4M |
| `forex_unified` | 16 forex tables | ~450K |
| `commodities_unified` | 15 commodity tables | ~411K |
| `indices_unified` | 15 index tables | ~235K |
| `bonds_unified` | 2 bond tables | ~2K |

### Support Tables

```sql
-- Users & Authentication
CREATE TABLE `cryptobot-462709.crypto_trading_data.users` (
    user_id STRING NOT NULL,
    email STRING NOT NULL,
    display_name STRING,
    role STRING DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    last_login TIMESTAMP,
    preferences JSON
);

-- Data Quality Monitoring
CREATE TABLE `cryptobot-462709.crypto_trading_data.data_quality_log` (
    check_id STRING NOT NULL,
    check_type STRING NOT NULL,
    asset_type STRING,
    timeframe STRING,
    status STRING,  -- 'pass', 'fail', 'warning'
    message STRING,
    metrics JSON,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(checked_at);

-- Scheduler Execution Log
CREATE TABLE `cryptobot-462709.crypto_trading_data.scheduler_log` (
    execution_id STRING NOT NULL,
    job_name STRING NOT NULL,
    status STRING,
    records_processed INT64,
    errors_count INT64,
    duration_seconds FLOAT64,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
)
PARTITION BY DATE(started_at);
```

---

## Migration Plan

### Phase 1: Preparation (Day 1)

1. **Create new unified tables** (empty)
2. **Create staging tables** for data transformation
3. **Backup existing tables** (export to Cloud Storage)

### Phase 2: Data Migration (Days 2-3)

```sql
-- Example: Migrate stocks data
INSERT INTO `cryptobot-462709.crypto_trading_data.stocks_unified`
SELECT
    symbol,
    'daily' as timeframe,
    datetime,
    open, high, low, close, volume,
    -- ... all other columns
    'twelvedata' as data_source,
    CURRENT_TIMESTAMP() as created_at,
    CURRENT_TIMESTAMP() as updated_at
FROM `cryptobot-462709.crypto_trading_data.v2_stocks_daily`
WHERE datetime IS NOT NULL;

-- Repeat for each source table and timeframe
```

### Phase 3: Validation (Day 4)

```sql
-- Verify row counts match
SELECT
    'stocks_unified' as table_name,
    COUNT(*) as new_count,
    (SELECT SUM(row_count) FROM (
        SELECT COUNT(*) as row_count FROM v2_stocks_daily
        UNION ALL
        SELECT COUNT(*) FROM v2_stocks_hourly
        -- ... etc
    )) as original_count
FROM stocks_unified;
```

### Phase 4: Cutover (Day 5)

1. **Update API endpoints** to query unified tables
2. **Update data pipelines** to write to unified tables
3. **Rename old tables** with `_deprecated` suffix
4. **Monitor for 7 days** before deletion

### Phase 5: Cleanup (Day 12+)

1. **Delete deprecated tables**
2. **Update documentation**
3. **Notify stakeholders**

---

## Tables to Delete (26 Empty Tables)

```sql
-- Empty tables that can be dropped immediately
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.5min_stock`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.active_trading_list`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.bonds_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.commodities_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.commodities_hourly_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.crypto_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.crypto_hourly_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.etfs_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.etfs_hourly_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.forex_5min_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.forex_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.forex_hourly_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.hourly_stock`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.indices_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.indices_hourly_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.market_news_sentiment`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.scheduler_summary_view`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.social_sentiment`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.stock_5min_top10_gainers`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.stock_hourly_data`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.stocks_5min_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.stocks_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.stocks_hourly_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.trading_sessions`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.unified_weekly_analysis`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.user_trades`;
```

---

## Expected Benefits

### Performance
- **10-100x faster queries** for full asset class analysis
- **Sub-second response** for symbol lookups (clustering)
- **Efficient time-range queries** (partitioning)

### Cost
- **~50% storage reduction** by eliminating duplicates
- **~90% query cost reduction** with partition filters
- **Automatic long-term storage** savings

### Maintainability
- **7 tables** instead of 140 to manage
- **Single schema** per asset type
- **Simplified data pipelines**

---

## Query Examples (Post-Migration)

```sql
-- Get latest daily data for a stock
SELECT * FROM stocks_unified
WHERE symbol = 'AAPL'
  AND timeframe = 'daily'
  AND datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
ORDER BY datetime DESC;

-- Get all timeframes for a crypto
SELECT
    symbol,
    timeframe,
    COUNT(*) as data_points,
    MIN(datetime) as first_record,
    MAX(datetime) as last_record
FROM crypto_unified
WHERE symbol = 'BTC/USD'
GROUP BY symbol, timeframe;

-- Cross-asset analysis
SELECT
    'stocks' as asset_type, AVG(rsi) as avg_rsi, AVG(adx) as avg_adx
FROM stocks_unified WHERE timeframe = 'daily' AND datetime = CURRENT_DATE() - 1
UNION ALL
SELECT
    'crypto', AVG(rsi), AVG(adx)
FROM crypto_unified WHERE timeframe = 'daily' AND datetime = CURRENT_DATE() - 1;
```

---

## Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Preparation | 1 day | Pending |
| Phase 2: Migration | 2 days | Pending |
| Phase 3: Validation | 1 day | Pending |
| Phase 4: Cutover | 1 day | Pending |
| Phase 5: Cleanup | 1 week after | Pending |

**Total estimated time: 5 days + 1 week monitoring**

---

*Generated: December 5, 2025*
*Database Audit: 140 tables, 7.5M rows, 2.35 GB*
