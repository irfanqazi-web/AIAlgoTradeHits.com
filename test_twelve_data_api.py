import requests
import json

API_KEY = "16ee060fd4d34a628a14bcb6f0167565"

print("=" * 80)
print("TWELVE DATA API EXPLORATION - PRO PLAN ($229/month)")
print("=" * 80)

# 1. Check API Usage and Plan Details
print("\n1. API USAGE & PLAN DETAILS:")
print("-" * 80)
response = requests.get(f"https://api.twelvedata.com/api_usage?apikey={API_KEY}")
if response.status_code == 200:
    usage = response.json()
    print(json.dumps(usage, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")

# 2. Test Real-Time Quote
print("\n2. REAL-TIME QUOTE (AAPL):")
print("-" * 80)
response = requests.get(f"https://api.twelvedata.com/quote?symbol=AAPL&apikey={API_KEY}")
if response.status_code == 200:
    quote = response.json()
    print(json.dumps(quote, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")

# 3. Test Time Series Data
print("\n3. TIME SERIES DATA (AAPL - Last 5 days):")
print("-" * 80)
response = requests.get(f"https://api.twelvedata.com/time_series?symbol=AAPL&interval=1day&outputsize=5&apikey={API_KEY}")
if response.status_code == 200:
    timeseries = response.json()
    print(json.dumps(timeseries, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")

# 4. Test Market Movers
print("\n4. MARKET MOVERS (Stocks - Gainers):")
print("-" * 80)
response = requests.get(f"https://api.twelvedata.com/market_movers/stocks?apikey={API_KEY}")
if response.status_code == 200:
    movers = response.json()
    print(json.dumps(movers, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")

# 5. Test Available Stocks List
print("\n5. AVAILABLE US STOCKS (First 10):")
print("-" * 80)
response = requests.get(f"https://api.twelvedata.com/stocks?country=United States&apikey={API_KEY}")
if response.status_code == 200:
    stocks = response.json()
    if 'data' in stocks:
        print(f"Total stocks available: {len(stocks['data'])}")
        print("\nFirst 10 stocks:")
        for stock in stocks['data'][:10]:
            print(f"  - {stock['symbol']}: {stock['name']} ({stock['exchange']})")
    else:
        print(json.dumps(stocks, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")

# 6. Test Technical Indicator (RSI)
print("\n6. TECHNICAL INDICATOR - RSI (AAPL):")
print("-" * 80)
response = requests.get(f"https://api.twelvedata.com/rsi?symbol=AAPL&interval=1day&time_period=14&apikey={API_KEY}")
if response.status_code == 200:
    rsi = response.json()
    print(json.dumps(rsi, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")

# 7. Test Exchanges List
print("\n7. AVAILABLE EXCHANGES:")
print("-" * 80)
response = requests.get(f"https://api.twelvedata.com/exchanges?apikey={API_KEY}")
if response.status_code == 200:
    exchanges = response.json()
    if 'data' in exchanges:
        print(f"Total exchanges: {len(exchanges['data'])}")
        print("\nUS Exchanges:")
        us_exchanges = [ex for ex in exchanges['data'] if ex.get('country') == 'United States']
        for ex in us_exchanges[:10]:
            print(f"  - {ex['name']} ({ex['code']})")
    else:
        print(json.dumps(exchanges, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")

print("\n" + "=" * 80)
print("API EXPLORATION COMPLETE")
print("=" * 80)
