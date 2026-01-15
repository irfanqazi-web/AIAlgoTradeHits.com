#!/usr/bin/env python3
"""
FIX AAPL AND BTC INDICATOR CALCULATIONS
=======================================
Based on DATA_QUALITY_IMPACT_REPORT.md and ML_VALIDATION_ANALYSIS_REPORT.md

Issues to fix:
1. AAPL: 80% of indicators are NULL (pivot_high_flag, pivot_low_flag, vwap_daily,
   awesome_osc, cci, mfi, rsi variants, macd variants, momentum)
2. BTC-USD: 100% of mfi is NULL, 78-80% of other indicators NULL
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

import time
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from google.cloud import bigquery

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# ============================================================
# TECHNICAL INDICATORS - MATCHING TRADINGVIEW/INDUSTRY STANDARD
# ============================================================

def calculate_sma(series, period):
    """Simple Moving Average"""
    return series.rolling(window=period, min_periods=period).mean()

def calculate_ema(series, period):
    """Exponential Moving Average"""
    return series.ewm(span=period, adjust=False, min_periods=period).mean()

def calculate_rsi(series, period=14):
    """RSI using Wilder's RMA (ewm alpha=1/period) - Industry Standard"""
    delta = series.diff()
    gain = delta.where(delta > 0, 0).ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    rs = gain / loss
    return (100 - (100 / (1 + rs))).replace([np.inf, -np.inf], np.nan)

def calculate_atr(high, low, close, period=14):
    """ATR using Wilder's RMA"""
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False, min_periods=period).mean()

def calculate_adx(high, low, close, period=14):
    """ADX using Wilder's RMA"""
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

    atr = calculate_atr(high, low, close, period)

    plus_dm_smooth = plus_dm.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    minus_dm_smooth = minus_dm.ewm(alpha=1/period, adjust=False, min_periods=period).mean()

    plus_di = 100 * plus_dm_smooth / atr
    minus_di = 100 * minus_dm_smooth / atr
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.ewm(alpha=1/period, adjust=False, min_periods=period).mean()

    return (adx.replace([np.inf, -np.inf], np.nan),
            plus_di.replace([np.inf, -np.inf], np.nan),
            minus_di.replace([np.inf, -np.inf], np.nan))

def calculate_stochastic(high, low, close, k_period=14, d_period=3):
    """Slow Stochastic"""
    lowest_low = low.rolling(window=k_period, min_periods=k_period).min()
    highest_high = high.rolling(window=k_period, min_periods=k_period).max()
    raw_k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    k = raw_k.rolling(window=d_period, min_periods=d_period).mean()
    d = k.rolling(window=d_period, min_periods=d_period).mean()
    return k.replace([np.inf, -np.inf], np.nan), d.replace([np.inf, -np.inf], np.nan)

def calculate_roc(series, period=10):
    """Rate of Change"""
    return ((series - series.shift(period)) / series.shift(period) * 100).replace([np.inf, -np.inf], np.nan)

def calculate_bollinger_bands(series, period=20, std_dev=2):
    """Bollinger Bands"""
    sma = calculate_sma(series, period)
    std = series.rolling(window=period, min_periods=period).std(ddof=0)
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower

def calculate_macd(series, fast=12, slow=26, signal=9):
    """MACD"""
    ema_fast = calculate_ema(series, fast)
    ema_slow = calculate_ema(series, slow)
    macd = ema_fast - ema_slow
    signal_line = calculate_ema(macd, signal)
    histogram = macd - signal_line
    return macd, signal_line, histogram

def calculate_cci(high, low, close, period=20):
    """Commodity Channel Index"""
    tp = (high + low + close) / 3
    sma_tp = tp.rolling(window=period, min_periods=period).mean()
    mean_dev = tp.rolling(window=period, min_periods=period).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    return ((tp - sma_tp) / (0.015 * mean_dev)).replace([np.inf, -np.inf], np.nan)

def calculate_williams_r(high, low, close, period=14):
    """Williams %R"""
    highest_high = high.rolling(window=period, min_periods=period).max()
    lowest_low = low.rolling(window=period, min_periods=period).min()
    return (-100 * (highest_high - close) / (highest_high - lowest_low)).replace([np.inf, -np.inf], np.nan)

def calculate_obv(close, volume):
    """On-Balance Volume"""
    direction = np.sign(close.diff())
    return (direction * volume).cumsum()

def calculate_mfi(high, low, close, volume, period=14):
    """Money Flow Index - CRITICAL: This was 100% NULL for BTC"""
    if volume.isna().all() or (volume == 0).all():
        print("    WARNING: Volume is all NULL or zero, cannot calculate MFI")
        return pd.Series([np.nan] * len(close), index=close.index)

    tp = (high + low + close) / 3
    raw_money_flow = tp * volume

    # Handle edge cases
    positive_flow = raw_money_flow.where(tp > tp.shift(1), 0)
    negative_flow = raw_money_flow.where(tp < tp.shift(1), 0)

    positive_sum = positive_flow.rolling(window=period, min_periods=period).sum()
    negative_sum = negative_flow.rolling(window=period, min_periods=period).sum()

    # Avoid division by zero
    mfi = 100 - (100 / (1 + positive_sum / negative_sum.replace(0, np.nan)))
    return mfi.replace([np.inf, -np.inf], np.nan)

def calculate_cmf(high, low, close, volume, period=20):
    """Chaikin Money Flow"""
    if volume.isna().all() or (volume == 0).all():
        return pd.Series([np.nan] * len(close), index=close.index)
    mfm = ((close - low) - (high - close)) / (high - low)
    mfv = mfm * volume
    cmf = mfv.rolling(window=period, min_periods=period).sum() / volume.rolling(window=period, min_periods=period).sum()
    return cmf.replace([np.inf, -np.inf], np.nan)

def calculate_pvo(volume, fast=12, slow=26):
    """Price Volume Oscillator"""
    if volume.isna().all() or (volume == 0).all():
        return pd.Series([np.nan] * len(volume), index=volume.index)
    ema_fast = calculate_ema(volume, fast)
    ema_slow = calculate_ema(volume, slow)
    return ((ema_fast - ema_slow) / ema_slow * 100).replace([np.inf, -np.inf], np.nan)

def calculate_ppo(series, fast=12, slow=26):
    """Percentage Price Oscillator"""
    ema_fast = calculate_ema(series, fast)
    ema_slow = calculate_ema(series, slow)
    return ((ema_fast - ema_slow) / ema_slow * 100).replace([np.inf, -np.inf], np.nan)

def calculate_trix(series, period=15):
    """Triple EMA Oscillator"""
    ema1 = calculate_ema(series, period)
    ema2 = calculate_ema(ema1, period)
    ema3 = calculate_ema(ema2, period)
    return (100 * ema3.pct_change()).replace([np.inf, -np.inf], np.nan)

def calculate_kama(series, period=10, fast=2, slow=30):
    """Kaufman Adaptive Moving Average"""
    change = abs(series - series.shift(period))
    volatility = abs(series.diff()).rolling(window=period, min_periods=period).sum()
    er = change / volatility
    fast_sc = 2 / (fast + 1)
    slow_sc = 2 / (slow + 1)
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
    kama = series.copy()
    for i in range(period, len(series)):
        if pd.notna(sc.iloc[i]) and pd.notna(kama.iloc[i-1]):
            kama.iloc[i] = kama.iloc[i-1] + sc.iloc[i] * (series.iloc[i] - kama.iloc[i-1])
    return kama.replace([np.inf, -np.inf], np.nan)

def calculate_ultimate_oscillator(high, low, close, period1=7, period2=14, period3=28):
    """Ultimate Oscillator"""
    bp = close - pd.concat([low, close.shift(1)], axis=1).min(axis=1)
    tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
    avg1 = bp.rolling(window=period1, min_periods=period1).sum() / tr.rolling(window=period1, min_periods=period1).sum()
    avg2 = bp.rolling(window=period2, min_periods=period2).sum() / tr.rolling(window=period2, min_periods=period2).sum()
    avg3 = bp.rolling(window=period3, min_periods=period3).sum() / tr.rolling(window=period3, min_periods=period3).sum()
    return (100 * (4 * avg1 + 2 * avg2 + avg3) / 7).replace([np.inf, -np.inf], np.nan)

def calculate_awesome_oscillator(high, low, fast=5, slow=34):
    """Awesome Oscillator - CRITICAL: This was 80% NULL for AAPL"""
    mp = (high + low) / 2
    return (calculate_sma(mp, fast) - calculate_sma(mp, slow)).replace([np.inf, -np.inf], np.nan)

def calculate_vwap(high, low, close, volume):
    """VWAP - Daily reset"""
    tp = (high + low + close) / 3
    return (tp * volume).cumsum() / volume.cumsum()

def calculate_pivot_flags(high, low, close, lookback=5):
    """Pivot High/Low flags - CRITICAL: This was 80% NULL for AAPL"""
    pivot_high = pd.Series(0, index=close.index)
    pivot_low = pd.Series(0, index=close.index)

    for i in range(lookback, len(close) - lookback):
        # Pivot High: high[i] is higher than all nearby highs
        if high.iloc[i] == high.iloc[i-lookback:i+lookback+1].max():
            pivot_high.iloc[i] = 1
        # Pivot Low: low[i] is lower than all nearby lows
        if low.iloc[i] == low.iloc[i-lookback:i+lookback+1].min():
            pivot_low.iloc[i] = 1

    return pivot_high, pivot_low


def recalculate_all_indicators(df):
    """Recalculate ALL indicators"""
    print(f"    Recalculating indicators for {len(df)} rows...")

    # Sort by datetime
    df = df.sort_values('datetime').reset_index(drop=True)

    # Ensure volume is numeric
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0)

    # Basic calculations
    df['previous_close'] = df['close'].shift(1)
    df['change'] = df['close'] - df['previous_close']
    df['percent_change'] = (df['change'] / df['previous_close'] * 100).replace([np.inf, -np.inf], np.nan)

    # RSI
    df['rsi'] = calculate_rsi(df['close'])

    # ATR
    df['atr'] = calculate_atr(df['high'], df['low'], df['close'])

    # ADX
    df['adx'], df['plus_di'], df['minus_di'] = calculate_adx(df['high'], df['low'], df['close'])

    # Stochastic
    df['stoch_k'], df['stoch_d'] = calculate_stochastic(df['high'], df['low'], df['close'])

    # ROC
    df['roc'] = calculate_roc(df['close'])

    # Bollinger Bands
    df['bollinger_upper'], df['bollinger_middle'], df['bollinger_lower'] = calculate_bollinger_bands(df['close'])
    df['bb_width'] = ((df['bollinger_upper'] - df['bollinger_lower']) / df['bollinger_middle'] * 100).replace([np.inf, -np.inf], np.nan)

    # Moving Averages
    df['sma_20'] = calculate_sma(df['close'], 20)
    df['sma_50'] = calculate_sma(df['close'], 50)
    df['sma_200'] = calculate_sma(df['close'], 200)
    df['ema_12'] = calculate_ema(df['close'], 12)
    df['ema_20'] = calculate_ema(df['close'], 20)
    df['ema_26'] = calculate_ema(df['close'], 26)
    df['ema_50'] = calculate_ema(df['close'], 50)
    df['ema_200'] = calculate_ema(df['close'], 200)

    # MACD
    df['macd'], df['macd_signal'], df['macd_histogram'] = calculate_macd(df['close'])

    # CCI - CRITICAL
    df['cci'] = calculate_cci(df['high'], df['low'], df['close'])

    # Williams %R
    df['williams_r'] = calculate_williams_r(df['high'], df['low'], df['close'])

    # Momentum - CRITICAL
    df['momentum'] = df['close'] - df['close'].shift(10)

    # OBV
    df['obv'] = calculate_obv(df['close'], df['volume'])

    # MFI - CRITICAL: Was 100% NULL for BTC
    df['mfi'] = calculate_mfi(df['high'], df['low'], df['close'], df['volume'])

    # CMF
    df['cmf'] = calculate_cmf(df['high'], df['low'], df['close'], df['volume'])

    # PVO
    df['pvo'] = calculate_pvo(df['volume'])

    # PPO
    df['ppo'] = calculate_ppo(df['close'])

    # TRIX
    df['trix'] = calculate_trix(df['close'])

    # KAMA
    df['kama'] = calculate_kama(df['close'])

    # Ultimate Oscillator
    df['ultimate_osc'] = calculate_ultimate_oscillator(df['high'], df['low'], df['close'])

    # Awesome Oscillator - CRITICAL: Was 80% NULL for AAPL
    df['awesome_osc'] = calculate_awesome_oscillator(df['high'], df['low'])

    # VWAP - CRITICAL: Was 80% NULL for AAPL
    df['vwap_daily'] = calculate_vwap(df['high'], df['low'], df['close'], df['volume'])

    # Pivot Flags - CRITICAL: Was 80% NULL for AAPL
    df['pivot_high_flag'], df['pivot_low_flag'] = calculate_pivot_flags(df['high'], df['low'], df['close'])

    # RSI derived - CRITICAL: Were 80% NULL for AAPL
    df['rsi_slope'] = df['rsi'].diff(5).replace([np.inf, -np.inf], np.nan)
    df['rsi_zscore'] = ((df['rsi'] - df['rsi'].rolling(window=20, min_periods=20).mean()) /
                        df['rsi'].rolling(window=20, min_periods=20).std()).replace([np.inf, -np.inf], np.nan)
    df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
    df['rsi_oversold'] = (df['rsi'] < 30).astype(int)

    # MACD derived - CRITICAL: Was 80% NULL for AAPL
    df['macd_cross'] = (df['macd'] > df['macd_signal']).astype(int)

    # EMA slopes
    df['ema20_slope'] = df['ema_20'].diff(5).replace([np.inf, -np.inf], np.nan)
    df['ema50_slope'] = df['ema_50'].diff(5).replace([np.inf, -np.inf], np.nan)

    # ATR derived
    df['atr_zscore'] = ((df['atr'] - df['atr'].rolling(window=20, min_periods=20).mean()) /
                        df['atr'].rolling(window=20, min_periods=20).std()).replace([np.inf, -np.inf], np.nan)
    df['atr_slope'] = df['atr'].diff(5).replace([np.inf, -np.inf], np.nan)

    # Volume derived
    df['volume_zscore'] = ((df['volume'] - df['volume'].rolling(window=20, min_periods=20).mean()) /
                           df['volume'].rolling(window=20, min_periods=20).std()).replace([np.inf, -np.inf], np.nan)
    df['volume_ratio'] = (df['volume'] / df['volume'].rolling(window=20, min_periods=1).mean()).replace([np.inf, -np.inf], np.nan)

    # Price vs MA percentages
    df['close_vs_sma20_pct'] = ((df['close'] - df['sma_20']) / df['sma_20'] * 100).replace([np.inf, -np.inf], np.nan)
    df['close_vs_sma50_pct'] = ((df['close'] - df['sma_50']) / df['sma_50'] * 100).replace([np.inf, -np.inf], np.nan)
    df['close_vs_sma200_pct'] = ((df['close'] - df['sma_200']) / df['sma_200'] * 100).replace([np.inf, -np.inf], np.nan)

    # Trend/Vol regimes
    df['trend_regime'] = (df['close'] > df['sma_200']).astype(int)
    df['vol_regime'] = (df['atr'] > df['atr'].rolling(window=50, min_periods=50).mean()).astype(int)

    # Log return
    df['log_return'] = (np.log(df['close'] / df['close'].shift(1))).replace([np.inf, -np.inf], np.nan)

    # Period returns
    df['return_2w'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10) * 100).replace([np.inf, -np.inf], np.nan)
    df['return_4w'] = ((df['close'] - df['close'].shift(20)) / df['close'].shift(20) * 100).replace([np.inf, -np.inf], np.nan)

    # Update timestamps
    df['updated_at'] = pd.Timestamp.now(tz='UTC')

    # Count non-null indicators
    key_indicators = ['rsi', 'mfi', 'macd', 'cci', 'awesome_osc', 'vwap_daily', 'pivot_high_flag', 'momentum']
    for ind in key_indicators:
        if ind in df.columns:
            non_null = df[ind].notna().sum()
            print(f"      {ind}: {non_null}/{len(df)} non-null ({100*non_null/len(df):.1f}%)")

    return df


def fix_symbol(table_name, symbol, symbol_column='symbol'):
    """Fix indicators for a specific symbol"""
    print(f"\n{'='*60}")
    print(f"Fixing {symbol} in {table_name}")
    print(f"{'='*60}")

    try:
        # Fetch all data for symbol
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE {symbol_column} = '{symbol}'
        ORDER BY datetime ASC
        """
        df = client.query(query).to_dataframe()

        if len(df) == 0:
            print(f"  No data found for {symbol}")
            return False

        if len(df) < 50:
            print(f"  Skipping {symbol}: Only {len(df)} rows (need at least 50)")
            return False

        print(f"  Fetched {len(df)} rows")

        # Check current data quality BEFORE fix
        print(f"\n  BEFORE FIX:")
        for col in ['rsi', 'mfi', 'macd', 'cci', 'awesome_osc', 'pivot_high_flag']:
            if col in df.columns:
                non_null = df[col].notna().sum()
                print(f"    {col}: {non_null}/{len(df)} ({100*non_null/len(df):.1f}%)")

        # Recalculate indicators
        print(f"\n  RECALCULATING...")
        df = recalculate_all_indicators(df)

        # Delete existing data
        print(f"\n  Deleting old data...")
        delete_query = f"""
        DELETE FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE {symbol_column} = '{symbol}'
        """
        client.query(delete_query).result()

        # Ensure proper types
        if 'average_volume' in df.columns:
            df['average_volume'] = df['average_volume'].fillna(0).astype('Int64')
        if 'obv' in df.columns:
            df['obv'] = df['obv'].fillna(0).astype('Int64')
        if 'volume' in df.columns:
            df['volume'] = df['volume'].fillna(0).astype('Int64')

        # Replace inf with NaN
        for col in df.select_dtypes(include=[np.floating]).columns:
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)

        # Upload
        print(f"  Uploading {len(df)} rows...")
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()

        print(f"  SUCCESS: Uploaded {len(df)} rows with fixed indicators")
        return True

    except Exception as e:
        print(f"  ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("FIX AAPL AND BTC INDICATOR CALCULATIONS")
    print("=" * 70)
    print()
    print("Issues being fixed:")
    print("  - AAPL: 80% NULL for pivot_high_flag, pivot_low_flag, vwap_daily,")
    print("          awesome_osc, cci, mfi, rsi variants, macd variants, momentum")
    print("  - BTC-USD: 100% NULL for mfi, 78-80% NULL for other indicators")
    print()

    start_time = time.time()

    results = []

    # Fix AAPL in stocks_daily_clean
    print("\n" + "="*70)
    print("FIXING AAPL IN stocks_daily_clean")
    print("="*70)
    success = fix_symbol('stocks_daily_clean', 'AAPL', 'symbol')
    results.append(('AAPL', 'stocks_daily_clean', success))

    # Fix BTC variants in crypto_daily_clean
    print("\n" + "="*70)
    print("FIXING BTC VARIANTS IN crypto_daily_clean")
    print("="*70)

    # Get all BTC symbols
    btc_query = """
    SELECT DISTINCT symbol
    FROM `aialgotradehits.crypto_trading_data.crypto_daily_clean`
    WHERE symbol LIKE '%BTC%'
    """
    btc_symbols = client.query(btc_query).to_dataframe()

    for _, row in btc_symbols.iterrows():
        symbol = row['symbol']
        success = fix_symbol('crypto_daily_clean', symbol, 'symbol')
        results.append((symbol, 'crypto_daily_clean', success))
        time.sleep(1)  # Rate limit

    elapsed = time.time() - start_time

    print()
    print("=" * 70)
    print("FIX COMPLETE - SUMMARY")
    print("=" * 70)

    for symbol, table, success in results:
        status = "SUCCESS" if success else "FAILED"
        print(f"  {symbol} ({table}): {status}")

    print()
    print(f"Total time: {elapsed/60:.1f} minutes")
    print("=" * 70)


if __name__ == "__main__":
    main()
