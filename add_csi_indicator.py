"""
Add CSI (Commodity Selection Index) to all historical tables
CSI = ADX * ATR * (Close / ATR)
CSI measures volatility and trend strength for commodity selection
"""
import sys
import io
from google.cloud import bigquery
import pandas as pd
import numpy as np

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

TABLES_TO_UPDATE = [
    'stocks_historical_daily',
    'cryptos_historical_daily',
    'etfs_historical_daily',
    'forex_historical_daily',
    'indices_historical_daily',
    'commodities_historical_daily'
]

def calculate_csi(df):
    """
    Calculate Commodity Selection Index (CSI)
    CSI = ADX * ATR * (Close / ATR)

    This formula measures:
    - ADX: Trend strength
    - ATR: Volatility
    - Close/ATR: Price to volatility ratio

    Higher CSI = Better trending and volatile instruments for trading
    """
    # Make sure we have required fields
    if 'adx' not in df.columns or 'atr' not in df.columns or 'close' not in df.columns:
        print("    Warning: Missing required fields (adx, atr, close)")
        return df

    # Calculate CSI
    # Avoid division by zero
    atr_safe = df['atr'].replace(0, np.nan)
    df['csi'] = df['adx'] * df['atr'] * (df['close'] / atr_safe)

    # Replace inf/nan with 0
    df['csi'] = df['csi'].replace([np.inf, -np.inf], 0)
    df['csi'] = df['csi'].fillna(0)

    return df

def add_csi_column(client, table_name):
    """Add CSI column to table if it doesn't exist"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    table = client.get_table(table_ref)

    # Check if CSI already exists
    field_names = [field.name for field in table.schema]
    if 'csi' in field_names:
        print(f"  CSI column already exists in {table_name}")
        return True

    # Add CSI column
    try:
        query = f"""
        ALTER TABLE `{table_ref}`
        ADD COLUMN IF NOT EXISTS csi FLOAT64
        """
        client.query(query).result()
        print(f"  ✓ Added CSI column to {table_name}")
        return True
    except Exception as e:
        print(f"  ✗ Error adding CSI column: {str(e)}")
        return False

def backfill_csi_for_table(client, table_name):
    """Backfill CSI values for all records in a table"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Get unique symbols
    query = f"""
    SELECT DISTINCT symbol
    FROM `{table_ref}`
    ORDER BY symbol
    """

    result = client.query(query).result()
    symbols = [row['symbol'] for row in result]

    print(f"  Processing {len(symbols)} symbols...")

    updated_count = 0

    for i, symbol in enumerate(symbols, 1):
        try:
            # Fetch data for this symbol
            query = f"""
            SELECT datetime, close, adx, atr, symbol
            FROM `{table_ref}`
            WHERE symbol = '{symbol}'
            ORDER BY datetime
            """

            df = client.query(query).to_dataframe()

            if len(df) == 0:
                continue

            # Calculate CSI
            df = calculate_csi(df)

            # Update records in BigQuery
            # Use MERGE to update existing records
            temp_table = f"{table_name}_csi_temp_{i}"
            temp_table_ref = f"{PROJECT_ID}.{DATASET_ID}.{temp_table}"

            # Upload temp table
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            )

            client.load_table_from_dataframe(
                df[['datetime', 'symbol', 'csi']],
                temp_table_ref,
                job_config=job_config
            ).result()

            # Merge with main table
            merge_query = f"""
            MERGE `{table_ref}` T
            USING `{temp_table_ref}` S
            ON T.symbol = S.symbol AND T.datetime = S.datetime
            WHEN MATCHED THEN
              UPDATE SET T.csi = S.csi
            """

            client.query(merge_query).result()

            # Delete temp table
            client.delete_table(temp_table_ref, not_found_ok=True)

            updated_count += len(df)
            print(f"    [{i}/{len(symbols)}] {symbol}: Updated {len(df)} rows")

        except Exception as e:
            print(f"    [{i}/{len(symbols)}] {symbol}: Error - {str(e)[:100]}")
            continue

    return updated_count

def main():
    """Main execution"""
    print("="*70)
    print("ADD CSI (COMMODITY SELECTION INDEX) TO ALL TABLES")
    print("CSI Formula: ADX * ATR * (Close / ATR)")
    print("="*70)
    print()

    client = bigquery.Client(project=PROJECT_ID)

    total_updated = 0

    for table_name in TABLES_TO_UPDATE:
        print(f"\n{'='*70}")
        print(f"Processing: {table_name}")
        print(f"{'='*70}")

        # Get current record count
        try:
            query = f"""
            SELECT COUNT(*) as count
            FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
            """
            result = client.query(query).result()
            row_count = list(result)[0]['count']
            print(f"  Current rows: {row_count:,}")
        except Exception as e:
            print(f"  Error getting row count: {str(e)}")
            continue

        # Add CSI column
        if not add_csi_column(client, table_name):
            continue

        # Backfill CSI values
        updated = backfill_csi_for_table(client, table_name)
        total_updated += updated

        print(f"  ✓ Updated {updated:,} records with CSI values")

    # Summary
    print("\n" + "="*70)
    print("CSI BACKFILL COMPLETE")
    print("="*70)
    print(f"Total records updated: {total_updated:,}")
    print("="*70)

if __name__ == "__main__":
    main()
