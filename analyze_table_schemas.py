"""
Analyze all BigQuery table schemas and use Gemini AI to propose optimal field ordering
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel
import json

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
VERTEX_PROJECT = 'cryptobot-462709'
VERTEX_LOCATION = 'us-central1'

def get_all_table_schemas():
    """Get schemas for all tables in the dataset"""
    client = bigquery.Client(project=PROJECT_ID)

    # Get all tables
    tables_query = f"""
    SELECT table_id, row_count
    FROM `{PROJECT_ID}.{DATASET_ID}.__TABLES__`
    ORDER BY row_count DESC
    """

    tables = list(client.query(tables_query).result())

    all_schemas = {}

    for table in tables:
        table_name = table.table_id
        row_count = table.row_count

        try:
            table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
            table_obj = client.get_table(table_ref)

            schema = []
            for field in table_obj.schema:
                schema.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode
                })

            all_schemas[table_name] = {
                'row_count': row_count,
                'num_fields': len(schema),
                'fields': schema,
                'field_names': [f['name'] for f in schema]
            }
        except Exception as e:
            print(f"Error getting schema for {table_name}: {e}")

    return all_schemas

def categorize_tables(schemas):
    """Categorize tables by asset type"""
    categories = {
        'stocks': [],
        'crypto': [],
        'forex': [],
        'etfs': [],
        'indices': [],
        'commodities': [],
        'other': []
    }

    for table_name, schema in schemas.items():
        table_lower = table_name.lower()
        if 'stock' in table_lower:
            categories['stocks'].append(table_name)
        elif 'crypto' in table_lower:
            categories['crypto'].append(table_name)
        elif 'forex' in table_lower:
            categories['forex'].append(table_name)
        elif 'etf' in table_lower:
            categories['etfs'].append(table_name)
        elif 'indic' in table_lower:
            categories['indices'].append(table_name)
        elif 'commodit' in table_lower:
            categories['commodities'].append(table_name)
        else:
            categories['other'].append(table_name)

    return categories

def analyze_with_gemini(schemas, categories):
    """Use Gemini AI to analyze schemas and propose optimal field ordering"""

    # Initialize Vertex AI
    vertexai.init(project=VERTEX_PROJECT, location=VERTEX_LOCATION)
    model = GenerativeModel("gemini-1.5-pro")

    # Build summary of all schemas
    schema_summary = []
    for table_name, schema in schemas.items():
        schema_summary.append(f"""
Table: {table_name}
Row Count: {schema['row_count']:,}
Fields ({schema['num_fields']}): {', '.join(schema['field_names'])}
""")

    prompt = f"""
You are a database architect specializing in financial trading data. Analyze these BigQuery table schemas and propose a standardized field ordering strategy.

CURRENT TABLES BY CATEGORY:
- Stocks: {', '.join(categories['stocks'])}
- Crypto: {', '.join(categories['crypto'])}
- Forex: {', '.join(categories['forex'])}
- ETFs: {', '.join(categories['etfs'])}
- Indices: {', '.join(categories['indices'])}
- Commodities: {', '.join(categories['commodities'])}
- Other: {', '.join(categories['other'])}

CURRENT TABLE SCHEMAS:
{''.join(schema_summary[:30])}  # Limit to first 30 tables

REQUIREMENTS:
1. Key identifier fields should come FIRST: symbol/ticker, name, asset_type/category
2. Classification fields next: exchange, country, sector, industry, currency
3. Price data: open, high, low, close, previous_close
4. Volume data: volume, average_volume
5. Change metrics: change, percent_change
6. Technical indicators (if applicable): RSI, MACD, SMA, EMA, etc.
7. Timestamps last: datetime, timestamp, created_at, updated_at

Please provide:

1. **STANDARDIZED FIELD ORDER TEMPLATE**
   - List the exact field order for trading data tables
   - Group fields logically

2. **FIELD NAMING CONVENTIONS**
   - Standardize field names across all tables
   - e.g., should it be 'symbol' or 'ticker'? 'pair' or 'symbol'?

3. **RECOMMENDED ACTIONS**
   - Which tables need restructuring?
   - Priority order for migration
   - Any fields that should be added or removed?

4. **SAMPLE SCHEMA**
   - Provide a complete recommended schema for:
     a) Daily price data table
     b) Hourly price data table
     c) Weekly summary table
     d) Master list table

Format your response clearly with headers and bullet points.
"""

    response = model.generate_content(prompt)
    return response.text

def main():
    print("=" * 80)
    print("BIGQUERY TABLE SCHEMA ANALYSIS")
    print("=" * 80)

    # Get all schemas
    print("\n1. Fetching all table schemas...")
    schemas = get_all_table_schemas()
    print(f"   Found {len(schemas)} tables")

    # Categorize tables
    print("\n2. Categorizing tables...")
    categories = categorize_tables(schemas)
    for cat, tables in categories.items():
        if tables:
            print(f"   {cat.capitalize()}: {len(tables)} tables")

    # Show current field patterns
    print("\n3. Current Field Patterns:")
    print("-" * 40)

    # Find common fields across tables
    all_fields = {}
    for table_name, schema in schemas.items():
        for field in schema['field_names']:
            if field not in all_fields:
                all_fields[field] = []
            all_fields[field].append(table_name)

    # Sort by frequency
    sorted_fields = sorted(all_fields.items(), key=lambda x: len(x[1]), reverse=True)
    print("\n   Most common fields:")
    for field, tables in sorted_fields[:20]:
        print(f"   - {field}: used in {len(tables)} tables")

    # Use Gemini AI for analysis
    print("\n4. Analyzing with Gemini AI...")
    print("-" * 40)

    try:
        ai_analysis = analyze_with_gemini(schemas, categories)
        print("\n" + ai_analysis)

        # Save the analysis
        with open('TABLE_SCHEMA_ANALYSIS.md', 'w', encoding='utf-8') as f:
            f.write("# BigQuery Table Schema Analysis\n\n")
            f.write("## Current State\n\n")
            f.write(f"Total Tables: {len(schemas)}\n\n")

            for cat, tables in categories.items():
                if tables:
                    f.write(f"### {cat.capitalize()} ({len(tables)} tables)\n")
                    for t in tables:
                        s = schemas[t]
                        f.write(f"- `{t}`: {s['row_count']:,} rows, {s['num_fields']} fields\n")
                    f.write("\n")

            f.write("\n## AI Recommended Schema Strategy\n\n")
            f.write(ai_analysis)

        print("\n\nAnalysis saved to TABLE_SCHEMA_ANALYSIS.md")

    except Exception as e:
        print(f"Error with Gemini AI: {e}")
        print("\nFalling back to rule-based analysis...")

        # Provide rule-based recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDED STANDARD FIELD ORDER")
        print("=" * 80)
        print("""
1. IDENTIFIER FIELDS (First):
   - symbol (or ticker)
   - name
   - asset_type (stock, crypto, forex, etf, index, commodity)

2. CLASSIFICATION FIELDS:
   - exchange
   - country
   - sector
   - industry
   - currency

3. PRICE DATA:
   - open
   - high
   - low
   - close
   - previous_close
   - change
   - percent_change

4. VOLUME DATA:
   - volume
   - average_volume

5. RANGE METRICS:
   - week_52_high
   - week_52_low
   - hi_lo (daily range)
   - pct_hi_lo

6. TECHNICAL INDICATORS (if applicable):
   - rsi, macd, macd_signal, macd_histogram
   - sma_20, sma_50, sma_200
   - ema_12, ema_26, ema_50
   - bollinger_upper, bollinger_middle, bollinger_lower
   - atr, adx, cci, obv
   - etc.

7. TIMESTAMPS (Last):
   - datetime
   - timestamp
   - created_at
   - updated_at
""")

if __name__ == "__main__":
    main()
