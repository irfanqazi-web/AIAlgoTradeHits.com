"""
Backfill missing days in BigQuery crypto_analysis table
Fetches daily OHLC data from Kraken for missing dates and appends to BigQuery
"""

import sys
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import krakenex
import pandas as pd
from google.cloud import bigquery
from datetime import datetime, timedelta
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = 'molten-optics-310919'
DATASET_ID = 'kamiyabPakistan'
TABLE_ID = 'crypto_analysis'

def get_missing_dates():
    """Get list of missing dates from BigQuery table"""

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    # Get the last date in the table
    query = f"""
    SELECT MAX(DATE(datetime)) as last_date
    FROM `{table_ref}`
    """

    result = client.query(query).to_dataframe()
    last_date = result['last_date'].iloc[0]

    logger.info(f"Last date in table: {last_date}")

    # Calculate missing dates from last_date + 1 to yesterday
    yesterday = (datetime.now() - timedelta(days=1)).date()
    missing_dates = []

    current_date = last_date + timedelta(days=1)
    while current_date <= yesterday:
        missing_dates.append(current_date)
        current_date += timedelta(days=1)

    logger.info(f"Found {len(missing_dates)} missing dates")

    return missing_dates

def fetch_data_for_date(target_date):
    """Fetch daily OHLC data for all USD pairs for a specific date"""

    logger.info(f"\nFetching data for {target_date}")

    # Initialize Kraken API
    kraken = krakenex.API()

    # Get all tradable asset pairs
    pairs_response = kraken.query_public('AssetPairs')

    if pairs_response['error']:
        logger.error(f"Error fetching pairs: {pairs_response['error']}")
        return None

    # Filter for USD pairs
    all_pairs = pairs_response['result']
    usd_pairs = {k: v for k, v in all_pairs.items() if 'USD' in k and v.get('status') == 'online'}

    logger.info(f"Found {len(usd_pairs)} USD trading pairs")

    # Calculate timestamp for the target date
    # We need to get data since the day before to ensure we get the complete daily candle
    since_date = target_date - timedelta(days=2)
    since_timestamp = int(datetime.combine(since_date, datetime.min.time()).timestamp())

    all_ohlc_data = []
    failed_pairs = []
    successful_pairs = 0

    for idx, (pair, info) in enumerate(usd_pairs.items(), 1):
        try:
            if idx % 50 == 0:
                logger.info(f"Progress: {idx}/{len(usd_pairs)} pairs")

            # Fetch OHLC data (1440 minute interval = daily)
            ohlc_response = kraken.query_public('OHLC', {
                'pair': pair,
                'interval': 1440,  # Daily candles
                'since': since_timestamp
            })

            if ohlc_response['error']:
                logger.warning(f"Error fetching {pair}: {ohlc_response['error']}")
                failed_pairs.append({'pair': pair, 'error': str(ohlc_response['error'])})
                continue

            # Parse OHLC data
            ohlc_list = list(ohlc_response['result'].values())[0]

            # Filter for the specific target date
            for candle in ohlc_list:
                candle_date = datetime.fromtimestamp(candle[0]).date()
                if candle_date == target_date:
                    all_ohlc_data.append({
                        'pair': pair,
                        'altname': info.get('altname', pair),
                        'base': info.get('base', ''),
                        'quote': info.get('quote', ''),
                        'timestamp': candle[0],
                        'datetime': datetime.fromtimestamp(candle[0]),
                        'open': float(candle[1]),
                        'high': float(candle[2]),
                        'low': float(candle[3]),
                        'close': float(candle[4]),
                        'vwap': float(candle[5]),
                        'volume': float(candle[6]),
                        'count': int(candle[7])
                    })
                    break

            successful_pairs += 1

            # Rate limiting
            time.sleep(1.5)

        except Exception as e:
            logger.error(f"Exception fetching {pair}: {str(e)}")
            failed_pairs.append({'pair': pair, 'error': str(e)})
            time.sleep(2)

    logger.info(f"Successfully fetched data from {successful_pairs}/{len(usd_pairs)} pairs")
    logger.info(f"Total records for {target_date}: {len(all_ohlc_data)}")

    if failed_pairs:
        logger.warning(f"Failed pairs: {len(failed_pairs)}")

    return pd.DataFrame(all_ohlc_data) if all_ohlc_data else None

def append_to_bigquery(df):
    """Append data to BigQuery table"""

    if df is None or df.empty:
        logger.warning("No data to upload")
        return False

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        schema=[
            bigquery.SchemaField("pair", "STRING"),
            bigquery.SchemaField("altname", "STRING"),
            bigquery.SchemaField("base", "STRING"),
            bigquery.SchemaField("quote", "STRING"),
            bigquery.SchemaField("timestamp", "INTEGER"),
            bigquery.SchemaField("datetime", "TIMESTAMP"),
            bigquery.SchemaField("open", "FLOAT"),
            bigquery.SchemaField("high", "FLOAT"),
            bigquery.SchemaField("low", "FLOAT"),
            bigquery.SchemaField("close", "FLOAT"),
            bigquery.SchemaField("vwap", "FLOAT"),
            bigquery.SchemaField("volume", "FLOAT"),
            bigquery.SchemaField("count", "INTEGER"),
        ],
    )

    try:
        logger.info(f"Uploading {len(df)} records to BigQuery")

        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()

        logger.info(f"✓ Successfully uploaded {len(df)} records")
        return True

    except Exception as e:
        logger.error(f"Error uploading to BigQuery: {str(e)}")
        return False

def main():
    """Main backfill function"""

    logger.info("="*70)
    logger.info("BACKFILL MISSING DAYS - Starting")
    logger.info("="*70)

    try:
        # Get missing dates
        missing_dates = get_missing_dates()

        if not missing_dates:
            logger.info("\n✓ No missing dates found! Data is up to date.")
            return

        logger.info(f"\n📅 Dates to backfill:")
        for date in missing_dates:
            logger.info(f"   - {date}")

        # Ask for confirmation
        print(f"\n⚠ This will fetch data for {len(missing_dates)} missing dates.")
        print(f"Estimated time: ~{len(missing_dates) * 10} minutes")
        response = input("\nProceed with backfill? (y/n): ")

        if response.lower() != 'y':
            logger.info("Backfill cancelled")
            return

        # Backfill each missing date
        total_records = 0
        successful_dates = 0

        for date in missing_dates:
            logger.info(f"\n{'='*70}")
            logger.info(f"Processing: {date}")
            logger.info(f"{'='*70}")

            # Fetch data for this date
            df = fetch_data_for_date(date)

            if df is not None and not df.empty:
                # Remove duplicates
                df = df.drop_duplicates(subset=['pair', 'timestamp'], keep='last')

                # Upload to BigQuery
                if append_to_bigquery(df):
                    total_records += len(df)
                    successful_dates += 1
                    logger.info(f"✓ Completed {date} - Added {len(df)} records")
                else:
                    logger.error(f"✗ Failed to upload data for {date}")
            else:
                logger.warning(f"✗ No data fetched for {date}")

            # Brief pause between dates
            time.sleep(3)

        # Summary
        logger.info("\n" + "="*70)
        logger.info("BACKFILL COMPLETE")
        logger.info("="*70)
        logger.info(f"\nSuccessful dates: {successful_dates}/{len(missing_dates)}")
        logger.info(f"Total records added: {total_records}")

        if successful_dates == len(missing_dates):
            logger.info("\n✓ All missing dates have been backfilled!")
        else:
            logger.warning(f"\n⚠ {len(missing_dates) - successful_dates} dates failed")

    except Exception as e:
        logger.error(f"\n✗ Error during backfill: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
