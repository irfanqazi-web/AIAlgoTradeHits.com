# Trading Data Status Report
## AIAlgoTradeHits - TwelveData Pipeline
**Generated:** December 17, 2025
**GCP Project:** aialgotradehits
**Dataset:** crypto_trading_data

---

## Executive Summary

The TwelveData data pipeline is now operational across **7 asset types** with **28 tables** covering 4 timeframes (daily, hourly, 5-minute, weekly). The latest parallel fetch added **91,615 new records** across all asset types.

### Overall Statistics
| Metric | Value |
|--------|-------|
| Total Asset Types | 7 |
| Total Tables | 28 |
| Total Symbols Tracked | 305+ |
| Data Range | 2022-2025 |
| API Plan | TwelveData $229/month |
| API Credits | 800/minute |

---

## Asset Type Coverage

### 1. STOCKS (US Equities)
| Table | Records | Symbols | Date Range |
|-------|---------|---------|------------|
| v2_stocks_daily | 186,150 | 152 | Jul 2024 - Dec 2025 |
| v2_stocks_hourly | 1,253,112 | 60 | Nov 2025 - Dec 2025 |
| v2_stocks_5min | 4,976,640 | 60 | Dec 2025 |
| v2_stocks_weekly | Available | 60+ | Historical |

**Top Symbols:** AAPL, MSFT, AMZN, NVDA, GOOGL, META, TSLA, JPM, V, MA, JNJ, UNH, HD, PG, etc.

### 2. CRYPTO (Cryptocurrencies)
| Table | Records | Symbols | Date Range |
|-------|---------|---------|------------|
| v2_crypto_daily | 98,550 | 45 | Dec 2024 - Dec 2025 |
| v2_crypto_hourly | 937,440 | 45 | Dec 2025 |
| v2_crypto_5min | 19,210,464 | 45 | Dec 2025 |
| v2_crypto_weekly | Available | 45+ | Historical |

**Top Symbols:** BTCUSD, ETHUSD, BNBUSD, XRPUSD, SOLUSD, ADAUSD, DOGEUSD, AVAXUSD, LINKUSD, etc.

### 3. FOREX (Currency Pairs)
| Table | Records | Symbols | Date Range |
|-------|---------|---------|------------|
| v2_forex_daily | 54,750 | 30 | Aug 2024 - Dec 2025 |
| v2_forex_hourly | 416,640 | 20 | Dec 2025 |
| v2_forex_5min | 5,265,504 | 20 | Dec 2025 |
| v2_forex_weekly | Available | 30 | Historical |

**Pairs:** EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD, EUR/GBP, EUR/JPY, GBP/JPY, etc.

### 4. ETFs (Exchange-Traded Funds)
| Table | Records | Symbols | Date Range |
|-------|---------|---------|------------|
| v2_etfs_daily | 67,160 | 40 | Jul 2024 - Dec 2025 |
| v2_etfs_hourly | 520,800 | 25 | Nov 2025 - Dec 2025 |
| v2_etfs_5min | 2,073,600 | 25 | Dec 2025 |
| v2_etfs_weekly | Available | 40 | Historical |

**Top ETFs:** SPY, QQQ, DIA, IWM, VOO, VTI, ARKK, XLF, XLK, XLE, XLV, GLD, SLV, TLT, etc.

### 5. INDICES (Market Indices)
| Table | Records | Symbols | Date Range |
|-------|---------|---------|------------|
| v2_indices_daily | 5,475 | 9 | Jan 2022 - Dec 2025 |
| v2_indices_hourly | 20,832 | 1 | Nov 2025 - Dec 2025 |
| v2_indices_5min | 82,656 | 1 | Nov 2025 - Dec 2025 |
| v2_indices_weekly | Available | 9 | Historical |

**Indices:** SPX, NDX, DAX, CAC, FTSE, HSI, AEX, SMI, IBEX

### 6. COMMODITIES
| Table | Records | Symbols | Date Range |
|-------|---------|---------|------------|
| v2_commodities_daily | 29,407 | 14 | Jul 2024 - Dec 2025 |
| v2_commodities_hourly | 252,000 | 12 | Aug 2025 - Dec 2025 |
| v2_commodities_5min | 3,175,488 | 12 | Jun 2025 - Dec 2025 |
| v2_commodities_weekly | Available | 14 | Historical |

**Commodities:** XAU/USD (Gold), XAG/USD (Silver), CL (WTI Oil), BZ (Brent), NG (Natural Gas), HG (Copper), ZC (Corn), ZS (Soybeans), KC (Coffee), SB (Sugar)

### 7. FUNDS (Mutual Funds) - NEW
| Table | Records | Symbols | Date Range |
|-------|---------|---------|------------|
| v2_funds_daily | 5,475 | 15 | Jan 2024 - Dec 2025 |

**Top Funds:** VFINX, VTSAX, FXAIX, VFIAX, VGTSX, VTSMX, FMAGX, PRWCX, AGTHX, OAKMX

---

## Cloud Schedulers Status

All schedulers are **ENABLED** and running:

| Scheduler | Schedule | Asset Type | Status |
|-----------|----------|------------|--------|
| twelvedata-daily-stocks | 0 0 * * * | Stocks | ENABLED |
| twelvedata-daily-crypto | 5 0 * * * | Crypto | ENABLED |
| twelvedata-daily-forex | 10 0 * * * | Forex | ENABLED |
| twelvedata-daily-etfs | 15 0 * * * | ETFs | ENABLED |
| twelvedata-daily-indices | 20 0 * * * | Indices | ENABLED |
| twelvedata-daily-commodities | 25 0 * * * | Commodities | ENABLED |
| twelvedata-hourly-stocks | 0 * * * * | Stocks | ENABLED |
| twelvedata-hourly-crypto | 5 * * * * | Crypto | ENABLED |
| twelvedata-hourly-forex | 10 * * * * | Forex | ENABLED |
| twelvedata-5min-stocks | */5 9-16 * * 1-5 | Stocks | ENABLED |
| twelvedata-5min-crypto | */5 * * * * | Crypto | ENABLED |
| twelvedata-weekly-all | 0 0 * * 0 | All | ENABLED |

---

## Technical Indicators (Per Masterquery Spec)

All tables include **24 technical indicators**:

### Momentum (6)
- RSI_14
- MACD, MACD_Signal, MACD_Histogram
- Stoch_K, Stoch_D

### Trend (10)
- SMA_20, SMA_50, SMA_200
- EMA_12, EMA_20, EMA_26, EMA_50, EMA_200
- Ichimoku Tenkan, Kijun (selected tables)

### Volatility (4)
- ATR_14
- BB_Upper, BB_Middle, BB_Lower

### Trend Strength (3)
- ADX, Plus_DI, Minus_DI

### Flow (2)
- MFI
- CMF (selected tables)

### Computed Signals
- Growth Score (0-100)
- In Rise Cycle (boolean)
- Trend Regime (string)

---

## Data Quality

| Check | Status |
|-------|--------|
| Daily data freshness | Current (Dec 17, 2025) |
| Hourly data freshness | Current |
| 5-min data freshness | Current |
| Duplicate detection | Enabled |
| Indicator calculation | 24 indicators |
| Rate limiting | 800 calls/min enforced |

---

## API Endpoints

**Base URL:** `https://trading-api-1075463475276.us-central1.run.app`

| Endpoint | Purpose |
|----------|---------|
| `/api/ai/trading-signals` | Generate buy/sell signals |
| `/api/ai/rise-cycle-candidates` | EMA crossover detection |
| `/api/ai/ml-predictions` | Growth score predictions |
| `/api/ai/growth-screener` | High growth scanner |
| `/api/ai/text-to-sql` | Natural language queries |

---

## Issues & Notes

1. **Indices Coverage:** Some international indices (N225, RUT, VIX) have invalid TwelveData symbols - need to find correct mappings
2. **Rate Limiting:** With 150+ stocks, sequential batch processing is required to stay within 800 calls/min
3. **Crypto Data:** Existing daily crypto data is current; new symbols may need separate fetch

---

## Recommendations

1. **Fix Index Symbols:** Update TwelveData index symbols (N225 -> NKX, etc.)
2. **Add More Indices:** Research valid TwelveData symbols for Russell 2000, VIX, etc.
3. **Monitor Schedulers:** All 40+ schedulers are active - monitor Cloud Function logs
4. **ML Feature Tables:** Update ml_models.daily_features_24 with new symbols

---

## Cost Estimate

| Component | Monthly Cost |
|-----------|-------------|
| TwelveData API | $229 |
| Cloud Functions | ~$50 |
| BigQuery Storage | ~$5 |
| Cloud Schedulers | ~$1 |
| **Total** | **~$285/month** |

---

*Report generated by parallel_all_assets_fetcher.py*
*Last fetch: 91,615 records in 16.6 minutes*
