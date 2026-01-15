from google.cloud import bigquery
import pandas as pd
import os

# Initialize BigQuery client
client = bigquery.Client(project='molten-optics-310919')

# Dataset and table details
dataset_id = 'kamiyabPakistan'
table_id_pairs = 'kraken_trading_pairs'
table_id_ohlc = 'crypto_analysis'

print("="*60)
print("Uploading Kraken Data to BigQuery")
print("="*60)

# Upload trading pairs table
print("\n1. Uploading trading pairs...")
if os.path.exists('kraken_usd_pairs.csv'):
    pairs_df = pd.read_csv('kraken_usd_pairs.csv')
    table_ref = f'{client.project}.{dataset_id}.{table_id_pairs}'

    # Define schema
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # Overwrite if exists
        autodetect=True
    )

    job = client.load_table_from_dataframe(
        pairs_df, table_ref, job_config=job_config
    )
    job.result()  # Wait for the job to complete

    print(f"   OK - Uploaded {len(pairs_df)} trading pairs to {table_ref}")
else:
    print("   ERROR - kraken_usd_pairs.csv not found")

# Upload OHLC data table
print("\n2. Uploading OHLC data...")
if os.path.exists('kraken_6month_ohlc_data.csv'):
    ohlc_df = pd.read_csv('kraken_6month_ohlc_data.csv')

    # Convert datetime string to proper datetime type
    ohlc_df['datetime'] = pd.to_datetime(ohlc_df['datetime'])

    table_ref = f'{client.project}.{dataset_id}.{table_id_ohlc}'

    # Define schema for better data types
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # Overwrite if exists
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

    job = client.load_table_from_dataframe(
        ohlc_df, table_ref, job_config=job_config
    )
    job.result()  # Wait for the job to complete

    print(f"   OK - Uploaded {len(ohlc_df)} OHLC records to {table_ref}")
    print(f"   - Date range: {ohlc_df['datetime'].min()} to {ohlc_df['datetime'].max()}")
    print(f"   - Unique pairs: {ohlc_df['pair'].nunique()}")
else:
    print("   ERROR - kraken_6month_ohlc_data.csv not found")

print("\n" + "="*60)
print("UPLOAD COMPLETE")
print("="*60)
print(f"\nBigQuery Tables Created:")
print(f"1. {client.project}.{dataset_id}.{table_id_pairs}")
print(f"   - Contains list of all trading pairs")
print(f"\n2. {client.project}.{dataset_id}.{table_id_ohlc}")
print(f"   - Contains 6 months of OHLC price data")
print("\nYou can now query these tables in BigQuery!")
