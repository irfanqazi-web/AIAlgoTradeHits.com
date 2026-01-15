"""
Local API Server for Testing
Serves NVIDIA and Bitcoin data from BigQuery
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import bigquery
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - Updated to use new project
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

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

def get_stock_data_from_table(symbol, table_name, limit=500):
    """Fetch stock data from a specific BigQuery table"""
    # For daily data, get recent data with valid indicators
    # For intraday, get all available data
    order_direction = "DESC" if table_name == "stocks_daily" else "ASC"

    query = f"""
    SELECT
        symbol,
        datetime,
        open,
        high,
        low,
        close,
        volume,
        rsi_14 as rsi,
        macd_line as macd,
        macd_signal,
        macd_histogram as macd_hist,
        bbands_upper as bb_upper,
        bbands_middle as bb_middle,
        bbands_lower as bb_lower,
        sma_20,
        sma_50,
        sma_200,
        ema_12,
        ema_26,
        ema_50,
        adx_14 as adx,
        atr_14 as atr,
        cci_14 as cci,
        willr_14 as williams_r,
        stoch_k,
        stoch_d,
        obv,
        mom_10 as momentum,
        roc_10 as roc
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
            # Convert datetime to Unix timestamp (seconds since epoch)
            timestamp = None
            if row.datetime:
                # If datetime is timezone-aware, use it directly; otherwise assume UTC
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
                'open': float(row.open) if row.open else None,
                'high': float(row.high) if row.high else None,
                'low': float(row.low) if row.low else None,
                'close': float(row.close) if row.close else None,
                'volume': float(row.volume) if row.volume else None,
                'rsi': float(row.rsi) if row.rsi else None,
                'macd': float(row.macd) if row.macd else None,
                'macd_signal': float(row.macd_signal) if row.macd_signal else None,
                'macd_histogram': float(row.macd_hist) if row.macd_hist else None,
                'bb_upper': float(row.bb_upper) if row.bb_upper else None,
                'bb_middle': float(row.bb_middle) if row.bb_middle else None,
                'bb_lower': float(row.bb_lower) if row.bb_lower else None,
                'sma_20': float(row.sma_20) if row.sma_20 else None,
                'sma_50': float(row.sma_50) if row.sma_50 else None,
                'sma_200': float(row.sma_200) if row.sma_200 else None,
                'ema_12': float(row.ema_12) if row.ema_12 else None,
                'ema_26': float(row.ema_26) if row.ema_26 else None,
                'ema_50': float(row.ema_50) if row.ema_50 else None,
                'adx': float(row.adx) if row.adx else None,
                'atr': float(row.atr) if row.atr else None,
                'cci': float(row.cci) if row.cci else None,
                'williams_r': float(row.williams_r) if row.williams_r else None,
                'stoch_k': float(row.stoch_k) if row.stoch_k else None,
                'stoch_d': float(row.stoch_d) if row.stoch_d else None,
                'obv': float(row.obv) if row.obv else None,
                'momentum': float(row.momentum) if row.momentum else None,
                'roc': float(row.roc) if row.roc else None,
            })

        # Reverse data if we fetched DESC (most recent first) to return chronological order
        if table_name == "stocks_daily":
            data.reverse()

        logger.info(f"Fetched {len(data)} records for {symbol} from {table_name}")
        return data
    except Exception as e:
        logger.error(f"Error fetching stock data from {table_name}: {str(e)}")
        return []

def get_crypto_data_from_table(pair, table_name, limit=500):
    """Fetch crypto data from a specific BigQuery table"""
    # For daily data, get recent data with valid indicators
    # For intraday, get all available data
    order_direction = "DESC" if table_name == "crypto_daily" else "ASC"

    # Convert pair format (BTC/USD -> BTCUSD for matching)
    symbol = pair.replace('/', '')

    query = f"""
    SELECT
        symbol as pair,
        datetime,
        open,
        high,
        low,
        close,
        volume,
        rsi_14 as rsi,
        macd_line as macd,
        macd_signal,
        macd_histogram as macd_hist,
        bbands_upper as bb_upper,
        bbands_middle as bb_middle,
        bbands_lower as bb_lower,
        sma_20,
        sma_50,
        sma_200,
        ema_12,
        ema_26,
        ema_50,
        adx_14 as adx,
        atr_14 as atr,
        cci_14 as cci,
        willr_14 as williams_r,
        stoch_k,
        stoch_d,
        obv,
        mom_10 as momentum,
        roc_10 as roc
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
            # Convert datetime to Unix timestamp (seconds since epoch)
            timestamp = None
            if row.datetime:
                # If datetime is timezone-aware, use it directly; otherwise assume UTC
                if row.datetime.tzinfo is None:
                    from datetime import timezone as tz
                    dt_utc = row.datetime.replace(tzinfo=tz.utc)
                    timestamp = int(dt_utc.timestamp())
                else:
                    timestamp = int(row.datetime.timestamp())

            data.append({
                'pair': row.pair,
                'datetime': row.datetime.isoformat() if row.datetime else None,
                'timestamp': timestamp,
                'open': float(row.open) if row.open else None,
                'high': float(row.high) if row.high else None,
                'low': float(row.low) if row.low else None,
                'close': float(row.close) if row.close else None,
                'volume': float(row.volume) if row.volume else None,
                'rsi': float(row.rsi) if row.rsi else None,
                'macd': float(row.macd) if row.macd else None,
                'macd_signal': float(row.macd_signal) if row.macd_signal else None,
                'macd_histogram': float(row.macd_hist) if row.macd_hist else None,
                'bb_upper': float(row.bb_upper) if row.bb_upper else None,
                'bb_middle': float(row.bb_middle) if row.bb_middle else None,
                'bb_lower': float(row.bb_lower) if row.bb_lower else None,
                'sma_20': float(row.sma_20) if row.sma_20 else None,
                'sma_50': float(row.sma_50) if row.sma_50 else None,
                'sma_200': float(row.sma_200) if row.sma_200 else None,
                'ema_12': float(row.ema_12) if row.ema_12 else None,
                'ema_26': float(row.ema_26) if row.ema_26 else None,
                'ema_50': float(row.ema_50) if row.ema_50 else None,
                'adx': float(row.adx) if row.adx else None,
                'atr': float(row.atr) if row.atr else None,
                'cci': float(row.cci) if row.cci else None,
                'williams_r': float(row.williams_r) if row.williams_r else None,
                'stoch_k': float(row.stoch_k) if row.stoch_k else None,
                'stoch_d': float(row.stoch_d) if row.stoch_d else None,
                'obv': float(row.obv) if row.obv else None,
                'momentum': float(row.momentum) if row.momentum else None,
                'roc': float(row.roc) if row.roc else None,
            })

        # Reverse data if we fetched DESC (most recent first) to return chronological order
        if table_name == "crypto_daily":
            data.reverse()

        logger.info(f"Fetched {len(data)} records for {pair} from {table_name}")
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

    data = get_stock_data_from_table(symbol, 'stocks_daily', limit)

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

    data = get_stock_data_from_table(symbol, 'stocks_15min', limit)

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

    data = get_stock_data_from_table(symbol, 'stocks_5min', limit)

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

    data = get_crypto_data_from_table(pair, 'crypto_daily', limit)

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

    data = get_crypto_data_from_table(pair, 'crypto_15min', limit)

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

    data = get_crypto_data_from_table(pair, 'crypto_5min', limit)

    return jsonify({
        'success': True,
        'data': data,
        'count': len(data)
    })

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
    FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily`
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
                'close': float(row.close) if row.close else 0,
                'rsi': float(row.rsi) if row.rsi else 0,
                'macd': float(row.macd) if row.macd else 0,
                'adx': float(row.adx) if row.adx else 0,
                'volume': float(row.volume) if row.volume else 0,
                'roc': float(row.roc) if row.roc else 0,
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
    FROM `{PROJECT_ID}.{DATASET_ID}.crypto_analysis`
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
                'close': float(row.close) if row.close else 0,
                'rsi': float(row.rsi) if row.rsi else 0,
                'macd': float(row.macd) if row.macd else 0,
                'adx': float(row.adx) if row.adx else 0,
                'volume': float(row.volume) if row.volume else 0,
                'roc': float(row.roc) if row.roc else 0,
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
        SELECT user_id, email, username, password_hash, preferences, first_login_completed, subscription_tier
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

        # Verify password (hash password with SHA256)
        import hashlib
        hashed_input = hashlib.sha256(password.encode()).hexdigest()
        if user.password_hash != hashed_input:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

        # Extract role from preferences JSON
        import json
        role = 'user'  # default role
        if user.preferences:
            try:
                prefs = json.loads(user.preferences)
                role = prefs.get('role', 'user')
            except:
                pass

        # Generate simple token (in production use JWT)
        import secrets
        token = hashlib.sha256(f"{email}{secrets.token_hex(16)}".encode()).hexdigest()

        return jsonify({
            'success': True,
            'user': {
                'user_id': user.user_id,
                'email': user.email,
                'username': user.username,
                'role': role,
                'subscription_tier': user.subscription_tier,
                'first_login_completed': user.first_login_completed,
                'token': token
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
        SELECT user_id, email, username, preferences, subscription_tier, account_status, created_at
        FROM `{PROJECT_ID}.{DATASET_ID}.users`
        ORDER BY created_at DESC
        """

        query_job = client.query(query)
        results = query_job.result()

        import json
        users = []
        for row in results:
            # Extract role from preferences
            role = 'user'
            if row.preferences:
                try:
                    prefs = json.loads(row.preferences)
                    role = prefs.get('role', 'user')
                except:
                    pass

            users.append({
                'user_id': row.user_id,
                'email': row.email,
                'username': row.username,
                'role': role,
                'subscription_tier': row.subscription_tier,
                'account_status': row.account_status,
                'created_at': row.created_at.isoformat() if row.created_at else None
            })

        return jsonify({'success': True, 'users': users})
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    print("\n" + "="*80)
    print("LOCAL API SERVER STARTING")
    print("="*80)
    print(f"Server running on http://localhost:8080")
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

    app.run(host='0.0.0.0', port=8080, debug=True)
