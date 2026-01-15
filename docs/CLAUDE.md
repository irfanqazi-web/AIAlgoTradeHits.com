# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **AIAlgoTradeHits.com** AI trading data pipeline that collects, processes, and stores multi-timeframe OHLC data with 24+ technical indicators, Growth Scores, Sentiment Scores, and ML predictions. The system is deployed on Google Cloud Platform (GCP) project `aialgotradehits` and uses TwelveData ($229/month plan = 2M records/day), Kraken, FRED, Finnhub, and CoinMarketCap APIs.

**Primary Reference:** `masterquery.md` v4.0 - Contains all specifications, formulas, and configurations.

## Architecture

### Data Collection Pipeline
Primary Cloud Functions:
- **Bulletproof Fetcher** (`cloud_function_bulletproof/`): Master fetcher for all assets with error tolerance
  - 200+ stocks, 50+ crypto, 40+ ETFs, 20+ forex pairs
  - 24 daily / 12 hourly / 8 5min indicators
  - Growth Score (0-100), Sentiment Score (0.00-1.00)
  - Buy/Sell/Hold recommendations
  - EMA cycle detection, trend regime classification
  - Circuit breaker, retries, dead letter queue
  - URL: `https://bulletproof-fetcher-6pmz2y7ouq-uc.a.run.app`

- **TwelveData Fetcher** (`cloud_function_twelvedata/`): Legacy fetcher with outputsize=5000

### Technical Indicators (Per masterquery.md v4.0)
Daily (24 indicators):
- **Momentum (6):** RSI_14, MACD, MACD_Histogram, ROC, Stoch_K, Stoch_D
- **Trend (10):** SMA_20/50/200, EMA_12/20/26/50/200, Ichimoku_Tenkan/Kijun
- **Volatility (4):** ATR_14, BB_Upper/Middle/Lower
- **Strength (3):** ADX, Plus_DI, Minus_DI
- **Flow (2):** MFI, CMF

### Growth Score Calculation (0-100)
```sql
growth_score =
  CASE WHEN rsi_14 BETWEEN 50 AND 70 THEN 25 ELSE 0 END +  -- RSI sweet spot
  CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +        -- MACD positive
  CASE WHEN adx > 25 THEN 25 ELSE 0 END +                  -- Strong trend
  CASE WHEN close > sma_200 THEN 25 ELSE 0 END             -- Above 200 MA
```

### EMA Cycle Detection
```sql
in_rise_cycle = (ema_12 > ema_26)
rise_cycle_start = (ema_12 > ema_26) AND (LAG(ema_12) <= LAG(ema_26))
fall_cycle_start = (ema_12 < ema_26) AND (LAG(ema_12) >= LAG(ema_26))
```

### Trend Regime Classification
```sql
STRONG_UPTREND: close > sma_50 AND sma_50 > sma_200 AND adx > 25
WEAK_UPTREND: close > sma_50 AND close > sma_200
STRONG_DOWNTREND: close < sma_50 AND sma_50 < sma_200 AND adx > 25
WEAK_DOWNTREND: close < sma_50 AND close < sma_200
CONSOLIDATION: else
```

### BigQuery Schema
**Project:** `aialgotradehits`
**Dataset:** `crypto_trading_data`

Tables:
- `stocks_daily_clean`, `stocks_hourly_clean` - Stock data
- `crypto_daily_clean`, `crypto_hourly_clean` - Crypto data
- `v2_stocks_daily`, `v2_crypto_daily` - Legacy v2 tables

ML Dataset: `aialgotradehits.ml_models`
- `daily_features_24` - 24 indicators per masterquery spec
- `direction_predictor_xgboost` - XGBoost classifier model

### Trading API (Cloud Run)
**Base URL:** `https://trading-api-1075463475276.us-central1.run.app`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ai/trading-signals` | GET | Generate buy/sell signals |
| `/api/ai/rise-cycle-candidates` | GET | EMA crossover detection |
| `/api/ai/ml-predictions` | GET | Growth score predictions |
| `/api/ai/growth-screener` | GET | High growth scanner |
| `/api/ai/text-to-sql` | POST | Natural language queries |

### API Keys (Store securely)
- **TwelveData:** $229/month, 800 calls/min, outputsize=5000
- **Kraken:** Public API for buy/sell volume
- **FRED:** Free, 100/day, economic indicators
- **Finnhub:** Free tier, 60 calls/min
- **CoinMarketCap:** Basic tier

## Common Commands

### Check BigQuery Data
```bash
python check_bigquery_counts.py
python monitor_twelvedata_quota.py  # Monitor 2M/day quota usage
```

### Manually Trigger Cloud Functions
```bash
# Bulletproof fetcher (all assets, hourly)
curl "https://bulletproof-fetcher-6pmz2y7ouq-uc.a.run.app?asset_type=all&interval=1h"

# Bulletproof fetcher (stocks only, daily)
curl "https://bulletproof-fetcher-6pmz2y7ouq-uc.a.run.app?asset_type=stocks&interval=1day"

# With Kraken buy/sell data
curl "https://bulletproof-fetcher-6pmz2y7ouq-uc.a.run.app?asset_type=crypto&interval=1h&include_kraken=true"

# With FRED economic data
curl "https://bulletproof-fetcher-6pmz2y7ouq-uc.a.run.app?interval=1day&include_fred=true"
```

### View Cloud Function Logs
```bash
gcloud functions logs read bulletproof-fetcher --project=aialgotradehits --limit=30
gcloud functions logs read twelvedata-fetcher --project=aialgotradehits --limit=30
```

### Check Cloud Schedulers
```bash
gcloud scheduler jobs list --project=aialgotradehits --location=us-central1

# Manually trigger a scheduler
gcloud scheduler jobs run bulletproof-hourly-all --location=us-central1 --project=aialgotradehits
```

### Deploy Cloud Functions
```bash
# Bulletproof fetcher (recommended)
cd cloud_function_bulletproof && gcloud functions deploy bulletproof-fetcher \
  --gen2 --runtime=python312 --region=us-central1 --source=. \
  --entry-point=bulletproof_fetch --trigger-http --allow-unauthenticated \
  --memory=4096MB --timeout=540s --project=aialgotradehits

# TwelveData fetcher
cd cloud_function_twelvedata && gcloud functions deploy twelvedata-fetcher \
  --gen2 --runtime=python312 --region=us-central1 --source=. \
  --entry-point=fetch_data --trigger-http --allow-unauthenticated \
  --memory=4096MB --timeout=540s --project=aialgotradehits
```

### Deploy Trading App to Cloud Run
```bash
cd stock-price-app

gcloud run deploy trading-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project aialgotradehits
```

### Local Development - Trading App
```bash
cd stock-price-app
npm install
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview production build
```

## Key Implementation Details

### Error Tolerance (Bulletproof Fetcher)
- **Exponential backoff with jitter:** 5 retries per symbol
- **Circuit breaker:** Opens after 10 failures, resets after 60s
- **Dead letter queue:** Failed symbols tracked for retry
- **Token bucket rate limiting:** 55 calls/min TwelveData

### Multi-Source Integration
The bulletproof fetcher integrates multiple data sources:
1. **TwelveData** - Primary OHLCV and indicators
2. **Kraken** - Buy/sell volume and trade counts
3. **FRED** - Economic indicators (10Y Treasury, VIX, etc.)

### TwelveData Quota Optimization
```python
# CRITICAL: outputsize MUST be 5000 (maximum)
TIMEFRAME_CONFIG = {
    'weekly': {'interval': '1week', 'outputsize': 5000},
    'daily': {'interval': '1day', 'outputsize': 5000},
    'hourly': {'interval': '1h', 'outputsize': 5000},
    '5min': {'interval': '5min', 'outputsize': 5000}
}
```
With $229 plan (800 calls/min × 5000 points) = 2M records/day potential.

## Cloud Schedulers

Current active schedulers:
- `bulletproof-hourly-all`: 0 * * * * (hourly, all assets)
- `bulletproof-daily-all`: 0 1 * * * (1 AM ET, all assets daily)
- `gap-detector-hourly`: 30 * * * * (detect and fill gaps)

## Cost Structure

Monthly estimated costs (~$250-300/month):
- **TwelveData API:** $229 (2M records/day)
- **Cloud Functions:** $15-20
- **BigQuery Storage:** $5-10
- **Cloud Run:** $5-10
- **Cloud Scheduler:** $0.30

## Important Files

- `masterquery.md` - **PRIMARY REFERENCE** - All specifications
- `cloud_function_bulletproof/main.py` - Bulletproof data fetcher
- `cloud_function_api/main.py` - Trading API endpoints
- `stock-price-app/` - React trading dashboard
- `monitor_twelvedata_quota.py` - Quota monitoring

## Query Examples

### Growth Score Screening
```sql
SELECT symbol, growth_score, trend_regime, in_rise_cycle, sentiment_score, recommendation
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND growth_score >= 75
ORDER BY growth_score DESC
LIMIT 20;
```

### Rise Cycle Candidates
```sql
SELECT symbol, datetime, close, ema_12, ema_26, rsi, volume, growth_score
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE rise_cycle_start = TRUE
  AND rsi BETWEEN 50 AND 70
ORDER BY datetime DESC
LIMIT 20;
```

### ML Predictions
```sql
SELECT * FROM `aialgotradehits.ml_models.v_daily_predictions`
WHERE predicted_direction = 'UP'
  AND probability > 0.55
ORDER BY probability DESC;
```

## Technical Constraints

1. **Windows Environment**: Scripts include Windows encoding fixes
2. **TwelveData Rate Limits**: 800 calls/min, use rate limiting
3. **Indicator Calculation**: Requires 50-200 candles minimum
4. **Function Timeout**: 540s max for Cloud Functions Gen2
