# NLP Smart Search - User Guide

**Feature**: AI-Powered Natural Language Search with Text & Voice Input
**Location**: Main navigation menu → "Smart Search" (NEW badge)
**URL**: https://crypto-trading-app-252370699783.us-central1.run.app

---

## Overview

The NLP Smart Search allows you to query your trading data using **plain English** instead of writing SQL. You can search across all 6 trading data tables (crypto and stock data in daily, hourly, and 5-minute timeframes) using either:

- ✅ **Text Input**: Type your query
- ✅ **Voice Input**: Speak your query (hands-free)

The system automatically:
1. Understands your natural language query
2. Converts it to optimized SQL
3. Executes the query against BigQuery
4. Displays results in tables and charts
5. Shows you the generated SQL for learning

---

## How to Access

### Desktop
1. Open the trading application at: https://crypto-trading-app-252370699783.us-central1.run.app
2. Login with your credentials
3. Click the **hamburger menu** (☰) in the top-left
4. Select **"Smart Search"** from the navigation menu (marked with "NEW" badge)

### Mobile
1. Open the trading app on your mobile browser
2. Tap the menu icon (☰)
3. Scroll to find **"Smart Search"**
4. Tap to open

---

## Using Text Input

### Basic Usage

1. **Click in the search box** at the top of the Smart Search page
2. **Type your query** in plain English
3. **Press Enter** or click the **Search button** (🔍)

### Example Text Queries

**Simple Symbol Queries:**
```
Bitcoin hourly last 24 hours
AAPL 5-minute
Ethereum daily
Tesla today
```

**Indicator-Based Queries:**
```
Oversold cryptos
Stocks with bullish MACD
High volume cryptos
Cryptos with RSI below 30
```

**Complex Queries:**
```
Top 10 stock gainers
Stocks with RSI below 40 and above 200 MA
Cryptos with strong trend and oversold
Bitcoin vs Ethereum
Show me AAPL with high volume
```

**Comparison Queries:**
```
Compare Bitcoin and Ethereum
AAPL vs TSLA
Show BTC and ETH side by side
```

---

## Using Voice Input 🎤

### Browser Compatibility

Voice input works on:
- ✅ **Chrome** (Desktop & Mobile) - Recommended
- ✅ **Edge** (Desktop & Mobile)
- ✅ **Safari** (iOS 14.5+)
- ❌ **Firefox** (Limited support)

### Step-by-Step Instructions

#### Desktop (Chrome/Edge)

1. **Navigate to Smart Search page**
2. **Click the microphone button** (🎤) on the right side of the search box
3. **Allow microphone access** when prompted (first time only)
   - Chrome: Click "Allow" in the popup
   - Edge: Click "Allow" in the popup
4. **Start speaking** your query clearly
5. The microphone button will turn **red** while listening
6. **Speak naturally**: "Show me Bitcoin hourly last 24 hours"
7. **Stop speaking** when done - the system auto-detects
8. Query executes automatically when speech recognition completes

#### Mobile (Chrome/Safari)

1. **Tap the Smart Search menu item**
2. **Tap the microphone icon** (🎤)
3. **Allow microphone access** (first time only)
   - iOS Safari: "Allow [App Name] to access microphone"
   - Android Chrome: "Allow microphone access"
4. **Speak your query** clearly and naturally
5. **Wait for auto-submit** after speech recognition completes

### Voice Query Examples

Speak these queries naturally (don't worry about perfect pronunciation):

**Simple queries:**
- "Bitcoin hourly last 24 hours"
- "Apple stock 5 minute"
- "Ethereum daily"
- "Tesla today"

**Indicator queries:**
- "Oversold cryptos"
- "Stocks with bullish MACD"
- "Show me high volume cryptos"

**Complex queries:**
- "Top 10 stock gainers"
- "Stocks with RSI below 40 and above 200 moving average"
- "Bitcoin compared to Ethereum"

### Troubleshooting Voice Input

**Microphone not working?**
1. Check browser permissions:
   - Chrome: Settings → Privacy & Security → Site Settings → Microphone
   - Safari: Safari → Settings → Websites → Microphone
2. Ensure microphone is not muted
3. Try refreshing the page
4. Try a different browser (Chrome works best)

**Speech not recognized?**
1. Speak more clearly and slowly
2. Reduce background noise
3. Check if microphone is too far away
4. Try using headphones with built-in mic

**Voice input button missing?**
- Your browser doesn't support Web Speech API
- Use Chrome or Edge instead
- Fall back to text input

---

## Understanding Results

### Results Display

After submitting a query, you'll see:

1. **Query Interpretation**: How the system understood your query
2. **Generated SQL**: The SQL query that was executed (for learning)
3. **Results Table**: Data in a sortable, scrollable table
4. **Auto-Generated Chart**: If query returns time-series data (5+ results with timestamps)

### Chart Types

**When you get a chart:**
- Queries with 5+ results containing datetime field
- Displays candlestick chart with OHLC data
- Interactive: zoom, pan, crosshair
- Shows volume bars (if available)

**When you get a table only:**
- Queries with fewer than 5 results
- Queries without datetime field
- Summary/aggregate queries

### Reading the Results

**Table Columns:**
- `symbol/pair`: Asset identifier (e.g., AAPL, BTCUSD)
- `datetime`: Timestamp of the data point
- `open/high/low/close`: OHLC price data
- `volume`: Trading volume
- `rsi/macd/sma_200`: Technical indicators (if available)

**Chart Features:**
- **Zoom**: Scroll wheel or pinch gesture
- **Pan**: Click and drag
- **Crosshair**: Hover over candles to see exact values
- **Timeframe**: Automatically adjusted based on data

---

## Query Patterns & Keywords

### Market Type Detection

**Crypto keywords:**
- "crypto", "cryptocurrency", "bitcoin", "ethereum", "BTC", "ETH"
- Triggers: `crypto_analysis`, `crypto_hourly_data`, or `crypto_5min_top10_gainers` tables

**Stock keywords:**
- "stock", "stocks", "equity", "share", "AAPL", "TSLA", "MSFT"
- Triggers: `stock_analysis`, `stock_hourly_data`, or `stock_5min_top10_gainers` tables

### Timeframe Detection

| Keyword | Table | Description |
|---------|-------|-------------|
| "daily", "day", "days", "today", "yesterday" | `*_analysis` | Daily data |
| "hourly", "hour", "hours", "1h", "1 hour" | `*_hourly_data` | Hourly data |
| "5-minute", "5 minute", "5min", "five minute" | `*_5min_top10_gainers` | 5-minute data |

### Symbol Detection

**Crypto symbols:**
- Bitcoin: "bitcoin", "btc", "xbt" → XXBTZUSD, BTCUSD
- Ethereum: "ethereum", "eth" → XETHZUSD, ETHUSD
- Solana: "solana", "sol" → SOLUSD
- Cardano: "cardano", "ada" → ADAUSD
- Dogecoin: "dogecoin", "doge" → DOGEUSD

**Stock symbols:**
- Apple: "apple", "aapl" → AAPL
- Tesla: "tesla", "tsla" → TSLA
- Microsoft: "microsoft", "msft" → MSFT
- Amazon: "amazon", "amzn" → AMZN
- Google: "google", "googl" → GOOGL

### Indicator Patterns

| Query Phrase | Indicator | Condition | Description |
|--------------|-----------|-----------|-------------|
| "oversold" | RSI | < 30 | Assets likely to bounce up |
| "overbought" | RSI | > 70 | Assets likely to pull back |
| "bullish macd" | MACD | > 0 | Upward momentum |
| "bearish macd" | MACD | < 0 | Downward momentum |
| "strong trend" | ADX | > 25 | Trending market |
| "high volume" | Volume | Top 20% | High trading activity |
| "below 200 ma" | SMA_200 | price < SMA | Below long-term average |
| "above 200 ma" | SMA_200 | price > SMA | Above long-term average |

### Comparison Queries

**Patterns:**
- "bitcoin vs ethereum" → Returns both BTC and ETH
- "aapl compared to tsla" → Returns both AAPL and TSLA
- "compare" + symbols → Multiple symbols in results

### Time Range

| Phrase | Time Range |
|--------|------------|
| "today" | Current date |
| "yesterday" | Previous day |
| "last 24 hours" | Past 24 hours |
| "last 7 days" | Past week |
| "last week" | Past 7 days |
| "last month" | Past 30 days |
| "this week" | Current week |

### Result Limits

| Phrase | Limit |
|--------|-------|
| "top 5" | 5 results |
| "top 10" | 10 results |
| "top 20" | 20 results |
| "first 100" | 100 results |
| (no limit specified) | 100 results (default) |

---

## Advanced Query Examples

### Beginner Queries

```
Bitcoin daily
AAPL hourly
Ethereum last 7 days
Show me Tesla
```

### Intermediate Queries

```
Oversold cryptos
Stocks with high volume
Bitcoin hourly last 24 hours
Top 10 crypto gainers
Stocks with RSI below 30
```

### Advanced Queries

```
Stocks with RSI below 40 and above 200 MA
Cryptos with strong trend and bullish MACD
Top 5 oversold stocks with high volume
Bitcoin vs Ethereum hourly last 7 days
Show AAPL with RSI below 35 and MACD above 0
Stocks with price above SMA 50 and volume above average
```

### Multi-Condition Queries

```
Cryptos with RSI below 30 and ADX above 25 and volume high
Stocks with price above 200 MA and RSI between 40 and 60
Top 10 cryptos with bullish MACD and strong trend
Show me oversold stocks with high volume today
```

---

## Query Results Interpretation

### Understanding Indicators

**RSI (Relative Strength Index)**
- **< 30**: Oversold (potential buy signal)
- **30-70**: Normal range
- **> 70**: Overbought (potential sell signal)

**MACD (Moving Average Convergence Divergence)**
- **> 0**: Bullish momentum
- **< 0**: Bearish momentum
- **Crossing 0**: Trend change signal

**ADX (Average Directional Index)**
- **< 20**: Weak trend
- **20-25**: Moderate trend
- **> 25**: Strong trend
- **> 50**: Very strong trend

**SMA_200 (200-day Simple Moving Average)**
- **Price > SMA_200**: Bullish long-term trend
- **Price < SMA_200**: Bearish long-term trend

**Volume**
- **High volume**: Strong interest, more reliable price moves
- **Low volume**: Weak interest, less reliable price moves

---

## Tips for Best Results

### Text Input Tips

1. **Be specific**: "Bitcoin hourly" instead of just "Bitcoin"
2. **Use timeframes**: "last 24 hours", "today", "daily"
3. **Combine conditions**: "oversold AND high volume"
4. **Use comparison words**: "vs", "compared to", "versus"
5. **Specify limits**: "top 10", "first 5"

### Voice Input Tips

1. **Speak clearly**: Enunciate each word
2. **Speak naturally**: Use conversational tone
3. **Pause briefly**: Between phrases (e.g., "Bitcoin... hourly... last 24 hours")
4. **Avoid filler words**: "um", "uh", "like"
5. **Quiet environment**: Reduce background noise
6. **Good microphone**: Use headphones if possible

### General Tips

1. **Start simple**: Try basic queries first
2. **Check interpretation**: See how system understood your query
3. **Review SQL**: Learn SQL by seeing generated queries
4. **Experiment**: Try different phrasings
5. **Use suggestions**: Click suggestion chips for ideas

---

## Common Use Cases

### Daily Monitoring

**Morning routine:**
```
1. "Top 10 crypto gainers" (see what's moving)
2. "Oversold stocks" (find potential buys)
3. "Bitcoin vs Ethereum" (compare majors)
```

### Trade Research

**Finding opportunities:**
```
1. "Stocks with RSI below 30 and high volume"
2. "Cryptos with strong trend and bullish MACD"
3. "Top 5 oversold cryptos with ADX above 25"
```

### Portfolio Tracking

**Checking your holdings:**
```
1. "AAPL hourly last 7 days"
2. "Bitcoin 5-minute"
3. "Tesla today"
```

### Technical Analysis

**Deep dive on indicators:**
```
1. "Show me AAPL with all indicators"
2. "Bitcoin hourly with RSI and MACD"
3. "Stocks with price above 200 MA"
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + K` (or `Cmd + K` on Mac) | Focus search box |
| `Enter` | Submit query |
| `Esc` | Clear search box |
| `Tab` | Navigate suggestion chips |

---

## Supported Data Tables

### Crypto Data (3 tables)

1. **crypto_analysis** (Daily)
   - 678 USD trading pairs
   - Daily OHLC + 29 indicators
   - Updated: Midnight ET

2. **crypto_hourly_data** (Hourly)
   - 678 USD trading pairs
   - Hourly OHLC + 29 indicators
   - Updated: Every hour

3. **crypto_5min_top10_gainers** (5-Minute)
   - Top 10 hourly gainers
   - 5-minute OHLC + indicators
   - Updated: Every 5 minutes

### Stock Data (3 tables)

1. **stock_analysis** (Daily)
   - 97 major US stocks
   - Daily OHLC + indicators
   - Updated: After market close

2. **stock_hourly_data** (Hourly)
   - 97 major US stocks
   - Hourly OHLC + indicators
   - Updated: Every hour (during market hours)
   - **Note**: Currently experiencing data collection issues with Yahoo Finance

3. **stock_5min_top10_gainers** (5-Minute)
   - Top 10 stock gainers
   - 5-minute OHLC + indicators
   - Updated: Every 5 minutes (during market hours)
   - **Note**: Currently experiencing data collection issues with Yahoo Finance

---

## Troubleshooting

### "No results found"

**Possible reasons:**
1. Data doesn't exist for the specified timeframe/symbol
2. Stock hourly/5-min tables are currently empty (Yahoo Finance issue)
3. Symbol name not recognized

**Solutions:**
- Try a different timeframe (e.g., "daily" instead of "hourly" for stocks)
- Check if crypto data works (should have data)
- Verify symbol name (e.g., "AAPL" not "Apple Inc")

### "Query failed" error

**Possible reasons:**
1. Backend API is down
2. BigQuery issue
3. Invalid SQL generated

**Solutions:**
- Refresh the page and try again
- Simplify your query
- Try a known working query (e.g., "Bitcoin daily")
- Check your internet connection

### Voice input not working

**Solutions:**
1. Check browser permissions
2. Use Chrome or Edge browser
3. Allow microphone access when prompted
4. Check if microphone is working (test in another app)
5. Try text input as fallback

### Chart not displaying

**Reasons:**
- Query returned fewer than 5 results
- No datetime field in results
- Query is an aggregate/summary

**This is normal** - not all queries produce charts. The table view will always show results.

---

## Privacy & Security

### Microphone Access

- Microphone access is **only used for voice input**
- No audio is stored or transmitted beyond speech recognition
- Audio is processed by your browser's built-in speech recognition (Google/Apple)
- You can revoke access anytime in browser settings

### Query Data

- All queries are sent to the backend API for processing
- Queries are logged for debugging purposes
- No sensitive data is stored in queries
- Data is transmitted over HTTPS (encrypted)

---

## Future Enhancements (Coming Soon)

- 🔜 **Save favorite queries**
- 🔜 **Query history**
- 🔜 **Export results to CSV/Excel**
- 🔜 **Schedule automated queries**
- 🔜 **Email alerts based on query results**
- 🔜 **More chart types** (line charts, bar charts, heatmaps)
- 🔜 **Multi-language support** (Spanish, French, Chinese)

---

## Support & Feedback

Having issues or suggestions?

1. **Check this guide** for common solutions
2. **Test with simple queries** first
3. **Review the generated SQL** to understand what went wrong
4. **Contact support** with:
   - Your query text
   - Screenshot of error (if any)
   - Browser and device info

---

## Examples Gallery

### Example 1: Find Oversold Cryptos

**Query (Text):**
```
oversold cryptos
```

**Query (Voice):**
🎤 "Show me oversold cryptos"

**Generated SQL:**
```sql
SELECT pair, close, rsi, datetime
FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`
WHERE rsi < 30
ORDER BY rsi ASC
LIMIT 100
```

**Results:** Table showing cryptos with RSI < 30, sorted by lowest RSI first

---

### Example 2: Bitcoin Hourly Chart

**Query (Text):**
```
Bitcoin hourly last 24 hours
```

**Query (Voice):**
🎤 "Bitcoin hourly last twenty four hours"

**Generated SQL:**
```sql
SELECT pair, datetime, open, high, low, close, volume
FROM `cryptobot-462709.crypto_trading_data.crypto_hourly_data`
WHERE pair IN ('XXBTZUSD', 'BTCUSD', 'XBTUSD')
  AND datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY datetime DESC
LIMIT 100
```

**Results:** Candlestick chart + table showing BTC hourly data for past 24 hours

---

### Example 3: Top Stock Gainers

**Query (Text):**
```
top 10 stock gainers
```

**Query (Voice):**
🎤 "Top ten stock gainers"

**Generated SQL:**
```sql
SELECT symbol, close, volume, datetime
FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
ORDER BY close DESC
LIMIT 10
```

**Results:** Table showing top 10 stocks by price

---

### Example 4: Complex Multi-Condition

**Query (Text):**
```
Stocks with RSI below 40 and above 200 MA
```

**Query (Voice):**
🎤 "Stocks with RSI below forty and above two hundred moving average"

**Generated SQL:**
```sql
SELECT symbol, close, rsi, sma_200, datetime
FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
WHERE rsi < 40
  AND close > sma_200
ORDER BY rsi ASC
LIMIT 100
```

**Results:** Table showing oversold stocks that are above long-term trend

---

**Happy Searching!** 🚀

For more help, visit the application's Help section or contact support.

**Last Updated**: November 16, 2025
