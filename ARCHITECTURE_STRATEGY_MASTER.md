# AIAlgoTradeHits - Master Architecture & Strategy Document

**Version:** 2.0
**Last Updated:** November 25, 2025
**Document Status:** AUTHORITATIVE - All implementation must follow this document

---

## Executive Summary

AIAlgoTradeHits is a professional-grade algorithmic trading intelligence platform built on three foundational pillars:

1. **Robust Data Collection** - Enterprise-grade data pipeline with 112+ technical indicators
2. **Interactive Professional Charting** - Institutional-quality visualization
3. **AI-Powered Smart Search** - Google Vertex AI with Gemini 2.0 for natural language queries

This document serves as the single source of truth for all architectural decisions and implementation standards.

---

## Table of Contents

1. [Core Architecture Principles](#1-core-architecture-principles)
2. [Data Collection Infrastructure](#2-data-collection-infrastructure)
3. [Technical Indicators Framework](#3-technical-indicators-framework)
4. [AI Smart Search Engine](#4-ai-smart-search-engine)
5. [Interactive Charting System](#5-interactive-charting-system)
6. [BigQuery Data Warehouse](#6-bigquery-data-warehouse)
7. [API Architecture](#7-api-architecture)
8. [Security & Compliance](#8-security--compliance)
9. [Performance Requirements](#9-performance-requirements)
10. [Implementation Roadmap](#10-implementation-roadmap)

---

## 1. Core Architecture Principles

### 1.1 Single Source of Truth
**ALL market data comes from TwelveData API ONLY.**
- No Kraken, Yahoo Finance, or other sources
- Ensures data consistency and reliability
- Simplifies maintenance and debugging
- Single API key management

### 1.2 Data Integrity First
- Every data point must be validated before storage
- Duplicate detection on all inserts
- Data quality checks on every pipeline run
- Audit trail for all data modifications

### 1.3 Scalability by Design
- Horizontal scaling for data collection
- Partitioned tables in BigQuery
- Cached API responses where appropriate
- Async processing for heavy operations

### 1.4 AI-Native Architecture
- All components designed with AI integration in mind
- Structured data optimized for LLM consumption
- Natural language interfaces throughout
- Continuous learning from user interactions

---

## 2. Data Collection Infrastructure

### 2.1 Asset Coverage Matrix

| Asset Type | Symbol Count | Example Symbols | Data Sources |
|------------|--------------|-----------------|--------------|
| Stocks | 500+ | AAPL, MSFT, GOOGL, NVDA, TSLA | US Exchanges |
| Crypto | 100+ | BTC/USD, ETH/USD, SOL/USD | Global Crypto |
| Forex | 50+ | EUR/USD, GBP/USD, USD/JPY | Forex Markets |
| ETFs | 200+ | SPY, QQQ, IWM, GLD, TLT | US ETF Markets |
| Indices | 30+ | SPX, NDX, DJI, VIX | Global Indices |
| Commodities | 20+ | GOLD, SILVER, OIL, NATGAS | Commodities |

**Total Coverage: 900+ Instruments**

### 2.2 Timeframe Matrix

| Timeframe | Update Frequency | Data Retention | Use Case |
|-----------|------------------|----------------|----------|
| Weekly | Sunday 11:59 PM ET | 10 years | Long-term trend analysis |
| Daily | 12:00 AM ET | 5 years | Swing trading, position analysis |
| Hourly | Every hour | 1 year | Short-term trading |
| 5-Minute | Every 5 min (market hours) | 90 days | Day trading, scalping |

### 2.3 Data Collection Pipeline Architecture

```
+-------------------+     +------------------+     +-------------------+
|   TwelveData API  | --> | Cloud Functions  | --> |    BigQuery       |
|   (Data Source)   |     | (Data Pipeline)  |     | (Data Warehouse)  |
+-------------------+     +------------------+     +-------------------+
                                  |
                                  v
                          +------------------+
                          | Data Validation  |
                          | - Schema check   |
                          | - Range check    |
                          | - Duplicate check|
                          +------------------+
```

### 2.4 Cloud Functions (24 Schedulers)

| Function Name | Schedule | Assets | Timeframe |
|---------------|----------|--------|-----------|
| stocks-weekly-fetcher | 0 23 * * 0 | Stocks | Weekly |
| stocks-daily-fetcher | 0 0 * * * | Stocks | Daily |
| stocks-hourly-fetcher | 0 * * * * | Stocks | Hourly |
| stocks-5min-fetcher | */5 9-16 * * 1-5 | Stocks | 5-Minute |
| crypto-weekly-fetcher | 0 23 * * 0 | Crypto | Weekly |
| crypto-daily-fetcher | 0 0 * * * | Crypto | Daily |
| crypto-hourly-fetcher | 0 * * * * | Crypto | Hourly |
| crypto-5min-fetcher | */5 * * * * | Crypto | 5-Minute |
| forex-weekly-fetcher | 0 23 * * 0 | Forex | Weekly |
| forex-daily-fetcher | 0 0 * * * | Forex | Daily |
| forex-hourly-fetcher | 0 * * * * | Forex | Hourly |
| forex-5min-fetcher | */5 * * * 1-5 | Forex | 5-Minute |
| etfs-weekly-fetcher | 0 23 * * 0 | ETFs | Weekly |
| etfs-daily-fetcher | 0 0 * * * | ETFs | Daily |
| etfs-hourly-fetcher | 0 * * * * | ETFs | Hourly |
| etfs-5min-fetcher | */5 9-16 * * 1-5 | ETFs | 5-Minute |
| indices-weekly-fetcher | 0 23 * * 0 | Indices | Weekly |
| indices-daily-fetcher | 0 0 * * * | Indices | Daily |
| indices-hourly-fetcher | 0 * * * * | Indices | Hourly |
| indices-5min-fetcher | */5 9-16 * * 1-5 | Indices | 5-Minute |
| commodities-weekly-fetcher | 0 23 * * 0 | Commodities | Weekly |
| commodities-daily-fetcher | 0 0 * * * | Commodities | Daily |
| commodities-hourly-fetcher | 0 * * * * | Commodities | Hourly |
| commodities-5min-fetcher | */5 9-16 * * 1-5 | Commodities | 5-Minute |

### 2.5 Data Validation Rules

```python
VALIDATION_RULES = {
    'price_fields': {
        'open': {'min': 0, 'max': 1000000, 'required': True},
        'high': {'min': 0, 'max': 1000000, 'required': True},
        'low': {'min': 0, 'max': 1000000, 'required': True},
        'close': {'min': 0, 'max': 1000000, 'required': True},
        'volume': {'min': 0, 'max': 1e15, 'required': True},
    },
    'ohlc_integrity': {
        'high >= low': True,
        'high >= open': True,
        'high >= close': True,
        'low <= open': True,
        'low <= close': True,
    },
    'indicator_ranges': {
        'rsi': {'min': 0, 'max': 100},
        'adx': {'min': 0, 'max': 100},
        'stoch_k': {'min': 0, 'max': 100},
        'stoch_d': {'min': 0, 'max': 100},
        'willr': {'min': -100, 'max': 0},
        'mfi': {'min': 0, 'max': 100},
        'cci': {'min': -500, 'max': 500},  # Typical range
    }
}
```

### 2.6 Error Handling & Recovery

| Error Type | Detection | Recovery Action |
|------------|-----------|-----------------|
| API Rate Limit | HTTP 429 | Exponential backoff, retry after delay |
| API Timeout | Timeout exception | Retry 3x with increasing timeout |
| Invalid Data | Validation failure | Log, skip record, alert |
| Duplicate Data | Primary key conflict | Skip insert, log |
| Missing Data | Gap detection | Backfill job triggered |
| Schema Mismatch | Type error | Transform or reject |

---

## 3. Technical Indicators Framework

### 3.1 Complete Indicator List (112 Indicators)

All indicators are fetched directly from TwelveData API to ensure accuracy and consistency.

#### Trend Indicators (22)
1. SMA (5, 10, 20, 50, 100, 200)
2. EMA (5, 10, 12, 20, 26, 50, 100, 200)
3. WMA (20)
4. DEMA (20)
5. TEMA (20)
6. KAMA (20)
7. T3MA (20)
8. TRIMA (20)
9. VWAP
10. MAMA
11. MCGINLEY_DYNAMIC
12. HT_TRENDLINE
13. ICHIMOKU (Tenkan, Kijun, Senkou A, Senkou B, Chikou)
14. SAR
15. SAREXT
16. MIDPOINT
17. MIDPRICE
18. BBANDS (Upper, Middle, Lower)
19. KELTNER (Upper, Middle, Lower)
20. PIVOT_POINTS_HL
21. LINEARREG
22. TSF

#### Momentum Indicators (34)
23. RSI (7, 14, 21)
24. MACD (Line, Signal, Histogram)
25. MACD_SLOPE
26. MACDEXT
27. STOCH (K, D)
28. STOCHF
29. STOCHRSI (K, D)
30. ADX (14)
31. ADXR
32. DX
33. PLUS_DI
34. MINUS_DI
35. PLUS_DM
36. MINUS_DM
37. CCI (14, 20)
38. CMO
39. MOM
40. ROC
41. ROCP
42. ROCR
43. ROCR100
44. WILLR
45. MFI
46. ULTOSC
47. PPO
48. APO
49. BOP
50. AROON (Up, Down)
51. AROONOSC
52. COPPOCK
53. KST
54. CRSI
55. DPO
56. PERCENT_B

#### Volume Indicators (4)
57. OBV
58. AD
59. ADOSC
60. RVOL

#### Volatility Indicators (5)
61. ATR (14)
62. NATR
63. TRANGE
64. SUPERTREND
65. SUPERTREND_HEIKINASHI

#### Cycle Indicators (5)
66. HT_DCPERIOD
67. HT_DCPHASE
68. HT_PHASOR
69. HT_SINE
70. HT_TRENDMODE

#### Price Transform (6)
71. AVGPRICE
72. MEDPRICE
73. TYPPRICE
74. WCLPRICE
75. HLC3
76. HEIKINASHICANDLES

#### Statistical Functions (9)
77. STDDEV
78. VAR
79. BETA
80. CORREL
81. LINEARREG_SLOPE
82. LINEARREG_ANGLE
83. LINEARREG_INTERCEPT
84. MAX/MIN/MINMAX
85. TSF

#### Math Functions (27)
86-112. ADD, SUB, MULT, DIV, SUM, AVG, SQRT, LN, LOG10, EXP, CEIL, FLOOR, ACOS, ASIN, ATAN, COS, COSH, SIN, SINH, TAN, TANH, MAX, MAXINDEX, MIN, MININDEX, MINMAX, MINMAXINDEX

### 3.2 Indicator Calculation Standards

```python
INDICATOR_DEFAULTS = {
    # Moving Averages
    'sma_periods': [5, 10, 20, 50, 100, 200],
    'ema_periods': [5, 10, 12, 20, 26, 50, 100, 200],

    # Momentum
    'rsi_period': 14,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'stoch_k': 14,
    'stoch_d': 3,

    # Trend
    'adx_period': 14,
    'cci_period': 20,

    # Volatility
    'atr_period': 14,
    'bbands_period': 20,
    'bbands_stddev': 2,

    # Ichimoku
    'ichimoku_tenkan': 9,
    'ichimoku_kijun': 26,
    'ichimoku_senkou_b': 52,
}
```

---

## 4. AI Smart Search Engine

### 4.1 Architecture Overview

The AI Smart Search is the **flagship feature** of AIAlgoTradeHits, powered by Google Vertex AI with Gemini 2.0 Pro.

```
+------------------+     +-------------------+     +------------------+
|   User Input     | --> |  Voice/Text       | --> |  Query Parser    |
| (Voice or Text)  |     |  Recognition      |     |  (NLP Prep)      |
+------------------+     +-------------------+     +------------------+
                                                           |
                                                           v
+------------------+     +-------------------+     +------------------+
|   Results        | <-- |  Response         | <-- |  Vertex AI       |
|   Display        |     |  Formatter        |     |  Gemini 2.0      |
+------------------+     +-------------------+     +------------------+
                                                           |
                                                           v
                                                  +------------------+
                                                  |   BigQuery       |
                                                  |   (SQL Gen)      |
                                                  +------------------+
```

### 4.2 Google Vertex AI Integration

#### 4.2.1 Model Selection
- **Primary Model:** Gemini 2.0 Pro (gemini-2.0-pro)
- **Fallback Model:** Gemini 1.5 Flash (for simple queries)
- **Region:** us-central1
- **Project:** aialgotradehits

#### 4.2.2 Vertex AI Configuration

```python
VERTEX_AI_CONFIG = {
    'project_id': 'aialgotradehits',
    'location': 'us-central1',
    'model_id': 'gemini-2.0-pro',
    'temperature': 0.1,  # Low for accuracy
    'max_output_tokens': 8192,
    'top_p': 0.95,
    'top_k': 40,
    'safety_settings': {
        'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
        'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
        'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
        'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
    }
}
```

### 4.3 Smart Search Capabilities

#### 4.3.1 Query Types Supported

| Query Type | Example | AI Processing |
|------------|---------|---------------|
| **Simple Lookup** | "Show me AAPL" | Direct symbol search |
| **Indicator Filter** | "Stocks with RSI below 30" | SQL generation with WHERE clause |
| **Multi-Condition** | "Tech stocks RSI < 30 AND MACD bullish crossover" | Complex SQL with JOINs |
| **Comparative** | "Compare AAPL vs MSFT momentum" | Side-by-side analysis |
| **Trend Analysis** | "Which cryptos are trending up this week?" | Trend detection algorithms |
| **Pattern Recognition** | "Find double bottom patterns in S&P 500" | Pattern matching queries |
| **Sector Analysis** | "Best performing tech stocks today" | Sector classification + ranking |
| **Correlation** | "What correlates with Bitcoin?" | Correlation matrix analysis |
| **Anomaly Detection** | "Unusual volume in any stock today" | Statistical anomaly detection |
| **Prediction Request** | "What's the outlook for NVDA?" | AI-powered analysis summary |

#### 4.3.2 Natural Language Understanding Examples

```
USER: "Show me oversold tech stocks with increasing volume"

AI PARSING:
- Asset Type: Stocks
- Sector Filter: Technology
- Indicator Condition 1: RSI < 30 (oversold)
- Indicator Condition 2: Volume > SMA(Volume, 20) (increasing volume)
- Sort: By RSI ascending (most oversold first)

GENERATED SQL:
SELECT symbol, close, rsi_14, volume, volume_sma_20,
       ((volume - volume_sma_20) / volume_sma_20 * 100) as volume_change_pct
FROM `aialgotradehits.crypto_trading_data.stocks_daily`
WHERE sector = 'Technology'
  AND rsi_14 < 30
  AND volume > volume_sma_20
  AND datetime = (SELECT MAX(datetime) FROM `aialgotradehits.crypto_trading_data.stocks_daily`)
ORDER BY rsi_14 ASC
LIMIT 20;
```

#### 4.3.3 Complex Query Examples

**Example 1: Multi-Asset Momentum Scan**
```
USER: "Find the top 10 assets across all markets with strongest bullish momentum"

AI ANALYSIS:
- Bullish momentum criteria:
  - RSI between 50-70 (strong but not overbought)
  - MACD histogram positive and increasing
  - Price above 50-day EMA
  - ADX > 25 (strong trend)
- Search across: Stocks, Crypto, Forex, ETFs, Indices, Commodities
- Rank by composite momentum score
```

**Example 2: Risk Analysis**
```
USER: "Which of my watchlist stocks have the highest volatility risk?"

AI ANALYSIS:
- Retrieve user's watchlist
- Calculate for each:
  - ATR as percentage of price
  - Standard deviation of returns
  - Beta relative to market
  - VIX correlation
- Rank by composite risk score
- Provide risk assessment summary
```

**Example 3: Trading Opportunity Detection**
```
USER: "Find me potential swing trading opportunities in crypto"

AI ANALYSIS:
- Identify cryptos with:
  - Recent pullback to support (price near lower Bollinger Band)
  - RSI showing bullish divergence
  - Volume declining on pullback (healthy correction)
  - Overall trend still bullish (above 200 EMA)
- Generate entry, stop-loss, and target levels
- Calculate risk/reward ratio
```

### 4.4 AI Response Framework

#### 4.4.1 Response Structure

```json
{
  "query_understanding": {
    "original_query": "string",
    "interpreted_intent": "string",
    "confidence_score": 0.95,
    "entities_extracted": {
      "asset_types": ["stocks"],
      "symbols": ["AAPL", "MSFT"],
      "indicators": ["RSI", "MACD"],
      "conditions": ["RSI < 30", "MACD > 0"],
      "timeframe": "daily",
      "limit": 20
    }
  },
  "sql_generated": "SELECT ...",
  "results": {
    "count": 15,
    "data": [...],
    "summary": "Found 15 oversold tech stocks..."
  },
  "ai_insights": {
    "market_context": "string",
    "key_observations": ["observation1", "observation2"],
    "risk_factors": ["risk1", "risk2"],
    "suggested_actions": ["action1", "action2"]
  },
  "follow_up_suggestions": [
    "Would you like to see the charts for these stocks?",
    "Want me to set up alerts when RSI crosses above 30?"
  ]
}
```

#### 4.4.2 AI Prompt Engineering

```python
SYSTEM_PROMPT = """
You are an expert financial analyst and trading assistant for AIAlgoTradeHits platform.

YOUR CAPABILITIES:
1. Analyze market data across 6 asset types: Stocks, Crypto, Forex, ETFs, Indices, Commodities
2. Access to 112 technical indicators for each asset
3. Generate BigQuery SQL queries to retrieve precise data
4. Provide institutional-grade market analysis

DATA SCHEMA CONTEXT:
{schema_context}

AVAILABLE INDICATORS:
{indicators_list}

CURRENT MARKET CONTEXT:
- Date: {current_date}
- Market Status: {market_status}
- Major Indices: {indices_summary}

RESPONSE GUIDELINES:
1. Always be precise with numbers - never approximate
2. Cite specific indicator values when making claims
3. Acknowledge uncertainty when data is insufficient
4. Provide actionable insights, not just data
5. Consider risk factors in all recommendations
6. Use professional financial terminology
7. Format responses for easy scanning

SQL GENERATION RULES:
1. Always use fully qualified table names
2. Include datetime filters for recent data
3. Handle NULL values appropriately
4. Optimize queries for performance
5. Limit results appropriately (default 20)
"""
```

### 4.5 Voice Input Processing

#### 4.5.1 Speech Recognition Pipeline

```
+------------------+     +-------------------+     +------------------+
|   Microphone     | --> |  Web Speech API   | --> |  Text Cleaning   |
|   Input          |     |  (Browser)        |     |  & Normalization |
+------------------+     +-------------------+     +------------------+
                                                           |
                                                           v
+------------------+     +-------------------+     +------------------+
|   AI Smart       | <-- |  Financial        | <-- |  Entity          |
|   Search         |     |  Term Mapping     |     |  Recognition     |
+------------------+     +-------------------+     +------------------+
```

#### 4.5.2 Financial Vocabulary Recognition

```javascript
FINANCIAL_VOCABULARY = {
  // Indicator aliases
  "our aside": "RSI",
  "are as I": "RSI",
  "Mac D": "MACD",
  "mac dee": "MACD",
  "bollinger": "BBANDS",
  "stochastic": "STOCH",

  // Asset aliases
  "apple": "AAPL",
  "microsoft": "MSFT",
  "bitcoin": "BTC/USD",
  "ethereum": "ETH/USD",
  "gold": "XAU/USD",

  // Condition aliases
  "oversold": "RSI < 30",
  "overbought": "RSI > 70",
  "bullish": "trend = 'up'",
  "bearish": "trend = 'down'",
  "golden cross": "SMA_50 > SMA_200 AND prev_SMA_50 < prev_SMA_200",
  "death cross": "SMA_50 < SMA_200 AND prev_SMA_50 > prev_SMA_200",
}
```

### 4.6 Search History & Learning

#### 4.6.1 Search Analytics Table

```sql
CREATE TABLE `aialgotradehits.crypto_trading_data.search_analytics` (
  search_id STRING NOT NULL,
  user_id STRING NOT NULL,
  query_text STRING NOT NULL,
  query_type STRING,  -- simple, filter, complex, pattern, etc.
  parsed_intent JSON,
  sql_generated STRING,
  result_count INT64,
  execution_time_ms INT64,
  user_feedback STRING,  -- helpful, not_helpful, null
  clicked_results JSON,
  session_id STRING,
  device_type STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

#### 4.6.2 Continuous Learning

The AI system improves over time by:
1. Analyzing successful queries (high click-through rate)
2. Learning from user feedback
3. Identifying common query patterns
4. Optimizing SQL generation based on performance
5. Expanding financial vocabulary from user inputs

---

## 5. Interactive Charting System

### 5.1 Charting Library Selection

**Primary Library:** TradingView Lightweight Charts v4.x
- Open source, lightweight (~40KB)
- Professional appearance
- Excellent performance
- Mobile responsive
- Active development

**Supplementary:** Custom WebGL renderer for advanced visualizations

### 5.2 Chart Types Supported

| Chart Type | Use Case | Implementation |
|------------|----------|----------------|
| Candlestick | Primary price display | Lightweight Charts |
| OHLC Bars | Alternative price display | Lightweight Charts |
| Line | Simple price/indicator | Lightweight Charts |
| Area | Volume, filled indicators | Lightweight Charts |
| Histogram | MACD, Volume | Lightweight Charts |
| Heikin-Ashi | Trend clarity | Custom transform |
| Renko | Noise reduction | Custom calculation |
| Point & Figure | Support/Resistance | Custom calculation |

### 5.3 Indicator Overlays

#### 5.3.1 Price Overlays (Same Pane)
- Moving Averages (SMA, EMA, WMA, etc.)
- Bollinger Bands
- Keltner Channels
- Ichimoku Cloud
- Pivot Points
- Parabolic SAR

#### 5.3.2 Separate Pane Indicators
- RSI
- MACD
- Stochastic
- ADX
- CCI
- Volume
- OBV
- ATR

### 5.4 Drawing Tools

| Tool | Description |
|------|-------------|
| Trend Line | Connect highs/lows for trend identification |
| Horizontal Line | Support/Resistance levels |
| Vertical Line | Time markers |
| Ray | Infinite trend projection |
| Channel | Parallel trend lines |
| Fibonacci Retracement | Key retracement levels |
| Fibonacci Extension | Price targets |
| Rectangle | Zone highlighting |
| Text Annotation | Notes and labels |
| Price Range | Measure price movement |
| Date Range | Measure time duration |

### 5.5 Chart Interaction Features

```javascript
CHART_FEATURES = {
  zoom: {
    mouse_wheel: true,
    pinch_touch: true,
    double_click_reset: true,
    zoom_limits: { min: '1D', max: '10Y' }
  },
  pan: {
    mouse_drag: true,
    touch_drag: true,
    keyboard_arrows: true
  },
  crosshair: {
    mode: 'magnet',  // snaps to candles
    show_price: true,
    show_time: true
  },
  tooltip: {
    show_ohlcv: true,
    show_indicators: true,
    show_change: true
  },
  timeframe_selector: {
    options: ['1m', '5m', '15m', '30m', '1h', '4h', '1D', '1W', '1M'],
    default: '1D'
  },
  chart_type_selector: {
    options: ['candle', 'ohlc', 'line', 'area', 'heikin-ashi'],
    default: 'candle'
  }
}
```

### 5.6 Multi-Chart Layouts

```
Layout Options:
+-------------------+     +--------+--------+     +--------+--------+
|                   |     |        |        |     |        |        |
|   Single Chart    |     |   2x1  |  Grid  |     |   2x2  |  Grid  |
|                   |     |        |        |     +--------+--------+
+-------------------+     +--------+--------+     |        |        |
                                                  +--------+--------+

+--------+--------+--------+     +-------------------+
|        |        |        |     |                   |
|   3x1  |  Grid  |        |     |   Main Chart      |
|        |        |        |     +--------+----------+
+--------+--------+--------+     | Mini 1 | Mini 2   |
                                 +--------+----------+
```

### 5.7 Real-Time Updates

For intraday timeframes, charts update in real-time:

```javascript
REALTIME_CONFIG = {
  update_interval_ms: 1000,  // 1 second
  data_source: 'websocket',  // or 'polling'
  reconnect_attempts: 5,
  reconnect_delay_ms: 3000,
  show_connection_status: true,
  buffer_size: 100  // candles to buffer
}
```

---

## 6. BigQuery Data Warehouse

### 6.1 Dataset Structure

```
aialgotradehits.crypto_trading_data/
├── Core Data Tables (24)
│   ├── stocks_weekly
│   ├── stocks_daily
│   ├── stocks_hourly
│   ├── stocks_5min
│   ├── crypto_weekly
│   ├── crypto_daily
│   ├── crypto_hourly
│   ├── crypto_5min
│   ├── forex_weekly
│   ├── forex_daily
│   ├── forex_hourly
│   ├── forex_5min
│   ├── etfs_weekly
│   ├── etfs_daily
│   ├── etfs_hourly
│   ├── etfs_5min
│   ├── indices_weekly
│   ├── indices_daily
│   ├── indices_hourly
│   ├── indices_5min
│   ├── commodities_weekly
│   ├── commodities_daily
│   ├── commodities_hourly
│   └── commodities_5min
│
├── Reference Tables
│   ├── symbols_master
│   ├── indicator_metadata
│   ├── sectors
│   └── exchanges
│
├── User Tables
│   ├── users
│   ├── watchlists
│   ├── alerts
│   └── portfolios
│
└── Analytics Tables
    ├── search_history
    ├── search_analytics
    └── user_activity
```

### 6.2 Core Table Schema (Example: stocks_daily)

```sql
CREATE TABLE `aialgotradehits.crypto_trading_data.stocks_daily` (
  -- Primary Key
  id STRING NOT NULL,

  -- Symbol Info
  symbol STRING NOT NULL,
  name STRING,
  exchange STRING,
  sector STRING,
  industry STRING,

  -- Timestamp
  datetime TIMESTAMP NOT NULL,
  date DATE,

  -- OHLCV
  open FLOAT64 NOT NULL,
  high FLOAT64 NOT NULL,
  low FLOAT64 NOT NULL,
  close FLOAT64 NOT NULL,
  volume FLOAT64,

  -- Moving Averages
  sma_5 FLOAT64,
  sma_10 FLOAT64,
  sma_20 FLOAT64,
  sma_50 FLOAT64,
  sma_100 FLOAT64,
  sma_200 FLOAT64,
  ema_5 FLOAT64,
  ema_10 FLOAT64,
  ema_12 FLOAT64,
  ema_20 FLOAT64,
  ema_26 FLOAT64,
  ema_50 FLOAT64,
  ema_100 FLOAT64,
  ema_200 FLOAT64,
  wma_20 FLOAT64,
  dema_20 FLOAT64,
  tema_20 FLOAT64,
  kama_20 FLOAT64,
  vwap FLOAT64,

  -- Momentum Indicators
  rsi_14 FLOAT64,
  rsi_7 FLOAT64,
  rsi_21 FLOAT64,
  macd_line FLOAT64,
  macd_signal FLOAT64,
  macd_histogram FLOAT64,
  stoch_k FLOAT64,
  stoch_d FLOAT64,
  stochrsi_k FLOAT64,
  stochrsi_d FLOAT64,
  willr_14 FLOAT64,
  cci_14 FLOAT64,
  cci_20 FLOAT64,
  mfi_14 FLOAT64,
  mom_10 FLOAT64,
  roc_10 FLOAT64,
  cmo_14 FLOAT64,
  ultosc FLOAT64,
  ppo_line FLOAT64,
  ppo_signal FLOAT64,
  apo FLOAT64,
  bop FLOAT64,

  -- Trend Indicators
  adx_14 FLOAT64,
  adxr_14 FLOAT64,
  dx_14 FLOAT64,
  plus_di FLOAT64,
  minus_di FLOAT64,
  aroon_up FLOAT64,
  aroon_down FLOAT64,
  aroon_osc FLOAT64,

  -- Volatility Indicators
  atr_14 FLOAT64,
  natr_14 FLOAT64,
  trange FLOAT64,
  bbands_upper FLOAT64,
  bbands_middle FLOAT64,
  bbands_lower FLOAT64,
  bbands_bandwidth FLOAT64,
  percent_b FLOAT64,
  keltner_upper FLOAT64,
  keltner_middle FLOAT64,
  keltner_lower FLOAT64,
  supertrend FLOAT64,
  supertrend_direction INT64,

  -- Volume Indicators
  obv FLOAT64,
  ad FLOAT64,
  adosc FLOAT64,
  rvol FLOAT64,

  -- Ichimoku
  ichimoku_tenkan FLOAT64,
  ichimoku_kijun FLOAT64,
  ichimoku_senkou_a FLOAT64,
  ichimoku_senkou_b FLOAT64,
  ichimoku_chikou FLOAT64,

  -- Statistics
  stddev_20 FLOAT64,
  variance_20 FLOAT64,
  linearreg FLOAT64,
  linearreg_slope FLOAT64,
  linearreg_angle FLOAT64,

  -- Derived Metrics
  change_pct FLOAT64,
  range_pct FLOAT64,
  body_pct FLOAT64,
  upper_shadow_pct FLOAT64,
  lower_shadow_pct FLOAT64,

  -- Trend Classification (AI-derived)
  trend_short STRING,  -- 'up', 'down', 'sideways'
  trend_medium STRING,
  trend_long STRING,

  -- Signal Flags (AI-derived)
  is_oversold BOOL,
  is_overbought BOOL,
  is_bullish_divergence BOOL,
  is_bearish_divergence BOOL,
  is_golden_cross BOOL,
  is_death_cross BOOL,

  -- Metadata
  data_source STRING DEFAULT 'twelvedata',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY date
CLUSTER BY symbol, sector;
```

### 6.3 Indexing Strategy

```sql
-- Clustered columns for common query patterns
CLUSTER BY symbol, sector;  -- For symbol lookups and sector analysis

-- Partitioning for date-based queries
PARTITION BY date;  -- Efficient date range queries

-- Materialized views for common aggregations
CREATE MATERIALIZED VIEW `aialgotradehits.crypto_trading_data.stocks_daily_latest` AS
SELECT *
FROM `aialgotradehits.crypto_trading_data.stocks_daily`
WHERE date = (SELECT MAX(date) FROM `aialgotradehits.crypto_trading_data.stocks_daily`);
```

---

## 7. API Architecture

### 7.1 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search` | POST | AI-powered smart search |
| `/api/symbols` | GET | List all symbols |
| `/api/symbols/{symbol}` | GET | Symbol details |
| `/api/quotes/{symbol}` | GET | Current quote |
| `/api/history/{symbol}` | GET | Historical data |
| `/api/indicators/{symbol}` | GET | All indicators |
| `/api/scan` | POST | Filtered asset scan |
| `/api/compare` | POST | Compare multiple assets |
| `/api/alerts` | GET/POST | User alerts |
| `/api/watchlist` | GET/POST | User watchlists |

### 7.2 Request/Response Format

```javascript
// POST /api/search
REQUEST:
{
  "query": "oversold tech stocks with high volume",
  "asset_types": ["stocks"],  // optional filter
  "timeframe": "daily",
  "limit": 20,
  "include_ai_insights": true
}

RESPONSE:
{
  "success": true,
  "query_id": "uuid",
  "execution_time_ms": 245,
  "results": {
    "count": 15,
    "data": [
      {
        "symbol": "INTC",
        "name": "Intel Corporation",
        "close": 45.23,
        "change_pct": -2.34,
        "volume": 45678900,
        "rsi_14": 28.5,
        "macd_histogram": -0.45,
        // ... more indicators
      }
    ]
  },
  "ai_insights": {
    "summary": "Found 15 tech stocks showing oversold conditions...",
    "key_findings": [...],
    "risk_warnings": [...],
    "suggested_actions": [...]
  },
  "metadata": {
    "data_as_of": "2025-11-25T16:00:00Z",
    "sql_generated": "SELECT ..."
  }
}
```

### 7.3 Rate Limiting

| User Tier | Requests/Min | Requests/Day |
|-----------|--------------|--------------|
| Free | 10 | 100 |
| Basic | 60 | 1,000 |
| Pro | 300 | 10,000 |
| Enterprise | Unlimited | Unlimited |

---

## 8. Security & Compliance

### 8.1 Authentication

- **Method:** Firebase Authentication
- **Supported:** Email/Password, Google OAuth, Apple Sign-In
- **Session:** JWT tokens with 1-hour expiry
- **Refresh:** Automatic token refresh

### 8.2 Data Security

| Layer | Protection |
|-------|------------|
| Transport | TLS 1.3 encryption |
| Storage | AES-256 encryption at rest |
| API Keys | Encrypted in Secret Manager |
| User Data | PII encryption, GDPR compliant |
| Access | IAM-based role permissions |

### 8.3 Compliance

- GDPR compliance for EU users
- SOC 2 Type II (planned)
- No storage of actual trading credentials
- No execution of trades (data/analysis only)

---

## 9. Performance Requirements

### 9.1 Response Time SLAs

| Operation | Target | Maximum |
|-----------|--------|---------|
| Simple Search | 200ms | 500ms |
| Complex AI Search | 1s | 3s |
| Chart Data Load | 300ms | 1s |
| Indicator Calculation | 100ms | 500ms |
| Export (1000 rows) | 2s | 5s |

### 9.2 Availability

- **Target:** 99.9% uptime
- **Planned Maintenance:** Sunday 2-4 AM ET
- **Data Freshness:** Within 5 minutes of source

### 9.3 Scalability Targets

| Metric | Current | Year 1 Target |
|--------|---------|---------------|
| Concurrent Users | 100 | 10,000 |
| Queries/Second | 10 | 1,000 |
| Data Points | 10M | 1B |
| Storage | 10GB | 1TB |

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
- [ ] BigQuery schema creation (all 24 tables)
- [ ] TwelveData data pipeline (all 24 fetchers)
- [ ] Data validation framework
- [ ] Basic API endpoints
- [ ] Initial data backfill

### Phase 2: Core Features (Weeks 5-8)
- [ ] Interactive charting (Lightweight Charts)
- [ ] Indicator overlays (top 20 indicators)
- [ ] Basic search functionality
- [ ] Symbol lookup and quotes
- [ ] User authentication

### Phase 3: AI Integration (Weeks 9-12)
- [ ] Vertex AI setup and configuration
- [ ] Smart Search natural language parsing
- [ ] SQL generation from queries
- [ ] AI insights generation
- [ ] Voice input support

### Phase 4: Advanced Features (Weeks 13-16)
- [ ] Advanced charting (drawing tools)
- [ ] Multi-chart layouts
- [ ] Watchlists and alerts
- [ ] Portfolio tracking
- [ ] Export functionality

### Phase 5: Optimization (Weeks 17-20)
- [ ] Performance optimization
- [ ] Caching layer
- [ ] Search result ranking
- [ ] Mobile optimization
- [ ] User feedback integration

---

## Appendix A: TwelveData API Reference

**Base URL:** `https://api.twelvedata.com`
**API Key:** `16ee060fd4d34a628a14bcb6f0167565`

### Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/time_series` | OHLCV data |
| `/quote` | Current price |
| `/technical_indicators` | List all indicators |
| `/{indicator}` | Specific indicator data |
| `/stocks` | Stock symbols |
| `/cryptocurrencies` | Crypto symbols |
| `/forex_pairs` | Forex pairs |
| `/etf` | ETF symbols |
| `/indices` | Index symbols |
| `/commodities` | Commodity symbols |

---

## Appendix B: GCP Project Details

| Resource | Value |
|----------|-------|
| Project ID | aialgotradehits |
| Region | us-central1 |
| BigQuery Dataset | crypto_trading_data |
| Cloud Functions Runtime | Python 3.11 |
| Cloud Run Region | us-central1 |
| Vertex AI Region | us-central1 |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Nov 24, 2025 | System | Initial document |
| 2.0 | Nov 25, 2025 | System | Major expansion: AI Smart Search, Charting, Full architecture |

**This document is the authoritative source for all architectural decisions. Any implementation that deviates from this document requires explicit approval.**
