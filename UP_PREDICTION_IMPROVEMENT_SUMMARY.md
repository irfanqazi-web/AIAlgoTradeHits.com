# UP Cycle Prediction Improvement Summary

## Executive Summary
Successfully implemented a Rise Cycle scoring system that improves UP prediction accuracy from 4.2% baseline to **18-22%** for high-score signals - a **4-5x improvement**.

## Problem Statement
The original XGBoost model showed severe class imbalance bias:
- DOWN Accuracy: 98.6%
- UP Accuracy: Only 10.6%
- Baseline UP rate: ~4-6%

## Solution: Rise Cycle Score System

### Features Created (27 total)
1. **EMA Crossover Detection**
   - `ema_bullish`: EMA12 > EMA26
   - `ema_cross_up`: Fresh bullish crossover

2. **RSI Momentum**
   - `rsi_momentum_3d`: 3-day RSI change
   - `rsi_sweet_spot`: RSI between 40-65

3. **MACD Signals**
   - `macd_turning_bullish`: Histogram crossing positive
   - `macd_hist_change`: Daily histogram change

4. **Trend Confirmation**
   - `above_sma20/50/200`: Price vs moving averages
   - `strong_trend`: ADX > 25

5. **Supporting Indicators**
   - `volume_ratio`: Volume vs 20-day average
   - `daily_range_position`: Close in daily range
   - `bullish_divergence`: Price/RSI divergence
   - `up_days_5`: Consecutive up days

### Composite Rise Cycle Score (0-10)
Points awarded for:
- EMA bullish alignment (+1)
- RSI in sweet spot (+1)
- MACD histogram positive (+1)
- Price above SMA50 (+1)
- Price above SMA200 (+1)
- ADX > 25 (strong trend) (+1)
- MFI healthy (30-70) (+1)
- Positive momentum (+1)
- MACD histogram increasing (+1)
- RSI increasing (+1)

## Results

### Rise Cycle Score Effectiveness (2025 Data)
| Score | Total Signals | UP Count | UP % |
|-------|--------------|----------|------|
| 0 | 5,458 | 190 | 3.5% |
| 1 | 16,475 | 449 | 2.7% |
| 2 | 12,804 | 379 | 3.0% |
| 3 | 2,290 | 133 | 5.8% |
| 4 | 2,578 | 246 | **9.5%** |
| 5 | 1,271 | 245 | **19.3%** |
| 6 | 372 | 81 | **21.8%** |

### Signal Performance
| Signal | Total | UP Count | UP % | vs Baseline |
|--------|-------|----------|------|-------------|
| STRONG_BUY (Score 6+) | 292 | 54 | **18.5%** | 4.4x |
| BUY (Score 5+) | 1,423 | 255 | **17.9%** | 4.3x |
| WEAK_BUY (Score 4+) | 1,377 | 148 | **10.7%** | 2.5x |

## BigQuery Objects Created

### Tables
- `aialgotradehits.ml_models.rise_cycle_features` - 81,736 records with 27 features
- `aialgotradehits.ml_models.rise_cycle_balanced` - 10,530 balanced training records

### Models
- `aialgotradehits.ml_models.rise_cycle_predictor_v1` - XGBoost classifier

### Views
- `aialgotradehits.ml_models.v_rise_cycle_signals_final` - Production signal view
- `aialgotradehits.ml_models.v_high_confidence_up_signals` - Model probability-based view

## Trading Signal Rules

### STRONG_BUY
- Rise Cycle Score >= 6
- EMA bullish (EMA12 > EMA26)
- RSI between 45-65

### BUY
- Rise Cycle Score >= 5
- EMA bullish

### WEAK_BUY
- Rise Cycle Score >= 4
- RSI between 40-65

## Current Signals (Jan 2026)
| Date | Symbol | Price | Score | Signal | RSI | ADX |
|------|--------|-------|-------|--------|-----|-----|
| 2026-01-08 | HON | $205.24 | 5 | BUY | 58.5 | 26.5 |
| 2026-01-08 | V | $352.23 | 5 | BUY | 60.9 | 46.2 |
| 2026-01-07 | RTX | $185.73 | 5 | BUY | 60.9 | 46.5 |
| 2026-01-06 | GOOGL | $314.34 | 5 | BUY | 58.3 | 28.6 |

## Key Findings

1. **Rise Cycle Score is highly predictive** - Score 5+ achieves ~19% UP rate vs 4% baseline
2. **EMA confirmation is critical** - Bullish EMA alignment filters false signals
3. **RSI sweet spot matters** - RSI 45-65 indicates room for upward movement
4. **Model probabilities less reliable** - Raw feature scores outperform model probability outputs

## Recommendations

1. **Use Rise Cycle Score >= 5 for BUY signals**
2. **Require EMA bullish confirmation**
3. **Set position size based on score** (higher score = larger position)
4. **Combine with volume confirmation** (volume_ratio > 1.0)
5. **Monitor ADX for trend strength** (>25 = strong trend)

## Files Created
- `improve_up_prediction.py` - Main implementation script
- `UP_PREDICTION_IMPROVEMENT_SUMMARY.md` - This summary

---
*Generated: 2026-01-11*
*AIAlgoTradeHits.com - ML Trading Signals*
