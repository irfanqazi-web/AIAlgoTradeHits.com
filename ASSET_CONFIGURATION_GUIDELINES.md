# AIAlgoTradeHits Asset Configuration Guidelines

**Developer:** irfan.qazi@aialgotradehits.com
**Version:** 1.0
**Last Updated:** December 2025

---

## 1. Core Principle: USD-Only Trading

All assets are quoted and traded in **USD only** to ensure:
- Consistent price comparisons across asset classes
- Accurate cross-correlation analysis
- Simplified portfolio calculations
- No currency conversion complexities

---

## 2. Symbol Standardization Rules

### 2.1 Symbol Format by Asset Type

| Asset Type | Format | Example | Storage Format |
|------------|--------|---------|----------------|
| Stocks | Ticker | AAPL | AAPL |
| Crypto | BASE/USD | BTC/USD | BTCUSD |
| Forex | BASE/USD | EUR/USD | EURUSD |
| ETFs | Ticker | SPY | SPY |
| Indices | Index Code | SPX | SPX |
| Commodities | Symbol/USD or Futures | XAU/USD, CL | XAUUSD, CL |

### 2.2 Symbol Transformation Rules

```python
# Standard symbol cleaning for database storage
def normalize_symbol(symbol: str) -> str:
    """
    Transform API symbol to database storage format.

    Examples:
        BTC/USD -> BTCUSD
        EUR/USD -> EURUSD
        XAU/USD -> XAUUSD
        AAPL -> AAPL
    """
    return symbol.replace('/', '').replace(':', '_').upper()
```

---

## 3. Approved Asset Lists (USD-Only)

### 3.1 US Stocks (Top 60 by Market Cap)

```python
STOCKS_USD = [
    # Technology
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'ORCL', 'AMD',
    'ADBE', 'CRM', 'CSCO', 'INTC', 'QCOM', 'TXN', 'IBM', 'NOW', 'AMAT', 'MU',

    # Healthcare
    'UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'PFE', 'TMO', 'ABT', 'DHR', 'BMY',

    # Finance
    'V', 'MA', 'JPM', 'BAC', 'WFC', 'GS', 'MS', 'BLK', 'AXP', 'C',

    # Consumer
    'WMT', 'PG', 'KO', 'PEP', 'COST', 'MCD', 'NKE', 'SBUX', 'TGT', 'HD',

    # Energy
    'XOM', 'CVX', 'COP', 'SLB', 'EOG',

    # Industrial
    'CAT', 'BA', 'GE', 'HON', 'UPS', 'RTX', 'UNP', 'DE', 'LMT', 'MMM'
]
```

### 3.2 Cryptocurrencies (USD Pairs Only)

**IMPORTANT:** Only use /USD pairs, NOT /USDT, /USDC, /EUR, etc.

```python
CRYPTO_USD = [
    # Top 20 by Market Cap
    'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'ADA/USD',
    'SOL/USD', 'DOGE/USD', 'DOT/USD', 'AVAX/USD', 'LINK/USD',
    'TRX/USD', 'ATOM/USD', 'UNI/USD', 'LTC/USD', 'BCH/USD',
    'XLM/USD', 'NEAR/USD', 'ALGO/USD', 'FIL/USD', 'VET/USD',

    # DeFi Tokens
    'AAVE/USD', 'GRT/USD', 'COMP/USD', 'SNX/USD', 'CRV/USD',

    # Layer 2 & New Chains
    'POL/USD', 'OP/USD', 'ARB/USD', 'SUI/USD', 'SEI/USD',

    # Gaming/Metaverse
    'SAND/USD', 'MANA/USD', 'AXS/USD', 'ENJ/USD', 'CHZ/USD',

    # Privacy & Other
    'XMR/USD', 'ZEC/USD', 'DASH/USD', 'ETC/USD', 'NEO/USD'
]

# EXCLUDED - Invalid or rebranded symbols
CRYPTO_EXCLUDED = [
    'MATIC/USD',  # Rebranded to POL
    'FTM/USD',    # Not available on TwelveData
    'MKR/USD',    # API issues
    'EOS/USD',    # Low liquidity
    'YFI/USD',    # Limited data
]
```

### 3.3 Forex (USD Pairs Only)

```python
FOREX_USD = [
    # Major Pairs (USD as quote or base)
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',

    # Emerging Markets vs USD
    'USD/MXN', 'USD/INR', 'USD/SGD', 'USD/HKD', 'USD/ZAR', 'USD/TRY',

    # Cross rates (for correlation only)
    'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY'
]
```

### 3.4 ETFs (USD Denominated)

#### TOP 20 ETFs by AUM (>$4.8 Trillion Combined) - January 2026

| Rank | Symbol | Name | AUM | Category | 1Y Return | 5Y Return |
|------|--------|------|-----|----------|-----------|-----------|
| 1 | VOO | Vanguard S&P 500 ETF | $849B | S&P 500 | +17.61% | +14.76% |
| 2 | IVV | iShares Core S&P 500 ETF | $784B | S&P 500 | +17.64% | +14.76% |
| 3 | SPY | SPDR S&P 500 ETF Trust | $713B | S&P 500 | +17.56% | +14.69% |
| 4 | VTI | Vanguard Total Stock Market ETF | $578B | Total US Market | +17.19% | +13.41% |
| 5 | QQQ | Invesco QQQ Trust | $406B | Growth/Tech | +19.45% | +15.87% |
| 6 | VUG | Vanguard Growth ETF | $203B | Growth | +16.92% | +15.19% |
| 7 | VEA | Vanguard FTSE Developed Markets ETF | $198B | Int'l Developed | +36.92% | +9.19% |
| 8 | IEFA | iShares Core MSCI EAFE ETF | $167B | Int'l Developed | +33.60% | +8.66% |
| 9 | VTV | Vanguard Value ETF | $161B | Value | +17.89% | +12.80% |
| 10 | BND | Vanguard Total Bond Market ETF | $126B | Bonds | +2.87% | -0.42% |
| 11 | IWF | iShares Russell 1000 Growth ETF | $125B | Growth | +15.94% | +15.72% |
| 12 | VXUS | Vanguard Total Int'l Stock ETF | $124B | Int'l Total | +34.64% | +7.70% |
| 13 | AGG | iShares Core U.S. Aggregate Bond ETF | $123B | Bonds | +2.75% | -0.56% |
| 14 | IEMG | iShares Core MSCI Emerging Markets ETF | $115B | Emerging Markets | +30.46% | +5.27% |
| 15 | VGT | Vanguard Information Technology ETF | $113B | Technology | +20.01% | +18.12% |
| 16 | GLD | SPDR Gold Shares | $109B | Gold | +69.90% | +12.56% |
| 17 | IJH | iShares Core S&P Mid-Cap ETF | $105B | Mid-Cap | +14.23% | +9.87% |
| 18 | VWO | Vanguard FTSE Emerging Markets ETF | $105B | Emerging Markets | +30.18% | +4.99% |
| 19 | VIG | Vanguard Dividend Appreciation ETF | $102B | Dividend Growth | +18.45% | +12.34% |
| 20 | SPLG | SPDR Portfolio S&P 500 ETF | $101B | S&P 500 | +17.68% | +14.78% |

```python
ETFS_USD = [
    # TOP 20 ETFs by AUM - Priority Tracking
    # S&P 500 ETFs ($2.4 trillion combined)
    'VOO', 'IVV', 'SPY', 'SPLG',

    # Total Market & Growth
    'VTI', 'QQQ', 'VUG', 'VGT', 'IWF',

    # Value
    'VTV',

    # International Developed
    'VEA', 'IEFA', 'VXUS',

    # Emerging Markets
    'IEMG', 'VWO',

    # Bonds
    'BND', 'AGG',

    # Mid-Cap & Dividend
    'IJH', 'VIG',

    # Gold
    'GLD',

    # Additional ETFs (Sector, Leveraged, Thematic)
    'IWM', 'DIA', 'EFA', 'EEM',
    'XLF', 'XLK', 'XLE', 'XLV', 'XLI', 'XLC', 'XLY', 'XLP', 'XLU', 'XLRE', 'XLB',
    'SLV', 'USO', 'UNG', 'TLT', 'IEF', 'LQD', 'HYG',
    'VNQ', 'ARKK', 'ARKG', 'ARKF', 'SOXX', 'SMH', 'XBI', 'IBB'
]
```

### 3.5 Indices (USD Markets)

```python
INDICES_USD = [
    # US Indices
    'SPX',      # S&P 500
    'IXIC',     # NASDAQ Composite
    'DJI',      # Dow Jones (use DJI:INDEXDJX for TwelveData)
    'RUT',      # Russell 2000
    'VIX',      # Volatility Index
]

# Note: For TwelveData API, some indices require exchange suffix
INDICES_TWELVEDATA_FORMAT = {
    'DJI': 'DJI:INDEXDJX',
    'RUT': 'RUT:INDEXRUSSELL',
}
```

### 3.6 Commodities (USD Priced)

```python
COMMODITIES_USD = [
    # Precious Metals (spot prices in USD)
    'XAU/USD',  # Gold
    'XAG/USD',  # Silver
    'XPT/USD',  # Platinum
    'XPD/USD',  # Palladium

    # Energy Futures (USD)
    'CL',       # WTI Crude Oil
    'BZ',       # Brent Crude
    'NG',       # Natural Gas
    'HO',       # Heating Oil

    # Metal Futures (USD)
    'GC',       # Gold Futures
    'SI',       # Silver Futures
    'HG',       # Copper Futures

    # Agricultural (USD)
    'ZC',       # Corn
    'ZW',       # Wheat
    'ZS',       # Soybeans
]
```

---

## 4. Cross-Correlation Guidelines

### 4.1 Correlation Pairs Structure

```sql
-- BigQuery table for storing correlation data
CREATE TABLE IF NOT EXISTS `aialgotradehits.crypto_trading_data.asset_correlations` (
    id STRING,
    symbol_1 STRING NOT NULL,        -- First asset symbol (normalized)
    symbol_2 STRING NOT NULL,        -- Second asset symbol (normalized)
    asset_type_1 STRING,             -- stocks, crypto, forex, etc.
    asset_type_2 STRING,
    correlation_30d FLOAT64,         -- 30-day correlation
    correlation_90d FLOAT64,         -- 90-day correlation
    correlation_365d FLOAT64,        -- 1-year correlation
    calculated_at TIMESTAMP,
    PRIMARY KEY (symbol_1, symbol_2)
);
```

### 4.2 Cross-Asset Correlation Categories

| Category | Assets Compared | Use Case |
|----------|-----------------|----------|
| Intra-Stock | AAPL vs MSFT | Sector rotation |
| Crypto-Stock | BTC vs NVDA | Tech correlation |
| Crypto-Gold | BTC vs XAU/USD | Safe haven analysis |
| Forex-Stock | USD/JPY vs SPY | Risk sentiment |
| Commodity-Stock | CL vs XLE | Energy sector |

---

## 5. Data Quality Rules

### 5.1 Required Fields for All Assets

```python
REQUIRED_FIELDS = [
    'symbol',           # Normalized symbol (e.g., BTCUSD)
    'datetime',         # UTC timestamp
    'open', 'high', 'low', 'close',
    'volume',
    'percent_change',   # Daily % change
]

INDICATOR_FIELDS = [
    'rsi', 'macd', 'macd_signal', 'macd_histogram',
    'sma_20', 'sma_50', 'sma_200',
    'ema_12', 'ema_26',
    'adx', 'atr',
    'bollinger_upper', 'bollinger_middle', 'bollinger_lower',
]
```

### 5.2 Data Validation Rules

```python
def validate_price_data(row: dict) -> bool:
    """Validate that price data is reasonable."""
    # Price must be positive
    if row['close'] <= 0:
        return False

    # OHLC consistency
    if not (row['low'] <= row['open'] <= row['high']):
        return False
    if not (row['low'] <= row['close'] <= row['high']):
        return False

    # Volume must be non-negative
    if row.get('volume', 0) < 0:
        return False

    # RSI must be 0-100
    if row.get('rsi') and not (0 <= row['rsi'] <= 100):
        return False

    return True
```

---

## 6. API Rate Limits & Best Practices

### 6.1 TwelveData API Limits

| Plan | Requests/Min | Requests/Day | Recommended Delay |
|------|--------------|--------------|-------------------|
| Free | 8 | 800 | 8 seconds |
| Basic | 60 | 5,000 | 1 second |
| Pro | 600 | 50,000 | 100ms |

### 6.2 Optimal Fetching Strategy

```python
# Configuration for TwelveData fetching
FETCH_CONFIG = {
    'max_concurrent_requests': 10,
    'request_delay_ms': 100,  # 10 requests/second for Pro plan
    'batch_size': 50,         # Symbols per batch
    'retry_attempts': 3,
    'retry_backoff_seconds': 2,
    'circuit_breaker_threshold': 10,  # Failures before pause
}
```

---

## 7. Table Naming Convention

```
Format: v2_{asset_type}_{timeframe}

Examples:
- v2_stocks_daily
- v2_crypto_hourly
- v2_forex_5min
- v2_etfs_weekly_summary
```

---

## 8. Symbol Cross-Reference Table

For tracking the same asset across different exchanges/currencies:

```sql
CREATE TABLE IF NOT EXISTS `aialgotradehits.crypto_trading_data.symbol_reference` (
    canonical_symbol STRING PRIMARY KEY,  -- Our standard: BTCUSD
    asset_type STRING,
    full_name STRING,

    -- Exchange-specific symbols
    twelvedata_symbol STRING,             -- BTC/USD
    coinbase_symbol STRING,               -- BTC-USD
    binance_symbol STRING,                -- BTCUSDT
    kraken_symbol STRING,                 -- XBTUSD

    -- Base currency
    quote_currency STRING DEFAULT 'USD',

    -- Status
    is_active BOOL DEFAULT TRUE,
    last_updated TIMESTAMP
);
```

---

## 9. Implementation Checklist

- [ ] All symbols normalized to standard format
- [ ] Only USD-denominated assets in database
- [ ] Invalid/rebranded symbols removed from config
- [ ] Cross-correlation table created
- [ ] Symbol reference table populated
- [ ] Rate limiting configured for API plan
- [ ] Data validation rules implemented
- [ ] Error handling for missing symbols

---

## 10. Contact

For questions or updates to this configuration:
- **Email:** irfan.qazi@aialgotradehits.com
- **Project:** aialgotradehits
- **Repository:** Trading

---

*This document should be updated whenever new assets are added or API changes occur.*
