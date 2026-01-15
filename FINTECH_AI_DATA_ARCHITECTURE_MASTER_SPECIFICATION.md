# AIAlgoTradeHits.com - Fintech AI Data Architecture & Implementation Specification

## Master Technical Document

**Version:** 2.0
**Platform:** Google Cloud Platform (GCP)
**AI Engine:** Vertex AI + Gemini 3
**Date:** November 2025
**Classification:** Technical Specification

---

## Executive Summary

AIAlgoTradeHits.com is a comprehensive cross-asset, AI-driven analytics, alerting, and intelligence platform delivering institutional-grade insights across **equities, ETFs, cryptocurrency, forex, commodities, and interest-rate markets**. Built entirely on Google Cloud Platform, the system leverages **Vertex AI**, **Gemini 3 LLM**, **BigQuery**, and **Cloud Run** to create a next-generation fintech trading intelligence engine.

### Platform Vision

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Data Warehouse** | BigQuery | Multi-layer data architecture (Bronze/Silver/Gold) |
| **AI/ML Engine** | Vertex AI | Predictive models, pattern recognition, regime classification |
| **LLM Intelligence** | Gemini 3 Pro | Natural language analysis, RAG-powered commentary |
| **Document Intelligence** | Document AI + RAG | Research document processing, knowledge retrieval |
| **Real-Time Serving** | Cloud Run + Cloud Functions | API endpoints, scheduled data collection |
| **Frontend** | React + TradingView Charts | Professional trading interface |

---

## Part 1: Data Architecture

### 1.1 Multi-Layer Data Architecture

The platform implements a rigorous four-layer data architecture inspired by institutional quant trading desks:

```
┌─────────────────────────────────────────────────────────┐
│                    INCOMING MARKET FEEDS                 │
│         (TwelveData, Kraken, Finnhub, News APIs)        │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                     BRONZE LAYER                         │
│              Raw, Immutable Market Data                  │
│         • Exact API responses preserved                  │
│         • Full lineage and audit trail                   │
│         • Compliance-grade immutability                  │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                     SILVER LAYER                         │
│             Cleaned & Standardized Data                  │
│         • Normalized timestamps (UTC)                    │
│         • Missing data handling                          │
│         • Anomaly removal (zero-volume, spikes)          │
│         • Session calendar alignment                     │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                      GOLD LAYER                          │
│           Engineered Features & Intelligence             │
│         • 70+ Technical Indicators                       │
│         • Pattern Recognition Signals                    │
│         • Cross-Asset Correlations                       │
│         • Volatility Regime Classification               │
│         • ML-Ready Feature Vectors                       │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                      WIDE TABLES                         │
│              Materialized Fast-Access Layer              │
│         • Flattened serving tables                       │
│         • Real-time UI/API access                        │
│         • LLM RAG retrieval optimized                    │
│         • ML inference ready                             │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
          ┌─────────────────┬─────────────────┐
          │   ML Models     │   LLM/RAG       │
          │   (Vertex AI)   │   (Gemini 3)    │
          └─────────────────┴─────────────────┘
```

### 1.2 BigQuery Table Structure

#### 1.2.1 Asset Class Tables (6 Categories)

| Table Name | Asset Class | Timeframes | Data Source |
|------------|-------------|------------|-------------|
| `stocks_historical_daily` | US Equities | Daily, Weekly | TwelveData |
| `stocks_hourly` | US Equities | Hourly, 5-min | TwelveData |
| `cryptos_historical_daily` | Cryptocurrency | Daily, Weekly | Kraken/TwelveData |
| `crypto_hourly_data` | Cryptocurrency | Hourly, 5-min | Kraken |
| `etfs_historical_daily` | ETFs | Daily, Weekly | TwelveData |
| `forex_historical_daily` | FX Pairs | Daily, Weekly | TwelveData |
| `indices_historical_daily` | Market Indices | Daily, Weekly | TwelveData |
| `commodities_historical_daily` | Commodities | Daily, Weekly | TwelveData |

#### 1.2.2 Complete Field Schema (Phase 1 Enhanced)

Based on Phase 1 Methodology requirements, the following fields are required for ML training:

##### Core OHLCV Fields (Required)

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `symbol` | STRING | Asset ticker symbol | ✅ Available |
| `datetime` | TIMESTAMP | Candle timestamp (UTC) | ✅ Available |
| `open` | FLOAT64 | Opening price | ✅ Available |
| `high` | FLOAT64 | High price | ✅ Available |
| `low` | FLOAT64 | Low price | ✅ Available |
| `close` | FLOAT64 | Closing price | ✅ Available |
| `volume` | FLOAT64 | Trading volume | ✅ Available |
| `candle_body_pct` | FLOAT64 | (close - open) / open | ⚠️ Add |
| `candle_range_pct` | FLOAT64 | (high - low) / open | ⚠️ Add |

##### Return & Momentum Fields

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `weekly_return` | FLOAT64 | Weekly percentage return | ✅ Available |
| `weekly_log_return` | FLOAT64 | ln(close_t / close_{t-1}) | ⚠️ Add |
| `return_2w` | FLOAT64 | 2-week return | ⚠️ Add |
| `return_4w` | FLOAT64 | 4-week return | ⚠️ Add |
| `daily_return_pct` | FLOAT64 | Daily return percentage | ✅ Available |

##### RSI Indicators

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `rsi_7` | FLOAT64 | RSI 7-period | ✅ Available |
| `rsi_14` | FLOAT64 | RSI 14-period | ✅ Available |
| `rsi_21` | FLOAT64 | RSI 21-period | ✅ Available |
| `rsi_slope` | FLOAT64 | RSI change rate | ⚠️ Add |
| `rsi_zscore` | FLOAT64 | RSI z-score (100-week) | ⚠️ Add |
| `rsi_overbought_flag` | INT64 | RSI > 70 flag | ⚠️ Add |
| `rsi_oversold_flag` | INT64 | RSI < 30 flag | ⚠️ Add |

##### MACD Indicators

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `macd` | FLOAT64 | MACD line (12,26) | ✅ Available |
| `macd_signal` | FLOAT64 | MACD signal (9) | ✅ Available |
| `macd_hist` | FLOAT64 | MACD histogram | ⚠️ Add |
| `macd_cross_flag` | INT64 | Cross signal (+1/-1/0) | ⚠️ Add |

##### Moving Averages - SMA

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `sma_5` | FLOAT64 | SMA 5-period | ✅ Available |
| `sma_10` | FLOAT64 | SMA 10-period | ✅ Available |
| `sma_20` | FLOAT64 | SMA 20-period | ✅ Available |
| `sma_50` | FLOAT64 | SMA 50-period | ✅ Available |
| `sma_100` | FLOAT64 | SMA 100-period | ✅ Available |
| `sma_200` | FLOAT64 | SMA 200-period | ✅ Available |

##### Moving Averages - EMA

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `ema_5` | FLOAT64 | EMA 5-period | ⚠️ Add |
| `ema_10` | FLOAT64 | EMA 10-period | ⚠️ Add |
| `ema_20` | FLOAT64 | EMA 20-period | ⚠️ Add |
| `ema_50` | FLOAT64 | EMA 50-period | ⚠️ Add |
| `ema_100` | FLOAT64 | EMA 100-period | ⚠️ Add |
| `ema_200` | FLOAT64 | EMA 200-period | ⚠️ Add |

##### MA Distance Features

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `close_vs_sma20_pct` | FLOAT64 | (close / SMA20 - 1) * 100 | ⚠️ Add |
| `close_vs_sma50_pct` | FLOAT64 | (close / SMA50 - 1) * 100 | ⚠️ Add |
| `close_vs_sma200_pct` | FLOAT64 | (close / SMA200 - 1) * 100 | ⚠️ Add |
| `close_vs_ema20_pct` | FLOAT64 | (close / EMA20 - 1) * 100 | ⚠️ Add |
| `ema_slope_20` | FLOAT64 | EMA20 slope | ⚠️ Add |
| `ema_slope_50` | FLOAT64 | EMA50 slope | ⚠️ Add |

##### Volatility Indicators

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `atr_7` | FLOAT64 | ATR 7-period | ✅ Available |
| `atr_14` | FLOAT64 | ATR 14-period | ✅ Available |
| `atr_pct` | FLOAT64 | ATR / close * 100 | ⚠️ Add |
| `atr_zscore` | FLOAT64 | ATR z-score | ⚠️ Add |
| `atr_slope` | FLOAT64 | ATR change rate | ⚠️ Add |
| `volatility_10` | FLOAT64 | 10-period volatility | ✅ Available |
| `volatility_20` | FLOAT64 | 20-period volatility | ✅ Available |

##### Bollinger Bands

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `bb_upper` | FLOAT64 | Upper band (20, 2σ) | ✅ Available |
| `bb_middle` | FLOAT64 | Middle band (SMA20) | ✅ Available |
| `bb_lower` | FLOAT64 | Lower band (20, 2σ) | ✅ Available |
| `bb_width` | FLOAT64 | Band width percentage | ✅ Available |
| `bb_percent` | FLOAT64 | %B indicator | ✅ Available |

##### Stochastic & Oscillators

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `stoch_k` | FLOAT64 | Stochastic %K | ✅ Available |
| `stoch_d` | FLOAT64 | Stochastic %D | ✅ Available |
| `williams_r` | FLOAT64 | Williams %R | ✅ Available |
| `cci` | FLOAT64 | CCI (20) | ✅ Available |

##### Volume Indicators

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `obv` | FLOAT64 | On-Balance Volume | ✅ Available |
| `volume_zscore` | FLOAT64 | Volume z-score | ⚠️ Add |
| `volume_ratio` | FLOAT64 | Volume / MA volume | ⚠️ Add |

##### Trend Indicators (ADX)

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `adx` | FLOAT64 | ADX (14) | ⚠️ Add |
| `plus_di` | FLOAT64 | +DI (14) | ⚠️ Add |
| `minus_di` | FLOAT64 | -DI (14) | ⚠️ Add |

##### Pivot & Structure Features

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `pivot_high_flag` | INT64 | Pivot high detected | ⚠️ Add |
| `pivot_low_flag` | INT64 | Pivot low detected | ⚠️ Add |
| `dist_to_pivot_high` | FLOAT64 | Distance to last pivot high | ⚠️ Add |
| `dist_to_pivot_low` | FLOAT64 | Distance to last pivot low | ⚠️ Add |

##### Regime & Classification

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `regime_state` | INT64 | Numeric regime (1-6) | ⚠️ Add |
| `regime_confidence` | FLOAT64 | Regime confidence (0-1) | ⚠️ Add |
| `momentum_signal` | STRING | overbought/oversold/bullish/bearish | ✅ Available |
| `trend_signal` | STRING | strong_bullish/bullish/bearish/strong_bearish | ✅ Available |

##### ML Target Variables

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `target_return_1d` | FLOAT64 | Next-day return % | ✅ Available |
| `target_return_5d` | FLOAT64 | 5-day forward return % | ✅ Available |
| `target_direction_1d` | INT64 | Next-day direction (0/1) | ✅ Available |

##### Lagged Features

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `close_lag_1` | FLOAT64 | Close t-1 | ✅ Available |
| `close_lag_2` | FLOAT64 | Close t-2 | ✅ Available |
| `close_lag_3` | FLOAT64 | Close t-3 | ✅ Available |
| `close_lag_5` | FLOAT64 | Close t-5 | ✅ Available |
| `close_lag_10` | FLOAT64 | Close t-10 | ✅ Available |
| `return_lag_1` | FLOAT64 | Return t-1 | ✅ Available |
| `return_lag_2` | FLOAT64 | Return t-2 | ✅ Available |
| `return_lag_3` | FLOAT64 | Return t-3 | ✅ Available |

##### Metadata Fields

| Field Name | Type | Description | Status |
|------------|------|-------------|--------|
| `asset_type` | STRING | stocks/cryptos/etfs/forex/indices/commodities | ✅ Available |
| `fetch_timestamp` | TIMESTAMP | Data collection timestamp | ✅ Available |

---

## Part 2: AI & Machine Learning Architecture

### 2.1 Vertex AI Integration

#### 2.1.1 Model Types & Use Cases

| Model Type | Vertex AI Service | Use Case |
|------------|-------------------|----------|
| **Gradient Boosting** | AutoML Tables | Regime classification, direction prediction |
| **Time Series** | Vertex AI Forecasting | Price prediction, volatility forecasting |
| **LSTM/Transformer** | Custom Training | Sequential pattern learning |
| **Vision Models** | AutoML Vision | Chart pattern recognition |
| **LLM** | Gemini 3 Pro | Commentary generation, analysis |

#### 2.1.2 ML Pipeline Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    VERTEX AI PIPELINES                   │
└─────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  TRAINING     │   │  PREDICTION   │   │  EVALUATION   │
│  PIPELINE     │   │  PIPELINE     │   │  PIPELINE     │
├───────────────┤   ├───────────────┤   ├───────────────┤
│ • Feature     │   │ • Real-time   │   │ • Backtesting │
│   extraction  │   │   inference   │   │ • Performance │
│ • Model       │   │ • Batch       │   │   metrics     │
│   training    │   │   predictions │   │ • Drift       │
│ • Hyperparameter│ │ • Alert       │   │   detection   │
│   tuning      │   │   generation  │   │               │
└───────────────┘   └───────────────┘   └───────────────┘
```

#### 2.1.3 Feature Store Configuration

```python
# Vertex AI Feature Store Schema
FEATURE_GROUPS = {
    "price_features": {
        "entity_type": "asset_timestamp",
        "features": [
            "open", "high", "low", "close", "volume",
            "candle_body_pct", "candle_range_pct"
        ]
    },
    "momentum_features": {
        "entity_type": "asset_timestamp",
        "features": [
            "rsi_7", "rsi_14", "rsi_21", "rsi_slope", "rsi_zscore",
            "macd", "macd_signal", "macd_hist", "macd_cross_flag",
            "stoch_k", "stoch_d", "williams_r", "cci"
        ]
    },
    "trend_features": {
        "entity_type": "asset_timestamp",
        "features": [
            "sma_20", "sma_50", "sma_200",
            "ema_20", "ema_50", "ema_200",
            "close_vs_sma20_pct", "close_vs_sma50_pct",
            "adx", "plus_di", "minus_di"
        ]
    },
    "volatility_features": {
        "entity_type": "asset_timestamp",
        "features": [
            "atr_14", "atr_pct", "atr_zscore",
            "bb_upper", "bb_middle", "bb_lower", "bb_width", "bb_percent",
            "volatility_10", "volatility_20"
        ]
    },
    "regime_features": {
        "entity_type": "asset_timestamp",
        "features": [
            "regime_state", "regime_confidence",
            "momentum_signal", "trend_signal"
        ]
    }
}
```

### 2.2 Gemini 3 LLM Integration

#### 2.2.1 LLM Use Cases

| Use Case | Input | Output | Frequency |
|----------|-------|--------|-----------|
| **Market Commentary** | Latest indicators, patterns, regime | Research-style analysis | Real-time |
| **Alert Explanations** | Alert trigger data, context | Natural language reasoning | Per alert |
| **Pattern Analysis** | Chart patterns, structure | Professional interpretation | On detection |
| **Risk Assessment** | Cross-asset correlations | Risk narrative | Hourly |
| **Q&A Interface** | User questions + RAG context | Informed responses | On-demand |

#### 2.2.2 RAG (Retrieval-Augmented Generation) Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   USER QUERY / TRIGGER                   │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   CONTEXT RETRIEVAL                      │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   BigQuery  │  │  Vector DB  │  │  Document   │     │
│  │   Market    │  │  Research   │  │  Store      │     │
│  │   Data      │  │  Embeddings │  │  (PDF/DOCX) │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   PROMPT CONSTRUCTION                    │
├─────────────────────────────────────────────────────────┤
│  System Instructions + Retrieved Context + User Query    │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                     GEMINI 3 PRO                         │
├─────────────────────────────────────────────────────────┤
│  • Grounded response generation                          │
│  • Citation of data sources                              │
│  • Confidence scoring                                    │
│  • Hallucination prevention                              │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   STRUCTURED OUTPUT                      │
├─────────────────────────────────────────────────────────┤
│  • Market analysis narrative                             │
│  • Key insights with citations                           │
│  • Risk warnings                                         │
│  • Actionable recommendations                            │
└─────────────────────────────────────────────────────────┘
```

#### 2.2.3 Document AI & Knowledge Base

The platform leverages Google Document AI for processing research documents, news, and institutional reports:

| Component | Service | Purpose |
|-----------|---------|---------|
| **PDF Processor** | Document AI | Extract text from research PDFs |
| **Embedding Generator** | Vertex AI Embeddings | Create vector representations |
| **Vector Store** | Vertex AI Vector Search | Semantic search over documents |
| **Knowledge Graph** | Enterprise Knowledge Graph | Entity relationships |

---

## Part 3: Implementation Phases

### 3.1 Phase 1: Trader-Focused AI Alert Engine

**Timeline:** Current - 3 months
**Focus:** Real-time alerts for equities and cryptocurrency

#### MVP Symbol Universe

| Category | Symbols | Count |
|----------|---------|-------|
| **US Equities** | AAPL, NVDA, JPM, LLY, MSFT, GOOGL, AMZN, META, TSLA, etc. | 50 |
| **ETFs** | SPY, QQQ, IWM, DIA, VTI, VOO, GLD, etc. | 30 |
| **Cryptocurrency** | BTC/USD, ETH/USD, SOL/USD, XRP/USD, etc. | 20 |
| **Forex** | EUR/USD, GBP/USD, USD/JPY, etc. | 20 |
| **Indices** | SPX, NDX, DJI, VIX, etc. | 14 |
| **Commodities** | XAU/USD, XAG/USD, CL, NG, etc. | 16 |

#### Phase 1 Deliverables

1. **Real-Time Alert System**
   - Trend flip alerts
   - Momentum reversal signals
   - Volatility expansion warnings
   - Breakout/breakdown detection
   - Pattern confirmation alerts

2. **AI-Enhanced Dashboards**
   - Regime classification display
   - Volatility heatmaps
   - Correlation monitors
   - Sentiment indicators

3. **LLM Commentary (Basic)**
   - Alert explanation generation
   - Daily market summaries
   - Pattern interpretation

### 3.2 Phase 2: Institutional Treasury Intelligence System

**Timeline:** 3-6 months
**Focus:** Enterprise-grade macro and treasury intelligence

#### Phase 2 Capabilities

| Capability | Description |
|------------|-------------|
| **Cross-Asset Correlation Engine** | Real-time correlation matrices across all asset classes |
| **Macro Regime Classification** | Risk-on/off detection, volatility regime scoring |
| **Treasury Exposure Analytics** | FX risk mapping, yield sensitivity analysis |
| **Yield Curve Analytics** | Curve shape analysis, rate sensitivity |
| **Early Warning System** | Liquidity stress, correlation breakdown alerts |
| **AI-Generated Institutional Reports** | Compliance-ready research commentary |

---

## Part 4: GCP Infrastructure

### 4.1 Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GCP PROJECT: cryptobot-462709         │
└─────────────────────────────────────────────────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    ▼                         ▼                         ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│ Cloud Run   │       │  BigQuery   │       │  Vertex AI  │
│ (Frontend + │       │  (Data      │       │  (ML +      │
│  API)       │       │  Warehouse) │       │  Gemini 3)  │
└─────────────┘       └─────────────┘       └─────────────┘
    │                         │                         │
    │                         │                         │
    ▼                         ▼                         ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│ Cloud       │       │ Cloud       │       │ Cloud       │
│ Functions   │       │ Storage     │       │ Scheduler   │
│ (Data Fetch)│       │ (Documents) │       │ (Triggers)  │
└─────────────┘       └─────────────┘       └─────────────┘
```

### 4.2 Cost Optimization Strategy

| Service | Optimization | Monthly Estimate |
|---------|--------------|------------------|
| **BigQuery** | Partitioned tables, clustering | $50-100 |
| **Cloud Functions** | Efficient scheduling, cold start optimization | $130 |
| **Cloud Run** | Auto-scaling, min instances | $50-100 |
| **Vertex AI** | Batch predictions, model caching | $200-500 |
| **Gemini 3** | Caching, prompt optimization | $100-300 |
| **Total Estimate** | | **$530-1,130/month** |

---

## Part 5: Missing Fields Implementation Plan

Based on Phase 1 Methodology analysis, the following fields need to be added:

### Priority 1: Critical ML Features (Add Immediately)

```python
MISSING_FIELDS_PRIORITY_1 = [
    # Log returns
    'weekly_log_return',  # ln(close_t / close_{t-1})

    # Multi-lag returns
    'return_2w',  # 2-week return
    'return_4w',  # 4-week return

    # RSI enhancements
    'rsi_slope',           # RSI change rate
    'rsi_zscore',          # RSI z-score
    'rsi_overbought_flag', # RSI > 70
    'rsi_oversold_flag',   # RSI < 30

    # MACD enhancements
    'macd_hist',           # MACD histogram
    'macd_cross_flag',     # Cross signal

    # EMA suite
    'ema_5', 'ema_10', 'ema_20', 'ema_50', 'ema_100', 'ema_200',

    # MA distance features
    'close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct',
    'close_vs_ema20_pct',

    # EMA slopes
    'ema_slope_20', 'ema_slope_50',
]
```

### Priority 2: Enhanced Features (Add Next Sprint)

```python
MISSING_FIELDS_PRIORITY_2 = [
    # ATR enhancements
    'atr_pct',      # ATR as % of price
    'atr_zscore',   # ATR z-score
    'atr_slope',    # ATR change rate

    # Volume enhancements
    'volume_zscore',  # Volume z-score
    'volume_ratio',   # Volume vs MA

    # ADX trend
    'adx', 'plus_di', 'minus_di',

    # Candle geometry
    'candle_body_pct',   # Body as % of open
    'candle_range_pct',  # Range as % of open
]
```

### Priority 3: Advanced Structure (Phase 2)

```python
MISSING_FIELDS_PRIORITY_3 = [
    # Pivot structure
    'pivot_high_flag', 'pivot_low_flag',
    'dist_to_pivot_high', 'dist_to_pivot_low',

    # Regime classification
    'regime_state',       # Numeric regime (1-6)
    'regime_confidence',  # Confidence score
]
```

---

## Part 6: Implementation Roadmap

### Week 1-2: Data Schema Enhancement
- [ ] Add Priority 1 missing fields to BigQuery tables
- [ ] Update data fetching scripts with new calculations
- [ ] Backfill historical data with new indicators

### Week 3-4: ML Pipeline Setup
- [ ] Configure Vertex AI Feature Store
- [ ] Create initial training pipelines
- [ ] Deploy baseline models

### Week 5-6: LLM Integration
- [ ] Implement RAG pipeline with BigQuery
- [ ] Configure Gemini 3 Pro prompts
- [ ] Build commentary generation endpoints

### Week 7-8: Testing & Optimization
- [ ] Backtest ML models
- [ ] Evaluate LLM output quality
- [ ] Performance optimization

---

## Appendix A: Technical Indicator Formulas

### A.1 Log Return
```
weekly_log_return = ln(close_t) - ln(close_{t-1})
```

### A.2 RSI Enhancements
```
rsi_slope = rsi_t - rsi_{t-1}
rsi_zscore = (rsi - mean_100w) / std_100w
rsi_overbought_flag = 1 if rsi > 70 else 0
rsi_oversold_flag = 1 if rsi < 30 else 0
```

### A.3 MACD Cross Flag
```
macd_cross_flag = +1 if macd crosses above signal
                  -1 if macd crosses below signal
                   0 otherwise
```

### A.4 MA Distance
```
close_vs_sma20_pct = (close / sma_20 - 1) * 100
```

### A.5 EMA Slope
```
ema_slope_20 = ema_20_t - ema_20_{t-1}
```

### A.6 ATR Percentage
```
atr_pct = (atr_14 / close) * 100
```

### A.7 Volume Z-Score
```
volume_zscore = (volume - mean_20) / std_20
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Nov 2025 | System | Initial draft |
| 2.0 | Nov 2025 | Claude/AI | Combined Phase 1 + AI/LLM specs |

---

**End of Document**
