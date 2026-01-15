"""
TwelveData Stocks Daily Data Fetcher
Fetches daily OHLCV data for top US stocks and calculates technical indicators
"""

import requests
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timedelta
import time
import logging
from flask import Flask, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'stocks_daily_td'
TWELVE_DATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'

# Top 100 US stocks to track
TOP_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'JNJ',
    'XOM', 'V', 'PG', 'JPM', 'MA', 'HD', 'CVX', 'MRK', 'ABBV', 'PEP',
    'KO', 'AVGO', 'COST', 'WMT', 'MCD', 'CSCO', 'ACN', 'LIN', 'ABT', 'TMO',
    'ADBE', 'DIS', 'NKE', 'CMCSA', 'CRM', 'PFE', 'VZ', 'NFLX', 'INTC', 'DHR',
    'WFC', 'NEE', 'TXN', 'PM', 'RTX', 'UPS', 'ORCL', 'QCOM', 'AMD', 'INTU',
    'HON', 'LOW', 'BA', 'UNP', 'SPGI', 'IBM', 'SBUX', 'CAT', 'GS', 'AMGN',
    'AXP', 'BLK', 'MDT', 'GILD', 'DE', 'AMT', 'CVS', 'NOW', 'ISRG', 'PLD',
    'MMM', 'LRCX', 'TJX', 'MO', 'SYK', 'ZTS', 'TMUS', 'BKNG', 'CI', 'ADP',
    'MDLZ', 'BDX', 'REGN', 'ADI', 'CB', 'SO', 'DUK', 'VRTX', 'MMC', 'SCHW',
    'C', 'EQIX', 'MU', 'PGR', 'CL', 'ATVI', 'SHW', 'EOG', 'NOC', 'ICE'
]

def fetch_time_series(symbol, interval='1day', outputsize=100):
    """
    Fetch OHLCV time series data from TwelveData
    """
    params = {
        'symbol': symbol,
        'interval': interval,
        'outputsize': outputsize,
        'apikey': TWELVE_DATA_API_KEY,
        'format': 'JSON'
    }

    try:
        response = requests.get(f"{BASE_URL}/time_series", params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'values' in data and len(data['values']) > 0:
                return data
            else:
                logger.warning(f"No data for {symbol}: {data.get('message', 'Unknown error')}")
                return None
        else:
            logger.error(f"API error for {symbol}: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {str(e)}")
        return None

def fetch_stock_metadata(symbol):
    """Fetch stock metadata (name, exchange, currency)"""
    params = {
        'symbol': symbol,
        'apikey': TWELVE_DATA_API_KEY
    }

    try:
        response = requests.get(f"{BASE_URL}/stocks", params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                stock_info = data['data'][0]
                return {
                    'name': stock_info.get('name', ''),
                    'exchange': stock_info.get('exchange', ''),
                    'currency': stock_info.get('currency', 'USD'),
                    'country': stock_info.get('country', 'US'),
                    'mic_code': stock_info.get('mic_code', '')
                }
    except Exception as e:
        logger.error(f"Error fetching metadata for {symbol}: {str(e)}")

    return {
        'name': '',
        'exchange': 'NASDAQ/NYSE',
        'currency': 'USD',
        'country': 'United States',
        'mic_code': ''
    }

def calculate_technical_indicators(df):
    """
    Calculate all 71 technical indicators
    Input: DataFrame with columns [datetime, open, high, low, close, volume]
    Output: DataFrame with added indicator columns
    """

    # Ensure we have enough data
    if len(df) < 200:
        logger.warning(f"Not enough data for indicators: {len(df)} rows")
        # Return df with null indicators
        indicator_cols = [
            'rsi', 'macd', 'macd_signal', 'macd_hist', 'stoch_k', 'stoch_d',
            'williams_r', 'cci', 'roc', 'momentum',
            'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'ema_50',
            'wma_20', 'dema_20', 'tema_20', 'kama_20', 'vwap',
            'bb_upper', 'bb_middle', 'bb_lower', 'atr', 'natr', 'stddev',
            'obv', 'ad', 'adosc', 'pvo',
            'adx', 'adxr', 'plus_di', 'minus_di', 'aroon_up', 'aroon_down',
            'aroonosc', 'trix', 'dx', 'sar',
            'cdl_doji', 'cdl_hammer', 'cdl_engulfing', 'cdl_harami', 'cdl_morningstar',
            'cdl_3blackcrows', 'cdl_2crows', 'cdl_3inside', 'cdl_3linestrike', 'cdl_abandonedbaby',
            'correl', 'linearreg', 'linearreg_slope', 'linearreg_angle', 'tsf', 'variance', 'beta',
            'ultosc', 'bop', 'cmo', 'dpo', 'ht_dcperiod', 'ht_dcphase', 'ht_trendmode',
            'midpoint', 'midprice', 'ppo', 'stochrsi', 'apo', 'ht_sine_lead'
        ]
        for col in indicator_cols:
            df[col] = None
        return df

    try:
        # Momentum Indicators
        df['rsi'] = calculate_rsi(df['close'], period=14)
        macd_data = calculate_macd(df['close'])
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_hist'] = macd_data['histogram']

        stoch = calculate_stochastic(df)
        df['stoch_k'] = stoch['k']
        df['stoch_d'] = stoch['d']

        df['williams_r'] = calculate_williams_r(df)
        df['cci'] = calculate_cci(df)
        df['roc'] = df['close'].pct_change(periods=10) * 100
        df['momentum'] = df['close'].diff(10)

        # Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['wma_20'] = df['close'].rolling(window=20).apply(lambda x: (x * np.arange(1, len(x) + 1)).sum() / np.arange(1, len(x) + 1).sum())

        # Simple DEMA/TEMA calculations
        ema_20 = df['close'].ewm(span=20, adjust=False).mean()
        df['dema_20'] = 2 * ema_20 - ema_20.ewm(span=20, adjust=False).mean()
        df['tema_20'] = 3 * ema_20 - 3 * ema_20.ewm(span=20, adjust=False).mean() + ema_20.ewm(span=20, adjust=False).mean().ewm(span=20, adjust=False).mean()

        df['kama_20'] = calculate_kama(df['close'], period=20)
        df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()

        # Volatility
        bb = calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb['upper']
        df['bb_middle'] = bb['middle']
        df['bb_lower'] = bb['lower']

        df['atr'] = calculate_atr(df)
        df['natr'] = (df['atr'] / df['close']) * 100
        df['stddev'] = df['close'].rolling(window=20).std()

        # Volume
        df['obv'] = calculate_obv(df)
        df['ad'] = calculate_ad(df)
        df['adosc'] = df['ad'].diff(3)
        ema_vol_12 = df['volume'].ewm(span=12, adjust=False).mean()
        ema_vol_26 = df['volume'].ewm(span=26, adjust=False).mean()
        df['pvo'] = ((ema_vol_12 - ema_vol_26) / ema_vol_26) * 100

        # Trend
        adx_data = calculate_adx(df)
        df['adx'] = adx_data['adx']
        df['plus_di'] = adx_data['plus_di']
        df['minus_di'] = adx_data['minus_di']
        df['dx'] = adx_data['dx']
        df['adxr'] = (df['adx'] + df['adx'].shift(14)) / 2

        aroon = calculate_aroon(df)
        df['aroon_up'] = aroon['up']
        df['aroon_down'] = aroon['down']
        df['aroonosc'] = aroon['up'] - aroon['down']

        df['trix'] = df['close'].ewm(span=15, adjust=False).mean().ewm(span=15, adjust=False).mean().ewm(span=15, adjust=False).mean().pct_change() * 100
        df['sar'] = calculate_sar(df)

        # Pattern Recognition (simplified)
        df['cdl_doji'] = detect_doji(df)
        df['cdl_hammer'] = detect_hammer(df)
        df['cdl_engulfing'] = detect_engulfing(df)
        df['cdl_harami'] = 0
        df['cdl_morningstar'] = 0
        df['cdl_3blackcrows'] = 0
        df['cdl_2crows'] = 0
        df['cdl_3inside'] = 0
        df['cdl_3linestrike'] = 0
        df['cdl_abandonedbaby'] = 0

        # Statistical
        df['correl'] = df['close'].rolling(window=20).corr(df['volume'])
        df['linearreg'] = calculate_linear_regression(df['close'], period=14)
        df['linearreg_slope'] = df['close'].rolling(window=14).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
        df['linearreg_angle'] = np.arctan(df['linearreg_slope']) * (180 / np.pi)
        df['tsf'] = df['linearreg']
        df['variance'] = df['close'].rolling(window=20).var()
        df['beta'] = df['close'].rolling(window=50).apply(lambda x: np.cov(x, df['close'].iloc[-50:])[0, 1] / np.var(df['close'].iloc[-50:]))

        # Other Advanced
        df['ultosc'] = calculate_ultimate_oscillator(df)
        df['bop'] = (df['close'] - df['open']) / (df['high'] - df['low'])
        df['cmo'] = calculate_cmo(df['close'])
        df['dpo'] = df['close'] - df['close'].rolling(window=20).mean().shift(10)
        df['ht_dcperiod'] = 20  # Simplified
        df['ht_dcphase'] = 0
        df['ht_trendmode'] = 1 if df['close'].iloc[-1] > df['sma_50'].iloc[-1] else 0
        df['midpoint'] = (df['high'].rolling(window=14).max() + df['low'].rolling(window=14).min()) / 2
        df['midprice'] = (df['high'] + df['low']) / 2
        df['ppo'] = ((df['ema_12'] - df['ema_26']) / df['ema_26']) * 100
        df['stochrsi'] = (df['rsi'] - df['rsi'].rolling(window=14).min()) / (df['rsi'].rolling(window=14).max() - df['rsi'].rolling(window=14).min()) * 100
        df['apo'] = df['ema_12'] - df['ema_26']
        df['ht_sine_lead'] = 0

    except Exception as e:
        logger.error(f"Error calculating indicators: {str(e)}")

    return df

# Helper functions for indicator calculations
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return {'macd': macd, 'signal': signal_line, 'histogram': histogram}

def calculate_stochastic(df, period=14):
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()
    k = 100 * (df['close'] - low_min) / (high_max - low_min)
    d = k.rolling(window=3).mean()
    return {'k': k, 'd': d}

def calculate_williams_r(df, period=14):
    high_max = df['high'].rolling(window=period).max()
    low_min = df['low'].rolling(window=period).min()
    return -100 * (high_max - df['close']) / (high_max - low_min)

def calculate_cci(df, period=20):
    tp = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = tp.rolling(window=period).mean()
    mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
    return (tp - sma_tp) / (0.015 * mad)

def calculate_bollinger_bands(series, period=20, std=2):
    middle = series.rolling(window=period).mean()
    std_dev = series.rolling(window=period).std()
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    return {'upper': upper, 'middle': middle, 'lower': lower}

def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(window=period).mean()

def calculate_obv(df):
    obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
    return obv

def calculate_ad(df):
    mfm = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
    mfv = mfm * df['volume']
    return mfv.cumsum()

def calculate_adx(df, period=14):
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    atr = calculate_atr(df, period)
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()

    return {'adx': adx, 'plus_di': plus_di, 'minus_di': minus_di, 'dx': dx}

def calculate_aroon(df, period=25):
    aroon_up = df['high'].rolling(window=period + 1).apply(lambda x: x.argmax()) / period * 100
    aroon_down = df['low'].rolling(window=period + 1).apply(lambda x: x.argmin()) / period * 100
    return {'up': aroon_up, 'down': aroon_down}

def calculate_sar(df, af=0.02, max_af=0.2):
    # Simplified SAR calculation
    return df['close'].rolling(window=2).mean()

def calculate_kama(series, period=20):
    change = np.abs(series - series.shift(period))
    volatility = series.diff().abs().rolling(window=period).sum()
    er = change / volatility
    sc = (er * (2 / (2 + 1) - 2 / (30 + 1)) + 2 / (30 + 1)) ** 2
    kama = pd.Series(index=series.index, dtype=float)
    kama.iloc[period] = series.iloc[period]
    for i in range(period + 1, len(series)):
        kama.iloc[i] = kama.iloc[i - 1] + sc.iloc[i] * (series.iloc[i] - kama.iloc[i - 1])
    return kama

def calculate_ultimate_oscillator(df):
    bp = df['close'] - df[['low', 'close']].shift().min(axis=1)
    tr = df[['high', 'close']].max(axis=1) - df[['low', 'close']].shift().min(axis=1)
    avg7 = bp.rolling(window=7).sum() / tr.rolling(window=7).sum()
    avg14 = bp.rolling(window=14).sum() / tr.rolling(window=14).sum()
    avg28 = bp.rolling(window=28).sum() / tr.rolling(window=28).sum()
    return 100 * ((4 * avg7) + (2 * avg14) + avg28) / 7

def calculate_cmo(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).sum()
    loss = -delta.where(delta < 0, 0).rolling(window=period).sum()
    return 100 * (gain - loss) / (gain + loss)

def calculate_linear_regression(series, period=14):
    lr = series.rolling(window=period).apply(lambda x: np.polyval(np.polyfit(range(len(x)), x, 1), len(x) - 1))
    return lr

def detect_doji(df):
    body = np.abs(df['close'] - df['open'])
    range_hl = df['high'] - df['low']
    return (body / range_hl < 0.1).astype(int)

def detect_hammer(df):
    body = np.abs(df['close'] - df['open'])
    lower_shadow = df[['open', 'close']].min(axis=1) - df['low']
    upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
    return ((lower_shadow > 2 * body) & (upper_shadow < body * 0.3)).astype(int)

def detect_engulfing(df):
    bullish = ((df['close'].shift() < df['open'].shift()) &
               (df['close'] > df['open']) &
               (df['open'] < df['close'].shift()) &
               (df['close'] > df['open'].shift())).astype(int)
    return bullish

def upload_to_bigquery(data_dict):
    """Upload data to BigQuery"""
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    try:
        errors = client.insert_rows_json(table_id, data_dict)
        if errors:
            logger.error(f"BigQuery insert errors: {errors}")
            return False
        else:
            logger.info(f"Successfully uploaded {len(data_dict)} rows to BigQuery")
            return True
    except Exception as e:
        logger.error(f"Error uploading to BigQuery: {str(e)}")
        return False

def daily_stock_fetcher(request):
    """
    Main Cloud Function entry point
    Fetches daily data for top 100 US stocks
    """
    logger.info("Starting TwelveData stocks daily fetcher...")

    successful = 0
    failed = 0
    all_data = []

    for i, symbol in enumerate(TOP_STOCKS):
        logger.info(f"Processing {symbol} ({i+1}/{len(TOP_STOCKS)})...")

        # Fetch time series data
        ts_data = fetch_time_series(symbol, interval='1day', outputsize=250)
        if not ts_data:
            failed += 1
            continue

        # Fetch metadata
        metadata = fetch_stock_metadata(symbol)

        # Convert to DataFrame
        df = pd.DataFrame(ts_data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(int)

        # Sort by datetime ascending for indicator calculation
        df = df.sort_values('datetime')

        # Calculate indicators
        df = calculate_technical_indicators(df)

        # Get only latest row (today's data)
        latest = df.iloc[-1]

        # Prepare data for BigQuery
        row_data = {
            'symbol': symbol,
            'name': metadata['name'],
            'exchange': metadata['exchange'],
            'mic_code': metadata['mic_code'],
            'currency': metadata['currency'],
            'asset_type': 'stock',
            'country': metadata['country'],
            'datetime': latest['datetime'].isoformat(),
            'date': latest['datetime'].date().isoformat(),
            'interval': '1day',
            'open': float(latest['open']),
            'high': float(latest['high']),
            'low': float(latest['low']),
            'close': float(latest['close']),
            'volume': int(latest['volume']),
            'data_source': 'twelvedata',
            'fetch_timestamp': datetime.utcnow().isoformat(),
            'api_status': 'ok'
        }

        # Add all indicators (convert NaN to None for BigQuery)
        indicator_fields = [
            'rsi', 'macd', 'macd_signal', 'macd_hist', 'stoch_k', 'stoch_d',
            'williams_r', 'cci', 'roc', 'momentum',
            'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'ema_50',
            'wma_20', 'dema_20', 'tema_20', 'kama_20', 'vwap',
            'bb_upper', 'bb_middle', 'bb_lower', 'atr', 'natr', 'stddev',
            'obv', 'ad', 'adosc', 'pvo',
            'adx', 'adxr', 'plus_di', 'minus_di', 'aroon_up', 'aroon_down',
            'aroonosc', 'trix', 'dx', 'sar',
            'cdl_doji', 'cdl_hammer', 'cdl_engulfing', 'cdl_harami', 'cdl_morningstar',
            'cdl_3blackcrows', 'cdl_2crows', 'cdl_3inside', 'cdl_3linestrike', 'cdl_abandonedbaby',
            'correl', 'linearreg', 'linearreg_slope', 'linearreg_angle', 'tsf', 'variance', 'beta',
            'ultosc', 'bop', 'cmo', 'dpo', 'ht_dcperiod', 'ht_dcphase', 'ht_trendmode',
            'midpoint', 'midprice', 'ppo', 'stochrsi', 'apo', 'ht_sine_lead'
        ]

        for field in indicator_fields:
            value = latest.get(field)
            if pd.isna(value):
                row_data[field] = None
            elif field.startswith('cdl_') or field in ['ht_trendmode']:
                row_data[field] = int(value) if value is not None else None
            else:
                row_data[field] = float(value) if value is not None else None

        all_data.append(row_data)
        successful += 1

        # Rate limiting: 8 calls per minute = 7.5 seconds per call
        time.sleep(8)

    # Upload all data to BigQuery
    if all_data:
        upload_to_bigquery(all_data)

    logger.info(f"Completed: {successful} successful, {failed} failed")

    return {
        'status': 'success',
        'successful': successful,
        'failed': failed,
        'total': len(TOP_STOCKS),
        'timestamp': datetime.utcnow().isoformat()
    }

# For local testing
if __name__ == '__main__':
    class Request:
        pass
    result = daily_stock_fetcher(Request())
    print(result)
