# API Keys Inventory - AIAlgoTradeHits.com
## Complete API Reference for Trading Data Infrastructure

**Last Updated:** December 16, 2025
**Owner:** haq.irfanul@gmail.com

---

## 🔑 CURRENT API KEYS (Active)

### 1. TwelveData API ($229/month Plan)
| Field | Value |
|-------|-------|
| **API Key** | `16ee060fd4d34a628a14bcb6f0167565` |
| **Plan** | Growing ($229/month) |
| **Rate Limit** | 800 calls/minute |
| **Coverage** | Stocks, ETFs, Forex, Crypto, Commodities, Indices |
| **Documentation** | https://twelvedata.com/docs |

**Available Data:**
- 10,300 USA ETFs
- 60 Commodities
- 8-10 USA Indices (SPX, NDX, etc.)
- 1 Interest Rate (US2Y only)
- Unlimited Stocks, Forex, Crypto

---

### 2. FRED API (Federal Reserve Economic Data) - FREE
| Field | Value |
|-------|-------|
| **API Key** | `608f96800c8a5d9bdb8d53ad059f06c1` |
| **Email** | haq.irfanul@gmail.com |
| **Plan** | Free (unlimited) |
| **Rate Limit** | 120 requests/minute |
| **Documentation** | https://fred.stlouisfed.org/docs/api/fred/ |

**Key Series Available:**
| Series ID | Description | Frequency |
|-----------|-------------|-----------|
| FEDFUNDS | Federal Funds Rate | Monthly |
| DGS10 | 10-Year Treasury Yield | Daily |
| DGS2 | 2-Year Treasury Yield | Daily |
| DGS30 | 30-Year Treasury Yield | Daily |
| DGS5 | 5-Year Treasury Yield | Daily |
| UNRATE | Unemployment Rate | Monthly |
| CPIAUCSL | Consumer Price Index | Monthly |
| GDP | Gross Domestic Product | Quarterly |
| MORTGAGE30US | 30-Year Mortgage Rate | Weekly |
| T10Y2Y | 10Y-2Y Treasury Spread | Daily |
| VIXCLS | VIX Volatility Index | Daily |
| SP500 | S&P 500 Index | Daily |
| DJIA | Dow Jones Industrial | Daily |
| NASDAQCOM | NASDAQ Composite | Daily |
| M2SL | M2 Money Supply | Monthly |
| WALCL | Fed Total Assets | Weekly |

**Total FRED Series:** 800,000+ economic indicators

---

### 3. Finnhub API
| Field | Value |
|-------|-------|
| **API Key** | `d4dg7t9r01qovljpm3g0d4dg7t9r01qovljpm3gg` |
| **Plan** | Free tier |
| **Rate Limit** | 60 calls/minute (free) |
| **Documentation** | https://finnhub.io/docs/api |

**Available Data:**
- Stock quotes & candles
- Company fundamentals
- Insider transactions
- Analyst recommendations
- Earnings calendar
- IPO calendar
- Economic calendar
- News & sentiment
- SEC filings

---

### 4. CoinMarketCap API
| Field | Value |
|-------|-------|
| **API Key** | `059474ae48b84628be6f4a94f9840c30` |
| **Plan** | Basic (Free) |
| **Rate Limit** | 333 calls/day |
| **Documentation** | https://coinmarketcap.com/api/documentation/v1/ |

**Available Data:**
- Cryptocurrency listings
- Market cap rankings
- Price quotes
- Historical data
- Exchange listings
- Global metrics

---

### 5. Google Cloud Platform
| Field | Value |
|-------|-------|
| **Project ID** | `aialgotradehits` |
| **Region** | `us-central1` |
| **Services** | BigQuery, Cloud Run, Cloud Functions, Cloud Scheduler |
| **Service Account** | `aialgotradehits-8863a22a9958.json` |

---

## 📊 RECOMMENDED ADDITIONAL FREE APIs

### Economic Data

| API | Cost | Data Type | URL |
|-----|------|-----------|-----|
| **BLS API** | Free | Employment, CPI, PPI | https://www.bls.gov/developers/ |
| **Census API** | Free | Demographics, Trade | https://www.census.gov/data/developers/data-sets.html |
| **BEA API** | Free | GDP, Trade, Income | https://apps.bea.gov/API/signup/ |
| **Treasury API** | Free | Debt, Rates | https://fiscaldata.treasury.gov/api-documentation/ |
| **World Bank API** | Free | Global indicators | https://datahelpdesk.worldbank.org/knowledgebase/topics/125589 |

### Financial Data

| API | Cost | Data Type | URL |
|-----|------|-----------|-----|
| **Alpha Vantage** | Free tier | Stocks, Forex, Crypto | https://www.alphavantage.co/ |
| **Yahoo Finance** | Free | Stocks, ETFs, Options | Via yfinance Python package |
| **IEX Cloud** | Free tier | Real-time quotes | https://iexcloud.io/ |
| **Polygon.io** | Free tier | Stocks, Options | https://polygon.io/ |
| **Quandl/Nasdaq** | Free tier | Alt data | https://data.nasdaq.com/ |

### News & Sentiment

| API | Cost | Data Type | URL |
|-----|------|-----------|-----|
| **NewsAPI** | Free tier | News articles | https://newsapi.org/ |
| **Marketaux** | Free tier | Financial news | https://www.marketaux.com/ |
| **GNews** | Free tier | News aggregation | https://gnews.io/ |

### Crypto Specific

| API | Cost | Data Type | URL |
|-----|------|-----------|-----|
| **CoinGecko** | Free | Crypto data | https://www.coingecko.com/en/api |
| **Binance API** | Free | Trading data | https://binance-docs.github.io/apidocs/ |
| **Kraken API** | Free | Trading data | https://docs.kraken.com/rest/ |

---

## 🔧 API USAGE IN CODEBASE

### TwelveData Integration Points:
- `cloud_function_all_assets/main.py` - All 7 asset types
- `cloud_function_stocks_daily/main.py` - Stock data
- `highspeed_data_accelerator.py` - Bulk fetching
- All schedulers use TwelveData for market data

### FRED Integration Points:
- To be created: `cloud_function_fred/main.py`
- Recommended for: Treasury yields, economic indicators

### Finnhub Integration Points:
- `fetch_finnhub_data.py` - Analyst recommendations
- `explore_finnhub_api.py` - API exploration
- Used for: Insider transactions, earnings calendar

### CoinMarketCap Integration Points:
- Crypto rankings and market cap data
- Global crypto market metrics

---

## 📋 API KEY SECURITY NOTES

⚠️ **IMPORTANT:**
1. Never commit API keys to public repositories
2. Use environment variables in production
3. Rotate keys periodically
4. Monitor usage to avoid rate limits
5. Keep backup keys for critical services

### Environment Variables Setup:
```bash
export TWELVEDATA_API_KEY="16ee060fd4d34a628a14bcb6f0167565"
export FRED_API_KEY="608f96800c8a5d9bdb8d53ad059f06c1"
export FINNHUB_API_KEY="d4dg7t9r01qovljpm3g0d4dg7t9r01qovljpm3gg"
export COINMARKETCAP_API_KEY="059474ae48b84628be6f4a94f9840c30"
```

---

## 📈 DATA COVERAGE SUMMARY

| Data Type | Primary Source | Backup Source |
|-----------|---------------|---------------|
| Stocks (OHLCV) | TwelveData | Yahoo Finance |
| ETFs | TwelveData | Yahoo Finance |
| Crypto | TwelveData | CoinMarketCap, CoinGecko |
| Forex | TwelveData | - |
| Indices | TwelveData | FRED |
| Commodities | TwelveData | - |
| Treasury Yields | FRED | TwelveData (limited) |
| Economic Data | FRED | BLS, BEA |
| Fundamentals | TwelveData, Finnhub | Yahoo Finance |
| News/Sentiment | Finnhub | NewsAPI |
| Analyst Ratings | Finnhub | - |

---

*Document maintained by AIAlgoTradeHits Trading Infrastructure*
