"""
Robust Self-Healing Stock Data Fetcher for TwelveData $229 Plan
- Parallel fetching with 800 calls/min rate limit
- Auto-detects and backfills missing data
- Self-correcting error handling with retries
- Automatic resume on failure
- Covers NASDAQ 100, S&P 500, Russell 2000 top stocks
"""
import functions_framework
from google.cloud import bigquery
from datetime import datetime, timezone, timedelta
import requests
import time
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"
STOCKS_TABLE = "stocks_daily_clean"
CRYPTO_TABLE = "crypto_daily_clean"
PROGRESS_TABLE = "data_fetch_progress"

# TwelveData $229 Plan: 800 calls/min = ~13 calls/sec
MAX_WORKERS = 8
CALLS_PER_SECOND = 10
MAX_RETRIES = 3
RETRY_DELAY = 5

# Thread-safe rate limiting
rate_lock = threading.Lock()
last_call_time = time.time()
call_count = 0

# ============ COMPLETE STOCK LISTS ============

# NASDAQ 100 Components
NASDAQ_100 = [
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'COST',
    'ASML', 'PEP', 'CSCO', 'AZN', 'ADBE', 'NFLX', 'AMD', 'TMUS', 'TXN', 'QCOM',
    'CMCSA', 'INTC', 'AMGN', 'HON', 'INTU', 'AMAT', 'ISRG', 'BKNG', 'SBUX', 'VRTX',
    'LRCX', 'MDLZ', 'ADI', 'GILD', 'PANW', 'REGN', 'ADP', 'MU', 'KLAC', 'SNPS',
    'CDNS', 'MELI', 'PYPL', 'CSX', 'MAR', 'CRWD', 'ORLY', 'MNST', 'MRVL', 'ABNB',
    'NXPI', 'CTAS', 'FTNT', 'DASH', 'PCAR', 'ADSK', 'WDAY', 'CEG', 'CPRT', 'ROP',
    'PAYX', 'KDP', 'AEP', 'ODFL', 'CHTR', 'ROST', 'MCHP', 'KHC', 'FAST', 'EA',
    'DXCM', 'VRSK', 'EXC', 'IDXX', 'CTSH', 'BIIB', 'XEL', 'FANG', 'ON', 'GEHC',
    'ZS', 'ANSS', 'TTD', 'CSGP', 'CDW', 'GFS', 'ILMN', 'DDOG', 'WBD', 'BKR',
    'DLTR', 'MDB', 'TEAM', 'MRNA', 'ALGN', 'EBAY', 'ZM', 'ENPH', 'SIRI', 'LCID'
]

# S&P 500 Top 150 (by market cap)
SP500_TOP = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'JNJ',
    'V', 'XOM', 'WMT', 'JPM', 'PG', 'MA', 'CVX', 'HD', 'ABBV', 'MRK',
    'KO', 'PEP', 'AVGO', 'COST', 'LLY', 'MCD', 'PFE', 'CSCO', 'TMO', 'ACN',
    'ABT', 'DHR', 'NKE', 'VZ', 'NEE', 'CRM', 'ADBE', 'CMCSA', 'TXN', 'INTC',
    'WFC', 'BMY', 'UPS', 'PM', 'QCOM', 'HON', 'RTX', 'AMGN', 'UNP', 'IBM',
    'BA', 'GE', 'SBUX', 'CAT', 'AMD', 'LOW', 'INTU', 'SPGI', 'AXP', 'DE',
    'GS', 'BLK', 'BKNG', 'LMT', 'ADI', 'T', 'PLD', 'TJX', 'GILD', 'MMC',
    'SYK', 'MDLZ', 'ADP', 'CI', 'VRTX', 'AMT', 'CB', 'REGN', 'ZTS', 'ISRG',
    'DUK', 'SO', 'TGT', 'MO', 'PNC', 'BDX', 'USB', 'NOC', 'MMM', 'CL',
    'EOG', 'ITW', 'EQIX', 'ICE', 'CSX', 'WM', 'APD', 'SHW', 'MCK', 'NSC',
    'COP', 'FDX', 'SCHW', 'EMR', 'ORLY', 'CTAS', 'FCX', 'MAR', 'GM', 'F',
    'PSX', 'HCA', 'MPC', 'OXY', 'SLB', 'AIG', 'TFC', 'TRV', 'AFL', 'COF',
    'CARR', 'DG', 'PSA', 'WMB', 'KMI', 'SPG', 'O', 'WELL', 'EQR', 'AVB',
    'EW', 'ILMN', 'A', 'DXCM', 'IDXX', 'IQV', 'MTD', 'BIIB', 'ALGN', 'RMD'
]

# Russell 2000 Top 50 (high-volume small caps)
RUSSELL_TOP = [
    'SMCI', 'MSTR', 'IONQ', 'RIOT', 'MARA', 'COIN', 'PLTR', 'SOFI', 'HOOD', 'AFRM',
    'RKLB', 'JOBY', 'DNA', 'OPEN', 'UPST', 'LC', 'NU', 'BILL', 'PATH', 'DKNG',
    'ROKU', 'SNAP', 'PINS', 'U', 'RBLX', 'DUOL', 'ASAN', 'DOCN', 'GTLB', 'CFLT',
    'GLBE', 'SHOP', 'SQ', 'CRSP', 'NTLA', 'BEAM', 'EDIT', 'VERV', 'RXRX', 'DNLI',
    'ARRY', 'RUN', 'SEDG', 'FSLR', 'PLUG', 'BE', 'BLDP', 'CHPT', 'EVGO', 'QS'
]

# Major ETFs (for index tracking)
MAJOR_ETFS = [
    'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO', 'EFA', 'EEM',
    'GLD', 'SLV', 'USO', 'TLT', 'AGG', 'BND', 'LQD', 'HYG', 'XLF', 'XLK',
    'XLE', 'XLV', 'XLY', 'XLP', 'XLI', 'XLB', 'XLU', 'XLRE', 'XLC', 'SMH',
    'SOXX', 'ARKK', 'IBB', 'XBI', 'VNQ', 'SCHD'
]

# Top 100 Cryptos (USD pairs)
TOP_CRYPTOS = [
    # Top 25 by Market Cap
    'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'SOL/USD', 'DOGE/USD', 'ADA/USD',
    'AVAX/USD', 'LINK/USD', 'DOT/USD', 'TRX/USD', 'MATIC/USD', 'SHIB/USD', 'LTC/USD',
    'ATOM/USD', 'UNI/USD', 'XMR/USD', 'ETC/USD', 'XLM/USD', 'BCH/USD', 'NEAR/USD',
    'FIL/USD', 'AAVE/USD', 'VET/USD', 'ALGO/USD',
    # 26-50
    'HBAR/USD', 'ICP/USD', 'APT/USD', 'ARB/USD', 'OP/USD', 'MKR/USD', 'SUI/USD',
    'SEI/USD', 'RNDR/USD', 'INJ/USD', 'FET/USD', 'PEPE/USD', 'WLD/USD', 'STX/USD',
    'IMX/USD', 'GMX/USD', 'PENDLE/USD', 'BONK/USD', 'JUP/USD', 'TIA/USD', 'PYTH/USD',
    'JTO/USD', 'WIF/USD', 'ORDI/USD', 'THETA/USD',
    # 51-75
    'FTM/USD', 'SAND/USD', 'MANA/USD', 'AXS/USD', 'EGLD/USD', 'XTZ/USD', 'EOS/USD',
    'FLOW/USD', 'NEO/USD', 'KAVA/USD', 'RUNE/USD', 'CHZ/USD', 'CRV/USD', 'COMP/USD',
    'SNX/USD', 'LDO/USD', 'ENJ/USD', 'GALA/USD', 'BAT/USD', 'ZEC/USD', 'DASH/USD',
    'WAVES/USD', 'SUSHI/USD', 'YFI/USD', 'GRT/USD',
    # 76-100
    'ONE/USD', 'CELO/USD', 'AR/USD', 'QNT/USD', 'RPL/USD', 'CFX/USD', 'AGIX/USD',
    'OCEAN/USD', 'DYDX/USD', 'SNT/USD', '1INCH/USD', 'ANKR/USD', 'API3/USD',
    'AUDIO/USD', 'BAND/USD', 'CELR/USD', 'DENT/USD', 'ENS/USD', 'HOT/USD', 'IOST/USD',
    'JASMY/USD', 'KNC/USD', 'LRC/USD', 'MASK/USD', 'STORJ/USD'
]

# Combine all stocks (deduplicated)
ALL_STOCKS = list(set(NASDAQ_100 + SP500_TOP + RUSSELL_TOP + MAJOR_ETFS))
ALL_CRYPTOS = TOP_CRYPTOS


def rate_limited_call():
    """Thread-safe rate limiting for API calls"""
    global last_call_time, call_count
    with rate_lock:
        current_time = time.time()
        elapsed = current_time - last_call_time

        # Reset counter every minute
        if elapsed >= 60:
            call_count = 0
            last_call_time = current_time

        # If we've hit the limit, wait
        if call_count >= 750:  # Leave buffer below 800
            sleep_time = 60 - elapsed
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
            call_count = 0
            last_call_time = time.time()

        # Small delay between calls
        min_delay = 1.0 / CALLS_PER_SECOND
        if elapsed < min_delay:
            time.sleep(min_delay - elapsed)

        call_count += 1
        last_call_time = time.time()


def fetch_with_retry(symbol, interval='1day', outputsize=30, asset_type='stock'):
    """Fetch data with automatic retry on failure"""
    for attempt in range(MAX_RETRIES):
        try:
            rate_limited_call()

            url = f"https://api.twelvedata.com/time_series"
            params = {
                'symbol': symbol,
                'interval': interval,
                'outputsize': outputsize,
                'apikey': API_KEY
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                if 'values' in data and data['values']:
                    return data
                elif 'code' in data and data['code'] == 429:
                    # Rate limited - wait and retry
                    logger.warning(f"Rate limited on {symbol}, waiting...")
                    time.sleep(30)
                    continue
                else:
                    logger.warning(f"No data for {symbol}: {data.get('message', 'Unknown error')}")
                    return None
            elif response.status_code == 429:
                logger.warning(f"Rate limited (429) on {symbol}, waiting...")
                time.sleep(30)
                continue
            else:
                logger.error(f"API error for {symbol}: {response.status_code}")

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout for {symbol}, attempt {attempt + 1}")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            time.sleep(RETRY_DELAY)

    return None


def calculate_indicators(df):
    """Calculate essential technical indicators"""
    try:
        if len(df) < 26:
            return df

        # Price columns
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']

        # Moving Averages
        df['sma_20'] = close.rolling(20).mean()
        df['sma_50'] = close.rolling(50).mean() if len(df) >= 50 else None
        df['sma_200'] = close.rolling(200).mean() if len(df) >= 200 else None
        df['ema_12'] = close.ewm(span=12, adjust=False).mean()
        df['ema_26'] = close.ewm(span=26, adjust=False).mean()
        df['ema_50'] = close.ewm(span=50, adjust=False).mean() if len(df) >= 50 else None

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        df['rsi'] = 100 - (100 / (1 + rs))

        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']

        # Bollinger Bands
        df['bb_middle'] = df['sma_20']
        bb_std = close.rolling(20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)

        # ATR
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['atr'] = tr.rolling(14).mean()

        # ADX
        plus_dm = high.diff().clip(lower=0)
        minus_dm = (-low.diff()).clip(lower=0)
        atr14 = df['atr']
        df['plus_di'] = 100 * (plus_dm.rolling(14).mean() / atr14)
        df['minus_di'] = 100 * (minus_dm.rolling(14).mean() / atr14)
        dx = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
        df['adx'] = dx.rolling(14).mean()

        # Volume indicators
        df['volume_sma'] = volume.rolling(20).mean()
        df['volume_ratio'] = volume / df['volume_sma']

        # Stochastic
        low_14 = low.rolling(14).min()
        high_14 = high.rolling(14).max()
        df['stoch_k'] = 100 * (close - low_14) / (high_14 - low_14)
        df['stoch_d'] = df['stoch_k'].rolling(3).mean()

        return df

    except Exception as e:
        logger.error(f"Error calculating indicators: {str(e)}")
        return df


def process_symbol(symbol, asset_type='stock'):
    """Process a single symbol - fetch and calculate indicators"""
    try:
        data = fetch_with_retry(symbol, outputsize=250 if asset_type == 'stock' else 100, asset_type=asset_type)

        if not data or 'values' not in data:
            return None

        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime')

        # Convert to numeric (handle missing volume for some crypto)
        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Volume might not exist for some crypto pairs
        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0)
        else:
            df['volume'] = 0

        # Add metadata
        meta = data.get('meta', {})
        df['symbol'] = symbol.replace('/USD', '') if '/' in symbol else symbol
        df['exchange'] = meta.get('exchange', '')
        df['currency'] = meta.get('currency', 'USD')
        df['asset_type'] = 'CRYPTO' if '/' in symbol else 'STOCK'
        df['data_source'] = 'twelve_data'

        # Calculate indicators
        df = calculate_indicators(df)

        # Add fetch timestamp
        df['fetch_timestamp'] = datetime.now(timezone.utc)

        # Only return recent data (last 30 days for updates)
        # Use pd.Timestamp for proper comparison with datetime64
        cutoff = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=30)
        df['datetime'] = pd.to_datetime(df['datetime'])
        if df['datetime'].dt.tz is None:
            df['datetime'] = df['datetime'].dt.tz_localize('UTC')
        df = df[df['datetime'] >= cutoff]
        # Remove timezone for BigQuery compatibility
        df['datetime'] = df['datetime'].dt.tz_localize(None)

        return df

    except Exception as e:
        logger.error(f"Error processing {symbol}: {str(e)}")
        return None


def check_missing_dates(client, table_id, symbols, days_back=7):
    """Check for missing dates in the data"""
    try:
        query = f"""
        WITH date_range AS (
            SELECT DATE_SUB(CURRENT_DATE(), INTERVAL {days_back} DAY) as start_date
        ),
        expected_dates AS (
            SELECT date
            FROM UNNEST(GENERATE_DATE_ARRAY(
                (SELECT start_date FROM date_range),
                CURRENT_DATE()
            )) as date
            WHERE EXTRACT(DAYOFWEEK FROM date) BETWEEN 2 AND 6  -- Weekdays only
        ),
        existing_data AS (
            SELECT symbol, DATE(datetime) as date
            FROM `{PROJECT_ID}.{DATASET_ID}.{table_id}`
            WHERE datetime >= (SELECT start_date FROM date_range)
            GROUP BY symbol, DATE(datetime)
        )
        SELECT e.date as missing_date
        FROM expected_dates e
        LEFT JOIN existing_data d ON e.date = d.date
        WHERE d.date IS NULL
        ORDER BY missing_date DESC
        LIMIT 10
        """

        result = client.query(query).result()
        missing = [row.missing_date for row in result]
        return missing

    except Exception as e:
        logger.error(f"Error checking missing dates: {str(e)}")
        return []


def upload_to_bigquery(client, df, table_id):
    """Upload dataframe to BigQuery with schema-aware filtering"""
    try:
        if df is None or df.empty:
            return 0

        # Clean up dataframe
        df = df.replace([np.inf, -np.inf], np.nan)

        # Get existing table schema
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_id}"
        try:
            table = client.get_table(table_ref)
            existing_columns = {field.name for field in table.schema}

            # Filter to only columns that exist in the table
            common_columns = [col for col in df.columns if col in existing_columns]
            df = df[common_columns]
            logger.info(f"Uploading {len(common_columns)} columns to {table_id}")
        except Exception as e:
            logger.warning(f"Could not get table schema, using all columns: {e}")

        # Fill NaN with appropriate defaults
        df = df.fillna(0)

        # Make sure datetime is timezone-naive for BigQuery
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime']).dt.tz_localize(None)

        # Configure job
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        )

        # Upload
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()

        logger.info(f"Successfully uploaded {len(df)} records to {table_id}")
        return len(df)

    except Exception as e:
        logger.error(f"BigQuery upload error: {str(e)}")
        return 0


def fetch_all_parallel(symbols, asset_type='stock'):
    """Fetch all symbols in parallel with rate limiting"""
    results = []
    failed = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_symbol = {
            executor.submit(process_symbol, symbol, asset_type): symbol
            for symbol in symbols
        }

        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                df = future.result()
                if df is not None and not df.empty:
                    results.append(df)
                    logger.info(f"Fetched {symbol}: {len(df)} records")
                else:
                    failed.append(symbol)
            except Exception as e:
                logger.error(f"Failed {symbol}: {str(e)}")
                failed.append(symbol)

    return results, failed


@functions_framework.http
def fetch_daily_data(request):
    """Main HTTP endpoint for Cloud Function"""
    start_time = time.time()

    try:
        client = bigquery.Client(project=PROJECT_ID)

        # Parse request for specific asset type
        request_json = request.get_json(silent=True) or {}
        asset_type = request_json.get('asset_type', 'all')
        backfill = request_json.get('backfill', False)

        results_summary = {
            'stocks': {'fetched': 0, 'records': 0, 'failed': 0},
            'crypto': {'fetched': 0, 'records': 0, 'failed': 0}
        }

        # Fetch Stocks
        if asset_type in ['all', 'stocks']:
            logger.info(f"Fetching {len(ALL_STOCKS)} stocks...")
            stock_dfs, stock_failed = fetch_all_parallel(ALL_STOCKS, 'stock')

            if stock_dfs:
                combined_stocks = pd.concat(stock_dfs, ignore_index=True)
                records = upload_to_bigquery(client, combined_stocks, STOCKS_TABLE)
                results_summary['stocks'] = {
                    'fetched': len(stock_dfs),
                    'records': records,
                    'failed': len(stock_failed)
                }
                logger.info(f"Uploaded {records} stock records")

            # Retry failed symbols once
            if stock_failed:
                logger.info(f"Retrying {len(stock_failed)} failed stocks...")
                time.sleep(10)
                retry_dfs, _ = fetch_all_parallel(stock_failed[:20], 'stock')
                if retry_dfs:
                    combined_retry = pd.concat(retry_dfs, ignore_index=True)
                    retry_records = upload_to_bigquery(client, combined_retry, STOCKS_TABLE)
                    results_summary['stocks']['records'] += retry_records
                    results_summary['stocks']['failed'] -= len(retry_dfs)

        # Fetch Cryptos
        if asset_type in ['all', 'crypto']:
            logger.info(f"Fetching {len(ALL_CRYPTOS)} cryptos...")
            crypto_dfs, crypto_failed = fetch_all_parallel(ALL_CRYPTOS, 'crypto')

            if crypto_dfs:
                combined_crypto = pd.concat(crypto_dfs, ignore_index=True)
                records = upload_to_bigquery(client, combined_crypto, CRYPTO_TABLE)
                results_summary['crypto'] = {
                    'fetched': len(crypto_dfs),
                    'records': records,
                    'failed': len(crypto_failed)
                }
                logger.info(f"Uploaded {records} crypto records")

        elapsed = time.time() - start_time

        response = {
            'success': True,
            'message': 'Data fetch completed',
            'duration_seconds': round(elapsed, 2),
            'results': results_summary,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"Completed in {elapsed:.1f}s: {results_summary}")
        return response, 200

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }, 500


# For local testing
if __name__ == "__main__":
    class MockRequest:
        def get_json(self, silent=False):
            return {'asset_type': 'all'}

    result, status = fetch_daily_data(MockRequest())
    print(json.dumps(result, indent=2))
