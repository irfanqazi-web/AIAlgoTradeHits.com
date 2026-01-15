"""
Kraken Pro Daily Data Fetcher with Technical Indicators
Fetches daily OHLC data and calculates comprehensive technical indicators
"""

import functions_framework
import krakenex
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
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'daily_crypto'

def calculate_fibonacci_levels(df):
    """Calculate Fibonacci retracement and extension levels"""

    # Find swing highs and lows for Fibonacci calculations
    # Use a 5-period window for swing detection
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

        # Fibonacci Retracement Levels (from swing low to swing high)
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

        # Distance from current price to Fibonacci levels (as percentage)
        current_price = df['close'].iloc[-1]
        df['dist_to_fib_236'] = ((df['fib_236'] - current_price) / current_price) * 100
        df['dist_to_fib_382'] = ((df['fib_382'] - current_price) / current_price) * 100
        df['dist_to_fib_500'] = ((df['fib_500'] - current_price) / current_price) * 100
        df['dist_to_fib_618'] = ((df['fib_618'] - current_price) / current_price) * 100
    else:
        # Default values if not enough swing points
        for col in ['fib_0', 'fib_236', 'fib_382', 'fib_500', 'fib_618', 'fib_786', 'fib_100',
                    'fib_ext_1272', 'fib_ext_1618', 'fib_ext_2618',
                    'dist_to_fib_236', 'dist_to_fib_382', 'dist_to_fib_500', 'dist_to_fib_618']:
            df[col] = None

    return df


def detect_elliott_wave_pattern(df):
    """Detect Elliott Wave patterns and key metrics"""

    # Elliott Wave requires at least 13 periods for basic 5-wave + 3-wave pattern
    if len(df) < 13:
        for col in ['elliott_wave_degree', 'wave_position', 'impulse_wave_count',
                    'corrective_wave_count', 'wave_1_high', 'wave_2_low', 'wave_3_high',
                    'wave_4_low', 'wave_5_high', 'trend_direction']:
            df[col] = None
        return df

    # Identify peaks and troughs for wave counting
    # Using a more sophisticated approach with multiple timeframes

    # Calculate price momentum and trend
    df['price_change'] = df['close'].diff()
    df['momentum'] = df['close'].diff(5)  # 5-period momentum

    # Identify trend direction (1: up, -1: down, 0: sideways)
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

    # Find local maxima and minima for wave identification
    window = 5
    df['local_max'] = df['high'] == df['high'].rolling(window=window, center=True).max()
    df['local_min'] = df['low'] == df['low'].rolling(window=window, center=True).min()

    # Get recent wave points
    recent_maxima = df[df['local_max'] == True].tail(5)
    recent_minima = df[df['local_min'] == True].tail(5)

    # Simple Elliott Wave detection
    # Looking for 5-wave impulse pattern
    if len(recent_maxima) >= 3 and len(recent_minima) >= 2:
        # Extract wave points
        waves = []
        for i in range(min(3, len(recent_maxima))):
            waves.append(('high', recent_maxima.iloc[i]['high'], recent_maxima.index[i]))
        for i in range(min(2, len(recent_minima))):
            waves.append(('low', recent_minima.iloc[i]['low'], recent_minima.index[i]))

        # Sort by index
        waves.sort(key=lambda x: x[2])

        # Check for impulse wave characteristics
        # Wave 3 should not be the shortest
        # Wave 2 should not retrace more than 100% of wave 1
        # Wave 4 should not overlap with wave 1

        impulse_count = 0
        corrective_count = 0

        if len(waves) >= 5:
            # Simplified wave counting
            for i in range(len(waves) - 1):
                if waves[i][0] != waves[i+1][0]:  # Alternating high/low
                    if waves[i][0] == 'low' and waves[i+1][0] == 'high':
                        impulse_count += 1
                    else:
                        corrective_count += 1

        df['impulse_wave_count'] = impulse_count
        df['corrective_wave_count'] = corrective_count

        # Estimate current wave position (1-5 for impulse, A-C for correction)
        total_waves = impulse_count + corrective_count
        if total_waves > 0:
            position = min(5, (impulse_count % 5) + 1) if impulse_count > 0 else 0
            df['wave_position'] = position
        else:
            df['wave_position'] = 0

        # Wave degree classification (Minute, Minor, Intermediate, Primary, Cycle)
        # Based on duration and price movement
        price_range = df['high'].max() - df['low'].min()
        duration = len(df)

        if duration >= 200 and price_range > df['close'].iloc[-1] * 0.3:
            df['elliott_wave_degree'] = 'Primary'
        elif duration >= 100 and price_range > df['close'].iloc[-1] * 0.2:
            df['elliott_wave_degree'] = 'Intermediate'
        elif duration >= 50:
            df['elliott_wave_degree'] = 'Minor'
        else:
            df['elliott_wave_degree'] = 'Minute'

        # Record wave peaks
        if len(recent_maxima) >= 3 and len(recent_minima) >= 2:
            df['wave_1_high'] = recent_maxima.iloc[-3]['high'] if len(recent_maxima) >= 3 else None
            df['wave_2_low'] = recent_minima.iloc[-2]['low'] if len(recent_minima) >= 2 else None
            df['wave_3_high'] = recent_maxima.iloc[-2]['high'] if len(recent_maxima) >= 2 else None
            df['wave_4_low'] = recent_minima.iloc[-1]['low'] if len(recent_minima) >= 1 else None
            df['wave_5_high'] = recent_maxima.iloc[-1]['high'] if len(recent_maxima) >= 1 else None
        else:
            for col in ['wave_1_high', 'wave_2_low', 'wave_3_high', 'wave_4_low', 'wave_5_high']:
                df[col] = None
    else:
        for col in ['elliott_wave_degree', 'wave_position', 'impulse_wave_count',
                    'corrective_wave_count', 'wave_1_high', 'wave_2_low', 'wave_3_high',
                    'wave_4_low', 'wave_5_high']:
            df[col] = None

    return df


def calculate_technical_indicators(df):
    """Calculate all technical indicators for a dataframe"""

    if len(df) < 200:  # Need enough data for SMA_200
        logger.warning(f"Not enough data for full indicator calculation: {len(df)} rows")
        # Still calculate what we can

    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)

    # Basic fields
    df['symbol'] = df['pair']
    df['open_price'] = df['open']
    df['hi_lo'] = df['high'] - df['low']
    df['pct_hi_lo_over_lo'] = ((df['high'] - df['low']) / df['low']) * 100

    # RSI (14 periods)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # Bollinger Bands
    df['sma_20'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['sma_20'] + (bb_std * 2)
    df['bb_lower'] = df['sma_20'] - (bb_std * 2)
    df['bb_percent'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

    # EMAs
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

    # SMAs
    df['ma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean()

    # Stochastic Oscillator
    low_14 = df['low'].rolling(window=14).min()
    high_14 = df['high'].rolling(window=14).max()
    df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # Williams %R
    df['williams_r'] = -100 * ((high_14 - df['close']) / (high_14 - low_14))

    # ADX (Average Directional Index) - simplified
    high_diff = df['high'].diff()
    low_diff = -df['low'].diff()

    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

    tr1 = df['high'] - df['low']
    tr2 = abs(df['high'] - df['close'].shift())
    tr3 = abs(df['low'] - df['close'].shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr14 = tr.rolling(window=14).mean()
    df['atr'] = atr14

    plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr14)
    minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr14)

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    df['adx'] = dx.rolling(window=14).mean()

    # CCI (Commodity Channel Index)
    tp = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = tp.rolling(window=20).mean()
    mad = tp.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
    df['cci'] = (tp - sma_tp) / (0.015 * mad)

    # ROC (Rate of Change)
    df['roc'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100

    # Momentum
    df['momentum'] = df['close'] - df['close'].shift(10)

    # TRIX (Triple Exponential Average)
    ema1 = df['close'].ewm(span=15, adjust=False).mean()
    ema2 = ema1.ewm(span=15, adjust=False).mean()
    ema3 = ema2.ewm(span=15, adjust=False).mean()
    df['trix'] = ((ema3 - ema3.shift()) / ema3.shift()) * 100

    # Ultimate Oscillator (simplified)
    bp = df['close'] - pd.concat([df['low'], df['close'].shift()], axis=1).min(axis=1)
    tr_uo = pd.concat([df['high'], df['close'].shift()], axis=1).max(axis=1) - pd.concat([df['low'], df['close'].shift()], axis=1).min(axis=1)

    avg7 = bp.rolling(window=7).sum() / tr_uo.rolling(window=7).sum()
    avg14 = bp.rolling(window=14).sum() / tr_uo.rolling(window=14).sum()
    avg28 = bp.rolling(window=28).sum() / tr_uo.rolling(window=28).sum()

    df['ultimate_oscillator'] = 100 * ((4 * avg7) + (2 * avg14) + avg28) / 7

    # KAMA (Kaufman's Adaptive Moving Average)
    change = abs(df['close'] - df['close'].shift(10))
    volatility = (abs(df['close'] - df['close'].shift())).rolling(window=10).sum()
    er = change / volatility  # Efficiency Ratio

    fastest = 2 / (2 + 1)
    slowest = 2 / (30 + 1)
    sc = (er * (fastest - slowest) + slowest) ** 2

    kama = pd.Series(index=df.index, dtype=float)
    kama.iloc[0] = df['close'].iloc[0]
    for i in range(1, len(df)):
        kama.iloc[i] = kama.iloc[i-1] + sc.iloc[i] * (df['close'].iloc[i] - kama.iloc[i-1])
    df['kama'] = kama

    # PPO (Percentage Price Oscillator)
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['ppo'] = ((ema12 - ema26) / ema26) * 100

    # PVO (Percentage Volume Oscillator)
    vol_ema12 = df['volume'].ewm(span=12, adjust=False).mean()
    vol_ema26 = df['volume'].ewm(span=26, adjust=False).mean()
    df['pvo'] = ((vol_ema12 - vol_ema26) / vol_ema26) * 100

    # Awesome Oscillator
    median_price = (df['high'] + df['low']) / 2
    ao_fast = median_price.rolling(window=5).mean()
    ao_slow = median_price.rolling(window=34).mean()
    df['awesome_oscillator'] = ao_fast - ao_slow

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

    # Calculate Fibonacci levels
    df = calculate_fibonacci_levels(df)

    # Detect Elliott Wave patterns
    df = detect_elliott_wave_pattern(df)

    return df


def fetch_daily_data():
    """Fetch daily OHLC data for all USD trading pairs from Kraken"""

    kraken = krakenex.API()

    logger.info("Fetching all tradable asset pairs from Kraken...")
    pairs_response = kraken.query_public('AssetPairs')

    if pairs_response['error']:
        logger.error(f"Error fetching pairs: {pairs_response['error']}")
        return None

    all_pairs = pairs_response['result']
    usd_pairs = {k: v for k, v in all_pairs.items() if 'USD' in k and v.get('status') == 'online'}

    logger.info(f"Found {len(usd_pairs)} USD trading pairs")

    # Fetch 250 days to ensure we have enough for SMA_200
    days_ago = datetime.now() - timedelta(days=250)
    since_timestamp = int(days_ago.timestamp())

    all_processed_data = []
    failed_pairs = []
    successful_pairs = 0

    for idx, (pair, info) in enumerate(usd_pairs.items(), 1):
        try:
            if idx % 50 == 0:
                logger.info(f"Progress: {idx}/{len(usd_pairs)} pairs")

            # Fetch OHLC data
            ohlc_response = kraken.query_public('OHLC', {
                'pair': pair,
                'interval': 1440,  # Daily candles
                'since': since_timestamp
            })

            if ohlc_response['error']:
                logger.warning(f"Error fetching {pair}: {ohlc_response['error']}")
                failed_pairs.append({'pair': pair, 'error': str(ohlc_response['error'])})
                continue

            # Parse OHLC data
            ohlc_list = list(ohlc_response['result'].values())[0]

            if len(ohlc_list) < 50:  # Need minimum data for indicators
                logger.warning(f"Not enough data for {pair}: {len(ohlc_list)} candles")
                continue

            # Create dataframe for this pair
            df_pair = pd.DataFrame(ohlc_list, columns=['timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
            df_pair['pair'] = pair
            df_pair['altname'] = info.get('altname', pair)
            df_pair['base'] = info.get('base', '')
            df_pair['quote'] = info.get('quote', '')

            # Convert types
            for col in ['open', 'high', 'low', 'close', 'vwap', 'volume']:
                df_pair[col] = df_pair[col].astype(float)
            df_pair['count'] = df_pair['count'].astype(int)
            df_pair['timestamp'] = df_pair['timestamp'].astype(int)
            df_pair['datetime'] = pd.to_datetime(df_pair['timestamp'], unit='s')

            # Calculate technical indicators
            df_pair = calculate_technical_indicators(df_pair)

            # Only keep the latest record (yesterday's data)
            df_latest = df_pair.tail(1)

            all_processed_data.append(df_latest)
            successful_pairs += 1

            # Rate limiting
            time.sleep(1.5)

        except Exception as e:
            logger.error(f"Exception fetching {pair}: {str(e)}")
            failed_pairs.append({'pair': pair, 'error': str(e)})
            time.sleep(2)

    logger.info(f"Successfully processed {successful_pairs}/{len(usd_pairs)} pairs")

    if failed_pairs:
        logger.warning(f"Failed pairs: {len(failed_pairs)}")

    if all_processed_data:
        return pd.concat(all_processed_data, ignore_index=True)
    return None


def append_to_bigquery(df):
    """Append data to BigQuery with all technical indicators"""

    if df is None or df.empty:
        logger.warning("No data to upload")
        return False

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    # Define comprehensive schema with Elliott Wave and Fibonacci fields
    schema = [
        bigquery.SchemaField("pair", "STRING"),
        bigquery.SchemaField("symbol", "STRING"),
        bigquery.SchemaField("altname", "STRING"),
        bigquery.SchemaField("base", "STRING"),
        bigquery.SchemaField("quote", "STRING"),
        bigquery.SchemaField("timestamp", "INTEGER"),
        bigquery.SchemaField("datetime", "TIMESTAMP"),
        bigquery.SchemaField("open", "FLOAT"),
        bigquery.SchemaField("open_price", "FLOAT"),
        bigquery.SchemaField("high", "FLOAT"),
        bigquery.SchemaField("low", "FLOAT"),
        bigquery.SchemaField("close", "FLOAT"),
        bigquery.SchemaField("vwap", "FLOAT"),
        bigquery.SchemaField("volume", "FLOAT"),
        bigquery.SchemaField("count", "INTEGER"),
        bigquery.SchemaField("hi_lo", "FLOAT"),
        bigquery.SchemaField("pct_hi_lo_over_lo", "FLOAT"),
        # Technical Indicators
        bigquery.SchemaField("rsi", "FLOAT"),
        bigquery.SchemaField("macd", "FLOAT"),
        bigquery.SchemaField("macd_signal", "FLOAT"),
        bigquery.SchemaField("macd_hist", "FLOAT"),
        bigquery.SchemaField("bb_upper", "FLOAT"),
        bigquery.SchemaField("bb_lower", "FLOAT"),
        bigquery.SchemaField("bb_percent", "FLOAT"),
        bigquery.SchemaField("ema_12", "FLOAT"),
        bigquery.SchemaField("ema_26", "FLOAT"),
        bigquery.SchemaField("ema_50", "FLOAT"),
        bigquery.SchemaField("ma_50", "FLOAT"),
        bigquery.SchemaField("sma_20", "FLOAT"),
        bigquery.SchemaField("sma_200", "FLOAT"),
        bigquery.SchemaField("stoch_k", "FLOAT"),
        bigquery.SchemaField("stoch_d", "FLOAT"),
        bigquery.SchemaField("williams_r", "FLOAT"),
        bigquery.SchemaField("adx", "FLOAT"),
        bigquery.SchemaField("cci", "FLOAT"),
        bigquery.SchemaField("roc", "FLOAT"),
        bigquery.SchemaField("momentum", "FLOAT"),
        bigquery.SchemaField("trix", "FLOAT"),
        bigquery.SchemaField("ultimate_oscillator", "FLOAT"),
        bigquery.SchemaField("kama", "FLOAT"),
        bigquery.SchemaField("ppo", "FLOAT"),
        bigquery.SchemaField("pvo", "FLOAT"),
        bigquery.SchemaField("awesome_oscillator", "FLOAT"),
        bigquery.SchemaField("atr", "FLOAT"),
        bigquery.SchemaField("obv", "FLOAT"),
        # Fibonacci Retracement Levels
        bigquery.SchemaField("fib_0", "FLOAT"),
        bigquery.SchemaField("fib_236", "FLOAT"),
        bigquery.SchemaField("fib_382", "FLOAT"),
        bigquery.SchemaField("fib_500", "FLOAT"),
        bigquery.SchemaField("fib_618", "FLOAT"),
        bigquery.SchemaField("fib_786", "FLOAT"),
        bigquery.SchemaField("fib_100", "FLOAT"),
        # Fibonacci Extension Levels
        bigquery.SchemaField("fib_ext_1272", "FLOAT"),
        bigquery.SchemaField("fib_ext_1618", "FLOAT"),
        bigquery.SchemaField("fib_ext_2618", "FLOAT"),
        # Distance to Fibonacci levels
        bigquery.SchemaField("dist_to_fib_236", "FLOAT"),
        bigquery.SchemaField("dist_to_fib_382", "FLOAT"),
        bigquery.SchemaField("dist_to_fib_500", "FLOAT"),
        bigquery.SchemaField("dist_to_fib_618", "FLOAT"),
        # Elliott Wave Analysis
        bigquery.SchemaField("elliott_wave_degree", "STRING"),
        bigquery.SchemaField("wave_position", "INTEGER"),
        bigquery.SchemaField("impulse_wave_count", "INTEGER"),
        bigquery.SchemaField("corrective_wave_count", "INTEGER"),
        bigquery.SchemaField("wave_1_high", "FLOAT"),
        bigquery.SchemaField("wave_2_low", "FLOAT"),
        bigquery.SchemaField("wave_3_high", "FLOAT"),
        bigquery.SchemaField("wave_4_low", "FLOAT"),
        bigquery.SchemaField("wave_5_high", "FLOAT"),
        bigquery.SchemaField("trend_direction", "INTEGER"),
        # Helper fields for wave detection
        bigquery.SchemaField("swing_high", "BOOLEAN"),
        bigquery.SchemaField("swing_low", "BOOLEAN"),
        bigquery.SchemaField("local_max", "BOOLEAN"),
        bigquery.SchemaField("local_min", "BOOLEAN"),
        bigquery.SchemaField("price_change", "FLOAT"),
    ]

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        schema=schema,
    )

    try:
        # Check for duplicates
        min_date = df['datetime'].min().strftime('%Y-%m-%d')
        max_date = df['datetime'].max().strftime('%Y-%m-%d')

        query = f"""
        SELECT DISTINCT pair, timestamp
        FROM `{table_ref}`
        WHERE DATE(datetime) BETWEEN '{min_date}' AND '{max_date}'
        """

        try:
            existing_data = client.query(query).to_dataframe()
            logger.info(f"Found {len(existing_data)} existing records")

            if not existing_data.empty:
                df['key'] = df['pair'] + '_' + df['timestamp'].astype(str)
                existing_data['key'] = existing_data['pair'] + '_' + existing_data['timestamp'].astype(str)

                df_filtered = df[~df['key'].isin(existing_data['key'])].copy()
                df_filtered = df_filtered.drop(columns=['key'])
            else:
                df_filtered = df
        except:
            df_filtered = df

        if df_filtered.empty:
            logger.info("No new data to insert")
            return True

        # Select only columns that match schema
        schema_cols = [field.name for field in schema]
        df_upload = df_filtered[[col for col in schema_cols if col in df_filtered.columns]]

        logger.info(f"Uploading {len(df_upload)} records with {len(df_upload.columns)} fields")

        job = client.load_table_from_dataframe(df_upload, table_ref, job_config=job_config)
        job.result()

        logger.info(f"Successfully uploaded {len(df_upload)} records")
        return True

    except Exception as e:
        logger.error(f"Error uploading to BigQuery: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""

    logger.info("="*60)
    logger.info("Starting Daily Crypto Data Fetch with Technical Indicators")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info("="*60)

    df = fetch_daily_data()

    if df is not None and not df.empty:
        df = df.drop_duplicates(subset=['pair', 'timestamp'], keep='last')
        logger.info(f"Final record count: {len(df)} records")

        success = append_to_bigquery(df)

        if success:
            logger.info("Daily data fetch with indicators completed successfully!")
        else:
            logger.error("Failed to upload data to BigQuery")
    else:
        logger.error("No data fetched from Kraken")

    logger.info("="*60)


@functions_framework.http
def fetch_daily_crypto(request):
    """Cloud Function entry point"""
    main()
    return 'Daily crypto data fetch with indicators completed', 200


if __name__ == "__main__":
    main()
