# Trading App - Current Status & Solution

## Date: December 10, 2025

## CURRENT STATUS

### Data Status

**stocks_daily_clean** ✅
- Rows: 30,560
- Symbols: 106 US stocks
- Latest Data: December 8, 2025
- **STATUS: READY TO USE**

**crypto_daily_clean** ❌
- Rows: 0
- STATUS: EMPTY - No crypto source data available
- **NEEDS: Crypto data pipeline setup**

### Application Status

**Frontend:** https://aialgotradehits-app-6pmz2y7ouq-uc.a.run.app
- Status: DEPLOYED but showing "No data available"
- Issue: Backend API not connected or not deployed

**Backend API:** trading-api (cloud_function_api)
- Status: NOT DEPLOYED or misconfigured
- Issue: Querying old table names (v2_stocks_daily) instead of clean tables

## ROOT CAUSE

The app shows "No data available" because:
1. Backend API is querying wrong table names (`v2_stocks_daily` instead of `stocks_daily_clean`)
2. Backend API may not be deployed at all
3. Frontend is trying to connect to non-existent or misconfigured backend

## SOLUTION - Get Stocks Working NOW

### Step 1: Update Backend API Table References

File: `cloud_function_api/main.py`

Change all table references:
- FROM: `v2_stocks_daily`
- TO: `stocks_daily_clean`

- FROM: `v2_cryptos_daily`
- TO: `crypto_daily_clean`

### Step 2: Deploy Backend API

```bash
cd cloud_function_api

# Deploy to Cloud Run
gcloud run deploy trading-api \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --project aialgotradehits \
    --memory 512Mi \
    --timeout 300
```

### Step 3: Update Frontend API URL

File: `stock-price-app/src/services/marketData.js`

Update BASE_URL to match deployed backend:
```javascript
const BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-XXXXX-uc.a.run.app'  // UPDATE THIS
);
```

### Step 4: Redeploy Frontend

```bash
cd stock-price-app

# Deploy to Cloud Run
gcloud run deploy aialgotradehits-app \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --project aialgotradehits \
    --memory 512Mi
```

## ALTERNATIVE QUICK FIX - Stocks Only

If you want to get stocks working IMMEDIATELY without backend deployment:

### Option A: Embed Stock List in Frontend

Modify TradingDashboard.jsx to query BigQuery directly or load from a static JSON file with the 106 stock symbols.

### Option B: Simple Cloud Function

Create a minimal Cloud Function that:
1. Accepts GET /api/stocks/list
2. Returns list of available stocks from stocks_daily_clean
3. Accepts GET /api/stocks/history?symbol=AAPL
4. Returns OHLC data for that stock

## CRYPTO DATA - TODO

To get crypto data working:

1. **Fetch USD Crypto Pairs**
   - Use Twelve Data API or Kraken API
   - Focus on major pairs: BTCUSD, ETHUSD, SOLUSD, ADAUSD, etc.
   - Historical data: Last 365 days minimum

2. **Calculate Indicators**
   - RSI, MACD, Bollinger Bands, etc.
   - Same indicator set as stocks

3. **Populate crypto_daily_clean**
   - Insert formatted data
   - Ensure schema matches stocks_daily_clean

4. **Update Backend API**
   - Add crypto endpoints
   - Query crypto_daily_clean table

## RECOMMENDATION

**IMMEDIATE ACTION:**
Get stocks working first using Solution above. This gives you a functional app with 106 US stocks and all indicators.

**NEXT PHASE:**
Set up crypto data pipeline (estimated 2-4 hours)

## FILES TO MODIFY

1. `cloud_function_api/main.py` - Update table names
2. `cloud_function_api/deploy_api.py` - Deployment script
3. `stock-price-app/src/services/marketData.js` - API URL
4. Deploy both backend and frontend

## COMMANDS TO RUN

```bash
# 1. Update backend code (manual edit of main.py)
# 2. Deploy backend
cd cloud_function_api
gcloud run deploy trading-api --source . --region us-central1 --allow-unauthenticated --project aialgotradehits

# 3. Get backend URL
gcloud run services describe trading-api --region us-central1 --project aialgotradehits --format="value(status.url)"

# 4. Update frontend with backend URL (manual edit)
# 5. Deploy frontend
cd ../stock-price-app
gcloud run deploy aialgotradehits-app --source . --region us-central1 --allow-unauthenticated --project aialgotradehits

# 6. Get frontend URL and test
gcloud run services describe aialgotradehits-app --region us-central1 --project aialgotradehits --format="value(status.url)"
```

## EXPECTED RESULT

After following the solution:
- ✅ 106 US stocks available in dropdown
- ✅ Daily charts with OHLC data
- ✅ All 29 technical indicators
- ✅ Latest data through December 8, 2025
- ❌ Crypto section empty (to be added in phase 2)

## NEXT SESSION TASKS

1. Fix backend table references
2. Deploy backend API
3. Connect frontend to backend
4. Test with one stock (e.g., AAPL, NVDA)
5. Verify all indicators display
6. Then add crypto data pipeline

---

**Status:** stocks_daily_clean is ready with 30,560 rows of clean data
**Blocker:** Backend API not deployed/configured correctly
**Solution Time:** 15-30 minutes to get stocks working
**Full Solution Time:** 2-4 hours to add cryptos
