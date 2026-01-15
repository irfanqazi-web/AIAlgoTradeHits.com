"""
Comprehensive BigQuery Database Audit
- Queries all tables for row counts
- Identifies empty and underutilized tables
- Categorizes tables by asset type
- Generates recommendations report
"""
import sys
import io
from datetime import datetime
from google.cloud import bigquery
import json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdout.reconfigure(line_buffering=True)

PROJECT_ID = "cryptobot-462709"
DATASET_ID = "crypto_trading_data"

# Asset category patterns for classification
CATEGORY_PATTERNS = {
    'stocks': ['stock', 'stocks', 'equity', 'equities'],
    'crypto': ['crypto', 'cryptocurrency', 'btc', 'eth', 'coin'],
    'forex': ['forex', 'fx', 'currency', 'currencies'],
    'etfs': ['etf', 'etfs'],
    'indices': ['index', 'indices', 'indice'],
    'commodities': ['commodity', 'commodities', 'gold', 'oil', 'silver'],
    'bonds': ['bond', 'bonds', 'treasury', 'interest_rate'],
}

def classify_table(table_name):
    """Classify table into asset category based on name"""
    table_lower = table_name.lower()

    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if pattern in table_lower:
                return category
    return 'other'

def get_timeframe(table_name):
    """Extract timeframe from table name"""
    table_lower = table_name.lower()
    timeframes = ['weekly', 'daily', 'hourly', '5min', '1min', 'monthly']
    for tf in timeframes:
        if tf in table_lower:
            return tf
    return 'unknown'

def run_audit():
    """Run comprehensive database audit"""
    print("=" * 80)
    print("BIGQUERY DATABASE AUDIT")
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print(f"Started: {datetime.now()}")
    print("=" * 80)

    client = bigquery.Client(project=PROJECT_ID)

    # Get all tables with metadata
    query = f"""
    SELECT
        table_id,
        row_count,
        size_bytes,
        TIMESTAMP_MILLIS(last_modified_time) as last_modified
    FROM `{PROJECT_ID}.{DATASET_ID}.__TABLES__`
    ORDER BY row_count DESC
    """

    print("\nFetching table metadata...")
    results = client.query(query).result()

    tables = []
    for row in results:
        tables.append({
            'table_name': row.table_id,
            'row_count': row.row_count,
            'size_mb': round(row.size_bytes / (1024 * 1024), 2) if row.size_bytes else 0,
            'last_modified': row.last_modified.isoformat() if row.last_modified else None,
            'category': classify_table(row.table_id),
            'timeframe': get_timeframe(row.table_id)
        })

    # Summary statistics
    total_tables = len(tables)
    total_rows = sum(t['row_count'] for t in tables)
    total_size_mb = sum(t['size_mb'] for t in tables)
    empty_tables = [t for t in tables if t['row_count'] == 0]
    small_tables = [t for t in tables if 0 < t['row_count'] < 100]

    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Tables: {total_tables}")
    print(f"Total Rows: {total_rows:,}")
    print(f"Total Size: {total_size_mb:.2f} MB ({total_size_mb/1024:.2f} GB)")
    print(f"Empty Tables: {len(empty_tables)}")
    print(f"Small Tables (<100 rows): {len(small_tables)}")

    # Category breakdown
    print(f"\n{'=' * 80}")
    print("CATEGORY BREAKDOWN")
    print(f"{'=' * 80}")

    categories = {}
    for t in tables:
        cat = t['category']
        if cat not in categories:
            categories[cat] = {'count': 0, 'rows': 0, 'size_mb': 0, 'tables': []}
        categories[cat]['count'] += 1
        categories[cat]['rows'] += t['row_count']
        categories[cat]['size_mb'] += t['size_mb']
        categories[cat]['tables'].append(t)

    for cat, data in sorted(categories.items(), key=lambda x: x[1]['rows'], reverse=True):
        avg_rows = data['rows'] / data['count'] if data['count'] > 0 else 0
        print(f"\n{cat.upper()}")
        print(f"  Tables: {data['count']}")
        print(f"  Total Rows: {data['rows']:,}")
        print(f"  Avg Rows/Table: {avg_rows:,.0f}")
        print(f"  Size: {data['size_mb']:.2f} MB")
        print(f"  % of Data: {(data['rows']/total_rows*100):.1f}%")

    # Empty tables detail
    if empty_tables:
        print(f"\n{'=' * 80}")
        print("EMPTY TABLES (0 rows)")
        print(f"{'=' * 80}")
        for t in empty_tables:
            print(f"  - {t['table_name']} ({t['category']})")

    # Small tables detail
    if small_tables:
        print(f"\n{'=' * 80}")
        print("SMALL TABLES (<100 rows)")
        print(f"{'=' * 80}")
        for t in sorted(small_tables, key=lambda x: x['row_count']):
            print(f"  - {t['table_name']}: {t['row_count']} rows ({t['category']})")

    # "Other" category detail
    other_tables = categories.get('other', {}).get('tables', [])
    if other_tables:
        print(f"\n{'=' * 80}")
        print("'OTHER' CATEGORY TABLES (need classification)")
        print(f"{'=' * 80}")
        for t in sorted(other_tables, key=lambda x: x['row_count'], reverse=True):
            print(f"  - {t['table_name']}: {t['row_count']:,} rows, {t['size_mb']:.2f} MB")

    # Tables by timeframe
    print(f"\n{'=' * 80}")
    print("TABLES BY TIMEFRAME")
    print(f"{'=' * 80}")
    timeframes = {}
    for t in tables:
        tf = t['timeframe']
        if tf not in timeframes:
            timeframes[tf] = {'count': 0, 'rows': 0}
        timeframes[tf]['count'] += 1
        timeframes[tf]['rows'] += t['row_count']

    for tf, data in sorted(timeframes.items(), key=lambda x: x[1]['rows'], reverse=True):
        print(f"  {tf}: {data['count']} tables, {data['rows']:,} rows")

    # Top 20 largest tables
    print(f"\n{'=' * 80}")
    print("TOP 20 LARGEST TABLES")
    print(f"{'=' * 80}")
    for i, t in enumerate(tables[:20], 1):
        print(f"  {i:2}. {t['table_name']}")
        print(f"      {t['row_count']:,} rows | {t['size_mb']:.2f} MB | {t['category']} | {t['timeframe']}")

    # Consolidation candidates
    print(f"\n{'=' * 80}")
    print("CONSOLIDATION RECOMMENDATIONS")
    print(f"{'=' * 80}")

    for cat, data in sorted(categories.items(), key=lambda x: x[1]['count'], reverse=True):
        if data['count'] > 1 and cat != 'other':
            print(f"\n{cat.upper()}: {data['count']} tables -> 1 unified table")
            print(f"  Current tables:")
            for t in sorted(data['tables'], key=lambda x: x['row_count'], reverse=True)[:5]:
                print(f"    - {t['table_name']}: {t['row_count']:,} rows")
            if data['count'] > 5:
                print(f"    ... and {data['count'] - 5} more")
            print(f"  Recommendation: Merge into `{cat}_unified` with columns:")
            print(f"    - symbol (VARCHAR)")
            print(f"    - datetime (TIMESTAMP) [partition key]")
            print(f"    - timeframe (VARCHAR: daily/hourly/5min/weekly)")
            print(f"    - open, high, low, close, volume")
            print(f"    - All technical indicators")

    # Save detailed report to JSON
    report = {
        'audit_date': datetime.now().isoformat(),
        'project_id': PROJECT_ID,
        'dataset_id': DATASET_ID,
        'summary': {
            'total_tables': total_tables,
            'total_rows': total_rows,
            'total_size_mb': total_size_mb,
            'empty_tables_count': len(empty_tables),
            'small_tables_count': len(small_tables)
        },
        'categories': {
            cat: {
                'count': data['count'],
                'rows': data['rows'],
                'size_mb': data['size_mb'],
                'avg_rows_per_table': data['rows'] / data['count'] if data['count'] > 0 else 0
            }
            for cat, data in categories.items()
        },
        'empty_tables': [t['table_name'] for t in empty_tables],
        'small_tables': [{'name': t['table_name'], 'rows': t['row_count']} for t in small_tables],
        'other_category_tables': [{'name': t['table_name'], 'rows': t['row_count']} for t in other_tables],
        'all_tables': tables
    }

    report_file = 'C:/1AITrading/Trading/database_audit_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n\nDetailed report saved to: {report_file}")

    print(f"\n{'=' * 80}")
    print("AUDIT COMPLETE")
    print(f"Finished: {datetime.now()}")
    print(f"{'=' * 80}")

    return report

if __name__ == "__main__":
    run_audit()
