"""
Check data status for all 6 trading tables
"""
from google.cloud import bigquery
from datetime import datetime, timedelta
import sys
import io

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

client = bigquery.Client(project=PROJECT_ID)

tables_to_check = [
    ('crypto_analysis', 'pair'),
    ('crypto_hourly_data', 'pair'),
    ('crypto_5min_top10_gainers', 'pair'),
    ('stock_analysis', 'symbol'),
    ('stock_hourly_data', 'symbol'),
    ('stock_5min_top10_gainers', 'symbol'),
]

print("=" * 80)
print("DATA STATUS CHECK - ALL 6 TRADING TABLES")
print("=" * 80)
print()

issues_found = []

for table_name, id_field in tables_to_check:
    print(f"\n{'=' * 80}")
    print(f"Table: {table_name}")
    print("=" * 80)

    try:
        # Get basic stats
        query = f"""
        SELECT
            COUNT(*) as total_records,
            MAX(datetime) as latest_data,
            MIN(datetime) as oldest_data,
            COUNT(DISTINCT {id_field}) as unique_symbols
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        """

        result = client.query(query).result()
        row = list(result)[0]

        total = row['total_records']
        latest = row['latest_data']
        oldest = row['oldest_data']
        symbols = row['unique_symbols']

        print(f"Total Records: {total:,}")
        print(f"Unique Symbols: {symbols:,}")
        print(f"Oldest Data: {oldest}")
        print(f"Latest Data: {latest}")

        # Check if data is stale
        if latest:
            now = datetime.now(latest.tzinfo)
            age = now - latest
            print(f"Data Age: {age}")

            # Define staleness thresholds
            if '5min' in table_name and age > timedelta(hours=1):
                issue = f"⚠️ {table_name}: 5-min data is {age} old (should be < 1 hour)"
                print(f"  {issue}")
                issues_found.append(issue)
            elif 'hourly' in table_name and age > timedelta(days=1):
                issue = f"⚠️ {table_name}: Hourly data is {age} old (should be < 1 day)"
                print(f"  {issue}")
                issues_found.append(issue)
            elif 'analysis' in table_name and age > timedelta(days=2):
                issue = f"⚠️ {table_name}: Daily data is {age} old (should be < 2 days)"
                print(f"  {issue}")
                issues_found.append(issue)
            else:
                print(f"  ✓ Data is fresh")

        # Check recent data distribution
        if '5min' not in table_name:
            query_recent = f"""
            SELECT DATE(datetime) as date, COUNT(*) as records
            FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
            WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            GROUP BY date
            ORDER BY date DESC
            LIMIT 7
            """

            result_recent = client.query(query_recent).result()
            rows_recent = list(result_recent)

            if rows_recent:
                print(f"\nRecent Data (Last 7 Days):")
                for row in rows_recent:
                    print(f"  {row['date']}: {row['records']:,} records")
            else:
                issue = f"⚠️ {table_name}: No data in last 7 days!"
                print(f"  {issue}")
                issues_found.append(issue)

    except Exception as e:
        issue = f"❌ {table_name}: ERROR - {str(e)}"
        print(f"  {issue}")
        issues_found.append(issue)

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)

if issues_found:
    print(f"\n⚠️ Found {len(issues_found)} issues:\n")
    for i, issue in enumerate(issues_found, 1):
        print(f"{i}. {issue}")
    print("\n📋 Action Required: Address these data issues before proceeding")
    print("   Consider Massive.com subscription for reliable data feeds")
else:
    print("\n✓ All tables have fresh data!")
    print("✓ Ready to proceed with table renaming")

print()
