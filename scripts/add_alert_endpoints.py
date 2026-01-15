"""Script to add alert endpoints to main.py"""

file_path = 'C:/1AITrading/Trading/cloud_function_api/main.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add import at the top
import_section = "from flask import Flask, request, jsonify, Response"
new_import = """from flask import Flask, request, jsonify, Response
try:
    from trading_alerts import TradingAlertSystem, get_alert_system
except ImportError:
    TradingAlertSystem = None
    get_alert_system = None"""

if 'from trading_alerts import' not in content:
    content = content.replace(import_section, new_import)
    print('Added trading_alerts import')

# Add alert endpoints
alert_endpoints = '''

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

'''

# Add before the final if __name__ block
if '/api/alerts/price-anomalies' not in content:
    # Find a good insertion point
    if "if __name__ ==" in content:
        idx = content.rfind("if __name__ ==")
        content = content[:idx] + alert_endpoints + "\n" + content[idx:]
        print('Added alert API endpoints')
    else:
        content += alert_endpoints
        print('Appended alert API endpoints')
else:
    print('Alert endpoints already exist')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('File updated successfully')
