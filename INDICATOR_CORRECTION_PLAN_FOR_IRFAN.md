# INDICATOR CORRECTION IMPLEMENTATION PLAN

**For:** Irfan Saheb
**From:** Saleem Ahmad / AI Trading System Team
**Date:** December 11, 2025
**Priority:** High - Affects ML Model Accuracy

---

## WHY WE'RE MAKING THESE CHANGES

**Primary Reason:** Match Industry Standards & TradingView

Our users will compare our platform against TradingView (the industry standard). When our RSI shows 14.53 but TradingView shows 27.27 for the same stock on the same day, users will lose confidence in our platform.

**Additional Benefits:**
- ML models trained on standard indicators will work correctly in live trading
- Users can validate our signals against other platforms
- Professional credibility - shows we follow established technical analysis standards
- Cross-platform compatibility for trading strategies

**Bottom Line:** We must match what traders see on TradingView/Bloomberg/other professional platforms.

---

## CHANGES REQUIRED - SUMMARY

| # | Indicator | Current Method | Change To | Reason |
|---|-----------|---------------|-----------|---------|
| 1 | RSI | SMA smoothing | Wilder's RMA | Industry standard (J. Welles Wilder's original formula) |
| 2 | ADX | SMA smoothing | Wilder's RMA | Industry standard (Wilder's original formula) |
| 3 | +DI | SMA smoothing | Wilder's RMA | Industry standard (Wilder's original formula) |
| 4 | -DI | SMA smoothing | Wilder's RMA | Industry standard (Wilder's original formula) |
| 5 | ATR | SMA smoothing | Wilder's RMA | Industry standard (Wilder's original formula) |
| 6 | Stochastic %K | Fast (raw) | Slow (SMA-3) | TradingView default |
| 7 | Stochastic %D | Fast variant | Slow variant | TradingView default |
| 8 | ROC | Period 12 | Period 10 | TradingView default |
| 9 | Ichimoku Senkou A | No shift | Shift +26 periods | Original Ichimoku design |
| 10 | Ichimoku Senkou B | No shift | Shift +26 periods | Original Ichimoku design |
| 11 | Bollinger Upper | ddof=1 | ddof=0 | TradingView standard |
| 12 | Bollinger Lower | ddof=1 | ddof=0 | TradingView standard |

---

## DETAILED CHANGES

### 1. RSI (Relative Strength Index)

**Current Code Pattern:**
```python
gain = delta.where(delta > 0, 0).rolling(window=14).mean()
loss = (-delta).where(delta < 0, 0).rolling(window=14).mean()
```

**Change To (Wilder's RMA):**
```python
gain = delta.where(delta > 0, 0).ewm(alpha=1/14, adjust=False).mean()
loss = (-delta).where(delta < 0, 0).ewm(alpha=1/14, adjust=False).mean()
```

**Why:** J. Welles Wilder Jr. (creator of RSI) specified this smoothing method. All professional platforms use it.

---

### 2. ATR (Average True Range)

**Current Code Pattern:**
```python
atr = true_range.rolling(window=14).mean()
```

**Change To (Wilder's RMA):**
```python
atr = true_range.ewm(alpha=1/14, adjust=False).mean()
```

**Why:** Wilder's original ATR formula. TradingView uses this.

---

### 3. ADX / +DI / -DI

**Current Code Pattern:**
```python
# Smoothing step uses .rolling().mean()
plus_dm_smooth = plus_dm.rolling(window=14).mean()
minus_dm_smooth = minus_dm.rolling(window=14).mean()
tr_smooth = true_range.rolling(window=14).mean()
```

**Change To (Wilder's RMA):**
```python
# Change all smoothing to ewm
plus_dm_smooth = plus_dm.ewm(alpha=1/14, adjust=False).mean()
minus_dm_smooth = minus_dm.ewm(alpha=1/14, adjust=False).mean()
tr_smooth = true_range.ewm(alpha=1/14, adjust=False).mean()
```

**Why:** ADX was designed by Wilder with his smoothing method. TradingView uses this.

---

### 4. Stochastic Oscillator

**Current Code (Fast Stochastic):**
```python
# %K - raw calculation (no smoothing)
stoch_k = 100 * (close - low_14) / (high_14 - low_14)

# %D - SMA of raw %K
stoch_d = stoch_k.rolling(window=3).mean()
```

**Change To (Slow Stochastic):**
```python
# Raw calculation first
raw_k = 100 * (close - low_14) / (high_14 - low_14)

# %K - Smoothed with SMA(3)
stoch_k = raw_k.rolling(window=3).mean()

# %D - SMA(3) of smoothed %K
stoch_d = stoch_k.rolling(window=3).mean()
```

**Why:** TradingView default is Slow Stochastic. Fast Stochastic is too noisy for most traders.

---

### 5. ROC (Rate of Change)

**Current Code:**
```python
roc = ((close - close.shift(12)) / close.shift(12)) * 100
```

**Change To:**
```python
roc = ((close - close.shift(10)) / close.shift(10)) * 100
```

**Why:** TradingView default period is 10. Industry standard.

---

### 6. Ichimoku Cloud (Senkou Span A & B)

**Current Code:**
```python
# Senkou Span A
senkou_a = (tenkan + kijun) / 2

# Senkou Span B
period_high_52 = high.rolling(window=52).max()
period_low_52 = low.rolling(window=52).min()
senkou_b = (period_high_52 + period_low_52) / 2
```

**Change To:**
```python
# Senkou Span A - ADD 26-PERIOD FORWARD SHIFT
senkou_a = ((tenkan + kijun) / 2).shift(26)

# Senkou Span B - ADD 26-PERIOD FORWARD SHIFT
period_high_52 = high.rolling(window=52).max()
period_low_52 = low.rolling(window=52).min()
senkou_b = ((period_high_52 + period_low_52) / 2).shift(26)
```

**Why:** The Ichimoku Cloud is DESIGNED to project future support/resistance. The 26-period forward shift is essential to its purpose. Without it, the indicator loses its predictive value. This is how Ichimoku Kinko Hyo was originally designed in 1968.

---

### 7. Bollinger Bands

**Current Code:**
```python
# Middle band
bb_middle = close.rolling(window=20).mean()

# Standard deviation with ddof=1 (sample std)
std = close.rolling(window=20).std(ddof=1)

# Bands
bb_upper = bb_middle + (2 * std)
bb_lower = bb_middle - (2 * std)
```

**Change To:**
```python
# Middle band (no change)
bb_middle = close.rolling(window=20).mean()

# Standard deviation with ddof=0 (population std)
std = close.rolling(window=20).std(ddof=0)

# Bands
bb_upper = bb_middle + (2 * std)
bb_lower = bb_middle - (2 * std)
```

**Why:** TradingView and most platforms use population standard deviation (ddof=0) for Bollinger Bands.

---

## IMPLEMENTATION STEPS

### Step 1: Update Code (4 hours)
1. Locate your indicator calculation module (likely `indicators.py` or `technical_indicators.py`)
2. Make the changes listed above for each indicator
3. **IMPORTANT:** Keep the old code commented out for reference
4. Add comments explaining the change: `# Changed to Wilder's RMA to match TradingView`

### Step 2: Test Against pandas_ta (4 hours)
1. Use Saleem's validation script: `validate_indicators.py`
2. Test on 3 symbols: SPY, QQQ, AAPL
3. Target: 95%+ match rate for all corrected indicators
4. If any indicator still fails, compare your code line-by-line with pandas_ta source code

### Step 3: Update Database Schema (1 hour)
**IMPORTANT DECISION NEEDED:**

**Option A: Overwrite existing data** (Recommended)
- Drop all existing indicator data
- Re-backfill with corrected calculations
- Clean break, no confusion

**Option B: Keep both versions** (Not Recommended)
- Add new columns: `rsi_v2`, `atr_v2`, etc.
- Keep old data for comparison
- More complex, doubles storage

**Saleem's Decision:** We recommend **Option A** - overwrite with correct data.

### Step 4: Re-Backfill All Data (8-12 hours)
1. Clear existing indicator data from database
2. Re-run backfill script for all 550-650 symbols
3. Monitor for errors during backfill
4. Verify data completeness after backfill

### Step 5: Validation (2 hours)
1. Run validation script on 10 random symbols
2. Compare 5 random dates against TradingView manually
3. Check for NULL values or calculation errors
4. Get Saleem's approval on sample data

### Step 6: Deploy (2 hours)
1. Update Cloud Functions with new indicator code
2. Update any ML model pipelines that reference indicators
3. Deploy to production
4. Monitor for issues in first 24 hours

---

## TOTAL ESTIMATED TIME

| Task | Time |
|------|------|
| Code updates | 4 hours |
| Testing | 4 hours |
| Schema decisions | 1 hour |
| Data backfill | 8-12 hours |
| Validation | 2 hours |
| Deployment | 2 hours |
| **TOTAL** | **21-25 hours** |

**Calendar Time:** 3-4 days (including backfill running overnight)

---

## VALIDATION CHECKLIST

Before marking this task complete, verify:

- [ ] Validation script shows 95%+ match for all 13 corrected indicators
- [ ] Manual spot-check: RSI on SPY matches TradingView for Dec 10, 2025
- [ ] Manual spot-check: ADX on QQQ matches TradingView for Dec 10, 2025
- [ ] Manual spot-check: Stochastic on AAPL matches TradingView for Dec 10, 2025
- [ ] All 550-650 symbols have complete indicator data (no excessive NULLs)
- [ ] Ichimoku Cloud shifts forward 26 periods (check visually on chart)
- [ ] ML training pipeline tested with new indicators (no errors)
- [ ] Saleem approval obtained on sample comparisons

---

## REFERENCE: WILDER'S RMA vs SMA

**What is Wilder's RMA (Relative Moving Average)?**

It's an exponentially weighted moving average with alpha = 1/period.

**Mathematical Formula:**
```
First value: RMA(1) = SMA(values, period)
Subsequent values: RMA(n) = (RMA(n-1) * (period - 1) + current_value) / period
```

**In pandas:**
```python
# Wilder's RMA
ewm(alpha=1/period, adjust=False).mean()

# Example for 14-period
ewm(alpha=1/14, adjust=False).mean()
```

**Why it's different from SMA:**
- SMA: All values have equal weight
- Wilder's RMA: Recent values have more weight, older values decay exponentially
- Result: Wilder's RMA is more responsive to recent price changes

**Who uses it:**
- RSI (J. Welles Wilder Jr., 1978)
- ATR (J. Welles Wilder Jr., 1978)
- ADX (J. Welles Wilder Jr., 1978)
- TradingView (for all Wilder indicators)
- Bloomberg Terminal
- pandas_ta library
- Every professional trading platform

---

## QUESTIONS FOR IRFAN

1. **Where is your indicator calculation code located?**
   - File name and path?

2. **Do you use pandas for calculations, or custom code?**
   - If pandas: Easy to update
   - If custom: May need more time

3. **How long does full backfill take currently?**
   - Need to estimate downtime

4. **Any dependencies on current indicator values?**
   - ML models that need retraining?
   - Alerts or triggers based on specific values?

5. **Preference on timing?**
   - Do this now, or wait for specific milestone?

---

## SUPPORT AVAILABLE

- Saleem's validation script: `validate_indicators.py`
- pandas_ta documentation: https://github.com/twopirllc/pandas-ta
- Wilder's formulas reference: Appendix B in SME review PDF
- Real-time support during implementation via this chat

---

## APPROVAL

**Task Approved By:** Saleem Ahmad
**Date:** December 11, 2025
**Priority:** High
**Target Completion:** December 14-15, 2025

---

**Once complete, we will have indicators that exactly match TradingView and industry standards. This is critical for user trust and ML model accuracy.**
