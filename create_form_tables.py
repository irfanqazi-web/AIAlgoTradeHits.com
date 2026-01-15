"""
Create individual BigQuery tables for each CPIC Form
134 tables, each with 20-60 records representing form transactions
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime, timedelta
import random
import re

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'cpic_data'

client = bigquery.Client(project=PROJECT_ID)

base_date = datetime.now()
names = ['John Smith', 'Maria Garcia', 'James Wilson', 'Sarah Chen', 'Michael Brown',
         'Emily Davis', 'Robert Johnson', 'Lisa Anderson', 'David Martinez', 'Jennifer Taylor',
         'William Lee', 'Amanda White', 'Craig Drake', 'Jim Keith']

# Form definitions with their schema types
FORMS = [
    # PRESELECT (15)
    ("CPIC_001_Strategic_Planning_Document", "strategy"),
    ("CPIC_002_Needs_Identification_Report", "business_analysis"),
    ("CPIC_003_Initial_Screening_Criteria", "governance"),
    ("CPIC_004_Preliminary_Business_Case", "investment"),
    ("CPIC_005_Portfolio_Prioritization_Request", "strategy"),
    ("CPIC_006_Mission_Alignment_Assessment", "strategy"),
    ("CPIC_007_Resource_Availability_Check", "resource"),
    ("CPIC_008_Technical_Feasibility_Study", "technical"),
    ("CPIC_009_Budget_Authority_Request", "financial"),
    ("CPIC_010_Stakeholder_Identification", "strategy"),
    ("CPIC_011_Initial_Risk_Screening", "risk"),
    ("CPIC_012_Capability_Gap_Assessment", "technical"),
    ("CPIC_013_Investment_Proposal_Draft", "investment"),
    ("CPIC_014_CIO_Endorsement_Request", "governance"),
    ("CPIC_015_IRB_Submission_Package", "governance"),
    # SELECT (24)
    ("CPIC_016_OMB_Exhibit_300_Business_Case", "investment"),
    ("CPIC_017_Investment_Screening_Criteria", "investment"),
    ("CPIC_018_Alternatives_Analysis", "investment"),
    ("CPIC_019_Cost_Benefit_Analysis", "financial"),
    ("CPIC_020_Risk_Assessment_Detailed", "risk"),
    ("CPIC_021_Strategic_Alignment_Assessment", "strategy"),
    ("CPIC_022_Architecture_Review_Request", "technical"),
    ("CPIC_023_Security_Requirements_Document", "security"),
    ("CPIC_024_Investment_Proposal_Final", "investment"),
    ("CPIC_025_Stakeholder_Analysis_Complete", "strategy"),
    ("CPIC_026_Capability_Gap_Analysis_Final", "technical"),
    ("CPIC_027_Resource_Requirements_Plan", "resource"),
    ("CPIC_028_Procurement_Strategy", "acquisition"),
    ("CPIC_029_Performance_Measures_Plan", "performance"),
    ("CPIC_030_IRB_Review_Package", "governance"),
    ("CPIC_031_EA_Compliance_Certification", "compliance"),
    ("CPIC_032_Privacy_Impact_Assessment_Initial", "compliance"),
    ("CPIC_033_Section_508_Assessment", "compliance"),
    ("CPIC_034_Budget_Formulation_Package", "financial"),
    ("CPIC_035_Governance_Structure_Plan", "governance"),
    ("CPIC_036_Communication_Plan", "strategy"),
    ("CPIC_037_Training_Needs_Assessment", "training"),
    ("CPIC_038_Transition_Planning_Document", "project"),
    ("CPIC_039_CIO_Approval_Package", "governance"),
    # CONTROL (80) - Monthly operations
    ("CPIC_040_Monthly_Status_Report", "reporting"),
    ("CPIC_041_Baseline_Change_Request", "change"),
    ("CPIC_042_Earned_Value_Management_Report", "financial"),
    ("CPIC_043_Risk_Register_Update", "risk"),
    ("CPIC_044_TechStat_Review_Preparation", "governance"),
    ("CPIC_045_Contractor_Performance_Report", "acquisition"),
    ("CPIC_046_Quality_Assurance_Report", "quality"),
    ("CPIC_047_Security_Assessment_Report", "security"),
    ("CPIC_048_Project_Schedule_Update", "project"),
    ("CPIC_049_Budget_Execution_Report", "financial"),
    ("CPIC_050_Release_Management_Plan", "development"),
]

# Add remaining control forms (51-119)
control_types = ['development', 'infrastructure', 'quality', 'operations', 'security', 'compliance', 'performance', 'technical', 'training', 'reporting']
for i in range(51, 120):
    form_type = control_types[(i-51) % len(control_types)]
    FORMS.append((f"CPIC_{i:03d}_Control_Form_{i}", form_type))

# Add evaluate forms (120-134)
for i in range(120, 135):
    FORMS.append((f"CPIC_{i:03d}_Evaluate_Form_{i}", "evaluation"))

# Schema templates by type
SCHEMAS = {
    'strategy': ['record_id', 'submission_date', 'investment_id', 'objective', 'strategy_area', 'target_date', 'responsible_party', 'progress_pct', 'priority', 'status', 'approver', 'comments', 'created_by', 'created_at'],
    'business_analysis': ['record_id', 'submission_date', 'investment_id', 'requirement_id', 'requirement_desc', 'business_need', 'priority', 'source', 'status', 'analyst', 'review_date', 'comments', 'created_by', 'created_at'],
    'governance': ['record_id', 'submission_date', 'investment_id', 'decision_item', 'decision_type', 'decision_maker', 'decision_date', 'outcome', 'rationale', 'action_required', 'status', 'comments', 'created_by', 'created_at'],
    'investment': ['record_id', 'submission_date', 'investment_id', 'budget_amount', 'fiscal_year', 'category', 'justification', 'roi_estimate', 'payback_period', 'status', 'reviewer', 'approval_date', 'comments', 'created_by', 'created_at'],
    'resource': ['record_id', 'submission_date', 'investment_id', 'resource_type', 'resource_name', 'allocation_pct', 'start_date', 'end_date', 'cost', 'status', 'manager', 'comments', 'created_by', 'created_at'],
    'technical': ['record_id', 'submission_date', 'investment_id', 'component', 'technology', 'version', 'environment', 'impact_area', 'complexity', 'status', 'engineer', 'review_date', 'comments', 'created_by', 'created_at'],
    'financial': ['record_id', 'submission_date', 'investment_id', 'line_item', 'budget_amount', 'actual_amount', 'variance', 'fiscal_year', 'quarter', 'status', 'finance_reviewer', 'comments', 'created_by', 'created_at'],
    'risk': ['record_id', 'submission_date', 'investment_id', 'risk_title', 'risk_category', 'probability', 'impact', 'risk_score', 'mitigation_plan', 'owner', 'due_date', 'status', 'comments', 'created_by', 'created_at'],
    'security': ['record_id', 'submission_date', 'investment_id', 'control_id', 'control_name', 'implementation_status', 'assessment_date', 'findings', 'remediation', 'auditor', 'status', 'comments', 'created_by', 'created_at'],
    'acquisition': ['record_id', 'submission_date', 'investment_id', 'contract_id', 'vendor_name', 'contract_value', 'period_of_performance', 'deliverable', 'performance_rating', 'status', 'co_name', 'comments', 'created_by', 'created_at'],
    'performance': ['record_id', 'submission_date', 'investment_id', 'kpi_name', 'target_value', 'actual_value', 'variance_pct', 'measurement_period', 'trend', 'status', 'owner', 'comments', 'created_by', 'created_at'],
    'compliance': ['record_id', 'submission_date', 'investment_id', 'requirement', 'regulation', 'compliance_status', 'evidence', 'reviewer', 'review_date', 'findings', 'remediation_date', 'status', 'comments', 'created_by', 'created_at'],
    'training': ['record_id', 'submission_date', 'investment_id', 'training_name', 'training_type', 'target_audience', 'completion_date', 'participants', 'pass_rate', 'status', 'trainer', 'comments', 'created_by', 'created_at'],
    'project': ['record_id', 'submission_date', 'investment_id', 'task_name', 'milestone', 'planned_start', 'planned_end', 'actual_start', 'actual_end', 'progress_pct', 'status', 'pm', 'comments', 'created_by', 'created_at'],
    'reporting': ['record_id', 'submission_date', 'investment_id', 'report_period', 'overall_status', 'cost_status', 'schedule_status', 'key_accomplishments', 'issues', 'next_steps', 'submitted_by', 'comments', 'created_by', 'created_at'],
    'change': ['record_id', 'submission_date', 'investment_id', 'change_type', 'change_description', 'impact_assessment', 'cost_impact', 'schedule_impact', 'requestor', 'approval_status', 'approved_by', 'comments', 'created_by', 'created_at'],
    'quality': ['record_id', 'submission_date', 'investment_id', 'test_type', 'test_case_id', 'test_result', 'defects_found', 'defects_fixed', 'pass_rate', 'tester', 'status', 'comments', 'created_by', 'created_at'],
    'development': ['record_id', 'submission_date', 'investment_id', 'sprint_id', 'feature', 'story_points', 'velocity', 'code_quality', 'bugs_count', 'developer', 'status', 'comments', 'created_by', 'created_at'],
    'infrastructure': ['record_id', 'submission_date', 'investment_id', 'system_name', 'environment', 'capacity_used', 'availability', 'incident_count', 'change_count', 'admin', 'status', 'comments', 'created_by', 'created_at'],
    'operations': ['record_id', 'submission_date', 'investment_id', 'service_name', 'sla_target', 'sla_actual', 'incidents', 'mttr', 'availability_pct', 'operator', 'status', 'comments', 'created_by', 'created_at'],
    'evaluation': ['record_id', 'submission_date', 'investment_id', 'evaluation_type', 'criteria', 'score', 'findings', 'recommendations', 'lessons_learned', 'evaluator', 'status', 'comments', 'created_by', 'created_at']
}

def generate_sample_data(schema_type, num_records):
    """Generate sample data for a form table"""
    schema = SCHEMAS.get(schema_type, SCHEMAS['reporting'])
    data = []

    for i in range(num_records):
        record = {'record_id': f'REC-{i+1:04d}'}

        for field in schema[1:]:  # Skip record_id
            if field == 'submission_date' or field == 'created_at':
                record[field] = (base_date - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d %H:%M:%S')
            elif field == 'investment_id':
                record[field] = f'INV-{random.randint(1, 15):02d}'
            elif 'date' in field:
                record[field] = (base_date + timedelta(days=random.randint(-90, 90))).strftime('%Y-%m-%d')
            elif 'status' in field:
                record[field] = random.choice(['Approved', 'Pending', 'In Review', 'Completed', 'Draft'])
            elif 'amount' in field or 'cost' in field or 'value' in field or 'budget' in field:
                record[field] = str(round(random.uniform(10000, 5000000), 2))
            elif 'pct' in field or 'rate' in field:
                record[field] = str(round(random.uniform(0, 100), 1))
            elif 'score' in field or 'count' in field or 'points' in field:
                record[field] = str(random.randint(1, 100))
            elif field in ['created_by', 'owner', 'reviewer', 'manager', 'engineer', 'analyst', 'approver', 'auditor', 'trainer', 'pm', 'developer', 'admin', 'operator', 'evaluator', 'submitted_by', 'approved_by', 'requestor', 'tester', 'co_name', 'responsible_party', 'decision_maker', 'finance_reviewer']:
                record[field] = random.choice(names)
            elif field == 'priority':
                record[field] = random.choice(['High', 'Medium', 'Low', 'Critical'])
            elif field == 'probability' or field == 'impact':
                record[field] = random.choice(['Low', 'Medium', 'High', 'Very High'])
            elif field == 'fiscal_year':
                record[field] = str(random.choice([2024, 2025, 2026]))
            elif field == 'quarter':
                record[field] = f'Q{random.randint(1, 4)}'
            elif field == 'environment':
                record[field] = random.choice(['Production', 'Staging', 'Development', 'QA'])
            elif field == 'trend':
                record[field] = random.choice(['Up', 'Down', 'Stable'])
            elif field == 'compliance_status':
                record[field] = random.choice(['Compliant', 'Non-Compliant', 'Partial'])
            elif field == 'test_result':
                record[field] = random.choice(['Pass', 'Fail', 'Blocked', 'Skipped'])
            elif 'comment' in field or 'description' in field or 'findings' in field or 'recommendation' in field or 'rationale' in field or 'justification' in field or 'accomplishments' in field or 'issues' in field or 'steps' in field or 'lessons' in field or 'evidence' in field or 'need' in field or 'mitigation' in field or 'remediation' in field:
                record[field] = f'Sample {field.replace("_", " ")} text for record {i+1}'
            else:
                record[field] = f'{field.replace("_", " ").title()} {i+1}'

        data.append(record)

    return schema, data

def create_and_populate_table(table_name, schema_type):
    """Create a form table and populate with data"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Generate schema and data
    schema_fields, data = generate_sample_data(schema_type, random.randint(20, 60))

    # Create table with STRING schema (flexible)
    schema = [bigquery.SchemaField(name, "STRING") for name in schema_fields]

    try:
        # Delete if exists
        client.delete_table(table_id, not_found_ok=True)

        # Create table
        table = bigquery.Table(table_id, schema=schema)
        client.create_table(table)

        # Insert data
        errors = client.insert_rows_json(table_id, data)
        if errors:
            return 0, str(errors[0])[:50]
        return len(data), None

    except Exception as e:
        return 0, str(e)[:50]

def main():
    print("=" * 70)
    print("Creating 134 Individual Form Tables in BigQuery")
    print("Each table represents a CPIC form with transaction records")
    print("=" * 70)

    total_tables = 0
    total_records = 0
    errors = []

    for i, (table_name, schema_type) in enumerate(FORMS):
        count, error = create_and_populate_table(table_name, schema_type)
        if error:
            errors.append((table_name, error))
            print(f"  {i+1:3d}. {table_name[:50]:<50} ERROR: {error}")
        else:
            total_tables += 1
            total_records += count
            print(f"  {i+1:3d}. {table_name[:50]:<50} {count:3d} records")

    print("\n" + "=" * 70)
    print(f"SUMMARY:")
    print(f"  Tables created: {total_tables}")
    print(f"  Total records: {total_records}")
    print(f"  Errors: {len(errors)}")
    print("=" * 70)

if __name__ == "__main__":
    main()
