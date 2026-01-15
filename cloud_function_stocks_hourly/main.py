"""
Stock Hourly Data Fetcher with Technical Indicators
Fetches hourly OHLC data for major US stocks and calculates comprehensive technical indicators
"""

import yfinance as yf
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timedelta, timezone
import time
import logging
import functions_framework

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'hourly_stock'

# Stock symbols to track (same as daily function - verified working)
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


def calculate_technical_indicators(df):
    """Calculate all technical indicators for a dataframe"""

    if len(df) < 200:
        logger.warning(f"Not enough data for full indicator calculation: {len(df)} rows")

    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)

    # RSI (14 periods)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # Bollinger Bands
    df['sma_20'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['sma_20'] + (bb_std * 2)
    df['bb_lower'] = df['sma_20'] - (bb_std * 2)
    df['bb_middle'] = df['sma_20']
    df['bb_width'] = df['bb_upper'] - df['bb_lower']

    # EMAs
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

    # SMAs
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean()

    # Stochastic Oscillator
    low_14 = df['low'].rolling(window=14).min()
    high_14 = df['high'].rolling(window=14).max()
    df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # Williams %R
    df['williams_r'] = -100 * ((high_14 - df['close']) / (high_14 - low_14))

    # ADX (Average Directional Index)
    high_diff = df['high'].diff()
    low_diff = -df['low'].diff()

    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

    tr1 = df['high'] - df['low']
    tr2 = abs(df['high'] - df['close'].shift())
    tr3 = abs(df['low'] - df['close'].shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr14 = tr.rolling(window=14).mean()
    df['atr'] = atr14

    plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr14)
    minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr14)
    df['plus_di'] = plus_di
    df['minus_di'] = minus_di

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    df['adx'] = dx.rolling(window=14).mean()

    # CCI (Commodity Channel Index)
    tp = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = tp.rolling(window=20).mean()
    mad = tp.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
    df['cci'] = (tp - sma_tp) / (0.015 * mad)

    # Momentum
    df['momentum'] = df['close'] - df['close'].shift(10)

    # Rate of Change
    df['roc'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100

    # OBV (On-Balance Volume)
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['obv'] = obv

    # PVO (Percentage Volume Oscillator)
    volume_ema12 = df['volume'].ewm(span=12, adjust=False).mean()
    volume_ema26 = df['volume'].ewm(span=26, adjust=False).mean()
    df['pvo'] = ((volume_ema12 - volume_ema26) / volume_ema26) * 100
    df['pvo_signal'] = df['pvo'].ewm(span=9, adjust=False).mean()

    # KAMA (Kaufman Adaptive Moving Average)
    change = abs(df['close'] - df['close'].shift(10))
    volatility = df['close'].diff().abs().rolling(window=10).sum()
    er = change / volatility
    fast_sc = 2 / (2 + 1)
    slow_sc = 2 / (30 + 1)
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2

    kama = [df['close'].iloc[0]]
    for i in range(1, len(df)):
        kama.append(kama[-1] + sc.iloc[i] * (df['close'].iloc[i] - kama[-1]))
    df['kama'] = kama

    # TRIX
    ema1 = df['close'].ewm(span=15, adjust=False).mean()
    ema2 = ema1.ewm(span=15, adjust=False).mean()
    ema3 = ema2.ewm(span=15, adjust=False).mean()
    df['trix'] = 100 * (ema3.diff() / ema3.shift())

    # PPO (Percentage Price Oscillator)
    df['ppo'] = ((df['ema_12'] - df['ema_26']) / df['ema_26']) * 100
    df['ppo_signal'] = df['ppo'].ewm(span=9, adjust=False).mean()

    # Ultimate Oscillator
    bp = df['close'] - df[['low', 'close']].shift().min(axis=1)
    tr_uo = df[['high', 'close']].shift().max(axis=1) - df[['low', 'close']].shift().min(axis=1)
    avg7 = bp.rolling(window=7).sum() / tr_uo.rolling(window=7).sum()
    avg14 = bp.rolling(window=14).sum() / tr_uo.rolling(window=14).sum()
    avg28 = bp.rolling(window=28).sum() / tr_uo.rolling(window=28).sum()
    df['ultimate_oscillator'] = 100 * ((4 * avg7 + 2 * avg14 + avg28) / 7)

    # Awesome Oscillator
    median_price = (df['high'] + df['low']) / 2
    ao_fast = median_price.rolling(window=5).mean()
    ao_slow = median_price.rolling(window=34).mean()
    df['awesome_oscillator'] = ao_fast - ao_slow

    return df


def clean_yahoo_finance_data(df):
    """Clean and validate Yahoo Finance data"""

    # Remove rows with NaN in critical OHLC columns
    df = df.dropna(subset=['open', 'high', 'low', 'close'])

    # Ensure volume is not negative
    df['volume'] = df['volume'].clip(lower=0)

    # Validate OHLC logic: high >= low, high >= open, high >= close, low <= open, low <= close
    df = df[
        (df['high'] >= df['low']) &
        (df['high'] >= df['open']) &
        (df['high'] >= df['close']) &
        (df['low'] <= df['open']) &
        (df['low'] <= df['close'])
    ]

    # Remove duplicate timestamps
    df = df[~df.index.duplicated(keep='first')]

    # Remove outliers (prices that change more than 50% in one candle - likely data errors)
    df['pct_change'] = df['close'].pct_change()
    df = df[abs(df['pct_change']) < 0.5]
    df = df.drop('pct_change', axis=1)

    return df


def fetch_stock_hourly_data(symbol):
    """Fetch hourly data for a single stock with data cleaning"""
    try:
        logger.info(f"Fetching hourly data for {symbol}")

        # Fetch last 60 days of hourly data (needed for 200-period indicators)
        stock = yf.Ticker(symbol)
        df = stock.history(period='60d', interval='1h')

        if df.empty:
            logger.warning(f"No data returned for {symbol}")
            return None

        # Clean the data
        df = clean_yahoo_finance_data(df)

        if df.empty:
            logger.warning(f"No valid data after cleaning for {symbol}")
            return None

        # Get stock info with error handling
        try:
            info = stock.info
            company_name = info.get('longName', symbol)
            sector = info.get('sector', 'Unknown')
            exchange = info.get('exchange', 'Unknown')
        except Exception as e:
            logger.warning(f"Could not fetch info for {symbol}: {e}")
            company_name = symbol
            sector = 'Unknown'
            exchange = 'Unknown'

        # Prepare dataframe
        df = df.reset_index()
        df.columns = [col.lower() for col in df.columns]

        # Rename columns to match our schema
        df = df.rename(columns={'datetime': 'timestamp_dt'})

        # Convert timestamp
        df['timestamp'] = df['timestamp_dt'].astype(np.int64) // 10**9
        df['datetime'] = df['timestamp_dt']

        # Add stock metadata
        df['symbol'] = symbol
        df['company_name'] = company_name
        df['sector'] = sector
        df['exchange'] = exchange

        # Calculate technical indicators
        df = calculate_technical_indicators(df)

        # Select only the latest hour (most recent data point)
        df = df.tail(1)

        # Select columns matching BigQuery schema
        columns = [
            'symbol', 'company_name', 'sector', 'exchange',
            'datetime', 'timestamp',
            'open', 'high', 'low', 'close', 'volume',
            'sma_20', 'sma_50', 'sma_200',
            'ema_12', 'ema_26', 'ema_50',
            'rsi', 'macd', 'macd_signal', 'macd_hist', 'momentum', 'roc',
            'bb_upper', 'bb_middle', 'bb_lower', 'bb_width',
            'atr', 'adx', 'plus_di', 'minus_di',
            'cci', 'williams_r', 'stoch_k', 'stoch_d',
            'obv', 'pvo', 'pvo_signal',
            'kama', 'trix', 'ppo', 'ppo_signal',
            'ultimate_oscillator', 'awesome_oscillator'
        ]

        df = df[columns]

        logger.info(f"✓ Fetched {len(df)} hourly records for {symbol}")
        return df

    except Exception as e:
        logger.error(f"✗ Error fetching {symbol}: {str(e)}")
        return None


def upload_to_bigquery(df):
    """Upload dataframe to BigQuery with duplicate detection"""
    if df is None or df.empty:
        return 0

    try:
        client = bigquery.Client(project=PROJECT_ID)
        table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

        # Get min/max timestamps for duplicate check
        min_ts = df['timestamp'].min()
        max_ts = df['timestamp'].max()
        symbols = df['symbol'].unique().tolist()

        # Query existing records
        query = f"""
        SELECT symbol, UNIX_SECONDS(datetime) as timestamp
        FROM `{table_ref}`
        WHERE UNIX_SECONDS(datetime) BETWEEN {min_ts} AND {max_ts}
        AND symbol IN ('{"','".join(symbols)}')
        """

        existing = client.query(query).to_dataframe()

        if not existing.empty:
            # Create composite key for deduplication
            existing['key'] = existing['symbol'] + '_' + existing['timestamp'].astype(str)
            df['key'] = df['symbol'] + '_' + df['timestamp'].astype(str)

            # Filter out duplicates
            df = df[~df['key'].isin(existing['key'])]
            df = df.drop('key', axis=1)

        if df.empty:
            logger.info("No new records to upload (all duplicates)")
            return 0

        # Upload to BigQuery
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema_update_options=[
                bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
            ]
        )

        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()

        logger.info(f"✓ Uploaded {len(df)} new records to BigQuery")
        return len(df)

    except Exception as e:
        logger.error(f"✗ Error uploading to BigQuery: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


@functions_framework.http
def main(request):
    """HTTP Cloud Function entry point"""

    logger.info("=" * 70)
    logger.info("STOCK HOURLY DATA FETCHER - STARTING")
    logger.info("=" * 70)

    start_time = time.time()
    all_data = []
    success_count = 0
    error_count = 0

    for i, symbol in enumerate(STOCK_SYMBOLS, 1):
        logger.info(f"\n[{i}/{len(STOCK_SYMBOLS)}] Processing {symbol}...")

        df = fetch_stock_hourly_data(symbol)

        if df is not None and not df.empty:
            all_data.append(df)
            success_count += 1
        else:
            error_count += 1

        # Rate limiting - increased to avoid Yahoo Finance throttling
        if i < len(STOCK_SYMBOLS):
            time.sleep(2.5)  # Increased from 1.5s to 2.5s

    # Combine all data
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        uploaded = upload_to_bigquery(combined_df)
    else:
        uploaded = 0

    elapsed = time.time() - start_time

    logger.info("=" * 70)
    logger.info("STOCK HOURLY DATA FETCHER - COMPLETE")
    logger.info("=" * 70)
    logger.info(f"✓ Success: {success_count}/{len(STOCK_SYMBOLS)} stocks")
    logger.info(f"✗ Errors: {error_count}")
    logger.info(f"📊 Records uploaded: {uploaded}")
    logger.info(f"⏱ Time elapsed: {elapsed:.2f}s")
    logger.info("=" * 70)

    return {
        'success': True,
        'symbols_processed': len(STOCK_SYMBOLS),
        'success_count': success_count,
        'error_count': error_count,
        'records_uploaded': uploaded,
        'elapsed_seconds': elapsed
    }, 200


if __name__ == "__main__":
    # For local testing
    class MockRequest:
        pass

    result, status = main(MockRequest())
    print(f"\nResult: {result}")
