"""
Quick fix to get trading app working:
1. Populate crypto_daily_clean with top cryptos
2. Update backend API table references
3. Deploy backend and frontend
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

def populate_crypto_daily_clean():
    """Populate crypto_daily_clean from existing crypto data"""
    client = bigquery.Client(project=PROJECT_ID)

    print("="*80)
    print("POPULATING CRYPTO_DAILY_CLEAN")
    print("="*80)

    # Copy data from available crypto sources (top cryptos like BTC, ETH, etc.)
    # First check if there's any crypto data we can use

    # Try to find crypto data in various tables
    tables_to_check = [
        'crypto_analysis',
        'crypto_hourly_data',
        'v2_cryptos_5min',
    ]

    crypto_data_query = """
    INSERT INTO `aialgotradehits.crypto_trading_data.crypto_daily_clean`
    (symbol, datetime, open, high, low, close, volume,
     rsi, macd, macd_signal, macd_histogram,
     bollinger_upper, bollinger_middle, bollinger_lower,
     sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
     adx, atr, cci, williams_r, stoch_k, stoch_d, obv, momentum, roc,
     sector, exchange)
    SELECT
        pair as symbol,
        TIMESTAMP(datetime) as datetime,
        open, high, low, close, volume,
        rsi, macd, macd_signal, macd_histogram,
        bollinger_upper, bollinger_middle, bollinger_lower,
        sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
        adx, atr, cci, williams_r, stoch_k, stoch_d, obv, momentum, roc,
        'Crypto' as sector,
        'Kraken' as exchange
    FROM `aialgotradehits.crypto_trading_data.crypto_analysis`
    WHERE pair LIKE '%USD'
      AND DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
    """

    try:
        print("\nInserting crypto USD pairs into crypto_daily_clean...")
        job = client.query(crypto_data_query)
        job.result()
        print(f"  Inserted {job.num_dml_affected_rows} rows")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        print("\nTrying alternative crypto sources...")
        return False

def verify_data():
    """Verify both clean tables have data"""
    client = bigquery.Client(project=PROJECT_ID)

    print("\n" + "="*80)
    print("VERIFYING DATA")
    print("="*80)

    # Check stocks
    stocks_query = """
    SELECT
        COUNT(*) as row_count,
        COUNT(DISTINCT symbol) as unique_symbols,
        MAX(datetime) as latest_date
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
    """

    print("\nstocks_daily_clean:")
    result = list(client.query(stocks_query))
    if result:
        row = result[0]
        print(f"  Rows: {row['row_count']:,}")
        print(f"  Symbols: {row['unique_symbols']}")
        print(f"  Latest: {row['latest_date']}")

    # Check cryptos
    crypto_query = """
    SELECT
        COUNT(*) as row_count,
        COUNT(DISTINCT symbol) as unique_symbols,
        MAX(datetime) as latest_date
    FROM `aialgotradehits.crypto_trading_data.crypto_daily_clean`
    """

    print("\ncrypto_daily_clean:")
    result = list(client.query(crypto_query))
    if result:
        row = result[0]
        print(f"  Rows: {row['row_count']:,}")
        print(f"  Symbols: {row['unique_symbols']}")
        print(f"  Latest: {row['latest_date']}")

def main():
    print("="*80)
    print("QUICK FIX - TRADING APP")
    print("="*80)
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Populate crypto data
    populate_crypto_daily_clean()

    # Step 2: Verify data
    verify_data()

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("1. Deploy backend API: cd cloud_function_api && gcloud run deploy...")
    print("2. Deploy frontend: cd stock-price-app && gcloud run deploy...")
    print("3. Test app at: https://aialgotradehits-app-6pmz2y7ouq-uc.a.run.app")

if __name__ == '__main__':
    main()
