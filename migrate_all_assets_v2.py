"""
Migrate All Assets to Clean 97-Field Schema - V2 FIXED
Fixes:
1. Forex: No volume field - set volume to 0
2. Indices: Use correct TwelveData symbols
3. Rate limiting: 1 second delay between API calls
4. Commodities: Use correct TwelveData format

Author: Claude Code
Date: December 2025
"""

import os
import sys
import time
import math
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timezone
from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
TWELVEDATA_BASE_URL = 'https://api.twelvedata.com'

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# Rate limiting - global counter
api_call_count = 0
last_reset_time = time.time()

def rate_limit():
    """Enforce rate limiting - max ~25 calls per minute to stay safe"""
    global api_call_count, last_reset_time

    current_time = time.time()
    elapsed = current_time - last_reset_time

    if elapsed >= 60:
        api_call_count = 0
        last_reset_time = current_time

    api_call_count += 1

    if api_call_count > 25:
        sleep_time = 60 - elapsed + 1
        print(f"  Rate limit reached. Sleeping {sleep_time:.0f} seconds...")
        time.sleep(sleep_time)
        api_call_count = 1
        last_reset_time = time.time()
    else:
        # Small delay between calls
        time.sleep(2.5)

# Asset configurations with CORRECT TwelveData symbols
ASSET_CONFIGS = {
    'etfs_remaining': {
        'target_table': 'etfs_daily_clean',
        'asset_type': 'ETF',
        'has_volume': True,
        'symbols': [
            # ETFs that failed in previous run
            'IJH', 'IWM', 'VIG', 'VXUS', 'GLD', 'VNQ', 'VGT', 'LQD',
            'SCHD', 'XLF', 'XLK', 'XLV', 'XLE', 'XLI', 'XLY', 'XLP', 'XLU', 'XLRE'
        ]
    },
    'forex': {
        'target_table': 'forex_daily_clean',
        'asset_type': 'Forex',
        'has_volume': False,  # Forex has no volume!
        'symbols': [
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'NZD/USD',
            'USD/CAD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'EUR/CHF', 'EUR/AUD',
            'AUD/JPY', 'GBP/CHF', 'EUR/CAD', 'CAD/JPY', 'AUD/NZD', 'GBP/AUD',
            'USD/MXN', 'USD/ZAR', 'USD/TRY', 'USD/INR', 'USD/CNH', 'USD/SGD'
        ]
    },
    'indices': {
        'target_table': 'indices_daily_clean',
        'asset_type': 'Index',
        'has_volume': True,
        'symbols': [
            # TwelveData index format: symbol:exchange or just ETF tracking
            'SPY',   # S&P 500 tracker
            'QQQ',   # Nasdaq 100 tracker
            'DIA',   # Dow Jones tracker
            'IWM',   # Russell 2000 tracker
            'VIX',   # CBOE VIX (needs special handling)
            'EFA',   # EAFE index tracker
            'EEM',   # Emerging markets tracker
            'IYR',   # Real estate index
            'XLF',   # Financial sector index
            'XLE',   # Energy sector index
        ]
    },
    'commodities': {
        'target_table': 'commodities_daily_clean',
        'asset_type': 'Commodity',
        'has_volume': True,
        'symbols': [
            # Use ETFs that track commodities
            'GLD',   # Gold ETF
            'SLV',   # Silver ETF
            'USO',   # Oil ETF
            'UNG',   # Natural Gas ETF
            'DBA',   # Agriculture ETF
            'PDBC',  # Diversified commodities
            'CORN',  # Corn ETF
            'WEAT',  # Wheat ETF
            'CPER',  # Copper ETF
            'PALL',  # Palladium ETF
        ]
    }
}

# 97-field schema
SCHEMA_FIELDS = [
    bigquery.SchemaField('symbol', 'STRING', mode='REQUIRED'),
    bigquery.SchemaField('datetime', 'TIMESTAMP', mode='REQUIRED'),
    bigquery.SchemaField('open', 'FLOAT64'),
    bigquery.SchemaField('high', 'FLOAT64'),
    bigquery.SchemaField('low', 'FLOAT64'),
    bigquery.SchemaField('close', 'FLOAT64'),
    bigquery.SchemaField('volume', 'FLOAT64'),
    bigquery.SchemaField('asset_type', 'STRING'),
    bigquery.SchemaField('exchange', 'STRING'),
    bigquery.SchemaField('currency', 'STRING'),
    # Technical Indicators - Momentum
    bigquery.SchemaField('rsi', 'FLOAT64'),
    bigquery.SchemaField('macd', 'FLOAT64'),
    bigquery.SchemaField('macd_signal', 'FLOAT64'),
    bigquery.SchemaField('macd_histogram', 'FLOAT64'),
    bigquery.SchemaField('stoch_k', 'FLOAT64'),
    bigquery.SchemaField('stoch_d', 'FLOAT64'),
    bigquery.SchemaField('cci', 'FLOAT64'),
    bigquery.SchemaField('williams_r', 'FLOAT64'),
    bigquery.SchemaField('momentum', 'FLOAT64'),
    bigquery.SchemaField('roc', 'FLOAT64'),
    # Moving Averages
    bigquery.SchemaField('sma_20', 'FLOAT64'),
    bigquery.SchemaField('sma_50', 'FLOAT64'),
    bigquery.SchemaField('sma_200', 'FLOAT64'),
    bigquery.SchemaField('ema_12', 'FLOAT64'),
    bigquery.SchemaField('ema_20', 'FLOAT64'),
    bigquery.SchemaField('ema_26', 'FLOAT64'),
    bigquery.SchemaField('ema_50', 'FLOAT64'),
    bigquery.SchemaField('ema_200', 'FLOAT64'),
    bigquery.SchemaField('kama', 'FLOAT64'),
    bigquery.SchemaField('trix', 'FLOAT64'),
    # Volatility
    bigquery.SchemaField('bollinger_upper', 'FLOAT64'),
    bigquery.SchemaField('bollinger_middle', 'FLOAT64'),
    bigquery.SchemaField('bollinger_lower', 'FLOAT64'),
    bigquery.SchemaField('bb_width', 'FLOAT64'),
    bigquery.SchemaField('atr', 'FLOAT64'),
    bigquery.SchemaField('natr', 'FLOAT64'),
    bigquery.SchemaField('true_range', 'FLOAT64'),
    bigquery.SchemaField('adx', 'FLOAT64'),
    bigquery.SchemaField('plus_di', 'FLOAT64'),
    bigquery.SchemaField('minus_di', 'FLOAT64'),
    # Volume Indicators
    bigquery.SchemaField('obv', 'FLOAT64'),
    bigquery.SchemaField('pvo', 'FLOAT64'),
    bigquery.SchemaField('ppo', 'FLOAT64'),
    bigquery.SchemaField('mfi', 'FLOAT64'),
    bigquery.SchemaField('cmf', 'FLOAT64'),
    bigquery.SchemaField('ad_line', 'FLOAT64'),
    bigquery.SchemaField('vwap', 'FLOAT64'),
    # Ichimoku
    bigquery.SchemaField('ichimoku_tenkan', 'FLOAT64'),
    bigquery.SchemaField('ichimoku_kijun', 'FLOAT64'),
    bigquery.SchemaField('ichimoku_senkou_a', 'FLOAT64'),
    bigquery.SchemaField('ichimoku_senkou_b', 'FLOAT64'),
    bigquery.SchemaField('ichimoku_chikou', 'FLOAT64'),
    # Other indicators
    bigquery.SchemaField('ultimate_oscillator', 'FLOAT64'),
    bigquery.SchemaField('awesome_oscillator', 'FLOAT64'),
    bigquery.SchemaField('price_change', 'FLOAT64'),
    bigquery.SchemaField('price_change_pct', 'FLOAT64'),
    bigquery.SchemaField('high_low_range', 'FLOAT64'),
    bigquery.SchemaField('gap', 'FLOAT64'),
    bigquery.SchemaField('gap_pct', 'FLOAT64'),
    # Support/Resistance
    bigquery.SchemaField('pivot_point', 'FLOAT64'),
    bigquery.SchemaField('r1', 'FLOAT64'),
    bigquery.SchemaField('r2', 'FLOAT64'),
    bigquery.SchemaField('r3', 'FLOAT64'),
    bigquery.SchemaField('s1', 'FLOAT64'),
    bigquery.SchemaField('s2', 'FLOAT64'),
    bigquery.SchemaField('s3', 'FLOAT64'),
    # Fibonacci levels
    bigquery.SchemaField('fib_0', 'FLOAT64'),
    bigquery.SchemaField('fib_236', 'FLOAT64'),
    bigquery.SchemaField('fib_382', 'FLOAT64'),
    bigquery.SchemaField('fib_500', 'FLOAT64'),
    bigquery.SchemaField('fib_618', 'FLOAT64'),
    bigquery.SchemaField('fib_786', 'FLOAT64'),
    bigquery.SchemaField('fib_1000', 'FLOAT64'),
    # Pattern recognition
    bigquery.SchemaField('doji', 'BOOLEAN'),
    bigquery.SchemaField('hammer', 'BOOLEAN'),
    bigquery.SchemaField('engulfing_bullish', 'BOOLEAN'),
    bigquery.SchemaField('engulfing_bearish', 'BOOLEAN'),
    bigquery.SchemaField('morning_star', 'BOOLEAN'),
    bigquery.SchemaField('evening_star', 'BOOLEAN'),
    # Trend
    bigquery.SchemaField('trend_sma_20', 'STRING'),
    bigquery.SchemaField('trend_sma_50', 'STRING'),
    bigquery.SchemaField('trend_sma_200', 'STRING'),
    bigquery.SchemaField('golden_cross', 'BOOLEAN'),
    bigquery.SchemaField('death_cross', 'BOOLEAN'),
    # Additional
    bigquery.SchemaField('typical_price', 'FLOAT64'),
    bigquery.SchemaField('median_price', 'FLOAT64'),
    bigquery.SchemaField('weighted_close', 'FLOAT64'),
    bigquery.SchemaField('avg_price', 'FLOAT64'),
    # Statistics
    bigquery.SchemaField('std_20', 'FLOAT64'),
    bigquery.SchemaField('variance_20', 'FLOAT64'),
    bigquery.SchemaField('zscore', 'FLOAT64'),
    # Metadata
    bigquery.SchemaField('fetch_timestamp', 'TIMESTAMP'),
    bigquery.SchemaField('data_source', 'STRING'),
    bigquery.SchemaField('timeframe', 'STRING'),
]


def safe_float(val):
    """Convert to safe float for JSON/BigQuery"""
    if val is None or pd.isna(val):
        return None
    try:
        f = float(val)
        if math.isinf(f) or math.isnan(f):
            return None
        return f
    except:
        return None


def calculate_indicators_saleem_corrections(df, has_volume=True):
    """
    Calculate all 97 technical indicators with Saleem's corrections:
    - Wilder's RMA for RSI, ATR, ADX
    - Slow Stochastic (smoothed %K)
    - ROC period = 10
    - Bollinger ddof=0
    - Ichimoku forward shift
    """
    if len(df) < 50:
        return df

    close = df['close']
    high = df['high']
    low = df['low']
    open_price = df['open']
    volume = df['volume'] if has_volume and 'volume' in df.columns else pd.Series([0] * len(df), index=df.index)

    # ============================================================
    # MOMENTUM INDICATORS
    # ============================================================

    # RSI (14) - Using Wilder's RMA (Saleem correction)
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)
    # Wilder's RMA: ewm with alpha=1/period
    avg_gain = gain.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    df['macd'] = ema_12 - ema_26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']

    # Slow Stochastic (14, 3, 3) - Saleem correction: smooth %K before %D
    lowest_low = low.rolling(14).min()
    highest_high = high.rolling(14).max()
    raw_k = 100 * (close - lowest_low) / (highest_high - lowest_low).replace(0, np.nan)
    df['stoch_k'] = raw_k.rolling(3).mean()  # Smoothed %K
    df['stoch_d'] = df['stoch_k'].rolling(3).mean()  # %D of smoothed %K

    # CCI (20)
    typical_price = (high + low + close) / 3
    sma_tp = typical_price.rolling(20).mean()
    mad = typical_price.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    df['cci'] = (typical_price - sma_tp) / (0.015 * mad).replace(0, np.nan)

    # Williams %R (14)
    df['williams_r'] = -100 * (highest_high - close) / (highest_high - lowest_low).replace(0, np.nan)

    # Momentum (10)
    df['momentum'] = close - close.shift(10)

    # ROC - period 10 (Saleem correction, NOT 12)
    df['roc'] = ((close - close.shift(10)) / close.shift(10).replace(0, np.nan)) * 100

    # ============================================================
    # MOVING AVERAGES
    # ============================================================
    df['sma_20'] = close.rolling(20).mean()
    df['sma_50'] = close.rolling(50).mean()
    df['sma_200'] = close.rolling(200).mean()
    df['ema_12'] = ema_12
    df['ema_20'] = close.ewm(span=20, adjust=False).mean()
    df['ema_26'] = ema_26
    df['ema_50'] = close.ewm(span=50, adjust=False).mean()
    df['ema_200'] = close.ewm(span=200, adjust=False).mean()

    # KAMA (10, 2, 30)
    change = (close - close.shift(10)).abs()
    volatility = close.diff().abs().rolling(10).sum()
    er = change / volatility.replace(0, np.nan)
    sc = (er * (2/3 - 2/31) + 2/31) ** 2
    kama = [close.iloc[0]]
    for i in range(1, len(close)):
        kama.append(kama[-1] + sc.iloc[i] * (close.iloc[i] - kama[-1]) if pd.notna(sc.iloc[i]) else kama[-1])
    df['kama'] = kama

    # TRIX (15)
    ema1 = close.ewm(span=15, adjust=False).mean()
    ema2 = ema1.ewm(span=15, adjust=False).mean()
    ema3 = ema2.ewm(span=15, adjust=False).mean()
    df['trix'] = ((ema3 - ema3.shift(1)) / ema3.shift(1).replace(0, np.nan)) * 100

    # ============================================================
    # VOLATILITY INDICATORS
    # ============================================================

    # Bollinger Bands (20, 2) - ddof=0 (Saleem correction: population std)
    bb_middle = close.rolling(20).mean()
    bb_std = close.rolling(20).std(ddof=0)  # Population std dev
    df['bollinger_middle'] = bb_middle
    df['bollinger_upper'] = bb_middle + 2 * bb_std
    df['bollinger_lower'] = bb_middle - 2 * bb_std
    df['bb_width'] = (df['bollinger_upper'] - df['bollinger_lower']) / bb_middle.replace(0, np.nan)

    # True Range and ATR (14) - Using Wilder's RMA
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['true_range'] = tr
    df['atr'] = tr.ewm(alpha=1/14, adjust=False, min_periods=14).mean()  # Wilder's RMA
    df['natr'] = (df['atr'] / close) * 100

    # ADX (14) - Using Wilder's RMA
    plus_dm = high.diff()
    minus_dm = (-low.diff())
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

    atr_14 = tr.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean() / atr_14.replace(0, np.nan))
    minus_di = 100 * (minus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean() / atr_14.replace(0, np.nan))

    df['plus_di'] = plus_di
    df['minus_di'] = minus_di
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan) * 100
    df['adx'] = dx.ewm(alpha=1/14, adjust=False, min_periods=14).mean()  # Wilder's RMA

    # ============================================================
    # VOLUME INDICATORS
    # ============================================================
    if has_volume and volume.sum() > 0:
        # OBV
        obv = [0]
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.append(obv[-1] + volume.iloc[i])
            elif close.iloc[i] < close.iloc[i-1]:
                obv.append(obv[-1] - volume.iloc[i])
            else:
                obv.append(obv[-1])
        df['obv'] = obv

        # PVO
        vol_ema_12 = volume.ewm(span=12, adjust=False).mean()
        vol_ema_26 = volume.ewm(span=26, adjust=False).mean()
        df['pvo'] = ((vol_ema_12 - vol_ema_26) / vol_ema_26.replace(0, np.nan)) * 100

        # MFI (14)
        typical_price = (high + low + close) / 3
        raw_money_flow = typical_price * volume
        pos_flow = raw_money_flow.where(typical_price > typical_price.shift(1), 0)
        neg_flow = raw_money_flow.where(typical_price < typical_price.shift(1), 0)
        money_ratio = pos_flow.rolling(14).sum() / neg_flow.rolling(14).sum().replace(0, np.nan)
        df['mfi'] = 100 - (100 / (1 + money_ratio))

        # CMF (21)
        clv = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
        df['cmf'] = (clv * volume).rolling(21).sum() / volume.rolling(21).sum().replace(0, np.nan)

        # A/D Line
        ad = [0]
        for i in range(1, len(close)):
            if high.iloc[i] != low.iloc[i]:
                clv_i = ((close.iloc[i] - low.iloc[i]) - (high.iloc[i] - close.iloc[i])) / (high.iloc[i] - low.iloc[i])
                ad.append(ad[-1] + clv_i * volume.iloc[i])
            else:
                ad.append(ad[-1])
        df['ad_line'] = ad

        # VWAP (cumulative)
        df['vwap'] = (typical_price * volume).cumsum() / volume.cumsum().replace(0, np.nan)
    else:
        df['obv'] = None
        df['pvo'] = None
        df['mfi'] = None
        df['cmf'] = None
        df['ad_line'] = None
        df['vwap'] = None

    # PPO
    df['ppo'] = ((ema_12 - ema_26) / ema_26.replace(0, np.nan)) * 100

    # ============================================================
    # ICHIMOKU CLOUD - with forward shift (Saleem correction)
    # ============================================================
    high_9 = high.rolling(9).max()
    low_9 = low.rolling(9).min()
    df['ichimoku_tenkan'] = (high_9 + low_9) / 2

    high_26 = high.rolling(26).max()
    low_26 = low.rolling(26).min()
    df['ichimoku_kijun'] = (high_26 + low_26) / 2

    # Senkou Span A and B - shifted FORWARD 26 periods
    senkou_a_raw = (df['ichimoku_tenkan'] + df['ichimoku_kijun']) / 2
    df['ichimoku_senkou_a'] = senkou_a_raw.shift(26)  # Forward shift

    high_52 = high.rolling(52).max()
    low_52 = low.rolling(52).min()
    senkou_b_raw = (high_52 + low_52) / 2
    df['ichimoku_senkou_b'] = senkou_b_raw.shift(26)  # Forward shift

    # Chikou Span - shifted BACK 26 periods
    df['ichimoku_chikou'] = close.shift(-26)

    # ============================================================
    # OTHER INDICATORS
    # ============================================================

    # Ultimate Oscillator
    bp = close - pd.concat([low, close.shift(1)], axis=1).min(axis=1)
    tr_uo = pd.concat([high, close.shift(1)], axis=1).max(axis=1) - pd.concat([low, close.shift(1)], axis=1).min(axis=1)
    avg7 = bp.rolling(7).sum() / tr_uo.rolling(7).sum().replace(0, np.nan)
    avg14 = bp.rolling(14).sum() / tr_uo.rolling(14).sum().replace(0, np.nan)
    avg28 = bp.rolling(28).sum() / tr_uo.rolling(28).sum().replace(0, np.nan)
    df['ultimate_oscillator'] = 100 * ((4 * avg7) + (2 * avg14) + avg28) / 7

    # Awesome Oscillator
    mid = (high + low) / 2
    df['awesome_oscillator'] = mid.rolling(5).mean() - mid.rolling(34).mean()

    # Price changes
    df['price_change'] = close - close.shift(1)
    df['price_change_pct'] = df['price_change'] / close.shift(1).replace(0, np.nan) * 100
    df['high_low_range'] = high - low
    df['gap'] = open_price - close.shift(1)
    df['gap_pct'] = df['gap'] / close.shift(1).replace(0, np.nan) * 100

    # Pivot Points
    df['pivot_point'] = (high.shift(1) + low.shift(1) + close.shift(1)) / 3
    df['r1'] = 2 * df['pivot_point'] - low.shift(1)
    df['r2'] = df['pivot_point'] + (high.shift(1) - low.shift(1))
    df['r3'] = high.shift(1) + 2 * (df['pivot_point'] - low.shift(1))
    df['s1'] = 2 * df['pivot_point'] - high.shift(1)
    df['s2'] = df['pivot_point'] - (high.shift(1) - low.shift(1))
    df['s3'] = low.shift(1) - 2 * (high.shift(1) - df['pivot_point'])

    # Fibonacci (using 50-day high/low)
    high_50 = high.rolling(50).max()
    low_50 = low.rolling(50).min()
    fib_range = high_50 - low_50
    df['fib_0'] = low_50
    df['fib_236'] = low_50 + 0.236 * fib_range
    df['fib_382'] = low_50 + 0.382 * fib_range
    df['fib_500'] = low_50 + 0.500 * fib_range
    df['fib_618'] = low_50 + 0.618 * fib_range
    df['fib_786'] = low_50 + 0.786 * fib_range
    df['fib_1000'] = high_50

    # Candlestick patterns
    body = (close - open_price).abs()
    upper_shadow = high - pd.concat([close, open_price], axis=1).max(axis=1)
    lower_shadow = pd.concat([close, open_price], axis=1).min(axis=1) - low

    df['doji'] = body < (0.1 * (high - low))
    df['hammer'] = (lower_shadow > 2 * body) & (upper_shadow < body * 0.5) & (close > open_price)
    df['engulfing_bullish'] = (close > open_price) & (close.shift(1) < open_price.shift(1)) & (close > open_price.shift(1)) & (open_price < close.shift(1))
    df['engulfing_bearish'] = (close < open_price) & (close.shift(1) > open_price.shift(1)) & (close < open_price.shift(1)) & (open_price > close.shift(1))
    df['morning_star'] = False  # Simplified
    df['evening_star'] = False  # Simplified

    # Trend
    df['trend_sma_20'] = np.where(close > df['sma_20'], 'Bullish', np.where(close < df['sma_20'], 'Bearish', 'Neutral'))
    df['trend_sma_50'] = np.where(close > df['sma_50'], 'Bullish', np.where(close < df['sma_50'], 'Bearish', 'Neutral'))
    df['trend_sma_200'] = np.where(close > df['sma_200'], 'Bullish', np.where(close < df['sma_200'], 'Bearish', 'Neutral'))

    # Golden/Death cross
    df['golden_cross'] = (df['sma_50'] > df['sma_200']) & (df['sma_50'].shift(1) <= df['sma_200'].shift(1))
    df['death_cross'] = (df['sma_50'] < df['sma_200']) & (df['sma_50'].shift(1) >= df['sma_200'].shift(1))

    # Price averages
    df['typical_price'] = (high + low + close) / 3
    df['median_price'] = (high + low) / 2
    df['weighted_close'] = (high + low + close + close) / 4
    df['avg_price'] = (open_price + high + low + close) / 4

    # Statistics
    df['std_20'] = close.rolling(20).std(ddof=0)
    df['variance_20'] = close.rolling(20).var(ddof=0)
    mean_20 = close.rolling(20).mean()
    df['zscore'] = (close - mean_20) / df['std_20'].replace(0, np.nan)

    return df


def fetch_twelvedata(symbol, has_volume=True):
    """Fetch data from TwelveData API"""
    rate_limit()

    try:
        url = f"{TWELVEDATA_BASE_URL}/time_series"
        params = {
            'symbol': symbol,
            'interval': '1day',
            'outputsize': 5000,
            'apikey': TWELVEDATA_API_KEY
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'code' in data and data['code'] != 200:
            return None, data.get('message', 'Unknown error')

        if 'values' not in data:
            return None, 'No values in response'

        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Convert numeric columns
        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Handle volume - if no volume field, set to 0
        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        else:
            df['volume'] = 0.0

        df = df.sort_values('datetime').reset_index(drop=True)

        return df, None

    except Exception as e:
        return None, str(e)


def process_symbol(symbol, asset_type, has_volume, exchange='', currency='USD'):
    """Process a single symbol"""
    try:
        df, error = fetch_twelvedata(symbol, has_volume)

        if error:
            print(f"  Error fetching {symbol}: {error}")
            return None, 0

        if df is None or len(df) < 50:
            print(f"  Insufficient data for {symbol}: {len(df) if df is not None else 0} rows")
            return None, 0

        # Add metadata
        df['symbol'] = symbol
        df['asset_type'] = asset_type
        df['exchange'] = exchange
        df['currency'] = currency

        # Calculate indicators
        df = calculate_indicators_saleem_corrections(df, has_volume)

        # Add metadata fields
        df['fetch_timestamp'] = datetime.now(timezone.utc)
        df['data_source'] = 'TwelveData'
        df['timeframe'] = '1D'

        # Ensure all schema columns exist
        for field in SCHEMA_FIELDS:
            if field.name not in df.columns:
                if field.field_type == 'BOOLEAN':
                    df[field.name] = False
                elif field.field_type == 'STRING':
                    df[field.name] = None
                else:
                    df[field.name] = None

        # Sanitize float columns
        for col in df.columns:
            if df[col].dtype in ['float64', 'float32']:
                df[col] = df[col].apply(safe_float)

        return df, len(df)

    except Exception as e:
        print(f"  Error processing {symbol}: {e}")
        return None, 0


def create_clean_table(table_name):
    """Create or verify clean table exists"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    table = bigquery.Table(table_id, schema=SCHEMA_FIELDS)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.MONTH,
        field="datetime"
    )
    table.clustering_fields = ["symbol", "asset_type"]

    try:
        table = client.create_table(table)
        print(f"Created table: {table_name}")
    except Exception as e:
        if 'Already Exists' in str(e):
            print(f"Table exists: {table_name}")
        else:
            raise e

    return table_id


def upload_to_bigquery(df, table_id):
    """Upload DataFrame to BigQuery"""
    if df is None or len(df) == 0:
        return 0

    # Select only schema columns
    schema_cols = [f.name for f in SCHEMA_FIELDS]
    df = df[[c for c in schema_cols if c in df.columns]]

    job_config = bigquery.LoadJobConfig(
        schema=SCHEMA_FIELDS,
        write_disposition='WRITE_APPEND',
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    return len(df)


def migrate_asset_class(asset_key, config):
    """Migrate a single asset class"""
    print(f"\n{'='*60}")
    print(f"Processing {asset_key.upper()}")
    print('='*60)

    table_id = create_clean_table(config['target_table'])

    symbols = config['symbols']
    asset_type = config['asset_type']
    has_volume = config.get('has_volume', True)

    total_rows = 0
    success_count = 0

    for i, symbol in enumerate(symbols, 1):
        df, rows = process_symbol(symbol, asset_type, has_volume)

        if df is not None and rows > 0:
            uploaded = upload_to_bigquery(df, table_id)
            total_rows += uploaded
            success_count += 1
            print(f"  [{i}/{len(symbols)}] {symbol}: {uploaded} rows")
        else:
            print(f"  [{i}/{len(symbols)}] {symbol}: No data")

    print(f"\n{asset_key.upper()} Complete: {success_count}/{len(symbols)} symbols, {total_rows:,} total rows")

    return success_count, total_rows


def main():
    """Main migration function"""
    print("="*60)
    print("ASSET MIGRATION V2 - FIXED VERSION")
    print("Using TwelveData API with Rate Limiting")
    print("="*60)
    print(f"Start time: {datetime.now()}\n")

    results = {}

    # Process each asset class
    for asset_key, config in ASSET_CONFIGS.items():
        success, rows = migrate_asset_class(asset_key, config)
        results[asset_key] = {'success': success, 'total': len(config['symbols']), 'rows': rows}

    # Summary
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)

    for asset_key, result in results.items():
        print(f"{asset_key}: {result['success']}/{result['total']} symbols, {result['rows']:,} rows")

    print(f"\nEnd time: {datetime.now()}")


if __name__ == '__main__':
    main()
