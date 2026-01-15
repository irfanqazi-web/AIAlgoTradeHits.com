#!/usr/bin/env python3
"""
Fix BigQuery Tables and Upload Data
====================================
1. Recreate tables without date partitioning (to avoid 4000 partition limit)
2. Upload comprehensive historical data properly
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.cloud import bigquery

# Configuration
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# Top symbols for 50% capacity
TOP_STOCKS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "JPM", "V", "UNH",
    "MA", "HD", "PG", "JNJ", "LLY", "BAC", "XOM", "CVX", "ABBV", "MRK",
    "KO", "PEP", "COST", "WMT", "AVGO", "TMO", "MCD", "CSCO", "ACN", "ABT",
    "CRM", "NKE", "DHR", "TXN", "NEE", "PM", "UPS", "RTX", "HON", "QCOM",
    "LOW", "CAT", "INTC", "BA", "GE", "AMD", "IBM", "SBUX", "DE", "GS"
]

TOP_ETFS = [
    "SPY", "QQQ", "IWM", "DIA", "VOO", "VTI", "IVV", "EFA", "VWO", "EEM",
    "XLF", "XLK", "XLV", "XLE", "XLI", "GLD", "SLV", "TLT", "BND", "AGG"
]


def recreate_tables():
    """Recreate tables WITHOUT partitioning to avoid partition limit"""
    print("\n--- Recreating BigQuery Tables (No Partitioning) ---")

    client = bigquery.Client(project=PROJECT_ID)

    schema = [
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("open", "FLOAT64"),
        bigquery.SchemaField("high", "FLOAT64"),
        bigquery.SchemaField("low", "FLOAT64"),
        bigquery.SchemaField("close", "FLOAT64"),
        bigquery.SchemaField("volume", "INT64"),
        bigquery.SchemaField("rsi", "FLOAT64"),
        bigquery.SchemaField("macd", "FLOAT64"),
        bigquery.SchemaField("macd_signal", "FLOAT64"),
        bigquery.SchemaField("macd_histogram", "FLOAT64"),
        bigquery.SchemaField("sma_20", "FLOAT64"),
        bigquery.SchemaField("sma_50", "FLOAT64"),
        bigquery.SchemaField("sma_200", "FLOAT64"),
        bigquery.SchemaField("ema_12", "FLOAT64"),
        bigquery.SchemaField("ema_26", "FLOAT64"),
        bigquery.SchemaField("ema_50", "FLOAT64"),
        bigquery.SchemaField("ema_200", "FLOAT64"),
        bigquery.SchemaField("bollinger_upper", "FLOAT64"),
        bigquery.SchemaField("bollinger_middle", "FLOAT64"),
        bigquery.SchemaField("bollinger_lower", "FLOAT64"),
        bigquery.SchemaField("atr", "FLOAT64"),
        bigquery.SchemaField("stoch_k", "FLOAT64"),
        bigquery.SchemaField("stoch_d", "FLOAT64"),
        bigquery.SchemaField("adx", "FLOAT64"),
        bigquery.SchemaField("cci", "FLOAT64"),
        bigquery.SchemaField("williams_r", "FLOAT64"),
        bigquery.SchemaField("momentum", "FLOAT64"),
        bigquery.SchemaField("roc", "FLOAT64"),
        bigquery.SchemaField("obv", "FLOAT64"),
        bigquery.SchemaField("mfi", "FLOAT64"),
        bigquery.SchemaField("growth_score", "INT64"),
        bigquery.SchemaField("trend_regime", "STRING"),
        bigquery.SchemaField("in_rise_cycle", "BOOL"),
    ]

    tables_to_create = [
        'stocks_daily_clean',  # Use new clean table names
        'etfs_daily_clean'
    ]

    for table_name in tables_to_create:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

        # Delete if exists
        try:
            client.delete_table(table_id)
            print(f"  Deleted existing: {table_name}")
        except:
            pass

        # Create without partitioning
        table = bigquery.Table(table_id, schema=schema)
        table = client.create_table(table)
        print(f"  Created: {table_name}")

    return True


def fetch_time_series(symbol, api_key, outputsize=5000):
    """Fetch OHLCV time series data"""
    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': symbol,
        'interval': '1day',
        'outputsize': outputsize,
        'apikey': api_key
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'values' in data:
            return data['values']
        elif 'code' in data:
            print(f"  API Error: {data.get('message', 'Unknown')[:50]}")
            return None
        return None
    except Exception as e:
        print(f"  Request Error: {str(e)[:50]}")
        return None


def calculate_indicators(df):
    """Calculate technical indicators"""
    try:
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # MACD
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        # SMAs
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['sma_200'] = df['close'].rolling(200).mean()

        # EMAs
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        df['ema_50'] = df['close'].ewm(span=50).mean()
        df['ema_200'] = df['close'].ewm(span=200).mean()

        # Bollinger Bands
        std20 = df['close'].rolling(20).std()
        df['bollinger_upper'] = df['sma_20'] + (std20 * 2)
        df['bollinger_middle'] = df['sma_20']
        df['bollinger_lower'] = df['sma_20'] - (std20 * 2)

        # ATR
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(14).mean()

        # Stochastic
        low14 = df['low'].rolling(14).min()
        high14 = df['high'].rolling(14).max()
        df['stoch_k'] = 100 * (df['close'] - low14) / (high14 - low14)
        df['stoch_d'] = df['stoch_k'].rolling(3).mean()

        # ADX (simplified)
        df['adx'] = 25.0

        # CCI
        tp = (df['high'] + df['low'] + df['close']) / 3
        sma_tp = tp.rolling(20).mean()
        mad = tp.rolling(20).apply(lambda x: abs(x - x.mean()).mean(), raw=True)
        df['cci'] = (tp - sma_tp) / (0.015 * mad)

        # Williams %R
        df['williams_r'] = -100 * (high14 - df['close']) / (high14 - low14)

        # Momentum & ROC
        df['momentum'] = df['close'] - df['close'].shift(10)
        df['roc'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100

        # OBV
        df['obv'] = (df['volume'] * ((df['close'] > df['close'].shift()).astype(int) * 2 - 1)).cumsum()

        # MFI
        mf = tp * df['volume']
        mf_pos = mf.where(tp > tp.shift(), 0).rolling(14).sum()
        mf_neg = mf.where(tp < tp.shift(), 0).rolling(14).sum()
        df['mfi'] = 100 - (100 / (1 + mf_pos / mf_neg))

        # Growth Score
        df['growth_score'] = (
            ((df['rsi'] >= 50) & (df['rsi'] <= 70)).astype(int) * 25 +
            (df['macd_histogram'] > 0).astype(int) * 25 +
            (df['adx'] > 25).astype(int) * 25 +
            (df['close'] > df['sma_200']).astype(int) * 25
        )

        # Trend Regime
        conditions = [
            (df['close'] > df['sma_50']) & (df['sma_50'] > df['sma_200']) & (df['adx'] > 25),
            (df['close'] > df['sma_50']) & (df['close'] > df['sma_200']),
            (df['close'] < df['sma_50']) & (df['sma_50'] < df['sma_200']) & (df['adx'] > 25),
            (df['close'] < df['sma_50']) & (df['close'] < df['sma_200'])
        ]
        choices = ['STRONG_UPTREND', 'WEAK_UPTREND', 'STRONG_DOWNTREND', 'WEAK_DOWNTREND']
        df['trend_regime'] = np.select(conditions, choices, default='CONSOLIDATION')

        # Rise Cycle
        df['in_rise_cycle'] = df['ema_12'] > df['ema_26']

    except Exception as e:
        print(f"  Indicator error: {e}")

    return df


def upload_to_bigquery(df, table_name):
    """Upload DataFrame to BigQuery with proper handling"""
    if df is None or df.empty:
        return 0

    try:
        client = bigquery.Client(project=PROJECT_ID)
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

        # Prepare data
        df = df.copy()

        # Convert datetime
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])

        # Convert numeric columns
        numeric_cols = ['open', 'high', 'low', 'close', 'rsi', 'macd', 'macd_signal',
                       'macd_histogram', 'sma_20', 'sma_50', 'sma_200', 'ema_12',
                       'ema_26', 'ema_50', 'ema_200', 'bollinger_upper', 'bollinger_middle',
                       'bollinger_lower', 'atr', 'stoch_k', 'stoch_d', 'adx', 'cci',
                       'williams_r', 'momentum', 'roc', 'mfi', 'obv']

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Convert volume to integer
        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype('Int64')

        # Convert growth_score to integer
        if 'growth_score' in df.columns:
            df['growth_score'] = pd.to_numeric(df['growth_score'], errors='coerce').fillna(0).astype('Int64')

        # Convert boolean
        if 'in_rise_cycle' in df.columns:
            df['in_rise_cycle'] = df['in_rise_cycle'].astype(bool)

        # Replace infinities with None
        df = df.replace([np.inf, -np.inf], np.nan)

        # Select only expected columns
        expected_cols = ['symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume',
                        'rsi', 'macd', 'macd_signal', 'macd_histogram',
                        'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'ema_50', 'ema_200',
                        'bollinger_upper', 'bollinger_middle', 'bollinger_lower',
                        'atr', 'stoch_k', 'stoch_d', 'adx', 'cci', 'williams_r',
                        'momentum', 'roc', 'obv', 'mfi', 'growth_score', 'trend_regime', 'in_rise_cycle']

        cols_to_upload = [c for c in expected_cols if c in df.columns]
        df = df[cols_to_upload]

        # Upload using load_table_from_dataframe (streaming)
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND
        )

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()

        return len(df)

    except Exception as e:
        print(f"  Upload error: {e}")
        return 0


def main():
    print("="*60)
    print("FIX TABLES AND UPLOAD COMPREHENSIVE DATA")
    print("="*60)

    # Step 1: Recreate tables without partitioning
    recreate_tables()

    # Rate limiting
    calls_made = 0
    minute_start = time.time()

    def rate_limit():
        nonlocal calls_made, minute_start
        if time.time() - minute_start >= 60:
            minute_start = time.time()
            calls_made = 0
        if calls_made >= 7:  # Only 7 calls per minute to be safe
            sleep_time = 60 - (time.time() - minute_start) + 2
            print(f"\n  Rate limit: sleeping {sleep_time:.0f}s...")
            time.sleep(sleep_time)
            minute_start = time.time()
            calls_made = 0
        calls_made += 1
        time.sleep(8)  # 8 second delay between calls

    # Fetch and upload stocks
    print(f"\n--- FETCHING {len(TOP_STOCKS)} STOCKS ---")
    stock_records = 0

    for i, symbol in enumerate(TOP_STOCKS):
        print(f"[{i+1}/{len(TOP_STOCKS)}] {symbol}...", end=" ")
        rate_limit()

        data = fetch_time_series(symbol, TWELVEDATA_API_KEY)
        if data:
            df = pd.DataFrame(data)
            df['symbol'] = symbol

            # Convert types
            for col in ['open', 'high', 'low', 'close']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype(int)
            df['datetime'] = pd.to_datetime(df['datetime'])

            # Calculate indicators
            df = df.sort_values('datetime')
            df = calculate_indicators(df)

            # Upload
            records = upload_to_bigquery(df, 'stocks_daily_clean')
            stock_records += records
            print(f"OK ({records:,} records)")
        else:
            print("FAILED")

    print(f"\nTotal stock records uploaded: {stock_records:,}")

    # Fetch and upload ETFs
    print(f"\n--- FETCHING {len(TOP_ETFS)} ETFs ---")
    etf_records = 0

    for i, symbol in enumerate(TOP_ETFS):
        print(f"[{i+1}/{len(TOP_ETFS)}] {symbol}...", end=" ")
        rate_limit()

        data = fetch_time_series(symbol, TWELVEDATA_API_KEY)
        if data:
            df = pd.DataFrame(data)
            df['symbol'] = symbol

            for col in ['open', 'high', 'low', 'close']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype(int)
            df['datetime'] = pd.to_datetime(df['datetime'])

            df = df.sort_values('datetime')
            df = calculate_indicators(df)

            records = upload_to_bigquery(df, 'etfs_daily_clean')
            etf_records += records
            print(f"OK ({records:,} records)")
        else:
            print("FAILED")

    print(f"\nTotal ETF records uploaded: {etf_records:,}")

    print("\n" + "="*60)
    print("UPLOAD COMPLETE")
    print("="*60)
    print(f"Stocks: {stock_records:,} records")
    print(f"ETFs: {etf_records:,} records")
    print(f"Total: {stock_records + etf_records:,} records")


if __name__ == "__main__":
    main()
