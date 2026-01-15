"""
BigQuery Table Audit, Cleanup, and Gap Analysis
- Identifies tables to KEEP vs DELETE
- Analyzes data gaps in clean tables
- Provides cleanup commands
"""
from google.cloud import bigquery
import pandas as pd
from datetime import datetime, timedelta

client = bigquery.Client(project='aialgotradehits')
dataset_id = 'aialgotradehits.crypto_trading_data'

print("="*100)
print("BIGQUERY TABLE AUDIT & CLEANUP ANALYSIS")
print("="*100)

# ==================== STEP 1: LIST ALL TABLES ====================
print("\n1. Fetching all tables...")

query = f"""
SELECT
    table_name,
    ROUND(size_bytes/1024/1024, 2) as size_mb,
    row_count,
    creation_time
FROM `{dataset_id}.__TABLES__`
ORDER BY size_bytes DESC
"""
all_tables = client.query(query).to_dataframe()
print(f"   Total tables: {len(all_tables)}")

# ==================== STEP 2: CATEGORIZE TABLES ====================
print("\n2. Categorizing tables...")

# Tables to KEEP (production clean tables)
KEEP_TABLES = [
    'stocks_daily_clean',
    'stocks_hourly_clean',
    'stocks_5min_clean',
    'stocks_1min_clean',  # Will create
    'crypto_daily_clean',
    'crypto_hourly_clean',
    'crypto_5min_clean',
    'crypto_1min_clean',  # Will create
]

# Tables to KEEP (supporting infrastructure)
KEEP_SUPPORTING = [
    'paper_trades',
    'strategy_signals',
    'strategy_backtests',
    'strategy_daily_summary',
    'rise_cycles',
    'search_history',
    'interest_rates',
    'sector_momentum_rankings',
]

# Categorize all tables
keep_tables = []
delete_temp_tables = []
delete_v2_tables = []
delete_legacy_tables = []
delete_features_tables = []

for _, row in all_tables.iterrows():
    table_name = row['table_name']

    if table_name in KEEP_TABLES or table_name in KEEP_SUPPORTING:
        keep_tables.append(row)
    elif table_name.startswith('temp_') or table_name.startswith('_temp_'):
        delete_temp_tables.append(row)
    elif table_name.startswith('v2_'):
        delete_v2_tables.append(row)
    elif any(x in table_name for x in ['crypto_analysis', 'crypto_hourly_data', 'crypto_5min',
                                         'btc_ai_training', 'nvda_ai_training', 'stocks_unified']):
        delete_legacy_tables.append(row)
    else:
        # Check if it's a supporting table we want to keep
        if any(x in table_name for x in ['fundamentals_', 'analyst_', 'earnings_', 'etf_',
                                          'dividends_', 'splits_', 'ipo_', 'sec_', 'market_',
                                          'mutual_fund_', 'fund_', 'institutional_', 'insider_',
                                          'exchange_']):
            keep_tables.append(row)
        else:
            delete_legacy_tables.append(row)

print(f"\n   ✓ KEEP: {len(keep_tables)} tables")
print(f"   ✗ DELETE (temp_*): {len(delete_temp_tables)} tables")
print(f"   ✗ DELETE (v2_*): {len(delete_v2_tables)} tables")
print(f"   ✗ DELETE (legacy): {len(delete_legacy_tables)} tables")

# ==================== STEP 3: STORAGE ANALYSIS ====================
print("\n3. Storage analysis...")

keep_size_mb = sum([r['size_mb'] for r in keep_tables])
delete_temp_size = sum([r['size_mb'] for r in delete_temp_tables])
delete_v2_size = sum([r['size_mb'] for r in delete_v2_tables])
delete_legacy_size = sum([r['size_mb'] for r in delete_legacy_tables])

total_delete_size = delete_temp_size + delete_v2_size + delete_legacy_size

print(f"\n   Current storage:")
print(f"   - KEEP tables: {keep_size_mb:.2f} MB")
print(f"   - DELETE temp_*: {delete_temp_size:.2f} MB")
print(f"   - DELETE v2_*: {delete_v2_size:.2f} MB")
print(f"   - DELETE legacy: {delete_legacy_size:.2f} MB")
print(f"   - TOTAL to delete: {total_delete_size:.2f} MB")
print(f"\n   After cleanup: {keep_size_mb:.2f} MB (saving ${(total_delete_size/1024)*0.02:.4f}/month)")

# ==================== STEP 4: ANALYZE CLEAN TABLES ====================
print("\n4. Analyzing clean tables...")

clean_tables_status = []

for table_name in KEEP_TABLES:
    try:
        # Check if table exists
        table_ref = client.get_table(f"{dataset_id}.{table_name}")

        # Get basic stats
        query = f"""
        SELECT
            COUNT(*) as total_rows,
            COUNT(DISTINCT symbol) as unique_symbols,
            MIN(datetime) as earliest_date,
            MAX(datetime) as latest_date,
            -- Check indicator coverage
            COUNTIF(rsi IS NOT NULL) * 100.0 / COUNT(*) as rsi_coverage,
            COUNTIF(macd IS NOT NULL) * 100.0 / COUNT(*) as macd_coverage,
            COUNTIF(mfi IS NOT NULL) * 100.0 / COUNT(*) as mfi_coverage,
            COUNTIF(vwap_daily IS NOT NULL) * 100.0 / COUNT(*) as vwap_coverage
        FROM `{dataset_id}.{table_name}`
        """
        stats = client.query(query).to_dataframe().iloc[0]

        clean_tables_status.append({
            'table': table_name,
            'status': 'EXISTS',
            'rows': int(stats['total_rows']),
            'symbols': int(stats['unique_symbols']),
            'earliest': stats['earliest_date'],
            'latest': stats['latest_date'],
            'rsi_coverage': stats['rsi_coverage'],
            'mfi_coverage': stats['mfi_coverage']
        })

    except Exception as e:
        clean_tables_status.append({
            'table': table_name,
            'status': 'MISSING',
            'rows': 0,
            'symbols': 0,
            'earliest': None,
            'latest': None,
            'rsi_coverage': 0,
            'mfi_coverage': 0
        })

# Print clean table status
print("\n   Clean Tables Status:")
print("   " + "-"*95)
print(f"   {'Table':<25} {'Status':<10} {'Rows':<10} {'Symbols':<10} {'RSI%':<8} {'MFI%':<8} {'Latest'}")
print("   " + "-"*95)

for status in clean_tables_status:
    latest = status['latest'].strftime('%Y-%m-%d') if status['latest'] else 'N/A'
    print(f"   {status['table']:<25} {status['status']:<10} {status['rows']:<10} "
          f"{status['symbols']:<10} {status['rsi_coverage']:<8.1f} "
          f"{status['mfi_coverage']:<8.1f} {latest}")

# ==================== STEP 5: GAP ANALYSIS ====================
print("\n5. Data gap analysis...")

gaps_found = []

for status in clean_tables_status:
    if status['status'] == 'EXISTS':
        table_name = status['table']

        # Check for date gaps
        query = f"""
        WITH date_sequence AS (
            SELECT DATE(datetime) as date
            FROM `{dataset_id}.{table_name}`
            WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
        ),
        all_dates AS (
            SELECT DISTINCT date
            FROM date_sequence
        ),
        expected_dates AS (
            SELECT DATE_SUB(CURRENT_DATE(), INTERVAL day_offset DAY) as expected_date
            FROM UNNEST(GENERATE_ARRAY(0, 89)) as day_offset
        )
        SELECT
            expected_date,
            CASE WHEN date IS NULL THEN 'MISSING' ELSE 'EXISTS' END as status
        FROM expected_dates
        LEFT JOIN all_dates ON expected_dates.expected_date = all_dates.date
        WHERE date IS NULL
        ORDER BY expected_date DESC
        LIMIT 30
        """

        try:
            missing_dates = client.query(query).to_dataframe()
            if len(missing_dates) > 0:
                gaps_found.append({
                    'table': table_name,
                    'gap_type': 'missing_dates',
                    'count': len(missing_dates),
                    'details': f"Missing {len(missing_dates)} dates in last 90 days"
                })
        except:
            pass

        # Check for indicator gaps (missing MFI, VWAP, etc.)
        if status['mfi_coverage'] < 70:
            gaps_found.append({
                'table': table_name,
                'gap_type': 'institutional_indicators',
                'count': status['symbols'],
                'details': f"MFI coverage only {status['mfi_coverage']:.1f}% (target: >70%)"
            })

if gaps_found:
    print("\n   Data Gaps Found:")
    print("   " + "-"*80)
    for gap in gaps_found:
        print(f"   [{gap['table']}] {gap['gap_type']}: {gap['details']}")
    print("   " + "-"*80)
else:
    print("   ✓ No significant gaps found!")

# ==================== STEP 6: GENERATE CLEANUP SCRIPT ====================
print("\n6. Generating cleanup script...")

cleanup_script = "cleanup_tables.sh"
with open(cleanup_script, 'w') as f:
    f.write("#!/bin/bash\n")
    f.write("# BigQuery Table Cleanup Script\n")
    f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"# Deletes {len(delete_temp_tables) + len(delete_v2_tables) + len(delete_legacy_tables)} tables\n")
    f.write(f"# Frees up {total_delete_size:.2f} MB of storage\n\n")

    f.write("PROJECT_ID=aialgotradehits\n")
    f.write("DATASET_ID=crypto_trading_data\n\n")

    # Delete temp tables
    if delete_temp_tables:
        f.write("# Delete temporary tables\n")
        f.write(f"echo 'Deleting {len(delete_temp_tables)} temp_* tables...'\n")
        for table in delete_temp_tables:
            f.write(f"bq rm -f -t $PROJECT_ID:$DATASET_ID.{table['table_name']}\n")
        f.write("\n")

    # Delete v2 tables
    if delete_v2_tables:
        f.write("# Delete v2_* tables\n")
        f.write(f"echo 'Deleting {len(delete_v2_tables)} v2_* tables...'\n")
        for table in delete_v2_tables:
            f.write(f"bq rm -f -t $PROJECT_ID:$DATASET_ID.{table['table_name']}\n")
        f.write("\n")

    # Delete legacy tables
    if delete_legacy_tables:
        f.write("# Delete legacy tables\n")
        f.write(f"echo 'Deleting {len(delete_legacy_tables)} legacy tables...'\n")
        for table in delete_legacy_tables:
            f.write(f"bq rm -f -t $PROJECT_ID:$DATASET_ID.{table['table_name']}\n")
        f.write("\n")

    f.write("echo 'Cleanup complete!'\n")
    f.write(f"echo 'Freed {total_delete_size:.2f} MB of storage'\n")

print(f"   ✓ Cleanup script generated: {cleanup_script}")
print(f"   Run: bash {cleanup_script}")

# ==================== STEP 7: SUMMARY & RECOMMENDATIONS ====================
print("\n" + "="*100)
print("SUMMARY & RECOMMENDATIONS")
print("="*100)

print("\n✓ KEEP (Production Clean Tables):")
for table in KEEP_TABLES:
    status = next((s for s in clean_tables_status if s['table'] == table), None)
    if status:
        if status['status'] == 'EXISTS':
            print(f"   ✓ {table:<25} ({status['rows']:,} rows, {status['symbols']} symbols)")
        else:
            print(f"   ⚠ {table:<25} (MISSING - needs creation)")

print(f"\n✗ DELETE ({len(delete_temp_tables) + len(delete_v2_tables) + len(delete_legacy_tables)} tables):")
print(f"   - temp_* tables: {len(delete_temp_tables)} ({delete_temp_size:.1f} MB)")
print(f"   - v2_* tables: {len(delete_v2_tables)} ({delete_v2_size:.1f} MB)")
print(f"   - legacy tables: {len(delete_legacy_tables)} ({delete_legacy_size:.1f} MB)")

print("\n📊 NEXT STEPS:")
print("   1. Run: bash cleanup_tables.sh (delete unnecessary tables)")
print("   2. Fill gaps in stocks_daily_clean (run indicator calculators)")
print("   3. Create stocks_1min_clean and crypto_1min_clean tables")
print("   4. Expand to 2,500 stocks + 150 crypto (recommended config)")
print("   5. Set up automated schedulers for daily updates")

print("\n" + "="*100)
