#!/usr/bin/env python3
"""
Backfill Remaining 104 Stocks with ALL 97 Fields
Uses same indicator calculations as QQQ/SPY backfill
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from google.cloud import bigquery

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TABLE_NAME = 'stocks_daily_clean'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'  # CORRECT API KEY
BASE_URL = 'https://api.twelvedata.com'

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# All 106 stocks - QQQ and SPY already done
ALL_STOCKS = [
    'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'META', 'TSLA', 'BRK.B', 'UNH', 'JNJ',
    'V', 'XOM', 'JPM', 'MA', 'PG', 'HD', 'CVX', 'MRK', 'ABBV', 'LLY',
    'PEP', 'KO', 'AVGO', 'COST', 'TMO', 'MCD', 'WMT', 'CSCO', 'ABT', 'ACN',
    'CRM', 'DHR', 'NEE', 'VZ', 'ADBE', 'NKE', 'PM', 'TXN', 'BMY', 'UNP',
    'RTX', 'HON', 'AMGN', 'IBM', 'ORCL', 'QCOM', 'SBUX', 'GE', 'CAT', 'DE',
    'BA', 'GS', 'AMD', 'LOW', 'INTC', 'PFE', 'MMM', 'UPS', 'DIS', 'MS',
    'AXP', 'BKNG', 'INTU', 'GILD', 'MDLZ', 'ADI', 'REGN', 'VRTX', 'MU', 'NOW',
    'SYK', 'CME', 'BLK', 'PGR', 'CI', 'BSX', 'SPGI', 'PLD', 'FI', 'ZTS',
    'ELV', 'BDX', 'AMAT', 'EOG', 'CVS', 'COP', 'PNC', 'CB', 'SO', 'T',
    'SLB', 'SCHW', 'TMUS', 'BAC', 'DUK', 'TJX', 'NOC', 'ADP', 'C', 'USB',
    'LMT', 'MDT', 'CL', 'AIG', 'PYPL', 'CMCSA'
]

DONE_SYMBOLS = ['QQQ', 'SPY']  # Already backfilled with 5000 rows

# Stock metadata - for metadata fields
STOCK_INFO = {
    'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology', 'industry': 'Consumer Electronics', 'exchange': 'NASDAQ', 'mic_code': 'XNAS'},
    'MSFT': {'name': 'Microsoft Corporation', 'sector': 'Technology', 'industry': 'Software', 'exchange': 'NASDAQ', 'mic_code': 'XNAS'},
    'AMZN': {'name': 'Amazon.com Inc.', 'sector': 'Consumer Cyclical', 'industry': 'Internet Retail', 'exchange': 'NASDAQ', 'mic_code': 'XNAS'},
    'NVDA': {'name': 'NVIDIA Corporation', 'sector': 'Technology', 'industry': 'Semiconductors', 'exchange': 'NASDAQ', 'mic_code': 'XNAS'},
    'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology', 'industry': 'Internet Services', 'exchange': 'NASDAQ', 'mic_code': 'XNAS'},
    'META': {'name': 'Meta Platforms Inc.', 'sector': 'Technology', 'industry': 'Internet Services', 'exchange': 'NASDAQ', 'mic_code': 'XNAS'},
    'TSLA': {'name': 'Tesla Inc.', 'sector': 'Consumer Cyclical', 'industry': 'Auto Manufacturers', 'exchange': 'NASDAQ', 'mic_code': 'XNAS'},
    'BRK.B': {'name': 'Berkshire Hathaway Inc.', 'sector': 'Financial Services', 'industry': 'Insurance', 'exchange': 'NYSE', 'mic_code': 'XNYS'},
    'UNH': {'name': 'UnitedHealth Group Inc.', 'sector': 'Healthcare', 'industry': 'Healthcare Plans', 'exchange': 'NYSE', 'mic_code': 'XNYS'},
    'JNJ': {'name': 'Johnson & Johnson', 'sector': 'Healthcare', 'industry': 'Drug Manufacturers', 'exchange': 'NYSE', 'mic_code': 'XNYS'},
    # ... more stocks will use defaults
}

# ============================================================
# TECHNICAL INDICATORS - ALL 97 FIELDS
# ============================================================

def calculate_sma(series, period):
    return series.rolling(window=period, min_periods=period).mean()

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False, min_periods=period).mean()

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period, min_periods=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=period).mean()
    rs = gain / loss
    return (100 - (100 / (1 + rs))).replace([np.inf, -np.inf], np.nan)

def calculate_macd(series, fast=12, slow=26, signal=9):
    ema_fast = calculate_ema(series, fast)
    ema_slow = calculate_ema(series, slow)
    macd = ema_fast - ema_slow
    signal_line = calculate_ema(macd, signal)
    histogram = macd - signal_line
    return macd, signal_line, histogram

def calculate_bollinger_bands(series, period=20, std_dev=2):
    sma = calculate_sma(series, period)
    std = series.rolling(window=period, min_periods=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower

def calculate_stochastic(high, low, close, k_period=14, d_period=3):
    lowest_low = low.rolling(window=k_period, min_periods=k_period).min()
    highest_high = high.rolling(window=k_period, min_periods=k_period).max()
    k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    d = k.rolling(window=d_period, min_periods=d_period).mean()
    return k.replace([np.inf, -np.inf], np.nan), d.replace([np.inf, -np.inf], np.nan)

def calculate_cci(high, low, close, period=20):
    tp = (high + low + close) / 3
    sma_tp = tp.rolling(window=period, min_periods=period).mean()
    mean_dev = tp.rolling(window=period, min_periods=period).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    return ((tp - sma_tp) / (0.015 * mean_dev)).replace([np.inf, -np.inf], np.nan)

def calculate_williams_r(high, low, close, period=14):
    highest_high = high.rolling(window=period, min_periods=period).max()
    lowest_low = low.rolling(window=period, min_periods=period).min()
    return (-100 * (highest_high - close) / (highest_high - lowest_low)).replace([np.inf, -np.inf], np.nan)

def calculate_atr(high, low, close, period=14):
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period, min_periods=period).mean()

def calculate_adx(high, low, close, period=14):
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    atr = calculate_atr(high, low, close, period)
    plus_di = 100 * calculate_ema(plus_dm, period) / atr
    minus_di = 100 * calculate_ema(minus_dm, period) / atr
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = calculate_ema(dx, period)
    return adx.replace([np.inf, -np.inf], np.nan), plus_di.replace([np.inf, -np.inf], np.nan), minus_di.replace([np.inf, -np.inf], np.nan)

def calculate_obv(close, volume):
    direction = np.sign(close.diff())
    obv = (direction * volume).cumsum()
    return obv

def calculate_mfi(high, low, close, volume, period=14):
    tp = (high + low + close) / 3
    raw_money_flow = tp * volume
    positive_flow = raw_money_flow.where(tp > tp.shift(1), 0).rolling(window=period, min_periods=period).sum()
    negative_flow = raw_money_flow.where(tp < tp.shift(1), 0).rolling(window=period, min_periods=period).sum()
    mfi = 100 - (100 / (1 + positive_flow / negative_flow))
    return mfi.replace([np.inf, -np.inf], np.nan)

def calculate_cmf(high, low, close, volume, period=20):
    mfm = ((close - low) - (high - close)) / (high - low)
    mfv = mfm * volume
    cmf = mfv.rolling(window=period, min_periods=period).sum() / volume.rolling(window=period, min_periods=period).sum()
    return cmf.replace([np.inf, -np.inf], np.nan)

def calculate_kama(series, period=10, fast=2, slow=30):
    change = abs(series - series.shift(period))
    volatility = abs(series.diff()).rolling(window=period, min_periods=period).sum()
    er = change / volatility
    fast_sc = 2 / (fast + 1)
    slow_sc = 2 / (slow + 1)
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
    kama = series.copy()
    for i in range(period, len(series)):
        if pd.notna(sc.iloc[i]) and pd.notna(kama.iloc[i-1]):
            kama.iloc[i] = kama.iloc[i-1] + sc.iloc[i] * (series.iloc[i] - kama.iloc[i-1])
    return kama.replace([np.inf, -np.inf], np.nan)

def calculate_trix(series, period=15):
    ema1 = calculate_ema(series, period)
    ema2 = calculate_ema(ema1, period)
    ema3 = calculate_ema(ema2, period)
    return (100 * ema3.pct_change()).replace([np.inf, -np.inf], np.nan)

def calculate_roc(series, period=12):
    return ((series - series.shift(period)) / series.shift(period) * 100).replace([np.inf, -np.inf], np.nan)

def calculate_pvo(volume, fast=12, slow=26, signal=9):
    ema_fast = calculate_ema(volume, fast)
    ema_slow = calculate_ema(volume, slow)
    return ((ema_fast - ema_slow) / ema_slow * 100).replace([np.inf, -np.inf], np.nan)

def calculate_ppo(series, fast=12, slow=26):
    ema_fast = calculate_ema(series, fast)
    ema_slow = calculate_ema(series, slow)
    return ((ema_fast - ema_slow) / ema_slow * 100).replace([np.inf, -np.inf], np.nan)

def calculate_ultimate_oscillator(high, low, close, period1=7, period2=14, period3=28):
    bp = close - pd.concat([low, close.shift(1)], axis=1).min(axis=1)
    tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
    avg1 = bp.rolling(window=period1, min_periods=period1).sum() / tr.rolling(window=period1, min_periods=period1).sum()
    avg2 = bp.rolling(window=period2, min_periods=period2).sum() / tr.rolling(window=period2, min_periods=period2).sum()
    avg3 = bp.rolling(window=period3, min_periods=period3).sum() / tr.rolling(window=period3, min_periods=period3).sum()
    return (100 * (4 * avg1 + 2 * avg2 + avg3) / 7).replace([np.inf, -np.inf], np.nan)

def calculate_awesome_oscillator(high, low, fast=5, slow=34):
    mp = (high + low) / 2
    return (calculate_sma(mp, fast) - calculate_sma(mp, slow)).replace([np.inf, -np.inf], np.nan)

def calculate_ichimoku(high, low, close, tenkan=9, kijun=26, senkou_b=52):
    tenkan_sen = (high.rolling(window=tenkan, min_periods=tenkan).max() + low.rolling(window=tenkan, min_periods=tenkan).min()) / 2
    kijun_sen = (high.rolling(window=kijun, min_periods=kijun).max() + low.rolling(window=kijun, min_periods=kijun).min()) / 2
    senkou_a = (tenkan_sen + kijun_sen) / 2
    senkou_b_line = (high.rolling(window=senkou_b, min_periods=senkou_b).max() + low.rolling(window=senkou_b, min_periods=senkou_b).min()) / 2
    chikou = close.shift(-kijun)
    return tenkan_sen, kijun_sen, senkou_a, senkou_b_line, chikou

# ============================================================
# FETCH AND CALCULATE ALL INDICATORS
# ============================================================

def fetch_ohlcv_data(symbol, outputsize=5000):
    """Fetch OHLCV data from TwelveData API"""
    url = f"{BASE_URL}/time_series"
    params = {
        'symbol': symbol,
        'interval': '1day',
        'outputsize': outputsize,
        'apikey': TWELVEDATA_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'values' not in data:
        print(f"  Error fetching {symbol}: {data.get('message', 'Unknown error')}")
        return None

    df = pd.DataFrame(data['values'])
    df['datetime'] = pd.to_datetime(df['datetime'])
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.sort_values('datetime').reset_index(drop=True)
    return df

def calculate_all_indicators(df, symbol):
    """Calculate all 97 fields"""
    print(f"  Calculating indicators for {symbol}...")

    # Basic OHLCV
    df['symbol'] = symbol
    df['previous_close'] = df['close'].shift(1)
    df['change'] = df['close'] - df['previous_close']
    df['percent_change'] = (df['change'] / df['previous_close'] * 100).replace([np.inf, -np.inf], np.nan)
    df['high_low'] = df['high'] - df['low']
    df['pct_high_low'] = (df['high_low'] / df['low'] * 100).replace([np.inf, -np.inf], np.nan)

    # 52-week high/low
    df['week_52_high'] = df['high'].rolling(window=252, min_periods=1).max()
    df['week_52_low'] = df['low'].rolling(window=252, min_periods=1).min()

    # Average volume
    df['average_volume'] = df['volume'].rolling(window=20, min_periods=1).mean().fillna(0).astype(int)

    # RSI
    df['rsi'] = calculate_rsi(df['close'])

    # MACD
    df['macd'], df['macd_signal'], df['macd_histogram'] = calculate_macd(df['close'])

    # Stochastic
    df['stoch_k'], df['stoch_d'] = calculate_stochastic(df['high'], df['low'], df['close'])

    # CCI
    df['cci'] = calculate_cci(df['high'], df['low'], df['close'])

    # Williams %R
    df['williams_r'] = calculate_williams_r(df['high'], df['low'], df['close'])

    # Momentum
    df['momentum'] = df['close'] - df['close'].shift(10)

    # Moving Averages
    df['sma_20'] = calculate_sma(df['close'], 20)
    df['sma_50'] = calculate_sma(df['close'], 50)
    df['sma_200'] = calculate_sma(df['close'], 200)
    df['ema_12'] = calculate_ema(df['close'], 12)
    df['ema_20'] = calculate_ema(df['close'], 20)
    df['ema_26'] = calculate_ema(df['close'], 26)
    df['ema_50'] = calculate_ema(df['close'], 50)
    df['ema_200'] = calculate_ema(df['close'], 200)
    df['kama'] = calculate_kama(df['close'])

    # Bollinger Bands
    df['bollinger_upper'], df['bollinger_middle'], df['bollinger_lower'] = calculate_bollinger_bands(df['close'])
    df['bb_width'] = ((df['bollinger_upper'] - df['bollinger_lower']) / df['bollinger_middle'] * 100).replace([np.inf, -np.inf], np.nan)

    # ADX
    df['adx'], df['plus_di'], df['minus_di'] = calculate_adx(df['high'], df['low'], df['close'])

    # ATR
    df['atr'] = calculate_atr(df['high'], df['low'], df['close'])

    # TRIX
    df['trix'] = calculate_trix(df['close'])

    # ROC
    df['roc'] = calculate_roc(df['close'])

    # OBV
    df['obv'] = calculate_obv(df['close'], df['volume'])

    # PVO
    df['pvo'] = calculate_pvo(df['volume'])

    # PPO
    df['ppo'] = calculate_ppo(df['close'])

    # Ultimate Oscillator
    df['ultimate_osc'] = calculate_ultimate_oscillator(df['high'], df['low'], df['close'])

    # Awesome Oscillator
    df['awesome_osc'] = calculate_awesome_oscillator(df['high'], df['low'])

    # Log return
    df['log_return'] = (np.log(df['close'] / df['close'].shift(1))).replace([np.inf, -np.inf], np.nan)

    # Period returns
    df['return_2w'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10) * 100).replace([np.inf, -np.inf], np.nan)
    df['return_4w'] = ((df['close'] - df['close'].shift(20)) / df['close'].shift(20) * 100).replace([np.inf, -np.inf], np.nan)

    # Price vs MA percentages
    df['close_vs_sma20_pct'] = ((df['close'] - df['sma_20']) / df['sma_20'] * 100).replace([np.inf, -np.inf], np.nan)
    df['close_vs_sma50_pct'] = ((df['close'] - df['sma_50']) / df['sma_50'] * 100).replace([np.inf, -np.inf], np.nan)
    df['close_vs_sma200_pct'] = ((df['close'] - df['sma_200']) / df['sma_200'] * 100).replace([np.inf, -np.inf], np.nan)

    # RSI features
    df['rsi_slope'] = df['rsi'].diff(5).replace([np.inf, -np.inf], np.nan)
    df['rsi_zscore'] = ((df['rsi'] - df['rsi'].rolling(window=20, min_periods=20).mean()) / df['rsi'].rolling(window=20, min_periods=20).std()).replace([np.inf, -np.inf], np.nan)
    df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
    df['rsi_oversold'] = (df['rsi'] < 30).astype(int)

    # MACD cross
    df['macd_cross'] = (df['macd'] > df['macd_signal']).astype(int)

    # EMA slopes
    df['ema20_slope'] = df['ema_20'].diff(5).replace([np.inf, -np.inf], np.nan)
    df['ema50_slope'] = df['ema_50'].diff(5).replace([np.inf, -np.inf], np.nan)

    # ATR features
    df['atr_zscore'] = ((df['atr'] - df['atr'].rolling(window=20, min_periods=20).mean()) / df['atr'].rolling(window=20, min_periods=20).std()).replace([np.inf, -np.inf], np.nan)
    df['atr_slope'] = df['atr'].diff(5).replace([np.inf, -np.inf], np.nan)

    # Volume features
    df['volume_zscore'] = ((df['volume'] - df['volume'].rolling(window=20, min_periods=20).mean()) / df['volume'].rolling(window=20, min_periods=20).std()).replace([np.inf, -np.inf], np.nan)
    df['volume_ratio'] = (df['volume'] / df['volume'].rolling(window=20, min_periods=1).mean()).replace([np.inf, -np.inf], np.nan)

    # Pivot points
    df['pivot_high_flag'] = ((df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1))).astype(int)
    df['pivot_low_flag'] = ((df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1))).astype(int)

    # Distance to pivots
    pivot_highs = df['high'].where(df['pivot_high_flag'] == 1).ffill()
    pivot_lows = df['low'].where(df['pivot_low_flag'] == 1).ffill()
    df['dist_to_pivot_high'] = ((df['close'] - pivot_highs) / pivot_highs * 100).replace([np.inf, -np.inf], np.nan)
    df['dist_to_pivot_low'] = ((df['close'] - pivot_lows) / pivot_lows * 100).replace([np.inf, -np.inf], np.nan)

    # Regime indicators
    df['trend_regime'] = (df['close'] > df['sma_200']).astype(int)
    df['vol_regime'] = (df['atr'] > df['atr'].rolling(window=50, min_periods=50).mean()).astype(int)

    # Regime confidence
    trend_strength = abs(df['close_vs_sma200_pct']) / 20
    df['regime_confidence'] = trend_strength.clip(0, 1).replace([np.inf, -np.inf], np.nan)

    # MFI
    df['mfi'] = calculate_mfi(df['high'], df['low'], df['close'], df['volume'])

    # CMF
    df['cmf'] = calculate_cmf(df['high'], df['low'], df['close'], df['volume'])

    # Ichimoku
    df['ichimoku_tenkan'], df['ichimoku_kijun'], df['ichimoku_senkou_a'], df['ichimoku_senkou_b'], df['ichimoku_chikou'] = calculate_ichimoku(df['high'], df['low'], df['close'])

    # VWAP (daily approximation)
    df['vwap_daily'] = ((df['high'] + df['low'] + df['close']) / 3).replace([np.inf, -np.inf], np.nan)
    df['vwap_weekly'] = df['vwap_daily'].rolling(window=5, min_periods=1).mean()

    # Volume profile placeholders
    df['volume_profile_poc'] = df['close'].rolling(window=20, min_periods=1).median()
    df['volume_profile_vah'] = df['high'].rolling(window=20, min_periods=1).quantile(0.7)
    df['volume_profile_val'] = df['low'].rolling(window=20, min_periods=1).quantile(0.3)

    # Add metadata fields
    info = STOCK_INFO.get(symbol, {
        'name': symbol,
        'sector': 'Unknown',
        'industry': 'Unknown',
        'exchange': 'NYSE' if symbol not in ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'META', 'TSLA', 'AMD', 'INTC', 'QCOM', 'AVGO', 'CSCO', 'ADBE', 'ORCL', 'COST', 'SBUX', 'INTU', 'AMGN', 'GILD', 'REGN', 'VRTX', 'ADI', 'MU', 'AMAT', 'BKNG'] else 'NASDAQ',
        'mic_code': 'XNYS' if symbol not in ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'META', 'TSLA', 'AMD', 'INTC', 'QCOM', 'AVGO', 'CSCO', 'ADBE', 'ORCL', 'COST', 'SBUX', 'INTU', 'AMGN', 'GILD', 'REGN', 'VRTX', 'ADI', 'MU', 'AMAT', 'BKNG'] else 'XNAS'
    })

    df['name'] = info.get('name', symbol)
    df['sector'] = info.get('sector', 'Unknown')
    df['industry'] = info.get('industry', 'Unknown')
    df['asset_type'] = 'stock'
    df['exchange'] = info.get('exchange', 'NYSE')
    df['mic_code'] = info.get('mic_code', 'XNYS')
    df['country'] = 'United States'
    df['currency'] = 'USD'
    df['type'] = 'stock'
    df['timestamp'] = df['datetime'].astype('int64') // 10**9
    df['data_source'] = 'twelvedata'
    df['created_at'] = pd.Timestamp.now(tz='UTC')
    df['updated_at'] = pd.Timestamp.now(tz='UTC')

    return df

def delete_existing_data(symbol):
    """Delete existing data for symbol before inserting new"""
    query = f"""
    DELETE FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}`
    WHERE symbol = '{symbol}'
    """
    try:
        client.query(query).result()
        print(f"  Deleted existing data for {symbol}")
    except Exception as e:
        print(f"  No existing data to delete for {symbol}")

def upload_to_bigquery(df, symbol):
    """Upload dataframe to BigQuery"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}"

    # Delete existing data first
    delete_existing_data(symbol)

    # Ensure proper data types
    df['average_volume'] = df['average_volume'].fillna(0).astype(int)
    df['obv'] = df['obv'].fillna(0).astype(int)

    # Convert datetime to timestamp for BigQuery
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Replace inf with NaN
    for col in df.select_dtypes(include=[np.floating]).columns:
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)

    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    print(f"  Uploaded {len(df)} rows for {symbol} to BigQuery")

def backfill_stock(symbol):
    """Backfill a single stock"""
    print(f"\nProcessing {symbol}...")

    # Fetch data
    df = fetch_ohlcv_data(symbol, outputsize=5000)
    if df is None or len(df) == 0:
        print(f"  FAILED: No data returned for {symbol}")
        return False

    print(f"  Fetched {len(df)} rows (from {df['datetime'].min()} to {df['datetime'].max()})")

    # Calculate indicators
    df = calculate_all_indicators(df, symbol)

    # Upload to BigQuery
    upload_to_bigquery(df, symbol)

    return True

def main():
    print("=" * 60)
    print("BACKFILL REMAINING STOCKS - 97 FIELDS")
    print("=" * 60)
    print(f"Using API Key: {TWELVEDATA_API_KEY[:10]}...")
    print(f"Total stocks to process: {len(ALL_STOCKS)}")
    print(f"Already done: {DONE_SYMBOLS}")
    print()

    # Get remaining stocks (not QQQ/SPY)
    remaining = [s for s in ALL_STOCKS if s not in DONE_SYMBOLS]
    print(f"Remaining stocks: {len(remaining)}")

    successful = 0
    failed = []

    for i, symbol in enumerate(remaining, 1):
        print(f"\n{'='*40}")
        print(f"Stock {i}/{len(remaining)}: {symbol}")
        print(f"{'='*40}")

        try:
            success = backfill_stock(symbol)
            if success:
                successful += 1
            else:
                failed.append(symbol)
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            failed.append(symbol)

        # Rate limit: wait 65 seconds between stocks to avoid TwelveData limit
        if i < len(remaining):
            print(f"\n  Waiting 65 seconds for API rate limit...")
            time.sleep(65)

    print("\n" + "=" * 60)
    print("BACKFILL COMPLETE")
    print("=" * 60)
    print(f"Successful: {successful}/{len(remaining)}")
    print(f"Failed: {len(failed)}")
    if failed:
        print(f"Failed symbols: {failed}")

if __name__ == '__main__':
    main()
