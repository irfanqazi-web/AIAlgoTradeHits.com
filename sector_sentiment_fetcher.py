#!/usr/bin/env python3
"""
Sector & Political Sentiment Fetcher
=====================================
Collects sentiment data from multiple sources:
1. TwelveData - Market sentiment by sector
2. Finnhub - News sentiment by sector/industry
3. NewsAPI/Finnhub - Trump statement tracking & impact analysis
4. X.com (Twitter) - Political sentiment (if available)

This data will be integrated with sector classification for improved stock ML predictions.
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json
from google.cloud import bigquery
from datetime import datetime, timedelta
import time

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
ML_DATASET = 'ml_models'

# API Keys (from environment or config)
TWELVEDATA_API_KEY = '2de1c0bb98e34e288d934e7b95a39c5f'
FINNHUB_API_KEY = 'ctm2s4hr01qjgphk2d90ctm2s4hr01qjgphk2d9g'

bq_client = bigquery.Client(project=PROJECT_ID)

print("=" * 70)
print("SECTOR & POLITICAL SENTIMENT FETCHER")
print("=" * 70)
print(f"Started: {datetime.now()}")

# =============================================================================
# STEP 1: Create Sentiment Tables in BigQuery
# =============================================================================
print("\n[1] CREATING SENTIMENT TABLES...")

# Sector Sentiment Table
sector_sentiment_table = f"""
CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{ML_DATASET}.sector_sentiment` (
    date DATE NOT NULL,
    sector STRING NOT NULL,
    sector_code INT64,

    -- Market Sentiment Metrics
    market_sentiment FLOAT64,           -- -1 to 1 (bearish to bullish)
    fear_greed_index FLOAT64,           -- 0 to 100

    -- News Sentiment
    news_sentiment FLOAT64,             -- -1 to 1
    news_volume INT64,                  -- Number of news articles
    positive_news_pct FLOAT64,          -- % positive articles
    negative_news_pct FLOAT64,          -- % negative articles

    -- Social Sentiment
    social_sentiment FLOAT64,           -- -1 to 1
    social_volume INT64,                -- Number of mentions

    -- Sector-specific metrics
    sector_momentum FLOAT64,            -- Relative sector strength
    sector_volatility FLOAT64,          -- Sector volatility index

    -- Political Impact
    political_sentiment FLOAT64,        -- -1 to 1 (negative to positive impact)
    trump_mention_impact FLOAT64,       -- Impact of Trump mentions on sector

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY date
"""

# Political Sentiment Table (Trump statements & market impact)
political_sentiment_table = f"""
CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{ML_DATASET}.political_sentiment` (
    date DATE NOT NULL,
    timestamp TIMESTAMP,

    -- Source Information
    source STRING,                      -- 'twitter', 'news', 'speech', etc.
    headline STRING,
    content_snippet STRING,

    -- Sentiment Analysis
    sentiment_score FLOAT64,            -- -1 to 1
    confidence FLOAT64,                 -- 0 to 1 confidence in sentiment

    -- Market Impact
    mentioned_sectors STRING,           -- Comma-separated sectors mentioned
    mentioned_symbols STRING,           -- Specific stocks mentioned
    expected_impact STRING,             -- 'BULLISH', 'BEARISH', 'NEUTRAL'
    impact_magnitude FLOAT64,           -- 0 to 1 (low to high impact)

    -- Trump-specific
    is_trump_related BOOL DEFAULT FALSE,
    trump_sentiment FLOAT64,            -- Trump's sentiment in statement (-1 to 1)

    -- Keyword flags
    tariff_mention BOOL DEFAULT FALSE,
    trade_war_mention BOOL DEFAULT FALSE,
    fed_mention BOOL DEFAULT FALSE,
    inflation_mention BOOL DEFAULT FALSE,
    jobs_mention BOOL DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY date
"""

try:
    bq_client.query(sector_sentiment_table).result()
    print("  Created: sector_sentiment table")
    bq_client.query(political_sentiment_table).result()
    print("  Created: political_sentiment table")
except Exception as e:
    print(f"  Table creation error: {e}")

# =============================================================================
# STEP 2: Sector-to-Keyword Mapping for News Filtering
# =============================================================================
SECTOR_KEYWORDS = {
    'Technology': ['tech', 'software', 'AI', 'semiconductor', 'chip', 'cloud', 'NVIDIA', 'Microsoft', 'Apple', 'Google', 'Meta', 'Amazon AWS'],
    'Healthcare': ['healthcare', 'pharma', 'biotech', 'drug', 'FDA', 'vaccine', 'hospital', 'medical', 'Pfizer', 'Johnson', 'Merck'],
    'Financials': ['bank', 'finance', 'interest rate', 'Fed', 'JPMorgan', 'Goldman', 'Wall Street', 'credit', 'loan', 'mortgage'],
    'Consumer Discretionary': ['retail', 'consumer', 'Amazon', 'Tesla', 'auto', 'car', 'spending', 'e-commerce', 'Nike', 'McDonald'],
    'Consumer Staples': ['grocery', 'food', 'Walmart', 'Costco', 'Procter', 'Coca-Cola', 'Pepsi', 'consumer goods'],
    'Industrials': ['manufacturing', 'industrial', 'Boeing', 'defense', 'aerospace', 'construction', 'infrastructure'],
    'Energy': ['oil', 'gas', 'energy', 'Exxon', 'Chevron', 'OPEC', 'petroleum', 'drilling', 'renewable'],
    'Materials': ['steel', 'mining', 'chemicals', 'raw materials', 'copper', 'aluminum', 'gold'],
    'Utilities': ['utility', 'electric', 'power', 'grid', 'solar', 'wind', 'nuclear'],
    'Real Estate': ['real estate', 'REIT', 'housing', 'property', 'mortgage', 'commercial real estate'],
    'Communication Services': ['telecom', 'media', 'streaming', 'Netflix', 'Disney', 'AT&T', 'Verizon', '5G'],
}

# Trump-specific keywords that impact markets
TRUMP_MARKET_KEYWORDS = {
    'tariff': {'sectors': ['Industrials', 'Technology', 'Materials'], 'impact': 'BEARISH'},
    'trade war': {'sectors': ['Technology', 'Industrials', 'Materials'], 'impact': 'BEARISH'},
    'china': {'sectors': ['Technology', 'Industrials', 'Consumer Discretionary'], 'impact': 'VARIABLE'},
    'tax cut': {'sectors': ['Financials', 'Consumer Discretionary'], 'impact': 'BULLISH'},
    'deregulation': {'sectors': ['Financials', 'Energy'], 'impact': 'BULLISH'},
    'interest rate': {'sectors': ['Financials', 'Real Estate'], 'impact': 'VARIABLE'},
    'fed': {'sectors': ['Financials', 'Real Estate'], 'impact': 'VARIABLE'},
    'infrastructure': {'sectors': ['Industrials', 'Materials'], 'impact': 'BULLISH'},
    'drill': {'sectors': ['Energy'], 'impact': 'BULLISH'},
    'oil': {'sectors': ['Energy'], 'impact': 'VARIABLE'},
    'big tech': {'sectors': ['Technology', 'Communication Services'], 'impact': 'BEARISH'},
    'antitrust': {'sectors': ['Technology', 'Communication Services'], 'impact': 'BEARISH'},
}

# =============================================================================
# STEP 3: Fetch Finnhub News Sentiment by Sector
# =============================================================================
print("\n[2] FETCHING SECTOR NEWS SENTIMENT (Finnhub)...")

def get_finnhub_news(category='general', min_id=0):
    """Fetch news from Finnhub"""
    url = f"https://finnhub.io/api/v1/news?category={category}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"  Finnhub error: {e}")
    return []

def get_finnhub_company_news(symbol, from_date, to_date):
    """Fetch company-specific news from Finnhub"""
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"  Finnhub company news error: {e}")
    return []

def analyze_sentiment_simple(text):
    """Simple keyword-based sentiment analysis"""
    if not text:
        return 0.0

    text_lower = text.lower()

    positive_words = ['surge', 'rally', 'gain', 'rise', 'bull', 'growth', 'profit', 'beat', 'exceed',
                      'optimistic', 'strong', 'boom', 'soar', 'jump', 'upgrade', 'buy', 'outperform']
    negative_words = ['fall', 'drop', 'crash', 'bear', 'loss', 'miss', 'decline', 'concern', 'fear',
                      'weak', 'cut', 'sell', 'downgrade', 'risk', 'tariff', 'war', 'recession', 'layoff']

    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)

    total = pos_count + neg_count
    if total == 0:
        return 0.0

    return (pos_count - neg_count) / total

def classify_news_by_sector(news_item):
    """Classify a news item into sectors based on keywords"""
    headline = news_item.get('headline', '')
    summary = news_item.get('summary', '')
    text = f"{headline} {summary}".lower()

    matched_sectors = []
    for sector, keywords in SECTOR_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                matched_sectors.append(sector)
                break

    return list(set(matched_sectors)) if matched_sectors else ['General']

# Fetch general market news from multiple categories
print("  Fetching market news from multiple categories...")
general_news = []

# Try multiple Finnhub news categories
for category in ['general', 'forex', 'crypto', 'merger']:
    news = get_finnhub_news(category)
    if news:
        general_news.extend(news)
        print(f"    {category}: {len(news)} articles")
    time.sleep(0.5)  # Respect rate limits

# Also fetch news for major bellwether stocks
bellwether_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'JPM', 'XOM', 'JNJ', 'WMT', 'TSLA', 'NVDA']
today_str = datetime.now().strftime('%Y-%m-%d')
week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

print("  Fetching bellwether company news...")
for symbol in bellwether_stocks:
    news = get_finnhub_company_news(symbol, week_ago, today_str)
    if news:
        general_news.extend(news[:10])  # Max 10 per company
        print(f"    {symbol}: {len(news)} articles")
    time.sleep(0.3)  # Respect rate limits

print(f"  Total retrieved: {len(general_news)} news articles")

# Analyze and categorize news by sector
sector_news_sentiment = {sector: {'articles': [], 'sentiment_sum': 0, 'count': 0}
                         for sector in SECTOR_KEYWORDS.keys()}

for news in general_news:
    sectors = classify_news_by_sector(news)
    sentiment = analyze_sentiment_simple(news.get('headline', '') + ' ' + news.get('summary', ''))

    for sector in sectors:
        if sector in sector_news_sentiment:
            sector_news_sentiment[sector]['articles'].append(news)
            sector_news_sentiment[sector]['sentiment_sum'] += sentiment
            sector_news_sentiment[sector]['count'] += 1

# =============================================================================
# STEP 4: Detect Trump-Related News and Analyze Impact
# =============================================================================
print("\n[3] ANALYZING TRUMP-RELATED NEWS & MARKET IMPACT...")

trump_keywords = ['trump', 'president trump', 'donald trump', 'potus', 'white house',
                  'trump administration', 'trump policy', 'trump statement', 'trump tariff']

trump_related_news = []
for news in general_news:
    headline = news.get('headline', '').lower()
    summary = news.get('summary', '').lower()
    text = f"{headline} {summary}"

    # Check if Trump-related
    is_trump_related = any(kw in text for kw in trump_keywords)
    if not is_trump_related:
        continue

    # Analyze market impact
    sentiment = analyze_sentiment_simple(text)

    # Detect market-moving keywords
    impacts = []
    affected_sectors = set()
    for keyword, info in TRUMP_MARKET_KEYWORDS.items():
        if keyword in text:
            impacts.append(info['impact'])
            affected_sectors.update(info['sectors'])

    trump_news_item = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.fromtimestamp(news.get('datetime', time.time())).isoformat(),
        'source': news.get('source', 'unknown'),
        'headline': news.get('headline', '')[:500],
        'content_snippet': news.get('summary', '')[:1000],
        'sentiment_score': sentiment,
        'confidence': 0.7,  # Base confidence
        'mentioned_sectors': ','.join(affected_sectors) if affected_sectors else '',
        'mentioned_symbols': '',
        'expected_impact': impacts[0] if impacts else 'NEUTRAL',
        'impact_magnitude': min(1.0, len(impacts) * 0.3),
        'is_trump_related': True,
        'trump_sentiment': sentiment,
        'tariff_mention': 'tariff' in text,
        'trade_war_mention': 'trade war' in text or 'trade' in text,
        'fed_mention': 'fed' in text or 'federal reserve' in text,
        'inflation_mention': 'inflation' in text,
        'jobs_mention': 'job' in text or 'employment' in text or 'unemployment' in text,
    }
    trump_related_news.append(trump_news_item)

print(f"  Found {len(trump_related_news)} Trump-related news articles")

# =============================================================================
# STEP 5: Fetch Additional Sentiment from TwelveData (if available)
# =============================================================================
print("\n[4] CHECKING TWELVEDATA SENTIMENT ENDPOINTS...")

def get_twelvedata_market_state():
    """Get market state from TwelveData"""
    url = f"https://api.twelvedata.com/market_state?apikey={TWELVEDATA_API_KEY}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"  TwelveData error: {e}")
    return {}

market_state = get_twelvedata_market_state()
if market_state:
    print(f"  Market state retrieved: {len(market_state)} exchanges")

# =============================================================================
# STEP 6: Build Sector Sentiment Records
# =============================================================================
print("\n[5] BUILDING SECTOR SENTIMENT RECORDS...")

SECTOR_CODES = {
    'Technology': 1, 'Healthcare': 2, 'Financials': 3,
    'Consumer Discretionary': 4, 'Consumer Staples': 5,
    'Industrials': 6, 'Energy': 7, 'Materials': 8,
    'Utilities': 9, 'Real Estate': 10, 'Communication Services': 11,
}

sector_sentiment_records = []
today = datetime.now().strftime('%Y-%m-%d')

for sector, data in sector_news_sentiment.items():
    count = data['count']
    avg_sentiment = data['sentiment_sum'] / count if count > 0 else 0.0

    # Calculate Trump impact on this sector
    trump_impact = 0.0
    for tn in trump_related_news:
        if sector in tn.get('mentioned_sectors', ''):
            impact_sign = 1 if tn['expected_impact'] == 'BULLISH' else -1 if tn['expected_impact'] == 'BEARISH' else 0
            trump_impact += tn['sentiment_score'] * impact_sign * tn['impact_magnitude']

    record = {
        'date': today,
        'sector': sector,
        'sector_code': SECTOR_CODES.get(sector, 0),
        'market_sentiment': avg_sentiment,
        'fear_greed_index': 50 + (avg_sentiment * 25),  # Convert to 0-100 scale
        'news_sentiment': avg_sentiment,
        'news_volume': count,
        'positive_news_pct': sum(1 for a in data['articles'] if analyze_sentiment_simple(a.get('headline', '')) > 0) / max(count, 1) * 100,
        'negative_news_pct': sum(1 for a in data['articles'] if analyze_sentiment_simple(a.get('headline', '')) < 0) / max(count, 1) * 100,
        'social_sentiment': 0.0,  # Would need Twitter/X API
        'social_volume': 0,
        'sector_momentum': 0.0,  # Will be calculated from price data
        'sector_volatility': 0.0,  # Will be calculated from price data
        'political_sentiment': trump_impact / max(len(trump_related_news), 1),
        'trump_mention_impact': trump_impact,
    }
    sector_sentiment_records.append(record)

# =============================================================================
# STEP 7: Upload to BigQuery
# =============================================================================
print("\n[6] UPLOADING SENTIMENT DATA TO BIGQUERY...")

import pandas as pd

# Upload sector sentiment using SQL INSERT (more reliable than dataframe)
if sector_sentiment_records:
    table_ref = f"{PROJECT_ID}.{ML_DATASET}.sector_sentiment"

    # Delete today's data if exists (to allow re-runs)
    delete_query = f"DELETE FROM `{table_ref}` WHERE date = '{today}'"
    try:
        bq_client.query(delete_query).result()
    except:
        pass

    # Insert records one by one
    inserted = 0
    for record in sector_sentiment_records:
        insert_query = f"""
        INSERT INTO `{table_ref}` (
            date, sector, sector_code, market_sentiment, fear_greed_index,
            news_sentiment, news_volume, positive_news_pct, negative_news_pct,
            social_sentiment, social_volume, sector_momentum, sector_volatility,
            political_sentiment, trump_mention_impact
        ) VALUES (
            DATE '{record['date']}',
            '{record['sector']}',
            {record['sector_code']},
            {record['market_sentiment']},
            {record['fear_greed_index']},
            {record['news_sentiment']},
            {record['news_volume']},
            {record['positive_news_pct']},
            {record['negative_news_pct']},
            {record['social_sentiment']},
            {record['social_volume']},
            {record['sector_momentum']},
            {record['sector_volatility']},
            {record['political_sentiment']},
            {record['trump_mention_impact']}
        )
        """
        try:
            bq_client.query(insert_query).result()
            inserted += 1
        except Exception as e:
            print(f"    Error inserting {record['sector']}: {e}")

    print(f"  Uploaded {inserted} sector sentiment records")

# Upload political sentiment (Trump news)
if trump_related_news:
    table_ref = f"{PROJECT_ID}.{ML_DATASET}.political_sentiment"

    # Delete today's data if exists
    delete_query = f"DELETE FROM `{table_ref}` WHERE date = '{today}'"
    try:
        bq_client.query(delete_query).result()
    except:
        pass

    inserted = 0
    for tn in trump_related_news:
        # Escape single quotes in text
        headline = tn['headline'].replace("'", "''")
        snippet = tn['content_snippet'].replace("'", "''")
        source = tn['source'].replace("'", "''")

        insert_query = f"""
        INSERT INTO `{table_ref}` (
            date, timestamp, source, headline, content_snippet,
            sentiment_score, confidence, mentioned_sectors, mentioned_symbols,
            expected_impact, impact_magnitude, is_trump_related, trump_sentiment,
            tariff_mention, trade_war_mention, fed_mention, inflation_mention, jobs_mention
        ) VALUES (
            DATE '{tn['date']}',
            TIMESTAMP '{tn['timestamp']}',
            '{source}',
            '{headline}',
            '{snippet}',
            {tn['sentiment_score']},
            {tn['confidence']},
            '{tn['mentioned_sectors']}',
            '{tn['mentioned_symbols']}',
            '{tn['expected_impact']}',
            {tn['impact_magnitude']},
            {str(tn['is_trump_related']).upper()},
            {tn['trump_sentiment']},
            {str(tn['tariff_mention']).upper()},
            {str(tn['trade_war_mention']).upper()},
            {str(tn['fed_mention']).upper()},
            {str(tn['inflation_mention']).upper()},
            {str(tn['jobs_mention']).upper()}
        )
        """
        try:
            bq_client.query(insert_query).result()
            inserted += 1
        except Exception as e:
            print(f"    Error inserting trump news: {str(e)[:100]}")

    print(f"  Uploaded {inserted} political/Trump sentiment records")

# =============================================================================
# STEP 8: Display Summary
# =============================================================================
print("\n" + "=" * 70)
print("SENTIMENT SUMMARY")
print("=" * 70)

print("\nSector Sentiment Overview:")
print("-" * 70)
print(f"{'Sector':30} | {'News':>5} | {'Sentiment':>10} | {'Trump Impact':>12}")
print("-" * 70)

for record in sorted(sector_sentiment_records, key=lambda x: x['news_sentiment'], reverse=True):
    sentiment_str = f"{record['news_sentiment']:+.2f}"
    trump_str = f"{record['trump_mention_impact']:+.2f}" if record['trump_mention_impact'] != 0 else "N/A"
    print(f"{record['sector']:30} | {record['news_volume']:>5} | {sentiment_str:>10} | {trump_str:>12}")

if trump_related_news:
    print(f"\nTrump-Related News: {len(trump_related_news)} articles found")
    print("-" * 70)
    for tn in trump_related_news[:5]:  # Show top 5
        print(f"  [{tn['expected_impact']}] {tn['headline'][:60]}...")
        if tn['mentioned_sectors']:
            print(f"    Sectors: {tn['mentioned_sectors']}")

print("\n" + "=" * 70)
print("SECTOR SENTIMENT FETCH COMPLETE")
print("=" * 70)
print(f"\nCompleted: {datetime.now()}")
print(f"\nNext: Run create_sector_enhanced_features.py to build ML training data")
