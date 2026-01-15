# AIAlgoTradeHits - GCP Cloud Architecture with Agentic AI Orchestration

**Project:** aialgotradehits
**Developer:** irfan.qazi@aialgotradehits.com
**Version:** 2.0
**Date:** December 2025

---

## Architecture Overview

```
                                    +-----------------------------------------+
                                    |           EXTERNAL DATA SOURCES         |
                                    +-----------------------------------------+
                                    |                                         |
                                    |   +-------------+    +---------------+  |
                                    |   | TwelveData  |    | Market News   |  |
                                    |   |     API     |    |    Feeds      |  |
                                    |   +------+------+    +-------+-------+  |
                                    |          |                   |          |
                                    +----------|-------------------|----------+
                                               |                   |
                                               v                   v
+-----------------------------------------------------------------------------------------------+
|                                    GOOGLE CLOUD PLATFORM                                       |
|                                    Project: aialgotradehits                                   |
+-----------------------------------------------------------------------------------------------+
|                                                                                               |
|   +-----------------------------------------------------------------------------------+       |
|   |                        ORCHESTRATION LAYER (Cloud Scheduler)                      |       |
|   +-----------------------------------------------------------------------------------+       |
|   |                                                                                   |       |
|   |   +---------------+  +---------------+  +---------------+  +---------------+      |       |
|   |   | stocks_daily  |  | crypto_daily  |  | forex_daily   |  | commodities   |      |       |
|   |   | (0 6 * * 1-5) |  | (0 * * * *)   |  | (0 6 * * 1-5) |  | (0 6 * * 1-5) |      |       |
|   |   +-------+-------+  +-------+-------+  +-------+-------+  +-------+-------+      |       |
|   |           |                  |                  |                  |              |       |
|   |   +-------+-------+  +-------+-------+  +-------+-------+  +-------+-------+      |       |
|   |   | etfs_daily    |  | indices_daily |  | stocks_hourly |  | crypto_hourly |      |       |
|   |   | (0 6 * * 1-5) |  | (0 6 * * 1-5) |  | (0 * * * 1-5) |  | (0 * * * *)   |      |       |
|   |   +---------------+  +---------------+  +---------------+  +---------------+      |       |
|   |                                                                                   |       |
|   +-----------------------------------------------------------------------------------+       |
|                                           |                                                   |
|                                           v                                                   |
|   +-----------------------------------------------------------------------------------+       |
|   |                     DATA INGESTION LAYER (Cloud Functions Gen2)                   |       |
|   +-----------------------------------------------------------------------------------+       |
|   |                                                                                   |       |
|   |   +-------------------+    +-------------------+    +-------------------+         |       |
|   |   | twelvedata-stocks |    | twelvedata-crypto |    | twelvedata-forex  |         |       |
|   |   |   Daily Fetcher   |    |   Daily Fetcher   |    |   Daily Fetcher   |         |       |
|   |   | +---------------+ |    | +---------------+ |    | +---------------+ |         |       |
|   |   | | Rate Limiter  | |    | | Rate Limiter  | |    | | Rate Limiter  | |         |       |
|   |   | | Async Batch   | |    | | Async Batch   | |    | | Async Batch   | |         |       |
|   |   | | Indicators    | |    | | Indicators    | |    | | Indicators    | |         |       |
|   |   | +---------------+ |    | +---------------+ |    | +---------------+ |         |       |
|   |   +--------+----------+    +--------+----------+    +--------+----------+         |       |
|   |            |                        |                        |                    |       |
|   |   +--------+----------+    +--------+----------+    +--------+----------+         |       |
|   |   | twelvedata-etfs   |    | twelvedata-indices|    | twelvedata-commod |         |       |
|   |   |   Daily Fetcher   |    |   Daily Fetcher   |    |   Daily Fetcher   |         |       |
|   |   +-------------------+    +-------------------+    +-------------------+         |       |
|   |                                                                                   |       |
|   +-----------------------------------------------------------------------------------+       |
|                                           |                                                   |
|                                           v                                                   |
|   +-----------------------------------------------------------------------------------+       |
|   |                      DATA STORAGE LAYER (BigQuery Data Warehouse)                 |       |
|   +-----------------------------------------------------------------------------------+       |
|   |                                                                                   |       |
|   |   Dataset: crypto_trading_data                                                    |       |
|   |   +---------------------------+  +---------------------------+                    |       |
|   |   |     v2_stocks_daily       |  |     v2_crypto_daily       |                    |       |
|   |   | - symbol, datetime        |  | - symbol, datetime        |                    |       |
|   |   | - OHLCV data              |  | - OHLCV data              |                    |       |
|   |   | - 29 Technical Indicators |  | - 29 Technical Indicators |                    |       |
|   |   +---------------------------+  +---------------------------+                    |       |
|   |                                                                                   |       |
|   |   +---------------------------+  +---------------------------+                    |       |
|   |   |     v2_forex_daily        |  |     v2_etfs_daily         |                    |       |
|   |   +---------------------------+  +---------------------------+                    |       |
|   |                                                                                   |       |
|   |   +---------------------------+  +---------------------------+                    |       |
|   |   |    v2_indices_daily       |  |  v2_commodities_daily     |                    |       |
|   |   +---------------------------+  +---------------------------+                    |       |
|   |                                                                                   |       |
|   |   +---------------------------+  +---------------------------+                    |       |
|   |   |    v2_*_hourly tables     |  |  v2_*_weekly_summary      |                    |       |
|   |   +---------------------------+  +---------------------------+                    |       |
|   |                                                                                   |       |
|   +-----------------------------------------------------------------------------------+       |
|                                           |                                                   |
|                                           v                                                   |
|   +-----------------------------------------------------------------------------------+       |
|   |                     AGENTIC AI LAYER (Vertex AI + Gemini)                         |       |
|   +-----------------------------------------------------------------------------------+       |
|   |                                                                                   |       |
|   |   +-------------------------------------------------------------------+           |       |
|   |   |                    AI ORCHESTRATION ENGINE                        |           |       |
|   |   |   +-----------------------------------------------------------+   |           |       |
|   |   |   |              Gemini 2.5 Pro / Flash Models                |   |           |       |
|   |   |   +-----------------------------------------------------------+   |           |       |
|   |   |                               |                                   |           |       |
|   |   |       +-----------------------+-----------------------+           |           |       |
|   |   |       |                       |                       |           |           |       |
|   |   |       v                       v                       v           |           |       |
|   |   |   +---------+          +-----------+          +-----------+       |           |       |
|   |   |   | Pattern |          |  Trading  |          |    NLP    |       |           |       |
|   |   |   | Recog.  |          |  Signals  |          |  Search   |       |           |       |
|   |   |   |  Agent  |          |   Agent   |          |   Agent   |       |           |       |
|   |   |   +---------+          +-----------+          +-----------+       |           |       |
|   |   |       |                       |                       |           |           |       |
|   |   |       v                       v                       v           |           |       |
|   |   |   +---------+          +-----------+          +-----------+       |           |       |
|   |   |   | Market  |          | Portfolio |          | Sentiment |       |           |       |
|   |   |   | Analysis|          |  Optimizer|          |  Analysis |       |           |       |
|   |   |   |  Agent  |          |   Agent   |          |   Agent   |       |           |       |
|   |   |   +---------+          +-----------+          +-----------+       |           |       |
|   |   |                                                                   |           |       |
|   |   +-------------------------------------------------------------------+           |       |
|   |                                                                                   |       |
|   |   +-------------------------------------------------------------------+           |       |
|   |   |                   AI TRAINING INFRASTRUCTURE                      |           |       |
|   |   |   +---------------------------+  +---------------------------+    |           |       |
|   |   |   | Cloud Storage Bucket      |  | Training Data Pipeline    |    |           |       |
|   |   |   | aialgotradehits-training  |  | - Historical Data         |    |           |       |
|   |   |   | - Model Artifacts         |  | - Feature Engineering     |    |           |       |
|   |   |   | - Training Docs           |  | - Model Fine-tuning       |    |           |       |
|   |   |   +---------------------------+  +---------------------------+    |           |       |
|   |   +-------------------------------------------------------------------+           |       |
|   |                                                                                   |       |
|   +-----------------------------------------------------------------------------------+       |
|                                           |                                                   |
|                                           v                                                   |
|   +-----------------------------------------------------------------------------------+       |
|   |                        API LAYER (Cloud Run - Serverless)                         |       |
|   +-----------------------------------------------------------------------------------+       |
|   |                                                                                   |       |
|   |   +-----------------------------------+    +-----------------------------------+  |       |
|   |   |       trading-api (Flask)         |    |      smart-search (Flask)         |  |       |
|   |   | +-------------------------------+ |    | +-------------------------------+ |  |       |
|   |   | | /api/stocks/history           | |    | | /api/ai/smart-search          | |  |       |
|   |   | | /api/crypto/daily/history     | |    | | /api/ai/pattern-recognition   | |  |       |
|   |   | | /api/forex/history            | |    | | /api/ai/predict               | |  |       |
|   |   | | /api/etfs/history             | |    | | /api/ai/analyze               | |  |       |
|   |   | | /api/indices/history          | |    | | /api/ai/training-docs         | |  |       |
|   |   | | /api/commodities/history      | |    | +-------------------------------+ |  |       |
|   |   | | /api/weekly/<asset_type>      | |    +-----------------------------------+  |       |
|   |   | | /api/analysis/nlp-search      | |                                          |       |
|   |   | | /api/auth/* (JWT Auth)        | |                                          |       |
|   |   | | /api/admin/* (Monitoring)     | |                                          |       |
|   |   | +-------------------------------+ |                                          |       |
|   |   +-----------------------------------+                                          |       |
|   |                                                                                   |       |
|   +-----------------------------------------------------------------------------------+       |
|                                           |                                                   |
|                                           v                                                   |
|   +-----------------------------------------------------------------------------------+       |
|   |                     FRONTEND LAYER (Cloud Run - React + Vite)                     |       |
|   +-----------------------------------------------------------------------------------+       |
|   |                                                                                   |       |
|   |   +-----------------------------------+    +-----------------------------------+  |       |
|   |   |      trading-app (React)          |    |    aialgotradehits (React)        |  |       |
|   |   | +-------------------------------+ |    | +-------------------------------+ |  |       |
|   |   | | TradingView Charts            | |    | | Landing Page                  | |  |       |
|   |   | | - Candlesticks                | |    | | User Authentication           | |  |       |
|   |   | | - RSI, MACD, Bollinger        | |    | | Subscription Management       | |  |       |
|   |   | | - Fibonacci, Elliott Wave    | |    | +-------------------------------+ |  |       |
|   |   | | - Support/Resistance          | |    +-----------------------------------+  |       |
|   |   | |                               | |                                          |       |
|   |   | | Weekly Dashboard              | |                                          |       |
|   |   | | Smart Search (NLP)            | |                                          |       |
|   |   | | AI Pattern Recognition        | |                                          |       |
|   |   | | Portfolio Tracker             | |                                          |       |
|   |   | | Admin Monitoring              | |                                          |       |
|   |   | +-------------------------------+ |                                          |       |
|   |   +-----------------------------------+                                          |       |
|   |                                                                                   |       |
|   +-----------------------------------------------------------------------------------+       |
|                                                                                               |
+-----------------------------------------------------------------------------------------------+
                                           |
                                           v
                              +------------------------+
                              |        END USERS       |
                              |  (Web Browser/Mobile)  |
                              +------------------------+
```

---

## Agentic AI Orchestration Flow

```
+-------------------------------------------------------------------------------------------+
|                            AGENTIC AI ORCHESTRATION PIPELINE                              |
+-------------------------------------------------------------------------------------------+
|                                                                                           |
|   USER QUERY                                                                              |
|       |                                                                                   |
|       v                                                                                   |
|   +-----------------------------------------------------------------------+               |
|   |                    MASTER ORCHESTRATOR AGENT                          |               |
|   |                      (Gemini 2.5 Pro)                                 |               |
|   |                                                                       |               |
|   |   1. Intent Classification                                            |               |
|   |   2. Task Decomposition                                               |               |
|   |   3. Agent Selection & Routing                                        |               |
|   |   4. Response Synthesis                                               |               |
|   +-----------------------------------------------------------------------+               |
|       |                                                                                   |
|       +------------------+------------------+------------------+                          |
|       |                  |                  |                  |                          |
|       v                  v                  v                  v                          |
|   +---------+       +---------+       +-----------+      +-----------+                   |
|   | DATA    |       | PATTERN |       | PREDICTION|      | SENTIMENT |                   |
|   | RETRIEVAL|       | ANALYSIS|       |   ENGINE  |      | ANALYSIS  |                   |
|   | AGENT   |       |  AGENT  |       |   AGENT   |      |   AGENT   |                   |
|   +---------+       +---------+       +-----------+      +-----------+                   |
|       |                  |                  |                  |                          |
|       v                  v                  v                  v                          |
|   +---------+       +---------+       +-----------+      +-----------+                   |
|   | BigQuery|       | Chart   |       | ML Models |      | News API  |                   |
|   | Tables  |       | Patterns|       | Forecasts |      | Sentiment |                   |
|   +---------+       +---------+       +-----------+      +-----------+                   |
|       |                  |                  |                  |                          |
|       +------------------+------------------+------------------+                          |
|                                    |                                                      |
|                                    v                                                      |
|   +-----------------------------------------------------------------------+               |
|   |                    RESPONSE AGGREGATION LAYER                         |               |
|   |                                                                       |               |
|   |   - Combine insights from all agents                                  |               |
|   |   - Generate coherent natural language response                       |               |
|   |   - Include confidence scores and data citations                      |               |
|   |   - Format for user consumption (charts, tables, text)                |               |
|   +-----------------------------------------------------------------------+               |
|                                    |                                                      |
|                                    v                                                      |
|                            USER RESPONSE                                                  |
|                                                                                           |
+-------------------------------------------------------------------------------------------+
```

---

## AI Agent Capabilities

### 1. Data Retrieval Agent
```
+-------------------------------------------+
|         DATA RETRIEVAL AGENT              |
+-------------------------------------------+
| Function: BigQuery SQL Generation         |
| Model: Gemini 2.5 Flash                   |
+-------------------------------------------+
| Capabilities:                             |
| - Natural language to SQL conversion      |
| - Multi-table JOINs across asset types    |
| - Time-series aggregations                |
| - Technical indicator calculations        |
| - Cross-asset correlation queries         |
+-------------------------------------------+
| Input: "Show me oversold stocks with      |
|         high volume in tech sector"       |
| Output: Structured data from BigQuery     |
+-------------------------------------------+
```

### 2. Pattern Recognition Agent
```
+-------------------------------------------+
|       PATTERN RECOGNITION AGENT           |
+-------------------------------------------+
| Function: Chart Pattern Detection         |
| Model: Gemini 2.5 Pro (Vision capable)    |
+-------------------------------------------+
| Capabilities:                             |
| - Head & Shoulders detection              |
| - Double Top/Bottom identification        |
| - Triangle patterns (ascending/descending)|
| - Flag and Pennant patterns               |
| - Candlestick pattern recognition         |
| - Elliott Wave detection                  |
| - Fibonacci level identification          |
+-------------------------------------------+
| Input: OHLCV data array                   |
| Output: Pattern type + confidence score   |
+-------------------------------------------+
```

### 3. Prediction Engine Agent
```
+-------------------------------------------+
|        PREDICTION ENGINE AGENT            |
+-------------------------------------------+
| Function: Price Movement Forecasting      |
| Model: Gemini 2.5 Pro + Custom ML         |
+-------------------------------------------+
| Capabilities:                             |
| - Short-term price predictions (1-5 days) |
| - Trend direction forecasting             |
| - Volatility predictions                  |
| - Support/Resistance level projections    |
| - Risk assessment scores                  |
+-------------------------------------------+
| Input: Historical OHLCV + indicators      |
| Output: Prediction + probability ranges   |
+-------------------------------------------+
```

### 4. Sentiment Analysis Agent
```
+-------------------------------------------+
|       SENTIMENT ANALYSIS AGENT            |
+-------------------------------------------+
| Function: Market Sentiment Scoring        |
| Model: Gemini 2.5 Flash                   |
+-------------------------------------------+
| Capabilities:                             |
| - News article sentiment analysis         |
| - Social media trend detection            |
| - Fear & Greed index interpretation       |
| - Sector sentiment aggregation            |
| - Event impact assessment                 |
+-------------------------------------------+
| Input: News feeds, social data            |
| Output: Sentiment scores (-1 to +1)       |
+-------------------------------------------+
```

---

## Cloud Scheduler Orchestration Matrix

```
+-------------------------+------------------+------------+-------------------+
| Scheduler Name          | Schedule (Cron)  | Timezone   | Target Function   |
+-------------------------+------------------+------------+-------------------+
| stocks-daily-fetcher    | 0 6 * * 1-5      | US/Eastern | twelvedata-stocks |
| crypto-daily-fetcher    | 0 */2 * * *      | UTC        | twelvedata-crypto |
| forex-daily-fetcher     | 0 6 * * 1-5      | US/Eastern | twelvedata-forex  |
| etfs-daily-fetcher      | 0 6 * * 1-5      | US/Eastern | twelvedata-etfs   |
| indices-daily-fetcher   | 0 6 * * 1-5      | US/Eastern | twelvedata-indices|
| commodities-fetcher     | 0 6 * * 1-5      | US/Eastern | twelvedata-commod |
| stocks-hourly-fetcher   | 0 * * * 1-5      | US/Eastern | stocks-hourly     |
| crypto-hourly-fetcher   | 0 * * * *        | UTC        | crypto-hourly     |
| weekly-summary-gen      | 0 0 * * 0        | US/Eastern | weekly-aggregator |
| ai-model-refresh        | 0 2 * * *        | UTC        | ai-training       |
+-------------------------+------------------+------------+-------------------+
```

---

## Technical Indicator Pipeline

```
+-----------------------------------------------------------------------------------+
|                          TECHNICAL INDICATOR CALCULATION                           |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|   RAW OHLCV DATA                                                                  |
|       |                                                                           |
|       v                                                                           |
|   +-------------------------------------------------------------------+           |
|   |                    INDICATOR ENGINE                                |           |
|   +-------------------------------------------------------------------+           |
|   |                                                                   |           |
|   |   MOMENTUM INDICATORS          TREND INDICATORS                   |           |
|   |   +------------------+         +------------------+               |           |
|   |   | RSI (14)         |         | SMA (20,50,200)  |               |           |
|   |   | MACD (12,26,9)   |         | EMA (12,26,50)   |               |           |
|   |   | Stochastic (K,D) |         | ADX              |               |           |
|   |   | Williams %R      |         | KAMA             |               |           |
|   |   | ROC              |         | TRIX             |               |           |
|   |   | Momentum         |         +------------------+               |           |
|   |   +------------------+                                            |           |
|   |                                                                   |           |
|   |   VOLATILITY INDICATORS        VOLUME INDICATORS                  |           |
|   |   +------------------+         +------------------+               |           |
|   |   | Bollinger Bands  |         | OBV              |               |           |
|   |   | ATR              |         | PVO              |               |           |
|   |   | Standard Dev     |         | Volume SMA       |               |           |
|   |   +------------------+         +------------------+               |           |
|   |                                                                   |           |
|   |   OSCILLATORS                                                     |           |
|   |   +------------------+                                            |           |
|   |   | CCI              |                                            |           |
|   |   | PPO              |                                            |           |
|   |   | Ultimate Osc     |                                            |           |
|   |   | Awesome Osc      |                                            |           |
|   |   +------------------+                                            |           |
|   |                                                                   |           |
|   +-------------------------------------------------------------------+           |
|       |                                                                           |
|       v                                                                           |
|   ENRICHED DATA --> BigQuery Tables                                               |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

---

## Security & Authentication Flow

```
+-----------------------------------------------------------------------------------+
|                            AUTHENTICATION ARCHITECTURE                             |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|   USER                                                                            |
|     |                                                                             |
|     v                                                                             |
|   +---------------------------+                                                   |
|   |     React Frontend        |                                                   |
|   |  (trading-app Cloud Run)  |                                                   |
|   +-------------+-------------+                                                   |
|                 |                                                                 |
|                 | POST /api/auth/login                                            |
|                 | {username, password}                                            |
|                 v                                                                 |
|   +---------------------------+                                                   |
|   |    Trading API            |                                                   |
|   |  (Flask + JWT)            |                                                   |
|   +-------------+-------------+                                                   |
|                 |                                                                 |
|                 | Verify credentials                                              |
|                 v                                                                 |
|   +---------------------------+                                                   |
|   |    BigQuery Users Table   |                                                   |
|   |  - password_hash (bcrypt) |                                                   |
|   |  - role (admin/user)      |                                                   |
|   |  - created_at             |                                                   |
|   +---------------------------+                                                   |
|                 |                                                                 |
|                 | Generate JWT Token                                              |
|                 v                                                                 |
|   +---------------------------+                                                   |
|   |    Return JWT Token       |                                                   |
|   |  - user_id                |                                                   |
|   |  - role                   |                                                   |
|   |  - expiry (24h)           |                                                   |
|   +---------------------------+                                                   |
|                 |                                                                 |
|                 | Store in localStorage                                           |
|                 v                                                                 |
|   +---------------------------+                                                   |
|   |  Authenticated Requests   |                                                   |
|   |  Authorization: Bearer    |                                                   |
|   +---------------------------+                                                   |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

---

## Cost Optimization Structure

```
+-----------------------------------------------------------------------------------+
|                              MONTHLY COST BREAKDOWN                                |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|   SERVICE                              ESTIMATED COST     OPTIMIZATION            |
|   +-----------------------------------------------------------------------+       |
|   | Cloud Scheduler (25 jobs)          |    $0.30       | Batch where possible   |
|   +-----------------------------------------------------------------------+       |
|   | Cloud Functions Gen2               |   $50.00       | Cold start optimize    |
|   | - 6 daily fetchers                 |                | Memory: 256MB-512MB    |
|   | - 2 hourly fetchers                |                | Timeout: 540s          |
|   +-----------------------------------------------------------------------+       |
|   | BigQuery Storage                   |   $10.00       | Partition by date      |
|   | - ~500GB historical data           |                | Cluster by symbol      |
|   | - Query processing                 |                | Use materialized views |
|   +-----------------------------------------------------------------------+       |
|   | Cloud Run                          |   $25.00       | Min instances: 0       |
|   | - trading-api                      |                | Max instances: 10      |
|   | - trading-app                      |                | CPU: 1, Memory: 512MB  |
|   +-----------------------------------------------------------------------+       |
|   | Vertex AI (Gemini)                 |   $30.00       | Use Flash for simple   |
|   | - Pattern recognition              |                | Cache common queries   |
|   | - NLP search                       |                | Batch requests         |
|   +-----------------------------------------------------------------------+       |
|   | Cloud Storage                      |    $2.00       | Lifecycle policies     |
|   | - Training data                    |                | Archive old data       |
|   +-----------------------------------------------------------------------+       |
|   | Networking                         |    $5.00       | CDN for static assets  |
|   +-----------------------------------------------------------------------+       |
|                                                                                   |
|   TOTAL ESTIMATED MONTHLY COST:        ~$122.30                                   |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

---

## Data Flow Summary

```
TwelveData API
     |
     | (Rate-limited: 800 req/day free, 5000/day Basic)
     v
Cloud Scheduler (Cron triggers)
     |
     | HTTP trigger
     v
Cloud Functions Gen2 (Python 3.12)
     |
     | - Async fetching (aiohttp)
     | - Technical indicators (pandas/numpy)
     | - Data validation
     v
BigQuery (Data Warehouse)
     |
     | - 6 asset type tables
     | - 29 technical indicators per record
     | - Partitioned by datetime
     v
Trading API (Cloud Run Flask)
     |
     | - RESTful endpoints
     | - JWT authentication
     | - Vertex AI integration
     v
React Frontend (Cloud Run Vite)
     |
     | - TradingView charts
     | - NLP search interface
     | - Real-time updates
     v
End Users
```

---

## GCP Services Used

| Service | Purpose | Configuration |
|---------|---------|---------------|
| Cloud Scheduler | Orchestration | 25+ scheduled jobs |
| Cloud Functions Gen2 | Data ingestion | Python 3.12, 256MB-512MB RAM |
| BigQuery | Data warehouse | US multi-region |
| Cloud Run | API & Frontend | Serverless containers |
| Vertex AI | Agentic AI | Gemini 2.5 Pro/Flash |
| Cloud Storage | Training data | Standard storage class |
| IAM | Access control | Service accounts |
| Cloud Logging | Monitoring | Structured logs |
| Cloud Monitoring | Observability | Custom dashboards |

---

## Contact

- **Developer:** irfan.qazi@aialgotradehits.com
- **Project:** aialgotradehits
- **Region:** us-central1
- **Status:** Production

---

*Architecture document generated December 2025*
