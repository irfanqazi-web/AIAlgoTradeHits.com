"""
Fix empty tables with proper data types
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

def get_timestamp():
    """Generate a proper timestamp"""
    dt = base_date - timedelta(days=random.randint(0, 180), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def insert_data(table_name, rows):
    """Insert data into table using SQL"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    for row in rows:
        # Build INSERT statement
        cols = ', '.join(row.keys())
        vals = []
        for v in row.values():
            if v is None:
                vals.append('NULL')
            elif isinstance(v, bool):
                vals.append('TRUE' if v else 'FALSE')
            elif isinstance(v, (int, float)):
                vals.append(str(v))
            else:
                # Escape single quotes
                escaped = str(v).replace("'", "\\'")
                vals.append(f"'{escaped}'")

        values_str = ', '.join(vals)
        query = f"INSERT INTO `{table_id}` ({cols}) VALUES ({values_str})"

        try:
            client.query(query).result()
        except Exception as e:
            print(f"    Error: {str(e)[:80]}")
            return False

    return True

def main():
    print("=" * 70)
    print("Fixing Empty Tables with Proper Data Types")
    print("=" * 70)

    # USERS table
    print("\nusers:")
    users_data = []
    for i in range(1, 26):
        users_data.append({
            'user_id': f'USR-{i:03d}',
            'email': f'{names[i % len(names)].lower().replace(" ", ".")}@irs.gov',
            'password_hash': 'hashed_password_value',
            'name': names[i % len(names)],
            'organization': 'IRS',
            'role': random.choice(['cio', 'coordinating_director', 'portfolio_manager', 'admin', 'technical_lead']),
            'title': random.choice(['Director', 'Manager', 'Analyst', 'Engineer', 'Coordinator']),
            'created_at': get_timestamp(),
            'last_login': get_timestamp(),
            'is_active': random.choice([True, True, True, False])  # 75% active
        })

    if insert_data('users', users_data):
        print(f"  Inserted {len(users_data)} records")

    # PROJECTS table
    print("\nprojects:")
    projects_data = []
    for i in range(1, 51):
        projects_data.append({
            'project_id': f'PRJ-{i:03d}',
            'name': f'Project {random.choice(["Alpha", "Beta", "Core", "Enterprise", "Cloud"])} {i}',
            'description': f'Project for {random.choice(["modernization", "security", "migration", "development", "infrastructure"])}',
            'investment_id': f'INV-{(i % 15) + 1:02d}',
            'status': random.choice(['active', 'completed', 'in_progress', 'pending', 'on_hold']),
            'health': random.choice(['green', 'yellow', 'red']),
            'start_date': (base_date - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
            'end_date': (base_date + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
            'budget': round(random.uniform(100000, 5000000), 2),
            'actual_spend': round(random.uniform(50000, 3000000), 2),
            'owner': random.choice(names),
            'created_at': get_timestamp()
        })

    if insert_data('projects', projects_data):
        print(f"  Inserted {len(projects_data)} records")

    # RISKS table
    print("\nrisks:")
    risks_data = []
    for i in range(1, 41):
        risks_data.append({
            'risk_id': f'RSK-{i:03d}',
            'title': f'{random.choice(["Schedule", "Budget", "Technical", "Resource", "Security"])} Risk - Item {i}',
            'description': f'Risk description for {random.choice(["delay", "overrun", "complexity", "shortage"])} scenario',
            'investment_id': f'INV-{(i % 15) + 1:02d}',
            'project_id': f'PRJ-{random.randint(1, 50):03d}',
            'category': random.choice(['schedule', 'cost', 'technical', 'resource', 'security', 'compliance']),
            'probability': random.choice(['low', 'medium', 'high']),
            'impact': random.choice(['low', 'medium', 'high', 'critical']),
            'status': random.choice(['open', 'mitigated', 'closed', 'monitoring']),
            'mitigation': f'Implement {random.choice(["contingency", "backup", "workaround"])} plan',
            'owner': random.choice(names),
            'created_at': get_timestamp()
        })

    if insert_data('risks', risks_data):
        print(f"  Inserted {len(risks_data)} records")

    # MONTHLY_REPORTS table
    print("\nmonthly_reports:")
    reports_data = []
    for i in range(1, 31):
        reports_data.append({
            'report_id': f'RPT-{i:03d}',
            'investment_id': f'INV-{(i % 15) + 1:02d}',
            'report_month': f'2025-{((i % 12) + 1):02d}',
            'fiscal_year': random.choice([2024, 2025, 2026]),
            'status': random.choice(['green', 'yellow', 'red']),
            'cost_variance': round(random.uniform(-15, 20), 1),
            'schedule_variance': round(random.uniform(-10, 15), 1),
            'cio_comments': f'CIO review comments for report {i}',
            'submitted_by': random.choice(names),
            'submitted_at': get_timestamp(),
            'created_at': get_timestamp()
        })

    if insert_data('monthly_reports', reports_data):
        print(f"  Inserted {len(reports_data)} records")

    # Final count
    print("\n" + "=" * 70)
    print("Final Record Counts:")
    print("=" * 70)

    for table_name in ['users', 'projects', 'risks', 'monthly_reports']:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        query = f"SELECT COUNT(*) as cnt FROM `{table_id}`"
        result = client.query(query).result()
        for row in result:
            print(f"  {table_name}: {row.cnt} records")

if __name__ == "__main__":
    main()
