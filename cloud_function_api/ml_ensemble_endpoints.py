
# ============================================================================
# GEMINI ENSEMBLE PREDICTION ENDPOINT
# Add this to cloud_function_api/main.py
# ============================================================================

from gemini_ensemble_integration import GeminiTradingAnalyst

# Initialize globally for reuse
ensemble_analyst = GeminiTradingAnalyst()

@app.route('/api/ml/ensemble-prediction', methods=['POST'])
def get_ensemble_prediction():
    """
    Get XGBoost + Gemini ensemble prediction for a symbol.

    POST body:
    {
        "symbol": "AAPL",
        "asset_type": "stocks"  // stocks, crypto, or etf
    }
    """
    data = request.get_json() or {}
    symbol = data.get('symbol', '').upper()
    asset_type = data.get('asset_type', 'stocks').lower()

    if not symbol:
        return jsonify({'status': 'error', 'message': 'Symbol required'}), 400

    # Get latest prediction from walk-forward model
    query = f"""
    SELECT *
    FROM `aialgotradehits.ml_models.walk_forward_predictions_v2`
    WHERE symbol = '{symbol}' AND asset_type = '{asset_type}'
    ORDER BY datetime DESC
    LIMIT 1
    """

    try:
        df = bq_client.query(query).to_dataframe()

        if df.empty:
            return jsonify({'status': 'error', 'message': f'No data for {symbol}'}), 404

        row = df.iloc[0]

        market_data = {
            'close': float(row['close']),
            'rsi': float(row['rsi']) if row['rsi'] else 50,
            'macd_histogram': float(row['macd_histogram']) if row['macd_histogram'] else 0,
            'adx': float(row['adx']) if row['adx'] else 0,
            'growth_score': int(row['growth_score']) if row['growth_score'] else 50,
            'in_rise_cycle': int(row['in_rise_cycle']) if row['in_rise_cycle'] else 0,
            'rise_cycle_start': int(row['rise_cycle_start']) if row['rise_cycle_start'] else 0,
            'pivot_high_flag': int(row['pivot_high_flag']) if row['pivot_high_flag'] else 0,
            'pivot_low_flag': int(row['pivot_low_flag']) if row['pivot_low_flag'] else 0,
            'golden_cross': int(row['golden_cross']) if row['golden_cross'] else 0,
            'trend_regime': row['trend_regime'] if row['trend_regime'] else 'UNKNOWN',
            'xgb_prob': float(row['up_probability'])
        }

        # Get Gemini analysis
        gemini_result = ensemble_analyst.analyze_market_data(symbol, asset_type, market_data)

        # Get ensemble prediction
        ensemble = ensemble_analyst.ensemble_prediction(
            asset_type,
            market_data['xgb_prob'],
            gemini_result
        )

        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'asset_type': asset_type,
            'datetime': str(row['datetime']),
            'price': float(row['close']),
            'market_data': market_data,
            'xgb_prediction': {
                'up_probability': market_data['xgb_prob'],
                'direction': 'UP' if market_data['xgb_prob'] > 0.5 else 'DOWN'
            },
            'gemini_prediction': gemini_result,
            'ensemble_prediction': ensemble,
            'final_recommendation': {
                'direction': ensemble['direction'],
                'confidence': ensemble['confidence'],
                'reasoning': gemini_result.get('reasoning', ''),
                'risk_level': gemini_result.get('risk_level', 'MEDIUM')
            }
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/ml/ensemble-signals', methods=['GET'])
def get_ensemble_signals():
    """
    Get ensemble buy/sell signals with Gemini enhancement.

    Query params:
    - asset_type: stocks, crypto, etf (default: all)
    - signal_type: buy, sell, all (default: all)
    - limit: max results (default: 20)
    """
    asset_type = request.args.get('asset_type', 'all')
    signal_type = request.args.get('signal_type', 'all')
    limit = int(request.args.get('limit', 20))

    # Get high-potential predictions from XGBoost
    query = f"""
    SELECT
        asset_type,
        symbol,
        FORMAT_TIMESTAMP('%Y-%m-%d', datetime) as date,
        close as price,
        rsi,
        macd_histogram,
        adx,
        growth_score,
        in_rise_cycle,
        pivot_low_flag,
        pivot_high_flag,
        golden_cross,
        trend_regime,
        up_probability,
        CASE
            WHEN up_probability >= 0.60 THEN 'BUY'
            WHEN up_probability <= 0.40 THEN 'SELL'
            ELSE 'HOLD'
        END as xgb_signal
    FROM `aialgotradehits.ml_models.walk_forward_predictions_v2`
    WHERE data_split = 'VALIDATE'
      AND datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    """

    if asset_type != 'all':
        query += f" AND asset_type = '{asset_type}'"

    if signal_type == 'buy':
        query += " AND up_probability >= 0.55"
    elif signal_type == 'sell':
        query += " AND up_probability <= 0.45"

    query += f" ORDER BY datetime DESC LIMIT {limit}"

    try:
        df = bq_client.query(query).to_dataframe()

        signals = []
        for _, row in df.iterrows():
            # Quick Gemini analysis for each signal
            market_data = {
                'close': float(row['price']),
                'rsi': float(row['rsi']) if row['rsi'] else 50,
                'macd_histogram': float(row['macd_histogram']) if row['macd_histogram'] else 0,
                'adx': float(row['adx']) if row['adx'] else 0,
                'growth_score': int(row['growth_score']) if row['growth_score'] else 50,
                'in_rise_cycle': int(row['in_rise_cycle']) if row['in_rise_cycle'] else 0,
                'pivot_low_flag': int(row['pivot_low_flag']) if row['pivot_low_flag'] else 0,
                'pivot_high_flag': int(row['pivot_high_flag']) if row['pivot_high_flag'] else 0,
                'golden_cross': int(row['golden_cross']) if row['golden_cross'] else 0,
                'trend_regime': row['trend_regime'] if row['trend_regime'] else 'UNKNOWN',
                'xgb_prob': float(row['up_probability'])
            }

            gemini_result = ensemble_analyst.analyze_market_data(
                row['symbol'], row['asset_type'], market_data
            )

            ensemble = ensemble_analyst.ensemble_prediction(
                row['asset_type'],
                market_data['xgb_prob'],
                gemini_result
            )

            signals.append({
                'symbol': row['symbol'],
                'asset_type': row['asset_type'],
                'date': row['date'],
                'price': float(row['price']),
                'xgb_signal': row['xgb_signal'],
                'xgb_probability': float(row['up_probability']),
                'ensemble_signal': ensemble['direction'],
                'ensemble_confidence': ensemble['confidence'],
                'gemini_reasoning': gemini_result.get('reasoning', ''),
                'risk_level': ensemble.get('risk_level', 'MEDIUM')
            })

        return jsonify({
            'status': 'success',
            'count': len(signals),
            'filters': {
                'asset_type': asset_type,
                'signal_type': signal_type
            },
            'signals': signals
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
