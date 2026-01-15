#!/usr/bin/env python3
"""
Index Stock Data Backfill Script
NASDAQ 100 + S&P 500 + Russell 2000 Coverage
Optimized for TwelveData $229 Pro Plan (1,597 credits/minute)

Per masterquery.md:
- Daily data with 24 indicators for ML training
- 5000 days historical data per symbol (~20 years)
- Hourly status reports
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import time
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.cloud import bigquery

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TABLE_NAME = 'stocks_daily_clean'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'
PROGRESS_FILE = 'index_backfill_progress.json'
STATUS_FILE = 'backfill_status.txt'

# Rate limiting - TwelveData $229 Pro = 1,597 credits/minute
# Time series = 1 credit, Profile = 1 credit
# Being conservative: 400 symbols/minute = 6.67 symbols/second
DELAY_BETWEEN_SYMBOLS = 0.15  # 150ms between symbols

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# =============================================================================
# INDEX STOCK LISTS - COMPREHENSIVE COVERAGE
# =============================================================================

# NASDAQ 100 (Full List)
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

# S&P 500 (Complete List)
SP500 = [
    # Technology
    "AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CRM", "ADBE", "AMD", "CSCO", "ACN",
    "IBM", "INTC", "INTU", "TXN", "QCOM", "AMAT", "NOW", "ADI", "LRCX", "MU",
    "KLAC", "SNPS", "CDNS", "MCHP", "FTNT", "ANSS", "KEYS", "MPWR", "TYL", "EPAM",
    "PAYC", "ZBRA", "CTSH", "IT", "BR", "AKAM", "FFIV", "JNPR", "NTAP", "WDC",
    "HPQ", "HPE", "DELL", "STX", "ENPH", "SEDG", "FSLR", "GNRC", "TER", "SWKS",

    # Healthcare
    "UNH", "JNJ", "LLY", "PFE", "ABBV", "MRK", "TMO", "ABT", "DHR", "BMY",
    "AMGN", "GILD", "VRTX", "REGN", "ISRG", "MDT", "SYK", "BSX", "BDX", "EW",
    "ZBH", "DXCM", "IDXX", "IQV", "A", "MTD", "HOLX", "BAX", "ALGN", "TECH",
    "ELV", "CI", "CVS", "HCA", "HUM", "CNC", "MCK", "CAH", "ABC", "VTRS",
    "ZTS", "BIIB", "MRNA", "MOH", "DVA", "LH", "DGX", "HSIC", "XRAY", "COO",

    # Financials
    "JPM", "BAC", "WFC", "GS", "MS", "BLK", "SCHW", "AXP", "C", "USB",
    "PNC", "TFC", "BK", "STT", "COF", "AIG", "MET", "PRU", "ALL", "TRV",
    "CB", "AFL", "PGR", "CME", "ICE", "SPGI", "MCO", "MSCI", "CBOE", "NDAQ",
    "FIS", "FISV", "GPN", "AJG", "AON", "MMC", "WTW", "BRO", "RJF", "HBAN",
    "KEY", "CFG", "RF", "FITB", "MTB", "NTRS", "ZION", "CMA", "FRC", "SBNY",

    # Consumer Discretionary
    "AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "SBUX", "TJX", "BKNG", "CMG",
    "ORLY", "AZO", "ROST", "DHI", "LEN", "PHM", "NVR", "DRI", "YUM", "DG",
    "DLTR", "EBAY", "ETSY", "BBY", "ULTA", "POOL", "GRMN", "LVS", "WYNN", "MGM",
    "CZR", "MAR", "HLT", "H", "EXPE", "CCL", "RCL", "NCLH", "F", "GM",
    "TGT", "COST", "WMT", "KMX", "AN", "LAD", "GPC", "AAP", "APTV", "BWA",

    # Consumer Staples
    "PG", "KO", "PEP", "PM", "MO", "EL", "CL", "KMB", "GIS", "K",
    "HSY", "SJM", "CAG", "CPB", "MKC", "CHD", "CLX", "KR", "SYY", "ADM",
    "TSN", "HRL", "MDLZ", "MNST", "KDP", "STZ", "BF.B", "TAP", "SAM", "WBA",
    "CVS", "COST", "WMT", "TGT", "DG", "DLTR", "KR", "ACI", "SFM", "CASY",

    # Energy
    "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "PXD", "VLO", "PSX", "OXY",
    "HAL", "DVN", "HES", "FANG", "BKR", "KMI", "WMB", "OKE", "TRGP", "LNG",
    "MRO", "APA", "CTRA", "EQT", "AR", "SWN", "RRC", "MTDR", "PR", "CHRD",

    # Industrials
    "CAT", "HON", "UNP", "BA", "RTX", "GE", "DE", "LMT", "UPS", "MMM",
    "NOC", "GD", "ITW", "EMR", "PH", "ETN", "CTAS", "CARR", "FDX", "OTIS",
    "WM", "RSG", "CMI", "JCI", "FAST", "PAYX", "ROK", "SWK", "DOV", "IR",
    "XYL", "IEX", "NDSN", "AME", "ROP", "TT", "TDG", "WAB", "GNRC", "PCAR",
    "ODFL", "JBHT", "CHRW", "EXPD", "CSX", "NSC", "UNP", "CP", "CNI", "KSU",

    # Utilities
    "NEE", "DUK", "SO", "D", "AEP", "SRE", "EXC", "XEL", "WEC", "ED",
    "PEG", "ES", "EIX", "AWK", "DTE", "PPL", "FE", "CMS", "AES", "NI",
    "EVRG", "ATO", "NRG", "VST", "PNW", "OGE", "LNT", "MGEE", "NWE", "AVA",

    # Materials
    "LIN", "APD", "ECL", "SHW", "FCX", "NEM", "NUE", "VMC", "MLM", "DOW",
    "DD", "PPG", "ALB", "CE", "EMN", "IFF", "FMC", "CF", "MOS", "BALL",
    "PKG", "IP", "WRK", "SEE", "AVY", "BMS", "RPM", "ASH", "HUN", "OLN",

    # Real Estate
    "PLD", "AMT", "CCI", "EQIX", "PSA", "SPG", "DLR", "O", "WELL", "AVB",
    "EQR", "VTR", "ARE", "BXP", "SLG", "MAA", "UDR", "ESS", "CPT", "INVH",
    "PEAK", "HST", "KIM", "REG", "FRT", "BRX", "CUBE", "EXR", "IRM", "SBAC",

    # Communication Services
    "GOOGL", "META", "NFLX", "DIS", "CMCSA", "VZ", "T", "TMUS", "CHTR", "EA",
    "TTWO", "ATVI", "WBD", "PARA", "OMC", "IPG", "FOXA", "NWS", "LYV", "MTCH"
]

# Russell 2000 Top Stocks (High Liquidity)
RUSSELL_2000_TOP = [
    # Technology
    "SMTC", "ALGM", "CRUS", "DIOD", "SLAB", "RMBS", "SITM", "POWI", "AMBA", "WOLF",
    "ONTO", "FORM", "NOVT", "NVMI", "VICR", "MKSI", "IPGP", "CGNX", "MIDD", "TDC",
    "MANH", "APPN", "ALRM", "NEWR", "DOMO", "BOX", "PING", "JAMF", "TENB", "SAIL",

    # Healthcare/Biotech
    "EXAS", "NTRA", "IONS", "SRPT", "ARWR", "NBIX", "HALO", "RARE", "ALKS", "PTCT",
    "INCY", "BMRN", "CORT", "SUPN", "PRGO", "PCRX", "LGND", "RCKT", "VERV", "APLS",
    "FOLD", "TGTX", "MIRM", "VCEL", "MNKD", "CTLT", "HZNP", "UTHR", "JAZZ", "SGEN",

    # Financials
    "HBAN", "RF", "KEY", "CFG", "FHN", "ZION", "CMA", "WAL", "FNB", "PNFP",
    "PACW", "EWBC", "BKU", "GBCI", "UMBF", "BOH", "PPBI", "SFBS", "BANR", "HOPE",
    "WSFS", "CADE", "HTLF", "TRMK", "CVBF", "FULT", "FFBC", "WAFD", "CBU", "NBTB",

    # Industrials
    "AIMC", "AGCO", "OSK", "SITE", "GGG", "RBC", "TTC", "GTLS", "ATKR", "ESAB",
    "SPXC", "TKR", "CENT", "LFUS", "ROCK", "KMT", "CW", "MATX", "ARCB", "SAIA",
    "WERN", "HTLD", "SNDR", "XPO", "GXO", "HUBG", "MRTN", "ECHO", "RLGT", "CVLG",

    # Consumer
    "WING", "TXRH", "CAKE", "BJRI", "PLAY", "DINE", "EAT", "BLMN", "DIN", "BOOT",
    "DECK", "SKX", "CROX", "SHOO", "CAL", "GES", "URBN", "ANF", "AEO", "EXPR",
    "CATO", "SCVL", "HIBB", "BGFV", "DKS", "PLCE", "CTRN", "TCS", "LEVI", "PVH",

    # Energy
    "SM", "RRC", "AR", "MTDR", "CTRA", "PDCE", "NOG", "MGY", "VTLE", "CHRD",
    "CIVI", "CPE", "ROCC", "ESTE", "NEXT", "GPOR", "TALO", "BORR", "RIG", "VAL",

    # Materials
    "CLF", "STLD", "CMC", "ATI", "CRS", "CENX", "KALU", "HUN", "OLN", "WLK",
    "TROX", "KWR", "MERC", "HWKN", "NGVT", "HCC", "ARCH", "BTU", "ARLP", "CEIX",

    # REITs
    "CUBE", "EXR", "LSI", "NSA", "REXR", "FR", "STAG", "TRNO", "PLYM", "GTY",
    "NNN", "EPR", "STOR", "SRC", "PINE", "ADC", "FCPT", "NTST", "KREF", "STWD"
]

# Combine all symbols and remove duplicates
ALL_SYMBOLS = list(set(NASDAQ_100 + SP500 + RUSSELL_2000_TOP))
ALL_SYMBOLS.sort()

print(f"Total unique symbols to process: {len(ALL_SYMBOLS)}")

# =============================================================================
# TECHNICAL INDICATORS (Per masterquery.md - 24 indicators)
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
    """Calculate 24+ indicators per masterquery.md specification"""

    # Basic price calculations
    df['previous_close'] = df['close'].shift(1)
    df['change'] = df['close'] - df['previous_close']
    df['percent_change'] = (100 * df['change'] / df['previous_close']).replace([np.inf, -np.inf], np.nan)
    df['high_low'] = df['high'] - df['low']
    df['average_volume'] = df['volume'].rolling(window=20, min_periods=5).mean().fillna(0).astype('int64')
    df['week_52_high'] = df['high'].rolling(window=252, min_periods=50).max()
    df['week_52_low'] = df['low'].rolling(window=252, min_periods=50).min()

    # MOMENTUM INDICATORS (6)
    df['rsi'] = calculate_rsi(df['close'], 14)
    df['macd'], df['macd_signal'], df['macd_histogram'] = calculate_macd(df['close'])
    df['stoch_k'], df['stoch_d'] = calculate_stochastic(df['high'], df['low'], df['close'])
    df['roc'] = (100 * (df['close'] - df['close'].shift(12)) / df['close'].shift(12)).replace([np.inf, -np.inf], np.nan)
    df['momentum'] = df['close'] - df['close'].shift(10)

    # TREND INDICATORS (10)
    df['sma_20'] = calculate_sma(df['close'], 20)
    df['sma_50'] = calculate_sma(df['close'], 50)
    df['sma_200'] = calculate_sma(df['close'], 200)
    df['ema_12'] = calculate_ema(df['close'], 12)
    df['ema_20'] = calculate_ema(df['close'], 20)
    df['ema_26'] = calculate_ema(df['close'], 26)
    df['ema_50'] = calculate_ema(df['close'], 50)
    df['ema_200'] = calculate_ema(df['close'], 200)
    df['ichimoku_tenkan'], df['ichimoku_kijun'] = calculate_ichimoku(df['high'], df['low'], df['close'])

    # VOLATILITY INDICATORS (4)
    df['atr'] = calculate_atr(df['high'], df['low'], df['close'], 14)
    df['bollinger_upper'], df['bollinger_middle'], df['bollinger_lower'] = calculate_bollinger_bands(df['close'])

    # TREND STRENGTH (3)
    df['adx'], df['plus_di'], df['minus_di'] = calculate_adx(df['high'], df['low'], df['close'])

    # VOLUME FLOW (2)
    df['mfi'] = calculate_mfi(df['high'], df['low'], df['close'], df['volume'])
    df['cmf'] = calculate_cmf(df['high'], df['low'], df['close'], df['volume'])

    # Additional indicators to match BigQuery schema
    df['pct_high_low'] = (100 * df['high_low'] / df['low']).replace([np.inf, -np.inf], np.nan)
    df['cci'] = ((df['high'] + df['low'] + df['close']) / 3 - df['close'].rolling(20).mean()) / (0.015 * df['close'].rolling(20).std())
    df['williams_r'] = -100 * (df['high'].rolling(14).max() - df['close']) / (df['high'].rolling(14).max() - df['low'].rolling(14).min())
    df['kama'] = df['close'].ewm(span=10).mean()  # Simplified KAMA
    df['bb_width'] = (df['bollinger_upper'] - df['bollinger_lower']) / df['bollinger_middle'] * 100
    df['trix'] = df['close'].ewm(span=15).mean().ewm(span=15).mean().ewm(span=15).mean().pct_change() * 100
    df['obv'] = (np.sign(df['close'].diff()) * df['volume']).cumsum()
    df['pvo'] = ((df['volume'].ewm(span=12).mean() - df['volume'].ewm(span=26).mean()) / df['volume'].ewm(span=26).mean() * 100)
    df['ppo'] = ((df['ema_12'] - df['ema_26']) / df['ema_26'] * 100)
    df['ultimate_osc'] = 50.0  # Simplified placeholder
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

    # Trend Regime - INTEGER per BigQuery schema (1=uptrend, -1=downtrend, 0=sideways)
    df['trend_regime'] = 0
    df.loc[(df['close'] > df['sma_50']) & (df['sma_50'] > df['sma_200']), 'trend_regime'] = 1
    df.loc[(df['close'] < df['sma_50']) & (df['sma_50'] < df['sma_200']), 'trend_regime'] = -1

    # Vol Regime
    df['vol_regime'] = 0
    df.loc[df['volume_zscore'] > 1, 'vol_regime'] = 1
    df.loc[df['volume_zscore'] < -1, 'vol_regime'] = -1

    df['regime_confidence'] = (df['adx'] / 100).clip(0, 1)

    # Ichimoku extended
    df['ichimoku_senkou_a'] = ((df['ichimoku_tenkan'] + df['ichimoku_kijun']) / 2).shift(26)
    df['ichimoku_senkou_b'] = ((df['high'].rolling(52).max() + df['low'].rolling(52).min()) / 2).shift(26)
    df['ichimoku_chikou'] = df['close'].shift(-26)

    # VWAP and Volume Profile
    df['vwap_daily'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
    df['vwap_weekly'] = df['vwap_daily']  # Simplified
    df['volume_profile_poc'] = df['close'].rolling(20).median()
    df['volume_profile_vah'] = df['high'].rolling(20).quantile(0.7)
    df['volume_profile_val'] = df['low'].rolling(20).quantile(0.3)

    # Replace inf values
    for col in df.columns:
        if df[col].dtype in ['float64', 'float32']:
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)

    return df


# =============================================================================
# API FUNCTIONS
# =============================================================================

def fetch_historical_data(symbol, outputsize=5000):
    """Fetch historical daily data from TwelveData API"""
    url = f"{BASE_URL}/time_series"
    params = {
        'symbol': symbol,
        'interval': '1day',
        'outputsize': outputsize,
        'apikey': TWELVEDATA_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=60)
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
    """Fetch company profile from TwelveData"""
    url = f"{BASE_URL}/profile"
    params = {'symbol': symbol, 'apikey': TWELVEDATA_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=30)
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
# DATA MANAGEMENT
# =============================================================================

def upload_to_bigquery(symbol, df, meta_data, profile_data):
    """Upload data to BigQuery"""

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

    # String columns - exclude from numeric conversion
    str_cols = {'symbol', 'name', 'sector', 'industry', 'asset_type', 'exchange', 'mic_code',
                'country', 'currency', 'type', 'data_source'}

    # Datetime columns
    datetime_cols = {'datetime', 'created_at', 'updated_at'}

    # Integer columns (per BigQuery schema)
    int_cols = {'timestamp', 'volume', 'average_volume', 'rsi_overbought', 'rsi_oversold',
                'macd_cross', 'pivot_high_flag', 'pivot_low_flag', 'trend_regime', 'vol_regime'}

    # Process each column explicitly
    for col in df.columns:
        if col in str_cols or col in datetime_cols:
            continue  # Skip string and datetime columns
        elif col in int_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
        elif df[col].dtype == 'object':
            continue  # Skip any other object/string columns
        else:
            # Convert all other numeric columns to float64
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('float64')
            except:
                pass  # Skip columns that can't be converted

    df = df.replace([np.inf, -np.inf], np.nan)

    # Delete existing data
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

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'completed': [], 'failed': [], 'total_records': 0, 'start_time': None}


def save_progress(progress):
    progress['last_update'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def write_status_report(progress, current_symbol, current_index, total_symbols):
    """Write status report to file"""
    now = datetime.now()
    elapsed = (now - datetime.fromisoformat(progress['start_time'])).total_seconds() / 3600 if progress['start_time'] else 0

    completed = len(progress['completed'])
    rate = completed / elapsed if elapsed > 0 else 0
    remaining = total_symbols - completed - len(progress['failed'])
    eta = remaining / rate if rate > 0 else 0

    report = f"""
================================================================================
BACKFILL STATUS REPORT - {now.strftime('%Y-%m-%d %H:%M:%S')}
================================================================================
Progress: {completed}/{total_symbols} symbols ({completed/total_symbols*100:.1f}%)
Failed: {len(progress['failed'])}
Remaining: {remaining}

Total Records: {progress['total_records']:,}
Elapsed Time: {elapsed:.2f} hours
Rate: {rate:.1f} symbols/hour
ETA: {eta:.1f} hours

Currently Processing: {current_symbol} ({current_index}/{total_symbols})
================================================================================
"""
    print(report)
    with open(STATUS_FILE, 'w') as f:
        f.write(report)


# =============================================================================
# MAIN
# =============================================================================

def process_symbol(symbol, index, total):
    """Process a single symbol"""
    print(f"[{index}/{total}] {symbol}...", end=" ", flush=True)

    df, meta_or_error = fetch_historical_data(symbol, outputsize=5000)

    if df is None:
        print(f"ERROR: {meta_or_error}")
        return False, 0

    time.sleep(DELAY_BETWEEN_SYMBOLS)
    profile = fetch_profile_data(symbol)

    df = calculate_all_indicators(df)
    rows = upload_to_bigquery(symbol, df, meta_or_error if isinstance(meta_or_error, dict) else {}, profile)

    print(f"OK ({rows} rows, {df['datetime'].min().date()} to {df['datetime'].max().date()})")
    return True, rows


def main():
    print("=" * 80)
    print("INDEX STOCK BACKFILL - NASDAQ 100 + S&P 500 + Russell 2000")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total symbols: {len(ALL_SYMBOLS)}")
    print("=" * 80)

    progress = load_progress()
    if not progress['start_time']:
        progress['start_time'] = datetime.now().isoformat()

    completed_set = set(progress['completed'])
    symbols_to_process = [s for s in ALL_SYMBOLS if s not in completed_set]

    print(f"Already completed: {len(completed_set)}")
    print(f"Remaining: {len(symbols_to_process)}")
    print()

    last_report = datetime.now()

    for i, symbol in enumerate(symbols_to_process, 1):
        try:
            success, rows = process_symbol(symbol, len(completed_set) + i, len(ALL_SYMBOLS))

            if success:
                progress['completed'].append(symbol)
                progress['total_records'] += rows
            else:
                progress['failed'].append(symbol)

            save_progress(progress)
            time.sleep(DELAY_BETWEEN_SYMBOLS)

            # Hourly status report
            if (datetime.now() - last_report).total_seconds() >= 3600:
                write_status_report(progress, symbol, len(completed_set) + i, len(ALL_SYMBOLS))
                last_report = datetime.now()

        except Exception as e:
            print(f"EXCEPTION: {e}")
            progress['failed'].append(symbol)
            save_progress(progress)

    # Final report
    print("\n" + "=" * 80)
    print("BACKFILL COMPLETE")
    print(f"Completed: {len(progress['completed'])}/{len(ALL_SYMBOLS)}")
    print(f"Failed: {len(progress['failed'])}")
    print(f"Total Records: {progress['total_records']:,}")
    print("=" * 80)


if __name__ == "__main__":
    main()
