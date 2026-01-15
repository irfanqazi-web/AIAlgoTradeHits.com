# Hourly Crypto Data Fetcher - Google Cloud Deployment

This folder contains the Cloud Function that fetches hourly (60-minute) OHLC data from Kraken Pro API and stores it in BigQuery.

## Overview

- **Function**: Fetches 60-minute candle data for all 635 USD trading pairs from Kraken Pro
- **Schedule**: Runs every hour via Google Cloud Scheduler
- **Storage**: Data is appended to `crypto_hourly_data` table in BigQuery
- **Runtime**: ~15-20 minutes per execution (due to API rate limiting)

## Files

- `main.py` - Main Cloud Function code
- `requirements.txt` - Python dependencies
- `deploy.sh` - Deployment script
- `setup_scheduler.sh` - Cloud Scheduler setup script

## Deployment Steps

### 1. Test Locally (Optional)

```bash
cd cloud_function
python main.py
```

This will fetch hourly data and upload to BigQuery from your local machine.

### 2. Deploy Cloud Function

```bash
cd cloud_function
chmod +x deploy.sh
./deploy.sh
```

Or manually:

```bash
gcloud functions deploy hourly-crypto-fetcher \
  --gen2 \
  --runtime=python313 \
  --region=us-central1 \
  --source=. \
  --entry-point=hourly_crypto_fetch \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=540s \
  --memory=512MB \
  --project=molten-optics-310919
```

**Note the Function URL** from the output - you'll need it for the scheduler.

### 3. Setup Cloud Scheduler

Edit `setup_scheduler.sh` and replace `YOUR_CLOUD_FUNCTION_URL` with the actual URL from step 2.

Then run:

```bash
chmod +x setup_scheduler.sh
./setup_scheduler.sh
```

Or manually:

```bash
gcloud scheduler jobs create http hourly-crypto-fetch-job \
  --location=us-central1 \
  --schedule="0 * * * *" \
  --uri=YOUR_CLOUD_FUNCTION_URL \
  --http-method=GET \
  --time-zone="America/New_York" \
  --project=molten-optics-310919
```

### 4. Manual Test

Test the scheduler job manually:

```bash
gcloud scheduler jobs run hourly-crypto-fetch-job --location=us-central1
```

Check the Cloud Function logs:

```bash
gcloud functions logs read hourly-crypto-fetcher \
  --region=us-central1 \
  --limit=50 \
  --project=molten-optics-310919
```

## BigQuery Table Schema

**Table**: `molten-optics-310919.kamiyabPakistan.crypto_hourly_data`

| Field | Type | Description |
|-------|------|-------------|
| pair | STRING | Kraken pair identifier |
| altname | STRING | Alternative name for the pair |
| base | STRING | Base currency |
| quote | STRING | Quote currency |
| timestamp | INTEGER | Unix timestamp |
| datetime | TIMESTAMP | Human-readable timestamp |
| open | FLOAT | Opening price |
| high | FLOAT | Highest price |
| low | FLOAT | Lowest price |
| close | FLOAT | Closing price |
| vwap | FLOAT | Volume-weighted average price |
| volume | FLOAT | Trading volume |
| count | INTEGER | Number of trades |
| fetched_at | TIMESTAMP | When the data was fetched |

## Schedule

- **Cron**: `0 * * * *` (Every hour at minute 0)
- **Timezone**: America/New_York
- **Example run times**: 1:00 AM, 2:00 AM, 3:00 AM, etc.

## Monitoring

### View Scheduler Jobs
```bash
gcloud scheduler jobs list --location=us-central1
```

### View Scheduler Job Details
```bash
gcloud scheduler jobs describe hourly-crypto-fetch-job --location=us-central1
```

### View Cloud Function Logs
```bash
gcloud functions logs read hourly-crypto-fetcher \
  --region=us-central1 \
  --limit=100 \
  --project=molten-optics-310919
```

### Query Recent Data in BigQuery
```sql
SELECT
  pair,
  datetime,
  close,
  volume,
  fetched_at
FROM `molten-optics-310919.kamiyabPakistan.crypto_hourly_data`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY datetime DESC, pair
LIMIT 100;
```

## Cost Estimates

- **Cloud Function**: ~$0.40/month (assuming 744 invocations/month)
- **Cloud Scheduler**: $0.10/month (1 job)
- **BigQuery Storage**: ~$0.02/month (1 GB of hourly data)
- **Total**: ~$0.52/month

## Troubleshooting

### Function Timeout
If the function times out, increase the timeout:
```bash
gcloud functions deploy hourly-crypto-fetcher --timeout=600s
```

### Memory Issues
If you get memory errors, increase memory:
```bash
gcloud functions deploy hourly-crypto-fetcher --memory=1024MB
```

### Check Logs
```bash
gcloud functions logs read hourly-crypto-fetcher --limit=50
```

### Pause Scheduler
```bash
gcloud scheduler jobs pause hourly-crypto-fetch-job --location=us-central1
```

### Resume Scheduler
```bash
gcloud scheduler jobs resume hourly-crypto-fetch-job --location=us-central1
```

### Delete Scheduler
```bash
gcloud scheduler jobs delete hourly-crypto-fetch-job --location=us-central1
```

## Data Deduplication

The function automatically removes duplicates based on `pair` and `timestamp` before uploading to BigQuery. If you need to deduplicate existing data in BigQuery:

```sql
CREATE OR REPLACE TABLE `molten-optics-310919.kamiyabPakistan.crypto_hourly_data` AS
SELECT * FROM (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY pair, timestamp ORDER BY fetched_at DESC) as rn
  FROM `molten-optics-310919.kamiyabPakistan.crypto_hourly_data`
)
WHERE rn = 1;
```
