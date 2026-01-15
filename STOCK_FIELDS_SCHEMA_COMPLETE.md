# Stock Data Fields - Complete Schema with Descriptions
**Generated:** December 8, 2025
**Purpose:** Comprehensive BigQuery schema for stock trading data
**Total Fields:** 84 (after removing 5 duplicates from original 89)

---

## SCHEMA OVERVIEW

### Field Categories:
1. **Core Identifiers & Timestamps** (3 fields) - S# 1-3
2. **OHLCV Price Data** (6 fields) - S# 4-9
3. **Price Change Statistics** (6 fields) - S# 10-15
4. **Technical Indicators - Momentum** (9 fields) - S# 16-24
5. **Technical Indicators - Moving Averages** (9 fields) - S# 25-33
6. **Technical Indicators - Trend & Volatility** (10 fields) - S# 34-43
7. **Technical Indicators - Volume** (3 fields) - S# 44-46
8. **Advanced ML Features - Returns** (3 fields) - S# 47-49
9. **Advanced ML Features - Relative Positions** (3 fields) - S# 50-52
10. **Advanced ML Features - Indicator Dynamics** (10 fields) - S# 53-62
11. **Advanced ML Features - Market Structure** (6 fields) - S# 63-68
12. **Advanced ML Features - Regime Detection** (3 fields) - S# 69-71
13. **Asset Metadata** (9 fields) - S# 72-80
14. **System Metadata** (4 fields) - S# 81-84

---

# COMPLETE FIELD DEFINITIONS

## 1. CORE IDENTIFIERS & TIMESTAMPS

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 1 | `datetime` | TIMESTAMP | Market DateTime | Primary timestamp of the trading data point (YYYY-MM-DD HH:MM:SS UTC) | REQUIRED |
| 2 | `symbol` | STRING | Stock Ticker Symbol | Standard trading symbol (e.g., AAPL, MSFT, TSLA) | REQUIRED |
| 3 | `timestamp` | INTEGER | Unix Timestamp | Unix epoch timestamp (seconds since 1970-01-01, for sorting/filtering) | NULLABLE |

---

## 2. OHLCV PRICE DATA

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 4 | `open` | FLOAT | Opening Price | First trade price of the period (USD) | NULLABLE |
| 5 | `high` | FLOAT | Highest Price | Highest trade price during the period (USD) | NULLABLE |
| 6 | `low` | FLOAT | Lowest Price | Lowest trade price during the period (USD) | NULLABLE |
| 7 | `close` | FLOAT | Closing Price | Last trade price of the period (USD) | NULLABLE |
| 8 | `previous_close` | FLOAT | Previous Closing Price | Closing price from the previous period (USD, for change calculations) | NULLABLE |
| 9 | `volume` | INTEGER | Trading Volume | Number of shares traded during the period | NULLABLE |

---

## 3. PRICE CHANGE STATISTICS

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 10 | `average_volume` | INTEGER | Average Trading Volume | Average volume over recent periods (typically 20-30 days) | NULLABLE |
| 11 | `change` | FLOAT | Price Change (Absolute) | Absolute price change: close - previous_close (USD) | NULLABLE |
| 12 | `percent_change` | FLOAT | Price Change (Percentage) | Percentage change: (close - previous_close) / previous_close * 100 (%) | NULLABLE |
| 13 | `high_low` | FLOAT | High-Low Range | Intraday price range: high - low (USD, absolute volatility measure) | NULLABLE |
| 14 | `pct_high_low` | FLOAT | High-Low Range (Percentage) | Percentage range: (high - low) * 100 / low (% relative to low price) | NULLABLE |
| 15 | `week_52_high` | FLOAT | 52-Week High | Highest price in the past 252 trading days (USD) | NULLABLE |
| 16 | `week_52_low` | FLOAT | 52-Week Low | Lowest price in the past 252 trading days (USD) | NULLABLE |

**Note:** Removed duplicate `week_52_high` at original S# 13

---

## 4. TECHNICAL INDICATORS - MOMENTUM

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 17 | `rsi` | FLOAT | Relative Strength Index | RSI momentum oscillator (0-100, oversold <30, overbought >70, period=14) | NULLABLE |
| 18 | `macd` | FLOAT | MACD Line | Moving Average Convergence Divergence line (12-day EMA - 26-day EMA) | NULLABLE |
| 19 | `macd_signal` | FLOAT | MACD Signal Line | 9-day EMA of MACD line (for crossover signals) | NULLABLE |
| 20 | `macd_histogram` | FLOAT | MACD Histogram | Difference: MACD - MACD Signal (measures momentum strength) | NULLABLE |
| 21 | `stoch_k` | FLOAT | Stochastic %K | Fast stochastic oscillator (0-100, period=14, overbought >80, oversold <20) | NULLABLE |
| 22 | `stoch_d` | FLOAT | Stochastic %D | Slow stochastic (3-day SMA of %K, smoother signal) | NULLABLE |
| 23 | `cci` | FLOAT | Commodity Channel Index | CCI momentum indicator (typical range: -100 to +100, period=20) | NULLABLE |
| 24 | `williams_r` | FLOAT | Williams %R | Williams Percent Range (-100 to 0, oversold <-80, overbought >-20, period=14) | NULLABLE |
| 25 | `momentum` | FLOAT | Momentum Indicator | Rate of price change: close - close[n periods ago] (period=10) | NULLABLE |

**Note:** Removed duplicate `williams_r` at original S# 38 and duplicate `momentum` at original S# 37

---

## 5. TECHNICAL INDICATORS - MOVING AVERAGES

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 26 | `sma_20` | FLOAT | Simple Moving Average (20-day) | 20-period simple moving average (short-term trend) | NULLABLE |
| 27 | `sma_50` | FLOAT | Simple Moving Average (50-day) | 50-period simple moving average (medium-term trend) | NULLABLE |
| 28 | `sma_200` | FLOAT | Simple Moving Average (200-day) | 200-period simple moving average (long-term trend) | NULLABLE |
| 29 | `ema_12` | FLOAT | Exponential Moving Average (12-day) | 12-period exponential moving average (MACD fast line component) | NULLABLE |
| 30 | `ema_20` | FLOAT | Exponential Moving Average (20-day) | 20-period exponential moving average (short-term trend, more reactive) | NULLABLE |
| 31 | `ema_26` | FLOAT | Exponential Moving Average (26-day) | 26-period exponential moving average (MACD slow line component) | NULLABLE |
| 32 | `ema_50` | FLOAT | Exponential Moving Average (50-day) | 50-period exponential moving average (medium-term trend) | NULLABLE |
| 33 | `ema_200` | FLOAT | Exponential Moving Average (200-day) | 200-period exponential moving average (long-term trend) | NULLABLE |
| 34 | `kama` | FLOAT | Kaufman Adaptive Moving Average | KAMA adaptive moving average (adjusts to market volatility, period=10) | NULLABLE |

**Note:** Removed duplicate `ema_50` at original S# 39

---

## 6. TECHNICAL INDICATORS - TREND & VOLATILITY

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 35 | `bollinger_upper` | FLOAT | Bollinger Band (Upper) | Upper Bollinger Band: SMA(20) + 2*StdDev (resistance level) | NULLABLE |
| 36 | `bollinger_middle` | FLOAT | Bollinger Band (Middle) | Middle Bollinger Band: 20-period SMA (baseline) | NULLABLE |
| 37 | `bollinger_lower` | FLOAT | Bollinger Band (Lower) | Lower Bollinger Band: SMA(20) - 2*StdDev (support level) | NULLABLE |
| 38 | `bb_width` | FLOAT | Bollinger Band Width | Band width: (upper - lower) / middle * 100 (volatility measure, %) | NULLABLE |
| 39 | `adx` | FLOAT | Average Directional Index | ADX trend strength indicator (0-100, strong trend >25, period=14) | NULLABLE |
| 40 | `plus_di` | FLOAT | Plus Directional Indicator (+DI) | Positive directional movement (bullish pressure, 0-100, period=14) | NULLABLE |
| 41 | `minus_di` | FLOAT | Minus Directional Indicator (-DI) | Negative directional movement (bearish pressure, 0-100, period=14) | NULLABLE |
| 42 | `atr` | FLOAT | Average True Range | ATR volatility indicator (absolute volatility in USD, period=14) | NULLABLE |
| 43 | `trix` | FLOAT | TRIX Indicator | Triple exponential average rate of change (momentum, period=15) | NULLABLE |
| 44 | `roc` | FLOAT | Rate of Change | ROC momentum indicator: (close - close[n]) / close[n] * 100 (%, period=10) | NULLABLE |

---

## 7. TECHNICAL INDICATORS - VOLUME

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 45 | `obv` | FLOAT | On-Balance Volume | OBV cumulative volume indicator (measures buying/selling pressure) | NULLABLE |
| 46 | `pvo` | FLOAT | Percentage Volume Oscillator | PVO volume momentum: (12-day EMA vol - 26-day EMA vol) / 26-day * 100 (%) | NULLABLE |
| 47 | `ppo` | FLOAT | Percentage Price Oscillator | PPO price momentum: (12-day EMA - 26-day EMA) / 26-day EMA * 100 (%) | NULLABLE |

**Note:** Removed duplicate `obv` at original S# 42

---

## 8. TECHNICAL INDICATORS - ADVANCED OSCILLATORS

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 48 | `ultimate_osc` | FLOAT | Ultimate Oscillator | Multi-timeframe momentum oscillator (7/14/28 periods, 0-100) | NULLABLE |
| 49 | `awesome_osc` | FLOAT | Awesome Oscillator | Awesome Oscillator: 5-period SMA - 34-period SMA of midpoints | NULLABLE |

---

## 9. ADVANCED ML FEATURES - RETURNS

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 50 | `log_return` | FLOAT | Logarithmic Return (1-day) | Natural log return: ln(close / previous_close), for ML feature scaling | NULLABLE |
| 51 | `return_2w` | FLOAT | Forward Return (2-week) | Forward-looking 2-week (10-day) return: (close[+10] - close) / close | NULLABLE |
| 52 | `return_4w` | FLOAT | Forward Return (4-week) | Forward-looking 4-week (20-day) return: (close[+20] - close) / close | NULLABLE |

---

## 10. ADVANCED ML FEATURES - RELATIVE POSITIONS

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 53 | `close_vs_sma20_pct` | FLOAT | Close vs SMA20 (Percentage) | Distance from 20-day SMA: (close - sma_20) / sma_20 * 100 (%) | NULLABLE |
| 54 | `close_vs_sma50_pct` | FLOAT | Close vs SMA50 (Percentage) | Distance from 50-day SMA: (close - sma_50) / sma_50 * 100 (%) | NULLABLE |
| 55 | `close_vs_sma200_pct` | FLOAT | Close vs SMA200 (Percentage) | Distance from 200-day SMA: (close - sma_200) / sma_200 * 100 (%) | NULLABLE |

---

## 11. ADVANCED ML FEATURES - INDICATOR DYNAMICS

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 56 | `rsi_slope` | FLOAT | RSI Slope (Rate of Change) | 5-day slope of RSI (momentum acceleration/deceleration) | NULLABLE |
| 57 | `rsi_zscore` | FLOAT | RSI Z-Score | Z-score of RSI over 20 periods (standardized deviation from mean) | NULLABLE |
| 58 | `rsi_overbought` | INTEGER | RSI Overbought Flag | Binary flag: 1 if RSI > 70 (overbought), 0 otherwise | NULLABLE |
| 59 | `rsi_oversold` | INTEGER | RSI Oversold Flag | Binary flag: 1 if RSI < 30 (oversold), 0 otherwise | NULLABLE |
| 60 | `macd_cross` | INTEGER | MACD Crossover Signal | Binary flag: 1 if MACD > Signal (bullish), 0 if MACD < Signal (bearish) | NULLABLE |
| 61 | `ema20_slope` | FLOAT | EMA20 Slope | 5-day slope of 20-day EMA (short-term trend direction) | NULLABLE |
| 62 | `ema50_slope` | FLOAT | EMA50 Slope | 5-day slope of 50-day EMA (medium-term trend direction) | NULLABLE |
| 63 | `atr_zscore` | FLOAT | ATR Z-Score | Z-score of ATR over 20 periods (volatility regime detection) | NULLABLE |
| 64 | `atr_slope` | FLOAT | ATR Slope | 5-day slope of ATR (volatility acceleration) | NULLABLE |
| 65 | `volume_zscore` | FLOAT | Volume Z-Score | Z-score of volume over 20 periods (abnormal volume detection) | NULLABLE |

---

## 12. ADVANCED ML FEATURES - VOLUME & PRICE RATIOS

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 66 | `volume_ratio` | FLOAT | Volume Ratio | Current volume / average_volume (volume surge detection) | NULLABLE |

---

## 13. ADVANCED ML FEATURES - MARKET STRUCTURE

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 67 | `pivot_high_flag` | INTEGER | Pivot High Flag | Binary flag: 1 if current candle is a local high (peak detection) | NULLABLE |
| 68 | `pivot_low_flag` | INTEGER | Pivot Low Flag | Binary flag: 1 if current candle is a local low (trough detection) | NULLABLE |
| 69 | `dist_to_pivot_high` | FLOAT | Distance to Last Pivot High | Price distance to most recent pivot high: (close - pivot_high) / close * 100 (%) | NULLABLE |
| 70 | `dist_to_pivot_low` | FLOAT | Distance to Last Pivot Low | Price distance to most recent pivot low: (close - pivot_low) / close * 100 (%) | NULLABLE |

---

## 14. ADVANCED ML FEATURES - REGIME DETECTION

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 71 | `trend_regime` | INTEGER | Trend Regime Classification | Trend classification: -1 (downtrend), 0 (sideways), 1 (uptrend) | NULLABLE |
| 72 | `vol_regime` | INTEGER | Volatility Regime Classification | Volatility classification: 0 (low vol), 1 (normal vol), 2 (high vol) | NULLABLE |
| 73 | `regime_confidence` | FLOAT | Regime Classification Confidence | Confidence score for regime classification (0.0-1.0) | NULLABLE |

---

## 15. ASSET METADATA

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 74 | `name` | STRING | Company/Asset Full Name | Full legal or common name (e.g., "Apple Inc.", "Tesla Inc.") | NULLABLE |
| 75 | `sector` | STRING | Economic Sector | GICS sector classification (e.g., Technology, Healthcare, Financials) | NULLABLE |
| 76 | `industry` | STRING | Industry Classification | GICS industry sub-classification (e.g., Software, Semiconductors) | NULLABLE |
| 77 | `asset_type` | STRING | Asset Type | Type of asset: "stock", "etf", "crypto", "forex", "commodity" | NULLABLE |
| 78 | `exchange` | STRING | Exchange Name | Exchange name (e.g., "NASDAQ", "NYSE", "London Stock Exchange") | NULLABLE |
| 79 | `mic_code` | STRING | Market Identifier Code | ISO 10383 MIC code (e.g., "XNAS" for NASDAQ, "XNYS" for NYSE) | NULLABLE |
| 80 | `country` | STRING | Country Code | ISO 3166-1 alpha-2 country code (e.g., "US", "GB", "JP") | NULLABLE |
| 81 | `currency` | STRING | Trading Currency | ISO 4217 currency code (e.g., "USD", "EUR", "GBP") | NULLABLE |
| 82 | `type` | STRING | Security Type | Security classification (e.g., "Common Stock", "Preferred Stock", "ADR") | NULLABLE |

---

## 16. SYSTEM METADATA

| S# | Field Name | Type | Full Name | Description | Mode |
|----|------------|------|-----------|-------------|------|
| 83 | `data_source` | STRING | Data Source Provider | API provider name (e.g., "TwelveData", "Alpha Vantage", "Finnhub") | NULLABLE |
| 84 | `created_at` | TIMESTAMP | Record Creation Timestamp | Timestamp when record was first inserted into BigQuery (system time) | NULLABLE |
| 85 | `updated_at` | TIMESTAMP | Record Update Timestamp | Timestamp when record was last updated in BigQuery (system time) | NULLABLE |

---

# FIELD ORDER RECOMMENDATIONS

## ✅ Current Order is EXCELLENT

Your field sequence follows best practices:

### 1. **Core Data First** (S# 1-16)
- Identifiers, timestamps, OHLCV, basic statistics
- **Why:** Essential for querying, partitioning, and clustering

### 2. **Technical Indicators Grouped** (S# 17-49)
- Momentum → Moving Averages → Trend/Volatility → Volume
- **Why:** Logical grouping makes queries more intuitive

### 3. **Advanced/ML Features** (S# 50-73)
- Returns, relative positions, indicator dynamics, market structure, regimes
- **Why:** Separates raw indicators from derived ML features

### 4. **Metadata Last** (S# 74-85)
- Asset info, system metadata
- **Why:** Queried less frequently, better at the end

### ⚠️ ONLY MINOR ADJUSTMENT NEEDED:

**Move `timestamp` (S# 3) to AFTER system metadata:**
- **Reason:** You have `datetime` (TIMESTAMP) as primary time field
- `timestamp` (INTEGER unix time) is redundant and should be optional/derived
- **New position:** S# 83 (before `data_source`)

---

# ISSUES FIXED IN THIS SCHEMA

## ✅ Duplicates Removed (5 fields):
1. ~~`week_52_high`~~ (was duplicated at original S# 13)
2. ~~`momentum`~~ (removed duplicate at original S# 37)
3. ~~`williams_r`~~ (removed duplicate at original S# 38)
4. ~~`ema_50`~~ (removed duplicate at original S# 39)
5. ~~`obv`~~ (removed duplicate at original S# 42)

## ✅ Field Names Fixed:
1. `high-low` → `high_low` (hyphen to underscore)
2. `pct_high-low` → `pct_high_low` (hyphen to underscore)

## ✅ Serial Numbers Fixed:
- Corrected duplicate S# 13 → now S# 13 (pct_high_low), S# 14 (week_52_low), S# 15 (week_52_high)

---

# FINAL FIELD COUNT

| Original | After Deduplication |
|----------|---------------------|
| 89 fields | **85 fields** |
| 5 duplicates removed | |
| 2 field names fixed | |

---

# BIGQUERY TABLE CREATION SQL

```sql
CREATE OR REPLACE TABLE `aialgotradehits.trading_data.stocks_master` (
  -- CORE IDENTIFIERS & TIMESTAMPS
  datetime TIMESTAMP NOT NULL,
  symbol STRING NOT NULL,

  -- OHLCV PRICE DATA
  open FLOAT64,
  high FLOAT64,
  low FLOAT64,
  close FLOAT64,
  previous_close FLOAT64,
  volume INT64,

  -- PRICE CHANGE STATISTICS
  average_volume INT64,
  change FLOAT64,
  percent_change FLOAT64,
  high_low FLOAT64,
  pct_high_low FLOAT64,
  week_52_high FLOAT64,
  week_52_low FLOAT64,

  -- TECHNICAL INDICATORS - MOMENTUM
  rsi FLOAT64,
  macd FLOAT64,
  macd_signal FLOAT64,
  macd_histogram FLOAT64,
  stoch_k FLOAT64,
  stoch_d FLOAT64,
  cci FLOAT64,
  williams_r FLOAT64,
  momentum FLOAT64,

  -- TECHNICAL INDICATORS - MOVING AVERAGES
  sma_20 FLOAT64,
  sma_50 FLOAT64,
  sma_200 FLOAT64,
  ema_12 FLOAT64,
  ema_20 FLOAT64,
  ema_26 FLOAT64,
  ema_50 FLOAT64,
  ema_200 FLOAT64,
  kama FLOAT64,

  -- TECHNICAL INDICATORS - TREND & VOLATILITY
  bollinger_upper FLOAT64,
  bollinger_middle FLOAT64,
  bollinger_lower FLOAT64,
  bb_width FLOAT64,
  adx FLOAT64,
  plus_di FLOAT64,
  minus_di FLOAT64,
  atr FLOAT64,
  trix FLOAT64,
  roc FLOAT64,

  -- TECHNICAL INDICATORS - VOLUME
  obv FLOAT64,
  pvo FLOAT64,
  ppo FLOAT64,

  -- TECHNICAL INDICATORS - ADVANCED OSCILLATORS
  ultimate_osc FLOAT64,
  awesome_osc FLOAT64,

  -- ADVANCED ML FEATURES - RETURNS
  log_return FLOAT64,
  return_2w FLOAT64,
  return_4w FLOAT64,

  -- ADVANCED ML FEATURES - RELATIVE POSITIONS
  close_vs_sma20_pct FLOAT64,
  close_vs_sma50_pct FLOAT64,
  close_vs_sma200_pct FLOAT64,

  -- ADVANCED ML FEATURES - INDICATOR DYNAMICS
  rsi_slope FLOAT64,
  rsi_zscore FLOAT64,
  rsi_overbought INT64,
  rsi_oversold INT64,
  macd_cross INT64,
  ema20_slope FLOAT64,
  ema50_slope FLOAT64,
  atr_zscore FLOAT64,
  atr_slope FLOAT64,
  volume_zscore FLOAT64,

  -- ADVANCED ML FEATURES - VOLUME & PRICE RATIOS
  volume_ratio FLOAT64,

  -- ADVANCED ML FEATURES - MARKET STRUCTURE
  pivot_high_flag INT64,
  pivot_low_flag INT64,
  dist_to_pivot_high FLOAT64,
  dist_to_pivot_low FLOAT64,

  -- ADVANCED ML FEATURES - REGIME DETECTION
  trend_regime INT64,
  vol_regime INT64,
  regime_confidence FLOAT64,

  -- ASSET METADATA
  name STRING,
  sector STRING,
  industry STRING,
  asset_type STRING,
  exchange STRING,
  mic_code STRING,
  country STRING,
  currency STRING,
  type STRING,

  -- SYSTEM METADATA
  timestamp INT64,
  data_source STRING,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
PARTITION BY DATE(datetime)
CLUSTER BY symbol, sector, exchange
OPTIONS(
  description="Master stocks table with OHLCV, 40+ technical indicators, and ML features",
  require_partition_filter=true
);
```

---

# PARTITIONING & CLUSTERING RECOMMENDATIONS

## Partitioning Strategy:
✅ **`PARTITION BY DATE(datetime)`**
- Partitions by date for efficient time-range queries
- Reduces scan costs (only scans relevant dates)
- Required for large tables (1M+ rows)

## Clustering Strategy:
✅ **`CLUSTER BY symbol, sector, exchange`**
- **symbol**: Most common filter (queries specific stocks)
- **sector**: Sector-based analysis queries
- **exchange**: Regional analysis (NASDAQ vs NYSE)

**Benefits:**
- 5-10× faster queries on clustered columns
- Automatic sorting within partitions
- Lower query costs

---

# NEXT STEPS

1. **Review this schema** and confirm field order
2. **Test with sample data** from 1-2 stocks
3. **Create BigQuery table** using SQL above
4. **Update data pipelines** to match new schema
5. **Migrate existing data** if needed

---

**Schema Complete ✅**

**Total Fields:** 85 (deduplicated from 89)
**Duplicates Removed:** 5
**Field Names Fixed:** 2
**Order:** Optimal (no changes recommended)
