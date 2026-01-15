"""
AI Trading Intelligence Cloud Function
Provides AI-powered predictions, pattern recognition, and trading signals
using Google Gemini AI and optionally Anthropic Claude
"""

import os
import json
import re
import functions_framework
from datetime import datetime, timedelta
from google.cloud import bigquery
import pandas as pd
import numpy as np
from flask import jsonify

# Initialize clients
PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'aialgotradehits')
DATA_PROJECT_ID = os.environ.get('DATA_PROJECT_ID', 'cryptobot-462709')  # Where trading data lives
DATASET_ID = os.environ.get('BIGQUERY_DATASET', 'crypto_trading_data')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
VERTEX_AI_LOCATION = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')

# Google AI Studio API Key (Gemini) - same key as smart-search function
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBfmO5dBuRNYc-4w-McEw8cPnb6lr2pao8')

# Initialize Google Generative AI at module level (like smart-search)
import google.generativeai as genai
genai.configure(api_key=GEMINI_API_KEY)

# Dynamic model selection - use current Gemini 2.x models
# Updated Dec 2024: Gemini 2.0 and 2.5 models are now available
MODEL_PRIORITY = [
    "gemini-2.0-flash",                     # Stable Gemini 2.0 (recommended)
    "gemini-2.5-flash",                     # Latest 2.5 flash
    "gemini-2.5-pro",                       # Latest 2.5 pro
]

def get_available_model():
    """Get the first available Gemini model from priority list"""
    for model_name in MODEL_PRIORITY:
        try:
            model = genai.GenerativeModel(model_name)
            # Test model availability by checking if it can be initialized
            print(f"Using Gemini model: {model_name}")
            return model, model_name
        except Exception as e:
            print(f"Model {model_name} not available: {str(e)}")
            continue
    # Final fallback
    return genai.GenerativeModel("gemini-1.5-pro"), "gemini-1.5-pro"

# Initialize with best available model at startup
_gemini_model, GEMINI_MODEL_ID = get_available_model()

bq_client = bigquery.Client(project=PROJECT_ID)

# Lazy load anthropic to avoid startup errors if not configured
anthropic_client = None
if ANTHROPIC_API_KEY:
    try:
        import anthropic
        anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    except:
        pass


def get_historical_data(symbol, timeframe='daily', days=90, asset_type='crypto'):
    """Fetch historical data from BigQuery for any asset type

    Supported asset_types: crypto, stocks, etfs, forex, indices, commodities, bonds, interest_rates
    """

    # Table mapping for all 8 asset types
    table_maps = {
        'crypto': {
            'daily': f'{DATA_PROJECT_ID}.{DATASET_ID}.crypto_analysis',
            'hourly': f'{DATA_PROJECT_ID}.{DATASET_ID}.crypto_hourly_data',
            '5min': f'{DATA_PROJECT_ID}.{DATASET_ID}.crypto_5min_top10_gainers',
            'weekly': f'{DATA_PROJECT_ID}.{DATASET_ID}.crypto_weekly',
            'symbol_col': 'pair'
        },
        'stocks': {
            'daily': f'{DATA_PROJECT_ID}.{DATASET_ID}.stocks_daily',
            'hourly': f'{DATA_PROJECT_ID}.{DATASET_ID}.stocks_hourly',
            '5min': f'{DATA_PROJECT_ID}.{DATASET_ID}.stocks_5min',
            'weekly': f'{DATA_PROJECT_ID}.{DATASET_ID}.stocks_weekly',
            'symbol_col': 'symbol'
        },
        'etfs': {
            'daily': f'{DATA_PROJECT_ID}.{DATASET_ID}.etfs_daily',
            'hourly': f'{DATA_PROJECT_ID}.{DATASET_ID}.etfs_hourly',
            '5min': f'{DATA_PROJECT_ID}.{DATASET_ID}.etfs_5min',
            'weekly': f'{DATA_PROJECT_ID}.{DATASET_ID}.etfs_weekly',
            'symbol_col': 'symbol'
        },
        'forex': {
            'daily': f'{DATA_PROJECT_ID}.{DATASET_ID}.forex_daily',
            'hourly': f'{DATA_PROJECT_ID}.{DATASET_ID}.forex_hourly',
            '5min': f'{DATA_PROJECT_ID}.{DATASET_ID}.forex_5min',
            'weekly': f'{DATA_PROJECT_ID}.{DATASET_ID}.forex_weekly',
            'symbol_col': 'symbol'
        },
        'indices': {
            'daily': f'{DATA_PROJECT_ID}.{DATASET_ID}.indices_daily',
            'hourly': f'{DATA_PROJECT_ID}.{DATASET_ID}.indices_hourly',
            '5min': f'{DATA_PROJECT_ID}.{DATASET_ID}.indices_5min',
            'weekly': f'{DATA_PROJECT_ID}.{DATASET_ID}.indices_weekly',
            'symbol_col': 'symbol'
        },
        'commodities': {
            'daily': f'{DATA_PROJECT_ID}.{DATASET_ID}.commodities_daily',
            'hourly': f'{DATA_PROJECT_ID}.{DATASET_ID}.commodities_hourly',
            '5min': f'{DATA_PROJECT_ID}.{DATASET_ID}.commodities_5min',
            'weekly': f'{DATA_PROJECT_ID}.{DATASET_ID}.commodities_weekly',
            'symbol_col': 'symbol'
        },
        'bonds': {
            'daily': f'{DATA_PROJECT_ID}.{DATASET_ID}.bonds_daily_td',
            'hourly': f'{DATA_PROJECT_ID}.{DATASET_ID}.bonds_daily_td',
            '5min': f'{DATA_PROJECT_ID}.{DATASET_ID}.bonds_daily_td',
            'weekly': f'{DATA_PROJECT_ID}.{DATASET_ID}.bonds_daily_td',
            'symbol_col': 'symbol'
        },
        'interest_rates': {
            'daily': f'{DATA_PROJECT_ID}.{DATASET_ID}.interest_rates',
            'hourly': f'{DATA_PROJECT_ID}.{DATASET_ID}.interest_rates',
            '5min': f'{DATA_PROJECT_ID}.{DATASET_ID}.interest_rates',
            'weekly': f'{DATA_PROJECT_ID}.{DATASET_ID}.interest_rates',
            'symbol_col': 'country'
        }
    }

    # Get table config for asset type
    asset_config = table_maps.get(asset_type, table_maps['crypto'])
    table = asset_config.get(timeframe, asset_config['daily'])
    symbol_col = asset_config['symbol_col']

    # Build query based on asset type - each has different schema
    if asset_type == 'interest_rates':
        query = f"""
            SELECT
                {symbol_col} as symbol,
                timestamp as datetime,
                rate_value as close,
                rate_value as open,
                rate_value as high,
                rate_value as low,
                0 as volume,
                0 as rsi, 0 as macd, 0 as macd_signal, 0 as macd_hist,
                0 as bb_upper, 0 as bb_middle, 0 as bb_lower,
                0 as adx, 0 as cci, 0 as obv, 0 as atr,
                0 as sma_20, 0 as sma_50, 0 as sma_200,
                0 as ema_12, 0 as ema_26
            FROM `{table}`
            WHERE {symbol_col} = @symbol
            ORDER BY timestamp DESC
            LIMIT 500
        """
    elif asset_type in ['forex', 'commodities', 'etfs', 'indices']:
        # These tables use different column naming conventions
        # Volume may or may not exist depending on asset type
        has_volume = asset_type in ['etfs', 'indices']
        volume_col = "IFNULL(volume, 0)" if has_volume else "0"

        query = f"""
            SELECT
                {symbol_col} as symbol,
                datetime,
                open,
                high,
                low,
                close,
                {volume_col} as volume,
                IFNULL(rsi_14, 0) as rsi,
                IFNULL(macd_line, 0) as macd,
                IFNULL(macd_signal, 0) as macd_signal,
                IFNULL(macd_histogram, 0) as macd_hist,
                IFNULL(bbands_upper, 0) as bb_upper,
                IFNULL(bbands_middle, 0) as bb_middle,
                IFNULL(bbands_lower, 0) as bb_lower,
                IFNULL(adx_14, 0) as adx,
                IFNULL(cci_14, 0) as cci,
                IFNULL(obv, 0) as obv,
                IFNULL(atr_14, 0) as atr,
                IFNULL(sma_20, 0) as sma_20,
                IFNULL(sma_50, 0) as sma_50,
                IFNULL(sma_200, 0) as sma_200,
                IFNULL(ema_12, 0) as ema_12,
                IFNULL(ema_26, 0) as ema_26
            FROM `{table}`
            WHERE {symbol_col} = @symbol
            AND CAST(datetime AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
            ORDER BY datetime DESC
            LIMIT 500
        """
    else:
        # Standard OHLCV query with indicators (stocks, crypto)
        query = f"""
            SELECT
                {symbol_col} as symbol,
                datetime,
                open,
                high,
                low,
                close,
                IFNULL(volume, 0) as volume,
                IFNULL(rsi, 0) as rsi,
                IFNULL(macd, 0) as macd,
                IFNULL(macd_signal, 0) as macd_signal,
                IFNULL(macd_hist, 0) as macd_hist,
                IFNULL(bb_upper, 0) as bb_upper,
                IFNULL(bb_middle, 0) as bb_middle,
                IFNULL(bb_lower, 0) as bb_lower,
                IFNULL(adx, 0) as adx,
                IFNULL(cci, 0) as cci,
                IFNULL(obv, 0) as obv,
                IFNULL(atr, 0) as atr,
                IFNULL(sma_20, 0) as sma_20,
                IFNULL(sma_50, 0) as sma_50,
                IFNULL(sma_200, 0) as sma_200,
                IFNULL(ema_12, 0) as ema_12,
                IFNULL(ema_26, 0) as ema_26
            FROM `{table}`
            WHERE {symbol_col} = @symbol
            AND CAST(datetime AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
            ORDER BY datetime DESC
            LIMIT 500
        """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
            bigquery.ScalarQueryParameter("days", "INT64", days),
        ]
    )

    try:
        df = bq_client.query(query, job_config=job_config).to_dataframe()
        return df
    except Exception as e:
        print(f"Query error for {asset_type}/{symbol}: {str(e)}")
        return pd.DataFrame()


def analyze_with_claude(data_summary, analysis_type='prediction'):
    """Use Claude for advanced market analysis"""

    if not anthropic_client:
        return {"error": "Claude API key not configured"}

    prompts = {
        'prediction': f"""You are an expert cryptocurrency trader and technical analyst.
Analyze the following market data and provide a price prediction for the next 24 hours.

Market Data:
{data_summary}

Provide your analysis in JSON format with these fields:
- prediction_1h: predicted price in 1 hour
- prediction_24h: predicted price in 24 hours
- prediction_7d: predicted price in 7 days
- confidence: confidence level (0-100)
- trend: "bullish", "bearish", or "neutral"
- key_factors: list of key factors influencing prediction
- risk_level: "low", "medium", or "high"
- recommendation: "strong_buy", "buy", "hold", "sell", or "strong_sell"
""",
        'pattern': f"""You are an expert in chart pattern recognition and technical analysis.
Analyze the following price and indicator data to identify any significant patterns.

Market Data:
{data_summary}

Identify patterns and provide response in JSON format:
- patterns_detected: list of detected patterns (e.g., "head_and_shoulders", "double_top", "bull_flag")
- support_levels: list of key support price levels
- resistance_levels: list of key resistance price levels
- pattern_reliability: score 0-100 for each pattern
- breakout_probability: probability of breakout (0-100)
- recommended_action: trading recommendation based on patterns
""",
        'signal': f"""You are a professional algorithmic trader. Generate trading signals based on this data.

Market Data:
{data_summary}

Provide trading signals in JSON format:
- signal: "strong_buy", "buy", "hold", "sell", or "strong_sell"
- entry_price: recommended entry price
- target_prices: list of 3 target prices
- stop_loss: recommended stop loss price
- risk_reward_ratio: calculated risk/reward ratio
- timeframe: recommended holding timeframe
- reasoning: brief explanation of the signal
"""
    }

    prompt = prompts.get(analysis_type, prompts['prediction'])

    try:
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract JSON from response
        response_text = message.content[0].text

        # Try to parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"raw_response": response_text}

    except Exception as e:
        return {"error": f"Claude API error: {str(e)}"}


def analyze_with_vertex_ai(data_summary, analysis_type='prediction'):
    """Use Google Gemini for market analysis via API key authentication

    Uses the pre-initialized _gemini_model from module level (same pattern as smart-search).
    """

    prompts = {
        'prediction': f"""Analyze this cryptocurrency market data and predict price movements:

{data_summary}

Provide a structured prediction with:
1. Short-term (1-hour) price forecast
2. Medium-term (24-hour) price forecast
3. Long-term (7-day) trend prediction
4. Confidence level and key reasoning
5. Risk factors to consider

Format as JSON.""",
        'pattern': f"""Identify chart patterns and technical signals from this data:

{data_summary}

Detect:
1. Classic chart patterns (head & shoulders, triangles, etc.)
2. Support and resistance levels
3. Candlestick patterns
4. Breakout opportunities

Format as JSON.""",
        'signal': f"""Generate actionable trading signals from this data:

{data_summary}

Provide:
1. Buy/Sell/Hold recommendation
2. Entry and exit prices
3. Stop loss levels
4. Risk management advice

Format as JSON."""
    }

    prompt = prompts.get(analysis_type, prompts['prediction'])

    try:
        # Use the pre-initialized model from module level
        response = _gemini_model.generate_content(prompt)
        response_text = response.text

        # Try to extract JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            result['model_used'] = GEMINI_MODEL_ID
            return result
        else:
            return {"raw_response": response_text, "model_used": GEMINI_MODEL_ID}

    except Exception as e:
        return {"error": f"Gemini API error: {str(e)}", "model_used": GEMINI_MODEL_ID}


def prepare_data_summary(df, asset_type='crypto'):
    """Prepare a concise summary of market data for AI analysis - supports all asset types"""

    if df.empty:
        return "No data available"

    latest = df.iloc[0]

    # Asset type labels for AI context
    asset_labels = {
        'crypto': 'Cryptocurrency',
        'stocks': 'Stock',
        'etfs': 'ETF',
        'forex': 'Forex Currency Pair',
        'indices': 'Market Index',
        'commodities': 'Commodity',
        'bonds': 'Bond',
        'interest_rates': 'Interest Rate'
    }
    asset_label = asset_labels.get(asset_type, 'Asset')

    # Handle interest rates differently (no technical indicators)
    if asset_type == 'interest_rates':
        summary = f"""
Asset Type: {asset_label}
Current Rate: {latest['close']:.2f}%
Rate Change: {((latest['close'] - df.iloc[-1]['close'])):.2f}% (absolute change)

Recent Rate History (last 10 periods):
{df[['datetime', 'close']].head(10).to_string()}
"""
        return summary

    # Standard summary for tradeable assets
    try:
        change_pct = ((latest['close'] - df.iloc[-1]['close']) / df.iloc[-1]['close'] * 100) if df.iloc[-1]['close'] != 0 else 0
        sma20_pct = ((latest['close'] - latest['sma_20']) / latest['sma_20'] * 100) if latest.get('sma_20', 0) != 0 else 0
        sma200_pct = ((latest['close'] - latest['sma_200']) / latest['sma_200'] * 100) if latest.get('sma_200', 0) != 0 else 0

        summary = f"""
Asset Type: {asset_label}
Current Price: ${latest['close']:.2f}
24h Change: {change_pct:.2f}%
24h High: ${df['high'].max():.2f}
24h Low: ${df['low'].min():.2f}
Volume: {latest['volume']:.0f}

Technical Indicators:
- RSI: {latest.get('rsi', 0):.2f} {'(Oversold)' if latest.get('rsi', 50) < 30 else '(Overbought)' if latest.get('rsi', 50) > 70 else '(Neutral)'}
- MACD: {latest.get('macd', 0):.2f} (Signal: {latest.get('macd_signal', 0):.2f})
- ADX: {latest.get('adx', 0):.2f} {'(Strong Trend)' if latest.get('adx', 0) > 25 else '(Weak Trend)'}
- Bollinger Bands: Upper ${latest.get('bb_upper', 0):.2f}, Lower ${latest.get('bb_lower', 0):.2f}
- Price vs SMA(20): {sma20_pct:.2f}%
- Price vs SMA(200): {sma200_pct:.2f}%

Recent Price Action (last 10 periods):
{df[['datetime', 'close', 'volume']].head(10).to_string()}
"""
    except Exception as e:
        summary = f"""
Asset Type: {asset_label}
Current Price: ${latest['close']:.2f}
Data processing note: Some indicators unavailable ({str(e)})

Recent Price Action (last 10 periods):
{df[['datetime', 'close']].head(10).to_string()}
"""

    return summary


@functions_framework.http
def ai_trading_intelligence(request):
    """
    Main HTTP endpoint for AI trading intelligence - Supports ALL 8 asset types

    Supported asset_types: crypto, stocks, etfs, forex, indices, commodities, bonds, interest_rates

    Example endpoints:
    - ?symbol=AAPL&asset_type=stocks&timeframe=daily&type=prediction&ai_provider=vertex
    - ?symbol=BTC/USD&asset_type=crypto&timeframe=daily&type=pattern&ai_provider=vertex
    - ?symbol=EUR/USD&asset_type=forex&timeframe=hourly&type=signal&ai_provider=vertex
    - ?symbol=SPY&asset_type=etfs&timeframe=daily&type=prediction&ai_provider=vertex
    - ?symbol=SPX&asset_type=indices&timeframe=daily&type=prediction&ai_provider=vertex
    - ?symbol=XAUUSD&asset_type=commodities&timeframe=daily&type=prediction&ai_provider=vertex
    - ?symbol=US&asset_type=interest_rates&timeframe=daily&type=prediction&ai_provider=vertex

    Legacy support: 'pair' parameter still works for backwards compatibility
    """

    # Enable CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {'Access-Control-Allow-Origin': '*'}

    try:
        # Parse request
        request_json = request.get_json(silent=True)
        request_args = request.args

        # Get parameters (support both 'symbol' and legacy 'pair')
        symbol = (request_args.get('symbol') or request_args.get('pair') or
                  (request_json.get('symbol') if request_json else None) or
                  (request_json.get('pair') if request_json else None) or 'BTC/USD')
        asset_type = request_args.get('asset_type') or (request_json.get('asset_type') if request_json else None) or 'crypto'
        timeframe = request_args.get('timeframe') or (request_json.get('timeframe') if request_json else None) or 'daily'
        analysis_type = request_args.get('type') or (request_json.get('type') if request_json else None) or 'prediction'
        ai_provider = request_args.get('ai_provider') or (request_json.get('ai_provider') if request_json else None) or 'vertex'

        # Fetch historical data for any asset type
        df = get_historical_data(symbol, timeframe, days=90, asset_type=asset_type)

        if df.empty:
            return jsonify({
                'error': 'No data available',
                'symbol': symbol,
                'asset_type': asset_type,
                'timeframe': timeframe,
                'hint': 'Check symbol format and asset_type. Examples: AAPL (stocks), BTC/USD (crypto), EUR/USD (forex)'
            }), 404, headers

        # Prepare data summary
        data_summary = prepare_data_summary(df, asset_type=asset_type)

        result = {
            'symbol': symbol,
            'asset_type': asset_type,
            'pair': symbol,  # Legacy support
            'timeframe': timeframe,
            'analysis_type': analysis_type,
            'timestamp': datetime.utcnow().isoformat(),
            'current_price': float(df.iloc[0]['close']),
        }

        # Get AI analysis based on provider
        if ai_provider in ['claude', 'both']:
            claude_analysis = analyze_with_claude(data_summary, analysis_type)
            result['claude_analysis'] = claude_analysis

        if ai_provider in ['vertex', 'both']:
            vertex_analysis = analyze_with_vertex_ai(data_summary, analysis_type)
            result['vertex_analysis'] = vertex_analysis

        # If both providers, create consensus
        if ai_provider == 'both':
            result['consensus'] = create_consensus(
                result.get('claude_analysis', {}),
                result.get('vertex_analysis', {})
            )

        return jsonify(result), 200, headers

    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500, headers


def create_consensus(claude_result, vertex_result):
    """Create consensus analysis from both AI providers"""

    consensus = {
        'providers_agree': False,
        'confidence': 0,
        'recommendation': 'hold'
    }

    # Simple consensus logic - can be enhanced
    try:
        if 'recommendation' in claude_result and 'recommendation' in vertex_result:
            if claude_result['recommendation'] == vertex_result['recommendation']:
                consensus['providers_agree'] = True
                consensus['recommendation'] = claude_result['recommendation']
                consensus['confidence'] = 90
            else:
                consensus['recommendation'] = 'hold'
                consensus['confidence'] = 50
    except:
        pass

    return consensus
