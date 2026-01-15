"""
NLP SQL Query Engine for Trading Data
Converts natural language queries to SQL across 6 trading tables
"""

import re
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class NLPQueryEngine:
    """Natural language to SQL converter for trading data"""

    def __init__(self, project_id='aialgotradehits', dataset_id='crypto_trading_data'):
        self.project_id = project_id
        self.dataset_id = dataset_id

        # Symbol mappings
        self.crypto_symbols = {
            'bitcoin': ['XXBTZUSD', 'BTCUSD', 'XBTUSD'],
            'btc': ['XXBTZUSD', 'BTCUSD', 'XBTUSD'],
            'ethereum': ['XETHZUSD', 'ETHUSD'],
            'eth': ['XETHZUSD', 'ETHUSD'],
            'solana': ['SOLUSD'],
            'sol': ['SOLUSD'],
            'cardano': ['ADAUSD'],
            'ada': ['ADAUSD'],
            'dogecoin': ['XDGUSD', 'DOGEUSD'],
            'doge': ['XDGUSD', 'DOGEUSD'],
            'shiba': ['SHIBUSD', 'SHIBUSDT'],
            'shib': ['SHIBUSD', 'SHIBUSDT'],
            'polkadot': ['DOTUSD'],
            'dot': ['DOTUSD'],
            'ripple': ['XRPUSD'],
            'xrp': ['XRPUSD'],
            'uniswap': ['UNIUSD'],
            'uni': ['UNIUSD'],
        }

        self.stock_symbols = {
            'apple': 'AAPL',
            'tesla': 'TSLA',
            'microsoft': 'MSFT',
            'amazon': 'AMZN',
            'google': 'GOOGL',
            'meta': 'META',
            'facebook': 'META',
            'nvidia': 'NVDA',
            'netflix': 'NFLX',
        }

        # Indicator patterns
        self.indicator_patterns = {
            r'oversold': ('rsi', '<', 30),
            r'overbought': ('rsi', '>', 70),
            r'bullish\s*macd': ('macd', '>', 0),
            r'bearish\s*macd': ('macd', '<', 0),
            r'strong\s*trend': ('adx', '>', 25),
            r'weak\s*trend': ('adx', '<', 20),
            r'high\s*volume': ('volume', '>', 'subquery:AVG'),
            r'low\s*volume': ('volume', '<', 'subquery:AVG'),
            r'volatile|volatility': ('atr', '>', 'subquery:AVG'),
            r'momentum|rising': ('roc', '>', 5),
            r'falling|declining': ('roc', '<', -5),
            r'above\s*200\s*ma': ('close', '>', 'sma_200'),
            r'below\s*200\s*ma': ('close', '<', 'sma_200'),
            r'above\s*50\s*ma': ('close', '>', '{ma_50}'),  # Will be replaced dynamically
            r'below\s*50\s*ma': ('close', '<', '{ma_50}'),  # Will be replaced dynamically
            r'above\s*20\s*ma': ('close', '>', 'sma_20'),
            r'below\s*20\s*ma': ('close', '<', 'sma_20'),
            r'bollinger\s*breakout': ('close', '>', 'bb_upper'),
            r'bollinger\s*breakdown': ('close', '<', 'bb_lower'),
        }

        # Timeframe keywords - updated to new naming convention
        self.timeframe_keywords = {
            'hourly': 'hourly',
            'hour': 'hourly',
            '1h': 'hourly',
            'daily': 'daily',
            'day': 'daily',
            '1d': 'daily',
            '5-minute': '5min',
            '5min': '5min',
            '5m': '5min',
            '5 minute': '5min',
        }

    def parse_query(self, query_text):
        """
        Parse natural language query and generate SQL
        Returns: (sql, table_name, interpretation)
        """
        query_lower = query_text.lower().strip()

        # Extract entities
        market_type = self._detect_market(query_lower)
        timeframe = self._detect_timeframe(query_lower)
        symbol = self._detect_symbol(query_lower, market_type)
        conditions = self._detect_conditions(query_lower)
        comparison = self._detect_comparison(query_lower)
        time_range = self._detect_time_range(query_lower)
        limit = self._detect_limit(query_lower)

        # Determine table
        table_name = self._select_table(market_type, timeframe)

        # Build SQL
        sql = self._generate_sql(
            table_name=table_name,
            market_type=market_type,
            symbol=symbol,
            conditions=conditions,
            comparison=comparison,
            time_range=time_range,
            limit=limit
        )

        # Generate interpretation
        interpretation = self._generate_interpretation(
            market_type, symbol, conditions, comparison, time_range, limit
        )

        return sql, table_name, interpretation

    def _detect_market(self, query):
        """Detect if query is about crypto or stocks"""
        crypto_keywords = ['crypto', 'bitcoin', 'btc', 'ethereum', 'eth', 'coin', 'altcoin', 'solana', 'doge']
        stock_keywords = ['stock', 'shares', 'equity', 'nasdaq', 'sp500', 's&p']

        # First check if query contains a known stock company name
        for company_name in self.stock_symbols.keys():
            if company_name in query:
                return 'stock'

        # Check for explicit stock symbols (all caps 2-4 letters)
        stock_pattern = r'\b[A-Z]{2,5}\b'
        if re.search(stock_pattern, query):
            # Common stock symbols
            known_stocks = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'SPY', 'QQQ', 'NFLX']
            for stock in known_stocks:
                if stock.lower() in query:
                    return 'stock'

        # Check for crypto names
        for crypto_name in self.crypto_symbols.keys():
            if crypto_name in query:
                return 'crypto'

        for keyword in crypto_keywords:
            if keyword in query:
                return 'crypto'

        for keyword in stock_keywords:
            if keyword in query:
                return 'stock'

        # Default to stock (changed from crypto)
        return 'stock'

    def _detect_timeframe(self, query):
        """Detect timeframe from query"""
        for keyword, table_suffix in self.timeframe_keywords.items():
            if keyword in query:
                return table_suffix
        return 'daily'  # default to daily

    def _detect_symbol(self, query, market_type):
        """Detect specific symbol/pair"""
        if market_type == 'crypto':
            # Use word boundaries to avoid false matches (e.g., "oversold" matching "sol")
            for name, symbols in self.crypto_symbols.items():
                pattern = r'\b' + re.escape(name) + r'\b'
                if re.search(pattern, query):
                    return symbols
        else:
            for name, symbol in self.stock_symbols.items():
                if name in query:
                    return [symbol]

            # Check for explicit stock symbols
            stock_pattern = r'\b([A-Z]{2,5})\b'
            matches = re.findall(stock_pattern, query.upper())
            if matches:
                return matches

        return None

    def _detect_conditions(self, query):
        """Detect indicator-based conditions"""
        conditions = []

        for pattern, (field, operator, value) in self.indicator_patterns.items():
            if re.search(pattern, query):
                conditions.append((field, operator, value))

        # Custom RSI values
        rsi_match = re.search(r'rsi\s*[<>]=?\s*(\d+)', query)
        if rsi_match:
            op = '<' if '<' in query else '>'
            val = int(rsi_match.group(1))
            conditions.append(('rsi', op, val))

        # Custom ADX values
        adx_match = re.search(r'adx\s*[<>]=?\s*(\d+)', query)
        if adx_match:
            op = '<' if '<' in query else '>'
            val = int(adx_match.group(1))
            conditions.append(('adx', op, val))

        return conditions

    def _detect_comparison(self, query):
        """Detect if query asks for top/bottom ranking"""
        if any(word in query for word in ['top', 'best', 'highest', 'biggest', 'most']):
            # Determine what to sort by
            if 'gainer' in query:
                return ('roc', 'DESC')
            elif 'loser' in query:
                return ('roc', 'ASC')
            elif 'volume' in query:
                return ('volume', 'DESC')
            elif 'volatile' in query:
                return ('atr', 'DESC')
            else:
                return ('roc', 'DESC')  # default to gainers

        if any(word in query for word in ['worst', 'lowest', 'smallest', 'bottom']):
            if 'volume' in query:
                return ('volume', 'ASC')
            else:
                return ('roc', 'ASC')  # losers

        return None

    def _detect_time_range(self, query):
        """Detect time range filter"""
        # Last N hours
        hours_match = re.search(r'last\s*(\d+)\s*hours?', query)
        if hours_match:
            return ('hours', int(hours_match.group(1)))

        # Last N days
        days_match = re.search(r'last\s*(\d+)\s*days?', query)
        if days_match:
            return ('days', int(days_match.group(1)))

        # Today
        if 'today' in query:
            return ('days', 0)  # current day

        # This week
        if 'this week' in query or 'week' in query:
            return ('days', 7)

        return None

    def _detect_limit(self, query):
        """Detect result limit"""
        # Extract number before 'top', 'best', etc.
        limit_match = re.search(r'(top|best|bottom)\s*(\d+)', query)
        if limit_match:
            return int(limit_match.group(2))

        # Extract standalone numbers
        num_match = re.search(r'\b(\d+)\s*(results?|items?|stocks?|cryptos?)?', query)
        if num_match:
            num = int(num_match.group(1))
            if num <= 100:  # reasonable limit
                return num

        return 20  # default

    def _select_table(self, market_type, timeframe):
        """Select appropriate table"""
        market = 'crypto' if market_type == 'crypto' else 'stock'
        table_name = f"{timeframe}_{market}"

        # Full table name with project and dataset
        return f"`{self.project_id}.{self.dataset_id}.{table_name}`"

    def _generate_sql(self, table_name, market_type, symbol, conditions, comparison, time_range, limit):
        """Generate SQL query"""
        id_field = 'pair' if market_type == 'crypto' else 'symbol'

        # SELECT clause - use fields that exist across tables
        # Crypto uses ma_50, Stock uses sma_50
        ma_50_field = 'ma_50' if market_type == 'crypto' else 'sma_50'

        select_fields = [
            id_field,
            'datetime',
            'open',
            'high',
            'low',
            'close',
            'volume',
            'rsi',
            'macd',
            'adx',
            'roc',
            'sma_20',
            ma_50_field
        ]

        # Only include sma_200 for daily and hourly (not 5-min stock)
        if '5min_stock' not in table_name:
            select_fields.append('sma_200')

        # Use subquery to get latest record per symbol first
        # This ensures we only look at the most recent data for each symbol
        use_latest_only = not symbol  # If no specific symbol, get latest for all symbols

        if use_latest_only:
            # Create a CTE (Common Table Expression) to get latest record per symbol
            select_clause = f"""WITH latest_records AS (
  SELECT {', '.join(select_fields)},
         ROW_NUMBER() OVER (PARTITION BY {id_field} ORDER BY datetime DESC) as rn
  FROM {table_name}
)
SELECT {', '.join(select_fields)}
FROM latest_records
WHERE rn = 1"""
            from_clause = ""  # Already included in CTE
        else:
            select_clause = f"SELECT {', '.join(select_fields)}"
            from_clause = f"FROM {table_name}"

        # WHERE clause
        where_conditions = []

        # Symbol filter
        if symbol:
            if len(symbol) == 1:
                where_conditions.append(f"{id_field} = '{symbol[0]}'")
            else:
                symbol_list = "', '".join(symbol)
                where_conditions.append(f"{id_field} IN ('{symbol_list}')")

        # Time range filter
        if time_range:
            range_type, range_value = time_range
            if range_type == 'hours':
                where_conditions.append(
                    f"datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {range_value} HOUR)"
                )
            elif range_type == 'days':
                if range_value == 0:
                    where_conditions.append("DATE(datetime) = CURRENT_DATE()")
                else:
                    where_conditions.append(
                        f"datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {range_value} DAY)"
                    )
        else:
            # Default: last 7 days to ensure we get data (increased from 2 days)
            where_conditions.append("DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)")

        # Indicator conditions
        for field, operator, value in conditions:
            # Replace {ma_50} placeholder with correct field name for this market type
            if isinstance(value, str) and '{ma_50}' in value:
                value = value.replace('{ma_50}', ma_50_field)

            if isinstance(value, str) and value.startswith('subquery:'):
                # Handle avg/percentile subqueries
                metric = value.split(':')[1]
                if metric == 'AVG':
                    if use_latest_only:
                        # For CTE, we need to reference the outer query
                        where_conditions.append(
                            f"{field} {operator} (SELECT AVG({field}) FROM latest_records WHERE rn = 1)"
                        )
                    else:
                        where_conditions.append(
                            f"{field} {operator} (SELECT AVG({field}) FROM {table_name})"
                        )
            else:
                where_conditions.append(f"{field} {operator} {value}")

        # Build WHERE clause
        if use_latest_only:
            # For CTE, we already have "WHERE rn = 1" in the CTE
            # Add additional conditions with AND
            if where_conditions:
                where_clause = "AND " + " AND ".join(where_conditions)
            else:
                where_clause = ""
        else:
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        # ORDER BY clause
        if comparison:
            sort_field, sort_dir = comparison
            order_clause = f"ORDER BY {sort_field} {sort_dir}"
        else:
            order_clause = "ORDER BY datetime DESC"

        # LIMIT clause
        limit_clause = f"LIMIT {limit}"

        # Combine all clauses
        # Note: For better performance, we should use a subquery to get latest records per symbol
        # But for now, we'll use the simple approach with time range filter
        sql = f"{select_clause}\n{from_clause}\n{where_clause}\n{order_clause}\n{limit_clause}"

        # Add comment to SQL for debugging
        sql = f"-- NLP Query: market={market_type}, symbol={symbol}, conditions={len(conditions)}\n{sql}"

        return sql

    def _generate_interpretation(self, market_type, symbol, conditions, comparison, time_range, limit):
        """Generate human-readable interpretation"""
        parts = []

        # What we're looking for
        if comparison:
            field, direction = comparison
            if field == 'roc':
                parts.append(f"Top {limit} {'gainers' if direction == 'DESC' else 'losers'}")
            elif field == 'volume':
                parts.append(f"{'Highest' if direction == 'DESC' else 'Lowest'} volume")
            else:
                parts.append(f"Sorted by {field}")
        else:
            parts.append(f"Showing {limit} results")

        # Market type
        market_name = "cryptocurrencies" if market_type == 'crypto' else "stocks"
        parts.append(f"for {market_name}")

        # Symbol filter
        if symbol:
            if len(symbol) == 1:
                parts.append(f"(symbol: {symbol[0]})")
            else:
                parts.append(f"({len(symbol)} symbols)")

        # Conditions
        if conditions:
            condition_text = []
            for field, op, val in conditions:
                op_text = {
                    '>': 'above',
                    '<': 'below',
                    '>=': 'at least',
                    '<=': 'at most',
                    '=': 'equal to'
                }.get(op, op)

                if isinstance(val, str) and val.startswith('subquery:'):
                    val_text = 'average'
                else:
                    val_text = str(val)

                condition_text.append(f"{field} {op_text} {val_text}")

            parts.append(f"with {', '.join(condition_text)}")

        # Time range
        if time_range:
            range_type, range_value = time_range
            if range_type == 'hours':
                parts.append(f"in last {range_value} hours")
            elif range_type == 'days':
                if range_value == 0:
                    parts.append("today")
                else:
                    parts.append(f"in last {range_value} days")

        return " ".join(parts)


# Example usage and testing
if __name__ == "__main__":
    engine = NLPQueryEngine()

    test_queries = [
        "oversold cryptos",
        "Bitcoin hourly last 24 hours",
        "top 10 stock gainers",
        "stocks with RSI below 40 and above 200 MA",
        "AAPL 5-minute",
        "high volume ethereum",
        "bullish MACD stocks",
        "Tesla today"
    ]

    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print(f"{'='*70}")
        sql, table, interpretation = engine.parse_query(query)
        print(f"Table: {table}")
        print(f"Interpretation: {interpretation}")
        print(f"\nSQL:\n{sql}")
