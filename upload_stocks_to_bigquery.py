"""
Upload Historical Stock Data to BigQuery
Reads stock_6month_ohlc_data.csv, calculates technical indicators, and uploads to BigQuery
"""

from google.cloud import bigquery
import pandas as pd
import numpy as np
import logging
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'stock_analysis'
CSV_FILE = 'stock_6month_ohlc_data.csv'


def calculate_technical_indicators(df):
    """Calculate all 81 technical indicators - same as crypto function"""

    # Ensure we have enough data
    if len(df) < 200:
        logger.warning(f"Insufficient data for full indicator calculation: {len(df)} rows")
        return df

    # Sort by date
    df = df.sort_values('datetime')

    # Moving Averages
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean()

    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']

    # ATR (Average True Range)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(window=14).mean()

    # ADX (Average Directional Index)
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr14 = true_range.rolling(window=14).sum()
    df['plus_di'] = 100 * (plus_dm.rolling(window=14).sum() / tr14)
    df['minus_di'] = 100 * (minus_dm.rolling(window=14).sum() / tr14)

    dx = 100 * np.abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
    df['adx'] = dx.rolling(window=14).mean()

    # Momentum
    df['momentum'] = df['close'] - df['close'].shift(10)
    df['roc'] = ((df['close'] - df['close'].shift(12)) / df['close'].shift(12)) * 100

    # CCI (Commodity Channel Index)
    tp = (df['high'] + df['low'] + df['close']) / 3
    df['cci'] = (tp - tp.rolling(window=20).mean()) / (0.015 * tp.rolling(window=20).std())

    # Williams %R
    hh = df['high'].rolling(window=14).max()
    ll = df['low'].rolling(window=14).min()
    df['williams_r'] = -100 * ((hh - df['close']) / (hh - ll))

    # Stochastic Oscillator
    df['stoch_k'] = 100 * ((df['close'] - ll) / (hh - ll))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # OBV (On-Balance Volume)
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['obv'] = obv

    # PVO (Percentage Volume Oscillator)
    vol_ema_12 = df['volume'].ewm(span=12, adjust=False).mean()
    vol_ema_26 = df['volume'].ewm(span=26, adjust=False).mean()
    df['pvo'] = ((vol_ema_12 - vol_ema_26) / vol_ema_26) * 100
    df['pvo_signal'] = df['pvo'].ewm(span=9, adjust=False).mean()

    # KAMA (Kaufman Adaptive Moving Average)
    change = np.abs(df['close'] - df['close'].shift(10))
    volatility = np.abs(df['close'].diff()).rolling(window=10).sum()
    er = change / volatility
    fast_sc = 2 / (2 + 1)
    slow_sc = 2 / (30 + 1)
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
    df['kama'] = df['close'].ewm(alpha=sc, adjust=False).mean()

    # TRIX
    ema1 = df['close'].ewm(span=15, adjust=False).mean()
    ema2 = ema1.ewm(span=15, adjust=False).mean()
    ema3 = ema2.ewm(span=15, adjust=False).mean()
    df['trix'] = 100 * (ema3.diff() / ema3.shift())

    # PPO (Percentage Price Oscillator)
    df['ppo'] = ((df['ema_12'] - df['ema_26']) / df['ema_26']) * 100
    df['ppo_signal'] = df['ppo'].ewm(span=9, adjust=False).mean()

    # Ultimate Oscillator
    bp = df['close'] - pd.concat([df['low'], df['close'].shift()], axis=1).min(axis=1)
    avg7 = bp.rolling(window=7).sum() / true_range.rolling(window=7).sum()
    avg14 = bp.rolling(window=14).sum() / true_range.rolling(window=14).sum()
    avg28 = bp.rolling(window=28).sum() / true_range.rolling(window=28).sum()
    df['ultimate_oscillator'] = 100 * ((4 * avg7 + 2 * avg14 + avg28) / 7)

    # Awesome Oscillator
    median_price = (df['high'] + df['low']) / 2
    df['awesome_oscillator'] = median_price.rolling(window=5).mean() - median_price.rolling(window=34).mean()

    # Call Fibonacci and Elliott Wave functions
    df = calculate_fibonacci_levels(df)
    df = detect_elliott_wave_pattern(df)

    return df


def calculate_fibonacci_levels(df):
    """Calculate Fibonacci retracement and extension levels"""

    window = 5

    # Detect swing highs and lows
    df['swing_high'] = (
        (df['high'] == df['high'].rolling(window=window, center=True).max()) &
        (df['high'] > df['high'].shift(1)) &
        (df['high'] > df['high'].shift(-1))
    )

    df['swing_low'] = (
        (df['low'] == df['low'].rolling(window=window, center=True).min()) &
        (df['low'] < df['low'].shift(1)) &
        (df['low'] < df['low'].shift(-1))
    )

    # Get recent swing points
    recent_swing_highs = df[df['swing_high'] == True].tail(2)
    recent_swing_lows = df[df['swing_low'] == True].tail(2)

    if len(recent_swing_highs) >= 1 and len(recent_swing_lows) >= 1:
        swing_high = recent_swing_highs.iloc[-1]['high']
        swing_low = recent_swing_lows.iloc[-1]['low']
        diff = swing_high - swing_low

        # Fibonacci Retracement Levels
        df['fib_0'] = swing_low
        df['fib_236'] = swing_low + (diff * 0.236)
        df['fib_382'] = swing_low + (diff * 0.382)
        df['fib_500'] = swing_low + (diff * 0.500)
        df['fib_618'] = swing_low + (diff * 0.618)
        df['fib_786'] = swing_low + (diff * 0.786)
        df['fib_100'] = swing_high

        # Fibonacci Extension Levels
        df['fib_ext_1272'] = swing_low + (diff * 1.272)
        df['fib_ext_1618'] = swing_low + (diff * 1.618)
        df['fib_ext_2618'] = swing_low + (diff * 2.618)

        # Distance to key levels (as percentage)
        df['dist_to_fib_236'] = ((df['close'] - df['fib_236']) / df['close']) * 100
        df['dist_to_fib_382'] = ((df['close'] - df['fib_382']) / df['close']) * 100
        df['dist_to_fib_500'] = ((df['close'] - df['fib_500']) / df['close']) * 100
        df['dist_to_fib_618'] = ((df['close'] - df['fib_618']) / df['close']) * 100

    return df


def detect_elliott_wave_pattern(df):
    """Detect Elliott Wave patterns"""

    if len(df) < 13:
        return df

    # Detect local maxima and minima
    df['local_maxima'] = (
        (df['high'] > df['high'].shift(1)) &
        (df['high'] > df['high'].shift(-1))
    )
    df['local_minima'] = (
        (df['low'] < df['low'].shift(1)) &
        (df['low'] < df['low'].shift(-1))
    )

    # Trend direction
    sma_20 = df['close'].rolling(window=20).mean()
    sma_50 = df['close'].rolling(window=50).mean()

    trend_direction = []
    for idx in range(len(df)):
        if idx < 50:
            trend_direction.append(0)
        elif sma_20.iloc[idx] > sma_50.iloc[idx] and df['close'].iloc[idx] > sma_20.iloc[idx]:
            trend_direction.append(1)  # Uptrend
        elif sma_20.iloc[idx] < sma_50.iloc[idx] and df['close'].iloc[idx] < sma_20.iloc[idx]:
            trend_direction.append(-1)  # Downtrend
        else:
            trend_direction.append(0)  # Sideways

    df['trend_direction'] = trend_direction

    # Trend strength
    df['trend_strength'] = np.abs(df['adx'])

    # Volatility regime
    atr_mean = df['atr'].rolling(window=20).mean()
    volatility_regime = []
    for idx in range(len(df)):
        if pd.isna(df['atr'].iloc[idx]) or pd.isna(atr_mean.iloc[idx]):
            volatility_regime.append('normal')
        elif df['atr'].iloc[idx] > atr_mean.iloc[idx] * 1.5:
            volatility_regime.append('high')
        elif df['atr'].iloc[idx] < atr_mean.iloc[idx] * 0.5:
            volatility_regime.append('low')
        else:
            volatility_regime.append('normal')

    df['volatility_regime'] = volatility_regime

    # Price changes
    df['price_change_1d'] = ((df['close'] - df['close'].shift(1)) / df['close'].shift(1)) * 100
    df['price_change_5d'] = ((df['close'] - df['close'].shift(5)) / df['close'].shift(5)) * 100
    df['price_change_20d'] = ((df['close'] - df['close'].shift(20)) / df['close'].shift(20)) * 100

    # Wave detection (simplified)
    recent_maxima = df[df['local_maxima'] == True].tail(5)
    recent_minima = df[df['local_minima'] == True].tail(5)

    if len(recent_maxima) >= 3 and len(recent_minima) >= 2:
        # Identify wave positions
        df['impulse_wave_count'] = len(recent_maxima)
        df['corrective_wave_count'] = len(recent_minima)

        # Determine wave position (1-5)
        wave_position = min(5, len(recent_maxima))
        df['wave_position'] = wave_position

        # Classify wave degree based on price movement
        price_range = df['close'].max() - df['close'].min()
        price_pct = (price_range / df['close'].mean()) * 100

        if price_pct > 50:
            df['elliott_wave_degree'] = 'Primary'
        elif price_pct > 20:
            df['elliott_wave_degree'] = 'Intermediate'
        elif price_pct > 10:
            df['elliott_wave_degree'] = 'Minor'
        else:
            df['elliott_wave_degree'] = 'Minute'

        # Record wave peaks
        if len(recent_maxima) >= 3:
            df['wave_1_high'] = recent_maxima.iloc[-3]['high']
            df['wave_3_high'] = recent_maxima.iloc[-2]['high']
            df['wave_5_high'] = recent_maxima.iloc[-1]['high']

        if len(recent_minima) >= 2:
            df['wave_2_low'] = recent_minima.iloc[-2]['low']
            df['wave_4_low'] = recent_minima.iloc[-1]['low']

    return df


def upload_to_bigquery():
    """Upload stock data with technical indicators to BigQuery"""

    logger.info("=" * 70)
    logger.info("UPLOADING HISTORICAL STOCK DATA TO BIGQUERY")
    logger.info("=" * 70)

    # Read CSV file
    logger.info(f"\nReading {CSV_FILE}...")
    df = pd.read_csv(CSV_FILE)
    logger.info(f"✓ Loaded {len(df)} rows for {df['symbol'].nunique()} symbols")

    # Convert datetime
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['date'] = pd.to_datetime(df['date'])

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    # Process each symbol separately
    all_symbols = df['symbol'].unique()
    total_uploaded = 0
    failed_symbols = []

    for idx, symbol in enumerate(all_symbols, 1):
        try:
            print(f"[{idx}/{len(all_symbols)}] Processing {symbol}...", end=' ', flush=True)

            # Get symbol data
            symbol_df = df[df['symbol'] == symbol].copy()
            symbol_df = symbol_df.sort_values('datetime')

            # Calculate technical indicators
            symbol_df = calculate_technical_indicators(symbol_df)

            # Replace inf and NaN with None
            symbol_df = symbol_df.replace([np.inf, -np.inf], np.nan)
            symbol_df = symbol_df.where(pd.notnull(symbol_df), None)

            # Upload to BigQuery
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
            )

            job = client.load_table_from_dataframe(
                symbol_df, table_ref, job_config=job_config
            )
            job.result()

            total_uploaded += len(symbol_df)
            print(f"✓ Uploaded {len(symbol_df)} rows")

        except Exception as e:
            logger.error(f"✗ ERROR: {str(e)}")
            failed_symbols.append(symbol)

    logger.info("\n" + "=" * 70)
    logger.info("UPLOAD COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Total rows uploaded: {total_uploaded}")
    logger.info(f"Successful symbols: {len(all_symbols) - len(failed_symbols)}/{len(all_symbols)}")

    if failed_symbols:
        logger.error(f"Failed symbols: {', '.join(failed_symbols)}")

    logger.info("=" * 70)


if __name__ == "__main__":
    upload_to_bigquery()
