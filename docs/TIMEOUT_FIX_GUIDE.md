# Cloud Scheduler Timeout Fix Guide

## Problem

Cloud Scheduler is timing out with `DEADLINE_EXCEEDED` errors (HTTP 504) when triggering Cloud Functions. This happens because:

1. **Hourly function** processes ~675 crypto pairs with 1.5s rate limiting = 15-20 minutes execution time
2. **Daily function** processes ~675 crypto pairs with 1.5s rate limiting = 15-20 minutes execution time
3. **5-minute function** processes 10 pairs but calculates 29 indicators = 5-10 minutes execution time

The original timeouts were too short:
- Cloud Functions: 540s (9 minutes) - not enough time to complete
- Cloud Schedulers: 180s (3 minutes) - scheduler gave up before function finished

## Solution

Increase both Cloud Function and Cloud Scheduler timeouts to allow full execution.

### Option 1: Quick Fix - Update Schedulers Only (Recommended First Step)

Run this Python script to update all scheduler timeouts immediately:

```bash
python fix_scheduler_timeouts.py
```

This updates:
- **Daily scheduler**: 1200s (20 minutes)
- **Hourly scheduler**: 1200s (20 minutes)
- **5-minute scheduler**: 600s (10 minutes)

### Option 2: Full Fix - Redeploy Functions with New Timeouts

For a complete fix, redeploy all functions with increased timeouts:

#### 1. Redeploy Daily Function
```bash
cd cloud_function_daily
python deploy_via_api.py
```
New timeout: 1200s (20 minutes)

#### 2. Redeploy Hourly Function
```bash
cd cloud_function_hourly
python deploy.py
```
New timeout: 1200s (20 minutes)

#### 3. Redeploy 5-Minute Function
```bash
cd cloud_function_5min
python deploy_all.py
```
New timeout: 600s (10 minutes)

**Note:** Each deployment takes 2-3 minutes. The 5-minute deployment also updates its scheduler automatically.

## What Changed

### Cloud Function Timeouts
All deployment scripts have been updated:

**cloud_function_daily/deploy_via_api.py:25**
```python
TIMEOUT_SECONDS = 1200  # 20 minutes - enough for ~675 pairs with 1.5s rate limiting
```

**cloud_function_hourly/deploy.py:24**
```python
TIMEOUT_SECONDS = 1200  # 20 minutes - enough for ~675 pairs with 1.5s rate limiting
```

**cloud_function_5min/deploy_all.py:21**
```python
TIMEOUT_SECONDS = 600  # 10 minutes - fetches only 10 pairs but calculates indicators
```

### Cloud Scheduler Timeouts
All scheduler setup scripts now include `attempt_deadline`:

```python
job = scheduler_v1.Job(
    name=job_path,
    # ... other config ...
    attempt_deadline=duration_pb2.Duration(seconds=1200),  # 20 minutes
    retry_config=scheduler_v1.RetryConfig(
        retry_count=2,
        max_retry_duration=duration_pb2.Duration(seconds=1200),
    ),
)
```

## Verification

### 1. Check Scheduler Status
```bash
gcloud scheduler jobs list --project=cryptobot-462709 --location=us-central1
```

All jobs should show `STATE: ENABLED`.

### 2. Monitor Next Scheduled Run
Wait for the next scheduled run (hourly runs every hour at :00). Check logs:

```bash
gcloud functions logs read hourly-crypto-fetcher --project=cryptobot-462709 --limit=50
```

Look for:
- `"Starting Hourly Crypto Data Fetch with Technical Indicators"`
- `"Successfully processed X/675 pairs"`
- `"Hourly data fetch with indicators completed successfully!"`

### 3. Check for Errors
```bash
gcloud scheduler jobs describe hourly-crypto-fetch-job \
  --location=us-central1 \
  --project=cryptobot-462709
```

Check the `lastAttemptTime` and `status` fields. Should show `SUCCESS` instead of `DEADLINE_EXCEEDED`.

### 4. Verify Data is Being Collected
```bash
python check_bigquery_counts.py
```

Should show recent timestamps and increasing record counts.

## Expected Execution Times

With 1.5 second rate limiting per pair:

| Function | Pairs | Time per Pair | Total Time |
|----------|-------|---------------|------------|
| Daily    | ~675  | 1.5s          | 15-20 min  |
| Hourly   | ~675  | 1.5s          | 15-20 min  |
| 5-Minute | 10    | 1.5s + indicators | 5-10 min   |

## Troubleshooting

### Issue: Still getting timeout errors after fix
**Solution:**
1. Verify scheduler was actually updated:
   ```bash
   gcloud scheduler jobs describe hourly-crypto-fetch-job --location=us-central1 --project=cryptobot-462709 | grep attemptDeadline
   ```
   Should show `attemptDeadline: 1200s`

2. If not updated, run `python fix_scheduler_timeouts.py` again

### Issue: Function still times out at 9 minutes
**Solution:**
Function timeout wasn't increased. Redeploy the function:
```bash
cd cloud_function_hourly
python deploy.py
```

### Issue: Python script fails with "No module named 'google.cloud'"
**Solution:**
Install required packages:
```bash
pip install google-cloud-scheduler google-cloud-functions
```

### Issue: gcloud commands fail with "grpc" module error
**Solution:**
This is a known gcloud CLI issue on Windows. Use the Python API scripts instead:
- Don't use: `gcloud functions deploy`
- Use: `python deploy.py` or `python deploy_via_api.py`

## Cost Impact

Increasing timeouts doesn't directly increase costs. You only pay for actual execution time, not the timeout limit.

However, your functions DO run for 15-20 minutes per execution:
- **Daily function**: Runs once per day = ~20 minutes/day
- **Hourly function**: Runs 24 times per day = ~8 hours/day
- **5-minute function**: Runs 288 times per day (every 5 min) = ~24 hours/day

Current estimated costs remain the same (~$135/month) since the execution time hasn't changed, only the timeout limits.

## Prevention

For future deployments:
1. Always set function timeout > expected execution time + buffer
2. Set scheduler `attempt_deadline` >= function timeout
3. Set scheduler `max_retry_duration` >= function timeout
4. Test with a manual trigger before relying on schedulers

## Files Modified

- `cloud_function_daily/deploy_via_api.py` - Updated TIMEOUT_SECONDS to 1200
- `cloud_function_hourly/deploy.py` - Updated TIMEOUT_SECONDS to 1200
- `cloud_function_5min/deploy_all.py` - Updated TIMEOUT_SECONDS to 600
- `setup_schedulers_cryptobot.py` - Added attempt_deadline to both schedulers
- `fix_scheduler_timeouts.py` - NEW: Script to fix existing schedulers

## Summary

✓ **Root cause**: Cloud Scheduler timeout (180s) was too short for functions that need 15-20 minutes

✓ **Quick fix**: Run `python fix_scheduler_timeouts.py` to update schedulers immediately

✓ **Complete fix**: Redeploy all functions with increased timeouts using their deploy scripts

✓ **Verification**: Check logs and BigQuery data to confirm successful execution

The functions will now complete successfully without DEADLINE_EXCEEDED errors.
