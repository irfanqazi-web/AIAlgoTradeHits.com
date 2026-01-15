"""
Test indicator calculation WITH BigQuery upload on single symbol (AAPL)
This will test the complete flow including the MERGE
"""

from google.cloud import bigquery
import pandas as pd
import numpy as np
import pandas_ta as ta

client = bigquery.Client(project='aialgotradehits')

symbol = 'AAPL'

print(f"Testing FULL FLOW for {symbol} (with BigQuery upload)...")
print("="*80)

# Fetch data
query = f"""
SELECT *
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE symbol = '{symbol}'
ORDER BY datetime
"""

df = client.query(query).to_dataframe()
print(f"Fetched {len(df)} rows for {symbol}")

# Reset index
df = df.reset_index(drop=True)

print("\nCalculating indicators...")

# Calculate all indicators (same as main script)
# RSI
rsi_series = ta.rsi(df['close'], length=14)
if rsi_series is not None:
    df['rsi'] = rsi_series.values

# MACD
macd_result = ta.macd(df['close'], fast=12, slow=26, signal=9)
if macd_result is not None and not macd_result.empty:
    if len(macd_result.columns) >= 3:
        df['macd'] = macd_result.iloc[:, 0].values
        df['macd_signal'] = macd_result.iloc[:, 1].values
        df['macd_histogram'] = macd_result.iloc[:, 2].values

# SMA
sma20 = ta.sma(df['close'], length=20)
if sma20 is not None:
    df['sma_20'] = sma20.values

sma50 = ta.sma(df['close'], length=50)
if sma50 is not None:
    df['sma_50'] = sma50.values

sma200 = ta.sma(df['close'], length=200)
if sma200 is not None:
    df['sma_200'] = sma200.values

# Add flags
if 'rsi' in df.columns:
    df['rsi_overbought'] = (df['rsi'] > 70).fillna(0).astype('int64')
    df['rsi_oversold'] = (df['rsi'] < 30).fillna(0).astype('int64')

df['updated_at'] = pd.Timestamp.now()

print("[OK] Indicators calculated")

# Now test upload
print("\nTesting BigQuery upload...")

temp_table = f"aialgotradehits.crypto_trading_data.temp_TEST_AAPL"

indicator_columns = [
    'datetime', 'symbol',  # Keys
    'rsi', 'macd', 'macd_signal', 'macd_histogram',
    'sma_20', 'sma_50', 'sma_200',
    'rsi_overbought', 'rsi_oversold',
    'updated_at'
]

# Only upload indicator columns
upload_df = df[indicator_columns].copy()

print(f"Upload DataFrame shape: {upload_df.shape}")
print(f"Upload DataFrame columns: {upload_df.columns.tolist()}")
print(f"\nSample data:")
print(upload_df.tail(3))

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)

print("\nUploading to temp table...")
job = client.load_table_from_dataframe(upload_df, temp_table, job_config=job_config)
job.result()

print("[OK] Uploaded to temp table")

# Test MERGE
print("\nTesting MERGE query...")
merge_query = f"""
MERGE `aialgotradehits.crypto_trading_data.stocks_daily_clean` T
USING `{temp_table}` S
ON T.symbol = S.symbol AND T.datetime = S.datetime
WHEN MATCHED THEN
  UPDATE SET
    rsi = S.rsi,
    macd = S.macd,
    macd_signal = S.macd_signal,
    macd_histogram = S.macd_histogram,
    sma_20 = S.sma_20,
    sma_50 = S.sma_50,
    sma_200 = S.sma_200,
    rsi_overbought = S.rsi_overbought,
    rsi_oversold = S.rsi_oversold,
    updated_at = S.updated_at
"""

client.query(merge_query).result()

print("[OK] MERGE completed")

# Drop temp table
client.delete_table(temp_table, not_found_ok=True)

print("[OK] Temp table dropped")

# Verify results
print("\nVerifying results...")
verify_query = f"""
SELECT
    datetime, symbol, close, rsi, macd, sma_20, sma_50, sma_200,
    rsi_overbought, rsi_oversold
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE symbol = '{symbol}'
ORDER BY datetime DESC
LIMIT 5
"""

result = client.query(verify_query).result()
print("\nLatest 5 rows after MERGE:")
for row in result:
    print(f"  {row.datetime}: RSI={row.rsi:.2f if row.rsi else 'NULL'}, "
          f"SMA200={row.sma_200:.2f if row.sma_200 else 'NULL'}, "
          f"Overbought={row.rsi_overbought}")

print("\n" + "="*80)
print("[SUCCESS] Full flow test PASSED!")
print("="*80)
