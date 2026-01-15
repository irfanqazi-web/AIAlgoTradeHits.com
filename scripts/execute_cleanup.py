"""
Automated BigQuery Table Cleanup
Deletes 197 unnecessary tables (temp_*, v2_*, legacy)
"""
import subprocess
import time

# Tables to delete
temp_tables = [
    "temp_CMCSA", "temp_FI", "temp_GE", "temp_GILD", "temp_GOOGL", "temp_GS",
    "temp_HD", "temp_HON", "temp_IBM", "temp_ICE", "temp_INTC", "temp_INTU",
    "temp_ISRG", "temp_JNJ", "temp_JPM", "temp_KO", "temp_LIN", "temp_LLY",
    "temp_LOW", "temp_LRCX", "temp_MA", "temp_MCD", "temp_MDLZ", "temp_META",
    "temp_MMC", "temp_MMM", "temp_MO", "temp_MRK", "temp_MS", "temp_MSFT",
    "temp_MU", "temp_NEE", "temp_NKE", "temp_NOC", "temp_NVDA", "temp_ORCL",
    "temp_PEP", "temp_PFE", "temp_PG", "temp_PGR", "temp_PLD", "temp_PM",
    "temp_PNC", "temp_QCOM", "temp_REGN", "temp_RTX", "temp_SBUX", "temp_SCHW",
    "temp_SLB", "temp_SO", "temp_SPGI", "temp_SYK", "temp_T", "temp_TJX",
    "temp_TMO", "temp_TMUS", "temp_TSLA", "temp_TXN", "temp_UNH", "temp_UNP",
    "temp_UPS", "temp_V", "temp_VRTX", "temp_VZ", "temp_WFC", "temp_WMT",
    "temp_XOM", "temp_ZTS",
]

temp_hourly_tables = [
    "temp_hourly_AAPL", "temp_hourly_ABBV", "temp_hourly_ABT", "temp_hourly_ACN",
    "temp_hourly_ADBE", "temp_hourly_AMD", "temp_hourly_AMGN", "temp_hourly_AMZN",
    "temp_hourly_AVGO", "temp_hourly_BA", "temp_hourly_BMY", "temp_hourly_BRK_B",
    "temp_hourly_CAT", "temp_hourly_CMCSA", "temp_hourly_COST", "temp_hourly_CRM",
    "temp_hourly_CSCO", "temp_hourly_CVX", "temp_hourly_DE", "temp_hourly_DHR",
    "temp_hourly_DIS", "temp_hourly_GE", "temp_hourly_GOOGL", "temp_hourly_GS",
    "temp_hourly_HD", "temp_hourly_HON", "temp_hourly_IBM", "temp_hourly_INTC",
    "temp_hourly_JNJ", "temp_hourly_JPM", "temp_hourly_KO", "temp_hourly_LLY",
    "temp_hourly_MA", "temp_hourly_MCD", "temp_hourly_META", "temp_hourly_MMM",
    "temp_hourly_MRK", "temp_hourly_MSFT", "temp_hourly_NEE", "temp_hourly_NKE",
    "temp_hourly_NVDA", "temp_hourly_ORCL", "temp_hourly_PEP", "temp_hourly_PFE",
    "temp_hourly_PG", "temp_hourly_PM", "temp_hourly_QCOM", "temp_hourly_RTX",
    "temp_hourly_SBUX", "temp_hourly_TMO", "temp_hourly_TSLA", "temp_hourly_TXN",
    "temp_hourly_UNH", "temp_hourly_UNP", "temp_hourly_UPS", "temp_hourly_V",
    "temp_hourly_VZ", "temp_hourly_WFC", "temp_hourly_WMT", "temp_hourly_XOM",
]

temp_features_tables = [
    "_temp_features_AAPL", "_temp_features_DIA", "_temp_features_ETHUSD",
    "_temp_features_IWM", "_temp_features_MSFT", "_temp_features_NVDA",
    "_temp_features_SOLUSD"
]

v2_tables = [
    "v2_bonds_daily",
    "v2_commodities_5min", "v2_commodities_daily", "v2_commodities_historical_daily",
    "v2_commodities_hourly", "v2_commodities_weekly_summary",
    "v2_crypto_5min", "v2_crypto_daily", "v2_crypto_hourly",
    "v2_cryptos_historical_daily", "v2_cryptos_weekly_summary",
    "v2_etfs_5min", "v2_etfs_daily", "v2_etfs_historical_daily",
    "v2_etfs_hourly", "v2_etfs_weekly_summary",
    "v2_forex_5min", "v2_forex_daily", "v2_forex_historical_daily",
    "v2_forex_hourly", "v2_forex_weekly_summary",
    "v2_indices_5min", "v2_indices_daily", "v2_indices_historical_daily",
    "v2_indices_hourly", "v2_indices_weekly_summary",
    "v2_stocks_5min", "v2_stocks_daily", "v2_stocks_historical_daily",
    "v2_stocks_hourly", "v2_stocks_master", "v2_stocks_weekly_summary"
]

legacy_tables = [
    "btc_ai_training_daily",
    "nvda_ai_training_daily",
    "stocks_unified_daily",
    "weekly_commodities_all",
    "weekly_crypto_all",
    "weekly_etfs_all",
    "weekly_forex_all",
    "weekly_funds_all",
    "weekly_indices_all",
    "weekly_stocks_all"
]

all_tables_to_delete = temp_tables + temp_hourly_tables + temp_features_tables + v2_tables + legacy_tables

print("="*100)
print("BIGQUERY TABLE CLEANUP - AUTOMATED EXECUTION")
print("="*100)
print(f"\nTotal tables to delete: {len(all_tables_to_delete)}")
print(f"  - temp_* tables: {len(temp_tables)}")
print(f"  - temp_hourly_* tables: {len(temp_hourly_tables)}")
print(f"  - _temp_features_* tables: {len(temp_features_tables)}")
print(f"  - v2_* tables: {len(v2_tables)}")
print(f"  - legacy tables: {len(legacy_tables)}")
print("\n" + "-"*100)

deleted_count = 0
failed_count = 0
failed_tables = []

start_time = time.time()

for i, table in enumerate(all_tables_to_delete, 1):
    try:
        cmd = f"bq rm -f -t aialgotradehits:crypto_trading_data.{table}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            deleted_count += 1
            status = "✓ DELETED"
        else:
            # Check if table doesn't exist (that's ok)
            if "Not found" in result.stderr or "not found" in result.stderr.lower():
                deleted_count += 1
                status = "✓ NOT FOUND (ok)"
            else:
                failed_count += 1
                failed_tables.append((table, result.stderr.strip()))
                status = "✗ FAILED"

        # Progress update every 20 tables
        if i % 20 == 0 or i == len(all_tables_to_delete):
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = (len(all_tables_to_delete) - i) * avg_time
            print(f"[{i}/{len(all_tables_to_delete)}] {table:<50} {status} | "
                  f"Elapsed: {elapsed:.1f}s | ETA: {remaining:.1f}s")

    except subprocess.TimeoutExpired:
        failed_count += 1
        failed_tables.append((table, "Timeout"))
        print(f"[{i}/{len(all_tables_to_delete)}] {table:<50} ✗ TIMEOUT")
    except Exception as e:
        failed_count += 1
        failed_tables.append((table, str(e)))
        print(f"[{i}/{len(all_tables_to_delete)}] {table:<50} ✗ ERROR: {e}")

total_time = time.time() - start_time

print("\n" + "="*100)
print("CLEANUP COMPLETE")
print("="*100)
print(f"\n✓ Successfully deleted/verified: {deleted_count}/{len(all_tables_to_delete)}")
print(f"✗ Failed: {failed_count}/{len(all_tables_to_delete)}")
print(f"Total time: {total_time:.1f} seconds")

if failed_tables:
    print("\nFailed tables:")
    for table, error in failed_tables[:10]:
        print(f"  - {table}: {error[:80]}")
    if len(failed_tables) > 10:
        print(f"  ... and {len(failed_tables)-10} more")

print("\n" + "="*100)
print("NEXT STEPS:")
print("  1. Verify clean tables remain: bq ls crypto_trading_data | findstr clean")
print("  2. Check storage freed: bq show --format=pretty crypto_trading_data")
print("  3. Proceed to fill data gaps and expand coverage")
print("="*100)
