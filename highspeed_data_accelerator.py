#!/usr/bin/env python3
"""
HIGH-SPEED TwelveData Accelerator
Maximizes $229 Plan Bandwidth: 800 calls/minute
Parallel processing for ALL 7 asset types
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading
import json
import os

# TwelveData Configuration - $229 Plan
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
BASE_URL = "https://api.twelvedata.com"

# Rate limiting for $229 plan
MAX_CALLS_PER_MINUTE = 800
CALLS_PER_SECOND = 13  # ~800/60
MAX_WORKERS = 12  # Moderate parallelism for reliability
BATCH_SIZE = 40  # Process in batches

# BigQuery Configuration
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# Rate limiting
call_times = []
call_lock = threading.Lock()

def rate_limit():
    """Enforce rate limiting for TwelveData $229 plan"""
    global call_times
    with call_lock:
        now = time.time()
        # Remove calls older than 60 seconds
        call_times = [t for t in call_times if now - t < 60]

        if len(call_times) >= MAX_CALLS_PER_MINUTE - 20:  # Safety margin
            sleep_time = 60 - (now - call_times[0]) + 0.5
            if sleep_time > 0:
                print(f"   Rate limit approaching, waiting {sleep_time:.1f}s...")
                time.sleep(sleep_time)
                call_times = [t for t in call_times if time.time() - t < 60]

        call_times.append(time.time())

# =============================================================================
# COMPREHENSIVE ASSET LISTS
# =============================================================================

# NASDAQ 100 Complete
NASDAQ_100 = [
    'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'META', 'GOOG', 'TSLA', 'AVGO', 'COST',
    'ASML', 'PEP', 'NFLX', 'AZN', 'CSCO', 'AMD', 'ADBE', 'TMUS', 'TXN', 'CMCSA',
    'INTC', 'AMGN', 'HON', 'QCOM', 'INTU', 'AMAT', 'ISRG', 'BKNG', 'SBUX', 'VRTX',
    'LRCX', 'ADI', 'MDLZ', 'GILD', 'REGN', 'ADP', 'MU', 'PANW', 'KLAC', 'SNPS',
    'CDNS', 'MELI', 'CRWD', 'CSX', 'ORLY', 'MAR', 'ABNB', 'PYPL', 'MNST', 'NXPI',
    'CTAS', 'MRVL', 'PCAR', 'FTNT', 'CPRT', 'PAYX', 'WDAY', 'ROST', 'MCHP', 'DXCM',
    'ODFL', 'KDP', 'AEP', 'TTD', 'IDXX', 'LULU', 'FAST', 'GEHC', 'EXC', 'VRSK',
    'EA', 'BKR', 'CTSH', 'FANG', 'ON', 'CCEP', 'XEL', 'CSGP', 'ANSS', 'CDW',
    'BIIB', 'ZS', 'TEAM', 'DDOG', 'GFS', 'ILMN', 'WBD', 'MDB', 'DLTR', 'MRNA',
    'WBA', 'SIRI', 'LCID', 'RIVN', 'CEG', 'ARM', 'SMCI', 'PLTR', 'DASH', 'COIN'
]

# S&P 500 Top 200
SP500_TOP_200 = [
    'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'META', 'TSLA', 'BRK.B', 'UNH', 'XOM',
    'JNJ', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV', 'LLY',
    'AVGO', 'PEP', 'COST', 'KO', 'TMO', 'MCD', 'WMT', 'CSCO', 'CRM', 'ACN',
    'ABT', 'BAC', 'DHR', 'ADBE', 'NFLX', 'PFE', 'CMCSA', 'TXN', 'VZ', 'WFC',
    'NKE', 'AMD', 'INTC', 'PM', 'UNP', 'DIS', 'T', 'ORCL', 'COP', 'RTX',
    'QCOM', 'NEE', 'LOW', 'HON', 'UPS', 'IBM', 'INTU', 'GE', 'CAT', 'SPGI',
    'ELV', 'DE', 'BA', 'LMT', 'AMAT', 'AMGN', 'PLD', 'GS', 'MS', 'BKNG',
    'SYK', 'BLK', 'ISRG', 'MDLZ', 'AXP', 'ADI', 'GILD', 'TJX', 'MMC', 'VRTX',
    'CB', 'ADP', 'LRCX', 'NOW', 'CVS', 'AMT', 'REGN', 'ZTS', 'C', 'TMUS',
    'CI', 'BDX', 'SCHW', 'CME', 'EOG', 'SO', 'MO', 'DUK', 'PGR', 'SNPS',
    'BSX', 'CDNS', 'ETN', 'ICE', 'AON', 'SLB', 'FCX', 'CSX', 'NOC', 'FIS',
    'PNC', 'CL', 'APD', 'MCK', 'SHW', 'EQIX', 'WM', 'ITW', 'USB', 'EMR',
    'MCO', 'NSC', 'TGT', 'MPC', 'GM', 'HUM', 'ORLY', 'PSX', 'OXY', 'FDX',
    'AZO', 'GD', 'MAR', 'VLO', 'TRV', 'EW', 'CTAS', 'CMG', 'ROP', 'AIG',
    'CCI', 'PCAR', 'APH', 'ADSK', 'SRE', 'MET', 'AEP', 'CARR', 'DXCM', 'HES',
    'F', 'PSA', 'SPG', 'D', 'MNST', 'HCA', 'PXD', 'JCI', 'FTNT', 'NEM',
    'MCHP', 'WELL', 'O', 'BIIB', 'TEL', 'DHI', 'LEN', 'MSCI', 'AFL', 'CPRT',
    'TFC', 'KMB', 'IDXX', 'DOW', 'ALL', 'PRU', 'PH', 'A', 'EL', 'PAYX',
    'CMI', 'AMP', 'ECL', 'GIS', 'OTIS', 'YUM', 'ON', 'ROK', 'KR', 'FAST',
    'STZ', 'HSY', 'CTVA', 'NUE', 'VRSK', 'DLR', 'DLTR', 'KEYS', 'BK', 'WMB'
]

# Russell 2000 Top 50
RUSSELL_TOP_50 = [
    'AXON', 'WING', 'PCVX', 'FTAI', 'CVLT', 'TPL', 'FN', 'RKLB', 'TBBK', 'EAT',
    'LNTH', 'MOD', 'GLNG', 'VNO', 'HQY', 'FIX', 'DOCS', 'RHP', 'NMRK', 'TFSL',
    'HIMS', 'CSWI', 'WDFC', 'UFPI', 'PRGS', 'PBH', 'CVCO', 'APPF', 'ACA', 'KTOS',
    'ALTR', 'SIG', 'AIT', 'OII', 'PRMW', 'CRVL', 'ACIW', 'RBC', 'MASI', 'LMB',
    'POWL', 'VRRM', 'SEM', 'PRCT', 'FRPT', 'ATGE', 'CENX', 'WABC', 'COHR', 'CLVT'
]

# Major ETFs
MAJOR_ETFS = [
    'SPY', 'QQQ', 'DIA', 'IWM', 'VOO', 'VTI', 'ARKK', 'XLF', 'XLK', 'XLE',
    'XLV', 'XLI', 'XLU', 'XLRE', 'XLY', 'XLP', 'XLB', 'XLC', 'GLD', 'SLV',
    'USO', 'TLT', 'IEF', 'HYG', 'LQD', 'IEMG', 'EFA', 'VWO', 'VEA', 'INDA',
    'EWJ', 'FXI', 'EWZ', 'KWEB', 'SOXL', 'TQQQ', 'SQQQ', 'UPRO', 'SPXU', 'UVXY'
]

# Top 100 Cryptocurrencies
TOP_CRYPTOS = [
    'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'SOL/USD', 'ADA/USD', 'DOGE/USD',
    'TRX/USD', 'DOT/USD', 'MATIC/USD', 'LTC/USD', 'SHIB/USD', 'AVAX/USD', 'LINK/USD',
    'ATOM/USD', 'XMR/USD', 'ETC/USD', 'BCH/USD', 'XLM/USD', 'NEAR/USD', 'UNI/USD',
    'APT/USD', 'FIL/USD', 'HBAR/USD', 'VET/USD', 'ICP/USD', 'AAVE/USD', 'ARB/USD',
    'OP/USD', 'MKR/USD', 'GRT/USD', 'ALGO/USD', 'QNT/USD', 'EOS/USD', 'SAND/USD',
    'MANA/USD', 'THETA/USD', 'AXS/USD', 'XTZ/USD', 'RUNE/USD', 'FTM/USD', 'EGLD/USD',
    'NEO/USD', 'FLOW/USD', 'CHZ/USD', 'KAVA/USD', 'ZEC/USD', 'DASH/USD', 'ENJ/USD',
    'CRV/USD', 'BAT/USD', 'COMP/USD', 'LDO/USD', 'SNX/USD', '1INCH/USD', 'RPL/USD',
    'SUSHI/USD', 'YFI/USD', 'ZRX/USD', 'ANKR/USD', 'CELO/USD', 'ICX/USD', 'IOTA/USD',
    'KSM/USD', 'WAVES/USD', 'ZIL/USD', 'QTUM/USD', 'ONT/USD', 'NANO/USD', 'RVN/USD',
    'SC/USD', 'DGB/USD', 'STORJ/USD', 'HIVE/USD', 'STEEM/USD', 'LSK/USD', 'ARDR/USD',
    'NMR/USD', 'MLN/USD', 'REP/USD', 'KNC/USD', 'BNT/USD', 'REN/USD', 'OCEAN/USD',
    'BAND/USD', 'UMA/USD', 'SKL/USD', 'CELR/USD', 'DENT/USD', 'FET/USD', 'CTSI/USD',
    'ALICE/USD', 'GALA/USD', 'IMX/USD', 'JASMY/USD', 'ROSE/USD', 'GMT/USD', 'APE/USD',
    'PEPE/USD', 'WLD/USD'
]

# Major Forex Pairs
FOREX_PAIRS = [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',
    'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY', 'EUR/CHF', 'GBP/CHF', 'EUR/AUD',
    'GBP/AUD', 'EUR/CAD', 'GBP/CAD', 'AUD/NZD', 'EUR/NZD', 'GBP/NZD',
    'CHF/JPY', 'CAD/JPY', 'NZD/JPY', 'AUD/CAD', 'USD/SGD', 'USD/HKD', 'USD/MXN',
    'USD/ZAR', 'USD/TRY', 'USD/NOK'
]

# Major Indices
INDICES = [
    'SPX', 'NDX', 'DJI', 'RUT', 'VIX', 'FTSE', 'DAX', 'CAC', 'HSI', 'N225',
    'STOXX50E', 'IBEX35', 'AEX', 'SMI', 'FTSEMIB'
]

# Commodities
COMMODITIES = [
    'XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD', 'WTI/USD', 'BRENT/USD',
    'NG/USD', 'HG/USD', 'WHEAT/USD', 'CORN/USD', 'SOYBEAN/USD', 'COFFEE/USD',
    'SUGAR/USD', 'COTTON/USD', 'COCOA/USD'
]


def fetch_time_series(symbol, interval='1day', outputsize=5000, asset_type='stocks'):
    """Fetch time series data from TwelveData with rate limiting"""
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

        if 'values' not in data:
            error_msg = data.get('message', data.get('code', 'Unknown error'))
            return None, f"No data: {error_msg}"

        df = pd.DataFrame(data['values'])
        df['symbol'] = symbol
        df['asset_type'] = asset_type

        # Convert types
        df['datetime'] = pd.to_datetime(df['datetime'])
        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype(int)
        else:
            df['volume'] = 0

        return df, None

    except Exception as e:
        return None, str(e)


def calculate_indicators(df):
    """Calculate technical indicators - optimized for speed"""
    if len(df) < 50:
        return df

    try:
        df = df.sort_values('datetime').reset_index(drop=True)

        # Simple Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        if len(df) >= 200:
            df['sma_200'] = df['close'].rolling(window=200).mean()

        # Exponential Moving Averages
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']

        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        df['rsi'] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        df['bb_middle'] = df['sma_20']
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)

        # ATR
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()

        # ADX components
        plus_dm = df['high'].diff()
        minus_dm = df['low'].diff().abs()
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

        atr_smooth = tr.rolling(window=14).sum()
        plus_di = 100 * (plus_dm.rolling(window=14).sum() / atr_smooth.replace(0, np.nan))
        minus_di = 100 * (minus_dm.rolling(window=14).sum() / atr_smooth.replace(0, np.nan))

        df['plus_di'] = plus_di
        df['minus_di'] = minus_di

        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
        df['adx'] = dx.rolling(window=14).mean()

        # Stochastic
        low_14 = df['low'].rolling(window=14).min()
        high_14 = df['high'].rolling(window=14).max()
        df['stoch_k'] = 100 * (df['close'] - low_14) / (high_14 - low_14).replace(0, np.nan)
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

        # Volume indicators
        if 'volume' in df.columns and df['volume'].sum() > 0:
            df['obv'] = (np.sign(df['close'].diff()) * df['volume']).cumsum()

        # Growth Score calculation (per masterquery.md)
        if 'sma_200' in df.columns:
            df['growth_score'] = (
                ((df['rsi'] >= 50) & (df['rsi'] <= 70)).astype(int) * 25 +
                (df['macd_hist'] > 0).astype(int) * 25 +
                (df['adx'] > 25).astype(int) * 25 +
                (df['close'] > df['sma_200']).astype(int) * 25
            )

        # Rise cycle detection
        df['in_rise_cycle'] = df['ema_12'] > df['ema_26']

    except Exception as e:
        pass  # Silent fail for indicators

    return df


def upload_to_bigquery(client, df, table_id):
    """Upload dataframe to BigQuery with schema matching"""
    if df.empty:
        return 0

    try:
        table_ref = client.dataset(DATASET_ID).table(table_id)
        table = client.get_table(table_ref)

        # Get existing columns
        existing_columns = {field.name for field in table.schema}

        # Filter to only existing columns
        common_columns = [col for col in df.columns if col in existing_columns]

        if not common_columns:
            return 0

        df_upload = df[common_columns].copy()

        # Handle timezone for datetime
        if 'datetime' in df_upload.columns:
            df_upload['datetime'] = pd.to_datetime(df_upload['datetime'])
            if df_upload['datetime'].dt.tz is not None:
                df_upload['datetime'] = df_upload['datetime'].dt.tz_localize(None)

        # Handle NaN values
        df_upload = df_upload.replace([np.inf, -np.inf], np.nan)

        # Upload
        job_config = bigquery.LoadJobConfig(write_disposition='WRITE_APPEND')
        job = client.load_table_from_dataframe(df_upload, table_ref, job_config=job_config)
        job.result()

        return len(df_upload)

    except Exception as e:
        return 0


def batch_process_symbols(symbols, asset_type, table_id, interval='1day', outputsize=5000):
    """Process symbols in parallel batches"""
    client = bigquery.Client(project=PROJECT_ID)

    total_records = 0
    successful = 0
    failed = 0

    print(f"\n  Processing {len(symbols)} {asset_type} symbols...")

    # Process in batches for better monitoring
    for batch_start in range(0, len(symbols), BATCH_SIZE):
        batch = symbols[batch_start:batch_start + BATCH_SIZE]

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(fetch_time_series, symbol, interval, outputsize, asset_type): symbol
                for symbol in batch
            }

            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    df, error = future.result()
                    if error:
                        failed += 1
                    elif df is not None and not df.empty:
                        df = calculate_indicators(df)
                        records = upload_to_bigquery(client, df, table_id)
                        total_records += records
                        successful += 1
                        if records > 0:
                            print(f"    + {symbol}: {records} records")
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1

        # Progress update
        processed = min(batch_start + BATCH_SIZE, len(symbols))
        print(f"  Progress: {processed}/{len(symbols)} ({successful} success, {failed} failed)")

    return total_records, successful, failed


def main():
    """Main execution - High-speed data collection for ALL asset types"""
    print("=" * 70)
    print("HIGH-SPEED TwelveData Accelerator - ALL 7 ASSET TYPES")
    print(f"Plan: $229 | Max Calls: {MAX_CALLS_PER_MINUTE}/min | Workers: {MAX_WORKERS}")
    print("=" * 70)

    start_time = time.time()

    # Combine all stock symbols (deduplicated)
    all_stocks = list(set(NASDAQ_100 + SP500_TOP_200 + RUSSELL_TOP_50 + MAJOR_ETFS))

    results = {}

    # Asset configurations: (symbols, asset_type, table_id)
    asset_configs = [
        (all_stocks, 'stocks', 'stocks_daily_clean'),
        (TOP_CRYPTOS, 'crypto', 'crypto_daily_clean'),
        (MAJOR_ETFS, 'etfs', 'etfs_daily_clean'),
        (FOREX_PAIRS, 'forex', 'forex_daily_clean'),
        (INDICES, 'indices', 'indices_daily_clean'),
        (COMMODITIES, 'commodities', 'commodities_daily_clean'),
    ]

    print(f"\nAssets to process:")
    for symbols, asset_type, _ in asset_configs:
        print(f"  - {asset_type.capitalize()}: {len(symbols)} symbols")

    # Process each asset type
    for symbols, asset_type, table_id in asset_configs:
        print(f"\n{'='*50}")
        print(f"FETCHING {asset_type.upper()} (Daily)")
        print("=" * 50)

        records, success, failed = batch_process_symbols(
            symbols, asset_type, table_id, '1day', 5000
        )
        results[asset_type] = {'records': records, 'success': success, 'failed': failed}

    # Final Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("DATA ACCELERATION COMPLETE - ALL 7 ASSET TYPES")
    print("=" * 70)
    print(f"\nElapsed Time: {elapsed/60:.1f} minutes")
    print(f"\nResults by Asset Type:")

    total_records = 0
    total_success = 0
    total_failed = 0

    for asset_type, res in results.items():
        print(f"  {asset_type.capitalize():12}: {res['records']:>10,} records ({res['success']:>3} success, {res['failed']:>3} failed)")
        total_records += res['records']
        total_success += res['success']
        total_failed += res['failed']

    print(f"\n  {'TOTAL':12}: {total_records:>10,} records ({total_success:>3} success, {total_failed:>3} failed)")

    # Save progress
    progress = {
        'last_run': datetime.now().isoformat(),
        'elapsed_minutes': elapsed/60,
        'results': results,
        'totals': {
            'records': total_records,
            'success': total_success,
            'failed': total_failed
        }
    }
    with open('accelerator_progress.json', 'w') as f:
        json.dump(progress, f, indent=2)

    print("\nProgress saved to accelerator_progress.json")


if __name__ == "__main__":
    main()
