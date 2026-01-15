# Manual Deployment Guide (Using GCP Console)

Since there's an issue with the gcloud CLI, here's how to deploy using the Google Cloud Console web interface.

## Step 1: Access Google Cloud Console

1. Open your web browser
2. Go to: https://console.cloud.google.com
3. Select project: `molten-optics-310919`

## Step 2: Deploy Cloud Function via Console

1. In the Google Cloud Console, go to **Cloud Functions**
   - URL: https://console.cloud.google.com/functions/list?project=molten-optics-310919

2. Click **CREATE FUNCTION** button

3. Configure the function:

   **Environment:**
   - Select `2nd gen`

   **Function name:**
   ```
   daily-crypto-fetcher
   ```

   **Region:**
   ```
   us-central1
   ```

   **Trigger:**
   - Trigger type: `HTTP`
   - Authentication: `Allow unauthenticated invocations` ✓

   Click **SAVE** and then **NEXT**

4. Configure the runtime:

   **Runtime:**
   ```
   Python 3.13
   ```

   **Entry point:**
   ```
   daily_crypto_fetch
   ```

   **Source code:**
   - Select `Inline Editor`

5. Copy the source files:

   **main.py** tab:
   - Open the file: `C:\Users\irfan\OneDrive - Aretec, Inc\Desktop\1AITrading\Trading\cloud_function_daily\main.py`
   - Copy ALL content
   - Paste into the `main.py` tab in the console

   **requirements.txt** tab:
   - Open the file: `C:\Users\irfan\OneDrive - Aretec, Inc\Desktop\1AITrading\Trading\cloud_function_daily\requirements.txt`
   - Copy ALL content
   - Paste into the `requirements.txt` tab in the console

6. Configure runtime settings:

   Click on **RUNTIME, BUILD, CONNECTIONS AND SECURITY SETTINGS** to expand

   **Memory allocated:**
   ```
   512 MiB
   ```

   **Timeout:**
   ```
   540 seconds
   ```

   **Maximum number of instances:**
   ```
   10
   ```

7. Click **DEPLOY** button

8. Wait for deployment (2-3 minutes)

9. Once deployed, copy the **Trigger URL** (it will look like):
   ```
   https://us-central1-molten-optics-310919.cloudfunctions.net/daily-crypto-fetcher
   ```

## Step 3: Set Up Cloud Scheduler via Console

1. In Google Cloud Console, go to **Cloud Scheduler**
   - URL: https://console.cloud.google.com/cloudscheduler?project=molten-optics-310919

2. Click **CREATE JOB**

3. Configure the scheduler job:

   **Define the schedule:**

   **Name:**
   ```
   daily-crypto-fetch-job
   ```

   **Region:**
   ```
   us-central1
   ```

   **Description:**
   ```
   Daily midnight job to fetch crypto OHLCV data from Kraken
   ```

   **Frequency** (cron format):
   ```
   0 0 * * *
   ```

   **Timezone:**
   ```
   America/New_York
   ```

   Click **CONTINUE**

4. Configure the execution:

   **Target type:**
   ```
   HTTP
   ```

   **URL:**
   ```
   [PASTE YOUR FUNCTION URL FROM STEP 2.9 HERE]
   ```

   **HTTP method:**
   ```
   GET
   ```

   **Auth header:**
   ```
   Add OIDC token
   ```

   **Service account:**
   ```
   Use the default compute service account
   ```

   Click **CONTINUE**

5. Configure retry settings (optional):

   **Max retry attempts:**
   ```
   3
   ```

   **Max retry duration:**
   ```
   600 seconds
   ```

   Click **CREATE**

## Step 4: Test the Deployment

1. In the Cloud Scheduler page, find your job `daily-crypto-fetch-job`

2. Click the **RUN NOW** button (⏵) to test

3. Check the execution:
   - Go to Cloud Functions
   - Click on `daily-crypto-fetcher`
   - Go to **LOGS** tab
   - Watch for successful execution

## Step 5: Verify Data in BigQuery

1. Go to BigQuery Console
   - URL: https://console.cloud.google.com/bigquery?project=molten-optics-310919

2. Run this query:

```sql
SELECT
  DATE(datetime) as date,
  COUNT(*) as num_records,
  COUNT(DISTINCT pair) as num_pairs
FROM `molten-optics-310919.kamiyabPakistan.crypto_analysis`
GROUP BY DATE(datetime)
ORDER BY date DESC
LIMIT 5;
```

3. You should see new data being added!

## Alternative: Fix gcloud CLI and Use Command Line

If you want to fix the gcloud CLI issue:

1. Run this command in PowerShell as Administrator:
   ```powershell
   pip install grpcio grpcio-tools protobuf
   ```

2. Or reinstall gcloud components:
   ```bash
   gcloud components reinstall
   ```

3. Then try the deployment script again:
   ```bash
   cd "C:\Users\irfan\OneDrive - Aretec, Inc\Desktop\1AITrading\Trading\cloud_function_daily"
   deploy.bat
   ```

## Monitoring After Deployment

### View Cloud Function Logs

```bash
gcloud functions logs read daily-crypto-fetcher --limit=50
```

Or via Console:
- Go to Cloud Functions → daily-crypto-fetcher → LOGS tab

### View Scheduler Job Status

```bash
gcloud scheduler jobs describe daily-crypto-fetch-job --location=us-central1
```

Or via Console:
- Go to Cloud Scheduler → daily-crypto-fetch-job

### Pause/Resume Scheduler

```bash
# Pause
gcloud scheduler jobs pause daily-crypto-fetch-job --location=us-central1

# Resume
gcloud scheduler jobs resume daily-crypto-fetch-job --location=us-central1
```

Or via Console:
- Go to Cloud Scheduler → daily-crypto-fetch-job → PAUSE/RESUME button

## Troubleshooting

### Function Fails to Deploy

- Check that Python 3.13 runtime is selected
- Verify all code is copied correctly
- Check quotas and billing are enabled

### Scheduler Doesn't Trigger

- Verify the Function URL is correct
- Check that OIDC authentication is configured
- Ensure the job is in ENABLED state

### No Data in BigQuery

- Check Cloud Function logs for errors
- Verify Kraken API is accessible
- Check BigQuery table permissions

## Summary

Once deployed:
- ✅ Cloud Function runs at midnight Eastern Time daily
- ✅ Fetches ~675 cryptocurrency pairs from Kraken
- ✅ Appends new daily data to BigQuery
- ✅ Handles duplicates automatically
- ✅ Costs ~$4-7 per month

The automated daily crypto data fetcher is now operational!
