"""
Deploy Multi-Source Data Fetcher Cloud Function
Runs at 1 AM daily to fetch from all data sources
"""

import subprocess
import sys

PROJECT_ID = 'aialgotradehits'
REGION = 'us-central1'
FUNCTION_NAME = 'multi-source-fetcher'

def deploy():
    print("=" * 60)
    print("DEPLOYING MULTI-SOURCE DATA FETCHER")
    print("=" * 60)

    # Deploy command
    cmd = [
        'gcloud', 'functions', 'deploy', FUNCTION_NAME,
        '--project', PROJECT_ID,
        '--region', REGION,
        '--runtime', 'python311',
        '--trigger-http',
        '--allow-unauthenticated',
        '--entry-point', 'multi_source_fetcher',
        '--memory', '4096MB',
        '--timeout', '3600s',  # 1 hour timeout for full data fetch
        '--min-instances', '0',
        '--max-instances', '1',
        '--set-env-vars', f'GCP_PROJECT={PROJECT_ID}',
        '--source', '.'
    ]

    print(f"\nDeploying {FUNCTION_NAME}...")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("DEPLOYMENT SUCCESSFUL!")
        print("=" * 60)
        print(f"\nFunction URL: https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}")
        print(f"\nTo trigger manually:")
        print(f"  curl https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}")
    else:
        print("\n" + "=" * 60)
        print("DEPLOYMENT FAILED!")
        print("=" * 60)
        print(f"\nSTDOUT:\n{result.stdout}")
        print(f"\nSTDERR:\n{result.stderr}")
        sys.exit(1)

    return result.returncode == 0


def update_scheduler():
    """Update the 1 AM scheduler to use this function"""
    print("\n" + "=" * 60)
    print("UPDATING 1 AM SCHEDULER")
    print("=" * 60)

    scheduler_name = 'multi-source-daily-1am'
    function_url = f'https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}'

    # Delete existing scheduler if it exists
    delete_cmd = [
        'gcloud', 'scheduler', 'jobs', 'delete', scheduler_name,
        '--project', PROJECT_ID,
        '--location', REGION,
        '--quiet'
    ]
    subprocess.run(delete_cmd, capture_output=True)

    # Create new scheduler
    create_cmd = [
        'gcloud', 'scheduler', 'jobs', 'create', 'http', scheduler_name,
        '--project', PROJECT_ID,
        '--location', REGION,
        '--schedule', '0 1 * * *',  # 1 AM daily
        '--time-zone', 'America/New_York',
        '--uri', function_url,
        '--http-method', 'GET',
        '--attempt-deadline', '1800s',  # 30 min timeout
        '--description', 'Daily multi-source data fetch at 1 AM (TwelveData, Kraken, FRED, Finnhub, CoinMarketCap)'
    ]

    print(f"\nCreating scheduler: {scheduler_name}")
    result = subprocess.run(create_cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Scheduler created: {scheduler_name}")
        print(f"Schedule: 0 1 * * * (1 AM daily, America/New_York)")
    else:
        print(f"Scheduler creation failed: {result.stderr}")

    return result.returncode == 0


if __name__ == '__main__':
    if deploy():
        update_scheduler()
        print("\n" + "=" * 60)
        print("ALL DONE!")
        print("=" * 60)
        print("\nData Sources Integrated:")
        print("  1. TwelveData ($229/month) - Stocks, Crypto, ETFs, Forex")
        print("  2. Kraken Pro - Crypto OHLCV with Buy/Sell Volume")
        print("  3. FRED API - Economic Indicators")
        print("  4. Finnhub - Analyst Recommendations")
        print("  5. CoinMarketCap - Crypto Rankings")
        print("\nNew Fields Added:")
        print("  - buy_volume, sell_volume (from Kraken)")
        print("  - buy_count, sell_count (number of traders)")
        print("  - trade_count (total trades)")
        print("  - buy_sell_ratio, buy_pressure")
        print("  - sentiment_score (0.00 - 1.00)")
        print("  - recommendation (STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL)")
