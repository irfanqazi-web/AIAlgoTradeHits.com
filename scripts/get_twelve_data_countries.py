#!/usr/bin/env python3
"""
Twelve Data - Country List Retriever
This script retrieves and displays all supported countries from the Twelve Data API
"""

import requests
import json
from datetime import datetime

# Configuration
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your Twelve Data API key
BASE_URL = "https://api.twelvedata.com"

def get_all_countries():
    """Retrieve all supported countries from Twelve Data"""
    print("🌍 Fetching all supported countries from Twelve Data...\n")
    
    try:
        response = requests.get(
            f"{BASE_URL}/countries",
            params={"apikey": API_KEY}
        )
        
        if response.status_code == 200:
            data = response.json()
            countries = data.get("data", [])
            
            print(f"✓ Successfully retrieved {len(countries)} countries\n")
            print("=" * 80)
            print(f"{'Country Name':<40} {'ISO3':<8} {'Currency':<8} {'Capital':<20}")
            print("=" * 80)
            
            for country in sorted(countries, key=lambda x: x['name']):
                name = country.get('name', 'N/A')
                iso3 = country.get('iso3', 'N/A')
                currency = country.get('currency', 'N/A')
                capital = country.get('capital', 'N/A')
                
                print(f"{name:<40} {iso3:<8} {currency:<8} {capital:<20}")
            
            print("=" * 80)
            
            # Save to JSON file
            filename = f"twelve_data_countries_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(countries, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ Complete list saved to: {filename}")
            return countries
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        return None


def get_all_exchanges():
    """Retrieve all stock exchanges and group by country"""
    print("\n\n📊 Fetching all stock exchanges...\n")
    
    try:
        response = requests.get(
            f"{BASE_URL}/exchanges",
            params={"apikey": API_KEY}
        )
        
        if response.status_code == 200:
            data = response.json()
            exchanges = data.get("data", [])
            
            print(f"✓ Successfully retrieved {len(exchanges)} exchanges\n")
            
            # Group by country
            by_country = {}
            for exchange in exchanges:
                country = exchange.get("country", "Unknown")
                if country not in by_country:
                    by_country[country] = []
                by_country[country].append({
                    'name': exchange.get('name', 'N/A'),
                    'code': exchange.get('code', 'N/A'),
                    'mic': exchange.get('mic_code', 'N/A')
                })
            
            print("=" * 80)
            print("Exchanges by Country")
            print("=" * 80)
            
            for country, exch_list in sorted(by_country.items()):
                print(f"\n{country} ({len(exch_list)} exchanges):")
                for exch in exch_list:
                    print(f"  • {exch['name']} ({exch['code']}) - MIC: {exch['mic']}")
            
            print("=" * 80)
            
            # Save to JSON file
            filename = f"twelve_data_exchanges_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(by_country, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ Exchange list saved to: {filename}")
            return by_country
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        return None


def get_stocks_by_country(country_code):
    """Get all stocks for a specific country"""
    print(f"\n📈 Fetching stocks for country: {country_code}...\n")
    
    try:
        response = requests.get(
            f"{BASE_URL}/stocks",
            params={
                "country": country_code,
                "apikey": API_KEY
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            stocks = data.get("data", [])
            
            print(f"✓ Found {len(stocks)} stocks in {country_code}\n")
            
            if len(stocks) > 0:
                print(f"First 10 stocks in {country_code}:")
                print("-" * 60)
                for stock in stocks[:10]:
                    print(f"{stock.get('symbol', 'N/A'):<10} - {stock.get('name', 'N/A')}")
                print("-" * 60)
            
            return stocks
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        return None


def generate_summary_report(countries, exchanges_by_country):
    """Generate a summary report"""
    print("\n\n" + "=" * 80)
    print("TWELVE DATA - MARKET COVERAGE SUMMARY REPORT")
    print("=" * 80)
    print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    if countries:
        print(f"\n📊 Total Countries Supported: {len(countries)}")
        
        # Group by region (simplified)
        regions = {}
        for country in countries:
            # This is a simplified categorization - you might want to enhance this
            name = country.get('name', '')
            if any(x in name for x in ['United States', 'Canada', 'Mexico', 'Brazil', 'Argentina', 'Chile']):
                region = 'Americas'
            elif any(x in name for x in ['United Kingdom', 'Germany', 'France', 'Italy', 'Spain', 'Netherlands', 'Belgium', 'Switzerland', 'Austria', 'Portugal', 'Ireland', 'Sweden', 'Norway', 'Denmark', 'Finland', 'Poland', 'Czech', 'Greece', 'Turkey']):
                region = 'Europe'
            elif any(x in name for x in ['China', 'Japan', 'India', 'Korea', 'Singapore', 'Hong Kong', 'Taiwan', 'Thailand', 'Malaysia', 'Indonesia', 'Philippines', 'Vietnam', 'Australia', 'New Zealand']):
                region = 'Asia-Pacific'
            elif any(x in name for x in ['South Africa', 'Egypt', 'Kenya', 'Nigeria', 'Morocco']):
                region = 'Africa & Middle East'
            else:
                region = 'Other'
            
            if region not in regions:
                regions[region] = []
            regions[region].append(country.get('name'))
        
        print("\n📍 Coverage by Region:")
        for region, country_list in sorted(regions.items()):
            print(f"\n{region}: {len(country_list)} countries")
    
    if exchanges_by_country:
        print(f"\n📊 Total Stock Exchanges: {sum(len(v) for v in exchanges_by_country.values())}")
        print(f"\n📍 Countries with Exchanges: {len(exchanges_by_country)}")
        
        print("\nTop 10 Countries by Number of Exchanges:")
        sorted_countries = sorted(exchanges_by_country.items(), key=lambda x: len(x[1]), reverse=True)
        for i, (country, exchanges) in enumerate(sorted_countries[:10], 1):
            print(f"{i:2d}. {country:<30} - {len(exchanges)} exchanges")
    
    print("\n" + "=" * 80)
    print("End of Report")
    print("=" * 80)


def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("TWELVE DATA - COUNTRY & EXCHANGE LIST RETRIEVER")
    print("=" * 80)
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("\n⚠️  WARNING: Please set your Twelve Data API key in the script!")
        print("   Get your free API key at: https://twelvedata.com")
        print("\n   1. Sign up for a free account")
        print("   2. Go to your dashboard")
        print("   3. Click 'API Keys' and reveal your key")
        print("   4. Replace 'YOUR_API_KEY_HERE' in this script with your key")
        return
    
    # Retrieve all countries
    countries = get_all_countries()
    
    # Retrieve all exchanges
    exchanges_by_country = get_all_exchanges()
    
    # Generate summary report
    if countries or exchanges_by_country:
        generate_summary_report(countries, exchanges_by_country)
    
    # Example: Get stocks for specific country (USA)
    # Uncomment the line below to test
    # get_stocks_by_country("USA")
    
    print("\n✓ Script completed successfully!")
    print("\nNext steps:")
    print("  1. Check the generated JSON files for complete data")
    print("  2. Modify the script to query specific countries")
    print("  3. Integrate the data into your application")


if __name__ == "__main__":
    main()
