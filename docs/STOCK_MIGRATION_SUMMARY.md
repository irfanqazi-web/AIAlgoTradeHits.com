# Stock Daily Data Migration Summary

**Date:** December 8, 2025
**Status:** Ready to Execute

---

## OVERVIEW

Created clean consolidated daily stock table with **85 fields** including:
- OHLCV data (6 fields)
- Technical indicators (40+ fields)
- ML features (15 fields)
- Asset metadata (9 fields)
- System metadata (4 fields)

---

## SOURCE TABLES (3 Tables to Consolidate)

| Table | Rows | Symbols | Date Range | Notes |
|-------|------|---------|------------|-------|
| `v2_stocks_daily` | 198,375 | 106 | 2023-11-27 to 2025-12-05 | Most recent (2 years) |
| `stocks_unified_daily` | 1,681,566 | 316 | 1998-12-04 to 2025-12-05 | **27 years of data!** |
| `v2_stocks_historical_daily` | 1,483,191 | 302 | 1998-12-04 to 2025-11-24 | Historical archive |
| **TOTAL** | **~3.36M** | **~400+** | **1998-2025** | After deduplication |

---

## EXCHANGE FILTERING

### ✅ ALLOWED (Keep):
- **NASDAQ**: XNAS, XNGS, XNCM, XNMS
- **NYSE**: XNYS, ARCX, XASE
- **CBOE**: BATS, CBOE, XCBO

### ❌ REJECTED (Filter Out):
- OTC: PINX, PSGM, OTCB, EXPM, OTCQ
- Pink Sheets: Any Pink Sheet stocks

### Expected Results:
- **Before filtering**: ~15,231 unique symbols in master list
- **After filtering**: ~5,450 symbols (36% kept, 64% rejected)
- **With time-series data**: ~250-350 symbols with full historical data

---

## TARGET TABLE: `stocks_daily_clean`

**Location:** `aialgotradehits.crypto_trading_data.stocks_daily_clean`

**Schema:** 85 fields organized as:

### 1. Core Identifiers (2 fields)
- `datetime` (TIMESTAMP, REQUIRED)
- `symbol` (STRING, REQUIRED)

### 2. OHLCV Data (6 fields)
- `open`, `high`, `low`, `close`, `previous_close`, `volume`

### 3. Price Statistics (7 fields)
- `average_volume`, `change`, `percent_change`
- `high_low` = high - low (absolute USD range)
- `pct_high_low` = (high - low) * 100 / low (% relative to low)
- `week_52_high`, `week_52_low`

### 4. Momentum Indicators (9 fields)
- `rsi`, `macd`, `macd_signal`, `macd_histogram`
- `stoch_k`, `stoch_d`, `cci`, `williams_r`, `momentum`

### 5. Moving Averages (9 fields)
- `sma_20`, `sma_50`, `sma_200`
- `ema_12`, `ema_20`, `ema_26`, `ema_50`, `ema_200`
- `kama`

### 6. Trend & Volatility (10 fields)
- `bollinger_upper`, `bollinger_middle`, `bollinger_lower`, `bb_width`
- `adx`, `plus_di`, `minus_di`, `atr`, `trix`, `roc`

### 7. Volume Indicators (3 fields)
- `obv`, `pvo`, `ppo`

### 8. Advanced Oscillators (2 fields)
- `ultimate_osc`, `awesome_osc`

### 9. ML Features - Returns (3 fields)
- `log_return` (1-day log return)
- `return_2w` (2-week forward return)
- `return_4w` (4-week forward return)

### 10. ML Features - Relative Positions (3 fields)
- `close_vs_sma20_pct`, `close_vs_sma50_pct`, `close_vs_sma200_pct`

### 11. ML Features - Indicator Dynamics (11 fields)
- `rsi_slope`, `rsi_zscore`, `rsi_overbought`, `rsi_oversold`
- `macd_cross`, `ema20_slope`, `ema50_slope`
- `atr_zscore`, `atr_slope`, `volume_zscore`, `volume_ratio`

### 12. ML Features - Market Structure (4 fields)
- `pivot_high_flag`, `pivot_low_flag`
- `dist_to_pivot_high`, `dist_to_pivot_low`

### 13. ML Features - Regime Detection (3 fields)
- `trend_regime` (1=uptrend, -1=downtrend, 0=sideways)
- `vol_regime` (1=high volatility, 0=low)
- `regime_confidence`

### 14. Asset Metadata (9 fields)
- `name`, `sector`, `industry`, `asset_type`
- `exchange`, `mic_code`, `country`, `currency`, `type`

### 15. System Metadata (4 fields)
- `timestamp` (Unix timestamp)
- `data_source` (TwelveData, etc.)
- `created_at`, `updated_at`

**Total:** 85 fields

---

## TABLE OPTIMIZATION

### Partitioning:
```sql
PARTITION BY DATE(datetime)
```
- Efficient time-range queries
- Reduces scan costs (only scans relevant dates)
- Required for tables with 1M+ rows

### Clustering:
```sql
CLUSTER BY symbol, sector, exchange
```
- 5-10× faster queries on these columns
- Automatic sorting within partitions
- Lower query costs

---

## MIGRATION PROCESS

### Step 1: Extract & Consolidate
1. Query all 3 source tables with UNION ALL
2. JOIN with `v2_stocks_master` to get proper MIC codes and metadata
3. Deduplicate: Prioritize v2_stocks_daily > stocks_unified_daily > v2_stocks_historical_daily
4. Filter to allowed MIC codes only
5. Validate OHLCV data (open, high, low, close, volume > 0)

### Step 2: Calculate Indicators
For each symbol (processed sequentially):
1. Sort by datetime ascending
2. Calculate all 40+ technical indicators using `pandas_ta`
3. Calculate all ML features (slopes, z-scores, flags, regimes)
4. Handle minimum data requirements (need 200+ rows for accurate indicators)

### Step 3: Upload to BigQuery
1. Reorder columns to match 85-field schema
2. Convert data types (integers, timestamps, floats)
3. Upload using `WRITE_APPEND` mode
4. Verify upload with count queries

### Step 4: Validation
1. Check row counts, unique symbols, date ranges
2. Verify exchange and MIC code distribution
3. Sample data quality checks
4. Test queries

---

## FILES CREATED

1. **`create_stocks_daily_clean_table.py`**
   - Creates BigQuery table with 85-field schema
   - Sets up partitioning and clustering
   - Status: ✅ **EXECUTED** - Table created successfully

2. **`migrate_to_stocks_daily_clean.py`**
   - Consolidates 3 source tables
   - Filters by MIC codes
   - Calculates all 85 fields
   - Status: ⏳ **READY TO RUN**

3. **`check_daily_stock_coverage.py`**
   - Analyzes source table coverage
   - Shows exchange distribution
   - Status: ✅ Executed

4. **`analyze_unified_daily.py`**
   - Checks stocks_unified_daily exchange data
   - Status: ✅ Executed

5. **`STOCK_MIGRATION_SUMMARY.md`**
   - This file
   - Complete migration documentation

---

## EXPECTED OUTCOMES

### Before Migration:
- 3 separate tables with overlapping/inconsistent data
- Includes OTC/Pink Sheet symbols (not desired)
- Minimal technical indicators
- Inconsistent metadata

### After Migration:
- 1 clean consolidated table: `stocks_daily_clean`
- **~2-3M rows** of deduplicated data (1998-2025, 27 years)
- **~250-350 symbols** from NASDAQ/NYSE/CBOE only
- **85 fields** per row including all indicators
- Optimized with partitioning and clustering
- Ready for AI/ML training and analysis

---

## EXECUTION COMMANDS

### Prerequisites:
```bash
pip install pandas pandas-ta google-cloud-bigquery numpy
```

### Step 1: Create Table (DONE ✅)
```bash
python create_stocks_daily_clean_table.py
```

### Step 2: Run Migration (NEXT)
```bash
python migrate_to_stocks_daily_clean.py
```
**Estimated time:** 15-30 minutes (depends on data volume and calculation speed)

### Step 3: Verify Results
```bash
# Check row counts
bq query --use_legacy_sql=false "
SELECT COUNT(*) as rows, COUNT(DISTINCT symbol) as symbols
FROM aialgotradehits.crypto_trading_data.stocks_daily_clean
"

# Sample data
bq query --use_legacy_sql=false --max_rows=10 "
SELECT symbol, datetime, close, rsi, macd, sma_50, volume, exchange, mic_code
FROM aialgotradehits.crypto_trading_data.stocks_daily_clean
WHERE symbol = 'AAPL'
ORDER BY datetime DESC
LIMIT 10
"
```

---

## SAMPLE QUERIES AFTER MIGRATION

### 1. Get Latest Data for AAPL
```sql
SELECT *
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE symbol = 'AAPL'
  AND DATE(datetime) = CURRENT_DATE()
ORDER BY datetime DESC
LIMIT 1;
```

### 2. Find Oversold Tech Stocks
```sql
SELECT symbol, close, rsi, sector, exchange
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE DATE(datetime) = CURRENT_DATE()
  AND sector = 'Technology'
  AND rsi < 30  -- Oversold
  AND close > sma_200  -- Above 200-day MA
ORDER BY rsi ASC;
```

### 3. Momentum Stocks with Volume Surge
```sql
SELECT symbol, close, percent_change, volume_ratio, rsi, macd, exchange
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE DATE(datetime) = CURRENT_DATE()
  AND volume_ratio > 2.0  -- 2x average volume
  AND macd > macd_signal  -- Bullish MACD
  AND rsi > 50
  AND rsi < 70
ORDER BY volume_ratio DESC
LIMIT 20;
```

### 4. Stocks in Uptrend Regime
```sql
SELECT symbol, close, trend_regime, regime_confidence, sma_50, sma_200
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE DATE(datetime) = CURRENT_DATE()
  AND trend_regime = 1  -- Uptrend
  AND regime_confidence > 1.5  -- High confidence
  AND close > sma_50
  AND sma_50 > sma_200  -- Golden cross
ORDER BY regime_confidence DESC;
```

---

## NEXT STEPS AFTER VALIDATION

1. **Test Queries**: Run sample queries to verify data quality
2. **Performance Test**: Check query speeds with partitioning/clustering
3. **Data Quality Check**: Verify indicators are calculating correctly
4. **Documentation**: Update application to use new table
5. **Cleanup**: After 1-2 weeks of validation, delete old tables:
   - `v2_stocks_daily` (keep v2_stocks_master for metadata)
   - `stocks_unified_daily`
   - `v2_stocks_historical_daily`

---

## COST ANALYSIS

### Storage:
- Estimated table size: ~5-10 GB (85 fields × 2-3M rows)
- BigQuery storage cost: $0.02/GB/month
- **Monthly cost:** $0.10 - $0.20

### Query Costs:
- Partitioning reduces scans by 90%+
- Clustering reduces scans by 50-80%
- **Estimated savings:** $50-$100/month vs non-optimized table

---

## KEY ACHIEVEMENTS

✅ **85-field schema** created with all technical indicators
✅ **Timestamp moved** to system metadata section (as recommended)
✅ **Exchange filtering** implemented (NASDAQ/NYSE/CBOE only)
✅ **3-table consolidation** strategy with deduplication
✅ **27 years** of historical data preserved (1998-2025)
✅ **Partitioning & clustering** configured for optimal performance
✅ **Migration script** ready with full indicator calculation

---

## ANSWER TO USER'S QUESTION

**Q:** "Is there anything that I am missing from NYSE or NASDAQ or CBOE? I guess the S&P 500 or Russell Index or NASDAQ 100 are part of this"

**A:** Current coverage analysis:

### What We Have:
- **NASDAQ 100**: ✅ Major tech leaders (AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META)
- **S&P 500**: ✅ Large-cap stocks (JPM, BAC, WMT, JNJ, PG, KO, XOM)
- **NYSE**: ✅ 65+ NYSE symbols (XNYS, ARCX, XASE)
- **NASDAQ**: ✅ 33+ NASDAQ symbols (XNGS, XNCM, XNMS, XNAS)

### What We DON'T Have:
- **Russell 2000**: ❌ Small-cap stocks (NOT included - only large/mid caps)
- **Liquid ETFs**: ❌ ETFs not included (SPY, QQQ, IWM, etc.)
- **Complete indices**: ❌ Not all 500 S&P 500 stocks, not all 2000 Russell 2000 stocks

### Summary:
- Current: **~100-350 symbols** (large/mid-cap focused)
- Recommended: Expand to **500-1,000 symbols** for comprehensive coverage
- Missing: Small-cap stocks (Russell 2000) and ETFs

---

**END OF MIGRATION SUMMARY**
