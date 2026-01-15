"""
Migrate data from 3 source tables to stocks_daily_clean
- v2_stocks_daily (106 symbols, 2023-2025)
- stocks_unified_daily (316 symbols, 1998-2025)
- v2_stocks_historical_daily (302 symbols, 1998-2025)

Filters:
- NASDAQ: XNAS, XNGS, XNCM, XNMS
- NYSE: XNYS, ARCX, XASE
- CBOE: BATS, CBOE, XCBO
- Reject: OTC, Pink Sheets

Calculates all 85 fields including technical indicators and ML features.
"""

from google.cloud import bigquery
import pandas as pd
import numpy as np
from datetime import datetime

# Initialize client
client = bigquery.Client(project='aialgotradehits')

# Allowed MIC codes
ALLOWED_MIC_CODES = [
    'XNAS', 'XNGS', 'XNCM', 'XNMS',  # NASDAQ
    'XNYS', 'ARCX', 'XASE',           # NYSE
    'BATS', 'CBOE', 'XCBO'            # CBOE
]

print("="*100)
print("MIGRATING TO stocks_daily_clean TABLE")
print("="*100)

# Step 1: Extract and consolidate data from 3 source tables
print("\nStep 1: Extracting data from source tables...")
print("-"*100)

extraction_query = f"""
WITH consolidated AS (
    -- Table 1: v2_stocks_daily (most recent, 2023-2025)
    SELECT
        d.datetime,
        d.symbol,
        d.open,
        d.high,
        d.low,
        d.close,
        d.volume,
        COALESCE(m.name, d.name) as name,
        COALESCE(m.exchange, 'UNKNOWN') as exchange,
        COALESCE(m.mic_code, 'UNKNOWN') as mic_code,
        COALESCE(m.sector, 'UNKNOWN') as sector,
        COALESCE(m.industry, 'UNKNOWN') as industry,
        COALESCE(m.asset_type, 'Common Stock') as asset_type,
        COALESCE(m.country, 'US') as country,
        COALESCE(m.currency, d.currency, 'USD') as currency,
        COALESCE(m.type, 'Common Stock') as type,
        'v2_stocks_daily' as source_table
    FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily` d
    LEFT JOIN `aialgotradehits.crypto_trading_data.v2_stocks_master` m
        ON d.symbol = m.symbol

    UNION ALL

    -- Table 2: stocks_unified_daily (historical, 1998-2025)
    SELECT
        s.datetime,
        s.symbol,
        s.open,
        s.high,
        s.low,
        s.close,
        CAST(s.volume AS INT64) as volume,
        COALESCE(m.name, s.name) as name,
        COALESCE(m.exchange, s.exchange, 'UNKNOWN') as exchange,
        COALESCE(m.mic_code, 'UNKNOWN') as mic_code,
        COALESCE(m.sector, 'UNKNOWN') as sector,
        COALESCE(m.industry, 'UNKNOWN') as industry,
        COALESCE(m.asset_type, 'Common Stock') as asset_type,
        COALESCE(m.country, 'US') as country,
        COALESCE(m.currency, s.currency, 'USD') as currency,
        COALESCE(m.type, 'Common Stock') as type,
        'stocks_unified_daily' as source_table
    FROM `aialgotradehits.crypto_trading_data.stocks_unified_daily` s
    LEFT JOIN `aialgotradehits.crypto_trading_data.v2_stocks_master` m
        ON s.symbol = m.symbol

    UNION ALL

    -- Table 3: v2_stocks_historical_daily (historical, 1998-2025)
    SELECT
        h.datetime,
        h.symbol,
        h.open,
        h.high,
        h.low,
        h.close,
        CAST(h.volume AS INT64) as volume,
        COALESCE(m.name, h.name) as name,
        COALESCE(m.exchange, h.exchange, 'UNKNOWN') as exchange,
        COALESCE(m.mic_code, 'UNKNOWN') as mic_code,
        COALESCE(m.sector, 'UNKNOWN') as sector,
        COALESCE(m.industry, 'UNKNOWN') as industry,
        COALESCE(m.asset_type, h.asset_type, 'Common Stock') as asset_type,
        COALESCE(m.country, h.country, 'US') as country,
        COALESCE(m.currency, h.currency, 'USD') as currency,
        COALESCE(m.type, 'Common Stock') as type,
        'v2_stocks_historical_daily' as source_table
    FROM `aialgotradehits.crypto_trading_data.v2_stocks_historical_daily` h
    LEFT JOIN `aialgotradehits.crypto_trading_data.v2_stocks_master` m
        ON h.symbol = m.symbol
),

-- Deduplicate: For same symbol+datetime, prioritize v2_stocks_daily > stocks_unified_daily > v2_stocks_historical_daily
deduplicated AS (
    SELECT * EXCEPT(row_num, source_table)
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY symbol, datetime
                ORDER BY
                    CASE source_table
                        WHEN 'v2_stocks_daily' THEN 1
                        WHEN 'stocks_unified_daily' THEN 2
                        WHEN 'v2_stocks_historical_daily' THEN 3
                    END
            ) as row_num
        FROM consolidated
    )
    WHERE row_num = 1
)

-- Filter to allowed MIC codes
SELECT *
FROM deduplicated
WHERE mic_code IN UNNEST(@allowed_mic_codes)
    AND open > 0
    AND high > 0
    AND low > 0
    AND close > 0
    AND volume > 0
ORDER BY symbol, datetime
"""

job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ArrayQueryParameter("allowed_mic_codes", "STRING", ALLOWED_MIC_CODES)
    ]
)

print(f"Querying consolidated data with MIC code filter: {', '.join(ALLOWED_MIC_CODES)}")
print("This may take a few minutes...")

query_job = client.query(extraction_query, job_config=job_config)
df = query_job.to_dataframe()

print(f"[OK] Extracted {len(df):,} rows from source tables")
print(f"     Unique symbols: {df['symbol'].nunique()}")
print(f"     Date range: {df['datetime'].min()} to {df['datetime'].max()}")
print(f"     Exchanges: {df['exchange'].value_counts().to_dict()}")
print(f"     MIC codes: {df['mic_code'].value_counts().to_dict()}")

if len(df) == 0:
    print("[ERROR] No data extracted! Check MIC code filter.")
    exit(1)

# Step 2: Calculate technical indicators per symbol
print("\nStep 2: Calculating technical indicators for each symbol...")
print("-"*100)

def calculate_technical_indicators(group_df):
    """
    Calculate all technical indicators and ML features for a single symbol.
    This function processes data for ONE symbol at a time.
    """
    import pandas_ta as ta

    df = group_df.copy().sort_values('datetime')

    # Need at least 200 rows for accurate indicators
    if len(df) < 200:
        return None

    try:
        # PRICE STATISTICS (9-15)
        df['average_volume'] = df['volume'].rolling(20).mean().astype('Int64')
        df['change'] = df['close'] - df['close'].shift(1)
        df['percent_change'] = ((df['close'] - df['close'].shift(1)) / df['close'].shift(1)) * 100
        df['previous_close'] = df['close'].shift(1)
        df['high_low'] = df['high'] - df['low']  # Absolute range
        df['pct_high_low'] = (df['high'] - df['low']) * 100 / df['low']  # % relative to low
        df['week_52_high'] = df['high'].rolling(252).max()  # 252 trading days = 1 year
        df['week_52_low'] = df['low'].rolling(252).min()

        # MOMENTUM INDICATORS (16-24)
        df['rsi'] = ta.rsi(df['close'], length=14)
        macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
        if macd is not None:
            df['macd'] = macd['MACD_12_26_9']
            df['macd_signal'] = macd['MACDs_12_26_9']
            df['macd_histogram'] = macd['MACDh_12_26_9']
        stoch = ta.stoch(df['high'], df['low'], df['close'], k=14, d=3)
        if stoch is not None:
            df['stoch_k'] = stoch['STOCHk_14_3_3']
            df['stoch_d'] = stoch['STOCHd_14_3_3']
        df['cci'] = ta.cci(df['high'], df['low'], df['close'], length=20)
        df['williams_r'] = ta.willr(df['high'], df['low'], df['close'], length=14)
        df['momentum'] = ta.mom(df['close'], length=10)

        # MOVING AVERAGES (25-33)
        df['sma_20'] = ta.sma(df['close'], length=20)
        df['sma_50'] = ta.sma(df['close'], length=50)
        df['sma_200'] = ta.sma(df['close'], length=200)
        df['ema_12'] = ta.ema(df['close'], length=12)
        df['ema_20'] = ta.ema(df['close'], length=20)
        df['ema_26'] = ta.ema(df['close'], length=26)
        df['ema_50'] = ta.ema(df['close'], length=50)
        df['ema_200'] = ta.ema(df['close'], length=200)
        df['kama'] = ta.kama(df['close'], length=10)

        # TREND & VOLATILITY (34-43)
        bbands = ta.bbands(df['close'], length=20, std=2)
        if bbands is not None:
            df['bollinger_upper'] = bbands['BBU_20_2.0']
            df['bollinger_middle'] = bbands['BBM_20_2.0']
            df['bollinger_lower'] = bbands['BBL_20_2.0']
            df['bb_width'] = bbands['BBB_20_2.0']
        adx_result = ta.adx(df['high'], df['low'], df['close'], length=14)
        if adx_result is not None:
            df['adx'] = adx_result['ADX_14']
            df['plus_di'] = adx_result['DMP_14']
            df['minus_di'] = adx_result['DMN_14']
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        df['trix'] = ta.trix(df['close'], length=15)
        df['roc'] = ta.roc(df['close'], length=10)

        # VOLUME INDICATORS (44-46)
        df['obv'] = ta.obv(df['close'], df['volume'])
        df['pvo'] = ta.pvo(df['volume'], fast=12, slow=26)
        df['ppo'] = ta.ppo(df['close'], fast=12, slow=26)

        # ADVANCED OSCILLATORS (47-48)
        df['ultimate_osc'] = ta.uo(df['high'], df['low'], df['close'])
        df['awesome_osc'] = ta.ao(df['high'], df['low'])

        # ML FEATURES - RETURNS (49-51)
        df['log_return'] = np.log(df['close'] / df['close'].shift(1))
        df['return_2w'] = (df['close'].shift(-10) - df['close']) / df['close'] * 100  # 2 weeks = 10 trading days
        df['return_4w'] = (df['close'].shift(-20) - df['close']) / df['close'] * 100  # 4 weeks = 20 trading days

        # ML FEATURES - RELATIVE POSITIONS (52-54)
        df['close_vs_sma20_pct'] = (df['close'] - df['sma_20']) / df['sma_20'] * 100
        df['close_vs_sma50_pct'] = (df['close'] - df['sma_50']) / df['sma_50'] * 100
        df['close_vs_sma200_pct'] = (df['close'] - df['sma_200']) / df['sma_200'] * 100

        # ML FEATURES - INDICATOR DYNAMICS (55-65)
        df['rsi_slope'] = df['rsi'].diff(5)  # 5-day slope
        df['rsi_zscore'] = (df['rsi'] - df['rsi'].rolling(20).mean()) / df['rsi'].rolling(20).std()
        df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
        df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
        df['macd_cross'] = np.where(
            (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1)), 1,
            np.where((df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1)), -1, 0)
        )
        df['ema20_slope'] = df['ema_20'].diff(5)
        df['ema50_slope'] = df['ema_50'].diff(5)
        df['atr_zscore'] = (df['atr'] - df['atr'].rolling(20).mean()) / df['atr'].rolling(20).std()
        df['atr_slope'] = df['atr'].diff(5)
        df['volume_zscore'] = (df['volume'] - df['volume'].rolling(20).mean()) / df['volume'].rolling(20).std()
        df['volume_ratio'] = df['volume'] / df['average_volume']

        # ML FEATURES - MARKET STRUCTURE (66-69)
        df['pivot_high_flag'] = ((df['high'] > df['high'].shift(1)) &
                                  (df['high'] > df['high'].shift(2)) &
                                  (df['high'] > df['high'].shift(-1)) &
                                  (df['high'] > df['high'].shift(-2))).astype(int)
        df['pivot_low_flag'] = ((df['low'] < df['low'].shift(1)) &
                                 (df['low'] < df['low'].shift(2)) &
                                 (df['low'] < df['low'].shift(-1)) &
                                 (df['low'] < df['low'].shift(-2))).astype(int)
        df['dist_to_pivot_high'] = df['close'] - df['high'].where(df['pivot_high_flag'] == 1).ffill()
        df['dist_to_pivot_low'] = df['close'] - df['low'].where(df['pivot_low_flag'] == 1).ffill()

        # ML FEATURES - REGIME DETECTION (70-72)
        sma_50_slope = df['sma_50'].diff(20)  # 20-day slope
        df['trend_regime'] = np.where(sma_50_slope > 0, 1, np.where(sma_50_slope < 0, -1, 0))
        atr_20_mean = df['atr'].rolling(20).mean()
        df['vol_regime'] = (df['atr'] > atr_20_mean).astype(int)
        df['regime_confidence'] = abs(sma_50_slope) / df['sma_50'].rolling(20).std()

        # SYSTEM METADATA (82-85)
        df['timestamp'] = df['datetime'].astype('int64') // 10**9  # Unix timestamp
        df['data_source'] = 'TwelveData'  # Assume TwelveData as primary source
        df['created_at'] = pd.Timestamp.now()
        df['updated_at'] = pd.Timestamp.now()

        return df

    except Exception as e:
        print(f"[ERROR] Failed to calculate indicators for {group_df['symbol'].iloc[0]}: {e}")
        return None

# Apply indicator calculation per symbol
print("Calculating indicators for each symbol (this will take several minutes)...")
symbols = df['symbol'].unique()
total_symbols = len(symbols)

processed_dfs = []
for i, symbol in enumerate(symbols, 1):
    print(f"  [{i}/{total_symbols}] Processing {symbol}...", end='\r')
    symbol_df = df[df['symbol'] == symbol]
    result_df = calculate_technical_indicators(symbol_df)
    if result_df is not None:
        processed_dfs.append(result_df)

print(f"\n[OK] Calculated indicators for {len(processed_dfs)} symbols")

if len(processed_dfs) == 0:
    print("[ERROR] No data after indicator calculation!")
    exit(1)

# Concatenate all processed dataframes
final_df = pd.concat(processed_dfs, ignore_index=True)

print(f"[OK] Final dataset: {len(final_df):,} rows, {len(final_df.columns)} columns")

# Step 3: Upload to BigQuery
print("\nStep 3: Uploading to BigQuery...")
print("-"*100)

# Reorder columns to match schema (85 fields)
column_order = [
    # CORE (1-2)
    'datetime', 'symbol',
    # OHLCV (3-8)
    'open', 'high', 'low', 'close', 'previous_close', 'volume',
    # PRICE STATS (9-15)
    'average_volume', 'change', 'percent_change', 'high_low', 'pct_high_low', 'week_52_high', 'week_52_low',
    # MOMENTUM (16-24)
    'rsi', 'macd', 'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'cci', 'williams_r', 'momentum',
    # MOVING AVERAGES (25-33)
    'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_20', 'ema_26', 'ema_50', 'ema_200', 'kama',
    # TREND & VOLATILITY (34-43)
    'bollinger_upper', 'bollinger_middle', 'bollinger_lower', 'bb_width', 'adx', 'plus_di', 'minus_di', 'atr', 'trix', 'roc',
    # VOLUME (44-46)
    'obv', 'pvo', 'ppo',
    # ADVANCED OSCILLATORS (47-48)
    'ultimate_osc', 'awesome_osc',
    # RETURNS (49-51)
    'log_return', 'return_2w', 'return_4w',
    # RELATIVE POSITIONS (52-54)
    'close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct',
    # INDICATOR DYNAMICS (55-65)
    'rsi_slope', 'rsi_zscore', 'rsi_overbought', 'rsi_oversold', 'macd_cross',
    'ema20_slope', 'ema50_slope', 'atr_zscore', 'atr_slope', 'volume_zscore', 'volume_ratio',
    # MARKET STRUCTURE (66-69)
    'pivot_high_flag', 'pivot_low_flag', 'dist_to_pivot_high', 'dist_to_pivot_low',
    # REGIME (70-72)
    'trend_regime', 'vol_regime', 'regime_confidence',
    # METADATA (73-81)
    'name', 'sector', 'industry', 'asset_type', 'exchange', 'mic_code', 'country', 'currency', 'type',
    # SYSTEM (82-85)
    'timestamp', 'data_source', 'created_at', 'updated_at'
]

# Ensure all columns exist (fill missing with NULL)
for col in column_order:
    if col not in final_df.columns:
        final_df[col] = None

final_df = final_df[column_order]

# Convert data types
print("Converting data types...")
# Convert integer flag columns
int_cols = ['rsi_overbought', 'rsi_oversold', 'macd_cross', 'pivot_high_flag', 'pivot_low_flag', 'trend_regime', 'vol_regime']
for col in int_cols:
    final_df[col] = final_df[col].fillna(0).astype('Int64')

# Convert volume and average_volume to integer
final_df['volume'] = final_df['volume'].fillna(0).astype('Int64')
final_df['average_volume'] = final_df['average_volume'].fillna(0).astype('Int64')
final_df['timestamp'] = final_df['timestamp'].fillna(0).astype('Int64')

print(f"[OK] Prepared {len(final_df):,} rows for upload")

# Upload to BigQuery
table_id = "aialgotradehits.crypto_trading_data.stocks_daily_clean"

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,  # Append to table
)

print(f"Uploading to {table_id}...")
print("This may take several minutes...")

job = client.load_table_from_dataframe(final_df, table_id, job_config=job_config)
job.result()  # Wait for job to complete

print("[OK] Upload complete!")
print("="*100)

# Step 4: Verify upload
print("\nStep 4: Verifying upload...")
print("-"*100)

verify_query = f"""
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT symbol) as unique_symbols,
    MIN(datetime) as min_date,
    MAX(datetime) as max_date,
    COUNT(DISTINCT exchange) as exchanges,
    COUNT(DISTINCT mic_code) as mic_codes
FROM `{table_id}`
"""

result = client.query(verify_query).result()
for row in result:
    print(f"Total rows: {row.total_rows:,}")
    print(f"Unique symbols: {row.unique_symbols}")
    print(f"Date range: {row.min_date} to {row.max_date}")
    print(f"Exchanges: {row.exchanges}")
    print(f"MIC codes: {row.mic_codes}")

print("="*100)
print("MIGRATION COMPLETE!")
print("="*100)
print("\nNext steps:")
print("1. Test queries on stocks_daily_clean table")
print("2. Verify data quality")
print("3. Delete old tables after validation")
