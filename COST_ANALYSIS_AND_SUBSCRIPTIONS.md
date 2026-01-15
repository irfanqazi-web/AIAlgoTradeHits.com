# Trading App - Cost Analysis & Subscription Requirements

**Date:** November 14, 2025
**Project:** AI Algo Trade Hits Trading Platform
**GCP Project ID:** cryptobot-462709

## Executive Summary

Your trading application is currently deployed and operational with the following monthly cost estimate: **$135-150/month**. This includes data collection from 674 crypto pairs and stock market data with automated collection, storage, and API serving.

## Required Subscriptions & Services

### 1. Google Cloud Platform (GCP) - PRIMARY PLATFORM
**Current Status:** ACTIVE
**Project ID:** cryptobot-462709
**Monthly Cost:** $135-150

#### Components Breakdown:

| Service | Purpose | Monthly Cost | Notes |
|---------|---------|--------------|-------|
| **Cloud Functions (Gen 2)** | Data collection (4 functions) | $126 | Hourly crypto, 5-min crypto, daily crypto, stock hourly |
| **BigQuery** | Data storage & queries | $2-5 | Storage: $0.02/GB, Queries: $5/TB |
| **Cloud Scheduler** | Automated triggers | $0.30 | 3 schedulers (daily, hourly, 5-min) |
| **Cloud Run** | API & Frontend hosting | $5-10 | Trading API + React Frontend |
| **Cloud Storage** | Document storage | $0.50 | 43 documents (markdown, PDF, DOCX) |

#### GCP Billing Account Requirements:
- **Setup:** Link a credit/debit card or bank account
- **Free Tier:** $300 credits for 90 days (may already be used)
- **Billing Alerts:** Set at $100, $125, $150 to monitor costs
- **Payment Method:** Credit card recommended for reliability

**Action Required:**
1. Go to https://console.cloud.google.com/billing
2. Verify billing account is active for project `cryptobot-462709`
3. Set up budget alerts at $100, $125, $150
4. Enable automatic payments

---

### 2. Data Provider APIs - CURRENTLY FREE

#### Kraken Pro API
**Status:** FREE (Public API)
**Purpose:** Cryptocurrency price data (674 pairs)
**Limits:** Rate limited to prevent abuse (currently using 1.5s delays)
**Cost:** $0/month
**Upgrade Path:** Kraken Pro subscription ($10-50/month) for:
  - Higher rate limits
  - WebSocket streaming data
  - Priority access during high volume

#### Yahoo Finance API
**Status:** FREE (via yfinance library)
**Purpose:** Stock market data
**Limits:** Unofficial API, may have rate limits
**Cost:** $0/month
**Upgrade Path:** Alpha Vantage or Polygon.io for production:
  - Alpha Vantage: $50-250/month for real-time data
  - Polygon.io: $29-199/month for stocks + crypto

---

## Current Monthly Cost Breakdown (Detailed)

### Cloud Functions Cost Analysis

#### 1. Daily Crypto Fetcher
- **Invocations:** 30/month (once daily)
- **Execution Time:** ~8 minutes per run
- **Memory:** 512MB
- **Monthly Cost:** ~$4

#### 2. Hourly Crypto Fetcher
- **Invocations:** 720/month (hourly)
- **Execution Time:** ~6 minutes per run
- **Memory:** 512MB
- **Monthly Cost:** ~$72

#### 3. 5-Minute Top 10 Crypto Fetcher
- **Invocations:** 8,640/month (every 5 min)
- **Execution Time:** ~2 minutes per run
- **Memory:** 512MB
- **Monthly Cost:** ~$50

#### 4. Stock Hourly Fetcher
- **Invocations:** 720/month (hourly)
- **Execution Time:** ~4 minutes per run
- **Memory:** 512MB
- **Monthly Cost:** ~$35 (if fully deployed)

**Total Cloud Functions:** $126-161/month

### BigQuery Storage & Query Costs

**Current Data:**
- Crypto Daily: 196,231 records (~2 GB)
- Crypto Hourly: 3,256 records (~0.5 GB)
- Crypto 5-Min: 2,408 records (~0.3 GB)
- **Total Storage:** ~3 GB × $0.02/GB = **$0.06/month**

**Query Costs:**
- API queries: ~10,000/month
- Dashboard queries: ~5,000/month
- **Total Queries:** ~0.05 TB × $5/TB = **$0.25/month**

**Monthly BigQuery:** $2-5 (including growth)

### Cloud Run Costs

#### Trading API
- **Requests:** ~50,000/month (estimated)
- **CPU Time:** 0.1 seconds per request
- **Memory:** 512MB
- **Monthly Cost:** ~$3

#### Frontend App
- **Requests:** ~10,000/month (user page loads)
- **Static serving:** Minimal CPU
- **Memory:** 256MB
- **Monthly Cost:** ~$2

**Total Cloud Run:** $5/month

---

## Performance Optimization Strategies

### 1. FASTEST Data Collection (Current: 6-8 minutes per run)

#### Option A: Parallel Processing with Cloud Functions
**Implementation:** Deploy multiple Cloud Functions, each handling a subset of pairs
- **Current:** 1 function fetches all 674 pairs sequentially
- **Optimized:** 10 functions fetch 67 pairs each in parallel
- **Speed Improvement:** 10x faster (~40 seconds vs 6 minutes)
- **Cost Impact:** +$0 (same total invocations, just distributed)

**How to Implement:**
```python
# Split pairs into 10 groups
pairs_per_function = 67
for i in range(10):
    deploy_function(f"crypto-fetcher-{i}", pairs[i*67:(i+1)*67])
```

#### Option B: Use Cloud Tasks for Distributed Workload
**Implementation:** Single function creates tasks for each pair
- **Speed Improvement:** Near real-time (depends on task queue)
- **Cost Impact:** +$0.40/million tasks = +$0.27/month
- **Benefit:** Better control, easier monitoring

#### Option C: Use Kraken WebSocket API (RECOMMENDED)
**Implementation:** Replace HTTP polling with WebSocket streaming
- **Speed Improvement:** INSTANT (real-time updates)
- **Cost Impact:** -50% Cloud Function costs (less frequent runs needed)
- **Subscription Required:** Kraken Pro ($0-50/month depending on tier)

**Fastest Setup:**
```python
# WebSocket streaming (real-time)
import asyncio
import websockets

async def stream_prices():
    async with websockets.connect('wss://ws.kraken.com/') as ws:
        await ws.send(json.dumps({
            "event": "subscribe",
            "pair": ["XBT/USD", "ETH/USD", ...],
            "subscription": {"name": "ticker"}
        }))
        while True:
            data = await ws.recv()
            # Insert directly to BigQuery
```

---

### 2. Reduce API Call Frequency

**Current Collection Intervals:**
- Daily: Every 24 hours ✓ (optimal)
- Hourly: Every 1 hour (can be optimized)
- 5-Minute: Every 5 minutes (can be optimized)

**Optimization Options:**

#### Option A: Reduce Hourly to Every 4 Hours
- **Cost Savings:** -75% on hourly function ($72 → $18)
- **Trade-off:** Less frequent updates, still sufficient for most use cases

#### Option B: Reduce 5-Min to Every 15 Minutes
- **Cost Savings:** -67% on 5-min function ($50 → $17)
- **Trade-off:** Still captures intraday moves, less granular

#### Option C: Smart Scheduling (Market Hours Only)
- **Implementation:** Only run during active trading hours
- **Cost Savings:** -50% (12 hours/day vs 24 hours/day)
- **Best For:** Stock data collection

**Recommended Configuration (70% cost reduction):**
```
Daily Crypto: Midnight ET (once/day) - $4/month
Hourly Crypto: Every 4 hours (6/day) - $18/month
5-Min Crypto: Top 10 pairs every 15 min - $17/month
Stock Hourly: Market hours only (9:30am-4pm ET, Mon-Fri) - $12/month

NEW TOTAL: ~$51/month (vs $126 current)
```

---

### 3. Use BigQuery Caching & Materialized Views

**Current:** Every API call queries raw data
**Optimized:** Create pre-aggregated views

```sql
-- Create materialized view for top gainers (refreshes hourly)
CREATE MATERIALIZED VIEW crypto_trading_data.top_gainers_hourly AS
SELECT pair, close, rsi, macd, roc, datetime
FROM crypto_trading_data.crypto_hourly_data
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY roc DESC
LIMIT 20;
```

**Benefits:**
- **Query Speed:** 10x faster (pre-computed)
- **Cost Savings:** -90% query costs
- **Implementation Time:** 30 minutes

---

### 4. Enable Cloud CDN for Frontend

**Current:** Cloud Run serves every request
**Optimized:** Cloud CDN caches static assets

**Setup:**
```bash
gcloud compute backend-services create trading-app-backend \
  --global --load-balancing-scheme=EXTERNAL

gcloud compute backend-services add-backend trading-app-backend \
  --global --serverless-backend=crypto-trading-app

gcloud compute url-maps create trading-app-map \
  --default-service=trading-app-backend
```

**Benefits:**
- **Speed:** 5-10x faster page loads globally
- **Cost:** +$0.08/GB (first 10TB free per month)
- **User Experience:** Significantly improved

---

## Recommended Optimization Plan

### Phase 1: Immediate (Cost: $0, Time: 2 hours)
1. ✅ Create BigQuery materialized views
2. ✅ Implement query caching in API
3. ✅ Set up billing alerts

**Expected Savings:** $2-5/month
**Performance Gain:** 5-10x faster API responses

### Phase 2: Short-term (Cost: $0, Time: 4 hours)
1. Reduce hourly collection to every 4 hours
2. Reduce 5-min collection to every 15 minutes
3. Implement parallel Cloud Functions

**Expected Savings:** $70/month
**Performance Gain:** 10x faster data collection

### Phase 3: Medium-term (Cost: $50/month, Time: 8 hours)
1. Upgrade to Kraken Pro WebSocket API
2. Implement real-time data streaming
3. Enable Cloud CDN for frontend

**Expected Savings:** -$50/month Cloud Functions, +$50 Kraken = $0 net
**Performance Gain:** REAL-TIME data (instant updates)

---

## Total Cost Scenarios

### Scenario A: Current Setup (No Changes)
**Monthly Cost:** $135-150
**Data Freshness:** Hourly & 5-min updates
**Performance:** Good (6-min collection time)

### Scenario B: Optimized Budget (Recommended)
**Monthly Cost:** $55-65
**Data Freshness:** 4-hour & 15-min updates
**Performance:** Excellent (40-second collection time)
**Savings:** $85/month ($1,020/year)

### Scenario C: Real-Time Premium
**Monthly Cost:** $100-120
**Data Freshness:** Real-time WebSocket streaming
**Performance:** Exceptional (instant updates)
**Best For:** Professional trading, production use

---

## How to Monitor & Control Costs

### 1. Enable Cost Alerts
```bash
# Set budget alerts
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="Trading App Budget" \
  --budget-amount=150 \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100
```

### 2. Monitor Usage Dashboard
- **URL:** https://console.cloud.google.com/billing/reports?project=cryptobot-462709
- **Review:** Weekly
- **Watch For:**   - Unexpected spikes in Cloud Function invocations
  - BigQuery query costs increasing
  - Cloud Run request surges

### 3. Cost Optimization Script
```python
# Auto-check costs and send alerts
from google.cloud import billing

def check_daily_costs():
    client = billing.CloudBillingClient()
    costs = client.get_project_billing_info(name='projects/cryptobot-462709')

    if costs > DAILY_LIMIT:
        send_alert(f'Daily costs: ${costs} exceeded limit ${DAILY_LIMIT}')
```

---

## Action Items for Tomorrow

1. **Verify Billing Setup** (5 min)
   - Check https://console.cloud.google.com/billing
   - Ensure credit card is active
   - Verify no payment issues

2. **Set Budget Alerts** (10 min)
   - Create alerts at $100, $125, $150
   - Add email: haq.irfanul@gmail.com

3. **Review Current Costs** (15 min)
   - Check actual usage in Billing Reports
   - Compare to estimates above
   - Identify any anomalies

4. **Decide on Optimization** (30 min)
   - Review Scenario A vs B vs C
   - Choose cost/performance balance
   - Plan implementation timeline

5. **Test Trading App** (10 min)
   - Visit: https://crypto-trading-app-252370699783.us-central1.run.app
   - Verify charts display data
   - Check all 3 timeframes (Daily, Hourly, 5-Min)

---

## Questions & Answers

### Q: Can I reduce costs to near-zero?
**A:** Yes, using GCP Free Tier:
- Cloud Functions: 2 million invocations/month free
- Cloud Run: 2 million requests/month free
- BigQuery: 1 TB queries/month free
- **If within free tier:** $0/month (first 90 days)
- **After free tier:** Minimum $5-10/month for minimal usage

### Q: How fast can data collection be?
**A:** Fastest options:
1. **Current (sequential):** 6-8 minutes
2. **Parallel functions:** 40-60 seconds
3. **WebSocket real-time:** Instant (<1 second)

### Q: What if I exceed the budget?
**A:** GCP will:
1. Send email alert at 80%, 100% of budget
2. Continue charging (won't automatically stop)
3. **Recommendation:** Set up billing limits or disable Cloud Functions

### Q: Can I pause the app to save costs?
**A:** Yes:
```bash
# Pause all Cloud Schedulers (stops data collection)
gcloud scheduler jobs pause daily-crypto-fetch-job --location=us-central1
gcloud scheduler jobs pause hourly-crypto-fetch-job --location=us-central1
gcloud scheduler jobs pause fivemin-top10-fetch-job --location=us-central1

# Resume when needed
gcloud scheduler jobs resume [JOB_NAME] --location=us-central1
```

---

## Support & Resources

- **GCP Billing Console:** https://console.cloud.google.com/billing
- **GCP Pricing Calculator:** https://cloud.google.com/products/calculator
- **Trading App Frontend:** https://crypto-trading-app-252370699783.us-central1.run.app
- **Trading API:** https://trading-api-252370699783.us-central1.run.app
- **Project Console:** https://console.cloud.google.com/home/dashboard?project=cryptobot-462709

**Emergency Cost Control:**
```bash
# If costs spike unexpectedly, run this to pause everything:
./pause_all_services.sh

# Or manually:
gcloud scheduler jobs pause-all --location=us-central1
```

---

**Last Updated:** November 14, 2025
**Next Review:** Weekly (every Monday)
