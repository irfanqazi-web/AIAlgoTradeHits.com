# MASTER TRADING DATA IMPLEMENTATION PLAN
## Twelve Data Pro Plan - Complete Multi-Asset Platform

**Generated:** November 20, 2025
**API Key:** `16ee060fd4d34a628a14bcb6f0167565`
**Plan:** Pro ($229/month) - 1,597 API calls/min + 1,500 WebSocket credits

---

## 📊 COMPLETE DATA INVENTORY - VERIFIED

### ✅ Asset Classes Available:

| Asset Class | Total Assets | USD Pairs | Focus for USA |
|-------------|-------------|-----------|---------------|
| **Stocks** | 20,076 | N/A | S&P 500 (500 stocks) |
| **ETFs** | 10,186 | N/A | Top 200 US ETFs |
| **Forex** | 1,436 pairs | 178 pairs | Major 20 USD pairs |
| **Crypto** | 2,149 coins | 1,136 pairs | Top 100 USD pairs |
| **Commodities** | 62 | N/A | All US-traded (40) |
| **Indices** | Available | N/A | Major US (S&P, Dow, Nasdaq) |
| **Bonds** | Available | N/A | US Treasury Bonds |
| **Mutual Funds** | Available | N/A | Top 100 US funds |

### ✅ US Stock Exchanges (16):
- **NYSE** (XNYS) - 3,032 stocks
- **NASDAQ** (XNAS, XNGS, XNCM, XNMS) - 4,435 stocks
- **OTC** (OTCB, OTCM, PINX, PSGM, EXPM, OTCQ) - 12,598 stocks
- **CBOE** (BATS)
- **NYSE Arca** (ARCX)
- **IEX** (IEXG)
- **ICE** (NYBOT)

### ✅ Global Exchanges: 96 across 58 countries

### ✅ Cryptocurrency Exchanges: 201 exchanges
Including: Binance, Coinbase, Kraken, Bitfinex, Bittrex, Gemini, Bitstamp, Huobi, KuCoin, FTX, OKX, etc.

---

## 🔧 TECHNICAL INDICATORS - 71+ VERIFIED

### Momentum Indicators (10):
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- STOCH (Stochastic Oscillator)
- WILLIAMS (Williams %R)
- CCI (Commodity Channel Index)
- ROC (Rate of Change)
- MOM (Momentum)
- STOCHRSI (Stochastic RSI)
- APO (Absolute Price Oscillator)
- PPO (Percentage Price Oscillator)

### Overlap Studies (11):
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)
- WMA (Weighted Moving Average)
- DEMA (Double Exponential MA)
- TEMA (Triple Exponential MA)
- TRIMA (Triangular MA)
- KAMA (Kaufman Adaptive MA)
- MAMA (MESA Adaptive MA)
- VWAP (Volume Weighted Average Price)
- T3 (T3 Moving Average)
- HT_TRENDLINE (Hilbert Transform)

### Volatility Indicators (6):
- BBANDS (Bollinger Bands)
- ATR (Average True Range)
- NATR (Normalized ATR)
- TRANGE (True Range)
- STDDEV (Standard Deviation)
- VARIANCE (Variance)

### Volume Indicators (4):
- OBV (On Balance Volume)
- AD (Chaikin A/D Line)
- ADOSC (Chaikin A/D Oscillator)
- PVO (Percentage Volume Oscillator)

### Trend Indicators (10):
- ADX (Average Directional Index)
- ADXR (ADX Rating)
- AROON (Aroon)
- AROONOSC (Aroon Oscillator)
- DX (Directional Movement Index)
- PLUS_DI (Plus Directional Indicator)
- MINUS_DI (Minus Directional Indicator)
- PLUS_DM (Plus Directional Movement)
- MINUS_DM (Minus Directional Movement)
- TRIX (Triple Exponential Average)

### Candlestick Pattern Recognition (10):
- CDL2CROWS (Two Crows)
- CDL3BLACKCROWS (Three Black Crows)
- CDL3INSIDE (Three Inside Up/Down)
- CDL3LINESTRIKE (Three-Line Strike)
- CDLABANDONEDBABY (Abandoned Baby)
- CDLDOJI (Doji)
- CDLENGULFING (Engulfing Pattern)
- CDLHAMMER (Hammer)
- CDLHARAMI (Harami Pattern)
- CDLMORNINGSTAR (Morning Star)

### Statistical Functions (7):
- CORREL (Pearson's Correlation)
- LINEARREG (Linear Regression)
- LINEARREG_ANGLE (LR Angle)
- LINEARREG_INTERCEPT (LR Intercept)
- LINEARREG_SLOPE (LR Slope)
- TSF (Time Series Forecast)
- VAR (Variance)

### Other Advanced Indicators (13):
- SAR (Parabolic SAR)
- SAREXT (Parabolic SAR Extended)
- ULTOSC (Ultimate Oscillator)
- BOP (Balance of Power)
- CMO (Chande Momentum Oscillator)
- DPO (Detrended Price Oscillator)
- HT_DCPERIOD (Hilbert Transform - Dominant Cycle Period)
- HT_DCPHASE (Hilbert Transform - Dominant Cycle Phase)
- HT_PHASOR (Hilbert Transform - Phasor Components)
- HT_SINE (Hilbert Transform - SineWave)
- HT_TRENDMODE (Hilbert Transform - Trend vs Cycle)
- MIDPOINT (MidPoint over period)
- MIDPRICE (Midpoint Price)

**Total: 71+ Technical Indicators**

---

## 📈 FUNDAMENTAL DATA ENDPOINTS - VERIFIED ✅

### Company Information:
- ✅ **Profile** - Company description, CEO, address, website, employees
- ✅ **Logo** - Company logo URLs
- ✅ **Statistics** - Market cap, PE ratio, PEG, Price-to-Sales, ROE, ROA

### Financial Statements:
- ✅ **Income Statement** - Revenue, gross profit, operating income, EPS, EBITDA
- ✅ **Balance Sheet** - Assets, liabilities, equity, cash, debt
- ✅ **Cash Flow** - Operating, investing, financing activities

### Corporate Actions:
- ✅ **Earnings Calendar** - Earnings dates, EPS estimates vs actuals
- ✅ **Dividends** - Dividend history with ex-dates and amounts
- ✅ **Stock Splits** - Split history with ratios
- ✅ **Insider Transactions** - Insider buying/selling activity

### NOT Available (404 Errors):
- ❌ **News API** - Not available in Pro plan
- ❌ **Sentiment Analysis** - Not available in Pro plan
- ❌ **Options Chain** - Not available

---

## 🏗️ BIGQUERY ARCHITECTURE - UNIFIED MULTI-ASSET SCHEMA

### Dataset: `cryptobot-462709.trading_data_unified`

---

### TABLE 1: `stocks_daily` (60 fields)

**Core OHLCV + Metadata (15 fields):**
```sql
- symbol STRING
- name STRING
- exchange STRING
- mic_code STRING
- currency STRING
- datetime TIMESTAMP
- date DATE
- open FLOAT64
- high FLOAT64
- low FLOAT64
- close FLOAT64
- volume INT64
- adjusted_close FLOAT64
- asset_type STRING (always 'STOCK')
- data_source STRING (always 'twelve_data')
```

**Technical Indicators (71 fields calculated in Python):**
```sql
# Momentum (10)
- rsi FLOAT64
- macd FLOAT64
- macd_signal FLOAT64
- macd_hist FLOAT64
- stoch_k FLOAT64
- stoch_d FLOAT64
- williams_r FLOAT64
- cci FLOAT64
- roc FLOAT64
- momentum FLOAT64

# Moving Averages (11)
- sma_20 FLOAT64
- sma_50 FLOAT64
- sma_200 FLOAT64
- ema_12 FLOAT64
- ema_26 FLOAT64
- ema_50 FLOAT64
- wma_20 FLOAT64
- dema_20 FLOAT64
- tema_20 FLOAT64
- kama_20 FLOAT64
- vwap FLOAT64

# Volatility (6)
- bb_upper FLOAT64
- bb_middle FLOAT64
- bb_lower FLOAT64
- atr FLOAT64
- natr FLOAT64
- stddev FLOAT64

# Volume (4)
- obv FLOAT64
- ad FLOAT64
- adosc FLOAT64
- pvo FLOAT64

# Trend (10)
- adx FLOAT64
- adxr FLOAT64
- plus_di FLOAT64
- minus_di FLOAT64
- aroon_up FLOAT64
- aroon_down FLOAT64
- aroonosc FLOAT64
- trix FLOAT64
- dx FLOAT64
- sar FLOAT64

# Pattern Recognition (10)
- cdl_doji FLOAT64
- cdl_hammer FLOAT64
- cdl_engulfing FLOAT64
- cdl_harami FLOAT64
- cdl_morningstar FLOAT64
- cdl_3blackcrows FLOAT64
- cdl_2crows FLOAT64
- cdl_3inside FLOAT64
- cdl_3linestrike FLOAT64
- cdl_abandonedbaby FLOAT64

# Statistical (7)
- correl FLOAT64
- linearreg FLOAT64
- linearreg_slope FLOAT64
- linearreg_angle FLOAT64
- tsf FLOAT64
- variance FLOAT64
- beta FLOAT64

# Other (13)
- ultosc FLOAT64
- bop FLOAT64
- cmo FLOAT64
- dpo FLOAT64
- ht_dcperiod FLOAT64
- ht_dcphase FLOAT64
- ht_trendmode FLOAT64
- midpoint FLOAT64
- midprice FLOAT64
- ppo FLOAT64
- stochrsi FLOAT64
- apo FLOAT64
- ht_sine_lead FLOAT64

# Metadata
- fetch_timestamp TIMESTAMP
```

---

### TABLE 2: `stocks_hourly` (Same schema as daily, 60 fields)

---

### TABLE 3: `stocks_5min_top100` (Same schema, 60 fields)

---

### TABLE 4: `etfs_daily` (Same schema, 60 fields)

---

### TABLE 5: `forex_daily` (58 fields - no volume indicators)

**Differences from stocks:**
- Remove: obv, ad, adosc, pvo (volume-based indicators)
- Add: bid, ask, spread fields

---

### TABLE 6: `forex_hourly` (58 fields)

---

### TABLE 7: `forex_5min_major20` (58 fields)

---

### TABLE 8: `crypto_daily` (60 fields - KEEP EXISTING)

✅ Already deployed and working with Kraken data

---

### TABLE 9: `crypto_hourly` (60 fields - KEEP EXISTING)

✅ Already deployed

---

### TABLE 10: `crypto_5min_top10` (60 fields - KEEP EXISTING)

✅ Already deployed

---

### TABLE 11: `commodities_daily` (60 fields)

Commodities to track (40 US-traded):
- Energy: Crude Oil (CL1), Brent (CO1), Natural Gas (NG/USD), Ethanol (DL1)
- Metals: Gold Gram (GAU/USD), Copper (HG1), Lithium (LC)
- Agriculture: Corn (C_1), Wheat, Soybeans, Coffee (KC1), Cotton (CT1), Cocoa (CC1), Orange Juice (JO1)
- Livestock: Live Cattle (LC1), Feeder Cattle (FC1), Lean Hogs (LH1)
- Dairy: Milk (DA), Cheese (CHE)
- Building: Lumber (LB1), Steel (JBP)

---

### TABLE 12: `commodities_hourly` (60 fields)

---

### TABLE 13: `indices_daily` (60 fields)

US Indices to track:
- S&P 500 (SPX)
- Dow Jones (DJI)
- Nasdaq Composite (IXIC)
- Russell 2000 (RUT)
- VIX (Volatility Index)

---

### TABLE 14: `bonds_daily` (58 fields)

US Treasury Bonds:
- 3-Month T-Bill
- 2-Year Treasury
- 5-Year Treasury
- 10-Year Treasury
- 30-Year Treasury

---

### TABLE 15: `stock_fundamentals` (40 fields)

```sql
- symbol STRING
- name STRING
- sector STRING
- industry STRING
- market_cap FLOAT64
- enterprise_value FLOAT64
- trailing_pe FLOAT64
- forward_pe FLOAT64
- peg_ratio FLOAT64
- price_to_sales FLOAT64
- price_to_book FLOAT64
- enterprise_to_revenue FLOAT64
- enterprise_to_ebitda FLOAT64
- profit_margin FLOAT64
- operating_margin FLOAT64
- return_on_assets FLOAT64
- return_on_equity FLOAT64
- revenue_ttm FLOAT64
- revenue_per_share FLOAT64
- quarterly_revenue_growth FLOAT64
- gross_profit_ttm FLOAT64
- ebitda FLOAT64
- net_income_ttm FLOAT64
- diluted_eps FLOAT64
- quarterly_earnings_growth FLOAT64
- total_cash FLOAT64
- total_cash_per_share FLOAT64
- total_debt FLOAT64
- debt_to_equity FLOAT64
- current_ratio FLOAT64
- book_value_per_share FLOAT64
- operating_cash_flow FLOAT64
- free_cash_flow FLOAT64
- fifty_two_week_low FLOAT64
- fifty_two_week_high FLOAT64
- ceo STRING
- employees INT64
- website STRING
- description STRING
- last_updated TIMESTAMP
```

---

### TABLE 16: `earnings_calendar` (15 fields)

```sql
- symbol STRING
- name STRING
- earnings_date DATE
- earnings_time STRING (Before Open / After Hours)
- eps_estimate FLOAT64
- eps_actual FLOAT64
- eps_difference FLOAT64
- eps_surprise_percent FLOAT64
- revenue_estimate FLOAT64
- revenue_actual FLOAT64
- exchange STRING
- country STRING
- fiscal_quarter STRING
- fiscal_year INT64
- fetch_timestamp TIMESTAMP
```

---

### TABLE 17: `dividends_history` (10 fields)

```sql
- symbol STRING
- ex_date DATE
- payment_date DATE
- record_date DATE
- amount FLOAT64
- currency STRING
- dividend_type STRING
- frequency STRING
- exchange STRING
- fetch_timestamp TIMESTAMP
```

---

### TABLE 18: `stock_splits_history` (10 fields)

```sql
- symbol STRING
- split_date DATE
- split_ratio FLOAT64
- from_factor INT64
- to_factor INT64
- description STRING
- exchange STRING
- currency STRING
- pre_split_price FLOAT64
- fetch_timestamp TIMESTAMP
```

---

### TABLE 19: `insider_transactions` (15 fields)

```sql
- symbol STRING
- full_name STRING
- position STRING
- transaction_date DATE
- date_reported DATE
- transaction_type STRING (Buy/Sale/Gift)
- is_direct BOOLEAN
- shares INT64
- value FLOAT64
- price_per_share FLOAT64
- shares_owned_after INT64
- exchange STRING
- currency STRING
- description STRING
- fetch_timestamp TIMESTAMP
```

---

### TABLE 20: `market_movers_daily` (15 fields)

```sql
- symbol STRING
- name STRING
- asset_type STRING (STOCK/CRYPTO/FOREX/COMMODITY)
- exchange STRING
- datetime TIMESTAMP
- date DATE
- last_price FLOAT64
- high FLOAT64
- low FLOAT64
- volume INT64
- change FLOAT64
- percent_change FLOAT64
- category STRING (gainer/loser)
- rank INT64
- fetch_timestamp TIMESTAMP
```

---

## 🚀 CLOUD FUNCTIONS ARCHITECTURE

### Function Naming Convention:
`{frequency}-{asset_type}-fetcher`

Example: `daily-stocks-fetcher`, `hourly-forex-fetcher`, `5min-crypto-top10-fetcher`

---

### DAILY FUNCTIONS (7 functions)

#### 1. `daily-stocks-fetcher`
- **Schedule:** `0 1 * * 1-5` (1 AM ET, weekdays only)
- **Assets:** S&P 500 stocks (500 symbols)
- **Interval:** 1day
- **Indicators:** All 71 indicators
- **Table:** `stocks_daily`
- **Memory:** 1GB
- **Timeout:** 540s
- **API Cost:** 500 credits
- **Execution Time:** ~8 minutes

#### 2. `daily-etfs-fetcher`
- **Schedule:** `0 2 * * 1-5` (2 AM ET, weekdays only)
- **Assets:** Top 200 US ETFs
- **Interval:** 1day
- **Table:** `etfs_daily`
- **API Cost:** 200 credits

#### 3. `daily-forex-fetcher`
- **Schedule:** `0 3 * * *` (3 AM ET, daily)
- **Assets:** 20 major USD pairs (EUR/USD, GBP/USD, JPY/USD, etc.)
- **Interval:** 1day
- **Table:** `forex_daily`
- **API Cost:** 20 credits

#### 4. `daily-crypto-fetcher` ✅ EXISTING
- **Schedule:** `0 0 * * *` (Midnight ET)
- **Assets:** ~675 USD crypto pairs (from Kraken)
- **Status:** Already deployed and working

#### 5. `daily-commodities-fetcher`
- **Schedule:** `0 4 * * 1-5` (4 AM ET, weekdays)
- **Assets:** 40 US-traded commodities
- **Table:** `commodities_daily`
- **API Cost:** 40 credits

#### 6. `daily-indices-fetcher`
- **Schedule:** `0 5 * * 1-5` (5 AM ET, weekdays)
- **Assets:** 5 major US indices
- **Table:** `indices_daily`
- **API Cost:** 5 credits

#### 7. `daily-bonds-fetcher`
- **Schedule:** `0 6 * * 1-5` (6 AM ET, weekdays)
- **Assets:** 5 US Treasury bonds
- **Table:** `bonds_daily`
- **API Cost:** 5 credits

**Total Daily Credits:** 1,445 credits

---

### HOURLY FUNCTIONS (6 functions)

#### 8. `hourly-stocks-fetcher`
- **Schedule:** `0 * * * *` (Every hour, market hours: 9 AM - 4 PM ET)
- **Assets:** S&P 500 stocks
- **Interval:** 1h
- **Table:** `stocks_hourly`
- **Memory:** 1GB
- **Timeout:** 540s
- **API Cost:** 500 credits/hour × 7 hours = 3,500/day

#### 9. `hourly-etfs-fetcher`
- **Schedule:** `5 * * * *` (5 min past the hour, market hours)
- **Assets:** Top 200 ETFs
- **Table:** `etfs_hourly`
- **API Cost:** 200 × 7 = 1,400/day

#### 10. `hourly-forex-fetcher`
- **Schedule:** `10 * * * *` (10 min past the hour, 24/7)
- **Assets:** 20 major USD pairs
- **Table:** `forex_hourly`
- **API Cost:** 20 × 24 = 480/day

#### 11. `hourly-crypto-fetcher` ✅ EXISTING
- **Schedule:** `0 * * * *`
- **Assets:** 675 USD crypto pairs
- **Status:** Already deployed

#### 12. `hourly-commodities-fetcher`
- **Schedule:** `15 * * * *` (15 min past, market hours)
- **Assets:** 40 commodities
- **Table:** `commodities_hourly`
- **API Cost:** 40 × 7 = 280/day

#### 13. `hourly-indices-fetcher`
- **Schedule:** `20 * * * *` (20 min past, market hours)
- **Assets:** 5 indices
- **Table:** `indices_hourly`
- **API Cost:** 5 × 7 = 35/day

**Total Hourly Credits:** 5,695/day

---

### 5-MINUTE FUNCTIONS (4 functions)

#### 14. `5min-stocks-top100-fetcher`
- **Schedule:** `*/5 9-16 * * 1-5` (Every 5 min, 9 AM - 4 PM ET)
- **Assets:** Top 100 gainers from hourly data
- **Interval:** 5min
- **Table:** `stocks_5min_top100`
- **Memory:** 512MB
- **Timeout:** 300s
- **API Cost:** 100 × 12 calls/hour × 7 hours = 8,400/day

#### 15. `5min-etfs-top50-fetcher`
- **Schedule:** `1-56/5 9-16 * * 1-5` (Offset by 1 min)
- **Assets:** Top 50 ETFs by volume
- **Table:** `etfs_5min_top50`
- **API Cost:** 50 × 12 × 7 = 4,200/day

#### 16. `5min-forex-major10-fetcher`
- **Schedule:** `*/5 * * * *` (24/7)
- **Assets:** 10 most volatile forex pairs
- **Table:** `forex_5min_major10`
- **API Cost:** 10 × 12 × 24 = 2,880/day

#### 17. `5min-crypto-top10-fetcher` ✅ EXISTING
- **Schedule:** `*/5 * * * *`
- **Assets:** Top 10 crypto gainers
- **Status:** Already deployed

**Total 5-Min Credits:** 15,480/day

---

### FUNDAMENTAL DATA FUNCTIONS (5 functions)

#### 18. `fundamentals-stocks-fetcher`
- **Schedule:** `0 7 * * 0` (Sunday 7 AM, weekly)
- **Assets:** S&P 500 stocks
- **Endpoints:** Profile, Statistics, Income Statement, Balance Sheet, Cash Flow
- **Table:** `stock_fundamentals`
- **API Cost:** 500 × 5 endpoints = 2,500 credits/week

#### 19. `earnings-calendar-fetcher`
- **Schedule:** `0 8 * * 1-5` (8 AM ET, daily)
- **Assets:** Fetch earnings for next 30 days
- **Table:** `earnings_calendar`
- **API Cost:** 100 credits/day

#### 20. `dividends-fetcher`
- **Schedule:** `0 9 * * 1` (Monday 9 AM, weekly)
- **Assets:** S&P 500 stocks
- **Table:** `dividends_history`
- **API Cost:** 500 credits/week

#### 21. `splits-fetcher`
- **Schedule:** `0 10 * * 1` (Monday 10 AM, weekly)
- **Assets:** S&P 500 stocks
- **Table:** `stock_splits_history`
- **API Cost:** 500 credits/week

#### 22. `insider-transactions-fetcher`
- **Schedule:** `0 11 * * 1` (Monday 11 AM, weekly)
- **Assets:** S&P 500 stocks
- **Table:** `insider_transactions`
- **API Cost:** 500 credits/week

**Total Fundamental Credits:** 2,100/week = ~300/day

---

### MARKET MOVERS FUNCTION (1 function)

#### 23. `market-movers-fetcher`
- **Schedule:** `0 9,12,15 * * 1-5` (9 AM, 12 PM, 3 PM ET)
- **Assets:** Top 25 gainers + Top 25 losers
- **Endpoints:** `/market_movers/stocks`, `/market_movers/crypto`, `/market_movers/forex`
- **Table:** `market_movers_daily`
- **API Cost:** 3 endpoints × 3 times/day = 9 credits/day

---

## 📈 TOTAL API USAGE ESTIMATION

### Daily Credits Breakdown:

| Category | Daily Credits | Monthly Credits | % of Limit |
|----------|--------------|-----------------|------------|
| Daily Functions | 1,445 | 43,350 | 0.9% |
| Hourly Functions | 5,695 | 170,850 | 3.6% |
| 5-Min Functions | 15,480 | 464,400 | 9.7% |
| Fundamentals | 300 | 9,000 | 0.2% |
| Market Movers | 9 | 270 | 0.01% |
| **Total** | **22,929** | **687,870** | **14.4%** |

**Monthly API Limit:** 1,597 calls/min × 60 min × 24 hours × 30 days = 4,780,800 credits
**Buffer Remaining:** 85.6% (4,092,930 credits)

---

## ⏱️ EXECUTION TIME ESTIMATES

### Daily Functions: ~30 minutes total
- Staggered: 1 AM - 6 AM ET (no conflicts)

### Hourly Functions: ~20 minutes per hour
- Staggered by 5-minute offsets (no conflicts)

### 5-Min Functions: ~3 minutes per cycle
- Staggered by 1-minute offsets (no conflicts)

### Peak Load:
- Market open (9:30 AM ET): All functions running
- Worst case: 1,200 credits/min (75% of limit)
- Safe operation with buffer

---

## 🎨 FRONTEND INTEGRATION

### Multi-Asset Selector Component

```jsx
<AssetClassSelector
  options={[
    { label: "Stocks", value: "stocks", icon: <StockIcon /> },
    { label: "ETFs", value: "etfs", icon: <ETFIcon /> },
    { label: "Crypto", value: "crypto", icon: <CryptoIcon /> },
    { label: "Forex", value: "forex", icon: <ForexIcon /> },
    { label: "Commodities", value: "commodities", icon: <CommodityIcon /> },
    { label: "Bonds", value: "bonds", icon: <BondIcon /> },
    { label: "Indices", value: "indices", icon: <IndexIcon /> },
  ]}
  onChange={handleAssetChange}
/>
```

### Unified Chart Component

```jsx
<UnifiedTradingChart
  assetType={selectedAssetType}
  symbol={selectedSymbol}
  interval={selectedInterval}
  indicators={selectedIndicators}
  dataSource="twelve_data"
/>
```

### Market Overview Dashboard

```jsx
<MarketOverviewDashboard
  stocks={{ gainers: topStockGainers, losers: topStockLosers }}
  crypto={{ gainers: topCryptoGainers, losers: topCryptoLosers }}
  forex={{ strongest: strongestCurrencies, weakest: weakestCurrencies }}
  commodities={{ gainers: topCommodityGainers }}
/>
```

---

## 💰 COST ANALYSIS

### Monthly Costs:

| Service | Cost |
|---------|------|
| Twelve Data API | $229.00 |
| Cloud Functions (23 functions) | $180.00 |
| BigQuery Storage (500GB) | $10.00 |
| BigQuery Queries | $15.00 |
| Cloud Scheduler (23 jobs) | $0.30 |
| Cloud Run (Trading App) | $5.00 |
| **Total Monthly** | **$439.30** |

**Annual Cost:** $5,271.60

---

## 🚦 IMPLEMENTATION PHASES

### Phase 1: Stock Data Pipeline (Week 1-2)
- [x] API key configured
- [ ] Create stocks BigQuery schema
- [ ] Build daily-stocks-fetcher
- [ ] Build hourly-stocks-fetcher
- [ ] Build 5min-stocks-top100-fetcher
- [ ] Deploy and test

### Phase 2: ETF Pipeline (Week 2-3)
- [ ] Create ETF schema
- [ ] Build ETF fetchers (daily, hourly, 5min)
- [ ] Deploy and test

### Phase 3: Forex Pipeline (Week 3)
- [ ] Create forex schema
- [ ] Build forex fetchers (daily, hourly, 5min)
- [ ] Deploy and test

### Phase 4: Commodities & Bonds (Week 4)
- [ ] Create commodity/bond schemas
- [ ] Build commodity fetchers
- [ ] Build bond fetchers
- [ ] Deploy and test

### Phase 5: Fundamental Data (Week 5)
- [ ] Create fundamental schemas
- [ ] Build fundamental fetchers
- [ ] Deploy weekly jobs
- [ ] Test data quality

### Phase 6: Frontend Integration (Week 6-7)
- [ ] Multi-asset selector UI
- [ ] Unified chart component
- [ ] Market overview dashboard
- [ ] Advanced screeners
- [ ] Deploy updated app

### Phase 7: Testing & Optimization (Week 8)
- [ ] Load testing
- [ ] Cost optimization
- [ ] Performance tuning
- [ ] Documentation

---

## 📋 ASSET UNIVERSE DETAILS

### Stocks (S&P 500):
500 largest US companies by market cap

### ETFs (Top 200):
- Sector ETFs (XLF, XLE, XLK, XLV, etc.)
- Index ETFs (SPY, QQQ, IWM, DIA)
- Bond ETFs (AGG, BND, TLT)
- Commodity ETFs (GLD, SLV, USO)
- International ETFs (EFA, EEM, VWO)

### Forex (Major 20 USD Pairs):
EUR/USD, GBP/USD, JPY/USD, AUD/USD, NZD/USD, CAD/USD, CHF/USD, CNY/USD, HKD/USD, SGD/USD, INR/USD, MXN/USD, BRL/USD, ZAR/USD, TRY/USD, KRW/USD, SEK/USD, NOK/USD, DKK/USD, PLN/USD

### Crypto (Top 100 USD Pairs):
BTC, ETH, BNB, XRP, ADA, DOGE, SOL, DOT, MATIC, SHIB, AVAX, UNI, LINK, ATOM, XLM, ALGO, VET, ICP, FIL, AAVE, etc.

### Commodities (40):
Metals, Energy, Agriculture, Livestock, Building Materials

### Bonds (5 US Treasury):
3M, 2Y, 5Y, 10Y, 30Y

### Indices (5 Major US):
SPX, DJI, IXIC, RUT, VIX

---

## 🔐 SECURITY & BEST PRACTICES

1. **API Key Management:**
   - Store in Secret Manager
   - Rotate every 90 days
   - Monitor usage hourly

2. **Rate Limiting:**
   - Max 1,200 calls/min (75% of limit)
   - Exponential backoff on errors
   - Circuit breaker pattern

3. **Data Validation:**
   - Check for null values
   - Validate indicator ranges
   - Duplicate detection

4. **Error Handling:**
   - Retry failed symbols (3 attempts)
   - Log all errors to BigQuery
   - Alert on >10% failure rate

5. **Monitoring:**
   - Cloud Monitoring dashboards
   - Uptime checks
   - Cost alerts

---

## 📊 SAMPLE QUERIES

### Find Oversold Stocks with Strong Trends:
```sql
SELECT symbol, close, rsi, adx, sma_200
FROM `cryptobot-462709.trading_data_unified.stocks_daily`
WHERE date = CURRENT_DATE() - 1
  AND rsi < 30
  AND adx > 25
  AND close > sma_200
ORDER BY rsi ASC
LIMIT 20;
```

### Top Forex Movers (Last Hour):
```sql
SELECT symbol, close, percent_change
FROM `cryptobot-462709.trading_data_unified.forex_hourly`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
ORDER BY ABS(percent_change) DESC
LIMIT 20;
```

### Commodities Correlation Matrix:
```sql
SELECT
  c1.symbol as commodity1,
  c2.symbol as commodity2,
  CORR(c1.close, c2.close) as correlation
FROM `cryptobot-462709.trading_data_unified.commodities_daily` c1
JOIN `cryptobot-462709.trading_data_unified.commodities_daily` c2
  ON c1.date = c2.date
WHERE c1.date >= CURRENT_DATE() - 90
  AND c1.symbol < c2.symbol
GROUP BY c1.symbol, c2.symbol
HAVING correlation > 0.8
ORDER BY correlation DESC;
```

---

## 🎯 SUCCESS METRICS

### Data Quality:
- 99%+ successful API calls
- <1% duplicate records
- <5% null indicator values

### Performance:
- Daily functions complete in <30 min
- Hourly functions complete in <10 min
- 5-min functions complete in <3 min

### Cost Efficiency:
- Stay under $500/month
- <15% API limit utilization
- <$100/TB BigQuery queries

### User Engagement:
- <2 second chart load times
- Real-time data (<5 min delay)
- 99.9% frontend uptime

---

## 🔄 MAINTENANCE SCHEDULE

### Daily:
- Monitor API usage
- Check for failed functions
- Review error logs

### Weekly:
- Analyze cost trends
- Review data quality metrics
- Update symbol lists

### Monthly:
- Performance optimization
- Cost analysis
- Schema updates if needed

### Quarterly:
- API key rotation
- Major feature updates
- User feedback review

---

## 📞 SUPPORT & RESOURCES

- **Twelve Data Docs:** https://twelvedata.com/docs
- **API Status:** https://status.twelvedata.com
- **GCP Console:** https://console.cloud.google.com/functions?project=cryptobot-462709
- **BigQuery Console:** https://console.cloud.google.com/bigquery?project=cryptobot-462709

---

## ✅ NEXT STEPS

1. **Review this plan** - Confirm asset classes and scope
2. **Prioritize phases** - Which assets to implement first?
3. **Set timeline** - Target completion date?
4. **Approve budget** - Is $439/month acceptable?

**Ready to build?** 🚀
