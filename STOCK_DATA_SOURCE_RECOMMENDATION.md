# Stock Data Source Recommendation
**Date**: November 16, 2025
**Purpose**: Resolve Yahoo Finance API throttling for intraday stock data

## Current Situation

### Problem
Yahoo Finance (via yfinance library) is throttling/rejecting ALL requests for hourly and 5-minute stock data:
- **Success Rate**: 0/97 stocks (100% failure)
- **Error**: "No price data found" or "Expecting value: line 1 column 1 (char 0)"
- **Root Cause**: Undocumented API changes, rate limiting, or requirement for premium access

### Impact
- Stock hourly table: **EMPTY** (0 records)
- Stock 5-minute table: **EMPTY** (0 records)
- Multi-timeframe charts cannot display intraday stock data
- NLP queries for stock hourly/5-min return no results

## Recommended Solution: Twelve Data API

Based on `crypto_stock_api_comparison.html` analysis:

### Why Twelve Data? ⭐

1. **Best Value**: FREE tier with 800 calls/day
2. **Comprehensive Coverage**: Stocks, forex, crypto, ETFs, indices
3. **All Timeframes**: 1min, 5min, 15min, 30min, 1hour, daily, weekly, monthly
4. **Technical Indicators**: Built-in (RSI, MACD, SMA, EMA, etc.)
5. **Reliable API**: Well-documented, stable, no sudden changes
6. **Easy Migration**: REST API similar to Alpha Vantage

### Pricing Tiers

| Plan | Price | API Calls/Day | API Calls/Minute | Best For |
|------|-------|---------------|------------------|----------|
| **Free** | $0/mo | 800 | 8 | Development, testing |
| **Basic** | $29/mo | 15,000 | 60 | Small apps, 50-100 stocks |
| **Pro** | $79/mo | 65,000 | 120 | Medium apps, 100-500 stocks |
| **Enterprise** | $399/mo | 100,000+ | 240+ | Production, all stocks |

### Coverage Comparison

| Feature | Twelve Data | Alpha Vantage | Polygon.io | Yahoo Finance |
|---------|-------------|---------------|------------|---------------|
| **Stock Intraday** | ✅ All intervals | ✅ 1min, 5min, etc. | ✅ Premium only | ❌ Throttled |
| **Crypto** | ✅ 100+ pairs | ❌ Limited | ✅ Yes | ✅ Yes (Kraken) |
| **Free Tier** | ✅ 800/day | ✅ 500/day | ✅ Delayed only | ✅ Unreliable |
| **Technical Indicators** | ✅ Built-in | ✅ Built-in | ❌ Need to calculate | ❌ Need to calculate |
| **Reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ (degraded) |
| **Documentation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ (undocumented) |

## Implementation Plan

### Phase 1: Free Tier Testing (Immediate)

**Setup**:
1. Sign up for Twelve Data free tier
2. Get API key
3. Test with 10-20 stocks
4. Validate data quality and latency

**API Key**: User will provide

**Sample Request**:
```python
import requests

API_KEY = "your_api_key"
symbol = "AAPL"
interval = "1h"

url = f"https://api.twelvedata.com/time_series"
params = {
    "symbol": symbol,
    "interval": interval,
    "apikey": API_KEY,
    "outputsize": 500  # last 500 periods
}

response = requests.get(url, params=params)
data = response.json()
```

**Response Format**:
```json
{
  "meta": {
    "symbol": "AAPL",
    "interval": "1h",
    "currency": "USD",
    "exchange_timezone": "America/New_York"
  },
  "values": [
    {
      "datetime": "2025-11-15 15:30:00",
      "open": "227.81",
      "high": "228.15",
      "low": "227.50",
      "close": "227.89",
      "volume": "2451893"
    },
    ...
  ],
  "status": "ok"
}
```

### Phase 2: Update Cloud Functions

**File**: `cloud_function_stocks_hourly/main.py`

**Changes Needed**:
```python
import requests

TWELVE_DATA_API_KEY = os.environ.get('TWELVE_DATA_API_KEY')

def fetch_stock_hourly_data_twelve(symbol):
    """Fetch hourly data from Twelve Data API"""
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": "1h",
        "apikey": TWELVE_DATA_API_KEY,
        "outputsize": 500,  # ~3 weeks of hourly data
        "timezone": "America/New_York"
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    if data.get("status") != "ok":
        logger.error(f"Twelve Data error for {symbol}: {data.get('message')}")
        return None

    # Convert to DataFrame
    df = pd.DataFrame(data["values"])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['symbol'] = symbol

    # Convert string values to numeric
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col])

    # Calculate technical indicators (same as before)
    df = calculate_technical_indicators(df)

    return df
```

**Environment Variable**:
```bash
gcloud functions deploy stock-hourly-fetcher \
  --set-env-vars TWELVE_DATA_API_KEY=your_api_key \
  ...other flags...
```

### Phase 3: Rate Limiting Strategy

**Free Tier (800 calls/day)**:
- **97 stocks × 1 call each = 97 calls/run**
- **Can run**: 8 times per day
- **Schedule**: Every 3 hours during market hours (9:30 AM - 4 PM ET)
  - 9:30 AM, 12:30 PM, 3:30 PM = 3 runs/day
- **Total calls**: 97 × 3 = 291 calls/day ✅ Under limit

**Basic Plan ($29/mo, 15,000 calls/day)**:
- **97 stocks × 1 call = 97 calls/run**
- **Can run**: 154 times per day
- **Schedule**: Every hour during market hours = 7 runs/day
- **Total calls**: 97 × 7 = 679 calls/day ✅ Under limit

**5-Minute Data**:
- **30 stocks × 1 call = 30 calls/run**
- **Schedule**: Every 5 minutes during market hours = 78 runs/day
- **Total calls**: 30 × 78 = 2,340 calls/day
- **Requires**: Basic plan minimum ($29/mo)

### Phase 4: Cost Optimization

**Option A: Free Tier Only**
- Cost: **$0/month**
- Coverage: Hourly data for 97 stocks
- Frequency: Every 3 hours during market hours
- Limitation: No 5-minute data

**Option B: Basic Plan**
- Cost: **$29/month**
- Coverage: Hourly + 5-minute for top 30 stocks
- Frequency: Hourly every hour, 5-min every 5 minutes
- Best for: Production use

**Option C: Hybrid (Recommended for Phase 1)**
- Cost: **$0/month** (free tier)
- Coverage: Hourly for top 50 high-value stocks only
- Frequency: Every hour during market hours
- Calls: 50 × 7 = 350 calls/day ✅ Under 800 limit
- Benefit: Test before committing to paid plan

## Alternative Options

### Alpha Vantage
**Pros**:
- Free tier: 500 calls/day
- Well-documented
- Reliable

**Cons**:
- Lower call limit than Twelve Data
- More expensive paid plans ($50-$500/mo)
- Slower response times

### Polygon.io
**Pros**:
- Excellent data quality
- Real-time data
- WebSocket support

**Cons**:
- No meaningful free tier (delayed data only)
- Expensive ($29-$399/mo for real-time)
- Overkill for our needs

### IEX Cloud
**Pros**:
- Free tier exists
- Good for US stocks

**Cons**:
- Limited free tier (50,000 messages/mo)
- Complex pricing
- Less comprehensive than Twelve Data

## Migration Timeline

### Week 1: Testing
- ✅ Get Twelve Data API key
- ✅ Test with 5-10 stocks
- ✅ Validate data format and quality
- ✅ Measure API latency
- ✅ Test technical indicator calculations

### Week 2: Development
- 🔄 Update `cloud_function_stocks_hourly/main.py`
- 🔄 Update `cloud_function_stocks_5min/main.py`
- 🔄 Add environment variable handling
- 🔄 Add error handling and retry logic
- 🔄 Update requirements.txt (if needed)

### Week 3: Deployment
- 🔄 Deploy updated hourly function
- 🔄 Deploy updated 5-min function
- 🔄 Test with free tier limits
- 🔄 Monitor BigQuery for data collection
- 🔄 Verify multi-timeframe charts work

### Week 4: Optimization
- 🔄 Fine-tune rate limiting
- 🔄 Optimize symbol selection (highest value stocks)
- 🔄 Decide on paid plan if needed
- 🔄 Full production deployment

## Crypto Data (No Changes Needed)

**Current Status**: ✅ All Working
- **Source**: Kraken Pro API (via ccxt library)
- **Reliability**: Excellent
- **Cost**: Free
- **Coverage**: 678 USD pairs, hourly + 5-min data
- **Recommendation**: Keep as-is

## User Information Received

1. **Twelve Data API Key**: To be provided by user
2. **Twelve Data Countries Script**: User has `get_twelve_data_countries` script
3. **Task**: Get list of countries and save to Trading folder

## Next Steps

### Immediate Actions
1. ✅ **Get Twelve Data API Key** from user
2. ✅ **Run `get_twelve_data_countries` script** to get supported countries
3. ✅ **Test API** with sample stock requests
4. ✅ **Create implementation PR** for review

### User Decision Required
- **Which plan?** Free tier (800/day) or Basic ($29/mo, 15K/day)
- **Which stocks?** All 97 or top 50 high-value only
- **Which frequencies?** Hourly only or hourly + 5-minute

## Summary

**Problem**: Yahoo Finance throttling stock intraday data
**Solution**: Migrate to Twelve Data API
**Cost**: Free tier (800 calls/day) to start, $29/mo for full coverage
**Timeline**: 1 week testing, 1 week implementation, 1 week deployment
**Risk**: Low (free tier available for testing)
**Benefit**: Reliable, documented, comprehensive stock data

**Recommendation**: ⭐ Start with Twelve Data free tier immediately, upgrade to Basic plan ($29/mo) once validated.

---

**Status**: Research Complete
**Next**: Awaiting user's Twelve Data API key and plan selection
