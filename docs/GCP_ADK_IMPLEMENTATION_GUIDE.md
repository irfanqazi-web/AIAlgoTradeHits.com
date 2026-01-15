# GCP Agent Development Kit (ADK) Implementation Guide
## Building AI Agents for AIAlgoTradeHits Trading Platform

**Document Version:** 1.0
**Created:** December 7, 2025

---

## 1. Introduction to GCP Agent Development Kit

### 1.1 What is GCP ADK?

The Google Cloud Platform Agent Development Kit provides tools and frameworks for building, testing, and deploying AI agents. For AIAlgoTradeHits, we leverage:

1. **Vertex AI Agent Builder** - Visual agent creation and configuration
2. **Vertex AI Workbench** - Development and testing environment
3. **Generative AI Models** - Gemini 2.5 Pro for natural language understanding
4. **Cloud Functions & Cloud Run** - Serverless agent execution
5. **BigQuery** - Data warehouse for trading analytics

### 1.2 Why Agents for Trading?

Trading analytics requires multiple specialized capabilities:
- Natural language query understanding
- Real-time market data processing
- Technical indicator calculations
- Sentiment analysis
- Risk assessment

An agentic architecture allows each capability to be developed, tested, and scaled independently.

---

## 2. Agent Architecture for AIAlgoTradeHits

### 2.1 Agent Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    MASTER TRADING ORCHESTRATOR                   │
│    - Routes queries to appropriate agents                        │
│    - Aggregates responses                                        │
│    - Maintains conversation context                              │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ TEXT-TO-SQL   │     │ MARKET        │     │ TECHNICAL     │
│ AGENT         │     │ SCANNER       │     │ ANALYSIS      │
│               │     │ AGENT         │     │ AGENT         │
│ Converts NL   │     │ Screens       │     │ Calculates    │
│ queries to    │     │ assets based  │     │ indicators    │
│ BigQuery SQL  │     │ on criteria   │     │ and signals   │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BIGQUERY DATA LAYER                      │
│  aialgotradehits.crypto_trading_data.*                          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Agent Definitions

| Agent | Purpose | Model | Tools |
|-------|---------|-------|-------|
| Master Orchestrator | Route queries, aggregate responses | Gemini 2.5 Pro | All agents |
| Text-to-SQL | Convert NL to SQL | Gemini 2.5 Pro | BigQuery |
| Market Scanner | Screen assets | Gemini 2.5 Flash | BigQuery, Calculator |
| Technical Analysis | Calculate indicators | Custom Python | pandas, ta-lib |
| Sentiment | Analyze market sentiment | Gemini 2.5 Pro | News APIs |
| Risk Assessment | Evaluate trading risk | Custom ML | Portfolio tools |

---

## 3. Setting Up the Development Environment

### 3.1 Prerequisites

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# Initialize gcloud
gcloud init
gcloud config set project aialgotradehits

# Enable required APIs
gcloud services enable \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  pubsub.googleapis.com

# Install Python dependencies
pip install google-cloud-aiplatform google-cloud-bigquery vertexai
```

### 3.2 Vertex AI Initialization

```python
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# Initialize Vertex AI
PROJECT_ID = "aialgotradehits"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

# Load Gemini 2.5 Pro model
model = GenerativeModel("gemini-2.5-pro")

# Test the model
response = model.generate_content("What is the RSI indicator?")
print(response.text)
```

---

## 4. Building the Text-to-SQL Agent

### 4.1 Agent Configuration

```python
# text_to_sql_agent.py

import json
import re
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel

class TextToSQLAgent:
    """
    Converts natural language queries to BigQuery SQL for trading data.
    Uses Gemini 2.5 Pro for query understanding and generation.
    """

    def __init__(self):
        self.project_id = "aialgotradehits"
        self.dataset_id = "crypto_trading_data"
        self.model = GenerativeModel("gemini-2.5-pro")
        self.bq_client = bigquery.Client(project=self.project_id)
        self.schema_context = self._load_schema_context()

    def _load_schema_context(self) -> str:
        """Load table schema documentation for context"""
        try:
            with open('TRADING_TABLE_DOCUMENTATION.md', 'r', encoding='utf-8') as f:
                return f.read()[:50000]  # Limit context size
        except FileNotFoundError:
            return self._get_dynamic_schema()

    def _get_dynamic_schema(self) -> str:
        """Generate schema context from BigQuery metadata"""
        schema_parts = []
        tables = [
            'v2_stocks_daily', 'v2_crypto_daily', 'v2_forex_daily',
            'v2_etfs_daily', 'v2_indices_daily', 'v2_commodities_daily'
        ]

        for table_name in tables:
            try:
                table = self.bq_client.get_table(
                    f"{self.project_id}.{self.dataset_id}.{table_name}"
                )
                columns = [f"{f.name} ({f.field_type})" for f in table.schema]
                schema_parts.append(f"{table_name}: {', '.join(columns[:20])}")
            except Exception:
                continue

        return "\n".join(schema_parts)

    def generate_sql(self, query: str, context: dict = None) -> dict:
        """
        Generate SQL from natural language query.

        Args:
            query: Natural language query from user
            context: Optional context (asset_type, period, page)

        Returns:
            dict with sql, interpretation, and metadata
        """
        context = context or {}

        prompt = self._build_prompt(query, context)
        response = self.model.generate_content(prompt)

        sql = self._extract_sql(response.text)
        validated = self._validate_sql(sql)

        return {
            "success": validated["valid"],
            "sql": validated["sql"] if validated["valid"] else None,
            "error": validated.get("error"),
            "interpretation": self._generate_interpretation(query),
            "tables_used": self._extract_tables(sql) if validated["valid"] else []
        }

    def _build_prompt(self, query: str, context: dict) -> str:
        """Build the prompt for SQL generation"""

        asset_type = context.get('asset_type', 'all')
        period = context.get('period', 'daily')

        return f"""You are an expert SQL developer for a trading analytics platform.

DATABASE: Google BigQuery
PROJECT: aialgotradehits
DATASET: crypto_trading_data

AVAILABLE TABLES:
- v2_stocks_daily: Daily stock data with 50+ fields including OHLCV and 29 technical indicators
- v2_stocks_weekly_summary: Weekly aggregated stock data
- v2_crypto_daily: Daily cryptocurrency data
- v2_crypto_weekly_summary: Weekly crypto data
- v2_forex_daily: Daily forex pair data
- v2_etfs_daily: Daily ETF data
- v2_indices_daily: Daily index data
- v2_commodities_daily: Daily commodity data

KEY COLUMNS (available in all tables):
- symbol: Asset ticker (STRING)
- name: Asset name (STRING)
- datetime: Timestamp (TIMESTAMP)
- open, high, low, close: OHLC prices (FLOAT)
- volume: Trading volume (FLOAT)
- percent_change: Daily change % (FLOAT)
- rsi: Relative Strength Index 0-100 (FLOAT)
- macd, macd_signal, macd_histogram: MACD indicator (FLOAT)
- sma_20, sma_50, sma_200: Simple Moving Averages (FLOAT)
- adx: Average Directional Index (FLOAT)
- bollinger_upper, bollinger_middle, bollinger_lower: Bollinger Bands (FLOAT)
- week_52_high, week_52_low: 52-week price range (FLOAT)
- sector, industry: Classification (STRING) - stocks only

CURRENT CONTEXT:
- Asset Type: {asset_type}
- Period: {period}

TRADING TERMINOLOGY:
- "oversold" = RSI < 30
- "overbought" = RSI > 70
- "strong trend" = ADX > 25
- "bullish MACD" = MACD > MACD_SIGNAL and MACD > 0
- "bearish MACD" = MACD < MACD_SIGNAL and MACD < 0
- "breakout" = Close near or above week_52_high
- "breakdown" = Close near or below week_52_low
- "gainers" = percent_change > 0, sorted DESC
- "losers" = percent_change < 0, sorted ASC
- "high volume" = volume > average_volume * 1.5

USER QUERY: "{query}"

Generate a BigQuery SQL query that answers this question.
IMPORTANT:
1. Use fully qualified table names: `aialgotradehits.crypto_trading_data.table_name`
2. Always include ORDER BY and LIMIT clauses
3. Handle NULL values with IS NOT NULL or COALESCE
4. For latest data, use ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC)
5. Return ONLY the SQL, no explanations

SQL:"""

    def _extract_sql(self, response: str) -> str:
        """Extract SQL from model response"""
        # Remove markdown code blocks if present
        sql = re.sub(r'```sql?\n?', '', response)
        sql = re.sub(r'```', '', sql)
        sql = sql.strip()
        return sql

    def _validate_sql(self, sql: str) -> dict:
        """Validate SQL for safety and correctness"""
        if not sql:
            return {"valid": False, "error": "Empty SQL generated"}

        # Check for dangerous keywords
        dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'CREATE']
        sql_upper = sql.upper()
        for keyword in dangerous:
            if keyword in sql_upper:
                return {"valid": False, "error": f"Dangerous keyword: {keyword}"}

        # Ensure SELECT only
        if not sql_upper.strip().startswith('SELECT'):
            return {"valid": False, "error": "Only SELECT queries allowed"}

        # Validate table reference
        if 'aialgotradehits.crypto_trading_data' not in sql:
            return {"valid": False, "error": "Invalid table reference"}

        return {"valid": True, "sql": sql}

    def _extract_tables(self, sql: str) -> list:
        """Extract table names from SQL"""
        pattern = r'`aialgotradehits\.crypto_trading_data\.([^`]+)`'
        return re.findall(pattern, sql)

    def _generate_interpretation(self, query: str) -> str:
        """Generate human-readable interpretation of query"""
        prompt = f"""Briefly explain what this trading query is asking for:
Query: "{query}"
One sentence explanation:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return "Processing your trading query"

    def execute_sql(self, sql: str, limit: int = 100) -> dict:
        """Execute SQL and return results"""
        try:
            query_job = self.bq_client.query(sql)
            results = list(query_job.result())

            data = []
            for row in results[:limit]:
                row_dict = dict(row)
                # Convert special types
                for key, value in row_dict.items():
                    if hasattr(value, 'isoformat'):
                        row_dict[key] = value.isoformat()
                data.append(row_dict)

            return {
                "success": True,
                "data": data,
                "count": len(data),
                "total_rows": len(results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": []
            }


# Example usage
if __name__ == "__main__":
    agent = TextToSQLAgent()

    # Test queries
    test_queries = [
        "Show me oversold tech stocks",
        "Top 10 crypto gainers today",
        "Stocks with bullish MACD and strong trend",
        "Find high volume stocks breaking out"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        result = agent.generate_sql(query)
        print(f"SQL: {result.get('sql', 'N/A')[:200]}...")
        print(f"Tables: {result.get('tables_used', [])}")
```

---

## 5. Building the Market Scanner Agent

### 5.1 Scanner Configuration

```python
# market_scanner_agent.py

from google.cloud import bigquery
from typing import List, Dict, Any
import vertexai
from vertexai.generative_models import GenerativeModel

class MarketScannerAgent:
    """
    Scans markets for trading opportunities based on technical and fundamental criteria.
    """

    def __init__(self):
        self.project_id = "aialgotradehits"
        self.dataset_id = "crypto_trading_data"
        self.bq_client = bigquery.Client(project=self.project_id)
        self.model = GenerativeModel("gemini-2.5-flash")  # Fast model for scanning

    def scan(self, criteria: Dict[str, Any]) -> List[Dict]:
        """
        Scan assets based on criteria.

        Args:
            criteria: Dictionary with filter criteria
                - asset_type: stocks, crypto, forex, etc.
                - rsi_min, rsi_max: RSI range
                - adx_min: Minimum ADX for trend strength
                - macd_signal: bullish, bearish
                - volume_ratio: Minimum volume vs average
                - sector: Sector filter (stocks only)
                - sort_by: Column to sort by
                - limit: Number of results

        Returns:
            List of matching assets with scores
        """
        asset_type = criteria.get('asset_type', 'stocks')
        table = self._get_table_name(asset_type)

        where_clauses = self._build_where_clauses(criteria)
        order_by = self._build_order_by(criteria)
        limit = criteria.get('limit', 50)

        sql = f"""
        WITH latest_data AS (
            SELECT
                symbol,
                name,
                sector,
                close,
                percent_change,
                volume,
                average_volume,
                rsi,
                macd,
                macd_signal,
                adx,
                week_52_high,
                week_52_low,
                ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
            FROM `{self.project_id}.{self.dataset_id}.{table}`
            WHERE close IS NOT NULL
        )
        SELECT
            symbol,
            name,
            sector,
            close as price,
            percent_change,
            volume,
            rsi,
            macd,
            adx,
            (close / week_52_high * 100) as pct_of_52w_high
        FROM latest_data
        WHERE rn = 1
        {where_clauses}
        {order_by}
        LIMIT {limit}
        """

        try:
            results = list(self.bq_client.query(sql).result())
            return [dict(row) for row in results]
        except Exception as e:
            return [{"error": str(e)}]

    def _get_table_name(self, asset_type: str) -> str:
        """Map asset type to table name"""
        mapping = {
            'stocks': 'v2_stocks_daily',
            'crypto': 'v2_crypto_daily',
            'forex': 'v2_forex_daily',
            'etfs': 'v2_etfs_daily',
            'indices': 'v2_indices_daily',
            'commodities': 'v2_commodities_daily'
        }
        return mapping.get(asset_type, 'v2_stocks_daily')

    def _build_where_clauses(self, criteria: Dict) -> str:
        """Build WHERE clauses from criteria"""
        clauses = []

        if 'rsi_min' in criteria:
            clauses.append(f"rsi >= {criteria['rsi_min']}")
        if 'rsi_max' in criteria:
            clauses.append(f"rsi <= {criteria['rsi_max']}")
        if 'adx_min' in criteria:
            clauses.append(f"adx >= {criteria['adx_min']}")
        if criteria.get('macd_signal') == 'bullish':
            clauses.append("macd > macd_signal")
        if criteria.get('macd_signal') == 'bearish':
            clauses.append("macd < macd_signal")
        if 'volume_ratio' in criteria:
            clauses.append(f"volume > average_volume * {criteria['volume_ratio']}")
        if 'sector' in criteria:
            clauses.append(f"sector = '{criteria['sector']}'")
        if criteria.get('near_52w_high'):
            clauses.append("close >= week_52_high * 0.95")
        if criteria.get('near_52w_low'):
            clauses.append("close <= week_52_low * 1.05")

        if clauses:
            return "AND " + " AND ".join(clauses)
        return ""

    def _build_order_by(self, criteria: Dict) -> str:
        """Build ORDER BY clause"""
        sort_by = criteria.get('sort_by', 'percent_change')
        direction = criteria.get('sort_direction', 'DESC')
        return f"ORDER BY {sort_by} {direction} NULLS LAST"

    # Preset scans
    def scan_gainers(self, asset_type: str = 'stocks', limit: int = 20) -> List[Dict]:
        """Find top gainers"""
        return self.scan({
            'asset_type': asset_type,
            'sort_by': 'percent_change',
            'sort_direction': 'DESC',
            'limit': limit
        })

    def scan_losers(self, asset_type: str = 'stocks', limit: int = 20) -> List[Dict]:
        """Find top losers"""
        return self.scan({
            'asset_type': asset_type,
            'sort_by': 'percent_change',
            'sort_direction': 'ASC',
            'limit': limit
        })

    def scan_oversold(self, asset_type: str = 'stocks', limit: int = 20) -> List[Dict]:
        """Find oversold assets (RSI < 30)"""
        return self.scan({
            'asset_type': asset_type,
            'rsi_max': 30,
            'sort_by': 'rsi',
            'sort_direction': 'ASC',
            'limit': limit
        })

    def scan_overbought(self, asset_type: str = 'stocks', limit: int = 20) -> List[Dict]:
        """Find overbought assets (RSI > 70)"""
        return self.scan({
            'asset_type': asset_type,
            'rsi_min': 70,
            'sort_by': 'rsi',
            'sort_direction': 'DESC',
            'limit': limit
        })

    def scan_breakouts(self, asset_type: str = 'stocks', limit: int = 20) -> List[Dict]:
        """Find assets breaking 52-week highs"""
        return self.scan({
            'asset_type': asset_type,
            'near_52w_high': True,
            'volume_ratio': 1.5,
            'sort_by': 'percent_change',
            'sort_direction': 'DESC',
            'limit': limit
        })

    def scan_strong_trends(self, asset_type: str = 'stocks', limit: int = 20) -> List[Dict]:
        """Find assets with strong trends (ADX > 25)"""
        return self.scan({
            'asset_type': asset_type,
            'adx_min': 25,
            'macd_signal': 'bullish',
            'sort_by': 'adx',
            'sort_direction': 'DESC',
            'limit': limit
        })


# Example usage
if __name__ == "__main__":
    scanner = MarketScannerAgent()

    print("=== Top Stock Gainers ===")
    for stock in scanner.scan_gainers()[:5]:
        print(f"{stock['symbol']}: {stock['percent_change']:.2f}%")

    print("\n=== Oversold Stocks ===")
    for stock in scanner.scan_oversold()[:5]:
        print(f"{stock['symbol']}: RSI {stock['rsi']:.1f}")
```

---

## 6. Building the Master Orchestrator

### 6.1 Orchestrator Implementation

```python
# trading_orchestrator.py

import asyncio
from typing import Dict, List, Any
import vertexai
from vertexai.generative_models import GenerativeModel
import json
import re

class TradingOrchestrator:
    """
    Master orchestrator that routes queries to specialized agents
    and aggregates their responses.
    """

    def __init__(self):
        self.model = GenerativeModel("gemini-2.5-pro")
        self.agents = {
            'text_to_sql': TextToSQLAgent(),
            'market_scanner': MarketScannerAgent(),
        }

    async def process_query(self, query: str, context: Dict = None) -> Dict:
        """
        Process a user query through the agent system.

        Args:
            query: Natural language query from user
            context: Optional context (page, asset_type, period)

        Returns:
            Aggregated response from agents
        """
        context = context or {}

        # Step 1: Classify the query intent
        intent = await self._classify_intent(query)

        # Step 2: Route to appropriate agents
        agents_to_use = self._select_agents(intent)

        # Step 3: Execute agents
        agent_results = {}
        for agent_name in agents_to_use:
            if agent_name in self.agents:
                result = await self._execute_agent(agent_name, query, context)
                agent_results[agent_name] = result

        # Step 4: Aggregate and format response
        response = await self._aggregate_results(agent_results, query, intent)

        return response

    async def _classify_intent(self, query: str) -> Dict:
        """Classify the query intent using Gemini"""
        prompt = f"""Classify this trading query into categories.

Query: "{query}"

Categories (select all that apply):
1. DATA_QUERY - Retrieving specific data from database
2. MARKET_SCAN - Screening for assets matching criteria
3. TECHNICAL_ANALYSIS - Questions about indicators/patterns
4. COMPARISON - Comparing multiple assets
5. DEFINITION - Asking what something means
6. PREDICTION - Asking about future price/trend

Return JSON only:
{{"categories": ["CATEGORY1"], "primary": "CATEGORY1", "entities": {{"asset_type": "stocks", "symbols": [], "indicators": []}}}}"""

        response = self.model.generate_content(prompt)
        try:
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return {"categories": ["DATA_QUERY"], "primary": "DATA_QUERY", "entities": {}}

    def _select_agents(self, intent: Dict) -> List[str]:
        """Select agents based on intent"""
        mapping = {
            'DATA_QUERY': ['text_to_sql'],
            'MARKET_SCAN': ['market_scanner', 'text_to_sql'],
            'TECHNICAL_ANALYSIS': ['text_to_sql'],
            'COMPARISON': ['text_to_sql'],
            'DEFINITION': [],  # Handle with Gemini directly
            'PREDICTION': ['text_to_sql']
        }

        agents = set()
        for category in intent.get('categories', ['DATA_QUERY']):
            agents.update(mapping.get(category, ['text_to_sql']))

        return list(agents)

    async def _execute_agent(self, agent_name: str, query: str, context: Dict) -> Dict:
        """Execute a specific agent"""
        agent = self.agents.get(agent_name)
        if not agent:
            return {"error": f"Agent {agent_name} not found"}

        if agent_name == 'text_to_sql':
            result = agent.generate_sql(query, context)
            if result.get('success') and result.get('sql'):
                execution = agent.execute_sql(result['sql'])
                result['data'] = execution.get('data', [])
                result['count'] = execution.get('count', 0)
            return result

        elif agent_name == 'market_scanner':
            # Parse criteria from query
            if 'oversold' in query.lower():
                return {"data": agent.scan_oversold(), "scan_type": "oversold"}
            elif 'gainer' in query.lower():
                return {"data": agent.scan_gainers(), "scan_type": "gainers"}
            elif 'breakout' in query.lower():
                return {"data": agent.scan_breakouts(), "scan_type": "breakouts"}
            else:
                return {"data": agent.scan_gainers(), "scan_type": "default"}

        return {"error": "Unknown agent"}

    async def _aggregate_results(self, results: Dict, query: str, intent: Dict) -> Dict:
        """Aggregate results from multiple agents"""

        # Combine data from all agents
        all_data = []
        for agent_name, result in results.items():
            if 'data' in result and isinstance(result['data'], list):
                all_data.extend(result['data'])

        # Remove duplicates by symbol
        seen = set()
        unique_data = []
        for item in all_data:
            symbol = item.get('symbol', '')
            if symbol and symbol not in seen:
                seen.add(symbol)
                unique_data.append(item)

        # Generate summary
        summary = await self._generate_summary(query, unique_data)

        return {
            "success": True,
            "query": query,
            "intent": intent,
            "results": unique_data[:100],
            "count": len(unique_data),
            "summary": summary,
            "agents_used": list(results.keys())
        }

    async def _generate_summary(self, query: str, data: List[Dict]) -> str:
        """Generate natural language summary of results"""
        if not data:
            return "No matching assets found for your query."

        # Sample data for summary
        sample = data[:5]
        symbols = [d.get('symbol', 'N/A') for d in sample]
        avg_change = sum(d.get('percent_change', 0) for d in sample) / len(sample)

        prompt = f"""Summarize these trading search results in 2 sentences:

Query: {query}
Found: {len(data)} assets
Top symbols: {', '.join(symbols)}
Average change: {avg_change:.2f}%

Summary:"""

        response = self.model.generate_content(prompt)
        return response.text.strip()


# Cloud Function entry point
def process_trading_query(request):
    """Cloud Function handler for trading queries"""
    import asyncio

    request_json = request.get_json()
    query = request_json.get('query', '')
    context = request_json.get('context', {})

    orchestrator = TradingOrchestrator()
    result = asyncio.run(orchestrator.process_query(query, context))

    return result
```

---

## 7. Deployment to Cloud Functions

### 7.1 Cloud Function Configuration

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'functions'
      - 'deploy'
      - 'trading-orchestrator'
      - '--gen2'
      - '--runtime=python311'
      - '--region=us-central1'
      - '--source=.'
      - '--entry-point=process_trading_query'
      - '--trigger-http'
      - '--memory=2Gi'
      - '--timeout=300s'
      - '--allow-unauthenticated'
      - '--set-env-vars=GOOGLE_CLOUD_PROJECT=aialgotradehits'
```

### 7.2 Requirements

```text
# requirements.txt
google-cloud-aiplatform>=1.35.0
google-cloud-bigquery>=3.11.0
vertexai>=0.0.1
flask>=2.0.0
gunicorn>=21.0.0
pandas>=2.0.0
numpy>=1.24.0
```

---

## 8. Testing Agents

### 8.1 Unit Tests

```python
# test_agents.py

import pytest
from text_to_sql_agent import TextToSQLAgent
from market_scanner_agent import MarketScannerAgent

class TestTextToSQLAgent:

    def setup_method(self):
        self.agent = TextToSQLAgent()

    def test_simple_query(self):
        result = self.agent.generate_sql("Show me top 10 tech stocks")
        assert result['success'] == True
        assert 'SELECT' in result['sql']
        assert 'LIMIT' in result['sql']

    def test_oversold_query(self):
        result = self.agent.generate_sql("Find oversold stocks")
        assert result['success'] == True
        assert 'rsi' in result['sql'].lower()
        assert '30' in result['sql'] or '<' in result['sql']

    def test_dangerous_query_blocked(self):
        result = self.agent.generate_sql("DROP TABLE stocks")
        assert result['success'] == False
        assert 'Dangerous' in result.get('error', '')

class TestMarketScannerAgent:

    def setup_method(self):
        self.agent = MarketScannerAgent()

    def test_scan_gainers(self):
        results = self.agent.scan_gainers(limit=5)
        assert len(results) <= 5
        assert all('symbol' in r for r in results)

    def test_scan_oversold(self):
        results = self.agent.scan_oversold(limit=5)
        assert all(r.get('rsi', 100) < 30 for r in results if r.get('rsi'))

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## 9. Monitoring and Logging

### 9.1 Logging Configuration

```python
# logging_config.py

import google.cloud.logging
import structlog

def setup_logging():
    # Initialize Cloud Logging
    client = google.cloud.logging.Client()
    client.setup_logging()

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )

    return structlog.get_logger()

# Usage in agents
logger = setup_logging()

logger.info("agent_query_processed",
    agent="text_to_sql",
    query="oversold stocks",
    sql_generated=True,
    results_count=42,
    latency_ms=250
)
```

---

## 10. Next Steps

### 10.1 Roadmap

1. **Week 1-2:** Deploy Text-to-SQL and Market Scanner agents
2. **Week 3-4:** Add Technical Analysis agent
3. **Week 5-6:** Integrate Sentiment agent with Finnhub
4. **Week 7-8:** Build Predictive Analytics agent
5. **Month 3:** Add real-time data streaming and alerts

### 10.2 Resources

- [Vertex AI Agent Builder Documentation](https://cloud.google.com/vertex-ai/docs/agent-builder)
- [Gemini API Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)

---

*Document Version: 1.0*
*Last Updated: December 7, 2025*
