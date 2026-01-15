"""
BigQuery NL2SQL Integration for AIAlgoTradeHits
Following Google ADK Text-to-SQL Reference Guide Section 6

Developer: irfan.qazi@aialgotradehits.com

This module provides:
1. Natural Language to SQL conversion using Gemini 2.5
2. Direct BigQuery integration via Vertex AI
3. Semantic search with query caching
4. Safe query execution with validation
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Google Cloud imports
try:
    from google.cloud import bigquery
    BQ_AVAILABLE = True
except ImportError:
    BQ_AVAILABLE = False

# Vertex AI imports
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False

# Google AI SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
LOCATION = 'us-central1'

# Models
GEMINI_FLASH = 'gemini-2.5-flash'
GEMINI_PRO = 'gemini-2.5-pro'

# Query cache (in-memory for demo, use Redis/Memcached in production)
QUERY_CACHE: Dict[str, Dict] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes

# =============================================================================
# SCHEMA DEFINITIONS
# =============================================================================

TABLE_SCHEMAS = {
    'v2_stocks_daily': {
        'description': 'Daily stock price data with 50+ fields including OHLCV and 29 technical indicators',
        'columns': {
            'symbol': 'Stock ticker symbol (STRING)',
            'name': 'Company name (STRING)',
            'sector': 'Market sector (STRING)',
            'industry': 'Industry classification (STRING)',
            'datetime': 'Timestamp of the data (TIMESTAMP)',
            'open': 'Opening price (FLOAT)',
            'high': 'Highest price (FLOAT)',
            'low': 'Lowest price (FLOAT)',
            'close': 'Closing price (FLOAT)',
            'volume': 'Trading volume (FLOAT)',
            'percent_change': 'Daily price change percentage (FLOAT)',
            'rsi': 'Relative Strength Index 0-100 (FLOAT)',
            'macd': 'MACD line value (FLOAT)',
            'macd_signal': 'MACD signal line (FLOAT)',
            'macd_histogram': 'MACD histogram (FLOAT)',
            'sma_20': '20-day Simple Moving Average (FLOAT)',
            'sma_50': '50-day Simple Moving Average (FLOAT)',
            'sma_200': '200-day Simple Moving Average (FLOAT)',
            'ema_12': '12-day Exponential Moving Average (FLOAT)',
            'ema_26': '26-day Exponential Moving Average (FLOAT)',
            'adx': 'Average Directional Index (FLOAT)',
            'atr': 'Average True Range (FLOAT)',
            'bollinger_upper': 'Upper Bollinger Band (FLOAT)',
            'bollinger_middle': 'Middle Bollinger Band (FLOAT)',
            'bollinger_lower': 'Lower Bollinger Band (FLOAT)',
            'week_52_high': '52-week high price (FLOAT)',
            'week_52_low': '52-week low price (FLOAT)',
        }
    },
    'v2_crypto_daily': {
        'description': 'Daily cryptocurrency data with technical indicators',
        'columns': {
            'symbol': 'Crypto symbol like BTCUSD (STRING)',
            'name': 'Cryptocurrency name (STRING)',
            'datetime': 'Timestamp (TIMESTAMP)',
            'open': 'Opening price (FLOAT)',
            'high': 'High price (FLOAT)',
            'low': 'Low price (FLOAT)',
            'close': 'Closing price (FLOAT)',
            'volume': 'Trading volume (FLOAT)',
            'percent_change': 'Daily change % (FLOAT)',
            'rsi': 'RSI indicator (FLOAT)',
            'macd': 'MACD value (FLOAT)',
            'adx': 'Trend strength (FLOAT)',
        }
    },
    'v2_forex_daily': {
        'description': 'Daily forex pair data',
        'columns': {
            'symbol': 'Forex pair like EUR/USD (STRING)',
            'datetime': 'Timestamp (TIMESTAMP)',
            'open': 'Opening rate (FLOAT)',
            'high': 'High rate (FLOAT)',
            'low': 'Low rate (FLOAT)',
            'close': 'Closing rate (FLOAT)',
            'percent_change': 'Daily change % (FLOAT)',
            'rsi': 'RSI indicator (FLOAT)',
            'atr': 'Average True Range (FLOAT)',
        }
    },
    'v2_etfs_daily': {'description': 'Daily ETF data', 'columns': {}},
    'v2_indices_daily': {'description': 'Daily market index data', 'columns': {}},
    'v2_commodities_daily': {'description': 'Daily commodity data', 'columns': {}},
    'v2_stocks_weekly_summary': {'description': 'Weekly aggregated stock data', 'columns': {}},
    'v2_crypto_weekly_summary': {'description': 'Weekly aggregated crypto data', 'columns': {}},
}

TRADING_TERMINOLOGY = """
TRADING TERMINOLOGY MAPPINGS:
- "oversold" = RSI < 30 (potential buy opportunity)
- "overbought" = RSI > 70 (potential sell signal)
- "strong trend" = ADX > 25
- "weak trend" or "no trend" = ADX < 20
- "bullish MACD" = MACD > MACD_SIGNAL and MACD > 0
- "bearish MACD" = MACD < MACD_SIGNAL
- "golden cross" = SMA_50 crossing above SMA_200
- "death cross" = SMA_50 crossing below SMA_200
- "breakout" = Close price >= 95% of week_52_high
- "breakdown" = Close price <= 105% of week_52_low
- "gainers" or "top performers" = ORDER BY percent_change DESC
- "losers" or "worst performers" = ORDER BY percent_change ASC
- "high volume" = volume > average * 1.5
- "volatile" = high ATR or wide Bollinger Bands
"""

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class NL2SQLResult:
    """Result of NL to SQL conversion"""
    success: bool
    natural_language: str
    generated_sql: Optional[str]
    interpretation: Optional[str]
    tables_used: List[str]
    execution_time_ms: float
    cached: bool
    error: Optional[str] = None

@dataclass
class QueryResult:
    """Result of SQL query execution"""
    success: bool
    data: List[Dict]
    row_count: int
    columns: List[str]
    execution_time_ms: float
    error: Optional[str] = None

# =============================================================================
# SCHEMA CONTEXT BUILDER
# =============================================================================

def build_schema_context() -> str:
    """Build comprehensive schema context for the LLM."""
    context_parts = [
        f"PROJECT: {PROJECT_ID}",
        f"DATASET: {DATASET_ID}",
        "",
        "AVAILABLE TABLES:",
        ""
    ]

    for table_name, info in TABLE_SCHEMAS.items():
        context_parts.append(f"TABLE: `{PROJECT_ID}.{DATASET_ID}.{table_name}`")
        context_parts.append(f"Description: {info['description']}")

        if info.get('columns'):
            context_parts.append("Columns:")
            for col_name, col_desc in info['columns'].items():
                context_parts.append(f"  - {col_name}: {col_desc}")
        context_parts.append("")

    context_parts.append(TRADING_TERMINOLOGY)

    return "\n".join(context_parts)

# =============================================================================
# QUERY CACHE
# =============================================================================

def get_cache_key(query: str, context: Dict = None) -> str:
    """Generate cache key for query."""
    cache_data = f"{query}:{json.dumps(context or {}, sort_keys=True)}"
    return hashlib.md5(cache_data.encode()).hexdigest()

def get_cached_result(key: str) -> Optional[Dict]:
    """Get cached result if not expired."""
    if key in QUERY_CACHE:
        cached = QUERY_CACHE[key]
        if datetime.now() < cached['expires']:
            return cached['result']
        else:
            del QUERY_CACHE[key]
    return None

def cache_result(key: str, result: Dict):
    """Cache query result."""
    QUERY_CACHE[key] = {
        'result': result,
        'expires': datetime.now() + timedelta(seconds=CACHE_TTL_SECONDS)
    }

# =============================================================================
# SQL VALIDATION
# =============================================================================

def validate_sql(sql: str) -> Tuple[bool, Optional[str]]:
    """
    Validate SQL query for safety.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sql or not sql.strip():
        return False, "Empty SQL query"

    sql_upper = sql.upper().strip()

    # Must be SELECT only
    if not sql_upper.startswith('SELECT'):
        return False, "Only SELECT statements are allowed"

    # Check for dangerous keywords
    dangerous_keywords = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE',
        'CREATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE', '--', ';DROP'
    ]

    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False, f"Dangerous keyword detected: {keyword}"

    # Must reference our dataset
    if PROJECT_ID not in sql and DATASET_ID not in sql:
        return False, "Query must reference aialgotradehits.crypto_trading_data"

    return True, None

# =============================================================================
# NL2SQL ENGINE
# =============================================================================

class BigQueryNL2SQL:
    """
    Natural Language to SQL engine for BigQuery.
    Supports both Vertex AI and Google AI SDK backends.
    """

    def __init__(
        self,
        use_vertex: bool = False,
        api_key: Optional[str] = None,
        model: str = GEMINI_FLASH
    ):
        """
        Initialize NL2SQL engine.

        Args:
            use_vertex: Use Vertex AI (requires GCP auth) or Google AI SDK
            api_key: Gemini API key (for Google AI SDK mode)
            model: Model to use (gemini-2.5-flash or gemini-2.5-pro)
        """
        self.model_name = model
        self.use_vertex = use_vertex
        self.schema_context = build_schema_context()

        # Initialize BigQuery client
        if BQ_AVAILABLE:
            self.bq_client = bigquery.Client(project=PROJECT_ID)
        else:
            self.bq_client = None

        # Initialize LLM client
        if use_vertex and VERTEX_AVAILABLE:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            self.model = GenerativeModel(model)
            self.client = None
        elif GENAI_AVAILABLE:
            self.client = genai.Client(api_key=api_key) if api_key else genai.Client()
            self.model = None
        else:
            raise ImportError("Neither Vertex AI nor google-genai SDK available")

        print(f"BigQuery NL2SQL initialized")
        print(f"  Backend: {'Vertex AI' if use_vertex else 'Google AI SDK'}")
        print(f"  Model: {model}")
        print(f"  Project: {PROJECT_ID}")

    def _build_prompt(self, query: str, context: Dict = None) -> str:
        """Build the prompt for SQL generation."""
        context = context or {}
        asset_type = context.get('asset_type', 'all')
        period = context.get('period', 'daily')

        return f"""You are an expert SQL developer for a trading analytics platform.
Convert the following natural language query to BigQuery SQL.

{self.schema_context}

USER CONTEXT:
- Preferred Asset Type: {asset_type}
- Preferred Period: {period}
- Current Date: {datetime.now().strftime('%Y-%m-%d')}

USER QUERY: "{query}"

SQL GENERATION RULES:
1. Use fully qualified table names: `{PROJECT_ID}.{DATASET_ID}.table_name`
2. Always include ORDER BY clause for deterministic results
3. Always include LIMIT clause (default 50, max 1000)
4. Handle NULL values with IS NOT NULL or COALESCE
5. For latest data per symbol, use: ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn ... WHERE rn = 1
6. Only generate SELECT statements
7. Use appropriate JOINs when combining tables

Generate ONLY the SQL query. No explanations, no markdown formatting.

SQL:"""

    def _extract_sql(self, response: str) -> str:
        """Extract and clean SQL from model response."""
        # Remove markdown code blocks
        sql = re.sub(r'```sql?\n?', '', response)
        sql = re.sub(r'```', '', sql)
        sql = sql.strip()

        # Extract just the SELECT statement
        if 'SELECT' in sql.upper():
            idx = sql.upper().find('SELECT')
            sql = sql[idx:]

            # Remove anything after the query ends
            # Look for common terminators
            for terminator in ['\n\n', '\nExplanation:', '\nNote:']:
                if terminator in sql:
                    sql = sql[:sql.find(terminator)]

        return sql.strip()

    def _extract_tables(self, sql: str) -> List[str]:
        """Extract table names from SQL."""
        pattern = rf'`{PROJECT_ID}\.{DATASET_ID}\.([^`]+)`'
        tables = re.findall(pattern, sql)
        return list(set(tables))

    def generate_sql(
        self,
        query: str,
        context: Dict = None,
        use_cache: bool = True
    ) -> NL2SQLResult:
        """
        Generate SQL from natural language query.

        Args:
            query: Natural language query
            context: Optional context (asset_type, period)
            use_cache: Whether to use query cache

        Returns:
            NL2SQLResult with generated SQL
        """
        start_time = datetime.now()

        # Check cache
        cache_key = get_cache_key(query, context)
        if use_cache:
            cached = get_cached_result(cache_key)
            if cached:
                return NL2SQLResult(
                    success=True,
                    natural_language=query,
                    generated_sql=cached['sql'],
                    interpretation=cached.get('interpretation'),
                    tables_used=cached.get('tables', []),
                    execution_time_ms=0,
                    cached=True
                )

        # Build prompt
        prompt = self._build_prompt(query, context)

        try:
            # Generate SQL using appropriate backend
            if self.use_vertex and self.model:
                response = self.model.generate_content(prompt)
                response_text = response.text
            else:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt],
                    config=types.GenerateContentConfig(temperature=0.1)
                )
                response_text = response.text

            # Extract and validate SQL
            sql = self._extract_sql(response_text)
            is_valid, error = validate_sql(sql)

            if not is_valid:
                return NL2SQLResult(
                    success=False,
                    natural_language=query,
                    generated_sql=sql,
                    interpretation=None,
                    tables_used=[],
                    execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                    cached=False,
                    error=error
                )

            tables = self._extract_tables(sql)

            # Cache successful result
            result_data = {'sql': sql, 'tables': tables}
            cache_result(cache_key, result_data)

            return NL2SQLResult(
                success=True,
                natural_language=query,
                generated_sql=sql,
                interpretation=f"Query for: {query}",
                tables_used=tables,
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                cached=False
            )

        except Exception as e:
            return NL2SQLResult(
                success=False,
                natural_language=query,
                generated_sql=None,
                interpretation=None,
                tables_used=[],
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                cached=False,
                error=str(e)
            )

    def execute_sql(self, sql: str, limit: int = 1000) -> QueryResult:
        """
        Execute SQL query against BigQuery.

        Args:
            sql: SQL query to execute
            limit: Maximum rows to return

        Returns:
            QueryResult with data
        """
        start_time = datetime.now()

        if not self.bq_client:
            return QueryResult(
                success=False,
                data=[],
                row_count=0,
                columns=[],
                execution_time_ms=0,
                error="BigQuery client not available"
            )

        # Validate SQL
        is_valid, error = validate_sql(sql)
        if not is_valid:
            return QueryResult(
                success=False,
                data=[],
                row_count=0,
                columns=[],
                execution_time_ms=0,
                error=error
            )

        try:
            query_job = self.bq_client.query(sql)
            results = query_job.result()

            # Convert to list of dicts
            data = []
            columns = []
            for i, row in enumerate(results):
                if i == 0:
                    columns = list(row.keys())
                if i >= limit:
                    break
                row_dict = dict(row)
                # Convert datetime objects to ISO format
                for key, value in row_dict.items():
                    if hasattr(value, 'isoformat'):
                        row_dict[key] = value.isoformat()
                data.append(row_dict)

            return QueryResult(
                success=True,
                data=data,
                row_count=len(data),
                columns=columns,
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )

        except Exception as e:
            return QueryResult(
                success=False,
                data=[],
                row_count=0,
                columns=[],
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error=str(e)
            )

    def query(
        self,
        natural_language: str,
        context: Dict = None,
        execute: bool = True
    ) -> Dict[str, Any]:
        """
        Full pipeline: Convert NL to SQL and optionally execute.

        Args:
            natural_language: Natural language query
            context: Optional context
            execute: Whether to execute the query

        Returns:
            Dict with SQL, data, and metadata
        """
        # Generate SQL
        nl2sql_result = self.generate_sql(natural_language, context)

        result = {
            'success': nl2sql_result.success,
            'natural_language': natural_language,
            'sql': nl2sql_result.generated_sql,
            'interpretation': nl2sql_result.interpretation,
            'tables_used': nl2sql_result.tables_used,
            'generation_time_ms': nl2sql_result.execution_time_ms,
            'cached': nl2sql_result.cached
        }

        if not nl2sql_result.success:
            result['error'] = nl2sql_result.error
            return result

        # Execute if requested
        if execute and nl2sql_result.generated_sql:
            exec_result = self.execute_sql(nl2sql_result.generated_sql)
            result['data'] = exec_result.data
            result['row_count'] = exec_result.row_count
            result['columns'] = exec_result.columns
            result['execution_time_ms'] = exec_result.execution_time_ms
            result['execution_success'] = exec_result.success
            if not exec_result.success:
                result['execution_error'] = exec_result.error

        return result

    def explain_query(self, query: str) -> str:
        """
        Explain what a natural language query is asking for.
        """
        prompt = f"""Explain in one sentence what this trading data query is asking for:
"{query}"

Be specific about the assets, indicators, and criteria involved."""

        try:
            if self.use_vertex and self.model:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            else:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt],
                    config=types.GenerateContentConfig(temperature=0.3)
                )
                return response.text.strip()
        except Exception as e:
            return f"Query: {query}"


# =============================================================================
# PRESET QUERIES
# =============================================================================

class TradingQueryPresets:
    """Preset trading queries for common use cases."""

    @staticmethod
    def oversold_stocks(limit: int = 20) -> str:
        return f"Find the top {limit} most oversold stocks with RSI below 30"

    @staticmethod
    def overbought_stocks(limit: int = 20) -> str:
        return f"Find the top {limit} most overbought stocks with RSI above 70"

    @staticmethod
    def breakout_candidates(limit: int = 20) -> str:
        return f"Find {limit} stocks breaking their 52-week highs with high volume"

    @staticmethod
    def strong_trends(limit: int = 20) -> str:
        return f"Find {limit} stocks with strong trends (ADX > 25) and bullish MACD"

    @staticmethod
    def top_gainers(asset_type: str = 'stocks', limit: int = 10) -> str:
        return f"Show the top {limit} {asset_type} gainers today"

    @staticmethod
    def top_losers(asset_type: str = 'stocks', limit: int = 10) -> str:
        return f"Show the top {limit} {asset_type} losers today"

    @staticmethod
    def sector_performance(sector: str) -> str:
        return f"Show performance summary for {sector} sector stocks"

    @staticmethod
    def crypto_opportunities() -> str:
        return "Find oversold cryptocurrencies with strong trend potential"

    @staticmethod
    def weekly_summary(asset_type: str = 'stocks') -> str:
        return f"Give me a weekly performance summary for {asset_type}"


# =============================================================================
# MAIN / CLI
# =============================================================================

def main():
    """Interactive CLI for testing NL2SQL."""
    print("=" * 70)
    print("AIAlgoTradeHits BigQuery NL2SQL Engine")
    print("Developer: irfan.qazi@aialgotradehits.com")
    print("=" * 70)

    # Check dependencies
    print("\nChecking dependencies...")
    print(f"  BigQuery: {'Available' if BQ_AVAILABLE else 'Not Available'}")
    print(f"  Vertex AI: {'Available' if VERTEX_AVAILABLE else 'Not Available'}")
    print(f"  Google AI SDK: {'Available' if GENAI_AVAILABLE else 'Not Available'}")

    if not GENAI_AVAILABLE and not VERTEX_AVAILABLE:
        print("\nError: No LLM backend available.")
        print("Install google-genai: pip install google-genai")
        return

    # Check for API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key and not VERTEX_AVAILABLE:
        print("\nWarning: GEMINI_API_KEY not set")
        print("Set it with: export GEMINI_API_KEY='your-api-key'")
        print("Get your key at: https://aistudio.google.com/app/apikey")
        return

    try:
        # Initialize engine
        engine = BigQueryNL2SQL(
            use_vertex=VERTEX_AVAILABLE,
            api_key=api_key
        )
    except Exception as e:
        print(f"\nError initializing NL2SQL engine: {e}")
        return

    # Example queries
    print("\nExample queries:")
    examples = [
        "Find oversold tech stocks",
        "Top 10 crypto gainers today",
        "Stocks with bullish MACD and strong trend",
        "Compare AAPL, MSFT, GOOGL performance",
        "Weekly summary for technology sector"
    ]
    for i, ex in enumerate(examples, 1):
        print(f"  {i}. {ex}")

    print("\nType your query (or 'quit' to exit):\n")

    while True:
        try:
            query = input("Query> ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            if not query:
                continue

            print("\nProcessing...")
            result = engine.query(query)

            if result['success']:
                print(f"\nGenerated SQL:")
                print("-" * 50)
                print(result.get('sql', 'N/A'))
                print("-" * 50)

                if result.get('data'):
                    print(f"\nResults ({result.get('row_count', 0)} rows):")
                    for row in result['data'][:5]:
                        symbol = row.get('symbol', 'N/A')
                        close = row.get('close', 0)
                        change = row.get('percent_change', 0)
                        print(f"  {symbol}: ${close:.2f} ({change:+.2f}%)")
                    if result.get('row_count', 0) > 5:
                        print(f"  ... and {result['row_count'] - 5} more")

                print(f"\nTiming: SQL={result.get('generation_time_ms', 0):.0f}ms, Exec={result.get('execution_time_ms', 0):.0f}ms")
            else:
                print(f"\nError: {result.get('error', 'Unknown error')}")

            print()

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\nGoodbye!")


if __name__ == "__main__":
    main()
