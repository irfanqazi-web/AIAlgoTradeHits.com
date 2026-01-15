#!/usr/bin/env python3
"""
Simple TwelveData Fetcher - Today's Data
Uses batch quotes + time_series for efficiency
$229 Plan optimized
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

# Configuration
PROJECT_ID = 'aialgotradehits'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'

# Key symbols to fetch
SYMBOLS = {
    'stocks': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM', 'V', 'JNJ',
               'WMT', 'PG', 'MA', 'HD', 'BAC', 'XOM', 'CVX', 'KO', 'PEP', 'MRK',
               'ABBV', 'COST', 'CRM', 'AMD', 'ADBE', 'NFLX', 'INTC', 'CSCO', 'VZ', 'DIS'],
    'crypto': ['BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'SOL/USD', 'DOGE/USD', 'ADA/USD',
               'AVAX/USD', 'LINK/USD', 'DOT/USD'],
    'etfs': ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI']
}

bq_client = bigquery.Client(project=PROJECT_ID)


def calculate_indicators(df):
    """Calculate all 24 indicators locally from OHLCV data"""
    if df is None or len(df) < 30:
        return df

    df = df.sort_values('datetime').copy()

    # Ensure numeric types
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        elif col == 'volume':
            df['volume'] = 0  # Default volume for crypto

    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['volume'].fillna(0)

    # SMAs
    df['sma_20'] = close.rolling(20).mean()
    df['sma_50'] = close.rolling(50).mean() if len(df) >= 50 else np.nan
    df['sma_200'] = close.rolling(200).mean() if len(df) >= 200 else np.nan

    # EMAs
    df['ema_12'] = close.ewm(span=12).mean()
    df['ema_20'] = close.ewm(span=20).mean()
    df['ema_26'] = close.ewm(span=26).mean()
    df['ema_50'] = close.ewm(span=50).mean()
    df['ema_200'] = close.ewm(span=200).mean() if len(df) >= 200 else np.nan

    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df['rsi_14'] = 100 - (100 / (1 + rs))

    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # Bollinger Bands
    df['bb_middle'] = df['sma_20']
    std = close.rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + (2 * std)
    df['bb_lower'] = df['bb_middle'] - (2 * std)

    # ATR
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr_14'] = tr.rolling(14).mean()

    # Stochastic
    low_14 = low.rolling(14).min()
    high_14 = high.rolling(14).max()
    df['stoch_k'] = 100 * (close - low_14) / (high_14 - low_14)
    df['stoch_d'] = df['stoch_k'].rolling(3).mean()

    # ADX
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

    atr = tr.ewm(span=14).mean()
    df['plus_di'] = 100 * (plus_dm.ewm(span=14).mean() / atr)
    df['minus_di'] = 100 * (minus_dm.ewm(span=14).mean() / atr)
    dx = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
    df['adx'] = dx.ewm(span=14).mean()

    # MFI (Money Flow Index)
    typical_price = (high + low + close) / 3
    money_flow = typical_price * volume
    positive_flow = money_flow.where(typical_price > typical_price.shift(), 0).rolling(14).sum()
    negative_flow = money_flow.where(typical_price < typical_price.shift(), 0).rolling(14).sum()
    mfi_ratio = positive_flow / negative_flow.replace(0, np.nan)
    df['mfi'] = 100 - (100 / (1 + mfi_ratio))

    # CMF (Chaikin Money Flow)
    mf_multiplier = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
    mf_volume = mf_multiplier * volume
    df['cmf'] = mf_volume.rolling(20).sum() / volume.rolling(20).sum()

    # Growth Score (per masterquery.md)
    df['growth_score'] = 0
    df.loc[(df['rsi_14'] >= 50) & (df['rsi_14'] <= 70), 'growth_score'] += 25
    df.loc[df['macd_hist'] > 0, 'growth_score'] += 25
    df.loc[df['adx'] > 25, 'growth_score'] += 25
    if 'sma_200' in df.columns:
        df.loc[df['close'] > df['sma_200'], 'growth_score'] += 25

    # Trend Regime
    df['trend_regime'] = 'CONSOLIDATION'
    if 'sma_50' in df.columns and 'sma_200' in df.columns:
        mask = (df['close'] > df['sma_50']) & (df['adx'] > 25)
        df.loc[mask, 'trend_regime'] = 'STRONG_UPTREND'
        mask = (df['close'] > df['sma_50']) & (df['adx'] <= 25)
        df.loc[mask, 'trend_regime'] = 'WEAK_UPTREND'
        mask = (df['close'] < df['sma_50']) & (df['adx'] > 25)
        df.loc[mask, 'trend_regime'] = 'STRONG_DOWNTREND'
        mask = (df['close'] < df['sma_50']) & (df['adx'] <= 25)
        df.loc[mask, 'trend_regime'] = 'WEAK_DOWNTREND'

    # Rise Cycle
    df['in_rise_cycle'] = df['ema_12'] > df['ema_26']

    return df


def fetch_time_series(symbol, outputsize=250):
    """Fetch OHLCV time series data"""
    try:
        url = f"{BASE_URL}/time_series"
        params = {
            'symbol': symbol,
            'interval': '1day',
            'outputsize': outputsize,
            'apikey': TWELVEDATA_API_KEY
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'values' not in data:
            print(f"  No data for {symbol}: {data.get('message', 'Unknown error')[:50]}")
            return None

        df = pd.DataFrame(data['values'])
        df['symbol'] = symbol.replace('/', '')
        df['datetime'] = pd.to_datetime(df['datetime'])

        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    except Exception as e:
        print(f"  Error fetching {symbol}: {e}")
        return None


def main():
    print("="*60)
    print("TWELVEDATA FETCHER - TODAY'S DATA WITH INDICATORS")
    print(f"Started: {datetime.now()}")
    print("="*60)

    all_data = []

    for asset_type, symbols in SYMBOLS.items():
        print(f"\n[{asset_type.upper()}] Fetching {len(symbols)} symbols...")

        for symbol in symbols:
            print(f"  Fetching {symbol}...", end=" ")

            df = fetch_time_series(symbol, outputsize=250)
            if df is not None and len(df) > 0:
                # Calculate indicators
                df = calculate_indicators(df)
                df['asset_type'] = asset_type.upper()

                # Get latest row only
                latest = df.sort_values('datetime').tail(1).copy()
                all_data.append(latest)

                gs = latest['growth_score'].iloc[0] if 'growth_score' in latest.columns else 0
                tr = latest['trend_regime'].iloc[0] if 'trend_regime' in latest.columns else 'N/A'
                print(f"OK - GS:{gs}, {tr}")
            else:
                print("FAILED")

            time.sleep(0.5)  # Rate limit

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df['fetch_timestamp'] = datetime.now(timezone.utc)

        print(f"\n{'='*60}")
        print(f"RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"Total symbols: {len(final_df)}")
        print(f"Columns: {len(final_df.columns)}")

        # Save to CSV
        csv_path = f"C:/1AITrading/Trading/today_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        final_df.to_csv(csv_path, index=False)
        print(f"Saved to: {csv_path}")

        # Upload to BigQuery
        try:
            table_ref = f"{PROJECT_ID}.ml_models.daily_features_24"
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
            )
            job = bq_client.load_table_from_dataframe(final_df, table_ref, job_config=job_config)
            job.result()
            print(f"Uploaded to BigQuery: {table_ref}")
        except Exception as e:
            print(f"BigQuery upload error: {e}")

        # Top growth scores
        print(f"\n{'='*60}")
        print("TOP 10 GROWTH SCORES")
        print(f"{'='*60}")
        top = final_df.nlargest(10, 'growth_score')[['symbol', 'asset_type', 'close', 'growth_score', 'trend_regime', 'rsi_14']]
        print(top.to_string(index=False))

    print(f"\n{'='*60}")
    print(f"COMPLETED: {datetime.now()}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
