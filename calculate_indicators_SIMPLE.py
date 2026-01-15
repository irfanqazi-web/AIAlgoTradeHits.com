"""
Simple version - Add MFI, CMF, Ichimoku only (skip VWAP and Volume Profile for now)
Fast execution - no complex calculations that require special index handling
"""

from google.cloud import bigquery
import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime
import time

client = bigquery.Client(project='aialgotradehits')

print("="*100)
print("ADD INSTITUTIONAL INDICATORS - MFI, CMF, ICHIMOKU")
print("="*100)

# Get symbols
query = "SELECT DISTINCT symbol FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean` ORDER BY symbol"
result = client.query(query).result()
symbols = [row.symbol for row in result]
total_symbols = len(symbols)

print(f"Processing {total_symbols} symbols...")
print("-"*100)

processed_count = 0
failed_symbols = []
start_time = time.time()

for i, symbol in enumerate(symbols, 1):
    try:
        # Fetch data
        query = f"""
        SELECT * FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
        WHERE symbol = '{symbol}'
        ORDER BY datetime
        """
        df = client.query(query).to_dataframe()

        if len(df) < 100:
            continue

        # Convert Int64 to regular int64
        for col in df.columns:
            if str(df[col].dtype) == 'Int64':
                df[col] = df[col].astype('float64').fillna(0).astype('int64')
        if 'volume' in df.columns:
            df['volume'] = df['volume'].astype('float64').fillna(0).astype('int64')

        # Calculate ONLY the simple indicators

        # MFI
        mfi_series = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14)
        if mfi_series is not None:
            df['mfi'] = mfi_series.values
        else:
            df['mfi'] = np.nan

        # CMF
        try:
            money_flow_multiplier = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
            money_flow_multiplier = money_flow_multiplier.fillna(0)
            money_flow_volume = money_flow_multiplier * df['volume']
            df['cmf'] = money_flow_volume.rolling(20).sum() / df['volume'].rolling(20).sum()
        except:
            df['cmf'] = np.nan

        # Ichimoku
        try:
            ichimoku_result = ta.ichimoku(df['high'], df['low'], df['close'])
            if ichimoku_result is not None:
                if isinstance(ichimoku_result, tuple):
                    ichimoku_result = ichimoku_result[0] if len(ichimoku_result) > 0 else None
                if ichimoku_result is not None and hasattr(ichimoku_result, 'columns'):
                    for col in ichimoku_result.columns:
                        if 'ISA' in col:
                            df['ichimoku_senkou_a'] = ichimoku_result[col].values
                        elif 'ISB' in col:
                            df['ichimoku_senkou_b'] = ichimoku_result[col].values
                        elif 'ITS' in col:
                            df['ichimoku_tenkan'] = ichimoku_result[col].values
                        elif 'IKS' in col:
                            df['ichimoku_kijun'] = ichimoku_result[col].values
                        elif 'ICS' in col:
                            df['ichimoku_chikou'] = ichimoku_result[col].values
        except:
            df['ichimoku_tenkan'] = np.nan
            df['ichimoku_kijun'] = np.nan
            df['ichimoku_senkou_a'] = np.nan
            df['ichimoku_senkou_b'] = np.nan
            df['ichimoku_chikou'] = np.nan

        df['updated_at'] = pd.Timestamp.now()

        # Upload only new columns
        temp_table = f"aialgotradehits.crypto_trading_data.temp_{symbol.replace('-', '_').replace('.', '_')}"
        upload_df = df[['datetime', 'symbol', 'mfi', 'cmf',
                        'ichimoku_tenkan', 'ichimoku_kijun', 'ichimoku_senkou_a',
                        'ichimoku_senkou_b', 'ichimoku_chikou', 'updated_at']].copy()

        job = client.load_table_from_dataframe(
            upload_df, temp_table,
            job_config=bigquery.LoadJobConfig(write_disposition='WRITE_TRUNCATE')
        )
        job.result()

        # Merge
        merge_query = f"""
        MERGE `aialgotradehits.crypto_trading_data.stocks_daily_clean` T
        USING `{temp_table}` S
        ON T.symbol = S.symbol AND T.datetime = S.datetime
        WHEN MATCHED THEN UPDATE SET
            mfi = S.mfi, cmf = S.cmf,
            ichimoku_tenkan = S.ichimoku_tenkan,
            ichimoku_kijun = S.ichimoku_kijun,
            ichimoku_senkou_a = S.ichimoku_senkou_a,
            ichimoku_senkou_b = S.ichimoku_senkou_b,
            ichimoku_chikou = S.ichimoku_chikou,
            updated_at = S.updated_at
        """
        client.query(merge_query).result()
        client.delete_table(temp_table, not_found_ok=True)

        processed_count += 1
        elapsed = time.time() - start_time
        print(f"[{i}/{total_symbols}] {symbol:8} - OK ({len(df)} rows) | Elapsed: {elapsed/60:.1f}m | Processed: {processed_count}")

    except Exception as e:
        print(f"[{i}/{total_symbols}] {symbol:8} - FAILED: {e}")
        failed_symbols.append((symbol, str(e)))

print("\n" + "="*100)
print(f"DONE! Processed: {processed_count}/{total_symbols} | Failed: {len(failed_symbols)}")
print(f"Time: {(time.time()-start_time)/60:.1f} minutes")
print("="*100)
