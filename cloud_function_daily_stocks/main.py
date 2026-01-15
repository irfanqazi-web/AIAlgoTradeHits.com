"""
Daily Stock Data Fetcher with Technical Indicators
Fetches daily OHLC data for major US stocks using Yahoo Finance and calculates
comprehensive technical indicators including Elliott Wave and Fibonacci analysis
"""

import yfinance as yf
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timedelta
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'daily_stock'

# Stock symbols to track (major US stocks and ETFs)
STOCK_SYMBOLS = [
    # Tech Giants (FAANG+)
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX',
    # Financial
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA', 'AXP', 'BLK',
    # Technology & Semiconductors
    'ORCL', 'CSCO', 'INTC', 'AMD', 'CRM', 'ADBE', 'NOW', 'AVGO', 'QCOM', 'TXN',
    # Healthcare & Pharma
    'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'MRK', 'ABT', 'DHR', 'LLY', 'BMY',
    # Consumer & Retail
    'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'COST', 'DIS', 'CMCSA',
    # Energy & Utilities
    'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'NEE', 'DUK', 'SO', 'D',
    # Industrial & Manufacturing
    'BA', 'CAT', 'HON', 'UNP', 'UPS', 'RTX', 'LMT', 'GE', 'MMM', 'DE',
    # Communication Services
    'T', 'VZ', 'TMUS', 'CHTR',
    # Materials & Chemicals
    'LIN', 'APD', 'ECL', 'SHW', 'DD', 'DOW', 'NEM', 'FCX',
    # Real Estate & REITs
    'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'SPG', 'O', 'WELL',
    # ETFs (Market Indices)
    'SPY', 'QQQ', 'DIA', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'AGG', 'TLT'
]


def calculate_fibonacci_levels(df):
    """Calculate Fibonacci retracement and extension levels - same as crypto"""

    window = 5

    # Detect swing highs and lows
    df['swing_high'] = (
        (df['high'] == df['high'].rolling(window=window, center=True).max()) &
        (df['high'] > df['high'].shift(1)) &
        (df['high'] > df['high'].shift(-1))
    )

    df['swing_low'] = (
        (df['low'] == df['low'].rolling(window=window, center=True).min()) &
        (df['low'] < df['low'].shift(1)) &
        (df['low'] < df['low'].shift(-1))
    )

    # Get recent swing points
    recent_swing_highs = df[df['swing_high'] == True].tail(2)
    recent_swing_lows = df[df['swing_low'] == True].tail(2)

    if len(recent_swing_highs) >= 1 and len(recent_swing_lows) >= 1:
        swing_high = recent_swing_highs.iloc[-1]['high']
        swing_low = recent_swing_lows.iloc[-1]['low']
        diff = swing_high - swing_low

        # Fibonacci Retracement Levels
        df['fib_0'] = swing_low
        df['fib_236'] = swing_low + (diff * 0.236)
        df['fib_382'] = swing_low + (diff * 0.382)
        df['fib_500'] = swing_low + (diff * 0.500)
        df['fib_618'] = swing_low + (diff * 0.618)
        df['fib_786'] = swing_low + (diff * 0.786)
        df['fib_100'] = swing_high

        # Fibonacci Extension Levels
        df['fib_ext_1272'] = swing_low + (diff * 1.272)
        df['fib_ext_1618'] = swing_low + (diff * 1.618)
        df['fib_ext_2618'] = swing_low + (diff * 2.618)

        # Distance to key levels
        current_price = df['close'].iloc[-1]
        df['dist_to_fib_236'] = ((df['fib_236'] - current_price) / current_price) * 100
        df['dist_to_fib_382'] = ((df['fib_382'] - current_price) / current_price) * 100
        df['dist_to_fib_500'] = ((df['fib_500'] - current_price) / current_price) * 100
        df['dist_to_fib_618'] = ((df['fib_618'] - current_price) / current_price) * 100

    return df


def detect_elliott_wave_pattern(df):
    """Detect Elliott Wave patterns - same as crypto"""

    if len(df) < 13:
        return df

    # Trend direction
    sma_20 = df['close'].rolling(window=20).mean()
    sma_50 = df['close'].rolling(window=50).mean()

    trend_direction = []
    for idx in range(len(df)):
        if idx < 50:
            trend_direction.append(0)
        elif sma_20.iloc[idx] > sma_50.iloc[idx] and df['close'].iloc[idx] > sma_20.iloc[idx]:
            trend_direction.append(1)  # Uptrend
        elif sma_20.iloc[idx] < sma_50.iloc[idx] and df['close'].iloc[idx] < sma_20.iloc[idx]:
            trend_direction.append(-1)  # Downtrend
        else:
            trend_direction.append(0)  # Sideways

    df['trend_direction'] = trend_direction

    # Detect local maxima and minima
    window = 5
    df['local_maxima'] = (
        (df['high'] > df['high'].shift(1)) &
        (df['high'] > df['high'].shift(-1))
    )
    df['local_minima'] = (
        (df['low'] < df['low'].shift(1)) &
        (df['low'] < df['low'].shift(-1))
    )

    # Get recent wave points
    recent_maxima = df[df['local_maxima'] == True].tail(5)
    recent_minima = df[df['local_minima'] == True].tail(5)

    if len(recent_maxima) >= 3 and len(recent_minima) >= 2:
        df['impulse_wave_count'] = len(recent_maxima)
        df['corrective_wave_count'] = len(recent_minima)

        wave_position = min(5, len(recent_maxima))
        df['wave_position'] = wave_position

        # Wave degree classification
        price_range = df['high'].max() - df['low'].min()
        price_pct = (price_range / df['close'].mean()) * 100

        if price_pct > 50:
            df['elliott_wave_degree'] = 'Primary'
        elif price_pct > 20:
            df['elliott_wave_degree'] = 'Intermediate'
        elif price_pct > 10:
            df['elliott_wave_degree'] = 'Minor'
        else:
            df['elliott_wave_degree'] = 'Minute'

        # Record wave peaks
        if len(recent_maxima) >= 3:
            df['wave_1_high'] = recent_maxima.iloc[-3]['high']
            df['wave_3_high'] = recent_maxima.iloc[-2]['high']
            df['wave_5_high'] = recent_maxima.iloc[-1]['high']

        if len(recent_minima) >= 2:
            df['wave_2_low'] = recent_minima.iloc[-2]['low']
            df['wave_4_low'] = recent_minima.iloc[-1]['low']

    # Trend strength
    df['trend_strength'] = np.abs(df['adx']) if 'adx' in df.columns else 0

    # Volatility regime
    if 'atr' in df.columns:
        atr_mean = df['atr'].rolling(window=20).mean()
        volatility_regime = []
        for idx in range(len(df)):
            if pd.isna(df['atr'].iloc[idx]) or pd.isna(atr_mean.iloc[idx]):
                volatility_regime.append('normal')
            elif df['atr'].iloc[idx] > atr_mean.iloc[idx] * 1.5:
                volatility_regime.append('high')
            elif df['atr'].iloc[idx] < atr_mean.iloc[idx] * 0.5:
                volatility_regime.append('low')
            else:
                volatility_regime.append('normal')
        df['volatility_regime'] = volatility_regime

    # Price changes
    df['price_change_1d'] = ((df['close'] - df['close'].shift(1)) / df['close'].shift(1)) * 100
    df['price_change_5d'] = ((df['close'] - df['close'].shift(5)) / df['close'].shift(5)) * 100
    df['price_change_20d'] = ((df['close'] - df['close'].shift(20)) / df['close'].shift(20)) * 100

    return df


def calculate_technical_indicators(df):
    """Calculate all technical indicators - same as crypto"""

    if len(df) < 200:
        logger.warning(f"Insufficient data for full indicator calculation: {len(df)} rows")

    # Sort by date
    df = df.sort_values('datetime').reset_index(drop=True)

    # Moving Averages
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean()

    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']

    # ATR
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(window=14).mean()

    # ADX
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr14 = true_range.rolling(window=14).sum()
    df['plus_di'] = 100 * (plus_dm.rolling(window=14).sum() / tr14)
    df['minus_di'] = 100 * (minus_dm.rolling(window=14).sum() / tr14)

    dx = 100 * np.abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
    df['adx'] = dx.rolling(window=14).mean()

    # Momentum
    df['momentum'] = df['close'] - df['close'].shift(10)
    df['roc'] = ((df['close'] - df['close'].shift(12)) / df['close'].shift(12)) * 100

    # CCI
    tp = (df['high'] + df['low'] + df['close']) / 3
    df['cci'] = (tp - tp.rolling(window=20).mean()) / (0.015 * tp.rolling(window=20).std())

    # Williams %R
    hh = df['high'].rolling(window=14).max()
    ll = df['low'].rolling(window=14).min()
    df['williams_r'] = -100 * ((hh - df['close']) / (hh - ll))

    # Stochastic
    df['stoch_k'] = 100 * ((df['close'] - ll) / (hh - ll))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # OBV
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['obv'] = obv

    # PVO
    vol_ema_12 = df['volume'].ewm(span=12, adjust=False).mean()
    vol_ema_26 = df['volume'].ewm(span=26, adjust=False).mean()
    df['pvo'] = ((vol_ema_12 - vol_ema_26) / vol_ema_26) * 100
    df['pvo_signal'] = df['pvo'].ewm(span=9, adjust=False).mean()

    # KAMA
    change = np.abs(df['close'] - df['close'].shift(10))
    volatility = np.abs(df['close'].diff()).rolling(window=10).sum()
    er = change / volatility
    fast_sc = 2 / (2 + 1)
    slow_sc = 2 / (30 + 1)
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
    df['kama'] = df['close'].ewm(alpha=sc, adjust=False).mean()

    # TRIX
    ema1 = df['close'].ewm(span=15, adjust=False).mean()
    ema2 = ema1.ewm(span=15, adjust=False).mean()
    ema3 = ema2.ewm(span=15, adjust=False).mean()
    df['trix'] = 100 * (ema3.diff() / ema3.shift())

    # PPO
    df['ppo'] = ((df['ema_12'] - df['ema_26']) / df['ema_26']) * 100
    df['ppo_signal'] = df['ppo'].ewm(span=9, adjust=False).mean()

    # Ultimate Oscillator
    bp = df['close'] - pd.concat([df['low'], df['close'].shift()], axis=1).min(axis=1)
    avg7 = bp.rolling(window=7).sum() / true_range.rolling(window=7).sum()
    avg14 = bp.rolling(window=14).sum() / true_range.rolling(window=14).sum()
    avg28 = bp.rolling(window=28).sum() / true_range.rolling(window=28).sum()
    df['ultimate_oscillator'] = 100 * ((4 * avg7 + 2 * avg14 + avg28) / 7)

    # Awesome Oscillator
    median_price = (df['high'] + df['low']) / 2
    df['awesome_oscillator'] = median_price.rolling(window=5).mean() - median_price.rolling(window=34).mean()

    # Calculate Fibonacci and Elliott Wave
    df = calculate_fibonacci_levels(df)
    df = detect_elliott_wave_pattern(df)

    return df


def fetch_daily_stock_data():
    """Fetch daily OHLC data for all stock symbols"""

    logger.info(f"Fetching data for {len(STOCK_SYMBOLS)} stock symbols...")

    # Fetch 250 days to ensure enough for SMA_200
    end_date = datetime.now()
    start_date = end_date - timedelta(days=250)

    all_processed_data = []
    failed_symbols = []
    successful_symbols = 0

    for idx, symbol in enumerate(STOCK_SYMBOLS, 1):
        try:
            if idx % 10 == 0:
                logger.info(f"Progress: {idx}/{len(STOCK_SYMBOLS)} symbols")

            # Fetch stock data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date, interval='1d')

            if hist.empty or len(hist) < 50:
                logger.warning(f"Not enough data for {symbol}: {len(hist)} days")
                failed_symbols.append(symbol)
                continue

            # Get stock info
            try:
                info = ticker.info
                company_name = info.get('longName', symbol)
                sector = info.get('sector', 'Unknown')
                industry = info.get('industry', 'Unknown')
                exchange = info.get('exchange', 'Unknown')
            except:
                company_name = symbol
                sector = 'Unknown'
                industry = 'Unknown'
                exchange = 'Unknown'

            # Create dataframe
            df_symbol = pd.DataFrame({
                'symbol': symbol,
                'company_name': company_name,
                'sector': sector,
                'industry': industry,
                'exchange': exchange,
                'datetime': hist.index,
                'date': hist.index.date,
                'timestamp': hist.index.astype(int) // 10**9,
                'open': hist['Open'].values,
                'high': hist['High'].values,
                'low': hist['Low'].values,
                'close': hist['Close'].values,
                'volume': hist['Volume'].values,
                'dividends': hist.get('Dividends', 0),
                'stock_splits': hist.get('Stock Splits', 0)
            })

            # Calculate technical indicators
            df_symbol = calculate_technical_indicators(df_symbol)

            # Only keep latest record (yesterday's data)
            df_latest = df_symbol.tail(1)

            all_processed_data.append(df_latest)
            successful_symbols += 1

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            logger.error(f"Exception fetching {symbol}: {str(e)}")
            failed_symbols.append(symbol)
            time.sleep(1)

    logger.info(f"Successfully processed {successful_symbols}/{len(STOCK_SYMBOLS)} symbols")

    if failed_symbols:
        logger.warning(f"Failed symbols ({len(failed_symbols)}): {', '.join(failed_symbols)}")

    if all_processed_data:
        return pd.concat(all_processed_data, ignore_index=True)
    return None


def append_to_bigquery(df):
    """Append stock data to BigQuery with all technical indicators"""

    if df is None or df.empty:
        logger.warning("No data to upload")
        return False

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    try:
        # Check for duplicates
        min_date = df['date'].min().strftime('%Y-%m-%d') if 'date' in df.columns else df['datetime'].min().strftime('%Y-%m-%d')
        max_date = df['date'].max().strftime('%Y-%m-%d') if 'date' in df.columns else df['datetime'].max().strftime('%Y-%m-%d')

        query = f"""
        SELECT DISTINCT symbol, timestamp
        FROM `{table_ref}`
        WHERE DATE(datetime) BETWEEN '{min_date}' AND '{max_date}'
        """

        try:
            existing_data = client.query(query).to_dataframe()
            logger.info(f"Found {len(existing_data)} existing records")

            if not existing_data.empty:
                df['key'] = df['symbol'] + '_' + df['timestamp'].astype(str)
                existing_data['key'] = existing_data['symbol'] + '_' + existing_data['timestamp'].astype(str)

                df_filtered = df[~df['key'].isin(existing_data['key'])].copy()
                df_filtered = df_filtered.drop(columns=['key'])
            else:
                df_filtered = df
        except:
            df_filtered = df

        if df_filtered.empty:
            logger.info("No new data to insert (all records already exist)")
            return True

        # Replace inf and NaN
        df_filtered = df_filtered.replace([np.inf, -np.inf], np.nan)
        df_filtered = df_filtered.where(pd.notnull(df_filtered), None)

        # Ensure date column is DATE type
        df_filtered['date'] = pd.to_datetime(df_filtered['date']).dt.date

        logger.info(f"Uploading {len(df_filtered)} new records to BigQuery")

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
        )

        job = client.load_table_from_dataframe(df_filtered, table_ref, job_config=job_config)
        job.result()

        logger.info(f"Successfully uploaded {len(df_filtered)} records")
        return True

    except Exception as e:
        logger.error(f"Error uploading to BigQuery: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""

    logger.info("="*70)
    logger.info("Starting Daily Stock Data Fetch with Technical Indicators")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info("="*70)

    df = fetch_daily_stock_data()

    if df is not None and not df.empty:
        df = df.drop_duplicates(subset=['symbol', 'timestamp'], keep='last')
        logger.info(f"Final record count: {len(df)} records")

        success = append_to_bigquery(df)

        if success:
            logger.info("Daily stock data fetch with indicators completed successfully!")
        else:
            logger.error("Failed to upload data to BigQuery")
    else:
        logger.error("No data fetched from Yahoo Finance")

    logger.info("="*70)


def daily_stock_fetch(request):
    """Cloud Function entry point"""
    main()
    return 'Daily stock data fetch with indicators completed', 200


if __name__ == "__main__":
    main()
