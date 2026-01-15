





# US Stock Market Data Implementation Plan
## Twelve Data API Pro Plan ($229/month)

**Generated:** November 20, 2025
**API Key:** `16ee060fd4d34a628a14bcb6f0167565`
**Plan:** Pro (1,597 API calls/minute + 1,500 WebSocket credits)

---

## Current API Capabilities - VERIFIED

### ✅ Working Endpoints Tested:
1. **API Usage Monitoring** - Track credit consumption
2. **Real-Time Quotes** - Live stock prices with 52-week data
3. **Time Series Data** - Historical OHLCV (multiple intervals)
4. **Market Movers** - Top gainers/losers in real-time
5. **Stock Lists** - 20,072 US stocks available
6. **Technical Indicators** - RSI, MACD, and 50+ more
7. **Exchange Data** - 96 global exchanges (10+ US exchanges)

### 📊 Available US Data:
- **Total US Stocks:** 20,072+
- **US Exchanges:** NYSE, NASDAQ, OTC, ICE, IEX, ARCX
- **Asset Types:** Stocks, ETFs, Mutual Funds, Bonds, Options
- **Intervals:** 1min, 5min, 15min, 30min, 1hour, 4hour, 1day, 1week, 1month
- **Pre/Post Market:** Available for US equities ✅

---

## Phase 1: US Stock Data Pipeline (Priority)

### A. BigQuery Schema Design

**Dataset:** `cryptobot-462709.stock_trading_data`

**Tables to Create:**

#### 1. `us_stocks_daily` (Daily OHLCV + Indicators)
```sql
Fields (45 total):
- symbol (STRING)
- name (STRING)
- exchange (STRING)
- mic_code (STRING)
- currency (STRING)
- datetime (TIMESTAMP)
- date (DATE)
- open (FLOAT64)
- high (FLOAT64)
- low (FLOAT64)
- close (FLOAT64)
- volume (INT64)
- adjusted_close (FLOAT64)

# Technical Indicators (32 fields)
- rsi (FLOAT64)
- macd (FLOAT64)
- macd_signal (FLOAT64)
- macd_hist (FLOAT64)
- bb_upper (FLOAT64)
- bb_middle (FLOAT64)
- bb_lower (FLOAT64)
- sma_20 (FLOAT64)
- sma_50 (FLOAT64)
- sma_200 (FLOAT64)
- ema_12 (FLOAT64)
- ema_26 (FLOAT64)
- ema_50 (FLOAT64)
- adx (FLOAT64)
- cci (FLOAT64)
- stoch_k (FLOAT64)
- stoch_d (FLOAT64)
- atr (FLOAT64)
- obv (FLOAT64)
- williams_r (FLOAT64)
- roc (FLOAT64)
- momentum (FLOAT64)
- ppo (FLOAT64)
- pvo (FLOAT64)
- trix (FLOAT64)
- kama (FLOAT64)
- awesome_osc (FLOAT64)
- ultimate_osc (FLOAT64)
- natr (FLOAT64)
- variance (FLOAT64)
- stddev (FLOAT64)
- correl (FLOAT64)

# Metadata
- data_source (STRING) = "twelve_data"
- fetch_timestamp (TIMESTAMP)
```

#### 2. `us_stocks_hourly` (Hourly Data + Indicators)
Same schema as daily with hourly granularity

#### 3. `us_stocks_5min_top100` (5-Minute Top Gainers)
Same schema for top 100 most active/volatile stocks

#### 4. `us_stocks_fundamentals` (Company Fundamentals)
```sql
Fields:
- symbol (STRING)
- name (STRING)
- sector (STRING)
- industry (STRING)
- market_cap (FLOAT64)
- pe_ratio (FLOAT64)
- dividend_yield (FLOAT64)
- earnings_date (DATE)
- last_updated (TIMESTAMP)
```

#### 5. `us_market_movers` (Daily Top Movers)
```sql
Fields:
- symbol (STRING)
- name (STRING)
- exchange (STRING)
- datetime (TIMESTAMP)
- last_price (FLOAT64)
- percent_change (FLOAT64)
- volume (INT64)
- category (STRING) -- "gainer" or "loser"
- fetch_date (DATE)
```

---

## Phase 2: Cloud Functions Implementation

### Function 1: `daily-stock-fetcher`
**Schedule:** `0 0 * * *` (Midnight ET)
**Memory:** 512MB
**Timeout:** 540s (9 minutes)
**Location:** `us-central1`

**Logic:**
1. Query Twelve Data for S&P 500 stocks (500 symbols)
2. Fetch daily OHLCV data with 200-day lookback
3. Calculate 32 technical indicators using TA-Lib
4. Check BigQuery for duplicates (composite key: symbol + date)
5. Upload only new records
6. Log failures and summary

**API Credits:** ~500 credits (1 per symbol)

---

### Function 2: `hourly-stock-fetcher`
**Schedule:** `0 * * * *` (Every hour)
**Memory:** 512MB
**Timeout:** 540s
**Location:** `us-central1`

**Logic:**
1. Fetch hourly data for S&P 500 stocks
2. Include pre/post-market data if available
3. Calculate indicators on 50+ hour window
4. Duplicate detection by symbol + hour
5. Upload to `us_stocks_hourly`

**API Credits:** ~500 credits/hour = 12,000/day

---

### Function 3: `fivemin-stock-top100-fetcher`
**Schedule:** `*/5 * * * *` (Every 5 minutes during market hours)
**Memory:** 256MB
**Timeout:** 300s
**Location:** `us-central1`

**Logic:**
1. Query `us_stocks_hourly` for top 100 gainers (last hour)
2. Fetch 5-minute OHLCV for these 100 symbols
3. Calculate short-term indicators (RSI, MACD, BB)
4. Upload to `us_stocks_5min_top100`

**API Credits:** ~100 credits every 5 min = 1,200/hour (market hours only)

---

### Function 4: `market-movers-fetcher`
**Schedule:** `0 9,12,15 * * 1-5` (3x daily during market hours)
**Memory:** 128MB
**Timeout:** 60s
**Location:** `us-central1`

**Logic:**
1. Call `/market_movers/stocks` endpoint
2. Store top 25 gainers and losers
3. Upload to `us_market_movers` table

**API Credits:** 1 credit per call = 3/day

---

### Function 5: `fundamentals-weekly-fetcher`
**Schedule:** `0 2 * * 0` (Sunday 2 AM)
**Memory:** 1GB
**Timeout:** 540s
**Location:** `us-central1`

**Logic:**
1. Fetch fundamentals for S&P 500 (quarterly update)
2. Get earnings calendar for next 30 days
3. Update `us_stocks_fundamentals` table

**API Credits:** ~100-500 credits/week (fundamentals are expensive)

---

## Phase 3: Rate Limiting & Optimization

### Strategy:
1. **Batch Requests:** Use Twelve Data's batch endpoint
   ```
   GET /time_series?symbol=AAPL,GOOGL,MSFT&interval=1day
   ```
   Credits: 1 per symbol (same as individual)

2. **Smart Scheduling:**
   - Daily fetcher: Midnight (no market conflict)
   - Hourly fetcher: Market hours only (9 AM - 4 PM ET)
   - 5-min fetcher: Market hours + 1 hour buffer

3. **Rate Limit Buffer:**
   - Max: 1,597 calls/minute
   - Target: 1,200 calls/minute (75% utilization)
   - Implement `time.sleep(0.05)` between calls

4. **WebSocket for Real-Time:**
   - Use 1,500 WS credits for live price streaming
   - Reserve for top 100 most traded stocks
   - Implement in Phase 4

---

## Phase 4: Stock Data Integration with Trading App

### Frontend Updates (`stock-price-app/`)

#### 1. Stock Search Component
```jsx
// Add stock search to Navigation.jsx
<StockSearch
  onSelectSymbol={handleSymbolChange}
  apiKey={TWELVE_DATA_API_KEY}
/>
```

#### 2. Stock Chart Component (Mirror Crypto Design)
```jsx
<TradingViewChart
  symbol={symbol}
  interval={interval}
  dataSource="stocks"  // Add toggle for stocks vs crypto
  showIndicators={true}
  showPrePostMarket={true}
/>
```

#### 3. Market Movers Widget
```jsx
<MarketMoversPanel
  type="gainers"  // or "losers"
  limit={10}
  refreshInterval={300000}  // 5 minutes
/>
```

#### 4. Stock Screener
```jsx
<StockScreener
  filters={{
    rsi: { min: 30, max: 70 },
    volume: { min: 1000000 },
    price: { min: 10, max: 500 }
  }}
/>
```

---

## Phase 5: API Cost Management

### Monthly Cost Estimate:

**Daily Function:**
- 500 stocks × 1 credit = 500 credits/day
- 30 days = 15,000 credits/month
- API Time: ~30 seconds/day

**Hourly Function:**
- 500 stocks × 24 hours = 12,000 credits/day
- 30 days = 360,000 credits/month
- API Time: ~15 minutes/day

**5-Min Function (Market Hours Only):**
- 100 stocks × 12 calls/hour × 6.5 hours × 22 trading days
- = 171,600 credits/month
- API Time: ~5 minutes/day

**Market Movers:**
- 3 calls/day × 22 trading days = 66 credits/month

**Fundamentals:**
- ~500 credits/week = 2,000 credits/month

**Total Monthly Credits:** ~548,666 credits
**API Limit:** 1,597 calls/min = 2,300,000 calls/month (plenty of headroom)

---

## Phase 6: Advanced Features (Future)

### A. WebSocket Real-Time Streaming
```python
from twelvedata import TDClient

td = TDClient(apikey=API_KEY)

# Stream top 50 stocks
symbols = ["AAPL", "GOOGL", "MSFT", ...]

ws = td.websocket(symbols=symbols)
ws.subscribe(symbols)
ws.connect()
```

### B. Sentiment Analysis Integration
- Parse news API for stock mentions
- Calculate sentiment scores
- Store in `us_stocks_sentiment` table

### C. Options Data
- Fetch options chains
- Calculate implied volatility
- Track unusual options activity

### D. Backtesting Engine
- Use historical data from BigQuery
- Test trading strategies
- Generate performance reports

---

## Implementation Timeline

### Week 1: Foundation
- ✅ API key configured
- ✅ Test endpoints verified
- [ ] Create BigQuery schema
- [ ] Build `daily-stock-fetcher` function
- [ ] Deploy and test daily collection

### Week 2: Hourly & 5-Min Data
- [ ] Build `hourly-stock-fetcher`
- [ ] Build `fivemin-stock-top100-fetcher`
- [ ] Set up Cloud Schedulers
- [ ] Monitor data collection

### Week 3: Market Movers & Fundamentals
- [ ] Build `market-movers-fetcher`
- [ ] Build `fundamentals-weekly-fetcher`
- [ ] Verify all data pipelines
- [ ] Performance optimization

### Week 4: Frontend Integration
- [ ] Add stock search to UI
- [ ] Update chart component for stocks
- [ ] Build market movers widget
- [ ] Deploy updated trading app

---

## Stock Universe Options

### Option 1: S&P 500 (Recommended)
- **Count:** 500 stocks
- **Coverage:** Large-cap US companies
- **API Cost:** Low (500 credits/fetch)
- **Quality:** High liquidity, reliable data

### Option 2: Russell 1000
- **Count:** 1,000 stocks
- **Coverage:** Large + mid-cap
- **API Cost:** Medium (1,000 credits/fetch)
- **Quality:** Good liquidity

### Option 3: Full US Market
- **Count:** 20,072 stocks
- **Coverage:** All listed US stocks
- **API Cost:** Very High (20k+ credits/fetch)
- **Quality:** Mixed (many low-volume stocks)

### Recommendation: Start with S&P 500
- Most actively traded
- Best data quality
- Manageable API costs
- Expand later if needed

---

## Next Steps

1. **Confirm Stock Universe:** Which stocks do you want to track? (S&P 500 recommended)
2. **Prioritize Features:** Which functions to build first?
3. **Set Target Date:** When do you want this operational?
4. **Review Cost:** Are the estimated API costs acceptable?

---

## Quick Start Commands

### Create BigQuery Tables:
```bash
python create_stock_bigquery_schema.py
```

### Deploy Stock Functions:
```bash
cd cloud_function_daily_stocks && python deploy.py
cd cloud_function_hourly_stocks && python deploy.py
cd cloud_function_5min_stocks && python deploy.py
```

### Test Data Collection:
```bash
python test_stock_data_collection.py
```

### Monitor API Usage:
```bash
python check_twelve_data_usage.py
```

---

## Support Resources

- **Twelve Data Docs:** https://twelvedata.com/docs
- **API Status:** https://status.twelvedata.com
- **Support:** support@twelvedata.com
- **Request Builder:** https://twelvedata.com/request-builder

---

**Ready to proceed?** Let me know which phase you'd like to start with!
