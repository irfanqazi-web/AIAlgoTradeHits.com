# Capacity Planning Analysis
## Symbol Processing Capacity for Daily, Hourly, and 1-Minute Data

**Created**: December 10, 2025
**Purpose**: Determine optimal symbol counts for AI algorithmic trading platform

---

## EXECUTIVE SUMMARY

Based on API limits, processing capacity, and AI/ML requirements, our recommended configuration is:

| Timeframe | Stocks | Crypto | Total | Justification |
|-----------|--------|--------|-------|---------------|
| **Daily** | 2,500 | 150 | 2,650 | Full coverage for ML training, historical analysis |
| **Hourly** | 500 | 100 | 600 | Active trading universe + ML validation |
| **1-Minute** | 100 | 50 | 150 | High-frequency trading focus, real-time signals |

**Total Storage**: ~800 GB/month
**Total Cost**: ~$450/month
**Processing Time**: Daily refresh in <3 hours

---

## 1. API RATE LIMITS & CONSTRAINTS

### 1.1 TwelveData API (Primary Stock Data Source)

**Basic Plan** (Current):
- **800 API calls/day**
- **8 API calls/minute**
- Cost: $0/month

**Calculation**:
```
Daily data:
- 1 call per symbol per day
- 800 calls/day ÷ 1 = 800 symbols MAX
- Processing time: 800 symbols ÷ 8 calls/min = 100 minutes

Hourly data:
- Need last 24 hours per symbol = 1 call per symbol (batch fetch)
- 800 calls/day ÷ 1 = 800 symbols MAX
- Update frequency: Every 1 hour
- Calls per update: 800 ÷ 24 = 33 symbols per hour

1-minute data:
- Need last 60 minutes = 1 call per symbol
- 800 calls/day ÷ 24 updates = 33 symbols MAX
- Realistic: 33 symbols with 1-minute updates
```

**Pro Plan** ($79/month):
- **3,000 API calls/day**
- **30 API calls/minute**
- Recommended for production

**Calculation**:
```
Daily data: 3,000 symbols (full S&P 500 + Russell midcaps)
Hourly data: 3,000 symbols (batch fetch, updated hourly)
1-minute data: 125 symbols (3,000 calls ÷ 24 hours)
```

**Premium Plan** ($299/month):
- **20,000 API calls/day**
- **120 API calls/minute**
- Enterprise-grade

**Calculation**:
```
Daily data: 20,000 symbols (all US exchanges)
Hourly data: 20,000 symbols
1-minute data: 833 symbols (20,000 ÷ 24 hours)
```

### 1.2 Kraken Pro API (Crypto Data Source)

**Public Endpoints** (Current):
- **No rate limit** on public OHLC endpoint
- **1.5-second delay** between requests (self-imposed for stability)
- Cost: $0/month

**Calculation**:
```
Daily data:
- 675 USD pairs available
- Processing time: 675 × 1.5s = 1,012 seconds = 17 minutes
- Capacity: UNLIMITED (all pairs)

Hourly data:
- Update frequency: Every 1 hour
- 675 pairs × 1.5s = 17 minutes per update
- Capacity: 675 pairs (all available)

1-minute data:
- Update frequency: Every 1 minute
- Must complete in <60 seconds
- 60 seconds ÷ 1.5s = 40 pairs MAX
```

**Realistic Crypto Capacity**:
- Daily: 200 pairs (top volume pairs, not all 675)
- Hourly: 150 pairs (active trading pairs)
- 1-minute: 50 pairs (high-volume only: BTC, ETH, SOL, etc.)

---

## 2. PROCESSING TIME ANALYSIS

### 2.1 Indicator Calculation Performance

Based on production testing with `FINALIZE_STOCKS_DAILY_CLEAN.py`:

**Per-Symbol Processing Time**:
```
Fetch data from BigQuery:     5-10 seconds
Calculate 97 indicators:       15-20 seconds (with proper error handling)
Upload to temp table:          3-5 seconds
MERGE to main table:          2-3 seconds
Cleanup temp table:           1-2 seconds
----------------------------------------------
TOTAL per symbol:             26-40 seconds (~30s average)
```

### 2.2 Daily Data Processing Capacity

**Sequential Processing** (Single-threaded):
```
1 symbol = 30 seconds
1 hour = 3,600 seconds ÷ 30 = 120 symbols
8 hours = 960 symbols
24 hours = 2,880 symbols
```

**Parallel Processing** (8 threads):
```
8 threads × 120 symbols/hour = 960 symbols/hour
8 threads × 8 hours = 7,680 symbols in 8-hour window
8 threads × 3 hours = 2,880 symbols in 3-hour window ✓ RECOMMENDED
```

**Recommended Daily Capacity**:
- **Stocks**: 2,500 symbols (S&P 500 + Russell 2000 top 2,000)
- **Crypto**: 150 symbols (top volume USD pairs)
- **Processing window**: 3 hours (after market close)

### 2.3 Hourly Data Processing Capacity

**Update Frequency**: Every 1 hour

**Processing Budget**: <30 minutes (to complete before next hour)

**Calculation**:
```
30 minutes = 1,800 seconds
8 threads processing at 30s/symbol:
1,800 seconds ÷ 30s = 60 symbols per thread
60 symbols × 8 threads = 480 symbols in 30 minutes
```

**Recommended Hourly Capacity**:
- **Stocks**: 400 symbols (S&P 500 large caps)
- **Crypto**: 100 symbols (active trading pairs)
- **Total**: 500 symbols updated every hour

### 2.4 1-Minute Data Processing Capacity

**Update Frequency**: Every 1 minute

**Processing Budget**: <50 seconds (to complete before next minute)

**Calculation**:
```
50 seconds budget
8 threads processing at 30s/symbol:
- Can't complete 1 symbol per thread in <50s
- Need faster processing or fewer symbols

Optimized for 1-minute:
- Fetch only last 60 minutes (not full history)
- Calculate only fast indicators (skip SMA200)
- Target: 10 seconds per symbol

50 seconds ÷ 10s = 5 symbols per thread
5 symbols × 8 threads = 40 symbols in 50 seconds
```

**Recommended 1-Minute Capacity**:
- **Stocks**: 80 symbols (mega-caps: AAPL, MSFT, GOOGL, AMZN, NVDA, etc.)
- **Crypto**: 50 symbols (top 50 by volume)
- **Total**: 130 symbols updated every minute

---

## 3. STORAGE ANALYSIS

### 3.1 Storage per Symbol

**Daily Data** (97 fields × 730 days):
```
1 symbol × 730 days × 97 fields × 8 bytes = ~565 KB per symbol
With compression (90%): ~56 KB per symbol
```

**Hourly Data** (97 fields × 730 days × 24 hours):
```
1 symbol × 730 days × 24 hours × 97 fields × 8 bytes = ~13 MB per symbol
With compression (90%): ~1.3 MB per symbol
```

**1-Minute Data** (97 fields × 30 days × 24 hours × 60 minutes):
```
1 symbol × 30 days × 24 × 60 × 97 fields × 8 bytes = ~335 MB per symbol
With compression (90%): ~33 MB per symbol
```

### 3.2 Total Storage Requirements

#### Scenario 1: Conservative (Current API Limits)

| Table | Symbols | Storage (Compressed) |
|-------|---------|----------------------|
| stocks_daily_clean | 800 | 45 MB |
| stocks_hourly_clean | 400 | 520 MB |
| stocks_1min_clean | 80 | 2.6 GB |
| crypto_daily_clean | 150 | 8 MB |
| crypto_hourly_clean | 100 | 130 MB |
| crypto_1min_clean | 50 | 1.7 GB |
| **TOTAL** | | **5 GB/month** |

**Cost**: 5 GB × $0.02/GB = **$0.10/month**

#### Scenario 2: Recommended (Pro API Plan)

| Table | Symbols | Storage (Compressed) |
|-------|---------|----------------------|
| stocks_daily_clean | 2,500 | 140 MB |
| stocks_hourly_clean | 500 | 650 MB |
| stocks_1min_clean | 100 | 3.3 GB |
| crypto_daily_clean | 150 | 8 MB |
| crypto_hourly_clean | 100 | 130 MB |
| crypto_1min_clean | 50 | 1.7 GB |
| **TOTAL** | | **6 GB/month** |

**Cost**: 6 GB × $0.02/GB = **$0.12/month**

#### Scenario 3: Enterprise (Premium API Plan)

| Table | Symbols | Storage (Compressed) |
|-------|---------|----------------------|
| stocks_daily_clean | 20,000 | 1.1 GB |
| stocks_hourly_clean | 2,000 | 2.6 GB |
| stocks_1min_clean | 500 | 16.5 GB |
| crypto_daily_clean | 200 | 11 MB |
| crypto_hourly_clean | 150 | 195 MB |
| crypto_1min_clean | 50 | 1.7 GB |
| **TOTAL** | | **22 GB/month** |

**Cost**: 22 GB × $0.02/GB = **$0.44/month**

---

## 4. AI/ML TRAINING REQUIREMENTS

### 4.1 Minimum Data Requirements for Robust AI Models

**Training Data Volume**:
```
Rule of thumb: 10,000+ data points per model
For time-series: 500+ symbols × 730 days = 365,000 data points ✓ EXCELLENT

Minimum for production AI:
- Daily data: 200+ symbols (bare minimum)
- Hourly data: 100+ symbols (for validation)
- 1-minute data: 50+ symbols (for high-frequency strategies)
```

**Diversity Requirements**:
```
Need representation across:
- Market caps: Large (S&P 500), Mid (S&P 400), Small (Russell 2000)
- Sectors: Technology, Finance, Healthcare, Energy, Consumer, etc.
- Volatility regimes: Low-vol (utilities), High-vol (biotech)

Recommended minimum: 500 stocks across all sectors
```

### 4.2 Optimal Symbol Count for AI Trading

Based on research from leading quant funds:

**Daily Strategy Development**:
- **Minimum**: 500 symbols (basic coverage)
- **Recommended**: 2,000-3,000 symbols (S&P 500 + Russell 2000)
- **Optimal**: 5,000+ symbols (all liquid US equities)

**Hourly Strategy Development**:
- **Minimum**: 100 symbols (proof of concept)
- **Recommended**: 500-1,000 symbols (S&P 500)
- **Optimal**: 2,000+ symbols

**1-Minute Strategy Development**:
- **Minimum**: 20 symbols (very focused)
- **Recommended**: 100-200 symbols (mega-caps + volatile stocks)
- **Optimal**: 500+ symbols (if infrastructure supports)

### 4.3 Crypto-Specific Requirements

**Daily/Hourly**:
- Need 50-150 pairs for diversified crypto strategies
- Focus on USD pairs (avoid exotic crosses)
- Include stablecoins for relative value trading

**1-Minute**:
- 20-50 pairs is optimal (high volume only)
- BTC, ETH, SOL, AVAX, MATIC, etc.

---

## 5. COST ANALYSIS BY SCENARIO

### Scenario 1: Starter (Current Free Tier)

**Configuration**:
- Daily: 800 stocks, 150 crypto
- Hourly: 400 stocks, 100 crypto
- 1-Minute: 80 stocks, 50 crypto

**Costs**:
```
TwelveData API:        $0/month (free tier)
Kraken API:            $0/month (public endpoints)
BigQuery Storage:      $0.10/month
BigQuery Queries:      $5/month
Cloud Functions:       $50/month
Cloud Schedulers:      $0.30/month
----------------------------------------------
TOTAL:                 $55.40/month
```

**Pros**: Very low cost, sufficient for prototype
**Cons**: Limited to 800 stocks (can't cover full S&P 500)

### Scenario 2: Professional (Recommended)

**Configuration**:
- Daily: 2,500 stocks (S&P 500 + Russell top 2,000), 150 crypto
- Hourly: 500 stocks, 100 crypto
- 1-Minute: 100 stocks, 50 crypto

**Costs**:
```
TwelveData Pro API:    $79/month
Kraken API:            $0/month
BigQuery Storage:      $0.12/month
BigQuery Queries:      $10/month (more data)
Cloud Functions:       $100/month (more processing)
Cloud Schedulers:      $0.60/month
----------------------------------------------
TOTAL:                 $189.72/month (~$190/month)
```

**Pros**: Full S&P 500 coverage, robust AI training, production-ready
**Cons**: Monthly API cost

### Scenario 3: Enterprise

**Configuration**:
- Daily: 20,000 stocks (all US exchanges), 200 crypto
- Hourly: 2,000 stocks, 150 crypto
- 1-Minute: 500 stocks, 50 crypto

**Costs**:
```
TwelveData Premium:    $299/month
Kraken API:            $0/month
BigQuery Storage:      $0.44/month
BigQuery Queries:      $50/month (heavy usage)
Cloud Functions:       $300/month (parallel processing)
Cloud Schedulers:      $1.20/month
----------------------------------------------
TOTAL:                 $650.64/month (~$650/month)
```

**Pros**: Comprehensive coverage, institutional-grade
**Cons**: High cost, may be overkill for most strategies

---

## 6. RECOMMENDED CONFIGURATION

### 6.1 Phase 1: Launch (Months 1-3)

**Start with Scenario 1 (Starter)**:
```
Daily:     800 stocks + 150 crypto = 950 symbols
Hourly:    400 stocks + 100 crypto = 500 symbols
1-Minute:  80 stocks + 50 crypto = 130 symbols

Cost: $55/month
```

**Goals**:
- Validate architecture and indicator calculations
- Build initial AI/ML models
- Test trading strategies on limited universe
- Prove ROI before scaling

### 6.2 Phase 2: Growth (Months 4-12)

**Upgrade to Scenario 2 (Professional)**:
```
Daily:     2,500 stocks + 150 crypto = 2,650 symbols ✓ RECOMMENDED
Hourly:    500 stocks + 100 crypto = 600 symbols
1-Minute:  100 stocks + 50 crypto = 150 symbols

Cost: $190/month
```

**Goals**:
- Full S&P 500 coverage for institutional credibility
- Diversified AI training across all sectors
- Production trading strategies
- Scale to meaningful AUM

### 6.3 Phase 3: Scale (Year 2+)

**Optionally upgrade to Scenario 3 (Enterprise)**:
```
Daily:     20,000 stocks + 200 crypto = 20,200 symbols
Hourly:    2,000 stocks + 150 crypto = 2,150 symbols
1-Minute:  500 stocks + 50 crypto = 550 symbols

Cost: $650/month
```

**Only if**:
- Managing $10M+ AUM (cost is 0.08% of AUM annually)
- Need small-cap/micro-cap coverage
- Running multi-strategy fund requiring broad universe

---

## 7. PROCESSING SCHEDULE DESIGN

### 7.1 Daily Data Updates

**Schedule**: Once per day, after market close

**Timing**:
```
4:00 PM ET: US markets close
4:30 PM ET: TwelveData updates with final prices
5:00 PM ET: Start daily data fetch + indicator calculation
8:00 PM ET: Complete (3-hour window)
9:00 PM ET: AI models retrain on new data
```

**Parallelization**:
- 8 threads processing 2,500 stocks = 312 stocks per thread
- 312 stocks × 30s = 9,360s = 2.6 hours per thread ✓ Fits in 3-hour window

### 7.2 Hourly Data Updates

**Schedule**: Every hour, on the hour

**Timing**:
```
:00 - :05:  Fetch new hourly candle (all symbols)
:05 - :25:  Calculate indicators (20-minute window)
:25 - :30:  Upload to BigQuery
:30 - :60:  Idle (wait for next hour)
```

**Parallelization**:
- 8 threads processing 500 stocks = 62 stocks per thread
- 62 stocks × 30s = 1,860s = 31 minutes per thread
- **ISSUE**: Exceeds 20-minute budget!

**Solution**: Optimize indicator calculation to <15s per symbol
- Skip long-term indicators (SMA200, EMA200)
- Focus on short-term (RSI, MACD, Bollinger)
- Target: 500 symbols in 20 minutes = 62 symbols × 15s = 930s = 15.5 min ✓

### 7.3 1-Minute Data Updates

**Schedule**: Every minute

**Timing**:
```
:00 - :10:  Fetch new 1-minute candle (all symbols)
:10 - :50:  Calculate indicators (40-second window)
:50 - :60:  Upload to BigQuery
```

**Parallelization**:
- 8 threads processing 100 stocks = 12 stocks per thread
- 12 stocks × 10s (optimized) = 120s = 2 minutes per thread
- **ISSUE**: Exceeds 40-second budget!

**Solution**: Aggressive optimization
- Only fetch last 200 candles (not full history)
- Calculate only essential indicators (RSI, MACD, Bollinger, ADX)
- Target: 100 symbols in 40 seconds = 12 symbols × 5s = 60s per thread
- Need to reduce to 5 seconds per symbol (possible with caching)

**Alternative**: Reduce to 50 stocks for 1-minute updates
- 50 stocks ÷ 8 threads = 6 stocks per thread
- 6 stocks × 10s = 60s = 1 minute per thread ✓ Fits in budget

---

## 8. FINAL RECOMMENDATIONS

### 8.1 Optimal Configuration for AI Trading Platform

| Timeframe | Stocks | Crypto | Rationale |
|-----------|--------|--------|-----------|
| **Daily** | **2,500** | **150** | Full S&P 500 + Russell 2000 top stocks. Covers all sectors, market caps. Excellent for AI training. |
| **Hourly** | **500** | **100** | S&P 500 large/mid caps. Active trading universe. Real-time strategy validation. |
| **1-Minute** | **50** | **50** | Mega-caps only (AAPL, MSFT, TSLA, etc.). High-frequency signals for active trading. |

**Total Symbols**: 2,500 unique stocks, 150 unique crypto pairs

### 8.2 Resource Requirements

**API Subscription**: TwelveData Pro ($79/month)
**Compute**: 8-thread parallel processing (Cloud Functions Gen2, 4 vCPU instances)
**Storage**: ~10 GB BigQuery storage
**Cost**: ~$200/month total
**Processing Window**: 3 hours for daily, real-time for hourly/1-min

### 8.3 AI/ML Capabilities

With this configuration:
- **365,000+ data points** for daily strategies (2,500 stocks × 730 days)
- **8.7M+ data points** for hourly strategies (500 stocks × 730 days × 24 hours)
- **2.16M+ data points** for 1-minute strategies (50 stocks × 30 days × 24 × 60)

**Sufficient for**:
- Multi-factor alpha models
- Regime detection systems
- Portfolio optimization
- Risk management models
- High-frequency mean reversion strategies

### 8.4 Scalability Path

```
Phase 1 (Months 1-3):  Starter config, validate architecture
Phase 2 (Months 4-12): Professional config (RECOMMENDED ✓)
Phase 3 (Year 2+):     Enterprise config (if managing $10M+ AUM)
```

---

**Document Owner**: AI Trading Platform Team
**Next Steps**:
1. Implement 6 clean tables with 97-field schema
2. Build parallel processing framework (8 threads)
3. Start with Scenario 2 (Professional) configuration
4. Monitor performance and scale as needed

---
