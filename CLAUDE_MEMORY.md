# Claude Memory - AI Trading Application Project

## Project Overview
- **Project Name**: AI Trading Application (AIAlgoTradeHits.com)
- **GCP Project ID**: cryptobot-462709
- **BigQuery Dataset**: crypto_trading_data
- **Main Directory**: `C:\Users\irfan\OneDrive - Aretec, Inc\Desktop\1AITrading\Trading`
- **Technology Stack**: React + Vite (Frontend), Flask (Backend), BigQuery (Database), Cloud Run (Hosting)

## Production URLs
- **Frontend Application**: https://crypto-trading-app-252370699783.us-central1.run.app
- **API Backend**: https://trading-api-252370699783.us-central1.run.app
- **API Base URL (Production)**: https://trading-api-252370699783.us-central1.run.app/api
- **API Base URL (Local)**: http://localhost:8080/api

## Test Data Configuration
- **Stock Symbol**: NVDA only
- **Crypto Symbol**: BTC/USD only
- **Data Source**: Twelve Data API (https://twelvedata.com)
- **Twelve Data API Key**: 16ee060fd4d34a628a14bcb6f0167565

## Data Schema (71 Technical Indicators)
**Source**: Twelve Data API format (NOT Kraken format)

**Indicator Categories**:
- Momentum: rsi, macd, macd_signal, macd_hist, stoch_k, stoch_d, williams_r, roc, momentum
- Trend: sma_20, sma_50, sma_200, ema_12, ema_26, ema_50, wma_20, dema_20, tema_20, kama_20, adx, adxr, plus_di, minus_di, aroon_up, aroon_down, aroonosc, trix, dx, sar
- Volatility: bb_upper, bb_middle, bb_lower, atr, natr, stddev
- Volume: obv, ad, adosc, pvo, vwap
- Oscillators: cci, ppo, ultosc, bop, cmo, dpo, stochrsi, apo
- Pattern Recognition: cdl_doji, cdl_hammer, cdl_engulfing, cdl_harami, cdl_morningstar, cdl_3blackcrows, cdl_2crows, cdl_3inside, cdl_3linestrike, cdl_abandonedbaby
- Statistical: correl, linearreg, linearreg_slope, linearreg_angle, tsf, variance, beta
- Advanced: ht_dcperiod, ht_dcphase, ht_trendmode, midpoint, midprice, ht_sine_lead

## BigQuery Table Structure

### Stock Tables
- `stocks_daily` - Daily OHLC + 71 indicators
- `stocks_hourly` - Hourly OHLC + 71 indicators
- `stocks_5min` - 5-minute OHLC + 71 indicators

### Crypto Tables
- `crypto_analysis` - Daily OHLC + 71 indicators
- `crypto_hourly_data` - Hourly OHLC + 71 indicators
- `crypto_5min_top10_gainers` - 5-minute OHLC + 71 indicators

**IMPORTANT**: Old table name was `crypto_daily`, now it's `crypto_analysis`

## Current Test Data Counts
- NVDA Daily: 400 records
- NVDA Hourly: 1,000 records
- NVDA 5-minute: 1,000 records
- BTC/USD Daily: 200 records
- BTC/USD Hourly: 500 records
- BTC/USD 5-minute: 500 records

## Common Commands

### Local Development
```bash
# Start API Server (port 8080)
python local_api_server.py

# Start Frontend Dev Server (port 5173 or 5174)
cd stock-price-app
npm run dev

# Fetch Fresh Data from Twelve Data
python fetch_fresh_twelvedata.py

# Verify Data in BigQuery
python verify_fresh_data.py

# Check BigQuery Table Counts
python check_bigquery_counts.py

# Check Stock Tables
python check_stock_tables.py
```

### Deployment Commands
```bash
# Deploy API Backend to Cloud Run
cd cloud_function_api
gcloud run deploy trading-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project cryptobot-462709

# Deploy Frontend to Cloud Run
cd stock-price-app
gcloud run deploy crypto-trading-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project cryptobot-462709
```

### Data Management
```bash
# Clear All BigQuery Tables
python clear_all_tables.py

# Recreate Crypto Tables with New Schema
python recreate_crypto_tables.py

# Load Fresh Test Data
python fetch_fresh_twelvedata.py
```

## Key Files and Locations

### Backend API
- **Local API**: `local_api_server.py`
- **Cloud API**: `cloud_function_api/main.py`
- **Requirements**: `cloud_function_api/requirements.txt`
- **Dockerfile**: `cloud_function_api/Dockerfile`

### Frontend
- **Main App**: `stock-price-app/src/App.jsx`
- **Dashboard**: `stock-price-app/src/components/TradingDashboard.jsx`
- **Charts**: `stock-price-app/src/components/TradingViewChart.jsx`
- **Multi-Panel**: `stock-price-app/src/components/MultiPanelChart.jsx`
- **Market Data Service**: `stock-price-app/src/services/marketData.js`
- **API Service**: `stock-price-app/src/services/api.js`

### Data Fetchers
- **Twelve Data Fetcher**: `fetch_fresh_twelvedata.py`
- **Stock Fetcher (6 months)**: `stock_data_fetcher_6months.py`
- **Kraken Data Fetcher**: `kraken_data_fetcher.py`

### Utilities
- **Verify Fresh Data**: `verify_fresh_data.py`
- **Check BigQuery Counts**: `check_bigquery_counts.py`
- **Check Stock Tables**: `check_stock_tables.py`
- **Check Table Schema**: `check_table_schema.py`
- **Clear All Tables**: `clear_all_tables.py`
- **Recreate Crypto Tables**: `recreate_crypto_tables.py`

## Recent Issues Fixed (November 2024)

### 1. Chart Width Issue
- **Problem**: Charts expanded to twice their size when data loaded
- **Solution**: Added `maxWidth: '100%'` and `overflow: 'hidden'` to chart containers, removed 100px subtraction from width calculations
- **Files**: `TradingViewChart.jsx`, `MultiPanelChart.jsx`

### 2. Duplicate Timestamp Error
- **Problem**: `Assertion failed: data must be asc ordered by time, index=1, time=1759449600, prev time=1759449600`
- **Root Cause**: BigQuery had duplicate records
- **Solution**:
  - Frontend: Added deduplication in `marketData.js` using Set to track timestamps
  - Backend: Cleaned tables using ROW_NUMBER() OVER (PARTITION BY)
- **Files**: `stock-price-app/src/services/marketData.js`

### 3. Marker Sorting Error
- **Problem**: `Assertion failed: data must be asc ordered by time` for markers
- **Solution**: Sort markers array before calling `setMarkers()`
- **Files**: `TradingViewChart.jsx` lines 877-880

### 4. Wrong Table Name for Crypto
- **Problem**: API querying `crypto_daily` but table was renamed to `crypto_analysis`
- **Solution**: Updated API endpoints to use correct table name
- **Files**: `local_api_server.py` line 395, `cloud_function_api/main.py` line 395

### 5. Schema Mismatch
- **Problem**: Old crypto tables had Kraken schema (~30 fields), new data has Twelve Data schema (71 indicators)
- **Solution**: Deleted old crypto tables and recreated with Twelve Data schema
- **Files**: `recreate_crypto_tables.py`, `fetch_fresh_twelvedata.py`

### 6. Missing Volume Field for Crypto
- **Problem**: Twelve Data API doesn't return volume for crypto, causing KeyError
- **Solution**: Added conditional check for volume field, default to 0 if missing
- **Files**: `fetch_fresh_twelvedata.py` lines 415-419

### 7. Date Field Type Issue
- **Problem**: pandas.date type doesn't convert well to BigQuery DATE
- **Solution**: Convert date to string: `df['date'] = df['datetime'].dt.date.astype(str)`
- **Files**: `fetch_fresh_twelvedata.py` line 440

## Important Implementation Details

### Deduplication Pattern (Frontend)
```javascript
// marketData.js lines 237-251
const sorted = transformed.sort((a, b) => a.time - b.time);
const deduplicated = [];
const seen = new Set();
for (let i = sorted.length - 1; i >= 0; i--) {
  const candle = sorted[i];
  if (!seen.has(candle.time)) {
    seen.add(candle.time);
    deduplicated.unshift(candle);
  }
}
```

### BigQuery Deduplication Pattern
```sql
CREATE OR REPLACE TABLE `cryptobot-462709.crypto_trading_data.stocks_daily` AS
SELECT * EXCEPT(row_num)
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY symbol, datetime ORDER BY datetime DESC) as row_num
  FROM `cryptobot-462709.crypto_trading_data.stocks_daily`
)
WHERE row_num = 1
```

### Chart Library Requirements
- Uses `lightweight-charts` library (TradingView style)
- Requires strictly ascending timestamps (Unix seconds, not milliseconds)
- No duplicate timestamps allowed
- Markers must be sorted before calling `setMarkers()`

### API Endpoints

**Market Summary**:
- GET `/api/summary/stock` - Returns NVDA data
- GET `/api/summary/crypto` - Returns BTC/USD data

**Historical Data**:
- GET `/api/stocks/history?symbol=NVDA&limit=500` - Daily stock data
- GET `/api/stocks/hourly/history?symbol=NVDA&limit=500` - Hourly stock data
- GET `/api/stocks/5min/history?symbol=NVDA&limit=500` - 5-minute stock data
- GET `/api/crypto/daily/history?pair=BTC/USD&limit=500` - Daily crypto data
- GET `/api/crypto/15min/history?pair=BTC/USD&limit=500` - Hourly crypto data
- GET `/api/crypto/5min/history?pair=BTC/USD&limit=500` - 5-minute crypto data

**Note**: Hourly endpoint uses "15min" in URL but actually serves hourly data

## Environment Variables

### Frontend (.env)
```
VITE_API_URL=http://localhost:8080/api  # Development
```

### Production
- Frontend automatically uses Cloud Run API URL when not in dev mode
- API URL: https://trading-api-252370699783.us-central1.run.app/api

## Authentication
- Login system exists but not used in test deployment
- Tables are publicly accessible via API for testing
- Admin panel available but not actively used

## Known Limitations
- Only NVDA stock data available (no other stocks)
- Only BTC/USD crypto data available (no other cryptos)
- Volume data for crypto defaults to 0 (not provided by Twelve Data)
- SSL certificate warnings when using curl (use -k flag)

## Next Steps / Future Enhancements
- Add more stock symbols (per US_STOCK_IMPLEMENTATION_PLAN.md)
- Add more crypto pairs
- Implement automated data refresh via Cloud Functions
- Add real-time data streaming
- Implement backtesting features
- Add AI pattern recognition
- Add trading signals based on indicators

## Troubleshooting

### Charts Not Displaying
1. Check browser console for errors
2. Verify API is returning data: `curl http://localhost:8080/api/summary/crypto`
3. Check for duplicate timestamps in logs
4. Verify BigQuery tables have data: `python verify_fresh_data.py`

### API Errors
1. Check if BigQuery tables exist and have correct schema
2. Verify table names: `crypto_analysis` not `crypto_daily`
3. Check API logs in Cloud Run console
4. Test endpoints locally first

### Deployment Issues
1. Ensure gcloud CLI is authenticated: `gcloud auth list`
2. Check project is set: `gcloud config get-value project`
3. Verify Dockerfile exists in deployment directory
4. Check Cloud Run logs for errors

## Project Documentation Files
- CLAUDE.md - Project overview and architecture
- QUICK_START_GUIDE.md - Getting started instructions
- DEPLOYMENT_COMPLETE.md - Deployment status
- COMPLETE_PROJECT_STATUS.md - Overall project status
- US_STOCK_IMPLEMENTATION_PLAN.md - Plan for adding US stocks
- STOCK_DATA_SOURCE_RECOMMENDATION.md - Data source analysis

---

**Last Updated**: November 21, 2024
**Current Status**: Production deployment complete with fresh test data (NVDA + BTC/USD)
**Cloud Run Revision**: trading-api-00026-8rg, crypto-trading-app-00057-gtz
