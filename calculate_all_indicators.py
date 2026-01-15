"""
Calculate ALL technical indicators for stocks_daily_clean table
Processes all 262 symbols, all 1.14M rows
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
print("CALCULATING TECHNICAL INDICATORS FOR ALL DATA")
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

        if len(df) < 200:
            print(f"  [{i}/{total_symbols}] {symbol:8} - SKIPPED (only {len(df)} rows, need 200+)")
            continue

        # Calculate indicators with error handling
        try:
            # Momentum Indicators
            df['rsi'] = ta.rsi(df['close'], length=14)

            # MACD
            macd_result = ta.macd(df['close'], fast=12, slow=26, signal=9)
            if macd_result is not None and not macd_result.empty:
                # Handle different possible column names
                macd_cols = macd_result.columns.tolist()
                if len(macd_cols) >= 3:
                    df['macd'] = macd_result.iloc[:, 0]
                    df['macd_signal'] = macd_result.iloc[:, 1]
                    df['macd_histogram'] = macd_result.iloc[:, 2]

            # Stochastic
            stoch_result = ta.stoch(df['high'], df['low'], df['close'], k=14, d=3)
            if stoch_result is not None and not stoch_result.empty:
                stoch_cols = stoch_result.columns.tolist()
                if len(stoch_cols) >= 2:
                    df['stoch_k'] = stoch_result.iloc[:, 0]
                    df['stoch_d'] = stoch_result.iloc[:, 1]

            df['cci'] = ta.cci(df['high'], df['low'], df['close'], length=20)
            df['williams_r'] = ta.willr(df['high'], df['low'], df['close'], length=14)
            df['momentum'] = ta.mom(df['close'], length=10)

            # Moving Averages
            df['sma_20'] = ta.sma(df['close'], length=20)
            df['sma_50'] = ta.sma(df['close'], length=50)
            df['sma_200'] = ta.sma(df['close'], length=200)
            df['ema_12'] = ta.ema(df['close'], length=12)
            df['ema_20'] = ta.ema(df['close'], length=20)
            df['ema_26'] = ta.ema(df['close'], length=26)
            df['ema_50'] = ta.ema(df['close'], length=50)
            df['ema_200'] = ta.ema(df['close'], length=200)
            df['kama'] = ta.kama(df['close'], length=10)

            # Bollinger Bands - handle different column naming
            bbands_result = ta.bbands(df['close'], length=20, std=2)
            if bbands_result is not None and not bbands_result.empty:
                bb_cols = bbands_result.columns.tolist()
                if len(bb_cols) >= 4:
                    df['bollinger_upper'] = bbands_result.iloc[:, 0]
                    df['bollinger_middle'] = bbands_result.iloc[:, 1]
                    df['bollinger_lower'] = bbands_result.iloc[:, 2]
                    df['bb_width'] = bbands_result.iloc[:, 3]

            # ADX
            adx_result = ta.adx(df['high'], df['low'], df['close'], length=14)
            if adx_result is not None and not adx_result.empty:
                adx_cols = adx_result.columns.tolist()
                if len(adx_cols) >= 3:
                    df['adx'] = adx_result.iloc[:, 0]
                    df['plus_di'] = adx_result.iloc[:, 1]
                    df['minus_di'] = adx_result.iloc[:, 2]

            df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
            df['trix'] = ta.trix(df['close'], length=15)
            df['roc'] = ta.roc(df['close'], length=10)

            # Volume Indicators
            df['obv'] = ta.obv(df['close'], df['volume'])
            df['pvo'] = ta.pvo(df['volume'], fast=12, slow=26)
            df['ppo'] = ta.ppo(df['close'], fast=12, slow=26)

            # Advanced Oscillators
            df['ultimate_osc'] = ta.uo(df['high'], df['low'], df['close'])
            df['awesome_osc'] = ta.ao(df['high'], df['low'])

            # ML Features - Returns
            df['log_return'] = np.log(df['close'] / df['close'].shift(1))
            df['return_2w'] = (df['close'].shift(-10) - df['close']) / df['close'] * 100
            df['return_4w'] = (df['close'].shift(-20) - df['close']) / df['close'] * 100

            # ML Features - Relative Positions
            df['close_vs_sma20_pct'] = (df['close'] - df['sma_20']) / df['sma_20'] * 100
            df['close_vs_sma50_pct'] = (df['close'] - df['sma_50']) / df['sma_50'] * 100
            df['close_vs_sma200_pct'] = (df['close'] - df['sma_200']) / df['sma_200'] * 100

            # ML Features - Indicator Dynamics
            df['rsi_slope'] = df['rsi'].diff(5)
            df['rsi_zscore'] = (df['rsi'] - df['rsi'].rolling(20).mean()) / df['rsi'].rolling(20).std()
            df['rsi_overbought'] = (df['rsi'] > 70).astype('Int64')
            df['rsi_oversold'] = (df['rsi'] < 30).astype('Int64')
            df['macd_cross'] = np.where(
                (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1)), 1,
                np.where((df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1)), -1, 0)
            )
            df['macd_cross'] = df['macd_cross'].astype('Int64')

            df['ema20_slope'] = df['ema_20'].diff(5)
            df['ema50_slope'] = df['ema_50'].diff(5)
            df['atr_zscore'] = (df['atr'] - df['atr'].rolling(20).mean()) / df['atr'].rolling(20).std()
            df['atr_slope'] = df['atr'].diff(5)
            df['volume_zscore'] = (df['volume'] - df['volume'].rolling(20).mean()) / df['volume'].rolling(20).std()
            df['volume_ratio'] = df['volume'] / df['average_volume']

            # ML Features - Market Structure
            df['pivot_high_flag'] = ((df['high'] > df['high'].shift(1)) &
                                      (df['high'] > df['high'].shift(2)) &
                                      (df['high'] > df['high'].shift(-1)) &
                                      (df['high'] > df['high'].shift(-2))).astype('Int64')
            df['pivot_low_flag'] = ((df['low'] < df['low'].shift(1)) &
                                     (df['low'] < df['low'].shift(2)) &
                                     (df['low'] < df['low'].shift(-1)) &
                                     (df['low'] < df['low'].shift(-2))).astype('Int64')
            df['dist_to_pivot_high'] = df['close'] - df['high'].where(df['pivot_high_flag'] == 1).ffill()
            df['dist_to_pivot_low'] = df['close'] - df['low'].where(df['pivot_low_flag'] == 1).ffill()

            # Distance to pivot as percentage of close price
            last_pivot_high = df['high'].where(df['pivot_high_flag'] == 1).ffill()
            last_pivot_low = df['low'].where(df['pivot_low_flag'] == 1).ffill()
            df['dist_to_pivot_high_pct'] = (df['close'] - last_pivot_high) / df['close'] * 100
            df['dist_to_pivot_low_pct'] = (df['close'] - last_pivot_low) / df['close'] * 100

            # ML Features - Regime Detection
            sma_50_slope = df['sma_50'].diff(20)
            df['trend_regime'] = np.where(sma_50_slope > 0, 1, np.where(sma_50_slope < 0, -1, 0))
            df['trend_regime'] = df['trend_regime'].astype('Int64')

            atr_20_mean = df['atr'].rolling(20).mean()
            df['vol_regime'] = (df['atr'] > atr_20_mean).astype('Int64')
            df['regime_confidence'] = abs(sma_50_slope) / df['sma_50'].rolling(20).std()

            # =========================================
            # MA CROSSOVER CYCLE TRACKING
            # =========================================
            # Golden Cross: EMA_12 crosses above EMA_26 (buy signal)
            df['golden_cross'] = ((df['ema_12'] > df['ema_26']) &
                                   (df['ema_12'].shift(1) <= df['ema_26'].shift(1))).astype('Int64')

            # Death Cross: EMA_12 crosses below EMA_26 (sell signal)
            df['death_cross'] = ((df['ema_12'] < df['ema_26']) &
                                  (df['ema_12'].shift(1) >= df['ema_26'].shift(1))).astype('Int64')

            # Cycle Type: 1 = RISE (above), -1 = FALL (below), 0 = neutral
            df['cycle_type'] = np.where(df['ema_12'] > df['ema_26'], 1,
                                        np.where(df['ema_12'] < df['ema_26'], -1, 0))
            df['cycle_type'] = df['cycle_type'].astype('Int64')

            # Track cycle start price (price at last crossover)
            crossover_mask = (df['golden_cross'] == 1) | (df['death_cross'] == 1)
            df['cycle_start_price'] = df['close'].where(crossover_mask).ffill()

            # Gain/Loss from cycle start (percentage)
            df['cycle_pnl_pct'] = ((df['close'] - df['cycle_start_price']) / df['cycle_start_price'] * 100).round(2)

            # Track cycle peak and bottom within current cycle
            df['cycle_peak'] = df.groupby((crossover_mask).cumsum())['high'].cummax()
            df['cycle_bottom'] = df.groupby((crossover_mask).cumsum())['low'].cummin()

            # Drawdown from peak (in RISE cycle)
            df['cycle_drawdown_pct'] = ((df['close'] - df['cycle_peak']) / df['cycle_peak'] * 100).round(2)

            # Recovery from bottom (in FALL cycle)
            df['cycle_recovery_pct'] = ((df['close'] - df['cycle_bottom']) / df['cycle_bottom'] * 100).round(2)

            # =========================================
            # VOLUME PRESSURE ANALYSIS
            # =========================================
            df['is_green'] = (df['close'] > df['open']).astype('Int64')
            df['is_red'] = (df['close'] < df['open']).astype('Int64')
            df['buy_pressure_pct'] = (df['is_green'].rolling(20).sum() / 20 * 100).round(1)
            df['sell_pressure_pct'] = (df['is_red'].rolling(20).sum() / 20 * 100).round(1)

            # =========================================
            # CANDLESTICK PATTERN DETECTION
            # =========================================
            body = abs(df['close'] - df['open'])
            candle_range = df['high'] - df['low']
            upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
            lower_shadow = df[['open', 'close']].min(axis=1) - df['low']

            # Hammer (bullish reversal)
            df['hammer'] = ((lower_shadow > 2 * body) & (upper_shadow < 0.3 * body) & (body > 0)).astype('Int64')

            # Shooting Star (bearish reversal)
            df['shooting_star'] = ((upper_shadow > 2 * body) & (lower_shadow < 0.3 * body) & (body > 0)).astype('Int64')

            # Bullish Engulfing
            df['bullish_engulfing'] = ((df['is_green'] == 1) & (df['is_red'].shift(1) == 1) &
                                        (df['close'] > df['open'].shift(1)) & (df['open'] < df['close'].shift(1))).astype('Int64')

            # Bearish Engulfing
            df['bearish_engulfing'] = ((df['is_red'] == 1) & (df['is_green'].shift(1) == 1) &
                                        (df['close'] < df['open'].shift(1)) & (df['open'] > df['close'].shift(1))).astype('Int64')

            # Doji (indecision)
            avg_body = body.rolling(20).mean()
            df['doji'] = (body < avg_body * 0.1).astype('Int64')

            # Update timestamp
            df['updated_at'] = pd.Timestamp.now()

        except Exception as calc_error:
            print(f"  [{i}/{total_symbols}] {symbol:8} - ERROR in calculations: {calc_error}")
            failed_symbols.append((symbol, str(calc_error)))
            continue

        # Prepare update data (only indicator fields + updated_at)
        update_fields = [
            'datetime', 'symbol',  # Keys for matching
            'rsi', 'macd', 'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'cci', 'williams_r', 'momentum',
            'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_20', 'ema_26', 'ema_50', 'ema_200', 'kama',
            'bollinger_upper', 'bollinger_middle', 'bollinger_lower', 'bb_width',
            'adx', 'plus_di', 'minus_di', 'atr', 'trix', 'roc',
            'obv', 'pvo', 'ppo', 'ultimate_osc', 'awesome_osc',
            'log_return', 'return_2w', 'return_4w',
            'close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct',
            'rsi_slope', 'rsi_zscore', 'rsi_overbought', 'rsi_oversold', 'macd_cross',
            'ema20_slope', 'ema50_slope', 'atr_zscore', 'atr_slope', 'volume_zscore', 'volume_ratio',
            'pivot_high_flag', 'pivot_low_flag', 'dist_to_pivot_high', 'dist_to_pivot_low',
            'dist_to_pivot_high_pct', 'dist_to_pivot_low_pct',
            'trend_regime', 'vol_regime', 'regime_confidence',
            # MA Crossover Cycle Tracking
            'golden_cross', 'death_cross', 'cycle_type', 'cycle_start_price', 'cycle_pnl_pct',
            'cycle_peak', 'cycle_bottom', 'cycle_drawdown_pct', 'cycle_recovery_pct',
            # Volume Pressure
            'is_green', 'is_red', 'buy_pressure_pct', 'sell_pressure_pct',
            # Candlestick Patterns
            'hammer', 'shooting_star', 'bullish_engulfing', 'bearish_engulfing', 'doji',
            'updated_at'
        ]

        update_df = df[update_fields].copy()

        # Delete old data for this symbol
        delete_query = f"""
        DELETE FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
        WHERE symbol = '{symbol}'
        """
        client.query(delete_query).result()

        # Re-insert with indicators (merge with original data)
        # Fetch original data again to get all fields
        original_query = f"""
        SELECT *
        FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
        WHERE symbol = '{symbol}'
        """
        # Wait, we just deleted it. Let me use a different approach - update in place

        # Better approach: Create temp table, then replace
        temp_table = f"aialgotradehits.crypto_trading_data.temp_{symbol.replace('-', '_').replace('.', '_')}"

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )

        # Upload entire dataframe with indicators
        job = client.load_table_from_dataframe(df, temp_table, job_config=job_config)
        job.result()

        # Merge back to main table
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
            log_return = S.log_return, return_2w = S.return_2w, return_4w = S.return_4w,
            close_vs_sma20_pct = S.close_vs_sma20_pct, close_vs_sma50_pct = S.close_vs_sma50_pct, close_vs_sma200_pct = S.close_vs_sma200_pct,
            rsi_slope = S.rsi_slope, rsi_zscore = S.rsi_zscore, rsi_overbought = S.rsi_overbought, rsi_oversold = S.rsi_oversold, macd_cross = S.macd_cross,
            ema20_slope = S.ema20_slope, ema50_slope = S.ema50_slope, atr_zscore = S.atr_zscore, atr_slope = S.atr_slope,
            volume_zscore = S.volume_zscore, volume_ratio = S.volume_ratio,
            pivot_high_flag = S.pivot_high_flag, pivot_low_flag = S.pivot_low_flag,
            dist_to_pivot_high = S.dist_to_pivot_high, dist_to_pivot_low = S.dist_to_pivot_low,
            dist_to_pivot_high_pct = S.dist_to_pivot_high_pct, dist_to_pivot_low_pct = S.dist_to_pivot_low_pct,
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
    for symbol, error in failed_symbols:
        print(f"  - {symbol}: {error[:80]}")

print("\n" + "="*100)
print("Validating results...")

# Validation
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

result = client.query(validation_query).result()
for row in result:
    print(f"Total rows: {row.total_rows:,}")
    print(f"Symbols: {row.unique_symbols}")
    print(f"Rows with RSI: {row.rows_with_rsi:,} ({row.rows_with_rsi/row.total_rows*100:.1f}%)")
    print(f"Rows with MACD: {row.rows_with_macd:,} ({row.rows_with_macd/row.total_rows*100:.1f}%)")
    print(f"Rows with SMA200: {row.rows_with_sma200:,} ({row.rows_with_sma200/row.total_rows*100:.1f}%)")
    print(f"Rows with Bollinger: {row.rows_with_bbands:,} ({row.rows_with_bbands/row.total_rows*100:.1f}%)")

print("="*100)
print("ALL DONE!")
