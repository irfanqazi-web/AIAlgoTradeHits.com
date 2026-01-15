"""
Local API Server for Testing
Serves NVIDIA and Bitcoin data from BigQuery
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from google.cloud import bigquery
from google.cloud import storage
from datetime import datetime
import logging
import bcrypt
import hashlib
import secrets
import base64
import json
import math

# Import AI endpoints module
try:
    from ai_endpoints import register_ai_endpoints
    AI_ENDPOINTS_AVAILABLE = True
    print("AI endpoints module imported successfully")
except ImportError as e:
    AI_ENDPOINTS_AVAILABLE = False
    print(f"AI endpoints import failed: {e}")
except Exception as e:
    AI_ENDPOINTS_AVAILABLE = False
    print(f"AI endpoints import error: {e}")

# Import Walk-Forward Validation endpoints module
try:
    from walk_forward_endpoints import register_walk_forward_endpoints
    WALK_FORWARD_ENDPOINTS_AVAILABLE = True
    print("Walk-Forward endpoints module imported successfully")
except ImportError as e:
    WALK_FORWARD_ENDPOINTS_AVAILABLE = False
    print(f"Walk-Forward endpoints import failed: {e}")
except Exception as e:
    WALK_FORWARD_ENDPOINTS_AVAILABLE = False
    print(f"Walk-Forward endpoints import error: {e}")

# Helper function to sanitize float values for JSON (handle Infinity/NaN)
def safe_float(val):
    """Convert value to float, returning None for Infinity/NaN/None"""
    if val is None:
        return None
    try:
        f = float(val)
        if math.isinf(f) or math.isnan(f):
            return None
        return f
    except (ValueError, TypeError):
        return None


def sanitize_row(row):
    """Convert BigQuery row to dict with safe float handling"""
    row_dict = dict(row)
    for key, value in row_dict.items():
        if hasattr(value, 'isoformat'):
            row_dict[key] = value.isoformat()
        elif isinstance(value, float):
            row_dict[key] = safe_float(value)
    return row_dict

# Vertex AI imports
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Vertex AI not available - install google-cloud-aiplatform")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when module loads
logger.info("="*80)
logger.info("TRADING API MODULE LOADING")
logger.info("="*80)

# Configuration - Everything in aialgotradehits (unified project)
PROJECT_ID = 'aialgotradehits'
DATA_PROJECT_ID = PROJECT_ID
USER_PROJECT_ID = PROJECT_ID
DATASET_ID = 'crypto_trading_data'

# AI Training Configuration
TRAINING_BUCKET = 'aialgotradehits-training'
VERTEX_AI_LOCATION = 'us-central1'

# Dynamic model selection - Vertex AI compatible models (prioritize latest)
GEMINI_MODEL_PRIORITY = [
    "gemini-2.5-pro",                       # Latest Gemini 2.5 Pro
    "gemini-2.5-flash",                     # Latest Gemini 2.5 Flash
    "gemini-2.0-flash",                     # Gemini 2.0 Flash
    "gemini-1.5-pro",                       # Fallback to 1.5 Pro
    "gemini-1.5-flash",                     # Fallback to 1.5 Flash
]

# Initialize Storage client
storage_client = storage.Client(project=DATA_PROJECT_ID)

# Initialize Vertex AI with dynamic model selection
gemini_model = None
GEMINI_MODEL = None

if VERTEX_AI_AVAILABLE:
    try:
        vertexai.init(project=DATA_PROJECT_ID, location=VERTEX_AI_LOCATION)

        # Try models in priority order until one works
        for model_name in GEMINI_MODEL_PRIORITY:
            try:
                gemini_model = GenerativeModel(model_name)
                GEMINI_MODEL = model_name
                logger.info(f"Vertex AI initialized with model: {model_name}")
                break
            except Exception as model_error:
                logger.warning(f"Model {model_name} not available: {model_error}")
                continue

        if gemini_model is None:
            logger.error("No Gemini model available from priority list")
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI: {e}")
        gemini_model = None

# Initialize BigQuery client
client = bigquery.Client(project=DATA_PROJECT_ID)

app = Flask(__name__)

# Configure CORS to allow all origins with credentials
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False,
        "max_age": 3600
    }
})

# Register AI Trading Intelligence endpoints
logger.info(f"AI_ENDPOINTS_AVAILABLE: {AI_ENDPOINTS_AVAILABLE}")
if AI_ENDPOINTS_AVAILABLE:
    try:
        register_ai_endpoints(app, client, PROJECT_ID, DATASET_ID, VERTEX_AI_AVAILABLE,
                              GEMINI_MODEL, GEMINI_MODEL_PRIORITY, sanitize_row)
        logger.info("AI Trading Intelligence endpoints registered successfully")
    except Exception as e:
        logger.error(f"Failed to register AI endpoints: {e}")
        import traceback
        logger.error(traceback.format_exc())
else:
    logger.warning("AI endpoints module not available - AI endpoints will not be registered")

# Register Walk-Forward Validation endpoints
logger.info(f"WALK_FORWARD_ENDPOINTS_AVAILABLE: {WALK_FORWARD_ENDPOINTS_AVAILABLE}")
if WALK_FORWARD_ENDPOINTS_AVAILABLE:
    try:
        register_walk_forward_endpoints(app, client, PROJECT_ID, DATASET_ID, sanitize_row)
        logger.info("Walk-Forward Validation endpoints registered successfully")
    except Exception as e:
        logger.error(f"Failed to register Walk-Forward endpoints: {e}")
        import traceback
        logger.error(traceback.format_exc())
else:
    logger.warning("Walk-Forward endpoints module not available")

def get_stock_data_from_table(symbol, table_name, limit=500):
    """Fetch stock data from a specific BigQuery table (clean schema)"""
    order_direction = "DESC"

    # Query using clean table schema
    query = f"""
    SELECT
        symbol,
        datetime,
        open,
        high,
        low,
        close,
        volume,
        rsi,
        macd,
        macd_signal,
        macd_histogram,
        bollinger_upper,
        bollinger_middle,
        bollinger_lower,
        sma_20,
        sma_50,
        sma_200,
        ema_12,
        ema_26,
        ema_50,
        adx,
        atr,
        cci,
        williams_r,
        stoch_k,
        stoch_d,
        obv,
        momentum,
        roc
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    WHERE symbol = '{symbol}'
    ORDER BY datetime {order_direction}
    LIMIT {limit}
    """

    try:
        query_job = client.query(query)
        results = query_job.result()

        data = []
        for row in results:
            timestamp = None
            if row.datetime:
                if row.datetime.tzinfo is None:
                    from datetime import timezone as tz
                    dt_utc = row.datetime.replace(tzinfo=tz.utc)
                    timestamp = int(dt_utc.timestamp())
                else:
                    timestamp = int(row.datetime.timestamp())

            data.append({
                'symbol': row.symbol,
                'datetime': row.datetime.isoformat() if row.datetime else None,
                'timestamp': timestamp,
                'open': safe_float(row.open) if row.open else None,
                'high': safe_float(row.high) if row.high else None,
                'low': safe_float(row.low) if row.low else None,
                'close': safe_float(row.close) if row.close else None,
                'volume': safe_float(row.volume) if row.volume else None,
                'rsi': safe_float(row.rsi) if row.rsi else None,
                'macd': safe_float(row.macd) if row.macd else None,
                'macd_signal': safe_float(row.macd_signal) if row.macd_signal else None,
                'macd_histogram': safe_float(row.macd_histogram) if row.macd_histogram else None,
                'bb_upper': safe_float(row.bollinger_upper) if row.bollinger_upper else None,
                'bb_middle': safe_float(row.bollinger_middle) if row.bollinger_middle else None,
                'bb_lower': safe_float(row.bollinger_lower) if row.bollinger_lower else None,
                'sma_20': safe_float(row.sma_20) if row.sma_20 else None,
                'sma_50': safe_float(row.sma_50) if row.sma_50 else None,
                'sma_200': safe_float(row.sma_200) if row.sma_200 else None,
                'ema_12': safe_float(row.ema_12) if row.ema_12 else None,
                'ema_26': safe_float(row.ema_26) if row.ema_26 else None,
                'ema_50': safe_float(row.ema_50) if row.ema_50 else None,
                'adx': safe_float(row.adx) if row.adx else None,
                'atr': safe_float(row.atr) if row.atr else None,
                'cci': safe_float(row.cci) if row.cci else None,
                'williams_r': safe_float(row.williams_r) if row.williams_r else None,
                'stoch_k': safe_float(row.stoch_k) if row.stoch_k else None,
                'stoch_d': safe_float(row.stoch_d) if row.stoch_d else None,
                'obv': safe_float(row.obv) if row.obv else None,
                'momentum': safe_float(row.momentum) if row.momentum else None,
                'roc': safe_float(row.roc) if row.roc else None,
            })

        # Always reverse data to show most recent first
        data.reverse()

        logger.info(f"Fetched {len(data)} records for {symbol} from {table_name}")
        return data
    except Exception as e:
        logger.error(f"Error fetching stock data from {table_name}: {str(e)}")
        return []

def get_crypto_data_from_table(pair, table_name, limit=500):
    """Fetch crypto data from a specific BigQuery table (v2 schema)"""
    order_direction = "DESC" if table_name == "crypto_daily_clean" else "ASC"

    # For _clean tables, keep the slash format (BTC/USD); for v2 tables, remove slash
    if '_clean' in table_name:
        symbol = pair  # Keep "BTC/USD" format for clean tables
    else:
        symbol = pair.replace('/', '') if pair else pair  # Convert to "BTCUSD" for v2 tables

    # Query using v2 standardized field names (symbol instead of pair)
    query = f"""
    WITH ranked AS (
        SELECT
            symbol,
            name,
            datetime,
            open,
            high,
            low,
            close,
            volume,
            rsi,
            macd,
            macd_signal,
            macd_histogram,
            bollinger_upper,
            bollinger_middle,
            bollinger_lower,
            sma_20,
            sma_50,
            sma_200,
            ema_12,
            ema_26,
            ema_50,
            adx,
            atr,
            cci,
            williams_r,
            stoch_k,
            stoch_d,
            obv,
            momentum,
            roc,
            ROW_NUMBER() OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE symbol = '{symbol}'
    )
    SELECT * EXCEPT(rn) FROM ranked WHERE rn = 1
    ORDER BY datetime {order_direction}
    LIMIT {limit}
    """

    try:
        query_job = client.query(query)
        results = query_job.result()

        data = []
        for row in results:
            timestamp = None
            if row.datetime:
                if row.datetime.tzinfo is None:
                    from datetime import timezone as tz
                    dt_utc = row.datetime.replace(tzinfo=tz.utc)
                    timestamp = int(dt_utc.timestamp())
                else:
                    timestamp = int(row.datetime.timestamp())

            data.append({
                'pair': row.name if row.name else row.symbol,  # Use name as pair display
                'symbol': row.symbol,
                'datetime': row.datetime.isoformat() if row.datetime else None,
                'timestamp': timestamp,
                'open': safe_float(row.open) if row.open else None,
                'high': safe_float(row.high) if row.high else None,
                'low': safe_float(row.low) if row.low else None,
                'close': safe_float(row.close) if row.close else None,
                'volume': safe_float(row.volume) if row.volume else None,
                'rsi': safe_float(row.rsi) if row.rsi else None,
                'macd': safe_float(row.macd) if row.macd else None,
                'macd_signal': safe_float(row.macd_signal) if row.macd_signal else None,
                'macd_histogram': safe_float(row.macd_histogram) if row.macd_histogram else None,
                'bb_upper': safe_float(row.bollinger_upper) if row.bollinger_upper else None,
                'bb_middle': safe_float(row.bollinger_middle) if row.bollinger_middle else None,
                'bb_lower': safe_float(row.bollinger_lower) if row.bollinger_lower else None,
                'sma_20': safe_float(row.sma_20) if row.sma_20 else None,
                'sma_50': safe_float(row.sma_50) if row.sma_50 else None,
                'sma_200': safe_float(row.sma_200) if row.sma_200 else None,
                'ema_12': safe_float(row.ema_12) if row.ema_12 else None,
                'ema_26': safe_float(row.ema_26) if row.ema_26 else None,
                'ema_50': safe_float(row.ema_50) if row.ema_50 else None,
                'adx': safe_float(row.adx) if row.adx else None,
                'atr': safe_float(row.atr) if row.atr else None,
                'cci': safe_float(row.cci) if row.cci else None,
                'williams_r': safe_float(row.williams_r) if row.williams_r else None,
                'stoch_k': safe_float(row.stoch_k) if row.stoch_k else None,
                'stoch_d': safe_float(row.stoch_d) if row.stoch_d else None,
                'obv': safe_float(row.obv) if row.obv else None,
                'momentum': safe_float(row.momentum) if row.momentum else None,
                'roc': safe_float(row.roc) if row.roc else None,
            })

        if table_name == "crypto_daily_clean":
            data.reverse()

        logger.info(f"Fetched {len(data)} records for {pair} ({symbol}) from {table_name}")
        return data
    except Exception as e:
        logger.error(f"Error fetching crypto data from {table_name}: {str(e)}")
        return []

# API Routes
@app.route('/api/stocks/history', methods=['GET'])
def get_stock_daily():
    """Get stock daily data"""
    symbol = request.args.get('symbol', 'NVDA')
    limit = int(request.args.get('limit', 500))

    data = get_stock_data_from_table(symbol, 'stocks_daily_clean', limit)

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })

@app.route('/api/stocks/15min/history', methods=['GET'])
def get_stock_15min():
    """Get stock 15-minute data"""
    symbol = request.args.get('symbol', 'NVDA')
    limit = int(request.args.get('limit', 500))

    data = get_stock_data_from_table(symbol, 'stocks_daily_clean', limit)  # Using hourly as 15min alternative

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })

@app.route('/api/stocks/5min/history', methods=['GET'])
def get_stock_5min():
    """Get stock 5-minute data"""
    symbol = request.args.get('symbol', 'NVDA')
    limit = int(request.args.get('limit', 500))

    data = get_stock_data_from_table(symbol, 'stocks_5min_clean', limit)

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })

@app.route('/api/crypto/daily/history', methods=['GET'])
def get_crypto_daily():
    """Get crypto daily data"""
    pair = request.args.get('pair', 'BTC/USD')
    limit = int(request.args.get('limit', 500))

    data = get_crypto_data_from_table(pair, 'crypto_daily_clean', limit)

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })

@app.route('/api/crypto/15min/history', methods=['GET'])
def get_crypto_15min():
    """Get crypto 15-minute data"""
    pair = request.args.get('pair', 'BTC/USD')
    limit = int(request.args.get('limit', 500))

    data = get_crypto_data_from_table(pair, 'crypto_daily_clean', limit)  # Using daily clean data

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })

@app.route('/api/crypto/5min/history', methods=['GET'])
def get_crypto_5min():
    """Get crypto 5-minute data"""
    pair = request.args.get('pair', 'BTC/USD')
    limit = int(request.args.get('limit', 500))

    data = get_crypto_data_from_table(pair, 'crypto_daily_clean', limit)

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })

# ============== GENERIC ASSET DATA FUNCTION ==============

def get_twelvedata_asset_data(symbol, table_name, limit=500, id_column='symbol'):
    """Fetch data from TwelveData asset tables (forex, etfs, indices, commodities)
    These tables have different column naming convention from crypto/stock tables
    """
    # Remove slash from symbol if present (EUR/USD -> EURUSD)
    clean_symbol = symbol.replace('/', '')

    order_direction = "DESC"

    # TwelveData tables use different column names
    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    WHERE {id_column} = '{clean_symbol}'
    ORDER BY datetime {order_direction}
    LIMIT {limit}
    """

    try:
        query_job = client.query(query)
        results = query_job.result()

        data = []
        for row in results:
            row_dict = dict(row)

            # Convert datetime to Unix timestamp (seconds since epoch)
            timestamp = None
            dt = row_dict.get('datetime')
            if dt:
                if dt.tzinfo is None:
                    from datetime import timezone as tz
                    dt_utc = dt.replace(tzinfo=tz.utc)
                    timestamp = int(dt_utc.timestamp())
                else:
                    timestamp = int(dt.timestamp())

            # Build response with standardized field names for frontend compatibility
            row_data = {
                'symbol': row_dict.get(id_column) or row_dict.get('symbol'),
                'datetime': dt.isoformat() if dt else None,
                'timestamp': timestamp,
                'open': float(row_dict.get('open')) if row_dict.get('open') else None,
                'high': float(row_dict.get('high')) if row_dict.get('high') else None,
                'low': float(row_dict.get('low')) if row_dict.get('low') else None,
                'close': float(row_dict.get('close')) if row_dict.get('close') else None,
                'volume': float(row_dict.get('volume')) if row_dict.get('volume') else 0,
            }

            # Map TwelveData column names to standard names for frontend
            # RSI - try different naming conventions
            row_data['rsi'] = float(row_dict.get('rsi_14') or row_dict.get('rsi') or 0) if (row_dict.get('rsi_14') or row_dict.get('rsi')) else None

            # MACD
            row_data['macd'] = float(row_dict.get('macd_line') or row_dict.get('macd') or 0) if (row_dict.get('macd_line') or row_dict.get('macd')) else None
            row_data['macd_signal'] = float(row_dict.get('macd_signal') or 0) if row_dict.get('macd_signal') else None
            row_data['macd_histogram'] = float(row_dict.get('macd_histogram') or row_dict.get('macd_hist') or 0) if (row_dict.get('macd_histogram') or row_dict.get('macd_hist')) else None

            # Bollinger Bands
            row_data['bb_upper'] = float(row_dict.get('bbands_upper') or row_dict.get('bb_upper') or 0) if (row_dict.get('bbands_upper') or row_dict.get('bb_upper')) else None
            row_data['bb_middle'] = float(row_dict.get('bbands_middle') or row_dict.get('bb_middle') or 0) if (row_dict.get('bbands_middle') or row_dict.get('bb_middle')) else None
            row_data['bb_lower'] = float(row_dict.get('bbands_lower') or row_dict.get('bb_lower') or 0) if (row_dict.get('bbands_lower') or row_dict.get('bb_lower')) else None

            # SMAs
            row_data['sma_20'] = float(row_dict.get('sma_20') or 0) if row_dict.get('sma_20') else None
            row_data['sma_50'] = float(row_dict.get('sma_50') or 0) if row_dict.get('sma_50') else None
            row_data['sma_200'] = float(row_dict.get('sma_200') or 0) if row_dict.get('sma_200') else None

            # EMAs
            row_data['ema_12'] = float(row_dict.get('ema_12') or 0) if row_dict.get('ema_12') else None
            row_data['ema_26'] = float(row_dict.get('ema_26') or 0) if row_dict.get('ema_26') else None
            row_data['ema_50'] = float(row_dict.get('ema_50') or 0) if row_dict.get('ema_50') else None

            # Other indicators
            row_data['adx'] = float(row_dict.get('adx_14') or row_dict.get('adx') or 0) if (row_dict.get('adx_14') or row_dict.get('adx')) else None
            row_data['atr'] = float(row_dict.get('atr_14') or row_dict.get('atr') or 0) if (row_dict.get('atr_14') or row_dict.get('atr')) else None
            row_data['cci'] = float(row_dict.get('cci_14') or row_dict.get('cci') or 0) if (row_dict.get('cci_14') or row_dict.get('cci')) else None
            row_data['williams_r'] = float(row_dict.get('willr_14') or row_dict.get('williams_r') or 0) if (row_dict.get('willr_14') or row_dict.get('williams_r')) else None
            row_data['stoch_k'] = float(row_dict.get('stoch_k') or 0) if row_dict.get('stoch_k') else None
            row_data['stoch_d'] = float(row_dict.get('stoch_d') or 0) if row_dict.get('stoch_d') else None
            row_data['obv'] = float(row_dict.get('obv') or 0) if row_dict.get('obv') else None
            row_data['momentum'] = float(row_dict.get('mom_10') or row_dict.get('momentum') or 0) if (row_dict.get('mom_10') or row_dict.get('momentum')) else None
            row_data['roc'] = float(row_dict.get('roc_10') or row_dict.get('roc') or 0) if (row_dict.get('roc_10') or row_dict.get('roc')) else None

            data.append(row_data)

        # Reverse data to return chronological order
        data.reverse()

        logger.info(f"Fetched {len(data)} records for {clean_symbol} from {table_name}")
        return data
    except Exception as e:
        logger.error(f"Error fetching data from {table_name}: {str(e)}")
        return []


# ============== FOREX HISTORY ENDPOINTS ==============

@app.route('/api/forex/history', methods=['GET'])
def get_forex_daily():
    """Get forex daily data"""
    symbol = request.args.get('symbol', 'EURUSD')
    limit = int(request.args.get('limit', 500))

    data = get_twelvedata_asset_data(symbol, 'forex_daily_clean', limit, 'symbol')

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })


@app.route('/api/forex/hourly/history', methods=['GET'])
def get_forex_hourly():
    """Get forex hourly data"""
    symbol = request.args.get('symbol', 'EURUSD')
    limit = int(request.args.get('limit', 500))

    data = get_twelvedata_asset_data(symbol, 'v2_forex_hourly', limit, 'symbol')

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })


# ============== ETFs HISTORY ENDPOINTS ==============

@app.route('/api/etfs/history', methods=['GET'])
def get_etfs_daily():
    """Get ETF daily data"""
    symbol = request.args.get('symbol', 'SPY')
    limit = int(request.args.get('limit', 500))

    data = get_twelvedata_asset_data(symbol, 'etfs_daily_clean', limit, 'symbol')

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })


@app.route('/api/etfs/hourly/history', methods=['GET'])
def get_etfs_hourly():
    """Get ETF hourly data"""
    symbol = request.args.get('symbol', 'SPY')
    limit = int(request.args.get('limit', 500))

    data = get_twelvedata_asset_data(symbol, 'v2_etfs_hourly', limit, 'symbol')

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })


# ============== INDICES HISTORY ENDPOINTS ==============

@app.route('/api/indices/history', methods=['GET'])
def get_indices_daily():
    """Get indices daily data"""
    symbol = request.args.get('symbol', 'IXIC')
    limit = int(request.args.get('limit', 500))

    data = get_twelvedata_asset_data(symbol, 'indices_daily_clean', limit, 'symbol')

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })


@app.route('/api/indices/hourly/history', methods=['GET'])
def get_indices_hourly():
    """Get indices hourly data"""
    symbol = request.args.get('symbol', 'IXIC')
    limit = int(request.args.get('limit', 500))

    data = get_twelvedata_asset_data(symbol, 'v2_indices_hourly', limit, 'symbol')

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })


# ============== COMMODITIES HISTORY ENDPOINTS ==============

@app.route('/api/commodities/history', methods=['GET'])
def get_commodities_daily():
    """Get commodities daily data"""
    symbol = request.args.get('symbol', 'XAUUSD')
    limit = int(request.args.get('limit', 500))

    data = get_twelvedata_asset_data(symbol, 'v2_commodities_daily', limit, 'symbol')

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })


@app.route('/api/commodities/hourly/history', methods=['GET'])
def get_commodities_hourly():
    """Get commodities hourly data"""
    symbol = request.args.get('symbol', 'XAUUSD')
    limit = int(request.args.get('limit', 500))

    data = get_twelvedata_asset_data(symbol, 'v2_commodities_hourly', limit, 'symbol')

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })


# ============== INTEREST RATES HISTORY ENDPOINT ==============

@app.route('/api/interest-rates/history', methods=['GET'])
def get_interest_rates():
    """Get interest rates data"""
    country = request.args.get('symbol', 'US')
    limit = int(request.args.get('limit', 500))

    # Interest rates table - actual schema has: country, central_bank, rate_name, rate_value, currency, timeframe, timestamp, fetch_date, fetch_hour, source, g20_member, region
    query = f"""
    SELECT
        country,
        timestamp as datetime,
        rate_value as close,
        rate_value as open,
        rate_value as high,
        rate_value as low,
        0 as volume,
        central_bank,
        rate_name,
        currency
    FROM `{PROJECT_ID}.{DATASET_ID}.interest_rates`
    WHERE country LIKE '%{country}%'
    ORDER BY timestamp DESC
    LIMIT {limit}
    """

    try:
        query_job = client.query(query)
        results = query_job.result()

        data = []
        for row in results:
            timestamp = None
            if row.datetime:
                if row.datetime.tzinfo is None:
                    from datetime import timezone as tz
                    dt_utc = row.datetime.replace(tzinfo=tz.utc)
                    timestamp = int(dt_utc.timestamp())
                else:
                    timestamp = int(row.datetime.timestamp())

            data.append({
                'symbol': row.country,
                'datetime': row.datetime.isoformat() if row.datetime else None,
                'timestamp': timestamp,
                'open': safe_float(row.open) if row.open else None,
                'high': safe_float(row.high) if row.high else None,
                'low': safe_float(row.low) if row.low else None,
                'close': safe_float(row.close) if row.close else None,
                'volume': 0
            })

        data.reverse()

        logger.info(f"Fetched {len(data)} interest rate records for {country}")
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
    except Exception as e:
        logger.error(f"Error fetching interest rates: {str(e)}")
        return jsonify({'success': False, 'error': str(e), 'data': [], 'count': 0})


@app.route('/api/crypto/pairs', methods=['GET'])
def get_all_crypto_pairs():
    """Get all available crypto pairs with latest data from crypto_daily_clean table"""
    try:
        # Get the most recent data for each symbol
        query = f"""
        WITH latest_per_symbol AS (
            SELECT
                symbol,
                datetime,
                close,
                volume,
                rsi,
                macd,
                adx,
                roc,
                ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
        )
        SELECT symbol, datetime, close, volume, rsi, macd, adx, roc
        FROM latest_per_symbol
        WHERE rn = 1
        ORDER BY symbol ASC
        """

        query_job = client.query(query)
        results = list(query_job.result())

        pairs = []
        for row in results:
            pairs.append({
                'pair': row.symbol,
                'symbol': row.symbol,
                'name': row.symbol,
                'close': safe_float(row.close) if row.close else 0,
                'volume': safe_float(row.volume) if row.volume else 0,
                'rsi': safe_float(row.rsi) if row.rsi else None,
                'macd': safe_float(row.macd) if row.macd else None,
                'adx': safe_float(row.adx) if row.adx else None,
                'roc': safe_float(row.roc) if row.roc else 0,
                'datetime': row.datetime.isoformat() if row.datetime else None
            })

        logger.info(f"Fetched {len(pairs)} crypto pairs from crypto_daily_clean")
        return jsonify({
            'success': True,
            'data': pairs,
            'count': len(pairs)
        })
    except Exception as e:
        logger.error(f"Error fetching crypto pairs: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/symbols', methods=['GET'])
def get_all_stock_symbols():
    """Get all available stock symbols with latest data from stocks_daily table"""
    try:
        # Get the most recent data for each symbol
        query = f"""
        WITH latest_per_symbol AS (
            SELECT
                symbol,
                datetime,
                close,
                volume,
                rsi,
                macd,
                adx,
                roc,
                ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        )
        SELECT symbol, datetime, close, volume, rsi, macd, adx, roc
        FROM latest_per_symbol
        WHERE rn = 1
        ORDER BY symbol ASC
        """

        query_job = client.query(query)
        results = list(query_job.result())

        symbols = []
        for row in results:
            symbols.append({
                'symbol': row.symbol,
                'close': safe_float(row.close) if row.close else 0,
                'volume': safe_float(row.volume) if row.volume else 0,
                'rsi': safe_float(row.rsi) if row.rsi else None,
                'macd': safe_float(row.macd) if row.macd else None,
                'adx': safe_float(row.adx) if row.adx else None,
                'roc': safe_float(row.roc) if row.roc else 0,
                'datetime': row.datetime.isoformat() if row.datetime else None
            })

        logger.info(f"Fetched {len(symbols)} stock symbols from stocks_daily")
        # Return both formats for compatibility
        symbol_list = [s['symbol'] for s in symbols]
        return jsonify({
            'success': True,
            'data': symbols,
            'symbols': symbol_list,  # For DataReconciliation component
            'count': len(symbols)
        })
    except Exception as e:
        logger.error(f"Error fetching stock symbols: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stocks/reconciliation/<symbol>', methods=['GET'])
def get_stock_reconciliation(symbol):
    """Get complete stock data for reconciliation view"""
    try:
        limit = request.args.get('limit', 100, type=int)

        # Query all columns from stocks_daily_clean
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT {limit}
        """

        query_job = client.query(query)
        results = list(query_job.result())

        if not results:
            return jsonify({
                'success': True,
                'records': [],
                'columns': [],
                'stats': None
            })

        # Get column names from first row (BigQuery Row objects support dict conversion)
        columns = list(dict(results[0]).keys())

        # Convert to list of dicts
        records = []
        for row in results:
            row_dict = dict(row)
            record = {}
            for col in columns:
                val = row_dict.get(col)
                if hasattr(val, 'isoformat'):
                    record[col] = val.isoformat()
                elif val is not None:
                    record[col] = safe_float(val) if isinstance(val, (int, float)) else str(val)
                else:
                    record[col] = None
            records.append(record)

        # Calculate stats
        total_query = f"""
        SELECT
            COUNT(*) as total_records,
            MIN(datetime) as start_date,
            MAX(datetime) as end_date
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        WHERE symbol = '{symbol}'
        """
        stats_result = list(client.query(total_query).result())

        stats = {
            'symbol': symbol,
            'total_records': stats_result[0].total_records if stats_result else 0,
            'total_fields': len(columns),
            'date_range': {
                'start': stats_result[0].start_date.isoformat() if stats_result and stats_result[0].start_date else None,
                'end': stats_result[0].end_date.isoformat() if stats_result and stats_result[0].end_date else None
            },
            'latest_price': float(records[0].get('close', 0)) if records else None
        }

        return jsonify({
            'success': True,
            'records': records,
            'columns': columns,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"Error in stock reconciliation: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stocks/reconciliation/<symbol>/download', methods=['GET'])
def download_stock_reconciliation(symbol):
    """Download complete stock data as CSV with all 97 fields in schema order

    Optional query parameters:
    - start_date: Start date for filtering (YYYY-MM-DD format)
    - end_date: End date for filtering (YYYY-MM-DD format)
    - timeframe: daily (default), hourly, or 5min
    """
    try:
        import csv
        from io import StringIO
        import math
        from datetime import datetime as dt

        # Get optional parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        timeframe = request.args.get('timeframe', 'daily')

        # Determine table based on timeframe
        table_map = {
            'daily': 'stocks_daily_clean',
            'hourly': 'stocks_hourly_clean',
            '5min': 'stocks_5min_clean'
        }
        table_name = table_map.get(timeframe, 'stocks_daily_clean')

        # Define column order matching the schema design (97 fields)
        SCHEMA_COLUMN_ORDER = [
            'datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume',
            'previous_close', 'change', 'percent_change', 'high_low', 'pct_high_low',
            'week_52_high', 'week_52_low', 'average_volume', 'rsi', 'macd',
            'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'cci',
            'williams_r', 'momentum', 'sma_20', 'sma_50', 'sma_200', 'ema_12',
            'ema_20', 'ema_26', 'ema_50', 'ema_200', 'kama', 'bollinger_upper',
            'bollinger_middle', 'bollinger_lower', 'bb_width', 'adx', 'plus_di',
            'minus_di', 'atr', 'trix', 'roc', 'obv', 'pvo', 'ppo', 'ultimate_osc',
            'awesome_osc', 'log_return', 'return_2w', 'return_4w',
            'close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct',
            'rsi_slope', 'rsi_zscore', 'rsi_overbought', 'rsi_oversold',
            'macd_cross', 'ema20_slope', 'ema50_slope', 'atr_zscore', 'atr_slope',
            'volume_zscore', 'volume_ratio', 'pivot_high_flag', 'pivot_low_flag',
            'dist_to_pivot_high', 'dist_to_pivot_low', 'dist_to_pivot_high_pct', 'dist_to_pivot_low_pct',
            'trend_regime', 'vol_regime', 'regime_confidence', 'mfi', 'cmf', 'ichimoku_tenkan', 'ichimoku_kijun',
            'ichimoku_senkou_a', 'ichimoku_senkou_b', 'ichimoku_chikou',
            'vwap_daily', 'vwap_weekly', 'volume_profile_poc', 'volume_profile_vah',
            'volume_profile_val', 'name', 'sector', 'industry', 'asset_type',
            'exchange', 'mic_code', 'country', 'currency', 'type', 'timestamp',
            'data_source', 'created_at', 'updated_at'
        ]

        # Decimal columns to round to 2 places
        DECIMAL_COLUMNS = {
            'open', 'high', 'low', 'close', 'previous_close', 'change', 'percent_change',
            'high_low', 'pct_high_low', 'week_52_high', 'week_52_low', 'rsi', 'macd',
            'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'cci', 'williams_r',
            'momentum', 'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_20', 'ema_26',
            'ema_50', 'ema_200', 'kama', 'bollinger_upper', 'bollinger_middle',
            'bollinger_lower', 'bb_width', 'adx', 'plus_di', 'minus_di', 'atr', 'trix',
            'roc', 'pvo', 'ppo', 'ultimate_osc', 'awesome_osc', 'log_return',
            'return_2w', 'return_4w', 'close_vs_sma20_pct', 'close_vs_sma50_pct',
            'close_vs_sma200_pct', 'rsi_slope', 'rsi_zscore', 'ema20_slope',
            'ema50_slope', 'atr_zscore', 'atr_slope', 'volume_zscore', 'volume_ratio',
            'dist_to_pivot_high', 'dist_to_pivot_low', 'dist_to_pivot_high_pct', 'dist_to_pivot_low_pct',
            'regime_confidence', 'mfi', 'cmf',
            'ichimoku_tenkan', 'ichimoku_kijun', 'ichimoku_senkou_a', 'ichimoku_senkou_b',
            'ichimoku_chikou', 'vwap_daily', 'vwap_weekly', 'volume_profile_poc',
            'volume_profile_vah', 'volume_profile_val'
        }

        # Build query with optional date range filter
        date_filter = ""
        if start_date and end_date:
            date_filter = f" AND DATE(datetime) >= '{start_date}' AND DATE(datetime) <= '{end_date}'"
        elif start_date:
            date_filter = f" AND DATE(datetime) >= '{start_date}'"
        elif end_date:
            date_filter = f" AND DATE(datetime) <= '{end_date}'"

        # Query data for symbol with optional date filter (NO LIMIT - full download, latest first)
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE symbol = '{symbol}'{date_filter}
        ORDER BY datetime DESC
        """

        query_job = client.query(query)
        results = list(query_job.result())

        if not results:
            return Response("No data found", mimetype='text/plain', status=404)

        # Get available columns from data
        available_cols = set(dict(results[0]).keys())

        # Use schema order, only including columns that exist
        columns = [col for col in SCHEMA_COLUMN_ORDER if col in available_cols]

        # Add any extra columns not in schema order at the end
        extra_cols = [col for col in available_cols if col not in SCHEMA_COLUMN_ORDER]
        columns.extend(sorted(extra_cols))

        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)

        for row in results:
            row_dict = dict(row)
            row_data = []
            for col in columns:
                val = row_dict.get(col)
                if val is None:
                    row_data.append('')
                elif hasattr(val, 'isoformat'):
                    row_data.append(val.isoformat())
                elif col == 'timestamp' and isinstance(val, (int, float)):
                    row_data.append(dt.utcfromtimestamp(val).strftime('%Y-%m-%dT%H:%M:%S'))
                elif isinstance(val, float):
                    if math.isnan(val) or math.isinf(val):
                        row_data.append('')
                    elif col in DECIMAL_COLUMNS:
                        row_data.append(round(val, 2))
                    else:
                        row_data.append(val)
                else:
                    row_data.append(val)
            writer.writerow(row_data)

        csv_content = output.getvalue()

        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={symbol}_97_fields_complete.csv'}
        )

    except Exception as e:
        logger.error(f"Error downloading stock data: {str(e)}")
        return Response(str(e), mimetype='text/plain', status=500)




@app.route('/api/crypto/reconciliation/<path:symbol>/download', methods=['GET'])
def download_crypto_reconciliation(symbol):
    """Download complete crypto data as CSV with all 97 fields in schema order

    Optional query parameters:
    - start_date: Start date for filtering (YYYY-MM-DD format)
    - end_date: End date for filtering (YYYY-MM-DD format)
    - timeframe: daily (default), hourly, or 5min
    """
    try:
        import csv
        from io import StringIO
        import math
        from datetime import datetime as dt

        # Get optional parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        timeframe = request.args.get('timeframe', 'daily')

        # Determine table based on timeframe
        table_map = {
            'daily': 'crypto_daily_clean',
            'hourly': 'crypto_hourly_clean',
            '5min': 'crypto_5min_clean'
        }
        table_name = table_map.get(timeframe, 'crypto_daily_clean')

        SCHEMA_COLUMN_ORDER = [
            'datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume',
            'previous_close', 'change', 'percent_change', 'high_low', 'pct_high_low',
            'week_52_high', 'week_52_low', 'average_volume', 'rsi', 'macd',
            'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'cci',
            'williams_r', 'momentum', 'sma_20', 'sma_50', 'sma_200', 'ema_12',
            'ema_20', 'ema_26', 'ema_50', 'ema_200', 'kama', 'bollinger_upper',
            'bollinger_middle', 'bollinger_lower', 'bb_width', 'adx', 'plus_di',
            'minus_di', 'atr', 'trix', 'roc', 'obv', 'pvo', 'ppo', 'ultimate_osc',
            'awesome_osc', 'log_return', 'return_2w', 'return_4w',
            'close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct',
            'rsi_slope', 'rsi_zscore', 'rsi_overbought', 'rsi_oversold',
            'macd_cross', 'ema20_slope', 'ema50_slope', 'atr_zscore', 'atr_slope',
            'volume_zscore', 'volume_ratio', 'pivot_high_flag', 'pivot_low_flag',
            'dist_to_pivot_high', 'dist_to_pivot_low', 'dist_to_pivot_high_pct', 'dist_to_pivot_low_pct',
            'trend_regime', 'vol_regime', 'regime_confidence', 'mfi', 'cmf', 'ichimoku_tenkan', 'ichimoku_kijun',
            'ichimoku_senkou_a', 'ichimoku_senkou_b', 'ichimoku_chikou',
            'vwap_daily', 'vwap_weekly', 'volume_profile_poc', 'volume_profile_vah',
            'volume_profile_val', 'name', 'sector', 'industry', 'asset_type',
            'exchange', 'mic_code', 'country', 'currency', 'type', 'timestamp',
            'data_source', 'created_at', 'updated_at'
        ]

        DECIMAL_COLUMNS = {
            'open', 'high', 'low', 'close', 'previous_close', 'change', 'percent_change',
            'high_low', 'pct_high_low', 'week_52_high', 'week_52_low', 'rsi', 'macd',
            'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'cci', 'williams_r',
            'momentum', 'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_20', 'ema_26',
            'ema_50', 'ema_200', 'kama', 'bollinger_upper', 'bollinger_middle',
            'bollinger_lower', 'bb_width', 'adx', 'plus_di', 'minus_di', 'atr', 'trix',
            'roc', 'pvo', 'ppo', 'ultimate_osc', 'awesome_osc', 'log_return',
            'return_2w', 'return_4w', 'close_vs_sma20_pct', 'close_vs_sma50_pct',
            'close_vs_sma200_pct', 'rsi_slope', 'rsi_zscore', 'ema20_slope',
            'ema50_slope', 'atr_zscore', 'atr_slope', 'volume_zscore', 'volume_ratio',
            'dist_to_pivot_high', 'dist_to_pivot_low', 'dist_to_pivot_high_pct', 'dist_to_pivot_low_pct',
            'regime_confidence', 'mfi', 'cmf',
            'ichimoku_tenkan', 'ichimoku_kijun', 'ichimoku_senkou_a', 'ichimoku_senkou_b',
            'ichimoku_chikou', 'vwap_daily', 'vwap_weekly', 'volume_profile_poc',
            'volume_profile_vah', 'volume_profile_val'
        }

        # Build query with optional date range filter
        date_filter = ""
        if start_date and end_date:
            date_filter = f" AND DATE(datetime) >= '{start_date}' AND DATE(datetime) <= '{end_date}'"
        elif start_date:
            date_filter = f" AND DATE(datetime) >= '{start_date}'"
        elif end_date:
            date_filter = f" AND DATE(datetime) <= '{end_date}'"

        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE symbol = '{symbol}'{date_filter}
        ORDER BY datetime DESC
        """

        query_job = client.query(query)
        results = list(query_job.result())

        if not results:
            return Response('No data found', mimetype='text/plain', status=404)

        available_cols = set(dict(results[0]).keys())
        columns = [col for col in SCHEMA_COLUMN_ORDER if col in available_cols]
        extra_cols = [col for col in available_cols if col not in SCHEMA_COLUMN_ORDER]
        columns.extend(sorted(extra_cols))

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)

        for row in results:
            row_dict = dict(row)
            row_data = []
            for col in columns:
                val = row_dict.get(col)
                if val is None:
                    row_data.append('')
                elif hasattr(val, 'isoformat'):
                    row_data.append(val.isoformat())
                elif col == 'timestamp' and isinstance(val, (int, float)):
                    row_data.append(dt.utcfromtimestamp(val).strftime('%Y-%m-%dT%H:%M:%S'))
                elif isinstance(val, float):
                    if math.isnan(val) or math.isinf(val):
                        row_data.append('')
                    elif col in DECIMAL_COLUMNS:
                        row_data.append(round(val, 2))
                    else:
                        row_data.append(val)
                else:
                    row_data.append(val)
            writer.writerow(row_data)

        csv_content = output.getvalue()

        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={symbol}_crypto_97_fields_complete.csv'}
        )

    except Exception as e:
        logger.error(f'Error downloading crypto data: {str(e)}')
        return Response(str(e), mimetype='text/plain', status=500)


def _download_asset_reconciliation(symbol, asset_type, table_name, start_date=None, end_date=None, timeframe='daily'):
    """Generic download function for all asset types

    Args:
        symbol: Asset symbol to download
        asset_type: Type of asset (etf, forex, index, etc.)
        table_name: BigQuery table name (base name for daily)
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        timeframe: daily (default), hourly, or 5min
    """
    # Adjust table name based on timeframe
    if timeframe == 'hourly':
        table_name = table_name.replace('_daily', '_hourly')
    elif timeframe == '5min':
        table_name = table_name.replace('_daily', '_5min')
    import csv
    from io import StringIO
    import math
    from datetime import datetime as dt

    SCHEMA_COLUMN_ORDER = [
        'datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume',
        'previous_close', 'change', 'percent_change', 'high_low', 'pct_high_low',
        'week_52_high', 'week_52_low', 'average_volume', 'rsi', 'macd',
        'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'cci',
        'williams_r', 'momentum', 'sma_20', 'sma_50', 'sma_200', 'ema_12',
        'ema_20', 'ema_26', 'ema_50', 'ema_200', 'kama', 'bollinger_upper',
        'bollinger_middle', 'bollinger_lower', 'bb_width', 'adx', 'plus_di',
        'minus_di', 'atr', 'trix', 'roc', 'obv', 'pvo', 'ppo', 'ultimate_osc',
        'awesome_osc', 'log_return', 'return_2w', 'return_4w',
        'close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct',
        'rsi_slope', 'rsi_zscore', 'rsi_overbought', 'rsi_oversold',
        'macd_cross', 'ema20_slope', 'ema50_slope', 'atr_zscore', 'atr_slope',
        'volume_zscore', 'volume_ratio', 'pivot_high_flag', 'pivot_low_flag',
        'dist_to_pivot_high', 'dist_to_pivot_low', 'dist_to_pivot_high_pct', 'dist_to_pivot_low_pct',
        'trend_regime', 'vol_regime', 'regime_confidence', 'mfi', 'cmf', 'ichimoku_tenkan', 'ichimoku_kijun',
        'ichimoku_senkou_a', 'ichimoku_senkou_b', 'ichimoku_chikou',
        'vwap_daily', 'vwap_weekly', 'volume_profile_poc', 'volume_profile_vah',
        'volume_profile_val', 'name', 'sector', 'industry', 'asset_type',
        'exchange', 'mic_code', 'country', 'currency', 'type', 'timestamp',
        'data_source', 'created_at', 'updated_at'
    ]

    DECIMAL_COLUMNS = {
        'open', 'high', 'low', 'close', 'previous_close', 'change', 'percent_change',
        'high_low', 'pct_high_low', 'week_52_high', 'week_52_low', 'rsi', 'macd',
        'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'cci', 'williams_r',
        'momentum', 'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_20', 'ema_26',
        'ema_50', 'ema_200', 'kama', 'bollinger_upper', 'bollinger_middle',
        'bollinger_lower', 'bb_width', 'adx', 'plus_di', 'minus_di', 'atr', 'trix',
        'roc', 'pvo', 'ppo', 'ultimate_osc', 'awesome_osc', 'log_return',
        'return_2w', 'return_4w', 'close_vs_sma20_pct', 'close_vs_sma50_pct',
        'close_vs_sma200_pct', 'rsi_slope', 'rsi_zscore', 'ema20_slope',
        'ema50_slope', 'atr_zscore', 'atr_slope', 'volume_zscore', 'volume_ratio',
        'dist_to_pivot_high', 'dist_to_pivot_low', 'dist_to_pivot_high_pct', 'dist_to_pivot_low_pct',
        'regime_confidence', 'mfi', 'cmf',
        'ichimoku_tenkan', 'ichimoku_kijun', 'ichimoku_senkou_a', 'ichimoku_senkou_b',
        'ichimoku_chikou', 'vwap_daily', 'vwap_weekly', 'volume_profile_poc',
        'volume_profile_vah', 'volume_profile_val'
    }

    # Build query with optional date range filter
    date_filter = ""
    if start_date and end_date:
        date_filter = f" AND DATE(datetime) >= '{start_date}' AND DATE(datetime) <= '{end_date}'"
    elif start_date:
        date_filter = f" AND DATE(datetime) >= '{start_date}'"
    elif end_date:
        date_filter = f" AND DATE(datetime) <= '{end_date}'"

    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    WHERE symbol = '{symbol}'{date_filter}
    ORDER BY datetime DESC
    """

    query_job = client.query(query)
    results = list(query_job.result())

    if not results:
        return Response(f'No {asset_type} data found for {symbol}', mimetype='text/plain', status=404)

    available_cols = set(dict(results[0]).keys())
    columns = [col for col in SCHEMA_COLUMN_ORDER if col in available_cols]
    extra_cols = [col for col in available_cols if col not in SCHEMA_COLUMN_ORDER]
    columns.extend(sorted(extra_cols))

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)

    for row in results:
        row_dict = dict(row)
        row_data = []
        for col in columns:
            val = row_dict.get(col)
            if val is None:
                row_data.append('')
            elif hasattr(val, 'isoformat'):
                row_data.append(val.isoformat())
            elif col == 'timestamp' and isinstance(val, (int, float)):
                row_data.append(dt.utcfromtimestamp(val).strftime('%Y-%m-%dT%H:%M:%S'))
            elif isinstance(val, float):
                if math.isnan(val) or math.isinf(val):
                    row_data.append('')
                elif col in DECIMAL_COLUMNS:
                    row_data.append(round(val, 2))
                else:
                    row_data.append(val)
            else:
                row_data.append(val)
        writer.writerow(row_data)

    csv_content = output.getvalue()

    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={symbol}_{asset_type}_complete.csv'}
    )


@app.route('/api/etfs/reconciliation/<symbol>/download', methods=['GET'])
def download_etf_reconciliation(symbol):
    """Download complete ETF data as CSV with optional date and timeframe filtering

    Optional query parameters:
    - start_date: Start date for filtering (YYYY-MM-DD format)
    - end_date: End date for filtering (YYYY-MM-DD format)
    - timeframe: daily (default), hourly, or 5min
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        timeframe = request.args.get('timeframe', 'daily')
        return _download_asset_reconciliation(symbol, 'etf', 'v2_etfs_daily', start_date, end_date, timeframe)
    except Exception as e:
        logger.error(f'Error downloading ETF data: {str(e)}')
        return Response(str(e), mimetype='text/plain', status=500)


@app.route('/api/forex/reconciliation/<path:symbol>/download', methods=['GET'])
def download_forex_reconciliation(symbol):
    """Download complete forex data as CSV with optional date and timeframe filtering

    Optional query parameters:
    - start_date: Start date for filtering (YYYY-MM-DD format)
    - end_date: End date for filtering (YYYY-MM-DD format)
    - timeframe: daily (default), hourly, or 5min
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        timeframe = request.args.get('timeframe', 'daily')
        return _download_asset_reconciliation(symbol, 'forex', 'v2_forex_daily', start_date, end_date, timeframe)
    except Exception as e:
        logger.error(f'Error downloading forex data: {str(e)}')
        return Response(str(e), mimetype='text/plain', status=500)


@app.route('/api/indices/reconciliation/<symbol>/download', methods=['GET'])
def download_indices_reconciliation(symbol):
    """Download complete indices data as CSV with optional date and timeframe filtering

    Optional query parameters:
    - start_date: Start date for filtering (YYYY-MM-DD format)
    - end_date: End date for filtering (YYYY-MM-DD format)
    - timeframe: daily (default), hourly, or 5min
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        timeframe = request.args.get('timeframe', 'daily')
        return _download_asset_reconciliation(symbol, 'index', 'v2_indices_daily', start_date, end_date, timeframe)
    except Exception as e:
        logger.error(f'Error downloading indices data: {str(e)}')
        return Response(str(e), mimetype='text/plain', status=500)


@app.route('/api/commodities/reconciliation/<symbol>/download', methods=['GET'])
def download_commodities_reconciliation(symbol):
    """Download complete commodities data as CSV with optional date and timeframe filtering

    Optional query parameters:
    - start_date: Start date for filtering (YYYY-MM-DD format)
    - end_date: End date for filtering (YYYY-MM-DD format)
    - timeframe: daily (default), hourly, or 5min
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        timeframe = request.args.get('timeframe', 'daily')
        return _download_asset_reconciliation(symbol, 'commodity', 'v2_commodities_daily', start_date, end_date, timeframe)
    except Exception as e:
        logger.error(f'Error downloading commodities data: {str(e)}')
        return Response(str(e), mimetype='text/plain', status=500)


@app.route('/api/interest_rates/reconciliation/<symbol>/download', methods=['GET'])
def download_interest_rates_reconciliation(symbol):
    """Download complete interest rates data as CSV with optional date and timeframe filtering

    Optional query parameters:
    - start_date: Start date for filtering (YYYY-MM-DD format)
    - end_date: End date for filtering (YYYY-MM-DD format)
    - timeframe: daily (default), hourly, or 5min
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        timeframe = request.args.get('timeframe', 'daily')
        return _download_asset_reconciliation(symbol, 'interest_rate', 'v2_interest_rates_daily', start_date, end_date, timeframe)
    except Exception as e:
        logger.error(f'Error downloading interest rates data: {str(e)}')
        return Response(str(e), mimetype='text/plain', status=500)


@app.route('/api/summary/stock', methods=['GET'])
def get_stock_summary():
    """Get stock market summary"""
    # For now, just return NVDA data since we only have one stock
    query = f"""
    SELECT
        symbol,
        close,
        rsi,
        macd,
        adx,
        volume,
        roc,
        datetime
    FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
    WHERE symbol = 'NVDA'
    ORDER BY datetime DESC
    LIMIT 1
    """

    try:
        query_job = client.query(query)
        results = list(query_job.result())

        if results:
            row = results[0]
            nvda_data = {
                'symbol': row.symbol,
                'close': safe_float(row.close) if row.close else 0,
                'rsi': safe_float(row.rsi) if row.rsi else 0,
                'macd': safe_float(row.macd) if row.macd else 0,
                'adx': safe_float(row.adx) if row.adx else 0,
                'volume': safe_float(row.volume) if row.volume else 0,
                'roc': safe_float(row.roc) if row.roc else 0,
                'datetime': row.datetime.isoformat() if row.datetime else None
            }

            return jsonify({
                'success': True,
                'summary': {
                    'top_gainers': [nvda_data],
                    'top_losers': [],
                    'highest_volume': [nvda_data],
                    'total_pairs': 1
                }
            })
        else:
            return jsonify({
                'success': True,
                'summary': {
                    'top_gainers': [],
                    'top_losers': [],
                    'highest_volume': [],
                    'total_pairs': 0
                }
            })
    except Exception as e:
        logger.error(f"Error fetching stock summary: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/summary/crypto', methods=['GET'])
def get_crypto_summary():
    """Get crypto market summary"""
    # For now, just return BTC data since we only have one crypto
    query = f"""
    SELECT
        pair,
        close,
        rsi,
        macd,
        adx,
        volume,
        roc,
        datetime
    FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
    WHERE pair = 'BTC/USD'
    ORDER BY datetime DESC
    LIMIT 1
    """

    try:
        query_job = client.query(query)
        results = list(query_job.result())

        if results:
            row = results[0]
            btc_data = {
                'pair': row.pair,
                'close': safe_float(row.close) if row.close else 0,
                'rsi': safe_float(row.rsi) if row.rsi else 0,
                'macd': safe_float(row.macd) if row.macd else 0,
                'adx': safe_float(row.adx) if row.adx else 0,
                'volume': safe_float(row.volume) if row.volume else 0,
                'roc': safe_float(row.roc) if row.roc else 0,
                'datetime': row.datetime.isoformat() if row.datetime else None
            }

            return jsonify({
                'success': True,
                'summary': {
                    'top_gainers': [btc_data],
                    'top_losers': [],
                    'highest_volume': [btc_data],
                    'total_pairs': 1
                }
            })
        else:
            return jsonify({
                'success': True,
                'summary': {
                    'top_gainers': [],
                    'top_losers': [],
                    'highest_volume': [],
                    'total_pairs': 0
                }
            })
    except Exception as e:
        logger.error(f"Error fetching crypto summary: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """User login endpoint"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Query user from BigQuery
        query = f"""
        SELECT user_id, email, username, subscription_tier, password_hash, first_login_completed, account_status
        FROM `{PROJECT_ID}.{DATASET_ID}.users`
        WHERE email = @email
        LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("email", "STRING", email)
            ]
        )

        query_job = client.query(query, job_config=job_config)
        results = list(query_job.result())

        if not results:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

        user = results[0]

        # Verify password using bcrypt
        try:
            password_valid = bcrypt.checkpw(
                password.encode('utf-8'),
                user.password_hash.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            password_valid = False

        if not password_valid:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

        # Generate simple token
        token = hashlib.sha256(f"{email}{secrets.token_hex(16)}".encode()).hexdigest()

        return jsonify({
            'success': True,
            'user': {
                'user_id': user.user_id,
                'email': user.email,
                'name': user.username,
                'role': user.subscription_tier,
                'subscription_tier': user.subscription_tier,
                'account_status': user.account_status,
                'token': token,
                'first_login_completed': user.first_login_completed
            }
        })
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/verify', methods=['GET', 'OPTIONS'])
def verify_token():
    """Verify authentication token"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # For now, just return success (in production verify JWT)
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'No token provided'}), 401

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/change-password', methods=['POST', 'OPTIONS'])
def change_password():
    """Change user password"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401

        # For now, just return success (in production implement proper password change)
        return jsonify({'success': True, 'message': 'Password changed successfully'})
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users', methods=['GET', 'OPTIONS'])
def get_users():
    """Get all users (admin only)"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        query = f"""
        SELECT user_id, email, username, subscription_tier, created_at, account_status, first_login_completed
        FROM `{PROJECT_ID}.{DATASET_ID}.users`
        ORDER BY created_at DESC
        """

        query_job = client.query(query)
        results = query_job.result()

        users = []
        for row in results:
            users.append({
                'user_id': row.user_id,
                'email': row.email,
                'name': row.username,
                'role': row.subscription_tier,
                'subscription_tier': row.subscription_tier,
                'status': row.account_status,
                'first_login_completed': row.first_login_completed,
                'created_at': row.created_at.isoformat() if row.created_at else None
            })

        return jsonify({'success': True, 'users': users})
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/available-symbols', methods=['GET'])
def get_available_symbols():
    """Get all available symbols for download, grouped by asset type"""
    try:
        # Query all unique symbols from each asset type table
        asset_queries = {
            'stocks': f"SELECT DISTINCT symbol, name, sector FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean` ORDER BY symbol",
            'crypto': f"SELECT DISTINCT symbol, name FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean` ORDER BY symbol",
            'etfs': f"SELECT DISTINCT symbol, name FROM `{PROJECT_ID}.{DATASET_ID}.v2_etfs_daily` ORDER BY symbol",
            'forex': f"SELECT DISTINCT symbol FROM `{PROJECT_ID}.{DATASET_ID}.v2_forex_daily` ORDER BY symbol",
            'indices': f"SELECT DISTINCT symbol FROM `{PROJECT_ID}.{DATASET_ID}.v2_indices_daily` ORDER BY symbol",
            'commodities': f"SELECT DISTINCT symbol FROM `{PROJECT_ID}.{DATASET_ID}.v2_commodities_daily` ORDER BY symbol",
        }

        result = {}
        total_symbols = 0

        for asset_type, query in asset_queries.items():
            try:
                query_job = client.query(query)
                rows = list(query_job.result())
                symbols = []
                for row in rows:
                    sym_data = {'symbol': row.symbol}
                    if hasattr(row, 'name') and row.name:
                        sym_data['name'] = row.name
                    if hasattr(row, 'sector') and row.sector:
                        sym_data['sector'] = row.sector
                    symbols.append(sym_data)
                result[asset_type] = {
                    'count': len(symbols),
                    'symbols': symbols
                }
                total_symbols += len(symbols)
            except Exception as e:
                logger.warning(f"Error fetching {asset_type} symbols: {e}")
                result[asset_type] = {'count': 0, 'symbols': [], 'error': str(e)}

        return jsonify({
            'success': True,
            'total_symbols': total_symbols,
            'asset_types': result,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error fetching available symbols: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


@app.route('/', methods=['GET'])
def root():
    """Root endpoint - API welcome page"""
    return jsonify({
        'name': 'AIAlgoTradeHits Trading API',
        'version': '2.0.0',
        'status': 'active',
        'description': 'AI-powered trading data platform with Gemini 2.5 Pro integration',
        'documentation': '/api/endpoints',
        'health': '/health',
        'endpoints': {
            'stocks': {
                'history': '/api/stocks/history?symbol=NVDA&limit=30',
                'symbols': '/api/stocks/symbols',
                '15min': '/api/stocks/15min/history?symbol=NVDA',
                '5min': '/api/stocks/5min/history?symbol=NVDA',
            },
            'crypto': {
                'daily': '/api/crypto/daily/history?symbol=BTC&limit=30',
                'pairs': '/api/crypto/pairs',
                '15min': '/api/crypto/15min/history?symbol=BTC',
                '5min': '/api/crypto/5min/history?symbol=BTC',
            },
            'ai': {
                'capabilities': '/api/ai/capabilities',
            },
            'finnhub': {
                'news': '/api/finnhub/news?category=all',
                'recommendations': '/api/finnhub/recommendations?symbol=AAPL',
                'insider_transactions': '/api/finnhub/insider-transactions?symbol=AAPL',
                'company_news': '/api/finnhub/company-news?symbol=AAPL',
            },
            'nlp': {
                'search': '/api/nlp/search?q=show%20me%20top%20stocks',
            },
            'analysis': {
                'stocks_weekly': '/api/analysis/stocks/weekly',
                'cryptos_weekly': '/api/analysis/cryptos/weekly',
            },
        },
        'powered_by': ['Google Cloud Platform', 'Vertex AI', 'Gemini 2.5 Pro', 'BigQuery'],
        'data_sources': ['TwelveData', 'Finnhub', 'CoinMarketCap'],
        'timestamp': datetime.utcnow().isoformat()
    })


# ============== ADMIN SCHEDULER MONITORING ENDPOINTS ==============

@app.route('/api/admin/scheduler-status', methods=['GET'])
def get_scheduler_status():
    """Get scheduler status and recent execution logs"""
    try:
        client = bigquery.Client(project=PROJECT_ID)

        # Get scheduler summary from the view
        summary_query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.scheduler_summary_view`
        ORDER BY scheduler_name
        """

        schedulers = []
        try:
            summary_results = client.query(summary_query).result()
            for row in summary_results:
                schedulers.append({
                    'scheduler_name': row.scheduler_name,
                    'function_name': row.function_name,
                    'table_name': row.table_name,
                    'last_execution_time': row.last_execution_time.isoformat() if row.last_execution_time else None,
                    'last_status': row.last_status,
                    'last_duration_minutes': safe_float(row.last_duration_minutes) if row.last_duration_minutes else None,
                    'total_executions_30d': row.total_executions_30d,
                    'successful_runs_30d': row.successful_runs_30d,
                    'failed_runs_30d': row.failed_runs_30d,
                    'avg_duration_minutes': safe_float(row.avg_duration_minutes) if row.avg_duration_minutes else None,
                    'total_records_inserted_30d': row.total_records_inserted_30d
                })
        except Exception as e:
            logger.warning(f"Could not query scheduler summary view: {e}")

        # Get recent execution logs
        logs_query = f"""
        SELECT
            scheduler_name,
            function_name,
            table_name,
            start_time,
            end_time,
            status,
            duration_seconds,
            total_symbols,
            successful_symbols,
            failed_symbols,
            records_inserted,
            error_message
        FROM `{PROJECT_ID}.{DATASET_ID}.scheduler_execution_log`
        WHERE execution_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
        ORDER BY start_time DESC
        LIMIT 50
        """

        recent_executions = []
        try:
            logs_results = client.query(logs_query).result()
            for row in logs_results:
                recent_executions.append({
                    'scheduler_name': row.scheduler_name,
                    'function_name': row.function_name,
                    'table_name': row.table_name,
                    'start_time': row.start_time.isoformat() if row.start_time else None,
                    'end_time': row.end_time.isoformat() if row.end_time else None,
                    'status': row.status,
                    'duration_seconds': safe_float(row.duration_seconds) if row.duration_seconds else None,
                    'total_symbols': row.total_symbols,
                    'successful_symbols': row.successful_symbols,
                    'failed_symbols': row.failed_symbols,
                    'records_inserted': row.records_inserted,
                    'error_message': row.error_message
                })
        except Exception as e:
            logger.warning(f"Could not query scheduler execution log: {e}")

        return jsonify({
            'success': True,
            'schedulers': schedulers,
            'recent_executions': recent_executions
        })

    except Exception as e:
        logger.error(f"Get scheduler status error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/trigger-scheduler', methods=['POST'])
def trigger_scheduler():
    """Manually trigger a scheduler by calling its Cloud Function"""
    try:
        data = request.get_json()
        scheduler_name = data.get('scheduler_name')

        if not scheduler_name:
            return jsonify({'success': False, 'error': 'scheduler_name is required'}), 400

        # Map scheduler names to Cloud Function URLs
        scheduler_urls = {
            'daily-crypto-fetcher': 'https://daily-crypto-fetcher-252370699783.us-central1.run.app',
            'hourly-crypto-fetcher': 'https://hourly-crypto-fetcher-252370699783.us-central1.run.app',
            'fivemin-top10-fetcher': 'https://fivemin-top10-fetcher-252370699783.us-central1.run.app',
            'daily-stock-fetcher': 'https://daily-stock-fetcher-252370699783.us-central1.run.app',
            'hourly-stock-fetcher': 'https://hourly-stock-fetcher-252370699783.us-central1.run.app',
            'fivemin-stock-fetcher': 'https://fivemin-stock-fetcher-252370699783.us-central1.run.app',
            'weekly-stock-fetcher': 'https://weekly-stock-fetcher-252370699783.us-central1.run.app',
            'weekly-crypto-fetcher': 'https://weekly-crypto-fetcher-252370699783.us-central1.run.app',
            'weekly-etf-fetcher': 'https://weekly-etf-fetcher-252370699783.us-central1.run.app',
            'weekly-forex-fetcher': 'https://weekly-forex-fetcher-252370699783.us-central1.run.app',
            'weekly-indices-fetcher': 'https://weekly-indices-fetcher-252370699783.us-central1.run.app',
            'weekly-commodities-fetcher': 'https://weekly-commodities-fetcher-252370699783.us-central1.run.app'
        }

        if scheduler_name not in scheduler_urls:
            return jsonify({'success': False, 'error': f'Unknown scheduler: {scheduler_name}'}), 400

        url = scheduler_urls[scheduler_name] + '?manual=true'

        import requests
        response = requests.get(url, timeout=30)

        return jsonify({
            'success': True,
            'message': f'Scheduler {scheduler_name} triggered',
            'response_code': response.status_code,
            'response_text': response.text[:200]
        })

    except Exception as e:
        logger.error(f"Trigger scheduler error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============== ANALYSIS ENDPOINTS ==============

@app.route('/api/analysis/stocks/weekly', methods=['GET'])
def get_weekly_stocks():
    """Get weekly stock analysis data with filters"""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        limit = request.args.get('limit', 100, type=int)
        sector = request.args.get('sector')
        volatility = request.args.get('volatility_category')
        market_cap = request.args.get('market_cap_category')

        where_clauses = []
        if sector:
            where_clauses.append(f"sector = '{sector}'")
        if volatility:
            where_clauses.append(f"volatility_category = '{volatility}'")
        if market_cap:
            where_clauses.append(f"market_cap_category = '{market_cap}'")

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        {where_sql}
        ORDER BY close DESC NULLS LAST
        LIMIT {limit}
        """

        results = client.query(query).result()
        data = [sanitize_row(row) for row in results]

        return jsonify({'success': True, 'data': data, 'count': len(data)})

    except Exception as e:
        logger.error(f"Get weekly stocks error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analysis/cryptos/weekly', methods=['GET'])
def get_weekly_cryptos():
    """Get weekly crypto analysis data with filters"""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        limit = request.args.get('limit', 100, type=int)
        category = request.args.get('category')
        volatility = request.args.get('volatility_category')

        where_clauses = []
        if category:
            where_clauses.append(f"category = '{category}'")
        if volatility:
            where_clauses.append(f"volatility_category = '{volatility}'")

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
        {where_sql}
        ORDER BY close DESC NULLS LAST
        LIMIT {limit}
        """

        results = client.query(query).result()
        data = [sanitize_row(row) for row in results]

        return jsonify({'success': True, 'data': data, 'count': len(data)})

    except Exception as e:
        logger.error(f"Get weekly cryptos error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analysis/etfs/weekly', methods=['GET'])
def get_weekly_etfs():
    """Get weekly ETF analysis data with filters"""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        limit = request.args.get('limit', 100, type=int)
        country = request.args.get('country')
        exchange = request.args.get('exchange')

        where_clauses = []
        if country:
            where_clauses.append(f"country = '{country}'")
        if exchange:
            where_clauses.append(f"exchange = '{exchange}'")

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.etfs_daily_clean`
        {where_sql}
        ORDER BY close DESC NULLS LAST
        LIMIT {limit}
        """

        results = client.query(query).result()
        data = [sanitize_row(row) for row in results]

        return jsonify({'success': True, 'data': data, 'count': len(data)})

    except Exception as e:
        logger.error(f"Get weekly ETFs error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analysis/forex/weekly', methods=['GET'])
def get_weekly_forex():
    """Get weekly Forex analysis data with filters"""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        limit = request.args.get('limit', 100, type=int)
        category = request.args.get('category')
        volatility = request.args.get('volatility_category')
        base_currency = request.args.get('base_currency')

        where_clauses = []
        if category:
            where_clauses.append(f"category = '{category}'")
        if volatility:
            where_clauses.append(f"volatility_category = '{volatility}'")
        if base_currency:
            where_clauses.append(f"base_currency = '{base_currency}'")

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.forex_daily_clean`
        {where_sql}
        ORDER BY close DESC NULLS LAST
        LIMIT {limit}
        """

        results = client.query(query).result()
        data = [sanitize_row(row) for row in results]

        return jsonify({'success': True, 'data': data, 'count': len(data)})

    except Exception as e:
        logger.error(f"Get weekly Forex error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analysis/indices/weekly', methods=['GET'])
def get_weekly_indices():
    """Get weekly Indices analysis data with filters"""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        limit = request.args.get('limit', 100, type=int)
        region = request.args.get('region')
        volatility = request.args.get('volatility_category')
        country = request.args.get('country')

        where_clauses = []
        if region:
            where_clauses.append(f"region = '{region}'")
        if volatility:
            where_clauses.append(f"volatility_category = '{volatility}'")
        if country:
            where_clauses.append(f"country = '{country}'")

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.indices_daily_clean`
        {where_sql}
        ORDER BY close DESC NULLS LAST
        LIMIT {limit}
        """

        results = client.query(query).result()
        data = [sanitize_row(row) for row in results]

        return jsonify({'success': True, 'data': data, 'count': len(data)})

    except Exception as e:
        logger.error(f"Get weekly Indices error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analysis/commodities/weekly', methods=['GET'])
def get_weekly_commodities():
    """Get weekly Commodities analysis data with filters"""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        limit = request.args.get('limit', 100, type=int)
        category = request.args.get('category')
        volatility = request.args.get('volatility_category')
        subcategory = request.args.get('subcategory')

        where_clauses = []
        if category:
            where_clauses.append(f"category = '{category}'")
        if volatility:
            where_clauses.append(f"volatility_category = '{volatility}'")
        if subcategory:
            where_clauses.append(f"subcategory = '{subcategory}'")

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.commodities_daily_clean`
        {where_sql}
        ORDER BY close DESC NULLS LAST
        LIMIT {limit}
        """

        results = client.query(query).result()
        data = [sanitize_row(row) for row in results]

        return jsonify({'success': True, 'data': data, 'count': len(data)})

    except Exception as e:
        logger.error(f"Get weekly Commodities error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============== TWELVEDATA UNIFIED ENDPOINT ==============

@app.route('/api/twelvedata/<asset_type>/<timeframe>', methods=['GET'])
def get_twelvedata(asset_type, timeframe):
    """
    Unified endpoint for all 7 asset types from TwelveData
    Asset types: stocks, crypto, forex, etfs, indices, commodities, interest_rates
    Timeframes: weekly, daily, hourly, 5min
    """
    try:
        client = bigquery.Client(project=PROJECT_ID)
        limit = request.args.get('limit', 100, type=int)

        # Map asset types to table names and identifier column (using v2 standardized tables)
        table_config = {
            'stocks': {
                'weekly': ('stocks_daily_clean', 'symbol'),
                'daily': ('stocks_daily_clean', 'symbol'),
                'hourly': ('stocks_daily_clean', 'symbol'),
                '5min': ('stocks_5min_clean', 'symbol')
            },
            'crypto': {
                'weekly': ('crypto_daily_clean', 'symbol'),
                'daily': ('crypto_daily_clean', 'symbol'),
                'hourly': ('crypto_daily_clean', 'symbol'),
                '5min': ('crypto_daily_clean', 'symbol')
            },
            'forex': {
                'weekly': ('forex_daily_clean', 'symbol'),
                'daily': ('forex_daily_clean', 'symbol'),
                'hourly': ('v2_forex_hourly', 'symbol'),
                '5min': ('v2_forex_5min', 'symbol')
            },
            'etfs': {
                'weekly': ('etfs_daily_clean', 'symbol'),
                'daily': ('etfs_daily_clean', 'symbol'),
                'hourly': ('v2_etfs_hourly', 'symbol'),
                '5min': ('v2_etfs_5min', 'symbol')
            },
            'indices': {
                'weekly': ('indices_daily_clean', 'symbol'),
                'daily': ('indices_daily_clean', 'symbol'),
                'hourly': ('v2_indices_hourly', 'symbol'),
                '5min': ('v2_indices_5min', 'symbol')
            },
            'commodities': {
                'weekly': ('commodities_daily_clean', 'symbol'),
                'daily': ('commodities_daily_clean', 'symbol'),
                'hourly': ('v2_commodities_hourly', 'symbol'),
                '5min': ('v2_commodities_5min', 'symbol')
            },
            'interest_rates': {
                'weekly': ('interest_rates', 'country'),
                'daily': ('interest_rates', 'country'),
                'hourly': ('interest_rates', 'country'),
                '5min': ('interest_rates', 'country')
            }
        }

        if asset_type not in table_config:
            return jsonify({'success': False, 'error': f'Unknown asset type: {asset_type}'}), 400

        if timeframe not in table_config[asset_type]:
            return jsonify({'success': False, 'error': f'Unknown timeframe: {timeframe}'}), 400

        table_name, id_column = table_config[asset_type][timeframe]

        # Interest rates uses 'timestamp' column, all others use 'datetime'
        order_column = 'timestamp' if asset_type == 'interest_rates' else 'datetime'

        # Build query to get UNIQUE symbols with their LATEST data
        # Uses ROW_NUMBER to pick the most recent row per symbol
        query = f"""
        WITH ranked AS (
            SELECT *,
                ROW_NUMBER() OVER (PARTITION BY {id_column} ORDER BY {order_column} DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        )
        SELECT * EXCEPT(rn)
        FROM ranked
        WHERE rn = 1
        ORDER BY {id_column}
        LIMIT {limit}
        """

        results = client.query(query).result()
        data = []
        for row in results:
            row_dict = dict(row)
            # Convert datetime objects to ISO strings and handle Infinity/NaN
            for key, value in row_dict.items():
                if hasattr(value, 'isoformat'):
                    row_dict[key] = value.isoformat()
                elif isinstance(value, float):
                    row_dict[key] = safe_float(value)
            data.append(row_dict)

        return jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'asset_type': asset_type,
            'timeframe': timeframe,
            'table': table_name
        })

    except Exception as e:
        logger.error(f"Get twelvedata {asset_type}/{timeframe} error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/twelvedata/<asset_type>/<timeframe>/history', methods=['GET'])
def get_twelvedata_history(asset_type, timeframe):
    """
    Get historical OHLCV data for a specific symbol
    Used for pattern recognition and chart analysis
    """
    from decimal import Decimal
    try:
        client = bigquery.Client(project=PROJECT_ID)
        symbol = request.args.get('symbol', '')
        limit = request.args.get('limit', 100, type=int)
        limit = min(limit, 500)  # Cap at 500 rows

        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol parameter required'}), 400

        # Map asset types to table names (using v2 standardized tables)
        table_config = {
            'stocks': {
                'weekly': 'stocks_daily_clean',
                'daily': 'stocks_daily_clean',
                'hourly': 'stocks_daily_clean',
                '5min': 'stocks_5min_clean'
            },
            'crypto': {
                'weekly': 'crypto_daily_clean',
                'daily': 'crypto_daily_clean',
                'hourly': 'crypto_daily_clean',
                '5min': 'crypto_daily_clean'
            },
            'forex': {
                'weekly': 'forex_daily_clean',
                'daily': 'forex_daily_clean',
                'hourly': 'v2_forex_hourly',
                '5min': 'v2_forex_5min'
            },
            'etfs': {
                'weekly': 'etfs_daily_clean',
                'daily': 'etfs_daily_clean',
                'hourly': 'v2_etfs_hourly',
                '5min': 'v2_etfs_5min'
            },
            'indices': {
                'weekly': 'indices_daily_clean',
                'daily': 'indices_daily_clean',
                'hourly': 'v2_indices_hourly',
                '5min': 'v2_indices_5min'
            },
            'commodities': {
                'weekly': 'commodities_daily_clean',
                'daily': 'v2_commodities_daily',
                'hourly': 'v2_commodities_hourly',
                '5min': 'v2_commodities_5min'
            }
        }

        if asset_type not in table_config:
            return jsonify({'success': False, 'error': f'Unknown asset type: {asset_type}'}), 400

        if timeframe not in table_config[asset_type]:
            return jsonify({'success': False, 'error': f'Unknown timeframe: {timeframe}'}), 400

        table_name = table_config[asset_type][timeframe]

        # Query historical data for the specific symbol
        query = f"""
        SELECT
            symbol,
            datetime,
            open,
            high,
            low,
            close,
            volume
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE UPPER(symbol) = UPPER(@symbol)
        ORDER BY datetime DESC
        LIMIT {limit}
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("symbol", "STRING", symbol)
            ]
        )

        results = client.query(query, job_config=job_config).result(timeout=30)
        data = []
        for row in results:
            row_dict = dict(row)
            # Convert datetime and Decimal types
            for key, value in row_dict.items():
                if isinstance(value, Decimal):
                    row_dict[key] = float(value)
                elif hasattr(value, 'isoformat'):
                    row_dict[key] = value.isoformat()
            data.append(row_dict)

        # Reverse to get chronological order (oldest first)
        data.reverse()

        if not data:
            return jsonify({
                'success': False,
                'error': f'No data found for symbol: {symbol}'
            }), 404

        return jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'symbol': symbol,
            'asset_type': asset_type,
            'timeframe': timeframe,
            'table': table_name
        })

    except Exception as e:
        logger.error(f"Get twelvedata history error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analysis/active-list', methods=['GET'])
def get_active_trading_list():
    """Get the current active trading list (top picks for day trading)"""
    try:
        client = bigquery.Client(project=PROJECT_ID)

        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.active_trading_list`
        WHERE generated_date = (SELECT MAX(generated_date) FROM `{PROJECT_ID}.{DATASET_ID}.active_trading_list`)
        ORDER BY selection_rank
        LIMIT 100
        """

        results = client.query(query).result()
        data = [sanitize_row(row) for row in results]

        return jsonify({'success': True, 'data': data, 'count': len(data)})

    except Exception as e:
        logger.error(f"Get active trading list error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analysis/nlp-search', methods=['POST'])
def nlp_search():
    """Natural language search for all 6 asset types"""
    try:
        data = request.get_json()
        query_text = data.get('query', '').lower()
        asset_type = data.get('asset_type', 'all')
        limit = data.get('limit', 1000)  # Default to 1000, no hard cap

        client = bigquery.Client(project=PROJECT_ID)

        # Parse natural language query into filters
        filters = parse_nlp_query(query_text)

        results = []

        # Search stocks
        if asset_type in ['all', 'stocks']:
            stock_results = search_stocks(client, filters)
            results.extend(stock_results)

        # Search cryptos
        if asset_type in ['all', 'cryptos']:
            crypto_results = search_cryptos(client, filters)
            results.extend(crypto_results)

        # Search ETFs
        if asset_type in ['all', 'etfs']:
            etf_results = search_etfs(client, filters)
            results.extend(etf_results)

        # Search Forex
        if asset_type in ['all', 'forex']:
            forex_results = search_forex(client, filters)
            results.extend(forex_results)

        # Search Indices
        if asset_type in ['all', 'indices']:
            indices_results = search_indices(client, filters)
            results.extend(indices_results)

        # Search Commodities
        if asset_type in ['all', 'commodities']:
            commodities_results = search_commodities(client, filters)
            results.extend(commodities_results)

        # Sort by relevance/score
        results.sort(key=lambda x: x.get('day_trade_score', 0) or 0, reverse=True)

        # Apply limit (default 1000, can be increased via request)
        limited_results = results[:limit] if limit else results

        return jsonify({
            'success': True,
            'query': query_text,
            'filters_applied': filters,
            'results': limited_results,
            'total_count': len(results),
            'returned_count': len(limited_results)
        })

    except Exception as e:
        logger.error(f"NLP search error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


def parse_nlp_query(query):
    """Parse natural language query into structured filters"""
    filters = {}

    # Volatility keywords
    if any(word in query for word in ['high volatility', 'volatile', 'risky']):
        filters['volatility_category'] = 'high'
    elif any(word in query for word in ['low volatility', 'stable', 'safe']):
        filters['volatility_category'] = 'low'
    elif 'medium volatility' in query:
        filters['volatility_category'] = 'medium'

    # Momentum keywords
    if any(word in query for word in ['bullish', 'rising', 'up', 'gaining', 'strong up']):
        filters['momentum_category'] = ['strong_up', 'up']
    elif any(word in query for word in ['bearish', 'falling', 'down', 'dropping']):
        filters['momentum_category'] = ['strong_down', 'down']

    # Market cap keywords
    if any(word in query for word in ['large cap', 'blue chip', 'big']):
        filters['market_cap_category'] = ['mega', 'large']
    elif any(word in query for word in ['mid cap', 'medium']):
        filters['market_cap_category'] = ['mid']
    elif any(word in query for word in ['small cap', 'penny', 'micro']):
        filters['market_cap_category'] = ['small', 'micro']

    # Sector keywords
    sectors = {
        'tech': 'Technology',
        'technology': 'Technology',
        'healthcare': 'Healthcare',
        'health': 'Healthcare',
        'finance': 'Financial Services',
        'financial': 'Financial Services',
        'bank': 'Financial Services',
        'energy': 'Energy',
        'oil': 'Energy',
        'consumer': 'Consumer Cyclical',
        'retail': 'Consumer Cyclical',
        'industrial': 'Industrials',
        'utility': 'Utilities',
        'real estate': 'Real Estate'
    }

    for keyword, sector in sectors.items():
        if keyword in query:
            filters['sector'] = sector
            break

    # Crypto category keywords
    crypto_categories = {
        'defi': 'DeFi',
        'meme': 'Meme',
        'layer 1': 'Smart Contract Platform',
        'smart contract': 'Smart Contract Platform',
        'payment': 'Payment',
        'oracle': 'Oracle',
        'layer 2': 'Layer 2',
        'ai': 'AI'
    }

    for keyword, category in crypto_categories.items():
        if keyword in query:
            filters['crypto_category'] = category
            break

    # Day trading keywords
    if any(word in query for word in ['day trading', 'day trade', 'scalp', 'intraday']):
        filters['min_day_trade_score'] = 60

    return filters


def search_stocks(client, filters):
    """Search stocks from stocks_master_list (15,231 TwelveData stocks with 18 fields)"""
    where_clauses = ["close IS NOT NULL"]

    # Filter by sector if specified
    if 'sector' in filters:
        where_clauses.append(f"sector = '{filters['sector']}'")

    # Filter by exchange
    if 'exchange' in filters:
        where_clauses.append(f"exchange = '{filters['exchange']}'")

    # Filter by country
    if 'country' in filters:
        where_clauses.append(f"country = '{filters['country']}'")

    # Filter by type (Common Stock, ETF, etc.)
    if 'type' in filters:
        where_clauses.append(f"type = '{filters['type']}'")

    # Filter by percent change (gainers/losers)
    if 'min_percent_change' in filters:
        where_clauses.append(f"percent_change >= {filters['min_percent_change']}")
    if 'max_percent_change' in filters:
        where_clauses.append(f"percent_change <= {filters['max_percent_change']}")

    # Filter by price (min_price, max_price)
    if 'min_price' in filters:
        where_clauses.append(f"close >= {filters['min_price']}")
    if 'max_price' in filters:
        where_clauses.append(f"close <= {filters['max_price']}")

    # Filter by volume
    if 'min_volume' in filters:
        where_clauses.append(f"volume >= {filters['min_volume']}")

    # Filter by 52-week metrics
    if 'near_52_high' in filters and filters['near_52_high']:
        where_clauses.append("close >= week_52_high * 0.95")
    if 'near_52_low' in filters and filters['near_52_low']:
        where_clauses.append("close <= week_52_low * 1.05")

    where_sql = "WHERE " + " AND ".join(where_clauses)

    # Query stocks_master_list with 18 TwelveData fields + calculated fields
    query = f"""
    SELECT
        'stock' as asset_type,
        symbol,
        name,
        exchange,
        type,
        country,
        sector,
        industry,
        currency,
        open,
        high,
        low,
        close,
        (high - low) as hi_lo,
        ROUND(SAFE_DIVIDE((high - low), low) * 100, 2) as pct_hi_lo,
        volume,
        previous_close,
        change,
        percent_change,
        average_volume,
        week_52_high,
        week_52_low
    FROM `{PROJECT_ID}.{DATASET_ID}.v2_stocks_master`
    {where_sql}
    ORDER BY percent_change DESC
    LIMIT 20000
    """

    try:
        results = client.query(query).result()
        return [sanitize_row(row) for row in results]
    except Exception as e:
        logger.error(f"Stock search error: {e}")
        return []


def search_cryptos(client, filters):
    """Search cryptos based on filters"""
    where_clauses = []

    if 'volatility_category' in filters:
        where_clauses.append(f"volatility_category = '{filters['volatility_category']}'")

    if 'momentum_category' in filters:
        cats = filters['momentum_category']
        if isinstance(cats, list):
            cat_str = "', '".join(cats)
            where_clauses.append(f"momentum_category IN ('{cat_str}')")

    if 'crypto_category' in filters:
        where_clauses.append(f"category = '{filters['crypto_category']}'")

    if 'min_day_trade_score' in filters:
        where_clauses.append(f"day_trade_score >= {filters['min_day_trade_score']}")

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
    SELECT
        'crypto' as asset_type,
        symbol,
        name,
        industry as sector,
        close as current_price,
        percent_change as weekly_change_percent,
        atr as volatility_weekly,
        rsi as day_trade_score,
        asset_type as market_cap_category,
        CASE WHEN rsi > 70 THEN 'Overbought' WHEN rsi < 30 THEN 'Oversold' ELSE 'Neutral' END as momentum_category,
        CASE WHEN atr > 5 THEN 'High' WHEN atr < 2 THEN 'Low' ELSE 'Medium' END as volatility_category
    FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
    {where_sql}
    ORDER BY close DESC NULLS LAST
    LIMIT 500
    """

    try:
        results = client.query(query).result()
        return [sanitize_row(row) for row in results]
    except:
        return []


def search_etfs(client, filters):
    """Search ETFs based on filters"""
    where_clauses = []

    if 'volatility_category' in filters:
        where_clauses.append(f"volatility_category = '{filters['volatility_category']}'")

    if 'momentum_category' in filters:
        cats = filters['momentum_category']
        if isinstance(cats, list):
            cat_str = "', '".join(cats)
            where_clauses.append(f"momentum_category IN ('{cat_str}')")

    if 'min_day_trade_score' in filters:
        where_clauses.append(f"day_trade_score >= {filters['min_day_trade_score']}")

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
    SELECT
        'etf' as asset_type,
        symbol,
        name,
        industry as sector,
        close as current_price,
        percent_change as weekly_change_percent,
        atr as volatility_weekly,
        rsi as day_trade_score,
        CAST(NULL AS STRING) as market_cap_category,
        CASE WHEN rsi > 70 THEN 'Overbought' WHEN rsi < 30 THEN 'Oversold' ELSE 'Neutral' END as momentum_category,
        CASE WHEN atr > 5 THEN 'High' WHEN atr < 2 THEN 'Low' ELSE 'Medium' END as volatility_category
    FROM `{PROJECT_ID}.{DATASET_ID}.etfs_daily_clean_summary`
    {where_sql}
    ORDER BY close DESC NULLS LAST
    LIMIT 500
    """

    try:
        results = client.query(query).result()
        return [sanitize_row(row) for row in results]
    except:
        return []


def search_forex(client, filters):
    """Search Forex pairs based on filters"""
    where_clauses = []

    if 'volatility_category' in filters:
        where_clauses.append(f"volatility_category = '{filters['volatility_category']}'")

    if 'momentum_category' in filters:
        cats = filters['momentum_category']
        if isinstance(cats, list):
            cat_str = "', '".join(cats)
            where_clauses.append(f"momentum_category IN ('{cat_str}')")

    if 'min_day_trade_score' in filters:
        where_clauses.append(f"day_trade_score >= {filters['min_day_trade_score']}")

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
    SELECT
        'forex' as asset_type,
        symbol,
        name,
        industry as sector,
        close as current_price,
        percent_change as weekly_change_percent,
        atr as volatility_weekly,
        rsi as day_trade_score,
        CAST(NULL AS STRING) as market_cap_category,
        CASE WHEN rsi > 70 THEN 'Overbought' WHEN rsi < 30 THEN 'Oversold' ELSE 'Neutral' END as momentum_category,
        CASE WHEN atr > 5 THEN 'High' WHEN atr < 2 THEN 'Low' ELSE 'Medium' END as volatility_category
    FROM `{PROJECT_ID}.{DATASET_ID}.forex_daily_clean_summary`
    {where_sql}
    ORDER BY close DESC NULLS LAST
    LIMIT 500
    """

    try:
        results = client.query(query).result()
        return [sanitize_row(row) for row in results]
    except:
        return []


def search_indices(client, filters):
    """Search Indices based on filters"""
    where_clauses = []

    if 'volatility_category' in filters:
        where_clauses.append(f"volatility_category = '{filters['volatility_category']}'")

    if 'momentum_category' in filters:
        cats = filters['momentum_category']
        if isinstance(cats, list):
            cat_str = "', '".join(cats)
            where_clauses.append(f"momentum_category IN ('{cat_str}')")

    if 'min_day_trade_score' in filters:
        where_clauses.append(f"day_trade_score >= {filters['min_day_trade_score']}")

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
    SELECT
        'index' as asset_type,
        symbol,
        name,
        industry as sector,
        close as current_price,
        percent_change as weekly_change_percent,
        atr as volatility_weekly,
        rsi as day_trade_score,
        CAST(NULL AS STRING) as market_cap_category,
        CASE WHEN rsi > 70 THEN 'Overbought' WHEN rsi < 30 THEN 'Oversold' ELSE 'Neutral' END as momentum_category,
        CASE WHEN atr > 5 THEN 'High' WHEN atr < 2 THEN 'Low' ELSE 'Medium' END as volatility_category
    FROM `{PROJECT_ID}.{DATASET_ID}.indices_daily_clean_summary`
    {where_sql}
    ORDER BY close DESC NULLS LAST
    LIMIT 500
    """

    try:
        results = client.query(query).result()
        return [sanitize_row(row) for row in results]
    except:
        return []


def search_commodities(client, filters):
    """Search Commodities based on filters"""
    where_clauses = []

    if 'volatility_category' in filters:
        where_clauses.append(f"volatility_category = '{filters['volatility_category']}'")

    if 'momentum_category' in filters:
        cats = filters['momentum_category']
        if isinstance(cats, list):
            cat_str = "', '".join(cats)
            where_clauses.append(f"momentum_category IN ('{cat_str}')")

    if 'min_day_trade_score' in filters:
        where_clauses.append(f"day_trade_score >= {filters['min_day_trade_score']}")

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
    SELECT
        'commodity' as asset_type,
        symbol,
        name,
        industry as sector,
        close as current_price,
        percent_change as weekly_change_percent,
        atr as volatility_weekly,
        rsi as day_trade_score,
        CAST(NULL AS STRING) as market_cap_category,
        CASE WHEN rsi > 70 THEN 'Overbought' WHEN rsi < 30 THEN 'Oversold' ELSE 'Neutral' END as momentum_category,
        CASE WHEN atr > 5 THEN 'High' WHEN atr < 2 THEN 'Low' ELSE 'Medium' END as volatility_category
    FROM `{PROJECT_ID}.{DATASET_ID}.commodities_daily_clean_summary`
    {where_sql}
    ORDER BY close DESC NULLS LAST
    LIMIT 500
    """

    try:
        results = client.query(query).result()
        return [sanitize_row(row) for row in results]
    except:
        return []


def search_weekly_assets(client, asset_type, filters):
    """Search using daily tables (which have actual data) for weekly context"""
    # Map asset types to their DAILY tables (which have actual price data)
    table_map = {
        'stocks': 'stocks_daily_clean',
        'cryptos': 'crypto_daily_clean',
        'forex': 'forex_daily_clean',
        'etfs': 'etfs_daily_clean',
        'indices': 'indices_daily_clean',
        'commodities': 'v2_commodities_daily',
    }

    table_name = table_map.get(asset_type)
    if not table_name:
        return []

    where_clauses = ["close IS NOT NULL AND close > 0"]

    # Filter by price
    if 'min_price' in filters:
        where_clauses.append(f"close >= {filters['min_price']}")
    if 'max_price' in filters:
        where_clauses.append(f"close <= {filters['max_price']}")

    # Filter by percent change (gainers/losers)
    if 'min_percent_change' in filters:
        where_clauses.append(f"percent_change >= {filters['min_percent_change']}")
    if 'max_percent_change' in filters:
        where_clauses.append(f"percent_change <= {filters['max_percent_change']}")

    # Filter by RSI (oversold/overbought)
    if 'min_rsi' in filters:
        where_clauses.append(f"rsi >= {filters['min_rsi']}")
    if 'max_rsi' in filters:
        where_clauses.append(f"rsi <= {filters['max_rsi']}")

    # Filter by 52-week metrics
    if filters.get('near_52_high'):
        where_clauses.append("close >= week_52_high * 0.95")
    if filters.get('near_52_low'):
        where_clauses.append("close <= week_52_low * 1.05")

    where_sql = " AND ".join(where_clauses)

    # Query daily table with ROW_NUMBER to get most recent data per symbol
    query = f"""
    WITH latest_data AS (
        SELECT
            symbol,
            name,
            asset_type,
            exchange,
            close,
            open,
            high,
            low,
            volume,
            percent_change,
            week_52_high,
            week_52_low,
            rsi,
            macd,
            adx,
            atr,
            sma_20,
            sma_50,
            sma_200,
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE {where_sql}
    )
    SELECT
        '{asset_type}' as asset_type_label,
        symbol,
        name,
        COALESCE(asset_type, exchange, '') as sector,
        close as current_price,
        open,
        high,
        low,
        volume,
        percent_change as weekly_change_percent,
        week_52_high,
        week_52_low,
        rsi,
        macd,
        adx,
        sma_20,
        sma_50,
        sma_200,
        CASE WHEN rsi > 70 THEN 'Overbought' WHEN rsi < 30 THEN 'Oversold' ELSE 'Neutral' END as momentum_category,
        CASE WHEN COALESCE(atr, 0) > 5 THEN 'High' WHEN COALESCE(atr, 0) > 2 THEN 'Medium' ELSE 'Low' END as volatility_category
    FROM latest_data
    WHERE rn = 1
    ORDER BY ABS(percent_change) DESC NULLS LAST
    LIMIT 500
    """

    try:
        logger.info(f"Weekly search query for {asset_type}: {query[:200]}...")
        results = client.query(query).result()
        return [sanitize_row(row) for row in results]
    except Exception as e:
        logger.error(f"Weekly search error for {asset_type}: {e}")
        return []


# ============== BIGQUERY TABLE INVENTORY ==============

@app.route('/api/admin/table-inventory', methods=['GET'])
def get_table_inventory():
    """Get inventory of all BigQuery tables with row counts for systematic development tracking"""
    try:
        client = bigquery.Client(project=DATA_PROJECT_ID)

        query = f"""
        SELECT
            table_id,
            row_count,
            ROUND(size_bytes / 1024 / 1024, 2) as size_mb,
            TIMESTAMP_MILLIS(creation_time) as created_at,
            TIMESTAMP_MILLIS(last_modified_time) as last_modified
        FROM `{DATA_PROJECT_ID}.{DATASET_ID}.__TABLES__`
        ORDER BY row_count DESC
        """

        results = client.query(query).result()

        tables = []
        total_rows = 0
        total_size_mb = 0

        for row in results:
            table_info = {
                'table_name': row.table_id,
                'row_count': row.row_count,
                'size_mb': safe_float(row.size_mb) if row.size_mb else 0,
                'created_at': row.created_at.isoformat() if row.created_at else None,
                'last_modified': row.last_modified.isoformat() if row.last_modified else None
            }
            tables.append(table_info)
            total_rows += row.row_count or 0
            total_size_mb += safe_float(row.size_mb) if row.size_mb else 0

        # Categorize tables
        categories = {
            'stocks': [t for t in tables if 'stock' in t['table_name'].lower()],
            'crypto': [t for t in tables if 'crypto' in t['table_name'].lower()],
            'forex': [t for t in tables if 'forex' in t['table_name'].lower()],
            'etfs': [t for t in tables if 'etf' in t['table_name'].lower()],
            'indices': [t for t in tables if 'indic' in t['table_name'].lower()],
            'commodities': [t for t in tables if 'commodit' in t['table_name'].lower()],
            'other': [t for t in tables if not any(x in t['table_name'].lower() for x in ['stock', 'crypto', 'forex', 'etf', 'indic', 'commodit'])]
        }

        return jsonify({
            'success': True,
            'summary': {
                'total_tables': len(tables),
                'total_rows': total_rows,
                'total_size_mb': round(total_size_mb, 2),
                'last_updated': datetime.utcnow().isoformat()
            },
            'categories': {
                cat: {
                    'count': len(cat_tables),
                    'total_rows': sum(t['row_count'] for t in cat_tables),
                    'tables': cat_tables
                }
                for cat, cat_tables in categories.items()
            },
            'all_tables': tables
        })

    except Exception as e:
        logger.error(f"Table inventory error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/table-schema/<table_name>', methods=['GET'])
def get_table_schema(table_name):
    """Get schema/structure of a specific BigQuery table"""
    try:
        client = bigquery.Client(project=DATA_PROJECT_ID)
        table_ref = f"{DATA_PROJECT_ID}.{DATASET_ID}.{table_name}"
        table = client.get_table(table_ref)

        schema = []
        for field in table.schema:
            schema.append({
                'name': field.name,
                'type': field.field_type,
                'mode': field.mode,
                'description': field.description or ''
            })

        # Get sample data (first 5 rows)
        sample_query = f"SELECT * FROM `{table_ref}` LIMIT 5"
        sample_results = client.query(sample_query).result()
        sample_data = [sanitize_row(row) for row in sample_results]

        # Convert any non-serializable types in sample data
        for row in sample_data:
            for key, value in row.items():
                if hasattr(value, 'isoformat'):
                    row[key] = value.isoformat()
                elif isinstance(value, bytes):
                    row[key] = value.decode('utf-8', errors='ignore')

        return jsonify({
            'success': True,
            'table_name': table_name,
            'num_rows': table.num_rows,
            'num_bytes': table.num_bytes,
            'size_mb': round(table.num_bytes / 1024 / 1024, 2) if table.num_bytes else 0,
            'created': table.created.isoformat() if table.created else None,
            'modified': table.modified.isoformat() if table.modified else None,
            'num_fields': len(schema),
            'schema': schema,
            'sample_data': sample_data
        })

    except Exception as e:
        logger.error(f"Table schema error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/table-data/<table_name>', methods=['GET'])
def get_table_data(table_name):
    """Get data from a BigQuery table for download/export"""
    from decimal import Decimal
    try:
        limit = request.args.get('limit', 1000, type=int)
        offset = request.args.get('offset', 0, type=int)
        limit = min(limit, 50000)  # Cap at 50000 rows for better downloads

        client = bigquery.Client(project=DATA_PROJECT_ID)
        table_ref = f"{DATA_PROJECT_ID}.{DATASET_ID}.{table_name}"

        # Get total count first
        count_query = f"SELECT COUNT(*) as total FROM `{table_ref}`"
        count_job = client.query(count_query)
        count_result = list(count_job.result(timeout=30))[0]
        total_rows = count_result.total

        # Query data with pagination - use timeout
        query = f"SELECT * FROM `{table_ref}` LIMIT {limit} OFFSET {offset}"
        job = client.query(query)
        results = job.result(timeout=120)  # 2 minute timeout
        data = [sanitize_row(row) for row in results]

        # Convert non-serializable types (including Decimal)
        for row in data:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
                elif hasattr(value, 'isoformat'):
                    row[key] = value.isoformat()
                elif isinstance(value, bytes):
                    row[key] = value.decode('utf-8', errors='ignore')
                elif value is None:
                    row[key] = None

        return jsonify({
            'success': True,
            'table_name': table_name,
            'row_count': len(data),
            'total_rows': total_rows,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + len(data)) < total_rows,
            'data': data
        })

    except Exception as e:
        logger.error(f"Table data error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/table-export/<table_name>', methods=['GET'])
def export_table_data(table_name):
    """Export table data as CSV stream for large downloads"""
    from decimal import Decimal
    try:
        limit = request.args.get('limit', 50000, type=int)
        limit = min(limit, 100000)  # Cap at 100k rows

        client = bigquery.Client(project=DATA_PROJECT_ID)
        table_ref = f"{DATA_PROJECT_ID}.{DATASET_ID}.{table_name}"

        # Get schema first
        table = client.get_table(table_ref)
        headers = [field.name for field in table.schema]

        # Query data with timeout
        query = f"SELECT * FROM `{table_ref}` LIMIT {limit}"
        job = client.query(query)
        results = job.result(timeout=180)  # 3 minute timeout for large exports

        def generate_csv():
            # Yield header row
            yield ','.join(headers) + '\n'
            # Yield data rows
            for row in results:
                values = []
                for h in headers:
                    val = row[h]
                    if val is None:
                        values.append('')
                    elif isinstance(val, Decimal):
                        values.append(str(safe_float(val)))
                    elif hasattr(val, 'isoformat'):
                        values.append(val.isoformat())
                    else:
                        str_val = str(val)
                        if ',' in str_val or '"' in str_val or '\n' in str_val:
                            str_val = '"' + str_val.replace('"', '""') + '"'
                        values.append(str_val)
                yield ','.join(values) + '\n'

        return Response(
            generate_csv(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={table_name}.csv',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )

    except Exception as e:
        logger.error(f"Table export error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/data-warehouse-status', methods=['GET'])
def get_data_warehouse_status():
    """Get comprehensive data warehouse status for monitoring dashboard"""
    try:
        # Query all tables from BigQuery using __TABLES__ (simpler and works everywhere)
        query = f"""
            SELECT
                table_id as table_name,
                row_count as total_rows,
                ROUND(size_bytes / 1048576, 2) as size_mb,
                TIMESTAMP_MILLIS(last_modified_time) as last_modified
            FROM `{DATA_PROJECT_ID}.{DATASET_ID}.__TABLES__`
            ORDER BY table_id
        """

        result = client.query(query)
        tables = []
        total_rows = 0
        total_size = 0

        for row in result:
            table_info = {
                'name': row.table_name,
                'rows': row.total_rows or 0,
                'size_mb': safe_float(row.size_mb or 0),
                'last_modified': row.last_modified.isoformat() if row.last_modified else None
            }
            tables.append(table_info)
            total_rows += table_info['rows']
            total_size += table_info['size_mb']

        # Get weekly progress from week-by-week tables (all 6 asset types)
        weekly_progress = {
            'stocks': {'current': 0, 'records': 0, 'target': 20000, 'weeks': 0},
            'crypto': {'current': 0, 'records': 0, 'target': 1100, 'weeks': 0},
            'forex': {'current': 0, 'records': 0, 'target': 500, 'weeks': 0},
            'etfs': {'current': 0, 'records': 0, 'target': 5000, 'weeks': 0},
            'indices': {'current': 0, 'records': 0, 'target': 500, 'weeks': 0},
            'commodities': {'current': 0, 'records': 0, 'target': 100, 'weeks': 0}
        }

        # Count symbols and weeks from new week-by-week tables
        asset_tables = {
            'stocks': 'weekly_stocks_all',
            'crypto': 'weekly_crypto_all',
            'forex': 'weekly_forex_all',
            'etfs': 'weekly_etfs_all',
            'indices': 'weekly_indices_all',
            'commodities': 'weekly_commodities_all'
        }

        for asset_type, table_name in asset_tables.items():
            try:
                query = f"""
                    SELECT
                        COUNT(DISTINCT symbol) as symbols,
                        COUNT(*) as records,
                        COUNT(DISTINCT week_start) as weeks
                    FROM `{DATA_PROJECT_ID}.{DATASET_ID}.{table_name}`
                """
                result = list(client.query(query))
                if result:
                    weekly_progress[asset_type]['current'] = result[0].symbols or 0
                    weekly_progress[asset_type]['records'] = result[0].records or 0
                    weekly_progress[asset_type]['weeks'] = result[0].weeks or 0
            except Exception as e:
                # Try fallback tables
                fallback_tables = {
                    'stocks': ['stocks_weekly_batch', 'stocks_daily_clean'],
                    'crypto': ['crypto_weekly_batch', 'crypto_daily_clean'],
                    'forex': ['forex_daily_clean'],
                    'etfs': ['etfs_daily_clean'],
                    'indices': ['indices_daily_clean'],
                    'commodities': ['commodities_daily_clean']
                }
                for fallback in fallback_tables.get(asset_type, []):
                    try:
                        query = f"""
                            SELECT COUNT(DISTINCT symbol) as symbols, COUNT(*) as records
                            FROM `{DATA_PROJECT_ID}.{DATASET_ID}.{fallback}`
                        """
                        result = list(client.query(query))
                        if result and result[0].symbols:
                            weekly_progress[asset_type]['current'] = result[0].symbols or 0
                            weekly_progress[asset_type]['records'] = result[0].records or 0
                            break
                    except:
                        continue

        return jsonify({
            'success': True,
            'tables': sorted(tables, key=lambda x: x['rows'], reverse=True),
            'summary': {
                'total_tables': len(tables),
                'total_rows': total_rows,
                'total_size_mb': round(total_size, 2)
            },
            'weekly_progress': weekly_progress,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Data warehouse status error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/table-inventory/ai-analysis', methods=['POST'])
def analyze_table_inventory_with_ai():
    """Use Gemini AI to analyze table inventory and provide intelligent insights"""
    try:
        if not VERTEX_AI_AVAILABLE or not gemini_model:
            return jsonify({
                'success': False,
                'error': 'Gemini AI not available',
                'fallback_insights': get_fallback_table_insights()
            }), 503

        data = request.get_json() or {}
        inventory_data = data.get('inventory_data')
        analysis_type = data.get('analysis_type', 'overview')  # overview, quality, recommendations

        if not inventory_data:
            return jsonify({'success': False, 'error': 'No inventory data provided'}), 400

        # Build the AI prompt based on analysis type
        prompt = build_table_inventory_prompt(inventory_data, analysis_type)

        # Call Gemini model
        response = gemini_model.generate_content(prompt)

        if response and response.text:
            return jsonify({
                'success': True,
                'model': GEMINI_MODEL,
                'analysis_type': analysis_type,
                'insights': response.text,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No response from AI model',
                'fallback_insights': get_fallback_table_insights()
            }), 500

    except Exception as e:
        logger.error(f"AI table analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_insights': get_fallback_table_insights()
        }), 500


def build_table_inventory_prompt(inventory_data, analysis_type):
    """Build AI prompt for table inventory analysis"""
    summary = inventory_data.get('summary', {})
    categories = inventory_data.get('categories', {})

    # Build category summary
    category_summary = []
    for cat, cat_data in categories.items():
        if isinstance(cat_data, dict):
            category_summary.append(f"- {cat.capitalize()}: {cat_data.get('count', 0)} tables, {cat_data.get('total_rows', 0):,} rows")

    base_context = f"""
You are an AI data analyst for a trading application. Analyze this BigQuery table inventory:

DATABASE SUMMARY:
- Total Tables: {summary.get('total_tables', 0)}
- Total Rows: {summary.get('total_rows', 0):,}
- Total Size: {summary.get('total_size_mb', 0):.2f} MB
- Last Updated: {summary.get('last_updated', 'Unknown')}

TABLES BY CATEGORY:
{chr(10).join(category_summary)}
"""

    if analysis_type == 'overview':
        return base_context + """
Provide a concise executive summary (3-5 key points) about this trading data infrastructure:
1. Overall health assessment
2. Data coverage analysis
3. Notable patterns or observations
4. Any potential concerns

Format with clear headers and bullet points. Be specific about numbers and percentages.
"""
    elif analysis_type == 'quality':
        return base_context + """
Analyze data quality and completeness:
1. Are there any empty or near-empty tables that need attention?
2. What's the data distribution across asset categories?
3. Are there any gaps in coverage?
4. Recommendations for data quality improvements

Format with clear headers and bullet points. Be actionable.
"""
    elif analysis_type == 'recommendations':
        return base_context + """
Provide strategic recommendations for this trading data platform:
1. Storage optimization opportunities
2. Table consolidation suggestions
3. Data pipeline improvements
4. Scaling considerations
5. Cost optimization tips

Format with clear headers, priority levels (High/Medium/Low), and estimated impact.
"""
    else:
        return base_context + """
Provide a brief, intelligent analysis of this table inventory with 3-5 key insights and actionable recommendations.
"""


def get_fallback_table_insights():
    """Generate basic insights without AI when Gemini is unavailable"""
    return {
        'status': 'fallback',
        'message': 'AI analysis temporarily unavailable. Basic statistics shown.',
        'tips': [
            'Monitor tables with 0 rows for potential data pipeline issues',
            'Large tables (>100MB) may benefit from partitioning',
            'Consider archiving tables not modified in 30+ days',
            'Ensure all asset categories have recent data'
        ]
    }


# ============== AI TRAINING ENDPOINTS ==============

@app.route('/api/ai/training-docs', methods=['GET'])
def list_training_docs():
    """List all documents in the training bucket"""
    try:
        bucket = storage_client.bucket(TRAINING_BUCKET)
        blobs = list(bucket.list_blobs())

        documents = []
        for blob in blobs:
            documents.append({
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created.isoformat() if blob.time_created else None,
                'updated': blob.updated.isoformat() if blob.updated else None,
                'md5_hash': blob.md5_hash
            })

        return jsonify({
            'success': True,
            'bucket': TRAINING_BUCKET,
            'documents': documents,
            'count': len(documents)
        })
    except Exception as e:
        logger.error(f"List training docs error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/training-docs/upload', methods=['POST'])
def upload_training_doc():
    """Upload a document to the training bucket"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Get optional metadata
        category = request.form.get('category', 'general')
        description = request.form.get('description', '')

        bucket = storage_client.bucket(TRAINING_BUCKET)

        # Create blob with metadata
        blob_name = f"{category}/{file.filename}"
        blob = bucket.blob(blob_name)

        # Set metadata
        blob.metadata = {
            'category': category,
            'description': description,
            'uploaded_by': request.form.get('uploaded_by', 'system'),
            'original_filename': file.filename
        }

        # Upload file
        blob.upload_from_file(file, content_type=file.content_type)

        return jsonify({
            'success': True,
            'message': f'Document uploaded successfully',
            'blob_name': blob_name,
            'size': blob.size,
            'content_type': blob.content_type
        })
    except Exception as e:
        logger.error(f"Upload training doc error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/training-docs/<path:filename>', methods=['DELETE'])
def delete_training_doc(filename):
    """Delete a document from the training bucket"""
    try:
        bucket = storage_client.bucket(TRAINING_BUCKET)
        blob = bucket.blob(filename)

        if not blob.exists():
            return jsonify({'success': False, 'error': 'Document not found'}), 404

        blob.delete()

        return jsonify({
            'success': True,
            'message': f'Document {filename} deleted successfully'
        })
    except Exception as e:
        logger.error(f"Delete training doc error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/training-docs/<path:filename>/download', methods=['GET'])
def download_training_doc(filename):
    """Download a document from the training bucket"""
    try:
        bucket = storage_client.bucket(TRAINING_BUCKET)
        blob = bucket.blob(filename)

        if not blob.exists():
            return jsonify({'success': False, 'error': 'Document not found'}), 404

        # Generate signed URL for download (valid for 1 hour)
        url = blob.generate_signed_url(
            version="v4",
            expiration=3600,
            method="GET"
        )

        return jsonify({
            'success': True,
            'download_url': url,
            'filename': filename
        })
    except Exception as e:
        logger.error(f"Download training doc error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """Check AI service status"""
    try:
        bucket_exists = False
        bucket_doc_count = 0

        try:
            bucket = storage_client.bucket(TRAINING_BUCKET)
            bucket_exists = bucket.exists()
            if bucket_exists:
                blobs = list(bucket.list_blobs())
                bucket_doc_count = len(blobs)
        except Exception as e:
            logger.warning(f"Bucket check failed: {e}")

        return jsonify({
            'success': True,
            'vertex_ai_available': VERTEX_AI_AVAILABLE,
            'gemini_model': GEMINI_MODEL if VERTEX_AI_AVAILABLE else None,
            'gemini_ready': gemini_model is not None,
            'training_bucket': TRAINING_BUCKET,
            'bucket_exists': bucket_exists,
            'training_docs_count': bucket_doc_count,
            'location': VERTEX_AI_LOCATION
        })
    except Exception as e:
        logger.error(f"AI status error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze():
    """Analyze data using Gemini AI"""
    try:
        if not VERTEX_AI_AVAILABLE or gemini_model is None:
            return jsonify({
                'success': False,
                'error': 'Vertex AI not available. Please install google-cloud-aiplatform'
            }), 503

        data = request.get_json()
        prompt = data.get('prompt', '')
        context = data.get('context', '')
        symbol = data.get('symbol', '')

        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400

        # Build the full prompt with trading context
        full_prompt = f"""You are an AI trading assistant for AIAlgoTradeHits.com.
You have expertise in technical analysis, pattern recognition, and market predictions.

{f"Symbol/Asset: {symbol}" if symbol else ""}
{f"Context Data: {context}" if context else ""}

User Query: {prompt}

Provide a detailed, professional analysis. Include:
1. Key observations
2. Technical indicators interpretation
3. Pattern recognition insights
4. Risk assessment
5. Actionable recommendations
"""

        # Generate response
        response = gemini_model.generate_content(full_prompt)

        return jsonify({
            'success': True,
            'response': response.text,
            'model': GEMINI_MODEL,
            'prompt_tokens': len(full_prompt.split()),
        })
    except Exception as e:
        logger.error(f"AI analyze error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/smart-search', methods=['POST'])
def ai_smart_search():
    """AI-powered context-sensitive smart search with natural language understanding"""
    try:
        if not VERTEX_AI_AVAILABLE or gemini_model is None:
            # Fallback to basic NLP search if AI not available
            return nlp_search()

        data = request.get_json()
        query = data.get('query', '')

        # Get context from request (asset type and period from frontend)
        context = data.get('context', {})
        context_asset_type = context.get('assetType', 'all')
        context_period = context.get('period', 'daily')
        context_page = context.get('page', 'dashboard')

        logger.info(f"Smart search context: asset={context_asset_type}, period={context_period}, page={context_page}")

        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400

        # Use Gemini to parse the query into structured filters
        parse_prompt = f"""Parse this trading search query into structured JSON filters:
Query: "{query}"

Return ONLY valid JSON with these possible fields:
{{
  "asset_types": ["stocks", "crypto", "forex", "etfs", "indices", "commodities"],
  "min_price": number (e.g., 100 for "stocks over $100"),
  "max_price": number (e.g., 50 for "stocks under $50"),
  "min_percent_change": number (e.g., 5 for "gainers more than 5%"),
  "max_percent_change": number (e.g., -5 for "losers more than 5%"),
  "min_volume": number (e.g., 1000000 for "high volume"),
  "volatility": "high" | "medium" | "low",
  "momentum": "bullish" | "bearish" | "neutral",
  "sector": "Technology" | "Healthcare" | "Energy" | "Financial" | "Consumer" | etc,
  "near_52_high": true/false (stocks near 52-week high),
  "near_52_low": true/false (stocks near 52-week low),
  "symbols": ["AAPL", "BTC/USD"] // specific symbols if mentioned
}}

Examples:
- "stocks over $100" -> {{"asset_types": ["stocks"], "min_price": 100}}
- "tech stocks under $50" -> {{"asset_types": ["stocks"], "sector": "Technology", "max_price": 50}}
- "top gainers" -> {{"asset_types": ["stocks"], "min_percent_change": 0}}
- "high volume stocks" -> {{"asset_types": ["stocks"], "min_volume": 1000000}}

Only include fields that are clearly implied by the query."""

        parse_response = gemini_model.generate_content(parse_prompt)

        # Try to parse the JSON from response
        try:
            import re
            json_match = re.search(r'\{.*\}', parse_response.text, re.DOTALL)
            if json_match:
                filters = json.loads(json_match.group())
            else:
                filters = {}
        except:
            filters = {}

        # Now perform the search with parsed filters
        client = bigquery.Client(project=PROJECT_ID)
        results = []

        # Use context to determine which assets to search
        # If context specifies a specific asset type, use that; otherwise use AI-parsed types
        if context_asset_type and context_asset_type != 'all':
            asset_types = [context_asset_type]
        else:
            asset_types = filters.get('asset_types', ['stocks', 'crypto'])

        # Determine the table prefix based on period context
        table_suffix = ''
        if context_period == 'weekly':
            table_suffix = '_weekly_summary'
        elif context_period == 'hourly':
            table_suffix = '_hourly'
        elif context_period == '5min':
            table_suffix = '_5min'
        else:
            table_suffix = '_daily'  # default to daily

        logger.info(f"Searching assets: {asset_types} with period suffix: {table_suffix}")

        for asset_type in asset_types[:3]:  # Limit to 3 asset types
            if asset_type == 'stocks':
                if context_period == 'weekly':
                    stock_results = search_weekly_assets(client, 'stocks', filters)
                else:
                    stock_results = search_stocks(client, filters)
                results.extend(stock_results)
            elif asset_type in ['crypto', 'cryptos']:
                if context_period == 'weekly':
                    crypto_results = search_weekly_assets(client, 'cryptos', filters)
                else:
                    crypto_results = search_cryptos(client, filters)
                results.extend(crypto_results)
            elif asset_type == 'forex':
                if context_period == 'weekly':
                    forex_results = search_weekly_assets(client, 'forex', filters)
                else:
                    forex_results = search_forex(client, filters)
                results.extend(forex_results)
            elif asset_type == 'etfs':
                if context_period == 'weekly':
                    etf_results = search_weekly_assets(client, 'etfs', filters)
                else:
                    etf_results = search_etfs(client, filters)
                results.extend(etf_results)
            elif asset_type == 'indices':
                if context_period == 'weekly':
                    index_results = search_weekly_assets(client, 'indices', filters)
                else:
                    index_results = search_indices(client, filters)
                results.extend(index_results)
            elif asset_type == 'commodities':
                if context_period == 'weekly':
                    commodity_results = search_weekly_assets(client, 'commodities', filters)
                else:
                    commodity_results = search_commodities(client, filters)
                results.extend(commodity_results)

        # Sort by percent change (most relevant for trading)
        results.sort(key=lambda x: abs(x.get('percent_change', 0) or x.get('weekly_change_percent', 0) or 0), reverse=True)

        # Generate AI summary of results
        if results:
            summary_prompt = f"""Summarize these trading search results in 2-3 sentences:
Query: {query}
Found {len(results)} results
Top picks: {[r.get('symbol', r.get('pair', 'N/A')) for r in results[:5]]}
"""
            summary_response = gemini_model.generate_content(summary_prompt)
            ai_summary = summary_response.text
        else:
            ai_summary = "No matching assets found for your query."

        # Log filter details for debugging
        logger.info(f"Smart search query: {query}")
        logger.info(f"Parsed filters: {filters}")
        logger.info(f"Results count before limit: {len(results)}")

        # Limit results to top 100 most relevant
        limited_results = results[:100]

        return jsonify({
            'success': True,
            'query': query,
            'parsed_filters': filters,
            'results': limited_results,
            'count': len(limited_results),
            'total_matches': len(results),
            'ai_summary': ai_summary,
            'model_used': GEMINI_MODEL
        })
    except Exception as e:
        logger.error(f"AI smart search error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/pattern-recognition', methods=['POST'])
def ai_pattern_recognition():
    """Analyze chart patterns using AI"""
    try:
        if not VERTEX_AI_AVAILABLE or gemini_model is None:
            return jsonify({
                'success': False,
                'error': 'Vertex AI not available'
            }), 503

        data = request.get_json()
        symbol = data.get('symbol', '')
        timeframe = data.get('timeframe', 'daily')
        price_data = data.get('price_data', [])

        if not symbol or not price_data:
            return jsonify({'success': False, 'error': 'Symbol and price_data required'}), 400

        # Format price data for analysis
        price_summary = []
        for i, p in enumerate(price_data[-20:]):  # Last 20 candles
            price_summary.append(f"[{i}] O:{p.get('open'):.2f} H:{p.get('high'):.2f} L:{p.get('low'):.2f} C:{p.get('close'):.2f}")

        pattern_prompt = f"""Analyze this price data for {symbol} ({timeframe} timeframe) and identify chart patterns:

Recent Price Action:
{chr(10).join(price_summary)}

Identify:
1. Current chart patterns (head and shoulders, double top/bottom, triangles, wedges, etc.)
2. Support and resistance levels
3. Trend direction and strength
4. Potential breakout/breakdown levels
5. Pattern completion probability

Format your response as:
- Pattern: [name]
- Confidence: [high/medium/low]
- Direction: [bullish/bearish/neutral]
- Key Levels: [list of prices]
- Recommendation: [brief action]
"""

        response = gemini_model.generate_content(pattern_prompt)

        return jsonify({
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'analysis': response.text,
            'data_points_analyzed': len(price_data)
        })
    except Exception as e:
        logger.error(f"Pattern recognition error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/predict', methods=['POST'])
def ai_predict():
    """Generate price predictions using AI"""
    try:
        if not VERTEX_AI_AVAILABLE or gemini_model is None:
            return jsonify({
                'success': False,
                'error': 'Vertex AI not available'
            }), 503

        data = request.get_json()
        symbol = data.get('symbol', '')
        timeframe = data.get('timeframe', 'daily')
        indicators = data.get('indicators', {})

        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol required'}), 400

        predict_prompt = f"""Based on the following technical indicators for {symbol}, provide a price prediction:

Timeframe: {timeframe}
Current Price: {indicators.get('close', 'N/A')}
RSI: {indicators.get('rsi', 'N/A')}
MACD: {indicators.get('macd', 'N/A')}
MACD Signal: {indicators.get('macd_signal', 'N/A')}
ADX: {indicators.get('adx', 'N/A')}
SMA 20: {indicators.get('sma_20', 'N/A')}
SMA 50: {indicators.get('sma_50', 'N/A')}
Bollinger Upper: {indicators.get('bollinger_upper', 'N/A')}
Bollinger Lower: {indicators.get('bollinger_lower', 'N/A')}
Volume Trend: {indicators.get('volume_trend', 'N/A')}

Provide:
1. Short-term outlook (1-3 days)
2. Medium-term outlook (1-2 weeks)
3. Key levels to watch
4. Risk/reward assessment
5. Confidence level (1-10)

IMPORTANT: This is for educational purposes only. Not financial advice."""

        response = gemini_model.generate_content(predict_prompt)

        return jsonify({
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'prediction': response.text,
            'disclaimer': 'This is AI-generated analysis for educational purposes only. Not financial advice.'
        })
    except Exception as e:
        logger.error(f"AI predict error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/train', methods=['POST'])
def ai_train():
    """Trigger training/fine-tuning with documents in the bucket"""
    try:
        data = request.get_json()
        training_type = data.get('type', 'context')
        categories = data.get('categories', [])

        # List documents in the training bucket
        bucket = storage_client.bucket(TRAINING_BUCKET)
        blobs = list(bucket.list_blobs())

        if not blobs:
            return jsonify({
                'success': False,
                'error': 'No training documents found in bucket'
            }), 400

        # Filter by categories if specified
        if categories:
            blobs = [b for b in blobs if any(cat in b.name for cat in categories)]

        # For now, we'll load document contents for context-based training
        training_context = []
        for blob in blobs[:10]:  # Limit to 10 docs
            if blob.size < 1000000:  # Skip files > 1MB
                try:
                    content = blob.download_as_text()
                    training_context.append({
                        'name': blob.name,
                        'content': content[:5000]  # First 5000 chars
                    })
                except:
                    pass

        # Store training context in a summary document
        summary_blob = bucket.blob('_training_context_summary.json')
        summary_data = {
            'last_trained': datetime.now().isoformat(),
            'documents_processed': len(training_context),
            'training_type': training_type,
            'categories': categories
        }
        summary_blob.upload_from_string(
            json.dumps(summary_data, indent=2),
            content_type='application/json'
        )

        return jsonify({
            'success': True,
            'message': 'Training context updated successfully',
            'documents_processed': len(training_context),
            'training_type': training_type,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"AI train error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/training-docs/categories', methods=['GET'])
def get_training_categories():
    """Get list of training document categories"""
    try:
        bucket = storage_client.bucket(TRAINING_BUCKET)
        blobs = list(bucket.list_blobs())

        categories = set()
        for blob in blobs:
            # Extract category from path (first folder)
            parts = blob.name.split('/')
            if len(parts) > 1:
                categories.add(parts[0])
            else:
                categories.add('uncategorized')

        return jsonify({
            'success': True,
            'categories': list(categories),
            'total_docs': len(blobs)
        })
    except Exception as e:
        logger.error(f"Get categories error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============== TRADING STRATEGY ENDPOINTS ==============

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get all trading strategies"""
    try:
        query = """
        SELECT
            strategy_id,
            strategy_name,
            strategy_code,
            description,
            strategy_type,
            asset_types,
            timeframes,
            is_active,
            is_paper_trading,
            is_live_trading,
            created_at
        FROM `aialgotradehits.crypto_trading_data.trading_strategies`
        ORDER BY created_at DESC
        """
        results = list(client.query(query).result())

        strategies = []
        for row in results:
            strategies.append({
                'strategy_id': row.strategy_id,
                'strategy_name': row.strategy_name,
                'strategy_code': row.strategy_code,
                'description': row.description,
                'strategy_type': row.strategy_type,
                'asset_types': list(row.asset_types) if row.asset_types else [],
                'timeframes': list(row.timeframes) if row.timeframes else [],
                'is_active': row.is_active,
                'is_paper_trading': row.is_paper_trading,
                'is_live_trading': row.is_live_trading,
                'created_at': row.created_at.isoformat() if row.created_at else None
            })

        return jsonify({
            'success': True,
            'strategies': strategies,
            'count': len(strategies)
        })
    except Exception as e:
        logger.error(f"Get strategies error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/strategies/<strategy_id>', methods=['GET'])
def get_strategy_detail(strategy_id):
    """Get detailed strategy info including parameters"""
    try:
        query = f"""
        SELECT *
        FROM `aialgotradehits.crypto_trading_data.trading_strategies`
        WHERE strategy_id = '{strategy_id}'
        """
        results = list(client.query(query).result())

        if not results:
            return jsonify({'success': False, 'error': 'Strategy not found'}), 404

        row = results[0]
        strategy = {
            'strategy_id': row.strategy_id,
            'strategy_name': row.strategy_name,
            'strategy_code': row.strategy_code,
            'description': row.description,
            'strategy_type': row.strategy_type,
            'asset_types': list(row.asset_types) if row.asset_types else [],
            'timeframes': list(row.timeframes) if row.timeframes else [],
            'parameters': json.loads(row.parameters) if row.parameters else {},
            'entry_rules': json.loads(row.entry_rules) if row.entry_rules else {},
            'exit_rules': json.loads(row.exit_rules) if row.exit_rules else {},
            'data_sources': list(row.data_sources) if row.data_sources else [],
            'is_active': row.is_active,
            'is_paper_trading': row.is_paper_trading,
            'is_live_trading': row.is_live_trading,
            'created_by': row.created_by,
            'created_at': row.created_at.isoformat() if row.created_at else None,
            'updated_at': row.updated_at.isoformat() if row.updated_at else None
        }

        return jsonify({
            'success': True,
            'strategy': strategy
        })
    except Exception as e:
        logger.error(f"Get strategy detail error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/strategies/<strategy_id>/signals', methods=['GET'])
def get_strategy_signals(strategy_id):
    """Get recent signals for a strategy"""
    try:
        limit = request.args.get('limit', 50, type=int)
        symbol = request.args.get('symbol', None)

        query = f"""
        SELECT
            signal_id,
            symbol,
            asset_type,
            signal_type,
            signal_strength,
            confidence_score,
            signal_price,
            signal_datetime,
            rsi,
            macd,
            volume,
            cycle_number,
            sector,
            sector_rank,
            ai_reasoning,
            is_executed
        FROM `aialgotradehits.crypto_trading_data.strategy_signals`
        WHERE strategy_id = '{strategy_id}'
        {"AND symbol = '" + symbol + "'" if symbol else ""}
        ORDER BY signal_datetime DESC
        LIMIT {limit}
        """
        results = list(client.query(query).result())

        signals = []
        for row in results:
            signals.append({
                'signal_id': row.signal_id,
                'symbol': row.symbol,
                'asset_type': row.asset_type,
                'signal_type': row.signal_type,
                'signal_strength': row.signal_strength,
                'confidence_score': row.confidence_score,
                'signal_price': row.signal_price,
                'signal_datetime': row.signal_datetime.isoformat() if row.signal_datetime else None,
                'rsi': row.rsi,
                'macd': row.macd,
                'volume': row.volume,
                'cycle_number': row.cycle_number,
                'sector': row.sector,
                'sector_rank': row.sector_rank,
                'ai_reasoning': row.ai_reasoning,
                'is_executed': row.is_executed
            })

        return jsonify({
            'success': True,
            'strategy_id': strategy_id,
            'signals': signals,
            'count': len(signals)
        })
    except Exception as e:
        logger.error(f"Get strategy signals error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rise-cycles/<symbol>/<date>', methods=['GET'])
def get_rise_cycles(symbol, date):
    """Get rise cycles for a symbol on a specific date"""
    try:
        query = f"""
        SELECT
            cycle_id,
            symbol,
            trade_date,
            cycle_number,
            entry_datetime,
            entry_price,
            entry_rsi,
            exit_datetime,
            exit_price,
            exit_rsi,
            exit_reason,
            duration_minutes,
            gain_pct,
            peak_price,
            peak_gain_pct,
            drawdown_from_peak,
            timeframe
        FROM `aialgotradehits.crypto_trading_data.rise_cycles`
        WHERE symbol = '{symbol}'
          AND trade_date = '{date}'
        ORDER BY cycle_number
        """
        results = list(client.query(query).result())

        cycles = []
        total_gain = 0
        for row in results:
            cycle = {
                'cycle_id': row.cycle_id,
                'symbol': row.symbol,
                'trade_date': str(row.trade_date),
                'cycle_number': row.cycle_number,
                'entry_datetime': row.entry_datetime.isoformat() if row.entry_datetime else None,
                'entry_price': row.entry_price,
                'entry_rsi': row.entry_rsi,
                'exit_datetime': row.exit_datetime.isoformat() if row.exit_datetime else None,
                'exit_price': row.exit_price,
                'exit_rsi': row.exit_rsi,
                'exit_reason': row.exit_reason,
                'duration_minutes': row.duration_minutes,
                'gain_pct': row.gain_pct,
                'peak_price': row.peak_price,
                'peak_gain_pct': row.peak_gain_pct,
                'drawdown_from_peak': row.drawdown_from_peak,
                'timeframe': row.timeframe
            }
            cycles.append(cycle)
            total_gain += row.gain_pct or 0

        # Calculate what-if scenario
        starting_capital = 10000
        current_capital = starting_capital
        for cycle in cycles:
            if cycle['gain_pct']:
                current_capital *= (1 + cycle['gain_pct'] / 100)

        return jsonify({
            'success': True,
            'symbol': symbol,
            'date': date,
            'cycles': cycles,
            'count': len(cycles),
            'summary': {
                'total_cycles': len(cycles),
                'winning_cycles': len([c for c in cycles if (c['gain_pct'] or 0) > 0]),
                'losing_cycles': len([c for c in cycles if (c['gain_pct'] or 0) <= 0]),
                'total_gain_pct': round(total_gain, 2),
                'starting_capital': starting_capital,
                'ending_capital': round(current_capital, 2),
                'total_return_pct': round((current_capital - starting_capital) / starting_capital * 100, 2)
            }
        })
    except Exception as e:
        logger.error(f"Get rise cycles error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/sector-momentum', methods=['GET'])
def get_sector_momentum():
    """Get current sector momentum rankings"""
    try:
        # Join weekly data with master table to get sector information
        query = """
        WITH latest_week AS (
            SELECT MAX(date) as max_date
            FROM `aialgotradehits.crypto_trading_data.weekly_stocks_all`
        ),
        sector_stats AS (
            SELECT
                m.sector,
                COUNT(DISTINCT w.symbol) as stock_count,
                AVG(w.change_percent) as avg_change_pct,
                SUM(w.volume) as total_volume,
                STDDEV(w.change_percent) as volatility
            FROM `aialgotradehits.crypto_trading_data.weekly_stocks_all` w
            INNER JOIN `aialgotradehits.crypto_trading_data.v2_stocks_master` m
                ON w.symbol = m.symbol
            CROSS JOIN latest_week lw
            WHERE w.date = lw.max_date
              AND m.sector IS NOT NULL
              AND m.sector != ''
            GROUP BY m.sector
        )
        SELECT
            sector,
            stock_count,
            ROUND(avg_change_pct, 2) as avg_change_pct,
            total_volume,
            ROUND(volatility, 2) as volatility,
            RANK() OVER (ORDER BY avg_change_pct DESC) as momentum_rank
        FROM sector_stats
        ORDER BY avg_change_pct DESC
        """
        results = list(client.query(query).result())

        sectors = []
        for row in results:
            sectors.append({
                'sector': row.sector,
                'stock_count': row.stock_count,
                'avg_change_pct': row.avg_change_pct,
                'total_volume': row.total_volume,
                'volatility': row.volatility,
                'momentum_rank': row.momentum_rank
            })

        return jsonify({
            'success': True,
            'sectors': sectors,
            'count': len(sectors),
            'top_3': sectors[:3] if len(sectors) >= 3 else sectors
        })
    except Exception as e:
        logger.error(f"Get sector momentum error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/sector-momentum/<sector>/stocks', methods=['GET'])
def get_sector_top_stocks(sector):
    """Get top stocks within a sector"""
    try:
        limit = request.args.get('limit', 20, type=int)

        query = f"""
        WITH latest_week AS (
            SELECT MAX(date) as max_date
            FROM `aialgotradehits.crypto_trading_data.weekly_stocks_all`
        )
        SELECT
            w.symbol,
            m.sector,
            m.industry,
            w.close as price,
            w.volume,
            ROUND(w.change_percent, 2) as week_change_pct,
            ROW_NUMBER() OVER (ORDER BY w.change_percent DESC) as sector_rank
        FROM `aialgotradehits.crypto_trading_data.weekly_stocks_all` w
        INNER JOIN `aialgotradehits.crypto_trading_data.v2_stocks_master` m
            ON w.symbol = m.symbol
        CROSS JOIN latest_week lw
        WHERE w.date = lw.max_date
          AND m.sector = '{sector}'
          AND w.change_percent IS NOT NULL
        ORDER BY w.change_percent DESC
        LIMIT {limit}
        """
        results = list(client.query(query).result())

        stocks = []
        for row in results:
            stocks.append({
                'symbol': row.symbol,
                'sector': row.sector,
                'industry': row.industry,
                'price': row.price,
                'volume': row.volume,
                'week_change_pct': row.week_change_pct,
                'sector_rank': row.sector_rank
            })

        return jsonify({
            'success': True,
            'sector': sector,
            'stocks': stocks,
            'count': len(stocks)
        })
    except Exception as e:
        logger.error(f"Get sector stocks error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/paper-trades', methods=['GET'])
def get_paper_trades():
    """Get paper trades with optional filtering"""
    try:
        strategy_id = request.args.get('strategy_id', None)
        status = request.args.get('status', None)
        limit = request.args.get('limit', 100, type=int)

        where_clauses = []
        if strategy_id:
            where_clauses.append(f"strategy_id = '{strategy_id}'")
        if status:
            where_clauses.append(f"status = '{status}'")

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
        SELECT
            trade_id,
            strategy_id,
            symbol,
            asset_type,
            trade_type,
            quantity,
            entry_price,
            exit_price,
            entry_datetime,
            exit_datetime,
            hold_duration_minutes,
            position_size,
            gross_pnl,
            net_pnl,
            pnl_percent,
            cycle_number,
            status,
            exit_reason
        FROM `aialgotradehits.crypto_trading_data.paper_trades`
        {where_sql}
        ORDER BY entry_datetime DESC
        LIMIT {limit}
        """
        results = list(client.query(query).result())

        trades = []
        total_pnl = 0
        for row in results:
            trade = {
                'trade_id': row.trade_id,
                'strategy_id': row.strategy_id,
                'symbol': row.symbol,
                'asset_type': row.asset_type,
                'trade_type': row.trade_type,
                'quantity': row.quantity,
                'entry_price': row.entry_price,
                'exit_price': row.exit_price,
                'entry_datetime': row.entry_datetime.isoformat() if row.entry_datetime else None,
                'exit_datetime': row.exit_datetime.isoformat() if row.exit_datetime else None,
                'hold_duration_minutes': row.hold_duration_minutes,
                'position_size': row.position_size,
                'gross_pnl': row.gross_pnl,
                'net_pnl': row.net_pnl,
                'pnl_percent': row.pnl_percent,
                'cycle_number': row.cycle_number,
                'status': row.status,
                'exit_reason': row.exit_reason
            }
            trades.append(trade)
            if row.net_pnl:
                total_pnl += row.net_pnl

        return jsonify({
            'success': True,
            'trades': trades,
            'count': len(trades),
            'total_pnl': round(total_pnl, 2)
        })
    except Exception as e:
        logger.error(f"Get paper trades error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/paper-trades/summary', methods=['GET'])
def get_paper_trades_summary():
    """Get paper trading portfolio summary"""
    try:
        query = """
        SELECT
            strategy_id,
            COUNT(*) as total_trades,
            COUNTIF(status = 'open') as open_trades,
            COUNTIF(status = 'closed') as closed_trades,
            COUNTIF(net_pnl > 0) as winning_trades,
            COUNTIF(net_pnl <= 0) as losing_trades,
            SUM(net_pnl) as total_pnl,
            AVG(pnl_percent) as avg_pnl_pct,
            MAX(net_pnl) as best_trade,
            MIN(net_pnl) as worst_trade
        FROM `aialgotradehits.crypto_trading_data.paper_trades`
        GROUP BY strategy_id
        """
        results = list(client.query(query).result())

        summaries = []
        for row in results:
            win_rate = (row.winning_trades / row.closed_trades * 100) if row.closed_trades > 0 else 0
            summaries.append({
                'strategy_id': row.strategy_id,
                'total_trades': row.total_trades,
                'open_trades': row.open_trades,
                'closed_trades': row.closed_trades,
                'winning_trades': row.winning_trades,
                'losing_trades': row.losing_trades,
                'win_rate': round(win_rate, 1),
                'total_pnl': round(row.total_pnl or 0, 2),
                'avg_pnl_pct': round(row.avg_pnl_pct or 0, 2),
                'best_trade': round(row.best_trade or 0, 2),
                'worst_trade': round(row.worst_trade or 0, 2)
            })

        return jsonify({
            'success': True,
            'summaries': summaries,
            'total_strategies': len(summaries)
        })
    except Exception as e:
        logger.error(f"Get paper trades summary error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/strategy-backtests/<strategy_id>', methods=['GET'])
def get_strategy_backtests(strategy_id):
    """Get backtest results for a strategy"""
    try:
        query = f"""
        SELECT
            backtest_id,
            strategy_id,
            start_date,
            end_date,
            symbols_tested,
            total_trades,
            winning_trades,
            losing_trades,
            win_rate,
            starting_capital,
            ending_capital,
            total_return_pct,
            max_drawdown_pct,
            sharpe_ratio,
            avg_win_pct,
            avg_loss_pct,
            profit_factor,
            ai_summary,
            ai_recommendations,
            created_at
        FROM `aialgotradehits.crypto_trading_data.strategy_backtests`
        WHERE strategy_id = '{strategy_id}'
        ORDER BY created_at DESC
        LIMIT 20
        """
        results = list(client.query(query).result())

        backtests = []
        for row in results:
            backtests.append({
                'backtest_id': row.backtest_id,
                'strategy_id': row.strategy_id,
                'start_date': str(row.start_date) if row.start_date else None,
                'end_date': str(row.end_date) if row.end_date else None,
                'symbols_tested': list(row.symbols_tested) if row.symbols_tested else [],
                'total_trades': row.total_trades,
                'winning_trades': row.winning_trades,
                'losing_trades': row.losing_trades,
                'win_rate': row.win_rate,
                'starting_capital': row.starting_capital,
                'ending_capital': row.ending_capital,
                'total_return_pct': row.total_return_pct,
                'max_drawdown_pct': row.max_drawdown_pct,
                'sharpe_ratio': row.sharpe_ratio,
                'avg_win_pct': row.avg_win_pct,
                'avg_loss_pct': row.avg_loss_pct,
                'profit_factor': row.profit_factor,
                'ai_summary': row.ai_summary,
                'ai_recommendations': row.ai_recommendations,
                'created_at': row.created_at.isoformat() if row.created_at else None
            })

        return jsonify({
            'success': True,
            'strategy_id': strategy_id,
            'backtests': backtests,
            'count': len(backtests)
        })
    except Exception as e:
        logger.error(f"Get strategy backtests error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============== WEEKLY SUMMARY ENDPOINTS ==============

# Table mapping for daily data (has actual prices) - used to calculate weekly aggregates
DAILY_TABLE_MAP = {
    'stocks': 'stocks_daily_clean',
    'cryptos': 'crypto_daily_clean',
    'etfs': 'etfs_daily_clean',
    'forex': 'forex_daily_clean',
    'indices': 'indices_daily_clean',
    'commodities': 'v2_commodities_daily',
}

# Legacy weekly summary tables (metadata only, no prices)
WEEKLY_TABLE_MAP = {
    'stocks': 'stocks_daily_clean_summary',
    'cryptos': 'crypto_daily_clean',
    'etfs': 'etfs_daily_clean_summary',
    'forex': 'forex_daily_clean_summary',
    'indices': 'indices_daily_clean_summary',
    'commodities': 'commodities_daily_clean_summary',
}


@app.route('/api/weekly/<asset_type>', methods=['GET'])
def get_weekly_data(asset_type):
    """Get weekly summary data aggregated from daily data"""
    try:
        if asset_type not in DAILY_TABLE_MAP:
            return jsonify({
                'success': False,
                'error': f'Invalid asset type. Valid types: {list(DAILY_TABLE_MAP.keys())}'
            }), 400

        daily_table = DAILY_TABLE_MAP[asset_type]
        limit = request.args.get('limit', 500, type=int)
        limit = min(limit, 1000)  # Cap at 1000

        # Get the most recent week of data aggregated by symbol
        # Using only fields that exist in the v2 daily tables
        query = f"""
        WITH latest_data AS (
            SELECT
                symbol,
                name,
                asset_type,
                exchange,
                country,
                currency,
                close,
                open,
                high,
                low,
                volume,
                percent_change,
                week_52_high,
                week_52_low,
                atr,
                rsi,
                macd,
                macd_signal,
                adx,
                sma_20,
                sma_50,
                sma_200,
                bollinger_upper,
                bollinger_lower,
                datetime,
                ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.{daily_table}`
            WHERE close IS NOT NULL AND close > 0
        ),
        week_ago AS (
            SELECT
                symbol,
                close as week_ago_close,
                ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.{daily_table}`
            WHERE close IS NOT NULL AND close > 0
              AND datetime <= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        )
        SELECT
            l.symbol,
            l.name,
            l.asset_type as sector,
            l.exchange as industry,
            l.close as current_price,
            l.open as open_price,
            l.high as high_price,
            l.low as low_price,
            l.volume,
            COALESCE(
                ROUND((l.close - w.week_ago_close) / NULLIF(w.week_ago_close, 0) * 100, 2),
                l.percent_change
            ) as weekly_change_percent,
            l.percent_change as daily_change_percent,
            l.week_52_high,
            l.week_52_low,
            COALESCE(l.atr, 0) as volatility_weekly,
            CASE
                WHEN COALESCE(l.atr, 0) > 5 THEN 'high'
                WHEN COALESCE(l.atr, 0) > 2 THEN 'medium'
                ELSE 'low'
            END as volatility_category,
            CASE
                WHEN l.percent_change > 0 AND l.macd > l.macd_signal THEN 'bullish'
                WHEN l.percent_change < 0 AND l.macd < l.macd_signal THEN 'bearish'
                ELSE 'neutral'
            END as trend_short,
            l.rsi,
            l.macd,
            l.macd_signal,
            l.adx,
            l.sma_20,
            l.sma_50,
            l.sma_200,
            l.bollinger_upper,
            l.bollinger_lower,
            l.datetime
        FROM latest_data l
        LEFT JOIN week_ago w ON l.symbol = w.symbol AND w.rn = 1
        WHERE l.rn = 1
        ORDER BY weekly_change_percent DESC NULLS LAST
        LIMIT {limit}
        """

        results = client.query(query).result()
        data = []
        for row in results:
            item = dict(row)
            # Convert datetime to string if present
            if item.get('datetime'):
                item['datetime'] = item['datetime'].isoformat()
            data.append(item)

        return jsonify({
            'success': True,
            'asset_type': asset_type,
            'table': daily_table,
            'data': data,
            'count': len(data)
        })
    except Exception as e:
        logger.error(f"Get weekly data error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/weekly/<asset_type>/summary', methods=['GET'])
def get_weekly_summary(asset_type):
    """Get summary statistics for weekly data from daily tables"""
    try:
        if asset_type not in DAILY_TABLE_MAP:
            return jsonify({
                'success': False,
                'error': f'Invalid asset type. Valid types: {list(DAILY_TABLE_MAP.keys())}'
            }), 400

        daily_table = DAILY_TABLE_MAP[asset_type]

        # Get summary statistics from daily data (most recent record per symbol)
        query = f"""
        WITH latest_per_symbol AS (
            SELECT
                symbol,
                close,
                percent_change,
                atr,
                rsi,
                datetime,
                ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.{daily_table}`
            WHERE close IS NOT NULL AND close > 0
        ),
        recent_data AS (
            SELECT * FROM latest_per_symbol WHERE rn = 1
        )
        SELECT
            COUNT(DISTINCT symbol) as count,
            AVG(percent_change) as avg_change,
            MAX(percent_change) as max_gain,
            MIN(percent_change) as max_loss,
            AVG(atr) as avg_volatility,
            COUNT(CASE WHEN percent_change > 0 THEN 1 END) as gainers_count,
            COUNT(CASE WHEN percent_change < 0 THEN 1 END) as losers_count,
            AVG(rsi) as avg_rsi,
            MAX(datetime) as last_updated
        FROM recent_data
        """

        results = list(client.query(query).result())
        if results:
            row = results[0]
            return jsonify({
                'success': True,
                'asset_type': asset_type,
                'table': daily_table,
                'count': row.count or 0,
                'avg_change': safe_float(row.avg_change) if row.avg_change else 0,
                'max_gain': safe_float(row.max_gain) if row.max_gain else 0,
                'max_loss': safe_float(row.max_loss) if row.max_loss else 0,
                'avg_volatility': safe_float(row.avg_volatility) if row.avg_volatility else 0,
                'gainers_count': row.gainers_count or 0,
                'losers_count': row.losers_count or 0,
                'avg_rsi': safe_float(row.avg_rsi) if row.avg_rsi else 0,
                'last_updated': row.last_updated.isoformat() if row.last_updated else None
            })
        return jsonify({'success': True, 'count': 0, 'avg_change': 0})
    except Exception as e:
        logger.error(f"Get weekly summary error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============== DATA WAREHOUSE ENDPOINTS ==============

@app.route('/api/market-movers', methods=['GET'])
def get_market_movers():
    """Get top market movers (gainers/losers) from all asset types"""
    try:
        asset_type = request.args.get('type', 'all')  # stocks, etf, crypto, all
        direction = request.args.get('direction', 'all')  # gainers, losers, all
        limit = min(request.args.get('limit', 25, type=int), 100)

        # market_movers table schema: datetime, market, category, rank, symbol, name, exchange, price, change, percent_change, volume, market_cap, fetch_timestamp
        query = f"""
        SELECT
            symbol, name, market, category,
            price, change, percent_change,
            volume, market_cap, fetch_timestamp
        FROM `{DATA_PROJECT_ID}.{DATASET_ID}.market_movers`
        WHERE DATE(fetch_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
        """

        if asset_type != 'all':
            query += f" AND market = '{asset_type}'"
        if direction != 'all':
            query += f" AND category = '{direction}'"

        query += f" ORDER BY ABS(percent_change) DESC LIMIT {limit}"

        results = list(client.query(query).result())

        movers = []
        for row in results:
            movers.append({
                'symbol': row.symbol,
                'name': row.name,
                'asset_type': row.market,
                'direction': row.category,
                'price': safe_float(row.price) if row.price else None,
                'change_value': safe_float(row.change) if row.change else None,
                'change_percent': safe_float(row.percent_change) if row.percent_change else None,
                'volume': int(row.volume) if row.volume else None,
                'market_cap': safe_float(row.market_cap) if row.market_cap else None,
                'fetch_timestamp': row.fetch_timestamp.isoformat() if row.fetch_timestamp else None
            })

        # Group by direction
        gainers = [m for m in movers if m['direction'] == 'gainer']
        losers = [m for m in movers if m['direction'] == 'loser']

        return jsonify({
            'success': True,
            'count': len(movers),
            'gainers': gainers,
            'losers': losers,
            'all': movers
        })
    except Exception as e:
        logger.error(f"Market movers error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/fundamentals/profile/<symbol>', methods=['GET'])
def get_company_profile(symbol):
    """Get company profile/fundamentals for a symbol"""
    try:
        query = f"""
        SELECT *
        FROM `{DATA_PROJECT_ID}.{DATASET_ID}.fundamentals_company_profile`
        WHERE symbol = '{symbol}'
        ORDER BY fetch_timestamp DESC
        LIMIT 1
        """

        results = list(client.query(query).result())

        if not results:
            return jsonify({'success': False, 'error': 'Symbol not found'}), 404

        row = results[0]
        profile = {col: (safe_float(val) if isinstance(val, (int, float)) and col not in ['symbol', 'name', 'exchange', 'sector', 'industry', 'country', 'ceo', 'description', 'website', 'address', 'city', 'state', 'zip', 'phone'] else (val.isoformat() if hasattr(val, 'isoformat') else val)) for col, val in row.items()}

        return jsonify({
            'success': True,
            'symbol': symbol,
            'profile': profile
        })
    except Exception as e:
        logger.error(f"Company profile error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/fundamentals/statistics/<symbol>', methods=['GET'])
def get_company_statistics(symbol):
    """Get company statistics for a symbol"""
    try:
        query = f"""
        SELECT *
        FROM `{DATA_PROJECT_ID}.{DATASET_ID}.fundamentals_statistics`
        WHERE symbol = '{symbol}'
        ORDER BY fetch_timestamp DESC
        LIMIT 1
        """

        results = list(client.query(query).result())

        if not results:
            return jsonify({'success': False, 'error': 'Symbol not found'}), 404

        row = results[0]
        stats = {}
        for col, val in row.items():
            if hasattr(val, 'isoformat'):
                stats[col] = val.isoformat()
            elif isinstance(val, (int, float)) and val is not None:
                stats[col] = safe_float(val)
            else:
                stats[col] = val

        return jsonify({
            'success': True,
            'symbol': symbol,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Company statistics error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analyst/recommendations/<symbol>', methods=['GET'])
def get_analyst_recommendations(symbol):
    """Get analyst recommendations for a symbol"""
    try:
        query = f"""
        SELECT *
        FROM `{DATA_PROJECT_ID}.{DATASET_ID}.analyst_recommendations`
        WHERE symbol = '{symbol}'
        ORDER BY fetch_timestamp DESC
        LIMIT 10
        """

        results = list(client.query(query).result())

        recs = []
        for row in results:
            rec = {}
            for col, val in row.items():
                if hasattr(val, 'isoformat'):
                    rec[col] = val.isoformat()
                elif isinstance(val, (int, float)) and val is not None:
                    rec[col] = safe_float(val)
                else:
                    rec[col] = val
            recs.append(rec)

        return jsonify({
            'success': True,
            'symbol': symbol,
            'recommendations': recs,
            'count': len(recs)
        })
    except Exception as e:
        logger.error(f"Analyst recommendations error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analyst/price-targets/<symbol>', methods=['GET'])
def get_price_targets(symbol):
    """Get analyst price targets for a symbol"""
    try:
        query = f"""
        SELECT *
        FROM `{DATA_PROJECT_ID}.{DATASET_ID}.analyst_price_targets`
        WHERE symbol = '{symbol}'
        ORDER BY fetch_timestamp DESC
        LIMIT 1
        """

        results = list(client.query(query).result())

        if not results:
            return jsonify({'success': False, 'error': 'No price targets found'}), 404

        row = results[0]
        targets = {}
        for col, val in row.items():
            if hasattr(val, 'isoformat'):
                targets[col] = val.isoformat()
            elif isinstance(val, (int, float)) and val is not None:
                targets[col] = safe_float(val)
            else:
                targets[col] = val

        return jsonify({
            'success': True,
            'symbol': symbol,
            'price_targets': targets
        })
    except Exception as e:
        logger.error(f"Price targets error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/etf/profile/<symbol>', methods=['GET'])
def get_etf_profile(symbol):
    """Get ETF profile information"""
    try:
        query = f"""
        SELECT *
        FROM `{DATA_PROJECT_ID}.{DATASET_ID}.etf_profile`
        WHERE symbol = '{symbol}'
        ORDER BY fetch_timestamp DESC
        LIMIT 1
        """

        results = list(client.query(query).result())

        if not results:
            return jsonify({'success': False, 'error': 'ETF not found'}), 404

        row = results[0]
        profile = {}
        for col, val in row.items():
            if hasattr(val, 'isoformat'):
                profile[col] = val.isoformat()
            elif isinstance(val, (int, float)) and val is not None:
                profile[col] = safe_float(val)
            else:
                profile[col] = val

        return jsonify({
            'success': True,
            'symbol': symbol,
            'profile': profile
        })
    except Exception as e:
        logger.error(f"ETF profile error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/etf/performance/<symbol>', methods=['GET'])
def get_etf_performance(symbol):
    """Get ETF performance data"""
    try:
        query = f"""
        SELECT *
        FROM `{DATA_PROJECT_ID}.{DATASET_ID}.etf_performance`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT 30
        """

        results = list(client.query(query).result())

        performance = []
        for row in results:
            perf = {}
            for col, val in row.items():
                if hasattr(val, 'isoformat'):
                    perf[col] = val.isoformat()
                elif isinstance(val, (int, float)) and val is not None:
                    perf[col] = safe_float(val)
                else:
                    perf[col] = val
            performance.append(perf)

        return jsonify({
            'success': True,
            'symbol': symbol,
            'performance': performance,
            'count': len(performance)
        })
    except Exception as e:
        logger.error(f"ETF performance error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/etf/list', methods=['GET'])
def get_etf_list():
    """Get list of all ETFs with profiles"""
    try:
        limit = min(request.args.get('limit', 50, type=int), 200)

        query = f"""
        SELECT DISTINCT
            p.symbol, p.name, p.fund_family, p.fund_type,
            p.expense_ratio, p.total_assets, p.nav,
            p.category, perf.return_1d, perf.return_1y
        FROM `{DATA_PROJECT_ID}.{DATASET_ID}.etf_profile` p
        LEFT JOIN `{DATA_PROJECT_ID}.{DATASET_ID}.etf_performance` perf
            ON p.symbol = perf.symbol
        ORDER BY p.total_assets DESC NULLS LAST
        LIMIT {limit}
        """

        results = list(client.query(query).result())

        etfs = []
        for row in results:
            etfs.append({
                'symbol': row.symbol,
                'name': row.name,
                'fund_family': row.fund_family,
                'fund_type': row.fund_type,
                'expense_ratio': safe_float(row.expense_ratio) if row.expense_ratio else None,
                'total_assets': safe_float(row.total_assets) if row.total_assets else None,
                'nav': safe_float(row.nav) if row.nav else None,
                'category': row.category,
                'return_1d': safe_float(row.return_1d) if row.return_1d else None,
                'return_1y': safe_float(row.return_1y) if row.return_1y else None
            })

        return jsonify({
            'success': True,
            'etfs': etfs,
            'count': len(etfs)
        })
    except Exception as e:
        logger.error(f"ETF list error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/fundamentals/list', methods=['GET'])
def get_fundamentals_list():
    """Get list of all companies with fundamentals data"""
    try:
        limit = min(request.args.get('limit', 50, type=int), 200)
        sector = request.args.get('sector', None)

        query = f"""
        SELECT DISTINCT
            p.symbol, p.name, p.exchange, p.sector, p.industry,
            p.employees, s.market_cap, s.trailing_pe as pe_ratio,
            s.forward_pe, s.beta
        FROM `{DATA_PROJECT_ID}.{DATASET_ID}.fundamentals_company_profile` p
        LEFT JOIN `{DATA_PROJECT_ID}.{DATASET_ID}.fundamentals_statistics` s
            ON p.symbol = s.symbol
        """

        if sector:
            query += f" WHERE p.sector = '{sector}'"

        query += f" ORDER BY s.market_cap DESC NULLS LAST LIMIT {limit}"

        results = list(client.query(query).result())

        companies = []
        for row in results:
            companies.append({
                'symbol': row.symbol,
                'name': row.name,
                'exchange': row.exchange,
                'sector': row.sector,
                'industry': row.industry,
                'market_cap': safe_float(row.market_cap) if row.market_cap else None,
                'employees': int(row.employees) if row.employees else None,
                'pe_ratio': safe_float(row.pe_ratio) if row.pe_ratio else None,
                'forward_pe': safe_float(row.forward_pe) if row.forward_pe else None,
                'beta': safe_float(row.beta) if row.beta else None
            })

        return jsonify({
            'success': True,
            'companies': companies,
            'count': len(companies)
        })
    except Exception as e:
        logger.error(f"Fundamentals list error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============== DATA DOWNLOAD FEATURE (ML Training) ==============
# Based on Saleem's DATA_DOWNLOAD_FEATURE_LEAN.md specification

# User tier download limits
DOWNLOAD_LIMITS = {
    'regular': {
        'max_symbols': 10,
        'max_days': 730,  # 2 years
        'hourly_limit': 5
    },
    'power': {
        'max_symbols': 100,
        'max_days': 1825,  # 5 years
        'hourly_limit': 20
    },
    'admin': {
        'max_symbols': float('inf'),
        'max_days': float('inf'),
        'hourly_limit': float('inf')
    }
}

# Indicator groups for download selection
INDICATOR_GROUPS = {
    'momentum': {
        'name': 'Momentum',
        'count': 9,
        'fields': ['rsi', 'macd', 'macd_signal', 'macd_histogram',
                   'stoch_k', 'stoch_d', 'cci', 'williams_r', 'momentum']
    },
    'moving_averages': {
        'name': 'Moving Averages',
        'count': 9,
        'fields': ['sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_20',
                   'ema_26', 'ema_50', 'ema_200', 'kama']
    },
    'trend_volatility': {
        'name': 'Trend & Volatility',
        'count': 10,
        'fields': ['bollinger_upper', 'bollinger_middle', 'bollinger_lower',
                   'bb_width', 'adx', 'plus_di', 'minus_di', 'atr',
                   'trix', 'ultimate_osc']
    },
    'volume': {
        'name': 'Volume',
        'count': 3,
        'fields': ['obv', 'pvo', 'ppo']
    },
    'institutional': {
        'name': 'Institutional',
        'count': 13,
        'fields': ['vwap_daily', 'vwap_weekly', 'volume_profile_poc',
                   'volume_profile_vah', 'volume_profile_val', 'mfi', 'cmf',
                   'roc', 'ichimoku_tenkan', 'ichimoku_kijun',
                   'ichimoku_senkou_a', 'ichimoku_senkou_b', 'ichimoku_chikou']
    },
    'cycle_tracking': {
        'name': 'MA Crossover Cycles',
        'count': 9,
        'fields': ['golden_cross', 'death_cross', 'cycle_type', 'cycle_start_price',
                   'cycle_pnl_pct', 'cycle_peak', 'cycle_bottom', 'cycle_drawdown_pct',
                   'cycle_recovery_pct']
    },
    'candlestick_patterns': {
        'name': 'Candlestick Patterns',
        'count': 5,
        'fields': ['hammer', 'shooting_star', 'bullish_engulfing', 'bearish_engulfing', 'doji']
    },
    'volume_pressure': {
        'name': 'Volume Pressure',
        'count': 4,
        'fields': ['is_green', 'is_red', 'buy_pressure_pct', 'sell_pressure_pct']
    },
    'ml_features': {
        'name': 'ML Features',
        'count': 24,
        'fields': ['log_return', 'return_2w', 'return_4w',
                   'close_vs_sma20_pct', 'close_vs_sma50_pct',
                   'close_vs_sma200_pct', 'rsi_slope', 'rsi_zscore',
                   'ema20_slope', 'ema50_slope', 'atr_zscore', 'atr_slope',
                   'volume_zscore', 'volume_ratio', 'pivot_high_flag',
                   'pivot_low_flag', 'dist_to_pivot_high', 'dist_to_pivot_low',
                   'dist_to_pivot_high_pct', 'dist_to_pivot_low_pct',
                   'trend_regime', 'vol_regime', 'regime_confidence', 'macd_cross']
    }
}

# Predefined symbol lists
PREDEFINED_LISTS = {
    'sp500_top50': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'XOM',
                    'JNJ', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV', 'LLY',
                    'PEP', 'KO', 'COST', 'AVGO', 'WMT', 'MCD', 'CSCO', 'TMO', 'ACN', 'ABT',
                    'DHR', 'ADBE', 'CRM', 'NKE', 'CMCSA', 'NEE', 'LIN', 'VZ', 'TXN', 'PM',
                    'ORCL', 'RTX', 'HON', 'QCOM', 'INTC', 'IBM', 'AMGN', 'AMD', 'CAT', 'BA'],
    'nasdaq100_top30': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'ADBE', 'COST',
                        'PEP', 'CSCO', 'CMCSA', 'INTC', 'NFLX', 'AMD', 'TXN', 'QCOM', 'AMGN', 'HON',
                        'INTU', 'AMAT', 'ISRG', 'BKNG', 'ADP', 'SBUX', 'GILD', 'ADI', 'MDLZ', 'REGN'],
    'dow30': ['AAPL', 'MSFT', 'UNH', 'HD', 'V', 'JNJ', 'WMT', 'PG', 'JPM', 'CVX',
              'MRK', 'KO', 'DIS', 'CSCO', 'MCD', 'VZ', 'NKE', 'IBM', 'AXP', 'CAT',
              'HON', 'GS', 'BA', 'AMGN', 'MMM', 'TRV', 'WBA', 'DOW', 'INTC', 'CRM'],
    'crypto_top20': ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOGE', 'DOT', 'AVAX', 'SHIB',
                     'MATIC', 'LTC', 'TRX', 'LINK', 'ATOM', 'UNI', 'XLM', 'ALGO', 'VET', 'FIL']
}

def get_user_limits(subscription_tier):
    """Get download limits for user tier"""
    tier = subscription_tier.lower() if subscription_tier else 'regular'
    if tier in DOWNLOAD_LIMITS:
        return DOWNLOAD_LIMITS[tier]
    return DOWNLOAD_LIMITS['regular']

def check_download_limits(user_tier, symbols_count, days_count):
    """Check if download request is within user limits"""
    limits = get_user_limits(user_tier)

    if symbols_count > limits['max_symbols']:
        return False, f"Too many symbols. Your limit is {limits['max_symbols']}, requested {symbols_count}"

    if days_count > limits['max_days']:
        years = limits['max_days'] / 365
        return False, f"Date range too large. Your limit is {years:.0f} years ({limits['max_days']} days)"

    return True, "OK"

@app.route('/api/download/indicators', methods=['GET'])
def get_download_indicators():
    """Get available indicator groups for download selection"""
    return jsonify({
        'success': True,
        'indicator_groups': INDICATOR_GROUPS,
        'ohlcv_fields': ['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume']
    })

@app.route('/api/download/symbol-lists', methods=['GET'])
def get_predefined_symbol_lists():
    """Get predefined symbol lists for quick selection"""
    lists_info = {}
    for key, symbols in PREDEFINED_LISTS.items():
        lists_info[key] = {
            'name': key.replace('_', ' ').title(),
            'count': len(symbols),
            'symbols': symbols
        }
    return jsonify({
        'success': True,
        'predefined_lists': lists_info
    })

@app.route('/api/download/symbols/browse', methods=['GET'])
def browse_all_symbols():
    """Browse all available symbols organized by asset type with full names"""
    try:
        asset_type = request.args.get('type', 'all')

        # Asset type configurations with friendly names
        asset_configs = {
            'crypto': {
                'table': 'crypto_daily_clean',
                'label': 'Cryptocurrencies',
                'icon': '🪙',
                'format_hint': 'Use format: BTC/USD, ETH/USD'
            },
            'stock': {
                'table': 'stocks_daily_clean',
                'label': 'Stocks',
                'icon': '📈',
                'format_hint': 'Use ticker symbol: AAPL, MSFT'
            },
            'etf': {
                'table': 'v2_etfs_daily',
                'label': 'ETFs',
                'icon': '📊',
                'format_hint': 'Use ticker symbol: SPY, QQQ'
            },
            'forex': {
                'table': 'v2_forex_daily',
                'label': 'Forex',
                'icon': '💱',
                'format_hint': 'Use format: EURUSD, GBPUSD (no slash)'
            },
            'index': {
                'table': 'v2_indices_daily',
                'label': 'Indices',
                'icon': '📉',
                'format_hint': 'Use ticker symbol: SPX'
            },
            'commodity': {
                'table': 'v2_commodities_daily',
                'label': 'Commodities',
                'icon': '🛢️',
                'format_hint': 'Use: XAUUSD (gold), CL (oil)'
            }
        }

        result = {}
        types_to_query = [asset_type] if asset_type != 'all' else list(asset_configs.keys())

        for atype in types_to_query:
            if atype not in asset_configs:
                continue
            config = asset_configs[atype]
            try:
                query = f"""
                SELECT DISTINCT symbol, COALESCE(name, symbol) as name
                FROM `{PROJECT_ID}.{DATASET_ID}.{config['table']}`
                ORDER BY symbol
                LIMIT 500
                """
                query_results = client.query(query).result()
                symbols = []
                for row in query_results:
                    symbols.append({
                        'symbol': row.symbol,
                        'name': row.name if row.name else row.symbol
                    })
                result[atype] = {
                    'label': config['label'],
                    'icon': config['icon'],
                    'format_hint': config['format_hint'],
                    'count': len(symbols),
                    'symbols': symbols
                }
            except Exception as e:
                logger.warning(f"Error querying {atype}: {e}")
                result[atype] = {
                    'label': config['label'],
                    'icon': config['icon'],
                    'format_hint': config['format_hint'],
                    'count': 0,
                    'symbols': [],
                    'error': str(e)
                }

        # Add popular symbols quick reference
        popular = {
            'crypto': ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'DOGE/USD', 'ADA/USD'],
            'stock': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META'],
            'etf': ['SPY', 'QQQ', 'IWM', 'DIA', 'GLD', 'VOO'],
            'forex': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD'],
            'commodity': ['XAUUSD', 'XAGUSD', 'CL', 'NG']
        }

        return jsonify({
            'success': True,
            'assets': result,
            'popular': popular
        })
    except Exception as e:
        logger.error(f"Browse symbols error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download/symbols/search', methods=['GET'])
def search_symbols_for_download():
    """Search available symbols for download (all 7 asset types)"""
    query = request.args.get('q', '').upper().strip()
    asset_type = request.args.get('type', 'all')
    limit = int(request.args.get('limit', 20))

    if not query or len(query) < 1:
        return jsonify({'success': True, 'results': []})

    results = []

    # Asset type to table mapping
    asset_tables = {
        'stock': ('stocks_daily_clean', 'stock'),
        'crypto': ('crypto_daily_clean', 'crypto'),
        'etf': ('v2_etfs_daily', 'etf'),
        'forex': ('v2_forex_daily', 'forex'),
        'index': ('v2_indices_daily', 'index'),
        'commodity': ('v2_commodities_daily', 'commodity'),
        'interest_rate': ('v2_interest_rates_daily', 'interest_rate')
    }

    # Determine which asset types to search
    if asset_type == 'all':
        search_types = list(asset_tables.keys())
    elif asset_type in asset_tables:
        search_types = [asset_type]
    else:
        search_types = ['stock', 'crypto']  # Default fallback

    for search_type in search_types:
        table_name, type_label = asset_tables[search_type]
        # Search by both symbol AND name for better discovery
        search_query = f"""
        SELECT DISTINCT symbol, COALESCE(name, symbol) as name, '{type_label}' as type
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE UPPER(symbol) LIKE '{query}%'
           OR UPPER(COALESCE(name, '')) LIKE '%{query}%'
        ORDER BY
            CASE WHEN UPPER(symbol) = '{query}' THEN 0
                 WHEN UPPER(symbol) LIKE '{query}%' THEN 1
                 ELSE 2 END,
            symbol
        LIMIT {limit}
        """
        try:
            query_results = client.query(search_query).result()
            for row in query_results:
                results.append({
                    'symbol': row.symbol,
                    'name': row.name if row.name else row.symbol,
                    'type': type_label
                })
        except Exception as e:
            logger.warning(f"{search_type} search error: {e}")

    return jsonify({
        'success': True,
        'results': results[:limit],
        'query': query
    })

@app.route('/api/download/limits', methods=['GET'])
def get_download_limits():
    """Get download limits for current user tier"""
    user_tier = request.args.get('tier', 'regular')
    limits = get_user_limits(user_tier)

    return jsonify({
        'success': True,
        'tier': user_tier,
        'limits': {
            'max_symbols': limits['max_symbols'] if limits['max_symbols'] != float('inf') else 'unlimited',
            'max_days': limits['max_days'] if limits['max_days'] != float('inf') else 'unlimited',
            'max_years': limits['max_days'] / 365 if limits['max_days'] != float('inf') else 'unlimited',
            'hourly_limit': limits['hourly_limit'] if limits['hourly_limit'] != float('inf') else 'unlimited'
        }
    })

@app.route('/api/download/preview', methods=['POST'])
def preview_download():
    """Preview download: estimate rows, size, and show sample data"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        indicator_groups = data.get('indicator_groups', [])
        asset_type = data.get('asset_type', 'stock')
        user_tier = data.get('user_tier', 'regular')

        if not symbols:
            return jsonify({'success': False, 'error': 'No symbols selected'}), 400

        # Calculate date range in days
        from datetime import datetime as dt
        start = dt.strptime(start_date, '%Y-%m-%d')
        end = dt.strptime(end_date, '%Y-%m-%d')
        days_count = (end - start).days

        # Check limits
        allowed, message = check_download_limits(user_tier, len(symbols), days_count)
        if not allowed:
            return jsonify({'success': False, 'error': message, 'limit_exceeded': True}), 403

        # Build column list
        columns = ['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume']
        for group in indicator_groups:
            if group in INDICATOR_GROUPS:
                columns.extend(INDICATOR_GROUPS[group]['fields'])

        # Determine table based on asset type and timeframe (all 7 asset types)
        timeframe = data.get('timeframe', 'daily')
        TABLE_MAP = {
            ('stock', 'daily'): 'stocks_daily_clean',
            ('stock', 'hourly'): 'v2_stocks_hourly',
            ('stock', '5min'): 'v2_stocks_5min',
            ('crypto', 'daily'): 'crypto_daily_clean',
            ('crypto', 'hourly'): 'v2_crypto_hourly',
            ('crypto', '5min'): 'v2_crypto_5min',
            ('etf', 'daily'): 'v2_etfs_daily',
            ('etf', 'hourly'): 'v2_etfs_hourly',
            ('forex', 'daily'): 'v2_forex_daily',
            ('forex', 'hourly'): 'v2_forex_hourly',
            ('index', 'daily'): 'v2_indices_daily',
            ('index', 'hourly'): 'v2_indices_hourly',
            ('commodity', 'daily'): 'v2_commodities_daily',
            ('commodity', 'hourly'): 'v2_commodities_hourly',
            ('interest_rate', 'daily'): 'v2_interest_rates_daily',
        }
        table_name = TABLE_MAP.get((asset_type, timeframe), 'stocks_daily_clean')

        # Count rows estimate
        symbols_str = ','.join([f"'{s}'" for s in symbols])
        count_query = f"""
        SELECT COUNT(*) as row_count
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE symbol IN ({symbols_str})
          AND datetime >= '{start_date}'
          AND datetime <= '{end_date}'
        """

        count_result = client.query(count_query).result()
        row_count = list(count_result)[0].row_count

        # Estimate file size (rough: ~100 bytes per row per column for CSV)
        estimated_size_bytes = row_count * len(columns) * 15
        estimated_size_mb = estimated_size_bytes / (1024 * 1024)

        # Get sample data (first 10 rows of first symbol)
        first_symbol = symbols[0]
        sample_columns = columns[:10]  # Limit preview columns
        sample_query = f"""
        SELECT {', '.join(sample_columns)}
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE symbol = '{first_symbol}'
          AND datetime >= '{start_date}'
          AND datetime <= '{end_date}'
        ORDER BY datetime
        LIMIT 10
        """

        sample_data = []
        try:
            sample_results = client.query(sample_query).result()
            for row in sample_results:
                sample_data.append(sanitize_row(row))
        except Exception as e:
            logger.warning(f"Sample query error: {e}")

        return jsonify({
            'success': True,
            'preview': {
                'symbols_count': len(symbols),
                'date_range': f"{start_date} to {end_date}",
                'days_count': days_count,
                'columns_count': len(columns),
                'columns': columns,
                'estimated_rows': row_count,
                'estimated_size_mb': round(estimated_size_mb, 2),
                'estimated_time_seconds': max(5, row_count // 1000),  # Rough estimate
                'sample_data': sample_data,
                'sample_symbol': first_symbol
            }
        })
    except Exception as e:
        logger.error(f"Download preview error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/data', methods=['POST'])
def download_data():
    """Generate and download data as CSV or Excel"""
    try:
        import pandas as pd
        import tempfile
        import os as os_module
        from io import BytesIO

        data = request.get_json()
        symbols = data.get('symbols', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        indicator_groups = data.get('indicator_groups', [])
        asset_type = data.get('asset_type', 'stock')
        file_format = data.get('format', 'csv')  # 'csv' or 'excel'
        user_tier = data.get('user_tier', 'regular')

        if not symbols:
            return jsonify({'success': False, 'error': 'No symbols selected'}), 400

        # Calculate date range and check limits
        from datetime import datetime as dt
        start = dt.strptime(start_date, '%Y-%m-%d')
        end = dt.strptime(end_date, '%Y-%m-%d')
        days_count = (end - start).days

        allowed, message = check_download_limits(user_tier, len(symbols), days_count)
        if not allowed:
            return jsonify({'success': False, 'error': message, 'limit_exceeded': True}), 403

        # Build column list
        columns = ['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume']
        for group in indicator_groups:
            if group in INDICATOR_GROUPS:
                # Only add columns that exist in the database
                for field in INDICATOR_GROUPS[group]['fields']:
                    if field not in columns:
                        columns.append(field)

        # Determine table based on asset type and timeframe (all 7 asset types)
        timeframe = data.get('timeframe', 'daily')
        TABLE_MAP = {
            ('stock', 'daily'): 'stocks_daily_clean',
            ('stock', 'hourly'): 'v2_stocks_hourly',
            ('stock', '5min'): 'v2_stocks_5min',
            ('crypto', 'daily'): 'crypto_daily_clean',
            ('crypto', 'hourly'): 'v2_crypto_hourly',
            ('crypto', '5min'): 'v2_crypto_5min',
            ('etf', 'daily'): 'v2_etfs_daily',
            ('etf', 'hourly'): 'v2_etfs_hourly',
            ('forex', 'daily'): 'v2_forex_daily',
            ('forex', 'hourly'): 'v2_forex_hourly',
            ('index', 'daily'): 'v2_indices_daily',
            ('index', 'hourly'): 'v2_indices_hourly',
            ('commodity', 'daily'): 'v2_commodities_daily',
            ('commodity', 'hourly'): 'v2_commodities_hourly',
            ('interest_rate', 'daily'): 'v2_interest_rates_daily',
        }
        table_name = TABLE_MAP.get((asset_type, timeframe), 'stocks_daily_clean')

        # Query data
        symbols_str = ','.join([f"'{s}'" for s in symbols])

        # Get available columns from schema to avoid errors
        schema_query = f"""
        SELECT column_name
        FROM `{PROJECT_ID}.{DATASET_ID}.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = '{table_name}'
        """
        available_columns = set()
        try:
            schema_result = client.query(schema_query).result()
            for row in schema_result:
                available_columns.add(row.column_name)
        except Exception as e:
            logger.warning(f"Could not fetch schema: {e}")
            # Use all columns as fallback
            available_columns = set(columns)

        # Filter to only available columns
        valid_columns = [c for c in columns if c in available_columns]

        data_query = f"""
        SELECT {', '.join(valid_columns)}
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE symbol IN ({symbols_str})
          AND datetime >= '{start_date}'
          AND datetime <= '{end_date}'
        ORDER BY symbol, datetime
        """

        logger.info(f"Download query: {data_query}")

        query_result = client.query(data_query).result()
        rows = [sanitize_row(row) for row in query_result]

        if not rows:
            return jsonify({'success': False, 'error': 'No data found for selected criteria'}), 404

        df = pd.DataFrame(rows)

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        symbol_count = len(symbols)

        if file_format == 'excel':
            # Create Excel with one sheet per symbol
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for symbol in symbols:
                    symbol_df = df[df['symbol'] == symbol].copy()
                    if not symbol_df.empty:
                        symbol_df = symbol_df.drop('symbol', axis=1)  # Remove redundant symbol column
                        # Clean sheet name (Excel has 31 char limit)
                        sheet_name = symbol[:31].replace('/', '_')
                        symbol_df.to_excel(writer, sheet_name=sheet_name, index=False)

            output.seek(0)
            filename = f"trading_data_{timestamp}_{symbol_count}symbols.xlsx"

            return Response(
                output.getvalue(),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={
                    'Content-Disposition': f'attachment; filename={filename}',
                    'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                }
            )
        else:
            # CSV format
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            filename = f"trading_data_{timestamp}_{symbol_count}symbols.csv"

            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename={filename}',
                    'Content-Type': 'text/csv'
                }
            )

    except Exception as e:
        logger.error(f"Download data error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/available-symbols', methods=['GET'])
def get_download_available_symbols():
    """Get all available symbols for download"""
    asset_type = request.args.get('type', 'stock')

    table_name = 'stocks_daily_clean' if asset_type == 'stock' else 'crypto_daily_clean'

    query = f"""
    SELECT DISTINCT symbol, MIN(datetime) as earliest_date, MAX(datetime) as latest_date, COUNT(*) as record_count
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    GROUP BY symbol
    ORDER BY symbol
    """

    try:
        results = client.query(query).result()
        symbols = []
        for row in results:
            symbols.append({
                'symbol': row.symbol,
                'earliest_date': row.earliest_date.isoformat() if row.earliest_date else None,
                'latest_date': row.latest_date.isoformat() if row.latest_date else None,
                'record_count': row.record_count
            })

        return jsonify({
            'success': True,
            'asset_type': asset_type,
            'symbols': symbols,
            'count': len(symbols)
        })
    except Exception as e:
        logger.error(f"Available symbols error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# ML MODEL TEST DATA ENDPOINTS
# =====================================================

# ML Test Data Presets - 10 pre-configured datasets for model validation
ML_TEST_PRESETS = {
    1: {'symbol': 'SPY', 'train_start': '2015-01-01', 'train_end': '2022-12-31', 'test_start': '2023-01-01', 'test_end': '2024-12-31', 'name': 'Test 1: Standard Split'},
    2: {'symbol': 'SPY', 'train_start': '2010-01-01', 'train_end': '2022-12-31', 'test_start': '2023-01-01', 'test_end': '2024-12-31', 'name': 'Test 2: Extended Training'},
    3: {'symbol': 'SPY', 'train_start': '2018-01-01', 'train_end': '2023-12-31', 'test_start': '2024-01-01', 'test_end': '2024-12-31', 'name': 'Test 3: Recent Focus'},
    4: {'symbol': 'SPY', 'train_start': '2006-01-01', 'train_end': '2020-02-28', 'test_start': '2021-01-01', 'test_end': '2024-12-31', 'name': 'Test 4: Pre/Post COVID'},
    5: {'symbol': 'QQQ', 'train_start': '2015-01-01', 'train_end': '2023-12-31', 'val_end': '2024-09-30', 'test_start': '2024-10-01', 'test_end': '2024-12-31', 'name': 'Test 5: Tech ETF (QQQ)'},
    6: {'symbol': 'AAPL', 'train_start': '2015-01-01', 'train_end': '2023-12-31', 'val_end': '2024-09-30', 'test_start': '2024-10-01', 'test_end': '2024-12-31', 'name': 'Test 6: Individual Stock (AAPL)'},
    7: {'symbol': 'BTC/USD', 'train_start': '2018-01-01', 'train_end': '2023-12-31', 'val_end': '2024-09-30', 'test_start': '2024-10-01', 'test_end': '2024-12-31', 'name': 'Test 7: Crypto (BTC)'},
    8: {'symbol': 'SPY', 'train_start': '2006-01-01', 'train_end': '2019-12-31', 'test_start': '2020-01-01', 'test_end': '2020-12-31', 'name': 'Test 8: COVID Crash'},
    9: {'symbol': 'SPY', 'train_start': '2006-01-01', 'train_end': '2021-12-31', 'test_start': '2022-01-01', 'test_end': '2022-12-31', 'name': 'Test 9: Bear Market 2022'},
    10: {'symbols': ['SPY', 'QQQ', 'AAPL'], 'train_start': '2015-01-01', 'train_end': '2023-12-31', 'test_start': '2024-01-01', 'test_end': '2024-12-31', 'name': 'Test 10: Multi-Asset Combined'}
}

@app.route('/api/download/ml-test-presets', methods=['GET'])
def get_ml_test_presets():
    """Get available ML test data presets"""
    return jsonify({
        'success': True,
        'presets': ML_TEST_PRESETS,
        'count': len(ML_TEST_PRESETS)
    })

@app.route('/api/download/ml-test-data', methods=['GET'])
def download_ml_test_data():
    """Download ML test data with train/test split"""
    try:
        import pandas as pd
        from io import BytesIO, StringIO

        # Get parameters
        symbols_str = request.args.get('symbols', '')
        train_start = request.args.get('train_start')
        train_end = request.args.get('train_end')
        test_start = request.args.get('test_start')
        test_end = request.args.get('test_end')
        val_end = request.args.get('val_end')
        file_format = request.args.get('format', 'csv')
        test_id = request.args.get('test_id', '0')
        test_name = request.args.get('test_name', 'custom')

        if not symbols_str or not train_start or not train_end or not test_start or not test_end:
            return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

        symbols = [s.strip() for s in symbols_str.split(',') if s.strip()]

        # Build columns list with all indicators
        columns = [
            'datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume',
            'rsi', 'macd', 'macd_signal', 'macd_histogram',
            'bollinger_upper', 'bollinger_middle', 'bollinger_lower',
            'sma_20', 'sma_50', 'sma_200',
            'ema_12', 'ema_26', 'ema_50', 'ema_200',
            'adx', 'atr', 'cci', 'williams_r',
            'stoch_k', 'stoch_d', 'obv', 'momentum', 'roc'
        ]

        # Determine table based on symbol (crypto vs stock/etf)
        all_data = []

        for symbol in symbols:
            # Determine table based on symbol type
            if '/' in symbol or symbol in ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']:
                table_name = 'crypto_daily_clean'
                # Convert symbol format
                db_symbol = symbol.replace('/', '')
            elif symbol in ['SPY', 'QQQ', 'DIA', 'IWM', 'VOO', 'VTI', 'ARKK']:
                table_name = 'v2_etfs_daily'
                db_symbol = symbol
            else:
                table_name = 'stocks_daily_clean'
                db_symbol = symbol

            # Get available columns for the table
            schema_query = f"""
            SELECT column_name
            FROM `{PROJECT_ID}.{DATASET_ID}.INFORMATION_SCHEMA.COLUMNS`
            WHERE table_name = '{table_name}'
            """
            available_columns = set()
            try:
                schema_result = client.query(schema_query).result()
                for row in schema_result:
                    available_columns.add(row.column_name)
            except Exception as e:
                logger.warning(f"Could not fetch schema for {table_name}: {e}")
                available_columns = set(columns)

            # Filter to available columns
            valid_columns = [c for c in columns if c in available_columns]

            # Query full date range (train + test)
            full_start = train_start
            full_end = test_end

            query = f"""
            SELECT {', '.join(valid_columns)}
            FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
            WHERE symbol = '{db_symbol}'
              AND datetime >= '{full_start}'
              AND datetime <= '{full_end}'
            ORDER BY datetime
            """

            try:
                results = client.query(query).result()
                rows = [sanitize_row(row) for row in results]

                # Add data_split column
                for row in rows:
                    dt = row.get('datetime', '')
                    if isinstance(dt, str):
                        dt_str = dt[:10]
                    else:
                        dt_str = dt.isoformat()[:10] if hasattr(dt, 'isoformat') else str(dt)[:10]

                    if dt_str <= train_end:
                        row['data_split'] = 'train'
                    elif val_end and dt_str <= val_end:
                        row['data_split'] = 'validation'
                    else:
                        row['data_split'] = 'test'

                all_data.extend(rows)
                logger.info(f"Fetched {len(rows)} rows for {symbol} from {table_name}")

            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                continue

        if not all_data:
            return jsonify({'success': False, 'error': 'No data found for selected symbols and date range'}), 404

        df = pd.DataFrame(all_data)

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        symbol_label = symbols[0] if len(symbols) == 1 else 'combined'
        filename_base = f"ml_test_{test_id}_{symbol_label}_{timestamp}"

        if file_format == 'xlsx':
            # Excel format with separate sheets for train/test
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Full data sheet
                df.to_excel(writer, sheet_name='All_Data', index=False)

                # Train data sheet
                train_df = df[df['data_split'] == 'train']
                if not train_df.empty:
                    train_df.to_excel(writer, sheet_name='Train', index=False)

                # Validation data sheet (if exists)
                if val_end:
                    val_df = df[df['data_split'] == 'validation']
                    if not val_df.empty:
                        val_df.to_excel(writer, sheet_name='Validation', index=False)

                # Test data sheet
                test_df = df[df['data_split'] == 'test']
                if not test_df.empty:
                    test_df.to_excel(writer, sheet_name='Test', index=False)

                # Info sheet
                info_data = {
                    'Property': ['Test ID', 'Test Name', 'Symbols', 'Train Period', 'Test Period', 'Total Rows', 'Train Rows', 'Test Rows', 'Columns', 'Generated'],
                    'Value': [test_id, test_name, ', '.join(symbols), f"{train_start} to {train_end}", f"{test_start} to {test_end}",
                              len(df), len(train_df), len(test_df), len(df.columns), datetime.now().isoformat()]
                }
                pd.DataFrame(info_data).to_excel(writer, sheet_name='Info', index=False)

            output.seek(0)
            filename = f"{filename_base}.xlsx"

            return Response(
                output.getvalue(),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                }
            )
        else:
            # CSV format
            output = StringIO()
            df.to_csv(output, index=False)
            filename = f"{filename_base}.csv"

            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Type': 'text/csv; charset=utf-8'
                }
            )

    except Exception as e:
        logger.error(f"ML test data download error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# FINNHUB DATA ENDPOINTS
# =====================================================

@app.route('/api/finnhub/news', methods=['GET'])
def get_finnhub_news():
    """Get market news from Finnhub"""
    category = request.args.get('category', 'general')
    limit = min(int(request.args.get('limit', 50)), 100)
    try:
        query = f"""
        SELECT id, category, datetime, headline, source, summary, url, related
        FROM `{PROJECT_ID}.{DATASET_ID}.market_news`
        WHERE category = '{category}' OR '{category}' = 'all'
        ORDER BY datetime DESC
        LIMIT {limit}
        """
        results = client.query(query).result()
        news = [sanitize_row(row) for row in results]
        return jsonify({'success': True, 'news': news, 'count': len(news)})
    except Exception as e:
        logger.error(f"Finnhub news error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/finnhub/recommendations', methods=['GET'])
def get_finnhub_recommendations():
    """Get analyst recommendations from Finnhub"""
    symbol = request.args.get('symbol', '')
    try:
        where_clause = f"WHERE symbol = '{symbol}'" if symbol else ""
        query = f"""
        SELECT symbol, period, strong_buy, buy, hold, sell, strong_sell,
               total_analysts, consensus, fetch_timestamp
        FROM `{PROJECT_ID}.{DATASET_ID}.finnhub_analyst_recommendations`
        {where_clause}
        ORDER BY fetch_timestamp DESC, period DESC
        LIMIT 100
        """
        results = client.query(query).result()
        recommendations = [sanitize_row(row) for row in results]
        return jsonify({'success': True, 'recommendations': recommendations, 'count': len(recommendations)})
    except Exception as e:
        logger.error(f"Finnhub recommendations error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/finnhub/insider-transactions', methods=['GET'])
def get_finnhub_insider_transactions():
    """Get insider transactions from Finnhub"""
    symbol = request.args.get('symbol', '')
    limit = min(int(request.args.get('limit', 50)), 200)
    try:
        where_clause = f"WHERE symbol = '{symbol}'" if symbol else ""
        query = f"""
        SELECT symbol, name, position, transaction_code, transaction_date,
               transaction_price, shares, value, filing_date
        FROM `{PROJECT_ID}.{DATASET_ID}.finnhub_insider_transactions`
        {where_clause}
        ORDER BY transaction_date DESC, filing_date DESC
        LIMIT {limit}
        """
        results = client.query(query).result()
        transactions = [sanitize_row(row) for row in results]
        return jsonify({'success': True, 'transactions': transactions, 'count': len(transactions)})
    except Exception as e:
        logger.error(f"Finnhub insider transactions error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/finnhub/company-news', methods=['GET'])
def get_finnhub_company_news():
    """Get company-specific news from Finnhub"""
    symbol = request.args.get('symbol', '')
    limit = min(int(request.args.get('limit', 20)), 100)
    if not symbol:
        return jsonify({'success': False, 'error': 'Symbol required'}), 400
    try:
        query = f"""
        SELECT symbol, id, category, datetime, headline, source, summary, url
        FROM `{PROJECT_ID}.{DATASET_ID}.company_news`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT {limit}
        """
        results = client.query(query).result()
        news = [sanitize_row(row) for row in results]
        return jsonify({'success': True, 'news': news, 'count': len(news)})
    except Exception as e:
        logger.error(f"Finnhub company news error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/capabilities', methods=['GET'])
def ai_capabilities():
    """Get available AI capabilities and service status"""
    capabilities = {
        'vertex_ai': VERTEX_AI_AVAILABLE,
        'gemini_model': GEMINI_MODEL,
        'models_available': GEMINI_MODEL_PRIORITY if VERTEX_AI_AVAILABLE else [],
        'features': {
            'pattern_recognition': VERTEX_AI_AVAILABLE,
            'predictions': VERTEX_AI_AVAILABLE,
            'smart_search': VERTEX_AI_AVAILABLE,
            'finnhub_news': True,
            'finnhub_recommendations': True,
            'finnhub_insider_transactions': True,
        },
        'google_ai_services': {
            'vertex_ai': 'Active - ML Platform',
            'gemini': f'Active - {GEMINI_MODEL}' if GEMINI_MODEL else 'Not initialized',
            'bigquery_ml': 'Active',
        }
    }
    return jsonify({'success': True, 'capabilities': capabilities})

# Log all registered routes
logger.info("Registered routes:")
for rule in app.url_map.iter_rules():
    logger.info(f"  {rule.rule} -> {rule.methods}")

import os



# ============== TRADING ALERTS API ==============

@app.route('/api/alerts/price-anomalies', methods=['GET'])
def get_price_anomalies():
    """Get recent price anomaly alerts"""
    try:
        if get_alert_system is None:
            return jsonify({'success': False, 'error': 'Alert system not available'}), 503

        asset_type = request.args.get('asset_type', 'stocks')
        lookback = int(request.args.get('lookback', 20))

        alert_system = get_alert_system()
        alerts = alert_system.detect_price_anomalies(asset_type, lookback)

        return jsonify({
            'success': True,
            'asset_type': asset_type,
            'alert_count': len(alerts),
            'alerts': alerts
        })
    except Exception as e:
        logger.error(f"Price anomalies error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts/volume-surges', methods=['GET'])
def get_volume_surges():
    """Get volume surge alerts"""
    try:
        if get_alert_system is None:
            return jsonify({'success': False, 'error': 'Alert system not available'}), 503

        asset_type = request.args.get('asset_type', 'stocks')

        alert_system = get_alert_system()
        alerts = alert_system.detect_volume_surges(asset_type)

        return jsonify({
            'success': True,
            'asset_type': asset_type,
            'alert_count': len(alerts),
            'alerts': alerts
        })
    except Exception as e:
        logger.error(f"Volume surges error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts/technical-signals', methods=['GET'])
def get_technical_signals():
    """Get technical trading signals"""
    try:
        if get_alert_system is None:
            return jsonify({'success': False, 'error': 'Alert system not available'}), 503

        asset_type = request.args.get('asset_type', 'stocks')

        alert_system = get_alert_system()
        signals = alert_system.detect_technical_signals(asset_type)

        return jsonify({
            'success': True,
            'asset_type': asset_type,
            'signal_count': len(signals),
            'signals': signals
        })
    except Exception as e:
        logger.error(f"Technical signals error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts/market-summary', methods=['GET'])
def get_market_alert_summary():
    """Get comprehensive market alert summary"""
    try:
        if get_alert_system is None:
            return jsonify({'success': False, 'error': 'Alert system not available'}), 503

        alert_system = get_alert_system()
        summary = alert_system.get_market_summary()

        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        logger.error(f"Market summary error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts/symbol/<path:symbol>', methods=['GET'])
def get_symbol_alerts(symbol):
    """Get all alerts for a specific symbol"""
    try:
        asset_type = request.args.get('asset_type', 'stocks')
        table = 'stocks_daily_clean' if asset_type == 'stocks' else 'crypto_daily_clean'

        query = f"""
        SELECT
            symbol, datetime, close, volume, rsi, macd, macd_signal, adx,
            golden_cross, death_cross, cycle_type, cycle_pnl_pct,
            hammer, shooting_star, bullish_engulfing, bearish_engulfing,
            buy_pressure_pct, sell_pressure_pct, trend_regime
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT 30
        """

        df = client.query(query).to_dataframe()

        if df.empty:
            return jsonify({'success': False, 'error': f'No data found for {symbol}'}), 404

        latest = df.iloc[0]
        alerts = []

        # Check various alert conditions
        if pd.notna(latest.get('golden_cross')) and latest['golden_cross'] == 1:
            alerts.append({'type': 'GOLDEN_CROSS', 'direction': 'BULLISH', 'strength': 'HIGH'})
        if pd.notna(latest.get('death_cross')) and latest['death_cross'] == 1:
            alerts.append({'type': 'DEATH_CROSS', 'direction': 'BEARISH', 'strength': 'HIGH'})
        if pd.notna(latest.get('rsi')) and latest['rsi'] > 70:
            alerts.append({'type': 'RSI_OVERBOUGHT', 'direction': 'BEARISH', 'strength': 'MEDIUM', 'value': float(latest['rsi'])})
        if pd.notna(latest.get('rsi')) and latest['rsi'] < 30:
            alerts.append({'type': 'RSI_OVERSOLD', 'direction': 'BULLISH', 'strength': 'MEDIUM', 'value': float(latest['rsi'])})
        if pd.notna(latest.get('hammer')) and latest['hammer'] == 1:
            alerts.append({'type': 'HAMMER_PATTERN', 'direction': 'BULLISH', 'strength': 'MEDIUM'})
        if pd.notna(latest.get('shooting_star')) and latest['shooting_star'] == 1:
            alerts.append({'type': 'SHOOTING_STAR', 'direction': 'BEARISH', 'strength': 'MEDIUM'})
        if pd.notna(latest.get('bullish_engulfing')) and latest['bullish_engulfing'] == 1:
            alerts.append({'type': 'BULLISH_ENGULFING', 'direction': 'BULLISH', 'strength': 'HIGH'})
        if pd.notna(latest.get('bearish_engulfing')) and latest['bearish_engulfing'] == 1:
            alerts.append({'type': 'BEARISH_ENGULFING', 'direction': 'BEARISH', 'strength': 'HIGH'})

        return jsonify({
            'success': True,
            'symbol': symbol,
            'latest_price': float(latest['close']),
            'latest_date': latest['datetime'].isoformat() if hasattr(latest['datetime'], 'isoformat') else str(latest['datetime']),
            'rsi': float(latest['rsi']) if pd.notna(latest.get('rsi')) else None,
            'adx': float(latest['adx']) if pd.notna(latest.get('adx')) else None,
            'trend_regime': int(latest['trend_regime']) if pd.notna(latest.get('trend_regime')) else 0,
            'cycle_pnl': float(latest['cycle_pnl_pct']) if pd.notna(latest.get('cycle_pnl_pct')) else None,
            'buy_pressure': float(latest['buy_pressure_pct']) if pd.notna(latest.get('buy_pressure_pct')) else None,
            'sell_pressure': float(latest['sell_pressure_pct']) if pd.notna(latest.get('sell_pressure_pct')) else None,
            'alerts': alerts,
            'alert_count': len(alerts)
        })

    except Exception as e:
        logger.error(f"Symbol alerts error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Get port from environment variable (Cloud Run) or default to 8080
    port = int(os.environ.get('PORT', 8080))

    print("\n" + "="*80)
    print("TRADING API SERVER STARTING")
    print("="*80)
    print(f"Server running on http://0.0.0.0:{port}")
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print("\nAvailable endpoints:")
    print("  GET /api/stocks/history?symbol=NVDA&limit=500")
    print("  GET /api/stocks/15min/history?symbol=NVDA&limit=500")
    print("  GET /api/stocks/5min/history?symbol=NVDA&limit=500")
    print("  GET /api/crypto/daily/history?pair=BTC/USD&limit=500")
    print("  GET /api/crypto/15min/history?pair=BTC/USD&limit=500")
    print("  GET /api/crypto/5min/history?pair=BTC/USD&limit=500")
    print("  GET /api/summary/stock")
    print("  GET /api/summary/crypto")
    print("  GET /health")
    print("="*80 + "\n")

    app.run(host='0.0.0.0', port=port, debug=False)

# ============== ADMIN TABLE COUNTS ENDPOINT ==============
@app.route('/api/admin/table-counts', methods=['GET'])
def get_table_counts():
    """Get row counts and sizes for all BigQuery tables - for Database Summary XLSX download"""
    try:
        # Query to get table information from __TABLES__ metadata
        query = f"""
        SELECT
            table_id as table_name,
            CASE
                WHEN table_id LIKE '%stock%' OR table_id LIKE '%Stock%' THEN 'stocks'
                WHEN table_id LIKE '%crypto%' OR table_id LIKE '%Crypto%' THEN 'crypto'
                WHEN table_id LIKE '%forex%' OR table_id LIKE '%Forex%' THEN 'forex'
                WHEN table_id LIKE '%etf%' OR table_id LIKE '%ETF%' THEN 'etfs'
                WHEN table_id LIKE '%indic%' OR table_id LIKE '%Indic%' THEN 'indices'
                WHEN table_id LIKE '%commodit%' OR table_id LIKE '%Commodit%' THEN 'commodities'
                WHEN table_id LIKE '%fundamental%' THEN 'fundamentals'
                WHEN table_id LIKE '%analyst%' THEN 'analyst'
                WHEN table_id LIKE '%earning%' THEN 'corporate_actions'
                WHEN table_id LIKE '%dividend%' THEN 'corporate_actions'
                WHEN table_id LIKE '%split%' THEN 'corporate_actions'
                WHEN table_id LIKE '%ipo%' THEN 'corporate_actions'
                ELSE 'other'
            END as category,
            row_count,
            ROUND(size_bytes / 1024 / 1024, 2) as size_mb
        FROM `{PROJECT_ID}.{DATASET_ID}.__TABLES__`
        WHERE table_id NOT LIKE '%TABLES%'
        ORDER BY row_count DESC
        """

        query_job = client.query(query)
        results = list(query_job.result())

        tables = []
        for row in results:
            tables.append({
                'table_name': row.table_name,
                'category': row.category,
                'row_count': int(row.row_count) if row.row_count else 0,
                'size_mb': safe_float(row.size_mb) if row.size_mb else 0.0
            })

        logger.info(f"✅ Fetched {len(tables)} table counts for Database Summary")

        return jsonify({
            'success': True,
            'tables': tables,
            'count': len(tables)
        })

    except Exception as e:
        logger.error(f"❌ Error fetching table counts: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'tables': [],
            'count': 0
        }), 500


# ============== ML PREDICTION ENDPOINTS ==============
ML_DATASET = 'ml_models'

@app.route('/api/ml/predictions', methods=['GET'])
def get_ml_predictions():
    """
    Get ML predictions from walk-forward model.

    Query params:
    - asset_type: stocks, crypto, etf (default: all)
    - confidence: HIGH, MEDIUM, LOW (default: all)
    - signal: BUY, SELL, HOLD (default: all)
    - limit: max results (default: 50)
    """
    asset_type = request.args.get('asset_type', 'all')
    confidence = request.args.get('confidence', 'all')
    signal = request.args.get('signal', 'all')
    limit = int(request.args.get('limit', 50))

    query = f"""
    SELECT
        asset_type,
        symbol,
        FORMAT_TIMESTAMP('%Y-%m-%d %H:%M', datetime) as datetime,
        ROUND(close, 2) as price,
        ROUND(up_probability * 100, 1) as up_probability_pct,
        predicted_direction,
        CASE
            WHEN up_probability >= 0.65 OR up_probability <= 0.35 THEN 'HIGH'
            WHEN up_probability >= 0.55 OR up_probability <= 0.45 THEN 'MEDIUM'
            ELSE 'LOW'
        END as confidence_level,
        CASE
            WHEN up_probability >= 0.60 THEN 'BUY'
            WHEN up_probability <= 0.40 THEN 'SELL'
            ELSE 'HOLD'
        END as signal,
        ROUND(rsi, 1) as rsi,
        growth_score,
        trend_regime
    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions_v2`
    WHERE data_split = 'VALIDATE'
    """

    if asset_type != 'all':
        query += f" AND asset_type = '{asset_type}'"

    if confidence != 'all':
        if confidence == 'HIGH':
            query += " AND (up_probability >= 0.65 OR up_probability <= 0.35)"
        elif confidence == 'MEDIUM':
            query += " AND (up_probability BETWEEN 0.45 AND 0.55)"

    if signal == 'BUY':
        query += " AND up_probability >= 0.60"
    elif signal == 'SELL':
        query += " AND up_probability <= 0.40"

    query += f" ORDER BY datetime DESC LIMIT {limit}"

    try:
        results = list(client.query(query).result())
        predictions = [sanitize_row(row) for row in results]

        return jsonify({
            'status': 'success',
            'count': len(predictions),
            'model': 'xgboost_walk_forward_v2',
            'filters': {'asset_type': asset_type, 'confidence': confidence, 'signal': signal},
            'predictions': predictions
        })
    except Exception as e:
        logger.error(f"ML predictions error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/ml/high-confidence-signals', methods=['GET'])
def get_high_confidence_signals():
    """
    Get HIGH confidence signals only (best accuracy).

    Query params:
    - asset_type: stocks, crypto, etf (default: all)
    - signal_type: buy, sell, all (default: all)
    - limit: max results (default: 30)
    """
    asset_type = request.args.get('asset_type', 'all')
    signal_type = request.args.get('signal_type', 'all')
    limit = int(request.args.get('limit', 30))

    query = f"""
    SELECT
        asset_type,
        symbol,
        FORMAT_TIMESTAMP('%Y-%m-%d', datetime) as date,
        ROUND(close, 2) as price,
        ROUND(up_probability * 100, 1) as up_pct,
        CASE
            WHEN up_probability >= 0.60 THEN 'BUY'
            WHEN up_probability <= 0.40 THEN 'SELL'
            ELSE 'HOLD'
        END as signal,
        growth_score,
        trend_regime,
        CASE WHEN pivot_low_flag = 1 THEN 'Pivot Low' ELSE '' END as pivot_low,
        CASE WHEN rise_cycle_start = 1 THEN 'Rise Start' ELSE '' END as rise_start,
        CASE WHEN golden_cross = 1 THEN 'Golden Cross' ELSE '' END as golden_cross_flag
    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions_v2`
    WHERE data_split = 'VALIDATE'
      AND (up_probability >= 0.65 OR up_probability <= 0.35)
    """

    if asset_type != 'all':
        query += f" AND asset_type = '{asset_type}'"

    if signal_type == 'buy':
        query += " AND up_probability >= 0.60"
    elif signal_type == 'sell':
        query += " AND up_probability <= 0.40"

    query += f" ORDER BY datetime DESC LIMIT {limit}"

    try:
        results = list(client.query(query).result())
        signals = [sanitize_row(row) for row in results]

        return jsonify({
            'status': 'success',
            'confidence': 'HIGH',
            'accuracy_note': 'Crypto: 81%, ETFs: 85%, Stocks: 55%',
            'count': len(signals),
            'signals': signals
        })
    except Exception as e:
        logger.error(f"High confidence signals error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/ml/walk-forward-summary', methods=['GET'])
def get_walk_forward_summary():
    """Get walk-forward model validation summary"""

    summary_query = f"""
    SELECT
        data_split,
        asset_type,
        COUNT(*) as total_predictions,
        SUM(CASE WHEN predicted_direction = actual_direction THEN 1 ELSE 0 END) as correct,
        ROUND(SUM(CASE WHEN predicted_direction = actual_direction THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as accuracy
    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions_v2`
    GROUP BY data_split, asset_type
    ORDER BY data_split, asset_type
    """

    try:
        results = list(client.query(summary_query).result())
        summary = [sanitize_row(row) for row in results]

        return jsonify({
            'status': 'success',
            'model': 'xgboost_walk_forward_v2',
            'methodology': {
                'training': 'Earliest data to Dec 31, 2022',
                'testing': '2023 (walk-forward)',
                'validation': '2024-2025 (continuous)'
            },
            'summary': summary
        })
    except Exception as e:
        logger.error(f"Walk-forward summary error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/ml/symbol-prediction/<symbol>', methods=['GET'])
def get_symbol_prediction(symbol):
    """
    Get latest ML prediction for a specific symbol.
    """
    asset_type = request.args.get('asset_type', 'stocks')

    query = f"""
    SELECT
        asset_type,
        symbol,
        datetime,
        close as price,
        up_probability,
        predicted_direction,
        actual_direction,
        rsi,
        macd_histogram,
        adx,
        growth_score,
        in_rise_cycle,
        rise_cycle_start,
        pivot_high_flag,
        pivot_low_flag,
        golden_cross,
        trend_regime
    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions_v2`
    WHERE symbol = @symbol AND asset_type = @asset_type
    ORDER BY datetime DESC
    LIMIT 10
    """

    try:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("symbol", "STRING", symbol.upper()),
                bigquery.ScalarQueryParameter("asset_type", "STRING", asset_type.lower())
            ]
        )
        results = list(client.query(query, job_config=job_config).result())

        if not results:
            return jsonify({'status': 'error', 'message': f'No predictions for {symbol}'}), 404

        predictions = [sanitize_row(row) for row in results]
        latest = predictions[0]

        return jsonify({
            'status': 'success',
            'symbol': symbol.upper(),
            'asset_type': asset_type,
            'latest_prediction': {
                'datetime': latest.get('datetime'),
                'price': latest.get('price'),
                'direction': latest.get('predicted_direction'),
                'up_probability': latest.get('up_probability'),
                'confidence': 'HIGH' if latest.get('up_probability', 0.5) >= 0.65 or latest.get('up_probability', 0.5) <= 0.35 else 'MEDIUM' if latest.get('up_probability', 0.5) >= 0.55 or latest.get('up_probability', 0.5) <= 0.45 else 'LOW',
                'growth_score': latest.get('growth_score'),
                'trend_regime': latest.get('trend_regime'),
                'signals': {
                    'in_rise_cycle': latest.get('in_rise_cycle'),
                    'rise_cycle_start': latest.get('rise_cycle_start'),
                    'pivot_low': latest.get('pivot_low_flag'),
                    'pivot_high': latest.get('pivot_high_flag'),
                    'golden_cross': latest.get('golden_cross')
                }
            },
            'history': predictions
        })
    except Exception as e:
        logger.error(f"Symbol prediction error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
