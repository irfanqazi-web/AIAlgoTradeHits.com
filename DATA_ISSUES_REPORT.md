# Data Issues Report
**Generated:** 2025-11-18 02:06 UTC
**Project:** cryptobot-462709
**Dataset:** crypto_trading_data

---

## Executive Summary

**Status:** ⚠️ **CRITICAL DATA ISSUES FOUND**

- ✅ **1 of 6 tables** collecting data actively (crypto 5-min)
- ⚠️ **2 of 6 tables** have stale data (crypto/stock daily and hourly)
- ❌ **3 of 6 tables** are completely empty (stock hourly and 5-min)

**Root Cause:** Schedulers may be failing OR data source APIs have issues

---

## Detailed Status by Table

### 1. crypto_analysis (Daily) ⚠️ **STALE**
- **Records:** 196,231
- **Symbols:** 678 crypto pairs
- **Latest Data:** 2025-11-09 (9 days old)
- **Issue:** No data collected in last 7 days
- **Scheduler:** `daily-crypto-fetch-job` (0 0 * * *) - May be failing

### 2. crypto_hourly_data ⚠️ **STALE**
- **Records:** 5,244
- **Symbols:** 685 crypto pairs
- **Latest Data:** 2025-11-15 06:00 (2.8 days old)
- **Recent Activity:**
  - Nov 15: 497 records
  - Nov 14: 1,704 records
  - Nov 13: 1,598 records
- **Issue:** Stopped collecting after Nov 15
- **Scheduler:** `hourly-crypto-fetch-job` (0 * * * *) - May be failing

### 3. crypto_5min_top10_gainers ✅ **ACTIVE**
- **Records:** 34,636
- **Symbols:** 71 pairs
- **Latest Data:** 2025-11-18 02:05 (1 minute ago!)
- **Status:** ✅ Working perfectly
- **Scheduler:** `fivemin-top10-fetch-job` (*/5 * * * *) - Working

### 4. stock_analysis (Daily) ⚠️ **STALE**
- **Records:** 35,987
- **Symbols:** 97 stocks
- **Latest Data:** 2025-11-07 (11 days old)
- **Issue:** No data in last 7 days
- **Scheduler:** `stock-daily-fetch-job` (0 0 * * *) - May be failing

### 5. stock_hourly_data ❌ **EMPTY**
- **Records:** 0
- **Symbols:** 0
- **Latest Data:** None
- **Issue:** Table never populated OR scheduler never ran
- **Scheduler:** `stock-hourly-fetch-job` (0 * * * *) - Not working

### 6. stock_5min_top10_gainers ❌ **EMPTY**
- **Records:** 0
- **Symbols:** 0
- **Latest Data:** None
- **Issue:** Table never populated OR scheduler never ran
- **Scheduler:** `stock-5min-fetch-job` (*/5 * * * *) - Not working

---

## Issues Identified

### Issue #1: Scheduler Failures
**Affected:** Daily/Hourly for both crypto and stocks

**Possible Causes:**
1. Cloud Function timeout (540s may not be enough for all symbols)
2. API rate limiting from Kraken/stock data source
3. Memory issues (512MB may be insufficient)
4. Network/connectivity problems
5. Authentication failures

**Action:** Check Cloud Function logs for errors

### Issue #2: Stock Data Never Initialized
**Affected:** stock_hourly_data, stock_5min_top10_gainers

**Possible Causes:**
1. Cloud Functions never successfully ran
2. No stock data source configured (need Massive.com?)
3. Functions deployed but pointing to wrong tables
4. API credentials missing/expired

**Action:** Verify stock data source and credentials

### Issue #3: Data Source Reliability
**Observation:** Only 5-min crypto collecting consistently

**Possible Causes:**
1. Free tier API limits hit for daily/hourly
2. Kraken API changed/deprecated endpoints
3. Different data sources for different timeframes

**Action:** Consider Massive.com for reliable feeds

---

## Immediate Actions Required

### Before Migration:

#### 1. Check Cloud Function Logs (PRIORITY)
```bash
# Check for errors in each function
gcloud functions logs read daily-crypto-fetcher --limit=50
gcloud functions logs read hourly-crypto-fetcher --limit=50
gcloud functions logs read stock-daily-fetcher --limit=50
gcloud functions logs read stock-hourly-fetcher --limit=50
gcloud functions logs read stock-5min-fetcher --limit=50
```

#### 2. Manually Trigger Functions
```bash
# Test if functions work when triggered manually
gcloud scheduler jobs run daily-crypto-fetch-job
gcloud scheduler jobs run stock-daily-fetch-job
# Wait 2-3 minutes, then check logs and tables
```

#### 3. Verify Stock Data Source
- Check if stock API credentials are configured
- Verify stock data source is accessible
- May need Massive.com subscription for stocks

---

## Migration Plan (Adjusted)

### Option A: Migrate Now (Accept Data Gaps)
**Pros:**
- Get clean table structure in place
- Fix Smart Search immediately
- Can backfill data later

**Cons:**
- Will still have data gaps until source fixed
- May waste time if functions still failing

### Option B: Fix Data First, Then Migrate (RECOMMENDED)
**Pros:**
- Verify schedulers working before migration
- Ensure clean data flowing
- Migration happens with confidence

**Cons:**
- Smart Search won't work until migration complete
- Takes more time

---

## Recommendations

### Immediate (Next 1 Hour):
1. ✅ Check Cloud Function logs for all 6 functions
2. ✅ Identify which functions are failing and why
3. ✅ Fix function errors (timeout, memory, API issues)
4. ✅ Manually trigger all functions to test

### Short Term (Today):
1. Get at least crypto daily/hourly working again
2. Investigate stock data source requirements
3. Consider Massive.com trial for stock data
4. Once 1-2 functions collecting data → Proceed with migration

### Long Term (This Week):
1. Subscribe to Massive.com for reliable data feeds
2. Complete table migration
3. Set up monitoring/alerts for data staleness
4. Backfill any missing historical data

---

## Data for Smart Search (Current State)

**What Works Now:**
- ✅ Crypto 5-min queries (fresh data)
- ⚠️ Crypto hourly queries (2.8 days old - acceptable for testing)

**What Doesn't Work:**
- ❌ Crypto daily queries (9 days old - too stale)
- ❌ Stock daily queries (11 days old - too stale)
- ❌ Stock hourly queries (no data)
- ❌ Stock 5-min queries (no data)

**Impact on Smart Search:**
- "Netflix", "Tesla" → 0 results (stock tables stale/empty)
- "Bitcoin" → 0 results for daily (stale), OK for hourly/5-min
- "5 minute top gainers crypto" → Works!
- "daily oversold stocks" → 0 results (stale data)

---

## Next Steps - Your Decision

**Path A: Investigate & Fix Data Collection First**
1. I check all Cloud Function logs
2. Identify and fix failing functions
3. Verify data flowing again
4. Then proceed with migration

**Path B: Migrate Tables Now, Fix Data Later**
1. Create new tables with correct names
2. Update all code to use new names
3. Deploy everything
4. Then troubleshoot data collection

**Which path do you prefer?**
- Say "Path A" to fix data first
- Say "Path B" to migrate now and fix data after

I recommend **Path A** - let's get the data pipelines healthy before migrating.
