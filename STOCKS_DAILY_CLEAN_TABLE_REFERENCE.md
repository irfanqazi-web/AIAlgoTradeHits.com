# stocks_daily_clean Table Reference
## Complete Field Documentation with Calculations

**Project**: AIAlgoTradeHits
**Dataset**: crypto_trading_data
**Table**: stocks_daily_clean
**Last Updated**: December 9, 2025
**Total Fields**: 80+ (11 base fields + 69 indicator fields)

---

## Table Structure

### Partitioning & Clustering
- **Partitioning**: By `datetime` (MONTH granularity)
- **Clustering**: By `symbol`, `sector`, `exchange`
- **Purpose**: Optimize query performance for time-series and symbol-based queries

---

## Field Definitions (Sequenced by Category)

### 1. BASE FIELDS (11 fields)

#### 1.1 Identification Fields
| Field | Type | Description |
|-------|------|-------------|
| `symbol` | STRING | Stock ticker symbol (e.g., 'AAPL', 'MSFT') |
| `name` | STRING | Company name |
| `exchange` | STRING | Exchange name (e.g., 'NASDAQ', 'NYSE') |
| `mic_code` | STRING | Market Identifier Code |
| `sector` | STRING | Business sector (e.g., 'Technology', 'Healthcare') |
| `currency` | STRING | Trading currency (typically 'USD') |

#### 1.2 Time & Price Fields
| Field | Type | Description |
|-------|------|-------------|
| `datetime` | TIMESTAMP | Trading date (daily resolution) |
| `open` | FLOAT | Opening price |
| `high` | FLOAT | Highest price during the day |
| `low` | FLOAT | Lowest price during the day |
| `close` | FLOAT | Closing price |
| `volume` | INT64 | Total trading volume |
| `average_volume` | FLOAT | Average volume over recent period |
| `percent_change` | FLOAT | Daily percent change: `((close - open) / open) * 100` |

#### 1.3 Metadata Fields
| Field | Type | Description |
|-------|------|-------------|
| `created_at` | TIMESTAMP | Row creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

---

### 2. MOMENTUM INDICATORS (9 fields)

#### 2.1 RSI (Relative Strength Index)
```
Formula: RSI = 100 - (100 / (1 + RS))
         where RS = Average Gain / Average Loss over period
Period: 14 days
Range: 0-100
Interpretation: >70 = Overbought, <30 = Oversold
```
| Field | Type | Description |
|-------|------|-------------|
| `rsi` | FLOAT | RSI(14) value |

#### 2.2 MACD (Moving Average Convergence Divergence)
```
Formula: MACD Line = EMA(12) - EMA(26)
         Signal Line = EMA(9) of MACD Line
         Histogram = MACD Line - Signal Line
Interpretation: Bullish when MACD > Signal, Bearish when MACD < Signal
```
| Field | Type | Description |
|-------|------|-------------|
| `macd` | FLOAT | MACD line (12, 26) |
| `macd_signal` | FLOAT | Signal line (9-day EMA of MACD) |
| `macd_histogram` | FLOAT | Histogram (MACD - Signal) |

#### 2.3 Stochastic Oscillator
```
Formula: %K = ((Current Close - Lowest Low) / (Highest High - Lowest Low)) * 100
         %D = 3-day SMA of %K
Period: 14 days for %K
Range: 0-100
Interpretation: >80 = Overbought, <20 = Oversold
```
| Field | Type | Description |
|-------|------|-------------|
| `stoch_k` | FLOAT | Stochastic %K (14, 3) |
| `stoch_d` | FLOAT | Stochastic %D (3-day SMA of %K) |

#### 2.4 CCI (Commodity Channel Index)
```
Formula: CCI = (Typical Price - SMA) / (0.015 × Mean Deviation)
         where Typical Price = (High + Low + Close) / 3
Period: 20 days
Range: Typically -100 to +100
Interpretation: >100 = Overbought, <-100 = Oversold
```
| Field | Type | Description |
|-------|------|-------------|
| `cci` | FLOAT | CCI(20) value |

#### 2.5 Williams %R
```
Formula: %R = ((Highest High - Close) / (Highest High - Lowest Low)) * -100
Period: 14 days
Range: -100 to 0
Interpretation: <-80 = Oversold, >-20 = Overbought
```
| Field | Type | Description |
|-------|------|-------------|
| `williams_r` | FLOAT | Williams %R (14) |

#### 2.6 Momentum
```
Formula: Momentum = Close(today) - Close(n periods ago)
Period: 10 days
Interpretation: Positive = Uptrend, Negative = Downtrend
```
| Field | Type | Description |
|-------|------|-------------|
| `momentum` | FLOAT | Momentum(10) value |

---

### 3. MOVING AVERAGES (10 fields)

#### 3.1 Simple Moving Averages (SMA)
```
Formula: SMA = Sum of Close prices over n periods / n
Purpose: Identify trend direction and support/resistance levels
```
| Field | Type | Description |
|-------|------|-------------|
| `sma_20` | FLOAT | 20-day Simple Moving Average |
| `sma_50` | FLOAT | 50-day Simple Moving Average |
| `sma_200` | FLOAT | 200-day Simple Moving Average |

#### 3.2 Exponential Moving Averages (EMA)
```
Formula: EMA = (Close × Multiplier) + (Previous EMA × (1 - Multiplier))
         where Multiplier = 2 / (Period + 1)
Purpose: More weight to recent prices, faster response than SMA
```
| Field | Type | Description |
|-------|------|-------------|
| `ema_12` | FLOAT | 12-day Exponential Moving Average |
| `ema_20` | FLOAT | 20-day Exponential Moving Average |
| `ema_26` | FLOAT | 26-day Exponential Moving Average |
| `ema_50` | FLOAT | 50-day Exponential Moving Average |
| `ema_200` | FLOAT | 200-day Exponential Moving Average |

#### 3.3 KAMA (Kaufman's Adaptive Moving Average)
```
Formula: KAMA = Previous KAMA + SC × (Price - Previous KAMA)
         where SC = (ER × (Fastest SC - Slowest SC) + Slowest SC)²
         ER = Efficiency Ratio = Net Change / Total Movement
Period: 10 days
Purpose: Adaptive MA that adjusts to market volatility
```
| Field | Type | Description |
|-------|------|-------------|
| `kama` | FLOAT | KAMA(10) value |

---

### 4. BOLLINGER BANDS (4 fields)

```
Formula: Middle Band = SMA(20)
         Upper Band = SMA(20) + (2 × Standard Deviation)
         Lower Band = SMA(20) - (2 × Standard Deviation)
         Width = (Upper Band - Lower Band) / Middle Band
Purpose: Measure volatility and identify overbought/oversold conditions
```
| Field | Type | Description |
|-------|------|-------------|
| `bollinger_upper` | FLOAT | Upper Bollinger Band (20, 2σ) |
| `bollinger_middle` | FLOAT | Middle Bollinger Band (SMA 20) |
| `bollinger_lower` | FLOAT | Lower Bollinger Band (20, 2σ) |
| `bb_width` | FLOAT | Bollinger Band Width (volatility measure) |

---

### 5. TREND INDICATORS - ADX (3 fields)

```
Formula: ADX = SMA of DX over 14 periods
         where DX = (|+DI - -DI| / |+DI + -DI|) × 100
         +DI = (Smoothed +DM / ATR) × 100
         -DI = (Smoothed -DM / ATR) × 100
Period: 14 days
Range: 0-100
Interpretation: >25 = Strong trend, <20 = Weak trend
```
| Field | Type | Description |
|-------|------|-------------|
| `adx` | FLOAT | Average Directional Index (14) |
| `plus_di` | FLOAT | Plus Directional Indicator (+DI) |
| `minus_di` | FLOAT | Minus Directional Indicator (-DI) |

---

### 6. VOLATILITY INDICATORS (2 fields)

#### 6.1 ATR (Average True Range)
```
Formula: True Range = Max of:
         - High - Low
         - |High - Previous Close|
         - |Low - Previous Close|
         ATR = 14-day EMA of True Range
Purpose: Measure market volatility
```
| Field | Type | Description |
|-------|------|-------------|
| `atr` | FLOAT | Average True Range (14) |

#### 6.2 TRIX (Triple Exponential Average)
```
Formula: TRIX = 1-day ROC of Triple EMA
         Triple EMA = EMA of EMA of EMA(15)
Period: 15 days
Purpose: Momentum indicator that filters out short-term noise
```
| Field | Type | Description |
|-------|------|-------------|
| `trix` | FLOAT | TRIX(15) value |

---

### 7. RATE OF CHANGE INDICATOR (1 field)

```
Formula: ROC = ((Close - Close(n periods ago)) / Close(n periods ago)) × 100
Period: 10 days
Purpose: Measure percentage price change over time
```
| Field | Type | Description |
|-------|------|-------------|
| `roc` | FLOAT | Rate of Change (10) |

---

### 8. VOLUME INDICATORS (3 fields)

#### 8.1 OBV (On-Balance Volume)
```
Formula: If Close > Previous Close: OBV = Previous OBV + Volume
         If Close < Previous Close: OBV = Previous OBV - Volume
         If Close = Previous Close: OBV = Previous OBV
Purpose: Relate volume to price changes
```
| Field | Type | Description |
|-------|------|-------------|
| `obv` | FLOAT | On-Balance Volume |

#### 8.2 PVO (Percentage Volume Oscillator)
```
Formula: PVO = ((EMA12(Volume) - EMA26(Volume)) / EMA26(Volume)) × 100
Purpose: Volume-based momentum indicator
```
| Field | Type | Description |
|-------|------|-------------|
| `pvo` | FLOAT | PVO (12, 26) |

#### 8.3 PPO (Percentage Price Oscillator)
```
Formula: PPO = ((EMA12 - EMA26) / EMA26) × 100
Purpose: Similar to MACD but in percentage terms
```
| Field | Type | Description |
|-------|------|-------------|
| `ppo` | FLOAT | PPO (12, 26) |

---

### 9. ADVANCED OSCILLATORS (2 fields)

#### 9.1 Ultimate Oscillator
```
Formula: UO = 100 × ((4 × Avg7) + (2 × Avg14) + Avg28) / (4 + 2 + 1)
         where Avg = BP / TR sum over period
         BP = Buying Pressure = Close - Min(Low, Previous Close)
         TR = True Range
Periods: 7, 14, 28 days
Range: 0-100
Purpose: Multi-timeframe momentum oscillator
```
| Field | Type | Description |
|-------|------|-------------|
| `ultimate_osc` | FLOAT | Ultimate Oscillator (7, 14, 28) |

#### 9.2 Awesome Oscillator
```
Formula: AO = SMA5(Median Price) - SMA34(Median Price)
         where Median Price = (High + Low) / 2
Purpose: Measure market momentum
```
| Field | Type | Description |
|-------|------|-------------|
| `awesome_osc` | FLOAT | Awesome Oscillator |

---

### 10. INSTITUTIONAL INDICATORS (11 fields) ⭐ NEW

#### 10.1 MFI (Money Flow Index)
```
Formula: MFI = 100 - (100 / (1 + Money Flow Ratio))
         Money Flow Ratio = Positive Money Flow / Negative Money Flow
         Typical Price = (High + Low + Close) / 3
         Raw Money Flow = Typical Price × Volume
Period: 14 days
Range: 0-100
Interpretation: >80 = Overbought, <20 = Oversold
Purpose: Volume-weighted RSI
```
| Field | Type | Description |
|-------|------|-------------|
| `mfi` | FLOAT | Money Flow Index (14) |

#### 10.2 CMF (Chaikin Money Flow)
```
Formula: CMF = Sum of Money Flow Volume (20) / Sum of Volume (20)
         Money Flow Multiplier = ((Close - Low) - (High - Close)) / (High - Low)
         Money Flow Volume = Money Flow Multiplier × Volume
Period: 20 days
Range: -1 to +1
Interpretation: >0 = Buying pressure, <0 = Selling pressure
Purpose: Measure buying/selling pressure
```
| Field | Type | Description |
|-------|------|-------------|
| `cmf` | FLOAT | Chaikin Money Flow (20) |

#### 10.3 Ichimoku Cloud (5 components)
```
Formula:
  Tenkan-sen (Conversion Line) = (9-day High + 9-day Low) / 2
  Kijun-sen (Base Line) = (26-day High + 26-day Low) / 2
  Senkou Span A (Leading Span A) = (Tenkan-sen + Kijun-sen) / 2, shifted +26
  Senkou Span B (Leading Span B) = (52-day High + 52-day Low) / 2, shifted +26
  Chikou Span (Lagging Span) = Close, shifted -26

Interpretation:
  - Price above cloud = Bullish
  - Price below cloud = Bearish
  - Span A > Span B = Bullish cloud
  - Span A < Span B = Bearish cloud
Purpose: All-in-one indicator for trend, momentum, and support/resistance
```
| Field | Type | Description |
|-------|------|-------------|
| `ichimoku_tenkan` | FLOAT | Tenkan-sen / Conversion Line (9) |
| `ichimoku_kijun` | FLOAT | Kijun-sen / Base Line (26) |
| `ichimoku_senkou_a` | FLOAT | Senkou Span A (leading, +26 shift) |
| `ichimoku_senkou_b` | FLOAT | Senkou Span B (leading, +26 shift) |
| `ichimoku_chikou` | FLOAT | Chikou Span (lagging, -26 shift) |

#### 10.4 VWAP (Volume Weighted Average Price)
```
Formula:
  VWAP = Cumulative(Typical Price × Volume) / Cumulative(Volume)
  where Typical Price = (High + Low + Close) / 3

Daily VWAP: Calculated from start of data (institutional benchmark)
Weekly VWAP: 5-day rolling VWAP

Purpose:
  - Institutional execution benchmark
  - Support/resistance level
  - Price above VWAP = Bullish, below = Bearish
```
| Field | Type | Description |
|-------|------|-------------|
| `vwap_daily` | FLOAT | Daily VWAP (cumulative from start) |
| `vwap_weekly` | FLOAT | Weekly VWAP (5-day rolling) |

#### 10.5 Volume Profile (3 components)
```
Algorithm:
  1. Divide price range into 10 bins over 20-day window
  2. Accumulate volume for each price bin
  3. POC = Price level with highest volume
  4. VAH/VAL = 70% value area boundaries around POC

Components:
  - POC (Point of Control): Price with most trading activity
  - VAH (Value Area High): Upper boundary of 70% volume
  - VAL (Value Area Low): Lower boundary of 70% volume

Purpose:
  - Identify institutional accumulation/distribution zones
  - Key support/resistance levels
  - Fair value regions
```
| Field | Type | Description |
|-------|------|-------------|
| `volume_profile_poc` | FLOAT | Point of Control (20-day window) |
| `volume_profile_vah` | FLOAT | Value Area High (70% volume) |
| `volume_profile_val` | FLOAT | Value Area Low (70% volume) |

---

### 11. ML FEATURES - RETURNS (3 fields)

```
Purpose: Machine learning features for predictive models
```
| Field | Type | Description | Formula |
|-------|------|-------------|---------|
| `log_return` | FLOAT | Logarithmic return | `ln(Close / Previous Close)` |
| `return_2w` | FLOAT | 2-week forward return % | `((Close[+10] - Close) / Close) × 100` |
| `return_4w` | FLOAT | 4-week forward return % | `((Close[+20] - Close) / Close) × 100` |

---

### 12. ML FEATURES - RELATIVE POSITIONS (3 fields)

```
Purpose: Measure price position relative to moving averages
```
| Field | Type | Description | Formula |
|-------|------|-------------|---------|
| `close_vs_sma20_pct` | FLOAT | Distance from SMA(20) % | `((Close - SMA20) / SMA20) × 100` |
| `close_vs_sma50_pct` | FLOAT | Distance from SMA(50) % | `((Close - SMA50) / SMA50) × 100` |
| `close_vs_sma200_pct` | FLOAT | Distance from SMA(200) % | `((Close - SMA200) / SMA200) × 100` |

---

### 13. ML FEATURES - INDICATOR DYNAMICS (11 fields)

```
Purpose: Capture rate of change and statistical properties of indicators
```
| Field | Type | Description | Formula |
|-------|------|-------------|---------|
| `rsi_slope` | FLOAT | 5-day RSI change | `RSI - RSI[5 days ago]` |
| `rsi_zscore` | FLOAT | RSI Z-score (20-day) | `(RSI - Mean) / Std Dev` |
| `rsi_overbought` | INT64 | RSI overbought flag | `1 if RSI > 70, else 0` |
| `rsi_oversold` | INT64 | RSI oversold flag | `1 if RSI < 30, else 0` |
| `macd_cross` | INT64 | MACD crossover signal | `1 = Bullish cross, -1 = Bearish cross, 0 = None` |
| `ema20_slope` | FLOAT | 5-day EMA(20) change | `EMA20 - EMA20[5 days ago]` |
| `ema50_slope` | FLOAT | 5-day EMA(50) change | `EMA50 - EMA50[5 days ago]` |
| `atr_zscore` | FLOAT | ATR Z-score (20-day) | `(ATR - Mean) / Std Dev` |
| `atr_slope` | FLOAT | 5-day ATR change | `ATR - ATR[5 days ago]` |
| `volume_zscore` | FLOAT | Volume Z-score (20-day) | `(Volume - Mean) / Std Dev` |
| `volume_ratio` | FLOAT | Volume vs average ratio | `Volume / Average Volume` |

---

### 14. ML FEATURES - MARKET STRUCTURE (4 fields)

```
Purpose: Identify pivot points and price structure
```
| Field | Type | Description | Formula |
|-------|------|-------------|---------|
| `pivot_high_flag` | INT64 | Pivot high detected | `1 if High > adjacent 4 highs, else 0` |
| `pivot_low_flag` | INT64 | Pivot low detected | `1 if Low < adjacent 4 lows, else 0` |
| `dist_to_pivot_high` | FLOAT | Distance to last pivot high | `Close - Last Pivot High` |
| `dist_to_pivot_low` | FLOAT | Distance to last pivot low | `Close - Last Pivot Low` |

---

### 15. ML FEATURES - REGIME DETECTION (3 fields)

```
Purpose: Identify market regime (trend/volatility state)
```
| Field | Type | Description | Formula |
|-------|------|-------------|---------|
| `trend_regime` | INT64 | Trend direction | `1 = Uptrend, -1 = Downtrend, 0 = Sideways` |
| `regime_confidence` | FLOAT | Trend strength measure | `abs(SMA50 slope) / Std Dev` |
| `vol_regime` | INT64 | Volatility state | `1 if ATR > 20-day mean, else 0` |

---

## Summary Statistics

### Total Fields: 80+
- **Base Fields**: 11 (identification, price, metadata)
- **Momentum Indicators**: 9 (RSI, MACD, Stochastic, CCI, Williams %R, Momentum)
- **Moving Averages**: 10 (SMA-3, EMA-5, KAMA-1, VWAP-1)
- **Bollinger Bands**: 4 (upper, middle, lower, width)
- **Trend Indicators**: 3 (ADX, +DI, -DI)
- **Volatility Indicators**: 2 (ATR, TRIX)
- **Rate of Change**: 1 (ROC)
- **Volume Indicators**: 3 (OBV, PVO, PPO)
- **Oscillators**: 2 (Ultimate, Awesome)
- **Institutional Indicators**: 11 (MFI, CMF, Ichimoku-5, VWAP-2, VProfile-3) ⭐ NEW
- **ML Features - Returns**: 3
- **ML Features - Relative Positions**: 3
- **ML Features - Indicator Dynamics**: 11
- **ML Features - Market Structure**: 4
- **ML Features - Regime Detection**: 3

### Total Indicators: 69 fields

---

## Data Quality Requirements

### Minimum Data Points
- **Short-term indicators** (RSI, MACD, Stochastic): Require 50+ rows
- **Medium-term indicators** (ADX, Bollinger): Require 100+ rows
- **Long-term indicators** (SMA200, EMA200): Require 200+ rows
- **Volume Profile**: Requires 20+ rows for rolling calculation

### Missing Data Handling
- Indicators return `NULL` when insufficient data
- Forward-looking features (return_2w, return_4w) are `NULL` for most recent rows
- Pivot distance features use forward-fill for last known pivot

---

## Usage Examples

### Query 1: Find Oversold Stocks with Strong Trends
```sql
SELECT symbol, close, rsi, adx, mfi
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE datetime = CURRENT_DATE() - 1
  AND rsi < 30           -- Oversold
  AND mfi < 20           -- Money Flow oversold
  AND adx > 25           -- Strong trend
ORDER BY rsi ASC
LIMIT 20;
```

### Query 2: Stocks Above Ichimoku Cloud
```sql
SELECT symbol, close,
       ichimoku_senkou_a, ichimoku_senkou_b,
       ichimoku_tenkan, ichimoku_kijun
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE datetime = CURRENT_DATE() - 1
  AND close > ichimoku_senkou_a
  AND close > ichimoku_senkou_b
  AND ichimoku_tenkan > ichimoku_kijun  -- Bullish conversion
ORDER BY (close - ichimoku_senkou_a) / close DESC
LIMIT 20;
```

### Query 3: Volume Profile Analysis
```sql
SELECT symbol, close,
       volume_profile_poc,
       volume_profile_vah,
       volume_profile_val,
       CASE
         WHEN close > volume_profile_vah THEN 'Above Value'
         WHEN close < volume_profile_val THEN 'Below Value'
         ELSE 'In Value Area'
       END as position
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE datetime = CURRENT_DATE() - 1
ORDER BY symbol;
```

### Query 4: VWAP Institutional Levels
```sql
SELECT symbol, close, vwap_daily, vwap_weekly,
       ROUND((close - vwap_daily) / vwap_daily * 100, 2) as vwap_daily_pct,
       ROUND((close - vwap_weekly) / vwap_weekly * 100, 2) as vwap_weekly_pct
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE datetime = CURRENT_DATE() - 1
  AND close > vwap_daily
  AND close > vwap_weekly  -- Price above both VWAPs = Strong
ORDER BY vwap_daily_pct DESC
LIMIT 20;
```

---

## Maintenance & Updates

### Calculation Process
1. Data fetched from Yahoo Finance API (daily OHLC)
2. Indicators calculated using pandas_ta library
3. Results uploaded to BigQuery via MERGE operation
4. Only indicators updated, base fields preserved

### Update Frequency
- **Development**: Manual runs via `calculate_all_indicators_ENHANCED.py`
- **Production**: Daily via Cloud Scheduler (after market close)

### Schema Evolution
- New indicator fields can be added without breaking existing queries
- MERGE operation automatically handles missing columns
- Null-safe for backward compatibility

---

## Related Tables

- **v2_stocks_daily**: Source table (base OHLC data only, no indicators)
- **stocks_hourly_clean**: Same indicators, hourly timeframe
- **stocks_5min_clean**: Same indicators, 5-minute timeframe
- **crypto_daily_clean**: Same indicators, cryptocurrency data (USD pairs only)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 7, 2025 | Initial table creation with 58 indicators |
| 2.0 | Dec 9, 2025 | Added 11 institutional indicators (MFI, CMF, Ichimoku-5, VWAP-2, VProfile-3) |

---

**END OF REFERENCE DOCUMENT**
