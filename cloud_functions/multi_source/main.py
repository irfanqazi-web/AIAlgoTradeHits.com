"""
Multi-Source Data Fetcher - Cloud Function
Runs daily at 1 AM to fetch data from all configured sources
Target: 2M+ records per day

Sources:
1. TwelveData ($229 plan) - 800 calls/min - Stocks, Crypto, ETFs, Forex, Indices
2. Kraken Pro API - Free - Crypto OHLCV with Volume (for MFI calculation)
3. FRED API - Free - Economic indicators
4. Finnhub API - Free - Fundamentals, earnings, analyst ratings
5. CoinMarketCap API - Free tier - Crypto rankings, market cap
"""

import functions_framework
from google.cloud import bigquery
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import time
import concurrent.futures
import json
import traceback

# =====================
# API CONFIGURATION
# =====================

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

# API Keys
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'  # $229/month - 800 calls/min
FRED_API_KEY = '608f96800c8a5d9bdb8d53ad059f06c1'  # Free - 120 req/min
FINNHUB_API_KEY = 'd4dg7t9r01qovljpm3g0d4dg7t9r01qovljpm3gg'  # Free - 60 calls/min
COINMARKETCAP_API_KEY = '059474ae48b84628be6f4a94f9840c30'  # Free - 333 calls/day

# API Base URLs
TWELVEDATA_URL = 'https://api.twelvedata.com'
FRED_URL = 'https://api.stlouisfed.org/fred'
FINNHUB_URL = 'https://finnhub.io/api/v1'
KRAKEN_URL = 'https://api.kraken.com/0/public'
CMC_URL = 'https://pro-api.coinmarketcap.com/v1'

# Rate limiting (per minute)
# TwelveData $229 plan = 800 calls/min capacity
# Using 120/min (0.5s delay) for faster fetching while staying well under limit
TWELVEDATA_RATE = 120  # Optimized for 800/min capacity
FRED_RATE = 100
FINNHUB_RATE = 50
KRAKEN_RATE = 40  # 1 call per 1.5 seconds

# =====================
# SYMBOL CONFIGURATIONS
# =====================

# Top 300 Stocks for daily data (Maximizing $229/month quota)
TOP_STOCKS = [
    # S&P 500 Top 100
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH',
    'LLY', 'JPM', 'XOM', 'V', 'JNJ', 'AVGO', 'PG', 'MA', 'HD', 'COST',
    'MRK', 'ABBV', 'CVX', 'CRM', 'KO', 'PEP', 'AMD', 'ADBE', 'WMT', 'MCD',
    'CSCO', 'BAC', 'ACN', 'NFLX', 'TMO', 'LIN', 'ORCL', 'ABT', 'DHR', 'INTC',
    'DIS', 'PM', 'CMCSA', 'VZ', 'WFC', 'TXN', 'NKE', 'COP', 'INTU', 'RTX',
    'NEE', 'QCOM', 'HON', 'IBM', 'AMGN', 'UNP', 'LOW', 'SPGI', 'CAT', 'GE',
    'BA', 'PLD', 'SBUX', 'DE', 'ELV', 'AMAT', 'BMY', 'GS', 'BLK', 'MDLZ',
    'ADI', 'ISRG', 'GILD', 'MMC', 'ADP', 'TJX', 'VRTX', 'AMT', 'SYK', 'REGN',
    'LMT', 'BKNG', 'MO', 'ETN', 'LRCX', 'CB', 'CI', 'PGR', 'C', 'ZTS',
    'PANW', 'BDX', 'SCHW', 'EOG', 'SO', 'MU', 'CME', 'NOC', 'DUK', 'SLB',
    # S&P 500 Next 100
    'PNC', 'ICE', 'MCK', 'CL', 'SNPS', 'BSX', 'CDNS', 'AON', 'ITW', 'USB',
    'CMG', 'WM', 'EQIX', 'SHW', 'FCX', 'ORLY', 'APD', 'KLAC', 'MSI', 'GD',
    'MPC', 'TGT', 'EMR', 'PSX', 'MMM', 'PH', 'AJG', 'ROP', 'CARR', 'NSC',
    'PCAR', 'MAR', 'GM', 'CTAS', 'HLT', 'NEM', 'AZO', 'WELL', 'TRV', 'MCHP',
    'AIG', 'FDX', 'OXY', 'ECL', 'F', 'AFL', 'TEL', 'CPRT', 'DXCM', 'KMB',
    'FTNT', 'SRE', 'PAYX', 'D', 'AEP', 'A', 'PSA', 'MSCI', 'O', 'DHI',
    'BK', 'IDXX', 'GIS', 'CCI', 'ROST', 'KDP', 'JCI', 'MNST', 'FAST', 'KMI',
    'YUM', 'CTVA', 'AME', 'AMP', 'ODFL', 'EXC', 'GWW', 'CMI', 'LHX', 'ALL',
    # High-Growth Tech & Popular Stocks
    'NOW', 'UBER', 'ABNB', 'SQ', 'SHOP', 'SNOW', 'PLTR', 'COIN', 'RIVN', 'AI',
    'LCID', 'NIO', 'XPEV', 'LI', 'DKNG', 'RBLX', 'U', 'CRWD', 'ZS', 'OKTA',
    'DDOG', 'NET', 'MDB', 'TWLO', 'DOCU', 'ZM', 'SPOT', 'PINS', 'SNAP', 'TTD',
    'AFRM', 'PATH', 'BILL', 'HUBS', 'ESTC', 'MNDY', 'GTLB', 'S', 'IOT', 'SMCI',
    # Additional S&P 500 & Large Cap
    'VRSK', 'OTIS', 'IQV', 'HAL', 'XEL', 'PCG', 'GEHC', 'CTSH', 'IT', 'HUM',
    'DVN', 'MLM', 'KR', 'EW', 'WEC', 'ED', 'VMC', 'FANG', 'DD', 'PYPL',
    'BIIB', 'WBA', 'DLTR', 'DG', 'EBAY', 'EA', 'TTWO', 'ATVI', 'ZBH', 'SYY',
    'STZ', 'HSY', 'K', 'GPC', 'LEN', 'PHM', 'TOL', 'NVR', 'MTH', 'KBH',
    # Financials & Insurance
    'MS', 'AXP', 'COF', 'DFS', 'SYF', 'ALLY', 'MTB', 'FITB', 'HBAN', 'RF',
    'KEY', 'CFG', 'ZION', 'CMA', 'FRC', 'WAL', 'SIVB', 'SBNY', 'MET', 'PRU',
    # Energy & Materials
    'VLO', 'MRO', 'APA', 'HES', 'BKR', 'NOV', 'RIG', 'DO', 'HP', 'CLR',
    'FSLR', 'ENPH', 'SEDG', 'RUN', 'NOVA', 'ALB', 'LYB', 'DOW', 'CE', 'EMN'
]

# Top Cryptos (TwelveData format)
TOP_CRYPTOS_TD = [
    'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'SOL/USD', 'DOGE/USD', 'ADA/USD',
    'AVAX/USD', 'LINK/USD', 'DOT/USD', 'SHIB/USD', 'TRX/USD', 'UNI/USD', 'ATOM/USD',
    'LTC/USD', 'NEAR/USD', 'APT/USD', 'FIL/USD', 'ARB/USD', 'XMR/USD',
    'BCH/USD', 'XLM/USD', 'ETC/USD', 'HBAR/USD', 'VET/USD', 'ALGO/USD',
    'SAND/USD', 'MANA/USD', 'AAVE/USD', 'THETA/USD', 'XTZ/USD', 'AXS/USD',
    'SNX/USD', 'COMP/USD', 'ZEC/USD', 'DASH/USD', 'ENJ/USD', 'BAT/USD',
    'CRV/USD', 'LRC/USD', 'SUSHI/USD', 'YFI/USD', '1INCH/USD', 'GRT/USD',
    'CHZ/USD', 'IOTA/USD', 'KAVA/USD', 'CELO/USD', 'ZRX/USD', 'ANKR/USD'
]

# Kraken crypto pairs (for volume data)
KRAKEN_CRYPTO_PAIRS = [
    'XXBTZUSD', 'XETHZUSD', 'SOLUSD', 'XRPUSD', 'ADAUSD', 'DOTUSD', 'DOGEUSD',
    'AVAXUSD', 'LINKUSD', 'ATOMUSD', 'LTCUSD', 'UNIUSD', 'XLMUSD', 'ALGOUSD',
    'MANAUSD', 'SANDUSD', 'AAVEUSD', 'GRTUSD', 'ENJUSD', 'BATUSD', 'CRVUSD',
    'COMPUSD', 'MKRUSD', 'SNXUSD', 'YFIUSD', '1INCHUSD', 'SUSHIUSD', 'ZRXUSD'
]

# ETFs (60 major ETFs)
TOP_ETFS = [
    # Major Index ETFs
    'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO', 'EFA', 'EEM',
    'IVV', 'IJH', 'IJR', 'MDY', 'VTV', 'VUG', 'VIG', 'SCHD', 'VYM', 'DVY',
    # Sector ETFs
    'XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLY', 'XLP', 'XLB', 'XLU', 'XLRE',
    'XLC', 'VGT', 'VHT', 'VFH', 'VDE', 'VCR', 'VDC', 'VIS', 'VAW', 'VPU',
    # Commodities & Precious Metals
    'GLD', 'SLV', 'USO', 'UNG', 'DBC', 'GSG', 'PDBC', 'IAU', 'GLDM', 'SIVR',
    # Bonds & Fixed Income
    'TLT', 'IEF', 'SHY', 'LQD', 'HYG', 'JNK', 'BND', 'AGG', 'VCIT', 'VCSH',
    # Thematic & Growth
    'VNQ', 'ARKK', 'ARKG', 'ARKW', 'ARKF', 'SMH', 'XBI', 'IBB', 'KRE', 'XHB',
    # International
    'VEU', 'VXUS', 'IEFA', 'IEMG', 'VWO', 'EWJ', 'FXI', 'EWZ', 'EWT', 'EWY'
]

# Forex pairs
FOREX_PAIRS = [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',
    'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'EUR/CHF', 'EUR/AUD', 'EUR/CAD', 'EUR/NZD',
    'GBP/CHF', 'GBP/AUD', 'GBP/CAD', 'GBP/NZD', 'AUD/JPY', 'AUD/NZD'
]

# Indices
INDICES = ['SPX', 'NDX', 'DJI', 'FTSE', 'DAX', 'CAC', 'HSI', 'NIKKEI']

# FRED Economic Series
FRED_SERIES = {
    'DGS10': '10-Year Treasury',
    'DGS2': '2-Year Treasury',
    'DGS30': '30-Year Treasury',
    'T10Y2Y': '10Y-2Y Spread',
    'FEDFUNDS': 'Fed Funds Rate',
    'VIXCLS': 'VIX Index',
    'SP500': 'S&P 500',
    'UNRATE': 'Unemployment Rate',
    'CPIAUCSL': 'Consumer Price Index',
    'MORTGAGE30US': '30Y Mortgage Rate'
}


# =====================
# TECHNICAL INDICATORS
# =====================

def calculate_indicators(df):
    """Calculate all 29 technical indicators including pivot flags and MFI"""
    if df is None or len(df) < 30:
        return df

    df = df.sort_values('datetime').copy()

    # Ensure numeric columns
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'volume' not in df.columns:
        df['volume'] = 0

    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['volume'].fillna(0)

    # =================
    # Moving Averages
    # =================
    df['sma_20'] = close.rolling(20).mean()
    df['sma_50'] = close.rolling(50).mean() if len(df) >= 50 else np.nan
    df['sma_200'] = close.rolling(200).mean() if len(df) >= 200 else np.nan
    df['ema_12'] = close.ewm(span=12, adjust=False).mean()
    df['ema_26'] = close.ewm(span=26, adjust=False).mean()
    df['ema_50'] = close.ewm(span=50, adjust=False).mean() if len(df) >= 50 else np.nan

    # =================
    # RSI (Wilder's RMA)
    # =================
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta.where(delta < 0, 0))
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df['rsi'] = 100 - (100 / (1 + rs))

    # RSI derivatives
    df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
    df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
    df['rsi_slope'] = df['rsi'].diff(3)
    rsi_mean = df['rsi'].rolling(20).mean()
    rsi_std = df['rsi'].rolling(20).std()
    df['rsi_zscore'] = (df['rsi'] - rsi_mean) / rsi_std.replace(0, np.nan)

    # =================
    # MACD
    # =================
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']

    # MACD Cross detection
    df['macd_cross'] = 0
    macd_above = df['macd'] > df['macd_signal']
    df.loc[macd_above & ~macd_above.shift(1).fillna(False), 'macd_cross'] = 1
    df.loc[~macd_above & macd_above.shift(1).fillna(True), 'macd_cross'] = -1

    # =================
    # Bollinger Bands
    # =================
    df['bb_middle'] = df['sma_20']
    std = close.rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + (2 * std)
    df['bb_lower'] = df['bb_middle'] - (2 * std)
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
    df['bb_percent'] = (close - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

    # =================
    # ATR (True Range)
    # =================
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr'] = tr.ewm(alpha=1/14, adjust=False).mean()

    # =================
    # ADX
    # =================
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    atr_14 = tr.ewm(alpha=1/14, adjust=False).mean()
    df['plus_di'] = 100 * (plus_dm.ewm(alpha=1/14, adjust=False).mean() / atr_14)
    df['minus_di'] = 100 * (minus_dm.ewm(alpha=1/14, adjust=False).mean() / atr_14)
    dx = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']).replace(0, np.nan)
    df['adx'] = dx.ewm(alpha=1/14, adjust=False).mean()

    # =================
    # CCI (Commodity Channel Index)
    # =================
    typical_price = (high + low + close) / 3
    tp_sma = typical_price.rolling(20).mean()
    tp_mad = typical_price.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    df['cci'] = (typical_price - tp_sma) / (0.015 * tp_mad)

    # =================
    # MFI (Money Flow Index) - Requires volume
    # =================
    if volume.sum() > 0:
        mf_multiplier = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
        mf_volume = mf_multiplier * volume
        pos_mf = mf_volume.where(mf_volume > 0, 0).rolling(14).sum()
        neg_mf = (-mf_volume.where(mf_volume < 0, 0)).rolling(14).sum()
        mf_ratio = pos_mf / neg_mf.replace(0, np.nan)
        df['mfi'] = 100 - (100 / (1 + mf_ratio))
    else:
        df['mfi'] = np.nan

    # =================
    # Momentum
    # =================
    df['momentum'] = close.pct_change(10) * 100

    # =================
    # Awesome Oscillator
    # =================
    median_price = (high + low) / 2
    df['awesome_osc'] = median_price.rolling(5).mean() - median_price.rolling(34).mean()

    # =================
    # VWAP Daily
    # =================
    if volume.sum() > 0:
        df['vwap_daily'] = (volume * (high + low + close) / 3).cumsum() / volume.cumsum()
    else:
        df['vwap_daily'] = (high + low + close) / 3

    # =================
    # Pivot Flags (Key ML Features)
    # =================
    lookback = 5
    df['pivot_high_flag'] = 0
    df['pivot_low_flag'] = 0

    for i in range(lookback, len(df) - lookback):
        window_high = high.iloc[i-lookback:i+lookback+1]
        window_low = low.iloc[i-lookback:i+lookback+1]

        if high.iloc[i] == window_high.max():
            df.iloc[i, df.columns.get_loc('pivot_high_flag')] = 1
        if low.iloc[i] == window_low.min():
            df.iloc[i, df.columns.get_loc('pivot_low_flag')] = 1

    # =================
    # OBV (On-Balance Volume)
    # =================
    if volume.sum() > 0:
        obv = [0]
        for i in range(1, len(df)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.append(obv[-1] + volume.iloc[i])
            elif close.iloc[i] < close.iloc[i-1]:
                obv.append(obv[-1] - volume.iloc[i])
            else:
                obv.append(obv[-1])
        df['obv'] = obv
    else:
        df['obv'] = np.nan

    # =================
    # Stochastic Oscillator
    # =================
    lowest_low = low.rolling(14).min()
    highest_high = high.rolling(14).max()
    df['stoch_k'] = 100 * (close - lowest_low) / (highest_high - lowest_low)
    df['stoch_d'] = df['stoch_k'].rolling(3).mean()

    # =================
    # Williams %R
    # =================
    df['williams_r'] = -100 * (highest_high - close) / (highest_high - lowest_low)

    # =================
    # ROC (Rate of Change)
    # =================
    df['roc'] = close.pct_change(12) * 100

    # =================
    # Growth Score (Custom)
    # =================
    df['growth_score'] = 0
    df.loc[(df['rsi'] >= 50) & (df['rsi'] <= 70), 'growth_score'] += 25
    df.loc[df['macd_histogram'] > 0, 'growth_score'] += 25
    df.loc[df['adx'] > 25, 'growth_score'] += 25
    if 'sma_200' in df.columns and not df['sma_200'].isna().all():
        df.loc[df['close'] > df['sma_200'], 'growth_score'] += 25

    # =================
    # SENTIMENT SCORE (0.00 - 1.00)
    # Composite sentiment based on technical + volume + momentum indicators
    # =================
    df['sentiment_score'] = 0.5  # Neutral baseline

    # Technical sentiment components (each adds/subtracts up to 0.125)
    # RSI component (0.125 max)
    rsi_sentiment = np.where(df['rsi'] > 70, -0.125,  # Overbought = bearish
                    np.where(df['rsi'] < 30, 0.125,   # Oversold = bullish
                    np.where(df['rsi'] > 50, 0.0625, -0.0625)))  # Neutral zone
    df['sentiment_score'] += rsi_sentiment

    # MACD sentiment (0.125 max)
    macd_sentiment = np.where(df['macd_histogram'] > 0, 0.125,
                     np.where(df['macd_histogram'] < 0, -0.125, 0))
    df['sentiment_score'] += macd_sentiment

    # MACD Cross sentiment (0.1 max)
    cross_sentiment = np.where(df['macd_cross'] == 1, 0.1,  # Bullish cross
                      np.where(df['macd_cross'] == -1, -0.1, 0))  # Bearish cross
    df['sentiment_score'] += cross_sentiment

    # ADX trend strength (0.075 max)
    adx_sentiment = np.where(df['adx'] > 25, 0.075, 0)  # Strong trend bonus
    df['sentiment_score'] += adx_sentiment

    # Price vs SMA 200 (0.1 max)
    if 'sma_200' in df.columns and not df['sma_200'].isna().all():
        sma_sentiment = np.where(df['close'] > df['sma_200'], 0.1, -0.1)
        df['sentiment_score'] += sma_sentiment

    # Pivot flag sentiment (0.075 max each)
    pivot_high_sentiment = np.where(df['pivot_high_flag'] == 1, -0.075, 0)  # High = potential reversal
    pivot_low_sentiment = np.where(df['pivot_low_flag'] == 1, 0.075, 0)   # Low = potential bounce
    df['sentiment_score'] += pivot_high_sentiment + pivot_low_sentiment

    # MFI sentiment (0.1 max) - Money Flow Index
    if 'mfi' in df.columns and not df['mfi'].isna().all():
        mfi_sentiment = np.where(df['mfi'] > 80, -0.1,  # Overbought
                        np.where(df['mfi'] < 20, 0.1,   # Oversold
                        np.where(df['mfi'] > 50, 0.05, -0.05)))
        df['sentiment_score'] += mfi_sentiment

    # Buy pressure sentiment (0.1 max) - From Kraken buy/sell data
    if 'buy_pressure' in df.columns and not df['buy_pressure'].isna().all():
        buy_pressure_sentiment = (df['buy_pressure'] - 0.5) * 0.2  # -0.1 to +0.1 range
        df['sentiment_score'] += buy_pressure_sentiment.fillna(0)

    # Clamp sentiment to 0.00 - 1.00 range
    df['sentiment_score'] = df['sentiment_score'].clip(0.00, 1.00)
    df['sentiment_score'] = df['sentiment_score'].round(2)

    # =================
    # BUY/SELL/HOLD RECOMMENDATION
    # Based on sentiment score + technical confirmations
    # =================
    df['recommendation'] = 'HOLD'  # Default

    # Strong BUY: High sentiment + technical confirmations
    strong_buy_mask = (
        (df['sentiment_score'] >= 0.70) &
        (df['rsi'] >= 40) & (df['rsi'] <= 70) &
        (df['macd_histogram'] > 0)
    )
    df.loc[strong_buy_mask, 'recommendation'] = 'STRONG_BUY'

    # BUY: Good sentiment + some confirmation
    buy_mask = (
        (df['sentiment_score'] >= 0.55) &
        (df['sentiment_score'] < 0.70) &
        ((df['macd_histogram'] > 0) | (df['rsi'] < 50))
    )
    df.loc[buy_mask, 'recommendation'] = 'BUY'

    # Strong SELL: Low sentiment + bearish confirmations
    strong_sell_mask = (
        (df['sentiment_score'] <= 0.30) &
        (df['macd_histogram'] < 0)
    )
    df.loc[strong_sell_mask, 'recommendation'] = 'STRONG_SELL'

    # SELL: Bearish sentiment + some confirmation
    sell_mask = (
        (df['sentiment_score'] > 0.30) &
        (df['sentiment_score'] <= 0.45) &
        ((df['macd_histogram'] < 0) | (df['rsi'] > 70))
    )
    df.loc[sell_mask, 'recommendation'] = 'SELL'

    return df


# =====================
# DATA FETCHING FUNCTIONS
# =====================

def fetch_twelvedata(symbol, interval='1day', outputsize=5000):
    """Fetch data from TwelveData API"""
    try:
        url = f"{TWELVEDATA_URL}/time_series"
        params = {
            'symbol': symbol,
            'interval': interval,
            'outputsize': outputsize,
            'apikey': TWELVEDATA_API_KEY
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'values' not in data:
            return None

        df = pd.DataFrame(data['values'])
        df['symbol'] = symbol.replace('/', '')
        df['source'] = 'TwelveData'

        # Convert numeric columns
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    except Exception as e:
        print(f"TwelveData error for {symbol}: {e}")
        return None


def fetch_kraken_ohlc(pair, interval=1440):
    """Fetch OHLC data from Kraken with volume and trade count"""
    try:
        six_months_ago = datetime.now() - timedelta(days=180)
        since_timestamp = int(six_months_ago.timestamp())

        url = f"{KRAKEN_URL}/OHLC"
        params = {
            'pair': pair,
            'interval': interval,
            'since': since_timestamp
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if data.get('error'):
            print(f"Kraken error for {pair}: {data['error']}")
            return None

        # Get the data array (first key in result)
        result = data.get('result', {})
        ohlc_key = [k for k in result.keys() if k != 'last']
        if not ohlc_key:
            return None

        ohlc_list = result[ohlc_key[0]]

        records = []
        for candle in ohlc_list:
            records.append({
                'datetime': datetime.fromtimestamp(candle[0]).strftime('%Y-%m-%d'),
                'symbol': pair.replace('XXBT', 'BTC').replace('XETH', 'ETH').replace('ZUSD', 'USD').replace('USD', ''),
                'open': float(candle[1]),
                'high': float(candle[2]),
                'low': float(candle[3]),
                'close': float(candle[4]),
                'vwap': float(candle[5]),
                'volume': float(candle[6]),
                'trade_count': int(candle[7]),  # Number of trades in period
                'source': 'Kraken'
            })

        return pd.DataFrame(records)

    except Exception as e:
        print(f"Kraken error for {pair}: {e}")
        return None


def fetch_kraken_trades(pair, since=None):
    """Fetch recent trades from Kraken to calculate buy/sell volume"""
    try:
        url = f"{KRAKEN_URL}/Trades"
        params = {'pair': pair}
        if since:
            params['since'] = since

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if data.get('error'):
            print(f"Kraken trades error for {pair}: {data['error']}")
            return None

        result = data.get('result', {})
        trades_key = [k for k in result.keys() if k != 'last']
        if not trades_key:
            return None

        trades = result[trades_key[0]]

        # Aggregate buy/sell volume
        buy_volume = 0.0
        sell_volume = 0.0
        buy_count = 0
        sell_count = 0
        total_trades = len(trades)

        for trade in trades:
            # trade format: [price, volume, time, buy/sell, market/limit, misc]
            volume = float(trade[1])
            side = trade[3]  # 'b' = buy, 's' = sell

            if side == 'b':
                buy_volume += volume
                buy_count += 1
            else:
                sell_volume += volume
                sell_count += 1

        return {
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'buy_count': buy_count,
            'sell_count': sell_count,
            'total_trades': total_trades,
            'buy_sell_ratio': buy_volume / sell_volume if sell_volume > 0 else 0,
            'buy_pressure': buy_volume / (buy_volume + sell_volume) if (buy_volume + sell_volume) > 0 else 0.5
        }

    except Exception as e:
        print(f"Kraken trades error for {pair}: {e}")
        return None


def fetch_kraken_full_data(pair):
    """Fetch complete Kraken data: OHLCV + Buy/Sell Volume + Trade Count"""
    try:
        # Get OHLC data
        ohlc_df = fetch_kraken_ohlc(pair)
        if ohlc_df is None or len(ohlc_df) == 0:
            return None

        # Get recent trades for buy/sell breakdown
        trades_data = fetch_kraken_trades(pair)

        if trades_data:
            # Add buy/sell metrics to most recent record
            ohlc_df['buy_volume'] = np.nan
            ohlc_df['sell_volume'] = np.nan
            ohlc_df['buy_count'] = np.nan
            ohlc_df['sell_count'] = np.nan
            ohlc_df['buy_sell_ratio'] = np.nan
            ohlc_df['buy_pressure'] = np.nan

            # Most recent row gets the trade breakdown
            if len(ohlc_df) > 0:
                idx = ohlc_df.index[-1]
                ohlc_df.loc[idx, 'buy_volume'] = trades_data['buy_volume']
                ohlc_df.loc[idx, 'sell_volume'] = trades_data['sell_volume']
                ohlc_df.loc[idx, 'buy_count'] = trades_data['buy_count']
                ohlc_df.loc[idx, 'sell_count'] = trades_data['sell_count']
                ohlc_df.loc[idx, 'buy_sell_ratio'] = trades_data['buy_sell_ratio']
                ohlc_df.loc[idx, 'buy_pressure'] = trades_data['buy_pressure']

        return ohlc_df

    except Exception as e:
        print(f"Kraken full data error for {pair}: {e}")
        return None


def fetch_fred_series(series_id, limit=5000):
    """Fetch data from FRED API"""
    try:
        params = {
            'series_id': series_id,
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'limit': limit,
            'sort_order': 'desc'
        }

        response = requests.get(f"{FRED_URL}/series/observations", params=params, timeout=30)
        data = response.json()

        if 'observations' not in data:
            return None

        df = pd.DataFrame(data['observations'])
        df['series_id'] = series_id
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['datetime'] = pd.to_datetime(df['date'])
        df['source'] = 'FRED'
        df = df[df['value'].notna()]

        return df[['datetime', 'series_id', 'value', 'source']]

    except Exception as e:
        print(f"FRED error for {series_id}: {e}")
        return None


def fetch_finnhub_quote(symbol):
    """Fetch current quote from Finnhub"""
    try:
        url = f"{FINNHUB_URL}/quote"
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }

        response = requests.get(url, params=params, timeout=30)
        return response.json()

    except Exception as e:
        print(f"Finnhub error for {symbol}: {e}")
        return None


def fetch_finnhub_recommendation(symbol):
    """Fetch analyst recommendations from Finnhub"""
    try:
        url = f"{FINNHUB_URL}/stock/recommendation"
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if data and len(data) > 0:
            return data[0]  # Latest recommendation
        return None

    except Exception as e:
        print(f"Finnhub recommendation error for {symbol}: {e}")
        return None


def fetch_coinmarketcap_listings(limit=100):
    """Fetch top cryptos from CoinMarketCap"""
    try:
        url = f"{CMC_URL}/cryptocurrency/listings/latest"
        headers = {'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY}
        params = {'limit': limit, 'convert': 'USD'}

        response = requests.get(url, headers=headers, params=params, timeout=30)
        data = response.json()

        if 'data' not in data:
            return None

        records = []
        for coin in data['data']:
            quote = coin.get('quote', {}).get('USD', {})
            records.append({
                'rank': coin['cmc_rank'],
                'symbol': coin['symbol'],
                'name': coin['name'],
                'price': quote.get('price'),
                'volume_24h': quote.get('volume_24h'),
                'market_cap': quote.get('market_cap'),
                'percent_change_24h': quote.get('percent_change_24h'),
                'percent_change_7d': quote.get('percent_change_7d'),
                'datetime': datetime.now(timezone.utc).isoformat(),
                'source': 'CoinMarketCap'
            })

        return pd.DataFrame(records)

    except Exception as e:
        print(f"CoinMarketCap error: {e}")
        return None


# =====================
# DEDUPLICATION FUNCTIONS
# =====================

def get_existing_keys(client, table_name, symbol_col='symbol', date_col='datetime'):
    """Get existing symbol+datetime combinations from table"""
    try:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

        # Get last 30 days of data to check for duplicates
        query = f"""
        SELECT DISTINCT CONCAT({symbol_col}, '_', CAST({date_col} AS STRING)) as key
        FROM `{table_id}`
        WHERE {date_col} >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        """

        result = client.query(query).result()
        existing_keys = set(row.key for row in result)
        print(f"  Found {len(existing_keys):,} existing keys in {table_name}")
        return existing_keys
    except Exception as e:
        print(f"  Error getting existing keys from {table_name}: {e}")
        return set()


def dedupe_dataframe(df, existing_keys, symbol_col='symbol', date_col='datetime'):
    """Remove rows that already exist in the table"""
    if df is None or len(df) == 0:
        return df

    # Create key column
    df['_key'] = df[symbol_col].astype(str) + '_' + df[date_col].astype(str)

    # Filter out existing records
    before_count = len(df)
    df = df[~df['_key'].isin(existing_keys)]
    after_count = len(df)

    # Remove key column
    if '_key' in df.columns:
        df = df.drop(columns=['_key'])

    if before_count > after_count:
        print(f"    Removed {before_count - after_count:,} duplicate records")

    return df


def upload_with_dedup(client, df, table_name, symbol_col='symbol', date_col='datetime'):
    """Upload data to BigQuery with automatic deduplication"""
    if df is None or len(df) == 0:
        return 0

    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    try:
        # Get existing keys
        existing_keys = get_existing_keys(client, table_name, symbol_col, date_col)

        # Dedupe the dataframe
        df_clean = dedupe_dataframe(df.copy(), existing_keys, symbol_col, date_col)

        if len(df_clean) == 0:
            print(f"  No new records to upload to {table_name}")
            return 0

        # Upload only new records
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
        )

        job = client.load_table_from_dataframe(df_clean, table_id, job_config=job_config)
        job.result()

        print(f"  Uploaded {len(df_clean):,} NEW records to {table_name}")
        return len(df_clean)

    except Exception as e:
        print(f"  Upload error for {table_name}: {e}")
        return 0


# =====================
# MAIN CLOUD FUNCTION
# =====================

@functions_framework.http
def multi_source_fetcher(request):
    """Main entry point for multi-source data fetching"""
    start_time = datetime.now(timezone.utc)
    print(f"Starting multi-source fetch at {start_time}")
    print("NOTE: Deduplication enabled - only NEW records will be inserted")

    results = {
        'twelvedata': {'records': 0, 'symbols': 0, 'errors': 0},
        'kraken': {'records': 0, 'symbols': 0, 'errors': 0},
        'fred': {'records': 0, 'series': 0, 'errors': 0},
        'finnhub': {'records': 0, 'symbols': 0, 'errors': 0},
        'coinmarketcap': {'records': 0, 'errors': 0}
    }

    try:
        client = bigquery.Client(project=PROJECT_ID)

        # ===================
        # 1. TWELVEDATA - Stocks (Primary source)
        # ===================
        print("\n=== FETCHING FROM TWELVEDATA (Stocks) ===")
        stock_data = []
        for symbol in TOP_STOCKS:  # ALL 200 stocks (was 150)
            df = fetch_twelvedata(symbol, '1day', 5000)
            if df is not None and len(df) > 0:
                df['asset_type'] = 'STOCK'
                df = calculate_indicators(df)
                stock_data.append(df)
                results['twelvedata']['symbols'] += 1
                results['twelvedata']['records'] += len(df)
                print(f"  {symbol}: {len(df)} records")
            else:
                results['twelvedata']['errors'] += 1
            time.sleep(0.5)  # Optimized for 800/min capacity (120 calls/min)

        # Upload stocks to BigQuery (with deduplication)
        if stock_data:
            stocks_df = pd.concat(stock_data, ignore_index=True)
            stocks_df['fetch_timestamp'] = datetime.now(timezone.utc)

            print(f"\nUploading stocks with deduplication...")
            uploaded = upload_with_dedup(client, stocks_df, 'stocks_daily_clean')
            results['twelvedata']['records'] = uploaded

        # ===================
        # 2. TWELVEDATA - Crypto
        # ===================
        print("\n=== FETCHING FROM TWELVEDATA (Crypto) ===")
        crypto_data = []
        for symbol in TOP_CRYPTOS_TD:  # ALL 50 cryptos (was 40)
            df = fetch_twelvedata(symbol, '1day', 5000)
            if df is not None and len(df) > 0:
                df['asset_type'] = 'CRYPTO'
                crypto_data.append(df)
                results['twelvedata']['symbols'] += 1
                results['twelvedata']['records'] += len(df)
                print(f"  {symbol}: {len(df)} records")
            else:
                results['twelvedata']['errors'] += 1
            time.sleep(0.5)  # Optimized for 800/min capacity

        # ===================
        # 3. KRAKEN - Crypto Volume Data (For MFI calculation + Buy/Sell Volume)
        # ===================
        print("\n=== FETCHING FROM KRAKEN (Crypto Volume + Buy/Sell Data) ===")
        kraken_data = []
        for pair in KRAKEN_CRYPTO_PAIRS[:20]:  # Top 20 for volume
            df = fetch_kraken_full_data(pair)  # Now includes buy/sell volume
            if df is not None and len(df) > 0:
                df['asset_type'] = 'CRYPTO'
                df = calculate_indicators(df)  # Now has real volume for MFI
                kraken_data.append(df)
                results['kraken']['symbols'] += 1
                results['kraken']['records'] += len(df)

                # Log buy/sell data if available
                if 'buy_volume' in df.columns and not df['buy_volume'].isna().all():
                    latest = df.iloc[-1]
                    print(f"  {pair}: {len(df)} records | Buy: {latest.get('buy_volume', 0):.2f} | Sell: {latest.get('sell_volume', 0):.2f} | Trades: {latest.get('trade_count', 0)}")
                else:
                    print(f"  {pair}: {len(df)} records with volume")
            else:
                results['kraken']['errors'] += 1
            time.sleep(2.0)  # Kraken rate limiting (extra time for trades API)

        # Upload crypto data (combine TwelveData + Kraken volume data) with deduplication
        all_crypto = crypto_data + kraken_data
        if all_crypto:
            crypto_df = pd.concat(all_crypto, ignore_index=True)
            crypto_df['fetch_timestamp'] = datetime.now(timezone.utc)

            print(f"\nUploading crypto with deduplication...")
            uploaded = upload_with_dedup(client, crypto_df, 'crypto_daily_clean')
            results['kraken']['records'] = uploaded

        # ===================
        # 4. TWELVEDATA - ETFs
        # ===================
        print("\n=== FETCHING FROM TWELVEDATA (ETFs) ===")
        etf_data = []
        for symbol in TOP_ETFS:
            df = fetch_twelvedata(symbol, '1day', 5000)
            if df is not None and len(df) > 0:
                df['asset_type'] = 'ETF'
                df = calculate_indicators(df)
                etf_data.append(df)
                results['twelvedata']['symbols'] += 1
                results['twelvedata']['records'] += len(df)
                print(f"  {symbol}: {len(df)} records")
            else:
                results['twelvedata']['errors'] += 1
            time.sleep(0.5)  # Optimized for 800/min capacity

        if etf_data:
            etfs_df = pd.concat(etf_data, ignore_index=True)
            etfs_df['fetch_timestamp'] = datetime.now(timezone.utc)

            print(f"\nUploading ETFs with deduplication...")
            upload_with_dedup(client, etfs_df, 'etfs_daily_clean')

        # ===================
        # 4b. TWELVEDATA - Forex (per masterquery.md)
        # ===================
        print("\n=== FETCHING FROM TWELVEDATA (Forex) ===")
        forex_data = []
        for symbol in FOREX_PAIRS:  # 20 forex pairs
            df = fetch_twelvedata(symbol, '1day', 5000)
            if df is not None and len(df) > 0:
                df['asset_type'] = 'FOREX'
                df = calculate_indicators(df)
                forex_data.append(df)
                results['twelvedata']['symbols'] += 1
                results['twelvedata']['records'] += len(df)
                print(f"  {symbol}: {len(df)} records")
            else:
                results['twelvedata']['errors'] += 1
            time.sleep(0.5)  # Optimized for 800/min capacity

        if forex_data:
            forex_df = pd.concat(forex_data, ignore_index=True)
            forex_df['fetch_timestamp'] = datetime.now(timezone.utc)

            print(f"\nUploading Forex with deduplication...")
            upload_with_dedup(client, forex_df, 'forex_daily_clean')

        # ===================
        # 4c. TWELVEDATA - Indices (per masterquery.md)
        # ===================
        print("\n=== FETCHING FROM TWELVEDATA (Indices) ===")
        indices_data = []
        for symbol in INDICES:  # 8 major indices
            df = fetch_twelvedata(symbol, '1day', 5000)
            if df is not None and len(df) > 0:
                df['asset_type'] = 'INDEX'
                df = calculate_indicators(df)
                indices_data.append(df)
                results['twelvedata']['symbols'] += 1
                results['twelvedata']['records'] += len(df)
                print(f"  {symbol}: {len(df)} records")
            else:
                results['twelvedata']['errors'] += 1
            time.sleep(0.5)  # Optimized for 800/min capacity

        if indices_data:
            indices_df = pd.concat(indices_data, ignore_index=True)
            indices_df['fetch_timestamp'] = datetime.now(timezone.utc)

            print(f"\nUploading Indices with deduplication...")
            upload_with_dedup(client, indices_df, 'indices_daily_clean')

        # ===================
        # 5. FRED - Economic Data
        # ===================
        print("\n=== FETCHING FROM FRED (Economic Data) ===")
        fred_data = []
        for series_id, name in FRED_SERIES.items():
            df = fetch_fred_series(series_id, 1000)
            if df is not None and len(df) > 0:
                fred_data.append(df)
                results['fred']['series'] += 1
                results['fred']['records'] += len(df)
                print(f"  {series_id} ({name}): {len(df)} records")
            else:
                results['fred']['errors'] += 1
            time.sleep(0.5)

        if fred_data:
            fred_df = pd.concat(fred_data, ignore_index=True)
            fred_df['fetch_timestamp'] = datetime.now(timezone.utc)
            table_id = f"{PROJECT_ID}.{DATASET_ID}.fred_economic_data"

            try:
                job_config = bigquery.LoadJobConfig(
                    write_disposition=bigquery.WriteDisposition.WRITE_APPEND
                )
                job = client.load_table_from_dataframe(fred_df, table_id, job_config=job_config)
                job.result()
                print(f"Uploaded {len(fred_df)} FRED records to BigQuery")
            except Exception as e:
                print(f"FRED upload error: {e}")

        # ===================
        # 6. FINNHUB - Analyst Recommendations
        # ===================
        print("\n=== FETCHING FROM FINNHUB (Analyst Ratings) ===")
        finnhub_data = []
        for symbol in TOP_STOCKS[:50]:  # Top 50 stocks
            rec = fetch_finnhub_recommendation(symbol)
            if rec:
                rec['symbol'] = symbol
                rec['fetch_timestamp'] = datetime.now(timezone.utc).isoformat()
                finnhub_data.append(rec)
                results['finnhub']['symbols'] += 1
                results['finnhub']['records'] += 1
                print(f"  {symbol}: Got recommendation")
            else:
                results['finnhub']['errors'] += 1
            time.sleep(1.2)  # Finnhub rate limiting

        if finnhub_data:
            finnhub_df = pd.DataFrame(finnhub_data)
            table_id = f"{PROJECT_ID}.{DATASET_ID}.finnhub_recommendations"

            try:
                job_config = bigquery.LoadJobConfig(
                    write_disposition=bigquery.WriteDisposition.WRITE_APPEND
                )
                job = client.load_table_from_dataframe(finnhub_df, table_id, job_config=job_config)
                job.result()
                print(f"Uploaded {len(finnhub_df)} Finnhub records to BigQuery")
            except Exception as e:
                print(f"Finnhub upload error: {e}")

        # ===================
        # 7. COINMARKETCAP - Crypto Rankings
        # ===================
        print("\n=== FETCHING FROM COINMARKETCAP (Rankings) ===")
        cmc_df = fetch_coinmarketcap_listings(100)
        if cmc_df is not None and len(cmc_df) > 0:
            results['coinmarketcap']['records'] = len(cmc_df)
            table_id = f"{PROJECT_ID}.{DATASET_ID}.cmc_crypto_rankings"

            try:
                job_config = bigquery.LoadJobConfig(
                    write_disposition=bigquery.WriteDisposition.WRITE_APPEND
                )
                job = client.load_table_from_dataframe(cmc_df, table_id, job_config=job_config)
                job.result()
                print(f"Uploaded {len(cmc_df)} CoinMarketCap records to BigQuery")
            except Exception as e:
                results['coinmarketcap']['errors'] += 1
                print(f"CMC upload error: {e}")

        # ===================
        # Calculate totals
        # ===================
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds() / 60

        total_records = sum([
            results['twelvedata']['records'],
            results['kraken']['records'],
            results['fred']['records'],
            results['finnhub']['records'],
            results['coinmarketcap']['records']
        ])

        response = {
            'status': 'success',
            'timestamp': end_time.isoformat(),
            'duration_minutes': round(duration, 1),
            'total_records': total_records,
            'quota_used': f"{(total_records / 2000000 * 100):.1f}%",
            'sources': results
        }

        print(f"\n=== COMPLETED ===")
        print(f"Total Records: {total_records:,}")
        print(f"Duration: {round(duration, 1)} minutes")
        print(f"TwelveData: {results['twelvedata']['records']:,} records")
        print(f"Kraken: {results['kraken']['records']:,} records (with volume)")
        print(f"FRED: {results['fred']['records']:,} records")
        print(f"Finnhub: {results['finnhub']['records']:,} records")
        print(f"CoinMarketCap: {results['coinmarketcap']['records']:,} records")

        return response, 200

    except Exception as e:
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return {
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }, 500


if __name__ == "__main__":
    # Local testing
    class FakeRequest:
        def get_json(self, silent=False):
            return {}

    result, status = multi_source_fetcher(FakeRequest())
    print(json.dumps(result, indent=2))
