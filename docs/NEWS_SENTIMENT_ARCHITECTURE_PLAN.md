# News, Sentiment & Market Events Architecture Plan
## AIAlgoTradeHits - Comprehensive Financial Environment Data Integration
**Generated: December 5, 2025**

---

## Executive Summary

This document outlines a comprehensive plan to integrate news, sentiment, and market events data from multiple sources to create a unified financial environment that impacts all 7 asset types: **Stocks, Crypto, Forex, ETFs, Indices, Commodities, and Bonds**.

---

## Part 1: API Sources Analysis

### 1.1 APIs You Currently Have

| API | Key Available | Primary Use | Monthly Cost |
|-----|---------------|-------------|--------------|
| **TwelveData** | `16ee060fd4d34a628a14bcb6f0167565` | Price data, fundamentals | $229/month |
| **Finnhub** | `d4dg7t9r01qovljpm3g0d4dg7t9r01qovljpm3gg` | News, sentiment, earnings | Free tier |
| **CoinMarketCap** | `059474ae48b84628be6f4a94f9840c30` | Crypto rankings, Fear/Greed | Basic plan |
| **KrakenPro** | (In your account) | Crypto trading, OHLC | Exchange fees |
| **Google Gemini 3 Pro** | (In your GCP account) | AI analysis, NLP | Pay-per-use |

### 1.2 Recommended Additional APIs

| API | Purpose | Pricing | Priority |
|-----|---------|---------|----------|
| **Santiment** | On-chain data, social sentiment | $49-299/month | HIGH |
| **The Tie** | Institutional-grade crypto sentiment | Enterprise | MEDIUM |
| **NewsAPI.org** | General news aggregation | $449/month | MEDIUM |
| **Alpha Vantage** | Economic indicators | Free-$300/month | LOW |
| **X (Twitter) API** | Real-time social sentiment | $100-5000/month | HIGH |

---

## Part 2: Data Categories by Asset Type

### 2.1 Stocks (20,000+ US Stocks)

| Data Type | Source | Frequency | Impact Level |
|-----------|--------|-----------|--------------|
| Company News | Finnhub | Real-time | HIGH |
| Earnings Calendar | Finnhub, TwelveData | Daily | HIGH |
| Analyst Ratings | Finnhub | Weekly | MEDIUM |
| Insider Transactions | Finnhub | Daily | HIGH |
| Social Sentiment | Finnhub (Reddit, Twitter) | Hourly | MEDIUM |
| Price Targets | Finnhub | Weekly | MEDIUM |
| SEC Filings | Finnhub | Real-time | HIGH |
| Economic Events | Finnhub | Daily | HIGH |

### 2.2 Crypto (1,500+ USD Pairs)

| Data Type | Source | Frequency | Impact Level |
|-----------|--------|-----------|--------------|
| Fear & Greed Index | CoinMarketCap | Hourly | HIGH |
| Social Sentiment | Santiment, Finnhub | Hourly | HIGH |
| On-Chain Metrics | Santiment | Daily | HIGH |
| Exchange Flows | Santiment | Hourly | HIGH |
| Whale Transactions | Santiment | Real-time | HIGH |
| Development Activity | Santiment | Daily | MEDIUM |
| Twitter Mentions | X API, Santiment | Hourly | MEDIUM |
| Reddit Sentiment | Finnhub | Hourly | MEDIUM |

### 2.3 Forex (500+ Pairs)

| Data Type | Source | Frequency | Impact Level |
|-----------|--------|-----------|--------------|
| Central Bank News | Finnhub | Real-time | CRITICAL |
| Economic Calendar | Finnhub | Daily | CRITICAL |
| Interest Rate Decisions | Finnhub | As released | CRITICAL |
| GDP Reports | Finnhub | Quarterly | HIGH |
| Employment Data | Finnhub | Monthly | HIGH |
| Inflation Data | Finnhub | Monthly | HIGH |

### 2.4 ETFs (5,000+)

| Data Type | Source | Frequency | Impact Level |
|-----------|--------|-----------|--------------|
| Holdings Changes | Finnhub | Daily | HIGH |
| Sector Rotation | TwelveData | Daily | MEDIUM |
| Flow Data | Finnhub | Daily | HIGH |
| Expense Ratio Changes | Finnhub | Weekly | LOW |

### 2.5 Indices (500+)

| Data Type | Source | Frequency | Impact Level |
|-----------|--------|-----------|--------------|
| Index Rebalancing | Finnhub | Quarterly | HIGH |
| Sector Performance | TwelveData | Daily | MEDIUM |
| Market Breadth | TwelveData | Daily | HIGH |

### 2.6 Commodities (100+)

| Data Type | Source | Frequency | Impact Level |
|-----------|--------|-----------|--------------|
| Supply/Demand Reports | NewsAPI | Weekly | HIGH |
| Weather Events | NewsAPI | Daily | HIGH |
| Geopolitical News | Finnhub | Real-time | CRITICAL |
| OPEC Announcements | NewsAPI | As released | CRITICAL |
| Inventory Reports | Finnhub | Weekly | HIGH |

### 2.7 Bonds

| Data Type | Source | Frequency | Impact Level |
|-----------|--------|-----------|--------------|
| Yield Curve | TwelveData | Daily | CRITICAL |
| Fed Announcements | Finnhub | As released | CRITICAL |
| Credit Ratings | Finnhub | As released | HIGH |
| Treasury Auctions | Finnhub | Weekly | HIGH |

---

## Part 3: Finnhub Integration Specification

### 3.1 Available Endpoints (Already in Your Code)

Based on `explore_finnhub_api.py`, you have access to:

```
✅ Real-time stock quotes
✅ Company profiles & fundamentals
✅ Market news (general + company-specific)
✅ News sentiment analysis
✅ Social sentiment (Reddit, Twitter)
✅ Analyst recommendations & price targets
✅ Earnings calendar & surprises
✅ Financial statements
✅ Insider trading transactions
✅ Stock splits history
✅ Economic calendar
✅ ETF holdings & profiles
✅ Cryptocurrency data
✅ Forex rates
```

### 3.2 News Endpoints

```python
# General Market News
GET /news?category=general  # Categories: general, forex, crypto, merger

# Company-Specific News
GET /company-news?symbol=AAPL&from=2025-01-01&to=2025-12-05

# News Sentiment Score
GET /news-sentiment?symbol=AAPL
# Returns: sentimentScore, bullishPercent, bearishPercent, articlesInLastWeek
```

### 3.3 Social Sentiment Endpoint

```python
GET /stock/social-sentiment?symbol=AAPL
# Returns: Reddit mentions, positive/negative mentions, sentiment score
```

### 3.4 Economic Calendar

```python
GET /calendar/economic
# Returns: event, time, country, impact, estimate, previous, actual
```

---

## Part 4: CoinMarketCap Integration Specification

### 4.1 Available Endpoints

```python
BASE_URL = "https://pro-api.coinmarketcap.com/v1"

# Latest Listings
GET /cryptocurrency/listings/latest
# Returns: Top cryptos by market cap with price, volume, changes

# Fear & Greed Index
GET /fear-and-greed/latest
# Returns: value (0-100), value_classification (Fear/Greed)

# Global Metrics
GET /global-metrics/quotes/latest
# Returns: total_market_cap, btc_dominance, defi_volume, stablecoin_volume

# Crypto Categories
GET /cryptocurrency/categories
# Returns: DeFi, Layer-1, Meme coins, etc. with market data
```

### 4.2 Fear & Greed Index Components

The CMC Fear & Greed Index analyzes:
1. **Price Momentum** - Top 10 crypto performance
2. **Volatility** - BTC/ETH implied volatility indices
3. **Derivatives Market** - Put/Call ratios
4. **Market Composition** - BTC dominance, Stablecoin Supply Ratio
5. **Social Trends** - Keyword searches, engagement metrics

---

## Part 5: Santiment Integration Specification (Recommended)

### 5.1 Why Santiment?

Santiment is the **market leader for sentiment metrics in digital assets since 2014**. They offer:
- 500+ on-chain metrics
- Coverage of 2500+ crypto assets
- Social media sentiment analysis
- Development activity tracking

### 5.2 Key Metrics Available

```python
# Install: pip install sanpy

from sanpy import san

# Network Activity
san.get("daily_active_addresses/bitcoin")
san.get("transaction_volume/ethereum")

# Sentiment Metrics
san.get("sentiment_positive_total/bitcoin")
san.get("sentiment_negative_total/bitcoin")
san.get("social_volume_total/bitcoin")

# Exchange Flows (Whale Tracking)
san.get("exchange_inflow/bitcoin")
san.get("exchange_outflow/bitcoin")

# Development Activity
san.get("dev_activity/ethereum")

# On-Chain Metrics
san.get("nvt/bitcoin")  # Network Value to Transactions
san.get("mvrv/bitcoin")  # Market Value to Realized Value
```

### 5.3 Pricing

| Plan | Price | API Calls | Features |
|------|-------|-----------|----------|
| Free | $0 | Limited | 3-month historical, basic metrics |
| Pro | $49/month | 10,000/day | Full historical, 200+ metrics |
| Pro+ | $99/month | 50,000/day | Real-time data, 500+ metrics |
| Enterprise | Custom | Unlimited | Custom feeds, webhook support |

---

## Part 6: X (Twitter) Integration Specification

### 6.1 Options for Twitter Data

**Option A: Official X API**
- Cost: $100/month (Basic) to $5,000/month (Pro)
- Access: Full firehose for $cashtags and crypto mentions
- Compliance: Full compliance with X terms

**Option B: Third-Party Aggregators**
- EODHD Tweets Sentiment API (aggregated daily)
- The Tie (institutional-grade)
- LunarCrush (crypto-focused)

### 6.2 S&P 500 X Sentiment Index

X offers an official **S&P 500 X Sentiment Index** that:
- Analyzes $cashtag posts ($AAPL, $TSLA, etc.)
- Tracks sentiment for top publicly-traded companies
- Powered by S&P Dow Jones Indices rules

### 6.3 Data Points to Capture

```json
{
  "symbol": "AAPL",
  "tweet_volume_24h": 15432,
  "positive_sentiment": 0.65,
  "negative_sentiment": 0.20,
  "neutral_sentiment": 0.15,
  "influencer_mentions": 45,
  "trending_rank": 3,
  "sentiment_change_24h": 0.05
}
```

---

## Part 7: Database Schema Design

### 7.1 BigQuery Tables Structure

```sql
-- Market News Table
CREATE TABLE crypto_trading_data.market_news (
  id STRING,
  headline STRING,
  summary STRING,
  source STRING,
  source_url STRING,
  category STRING,  -- general, forex, crypto, merger, company
  related_symbols ARRAY<STRING>,
  sentiment_score FLOAT64,
  sentiment_label STRING,  -- positive, negative, neutral
  published_at TIMESTAMP,
  fetched_at TIMESTAMP,
  api_source STRING  -- finnhub, coinmarketcap, newsapi
);

-- Asset Sentiment Table
CREATE TABLE crypto_trading_data.asset_sentiment (
  symbol STRING,
  asset_type STRING,  -- stock, crypto, forex, etf, index, commodity, bond
  datetime TIMESTAMP,

  -- Finnhub Sentiment
  finnhub_sentiment_score FLOAT64,
  finnhub_bullish_percent FLOAT64,
  finnhub_bearish_percent FLOAT64,
  articles_last_week INT64,

  -- Social Sentiment
  reddit_mentions INT64,
  reddit_positive INT64,
  reddit_negative INT64,
  twitter_mentions INT64,
  twitter_sentiment FLOAT64,

  -- Analyst Data
  analyst_strong_buy INT64,
  analyst_buy INT64,
  analyst_hold INT64,
  analyst_sell INT64,
  analyst_strong_sell INT64,
  price_target_high FLOAT64,
  price_target_mean FLOAT64,
  price_target_low FLOAT64,

  fetched_at TIMESTAMP
);

-- Crypto Sentiment Table (Santiment + CoinMarketCap)
CREATE TABLE crypto_trading_data.crypto_sentiment (
  symbol STRING,
  datetime TIMESTAMP,

  -- Fear & Greed (CoinMarketCap)
  fear_greed_value INT64,
  fear_greed_label STRING,

  -- Social Volume (Santiment)
  social_volume_total INT64,
  social_volume_reddit INT64,
  social_volume_telegram INT64,
  social_volume_twitter INT64,
  sentiment_positive FLOAT64,
  sentiment_negative FLOAT64,
  sentiment_balance FLOAT64,

  -- On-Chain Metrics (Santiment)
  daily_active_addresses INT64,
  transaction_volume FLOAT64,
  exchange_inflow FLOAT64,
  exchange_outflow FLOAT64,
  nvt_ratio FLOAT64,
  mvrv_ratio FLOAT64,

  -- Development Activity
  dev_activity_score FLOAT64,
  github_commits_30d INT64,

  fetched_at TIMESTAMP
);

-- Economic Events Table
CREATE TABLE crypto_trading_data.economic_events (
  event_id STRING,
  event_name STRING,
  country STRING,
  datetime TIMESTAMP,
  impact STRING,  -- low, medium, high
  forecast FLOAT64,
  previous FLOAT64,
  actual FLOAT64,
  currency STRING,
  event_type STRING,  -- interest_rate, gdp, employment, inflation, fed
  fetched_at TIMESTAMP
);

-- Insider Transactions Table
CREATE TABLE crypto_trading_data.insider_transactions (
  symbol STRING,
  insider_name STRING,
  position STRING,
  transaction_type STRING,  -- buy, sell, exercise
  transaction_date DATE,
  shares INT64,
  price FLOAT64,
  value FLOAT64,
  shares_owned_after INT64,
  fetched_at TIMESTAMP
);

-- Earnings Calendar Table
CREATE TABLE crypto_trading_data.earnings_calendar (
  symbol STRING,
  company_name STRING,
  report_date DATE,
  fiscal_quarter STRING,
  eps_estimate FLOAT64,
  eps_actual FLOAT64,
  eps_surprise FLOAT64,
  eps_surprise_percent FLOAT64,
  revenue_estimate FLOAT64,
  revenue_actual FLOAT64,
  time_of_day STRING,  -- before_market, after_market
  fetched_at TIMESTAMP
);
```

---

## Part 8: Data Collection Schedule

### 8.1 Cloud Function Schedule

| Function Name | Data Type | Frequency | Asset Types |
|---------------|-----------|-----------|-------------|
| `fetch-market-news` | News articles | Every 15 min | All |
| `fetch-asset-sentiment` | Sentiment scores | Hourly | Stocks, ETFs |
| `fetch-crypto-sentiment` | Crypto sentiment | Hourly | Crypto |
| `fetch-fear-greed` | Fear/Greed Index | Every 30 min | Crypto |
| `fetch-economic-events` | Economic calendar | Daily | Forex, Bonds |
| `fetch-insider-trades` | Insider transactions | Daily | Stocks |
| `fetch-earnings-calendar` | Earnings | Daily | Stocks |
| `fetch-analyst-ratings` | Analyst data | Daily | Stocks |
| `fetch-social-sentiment` | Social media | Every 2 hours | Stocks, Crypto |

### 8.2 API Call Budget

| API | Rate Limit | Daily Budget | Monthly Budget |
|-----|------------|--------------|----------------|
| Finnhub | 60/min | 86,400 | 2,592,000 |
| CoinMarketCap | 333/day (Basic) | 333 | 10,000 |
| TwelveData | 600 credits/min | ~792,000 | 23,760,000 |
| Santiment (Pro) | 10,000/day | 10,000 | 300,000 |

---

## Part 9: Frontend Sentiment Dashboard Components

### 9.1 Proposed UI Sections

```
/sentiment
├── Market Overview
│   ├── Fear & Greed Gauge (Crypto)
│   ├── Market Mood Indicator (Stocks)
│   └── Economic Calendar Widget
├── Asset-Specific Sentiment
│   ├── Sentiment Score Card
│   ├── News Feed (filterable)
│   ├── Social Media Mentions Chart
│   └── Analyst Ratings Display
├── News Center
│   ├── Breaking News Ticker
│   ├── Category Filters (General, Crypto, Forex, etc.)
│   ├── Company-Specific News
│   └── Sentiment Heatmap
└── Analytics
    ├── Sentiment vs Price Correlation
    ├── Volume vs Social Mentions
    └── Insider Trading Activity
```

### 9.2 Components to Build

1. **FearGreedGauge.jsx** - Visual gauge for crypto market sentiment
2. **NewsFeed.jsx** - Real-time news with sentiment labels
3. **SentimentChart.jsx** - Time-series sentiment visualization
4. **SocialMentions.jsx** - Twitter/Reddit activity tracker
5. **EconomicCalendar.jsx** - Upcoming events with impact ratings
6. **InsiderTracker.jsx** - Latest insider transactions
7. **AnalystRatings.jsx** - Buy/Hold/Sell distribution
8. **SentimentHeatmap.jsx** - Market-wide sentiment overview

---

## Part 10: Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Create BigQuery sentiment tables
- [ ] Build Finnhub news fetcher Cloud Function
- [ ] Build Finnhub sentiment fetcher Cloud Function
- [ ] Add CoinMarketCap Fear/Greed fetcher
- [ ] Create basic News Feed component

### Phase 2: Social Sentiment (Week 3-4)
- [ ] Integrate Finnhub social sentiment
- [ ] Evaluate and subscribe to Santiment API
- [ ] Build crypto sentiment Cloud Functions
- [ ] Create Sentiment Dashboard page
- [ ] Add Fear/Greed Gauge component

### Phase 3: Economic Events (Week 5-6)
- [ ] Build economic calendar fetcher
- [ ] Create insider transactions tracker
- [ ] Build earnings calendar integration
- [ ] Create Economic Calendar component
- [ ] Add Insider Tracker component

### Phase 4: Advanced Analytics (Week 7-8)
- [ ] Link sentiment to price data
- [ ] Build sentiment vs price correlation charts
- [ ] Implement AI-powered sentiment analysis with Gemini
- [ ] Create predictive sentiment signals
- [ ] Build alerting system for sentiment changes

### Phase 5: X (Twitter) Integration (Week 9-10)
- [ ] Evaluate X API options
- [ ] Implement Twitter sentiment fetcher
- [ ] Create social mentions tracker
- [ ] Build real-time Twitter feed widget

---

## Part 11: Estimated Monthly Costs

| Service | Current Cost | With Sentiment | Notes |
|---------|--------------|----------------|-------|
| TwelveData | $229 | $229 | Already subscribed |
| Finnhub | $0 | $0 | Free tier sufficient |
| CoinMarketCap | ~$0 | $0-79 | Basic free, may need Startup |
| Santiment | $0 | $49-99 | Recommended Pro plan |
| X (Twitter) API | $0 | $100 | Basic tier for sentiment |
| NewsAPI | $0 | $0-449 | Optional for broader coverage |
| GCP (BigQuery) | ~$5 | ~$15 | Increased storage |
| GCP (Cloud Functions) | ~$126 | ~$180 | More functions |
| GCP (Cloud Run) | ~$5 | ~$10 | API traffic increase |

**Total Estimated: $578-1,161/month** (depending on API choices)

---

## Part 12: Quick Start - Recommended Actions

### Immediate (Today)
1. ✅ You have Finnhub API ready - start fetching news/sentiment NOW
2. ✅ You have CoinMarketCap API ready - add Fear/Greed Index
3. Create BigQuery sentiment tables

### This Week
1. Build Cloud Function for Finnhub news fetcher
2. Build Cloud Function for CoinMarketCap Fear/Greed
3. Create basic sentiment dashboard page

### This Month
1. Evaluate Santiment trial ($0 for basic)
2. Consider X API Basic tier ($100/month)
3. Build comprehensive sentiment components

---

## Appendix A: API Documentation Links

- [Finnhub API Docs](https://finnhub.io/docs/api)
- [CoinMarketCap API Docs](https://coinmarketcap.com/api/documentation/v1/)
- [Santiment API Docs](https://academy.santiment.net/sanapi/)
- [X Developer Platform](https://developer.x.com/)
- [TwelveData API Docs](https://twelvedata.com/docs)
- [Santiment Python Client (sanpy)](https://github.com/santiment/sanpy)

---

## Appendix B: Sample API Responses

### Finnhub News Sentiment Response
```json
{
  "buzz": {
    "articlesInLastWeek": 48,
    "weeklyAverage": 52.5,
    "buzz": 0.914
  },
  "sentiment": {
    "bullishPercent": 0.72,
    "bearishPercent": 0.28
  },
  "companyNewsScore": 0.85,
  "sectorAverageNewsScore": 0.65,
  "symbol": "AAPL"
}
```

### CoinMarketCap Fear/Greed Response
```json
{
  "data": {
    "value": 27,
    "value_classification": "Fear",
    "timestamp": "2025-12-05T00:00:00.000Z",
    "time_until_update": "18:30:00"
  }
}
```

### Santiment Social Volume Response
```json
{
  "datetime": "2025-12-05T00:00:00Z",
  "value": 15432,
  "sentiment_positive": 0.65,
  "sentiment_negative": 0.22,
  "sentiment_balance": 0.43
}
```

---

## Part 13: Database Optimization Recommendations

### 13.1 Current Database State (Audit: December 5, 2025)

| Metric | Current Value | Issue |
|--------|---------------|-------|
| **Total Tables** | 140 | Highly fragmented |
| **Total Rows** | 7.5M | Spread across too many tables |
| **Total Size** | 2.35 GB | Manageable |
| **Empty Tables** | 26 | Wasted resources |
| **Duplicate Tables** | ~15 pairs | Identical data in multiple tables |

### 13.2 Data Distribution by Asset Type

| Asset Type | Tables | Rows | % of Data |
|------------|--------|------|-----------|
| Stocks | 35 | 4,118,838 | 54.8% |
| ETFs | 15 | 1,356,436 | 18.1% |
| Crypto | 30 | 925,126 | 12.3% |
| Forex | 16 | 448,862 | 6.0% |
| Commodities | 15 | 411,142 | 5.5% |
| Indices | 15 | 235,141 | 3.1% |
| Other | 12 | 15,606 | 0.2% |
| Bonds | 2 | 1,532 | 0.0% |

### 13.3 Table Consolidation Strategy

**Migrate 140 tables → 7 unified tables + 3 support tables**

```sql
-- Unified table template (applies to all asset types)
CREATE TABLE `cryptobot-462709.crypto_trading_data.{asset}_unified` (
  symbol STRING NOT NULL,
  timeframe STRING NOT NULL,  -- 'weekly', 'daily', 'hourly', '5min'
  datetime TIMESTAMP NOT NULL,

  -- OHLCV
  open FLOAT64, high FLOAT64, low FLOAT64, close FLOAT64, volume INT64,

  -- Indicators (29 total)
  sma_20 FLOAT64, sma_50 FLOAT64, sma_200 FLOAT64,
  ema_12 FLOAT64, ema_26 FLOAT64, ema_50 FLOAT64,
  rsi FLOAT64, macd FLOAT64, macd_signal FLOAT64, macd_histogram FLOAT64,
  bollinger_upper FLOAT64, bollinger_middle FLOAT64, bollinger_lower FLOAT64,
  atr FLOAT64, adx FLOAT64, cci FLOAT64, obv INT64,
  -- ... remaining indicators

  -- Metadata
  exchange STRING, currency STRING, data_source STRING
)
PARTITION BY DATE(datetime)
CLUSTER BY symbol, timeframe;
```

**New unified tables:**
1. `stocks_unified` (replaces 35 tables)
2. `crypto_unified` (replaces 30 tables)
3. `etfs_unified` (replaces 15 tables)
4. `forex_unified` (replaces 16 tables)
5. `commodities_unified` (replaces 15 tables)
6. `indices_unified` (replaces 15 tables)
7. `bonds_unified` (replaces 2 tables)

### 13.4 Sentiment Tables Integration

The new sentiment tables from this plan should follow the unified pattern:

```sql
-- Unified sentiment table (combines all sentiment sources)
CREATE TABLE `cryptobot-462709.crypto_trading_data.sentiment_unified` (
  symbol STRING NOT NULL,
  asset_type STRING NOT NULL,  -- 'stock', 'crypto', 'forex', etc.
  datetime TIMESTAMP NOT NULL,

  -- Finnhub Sentiment
  finnhub_score FLOAT64,
  finnhub_bullish_pct FLOAT64,
  finnhub_bearish_pct FLOAT64,

  -- Social Sentiment
  reddit_mentions INT64,
  twitter_mentions INT64,
  social_sentiment_score FLOAT64,

  -- Crypto-specific (nullable for non-crypto)
  fear_greed_value INT64,
  fear_greed_label STRING,
  exchange_inflow FLOAT64,
  exchange_outflow FLOAT64,

  -- Metadata
  data_source STRING
)
PARTITION BY DATE(datetime)
CLUSTER BY asset_type, symbol;
```

### 13.5 Empty Tables to Delete (26 tables)

```sql
-- Execute to clean up empty tables
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.5min_stock`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.active_trading_list`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.bonds_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.commodities_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.commodities_hourly_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.crypto_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.crypto_hourly_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.etfs_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.etfs_hourly_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.forex_5min_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.forex_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.forex_hourly_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.hourly_stock`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.indices_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.indices_hourly_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.market_news_sentiment`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.scheduler_summary_view`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.social_sentiment`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.stock_5min_top10_gainers`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.stock_hourly_data`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.stocks_5min_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.stocks_daily_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.stocks_hourly_td`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.trading_sessions`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.unified_weekly_analysis`;
DROP TABLE IF EXISTS `cryptobot-462709.crypto_trading_data.user_trades`;
```

### 13.6 Data Quality Monitoring

New monitoring endpoints added to `cloud_function_monitoring`:

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/monitoring?endpoint=data-quality` | Check freshness per category | Freshness status, row counts |
| `/monitoring?endpoint=empty-tables` | List empty tables | Table names ready for deletion |
| `/monitoring?endpoint=duplicates` | Find duplicate tables | Tables with identical row counts |
| `/monitoring?endpoint=category-summary` | Asset category breakdown | Rows and counts per category |
| `/monitoring?endpoint=full` | Complete health check | All metrics combined |

### 13.7 Expected Benefits After Optimization

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Tables to manage | 140 | 10 | **93% reduction** |
| Query complexity | High | Low | **Single table per asset** |
| Storage cost | ~$2/month | ~$1/month | **50% reduction** |
| Query cost | Variable | Optimized | **90% reduction with partitions** |
| Data freshness checks | Manual | Automated | **Real-time monitoring** |

### 13.8 Migration Timeline

| Phase | Tasks | Status |
|-------|-------|--------|
| Phase 1 | Create unified tables, backup existing | Pending |
| Phase 2 | Migrate data with deduplication | Pending |
| Phase 3 | Validate row counts match | Pending |
| Phase 4 | Update API endpoints, rename old tables | Pending |
| Phase 5 | Delete deprecated tables after 7-day monitoring | Pending |

**See `TABLE_CONSOLIDATION_PLAN.md` for detailed migration scripts.**

---

*Document Version: 1.1*
*Updated: December 5, 2025 - Added Database Optimization section*
*Created by: Claude Code for AIAlgoTradeHits*
