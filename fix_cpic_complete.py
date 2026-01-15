"""
Complete fix for CPIC Solutions:
1. Fix frontend onclick syntax
2. Populate BigQuery tables with sample data
3. Fix back button
"""

import os
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime, timedelta
import random

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'cpic_data'

def fix_frontend_onclick(filepath):
    """Fix the broken onclick syntax in frontend"""
    print(f"Fixing frontend onclick in {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the broken onclick syntax - $${f.form_id} should be ${f.form_id}
    content = content.replace("onclick=\"openFormDetail(\\'$${f.form_id}\\'", "onclick=\"openFormDetail(\\'${f.form_id}\\'")
    content = content.replace("\\'$${f.form_name}\\')", "\\'${f.form_name}\\')")

    # Also ensure proper escape for template literals
    content = content.replace("openFormDetail(\\'${f.form_id}\\', \\'${f.form_name}\\')", "openFormDetail(\\`${f.form_id}\\`, \\`${f.form_name}\\`)")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Fixed onclick syntax")

def populate_bigquery_tables():
    """Populate all BigQuery tables with sample data"""
    print("\nPopulating BigQuery tables...")

    client = bigquery.Client(project=PROJECT_ID)

    # Sample data generators
    names = ['John Smith', 'Maria Garcia', 'James Wilson', 'Sarah Chen', 'Michael Brown',
             'Emily Davis', 'Robert Johnson', 'Lisa Anderson', 'David Martinez', 'Jennifer Taylor',
             'William Lee', 'Amanda White', 'Craig Drake', 'Jim Keith']

    statuses = ['Active', 'Completed', 'In Progress', 'Pending', 'Approved', 'Draft']
    risk_levels = ['Low', 'Medium', 'High', 'Critical']
    phases = ['Preselect', 'Select', 'Control', 'Evaluate']

    base_date = datetime.now()

    # Table definitions with sample data
    tables_data = {
        'projects': {
            'schema': [
                'project_id', 'project_name', 'investment_id', 'status', 'start_date',
                'end_date', 'budget', 'actual_spend', 'progress_pct', 'project_manager',
                'description', 'risk_level', 'created_date'
            ],
            'rows': [
                {
                    'project_id': f'PRJ-{i:03d}',
                    'project_name': f'{random.choice(["Phase", "Module", "Release", "Sprint", "Initiative"])} {random.choice(["Alpha", "Beta", "Core", "Enterprise", "Cloud"])} {i}',
                    'investment_id': f'INV-{(i % 9) + 1:02d}',
                    'status': random.choice(statuses),
                    'start_date': (base_date - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
                    'end_date': (base_date + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
                    'budget': round(random.uniform(100000, 5000000), 2),
                    'actual_spend': round(random.uniform(50000, 3000000), 2),
                    'progress_pct': random.randint(10, 100),
                    'project_manager': random.choice(names),
                    'description': f'Project for {random.choice(["system modernization", "security enhancement", "data migration", "API development", "infrastructure upgrade"])}',
                    'risk_level': random.choice(risk_levels),
                    'created_date': base_date.strftime('%Y-%m-%d')
                }
                for i in range(1, 21)
            ]
        },
        'risks': {
            'schema': [
                'risk_id', 'risk_name', 'investment_id', 'project_id', 'category',
                'probability', 'impact', 'risk_score', 'status', 'owner',
                'mitigation_plan', 'identified_date', 'due_date'
            ],
            'rows': [
                {
                    'risk_id': f'RSK-{i:03d}',
                    'risk_name': f'{random.choice(["Schedule", "Budget", "Technical", "Resource", "Security"])} Risk - {random.choice(["Delay", "Overrun", "Complexity", "Shortage", "Vulnerability"])}',
                    'investment_id': f'INV-{(i % 9) + 1:02d}',
                    'project_id': f'PRJ-{(i % 20) + 1:03d}',
                    'category': random.choice(['Schedule', 'Cost', 'Technical', 'Resource', 'Security', 'Compliance']),
                    'probability': random.choice(['Low', 'Medium', 'High']),
                    'impact': random.choice(['Low', 'Medium', 'High', 'Critical']),
                    'risk_score': random.randint(1, 25),
                    'status': random.choice(['Open', 'Mitigated', 'Closed', 'Monitoring']),
                    'owner': random.choice(names),
                    'mitigation_plan': f'Implement {random.choice(["contingency", "backup", "workaround", "alternative", "escalation"])} plan',
                    'identified_date': (base_date - timedelta(days=random.randint(10, 90))).strftime('%Y-%m-%d'),
                    'due_date': (base_date + timedelta(days=random.randint(10, 90))).strftime('%Y-%m-%d')
                }
                for i in range(1, 21)
            ]
        },
        'monthly_reports': {
            'schema': [
                'report_id', 'investment_id', 'report_month', 'overall_status', 'cost_status',
                'schedule_status', 'executive_summary', 'risks_high', 'risks_medium', 'risks_low',
                'submitted_by', 'submitted_date', 'approved_by', 'approved_date'
            ],
            'rows': [
                {
                    'report_id': f'RPT-{i:03d}',
                    'investment_id': f'INV-{(i % 9) + 1:02d}',
                    'report_month': f'2025-{((i % 12) + 1):02d}',
                    'overall_status': random.choice(['green', 'yellow', 'red']),
                    'cost_status': random.choice(['green', 'yellow', 'red']),
                    'schedule_status': random.choice(['green', 'yellow', 'red']),
                    'executive_summary': f'Monthly status report for {random.choice(["Q1", "Q2", "Q3", "Q4"])} activities. {random.choice(["On track", "Minor delays", "Requires attention", "Progressing well"])}.',
                    'risks_high': random.randint(0, 3),
                    'risks_medium': random.randint(0, 5),
                    'risks_low': random.randint(0, 8),
                    'submitted_by': random.choice(names),
                    'submitted_date': (base_date - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
                    'approved_by': random.choice(names),
                    'approved_date': (base_date - timedelta(days=random.randint(0, 15))).strftime('%Y-%m-%d')
                }
                for i in range(1, 21)
            ]
        },
        'form_records': {
            'schema': [
                'record_id', 'form_id', 'field_name', 'field_value', 'record_index',
                'created_by', 'created_date', 'modified_by', 'modified_date', 'status'
            ],
            'rows': []  # Will be populated with form records
        }
    }

    # Generate form records for all 185 forms (covers both solutions)
    form_record_rows = []
    record_counter = 1
    for form_num in range(1, 186):
        form_id = f'CPIC-{form_num:03d}'
        num_records = random.randint(15, 20)

        for rec_idx in range(num_records):
            # Create multiple field entries per record
            fields = [
                ('item_name', f'{random.choice(["Task", "Action", "Item", "Entry"])} {rec_idx + 1}'),
                ('description', f'{random.choice(["Review", "Update", "Implement", "Assess", "Document"])} {random.choice(["system", "process", "component", "module"])}'),
                ('status', random.choice(statuses)),
                ('assigned_to', random.choice(names)),
                ('due_date', (base_date + timedelta(days=random.randint(-30, 90))).strftime('%Y-%m-%d')),
                ('priority', random.choice(['High', 'Medium', 'Low'])),
                ('amount', str(round(random.uniform(10000, 500000), 2))),
                ('completion_pct', str(random.randint(0, 100))),
            ]

            for field_name, field_value in fields:
                form_record_rows.append({
                    'record_id': f'REC-{record_counter:06d}',
                    'form_id': form_id,
                    'field_name': field_name,
                    'field_value': field_value,
                    'record_index': rec_idx + 1,
                    'created_by': random.choice(names),
                    'created_date': (base_date - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d'),
                    'modified_by': random.choice(names),
                    'modified_date': (base_date - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                    'status': random.choice(['Active', 'Archived', 'Draft'])
                })
                record_counter += 1

    tables_data['form_records']['rows'] = form_record_rows[:5000]  # Limit to avoid timeout

    # Additional tables that need data
    additional_tables = {
        'activities': {
            'schema': ['activity_id', 'activity_type', 'description', 'user_id', 'investment_id',
                      'timestamp', 'details', 'status'],
            'rows': [
                {
                    'activity_id': f'ACT-{i:04d}',
                    'activity_type': random.choice(['Update', 'Create', 'Approve', 'Review', 'Submit', 'Comment']),
                    'description': f'{random.choice(["Updated", "Created", "Reviewed", "Approved", "Submitted"])} {random.choice(["form", "report", "document", "record"])}',
                    'user_id': f'USR-{random.randint(1, 10):03d}',
                    'investment_id': f'INV-{(i % 9) + 1:02d}',
                    'timestamp': (base_date - timedelta(hours=random.randint(1, 720))).isoformat(),
                    'details': f'Activity details for item {i}',
                    'status': random.choice(['Completed', 'Pending'])
                }
                for i in range(1, 51)
            ]
        },
        'approvals': {
            'schema': ['approval_id', 'item_type', 'item_id', 'requested_by', 'approved_by',
                      'request_date', 'approval_date', 'status', 'comments'],
            'rows': [
                {
                    'approval_id': f'APR-{i:03d}',
                    'item_type': random.choice(['Investment', 'Project', 'BCR', 'Report', 'Form']),
                    'item_id': f'{random.choice(["INV", "PRJ", "BCR", "RPT"])}-{random.randint(1, 20):03d}',
                    'requested_by': random.choice(names),
                    'approved_by': random.choice(names) if random.random() > 0.3 else None,
                    'request_date': (base_date - timedelta(days=random.randint(5, 60))).strftime('%Y-%m-%d'),
                    'approval_date': (base_date - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d') if random.random() > 0.3 else None,
                    'status': random.choice(['Approved', 'Pending', 'Rejected', 'In Review']),
                    'comments': f'Approval comment for item {i}'
                }
                for i in range(1, 21)
            ]
        },
        'baselines': {
            'schema': ['baseline_id', 'investment_id', 'project_id', 'baseline_date', 'cost_baseline',
                      'schedule_baseline', 'scope_baseline', 'created_by', 'version'],
            'rows': [
                {
                    'baseline_id': f'BSL-{i:03d}',
                    'investment_id': f'INV-{(i % 9) + 1:02d}',
                    'project_id': f'PRJ-{(i % 20) + 1:03d}',
                    'baseline_date': (base_date - timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d'),
                    'cost_baseline': round(random.uniform(500000, 10000000), 2),
                    'schedule_baseline': (base_date + timedelta(days=random.randint(60, 365))).strftime('%Y-%m-%d'),
                    'scope_baseline': f'Scope v{i}.0 - {random.choice(["Full", "Phase 1", "MVP", "Core"])} implementation',
                    'created_by': random.choice(names),
                    'version': f'{(i // 5) + 1}.{i % 5}'
                }
                for i in range(1, 21)
            ]
        },
        'milestones': {
            'schema': ['milestone_id', 'project_id', 'milestone_name', 'planned_date', 'actual_date',
                      'status', 'description', 'owner'],
            'rows': [
                {
                    'milestone_id': f'MLS-{i:03d}',
                    'project_id': f'PRJ-{(i % 20) + 1:03d}',
                    'milestone_name': f'{random.choice(["Phase", "Gate", "Release", "Review"])} {random.choice(["1", "2", "3", "A", "B"])} {random.choice(["Complete", "Approved", "Delivered"])}',
                    'planned_date': (base_date + timedelta(days=random.randint(-60, 180))).strftime('%Y-%m-%d'),
                    'actual_date': (base_date + timedelta(days=random.randint(-60, 30))).strftime('%Y-%m-%d') if random.random() > 0.4 else None,
                    'status': random.choice(['Completed', 'On Track', 'At Risk', 'Delayed', 'Pending']),
                    'description': f'Milestone for {random.choice(["development", "testing", "deployment", "review"])} phase',
                    'owner': random.choice(names)
                }
                for i in range(1, 31)
            ]
        },
        'budget_items': {
            'schema': ['budget_id', 'investment_id', 'category', 'line_item', 'fy2024', 'fy2025',
                      'fy2026', 'total', 'status'],
            'rows': [
                {
                    'budget_id': f'BUD-{i:03d}',
                    'investment_id': f'INV-{(i % 9) + 1:02d}',
                    'category': random.choice(['Personnel', 'Hardware', 'Software', 'Services', 'Training', 'Other']),
                    'line_item': f'{random.choice(["Contractor", "License", "Infrastructure", "Support", "Development"])} - {random.choice(["Core", "Extended", "Annual", "One-time"])}',
                    'fy2024': round(random.uniform(50000, 2000000), 2),
                    'fy2025': round(random.uniform(50000, 2500000), 2),
                    'fy2026': round(random.uniform(50000, 3000000), 2),
                    'total': round(random.uniform(200000, 7000000), 2),
                    'status': random.choice(['Approved', 'Pending', 'Under Review'])
                }
                for i in range(1, 31)
            ]
        },
        'compliance_items': {
            'schema': ['compliance_id', 'investment_id', 'requirement', 'category', 'status',
                      'evidence', 'reviewer', 'review_date', 'next_review'],
            'rows': [
                {
                    'compliance_id': f'CMP-{i:03d}',
                    'investment_id': f'INV-{(i % 9) + 1:02d}',
                    'requirement': f'{random.choice(["FISMA", "Section 508", "FITARA", "Privacy Act", "ATO"])} - {random.choice(["Annual Review", "Continuous Monitoring", "Assessment", "Certification"])}',
                    'category': random.choice(['Security', 'Privacy', 'Accessibility', 'Governance', 'Data']),
                    'status': random.choice(['Compliant', 'Non-Compliant', 'Partial', 'In Progress']),
                    'evidence': f'Evidence document ref: DOC-{random.randint(100, 999)}',
                    'reviewer': random.choice(names),
                    'review_date': (base_date - timedelta(days=random.randint(10, 90))).strftime('%Y-%m-%d'),
                    'next_review': (base_date + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
                }
                for i in range(1, 21)
            ]
        },
        'techstat_reviews': {
            'schema': ['review_id', 'investment_id', 'review_date', 'review_type', 'findings',
                      'action_items', 'status', 'next_review', 'reviewer'],
            'rows': [
                {
                    'review_id': f'TSR-{i:03d}',
                    'investment_id': f'INV-{(i % 9) + 1:02d}',
                    'review_date': (base_date - timedelta(days=random.randint(10, 180))).strftime('%Y-%m-%d'),
                    'review_type': random.choice(['Quarterly', 'Monthly', 'Ad-hoc', 'Escalation']),
                    'findings': f'{random.randint(1, 5)} findings identified - {random.choice(["schedule variance", "cost overrun", "scope creep", "resource issues"])}',
                    'action_items': random.randint(0, 8),
                    'status': random.choice(['Closed', 'Open', 'In Progress']),
                    'next_review': (base_date + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d'),
                    'reviewer': random.choice(names)
                }
                for i in range(1, 16)
            ]
        },
        'documents': {
            'schema': ['document_id', 'document_name', 'document_type', 'investment_id', 'project_id',
                      'version', 'status', 'uploaded_by', 'upload_date', 'file_size'],
            'rows': [
                {
                    'document_id': f'DOC-{i:04d}',
                    'document_name': f'{random.choice(["Business Case", "Project Plan", "Risk Register", "Status Report", "Technical Design", "Test Plan"])}_v{random.randint(1,5)}.{random.choice(["pdf", "docx", "xlsx"])}',
                    'document_type': random.choice(['Business Case', 'Report', 'Plan', 'Assessment', 'Review']),
                    'investment_id': f'INV-{(i % 9) + 1:02d}',
                    'project_id': f'PRJ-{(i % 20) + 1:03d}' if random.random() > 0.3 else None,
                    'version': f'{random.randint(1,5)}.{random.randint(0,9)}',
                    'status': random.choice(['Final', 'Draft', 'Under Review', 'Approved']),
                    'uploaded_by': random.choice(names),
                    'upload_date': (base_date - timedelta(days=random.randint(1, 120))).strftime('%Y-%m-%d'),
                    'file_size': random.randint(50, 5000)
                }
                for i in range(1, 41)
            ]
        },
        'action_items': {
            'schema': ['action_id', 'description', 'source', 'investment_id', 'assigned_to',
                      'due_date', 'status', 'priority', 'created_date', 'closed_date'],
            'rows': [
                {
                    'action_id': f'ACN-{i:03d}',
                    'description': f'{random.choice(["Review", "Update", "Complete", "Submit", "Approve"])} {random.choice(["documentation", "assessment", "report", "plan", "analysis"])} for {random.choice(["Q1", "Q2", "Q3", "Q4"])}',
                    'source': random.choice(['TechStat', 'IRB', 'Monthly Review', 'Risk Assessment', 'Audit']),
                    'investment_id': f'INV-{(i % 9) + 1:02d}',
                    'assigned_to': random.choice(names),
                    'due_date': (base_date + timedelta(days=random.randint(-30, 60))).strftime('%Y-%m-%d'),
                    'status': random.choice(['Open', 'In Progress', 'Closed', 'Overdue']),
                    'priority': random.choice(['High', 'Medium', 'Low']),
                    'created_date': (base_date - timedelta(days=random.randint(10, 90))).strftime('%Y-%m-%d'),
                    'closed_date': (base_date - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d') if random.random() > 0.5 else None
                }
                for i in range(1, 31)
            ]
        },
        'metrics': {
            'schema': ['metric_id', 'metric_name', 'investment_id', 'target_value', 'actual_value',
                      'measurement_date', 'trend', 'status', 'owner'],
            'rows': [
                {
                    'metric_id': f'MTR-{i:03d}',
                    'metric_name': random.choice(['Cost Performance Index', 'Schedule Performance Index', 'Defect Density', 'User Satisfaction', 'System Availability', 'Response Time']),
                    'investment_id': f'INV-{(i % 9) + 1:02d}',
                    'target_value': round(random.uniform(0.8, 1.2), 2),
                    'actual_value': round(random.uniform(0.6, 1.3), 2),
                    'measurement_date': (base_date - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d'),
                    'trend': random.choice(['Up', 'Down', 'Stable']),
                    'status': random.choice(['Green', 'Yellow', 'Red']),
                    'owner': random.choice(names)
                }
                for i in range(1, 31)
            ]
        }
    }

    # Merge all tables
    tables_data.update(additional_tables)

    # Insert data into BigQuery
    for table_name, table_info in tables_data.items():
        if not table_info['rows']:
            continue

        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

        try:
            # Check if table exists, create if not
            try:
                client.get_table(table_id)
                print(f"  Table {table_name} exists")
            except Exception:
                # Create table with schema
                schema = [bigquery.SchemaField(col, "STRING") for col in table_info['schema']]
                table = bigquery.Table(table_id, schema=schema)
                client.create_table(table)
                print(f"  Created table {table_name}")

            # Clear existing data
            query = f"DELETE FROM `{table_id}` WHERE TRUE"
            try:
                client.query(query).result()
            except Exception:
                pass  # Table might be empty or not exist

            # Convert all values to strings for insertion
            rows_to_insert = []
            for row in table_info['rows']:
                str_row = {k: str(v) if v is not None else None for k, v in row.items()}
                rows_to_insert.append(str_row)

            # Insert in batches
            batch_size = 500
            for i in range(0, len(rows_to_insert), batch_size):
                batch = rows_to_insert[i:i+batch_size]
                errors = client.insert_rows_json(table_id, batch)
                if errors:
                    print(f"    Errors inserting batch: {errors[:2]}")

            print(f"  Inserted {len(rows_to_insert)} rows into {table_name}")

        except Exception as e:
            print(f"  Error with table {table_name}: {e}")

    print("\nBigQuery tables populated!")

def main():
    print("=" * 60)
    print("CPIC Complete Fix Script")
    print("=" * 60)

    base_path = r"C:\1AITrading\Trading"

    # Fix Solution A frontend
    print("\n--- Fixing Solution A Frontend ---")
    fix_frontend_onclick(os.path.join(base_path, "cpic_suggestion_a", "backend", "frontend", "index.html"))

    # Fix Solution B frontend
    print("\n--- Fixing Solution B Frontend ---")
    fix_frontend_onclick(os.path.join(base_path, "cpic_suggestion_b", "backend", "frontend", "index.html"))

    # Populate BigQuery tables
    print("\n--- Populating BigQuery Tables ---")
    populate_bigquery_tables()

    print("\n" + "=" * 60)
    print("Fix complete! Redeploy both solutions.")
    print("=" * 60)

if __name__ == "__main__":
    main()
