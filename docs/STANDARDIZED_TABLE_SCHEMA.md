# Standardized BigQuery Table Schema
## Field Ordering for All Asset Tables (Stocks & Crypto)

**Applies to:**
- `stocks_daily_clean`
- `stocks_hourly_clean`
- `stocks_5min_clean`
- `crypto_daily_clean`

**Version**: 2.0 (Enhanced with Institutional Indicators)
**Last Updated**: December 9, 2025
**Total Fields**: 80

---

## Canonical Field Order

### 1-16: BASE FIELDS (Identity, Price, Volume, Metadata)

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 1 | `datetime` | TIMESTAMP | Time | Trading timestamp (partitioning key) |
| 2 | `symbol` | STRING | Identity | Ticker symbol (clustering key 1) |
| 3 | `name` | STRING | Identity | Asset/company name |
| 4 | `exchange` | STRING | Identity | Exchange name (clustering key 3) |
| 5 | `mic_code` | STRING | Identity | Market Identifier Code |
| 6 | `sector` | STRING | Identity | Business sector (clustering key 2) |
| 7 | `currency` | STRING | Identity | Trading currency |
| 8 | `open` | FLOAT | Price | Opening price |
| 9 | `high` | FLOAT | Price | Highest price |
| 10 | `low` | FLOAT | Price | Lowest price |
| 11 | `close` | FLOAT | Price | Closing price |
| 12 | `volume` | INT64 | Volume | Trading volume |
| 13 | `average_volume` | FLOAT | Volume | Average volume (recent period) |
| 14 | `percent_change` | FLOAT | Derived | Daily percent change |
| 15 | `created_at` | TIMESTAMP | Metadata | Row creation timestamp |
| 16 | `updated_at` | TIMESTAMP | Metadata | Last update timestamp |

---

### 17-25: MOMENTUM INDICATORS

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 17 | `rsi` | FLOAT | Momentum | RSI(14) - Relative Strength Index |
| 18 | `macd` | FLOAT | Momentum | MACD Line (12, 26) |
| 19 | `macd_signal` | FLOAT | Momentum | MACD Signal Line (9) |
| 20 | `macd_histogram` | FLOAT | Momentum | MACD Histogram |
| 21 | `stoch_k` | FLOAT | Momentum | Stochastic %K (14, 3) |
| 22 | `stoch_d` | FLOAT | Momentum | Stochastic %D (3) |
| 23 | `cci` | FLOAT | Momentum | CCI(20) - Commodity Channel Index |
| 24 | `williams_r` | FLOAT | Momentum | Williams %R (14) |
| 25 | `momentum` | FLOAT | Momentum | Momentum(10) |

---

### 26-35: MOVING AVERAGES

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 26 | `sma_20` | FLOAT | Moving Avg | 20-day Simple Moving Average |
| 27 | `sma_50` | FLOAT | Moving Avg | 50-day Simple Moving Average |
| 28 | `sma_200` | FLOAT | Moving Avg | 200-day Simple Moving Average |
| 29 | `ema_12` | FLOAT | Moving Avg | 12-day Exponential Moving Average |
| 30 | `ema_20` | FLOAT | Moving Avg | 20-day Exponential Moving Average |
| 31 | `ema_26` | FLOAT | Moving Avg | 26-day Exponential Moving Average |
| 32 | `ema_50` | FLOAT | Moving Avg | 50-day Exponential Moving Average |
| 33 | `ema_200` | FLOAT | Moving Avg | 200-day Exponential Moving Average |
| 34 | `kama` | FLOAT | Moving Avg | KAMA(10) - Kaufman Adaptive MA |
| 35 | `vwap_daily` | FLOAT | Moving Avg | Daily VWAP ⭐ NEW |

---

### 36-39: BOLLINGER BANDS

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 36 | `bollinger_upper` | FLOAT | Volatility | Upper Bollinger Band (20, 2σ) |
| 37 | `bollinger_middle` | FLOAT | Volatility | Middle Bollinger Band (SMA 20) |
| 38 | `bollinger_lower` | FLOAT | Volatility | Lower Bollinger Band (20, 2σ) |
| 39 | `bb_width` | FLOAT | Volatility | Bollinger Band Width |

---

### 40-42: ADX TREND INDICATORS

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 40 | `adx` | FLOAT | Trend | ADX(14) - Average Directional Index |
| 41 | `plus_di` | FLOAT | Trend | Plus Directional Indicator (+DI) |
| 42 | `minus_di` | FLOAT | Trend | Minus Directional Indicator (-DI) |

---

### 43-45: OTHER VOLATILITY & TREND

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 43 | `atr` | FLOAT | Volatility | ATR(14) - Average True Range |
| 44 | `trix` | FLOAT | Trend | TRIX(15) - Triple EMA |
| 45 | `roc` | FLOAT | Momentum | ROC(10) - Rate of Change |

---

### 46-48: VOLUME INDICATORS

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 46 | `obv` | FLOAT | Volume | On-Balance Volume |
| 47 | `pvo` | FLOAT | Volume | PVO(12, 26) - Percentage Volume Oscillator |
| 48 | `ppo` | FLOAT | Volume | PPO(12, 26) - Percentage Price Oscillator |

---

### 49-50: ADVANCED OSCILLATORS

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 49 | `ultimate_osc` | FLOAT | Oscillator | Ultimate Oscillator (7, 14, 28) |
| 50 | `awesome_osc` | FLOAT | Oscillator | Awesome Oscillator |

---

### 51-61: INSTITUTIONAL INDICATORS ⭐ NEW

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 51 | `mfi` | FLOAT | Institutional | MFI(14) - Money Flow Index |
| 52 | `cmf` | FLOAT | Institutional | CMF(20) - Chaikin Money Flow |
| 53 | `ichimoku_tenkan` | FLOAT | Institutional | Ichimoku Tenkan-sen (9) |
| 54 | `ichimoku_kijun` | FLOAT | Institutional | Ichimoku Kijun-sen (26) |
| 55 | `ichimoku_senkou_a` | FLOAT | Institutional | Ichimoku Senkou Span A |
| 56 | `ichimoku_senkou_b` | FLOAT | Institutional | Ichimoku Senkou Span B |
| 57 | `ichimoku_chikou` | FLOAT | Institutional | Ichimoku Chikou Span |
| 58 | `vwap_weekly` | FLOAT | Institutional | Weekly VWAP (5-day rolling) |
| 59 | `volume_profile_poc` | FLOAT | Institutional | Volume Profile - Point of Control |
| 60 | `volume_profile_vah` | FLOAT | Institutional | Volume Profile - Value Area High |
| 61 | `volume_profile_val` | FLOAT | Institutional | Volume Profile - Value Area Low |

---

### 62-64: ML FEATURES - RETURNS

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 62 | `log_return` | FLOAT | ML Feature | Logarithmic return |
| 63 | `return_2w` | FLOAT | ML Feature | 2-week forward return % |
| 64 | `return_4w` | FLOAT | ML Feature | 4-week forward return % |

---

### 65-67: ML FEATURES - RELATIVE POSITIONS

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 65 | `close_vs_sma20_pct` | FLOAT | ML Feature | Distance from SMA(20) % |
| 66 | `close_vs_sma50_pct` | FLOAT | ML Feature | Distance from SMA(50) % |
| 67 | `close_vs_sma200_pct` | FLOAT | ML Feature | Distance from SMA(200) % |

---

### 68-78: ML FEATURES - INDICATOR DYNAMICS

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 68 | `rsi_slope` | FLOAT | ML Feature | 5-day RSI change |
| 69 | `rsi_zscore` | FLOAT | ML Feature | RSI Z-score (20-day) |
| 70 | `rsi_overbought` | INT64 | ML Feature | RSI overbought flag (>70) |
| 71 | `rsi_oversold` | INT64 | ML Feature | RSI oversold flag (<30) |
| 72 | `macd_cross` | INT64 | ML Feature | MACD crossover signal |
| 73 | `ema20_slope` | FLOAT | ML Feature | 5-day EMA(20) change |
| 74 | `ema50_slope` | FLOAT | ML Feature | 5-day EMA(50) change |
| 75 | `atr_zscore` | FLOAT | ML Feature | ATR Z-score (20-day) |
| 76 | `atr_slope` | FLOAT | ML Feature | 5-day ATR change |
| 77 | `volume_zscore` | FLOAT | ML Feature | Volume Z-score (20-day) |
| 78 | `volume_ratio` | FLOAT | ML Feature | Volume / Average Volume |

---

### 79-82: ML FEATURES - MARKET STRUCTURE

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 79 | `pivot_high_flag` | INT64 | ML Feature | Pivot high detected flag |
| 80 | `pivot_low_flag` | INT64 | ML Feature | Pivot low detected flag |
| 81 | `dist_to_pivot_high` | FLOAT | ML Feature | Distance to last pivot high |
| 82 | `dist_to_pivot_low` | FLOAT | ML Feature | Distance to last pivot low |

---

### 83-85: ML FEATURES - REGIME DETECTION

| # | Field Name | Type | Category | Description |
|---|------------|------|----------|-------------|
| 83 | `trend_regime` | INT64 | ML Feature | Trend direction (1/-1/0) |
| 84 | `regime_confidence` | FLOAT | ML Feature | Trend strength measure |
| 85 | `vol_regime` | INT64 | ML Feature | Volatility state (high=1/low=0) |

---

## Field Count by Category

| Category | Count | Field Range |
|----------|-------|-------------|
| Base Fields (Identity, Price, Metadata) | 16 | 1-16 |
| Momentum Indicators | 9 | 17-25 |
| Moving Averages (incl VWAP) | 10 | 26-35 |
| Bollinger Bands | 4 | 36-39 |
| ADX Trend | 3 | 40-42 |
| Other Volatility/Trend | 3 | 43-45 |
| Volume Indicators | 3 | 46-48 |
| Oscillators | 2 | 49-50 |
| **Institutional Indicators** ⭐ | **11** | **51-61** |
| ML Features - Returns | 3 | 62-64 |
| ML Features - Relative Positions | 3 | 65-67 |
| ML Features - Indicator Dynamics | 11 | 68-78 |
| ML Features - Market Structure | 4 | 79-82 |
| ML Features - Regime Detection | 3 | 83-85 |
| **TOTAL** | **85** | **1-85** |

---

## BigQuery Schema Definition

```sql
CREATE TABLE `aialgotradehits.crypto_trading_data.{TABLE_NAME}`
(
  -- BASE FIELDS (1-16)
  datetime TIMESTAMP OPTIONS(description="Trading timestamp (partitioning key)"),
  symbol STRING OPTIONS(description="Ticker symbol (clustering key 1)"),
  name STRING OPTIONS(description="Asset/company name"),
  exchange STRING OPTIONS(description="Exchange name (clustering key 3)"),
  mic_code STRING OPTIONS(description="Market Identifier Code"),
  sector STRING OPTIONS(description="Business sector (clustering key 2)"),
  currency STRING OPTIONS(description="Trading currency"),
  open FLOAT64 OPTIONS(description="Opening price"),
  high FLOAT64 OPTIONS(description="Highest price"),
  low FLOAT64 OPTIONS(description="Lowest price"),
  close FLOAT64 OPTIONS(description="Closing price"),
  volume INT64 OPTIONS(description="Trading volume"),
  average_volume FLOAT64 OPTIONS(description="Average volume"),
  percent_change FLOAT64 OPTIONS(description="Daily percent change"),
  created_at TIMESTAMP OPTIONS(description="Row creation timestamp"),
  updated_at TIMESTAMP OPTIONS(description="Last update timestamp"),

  -- MOMENTUM INDICATORS (17-25)
  rsi FLOAT64 OPTIONS(description="RSI(14)"),
  macd FLOAT64 OPTIONS(description="MACD Line (12,26)"),
  macd_signal FLOAT64 OPTIONS(description="MACD Signal (9)"),
  macd_histogram FLOAT64 OPTIONS(description="MACD Histogram"),
  stoch_k FLOAT64 OPTIONS(description="Stochastic %K (14,3)"),
  stoch_d FLOAT64 OPTIONS(description="Stochastic %D (3)"),
  cci FLOAT64 OPTIONS(description="CCI(20)"),
  williams_r FLOAT64 OPTIONS(description="Williams %R (14)"),
  momentum FLOAT64 OPTIONS(description="Momentum(10)"),

  -- MOVING AVERAGES (26-35)
  sma_20 FLOAT64 OPTIONS(description="SMA(20)"),
  sma_50 FLOAT64 OPTIONS(description="SMA(50)"),
  sma_200 FLOAT64 OPTIONS(description="SMA(200)"),
  ema_12 FLOAT64 OPTIONS(description="EMA(12)"),
  ema_20 FLOAT64 OPTIONS(description="EMA(20)"),
  ema_26 FLOAT64 OPTIONS(description="EMA(26)"),
  ema_50 FLOAT64 OPTIONS(description="EMA(50)"),
  ema_200 FLOAT64 OPTIONS(description="EMA(200)"),
  kama FLOAT64 OPTIONS(description="KAMA(10)"),
  vwap_daily FLOAT64 OPTIONS(description="Daily VWAP"),

  -- BOLLINGER BANDS (36-39)
  bollinger_upper FLOAT64 OPTIONS(description="Upper Bollinger Band (20,2σ)"),
  bollinger_middle FLOAT64 OPTIONS(description="Middle Bollinger Band"),
  bollinger_lower FLOAT64 OPTIONS(description="Lower Bollinger Band (20,2σ)"),
  bb_width FLOAT64 OPTIONS(description="Bollinger Band Width"),

  -- ADX TREND (40-42)
  adx FLOAT64 OPTIONS(description="ADX(14)"),
  plus_di FLOAT64 OPTIONS(description="+DI"),
  minus_di FLOAT64 OPTIONS(description="-DI"),

  -- OTHER VOLATILITY/TREND (43-45)
  atr FLOAT64 OPTIONS(description="ATR(14)"),
  trix FLOAT64 OPTIONS(description="TRIX(15)"),
  roc FLOAT64 OPTIONS(description="ROC(10)"),

  -- VOLUME INDICATORS (46-48)
  obv FLOAT64 OPTIONS(description="On-Balance Volume"),
  pvo FLOAT64 OPTIONS(description="PVO(12,26)"),
  ppo FLOAT64 OPTIONS(description="PPO(12,26)"),

  -- OSCILLATORS (49-50)
  ultimate_osc FLOAT64 OPTIONS(description="Ultimate Oscillator (7,14,28)"),
  awesome_osc FLOAT64 OPTIONS(description="Awesome Oscillator"),

  -- INSTITUTIONAL INDICATORS (51-61) ⭐ NEW
  mfi FLOAT64 OPTIONS(description="Money Flow Index(14)"),
  cmf FLOAT64 OPTIONS(description="Chaikin Money Flow(20)"),
  ichimoku_tenkan FLOAT64 OPTIONS(description="Ichimoku Tenkan-sen(9)"),
  ichimoku_kijun FLOAT64 OPTIONS(description="Ichimoku Kijun-sen(26)"),
  ichimoku_senkou_a FLOAT64 OPTIONS(description="Ichimoku Senkou Span A"),
  ichimoku_senkou_b FLOAT64 OPTIONS(description="Ichimoku Senkou Span B"),
  ichimoku_chikou FLOAT64 OPTIONS(description="Ichimoku Chikou Span"),
  vwap_weekly FLOAT64 OPTIONS(description="Weekly VWAP (5-day)"),
  volume_profile_poc FLOAT64 OPTIONS(description="Volume Profile POC"),
  volume_profile_vah FLOAT64 OPTIONS(description="Volume Profile VAH"),
  volume_profile_val FLOAT64 OPTIONS(description="Volume Profile VAL"),

  -- ML FEATURES - RETURNS (62-64)
  log_return FLOAT64 OPTIONS(description="Logarithmic return"),
  return_2w FLOAT64 OPTIONS(description="2-week forward return %"),
  return_4w FLOAT64 OPTIONS(description="4-week forward return %"),

  -- ML FEATURES - RELATIVE POSITIONS (65-67)
  close_vs_sma20_pct FLOAT64 OPTIONS(description="Distance from SMA(20) %"),
  close_vs_sma50_pct FLOAT64 OPTIONS(description="Distance from SMA(50) %"),
  close_vs_sma200_pct FLOAT64 OPTIONS(description="Distance from SMA(200) %"),

  -- ML FEATURES - INDICATOR DYNAMICS (68-78)
  rsi_slope FLOAT64 OPTIONS(description="5-day RSI change"),
  rsi_zscore FLOAT64 OPTIONS(description="RSI Z-score (20-day)"),
  rsi_overbought INT64 OPTIONS(description="RSI >70 flag"),
  rsi_oversold INT64 OPTIONS(description="RSI <30 flag"),
  macd_cross INT64 OPTIONS(description="MACD crossover signal"),
  ema20_slope FLOAT64 OPTIONS(description="5-day EMA(20) change"),
  ema50_slope FLOAT64 OPTIONS(description="5-day EMA(50) change"),
  atr_zscore FLOAT64 OPTIONS(description="ATR Z-score (20-day)"),
  atr_slope FLOAT64 OPTIONS(description="5-day ATR change"),
  volume_zscore FLOAT64 OPTIONS(description="Volume Z-score (20-day)"),
  volume_ratio FLOAT64 OPTIONS(description="Volume / Avg Volume"),

  -- ML FEATURES - MARKET STRUCTURE (79-82)
  pivot_high_flag INT64 OPTIONS(description="Pivot high detected"),
  pivot_low_flag INT64 OPTIONS(description="Pivot low detected"),
  dist_to_pivot_high FLOAT64 OPTIONS(description="Distance to last pivot high"),
  dist_to_pivot_low FLOAT64 OPTIONS(description="Distance to last pivot low"),

  -- ML FEATURES - REGIME DETECTION (83-85)
  trend_regime INT64 OPTIONS(description="Trend direction (1/-1/0)"),
  regime_confidence FLOAT64 OPTIONS(description="Trend strength"),
  vol_regime INT64 OPTIONS(description="Volatility state (1/0)")
)
PARTITION BY DATE(datetime)
CLUSTER BY symbol, sector, exchange
OPTIONS(
  description="Multi-timeframe asset data with 69 technical indicators",
  labels=[("version", "2_0"), ("enhanced", "institutional_indicators")]
);
```

---

## Python Field Order (for DataFrame operations)

```python
# Canonical field order for ALL asset tables
CANONICAL_FIELD_ORDER = [
    # BASE FIELDS (1-16)
    'datetime', 'symbol', 'name', 'exchange', 'mic_code', 'sector', 'currency',
    'open', 'high', 'low', 'close', 'volume', 'average_volume', 'percent_change',
    'created_at', 'updated_at',

    # MOMENTUM INDICATORS (17-25)
    'rsi', 'macd', 'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d',
    'cci', 'williams_r', 'momentum',

    # MOVING AVERAGES (26-35)
    'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_20', 'ema_26', 'ema_50', 'ema_200',
    'kama', 'vwap_daily',

    # BOLLINGER BANDS (36-39)
    'bollinger_upper', 'bollinger_middle', 'bollinger_lower', 'bb_width',

    # ADX TREND (40-42)
    'adx', 'plus_di', 'minus_di',

    # OTHER VOLATILITY/TREND (43-45)
    'atr', 'trix', 'roc',

    # VOLUME INDICATORS (46-48)
    'obv', 'pvo', 'ppo',

    # OSCILLATORS (49-50)
    'ultimate_osc', 'awesome_osc',

    # INSTITUTIONAL INDICATORS (51-61) ⭐ NEW
    'mfi', 'cmf',
    'ichimoku_tenkan', 'ichimoku_kijun', 'ichimoku_senkou_a', 'ichimoku_senkou_b', 'ichimoku_chikou',
    'vwap_weekly', 'volume_profile_poc', 'volume_profile_vah', 'volume_profile_val',

    # ML FEATURES - RETURNS (62-64)
    'log_return', 'return_2w', 'return_4w',

    # ML FEATURES - RELATIVE POSITIONS (65-67)
    'close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct',

    # ML FEATURES - INDICATOR DYNAMICS (68-78)
    'rsi_slope', 'rsi_zscore', 'rsi_overbought', 'rsi_oversold', 'macd_cross',
    'ema20_slope', 'ema50_slope', 'atr_zscore', 'atr_slope', 'volume_zscore', 'volume_ratio',

    # ML FEATURES - MARKET STRUCTURE (79-82)
    'pivot_high_flag', 'pivot_low_flag', 'dist_to_pivot_high', 'dist_to_pivot_low',

    # ML FEATURES - REGIME DETECTION (83-85)
    'trend_regime', 'regime_confidence', 'vol_regime'
]

# Usage in scripts:
# df = df[CANONICAL_FIELD_ORDER]  # Reorder before upload
```

---

## Cross-Table Consistency

### stocks_daily_clean
- **Timeframe**: Daily
- **Partitioning**: MONTH(datetime)
- **All 85 fields** in canonical order

### stocks_hourly_clean
- **Timeframe**: Hourly
- **Partitioning**: DAY(datetime)
- **All 85 fields** in canonical order (same as daily)

### stocks_5min_clean
- **Timeframe**: 5-minute
- **Partitioning**: DAY(datetime)
- **All 85 fields** in canonical order (same as daily)

### crypto_daily_clean
- **Timeframe**: Daily
- **Partitioning**: MONTH(datetime)
- **Filter**: USD trading pairs only
- **All 85 fields** in canonical order (same as stocks)

---

## Version Control

| Version | Date | Changes | Fields Added |
|---------|------|---------|--------------|
| 1.0 | Dec 7, 2025 | Initial schema | 74 fields |
| 2.0 | Dec 9, 2025 | Added institutional indicators | +11 fields (51-61) |
|  |  | - MFI, CMF | 51-52 |
|  |  | - Ichimoku Cloud (5 components) | 53-57 |
|  |  | - VWAP Weekly | 58 |
|  |  | - Volume Profile (POC, VAH, VAL) | 59-61 |
|  |  | **Total: 85 fields** | |

---

## Compliance Notes

✅ **Field Order**: Strictly maintained across all tables
✅ **Field Numbering**: 1-85 canonical sequence
✅ **Data Types**: Consistent across all asset classes
✅ **Naming Convention**: Snake_case, descriptive
✅ **Null Handling**: All indicator fields nullable
✅ **Partitioning**: Optimized by timeframe granularity
✅ **Clustering**: Optimized for query patterns (symbol, sector, exchange)

---

**END OF STANDARDIZED SCHEMA**
