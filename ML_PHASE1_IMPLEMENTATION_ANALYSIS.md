# ML Model Phase 1 Methodology - Implementation Analysis

**Project:** AIAlgoTradeHits
**Document:** Phase 1 ML Feature Implementation Status
**Created:** December 7, 2025
**Author:** Analysis by Claude Code based on Saleem's Phase 1 Methodology v4

---

## Executive Summary

| Category | Count | Percentage |
|----------|-------|------------|
| **Already Implemented** | 7 | 35% |
| **Partially Implemented** | 2 | 10% |
| **To Be Implemented** | 11 | 55% |
| **Total Features** | 20 | 100% |

---

## Detailed Feature Analysis

### IMPLEMENTED FEATURES (Ready for ML Training)

| # | Feature | Status | Current Field Names | Notes |
|---|---------|--------|---------------------|-------|
| 1 | **OHLCV + Timestamp** | COMPLETE | `open`, `high`, `low`, `close`, `volume`, `datetime` | Core data available in all v2 tables |
| 2 | **Weekly Return (% change)** | COMPLETE | `percent_change`, `weekly_change_percent` | Available in all tables |
| 5 | **RSI(14)** | COMPLETE | `rsi` | 14-period RSI calculated |
| 7 | **MACD(12,26,9)** | COMPLETE | `macd`, `macd_signal`, `macd_histogram` | Full MACD with histogram |
| 9 | **SMA20 / SMA50 / SMA200** | COMPLETE | `sma_20`, `sma_50`, `sma_200` | All three SMAs available |
| 13 | **ATR(14)** | COMPLETE | `atr` | Average True Range calculated |
| 15 | **Bollinger Bands (20,2)** | PARTIAL | `bollinger_upper`, `bollinger_middle`, `bollinger_lower` | Bands available, width needs calculation |

---

### PARTIALLY IMPLEMENTED (Minor Additions Needed)

| # | Feature | Current Status | What's Missing | Effort |
|---|---------|----------------|----------------|--------|
| 15 | **Bollinger Bands Width** | Bands exist | `bb_width = (upper - lower) / middle` | 5 min |
| 16 | **Volume z-score / ratio** | `volume` exists | z-score and ratio calculations | 10 min |

---

### TO BE IMPLEMENTED (New Features Required)

| # | Feature | Priority | Complexity | Est. Time |
|---|---------|----------|------------|-----------|
| 3 | **Weekly Log Return** | HIGH | Low | 5 min |
| 4 | **Multi-lag Returns (2w/4w)** | HIGH | Low | 10 min |
| 6 | **RSI slope / z-score / flags** | HIGH | Medium | 15 min |
| 8 | **MACD Histogram + Cross flag** | MEDIUM | Low | 10 min |
| 10 | **EMA20 / EMA50 / EMA200** | HIGH | Low | 10 min |
| 11 | **MA Distance % (close vs MA)** | HIGH | Low | 10 min |
| 12 | **EMA Slopes (20/50)** | MEDIUM | Low | 10 min |
| 14 | **ATR z-score / slope** | MEDIUM | Medium | 15 min |
| 17 | **ADX(14) + DI+/DI-** | HIGH | Medium | 20 min |
| 18 | **Pivot High / Pivot Low flags** | MEDIUM | Medium | 20 min |
| 19 | **Distance to last pivot** | MEDIUM | Medium | 15 min |
| 20 | **Numeric Regime State** | HIGH | High | 30 min |

---

## Implementation Plan

### Phase 1A: Quick Wins (30 minutes)
Features that can be added with simple calculations:

```python
# 3. Weekly Log Return
df['log_return'] = np.log(df['close'] / df['close'].shift(1))

# 4. Multi-lag Returns
df['return_2w'] = df['close'] / df['close'].shift(2) - 1
df['return_4w'] = df['close'] / df['close'].shift(4) - 1

# 10. EMAs
df['ema_20'] = df['close'].ewm(span=20).mean()
df['ema_50'] = df['close'].ewm(span=50).mean()
df['ema_200'] = df['close'].ewm(span=200).mean()

# 11. MA Distance %
df['close_vs_sma20_pct'] = (df['close'] / df['sma_20'] - 1) * 100
df['close_vs_sma50_pct'] = (df['close'] / df['sma_50'] - 1) * 100
df['close_vs_sma200_pct'] = (df['close'] / df['sma_200'] - 1) * 100

# 15. Bollinger Width
df['bb_width'] = (df['bollinger_upper'] - df['bollinger_lower']) / df['bollinger_middle']
```

### Phase 1B: Momentum Enhancements (45 minutes)

```python
# 6. RSI derivatives
df['rsi_slope'] = df['rsi'] - df['rsi'].shift(1)
df['rsi_zscore'] = (df['rsi'] - df['rsi'].rolling(100).mean()) / df['rsi'].rolling(100).std()
df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
df['rsi_oversold'] = (df['rsi'] < 30).astype(int)

# 8. MACD Cross Flag
df['macd_cross'] = np.where(
    (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1)), 1,
    np.where((df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1)), -1, 0)
)

# 12. EMA Slopes
df['ema20_slope'] = df['ema_20'] - df['ema_20'].shift(1)
df['ema50_slope'] = df['ema_50'] - df['ema_50'].shift(1)

# 14. ATR derivatives
df['atr_zscore'] = (df['atr'] - df['atr'].rolling(52).mean()) / df['atr'].rolling(52).std()
df['atr_slope'] = df['atr'] - df['atr'].shift(1)

# 16. Volume z-score
df['volume_zscore'] = (df['volume'] - df['volume'].rolling(52).mean()) / df['volume'].rolling(52).std()
df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
```

### Phase 1C: Advanced Features (60 minutes)

```python
# 17. ADX + DI components
# (Already have ADX, need DI+ and DI-)
df['plus_di'] = ... # Directional Indicator Plus
df['minus_di'] = ... # Directional Indicator Minus

# 18-19. Pivot Points
def find_pivots(df, window=5):
    df['pivot_high'] = df['high'][(df['high'] == df['high'].rolling(window*2+1, center=True).max())]
    df['pivot_low'] = df['low'][(df['low'] == df['low'].rolling(window*2+1, center=True).min())]
    return df

# 20. Numeric Regime State
def calculate_regime(df):
    # Trend regime: 1=bullish, -1=bearish, 0=neutral
    df['trend_regime'] = np.where(
        (df['close'] > df['sma_50']) & (df['sma_50'] > df['sma_200']), 1,
        np.where((df['close'] < df['sma_50']) & (df['sma_50'] < df['sma_200']), -1, 0)
    )
    # Volatility regime: 1=high, 0=normal, -1=low
    df['vol_regime'] = np.where(
        df['atr_zscore'] > 1, 1,
        np.where(df['atr_zscore'] < -1, -1, 0)
    )
    return df
```

---

## Current BigQuery Schema vs Required

### Existing Fields (v2_*_daily tables):
```
datetime, open, high, low, close, volume, symbol, name, exchange, currency,
percent_change, rsi, macd, macd_signal, macd_histogram,
bollinger_upper, bollinger_middle, bollinger_lower,
sma_20, sma_50, sma_200, ema_12, ema_26, adx, atr,
stoch_k, stoch_d, cci, williams_r, obv, momentum, roc
```

### New Fields to Add (Phase 1 ML Features):
```sql
-- Phase 1A: Quick Wins
log_return FLOAT64,
return_2w FLOAT64,
return_4w FLOAT64,
ema_20 FLOAT64,
ema_50 FLOAT64,
ema_200 FLOAT64,
close_vs_sma20_pct FLOAT64,
close_vs_sma50_pct FLOAT64,
close_vs_sma200_pct FLOAT64,
bb_width FLOAT64,

-- Phase 1B: Momentum Enhancements
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
volume_ratio FLOAT64,

-- Phase 1C: Advanced Features
plus_di FLOAT64,
minus_di FLOAT64,
pivot_high_flag INT64,
pivot_low_flag INT64,
dist_to_pivot_high FLOAT64,
dist_to_pivot_low FLOAT64,
trend_regime INT64,
vol_regime INT64,
regime_confidence FLOAT64
```

---

## Training Data Requirements

### Current Data Available:
| Symbol | Daily | Hourly | 5-min | Total |
|--------|-------|--------|-------|-------|
| BTCUSD | 3,651 | 720 | 2,304 | 6,675 |
| QQQ | 2,512 | 137 | 390 | 3,039 |
| SPY | 2,512 | 137 | 390 | 3,039 |
| **Total** | **8,675** | **994** | **3,084** | **12,753** |

### Data Coverage:
- **Daily**: 10 years (2015-2025) - READY FOR ML
- **Hourly**: 1 month - READY FOR ML
- **5-minute**: 1 week - READY FOR ML

---

## Implementation Timeline

| Phase | Features | Time | Cumulative |
|-------|----------|------|------------|
| **1A: Quick Wins** | #3, #4, #10, #11, #15 | 30 min | 30 min |
| **1B: Momentum** | #6, #8, #12, #14, #16 | 45 min | 1h 15m |
| **1C: Advanced** | #17, #18, #19, #20 | 60 min | 2h 15m |
| **Testing & Validation** | All features | 30 min | 2h 45m |
| **BigQuery Schema Update** | Add new columns | 15 min | 3h 00m |

**Total Estimated Time: 3 hours**

---

## Recommended Next Steps

1. **Immediate (Today)**:
   - Run Phase 1A quick wins script
   - Add new columns to BigQuery tables
   - Backfill BTC, QQQ, SPY with new features

2. **Short-term (This Week)**:
   - Complete Phase 1B and 1C features
   - Validate feature calculations
   - Create feature importance analysis

3. **ML Training Ready**:
   - Export training dataset with all 20 features
   - Begin Gemini 2.5 model training
   - Establish baseline prediction accuracy

---

## Feature Importance for Price Prediction

Based on ML research, expected feature importance ranking:

| Rank | Feature | Why Important |
|------|---------|---------------|
| 1 | Multi-lag Returns (2w/4w) | Direct momentum measure |
| 2 | MA Distance % | Mean reversion signal |
| 3 | RSI + derivatives | Overbought/oversold timing |
| 4 | Volume z-score | Confirms price moves |
| 5 | Regime State | Context for predictions |
| 6 | ATR z-score | Volatility regime |
| 7 | MACD Cross | Trend change signal |
| 8 | Pivot distances | Support/resistance levels |
| 9 | EMA Slopes | Trend acceleration |
| 10 | Bollinger Width | Volatility compression |

---

## Contact

- **Developer**: irfan.qazi@aialgotradehits.com
- **Methodology Author**: Saleem Ahmad
- **Project**: aialgotradehits
- **Date**: December 2025

---

*Document generated based on "Phase 1 methodology.xlsx" by Saleem Ahmad*
