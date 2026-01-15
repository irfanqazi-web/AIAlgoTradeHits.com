"""
Create BigQuery datasets and tables in cryptobot-462709 project
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

def create_dataset():
    """Create BigQuery dataset"""
    print(f"Creating dataset: {DATASET_ID}")

    client = bigquery.Client(project=PROJECT_ID)

    dataset_id = f"{PROJECT_ID}.{DATASET_ID}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"
    dataset.description = "Cryptocurrency trading data with technical indicators"

    try:
        dataset = client.create_dataset(dataset, exists_ok=True)
        print(f"✓ Dataset {dataset_id} created/verified")
    except Exception as e:
        print(f"Error creating dataset: {e}")
        return False

    return True


def create_daily_table():
    """Create daily crypto analysis table"""
    print("\nCreating daily crypto analysis table...")

    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{DATASET_ID}.crypto_analysis"

    schema = [
        bigquery.SchemaField("pair", "STRING"),
        bigquery.SchemaField("symbol", "STRING"),
        bigquery.SchemaField("altname", "STRING"),
        bigquery.SchemaField("base", "STRING"),
        bigquery.SchemaField("quote", "STRING"),
        bigquery.SchemaField("timestamp", "INTEGER"),
        bigquery.SchemaField("datetime", "TIMESTAMP"),
        bigquery.SchemaField("open", "FLOAT"),
        bigquery.SchemaField("open_price", "FLOAT"),
        bigquery.SchemaField("high", "FLOAT"),
        bigquery.SchemaField("low", "FLOAT"),
        bigquery.SchemaField("close", "FLOAT"),
        bigquery.SchemaField("vwap", "FLOAT"),
        bigquery.SchemaField("volume", "FLOAT"),
        bigquery.SchemaField("count", "INTEGER"),
        bigquery.SchemaField("hi_lo", "FLOAT"),
        bigquery.SchemaField("pct_hi_lo_over_lo", "FLOAT"),
        bigquery.SchemaField("rsi", "FLOAT"),
        bigquery.SchemaField("macd", "FLOAT"),
        bigquery.SchemaField("macd_signal", "FLOAT"),
        bigquery.SchemaField("macd_hist", "FLOAT"),
        bigquery.SchemaField("bb_upper", "FLOAT"),
        bigquery.SchemaField("bb_lower", "FLOAT"),
        bigquery.SchemaField("bb_percent", "FLOAT"),
        bigquery.SchemaField("ema_12", "FLOAT"),
        bigquery.SchemaField("ema_26", "FLOAT"),
        bigquery.SchemaField("ema_50", "FLOAT"),
        bigquery.SchemaField("ma_50", "FLOAT"),
        bigquery.SchemaField("sma_20", "FLOAT"),
        bigquery.SchemaField("sma_200", "FLOAT"),
        bigquery.SchemaField("stoch_k", "FLOAT"),
        bigquery.SchemaField("stoch_d", "FLOAT"),
        bigquery.SchemaField("williams_r", "FLOAT"),
        bigquery.SchemaField("adx", "FLOAT"),
        bigquery.SchemaField("cci", "FLOAT"),
        bigquery.SchemaField("roc", "FLOAT"),
        bigquery.SchemaField("momentum", "FLOAT"),
        bigquery.SchemaField("trix", "FLOAT"),
        bigquery.SchemaField("ultimate_oscillator", "FLOAT"),
        bigquery.SchemaField("kama", "FLOAT"),
        bigquery.SchemaField("ppo", "FLOAT"),
        bigquery.SchemaField("pvo", "FLOAT"),
        bigquery.SchemaField("awesome_oscillator", "FLOAT"),
        bigquery.SchemaField("atr", "FLOAT"),
        bigquery.SchemaField("obv", "FLOAT"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Daily cryptocurrency OHLCV data with 29 technical indicators"

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✓ Table crypto_analysis created with {len(schema)} fields")
    except Exception as e:
        print(f"Error creating table: {e}")
        return False

    return True


def create_hourly_table():
    """Create hourly crypto data table"""
    print("\nCreating hourly crypto data table...")

    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{DATASET_ID}.crypto_hourly_data"

    schema = [
        bigquery.SchemaField("pair", "STRING"),
        bigquery.SchemaField("symbol", "STRING"),
        bigquery.SchemaField("altname", "STRING"),
        bigquery.SchemaField("base", "STRING"),
        bigquery.SchemaField("quote", "STRING"),
        bigquery.SchemaField("timestamp", "INTEGER"),
        bigquery.SchemaField("datetime", "TIMESTAMP"),
        bigquery.SchemaField("open", "FLOAT"),
        bigquery.SchemaField("open_price", "FLOAT"),
        bigquery.SchemaField("high", "FLOAT"),
        bigquery.SchemaField("low", "FLOAT"),
        bigquery.SchemaField("close", "FLOAT"),
        bigquery.SchemaField("vwap", "FLOAT"),
        bigquery.SchemaField("volume", "FLOAT"),
        bigquery.SchemaField("count", "INTEGER"),
        bigquery.SchemaField("hi_lo", "FLOAT"),
        bigquery.SchemaField("pct_hi_lo_over_lo", "FLOAT"),
        bigquery.SchemaField("rsi", "FLOAT"),
        bigquery.SchemaField("macd", "FLOAT"),
        bigquery.SchemaField("macd_signal", "FLOAT"),
        bigquery.SchemaField("macd_hist", "FLOAT"),
        bigquery.SchemaField("bb_upper", "FLOAT"),
        bigquery.SchemaField("bb_lower", "FLOAT"),
        bigquery.SchemaField("bb_percent", "FLOAT"),
        bigquery.SchemaField("ema_12", "FLOAT"),
        bigquery.SchemaField("ema_26", "FLOAT"),
        bigquery.SchemaField("ema_50", "FLOAT"),
        bigquery.SchemaField("ma_50", "FLOAT"),
        bigquery.SchemaField("sma_20", "FLOAT"),
        bigquery.SchemaField("sma_200", "FLOAT"),
        bigquery.SchemaField("stoch_k", "FLOAT"),
        bigquery.SchemaField("stoch_d", "FLOAT"),
        bigquery.SchemaField("williams_r", "FLOAT"),
        bigquery.SchemaField("adx", "FLOAT"),
        bigquery.SchemaField("cci", "FLOAT"),
        bigquery.SchemaField("roc", "FLOAT"),
        bigquery.SchemaField("momentum", "FLOAT"),
        bigquery.SchemaField("trix", "FLOAT"),
        bigquery.SchemaField("ultimate_oscillator", "FLOAT"),
        bigquery.SchemaField("kama", "FLOAT"),
        bigquery.SchemaField("ppo", "FLOAT"),
        bigquery.SchemaField("pvo", "FLOAT"),
        bigquery.SchemaField("awesome_oscillator", "FLOAT"),
        bigquery.SchemaField("atr", "FLOAT"),
        bigquery.SchemaField("obv", "FLOAT"),
        bigquery.SchemaField("fetched_at", "TIMESTAMP"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Hourly cryptocurrency OHLCV data with 29 technical indicators"

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✓ Table crypto_hourly_data created with {len(schema)} fields")
    except Exception as e:
        print(f"Error creating table: {e}")
        return False

    return True


def create_5min_table():
    """Create 5-minute top-10 gainers table"""
    print("\nCreating 5-minute top-10 gainers table...")

    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{DATASET_ID}.crypto_5min_top10_gainers"

    schema = [
        bigquery.SchemaField("pair", "STRING"),
        bigquery.SchemaField("symbol", "STRING"),
        bigquery.SchemaField("timestamp", "INTEGER"),
        bigquery.SchemaField("datetime", "TIMESTAMP"),
        bigquery.SchemaField("open", "FLOAT"),
        bigquery.SchemaField("open_price", "FLOAT"),
        bigquery.SchemaField("high", "FLOAT"),
        bigquery.SchemaField("low", "FLOAT"),
        bigquery.SchemaField("close", "FLOAT"),
        bigquery.SchemaField("vwap", "FLOAT"),
        bigquery.SchemaField("volume", "FLOAT"),
        bigquery.SchemaField("count", "INTEGER"),
        bigquery.SchemaField("hi_lo", "FLOAT"),
        bigquery.SchemaField("pct_hi_lo_over_lo", "FLOAT"),
        bigquery.SchemaField("rsi", "FLOAT"),
        bigquery.SchemaField("macd", "FLOAT"),
        bigquery.SchemaField("macd_signal", "FLOAT"),
        bigquery.SchemaField("macd_hist", "FLOAT"),
        bigquery.SchemaField("bb_upper", "FLOAT"),
        bigquery.SchemaField("bb_lower", "FLOAT"),
        bigquery.SchemaField("bb_percent", "FLOAT"),
        bigquery.SchemaField("ema_12", "FLOAT"),
        bigquery.SchemaField("ema_26", "FLOAT"),
        bigquery.SchemaField("ema_50", "FLOAT"),
        bigquery.SchemaField("ma_50", "FLOAT"),
        bigquery.SchemaField("sma_20", "FLOAT"),
        bigquery.SchemaField("sma_200", "FLOAT"),
        bigquery.SchemaField("stoch_k", "FLOAT"),
        bigquery.SchemaField("stoch_d", "FLOAT"),
        bigquery.SchemaField("williams_r", "FLOAT"),
        bigquery.SchemaField("adx", "FLOAT"),
        bigquery.SchemaField("cci", "FLOAT"),
        bigquery.SchemaField("roc", "FLOAT"),
        bigquery.SchemaField("momentum", "FLOAT"),
        bigquery.SchemaField("trix", "FLOAT"),
        bigquery.SchemaField("ultimate_oscillator", "FLOAT"),
        bigquery.SchemaField("kama", "FLOAT"),
        bigquery.SchemaField("ppo", "FLOAT"),
        bigquery.SchemaField("pvo", "FLOAT"),
        bigquery.SchemaField("awesome_oscillator", "FLOAT"),
        bigquery.SchemaField("atr", "FLOAT"),
        bigquery.SchemaField("obv", "FLOAT"),
        bigquery.SchemaField("fetched_at", "TIMESTAMP"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "5-minute OHLCV data for top 10 hourly gainers with 29 technical indicators"

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✓ Table crypto_5min_top10_gainers created with {len(schema)} fields")
    except Exception as e:
        print(f"Error creating table: {e}")
        return False

    return True


def main():
    print("="*70)
    print("CREATING BIGQUERY SCHEMA IN cryptobot-462709")
    print("="*70)
    print()

    if not create_dataset():
        sys.exit(1)

    if not create_daily_table():
        sys.exit(1)

    if not create_hourly_table():
        sys.exit(1)

    if not create_5min_table():
        sys.exit(1)

    print("\n" + "="*70)
    print("✓ ALL BIGQUERY TABLES CREATED SUCCESSFULLY!")
    print("="*70)
    print(f"\nDataset: {PROJECT_ID}.{DATASET_ID}")
    print("Tables:")
    print("  1. crypto_analysis (Daily data with indicators)")
    print("  2. crypto_hourly_data (Hourly data with indicators)")
    print("  3. crypto_5min_top10_gainers (5-min data with indicators)")
    print()


if __name__ == "__main__":
    main()
