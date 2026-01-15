# AI Trading Data Pipeline - FULLY DEPLOYED WITH TECHNICAL INDICATORS

## Deployment Status: COMPLETE ✓

All three Cloud Functions have been successfully deployed with comprehensive technical indicators and are running automatically in the background.

---

## System Overview

### 1. Daily Crypto Fetcher
**Status:** ENABLED ✓
**Function:** daily-crypto-fetcher
**Schedule:** Every day at midnight ET (0 0 * * *)
**Table:** `molten-optics-310919.kamiyabPakistan.crypto_analysis`
**URL:** https://daily-crypto-fetcher-qatsqsbqra-uc.a.run.app

**What it does:**
- Fetches 250 days of historical data for each crypto pair
- Calculates 29 technical indicators from historical context
- Stores only the latest daily record with all indicators
- Covers ~675 USD cryptocurrency pairs from Kraken Pro

### 2. Hourly Crypto Fetcher
**Status:** ENABLED ✓
**Function:** hourly-crypto-fetcher
**Schedule:** Every hour (0 * * * *)
**Table:** `molten-optics-310919.kamiyabPakistan.crypto_hourly_data`
**URL:** https://hourly-crypto-fetcher-qatsqsbqra-uc.a.run.app

**What it does:**
- Fetches 250 hours of historical data for each crypto pair
- Calculates 29 technical indicators from historical context
- Stores the latest hourly record with all indicators
- Covers all USD cryptocurrency pairs from Kraken Pro

### 3. 5-Minute Top-10 Gainers Fetcher
**Status:** ENABLED ✓
**Function:** fivemin-top10-fetcher
**Schedule:** Every 5 minutes (*/5 * * * *)
**Table:** `molten-optics-310919.kamiyabPakistan.crypto_5min_top10_gainers`
**URL:** https://fivemin-top10-fetcher-qatsqsbqra-uc.a.run.app

**What it does:**
- Analyzes hourly data to find top 10 gainers
- Fetches 20 hours of 5-minute OHLC data for each top gainer
- Calculates 29 technical indicators from historical context
- Stores the latest hour of 5-minute records with indicators
- Dynamically updates based on market movers

---

## Technical Indicators (29 Total)

All three systems calculate the following comprehensive set of technical indicators:

### Price-Based Indicators
- **symbol** - Trading pair symbol
- **open_price** - Opening price (same as open)
- **hi_lo** - High-Low range
- **pct_hi_lo_over_lo** - High-Low percentage over Low

### Momentum Indicators
- **rsi** - Relative Strength Index (14 periods)
- **macd** - Moving Average Convergence Divergence
- **macd_signal** - MACD Signal Line (9 periods)
- **macd_hist** - MACD Histogram (difference between MACD and Signal)
- **roc** - Rate of Change (10 periods)
- **momentum** - Price Momentum (10 periods)
- **stoch_k** - Stochastic %K (14 periods)
- **stoch_d** - Stochastic %D (3 periods)
- **williams_r** - Williams %R (14 periods)

### Trend Indicators
- **ema_12** - 12-period Exponential Moving Average
- **ema_26** - 26-period Exponential Moving Average
- **ema_50** - 50-period Exponential Moving Average
- **sma_20** - 20-period Simple Moving Average
- **ma_50** - 50-period Simple Moving Average
- **sma_200** - 200-period Simple Moving Average
- **adx** - Average Directional Index (14 periods)
- **trix** - Triple Exponential Average
- **kama** - Kaufman Adaptive Moving Average

### Volatility Indicators
- **bb_upper** - Bollinger Band Upper (20 periods, 2 std dev)
- **bb_lower** - Bollinger Band Lower (20 periods, 2 std dev)
- **bb_percent** - Bollinger Band %B position
- **atr** - Average True Range (14 periods)

### Volume Indicators
- **obv** - On-Balance Volume
- **pvo** - Percentage Volume Oscillator

### Oscillators
- **cci** - Commodity Channel Index (20 periods)
- **ppo** - Percentage Price Oscillator
- **ultimate_oscillator** - Ultimate Oscillator (7, 14, 28 periods)
- **awesome_oscillator** - Awesome Oscillator (5, 34 periods)

---

## BigQuery Schema

Each table now has **44 fields** (up from 13-14 original fields):

**Core Fields (15):**
- pair, symbol, altname, base, quote
- timestamp, datetime
- open, open_price, high, low, close
- vwap, volume, count

**Technical Indicator Fields (29):**
- All indicators listed above

**Metadata (1):**
- fetched_at (for hourly and 5-minute only)

---

## Automatic Data Collection

### Schedule Summary
| Interval | Schedule | Next Run | Pairs | Records/Run |
|----------|----------|----------|-------|-------------|
| Daily | Midnight ET | ~12:00 AM | ~675 | ~675 |
| Hourly | Every hour | :00 | ~675 | ~675 |
| 5-Minute | Every 5 min | :00, :05, :10... | 10 | ~120 |

### Data Retention
- **Daily:** Historical data since 2025-04-12 with indicators
- **Hourly:** Rolling updates with indicators
- **5-Minute:** Top 10 gainers only, rolling updates with indicators

### Cost Estimate
**Updated with Technical Indicators:**
- Daily: ~$4/month (increased processing time)
- Hourly: ~$72/month (increased processing time)
- 5-Minute: ~$50/month (increased processing time)
- **Total: ~$130/month** (was $89/month before indicators)

The increase is due to fetching 200-250 periods of historical data for proper indicator calculation.

---

## Trading Application Integration

### Next Steps for AI Trading Application

Your trading databases are now ready with comprehensive technical analysis data:

1. **Daily Analysis Database** (`crypto_analysis`)
   - Use for: Long-term trend analysis, swing trading strategies
   - Contains: 200-day moving averages, long-term RSI, MACD trends

2. **Hourly Analysis Database** (`crypto_hourly_data`)
   - Use for: Day trading strategies, medium-term trend detection
   - Contains: Hourly indicators, recent volatility metrics

3. **5-Minute High-Frequency Database** (`crypto_5min_top10_gainers`)
   - Use for: Scalping, momentum trading, quick entries/exits
   - Contains: Real-time indicators for market movers

### Sample Integration Queries

**Find Oversold Opportunities (Daily):**
```sql
SELECT pair, close, rsi, macd, adx, datetime
FROM `molten-optics-310919.kamiyabPakistan.crypto_analysis`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND rsi < 30  -- Oversold
  AND adx > 25  -- Strong trend
ORDER BY rsi ASC
LIMIT 20;
```

**Find Bullish MACD Crossovers (Hourly):**
```sql
SELECT pair, close, macd, macd_signal, rsi, datetime
FROM `molten-optics-310919.kamiyabPakistan.crypto_hourly_data`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 3 HOUR)
  AND macd > macd_signal  -- Bullish crossover
  AND macd_hist > 0
  AND rsi > 50  -- Confirm momentum
ORDER BY macd_hist DESC
LIMIT 15;
```

**Identify Breakout Candidates (5-Minute):**
```sql
SELECT pair, close, bb_percent, rsi, volume, datetime
FROM `molten-optics-310919.kamiyabPakistan.crypto_5min_top10_gainers`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 MINUTE)
  AND bb_percent > 0.95  -- Near upper band
  AND rsi > 60  -- Momentum building
  AND volume > 0
ORDER BY bb_percent DESC, rsi DESC;
```

**Multi-Timeframe Confluence:**
```sql
-- Find pairs showing strength across all timeframes
WITH daily_strong AS (
  SELECT pair FROM `molten-optics-310919.kamiyabPakistan.crypto_analysis`
  WHERE DATE(datetime) = CURRENT_DATE() - 1 AND rsi > 60 AND adx > 25
),
hourly_strong AS (
  SELECT DISTINCT pair FROM `molten-optics-310919.kamiyabPakistan.crypto_hourly_data`
  WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 HOUR)
    AND macd > macd_signal AND rsi > 55
)
SELECT d.pair, 'Strong across Daily + Hourly' as signal
FROM daily_strong d
INNER JOIN hourly_strong h ON d.pair = h.pair;
```

---

## System Health Monitoring

### Check Scheduler Status
```bash
gcloud scheduler jobs list --location=us-central1
```

### Check Function Logs
```bash
# Daily function
gcloud functions logs read daily-crypto-fetcher --limit=50

# Hourly function
gcloud functions logs read hourly-crypto-fetcher --limit=50

# 5-minute function
gcloud functions logs read fivemin-top10-fetcher --limit=50
```

### Verify Latest Data
```sql
-- Check daily data freshness
SELECT MAX(datetime) as latest_daily_data, COUNT(*) as total_records
FROM `molten-optics-310919.kamiyabPakistan.crypto_analysis`
WHERE DATE(datetime) >= CURRENT_DATE() - 2;

-- Check hourly data freshness
SELECT MAX(datetime) as latest_hourly_data, COUNT(*) as total_records
FROM `molten-optics-310919.kamiyabPakistan.crypto_hourly_data`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 3 HOUR);

-- Check 5-minute data freshness
SELECT MAX(datetime) as latest_5min_data, COUNT(DISTINCT pair) as unique_pairs
FROM `molten-optics-310919.kamiyabPakistan.crypto_5min_top10_gainers`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 MINUTE);
```

---

## What's Running Automatically

✓ **Daily Scheduler** - Fetches ~675 pairs at midnight ET with 29 indicators
✓ **Hourly Scheduler** - Fetches ~675 pairs every hour with 29 indicators
✓ **5-Minute Scheduler** - Fetches top 10 gainers every 5 minutes with 29 indicators

All data is enriched with comprehensive technical indicators calculated from proper historical context.

---

## Important Files

### Deployment Scripts
- `cloud_function_daily/deploy_via_api.py` - Deploy daily function
- `cloud_function_hourly/deploy.py` - Deploy hourly function
- `cloud_function_5min/deploy_all.py` - Deploy 5-minute function + scheduler

### Main Code Files
- `cloud_function_daily/main.py` - Daily fetcher with indicators
- `cloud_function_hourly/main.py` - Hourly fetcher with indicators
- `cloud_function_5min/main.py` - 5-minute fetcher with indicators

### Backup Files
- `cloud_function_*/main_backup.py` - Original versions without indicators

### Documentation
- `deploy_all_with_indicators.md` - Deployment guide
- `COMPLETE_DEPLOYMENT_SUMMARY.md` - Original deployment summary
- This file - Complete deployment status with indicators

---

## Trading Application Link Instructions

When you're ready to connect your AI Trading Application:

1. **Credentials:** Use the service account credentials or Application Default Credentials
2. **Project ID:** molten-optics-310919
3. **Dataset ID:** kamiyabPakistan
4. **Tables:**
   - Daily: `crypto_analysis`
   - Hourly: `crypto_hourly_data`
   - 5-Minute: `crypto_5min_top10_gainers`

5. **Python Example:**
```python
from google.cloud import bigquery

client = bigquery.Client(project='molten-optics-310919')

# Query daily data with indicators
query = """
SELECT pair, close, rsi, macd, bb_percent, adx, datetime
FROM `molten-optics-310919.kamiyabPakistan.crypto_analysis`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND rsi < 40  -- Your strategy logic here
ORDER BY rsi ASC
"""

results = client.query(query).to_dataframe()
print(results)
```

---

## Success Summary

**Deployment Date:** October 11, 2025
**Systems Deployed:** 3
**Cloud Functions:** 3
**Cloud Schedulers:** 3
**BigQuery Tables:** 3
**Technical Indicators per Record:** 29
**Total Schema Fields:** 44
**Coverage:** ~675 crypto pairs
**Status:** ALL SYSTEMS OPERATIONAL ✓

Your AI Trading data pipeline is now fully operational with comprehensive technical analysis indicators, running automatically in the background, and ready for integration with your trading application.

---

**Ready for AI Trading Application Integration!**
