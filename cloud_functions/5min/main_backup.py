"""
Kraken Pro 5-Minute Top-10 Gainers Data Fetcher
Fetches 5-minute OHLC data for top 10 hourly gainers and stores in BigQuery
Designed to run every 5 minutes via Google Cloud Scheduler
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
HOURLY_TABLE_ID = 'crypto_hourly_data'
FIVE_MIN_TABLE_ID = 'crypto_5min_top10_gainers'

def get_top10_gainers():
    """Get top 10 hourly gainers from hourly data"""

    logger.info("Calculating top 10 hourly gainers...")

    client = bigquery.Client(project=PROJECT_ID)

    # Query to get hourly gains
    query = f"""
    WITH latest_hour AS (
        SELECT
            pair,
            close as current_close,
            timestamp as current_timestamp,
            ROW_NUMBER() OVER (PARTITION BY pair ORDER BY timestamp DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.{HOURLY_TABLE_ID}`
        WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 HOUR)
    ),
    previous_hour AS (
        SELECT
            pair,
            close as previous_close,
            timestamp as previous_timestamp,
            ROW_NUMBER() OVER (PARTITION BY pair ORDER BY timestamp DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.{HOURLY_TABLE_ID}`
        WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 3 HOUR)
          AND datetime < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
    )
    SELECT
        l.pair,
        l.current_close,
        p.previous_close,
        ((l.current_close - p.previous_close) / p.previous_close * 100) as hourly_gain_pct
    FROM latest_hour l
    JOIN previous_hour p ON l.pair = p.pair
    WHERE l.rn = 1 AND p.rn = 1
      AND p.previous_close > 0
    ORDER BY hourly_gain_pct DESC
    LIMIT 10
    """

    try:
        result = client.query(query).to_dataframe()

        if result.empty:
            logger.warning("No hourly data found for gain calculation")
            return []

        top_pairs = result['pair'].tolist()
        logger.info(f"Top 10 gainers: {top_pairs}")
        logger.info(f"Gains: {result[['pair', 'hourly_gain_pct']].to_dict('records')}")

        return top_pairs

    except Exception as e:
        logger.error(f"Error calculating top gainers: {e}")
        return []


def fetch_5min_data_for_pairs(pairs):
    """Fetch 5-minute OHLC data for specific pairs"""

    if not pairs:
        logger.warning("No pairs to fetch")
        return None

    logger.info(f"Fetching 5-minute data for {len(pairs)} pairs...")

    # Initialize Kraken API
    kraken = krakenex.API()

    # Calculate timestamp for last hour (to get recent 5-min candles)
    one_hour_ago = datetime.now() - timedelta(hours=1)
    since_timestamp = int(one_hour_ago.timestamp())

    all_ohlc_data = []
    failed_pairs = []

    for idx, pair in enumerate(pairs, 1):
        try:
            logger.info(f"[{idx}/{len(pairs)}] Fetching {pair}")

            # Fetch OHLC data (5 minute interval)
            ohlc_response = kraken.query_public('OHLC', {
                'pair': pair,
                'interval': 5,  # 5-minute candles
                'since': since_timestamp
            })

            if ohlc_response['error']:
                logger.warning(f"Error fetching {pair}: {ohlc_response['error']}")
                failed_pairs.append({'pair': pair, 'error': str(ohlc_response['error'])})
                continue

            # Parse OHLC data
            result_keys = list(ohlc_response['result'].keys())
            data_key = [k for k in result_keys if k != 'last'][0]
            ohlc_list = ohlc_response['result'][data_key]

            for candle in ohlc_list:
                all_ohlc_data.append({
                    'pair': pair,
                    'timestamp': candle[0],
                    'datetime': datetime.fromtimestamp(candle[0]),
                    'open': float(candle[1]),
                    'high': float(candle[2]),
                    'low': float(candle[3]),
                    'close': float(candle[4]),
                    'vwap': float(candle[5]),
                    'volume': float(candle[6]),
                    'count': int(candle[7]),
                    'fetched_at': datetime.now()
                })

            # Rate limiting
            time.sleep(1.5)

        except Exception as e:
            logger.error(f"Exception fetching {pair}: {str(e)}")
            failed_pairs.append({'pair': pair, 'error': str(e)})
            time.sleep(2)

    logger.info(f"Fetched {len(all_ohlc_data)} 5-minute candles")

    if failed_pairs:
        logger.warning(f"Failed pairs: {len(failed_pairs)}")

    return pd.DataFrame(all_ohlc_data) if all_ohlc_data else None


def append_to_bigquery(df):
    """Append data to BigQuery 5-minute table"""

    if df is None or df.empty:
        logger.warning("No data to upload")
        return False

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{FIVE_MIN_TABLE_ID}'

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        schema=[
            bigquery.SchemaField("pair", "STRING"),
            bigquery.SchemaField("timestamp", "INTEGER"),
            bigquery.SchemaField("datetime", "TIMESTAMP"),
            bigquery.SchemaField("open", "FLOAT"),
            bigquery.SchemaField("high", "FLOAT"),
            bigquery.SchemaField("low", "FLOAT"),
            bigquery.SchemaField("close", "FLOAT"),
            bigquery.SchemaField("vwap", "FLOAT"),
            bigquery.SchemaField("volume", "FLOAT"),
            bigquery.SchemaField("count", "INTEGER"),
            bigquery.SchemaField("fetched_at", "TIMESTAMP"),
        ],
    )

    try:
        # Check for duplicates
        min_timestamp = df['timestamp'].min()
        max_timestamp = df['timestamp'].max()

        query = f"""
        SELECT DISTINCT pair, timestamp
        FROM `{table_ref}`
        WHERE timestamp BETWEEN {min_timestamp} AND {max_timestamp}
        """

        try:
            existing_data = client.query(query).to_dataframe()

            if not existing_data.empty:
                df['key'] = df['pair'] + '_' + df['timestamp'].astype(str)
                existing_data['key'] = existing_data['pair'] + '_' + existing_data['timestamp'].astype(str)

                df_filtered = df[~df['key'].isin(existing_data['key'])].copy()
                df_filtered = df_filtered.drop(columns=['key'])

                logger.info(f"After filtering duplicates: {len(df_filtered)} new records")
            else:
                df_filtered = df
        except:
            df_filtered = df

        if df_filtered.empty:
            logger.info("No new data to insert")
            return True

        logger.info(f"Uploading {len(df_filtered)} records to BigQuery")

        job = client.load_table_from_dataframe(df_filtered, table_ref, job_config=job_config)
        job.result()

        logger.info(f"✓ Successfully uploaded {len(df_filtered)} records")
        return True

    except Exception as e:
        logger.error(f"Error uploading to BigQuery: {str(e)}")
        return False


def main():
    """Main function"""

    logger.info("="*60)
    logger.info("Starting 5-Minute Top-10 Gainers Data Fetch")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info("="*60)

    # Step 1: Get top 10 hourly gainers
    top_pairs = get_top10_gainers()

    if not top_pairs:
        logger.warning("No top gainers identified, skipping fetch")
        return

    # Step 2: Fetch 5-minute data for those pairs
    df = fetch_5min_data_for_pairs(top_pairs)

    if df is not None and not df.empty:
        # Remove duplicates
        df = df.drop_duplicates(subset=['pair', 'timestamp'], keep='last')
        logger.info(f"After deduplication: {len(df)} records")

        # Step 3: Upload to BigQuery
        success = append_to_bigquery(df)

        if success:
            logger.info("5-minute data fetch completed successfully!")
        else:
            logger.error("Failed to upload data to BigQuery")
    else:
        logger.error("No 5-minute data fetched")

    logger.info("="*60)


# For Google Cloud Functions
def fivemin_top10_fetch(request):
    """
    Cloud Function entry point for 5-minute top-10 gainers fetch
    """
    main()
    return '5-minute top-10 gainers fetch completed', 200


# For local testing
if __name__ == "__main__":
    main()
