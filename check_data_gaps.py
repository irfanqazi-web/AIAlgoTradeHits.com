"""
Check BigQuery crypto_analysis table for data gaps and completeness
Identifies missing dates and provides statistics
"""

import sys
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime, timedelta
import pandas as pd

# Configuration
PROJECT_ID = 'molten-optics-310919'
DATASET_ID = 'kamiyabPakistan'
TABLE_ID = 'crypto_analysis'

def check_data_status():
    """Check the current status of data in BigQuery"""

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    print("="*70)
    print("BIGQUERY DATA STATUS CHECK")
    print("="*70)

    # Check if table exists
    try:
        table = client.get_table(table_ref)
        print(f"\n✓ Table exists: {table_ref}")
        print(f"  Total rows: {table.num_rows:,}")
        print(f"  Size: {table.num_bytes / (1024**2):.2f} MB")
    except Exception as e:
        print(f"\n✗ Error accessing table: {e}")
        return

    # Get date range
    query = f"""
    SELECT
        MIN(DATE(datetime)) as min_date,
        MAX(DATE(datetime)) as max_date,
        COUNT(DISTINCT DATE(datetime)) as num_dates,
        COUNT(*) as total_records,
        COUNT(DISTINCT pair) as num_pairs
    FROM `{table_ref}`
    """

    print("\n" + "="*70)
    print("DATE RANGE & COVERAGE")
    print("="*70)

    result = client.query(query).to_dataframe()

    if result.empty or result['min_date'].iloc[0] is None:
        print("\n✗ Table is empty - no data found")
        return

    min_date = result['min_date'].iloc[0]
    max_date = result['max_date'].iloc[0]
    num_dates = result['num_dates'].iloc[0]
    total_records = result['total_records'].iloc[0]
    num_pairs = result['num_pairs'].iloc[0]

    print(f"\nFirst date: {min_date}")
    print(f"Last date:  {max_date}")
    print(f"Total unique dates: {num_dates}")
    print(f"Total records: {total_records:,}")
    print(f"Unique trading pairs: {num_pairs}")
    print(f"Average records per day: {total_records / num_dates:.0f}")

    # Calculate expected vs actual dates
    expected_dates = (max_date - min_date).days + 1
    missing_dates = expected_dates - num_dates

    print(f"\nExpected dates: {expected_dates}")
    print(f"Missing dates: {missing_dates}")

    if missing_dates > 0:
        print(f"Data completeness: {(num_dates/expected_dates)*100:.1f}%")
    else:
        print("Data completeness: 100%")

    # Find missing dates
    if missing_dates > 0:
        print("\n" + "="*70)
        print("MISSING DATES")
        print("="*70)

        query_missing = f"""
        WITH date_range AS (
            SELECT DATE_ADD(DATE(MIN(datetime)), INTERVAL seq DAY) as date
            FROM `{table_ref}`,
            UNNEST(GENERATE_ARRAY(0, DATE_DIFF(DATE(MAX(datetime)), DATE(MIN(datetime)), DAY))) seq
        ),
        existing_dates AS (
            SELECT DISTINCT DATE(datetime) as date
            FROM `{table_ref}`
        )
        SELECT dr.date as missing_date
        FROM date_range dr
        LEFT JOIN existing_dates ed ON dr.date = ed.date
        WHERE ed.date IS NULL
        ORDER BY dr.date
        LIMIT 100
        """

        missing = client.query(query_missing).to_dataframe()

        if not missing.empty:
            print(f"\nFound {len(missing)} missing dates (showing first 100):")
            for idx, row in missing.head(50).iterrows():
                print(f"  - {row['missing_date']}")

            if len(missing) > 50:
                print(f"  ... and {len(missing) - 50} more")

    # Check records per day
    print("\n" + "="*70)
    print("DAILY RECORD COUNTS (Last 10 Days)")
    print("="*70)

    query_daily = f"""
    SELECT
        DATE(datetime) as date,
        COUNT(*) as num_records,
        COUNT(DISTINCT pair) as num_pairs
    FROM `{table_ref}`
    GROUP BY DATE(datetime)
    ORDER BY DATE(datetime) DESC
    LIMIT 10
    """

    daily_counts = client.query(query_daily).to_dataframe()

    print("\nDate          | Records | Pairs")
    print("-" * 40)
    for idx, row in daily_counts.iterrows():
        print(f"{row['date']} | {row['num_records']:>7} | {row['num_pairs']:>5}")

    # Check for today's data
    print("\n" + "="*70)
    print("TODAY'S DATA")
    print("="*70)

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    query_today = f"""
    SELECT COUNT(*) as count
    FROM `{table_ref}`
    WHERE DATE(datetime) = '{today}'
    """

    today_count = client.query(query_today).to_dataframe()['count'].iloc[0]

    if today_count > 0:
        print(f"\n✓ Today's data exists: {today_count} records")
    else:
        print(f"\n✗ No data for today ({today})")

    query_yesterday = f"""
    SELECT COUNT(*) as count
    FROM `{table_ref}`
    WHERE DATE(datetime) = '{yesterday}'
    """

    yesterday_count = client.query(query_yesterday).to_dataframe()['count'].iloc[0]

    if yesterday_count > 0:
        print(f"✓ Yesterday's data exists: {yesterday_count} records")
    else:
        print(f"✗ No data for yesterday ({yesterday})")

    # Calculate days since last update
    days_since_update = (today - max_date).days

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print(f"\nLast update: {max_date} ({days_since_update} days ago)")

    if days_since_update == 0:
        print("✓ Data is up to date!")
    elif days_since_update == 1:
        print("⚠ Data is 1 day behind")
    else:
        print(f"⚠ Data is {days_since_update} days behind")

    if missing_dates > 0:
        print(f"⚠ {missing_dates} dates are missing in the historical data")
        print("\nRecommendation: Run backfill script to fill gaps")
    else:
        print("✓ No gaps in historical data")

    print("\n" + "="*70)

    return {
        'min_date': min_date,
        'max_date': max_date,
        'missing_dates': missing_dates,
        'days_behind': days_since_update,
        'total_records': total_records
    }

if __name__ == "__main__":
    try:
        status = check_data_status()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
