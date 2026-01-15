

# TwelveData API - Complete Field Reference
## Exact Fields Pulled from Each API Endpoint

---

## **1. /stocks Endpoint** (Stock List)
**Purpose:** Get list of all US stocks
**Used in:** `initialize_stocks_master_list.py`, `weekly_stock_fetcher.py`

### Fields Returned:
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc",
  "currency": "USD",
  "exchange": "NASDAQ",
  "mic_code": "XNGS",
  "country": "United States",
  "type": "Common Stock"  // or "ETF"
}
```

### Exact Fields Used:
- `symbol` - Stock ticker symbol (STRING)
- `name` - Company/ETF name (STRING)
- `currency` - Trading currency, usually "USD" (STRING)
- `exchange` - Stock exchange name (STRING)
- `mic_code` - Market Identifier Code (STRING)
- `country` - Country, filtered to "United States" (STRING)
- `type` - Security type: "Common Stock" or "ETF" (STRING)

---

## **2. /quote Endpoint** (Current Quote)
**Purpose:** Get current price and basic info
**Used in:** `initialize_stocks_master_list.py`, `weekly_stock_fetcher.py`

### Fields Returned:
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc",
  "exchange": "NASDAQ",
  "mic_code": "XNGS",
  "currency": "USD",
  "datetime": "2025-12-08",
  "open": "195.50",
  "high": "197.30",
  "low": "194.80",
  "close": "196.50",
  "volume": "52000000",
  "previous_close": "194.20",
  "change": "2.30",
  "percent_change": "1.18",
  "average_volume": "48500000",
  "is_market_open": true,
  "fifty_two_week": {
    "high": "199.62",
    "low": "164.08"
  },
  "sector": "Technology",
  "industry": "Consumer Electronics"
}
```

### Exact Fields Used:
- `symbol` - Stock ticker (STRING)
- `name` - Company name (STRING)
- `exchange` - Exchange (STRING)
- `mic_code` - Market Identifier Code (STRING)
- `currency` - Currency (STRING)
- `datetime` - Quote datetime (STRING/DATETIME)
- `open` - Opening price (FLOAT)
- `high` - High price (FLOAT)
- `low` - Low price (FLOAT)
- `close` - Closing/current price (FLOAT)
- `volume` - Trading volume (INTEGER)
- `previous_close` - Previous closing price (FLOAT)
- `change` - Price change in dollars (FLOAT)
- `percent_change` - Percent change (FLOAT)
- `average_volume` - Average volume (INTEGER)
- `is_market_open` - Market status (BOOLEAN)
- `fifty_two_week.high` - 52-week high (FLOAT)
- `fifty_two_week.low` - 52-week low (FLOAT)
- `sector` - Business sector (STRING)
- `industry` - Industry classification (STRING)

---

## **3. /time_series Endpoint** (Historical OHLCV)
**Purpose:** Get historical price data with various intervals
**Used in:** `cloud_function_stocks_daily/main.py`, `weekly_stock_fetcher.py`

### Request Parameters:
```
symbol: AAPL
interval: 1day (or 1week, 1hour, 5min, etc.)
outputsize: 250 (number of data points)
apikey: YOUR_API_KEY
```

### Response Structure:
```json
{
  "meta": {
    "symbol": "AAPL",
    "interval": "1day",
    "currency": "USD",
    "exchange": "NASDAQ",
    "mic_code": "XNGS",
    "type": "Common Stock"
  },
  "values": [
    {
      "datetime": "2025-12-08",
      "open": "195.50",
      "high": "197.30",
      "low": "194.80",
      "close": "196.50",
      "volume": "52000000"
    },
    // ... more historical records
  ]
}
```

### Exact Fields Used:

**From meta:**
- `symbol` - Stock ticker (STRING)
- `exchange` - Stock exchange (STRING)
- `mic_code` - Market Identifier Code (STRING)
- `currency` - Trading currency (STRING)

**From values array (each record):**
- `datetime` - Date/time of candle (DATETIME)
- `open` - Opening price (FLOAT)
- `high` - High price (FLOAT)
- `low` - Low price (FLOAT)
- `close` - Closing price (FLOAT)
- `volume` - Trading volume (FLOAT/INTEGER)

---

## **4. /statistics Endpoint** (Advanced Stats)
**Purpose:** Get fundamental statistics and ratios
**Used in:** `weekly_stock_fetcher.py` (optional, may not be available for all stocks)

### Fields Returned:
```json
{
  "statistics": {
    "valuations_metrics": {
      "market_capitalization": 3000000000000,
      "trailing_pe": 29.5,
      "forward_pe": 28.1
    },
    "financials": {
      "diluted_eps_ttm": 6.42,
      "revenue_ttm": 383000000000,
      "net_income_ttm": 96000000000
    },
    "stock_price_summary": {
      "beta": 1.25,
      "52_week_high": 199.62,
      "52_week_low": 164.08
    }
  }
}
```

### Exact Fields Used:
- `statistics.valuations_metrics.market_capitalization` - Market cap in dollars (FLOAT)
- `statistics.valuations_metrics.trailing_pe` - P/E ratio (FLOAT)
- `statistics.financials.diluted_eps_ttm` - Earnings per share (FLOAT)
- `statistics.stock_price_summary.beta` - Beta coefficient (FLOAT)

**Note:** This endpoint often fails for many stocks, so these fields are OPTIONAL.

---

## **5. Fields NOT from TwelveData API**
### (Calculated or Added by Your Code)

### Technical Indicators (71 total - calculated from OHLCV data):
- `rsi`, `macd`, `macd_signal`, `macd_hist`
- `stoch_k`, `stoch_d`, `williams_r`, `cci`, `roc`, `momentum`
- `sma_20`, `sma_50`, `sma_200`
- `ema_12`, `ema_26`, `ema_50`, `ema_100`, `ema_200`
- `wma_20`, `dema_20`, `tema_20`, `kama_20`, `vwap`
- `bb_upper`, `bb_middle`, `bb_lower`
- `atr`, `natr`, `stddev`
- `obv`, `ad`, `adosc`, `pvo`
- `adx`, `adxr`, `plus_di`, `minus_di`
- `aroon_up`, `aroon_down`, `aroonosc`, `trix`, `dx`, `sar`
- `cdl_*` (10 candlestick patterns)
- `correl`, `linearreg`, `linearreg_slope`, `linearreg_angle`, `tsf`, `variance`, `beta`
- `ultosc`, `bop`, `cmo`, `dpo`, `ht_*`, `midpoint`, `midprice`, `ppo`, `stochrsi`, `apo`

### Metadata Fields (added by your code):
- `asset_type` - "STOCK" or "ETF" (STRING)
- `data_source` - "twelvedata" or "twelve_data" (STRING)
- `fetch_timestamp` - When data was fetched (TIMESTAMP)
- `created_at` - Record creation time (TIMESTAMP)
- `updated_at` - Last update time (TIMESTAMP)
- `adjusted_close` - Same as close for stocks (FLOAT)
- `date` - Date extracted from datetime (DATE)

### Calculated Metrics (weekly analysis):
- `weekly_change` - Price change over week (FLOAT)
- `weekly_change_percent` - Percent change over week (FLOAT)
- `percent_from_52_high` - Distance from 52-week high (FLOAT)
- `percent_from_52_low` - Distance from 52-week low (FLOAT)
- `volatility_weekly` - Weekly volatility (FLOAT)
- `atr_percent` - ATR as % of price (FLOAT)
- `day_trade_score` - Trading suitability (0-100) (FLOAT)
- `liquidity_score` - Liquidity score (0-100) (FLOAT)
- `momentum_score` - Momentum score (0-100) (FLOAT)
- `market_cap_category` - "mega", "large", "mid", "small", "micro" (STRING)
- `volatility_category` - "high", "medium", "low" (STRING)
- `momentum_category` - "strong_up", "up", "neutral", "down", "strong_down" (STRING)
- `above_sma_20` - Price above 20-day MA (BOOLEAN)
- `trend_short` - "bullish" or "bearish" (STRING)

### Additional Fields:
- `week_start_date` - Start of trading week (DATE)
- `week_end_date` - End of trading week (DATE)
- `is_active_pick` - Featured stock flag (BOOLEAN)
- `active_pick_reason` - Why featured (STRING)
- `is_active` - Active tracking flag (BOOLEAN)
- `last_weekly_update` - Last update timestamp (TIMESTAMP)
- `quote_datetime` - Original quote datetime from API (STRING)

---

## **Summary: TwelveData API Field Count**

| Endpoint | Fields Returned | Fields Actually Used |
|----------|----------------|---------------------|
| `/stocks` | 7 | 7 (all) |
| `/quote` | 19 | 19 (all) |
| `/time_series` | 5 (values) + 4 (meta) | 9 (all) |
| `/statistics` | ~20+ | 4 (optional) |

**Total TwelveData API Fields Used: ~27 fields**

**Total Calculated/Added Fields: ~100+ fields**

**Total Fields in v2_stocks_master: 55 fields** (27 from API + 28 calculated/technical)

---

## **Key Insights**

1. **Base Data (27 fields)** comes from TwelveData API
2. **Technical Indicators (71 fields)** are calculated from OHLCV data using Python libraries
3. **Metadata & Scores (20+ fields)** are calculated by your code
4. **v2_stocks_master table has 55 fields** - combination of:
   - Basic info from `/stocks` and `/quote` (27 fields)
   - A subset of technical indicators (28 fields)
   - Not all 71 indicators are stored in master table

---

## **Which Fields Are in v2_stocks_master?**

Based on the Excel file analysis, v2_stocks_master contains:

### From TwelveData API (27 fields):
- symbol, name, asset_type, exchange, country
- sector, industry, currency, mic_code, type
- open, high, low, close, previous_close
- volume, average_volume
- change, percent_change
- hi_lo, pct_hi_lo
- week_52_high, week_52_low
- datetime, data_source
- created_at, updated_at

### Technical Indicators in Master Table (28 fields):
- adx, atr
- awesome_osc
- bollinger_lower, bollinger_middle, bollinger_upper
- cci
- ema_12, ema_26, ema_50
- kama
- macd, macd_histogram, macd_signal
- minus_di, plus_di
- momentum
- obv
- ppo, pvo
- roc, rsi
- sma_20, sma_50, sma_200
- stoch_d, stoch_k
- trix
- ultimate_osc
- williams_r
- timestamp (duplicate of datetime)

**Total: 55 fields in v2_stocks_master**

---

## **Important Notes**

1. The **Structure tab showed only 27 fields** because that was the original schema definition
2. The **Data tab has 55 fields** because technical indicators were added later
3. The BigQuery schema description was never updated to include the 28 technical indicator fields
4. All 71 indicators are calculated but only 28 are stored in the master table
5. The full 71 indicators are stored in the daily/hourly/5min tables

---

**Created:** December 8, 2025
**Purpose:** Complete reference for TwelveData API integration
