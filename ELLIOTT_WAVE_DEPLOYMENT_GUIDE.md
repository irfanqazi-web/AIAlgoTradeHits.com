# Elliott Wave & Fibonacci Analysis - Deployment Guide

## Overview

This guide covers the deployment and usage of the enhanced daily crypto data collection system with Elliott Wave theory and Fibonacci analysis integrated into the KrakenPro cryptocurrency trading platform.

## What's New

### 1. Elliott Wave Pattern Detection

The system now automatically detects and analyzes Elliott Wave patterns in daily cryptocurrency data:

**Elliott Wave Fields:**
- `elliott_wave_degree`: Wave classification (Minute, Minor, Intermediate, Primary, Cycle)
- `wave_position`: Current position in the 5-wave impulse sequence (1-5)
- `impulse_wave_count`: Number of impulse waves detected
- `corrective_wave_count`: Number of corrective waves detected
- `wave_1_high`: Peak of Wave 1
- `wave_2_low`: Trough of Wave 2
- `wave_3_high`: Peak of Wave 3 (typically the longest)
- `wave_4_low`: Trough of Wave 4
- `wave_5_high`: Peak of Wave 5
- `trend_direction`: Overall trend (1: uptrend, -1: downtrend, 0: sideways)

### 2. Fibonacci Retracement & Extension Levels

Automatic calculation of key Fibonacci levels for each trading pair:

**Fibonacci Retracement Levels:**
- `fib_0`: 0% level (swing low)
- `fib_236`: 23.6% retracement
- `fib_382`: 38.2% retracement (minor support/resistance)
- `fib_500`: 50% retracement (key psychological level)
- `fib_618`: 61.8% retracement (golden ratio, major support/resistance)
- `fib_786`: 78.6% retracement
- `fib_100`: 100% level (swing high)

**Fibonacci Extension Levels:**
- `fib_ext_1272`: 127.2% extension (profit target 1)
- `fib_ext_1618`: 161.8% extension (golden ratio extension, profit target 2)
- `fib_ext_2618`: 261.8% extension (profit target 3)

**Distance Metrics:**
- `dist_to_fib_236`: Percentage distance from current price to 23.6% level
- `dist_to_fib_382`: Percentage distance to 38.2% level
- `dist_to_fib_500`: Percentage distance to 50% level
- `dist_to_fib_618`: Percentage distance to 61.8% level

### 3. User Management Tables

Three new BigQuery tables for Cloud Run deployment:

**users table:**
- User authentication and profile information
- Trading preferences and UI settings
- Subscription management
- API key storage (encrypted)
- Activity tracking

**trading_sessions table:**
- Session tracking for user activity
- IP address and device information
- Session duration and action counts

**user_trades table:**
- Complete trading history
- Entry/exit prices and P&L tracking
- Elliott Wave and Fibonacci levels at entry
- Technical indicator values at trade execution

## Deployment Steps

### Step 1: Deploy Updated Daily Cloud Function

```bash
cd cloud_function_daily

# Deploy the updated function with Elliott Wave calculations
python deploy_via_api.py
```

The deploy script will:
- Package the updated main.py with Elliott Wave and Fibonacci functions
- Deploy to Google Cloud Functions
- Configure with 540 second timeout
- Allocate 2GB memory

### Step 2: Verify BigQuery Schema Update

The schema now includes 81 total fields (up from 45):
- 45 original technical indicator fields
- 17 Fibonacci analysis fields
- 10 Elliott Wave detection fields
- 9 helper fields for wave pattern detection

Check the schema:
```bash
bq show cryptobot-462709:crypto_trading_data.crypto_analysis
```

### Step 3: Trigger Initial Data Collection

```bash
# Make function publicly accessible
gcloud functions add-invoker-policy-binding daily-crypto-fetcher \
  --region=us-central1 \
  --member=allUsers \
  --project=cryptobot-462709

# Trigger the function manually
curl https://daily-crypto-fetcher-cnyn5l4u2a-uc.a.run.app
```

Wait for completion (approximately 15-20 minutes for ~675 pairs).

### Step 4: Verify Data with Elliott Wave Fields

```sql
SELECT
  pair,
  close,
  elliott_wave_degree,
  wave_position,
  trend_direction,
  fib_618,
  fib_500,
  dist_to_fib_618,
  wave_3_high,
  wave_5_high
FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND elliott_wave_degree IS NOT NULL
ORDER BY close DESC
LIMIT 20;
```

### Step 5: Create User Tables (Already Completed)

User tables have been created:
- `users`: User authentication and preferences
- `trading_sessions`: Session tracking
- `user_trades`: Trading history

Verify:
```bash
bq ls cryptobot-462709:crypto_trading_data
```

### Step 6: Cloud Scheduler Configuration

The daily scheduler is already configured. Verify it's running:

```bash
# Check scheduler status
gcloud scheduler jobs describe daily-crypto-fetch-job \
  --location=us-central1 \
  --project=cryptobot-462709

# Manually trigger if needed
gcloud scheduler jobs run daily-crypto-fetch-job \
  --location=us-central1 \
  --project=cryptobot-462709
```

## Using Elliott Wave Data in Your Application

### Example Queries

#### Find Crypto in Wave 3 (Strong Uptrend)

Wave 3 is typically the strongest and longest impulse wave:

```sql
SELECT
  pair,
  close,
  elliott_wave_degree,
  wave_position,
  wave_1_high,
  wave_2_low,
  wave_3_high,
  trend_direction,
  rsi,
  macd
FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND wave_position = 3
  AND trend_direction = 1
  AND rsi < 70  -- Not overbought
ORDER BY (wave_3_high - wave_1_high) DESC
LIMIT 10;
```

#### Find Crypto at Key Fibonacci Levels

```sql
SELECT
  pair,
  close,
  fib_618,
  fib_500,
  fib_382,
  dist_to_fib_618,
  rsi,
  macd,
  trend_direction
FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND ABS(dist_to_fib_618) < 2  -- Within 2% of 61.8% level
  AND trend_direction = 1
ORDER BY rsi ASC
LIMIT 10;
```

#### Find Wave 5 Completion (Potential Reversal)

Wave 5 often marks the end of an impulse sequence:

```sql
SELECT
  pair,
  close,
  elliott_wave_degree,
  wave_position,
  wave_5_high,
  wave_3_high,
  fib_ext_1618,
  rsi,
  macd_hist,
  trend_direction
FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND wave_position = 5
  AND rsi > 70  -- Overbought - potential reversal
  AND close >= fib_ext_1618  -- Price at extension level
ORDER BY rsi DESC
LIMIT 10;
```

#### Combine Elliott Wave + Fibonacci + Technical Indicators

```sql
WITH analysis AS (
  SELECT
    pair,
    close,
    elliott_wave_degree,
    wave_position,
    trend_direction,
    fib_618,
    fib_500,
    dist_to_fib_618,
    dist_to_fib_500,
    rsi,
    macd,
    macd_signal,
    adx,
    wave_2_low,
    wave_3_high
  FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`
  WHERE DATE(datetime) = CURRENT_DATE() - 1
)
SELECT *
FROM analysis
WHERE
  -- Elliott Wave: Looking for Wave 3 or early Wave 4
  wave_position IN (3, 4)
  -- Fibonacci: Price near 38.2% or 50% retracement
  AND (ABS(dist_to_fib_500) < 3 OR ABS(dist_to_fib_618) < 3)
  -- Trend: Uptrend
  AND trend_direction = 1
  -- RSI: Not overbought
  AND rsi BETWEEN 30 AND 70
  -- MACD: Positive momentum
  AND macd > macd_signal
  -- ADX: Strong trend
  AND adx > 25
ORDER BY adx DESC, rsi ASC
LIMIT 20;
```

## Elliott Wave Trading Rules

### Wave 1 (Initial Impulse)
- Often difficult to identify in real-time
- Usually accompanied by low volume
- **Entry**: Wait for Wave 2 pullback

### Wave 2 (Correction)
- Typically retraces 38.2% to 61.8% of Wave 1
- Should NOT retrace more than 100% of Wave 1
- **Entry**: Buy near Fibonacci 61.8% level with confirmation

### Wave 3 (Strongest Move)
- Usually the longest and strongest wave
- Must be longer than both Wave 1 and Wave 5
- High volume, strong momentum
- **Entry**: Early Wave 3 or on pullbacks
- **Target**: Fibonacci extensions (127.2%, 161.8%)

### Wave 4 (Correction)
- Often retraces 23.6% to 38.2% of Wave 3
- Should NOT overlap with Wave 1 price territory
- **Entry**: Buy near Fibonacci 38.2% level

### Wave 5 (Final Impulse)
- Often shows divergence on indicators (RSI, MACD)
- Volume often lower than Wave 3
- **Exit**: Near Fibonacci extension levels
- **Warning**: Reversal likely after Wave 5 completion

## Integration with Stock Price App

The trading app now has access to:

1. **Daily Elliott Wave data** for all ~675 USD crypto pairs
2. **Fibonacci levels** automatically calculated and updated daily
3. **User tables** ready for authentication when deployed to Cloud Run

### Next Steps for Frontend Integration:

1. **Query Elliott Wave data** from BigQuery
2. **Display wave patterns** on charts with visual indicators
3. **Show Fibonacci levels** as horizontal lines on price charts
4. **Implement alerts** when price reaches key Fibonacci levels
5. **Highlight opportunities** when Wave + Fibonacci + Technical indicators align

## Monitoring and Maintenance

### Check Daily Function Logs

```bash
gcloud functions logs read daily-crypto-fetcher \
  --project=cryptobot-462709 \
  --limit=50
```

### Verify Data Freshness

```sql
SELECT
  DATE(datetime) as date,
  COUNT(DISTINCT pair) as unique_pairs,
  COUNT(*) as total_records,
  COUNTIF(elliott_wave_degree IS NOT NULL) as with_elliott_wave,
  COUNTIF(fib_618 IS NOT NULL) as with_fibonacci
FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`
WHERE DATE(datetime) >= CURRENT_DATE() - 7
GROUP BY date
ORDER BY date DESC;
```

### Monitor Scheduler

```bash
gcloud scheduler jobs list \
  --project=cryptobot-462709 \
  --location=us-central1
```

## Cost Estimates

Updated monthly costs with Elliott Wave calculations:

- **Cloud Functions**: ~$4/month (daily function)
  - Executions: ~30/month
  - Duration: ~20 minutes per run
  - Memory: 2GB

- **BigQuery Storage**: ~$3/month (increased from $2)
  - Daily table: ~81 fields × 675 pairs × 365 days
  - User tables: Minimal initial storage

- **BigQuery Queries**: Pay-per-query
  - $5/TB scanned
  - Elliott Wave queries typically scan 10-100 MB

**Total Estimated Cost**: ~$7-10/month

## Troubleshooting

### Elliott Wave Not Detected

Some pairs may not have enough data for wave pattern detection:
- Requires minimum 13 daily candles
- Requires identifiable swing highs and lows
- Check `swing_high` and `swing_low` boolean fields

### Fibonacci Levels Missing

Fibonacci calculation requires:
- At least 1 recent swing high
- At least 1 recent swing low
- Check data availability for the specific pair

### Schema Mismatch

If you encounter schema errors:
1. Backup existing data
2. Drop and recreate table with new schema
3. Re-run historical data collection

## Support and Documentation

- **Elliott Wave Theory**: Classic 5-wave impulse + 3-wave correction pattern
- **Fibonacci Ratios**: 23.6%, 38.2%, 50%, 61.8%, 78.6%, 127.2%, 161.8%, 261.8%
- **BigQuery Documentation**: https://cloud.google.com/bigquery/docs
- **Cloud Functions**: https://cloud.google.com/functions/docs

---

**Last Updated**: 2025-11-07
**Version**: 2.0 with Elliott Wave & Fibonacci Analysis
**Project**: cryptobot-462709
