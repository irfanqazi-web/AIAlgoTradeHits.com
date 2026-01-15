"""
High-Speed TwelveData Fetcher for $229 Growing Plan
Optimized for 800 API calls/minute rate limit
Uploads to aialgotradehits unified BigQuery project
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timezone
import time
import json
import os
import hashlib
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'
PROGRESS_FILE = 'highspeed_fetch_progress.json'

# Rate limiting for $229 Growing Plan (800 calls/min = ~13.3 calls/sec)
# Using 10 calls/sec to be safe
CALLS_PER_SECOND = 10
CALL_DELAY = 1.0 / CALLS_PER_SECOND

# Thread-safe rate limiter
rate_lock = threading.Lock()
last_call_time = 0

# Top 100 Cryptos (USD pairs)
TOP_CRYPTOS = [
    'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'SOL/USD', 'DOGE/USD', 'ADA/USD',
    'AVAX/USD', 'LINK/USD', 'DOT/USD', 'TRX/USD', 'MATIC/USD', 'SHIB/USD', 'LTC/USD',
    'ATOM/USD', 'UNI/USD', 'XMR/USD', 'ETC/USD', 'XLM/USD', 'BCH/USD', 'NEAR/USD',
    'FIL/USD', 'AAVE/USD', 'VET/USD', 'ALGO/USD', 'HBAR/USD', 'ICP/USD', 'APT/USD',
    'SAND/USD', 'MANA/USD', 'AXS/USD', 'EGLD/USD', 'XTZ/USD', 'THETA/USD', 'EOS/USD',
    'FLOW/USD', 'IMX/USD', 'NEO/USD', 'KAVA/USD', 'RUNE/USD', 'CHZ/USD', 'CRV/USD',
    'COMP/USD', 'SNX/USD', 'LDO/USD', 'ENJ/USD', 'GALA/USD', 'CAKE/USD', 'KLAY/USD',
    'BAT/USD', 'ZEC/USD', 'DASH/USD', 'WAVES/USD', 'SUSHI/USD', 'YFI/USD', 'GRT/USD',
    'FTM/USD', 'ONE/USD', 'CELO/USD', 'AR/USD', 'OP/USD', 'ARB/USD', 'MKR/USD',
    'QNT/USD', 'RPL/USD', 'INJ/USD', 'CFX/USD', 'SUI/USD', 'SEI/USD', 'TIA/USD',
    'STX/USD', 'RNDR/USD', 'WLD/USD', 'BLUR/USD', 'PEPE/USD', 'FLOKI/USD', 'BONK/USD',
    'FET/USD', 'AGIX/USD', 'OCEAN/USD', 'PENDLE/USD', 'GMX/USD', 'DYDX/USD', 'SNT/USD',
    '1INCH/USD', 'ANKR/USD', 'API3/USD', 'AUDIO/USD', 'BAND/USD', 'CELR/USD', 'CTK/USD',
    'DENT/USD', 'ENS/USD', 'HOT/USD', 'IOST/USD', 'JASMY/USD', 'KNC/USD', 'LRC/USD',
    'MASK/USD', 'STORJ/USD'
]

# Top 200 Stocks
TOP_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'JPM', 'V',
    'JNJ', 'UNH', 'MA', 'HD', 'PG', 'XOM', 'COST', 'ABBV', 'MRK', 'CVX',
    'LLY', 'PEP', 'KO', 'AVGO', 'WMT', 'MCD', 'CSCO', 'ACN', 'TMO', 'ABT',
    'CRM', 'DHR', 'NKE', 'LIN', 'TXN', 'NEE', 'PM', 'VZ', 'ORCL', 'RTX',
    'ADBE', 'HON', 'LOW', 'UPS', 'QCOM', 'INTC', 'AMGN', 'IBM', 'CAT', 'MS',
    'BA', 'GE', 'INTU', 'AMD', 'ISRG', 'AMAT', 'BKNG', 'GS', 'BLK', 'SBUX',
    'DE', 'PLD', 'AXP', 'GILD', 'MDLZ', 'ADI', 'REGN', 'VRTX', 'SYK', 'TJX',
    'CME', 'LRCX', 'SCHW', 'CVS', 'MMC', 'CB', 'C', 'CI', 'ZTS', 'EOG',
    'ETN', 'SO', 'DUK', 'SNPS', 'FI', 'BDX', 'NOC', 'BSX', 'EQIX', 'PGR',
    'MO', 'ICE', 'PNC', 'APD', 'CL', 'WM', 'SLB', 'EMR', 'ITW', 'FCX',
    'CDNS', 'SHW', 'AON', 'CMG', 'USB', 'GM', 'F', 'NSC', 'CSX', 'HUM',
    'MAR', 'ORLY', 'MPC', 'MCO', 'TGT', 'PSX', 'KLAC', 'ADP', 'MCHP', 'GD',
    'NXPI', 'OXY', 'AZO', 'HCA', 'PCAR', 'AEP', 'ROP', 'MNST', 'MSI', 'TFC',
    'MRNA', 'FTNT', 'PH', 'EXC', 'PAYX', 'KDP', 'COF', 'ROST', 'VLO', 'ADSK',
    'AIG', 'AFL', 'IDXX', 'HES', 'IQV', 'MSCI', 'DXCM', 'DVN', 'WELL', 'TEL',
    'CCI', 'AMT', 'SPG', 'PSA', 'O', 'DLR', 'EQR', 'CBRE', 'AVB', 'ARE',
    'PLTR', 'COIN', 'SHOP', 'SQ', 'PYPL', 'SNOW', 'CRWD', 'DDOG', 'ZS', 'NET',
    'PANW', 'OKTA', 'MDB', 'ESTC', 'TWLO', 'UBER', 'ABNB', 'RIVN', 'LCID', 'NIO',
    'LI', 'XPEV', 'GRAB', 'SE', 'MELI', 'NU', 'SOFI', 'ARM', 'SMCI', 'DELL',
    'HPE', 'HPQ', 'NTAP', 'WDC', 'ANET', 'KEYS', 'MRVL', 'FSR', 'MSTR', 'HMC'
]

# Top ETFs
TOP_ETFS = [
    'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO', 'EFA', 'EEM',
    'GLD', 'SLV', 'USO', 'TLT', 'AGG', 'BND', 'LQD', 'HYG', 'XLF', 'XLK',
    'XLE', 'XLV', 'XLY', 'XLP', 'XLI', 'XLB', 'XLU', 'XLRE', 'XLC', 'SMH',
    'SOXX', 'ARKK', 'ARKG', 'ARKF', 'IBB', 'XBI', 'XHB', 'XRT', 'KRE', 'VNQ',
    'FXI', 'MCHI', 'KWEB', 'EWJ', 'EWZ', 'EWY', 'EWW', 'EWC', 'EWA', 'VGK',
    'SCHD'
]

# Major Forex Pairs
TOP_FOREX = [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD', 'NZD/USD', 'USD/CHF',
    'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY', 'EUR/AUD', 'GBP/AUD', 'EUR/CAD',
    'GBP/CAD', 'AUD/CAD', 'NZD/JPY', 'GBP/NZD', 'EUR/NZD', 'AUD/NZD', 'CHF/JPY',
    'CAD/JPY', 'EUR/CHF', 'GBP/CHF', 'USD/MXN', 'USD/ZAR', 'USD/SGD', 'USD/HKD',
    'USD/INR', 'EUR/SGD'
]

# Major Indices
TOP_INDICES = [
    'SPX', 'NDX', 'DJI', 'VIX', 'FTSE', 'DAX', 'CAC', 'IBEX', 'AEX', 'SMI',
    'HSI', 'SSE', 'STI', 'SET', 'ASX', 'BSE', 'N225'
]

# Major Commodities
TOP_COMMODITIES = [
    'XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD', 'CL', 'BZ', 'NG', 'HO', 'RB',
    'ZC', 'ZS', 'ZW', 'KC', 'CC', 'SB', 'CT', 'HG', 'LC', 'LH'
]


def load_progress():
    """Load progress from file"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        'completed': [],
        'api_calls': 0,
        'last_run': None,
        'errors': []
    }


def save_progress(progress):
    """Save progress to file"""
    progress['last_run'] = datetime.now(timezone.utc).isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def rate_limited_call():
    """Ensure rate limiting between API calls"""
    global last_call_time
    with rate_lock:
        current_time = time.time()
        elapsed = current_time - last_call_time
        if elapsed < CALL_DELAY:
            time.sleep(CALL_DELAY - elapsed)
        last_call_time = time.time()


def fetch_time_series(symbol, interval='1day', outputsize=365):
    """Fetch OHLCV data from TwelveData with rate limiting"""
    rate_limited_call()

    try:
        url = f"{BASE_URL}/time_series"
        params = {
            'symbol': symbol,
            'interval': interval,
            'outputsize': outputsize,
            'apikey': TWELVEDATA_API_KEY,
            'format': 'JSON'
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'values' not in data:
            error_msg = data.get('message', 'Unknown error')
            if 'API credits' in error_msg or 'rate limit' in error_msg.lower():
                print(f"\n[!] Rate limit hit, waiting 60 seconds...")
                time.sleep(60)
                return fetch_time_series(symbol, interval, outputsize)
            return None, error_msg

        df = pd.DataFrame(data['values'])
        df['symbol'] = symbol.replace('/', '')
        df['original_symbol'] = symbol
        df['name'] = data.get('meta', {}).get('name', symbol)
        df['exchange'] = data.get('meta', {}).get('exchange', '')
        df['currency'] = data.get('meta', {}).get('currency', 'USD')
        df['type'] = data.get('meta', {}).get('type', '')

        # Convert types
        df['datetime'] = pd.to_datetime(df['datetime'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df, None

    except Exception as e:
        return None, str(e)


def calculate_technical_indicators(df):
    """Calculate all technical indicators"""
    if len(df) < 50:
        return df

    df = df.sort_values('datetime').reset_index(drop=True)

    # Ensure volume column exists (crypto may not have it)
    if 'volume' not in df.columns:
        df['volume'] = 0

    # Moving Averages
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    if len(df) >= 200:
        df['sma_200'] = df['close'].rolling(window=200).mean()
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # Bollinger Bands
    df['bb_middle'] = df['sma_20']
    std_20 = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (std_20 * 2)
    df['bb_lower'] = df['bb_middle'] - (std_20 * 2)

    # ATR
    tr1 = df['high'] - df['low']
    tr2 = abs(df['high'] - df['close'].shift())
    tr3 = abs(df['low'] - df['close'].shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr'] = tr.rolling(window=14).mean()

    # ADX
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    if df['atr'].notna().any():
        df['plus_di'] = 100 * (plus_dm.rolling(window=14).mean() / df['atr'])
        df['minus_di'] = 100 * (minus_dm.rolling(window=14).mean() / df['atr'])
        dx = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
        df['adx'] = dx.rolling(window=14).mean()

    # Stochastic
    high_14 = df['high'].rolling(window=14).max()
    low_14 = df['low'].rolling(window=14).min()
    df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # OBV (only if volume data exists)
    if df['volume'].sum() > 0:
        df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
    else:
        df['obv'] = 0

    # Price Changes
    df['price_change_1d'] = df['close'].pct_change(1) * 100
    df['price_change_5d'] = df['close'].pct_change(5) * 100
    df['price_change_20d'] = df['close'].pct_change(20) * 100

    # Clean up
    df = df.replace({np.nan: None, np.inf: None, -np.inf: None})

    return df


def generate_record_id(symbol, datetime_val):
    """Generate unique record ID"""
    key = f"{symbol}_{datetime_val}"
    return hashlib.md5(key.encode()).hexdigest()[:16]


def upload_to_bigquery(df, table_name, client):
    """Upload dataframe to BigQuery"""
    if df is None or df.empty:
        return 0

    try:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

        # Generate unique IDs
        df['id'] = df.apply(lambda row: generate_record_id(row['symbol'], row['datetime']), axis=1)

        # Add date column
        df['date'] = pd.to_datetime(df['datetime']).dt.date

        # Add metadata
        df['data_source'] = 'twelvedata'
        df['created_at'] = datetime.now(timezone.utc)
        df['updated_at'] = datetime.now(timezone.utc)

        # Upload with schema flexibility
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
        )

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()

        return len(df)

    except Exception as e:
        print(f"  [!] Upload error: {e}")
        return 0


def fetch_asset_category(category, symbols, table_name, progress, client):
    """Fetch all symbols for a category"""
    print(f"\n{'='*70}")
    print(f"FETCHING {category.upper()}")
    print(f"{'='*70}")

    total_rows = 0

    for i, symbol in enumerate(symbols):
        key = f"{category}:{symbol}"

        if key in progress['completed']:
            continue

        print(f"[{i+1}/{len(symbols)}] {symbol}...", end=" ", flush=True)

        df, error = fetch_time_series(symbol)
        progress['api_calls'] += 1

        if error:
            print(f"ERROR: {error}")
            progress['errors'].append({'symbol': symbol, 'error': error})
            continue

        if df is not None and not df.empty:
            df['asset_type'] = category
            df = calculate_technical_indicators(df)
            rows = upload_to_bigquery(df, table_name, client)
            total_rows += rows
            print(f"OK ({len(df)} rows)")
            progress['completed'].append(key)
        else:
            print("NO DATA")

        # Save progress every 10 symbols
        if (i + 1) % 10 == 0:
            save_progress(progress)
            print(f"  [Progress saved: {len(progress['completed'])} completed, {progress['api_calls']} API calls]")

    return total_rows


def main():
    parser = argparse.ArgumentParser(description='High-Speed TwelveData Fetcher')
    parser.add_argument('--category', type=str, default='all',
                        help='Category: cryptos, stocks, etfs, forex, indices, commodities, or all')
    parser.add_argument('--outputsize', type=int, default=365,
                        help='Number of data points to fetch (default: 365 for 1 year)')
    args = parser.parse_args()

    print("="*70)
    print("HIGH-SPEED TWELVEDATA FETCHER")
    print("$229 Growing Plan - 800 calls/min")
    print(f"Target Project: {PROJECT_ID}")
    print("="*70)

    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    # Load progress
    progress = load_progress()
    print(f"Resuming from: {len(progress['completed'])} completed, {progress['api_calls']} API calls")

    # Create tables if needed
    categories = {
        'cryptos': (TOP_CRYPTOS, 'crypto_daily'),
        'stocks': (TOP_STOCKS, 'stock_daily'),
        'etfs': (TOP_ETFS, 'etf_daily'),
        'forex': (TOP_FOREX, 'forex_daily'),
        'indices': (TOP_INDICES, 'indices_daily'),
        'commodities': (TOP_COMMODITIES, 'commodities_daily')
    }

    total_rows = 0
    start_time = time.time()

    if args.category == 'all':
        for cat_name, (symbols, table) in categories.items():
            rows = fetch_asset_category(cat_name, symbols, table, progress, client)
            total_rows += rows
            save_progress(progress)
    else:
        if args.category in categories:
            symbols, table = categories[args.category]
            total_rows = fetch_asset_category(args.category, symbols, table, progress, client)
            save_progress(progress)
        else:
            print(f"Unknown category: {args.category}")
            return

    elapsed = time.time() - start_time

    print("\n" + "="*70)
    print("FETCH COMPLETE")
    print(f"Total rows uploaded: {total_rows}")
    print(f"Total API calls: {progress['api_calls']}")
    print(f"Completed symbols: {len(progress['completed'])}")
    print(f"Time elapsed: {elapsed/60:.1f} minutes")
    print(f"Average rate: {progress['api_calls']/(elapsed/60):.1f} calls/min")
    print("="*70)


if __name__ == "__main__":
    main()
