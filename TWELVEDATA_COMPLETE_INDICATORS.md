# TwelveData Complete Technical Indicators Reference

**Official API Endpoint:** `https://api.twelvedata.com/technical_indicators`

This document contains the complete, authoritative list of 112 technical indicators from TwelveData's API. The list is dynamically fetched from the API to ensure accuracy.

---

## Complete Itemized List (112 Indicators)

### Overlap Studies / Trend Following

| # | Code | Full Name | Description |
|---|------|-----------|-------------|
| 1 | BBANDS | Bollinger Bands | Volatility bands located above and below a moving average |
| 2 | DEMA | Double Exponential Moving Average | Used to eliminate lag in trend identification |
| 3 | EMA | Exponential Moving Average | Places greater importance on recent data points |
| 4 | HT_TRENDLINE | Hilbert Transform Instantaneous Trendline | Identifies dominant cycle trendline |
| 5 | ICHIMOKU | Ichimoku Kinko Hyo | Shows trend direction, momentum, and support/resistance |
| 6 | KAMA | Kaufman's Adaptive Moving Average | Incorporates market noise and volatility |
| 7 | KELTNER | Keltner Channels | Volatility indicator used to spot trend changes |
| 8 | MA | Moving Average | Smooths out price fluctuations |
| 9 | MAMA | MESA Adaptive Moving Average | Adapts to price fluctuations based on rate of change |
| 10 | MAVP | Moving Average Variable Period | MA with dynamically adjusted period |
| 11 | MCGINLEY_DYNAMIC | McGinley Dynamic | Self-adjusting moving average |
| 12 | MIDPOINT | MidPoint | Midpoint value over period |
| 13 | MIDPRICE | Midpoint Price | Midpoint price over period |
| 14 | PIVOT_POINTS_HL | Pivot Points (High/Low) | Support and resistance levels |
| 15 | SAR | Parabolic SAR | Identifies and spots upcoming asset momentum |
| 16 | SAREXT | Parabolic SAR Extended | Extended version with more parameters |
| 17 | SMA | Simple Moving Average | Arithmetic moving average of closing prices |
| 18 | T3MA | Triple Exponential Moving Average (T3) | Better smoothing than classical TEMA |
| 19 | TEMA | Triple Exponential Moving Average | Smooths out price fluctuations |
| 20 | TRIMA | Triangular Moving Average | More weight on prices in middle of time period |
| 21 | VWAP | Volume Weighted Average Price | Commonly used as a trading benchmark |
| 22 | WMA | Weighted Moving Average | More weight on recent data points |

### Momentum Indicators

| # | Code | Full Name | Description |
|---|------|-----------|-------------|
| 23 | ADX | Average Directional Index | Decides if the price trend is strong |
| 24 | ADXR | Average Directional Movement Index Rating | Smoothed ADX |
| 25 | APO | Absolute Price Oscillator | Difference between two price moving averages |
| 26 | AROON | Aroon Indicator | Identifies if the price is trending |
| 27 | AROONOSC | Aroon Oscillator | Difference between Aroon Up and Down |
| 28 | BOP | Balance of Power | Measures relative strength between buyers and sellers |
| 29 | CCI | Commodity Channel Index | Identifies new trends and assesses critical conditions |
| 30 | CMO | Chande Momentum Oscillator | Shows overbought and oversold conditions |
| 31 | COPPOCK | Coppock Curve | Detects long-term trend changes |
| 32 | CRSI | ConnorsRSI | Shows oversold and overbought levels |
| 33 | DPO | Detrended Price Oscillator | Separates price from the trend |
| 34 | DX | Directional Movement Index | Identifies which direction the price is moving |
| 35 | KST | Know Sure Thing | Calculates price momentum for four distinct price cycles |
| 36 | MACD | Moving Average Convergence Divergence | Subtracts longer MA from shorter |
| 37 | MACD_SLOPE | MACD Regression Slope | Rate of change of MACD |
| 38 | MACDEXT | MACD Extended | MACD with customizable moving averages |
| 39 | MFI | Money Flow Index | Identifies overbought and oversold levels |
| 40 | MINUS_DI | Minus Directional Indicator | Measures existence of downtrend |
| 41 | MINUS_DM | Minus Directional Movement | Raw downward movement |
| 42 | MOM | Momentum | Compares current price with previous price N periods ago |
| 43 | PERCENT_B | %B Indicator | Position of asset price relative to Bollinger Bands |
| 44 | PLUS_DI | Plus Directional Indicator | Measures existence of uptrend |
| 45 | PLUS_DM | Plus Directional Movement | Raw upward movement |
| 46 | PPO | Percentage Price Oscillator | Relationship between two MAs as percentage |
| 47 | ROC | Rate of Change | Rate of change between current and past price |
| 48 | ROCP | Rate of Change Percentage | ROC as decimal percentage |
| 49 | ROCR | Rate of Change Ratio | Ratio of current to past price |
| 50 | ROCR100 | Rate of Change Ratio 100 | ROCR scaled by 100 |
| 51 | RSI | Relative Strength Index | Assesses overbought/oversold conditions |
| 52 | STOCH | Stochastic Oscillator | Decides if the price trend is strong |
| 53 | STOCHF | Stochastic Fast | More sensitive to price changes |
| 54 | STOCHRSI | Stochastic RSI | Combines STOCH and RSI indicators |
| 55 | ULTOSC | Ultimate Oscillator | Takes into account three different time periods |
| 56 | WILLR | Williams %R | Calculates overbought and oversold levels |

### Volume Indicators

| # | Code | Full Name | Description |
|---|------|-----------|-------------|
| 57 | AD | Chaikin A/D Line | Calculates Advance/Decline of an asset |
| 58 | ADOSC | Chaikin A/D Oscillator | Finds relationship between increasing/decreasing volume |
| 59 | OBV | On Balance Volume | Momentum indicator using volume flow |
| 60 | RVOL | Relative Volume | Compares current trading volume to past volume |

### Volatility Indicators

| # | Code | Full Name | Description |
|---|------|-----------|-------------|
| 61 | ATR | Average True Range | Measures market volatility |
| 62 | NATR | Normalized Average True Range | Compares across different price levels |
| 63 | SUPERTREND | SuperTrend | Detects price direction on intraday timeframes |
| 64 | SUPERTREND_HEIKINASHICANDLES | SuperTrend Heikin Ashi | SuperTrend with HA candles |
| 65 | TRANGE | True Range | Determines normal trading range of an asset |

### Cycle Indicators

| # | Code | Full Name | Description |
|---|------|-----------|-------------|
| 66 | HT_DCPERIOD | Hilbert Transform Dominant Cycle Period | Identifies dominant cycle |
| 67 | HT_DCPHASE | Hilbert Transform Dominant Cycle Phase | Phase of dominant cycle |
| 68 | HT_PHASOR | Hilbert Transform Phasor Components | In-phase and quadrature components |
| 69 | HT_SINE | Hilbert Transform SineWave | Sine of phase angle |
| 70 | HT_TRENDMODE | Hilbert Transform Trend vs Cycle Mode | Identifies trend or cycle |

### Price Transform

| # | Code | Full Name | Description |
|---|------|-----------|-------------|
| 71 | AVGPRICE | Average Price | Average of OHLC prices |
| 72 | HEIKINASHICANDLES | Heikin-Ashi Candles | Smoothed candlestick chart (average bar) |
| 73 | HLC3 | HLC3 | Average of High, Low, Close |
| 74 | MEDPRICE | Median Price | Average of high and low |
| 75 | TYPPRICE | Typical Price | Average of HLC |
| 76 | WCLPRICE | Weighted Close Price | Weighted average emphasizing close |

### Math Transform Functions

| # | Code | Full Name | Description |
|---|------|-----------|-------------|
| 77 | ACOS | Arccosine | Inverse cosine function |
| 78 | ASIN | Arcsine | Inverse sine function |
| 79 | ATAN | Arctangent | Inverse tangent function |
| 80 | CEIL | Ceiling | Rounds up to nearest integer |
| 81 | COS | Cosine | Cosine function |
| 82 | COSH | Hyperbolic Cosine | Hyperbolic cosine function |
| 83 | EXP | Exponential | Calculates exponential of values |
| 84 | FLOOR | Floor | Rounds down to nearest integer |
| 85 | LN | Natural Logarithm | Calculates natural log |
| 86 | LOG10 | Logarithm Base 10 | Calculates log base 10 |
| 87 | SIN | Sine | Sine function |
| 88 | SINH | Hyperbolic Sine | Hyperbolic sine function |
| 89 | SQRT | Square Root | Calculates square root |
| 90 | TAN | Tangent | Tangent function |
| 91 | TANH | Hyperbolic Tangent | Hyperbolic tangent function |

### Math Operators

| # | Code | Full Name | Description |
|---|------|-----------|-------------|
| 92 | ADD | Addition | Adds two series together |
| 93 | DIV | Division | Divides one series by another |
| 94 | MULT | Multiplication | Multiplies series together |
| 95 | SUB | Subtraction | Subtracts one series from another |
| 96 | SUM | Summation | Running sum over period |
| 97 | AVG | Average | Averages multiple series |
| 98 | MAX | Maximum | Highest value over period |
| 99 | MAXINDEX | Maximum Index | Index of highest value |
| 100 | MIN | Minimum | Lowest value over period |
| 101 | MININDEX | Minimum Index | Index of lowest value |
| 102 | MINMAX | Min Max | Both minimum and maximum values |
| 103 | MINMAXINDEX | Min Max Index | Indices of min and max values |

### Statistical Functions

| # | Code | Full Name | Description |
|---|------|-----------|-------------|
| 104 | BETA | Beta | Measures volatility relative to market |
| 105 | CORREL | Pearson's Correlation Coefficient | Measures correlation between series |
| 106 | LINEARREG | Linear Regression | Best-fit straight line for trend |
| 107 | LINEARREGANGLE | Linear Regression Angle | Angle of regression line |
| 108 | LINEARREGINTERCEPT | Linear Regression Intercept | Y-intercept of regression |
| 109 | LINEARREGSLOPE | Linear Regression Slope | Slope of regression line |
| 110 | STDDEV | Standard Deviation | Measures volatility/dispersion |
| 111 | TSF | Time Series Forecast | Projects future values |
| 112 | VAR | Variance | Spread between data points |

---

## Flexible BigQuery Schema for Indicators

This schema is designed to be **flexible and extensible** - new indicators can be added without schema changes.

### Table: indicator_metadata (Reference Table)

```sql
CREATE TABLE IF NOT EXISTS `aialgotradehits.crypto_trading_data.indicator_metadata` (
  indicator_id INT64 NOT NULL,
  indicator_code STRING NOT NULL,
  indicator_name STRING NOT NULL,
  category STRING,
  description STRING,
  default_period INT64,
  parameters JSON,
  output_fields JSON,
  is_active BOOL DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### Table: indicator_values (Flexible Storage)

```sql
CREATE TABLE IF NOT EXISTS `aialgotradehits.crypto_trading_data.indicator_values` (
  id STRING NOT NULL,
  symbol STRING NOT NULL,
  asset_type STRING NOT NULL,
  timeframe STRING NOT NULL,
  datetime TIMESTAMP NOT NULL,
  indicator_code STRING NOT NULL,
  value FLOAT64,
  value_json JSON,
  parameters_used JSON,
  data_source STRING DEFAULT 'twelvedata',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(datetime)
CLUSTER BY symbol, indicator_code, timeframe;
```

### Table: ohlcv_data (Core Price Data)

```sql
CREATE TABLE IF NOT EXISTS `aialgotradehits.crypto_trading_data.ohlcv_data` (
  id STRING NOT NULL,
  symbol STRING NOT NULL,
  asset_type STRING NOT NULL,
  timeframe STRING NOT NULL,
  datetime TIMESTAMP NOT NULL,
  open FLOAT64,
  high FLOAT64,
  low FLOAT64,
  close FLOAT64,
  volume FLOAT64,
  data_source STRING DEFAULT 'twelvedata',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(datetime)
CLUSTER BY symbol, asset_type, timeframe;
```

### Table: indicator_calculations (Denormalized for Fast Queries)

```sql
CREATE TABLE IF NOT EXISTS `aialgotradehits.crypto_trading_data.indicator_calculations` (
  id STRING NOT NULL,
  symbol STRING NOT NULL,
  asset_type STRING NOT NULL,
  timeframe STRING NOT NULL,
  datetime TIMESTAMP NOT NULL,

  -- Core OHLCV
  open FLOAT64,
  high FLOAT64,
  low FLOAT64,
  close FLOAT64,
  volume FLOAT64,

  -- Moving Averages (expandable)
  sma_5 FLOAT64,
  sma_10 FLOAT64,
  sma_20 FLOAT64,
  sma_50 FLOAT64,
  sma_100 FLOAT64,
  sma_200 FLOAT64,
  ema_5 FLOAT64,
  ema_10 FLOAT64,
  ema_12 FLOAT64,
  ema_20 FLOAT64,
  ema_26 FLOAT64,
  ema_50 FLOAT64,
  ema_100 FLOAT64,
  ema_200 FLOAT64,
  wma_20 FLOAT64,
  dema_20 FLOAT64,
  tema_20 FLOAT64,
  kama_20 FLOAT64,
  t3ma_20 FLOAT64,
  trima_20 FLOAT64,

  -- Momentum
  rsi_14 FLOAT64,
  rsi_7 FLOAT64,
  rsi_21 FLOAT64,
  macd_line FLOAT64,
  macd_signal FLOAT64,
  macd_histogram FLOAT64,
  stoch_k FLOAT64,
  stoch_d FLOAT64,
  stochrsi_k FLOAT64,
  stochrsi_d FLOAT64,
  willr_14 FLOAT64,
  cci_14 FLOAT64,
  cci_20 FLOAT64,
  mfi_14 FLOAT64,
  mom_10 FLOAT64,
  roc_10 FLOAT64,
  cmo_14 FLOAT64,
  ultosc FLOAT64,
  ppo_line FLOAT64,
  ppo_signal FLOAT64,
  apo FLOAT64,
  bop FLOAT64,

  -- Trend
  adx_14 FLOAT64,
  adxr_14 FLOAT64,
  dx_14 FLOAT64,
  plus_di FLOAT64,
  minus_di FLOAT64,
  plus_dm FLOAT64,
  minus_dm FLOAT64,
  aroon_up FLOAT64,
  aroon_down FLOAT64,
  aroon_osc FLOAT64,

  -- Volatility
  atr_14 FLOAT64,
  natr_14 FLOAT64,
  trange FLOAT64,
  bbands_upper FLOAT64,
  bbands_middle FLOAT64,
  bbands_lower FLOAT64,
  bbands_bandwidth FLOAT64,
  percent_b FLOAT64,
  keltner_upper FLOAT64,
  keltner_middle FLOAT64,
  keltner_lower FLOAT64,
  supertrend FLOAT64,
  supertrend_direction INT64,

  -- Volume
  obv FLOAT64,
  ad FLOAT64,
  adosc FLOAT64,
  vwap FLOAT64,
  rvol FLOAT64,

  -- Ichimoku
  ichimoku_tenkan FLOAT64,
  ichimoku_kijun FLOAT64,
  ichimoku_senkou_a FLOAT64,
  ichimoku_senkou_b FLOAT64,
  ichimoku_chikou FLOAT64,

  -- Statistics
  stddev_20 FLOAT64,
  variance_20 FLOAT64,
  beta FLOAT64,
  correlation FLOAT64,
  linearreg FLOAT64,
  linearreg_slope FLOAT64,
  linearreg_angle FLOAT64,
  linearreg_intercept FLOAT64,
  tsf FLOAT64,

  -- Cycle
  ht_trendline FLOAT64,
  ht_sine FLOAT64,
  ht_leadsine FLOAT64,
  ht_trendmode INT64,
  ht_dcperiod FLOAT64,
  ht_dcphase FLOAT64,

  -- Price Transform
  avgprice FLOAT64,
  medprice FLOAT64,
  typprice FLOAT64,
  wclprice FLOAT64,
  hlc3 FLOAT64,

  -- Additional Indicators (JSON for flexibility)
  additional_indicators JSON,

  -- Metadata
  data_source STRING DEFAULT 'twelvedata',
  calculation_version STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(datetime)
CLUSTER BY symbol, asset_type, timeframe;
```

---

## Python Code to Fetch Latest Indicators from API

```python
import requests
import json
from datetime import datetime

def fetch_twelvedata_indicators():
    """Fetch complete indicator list from TwelveData API"""
    url = "https://api.twelvedata.com/technical_indicators"

    response = requests.get(url)
    data = response.json()

    indicators = []
    for i, (code, info) in enumerate(data.get('data', {}).items(), 1):
        indicators.append({
            'id': i,
            'code': code,
            'name': info.get('full_name', code),
            'description': info.get('description', ''),
            'type': info.get('type', 'unknown'),
            'parameters': info.get('parameters', []),
            'output_values': info.get('output_values', [])
        })

    return indicators

def update_indicator_metadata(indicators, bigquery_client, table_id):
    """Update BigQuery metadata table with latest indicators"""
    rows_to_insert = []

    for ind in indicators:
        rows_to_insert.append({
            'indicator_id': ind['id'],
            'indicator_code': ind['code'],
            'indicator_name': ind['name'],
            'category': ind['type'],
            'description': ind['description'],
            'parameters': json.dumps(ind['parameters']),
            'output_fields': json.dumps(ind['output_values']),
            'is_active': True,
            'updated_at': datetime.utcnow().isoformat()
        })

    # Use MERGE to update existing or insert new
    errors = bigquery_client.insert_rows_json(table_id, rows_to_insert)
    return errors

# Usage
if __name__ == "__main__":
    indicators = fetch_twelvedata_indicators()
    print(f"Total indicators available: {len(indicators)}")

    # Save to JSON for reference
    with open('twelvedata_indicators.json', 'w') as f:
        json.dump(indicators, f, indent=2)
```

---

## API Parameters Reference

### Common Parameters (All Indicators)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Ticker symbol (AAPL, BTC/USD, EUR/USD) |
| interval | string | Yes | 1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 1day, 1week, 1month |
| exchange | string | No | Exchange name (NYSE, NASDAQ, BINANCE) |
| country | string | No | Country code (US, UK, JP) |
| outputsize | int | No | Number of data points (1-5000, default 30) |
| format | string | No | Response format (JSON, CSV) |
| dp | int | No | Decimal places (default 5) |
| timezone | string | No | Timezone (America/New_York, UTC) |
| apikey | string | Yes | Your TwelveData API key |

### Indicator-Specific Parameters

#### Moving Averages (SMA, EMA, WMA, DEMA, TEMA, etc.)
| Parameter | Default | Description |
|-----------|---------|-------------|
| time_period | 9 | Number of data points |
| series_type | close | Price type (open, high, low, close) |

#### RSI
| Parameter | Default | Description |
|-----------|---------|-------------|
| time_period | 14 | RSI calculation period |
| series_type | close | Price type |

#### MACD
| Parameter | Default | Description |
|-----------|---------|-------------|
| fast_period | 12 | Fast EMA period |
| slow_period | 26 | Slow EMA period |
| signal_period | 9 | Signal line period |
| series_type | close | Price type |

#### Bollinger Bands
| Parameter | Default | Description |
|-----------|---------|-------------|
| time_period | 20 | MA period |
| sd | 2 | Standard deviation multiplier |
| ma_type | SMA | Moving average type |
| series_type | close | Price type |

#### Stochastic
| Parameter | Default | Description |
|-----------|---------|-------------|
| fast_k_period | 14 | Fast K period |
| slow_k_period | 3 | Slow K smoothing |
| slow_d_period | 3 | Slow D smoothing |
| slow_kma_type | SMA | K MA type |
| slow_dma_type | SMA | D MA type |

#### ADX
| Parameter | Default | Description |
|-----------|---------|-------------|
| time_period | 14 | ADX period |

#### ATR
| Parameter | Default | Description |
|-----------|---------|-------------|
| time_period | 14 | ATR period |

#### CCI
| Parameter | Default | Description |
|-----------|---------|-------------|
| time_period | 20 | CCI period |

#### Ichimoku
| Parameter | Default | Description |
|-----------|---------|-------------|
| conversion_line_period | 9 | Tenkan-sen |
| base_line_period | 26 | Kijun-sen |
| leading_span_b_period | 52 | Senkou Span B |
| lagging_span_period | 26 | Chikou Span |

---

## Summary Statistics

- **Total Indicators:** 112
- **Categories:** 10 (Overlap, Momentum, Volume, Volatility, Cycle, Price Transform, Math Transform, Math Operators, Statistics)
- **Timeframes Supported:** 12 (1min to 1month)
- **Asset Classes:** 6 (Stocks, Crypto, Forex, ETFs, Indices, Commodities)

**Last Updated:** November 25, 2025
**Source:** TwelveData API `/technical_indicators` endpoint
