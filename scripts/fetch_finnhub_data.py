"""
Finnhub Data Fetcher - News, Analyst Recommendations, Insider Trading, Earnings
Uses FREE tier of Finnhub API (60 calls/minute)

Author: Claude Code
Date: December 2025
"""

import os
import sys
import io
import time
import json
import requests
from datetime import datetime, timedelta, timezone
from google.cloud import bigquery

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
FINNHUB_API_KEY = 'd4dg7t9r01qovljpm3g0d4dg7t9r01qovljpm3gg'
FINNHUB_BASE_URL = 'https://finnhub.io/api/v1'

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# Top stocks to track
TOP_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'XOM',
    'JNJ', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV', 'LLY',
    'COST', 'PEP', 'KO', 'WMT', 'BAC', 'AVGO', 'PFE', 'CSCO', 'TMO', 'MCD',
    'CRM', 'ACN', 'DHR', 'ABT', 'LIN', 'CMCSA', 'NKE', 'ADBE', 'TXN', 'VZ'
]


def make_request(endpoint, params=None):
    """Make Finnhub API request with rate limiting"""
    if params is None:
        params = {}
    params['token'] = FINNHUB_API_KEY

    try:
        response = requests.get(f"{FINNHUB_BASE_URL}/{endpoint}", params=params, timeout=15)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Status {response.status_code}: {response.text}"
    except Exception as e:
        return None, str(e)


def create_tables_if_not_exist():
    """Create BigQuery tables for Finnhub data"""

    # Market News table
    news_schema = [
        bigquery.SchemaField('id', 'INTEGER'),
        bigquery.SchemaField('category', 'STRING'),
        bigquery.SchemaField('datetime', 'TIMESTAMP'),
        bigquery.SchemaField('headline', 'STRING'),
        bigquery.SchemaField('image', 'STRING'),
        bigquery.SchemaField('related', 'STRING'),
        bigquery.SchemaField('source', 'STRING'),
        bigquery.SchemaField('summary', 'STRING'),
        bigquery.SchemaField('url', 'STRING'),
        bigquery.SchemaField('fetch_timestamp', 'TIMESTAMP'),
    ]

    # Analyst Recommendations table
    recommendations_schema = [
        bigquery.SchemaField('symbol', 'STRING'),
        bigquery.SchemaField('period', 'DATE'),
        bigquery.SchemaField('strong_buy', 'INTEGER'),
        bigquery.SchemaField('buy', 'INTEGER'),
        bigquery.SchemaField('hold', 'INTEGER'),
        bigquery.SchemaField('sell', 'INTEGER'),
        bigquery.SchemaField('strong_sell', 'INTEGER'),
        bigquery.SchemaField('total_analysts', 'INTEGER'),
        bigquery.SchemaField('consensus', 'STRING'),
        bigquery.SchemaField('fetch_timestamp', 'TIMESTAMP'),
    ]

    # Insider Transactions table (already exists based on table list)
    insider_schema = [
        bigquery.SchemaField('symbol', 'STRING'),
        bigquery.SchemaField('name', 'STRING'),
        bigquery.SchemaField('position', 'STRING'),
        bigquery.SchemaField('transaction_code', 'STRING'),
        bigquery.SchemaField('transaction_date', 'DATE'),
        bigquery.SchemaField('transaction_price', 'FLOAT64'),
        bigquery.SchemaField('shares', 'INTEGER'),
        bigquery.SchemaField('value', 'FLOAT64'),
        bigquery.SchemaField('filing_date', 'DATE'),
        bigquery.SchemaField('change', 'INTEGER'),
        bigquery.SchemaField('fetch_timestamp', 'TIMESTAMP'),
    ]

    # Company News table
    company_news_schema = [
        bigquery.SchemaField('symbol', 'STRING'),
        bigquery.SchemaField('id', 'INTEGER'),
        bigquery.SchemaField('category', 'STRING'),
        bigquery.SchemaField('datetime', 'TIMESTAMP'),
        bigquery.SchemaField('headline', 'STRING'),
        bigquery.SchemaField('image', 'STRING'),
        bigquery.SchemaField('source', 'STRING'),
        bigquery.SchemaField('summary', 'STRING'),
        bigquery.SchemaField('url', 'STRING'),
        bigquery.SchemaField('fetch_timestamp', 'TIMESTAMP'),
    ]

    tables = {
        'market_news': news_schema,
        'finnhub_analyst_recommendations': recommendations_schema,
        'finnhub_insider_transactions': insider_schema,
        'company_news': company_news_schema,
    }

    for table_name, schema in tables.items():
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        try:
            client.get_table(table_id)
            print(f"  Table {table_name} exists")
        except Exception:
            table = bigquery.Table(table_id, schema=schema)
            client.create_table(table)
            print(f"  Created table {table_name}")


def fetch_market_news():
    """Fetch general market news"""
    print("\n=== FETCHING MARKET NEWS ===")

    categories = ['general', 'forex', 'crypto', 'merger']
    all_articles = []

    for category in categories:
        data, error = make_request('news', {'category': category})
        if error:
            print(f"  Error fetching {category} news: {error}")
            continue

        if data:
            for article in data[:25]:  # Top 25 per category
                all_articles.append({
                    'id': article.get('id'),
                    'category': article.get('category'),
                    'datetime': datetime.fromtimestamp(article.get('datetime', 0), tz=timezone.utc).isoformat() if article.get('datetime') else None,
                    'headline': article.get('headline', '')[:1000],
                    'image': article.get('image', '')[:500],
                    'related': article.get('related', '')[:100],
                    'source': article.get('source', '')[:100],
                    'summary': article.get('summary', '')[:2000],
                    'url': article.get('url', '')[:500],
                    'fetch_timestamp': datetime.now(timezone.utc).isoformat()
                })
            print(f"  Fetched {len(data)} {category} articles")
        time.sleep(1)  # Rate limiting

    if all_articles:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.market_news"
        errors = client.insert_rows_json(table_id, all_articles)
        if errors:
            print(f"  Insert errors: {errors[:3]}")
        else:
            print(f"  Inserted {len(all_articles)} news articles")

    return len(all_articles)


def fetch_analyst_recommendations():
    """Fetch analyst recommendations for top stocks"""
    print("\n=== FETCHING ANALYST RECOMMENDATIONS ===")

    recommendations = []

    for i, symbol in enumerate(TOP_STOCKS, 1):
        data, error = make_request('stock/recommendation', {'symbol': symbol})

        if error:
            print(f"  [{i}/{len(TOP_STOCKS)}] {symbol}: Error - {error}")
            continue

        if data and len(data) > 0:
            latest = data[0]
            total = (latest.get('strongBuy', 0) + latest.get('buy', 0) +
                     latest.get('hold', 0) + latest.get('sell', 0) + latest.get('strongSell', 0))

            # Determine consensus
            strong_buy = latest.get('strongBuy', 0)
            buy = latest.get('buy', 0)
            hold = latest.get('hold', 0)
            sell = latest.get('sell', 0)
            strong_sell = latest.get('strongSell', 0)

            bullish = strong_buy + buy
            bearish = sell + strong_sell

            if bullish > bearish * 2:
                consensus = 'Strong Buy'
            elif bullish > bearish:
                consensus = 'Buy'
            elif bearish > bullish * 2:
                consensus = 'Strong Sell'
            elif bearish > bullish:
                consensus = 'Sell'
            else:
                consensus = 'Hold'

            recommendations.append({
                'symbol': symbol,
                'period': latest.get('period'),
                'strong_buy': strong_buy,
                'buy': buy,
                'hold': hold,
                'sell': sell,
                'strong_sell': strong_sell,
                'total_analysts': total,
                'consensus': consensus,
                'fetch_timestamp': datetime.now(timezone.utc).isoformat()
            })
            print(f"  [{i}/{len(TOP_STOCKS)}] {symbol}: {consensus} ({total} analysts)")
        else:
            print(f"  [{i}/{len(TOP_STOCKS)}] {symbol}: No data")

        time.sleep(1)  # Rate limiting (60 calls/min)

    if recommendations:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.finnhub_analyst_recommendations"
        errors = client.insert_rows_json(table_id, recommendations)
        if errors:
            print(f"  Insert errors: {errors[:3]}")
        else:
            print(f"  Inserted {len(recommendations)} recommendations")

    return len(recommendations)


def fetch_insider_transactions():
    """Fetch insider transactions for top stocks"""
    print("\n=== FETCHING INSIDER TRANSACTIONS ===")

    transactions = []
    from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')

    for i, symbol in enumerate(TOP_STOCKS[:20], 1):  # Limit to top 20 to save API calls
        data, error = make_request('stock/insider-transactions', {
            'symbol': symbol,
            'from': from_date,
            'to': to_date
        })

        if error:
            print(f"  [{i}/20] {symbol}: Error - {error}")
            continue

        if data and 'data' in data:
            for txn in data['data'][:10]:  # Top 10 per symbol
                transactions.append({
                    'symbol': symbol,
                    'name': txn.get('name', '')[:200],
                    'position': txn.get('position', '')[:200],
                    'transaction_code': txn.get('transactionCode', ''),
                    'transaction_date': txn.get('transactionDate'),
                    'transaction_price': txn.get('transactionPrice'),
                    'shares': int(txn.get('share', 0)) if txn.get('share') else 0,
                    'value': txn.get('value'),
                    'filing_date': txn.get('filingDate'),
                    'change': int(txn.get('change', 0)) if txn.get('change') else 0,
                    'fetch_timestamp': datetime.now(timezone.utc).isoformat()
                })
            print(f"  [{i}/20] {symbol}: {len(data['data'])} transactions")
        else:
            print(f"  [{i}/20] {symbol}: No transactions")

        time.sleep(1)

    if transactions:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.finnhub_insider_transactions"
        errors = client.insert_rows_json(table_id, transactions)
        if errors:
            print(f"  Insert errors: {errors[:3]}")
        else:
            print(f"  Inserted {len(transactions)} transactions")

    return len(transactions)


def fetch_company_news():
    """Fetch company-specific news for top stocks"""
    print("\n=== FETCHING COMPANY NEWS ===")

    all_news = []
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')

    for i, symbol in enumerate(TOP_STOCKS[:15], 1):  # Limit to 15 to save API calls
        data, error = make_request('company-news', {
            'symbol': symbol,
            'from': from_date,
            'to': to_date
        })

        if error:
            print(f"  [{i}/15] {symbol}: Error - {error}")
            continue

        if data:
            for article in data[:10]:  # Top 10 per symbol
                all_news.append({
                    'symbol': symbol,
                    'id': article.get('id'),
                    'category': article.get('category', '')[:100],
                    'datetime': datetime.fromtimestamp(article.get('datetime', 0), tz=timezone.utc).isoformat() if article.get('datetime') else None,
                    'headline': article.get('headline', '')[:1000],
                    'image': article.get('image', '')[:500],
                    'source': article.get('source', '')[:100],
                    'summary': article.get('summary', '')[:2000],
                    'url': article.get('url', '')[:500],
                    'fetch_timestamp': datetime.now(timezone.utc).isoformat()
                })
            print(f"  [{i}/15] {symbol}: {len(data)} articles")
        else:
            print(f"  [{i}/15] {symbol}: No news")

        time.sleep(1)

    if all_news:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.company_news"
        errors = client.insert_rows_json(table_id, all_news)
        if errors:
            print(f"  Insert errors: {errors[:3]}")
        else:
            print(f"  Inserted {len(all_news)} company news articles")

    return len(all_news)


def fetch_earnings_calendar():
    """Fetch upcoming earnings"""
    print("\n=== FETCHING EARNINGS CALENDAR ===")

    from_date = datetime.now().strftime('%Y-%m-%d')
    to_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')

    data, error = make_request('calendar/earnings', {
        'from': from_date,
        'to': to_date
    })

    if error:
        print(f"  Error: {error}")
        return 0

    if data and 'earningsCalendar' in data:
        earnings = data['earningsCalendar']
        print(f"  Found {len(earnings)} upcoming earnings in next 14 days")

        # Update earnings_calendar table
        table_id = f"{PROJECT_ID}.{DATASET_ID}.earnings_calendar"

        earnings_rows = []
        for e in earnings[:100]:  # Top 100
            earnings_rows.append({
                'symbol': e.get('symbol'),
                'date': e.get('date'),
                'eps_estimate': e.get('epsEstimate'),
                'eps_actual': e.get('epsActual'),
                'revenue_estimate': e.get('revenueEstimate'),
                'revenue_actual': e.get('revenueActual'),
                'hour': e.get('hour'),
                'quarter': e.get('quarter'),
                'year': e.get('year'),
                'fetch_timestamp': datetime.now(timezone.utc).isoformat()
            })

        if earnings_rows:
            errors = client.insert_rows_json(table_id, earnings_rows)
            if errors:
                print(f"  Insert errors: {errors[:3]}")
            else:
                print(f"  Inserted {len(earnings_rows)} earnings records")

        return len(earnings)

    return 0


def main():
    """Main execution"""
    print("="*60)
    print("FINNHUB DATA FETCHER")
    print("="*60)
    print(f"Start time: {datetime.now()}")
    print(f"API: Finnhub FREE tier (60 calls/minute)")

    # Create tables if needed
    print("\n=== CHECKING TABLES ===")
    create_tables_if_not_exist()

    # Fetch all data
    total = 0

    total += fetch_market_news()
    total += fetch_analyst_recommendations()
    total += fetch_insider_transactions()
    total += fetch_company_news()
    total += fetch_earnings_calendar()

    print("\n" + "="*60)
    print(f"FINNHUB FETCH COMPLETE")
    print(f"Total records fetched: {total}")
    print(f"End time: {datetime.now()}")
    print("="*60)


if __name__ == '__main__':
    main()
