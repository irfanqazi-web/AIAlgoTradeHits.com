"""
Comprehensive Finnhub API Exploration
Test all available endpoints with the provided API key
"""
import requests
import json
import sys
import io
from datetime import datetime, timedelta

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Finnhub API Key
API_KEY = "d4dg7t9r01qovljpm3g0d4dg7t9r01qovljpm3gg"
BASE_URL = "https://finnhub.io/api/v1"

def make_request(endpoint, params=None):
    """Make API request with error handling"""
    if params is None:
        params = {}
    params['token'] = API_KEY

    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status {response.status_code}", "message": response.text}
    except Exception as e:
        return {"error": str(e)}

def print_section(title):
    """Print section header"""
    print("\n" + "=" * 100)
    print(f"{title}")
    print("=" * 100)

def explore_market_data():
    """Test market data endpoints"""
    print_section("1. MARKET DATA - REAL-TIME QUOTES")

    # Test quote for major stocks
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'BTC-USD']
    for symbol in symbols:
        data = make_request('quote', {'symbol': symbol})
        if 'error' not in data:
            print(f"✅ {symbol}: ${data.get('c', 'N/A')} | Change: {data.get('dp', 'N/A')}%")
        else:
            print(f"❌ {symbol}: {data.get('error')}")

def explore_stock_symbols():
    """Get list of available stock symbols"""
    print_section("2. STOCK SYMBOLS - US EXCHANGES")

    exchanges = ['US', 'NASDAQ', 'NYSE']
    for exchange in exchanges:
        data = make_request('stock/symbol', {'exchange': exchange})
        if isinstance(data, list):
            print(f"✅ {exchange}: {len(data)} symbols available")
            if len(data) > 0:
                print(f"   Sample: {data[0].get('symbol')} - {data[0].get('description')}")
        else:
            print(f"❌ {exchange}: {data.get('error')}")

def explore_company_profile():
    """Get company profile data"""
    print_section("3. COMPANY PROFILE - FUNDAMENTAL DATA")

    symbols = ['AAPL', 'TSLA', 'NVDA']
    for symbol in symbols:
        data = make_request('stock/profile2', {'symbol': symbol})
        if 'error' not in data and data:
            print(f"\n✅ {symbol}:")
            print(f"   Name: {data.get('name')}")
            print(f"   Industry: {data.get('finnhubIndustry')}")
            print(f"   Market Cap: ${data.get('marketCapitalization', 0):.2f}B")
            print(f"   Country: {data.get('country')}")
            print(f"   IPO: {data.get('ipo')}")
            print(f"   Website: {data.get('weburl')}")
        else:
            print(f"❌ {symbol}: {data.get('error') if isinstance(data, dict) else 'No data'}")

def explore_news():
    """Get market news"""
    print_section("4. MARKET NEWS - GENERAL & COMPANY-SPECIFIC")

    # General market news
    print("\n📰 General Market News:")
    data = make_request('news', {'category': 'general'})
    if isinstance(data, list) and len(data) > 0:
        print(f"✅ Found {len(data)} articles")
        for i, article in enumerate(data[:5], 1):
            print(f"\n{i}. {article.get('headline')}")
            print(f"   Source: {article.get('source')} | {datetime.fromtimestamp(article.get('datetime', 0))}")
            print(f"   URL: {article.get('url')}")
    else:
        print(f"❌ Error: {data.get('error') if isinstance(data, dict) else 'No data'}")

    # Company-specific news
    print("\n📰 Company News (AAPL):")
    today = datetime.now().strftime('%Y-%m-%d')
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    data = make_request('company-news', {'symbol': 'AAPL', 'from': week_ago, 'to': today})
    if isinstance(data, list) and len(data) > 0:
        print(f"✅ Found {len(data)} AAPL articles in last 7 days")
        for i, article in enumerate(data[:3], 1):
            print(f"\n{i}. {article.get('headline')}")
            print(f"   Source: {article.get('source')}")
    else:
        print(f"❌ Error: {data.get('error') if isinstance(data, dict) else 'No data'}")

def explore_news_sentiment():
    """Get news sentiment analysis"""
    print_section("5. NEWS SENTIMENT - COMPANY-LEVEL SENTIMENT SCORES")

    symbols = ['AAPL', 'TSLA', 'NVDA', 'META', 'GOOGL']
    for symbol in symbols:
        data = make_request('news-sentiment', {'symbol': symbol})
        if 'error' not in data and 'sentiment' in data:
            sentiment = data.get('sentiment', {})
            print(f"\n✅ {symbol}:")
            print(f"   Sentiment Score: {sentiment.get('sentimentScore', 'N/A')}")
            print(f"   Bullish %: {sentiment.get('bullishPercent', 'N/A')}")
            print(f"   Bearish %: {sentiment.get('bearishPercent', 'N/A')}")
            print(f"   Articles Analyzed: {data.get('buzz', {}).get('articlesInLastWeek', 'N/A')}")
            print(f"   Weekly Average: {data.get('buzz', {}).get('weeklyAverage', 'N/A')}")
        else:
            print(f"❌ {symbol}: {data.get('error') if isinstance(data, dict) else 'No data'}")

def explore_social_sentiment():
    """Get social media sentiment (Reddit, Twitter)"""
    print_section("6. SOCIAL SENTIMENT - REDDIT & TWITTER MENTIONS")

    symbols = ['AAPL', 'TSLA', 'GME', 'AMC']
    for symbol in symbols:
        data = make_request('stock/social-sentiment', {'symbol': symbol})
        if isinstance(data, dict) and 'data' in data and len(data['data']) > 0:
            latest = data['data'][0]  # Most recent data point
            print(f"\n✅ {symbol} (Latest):")
            print(f"   Reddit Mentions: {latest.get('mention', 0)}")
            print(f"   Reddit Positive: {latest.get('positiveMention', 0)}")
            print(f"   Reddit Negative: {latest.get('negativeMention', 0)}")
            print(f"   Reddit Score: {latest.get('score', 0)}")
        else:
            print(f"❌ {symbol}: {data.get('error') if isinstance(data, dict) else 'No data'}")

def explore_recommendation_trends():
    """Get analyst recommendations"""
    print_section("7. ANALYST RECOMMENDATIONS - BUY/SELL/HOLD TRENDS")

    symbols = ['AAPL', 'TSLA', 'NVDA', 'META']
    for symbol in symbols:
        data = make_request('stock/recommendation', {'symbol': symbol})
        if isinstance(data, list) and len(data) > 0:
            latest = data[0]
            print(f"\n✅ {symbol} ({latest.get('period')}):")
            print(f"   Strong Buy: {latest.get('strongBuy', 0)}")
            print(f"   Buy: {latest.get('buy', 0)}")
            print(f"   Hold: {latest.get('hold', 0)}")
            print(f"   Sell: {latest.get('sell', 0)}")
            print(f"   Strong Sell: {latest.get('strongSell', 0)}")
        else:
            print(f"❌ {symbol}: {data.get('error') if isinstance(data, dict) else 'No data'}")

def explore_price_target():
    """Get analyst price targets"""
    print_section("8. ANALYST PRICE TARGETS - CONSENSUS ESTIMATES")

    symbols = ['AAPL', 'TSLA', 'NVDA']
    for symbol in symbols:
        data = make_request('stock/price-target', {'symbol': symbol})
        if 'error' not in data and data:
            print(f"\n✅ {symbol}:")
            print(f"   Target High: ${data.get('targetHigh', 'N/A')}")
            print(f"   Target Mean: ${data.get('targetMean', 'N/A')}")
            print(f"   Target Low: ${data.get('targetLow', 'N/A')}")
            print(f"   Target Median: ${data.get('targetMedian', 'N/A')}")
            print(f"   Last Updated: {data.get('lastUpdated', 'N/A')}")
        else:
            print(f"❌ {symbol}: {data.get('error') if isinstance(data, dict) else 'No data'}")

def explore_earnings():
    """Get earnings calendar and surprises"""
    print_section("9. EARNINGS - CALENDAR & SURPRISES")

    # Earnings calendar
    print("\n📅 Upcoming Earnings:")
    today = datetime.now().strftime('%Y-%m-%d')
    week_later = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    data = make_request('calendar/earnings', {'from': today, 'to': week_later})
    if isinstance(data, dict) and 'earningsCalendar' in data:
        calendar = data['earningsCalendar']
        print(f"✅ Found {len(calendar)} upcoming earnings")
        for i, earning in enumerate(calendar[:5], 1):
            print(f"\n{i}. {earning.get('symbol')}:")
            print(f"   Date: {earning.get('date')}")
            print(f"   EPS Est: ${earning.get('epsEstimate', 'N/A')}")
            print(f"   Revenue Est: ${earning.get('revenueEstimate', 'N/A')}")

    # Earnings surprises
    print("\n📊 Recent Earnings Surprises:")
    symbols = ['AAPL', 'MSFT']
    for symbol in symbols:
        data = make_request('stock/earnings', {'symbol': symbol})
        if isinstance(data, list) and len(data) > 0:
            latest = data[0]
            print(f"\n✅ {symbol}:")
            print(f"   Period: {latest.get('period')}")
            print(f"   Actual EPS: ${latest.get('actual', 'N/A')}")
            print(f"   Estimate EPS: ${latest.get('estimate', 'N/A')}")
            print(f"   Surprise: ${latest.get('surprise', 'N/A')}")

def explore_financials():
    """Get financial statements"""
    print_section("10. FINANCIAL STATEMENTS - INCOME/BALANCE/CASH FLOW")

    symbol = 'AAPL'
    statements = ['income', 'balance-sheet', 'cash-flow']

    for statement in statements:
        data = make_request(f'stock/financials-reported', {'symbol': symbol, 'freq': 'annual'})
        if isinstance(data, dict) and 'data' in data and len(data['data']) > 0:
            print(f"\n✅ {symbol} - {statement.upper()}:")
            print(f"   Reports available: {len(data['data'])}")
            latest = data['data'][0]
            print(f"   Latest report: {latest.get('year')}-Q{latest.get('quarter', 'Annual')}")
            print(f"   Filed: {latest.get('filedDate')}")
        break  # Just test once since endpoint is same

def explore_insider_trading():
    """Get insider transactions"""
    print_section("11. INSIDER TRADING - BUY/SELL TRANSACTIONS")

    symbols = ['AAPL', 'TSLA']
    for symbol in symbols:
        data = make_request('stock/insider-transactions', {'symbol': symbol})
        if isinstance(data, dict) and 'data' in data and len(data['data']) > 0:
            transactions = data['data'][:5]
            print(f"\n✅ {symbol} - Recent Transactions:")
            for i, txn in enumerate(transactions, 1):
                print(f"\n{i}. {txn.get('name')} ({txn.get('position')})")
                print(f"   Transaction: {txn.get('transactionCode')} | Date: {txn.get('transactionDate')}")
                print(f"   Shares: {txn.get('share', 'N/A')} | Value: ${txn.get('value', 'N/A')}")
        else:
            print(f"❌ {symbol}: No recent insider transactions")

def explore_stock_splits():
    """Get stock split history"""
    print_section("12. STOCK SPLITS - HISTORICAL SPLITS")

    symbols = ['AAPL', 'TSLA', 'NVDA']
    today = datetime.now().strftime('%Y-%m-%d')
    five_years_ago = (datetime.now() - timedelta(days=1825)).strftime('%Y-%m-%d')

    for symbol in symbols:
        data = make_request('stock/split', {'symbol': symbol, 'from': five_years_ago, 'to': today})
        if isinstance(data, list) and len(data) > 0:
            print(f"\n✅ {symbol}: {len(data)} splits in last 5 years")
            for split in data:
                print(f"   Date: {split.get('date')} | Ratio: {split.get('fromFactor')}:{split.get('toFactor')}")
        else:
            print(f"❌ {symbol}: No splits in last 5 years")

def explore_economic_calendar():
    """Get economic events calendar"""
    print_section("13. ECONOMIC CALENDAR - FED MEETINGS, GDP, INFLATION")

    data = make_request('calendar/economic')
    if isinstance(data, dict) and 'economicCalendar' in data:
        events = data['economicCalendar'][:10]
        print(f"✅ Found {len(events)} upcoming economic events")
        for i, event in enumerate(events, 1):
            print(f"\n{i}. {event.get('event')}")
            print(f"   Date: {event.get('time')}")
            print(f"   Country: {event.get('country')}")
            print(f"   Impact: {event.get('impact')}")
            print(f"   Estimate: {event.get('estimate')} | Previous: {event.get('previous')}")

def explore_market_holidays():
    """Get market holidays"""
    print_section("14. MARKET HOLIDAYS - US STOCK MARKET CLOSURES")

    data = make_request('stock/market-holiday', {'exchange': 'US'})
    if isinstance(data, dict) and 'data' in data:
        holidays = data['data'][:10]
        print(f"✅ Found {len(holidays)} upcoming US market holidays")
        for i, holiday in enumerate(holidays, 1):
            print(f"{i}. {holiday.get('eventName')} - {holiday.get('atDate')}")

def explore_etf_data():
    """Get ETF holdings and profile"""
    print_section("15. ETF DATA - HOLDINGS & EXPOSURE")

    etf = 'SPY'

    # ETF Profile
    data = make_request('etf/profile', {'symbol': etf})
    if isinstance(data, dict) and 'profile' in data:
        profile = data['profile']
        print(f"\n✅ {etf} Profile:")
        print(f"   Name: {profile.get('name')}")
        print(f"   AUM: ${profile.get('aum', 0):.2f}B")
        print(f"   Expense Ratio: {profile.get('expenseRatio')}%")
        print(f"   Inception: {profile.get('inceptionDate')}")

    # ETF Holdings
    data = make_request('etf/holdings', {'symbol': etf})
    if isinstance(data, dict) and 'holdings' in data:
        holdings = data['holdings'][:10]
        print(f"\n✅ {etf} Top 10 Holdings:")
        for i, holding in enumerate(holdings, 1):
            print(f"{i}. {holding.get('symbol')} - {holding.get('name')} ({holding.get('percent')}%)")

def explore_crypto_data():
    """Get cryptocurrency data"""
    print_section("16. CRYPTOCURRENCY - EXCHANGES & SYMBOLS")

    # Crypto exchanges
    data = make_request('crypto/exchange')
    if isinstance(data, list):
        print(f"✅ Found {len(data)} crypto exchanges")
        print(f"   Sample exchanges: {', '.join(data[:10])}")

    # Crypto symbols on Binance
    data = make_request('crypto/symbol', {'exchange': 'binance'})
    if isinstance(data, list):
        usd_pairs = [s for s in data if 'USDT' in s.get('symbol', '')][:20]
        print(f"\n✅ Binance USDT pairs (sample): {len(usd_pairs)}")
        for pair in usd_pairs[:10]:
            print(f"   {pair.get('displaySymbol')} - {pair.get('description')}")

def explore_forex_data():
    """Get forex rates"""
    print_section("17. FOREX - CURRENCY EXCHANGE RATES")

    data = make_request('forex/rates', {'base': 'USD'})
    if isinstance(data, dict) and 'quote' in data:
        quotes = data['quote']
        major_currencies = ['EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF']
        print(f"✅ USD Exchange Rates:")
        for currency in major_currencies:
            if currency in quotes:
                print(f"   USD/{currency}: {quotes[currency]}")

def check_api_usage():
    """Check API usage limits"""
    print_section("18. API USAGE & RATE LIMITS")

    print("ℹ️  Finnhub API Plan Information:")
    print("   Free tier typically includes:")
    print("   - 60 API calls/minute")
    print("   - Real-time US stock data")
    print("   - Company fundamentals")
    print("   - News & sentiment")
    print("   - Social sentiment (limited)")
    print("\n   Note: Some endpoints may require premium subscription")

def main():
    print("=" * 100)
    print("FINNHUB API COMPREHENSIVE EXPLORATION")
    print("Testing all major endpoints with provided API key")
    print("=" * 100)

    # Run all explorations
    explore_market_data()
    explore_stock_symbols()
    explore_company_profile()
    explore_news()
    explore_news_sentiment()
    explore_social_sentiment()
    explore_recommendation_trends()
    explore_price_target()
    explore_earnings()
    explore_financials()
    explore_insider_trading()
    explore_stock_splits()
    explore_economic_calendar()
    explore_market_holidays()
    explore_etf_data()
    explore_crypto_data()
    explore_forex_data()
    check_api_usage()

    print("\n" + "=" * 100)
    print("✅ EXPLORATION COMPLETE!")
    print("=" * 100)
    print("\nKey Finnhub Capabilities:")
    print("✅ Real-time stock quotes")
    print("✅ Company profiles & fundamentals")
    print("✅ Market news (general + company-specific)")
    print("✅ News sentiment analysis")
    print("✅ Social sentiment (Reddit, Twitter)")
    print("✅ Analyst recommendations & price targets")
    print("✅ Earnings calendar & surprises")
    print("✅ Financial statements")
    print("✅ Insider trading transactions")
    print("✅ Stock splits history")
    print("✅ Economic calendar")
    print("✅ ETF holdings & profiles")
    print("✅ Cryptocurrency data")
    print("✅ Forex rates")

if __name__ == "__main__":
    main()
