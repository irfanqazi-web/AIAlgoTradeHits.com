"""
Complete ADK Trading Agent Implementation for AIAlgoTradeHits
Following Google ADK Text-to-SQL Reference Guide Patterns

Developer: irfan.qazi@aialgotradehits.com
Reference: Google_ADK_Text_to_SQL_Reference_Guide.pdf

This implementation creates a multi-agent trading system with:
- market_data_agent: API integrations and real-time data
- technical_analysis_agent: RSI, MACD, pattern detection
- database_agent: MCP Toolbox BigQuery queries
- signal_agent: BUY/SELL/HOLD recommendations
- trading_coordinator (root_agent): Orchestrates all agents
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Google ADK imports
try:
    from google.adk.agents import Agent, ParallelAgent, SequentialAgent
    from google.adk.tools import FunctionTool
    from google.adk.runners import Runner
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    print("Note: google-adk not installed. Install with: pip install google-adk")
    # Define placeholder classes for development
    class Agent:
        def __init__(self, *args, **kwargs): pass
    class ParallelAgent:
        def __init__(self, *args, **kwargs): pass
    class SequentialAgent:
        def __init__(self, *args, **kwargs): pass
    class FunctionTool:
        def __init__(self, *args, **kwargs): pass

# Google AI SDK for Gemini
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Note: google-genai not installed. Install with: pip install google-genai")

# BigQuery client
try:
    from google.cloud import bigquery
    BQ_AVAILABLE = True
except ImportError:
    BQ_AVAILABLE = False
    print("Note: google-cloud-bigquery not installed")

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
LOCATION = 'us-central1'
MODEL_NAME = 'gemini-2.5-flash'

# Trading thresholds
TRADING_CONFIG = {
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    'adx_strong_trend': 25,
    'adx_weak_trend': 20,
    'volume_spike_multiplier': 1.5,
    'breakout_threshold_pct': 95,  # % of 52-week high
    'breakdown_threshold_pct': 105,  # % of 52-week low
}

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class TradingSignal:
    """Trading signal output"""
    symbol: str
    asset_type: str
    signal: str  # BUY, SELL, HOLD
    strength: float  # 0-100
    price: float
    indicators: Dict[str, float]
    reasons: List[str]
    timestamp: datetime

@dataclass
class MarketAnalysis:
    """Market analysis result"""
    sector: str
    trend: str  # BULLISH, BEARISH, NEUTRAL
    top_gainers: List[Dict]
    top_losers: List[Dict]
    oversold_assets: List[Dict]
    overbought_assets: List[Dict]
    breakout_candidates: List[Dict]

# =============================================================================
# TOOL DEFINITIONS (Following MCP Toolbox Pattern)
# =============================================================================

def get_stock_daily_data(symbol: str, limit: int = 100) -> Dict[str, Any]:
    """
    Get daily stock data with technical indicators.

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        limit: Number of records to return

    Returns:
        Dict with stock data including OHLCV and indicators
    """
    if not BQ_AVAILABLE:
        return {"error": "BigQuery not available"}

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
    SELECT symbol, name, sector, datetime, open, high, low, close, volume,
           percent_change, rsi, macd, macd_signal, macd_histogram,
           sma_20, sma_50, sma_200, adx, atr, bollinger_upper, bollinger_lower,
           week_52_high, week_52_low
    FROM `{PROJECT_ID}.{DATASET_ID}.v2_stocks_daily`
    WHERE symbol = @symbol
    ORDER BY datetime DESC
    LIMIT @limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    try:
        results = client.query(query, job_config=job_config).result()
        data = [dict(row) for row in results]
        return {"success": True, "data": data, "count": len(data)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_crypto_daily_data(symbol: str, limit: int = 100) -> Dict[str, Any]:
    """
    Get daily cryptocurrency data with technical indicators.

    Args:
        symbol: Crypto symbol (e.g., BTCUSD, ETHUSD)
        limit: Number of records to return
    """
    if not BQ_AVAILABLE:
        return {"error": "BigQuery not available"}

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
    SELECT symbol, name, datetime, open, high, low, close, volume,
           percent_change, rsi, macd, macd_signal, macd_histogram,
           sma_20, sma_50, sma_200, adx, atr, bollinger_upper, bollinger_lower
    FROM `{PROJECT_ID}.{DATASET_ID}.v2_crypto_daily`
    WHERE symbol = @symbol
    ORDER BY datetime DESC
    LIMIT @limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    try:
        results = client.query(query, job_config=job_config).result()
        data = [dict(row) for row in results]
        return {"success": True, "data": data, "count": len(data)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_oversold_assets(asset_type: str = 'stocks', rsi_threshold: float = 30, limit: int = 20) -> Dict[str, Any]:
    """
    Find oversold assets with RSI below threshold.

    Args:
        asset_type: 'stocks', 'crypto', 'forex', 'etfs', 'indices', 'commodities'
        rsi_threshold: RSI value threshold (default 30)
        limit: Number of results
    """
    if not BQ_AVAILABLE:
        return {"error": "BigQuery not available"}

    client = bigquery.Client(project=PROJECT_ID)
    table = f"v2_{asset_type}_daily"

    query = f"""
    WITH latest AS (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
    )
    SELECT symbol, name, close, percent_change, rsi, macd, adx, volume
    FROM latest
    WHERE rn = 1
      AND rsi < @rsi_threshold
      AND rsi IS NOT NULL
    ORDER BY rsi ASC
    LIMIT @limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("rsi_threshold", "FLOAT64", rsi_threshold),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    try:
        results = client.query(query, job_config=job_config).result()
        data = [dict(row) for row in results]
        return {"success": True, "data": data, "count": len(data), "criteria": f"RSI < {rsi_threshold}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_overbought_assets(asset_type: str = 'stocks', rsi_threshold: float = 70, limit: int = 20) -> Dict[str, Any]:
    """
    Find overbought assets with RSI above threshold.
    """
    if not BQ_AVAILABLE:
        return {"error": "BigQuery not available"}

    client = bigquery.Client(project=PROJECT_ID)
    table = f"v2_{asset_type}_daily"

    query = f"""
    WITH latest AS (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
    )
    SELECT symbol, name, close, percent_change, rsi, macd, adx, volume
    FROM latest
    WHERE rn = 1
      AND rsi > @rsi_threshold
      AND rsi IS NOT NULL
    ORDER BY rsi DESC
    LIMIT @limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("rsi_threshold", "FLOAT64", rsi_threshold),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    try:
        results = client.query(query, job_config=job_config).result()
        data = [dict(row) for row in results]
        return {"success": True, "data": data, "count": len(data), "criteria": f"RSI > {rsi_threshold}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_top_gainers(asset_type: str = 'stocks', limit: int = 10) -> Dict[str, Any]:
    """Get top performing assets by daily percent change."""
    if not BQ_AVAILABLE:
        return {"error": "BigQuery not available"}

    client = bigquery.Client(project=PROJECT_ID)
    table = f"v2_{asset_type}_daily"

    query = f"""
    WITH latest AS (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
    )
    SELECT symbol, name, close, percent_change, volume, rsi, macd
    FROM latest
    WHERE rn = 1 AND percent_change IS NOT NULL
    ORDER BY percent_change DESC
    LIMIT @limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    try:
        results = client.query(query, job_config=job_config).result()
        data = [dict(row) for row in results]
        return {"success": True, "data": data, "count": len(data)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_top_losers(asset_type: str = 'stocks', limit: int = 10) -> Dict[str, Any]:
    """Get worst performing assets by daily percent change."""
    if not BQ_AVAILABLE:
        return {"error": "BigQuery not available"}

    client = bigquery.Client(project=PROJECT_ID)
    table = f"v2_{asset_type}_daily"

    query = f"""
    WITH latest AS (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
    )
    SELECT symbol, name, close, percent_change, volume, rsi, macd
    FROM latest
    WHERE rn = 1 AND percent_change IS NOT NULL
    ORDER BY percent_change ASC
    LIMIT @limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    try:
        results = client.query(query, job_config=job_config).result()
        data = [dict(row) for row in results]
        return {"success": True, "data": data, "count": len(data)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def find_breakout_candidates(asset_type: str = 'stocks', threshold_pct: float = 95, limit: int = 20) -> Dict[str, Any]:
    """Find assets breaking 52-week highs (potential breakouts)."""
    if not BQ_AVAILABLE:
        return {"error": "BigQuery not available"}

    client = bigquery.Client(project=PROJECT_ID)
    table = f"v2_{asset_type}_daily"

    query = f"""
    WITH latest AS (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
    )
    SELECT symbol, name, close, week_52_high,
           ROUND(close / week_52_high * 100, 2) as pct_of_52w_high,
           percent_change, volume, rsi, adx
    FROM latest
    WHERE rn = 1
      AND close >= week_52_high * (@threshold_pct / 100)
      AND week_52_high IS NOT NULL
      AND week_52_high > 0
    ORDER BY pct_of_52w_high DESC
    LIMIT @limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("threshold_pct", "FLOAT64", threshold_pct),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    try:
        results = client.query(query, job_config=job_config).result()
        data = [dict(row) for row in results]
        return {"success": True, "data": data, "count": len(data), "criteria": f"Price >= {threshold_pct}% of 52-week high"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def find_strong_trends(asset_type: str = 'stocks', adx_threshold: float = 25, limit: int = 20) -> Dict[str, Any]:
    """Find assets with strong trends (ADX > threshold) and bullish MACD."""
    if not BQ_AVAILABLE:
        return {"error": "BigQuery not available"}

    client = bigquery.Client(project=PROJECT_ID)
    table = f"v2_{asset_type}_daily"

    query = f"""
    WITH latest AS (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
    )
    SELECT symbol, name, close, percent_change, adx, macd, macd_signal, rsi
    FROM latest
    WHERE rn = 1
      AND adx > @adx_threshold
      AND macd > macd_signal
      AND adx IS NOT NULL
    ORDER BY adx DESC
    LIMIT @limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("adx_threshold", "FLOAT64", adx_threshold),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    try:
        results = client.query(query, job_config=job_config).result()
        data = [dict(row) for row in results]
        return {"success": True, "data": data, "count": len(data), "criteria": f"ADX > {adx_threshold} and MACD > Signal"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def execute_custom_sql(sql: str) -> Dict[str, Any]:
    """
    Execute a custom SQL query against BigQuery.
    Only SELECT statements are allowed for safety.
    """
    if not BQ_AVAILABLE:
        return {"error": "BigQuery not available"}

    # Safety check - only allow SELECT
    sql_upper = sql.upper().strip()
    if not sql_upper.startswith('SELECT'):
        return {"error": "Only SELECT statements are allowed"}

    # Check for dangerous keywords
    dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'CREATE', 'GRANT']
    for keyword in dangerous:
        if keyword in sql_upper:
            return {"error": f"Dangerous keyword detected: {keyword}"}

    client = bigquery.Client(project=PROJECT_ID)

    try:
        results = client.query(sql).result()
        data = [dict(row) for row in results]
        return {"success": True, "data": data, "count": len(data)}
    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def calculate_signal_strength(rsi: float, macd: float, macd_signal: float, adx: float) -> tuple:
    """
    Calculate trading signal and strength based on technical indicators.

    Returns:
        tuple: (signal: str, strength: float, reasons: list)
    """
    signal = "HOLD"
    strength = 50.0
    reasons = []

    # RSI Analysis
    if rsi is not None:
        if rsi < 30:
            strength += 20
            reasons.append(f"Oversold (RSI={rsi:.1f})")
        elif rsi < 40:
            strength += 10
            reasons.append(f"Approaching oversold (RSI={rsi:.1f})")
        elif rsi > 70:
            strength -= 20
            reasons.append(f"Overbought (RSI={rsi:.1f})")
        elif rsi > 60:
            strength -= 10
            reasons.append(f"Approaching overbought (RSI={rsi:.1f})")

    # MACD Analysis
    if macd is not None and macd_signal is not None:
        macd_diff = macd - macd_signal
        if macd_diff > 0:
            strength += 15
            reasons.append(f"Bullish MACD crossover")
        else:
            strength -= 15
            reasons.append(f"Bearish MACD")

    # ADX Analysis (Trend Strength)
    if adx is not None:
        if adx > 25:
            reasons.append(f"Strong trend (ADX={adx:.1f})")
            # Strong trend amplifies the signal
            if strength > 50:
                strength += 10
            elif strength < 50:
                strength -= 10
        elif adx < 20:
            reasons.append(f"Weak trend (ADX={adx:.1f})")

    # Determine signal
    if strength >= 70:
        signal = "BUY"
    elif strength <= 30:
        signal = "SELL"
    else:
        signal = "HOLD"

    # Clamp strength to 0-100
    strength = max(0, min(100, strength))

    return signal, strength, reasons


def analyze_asset(symbol: str, asset_type: str = 'stocks') -> TradingSignal:
    """
    Perform comprehensive analysis on a single asset.

    Args:
        symbol: Asset symbol
        asset_type: Type of asset

    Returns:
        TradingSignal with recommendation
    """
    # Get data based on asset type
    if asset_type == 'stocks':
        result = get_stock_daily_data(symbol, limit=1)
    elif asset_type == 'crypto':
        result = get_crypto_daily_data(symbol, limit=1)
    else:
        # Generic query
        result = get_stock_daily_data(symbol, limit=1)

    if not result.get('success') or not result.get('data'):
        return TradingSignal(
            symbol=symbol,
            asset_type=asset_type,
            signal="UNKNOWN",
            strength=0,
            price=0,
            indicators={},
            reasons=["No data available"],
            timestamp=datetime.now()
        )

    data = result['data'][0]

    # Extract indicators
    rsi = data.get('rsi')
    macd = data.get('macd')
    macd_signal = data.get('macd_signal')
    adx = data.get('adx')
    close = data.get('close', 0)

    # Calculate signal
    signal, strength, reasons = calculate_signal_strength(rsi, macd, macd_signal, adx)

    return TradingSignal(
        symbol=symbol,
        asset_type=asset_type,
        signal=signal,
        strength=strength,
        price=close,
        indicators={
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'adx': adx,
            'sma_20': data.get('sma_20'),
            'sma_50': data.get('sma_50'),
            'sma_200': data.get('sma_200'),
        },
        reasons=reasons,
        timestamp=datetime.now()
    )


# =============================================================================
# ADK AGENT DEFINITIONS (Following Reference Guide Pattern)
# =============================================================================

# Define tools for agents
stock_data_tool = FunctionTool(get_stock_daily_data) if ADK_AVAILABLE else None
crypto_data_tool = FunctionTool(get_crypto_daily_data) if ADK_AVAILABLE else None
oversold_tool = FunctionTool(search_oversold_assets) if ADK_AVAILABLE else None
overbought_tool = FunctionTool(search_overbought_assets) if ADK_AVAILABLE else None
gainers_tool = FunctionTool(get_top_gainers) if ADK_AVAILABLE else None
losers_tool = FunctionTool(get_top_losers) if ADK_AVAILABLE else None
breakout_tool = FunctionTool(find_breakout_candidates) if ADK_AVAILABLE else None
trend_tool = FunctionTool(find_strong_trends) if ADK_AVAILABLE else None
sql_tool = FunctionTool(execute_custom_sql) if ADK_AVAILABLE else None


def create_market_data_agent():
    """
    Market Data Agent - Handles real-time data retrieval and API integrations.
    """
    if not ADK_AVAILABLE:
        return None

    return Agent(
        name="market_data_agent",
        model=MODEL_NAME,
        description="Retrieves real-time market data for stocks and cryptocurrencies",
        instruction="""You are a market data specialist. Your role is to:
1. Fetch current price and volume data for requested assets
2. Retrieve historical OHLCV data for analysis
3. Provide real-time market snapshots
4. Support both stocks and cryptocurrency data

Always return data in a structured format with symbol, price, volume, and timestamp.
Use the appropriate tool based on asset type (stocks vs crypto).
""",
        tools=[stock_data_tool, crypto_data_tool]
    )


def create_technical_analysis_agent():
    """
    Technical Analysis Agent - Computes and interprets technical indicators.
    """
    if not ADK_AVAILABLE:
        return None

    return Agent(
        name="technical_analysis_agent",
        model=MODEL_NAME,
        description="Analyzes technical indicators (RSI, MACD, ADX, Bollinger Bands)",
        instruction="""You are a technical analysis expert. Your role is to:
1. Analyze RSI levels (oversold < 30, overbought > 70)
2. Interpret MACD signals (bullish/bearish crossovers)
3. Evaluate trend strength using ADX (strong > 25)
4. Identify Bollinger Band breakouts
5. Detect chart patterns and support/resistance levels

Provide clear interpretations of indicator values and their implications.
Use the oversold/overbought search tools for screening.
""",
        tools=[oversold_tool, overbought_tool, trend_tool]
    )


def create_database_agent():
    """
    Database Agent - Handles MCP Toolbox queries via BigQuery.
    """
    if not ADK_AVAILABLE:
        return None

    return Agent(
        name="database_agent",
        model=MODEL_NAME,
        description="Executes database queries for market data and analytics",
        instruction=f"""You are a database query specialist for the AIAlgoTradeHits trading platform.

DATABASE: {PROJECT_ID}.{DATASET_ID}

AVAILABLE TABLES:
- v2_stocks_daily: Daily stock data with 50+ fields and 29 technical indicators
- v2_crypto_daily: Daily cryptocurrency data
- v2_forex_daily: Daily forex pair data
- v2_etfs_daily: Daily ETF data
- v2_indices_daily: Daily market index data
- v2_commodities_daily: Daily commodity data
- v2_stocks_weekly_summary: Weekly aggregated stock data
- v2_crypto_weekly_summary: Weekly aggregated crypto data

QUERY RULES:
1. Always use fully qualified table names
2. Include ORDER BY and LIMIT clauses
3. Handle NULL values with IS NOT NULL or COALESCE
4. For latest data, use ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC)
5. Only generate SELECT statements

Use the tools to execute queries and return structured results.
""",
        tools=[sql_tool, gainers_tool, losers_tool, breakout_tool]
    )


def create_signal_agent():
    """
    Signal Agent - Generates BUY/SELL/HOLD recommendations.
    """
    if not ADK_AVAILABLE:
        return None

    return Agent(
        name="signal_agent",
        model=MODEL_NAME,
        description="Generates trading signals based on technical and quantitative analysis",
        instruction="""You are a trading signal generator. Your role is to:
1. Combine technical indicator analysis to generate signals
2. Produce BUY, SELL, or HOLD recommendations
3. Provide signal strength (0-100 scale)
4. List supporting reasons for each recommendation

SIGNAL CRITERIA:
- BUY: RSI < 30 + Bullish MACD + Strong trend (ADX > 25)
- SELL: RSI > 70 + Bearish MACD crossover
- HOLD: Mixed signals or weak trend

Always provide risk assessment and confidence level with signals.
""",
        tools=[oversold_tool, overbought_tool, trend_tool]
    )


def create_trading_coordinator():
    """
    Trading Coordinator (Root Agent) - Orchestrates all specialized agents.
    Following ADK Reference Guide Section 8 pattern.
    """
    if not ADK_AVAILABLE:
        return None

    # Create sub-agents
    market_data_agent = create_market_data_agent()
    technical_analysis_agent = create_technical_analysis_agent()
    database_agent = create_database_agent()
    signal_agent = create_signal_agent()

    # Parallel agent for data collection (market data + database queries)
    data_collection_agent = ParallelAgent(
        name="data_collection",
        sub_agents=[market_data_agent, database_agent]
    )

    # Sequential agent for analysis pipeline
    analysis_pipeline = SequentialAgent(
        name="analysis_pipeline",
        sub_agents=[data_collection_agent, technical_analysis_agent, signal_agent]
    )

    # Root trading coordinator
    return Agent(
        name="trading_coordinator",
        model=MODEL_NAME,
        description="Master trading coordinator that orchestrates market analysis and signal generation",
        instruction="""You are the master trading coordinator for AIAlgoTradeHits.

Your responsibilities:
1. Coordinate data collection from multiple sources
2. Orchestrate technical and quantitative analysis
3. Generate comprehensive trading reports
4. Provide actionable trading recommendations

WORKFLOW:
1. First, gather market data using the data collection agent
2. Then, run technical analysis on the gathered data
3. Finally, generate trading signals with recommendations

For market scans, check:
- Top gainers and losers
- Oversold opportunities (RSI < 30)
- Breakout candidates (near 52-week highs)
- Strong trend stocks (ADX > 25 with bullish MACD)

Always provide a summary with the top 3-5 opportunities.
""",
        sub_agents=[analysis_pipeline]
    )


# =============================================================================
# TEXT-TO-SQL AGENT
# =============================================================================

class TradingTextToSQLAgent:
    """
    Text-to-SQL Agent using Gemini 2.5 for natural language query processing.
    """

    def __init__(self, api_key: Optional[str] = None):
        if not GENAI_AVAILABLE:
            raise ImportError("google-genai not installed")

        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()
        self.bq_client = bigquery.Client(project=PROJECT_ID) if BQ_AVAILABLE else None

        # Load schema context
        self.schema_context = self._build_schema_context()

    def _build_schema_context(self) -> str:
        """Build comprehensive schema context for prompts."""
        return f"""
DATABASE CONTEXT:
Project: {PROJECT_ID}
Dataset: {DATASET_ID}

AVAILABLE TABLES:
1. v2_stocks_daily - Daily stock price data with 50+ fields including OHLCV and 29 technical indicators
   Key columns: symbol, name, sector, datetime, open, high, low, close, volume, percent_change,
   rsi, macd, macd_signal, sma_20, sma_50, sma_200, adx, atr, bollinger_upper, bollinger_lower

2. v2_crypto_daily - Daily cryptocurrency data with technical indicators
   Key columns: symbol, name, datetime, close, volume, percent_change, rsi, macd, adx

3. v2_forex_daily - Daily forex pair data
4. v2_etfs_daily - Daily ETF data
5. v2_indices_daily - Daily market index data
6. v2_commodities_daily - Daily commodity data
7. v2_stocks_weekly_summary - Weekly aggregated stock data
8. v2_crypto_weekly_summary - Weekly aggregated crypto data

TRADING TERMINOLOGY:
- "oversold" = RSI < 30
- "overbought" = RSI > 70
- "strong trend" = ADX > 25
- "bullish MACD" = MACD > MACD_SIGNAL
- "breakout" = Close near 52-week high (>= 95%)
- "gainers" = percent_change > 0, ORDER BY percent_change DESC
- "losers" = percent_change < 0, ORDER BY percent_change ASC
"""

    def generate_sql(self, query: str, asset_type: str = 'all') -> Dict[str, Any]:
        """Generate SQL from natural language query."""
        prompt = f"""{self.schema_context}

USER QUERY: "{query}"

Generate a BigQuery SQL query that answers this question.
Use fully qualified table names: `{PROJECT_ID}.{DATASET_ID}.table_name`
Always include ORDER BY and LIMIT clauses.
Return ONLY the SQL query, no explanations.

SQL:"""

        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=[prompt],
                config=types.GenerateContentConfig(temperature=0.1)
            )

            sql = self._extract_sql(response.text)
            return {"success": True, "sql": sql}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _extract_sql(self, response: str) -> str:
        """Extract SQL from model response."""
        import re
        sql = re.sub(r'```sql?\n?', '', response)
        sql = re.sub(r'```', '', sql)
        sql = sql.strip()
        if 'SELECT' in sql.upper():
            idx = sql.upper().find('SELECT')
            sql = sql[idx:]
        return sql

    def query(self, natural_language: str, execute: bool = True) -> Dict[str, Any]:
        """Full pipeline: parse query, generate SQL, and execute."""
        result = self.generate_sql(natural_language)

        if not result['success']:
            return result

        if execute and self.bq_client:
            try:
                query_job = self.bq_client.query(result['sql'])
                data = [dict(row) for row in query_job.result()]
                result['data'] = data
                result['count'] = len(data)
            except Exception as e:
                result['execution_error'] = str(e)

        return result


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def scan_market(scan_type: str = 'oversold', asset_type: str = 'stocks', limit: int = 20) -> Dict[str, Any]:
    """
    Quick market scan function.

    Args:
        scan_type: 'oversold', 'overbought', 'gainers', 'losers', 'breakouts', 'strong_trends'
        asset_type: 'stocks', 'crypto', etc.
        limit: Number of results
    """
    scanners = {
        'oversold': lambda: search_oversold_assets(asset_type, 30, limit),
        'overbought': lambda: search_overbought_assets(asset_type, 70, limit),
        'gainers': lambda: get_top_gainers(asset_type, limit),
        'losers': lambda: get_top_losers(asset_type, limit),
        'breakouts': lambda: find_breakout_candidates(asset_type, 95, limit),
        'strong_trends': lambda: find_strong_trends(asset_type, 25, limit),
    }

    scanner = scanners.get(scan_type, scanners['oversold'])
    return scanner()


def get_trading_opportunities(asset_type: str = 'stocks') -> Dict[str, Any]:
    """
    Get comprehensive trading opportunities across multiple criteria.
    """
    return {
        'oversold': search_oversold_assets(asset_type, 30, 10),
        'breakouts': find_breakout_candidates(asset_type, 95, 10),
        'strong_trends': find_strong_trends(asset_type, 25, 10),
        'top_gainers': get_top_gainers(asset_type, 10),
        'timestamp': datetime.now().isoformat()
    }


# =============================================================================
# MAIN / CLI
# =============================================================================

def main():
    """Interactive CLI for testing the trading agents."""
    print("=" * 70)
    print("AIAlgoTradeHits ADK Trading Agent System")
    print("Developer: irfan.qazi@aialgotradehits.com")
    print("=" * 70)

    print("\nInitializing agents...")

    # Check dependencies
    print(f"  ADK Available: {ADK_AVAILABLE}")
    print(f"  Gemini Available: {GENAI_AVAILABLE}")
    print(f"  BigQuery Available: {BQ_AVAILABLE}")

    if not BQ_AVAILABLE:
        print("\nWarning: BigQuery not available. Running in demo mode.")

    # Demo market scan
    print("\n" + "=" * 70)
    print("MARKET SCAN DEMO")
    print("=" * 70)

    scans = ['oversold', 'breakouts', 'strong_trends', 'gainers']

    for scan_type in scans:
        print(f"\n--- {scan_type.upper()} STOCKS ---")
        result = scan_market(scan_type, 'stocks', 5)

        if result.get('success'):
            for item in result.get('data', [])[:5]:
                symbol = item.get('symbol', 'N/A')
                close = item.get('close', 0)
                change = item.get('percent_change', 0)
                rsi = item.get('rsi', 'N/A')
                print(f"  {symbol}: ${close:.2f} ({change:+.2f}%) RSI={rsi}")
        else:
            print(f"  Error: {result.get('error', 'Unknown')}")

    print("\n" + "=" * 70)
    print("System ready. Use TradingTextToSQLAgent for natural language queries.")
    print("Example: agent.query('Find oversold tech stocks with strong trends')")
    print("=" * 70)


if __name__ == "__main__":
    main()
