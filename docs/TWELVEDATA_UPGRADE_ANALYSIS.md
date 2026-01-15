# TwelveData API Upgrade Analysis Report

## Executive Summary

This report analyzes TwelveData pricing plans to help you decide on upgrading from your current plan. TwelveData provides comprehensive financial market data but **does NOT include central bank interest rates**. For interest rate data, we recommend integrating a separate API (see recommendations below).

---

## Current TwelveData Pricing Plans

### Free Plan
- **Cost:** $0/month
- **API Credits:** 800/day
- **Limitations:** 8 API calls/minute, limited to US stocks
- **Best For:** Testing and development

### Basic Plan
- **Cost:** $79/month ($66/month annual)
- **API Credits:** 6,935/day
- **Features:**
  - Extended hours data
  - 55 markets access
  - Technical indicators
  - Fundamental data (basic)

### Pro Plan - **$229/month** ($191/month annual)
- **API Credits:** 1,597 API + 1,500 WebSocket per minute
- **Key Features:**
  - 47 additional markets (102 total)
  - WebSocket real-time streaming
  - Fundamentals data
  - Pre/post US market data
  - Market movers
  - Batch requests (up to 120 symbols)
  - Priority email support

### Ultra Plan - **$999/month** ($832/month annual)
- **API Credits:** 10,946 API + 10,000 WebSocket per minute
- **Key Features:**
  - All 74 exchanges globally
  - Actual fundamentals (real-time)
  - Mutual funds & ETFs breakdown
  - Analysis data (price targets, recommendations)
  - Priority support

### Enterprise Plan - **$1,999/month** ($1,659/month annual)
- **API Credits:** 17,711+ API + 15,000+ WebSocket
- **Key Features:**
  - 83+ markets
  - Historical fundamentals
  - 99.99% SLA guarantee
  - Dedicated account manager
  - Custom solutions

---

## What You Get at $399/month (Pro Plan Annual)

The **$399** price point falls between Basic and Pro plans. At annual billing:
- **Pro Plan:** ~$191/month = ~$2,292/year

### Pro Plan Includes:

| Feature | Availability |
|---------|-------------|
| Real-time Stocks (US) | Yes |
| Real-time Forex | Yes |
| Real-time Crypto | Yes |
| Real-time ETFs | Yes |
| Real-time Indices | Yes |
| Real-time Commodities | Yes |
| Historical Data (20+ years) | Yes |
| Technical Indicators (100+) | Yes |
| Fundamentals (Earnings, Dividends) | Yes |
| Pre/Post Market Data | Yes |
| WebSocket Streaming | Yes |
| Batch Requests | Yes (120 symbols) |

### Pro Plan Does NOT Include:
- Central bank interest rates
- Economic calendar/indicators
- Macroeconomic data
- Historical fundamentals
- Mutual fund composition breakdown

---

## Data Available Through TwelveData API

### Asset Classes
1. **Stocks** - 50,000+ symbols across 102 exchanges
2. **Forex** - 1,200+ currency pairs
3. **Cryptocurrencies** - 2,000+ pairs
4. **ETFs** - 2,500+ funds
5. **Indices** - 300+ global indices
6. **Commodities** - Metals, Energy, Agriculture
7. **Bonds** - Government and corporate
8. **Mutual Funds** - 40,000+ funds (Ultra+ plans)

### Technical Indicators (100+)
- Momentum: RSI, MACD, Stochastic, CCI, Williams %R
- Trend: SMA, EMA, ADX, Ichimoku, SuperTrend
- Volatility: Bollinger Bands, ATR, Keltner Channels
- Volume: OBV, MFI, VWAP, A/D Line
- Overlap: Parabolic SAR, Pivot Points

### Fundamental Data
- Company Profiles
- Earnings Calendar & History
- Dividend Calendar & History
- Stock Splits
- Financial Statements (Income, Balance Sheet, Cash Flow)
- Analyst Ratings & Price Targets
- Insider Trading

### Real-Time Features
- WebSocket streaming
- Quote snapshots
- Market movers (gainers/losers)
- Pre/Post market data

---

## Recommendation for Your Use Case

### For Trading Application with AI (Your Current Setup):
**Recommended: Pro Plan (~$229/month)**

**Reasoning:**
1. WebSocket streaming for real-time price updates
2. 100+ technical indicators calculated server-side
3. Pre/post market data for extended trading
4. Sufficient API credits for your asset coverage
5. Batch requests reduce API calls

### If You Need More:
**Consider Ultra Plan ($999/month) if you need:**
- Mutual fund detailed breakdowns
- Real-time analyst recommendations
- Higher API rate limits
- All global exchanges

---

## Interest Rates Data - Separate Integration Required

**TwelveData does NOT provide central bank interest rates.**

### Recommended Interest Rate APIs:

#### 1. FRED API (Federal Reserve) - FREE
- **URL:** https://fred.stlouisfed.org/docs/api/fred/
- **Coverage:** US rates, some global rates
- **Cost:** Free (unlimited)
- **Data:** Federal Funds Rate, Treasury Yields, LIBOR

#### 2. API Ninjas Interest Rate API
- **URL:** https://api-ninjas.com/api/interestrate
- **Coverage:** 22 countries central bank rates
- **Cost:** Free tier available
- **Update Frequency:** Every 4 hours

#### 3. Nasdaq Data Link (Quandl)
- **URL:** https://data.nasdaq.com
- **Coverage:** Comprehensive global rates
- **Cost:** Free for most datasets
- **Data:** Fed funds, LIBOR, EURIBOR, government yields

#### 4. Zyla Labs Interest Rate APIs
- **URL:** https://zylalabs.com
- **Coverage:** Global central bank rates
- **Cost:** Paid plans starting ~$10/month
- **Features:** Real-time updates, historical data

### Recommended Approach for Interest Rates:
1. **Primary:** FRED API (free, reliable, official US data)
2. **Global:** API Ninjas or Nasdaq Data Link
3. **Integration:** Add to your Cloud Function to fetch and store in BigQuery

---

## Cost-Benefit Analysis

| Plan | Monthly Cost | Annual Cost | Best For |
|------|-------------|-------------|----------|
| Basic | $79 | $792 | Light usage, development |
| **Pro** | $229 | **$2,292** | **Production trading apps** |
| Ultra | $999 | $9,990 | Institutional, heavy usage |
| Enterprise | $1,999 | $19,908 | Large-scale operations |

### Your Current Usage Estimate:
- 6 asset types x 50 symbols = 300 symbols
- 4 timeframes = 1,200 API calls per fetch cycle
- With indicators = ~5,000 calls per full refresh
- **Pro Plan (1,597/min) is sufficient**

---

## Action Items

1. **Upgrade to Pro Plan** if you need WebSocket streaming and higher limits
2. **Integrate FRED API** for US interest rates (free)
3. **Add API Ninjas** for global central bank rates
4. **Create interest_rates table** in BigQuery
5. **Set up schedulers** for automated data collection

---

## Sources

- [TwelveData Pricing](https://twelvedata.com/pricing)
- [TwelveData API Documentation](https://twelvedata.com/docs)
- [FRED API](https://fred.stlouisfed.org/docs/api/fred/)
- [API Ninjas Interest Rate](https://api-ninjas.com/api/interestrate)
- [Nasdaq Data Link](https://data.nasdaq.com)
- [Zyla Labs Interest Rate APIs](https://zylalabs.com/blog/top-global-interest-rates-api-alternatives-in-2025)

---

*Report Generated: November 26, 2025*
