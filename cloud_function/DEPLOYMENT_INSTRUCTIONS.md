# Cloud Function Deployment Instructions

You have two options to deploy the Cloud Function:

## Option 1: Deploy via Google Cloud Console (Web Interface) - RECOMMENDED

### Step 1: Open Google Cloud Console
1. Go to https://console.cloud.google.com
2. Select project: **molten-optics-310919**

### Step 2: Navigate to Cloud Functions
1. In the left menu, go to **Cloud Functions**
2. Click **CREATE FUNCTION** button

### Step 3: Configure Function Basics
Fill in the following details:

**Basics:**
- Environment: **2nd gen**
- Function name: `hourly-crypto-fetcher`
- Region: `us-central1`

**Trigger:**
- Trigger type: **HTTPS**
- Authentication: **Allow unauthenticated invocations** (check the box)
- Click **SAVE**

**Runtime, build, connections and security settings:**
- Memory allocated: **512 MiB**
- Timeout: **540 seconds**
- Maximum instances: **1** (to avoid concurrent runs)
- Click **NEXT**

### Step 4: Upload Code

**Runtime:** Select `Python 3.13`

**Entry point:** Enter `hourly_crypto_fetch`

**Source code:** Choose **ZIP upload** or **Inline editor**

#### Method A: ZIP Upload
1. Create a ZIP file containing:
   - `main.py` (from cloud_function folder)
   - `requirements.txt` (from cloud_function folder)
2. Upload the ZIP file

#### Method B: Inline Editor
1. Click on `main.py` in the editor
2. Copy and paste the entire contents from `cloud_function/main.py`
3. Click on `requirements.txt` in the editor
4. Copy and paste the contents from `cloud_function/requirements.txt`

### Step 5: Deploy
1. Click **DEPLOY** button
2. Wait 3-5 minutes for deployment to complete
3. **COPY THE TRIGGER URL** - you'll need this for the scheduler!

---

## Option 2: Deploy via Command Line (requires gcloud SDK)

### Step 1: Install Google Cloud SDK
Download and install from: https://cloud.google.com/sdk/docs/install

For Windows:
1. Download the installer: https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe
2. Run the installer
3. Follow the installation wizard
4. Initialize: `gcloud init`
5. Login: `gcloud auth login`

### Step 2: Deploy Function
```bash
cd cloud_function

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
  --max-instances=1 \
  --project=molten-optics-310919
```

---

## After Deployment - Setup Cloud Scheduler

### Via Google Cloud Console:

1. Go to **Cloud Scheduler** in the left menu
2. Click **CREATE JOB**

**Define the schedule:**
- Name: `hourly-crypto-fetch-job`
- Region: `us-central1`
- Frequency (cron): `0 * * * *`
- Timezone: `America/New_York (EST/EDT)`

**Configure the execution:**
- Target type: **HTTP**
- URL: **[PASTE YOUR CLOUD FUNCTION TRIGGER URL]**
- HTTP method: **GET**
- Auth header: **None** (since function allows unauthenticated)

3. Click **CREATE**

### Via Command Line:

```bash
gcloud scheduler jobs create http hourly-crypto-fetch-job \
  --location=us-central1 \
  --schedule="0 * * * *" \
  --uri=YOUR_CLOUD_FUNCTION_URL \
  --http-method=GET \
  --time-zone="America/New_York" \
  --project=molten-optics-310919
```

---

## Testing the Deployment

### Test the Cloud Function manually:

**Via Console:**
1. Go to Cloud Functions
2. Click on `hourly-crypto-fetcher`
3. Go to **TESTING** tab
4. Click **TEST THE FUNCTION**
5. Check logs for execution

**Via URL:**
Open the Trigger URL in your browser - you should see:
```
Hourly crypto data fetch completed
```

### Test the Scheduler:

**Via Console:**
1. Go to Cloud Scheduler
2. Find `hourly-crypto-fetch-job`
3. Click **RUN NOW**
4. Go to Cloud Functions logs to verify execution

**Via Command Line:**
```bash
gcloud scheduler jobs run hourly-crypto-fetch-job --location=us-central1
```

---

## Verify Data in BigQuery

After the function runs successfully, verify the data:

```sql
SELECT
  COUNT(*) as total_records,
  COUNT(DISTINCT pair) as unique_pairs,
  MIN(datetime) as earliest_record,
  MAX(datetime) as latest_record
FROM `molten-optics-310919.kamiyabPakistan.crypto_hourly_data`;
```

Expected first run: ~635 records (one per pair)

---

## Monitoring

### View Logs:
- **Console**: Cloud Functions → hourly-crypto-fetcher → LOGS tab
- **Command**: `gcloud functions logs read hourly-crypto-fetcher --limit=50`

### View Scheduler Status:
- **Console**: Cloud Scheduler → hourly-crypto-fetch-job
- **Command**: `gcloud scheduler jobs describe hourly-crypto-fetch-job --location=us-central1`

---

## Troubleshooting

**Function timeout:**
- Increase timeout to 600s in function configuration

**Out of memory:**
- Increase memory to 1024MB in function configuration

**Rate limiting:**
- The function already includes 1.5s delays between API calls
- This should stay within Kraken's limits

**Duplicate data:**
- The function automatically deduplicates before upload
- Use the SQL in README.md to deduplicate existing data if needed

---

## Important Notes

1. **First run will take ~15-20 minutes** due to API rate limiting (635 pairs × 1.5 seconds each)
2. **Set max instances to 1** to prevent multiple concurrent executions
3. **Monitor costs** in Google Cloud Console → Billing
4. **The BigQuery table will be created automatically** on first run
5. **Data is appended**, not replaced, so you'll build a historical dataset over time
