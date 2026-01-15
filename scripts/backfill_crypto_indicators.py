"""
Backfill Technical Indicators for Crypto Historical Data
Calculates all 29 technical indicators for historical crypto data in BigQuery
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
TABLE_ID = 'crypto_analysis'

def calculate_technical_indicators(df):
    """Calculate all 29 technical indicators"""

    if len(df) < 200:
        logger.warning(f"Not enough data points ({len(df)}), need at least 200 for accurate indicators")
        return df

    # Sort by datetime to ensure proper calculation
    df = df.sort_values('datetime').reset_index(drop=True)

    # 1. RSI (Relative Strength Index) - 14 period
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # 2. MACD (Moving Average Convergence Divergence)
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # 3. Bollinger Bands
    df['sma_20'] = df['close'].rolling(window=20).mean()
    std_20 = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['sma_20'] + (std_20 * 2)
    df['bb_lower'] = df['sma_20'] - (std_20 * 2)
    df['bb_percent'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

    # 4. EMAs
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

    # 5. SMAs
    df['sma_200'] = df['close'].rolling(window=200).mean()
    df['ma_50'] = df['close'].rolling(window=50).mean()

    # 6. Stochastic Oscillator
    low_14 = df['low'].rolling(window=14).min()
    high_14 = df['high'].rolling(window=14).max()
    df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # 7. Williams %R
    df['williams_r'] = -100 * ((high_14 - df['close']) / (high_14 - low_14))

    # 8. ADX (Average Directional Index)
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr1 = df['high'] - df['low']
    tr2 = abs(df['high'] - df['close'].shift())
    tr3 = abs(df['low'] - df['close'].shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=14).mean()

    plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    df['adx'] = dx.rolling(window=14).mean()

    # 9. CCI (Commodity Channel Index)
    tp = (df['high'] + df['low'] + df['close']) / 3
    df['cci'] = (tp - tp.rolling(window=20).mean()) / (0.015 * tp.rolling(window=20).std())

    # 10. ROC (Rate of Change)
    df['roc'] = ((df['close'] - df['close'].shift(12)) / df['close'].shift(12)) * 100

    # 11. Momentum
    df['momentum'] = df['close'] - df['close'].shift(10)

    # 12. TRIX (Triple Exponential Average)
    ema1 = df['close'].ewm(span=15, adjust=False).mean()
    ema2 = ema1.ewm(span=15, adjust=False).mean()
    ema3 = ema2.ewm(span=15, adjust=False).mean()
    df['trix'] = (ema3.diff() / ema3) * 100

    # 13. Ultimate Oscillator
    bp = df['close'] - pd.concat([df['low'], df['close'].shift()], axis=1).min(axis=1)
    tr = pd.concat([df['high'] - df['low'],
                    abs(df['high'] - df['close'].shift()),
                    abs(df['low'] - df['close'].shift())], axis=1).max(axis=1)

    avg7 = bp.rolling(window=7).sum() / tr.rolling(window=7).sum()
    avg14 = bp.rolling(window=14).sum() / tr.rolling(window=14).sum()
    avg28 = bp.rolling(window=28).sum() / tr.rolling(window=28).sum()

    df['ultimate_oscillator'] = 100 * ((4 * avg7) + (2 * avg14) + avg28) / 7

    # 14. KAMA (Kaufman's Adaptive Moving Average)
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

    # 15. PPO (Percentage Price Oscillator)
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['ppo'] = ((ema12 - ema26) / ema26) * 100

    # 16. PVO (Percentage Volume Oscillator)
    vol_ema12 = df['volume'].ewm(span=12, adjust=False).mean()
    vol_ema26 = df['volume'].ewm(span=26, adjust=False).mean()
    df['pvo'] = ((vol_ema12 - vol_ema26) / vol_ema26) * 100

    # 17. Awesome Oscillator
    median_price = (df['high'] + df['low']) / 2
    ao = median_price.rolling(window=5).mean() - median_price.rolling(window=34).mean()
    df['awesome_oscillator'] = ao

    # 18. ATR (Average True Range)
    df['atr'] = atr

    # 19. OBV (On-Balance Volume)
    df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()

    # Fill NaN values with None for BigQuery compatibility
    df = df.replace({np.nan: None, np.inf: None, -np.inf: None})

    return df


def backfill_pair_indicators(client, pair_symbol):
    """Backfill indicators for a specific trading pair"""

    logger.info(f"Processing {pair_symbol}...")

    try:
        # Fetch all historical data for this pair
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE pair = '{pair_symbol}'
        ORDER BY datetime ASC
        """

        df = client.query(query).to_dataframe()

        if len(df) == 0:
            logger.warning(f"No data found for {pair_symbol}")
            return 0

        logger.info(f"  Found {len(df)} records from {df['datetime'].min()} to {df['datetime'].max()}")

        # Calculate indicators
        df = calculate_technical_indicators(df)

        # Update records in BigQuery
        # We'll do this in batches to avoid overwhelming BigQuery
        batch_size = 500
        updated_count = 0

        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]

            # Create update statements for each record
            for idx, row in batch_df.iterrows():
                # Helper function to format values for SQL
                def format_value(val):
                    if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
                        return 'NULL'
                    return str(val)

                update_query = f"""
                UPDATE `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
                SET
                    rsi = {format_value(row['rsi'])},
                    macd = {format_value(row['macd'])},
                    macd_signal = {format_value(row['macd_signal'])},
                    macd_hist = {format_value(row['macd_hist'])},
                    bb_upper = {format_value(row['bb_upper'])},
                    bb_lower = {format_value(row['bb_lower'])},
                    bb_percent = {format_value(row['bb_percent'])},
                    ema_12 = {format_value(row['ema_12'])},
                    ema_26 = {format_value(row['ema_26'])},
                    ema_50 = {format_value(row['ema_50'])},
                    ma_50 = {format_value(row['ma_50'])},
                    sma_20 = {format_value(row['sma_20'])},
                    sma_200 = {format_value(row['sma_200'])},
                    stoch_k = {format_value(row['stoch_k'])},
                    stoch_d = {format_value(row['stoch_d'])},
                    williams_r = {format_value(row['williams_r'])},
                    adx = {format_value(row['adx'])},
                    cci = {format_value(row['cci'])},
                    roc = {format_value(row['roc'])},
                    momentum = {format_value(row['momentum'])},
                    trix = {format_value(row['trix'])},
                    ultimate_oscillator = {format_value(row['ultimate_oscillator'])},
                    kama = {format_value(row['kama'])},
                    ppo = {format_value(row['ppo'])},
                    pvo = {format_value(row['pvo'])},
                    awesome_oscillator = {format_value(row['awesome_oscillator'])},
                    atr = {format_value(row['atr'])},
                    obv = {format_value(row['obv'])}
                WHERE pair = '{pair_symbol}'
                  AND datetime = TIMESTAMP('{row['datetime']}')
                """

                try:
                    client.query(update_query).result()
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Error updating record for {pair_symbol} at {row['datetime']}: {str(e)}")

            logger.info(f"  Updated {updated_count}/{len(df)} records...")
            time.sleep(0.5)  # Rate limiting

        logger.info(f"✓ Completed {pair_symbol}: {updated_count} records updated")
        return updated_count

    except Exception as e:
        logger.error(f"✗ Error processing {pair_symbol}: {str(e)}")
        return 0


def main():
    """Main execution function"""

    print("=" * 70)
    print("CRYPTO INDICATORS BACKFILL SCRIPT")
    print("=" * 70)
    print()

    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    # Get all unique pairs
    query = f"""
    SELECT DISTINCT pair
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    ORDER BY pair
    """

    pairs_df = client.query(query).to_dataframe()
    total_pairs = len(pairs_df)

    print(f"Found {total_pairs} unique trading pairs to process")
    print()

    # Process each pair
    total_updated = 0
    start_time = time.time()

    for idx, row in pairs_df.iterrows():
        pair = row['pair']
        print(f"\n[{idx+1}/{total_pairs}] Processing {pair}...")

        updated = backfill_pair_indicators(client, pair)
        total_updated += updated

        # Progress update
        elapsed = time.time() - start_time
        avg_time = elapsed / (idx + 1)
        remaining = (total_pairs - idx - 1) * avg_time

        print(f"Progress: {idx+1}/{total_pairs} pairs | "
              f"Updated: {total_updated} records | "
              f"ETA: {remaining/60:.1f} minutes")

    print()
    print("=" * 70)
    print("BACKFILL COMPLETE")
    print(f"Total pairs processed: {total_pairs}")
    print(f"Total records updated: {total_updated}")
    print(f"Total time: {(time.time() - start_time)/60:.1f} minutes")
    print("=" * 70)


if __name__ == "__main__":
    main()
