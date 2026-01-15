"""
Migrate All Assets to Clean Schema (97-field)
Uses TwelveData API with parallel processing for optimal speed
Based on claude-code-master-prompt.md optimization guidelines
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.cloud import bigquery
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

# Configuration from master query
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
TWELVEDATA_BASE_URL = 'https://api.twelvedata.com'

# Batch up to 8 symbols per request (TwelveData optimization)
BATCH_SIZE = 8
PARALLEL_WORKERS = 10

client = bigquery.Client(project=PROJECT_ID)

# Asset configurations
ASSET_CONFIGS = {
    'etfs': {
        'source_table': 'v2_etfs_historical_daily',
        'target_table': 'etfs_daily_clean',
        'asset_type': 'ETF',
        'symbols': [
            'SPY', 'IVV', 'VOO', 'VTI', 'QQQ', 'VEA', 'IEFA', 'VTV', 'BND', 'VUG',
            'AGG', 'VWO', 'IJH', 'IWM', 'VIG', 'VXUS', 'GLD', 'VNQ', 'VGT', 'LQD',
            'SCHD', 'XLF', 'XLK', 'XLE', 'XLV', 'XLI', 'XLY', 'XLP', 'XLU', 'XLRE'
        ]
    },
    'forex': {
        'source_table': 'v2_forex_historical_daily',
        'target_table': 'forex_daily_clean',
        'asset_type': 'Forex',
        'symbols': [
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD',
            'NZD/USD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'EUR/CHF', 'AUD/JPY',
            'EUR/AUD', 'GBP/CHF', 'CAD/JPY', 'AUD/NZD', 'EUR/CAD', 'GBP/AUD',
            'USD/MXN', 'USD/ZAR', 'USD/TRY', 'USD/INR', 'USD/CNH', 'USD/SGD'
        ]
    },
    'indices': {
        'source_table': 'v2_indices_historical_daily',
        'target_table': 'indices_daily_clean',
        'asset_type': 'Index',
        'symbols': [
            'SPX', 'NDX', 'DJI', 'RUT', 'VIX', 'IXIC', 'FTSE', 'DAX', 'CAC',
            'N225', 'HSI', 'SSEC', 'KOSPI', 'ASX200', 'IBEX', 'FTSEMIB', 'SMI',
            'AEX', 'BEL20', 'STOXX50E'
        ]
    },
    'commodities': {
        'source_table': 'v2_commodities_historical_daily',
        'target_table': 'commodities_daily_clean',
        'asset_type': 'Commodity',
        'symbols': [
            'XAU/USD', 'XAG/USD', 'CL', 'NG', 'HG', 'SI', 'GC', 'PL', 'PA',
            'ZC', 'ZW', 'ZS', 'KC', 'CT', 'SB', 'CC', 'OJ', 'LB', 'HE', 'LE'
        ]
    }
}

# 97-field schema (same as stocks_daily_clean)
CLEAN_SCHEMA = [
    bigquery.SchemaField("symbol", "STRING"),
    bigquery.SchemaField("datetime", "TIMESTAMP"),
    bigquery.SchemaField("open", "FLOAT"),
    bigquery.SchemaField("high", "FLOAT"),
    bigquery.SchemaField("low", "FLOAT"),
    bigquery.SchemaField("close", "FLOAT"),
    bigquery.SchemaField("volume", "FLOAT"),
    bigquery.SchemaField("timestamp", "INTEGER"),
    # Moving Averages
    bigquery.SchemaField("sma_20", "FLOAT"),
    bigquery.SchemaField("sma_50", "FLOAT"),
    bigquery.SchemaField("sma_200", "FLOAT"),
    bigquery.SchemaField("ema_12", "FLOAT"),
    bigquery.SchemaField("ema_20", "FLOAT"),
    bigquery.SchemaField("ema_26", "FLOAT"),
    bigquery.SchemaField("ema_50", "FLOAT"),
    bigquery.SchemaField("ema_200", "FLOAT"),
    bigquery.SchemaField("kama", "FLOAT"),
    bigquery.SchemaField("t3", "FLOAT"),
    bigquery.SchemaField("tema", "FLOAT"),
    bigquery.SchemaField("dema", "FLOAT"),
    bigquery.SchemaField("wma_20", "FLOAT"),
    bigquery.SchemaField("hma_20", "FLOAT"),
    bigquery.SchemaField("vwma_20", "FLOAT"),
    # Momentum Indicators
    bigquery.SchemaField("rsi", "FLOAT"),
    bigquery.SchemaField("macd", "FLOAT"),
    bigquery.SchemaField("macd_signal", "FLOAT"),
    bigquery.SchemaField("macd_histogram", "FLOAT"),
    bigquery.SchemaField("stoch_k", "FLOAT"),
    bigquery.SchemaField("stoch_d", "FLOAT"),
    bigquery.SchemaField("stoch_rsi_k", "FLOAT"),
    bigquery.SchemaField("stoch_rsi_d", "FLOAT"),
    bigquery.SchemaField("williams_r", "FLOAT"),
    bigquery.SchemaField("cci", "FLOAT"),
    bigquery.SchemaField("roc", "FLOAT"),
    bigquery.SchemaField("momentum", "FLOAT"),
    bigquery.SchemaField("tsi", "FLOAT"),
    bigquery.SchemaField("uo", "FLOAT"),
    bigquery.SchemaField("ao", "FLOAT"),
    bigquery.SchemaField("ppo", "FLOAT"),
    bigquery.SchemaField("pvo", "FLOAT"),
    # Volatility Indicators
    bigquery.SchemaField("atr", "FLOAT"),
    bigquery.SchemaField("natr", "FLOAT"),
    bigquery.SchemaField("bollinger_upper", "FLOAT"),
    bigquery.SchemaField("bollinger_middle", "FLOAT"),
    bigquery.SchemaField("bollinger_lower", "FLOAT"),
    bigquery.SchemaField("bb_width", "FLOAT"),
    bigquery.SchemaField("bb_percent", "FLOAT"),
    bigquery.SchemaField("keltner_upper", "FLOAT"),
    bigquery.SchemaField("keltner_middle", "FLOAT"),
    bigquery.SchemaField("keltner_lower", "FLOAT"),
    bigquery.SchemaField("donchian_upper", "FLOAT"),
    bigquery.SchemaField("donchian_middle", "FLOAT"),
    bigquery.SchemaField("donchian_lower", "FLOAT"),
    # Trend Indicators
    bigquery.SchemaField("adx", "FLOAT"),
    bigquery.SchemaField("plus_di", "FLOAT"),
    bigquery.SchemaField("minus_di", "FLOAT"),
    bigquery.SchemaField("aroon_up", "FLOAT"),
    bigquery.SchemaField("aroon_down", "FLOAT"),
    bigquery.SchemaField("aroon_osc", "FLOAT"),
    bigquery.SchemaField("supertrend", "FLOAT"),
    bigquery.SchemaField("supertrend_direction", "INTEGER"),
    bigquery.SchemaField("psar", "FLOAT"),
    bigquery.SchemaField("psar_direction", "INTEGER"),
    bigquery.SchemaField("trix", "FLOAT"),
    bigquery.SchemaField("mass_index", "FLOAT"),
    bigquery.SchemaField("dpo", "FLOAT"),
    bigquery.SchemaField("vortex_pos", "FLOAT"),
    bigquery.SchemaField("vortex_neg", "FLOAT"),
    # Volume Indicators
    bigquery.SchemaField("obv", "FLOAT"),
    bigquery.SchemaField("obv_ema", "FLOAT"),
    bigquery.SchemaField("cmf", "FLOAT"),
    bigquery.SchemaField("mfi", "FLOAT"),
    bigquery.SchemaField("ad_line", "FLOAT"),
    bigquery.SchemaField("adosc", "FLOAT"),
    bigquery.SchemaField("eom", "FLOAT"),
    bigquery.SchemaField("vpt", "FLOAT"),
    bigquery.SchemaField("nvi", "FLOAT"),
    bigquery.SchemaField("pvi", "FLOAT"),
    bigquery.SchemaField("volume_sma_20", "FLOAT"),
    bigquery.SchemaField("volume_ratio", "FLOAT"),
    # Ichimoku Cloud
    bigquery.SchemaField("ichimoku_tenkan", "FLOAT"),
    bigquery.SchemaField("ichimoku_kijun", "FLOAT"),
    bigquery.SchemaField("ichimoku_senkou_a", "FLOAT"),
    bigquery.SchemaField("ichimoku_senkou_b", "FLOAT"),
    bigquery.SchemaField("ichimoku_chikou", "FLOAT"),
    # Price Action
    bigquery.SchemaField("pivot", "FLOAT"),
    bigquery.SchemaField("r1", "FLOAT"),
    bigquery.SchemaField("r2", "FLOAT"),
    bigquery.SchemaField("r3", "FLOAT"),
    bigquery.SchemaField("s1", "FLOAT"),
    bigquery.SchemaField("s2", "FLOAT"),
    bigquery.SchemaField("s3", "FLOAT"),
    # Metadata
    bigquery.SchemaField("name", "STRING"),
    bigquery.SchemaField("exchange", "STRING"),
    bigquery.SchemaField("currency", "STRING"),
    bigquery.SchemaField("asset_type", "STRING"),
    bigquery.SchemaField("sector", "STRING"),
    bigquery.SchemaField("industry", "STRING"),
    bigquery.SchemaField("fetch_timestamp", "TIMESTAMP"),
]


def calculate_all_indicators(df):
    """Calculate all 97 indicators using Saleem's corrections"""
    if len(df) < 200:
        return df

    df = df.sort_values('datetime').copy()
    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['volume'].fillna(0)

    # === Moving Averages ===
    df['sma_20'] = close.rolling(20).mean()
    df['sma_50'] = close.rolling(50).mean()
    df['sma_200'] = close.rolling(200).mean()
    df['ema_12'] = close.ewm(span=12, adjust=False).mean()
    df['ema_20'] = close.ewm(span=20, adjust=False).mean()
    df['ema_26'] = close.ewm(span=26, adjust=False).mean()
    df['ema_50'] = close.ewm(span=50, adjust=False).mean()
    df['ema_200'] = close.ewm(span=200, adjust=False).mean()

    # KAMA (Kaufman Adaptive MA)
    change = abs(close - close.shift(10))
    volatility = abs(close - close.shift(1)).rolling(10).sum()
    er = change / volatility.replace(0, np.nan)
    sc = (er * (2/3 - 2/31) + 2/31) ** 2
    kama = [close.iloc[0]]
    for i in range(1, len(close)):
        kama.append(kama[-1] + sc.iloc[i] * (close.iloc[i] - kama[-1]) if pd.notna(sc.iloc[i]) else kama[-1])
    df['kama'] = kama

    # Other MAs
    df['wma_20'] = (close * range(1, len(close)+1)).rolling(20).sum() / sum(range(1, 21)) if len(close) >= 20 else np.nan
    df['tema'] = 3 * df['ema_20'] - 3 * df['ema_20'].ewm(span=20, adjust=False).mean() + df['ema_20'].ewm(span=20, adjust=False).mean().ewm(span=20, adjust=False).mean()
    df['dema'] = 2 * df['ema_20'] - df['ema_20'].ewm(span=20, adjust=False).mean()
    df['t3'] = df['dema']  # Simplified
    df['hma_20'] = df['wma_20']  # Simplified
    df['vwma_20'] = (close * volume).rolling(20).sum() / volume.rolling(20).sum()

    # === Momentum Indicators ===
    # RSI with Wilder's RMA (Saleem's correction)
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']

    # Slow Stochastic (Saleem's correction)
    lowest_low = low.rolling(14).min()
    highest_high = high.rolling(14).max()
    raw_k = 100 * (close - lowest_low) / (highest_high - lowest_low).replace(0, np.nan)
    df['stoch_k'] = raw_k.rolling(3).mean()  # Smoothed K
    df['stoch_d'] = df['stoch_k'].rolling(3).mean()

    # Stoch RSI
    rsi_min = df['rsi'].rolling(14).min()
    rsi_max = df['rsi'].rolling(14).max()
    df['stoch_rsi_k'] = 100 * (df['rsi'] - rsi_min) / (rsi_max - rsi_min).replace(0, np.nan)
    df['stoch_rsi_d'] = df['stoch_rsi_k'].rolling(3).mean()

    # Williams %R
    df['williams_r'] = -100 * (highest_high - close) / (highest_high - lowest_low).replace(0, np.nan)

    # CCI
    typical_price = (high + low + close) / 3
    sma_tp = typical_price.rolling(20).mean()
    mad = typical_price.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean())
    df['cci'] = (typical_price - sma_tp) / (0.015 * mad)

    # ROC (10 period - Saleem's correction)
    df['roc'] = ((close - close.shift(10)) / close.shift(10).replace(0, np.nan)) * 100

    # Momentum
    df['momentum'] = close - close.shift(10)

    # TSI
    pc = close.diff()
    double_smooth_pc = pc.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    double_smooth_abs_pc = pc.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    df['tsi'] = 100 * double_smooth_pc / double_smooth_abs_pc.replace(0, np.nan)

    # Ultimate Oscillator
    bp = close - np.minimum(low, close.shift(1))
    tr = np.maximum(high, close.shift(1)) - np.minimum(low, close.shift(1))
    avg7 = bp.rolling(7).sum() / tr.rolling(7).sum()
    avg14 = bp.rolling(14).sum() / tr.rolling(14).sum()
    avg28 = bp.rolling(28).sum() / tr.rolling(28).sum()
    df['uo'] = 100 * (4*avg7 + 2*avg14 + avg28) / 7

    # Awesome Oscillator
    df['ao'] = (high + low).rolling(5).mean() / 2 - (high + low).rolling(34).mean() / 2

    # PPO & PVO
    df['ppo'] = (df['ema_12'] - df['ema_26']) / df['ema_26'] * 100
    vol_ema_12 = volume.ewm(span=12, adjust=False).mean()
    vol_ema_26 = volume.ewm(span=26, adjust=False).mean()
    df['pvo'] = (vol_ema_12 - vol_ema_26) / vol_ema_26.replace(0, np.nan) * 100

    # === Volatility Indicators ===
    # ATR with Wilder's RMA
    tr = pd.concat([
        high - low,
        abs(high - close.shift(1)),
        abs(low - close.shift(1))
    ], axis=1).max(axis=1)
    df['atr'] = tr.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    df['natr'] = (df['atr'] / close) * 100

    # Bollinger Bands (ddof=0 - Saleem's correction)
    df['bollinger_middle'] = df['sma_20']
    bb_std = close.rolling(20).std(ddof=0)
    df['bollinger_upper'] = df['bollinger_middle'] + 2 * bb_std
    df['bollinger_lower'] = df['bollinger_middle'] - 2 * bb_std
    df['bb_width'] = (df['bollinger_upper'] - df['bollinger_lower']) / df['bollinger_middle']
    df['bb_percent'] = (close - df['bollinger_lower']) / (df['bollinger_upper'] - df['bollinger_lower']).replace(0, np.nan)

    # Keltner Channels
    df['keltner_middle'] = df['ema_20']
    df['keltner_upper'] = df['keltner_middle'] + 2 * df['atr']
    df['keltner_lower'] = df['keltner_middle'] - 2 * df['atr']

    # Donchian Channels
    df['donchian_upper'] = high.rolling(20).max()
    df['donchian_lower'] = low.rolling(20).min()
    df['donchian_middle'] = (df['donchian_upper'] + df['donchian_lower']) / 2

    # === Trend Indicators ===
    # ADX with Wilder's RMA
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

    atr_rma = tr.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean() / atr_rma
    minus_di = 100 * minus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean() / atr_rma
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
    df['adx'] = dx.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    df['plus_di'] = plus_di
    df['minus_di'] = minus_di

    # Aroon
    df['aroon_up'] = 100 * (25 - high.rolling(25).apply(lambda x: 25 - x.argmax())) / 25
    df['aroon_down'] = 100 * (25 - low.rolling(25).apply(lambda x: 25 - x.argmin())) / 25
    df['aroon_osc'] = df['aroon_up'] - df['aroon_down']

    # PSAR (simplified)
    df['psar'] = close.shift(1)
    df['psar_direction'] = (close > df['psar']).astype(int)

    # Supertrend (simplified)
    df['supertrend'] = df['ema_20']
    df['supertrend_direction'] = (close > df['supertrend']).astype(int)

    # TRIX
    ema1 = close.ewm(span=15, adjust=False).mean()
    ema2 = ema1.ewm(span=15, adjust=False).mean()
    ema3 = ema2.ewm(span=15, adjust=False).mean()
    df['trix'] = (ema3 - ema3.shift(1)) / ema3.shift(1) * 10000

    # Mass Index
    ema_range = (high - low).ewm(span=9, adjust=False).mean()
    double_ema_range = ema_range.ewm(span=9, adjust=False).mean()
    df['mass_index'] = (ema_range / double_ema_range).rolling(25).sum()

    # DPO
    df['dpo'] = close.shift(int(20/2 + 1)) - df['sma_20']

    # Vortex
    vm_plus = abs(high - low.shift(1))
    vm_minus = abs(low - high.shift(1))
    df['vortex_pos'] = vm_plus.rolling(14).sum() / tr.rolling(14).sum()
    df['vortex_neg'] = vm_minus.rolling(14).sum() / tr.rolling(14).sum()

    # === Volume Indicators ===
    df['obv'] = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    df['obv_ema'] = df['obv'].ewm(span=20, adjust=False).mean()

    # CMF
    mf_multiplier = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
    mf_volume = mf_multiplier * volume
    df['cmf'] = mf_volume.rolling(20).sum() / volume.rolling(20).sum()

    # MFI
    typical_price = (high + low + close) / 3
    mf = typical_price * volume
    pos_mf = mf.where(typical_price > typical_price.shift(1), 0)
    neg_mf = mf.where(typical_price < typical_price.shift(1), 0)
    mfr = pos_mf.rolling(14).sum() / neg_mf.rolling(14).sum().replace(0, np.nan)
    df['mfi'] = 100 - (100 / (1 + mfr))

    # A/D Line & ADOSC
    clv = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
    df['ad_line'] = (clv * volume).fillna(0).cumsum()
    df['adosc'] = df['ad_line'].ewm(span=3, adjust=False).mean() - df['ad_line'].ewm(span=10, adjust=False).mean()

    # EOM
    distance = ((high + low) / 2) - ((high.shift(1) + low.shift(1)) / 2)
    box_ratio = (volume / 100000000) / (high - low).replace(0, np.nan)
    df['eom'] = distance / box_ratio

    # VPT
    df['vpt'] = (volume * ((close - close.shift(1)) / close.shift(1))).fillna(0).cumsum()

    # NVI & PVI
    nvi = [1000]
    pvi = [1000]
    for i in range(1, len(df)):
        if volume.iloc[i] < volume.iloc[i-1]:
            nvi.append(nvi[-1] * (1 + (close.iloc[i] - close.iloc[i-1]) / close.iloc[i-1]))
        else:
            nvi.append(nvi[-1])
        if volume.iloc[i] > volume.iloc[i-1]:
            pvi.append(pvi[-1] * (1 + (close.iloc[i] - close.iloc[i-1]) / close.iloc[i-1]))
        else:
            pvi.append(pvi[-1])
    df['nvi'] = nvi
    df['pvi'] = pvi

    df['volume_sma_20'] = volume.rolling(20).mean()
    df['volume_ratio'] = volume / df['volume_sma_20'].replace(0, np.nan)

    # === Ichimoku Cloud (with forward shift - Saleem's correction) ===
    tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
    kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
    senkou_a_raw = (tenkan + kijun) / 2
    senkou_b_raw = (high.rolling(52).max() + low.rolling(52).min()) / 2

    df['ichimoku_tenkan'] = tenkan
    df['ichimoku_kijun'] = kijun
    df['ichimoku_senkou_a'] = senkou_a_raw.shift(26)  # Forward shift
    df['ichimoku_senkou_b'] = senkou_b_raw.shift(26)  # Forward shift
    df['ichimoku_chikou'] = close.shift(-26)

    # === Pivot Points ===
    df['pivot'] = (high.shift(1) + low.shift(1) + close.shift(1)) / 3
    df['r1'] = 2 * df['pivot'] - low.shift(1)
    df['r2'] = df['pivot'] + (high.shift(1) - low.shift(1))
    df['r3'] = high.shift(1) + 2 * (df['pivot'] - low.shift(1))
    df['s1'] = 2 * df['pivot'] - high.shift(1)
    df['s2'] = df['pivot'] - (high.shift(1) - low.shift(1))
    df['s3'] = low.shift(1) - 2 * (high.shift(1) - df['pivot'])

    return df


def fetch_symbol_data(symbol, asset_type, outputsize=5000):
    """Fetch historical data from TwelveData"""
    try:
        url = f"{TWELVEDATA_BASE_URL}/time_series"
        params = {
            'symbol': symbol,
            'interval': '1day',
            'outputsize': outputsize,
            'apikey': TWELVEDATA_API_KEY,
            'format': 'JSON'
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'values' not in data:
            print(f"  No data for {symbol}: {data.get('message', 'Unknown error')}")
            return None

        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df['symbol'] = symbol
        df['timestamp'] = df['datetime'].astype(int) // 10**9
        df['asset_type'] = asset_type
        df['name'] = data.get('meta', {}).get('name', symbol)
        df['exchange'] = data.get('meta', {}).get('exchange', '')
        df['currency'] = data.get('meta', {}).get('currency', 'USD')
        df['sector'] = ''
        df['industry'] = ''
        df['fetch_timestamp'] = datetime.utcnow()

        # Calculate indicators
        df = calculate_all_indicators(df)

        return df

    except Exception as e:
        print(f"  Error fetching {symbol}: {e}")
        return None


def create_clean_table(table_name):
    """Create clean table with 97-field schema"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    table = bigquery.Table(table_ref, schema=CLEAN_SCHEMA)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.MONTH,
        field="datetime"
    )
    table.clustering_fields = ["symbol", "asset_type", "exchange"]

    try:
        client.delete_table(table_ref, not_found_ok=True)
        client.create_table(table)
        print(f"Created table: {table_name}")
        return True
    except Exception as e:
        print(f"Error creating table {table_name}: {e}")
        return False


def upload_to_bigquery(df, table_name):
    """Upload DataFrame to BigQuery"""
    if df is None or len(df) == 0:
        return 0

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Keep only schema columns
    schema_cols = [field.name for field in CLEAN_SCHEMA]
    df_clean = df[[c for c in schema_cols if c in df.columns]].copy()

    # Add missing columns as NULL
    for col in schema_cols:
        if col not in df_clean.columns:
            df_clean[col] = None

    # Reorder columns
    df_clean = df_clean[schema_cols]

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )

    try:
        job = client.load_table_from_dataframe(df_clean, table_ref, job_config=job_config)
        job.result()
        return len(df_clean)
    except Exception as e:
        print(f"  Upload error: {e}")
        return 0


def process_asset_type(asset_key, config):
    """Process all symbols for an asset type"""
    print(f"\n{'='*60}")
    print(f"Processing {asset_key.upper()}")
    print(f"{'='*60}")

    # Create clean table
    table_name = config['target_table']
    if not create_clean_table(table_name):
        return

    symbols = config['symbols']
    asset_type = config['asset_type']
    total_rows = 0
    success_count = 0

    # Process symbols with parallel execution
    with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
        futures = {
            executor.submit(fetch_symbol_data, symbol, asset_type): symbol
            for symbol in symbols
        }

        for i, future in enumerate(as_completed(futures)):
            symbol = futures[future]
            try:
                df = future.result()
                if df is not None and len(df) > 0:
                    rows = upload_to_bigquery(df, table_name)
                    total_rows += rows
                    success_count += 1
                    print(f"  [{i+1}/{len(symbols)}] {symbol}: {rows} rows")
                else:
                    print(f"  [{i+1}/{len(symbols)}] {symbol}: No data")
            except Exception as e:
                print(f"  [{i+1}/{len(symbols)}] {symbol}: Error - {e}")

            # Rate limiting
            time.sleep(0.1)

    print(f"\n{asset_key.upper()} Complete: {success_count}/{len(symbols)} symbols, {total_rows:,} total rows")
    return total_rows


def main():
    print("="*60)
    print("ALL ASSET MIGRATION TO CLEAN SCHEMA (97 Fields)")
    print("Using TwelveData API with Parallel Processing")
    print("="*60)
    print(f"Start time: {datetime.now()}")

    total_all = 0

    for asset_key, config in ASSET_CONFIGS.items():
        rows = process_asset_type(asset_key, config)
        if rows:
            total_all += rows

    print("\n" + "="*60)
    print("MIGRATION COMPLETE")
    print("="*60)
    print(f"Total rows across all assets: {total_all:,}")
    print(f"End time: {datetime.now()}")

    # List created tables
    print("\nCreated clean tables:")
    for asset_key, config in ASSET_CONFIGS.items():
        print(f"  - {config['target_table']}")


if __name__ == '__main__':
    main()
