"""
Fix empty tables by checking their schema and inserting matching data
Tables: monthly_reports, projects, risks, users
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime, timedelta
import random

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'cpic_data'

client = bigquery.Client(project=PROJECT_ID)

names = ['John Smith', 'Maria Garcia', 'James Wilson', 'Sarah Chen', 'Michael Brown',
         'Emily Davis', 'Robert Johnson', 'Lisa Anderson', 'David Martinez', 'Jennifer Taylor',
         'William Lee', 'Amanda White', 'Craig Drake', 'Jim Keith']

base_date = datetime.now()

def get_table_schema(table_name):
    """Get the actual schema of a table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    table = client.get_table(table_id)
    return [field.name for field in table.schema]

def insert_data(table_name, rows):
    """Insert data into table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Convert all values to strings
    str_rows = [{k: str(v) if v is not None else None for k, v in row.items()} for row in rows]

    # Insert in batches
    errors = client.insert_rows_json(table_id, str_rows)
    if errors:
        print(f"    Errors: {errors[:2]}")
    return len(str_rows)

def main():
    print("=" * 70)
    print("Fixing Empty Tables")
    print("=" * 70)

    empty_tables = ['monthly_reports', 'projects', 'risks', 'users']

    for table_name in empty_tables:
        print(f"\n{table_name}:")

        # Get actual schema
        schema = get_table_schema(table_name)
        print(f"  Schema: {schema}")

        # Generate data based on actual schema
        rows = []

        if table_name == 'users':
            for i in range(1, 26):
                row = {}
                for col in schema:
                    if col == 'user_id':
                        row[col] = f'USR-{i:03d}'
                    elif col == 'email':
                        row[col] = f'{names[i % len(names)].lower().replace(" ", ".")}@irs.gov'
                    elif col == 'name':
                        row[col] = names[i % len(names)]
                    elif col == 'role':
                        row[col] = random.choice(['cio', 'coordinating_director', 'portfolio_manager', 'admin'])
                    elif col == 'organization':
                        row[col] = 'IRS'
                    elif col == 'title':
                        row[col] = random.choice(['Director', 'Manager', 'Analyst', 'Engineer'])
                    elif col == 'password_hash':
                        row[col] = 'hashed_password'
                    elif 'date' in col.lower():
                        row[col] = (base_date - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d')
                    else:
                        row[col] = f'value_{col}_{i}'
                rows.append(row)

        elif table_name == 'projects':
            for i in range(1, 51):
                row = {}
                for col in schema:
                    if col == 'project_id':
                        row[col] = f'PRJ-{i:03d}'
                    elif col == 'name' or col == 'project_name':
                        row[col] = f'Project {random.choice(["Alpha", "Beta", "Core"])} {i}'
                    elif col == 'investment_id':
                        row[col] = f'INV-{(i % 15) + 1:02d}'
                    elif col == 'status':
                        row[col] = random.choice(['Active', 'Completed', 'In Progress', 'Pending'])
                    elif col == 'budget':
                        row[col] = str(round(random.uniform(100000, 5000000), 2))
                    elif col == 'actual_spend':
                        row[col] = str(round(random.uniform(50000, 3000000), 2))
                    elif col == 'progress_pct':
                        row[col] = str(random.randint(10, 100))
                    elif 'manager' in col.lower():
                        row[col] = random.choice(names)
                    elif 'description' in col.lower():
                        row[col] = f'Project description {i}'
                    elif 'date' in col.lower():
                        row[col] = (base_date + timedelta(days=random.randint(-90, 180))).strftime('%Y-%m-%d')
                    else:
                        row[col] = f'value_{i}'
                rows.append(row)

        elif table_name == 'risks':
            for i in range(1, 41):
                row = {}
                for col in schema:
                    if col == 'risk_id':
                        row[col] = f'RSK-{i:03d}'
                    elif col == 'name' or col == 'risk_name':
                        row[col] = f'{random.choice(["Schedule", "Budget", "Technical"])} Risk {i}'
                    elif col == 'investment_id':
                        row[col] = f'INV-{(i % 15) + 1:02d}'
                    elif col == 'project_id':
                        row[col] = f'PRJ-{random.randint(1, 50):03d}'
                    elif col == 'category':
                        row[col] = random.choice(['Schedule', 'Cost', 'Technical', 'Resource'])
                    elif col == 'probability':
                        row[col] = random.choice(['Low', 'Medium', 'High'])
                    elif col == 'impact':
                        row[col] = random.choice(['Low', 'Medium', 'High', 'Critical'])
                    elif col == 'risk_score':
                        row[col] = str(random.randint(1, 25))
                    elif col == 'status':
                        row[col] = random.choice(['Open', 'Mitigated', 'Closed'])
                    elif 'owner' in col.lower():
                        row[col] = random.choice(names)
                    elif col == 'mitigation':
                        row[col] = f'Mitigation plan {i}'
                    elif 'date' in col.lower():
                        row[col] = (base_date + timedelta(days=random.randint(-30, 60))).strftime('%Y-%m-%d')
                    else:
                        row[col] = f'value_{i}'
                rows.append(row)

        elif table_name == 'monthly_reports':
            for i in range(1, 31):
                row = {}
                for col in schema:
                    if col == 'report_id':
                        row[col] = f'RPT-{i:03d}'
                    elif col == 'investment_id':
                        row[col] = f'INV-{(i % 15) + 1:02d}'
                    elif col == 'report_month':
                        row[col] = f'2025-{((i % 12) + 1):02d}'
                    elif 'status' in col.lower():
                        row[col] = random.choice(['green', 'yellow', 'red'])
                    elif col == 'executive_summary':
                        row[col] = f'Monthly report summary for period {i}'
                    elif 'risks' in col.lower():
                        row[col] = str(random.randint(0, 5))
                    elif 'by' in col.lower():
                        row[col] = random.choice(names)
                    elif 'date' in col.lower():
                        row[col] = (base_date - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
                    else:
                        row[col] = f'value_{i}'
                rows.append(row)

        # Insert data
        if rows:
            count = insert_data(table_name, rows)
            print(f"  Inserted {count} records")

    # Final count
    print("\n" + "=" * 70)
    print("Final Record Counts:")
    print("=" * 70)

    for table_name in empty_tables:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        query = f"SELECT COUNT(*) as cnt FROM `{table_id}`"
        result = client.query(query).result()
        for row in result:
            print(f"  {table_name}: {row.cnt} records")

if __name__ == "__main__":
    main()
