"""
Export stocks_master_list with 18 fields (in order) to Excel
Includes calculated fields: hi_lo and pct_hi_lo
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
    print("Exporting stocks_master_list with 18 fields to Excel...")

    client = bigquery.Client(project=PROJECT_ID)

    # Query with 18 fields in the requested order plus calculated fields
    query = f"""
    SELECT
        symbol,
        exchange,
        type,
        country,
        open,
        high,
        low,
        close,
        (high - low) as hi_lo,
        ROUND(SAFE_DIVIDE((high - low), low) * 100, 2) as pct_hi_lo,
        volume,
        previous_close,
        change,
        percent_change,
        average_volume,
        week_52_high,
        week_52_low,
        name
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    WHERE close IS NOT NULL
    ORDER BY percent_change DESC
    """

    print("Running query...")
    df = client.query(query).to_dataframe()

    print(f"Retrieved {len(df)} records")

    # Add rank column at the beginning
    df.insert(0, 'rank', range(1, len(df) + 1))

    # Export to Excel
    excel_path = r'C:\1AITrading\Trading\stocks_master_list_18fields.xlsx'
    df.to_excel(excel_path, index=False, sheet_name='Stocks')
    print(f"Exported to: {excel_path}")

    # Show sample
    print("\nSample data (top 20 stocks by percent_change):")
    print(df.head(20).to_string())

    # Show summary
    print(f"\n=== SUMMARY ===")
    print(f"Total records: {len(df)}")
    print(f"Columns (19 including rank): {list(df.columns)}")

    # Show exchanges
    print(f"\nExchanges: {df['exchange'].value_counts().to_dict()}")

if __name__ == "__main__":
    main()
