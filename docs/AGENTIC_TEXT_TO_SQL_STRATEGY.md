# Agentic Text-to-SQL Strategy for AIAlgoTradeHits
## A Comprehensive Framework for AI-Powered Trading Analytics

**Document Version:** 1.0
**Created:** December 7, 2025
**Author:** AIAlgoTradeHits Development Team

---

## Executive Summary

This document outlines a robust agentic Text-to-SQL strategy leveraging Google Cloud Platform's (GCP) Agent Development Kit (ADK), Vertex AI with Gemini 2.5, and BigQuery to create an intelligent trading analytics platform. The strategy enables natural language queries to be converted into precise SQL queries, delivering actionable trading insights.

---

## Part 1: System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                 │
│  │   Web App       │  │   Voice Input   │  │   API Clients   │                 │
│  │   (React)       │  │   (WebSpeech)   │  │   (REST/gRPC)   │                 │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘                 │
└───────────┼─────────────────────┼─────────────────────┼─────────────────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATION LAYER                                     │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                    MASTER ORCHESTRATOR AGENT                               │  │
│  │   - Query Classification                                                   │  │
│  │   - Agent Routing                                                          │  │
│  │   - Response Aggregation                                                   │  │
│  │   - Context Management                                                     │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SPECIALIZED AGENT LAYER                                 │
│                                                                                   │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐           │
│  │  TEXT-TO-SQL      │  │  MARKET SCANNER   │  │  TECHNICAL        │           │
│  │  AGENT            │  │  AGENT            │  │  ANALYSIS AGENT   │           │
│  │                   │  │                   │  │                   │           │
│  │  - Query Parsing  │  │  - Asset Scanning │  │  - Indicator Calc │           │
│  │  - SQL Generation │  │  - Pattern Detect │  │  - Signal Generate│           │
│  │  - Query Optimize │  │  - Ranking Logic  │  │  - Trend Analysis │           │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘           │
│                                                                                   │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐           │
│  │  SENTIMENT        │  │  PREDICTIVE       │  │  RISK             │           │
│  │  AGENT            │  │  ANALYTICS AGENT  │  │  ASSESSMENT AGENT │           │
│  │                   │  │                   │  │                   │           │
│  │  - News Analysis  │  │  - ML Predictions │  │  - Position Sizing│           │
│  │  - Social Feeds   │  │  - Price Targets  │  │  - Volatility Calc│           │
│  │  - Fear/Greed     │  │  - Trend Forecast │  │  - Correlation    │           │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AI/ML LAYER (VERTEX AI)                                 │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐           │
│  │  Gemini 2.5 Pro   │  │  Custom ML Models │  │  Embeddings API   │           │
│  │  - NLU/NLG        │  │  - Price Predict  │  │  - Semantic Search│           │
│  │  - Text-to-SQL    │  │  - Pattern Recog  │  │  - Document RAG   │           │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER (BIGQUERY)                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    TRADING DATA WAREHOUSE                                │    │
│  │   Dataset: aialgotradehits.crypto_trading_data                          │    │
│  │                                                                          │    │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │    │
│  │   │ v2_stocks_*  │  │ v2_crypto_*  │  │ v2_forex_*   │                 │    │
│  │   │ - daily      │  │ - daily      │  │ - daily      │                 │    │
│  │   │ - hourly     │  │ - hourly     │  │ - hourly     │                 │    │
│  │   │ - 5min       │  │ - 5min       │  │ - 5min       │                 │    │
│  │   │ - weekly     │  │ - weekly     │  │ - weekly     │                 │    │
│  │   └──────────────┘  └──────────────┘  └──────────────┘                 │    │
│  │                                                                          │    │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │    │
│  │   │ v2_etfs_*    │  │ v2_indices_* │  │v2_commodities│                 │    │
│  │   └──────────────┘  └──────────────┘  └──────────────┘                 │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Agent Communication Flow

```
User Query: "Show me tech stocks that are oversold and breaking out"
                    │
                    ▼
┌───────────────────────────────────────────────────────────────┐
│                   MASTER ORCHESTRATOR                          │
│   1. Parse intent: STOCK SCREENING + TECHNICAL ANALYSIS       │
│   2. Extract entities: sector=Technology, rsi<30, breakout    │
│   3. Route to: TEXT-TO-SQL + TECHNICAL ANALYSIS agents        │
└───────────────────────────────────────────────────────────────┘
                    │
        ┌──────────┴──────────┐
        ▼                     ▼
┌───────────────┐     ┌───────────────┐
│ TEXT-TO-SQL   │     │ TECHNICAL     │
│ AGENT         │     │ ANALYSIS      │
│               │     │ AGENT         │
│ Generate SQL: │     │               │
│ SELECT *      │     │ Validate:     │
│ FROM stocks   │     │ - RSI < 30    │
│ WHERE sector  │     │ - Near 52w Hi │
│ = 'Tech'      │     │ - Volume spike│
│ AND rsi < 30  │     │               │
└───────────────┘     └───────────────┘
        │                     │
        └──────────┬──────────┘
                   ▼
┌───────────────────────────────────────────────────────────────┐
│                   RESULT AGGREGATOR                            │
│   1. Execute SQL query                                         │
│   2. Apply technical filters                                   │
│   3. Rank by opportunity score                                 │
│   4. Generate natural language summary                         │
└───────────────────────────────────────────────────────────────┘
                   │
                   ▼
        Final Response to User
```

---

## Part 2: Agent Specifications

### 2.1 Text-to-SQL Agent

**Purpose:** Convert natural language queries into precise BigQuery SQL

**Capabilities:**
- Parse trading terminology (oversold, breakout, momentum, etc.)
- Map natural language to technical indicators (RSI, MACD, ADX, etc.)
- Generate optimized SQL queries for large datasets
- Handle temporal queries (today, last week, 52-week, etc.)
- Support multi-asset type queries (stocks, crypto, forex, etc.)

**Implementation with Gemini 2.5:**

```python
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel

class TextToSQLAgent:
    def __init__(self):
        self.model = GenerativeModel("gemini-2.5-pro")
        self.schema_context = self._load_schema_documentation()

    def _load_schema_documentation(self):
        # Load TRADING_TABLE_DOCUMENTATION.md content
        with open('TRADING_TABLE_DOCUMENTATION.md', 'r') as f:
            return f.read()

    def generate_sql(self, natural_language_query: str, context: dict) -> dict:
        """Generate SQL from natural language query"""

        prompt = f"""You are an expert SQL developer for a trading analytics platform.

DATABASE SCHEMA AND TRADING TERMINOLOGY:
{self.schema_context}

USER CONTEXT:
- Current Page: {context.get('page', 'dashboard')}
- Asset Type Focus: {context.get('asset_type', 'all')}
- Time Period: {context.get('period', 'daily')}

USER QUERY: "{natural_language_query}"

Generate a BigQuery SQL query that answers the user's question.
Return ONLY the SQL query, no explanations.

IMPORTANT RULES:
1. Always use fully qualified table names: `aialgotradehits.crypto_trading_data.table_name`
2. For daily data, use v2_{{asset_type}}_daily tables
3. For weekly data, use v2_{{asset_type}}_weekly_summary tables
4. Always include ORDER BY and LIMIT clauses
5. Handle NULL values appropriately with COALESCE or IS NOT NULL
6. Use ROW_NUMBER() for getting latest records per symbol
"""

        response = self.model.generate_content(prompt)

        return {
            'sql': response.text.strip(),
            'interpretation': self._generate_interpretation(natural_language_query),
            'tables_used': self._extract_tables(response.text)
        }
```

### 2.2 Market Scanner Agent

**Purpose:** Scan markets for trading opportunities based on criteria

**Capabilities:**
- Screen across all asset types simultaneously
- Apply technical indicator filters
- Rank opportunities by configurable scoring
- Detect chart patterns (breakouts, reversals, consolidations)

**Key Functions:**
1. `scan_gainers()` - Find top performing assets
2. `scan_losers()` - Find worst performing assets
3. `scan_oversold()` - Find RSI < 30 assets
4. `scan_overbought()` - Find RSI > 70 assets
5. `scan_breakouts()` - Find assets near 52-week highs
6. `scan_volume_spike()` - Find unusual volume activity

### 2.3 Technical Analysis Agent

**Purpose:** Calculate and interpret technical indicators

**Capabilities:**
- Real-time indicator calculations
- Multi-timeframe analysis
- Signal generation (buy/sell/hold)
- Trend identification (uptrend, downtrend, sideways)
- Support/resistance level detection

**Indicators Supported:**
| Category | Indicators |
|----------|------------|
| Momentum | RSI, MACD, Stochastic, ROC, Momentum, Williams %R |
| Trend | SMA (20/50/200), EMA (12/26/50), ADX, KAMA, TRIX |
| Volatility | Bollinger Bands, ATR, Standard Deviation |
| Volume | OBV, PVO, Volume MA |
| Oscillators | CCI, PPO, Ultimate Oscillator, Awesome Oscillator |

### 2.4 Sentiment Agent

**Purpose:** Analyze market sentiment from news and social media

**Data Sources:**
- Finnhub API (news sentiment)
- CoinMarketCap (Fear & Greed Index for crypto)
- Social sentiment (Reddit, Twitter mentions)

**Capabilities:**
- News headline sentiment analysis
- Aggregate sentiment scoring
- Fear/Greed index tracking
- Social mention volume tracking

### 2.5 Predictive Analytics Agent

**Purpose:** Generate price predictions using ML models

**Models:**
1. Time Series Forecasting (Prophet, LSTM)
2. Price Target Estimation
3. Trend Probability Scoring
4. Volatility Prediction

### 2.6 Risk Assessment Agent

**Purpose:** Evaluate and manage trading risk

**Capabilities:**
- Position sizing recommendations
- Stop-loss level suggestions
- Portfolio correlation analysis
- Volatility-adjusted returns
- Drawdown calculations

---

## Part 3: GCP Agent Development Kit (ADK) Implementation

### 3.1 ADK Overview

Google Cloud ADK provides tools for building, deploying, and managing AI agents. For AIAlgoTradeHits, we'll use:

1. **Vertex AI Agent Builder** - Create and orchestrate agents
2. **Vertex AI Workbench** - Develop and test agents
3. **Cloud Functions** - Serverless agent execution
4. **Cloud Run** - Containerized agent services
5. **Pub/Sub** - Inter-agent communication

### 3.2 Agent Configuration Template

```yaml
# agent_config.yaml
agent:
  name: text-to-sql-trading-agent
  version: 1.0.0
  description: "Converts natural language to SQL for trading analytics"

  model:
    name: gemini-2.5-pro
    parameters:
      temperature: 0.1  # Low for precise SQL generation
      max_tokens: 2048
      top_p: 0.95

  tools:
    - name: bigquery_executor
      type: function
      description: "Executes SQL queries against BigQuery"
      parameters:
        project_id: aialgotradehits
        dataset_id: crypto_trading_data

    - name: schema_lookup
      type: retrieval
      description: "Retrieves table schema information"
      data_source: gs://aialgotradehits-training/schemas/

  knowledge_base:
    - trading_terminology.json
    - indicator_definitions.json
    - sql_examples.json

  fallback:
    type: escalate_to_human
    message: "I couldn't understand your query. Please rephrase or contact support."
```

### 3.3 Multi-Agent Orchestration

```python
from google.cloud import aiplatform
from typing import List, Dict, Any

class TradingAgentOrchestrator:
    """Master orchestrator for coordinating trading agents"""

    def __init__(self):
        self.agents = {
            'text_to_sql': TextToSQLAgent(),
            'market_scanner': MarketScannerAgent(),
            'technical_analysis': TechnicalAnalysisAgent(),
            'sentiment': SentimentAgent(),
            'predictive': PredictiveAgent(),
            'risk': RiskAssessmentAgent()
        }
        self.gemini = GenerativeModel("gemini-2.5-pro")

    async def process_query(self, query: str, context: dict) -> dict:
        """Process user query through appropriate agents"""

        # Step 1: Classify query intent
        intent = await self._classify_intent(query)

        # Step 2: Route to appropriate agents
        agents_to_use = self._select_agents(intent)

        # Step 3: Execute agents in parallel where possible
        results = await self._execute_agents(agents_to_use, query, context)

        # Step 4: Aggregate and format response
        response = await self._aggregate_results(results, query)

        return response

    async def _classify_intent(self, query: str) -> dict:
        """Use Gemini to classify the query intent"""

        prompt = f"""Classify this trading query into categories:

Query: "{query}"

Categories (select all that apply):
1. STOCK_SCREENING - Looking for stocks/assets matching criteria
2. TECHNICAL_ANALYSIS - Asking about indicators or patterns
3. SENTIMENT_ANALYSIS - Asking about market sentiment or news
4. PRICE_PREDICTION - Asking for price forecasts
5. RISK_ASSESSMENT - Asking about risk or position sizing
6. DATA_QUERY - Simple data retrieval

Return JSON: {{"categories": ["CATEGORY1", "CATEGORY2"], "primary": "CATEGORY1"}}"""

        response = self.gemini.generate_content(prompt)
        return json.loads(response.text)

    def _select_agents(self, intent: dict) -> List[str]:
        """Map intents to agents"""

        mapping = {
            'STOCK_SCREENING': ['text_to_sql', 'market_scanner'],
            'TECHNICAL_ANALYSIS': ['text_to_sql', 'technical_analysis'],
            'SENTIMENT_ANALYSIS': ['sentiment'],
            'PRICE_PREDICTION': ['predictive', 'technical_analysis'],
            'RISK_ASSESSMENT': ['risk', 'technical_analysis'],
            'DATA_QUERY': ['text_to_sql']
        }

        agents = set()
        for category in intent.get('categories', ['DATA_QUERY']):
            agents.update(mapping.get(category, ['text_to_sql']))

        return list(agents)
```

---

## Part 4: Text-to-SQL Best Practices

### 4.1 Query Classification Taxonomy

```
TRADING QUERIES
├── SCREENING QUERIES
│   ├── Performance-based (gainers, losers, movers)
│   ├── Indicator-based (oversold, overbought, strong trend)
│   ├── Price-based (over $100, under $50, penny stocks)
│   └── Sector-based (tech stocks, energy, healthcare)
│
├── ANALYTICAL QUERIES
│   ├── Single-asset analysis (AAPL performance)
│   ├── Comparison queries (AAPL vs MSFT)
│   ├── Aggregate queries (average RSI by sector)
│   └── Time-series queries (price history)
│
├── PREDICTIVE QUERIES
│   ├── Trend questions (is AAPL bullish?)
│   ├── Target questions (price target for BTC?)
│   └── Signal questions (should I buy XYZ?)
│
└── INFORMATIONAL QUERIES
    ├── Definition queries (what is RSI?)
    ├── Schema queries (what data do you have?)
    └── Status queries (when was data updated?)
```

### 4.2 SQL Generation Templates

**Template 1: Screening Query**
```sql
-- Natural Language: "Show me oversold tech stocks"
SELECT
    symbol,
    name,
    sector,
    close as price,
    percent_change,
    rsi,
    macd
FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
WHERE
    sector = 'Technology'
    AND rsi < 30
    AND rsi IS NOT NULL
ORDER BY rsi ASC
LIMIT 50;
```

**Template 2: Top N Query**
```sql
-- Natural Language: "Top 10 crypto gainers today"
WITH latest_data AS (
    SELECT
        symbol,
        name,
        close,
        percent_change,
        volume,
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
    FROM `aialgotradehits.crypto_trading_data.v2_crypto_daily`
    WHERE DATE(datetime) = CURRENT_DATE()
)
SELECT symbol, name, close, percent_change, volume
FROM latest_data
WHERE rn = 1
ORDER BY percent_change DESC
LIMIT 10;
```

**Template 3: Comparison Query**
```sql
-- Natural Language: "Compare AAPL and MSFT performance"
WITH symbol_data AS (
    SELECT
        symbol,
        close,
        percent_change,
        rsi,
        macd,
        adx,
        datetime,
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
    FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
    WHERE symbol IN ('AAPL', 'MSFT')
)
SELECT
    symbol,
    close as current_price,
    percent_change as daily_change,
    rsi,
    macd,
    adx
FROM symbol_data
WHERE rn = 1;
```

### 4.3 Error Handling Strategy

```python
class SQLGenerationError(Exception):
    """Custom exception for SQL generation failures"""
    pass

class TextToSQLAgent:

    def generate_sql_with_fallback(self, query: str, context: dict) -> dict:
        """Generate SQL with multiple fallback strategies"""

        # Strategy 1: Direct Gemini generation
        try:
            result = self._gemini_generate(query, context)
            if self._validate_sql(result['sql']):
                return result
        except Exception as e:
            logger.warning(f"Gemini generation failed: {e}")

        # Strategy 2: Template matching
        try:
            result = self._template_match(query, context)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Template matching failed: {e}")

        # Strategy 3: Basic NLP parsing
        try:
            result = self._basic_nlp_parse(query, context)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Basic NLP failed: {e}")

        # Strategy 4: Return safe default query
        return self._default_query(context)

    def _validate_sql(self, sql: str) -> bool:
        """Validate SQL syntax and safety"""

        # Check for dangerous keywords
        dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE']
        sql_upper = sql.upper()
        for keyword in dangerous:
            if keyword in sql_upper:
                raise SQLGenerationError(f"Dangerous SQL keyword detected: {keyword}")

        # Verify table references
        if 'aialgotradehits.crypto_trading_data' not in sql:
            raise SQLGenerationError("Invalid table reference")

        return True
```

---

## Part 5: Trading Signal Generation

### 5.1 Signal Scoring System

Each asset receives a composite trading score based on multiple factors:

```python
class TradingSignalGenerator:

    def calculate_signal_score(self, data: dict) -> dict:
        """Calculate composite trading signal score (0-100)"""

        scores = {}

        # Momentum Score (0-25)
        rsi = data.get('rsi', 50)
        if rsi < 30:
            scores['momentum'] = 25 - (30 - rsi)  # Oversold = bullish
        elif rsi > 70:
            scores['momentum'] = 25 - (rsi - 70)  # Overbought = bearish
        else:
            scores['momentum'] = 12.5

        # Trend Score (0-25)
        adx = data.get('adx', 20)
        if adx > 25:
            scores['trend'] = min(25, adx - 10)
        else:
            scores['trend'] = adx / 2

        # MACD Score (0-25)
        macd = data.get('macd', 0)
        macd_signal = data.get('macd_signal', 0)
        if macd > macd_signal:
            scores['macd'] = 25  # Bullish crossover
        else:
            scores['macd'] = 0

        # Volume Score (0-25)
        volume_ratio = data.get('volume', 0) / data.get('average_volume', 1)
        scores['volume'] = min(25, volume_ratio * 10)

        total_score = sum(scores.values())

        return {
            'total_score': total_score,
            'component_scores': scores,
            'signal': 'BUY' if total_score > 65 else 'SELL' if total_score < 35 else 'HOLD',
            'confidence': self._calculate_confidence(scores)
        }
```

### 5.2 Opportunity Ranking

```sql
-- SQL for generating opportunity rankings
WITH scored_assets AS (
    SELECT
        symbol,
        name,
        close,
        percent_change,
        rsi,
        macd,
        macd_signal,
        adx,
        volume,
        average_volume,

        -- Momentum Score
        CASE
            WHEN rsi < 30 THEN 25 - (30 - rsi)
            WHEN rsi > 70 THEN 25 - (rsi - 70)
            ELSE 12.5
        END as momentum_score,

        -- Trend Score
        CASE
            WHEN adx > 25 THEN LEAST(25, adx - 10)
            ELSE adx / 2
        END as trend_score,

        -- MACD Score
        CASE WHEN macd > macd_signal THEN 25 ELSE 0 END as macd_score,

        -- Volume Score
        LEAST(25, SAFE_DIVIDE(volume, average_volume) * 10) as volume_score

    FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
    WHERE rsi IS NOT NULL AND macd IS NOT NULL
)
SELECT
    symbol,
    name,
    close as price,
    percent_change,
    rsi,
    adx,
    (momentum_score + trend_score + macd_score + volume_score) as opportunity_score,
    CASE
        WHEN (momentum_score + trend_score + macd_score + volume_score) > 65 THEN 'BUY'
        WHEN (momentum_score + trend_score + macd_score + volume_score) < 35 THEN 'SELL'
        ELSE 'HOLD'
    END as signal
FROM scored_assets
ORDER BY opportunity_score DESC
LIMIT 50;
```

---

## Part 6: Deployment Strategy

### 6.1 Cloud Architecture

```yaml
# deployment.yaml
services:
  orchestrator:
    type: cloud_run
    image: gcr.io/aialgotradehits/trading-orchestrator
    memory: 2Gi
    cpu: 2
    min_instances: 1
    max_instances: 10
    environment:
      - VERTEX_AI_PROJECT: aialgotradehits
      - BIGQUERY_DATASET: crypto_trading_data
      - GEMINI_MODEL: gemini-2.5-pro

  text_to_sql_agent:
    type: cloud_function
    runtime: python311
    memory: 1Gi
    timeout: 120s
    trigger: http

  market_scanner_agent:
    type: cloud_function
    runtime: python311
    memory: 2Gi
    timeout: 300s
    trigger: pubsub
    topic: market-scan-requests

  technical_agent:
    type: cloud_run
    image: gcr.io/aialgotradehits/technical-agent
    memory: 4Gi
    cpu: 4
    concurrency: 100
```

### 6.2 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ai/smart-search` | POST | Natural language query processing |
| `/api/ai/text-to-sql` | POST | Direct SQL generation from NL |
| `/api/ai/market-scan` | POST | Market screening with filters |
| `/api/ai/technical` | POST | Technical analysis for symbol |
| `/api/ai/signals` | GET | Current trading signals |
| `/api/ai/predictions` | POST | Price predictions for symbol |

---

## Part 7: Performance Optimization

### 7.1 Query Caching Strategy

```python
from google.cloud import redis

class QueryCache:
    def __init__(self):
        self.redis = redis.Client()
        self.ttl = {
            'static_data': 86400,      # 24 hours
            'daily_data': 3600,        # 1 hour
            'realtime_data': 60,       # 1 minute
            'computed_signals': 300    # 5 minutes
        }

    def get_or_compute(self, query_hash: str, compute_fn: callable, data_type: str):
        cached = self.redis.get(query_hash)
        if cached:
            return json.loads(cached)

        result = compute_fn()
        self.redis.setex(query_hash, self.ttl[data_type], json.dumps(result))
        return result
```

### 7.2 BigQuery Optimization

```sql
-- Use partitioning and clustering for optimal performance
CREATE OR REPLACE TABLE `aialgotradehits.crypto_trading_data.v2_stocks_daily_optimized`
PARTITION BY DATE(datetime)
CLUSTER BY symbol, sector
AS SELECT * FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`;

-- Materialized view for common queries
CREATE MATERIALIZED VIEW `aialgotradehits.crypto_trading_data.mv_daily_signals`
AS
SELECT
    symbol,
    name,
    sector,
    close,
    percent_change,
    rsi,
    macd,
    adx,
    CASE WHEN rsi < 30 THEN 'OVERSOLD' WHEN rsi > 70 THEN 'OVERBOUGHT' ELSE 'NEUTRAL' END as rsi_signal,
    CASE WHEN macd > macd_signal THEN 'BULLISH' ELSE 'BEARISH' END as macd_signal,
    CASE WHEN adx > 25 THEN 'STRONG' ELSE 'WEAK' END as trend_strength
FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
WHERE DATE(datetime) = CURRENT_DATE();
```

---

## Part 8: Monitoring and Observability

### 8.1 Metrics to Track

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `query_latency_p95` | 95th percentile query time | > 5 seconds |
| `sql_generation_success_rate` | % of successful SQL generations | < 95% |
| `agent_error_rate` | % of agent failures | > 5% |
| `cache_hit_rate` | % of queries served from cache | < 50% |
| `bigquery_slot_usage` | BigQuery compute usage | > 80% capacity |

### 8.2 Logging Strategy

```python
import structlog

logger = structlog.get_logger()

class AgentLogger:
    def log_query(self, query: str, context: dict, result: dict, latency_ms: int):
        logger.info(
            "agent_query_processed",
            query=query[:200],
            context=context,
            success=result.get('success', False),
            latency_ms=latency_ms,
            sql_generated=bool(result.get('sql')),
            results_count=len(result.get('results', []))
        )
```

---

## Part 9: Security Considerations

### 9.1 SQL Injection Prevention

```python
class SQLSanitizer:
    BLOCKED_KEYWORDS = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER',
        'TRUNCATE', 'CREATE', 'GRANT', 'REVOKE', 'EXECUTE'
    ]

    def sanitize(self, sql: str) -> str:
        # Check for blocked keywords
        sql_upper = sql.upper()
        for keyword in self.BLOCKED_KEYWORDS:
            if keyword in sql_upper:
                raise SecurityError(f"Blocked SQL keyword: {keyword}")

        # Ensure only SELECT statements
        if not sql_upper.strip().startswith('SELECT'):
            raise SecurityError("Only SELECT statements allowed")

        # Validate table references
        if 'aialgotradehits.crypto_trading_data' not in sql:
            raise SecurityError("Invalid table reference")

        return sql
```

### 9.2 Rate Limiting

```python
from google.cloud import redis

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.redis = redis.Client()
        self.limit = requests_per_minute

    def check_limit(self, user_id: str) -> bool:
        key = f"rate_limit:{user_id}"
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, 60)
        return current <= self.limit
```

---

## Part 10: Future Roadmap

### Phase 1: Foundation (Months 1-2)
- [x] Implement Text-to-SQL agent with Gemini 2.5
- [x] Deploy basic market scanner
- [ ] Create comprehensive schema documentation
- [ ] Build initial API endpoints

### Phase 2: Intelligence (Months 3-4)
- [ ] Add technical analysis agent
- [ ] Implement sentiment analysis integration
- [ ] Build predictive models
- [ ] Create signal scoring system

### Phase 3: Scale (Months 5-6)
- [ ] Optimize query performance
- [ ] Implement caching layer
- [ ] Add real-time data streaming
- [ ] Build alerting system

### Phase 4: Advanced (Months 7+)
- [ ] Multi-agent orchestration
- [ ] Custom ML model training
- [ ] Portfolio optimization agent
- [ ] Backtesting agent

---

## Conclusion

This agentic Text-to-SQL strategy provides a robust framework for building an AI-powered trading analytics platform. By leveraging GCP's Vertex AI with Gemini 2.5 and a multi-agent architecture, AIAlgoTradeHits can deliver:

1. **Natural Language Access** - Users can query trading data using plain English
2. **Intelligent Analysis** - Multiple specialized agents provide comprehensive insights
3. **Scalable Architecture** - Cloud-native design handles growing data and users
4. **Predictive Capabilities** - ML models provide forward-looking analysis
5. **Real-time Signals** - Continuous monitoring and alerting for trading opportunities

The implementation follows best practices for security, performance, and maintainability, positioning AIAlgoTradeHits as a leading AI-powered trading platform.

---

*Document Version: 1.0*
*Last Updated: December 7, 2025*
*Author: AIAlgoTradeHits Development Team*
