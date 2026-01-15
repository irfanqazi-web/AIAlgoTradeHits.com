"""
Extended Historical Daily Data Fetcher - Phase 2
Adds more symbols to maximize daily API quota (800 calls)
Includes ALL Priority 1 & Priority 2 missing fields from Phase 1 Methodology

This extends the original fetch_historical_enhanced.py with additional symbols:
- 100 more US stocks (total 150)
- 30 more cryptocurrencies (total 52)
- 20 more ETFs (total 50)
- 10 more forex pairs (total 30)
- More indices and commodities
"""
import requests
import time
import sys
import io
import warnings
import json
import os
from datetime import datetime, timezone
from google.cloud import bigquery
import pandas as pd
import numpy as np

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

warnings.filterwarnings('ignore')

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TWELVE_DATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'

# Rate limiting: 8 calls/minute = 7.5 seconds between calls
RATE_LIMIT_SECONDS = 8

# Progress file to track completed symbols
PROGRESS_FILE = 'historical_fetch_progress_v2.json'

# EXTENDED symbols list - adding more to use full quota
SYMBOLS = {
    'stocks': {
        'table': 'stocks_historical_daily_v2',
        'symbols': [
            # Original 50
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'JNJ',
            'V', 'JPM', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV', 'PFE', 'KO',
            'PEP', 'COST', 'AVGO', 'TMO', 'MCD', 'WMT', 'CSCO', 'ABT', 'ACN', 'DHR',
            'NKE', 'DIS', 'VZ', 'ADBE', 'CRM', 'TXN', 'NEE', 'PM', 'UNP', 'RTX',
            'INTC', 'AMD', 'IBM', 'QCOM', 'ORCL', 'LOW', 'CAT', 'BA', 'GE', 'SPGI',
            # Additional 100 stocks - S&P 500 components
            'LMT', 'BLK', 'MDLZ', 'ISRG', 'ADP', 'GILD', 'BKNG', 'ADI', 'VRTX', 'REGN',
            'SBUX', 'LRCX', 'PANW', 'KLAC', 'SNPS', 'CME', 'CDNS', 'MELI', 'SYK', 'AZN',
            'EQIX', 'PYPL', 'MU', 'NOW', 'ORLY', 'CSX', 'MRVL', 'NXPI', 'FTNT', 'MAR',
            'AXP', 'FDX', 'ADM', 'CMG', 'MMC', 'ICE', 'COP', 'EMR', 'WM', 'NSC',
            'SHW', 'TGT', 'PLD', 'PSA', 'CCI', 'WELL', 'DLR', 'AMT', 'O', 'SPG',
            'EOG', 'SLB', 'PSX', 'VLO', 'OXY', 'HAL', 'DVN', 'MPC', 'HES', 'FANG',
            'GM', 'F', 'TM', 'HMC', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'FSR',
            'COIN', 'MSTR', 'SQ', 'PYPL', 'SHOP', 'SE', 'MELI', 'GRAB', 'NU', 'SOFI',
            'PLTR', 'SNOW', 'DDOG', 'ZS', 'CRWD', 'NET', 'MDB', 'OKTA', 'SPLK', 'ESTC',
            'ARM', 'SMCI', 'DELL', 'HPE', 'HPQ', 'ANET', 'KEYS', 'JNPR', 'NTAP', 'WDC'
        ]
    },
    'cryptos': {
        'table': 'cryptos_historical_daily_v2',
        'symbols': [
            # Original 22 (minus invalid ones)
            'BTC/USD', 'ETH/USD', 'XRP/USD', 'SOL/USD', 'ADA/USD', 'DOGE/USD', 'DOT/USD',
            'AVAX/USD', 'LINK/USD', 'LTC/USD', 'UNI/USD', 'ATOM/USD', 'XLM/USD',
            'ALGO/USD', 'VET/USD', 'FIL/USD', 'AAVE/USD', 'XTZ/USD', 'SHIB/USD',
            'NEAR/USD', 'APT/USD',
            # Additional 30 cryptos
            'TRX/USD', 'ETC/USD', 'BCH/USD', 'XMR/USD', 'MKR/USD', 'COMP/USD',
            'SNX/USD', 'YFI/USD', 'SUSHI/USD', 'CRV/USD', 'BAL/USD', 'LDO/USD',
            'OP/USD', 'ARB/USD', 'IMX/USD', 'SAND/USD', 'MANA/USD', 'AXS/USD',
            'ENJ/USD', 'GALA/USD', 'ICP/USD', 'FTM/USD', 'RUNE/USD', 'KAVA/USD',
            'CELO/USD', 'FLOW/USD', 'HBAR/USD', 'EGLD/USD', 'ZEC/USD', 'DASH/USD'
        ]
    },
    'etfs': {
        'table': 'etfs_historical_daily_v2',
        'symbols': [
            # Original 30
            'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO', 'EFA', 'EEM',
            'AGG', 'BND', 'LQD', 'TLT', 'GLD', 'SLV', 'USO', 'XLF', 'XLK', 'XLE',
            'XLV', 'XLI', 'XLY', 'XLP', 'XLU', 'ARKK', 'ARKG', 'ARKF', 'VNQ', 'SCHD',
            # Additional 20 ETFs
            'XLB', 'XLC', 'XLRE', 'SMH', 'SOXX', 'IBB', 'XBI', 'XRT', 'XHB', 'KRE',
            'FXI', 'KWEB', 'MCHI', 'VGK', 'EWJ', 'EWZ', 'EWY', 'EWW', 'EWC', 'EWA'
        ]
    },
    'forex': {
        'table': 'forex_historical_daily_v2',
        'symbols': [
            # Original 20
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',
            'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY', 'EUR/CHF', 'EUR/AUD', 'GBP/AUD',
            'USD/SGD', 'USD/HKD', 'USD/MXN', 'USD/ZAR', 'USD/INR', 'EUR/CAD',
            # Additional 10 pairs
            'GBP/CHF', 'EUR/NZD', 'GBP/NZD', 'AUD/NZD', 'CAD/JPY', 'CHF/JPY',
            'NZD/JPY', 'GBP/CAD', 'EUR/SGD', 'AUD/CAD'
        ]
    },
    'indices': {
        'table': 'indices_historical_daily_v2',
        'symbols': [
            # Original (with valid symbols only)
            'SPX', 'NDX', 'FTSE', 'DAX', 'CAC', 'HSI', 'IBEX', 'AEX', 'SMI',
            # Additional indices
            'NIFTY', 'SENSEX', 'ASX', 'NKY', 'KOSPI', 'TWSE', 'SET', 'STI'
        ]
    },
    'commodities': {
        'table': 'commodities_historical_daily_v2',
        'symbols': [
            # Original (with valid symbols)
            'XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD', 'CL', 'BZ', 'NG', 'HO',
            'ZC', 'ZS', 'KC', 'CC', 'SB', 'LC',
            # Additional commodities
            'XCU/USD', 'LH', 'OJ', 'RB'
        ]
    }
}


def load_progress():
    """Load progress from file"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'completed': [], 'api_calls': 0, 'last_run': None}


def save_progress(progress):
    """Save progress to file"""
    progress['last_run'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def calculate_enhanced_indicators(df):
    """
    Calculate 80+ technical indicators including ALL Phase 1 Priority 1 & 2 fields
    """
    if len(df) < 5:
        return df

    # Convert to float
    df['open'] = pd.to_numeric(df['open'], errors='coerce')
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')

    close = df['close']
    high = df['high']
    low = df['low']
    open_price = df['open']

    # Handle volume
    if 'volume' in df.columns:
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0)
        volume = df['volume']
    else:
        df['volume'] = 0
        volume = pd.Series([0] * len(df), index=df.index)

    # =========================================================================
    # PRIORITY 1: CRITICAL ML FEATURES
    # =========================================================================

    # --- Returns & Log Returns ---
    df['daily_return_pct'] = close.pct_change() * 100
    df['weekly_log_return'] = np.log(close / close.shift(1))

    # Multi-lag returns
    if len(df) >= 2:
        df['return_2w'] = (close / close.shift(2) - 1) * 100
    if len(df) >= 4:
        df['return_4w'] = (close / close.shift(4) - 1) * 100
    if len(df) >= 8:
        df['return_8w'] = (close / close.shift(8) - 1) * 100

    # --- Candle Geometry ---
    df['candle_body_pct'] = ((close - open_price) / open_price) * 100
    df['candle_range_pct'] = ((high - low) / open_price) * 100
    df['high_low_pct'] = ((high - low) / close) * 100

    body_high = df[['open', 'close']].max(axis=1)
    body_low = df[['open', 'close']].min(axis=1)
    df['upper_shadow_pct'] = ((high - body_high) / (high - low + 0.0001)) * 100
    df['lower_shadow_pct'] = ((body_low - low) / (high - low + 0.0001)) * 100

    # --- Moving Averages: SMA ---
    for period in [5, 10, 20, 50, 100, 200]:
        if len(df) >= period:
            df[f'sma_{period}'] = close.rolling(window=period).mean()

    # --- Moving Averages: EMA ---
    for period in [5, 10, 12, 20, 26, 50, 100, 200]:
        if len(df) >= period:
            df[f'ema_{period}'] = close.ewm(span=period, adjust=False).mean()

    # --- MA Distance Features ---
    if 'sma_20' in df.columns:
        df['close_vs_sma20_pct'] = ((close / df['sma_20']) - 1) * 100
    if 'sma_50' in df.columns:
        df['close_vs_sma50_pct'] = ((close / df['sma_50']) - 1) * 100
    if 'sma_200' in df.columns:
        df['close_vs_sma200_pct'] = ((close / df['sma_200']) - 1) * 100
    if 'ema_20' in df.columns:
        df['close_vs_ema20_pct'] = ((close / df['ema_20']) - 1) * 100
    if 'ema_50' in df.columns:
        df['close_vs_ema50_pct'] = ((close / df['ema_50']) - 1) * 100

    # --- EMA Slopes ---
    if 'ema_20' in df.columns:
        df['ema_slope_20'] = df['ema_20'].diff()
    if 'ema_50' in df.columns:
        df['ema_slope_50'] = df['ema_50'].diff()

    # --- MACD with Histogram & Cross Flag ---
    if len(df) >= 26:
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']

        macd_above = df['macd'] > df['macd_signal']
        df['macd_cross_flag'] = 0
        df.loc[macd_above & ~macd_above.shift(1).fillna(False), 'macd_cross_flag'] = 1
        df.loc[~macd_above & macd_above.shift(1).fillna(True), 'macd_cross_flag'] = -1

    # --- RSI with Enhancements ---
    for period in [7, 14, 21]:
        if len(df) >= period:
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss.replace(0, 0.0001)
            df[f'rsi_{period}'] = 100 - (100 / (1 + rs))

    if 'rsi_14' in df.columns:
        df['rsi_slope'] = df['rsi_14'].diff()
        lookback = min(100, len(df) - 1)
        if lookback >= 20:
            rsi_mean = df['rsi_14'].rolling(window=lookback).mean()
            rsi_std = df['rsi_14'].rolling(window=lookback).std()
            df['rsi_zscore'] = (df['rsi_14'] - rsi_mean) / rsi_std.replace(0, 0.0001)
        df['rsi_overbought_flag'] = (df['rsi_14'] > 70).astype(int)
        df['rsi_oversold_flag'] = (df['rsi_14'] < 30).astype(int)

    # =========================================================================
    # PRIORITY 2: ENHANCED FEATURES
    # =========================================================================

    # --- Bollinger Bands ---
    if len(df) >= 20:
        sma20 = close.rolling(window=20).mean()
        std20 = close.rolling(window=20).std()
        df['bb_upper'] = sma20 + (std20 * 2)
        df['bb_middle'] = sma20
        df['bb_lower'] = sma20 - (std20 * 2)
        df['bb_width'] = ((df['bb_upper'] - df['bb_lower']) / df['bb_middle']) * 100
        df['bb_percent'] = ((close - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])) * 100

    # --- ATR with Enhancements ---
    for period in [7, 14]:
        if len(df) >= period:
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            df[f'atr_{period}'] = tr.rolling(window=period).mean()

    if 'atr_14' in df.columns:
        df['atr_pct'] = (df['atr_14'] / close) * 100
        df['atr_slope'] = df['atr_14'].diff()
        lookback = min(100, len(df) - 1)
        if lookback >= 20:
            atr_mean = df['atr_14'].rolling(window=lookback).mean()
            atr_std = df['atr_14'].rolling(window=lookback).std()
            df['atr_zscore'] = (df['atr_14'] - atr_mean) / atr_std.replace(0, 0.0001)

    # --- Volume Features ---
    if volume.sum() > 0:
        vol_mean = volume.rolling(window=20).mean()
        vol_std = volume.rolling(window=20).std()
        df['volume_zscore'] = (volume - vol_mean) / vol_std.replace(0, 0.0001)
        df['volume_ratio'] = volume / vol_mean.replace(0, 0.0001)
        obv = [0]
        for i in range(1, len(df)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.append(obv[-1] + volume.iloc[i])
            elif close.iloc[i] < close.iloc[i-1]:
                obv.append(obv[-1] - volume.iloc[i])
            else:
                obv.append(obv[-1])
        df['obv'] = obv

    # --- ADX and Directional Indicators ---
    if len(df) >= 14:
        high_diff = high.diff()
        low_diff = -low.diff()
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr14 = tr.rolling(window=14).mean()
        plus_dm14 = plus_dm.rolling(window=14).mean()
        minus_dm14 = minus_dm.rolling(window=14).mean()
        df['plus_di'] = (plus_dm14 / atr14) * 100
        df['minus_di'] = (minus_dm14 / atr14) * 100
        di_diff = abs(df['plus_di'] - df['minus_di'])
        di_sum = df['plus_di'] + df['minus_di']
        df['dx'] = (di_diff / di_sum.replace(0, 0.0001)) * 100
        df['adx'] = df['dx'].rolling(window=14).mean()

    # --- Stochastic ---
    if len(df) >= 14:
        lowest_low = low.rolling(window=14).min()
        highest_high = high.rolling(window=14).max()
        df['stoch_k'] = ((close - lowest_low) / (highest_high - lowest_low)) * 100
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
        df['williams_r'] = ((highest_high - close) / (highest_high - lowest_low)) * -100

    # --- CCI ---
    if len(df) >= 20:
        tp = (high + low + close) / 3
        df['cci'] = (tp - tp.rolling(window=20).mean()) / (0.015 * tp.rolling(window=20).std())

    # --- ROC ---
    for period in [5, 10, 20]:
        if len(df) >= period:
            df[f'roc_{period}'] = ((close - close.shift(period)) / close.shift(period)) * 100

    # --- Volatility ---
    if len(df) >= 20:
        returns = close.pct_change()
        df['volatility_10'] = returns.rolling(window=10).std() * np.sqrt(252) * 100
        df['volatility_20'] = returns.rolling(window=20).std() * np.sqrt(252) * 100

    # --- Lagged Features ---
    for lag in [1, 2, 3, 5, 10]:
        if len(df) >= lag:
            df[f'close_lag_{lag}'] = close.shift(lag)
            df[f'return_lag_{lag}'] = df['daily_return_pct'].shift(lag)

    # --- Target Variables ---
    df['target_return_1d'] = close.shift(-1).pct_change() * 100
    df['target_return_5d'] = ((close.shift(-5) - close) / close) * 100
    df['target_direction_1d'] = (close.shift(-1) > close).astype(int)

    # --- Signal Categories ---
    if 'rsi_14' in df.columns:
        def momentum_signal(x):
            if pd.isna(x):
                return 'neutral'
            if x > 70:
                return 'overbought'
            elif x < 30:
                return 'oversold'
            elif x > 50:
                return 'bullish'
            else:
                return 'bearish'
        df['momentum_signal'] = df['rsi_14'].apply(momentum_signal)

    if 'sma_50' in df.columns and 'sma_200' in df.columns:
        def trend_signal(row):
            if pd.isna(row['sma_50']) or pd.isna(row['sma_200']):
                return 'neutral'
            if row['close'] > row['sma_50'] > row['sma_200']:
                return 'strong_bullish'
            elif row['close'] > row['sma_50']:
                return 'bullish'
            elif row['close'] < row['sma_50'] < row['sma_200']:
                return 'strong_bearish'
            else:
                return 'bearish'
        df['trend_signal'] = df.apply(trend_signal, axis=1)

    return df


def fetch_historical_data(symbol, outputsize=5000):
    """Fetch historical daily data from Twelve Data API"""
    try:
        url = "https://api.twelvedata.com/time_series"
        params = {
            'symbol': symbol,
            'interval': '1day',
            'outputsize': outputsize,
            'apikey': TWELVE_DATA_API_KEY
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'code' in data:
            if data['code'] == 429:
                print(f"  Rate limit hit! Waiting 60 seconds...")
                time.sleep(60)
                return None
            elif data['code'] == 401 or 'quota' in data.get('message', '').lower():
                print(f"  API quota exceeded!")
                return 'QUOTA_EXCEEDED'
            else:
                print(f"  API Error: {data.get('message', 'Unknown')[:50]}")
                return None

        if 'values' not in data:
            print(f"  No data returned")
            return None

        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime').reset_index(drop=True)

        return df

    except Exception as e:
        print(f"  Exception: {str(e)[:50]}")
        return None


def create_enhanced_table(client, table_id):
    """Create BigQuery table with enhanced schema"""
    schema = [
        bigquery.SchemaField("symbol", "STRING"),
        bigquery.SchemaField("datetime", "TIMESTAMP"),
        bigquery.SchemaField("open", "FLOAT64"),
        bigquery.SchemaField("high", "FLOAT64"),
        bigquery.SchemaField("low", "FLOAT64"),
        bigquery.SchemaField("close", "FLOAT64"),
        bigquery.SchemaField("volume", "FLOAT64"),
        bigquery.SchemaField("candle_body_pct", "FLOAT64"),
        bigquery.SchemaField("candle_range_pct", "FLOAT64"),
        bigquery.SchemaField("high_low_pct", "FLOAT64"),
        bigquery.SchemaField("upper_shadow_pct", "FLOAT64"),
        bigquery.SchemaField("lower_shadow_pct", "FLOAT64"),
        bigquery.SchemaField("daily_return_pct", "FLOAT64"),
        bigquery.SchemaField("weekly_log_return", "FLOAT64"),
        bigquery.SchemaField("return_2w", "FLOAT64"),
        bigquery.SchemaField("return_4w", "FLOAT64"),
        bigquery.SchemaField("return_8w", "FLOAT64"),
        bigquery.SchemaField("sma_5", "FLOAT64"),
        bigquery.SchemaField("sma_10", "FLOAT64"),
        bigquery.SchemaField("sma_20", "FLOAT64"),
        bigquery.SchemaField("sma_50", "FLOAT64"),
        bigquery.SchemaField("sma_100", "FLOAT64"),
        bigquery.SchemaField("sma_200", "FLOAT64"),
        bigquery.SchemaField("ema_5", "FLOAT64"),
        bigquery.SchemaField("ema_10", "FLOAT64"),
        bigquery.SchemaField("ema_12", "FLOAT64"),
        bigquery.SchemaField("ema_20", "FLOAT64"),
        bigquery.SchemaField("ema_26", "FLOAT64"),
        bigquery.SchemaField("ema_50", "FLOAT64"),
        bigquery.SchemaField("ema_100", "FLOAT64"),
        bigquery.SchemaField("ema_200", "FLOAT64"),
        bigquery.SchemaField("close_vs_sma20_pct", "FLOAT64"),
        bigquery.SchemaField("close_vs_sma50_pct", "FLOAT64"),
        bigquery.SchemaField("close_vs_sma200_pct", "FLOAT64"),
        bigquery.SchemaField("close_vs_ema20_pct", "FLOAT64"),
        bigquery.SchemaField("close_vs_ema50_pct", "FLOAT64"),
        bigquery.SchemaField("ema_slope_20", "FLOAT64"),
        bigquery.SchemaField("ema_slope_50", "FLOAT64"),
        bigquery.SchemaField("macd", "FLOAT64"),
        bigquery.SchemaField("macd_signal", "FLOAT64"),
        bigquery.SchemaField("macd_hist", "FLOAT64"),
        bigquery.SchemaField("macd_cross_flag", "INT64"),
        bigquery.SchemaField("rsi_7", "FLOAT64"),
        bigquery.SchemaField("rsi_14", "FLOAT64"),
        bigquery.SchemaField("rsi_21", "FLOAT64"),
        bigquery.SchemaField("rsi_slope", "FLOAT64"),
        bigquery.SchemaField("rsi_zscore", "FLOAT64"),
        bigquery.SchemaField("rsi_overbought_flag", "INT64"),
        bigquery.SchemaField("rsi_oversold_flag", "INT64"),
        bigquery.SchemaField("bb_upper", "FLOAT64"),
        bigquery.SchemaField("bb_middle", "FLOAT64"),
        bigquery.SchemaField("bb_lower", "FLOAT64"),
        bigquery.SchemaField("bb_width", "FLOAT64"),
        bigquery.SchemaField("bb_percent", "FLOAT64"),
        bigquery.SchemaField("atr_7", "FLOAT64"),
        bigquery.SchemaField("atr_14", "FLOAT64"),
        bigquery.SchemaField("atr_pct", "FLOAT64"),
        bigquery.SchemaField("atr_slope", "FLOAT64"),
        bigquery.SchemaField("atr_zscore", "FLOAT64"),
        bigquery.SchemaField("volume_zscore", "FLOAT64"),
        bigquery.SchemaField("volume_ratio", "FLOAT64"),
        bigquery.SchemaField("obv", "FLOAT64"),
        bigquery.SchemaField("adx", "FLOAT64"),
        bigquery.SchemaField("plus_di", "FLOAT64"),
        bigquery.SchemaField("minus_di", "FLOAT64"),
        bigquery.SchemaField("dx", "FLOAT64"),
        bigquery.SchemaField("stoch_k", "FLOAT64"),
        bigquery.SchemaField("stoch_d", "FLOAT64"),
        bigquery.SchemaField("williams_r", "FLOAT64"),
        bigquery.SchemaField("cci", "FLOAT64"),
        bigquery.SchemaField("roc_5", "FLOAT64"),
        bigquery.SchemaField("roc_10", "FLOAT64"),
        bigquery.SchemaField("roc_20", "FLOAT64"),
        bigquery.SchemaField("volatility_10", "FLOAT64"),
        bigquery.SchemaField("volatility_20", "FLOAT64"),
        bigquery.SchemaField("close_lag_1", "FLOAT64"),
        bigquery.SchemaField("close_lag_2", "FLOAT64"),
        bigquery.SchemaField("close_lag_3", "FLOAT64"),
        bigquery.SchemaField("close_lag_5", "FLOAT64"),
        bigquery.SchemaField("close_lag_10", "FLOAT64"),
        bigquery.SchemaField("return_lag_1", "FLOAT64"),
        bigquery.SchemaField("return_lag_2", "FLOAT64"),
        bigquery.SchemaField("return_lag_3", "FLOAT64"),
        bigquery.SchemaField("target_return_1d", "FLOAT64"),
        bigquery.SchemaField("target_return_5d", "FLOAT64"),
        bigquery.SchemaField("target_direction_1d", "INT64"),
        bigquery.SchemaField("momentum_signal", "STRING"),
        bigquery.SchemaField("trend_signal", "STRING"),
        bigquery.SchemaField("asset_type", "STRING"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    try:
        client.create_table(table)
        print(f"  Created table {table_id}")
    except Exception as e:
        if "Already Exists" in str(e):
            pass
        else:
            print(f"  Table note: {str(e)[:50]}")


def upload_to_bigquery(client, df, table_id, symbol, asset_type):
    """Upload DataFrame to BigQuery"""
    if df is None or len(df) == 0:
        return 0

    df['symbol'] = symbol
    df['asset_type'] = asset_type
    df['fetch_timestamp'] = datetime.now(timezone.utc).isoformat()
    df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

    valid_columns = [
        'symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume',
        'candle_body_pct', 'candle_range_pct', 'high_low_pct', 'upper_shadow_pct', 'lower_shadow_pct',
        'daily_return_pct', 'weekly_log_return', 'return_2w', 'return_4w', 'return_8w',
        'sma_5', 'sma_10', 'sma_20', 'sma_50', 'sma_100', 'sma_200',
        'ema_5', 'ema_10', 'ema_12', 'ema_20', 'ema_26', 'ema_50', 'ema_100', 'ema_200',
        'close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct',
        'close_vs_ema20_pct', 'close_vs_ema50_pct',
        'ema_slope_20', 'ema_slope_50',
        'macd', 'macd_signal', 'macd_hist', 'macd_cross_flag',
        'rsi_7', 'rsi_14', 'rsi_21', 'rsi_slope', 'rsi_zscore',
        'rsi_overbought_flag', 'rsi_oversold_flag',
        'bb_upper', 'bb_middle', 'bb_lower', 'bb_width', 'bb_percent',
        'atr_7', 'atr_14', 'atr_pct', 'atr_slope', 'atr_zscore',
        'volume_zscore', 'volume_ratio', 'obv',
        'adx', 'plus_di', 'minus_di', 'dx',
        'stoch_k', 'stoch_d', 'williams_r', 'cci',
        'roc_5', 'roc_10', 'roc_20',
        'volatility_10', 'volatility_20',
        'close_lag_1', 'close_lag_2', 'close_lag_3', 'close_lag_5', 'close_lag_10',
        'return_lag_1', 'return_lag_2', 'return_lag_3',
        'target_return_1d', 'target_return_5d', 'target_direction_1d',
        'momentum_signal', 'trend_signal',
        'asset_type', 'fetch_timestamp'
    ]

    available_columns = [c for c in valid_columns if c in df.columns]
    df_upload = df[available_columns].copy()
    df_upload = df_upload.replace({np.nan: None, np.inf: None, -np.inf: None})
    records = df_upload.to_dict('records')

    batch_size = 500
    total_uploaded = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        try:
            errors = client.insert_rows_json(table_id, batch)
            if errors:
                print(f"    Batch {i//batch_size + 1} errors: {len(errors)}")
            else:
                total_uploaded += len(batch)
        except Exception as e:
            print(f"    Upload error: {str(e)[:50]}")

    return total_uploaded


def main():
    print("=" * 70)
    print("EXTENDED HISTORICAL DATA FETCHER v2.0")
    print("Adding 200+ more symbols to maximize daily quota")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Load progress
    progress = load_progress()
    completed = set(progress.get('completed', []))
    api_calls = progress.get('api_calls', 0)

    # Count total and remaining
    total_symbols = sum(len(config['symbols']) for config in SYMBOLS.values())
    remaining = total_symbols - len(completed)

    print(f"\nProgress: {len(completed)} symbols completed, {api_calls} API calls used today")
    print(f"Total symbols in extended list: {total_symbols}")
    print(f"Remaining to fetch: {remaining}")
    print(f"Remaining daily quota: ~{800 - api_calls} calls\n")

    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    total_records = 0
    quota_exceeded = False

    for asset_type, config in SYMBOLS.items():
        if quota_exceeded:
            break

        table_name = config['table']
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        symbols = config['symbols']

        print(f"\n{'='*60}")
        print(f"PROCESSING {asset_type.upper()}")
        print(f"Table: {table_name}")
        print(f"Symbols: {len(symbols)}")
        print(f"{'='*60}")

        create_enhanced_table(client, table_id)

        for i, symbol in enumerate(symbols):
            symbol_key = f"{asset_type}:{symbol}"

            if symbol_key in completed:
                continue  # Skip silently for cleaner output

            print(f"[{i+1}/{len(symbols)}] Fetching {symbol}...", end=" ")
            sys.stdout.flush()

            df = fetch_historical_data(symbol)
            api_calls += 1

            if isinstance(df, str) and df == 'QUOTA_EXCEEDED':
                print("\n\n*** API QUOTA EXCEEDED ***")
                print("Run this script again tomorrow to continue.")
                quota_exceeded = True
                break

            if df is None or (hasattr(df, '__len__') and len(df) == 0):
                print("No data")
                time.sleep(RATE_LIMIT_SECONDS)
                continue

            print(f"Got {len(df)} days", end=" ")

            df = calculate_enhanced_indicators(df)
            uploaded = upload_to_bigquery(client, df, table_id, symbol, asset_type)

            if uploaded > 0:
                print(f"- Uploaded {uploaded} records")
                completed.add(symbol_key)
                total_records += uploaded
            else:
                print("- Upload failed")

            progress['completed'] = list(completed)
            progress['api_calls'] = api_calls
            save_progress(progress)

            time.sleep(RATE_LIMIT_SECONDS)

    print("\n" + "=" * 70)
    print("FETCH SESSION COMPLETE")
    print("=" * 70)
    print(f"Total symbols completed: {len(completed)}")
    print(f"Total API calls used: {api_calls}")
    print(f"Total records uploaded: {total_records}")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if quota_exceeded:
        print("\n*** Run this script again tomorrow to continue ***")
    else:
        remaining_symbols = sum(len(c['symbols']) for c in SYMBOLS.values()) - len(completed)
        if remaining_symbols > 0:
            print(f"\n{remaining_symbols} symbols remaining. Run again to continue.")
        else:
            print("\n*** All historical data has been fetched! ***")


if __name__ == '__main__':
    main()
