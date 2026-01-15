"""
Test the AI Smart Search Function
"""

import requests
import json
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Smart Search endpoint
SMART_SEARCH_URL = "https://smart-search-6pmz2y7ouq-uc.a.run.app"

def test_query(query: str, execute: bool = False):
    """Test a natural language query"""
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print('='*60)

    payload = {
        "query": query,
        "execute": execute  # Set to True to also run the SQL
    }

    try:
        response = requests.post(
            SMART_SEARCH_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\nSUCCESS! (Execution time: {data.get('execution_time_ms', 'N/A')}ms)")

            if 'ai_analysis' in data:
                ai = data['ai_analysis']
                print(f"\n--- AI UNDERSTANDING ---")
                if 'query_understanding' in ai:
                    qu = ai['query_understanding']
                    print(f"Intent: {qu.get('intent', 'N/A')}")
                    print(f"Asset Type: {qu.get('asset_type', 'N/A')}")
                    print(f"Timeframe: {qu.get('timeframe', 'N/A')}")
                    print(f"Filters: {qu.get('filters', [])}")

                print(f"\n--- GENERATED SQL ---")
                print(ai.get('sql', 'No SQL generated'))

                print(f"\n--- EXPLANATION ---")
                print(ai.get('explanation', 'N/A'))

                print(f"\n--- TRADING INSIGHT ---")
                print(ai.get('trading_insight', 'N/A'))

            if 'results' in data and data['results'].get('success'):
                print(f"\n--- QUERY RESULTS ({data['results']['count']} rows) ---")
                for i, row in enumerate(data['results']['data'][:5]):  # Show first 5
                    print(f"  {i+1}. {row}")
                if data['results']['count'] > 5:
                    print(f"  ... and {data['results']['count'] - 5} more rows")

        else:
            print(f"\nERROR: {response.status_code}")
            print(response.text)

    except requests.exceptions.Timeout:
        print("\nTIMEOUT: Request took too long")
    except Exception as e:
        print(f"\nERROR: {e}")


def main():
    print("=" * 60)
    print("AI SMART SEARCH TEST SUITE")
    print("=" * 60)

    # Test queries
    test_queries = [
        "Show me oversold stocks",
        "Bitcoin price with RSI and MACD",
        "Top 10 cryptos by volume",
        "Find stocks with golden cross",
        "Which forex pairs are trending strongly?",
    ]

    print("\nTesting basic query (without execution)...")
    test_query("show me oversold stocks", execute=False)

    print("\n\n" + "=" * 60)
    print("Would you like to test more queries?")
    print("=" * 60)

    for i, q in enumerate(test_queries, 1):
        print(f"  {i}. {q}")

    print("\nEnter query number (1-5) or type your own query:")
    print("(Press Ctrl+C to exit)")

    try:
        while True:
            user_input = input("\n> ").strip()
            if not user_input:
                continue

            if user_input.isdigit():
                idx = int(user_input) - 1
                if 0 <= idx < len(test_queries):
                    test_query(test_queries[idx], execute=False)
                else:
                    print("Invalid number")
            else:
                test_query(user_input, execute=False)

    except KeyboardInterrupt:
        print("\n\nExiting...")


if __name__ == "__main__":
    main()
