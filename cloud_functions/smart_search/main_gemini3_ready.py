"""
AI Smart Search Engine - Ready for Google Gemini 3 Pro
AIAlgoTradeHits Trading Platform

This version supports both:
1. Current: Google Generative AI SDK (gemini-2.0-flash)
2. Future: Vertex AI with Gemini 3 Pro (when enabled by Google)

Switch USE_VERTEX_AI = True once Google grants Vertex AI access.
"""

import functions_framework
from flask import jsonify, request
from google.cloud import bigquery
import json
import re
import os
from datetime import datetime

# Configuration
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# ============================================================
# GEMINI 3 PRO CONFIGURATION
# Set USE_VERTEX_AI = True once Google enables Vertex AI access
# ============================================================
USE_VERTEX_AI = False  # Change to True when Vertex AI is enabled

if USE_VERTEX_AI:
    # Vertex AI Mode - For Gemini 3 Pro
    import vertexai
    from vertexai.generative_models import GenerativeModel, GenerationConfig

    vertexai.init(project=PROJECT_ID, location="us-central1")

    # Gemini 3 Pro model - update model name when Google provides it
    MODEL_NAME = "gemini-3-pro-preview"  # or "gemini-3-pro" when available
    _model = GenerativeModel(MODEL_NAME)
    MODEL_ID = MODEL_NAME
    print(f"Using Vertex AI with model: {MODEL_NAME}")

else:
    # Google Generative AI Mode - Current working version
    import google.generativeai as genai

    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBfmO5dBuRNYc-4w-McEw8cPnb6lr2pao8')
    genai.configure(api_key=GEMINI_API_KEY)

    # Current available models
    MODEL_PRIORITY = [
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ]

    def get_available_model():
        for model_name in MODEL_PRIORITY:
            try:
                model = genai.GenerativeModel(model_name)
                print(f"Using Gemini model: {model_name}")
                return model, model_name
            except Exception as e:
                print(f"Model {model_name} not available: {str(e)}")
                continue
        return genai.GenerativeModel("gemini-2.0-flash"), "gemini-2.0-flash"

    _model, MODEL_ID = get_available_model()

# BigQuery client
bq_client = bigquery.Client(project=PROJECT_ID)

# System prompt for the AI
SYSTEM_PROMPT = """You are an expert financial analyst and SQL query generator for AIAlgoTradeHits trading platform.

YOUR ROLE:
1. Understand natural language trading queries
2. Generate precise BigQuery SQL to retrieve the requested data
3. Provide professional market insights based on results

AVAILABLE TABLES (all in aialgotradehits.crypto_trading_data):
- stocks_daily, stocks_hourly, stocks_5min, stocks_weekly
- crypto_daily, crypto_hourly, crypto_5min, crypto_weekly
- forex_daily, forex_hourly, forex_5min, forex_weekly
- etfs_daily, etfs_hourly, etfs_5min, etfs_weekly
- indices_daily, indices_hourly, indices_5min, indices_weekly
- commodities_daily, commodities_hourly, commodities_5min, commodities_weekly

AVAILABLE COLUMNS (common to all tables):
- symbol (STRING): Ticker symbol
- datetime (TIMESTAMP): Data timestamp
- date (DATE): Date only
- open, high, low, close, volume (FLOAT64): OHLCV data

TECHNICAL INDICATORS (FLOAT64):
- Moving Averages: sma_5, sma_10, sma_20, sma_50, sma_100, sma_200, ema_12, ema_20, ema_26, ema_50, ema_100, ema_200
- Momentum: rsi_14, macd_line, macd_signal, macd_histogram, stoch_k, stoch_d, willr_14, cci_14, mfi_14, mom_10, roc_10
- Trend: adx_14, plus_di, minus_di, aroon_up, aroon_down
- Volatility: atr_14, bbands_upper, bbands_middle, bbands_lower, percent_b
- Volume: obv, ad, adosc, vwap

TRADING TERMINOLOGY:
- "oversold" = RSI < 30
- "overbought" = RSI > 70
- "golden cross" = sma_50 crosses above sma_200
- "death cross" = sma_50 crosses below sma_200
- "bullish MACD" = macd_histogram > 0
- "bearish MACD" = macd_histogram < 0
- "strong trend" = adx_14 > 25
- "weak trend" = adx_14 < 20
- "high volume" = volume > average volume (use subquery)
- "breaking out" = close > bbands_upper

RESPONSE FORMAT (JSON):
{
  "query_understanding": {
    "intent": "brief description of what user wants",
    "asset_type": "stocks|crypto|forex|etfs|indices|commodities",
    "timeframe": "daily|hourly|5min|weekly",
    "filters": ["list of conditions identified"]
  },
  "sql": "YOUR BIGQUERY SQL HERE",
  "explanation": "Brief explanation of the query logic",
  "trading_insight": "Professional trading perspective on this type of query"
}

SQL GENERATION RULES:
1. Always use fully qualified table names: `aialgotradehits.crypto_trading_data.tablename`
2. For latest data, use: WHERE date = (SELECT MAX(date) FROM `aialgotradehits.crypto_trading_data.tablename`)
3. Always include ORDER BY and LIMIT (default LIMIT 20)
4. Handle NULLs: Use IFNULL or WHERE column IS NOT NULL
5. For percentage calculations, multiply by 100
6. Return symbol, close price, and relevant indicators
7. Use backticks for table names with special characters

Always respond with valid JSON only. No markdown code blocks, no extra text before or after the JSON."""


def generate_sql_from_query(user_query: str) -> dict:
    """Use Gemini to convert natural language to SQL"""

    prompt = f"""{SYSTEM_PROMPT}

User Query: {user_query}

Generate the SQL query and analysis. Respond with JSON only, no markdown."""

    try:
        if USE_VERTEX_AI:
            # Vertex AI generation
            response = _model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.1,
                    top_p=0.95,
                    max_output_tokens=2048,
                )
            )
            response_text = response.text.strip()
        else:
            # Google Generative AI generation
            import google.generativeai as genai
            response = _model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            response_text = response.text.strip()

        # Clean up response if needed (remove markdown code blocks)
        if response_text.startswith("```"):
            response_text = re.sub(r'^```json?\n?', '', response_text)
            response_text = re.sub(r'\n?```$', '', response_text)

        # Try to find JSON in response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            response_text = json_match.group()

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            result = {
                "query_understanding": {"intent": "Parse error", "filters": []},
                "sql": None,
                "explanation": f"Failed to parse AI response: {str(e)}",
                "trading_insight": None,
                "raw_response": response_text[:500]
            }

        return result

    except Exception as e:
        return {
            "query_understanding": {"intent": "Error", "filters": []},
            "sql": None,
            "explanation": f"AI Error: {str(e)}",
            "trading_insight": None
        }


def execute_query(sql: str) -> dict:
    """Execute BigQuery SQL and return results"""
    try:
        query_job = bq_client.query(sql)
        results = query_job.result()

        # Convert to list of dicts
        rows = []
        for row in results:
            row_dict = dict(row)
            # Convert any non-serializable types
            for key, value in row_dict.items():
                if hasattr(value, 'isoformat'):
                    row_dict[key] = value.isoformat()
                elif isinstance(value, float) and (value != value):  # NaN check
                    row_dict[key] = None
            rows.append(row_dict)

        return {"success": True, "data": rows, "count": len(rows)}

    except Exception as e:
        return {"success": False, "error": str(e), "data": [], "count": 0}


@functions_framework.http
def smart_search(request):
    """
    AI Smart Search HTTP endpoint

    POST /smart_search
    Body: {"query": "your natural language query", "execute": true/false}

    Returns: JSON with AI analysis, SQL, and optionally results
    """

    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }

    try:
        # Handle GET request (health check)
        if request.method == 'GET':
            return jsonify({
                "status": "healthy",
                "service": "smart-search",
                "model": MODEL_ID,
                "vertex_ai_enabled": USE_VERTEX_AI,
                "timestamp": datetime.utcnow().isoformat()
            }), 200, headers

        # Get the query from request
        request_json = request.get_json(silent=True)

        if not request_json or 'query' not in request_json:
            return jsonify({
                "success": False,
                "error": "Missing 'query' in request body. Send POST with {\"query\": \"your question\"}"
            }), 400, headers

        user_query = request_json['query']
        execute_sql = request_json.get('execute', True)

        start_time = datetime.now()

        # Step 1: Generate SQL from natural language
        ai_response = generate_sql_from_query(user_query)

        response_data = {
            "success": True,
            "query": user_query,
            "ai_analysis": ai_response,
            "model_used": MODEL_ID,
            "vertex_ai": USE_VERTEX_AI,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Step 2: Execute the SQL if requested and SQL was generated
        if execute_sql and ai_response.get('sql'):
            sql_result = execute_query(ai_response['sql'])
            response_data["results"] = sql_result

        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        response_data["execution_time_ms"] = round(execution_time, 2)

        return jsonify(response_data), 200, headers

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500, headers
