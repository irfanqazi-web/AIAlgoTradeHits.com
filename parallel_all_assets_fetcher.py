#!/usr/bin/env python3
"""
Parallel TwelveData Fetcher for ALL 7 Asset Types
Uses $229 plan bandwidth: 800 API calls/minute
Fetches stocks, crypto, forex, ETFs, indices, commodities, funds
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading
import sys
import io

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# TwelveData Configuration - $229 Plan
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
BASE_URL = "https://api.twelvedata.com"

# Rate limiting for $229 plan - aggressive but safe
MAX_CALLS_PER_MINUTE = 750  # Leave buffer
MAX_WORKERS = 15  # Parallel threads
BATCH_DELAY = 0.08  # 80ms between calls

# BigQuery Configuration
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# Rate limiting
call_times = []
call_lock = threading.Lock()
total_calls = 0

def rate_limit():
    """Enforce rate limiting"""
    global call_times, total_calls
    with call_lock:
        now = time.time()
        call_times = [t for t in call_times if now - t < 60]

        if len(call_times) >= MAX_CALLS_PER_MINUTE:
            sleep_time = 60 - (now - call_times[0]) + 0.5
            if sleep_time > 0:
                print(f"    Rate limit reached, sleeping {sleep_time:.1f}s...")
                time.sleep(sleep_time)
                call_times = [t for t in call_times if time.time() - t < 60]

        call_times.append(time.time())
        total_calls += 1
        time.sleep(BATCH_DELAY)

# =============================================================================
# ENHANCED ASSET CONFIGURATIONS - Full $229 Plan Coverage
# =============================================================================

ASSET_CONFIGS = {
    'stocks': {
        'v2_table': 'v2_stocks_daily',
        'symbols': [
            # Top 100 US Stocks by Market Cap
            'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'META', 'GOOG', 'TSLA', 'AVGO', 'COST',
            'PEP', 'NFLX', 'CSCO', 'AMD', 'ADBE', 'TMUS', 'TXN', 'CMCSA', 'INTC', 'AMGN',
            'HON', 'QCOM', 'INTU', 'AMAT', 'ISRG', 'BKNG', 'SBUX', 'VRTX', 'LRCX', 'ADI',
            'MDLZ', 'GILD', 'REGN', 'ADP', 'MU', 'PANW', 'KLAC', 'SNPS', 'CDNS', 'MELI',
            'CRWD', 'CSX', 'ORLY', 'MAR', 'ABNB', 'PYPL', 'MNST', 'NXPI', 'BRK.B', 'UNH',
            'XOM', 'JNJ', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV',
            'LLY', 'KO', 'TMO', 'MCD', 'WMT', 'CRM', 'ACN', 'ABT', 'BAC', 'DHR',
            'PFE', 'VZ', 'WFC', 'NKE', 'PM', 'UNP', 'DIS', 'ORCL', 'COP', 'RTX',
            'NEE', 'LOW', 'UPS', 'IBM', 'GE', 'CAT', 'SPGI', 'DE', 'BA', 'LMT',
            'GS', 'MS', 'SYK', 'BLK', 'AXP', 'NOW', 'CVS', 'AMT', 'C', 'CI',
            # Additional 50 mid-cap stocks
            'SCHW', 'CME', 'EOG', 'SO', 'MO', 'DUK', 'PGR', 'BSX', 'ETN', 'ICE',
            'AON', 'SLB', 'FCX', 'NOC', 'PNC', 'CL', 'APD', 'MCK', 'SHW', 'EQIX',
            'WM', 'ITW', 'USB', 'EMR', 'MCO', 'NSC', 'TGT', 'GM', 'FDX', 'AZO',
            'GD', 'TRV', 'CMG', 'ROP', 'AIG', 'APH', 'ADSK', 'MET', 'CARR', 'F',
            'PSA', 'SPG', 'D', 'HCA', 'JCI', 'NEM', 'WELL', 'O', 'DHI', 'LEN'
        ]
    },
    'crypto': {
        'v2_table': 'v2_crypto_daily',
        'symbols': [
            # Top 50 Cryptocurrencies
            'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'SOL/USD', 'ADA/USD', 'DOGE/USD',
            'TRX/USD', 'DOT/USD', 'MATIC/USD', 'LTC/USD', 'SHIB/USD', 'AVAX/USD', 'LINK/USD',
            'ATOM/USD', 'XMR/USD', 'ETC/USD', 'BCH/USD', 'XLM/USD', 'NEAR/USD', 'UNI/USD',
            'FIL/USD', 'HBAR/USD', 'VET/USD', 'ICP/USD', 'AAVE/USD', 'ARB/USD', 'OP/USD',
            'GRT/USD', 'ALGO/USD', 'SAND/USD', 'MANA/USD', 'THETA/USD', 'AXS/USD', 'XTZ/USD',
            'NEO/USD', 'CHZ/USD', 'ZEC/USD', 'DASH/USD', 'ENJ/USD', 'BAT/USD', 'COMP/USD',
            'SNX/USD', 'SUSHI/USD', 'YFI/USD', 'IMX/USD', 'APE/USD', 'PEPE/USD', 'SUI/USD', 'SEI/USD'
        ]
    },
    'etfs': {
        'v2_table': 'v2_etfs_daily',
        'symbols': [
            # Major ETFs - 40 symbols
            'SPY', 'QQQ', 'DIA', 'IWM', 'VOO', 'VTI', 'ARKK', 'XLF', 'XLK', 'XLE',
            'XLV', 'XLI', 'XLU', 'XLRE', 'XLY', 'XLP', 'XLB', 'XLC', 'GLD', 'SLV',
            'USO', 'TLT', 'IEF', 'HYG', 'LQD', 'EEM', 'EFA', 'VWO', 'VEA', 'INDA',
            'EWJ', 'FXI', 'EWZ', 'KWEB', 'SMH', 'SOXX', 'VNQ', 'IEFA', 'AGG', 'BND'
        ]
    },
    'forex': {
        'v2_table': 'v2_forex_daily',
        'symbols': [
            # Major and Minor Forex Pairs - 30 pairs
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',
            'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY', 'EUR/CHF', 'GBP/CHF', 'EUR/AUD',
            'GBP/AUD', 'EUR/CAD', 'GBP/CAD', 'AUD/NZD', 'EUR/NZD', 'GBP/NZD',
            'CHF/JPY', 'CAD/JPY', 'NZD/JPY', 'AUD/CAD', 'USD/SGD', 'USD/HKD', 'USD/MXN',
            'USD/ZAR', 'USD/TRY', 'USD/INR'
        ]
    },
    'indices': {
        'v2_table': 'v2_indices_daily',
        'symbols': [
            # Major World Indices - 20 indices
            'SPX', 'NDX', 'DJI', 'RUT', 'VIX',  # US
            'FTSE', 'DAX', 'CAC', 'STOXX50E', 'IBEX', 'AEX', 'SMI',  # Europe
            'N225', 'HSI', 'SSEC', 'KOSPI', 'TWII', 'SENSEX',  # Asia
            'GSPTSE', 'BVSP'  # Americas
        ]
    },
    'commodities': {
        'v2_table': 'v2_commodities_daily',
        'symbols': [
            # Major Commodities - 15 symbols
            'XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD',  # Precious metals
            'CL', 'BZ', 'NG', 'HO',  # Energy (WTI, Brent, Natural Gas, Heating Oil)
            'HG', 'ZC', 'ZS', 'ZW',  # Base metals and grains
            'KC', 'SB', 'CT'  # Softs (Coffee, Sugar, Cotton)
        ]
    },
    'funds': {
        'v2_table': 'v2_funds_daily',
        'symbols': [
            # Top Mutual Funds - 15 symbols
            'VFINX', 'VTSAX', 'FXAIX', 'VFIAX', 'VGTSX',
            'VTSMX', 'VBMFX', 'FBALX', 'FDIVX', 'FMAGX',
            'VWELX', 'VWINX', 'PRWCX', 'AGTHX', 'OAKMX'
        ]
    }
}


def fetch_symbol(symbol, interval='1day', outputsize=365):
    """Fetch data for a single symbol"""
    rate_limit()
    try:
        params = {
            'symbol': symbol,
            'interval': interval,
            'outputsize': outputsize,
            'apikey': TWELVEDATA_API_KEY,
            'format': 'JSON'
        }

        response = requests.get(f"{BASE_URL}/time_series", params=params, timeout=30)
        data = response.json()

        if 'values' in data:
            df = pd.DataFrame(data['values'])
            df['symbol'] = symbol.replace('/', '')  # Remove / for BQ compatibility
            df['datetime'] = pd.to_datetime(df['datetime'])

            for col in ['open', 'high', 'low', 'close']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            if 'volume' in df.columns:
                df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype(int)
            else:
                df['volume'] = 0

            return df, None

        return None, data.get('message', data.get('code', 'Unknown error'))

    except Exception as e:
        return None, str(e)


def calculate_indicators(df):
    """Calculate 24 technical indicators per masterquery spec"""
    if len(df) < 50:
        return df

    try:
        df = df.sort_values('datetime').reset_index(drop=True)

        # SMAs
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=min(200, len(df))).mean()

        # EMAs
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema_200'] = df['close'].ewm(span=min(200, len(df)), adjust=False).mean()

        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        df['rsi_14'] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['sma_20'] + (bb_std * 2)
        df['bb_middle'] = df['sma_20']
        df['bb_lower'] = df['sma_20'] - (bb_std * 2)

        # ATR
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr_14'] = tr.rolling(window=14).mean()

        # Stochastic
        low_14 = df['low'].rolling(window=14).min()
        high_14 = df['high'].rolling(window=14).max()
        df['stoch_k'] = 100 * (df['close'] - low_14) / (high_14 - low_14)
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

        # ADX (simplified)
        plus_dm = df['high'].diff()
        minus_dm = df['low'].diff().abs()
        plus_dm = plus_dm.where(plus_dm > minus_dm, 0)
        minus_dm = minus_dm.where(minus_dm > plus_dm, 0)
        df['plus_di'] = 100 * (plus_dm.rolling(14).mean() / df['atr_14'])
        df['minus_di'] = 100 * (minus_dm.rolling(14).mean() / df['atr_14'])
        df['adx'] = abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']) * 100
        df['adx'] = df['adx'].rolling(14).mean()

        # MFI (Money Flow Index)
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        raw_mf = typical_price * df['volume']
        mf_positive = raw_mf.where(typical_price > typical_price.shift(), 0).rolling(14).sum()
        mf_negative = raw_mf.where(typical_price < typical_price.shift(), 0).rolling(14).sum()
        df['mfi'] = 100 - (100 / (1 + mf_positive / mf_negative.replace(0, np.nan)))

        # Growth Score (per masterquery)
        df['growth_score'] = (
            ((df['rsi_14'] >= 50) & (df['rsi_14'] <= 70)).astype(int) * 25 +
            (df['macd_histogram'] > 0).astype(int) * 25 +
            (df['adx'] > 25).astype(int) * 25 +
            (df['close'] > df['sma_200']).astype(int) * 25
        )

        # Rise Cycle
        df['in_rise_cycle'] = df['ema_12'] > df['ema_26']

    except Exception as e:
        print(f"    Indicator calculation error: {e}")

    return df


def upload_to_bigquery(client, df, table_id):
    """Upload data to BigQuery v2 table"""
    if df.empty:
        return 0

    try:
        # Get existing schema
        table_ref = client.dataset(DATASET_ID).table(table_id)

        try:
            table = client.get_table(table_ref)
            existing_columns = {field.name for field in table.schema}
        except:
            # Table doesn't exist, create it
            existing_columns = {'symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume',
                               'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'rsi_14',
                               'macd', 'macd_signal', 'macd_histogram', 'bb_upper', 'bb_lower',
                               'atr_14', 'stoch_k', 'stoch_d', 'adx', 'growth_score', 'in_rise_cycle'}

        # Filter to matching columns
        common_columns = [col for col in df.columns if col in existing_columns]
        if not common_columns:
            common_columns = ['symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume']

        df_upload = df[common_columns].copy()

        # Fix datetime
        if 'datetime' in df_upload.columns:
            df_upload['datetime'] = pd.to_datetime(df_upload['datetime'])
            if df_upload['datetime'].dt.tz is not None:
                df_upload['datetime'] = df_upload['datetime'].dt.tz_localize(None)

        # Replace inf values
        df_upload = df_upload.replace([np.inf, -np.inf], np.nan)

        # Upload
        job_config = bigquery.LoadJobConfig(write_disposition='WRITE_APPEND')
        job = client.load_table_from_dataframe(df_upload, table_ref, job_config=job_config)
        job.result()

        return len(df_upload)

    except Exception as e:
        print(f"    Upload error: {e}")
        return 0


def process_asset_type(asset_type, client):
    """Process all symbols for an asset type in parallel"""
    config = ASSET_CONFIGS.get(asset_type)
    if not config:
        return {'error': f'Unknown asset type: {asset_type}'}

    symbols = config['symbols']
    table_id = config['v2_table']

    results = {'success': 0, 'failed': 0, 'records': 0, 'symbols_processed': []}

    print(f"\n{'='*60}")
    print(f"  Processing {asset_type.upper()}: {len(symbols)} symbols -> {table_id}")
    print(f"{'='*60}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_symbol, symbol): symbol for symbol in symbols}

        for future in as_completed(futures):
            symbol = futures[future]
            try:
                df, error = future.result()

                if error:
                    results['failed'] += 1
                    print(f"  X {symbol}: {error}")
                elif df is not None and not df.empty:
                    df = calculate_indicators(df)
                    records = upload_to_bigquery(client, df, table_id)
                    results['records'] += records
                    results['success'] += 1
                    results['symbols_processed'].append(symbol)
                    print(f"  + {symbol}: {records} records")
                else:
                    results['failed'] += 1
                    print(f"  X {symbol}: No data")
            except Exception as e:
                results['failed'] += 1
                print(f"  X {symbol}: {e}")

    return results


def main():
    """Main function - process all 7 asset types in parallel batches"""
    print("\n" + "="*70)
    print("  TWELVEDATA PARALLEL FETCHER - ALL 7 ASSET TYPES")
    print("  $229 Plan: 800 API calls/minute")
    print("="*70)

    start_time = time.time()
    client = bigquery.Client(project=PROJECT_ID)

    all_results = {}

    # Process each asset type
    for asset_type in ASSET_CONFIGS.keys():
        all_results[asset_type] = process_asset_type(asset_type, client)

    # Summary
    elapsed = time.time() - start_time

    print("\n" + "="*70)
    print("  FINAL SUMMARY")
    print("="*70)

    total_records = 0
    total_success = 0
    total_failed = 0

    for asset_type, results in all_results.items():
        records = results.get('records', 0)
        success = results.get('success', 0)
        failed = results.get('failed', 0)
        total_records += records
        total_success += success
        total_failed += failed

        print(f"  {asset_type.upper():15} | {success:3} success | {failed:3} failed | {records:6} records")

    print("-"*70)
    print(f"  {'TOTAL':15} | {total_success:3} success | {total_failed:3} failed | {total_records:6} records")
    print(f"\n  Time: {elapsed/60:.1f} minutes | API calls: {total_calls}")
    print("="*70)

    # Write results to file
    with open('parallel_fetch_results.json', 'w') as f:
        import json
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'elapsed_minutes': round(elapsed/60, 1),
            'total_api_calls': total_calls,
            'total_records': total_records,
            'total_success': total_success,
            'total_failed': total_failed,
            'details': {k: {key: val for key, val in v.items() if key != 'symbols_processed'}
                       for k, v in all_results.items()}
        }, f, indent=2)

    print("\nResults saved to parallel_fetch_results.json")
    return all_results


if __name__ == "__main__":
    main()
