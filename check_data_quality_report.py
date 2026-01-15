"""
Data Quality Check - Verify indicator completeness in BigQuery
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from google.cloud import bigquery
import pandas as pd

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

def check_data_quality():
    client = bigquery.Client(project=PROJECT_ID)

    print("=" * 80)
    print("DATA QUALITY REPORT - BigQuery Tables")
    print("=" * 80)

    # Check stocks_daily_clean
    print("\n[STOCKS DAILY CLEAN] - Key Indicator Completeness")
    print("-" * 80)

    query = """
    SELECT
        symbol,
        COUNT(*) as total_rows,
        SUM(CASE WHEN pivot_high_flag IS NOT NULL THEN 1 ELSE 0 END) as pivot_high_ok,
        SUM(CASE WHEN pivot_low_flag IS NOT NULL THEN 1 ELSE 0 END) as pivot_low_ok,
        SUM(CASE WHEN mfi IS NOT NULL THEN 1 ELSE 0 END) as mfi_ok,
        SUM(CASE WHEN growth_score IS NOT NULL THEN 1 ELSE 0 END) as growth_score_ok,
        SUM(CASE WHEN sentiment_score IS NOT NULL THEN 1 ELSE 0 END) as sentiment_ok,
        ROUND(100.0 * SUM(CASE WHEN pivot_high_flag IS NOT NULL AND mfi IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_complete
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
    WHERE symbol IN ('AAPL', 'SPY', 'QQQ', 'MSFT', 'NVDA', 'TSLA', 'GOOGL', 'META', 'AMZN')
    GROUP BY symbol
    ORDER BY symbol
    """

    try:
        results = list(client.query(query).result())
        for row in results:
            status = "✅" if row.pct_complete >= 90 else "⚠️" if row.pct_complete >= 50 else "❌"
            print(f"{status} {row.symbol}: {row.total_rows:,} rows | pivot_h={row.pivot_high_ok:,} | pivot_l={row.pivot_low_ok:,} | mfi={row.mfi_ok:,} | growth={row.growth_score_ok:,} | sentiment={row.sentiment_ok:,} | {row.pct_complete}% complete")
    except Exception as e:
        print(f"Error querying stocks: {e}")

    # Check crypto_daily_clean
    print("\n[CRYPTO DAILY CLEAN] - Key Indicator Completeness")
    print("-" * 80)

    query2 = """
    SELECT
        symbol,
        COUNT(*) as total_rows,
        SUM(CASE WHEN pivot_high_flag IS NOT NULL THEN 1 ELSE 0 END) as pivot_high_ok,
        SUM(CASE WHEN pivot_low_flag IS NOT NULL THEN 1 ELSE 0 END) as pivot_low_ok,
        SUM(CASE WHEN mfi IS NOT NULL THEN 1 ELSE 0 END) as mfi_ok,
        SUM(CASE WHEN growth_score IS NOT NULL THEN 1 ELSE 0 END) as growth_score_ok,
        ROUND(100.0 * SUM(CASE WHEN pivot_high_flag IS NOT NULL AND mfi IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_complete
    FROM `aialgotradehits.crypto_trading_data.crypto_daily_clean`
    WHERE symbol IN ('BTCUSD', 'ETHUSD', 'SOLUSD', 'XRPUSD', 'ADAUSD', 'DOGEUSD')
    GROUP BY symbol
    ORDER BY symbol
    """

    try:
        results2 = list(client.query(query2).result())
        for row in results2:
            status = "✅" if row.pct_complete >= 90 else "⚠️" if row.pct_complete >= 50 else "❌"
            print(f"{status} {row.symbol}: {row.total_rows:,} rows | pivot_h={row.pivot_high_ok:,} | pivot_l={row.pivot_low_ok:,} | mfi={row.mfi_ok:,} | growth={row.growth_score_ok:,} | {row.pct_complete}% complete")
    except Exception as e:
        print(f"Error querying crypto: {e}")

    # Check hourly data
    print("\n📊 STOCKS HOURLY CLEAN - Recent Data")
    print("-" * 80)

    query3 = """
    SELECT
        symbol,
        COUNT(*) as total_rows,
        MIN(datetime) as earliest,
        MAX(datetime) as latest,
        SUM(CASE WHEN rsi IS NOT NULL THEN 1 ELSE 0 END) as rsi_ok,
        SUM(CASE WHEN ema_12 IS NOT NULL THEN 1 ELSE 0 END) as ema_ok
    FROM `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
    WHERE symbol IN ('AAPL', 'SPY', 'QQQ')
    GROUP BY symbol
    ORDER BY symbol
    """

    try:
        results3 = list(client.query(query3).result())
        for row in results3:
            print(f"  {row.symbol}: {row.total_rows:,} rows | {row.earliest} to {row.latest} | rsi={row.rsi_ok:,} | ema={row.ema_ok:,}")
    except Exception as e:
        print(f"Error querying hourly: {e}")

    print("\n" + "=" * 80)
    print("DATA QUALITY CHECK COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    check_data_quality()
