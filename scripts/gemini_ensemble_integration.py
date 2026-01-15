"""
Gemini 2.5 Pro Ensemble Integration
===================================
Combines XGBoost predictions with Gemini qualitative analysis
to improve accuracy, especially for stocks.

Author: Claude Code
Date: January 2026
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
import json
from datetime import datetime
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel

# Configuration
PROJECT_ID = 'aialgotradehits'
REGION = 'us-central1'
ML_DATASET = 'ml_models'

# Initialize
bq_client = bigquery.Client(project=PROJECT_ID)
vertexai.init(project=PROJECT_ID, location=REGION)

print("=" * 80)
print("GEMINI 2.5 PRO ENSEMBLE INTEGRATION")
print("=" * 80)
print(f"Started: {datetime.now()}")


class GeminiTradingAnalyst:
    """
    Gemini 2.5 Pro integration for qualitative trading analysis.
    Combines with XGBoost for ensemble predictions.
    """

    def __init__(self):
        """Initialize Gemini model"""
        self.model = None
        self.model_name = None

        try:
            # Try Gemini 2.0 Flash first (faster, cheaper)
            self.model = GenerativeModel("gemini-2.0-flash-001")
            self.model_name = "gemini-2.0-flash-001"
        except Exception:
            try:
                # Fall back to Gemini 1.5 Pro
                self.model = GenerativeModel("gemini-1.5-pro")
                self.model_name = "gemini-1.5-pro"
            except Exception as e:
                print(f"Warning: Could not initialize Gemini: {e}")

        # Ensemble weights - adjusted based on walk-forward results
        # Stocks: XGBoost only 55% accurate, give more weight to Gemini
        self.weights = {
            'stocks': {'xgb': 0.50, 'gemini': 0.50},
            'crypto': {'xgb': 0.70, 'gemini': 0.30},  # XGBoost already 81% accurate
            'etf': {'xgb': 0.70, 'gemini': 0.30}      # XGBoost already 85% accurate
        }

    def analyze_market_data(self, symbol: str, asset_type: str, market_data: dict) -> dict:
        """
        Get Gemini's qualitative analysis of market conditions.
        """
        if self.model is None:
            return self._default_response()

        prompt = f"""You are an expert financial analyst. Analyze the following market data for {symbol} ({asset_type}) and provide a trading prediction.

CURRENT MARKET DATA:
- Symbol: {symbol}
- Asset Type: {asset_type.upper()}
- Price: ${market_data.get('close', 0):.2f}
- RSI (14): {market_data.get('rsi', 50):.1f} {'(Oversold - potential buy)' if market_data.get('rsi', 50) < 30 else '(Overbought - potential sell)' if market_data.get('rsi', 50) > 70 else '(Neutral)'}
- MACD Histogram: {market_data.get('macd_histogram', 0):.4f} {'(Bullish momentum)' if market_data.get('macd_histogram', 0) > 0 else '(Bearish momentum)'}
- ADX (Trend Strength): {market_data.get('adx', 0):.1f} {'(Strong trend)' if market_data.get('adx', 0) > 25 else '(Weak trend)'}
- Growth Score: {market_data.get('growth_score', 0)}/100
- In Rise Cycle: {'Yes (EMA12 > EMA26)' if market_data.get('in_rise_cycle', 0) == 1 else 'No (Bearish)'}
- Trend Regime: {market_data.get('trend_regime', 'UNKNOWN')}
- Pivot Low Flag: {'Yes (potential reversal bottom)' if market_data.get('pivot_low_flag', 0) == 1 else 'No'}
- Pivot High Flag: {'Yes (potential reversal top)' if market_data.get('pivot_high_flag', 0) == 1 else 'No'}
- Golden Cross: {'Yes (50 SMA crossed above 200 SMA)' if market_data.get('golden_cross', 0) == 1 else 'No'}
- XGBoost UP Probability: {market_data.get('xgb_prob', 0.5)*100:.1f}%

ANALYSIS GUIDELINES:
1. Pivot Low + Low RSI + Rise Cycle Start = Strong BUY signal
2. Pivot High + High RSI + Fall Cycle = Strong SELL signal
3. Golden Cross = Medium-term bullish confirmation
4. Growth Score > 75 = Bullish fundamentals alignment
5. Strong uptrend (ADX > 25) with positive MACD = Momentum continuation

Provide your analysis in this exact JSON format:
{{
    "direction": "UP" or "DOWN" or "NEUTRAL",
    "confidence": 0.0 to 1.0,
    "reasoning": "Brief 1-2 sentence explanation",
    "risk_level": "HIGH" or "MEDIUM" or "LOW"
}}

Respond ONLY with the JSON, no other text."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Parse JSON from response
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]

            result = json.loads(text)

            # Normalize confidence to 0-1
            if 'confidence' in result:
                if isinstance(result['confidence'], str):
                    conf_map = {'HIGH': 0.8, 'MEDIUM': 0.6, 'LOW': 0.4}
                    result['confidence'] = conf_map.get(result['confidence'].upper(), 0.5)
                result['confidence'] = max(0, min(1, float(result['confidence'])))

            return result

        except Exception as e:
            print(f"    Gemini error for {symbol}: {str(e)[:50]}")
            return self._default_response()

    def _default_response(self) -> dict:
        """Default response when Gemini is unavailable"""
        return {
            'direction': 'NEUTRAL',
            'confidence': 0.5,
            'reasoning': 'Unable to perform qualitative analysis',
            'risk_level': 'MEDIUM'
        }

    def ensemble_prediction(self, asset_type: str, xgb_prob: float, gemini_result: dict) -> dict:
        """
        Combine XGBoost probability with Gemini analysis.
        Uses asset-type-specific weights.
        """
        weights = self.weights.get(asset_type, {'xgb': 0.60, 'gemini': 0.40})

        # Convert XGBoost probability to score (-1 to 1)
        xgb_score = (xgb_prob - 0.5) * 2  # 0.7 -> 0.4, 0.3 -> -0.4

        # Convert Gemini direction and confidence to score
        direction_map = {'UP': 1, 'NEUTRAL': 0, 'DOWN': -1}
        gemini_direction = gemini_result.get('direction', 'NEUTRAL')
        gemini_conf = gemini_result.get('confidence', 0.5)
        gemini_score = direction_map.get(gemini_direction, 0) * gemini_conf

        # Weighted ensemble score
        ensemble_score = (weights['xgb'] * xgb_score) + (weights['gemini'] * gemini_score)

        # Determine final direction
        if ensemble_score > 0.15:
            final_direction = 'UP'
        elif ensemble_score < -0.15:
            final_direction = 'DOWN'
        else:
            final_direction = 'NEUTRAL'

        # Determine confidence
        abs_score = abs(ensemble_score)
        if abs_score > 0.4:
            final_confidence = 'HIGH'
        elif abs_score > 0.2:
            final_confidence = 'MEDIUM'
        else:
            final_confidence = 'LOW'

        return {
            'direction': final_direction,
            'confidence': final_confidence,
            'ensemble_score': round(ensemble_score, 4),
            'xgb_contribution': round(weights['xgb'] * xgb_score, 4),
            'gemini_contribution': round(weights['gemini'] * gemini_score, 4),
            'xgb_probability': round(xgb_prob, 4),
            'gemini_direction': gemini_direction,
            'gemini_confidence': round(gemini_conf, 4),
            'gemini_reasoning': gemini_result.get('reasoning', ''),
            'risk_level': gemini_result.get('risk_level', 'MEDIUM'),
            'weights_used': weights
        }


def test_gemini_integration():
    """Test Gemini integration with sample predictions"""
    print("\n" + "-" * 60)
    print("TESTING GEMINI ENSEMBLE INTEGRATION")
    print("-" * 60)

    analyst = GeminiTradingAnalyst()
    print(f"Gemini Model: {analyst.model_name}")
    print(f"Ensemble Weights: {analyst.weights}")

    # Get sample predictions from walk-forward model
    sample_query = f"""
    SELECT
        asset_type,
        symbol,
        datetime,
        close,
        rsi,
        macd_histogram,
        adx,
        growth_score,
        in_rise_cycle,
        rise_cycle_start,
        pivot_high_flag,
        pivot_low_flag,
        golden_cross,
        trend_regime,
        up_probability
    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions_v2`
    WHERE data_split = 'VALIDATE'
      AND up_probability IS NOT NULL
    ORDER BY datetime DESC
    LIMIT 9
    """

    print("\nFetching sample predictions...")
    df = bq_client.query(sample_query).to_dataframe()

    print(f"\nTesting {len(df)} predictions:\n")

    results = []
    for _, row in df.iterrows():
        symbol = row['symbol']
        asset_type = row['asset_type']

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

        print(f"{symbol} ({asset_type}):")
        print(f"  Price: ${market_data['close']:.2f} | RSI: {market_data['rsi']:.0f} | Growth: {market_data['growth_score']}")

        # Get Gemini analysis
        gemini_result = analyst.analyze_market_data(symbol, asset_type, market_data)
        print(f"  Gemini: {gemini_result['direction']} (conf: {gemini_result['confidence']:.2f})")

        # Get ensemble prediction
        xgb_prob = market_data['xgb_prob']
        ensemble = analyst.ensemble_prediction(asset_type, xgb_prob, gemini_result)
        print(f"  XGBoost: {xgb_prob*100:.1f}% UP")
        print(f"  ENSEMBLE: {ensemble['direction']} ({ensemble['confidence']}) score={ensemble['ensemble_score']:.3f}")
        print(f"  Reason: {gemini_result.get('reasoning', 'N/A')[:80]}")
        print()

        results.append({
            'symbol': symbol,
            'asset_type': asset_type,
            'xgb_prob': xgb_prob,
            'gemini_direction': gemini_result['direction'],
            'gemini_conf': gemini_result['confidence'],
            'ensemble_direction': ensemble['direction'],
            'ensemble_confidence': ensemble['confidence'],
            'ensemble_score': ensemble['ensemble_score']
        })

    return results


def create_ensemble_api_code():
    """Generate API endpoint code for ensemble predictions"""
    print("\n" + "-" * 60)
    print("GENERATING API ENDPOINT CODE")
    print("-" * 60)

    api_code = '''
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
'''

    # Save API code
    api_file = 'C:/1AITrading/Trading/cloud_function_api/ml_ensemble_endpoints.py'
    with open(api_file, 'w', encoding='utf-8') as f:
        f.write(api_code)

    print(f"  API endpoint code saved to: {api_file}")
    print("\n  Endpoints created:")
    print("    POST /api/ml/ensemble-prediction - Get ensemble prediction for single symbol")
    print("    GET  /api/ml/ensemble-signals    - Get bulk ensemble signals")

    return api_code


def main():
    """Run Gemini ensemble integration"""

    # Test integration
    results = test_gemini_integration()

    # Generate API code
    create_ensemble_api_code()

    # Summary
    print("\n" + "=" * 80)
    print("GEMINI ENSEMBLE INTEGRATION COMPLETE")
    print("=" * 80)
    print(f"""
CONFIGURATION:
  Model: {GeminiTradingAnalyst().model_name}

  Asset-Specific Weights:
    - Stocks: XGBoost 50% + Gemini 50% (stocks need more help)
    - Crypto: XGBoost 70% + Gemini 30% (XGBoost 81% accurate)
    - ETFs:   XGBoost 70% + Gemini 30% (XGBoost 85% accurate)

ENSEMBLE BENEFITS:
  1. Qualitative context for stock analysis
  2. Market sentiment interpretation
  3. Pivot point validation
  4. Risk level assessment

FILES CREATED:
  - cloud_function_api/ml_ensemble_endpoints.py

NEXT STEPS:
  1. Add endpoints to main.py
  2. Deploy updated API to Cloud Run
  3. Test endpoint: POST /api/ml/ensemble-prediction {{"symbol": "AAPL"}}

Completed: {datetime.now()}
""")


if __name__ == "__main__":
    main()
