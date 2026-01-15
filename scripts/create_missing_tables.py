"""
Create and populate the 9 missing BigQuery tables
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

def ts():
    return (base_date - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d %H:%M:%S')

def d():
    return (base_date - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d')

# Define schemas and data generators for missing tables
MISSING_TABLES = {
    'notional_structure': {
        'schema': [
            ('structure_id', 'STRING'),
            ('name', 'STRING'),
            ('description', 'STRING'),
            ('parent_id', 'STRING'),
            ('level', 'INTEGER'),
            ('category', 'STRING'),
            ('budget_allocation', 'FLOAT'),
            ('status', 'STRING'),
            ('effective_date', 'STRING'),
            ('owner', 'STRING'),
            ('created_at', 'STRING')
        ],
        'generator': lambda i: {
            'structure_id': f'NS-{i:03d}',
            'name': f'{random.choice(["IT Infrastructure", "Application Dev", "Security", "Data Analytics", "Cloud Services"])} Unit {i}',
            'description': f'Notional structure for organizational unit {i} covering {random.choice(["modernization", "operations", "transformation"])} initiatives',
            'parent_id': f'NS-{max(1, i-random.randint(1,5)):03d}' if i > 1 else 'ROOT',
            'level': random.randint(1, 5),
            'category': random.choice(['Division', 'Branch', 'Section', 'Team', 'Unit']),
            'budget_allocation': round(random.uniform(500000, 10000000), 2),
            'status': random.choice(['Active', 'Proposed', 'Under Review']),
            'effective_date': d(),
            'owner': random.choice(names),
            'created_at': ts()
        }
    },
    'investment_level': {
        'schema': [
            ('level_id', 'STRING'),
            ('investment_id', 'STRING'),
            ('level_name', 'STRING'),
            ('description', 'STRING'),
            ('threshold_min', 'FLOAT'),
            ('threshold_max', 'FLOAT'),
            ('approval_authority', 'STRING'),
            ('review_frequency', 'STRING'),
            ('status', 'STRING'),
            ('created_at', 'STRING')
        ],
        'generator': lambda i: {
            'level_id': f'IL-{i:03d}',
            'investment_id': f'INV-{(i % 15) + 1:02d}',
            'level_name': random.choice(['Tier 1 - Major', 'Tier 2 - Significant', 'Tier 3 - Standard', 'Tier 4 - Minor']),
            'description': f'Investment classification level {i} for {random.choice(["enterprise", "departmental", "project-level"])} investments',
            'threshold_min': round(random.uniform(100000, 1000000), 2),
            'threshold_max': round(random.uniform(1000000, 50000000), 2),
            'approval_authority': random.choice(['CIO', 'Deputy CIO', 'IRB', 'Division Director']),
            'review_frequency': random.choice(['Monthly', 'Quarterly', 'Semi-Annual', 'Annual']),
            'status': random.choice(['Active', 'Pending', 'Approved']),
            'created_at': ts()
        }
    },
    'activity_level': {
        'schema': [
            ('activity_id', 'STRING'),
            ('investment_id', 'STRING'),
            ('project_id', 'STRING'),
            ('activity_name', 'STRING'),
            ('description', 'STRING'),
            ('activity_type', 'STRING'),
            ('start_date', 'STRING'),
            ('end_date', 'STRING'),
            ('progress_pct', 'INTEGER'),
            ('status', 'STRING'),
            ('owner', 'STRING'),
            ('created_at', 'STRING')
        ],
        'generator': lambda i: {
            'activity_id': f'ACT-{i:03d}',
            'investment_id': f'INV-{(i % 15) + 1:02d}',
            'project_id': f'PRJ-{random.randint(1, 50):03d}',
            'activity_name': f'{random.choice(["Requirements", "Design", "Development", "Testing", "Deployment"])} Phase {i}',
            'description': f'Activity for {random.choice(["system integration", "data migration", "security implementation", "user training"])} tasks',
            'activity_type': random.choice(['Development', 'Operations', 'Maintenance', 'Enhancement']),
            'start_date': d(),
            'end_date': (base_date + timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d'),
            'progress_pct': random.randint(0, 100),
            'status': random.choice(['Not Started', 'In Progress', 'Completed', 'On Hold']),
            'owner': random.choice(names),
            'created_at': ts()
        }
    },
    'cpic_phase_tracking': {
        'schema': [
            ('tracking_id', 'STRING'),
            ('investment_id', 'STRING'),
            ('phase', 'STRING'),
            ('phase_status', 'STRING'),
            ('entry_date', 'STRING'),
            ('exit_date', 'STRING'),
            ('gate_review_date', 'STRING'),
            ('gate_decision', 'STRING'),
            ('reviewer', 'STRING'),
            ('notes', 'STRING'),
            ('created_at', 'STRING')
        ],
        'generator': lambda i: {
            'tracking_id': f'PT-{i:03d}',
            'investment_id': f'INV-{(i % 15) + 1:02d}',
            'phase': random.choice(['Preselect', 'Select', 'Control', 'Evaluate']),
            'phase_status': random.choice(['Active', 'Completed', 'Pending Gate Review']),
            'entry_date': d(),
            'exit_date': (base_date + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d'),
            'gate_review_date': d(),
            'gate_decision': random.choice(['Approved', 'Conditional', 'Deferred', 'Pending']),
            'reviewer': random.choice(names),
            'notes': f'Phase tracking notes for investment review cycle {i}',
            'created_at': ts()
        }
    },
    'compliance_status': {
        'schema': [
            ('compliance_id', 'STRING'),
            ('investment_id', 'STRING'),
            ('requirement', 'STRING'),
            ('description', 'STRING'),
            ('regulation', 'STRING'),
            ('status', 'STRING'),
            ('assessment_date', 'STRING'),
            ('next_review', 'STRING'),
            ('findings', 'STRING'),
            ('remediation_plan', 'STRING'),
            ('owner', 'STRING'),
            ('created_at', 'STRING')
        ],
        'generator': lambda i: {
            'compliance_id': f'CMP-{i:03d}',
            'investment_id': f'INV-{(i % 15) + 1:02d}',
            'requirement': random.choice(['FISMA', 'Section 508', 'Privacy Act', 'FITARA', 'OMB A-130']),
            'description': f'Compliance assessment for {random.choice(["security controls", "accessibility standards", "privacy requirements", "IT management"])}',
            'regulation': random.choice(['Federal', 'Treasury', 'IRS Policy', 'OMB Circular']),
            'status': random.choice(['Compliant', 'Non-Compliant', 'Partially Compliant', 'Under Review']),
            'assessment_date': d(),
            'next_review': (base_date + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
            'findings': f'{random.randint(0, 5)} findings identified',
            'remediation_plan': f'Remediation activities scheduled for {random.choice(["Q1", "Q2", "Q3", "Q4"])} FY{random.randint(2025, 2026)}',
            'owner': random.choice(names),
            'created_at': ts()
        }
    },
    'operational_metrics': {
        'schema': [
            ('metric_id', 'STRING'),
            ('investment_id', 'STRING'),
            ('metric_name', 'STRING'),
            ('description', 'STRING'),
            ('category', 'STRING'),
            ('target_value', 'FLOAT'),
            ('actual_value', 'FLOAT'),
            ('variance_pct', 'FLOAT'),
            ('measurement_period', 'STRING'),
            ('trend', 'STRING'),
            ('status', 'STRING'),
            ('owner', 'STRING'),
            ('created_at', 'STRING')
        ],
        'generator': lambda i: {
            'metric_id': f'OM-{i:03d}',
            'investment_id': f'INV-{(i % 15) + 1:02d}',
            'metric_name': random.choice(['System Availability', 'Response Time', 'User Satisfaction', 'Cost Efficiency', 'Throughput']),
            'description': f'Operational performance metric for {random.choice(["production systems", "user services", "batch processing", "API endpoints"])}',
            'category': random.choice(['Performance', 'Reliability', 'Cost', 'Quality', 'Security']),
            'target_value': round(random.uniform(90, 99.9), 2),
            'actual_value': round(random.uniform(85, 99.9), 2),
            'variance_pct': round(random.uniform(-10, 10), 2),
            'measurement_period': f'{random.choice(["Q1", "Q2", "Q3", "Q4"])} FY2025',
            'trend': random.choice(['Improving', 'Stable', 'Declining']),
            'status': random.choice(['On Target', 'Below Target', 'Above Target']),
            'owner': random.choice(names),
            'created_at': ts()
        }
    },
    'current_structure': {
        'schema': [
            ('structure_id', 'STRING'),
            ('name', 'STRING'),
            ('description', 'STRING'),
            ('structure_type', 'STRING'),
            ('parent_id', 'STRING'),
            ('level', 'INTEGER'),
            ('organization', 'STRING'),
            ('budget', 'FLOAT'),
            ('fte_count', 'INTEGER'),
            ('status', 'STRING'),
            ('effective_date', 'STRING'),
            ('owner', 'STRING'),
            ('created_at', 'STRING')
        ],
        'generator': lambda i: {
            'structure_id': f'CS-{i:03d}',
            'name': f'{random.choice(["Enterprise Services", "Tax Processing", "Compliance Systems", "Taxpayer Services", "IT Operations"])} - {i}',
            'description': f'Current organizational structure for {random.choice(["IT division", "business unit", "shared services", "program office"])}',
            'structure_type': random.choice(['Division', 'Office', 'Branch', 'Section']),
            'parent_id': f'CS-{max(1, i-random.randint(1,3)):03d}' if i > 1 else 'ROOT',
            'level': random.randint(1, 4),
            'organization': 'IRS',
            'budget': round(random.uniform(1000000, 50000000), 2),
            'fte_count': random.randint(10, 500),
            'status': random.choice(['Active', 'Restructuring', 'Proposed']),
            'effective_date': d(),
            'owner': random.choice(names),
            'created_at': ts()
        }
    },
    'future_structure': {
        'schema': [
            ('structure_id', 'STRING'),
            ('name', 'STRING'),
            ('description', 'STRING'),
            ('structure_type', 'STRING'),
            ('current_structure_id', 'STRING'),
            ('target_state', 'STRING'),
            ('transition_date', 'STRING'),
            ('budget_impact', 'FLOAT'),
            ('fte_impact', 'INTEGER'),
            ('status', 'STRING'),
            ('approval_status', 'STRING'),
            ('owner', 'STRING'),
            ('created_at', 'STRING')
        ],
        'generator': lambda i: {
            'structure_id': f'FS-{i:03d}',
            'name': f'{random.choice(["Digital Services", "Cloud Operations", "Data Analytics", "Modernization Office", "Cyber Security"])} - Future {i}',
            'description': f'Future state organizational structure for {random.choice(["IT transformation", "cloud migration", "service consolidation", "capability enhancement"])}',
            'structure_type': random.choice(['Division', 'Center of Excellence', 'Shared Services', 'Virtual Team']),
            'current_structure_id': f'CS-{random.randint(1, 40):03d}',
            'target_state': random.choice(['Consolidated', 'Expanded', 'Realigned', 'New Capability']),
            'transition_date': (base_date + timedelta(days=random.randint(90, 730))).strftime('%Y-%m-%d'),
            'budget_impact': round(random.uniform(-5000000, 10000000), 2),
            'fte_impact': random.randint(-50, 100),
            'status': random.choice(['Planning', 'Approved', 'In Transition', 'Proposed']),
            'approval_status': random.choice(['Pending', 'Approved', 'Under Review']),
            'owner': random.choice(names),
            'created_at': ts()
        }
    },
    'investment_mapping': {
        'schema': [
            ('mapping_id', 'STRING'),
            ('investment_id', 'STRING'),
            ('strategic_goal', 'STRING'),
            ('description', 'STRING'),
            ('business_capability', 'STRING'),
            ('technology_domain', 'STRING'),
            ('alignment_score', 'INTEGER'),
            ('priority', 'STRING'),
            ('dependencies', 'STRING'),
            ('status', 'STRING'),
            ('owner', 'STRING'),
            ('created_at', 'STRING')
        ],
        'generator': lambda i: {
            'mapping_id': f'IM-{i:03d}',
            'investment_id': f'INV-{(i % 15) + 1:02d}',
            'strategic_goal': random.choice(['Taxpayer Service Excellence', 'Enforcement Modernization', 'IT Infrastructure', 'Workforce Development', 'Data Analytics']),
            'description': f'Investment mapping to strategic objectives for {random.choice(["enterprise initiatives", "modernization programs", "compliance systems"])}',
            'business_capability': random.choice(['Customer Service', 'Tax Processing', 'Compliance', 'Analytics', 'Infrastructure']),
            'technology_domain': random.choice(['Cloud', 'Data', 'Security', 'Applications', 'Infrastructure']),
            'alignment_score': random.randint(60, 100),
            'priority': random.choice(['High', 'Medium', 'Low', 'Critical']),
            'dependencies': f'{random.randint(1, 5)} dependent investments',
            'status': random.choice(['Mapped', 'Under Review', 'Approved']),
            'owner': random.choice(names),
            'created_at': ts()
        }
    }
}

def create_and_populate_table(table_name, config):
    """Create table and populate with data"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Create schema
    schema = [bigquery.SchemaField(name, dtype) for name, dtype in config['schema']]

    # Delete if exists
    client.delete_table(table_id, not_found_ok=True)

    # Create table
    table = bigquery.Table(table_id, schema=schema)
    client.create_table(table)
    print(f"  Created table: {table_name}")

    # Generate data (40 records each)
    num_records = random.randint(35, 50)
    data = []
    for i in range(1, num_records + 1):
        record = config['generator'](i)
        data.append(record)

    # Insert data
    errors = client.insert_rows_json(table_id, data)
    if errors:
        print(f"    Errors: {errors[0]}")
        return 0

    print(f"  Inserted {len(data)} records")
    return len(data)

def main():
    print("=" * 70)
    print("Creating and Populating 9 Missing Tables")
    print("=" * 70)

    total_records = 0

    for table_name, config in MISSING_TABLES.items():
        print(f"\n{table_name}:")
        count = create_and_populate_table(table_name, config)
        total_records += count

    print("\n" + "=" * 70)
    print("Verification - All Table Counts:")
    print("=" * 70)

    # Verify counts for the 9 new tables
    for table_name in MISSING_TABLES.keys():
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        query = f"SELECT COUNT(*) as cnt FROM `{table_id}`"
        result = client.query(query).result()
        for row in result:
            print(f"  {table_name}: {row.cnt} records")

    print(f"\n  TOTAL NEW RECORDS: {total_records}")

if __name__ == "__main__":
    main()
