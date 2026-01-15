"""
Export BigQuery data to Cloud Storage for Timeseries Insights API
Based on: gcp-timeseries-bigquery-implementation.html

This script:
1. Exports BigQuery tables to GCS in NDJSON format
2. Transforms data to Timeseries Insights event format
3. Creates GCS bucket structure for the API
"""

from google.cloud import bigquery, storage
import json
import gzip
from datetime import datetime
import os

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
GCS_BUCKET = 'aialgotradehits-timeseries'
LOCATION = 'us-central1'

bq_client = bigquery.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)


def create_gcs_bucket_if_not_exists():
    """Create GCS bucket for timeseries data if it doesn't exist"""
    try:
        bucket = storage_client.get_bucket(GCS_BUCKET)
        print(f"Bucket {GCS_BUCKET} already exists")
    except Exception:
        bucket = storage_client.create_bucket(
            GCS_BUCKET,
            location=LOCATION
        )
        print(f"Created bucket {GCS_BUCKET}")
    return bucket


def export_table_to_gcs(table_name: str, gcs_prefix: str, where_clause: str = ""):
    """Export BigQuery table to GCS in NDJSON format"""

    destination_uri = f"gs://{GCS_BUCKET}/{gcs_prefix}/*.json.gz"

    # Build query for export
    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    {where_clause}
    """

    # Create temp table with export data
    temp_table = f"{PROJECT_ID}.{DATASET_ID}.temp_export_{table_name}"

    job_config = bigquery.QueryJobConfig(
        destination=temp_table,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    print(f"Creating temp table for {table_name}...")
    query_job = bq_client.query(query, job_config=job_config)
    query_job.result()

    # Export temp table to GCS
    extract_config = bigquery.ExtractJobConfig(
        destination_format=bigquery.DestinationFormat.NEWLINE_DELIMITED_JSON,
        compression=bigquery.Compression.GZIP
    )

    print(f"Exporting {table_name} to {destination_uri}...")
    extract_job = bq_client.extract_table(
        temp_table,
        destination_uri,
        job_config=extract_config
    )
    extract_job.result()

    # Get row count
    table = bq_client.get_table(temp_table)
    row_count = table.num_rows

    # Clean up temp table
    bq_client.delete_table(temp_table)

    print(f"Exported {row_count:,} rows to {destination_uri}")
    return row_count


def transform_stock_to_event(record: dict) -> dict:
    """Transform BigQuery stock record to Timeseries Insights event format"""

    dimensions = [
        {"name": "symbol", "stringVal": record.get("symbol", "UNKNOWN")},
        {"name": "asset_type", "stringVal": "stock"},
    ]

    # Add numeric dimensions
    numeric_fields = [
        'open', 'high', 'low', 'close', 'volume',
        'rsi', 'macd', 'adx', 'atr',
        'sma_20', 'sma_50', 'sma_200',
        'bollinger_upper', 'bollinger_lower',
        'buy_pressure_pct', 'sell_pressure_pct'
    ]

    for field in numeric_fields:
        value = record.get(field)
        if value is not None and value != '' and str(value) != 'NaN':
            try:
                if field == 'volume':
                    dimensions.append({"name": field, "longVal": int(float(value))})
                else:
                    dimensions.append({"name": field, "doubleVal": float(value)})
            except (ValueError, TypeError):
                pass

    # Add categorical dimensions
    if record.get('trend_regime') is not None:
        dimensions.append({"name": "trend_regime", "longVal": int(record['trend_regime'])})

    if record.get('cycle_type') is not None:
        dimensions.append({"name": "cycle_type", "longVal": int(record['cycle_type'])})

    # Build event
    timestamp = record.get('datetime')
    if isinstance(timestamp, str):
        event_time = timestamp
    else:
        event_time = timestamp.isoformat() if timestamp else datetime.now().isoformat()

    event = {
        "eventTime": event_time,
        "dimensions": dimensions
    }

    return event


def transform_crypto_to_event(record: dict) -> dict:
    """Transform BigQuery crypto record to Timeseries Insights event format"""

    dimensions = [
        {"name": "symbol", "stringVal": record.get("symbol", "UNKNOWN")},
        {"name": "asset_type", "stringVal": "crypto"},
    ]

    # Add numeric dimensions
    numeric_fields = [
        'open', 'high', 'low', 'close', 'volume',
        'rsi', 'macd', 'adx', 'atr',
        'sma_20', 'sma_50', 'sma_200',
        'bollinger_upper', 'bollinger_lower',
        'buy_pressure_pct', 'sell_pressure_pct'
    ]

    for field in numeric_fields:
        value = record.get(field)
        if value is not None and value != '' and str(value) != 'NaN':
            try:
                if field == 'volume':
                    dimensions.append({"name": field, "doubleVal": float(value)})
                else:
                    dimensions.append({"name": field, "doubleVal": float(value)})
            except (ValueError, TypeError):
                pass

    # Add categorical dimensions
    if record.get('trend_regime') is not None:
        dimensions.append({"name": "trend_regime", "longVal": int(record['trend_regime'])})

    if record.get('cycle_type') is not None:
        dimensions.append({"name": "cycle_type", "longVal": int(record['cycle_type'])})

    # Build event
    timestamp = record.get('datetime')
    if isinstance(timestamp, str):
        event_time = timestamp
    else:
        event_time = timestamp.isoformat() if timestamp else datetime.now().isoformat()

    event = {
        "eventTime": event_time,
        "dimensions": dimensions
    }

    return event


def transform_gcs_files_to_events(input_prefix: str, output_prefix: str, transform_func):
    """Transform exported JSON files to Timeseries events format"""

    bucket = storage_client.bucket(GCS_BUCKET)
    blobs = bucket.list_blobs(prefix=input_prefix)

    event_count = 0

    for blob in blobs:
        if not blob.name.endswith('.json.gz'):
            continue

        print(f"Transforming {blob.name}...")

        # Download and decompress
        content = blob.download_as_bytes()
        decompressed = gzip.decompress(content).decode('utf-8')

        events = []
        for line in decompressed.split('\n'):
            if line.strip():
                try:
                    record = json.loads(line)
                    event = transform_func(record)
                    events.append(event)
                except json.JSONDecodeError:
                    continue

        if events:
            # Write transformed events
            output_name = f"{output_prefix}/{blob.name.split('/')[-1]}"
            output_blob = bucket.blob(output_name)

            output_data = '\n'.join([json.dumps(e) for e in events])
            compressed = gzip.compress(output_data.encode('utf-8'))

            output_blob.upload_from_string(compressed, content_type='application/gzip')
            event_count += len(events)
            print(f"  Wrote {len(events)} events to {output_name}")

    return event_count


def export_all_data():
    """Export all market data to GCS for Timeseries API"""

    print("=" * 80)
    print("EXPORTING BIGQUERY DATA TO GCS FOR TIMESERIES INSIGHTS API")
    print("=" * 80)
    print(f"Started: {datetime.now()}")

    # Create bucket
    create_gcs_bucket_if_not_exists()

    # Export stocks data
    print("\n--- STOCKS DATA ---")
    stock_rows = export_table_to_gcs(
        'stocks_daily_clean',
        'raw/stocks',
        "WHERE datetime >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY))"
    )

    # Export crypto data
    print("\n--- CRYPTO DATA ---")
    crypto_rows = export_table_to_gcs(
        'crypto_daily_clean',
        'raw/crypto',
        "WHERE datetime >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY))"
    )

    # Transform to events format
    print("\n--- TRANSFORMING TO EVENTS FORMAT ---")

    print("\nTransforming stocks...")
    stock_events = transform_gcs_files_to_events(
        'raw/stocks',
        'events/stocks',
        transform_stock_to_event
    )

    print("\nTransforming crypto...")
    crypto_events = transform_gcs_files_to_events(
        'raw/crypto',
        'events/crypto',
        transform_crypto_to_event
    )

    # Summary
    print("\n" + "=" * 80)
    print("EXPORT SUMMARY")
    print("=" * 80)
    print(f"Stock rows exported: {stock_rows:,}")
    print(f"Crypto rows exported: {crypto_rows:,}")
    print(f"Stock events created: {stock_events:,}")
    print(f"Crypto events created: {crypto_events:,}")
    print(f"\nGCS Bucket: gs://{GCS_BUCKET}/")
    print(f"Raw data: gs://{GCS_BUCKET}/raw/")
    print(f"Events data: gs://{GCS_BUCKET}/events/")
    print(f"\nCompleted: {datetime.now()}")


def quick_export():
    """Quick export of recent data (last 30 days)"""

    print("Quick export of last 30 days data...")

    create_gcs_bucket_if_not_exists()

    # Export stocks
    stock_rows = export_table_to_gcs(
        'stocks_daily_clean',
        'raw/stocks_recent',
        "WHERE datetime >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY))"
    )

    # Export crypto
    crypto_rows = export_table_to_gcs(
        'crypto_daily_clean',
        'raw/crypto_recent',
        "WHERE datetime >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY))"
    )

    print(f"\nExported {stock_rows + crypto_rows:,} total rows")
    return stock_rows + crypto_rows


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_export()
    else:
        export_all_data()
