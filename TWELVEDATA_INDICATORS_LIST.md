# TwelveData Technical Indicators - Complete List

This document provides a comprehensive numbered list of all technical indicators and parameters available from TwelveData.com API.

## Category 1: Overlap Studies (21 Indicators)

1. **BBANDS** - Bollinger Bands - Shows volatility bands above and below a moving average
2. **DEMA** - Double Exponential Moving Average - Reduces lag compared to traditional EMA
3. **EMA** - Exponential Moving Average - Weighted moving average giving more weight to recent prices
4. **HT_TRENDLINE** - Hilbert Transform Instantaneous Trendline - Identifies trend direction
5. **ICHIMOKU** - Ichimoku Cloud - Japanese charting technique showing support/resistance
6. **KAMA** - Kaufman Adaptive Moving Average - Adapts to market volatility
7. **KELTNER** - Keltner Channel - Volatility-based envelope set above and below EMA
8. **MA** - Moving Average - Generic moving average indicator
9. **MAMA** - MESA Adaptive Moving Average - Adapts to price movements
10. **MCGINLEY** - McGinley Dynamic - Smooths price data with minimal lag
11. **MIDPOINT** - Midpoint - Calculates midpoint of highest and lowest values
12. **MIDPRICE** - Midprice - Average of high and low prices
13. **PIVOT_POINTS_HL** - Pivot Points (High/Low) - Support and resistance levels
14. **SAR** - Parabolic SAR - Stop and reverse indicator for trends
15. **SAREXT** - Parabolic SAR Extended - Extended version with more parameters
16. **SMA** - Simple Moving Average - Average price over specified period
17. **T3MA** - Triple Exponential Moving Average (T3) - Smooth moving average
18. **TEMA** - Triple Exponential Moving Average - Reduces lag in trend identification
19. **TRIMA** - Triangular Moving Average - Double-smoothed simple moving average
20. **VWAP** - Volume Weighted Average Price - Average price weighted by volume
21. **WMA** - Weighted Moving Average - Assigns more weight to recent data

## Category 2: Momentum Indicators (35 Indicators)

22. **ADX** - Average Directional Index - Measures trend strength (0-100)
23. **ADXR** - Average Directional Movement Rating - Smoothed version of ADX
24. **APO** - Absolute Price Oscillator - Difference between two EMAs
25. **AROON** - Aroon Indicator - Identifies trend changes and strength
26. **AROONOSC** - Aroon Oscillator - Difference between Aroon Up and Down
27. **BOP** - Balance of Power - Measures buying vs selling pressure
28. **CCI** - Commodity Channel Index - Identifies cyclical trends
29. **CMO** - Chande Momentum Oscillator - Measures momentum
30. **COPPOCK** - Coppock Curve - Long-term momentum indicator
31. **CRSI** - Connors RSI - Composite RSI indicator
32. **DPO** - Detrended Price Oscillator - Removes trend to identify cycles
33. **DX** - Directional Movement Index - Measures directional movement
34. **KST** - Know Sure Thing - Momentum oscillator based on ROC
35. **MACD** - Moving Average Convergence Divergence - Trend-following momentum
36. **MACD_SLOPE** - MACD Slope - Rate of change of MACD
37. **MACDEXT** - MACD Extended - MACD with customizable moving averages
38. **MFI** - Money Flow Index - Volume-weighted RSI
39. **MINUS_DI** - Minus Directional Indicator - Measures downward movement
40. **MINUS_DM** - Minus Directional Movement - Raw downward movement
41. **MOM** - Momentum - Rate of price change
42. **PERCENT_B** - Percent B - Position within Bollinger Bands
43. **PLUS_DI** - Plus Directional Indicator - Measures upward movement
44. **PLUS_DM** - Plus Directional Movement - Raw upward movement
45. **PPO** - Percentage Price Oscillator - MACD expressed as percentage
46. **ROC** - Rate of Change - Percentage change between current and past price
47. **ROCP** - Rate of Change Percentage - ROC as decimal
48. **ROCR** - Rate of Change Ratio - Ratio of current to past price
49. **ROCR100** - Rate of Change Ratio 100 - ROCR scaled by 100
50. **RSI** - Relative Strength Index - Momentum oscillator (0-100)
51. **STOCH** - Stochastic Oscillator - Compares closing price to price range
52. **STOCHF** - Stochastic Fast - Fast version of stochastic
53. **STOCHRSI** - Stochastic RSI - RSI values applied to stochastic formula
54. **ULTOSC** - Ultimate Oscillator - Multi-timeframe momentum
55. **WILLR** - Williams %R - Momentum indicator comparing close to high-low range

## Category 3: Volume Indicators (4 Indicators)

56. **AD** - Accumulation/Distribution - Measures cumulative money flow
57. **ADOSC** - Accumulation/Distribution Oscillator - Momentum of A/D line
58. **OBV** - On-Balance Volume - Cumulative volume indicator
59. **RVOL** - Relative Volume - Current volume compared to average

## Category 4: Volatility Indicators (5 Indicators)

60. **ATR** - Average True Range - Measures market volatility
61. **NATR** - Normalized Average True Range - ATR as percentage of close
62. **SUPERTREND** - Supertrend - Trend-following indicator
63. **SUPERTREND_HEIKINASHI** - Supertrend Heikin Ashi - Supertrend with HA candles
64. **TRANGE** - True Range - Single-period volatility measure

## Category 5: Price Transform (19 Indicators)

65. **ADD** - Addition - Adds two series together
66. **AVG** - Average - Averages multiple series
67. **AVGPRICE** - Average Price - Average of OHLC prices
68. **CEIL** - Ceiling - Rounds up to nearest integer
69. **DIV** - Division - Divides one series by another
70. **EXP** - Exponential - Calculates exponential of values
71. **FLOOR** - Floor - Rounds down to nearest integer
72. **HEIKINASHICANDLES** - Heikin Ashi Candles - Smoothed candlestick chart
73. **HLC3** - HLC3 - Average of High, Low, Close
74. **LN** - Natural Logarithm - Calculates natural log
75. **LOG10** - Logarithm Base 10 - Calculates log base 10
76. **MEDPRICE** - Median Price - Average of high and low
77. **MULT** - Multiplication - Multiplies series together
78. **SQRT** - Square Root - Calculates square root
79. **SUB** - Subtraction - Subtracts one series from another
80. **SUM** - Summation - Running sum over period
81. **TYPPRICE** - Typical Price - Average of HLC
82. **WCLPRICE** - Weighted Close Price - Weighted average emphasizing close

## Category 6: Cycle Indicators (5 Indicators)

83. **HT_DCPERIOD** - Hilbert Transform Dominant Cycle Period - Identifies dominant cycle
84. **HT_DCPHASE** - Hilbert Transform Dominant Cycle Phase - Phase of dominant cycle
85. **HT_PHASOR** - Hilbert Transform Phasor Components - In-phase and quadrature components
86. **HT_SINE** - Hilbert Transform Sine Wave - Sine of phase angle
87. **HT_TRENDMODE** - Hilbert Transform Trend vs Cycle Mode - Identifies trend or cycle

## Category 7: Statistic Functions (16 Indicators)

88. **BETA** - Beta - Measures volatility relative to market
89. **CORREL** - Correlation Coefficient - Measures correlation between series
90. **LINEARREG** - Linear Regression - Best-fit straight line
91. **LINEARREG_ANGLE** - Linear Regression Angle - Angle of regression line
92. **LINEARREG_INTERCEPT** - Linear Regression Intercept - Y-intercept of regression
93. **LINEARREG_SLOPE** - Linear Regression Slope - Slope of regression line
94. **MAX** - Maximum - Highest value over period
95. **MAXINDEX** - Maximum Index - Index of highest value
96. **MIN** - Minimum - Lowest value over period
97. **MININDEX** - Minimum Index - Index of lowest value
98. **MINMAX** - Min Max - Both minimum and maximum values
99. **MINMAXINDEX** - Min Max Index - Indices of min and max values
100. **STDDEV** - Standard Deviation - Measures price dispersion
101. **TSF** - Time Series Forecast - Projects future values
102. **VAR** - Variance - Squared standard deviation

## Category 8: Pattern Recognition (Coming Soon)

103. **CDL_DOJI** - Doji Candlestick Pattern
104. **CDL_ENGULFING** - Engulfing Pattern
105. **CDL_HAMMER** - Hammer Pattern
106. **CDL_MORNINGSTAR** - Morning Star Pattern
107. **CDL_EVENINGSTAR** - Evening Star Pattern
(Additional candlestick patterns available)

## Common Parameters for All Indicators

| Parameter | Description | Example Values |
|-----------|-------------|----------------|
| symbol | Stock/Crypto ticker | AAPL, BTC/USD |
| interval | Time interval | 1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 1day, 1week, 1month |
| exchange | Exchange name | NYSE, NASDAQ, BINANCE |
| country | Country code | US, UK, JP |
| outputsize | Number of data points | 1-5000 |
| format | Response format | JSON, CSV |
| dp | Decimal places | 2, 4, 6 |
| timezone | Timezone | America/New_York, UTC |

## Indicator-Specific Parameters

### Moving Averages (SMA, EMA, WMA, etc.)
- time_period: Number of periods (default: 14)
- series_type: Price type (open, high, low, close)

### RSI
- time_period: Number of periods (default: 14)
- series_type: Price type (default: close)

### MACD
- fast_period: Fast EMA period (default: 12)
- slow_period: Slow EMA period (default: 26)
- signal_period: Signal line period (default: 9)
- series_type: Price type (default: close)

### Bollinger Bands
- time_period: Number of periods (default: 20)
- sd: Standard deviation multiplier (default: 2)
- ma_type: Moving average type (SMA, EMA, etc.)
- series_type: Price type (default: close)

### Stochastic
- fast_k_period: Fast K period (default: 14)
- slow_k_period: Slow K period (default: 3)
- slow_d_period: Slow D period (default: 3)
- slow_kma_type: Slow K MA type (default: SMA)
- slow_dma_type: Slow D MA type (default: SMA)

### ADX
- time_period: Number of periods (default: 14)

### ATR
- time_period: Number of periods (default: 14)

### CCI
- time_period: Number of periods (default: 20)

### Ichimoku Cloud
- conversion_line_period: Tenkan-sen (default: 9)
- base_line_period: Kijun-sen (default: 26)
- leading_span_b_period: Senkou Span B (default: 52)
- lagging_span_period: Chikou Span (default: 26)
- include_ahead_span_period: Include future cloud (default: true)

## API Endpoint Examples

### Get RSI for AAPL
```
GET /rsi?symbol=AAPL&interval=1day&time_period=14
```

### Get MACD for Bitcoin
```
GET /macd?symbol=BTC/USD&interval=1h&fast_period=12&slow_period=26&signal_period=9
```

### Get Bollinger Bands for Tesla
```
GET /bbands?symbol=TSLA&interval=4h&time_period=20&sd=2
```

### Get Multiple Indicators
```
GET /time_series?symbol=AAPL&interval=1day&indicators=rsi,macd,sma:20,ema:50
```

## Summary

- **Total Indicators: 102+** (with more being added regularly)
- **Categories: 8** major groupings
- **Timeframes: 12** intervals from 1-minute to monthly
- **Asset Classes: 6** (Stocks, Crypto, Forex, ETFs, Indices, Commodities)
- **Global Coverage: 50+** exchanges worldwide

For the most up-to-date list, use the `/technical_indicators` endpoint which returns metadata for all available indicators.
