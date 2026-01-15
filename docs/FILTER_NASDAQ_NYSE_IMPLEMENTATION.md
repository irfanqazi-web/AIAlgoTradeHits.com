# How to Limit Stock Data to NASDAQ and NYSE Only

## Overview
By default, your system fetches ALL US stocks from TwelveData (~20,000+ stocks). This includes many small exchanges you may not care about. This guide shows how to filter to only NASDAQ and NYSE stocks.

---

## Exchange Codes Reference

### NASDAQ Exchanges:
- `NASDAQ` - NASDAQ Stock Market (main)
- `NASDAQ Global Market`
- `NASDAQ Global Select`
- `NASDAQ Capital Market`

### NYSE Exchanges:
- `NYSE` - New York Stock Exchange (main)
- `NYSE American` - formerly AMEX
- `NYSE Arca` - electronic exchange for ETFs

### Other Major Exchanges (currently included but can be excluded):
- `BATS` - BATS Global Markets
- `OTC` - Over The Counter
- `PINK` - Pink Sheets (penny stocks)
- `CBOE` - Chicago Board Options Exchange (for ETFs)
- Many smaller regional exchanges

---

## Implementation Strategy

You need to add a filter in TWO places:

1. **`initialize_stocks_master_list.py`** - Initial population of master list
2. **`weekly_stock_fetcher.py`** - Weekly updates
3. **Optional: Cloud Functions** - If you want to filter daily/hourly/5min fetchers

---

## Solution 1: Filter by Exchange Name (Simple)

### Add Exchange Filter Constant

Add this at the top of both files (after imports):

```python
# Exchange filter - only include these exchanges
ALLOWED_EXCHANGES = {
    # NASDAQ
    'NASDAQ',
    'NASDAQ Global Market',
    'NASDAQ Global Select',
    'NASDAQ Capital Market',

    # NYSE
    'NYSE',
    'NYSE American',
    'NYSE Arca',

    # Optional: CBOE for ETFs
    'CBOE'
}

# If you want to be more permissive, use partial matching:
ALLOWED_EXCHANGE_KEYWORDS = ['NASDAQ', 'NYSE']
```

### Modify `get_all_us_stocks()` Function

**Option A: Exact Match (Strict)**

```python
def get_all_us_stocks():
    """Get list of US stocks from TwelveData /stocks endpoint - NASDAQ/NYSE only"""
    print("Step 1: Fetching US stock list from TwelveData /stocks endpoint...")
    url = "https://api.twelvedata.com/stocks"
    params = {
        'country': 'United States',
        'apikey': TWELVE_DATA_API_KEY
    }

    response = requests.get(url, params=params, timeout=60)
    data = response.json()

    if 'data' not in data:
        print(f"Error: {data}")
        return []

    stocks = []
    for item in data['data']:
        exchange = item.get('exchange', '')

        # Filter: NASDAQ/NYSE only + Common Stock/ETF only
        if (item.get('type') in ['Common Stock', 'ETF'] and
            exchange in ALLOWED_EXCHANGES):
            stocks.append({
                'symbol': item['symbol'],
                'name': item['name'],
                'currency': item.get('currency', 'USD'),
                'exchange': item['exchange'],
                'mic_code': item.get('mic_code', ''),
                'country': item.get('country', 'United States'),
                'type': item['type']
            })

    print(f"   Found {len(stocks)} stocks on NASDAQ/NYSE (Common Stock + ETF)")
    return stocks
```

**Option B: Keyword Match (More Permissive)**

```python
def get_all_us_stocks():
    """Get list of US stocks from TwelveData /stocks endpoint - NASDAQ/NYSE only"""
    print("Step 1: Fetching US stock list from TwelveData /stocks endpoint...")
    url = "https://api.twelvedata.com/stocks"
    params = {
        'country': 'United States',
        'apikey': TWELVE_DATA_API_KEY
    }

    response = requests.get(url, params=params, timeout=60)
    data = response.json()

    if 'data' not in data:
        print(f"Error: {data}")
        return []

    stocks = []
    filtered_count = 0

    for item in data['data']:
        exchange = item.get('exchange', '')

        # Check if exchange contains NASDAQ or NYSE
        is_allowed = any(keyword in exchange.upper() for keyword in ['NASDAQ', 'NYSE'])

        # Filter: NASDAQ/NYSE only + Common Stock/ETF only
        if (item.get('type') in ['Common Stock', 'ETF'] and is_allowed):
            stocks.append({
                'symbol': item['symbol'],
                'name': item['name'],
                'currency': item.get('currency', 'USD'),
                'exchange': item['exchange'],
                'mic_code': item.get('mic_code', ''),
                'country': item.get('country', 'United States'),
                'type': item['type']
            })
        else:
            filtered_count += 1

    print(f"   Found {len(stocks)} stocks on NASDAQ/NYSE (Common Stock + ETF)")
    print(f"   Filtered out {filtered_count} stocks from other exchanges")
    return stocks
```

---

## Solution 2: Filter by MIC Code (Most Accurate)

MIC (Market Identifier Code) is a standardized ISO 10383 code for exchanges.

### Common MIC Codes:

```python
# MIC codes for major US exchanges
ALLOWED_MIC_CODES = {
    'XNAS',  # NASDAQ
    'XNGS',  # NASDAQ Global Select
    'XNCM',  # NASDAQ Capital Market
    'XNMS',  # NASDAQ Global Market
    'XNYS',  # NYSE (New York Stock Exchange)
    'ARCX',  # NYSE Arca
    'XASE',  # NYSE American (formerly AMEX)
    'BATS',  # BATS (optional)
}
```

### Modify Function to Use MIC Codes:

```python
def get_all_us_stocks():
    """Get list of US stocks from TwelveData /stocks endpoint - NASDAQ/NYSE only"""
    print("Step 1: Fetching US stock list from TwelveData /stocks endpoint...")
    url = "https://api.twelvedata.com/stocks"
    params = {
        'country': 'United States',
        'apikey': TWELVE_DATA_API_KEY
    }

    response = requests.get(url, params=params, timeout=60)
    data = response.json()

    if 'data' not in data:
        print(f"Error: {data}")
        return []

    stocks = []
    exchange_stats = {}  # Track exchanges for reporting

    for item in data['data']:
        mic_code = item.get('mic_code', '')
        exchange = item.get('exchange', '')

        # Track exchange distribution
        exchange_stats[exchange] = exchange_stats.get(exchange, 0) + 1

        # Filter: NASDAQ/NYSE (by MIC) + Common Stock/ETF only
        if (item.get('type') in ['Common Stock', 'ETF'] and
            mic_code in ALLOWED_MIC_CODES):
            stocks.append({
                'symbol': item['symbol'],
                'name': item['name'],
                'currency': item.get('currency', 'USD'),
                'exchange': item['exchange'],
                'mic_code': item.get('mic_code', ''),
                'country': item.get('country', 'United States'),
                'type': item['type']
            })

    print(f"   Found {len(stocks)} stocks on NASDAQ/NYSE (Common Stock + ETF)")
    print(f"   Exchange breakdown:")
    for exch, count in sorted(exchange_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        included = "✓" if any(mic in ALLOWED_MIC_CODES for mic in [exch]) else "✗"
        print(f"     {included} {exch}: {count} stocks")

    return stocks
```

---

## Where to Apply These Changes

### **1. initialize_stocks_master_list.py**
Modify the `get_all_us_stocks()` function (lines 36-67)

### **2. weekly_stock_fetcher.py**
Modify the `get_all_us_stocks()` function (lines 72-101)

### **3. Optional: Cloud Functions for Daily/Hourly**
If you have Cloud Functions that fetch daily/hourly data, you can:
- **Option A:** Filter at source (modify symbol lists)
- **Option B:** Filter in BigQuery (query WHERE exchange IN (...))
- **Option C:** Keep all data but add `is_major_exchange` flag

---

## Example: Complete Implementation

Here's the complete modified function with both filtering methods:

```python
# At top of file, after imports
# ================================
# Exchange Filter Configuration
# ================================

# Method 1: Use MIC codes (recommended - most accurate)
ALLOWED_MIC_CODES = {
    'XNAS',  # NASDAQ
    'XNGS',  # NASDAQ Global Select
    'XNCM',  # NASDAQ Capital Market
    'XNMS',  # NASDAQ Global Market
    'XNYS',  # NYSE (New York Stock Exchange)
    'ARCX',  # NYSE Arca
    'XASE',  # NYSE American
}

# Method 2: Use exchange names (alternative)
ALLOWED_EXCHANGES = {
    'NASDAQ', 'NASDAQ Global Market', 'NASDAQ Global Select', 'NASDAQ Capital Market',
    'NYSE', 'NYSE American', 'NYSE Arca'
}

# Method 3: Use keywords (most permissive)
ALLOWED_EXCHANGE_KEYWORDS = ['NASDAQ', 'NYSE']

# Choose your method:
FILTER_METHOD = 'mic_code'  # Options: 'mic_code', 'exact', 'keyword'


def get_all_us_stocks():
    """Get list of US stocks from TwelveData /stocks endpoint - NASDAQ/NYSE only"""
    print("Step 1: Fetching US stock list from TwelveData /stocks endpoint...")
    print(f"   Filter method: {FILTER_METHOD}")

    url = "https://api.twelvedata.com/stocks"
    params = {
        'country': 'United States',
        'apikey': TWELVE_DATA_API_KEY
    }

    response = requests.get(url, params=params, timeout=60)
    data = response.json()

    if 'data' not in data:
        print(f"Error: {data}")
        return []

    stocks = []
    total_stocks = len(data['data'])
    filtered_count = 0

    for item in data['data']:
        exchange = item.get('exchange', '')
        mic_code = item.get('mic_code', '')
        stock_type = item.get('type', '')

        # Apply filter based on chosen method
        is_allowed_exchange = False

        if FILTER_METHOD == 'mic_code':
            is_allowed_exchange = mic_code in ALLOWED_MIC_CODES
        elif FILTER_METHOD == 'exact':
            is_allowed_exchange = exchange in ALLOWED_EXCHANGES
        elif FILTER_METHOD == 'keyword':
            is_allowed_exchange = any(kw in exchange.upper() for kw in ALLOWED_EXCHANGE_KEYWORDS)

        # Filter: Allowed exchange + Common Stock/ETF only
        if stock_type in ['Common Stock', 'ETF'] and is_allowed_exchange:
            stocks.append({
                'symbol': item['symbol'],
                'name': item['name'],
                'currency': item.get('currency', 'USD'),
                'exchange': item['exchange'],
                'mic_code': item.get('mic_code', ''),
                'country': item.get('country', 'United States'),
                'type': item['type']
            })
        else:
            filtered_count += 1

    print(f"   Total US stocks available: {total_stocks}")
    print(f"   Stocks on NASDAQ/NYSE: {len(stocks)}")
    print(f"   Filtered out: {filtered_count} stocks from other exchanges")
    return stocks
```

---

## Testing the Filter

Before deploying, test to see how many stocks you'll get:

```python
# Add this to the main() function
stocks = get_all_us_stocks()

# Show sample of exchanges
exchange_counts = {}
for stock in stocks:
    exch = stock['exchange']
    exchange_counts[exch] = exchange_counts.get(exch, 0) + 1

print("\nExchange distribution:")
for exch, count in sorted(exchange_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {exch}: {count} stocks")
```

---

## Expected Results

### Before Filtering (All US Exchanges):
- Total stocks: ~20,000+
- Includes: OTC, Pink Sheets, regional exchanges

### After Filtering (NASDAQ/NYSE Only):
- **NASDAQ stocks: ~3,500-4,000**
- **NYSE stocks: ~2,500-3,000**
- **Total: ~6,000-7,000 stocks**

---

## BigQuery Impact

### Storage Reduction:
- **Before:** 20,000 stocks × 52 weeks = ~1 million records/year
- **After:** 6,500 stocks × 52 weeks = ~340,000 records/year
- **Savings:** ~66% reduction in storage and API costs

### API Call Reduction:
- **Before:** 20,000 stocks × 3 API calls = 60,000 calls/week
- **After:** 6,500 stocks × 3 API calls = 19,500 calls/week
- **Savings:** ~67% reduction in API usage

---

## Recommendation

**Use Method 1 (MIC Code filtering)** because:
1. ✅ Most accurate and standardized
2. ✅ No ambiguity about exchange variations
3. ✅ Future-proof (ISO standard)
4. ✅ Easy to maintain

**Alternative: Use Method 2 (Keyword matching)** if:
- TwelveData's MIC codes are incomplete
- You want more flexibility
- You want to include variations automatically

---

## Next Steps

1. ✅ Choose your filtering method (recommend: MIC codes)
2. ✅ Update `initialize_stocks_master_list.py`
3. ✅ Update `weekly_stock_fetcher.py`
4. ✅ Test locally to see stock counts
5. ✅ Re-run initialization to rebuild master list
6. ✅ Update Cloud Functions if needed

**Want me to implement this for you?**
