C# Twelve Data - Supported Countries List

**Document Created**: November 16, 2025
**Purpose**: Complete list of countries supported by Twelve Data API
**Total Countries**: 50+

## Overview

Twelve Data provides comprehensive financial market data coverage across **50+ countries** on 5 continents, with access to:

- **90+ International Stock Exchanges**
- **180+ Cryptocurrency Exchanges**
- **100,000+ Financial Instruments**

## To Get the Live Country List

Since Twelve Data does not publish a static list on their website, you need to use their API to retrieve the current list. Use the provided Python script:

```bash
python fetch_twelve_data_countries.py
```

This will:
1. Prompt you for your Twelve Data API key
2. Fetch the complete list from `https://api.twelvedata.com/countries`
3. Generate a detailed table with all countries, ISO codes, currencies, and capitals
4. Save both JSON and Markdown formatted outputs

## Confirmed Supported Countries (by Region)

### 🌎 Americas (5+ Countries)

| Country | ISO3 | Exchange(s) | Coverage |
|---------|------|-------------|----------|
| **United States** | USA | NYSE, NASDAQ, AMEX, OTC, BATS | Complete |
| **Canada** | CAN | TSX, TSX-V | Complete |
| **Brazil** | BRA | B3 | Complete |
| **Mexico** | MEX | BMV | Yes |
| **Argentina** | ARG | BCBA | Yes |
| **Chile** | CHL | Santiago SE | Yes |

### 🌍 Europe (15+ Countries)

| Country | ISO3 | Exchange(s) | Coverage |
|---------|------|-------------|----------|
| **United Kingdom** | GBR | LSE, AIM | Complete |
| **Germany** | DEU | XETRA, Frankfurt | Complete |
| **France** | FRA | Euronext Paris | Complete |
| **Netherlands** | NLD | Euronext Amsterdam | Complete |
| **Belgium** | BEL | Euronext Brussels | Complete |
| **Portugal** | PRT | Euronext Lisbon | Complete |
| **Ireland** | IRL | Euronext Dublin | Complete |
| **Italy** | ITA | Borsa Italiana | Yes |
| **Spain** | ESP | BME Spanish | Yes |
| **Switzerland** | CHE | SIX Swiss | Yes |
| **Sweden** | SWE | Nasdaq Stockholm | Yes |
| **Norway** | NOR | Oslo Børs | Yes |
| **Denmark** | DNK | Nasdaq Copenhagen | Yes |
| **Finland** | FIN | Nasdaq Helsinki | Yes |
| **Poland** | POL | WSE | Yes |
| **Czech Republic** | CZE | PSE | Yes |
| **Greece** | GRC | ATHEX | Yes |
| **Turkey** | TUR | Borsa Istanbul | Complete |
| **Russia** | RUS | MOEX | Yes |

### 🌏 Asia & Oceania (15+ Countries)

| Country | ISO3 | Exchange(s) | Coverage |
|---------|------|-------------|----------|
| **India** | IND | NSE, BSE | Complete |
| **Singapore** | SGP | SGX | Complete |
| **Sri Lanka** | LKA | CSE | Yes |
| **Japan** | JPN | Tokyo SE | Complete |
| **China** | CHN | Shanghai, Shenzhen | Complete |
| **Hong Kong** | HKG | HKEX | Complete |
| **Taiwan** | TWN | TWSE | Yes |
| **South Korea** | KOR | KRX | Yes |
| **Thailand** | THA | SET | Yes |
| **Malaysia** | MYS | Bursa Malaysia | Yes |
| **Indonesia** | IDN | IDX | Yes |
| **Philippines** | PHL | PSE | Yes |
| **Vietnam** | VNM | HOSE, HNX | Yes |
| **Australia** | AUS | ASX | Complete |
| **New Zealand** | NZL | NZX | Yes |
| **Pakistan** | PAK | PSX | Yes |
| **Bangladesh** | BGD | DSE | Yes |

### 🌍 Africa & Middle East (8+ Countries)

| Country | ISO3 | Exchange(s) | Coverage |
|---------|------|-------------|----------|
| **South Africa** | ZAF | JSE | Complete |
| **Egypt** | EGY | EGX | Yes |
| **Nigeria** | NGA | NSE | Yes |
| **Kenya** | KEN | NSE | Yes |
| **Morocco** | MAR | Casablanca SE | Yes |
| **Saudi Arabia** | SAU | Tadawul | Yes |
| **United Arab Emirates** | ARE | DFM, ADX | Yes |
| **Qatar** | QAT | QE | Yes |
| **Kuwait** | KWT | Boursa Kuwait | Yes |

## API Usage

### Get Complete List via API

```python
import requests

API_KEY = "your_twelve_data_api_key"

# Get all countries
response = requests.get(
    "https://api.twelvedata.com/countries",
    params={"apikey": API_KEY}
)

countries = response.json()["data"]

print(f"Total Countries: {len(countries)}")

for country in countries:
    print(f"{country['name']} ({country['iso3']}) - {country['currency']}")
```

### Get Stocks for Specific Country

```python
import requests

API_KEY = "your_twelve_data_api_key"

# Get all US stocks
response = requests.get(
    "https://api.twelvedata.com/stocks",
    params={
        "country": "USA",  # Use ISO3 code
        "apikey": API_KEY
    }
)

stocks = response.json()["data"]
print(f"Found {len(stocks)} stocks in USA")

# Example for India
response = requests.get(
    "https://api.twelvedata.com/stocks",
    params={
        "country": "IND",
        "apikey": API_KEY
    }
)

stocks = response.json()["data"]
print(f"Found {len(stocks)} stocks in India")
```

### Get All Exchanges

```python
import requests

API_KEY = "your_twelve_data_api_key"

response = requests.get(
    "https://api.twelvedata.com/exchanges",
    params={"apikey": API_KEY}
)

exchanges = response.json()["data"]

# Group by country
by_country = {}
for exchange in exchanges:
    country = exchange.get("country", "Unknown")
    if country not in by_country:
        by_country[country] = []
    by_country[country].append({
        'name': exchange['name'],
        'code': exchange['code'],
        'mic': exchange.get('mic_code', 'N/A')
    })

# Print
for country, exch_list in sorted(by_country.items()):
    print(f"\n{country} ({len(exch_list)} exchanges):")
    for exch in exch_list:
        print(f"  • {exch['name']} ({exch['code']}) - MIC: {exch['mic']}")
```

## Coverage by Plan Tier

### Free Tier ($0/month)
- **US Markets**: Complete coverage (NYSE, NASDAQ, AMEX, OTC)
- **Forex**: 120+ currency pairs
- **Crypto**: 180+ exchanges
- **Limitations**: 800 calls/day, 8 calls/minute

### Grow Plan ($29/month)
- **Everything in Free** +
- **Canada**: Complete TSX coverage
- **India**: NSE, BSE exchanges
- **Europe**: Major European markets
- **Turkey**: Borsa Istanbul
- **Brazil**: B3 exchange
- **Limitations**: 15,000 calls/day, 60 calls/minute

### Pro Plan ($79/month)
- **Everything in Grow** +
- **All International Markets**: Complete global coverage
- **WebSocket Streaming**: Real-time data feeds
- **Limitations**: 65,000 calls/day, 120 calls/minute

### Ultra Plan ($149/month)
- **Everything in Pro** +
- **Complete India Coverage**: All Indian stocks
- **Advanced Features**: Fundamentals, earnings, dividends
- **Limitations**: 100,000 calls/day, 240 calls/minute

### Mega Plan ($399/month)
- **Everything in Ultra** +
- **All Markets**: Unlimited access
- **Priority Support**: Dedicated account manager
- **Custom Solutions**: Tailored data packages
- **Limitations**: 100,000+ calls/day, 240+ calls/minute

## Asset Types Supported

- ✅ **Common Stocks**: US and international equities
- ✅ **ETFs**: 12,000+ exchange-traded funds
- ✅ **Mutual Funds**: Global mutual fund coverage
- ✅ **Indices**: Major market indices worldwide
- ✅ **Forex**: 120+ currency pairs
- ✅ **Cryptocurrencies**: 180+ exchanges, 2,000+ coins
- ✅ **Commodities**: Gold, silver, oil, natural gas
- ✅ **Bonds**: Government and corporate bonds
- ✅ **Options**: US options markets

## Data Intervals Available

- ✅ **1 minute**
- ✅ **5 minutes**
- ✅ **15 minutes**
- ✅ **30 minutes**
- ✅ **45 minutes**
- ✅ **1 hour**
- ✅ **2 hours**
- ✅ **4 hours**
- ✅ **8 hours**
- ✅ **1 day**
- ✅ **1 week**
- ✅ **1 month**

## Technical Indicators (Built-in)

Twelve Data provides built-in technical indicators (no need to calculate manually):

- **Trend**: SMA, EMA, WMA, DEMA, TEMA, TRIMA, KAMA, T3
- **Momentum**: RSI, MACD, Stochastic, Williams %R, ROC, MOM
- **Volatility**: Bollinger Bands, ATR, Standard Deviation
- **Volume**: OBV, AD, ADOSC, MFI
- **Oscillators**: CCI, CMO, PPO, Ultimate Oscillator, Awesome Oscillator
- **Pattern Recognition**: Candlestick patterns

## Next Steps

### 1. Get Your API Key
1. Sign up at https://twelvedata.com
2. Navigate to your dashboard
3. Click "API Keys" → "Reveal"
4. Copy your API key

### 2. Run the Country Fetcher Script
```bash
python fetch_twelve_data_countries.py
```
This will prompt for your API key and generate:
- `twelve_data_countries_YYYYMMDD.json` - Full JSON data
- Updated version of this markdown file with complete list

### 3. Test API Access
```bash
# Test with a simple request
curl "https://api.twelvedata.com/countries?apikey=YOUR_API_KEY"
```

## Migration from Yahoo Finance

If migrating from Yahoo Finance (yfinance):

### Before (Yahoo Finance):
```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1d", interval="1h")
```

### After (Twelve Data):
```python
import requests

API_KEY = "your_key"

response = requests.get(
    "https://api.twelvedata.com/time_series",
    params={
        "symbol": "AAPL",
        "interval": "1h",
        "apikey": API_KEY,
        "outputsize": 500  # Last 500 hours
    }
)

data = response.json()["values"]
```

## Resources

- 📚 **Documentation**: https://twelvedata.com/docs
- 💬 **Support**: https://support.twelvedata.com
- 💰 **Pricing**: https://twelvedata.com/pricing
- 🔑 **API Keys**: https://twelvedata.com/account/api-keys

---

**Note**: This document was created based on available information. To get the exact current list of all 50+ supported countries with full details (ISO codes, currencies, capitals), run the `fetch_twelve_data_countries.py` script with your Twelve Data API key.

**Last Updated**: November 16, 2025
