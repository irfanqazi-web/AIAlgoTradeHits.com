"""
Flask API Endpoints for Data Reconciliation Dashboard
Provides endpoints to fetch all stock symbols, complete field data, and CSV downloads
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from google.cloud import bigquery
import pandas as pd
import io
import sys

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)
CORS(app)

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
client = bigquery.Client(project=PROJECT_ID)

@app.route('/api/stocks/symbols', methods=['GET'])
def get_stock_symbols():
    """Get all unique stock symbols from historical daily table"""
    try:
        query = f"""
        SELECT DISTINCT symbol
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_historical_daily`
        ORDER BY symbol
        """

        result = client.query(query).result()
        symbols = [row['symbol'] for row in result]

        return jsonify({
            'success': True,
            'symbols': symbols,
            'count': len(symbols)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stocks/reconciliation/<symbol>', methods=['GET'])
def get_stock_reconciliation_data(symbol):
    """
    Get complete reconciliation data for a specific stock symbol
    Includes all fields with pagination
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        limit = min(limit, 5000)  # Cap at 5000 records

        # Fetch all data for the symbol
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_historical_daily`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT {limit}
        """

        df = client.query(query).to_dataframe()

        if df.empty:
            return jsonify({
                'success': False,
                'error': f'No data found for symbol {symbol}'
            }), 404

        # Get column names
        columns = df.columns.tolist()

        # Convert datetime to string for JSON serialization
        if 'datetime' in df.columns:
            df['datetime'] = df['datetime'].astype(str)

        # Convert to records
        records = df.to_dict('records')

        # Get statistics
        stats = {
            'symbol': symbol,
            'total_records': len(df),
            'total_fields': len(columns),
            'date_range': {
                'start': str(df['datetime'].min()) if 'datetime' in df.columns else None,
                'end': str(df['datetime'].max()) if 'datetime' in df.columns else None
            },
            'latest_price': float(df.iloc[0]['close']) if 'close' in df.columns and len(df) > 0 else None
        }

        return jsonify({
            'success': True,
            'symbol': symbol,
            'records': records,
            'columns': columns,
            'stats': stats,
            'displayed_count': len(records)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stocks/reconciliation/<symbol>/download', methods=['GET'])
def download_stock_full_dataset(symbol):
    """Download complete dataset for a stock symbol as CSV"""
    try:
        # Fetch ALL data for the symbol (no limit)
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_historical_daily`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        """

        df = client.query(query).to_dataframe()

        if df.empty:
            return jsonify({
                'success': False,
                'error': f'No data found for symbol {symbol}'
            }), 404

        # Convert datetime to string
        if 'datetime' in df.columns:
            df['datetime'] = df['datetime'].astype(str)

        # Create CSV in memory
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        # Convert to BytesIO for sending
        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8'))
        mem.seek(0)

        # Send file
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{symbol}_complete_dataset_{pd.Timestamp.now().strftime("%Y%m%d")}.csv'
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stocks/reconciliation/fields', methods=['GET'])
def get_all_field_names():
    """Get list of all field names with descriptions"""
    try:
        # Get schema from table
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.stocks_historical_daily"
        table = client.get_table(table_ref)

        fields = [{
            'name': field.name,
            'type': field.field_type,
            'mode': field.mode,
            'description': field.description or ''
        } for field in table.schema]

        # Group fields by category
        categories = {
            'Basic': ['datetime', 'open', 'high', 'low', 'close', 'volume', 'symbol', 'asset_type'],
            'Moving Averages': ['sma_5', 'sma_10', 'sma_20', 'sma_50', 'sma_100', 'sma_200',
                               'ema_5', 'ema_10', 'ema_12', 'ema_20', 'ema_26', 'ema_50', 'ema_100', 'ema_200'],
            'Momentum': ['rsi', 'rsi_7', 'rsi_14', 'rsi_21', 'macd', 'macd_signal', 'macd_hist',
                        'stoch_k', 'stoch_d', 'williams_r', 'roc_5', 'roc_10', 'roc_20', 'cci'],
            'Volatility': ['atr', 'atr_7', 'atr_14', 'bb_upper', 'bb_middle', 'bb_lower', 'bb_width',
                          'bb_percent', 'volatility_10', 'volatility_20'],
            'Trend': ['adx', 'plus_di', 'minus_di', 'dx'],
            'Volume': ['obv', 'volume_zscore', 'volume_ratio'],
            'Returns': ['weekly_log_return', 'return_2w', 'return_4w', 'return_8w', 'daily_return_pct',
                       'return_lag_1', 'return_lag_2', 'return_lag_3'],
            'Price Ratios': ['close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct',
                           'close_vs_ema20_pct', 'close_vs_ema50_pct', 'high_low_pct'],
            'Slopes': ['rsi_slope', 'ema_slope_20', 'ema_slope_50', 'atr_slope'],
            'Z-Scores': ['rsi_zscore', 'atr_zscore', 'volume_zscore'],
            'Flags': ['rsi_overbought_flag', 'rsi_oversold_flag', 'macd_cross_flag'],
            'Lags': ['close_lag_1', 'close_lag_2', 'close_lag_3', 'close_lag_5', 'close_lag_10'],
            'Targets': ['target_return_1d', 'target_return_5d', 'target_direction_1d'],
            'Signals': ['momentum_signal', 'trend_signal'],
            'Candles': ['candle_body_pct', 'candle_range_pct', 'upper_shadow_pct', 'lower_shadow_pct'],
            'Advanced': ['csi', 'fetch_timestamp']
        }

        return jsonify({
            'success': True,
            'fields': fields,
            'total_fields': len(fields),
            'categories': categories
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cryptos/symbols', methods=['GET'])
def get_crypto_symbols():
    """Get all unique crypto symbols from historical daily table"""
    try:
        query = f"""
        SELECT DISTINCT symbol
        FROM `{PROJECT_ID}.{DATASET_ID}.cryptos_historical_daily`
        ORDER BY symbol
        """

        result = client.query(query).result()
        symbols = [row['symbol'] for row in result]

        return jsonify({
            'success': True,
            'symbols': symbols,
            'count': len(symbols)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cryptos/reconciliation/<symbol>', methods=['GET'])
def get_crypto_reconciliation_data(symbol):
    """Get complete reconciliation data for a specific crypto symbol"""
    try:
        limit = request.args.get('limit', 100, type=int)
        limit = min(limit, 5000)

        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.cryptos_historical_daily`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT {limit}
        """

        df = client.query(query).to_dataframe()

        if df.empty:
            return jsonify({
                'success': False,
                'error': f'No data found for symbol {symbol}'
            }), 404

        columns = df.columns.tolist()

        if 'datetime' in df.columns:
            df['datetime'] = df['datetime'].astype(str)

        records = df.to_dict('records')

        stats = {
            'symbol': symbol,
            'total_records': len(df),
            'total_fields': len(columns),
            'date_range': {
                'start': str(df['datetime'].min()) if 'datetime' in df.columns else None,
                'end': str(df['datetime'].max()) if 'datetime' in df.columns else None
            },
            'latest_price': float(df.iloc[0]['close']) if 'close' in df.columns and len(df) > 0 else None
        }

        return jsonify({
            'success': True,
            'symbol': symbol,
            'records': records,
            'columns': columns,
            'stats': stats,
            'displayed_count': len(records)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stocks/weekly/<symbol>', methods=['GET'])
def get_stock_weekly_data(symbol):
    """Get weekly data for a specific stock symbol"""
    try:
        limit = request.args.get('limit', 52, type=int)
        limit = min(limit, 260)  # Max 5 years

        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_weekly`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT {limit}
        """

        df = client.query(query).to_dataframe()

        if df.empty:
            return jsonify({
                'success': False,
                'error': f'No weekly data found for symbol {symbol}'
            }), 404

        columns = df.columns.tolist()

        if 'datetime' in df.columns:
            df['datetime'] = df['datetime'].astype(str)

        records = df.to_dict('records')

        # Calculate 52-week high/low
        high_52w = df['high'].max() if 'high' in df.columns else None
        low_52w = df['low'].min() if 'low' in df.columns else None

        stats = {
            'symbol': symbol,
            'total_records': len(df),
            'total_fields': len(columns),
            'latest_price': float(df.iloc[0]['close']) if 'close' in df.columns and len(df) > 0 else None,
            'high_52w': float(high_52w) if high_52w else None,
            'low_52w': float(low_52w) if low_52w else None
        }

        return jsonify({
            'success': True,
            'symbol': symbol,
            'records': records,
            'columns': columns,
            'stats': stats,
            'displayed_count': len(records)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cryptos/weekly/<symbol>', methods=['GET'])
def get_crypto_weekly_data(symbol):
    """Get weekly data for a specific crypto symbol"""
    try:
        limit = request.args.get('limit', 52, type=int)
        limit = min(limit, 260)

        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.cryptos_weekly`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT {limit}
        """

        df = client.query(query).to_dataframe()

        if df.empty:
            return jsonify({
                'success': False,
                'error': f'No weekly data found for symbol {symbol}'
            }), 404

        columns = df.columns.tolist()

        if 'datetime' in df.columns:
            df['datetime'] = df['datetime'].astype(str)

        records = df.to_dict('records')

        high_52w = df['high'].max() if 'high' in df.columns else None
        low_52w = df['low'].min() if 'low' in df.columns else None

        stats = {
            'symbol': symbol,
            'total_records': len(df),
            'total_fields': len(columns),
            'latest_price': float(df.iloc[0]['close']) if 'close' in df.columns and len(df) > 0 else None,
            'high_52w': float(high_52w) if high_52w else None,
            'low_52w': float(low_52w) if low_52w else None
        }

        return jsonify({
            'success': True,
            'symbol': symbol,
            'records': records,
            'columns': columns,
            'stats': stats,
            'displayed_count': len(records)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Data Reconciliation API',
        'version': '1.0.0'
    })


if __name__ == '__main__':
    print("="*70)
    print("DATA RECONCILIATION API SERVER")
    print("="*70)
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print("Endpoints:")
    print("  GET  /api/stocks/symbols")
    print("  GET  /api/stocks/reconciliation/<symbol>")
    print("  GET  /api/stocks/reconciliation/<symbol>/download")
    print("  GET  /api/stocks/reconciliation/fields")
    print("  GET  /api/cryptos/symbols")
    print("  GET  /api/cryptos/reconciliation/<symbol>")
    print("  GET  /health")
    print("="*70)
    print()

    # Run on port 8080 for local development
    app.run(host='0.0.0.0', port=8080, debug=True)
