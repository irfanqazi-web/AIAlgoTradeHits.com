"""
Backfill All Missing Indicators - Based on Architecture Document
Adds 31 missing fields to all historical data tables using formulas from Phase 1 Methodology

MISSING FIELDS TO ADD:
Priority 1 (Critical ML Features):
- weekly_log_return: ln(close_t / close_t-1)
- return_2w, return_4w, return_8w: Multi-period returns
- rsi_slope, rsi_zscore, rsi_overbought_flag, rsi_oversold_flag: RSI enhancements
- macd_cross_flag: MACD cross signal (+1/-1/0)
- ema_12, ema_26: Additional EMAs
- close_vs_sma20_pct, close_vs_sma50_pct, close_vs_sma200_pct: MA distance
- close_vs_ema20_pct, close_vs_ema50_pct: EMA distance
- ema_slope_20, ema_slope_50: EMA slopes

Priority 2 (Enhanced Features):
- atr_pct, atr_slope, atr_zscore: ATR enhancements
- volume_zscore, volume_ratio: Volume features
- adx, plus_di, minus_di, dx: Trend strength
- candle_body_pct, candle_range_pct, upper_shadow_pct, lower_shadow_pct: Candle geometry
"""

import sys
import io
import warnings
from datetime import datetime, timezone
from google.cloud import bigquery
import pandas as pd
import numpy as np

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

warnings.filterwarnings('ignore')

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

# All tables to backfill
TABLES_TO_BACKFILL = [
    'stocks_historical_daily',
    'cryptos_historical_daily',
    'etfs_historical_daily',
    'forex_historical_daily',
    'indices_historical_daily',
    'commodities_historical_daily',
]

# Missing fields with their BigQuery types
MISSING_FIELDS = [
    ('weekly_log_return', 'FLOAT64'),
    ('return_2w', 'FLOAT64'),
    ('return_4w', 'FLOAT64'),
    ('return_8w', 'FLOAT64'),
    ('rsi_slope', 'FLOAT64'),
    ('rsi_zscore', 'FLOAT64'),
    ('rsi_overbought_flag', 'INT64'),
    ('rsi_oversold_flag', 'INT64'),
    ('macd_cross_flag', 'INT64'),
    ('ema_12', 'FLOAT64'),
    ('ema_26', 'FLOAT64'),
    ('close_vs_sma20_pct', 'FLOAT64'),
    ('close_vs_sma50_pct', 'FLOAT64'),
    ('close_vs_sma200_pct', 'FLOAT64'),
    ('close_vs_ema20_pct', 'FLOAT64'),
    ('close_vs_ema50_pct', 'FLOAT64'),
    ('ema_slope_20', 'FLOAT64'),
    ('ema_slope_50', 'FLOAT64'),
    ('atr_pct', 'FLOAT64'),
    ('atr_slope', 'FLOAT64'),
    ('atr_zscore', 'FLOAT64'),
    ('volume_zscore', 'FLOAT64'),
    ('volume_ratio', 'FLOAT64'),
    ('adx', 'FLOAT64'),
    ('plus_di', 'FLOAT64'),
    ('minus_di', 'FLOAT64'),
    ('dx', 'FLOAT64'),
    ('candle_body_pct', 'FLOAT64'),
    ('candle_range_pct', 'FLOAT64'),
    ('upper_shadow_pct', 'FLOAT64'),
    ('lower_shadow_pct', 'FLOAT64'),
]


def add_missing_columns(client, table_id, existing_fields):
    """Add missing columns to the table schema"""
    fields_to_add = []

    for field_name, field_type in MISSING_FIELDS:
        if field_name not in existing_fields:
            fields_to_add.append(f"ADD COLUMN IF NOT EXISTS {field_name} {field_type}")

    if not fields_to_add:
        print(f"  All columns already exist in {table_id}")
        return True

    # BigQuery ALTER TABLE to add columns
    for field_def in fields_to_add:
        try:
            query = f"ALTER TABLE `{table_id}` {field_def}"
            client.query(query).result()
        except Exception as e:
            if "already exists" not in str(e).lower():
                print(f"  Error adding column: {e}")

    print(f"  Added {len(fields_to_add)} new columns to {table_id}")
    return True


def calculate_missing_indicators(df):
    """Calculate all missing indicators for a DataFrame"""

    if len(df) < 5:
        return df

    # Ensure numeric types
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    close = df['close']
    high = df['high']
    low = df['low']
    open_price = df['open']
    volume = df['volume'] if 'volume' in df.columns else pd.Series([0] * len(df), index=df.index)

    # =========================================================================
    # PRIORITY 1: CRITICAL ML FEATURES
    # =========================================================================

    # Log Return: ln(close_t / close_t-1)
    df['weekly_log_return'] = np.log(close / close.shift(1))

    # Multi-period returns
    if len(df) >= 2:
        df['return_2w'] = (close / close.shift(2) - 1) * 100
    if len(df) >= 4:
        df['return_4w'] = (close / close.shift(4) - 1) * 100
    if len(df) >= 8:
        df['return_8w'] = (close / close.shift(8) - 1) * 100

    # RSI Enhancements
    if 'rsi_14' in df.columns:
        rsi = df['rsi_14']

        # RSI Slope: rsi_t - rsi_t-1
        df['rsi_slope'] = rsi.diff()

        # RSI Z-Score: (rsi - mean_100) / std_100
        lookback = min(100, len(df) - 1)
        if lookback >= 20:
            rsi_mean = rsi.rolling(window=lookback, min_periods=20).mean()
            rsi_std = rsi.rolling(window=lookback, min_periods=20).std()
            df['rsi_zscore'] = (rsi - rsi_mean) / rsi_std.replace(0, 0.0001)

        # RSI Flags
        df['rsi_overbought_flag'] = (rsi > 70).astype(int)
        df['rsi_oversold_flag'] = (rsi < 30).astype(int)

    # MACD Cross Flag
    if 'macd' in df.columns and 'macd_signal' in df.columns:
        macd_above = df['macd'] > df['macd_signal']
        df['macd_cross_flag'] = 0
        # Bullish cross: MACD crosses above signal
        df.loc[macd_above & ~macd_above.shift(1).fillna(False), 'macd_cross_flag'] = 1
        # Bearish cross: MACD crosses below signal
        df.loc[~macd_above & macd_above.shift(1).fillna(True), 'macd_cross_flag'] = -1

    # Additional EMAs (12 and 26 for MACD components)
    if len(df) >= 12:
        df['ema_12'] = close.ewm(span=12, adjust=False).mean()
    if len(df) >= 26:
        df['ema_26'] = close.ewm(span=26, adjust=False).mean()

    # MA Distance Features
    if 'sma_20' in df.columns:
        df['close_vs_sma20_pct'] = ((close / df['sma_20']) - 1) * 100
    if 'sma_50' in df.columns:
        df['close_vs_sma50_pct'] = ((close / df['sma_50']) - 1) * 100
    if 'sma_200' in df.columns:
        df['close_vs_sma200_pct'] = ((close / df['sma_200']) - 1) * 100
    if 'ema_20' in df.columns:
        df['close_vs_ema20_pct'] = ((close / df['ema_20']) - 1) * 100
    if 'ema_50' in df.columns:
        df['close_vs_ema50_pct'] = ((close / df['ema_50']) - 1) * 100

    # EMA Slopes
    if 'ema_20' in df.columns:
        df['ema_slope_20'] = df['ema_20'].diff()
    if 'ema_50' in df.columns:
        df['ema_slope_50'] = df['ema_50'].diff()

    # =========================================================================
    # PRIORITY 2: ENHANCED FEATURES
    # =========================================================================

    # ATR Enhancements
    if 'atr_14' in df.columns:
        atr = df['atr_14']

        # ATR Percentage: (atr / close) * 100
        df['atr_pct'] = (atr / close) * 100

        # ATR Slope
        df['atr_slope'] = atr.diff()

        # ATR Z-Score
        lookback = min(100, len(df) - 1)
        if lookback >= 20:
            atr_mean = atr.rolling(window=lookback, min_periods=20).mean()
            atr_std = atr.rolling(window=lookback, min_periods=20).std()
            df['atr_zscore'] = (atr - atr_mean) / atr_std.replace(0, 0.0001)

    # Volume Features
    if volume.sum() > 0:
        vol_mean = volume.rolling(window=20, min_periods=5).mean()
        vol_std = volume.rolling(window=20, min_periods=5).std()

        # Volume Z-Score: (volume - mean_20) / std_20
        df['volume_zscore'] = (volume - vol_mean) / vol_std.replace(0, 0.0001)

        # Volume Ratio: volume / MA_volume
        df['volume_ratio'] = volume / vol_mean.replace(0, 0.0001)

    # ADX and Directional Indicators
    if len(df) >= 14:
        # Calculate +DM and -DM
        high_diff = high.diff()
        low_diff = -low.diff()

        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Smoothed values (14-period)
        atr14 = tr.rolling(window=14, min_periods=5).mean()
        plus_dm14 = plus_dm.rolling(window=14, min_periods=5).mean()
        minus_dm14 = minus_dm.rolling(window=14, min_periods=5).mean()

        # +DI and -DI
        df['plus_di'] = (plus_dm14 / atr14.replace(0, 0.0001)) * 100
        df['minus_di'] = (minus_dm14 / atr14.replace(0, 0.0001)) * 100

        # DX and ADX
        di_diff = abs(df['plus_di'] - df['minus_di'])
        di_sum = df['plus_di'] + df['minus_di']
        df['dx'] = (di_diff / di_sum.replace(0, 0.0001)) * 100
        df['adx'] = df['dx'].rolling(window=14, min_periods=5).mean()

    # Candle Geometry
    # candle_body_pct: (close - open) / open * 100
    df['candle_body_pct'] = ((close - open_price) / open_price.replace(0, 0.0001)) * 100

    # candle_range_pct: (high - low) / open * 100
    df['candle_range_pct'] = ((high - low) / open_price.replace(0, 0.0001)) * 100

    # Shadow percentages
    body_high = df[['open', 'close']].max(axis=1)
    body_low = df[['open', 'close']].min(axis=1)
    candle_range = high - low

    # upper_shadow_pct: (high - max(open,close)) / (high - low) * 100
    df['upper_shadow_pct'] = ((high - body_high) / candle_range.replace(0, 0.0001)) * 100

    # lower_shadow_pct: (min(open,close) - low) / (high - low) * 100
    df['lower_shadow_pct'] = ((body_low - low) / candle_range.replace(0, 0.0001)) * 100

    return df


def backfill_table(client, table_name):
    """Backfill missing indicators for a single table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    print(f"\n{'='*60}")
    print(f"Processing: {table_name}")
    print(f"{'='*60}")

    # Get current schema
    try:
        table = client.get_table(table_id)
        existing_fields = set(f.name for f in table.schema)
        row_count = table.num_rows
        print(f"  Current rows: {row_count}")
        print(f"  Current fields: {len(existing_fields)}")
    except Exception as e:
        print(f"  Error accessing table: {e}")
        return 0

    # Add missing columns first
    add_missing_columns(client, table_id, existing_fields)

    # Get unique symbols
    query = f"SELECT DISTINCT symbol FROM `{table_id}`"
    symbols_df = client.query(query).to_dataframe()
    symbols = symbols_df['symbol'].tolist()
    print(f"  Unique symbols: {len(symbols)}")

    total_updated = 0

    for i, symbol in enumerate(symbols):
        print(f"  [{i+1}/{len(symbols)}] Processing {symbol}...", end=" ")
        sys.stdout.flush()

        try:
            # Fetch data for this symbol
            query = f"""
                SELECT * FROM `{table_id}`
                WHERE symbol = '{symbol}'
                ORDER BY datetime ASC
            """
            df = client.query(query).to_dataframe()

            if len(df) == 0:
                print("No data")
                continue

            # Calculate missing indicators
            df = calculate_missing_indicators(df)

            # Prepare update data - only the new columns
            new_columns = [field[0] for field in MISSING_FIELDS if field[0] in df.columns]

            if not new_columns:
                print("No new columns to update")
                continue

            # Create a temp table and merge
            temp_table_id = f"{PROJECT_ID}.{DATASET_ID}.temp_backfill_{table_name}"

            # Select only symbol, datetime, and new columns for the temp table
            df_update = df[['symbol', 'datetime'] + new_columns].copy()

            # Replace inf/nan with None
            df_update = df_update.replace({np.nan: None, np.inf: None, -np.inf: None})

            # Upload to temp table
            job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
            client.load_table_from_dataframe(df_update, temp_table_id, job_config=job_config).result()

            # Build MERGE statement
            set_clauses = [f"T.{col} = S.{col}" for col in new_columns]
            merge_query = f"""
                MERGE `{table_id}` T
                USING `{temp_table_id}` S
                ON T.symbol = S.symbol AND T.datetime = S.datetime
                WHEN MATCHED THEN
                    UPDATE SET {', '.join(set_clauses)}
            """

            client.query(merge_query).result()

            # Drop temp table
            client.delete_table(temp_table_id, not_found_ok=True)

            print(f"Updated {len(df)} rows")
            total_updated += len(df)

        except Exception as e:
            print(f"Error: {str(e)[:50]}")

    return total_updated


def main():
    print("=" * 70)
    print("BACKFILL ALL MISSING INDICATORS")
    print("Based on Phase 1 Methodology Architecture Document")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    print(f"\nMissing fields to add: {len(MISSING_FIELDS)}")
    print("Priority 1 (Critical):")
    print("  - weekly_log_return, return_2w/4w/8w")
    print("  - rsi_slope, rsi_zscore, rsi_overbought/oversold_flag")
    print("  - macd_cross_flag, ema_12, ema_26")
    print("  - close_vs_sma20/50/200_pct, close_vs_ema20/50_pct")
    print("  - ema_slope_20/50")
    print("Priority 2 (Enhanced):")
    print("  - atr_pct, atr_slope, atr_zscore")
    print("  - volume_zscore, volume_ratio")
    print("  - adx, plus_di, minus_di, dx")
    print("  - candle_body_pct, candle_range_pct, upper/lower_shadow_pct")

    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    total_records = 0

    for table_name in TABLES_TO_BACKFILL:
        records = backfill_table(client, table_name)
        total_records += records

    print("\n" + "=" * 70)
    print("BACKFILL COMPLETE")
    print("=" * 70)
    print(f"Total records updated: {total_records}")
    print(f"Tables processed: {len(TABLES_TO_BACKFILL)}")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    main()
