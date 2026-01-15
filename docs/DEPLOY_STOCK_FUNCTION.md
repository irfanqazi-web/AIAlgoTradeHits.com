# Deploy Stock Cloud Function - Manual Steps

## Status Update

✅ **BigQuery Table Created**: `cryptobot-462709.crypto_trading_data.stock_analysis` (81 fields)
🔄 **Historical Data Upload**: IN PROGRESS (~40/97 stocks uploaded)
⏳ **Cloud Function**: Ready to deploy
⏳ **Cloud Scheduler**: Ready to create

---

## Step 1: Deploy Cloud Function (Manual)

Since gcloud has a module issue on your system, deploy using Google Cloud Console:

### Option A: Via Google Cloud Console (Easiest)

1. **Go to Cloud Functions**:
   - Open: https://console.cloud.google.com/functions/list?project=cryptobot-462709

2. **Create Function**:
   - Click "CREATE FUNCTION"
   - Choose **2nd gen**
   - Function name: `daily-stock-fetcher`
   - Region: `us-central1`
   - Trigger: HTTP
   - Authentication: Allow unauthenticated invocations
   - Click "SAVE" then "NEXT"

3. **Configure Code**:
   - Runtime: Python 3.11
   - Entry point: `daily_stock_fetch`
   - Source code: Inline editor

   Copy the contents from:
   - `cloud_function_daily_stocks/main.py` → main.py (in editor)
   - `cloud_function_daily_stocks/requirements.txt` → requirements.txt (in editor)

4. **Advanced Settings**:
   - Memory: 2 GiB
   - Timeout: 540 seconds
   - Max instances: 1

5. **Click "DEPLOY"** (takes 2-3 minutes)

6. **Get Function URL**:
   - After deployment, copy the trigger URL
   - Example: `https://us-central1-cryptobot-462709.cloudfunctions.net/daily-stock-fetcher`

### Option B: Fix gcloud and Deploy

If you want to fix gcloud:

```bash
# Fix Python path for gcloud
set CLOUDSDK_PYTHON=C:\Users\irfan\AppData\Local\Programs\Python\Python313\python.exe

# Then deploy
cd cloud_function_daily_stocks
gcloud functions deploy daily-stock-fetcher \
  --gen2 \
  --runtime python311 \
  --region us-central1 \
  --source . \
  --entry-point daily_stock_fetch \
  --trigger-http \
  --allow-unauthenticated \
  --timeout 540 \
  --memory 2Gi \
  --max-instances 1 \
  --project cryptobot-462709
```

---

## Step 2: Create Cloud Scheduler

Once the Cloud Function is deployed, create the daily scheduler:

```bash
# Delete existing scheduler if any
gcloud scheduler jobs delete daily-stock-fetch-job \
  --location us-central1 \
  --project cryptobot-462709 \
  --quiet

# Create new scheduler (midnight ET daily)
gcloud scheduler jobs create http daily-stock-fetch-job \
  --location us-central1 \
  --schedule "0 0 * * *" \
  --uri https://us-central1-cryptobot-462709.cloudfunctions.net/daily-stock-fetcher \
  --http-method GET \
  --time-zone America/New_York \
  --project cryptobot-462709 \
  --description "Daily stock data fetch with Elliott Wave and Fibonacci"
```

---

## Step 3: Test the Function

Test manually:

```bash
# Via curl
curl https://us-central1-cryptobot-462709.cloudfunctions.net/daily-stock-fetcher

# Or manually trigger scheduler
gcloud scheduler jobs run daily-stock-fetch-job \
  --location us-central1 \
  --project cryptobot-462709
```

---

## Step 4: Verify Data in BigQuery

Check that data is being populated:

```sql
-- Count total records
SELECT COUNT(*) as total_records, COUNT(DISTINCT symbol) as unique_stocks
FROM `cryptobot-462709.crypto_trading_data.stock_analysis`;

-- View latest data with Elliott Wave
SELECT
  symbol,
  company_name,
  sector,
  DATE(datetime) as date,
  close,
  elliott_wave_degree,
  wave_position,
  fib_618,
  rsi,
  macd
FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
ORDER BY datetime DESC
LIMIT 20;
```

---

## Current Status

**Historical Data Upload Progress**:
- The upload script is currently running
- Processing: ~40/97 stocks completed
- Each stock: 126 days × 81 fields = full technical analysis
- ETA: ~3-4 minutes remaining

**When Upload Completes**:
- You'll have ~12,222 rows in BigQuery
- 97 stocks × 126 days each
- All with Elliott Wave & Fibonacci levels

---

## File Locations

All files are in: `C:\Users\irfan\OneDrive - Aretec, Inc\Desktop\1AITrading\Trading\`

- **Cloud Function Code**: `cloud_function_daily_stocks/main.py`
- **Requirements**: `cloud_function_daily_stocks/requirements.txt`
- **Historical Data**: `stock_6month_ohlc_data.csv`
- **Documentation**: `STOCK_DEPLOYMENT_GUIDE.md`

---

## Next Steps After Deployment

1. ✅ Historical data uploaded to BigQuery
2. ✅ Daily Cloud Function deployed
3. ✅ Cloud Scheduler created
4. 📊 Integrate into trading app (stock-price-app)
5. 📈 Add stock charts with Elliott Wave overlays
6. 🎯 Create trading signals based on Fibonacci levels

---

**Note**: The historical data upload is currently running in the background. You can check progress in the terminal where it's executing. Once complete, you'll see: "UPLOAD COMPLETE - Total rows uploaded: 12222"
