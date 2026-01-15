"""
Backfill Technical Indicators for Stock Historical Data
Calculates all technical indicators including Fibonacci and Elliott Wave for historical stock data
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timedelta
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'stock_analysis'


def calculate_fibonacci_levels(df):
    """Calculate Fibonacci retracement and extension levels"""

    # Find swing highs and lows for Fibonacci calculations
    window = 5

    # Swing highs: higher than surrounding periods
    df['swing_high'] = (
        (df['high'] == df['high'].rolling(window=window, center=True).max()) &
        (df['high'] > df['high'].shift(1)) &
        (df['high'] > df['high'].shift(-1))
    )

    # Swing lows: lower than surrounding periods
    df['swing_low'] = (
        (df['low'] == df['low'].rolling(window=window, center=True).min()) &
        (df['low'] < df['low'].shift(1)) &
        (df['low'] < df['low'].shift(-1))
    )

    # Get last significant swing high and low
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

        # Distance from current price to Fibonacci levels
        current_price = df['close'].iloc[-1]
        df['dist_to_fib_236'] = ((df['fib_236'] - current_price) / current_price) * 100
        df['dist_to_fib_382'] = ((df['fib_382'] - current_price) / current_price) * 100
        df['dist_to_fib_500'] = ((df['fib_500'] - current_price) / current_price) * 100
        df['dist_to_fib_618'] = ((df['fib_618'] - current_price) / current_price) * 100
    else:
        for col in ['fib_0', 'fib_236', 'fib_382', 'fib_500', 'fib_618', 'fib_786', 'fib_100',
                    'fib_ext_1272', 'fib_ext_1618', 'fib_ext_2618',
                    'dist_to_fib_236', 'dist_to_fib_382', 'dist_to_fib_500', 'dist_to_fib_618']:
            df[col] = None

    return df


def detect_elliott_wave_pattern(df):
    """Detect Elliott Wave patterns"""

    if len(df) < 13:
        for col in ['elliott_wave_degree', 'wave_position', 'impulse_wave_count',
                    'corrective_wave_count', 'wave_1_high', 'wave_2_low', 'wave_3_high',
                    'wave_4_low', 'wave_5_high', 'trend_direction', 'local_maxima', 'local_minima']:
            df[col] = None
        return df

    # Identify local extrema using rolling windows (simpler approach without scipy)
    window = 3
    df['local_maxima'] = None
    df['local_minima'] = None

    for i in range(window, len(df) - window):
        # Local maxima: higher than neighbors
        if all(df['high'].iloc[i] >= df['high'].iloc[i-j] for j in range(1, window+1)) and \
           all(df['high'].iloc[i] >= df['high'].iloc[i+j] for j in range(1, window+1)):
            df.loc[df.index[i], 'local_maxima'] = df['high'].iloc[i]

        # Local minima: lower than neighbors
        if all(df['low'].iloc[i] <= df['low'].iloc[i-j] for j in range(1, window+1)) and \
           all(df['low'].iloc[i] <= df['low'].iloc[i+j] for j in range(1, window+1)):
            df.loc[df.index[i], 'local_minima'] = df['low'].iloc[i]

    # Calculate trend direction
    sma_short = df['close'].rolling(window=10).mean()
    sma_long = df['close'].rolling(window=50).mean()
    df['trend_direction'] = np.where(sma_short > sma_long, 'UP', 'DOWN')

    # Simple wave counting (this is a simplified version)
    peaks = df[df['local_maxima'].notna()].index.tolist()
    troughs = df[df['local_minima'].notna()].index.tolist()

    if len(peaks) >= 3 and len(troughs) >= 2:
        # Basic 5-wave impulse pattern detection
        df['impulse_wave_count'] = min(len(peaks), 5)
        df['corrective_wave_count'] = min(len(troughs), 3)

        # Mark wave levels (last 5 peaks and 4 troughs)
        if len(peaks) >= 1:
            df['wave_1_high'] = df.loc[peaks[-1], 'high'] if len(peaks) >= 1 else None
        if len(troughs) >= 1:
            df['wave_2_low'] = df.loc[troughs[-1], 'low'] if len(troughs) >= 1 else None
        if len(peaks) >= 2:
            df['wave_3_high'] = df.loc[peaks[-2], 'high'] if len(peaks) >= 2 else None
        if len(troughs) >= 2:
            df['wave_4_low'] = df.loc[troughs[-2], 'low'] if len(troughs) >= 2 else None
        if len(peaks) >= 3:
            df['wave_5_high'] = df.loc[peaks[-3], 'high'] if len(peaks) >= 3 else None

        # Elliott Wave degree (simplified)
        price_range = df['high'].max() - df['low'].min()
        if price_range > df['close'].iloc[-1] * 0.5:
            df['elliott_wave_degree'] = 'PRIMARY'
        elif price_range > df['close'].iloc[-1] * 0.2:
            df['elliott_wave_degree'] = 'INTERMEDIATE'
        else:
            df['elliott_wave_degree'] = 'MINOR'

        # Current wave position (as integer 1-5)
        wave_pos = (df['impulse_wave_count'].iloc[-1] % 5) + 1
        df['wave_position'] = int(wave_pos) if pd.notna(wave_pos) else None
    else:
        for col in ['elliott_wave_degree', 'wave_position', 'impulse_wave_count',
                    'corrective_wave_count', 'wave_1_high', 'wave_2_low', 'wave_3_high',
                    'wave_4_low', 'wave_5_high']:
            df[col] = None

    return df


def calculate_technical_indicators(df):
    """Calculate all technical indicators"""

    if len(df) < 200:
        logger.warning(f"Not enough data points ({len(df)}), need at least 200")
        return df

    df = df.sort_values('datetime').reset_index(drop=True)

    # Moving Averages
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean()
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

    # RSI - Using Wilder's RMA (ewm alpha=1/period) - Industry Standard / TradingView
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # Momentum
    df['momentum'] = df['close'] - df['close'].shift(10)

    # ROC - Period 10 (TradingView default, changed from 12)
    df['roc'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100

    # Bollinger Bands - Using ddof=0 (population std dev) - TradingView Standard
    df['bb_middle'] = df['sma_20']
    std_20 = df['close'].rolling(window=20).std(ddof=0)  # Population std dev
    df['bb_upper'] = df['bb_middle'] + (std_20 * 2)
    df['bb_lower'] = df['bb_middle'] - (std_20 * 2)
    df['bb_width'] = df['bb_upper'] - df['bb_lower']

    # ATR - Using Wilder's RMA (ewm alpha=1/period) - Industry Standard / TradingView
    tr1 = df['high'] - df['low']
    tr2 = abs(df['high'] - df['close'].shift())
    tr3 = abs(df['low'] - df['close'].shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr'] = tr.ewm(alpha=1/14, adjust=False, min_periods=14).mean()

    # ADX and Directional Indicators - Using Wilder's RMA
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

    plus_dm_smooth = plus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    minus_dm_smooth = minus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    df['plus_di'] = 100 * plus_dm_smooth / df['atr']
    df['minus_di'] = 100 * minus_dm_smooth / df['atr']
    dx = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
    df['adx'] = dx.ewm(alpha=1/14, adjust=False, min_periods=14).mean()

    # CCI
    tp = (df['high'] + df['low'] + df['close']) / 3
    df['cci'] = (tp - tp.rolling(window=20).mean()) / (0.015 * tp.rolling(window=20).std())

    # Williams %R
    high_14 = df['high'].rolling(window=14).max()
    low_14 = df['low'].rolling(window=14).min()
    df['williams_r'] = -100 * ((high_14 - df['close']) / (high_14 - low_14))

    # Stochastic - Slow Stochastic (TradingView default) - %K smoothed with SMA(3)
    raw_k = 100 * ((df['close'] - low_14) / (high_14 - low_14))
    df['stoch_k'] = raw_k.rolling(window=3, min_periods=3).mean()  # Smooth %K
    df['stoch_d'] = df['stoch_k'].rolling(window=3, min_periods=3).mean()  # %D is SMA of smoothed %K

    # OBV
    df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()

    # PVO
    vol_ema12 = df['volume'].ewm(span=12, adjust=False).mean()
    vol_ema26 = df['volume'].ewm(span=26, adjust=False).mean()
    df['pvo'] = ((vol_ema12 - vol_ema26) / vol_ema26) * 100
    df['pvo_signal'] = df['pvo'].ewm(span=9, adjust=False).mean()

    # KAMA
    change = abs(df['close'] - df['close'].shift(10))
    volatility = df['close'].diff().abs().rolling(window=10).sum()
    er = change / volatility
    fast_sc = 2 / (2 + 1)
    slow_sc = 2 / (30 + 1)
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2

    df['kama'] = 0.0
    df.loc[df.index[10], 'kama'] = df.loc[df.index[10], 'close']
    for i in range(11, len(df)):
        df.loc[df.index[i], 'kama'] = df.loc[df.index[i-1], 'kama'] + sc.iloc[i] * (df.loc[df.index[i], 'close'] - df.loc[df.index[i-1], 'kama'])

    # TRIX
    ema1 = df['close'].ewm(span=15, adjust=False).mean()
    ema2 = ema1.ewm(span=15, adjust=False).mean()
    ema3 = ema2.ewm(span=15, adjust=False).mean()
    df['trix'] = (ema3.diff() / ema3) * 100

    # PPO
    df['ppo'] = ((df['ema_12'] - df['ema_26']) / df['ema_26']) * 100
    df['ppo_signal'] = df['ppo'].ewm(span=9, adjust=False).mean()

    # Ultimate Oscillator
    bp = df['close'] - pd.concat([df['low'], df['close'].shift()], axis=1).min(axis=1)
    tr_uo = pd.concat([df['high'] - df['low'],
                       abs(df['high'] - df['close'].shift()),
                       abs(df['low'] - df['close'].shift())], axis=1).max(axis=1)

    avg7 = bp.rolling(window=7).sum() / tr_uo.rolling(window=7).sum()
    avg14 = bp.rolling(window=14).sum() / tr_uo.rolling(window=14).sum()
    avg28 = bp.rolling(window=28).sum() / tr_uo.rolling(window=28).sum()
    df['ultimate_oscillator'] = 100 * ((4 * avg7) + (2 * avg14) + avg28) / 7

    # Awesome Oscillator
    median_price = (df['high'] + df['low']) / 2
    df['awesome_oscillator'] = median_price.rolling(window=5).mean() - median_price.rolling(window=34).mean()

    # Trend Strength
    df['trend_strength'] = abs(df['adx'])

    # Volatility Regime
    df['volatility_regime'] = np.where(df['atr'] > df['atr'].rolling(window=20).mean(), 'HIGH', 'LOW')

    # Price Changes
    df['price_change_1d'] = df['close'].pct_change(1) * 100
    df['price_change_5d'] = df['close'].pct_change(5) * 100
    df['price_change_20d'] = df['close'].pct_change(20) * 100

    # Fibonacci levels
    df = calculate_fibonacci_levels(df)

    # Elliott Wave
    df = detect_elliott_wave_pattern(df)

    df = df.replace({np.nan: None, np.inf: None, -np.inf: None})

    return df


def backfill_stock_indicators(client, symbol):
    """Backfill indicators for a specific stock symbol"""

    logger.info(f"Processing {symbol}...")

    try:
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE symbol = '{symbol}'
        ORDER BY datetime ASC
        """

        df = client.query(query).to_dataframe()

        if len(df) == 0:
            logger.warning(f"No data found for {symbol}")
            return 0

        logger.info(f"  Found {len(df)} records from {df['datetime'].min()} to {df['datetime'].max()}")

        df = calculate_technical_indicators(df)

        # Update in batches
        batch_size = 100
        updated_count = 0

        # Prepare columns for update
        indicator_cols = ['sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'ema_50', 'rsi',
                         'macd', 'macd_signal', 'macd_hist', 'momentum', 'roc', 'bb_upper',
                         'bb_middle', 'bb_lower', 'bb_width', 'atr', 'adx', 'plus_di', 'minus_di',
                         'cci', 'williams_r', 'stoch_k', 'stoch_d', 'obv', 'pvo', 'pvo_signal',
                         'kama', 'trix', 'ppo', 'ppo_signal', 'ultimate_oscillator', 'awesome_oscillator',
                         'fib_0', 'fib_236', 'fib_382', 'fib_500', 'fib_618', 'fib_786', 'fib_100',
                         'fib_ext_1272', 'fib_ext_1618', 'fib_ext_2618', 'dist_to_fib_236',
                         'dist_to_fib_382', 'dist_to_fib_500', 'dist_to_fib_618',
                         'elliott_wave_degree', 'wave_position', 'impulse_wave_count',
                         'corrective_wave_count', 'wave_1_high', 'wave_2_low', 'wave_3_high',
                         'wave_4_low', 'wave_5_high', 'trend_direction', 'swing_high', 'swing_low',
                         'local_maxima', 'local_minima', 'trend_strength', 'volatility_regime',
                         'price_change_1d', 'price_change_5d', 'price_change_20d']

        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]

            for idx, row in batch_df.iterrows():
                set_clauses = []
                for col in indicator_cols:
                    if col in row:
                        val = row[col]
                        # Check for None, NaN, or inf
                        if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
                            set_clauses.append(f"{col} = NULL")
                        elif isinstance(val, bool):
                            set_clauses.append(f"{col} = {str(val).upper()}")
                        elif isinstance(val, (int, float)):
                            set_clauses.append(f"{col} = {val}")
                        else:
                            set_clauses.append(f"{col} = '{val}'")
                    else:
                        set_clauses.append(f"{col} = NULL")

                update_query = f"""
                UPDATE `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
                SET {', '.join(set_clauses)}
                WHERE symbol = '{symbol}'
                  AND datetime = TIMESTAMP('{row['datetime']}')
                """

                try:
                    client.query(update_query).result()
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Error updating {symbol} at {row['datetime']}: {str(e)}")

            logger.info(f"  Updated {updated_count}/{len(df)} records...")
            time.sleep(0.3)

        logger.info(f"✓ Completed {symbol}: {updated_count} records updated")
        return updated_count

    except Exception as e:
        logger.error(f"✗ Error processing {symbol}: {str(e)}")
        return 0


def main():
    """Main execution"""

    print("=" * 70)
    print("STOCK INDICATORS BACKFILL SCRIPT")
    print("=" * 70)
    print()

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
    SELECT DISTINCT symbol
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    ORDER BY symbol
    """

    symbols_df = client.query(query).to_dataframe()
    total_symbols = len(symbols_df)

    print(f"Found {total_symbols} unique stock symbols to process")
    print()

    total_updated = 0
    start_time = time.time()

    for idx, row in symbols_df.iterrows():
        symbol = row['symbol']
        print(f"\n[{idx+1}/{total_symbols}] Processing {symbol}...")

        updated = backfill_stock_indicators(client, symbol)
        total_updated += updated

        elapsed = time.time() - start_time
        avg_time = elapsed / (idx + 1)
        remaining = (total_symbols - idx - 1) * avg_time

        print(f"Progress: {idx+1}/{total_symbols} symbols | "
              f"Updated: {total_updated} records | "
              f"ETA: {remaining/60:.1f} minutes")

    print()
    print("=" * 70)
    print("BACKFILL COMPLETE")
    print(f"Total symbols processed: {total_symbols}")
    print(f"Total records updated: {total_updated}")
    print(f"Total time: {(time.time() - start_time)/60:.1f} minutes")
    print("=" * 70)


if __name__ == "__main__":
    main()
