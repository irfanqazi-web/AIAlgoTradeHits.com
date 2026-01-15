#!/usr/bin/env python3
"""
RECALCULATE ALL INDICATORS WITH SALEEM'S CORRECTIONS
=====================================================
Based on INDICATOR_CORRECTION_PLAN_FOR_IRFAN.md

Corrections Applied:
1. RSI: SMA -> Wilder's RMA (ewm alpha=1/period)
2. ATR: SMA -> Wilder's RMA (ewm alpha=1/period)
3. ADX/+DI/-DI: SMA -> Wilder's RMA (ewm alpha=1/period)
4. Stochastic: Fast -> Slow (smooth %K with SMA-3)
5. ROC: Period 12 -> 10
6. Ichimoku Senkou A/B: Add 26-period forward shift
7. Bollinger Bands: ddof=1 -> ddof=0 (population std dev)

This script recalculates indicators for:
- stocks_daily_clean (110 symbols)
- crypto_daily_clean (46 symbols)
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
# CORRECTED TECHNICAL INDICATORS - SALEEM'S SPECIFICATIONS
# ============================================================

def calculate_sma(series, period):
    """Simple Moving Average"""
    return series.rolling(window=period, min_periods=period).mean()

def calculate_ema(series, period):
    """Exponential Moving Average"""
    return series.ewm(span=period, adjust=False, min_periods=period).mean()

def calculate_rsi(series, period=14):
    """RSI using Wilder's RMA (ewm alpha=1/period) - Industry Standard / TradingView

    CORRECTION: Changed from SMA to Wilder's RMA for gain/loss smoothing
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0).ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    rs = gain / loss
    return (100 - (100 / (1 + rs))).replace([np.inf, -np.inf], np.nan)

def calculate_atr(high, low, close, period=14):
    """ATR using Wilder's RMA (ewm alpha=1/period) - Industry Standard / TradingView

    CORRECTION: Changed from SMA to Wilder's RMA for TR smoothing
    """
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False, min_periods=period).mean()

def calculate_adx(high, low, close, period=14):
    """ADX using Wilder's RMA (ewm alpha=1/period) - Industry Standard / TradingView

    CORRECTION: Changed from SMA/EMA to Wilder's RMA for all smoothing
    """
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
    """Slow Stochastic (TradingView default) - %K is smoothed with SMA(3)

    CORRECTION: Changed from Fast to Slow Stochastic
    Fast: %K = raw, %D = SMA(%K)
    Slow: %K = SMA(raw_k), %D = SMA(%K)
    """
    lowest_low = low.rolling(window=k_period, min_periods=k_period).min()
    highest_high = high.rolling(window=k_period, min_periods=k_period).max()
    raw_k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    # %K is smoothed (Slow Stochastic)
    k = raw_k.rolling(window=d_period, min_periods=d_period).mean()
    # %D is SMA of smoothed %K
    d = k.rolling(window=d_period, min_periods=d_period).mean()
    return k.replace([np.inf, -np.inf], np.nan), d.replace([np.inf, -np.inf], np.nan)

def calculate_roc(series, period=10):
    """ROC with period=10 (TradingView default)

    CORRECTION: Changed from period=12 to period=10
    """
    return ((series - series.shift(period)) / series.shift(period) * 100).replace([np.inf, -np.inf], np.nan)

def calculate_bollinger_bands(series, period=20, std_dev=2):
    """Bollinger Bands with ddof=0 (population std dev) - TradingView Standard

    CORRECTION: Changed from ddof=1 (sample) to ddof=0 (population)
    """
    sma = calculate_sma(series, period)
    std = series.rolling(window=period, min_periods=period).std(ddof=0)
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower

def calculate_ichimoku(high, low, close, tenkan=9, kijun=26, senkou_b=52):
    """Ichimoku Cloud with proper Senkou A/B 26-period forward shift - TradingView Standard

    CORRECTION: Added 26-period FORWARD shift to Senkou A and B
    """
    tenkan_sen = (high.rolling(window=tenkan, min_periods=tenkan).max() +
                  low.rolling(window=tenkan, min_periods=tenkan).min()) / 2
    kijun_sen = (high.rolling(window=kijun, min_periods=kijun).max() +
                 low.rolling(window=kijun, min_periods=kijun).min()) / 2

    # Calculate Senkou A and B (before shift)
    senkou_a_raw = (tenkan_sen + kijun_sen) / 2
    senkou_b_raw = (high.rolling(window=senkou_b, min_periods=senkou_b).max() +
                    low.rolling(window=senkou_b, min_periods=senkou_b).min()) / 2

    # Apply 26-period FORWARD shift to Senkou A and B (TradingView standard)
    senkou_a = senkou_a_raw.shift(kijun)  # Shift forward 26 periods
    senkou_b_line = senkou_b_raw.shift(kijun)  # Shift forward 26 periods

    # Chikou Span is shifted BACKWARD 26 periods
    chikou = close.shift(-kijun)

    return tenkan_sen, kijun_sen, senkou_a, senkou_b_line, chikou

def calculate_macd(series, fast=12, slow=26, signal=9):
    """MACD - No changes needed"""
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
    """Money Flow Index"""
    tp = (high + low + close) / 3
    raw_money_flow = tp * volume
    positive_flow = raw_money_flow.where(tp > tp.shift(1), 0).rolling(window=period, min_periods=period).sum()
    negative_flow = raw_money_flow.where(tp < tp.shift(1), 0).rolling(window=period, min_periods=period).sum()
    mfi = 100 - (100 / (1 + positive_flow / negative_flow))
    return mfi.replace([np.inf, -np.inf], np.nan)

def calculate_cmf(high, low, close, volume, period=20):
    """Chaikin Money Flow"""
    mfm = ((close - low) - (high - close)) / (high - low)
    mfv = mfm * volume
    cmf = mfv.rolling(window=period, min_periods=period).sum() / volume.rolling(window=period, min_periods=period).sum()
    return cmf.replace([np.inf, -np.inf], np.nan)

def calculate_pvo(volume, fast=12, slow=26):
    """Price Volume Oscillator"""
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
    """Awesome Oscillator"""
    mp = (high + low) / 2
    return (calculate_sma(mp, fast) - calculate_sma(mp, slow)).replace([np.inf, -np.inf], np.nan)


def recalculate_all_indicators(df):
    """Recalculate ALL indicators with Saleem's corrections"""

    # Sort by datetime
    df = df.sort_values('datetime').reset_index(drop=True)

    # Basic calculations
    df['previous_close'] = df['close'].shift(1)
    df['change'] = df['close'] - df['previous_close']
    df['percent_change'] = (df['change'] / df['previous_close'] * 100).replace([np.inf, -np.inf], np.nan)

    # RSI (CORRECTED: Wilder's RMA)
    df['rsi'] = calculate_rsi(df['close'])

    # ATR (CORRECTED: Wilder's RMA)
    df['atr'] = calculate_atr(df['high'], df['low'], df['close'])

    # ADX (CORRECTED: Wilder's RMA)
    df['adx'], df['plus_di'], df['minus_di'] = calculate_adx(df['high'], df['low'], df['close'])

    # Stochastic (CORRECTED: Slow instead of Fast)
    df['stoch_k'], df['stoch_d'] = calculate_stochastic(df['high'], df['low'], df['close'])

    # ROC (CORRECTED: Period 10 instead of 12)
    df['roc'] = calculate_roc(df['close'])

    # Bollinger Bands (CORRECTED: ddof=0)
    df['bollinger_upper'], df['bollinger_middle'], df['bollinger_lower'] = calculate_bollinger_bands(df['close'])
    df['bb_width'] = ((df['bollinger_upper'] - df['bollinger_lower']) / df['bollinger_middle'] * 100).replace([np.inf, -np.inf], np.nan)

    # Ichimoku (CORRECTED: 26-period forward shift for Senkou A/B)
    df['ichimoku_tenkan'], df['ichimoku_kijun'], df['ichimoku_senkou_a'], df['ichimoku_senkou_b'], df['ichimoku_chikou'] = calculate_ichimoku(df['high'], df['low'], df['close'])

    # Moving Averages (unchanged)
    df['sma_20'] = calculate_sma(df['close'], 20)
    df['sma_50'] = calculate_sma(df['close'], 50)
    df['sma_200'] = calculate_sma(df['close'], 200)
    df['ema_12'] = calculate_ema(df['close'], 12)
    df['ema_20'] = calculate_ema(df['close'], 20)
    df['ema_26'] = calculate_ema(df['close'], 26)
    df['ema_50'] = calculate_ema(df['close'], 50)
    df['ema_200'] = calculate_ema(df['close'], 200)

    # MACD (unchanged)
    df['macd'], df['macd_signal'], df['macd_histogram'] = calculate_macd(df['close'])

    # CCI
    df['cci'] = calculate_cci(df['high'], df['low'], df['close'])

    # Williams %R
    df['williams_r'] = calculate_williams_r(df['high'], df['low'], df['close'])

    # Momentum
    df['momentum'] = df['close'] - df['close'].shift(10)

    # OBV
    df['obv'] = calculate_obv(df['close'], df['volume'])

    # MFI
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

    # Awesome Oscillator
    df['awesome_osc'] = calculate_awesome_oscillator(df['high'], df['low'])

    # Additional derived indicators
    df['rsi_slope'] = df['rsi'].diff(5).replace([np.inf, -np.inf], np.nan)
    df['rsi_zscore'] = ((df['rsi'] - df['rsi'].rolling(window=20, min_periods=20).mean()) / df['rsi'].rolling(window=20, min_periods=20).std()).replace([np.inf, -np.inf], np.nan)
    df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
    df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
    df['macd_cross'] = (df['macd'] > df['macd_signal']).astype(int)
    df['ema20_slope'] = df['ema_20'].diff(5).replace([np.inf, -np.inf], np.nan)
    df['ema50_slope'] = df['ema_50'].diff(5).replace([np.inf, -np.inf], np.nan)
    df['atr_zscore'] = ((df['atr'] - df['atr'].rolling(window=20, min_periods=20).mean()) / df['atr'].rolling(window=20, min_periods=20).std()).replace([np.inf, -np.inf], np.nan)
    df['atr_slope'] = df['atr'].diff(5).replace([np.inf, -np.inf], np.nan)
    df['volume_zscore'] = ((df['volume'] - df['volume'].rolling(window=20, min_periods=20).mean()) / df['volume'].rolling(window=20, min_periods=20).std()).replace([np.inf, -np.inf], np.nan)
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

    return df


def process_table(table_name, symbol_column='symbol'):
    """Process a single table"""
    print(f"\n{'='*60}")
    print(f"Processing table: {table_name}")
    print(f"{'='*60}")

    # Get distinct symbols
    query = f"""
    SELECT DISTINCT {symbol_column} as symbol
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    ORDER BY {symbol_column}
    """
    symbols_df = client.query(query).to_dataframe()
    total_symbols = len(symbols_df)

    print(f"Found {total_symbols} symbols to process")

    success_count = 0
    error_count = 0
    total_rows = 0

    for idx, row in symbols_df.iterrows():
        symbol = row['symbol']
        print(f"\n[{idx+1}/{total_symbols}] Processing {symbol}...")

        try:
            # Fetch all data for symbol
            query = f"""
            SELECT *
            FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
            WHERE {symbol_column} = '{symbol}'
            ORDER BY datetime ASC
            """
            df = client.query(query).to_dataframe()

            if len(df) < 50:
                print(f"  Skipping {symbol}: Only {len(df)} rows (need at least 50)")
                continue

            print(f"  Fetched {len(df)} rows")

            # Recalculate indicators
            df = recalculate_all_indicators(df)

            # Delete existing data
            delete_query = f"""
            DELETE FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
            WHERE {symbol_column} = '{symbol}'
            """
            client.query(delete_query).result()

            # Ensure proper types
            if 'average_volume' in df.columns:
                df['average_volume'] = df['average_volume'].fillna(0).astype(int)
            if 'obv' in df.columns:
                df['obv'] = df['obv'].fillna(0).astype(int)

            # Replace inf with NaN
            for col in df.select_dtypes(include=[np.floating]).columns:
                df[col] = df[col].replace([np.inf, -np.inf], np.nan)

            # Upload
            table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
            job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
            job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()

            print(f"  Uploaded {len(df)} rows with corrected indicators")
            success_count += 1
            total_rows += len(df)

        except Exception as e:
            print(f"  ERROR processing {symbol}: {str(e)}")
            error_count += 1

        # Small delay to avoid rate limits
        time.sleep(0.5)

    return success_count, error_count, total_rows


def main():
    print("=" * 70)
    print("RECALCULATE INDICATORS - SALEEM'S CORRECTIONS")
    print("=" * 70)
    print()
    print("Corrections being applied:")
    print("  1. RSI: SMA -> Wilder's RMA (ewm alpha=1/period)")
    print("  2. ATR: SMA -> Wilder's RMA")
    print("  3. ADX/+DI/-DI: SMA -> Wilder's RMA")
    print("  4. Stochastic: Fast -> Slow (smooth %K)")
    print("  5. ROC: Period 12 -> 10")
    print("  6. Ichimoku: Add 26-period forward shift")
    print("  7. Bollinger Bands: ddof=1 -> ddof=0")
    print()

    start_time = time.time()

    # Process stocks_daily_clean
    stock_success, stock_errors, stock_rows = process_table('stocks_daily_clean', 'symbol')

    # Process crypto_daily_clean
    crypto_success, crypto_errors, crypto_rows = process_table('crypto_daily_clean', 'symbol')

    elapsed = time.time() - start_time

    print()
    print("=" * 70)
    print("RECALCULATION COMPLETE")
    print("=" * 70)
    print(f"Stocks: {stock_success} symbols, {stock_rows} rows ({stock_errors} errors)")
    print(f"Crypto: {crypto_success} symbols, {crypto_rows} rows ({crypto_errors} errors)")
    print(f"Total time: {elapsed/60:.1f} minutes")
    print()
    print("All indicators now match TradingView/Industry standards!")
    print("=" * 70)


if __name__ == "__main__":
    main()
