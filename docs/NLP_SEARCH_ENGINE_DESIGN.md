# NLP SQL Query Engine Design
**Date**: November 16, 2025
**Purpose**: Natural language search across all 6 trading data tables

## Architecture Overview

### Data Tables (6 Total)
1. **crypto_analysis** - Daily crypto OHLC + 29 indicators
2. **crypto_hourly_data** - Hourly crypto OHLC + 29 indicators
3. **crypto_5min_top10_gainers** - 5-minute crypto OHLC + indicators
4. **stock_analysis** - Daily stock OHLC + 29 indicators
5. **stock_hourly_data** - Hourly stock OHLC + 29 indicators
6. **stock_5min_top10_gainers** - 5-minute stock OHLC + indicators

### Query Patterns to Support

#### 1. Symbol/Pair Lookup
- "Show me Bitcoin"
- "AAPL hourly data"
- "Tesla 5-minute chart"
- "ETH vs BTC"

#### 2. Indicator-Based Queries
- "Oversold cryptos" (RSI < 30)
- "Stocks with bullish MACD"
- "Cryptos breaking Bollinger Bands"
- "Strong trend stocks" (ADX > 25)
- "High momentum plays"

#### 3. Time-Based Queries
- "Bitcoin last 24 hours"
- "AAPL today"
- "Top gainers this hour"
- "Weekly performance"

#### 4. Complex Multi-Condition
- "Oversold stocks with strong volume"
- "Cryptos above 200 MA with RSI below 40"
- "High volatility stocks in uptrend"
- "Fibonacci retracement opportunities"

#### 5. Comparative Queries
- "Top 10 gainers"
- "Biggest losers today"
- "Highest volume cryptos"
- "Most volatile stocks"

## NLP Processing Pipeline

### Step 1: Intent Classification
Classify query intent:
- **LOOKUP**: Find specific symbol/pair
- **FILTER**: Apply indicator filters
- **COMPARE**: Rank/sort results
- **TIMERANGE**: Specific time period
- **MULTI**: Complex multi-condition

### Step 2: Entity Extraction
Extract entities:
- **Symbol**: AAPL, BTC, TSLA, ETH
- **Timeframe**: hourly, daily, 5min, 5-minute
- **Indicator**: RSI, MACD, Bollinger, ADX, ATR
- **Threshold**: >70, <30, above, below
- **Comparison**: top, highest, biggest, most
- **Count**: 10, 20, top 5

### Step 3: Table Selection
Determine which table(s) to query:
- **crypto** keywords → crypto tables
- **stock** keywords or stock symbols → stock tables
- **hourly** → hourly tables
- **5-minute, 5min** → 5min tables
- **daily, default** → analysis tables

### Step 4: SQL Generation
Build SQL query with:
- SELECT clause (fields needed)
- FROM clause (table selection)
- WHERE clause (filters)
- ORDER BY clause (sorting)
- LIMIT clause (result count)

### Step 5: Result Formatting
Format results for frontend:
- Chart data format
- Table display format
- Summary statistics

## Implementation Components

### Backend API Endpoint
```
POST /api/nlp/query
Body: { "query": "oversold cryptos with high volume" }
Response: {
  "sql": "SELECT...",
  "table": "crypto_analysis",
  "results": [...],
  "count": 15,
  "interpretation": "Found 15 cryptocurrencies with RSI < 30 and volume > average"
}
```

### NLP Processing Module
```python
class NLPQueryEngine:
    def __init__(self):
        self.symbol_map = {...}  # BTC → XXBTZUSD, etc.
        self.indicator_patterns = {...}
        self.timeframe_keywords = {...}

    def parse_query(self, query_text):
        intent = self.classify_intent(query_text)
        entities = self.extract_entities(query_text)
        tables = self.select_tables(entities)
        sql = self.generate_sql(intent, entities, tables)
        return sql, tables

    def classify_intent(self, text):
        # Pattern matching or simple ML classifier
        ...

    def extract_entities(self, text):
        # Regex patterns + keyword matching
        ...

    def generate_sql(self, intent, entities, tables):
        # SQL template filling
        ...
```

### Keyword Dictionaries

#### Indicators
```python
INDICATOR_KEYWORDS = {
    'oversold': ('rsi', '<', 30),
    'overbought': ('rsi', '>', 70),
    'bullish': ('macd', '>', 0),
    'bearish': ('macd', '<', 0),
    'strong trend': ('adx', '>', 25),
    'weak trend': ('adx', '<', 20),
    'high volume': ('volume', '>', 'AVG(volume)'),
    'volatile': ('atr', '>', 'AVG(atr)'),
    'momentum': ('roc', '>', 5),
    'bollinger breakout': ('close', '>', 'bb_upper'),
    'below 200 ma': ('close', '<', 'sma_200'),
    'above 50 ma': ('close', '>', 'sma_50'),
}
```

#### Symbols
```python
CRYPTO_SYMBOLS = {
    'bitcoin': ['XXBTZUSD', 'BTCUSD', 'XBTUSD'],
    'btc': ['XXBTZUSD', 'BTCUSD', 'XBTUSD'],
    'ethereum': ['XETHZUSD', 'ETHUSD'],
    'eth': ['XETHZUSD', 'ETHUSD'],
    'solana': ['SOLUSD'],
    'sol': ['SOLUSD'],
    ...
}

STOCK_SYMBOLS = {
    'apple': 'AAPL',
    'tesla': 'TSLA',
    'nvidia': 'NVDA',
    'microsoft': 'MSFT',
    ...
}
```

#### Timeframes
```python
TIMEFRAME_KEYWORDS = {
    'hourly': 'hourly_data',
    'hour': 'hourly_data',
    '1h': 'hourly_data',
    'daily': 'analysis',
    'day': 'analysis',
    '1d': 'analysis',
    '5-minute': '5min_top10_gainers',
    '5min': '5min_top10_gainers',
    '5m': '5min_top10_gainers',
}
```

## Example Query Translations

### Example 1: "Oversold cryptos"
```python
Input: "oversold cryptos"
Intent: FILTER
Entities: {
    'market': 'crypto',
    'indicator': 'rsi',
    'condition': '<',
    'threshold': 30,
    'timeframe': 'daily'  # default
}
Table: crypto_analysis
SQL:
  SELECT pair, close, rsi, volume, datetime
  FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`
  WHERE rsi < 30
  AND DATE(datetime) = CURRENT_DATE() - 1
  ORDER BY rsi ASC
  LIMIT 20
```

### Example 2: "Bitcoin hourly last 24 hours"
```python
Input: "bitcoin hourly last 24 hours"
Intent: LOOKUP + TIMERANGE
Entities: {
    'symbol': 'XXBTZUSD',
    'market': 'crypto',
    'timeframe': 'hourly',
    'time_range': '24 hours'
}
Table: crypto_hourly_data
SQL:
  SELECT pair, datetime, open, high, low, close, volume,
         rsi, macd, adx
  FROM `cryptobot-462709.crypto_trading_data.crypto_hourly_data`
  WHERE pair IN ('XXBTZUSD', 'BTCUSD', 'XBTUSD')
  AND datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  ORDER BY datetime DESC
  LIMIT 24
```

### Example 3: "Top 10 gainers stocks"
```python
Input: "top 10 gainers stocks"
Intent: COMPARE
Entities: {
    'market': 'stock',
    'comparison': 'top',
    'metric': 'roc',
    'count': 10,
    'direction': 'DESC',
    'timeframe': 'daily'
}
Table: stock_analysis
SQL:
  SELECT symbol, close, roc, volume, rsi, macd, datetime
  FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
  WHERE DATE(datetime) = CURRENT_DATE() - 1
  ORDER BY roc DESC
  LIMIT 10
```

### Example 4: "Stocks with RSI below 40 and above 200 MA"
```python
Input: "stocks with RSI below 40 and above 200 MA"
Intent: MULTI
Entities: {
    'market': 'stock',
    'conditions': [
        ('rsi', '<', 40),
        ('close', '>', 'sma_200')
    ],
    'timeframe': 'daily'
}
Table: stock_analysis
SQL:
  SELECT symbol, close, rsi, sma_200, roc, volume, datetime
  FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
  WHERE rsi < 40
  AND close > sma_200
  AND DATE(datetime) = CURRENT_DATE() - 1
  ORDER BY roc DESC
  LIMIT 20
```

## Frontend Integration

### Search Bar Component
```javascript
async function handleNLPSearch(query) {
  const response = await fetch('/api/nlp/query', {
    method: 'POST',
    body: JSON.stringify({ query }),
    headers: { 'Content-Type': 'application/json' }
  });

  const result = await response.json();

  // Display interpretation
  showInterpretation(result.interpretation);

  // Display results in table or chart
  if (result.display_mode === 'chart') {
    renderChart(result.results);
  } else {
    renderTable(result.results);
  }
}
```

### Search Suggestions
```javascript
const SEARCH_SUGGESTIONS = [
  "Oversold cryptos",
  "Bitcoin hourly",
  "Top 10 stock gainers",
  "Stocks with bullish MACD",
  "High volume cryptos",
  "AAPL 5-minute",
  "Ethereum vs Bitcoin",
  "Strong trend stocks",
  "Bollinger breakout opportunities"
];
```

## Performance Optimizations

1. **Query Caching**: Cache recent NLP queries (15-minute TTL)
2. **Pre-computed Views**: Create materialized views for common queries
3. **Index Optimization**: Ensure indexes on rsi, macd, adx, volume, datetime
4. **Result Limiting**: Default LIMIT 20, max LIMIT 100
5. **Parallel Queries**: Query multiple tables in parallel when needed

## Security Considerations

1. **SQL Injection Prevention**: Use parameterized queries only
2. **Query Validation**: Whitelist allowed tables and fields
3. **Rate Limiting**: Max 10 NLP queries per minute per user
4. **Query Complexity**: Limit JOIN operations and subqueries
5. **Result Size**: Cap at 1000 rows maximum

## Future Enhancements

1. **ML-based NLP**: Replace pattern matching with transformer model
2. **Query History**: Learn from user patterns
3. **Auto-complete**: Suggest completions as user types
4. **Multi-language**: Support Spanish, Chinese queries
5. **Voice Search**: Integrate speech-to-text
6. **Chart Auto-generation**: Auto-select best chart type for query
7. **Alert Creation**: "Alert me when Bitcoin becomes oversold"

---

**Status**: Design Complete
**Next Step**: Implement NLPQueryEngine class in trading-api
