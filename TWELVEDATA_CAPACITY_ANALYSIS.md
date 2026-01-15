# TwelveData $229 Plan - Capacity Analysis Report

**Generated:** December 17, 2025
**API Plan:** Pro ($229/month)
**Plan Limit:** 800 credits/minute (1,152,000 credits/day theoretical max)

---

## Current API Usage Status

```
Current Usage:  1 credit (just checked)
Plan Limit:     800 credits/minute
Plan Category:  Pro
```

---

## Available Data vs Currently Extracted

| Asset Type | Available | Currently Extracted | Utilization |
|------------|-----------|---------------------|-------------|
| **US Stocks** (NYSE+NASDAQ) | 7,641 | 152 | **2.0%** |
| **Cryptocurrencies** | 2,136 | 45 | **2.1%** |
| **Forex Pairs** | 1,459 | 30 | **2.1%** |
| **US ETFs** | 10,299 | 40 | **0.4%** |
| **Indices** | 1,355 | 9 | **0.7%** |
| **Commodities** | 60 | 14 | **23.3%** |
| **US Mutual Funds** | 82,695 | 15 | **0.02%** |
| **TOTAL** | **105,645** | **305** | **0.29%** |

---

## Daily Data Extraction Estimate (Per $229 Plan)

### Theoretical Maximum Capacity

| Metric | Value |
|--------|-------|
| Credits per minute | 800 |
| Credits per hour | 48,000 |
| Credits per day | 1,152,000 |
| Credits per month | 34,560,000 |

### Current Daily Usage (Estimated)

| Scheduler | Frequency | Symbols | Calls/Day |
|-----------|-----------|---------|-----------|
| Daily (all assets) | Once/day | 305 | ~305 |
| Hourly (stocks/crypto) | 24x/day | 105 | ~2,520 |
| 5-minute (top gainers) | 288x/day | 10-20 | ~4,320 |
| Weekly | Once/week | 305 | ~44/day avg |
| **TOTAL** | | | **~7,200** |

### Capacity Utilization

```
Current Daily Usage:     ~7,200 calls
Available Daily Capacity: 1,152,000 calls
UTILIZATION:             0.63% of available capacity
UNUSED CAPACITY:         99.37%
```

---

## Data Volume Per Day (Estimated)

Each API call returns up to 5,000 data points with OHLCV + 24 indicators.

### Current Data Volume

| Timeframe | Symbols | Records/Symbol | Total Records/Day |
|-----------|---------|----------------|-------------------|
| Daily | 305 | 1 | 305 |
| Hourly | 105 | 24 | 2,520 |
| 5-minute | 15 avg | 288 | 4,320 |
| Weekly | 305 | 0.14 | ~44 |
| **TOTAL** | | | **~7,200 records/day** |

### With 24 Indicators Each

- **7,200 records × 45 fields = 324,000 data points/day**
- **~10 million data points/month**

---

## Expansion Opportunities (Untapped Capacity)

### Option 1: Expand Stock Coverage (Conservative)

| Current | Proposed | API Calls |
|---------|----------|-----------|
| 152 stocks | 500 stocks | +348 calls/day |
| Top 152 by market cap | S&P 500 complete | Minimal impact |

**Result:** Full S&P 500 coverage within 0.7% capacity

### Option 2: Expand All Asset Classes (Moderate)

| Asset Type | Current | Proposed | Additional Calls |
|------------|---------|----------|------------------|
| Stocks | 152 | 500 | +348 |
| Crypto | 45 | 100 | +55 |
| ETFs | 40 | 150 | +110 |
| Forex | 30 | 50 | +20 |
| Indices | 9 | 30 | +21 |
| Commodities | 14 | 40 | +26 |
| Funds | 15 | 50 | +35 |
| **TOTAL** | **305** | **920** | **+615** |

**Result:** Triple symbol coverage at 2% capacity

### Option 3: Maximum Extraction (Aggressive)

| Configuration | Symbols | Daily Calls |
|---------------|---------|-------------|
| All timeframes for 2,000 symbols | 2,000 | ~50,000 |
| Daily capacity | - | 1,152,000 |
| **Utilization** | | **4.3%** |

**Result:** 6x current symbols, still under 5% capacity

---

## Additional Endpoints Available (Not Yet Used)

### Fundamentals Data

| Endpoint | Data Provided | API Credits |
|----------|---------------|-------------|
| `/earnings` | Quarterly earnings | 1 per call |
| `/earnings_calendar` | Upcoming earnings | 1 per call |
| `/dividends` | Dividend history | 1 per call |
| `/dividends_calendar` | Ex-dividend dates | 1 per call |
| `/splits` | Stock splits | 1 per call |
| `/splits_calendar` | Upcoming splits | 1 per call |
| `/statistics` | Key stats (P/E, Beta) | 1 per call |
| `/profile` | Company profile | 1 per call |
| `/financials` | Balance sheet, income | 1 per call |
| `/cash_flow` | Cash flow statement | 1 per call |
| `/balance_sheet` | Balance sheet detail | 1 per call |
| `/income_statement` | Income statement | 1 per call |

### Technical Analysis Endpoints

| Endpoint | Indicators |
|----------|------------|
| `/technical_indicators` | Pre-calculated TA |
| `/pattern_recognition` | Candlestick patterns |
| `/pivot_points` | Support/resistance |

### Real-Time Data (Higher Tier)

| Feature | Status |
|---------|--------|
| Real-time quotes | Requires upgrade |
| WebSocket streaming | Requires upgrade |
| Level 2 data | Not available |

---

## Recommendations for Maximum Value

### Phase 1: Immediate (This Week)

1. **Expand S&P 500**: Add remaining 348 stocks
2. **Add Top 100 Crypto**: Expand from 45 to 100
3. **Add Top 100 ETFs**: Expand from 40 to 100
4. **Enable Fundamentals**: Add earnings, dividends, splits

**Impact:** 2x data coverage, <3% capacity used

### Phase 2: Short-Term (Next Month)

1. **Add International Stocks**: FTSE 100, DAX 40, CAC 40
2. **Expand Indices**: Add all valid indices
3. **Historical Backfill**: 5+ years of daily data
4. **Add Weekly Fundamentals**: Financial statements

**Impact:** 3x data coverage, <5% capacity used

### Phase 3: Full Utilization

1. **2,000+ Symbols**: All liquid US securities
2. **Multi-exchange**: Global stock coverage
3. **All Timeframes**: 1-min data for active trading
4. **Full Fundamentals**: All financial endpoints

**Impact:** 10x+ current coverage, ~10% capacity

---

## Summary

| Metric | Current | Potential |
|--------|---------|-----------|
| Symbols tracked | 305 | 2,000+ |
| Daily API calls | ~7,200 | 100,000+ |
| Capacity used | 0.63% | 10%+ |
| Records/day | 7,200 | 100,000+ |
| Data points/month | 10M | 100M+ |

### Key Finding

**You are using less than 1% of your TwelveData $229 plan capacity.**

The plan allows 800 calls/minute (1.15M/day), but current schedulers use only ~7,200 calls/day.

There is massive room for expansion:
- 10x more symbols
- Fundamentals data
- Longer historical periods
- Higher frequency data

---

*Report generated December 17, 2025*
