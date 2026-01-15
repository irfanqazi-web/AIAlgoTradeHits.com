"""
Gemini 2.5 Text-to-SQL Agent for AIAlgoTradeHits
Uses Google AI SDK (google-genai) for natural language to SQL conversion

Developer: irfan.qazi@aialgotradehits.com
API Documentation: https://ai.google.dev/api
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

# Google AI SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Install google-genai: pip install google-genai")

# BigQuery for data access
from google.cloud import bigquery

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
GEMINI_MODEL = 'gemini-2.5-flash'  # Can also use gemini-2.5-pro for complex queries

# Trading table metadata for context
TRADING_TABLES = {
    'v2_stocks_daily': {
        'description': 'Daily stock price data with 50+ fields including OHLCV and 29 technical indicators',
        'asset_type': 'stocks',
        'key_columns': ['symbol', 'name', 'sector', 'close', 'percent_change', 'rsi', 'macd', 'adx', 'volume']
    },
    'v2_stocks_weekly_summary': {
        'description': 'Weekly aggregated stock data for position trading',
        'asset_type': 'stocks',
        'key_columns': ['symbol', 'name', 'close', 'weekly_change_percent', 'week_52_high', 'week_52_low']
    },
    'v2_crypto_daily': {
        'description': 'Daily cryptocurrency data with technical indicators',
        'asset_type': 'crypto',
        'key_columns': ['symbol', 'name', 'close', 'percent_change', 'rsi', 'macd', 'volume']
    },
    'v2_forex_daily': {
        'description': 'Daily forex pair data',
        'asset_type': 'forex',
        'key_columns': ['symbol', 'close', 'percent_change', 'rsi', 'atr']
    },
    'v2_etfs_daily': {
        'description': 'Daily ETF data',
        'asset_type': 'etfs',
        'key_columns': ['symbol', 'name', 'close', 'percent_change', 'rsi', 'volume']
    },
    'v2_indices_daily': {
        'description': 'Daily market index data',
        'asset_type': 'indices',
        'key_columns': ['symbol', 'name', 'close', 'percent_change', 'rsi']
    },
    'v2_commodities_daily': {
        'description': 'Daily commodity data',
        'asset_type': 'commodities',
        'key_columns': ['symbol', 'name', 'close', 'percent_change', 'rsi', 'atr']
    }
}

# Trading terminology for query understanding
TRADING_TERMINOLOGY = """
TRADING TERMINOLOGY MAPPINGS:
- "oversold" = RSI < 30 (potential buy signal)
- "overbought" = RSI > 70 (potential sell signal)
- "strong trend" = ADX > 25
- "weak trend" = ADX < 20
- "bullish MACD" = MACD > MACD_SIGNAL and MACD > 0
- "bearish MACD" = MACD < MACD_SIGNAL
- "golden cross" = SMA_50 crosses above SMA_200
- "death cross" = SMA_50 crosses below SMA_200
- "breakout" = Close near or above week_52_high (95%)
- "breakdown" = Close near or below week_52_low (105%)
- "gainers" = percent_change > 0, ORDER BY percent_change DESC
- "losers" = percent_change < 0, ORDER BY percent_change ASC
- "high volume" = volume > average_volume * 1.5
- "momentum" = ROC (Rate of Change) indicator
- "volatility" = ATR (Average True Range) or Bollinger Band width
- "support level" = Recent low prices or lower Bollinger Band
- "resistance level" = Recent high prices or upper Bollinger Band
"""

# Column descriptions for SQL generation
COLUMN_DESCRIPTIONS = """
KEY COLUMNS (available in all tables):
- symbol (STRING): Asset ticker symbol (e.g., AAPL, BTCUSD)
- name (STRING): Full asset name
- datetime (TIMESTAMP): Data timestamp
- open, high, low, close (FLOAT): OHLC prices
- volume (FLOAT): Trading volume
- percent_change (FLOAT): Daily price change percentage
- rsi (FLOAT): Relative Strength Index (0-100), <30 = oversold, >70 = overbought
- macd (FLOAT): MACD line value
- macd_signal (FLOAT): MACD signal line
- macd_histogram (FLOAT): MACD histogram (macd - macd_signal)
- sma_20, sma_50, sma_200 (FLOAT): Simple Moving Averages
- ema_12, ema_26, ema_50 (FLOAT): Exponential Moving Averages
- adx (FLOAT): Average Directional Index (trend strength, >25 = strong)
- atr (FLOAT): Average True Range (volatility)
- bollinger_upper, bollinger_middle, bollinger_lower (FLOAT): Bollinger Bands
- cci (FLOAT): Commodity Channel Index
- stoch_k, stoch_d (FLOAT): Stochastic oscillator
- williams_r (FLOAT): Williams %R
- obv (FLOAT): On-Balance Volume
- week_52_high, week_52_low (FLOAT): 52-week price range
- sector (STRING): Sector classification (stocks only)
- industry (STRING): Industry classification (stocks only)
"""


class GeminiTextToSQLAgent:
    """
    Text-to-SQL Agent using Google AI Gemini 2.5
    Converts natural language trading queries to BigQuery SQL
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the agent.

        Args:
            api_key: Gemini API key. If not provided, uses GEMINI_API_KEY env var.
        """
        if not GENAI_AVAILABLE:
            raise ImportError("google-genai not installed. Run: pip install google-genai")

        # Initialize Gemini client
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            # Uses GEMINI_API_KEY environment variable
            self.client = genai.Client()

        # Initialize BigQuery client
        self.bq_client = bigquery.Client(project=PROJECT_ID)

        # Load schema context
        self.schema_context = self._build_schema_context()

        print(f"Gemini Text-to-SQL Agent initialized")
        print(f"Model: {GEMINI_MODEL}")
        print(f"Project: {PROJECT_ID}")
        print(f"Dataset: {DATASET_ID}")

    def _build_schema_context(self) -> str:
        """Build schema context for the prompt"""
        tables_info = []
        for table_name, info in TRADING_TABLES.items():
            tables_info.append(f"- {table_name}: {info['description']}")
            tables_info.append(f"  Key columns: {', '.join(info['key_columns'])}")

        return "\n".join(tables_info)

    def generate_sql(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate SQL from natural language query.

        Args:
            query: Natural language query
            context: Optional context (asset_type, period, page)

        Returns:
            Dict with sql, interpretation, success status
        """
        context = context or {}
        asset_type = context.get('asset_type', 'all')
        period = context.get('period', 'daily')

        # Build the prompt
        prompt = self._build_prompt(query, asset_type, period)

        try:
            # Generate SQL using Gemini 2.5
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Low temperature for precise SQL
                    system_instruction="""You are an expert SQL developer for a trading analytics platform.
Your task is to convert natural language queries about trading data into precise BigQuery SQL queries.
Always generate valid, safe SELECT queries with proper table references and LIMIT clauses.
Never generate DROP, DELETE, UPDATE, INSERT, or any other data-modifying statements."""
                )
            )

            sql = self._extract_sql(response.text)
            validation = self._validate_sql(sql)

            if validation['valid']:
                return {
                    'success': True,
                    'sql': sql,
                    'interpretation': self._generate_interpretation(query),
                    'tables_used': self._extract_tables(sql),
                    'model': GEMINI_MODEL
                }
            else:
                return {
                    'success': False,
                    'error': validation['error'],
                    'sql': None
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'sql': None
            }

    def _build_prompt(self, query: str, asset_type: str, period: str) -> str:
        """Build the prompt for SQL generation"""

        # Determine default table based on context
        if asset_type != 'all':
            default_table = f"v2_{asset_type}_{period}"
        else:
            default_table = "v2_stocks_daily"

        return f"""Generate a BigQuery SQL query for this trading data request.

DATABASE CONTEXT:
- Project: aialgotradehits
- Dataset: crypto_trading_data

AVAILABLE TABLES:
{self.schema_context}

{COLUMN_DESCRIPTIONS}

{TRADING_TERMINOLOGY}

USER CONTEXT:
- Preferred Asset Type: {asset_type}
- Preferred Period: {period}
- Default Table: {default_table}

USER QUERY: "{query}"

REQUIREMENTS:
1. Use fully qualified table names: `aialgotradehits.crypto_trading_data.table_name`
2. Always include ORDER BY and LIMIT clauses (default LIMIT 50)
3. Handle NULL values with IS NOT NULL or COALESCE
4. For latest data, use ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC)
5. Only generate SELECT statements

Return ONLY the SQL query, no explanations or markdown formatting.

SQL:"""

    def _extract_sql(self, response: str) -> str:
        """Extract SQL from model response"""
        # Remove markdown code blocks
        sql = re.sub(r'```sql?\n?', '', response)
        sql = re.sub(r'```', '', sql)
        # Remove leading/trailing whitespace
        sql = sql.strip()
        # Remove any explanatory text before SELECT
        if 'SELECT' in sql.upper():
            idx = sql.upper().find('SELECT')
            sql = sql[idx:]
        return sql

    def _validate_sql(self, sql: str) -> Dict[str, Any]:
        """Validate SQL for safety and correctness"""
        if not sql:
            return {'valid': False, 'error': 'Empty SQL generated'}

        sql_upper = sql.upper()

        # Check for dangerous keywords
        dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'CREATE', 'GRANT']
        for keyword in dangerous:
            if keyword in sql_upper:
                return {'valid': False, 'error': f'Dangerous keyword detected: {keyword}'}

        # Ensure SELECT only
        if not sql_upper.strip().startswith('SELECT'):
            return {'valid': False, 'error': 'Only SELECT statements allowed'}

        # Validate table reference
        if 'aialgotradehits.crypto_trading_data' not in sql:
            return {'valid': False, 'error': 'Invalid table reference - must use aialgotradehits.crypto_trading_data'}

        return {'valid': True}

    def _extract_tables(self, sql: str) -> List[str]:
        """Extract table names from SQL"""
        pattern = r'`aialgotradehits\.crypto_trading_data\.([^`]+)`'
        return re.findall(pattern, sql)

    def _generate_interpretation(self, query: str) -> str:
        """Generate human-readable interpretation"""
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[f"In one sentence, explain what this trading query is asking for: \"{query}\""],
                config=types.GenerateContentConfig(temperature=0.3)
            )
            return response.text.strip()
        except Exception:
            return f"Processing query: {query}"

    def execute_query(self, sql: str, limit: int = 100) -> Dict[str, Any]:
        """
        Execute SQL query against BigQuery.

        Args:
            sql: SQL query to execute
            limit: Maximum results to return

        Returns:
            Dict with success status and data
        """
        try:
            query_job = self.bq_client.query(sql)
            results = list(query_job.result())

            data = []
            for row in results[:limit]:
                row_dict = dict(row)
                # Convert datetime objects to ISO format
                for key, value in row_dict.items():
                    if hasattr(value, 'isoformat'):
                        row_dict[key] = value.isoformat()
                data.append(row_dict)

            return {
                'success': True,
                'data': data,
                'count': len(data),
                'total_rows': len(results)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

    def query(self, natural_language: str, context: Dict = None, execute: bool = True) -> Dict[str, Any]:
        """
        Full pipeline: parse query, generate SQL, and optionally execute.

        Args:
            natural_language: Natural language query
            context: Optional context
            execute: Whether to execute the query

        Returns:
            Complete result with SQL and data
        """
        # Generate SQL
        result = self.generate_sql(natural_language, context)

        if not result['success']:
            return result

        # Execute if requested
        if execute and result.get('sql'):
            execution = self.execute_query(result['sql'])
            result['data'] = execution.get('data', [])
            result['count'] = execution.get('count', 0)
            result['total_rows'] = execution.get('total_rows', 0)
            result['execution_success'] = execution.get('success', False)
            if not execution['success']:
                result['execution_error'] = execution.get('error')

        return result

    def scan_market(self, scan_type: str, asset_type: str = 'stocks', limit: int = 20) -> Dict[str, Any]:
        """
        Preset market scans.

        Args:
            scan_type: Type of scan (gainers, losers, oversold, overbought, breakouts, strong_trends)
            asset_type: Asset type to scan
            limit: Number of results

        Returns:
            Scan results
        """
        scan_queries = {
            'gainers': f"Top {limit} {asset_type} gainers today",
            'losers': f"Top {limit} {asset_type} losers today",
            'oversold': f"Find oversold {asset_type} with RSI below 30",
            'overbought': f"Find overbought {asset_type} with RSI above 70",
            'breakouts': f"{asset_type} breaking 52-week highs with high volume",
            'strong_trends': f"{asset_type} with ADX above 25 and bullish MACD",
            'high_volume': f"High volume {asset_type} today"
        }

        query = scan_queries.get(scan_type, scan_queries['gainers'])
        return self.query(query, context={'asset_type': asset_type})


# Interactive CLI for testing
def main():
    """Interactive CLI for testing the Text-to-SQL agent"""

    print("=" * 60)
    print("AIAlgoTradeHits Gemini Text-to-SQL Agent")
    print("=" * 60)

    # Check for API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("\nWARNING: GEMINI_API_KEY environment variable not set")
        print("Set it with: export GEMINI_API_KEY='your-api-key'")
        print("Get your API key from: https://aistudio.google.com/app/apikey")
        return

    try:
        agent = GeminiTextToSQLAgent()
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        return

    # Example queries
    example_queries = [
        "Show me top 10 tech stock gainers",
        "Find oversold crypto with RSI below 30",
        "Stocks with bullish MACD and strong trend",
        "High volume stocks breaking 52-week highs",
        "Compare AAPL, MSFT, and GOOGL performance"
    ]

    print("\nExample queries:")
    for i, q in enumerate(example_queries, 1):
        print(f"  {i}. {q}")

    print("\nType your query (or 'quit' to exit):\n")

    while True:
        try:
            query = input("Query> ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            if not query:
                continue

            print("\nProcessing...")
            result = agent.query(query)

            if result['success']:
                print(f"\nSQL Generated:")
                print("-" * 40)
                print(result.get('sql', 'N/A'))
                print("-" * 40)

                if result.get('data'):
                    print(f"\nResults ({result.get('count', 0)} rows):")
                    for row in result['data'][:5]:
                        print(f"  {row.get('symbol', 'N/A')}: ${row.get('close', 0):.2f} ({row.get('percent_change', 0):.2f}%)")
                    if result.get('count', 0) > 5:
                        print(f"  ... and {result['count'] - 5} more")
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
