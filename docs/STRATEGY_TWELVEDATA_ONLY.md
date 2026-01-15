# AIAlgoTradeHits - TwelveData Architecture & Strategy Document

**Version:** 2.0
**Last Updated:** November 25, 2025
**Document Status:** AUTHORITATIVE - All implementation must follow this document

---

## Executive Summary

AIAlgoTradeHits is a professional-grade algorithmic trading intelligence platform built on three foundational pillars:

1. **Robust Data Collection** - Enterprise-grade data pipeline with 112+ technical indicators
2. **Interactive Professional Charting** - Institutional-quality visualization
3. **AI-Powered Smart Search** - Google Vertex AI with Gemini 2.0 for natural language queries

---

## Core Principle

**ALL market data comes from TwelveData API ONLY. No Kraken, no Yahoo Finance, no other sources.**

This ensures:
- Data consistency and reliability
- Single source of truth
- Simplified maintenance and debugging
- Single API key management

---

## Table of Contents

1. [Data Architecture](#1-data-architecture)
2. [Robust Data Collection Infrastructure](#2-robust-data-collection-infrastructure)
3. [Technical Indicators Framework (112 Indicators)](#3-technical-indicators-framework-112-indicators)
4. [AI Smart Search Engine (Vertex AI + Gemini)](#4-ai-smart-search-engine-vertex-ai--gemini)
5. [Interactive Professional Charting](#5-interactive-professional-charting)
6. [BigQuery Data Warehouse](#6-bigquery-data-warehouse)
7. [API Architecture](#7-api-architecture)
8. [Cloud Functions & Schedulers](#8-cloud-functions--schedulers)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [Project Configuration](#10-project-configuration)

---

## 1. Data Architecture

### 1.1 Six Asset Types (All from TwelveData)

| Asset Type | Symbol Count | Examples | Markets |
|------------|--------------|----------|---------|
| **Stocks** | 500+ | AAPL, MSFT, GOOGL, NVDA, TSLA | US Exchanges |
| **Crypto** | 100+ | BTC/USD, ETH/USD, SOL/USD | Global Crypto |
| **Forex** | 50+ | EUR/USD, GBP/USD, USD/JPY | Forex Markets |
| **ETFs** | 200+ | SPY, QQQ, IWM, GLD, TLT | US ETF Markets |
| **Indices** | 30+ | SPX, NDX, DJI, VIX | Global Indices |
| **Commodities** | 20+ | GOLD, SILVER, OIL, NATGAS | Commodities |

**Total Coverage: 900+ Instruments**

### 1.2 Four Timeframes per Asset Type

| Timeframe | Update Frequency | Data Retention | Use Case |
|-----------|------------------|----------------|----------|
| **Weekly** | Sunday 11:59 PM ET | 10 years | Long-term trend analysis |
| **Daily** | 12:00 AM ET | 5 years | Swing trading, position analysis |
| **Hourly** | Every hour | 1 year | Short-term trading |
| **5-Minute** | Every 5 min (market hours) | 90 days | Day trading, scalping |

### 1.3 BigQuery Tables (24 Core + Support Tables)

```
aialgotradehits.crypto_trading_data/
├── stocks_weekly
├── stocks_daily
├── stocks_hourly
├── stocks_5min
├── crypto_weekly
├── crypto_daily
├── crypto_hourly
├── crypto_5min
├── forex_weekly
├── forex_daily
├── forex_hourly
├── forex_5min
├── etfs_weekly
├── etfs_daily
├── etfs_hourly
├── etfs_5min
├── indices_weekly
├── indices_daily
├── indices_hourly
├── indices_5min
├── commodities_weekly
├── commodities_daily
├── commodities_hourly
├── commodities_5min
├── users
├── search_history
├── search_analytics
├── symbols_master
├── indicator_metadata
└── watchlists
```

---

## 2. Robust Data Collection Infrastructure

### 2.1 Data Pipeline Architecture

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
                          | - OHLC integrity |
                          +------------------+
```

### 2.2 Data Validation Rules (CRITICAL)

**Every data point MUST be validated before storage:**

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
        'cci': {'min': -500, 'max': 500},
    }
}
```

### 2.3 Error Handling & Recovery

| Error Type | Detection | Recovery Action |
|------------|-----------|-----------------|
| API Rate Limit | HTTP 429 | Exponential backoff, retry after delay |
| API Timeout | Timeout exception | Retry 3x with increasing timeout |
| Invalid Data | Validation failure | Log, skip record, alert |
| Duplicate Data | Primary key conflict | Skip insert, log |
| Missing Data | Gap detection | Backfill job triggered |
| Schema Mismatch | Type error | Transform or reject |

### 2.4 Data Quality Assurance

- **Duplicate Detection:** Composite key check before every insert
- **Gap Detection:** Daily audit to identify missing data periods
- **Integrity Checks:** OHLC relationship validation
- **Freshness Monitoring:** Alert if data older than expected
- **Audit Trail:** Log all data modifications

---

## 3. Technical Indicators Framework (112 Indicators)

### 3.1 Complete Indicator List

All indicators are fetched directly from TwelveData API via `/technical_indicators` endpoint.

#### Trend Indicators (22)
| # | Code | Name | Default Period |
|---|------|------|----------------|
| 1 | SMA | Simple Moving Average | 5, 10, 20, 50, 100, 200 |
| 2 | EMA | Exponential Moving Average | 5, 10, 12, 20, 26, 50, 100, 200 |
| 3 | WMA | Weighted Moving Average | 20 |
| 4 | DEMA | Double Exponential MA | 20 |
| 5 | TEMA | Triple Exponential MA | 20 |
| 6 | KAMA | Kaufman Adaptive MA | 20 |
| 7 | T3MA | T3 Moving Average | 20 |
| 8 | TRIMA | Triangular MA | 20 |
| 9 | MAMA | MESA Adaptive MA | - |
| 10 | MCGINLEY_DYNAMIC | McGinley Dynamic | 20 |
| 11 | HT_TRENDLINE | Hilbert Transform Trendline | - |
| 12 | VWAP | Volume Weighted Average Price | - |
| 13 | SAR | Parabolic SAR | 0.02, 0.2 |
| 14 | SAREXT | Parabolic SAR Extended | - |
| 15 | BBANDS | Bollinger Bands | 20, 2 |
| 16 | KELTNER | Keltner Channels | 20 |
| 17 | ICHIMOKU | Ichimoku Cloud | 9, 26, 52 |
| 18 | PIVOT_POINTS_HL | Pivot Points | - |
| 19 | MIDPOINT | Midpoint | 14 |
| 20 | MIDPRICE | Midpoint Price | 14 |
| 21 | LINEARREG | Linear Regression | 14 |
| 22 | TSF | Time Series Forecast | 14 |

#### Momentum Indicators (34)
| # | Code | Name | Default Period |
|---|------|------|----------------|
| 23 | RSI | Relative Strength Index | 7, 14, 21 |
| 24 | MACD | Moving Average Convergence Divergence | 12, 26, 9 |
| 25 | MACD_SLOPE | MACD Slope | - |
| 26 | MACDEXT | MACD Extended | - |
| 27 | STOCH | Stochastic Oscillator | 14, 3, 3 |
| 28 | STOCHF | Stochastic Fast | 14, 3 |
| 29 | STOCHRSI | Stochastic RSI | 14, 14, 3, 3 |
| 30 | ADX | Average Directional Index | 14 |
| 31 | ADXR | ADX Rating | 14 |
| 32 | DX | Directional Movement Index | 14 |
| 33 | PLUS_DI | Plus Directional Indicator | 14 |
| 34 | MINUS_DI | Minus Directional Indicator | 14 |
| 35 | PLUS_DM | Plus Directional Movement | 14 |
| 36 | MINUS_DM | Minus Directional Movement | 14 |
| 37 | CCI | Commodity Channel Index | 14, 20 |
| 38 | CMO | Chande Momentum Oscillator | 14 |
| 39 | MOM | Momentum | 10 |
| 40 | ROC | Rate of Change | 10 |
| 41 | ROCP | Rate of Change Percentage | 10 |
| 42 | ROCR | Rate of Change Ratio | 10 |
| 43 | ROCR100 | Rate of Change Ratio 100 | 10 |
| 44 | WILLR | Williams %R | 14 |
| 45 | MFI | Money Flow Index | 14 |
| 46 | ULTOSC | Ultimate Oscillator | 7, 14, 28 |
| 47 | PPO | Percentage Price Oscillator | 12, 26, 9 |
| 48 | APO | Absolute Price Oscillator | 12, 26 |
| 49 | BOP | Balance of Power | - |
| 50 | AROON | Aroon Indicator | 14 |
| 51 | AROONOSC | Aroon Oscillator | 14 |
| 52 | COPPOCK | Coppock Curve | 14, 11, 10 |
| 53 | KST | Know Sure Thing | - |
| 54 | CRSI | Connors RSI | 3, 2, 100 |
| 55 | DPO | Detrended Price Oscillator | 20 |
| 56 | PERCENT_B | %B Indicator | 20, 2 |

#### Volume Indicators (4)
| # | Code | Name | Description |
|---|------|------|-------------|
| 57 | OBV | On Balance Volume | Cumulative volume indicator |
| 58 | AD | Accumulation/Distribution | Money flow indicator |
| 59 | ADOSC | A/D Oscillator | 3, 10 |
| 60 | RVOL | Relative Volume | Volume vs average |

#### Volatility Indicators (5)
| # | Code | Name | Default Period |
|---|------|------|----------------|
| 61 | ATR | Average True Range | 14 |
| 62 | NATR | Normalized ATR | 14 |
| 63 | TRANGE | True Range | - |
| 64 | SUPERTREND | SuperTrend | 10, 3 |
| 65 | SUPERTREND_HEIKINASHI | SuperTrend Heikin Ashi | 10, 3 |

#### Cycle Indicators (5)
| # | Code | Name |
|---|------|------|
| 66 | HT_DCPERIOD | Hilbert Transform Dominant Cycle Period |
| 67 | HT_DCPHASE | Hilbert Transform Dominant Cycle Phase |
| 68 | HT_PHASOR | Hilbert Transform Phasor Components |
| 69 | HT_SINE | Hilbert Transform Sine Wave |
| 70 | HT_TRENDMODE | Hilbert Transform Trend vs Cycle Mode |

#### Price Transform (6)
| # | Code | Name |
|---|------|------|
| 71 | AVGPRICE | Average Price (OHLC/4) |
| 72 | MEDPRICE | Median Price ((H+L)/2) |
| 73 | TYPPRICE | Typical Price ((H+L+C)/3) |
| 74 | WCLPRICE | Weighted Close ((H+L+2C)/4) |
| 75 | HLC3 | HLC3 |
| 76 | HEIKINASHICANDLES | Heikin Ashi Candles |

#### Statistical Functions (9)
| # | Code | Name |
|---|------|------|
| 77 | STDDEV | Standard Deviation |
| 78 | VAR | Variance |
| 79 | BETA | Beta |
| 80 | CORREL | Correlation Coefficient |
| 81 | LINEARREG_SLOPE | Linear Regression Slope |
| 82 | LINEARREG_ANGLE | Linear Regression Angle |
| 83 | LINEARREG_INTERCEPT | Linear Regression Intercept |
| 84 | MAX/MIN/MINMAX | Highest/Lowest Values |
| 85 | TSF | Time Series Forecast |

#### Math Functions (27)
| # | Codes |
|---|-------|
| 86-112 | ADD, SUB, MULT, DIV, SUM, AVG, SQRT, LN, LOG10, EXP, CEIL, FLOOR, ACOS, ASIN, ATAN, COS, COSH, SIN, SINH, TAN, TANH, MAX, MAXINDEX, MIN, MININDEX, MINMAX, MINMAXINDEX |

### 3.2 Indicator Auto-Sync from API

The system automatically syncs new indicators from TwelveData:

```python
def fetch_twelvedata_indicators():
    """Fetch complete indicator list from TwelveData API"""
    url = "https://api.twelvedata.com/technical_indicators"
    response = requests.get(url)
    return response.json()['data']
```

---

## 4. AI Smart Search Engine (Vertex AI + Gemini)

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
|   Display        |     |  Formatter        |     |  Gemini 2.0 Pro  |
+------------------+     +-------------------+     +------------------+
                                                           |
                                                           v
                                                  +------------------+
                                                  |   BigQuery       |
                                                  |   (SQL Gen)      |
                                                  +------------------+
```

### 4.2 Google Vertex AI Configuration

```python
VERTEX_AI_CONFIG = {
    'project_id': 'aialgotradehits',
    'location': 'us-central1',
    'model_id': 'gemini-2.0-pro',
    'temperature': 0.1,  # Low for accuracy
    'max_output_tokens': 8192,
    'top_p': 0.95,
    'top_k': 40,
}
```

### 4.3 Query Types Supported

| Query Type | Example | AI Processing |
|------------|---------|---------------|
| **Simple Lookup** | "Show me AAPL" | Direct symbol search |
| **Indicator Filter** | "Stocks with RSI below 30" | SQL WHERE clause |
| **Multi-Condition** | "Tech stocks RSI < 30 AND MACD bullish crossover" | Complex SQL |
| **Comparative** | "Compare AAPL vs MSFT momentum" | Side-by-side analysis |
| **Trend Analysis** | "Which cryptos are trending up this week?" | Trend detection |
| **Pattern Recognition** | "Find double bottom patterns in S&P 500" | Pattern matching |
| **Sector Analysis** | "Best performing tech stocks today" | Sector + ranking |
| **Correlation** | "What correlates with Bitcoin?" | Correlation matrix |
| **Anomaly Detection** | "Unusual volume in any stock today" | Statistical anomaly |
| **Prediction Request** | "What's the outlook for NVDA?" | AI analysis summary |

### 4.4 Natural Language Query Examples

**Example 1: Oversold Tech Stocks**
```
USER: "Show me oversold tech stocks with increasing volume"

AI PARSING:
- Asset Type: Stocks
- Sector Filter: Technology
- Indicator Condition 1: RSI < 30 (oversold)
- Indicator Condition 2: Volume > SMA(Volume, 20)
- Sort: By RSI ascending

GENERATED SQL:
SELECT symbol, close, rsi_14, volume,
       ((volume - volume_sma_20) / volume_sma_20 * 100) as volume_change_pct
FROM `aialgotradehits.crypto_trading_data.stocks_daily`
WHERE sector = 'Technology'
  AND rsi_14 < 30
  AND volume > volume_sma_20
  AND date = (SELECT MAX(date) FROM stocks_daily)
ORDER BY rsi_14 ASC
LIMIT 20;
```

**Example 2: Multi-Asset Momentum Scan**
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

**Example 3: Golden Cross Detection**
```
USER: "Show me stocks that just had a golden cross"

AI PARSING:
- Golden Cross: 50-day SMA crosses above 200-day SMA
- Condition: Current SMA_50 > SMA_200 AND Previous SMA_50 < Previous SMA_200

GENERATED SQL:
WITH ranked AS (
  SELECT symbol, date, close, sma_50, sma_200,
         LAG(sma_50) OVER (PARTITION BY symbol ORDER BY date) as prev_sma_50,
         LAG(sma_200) OVER (PARTITION BY symbol ORDER BY date) as prev_sma_200
  FROM stocks_daily
  WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 5 DAY)
)
SELECT symbol, close, sma_50, sma_200
FROM ranked
WHERE sma_50 > sma_200
  AND prev_sma_50 < prev_sma_200
  AND date = (SELECT MAX(date) FROM ranked);
```

### 4.5 AI System Prompt

```python
SYSTEM_PROMPT = """
You are an expert financial analyst and trading assistant for AIAlgoTradeHits.

YOUR CAPABILITIES:
1. Analyze market data across 6 asset types: Stocks, Crypto, Forex, ETFs, Indices, Commodities
2. Access to 112 technical indicators for each asset
3. Generate BigQuery SQL queries to retrieve precise data
4. Provide institutional-grade market analysis

DATA SCHEMA CONTEXT:
{schema_context}

AVAILABLE INDICATORS:
{indicators_list}

RESPONSE GUIDELINES:
1. Always be precise with numbers - never approximate
2. Cite specific indicator values when making claims
3. Acknowledge uncertainty when data is insufficient
4. Provide actionable insights, not just data
5. Consider risk factors in all recommendations
6. Use professional financial terminology

SQL GENERATION RULES:
1. Always use fully qualified table names (aialgotradehits.crypto_trading_data.xxx)
2. Include datetime filters for recent data
3. Handle NULL values appropriately
4. Optimize queries for performance
5. Limit results appropriately (default 20)
"""
```

### 4.6 Voice Input Support

```javascript
FINANCIAL_VOCABULARY = {
  // Indicator aliases
  "our aside": "RSI",
  "are as I": "RSI",
  "Mac D": "MACD",
  "bollinger": "BBANDS",
  "stochastic": "STOCH",

  // Asset aliases
  "apple": "AAPL",
  "microsoft": "MSFT",
  "bitcoin": "BTC/USD",
  "ethereum": "ETH/USD",

  // Condition aliases
  "oversold": "RSI < 30",
  "overbought": "RSI > 70",
  "golden cross": "SMA_50 > SMA_200 AND prev_SMA_50 < prev_SMA_200",
  "death cross": "SMA_50 < SMA_200 AND prev_SMA_50 > prev_SMA_200",
}
```

### 4.7 AI Response Format

```json
{
  "query_understanding": {
    "original_query": "string",
    "interpreted_intent": "string",
    "confidence_score": 0.95,
    "entities_extracted": {
      "asset_types": ["stocks"],
      "symbols": ["AAPL"],
      "indicators": ["RSI", "MACD"],
      "conditions": ["RSI < 30"]
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

---

## 5. Interactive Professional Charting

### 5.1 Charting Library

**Primary Library:** TradingView Lightweight Charts v4.x
- Professional institutional appearance
- Excellent performance (~40KB)
- Mobile responsive
- Active development

### 5.2 Chart Types

| Chart Type | Use Case |
|------------|----------|
| Candlestick | Primary price display |
| OHLC Bars | Alternative price view |
| Line | Simple price/indicator |
| Area | Volume, filled indicators |
| Histogram | MACD, Volume |
| Heikin-Ashi | Trend clarity |

### 5.3 Indicator Overlays

**Price Overlays (Same Pane):**
- Moving Averages (SMA, EMA, WMA)
- Bollinger Bands
- Keltner Channels
- Ichimoku Cloud
- Pivot Points
- Parabolic SAR

**Separate Pane Indicators:**
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
| Trend Line | Connect highs/lows |
| Horizontal Line | Support/Resistance |
| Channel | Parallel trend lines |
| Fibonacci Retracement | Key levels |
| Fibonacci Extension | Price targets |
| Rectangle | Zone highlighting |
| Text Annotation | Notes and labels |

### 5.5 Chart Interaction Features

```javascript
CHART_FEATURES = {
  zoom: {
    mouse_wheel: true,
    pinch_touch: true,
    double_click_reset: true
  },
  pan: {
    mouse_drag: true,
    touch_drag: true,
    keyboard_arrows: true
  },
  crosshair: {
    mode: 'magnet',
    show_price: true,
    show_time: true
  },
  tooltip: {
    show_ohlcv: true,
    show_indicators: true,
    show_change: true
  },
  timeframe_selector: ['1m', '5m', '15m', '30m', '1h', '4h', '1D', '1W', '1M'],
  chart_type_selector: ['candle', 'ohlc', 'line', 'area', 'heikin-ashi']
}
```

### 5.6 Multi-Chart Layouts

```
+-------------------+     +--------+--------+     +--------+--------+
|                   |     |        |        |     |        |        |
|   Single Chart    |     |   2x1  |  Grid  |     |   2x2  |  Grid  |
|                   |     |        |        |     +--------+--------+
+-------------------+     +--------+--------+     |        |        |
                                                  +--------+--------+
```

---

## 6. BigQuery Data Warehouse

### 6.1 Core Table Schema

```sql
CREATE TABLE `aialgotradehits.crypto_trading_data.stocks_daily` (
  -- Primary Key
  id STRING NOT NULL,

  -- Symbol Info
  symbol STRING NOT NULL,
  name STRING,
  exchange STRING,
  sector STRING,

  -- Timestamp
  datetime TIMESTAMP NOT NULL,
  date DATE,

  -- OHLCV
  open FLOAT64 NOT NULL,
  high FLOAT64 NOT NULL,
  low FLOAT64 NOT NULL,
  close FLOAT64 NOT NULL,
  volume FLOAT64,

  -- Moving Averages (12 columns)
  sma_5 FLOAT64, sma_10 FLOAT64, sma_20 FLOAT64, sma_50 FLOAT64, sma_100 FLOAT64, sma_200 FLOAT64,
  ema_12 FLOAT64, ema_20 FLOAT64, ema_26 FLOAT64, ema_50 FLOAT64, ema_100 FLOAT64, ema_200 FLOAT64,

  -- Momentum (20 columns)
  rsi_14 FLOAT64, macd_line FLOAT64, macd_signal FLOAT64, macd_histogram FLOAT64,
  stoch_k FLOAT64, stoch_d FLOAT64, stochrsi_k FLOAT64, stochrsi_d FLOAT64,
  willr_14 FLOAT64, cci_14 FLOAT64, mfi_14 FLOAT64, mom_10 FLOAT64, roc_10 FLOAT64,
  cmo_14 FLOAT64, ultosc FLOAT64, ppo_line FLOAT64, apo FLOAT64, bop FLOAT64,
  percent_b FLOAT64, crsi FLOAT64,

  -- Trend (10 columns)
  adx_14 FLOAT64, adxr_14 FLOAT64, dx_14 FLOAT64,
  plus_di FLOAT64, minus_di FLOAT64,
  aroon_up FLOAT64, aroon_down FLOAT64, aroon_osc FLOAT64,
  kama_20 FLOAT64, vwap FLOAT64,

  -- Volatility (10 columns)
  atr_14 FLOAT64, natr_14 FLOAT64, trange FLOAT64,
  bbands_upper FLOAT64, bbands_middle FLOAT64, bbands_lower FLOAT64, bbands_bandwidth FLOAT64,
  keltner_upper FLOAT64, keltner_middle FLOAT64, keltner_lower FLOAT64,

  -- Volume (4 columns)
  obv FLOAT64, ad FLOAT64, adosc FLOAT64, rvol FLOAT64,

  -- Ichimoku (5 columns)
  ichimoku_tenkan FLOAT64, ichimoku_kijun FLOAT64,
  ichimoku_senkou_a FLOAT64, ichimoku_senkou_b FLOAT64, ichimoku_chikou FLOAT64,

  -- Statistics (5 columns)
  stddev_20 FLOAT64, variance_20 FLOAT64,
  linearreg FLOAT64, linearreg_slope FLOAT64, linearreg_angle FLOAT64,

  -- Derived Metrics
  change_pct FLOAT64,
  range_pct FLOAT64,

  -- AI-Derived Classifications
  trend_short STRING,  -- 'up', 'down', 'sideways'
  trend_medium STRING,
  trend_long STRING,
  is_oversold BOOL,
  is_overbought BOOL,

  -- Metadata
  data_source STRING DEFAULT 'twelvedata',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY date
CLUSTER BY symbol, sector;
```

---

## 7. API Architecture

### 7.1 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search` | POST | AI-powered smart search |
| `/api/symbols` | GET | List all symbols |
| `/api/symbols/{symbol}` | GET | Symbol details |
| `/api/quotes/{symbol}` | GET | Current quote |
| `/api/history/{symbol}` | GET | Historical data |
| `/api/indicators/{symbol}` | GET | All indicators |
| `/api/scan` | POST | Filtered asset scan |
| `/api/alerts` | GET/POST | User alerts |
| `/api/watchlist` | GET/POST | User watchlists |

### 7.2 Response Format

```json
{
  "success": true,
  "query_id": "uuid",
  "execution_time_ms": 245,
  "results": {
    "count": 15,
    "data": [...]
  },
  "ai_insights": {
    "summary": "...",
    "key_findings": [...],
    "risk_warnings": [...]
  }
}
```

---

## 8. Cloud Functions & Schedulers

### 8.1 24 Cloud Schedulers

| Function | Schedule | Timezone |
|----------|----------|----------|
| stocks-weekly-fetcher | 0 23 * * 0 | America/New_York |
| stocks-daily-fetcher | 0 0 * * * | America/New_York |
| stocks-hourly-fetcher | 0 * * * * | America/New_York |
| stocks-5min-fetcher | */5 9-16 * * 1-5 | America/New_York |
| crypto-weekly-fetcher | 0 23 * * 0 | America/New_York |
| crypto-daily-fetcher | 0 0 * * * | America/New_York |
| crypto-hourly-fetcher | 0 * * * * | America/New_York |
| crypto-5min-fetcher | */5 * * * * | America/New_York |
| forex-weekly-fetcher | 0 23 * * 0 | America/New_York |
| forex-daily-fetcher | 0 0 * * * | America/New_York |
| forex-hourly-fetcher | 0 * * * * | America/New_York |
| forex-5min-fetcher | */5 * * * 1-5 | America/New_York |
| etfs-weekly-fetcher | 0 23 * * 0 | America/New_York |
| etfs-daily-fetcher | 0 0 * * * | America/New_York |
| etfs-hourly-fetcher | 0 * * * * | America/New_York |
| etfs-5min-fetcher | */5 9-16 * * 1-5 | America/New_York |
| indices-weekly-fetcher | 0 23 * * 0 | America/New_York |
| indices-daily-fetcher | 0 0 * * * | America/New_York |
| indices-hourly-fetcher | 0 * * * * | America/New_York |
| indices-5min-fetcher | */5 9-16 * * 1-5 | America/New_York |
| commodities-weekly-fetcher | 0 23 * * 0 | America/New_York |
| commodities-daily-fetcher | 0 0 * * * | America/New_York |
| commodities-hourly-fetcher | 0 * * * * | America/New_York |
| commodities-5min-fetcher | */5 9-16 * * 1-5 | America/New_York |

---

## 9. Implementation Roadmap

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
- [ ] Search result ranking
- [ ] Mobile optimization
- [ ] User feedback integration

---

## 10. Project Configuration

### 10.1 GCP Resources

| Resource | Value |
|----------|-------|
| **Project ID** | aialgotradehits |
| **Region** | us-central1 |
| **BigQuery Dataset** | crypto_trading_data |
| **Cloud Functions Runtime** | Python 3.11 |
| **Vertex AI Model** | gemini-2.0-pro |

### 10.2 TwelveData API

```
API Key: 16ee060fd4d34a628a14bcb6f0167565
Base URL: https://api.twelvedata.com
```

### 10.3 What to Remove (Legacy)

- All Kraken API code
- All Yahoo Finance code
- Duplicate/redundant tables
- Old cloud functions using other data sources

---

## Document Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Nov 24, 2025 | Initial strategy document |
| 2.0 | Nov 25, 2025 | Major expansion: AI Smart Search (Vertex AI + Gemini), Professional Charting, Complete 112 Indicators, Robust Data Collection |

---

**This document is the AUTHORITATIVE source for all architectural decisions. Any implementation must follow this document exactly.**
