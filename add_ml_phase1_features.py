"""
Add ML Phase 1 Features to BigQuery Tables
Implements Phase 1A, 1B, and 1C features from Saleem's methodology
"""

import sys
import io
from google.cloud import bigquery
from datetime import datetime
import pandas as pd
import numpy as np

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

client = bigquery.Client(project=PROJECT_ID)

print("=" * 80)
print("ML PHASE 1 FEATURE IMPLEMENTATION")
print(f"Project: {PROJECT_ID}")
print(f"Dataset: {DATASET_ID}")
print(f"Timestamp: {datetime.now().isoformat()}")
print("=" * 80)

# Tables to add features to
TABLES = [
    "v2_crypto_daily",
    "v2_stocks_daily",
    "v2_etfs_daily"
]

# Phase 1A: Quick Win Features
PHASE_1A_COLUMNS = """
    log_return FLOAT64,
    return_2w FLOAT64,
    return_4w FLOAT64,
    ema_20 FLOAT64,
    ema_50 FLOAT64,
    ema_200 FLOAT64,
    close_vs_sma20_pct FLOAT64,
    close_vs_sma50_pct FLOAT64,
    close_vs_sma200_pct FLOAT64,
    bb_width FLOAT64
"""

# Phase 1B: Momentum Enhancement Features
PHASE_1B_COLUMNS = """
    rsi_slope FLOAT64,
    rsi_zscore FLOAT64,
    rsi_overbought INT64,
    rsi_oversold INT64,
    macd_cross INT64,
    ema20_slope FLOAT64,
    ema50_slope FLOAT64,
    atr_zscore FLOAT64,
    atr_slope FLOAT64,
    volume_zscore FLOAT64,
    volume_ratio FLOAT64
"""

# Phase 1C: Advanced Features
PHASE_1C_COLUMNS = """
    plus_di FLOAT64,
    minus_di FLOAT64,
    pivot_high_flag INT64,
    pivot_low_flag INT64,
    dist_to_pivot_high FLOAT64,
    dist_to_pivot_low FLOAT64,
    trend_regime INT64,
    vol_regime INT64,
    regime_confidence FLOAT64
"""


def add_columns_to_table(table_name, columns_sql):
    """Add new columns to a BigQuery table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Parse columns from SQL string
    columns = []
    for line in columns_sql.strip().split('\n'):
        line = line.strip().rstrip(',')
        if line:
            parts = line.split()
            if len(parts) >= 2:
                columns.append((parts[0], parts[1]))

    # Get existing schema
    table = client.get_table(table_id)
    existing_columns = {field.name for field in table.schema}

    # Add new columns
    new_schema = list(table.schema)
    added = []

    for col_name, col_type in columns:
        if col_name not in existing_columns:
            new_schema.append(bigquery.SchemaField(col_name, col_type))
            added.append(col_name)

    if added:
        table.schema = new_schema
        client.update_table(table, ["schema"])
        print(f"  Added {len(added)} columns to {table_name}: {', '.join(added)}")
    else:
        print(f"  No new columns needed for {table_name}")

    return added


def calculate_features_for_symbol(table_name, symbol):
    """Calculate Phase 1 features for a specific symbol"""

    # Query existing data
    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    WHERE symbol = '{symbol}'
    ORDER BY datetime
    """

    df = client.query(query).to_dataframe()

    if df.empty or len(df) < 200:
        print(f"    Skipping {symbol} - insufficient data ({len(df)} rows)")
        return 0

    print(f"    Processing {symbol} - {len(df)} rows")

    # Phase 1A: Quick Wins
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    df['return_2w'] = df['close'] / df['close'].shift(2) - 1
    df['return_4w'] = df['close'] / df['close'].shift(4) - 1
    df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()

    # MA Distance %
    if 'sma_20' in df.columns and df['sma_20'].notna().any():
        df['close_vs_sma20_pct'] = (df['close'] / df['sma_20'] - 1) * 100
    if 'sma_50' in df.columns and df['sma_50'].notna().any():
        df['close_vs_sma50_pct'] = (df['close'] / df['sma_50'] - 1) * 100
    if 'sma_200' in df.columns and df['sma_200'].notna().any():
        df['close_vs_sma200_pct'] = (df['close'] / df['sma_200'] - 1) * 100

    # Bollinger Width
    if 'bollinger_upper' in df.columns and 'bollinger_lower' in df.columns and 'bollinger_middle' in df.columns:
        df['bb_width'] = (df['bollinger_upper'] - df['bollinger_lower']) / df['bollinger_middle']

    # Phase 1B: Momentum Enhancements
    if 'rsi' in df.columns and df['rsi'].notna().any():
        df['rsi_slope'] = df['rsi'] - df['rsi'].shift(1)
        df['rsi_zscore'] = (df['rsi'] - df['rsi'].rolling(100, min_periods=20).mean()) / df['rsi'].rolling(100, min_periods=20).std()
        df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
        df['rsi_oversold'] = (df['rsi'] < 30).astype(int)

    # MACD Cross
    if 'macd' in df.columns and 'macd_signal' in df.columns:
        df['macd_cross'] = np.where(
            (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1)), 1,
            np.where((df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1)), -1, 0)
        )

    # EMA Slopes
    df['ema20_slope'] = df['ema_20'] - df['ema_20'].shift(1)
    df['ema50_slope'] = df['ema_50'] - df['ema_50'].shift(1)

    # ATR derivatives
    if 'atr' in df.columns and df['atr'].notna().any():
        df['atr_zscore'] = (df['atr'] - df['atr'].rolling(52, min_periods=14).mean()) / df['atr'].rolling(52, min_periods=14).std()
        df['atr_slope'] = df['atr'] - df['atr'].shift(1)

    # Volume metrics
    if 'volume' in df.columns and df['volume'].notna().any():
        df['volume_zscore'] = (df['volume'] - df['volume'].rolling(52, min_periods=14).mean()) / df['volume'].rolling(52, min_periods=14).std()
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20, min_periods=5).mean()

    # Phase 1C: Advanced Features
    if 'adx' in df.columns:
        # Calculate DI+ and DI- from ADX components if available
        df['plus_di'] = None  # Would need raw +DM/-DM calculation
        df['minus_di'] = None

    # Pivot Points (simple version)
    window = 5
    df['pivot_high_flag'] = (df['high'] == df['high'].rolling(window * 2 + 1, center=True).max()).astype(int)
    df['pivot_low_flag'] = (df['low'] == df['low'].rolling(window * 2 + 1, center=True).min()).astype(int)

    # Distance to pivots (placeholder - would need forward-fill logic)
    df['dist_to_pivot_high'] = None
    df['dist_to_pivot_low'] = None

    # Regime State
    if 'sma_50' in df.columns and 'sma_200' in df.columns:
        df['trend_regime'] = np.where(
            (df['close'] > df['sma_50']) & (df['sma_50'] > df['sma_200']), 1,
            np.where((df['close'] < df['sma_50']) & (df['sma_50'] < df['sma_200']), -1, 0)
        )

    if 'atr_zscore' in df.columns:
        df['vol_regime'] = np.where(
            df['atr_zscore'] > 1, 1,
            np.where(df['atr_zscore'] < -1, -1, 0)
        )

    df['regime_confidence'] = None  # Would need more complex calculation

    # Replace inf with None
    df = df.replace([np.inf, -np.inf], None)

    # Get columns to update
    feature_columns = [
        'log_return', 'return_2w', 'return_4w', 'ema_20', 'ema_50', 'ema_200',
        'close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct', 'bb_width',
        'rsi_slope', 'rsi_zscore', 'rsi_overbought', 'rsi_oversold', 'macd_cross',
        'ema20_slope', 'ema50_slope', 'atr_zscore', 'atr_slope', 'volume_zscore', 'volume_ratio',
        'pivot_high_flag', 'pivot_low_flag', 'trend_regime', 'vol_regime'
    ]

    existing_cols = [c for c in feature_columns if c in df.columns]

    # Update table with new features - Create temp table and merge
    updates = df[['datetime', 'symbol'] + existing_cols].dropna(subset=['datetime'])

    if len(updates) > 0:
        # Use a temporary table approach for updates
        temp_table = f"{PROJECT_ID}.{DATASET_ID}._temp_features_{symbol.replace('-', '_')}"

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE"
        )

        try:
            job = client.load_table_from_dataframe(updates, temp_table, job_config=job_config)
            job.result()

            # Merge updates
            update_sets = ", ".join([f"t.{c} = s.{c}" for c in existing_cols])
            merge_query = f"""
            MERGE `{PROJECT_ID}.{DATASET_ID}.{table_name}` t
            USING `{temp_table}` s
            ON t.datetime = s.datetime AND t.symbol = s.symbol
            WHEN MATCHED THEN UPDATE SET {update_sets}
            """

            client.query(merge_query).result()

            # Clean up temp table
            client.delete_table(temp_table, not_found_ok=True)

            return len(updates)
        except Exception as e:
            print(f"    Error updating {symbol}: {e}")
            return 0

    return 0


def main():
    total_updated = 0

    # Add columns to all tables
    print("\nPhase 1: Adding new columns to tables...")
    print("-" * 60)

    for table in TABLES:
        print(f"\nProcessing {table}:")

        # Add Phase 1A columns
        print("  Phase 1A (Quick Wins):")
        add_columns_to_table(table, PHASE_1A_COLUMNS)

        # Add Phase 1B columns
        print("  Phase 1B (Momentum):")
        add_columns_to_table(table, PHASE_1B_COLUMNS)

        # Add Phase 1C columns
        print("  Phase 1C (Advanced):")
        add_columns_to_table(table, PHASE_1C_COLUMNS)

    # Calculate features for key symbols
    print("\n\nPhase 2: Calculating features for key symbols...")
    print("-" * 60)

    key_symbols = {
        "v2_crypto_daily": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "v2_stocks_daily": ["SPY", "QQQ", "AAPL", "MSFT", "NVDA"],
        "v2_etfs_daily": ["SPY", "QQQ", "IWM", "DIA"]
    }

    for table, symbols in key_symbols.items():
        print(f"\n{table}:")
        for symbol in symbols:
            rows = calculate_features_for_symbol(table, symbol)
            total_updated += rows
            if rows > 0:
                print(f"    {symbol}: Updated {rows} rows")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total rows updated with ML features: {total_updated}")
    print("=" * 80)


if __name__ == "__main__":
    main()
