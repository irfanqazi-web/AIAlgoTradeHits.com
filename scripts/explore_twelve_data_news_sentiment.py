import requests
import json
import sys
import io

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_KEY = "16ee060fd4d34a628a14bcb6f0167565"

print("=" * 100)
print("TWELVE DATA - NEWS, SENTIMENT & COMPLETE BREAKDOWN")
print("=" * 100)

# 1. NEWS API - Check if available
print("\n" + "=" * 100)
print("1. NEWS API - Available Endpoints")
print("=" * 100)

# Test news for a major stock
print("\nTesting News API for AAPL:")
response = requests.get(f"https://api.twelvedata.com/news?symbol=AAPL&apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    news = response.json()
    print(json.dumps(news, indent=2)[:2000])
else:
    print(f"Response: {response.text[:500]}")

# 2. SENTIMENT ANALYSIS
print("\n" + "=" * 100)
print("2. SENTIMENT ANALYSIS")
print("=" * 100)
print("\nChecking if sentiment endpoint is available:")
response = requests.get(f"https://api.twelvedata.com/sentiment?symbol=AAPL&apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    sentiment = response.json()
    print(json.dumps(sentiment, indent=2)[:1000])
else:
    print(f"Response: {response.text[:500]}")

# 3. ALL COUNTRIES
print("\n" + "=" * 100)
print("3. ALL COUNTRIES WITH STOCK DATA")
print("=" * 100)

# Get all stocks and extract unique countries
response = requests.get(f"https://api.twelvedata.com/stocks?apikey={API_KEY}")
if response.status_code == 200:
    all_stocks = response.json()
    if 'data' in all_stocks:
        countries = {}
        for stock in all_stocks['data']:
            country = stock.get('country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1

        print(f"✅ Total Countries: {len(countries)}")
        print(f"\nCountries by Stock Count:")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:30]:
            print(f"  - {country}: {count} stocks")

# 4. ALL EXCHANGES
print("\n" + "=" * 100)
print("4. ALL EXCHANGES - COMPLETE LIST")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/exchanges?apikey={API_KEY}")
if response.status_code == 200:
    exchanges = response.json()
    if 'data' in exchanges:
        print(f"✅ Total Exchanges: {len(exchanges['data'])}")

        # Group by country
        by_country = {}
        for ex in exchanges['data']:
            country = ex.get('country', 'Unknown')
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(ex)

        print(f"\n✅ Countries with Exchanges: {len(by_country)}")
        print(f"\nExchanges by Country:")
        for country in sorted(by_country.keys()):
            exs = by_country[country]
            print(f"\n  {country} ({len(exs)} exchanges):")
            for ex in exs[:5]:  # Show first 5
                print(f"    - {ex['name']} ({ex['code']}) [{ex.get('timezone', 'N/A')}]")
            if len(exs) > 5:
                print(f"    ... and {len(exs) - 5} more")

# 5. CRYPTOCURRENCY EXCHANGES
print("\n" + "=" * 100)
print("5. CRYPTOCURRENCY EXCHANGES")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/cryptocurrency_exchanges?apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    crypto_ex = response.json()
    if 'data' in crypto_ex:
        print(f"✅ Total Crypto Exchanges: {len(crypto_ex['data'])}")
        print(f"\nCrypto Exchanges:")
        for ex in crypto_ex['data'][:30]:
            print(f"  - {ex['name']}")
    else:
        print(json.dumps(crypto_ex, indent=2)[:1000])
else:
    print(f"Response: {response.text[:500]}")

# 6. EARNINGS CALENDAR
print("\n" + "=" * 100)
print("6. EARNINGS CALENDAR")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/earnings_calendar?symbol=AAPL&apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    earnings = response.json()
    print(json.dumps(earnings, indent=2)[:1000])
else:
    print(f"Response: {response.text[:500]}")

# 7. DIVIDENDS
print("\n" + "=" * 100)
print("7. DIVIDENDS DATA")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/dividends?symbol=AAPL&apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    dividends = response.json()
    print(json.dumps(dividends, indent=2)[:1000])
else:
    print(f"Response: {response.text[:500]}")

# 8. STOCK SPLITS
print("\n" + "=" * 100)
print("8. STOCK SPLITS DATA")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/splits?symbol=AAPL&apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    splits = response.json()
    print(json.dumps(splits, indent=2)[:1000])
else:
    print(f"Response: {response.text[:500]}")

# 9. COMPANY PROFILE / LOGO
print("\n" + "=" * 100)
print("9. COMPANY PROFILE & LOGO")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/profile?symbol=AAPL&apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    profile = response.json()
    print(json.dumps(profile, indent=2)[:1500])
else:
    print(f"Response: {response.text[:500]}")

# 10. LOGO URL
print("\n" + "=" * 100)
print("10. COMPANY LOGO")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/logo?symbol=AAPL&apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    logo = response.json()
    print(json.dumps(logo, indent=2))
else:
    print(f"Response: {response.text[:500]}")

# 11. STATISTICS
print("\n" + "=" * 100)
print("11. KEY STATISTICS")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/statistics?symbol=AAPL&apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    stats = response.json()
    print(json.dumps(stats, indent=2)[:1500])
else:
    print(f"Response: {response.text[:500]}")

# 12. OPTIONS CHAIN (if available)
print("\n" + "=" * 100)
print("12. OPTIONS DATA")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/options/chain?symbol=AAPL&apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    options = response.json()
    print(json.dumps(options, indent=2)[:1000])
else:
    print(f"Response: {response.text[:500]}")

# 13. INSIDER TRANSACTIONS
print("\n" + "=" * 100)
print("13. INSIDER TRANSACTIONS")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/insider_transactions?symbol=AAPL&apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    insider = response.json()
    print(json.dumps(insider, indent=2)[:1000])
else:
    print(f"Response: {response.text[:500]}")

# 14. INCOME STATEMENT
print("\n" + "=" * 100)
print("14. INCOME STATEMENT (FUNDAMENTALS)")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/income_statement?symbol=AAPL&apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    income = response.json()
    print(json.dumps(income, indent=2)[:1500])
else:
    print(f"Response: {response.text[:500]}")

# 15. BALANCE SHEET
print("\n" + "=" * 100)
print("15. BALANCE SHEET (FUNDAMENTALS)")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/balance_sheet?symbol=AAPL&apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    balance = response.json()
    print(json.dumps(balance, indent=2)[:1500])
else:
    print(f"Response: {response.text[:500]}")

# 16. CASH FLOW
print("\n" + "=" * 100)
print("16. CASH FLOW STATEMENT")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/cash_flow?symbol=AAPL&apikey={API_KEY}")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    cashflow = response.json()
    print(json.dumps(cashflow, indent=2)[:1500])
else:
    print(f"Response: {response.text[:500]}")

# API Usage
print("\n" + "=" * 100)
print("17. FINAL API USAGE")
print("=" * 100)
response = requests.get(f"https://api.twelvedata.com/api_usage?apikey={API_KEY}")
if response.status_code == 200:
    usage = response.json()
    print(json.dumps(usage, indent=2))

print("\n" + "=" * 100)
print("COMPLETE EXPLORATION FINISHED")
print("=" * 100)
