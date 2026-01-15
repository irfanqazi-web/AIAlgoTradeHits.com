"""
Intraday Stock Data Fetcher
Fetches hourly and 5-minute data for stocks from TwelveData
Stores in BigQuery for Rise Cycle Detection strategy
"""
import sys
import io
import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from google.cloud import bigquery

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = "cryptobot-462709"
DATASET_ID = "crypto_trading_data"
TWELVEDATA_API_KEY = os.getenv('TWELVEDATA_API_KEY', '16ee060fd4d34a628a14bcb6f0167565')

# TwelveData rate limit: 55 requests per minute for $229 plan
RATE_LIMIT_DELAY = 1.2  # seconds between requests

client = bigquery.Client(project=PROJECT_ID)


def create_intraday_tables():
    """Create hourly and 5min stock tables if they don't exist"""

    schema = [
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("open", "FLOAT64"),
        bigquery.SchemaField("high", "FLOAT64"),
        bigquery.SchemaField("low", "FLOAT64"),
        bigquery.SchemaField("close", "FLOAT64"),
        bigquery.SchemaField("volume", "INT64"),
        bigquery.SchemaField("exchange", "STRING"),
        bigquery.SchemaField("currency", "STRING"),
        bigquery.SchemaField("sector", "STRING"),
        bigquery.SchemaField("industry", "STRING"),
        bigquery.SchemaField("fetched_at", "TIMESTAMP"),
    ]

    tables = ['stocks_hourly', 'stocks_5min']

    for table_name in tables:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        table = bigquery.Table(table_id, schema=schema)
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="datetime"
        )
        table.clustering_fields = ["symbol"]

        try:
            client.create_table(table, exists_ok=True)
            print(f"  Table ready: {table_name}")
        except Exception as e:
            print(f"  Error creating {table_name}: {e}")


def get_sector_info(symbol):
    """Get sector/industry from master list"""
    query = f"""
    SELECT sector, industry
    FROM `{PROJECT_ID}.{DATASET_ID}.stocks_master_list`
    WHERE symbol = '{symbol}'
    LIMIT 1
    """
    try:
        result = list(client.query(query).result())
        if result:
            return result[0].sector, result[0].industry
    except:
        pass
    return None, None


def fetch_intraday_data(symbol, interval='1h', outputsize=100):
    """
    Fetch intraday data from TwelveData API

    Parameters:
        symbol: Stock symbol (e.g., 'AAPL')
        interval: '1h' for hourly, '5min' for 5-minute
        outputsize: Number of data points (max 5000)

    Returns:
        DataFrame with OHLCV data
    """
    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': symbol,
        'interval': interval,
        'outputsize': outputsize,
        'apikey': TWELVEDATA_API_KEY,
        'timezone': 'America/New_York'
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'values' not in data:
            if 'message' in data:
                print(f"    API error for {symbol}: {data['message']}")
            return pd.DataFrame()

        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])

        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype(int)

        df['symbol'] = symbol
        df['exchange'] = data.get('meta', {}).get('exchange', 'UNKNOWN')
        df['currency'] = data.get('meta', {}).get('currency', 'USD')

        # Get sector info
        sector, industry = get_sector_info(symbol)
        df['sector'] = sector
        df['industry'] = industry
        df['fetched_at'] = datetime.now(timezone.utc)

        return df

    except Exception as e:
        print(f"    Error fetching {symbol}: {e}")
        return pd.DataFrame()


def upload_to_bigquery(df, table_name):
    """Upload dataframe to BigQuery - using core fields only"""
    if len(df) == 0:
        return 0

    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Convert datetime to string for JSON upload - use only core OHLCV fields
    records = []
    for _, row in df.iterrows():
        record = {
            'symbol': row['symbol'],
            'datetime': row['datetime'].isoformat(),
            'open': float(row['open']) if pd.notna(row['open']) else None,
            'high': float(row['high']) if pd.notna(row['high']) else None,
            'low': float(row['low']) if pd.notna(row['low']) else None,
            'close': float(row['close']) if pd.notna(row['close']) else None,
            'volume': int(row['volume']) if pd.notna(row['volume']) else 0
        }
        records.append(record)

    try:
        errors = client.insert_rows_json(table_id, records)
        if errors:
            print(f"    Upload errors: {errors[:2]}")
            return 0
        return len(records)
    except Exception as e:
        print(f"    Upload error: {e}")
        return 0


def fetch_top_stocks_intraday(symbols, interval='1h', days_back=5):
    """
    Fetch intraday data for a list of symbols

    Parameters:
        symbols: List of stock symbols
        interval: '1h' or '5min'
        days_back: How many days of data to fetch
    """
    table_name = 'stocks_hourly' if interval == '1h' else 'stocks_5min'
    outputsize = days_back * 8 if interval == '1h' else days_back * 78  # ~8 hours/day trading

    print(f"\nFetching {interval} data for {len(symbols)} symbols...")
    print(f"Target table: {table_name}")
    print(f"Data points per symbol: {outputsize}")

    total_uploaded = 0

    for i, symbol in enumerate(symbols, 1):
        print(f"  [{i}/{len(symbols)}] {symbol}...", end=" ")

        df = fetch_intraday_data(symbol, interval, outputsize)

        if len(df) > 0:
            uploaded = upload_to_bigquery(df, table_name)
            total_uploaded += uploaded
            print(f"{uploaded} records")
        else:
            print("no data")

        # Rate limit
        time.sleep(RATE_LIMIT_DELAY)

    return total_uploaded


def get_top_momentum_stocks(limit=50):
    """Get top momentum stocks from weekly data for intraday tracking"""
    query = f"""
    WITH latest_week AS (
        SELECT MAX(week_start) as max_week
        FROM `{PROJECT_ID}.{DATASET_ID}.weekly_stocks_all`
    )
    SELECT w.symbol, w.week_change_pct, w.volume, w.close
    FROM `{PROJECT_ID}.{DATASET_ID}.weekly_stocks_all` w
    CROSS JOIN latest_week lw
    WHERE w.week_start = lw.max_week
      AND w.week_change_pct IS NOT NULL
      AND w.volume > 100000
      AND w.close > 5
    ORDER BY ABS(w.week_change_pct) DESC
    LIMIT {limit}
    """

    try:
        results = list(client.query(query).result())
        symbols = [row.symbol for row in results]
        print(f"Found {len(symbols)} top momentum stocks")
        return symbols
    except Exception as e:
        print(f"Error getting momentum stocks: {e}")
        return []


# Default top stocks to track (major companies)
DEFAULT_TOP_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'JNJ',
    'V', 'XOM', 'JPM', 'PG', 'MA', 'HD', 'CVX', 'ABBV', 'MRK', 'LLY',
    'PEP', 'KO', 'COST', 'AVGO', 'TMO', 'MCD', 'WMT', 'CSCO', 'ACN', 'ABT',
    'CRM', 'DHR', 'VZ', 'ADBE', 'NKE', 'CMCSA', 'TXN', 'PM', 'NEE', 'RTX',
    'AMD', 'INTC', 'QCOM', 'IBM', 'NOW', 'ORCL', 'INTU', 'AMAT', 'NFLX', 'PYPL'
]


if __name__ == "__main__":
    print("=" * 60)
    print("INTRADAY STOCK DATA FETCHER")
    print(f"Started: {datetime.now(timezone.utc)}")
    print("=" * 60)

    # Create tables
    print("\n1. Creating intraday tables...")
    create_intraday_tables()

    # Try to get momentum stocks, fall back to defaults
    print("\n2. Getting stocks to track...")
    symbols = get_top_momentum_stocks(50)
    if not symbols:
        print("   Using default top 50 stocks")
        symbols = DEFAULT_TOP_STOCKS

    # Fetch hourly data
    print("\n3. Fetching hourly data...")
    hourly_count = fetch_top_stocks_intraday(symbols[:25], interval='1h', days_back=5)
    print(f"   Total hourly records: {hourly_count}")

    # Fetch 5-minute data (fewer symbols due to API limits)
    print("\n4. Fetching 5-minute data...")
    fivemin_count = fetch_top_stocks_intraday(symbols[:10], interval='5min', days_back=2)
    print(f"   Total 5-min records: {fivemin_count}")

    print("\n" + "=" * 60)
    print("INTRADAY FETCH COMPLETE")
    print("=" * 60)
    print(f"""
Data fetched:
  - Hourly: {hourly_count} records for {min(25, len(symbols))} symbols
  - 5-min: {fivemin_count} records for {min(10, len(symbols))} symbols

Tables populated:
  - stocks_hourly: For Rise Cycle Detection (hourly)
  - stocks_5min: For Rise Cycle Detection (5-minute)

Next steps:
  - Run rise_cycle_detector.py to analyze cycles
  - Set up Cloud Scheduler to run this hourly
""")
