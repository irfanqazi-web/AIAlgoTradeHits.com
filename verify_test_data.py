"""
Verify test data uploaded to BigQuery
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = "cryptobot-462709"
DATASET_ID = "crypto_trading_data"

def check_table(table_name):
    """Check table contents"""
    client = bigquery.Client(project=PROJECT_ID)

    print(f"\n{'='*80}")
    print(f"TABLE: {table_name}")
    print(f"{'='*80}")

    # Get count
    query = f"SELECT COUNT(*) as count FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`"
    try:
        result = client.query(query).result()
        for row in result:
            print(f"  Total records: {row['count']}")
    except Exception as e:
        print(f"  Error: {str(e)}")
        return

    # Get date range
    query = f"""
    SELECT
        MIN(datetime) as min_date,
        MAX(datetime) as max_date
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    """
    try:
        result = client.query(query).result()
        for row in result:
            print(f"  Date range: {row['min_date']} to {row['max_date']}")
    except Exception as e:
        print(f"  Date range error: {str(e)}")

    # Get sample data
    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    ORDER BY datetime DESC
    LIMIT 3
    """
    try:
        result = client.query(query).result()
        print(f"\n  Sample data (latest 3 records):")
        for i, row in enumerate(result, 1):
            if 'symbol' in row.keys():
                print(f"    {i}. {row.get('symbol')} - {row.get('datetime')} - Close: ${row.get('close'):.2f}")
            elif 'pair' in row.keys():
                print(f"    {i}. {row.get('pair')} - {row.get('datetime')} - Close: ${row.get('close'):.2f}")
    except Exception as e:
        print(f"  Sample data error: {str(e)}")

def main():
    print("\n" + "="*80)
    print("BIGQUERY DATA VERIFICATION")
    print("="*80)

    # Stock tables
    print("\n" + "#"*80)
    print("# STOCK DATA")
    print("#"*80)
    check_table('stocks_daily')
    check_table('stocks_15min')
    check_table('stocks_5min')

    # Crypto tables
    print("\n" + "#"*80)
    print("# CRYPTO DATA")
    print("#"*80)
    check_table('crypto_daily')
    check_table('crypto_15min')
    check_table('crypto_5min')

    print("\n" + "="*80)
    print("VERIFICATION COMPLETE!")
    print("="*80)

if __name__ == '__main__':
    main()
