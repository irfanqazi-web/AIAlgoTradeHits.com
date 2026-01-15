import requests
import json
import sys
import io
from datetime import datetime

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration - User needs to provide API key
API_KEY = input("Please enter your Twelve Data API key: ").strip()

if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
    print("\nError: Please provide a valid Twelve Data API key")
    print("Get your free API key at: https://twelvedata.com")
    sys.exit(1)

BASE_URL = "https://api.twelvedata.com"

print("\n" + "=" * 80)
print("TWELVE DATA - COUNTRY & EXCHANGE LIST RETRIEVER")
print("=" * 80)

# Fetch countries
print("\n🌍 Fetching all supported countries from Twelve Data...\n")

try:
    response = requests.get(
        f"{BASE_URL}/countries",
        params={"apikey": API_KEY}
    )

    if response.status_code == 200:
        data = response.json()
        countries = data.get("data", [])

        print(f"✓ Successfully retrieved {len(countries)} countries\n")

        # Print formatted table
        print("=" * 100)
        print(f"{'Country Name':<40} {'ISO3':<8} {'ISO2':<6} {'Currency':<10} {'Capital':<20}")
        print("=" * 100)

        for country in sorted(countries, key=lambda x: x.get('name', '')):
            name = country.get('name', 'N/A')
            iso3 = country.get('iso3', 'N/A')
            iso2 = country.get('iso2', 'N/A')
            currency = country.get('currency', 'N/A')
            capital = country.get('capital', 'N/A')

            print(f"{name:<40} {iso3:<8} {iso2:<6} {currency:<10} {capital:<20}")

        print("=" * 100)

        # Save to JSON
        json_filename = f"twelve_data_countries_{datetime.now().strftime('%Y%m%d')}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(countries, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Complete list saved to: {json_filename}")

        # Create markdown document
        md_content = f"""# Twelve Data - Supported Countries

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Countries**: {len(countries)}

## Summary

Twelve Data provides financial market data coverage across **{len(countries)} countries** worldwide.

## Complete Country List

| Country Name | ISO3 | ISO2 | Currency | Capital |
|--------------|------|------|----------|---------|
"""

        for country in sorted(countries, key=lambda x: x.get('name', '')):
            name = country.get('name', 'N/A')
            iso3 = country.get('iso3', 'N/A')
            iso2 = country.get('iso2', 'N/A')
            currency = country.get('currency', 'N/A')
            capital = country.get('capital', 'N/A')
            md_content += f"| {name} | {iso3} | {iso2} | {currency} | {capital} |\n"

        md_content += f"""
## Regions Breakdown

### Americas
"""

        americas = [c for c in countries if c.get('name', '') in [
            'United States', 'Canada', 'Mexico', 'Brazil', 'Argentina', 'Chile',
            'Colombia', 'Peru', 'Venezuela', 'Ecuador', 'Uruguay', 'Paraguay'
        ]]

        for country in sorted(americas, key=lambda x: x.get('name', '')):
            md_content += f"- **{country.get('name')}** ({country.get('iso3')}) - {country.get('currency')}\n"

        md_content += "\n### Europe\n"

        europe = [c for c in countries if c.get('name', '') in [
            'United Kingdom', 'Germany', 'France', 'Italy', 'Spain', 'Netherlands',
            'Belgium', 'Switzerland', 'Austria', 'Portugal', 'Ireland', 'Sweden',
            'Norway', 'Denmark', 'Finland', 'Poland', 'Czech Republic', 'Greece',
            'Turkey', 'Russia'
        ]]

        for country in sorted(europe, key=lambda x: x.get('name', '')):
            md_content += f"- **{country.get('name')}** ({country.get('iso3')}) - {country.get('currency')}\n"

        md_content += "\n### Asia-Pacific\n"

        asia = [c for c in countries if c.get('name', '') in [
            'China', 'Japan', 'India', 'South Korea', 'Singapore', 'Hong Kong',
            'Taiwan', 'Thailand', 'Malaysia', 'Indonesia', 'Philippines', 'Vietnam',
            'Australia', 'New Zealand', 'Pakistan', 'Bangladesh', 'Sri Lanka'
        ]]

        for country in sorted(asia, key=lambda x: x.get('name', '')):
            md_content += f"- **{country.get('name')}** ({country.get('iso3')}) - {country.get('currency')}\n"

        md_content += f"""
## API Usage

To query stocks from a specific country:

```python
import requests

API_KEY = "your_api_key"
country_code = "USA"  # Use ISO3 code

response = requests.get(
    "https://api.twelvedata.com/stocks",
    params={{
        "country": country_code,
        "apikey": API_KEY
    }}
)

stocks = response.json()["data"]
print(f"Found {{len(stocks)}} stocks in {{country_code}}")
```

## Data Source

This list was retrieved from the Twelve Data API `/countries` endpoint.

For the most up-to-date information, visit: https://twelvedata.com/docs#countries

---
*Generated by Twelve Data Country List Retriever*
"""

        md_filename = "TWELVE_DATA_COUNTRIES.md"
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"✓ Markdown document saved to: {md_filename}")
        print(f"\n✓ Script completed successfully!")

    else:
        print(f"❌ Error: HTTP {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ Error occurred: {str(e)}")
    import traceback
    traceback.print_exc()
