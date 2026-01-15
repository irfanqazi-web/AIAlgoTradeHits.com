"""
SIMPLIFIED Migration: Basic OHLCV data + metadata only
We'll calculate indicators in a separate step after validating the base data
"""

from google.cloud import bigquery
import pandas as pd
import numpy as np
from datetime import datetime

client = bigquery.Client(project='aialgotradehits')

ALLOWED_MIC_CODES = [
    'XNAS', 'XNGS', 'XNCM', 'XNMS',  # NASDAQ
    'XNYS', 'ARCX', 'XASE',           # NYSE
    'BATS', 'CBOE', 'XCBO'            # CBOE
]

print("="*100)
print("SIMPLIFIED MIGRATION: Basic Data Only (OHLCV + Metadata)")
print("="*100)

# Step 1: Extract and consolidate
print("\nStep 1: Extracting and consolidating data...")
print("-"*100)

extraction_query = f"""
WITH consolidated AS (
    SELECT
        d.datetime,
        d.symbol,
        d.open,
        d.high,
        d.low,
        d.close,
        CAST(d.volume AS INT64) as volume,
        COALESCE(m.name, d.name) as name,
        COALESCE(m.exchange, 'UNKNOWN') as exchange,
        COALESCE(m.mic_code, 'UNKNOWN') as mic_code,
        COALESCE(m.sector, 'UNKNOWN') as sector,
        COALESCE(m.industry, 'UNKNOWN') as industry,
        COALESCE(m.asset_type, 'Common Stock') as asset_type,
        COALESCE(m.country, 'US') as country,
        COALESCE(m.currency, d.currency, 'USD') as currency,
        COALESCE(m.type, 'Common Stock') as type,
        'v2_stocks_daily' as source_table,
        1 as priority
    FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily` d
    LEFT JOIN `aialgotradehits.crypto_trading_data.v2_stocks_master` m
        ON d.symbol = m.symbol

    UNION ALL

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
        'stocks_unified_daily' as source_table,
        2 as priority
    FROM `aialgotradehits.crypto_trading_data.stocks_unified_daily` s
    LEFT JOIN `aialgotradehits.crypto_trading_data.v2_stocks_master` m
        ON s.symbol = m.symbol

    UNION ALL

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
        'v2_stocks_historical_daily' as source_table,
        3 as priority
    FROM `aialgotradehits.crypto_trading_data.v2_stocks_historical_daily` h
    LEFT JOIN `aialgotradehits.crypto_trading_data.v2_stocks_master` m
        ON h.symbol = m.symbol
),

deduplicated AS (
    SELECT * EXCEPT(row_num, source_table, priority)
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY symbol, datetime
                ORDER BY priority
            ) as row_num
        FROM consolidated
    )
    WHERE row_num = 1
)

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

print(f"Querying with MIC filter: {', '.join(ALLOWED_MIC_CODES)}")
query_job = client.query(extraction_query, job_config=job_config)
df = query_job.to_dataframe()

print(f"[OK] Extracted {len(df):,} rows")
print(f"     Symbols: {df['symbol'].nunique()}")
print(f"     Date range: {df['datetime'].min()} to {df['datetime'].max()}")
print(f"     Exchanges: {df['exchange'].value_counts().to_dict()}")

# Step 2: Add calculated fields (basic only, no indicators yet)
print("\nStep 2: Adding basic calculated fields...")
print("-"*100)

df = df.sort_values(['symbol', 'datetime'])

# Calculate basic price statistics per symbol
def add_basic_calculations(group_df):
    df_calc = group_df.copy()

    # Price statistics
    df_calc['previous_close'] = df_calc['close'].shift(1)
    df_calc['change'] = df_calc['close'] - df_calc['previous_close']
    df_calc['percent_change'] = (df_calc['change'] / df_calc['previous_close']) * 100
    df_calc['high_low'] = df_calc['high'] - df_calc['low']
    df_calc['pct_high_low'] = (df_calc['high'] - df_calc['low']) * 100 / df_calc['low']
    df_calc['average_volume'] = df_calc['volume'].rolling(20, min_periods=1).mean().astype('Int64')
    df_calc['week_52_high'] = df_calc['high'].rolling(252, min_periods=1).max()
    df_calc['week_52_low'] = df_calc['low'].rolling(252, min_periods=1).min()

    # System metadata
    df_calc['timestamp'] = df_calc['datetime'].astype('int64') // 10**9
    df_calc['data_source'] = 'TwelveData'
    df_calc['created_at'] = pd.Timestamp.now()
    df_calc['updated_at'] = pd.Timestamp.now()

    return df_calc

print("Calculating basic fields for each symbol...")
processed_dfs = []
symbols = df['symbol'].unique()
for i, symbol in enumerate(symbols, 1):
    print(f"  [{i}/{len(symbols)}] {symbol}...", end='\r')
    symbol_df = df[df['symbol'] == symbol]
    result_df = add_basic_calculations(symbol_df)
    processed_dfs.append(result_df)

print(f"\n[OK] Processed {len(processed_dfs)} symbols")

final_df = pd.concat(processed_dfs, ignore_index=True)

# Step 3: Prepare for upload
print("\nStep 3: Preparing data for upload...")
print("-"*100)

# Create final dataframe with all 85 columns (indicators set to NULL for now)
upload_df = pd.DataFrame()

# CORE (1-2)
upload_df['datetime'] = final_df['datetime']
upload_df['symbol'] = final_df['symbol']

# OHLCV (3-8)
upload_df['open'] = final_df['open']
upload_df['high'] = final_df['high']
upload_df['low'] = final_df['low']
upload_df['close'] = final_df['close']
upload_df['previous_close'] = final_df['previous_close']
upload_df['volume'] = final_df['volume'].astype('Int64')

# PRICE STATS (9-15)
upload_df['average_volume'] = final_df['average_volume']
upload_df['change'] = final_df['change']
upload_df['percent_change'] = final_df['percent_change']
upload_df['high_low'] = final_df['high_low']
upload_df['pct_high_low'] = final_df['pct_high_low']
upload_df['week_52_high'] = final_df['week_52_high']
upload_df['week_52_low'] = final_df['week_52_low']

# MOMENTUM (16-24) - NULL for now
for col in ['rsi', 'macd', 'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'cci', 'williams_r', 'momentum']:
    upload_df[col] = None

# MOVING AVERAGES (25-33) - NULL for now
for col in ['sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_20', 'ema_26', 'ema_50', 'ema_200', 'kama']:
    upload_df[col] = None

# TREND & VOLATILITY (34-43) - NULL for now
for col in ['bollinger_upper', 'bollinger_middle', 'bollinger_lower', 'bb_width', 'adx', 'plus_di', 'minus_di', 'atr', 'trix', 'roc']:
    upload_df[col] = None

# VOLUME (44-46) - NULL for now
for col in ['obv', 'pvo', 'ppo']:
    upload_df[col] = None

# OSCILLATORS (47-48) - NULL for now
for col in ['ultimate_osc', 'awesome_osc']:
    upload_df[col] = None

# RETURNS (49-51) - NULL for now
for col in ['log_return', 'return_2w', 'return_4w']:
    upload_df[col] = None

# RELATIVE POSITIONS (52-54) - NULL for now
for col in ['close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct']:
    upload_df[col] = None

# INDICATOR DYNAMICS (55-65) - NULL for now
for col in ['rsi_slope', 'rsi_zscore', 'rsi_overbought', 'rsi_oversold', 'macd_cross', 'ema20_slope', 'ema50_slope', 'atr_zscore', 'atr_slope', 'volume_zscore', 'volume_ratio']:
    upload_df[col] = None

# MARKET STRUCTURE (66-69) - NULL for now
for col in ['pivot_high_flag', 'pivot_low_flag', 'dist_to_pivot_high', 'dist_to_pivot_low']:
    upload_df[col] = None

# REGIME (70-72) - NULL for now
for col in ['trend_regime', 'vol_regime', 'regime_confidence']:
    upload_df[col] = None

# METADATA (73-81)
upload_df['name'] = final_df['name']
upload_df['sector'] = final_df['sector']
upload_df['industry'] = final_df['industry']
upload_df['asset_type'] = final_df['asset_type']
upload_df['exchange'] = final_df['exchange']
upload_df['mic_code'] = final_df['mic_code']
upload_df['country'] = final_df['country']
upload_df['currency'] = final_df['currency']
upload_df['type'] = final_df['type']

# SYSTEM (82-85)
upload_df['timestamp'] = final_df['timestamp'].astype('Int64')
upload_df['data_source'] = final_df['data_source']
upload_df['created_at'] = final_df['created_at']
upload_df['updated_at'] = final_df['updated_at']

print(f"[OK] Prepared {len(upload_df):,} rows with 85 columns")
print(f"     Columns with data: 27 (basic OHLCV + metadata)")
print(f"     Columns NULL: 58 (technical indicators - will calculate later)")

# Step 4: Upload
print("\nStep 4: Uploading to BigQuery...")
print("-"*100)

table_id = "aialgotradehits.crypto_trading_data.stocks_daily_clean"
job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Replace existing data
)

print(f"Uploading to {table_id}...")
job = client.load_table_from_dataframe(upload_df, table_id, job_config=job_config)
job.result()

print("[OK] Upload complete!")
print("="*100)

# Step 5: Verify
print("\nStep 5: Verification...")
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
print("BASIC MIGRATION COMPLETE!")
print("="*100)
print("\nNote: Technical indicators (58 fields) are NULL")
print("Next step: Calculate indicators in separate process")
