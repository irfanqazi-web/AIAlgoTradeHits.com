"""
Kraken Pro Hourly Data Fetcher with Technical Indicators
Fetches 60-minute OHLC data and calculates comprehensive technical indicators
"""

import krakenex
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timedelta
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'hourly_crypto'

def calculate_technical_indicators(df):
    """Calculate all technical indicators for a dataframe"""

    if len(df) < 200:
        logger.warning(f"Not enough data for full indicator calculation: {len(df)} rows")

    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)

    # Basic fields
    df['symbol'] = df['pair']
    df['open_price'] = df['open']
    df['hi_lo'] = df['high'] - df['low']
    df['pct_hi_lo_over_lo'] = ((df['high'] - df['low']) / df['low']) * 100

    # RSI (14 periods)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # Bollinger Bands
    df['sma_20'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['sma_20'] + (bb_std * 2)
    df['bb_lower'] = df['sma_20'] - (bb_std * 2)
    df['bb_percent'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

    # EMAs
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

    # SMAs
    df['ma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean()

    # Stochastic Oscillator
    low_14 = df['low'].rolling(window=14).min()
    high_14 = df['high'].rolling(window=14).max()
    df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # Williams %R
    df['williams_r'] = -100 * ((high_14 - df['close']) / (high_14 - low_14))

    # ADX (Average Directional Index) - simplified
    high_diff = df['high'].diff()
    low_diff = -df['low'].diff()

    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

    tr1 = df['high'] - df['low']
    tr2 = abs(df['high'] - df['close'].shift())
    tr3 = abs(df['low'] - df['close'].shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr14 = tr.rolling(window=14).mean()
    df['atr'] = atr14

    plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr14)
    minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr14)

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    df['adx'] = dx.rolling(window=14).mean()

    # CCI (Commodity Channel Index)
    tp = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = tp.rolling(window=20).mean()
    mad = tp.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
    df['cci'] = (tp - sma_tp) / (0.015 * mad)

    # ROC (Rate of Change)
    df['roc'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100

    # Momentum
    df['momentum'] = df['close'] - df['close'].shift(10)

    # TRIX (Triple Exponential Average)
    ema1 = df['close'].ewm(span=15, adjust=False).mean()
    ema2 = ema1.ewm(span=15, adjust=False).mean()
    ema3 = ema2.ewm(span=15, adjust=False).mean()
    df['trix'] = ((ema3 - ema3.shift()) / ema3.shift()) * 100

    # Ultimate Oscillator (simplified)
    bp = df['close'] - pd.concat([df['low'], df['close'].shift()], axis=1).min(axis=1)
    tr_uo = pd.concat([df['high'], df['close'].shift()], axis=1).max(axis=1) - pd.concat([df['low'], df['close'].shift()], axis=1).min(axis=1)

    avg7 = bp.rolling(window=7).sum() / tr_uo.rolling(window=7).sum()
    avg14 = bp.rolling(window=14).sum() / tr_uo.rolling(window=14).sum()
    avg28 = bp.rolling(window=28).sum() / tr_uo.rolling(window=28).sum()

    df['ultimate_oscillator'] = 100 * ((4 * avg7) + (2 * avg14) + avg28) / 7

    # KAMA (Kaufman's Adaptive Moving Average)
    change = abs(df['close'] - df['close'].shift(10))
    volatility = (abs(df['close'] - df['close'].shift())).rolling(window=10).sum()
    er = change / volatility  # Efficiency Ratio

    fastest = 2 / (2 + 1)
    slowest = 2 / (30 + 1)
    sc = (er * (fastest - slowest) + slowest) ** 2

    kama = pd.Series(index=df.index, dtype=float)
    kama.iloc[0] = df['close'].iloc[0]
    for i in range(1, len(df)):
        kama.iloc[i] = kama.iloc[i-1] + sc.iloc[i] * (df['close'].iloc[i] - kama.iloc[i-1])
    df['kama'] = kama

    # PPO (Percentage Price Oscillator)
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['ppo'] = ((ema12 - ema26) / ema26) * 100

    # PVO (Percentage Volume Oscillator)
    vol_ema12 = df['volume'].ewm(span=12, adjust=False).mean()
    vol_ema26 = df['volume'].ewm(span=26, adjust=False).mean()
    df['pvo'] = ((vol_ema12 - vol_ema26) / vol_ema26) * 100

    # Awesome Oscillator
    median_price = (df['high'] + df['low']) / 2
    ao_fast = median_price.rolling(window=5).mean()
    ao_slow = median_price.rolling(window=34).mean()
    df['awesome_oscillator'] = ao_fast - ao_slow

    # OBV (On-Balance Volume)
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['obv'] = obv

    return df


def fetch_hourly_data():
    """Fetch 60-minute OHLC data for top 100 USD trading pairs from Kraken"""

    kraken = krakenex.API()

    # Top 100 most liquid and actively traded crypto pairs
    TOP_CRYPTO_PAIRS = [
        # Major cryptos (Top 20)
        'XXBTZUSD', 'XETHZUSD', 'USDTZUSD', 'XRPUSD', 'SOLUSD',
        'ADAUSD', 'DOGEUSDT', 'MATICUSD', 'DOTUSDT', 'AVAXUSD',
        'LINKUSD', 'ATOMUSD', 'UNIUSD', 'XLMUSD', 'ETCUSD',
        'LTCUSD', 'NEARUSD', 'ALGOUSD', 'BCHUSD', 'TRXUSD',

        # DeFi & Layer 2 (20)
        'AAVEUSD', 'MKRUSD', 'COMPUSD', 'SNXUSD', 'YFIUSD',
        'CRVUSD', 'BALUSD', 'GRTUSD', 'LRCUSD', 'ENJUSD',
        'MANAUSD', 'SANDUSD', 'AXSUSD', 'RUNEUSD', 'FTMUSD',
        'ICXUSD', 'ZRXUSD', 'OMGUSD', 'KNCUSD', '1INCHUSD',

        # Popular altcoins (30)
        'FILUSD', 'EGLDUSD', 'APEUSD', 'CHZUSD', 'KSMUSD',
        'FLOWUSD', 'IOTAUSD', 'ZILUSD', 'BATUSD', 'ZECUSD',
        'DASHUSD', 'QTUMUSD', 'ICPUSD', 'THETAUSD', 'VETUSDT',
        'HBARUSD', 'EOSUSD', 'XTZUSD', 'WAVESUSDT', 'ARUSD',
        'PEPEUSD', 'LDOUSD', 'BLURUSD', 'ARBUSDT', 'OPUSD',
        'INJUSD', 'SUIUSD', 'TONUSD', 'BONKUSD', 'WIFUSD',

        # Stablecoins & Wrapped (10)
        'USDCUSD', 'DAIUSD', 'WBTCUSD', 'WETHUSDT', 'FDUSDUSDT',
        'USDPUSD', 'USDDUSDT', 'TUSDUSDT', 'BUSDUSD', 'PAXUSD',

        # Gaming & Metaverse (10)
        'GALAUSD', 'IMXUSD', 'GMTUSD', 'APTUSD', 'ROSEUSD',
        'ANKRUSD', 'AUDIOUSD', 'STORJUSD', 'OCEANUSD', 'SKLUSD',

        # Meme & Community (10)
        'SHIBUSDT', 'FLOKIUSD', 'LUNCUSDT', 'SPELLUSDT', 'SUSHIUSD',
        'FETUSD', 'AGIXUSD', 'RENDERUSD', 'JASMYUSD', 'ACHUSDT'
    ]

    logger.info(f"Configured to fetch {len(TOP_CRYPTO_PAIRS)} top crypto pairs")

    # Validate pairs exist and are online
    logger.info("Fetching tradable asset pairs from Kraken...")
    pairs_response = kraken.query_public('AssetPairs')

    if pairs_response['error']:
        logger.error(f"Error fetching pairs: {pairs_response['error']}")
        return None

    all_pairs = pairs_response['result']

    # Filter to only include pairs that are in our top list and are online
    usd_pairs = {}
    for pair in TOP_CRYPTO_PAIRS:
        if pair in all_pairs and all_pairs[pair].get('status') == 'online':
            usd_pairs[pair] = all_pairs[pair]
        else:
            logger.warning(f"Pair {pair} not found or not online")

    logger.info(f"Successfully validated {len(usd_pairs)} USD trading pairs")

    # Fetch 250 hours to ensure we have enough for SMA_200
    hours_ago = datetime.now() - timedelta(hours=250)
    since_timestamp = int(hours_ago.timestamp())

    all_processed_data = []
    failed_pairs = []
    successful_pairs = 0

    for idx, (pair, info) in enumerate(usd_pairs.items(), 1):
        try:
            if idx % 50 == 0:
                logger.info(f"Progress: {idx}/{len(usd_pairs)} pairs")

            # Fetch OHLC data
            ohlc_response = kraken.query_public('OHLC', {
                'pair': pair,
                'interval': 60,  # 60-minute candles
                'since': since_timestamp
            })

            if ohlc_response['error']:
                logger.warning(f"Error fetching {pair}: {ohlc_response['error']}")
                failed_pairs.append({'pair': pair, 'error': str(ohlc_response['error'])})
                continue

            # Parse OHLC data
            ohlc_list = list(ohlc_response['result'].values())[0]

            if len(ohlc_list) < 50:
                logger.warning(f"Not enough data for {pair}: {len(ohlc_list)} candles")
                continue

            # Create dataframe for this pair
            df_pair = pd.DataFrame(ohlc_list, columns=['timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
            df_pair['pair'] = pair
            df_pair['altname'] = info.get('altname', pair)
            df_pair['base'] = info.get('base', '')
            df_pair['quote'] = info.get('quote', '')

            # Convert types
            for col in ['open', 'high', 'low', 'close', 'vwap', 'volume']:
                df_pair[col] = df_pair[col].astype(float)
            df_pair['count'] = df_pair['count'].astype(int)
            df_pair['timestamp'] = df_pair['timestamp'].astype(int)
            df_pair['datetime'] = pd.to_datetime(df_pair['timestamp'], unit='s')

            # Calculate technical indicators
            df_pair = calculate_technical_indicators(df_pair)

            # Store ALL hourly records, not just latest
            df_pair['fetched_at'] = datetime.now()

            all_processed_data.append(df_pair)
            successful_pairs += 1

            # Rate limiting
            time.sleep(1.5)

        except Exception as e:
            logger.error(f"Exception fetching {pair}: {str(e)}")
            failed_pairs.append({'pair': pair, 'error': str(e)})
            time.sleep(2)

    logger.info(f"Successfully processed {successful_pairs}/{len(usd_pairs)} pairs")

    if failed_pairs:
        logger.warning(f"Failed pairs: {len(failed_pairs)}")

    if all_processed_data:
        return pd.concat(all_processed_data, ignore_index=True)
    return None


def append_to_bigquery(df):
    """Append data to BigQuery with all technical indicators"""

    if df is None or df.empty:
        logger.warning("No data to upload")
        return False

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    # Define comprehensive schema
    schema = [
        bigquery.SchemaField("pair", "STRING"),
        bigquery.SchemaField("symbol", "STRING"),
        bigquery.SchemaField("altname", "STRING"),
        bigquery.SchemaField("base", "STRING"),
        bigquery.SchemaField("quote", "STRING"),
        bigquery.SchemaField("timestamp", "INTEGER"),
        bigquery.SchemaField("datetime", "TIMESTAMP"),
        bigquery.SchemaField("open", "FLOAT"),
        bigquery.SchemaField("open_price", "FLOAT"),
        bigquery.SchemaField("high", "FLOAT"),
        bigquery.SchemaField("low", "FLOAT"),
        bigquery.SchemaField("close", "FLOAT"),
        bigquery.SchemaField("vwap", "FLOAT"),
        bigquery.SchemaField("volume", "FLOAT"),
        bigquery.SchemaField("count", "INTEGER"),
        bigquery.SchemaField("hi_lo", "FLOAT"),
        bigquery.SchemaField("pct_hi_lo_over_lo", "FLOAT"),
        bigquery.SchemaField("rsi", "FLOAT"),
        bigquery.SchemaField("macd", "FLOAT"),
        bigquery.SchemaField("macd_signal", "FLOAT"),
        bigquery.SchemaField("macd_hist", "FLOAT"),
        bigquery.SchemaField("bb_upper", "FLOAT"),
        bigquery.SchemaField("bb_lower", "FLOAT"),
        bigquery.SchemaField("bb_percent", "FLOAT"),
        bigquery.SchemaField("ema_12", "FLOAT"),
        bigquery.SchemaField("ema_26", "FLOAT"),
        bigquery.SchemaField("ema_50", "FLOAT"),
        bigquery.SchemaField("ma_50", "FLOAT"),
        bigquery.SchemaField("sma_20", "FLOAT"),
        bigquery.SchemaField("sma_200", "FLOAT"),
        bigquery.SchemaField("stoch_k", "FLOAT"),
        bigquery.SchemaField("stoch_d", "FLOAT"),
        bigquery.SchemaField("williams_r", "FLOAT"),
        bigquery.SchemaField("adx", "FLOAT"),
        bigquery.SchemaField("cci", "FLOAT"),
        bigquery.SchemaField("roc", "FLOAT"),
        bigquery.SchemaField("momentum", "FLOAT"),
        bigquery.SchemaField("trix", "FLOAT"),
        bigquery.SchemaField("ultimate_oscillator", "FLOAT"),
        bigquery.SchemaField("kama", "FLOAT"),
        bigquery.SchemaField("ppo", "FLOAT"),
        bigquery.SchemaField("pvo", "FLOAT"),
        bigquery.SchemaField("awesome_oscillator", "FLOAT"),
        bigquery.SchemaField("atr", "FLOAT"),
        bigquery.SchemaField("obv", "FLOAT"),
        bigquery.SchemaField("fetched_at", "TIMESTAMP"),
    ]

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        schema=schema,
    )

    try:
        # Check for duplicates
        min_timestamp = df['timestamp'].min()
        max_timestamp = df['timestamp'].max()

        query = f"""
        SELECT DISTINCT pair, timestamp
        FROM `{table_ref}`
        WHERE timestamp BETWEEN {min_timestamp} AND {max_timestamp}
        """

        try:
            existing_data = client.query(query).to_dataframe()
            logger.info(f"Found {len(existing_data)} existing records")

            if not existing_data.empty:
                df['key'] = df['pair'] + '_' + df['timestamp'].astype(str)
                existing_data['key'] = existing_data['pair'] + '_' + existing_data['timestamp'].astype(str)

                df_filtered = df[~df['key'].isin(existing_data['key'])].copy()
                df_filtered = df_filtered.drop(columns=['key'])
            else:
                df_filtered = df
        except:
            df_filtered = df

        if df_filtered.empty:
            logger.info("No new data to insert")
            return True

        # Select only columns that match schema
        schema_cols = [field.name for field in schema]
        df_upload = df_filtered[[col for col in schema_cols if col in df_filtered.columns]]

        logger.info(f"Uploading {len(df_upload)} records with {len(df_upload.columns)} fields")

        job = client.load_table_from_dataframe(df_upload, table_ref, job_config=job_config)
        job.result()

        logger.info(f"Successfully uploaded {len(df_upload)} records")
        return True

    except Exception as e:
        logger.error(f"Error uploading to BigQuery: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main(request):
    """Main function - HTTP Cloud Function entry point"""

    logger.info("="*60)
    logger.info("Starting Hourly Crypto Data Fetch with Technical Indicators")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info("="*60)

    df = fetch_hourly_data()

    if df is not None and not df.empty:
        df = df.drop_duplicates(subset=['pair', 'timestamp'], keep='last')
        logger.info(f"Final record count: {len(df)} records")

        success = append_to_bigquery(df)

        if success:
            logger.info("Hourly data fetch with indicators completed successfully!")
            logger.info("="*60)
            return 'Hourly crypto data fetch completed successfully', 200
        else:
            logger.error("Failed to upload data to BigQuery")
            logger.info("="*60)
            return 'Failed to upload to BigQuery', 500
    else:
        logger.error("No data fetched from Kraken")
        logger.info("="*60)
        return 'No data fetched from Kraken', 500


def hourly_crypto_fetch(request):
    """Cloud Function entry point"""
    main()
    return 'Hourly crypto data fetch with indicators completed', 200


if __name__ == "__main__":
    main()
