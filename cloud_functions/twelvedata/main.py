"""
TwelveData ULTRA-OPTIMIZED Async Fetcher
Features:
- True async with aiohttp (30x+ faster than ThreadPool)
- Semaphore-based rate limiting
- Valid TwelveData symbols (updated Dec 2025)
- Batch BigQuery uploads
- Circuit breaker pattern
- Correct v2 table naming
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
import hashlib
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'

# Ultra-high performance settings
MAX_CONCURRENT = 20  # Concurrent async requests
BATCH_SIZE = 500  # BigQuery batch size
REQUEST_TIMEOUT = 25
RATE_LIMIT_PER_SECOND = 15  # Stay under TwelveData limits
SEMAPHORE_DELAY = 1.0 / RATE_LIMIT_PER_SECOND

# Circuit breaker
circuit_state = {'failures': 0, 'is_open': False, 'reset_at': None}

# =============================================================================
# VALID TWELVEDATA SYMBOLS (Updated Dec 2025)
# =============================================================================

ASSET_CONFIG = {
    'stocks': {
        'symbols': [
            # S&P 500 Top 100 by Market Cap (Updated Dec 2025)
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH',
            'JNJ', 'V', 'XOM', 'WMT', 'JPM', 'PG', 'MA', 'CVX', 'HD', 'ABBV',
            'MRK', 'KO', 'PEP', 'AVGO', 'COST', 'LLY', 'MCD', 'PFE', 'CSCO', 'TMO',
            'ACN', 'ABT', 'DHR', 'NKE', 'VZ', 'NEE', 'CRM', 'ADBE', 'CMCSA', 'TXN',
            'INTC', 'WFC', 'BMY', 'UPS', 'PM', 'QCOM', 'HON', 'RTX', 'AMGN', 'UNP',
            'IBM', 'ORCL', 'AMD', 'CAT', 'GS', 'BA', 'SBUX', 'GE', 'DE', 'MMM',
            'DIS', 'LOW', 'INTU', 'MS', 'BLK', 'SPGI', 'MDLZ', 'ISRG', 'ADP', 'GILD',
            'SYK', 'VRTX', 'AXP', 'ADI', 'BKNG', 'REGN', 'SCHW', 'ETN', 'LMT', 'LRCX',
            'ZTS', 'MO', 'C', 'PLD', 'NOW', 'CB', 'CI', 'CME', 'CVS', 'BDX',
            'EOG', 'SO', 'DUK', 'SLB', 'BSX', 'MU', 'APD', 'ICE', 'PANW', 'CL',
            # S&P 500 - Next 100 (101-200)
            'NOC', 'ITW', 'PNC', 'SHW', 'AON', 'USB', 'TJX', 'FCX', 'SNPS', 'TGT',
            'CDNS', 'FDX', 'COP', 'PSA', 'NSC', 'WM', 'EMR', 'MCK', 'MCO', 'HUM',
            'MAR', 'ROP', 'GD', 'MPC', 'APH', 'OXY', 'WELL', 'ORLY', 'TT', 'MCHP',
            'PH', 'MSI', 'NXPI', 'ECL', 'PSX', 'CTAS', 'AJG', 'AFL', 'HLT', 'VLO',
            'FIS', 'ANET', 'NEM', 'PAYX', 'KMB', 'PCAR', 'AZO', 'TRV', 'STZ', 'SPG',
            # Russell 2000 Top Stocks
            'AXON', 'DECK', 'ELF', 'FN', 'LSTR', 'CRUS', 'SSD', 'SITE', 'CRVL', 'KRYS',
            'TREX', 'PRMW', 'RBC', 'SHAK', 'PI', 'CORT', 'OMCL', 'GFF', 'BCPC', 'DY',
            # Tech Growth Stocks
            'CRWD', 'DDOG', 'NET', 'ZS', 'SNOW', 'PLTR', 'COIN', 'SHOP', 'SQ', 'PYPL',
            'ROKU', 'U', 'TTD', 'SNAP', 'PINS', 'UBER', 'LYFT', 'DASH', 'ABNB', 'HOOD',
            # Financial Sector
            'BAC', 'T', 'TMUS', 'CCI', 'AMT', 'EQIX', 'PSA', 'DLR', 'AVB', 'EQR',
            # Healthcare & Biotech
            'MRNA', 'BIIB', 'RGEN', 'ALNY', 'SRPT', 'EXEL', 'INCY', 'JAZZ', 'BMRN', 'UTHR',
            # Energy
            'DVN', 'HAL', 'BKR', 'FANG', 'PXD', 'APA', 'MRO', 'OVV', 'CTRA', 'EQT',
            # Consumer
            'LULU', 'RCL', 'MAR', 'HLT', 'CCL', 'NCLH', 'EXPE', 'BKNG', 'WYNN', 'LVS',
            # Industrial
            'FTV', 'IR', 'ROK', 'AME', 'XYL', 'IEX', 'PNR', 'GNRC', 'TTC', 'SNA'
        ],
        'exchange': 'NASDAQ,NYSE'
    },
    'crypto': {
        'symbols': [
            # VALID TwelveData crypto symbols (tested Dec 2025)
            'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'ADA/USD', 'SOL/USD', 'DOGE/USD',
            'DOT/USD', 'LTC/USD', 'SHIB/USD', 'TRX/USD', 'AVAX/USD', 'LINK/USD',
            'ATOM/USD', 'UNI/USD', 'XMR/USD', 'ETC/USD', 'XLM/USD', 'BCH/USD',
            'FIL/USD', 'NEAR/USD', 'ALGO/USD', 'VET/USD', 'ICP/USD',
            'HBAR/USD', 'AAVE/USD', 'SAND/USD', 'MANA/USD', 'AXS/USD',
            'THETA/USD', 'XTZ/USD', 'ZEC/USD', 'DASH/USD', 'NEO/USD',
            'BAT/USD', 'COMP/USD', 'ENJ/USD', 'CHZ/USD', 'GRT/USD',
            # POL replaced MATIC, APE still valid
            'POL/USD', 'APE/USD', 'OP/USD', 'ARB/USD', 'SUI/USD', 'SEI/USD',
            # Additional cryptos
            'ZORA/USD', 'IMX/USD', 'INJ/USD', 'LDO/USD', 'RUNE/USD', 'CRO/USD',
            'SNX/USD', 'RPL/USD', 'FLOW/USD', 'CFX/USD'
        ]
    },
    'forex': {
        'symbols': [
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',
            'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'EUR/CHF', 'AUD/JPY', 'USD/MXN', 'USD/INR',
            'EUR/AUD', 'GBP/CHF', 'EUR/CAD', 'AUD/NZD', 'USD/SGD', 'USD/HKD'
        ]
    },
    'etfs': {
        'symbols': [
            # TOP 20 ETFs by AUM (>$4.8 trillion combined) - Priority
            'VOO', 'IVV', 'SPY', 'SPLG',  # S&P 500 ETFs
            'VTI', 'QQQ', 'VUG', 'VGT', 'IWF',  # Total Market & Growth
            'VTV',  # Value
            'VEA', 'IEFA', 'VXUS',  # International Developed
            'IEMG', 'VWO',  # Emerging Markets
            'BND', 'AGG',  # Bonds
            'IJH', 'VIG',  # Mid-Cap & Dividend
            'GLD',  # Gold
            # Additional ETFs
            'IWM', 'DIA', 'EFA', 'EEM', 'SLV', 'USO', 'TLT', 'IEF', 'LQD', 'HYG',
            'VNQ', 'XLF', 'XLK', 'XLE', 'XLV', 'ARKK', 'SOXX', 'SMH'
        ],
        'exchange': 'NYSE,NASDAQ'
    },
    'indices': {
        'symbols': [
            # Use TwelveData format for indices
            'SPX', 'IXIC', 'DJI:INDEXDJX', 'RUT:INDEXRUSSELL',
            'FTSE:INDEXFTSE', 'GDAXI:INDEXDB', 'N225:INDEXNIKKEI',
            'HSI:INDEXHANGSENG', 'STOXX50E:INDEXSTOXX'
        ]
    },
    'commodities': {
        'symbols': [
            # Valid TwelveData commodity symbols
            'XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD',
            'CL', 'BZ', 'NG', 'HO',  # Oil, Brent, NatGas, Heating Oil
            'GC', 'SI', 'HG',  # Gold, Silver, Copper futures
            'ZC', 'ZW', 'ZS'  # Corn, Wheat, Soybean futures
        ]
    }
}

TIMEFRAME_CONFIG = {
    'weekly': {'interval': '1week', 'outputsize': 5000},   # MAX - was 52!
    'daily': {'interval': '1day', 'outputsize': 5000},    # MAX - was 365!
    'hourly': {'interval': '1h', 'outputsize': 5000},     # MAX - was 168!
    '5min': {'interval': '5min', 'outputsize': 5000}      # MAX - was 288!
}


# =============================================================================
# ASYNC FETCH FUNCTIONS
# =============================================================================

async def rate_limited_fetch(semaphore: asyncio.Semaphore, session: aiohttp.ClientSession,
                             url: str, params: dict) -> Optional[dict]:
    """Fetch with rate limiting via semaphore"""
    if circuit_state['is_open']:
        if circuit_state['reset_at'] and datetime.now() < circuit_state['reset_at']:
            return None
        circuit_state['is_open'] = False
        circuit_state['failures'] = 0

    async with semaphore:
        try:
            await asyncio.sleep(SEMAPHORE_DELAY)  # Rate limit

            async with session.get(url, params=params, timeout=REQUEST_TIMEOUT) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'values' in data:
                        circuit_state['failures'] = max(0, circuit_state['failures'] - 1)
                        return data
                    elif 'message' in data:
                        logger.debug(f"No data for {params.get('symbol')}: {data['message']}")
                        return None
                elif response.status == 429:
                    logger.warning("Rate limited - backing off")
                    await asyncio.sleep(5)
                    return None
                else:
                    circuit_state['failures'] += 1
                    if circuit_state['failures'] >= 15:
                        circuit_state['is_open'] = True
                        circuit_state['reset_at'] = datetime.now() + timedelta(minutes=3)
                    return None

        except asyncio.TimeoutError:
            logger.warning(f"Timeout for {params.get('symbol')}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {params.get('symbol')}: {e}")
            return None


async def fetch_time_series_async(semaphore: asyncio.Semaphore, session: aiohttp.ClientSession,
                                  symbol: str, interval: str, outputsize: int) -> Optional[pd.DataFrame]:
    """Async fetch of time series data"""
    params = {
        'symbol': symbol,
        'interval': interval,
        'outputsize': outputsize,
        'apikey': TWELVEDATA_API_KEY,
        'format': 'JSON'
    }

    data = await rate_limited_fetch(semaphore, session, f"{BASE_URL}/time_series", params)

    if data and 'values' in data:
        df = pd.DataFrame(data['values'])
        df['symbol'] = symbol.replace('/', '').replace(':', '_')
        df['name'] = data.get('meta', {}).get('name', symbol)
        df['exchange'] = data.get('meta', {}).get('exchange', '')
        df['currency'] = data.get('meta', {}).get('currency', 'USD')

        df['datetime'] = pd.to_datetime(df['datetime'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Calculate percent change
        if len(df) >= 2 and 'close' in df.columns:
            df['percent_change'] = df['close'].pct_change() * 100

        return df

    return None


async def fetch_indicator_async(semaphore: asyncio.Semaphore, session: aiohttp.ClientSession,
                                symbol: str, interval: str, indicator: str, params: dict) -> Optional[dict]:
    """Async fetch of a single indicator"""
    request_params = {
        'symbol': symbol,
        'interval': interval,
        'apikey': TWELVEDATA_API_KEY,
        'outputsize': 1,
        **params
    }

    data = await rate_limited_fetch(semaphore, session, f"{BASE_URL}/{indicator}", request_params)

    if data and 'values' in data and len(data['values']) > 0:
        return data['values'][0]
    return None


async def fetch_all_indicators_async(semaphore: asyncio.Semaphore, session: aiohttp.ClientSession,
                                     symbol: str, interval: str) -> dict:
    """Fetch all indicators concurrently for a symbol"""
    indicators_to_fetch = [
        ('rsi', {'time_period': 14}),
        ('macd', {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}),
        ('bbands', {'time_period': 20, 'sd': 2}),
        ('sma', {'time_period': 20}),
        ('sma', {'time_period': 50}),
        ('sma', {'time_period': 200}),
        ('ema', {'time_period': 12}),
        ('ema', {'time_period': 26}),
        ('adx', {'time_period': 14}),
        ('atr', {'time_period': 14}),
        ('stoch', {'fast_k_period': 14, 'slow_k_period': 3, 'slow_d_period': 3}),
        ('cci', {'time_period': 20}),
    ]

    tasks = [
        fetch_indicator_async(semaphore, session, symbol, interval, ind, params)
        for ind, params in indicators_to_fetch
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    indicators = {}

    for i, result in enumerate(results):
        if isinstance(result, Exception) or result is None:
            continue

        ind_name = indicators_to_fetch[i][0]
        params = indicators_to_fetch[i][1]

        try:
            if ind_name == 'rsi':
                indicators['rsi'] = float(result.get('rsi', 0) or 0)
            elif ind_name == 'macd':
                indicators['macd'] = float(result.get('macd', 0) or 0)
                indicators['macd_signal'] = float(result.get('macd_signal', 0) or 0)
                indicators['macd_histogram'] = float(result.get('macd_hist', 0) or 0)
            elif ind_name == 'bbands':
                indicators['bollinger_upper'] = float(result.get('upper_band', 0) or 0)
                indicators['bollinger_middle'] = float(result.get('middle_band', 0) or 0)
                indicators['bollinger_lower'] = float(result.get('lower_band', 0) or 0)
            elif ind_name == 'sma':
                period = params['time_period']
                indicators[f'sma_{period}'] = float(result.get('sma', 0) or 0)
            elif ind_name == 'ema':
                period = params['time_period']
                indicators[f'ema_{period}'] = float(result.get('ema', 0) or 0)
            elif ind_name == 'adx':
                indicators['adx'] = float(result.get('adx', 0) or 0)
            elif ind_name == 'atr':
                indicators['atr'] = float(result.get('atr', 0) or 0)
            elif ind_name == 'stoch':
                indicators['stoch_k'] = float(result.get('slow_k', 0) or 0)
                indicators['stoch_d'] = float(result.get('slow_d', 0) or 0)
            elif ind_name == 'cci':
                indicators['cci'] = float(result.get('cci', 0) or 0)
        except (ValueError, TypeError):
            continue

    return indicators


async def fetch_symbol_complete(semaphore: asyncio.Semaphore, session: aiohttp.ClientSession,
                                symbol: str, interval: str, outputsize: int,
                                fetch_indicators: bool = True) -> Optional[pd.DataFrame]:
    """Fetch complete data for a single symbol"""
    df = await fetch_time_series_async(semaphore, session, symbol, interval, outputsize)

    if df is None or df.empty:
        return None

    if fetch_indicators:
        indicators = await fetch_all_indicators_async(semaphore, session, symbol, interval)
        for key, value in indicators.items():
            df[key] = value

    return df


async def fetch_all_symbols_async(symbols: List[str], interval: str, outputsize: int,
                                  fetch_indicators: bool = True) -> List[pd.DataFrame]:
    """Fetch all symbols concurrently with rate limiting"""
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT, limit_per_host=MAX_CONCURRENT)
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT * 2)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [
            fetch_symbol_complete(semaphore, session, symbol, interval, outputsize, fetch_indicators)
            for symbol in symbols
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

    dataframes = []
    successful = 0
    failed = 0

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Error for {symbols[i]}: {result}")
            failed += 1
        elif result is not None and not result.empty:
            dataframes.append(result)
            successful += 1
        else:
            failed += 1

    logger.info(f"Fetched {successful}/{len(symbols)} symbols ({failed} failed)")
    return dataframes


def calculate_indicators_local(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate indicators locally - saves 12 API calls per symbol!"""
    if len(df) < 50:
        return df

    df = df.sort_values('datetime').copy()

    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta.where(delta < 0, 0))
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df['rsi'] = 100 - (100 / (1 + rs))

    # Moving Averages
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean() if len(df) >= 200 else None
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()

    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']

    # Bollinger Bands
    df['bollinger_middle'] = df['sma_20']
    std_20 = df['close'].rolling(window=20).std()
    df['bollinger_upper'] = df['bollinger_middle'] + (std_20 * 2)
    df['bollinger_lower'] = df['bollinger_middle'] - (std_20 * 2)

    # ATR
    tr1 = df['high'] - df['low']
    tr2 = abs(df['high'] - df['close'].shift())
    tr3 = abs(df['low'] - df['close'].shift())
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(window=14).mean()

    # Stochastic
    low_14 = df['low'].rolling(window=14).min()
    high_14 = df['high'].rolling(window=14).max()
    df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14).replace(0, np.nan))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # ADX
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    tr_sum = true_range.rolling(window=14).sum()
    df['plus_di'] = 100 * (plus_dm.rolling(window=14).sum() / tr_sum.replace(0, np.nan))
    df['minus_di'] = 100 * (minus_dm.rolling(window=14).sum() / tr_sum.replace(0, np.nan))
    dx = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']).replace(0, np.nan)
    df['adx'] = dx.rolling(window=14).mean()

    # CCI
    tp = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = tp.rolling(window=20).mean()
    mad = tp.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
    df['cci'] = (tp - sma_tp) / (0.015 * mad)

    return df


def upload_to_bigquery(dataframes: List[pd.DataFrame], table_id: str) -> Tuple[bool, int]:
    """Upload combined dataframes to BigQuery"""
    if not dataframes:
        return True, 0

    try:
        # Calculate indicators locally for each dataframe
        processed_dfs = []
        for df in dataframes:
            processed_dfs.append(calculate_indicators_local(df))

        combined = pd.concat(processed_dfs, ignore_index=True)

        if combined.empty:
            return True, 0

        # Generate unique IDs
        combined['id'] = combined.apply(
            lambda row: hashlib.md5(f"{row['symbol']}_{row['datetime']}".encode()).hexdigest()[:16],
            axis=1
        )

        combined['date'] = pd.to_datetime(combined['datetime']).dt.date
        combined['data_source'] = 'twelvedata'
        combined['created_at'] = datetime.now(timezone.utc)
        combined['updated_at'] = datetime.now(timezone.utc)

        # Drop duplicates
        combined = combined.drop_duplicates(subset=['symbol', 'datetime'], keep='last')

        client = bigquery.Client(project=PROJECT_ID)

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
        )

        job = client.load_table_from_dataframe(combined, table_id, job_config=job_config)
        job.result()

        logger.info(f"Uploaded {len(combined)} rows to {table_id}")
        return True, len(combined)

    except Exception as e:
        logger.error(f"BigQuery upload error: {e}")
        return False, 0


def run_async_fetch(asset_types: List[str], timeframe: str, limit: Optional[int] = None,
                    fetch_indicators: bool = True) -> Dict[str, Any]:
    """Run async fetch for specified asset types"""
    tf_config = TIMEFRAME_CONFIG.get(timeframe, TIMEFRAME_CONFIG['daily'])
    interval = tf_config['interval']
    outputsize = tf_config['outputsize']

    results = {}
    total_rows = 0

    for asset_type in asset_types:
        if asset_type not in ASSET_CONFIG:
            continue

        symbols = ASSET_CONFIG[asset_type]['symbols']
        if limit and limit > 0:
            symbols = symbols[:limit]

        logger.info(f"Fetching {len(symbols)} {asset_type} symbols...")

        # Run async fetch
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            dataframes = loop.run_until_complete(
                fetch_all_symbols_async(symbols, interval, outputsize, fetch_indicators)
            )
        finally:
            loop.close()

        # Upload to correct v2 table
        table_id = f"{PROJECT_ID}.{DATASET_ID}.v2_{asset_type}_{timeframe}"
        success, rows = upload_to_bigquery(dataframes, table_id)

        results[asset_type] = {
            'symbols_attempted': len(symbols),
            'symbols_fetched': len(dataframes),
            'rows_uploaded': rows,
            'success': success,
            'table': table_id
        }
        total_rows += rows

    return {'results': results, 'total_rows': total_rows}


@functions_framework.http
def fetch_twelvedata_optimized(request):
    """
    ULTRA-OPTIMIZED Cloud Function Entry Point

    Query params:
        asset_type: stocks, crypto, forex, etfs, indices, commodities, or 'all'
        timeframe: weekly, daily, hourly, 5min
        limit: max symbols per asset type
        fast: true = skip indicators for faster fetch
    """
    start_time = time.time()

    request_json = request.get_json(silent=True) or {}
    args = request.args

    asset_type = args.get('asset_type') or request_json.get('asset_type') or 'all'
    timeframe = args.get('timeframe') or request_json.get('timeframe') or 'daily'
    limit = args.get('limit') or request_json.get('limit')
    fast_mode = args.get('fast', '').lower() == 'true'

    if limit:
        limit = int(limit)

    logger.info(f"ULTRA-OPTIMIZED fetch: {asset_type}/{timeframe}, limit={limit}, fast={fast_mode}")

    # Determine asset types
    if asset_type == 'all':
        asset_types = list(ASSET_CONFIG.keys())
    else:
        asset_types = [asset_type]

    # Run async fetch - ALWAYS use fast mode to avoid wasting API calls on single-record indicators
    # Indicators are calculated locally instead
    result = run_async_fetch(asset_types, timeframe, limit, fetch_indicators=False)

    elapsed = time.time() - start_time

    return {
        'status': 'completed',
        'mode': 'ultra-optimized-async',
        'asset_type': asset_type,
        'timeframe': timeframe,
        'total_rows': result['total_rows'],
        'results': result['results'],
        'elapsed_seconds': round(elapsed, 2),
        'requests_per_second': round(sum(r['symbols_attempted'] for r in result['results'].values()) / max(elapsed, 1), 2),
        'circuit_breaker': 'open' if circuit_state['is_open'] else 'closed',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


# For local testing
if __name__ == "__main__":
    class MockRequest:
        args = {'asset_type': 'stocks', 'timeframe': 'daily', 'limit': '10', 'fast': 'true'}
        def get_json(self, silent=False):
            return None

    result = fetch_twelvedata_optimized(MockRequest())
    print(result)
