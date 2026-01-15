"""
Fast populate all BigQuery tables with proper counts
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime, timedelta
import random
import json

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'cpic_data'

client = bigquery.Client(project=PROJECT_ID)

names = ['John Smith', 'Maria Garcia', 'James Wilson', 'Sarah Chen', 'Michael Brown',
         'Emily Davis', 'Robert Johnson', 'Lisa Anderson', 'David Martinez', 'Jennifer Taylor',
         'William Lee', 'Amanda White', 'Craig Drake', 'Jim Keith']

base_date = datetime.now()

def ts():
    """Generate timestamp string"""
    return (base_date - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d %H:%M:%S')

def d():
    """Generate date string"""
    return (base_date - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d')

def count_all_tables():
    """Count records in all tables"""
    dataset_ref = client.dataset(DATASET_ID)
    tables = list(client.list_tables(dataset_ref))

    counts = {}
    for table in tables:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table.table_id}"
        try:
            query = f"SELECT COUNT(*) as cnt FROM `{table_id}`"
            result = client.query(query).result()
            for row in result:
                counts[table.table_id] = row.cnt
        except:
            counts[table.table_id] = -1

    return counts

def populate_table_sql(table_name, values_list):
    """Populate table using batch SQL INSERT"""
    if not values_list:
        return 0

    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Get column names from first row
    cols = list(values_list[0].keys())
    col_str = ', '.join(cols)

    # Build VALUES clause - batch 50 at a time
    batch_size = 50
    inserted = 0

    for i in range(0, len(values_list), batch_size):
        batch = values_list[i:i+batch_size]
        values_strs = []

        for row in batch:
            vals = []
            for col in cols:
                v = row.get(col)
                if v is None:
                    vals.append('NULL')
                elif isinstance(v, bool):
                    vals.append('TRUE' if v else 'FALSE')
                elif isinstance(v, (int, float)):
                    vals.append(str(v))
                else:
                    escaped = str(v).replace("'", "\\'").replace('\n', ' ')
                    vals.append(f"'{escaped}'")
            values_strs.append(f"({', '.join(vals)})")

        query = f"INSERT INTO `{table_id}` ({col_str}) VALUES {', '.join(values_strs)}"

        try:
            client.query(query).result()
            inserted += len(batch)
        except Exception as e:
            print(f"    Error inserting batch: {str(e)[:100]}")

    return inserted

def main():
    print("=" * 70)
    print("FAST POPULATE ALL CPIC TABLES")
    print("=" * 70)

    # First get current counts
    print("\nCURRENT TABLE COUNTS:")
    print("-" * 50)
    counts = count_all_tables()
    for table, count in sorted(counts.items()):
        status = "OK" if count >= 20 else "NEEDS DATA"
        print(f"  {table:<35} {count:>6}  {status}")

    # Tables that need data (< 20 records)
    tables_to_fill = {k: v for k, v in counts.items() if v < 20}

    print(f"\n{len(tables_to_fill)} tables need data")
    print("-" * 50)

    # Define data for tables that need it
    for table_name, current_count in tables_to_fill.items():
        needed = 30 - current_count  # Target 30 records
        if needed <= 0:
            continue

        print(f"\n{table_name}: adding {needed} records...")

        data = []

        if table_name == 'users':
            for i in range(needed):
                data.append({
                    'user_id': f'USR-{100+i:03d}',
                    'email': f'user{100+i}@irs.gov',
                    'password_hash': 'hash123',
                    'name': random.choice(names),
                    'organization': 'IRS',
                    'role': random.choice(['cio', 'admin', 'portfolio_manager', 'technical_lead']),
                    'title': random.choice(['Director', 'Manager', 'Analyst']),
                    'created_at': ts(),
                    'last_login': ts(),
                    'is_active': True
                })

        elif table_name == 'projects':
            for i in range(needed):
                data.append({
                    'project_id': f'PRJ-{100+i:03d}',
                    'name': f'Project {random.choice(["Alpha", "Beta", "Core"])} {100+i}',
                    'description': f'Project description {i}',
                    'investment_id': f'INV-{(i % 15) + 1:02d}',
                    'status': random.choice(['active', 'completed', 'in_progress']),
                    'health': random.choice(['green', 'yellow', 'red']),
                    'start_date': d(),
                    'end_date': d(),
                    'budget': round(random.uniform(100000, 5000000), 2),
                    'actual_spend': round(random.uniform(50000, 3000000), 2),
                    'owner': random.choice(names),
                    'created_at': ts()
                })

        elif table_name == 'risks':
            for i in range(needed):
                data.append({
                    'risk_id': f'RSK-{100+i:03d}',
                    'title': f'Risk Item {100+i}',
                    'description': f'Risk description {i}',
                    'investment_id': f'INV-{(i % 15) + 1:02d}',
                    'project_id': f'PRJ-{random.randint(1, 50):03d}',
                    'category': random.choice(['schedule', 'cost', 'technical']),
                    'probability': random.choice(['low', 'medium', 'high']),
                    'impact': random.choice(['low', 'medium', 'high']),
                    'status': random.choice(['open', 'mitigated', 'closed']),
                    'mitigation': f'Mitigation plan {i}',
                    'owner': random.choice(names),
                    'created_at': ts()
                })

        elif table_name == 'monthly_reports':
            for i in range(needed):
                data.append({
                    'report_id': f'RPT-{100+i:03d}',
                    'investment_id': f'INV-{(i % 15) + 1:02d}',
                    'report_month': f'2025-{((i % 12) + 1):02d}',
                    'fiscal_year': random.choice([2024, 2025]),
                    'status': random.choice(['green', 'yellow', 'red']),
                    'cost_variance': round(random.uniform(-15, 20), 1),
                    'schedule_variance': round(random.uniform(-10, 15), 1),
                    'cio_comments': f'Comments {i}',
                    'submitted_by': random.choice(names),
                    'submitted_at': ts(),
                    'created_at': ts()
                })

        elif table_name == 'investments':
            # Already has 9 - just add if needed
            for i in range(needed):
                data.append({
                    'investment_id': f'INV-{20+i:02d}',
                    'uii': f'015-{1000000+i:09d}',
                    'name': f'Investment {20+i}',
                    'short_name': f'INV{20+i}',
                    'description': f'Investment description {i}',
                    'category': random.choice(['MISSION', 'FOUNDATIONAL']),
                    'investment_type': random.choice(['major-it', 'non-major-it']),
                    'lifecycle_stage': random.choice(['control', 'select', 'evaluate']),
                    'status': 'active',
                    'health': random.choice(['green', 'yellow']),
                    'budget_fy25': round(random.uniform(10000000, 100000000), 2),
                    'actual_spend_ytd': round(random.uniform(5000000, 50000000), 2),
                    'owner': random.choice(names),
                    'created_at': ts()
                })

        elif table_name == 'workflows':
            # Already has 8 - just add if needed
            for i in range(needed):
                data.append({
                    'workflow_id': f'WF-{10+i:02d}',
                    'name': f'Workflow {10+i}',
                    'description': f'Workflow description {i}',
                    'phase': random.choice(['PRESELECT', 'SELECT', 'CONTROL', 'EVALUATE']),
                    'steps': json.dumps(['Step1', 'Step2', 'Step3']),
                    'duration': f'{random.randint(1, 12)} weeks',
                    'created_at': ts()
                })

        elif table_name == 'cpic_forms':
            # Should have 134 - add more if needed
            for i in range(needed):
                data.append({
                    'form_id': f'CPIC-{200+i:03d}',
                    'form_name': f'Additional Form {200+i}',
                    'form_code': f'AF-{i:03d}',
                    'functional_area': random.choice(['Governance', 'Technical', 'Financial', 'Risk']),
                    'description': f'Additional form description {i}',
                    'investment_id': f'INV-{(i % 15) + 1:02d}',
                    'fiscal_year': 2025,
                    'status': random.choice(['Active', 'Draft', 'Pending']),
                    'risk_level': random.choice(['Low', 'Medium', 'High']),
                    'owner': random.choice(names),
                    'cpic_phase': random.choice(['Preselect', 'Select', 'Control', 'Evaluate']),
                    'created_at': ts()
                })

        if data:
            inserted = populate_table_sql(table_name, data)
            print(f"  Inserted {inserted} records")

    # Final counts
    print("\n" + "=" * 70)
    print("FINAL TABLE COUNTS:")
    print("=" * 70)
    final_counts = count_all_tables()
    total = 0
    for table, count in sorted(final_counts.items()):
        print(f"  {table:<35} {count:>6} records")
        total += count if count > 0 else 0
    print("-" * 50)
    print(f"  {'TOTAL':<35} {total:>6} records")

if __name__ == "__main__":
    main()
