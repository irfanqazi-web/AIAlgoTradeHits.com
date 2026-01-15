# Table Renaming & Reorganization Strategy

## Current State Assessment

### Existing Tables (10 total)
**Raw Data Tables (6):**
1. `crypto_analysis` → Should be `daily_crypto`
2. `crypto_hourly_data` → Should be `hourly_crypto`
3. `crypto_5min_top10_gainers` → Should be `5min_crypto`
4. `stock_analysis` → Should be `daily_stock`
5. `stock_hourly_data` → Should be `hourly_stock`
6. `stock_5min_top10_gainers` → Should be `5min_stock`

**System Tables (4):**
7. `users` - User accounts (keep as-is)
8. `search_history` - NLP search logs (keep as-is)
9. `user_trades` - Trade tracking (keep as-is)
10. `trading_sessions` - Session tracking (keep as-is)

### Cloud Functions (6)
1. `daily-crypto-fetcher` → Writes to `crypto_analysis`
2. `hourly-crypto-fetcher` → Writes to `crypto_hourly_data`
3. `fivemin-top10-fetcher` → Writes to `crypto_5min_top10_gainers`
4. `stock-daily-fetcher` → Writes to `stock_analysis`
5. `stock-hourly-fetcher` → Writes to `stock_hourly_data`
6. `stock-5min-fetcher` → Writes to `stock_5min_top10_gainers`

### Cloud Schedulers (6)
1. `daily-crypto-fetch-job` → Triggers daily-crypto-fetcher (0 0 * * *)
2. `hourly-crypto-fetch-job` → Triggers hourly-crypto-fetcher (0 * * * *)
3. `fivemin-top10-fetch-job` → Triggers fivemin-top10-fetcher (*/5 * * * *)
4. `stock-daily-fetch-job` → Triggers stock-daily-fetcher (0 0 * * *)
5. `stock-hourly-fetch-job` → Triggers stock-hourly-fetcher (0 * * * *)
6. `stock-5min-fetch-job` → Triggers stock-5min-fetcher (*/5 * * * *)

---

## Proposed Architecture

### Phase 1: Raw Data Tables (Rename existing)
Store OHLC + basic indicators from data sources.

**Naming Convention:** `{timeframe}_{market}`

1. `daily_crypto` - Daily OHLC for all crypto pairs
2. `hourly_crypto` - Hourly OHLC for all crypto pairs
3. `5min_crypto` - 5-minute OHLC for top gainers
4. `daily_stock` - Daily OHLC for all stocks
5. `hourly_stock` - Hourly OHLC for all stocks
6. `5min_stock` - 5-minute OHLC for top gainers

**Fields:** symbol/pair, datetime, open, high, low, close, volume, basic indicators (RSI, MACD, ADX, ROC, SMAs)

### Phase 2: Analysis Tables (Create new - Future)
Derived tables with advanced analysis and patterns.

**Naming Convention:** `{timeframe}_{market}_analysis`

1. `daily_crypto_analysis` - Advanced analysis on daily crypto
2. `hourly_crypto_analysis` - Advanced analysis on hourly crypto
3. `5min_crypto_analysis` - Advanced analysis on 5-min crypto
4. `daily_stock_analysis` - Advanced analysis on daily stocks
5. `hourly_stock_analysis` - Advanced analysis on hourly stocks
6. `5min_stock_analysis` - Advanced analysis on 5-min stocks

**Additional Fields (Future):**
- Elliott Wave patterns
- Fibonacci levels
- Support/Resistance zones
- Chart patterns (head & shoulders, triangles, etc.)
- Supply/Demand zones
- AI predictions
- Sentiment scores

---

## Implementation Plan

### Step 1: Create New Tables with Correct Names
```sql
-- Copy existing tables to new names
CREATE TABLE `cryptobot-462709.crypto_trading_data.daily_crypto`
AS SELECT * FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`;

CREATE TABLE `cryptobot-462709.crypto_trading_data.hourly_crypto`
AS SELECT * FROM `cryptobot-462709.crypto_trading_data.crypto_hourly_data`;

CREATE TABLE `cryptobot-462709.crypto_trading_data.5min_crypto`
AS SELECT * FROM `cryptobot-462709.crypto_trading_data.crypto_5min_top10_gainers`;

CREATE TABLE `cryptobot-462709.crypto_trading_data.daily_stock`
AS SELECT * FROM `cryptobot-462709.crypto_trading_data.stock_analysis`;

CREATE TABLE `cryptobot-462709.crypto_trading_data.hourly_stock`
AS SELECT * FROM `cryptobot-462709.crypto_trading_data.stock_hourly_data`;

CREATE TABLE `cryptobot-462709.crypto_trading_data.5min_stock`
AS SELECT * FROM `cryptobot-462709.crypto_trading_data.stock_5min_top10_gainers`;
```

### Step 2: Update Cloud Functions
Update table references in all 6 Cloud Functions:

**Files to modify:**
- `cloud_function_daily/main.py` → Change `crypto_analysis` to `daily_crypto`
- `cloud_function_hourly/main.py` → Change `crypto_hourly_data` to `hourly_crypto`
- `cloud_function_5min/main.py` → Change `crypto_5min_top10_gainers` to `5min_crypto`
- `cloud_function_daily_stocks/main.py` → Change `stock_analysis` to `daily_stock`
- `cloud_function_stocks_hourly/main.py` → Change `stock_hourly_data` to `hourly_stock`
- `cloud_function_stocks_5min/main.py` → Change `stock_5min_top10_gainers` to `5min_stock`

### Step 3: Update NLP Query Engine
Update `cloud_function_api/nlp_query_engine.py`:

```python
def _select_table(self, market_type, timeframe):
    """Select appropriate table"""
    # NEW naming convention: {timeframe}_{market}
    table_name = f"{timeframe}_{market_type}"
    return f"`{self.project_id}.{self.dataset_id}.{table_name}`"
```

Update timeframe mapping:
```python
self.timeframe_keywords = {
    'hourly': 'hourly',
    'hour': 'hourly',
    '1h': 'hourly',
    'daily': 'daily',
    'day': 'daily',
    '1d': 'daily',
    '5-minute': '5min',
    '5min': '5min',
    '5m': '5min',
    '5 minute': '5min',
}
```

### Step 4: Update Frontend API Service
Update `stock-price-app/src/services/marketData.js` to use new table names.

### Step 5: Deploy All Changes
1. Deploy all 6 Cloud Functions
2. Deploy updated trading-api
3. Verify schedulers are triggering correctly
4. Monitor data ingestion for 1 hour

### Step 6: Verify Data Flow
1. Check all 6 tables have recent data
2. Test NLP queries against new tables
3. Verify charts display correctly
4. Test Smart Search functionality

### Step 7: Cleanup (After verification)
Once everything works for 24-48 hours:
```sql
DROP TABLE `cryptobot-462709.crypto_trading_data.crypto_analysis`;
DROP TABLE `cryptobot-462709.crypto_trading_data.crypto_hourly_data`;
DROP TABLE `cryptobot-462709.crypto_trading_data.crypto_5min_top10_gainers`;
DROP TABLE `cryptobot-462709.crypto_trading_data.stock_analysis`;
DROP TABLE `cryptobot-462709.crypto_trading_data.stock_hourly_data`;
DROP TABLE `cryptobot-462709.crypto_trading_data.stock_5min_top10_gainers`;
```

---

## Data Status Check

### Current Data Availability:

**Crypto Tables:**
- `crypto_analysis` (daily): 196,231 records, latest: 2025-11-09 ⚠️ STALE
- `crypto_hourly_data`: 5,244 records, latest: 2025-11-15 06:00 ⚠️ STALE
- `crypto_5min_top10_gainers`: 34,440 records, latest: 2025-11-18 01:30 ✓ ACTIVE

**Stock Tables:**
- `stock_analysis` (daily): 35,987 records, latest: TBD
- `stock_hourly_data`: Active
- `stock_5min_top10_gainers`: Active

**Issue:** Daily and hourly crypto schedulers may not be running. Need to verify.

---

## Rollout Timeline

**Day 1 (Today):**
- ✓ Create strategy document
- Create new tables with correct names
- Update NLP engine
- Deploy trading-api

**Day 1-2:**
- Update all 6 Cloud Functions
- Deploy all functions
- Verify schedulers triggering
- Monitor data ingestion

**Day 2-3:**
- Test Smart Search extensively
- Verify all timeframes working
- Document any data gaps

**Day 4-5:**
- Address data quality issues with Massive.com
- Optimize queries
- Fine-tune indicators

**Week 2+:**
- Design analysis table schemas
- Implement advanced patterns
- Add AI predictions

---

## Risk Mitigation

1. **Data Loss Prevention:** Copy tables before renaming (using CREATE TABLE AS SELECT)
2. **Dual Running:** Keep old tables active during transition period
3. **Rollback Plan:** Can revert NLP engine to old table names if issues arise
4. **Monitoring:** Check data counts every hour during first 24 hours
5. **Backup:** Old tables remain until confirmed new tables working perfectly

---

## Success Criteria

✓ All 6 schedulers running without errors
✓ Data flowing into all 6 new tables
✓ NLP queries returning results
✓ Smart Search working with all combinations:
  - Daily/Hourly/5min × Crypto/Stock × Various filters
✓ Charts displaying correctly for all timeframes
✓ No data gaps or missing records

---

## Next Steps

1. **Approve this strategy**
2. **Execute table creation**
3. **Update and deploy Cloud Functions**
4. **Test Smart Search**
5. **Address data quality with Massive.com subscription**
6. **Design analysis table schemas for Phase 2**
