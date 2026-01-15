"""
Export stocks_master_list from BigQuery to CSV
"""
from google.cloud import bigquery
import pandas as pd
import sys
import io

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'stocks_master_list'

def main():
    print("Exporting stocks_master_list to CSV...")

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    ORDER BY symbol
    """

    print("Running query...")
    df = client.query(query).to_dataframe()

    print(f"Retrieved {len(df)} records")

    # Export to CSV
    csv_path = r'C:\1AITrading\Trading\stocks_master_list.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"Exported to: {csv_path}")

    # Show sample
    print("\nSample data (first 10 rows):")
    print(df.head(10).to_string())

    # Show summary
    print(f"\n=== SUMMARY ===")
    print(f"Total records: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Column names: {', '.join(df.columns.tolist())}")

    # Show exchanges
    print(f"\nExchanges: {df['exchange'].value_counts().to_dict()}")

    # Show types
    print(f"\nTypes: {df['type'].value_counts().to_dict()}")

if __name__ == "__main__":
    main()
