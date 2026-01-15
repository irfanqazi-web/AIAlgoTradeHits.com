"""
NL2SQL Query Engine for AIAlgoTradeHits Trading Platform
Version: 1.0
Integrates with Gemini 2.5 Pro for natural language to SQL conversion
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import bigquery

# ============================================
# CONFIGURATION
# ============================================

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aialgotradehits")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
DATASET = "crypto_trading_data"

class QueryIntent(Enum):
    LOOKUP = "lookup"
    FILTER = "filter"
    CYCLE = "cycle"
    COMPARE = "compare"
    TIMERANGE = "timerange"
    MULTI = "multi"
    PATTERN = "pattern"
    GROWTH = "growth"

@dataclass
class ParsedQuery:
    intent: QueryIntent
    entities: Dict
    tables: List[str]
    sql: str
    interpretation: str

# ============================================
# INDICATOR KEYWORD MAPPINGS
# ============================================

INDICATOR_KEYWORDS = {
    # Basic RSI Conditions
    'oversold': ('rsi_14', '<', 30),
    'overbought': ('rsi_14', '>', 70),
    'neutral rsi': ('rsi_14', 'BETWEEN', (40, 60)),
    
    # MACD Conditions
    'bullish': ('macd_histogram', '>', 0),
    'bearish': ('macd_histogram', '<', 0),
    'macd crossover': ('macd', '>', 'macd_signal'),
    
    # Trend Strength
    'strong trend': ('adx', '>', 25),
    'weak trend': ('adx', '<', 20),
    'very strong trend': ('adx', '>', 50),
    
    # Volume Conditions
    'high volume': ('volume', '>', 'volume_sma_20'),
    'low volume': ('volume', '<', 'volume_sma_20'),
    
    # Volatility
    'volatile': ('atr', '>', 'atr_avg'),
    'low volatility': ('atr', '<', 'atr_avg'),
    
    # Momentum
    'momentum': ('roc', '>', 5),
    'negative momentum': ('roc', '<', -5),
    
    # Bollinger Bands
    'bollinger breakout': ('close', '>', 'bb_upper'),
    'bollinger breakdown': ('close', '<', 'bb_lower'),
    'bollinger squeeze': ('bb_width', '<', 'bb_width_avg'),
    
    # Moving Averages
    'above 200 ma': ('close', '>', 'sma_200'),
    'below 200 ma': ('close', '<', 'sma_200'),
    'above 50 ma': ('close', '>', 'sma_50'),
    'below 50 ma': ('close', '<', 'sma_50'),
}

# Rise/Fall Cycle Keywords
CYCLE_KEYWORDS = {
    'rise cycle': "sma_9 > sma_21",
    'fall cycle': "sma_9 < sma_21",
    'rise cycle start': "sma_9 > sma_21 AND LAG(sma_9) OVER w <= LAG(sma_21) OVER w",
    'fall cycle start': "sma_9 < sma_21 AND LAG(sma_9) OVER w >= LAG(sma_21) OVER w",
    'golden cross': "sma_50 > sma_200 AND LAG(sma_50) OVER w <= LAG(sma_200) OVER w",
    'death cross': "sma_50 < sma_200 AND LAG(sma_50) OVER w >= LAG(sma_200) OVER w",
    'uptrend': "close > sma_50 AND sma_50 > sma_200",
    'downtrend': "close < sma_50 AND sma_50 < sma_200",
}

# Pattern Keywords
PATTERN_KEYWORDS = {
    'head and shoulders': "pattern_head_shoulders = TRUE",
    'inverse head and shoulders': "pattern_inverse_head_shoulders = TRUE",
    'double top': "pattern_double_top = TRUE",
    'double bottom': "pattern_double_bottom = TRUE",
    'ascending triangle': "pattern_ascending_triangle = TRUE",
    'descending triangle': "pattern_descending_triangle = TRUE",
    'symmetrical triangle': "pattern_symmetrical_triangle = TRUE",
    'triangle': "(pattern_ascending_triangle OR pattern_descending_triangle OR pattern_symmetrical_triangle)",
    'bull flag': "pattern_bull_flag = TRUE",
    'bear flag': "pattern_bear_flag = TRUE",
    'flag': "(pattern_bull_flag OR pattern_bear_flag)",
    'rising wedge': "pattern_rising_wedge = TRUE",
    'falling wedge': "pattern_falling_wedge = TRUE",
    'wedge': "(pattern_rising_wedge OR pattern_falling_wedge)",
    'bullish pattern': "(pattern_double_bottom OR pattern_inverse_head_shoulders OR pattern_ascending_triangle OR pattern_falling_wedge)",
    'bearish pattern': "(pattern_double_top OR pattern_head_shoulders OR pattern_descending_triangle OR pattern_rising_wedge)",
}

# Symbol Mappings
CRYPTO_SYMBOLS = {
    'bitcoin': ['XXBTZUSD', 'BTCUSD', 'BTC'],
    'btc': ['XXBTZUSD', 'BTCUSD'],
    'ethereum': ['XETHZUSD', 'ETHUSD', 'ETH'],
    'eth': ['XETHZUSD', 'ETHUSD'],
    'solana': ['SOLUSD', 'SOL'],
    'sol': ['SOLUSD'],
    'ripple': ['XRPUSD', 'XRP'],
    'xrp': ['XRPUSD'],
    'cardano': ['ADAUSD', 'ADA'],
    'dogecoin': ['DOGEUSD', 'DOGE'],
}

STOCK_SYMBOLS = {
    'apple': 'AAPL',
    'tesla': 'TSLA',
    'nvidia': 'NVDA',
    'microsoft': 'MSFT',
    'amazon': 'AMZN',
    'google': 'GOOGL',
    'meta': 'META',
    'netflix': 'NFLX',
}

# ============================================
# TABLE SELECTION
# ============================================

TABLES = {
    'crypto_daily': f"`{PROJECT_ID}.{DATASET}.crypto_analysis`",
    'crypto_hourly': f"`{PROJECT_ID}.{DATASET}.crypto_hourly_data`",
    'crypto_5min': f"`{PROJECT_ID}.{DATASET}.crypto_5min_top10_gainers`",
    'stock_daily': f"`{PROJECT_ID}.{DATASET}.stock_analysis`",
    'stock_hourly': f"`{PROJECT_ID}.{DATASET}.stock_hourly_data`",
    'stock_5min': f"`{PROJECT_ID}.{DATASET}.stock_5min_top10_gainers`",
}

# ============================================
# NL2SQL QUERY ENGINE CLASS
# ============================================

class NL2SQLEngine:
    """Natural Language to SQL Query Engine with Gemini 2.5 Pro"""
    
    def __init__(self, use_gemini: bool = True):
        self.use_gemini = use_gemini
        self.bq_client = bigquery.Client(project=PROJECT_ID)
        
        if use_gemini:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            self.gemini_model = GenerativeModel("gemini-2.5-pro")
    
    def parse_query(self, query_text: str) -> ParsedQuery:
        """Parse natural language query and generate SQL"""
        query_lower = query_text.lower().strip()
        
        # Classify intent
        intent = self._classify_intent(query_lower)
        
        # Extract entities
        entities = self._extract_entities(query_lower)
        
        # Select appropriate tables
        tables = self._select_tables(entities)
        
        # Generate SQL
        if self.use_gemini:
            sql = self._generate_sql_gemini(query_text, entities, tables)
        else:
            sql = self._generate_sql_rules(query_lower, entities, tables)
        
        # Generate interpretation
        interpretation = self._generate_interpretation(entities, tables)
        
        return ParsedQuery(
            intent=intent,
            entities=entities,
            tables=tables,
            sql=sql,
            interpretation=interpretation
        )
    
    def execute_query(self, sql: str) -> List[Dict]:
        """Execute SQL query against BigQuery"""
        try:
            query_job = self.bq_client.query(sql)
            results = query_job.result()
            return [dict(row) for row in results]
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    def _classify_intent(self, query: str) -> QueryIntent:
        """Classify the intent of the query"""
        # Pattern detection
        if any(kw in query for kw in PATTERN_KEYWORDS.keys()):
            return QueryIntent.PATTERN
        
        # Cycle detection
        if any(kw in query for kw in CYCLE_KEYWORDS.keys()):
            return QueryIntent.CYCLE
        
        # Growth/Opportunity
        if any(kw in query for kw in ['growth', 'momentum', 'opportunity', 'accumulation']):
            return QueryIntent.GROWTH
        
        # Comparison
        if any(kw in query for kw in ['top', 'best', 'highest', 'lowest', 'vs', 'compare']):
            return QueryIntent.COMPARE
        
        # Time-based
        if any(kw in query for kw in ['last', 'today', 'yesterday', 'hourly', '5-minute', 'week']):
            return QueryIntent.TIMERANGE
        
        # Multi-condition
        if ' and ' in query or ' with ' in query:
            return QueryIntent.MULTI
        
        # Filter
        if any(kw in query for kw in INDICATOR_KEYWORDS.keys()):
            return QueryIntent.FILTER
        
        # Default to lookup
        return QueryIntent.LOOKUP
    
    def _extract_entities(self, query: str) -> Dict:
        """Extract entities from the query"""
        entities = {
            'market': None,
            'timeframe': 'daily',
            'symbols': [],
            'conditions': [],
            'patterns': [],
            'cycles': [],
            'limit': 20,
            'sort': None,
        }
        
        # Detect market type
        if any(kw in query for kw in ['crypto', 'bitcoin', 'btc', 'eth', 'ethereum', 'sol']):
            entities['market'] = 'crypto'
        elif any(kw in query for kw in ['stock', 'stocks', 'aapl', 'tsla', 'nvda', 'msft']):
            entities['market'] = 'stock'
        
        # Detect timeframe
        if 'hourly' in query or 'hour' in query:
            entities['timeframe'] = 'hourly'
        elif '5-minute' in query or '5min' in query or '5 minute' in query:
            entities['timeframe'] = '5min'
        
        # Extract symbols
        for name, symbols in CRYPTO_SYMBOLS.items():
            if name in query:
                entities['symbols'].extend(symbols[:1])  # Use first symbol
                entities['market'] = 'crypto'
        
        for name, symbol in STOCK_SYMBOLS.items():
            if name in query:
                entities['symbols'].append(symbol)
                entities['market'] = 'stock'
        
        # Extract indicator conditions
        for keyword, condition in INDICATOR_KEYWORDS.items():
            if keyword in query:
                entities['conditions'].append({
                    'keyword': keyword,
                    'field': condition[0],
                    'operator': condition[1],
                    'value': condition[2]
                })
        
        # Extract pattern conditions
        for keyword, sql_condition in PATTERN_KEYWORDS.items():
            if keyword in query:
                entities['patterns'].append({
                    'keyword': keyword,
                    'condition': sql_condition
                })
        
        # Extract cycle conditions
        for keyword, sql_condition in CYCLE_KEYWORDS.items():
            if keyword in query:
                entities['cycles'].append({
                    'keyword': keyword,
                    'condition': sql_condition
                })
        
        # Extract limit
        limit_match = re.search(r'top\s+(\d+)', query)
        if limit_match:
            entities['limit'] = int(limit_match.group(1))
        
        return entities
    
    def _select_tables(self, entities: Dict) -> List[str]:
        """Select appropriate BigQuery tables"""
        market = entities.get('market', 'crypto')
        timeframe = entities.get('timeframe', 'daily')
        
        if market == 'stock':
            if timeframe == 'hourly':
                return [TABLES['stock_hourly']]
            elif timeframe == '5min':
                return [TABLES['stock_5min']]
            else:
                return [TABLES['stock_daily']]
        else:  # crypto
            if timeframe == 'hourly':
                return [TABLES['crypto_hourly']]
            elif timeframe == '5min':
                return [TABLES['crypto_5min']]
            else:
                return [TABLES['crypto_daily']]
    
    def _generate_sql_gemini(self, query: str, entities: Dict, tables: List[str]) -> str:
        """Generate SQL using Gemini 2.5 Pro"""
        prompt = f"""You are an expert SQL generator for a trading analytics platform.
Convert this natural language query to BigQuery SQL.

AVAILABLE TABLES:
{', '.join(tables)}

STANDARD FIELDS:
- pair/symbol, date/datetime, open, high, low, close, volume
- rsi_14, macd, macd_signal, macd_histogram
- sma_9, sma_21, sma_50, sma_200, ema_12, ema_26
- adx, bb_upper, bb_middle, bb_lower, atr, roc, obv, vwap
- Pattern flags: pattern_head_shoulders, pattern_double_top, pattern_double_bottom,
  pattern_ascending_triangle, pattern_descending_triangle, pattern_bull_flag, etc.

RISE/FALL CYCLE DETECTION:
- Rise cycle: sma_9 > sma_21
- Rise cycle START: sma_9 > sma_21 AND LAG(sma_9) OVER w <= LAG(sma_21) OVER w
- Golden cross: sma_50 crosses above sma_200

INDICATOR CONDITIONS:
- Oversold: rsi_14 < 30
- Overbought: rsi_14 > 70
- Bullish: macd_histogram > 0
- Strong trend: adx > 25

USER QUERY: {query}

DETECTED ENTITIES: {json.dumps(entities, indent=2)}

Generate a valid BigQuery SQL query. Return ONLY the SQL, no explanation.
Use window functions with WINDOW w AS (PARTITION BY pair/symbol ORDER BY date/datetime) for cycle detection.
Default LIMIT to {entities.get('limit', 20)}.
"""
        
        response = self.gemini_model.generate_content(prompt)
        sql = response.text.strip()
        
        # Clean up SQL (remove markdown code blocks if present)
        sql = re.sub(r'^```sql\s*', '', sql)
        sql = re.sub(r'\s*```$', '', sql)
        
        return sql
    
    def _generate_sql_rules(self, query: str, entities: Dict, tables: List[str]) -> str:
        """Generate SQL using rule-based approach (fallback)"""
        table = tables[0]
        symbol_field = 'symbol' if 'stock' in table else 'pair'
        date_field = 'datetime' if 'hourly' in table or '5min' in table else 'date'
        
        # Build SELECT clause
        select_fields = [
            symbol_field,
            date_field,
            'close',
            'volume',
            'rsi_14',
            'macd_histogram',
            'adx',
            'sma_9',
            'sma_21'
        ]
        
        # Build WHERE clause
        where_conditions = []
        
        # Add date filter
        if entities['timeframe'] == 'hourly':
            where_conditions.append(f"{date_field} >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)")
        elif entities['timeframe'] == '5min':
            where_conditions.append(f"{date_field} >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)")
        else:
            where_conditions.append(f"DATE({date_field}) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)")
        
        # Add symbol filter
        if entities['symbols']:
            symbols_str = ', '.join([f"'{s}'" for s in entities['symbols']])
            where_conditions.append(f"{symbol_field} IN ({symbols_str})")
        
        # Add indicator conditions
        for cond in entities['conditions']:
            if isinstance(cond['value'], tuple):
                where_conditions.append(
                    f"{cond['field']} BETWEEN {cond['value'][0]} AND {cond['value'][1]}"
                )
            elif isinstance(cond['value'], str):
                where_conditions.append(f"{cond['field']} {cond['operator']} {cond['value']}")
            else:
                where_conditions.append(f"{cond['field']} {cond['operator']} {cond['value']}")
        
        # Add pattern conditions
        for pattern in entities['patterns']:
            where_conditions.append(pattern['condition'])
        
        # Add cycle conditions (requires window function)
        window_clause = ""
        if entities['cycles']:
            window_clause = f"\nWINDOW w AS (PARTITION BY {symbol_field} ORDER BY {date_field})"
            for cycle in entities['cycles']:
                where_conditions.append(cycle['condition'])
        
        # Build final SQL
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        sql = f"""SELECT {', '.join(select_fields)}
FROM {table}
WHERE {where_clause}{window_clause}
ORDER BY {date_field} DESC
LIMIT {entities['limit']};"""
        
        return sql
    
    def _generate_interpretation(self, entities: Dict, tables: List[str]) -> str:
        """Generate human-readable interpretation of the query"""
        parts = []
        
        market = entities.get('market', 'crypto')
        parts.append(f"Searching {market} data")
        
        if entities.get('symbols'):
            parts.append(f"for symbols: {', '.join(entities['symbols'])}")
        
        if entities.get('conditions'):
            cond_names = [c['keyword'] for c in entities['conditions']]
            parts.append(f"with conditions: {', '.join(cond_names)}")
        
        if entities.get('patterns'):
            pattern_names = [p['keyword'] for p in entities['patterns']]
            parts.append(f"matching patterns: {', '.join(pattern_names)}")
        
        if entities.get('cycles'):
            cycle_names = [c['keyword'] for c in entities['cycles']]
            parts.append(f"in {', '.join(cycle_names)}")
        
        parts.append(f"using {entities.get('timeframe', 'daily')} data")
        parts.append(f"(limit {entities.get('limit', 20)})")
        
        return " ".join(parts)


# ============================================
# API HANDLER FUNCTIONS
# ============================================

def handle_nlp_query(request_body: Dict) -> Dict:
    """Handle NLP query API request"""
    query_text = request_body.get('query', '')
    use_gemini = request_body.get('use_gemini', True)
    execute = request_body.get('execute', True)
    
    if not query_text:
        return {'error': 'Query text is required'}
    
    engine = NL2SQLEngine(use_gemini=use_gemini)
    
    try:
        parsed = engine.parse_query(query_text)
        
        response = {
            'query': query_text,
            'intent': parsed.intent.value,
            'entities': parsed.entities,
            'sql': parsed.sql,
            'interpretation': parsed.interpretation,
            'tables': parsed.tables,
        }
        
        if execute:
            results = engine.execute_query(parsed.sql)
            response['results'] = results
            response['count'] = len(results)
        
        return response
        
    except Exception as e:
        return {'error': str(e)}


def get_search_suggestions() -> List[str]:
    """Return list of search suggestions"""
    return [
        "Oversold cryptos",
        "Bitcoin hourly last 24 hours",
        "Top 10 stock gainers",
        "Stocks with bullish MACD",
        "Cryptos starting a rise cycle",
        "High volume cryptos",
        "Stocks with ascending triangle",
        "Golden cross stocks",
        "Strong growth momentum",
        "Double bottom patterns",
        "Overbought with high volume",
        "Death cross warning",
        "Falling wedge breakout candidates",
        "RSI below 30 and above 200 MA",
    ]


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    # Example queries
    test_queries = [
        "Show me oversold cryptos with high volume",
        "Bitcoin hourly last 24 hours",
        "Top 10 stocks starting a rise cycle",
        "Cryptos with ascending triangle pattern",
        "Stocks with RSI below 40 and above 200 MA",
        "Golden cross stocks this week",
    ]
    
    engine = NL2SQLEngine(use_gemini=False)  # Use rules-based for testing
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        parsed = engine.parse_query(query)
        print(f"Intent: {parsed.intent.value}")
        print(f"Interpretation: {parsed.interpretation}")
        print(f"SQL:\n{parsed.sql}")
