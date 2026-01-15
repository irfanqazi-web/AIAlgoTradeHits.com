"""
Automated Historical Daily Data Fetcher for All 6 Asset Types
Fetches maximum historical data from Twelve Data API until quota exhausted
Uploads to BigQuery with technical indicators for AI training

Rate Limit: 800 API calls/day, 8 calls/minute
Each symbol uses 1 API call for time_series data
"""
import requests
import time
import sys
import io
import warnings
import json
import os
from datetime import datetime, timezone
from google.cloud import bigquery
import pandas as pd
import numpy as np

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

warnings.filterwarnings('ignore')

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TWELVE_DATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'

# Rate limiting: 8 calls/minute = 7.5 seconds between calls
RATE_LIMIT_SECONDS = 8

# Progress file to track completed symbols
PROGRESS_FILE = 'historical_fetch_progress.json'

# All symbols to fetch by asset type
SYMBOLS = {
    'stocks': {
        'table': 'stocks_historical_daily',
        'symbols': [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'JNJ',
            'V', 'JPM', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV', 'PFE', 'KO',
            'PEP', 'COST', 'AVGO', 'TMO', 'MCD', 'WMT', 'CSCO', 'ABT', 'ACN', 'DHR',
            'NKE', 'DIS', 'VZ', 'ADBE', 'CRM', 'TXN', 'NEE', 'PM', 'UNP', 'RTX',
            'INTC', 'AMD', 'IBM', 'QCOM', 'ORCL', 'LOW', 'CAT', 'BA', 'GE', 'SPGI'
        ]
    },
    'cryptos': {
        'table': 'cryptos_historical_daily',
        'symbols': [
            'BTC/USD', 'ETH/USD', 'XRP/USD', 'SOL/USD', 'ADA/USD', 'DOGE/USD', 'DOT/USD',
            'AVAX/USD', 'LINK/USD', 'LTC/USD', 'UNI/USD', 'ATOM/USD', 'XLM/USD',
            'ALGO/USD', 'VET/USD', 'FIL/USD', 'AAVE/USD', 'EOS/USD', 'XTZ/USD', 'SHIB/USD'
        ]
    },
    'etfs': {
        'table': 'etfs_historical_daily',
        'symbols': [
            'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO', 'EFA', 'EEM',
            'AGG', 'BND', 'LQD', 'TLT', 'GLD', 'SLV', 'USO', 'XLF', 'XLK', 'XLE',
            'XLV', 'XLI', 'XLY', 'XLP', 'XLU', 'ARKK', 'ARKG', 'ARKF', 'VNQ', 'SCHD'
        ]
    },
    'forex': {
        'table': 'forex_historical_daily',
        'symbols': [
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',
            'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY', 'EUR/CHF', 'EUR/AUD', 'GBP/AUD',
            'USD/SGD', 'USD/HKD', 'USD/MXN', 'USD/ZAR', 'USD/INR', 'EUR/CAD'
        ]
    },
    'indices': {
        'table': 'indices_historical_daily',
        'symbols': [
            'SPX', 'NDX', 'DJI', 'RUT', 'VIX', 'FTSE', 'DAX', 'CAC', 'N225', 'HSI',
            'STOXX50E', 'IBEX', 'AEX', 'SMI'
        ]
    },
    'commodities': {
        'table': 'commodities_historical_daily',
        'symbols': [
            'XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD', 'CL', 'BZ', 'NG', 'HO',
            'ZC', 'ZW', 'ZS', 'KC', 'CC', 'SB', 'CT', 'LC'
        ]
    }
}


def load_progress():
    """Load progress from file"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'completed': [], 'api_calls': 0, 'last_run': None}


def save_progress(progress):
    """Save progress to file"""
    progress['last_run'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def calculate_technical_indicators(df):
    """Calculate 50+ technical indicators for AI training"""
    if len(df) < 5:
        return df

    # Price columns
    close = df['close'].astype(float)
    high = df['high'].astype(float)
    low = df['low'].astype(float)
    volume = df['volume'].astype(float) if 'volume' in df.columns else pd.Series([0]*len(df))

    # Moving Averages
    for period in [5, 10, 20, 50, 100, 200]:
        if len(df) >= period:
            df[f'sma_{period}'] = close.rolling(window=period).mean()
            df[f'ema_{period}'] = close.ewm(span=period, adjust=False).mean()

    # MACD
    if len(df) >= 26:
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']

    # RSI
    for period in [7, 14, 21]:
        if len(df) >= period:
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss.replace(0, 0.0001)
            df[f'rsi_{period}'] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    if len(df) >= 20:
        sma20 = close.rolling(window=20).mean()
        std20 = close.rolling(window=20).std()
        df['bb_upper'] = sma20 + (std20 * 2)
        df['bb_middle'] = sma20
        df['bb_lower'] = sma20 - (std20 * 2)
        df['bb_width'] = ((df['bb_upper'] - df['bb_lower']) / df['bb_middle']) * 100
        df['bb_percent'] = ((close - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])) * 100

    # ATR
    for period in [7, 14]:
        if len(df) >= period:
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            df[f'atr_{period}'] = tr.rolling(window=period).mean()

    # Stochastic
    if len(df) >= 14:
        lowest_low = low.rolling(window=14).min()
        highest_high = high.rolling(window=14).max()
        df['stoch_k'] = ((close - lowest_low) / (highest_high - lowest_low)) * 100
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # Williams %R
    if len(df) >= 14:
        df['williams_r'] = ((highest_high - close) / (highest_high - lowest_low)) * -100

    # CCI
    if len(df) >= 20:
        tp = (high + low + close) / 3
        df['cci'] = (tp - tp.rolling(window=20).mean()) / (0.015 * tp.rolling(window=20).std())

    # ROC (Rate of Change)
    for period in [5, 10, 20]:
        if len(df) >= period:
            df[f'roc_{period}'] = ((close - close.shift(period)) / close.shift(period)) * 100

    # OBV
    if len(df) >= 2 and volume.sum() > 0:
        obv = [0]
        for i in range(1, len(df)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.append(obv[-1] + volume.iloc[i])
            elif close.iloc[i] < close.iloc[i-1]:
                obv.append(obv[-1] - volume.iloc[i])
            else:
                obv.append(obv[-1])
        df['obv'] = obv

    # Volatility
    if len(df) >= 20:
        returns = close.pct_change()
        df['volatility_10'] = returns.rolling(window=10).std() * np.sqrt(252) * 100
        df['volatility_20'] = returns.rolling(window=20).std() * np.sqrt(252) * 100

    # Price features
    df['daily_return_pct'] = close.pct_change() * 100
    df['high_low_pct'] = ((high - low) / close) * 100

    # Lagged features
    for lag in [1, 2, 3, 5, 10]:
        if len(df) >= lag:
            df[f'close_lag_{lag}'] = close.shift(lag)
            df[f'return_lag_{lag}'] = df['daily_return_pct'].shift(lag)

    # Target variables (for supervised learning)
    df['target_return_1d'] = close.shift(-1).pct_change() * 100
    df['target_return_5d'] = ((close.shift(-5) - close) / close) * 100
    df['target_direction_1d'] = (close.shift(-1) > close).astype(int)

    # Signal categories
    if 'rsi_14' in df.columns:
        df['momentum_signal'] = df['rsi_14'].apply(
            lambda x: 'overbought' if x > 70 else ('oversold' if x < 30 else ('bullish' if x > 50 else 'bearish'))
        )

    if 'sma_50' in df.columns and 'sma_200' in df.columns:
        df['trend_signal'] = df.apply(
            lambda row: 'strong_bullish' if row['close'] > row['sma_50'] > row['sma_200']
            else ('bullish' if row['close'] > row['sma_50'] else
                  ('strong_bearish' if row['close'] < row['sma_50'] < row['sma_200'] else 'bearish')),
            axis=1
        )

    return df


def fetch_historical_data(symbol, outputsize=5000):
    """Fetch historical daily data from Twelve Data API"""
    try:
        url = f"https://api.twelvedata.com/time_series"
        params = {
            'symbol': symbol,
            'interval': '1day',
            'outputsize': outputsize,
            'apikey': TWELVE_DATA_API_KEY
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        # Check for rate limit or quota exceeded
        if 'code' in data:
            if data['code'] == 429:
                print(f"  Rate limit hit! Waiting 60 seconds...")
                time.sleep(60)
                return None
            elif data['code'] == 401 or 'quota' in data.get('message', '').lower():
                print(f"  API quota exceeded!")
                return 'QUOTA_EXCEEDED'
            else:
                print(f"  API Error: {data.get('message', 'Unknown')}")
                return None

        if 'values' not in data:
            print(f"  No data returned")
            return None

        # Convert to DataFrame
        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Convert numeric columns
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Sort by date ascending
        df = df.sort_values('datetime').reset_index(drop=True)

        return df

    except Exception as e:
        print(f"  Exception: {str(e)[:50]}")
        return None


def create_table_if_not_exists(client, table_id, asset_type):
    """Create BigQuery table with appropriate schema"""
    schema = [
        bigquery.SchemaField("symbol", "STRING"),
        bigquery.SchemaField("datetime", "TIMESTAMP"),
        bigquery.SchemaField("open", "FLOAT64"),
        bigquery.SchemaField("high", "FLOAT64"),
        bigquery.SchemaField("low", "FLOAT64"),
        bigquery.SchemaField("close", "FLOAT64"),
        bigquery.SchemaField("volume", "FLOAT64"),
        bigquery.SchemaField("sma_5", "FLOAT64"),
        bigquery.SchemaField("sma_10", "FLOAT64"),
        bigquery.SchemaField("sma_20", "FLOAT64"),
        bigquery.SchemaField("sma_50", "FLOAT64"),
        bigquery.SchemaField("sma_100", "FLOAT64"),
        bigquery.SchemaField("sma_200", "FLOAT64"),
        bigquery.SchemaField("ema_5", "FLOAT64"),
        bigquery.SchemaField("ema_10", "FLOAT64"),
        bigquery.SchemaField("ema_20", "FLOAT64"),
        bigquery.SchemaField("ema_50", "FLOAT64"),
        bigquery.SchemaField("ema_100", "FLOAT64"),
        bigquery.SchemaField("ema_200", "FLOAT64"),
        bigquery.SchemaField("macd", "FLOAT64"),
        bigquery.SchemaField("macd_signal", "FLOAT64"),
        bigquery.SchemaField("macd_hist", "FLOAT64"),
        bigquery.SchemaField("rsi_7", "FLOAT64"),
        bigquery.SchemaField("rsi_14", "FLOAT64"),
        bigquery.SchemaField("rsi_21", "FLOAT64"),
        bigquery.SchemaField("bb_upper", "FLOAT64"),
        bigquery.SchemaField("bb_middle", "FLOAT64"),
        bigquery.SchemaField("bb_lower", "FLOAT64"),
        bigquery.SchemaField("bb_width", "FLOAT64"),
        bigquery.SchemaField("bb_percent", "FLOAT64"),
        bigquery.SchemaField("atr_7", "FLOAT64"),
        bigquery.SchemaField("atr_14", "FLOAT64"),
        bigquery.SchemaField("stoch_k", "FLOAT64"),
        bigquery.SchemaField("stoch_d", "FLOAT64"),
        bigquery.SchemaField("williams_r", "FLOAT64"),
        bigquery.SchemaField("cci", "FLOAT64"),
        bigquery.SchemaField("roc_5", "FLOAT64"),
        bigquery.SchemaField("roc_10", "FLOAT64"),
        bigquery.SchemaField("roc_20", "FLOAT64"),
        bigquery.SchemaField("obv", "FLOAT64"),
        bigquery.SchemaField("volatility_10", "FLOAT64"),
        bigquery.SchemaField("volatility_20", "FLOAT64"),
        bigquery.SchemaField("daily_return_pct", "FLOAT64"),
        bigquery.SchemaField("high_low_pct", "FLOAT64"),
        bigquery.SchemaField("close_lag_1", "FLOAT64"),
        bigquery.SchemaField("close_lag_2", "FLOAT64"),
        bigquery.SchemaField("close_lag_3", "FLOAT64"),
        bigquery.SchemaField("close_lag_5", "FLOAT64"),
        bigquery.SchemaField("close_lag_10", "FLOAT64"),
        bigquery.SchemaField("return_lag_1", "FLOAT64"),
        bigquery.SchemaField("return_lag_2", "FLOAT64"),
        bigquery.SchemaField("return_lag_3", "FLOAT64"),
        bigquery.SchemaField("target_return_1d", "FLOAT64"),
        bigquery.SchemaField("target_return_5d", "FLOAT64"),
        bigquery.SchemaField("target_direction_1d", "INT64"),
        bigquery.SchemaField("momentum_signal", "STRING"),
        bigquery.SchemaField("trend_signal", "STRING"),
        bigquery.SchemaField("asset_type", "STRING"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    try:
        client.create_table(table)
        print(f"  Created table {table_id}")
    except Exception as e:
        if "Already Exists" in str(e):
            pass  # Table already exists
        else:
            print(f"  Table creation note: {str(e)[:50]}")


def upload_to_bigquery(client, df, table_id, symbol, asset_type):
    """Upload DataFrame to BigQuery"""
    if df is None or len(df) == 0:
        return 0

    # Add metadata
    df['symbol'] = symbol
    df['asset_type'] = asset_type
    df['fetch_timestamp'] = datetime.now(timezone.utc).isoformat()

    # Convert datetime to string for BigQuery
    df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Select only columns that exist
    valid_columns = [
        'symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume',
        'sma_5', 'sma_10', 'sma_20', 'sma_50', 'sma_100', 'sma_200',
        'ema_5', 'ema_10', 'ema_20', 'ema_50', 'ema_100', 'ema_200',
        'macd', 'macd_signal', 'macd_hist',
        'rsi_7', 'rsi_14', 'rsi_21',
        'bb_upper', 'bb_middle', 'bb_lower', 'bb_width', 'bb_percent',
        'atr_7', 'atr_14', 'stoch_k', 'stoch_d', 'williams_r', 'cci',
        'roc_5', 'roc_10', 'roc_20', 'obv',
        'volatility_10', 'volatility_20', 'daily_return_pct', 'high_low_pct',
        'close_lag_1', 'close_lag_2', 'close_lag_3', 'close_lag_5', 'close_lag_10',
        'return_lag_1', 'return_lag_2', 'return_lag_3',
        'target_return_1d', 'target_return_5d', 'target_direction_1d',
        'momentum_signal', 'trend_signal', 'asset_type', 'fetch_timestamp'
    ]

    available_columns = [c for c in valid_columns if c in df.columns]
    df_upload = df[available_columns].copy()

    # Replace NaN with None for JSON serialization
    df_upload = df_upload.replace({np.nan: None, np.inf: None, -np.inf: None})

    # Convert to records
    records = df_upload.to_dict('records')

    # Upload in batches
    batch_size = 500
    total_uploaded = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        try:
            errors = client.insert_rows_json(table_id, batch)
            if errors:
                print(f"    Batch {i//batch_size + 1} errors: {len(errors)}")
            else:
                total_uploaded += len(batch)
        except Exception as e:
            print(f"    Upload error: {str(e)[:50]}")

    return total_uploaded


def main():
    print("=" * 70)
    print("AUTOMATED HISTORICAL DATA FETCHER")
    print("Fetching maximum daily data for all 6 asset types")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Load progress
    progress = load_progress()
    completed = set(progress.get('completed', []))
    api_calls = progress.get('api_calls', 0)

    print(f"\nProgress: {len(completed)} symbols completed, {api_calls} API calls used")
    print(f"Remaining daily quota: ~{800 - api_calls} calls\n")

    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    total_records = 0
    quota_exceeded = False

    for asset_type, config in SYMBOLS.items():
        if quota_exceeded:
            break

        table_name = config['table']
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        symbols = config['symbols']

        print(f"\n{'='*60}")
        print(f"PROCESSING {asset_type.upper()}")
        print(f"Table: {table_name}")
        print(f"Symbols: {len(symbols)}")
        print(f"{'='*60}")

        # Create table if not exists
        create_table_if_not_exists(client, table_id, asset_type)

        for i, symbol in enumerate(symbols):
            symbol_key = f"{asset_type}:{symbol}"

            if symbol_key in completed:
                print(f"[{i+1}/{len(symbols)}] {symbol} - Already completed, skipping")
                continue

            print(f"[{i+1}/{len(symbols)}] Fetching {symbol}...", end=" ")
            sys.stdout.flush()

            # Fetch data
            df = fetch_historical_data(symbol)
            api_calls += 1

            if isinstance(df, str) and df == 'QUOTA_EXCEEDED':
                print("\n\n*** API QUOTA EXCEEDED ***")
                print("Run this script again tomorrow to continue.")
                quota_exceeded = True
                break

            if df is None or (hasattr(df, '__len__') and len(df) == 0):
                print("No data")
                time.sleep(RATE_LIMIT_SECONDS)
                continue

            print(f"Got {len(df)} days", end=" ")

            # Calculate indicators
            df = calculate_technical_indicators(df)

            # Upload to BigQuery
            uploaded = upload_to_bigquery(client, df, table_id, symbol, asset_type)

            if uploaded > 0:
                print(f"- Uploaded {uploaded} records")
                completed.add(symbol_key)
                total_records += uploaded
            else:
                print("- Upload failed")

            # Save progress after each symbol
            progress['completed'] = list(completed)
            progress['api_calls'] = api_calls
            save_progress(progress)

            # Rate limiting
            time.sleep(RATE_LIMIT_SECONDS)

    print("\n" + "=" * 70)
    print("FETCH SESSION COMPLETE")
    print("=" * 70)
    print(f"Total symbols completed: {len(completed)}")
    print(f"Total API calls used: {api_calls}")
    print(f"Total records uploaded: {total_records}")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if quota_exceeded:
        print("\n*** Run this script again tomorrow to continue ***")
    else:
        remaining_symbols = sum(len(c['symbols']) for c in SYMBOLS.values()) - len(completed)
        if remaining_symbols > 0:
            print(f"\n{remaining_symbols} symbols remaining. Run again to continue.")
        else:
            print("\n*** All historical data has been fetched! ***")


if __name__ == '__main__':
    main()
