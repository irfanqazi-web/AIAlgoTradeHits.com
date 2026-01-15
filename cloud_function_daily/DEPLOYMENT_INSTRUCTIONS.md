# Step-by-Step Deployment Instructions

## Quick Start (5 Minutes)

### 1. Navigate to the Directory

```bash
cd "C:\Users\irfan\OneDrive - Aretec, Inc\Desktop\1AITrading\Trading\cloud_function_daily"
```

### 2. Deploy the Cloud Function

```bash
chmod +x deploy.sh
./deploy.sh
```

**Expected Output:**
```
Deploying function...
✓ Function deployed successfully!
Function URL: https://us-central1-molten-optics-310919.cloudfunctions.net/daily-crypto-fetcher
```

**⚠️ IMPORTANT**: Copy the Function URL from the output!

### 3. Configure the Scheduler

Edit `setup_scheduler.sh` and replace the URL:

```bash
# Change this line:
FUNCTION_URL="YOUR_CLOUD_FUNCTION_URL"

# To (using your copied URL):
FUNCTION_URL="https://us-central1-molten-optics-310919.cloudfunctions.net/daily-crypto-fetcher"
```

### 4. Deploy the Scheduler

```bash
chmod +x setup_scheduler.sh
./setup_scheduler.sh
```

**Expected Output:**
```
✓ Cloud Scheduler job created successfully!
Job will run daily at midnight (00:00) Eastern Time
```

### 5. Test the Setup

Trigger a manual run to verify everything works:

```bash
gcloud scheduler jobs run daily-crypto-fetch-job --location=us-central1
```

### 6. Verify Data in BigQuery

Go to BigQuery and run:

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

You should see new data with today's date!

---

## Detailed Deployment Steps

### Prerequisites Check

1. **Google Cloud SDK Installed**
   ```bash
   gcloud --version
   ```
   If not installed, download from: https://cloud.google.com/sdk/docs/install

2. **Authentication**
   ```bash
   gcloud auth login
   gcloud config set project molten-optics-310919
   ```

3. **Enable Required APIs**
   ```bash
   gcloud services enable cloudfunctions.googleapis.com
   gcloud services enable cloudscheduler.googleapis.com
   gcloud services enable bigquery.googleapis.com
   ```

4. **Verify BigQuery Table Exists**
   ```bash
   bq show molten-optics-310919:kamiyabPakistan.crypto_analysis
   ```

### Deployment Process

#### Step 1: Review the Code

Check `main.py` to ensure configuration is correct:

```python
PROJECT_ID = 'molten-optics-310919'
DATASET_ID = 'kamiyabPakistan'
TABLE_ID = 'crypto_analysis'
```

#### Step 2: Deploy Cloud Function

Option A - Using the script (recommended):
```bash
./deploy.sh
```

Option B - Manual deployment:
```bash
gcloud functions deploy daily-crypto-fetcher \
  --gen2 \
  --runtime=python313 \
  --region=us-central1 \
  --source=. \
  --entry-point=daily_crypto_fetch \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=540s \
  --memory=512MB \
  --project=molten-optics-310919
```

Wait for deployment to complete (2-3 minutes).

#### Step 3: Get Function URL

If you missed the URL in the output, retrieve it:

```bash
gcloud functions describe daily-crypto-fetcher \
  --region=us-central1 \
  --format="value(serviceConfig.uri)"
```

#### Step 4: Update Scheduler Script

Edit `setup_scheduler.sh`:

```bash
nano setup_scheduler.sh
# or
notepad setup_scheduler.sh
```

Update the `FUNCTION_URL` variable with your actual URL.

#### Step 5: Create Scheduler Job

```bash
./setup_scheduler.sh
```

#### Step 6: Verify Scheduler

```bash
gcloud scheduler jobs list --location=us-central1
```

You should see `daily-crypto-fetch-job` with state `ENABLED`.

### Testing

#### Test 1: Manual Trigger

```bash
gcloud scheduler jobs run daily-crypto-fetch-job --location=us-central1
```

#### Test 2: Check Logs

```bash
gcloud functions logs read daily-crypto-fetcher --limit=100
```

Look for:
- "Starting Daily Crypto Data Fetch"
- "Successfully fetched data from XXX pairs"
- "Successfully appended XXX records to BigQuery"

#### Test 3: Verify BigQuery Data

```sql
-- Check most recent data
SELECT *
FROM `molten-optics-310919.kamiyabPakistan.crypto_analysis`
WHERE DATE(datetime) = CURRENT_DATE()
LIMIT 10;

-- Check data completeness
SELECT
  DATE(datetime) as date,
  COUNT(*) as records,
  COUNT(DISTINCT pair) as pairs
FROM `molten-optics-310919.kamiyabPakistan.crypto_analysis`
GROUP BY date
ORDER BY date DESC
LIMIT 10;
```

### Monitoring Setup

#### Set Up Log-Based Alerts (Optional)

Create an alert for function failures:

```bash
# This creates a notification when the function fails
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_NOTIFICATION_CHANNEL \
  --display-name="Daily Crypto Fetch Failures" \
  --condition-display-name="Function Error Rate" \
  --condition-threshold-value=1 \
  --condition-threshold-duration=60s
```

#### View Execution History

```bash
gcloud scheduler jobs describe daily-crypto-fetch-job \
  --location=us-central1 \
  --format="table(state, schedule, lastAttemptTime, status)"
```

### Customization

#### Change Schedule Time

Edit `setup_scheduler.sh` and modify the schedule:

```bash
# Midnight Eastern Time (default)
--schedule="0 0 * * *"

# 6 AM Eastern Time
--schedule="0 6 * * *"

# Twice daily (midnight and noon)
--schedule="0 0,12 * * *"
```

Then update the job:
```bash
gcloud scheduler jobs update http daily-crypto-fetch-job \
  --location=us-central1 \
  --schedule="0 6 * * *"
```

#### Change Timezone

```bash
gcloud scheduler jobs update http daily-crypto-fetch-job \
  --location=us-central1 \
  --time-zone="America/Los_Angeles"  # Pacific Time
```

Available timezones: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

#### Increase Timeout

If the function times out, edit `deploy.sh`:

```bash
--timeout=540s  # Change to maximum for HTTP functions
```

Then redeploy:
```bash
./deploy.sh
```

### Troubleshooting

#### Problem: "Permission denied" errors

**Solution:**
```bash
# Grant necessary permissions
gcloud projects add-iam-policy-binding molten-optics-310919 \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/cloudfunctions.admin"

gcloud projects add-iam-policy-binding molten-optics-310919 \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/cloudscheduler.admin"
```

#### Problem: Function times out

**Solution:**
- Check logs: `gcloud functions logs read daily-crypto-fetcher --limit=100`
- Increase timeout in `deploy.sh` (max 540s)
- Reduce the number of pairs being fetched

#### Problem: "Table not found" error

**Solution:**
```bash
# Verify table exists
bq show molten-optics-310919:kamiyabPakistan.crypto_analysis

# If not, create it using your historical data script
python upload_to_bigquery.py
```

#### Problem: Duplicate data in BigQuery

**Solution:**
The function has built-in duplicate detection. If you still see duplicates:

```sql
-- Remove duplicates
CREATE OR REPLACE TABLE `molten-optics-310919.kamiyabPakistan.crypto_analysis` AS
SELECT DISTINCT *
FROM `molten-optics-310919.kamiyabPakistan.crypto_analysis`;
```

#### Problem: Scheduler not triggering

**Solution:**
```bash
# Check job status
gcloud scheduler jobs describe daily-crypto-fetch-job --location=us-central1

# If paused, resume it
gcloud scheduler jobs resume daily-crypto-fetch-job --location=us-central1

# Delete and recreate if needed
gcloud scheduler jobs delete daily-crypto-fetch-job --location=us-central1
./setup_scheduler.sh
```

### Maintenance

#### View Recent Logs

```bash
# Last 50 lines
gcloud functions logs read daily-crypto-fetcher --limit=50

# Logs from last 24 hours
gcloud functions logs read daily-crypto-fetcher \
  --start-time="2025-01-09T00:00:00Z"
```

#### Update Function Code

After modifying `main.py`:

```bash
./deploy.sh
```

No need to update the scheduler.

#### Pause Scheduled Runs

```bash
# Pause
gcloud scheduler jobs pause daily-crypto-fetch-job --location=us-central1

# Resume
gcloud scheduler jobs resume daily-crypto-fetch-job --location=us-central1
```

#### Delete Everything

```bash
# Delete function
gcloud functions delete daily-crypto-fetcher --region=us-central1

# Delete scheduler job
gcloud scheduler jobs delete daily-crypto-fetch-job --location=us-central1
```

### Cost Monitoring

#### View Current Costs

```bash
# Install billing API
gcloud services enable cloudbilling.googleapis.com

# View costs (via Cloud Console)
# https://console.cloud.google.com/billing
```

#### Estimated Monthly Costs

- Cloud Function: $3-6/month (540s daily execution)
- Cloud Scheduler: $0.10/month (1 job)
- BigQuery Storage: ~$0.50/month (incremental daily data)
- **Total: ~$4-7/month**

### Next Steps

1. ✅ Deploy function
2. ✅ Set up scheduler
3. ✅ Test manually
4. ✅ Verify data in BigQuery
5. Monitor for a week
6. Set up alerting (optional)
7. Document any customizations

### Support Resources

- Cloud Functions Docs: https://cloud.google.com/functions/docs
- Cloud Scheduler Docs: https://cloud.google.com/scheduler/docs
- Kraken API Docs: https://docs.kraken.com/rest/
- BigQuery Docs: https://cloud.google.com/bigquery/docs

### Emergency Contacts

If something goes wrong:
1. Check Cloud Function logs
2. Check Scheduler execution history
3. Verify Kraken API status: https://status.kraken.com
4. Check BigQuery table integrity

---

**Deployment Complete!** 🎉

Your daily crypto data fetcher is now running automatically at midnight Eastern Time every day.
