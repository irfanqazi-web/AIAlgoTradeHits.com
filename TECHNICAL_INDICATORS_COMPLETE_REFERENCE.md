# Technical Indicators - Complete Reference Guide

**Project:** AIAlgoTradeHits Stock Analysis System
**Table:** `aialgotradehits.crypto_trading_data.stocks_daily_clean`
**Total Indicator Fields:** 58
**Data Coverage:** 1,141,844 rows | 262 symbols | 1998-2025 (27 years)

---

## Table of Contents

1. [Momentum Indicators (9 fields)](#1-momentum-indicators)
2. [Moving Averages (9 fields)](#2-moving-averages)
3. [Trend & Volatility Indicators (10 fields)](#3-trend--volatility-indicators)
4. [Volume Indicators (3 fields)](#4-volume-indicators)
5. [Advanced Oscillators (2 fields)](#5-advanced-oscillators)
6. [ML Features - Returns (3 fields)](#6-ml-features---returns)
7. [ML Features - Relative Positions (3 fields)](#7-ml-features---relative-positions)
8. [ML Features - Indicator Dynamics (11 fields)](#8-ml-features---indicator-dynamics)
9. [ML Features - Market Structure (4 fields)](#9-ml-features---market-structure)
10. [ML Features - Regime Detection (3 fields)](#10-ml-features---regime-detection)
11. [Implementation Notes](#implementation-notes)

---

## 1. MOMENTUM INDICATORS (9 fields)

### 1.1 RSI (Relative Strength Index)
- **Field:** `rsi`
- **Type:** FLOAT64
- **Range:** 0-100
- **Purpose:** Measures momentum and identifies overbought/oversold conditions

**Formula:**
```
RSI = 100 - (100 / (1 + RS))
where RS = Average Gain / Average Loss over N periods (typically 14)

Average Gain = Sum of Gains over N periods / N
Average Loss = Sum of Losses over N periods / N
```

**Interpretation:**
- **RSI > 70:** Overbought condition (potential sell signal)
- **RSI < 30:** Oversold condition (potential buy signal)
- **RSI = 50:** Neutral momentum
- **Divergence:** Price making new highs while RSI doesn't = bearish divergence

**pandas_ta Implementation:**
```python
df['rsi'] = ta.rsi(df['close'], length=14)
```

---

### 1.2 MACD (Moving Average Convergence Divergence)
- **Fields:** `macd`, `macd_signal`, `macd_histogram`
- **Type:** FLOAT64
- **Purpose:** Trend-following momentum indicator showing relationship between two moving averages

**Formula:**
```
MACD Line = EMA(12) - EMA(26)
Signal Line = EMA(9) of MACD Line
Histogram = MACD Line - Signal Line
```

**Interpretation:**
- **MACD > Signal:** Bullish crossover (buy signal)
- **MACD < Signal:** Bearish crossover (sell signal)
- **Histogram > 0:** Bullish momentum
- **Histogram < 0:** Bearish momentum
- **Divergence:** Price and MACD moving in opposite directions

**pandas_ta Implementation:**
```python
macd_result = ta.macd(df['close'], fast=12, slow=26, signal=9)
df['macd'] = macd_result.iloc[:, 0]           # MACD line
df['macd_signal'] = macd_result.iloc[:, 1]    # Signal line
df['macd_histogram'] = macd_result.iloc[:, 2] # Histogram
```

---

### 1.3 Stochastic Oscillator
- **Fields:** `stoch_k`, `stoch_d`
- **Type:** FLOAT64
- **Range:** 0-100
- **Purpose:** Compares closing price to price range over time

**Formula:**
```
%K = 100 × (Close - Lowest Low) / (Highest High - Lowest Low)
where Lowest Low and Highest High are over K periods (typically 14)

%D = SMA(%K, D periods) where D is typically 3
```

**Interpretation:**
- **%K > 80:** Overbought
- **%K < 20:** Oversold
- **%K crosses above %D:** Bullish signal
- **%K crosses below %D:** Bearish signal

**pandas_ta Implementation:**
```python
stoch_result = ta.stoch(df['high'], df['low'], df['close'], k=14, d=3)
df['stoch_k'] = stoch_result.iloc[:, 0]  # %K line
df['stoch_d'] = stoch_result.iloc[:, 1]  # %D line
```

---

### 1.4 CCI (Commodity Channel Index)
- **Field:** `cci`
- **Type:** FLOAT64
- **Range:** Unbounded (typically -200 to +200)
- **Purpose:** Identifies cyclical trends and overbought/oversold levels

**Formula:**
```
Typical Price = (High + Low + Close) / 3
CCI = (Typical Price - SMA of Typical Price) / (0.015 × Mean Deviation)

where Mean Deviation = Average of |Typical Price - SMA|
```

**Interpretation:**
- **CCI > +100:** Overbought, strong uptrend
- **CCI < -100:** Oversold, strong downtrend
- **CCI between -100 and +100:** Normal trading range
- **Zero line crossover:** Trend change signal

**pandas_ta Implementation:**
```python
df['cci'] = ta.cci(df['high'], df['low'], df['close'], length=20)
```

---

### 1.5 Williams %R
- **Field:** `williams_r`
- **Type:** FLOAT64
- **Range:** -100 to 0
- **Purpose:** Momentum indicator measuring overbought/oversold levels

**Formula:**
```
%R = -100 × (Highest High - Close) / (Highest High - Lowest Low)
where Highest High and Lowest Low are over N periods (typically 14)
```

**Interpretation:**
- **%R > -20:** Overbought
- **%R < -80:** Oversold
- **%R crosses -50:** Trend change signal
- **Opposite of Stochastic:** Values are inverted

**pandas_ta Implementation:**
```python
df['williams_r'] = ta.willr(df['high'], df['low'], df['close'], length=14)
```

---

### 1.6 Momentum
- **Field:** `momentum`
- **Type:** FLOAT64
- **Purpose:** Rate of change of price

**Formula:**
```
Momentum = Close(today) - Close(N periods ago)
where N is typically 10
```

**Interpretation:**
- **Momentum > 0:** Upward price movement
- **Momentum < 0:** Downward price movement
- **Magnitude:** Indicates strength of movement
- **Zero crossover:** Potential trend change

**pandas_ta Implementation:**
```python
df['momentum'] = ta.mom(df['close'], length=10)
```

---

## 2. MOVING AVERAGES (9 fields)

### 2.1 Simple Moving Averages (SMA)
- **Fields:** `sma_20`, `sma_50`, `sma_200`
- **Type:** FLOAT64
- **Purpose:** Smooths price data to identify trend direction

**Formula:**
```
SMA = Sum of Closing Prices over N periods / N
```

**Interpretations:**

**SMA 20 (Short-term trend):**
- Tracks 20 trading days (~1 month)
- Quick response to price changes
- Used for short-term trading signals

**SMA 50 (Medium-term trend):**
- Tracks 50 trading days (~2.5 months)
- Balanced trend indicator
- Common support/resistance level

**SMA 200 (Long-term trend):**
- Tracks 200 trading days (~10 months)
- Indicates major trend direction
- Key level: Above = bull market, Below = bear market

**Trading Signals:**
- **Golden Cross:** SMA 50 crosses above SMA 200 (bullish)
- **Death Cross:** SMA 50 crosses below SMA 200 (bearish)
- **Price above SMA:** Bullish signal
- **Price below SMA:** Bearish signal

**pandas_ta Implementation:**
```python
df['sma_20'] = ta.sma(df['close'], length=20)
df['sma_50'] = ta.sma(df['close'], length=50)
df['sma_200'] = ta.sma(df['close'], length=200)
```

---

### 2.2 Exponential Moving Averages (EMA)
- **Fields:** `ema_12`, `ema_20`, `ema_26`, `ema_50`, `ema_200`
- **Type:** FLOAT64
- **Purpose:** Weighted moving average giving more importance to recent prices

**Formula:**
```
EMA(today) = (Close(today) × Multiplier) + (EMA(yesterday) × (1 - Multiplier))

where Multiplier = 2 / (N + 1)
and N is the number of periods
```

**Multipliers:**
- EMA 12: 2/(12+1) = 0.1538
- EMA 20: 2/(20+1) = 0.0952
- EMA 26: 2/(26+1) = 0.0741
- EMA 50: 2/(50+1) = 0.0392
- EMA 200: 2/(200+1) = 0.00995

**Interpretation:**
- **More responsive** than SMA to recent price changes
- **EMA 12 & 26:** Used in MACD calculation
- **EMA 20:** Short-term trend
- **EMA 50:** Medium-term trend
- **EMA 200:** Long-term trend
- **Price > EMA:** Bullish
- **Price < EMA:** Bearish

**pandas_ta Implementation:**
```python
df['ema_12'] = ta.ema(df['close'], length=12)
df['ema_20'] = ta.ema(df['close'], length=20)
df['ema_26'] = ta.ema(df['close'], length=26)
df['ema_50'] = ta.ema(df['close'], length=50)
df['ema_200'] = ta.ema(df['close'], length=200)
```

---

### 2.3 KAMA (Kaufman's Adaptive Moving Average)
- **Field:** `kama`
- **Type:** FLOAT64
- **Purpose:** Adaptive moving average that adjusts smoothing based on market volatility

**Formula:**
```
Efficiency Ratio (ER) = |Change over N periods| / Sum of |Daily Changes|

Smoothing Constant (SC) = [ER × (Fastest SC - Slowest SC) + Slowest SC]²

KAMA = KAMA(previous) + SC × [Price - KAMA(previous)]

where:
- N = 10 periods (default)
- Fastest SC = 2/(2+1) = 0.6667
- Slowest SC = 2/(30+1) = 0.0645
```

**Interpretation:**
- **Adapts to market conditions:** Fast in trending markets, slow in choppy markets
- **Less lag** than traditional moving averages in trends
- **Reduced noise** during consolidation
- **Price > KAMA:** Bullish
- **Price < KAMA:** Bearish

**pandas_ta Implementation:**
```python
df['kama'] = ta.kama(df['close'], length=10)
```

---

## 3. TREND & VOLATILITY INDICATORS (10 fields)

### 3.1 Bollinger Bands
- **Fields:** `bollinger_upper`, `bollinger_middle`, `bollinger_lower`, `bb_width`
- **Type:** FLOAT64
- **Purpose:** Volatility indicator showing price envelope based on standard deviation

**Formula:**
```
Middle Band = SMA(20)
Upper Band = SMA(20) + (2 × Standard Deviation)
Lower Band = SMA(20) - (2 × Standard Deviation)
BB Width = (Upper Band - Lower Band) / Middle Band
```

**Interpretation:**

**Band Position:**
- **Price near Upper Band:** Overbought condition
- **Price near Lower Band:** Oversold condition
- **Price at Middle Band:** Fair value

**Band Width:**
- **Narrow bands (BB Width small):** Low volatility, potential breakout coming
- **Wide bands (BB Width large):** High volatility, potential reversal
- **Bollinger Squeeze:** Bands tighten before significant move

**Trading Signals:**
- **Bollinger Bounce:** Price bounces off upper/lower band
- **Bollinger Squeeze:** Bands contract then expand (breakout signal)
- **Walking the Bands:** Strong trend when price stays near one band

**pandas_ta Implementation:**
```python
bbands_result = ta.bbands(df['close'], length=20, std=2)
df['bollinger_upper'] = bbands_result.iloc[:, 0]   # Upper band
df['bollinger_middle'] = bbands_result.iloc[:, 1]  # Middle band (SMA 20)
df['bollinger_lower'] = bbands_result.iloc[:, 2]   # Lower band
df['bb_width'] = bbands_result.iloc[:, 3]          # Band width
```

---

### 3.2 ADX (Average Directional Index)
- **Fields:** `adx`, `plus_di`, `minus_di`
- **Type:** FLOAT64
- **Range:** 0-100
- **Purpose:** Measures trend strength regardless of direction

**Formula:**
```
True Range (TR) = max(High - Low, |High - Close(prev)|, |Low - Close(prev)|)

+DM (Directional Movement) = High - High(prev) if > 0 and > (Low(prev) - Low), else 0
-DM = Low(prev) - Low if > 0 and > (High - High(prev)), else 0

+DI (Directional Indicator) = 100 × Smoothed +DM / ATR
-DI = 100 × Smoothed -DM / ATR

DX = 100 × |+DI - -DI| / (+DI + -DI)

ADX = Smoothed Average of DX over N periods (typically 14)
```

**Interpretation:**

**ADX Value:**
- **ADX < 20:** Weak trend or ranging market
- **ADX 20-25:** Trend emerging
- **ADX 25-50:** Strong trend
- **ADX 50-75:** Very strong trend
- **ADX > 75:** Extremely strong trend (rare)

**Directional Indicators:**
- **+DI > -DI:** Uptrend
- **-DI > +DI:** Downtrend
- **+DI crosses above -DI:** Bullish signal
- **-DI crosses above +DI:** Bearish signal

**Trading Strategy:**
- **ADX rising + +DI > -DI:** Strong uptrend, consider long
- **ADX rising + -DI > +DI:** Strong downtrend, consider short
- **ADX falling:** Trend weakening, potential reversal

**pandas_ta Implementation:**
```python
adx_result = ta.adx(df['high'], df['low'], df['close'], length=14)
df['adx'] = adx_result.iloc[:, 0]        # ADX
df['plus_di'] = adx_result.iloc[:, 1]    # +DI
df['minus_di'] = adx_result.iloc[:, 2]   # -DI
```

---

### 3.3 ATR (Average True Range)
- **Field:** `atr`
- **Type:** FLOAT64
- **Purpose:** Measures market volatility

**Formula:**
```
True Range = max of:
  1. High - Low
  2. |High - Close(previous)|
  3. |Low - Close(previous)|

ATR = Exponential Moving Average of True Range over N periods (typically 14)
```

**Interpretation:**
- **High ATR:** High volatility, large price swings
- **Low ATR:** Low volatility, small price movements
- **ATR increasing:** Volatility expanding
- **ATR decreasing:** Volatility contracting

**Trading Applications:**
- **Position sizing:** Use ATR to determine stop-loss distance
- **Volatility breakout:** ATR spike indicates potential breakout
- **Stop-loss placement:** Set stops at 2-3 × ATR below entry

**pandas_ta Implementation:**
```python
df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
```

---

### 3.4 TRIX (Triple Exponential Average)
- **Field:** `trix`
- **Type:** FLOAT64
- **Purpose:** Momentum oscillator showing rate of change of triple EMA

**Formula:**
```
Single EMA = EMA(Close, N)
Double EMA = EMA(Single EMA, N)
Triple EMA = EMA(Double EMA, N)

TRIX = % change in Triple EMA = (Triple EMA - Triple EMA(prev)) / Triple EMA(prev) × 100

where N is typically 15
```

**Interpretation:**
- **TRIX > 0:** Bullish momentum
- **TRIX < 0:** Bearish momentum
- **TRIX crosses above zero:** Buy signal
- **TRIX crosses below zero:** Sell signal
- **Divergence:** Price and TRIX moving in opposite directions

**pandas_ta Implementation:**
```python
df['trix'] = ta.trix(df['close'], length=15)
```

---

### 3.5 ROC (Rate of Change)
- **Field:** `roc`
- **Type:** FLOAT64
- **Purpose:** Momentum oscillator measuring percentage change in price

**Formula:**
```
ROC = (Close - Close(N periods ago)) / Close(N periods ago) × 100

where N is typically 10
```

**Interpretation:**
- **ROC > 0:** Price increasing (bullish)
- **ROC < 0:** Price decreasing (bearish)
- **ROC crosses above zero:** Buy signal
- **ROC crosses below zero:** Sell signal
- **Extreme values:** Overbought/oversold conditions
- **Divergence:** Early warning of trend change

**pandas_ta Implementation:**
```python
df['roc'] = ta.roc(df['close'], length=10)
```

---

## 4. VOLUME INDICATORS (3 fields)

### 4.1 OBV (On-Balance Volume)
- **Field:** `obv`
- **Type:** FLOAT64
- **Purpose:** Cumulative volume indicator showing buying/selling pressure

**Formula:**
```
If Close > Close(previous):
    OBV = OBV(previous) + Volume

If Close < Close(previous):
    OBV = OBV(previous) - Volume

If Close = Close(previous):
    OBV = OBV(previous)
```

**Interpretation:**
- **OBV rising:** Buying pressure, volume confirming uptrend
- **OBV falling:** Selling pressure, volume confirming downtrend
- **Price up + OBV down:** Divergence, potential reversal
- **Price down + OBV up:** Divergence, potential bounce
- **OBV breakout before price:** Leading indicator

**pandas_ta Implementation:**
```python
df['obv'] = ta.obv(df['close'], df['volume'])
```

---

### 4.2 PVO (Percentage Volume Oscillator)
- **Field:** `pvo`
- **Type:** FLOAT64
- **Purpose:** MACD for volume, showing difference between two volume EMAs

**Formula:**
```
PVO = (EMA(Volume, Fast) - EMA(Volume, Slow)) / EMA(Volume, Slow) × 100

where Fast = 12, Slow = 26 (default)
```

**Interpretation:**
- **PVO > 0:** Volume above average (increasing activity)
- **PVO < 0:** Volume below average (decreasing activity)
- **PVO rising:** Volume momentum increasing
- **PVO falling:** Volume momentum decreasing
- **Use with price:** Confirm breakouts with PVO spikes

**pandas_ta Implementation:**
```python
df['pvo'] = ta.pvo(df['volume'], fast=12, slow=26)
```

---

### 4.3 PPO (Percentage Price Oscillator)
- **Field:** `ppo`
- **Type:** FLOAT64
- **Purpose:** Similar to MACD but in percentage terms

**Formula:**
```
PPO = (EMA(Close, Fast) - EMA(Close, Slow)) / EMA(Close, Slow) × 100

where Fast = 12, Slow = 26 (default)
```

**Interpretation:**
- **PPO > 0:** Short-term EMA above long-term (bullish)
- **PPO < 0:** Short-term EMA below long-term (bearish)
- **PPO crosses above zero:** Buy signal
- **PPO crosses below zero:** Sell signal
- **Better for comparing different price levels** than MACD

**pandas_ta Implementation:**
```python
df['ppo'] = ta.ppo(df['close'], fast=12, slow=26)
```

---

## 5. ADVANCED OSCILLATORS (2 fields)

### 5.1 Ultimate Oscillator
- **Field:** `ultimate_osc`
- **Type:** FLOAT64
- **Range:** 0-100
- **Purpose:** Multi-timeframe momentum oscillator (combines 7, 14, 28 periods)

**Formula:**
```
Buying Pressure (BP) = Close - min(Low, Close(prev))
True Range (TR) = max(High, Close(prev)) - min(Low, Close(prev))

Average7 = Sum(BP, 7) / Sum(TR, 7)
Average14 = Sum(BP, 14) / Sum(TR, 14)
Average28 = Sum(BP, 28) / Sum(TR, 28)

UO = 100 × [(4 × Average7) + (2 × Average14) + Average28] / (4 + 2 + 1)
```

**Interpretation:**
- **UO > 70:** Overbought
- **UO < 30:** Oversold
- **Bullish Divergence:** Price makes lower low, UO makes higher low (buy signal)
- **Bearish Divergence:** Price makes higher high, UO makes lower high (sell signal)

**pandas_ta Implementation:**
```python
df['ultimate_osc'] = ta.uo(df['high'], df['low'], df['close'])
```

---

### 5.2 Awesome Oscillator
- **Field:** `awesome_osc`
- **Type:** FLOAT64
- **Purpose:** Momentum indicator comparing recent to overall market momentum

**Formula:**
```
Median Price = (High + Low) / 2

AO = SMA(Median Price, 5) - SMA(Median Price, 34)
```

**Interpretation:**
- **AO > 0:** Bullish momentum (short-term > long-term)
- **AO < 0:** Bearish momentum (short-term < long-term)
- **AO crosses above zero:** Buy signal
- **AO crosses below zero:** Sell signal
- **Twin Peaks:** Two consecutive peaks above/below zero line

**Trading Signals:**
- **Saucer:** AO changes direction (3 bars pattern)
- **Zero Line Cross:** Momentum shift
- **Twin Peaks:** Divergence pattern

**pandas_ta Implementation:**
```python
df['awesome_osc'] = ta.ao(df['high'], df['low'])
```

---

## 6. ML FEATURES - RETURNS (3 fields)

### 6.1 Log Return
- **Field:** `log_return`
- **Type:** FLOAT64
- **Purpose:** Daily logarithmic return (better for statistical analysis)

**Formula:**
```
Log Return = ln(Close(today) / Close(yesterday))

where ln is natural logarithm
```

**Why Log Returns:**
- **Additive:** Sum of log returns = log return of total period
- **Symmetric:** +10% and -10% are equidistant
- **Normally distributed:** Better for statistical models
- **Time consistency:** Can compare across different periods

**Interpretation:**
- **Log Return > 0:** Price increased
- **Log Return < 0:** Price decreased
- **Magnitude:** Indicates size of price change
- **Convert to %:** e^(log_return) - 1

**Implementation:**
```python
df['log_return'] = np.log(df['close'] / df['close'].shift(1))
```

---

### 6.2 Forward Returns
- **Fields:** `return_2w`, `return_4w`
- **Type:** FLOAT64
- **Purpose:** Future price change (for ML target variables)

**Formula:**
```
return_2w = (Close(10 days ahead) - Close(today)) / Close(today) × 100
return_4w = (Close(20 days ahead) - Close(today)) / Close(today) × 100
```

**Purpose:**
- **ML Training Labels:** Predict future returns
- **2-week outlook:** Short-term trend prediction
- **4-week outlook:** Medium-term trend prediction
- **Strategy backtesting:** Evaluate entry timing

**Implementation:**
```python
df['return_2w'] = (df['close'].shift(-10) - df['close']) / df['close'] * 100
df['return_4w'] = (df['close'].shift(-20) - df['close']) / df['close'] * 100
```

---

## 7. ML FEATURES - RELATIVE POSITIONS (3 fields)

### 7.1 Price vs Moving Averages
- **Fields:** `close_vs_sma20_pct`, `close_vs_sma50_pct`, `close_vs_sma200_pct`
- **Type:** FLOAT64
- **Purpose:** Price position relative to key moving averages

**Formula:**
```
close_vs_sma20_pct = (Close - SMA20) / SMA20 × 100
close_vs_sma50_pct = (Close - SMA50) / SMA50 × 100
close_vs_sma200_pct = (Close - SMA200) / SMA200 × 100
```

**Interpretation:**

**Positive Values (Price above MA):**
- **0-2%:** Slightly above, testing support
- **2-5%:** Healthy uptrend
- **5-10%:** Strong uptrend
- **>10%:** Extended, potential pullback

**Negative Values (Price below MA):**
- **0 to -2%:** Slightly below, testing resistance
- **-2% to -5%:** Downtrend
- **-5% to -10%:** Strong downtrend
- **< -10%:** Oversold, potential bounce

**Trading Signals:**
- **All three positive:** Strong bullish trend
- **All three negative:** Strong bearish trend
- **Price crosses SMA20:** Short-term trend change
- **Price crosses SMA200:** Major trend change

**Implementation:**
```python
df['close_vs_sma20_pct'] = (df['close'] - df['sma_20']) / df['sma_20'] * 100
df['close_vs_sma50_pct'] = (df['close'] - df['sma_50']) / df['sma_50'] * 100
df['close_vs_sma200_pct'] = (df['close'] - df['sma_200']) / df['sma_200'] * 100
```

---

## 8. ML FEATURES - INDICATOR DYNAMICS (11 fields)

### 8.1 RSI Slope
- **Field:** `rsi_slope`
- **Type:** FLOAT64
- **Purpose:** Rate of change of RSI (momentum of momentum)

**Formula:**
```
rsi_slope = RSI(today) - RSI(5 days ago)
```

**Interpretation:**
- **Positive slope:** RSI increasing, momentum building
- **Negative slope:** RSI decreasing, momentum fading
- **Slope approaching zero:** Momentum stabilizing
- **Large absolute values:** Rapid momentum change

**Implementation:**
```python
df['rsi_slope'] = df['rsi'].diff(5)
```

---

### 8.2 RSI Z-Score
- **Field:** `rsi_zscore`
- **Type:** FLOAT64
- **Purpose:** Normalized RSI position relative to recent mean

**Formula:**
```
RSI Mean = Rolling Mean of RSI (20 periods)
RSI Std = Rolling Standard Deviation of RSI (20 periods)

rsi_zscore = (RSI - RSI Mean) / RSI Std
```

**Interpretation:**
- **Z > 2:** RSI extremely high relative to recent range
- **Z > 1:** RSI high, above normal
- **Z = 0:** RSI at recent average
- **Z < -1:** RSI low, below normal
- **Z < -2:** RSI extremely low relative to recent range

**Implementation:**
```python
df['rsi_zscore'] = (df['rsi'] - df['rsi'].rolling(20).mean()) / df['rsi'].rolling(20).std()
```

---

### 8.3 RSI Overbought/Oversold Flags
- **Fields:** `rsi_overbought`, `rsi_oversold`
- **Type:** INT64
- **Values:** 0 or 1
- **Purpose:** Binary flags for extreme RSI levels

**Formula:**
```
rsi_overbought = 1 if RSI > 70, else 0
rsi_oversold = 1 if RSI < 30, else 0
```

**Interpretation:**
- **rsi_overbought = 1:** Stock in overbought territory
- **rsi_oversold = 1:** Stock in oversold territory
- **Both = 0:** RSI in normal range (30-70)

**Implementation:**
```python
df['rsi_overbought'] = (df['rsi'] > 70).astype('Int64')
df['rsi_oversold'] = (df['rsi'] < 30).astype('Int64')
```

---

### 8.4 MACD Cross Signal
- **Field:** `macd_cross`
- **Type:** INT64
- **Values:** -1, 0, or 1
- **Purpose:** Detects MACD crossover events

**Formula:**
```
If MACD crosses above Signal (bullish):
    macd_cross = 1

If MACD crosses below Signal (bearish):
    macd_cross = -1

Otherwise:
    macd_cross = 0
```

**Interpretation:**
- **+1:** Bullish crossover (buy signal)
- **-1:** Bearish crossover (sell signal)
- **0:** No crossover

**Implementation:**
```python
df['macd_cross'] = np.where(
    (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1)), 1,
    np.where((df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1)), -1, 0)
)
df['macd_cross'] = df['macd_cross'].astype('Int64')
```

---

### 8.5 EMA Slopes
- **Fields:** `ema20_slope`, `ema50_slope`
- **Type:** FLOAT64
- **Purpose:** Rate of change of EMAs (trend direction and strength)

**Formula:**
```
ema20_slope = EMA20(today) - EMA20(5 days ago)
ema50_slope = EMA50(today) - EMA50(5 days ago)
```

**Interpretation:**
- **Positive slope:** Uptrend
- **Negative slope:** Downtrend
- **Slope magnitude:** Trend strength
- **Slope approaching zero:** Trend weakening
- **Both slopes positive:** Strong uptrend
- **Both slopes negative:** Strong downtrend

**Implementation:**
```python
df['ema20_slope'] = df['ema_20'].diff(5)
df['ema50_slope'] = df['ema_50'].diff(5)
```

---

### 8.6 ATR Z-Score
- **Field:** `atr_zscore`
- **Type:** FLOAT64
- **Purpose:** Normalized ATR position (volatility regime detection)

**Formula:**
```
ATR Mean = Rolling Mean of ATR (20 periods)
ATR Std = Rolling Standard Deviation of ATR (20 periods)

atr_zscore = (ATR - ATR Mean) / ATR Std
```

**Interpretation:**
- **Z > 2:** Extremely high volatility
- **Z > 1:** Above-normal volatility
- **Z = 0:** Normal volatility
- **Z < -1:** Below-normal volatility (calm market)

**Implementation:**
```python
df['atr_zscore'] = (df['atr'] - df['atr'].rolling(20).mean()) / df['atr'].rolling(20).std()
```

---

### 8.7 ATR Slope
- **Field:** `atr_slope`
- **Type:** FLOAT64
- **Purpose:** Rate of change of volatility

**Formula:**
```
atr_slope = ATR(today) - ATR(5 days ago)
```

**Interpretation:**
- **Positive slope:** Volatility expanding
- **Negative slope:** Volatility contracting
- **Large positive:** Potential breakout or panic
- **Large negative:** Market calming down

**Implementation:**
```python
df['atr_slope'] = df['atr'].diff(5)
```

---

### 8.8 Volume Z-Score
- **Field:** `volume_zscore`
- **Type:** FLOAT64
- **Purpose:** Normalized volume position

**Formula:**
```
Volume Mean = Rolling Mean of Volume (20 periods)
Volume Std = Rolling Standard Deviation of Volume (20 periods)

volume_zscore = (Volume - Volume Mean) / Volume Std
```

**Interpretation:**
- **Z > 2:** Extremely high volume (potential breakout/breakdown)
- **Z > 1:** Above-average volume
- **Z = 0:** Normal volume
- **Z < -1:** Below-average volume (low interest)

**Implementation:**
```python
df['volume_zscore'] = (df['volume'] - df['volume'].rolling(20).mean()) / df['volume'].rolling(20).std()
```

---

### 8.9 Volume Ratio
- **Field:** `volume_ratio`
- **Type:** FLOAT64
- **Purpose:** Current volume vs 50-day average

**Formula:**
```
volume_ratio = Volume(today) / Average Volume(50 days)
```

**Interpretation:**
- **Ratio > 2:** Very high volume (2x normal)
- **Ratio 1-2:** Above-average volume
- **Ratio = 1:** Normal volume
- **Ratio 0.5-1:** Below-average volume
- **Ratio < 0.5:** Very low volume

**Implementation:**
```python
df['volume_ratio'] = df['volume'] / df['average_volume']
```

---

## 9. ML FEATURES - MARKET STRUCTURE (4 fields)

### 9.1 Pivot High Flag
- **Field:** `pivot_high_flag`
- **Type:** INT64
- **Values:** 0 or 1
- **Purpose:** Identifies local peaks (resistance levels)

**Formula:**
```
pivot_high_flag = 1 if:
    High(today) > High(yesterday) AND
    High(today) > High(2 days ago) AND
    High(today) > High(tomorrow) AND
    High(today) > High(2 days ahead)

Otherwise: 0
```

**Interpretation:**
- **1:** Local high point (potential resistance)
- **0:** Not a pivot high
- **Use:** Identify swing highs, resistance levels, chart patterns

**Implementation:**
```python
df['pivot_high_flag'] = ((df['high'] > df['high'].shift(1)) &
                          (df['high'] > df['high'].shift(2)) &
                          (df['high'] > df['high'].shift(-1)) &
                          (df['high'] > df['high'].shift(-2))).astype('Int64')
```

---

### 9.2 Pivot Low Flag
- **Field:** `pivot_low_flag`
- **Type:** INT64
- **Values:** 0 or 1
- **Purpose:** Identifies local troughs (support levels)

**Formula:**
```
pivot_low_flag = 1 if:
    Low(today) < Low(yesterday) AND
    Low(today) < Low(2 days ago) AND
    Low(today) < Low(tomorrow) AND
    Low(today) < Low(2 days ahead)

Otherwise: 0
```

**Interpretation:**
- **1:** Local low point (potential support)
- **0:** Not a pivot low
- **Use:** Identify swing lows, support levels, reversal points

**Implementation:**
```python
df['pivot_low_flag'] = ((df['low'] < df['low'].shift(1)) &
                         (df['low'] < df['low'].shift(2)) &
                         (df['low'] < df['low'].shift(-1)) &
                         (df['low'] < df['low'].shift(-2))).astype('Int64')
```

---

### 9.3 Distance to Pivot High
- **Field:** `dist_to_pivot_high`
- **Type:** FLOAT64
- **Purpose:** Price distance from last pivot high (resistance)

**Formula:**
```
Last Pivot High = Most recent high where pivot_high_flag = 1
dist_to_pivot_high = Close(today) - Last Pivot High
```

**Interpretation:**
- **Negative value:** Price below last pivot high (resistance overhead)
- **Zero:** Price at last pivot high (testing resistance)
- **Positive value:** Price above last pivot high (breakout)
- **Large negative:** Far from resistance
- **Small negative:** Near resistance

**Implementation:**
```python
df['dist_to_pivot_high'] = df['close'] - df['high'].where(df['pivot_high_flag'] == 1).ffill()
```

---

### 9.4 Distance to Pivot Low
- **Field:** `dist_to_pivot_low`
- **Type:** FLOAT64
- **Purpose:** Price distance from last pivot low (support)

**Formula:**
```
Last Pivot Low = Most recent low where pivot_low_flag = 1
dist_to_pivot_low = Close(today) - Last Pivot Low
```

**Interpretation:**
- **Positive value:** Price above last pivot low (support holding)
- **Zero:** Price at last pivot low (testing support)
- **Negative value:** Price below last pivot low (breakdown)
- **Large positive:** Far from support
- **Small positive:** Near support

**Implementation:**
```python
df['dist_to_pivot_low'] = df['close'] - df['low'].where(df['pivot_low_flag'] == 1).ffill()
```

---

## 10. ML FEATURES - REGIME DETECTION (3 fields)

### 10.1 Trend Regime
- **Field:** `trend_regime`
- **Type:** INT64
- **Values:** -1, 0, or 1
- **Purpose:** Classifies market as uptrend, downtrend, or neutral

**Formula:**
```
SMA50 Slope = SMA50(today) - SMA50(20 days ago)

trend_regime = 1 if SMA50 Slope > 0 (uptrend)
trend_regime = -1 if SMA50 Slope < 0 (downtrend)
trend_regime = 0 if SMA50 Slope = 0 (neutral)
```

**Interpretation:**
- **+1:** Uptrend regime (bullish environment)
- **-1:** Downtrend regime (bearish environment)
- **0:** Neutral/sideways regime

**Trading Application:**
- **+1:** Favor long positions, buy dips
- **-1:** Favor short positions or stay out
- **0:** Range-bound strategies, mean reversion

**Implementation:**
```python
sma_50_slope = df['sma_50'].diff(20)
df['trend_regime'] = np.where(sma_50_slope > 0, 1, np.where(sma_50_slope < 0, -1, 0))
df['trend_regime'] = df['trend_regime'].astype('Int64')
```

---

### 10.2 Volatility Regime
- **Field:** `vol_regime`
- **Type:** INT64
- **Values:** 0 or 1
- **Purpose:** Classifies market volatility as high or low

**Formula:**
```
ATR 20-day Mean = Rolling Mean of ATR (20 periods)

vol_regime = 1 if ATR > ATR 20-day Mean (high volatility)
vol_regime = 0 if ATR <= ATR 20-day Mean (low volatility)
```

**Interpretation:**
- **1:** High volatility regime (larger price swings)
- **0:** Low volatility regime (smaller price swings)

**Trading Application:**
- **vol_regime = 1:** Widen stops, reduce position size, expect larger moves
- **vol_regime = 0:** Tighten stops, normal position size, expect smaller moves

**Implementation:**
```python
atr_20_mean = df['atr'].rolling(20).mean()
df['vol_regime'] = (df['atr'] > atr_20_mean).astype('Int64')
```

---

### 10.3 Regime Confidence
- **Field:** `regime_confidence`
- **Type:** FLOAT64
- **Purpose:** Confidence level of trend regime classification

**Formula:**
```
SMA50 Slope = SMA50(today) - SMA50(20 days ago)
SMA50 Std = Rolling Standard Deviation of SMA50 (20 periods)

regime_confidence = |SMA50 Slope| / SMA50 Std
```

**Interpretation:**
- **High value (>2):** Strong, clear trend
- **Medium value (1-2):** Moderate trend
- **Low value (<1):** Weak or uncertain trend
- **Very low (<0.5):** No clear trend, choppy market

**Trading Application:**
- **High confidence:** Trust trend signals, follow trend
- **Low confidence:** Be cautious, consider range-bound strategies

**Implementation:**
```python
sma_50_slope = df['sma_50'].diff(20)
df['regime_confidence'] = abs(sma_50_slope) / df['sma_50'].rolling(20).std()
```

---

## IMPLEMENTATION NOTES

### Minimum Data Requirements

For accurate indicator calculation, minimum historical data points required:

| Indicator | Minimum Days |
|-----------|-------------|
| RSI (14) | 14 |
| MACD (12,26,9) | 35 |
| SMA 20 | 20 |
| SMA 50 | 50 |
| SMA 200 | 200 |
| EMA 200 | 200 |
| Bollinger Bands (20) | 20 |
| ADX (14) | 14 |
| ATR (14) | 14 |
| Stochastic (14,3) | 17 |
| All ML Features | 200 |

**Recommendation:** Require minimum 200 days of data for complete indicator suite.

---

### Error Handling

**Common Issues:**

1. **Insufficient Data:**
   - Early rows (<200 days) will have NULL for some indicators
   - This is normal and expected
   - Solution: Only use data points with sufficient history

2. **pandas_ta Column Naming:**
   - pandas_ta may return different column names than expected
   - Solution: Use positional indexing (`.iloc[:, 0]`) instead of named columns
   - Example: `macd_result.iloc[:, 0]` instead of `macd_result['MACD']`

3. **Data Type Conversion:**
   - Integer indicators (flags, regimes) need explicit casting
   - Use `.astype('Int64')` for nullable integers
   - Example: `df['rsi_overbought'] = (df['rsi'] > 70).astype('Int64')`

4. **Division by Zero:**
   - Can occur with z-scores when standard deviation = 0
   - pandas handles gracefully with NaN
   - Filter out inf/NaN before BigQuery upload if needed

---

### Performance Optimization

For large datasets (1M+ rows):

1. **Process by Symbol:**
   - Fetch and calculate indicators per symbol
   - Prevents memory issues
   - Enables parallel processing

2. **Batch Updates:**
   - Use temp tables for calculation
   - MERGE back to main table
   - Drop temp tables after

3. **Index Strategy:**
   - Partition by MONTH (not DAY for 27 years)
   - Cluster by: symbol, sector, exchange
   - Speeds up symbol-specific queries

---

### Validation Queries

**Check Overall Completion:**
```sql
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT symbol) as symbols,
    COUNTIF(rsi IS NOT NULL) * 100.0 / COUNT(*) as rsi_pct,
    COUNTIF(macd IS NOT NULL) * 100.0 / COUNT(*) as macd_pct,
    COUNTIF(sma_200 IS NOT NULL) * 100.0 / COUNT(*) as sma200_pct
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`;
```

**Check Sample Data:**
```sql
SELECT
    datetime, symbol, close,
    rsi, macd, sma_50, sma_200,
    bollinger_upper, bollinger_lower,
    trend_regime, vol_regime
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE symbol = 'AAPL'
ORDER BY datetime DESC
LIMIT 10;
```

**Find Missing Indicators:**
```sql
SELECT
    symbol,
    COUNT(*) as total_rows,
    COUNTIF(rsi IS NULL) as missing_rsi
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
GROUP BY symbol
HAVING missing_rsi > 0
ORDER BY missing_rsi DESC;
```

---

## SUMMARY TABLE

| Category | Count | Fields |
|----------|-------|--------|
| **Momentum Indicators** | 9 | rsi, macd, macd_signal, macd_histogram, stoch_k, stoch_d, cci, williams_r, momentum |
| **Moving Averages** | 9 | sma_20, sma_50, sma_200, ema_12, ema_20, ema_26, ema_50, ema_200, kama |
| **Trend & Volatility** | 10 | bollinger_upper, bollinger_middle, bollinger_lower, bb_width, adx, plus_di, minus_di, atr, trix, roc |
| **Volume Indicators** | 3 | obv, pvo, ppo |
| **Advanced Oscillators** | 2 | ultimate_osc, awesome_osc |
| **ML - Returns** | 3 | log_return, return_2w, return_4w |
| **ML - Relative Positions** | 3 | close_vs_sma20_pct, close_vs_sma50_pct, close_vs_sma200_pct |
| **ML - Indicator Dynamics** | 11 | rsi_slope, rsi_zscore, rsi_overbought, rsi_oversold, macd_cross, ema20_slope, ema50_slope, atr_zscore, atr_slope, volume_zscore, volume_ratio |
| **ML - Market Structure** | 4 | pivot_high_flag, pivot_low_flag, dist_to_pivot_high, dist_to_pivot_low |
| **ML - Regime Detection** | 3 | trend_regime, vol_regime, regime_confidence |
| **TOTAL** | **58** | All technical indicators and ML features |

---

## NEXT STEPS

After indicator calculation completes:

1. **Validate Data:**
   - Run validation queries
   - Check sample symbols (AAPL, MSFT, GOOGL)
   - Verify >99% completion rate

2. **Update APIs:**
   - Modify endpoints to use `stocks_daily_clean`
   - Add indicator-based screening
   - Implement technical analysis queries

3. **Update Frontend:**
   - Display indicators on charts
   - Add technical indicator overlays
   - Implement screener based on indicators

4. **ML Model Training:**
   - Use 27 years of indicator data
   - Train price prediction models
   - Backtest trading strategies

5. **Expand Coverage:**
   - Add Russell 2000 symbols (~2000 more)
   - Add liquid ETFs (~100 more)
   - Complete S&P 500 coverage

---

**Document Version:** 1.0
**Date:** December 9, 2025
**Status:** Reference documentation complete, indicator calculation pending fix

---

**END OF TECHNICAL INDICATORS REFERENCE**
