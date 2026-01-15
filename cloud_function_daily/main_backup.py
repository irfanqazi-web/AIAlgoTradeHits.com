"""
Kraken Pro Daily Data Fetcher
Fetches daily OHLC data for all crypto pairs and appends to historical BigQuery table
Designed to run daily at midnight via Google Cloud Scheduler
"""

import krakenex
import pandas as pd
from google.cloud import bigquery
from datetime import datetime, timedelta
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = 'molten-optics-310919'
DATASET_ID = 'kamiyabPakistan'
TABLE_ID = 'crypto_analysis'  # Historical daily table

def fetch_daily_data():
    """Fetch daily OHLC data for all USD trading pairs from Kraken"""

    # Initialize Kraken API
    kraken = krakenex.API()

    # Get all tradable asset pairs
    logger.info("Fetching all tradable asset pairs from Kraken...")
    pairs_response = kraken.query_public('AssetPairs')

    if pairs_response['error']:
        logger.error(f"Error fetching pairs: {pairs_response['error']}")
        return None

    # Filter for USD pairs
    all_pairs = pairs_response['result']
    usd_pairs = {k: v for k, v in all_pairs.items() if 'USD' in k and v.get('status') == 'online'}

    logger.info(f"Found {len(usd_pairs)} USD trading pairs")

    # Calculate timestamp for yesterday's data
    # Fetch the last 3 days to ensure we get the complete daily candle
    three_days_ago = datetime.now() - timedelta(days=3)
    since_timestamp = int(three_days_ago.timestamp())

    all_ohlc_data = []
    failed_pairs = []
    successful_pairs = 0

    for idx, (pair, info) in enumerate(usd_pairs.items(), 1):
        try:
            logger.info(f"[{idx}/{len(usd_pairs)}] Fetching {pair} ({info.get('altname', pair)})")

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
            ohlc_list = list(ohlc_response['result'].values())[0]  # Get the data array

            for candle in ohlc_list:
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

            successful_pairs += 1

            # Rate limiting: Kraken allows 1 call per second for public API
            time.sleep(1.5)

        except Exception as e:
            logger.error(f"Exception fetching {pair}: {str(e)}")
            failed_pairs.append({'pair': pair, 'error': str(e)})
            time.sleep(2)

    logger.info(f"Successfully fetched data from {successful_pairs}/{len(usd_pairs)} pairs")
    logger.info(f"Total records: {len(all_ohlc_data)}")

    if failed_pairs:
        logger.warning(f"Failed pairs: {len(failed_pairs)}")

    return pd.DataFrame(all_ohlc_data) if all_ohlc_data else None


def append_to_bigquery(df):
    """Append data to BigQuery historical table, avoiding duplicates"""

    if df is None or df.empty:
        logger.warning("No data to upload")
        return False

    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    # Define schema matching the existing crypto_analysis table
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",  # Append to existing table
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
        # First, check for existing data to avoid duplicates
        logger.info("Checking for existing data to avoid duplicates...")

        # Get the date range of new data
        min_date = df['datetime'].min().strftime('%Y-%m-%d')
        max_date = df['datetime'].max().strftime('%Y-%m-%d')

        # Query existing data for this date range
        query = f"""
        SELECT DISTINCT pair, timestamp
        FROM `{table_ref}`
        WHERE DATE(datetime) BETWEEN '{min_date}' AND '{max_date}'
        """

        existing_data = client.query(query).to_dataframe()
        logger.info(f"Found {len(existing_data)} existing records in date range")

        # Remove duplicates
        if not existing_data.empty:
            # Create a key for comparison
            df['key'] = df['pair'] + '_' + df['timestamp'].astype(str)
            existing_data['key'] = existing_data['pair'] + '_' + existing_data['timestamp'].astype(str)

            # Filter out existing records
            df_filtered = df[~df['key'].isin(existing_data['key'])].copy()
            df_filtered = df_filtered.drop(columns=['key'])

            logger.info(f"After filtering duplicates: {len(df_filtered)} new records to insert")
        else:
            df_filtered = df

        if df_filtered.empty:
            logger.info("No new data to insert (all records already exist)")
            return True

        # Upload to BigQuery
        logger.info(f"Uploading {len(df_filtered)} new records to BigQuery table: {table_ref}")

        job = client.load_table_from_dataframe(
            df_filtered, table_ref, job_config=job_config
        )
        job.result()  # Wait for the job to complete

        logger.info(f"Successfully appended {len(df_filtered)} records to BigQuery")
        logger.info(f"Date range: {df_filtered['datetime'].min()} to {df_filtered['datetime'].max()}")
        logger.info(f"Unique pairs: {df_filtered['pair'].nunique()}")

        return True

    except Exception as e:
        logger.error(f"Error uploading to BigQuery: {str(e)}")
        return False


def main():
    """Main function to fetch and upload daily data"""

    logger.info("="*60)
    logger.info("Starting Daily Crypto Data Fetch")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info("="*60)

    # Fetch data
    df = fetch_daily_data()

    if df is not None and not df.empty:
        # Remove duplicates within the fetched data
        df = df.drop_duplicates(subset=['pair', 'timestamp'], keep='last')
        logger.info(f"After deduplication: {len(df)} records")

        # Append to BigQuery (with duplicate checking)
        success = append_to_bigquery(df)

        if success:
            logger.info("Daily data fetch completed successfully!")
        else:
            logger.error("Failed to upload data to BigQuery")
    else:
        logger.error("No data fetched from Kraken")

    logger.info("="*60)


# For Google Cloud Functions
def daily_crypto_fetch(request):
    """
    Cloud Function entry point for daily data fetch
    """
    main()
    return 'Daily crypto data fetch completed', 200


# For local testing
if __name__ == "__main__":
    main()
