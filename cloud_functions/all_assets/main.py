#!/usr/bin/env python3
"""
Error-Tolerant TwelveData Fetcher for ALL 7 Asset Types
Robust Cloud Function with automatic retry and self-healing capabilities
"""

import functions_framework
from flask import jsonify, request
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading
import json
import traceback

# TwelveData Configuration - $229 Plan
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
BASE_URL = "https://api.twelvedata.com"

# Rate limiting for $229 plan
MAX_CALLS_PER_MINUTE = 800
MAX_WORKERS = 10
BATCH_SIZE = 30

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
        call_times = [t for t in call_times if now - t < 60]

        if len(call_times) >= MAX_CALLS_PER_MINUTE - 30:
            sleep_time = 60 - (now - call_times[0]) + 1
            if sleep_time > 0:
                time.sleep(sleep_time)
                call_times = [t for t in call_times if time.time() - t < 60]

        call_times.append(time.time())


# =============================================================================
# ASSET CONFIGURATIONS
# =============================================================================

ASSET_CONFIGS = {
    'stocks': {
        'table': 'stocks_daily_clean',
        'symbols': [
            'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'META', 'GOOG', 'TSLA', 'AVGO', 'COST',
            'ASML', 'PEP', 'NFLX', 'AZN', 'CSCO', 'AMD', 'ADBE', 'TMUS', 'TXN', 'CMCSA',
            'INTC', 'AMGN', 'HON', 'QCOM', 'INTU', 'AMAT', 'ISRG', 'BKNG', 'SBUX', 'VRTX',
            'LRCX', 'ADI', 'MDLZ', 'GILD', 'REGN', 'ADP', 'MU', 'PANW', 'KLAC', 'SNPS',
            'CDNS', 'MELI', 'CRWD', 'CSX', 'ORLY', 'MAR', 'ABNB', 'PYPL', 'MNST', 'NXPI',
            'BRK.B', 'UNH', 'XOM', 'JNJ', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX',
            'MRK', 'ABBV', 'LLY', 'KO', 'TMO', 'MCD', 'WMT', 'CRM', 'ACN', 'ABT',
            'BAC', 'DHR', 'PFE', 'VZ', 'WFC', 'NKE', 'PM', 'UNP', 'DIS', 'T',
            'ORCL', 'COP', 'RTX', 'NEE', 'LOW', 'UPS', 'IBM', 'GE', 'CAT', 'SPGI',
            'ELV', 'DE', 'BA', 'LMT', 'PLD', 'GS', 'MS', 'SYK', 'BLK',
            'AXP', 'TJX', 'MMC', 'CB', 'NOW', 'CVS', 'AMT', 'ZTS', 'C',
            'CI', 'BDX', 'SCHW', 'CME', 'EOG', 'SO', 'MO', 'DUK', 'PGR',
            'BSX', 'ETN', 'ICE', 'AON', 'SLB', 'FCX', 'NOC', 'FIS',
            'PNC', 'CL', 'APD', 'MCK', 'SHW', 'EQIX', 'WM', 'ITW', 'USB', 'EMR',
            'MCO', 'NSC', 'TGT', 'MPC', 'GM', 'HUM', 'PSX', 'OXY', 'FDX',
            'AZO', 'GD', 'VLO', 'TRV', 'EW', 'CMG', 'ROP', 'AIG',
            'CCI', 'APH', 'ADSK', 'SRE', 'MET', 'CARR', 'HES',
            'F', 'PSA', 'SPG', 'D', 'HCA', 'PXD', 'JCI', 'NEM',
            'WELL', 'O', 'TEL', 'DHI', 'LEN', 'MSCI', 'AFL',
            'TFC', 'KMB', 'DOW', 'ALL', 'PRU', 'PH', 'A', 'EL',
            'CMI', 'AMP', 'ECL', 'GIS', 'OTIS', 'YUM', 'ROK', 'KR',
            'STZ', 'HSY', 'CTVA', 'NUE', 'DLR', 'KEYS', 'BK', 'WMB'
        ]
    },
    'crypto': {
        'table': 'crypto_daily_clean',
        'symbols': [
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
    },
    'etfs': {
        'table': 'etfs_daily_clean',
        'symbols': [
            'SPY', 'QQQ', 'DIA', 'IWM', 'VOO', 'VTI', 'ARKK', 'XLF', 'XLK', 'XLE',
            'XLV', 'XLI', 'XLU', 'XLRE', 'XLY', 'XLP', 'XLB', 'XLC', 'GLD', 'SLV',
            'USO', 'TLT', 'IEF', 'HYG', 'LQD', 'IEMG', 'EFA', 'VWO', 'VEA', 'INDA',
            'EWJ', 'FXI', 'EWZ', 'KWEB', 'SOXL', 'TQQQ', 'SQQQ', 'UPRO', 'SPXU', 'UVXY'
        ]
    },
    'forex': {
        'table': 'forex_daily_clean',
        'symbols': [
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',
            'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY', 'EUR/CHF', 'GBP/CHF', 'EUR/AUD',
            'GBP/AUD', 'EUR/CAD', 'GBP/CAD', 'AUD/NZD', 'EUR/NZD', 'GBP/NZD',
            'CHF/JPY', 'CAD/JPY', 'NZD/JPY', 'AUD/CAD', 'USD/SGD', 'USD/HKD', 'USD/MXN',
            'USD/ZAR', 'USD/TRY', 'USD/NOK'
        ]
    },
    'indices': {
        'table': 'indices_daily_clean',
        'symbols': [
            'SPX', 'NDX', 'DJI', 'RUT', 'VIX', 'FTSE', 'DAX', 'CAC', 'HSI', 'N225',
            'STOXX50E', 'IBEX35', 'AEX', 'SMI', 'FTSEMIB'
        ]
    },
    'commodities': {
        'table': 'commodities_daily_clean',
        'symbols': [
            'XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD', 'WTI/USD', 'BRENT/USD',
            'NG/USD', 'HG/USD', 'WHEAT/USD', 'CORN/USD', 'SOYBEAN/USD', 'COFFEE/USD',
            'SUGAR/USD', 'COTTON/USD', 'COCOA/USD'
        ]
    }
}


def fetch_with_retry(symbol, interval='1day', outputsize=100, max_retries=3):
    """Fetch data with automatic retry on failure"""
    for attempt in range(max_retries):
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
                df['symbol'] = symbol
                df['datetime'] = pd.to_datetime(df['datetime'])

                for col in ['open', 'high', 'low', 'close']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

                if 'volume' in df.columns:
                    df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype(int)
                else:
                    df['volume'] = 0

                return df, None

            error = data.get('message', data.get('code', 'Unknown'))
            if 'rate limit' in str(error).lower():
                time.sleep(5 * (attempt + 1))  # Exponential backoff
                continue

            return None, error

        except requests.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return None, "Timeout"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1 * (attempt + 1))
                continue
            return None, str(e)

    return None, "Max retries exceeded"


def calculate_indicators(df):
    """Calculate technical indicators"""
    if len(df) < 20:
        return df

    try:
        df = df.sort_values('datetime').reset_index(drop=True)

        # Basic indicators
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
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
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['sma_20'] + (bb_std * 2)
        df['bb_lower'] = df['sma_20'] - (bb_std * 2)

        # ATR
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()

    except:
        pass

    return df


def upload_to_bigquery(client, df, table_id):
    """Upload with schema matching and error handling"""
    if df.empty:
        return 0

    try:
        table_ref = client.dataset(DATASET_ID).table(table_id)
        table = client.get_table(table_ref)
        existing_columns = {field.name for field in table.schema}

        common_columns = [col for col in df.columns if col in existing_columns]
        if not common_columns:
            return 0

        df_upload = df[common_columns].copy()

        if 'datetime' in df_upload.columns:
            df_upload['datetime'] = pd.to_datetime(df_upload['datetime'])
            if df_upload['datetime'].dt.tz is not None:
                df_upload['datetime'] = df_upload['datetime'].dt.tz_localize(None)

        df_upload = df_upload.replace([np.inf, -np.inf], np.nan)

        job_config = bigquery.LoadJobConfig(write_disposition='WRITE_APPEND')
        job = client.load_table_from_dataframe(df_upload, table_ref, job_config=job_config)
        job.result()

        return len(df_upload)
    except Exception as e:
        print(f"Upload error: {e}")
        return 0


def process_asset_type(asset_type, backfill=False):
    """Process a single asset type"""
    config = ASSET_CONFIGS.get(asset_type)
    if not config:
        return {'error': f'Unknown asset type: {asset_type}'}

    symbols = config['symbols']
    table_id = config['table']
    outputsize = 5000 if backfill else 100  # Backfill gets more history

    client = bigquery.Client(project=PROJECT_ID)
    results = {'success': 0, 'failed': 0, 'records': 0, 'errors': []}

    print(f"Processing {len(symbols)} {asset_type} symbols...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_with_retry, symbol, '1day', outputsize): symbol
            for symbol in symbols
        }

        for future in as_completed(futures):
            symbol = futures[future]
            try:
                df, error = future.result()

                if error:
                    results['failed'] += 1
                    if len(results['errors']) < 10:
                        results['errors'].append(f"{symbol}: {error}")
                elif df is not None and not df.empty:
                    df = calculate_indicators(df)
                    records = upload_to_bigquery(client, df, table_id)
                    results['records'] += records
                    results['success'] += 1
                    print(f"  + {symbol}: {records} records")
                else:
                    results['failed'] += 1
            except Exception as e:
                results['failed'] += 1

    return results


@functions_framework.http
def main(request):
    """Main entry point - handles all asset types"""
    try:
        # Parse request
        request_json = request.get_json(silent=True) or {}
        asset_type = request_json.get('asset_type', 'all')
        backfill = request_json.get('backfill', False)

        print(f"Request: asset_type={asset_type}, backfill={backfill}")

        start_time = time.time()
        all_results = {}

        if asset_type == 'all':
            # Process all asset types
            for at in ASSET_CONFIGS.keys():
                print(f"\n{'='*40}")
                print(f"Processing {at.upper()}")
                print('='*40)
                all_results[at] = process_asset_type(at, backfill)
        else:
            # Process single asset type
            all_results[asset_type] = process_asset_type(asset_type, backfill)

        # Summary
        total_records = sum(r['records'] for r in all_results.values())
        total_success = sum(r['success'] for r in all_results.values())
        total_failed = sum(r['failed'] for r in all_results.values())
        elapsed = time.time() - start_time

        response = {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'elapsed_seconds': round(elapsed, 1),
            'summary': {
                'total_records': total_records,
                'total_success': total_success,
                'total_failed': total_failed
            },
            'details': all_results
        }

        print(f"\nCompleted in {elapsed:.1f}s: {total_records} records, {total_success} success, {total_failed} failed")

        return jsonify(response), 200

    except Exception as e:
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


if __name__ == "__main__":
    # For local testing
    class FakeRequest:
        def get_json(self, silent=False):
            return {'asset_type': 'etfs', 'backfill': False}

    result = main(FakeRequest())
    print(result)
