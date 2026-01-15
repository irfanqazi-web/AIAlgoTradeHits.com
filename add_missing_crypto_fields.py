"""
Add missing indicator fields to crypto_analysis table to match stock_analysis
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'crypto_analysis'

def add_missing_fields():
    """Add all missing fields from stock_analysis to crypto_analysis"""

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    table = client.get_table(table_ref)

    print("Adding missing indicator fields to crypto_analysis table...")
    print()

    # Fields to add (based on stock_analysis that are missing from crypto)
    new_fields = [
        bigquery.SchemaField("bb_middle", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("bb_width", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("plus_di", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("minus_di", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("pvo_signal", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ppo_signal", "FLOAT64", mode="NULLABLE"),

        # Fibonacci levels
        bigquery.SchemaField("fib_0", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("fib_236", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("fib_382", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("fib_500", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("fib_618", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("fib_786", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("fib_100", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("fib_ext_1272", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("fib_ext_1618", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("fib_ext_2618", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("dist_to_fib_236", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("dist_to_fib_382", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("dist_to_fib_500", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("dist_to_fib_618", "FLOAT64", mode="NULLABLE"),

        # Elliott Wave analysis
        bigquery.SchemaField("elliott_wave_degree", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("wave_position", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("impulse_wave_count", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("corrective_wave_count", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("wave_1_high", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("wave_2_low", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("wave_3_high", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("wave_4_low", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("wave_5_high", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("trend_direction", "STRING", mode="NULLABLE"),

        # Pattern detection
        bigquery.SchemaField("swing_high", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("swing_low", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("local_maxima", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("local_minima", "FLOAT64", mode="NULLABLE"),

        # Additional metrics
        bigquery.SchemaField("trend_strength", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("volatility_regime", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("price_change_1d", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("price_change_5d", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("price_change_20d", "FLOAT64", mode="NULLABLE"),
    ]

    # Get current schema and add new fields
    schema = table.schema.copy()
    existing_field_names = {field.name for field in schema}

    fields_added = 0
    for field in new_fields:
        if field.name not in existing_field_names:
            schema.append(field)
            fields_added += 1
            print(f"  ✓ Adding field: {field.name} ({field.field_type})")

    if fields_added > 0:
        table.schema = schema
        table = client.update_table(table, ["schema"])
        print()
        print(f"✓ Successfully added {fields_added} new fields to crypto_analysis table")
    else:
        print("  All fields already exist")

    print()
    print("=" * 70)
    print("SCHEMA UPDATE COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    add_missing_fields()
