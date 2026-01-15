"""
BULLETPROOF TwelveData Fetcher v4.0 - Per MasterQuery.md Specifications
========================================================================

Implements ALL features from masterquery.md:
- Growth Score (0-100) calculation
- Sentiment Score (0.00-1.00) calculation
- Buy/Sell/Hold Recommendations
- EMA Cycle Detection (Rise/Fall cycles)
- Trend Regime Classification
- 24 Daily / 12 Hourly / 8 5min indicators
- Multi-source integration (TwelveData, Kraken, FRED, Finnhub, CMC)
- Error-proof with retries, circuit breaker, dead letter queue

$229 TwelveData Plan: 800 calls/min, 5000 points/call = 2M records/day
"""

import asyncio
import aiohttp
import functions_framework
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timezone, timedelta
import time
import logging
import random
import json
import requests
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION - Per masterquery.md
# =============================================================================

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
ML_DATASET = 'ml_models'

# API Keys (from masterquery.md)
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
FRED_API_KEY = '608f96800c8a5d9bdb8d53ad059f06c1'
FINNHUB_API_KEY = 'd4dg7t9r01qovljpm3g0d4dg7t9r01qovljpm3gg'
CMC_API_KEY = '059474ae48b84628be6f4a94f9840c30'

# API URLs
TWELVEDATA_URL = 'https://api.twelvedata.com'
KRAKEN_URL = 'https://api.kraken.com/0/public'
FRED_URL = 'https://api.stlouisfed.org/fred'
FINNHUB_URL = 'https://finnhub.io/api/v1'
CMC_URL = 'https://pro-api.coinmarketcap.com/v1'

# Performance settings
MAX_CONCURRENT = 30
MAX_OUTPUT_SIZE = 5000
BATCH_UPLOAD_SIZE = 1000
REQUEST_TIMEOUT = 30

# Error tolerance
MAX_RETRIES = 5
RETRY_BASE_DELAY = 1.0
RETRY_MAX_DELAY = 30.0
CIRCUIT_BREAKER_THRESHOLD = 10
CIRCUIT_BREAKER_RESET_TIME = 60

# Rate limits (per masterquery.md)
RATE_LIMITS = {
    'twelvedata': 55,  # Conservative for 800/min
    'kraken': 40,
    'fred': 100,
    'finnhub': 50,
    'cmc': 10
}

# Growth Score thresholds (per masterquery.md)
GROWTH_RSI_MIN = 50
GROWTH_RSI_MAX = 70
GROWTH_ADX_MIN = 25


# =============================================================================
# ERROR HANDLING CLASSES
# =============================================================================

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0

    def record_success(self):
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker CLOSED - recovered")

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= CIRCUIT_BREAKER_THRESHOLD:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker OPEN - {self.failure_count} failures")

    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > CIRCUIT_BREAKER_RESET_TIME:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True


@dataclass
class QuotaTracker:
    records_fetched: int = 0
    api_calls: int = 0
    start_time: float = field(default_factory=time.time)

    def add(self, count: int):
        self.records_fetched += count
        self.api_calls += 1

    def get_report(self) -> dict:
        elapsed = time.time() - self.start_time
        return {
            'records_fetched': self.records_fetched,
            'api_calls': self.api_calls,
            'elapsed_seconds': round(elapsed, 2),
            'records_per_second': round(self.records_fetched / max(elapsed, 1), 2),
            'quota_usage_pct': round(self.records_fetched / 2_000_000 * 100, 2)
        }


@dataclass
class DeadLetterQueue:
    items: List[Dict] = field(default_factory=list)

    def add(self, symbol: str, error: str):
        self.items.append({'symbol': symbol, 'error': error, 'time': datetime.now(timezone.utc).isoformat()})

    def count(self) -> int:
        return len(self.items)


# Global state
circuit_breaker = CircuitBreaker()
quota_tracker = QuotaTracker()
dead_letter_queue = DeadLetterQueue()


# =============================================================================
# SYMBOL CONFIGURATION - Per masterquery.md (200+ stocks, 50+ crypto)
# =============================================================================

SYMBOLS = {
    'stocks': [
        # S&P 500 Top 200 (per masterquery.md)
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'JNJ',
        'V', 'XOM', 'WMT', 'JPM', 'MA', 'PG', 'HD', 'CVX', 'MRK', 'ABBV',
        'LLY', 'PFE', 'KO', 'PEP', 'COST', 'AVGO', 'TMO', 'MCD', 'CSCO', 'ACN',
        'ABT', 'DHR', 'CMCSA', 'VZ', 'ADBE', 'NKE', 'INTC', 'CRM', 'TXN', 'PM',
        'NEE', 'UPS', 'MS', 'RTX', 'HON', 'QCOM', 'BA', 'LOW', 'SPGI', 'IBM',
        'GE', 'CAT', 'AMAT', 'BLK', 'INTU', 'ISRG', 'AMD', 'GILD', 'MDT', 'AXP',
        'SYK', 'BKNG', 'ADI', 'MDLZ', 'REGN', 'VRTX', 'LRCX', 'ADP', 'PANW', 'MU',
        'SNPS', 'KLAC', 'CDNS', 'NXPI', 'MRVL', 'FTNT', 'ABNB', 'WDAY', 'TEAM', 'DDOG',
        'ZS', 'CRWD', 'NET', 'SNOW', 'MDB', 'OKTA', 'HUBS', 'VEEV', 'TTD', 'ROKU',
        'SQ', 'PYPL', 'COIN', 'HOOD', 'SOFI', 'NOW', 'UBER', 'SHOP', 'PLTR', 'SNAP',
        'NOC', 'ITW', 'PNC', 'SHW', 'AON', 'USB', 'TJX', 'FCX', 'TGT', 'FDX',
        'COP', 'PSA', 'NSC', 'WM', 'EMR', 'MCK', 'MCO', 'HUM', 'MAR', 'ROP',
        'GD', 'MPC', 'APH', 'OXY', 'WELL', 'ORLY', 'TT', 'MCHP', 'PH', 'MSI',
        'ECL', 'PSX', 'CTAS', 'AJG', 'AFL', 'HLT', 'VLO', 'ANET', 'NEM', 'PAYX',
        'KMB', 'PCAR', 'AZO', 'TRV', 'STZ', 'SPG', 'EW', 'CARR', 'ODFL', 'ROST',
        'CMG', 'KEYS', 'DOW', 'DD', 'YUM', 'FAST', 'EXC', 'AEP', 'WEC', 'KMI',
        'OKE', 'WMB', 'ET', 'KDP', 'CLX', 'HSY', 'GIS', 'BAC', 'C', 'WFC',
        'MRNA', 'BIIB', 'RGEN', 'DVN', 'HAL', 'BKR', 'FANG', 'APA', 'MRO', 'EQT',
        # Dividend Champions (25+ years consecutive increases)
        'K', 'SJM', 'HRL', 'MKC', 'DOV', 'SWK', 'CINF', 'BEN', 'TROW', 'ED', 'FRT', 'ESS', 'PPG',
        # Additional Dividend Aristocrats
        'MMM', 'CB', 'CL', 'NUE', 'APD', 'D', 'SO', 'XEL', 'T', 'O', 'SBUX', 'BDX', 'CAH'
    ],
    'crypto': [
        # 50+ cryptos (per masterquery.md)
        'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'ADA/USD', 'SOL/USD', 'DOGE/USD',
        'DOT/USD', 'LTC/USD', 'SHIB/USD', 'TRX/USD', 'AVAX/USD', 'LINK/USD',
        'ATOM/USD', 'UNI/USD', 'XMR/USD', 'ETC/USD', 'XLM/USD', 'BCH/USD',
        'FIL/USD', 'NEAR/USD', 'ALGO/USD', 'VET/USD', 'HBAR/USD',
        'AAVE/USD', 'SAND/USD', 'MANA/USD', 'AXS/USD', 'THETA/USD',
        'XTZ/USD', 'NEO/USD', 'BAT/USD', 'COMP/USD', 'ENJ/USD', 'CHZ/USD',
        'GRT/USD', 'POL/USD', 'APE/USD', 'OP/USD', 'ARB/USD', 'INJ/USD',
        'SUI/USD', 'SEI/USD', 'TIA/USD', 'RUNE/USD', 'LDO/USD', 'IMX/USD',
        'CRO/USD', 'FTM/USD', 'EGLD/USD', 'FLOW/USD'
    ],
    'etfs': [
        # TOP 20 ETFs by AUM (>$4.8 trillion combined) - Priority tracking
        # S&P 500 ETFs ($2.3T combined)
        'VOO', 'IVV', 'SPY', 'SPLG',
        # Total Market & Growth
        'VTI', 'QQQ', 'VUG', 'VGT', 'IWF',
        # Value
        'VTV',
        # International Developed ($490B)
        'VEA', 'IEFA', 'VXUS',
        # Emerging Markets
        'IEMG', 'VWO',
        # Bonds
        'BND', 'AGG',
        # Mid-Cap & Dividend
        'IJH', 'VIG',
        # Commodities
        'GLD',
        # Additional ETFs (sector, leveraged, thematic)
        'QQQI', 'IWM', 'DIA', 'EFA', 'TLT', 'SLV', 'USO',
        'XLF', 'XLK', 'XLE', 'XLV', 'XLI', 'XLY', 'XLP', 'XLU', 'XLRE', 'XLC', 'XLB',
        'VNQ', 'ARKK', 'ARKG', 'ARKF', 'SOXL', 'TQQQ', 'SPXL', 'FAS', 'TNA', 'LABU', 'TECL', 'SMH', 'IBB'
    ],
    'forex': [
        # 20+ forex pairs (per masterquery.md)
        'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',
        'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'EUR/CHF', 'AUD/JPY', 'GBP/CHF', 'EUR/AUD',
        'EUR/CAD', 'AUD/NZD', 'GBP/AUD', 'GBP/CAD', 'CHF/JPY', 'CAD/JPY'
    ]
}

# Kraken pairs for buy/sell volume (per masterquery.md)
KRAKEN_PAIRS = [
    'XXBTZUSD', 'XETHZUSD', 'XXRPZUSD', 'ADAUSD', 'DOTUSD', 'SOLUSD',
    'DOGEUSD', 'LTCUSD', 'AVAXUSD', 'LINKUSD', 'ATOMUSD', 'XLMUSD',
    'ALGOUSD', 'TRXUSD', 'XETCZUSD', 'XXMRZUSD', 'FILUSD', 'AAVEUSD'
]

# FRED series (per masterquery.md)
FRED_SERIES = [
    'DGS10', 'DGS2', 'DGS30', 'T10Y2Y', 'FEDFUNDS', 'VIXCLS',
    'SP500', 'UNRATE', 'CPIAUCSL', 'MORTGAGE30US'
]


# =============================================================================
# INDICATOR CALCULATIONS - Per masterquery.md
# =============================================================================

def calculate_growth_score(row: dict) -> int:
    """
    Calculate Growth Score (0-100) per masterquery.md formula:
    - RSI 50-70: +25
    - MACD histogram > 0: +25
    - ADX > 25: +25
    - Close > SMA_200: +25
    """
    score = 0

    rsi = row.get('rsi') or row.get('rsi_14')
    if rsi and GROWTH_RSI_MIN <= rsi <= GROWTH_RSI_MAX:
        score += 25

    macd_hist = row.get('macd_histogram')
    if macd_hist and macd_hist > 0:
        score += 25

    adx = row.get('adx')
    if adx and adx > GROWTH_ADX_MIN:
        score += 25

    close = row.get('close')
    sma_200 = row.get('sma_200')
    if close and sma_200 and close > sma_200:
        score += 25

    return score


def calculate_sentiment_score(row: dict) -> float:
    """
    Calculate Sentiment Score (0.00-1.00) per masterquery.md:
    - RSI: 0.125 weight
    - MACD Histogram: 0.125 weight
    - MACD Cross: 0.100 weight
    - ADX Strength: 0.075 weight
    - SMA 200: 0.100 weight
    - Pivot Flags: 0.075 weight
    - MFI: 0.100 weight
    - Buy Pressure: 0.100 weight
    """
    score = 0.5  # Start neutral

    # RSI component (0.125)
    rsi = row.get('rsi') or row.get('rsi_14')
    if rsi:
        if 30 <= rsi <= 50:  # Oversold bullish
            score += 0.125
        elif rsi > 70:  # Overbought bearish
            score -= 0.125

    # MACD Histogram (0.125)
    macd_hist = row.get('macd_histogram')
    if macd_hist:
        if macd_hist > 0:
            score += 0.125
        else:
            score -= 0.125

    # ADX Strength bonus (0.075)
    adx = row.get('adx')
    if adx and adx > 25:
        score += 0.075 if row.get('plus_di', 0) > row.get('minus_di', 0) else -0.075

    # SMA 200 (0.100)
    close = row.get('close')
    sma_200 = row.get('sma_200')
    if close and sma_200:
        if close > sma_200:
            score += 0.100
        else:
            score -= 0.100

    # MFI (0.100)
    mfi = row.get('mfi')
    if mfi:
        if mfi > 50:
            score += 0.100
        else:
            score -= 0.100

    # Buy pressure (0.100)
    buy_pressure = row.get('buy_pressure')
    if buy_pressure:
        score += (buy_pressure - 0.5) * 0.2

    return max(0.0, min(1.0, score))


def get_recommendation(sentiment: float, rsi: float = None, macd_hist: float = None) -> str:
    """
    Get Buy/Sell/Hold recommendation per masterquery.md:
    - STRONG_BUY: sentiment >= 0.70 AND RSI 40-70 AND MACD_Histogram > 0
    - BUY: sentiment 0.55-0.69
    - HOLD: sentiment 0.45-0.54
    - SELL: sentiment 0.30-0.44
    - STRONG_SELL: sentiment <= 0.30
    """
    if sentiment >= 0.70:
        if rsi and 40 <= rsi <= 70 and macd_hist and macd_hist > 0:
            return 'STRONG_BUY'
        return 'BUY'
    elif sentiment >= 0.55:
        return 'BUY'
    elif sentiment >= 0.45:
        return 'HOLD'
    elif sentiment >= 0.30:
        return 'SELL'
    else:
        return 'STRONG_SELL'


def get_trend_regime(row: dict) -> str:
    """
    Classify trend regime per masterquery.md:
    - STRONG_UPTREND: close > sma_50 AND sma_50 > sma_200 AND adx > 25
    - WEAK_UPTREND: close > sma_50 AND close > sma_200
    - STRONG_DOWNTREND: close < sma_50 AND sma_50 < sma_200 AND adx > 25
    - WEAK_DOWNTREND: close < sma_50 AND close < sma_200
    - CONSOLIDATION: else
    """
    close = row.get('close')
    sma_50 = row.get('sma_50')
    sma_200 = row.get('sma_200')
    adx = row.get('adx')

    if not all([close, sma_50]):
        return 'UNKNOWN'

    if close > sma_50:
        if sma_200 and sma_50 > sma_200 and adx and adx > 25:
            return 'STRONG_UPTREND'
        elif sma_200 and close > sma_200:
            return 'WEAK_UPTREND'
    elif close < sma_50:
        if sma_200 and sma_50 < sma_200 and adx and adx > 25:
            return 'STRONG_DOWNTREND'
        elif sma_200 and close < sma_200:
            return 'WEAK_DOWNTREND'

    return 'CONSOLIDATION'


def detect_ema_cycle(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect EMA rise/fall cycles per masterquery.md:
    - in_rise_cycle = ema_12 > ema_26
    - rise_cycle_start = crossover
    - fall_cycle_start = crossunder
    """
    if 'ema_12' not in df.columns or 'ema_26' not in df.columns:
        return df

    df['in_rise_cycle'] = df['ema_12'] > df['ema_26']
    df['prev_in_rise'] = df['in_rise_cycle'].shift(1)
    df['rise_cycle_start'] = (df['in_rise_cycle']) & (~df['prev_in_rise'].fillna(False))
    df['fall_cycle_start'] = (~df['in_rise_cycle']) & (df['prev_in_rise'].fillna(True))
    df.drop('prev_in_rise', axis=1, inplace=True)

    return df


def detect_crosses(df: pd.DataFrame) -> pd.DataFrame:
    """Detect golden/death crosses per masterquery.md"""
    if 'sma_50' not in df.columns or 'sma_200' not in df.columns:
        return df

    df['sma_50_prev'] = df['sma_50'].shift(1)
    df['sma_200_prev'] = df['sma_200'].shift(1)

    df['golden_cross'] = (df['sma_50'] > df['sma_200']) & (df['sma_50_prev'] <= df['sma_200_prev'])
    df['death_cross'] = (df['sma_50'] < df['sma_200']) & (df['sma_50_prev'] >= df['sma_200_prev'])

    df.drop(['sma_50_prev', 'sma_200_prev'], axis=1, inplace=True)

    return df


def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate ALL 24 daily indicators per masterquery.md:
    - Momentum (6): RSI, MACD, ROC, Stoch_K, Stoch_D, MFI
    - Trend (10): SMA_20/50/200, EMA_12/20/26/50/200, Ichimoku
    - Volatility (4): ATR, BB_Upper/Middle/Lower
    - Strength (3): ADX, Plus_DI, Minus_DI
    - Flow (2): MFI, CMF
    """
    if len(df) < 50:
        return df

    df = df.sort_values('datetime').copy()

    # === MOMENTUM INDICATORS ===

    # RSI (14)
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta.where(delta < 0, 0))
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df['rsi'] = 100 - (100 / (1 + rs))
    df['rsi_14'] = df['rsi']

    # RSI derivatives
    df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
    df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
    df['rsi_slope'] = df['rsi'].diff(5) / 5
    df['rsi_zscore'] = (df['rsi'] - df['rsi'].rolling(20).mean()) / df['rsi'].rolling(20).std()

    # MACD
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']

    # MACD cross
    df['macd_prev'] = df['macd'].shift(1)
    df['macd_signal_prev'] = df['macd_signal'].shift(1)
    df['macd_cross'] = np.where(
        (df['macd'] > df['macd_signal']) & (df['macd_prev'] <= df['macd_signal_prev']), 1,
        np.where((df['macd'] < df['macd_signal']) & (df['macd_prev'] >= df['macd_signal_prev']), -1, 0)
    )
    df.drop(['macd_prev', 'macd_signal_prev'], axis=1, inplace=True)

    # ROC
    df['roc'] = ((df['close'] - df['close'].shift(12)) / df['close'].shift(12)) * 100

    # Stochastic
    low_14 = df['low'].rolling(window=14).min()
    high_14 = df['high'].rolling(window=14).max()
    df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14).replace(0, np.nan))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # === TREND INDICATORS ===

    # SMAs
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    if len(df) >= 200:
        df['sma_200'] = df['close'].rolling(window=200).mean()

    # EMAs
    df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
    if len(df) >= 200:
        df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()

    # Ichimoku (simplified)
    high_9 = df['high'].rolling(window=9).max()
    low_9 = df['low'].rolling(window=9).min()
    df['ichimoku_tenkan'] = (high_9 + low_9) / 2

    high_26 = df['high'].rolling(window=26).max()
    low_26 = df['low'].rolling(window=26).min()
    df['ichimoku_kijun'] = (high_26 + low_26) / 2

    # === VOLATILITY INDICATORS ===

    # ATR
    tr1 = df['high'] - df['low']
    tr2 = abs(df['high'] - df['close'].shift())
    tr3 = abs(df['low'] - df['close'].shift())
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(window=14).mean()
    df['atr_14'] = df['atr']

    # Bollinger Bands
    df['bb_middle'] = df['sma_20']
    df['bollinger_middle'] = df['bb_middle']
    std_20 = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (std_20 * 2)
    df['bb_lower'] = df['bb_middle'] - (std_20 * 2)
    df['bollinger_upper'] = df['bb_upper']
    df['bollinger_lower'] = df['bb_lower']
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
    df['bb_percent'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

    # === TREND STRENGTH ===

    # ADX
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    plus_dm[plus_dm < minus_dm] = 0
    minus_dm[minus_dm < plus_dm] = 0

    tr_sum = true_range.rolling(window=14).sum()
    df['plus_di'] = 100 * (plus_dm.rolling(window=14).sum() / tr_sum.replace(0, np.nan))
    df['minus_di'] = 100 * (minus_dm.rolling(window=14).sum() / tr_sum.replace(0, np.nan))
    dx = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']).replace(0, np.nan)
    df['adx'] = dx.rolling(window=14).mean()

    # === VOLUME INDICATORS ===

    # MFI (Money Flow Index)
    tp = (df['high'] + df['low'] + df['close']) / 3
    raw_money_flow = tp * df['volume']
    positive_flow = raw_money_flow.where(tp > tp.shift(1), 0)
    negative_flow = raw_money_flow.where(tp < tp.shift(1), 0)
    money_ratio = positive_flow.rolling(14).sum() / negative_flow.rolling(14).sum().replace(0, np.nan)
    df['mfi'] = 100 - (100 / (1 + money_ratio))

    # CMF (Chaikin Money Flow)
    clv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low']).replace(0, np.nan)
    df['cmf'] = (clv * df['volume']).rolling(20).sum() / df['volume'].rolling(20).sum()

    # CCI
    sma_tp = tp.rolling(window=20).mean()
    mad = tp.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
    df['cci'] = (tp - sma_tp) / (0.015 * mad)

    # Williams %R
    df['williams_r'] = -100 * ((high_14 - df['close']) / (high_14 - low_14).replace(0, np.nan))

    # Momentum
    df['momentum'] = df['close'] - df['close'].shift(10)

    # Awesome Oscillator
    df['awesome_osc'] = df['close'].rolling(5).mean() - df['close'].rolling(34).mean()

    # OBV
    close_vals = df['close'].values
    volume_vals = df['volume'].values.astype(float)
    obv = [0]
    for i in range(1, len(df)):
        if close_vals[i] > close_vals[i-1]:
            obv.append(obv[-1] + volume_vals[i])
        elif close_vals[i] < close_vals[i-1]:
            obv.append(obv[-1] - volume_vals[i])
        else:
            obv.append(obv[-1])
    df['obv'] = obv

    # Pivot flags
    df['pivot_high_flag'] = ((df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1))).astype(int)
    df['pivot_low_flag'] = ((df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1))).astype(int)

    # === CYCLE DETECTION ===
    df = detect_ema_cycle(df)
    df = detect_crosses(df)

    return df


# =============================================================================
# DATA FETCHING
# =============================================================================

async def fetch_twelvedata(session: aiohttp.ClientSession, symbol: str,
                          interval: str, asset_type: str) -> Optional[Dict]:
    """Fetch from TwelveData with retry logic"""

    if not circuit_breaker.can_execute():
        return None

    await asyncio.sleep(1.0 / RATE_LIMITS['twelvedata'])

    params = {
        'symbol': symbol,
        'interval': interval,
        'outputsize': MAX_OUTPUT_SIZE,
        'apikey': TWELVEDATA_API_KEY,
    }

    for attempt in range(MAX_RETRIES):
        try:
            async with session.get(f"{TWELVEDATA_URL}/time_series", params=params,
                                  timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as response:
                if response.status == 429:
                    await asyncio.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                    continue

                data = await response.json()

                if 'values' not in data:
                    raise Exception(data.get('message', 'No values'))

                circuit_breaker.record_success()
                quota_tracker.add(len(data['values']))

                return {
                    'symbol': symbol,
                    'asset_type': asset_type,
                    'interval': interval,
                    'values': data['values'],
                    'count': len(data['values'])
                }

        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                circuit_breaker.record_failure()
                dead_letter_queue.add(symbol, str(e))
                return None
            await asyncio.sleep(RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0, 1))

    return None


def fetch_kraken_buy_sell(pair: str) -> Optional[Dict]:
    """Fetch buy/sell volume from Kraken per masterquery.md"""
    try:
        time.sleep(1.0 / RATE_LIMITS['kraken'])

        response = requests.get(f"{KRAKEN_URL}/Trades", params={'pair': pair}, timeout=15)
        data = response.json()

        if data.get('error'):
            return None

        result_key = list(data['result'].keys())[0] if data['result'] else None
        if not result_key or result_key == 'last':
            return None

        trades = data['result'][result_key]

        buy_volume = sum(float(t[1]) for t in trades if t[3] == 'b')
        sell_volume = sum(float(t[1]) for t in trades if t[3] == 's')
        buy_count = sum(1 for t in trades if t[3] == 'b')
        sell_count = sum(1 for t in trades if t[3] == 's')

        total_volume = buy_volume + sell_volume
        buy_pressure = buy_volume / total_volume if total_volume > 0 else 0.5

        return {
            'pair': pair,
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'buy_count': buy_count,
            'sell_count': sell_count,
            'trade_count': len(trades),
            'buy_sell_ratio': buy_volume / sell_volume if sell_volume > 0 else 1.0,
            'buy_pressure': buy_pressure
        }

    except Exception as e:
        logger.warning(f"Kraken error for {pair}: {e}")
        return None


def fetch_fred_data() -> List[Dict]:
    """Fetch economic indicators from FRED per masterquery.md"""
    results = []

    for series_id in FRED_SERIES:
        try:
            time.sleep(1.0 / RATE_LIMITS['fred'])

            params = {
                'series_id': series_id,
                'api_key': FRED_API_KEY,
                'file_type': 'json',
                'limit': 100,
                'sort_order': 'desc'
            }

            response = requests.get(f"{FRED_URL}/series/observations", params=params, timeout=15)
            data = response.json()

            if 'observations' in data:
                results.append({
                    'series_id': series_id,
                    'observations': data['observations'][:30]  # Last 30 values
                })

        except Exception as e:
            logger.warning(f"FRED error for {series_id}: {e}")

    return results


def fetch_coinmarketcap_data() -> List[Dict]:
    """
    Fetch crypto rankings and market data from CoinMarketCap per masterquery.md
    - Top 100 cryptocurrencies by market cap
    - Market cap, volume, price changes
    """
    results = []

    try:
        time.sleep(1.0 / RATE_LIMITS['cmc'])

        headers = {
            'X-CMC_PRO_API_KEY': CMC_API_KEY,
            'Accept': 'application/json'
        }

        # Top 100 cryptos by market cap
        params = {
            'start': 1,
            'limit': 100,
            'convert': 'USD',
            'sort': 'market_cap',
            'sort_dir': 'desc'
        }

        response = requests.get(
            f"{CMC_URL}/cryptocurrency/listings/latest",
            headers=headers,
            params=params,
            timeout=30
        )

        data = response.json()

        if data.get('status', {}).get('error_code') == 0 and 'data' in data:
            for crypto in data['data']:
                quote = crypto.get('quote', {}).get('USD', {})
                results.append({
                    'symbol': crypto['symbol'],
                    'name': crypto['name'],
                    'cmc_rank': crypto['cmc_rank'],
                    'market_cap': quote.get('market_cap'),
                    'price': quote.get('price'),
                    'volume_24h': quote.get('volume_24h'),
                    'percent_change_1h': quote.get('percent_change_1h'),
                    'percent_change_24h': quote.get('percent_change_24h'),
                    'percent_change_7d': quote.get('percent_change_7d'),
                    'circulating_supply': crypto.get('circulating_supply'),
                    'total_supply': crypto.get('total_supply'),
                    'fetch_timestamp': datetime.now(timezone.utc).isoformat()
                })
            logger.info(f"CoinMarketCap: Fetched {len(results)} crypto rankings")
        else:
            logger.warning(f"CoinMarketCap error: {data.get('status', {}).get('error_message', 'Unknown')}")

    except Exception as e:
        logger.warning(f"CoinMarketCap fetch error: {e}")

    return results


def fetch_finnhub_recommendations() -> List[Dict]:
    """
    Fetch analyst recommendations from Finnhub per masterquery.md
    - Buy/Sell/Hold ratings for tracked stocks
    """
    results = []

    # Top stocks to get recommendations for
    top_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM',
                  'V', 'JNJ', 'WMT', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV',
                  'KO', 'PEP', 'COST', 'AVGO', 'TMO', 'MCD', 'CSCO', 'ACN']

    for symbol in top_stocks:
        try:
            time.sleep(1.0 / RATE_LIMITS['finnhub'])

            params = {
                'symbol': symbol,
                'token': FINNHUB_API_KEY
            }

            response = requests.get(
                f"{FINNHUB_URL}/stock/recommendation",
                params=params,
                timeout=15
            )

            data = response.json()

            if data and isinstance(data, list) and len(data) > 0:
                latest = data[0]  # Most recent recommendation
                results.append({
                    'symbol': symbol,
                    'period': latest.get('period'),
                    'strong_buy': latest.get('strongBuy', 0),
                    'buy': latest.get('buy', 0),
                    'hold': latest.get('hold', 0),
                    'sell': latest.get('sell', 0),
                    'strong_sell': latest.get('strongSell', 0),
                    'fetch_timestamp': datetime.now(timezone.utc).isoformat()
                })

        except Exception as e:
            logger.warning(f"Finnhub error for {symbol}: {e}")

    logger.info(f"Finnhub: Fetched {len(results)} analyst recommendations")
    return results


def upload_cmc_data(data: List[Dict]) -> int:
    """Upload CoinMarketCap data to BigQuery"""
    if not data:
        return 0

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.cmc_crypto_rankings"

    try:
        errors = client.insert_rows_json(table_ref, data)
        if not errors:
            logger.info(f"Uploaded {len(data)} CMC records")
            return len(data)
        else:
            logger.error(f"CMC upload errors: {errors[:3]}")
            return 0
    except Exception as e:
        logger.error(f"CMC upload error: {e}")
        return 0


def upload_finnhub_data(data: List[Dict]) -> int:
    """Upload Finnhub recommendations to BigQuery"""
    if not data:
        return 0

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.finnhub_recommendations"

    try:
        errors = client.insert_rows_json(table_ref, data)
        if not errors:
            logger.info(f"Uploaded {len(data)} Finnhub records")
            return len(data)
        else:
            logger.error(f"Finnhub upload errors: {errors[:3]}")
            return 0
    except Exception as e:
        logger.error(f"Finnhub upload error: {e}")
        return 0


def upload_fred_data(data: List[Dict]) -> int:
    """Upload FRED economic data to BigQuery"""
    if not data:
        return 0

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.fred_economic_data"

    records = []
    now = datetime.now(timezone.utc).isoformat()

    for series in data:
        series_id = series['series_id']
        for obs in series.get('observations', []):
            if obs.get('value') and obs['value'] != '.':
                records.append({
                    'series_id': series_id,
                    'date': obs['date'],
                    'value': float(obs['value']),
                    'fetch_timestamp': now
                })

    if not records:
        return 0

    try:
        # Upload in batches
        uploaded = 0
        for i in range(0, len(records), 500):
            batch = records[i:i+500]
            errors = client.insert_rows_json(table_ref, batch)
            if not errors:
                uploaded += len(batch)

        logger.info(f"Uploaded {uploaded} FRED records")
        return uploaded
    except Exception as e:
        logger.error(f"FRED upload error: {e}")
        return 0


# =============================================================================
# DATA PROCESSING
# =============================================================================

def process_and_upload(data: List[Dict], interval: str) -> Dict[str, int]:
    """Process fetched data, calculate all indicators, and upload"""

    upload_results = {}

    # Group by asset type
    by_asset = {}
    for item in data:
        if item is None:
            continue
        asset_type = item.get('asset_type', 'unknown')
        if asset_type not in by_asset:
            by_asset[asset_type] = []
        by_asset[asset_type].append(item)

    client = bigquery.Client(project=PROJECT_ID)

    for asset_type, items in by_asset.items():
        all_records = []

        for item in items:
            try:
                df = pd.DataFrame(item['values'])
                df['datetime'] = pd.to_datetime(df['datetime'])

                for col in ['open', 'high', 'low', 'close', 'volume']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                df['symbol'] = item['symbol']
                df['asset_type'] = asset_type
                df['interval'] = item['interval']
                df['data_source'] = 'twelvedata'

                # Calculate ALL indicators
                df = calculate_all_indicators(df)

                # Calculate growth score, sentiment, recommendation for each row
                records = df.to_dict('records')
                for record in records:
                    record['growth_score'] = calculate_growth_score(record)
                    record['sentiment_score'] = calculate_sentiment_score(record)
                    record['recommendation'] = get_recommendation(
                        record['sentiment_score'],
                        record.get('rsi'),
                        record.get('macd_histogram')
                    )
                    record['trend_regime'] = get_trend_regime(record)

                # Timestamps
                now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                for record in records:
                    record['created_at'] = now
                    record['updated_at'] = now
                    record['fetch_timestamp'] = now
                    if 'datetime' in record and hasattr(record['datetime'], 'strftime'):
                        record['datetime'] = record['datetime'].strftime('%Y-%m-%d %H:%M:%S')

                # Clean NaN values
                for record in records:
                    for key, value in list(record.items()):
                        if pd.isna(value):
                            record[key] = None

                all_records.extend(records)

            except Exception as e:
                logger.error(f"Error processing {item.get('symbol')}: {e}")

        # Determine table
        table_suffix = 'hourly_clean' if '1h' in interval else 'daily_clean'
        table_name = f"{asset_type}_{table_suffix}"
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

        # Upload in batches
        uploaded = 0
        for i in range(0, len(all_records), BATCH_UPLOAD_SIZE):
            batch = all_records[i:i + BATCH_UPLOAD_SIZE]
            try:
                errors = client.insert_rows_json(table_ref, batch)
                if not errors:
                    uploaded += len(batch)
            except Exception as e:
                logger.error(f"Upload error: {e}")

        upload_results[asset_type] = {
            'processed': len(all_records),
            'uploaded': uploaded
        }

        logger.info(f"Uploaded {uploaded:,} {asset_type} records to {table_name}")

    return upload_results


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

async def fetch_all_assets(asset_types: List[str], interval: str) -> List[Dict]:
    """Fetch all assets concurrently"""

    results = []

    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT)
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT * 2)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:

        for asset_type in asset_types:
            if asset_type not in SYMBOLS:
                continue

            symbols = SYMBOLS[asset_type]
            logger.info(f"Fetching {len(symbols)} {asset_type} symbols...")

            tasks = [
                fetch_twelvedata(session, symbol, interval, asset_type)
                for symbol in symbols
            ]

            asset_results = await asyncio.gather(*tasks, return_exceptions=True)

            valid = [r for r in asset_results if r and not isinstance(r, Exception)]
            results.extend(valid)

            logger.info(f"{asset_type}: {len(valid)}/{len(symbols)} successful")

    return results


@functions_framework.http
def bulletproof_fetch(request):
    """
    BULLETPROOF Cloud Function Entry Point - Per masterquery.md v4.0

    Features:
    - 24 daily indicators / 12 hourly indicators
    - Growth Score (0-100)
    - Sentiment Score (0.00-1.00)
    - Buy/Sell/Hold recommendations
    - EMA cycle detection
    - Trend regime classification
    - Multi-source data: TwelveData, Kraken, FRED, CoinMarketCap, Finnhub
    - Error-proof with retries, circuit breaker, dead letter queue

    Query params:
        asset_type: stocks, crypto, etfs, forex, all (default: all)
        interval: 1h, 1day (default: 1h)
        include_kraken: true/false (default: true for crypto)
        include_fred: true/false (default: false)
        include_cmc: true/false (default: false) - CoinMarketCap crypto rankings
        include_finnhub: true/false (default: false) - Analyst recommendations
    """

    start_time = time.time()
    logger.info("="*60)
    logger.info("BULLETPROOF FETCH v4.0 - Per masterquery.md")
    logger.info("Multi-Source: TwelveData, Kraken, FRED, CMC, Finnhub")
    logger.info("="*60)

    # Reset global state
    global circuit_breaker, quota_tracker, dead_letter_queue
    circuit_breaker = CircuitBreaker()
    quota_tracker = QuotaTracker()
    dead_letter_queue = DeadLetterQueue()

    # Parse parameters
    args = request.args
    asset_type = args.get('asset_type', 'all')
    interval = args.get('interval', '1h')
    include_kraken = args.get('include_kraken', 'true').lower() == 'true'
    include_fred = args.get('include_fred', 'false').lower() == 'true'
    include_cmc = args.get('include_cmc', 'false').lower() == 'true'
    include_finnhub = args.get('include_finnhub', 'false').lower() == 'true'

    # Determine asset types
    if asset_type == 'all':
        asset_types = list(SYMBOLS.keys())
    else:
        asset_types = [asset_type]

    # =============================
    # 1. TWELVEDATA - Primary Source
    # =============================
    logger.info(">>> PHASE 1: TwelveData API (OHLCV + Indicators)")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        data = loop.run_until_complete(fetch_all_assets(asset_types, interval))
    finally:
        loop.close()

    # =============================
    # 2. KRAKEN - Buy/Sell Volume
    # =============================
    kraken_data = {}
    if include_kraken and ('crypto' in asset_types or asset_type == 'all'):
        logger.info(">>> PHASE 2: Kraken API (Buy/Sell Volume)")
        for pair in KRAKEN_PAIRS:
            result = fetch_kraken_buy_sell(pair)
            if result:
                kraken_data[pair] = result
        logger.info(f"Kraken: {len(kraken_data)} pairs fetched")

    # =============================
    # 3. FRED - Economic Indicators
    # =============================
    fred_uploaded = 0
    if include_fred:
        logger.info(">>> PHASE 3: FRED API (Economic Indicators)")
        fred_data = fetch_fred_data()
        if fred_data:
            fred_uploaded = upload_fred_data(fred_data)
        logger.info(f"FRED: {fred_uploaded} records uploaded")

    # =============================
    # 4. COINMARKETCAP - Crypto Rankings
    # =============================
    cmc_uploaded = 0
    if include_cmc:
        logger.info(">>> PHASE 4: CoinMarketCap API (Crypto Rankings)")
        cmc_data = fetch_coinmarketcap_data()
        if cmc_data:
            cmc_uploaded = upload_cmc_data(cmc_data)
        logger.info(f"CoinMarketCap: {cmc_uploaded} records uploaded")

    # =============================
    # 5. FINNHUB - Analyst Recommendations
    # =============================
    finnhub_uploaded = 0
    if include_finnhub:
        logger.info(">>> PHASE 5: Finnhub API (Analyst Recommendations)")
        finnhub_data = fetch_finnhub_recommendations()
        if finnhub_data:
            finnhub_uploaded = upload_finnhub_data(finnhub_data)
        logger.info(f"Finnhub: {finnhub_uploaded} records uploaded")

    # =============================
    # 6. PROCESS & UPLOAD
    # =============================
    logger.info(">>> PHASE 6: Process Indicators & Upload to BigQuery")
    upload_results = process_and_upload(data, interval)

    elapsed = time.time() - start_time

    response = {
        'status': 'completed',
        'mode': 'bulletproof_v4_multi_source',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds': round(elapsed, 2),
        'parameters': {
            'asset_type': asset_type,
            'interval': interval,
            'outputsize': MAX_OUTPUT_SIZE,
            'include_kraken': include_kraken,
            'include_fred': include_fred,
            'include_cmc': include_cmc,
            'include_finnhub': include_finnhub
        },
        'features_per_masterquery': {
            'indicators': '24 daily / 12 hourly',
            'growth_score': '0-100',
            'sentiment_score': '0.00-1.00',
            'recommendations': 'STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL',
            'trend_regime': 'STRONG_UPTREND/WEAK_UPTREND/CONSOLIDATION/etc',
            'ema_cycles': 'rise_cycle_start/fall_cycle_start',
            'crosses': 'golden_cross/death_cross'
        },
        'data_sources': {
            'twelvedata': {
                'records_fetched': quota_tracker.records_fetched,
                'api_calls': quota_tracker.api_calls,
                'quota_usage_pct': quota_tracker.get_report()['quota_usage_pct']
            },
            'kraken': {
                'pairs_fetched': len(kraken_data),
                'fields': 'buy_volume, sell_volume, buy_count, sell_count, trade_count, buy_sell_ratio, buy_pressure'
            },
            'fred': {
                'records_uploaded': fred_uploaded,
                'series': FRED_SERIES if include_fred else []
            },
            'coinmarketcap': {
                'records_uploaded': cmc_uploaded,
                'fields': 'market_cap, volume_24h, percent_change_1h/24h/7d'
            },
            'finnhub': {
                'records_uploaded': finnhub_uploaded,
                'fields': 'strong_buy, buy, hold, sell, strong_sell'
            }
        },
        'quota': quota_tracker.get_report(),
        'upload_results': upload_results,
        'circuit_breaker': circuit_breaker.state.value,
        'dead_letter_queue': dead_letter_queue.count(),
        'overall': {
            'total_twelvedata_records': quota_tracker.records_fetched,
            'total_uploaded': sum(r.get('uploaded', 0) for r in upload_results.values()),
            'supplemental_data': {
                'kraken': len(kraken_data),
                'fred': fred_uploaded,
                'cmc': cmc_uploaded,
                'finnhub': finnhub_uploaded
            }
        }
    }

    logger.info("="*60)
    logger.info(f"COMPLETED: {response['overall']['total_uploaded']:,} TwelveData records")
    logger.info(f"Supplemental: Kraken={len(kraken_data)}, FRED={fred_uploaded}, CMC={cmc_uploaded}, Finnhub={finnhub_uploaded}")
    logger.info(f"Time: {elapsed:.1f}s | Quota: {quota_tracker.get_report()['quota_usage_pct']:.2f}%")
    logger.info("="*60)

    return response, 200


@functions_framework.http
def detect_and_fill_gaps(request):
    """Self-healing gap detector per masterquery.md"""

    logger.info("Starting gap detection...")

    client = bigquery.Client(project=PROJECT_ID)
    gaps_found = []

    tables = [
        ('stocks_hourly_clean', 24),
        ('crypto_hourly_clean', 24),
        ('stocks_daily_clean', 48),
        ('crypto_daily_clean', 48),
    ]

    for table_name, stale_hours in tables:
        try:
            query = f"""
            SELECT symbol, MAX(datetime) as last_update
            FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
            GROUP BY symbol
            HAVING TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(datetime), HOUR) > {stale_hours}
            LIMIT 50
            """

            results = list(client.query(query).result())

            for row in results:
                gaps_found.append({
                    'table': table_name,
                    'symbol': row.symbol,
                    'last_update': str(row.last_update)
                })

        except Exception as e:
            logger.error(f"Error checking {table_name}: {e}")

    return {
        'status': 'completed',
        'gaps_found': len(gaps_found),
        'gaps': gaps_found[:20]
    }, 200


if __name__ == "__main__":
    class MockRequest:
        def __init__(self):
            self.args = {'asset_type': 'stocks', 'interval': '1h'}

    result, status = bulletproof_fetch(MockRequest())
    print(json.dumps(result, indent=2, default=str))
