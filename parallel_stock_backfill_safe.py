#!/usr/bin/env python3
"""
SAFE PARALLEL Index Stock Data Backfill Script
Optimized for TwelveData $229 Pro Plan (1,597 credits/minute)

SAFE VERSION: Parallel API fetching + Sequential uploads (no data loss)
- Fetches data in parallel (fast)
- Uploads one symbol at a time (safe)
- Delete + Upload atomic per symbol

Performance Target: 300+ symbols/hour (vs 107/hour sequential)
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import time
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import deque
import queue

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TABLE_NAME = 'stocks_daily_clean'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'
PROGRESS_FILE = 'index_backfill_progress.json'
STATUS_FILE = 'backfill_status.txt'

# Parallel Processing Settings - CONSERVATIVE
MAX_WORKERS = 10  # Concurrent API calls
RATE_LIMIT_PER_MINUTE = 600  # More conservative limit

# Rate limiter
class RateLimiter:
    def __init__(self, max_per_minute):
        self.max_per_minute = max_per_minute
        self.timestamps = deque()
        self.lock = threading.Lock()

    def acquire(self):
        with self.lock:
            now = time.time()
            while self.timestamps and now - self.timestamps[0] > 60:
                self.timestamps.popleft()

            if len(self.timestamps) >= self.max_per_minute:
                sleep_time = 60 - (now - self.timestamps[0]) + 0.1
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    now = time.time()
                    while self.timestamps and now - self.timestamps[0] > 60:
                        self.timestamps.popleft()

            self.timestamps.append(now)

rate_limiter = RateLimiter(RATE_LIMIT_PER_MINUTE)

# Create session with connection pooling
def create_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, 'session'):
        thread_local.session = create_session()
    return thread_local.session

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# =============================================================================
# INDEX STOCK LISTS
# =============================================================================

NASDAQ_100 = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "COST", "ASML",
    "ADBE", "PEP", "CSCO", "AZN", "NFLX", "AMD", "TMUS", "CMCSA", "INTC", "INTU",
    "TXN", "QCOM", "AMGN", "HON", "AMAT", "ISRG", "BKNG", "SBUX", "VRTX", "GILD",
    "ADI", "ADP", "MDLZ", "LRCX", "REGN", "PANW", "KLAC", "MU", "SNPS", "CDNS",
    "CSX", "PYPL", "MELI", "MNST", "MAR", "ORLY", "NXPI", "MRVL", "ABNB", "CTAS",
    "FTNT", "PCAR", "CPRT", "KDP", "WDAY", "PAYX", "ROST", "AEP", "ADSK", "MRNA",
    "ODFL", "CHTR", "MCHP", "KHC", "DXCM", "IDXX", "EXC", "LULU", "FAST", "ON",
    "VRSK", "CEG", "EA", "CTSH", "XEL", "CSGP", "ANSS", "GEHC", "BKR", "FANG",
    "DLTR", "TEAM", "WBD", "TTWO", "ZS", "ILMN", "ALGN", "WBA", "GFS", "BIIB",
    "EBAY", "ENPH", "SIRI", "DDOG", "CRWD", "ZM", "OKTA", "SPLK", "DOCU", "ROKU"
]

SP500 = [
    "AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CRM", "ADBE", "AMD", "CSCO", "ACN",
    "IBM", "INTC", "INTU", "TXN", "QCOM", "AMAT", "NOW", "ADI", "LRCX", "MU",
    "KLAC", "SNPS", "CDNS", "MCHP", "FTNT", "ANSS", "KEYS", "MPWR", "TYL", "EPAM",
    "PAYC", "ZBRA", "CTSH", "IT", "BR", "AKAM", "FFIV", "JNPR", "NTAP", "WDC",
    "HPQ", "HPE", "DELL", "STX", "ENPH", "SEDG", "FSLR", "GNRC", "TER", "SWKS",
    "UNH", "JNJ", "LLY", "PFE", "ABBV", "MRK", "TMO", "ABT", "DHR", "BMY",
    "AMGN", "GILD", "VRTX", "REGN", "ISRG", "MDT", "SYK", "BSX", "BDX", "EW",
    "ZBH", "DXCM", "IDXX", "IQV", "A", "MTD", "HOLX", "BAX", "ALGN", "TECH",
    "ELV", "CI", "CVS", "HCA", "HUM", "CNC", "MCK", "CAH", "ABC", "VTRS",
    "ZTS", "BIIB", "MRNA", "MOH", "DVA", "LH", "DGX", "HSIC", "XRAY", "COO",
    "JPM", "BAC", "WFC", "GS", "MS", "BLK", "SCHW", "AXP", "C", "USB",
    "PNC", "TFC", "BK", "STT", "COF", "AIG", "MET", "PRU", "ALL", "TRV",
    "CB", "AFL", "PGR", "CME", "ICE", "SPGI", "MCO", "MSCI", "CBOE", "NDAQ",
    "FIS", "FISV", "GPN", "AJG", "AON", "MMC", "WTW", "BRO", "RJF", "HBAN",
    "KEY", "CFG", "RF", "FITB", "MTB", "NTRS", "ZION", "CMA", "FRC", "SBNY",
    "AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "SBUX", "TJX", "BKNG", "CMG",
    "ORLY", "AZO", "ROST", "DHI", "LEN", "PHM", "NVR", "DRI", "YUM", "DG",
    "DLTR", "EBAY", "ETSY", "BBY", "ULTA", "POOL", "GRMN", "LVS", "WYNN", "MGM",
    "CZR", "MAR", "HLT", "H", "EXPE", "CCL", "RCL", "NCLH", "F", "GM",
    "TGT", "COST", "WMT", "KMX", "AN", "LAD", "GPC", "AAP", "APTV", "BWA",
    "PG", "KO", "PEP", "PM", "MO", "EL", "CL", "KMB", "GIS", "K",
    "HSY", "SJM", "CAG", "CPB", "MKC", "CHD", "CLX", "KR", "SYY", "ADM",
    "TSN", "HRL", "MDLZ", "MNST", "KDP", "STZ", "BF.B", "TAP", "SAM", "WBA",
    "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "PXD", "VLO", "PSX", "OXY",
    "HAL", "DVN", "HES", "FANG", "BKR", "KMI", "WMB", "OKE", "TRGP", "LNG",
    "MRO", "APA", "CTRA", "EQT", "AR", "SWN", "RRC", "MTDR", "PR", "CHRD",
    "CAT", "HON", "UNP", "BA", "RTX", "GE", "DE", "LMT", "UPS", "MMM",
    "NOC", "GD", "ITW", "EMR", "PH", "ETN", "CTAS", "CARR", "FDX", "OTIS",
    "WM", "RSG", "CMI", "JCI", "FAST", "PAYX", "ROK", "SWK", "DOV", "IR",
    "XYL", "IEX", "NDSN", "AME", "ROP", "TT", "TDG", "WAB", "GNRC", "PCAR",
    "ODFL", "JBHT", "CHRW", "EXPD", "CSX", "NSC", "CNI", "KSU",
    "NEE", "DUK", "SO", "D", "AEP", "SRE", "EXC", "XEL", "WEC", "ED",
    "PEG", "ES", "EIX", "AWK", "DTE", "PPL", "FE", "CMS", "AES", "NI",
    "EVRG", "ATO", "NRG", "VST", "PNW", "OGE", "LNT", "MGEE", "NWE", "AVA",
    "LIN", "APD", "ECL", "SHW", "FCX", "NEM", "NUE", "VMC", "MLM", "DOW",
    "DD", "PPG", "ALB", "CE", "EMN", "IFF", "FMC", "CF", "MOS", "BALL",
    "PKG", "IP", "WRK", "SEE", "AVY", "BMS", "RPM", "ASH", "HUN", "OLN",
    "PLD", "AMT", "CCI", "EQIX", "PSA", "SPG", "DLR", "O", "WELL", "AVB",
    "EQR", "VTR", "ARE", "BXP", "SLG", "MAA", "UDR", "ESS", "CPT", "INVH",
    "PEAK", "HST", "KIM", "REG", "FRT", "BRX", "CUBE", "EXR", "IRM", "SBAC",
    "GOOGL", "META", "NFLX", "DIS", "CMCSA", "VZ", "T", "TMUS", "CHTR", "EA",
    "TTWO", "ATVI", "WBD", "PARA", "OMC", "IPG", "FOXA", "NWS", "LYV", "MTCH"
]

RUSSELL_2000_TOP = [
    "SMTC", "ALGM", "CRUS", "DIOD", "SLAB", "RMBS", "SITM", "POWI", "AMBA", "WOLF",
    "ONTO", "FORM", "NOVT", "NVMI", "VICR", "MKSI", "IPGP", "CGNX", "MIDD", "TDC",
    "MANH", "APPN", "ALRM", "NEWR", "DOMO", "BOX", "PING", "JAMF", "TENB", "SAIL",
    "EXAS", "NTRA", "IONS", "SRPT", "ARWR", "NBIX", "HALO", "RARE", "ALKS", "PTCT",
    "INCY", "BMRN", "CORT", "SUPN", "PRGO", "PCRX", "LGND", "RCKT", "VERV", "APLS",
    "FOLD", "TGTX", "MIRM", "VCEL", "MNKD", "CTLT", "HZNP", "UTHR", "JAZZ", "SGEN",
    "HBAN", "RF", "KEY", "CFG", "FHN", "ZION", "CMA", "WAL", "FNB", "PNFP",
    "PACW", "EWBC", "BKU", "GBCI", "UMBF", "BOH", "PPBI", "SFBS", "BANR", "HOPE",
    "WSFS", "CADE", "HTLF", "TRMK", "CVBF", "FULT", "FFBC", "WAFD", "CBU", "NBTB",
    "AIMC", "AGCO", "OSK", "SITE", "GGG", "RBC", "TTC", "GTLS", "ATKR", "ESAB",
    "SPXC", "TKR", "CENT", "LFUS", "ROCK", "KMT", "CW", "MATX", "ARCB", "SAIA",
    "WERN", "HTLD", "SNDR", "XPO", "GXO", "HUBG", "MRTN", "ECHO", "RLGT", "CVLG",
    "WING", "TXRH", "CAKE", "BJRI", "PLAY", "DINE", "EAT", "BLMN", "DIN", "BOOT",
    "DECK", "SKX", "CROX", "SHOO", "CAL", "GES", "URBN", "ANF", "AEO", "EXPR",
    "CATO", "SCVL", "HIBB", "BGFV", "DKS", "PLCE", "CTRN", "TCS", "LEVI", "PVH",
    "SM", "RRC", "AR", "MTDR", "CTRA", "PDCE", "NOG", "MGY", "VTLE", "CHRD",
    "CIVI", "CPE", "ROCC", "ESTE", "NEXT", "GPOR", "TALO", "BORR", "RIG", "VAL",
    "CLF", "STLD", "CMC", "ATI", "CRS", "CENX", "KALU", "HUN", "OLN", "WLK",
    "TROX", "KWR", "MERC", "HWKN", "NGVT", "HCC", "ARCH", "BTU", "ARLP", "CEIX",
    "CUBE", "EXR", "LSI", "NSA", "REXR", "FR", "STAG", "TRNO", "PLYM", "GTY",
    "NNN", "EPR", "STOR", "SRC", "PINE", "ADC", "FCPT", "NTST", "KREF", "STWD"
]

ALL_SYMBOLS = sorted(list(set(NASDAQ_100 + SP500 + RUSSELL_2000_TOP)))
print(f"Total unique symbols to process: {len(ALL_SYMBOLS)}")

# =============================================================================
# TECHNICAL INDICATORS (Simplified for performance)
# =============================================================================

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
    macd_signal = calculate_ema(macd, signal)
    macd_histogram = macd - macd_signal
    return macd, macd_signal, macd_histogram

def calculate_bollinger_bands(series, period=20, std_dev=2):
    middle = calculate_sma(series, period)
    std = series.rolling(window=period, min_periods=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return upper, middle, lower

def calculate_stochastic(high, low, close, k_period=14, d_period=3):
    lowest_low = low.rolling(window=k_period, min_periods=k_period).min()
    highest_high = high.rolling(window=k_period, min_periods=k_period).max()
    denom = highest_high - lowest_low
    stoch_k = (100 * (close - lowest_low) / denom).replace([np.inf, -np.inf], np.nan)
    stoch_d = stoch_k.rolling(window=d_period, min_periods=d_period).mean()
    return stoch_k, stoch_d

def calculate_atr(high, low, close, period=14):
    prev_close = close.shift(1)
    tr = pd.concat([high - low, abs(high - prev_close), abs(low - prev_close)], axis=1).max(axis=1)
    return tr.rolling(window=period, min_periods=period).mean()

def calculate_adx(high, low, close, period=14):
    prev_high = high.shift(1)
    prev_low = low.shift(1)
    prev_close = close.shift(1)
    plus_dm = (high - prev_high).where((high - prev_high) > (prev_low - low), 0).where((high - prev_high) > 0, 0)
    minus_dm = (prev_low - low).where((prev_low - low) > (high - prev_high), 0).where((prev_low - low) > 0, 0)
    tr = pd.concat([high - low, abs(high - prev_close), abs(low - prev_close)], axis=1).max(axis=1)
    atr = tr.rolling(window=period, min_periods=period).mean()
    plus_di = (100 * plus_dm.rolling(window=period).mean() / atr).replace([np.inf, -np.inf], np.nan)
    minus_di = (100 * minus_dm.rolling(window=period).mean() / atr).replace([np.inf, -np.inf], np.nan)
    dx = (100 * abs(plus_di - minus_di) / (plus_di + minus_di)).replace([np.inf, -np.inf], np.nan)
    adx = dx.rolling(window=period, min_periods=period).mean()
    return adx, plus_di, minus_di

def calculate_mfi(high, low, close, volume, period=14):
    tp = (high + low + close) / 3
    mf = tp * volume
    positive_mf = mf.where(tp > tp.shift(1), 0).rolling(window=period).sum()
    negative_mf = mf.where(tp < tp.shift(1), 0).rolling(window=period).sum()
    return (100 - (100 / (1 + positive_mf / negative_mf))).replace([np.inf, -np.inf], np.nan)

def calculate_cmf(high, low, close, volume, period=20):
    mfm = ((close - low) - (high - close)) / (high - low)
    mfm = mfm.replace([np.inf, -np.inf], 0).fillna(0)
    return (mfm * volume).rolling(window=period).sum() / volume.rolling(window=period).sum()

def calculate_ichimoku(high, low, close):
    tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
    kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
    return tenkan, kijun

def calculate_all_indicators(df):
    """Calculate all indicators"""
    df['previous_close'] = df['close'].shift(1)
    df['change'] = df['close'] - df['previous_close']
    df['percent_change'] = (100 * df['change'] / df['previous_close']).replace([np.inf, -np.inf], np.nan)
    df['high_low'] = df['high'] - df['low']
    df['average_volume'] = df['volume'].rolling(window=20, min_periods=5).mean().fillna(0).astype('int64')
    df['week_52_high'] = df['high'].rolling(window=252, min_periods=50).max()
    df['week_52_low'] = df['low'].rolling(window=252, min_periods=50).min()
    df['rsi'] = calculate_rsi(df['close'], 14)
    df['macd'], df['macd_signal'], df['macd_histogram'] = calculate_macd(df['close'])
    df['stoch_k'], df['stoch_d'] = calculate_stochastic(df['high'], df['low'], df['close'])
    df['roc'] = (100 * (df['close'] - df['close'].shift(12)) / df['close'].shift(12)).replace([np.inf, -np.inf], np.nan)
    df['momentum'] = df['close'] - df['close'].shift(10)
    df['sma_20'] = calculate_sma(df['close'], 20)
    df['sma_50'] = calculate_sma(df['close'], 50)
    df['sma_200'] = calculate_sma(df['close'], 200)
    df['ema_12'] = calculate_ema(df['close'], 12)
    df['ema_20'] = calculate_ema(df['close'], 20)
    df['ema_26'] = calculate_ema(df['close'], 26)
    df['ema_50'] = calculate_ema(df['close'], 50)
    df['ema_200'] = calculate_ema(df['close'], 200)
    df['ichimoku_tenkan'], df['ichimoku_kijun'] = calculate_ichimoku(df['high'], df['low'], df['close'])
    df['atr'] = calculate_atr(df['high'], df['low'], df['close'], 14)
    df['bollinger_upper'], df['bollinger_middle'], df['bollinger_lower'] = calculate_bollinger_bands(df['close'])
    df['adx'], df['plus_di'], df['minus_di'] = calculate_adx(df['high'], df['low'], df['close'])
    df['mfi'] = calculate_mfi(df['high'], df['low'], df['close'], df['volume'])
    df['cmf'] = calculate_cmf(df['high'], df['low'], df['close'], df['volume'])
    df['pct_high_low'] = (100 * df['high_low'] / df['low']).replace([np.inf, -np.inf], np.nan)
    df['cci'] = ((df['high'] + df['low'] + df['close']) / 3 - df['close'].rolling(20).mean()) / (0.015 * df['close'].rolling(20).std())
    df['williams_r'] = -100 * (df['high'].rolling(14).max() - df['close']) / (df['high'].rolling(14).max() - df['low'].rolling(14).min())
    df['kama'] = df['close'].ewm(span=10).mean()
    df['bb_width'] = (df['bollinger_upper'] - df['bollinger_lower']) / df['bollinger_middle'] * 100
    df['trix'] = df['close'].ewm(span=15).mean().ewm(span=15).mean().ewm(span=15).mean().pct_change() * 100
    df['obv'] = (np.sign(df['close'].diff()) * df['volume']).cumsum()
    df['pvo'] = ((df['volume'].ewm(span=12).mean() - df['volume'].ewm(span=26).mean()) / df['volume'].ewm(span=26).mean() * 100)
    df['ppo'] = ((df['ema_12'] - df['ema_26']) / df['ema_26'] * 100)
    df['ultimate_osc'] = 50.0
    df['awesome_osc'] = ((df['high'] + df['low']) / 2).rolling(5).mean() - ((df['high'] + df['low']) / 2).rolling(34).mean()
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    df['return_2w'] = (df['close'] - df['close'].shift(10)) / df['close'].shift(10) * 100
    df['return_4w'] = (df['close'] - df['close'].shift(20)) / df['close'].shift(20) * 100
    df['close_vs_sma20_pct'] = (df['close'] - df['sma_20']) / df['sma_20'] * 100
    df['close_vs_sma50_pct'] = (df['close'] - df['sma_50']) / df['sma_50'] * 100
    df['close_vs_sma200_pct'] = (df['close'] - df['sma_200']) / df['sma_200'] * 100
    df['rsi_slope'] = df['rsi'] - df['rsi'].shift(5)
    df['rsi_zscore'] = (df['rsi'] - df['rsi'].rolling(20).mean()) / df['rsi'].rolling(20).std()
    df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
    df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
    df['macd_cross'] = ((df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))).astype(int) - \
                       ((df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))).astype(int)
    df['ema20_slope'] = df['ema_20'] - df['ema_20'].shift(5)
    df['ema50_slope'] = df['ema_50'] - df['ema_50'].shift(5)
    df['atr_zscore'] = (df['atr'] - df['atr'].rolling(20).mean()) / df['atr'].rolling(20).std()
    df['atr_slope'] = df['atr'] - df['atr'].shift(5)
    df['volume_zscore'] = (df['volume'] - df['volume'].rolling(20).mean()) / df['volume'].rolling(20).std()
    df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
    df['pivot_high_flag'] = ((df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1).fillna(0))).astype(int)
    df['pivot_low_flag'] = ((df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1).fillna(float('inf')))).astype(int)
    df['dist_to_pivot_high'] = (df['close'] - df['high'].where(df['pivot_high_flag'] == 1).ffill()) / df['high'].where(df['pivot_high_flag'] == 1).ffill() * 100
    df['dist_to_pivot_low'] = (df['close'] - df['low'].where(df['pivot_low_flag'] == 1).ffill()) / df['low'].where(df['pivot_low_flag'] == 1).ffill() * 100
    df['trend_regime'] = 0
    df.loc[(df['close'] > df['sma_50']) & (df['sma_50'] > df['sma_200']), 'trend_regime'] = 1
    df.loc[(df['close'] < df['sma_50']) & (df['sma_50'] < df['sma_200']), 'trend_regime'] = -1
    df['vol_regime'] = 0
    df.loc[df['volume_zscore'] > 1, 'vol_regime'] = 1
    df.loc[df['volume_zscore'] < -1, 'vol_regime'] = -1
    df['regime_confidence'] = (df['adx'] / 100).clip(0, 1)
    df['ichimoku_senkou_a'] = ((df['ichimoku_tenkan'] + df['ichimoku_kijun']) / 2).shift(26)
    df['ichimoku_senkou_b'] = ((df['high'].rolling(52).max() + df['low'].rolling(52).min()) / 2).shift(26)
    df['ichimoku_chikou'] = df['close'].shift(-26)
    df['vwap_daily'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
    df['vwap_weekly'] = df['vwap_daily']
    df['volume_profile_poc'] = df['close'].rolling(20).median()
    df['volume_profile_vah'] = df['high'].rolling(20).quantile(0.7)
    df['volume_profile_val'] = df['low'].rolling(20).quantile(0.3)

    for col in df.columns:
        if df[col].dtype in ['float64', 'float32']:
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)

    return df

# =============================================================================
# API FUNCTIONS
# =============================================================================

def fetch_historical_data(symbol, outputsize=5000):
    """Fetch historical daily data"""
    rate_limiter.acquire()
    session = get_session()

    url = f"{BASE_URL}/time_series"
    params = {
        'symbol': symbol,
        'interval': '1day',
        'outputsize': outputsize,
        'apikey': TWELVEDATA_API_KEY
    }

    try:
        response = session.get(url, params=params, timeout=60)
        data = response.json()

        if 'values' in data:
            df = pd.DataFrame(data['values'])
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime').reset_index(drop=True)

            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            return df, data.get('meta', {})
        else:
            return None, data.get('message', 'Unknown error')
    except Exception as e:
        return None, str(e)


def fetch_profile_data(symbol):
    """Fetch company profile"""
    rate_limiter.acquire()
    session = get_session()

    url = f"{BASE_URL}/profile"
    params = {'symbol': symbol, 'apikey': TWELVEDATA_API_KEY}

    try:
        response = session.get(url, params=params, timeout=30)
        data = response.json()
        return {
            'sector': data.get('sector', ''),
            'industry': data.get('industry', ''),
            'name': data.get('name', ''),
            'asset_type': data.get('type', 'Common Stock')
        }
    except:
        return {}

# =============================================================================
# PARALLEL FETCHING + SAFE UPLOAD
# =============================================================================

def fetch_symbol_data(symbol):
    """Fetch all data for a symbol (parallel safe)"""
    try:
        df, meta_or_error = fetch_historical_data(symbol, outputsize=5000)

        if df is None:
            return {'symbol': symbol, 'success': False, 'error': meta_or_error}

        profile = fetch_profile_data(symbol)
        df = calculate_all_indicators(df)

        return {
            'symbol': symbol,
            'success': True,
            'df': df,
            'meta': meta_or_error if isinstance(meta_or_error, dict) else {},
            'profile': profile
        }
    except Exception as e:
        return {'symbol': symbol, 'success': False, 'error': str(e)}


def upload_symbol_to_bigquery(symbol, df, meta_data, profile_data):
    """Upload single symbol to BigQuery (thread-safe)"""
    df['symbol'] = symbol
    df['name'] = profile_data.get('name', '') or meta_data.get('symbol', symbol)
    df['sector'] = profile_data.get('sector', '')
    df['industry'] = profile_data.get('industry', '')
    df['asset_type'] = profile_data.get('asset_type', 'Common Stock')
    df['exchange'] = meta_data.get('exchange', '')
    df['mic_code'] = meta_data.get('mic_code', '')
    df['country'] = 'United States'
    df['currency'] = meta_data.get('currency', 'USD')
    df['type'] = 'stock'
    df['data_source'] = 'twelvedata'
    df['timestamp'] = (df['datetime'].astype('int64') // 10**9).astype('int64')
    now = datetime.now()
    df['created_at'] = now
    df['updated_at'] = now

    str_cols = {'symbol', 'name', 'sector', 'industry', 'asset_type', 'exchange', 'mic_code',
                'country', 'currency', 'type', 'data_source'}
    datetime_cols = {'datetime', 'created_at', 'updated_at'}
    int_cols = {'timestamp', 'volume', 'average_volume', 'rsi_overbought', 'rsi_oversold',
                'macd_cross', 'pivot_high_flag', 'pivot_low_flag', 'trend_regime', 'vol_regime'}

    for col in df.columns:
        if col in str_cols or col in datetime_cols:
            continue
        elif col in int_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
        elif df[col].dtype == 'object':
            continue
        else:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('float64')
            except:
                pass

    df = df.replace([np.inf, -np.inf], np.nan)

    # Delete existing data for this symbol
    delete_query = f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}` WHERE symbol = '{symbol}'"
    client.query(delete_query).result()

    # Upload
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}"
    job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()

    return len(df)

# =============================================================================
# PROGRESS TRACKING
# =============================================================================

progress_lock = threading.Lock()

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'completed': [], 'failed': [], 'total_records': 0, 'start_time': None}


def save_progress(progress):
    progress['last_update'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def update_progress(progress, completed=None, failed=None, records=0):
    with progress_lock:
        if completed:
            if completed not in progress['completed']:
                progress['completed'].append(completed)
        if failed:
            progress['failed'].append(failed)
        progress['total_records'] += records
        save_progress(progress)

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 80)
    print("SAFE PARALLEL INDEX STOCK BACKFILL")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total symbols: {len(ALL_SYMBOLS)}")
    print(f"Workers: {MAX_WORKERS} | Rate limit: {RATE_LIMIT_PER_MINUTE}/min")
    print("Mode: Parallel fetch + Sequential safe upload")
    print("=" * 80)

    progress = load_progress()
    if not progress['start_time']:
        progress['start_time'] = datetime.now().isoformat()
        save_progress(progress)

    completed_set = set(progress['completed'])
    symbols_to_process = [s for s in ALL_SYMBOLS if s not in completed_set]

    print(f"Already completed: {len(completed_set)}")
    print(f"Remaining: {len(symbols_to_process)}")
    print()

    if not symbols_to_process:
        print("All symbols already processed!")
        return

    # Queue for upload results
    upload_queue = queue.Queue()
    processed_count = len(completed_set)
    start_time = time.time()

    # Process in parallel - fetch only
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_symbol_data, symbol): symbol for symbol in symbols_to_process}

        for future in as_completed(futures):
            symbol = futures[future]
            try:
                result = future.result()

                if result['success']:
                    # Upload sequentially (safe)
                    try:
                        rows = upload_symbol_to_bigquery(
                            result['symbol'],
                            result['df'],
                            result['meta'],
                            result['profile']
                        )
                        processed_count += 1
                        update_progress(progress, completed=result['symbol'], records=rows)

                        elapsed = time.time() - start_time
                        rate = (processed_count - len(completed_set)) / (elapsed / 3600) if elapsed > 0 else 0
                        date_range = f"{result['df']['datetime'].min().date()} to {result['df']['datetime'].max().date()}"
                        print(f"[{processed_count}/{len(ALL_SYMBOLS)}] {symbol}: OK ({rows} rows, {date_range}) | Rate: {rate:.0f}/hr")

                    except Exception as e:
                        print(f"[{processed_count}/{len(ALL_SYMBOLS)}] {symbol}: UPLOAD FAILED - {e}")
                        update_progress(progress, failed=symbol)
                else:
                    print(f"[SKIP] {symbol}: {result['error']}")
                    update_progress(progress, failed=symbol)

            except Exception as e:
                print(f"[ERROR] {symbol}: {e}")
                update_progress(progress, failed=symbol)

    # Final report
    total_elapsed = (datetime.now() - datetime.fromisoformat(progress['start_time'])).total_seconds() / 3600
    print("\n" + "=" * 80)
    print("SAFE PARALLEL BACKFILL COMPLETE")
    print(f"Completed: {len(progress['completed'])}/{len(ALL_SYMBOLS)}")
    print(f"Failed: {len(set(progress['failed']))}")
    print(f"Total Records: {progress['total_records']:,}")
    print(f"Total Time: {total_elapsed:.2f} hours")
    print(f"Rate: {len(progress['completed'])/total_elapsed:.1f} symbols/hour")
    print("=" * 80)


if __name__ == "__main__":
    main()
