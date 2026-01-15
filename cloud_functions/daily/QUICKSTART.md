# Quick Start Guide - Daily Crypto Data Fetcher

## What This Does

Automatically downloads daily OHLCV data for ~675 cryptocurrencies from Kraken Pro API every night at midnight and appends it to your BigQuery historical database.

## 3-Step Deployment

### Step 1: Deploy the Function (2 minutes)

```bash
cd cloud_function_daily
./deploy.sh
```

Copy the Function URL from the output (it looks like this):
```
https://us-central1-molten-optics-310919.cloudfunctions.net/daily-crypto-fetcher
```

### Step 2: Update Scheduler Script (30 seconds)

Open `setup_scheduler.sh` and replace `YOUR_CLOUD_FUNCTION_URL` with the URL you just copied.

### Step 3: Deploy the Scheduler (1 minute)

```bash
./setup_scheduler.sh
```

## Done! 🎉

Your system is now fetching crypto data daily at midnight.

## Verify It's Working

Test it manually:
```bash
gcloud scheduler jobs run daily-crypto-fetch-job --location=us-central1
```

Check the data in BigQuery:
```sql
SELECT COUNT(*), DATE(datetime)
FROM `molten-optics-310919.kamiyabPakistan.crypto_analysis`
GROUP BY DATE(datetime)
ORDER BY DATE(datetime) DESC
LIMIT 5;
```

## Common Commands

**View logs:**
```bash
gcloud functions logs read daily-crypto-fetcher --limit=50
```

**Check scheduler status:**
```bash
gcloud scheduler jobs describe daily-crypto-fetch-job --location=us-central1
```

**Pause/Resume:**
```bash
gcloud scheduler jobs pause daily-crypto-fetch-job --location=us-central1
gcloud scheduler jobs resume daily-crypto-fetch-job --location=us-central1
```

## What Happens Every Night

1. **00:00 ET** - Cloud Scheduler triggers the function
2. **00:00-00:09 ET** - Function fetches data from Kraken for ~675 pairs
3. **00:09-00:10 ET** - Data is appended to BigQuery (duplicates removed)
4. **Result** - ~675 new daily records in your database

## Cost

~$4-7 per month total

## Need Help?

See `DEPLOYMENT_INSTRUCTIONS.md` for detailed troubleshooting.
