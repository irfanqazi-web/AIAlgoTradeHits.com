"""
Test indicator calculation on single symbol (AAPL) to verify fix
"""

from google.cloud import bigquery
import pandas as pd
import numpy as np
import pandas_ta as ta

client = bigquery.Client(project='aialgotradehits')

symbol = 'AAPL'

print(f"Testing indicator calculation for {symbol}...")
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

try:
    # RSI
    rsi_series = ta.rsi(df['close'], length=14)
    if rsi_series is not None:
        df['rsi'] = rsi_series.values
        print(f"[OK] RSI: {df['rsi'].notna().sum()} non-null values")

    # MACD
    macd_result = ta.macd(df['close'], fast=12, slow=26, signal=9)
    if macd_result is not None and not macd_result.empty:
        if len(macd_result.columns) >= 3:
            df['macd'] = macd_result.iloc[:, 0].values
            df['macd_signal'] = macd_result.iloc[:, 1].values
            df['macd_histogram'] = macd_result.iloc[:, 2].values
            print(f"[OK] MACD: {df['macd'].notna().sum()} non-null values")

    # SMA 20
    sma20 = ta.sma(df['close'], length=20)
    if sma20 is not None:
        df['sma_20'] = sma20.values
        print(f"[OK] SMA 20: {df['sma_20'].notna().sum()} non-null values")

    # SMA 50
    sma50 = ta.sma(df['close'], length=50)
    if sma50 is not None:
        df['sma_50'] = sma50.values
        print(f"[OK] SMA 50: {df['sma_50'].notna().sum()} non-null values")

    # SMA 200
    sma200 = ta.sma(df['close'], length=200)
    if sma200 is not None:
        df['sma_200'] = sma200.values
        print(f"[OK] SMA 200: {df['sma_200'].notna().sum()} non-null values")

    # Bollinger Bands
    bbands_result = ta.bbands(df['close'], length=20, std=2)
    if bbands_result is not None and not bbands_result.empty:
        if len(bbands_result.columns) >= 4:
            df['bollinger_upper'] = bbands_result.iloc[:, 0].values
            df['bollinger_middle'] = bbands_result.iloc[:, 1].values
            df['bollinger_lower'] = bbands_result.iloc[:, 2].values
            df['bb_width'] = bbands_result.iloc[:, 3].values
            print(f"[OK] Bollinger Bands: {df['bollinger_upper'].notna().sum()} non-null values")

    # ML Features
    df['close_vs_sma20_pct'] = (df['close'] - df['sma_20']) / df['sma_20'] * 100
    print(f"[OK] close_vs_sma20_pct: {df['close_vs_sma20_pct'].notna().sum()} non-null values")

    # Check latest 10 rows
    print("\nLatest 10 rows with indicators:")
    print(df[['datetime', 'symbol', 'close', 'rsi', 'macd', 'sma_20', 'sma_50', 'sma_200', 'bollinger_upper']].tail(10))

    print("\n" + "="*80)
    print("[SUCCESS] TEST PASSED! All indicators calculated successfully.")
    print(f"Total rows: {len(df)}")
    print(f"RSI not null: {df['rsi'].notna().sum()} ({df['rsi'].notna().sum()/len(df)*100:.1f}%)")
    print(f"MACD not null: {df['macd'].notna().sum()} ({df['macd'].notna().sum()/len(df)*100:.1f}%)")
    print(f"SMA200 not null: {df['sma_200'].notna().sum()} ({df['sma_200'].notna().sum()/len(df)*100:.1f}%)")

except Exception as e:
    print(f"\n[FAILED] TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
