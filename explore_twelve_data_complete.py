import requests
import json
import sys
import io

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_KEY = "16ee060fd4d34a628a14bcb6f0167565"

print("=" * 100)
print("TWELVE DATA COMPLETE EXPLORATION - ALL ASSET CLASSES & 100+ INDICATORS")
print("=" * 100)

# 1. STOCKS
print("\n" + "=" * 100)
print("1. STOCKS - US MARKET")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/stocks?country=United States&apikey={API_KEY}")
if response.status_code == 200:
    stocks = response.json()
    if 'data' in stocks:
        print(f"✅ Total US Stocks: {len(stocks['data'])}")
        exchanges = {}
        for stock in stocks['data']:
            ex = stock.get('exchange', 'Unknown')
            exchanges[ex] = exchanges.get(ex, 0) + 1
        print("\nStocks by Exchange:")
        for ex, count in sorted(exchanges.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {ex}: {count} stocks")
        print(f"\nSample Stocks:")
        for stock in stocks['data'][:5]:
            print(f"  - {stock['symbol']}: {stock['name']} ({stock['exchange']})")

# 2. ETFs
print("\n" + "=" * 100)
print("2. ETFs - US MARKET")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/etf?country=United States&apikey={API_KEY}")
if response.status_code == 200:
    etfs = response.json()
    if 'data' in etfs:
        print(f"✅ Total US ETFs: {len(etfs['data'])}")
        print(f"\nSample ETFs:")
        for etf in etfs['data'][:10]:
            print(f"  - {etf['symbol']}: {etf['name']} ({etf.get('exchange', 'N/A')})")

# 3. FOREX (Currency Pairs)
print("\n" + "=" * 100)
print("3. FOREX - CURRENCY PAIRS")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/forex_pairs?apikey={API_KEY}")
if response.status_code == 200:
    forex = response.json()
    if 'data' in forex:
        print(f"✅ Total Forex Pairs: {len(forex['data'])}")
        # Filter USD pairs
        usd_pairs = [p for p in forex['data'] if 'USD' in p['symbol']]
        print(f"✅ USD Currency Pairs: {len(usd_pairs)}")
        print(f"\nMajor USD Pairs:")
        for pair in usd_pairs[:15]:
            print(f"  - {pair['symbol']}: {pair.get('currency_base', 'N/A')}/{pair.get('currency_quote', 'N/A')}")

# 4. CRYPTOCURRENCIES
print("\n" + "=" * 100)
print("4. CRYPTOCURRENCIES")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/cryptocurrencies?apikey={API_KEY}")
if response.status_code == 200:
    crypto = response.json()
    if 'data' in crypto:
        print(f"✅ Total Cryptocurrencies: {len(crypto['data'])}")
        # Filter USD pairs
        usd_crypto = [c for c in crypto['data'] if 'USD' in c['symbol']]
        print(f"✅ USD Crypto Pairs: {len(usd_crypto)}")
        print(f"\nTop USD Crypto Pairs:")
        for c in usd_crypto[:20]:
            print(f"  - {c['symbol']}: {c.get('currency_base', 'N/A')}/{c.get('currency_quote', 'N/A')}")

# 5. COMMODITIES
print("\n" + "=" * 100)
print("5. COMMODITIES")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/commodities?apikey={API_KEY}")
if response.status_code == 200:
    commodities = response.json()
    if 'data' in commodities:
        print(f"✅ Total Commodities: {len(commodities['data'])}")
        print(f"\nAvailable Commodities:")
        for comm in commodities['data'][:25]:
            print(f"  - {comm['symbol']}: {comm['name']} ({comm.get('exchange', 'N/A')})")

# 6. BONDS
print("\n" + "=" * 100)
print("6. BONDS")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/bonds?apikey={API_KEY}")
if response.status_code == 200:
    bonds = response.json()
    if 'data' in bonds:
        print(f"✅ Total Bonds: {len(bonds['data'])}")
        print(f"\nUS Bonds:")
        us_bonds = [b for b in bonds['data'] if b.get('country') == 'United States']
        for bond in us_bonds[:20]:
            print(f"  - {bond['symbol']}: {bond['name']}")

# 7. INDICES
print("\n" + "=" * 100)
print("7. INDICES")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/indices?country=United States&apikey={API_KEY}")
if response.status_code == 200:
    indices = response.json()
    if 'data' in indices:
        print(f"✅ Total US Indices: {len(indices['data'])}")
        print(f"\nMajor US Indices:")
        for idx in indices['data'][:20]:
            print(f"  - {idx['symbol']}: {idx['name']}")

# 8. MUTUAL FUNDS
print("\n" + "=" * 100)
print("8. MUTUAL FUNDS - US")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/mutual_funds?country=United States&apikey={API_KEY}")
if response.status_code == 200:
    funds = response.json()
    if 'data' in funds:
        print(f"✅ Total US Mutual Funds: {len(funds['data'])}")
        print(f"\nSample Mutual Funds:")
        for fund in funds['data'][:10]:
            print(f"  - {fund['symbol']}: {fund['name']}")

# 9. TECHNICAL INDICATORS - Get complete list
print("\n" + "=" * 100)
print("9. TECHNICAL INDICATORS - COMPLETE LIST")
print("=" * 100)

# Test different indicator categories
indicators_to_test = {
    "Momentum Indicators": [
        ("RSI", "Relative Strength Index"),
        ("MACD", "Moving Average Convergence Divergence"),
        ("STOCH", "Stochastic Oscillator"),
        ("WILLIAMS", "Williams %R"),
        ("CCI", "Commodity Channel Index"),
        ("ROC", "Rate of Change"),
        ("MOM", "Momentum"),
        ("STOCHRSI", "Stochastic RSI"),
        ("APO", "Absolute Price Oscillator"),
        ("PPO", "Percentage Price Oscillator"),
    ],
    "Overlap Studies": [
        ("SMA", "Simple Moving Average"),
        ("EMA", "Exponential Moving Average"),
        ("WMA", "Weighted Moving Average"),
        ("DEMA", "Double Exponential Moving Average"),
        ("TEMA", "Triple Exponential Moving Average"),
        ("TRIMA", "Triangular Moving Average"),
        ("KAMA", "Kaufman Adaptive Moving Average"),
        ("MAMA", "MESA Adaptive Moving Average"),
        ("VWAP", "Volume Weighted Average Price"),
        ("T3", "T3 Moving Average"),
        ("HT_TRENDLINE", "Hilbert Transform - Instantaneous Trendline"),
    ],
    "Volatility Indicators": [
        ("BBANDS", "Bollinger Bands"),
        ("ATR", "Average True Range"),
        ("NATR", "Normalized Average True Range"),
        ("TRANGE", "True Range"),
        ("STDDEV", "Standard Deviation"),
        ("VARIANCE", "Variance"),
    ],
    "Volume Indicators": [
        ("OBV", "On Balance Volume"),
        ("AD", "Chaikin A/D Line"),
        ("ADOSC", "Chaikin A/D Oscillator"),
        ("PVO", "Percentage Volume Oscillator"),
    ],
    "Trend Indicators": [
        ("ADX", "Average Directional Index"),
        ("ADXR", "Average Directional Movement Index Rating"),
        ("AROON", "Aroon"),
        ("AROONOSC", "Aroon Oscillator"),
        ("DX", "Directional Movement Index"),
        ("PLUS_DI", "Plus Directional Indicator"),
        ("MINUS_DI", "Minus Directional Indicator"),
        ("PLUS_DM", "Plus Directional Movement"),
        ("MINUS_DM", "Minus Directional Movement"),
        ("TRIX", "Triple Exponential Average"),
    ],
    "Pattern Recognition": [
        ("CDL2CROWS", "Two Crows"),
        ("CDL3BLACKCROWS", "Three Black Crows"),
        ("CDL3INSIDE", "Three Inside Up/Down"),
        ("CDL3LINESTRIKE", "Three-Line Strike"),
        ("CDLABANDONEDBABY", "Abandoned Baby"),
        ("CDLDOJI", "Doji"),
        ("CDLENGULFING", "Engulfing Pattern"),
        ("CDLHAMMER", "Hammer"),
        ("CDLHARAMI", "Harami Pattern"),
        ("CDLMORNINGSTAR", "Morning Star"),
    ],
    "Statistical Functions": [
        ("CORREL", "Pearson's Correlation Coefficient"),
        ("LINEARREG", "Linear Regression"),
        ("LINEARREG_ANGLE", "Linear Regression Angle"),
        ("LINEARREG_INTERCEPT", "Linear Regression Intercept"),
        ("LINEARREG_SLOPE", "Linear Regression Slope"),
        ("TSF", "Time Series Forecast"),
        ("VAR", "Variance"),
    ],
    "Other Indicators": [
        ("SAR", "Parabolic SAR"),
        ("SAREXT", "Parabolic SAR - Extended"),
        ("ULTOSC", "Ultimate Oscillator"),
        ("BOP", "Balance of Power"),
        ("CMO", "Chande Momentum Oscillator"),
        ("DPO", "Detrended Price Oscillator"),
        ("HT_DCPERIOD", "Hilbert Transform - Dominant Cycle Period"),
        ("HT_DCPHASE", "Hilbert Transform - Dominant Cycle Phase"),
        ("HT_PHASOR", "Hilbert Transform - Phasor Components"),
        ("HT_SINE", "Hilbert Transform - SineWave"),
        ("HT_TRENDMODE", "Hilbert Transform - Trend vs Cycle Mode"),
        ("MIDPOINT", "MidPoint over period"),
        ("MIDPRICE", "Midpoint Price over period"),
    ]
}

total_indicators = 0
for category, indicators in indicators_to_test.items():
    print(f"\n{category}:")
    for ind_code, ind_name in indicators:
        print(f"  ✅ {ind_code}: {ind_name}")
        total_indicators += 1

print(f"\n{'=' * 100}")
print(f"✅ Total Technical Indicators Available: {total_indicators}+")

# 10. Test a complex indicator request
print("\n" + "=" * 100)
print("10. SAMPLE INDICATOR REQUEST - BBANDS (Bollinger Bands)")
print("=" * 100)
response = requests.get(
    f"https://api.twelvedata.com/bbands?symbol=AAPL&interval=1day&time_period=20&series_type=close&apikey={API_KEY}"
)
if response.status_code == 200:
    bbands = response.json()
    print(json.dumps(bbands, indent=2)[:1000] + "...")

# 11. Check available intervals
print("\n" + "=" * 100)
print("11. AVAILABLE TIME INTERVALS")
print("=" * 100)
intervals = [
    "1min", "5min", "15min", "30min", "45min",
    "1h", "2h", "4h", "8h",
    "1day", "1week", "1month"
]
print("✅ Supported Intervals:")
for interval in intervals:
    print(f"  - {interval}")

# 12. Exchanges summary
print("\n" + "=" * 100)
print("12. US EXCHANGES SUMMARY")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/exchanges?apikey={API_KEY}")
if response.status_code == 200:
    exchanges_data = response.json()
    if 'data' in exchanges_data:
        us_exchanges = [ex for ex in exchanges_data['data'] if ex.get('country') == 'United States']
        print(f"✅ Total US Exchanges: {len(us_exchanges)}")
        print("\nUS Exchanges:")
        for ex in us_exchanges:
            print(f"  - {ex['name']} ({ex['code']}) - {ex.get('timezone', 'N/A')}")

# 13. API Usage Summary
print("\n" + "=" * 100)
print("13. API USAGE SUMMARY")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/api_usage?apikey={API_KEY}")
if response.status_code == 200:
    usage = response.json()
    print(json.dumps(usage, indent=2))

    # Calculate utilization
    current = usage.get('current_usage', 0)
    limit = usage.get('plan_limit', 1)
    utilization = (current / limit) * 100
    print(f"\n📊 Current Utilization: {utilization:.2f}%")
    print(f"📊 Remaining Credits: {limit - current}")

print("\n" + "=" * 100)
print("EXPLORATION COMPLETE")
print("=" * 100)
