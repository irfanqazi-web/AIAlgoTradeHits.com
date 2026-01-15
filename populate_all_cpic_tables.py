"""
Populate ALL CPIC BigQuery Tables with 20-60 records each
Tables: portfolio_summary, project_baseline, project_financial, projects, reference_data,
        review_history, risk_register, risks, saved_reports, spike_sync_history,
        strategic_alignment, system_config, user_dashboard_config, user_sessions, users, workflow_approvals
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime, timedelta
import random
import uuid

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'cpic_data'

client = bigquery.Client(project=PROJECT_ID)

# Sample data
names = ['John Smith', 'Maria Garcia', 'James Wilson', 'Sarah Chen', 'Michael Brown',
         'Emily Davis', 'Robert Johnson', 'Lisa Anderson', 'David Martinez', 'Jennifer Taylor',
         'William Lee', 'Amanda White', 'Craig Drake', 'Jim Keith', 'Miji Mathews',
         'Eric Markow', 'Lou Capece', 'Houman Rasouli', 'Rob King', 'Courtney Williams']

emails = [n.lower().replace(' ', '.') + '@irs.gov' for n in names]
statuses = ['Active', 'Completed', 'In Progress', 'Pending', 'Approved', 'Draft', 'Under Review']
risk_levels = ['Low', 'Medium', 'High', 'Critical']
health_colors = ['green', 'yellow', 'red']
phases = ['Preselect', 'Select', 'Control', 'Evaluate']
roles = ['cio', 'coordinating_director', 'portfolio_manager', 'technical_lead', 'investment_coordinator', 'admin']

base_date = datetime.now()

def create_table_if_not_exists(table_name, schema):
    """Create table with schema if it doesn't exist"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    try:
        client.get_table(table_id)
        return True
    except Exception:
        schema_fields = [bigquery.SchemaField(name, "STRING") for name in schema]
        table = bigquery.Table(table_id, schema=schema_fields)
        client.create_table(table)
        print(f"  Created table {table_name}")
        return True

def insert_data(table_name, rows):
    """Insert data into table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Convert all values to strings
    str_rows = []
    for row in rows:
        str_rows.append({k: str(v) if v is not None else None for k, v in row.items()})

    # Delete existing data
    try:
        query = f"DELETE FROM `{table_id}` WHERE TRUE"
        client.query(query).result()
    except Exception:
        pass

    # Insert in batches
    batch_size = 100
    for i in range(0, len(str_rows), batch_size):
        batch = str_rows[i:i+batch_size]
        errors = client.insert_rows_json(table_id, batch)
        if errors:
            print(f"    Insert errors: {errors[:1]}")

    return len(str_rows)

def count_table(table_name):
    """Count rows in table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    try:
        query = f"SELECT COUNT(*) as cnt FROM `{table_id}`"
        result = client.query(query).result()
        for row in result:
            return row.cnt
    except Exception as e:
        return f"Error: {e}"

# ============== TABLE DEFINITIONS AND DATA ==============

tables = {
    'portfolio_summary': {
        'schema': ['summary_id', 'portfolio_name', 'total_investments', 'total_budget', 'health_status',
                  'fiscal_year', 'created_date', 'updated_date', 'owner', 'description'],
        'data': [
            {
                'summary_id': f'PS-{i:03d}',
                'portfolio_name': f'{random.choice(["IT", "Mission", "Infrastructure", "Security", "Enterprise"])} Portfolio {i}',
                'total_investments': str(random.randint(5, 25)),
                'total_budget': str(round(random.uniform(10000000, 500000000), 2)),
                'health_status': random.choice(health_colors),
                'fiscal_year': str(random.choice([2024, 2025, 2026])),
                'created_date': (base_date - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
                'updated_date': (base_date - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                'owner': random.choice(names),
                'description': f'Portfolio summary for {random.choice(["enterprise", "mission", "security", "data"])} investments'
            }
            for i in range(1, 31)
        ]
    },
    'project_baseline': {
        'schema': ['baseline_id', 'project_id', 'investment_id', 'baseline_version', 'baseline_date',
                  'cost_baseline', 'schedule_baseline_end', 'scope_summary', 'approved_by', 'status'],
        'data': [
            {
                'baseline_id': f'BL-{i:03d}',
                'project_id': f'PRJ-{random.randint(1, 50):03d}',
                'investment_id': f'INV-{(i % 15) + 1:02d}',
                'baseline_version': f'{random.randint(1, 5)}.{random.randint(0, 9)}',
                'baseline_date': (base_date - timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d'),
                'cost_baseline': str(round(random.uniform(100000, 10000000), 2)),
                'schedule_baseline_end': (base_date + timedelta(days=random.randint(60, 365))).strftime('%Y-%m-%d'),
                'scope_summary': f'{random.choice(["Phase", "Release", "MVP", "Full"])} scope - {random.choice(["development", "deployment", "migration", "modernization"])}',
                'approved_by': random.choice(names),
                'status': random.choice(['Active', 'Superseded', 'Draft'])
            }
            for i in range(1, 41)
        ]
    },
    'project_financial': {
        'schema': ['financial_id', 'project_id', 'investment_id', 'fiscal_year', 'budget_allocated',
                  'actual_spend', 'committed', 'forecast', 'variance_pct', 'status', 'updated_date'],
        'data': [
            {
                'financial_id': f'FIN-{i:03d}',
                'project_id': f'PRJ-{random.randint(1, 50):03d}',
                'investment_id': f'INV-{(i % 15) + 1:02d}',
                'fiscal_year': str(random.choice([2024, 2025, 2026])),
                'budget_allocated': str(round(random.uniform(500000, 10000000), 2)),
                'actual_spend': str(round(random.uniform(100000, 5000000), 2)),
                'committed': str(round(random.uniform(50000, 3000000), 2)),
                'forecast': str(round(random.uniform(400000, 9000000), 2)),
                'variance_pct': str(round(random.uniform(-20, 30), 1)),
                'status': random.choice(['On Budget', 'Over Budget', 'Under Budget']),
                'updated_date': (base_date - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
            }
            for i in range(1, 51)
        ]
    },
    'projects': {
        'schema': ['project_id', 'name', 'investment_id', 'status', 'start_date', 'end_date',
                  'budget', 'actual_spend', 'progress_pct', 'manager', 'description', 'risk_level'],
        'data': [
            {
                'project_id': f'PRJ-{i:03d}',
                'name': f'{random.choice(["Phase", "Module", "Release", "Sprint"])} {random.choice(["Alpha", "Beta", "Core", "Enterprise"])} {i}',
                'investment_id': f'INV-{(i % 15) + 1:02d}',
                'status': random.choice(statuses),
                'start_date': (base_date - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
                'end_date': (base_date + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
                'budget': str(round(random.uniform(100000, 5000000), 2)),
                'actual_spend': str(round(random.uniform(50000, 3000000), 2)),
                'progress_pct': str(random.randint(5, 100)),
                'manager': random.choice(names),
                'description': f'Project for {random.choice(["modernization", "security", "migration", "development"])}',
                'risk_level': random.choice(risk_levels)
            }
            for i in range(1, 51)
        ]
    },
    'reference_data': {
        'schema': ['ref_id', 'category', 'code', 'value', 'description', 'display_order', 'active', 'created_date'],
        'data': [
            {
                'ref_id': f'REF-{i:03d}',
                'category': random.choice(['STATUS', 'RISK_LEVEL', 'PHASE', 'ROLE', 'APPROPRIATION', 'INVESTMENT_TYPE']),
                'code': f'CODE_{i:03d}',
                'value': random.choice(['Active', 'Pending', 'Low', 'High', 'Control', 'Select', 'CIO', 'PM', 'BSM', 'OPS']),
                'description': f'Reference data item {i}',
                'display_order': str(i),
                'active': random.choice(['true', 'false']),
                'created_date': (base_date - timedelta(days=random.randint(100, 500))).strftime('%Y-%m-%d')
            }
            for i in range(1, 41)
        ]
    },
    'review_history': {
        'schema': ['review_id', 'item_type', 'item_id', 'review_type', 'reviewer', 'review_date',
                  'decision', 'comments', 'next_review_date'],
        'data': [
            {
                'review_id': f'RVW-{i:04d}',
                'item_type': random.choice(['Investment', 'Project', 'Form', 'Report', 'Risk']),
                'item_id': f'{random.choice(["INV", "PRJ", "CPIC", "RPT", "RSK"])}-{random.randint(1, 50):03d}',
                'review_type': random.choice(['Monthly', 'Quarterly', 'TechStat', 'IRB', 'CIO']),
                'reviewer': random.choice(names),
                'review_date': (base_date - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d'),
                'decision': random.choice(['Approved', 'Rejected', 'Pending Changes', 'Escalated']),
                'comments': f'Review comments for item {i}',
                'next_review_date': (base_date + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d')
            }
            for i in range(1, 61)
        ]
    },
    'risk_register': {
        'schema': ['register_id', 'risk_id', 'investment_id', 'project_id', 'risk_title', 'category',
                  'probability', 'impact', 'risk_score', 'status', 'owner', 'mitigation', 'identified_date', 'due_date'],
        'data': [
            {
                'register_id': f'RR-{i:03d}',
                'risk_id': f'RSK-{i:03d}',
                'investment_id': f'INV-{(i % 15) + 1:02d}',
                'project_id': f'PRJ-{random.randint(1, 50):03d}',
                'risk_title': f'{random.choice(["Schedule", "Cost", "Technical", "Resource", "Security"])} - {random.choice(["Delay", "Overrun", "Complexity", "Shortage"])}',
                'category': random.choice(['Schedule', 'Cost', 'Technical', 'Resource', 'Security', 'Compliance']),
                'probability': random.choice(['Low', 'Medium', 'High']),
                'impact': random.choice(['Low', 'Medium', 'High', 'Critical']),
                'risk_score': str(random.randint(1, 25)),
                'status': random.choice(['Open', 'Mitigated', 'Closed', 'Monitoring']),
                'owner': random.choice(names),
                'mitigation': f'Implement {random.choice(["contingency", "backup", "alternative"])} plan',
                'identified_date': (base_date - timedelta(days=random.randint(10, 180))).strftime('%Y-%m-%d'),
                'due_date': (base_date + timedelta(days=random.randint(10, 90))).strftime('%Y-%m-%d')
            }
            for i in range(1, 51)
        ]
    },
    'risks': {
        'schema': ['risk_id', 'name', 'investment_id', 'project_id', 'category', 'probability',
                  'impact', 'score', 'status', 'owner', 'mitigation', 'identified_date'],
        'data': [
            {
                'risk_id': f'RSK-{i:03d}',
                'name': f'{random.choice(["Schedule", "Budget", "Technical", "Resource"])} Risk {i}',
                'investment_id': f'INV-{(i % 15) + 1:02d}',
                'project_id': f'PRJ-{random.randint(1, 50):03d}',
                'category': random.choice(['Schedule', 'Cost', 'Technical', 'Resource', 'Security']),
                'probability': random.choice(['Low', 'Medium', 'High']),
                'impact': random.choice(['Low', 'Medium', 'High', 'Critical']),
                'score': str(random.randint(1, 25)),
                'status': random.choice(['Open', 'Mitigated', 'Closed']),
                'owner': random.choice(names),
                'mitigation': f'Risk mitigation plan {i}',
                'identified_date': (base_date - timedelta(days=random.randint(10, 120))).strftime('%Y-%m-%d')
            }
            for i in range(1, 41)
        ]
    },
    'saved_reports': {
        'schema': ['report_id', 'report_name', 'report_type', 'created_by', 'created_date',
                  'last_run', 'schedule', 'parameters', 'status'],
        'data': [
            {
                'report_id': f'SRPT-{i:03d}',
                'report_name': f'{random.choice(["Monthly", "Quarterly", "Weekly", "Annual"])} {random.choice(["Status", "Financial", "Risk", "Performance"])} Report',
                'report_type': random.choice(['Status', 'Financial', 'Risk', 'Compliance', 'Executive']),
                'created_by': random.choice(names),
                'created_date': (base_date - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
                'last_run': (base_date - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                'schedule': random.choice(['Daily', 'Weekly', 'Monthly', 'On-Demand']),
                'parameters': f'{{"investment_id": "INV-{random.randint(1,15):02d}", "fiscal_year": "{random.choice([2024, 2025])}"}}',
                'status': random.choice(['Active', 'Paused', 'Archived'])
            }
            for i in range(1, 31)
        ]
    },
    'spike_sync_history': {
        'schema': ['sync_id', 'investment_id', 'sync_date', 'sync_type', 'status', 'records_synced',
                  'errors', 'initiated_by', 'duration_seconds'],
        'data': [
            {
                'sync_id': f'SYNC-{i:04d}',
                'investment_id': f'INV-{(i % 15) + 1:02d}',
                'sync_date': (base_date - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d %H:%M:%S'),
                'sync_type': random.choice(['Full', 'Incremental', 'Manual', 'Scheduled']),
                'status': random.choice(['Completed', 'Failed', 'Partial']),
                'records_synced': str(random.randint(10, 500)),
                'errors': str(random.randint(0, 5)),
                'initiated_by': random.choice(names + ['System']),
                'duration_seconds': str(random.randint(5, 300))
            }
            for i in range(1, 41)
        ]
    },
    'strategic_alignment': {
        'schema': ['alignment_id', 'investment_id', 'strategic_goal', 'alignment_score', 'justification',
                  'reviewer', 'review_date', 'fiscal_year', 'status'],
        'data': [
            {
                'alignment_id': f'SA-{i:03d}',
                'investment_id': f'INV-{(i % 15) + 1:02d}',
                'strategic_goal': random.choice(['Digital Transformation', 'Customer Service Excellence', 'Operational Efficiency', 'Security & Compliance', 'Data-Driven Decision Making']),
                'alignment_score': str(random.randint(60, 100)),
                'justification': f'Investment supports {random.choice(["modernization", "efficiency", "compliance", "innovation"])} objectives',
                'reviewer': random.choice(names),
                'review_date': (base_date - timedelta(days=random.randint(10, 90))).strftime('%Y-%m-%d'),
                'fiscal_year': str(random.choice([2024, 2025, 2026])),
                'status': random.choice(['Approved', 'Under Review', 'Pending'])
            }
            for i in range(1, 31)
        ]
    },
    'system_config': {
        'schema': ['config_id', 'config_key', 'config_value', 'category', 'description',
                  'last_updated', 'updated_by', 'active'],
        'data': [
            {
                'config_id': f'CFG-{i:03d}',
                'config_key': f'{random.choice(["MAX", "MIN", "DEFAULT", "ENABLE", "THRESHOLD"])}_{random.choice(["RECORDS", "USERS", "TIMEOUT", "RETRY", "LIMIT"])}',
                'config_value': str(random.choice([10, 50, 100, 500, 'true', 'false', '1000', '5000'])),
                'category': random.choice(['System', 'Security', 'Performance', 'Feature', 'Integration']),
                'description': f'Configuration setting {i}',
                'last_updated': (base_date - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d'),
                'updated_by': random.choice(names),
                'active': random.choice(['true', 'false'])
            }
            for i in range(1, 26)
        ]
    },
    'user_dashboard_config': {
        'schema': ['config_id', 'user_id', 'dashboard_name', 'layout_config', 'widgets',
                  'created_date', 'last_modified', 'is_default'],
        'data': [
            {
                'config_id': f'UDC-{i:03d}',
                'user_id': f'USR-{random.randint(1, 20):03d}',
                'dashboard_name': f'{random.choice(["Executive", "Portfolio", "Project", "Risk", "Custom"])} Dashboard',
                'layout_config': f'{{"columns": {random.choice([2, 3, 4])}, "rows": {random.choice([2, 3])}}}',
                'widgets': f'["status_cards", "charts", "tables", "kpis"]',
                'created_date': (base_date - timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d'),
                'last_modified': (base_date - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                'is_default': random.choice(['true', 'false'])
            }
            for i in range(1, 31)
        ]
    },
    'user_sessions': {
        'schema': ['session_id', 'user_id', 'login_time', 'logout_time', 'ip_address',
                  'user_agent', 'status', 'last_activity'],
        'data': [
            {
                'session_id': str(uuid.uuid4())[:8].upper(),
                'user_id': f'USR-{random.randint(1, 20):03d}',
                'login_time': (base_date - timedelta(hours=random.randint(1, 720))).strftime('%Y-%m-%d %H:%M:%S'),
                'logout_time': (base_date - timedelta(hours=random.randint(0, 500))).strftime('%Y-%m-%d %H:%M:%S') if random.random() > 0.3 else None,
                'ip_address': f'{random.randint(10, 192)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}',
                'user_agent': random.choice(['Chrome/120.0', 'Firefox/121.0', 'Safari/17.0', 'Edge/120.0']),
                'status': random.choice(['Active', 'Expired', 'Logged Out']),
                'last_activity': (base_date - timedelta(minutes=random.randint(0, 60))).strftime('%Y-%m-%d %H:%M:%S')
            }
            for i in range(1, 51)
        ]
    },
    'users': {
        'schema': ['user_id', 'email', 'name', 'role', 'organization', 'title',
                  'created_date', 'last_login', 'status', 'password_hash'],
        'data': [
            {
                'user_id': f'USR-{i:03d}',
                'email': emails[i % len(emails)],
                'name': names[i % len(names)],
                'role': roles[i % len(roles)],
                'organization': 'IRS',
                'title': random.choice(['Director', 'Manager', 'Analyst', 'Engineer', 'Coordinator']),
                'created_date': (base_date - timedelta(days=random.randint(30, 500))).strftime('%Y-%m-%d'),
                'last_login': (base_date - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                'status': random.choice(['Active', 'Inactive', 'Pending']),
                'password_hash': 'hashed_password_placeholder'
            }
            for i in range(1, 26)
        ]
    },
    'workflow_approvals': {
        'schema': ['approval_id', 'workflow_type', 'item_type', 'item_id', 'requested_by',
                  'current_approver', 'request_date', 'status', 'comments', 'approved_date', 'approval_level'],
        'data': [
            {
                'approval_id': f'WFA-{i:04d}',
                'workflow_type': random.choice(['Investment Approval', 'BCR', 'Project Initiation', 'Risk Escalation', 'Report Submission']),
                'item_type': random.choice(['Investment', 'Project', 'BCR', 'Report', 'Risk']),
                'item_id': f'{random.choice(["INV", "PRJ", "BCR", "RPT"])}-{random.randint(1, 50):03d}',
                'requested_by': random.choice(names),
                'current_approver': random.choice(names),
                'request_date': (base_date - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d'),
                'status': random.choice(['Pending', 'Approved', 'Rejected', 'Escalated', 'Cancelled']),
                'comments': f'Approval request comments {i}',
                'approved_date': (base_date - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d') if random.random() > 0.4 else None,
                'approval_level': str(random.randint(1, 4))
            }
            for i in range(1, 51)
        ]
    }
}

def main():
    print("=" * 70)
    print("CPIC BigQuery Tables - Populate All with 20-60 Records")
    print("=" * 70)

    # Create and populate all tables
    for table_name, table_info in tables.items():
        print(f"\n{table_name}:")
        create_table_if_not_exists(table_name, table_info['schema'])
        count = insert_data(table_name, table_info['data'])
        print(f"  Inserted {count} records")

    # Now count all tables
    print("\n" + "=" * 70)
    print("RECORD COUNTS FOR ALL TABLES:")
    print("=" * 70)

    all_tables = list(tables.keys())
    for table_name in sorted(all_tables):
        count = count_table(table_name)
        print(f"  {table_name}: {count} records")

    print("\n" + "=" * 70)
    print("All tables populated successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
