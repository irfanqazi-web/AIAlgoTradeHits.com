"""
Calculate ALL technical indicators for stocks_daily_clean table - ENHANCED VERSION
Adds 11 missing institutional indicators (MFI, CMF, Ichimoku-5, VWAP-2, VProfile-3)
Total indicators: 58 + 11 = 69 fields
Estimated time: 1.5-2 hours
"""

from google.cloud import bigquery
import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime
import time

client = bigquery.Client(project='aialgotradehits')

print("="*100)
print("CALCULATING TECHNICAL INDICATORS - ENHANCED WITH INSTITUTIONAL INDICATORS")
print("="*100)
print(f"Started: {datetime.now()}")

# Step 1: Get list of all symbols
print("\nStep 1: Getting symbol list...")
query = """
SELECT DISTINCT symbol
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
ORDER BY symbol
"""
result = client.query(query).result()
symbols = [row.symbol for row in result]
total_symbols = len(symbols)

print(f"[OK] Found {total_symbols} symbols to process")

# Step 2: Process each symbol
print("\nStep 2: Processing symbols...")
print("-"*100)

processed_count = 0
failed_symbols = []
start_time = time.time()

for i, symbol in enumerate(symbols, 1):
    symbol_start = time.time()

    try:
        # Fetch data for this symbol
        query = f"""
        SELECT *
        FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
        WHERE symbol = '{symbol}'
        ORDER BY datetime
        """

        df = client.query(query).to_dataframe()

        if len(df) < 100:
            print(f"  [{i}/{total_symbols}] {symbol:8} - SKIPPED (only {len(df)} rows, need 100+)")
            continue

        # Reset index to ensure clean integer index
        df = df.reset_index(drop=True)

        # FIX: Convert all nullable Int64 columns to regular int64
        for col in df.columns:
            if str(df[col].dtype) == 'Int64':
                df[col] = df[col].astype('float64').fillna(0).astype('int64')

        # Explicitly convert volume and average_volume
        if 'volume' in df.columns:
            df['volume'] = df['volume'].astype('float64').fillna(0).astype('int64')
        if 'average_volume' in df.columns:
            df['average_volume'] = df['average_volume'].astype('float64').fillna(0).astype('int64')

        # Calculate indicators with error handling
        try:
            # ================== MOMENTUM INDICATORS ==================

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

            # Stochastic
            stoch_result = ta.stoch(df['high'], df['low'], df['close'], k=14, d=3)
            if stoch_result is not None and not stoch_result.empty:
                if len(stoch_result.columns) >= 2:
                    df['stoch_k'] = stoch_result.iloc[:, 0].values
                    df['stoch_d'] = stoch_result.iloc[:, 1].values

            # CCI
            cci_series = ta.cci(df['high'], df['low'], df['close'], length=20)
            if cci_series is not None:
                df['cci'] = cci_series.values

            # Williams %R
            willr_series = ta.willr(df['high'], df['low'], df['close'], length=14)
            if willr_series is not None:
                df['williams_r'] = willr_series.values

            # Momentum
            mom_series = ta.mom(df['close'], length=10)
            if mom_series is not None:
                df['momentum'] = mom_series.values

            # ================== MOVING AVERAGES ==================

            # Simple Moving Averages
            sma20 = ta.sma(df['close'], length=20)
            if sma20 is not None:
                df['sma_20'] = sma20.values

            sma50 = ta.sma(df['close'], length=50)
            if sma50 is not None:
                df['sma_50'] = sma50.values

            sma200 = ta.sma(df['close'], length=200)
            if sma200 is not None:
                df['sma_200'] = sma200.values

            # Exponential Moving Averages
            ema12 = ta.ema(df['close'], length=12)
            if ema12 is not None:
                df['ema_12'] = ema12.values

            ema20 = ta.ema(df['close'], length=20)
            if ema20 is not None:
                df['ema_20'] = ema20.values

            ema26 = ta.ema(df['close'], length=26)
            if ema26 is not None:
                df['ema_26'] = ema26.values

            ema50 = ta.ema(df['close'], length=50)
            if ema50 is not None:
                df['ema_50'] = ema50.values

            ema200 = ta.ema(df['close'], length=200)
            if ema200 is not None:
                df['ema_200'] = ema200.values

            # KAMA
            kama_series = ta.kama(df['close'], length=10)
            if kama_series is not None:
                df['kama'] = kama_series.values

            # ================== BOLLINGER BANDS ==================

            bbands_result = ta.bbands(df['close'], length=20, std=2)
            if bbands_result is not None and not bbands_result.empty:
                if len(bbands_result.columns) >= 4:
                    df['bollinger_upper'] = bbands_result.iloc[:, 0].values
                    df['bollinger_middle'] = bbands_result.iloc[:, 1].values
                    df['bollinger_lower'] = bbands_result.iloc[:, 2].values
                    df['bb_width'] = bbands_result.iloc[:, 3].values

            # ================== ADX ==================

            adx_result = ta.adx(df['high'], df['low'], df['close'], length=14)
            if adx_result is not None and not adx_result.empty:
                if len(adx_result.columns) >= 3:
                    df['adx'] = adx_result.iloc[:, 0].values
                    df['plus_di'] = adx_result.iloc[:, 1].values
                    df['minus_di'] = adx_result.iloc[:, 2].values

            # ================== OTHER TREND/VOLATILITY ==================

            # ATR
            atr_series = ta.atr(df['high'], df['low'], df['close'], length=14)
            if atr_series is not None:
                df['atr'] = atr_series.values

            # TRIX
            trix_series = ta.trix(df['close'], length=15)
            if trix_series is not None:
                df['trix'] = trix_series.values

            # ROC
            roc_series = ta.roc(df['close'], length=10)
            if roc_series is not None:
                df['roc'] = roc_series.values

            # ================== VOLUME INDICATORS ==================

            # OBV
            obv_series = ta.obv(df['close'], df['volume'])
            if obv_series is not None:
                df['obv'] = obv_series.values

            # PVO
            pvo_series = ta.pvo(df['volume'], fast=12, slow=26)
            if pvo_series is not None:
                df['pvo'] = pvo_series.values

            # PPO
            ppo_series = ta.ppo(df['close'], fast=12, slow=26)
            if ppo_series is not None:
                df['ppo'] = ppo_series.values

            # ================== ADVANCED OSCILLATORS ==================

            # Ultimate Oscillator
            uo_series = ta.uo(df['high'], df['low'], df['close'])
            if uo_series is not None:
                df['ultimate_osc'] = uo_series.values

            # Awesome Oscillator
            ao_series = ta.ao(df['high'], df['low'])
            if ao_series is not None:
                df['awesome_osc'] = ao_series.values

            # ================== NEW INSTITUTIONAL INDICATORS ==================

            # 1. MFI (Money Flow Index) - 1 field
            mfi_series = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14)
            if mfi_series is not None:
                df['mfi'] = mfi_series.values

            # 2. CMF (Chaikin Money Flow) - 1 field
            # CMF = SUM((((Close - Low) - (High - Close)) / (High - Low)) * Volume, n) / SUM(Volume, n)
            # pandas_ta has ad (Accumulation/Distribution) but not CMF directly, so calculate manually
            try:
                money_flow_multiplier = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
                money_flow_multiplier = money_flow_multiplier.fillna(0)
                money_flow_volume = money_flow_multiplier * df['volume']
                cmf_period = 20
                df['cmf'] = money_flow_volume.rolling(cmf_period).sum() / df['volume'].rolling(cmf_period).sum()
            except:
                df['cmf'] = np.nan

            # 3. Ichimoku Cloud (5 components) - 5 fields
            try:
                ichimoku_result = ta.ichimoku(df['high'], df['low'], df['close'])
                # Handle both tuple and DataFrame returns
                if ichimoku_result is not None:
                    # If it's a tuple, unpack it (pandas_ta sometimes returns tuple of DataFrames)
                    if isinstance(ichimoku_result, tuple):
                        ichimoku_result = ichimoku_result[0] if len(ichimoku_result) > 0 else None

                    if ichimoku_result is not None and hasattr(ichimoku_result, 'columns') and not ichimoku_result.empty:
                        # Ichimoku returns multiple series: ISA_9, ISB_26, ITS_9, IKS_26, ICS_26
                        for col in ichimoku_result.columns:
                            if 'ISA' in col or 'SENKOU_A' in col:
                                df['ichimoku_senkou_a'] = ichimoku_result[col].values
                            elif 'ISB' in col or 'SENKOU_B' in col:
                                df['ichimoku_senkou_b'] = ichimoku_result[col].values
                            elif 'ITS' in col or 'TENKAN' in col:
                                df['ichimoku_tenkan'] = ichimoku_result[col].values
                            elif 'IKS' in col or 'KIJUN' in col:
                                df['ichimoku_kijun'] = ichimoku_result[col].values
                            elif 'ICS' in col or 'CHIKOU' in col:
                                df['ichimoku_chikou'] = ichimoku_result[col].values
            except Exception as ichimoku_error:
                # If Ichimoku fails, just set to NaN and continue
                df['ichimoku_tenkan'] = np.nan
                df['ichimoku_kijun'] = np.nan
                df['ichimoku_senkou_a'] = np.nan
                df['ichimoku_senkou_b'] = np.nan
                df['ichimoku_chikou'] = np.nan

            # 4. VWAP (Daily) - 1 field
            # For daily data, we calculate cumulative VWAP from the start of the data
            vwap_series = ta.vwap(df['high'], df['low'], df['close'], df['volume'])
            if vwap_series is not None:
                df['vwap_daily'] = vwap_series.values

            # 5. VWAP Weekly - 1 field
            # Calculate rolling 5-day (weekly) VWAP
            try:
                typical_price = (df['high'] + df['low'] + df['close']) / 3
                vwap_weekly_num = (typical_price * df['volume']).rolling(5).sum()
                vwap_weekly_denom = df['volume'].rolling(5).sum()
                df['vwap_weekly'] = vwap_weekly_num / vwap_weekly_denom
            except:
                df['vwap_weekly'] = np.nan

            # 6. Volume Profile (POC, VAH, VAL) - 3 fields
            # Volume Profile calculates price levels with highest volume (POC = Point of Control)
            # VAH = Value Area High, VAL = Value Area Low
            # This is complex for daily data, so we'll use a simplified rolling window approach
            try:
                rolling_window = 20  # 20-day rolling volume profile

                # For each row, calculate volume profile for past 20 days
                poc_list = []
                vah_list = []
                val_list = []

                for idx in range(len(df)):
                    if idx < rolling_window:
                        poc_list.append(np.nan)
                        vah_list.append(np.nan)
                        val_list.append(np.nan)
                        continue

                    # Get window data
                    window_df = df.iloc[idx-rolling_window:idx].copy()

                    # Create price bins (10 bins across price range)
                    price_min = window_df['low'].min()
                    price_max = window_df['high'].max()
                    n_bins = 10
                    bins = np.linspace(price_min, price_max, n_bins + 1)

                    # Calculate volume for each price bin
                    volume_by_price = np.zeros(n_bins)
                    for _, row in window_df.iterrows():
                        # Distribute volume across bins that the candle touches
                        bin_idx_low = np.searchsorted(bins, row['low']) - 1
                        bin_idx_high = np.searchsorted(bins, row['high']) - 1
                        bin_idx_low = max(0, min(bin_idx_low, n_bins - 1))
                        bin_idx_high = max(0, min(bin_idx_high, n_bins - 1))

                        for b in range(bin_idx_low, bin_idx_high + 1):
                            volume_by_price[b] += row['volume'] / (bin_idx_high - bin_idx_low + 1)

                    # POC = price level with highest volume
                    poc_bin = np.argmax(volume_by_price)
                    poc_price = (bins[poc_bin] + bins[poc_bin + 1]) / 2
                    poc_list.append(poc_price)

                    # VAH/VAL = 70% value area around POC
                    total_volume = volume_by_price.sum()
                    target_volume = total_volume * 0.70

                    # Find value area by expanding from POC
                    current_volume = volume_by_price[poc_bin]
                    lower_bin = poc_bin
                    upper_bin = poc_bin

                    while current_volume < target_volume and (lower_bin > 0 or upper_bin < n_bins - 1):
                        # Expand to higher or lower bin based on which has more volume
                        can_go_lower = lower_bin > 0
                        can_go_higher = upper_bin < n_bins - 1

                        vol_lower = volume_by_price[lower_bin - 1] if can_go_lower else 0
                        vol_higher = volume_by_price[upper_bin + 1] if can_go_higher else 0

                        if can_go_higher and (vol_higher >= vol_lower or not can_go_lower):
                            upper_bin += 1
                            current_volume += volume_by_price[upper_bin]
                        elif can_go_lower:
                            lower_bin -= 1
                            current_volume += volume_by_price[lower_bin]
                        else:
                            break

                    vah_price = bins[upper_bin + 1]  # Upper edge of upper bin
                    val_price = bins[lower_bin]      # Lower edge of lower bin

                    vah_list.append(vah_price)
                    val_list.append(val_price)

                df['volume_profile_poc'] = poc_list
                df['volume_profile_vah'] = vah_list
                df['volume_profile_val'] = val_list

            except Exception as vp_error:
                print(f"    Warning: Volume Profile calculation failed: {vp_error}")
                df['volume_profile_poc'] = np.nan
                df['volume_profile_vah'] = np.nan
                df['volume_profile_val'] = np.nan

            # ================== ML FEATURES - RETURNS ==================

            df['log_return'] = np.log(df['close'] / df['close'].shift(1))
            df['return_2w'] = (df['close'].shift(-10) - df['close']) / df['close'] * 100
            df['return_4w'] = (df['close'].shift(-20) - df['close']) / df['close'] * 100

            # ================== ML FEATURES - RELATIVE POSITIONS ==================

            if 'sma_20' in df.columns:
                df['close_vs_sma20_pct'] = (df['close'] - df['sma_20']) / df['sma_20'] * 100
            if 'sma_50' in df.columns:
                df['close_vs_sma50_pct'] = (df['close'] - df['sma_50']) / df['sma_50'] * 100
            if 'sma_200' in df.columns:
                df['close_vs_sma200_pct'] = (df['close'] - df['sma_200']) / df['sma_200'] * 100

            # ================== ML FEATURES - INDICATOR DYNAMICS ==================

            if 'rsi' in df.columns:
                df['rsi_slope'] = df['rsi'].diff(5)
                df['rsi_zscore'] = (df['rsi'] - df['rsi'].rolling(20).mean()) / df['rsi'].rolling(20).std()
                df['rsi_overbought'] = (df['rsi'] > 70).fillna(0).astype('int64')
                df['rsi_oversold'] = (df['rsi'] < 30).fillna(0).astype('int64')

            if 'macd' in df.columns and 'macd_signal' in df.columns:
                df['macd_cross'] = np.where(
                    (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1)), 1,
                    np.where((df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1)), -1, 0)
                )
                df['macd_cross'] = pd.Series(df['macd_cross']).fillna(0).astype('int64')

            if 'ema_20' in df.columns:
                df['ema20_slope'] = df['ema_20'].diff(5)
            if 'ema_50' in df.columns:
                df['ema50_slope'] = df['ema_50'].diff(5)

            if 'atr' in df.columns:
                df['atr_zscore'] = (df['atr'] - df['atr'].rolling(20).mean()) / df['atr'].rolling(20).std()
                df['atr_slope'] = df['atr'].diff(5)

            df['volume_zscore'] = (df['volume'] - df['volume'].rolling(20).mean()) / df['volume'].rolling(20).std()

            if 'average_volume' in df.columns:
                df['volume_ratio'] = df['volume'] / df['average_volume']

            # ================== ML FEATURES - MARKET STRUCTURE ==================

            df['pivot_high_flag'] = ((df['high'] > df['high'].shift(1)) &
                                      (df['high'] > df['high'].shift(2)) &
                                      (df['high'] > df['high'].shift(-1)) &
                                      (df['high'] > df['high'].shift(-2))).fillna(0).astype('int64')

            df['pivot_low_flag'] = ((df['low'] < df['low'].shift(1)) &
                                     (df['low'] < df['low'].shift(2)) &
                                     (df['low'] < df['low'].shift(-1)) &
                                     (df['low'] < df['low'].shift(-2))).fillna(0).astype('int64')

            df['dist_to_pivot_high'] = df['close'] - df['high'].where(df['pivot_high_flag'] == 1).ffill()
            df['dist_to_pivot_low'] = df['close'] - df['low'].where(df['pivot_low_flag'] == 1).ffill()

            # ================== ML FEATURES - REGIME DETECTION ==================

            if 'sma_50' in df.columns:
                sma_50_slope = df['sma_50'].diff(20)
                df['trend_regime'] = np.where(sma_50_slope > 0, 1, np.where(sma_50_slope < 0, -1, 0))
                df['trend_regime'] = pd.Series(df['trend_regime']).fillna(0).astype('int64')
                df['regime_confidence'] = abs(sma_50_slope) / df['sma_50'].rolling(20).std()

            if 'atr' in df.columns:
                atr_20_mean = df['atr'].rolling(20).mean()
                df['vol_regime'] = (df['atr'] > atr_20_mean).fillna(0).astype('int64')

            # Update timestamp
            df['updated_at'] = pd.Timestamp.now()

        except Exception as calc_error:
            print(f"  [{i}/{total_symbols}] {symbol:8} - ERROR in calculations: {calc_error}")
            failed_symbols.append((symbol, str(calc_error)))
            continue

        # Upload using temp table and merge
        temp_table = f"aialgotradehits.crypto_trading_data.temp_{symbol.replace('-', '_').replace('.', '_')}"

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )

        # All indicator fields including the new 11 institutional indicators
        indicator_columns = [
            'datetime', 'symbol',  # Keys for matching
            # Standard indicators (existing 58)
            'rsi', 'macd', 'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'cci', 'williams_r', 'momentum',
            'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_20', 'ema_26', 'ema_50', 'ema_200', 'kama',
            'bollinger_upper', 'bollinger_middle', 'bollinger_lower', 'bb_width',
            'adx', 'plus_di', 'minus_di', 'atr', 'trix', 'roc',
            'obv', 'pvo', 'ppo', 'ultimate_osc', 'awesome_osc',
            # NEW: Institutional indicators (11 fields)
            'mfi', 'cmf',
            'ichimoku_tenkan', 'ichimoku_kijun', 'ichimoku_senkou_a', 'ichimoku_senkou_b', 'ichimoku_chikou',
            'vwap_daily', 'vwap_weekly',
            'volume_profile_poc', 'volume_profile_vah', 'volume_profile_val',
            # ML features
            'log_return', 'return_2w', 'return_4w',
            'close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct',
            'rsi_slope', 'rsi_zscore', 'rsi_overbought', 'rsi_oversold', 'macd_cross',
            'ema20_slope', 'ema50_slope', 'atr_zscore', 'atr_slope', 'volume_zscore', 'volume_ratio',
            'pivot_high_flag', 'pivot_low_flag', 'dist_to_pivot_high', 'dist_to_pivot_low',
            'trend_regime', 'vol_regime', 'regime_confidence',
            'updated_at'
        ]

        # Only upload these columns
        upload_df = df[indicator_columns].copy()

        job = client.load_table_from_dataframe(upload_df, temp_table, job_config=job_config)
        job.result()

        # Merge back to main table (MERGE will auto-add new columns)
        merge_query = f"""
        MERGE `aialgotradehits.crypto_trading_data.stocks_daily_clean` T
        USING `{temp_table}` S
        ON T.symbol = S.symbol AND T.datetime = S.datetime
        WHEN MATCHED THEN
          UPDATE SET
            rsi = S.rsi, macd = S.macd, macd_signal = S.macd_signal, macd_histogram = S.macd_histogram,
            stoch_k = S.stoch_k, stoch_d = S.stoch_d, cci = S.cci, williams_r = S.williams_r, momentum = S.momentum,
            sma_20 = S.sma_20, sma_50 = S.sma_50, sma_200 = S.sma_200,
            ema_12 = S.ema_12, ema_20 = S.ema_20, ema_26 = S.ema_26, ema_50 = S.ema_50, ema_200 = S.ema_200, kama = S.kama,
            bollinger_upper = S.bollinger_upper, bollinger_middle = S.bollinger_middle, bollinger_lower = S.bollinger_lower, bb_width = S.bb_width,
            adx = S.adx, plus_di = S.plus_di, minus_di = S.minus_di, atr = S.atr, trix = S.trix, roc = S.roc,
            obv = S.obv, pvo = S.pvo, ppo = S.ppo, ultimate_osc = S.ultimate_osc, awesome_osc = S.awesome_osc,
            mfi = S.mfi, cmf = S.cmf,
            ichimoku_tenkan = S.ichimoku_tenkan, ichimoku_kijun = S.ichimoku_kijun,
            ichimoku_senkou_a = S.ichimoku_senkou_a, ichimoku_senkou_b = S.ichimoku_senkou_b, ichimoku_chikou = S.ichimoku_chikou,
            vwap_daily = S.vwap_daily, vwap_weekly = S.vwap_weekly,
            volume_profile_poc = S.volume_profile_poc, volume_profile_vah = S.volume_profile_vah, volume_profile_val = S.volume_profile_val,
            log_return = S.log_return, return_2w = S.return_2w, return_4w = S.return_4w,
            close_vs_sma20_pct = S.close_vs_sma20_pct, close_vs_sma50_pct = S.close_vs_sma50_pct, close_vs_sma200_pct = S.close_vs_sma200_pct,
            rsi_slope = S.rsi_slope, rsi_zscore = S.rsi_zscore, rsi_overbought = S.rsi_overbought, rsi_oversold = S.rsi_oversold, macd_cross = S.macd_cross,
            ema20_slope = S.ema20_slope, ema50_slope = S.ema50_slope, atr_zscore = S.atr_zscore, atr_slope = S.atr_slope,
            volume_zscore = S.volume_zscore, volume_ratio = S.volume_ratio,
            pivot_high_flag = S.pivot_high_flag, pivot_low_flag = S.pivot_low_flag,
            dist_to_pivot_high = S.dist_to_pivot_high, dist_to_pivot_low = S.dist_to_pivot_low,
            trend_regime = S.trend_regime, vol_regime = S.vol_regime, regime_confidence = S.regime_confidence,
            updated_at = S.updated_at
        """

        client.query(merge_query).result()

        # Drop temp table
        client.delete_table(temp_table, not_found_ok=True)

        processed_count += 1
        symbol_time = time.time() - symbol_start
        elapsed = time.time() - start_time
        avg_time = elapsed / processed_count
        remaining = (total_symbols - i) * avg_time

        print(f"  [{i}/{total_symbols}] {symbol:8} - OK ({len(df):,} rows, {symbol_time:.1f}s) | "
              f"Elapsed: {elapsed/60:.1f}m | ETA: {remaining/60:.1f}m")

    except Exception as e:
        print(f"  [{i}/{total_symbols}] {symbol:8} - FAILED: {e}")
        failed_symbols.append((symbol, str(e)))

print("\n" + "="*100)
print("CALCULATION COMPLETE!")
print("="*100)
print(f"Finished: {datetime.now()}")
print(f"Total time: {(time.time() - start_time)/60:.1f} minutes")
print(f"Processed: {processed_count}/{total_symbols} symbols")
print(f"Failed: {len(failed_symbols)} symbols")

if failed_symbols:
    print("\nFailed symbols:")
    for symbol, error in failed_symbols[:20]:
        print(f"  - {symbol}: {error[:80]}")
    if len(failed_symbols) > 20:
        print(f"  ... and {len(failed_symbols) - 20} more")

print("\n" + "="*100)
print("Validating results...")

# Validation including new indicators
validation_query = """
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT symbol) as unique_symbols,
    COUNTIF(rsi IS NOT NULL) as rows_with_rsi,
    COUNTIF(macd IS NOT NULL) as rows_with_macd,
    COUNTIF(sma_200 IS NOT NULL) as rows_with_sma200,
    COUNTIF(bollinger_upper IS NOT NULL) as rows_with_bbands
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
"""

try:
    result = client.query(validation_query).result()
    for row in result:
        print(f"Total rows: {row.total_rows:,}")
        print(f"Symbols: {row.unique_symbols}")
        print(f"Rows with RSI: {row.rows_with_rsi:,} ({row.rows_with_rsi/row.total_rows*100:.1f}%)")
        print(f"Rows with MACD: {row.rows_with_macd:,} ({row.rows_with_macd/row.total_rows*100:.1f}%)")
        print(f"Rows with SMA200: {row.rows_with_sma200:,} ({row.rows_with_sma200/row.total_rows*100:.1f}%)")
        print(f"Rows with Bollinger: {row.rows_with_bbands:,} ({row.rows_with_bbands/row.total_rows*100:.1f}%)")

        # Try to check new indicators if they exist
        try:
            new_indicator_query = """
            SELECT
                COUNTIF(mfi IS NOT NULL) as rows_with_mfi,
                COUNTIF(cmf IS NOT NULL) as rows_with_cmf,
                COUNTIF(ichimoku_tenkan IS NOT NULL) as rows_with_ichimoku,
                COUNTIF(vwap_daily IS NOT NULL) as rows_with_vwap,
                COUNTIF(volume_profile_poc IS NOT NULL) as rows_with_vprofile
            FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
            """
            new_result = client.query(new_indicator_query).result()
            for new_row in new_result:
                print(f"\n--- NEW INSTITUTIONAL INDICATORS ---")
                print(f"Rows with MFI: {new_row.rows_with_mfi:,} ({new_row.rows_with_mfi/row.total_rows*100:.1f}%)")
                print(f"Rows with CMF: {new_row.rows_with_cmf:,} ({new_row.rows_with_cmf/row.total_rows*100:.1f}%)")
                print(f"Rows with Ichimoku: {new_row.rows_with_ichimoku:,} ({new_row.rows_with_ichimoku/row.total_rows*100:.1f}%)")
                print(f"Rows with VWAP: {new_row.rows_with_vwap:,} ({new_row.rows_with_vwap/row.total_rows*100:.1f}%)")
                print(f"Rows with Volume Profile: {new_row.rows_with_vprofile:,} ({new_row.rows_with_vprofile/row.total_rows*100:.1f}%)")
        except:
            print("\nNew institutional indicators not yet in schema (will be added on first successful update)")

except Exception as e:
    print(f"Validation query failed: {e}")

print("="*100)
print("ALL DONE! Enhanced with 11 institutional indicators")
print("Total indicators: 69 fields (58 standard + 11 institutional)")
