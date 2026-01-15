"""
Weekly Data Fetcher for All 7 Asset Types
Fetches weekly OHLCV + 82 technical indicator fields from Twelvedata
Assets: Stocks, Crypto, ETFs, Forex, Indices, Commodities, Funds
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timedelta
import time
import json
import os
import hashlib

# Add utils to path
import sys
sys.path.insert(0, 'C:/1AITrading/Trading')
from utils.datetime_utils import get_utc_now_str, to_bigquery_datetime, to_bigquery_date

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'
PROGRESS_FILE = 'weekly_all_assets_progress.json'

# Rate limiting for $229 Growing Plan (800 calls/min)
CALLS_PER_MINUTE = 700
CALL_DELAY = 60.0 / CALLS_PER_MINUTE

# Asset configurations - ALL symbols from Twelvedata API
ASSET_CONFIGS = {
    'stocks': {
        'table': 'weekly_stocks_all',
        'master_table': 'v2_stocks_master',  # Get from BigQuery master
        'symbol_field': 'symbol'
    },
    'crypto': {
        'table': 'weekly_crypto_all',
        'api_endpoint': 'cryptocurrencies',  # Get ALL from Twelvedata API
        'filter': {'currency_quote': 'USD'}  # Filter USD pairs only
    },
    'etfs': {
        'table': 'weekly_etfs_all',
        'api_endpoint': 'etf',
        'filter': {'country': 'United States'}  # US ETFs only
    },
    'forex': {
        'table': 'weekly_forex_all',
        'api_endpoint': 'forex_pairs',
        'filter': {}  # Get all forex pairs
    },
    'indices': {
        'table': 'weekly_indices_all',
        'api_endpoint': 'indices',
        'filter': {}  # Get all indices
    },
    'commodities': {
        'table': 'weekly_commodities_all',
        'api_endpoint': 'commodities',
        'filter': {}  # Get all commodities (only 60)
    },
    'funds': {
        'table': 'weekly_funds_all',
        'api_endpoint': 'funds',
        'filter': {'country': 'United States'}  # US funds only (otherwise 251K!)
    }
}


def load_progress():
    """Load progress from file"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        'current_asset': 'stocks',
        'current_week': None,
        'completed_symbols': {},
        'failed_symbols': {},
        'total_records': 0
    }


def save_progress(progress):
    """Save progress to file"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def get_symbols_for_asset(asset_type):
    """Get list of symbols for an asset type - ALL from Twelvedata API"""
    config = ASSET_CONFIGS[asset_type]

    # If master_table specified, get from BigQuery
    if 'master_table' in config:
        client = bigquery.Client(project=PROJECT_ID)
        query = f"""
        SELECT DISTINCT symbol, name, exchange
        FROM `{PROJECT_ID}.{DATASET_ID}.{config['master_table']}`
        WHERE symbol IS NOT NULL
        ORDER BY symbol
        """
        result = client.query(query).result()
        return [{'symbol': row.symbol, 'name': row.name or '', 'exchange': row.exchange or ''} for row in result]

    # Get ALL from Twelvedata API
    if 'api_endpoint' in config:
        endpoint = config['api_endpoint']
        filter_config = config.get('filter', {})

        url = f"{BASE_URL}/{endpoint}"
        params = {'apikey': TWELVEDATA_API_KEY}

        try:
            response = requests.get(url, params=params, timeout=60)
            data = response.json()

            symbols = []
            items = data.get('data', data.get('result', {}).get('list', []))

            for item in items:
                # Apply filters
                skip = False
                for key, value in filter_config.items():
                    if item.get(key) != value:
                        skip = True
                        break

                if skip:
                    continue

                # Get symbol - different field names for different endpoints
                symbol = item.get('symbol')
                if not symbol and 'currency_base' in item:
                    # Crypto pairs
                    symbol = f"{item['currency_base']}/{item.get('currency_quote', 'USD')}"

                if symbol:
                    symbols.append({
                        'symbol': symbol,
                        'name': item.get('name', item.get('currency_base', '')),
                        'exchange': item.get('exchange', item.get('mic_code', ''))
                    })

            print(f"  Loaded {len(symbols)} {asset_type} symbols from Twelvedata API")
            return symbols

        except Exception as e:
            print(f"  Error loading {asset_type} symbols: {e}")
            return []

    return []


def fetch_weekly_with_indicators(symbol, weeks=52):
    """Fetch weekly OHLCV data with technical indicators from Twelvedata"""

    # Fetch OHLCV
    ohlcv_url = f"{BASE_URL}/time_series"
    params = {
        'symbol': symbol,
        'interval': '1week',
        'outputsize': weeks,
        'apikey': TWELVEDATA_API_KEY
    }

    try:
        response = requests.get(ohlcv_url, params=params, timeout=30)
        data = response.json()

        if 'values' not in data:
            return None, data.get('message', 'No data')

        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Sort by date ascending for indicator calculation
        df = df.sort_values('datetime').reset_index(drop=True)

        # Calculate all technical indicators
        df = calculate_all_indicators(df)

        return df, None

    except Exception as e:
        return None, str(e)


def calculate_all_indicators(df):
    """Calculate all 82 technical indicators"""

    if len(df) < 5:
        return df

    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['volume'].fillna(0)

    # RSI calculations
    for period in [7, 14, 21]:
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, np.nan)
        df[f'rsi_{period}'] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['macd_line'] = ema12 - ema26
    df['macd_signal'] = df['macd_line'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd_line'] - df['macd_signal']

    # Bollinger Bands
    sma20 = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    df['bbands_upper'] = sma20 + (std20 * 2)
    df['bbands_middle'] = sma20
    df['bbands_lower'] = sma20 - (std20 * 2)
    df['bbands_width'] = (df['bbands_upper'] - df['bbands_lower']) / df['bbands_middle']
    df['bbands_percent'] = (close - df['bbands_lower']) / (df['bbands_upper'] - df['bbands_lower'])

    # SMAs
    for period in [5, 10, 20, 50, 100, 200]:
        df[f'sma_{period}'] = close.rolling(window=min(period, len(df))).mean()

    # EMAs
    for period in [5, 10, 12, 20, 26, 50, 100, 200]:
        df[f'ema_{period}'] = close.ewm(span=min(period, len(df)), adjust=False).mean()

    # WMA, DEMA, TEMA
    weights = np.arange(1, 21)
    df['wma_20'] = close.rolling(window=20).apply(lambda x: np.dot(x, weights[:len(x)]) / weights[:len(x)].sum(), raw=True)
    ema20 = close.ewm(span=20, adjust=False).mean()
    ema_of_ema20 = ema20.ewm(span=20, adjust=False).mean()
    df['dema_20'] = 2 * ema20 - ema_of_ema20
    ema_of_ema_of_ema20 = ema_of_ema20.ewm(span=20, adjust=False).mean()
    df['tema_20'] = 3 * ema20 - 3 * ema_of_ema20 + ema_of_ema_of_ema20

    # KAMA
    change = abs(close - close.shift(10))
    volatility = abs(close.diff()).rolling(window=10).sum()
    er = change / volatility.replace(0, np.nan)
    sc = (er * (2/3 - 2/31) + 2/31) ** 2
    kama = [close.iloc[0]]
    for i in range(1, len(close)):
        kama.append(kama[-1] + sc.iloc[i] * (close.iloc[i] - kama[-1]) if not pd.isna(sc.iloc[i]) else kama[-1])
    df['kama_20'] = kama

    # VWAP (approximation for weekly)
    df['vwap'] = (volume * (high + low + close) / 3).cumsum() / volume.cumsum().replace(0, np.nan)

    # ADX, DX, +DI, -DI
    tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    atr14 = tr.rolling(window=14).mean()
    df['plus_di'] = 100 * (plus_dm.rolling(window=14).mean() / atr14)
    df['minus_di'] = 100 * (minus_dm.rolling(window=14).mean() / atr14)
    df['dx_14'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']).replace(0, np.nan)
    df['adx_14'] = df['dx_14'].rolling(window=14).mean()

    # ATR
    df['atr_14'] = atr14

    # Stochastic
    low14 = low.rolling(window=14).min()
    high14 = high.rolling(window=14).max()
    df['stoch_k'] = 100 * (close - low14) / (high14 - low14).replace(0, np.nan)
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # CCI
    tp = (high + low + close) / 3
    for period in [14, 20]:
        sma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
        df[f'cci_{period}'] = (tp - sma_tp) / (0.015 * mad)

    # Williams %R
    df['willr_14'] = -100 * (high14 - close) / (high14 - low14).replace(0, np.nan)

    # Momentum and ROC
    df['mom_10'] = close - close.shift(10)
    df['roc_10'] = 100 * (close - close.shift(10)) / close.shift(10).replace(0, np.nan)

    # MFI
    tp = (high + low + close) / 3
    mf = tp * volume
    pos_mf = mf.where(tp > tp.shift(1), 0).rolling(window=14).sum()
    neg_mf = mf.where(tp < tp.shift(1), 0).rolling(window=14).sum()
    df['mfi_14'] = 100 - (100 / (1 + pos_mf / neg_mf.replace(0, np.nan)))

    # OBV
    df['obv'] = (np.sign(close.diff()) * volume).fillna(0).cumsum()

    # A/D
    clv = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
    df['ad'] = (clv * volume).fillna(0).cumsum()

    # Aroon
    df['aroon_up'] = 100 * (14 - high.rolling(window=14).apply(lambda x: 14 - x.argmax() - 1, raw=True)) / 14
    df['aroon_down'] = 100 * (14 - low.rolling(window=14).apply(lambda x: 14 - x.argmin() - 1, raw=True)) / 14
    df['aroon_osc'] = df['aroon_up'] - df['aroon_down']

    # Ichimoku
    df['ichimoku_tenkan'] = (high.rolling(window=9).max() + low.rolling(window=9).min()) / 2
    df['ichimoku_kijun'] = (high.rolling(window=26).max() + low.rolling(window=26).min()) / 2
    df['ichimoku_senkou_a'] = (df['ichimoku_tenkan'] + df['ichimoku_kijun']) / 2
    df['ichimoku_senkou_b'] = (high.rolling(window=52).max() + low.rolling(window=52).min()) / 2
    df['ichimoku_chikou'] = close.shift(-26)

    # Supertrend (simplified)
    hl2 = (high + low) / 2
    atr = tr.rolling(window=10).mean()
    upper_band = hl2 + (2 * atr)
    lower_band = hl2 - (2 * atr)
    df['supertrend'] = np.where(close > upper_band.shift(1), lower_band, upper_band)
    df['supertrend_direction'] = np.where(close > df['supertrend'], 1, -1)

    # Change percent
    df['change_percent'] = close.pct_change() * 100

    # Price calculations
    df['typical_price'] = (high + low + close) / 3
    df['median_price'] = (high + low) / 2
    df['weighted_close'] = (high + low + 2 * close) / 4

    # Pivot points
    df['pivot'] = (high.shift(1) + low.shift(1) + close.shift(1)) / 3
    df['r1'] = 2 * df['pivot'] - low.shift(1)
    df['s1'] = 2 * df['pivot'] - high.shift(1)
    df['r2'] = df['pivot'] + (high.shift(1) - low.shift(1))
    df['s2'] = df['pivot'] - (high.shift(1) - low.shift(1))
    df['r3'] = high.shift(1) + 2 * (df['pivot'] - low.shift(1))
    df['s3'] = low.shift(1) - 2 * (high.shift(1) - df['pivot'])

    # Trend direction
    df['trend_direction'] = np.where(
        close > df['sma_20'], 'up',
        np.where(close < df['sma_20'], 'down', 'neutral')
    )

    return df


def create_weekly_table(client, table_name):
    """Create weekly table with 82 fields schema"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    schema = [
        bigquery.SchemaField("id", "STRING"),
        bigquery.SchemaField("symbol", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("exchange", "STRING"),
        bigquery.SchemaField("currency", "STRING"),
        bigquery.SchemaField("datetime", "DATETIME"),
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("open", "FLOAT"),
        bigquery.SchemaField("high", "FLOAT"),
        bigquery.SchemaField("low", "FLOAT"),
        bigquery.SchemaField("close", "FLOAT"),
        bigquery.SchemaField("volume", "FLOAT"),
        bigquery.SchemaField("rsi_7", "FLOAT"),
        bigquery.SchemaField("rsi_14", "FLOAT"),
        bigquery.SchemaField("rsi_21", "FLOAT"),
        bigquery.SchemaField("macd_line", "FLOAT"),
        bigquery.SchemaField("macd_signal", "FLOAT"),
        bigquery.SchemaField("macd_histogram", "FLOAT"),
        bigquery.SchemaField("bbands_upper", "FLOAT"),
        bigquery.SchemaField("bbands_middle", "FLOAT"),
        bigquery.SchemaField("bbands_lower", "FLOAT"),
        bigquery.SchemaField("bbands_width", "FLOAT"),
        bigquery.SchemaField("bbands_percent", "FLOAT"),
        bigquery.SchemaField("sma_5", "FLOAT"),
        bigquery.SchemaField("sma_10", "FLOAT"),
        bigquery.SchemaField("sma_20", "FLOAT"),
        bigquery.SchemaField("sma_50", "FLOAT"),
        bigquery.SchemaField("sma_100", "FLOAT"),
        bigquery.SchemaField("sma_200", "FLOAT"),
        bigquery.SchemaField("ema_5", "FLOAT"),
        bigquery.SchemaField("ema_10", "FLOAT"),
        bigquery.SchemaField("ema_12", "FLOAT"),
        bigquery.SchemaField("ema_20", "FLOAT"),
        bigquery.SchemaField("ema_26", "FLOAT"),
        bigquery.SchemaField("ema_50", "FLOAT"),
        bigquery.SchemaField("ema_100", "FLOAT"),
        bigquery.SchemaField("ema_200", "FLOAT"),
        bigquery.SchemaField("wma_20", "FLOAT"),
        bigquery.SchemaField("dema_20", "FLOAT"),
        bigquery.SchemaField("tema_20", "FLOAT"),
        bigquery.SchemaField("kama_20", "FLOAT"),
        bigquery.SchemaField("vwap", "FLOAT"),
        bigquery.SchemaField("adx_14", "FLOAT"),
        bigquery.SchemaField("dx_14", "FLOAT"),
        bigquery.SchemaField("plus_di", "FLOAT"),
        bigquery.SchemaField("minus_di", "FLOAT"),
        bigquery.SchemaField("atr_14", "FLOAT"),
        bigquery.SchemaField("stoch_k", "FLOAT"),
        bigquery.SchemaField("stoch_d", "FLOAT"),
        bigquery.SchemaField("cci_14", "FLOAT"),
        bigquery.SchemaField("cci_20", "FLOAT"),
        bigquery.SchemaField("willr_14", "FLOAT"),
        bigquery.SchemaField("mom_10", "FLOAT"),
        bigquery.SchemaField("roc_10", "FLOAT"),
        bigquery.SchemaField("mfi_14", "FLOAT"),
        bigquery.SchemaField("obv", "FLOAT"),
        bigquery.SchemaField("ad", "FLOAT"),
        bigquery.SchemaField("aroon_up", "FLOAT"),
        bigquery.SchemaField("aroon_down", "FLOAT"),
        bigquery.SchemaField("aroon_osc", "FLOAT"),
        bigquery.SchemaField("ichimoku_tenkan", "FLOAT"),
        bigquery.SchemaField("ichimoku_kijun", "FLOAT"),
        bigquery.SchemaField("ichimoku_senkou_a", "FLOAT"),
        bigquery.SchemaField("ichimoku_senkou_b", "FLOAT"),
        bigquery.SchemaField("ichimoku_chikou", "FLOAT"),
        bigquery.SchemaField("supertrend", "FLOAT"),
        bigquery.SchemaField("supertrend_direction", "INTEGER"),
        bigquery.SchemaField("change_percent", "FLOAT"),
        bigquery.SchemaField("typical_price", "FLOAT"),
        bigquery.SchemaField("median_price", "FLOAT"),
        bigquery.SchemaField("weighted_close", "FLOAT"),
        bigquery.SchemaField("pivot", "FLOAT"),
        bigquery.SchemaField("r1", "FLOAT"),
        bigquery.SchemaField("s1", "FLOAT"),
        bigquery.SchemaField("r2", "FLOAT"),
        bigquery.SchemaField("s2", "FLOAT"),
        bigquery.SchemaField("r3", "FLOAT"),
        bigquery.SchemaField("s3", "FLOAT"),
        bigquery.SchemaField("trend_direction", "STRING"),
        bigquery.SchemaField("data_source", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
    ]

    try:
        client.get_table(table_ref)
        print(f"  Table {table_name} exists")
    except Exception:
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)
        print(f"  Created table {table_name}")

    return schema


def upload_to_bigquery(client, table_name, df, symbol_info):
    """Upload DataFrame to BigQuery"""
    if df is None or len(df) == 0:
        return 0

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Prepare records
    records = []
    now_str = get_utc_now_str()

    for _, row in df.iterrows():
        record = {
            'id': hashlib.md5(f"{symbol_info['symbol']}_{row['datetime']}".encode()).hexdigest(),
            'symbol': symbol_info['symbol'],
            'name': symbol_info.get('name', ''),
            'exchange': symbol_info.get('exchange', ''),
            'currency': 'USD',
            'datetime': to_bigquery_datetime(row['datetime']),
            'date': to_bigquery_date(row['datetime']),
            'data_source': 'twelvedata',
            'created_at': now_str,
            'updated_at': now_str
        }

        # Add all numeric fields
        numeric_fields = [
            'open', 'high', 'low', 'close', 'volume',
            'rsi_7', 'rsi_14', 'rsi_21',
            'macd_line', 'macd_signal', 'macd_histogram',
            'bbands_upper', 'bbands_middle', 'bbands_lower', 'bbands_width', 'bbands_percent',
            'sma_5', 'sma_10', 'sma_20', 'sma_50', 'sma_100', 'sma_200',
            'ema_5', 'ema_10', 'ema_12', 'ema_20', 'ema_26', 'ema_50', 'ema_100', 'ema_200',
            'wma_20', 'dema_20', 'tema_20', 'kama_20', 'vwap',
            'adx_14', 'dx_14', 'plus_di', 'minus_di', 'atr_14',
            'stoch_k', 'stoch_d', 'cci_14', 'cci_20', 'willr_14',
            'mom_10', 'roc_10', 'mfi_14', 'obv', 'ad',
            'aroon_up', 'aroon_down', 'aroon_osc',
            'ichimoku_tenkan', 'ichimoku_kijun', 'ichimoku_senkou_a', 'ichimoku_senkou_b', 'ichimoku_chikou',
            'supertrend', 'change_percent',
            'typical_price', 'median_price', 'weighted_close',
            'pivot', 'r1', 's1', 'r2', 's2', 'r3', 's3'
        ]

        for field in numeric_fields:
            if field in row and pd.notna(row[field]):
                record[field] = float(row[field])
            else:
                record[field] = None

        # Integer field
        if 'supertrend_direction' in row and pd.notna(row['supertrend_direction']):
            record['supertrend_direction'] = int(row['supertrend_direction'])
        else:
            record['supertrend_direction'] = None

        # String field
        record['trend_direction'] = row.get('trend_direction', 'neutral')

        records.append(record)

    # Upload using insert_rows_json to avoid pyarrow type issues
    errors = client.insert_rows_json(table_ref, records)
    if errors:
        # Only show first error to avoid spam
        print(f"    Upload error: {str(errors[0])[:80]}")
        return 0

    return len(records)


def main():
    print("=" * 70)
    print("WEEKLY DATA FETCHER - ALL 7 ASSET TYPES")
    print("=" * 70)
    print(f"Project: {PROJECT_ID}")
    print(f"82 Technical Indicators per record")
    print(f"Started: {datetime.now()}")
    print()

    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    # Load progress
    progress = load_progress()

    # Process each asset type
    asset_types = ['stocks', 'crypto', 'etfs', 'forex', 'indices', 'commodities', 'funds']

    total_records = progress.get('total_records', 0)
    start_time = time.time()

    for asset_type in asset_types:
        config = ASSET_CONFIGS[asset_type]
        table_name = config['table']

        print(f"\n{'='*60}")
        print(f"Processing: {asset_type.upper()}")
        print(f"{'='*60}")

        # Create table if needed
        create_weekly_table(client, table_name)

        # Get symbols
        symbols = get_symbols_for_asset(asset_type)
        print(f"Symbols to process: {len(symbols)}")

        # Track completed for this asset
        completed_key = f"{asset_type}_completed"
        completed = set(progress.get('completed_symbols', {}).get(asset_type, []))

        successful = 0
        failed = 0

        for i, symbol_info in enumerate(symbols):
            symbol = symbol_info['symbol']

            # Skip if already completed
            if symbol in completed:
                continue

            # Progress display
            if i > 0 and i % 50 == 0:
                elapsed = time.time() - start_time
                rate = (successful + failed) / elapsed * 60 if elapsed > 0 else 0
                print(f"  Progress: {i}/{len(symbols)} | Success: {successful} | Rate: {rate:.1f}/min")

            # Fetch data with indicators
            df, error = fetch_weekly_with_indicators(symbol, weeks=260)  # 5 years

            if error:
                if 'rate limit' in str(error).lower():
                    print(f"  Rate limit - waiting 60s...")
                    time.sleep(60)
                    df, error = fetch_weekly_with_indicators(symbol, weeks=260)

                if error:
                    failed += 1
                    if failed % 100 == 0:
                        print(f"  [FAIL] {symbol}: {error[:40]}")
                    continue

            # Upload to BigQuery
            try:
                count = upload_to_bigquery(client, table_name, df, symbol_info)
                total_records += count
                successful += 1

                # Track progress
                if asset_type not in progress.get('completed_symbols', {}):
                    progress['completed_symbols'][asset_type] = []
                progress['completed_symbols'][asset_type].append(symbol)
                progress['total_records'] = total_records

                if successful % 100 == 0:
                    print(f"  [OK] {symbol}: {count} weeks | Total: {total_records:,}")
                    save_progress(progress)

            except Exception as e:
                failed += 1
                print(f"  [UPLOAD ERROR] {symbol}: {str(e)[:40]}")

            # Rate limiting
            time.sleep(CALL_DELAY)

        print(f"\n{asset_type.upper()} Complete: {successful} success, {failed} failed")
        save_progress(progress)

    # Final summary
    elapsed = time.time() - start_time
    print()
    print("=" * 70)
    print("WEEKLY DATA FETCH COMPLETE")
    print("=" * 70)
    print(f"Total records: {total_records:,}")
    print(f"Time elapsed: {elapsed/60:.1f} minutes")
    print(f"Completed: {datetime.now()}")


if __name__ == "__main__":
    main()
