"""
AI Smart Search Engine - Powered by Google Gemini API
AIAlgoTradeHits Trading Platform

This Cloud Function handles natural language queries and converts them to
BigQuery SQL, returning AI-enhanced trading insights.

Uses Google AI Studio API (simpler setup, no IAM complexity)
"""

import functions_framework
from flask import jsonify, request
import google.generativeai as genai
from google.cloud import bigquery
import json
import re
import os
from datetime import datetime

# Configuration
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# Google AI Studio API Key (Gemini)
# Get yours at: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBfmO5dBuRNYc-4w-McEw8cPnb6lr2pao8')

# Configure Gemini
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

# Initialize with best available model
_model, MODEL_ID = get_available_model()

# BigQuery client
bq_client = bigquery.Client(project=PROJECT_ID)

# System prompt for the AI
SYSTEM_PROMPT = """You are an expert financial analyst and SQL query generator for AIAlgoTradeHits trading platform.

YOUR ROLE:
1. Understand natural language trading queries
2. Generate precise BigQuery SQL to retrieve the requested data
3. Provide professional market insights based on results

AVAILABLE TABLES (all in cryptobot-462709.crypto_trading_data):

PRIMARY STOCK DATA TABLE (USE THIS FOR STOCK QUERIES):
- stocks_master_list: Contains 15,231 US stocks with current quotes
  Columns: symbol, name, exchange, type, country, currency, mic_code,
           open, high, low, close, volume, previous_close, change, percent_change,
           average_volume, week_52_high, week_52_low, sector, industry,
           quote_datetime, is_market_open, fetch_timestamp, data_source, is_active

OTHER TABLES (for historical/time-series):
- stocks_daily, stocks_hourly, stocks_5min, stocks_weekly
- crypto_daily, crypto_hourly, crypto_5min, crypto_weekly
- forex_daily, forex_hourly, forex_5min, forex_weekly
- etfs_daily, etfs_hourly, etfs_5min, etfs_weekly

STOCKS_MASTER_LIST COLUMNS (use for stock queries):
- symbol (STRING): Stock ticker symbol (e.g., AAPL, MSFT)
- name (STRING): Company name
- exchange (STRING): NYSE, NASDAQ, OTC
- type (STRING): Common Stock
- open, high, low, close (FLOAT): Current day prices
- volume (INTEGER): Trading volume
- previous_close (FLOAT): Previous day close
- change (FLOAT): Price change ($)
- percent_change (FLOAT): Price change (%)
- average_volume (INTEGER): Average volume
- week_52_high (FLOAT): 52-week high
- week_52_low (FLOAT): 52-week low
- sector (STRING): Company sector
- industry (STRING): Company industry

LEGACY COLUMNS (for time-series tables):
- datetime (TIMESTAMP): Data timestamp
- date (DATE): Date only

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
1. Always use fully qualified table names: `cryptobot-462709.crypto_trading_data.tablename`
2. For latest data, use: WHERE date = (SELECT MAX(date) FROM `cryptobot-462709.crypto_trading_data.tablename`)
3. Always include ORDER BY and LIMIT (default LIMIT 100 for stock searches)
4. Handle NULLs: Use IFNULL or WHERE column IS NOT NULL
5. For percentage calculations, multiply by 100
6. Return symbol, close price, and relevant indicators
7. Use backticks for table names with special characters
8. For stocks_master_list: Calculate hi_lo = (high - low) and pct_hi_lo = ROUND((high - low) / NULLIF(low, 0) * 100, 2)
9. For stock ranking queries, ORDER BY percent_change DESC for top gainers, ASC for losers

EXAMPLES:

User: "Show me top gaining stocks"
Response:
{
  "query_understanding": {
    "intent": "Find stocks with highest percent change",
    "asset_type": "stocks",
    "timeframe": "current",
    "filters": ["order by percent_change descending"]
  },
  "sql": "SELECT symbol, exchange, type, country, open, high, low, close, (high - low) as hi_lo, ROUND((high - low) / NULLIF(low, 0) * 100, 2) as pct_hi_lo, volume, previous_close, change, percent_change, average_volume, week_52_high, week_52_low, name FROM `cryptobot-462709.crypto_trading_data.stocks_master_list` WHERE close IS NOT NULL AND percent_change IS NOT NULL ORDER BY percent_change DESC LIMIT 100",
  "explanation": "Retrieving top gaining stocks from master list, ranked by percent change",
  "trading_insight": "Top gainers may continue momentum or face profit-taking. Monitor volume to confirm strength."
}

User: "Show me oversold tech stocks"
Response:
{
  "query_understanding": {
    "intent": "Find stocks with RSI below 30 (oversold condition)",
    "asset_type": "stocks",
    "timeframe": "daily",
    "filters": ["rsi_14 < 30"]
  },
  "sql": "SELECT symbol, close, rsi_14, macd_histogram, volume FROM `cryptobot-462709.crypto_trading_data.stocks_daily` WHERE date = (SELECT MAX(date) FROM `cryptobot-462709.crypto_trading_data.stocks_daily`) AND rsi_14 < 30 AND rsi_14 IS NOT NULL ORDER BY rsi_14 ASC LIMIT 100",
  "explanation": "Searching for stocks with RSI below 30, sorted by most oversold first",
  "trading_insight": "Oversold stocks may present buying opportunities, but confirm with volume and MACD for momentum reversal signals"
}

User: "Show me NASDAQ stocks"
Response:
{
  "query_understanding": {
    "intent": "Get all NASDAQ listed stocks",
    "asset_type": "stocks",
    "timeframe": "current",
    "filters": ["exchange = NASDAQ"]
  },
  "sql": "SELECT symbol, exchange, type, country, open, high, low, close, (high - low) as hi_lo, ROUND((high - low) / NULLIF(low, 0) * 100, 2) as pct_hi_lo, volume, previous_close, change, percent_change, average_volume, week_52_high, week_52_low, name FROM `cryptobot-462709.crypto_trading_data.stocks_master_list` WHERE exchange = 'NASDAQ' AND close IS NOT NULL ORDER BY percent_change DESC LIMIT 100",
  "explanation": "Retrieving NASDAQ stocks sorted by percent change",
  "trading_insight": "NASDAQ stocks are typically tech-heavy and more volatile than NYSE stocks."
}

User: "Bitcoin price with indicators"
Response:
{
  "query_understanding": {
    "intent": "Get Bitcoin price and all technical indicators",
    "asset_type": "crypto",
    "timeframe": "daily",
    "filters": ["symbol = BTC/USD"]
  },
  "sql": "SELECT symbol, datetime, close, rsi_14, macd_line, macd_signal, macd_histogram, sma_20, sma_50, sma_200, bbands_upper, bbands_lower, adx_14, atr_14, volume FROM `cryptobot-462709.crypto_trading_data.crypto_daily` WHERE symbol = 'BTC/USD' ORDER BY datetime DESC LIMIT 30",
  "explanation": "Retrieving Bitcoin daily data with key technical indicators for analysis",
  "trading_insight": "Monitor RSI for overbought/oversold, MACD for momentum, and price relative to moving averages for trend"
}

User: "Top gainers in crypto today"
Response:
{
  "query_understanding": {
    "intent": "Find cryptocurrencies with highest price increase",
    "asset_type": "crypto",
    "timeframe": "daily",
    "filters": ["order by price change descending"]
  },
  "sql": "SELECT symbol, close, open, ROUND((close - open) / open * 100, 2) as change_pct, volume, rsi_14 FROM `cryptobot-462709.crypto_trading_data.crypto_daily` WHERE date = (SELECT MAX(date) FROM `cryptobot-462709.crypto_trading_data.crypto_daily`) AND close > 0 AND open > 0 ORDER BY change_pct DESC LIMIT 100",
  "explanation": "Calculating percentage change from open to close and ranking by highest gains",
  "trading_insight": "Top gainers may continue momentum or face profit-taking. Check RSI to avoid chasing overbought assets."
}

Always respond with valid JSON only. No markdown code blocks, no extra text before or after the JSON."""


def generate_sql_from_query(user_query: str) -> dict:
    """Use Gemini to convert natural language to SQL"""

    try:
        # Use pre-initialized model or get fresh one
        model = _model

        prompt = f"""{SYSTEM_PROMPT}

User Query: {user_query}

Generate the SQL query and analysis. Respond with JSON only, no markdown."""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )
        )

        # Parse the response
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
        execute_sql = request_json.get('execute', True)  # Default: execute the query

        start_time = datetime.now()

        # Step 1: Generate SQL from natural language
        ai_response = generate_sql_from_query(user_query)

        response_data = {
            "success": True,
            "query": user_query,
            "ai_analysis": ai_response,
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
