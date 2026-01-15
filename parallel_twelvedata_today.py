#!/usr/bin/env python3
"""
Parallel TwelveData Fetcher - Today's Data
$229 Plan: 800 credits/min, 8 complex requests/min
Fetches all 24 indicators per masterquery.md spec
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timezone, timedelta
import time
import concurrent.futures
import threading
from collections import defaultdict

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
ML_DATASET_ID = 'ml_models'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'

# Rate limiting for $229 plan (800 credits/min, up to 120 req/min for basic endpoints)
# Complex indicators count as 2-10 credits each
CREDITS_PER_MIN = 800
MAX_REQUESTS_PER_MIN = 55  # Stay under 60 to be safe
REQUEST_DELAY = 0.08  # ~75 requests/min max

# Thread-safe rate limiter
rate_lock = threading.Lock()
request_count = 0
last_reset = time.time()

# Top 100 US Stocks (NASDAQ/NYSE)
TOP_100_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH',
    'LLY', 'JPM', 'XOM', 'V', 'JNJ', 'AVGO', 'PG', 'MA', 'HD', 'COST',
    'MRK', 'ABBV', 'CVX', 'CRM', 'KO', 'PEP', 'AMD', 'ADBE', 'WMT', 'MCD',
    'CSCO', 'BAC', 'ACN', 'NFLX', 'TMO', 'LIN', 'ORCL', 'ABT', 'DHR', 'INTC',
    'DIS', 'PM', 'CMCSA', 'VZ', 'WFC', 'TXN', 'NKE', 'COP', 'INTU', 'RTX',
    'NEE', 'QCOM', 'HON', 'IBM', 'AMGN', 'UNP', 'LOW', 'SPGI', 'CAT', 'GE',
    'BA', 'PLD', 'SBUX', 'DE', 'ELV', 'AMAT', 'BMY', 'GS', 'BLK', 'MDLZ',
    'ADI', 'ISRG', 'GILD', 'MMC', 'ADP', 'TJX', 'VRTX', 'AMT', 'SYK', 'REGN',
    'LMT', 'BKNG', 'MO', 'ETN', 'LRCX', 'CB', 'CI', 'PGR', 'C', 'ZTS',
    'PANW', 'BDX', 'SCHW', 'EOG', 'SO', 'MU', 'CME', 'NOC', 'DUK', 'SLB'
]

# Top 20 Cryptos
TOP_20_CRYPTO = [
    'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'SOL/USD', 'DOGE/USD', 'ADA/USD',
    'AVAX/USD', 'LINK/USD', 'DOT/USD', 'MATIC/USD', 'SHIB/USD', 'TRX/USD', 'UNI/USD',
    'ATOM/USD', 'LTC/USD', 'NEAR/USD', 'APT/USD', 'FIL/USD', 'ARB/USD'
]

# Key ETFs
KEY_ETFS = ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'XLF', 'XLE', 'XLK', 'XLV']

# Initialize BigQuery client
bq_client = bigquery.Client(project=PROJECT_ID)


def rate_limit():
    """Rate limiter for API calls"""
    global request_count, last_reset
    with rate_lock:
        current_time = time.time()
        if current_time - last_reset >= 60:
            request_count = 0
            last_reset = current_time

        if request_count >= MAX_REQUESTS_PER_MIN:
            sleep_time = 60 - (current_time - last_reset) + 1
            if sleep_time > 0:
                print(f"    Rate limit ({request_count} reqs), sleeping {sleep_time:.1f}s...")
                time.sleep(sleep_time)
                request_count = 0
                last_reset = time.time()

        request_count += 1
        time.sleep(REQUEST_DELAY)


def fetch_ohlcv(symbol, interval='1day', outputsize=30):
    """Fetch OHLCV data"""
    try:
        rate_limit()
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
            return None

        df = pd.DataFrame(data['values'])
        df['symbol'] = symbol.replace('/', '')
        df['datetime'] = pd.to_datetime(df['datetime'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    except Exception as e:
        print(f"    Error fetching {symbol}: {e}")
        return None


def fetch_indicator(symbol, indicator, interval='1day', outputsize=30, **params):
    """Fetch single indicator from TwelveData"""
    try:
        rate_limit()
        url = f"{BASE_URL}/{indicator}"
        request_params = {
            'symbol': symbol,
            'interval': interval,
            'outputsize': outputsize,
            'apikey': TWELVEDATA_API_KEY,
            'format': 'JSON',
            **params
        }

        response = requests.get(url, params=request_params, timeout=30)
        data = response.json()

        if 'values' not in data:
            return None

        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])

        return df

    except Exception as e:
        return None


def fetch_all_indicators_for_symbol(symbol, interval='1day'):
    """Fetch all 24 indicators for a symbol per masterquery.md"""
    print(f"  Fetching {symbol}...")

    # Get OHLCV base data
    ohlcv = fetch_ohlcv(symbol, interval, outputsize=30)
    if ohlcv is None or ohlcv.empty:
        print(f"    No OHLCV data for {symbol}")
        return None

    result = ohlcv.copy()

    # Indicator definitions per masterquery.md
    indicators = {
        # Momentum (6)
        'rsi': {'endpoint': 'rsi', 'params': {'time_period': 14}, 'col': 'rsi_14'},
        'macd': {'endpoint': 'macd', 'params': {}, 'cols': ['macd', 'macd_signal', 'macd_hist']},
        'stoch': {'endpoint': 'stoch', 'params': {}, 'cols': ['slow_k', 'slow_d']},
        'mfi': {'endpoint': 'mfi', 'params': {'time_period': 14}, 'col': 'mfi'},

        # Trend EMAs (5)
        'ema_12': {'endpoint': 'ema', 'params': {'time_period': 12}, 'col': 'ema_12'},
        'ema_20': {'endpoint': 'ema', 'params': {'time_period': 20}, 'col': 'ema_20'},
        'ema_26': {'endpoint': 'ema', 'params': {'time_period': 26}, 'col': 'ema_26'},
        'ema_50': {'endpoint': 'ema', 'params': {'time_period': 50}, 'col': 'ema_50'},
        'ema_200': {'endpoint': 'ema', 'params': {'time_period': 200}, 'col': 'ema_200'},

        # Trend SMAs (3)
        'sma_20': {'endpoint': 'sma', 'params': {'time_period': 20}, 'col': 'sma_20'},
        'sma_50': {'endpoint': 'sma', 'params': {'time_period': 50}, 'col': 'sma_50'},
        'sma_200': {'endpoint': 'sma', 'params': {'time_period': 200}, 'col': 'sma_200'},

        # Volatility (4)
        'atr': {'endpoint': 'atr', 'params': {'time_period': 14}, 'col': 'atr_14'},
        'bbands': {'endpoint': 'bbands', 'params': {}, 'cols': ['upper_band', 'middle_band', 'lower_band']},

        # Trend Strength (3)
        'adx': {'endpoint': 'adx', 'params': {'time_period': 14}, 'col': 'adx'},
        'plus_di': {'endpoint': 'plus_di', 'params': {'time_period': 14}, 'col': 'plus_di'},
        'minus_di': {'endpoint': 'minus_di', 'params': {'time_period': 14}, 'col': 'minus_di'},

        # Ichimoku (2)
        'ichimoku': {'endpoint': 'ichimoku', 'params': {}, 'cols': ['tenkan_sen', 'kijun_sen']},

        # Flow (1)
        'cmf': {'endpoint': 'cmf', 'params': {'time_period': 20}, 'col': 'cmf'},
    }

    for name, config in indicators.items():
        try:
            ind_df = fetch_indicator(symbol, config['endpoint'], interval, 30, **config['params'])

            if ind_df is not None and not ind_df.empty:
                # Merge with result
                if 'col' in config:
                    # Single column indicator
                    col_name = list(ind_df.columns)[1] if len(ind_df.columns) > 1 else ind_df.columns[0]
                    ind_df = ind_df.rename(columns={col_name: config['col']})
                    result = result.merge(ind_df[['datetime', config['col']]], on='datetime', how='left')
                elif 'cols' in config:
                    # Multi-column indicator
                    for i, col in enumerate(config['cols']):
                        if i + 1 < len(ind_df.columns):
                            orig_col = ind_df.columns[i + 1]
                            ind_df = ind_df.rename(columns={orig_col: col})
                    result = result.merge(ind_df[['datetime'] + config['cols']], on='datetime', how='left')

        except Exception as e:
            print(f"      Error with {name}: {e}")
            continue

    # Convert all numeric columns to float
    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'rsi_14', 'macd', 'macd_signal', 'macd_hist',
                    'slow_k', 'slow_d', 'mfi', 'ema_12', 'ema_20', 'ema_26', 'ema_50', 'ema_200',
                    'sma_20', 'sma_50', 'sma_200', 'atr_14', 'upper_band', 'middle_band', 'lower_band',
                    'adx', 'plus_di', 'minus_di', 'tenkan_sen', 'kijun_sen', 'cmf']
    for col in numeric_cols:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce')

    # Remove duplicate columns if any
    result = result.loc[:, ~result.columns.duplicated()]

    # Calculate Growth Score per masterquery.md
    try:
        result['growth_score'] = 0

        # RSI between 50-70: +25
        if 'rsi_14' in result.columns:
            result.loc[(result['rsi_14'] >= 50) & (result['rsi_14'] <= 70), 'growth_score'] += 25

        # MACD histogram > 0: +25
        if 'macd_hist' in result.columns:
            result.loc[result['macd_hist'] > 0, 'growth_score'] += 25

        # ADX > 25: +25
        if 'adx' in result.columns:
            result.loc[result['adx'] > 25, 'growth_score'] += 25

        # Close > SMA_200: +25
        if 'sma_200' in result.columns:
            result.loc[result['close'] > result['sma_200'], 'growth_score'] += 25

        # Calculate trend regime
        result['trend_regime'] = 'CONSOLIDATION'
        if 'sma_50' in result.columns and 'sma_200' in result.columns and 'adx' in result.columns:
            # Strong uptrend
            mask = (result['close'] > result['sma_50']) & (result['sma_50'] > result['sma_200']) & (result['adx'] > 25)
            result.loc[mask, 'trend_regime'] = 'STRONG_UPTREND'

            # Weak uptrend
            mask = (result['close'] > result['sma_50']) & (result['close'] > result['sma_200']) & (result['trend_regime'] == 'CONSOLIDATION')
            result.loc[mask, 'trend_regime'] = 'WEAK_UPTREND'

            # Strong downtrend
            mask = (result['close'] < result['sma_50']) & (result['sma_50'] < result['sma_200']) & (result['adx'] > 25)
            result.loc[mask, 'trend_regime'] = 'STRONG_DOWNTREND'

            # Weak downtrend
            mask = (result['close'] < result['sma_50']) & (result['close'] < result['sma_200']) & (result['trend_regime'] == 'CONSOLIDATION')
            result.loc[mask, 'trend_regime'] = 'WEAK_DOWNTREND'

        # Rise cycle detection
        result['in_rise_cycle'] = False
        if 'ema_12' in result.columns and 'ema_26' in result.columns:
            result['in_rise_cycle'] = result['ema_12'] > result['ema_26']

    except Exception as e:
        print(f"      Error calculating derived fields: {e}")

    print(f"    {symbol}: {len(result)} rows, {len(result.columns)} columns")
    return result


def upload_to_bigquery(df, table_name, dataset_id=ML_DATASET_ID):
    """Upload dataframe to BigQuery"""
    if df is None or df.empty:
        return False

    try:
        table_ref = f"{PROJECT_ID}.{dataset_id}.{table_name}"

        # Configure job
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
        )

        job = bq_client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()

        return True

    except Exception as e:
        print(f"    Error uploading to {table_name}: {e}")
        return False


def fetch_symbols_parallel(symbols, asset_type, interval='1day', max_workers=4):
    """Fetch multiple symbols in parallel"""
    all_data = []

    print(f"\n{'='*60}")
    print(f"Fetching {len(symbols)} {asset_type} symbols (parallel={max_workers})")
    print(f"{'='*60}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_symbol = {
            executor.submit(fetch_all_indicators_for_symbol, symbol, interval): symbol
            for symbol in symbols
        }

        for future in concurrent.futures.as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                data = future.result()
                if data is not None and not data.empty:
                    data['asset_type'] = asset_type
                    all_data.append(data)
            except Exception as e:
                print(f"    Failed {symbol}: {e}")

    if all_data:
        # Reset index on each dataframe before concat
        for i, df in enumerate(all_data):
            all_data[i] = df.reset_index(drop=True)
        combined = pd.concat(all_data, ignore_index=True)
        # Remove any duplicate columns
        combined = combined.loc[:, ~combined.columns.duplicated()]
        print(f"  Total: {len(combined)} rows from {len(all_data)} symbols")
        return combined

    return None


def main():
    """Main execution"""
    print("="*60)
    print("PARALLEL TWELVEDATA FETCHER - TODAY'S DATA")
    print(f"Started: {datetime.now()}")
    print(f"$229 Plan: {CREDITS_PER_MIN} credits/min")
    print("="*60)

    all_results = []

    # Fetch Stocks (parallel 3 workers to stay within rate limits)
    stocks_data = fetch_symbols_parallel(TOP_100_STOCKS[:50], 'STOCK', max_workers=3)
    if stocks_data is not None:
        all_results.append(stocks_data)

    # Fetch more stocks
    stocks_data2 = fetch_symbols_parallel(TOP_100_STOCKS[50:], 'STOCK', max_workers=3)
    if stocks_data2 is not None:
        all_results.append(stocks_data2)

    # Fetch Crypto
    crypto_data = fetch_symbols_parallel(TOP_20_CRYPTO, 'CRYPTO', max_workers=2)
    if crypto_data is not None:
        all_results.append(crypto_data)

    # Fetch ETFs
    etf_data = fetch_symbols_parallel(KEY_ETFS, 'ETF', max_workers=2)
    if etf_data is not None:
        all_results.append(etf_data)

    # Combine and upload
    if all_results:
        final_df = pd.concat(all_results, ignore_index=True)
        final_df['fetch_timestamp'] = datetime.now(timezone.utc)

        print(f"\n{'='*60}")
        print(f"UPLOAD TO BIGQUERY")
        print(f"{'='*60}")
        print(f"Total rows: {len(final_df)}")
        print(f"Columns: {len(final_df.columns)}")
        print(f"Symbols: {final_df['symbol'].nunique()}")

        # Upload to daily features table
        success = upload_to_bigquery(final_df, 'daily_features_24')
        if success:
            print("  Uploaded to ml_models.daily_features_24")

        # Also save to CSV as backup
        csv_path = f"C:/1AITrading/Trading/twelvedata_today_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        final_df.to_csv(csv_path, index=False)
        print(f"  Saved to {csv_path}")

        # Print summary
        print(f"\n{'='*60}")
        print("SUMMARY BY ASSET TYPE")
        print(f"{'='*60}")
        summary = final_df.groupby('asset_type').agg({
            'symbol': 'nunique',
            'datetime': 'count',
            'growth_score': 'mean'
        }).rename(columns={'symbol': 'symbols', 'datetime': 'rows', 'growth_score': 'avg_growth_score'})
        print(summary.to_string())

        # Print top growth scores
        print(f"\n{'='*60}")
        print("TOP 10 GROWTH SCORES")
        print(f"{'='*60}")
        latest = final_df.sort_values('datetime').groupby('symbol').tail(1)
        top_scores = latest.nlargest(10, 'growth_score')[['symbol', 'asset_type', 'close', 'growth_score', 'trend_regime', 'in_rise_cycle']]
        print(top_scores.to_string(index=False))

    print(f"\n{'='*60}")
    print(f"COMPLETED: {datetime.now()}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
