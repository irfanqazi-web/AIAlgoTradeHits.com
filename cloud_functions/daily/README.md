# Daily Kraken Crypto Data Fetcher - Google Cloud Function

This Cloud Function fetches daily OHLCV (Open, High, Low, Close, Volume) data from Kraken Pro API for ~675 USD cryptocurrency trading pairs and appends the data to the historical BigQuery table.

## Overview

- **Function Name**: `daily-crypto-fetcher`
- **Schedule**: Runs daily at midnight (00:00 Eastern Time)
- **Data Source**: Kraken Pro Public API
- **Destination**: BigQuery table `molten-optics-310919.kamiyabPakistan.crypto_analysis`
- **Pairs Covered**: ~675 USD trading pairs
- **Interval**: Daily (1440-minute candles)

## Features

- ✅ Fetches daily OHLC data for all USD crypto pairs from Kraken
- ✅ Automatically appends to historical BigQuery table
- ✅ Duplicate detection and prevention
- ✅ Robust error handling and logging
- ✅ Rate limiting to comply with Kraken API limits
- ✅ Automatic retry logic for failed pairs

## BigQuery Table Schema

The data is appended to the `crypto_analysis` table with the following schema:

| Field | Type | Description |
|-------|------|-------------|
| pair | STRING | Trading pair (e.g., BTCUSD) |
| altname | STRING | Alternative pair name |
| base | STRING | Base currency |
| quote | STRING | Quote currency |
| timestamp | INTEGER | Unix timestamp |
| datetime | TIMESTAMP | Date and time |
| open | FLOAT | Opening price |
| high | FLOAT | Highest price |
| low | FLOAT | Lowest price |
| close | FLOAT | Closing price |
| vwap | FLOAT | Volume-weighted average price |
| volume | FLOAT | Trading volume |
| count | INTEGER | Number of trades |

## Deployment Instructions

### Prerequisites

1. Google Cloud SDK installed and configured
2. Active GCP project: `molten-optics-310919`
3. BigQuery dataset: `kamiyabPakistan` with table `crypto_analysis`
4. Proper IAM permissions for Cloud Functions and Cloud Scheduler

### Step 1: Deploy the Cloud Function

```bash
cd cloud_function_daily
chmod +x deploy.sh
./deploy.sh
```

This will:
- Deploy the Cloud Function to Google Cloud
- Set up HTTP trigger
- Configure timeout (540s) and memory (512MB)
- Output the Function URL

**Important**: Copy the Function URL from the output!

### Step 2: Set Up Cloud Scheduler

1. Edit `setup_scheduler.sh` and replace `YOUR_CLOUD_FUNCTION_URL` with the actual Function URL from Step 1

2. Run the scheduler setup:

```bash
chmod +x setup_scheduler.sh
./setup_scheduler.sh
```

This will create a Cloud Scheduler job that triggers the function daily at midnight Eastern Time.

### Step 3: Verify Setup

Check if the scheduler job was created:

```bash
gcloud scheduler jobs list --location=us-central1
```

View job details:

```bash
gcloud scheduler jobs describe daily-crypto-fetch-job --location=us-central1
```

## Testing

### Test Locally

```bash
python main.py
```

### Trigger Manually via Cloud Scheduler

```bash
gcloud scheduler jobs run daily-crypto-fetch-job --location=us-central1
```

### Test Cloud Function Directly

```bash
curl https://YOUR_FUNCTION_URL
```

## Monitoring

### View Logs

```bash
gcloud functions logs read daily-crypto-fetcher --limit=50
```

### Check Scheduler Job History

```bash
gcloud scheduler jobs describe daily-crypto-fetch-job --location=us-central1
```

### BigQuery Verification

Query the table to verify data is being appended:

```sql
SELECT
  DATE(datetime) as date,
  COUNT(*) as num_records,
  COUNT(DISTINCT pair) as num_pairs
FROM `molten-optics-310919.kamiyabPakistan.crypto_analysis`
GROUP BY DATE(datetime)
ORDER BY date DESC
LIMIT 10;
```

## Cost Estimates

- **Cloud Function**: ~$0.10-0.20 per day (based on 540s execution time daily)
- **Cloud Scheduler**: $0.10 per month for 1 job
- **BigQuery Storage**: Minimal (incremental daily data)
- **BigQuery Queries**: Based on usage

**Total Estimated Cost**: ~$3-6 per month

## Troubleshooting

### Function Timeout

If the function times out before completing all pairs:
- Increase timeout in `deploy.sh` (max 540s for HTTP functions)
- Consider breaking into smaller batches

### API Rate Limiting

The function includes 1.5-second delays between API calls to respect Kraken's rate limits. If you encounter rate limit errors:
- Increase sleep time in `main.py` (line 91)
- Check Kraken API status

### Duplicate Data

The function includes duplicate detection. If you see duplicates in BigQuery:
- Check the deduplication query in `main.py` (lines 140-160)
- Manually remove duplicates:

```sql
CREATE OR REPLACE TABLE `molten-optics-310919.kamiyabPakistan.crypto_analysis` AS
SELECT DISTINCT *
FROM `molten-optics-310919.kamiyabPakistan.crypto_analysis`;
```

## Data Freshness

- **Schedule**: Daily at 00:00 ET
- **Data Window**: Fetches last 3 days to ensure complete daily candles
- **Pairs**: ~675 USD trading pairs
- **Expected Records**: ~675 new records per day

## Maintenance

### Update Trading Pairs

The function automatically fetches all active USD pairs from Kraken, so no manual updates needed when new pairs are added.

### Modify Schedule

To change the schedule, update the `--schedule` parameter in `setup_scheduler.sh`:

```bash
--schedule="0 0 * * *"  # Daily at midnight
--schedule="0 */6 * * *"  # Every 6 hours
--schedule="0 12 * * 0"  # Weekly on Sunday at noon
```

Then re-run the setup script.

### Pause/Resume

Pause the scheduler:
```bash
gcloud scheduler jobs pause daily-crypto-fetch-job --location=us-central1
```

Resume the scheduler:
```bash
gcloud scheduler jobs resume daily-crypto-fetch-job --location=us-central1
```

## Architecture

```
┌─────────────────────┐
│  Cloud Scheduler    │
│  (Daily @ Midnight) │
└──────────┬──────────┘
           │ HTTP Trigger
           ▼
┌─────────────────────┐
│  Cloud Function     │
│  daily-crypto-      │
│  fetcher            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐      ┌─────────────────────┐
│  Kraken Pro API     │      │  BigQuery           │
│  ~675 USD Pairs     │─────▶│  crypto_analysis    │
│  Daily OHLC Data    │      │  Historical Table   │
└─────────────────────┘      └─────────────────────┘
```

## Support

For issues or questions:
- Check Cloud Function logs
- Verify Cloud Scheduler job status
- Review BigQuery table for data integrity
- Check Kraken API status at https://status.kraken.com

## License

This code is part of the AI Trading application project.
