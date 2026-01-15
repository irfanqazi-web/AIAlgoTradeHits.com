"""
PROPERLY FIXED VERSION - Add 11 institutional indicators with correct DatetimeIndex handling
- Sets datetime as index BEFORE VWAP calculation
- Resets index AFTER VWAP calculation
- Handles all indicator edge cases properly
"""

from google.cloud import bigquery
import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime
import time

client = bigquery.Client(project='aialgotradehits')

print("="*100)
print("ADD INSTITUTIONAL INDICATORS - PROPER VERSION WITH DATETIMEINDEX")
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
            print(f"[{i}/{total_symbols}] {symbol:8} - SKIPPED (only {len(df)} rows, need 100+)")
            continue

        # Convert Int64 to regular int64 to avoid pandas_ta issues
        for col in df.columns:
            if str(df[col].dtype) == 'Int64':
                df[col] = df[col].astype('float64').fillna(0).astype('int64')
        if 'volume' in df.columns:
            df['volume'] = df['volume'].astype('float64').fillna(0).astype('int64')

        # ===========================================
        # 1. MFI (Money Flow Index)
        # ===========================================
        try:
            mfi_series = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14)
            if mfi_series is not None:
                df['mfi'] = mfi_series.values
            else:
                df['mfi'] = np.nan
        except Exception as e:
            df['mfi'] = np.nan
            print(f"    MFI calculation failed: {e}")

        # ===========================================
        # 2. CMF (Chaikin Money Flow)
        # ===========================================
        try:
            money_flow_multiplier = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
            money_flow_multiplier = money_flow_multiplier.fillna(0)
            money_flow_volume = money_flow_multiplier * df['volume']
            df['cmf'] = money_flow_volume.rolling(20).sum() / df['volume'].rolling(20).sum()
        except Exception as e:
            df['cmf'] = np.nan
            print(f"    CMF calculation failed: {e}")

        # ===========================================
        # 3. Ichimoku Cloud (5 components)
        # ===========================================
        try:
            ichimoku_result = ta.ichimoku(df['high'], df['low'], df['close'])
            if ichimoku_result is not None:
                # Handle tuple return
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
                else:
                    raise ValueError("Ichimoku result is not a DataFrame")
            else:
                raise ValueError("Ichimoku returned None")
        except Exception as e:
            df['ichimoku_tenkan'] = np.nan
            df['ichimoku_kijun'] = np.nan
            df['ichimoku_senkou_a'] = np.nan
            df['ichimoku_senkou_b'] = np.nan
            df['ichimoku_chikou'] = np.nan
            print(f"    Ichimoku calculation failed: {e}")

        # ===========================================
        # 4. VWAP - THE PROPER WAY WITH DATETIMEINDEX
        # ===========================================
        try:
            # CRITICAL: Set datetime as index BEFORE VWAP calculation
            df_vwap = df.copy()
            df_vwap.set_index('datetime', inplace=True)

            # Now calculate VWAP with DatetimeIndex
            vwap_result = ta.vwap(df_vwap['high'], df_vwap['low'], df_vwap['close'], df_vwap['volume'])

            if vwap_result is not None:
                # Daily VWAP
                df['vwap_daily'] = vwap_result.values

                # Weekly VWAP (5-day rolling average of VWAP)
                df['vwap_weekly'] = pd.Series(vwap_result.values).rolling(5).mean().values
            else:
                df['vwap_daily'] = np.nan
                df['vwap_weekly'] = np.nan
        except Exception as e:
            df['vwap_daily'] = np.nan
            df['vwap_weekly'] = np.nan
            print(f"    VWAP calculation failed: {e}")

        # ===========================================
        # 5. Volume Profile (POC, VAH, VAL)
        # ===========================================
        try:
            # Simple 20-day rolling volume profile
            window = 20
            if len(df) >= window:
                poc_list = []
                vah_list = []
                val_list = []

                for idx in range(len(df)):
                    if idx < window - 1:
                        poc_list.append(np.nan)
                        vah_list.append(np.nan)
                        val_list.append(np.nan)
                    else:
                        window_df = df.iloc[idx-window+1:idx+1]

                        # Create 10 price bins
                        price_min = window_df['low'].min()
                        price_max = window_df['high'].max()
                        price_range = price_max - price_min

                        if price_range > 0:
                            bins = np.linspace(price_min, price_max, 11)
                            bin_volumes = np.zeros(10)

                            # Accumulate volume in each bin
                            for _, row in window_df.iterrows():
                                bin_idx = min(9, int((row['close'] - price_min) / price_range * 10))
                                bin_volumes[bin_idx] += row['volume']

                            # POC = price level with highest volume
                            poc_bin_idx = np.argmax(bin_volumes)
                            poc_price = (bins[poc_bin_idx] + bins[poc_bin_idx + 1]) / 2
                            poc_list.append(poc_price)

                            # VAH/VAL = 70% value area boundaries
                            cumsum = np.cumsum(bin_volumes)
                            total_volume = cumsum[-1]
                            target_volume = total_volume * 0.7

                            # Find VAL (lower boundary)
                            val_idx = 0
                            for j in range(10):
                                if cumsum[j] >= total_volume * 0.15:
                                    val_idx = j
                                    break
                            val_price = (bins[val_idx] + bins[val_idx + 1]) / 2
                            val_list.append(val_price)

                            # Find VAH (upper boundary)
                            vah_idx = 9
                            for j in range(9, -1, -1):
                                if (total_volume - cumsum[j]) >= total_volume * 0.15:
                                    vah_idx = j
                                    break
                            vah_price = (bins[vah_idx] + bins[vah_idx + 1]) / 2
                            vah_list.append(vah_price)
                        else:
                            poc_list.append(window_df['close'].iloc[-1])
                            vah_list.append(window_df['high'].max())
                            val_list.append(window_df['low'].min())

                df['volume_profile_poc'] = poc_list
                df['volume_profile_vah'] = vah_list
                df['volume_profile_val'] = val_list
            else:
                df['volume_profile_poc'] = np.nan
                df['volume_profile_vah'] = np.nan
                df['volume_profile_val'] = np.nan
        except Exception as e:
            df['volume_profile_poc'] = np.nan
            df['volume_profile_vah'] = np.nan
            df['volume_profile_val'] = np.nan
            print(f"    Volume Profile calculation failed: {e}")

        # Add timestamp
        df['updated_at'] = pd.Timestamp.now()

        # Upload only new columns to temp table
        temp_table = f"aialgotradehits.crypto_trading_data.temp_{symbol.replace('-', '_').replace('.', '_')}"
        upload_df = df[['datetime', 'symbol',
                        'mfi', 'cmf',
                        'ichimoku_tenkan', 'ichimoku_kijun',
                        'ichimoku_senkou_a', 'ichimoku_senkou_b', 'ichimoku_chikou',
                        'vwap_daily', 'vwap_weekly',
                        'volume_profile_poc', 'volume_profile_vah', 'volume_profile_val',
                        'updated_at']].copy()

        job = client.load_table_from_dataframe(
            upload_df, temp_table,
            job_config=bigquery.LoadJobConfig(write_disposition='WRITE_TRUNCATE')
        )
        job.result()

        # Merge back to main table
        merge_query = f"""
        MERGE `aialgotradehits.crypto_trading_data.stocks_daily_clean` T
        USING `{temp_table}` S
        ON T.symbol = S.symbol AND T.datetime = S.datetime
        WHEN MATCHED THEN UPDATE SET
            mfi = S.mfi,
            cmf = S.cmf,
            ichimoku_tenkan = S.ichimoku_tenkan,
            ichimoku_kijun = S.ichimoku_kijun,
            ichimoku_senkou_a = S.ichimoku_senkou_a,
            ichimoku_senkou_b = S.ichimoku_senkou_b,
            ichimoku_chikou = S.ichimoku_chikou,
            vwap_daily = S.vwap_daily,
            vwap_weekly = S.vwap_weekly,
            volume_profile_poc = S.volume_profile_poc,
            volume_profile_vah = S.volume_profile_vah,
            volume_profile_val = S.volume_profile_val,
            updated_at = S.updated_at
        """
        client.query(merge_query).result()
        client.delete_table(temp_table, not_found_ok=True)

        processed_count += 1
        elapsed = time.time() - start_time
        avg_time = elapsed / processed_count
        remaining = (total_symbols - processed_count) * avg_time
        print(f"[{i}/{total_symbols}] {symbol:8} - OK ({len(df)} rows) | Elapsed: {elapsed/60:.1f}m | ETA: {remaining/60:.1f}m | Processed: {processed_count}")

    except Exception as e:
        print(f"[{i}/{total_symbols}] {symbol:8} - FAILED: {e}")
        failed_symbols.append((symbol, str(e)))

print("\n" + "="*100)
print(f"DONE! Processed: {processed_count}/{total_symbols} | Failed: {len(failed_symbols)}")
print(f"Total Time: {(time.time()-start_time)/60:.1f} minutes")
if failed_symbols:
    print("\nFailed Symbols:")
    for sym, err in failed_symbols[:10]:
        print(f"  - {sym}: {err}")
print("="*100)
