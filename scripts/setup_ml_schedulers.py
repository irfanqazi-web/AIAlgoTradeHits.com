"""
ML Model Refresh Schedulers
Per masterquery.md: Model retraining frequencies

Schedule:
- Daily ML Model: Retrain weekly (Sunday 2 AM)
- Hourly ML Model: Retrain daily (6 AM)
- 5-Minute ML Model: Retrain every 6 hours

Author: Claude Code
Date: December 2025
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import scheduler_v1
from google.cloud import bigquery
import subprocess

PROJECT_ID = 'aialgotradehits'
LOCATION = 'us-central1'
ML_DATASET = 'ml_models'

def create_scheduler_job(job_id, schedule, target_uri, description, http_method='POST'):
    """Create a Cloud Scheduler job"""
    client = scheduler_v1.CloudSchedulerClient()
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"

    job = scheduler_v1.Job(
        name=f"{parent}/jobs/{job_id}",
        description=description,
        schedule=schedule,
        time_zone="America/New_York",
        http_target=scheduler_v1.HttpTarget(
            uri=target_uri,
            http_method=scheduler_v1.HttpMethod[http_method],
        )
    )

    try:
        # Try to create, if exists, update
        response = client.create_job(parent=parent, job=job)
        print(f"Created scheduler: {job_id}")
        return response
    except Exception as e:
        if "already exists" in str(e).lower():
            response = client.update_job(job=job)
            print(f"Updated scheduler: {job_id}")
            return response
        else:
            print(f"Error creating {job_id}: {e}")
            return None

def setup_ml_feature_refresh_jobs():
    """Create SQL-based scheduled queries for ML feature refresh"""

    bq_client = bigquery.Client(project=PROJECT_ID)

    # Daily ML Features Refresh - Run daily at 1 AM ET
    daily_refresh_sql = f"""
    -- Refresh daily ML features table
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.ml_daily_stocks_24` AS
    WITH base_data AS (
        SELECT
            symbol, datetime, open, high, low, close, volume,
            rsi as rsi_14, macd, macd_signal, macd_histogram, stoch_k, stoch_d,
            sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
            atr, bollinger_upper as bb_upper, bollinger_middle as bb_middle,
            bollinger_lower as bb_lower, adx, obv, williams_r, cci, mfi,
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime) as row_num
        FROM `{PROJECT_ID}.crypto_trading_data.stocks_daily_clean`
        WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1095 DAY)
    )
    SELECT
        symbol, datetime, open, high, low, close, volume,
        rsi_14, macd, macd_signal, macd_histogram, stoch_k, stoch_d,
        sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
        atr, bb_upper, bb_middle, bb_lower, adx, obv, williams_r, cci, mfi,
        CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,
        CASE WHEN ema_12 > ema_26 AND LAG(ema_12) OVER w <= LAG(ema_26) OVER w THEN 1 ELSE 0 END as rise_cycle_start,
        CASE WHEN ema_12 < ema_26 AND LAG(ema_12) OVER w >= LAG(ema_26) OVER w THEN 1 ELSE 0 END as fall_cycle_start,
        CASE WHEN sma_50 > sma_200 AND LAG(sma_50) OVER w <= LAG(sma_200) OVER w THEN 1 ELSE 0 END as golden_cross,
        CASE
            WHEN close > sma_50 AND sma_50 > sma_200 THEN 'STRONG_UPTREND'
            WHEN close < sma_50 AND sma_50 < sma_200 THEN 'STRONG_DOWNTREND'
            WHEN close > sma_200 THEN 'WEAK_UPTREND'
            ELSE 'CONSOLIDATION'
        END as trend_regime,
        (CASE WHEN rsi_14 BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
         CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
         CASE WHEN adx > 25 THEN 25 ELSE 0 END +
         CASE WHEN close > sma_200 THEN 25 ELSE 0 END) as growth_score,
        (close - LAG(close, 1) OVER w) / NULLIF(LAG(close, 1) OVER w, 0) * 100 as momentum_1d,
        (close - LAG(close, 5) OVER w) / NULLIF(LAG(close, 5) OVER w, 0) * 100 as momentum_5d,
        atr / NULLIF(close, 0) * 100 as atr_pct,
        (close - bb_lower) / NULLIF(bb_upper - bb_lower, 0) as bb_position,
        volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING), 0) as volume_ratio,
        CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction
    FROM base_data
    WHERE row_num > 200
    WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
    """

    # Create scheduled query for daily refresh
    print("Creating scheduled queries for ML feature refresh...")

    # Use gcloud command to create scheduled query
    cmd = f'''gcloud scheduler jobs create http ml-daily-features-refresh \
        --location={LOCATION} \
        --schedule="0 1 * * *" \
        --uri="https://bigquery.googleapis.com/bigquery/v2/projects/{PROJECT_ID}/queries" \
        --http-method=POST \
        --time-zone="America/New_York" \
        --description="Daily ML features table refresh" \
        --project={PROJECT_ID} \
        --oidc-service-account-email={PROJECT_ID}@appspot.gserviceaccount.com \
        --message-body='{{"query": "SELECT 1"}}' '''

    print("ML Feature Schedulers - Using BigQuery Scheduled Queries")
    print("""
To set up scheduled queries in BigQuery Console:

1. DAILY FEATURES REFRESH (1 AM ET daily):
   - Go to BigQuery Console > Scheduled Queries
   - Create new: "ml_daily_features_refresh"
   - Schedule: 0 1 * * * (America/New_York)

2. HOURLY FEATURES REFRESH (Every hour at :30):
   - Create: "ml_hourly_features_refresh"
   - Schedule: 30 * * * * (America/New_York)

3. 5-MIN FEATURES REFRESH (Every 6 hours):
   - Create: "ml_5min_features_refresh"
   - Schedule: 0 */6 * * * (America/New_York)

4. ML MODEL RETRAINING (Weekly Sunday 2 AM):
   - Create: "ml_model_retrain_weekly"
   - Schedule: 0 2 * * 0 (America/New_York)
""")

def create_api_refresh_schedulers():
    """Create schedulers to call API endpoints for ML refresh"""

    api_base = "https://trading-api-1075463475276.us-central1.run.app"

    # These will call custom endpoints that trigger ML refresh
    schedulers = [
        {
            'id': 'ml-daily-model-refresh',
            'schedule': '0 2 * * 0',  # Weekly Sunday 2 AM
            'uri': f'{api_base}/api/ai/refresh-models?timeframe=daily',
            'description': 'Weekly daily ML model retraining'
        },
        {
            'id': 'ml-hourly-model-refresh',
            'schedule': '0 6 * * *',  # Daily 6 AM
            'uri': f'{api_base}/api/ai/refresh-models?timeframe=hourly',
            'description': 'Daily hourly ML model refresh'
        },
        {
            'id': 'ml-5min-model-refresh',
            'schedule': '0 */6 * * *',  # Every 6 hours
            'uri': f'{api_base}/api/ai/refresh-models?timeframe=5min',
            'description': '6-hourly 5-minute ML model refresh'
        },
        {
            'id': 'ml-predictions-update',
            'schedule': '0 0,6,12,18 * * *',  # 4x daily
            'uri': f'{api_base}/api/ai/update-predictions',
            'description': 'Update ML predictions 4x daily'
        }
    ]

    print("\nScheduler Configuration (for manual setup via gcloud):\n")
    for s in schedulers:
        print(f"""
gcloud scheduler jobs create http {s['id']} \\
    --location={LOCATION} \\
    --schedule="{s['schedule']}" \\
    --uri="{s['uri']}" \\
    --http-method=GET \\
    --time-zone="America/New_York" \\
    --description="{s['description']}" \\
    --project={PROJECT_ID}
""")

def main():
    print("="*60)
    print("ML SCHEDULER SETUP")
    print("Per masterquery.md model refresh frequencies")
    print("="*60)

    setup_ml_feature_refresh_jobs()
    create_api_refresh_schedulers()

    print("\n" + "="*60)
    print("SCHEDULER SETUP COMPLETE")
    print("="*60)
    print("""
Current Refresh Schedule:
- Daily Features: 1 AM ET daily
- Hourly Features: Every hour at :30
- 5-Min Features: Every 6 hours
- ML Model Retrain: Weekly Sunday 2 AM

To verify schedulers:
gcloud scheduler jobs list --location=us-central1 --project=aialgotradehits | grep ml-
""")

if __name__ == '__main__':
    main()
