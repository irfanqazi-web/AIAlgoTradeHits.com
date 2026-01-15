# Quick Start Guide - cryptobot-462709 Trading Pipeline

## Current Status: 95% Complete ✓

All infrastructure is deployed. You just need to run 3 simple commands to complete the setup.

---

## Complete Setup in 3 Steps

### Step 1: Make Functions Public (Required for Schedulers)

Run these three commands in your terminal:

```bash
gcloud functions add-invoker-policy-binding daily-crypto-fetcher --region=us-central1 --member=allUsers --project=cryptobot-462709

gcloud functions add-invoker-policy-binding hourly-crypto-fetcher --region=us-central1 --member=allUsers --project=cryptobot-462709

gcloud functions add-invoker-policy-binding fivemin-top10-fetcher --region=us-central1 --member=allUsers --project=cryptobot-462709
```

**Time:** 1-2 minutes

### Step 2: Trigger Functions to Populate Tables

After Step 1 completes, run these commands:

```bash
# Trigger Daily Function (will run 15-20 minutes)
curl https://daily-crypto-fetcher-cnyn5l4u2a-uc.a.run.app

# Trigger Hourly Function (will run 12-15 minutes)
curl https://hourly-crypto-fetcher-cnyn5l4u2a-uc.a.run.app

# Trigger 5-Minute Function (will run 5-7 minutes)
curl https://fivemin-top10-fetcher-cnyn5l4u2a-uc.a.run.app
```

**Note:** These run in the background. You can close the terminal.

**Time:** 20-30 minutes total (running in background)

### Step 3: Verify Data is Populating

After ~30 minutes, check your BigQuery tables:

```bash
python check_bigquery_counts.py
```

**Expected Results:**
- Daily table: ~675 records
- Hourly table: ~675 records
- 5-Minute table: ~120 records

---

## Optional: Deploy Trading Application

If you want the web-based trading dashboard:

```bash
cd stock-price-app

gcloud run deploy crypto-trading-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project cryptobot-462709
```

**Time:** 5-10 minutes

---

## What Happens After Setup

Once complete, your system will automatically:

✓ **Collect daily data** at midnight ET every night
✓ **Collect hourly data** every hour
✓ **Collect 5-minute data** for top 10 gainers every 5 minutes
✓ **Calculate 29 technical indicators** for all data
✓ **Store everything in BigQuery** for your AI trading algorithms

**No further action required!**

---

## Quick Verification

### Check Schedulers are Running
```bash
gcloud scheduler jobs list --project=cryptobot-462709 --location=us-central1
```

All three should show `STATE: ENABLED`

### Check Latest Data
```sql
-- Run in BigQuery Console
SELECT MAX(datetime) as latest_data, COUNT(*) as records
FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`;
```

---

## Deployed Infrastructure

| Component | Status | Details |
|-----------|--------|---------|
| BigQuery Dataset | ✓ Complete | 3 tables with 29 indicators each |
| Daily Cloud Function | ✓ Deployed | Runs at midnight ET |
| Hourly Cloud Function | ✓ Deployed | Runs every hour |
| 5-Min Cloud Function | ✓ Deployed | Runs every 5 minutes |
| Daily Scheduler | ✓ Enabled | Auto-triggers daily function |
| Hourly Scheduler | ✓ Enabled | Auto-triggers hourly function |
| 5-Min Scheduler | ✓ Enabled | Auto-triggers 5-min function |

---

## Access Your Data

### Python Example
```python
from google.cloud import bigquery

client = bigquery.Client(project='cryptobot-462709')

# Get latest data with indicators
query = """
SELECT pair, close, rsi, macd, bb_percent, adx
FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`
WHERE DATE(datetime) = CURRENT_DATE() - 1
ORDER BY rsi DESC
LIMIT 10
"""

df = client.query(query).to_dataframe()
print(df)
```

### Sample Trading Query
```sql
-- Find oversold cryptos with strong trends
SELECT pair, close, rsi, adx, sma_200, datetime
FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND rsi < 30  -- Oversold
  AND adx > 25  -- Strong trend
  AND close > sma_200  -- Above 200-day MA
ORDER BY rsi ASC
LIMIT 20;
```

---

## Need Help?

**Check Function Logs:**
```bash
gcloud functions logs read daily-crypto-fetcher --project=cryptobot-462709 --limit=20
```

**Manually Trigger a Scheduler:**
```bash
gcloud scheduler jobs run daily-crypto-fetch-job --location=us-central1 --project=cryptobot-462709
```

**Check Table Counts:**
```bash
python check_bigquery_counts.py
```

---

## Cost Overview

**Monthly Costs:** ~$135/month
- Cloud Functions: $126/month
- BigQuery: $2/month
- Cloud Scheduler: $0.30/month
- Cloud Run (if deployed): $5/month

---

## Summary

**What's Done:**
✓ Complete infrastructure deployed
✓ All schedulers configured and enabled
✓ 29 technical indicators implemented
✓ Multi-timeframe data collection ready

**What You Need to Do:**
1. Run 3 commands to make functions public (1 minute)
2. Trigger functions once to populate tables (30 minutes wait)
3. Verify data is collecting properly (1 minute)

**Total Your Time:** ~5 minutes of active work
**Total Wait Time:** ~30 minutes for initial data population

---

**After setup, everything runs automatically 24/7!**

Ready to build AI-powered trading algorithms with comprehensive technical analysis data.
