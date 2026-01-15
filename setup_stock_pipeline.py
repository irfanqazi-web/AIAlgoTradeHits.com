"""
Complete Setup Script for Stock Data Pipeline
1. Creates BigQuery table
2. Fetches 6 months historical data
3. Uploads to BigQuery with indicators
4. Deploys Cloud Function
5. Sets up Cloud Scheduler
"""

import subprocess
import sys
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'

def run_script(script_name, description):
    """Run a Python script and return success status"""

    logger.info(f"\n{'='*70}")
    logger.info(f"{description}")
    logger.info(f"{'='*70}\n")

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(result.stdout)
        logger.info(f"✓ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ {description} failed!")
        logger.error(f"Error: {e}")
        logger.error(f"Output: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        return False

def main():
    """Main setup function"""

    logger.info("\n" + "="*70)
    logger.info("STOCK DATA PIPELINE - COMPLETE SETUP")
    logger.info("="*70)
    logger.info(f"\nProject: {PROJECT_ID}")
    logger.info(f"Region: {REGION}")
    logger.info(f"\nThis script will:")
    logger.info("  1. Create BigQuery stock_analysis table")
    logger.info("  2. Fetch 6 months of historical stock data")
    logger.info("  3. Upload historical data with Elliott Wave & Fibonacci indicators")
    logger.info("  4. Deploy daily stock Cloud Function")
    logger.info("  5. Set up Cloud Scheduler for daily updates")
    logger.info("\n" + "="*70)

    input("\nPress Enter to continue...")

    # Step 1: Create BigQuery table
    if not run_script('create_stock_bigquery_schema.py', 'STEP 1: Creating BigQuery Table'):
        logger.error("Failed to create BigQuery table. Exiting...")
        return False

    time.sleep(2)

    # Step 2: Fetch historical data
    logger.info(f"\n{'='*70}")
    logger.info("STEP 2: Fetching 6 Months Historical Data")
    logger.info(f"{'='*70}\n")
    logger.info("Installing yfinance if needed...")

    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'yfinance'],
                      capture_output=True, check=True)
    except:
        pass

    if not run_script('stock_data_fetcher_6months.py', 'Fetching Historical Stock Data'):
        logger.error("Failed to fetch historical data. Exiting...")
        return False

    time.sleep(2)

    # Step 3: Upload to BigQuery
    if not run_script('upload_stocks_to_bigquery.py', 'STEP 3: Uploading to BigQuery'):
        logger.error("Failed to upload to BigQuery. Exiting...")
        return False

    time.sleep(2)

    # Step 4: Deploy Cloud Function
    logger.info(f"\n{'='*70}")
    logger.info("STEP 4: Deploying Daily Stock Cloud Function")
    logger.info(f"{'='*70}\n")

    try:
        result = subprocess.run(
            [sys.executable, 'cloud_function_daily_stocks/deploy_via_api.py'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        logger.info(result.stdout)
        if result.returncode != 0:
            logger.error(f"Deployment failed: {result.stderr}")
            logger.info("\nYou can manually deploy later using:")
            logger.info("  cd cloud_function_daily_stocks")
            logger.info("  python deploy_via_api.py")
    except Exception as e:
        logger.error(f"Deployment error: {e}")
        logger.info("\nYou can manually deploy later using:")
        logger.info("  cd cloud_function_daily_stocks")
        logger.info("  python deploy_via_api.py")

    time.sleep(2)

    # Step 5: Set up Cloud Scheduler
    logger.info(f"\n{'='*70}")
    logger.info("STEP 5: Setting Up Cloud Scheduler")
    logger.info(f"{'='*70}\n")

    scheduler_name = 'daily-stock-fetch-job'
    function_url = f"https://{REGION}-{PROJECT_ID}.cloudfunctions.net/daily-stock-fetcher"

    logger.info("Creating Cloud Scheduler job...")

    # Delete existing scheduler if any
    try:
        subprocess.run([
            'gcloud', 'scheduler', 'jobs', 'delete', scheduler_name,
            '--location', REGION,
            '--project', PROJECT_ID,
            '--quiet'
        ], capture_output=True)
    except:
        pass

    # Create new scheduler
    try:
        result = subprocess.run([
            'gcloud', 'scheduler', 'jobs', 'create', 'http', scheduler_name,
            '--location', REGION,
            '--schedule', '0 0 * * *',  # Midnight ET
            '--uri', function_url,
            '--http-method', 'GET',
            '--time-zone', 'America/New_York',
            '--project', PROJECT_ID,
            '--description', 'Daily stock data fetch with technical indicators'
        ], capture_output=True, text=True, check=True)

        logger.info(result.stdout)
        logger.info(f"✓ Cloud Scheduler created successfully!")

    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Failed to create scheduler: {e}")
        logger.error(f"Output: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        logger.info("\nYou can manually create the scheduler using:")
        logger.info(f"  gcloud scheduler jobs create http {scheduler_name} \\")
        logger.info(f"    --location {REGION} \\")
        logger.info(f"    --schedule '0 0 * * *' \\")
        logger.info(f"    --uri {function_url} \\")
        logger.info(f"    --http-method GET \\")
        logger.info(f"    --time-zone America/New_York \\")
        logger.info(f"    --project {PROJECT_ID}")

    # Final summary
    logger.info("\n" + "="*70)
    logger.info("SETUP COMPLETE!")
    logger.info("="*70)
    logger.info("\nStock data pipeline is now configured:")
    logger.info(f"  ✓ BigQuery table: {PROJECT_ID}.crypto_trading_data.stock_analysis")
    logger.info(f"  ✓ Historical data: 6 months loaded")
    logger.info(f"  ✓ Cloud Function: daily-stock-fetcher")
    logger.info(f"  ✓ Scheduler: Runs daily at midnight ET")

    logger.info("\nNext steps:")
    logger.info("  1. Test the function manually:")
    logger.info(f"     curl {function_url}")
    logger.info("  2. View data in BigQuery:")
    logger.info(f"     bq query --use_legacy_sql=false 'SELECT * FROM crypto_trading_data.stock_analysis LIMIT 10'")
    logger.info("  3. Check scheduler:")
    logger.info(f"     gcloud scheduler jobs describe {scheduler_name} --location {REGION}")

    logger.info("\n" + "="*70)

    return True

if __name__ == "__main__":
    main()
