# Multi-Timeframe Stock Indicator System - Implementation Plan

**Date:** December 9, 2025
**Status:** Daily calculation in progress (fixing upload issue)
**Goal:** Create 3 clean tables with indicators: Daily, Hourly, 5-Minute

---

## CURRENT STATUS

### Daily Table (stocks_daily_clean) - IN PROGRESS
- **Data:** 1,141,844 rows, 262 symbols, 27 years (1998-2025)
- **Status:** Indicator calculation hitting BigQuery upload error
- **Issue:** INT64 fields getting float values during calculation
- **Fix:** Only upload indicator fields, not base OHLCV fields
- **ETA:** Will restart once fixed (~2 hours to complete)

### Hourly Table (stocks_hourly_clean) - READY TO CREATE
- **Source:** `v2_stocks_hourly`
- **Data:** 486,915 rows, 60 symbols, 4 months
- **Capacity:** Can process all 60 stocks in 46 minutes
- **Strategy:** Run every hour during market hours (9 AM - 4 PM)

### 5-Minute Table (stocks_5min_clean) - READY TO CREATE
- **Source:** `v2_stocks_5min`
- **Data:** 1,976,497 rows, 60 symbols, 1 month
- **Capacity:** Can process 10 stocks in 31 minutes
- **Strategy:** Top 10 liquid stocks every 15-30 minutes

---

## IMPLEMENTATION PLAN

### Phase 1: Fix & Complete Daily (TODAY)
1. ✅ Diagnose issue: Int64 upload error for base fields
2. ⏳ Fix script: Only upload indicator fields to BigQuery
3. ⏳ Test on single symbol
4. ⏳ Run full calculation (262 symbols, ~2 hours)
5. ⏳ Validate results

### Phase 2: Create Hourly System (TODAY/TOMORROW)
1. Create `stocks_hourly_clean` table with 85-field schema
2. Migrate existing hourly data from `v2_stocks_hourly`
3. Create calculation script (adapted from daily)
4. Test on single symbol
5. Run full calculation (60 stocks, ~46 minutes)
6. Create Cloud Function for automated updates
7. Set up Cloud Scheduler: `0 9-16 * * 1-5`

### Phase 3: Create 5-Minute System (TOMORROW)
1. Create `stocks_5min_clean` table with 85-field schema
2. Migrate existing 5-min data from `v2_stocks_5min`
3. Create calculation script (adapted from daily)
4. Test on single symbol
5. Define top 10 liquid stocks list
6. Run calculation for top 10 (31 minutes)
7. Create Cloud Function for automated updates
8. Set up Cloud Scheduler: `*/15 9-16 * * 1-5` or `*/30 9-16 * * 1-5`

### Phase 4: Weekly/Monthly/Quarterly Reports (FUTURE)
- Aggregate from daily data (no separate tables needed)
- Create SQL views or reporting functions
- Examples:
  - Weekly: `GROUP BY EXTRACT(WEEK FROM datetime), EXTRACT(YEAR FROM datetime)`
  - Monthly: `GROUP BY EXTRACT(MONTH FROM datetime), EXTRACT(YEAR FROM datetime)`
  - Quarterly: `GROUP BY EXTRACT(QUARTER FROM datetime), EXTRACT(YEAR FROM datetime)`

---

## ARCHITECTURE DESIGN

### Table Structure (All 3 timeframes)

```
Project: aialgotradehits
Dataset: crypto_trading_data

Tables:
1. stocks_daily_clean    (262 symbols, 27 years, 85 fields)
2. stocks_hourly_clean   (60 symbols, 4 months, 85 fields)
3. stocks_5min_clean     (10-60 symbols, 1 month, 85 fields)
```

All tables share identical 85-field schema:
- **27 Base Fields:** OHLCV, metadata
- **58 Indicator Fields:** Technical indicators + ML features

### Partitioning Strategy

**Daily:**
- Partition: MONTH (datetime)
- Cluster: symbol, sector, exchange
- Reason: 27 years = 324 months (within 4000 limit)

**Hourly:**
- Partition: DAY (datetime)
- Cluster: symbol, sector, exchange
- Reason: 4 months = ~120 days (well within limit)

**5-Minute:**
- Partition: DAY (datetime)
- Cluster: symbol, sector, exchange
- Reason: 1 month = ~30 days (well within limit)

---

## PROCESSING CAPACITY & SCHEDULING

### Daily Processing
- **Symbols:** 262
- **Time per symbol:** ~25 seconds (avg 4,360 rows)
- **Total time:** ~109 minutes (1.8 hours)
- **Schedule:** Once daily after market close
- **Scheduler:** `0 17 * * 1-5` (5 PM ET weekdays)
- **Completion:** By 6:50 PM

### Hourly Processing
- **Symbols:** 60
- **Time per symbol:** ~46 seconds (avg 8,115 rows)
- **Total time:** ~46 minutes
- **Schedule:** Every hour during market hours
- **Scheduler:** `0 9-16 * * 1-5` (9 AM - 4 PM ET weekdays)
- **Runs per day:** 8 times (9 AM, 10 AM, ... 4 PM)

### 5-Minute Processing - OPTION A (Top 10 Focus)
- **Symbols:** 10 (most liquid)
- **Top 10:** AAPL, MSFT, NVDA, TSLA, AMZN, GOOGL, META, SPY, QQQ, AMD
- **Time per symbol:** ~3.1 minutes (avg 32,941 rows)
- **Total time:** ~31 minutes
- **Schedule:** Every 30 minutes during market hours
- **Scheduler:** `*/30 9-16 * * 1-5` (every 30 min, 9 AM - 4 PM)
- **Runs per day:** 15 times

### 5-Minute Processing - OPTION B (Rolling All 60)
- **Symbols:** 60 (divided into 4 batches of 15)
- **Batch 1:** Minutes 0, 15, 30, 45
- **Batch 2:** Minutes 5, 20, 35, 50
- **Batch 3:** Minutes 10, 25, 40, 55
- **Batch 4:** Minutes 7, 22, 37, 52
- **Each stock updated:** Every ~1 hour
- **Schedulers:** 4 separate Cloud Schedulers

**Recommendation:** Start with Option A (Top 10), expand to Option B if needed.

---

## CLOUD FUNCTION ARCHITECTURE

### Function 1: Daily Indicator Calculator
```
Name: stocks-daily-indicator-calculator
Runtime: Python 3.13
Memory: 2GB
Timeout: 10 minutes
Trigger: Cloud Scheduler (HTTP)
Schedule: 0 17 * * 1-5
Description: Calculate indicators for all 262 stocks daily
```

### Function 2: Hourly Indicator Calculator
```
Name: stocks-hourly-indicator-calculator
Runtime: Python 3.13
Memory: 2GB
Timeout: 10 minutes
Trigger: Cloud Scheduler (HTTP)
Schedule: 0 9-16 * * 1-5
Description: Calculate indicators for all 60 stocks hourly
```

### Function 3: 5-Minute Indicator Calculator (Top 10)
```
Name: stocks-5min-indicator-calculator
Runtime: Python 3.13
Memory: 2GB
Timeout: 10 minutes
Trigger: Cloud Scheduler (HTTP)
Schedule: */30 9-16 * * 1-5
Description: Calculate indicators for top 10 liquid stocks
```

---

## DATA FLOW

### Daily Data Flow
```
v2_stocks_daily (262 symbols, raw)
    ↓ [One-time migration]
stocks_daily_clean (262 symbols, with indicators)
    ↓ [Daily updates]
Cloud Function (calculate new indicators)
    ↓ [MERGE INTO]
stocks_daily_clean (updated with latest day)
```

### Hourly Data Flow
```
v2_stocks_hourly (60 symbols, raw)
    ↓ [One-time migration]
stocks_hourly_clean (60 symbols, with indicators)
    ↓ [Hourly updates]
Cloud Function (calculate latest hour indicators)
    ↓ [MERGE INTO]
stocks_hourly_clean (updated with latest hour)
```

### 5-Minute Data Flow
```
v2_stocks_5min (60 symbols, raw)
    ↓ [One-time migration]
stocks_5min_clean (10-60 symbols, with indicators)
    ↓ [Every 15-30 min]
Cloud Function (calculate latest 5-min indicators)
    ↓ [MERGE INTO]
stocks_5min_clean (updated with latest 5-min bar)
```

---

## API ENDPOINTS (FUTURE)

### Daily Endpoints
- `GET /api/stocks/daily/{symbol}` - Get daily data with indicators
- `GET /api/stocks/daily/{symbol}/latest` - Get latest day
- `GET /api/stocks/daily/screener` - Screen stocks by indicator criteria

### Hourly Endpoints
- `GET /api/stocks/hourly/{symbol}` - Get hourly data with indicators
- `GET /api/stocks/hourly/{symbol}/latest` - Get latest hour
- `GET /api/stocks/hourly/top-movers` - Get most active hourly

### 5-Minute Endpoints
- `GET /api/stocks/5min/{symbol}` - Get 5-min data with indicators
- `GET /api/stocks/5min/{symbol}/latest` - Get latest 5-min bar
- `GET /api/stocks/5min/real-time` - Get real-time top 10 with indicators

### Aggregation Endpoints
- `GET /api/stocks/weekly/{symbol}` - Aggregated weekly from daily
- `GET /api/stocks/monthly/{symbol}` - Aggregated monthly from daily
- `GET /api/stocks/quarterly/{symbol}` - Aggregated quarterly from daily

---

## COST ESTIMATION

### BigQuery Storage
- Daily: 1.14M rows × 85 fields × 8 bytes = ~773 MB = $0.02/month
- Hourly: 487K rows × 85 fields × 8 bytes = ~331 MB = $0.01/month
- 5-Minute: 1.98M rows × 85 fields × 8 bytes = ~1.35 GB = $0.03/month
- **Total Storage:** $0.06/month

### Cloud Functions
- Daily: 1 run/day × 120 min × 2GB = $0.01/day = $0.30/month
- Hourly: 8 runs/day × 46 min × 2GB = $0.20/day = $6/month
- 5-Minute: 15 runs/day × 31 min × 2GB = $0.93/day = $28/month
- **Total Functions:** $34.30/month

### Cloud Scheduler
- 3 schedulers × $0.10/month = $0.30/month

### Total Estimated Cost
**$34.66/month** for complete multi-timeframe indicator system

---

## PERFORMANCE METRICS

### Calculation Speed
- Daily: 25 seconds/symbol (~220 rows/second)
- Hourly: 46 seconds/symbol (~176 rows/second)
- 5-Minute: 188 seconds/symbol (~175 rows/second)

### Latency (Time to Fresh Indicators)
- Daily: Updated once per day (5-7 PM)
- Hourly: Updated every hour (within 46 minutes)
- 5-Minute (Top 10): Updated every 30 minutes (within 31 minutes)

### Data Freshness
- Daily: Same day close data available by 7 PM
- Hourly: Current hour data available by end of next hour
- 5-Minute (Top 10): Updated 15 times per day

---

## MONITORING & ALERTS

### Success Criteria
- **Daily:** All 262 symbols processed, >99% indicator coverage
- **Hourly:** All 60 symbols processed, >99% indicator coverage
- **5-Minute:** Top 10 symbols processed, >99% indicator coverage

### Monitoring Metrics
- Execution time per function
- Success/failure rate per symbol
- Indicator coverage percentage
- BigQuery query costs
- Function invocation costs

### Alerting (Future)
- Email alert if function fails
- Slack notification on completion
- Dashboard showing latest run status

---

## NEXT STEPS

### Immediate (Today)
1. Fix daily calculation BigQuery upload issue
2. Complete daily indicator calculation (262 symbols)
3. Validate daily results
4. Create documentation

### Tomorrow
1. Create hourly table and calculation script
2. Run hourly calculation (60 symbols)
3. Create 5-minute table and calculation script
4. Run 5-minute calculation (10 symbols)

### This Week
1. Deploy all 3 Cloud Functions
2. Set up all 3 Cloud Schedulers
3. Test automated updates
4. Update frontend to use new tables

### Future Enhancements
1. Add more stocks to 5-minute (expand from 10 to 60)
2. Create aggregation views (weekly, monthly, quarterly)
3. Add API endpoints for all timeframes
4. Implement real-time WebSocket updates
5. Add ML model predictions using indicators

---

## FILES CREATED

1. `TECHNICAL_INDICATORS_COMPLETE_REFERENCE.md` - Complete indicator formulas
2. `MORNING_STATUS_REPORT_DEC9.md` - Morning progress report
3. `MULTI_TIMEFRAME_IMPLEMENTATION_PLAN.md` - This document
4. `calculate_all_indicators_FIXED.py` - Daily calculation script (fixing)
5. (To create) `calculate_hourly_indicators.py` - Hourly calculation script
6. (To create) `calculate_5min_indicators.py` - 5-minute calculation script

---

**Status:** Day 1 of multi-timeframe implementation
**Progress:** Daily table 50% complete (schema done, calculation fixing)
**Next:** Complete daily, then build hourly and 5-minute systems

---

**END OF IMPLEMENTATION PLAN**
