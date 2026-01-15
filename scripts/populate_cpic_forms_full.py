"""
Populate cpic_forms table with all 134 forms
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

base_date = datetime.now()

# All 134 CPIC Forms (same as in main.py)
FORMS = [
    # PRESELECT FORMS (15)
    {"form_id": "CPIC-001", "form_name": "Strategic Planning Document", "form_code": "SPD-001", "functional_area": "Strategy", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-002", "form_name": "Needs Identification Report", "form_code": "NIR-001", "functional_area": "Business Analysis", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-003", "form_name": "Initial Screening Criteria", "form_code": "ISC-001", "functional_area": "Governance", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-004", "form_name": "Preliminary Business Case", "form_code": "PBC-001", "functional_area": "Investment Planning", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-005", "form_name": "Portfolio Prioritization Request", "form_code": "PPR-001", "functional_area": "Strategy", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-006", "form_name": "Mission Alignment Assessment", "form_code": "MAA-001", "functional_area": "Strategy", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-007", "form_name": "Resource Availability Check", "form_code": "RAC-001", "functional_area": "Resource Management", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-008", "form_name": "Technical Feasibility Study", "form_code": "TFS-001", "functional_area": "Enterprise Architecture", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-009", "form_name": "Budget Authority Request", "form_code": "BAR-001", "functional_area": "Financial Analysis", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-010", "form_name": "Stakeholder Identification", "form_code": "SID-001", "functional_area": "Strategy", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-011", "form_name": "Initial Risk Screening", "form_code": "IRS-001", "functional_area": "Risk Management", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-012", "form_name": "Capability Gap Assessment", "form_code": "CGA-001", "functional_area": "Enterprise Architecture", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-013", "form_name": "Investment Proposal Draft", "form_code": "IPD-001", "functional_area": "Investment Planning", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-014", "form_name": "CIO Endorsement Request", "form_code": "CER-001", "functional_area": "Governance", "cpic_phase": "Preselect"},
    {"form_id": "CPIC-015", "form_name": "IRB Submission Package", "form_code": "ISP-001", "functional_area": "Governance", "cpic_phase": "Preselect"},
    # SELECT FORMS (24)
    {"form_id": "CPIC-016", "form_name": "OMB Exhibit 300 Business Case", "form_code": "BC-300-001", "functional_area": "Investment Planning", "cpic_phase": "Select"},
    {"form_id": "CPIC-017", "form_name": "Investment Screening Criteria", "form_code": "ISC-002", "functional_area": "Investment Planning", "cpic_phase": "Select"},
    {"form_id": "CPIC-018", "form_name": "Alternatives Analysis", "form_code": "AA-001", "functional_area": "Investment Planning", "cpic_phase": "Select"},
    {"form_id": "CPIC-019", "form_name": "Cost-Benefit Analysis", "form_code": "CBA-001", "functional_area": "Financial Analysis", "cpic_phase": "Select"},
    {"form_id": "CPIC-020", "form_name": "Risk Assessment Detailed", "form_code": "RAD-001", "functional_area": "Risk Management", "cpic_phase": "Select"},
    {"form_id": "CPIC-021", "form_name": "Strategic Alignment Assessment", "form_code": "SAA-001", "functional_area": "Strategy", "cpic_phase": "Select"},
    {"form_id": "CPIC-022", "form_name": "Architecture Review Request", "form_code": "ARR-001", "functional_area": "Enterprise Architecture", "cpic_phase": "Select"},
    {"form_id": "CPIC-023", "form_name": "Security Requirements Document", "form_code": "SRD-001", "functional_area": "Cybersecurity", "cpic_phase": "Select"},
    {"form_id": "CPIC-024", "form_name": "Investment Proposal Final", "form_code": "IPF-001", "functional_area": "Investment Planning", "cpic_phase": "Select"},
    {"form_id": "CPIC-025", "form_name": "Stakeholder Analysis Complete", "form_code": "SAC-001", "functional_area": "Strategy", "cpic_phase": "Select"},
    {"form_id": "CPIC-026", "form_name": "Capability Gap Analysis Final", "form_code": "CGAF-001", "functional_area": "Enterprise Architecture", "cpic_phase": "Select"},
    {"form_id": "CPIC-027", "form_name": "Resource Requirements Plan", "form_code": "RRP-001", "functional_area": "Resource Management", "cpic_phase": "Select"},
    {"form_id": "CPIC-028", "form_name": "Procurement Strategy", "form_code": "PS-001", "functional_area": "Acquisition", "cpic_phase": "Select"},
    {"form_id": "CPIC-029", "form_name": "Performance Measures Plan", "form_code": "PMP-001", "functional_area": "Performance", "cpic_phase": "Select"},
    {"form_id": "CPIC-030", "form_name": "IRB Review Package", "form_code": "IRP-001", "functional_area": "Governance", "cpic_phase": "Select"},
    {"form_id": "CPIC-031", "form_name": "EA Compliance Certification", "form_code": "EAC-001", "functional_area": "Enterprise Architecture", "cpic_phase": "Select"},
    {"form_id": "CPIC-032", "form_name": "Privacy Impact Assessment Initial", "form_code": "PIA-I-001", "functional_area": "Privacy", "cpic_phase": "Select"},
    {"form_id": "CPIC-033", "form_name": "Section 508 Assessment", "form_code": "S508-001", "functional_area": "Compliance", "cpic_phase": "Select"},
    {"form_id": "CPIC-034", "form_name": "Budget Formulation Package", "form_code": "BFP-001", "functional_area": "Financial Analysis", "cpic_phase": "Select"},
    {"form_id": "CPIC-035", "form_name": "Governance Structure Plan", "form_code": "GSP-001", "functional_area": "Governance", "cpic_phase": "Select"},
    {"form_id": "CPIC-036", "form_name": "Communication Plan", "form_code": "CP-001", "functional_area": "Strategy", "cpic_phase": "Select"},
    {"form_id": "CPIC-037", "form_name": "Training Needs Assessment", "form_code": "TNA-001", "functional_area": "Training", "cpic_phase": "Select"},
    {"form_id": "CPIC-038", "form_name": "Transition Planning Document", "form_code": "TPD-001", "functional_area": "Project Management", "cpic_phase": "Select"},
    {"form_id": "CPIC-039", "form_name": "CIO Approval Package", "form_code": "CAP-001", "functional_area": "Governance", "cpic_phase": "Select"},
    # CONTROL FORMS (80)
    {"form_id": "CPIC-040", "form_name": "Monthly Status Report", "form_code": "MSR-001", "functional_area": "Reporting", "cpic_phase": "Control"},
    {"form_id": "CPIC-041", "form_name": "Baseline Change Request", "form_code": "BCR-001", "functional_area": "Change Management", "cpic_phase": "Control"},
    {"form_id": "CPIC-042", "form_name": "Earned Value Management Report", "form_code": "EVM-001", "functional_area": "Financial Analysis", "cpic_phase": "Control"},
    {"form_id": "CPIC-043", "form_name": "Risk Register Update", "form_code": "RRU-001", "functional_area": "Risk Management", "cpic_phase": "Control"},
    {"form_id": "CPIC-044", "form_name": "TechStat Review Preparation", "form_code": "TSP-001", "functional_area": "Governance", "cpic_phase": "Control"},
    {"form_id": "CPIC-045", "form_name": "Contractor Performance Report", "form_code": "CPR-001", "functional_area": "Acquisition", "cpic_phase": "Control"},
    {"form_id": "CPIC-046", "form_name": "Quality Assurance Report", "form_code": "QAR-001", "functional_area": "Quality", "cpic_phase": "Control"},
    {"form_id": "CPIC-047", "form_name": "Security Assessment Report", "form_code": "SAR-001", "functional_area": "Cybersecurity", "cpic_phase": "Control"},
    {"form_id": "CPIC-048", "form_name": "Project Schedule Update", "form_code": "PSU-001", "functional_area": "Project Management", "cpic_phase": "Control"},
    {"form_id": "CPIC-049", "form_name": "Budget Execution Report", "form_code": "BER-001", "functional_area": "Financial Analysis", "cpic_phase": "Control"},
    {"form_id": "CPIC-050", "form_name": "Release Management Plan", "form_code": "RMP-001", "functional_area": "Development", "cpic_phase": "Control"},
]

# Generate remaining forms for Control phase (51-119)
for i in range(51, 120):
    areas = ['Development', 'Infrastructure', 'Quality', 'Operations', 'Cybersecurity', 'Compliance', 'Performance', 'Enterprise Architecture', 'Data Management', 'Training']
    form_types = ['Report', 'Assessment', 'Review', 'Update', 'Status', 'Dashboard', 'Analysis', 'Checklist']
    FORMS.append({
        "form_id": f"CPIC-{i:03d}",
        "form_name": f"{random.choice(form_types)} - {random.choice(areas)}",
        "form_code": f"CTL-{i:03d}",
        "functional_area": random.choice(areas),
        "cpic_phase": "Control"
    })

# EVALUATE FORMS (15)
for i in range(120, 135):
    areas = ['Evaluation', 'Performance', 'Financial Analysis', 'Strategy', 'Operations']
    form_types = ['Post-Implementation Review', 'Benefits Realization', 'Lessons Learned', 'Technology Assessment', 'Investment Closeout']
    FORMS.append({
        "form_id": f"CPIC-{i:03d}",
        "form_name": f"{form_types[(i-120) % len(form_types)]} {i-119}",
        "form_code": f"EVL-{i-119:03d}",
        "functional_area": random.choice(areas),
        "cpic_phase": "Evaluate"
    })

names = ['John Smith', 'Maria Garcia', 'James Wilson', 'Sarah Chen', 'Michael Brown', 'Emily Davis']

def main():
    print("=" * 70)
    print("Populating cpic_forms with ALL 134 forms")
    print("=" * 70)

    table_id = f"{PROJECT_ID}.{DATASET_ID}.cpic_forms"

    # Clear existing data
    print("Clearing existing forms...")
    query = f"DELETE FROM `{table_id}` WHERE TRUE"
    try:
        client.query(query).result()
    except:
        pass

    # Prepare all 134 forms
    rows = []
    for i, form in enumerate(FORMS):
        rows.append({
            'form_id': form['form_id'],
            'form_name': form['form_name'],
            'form_code': form['form_code'],
            'functional_area': form['functional_area'],
            'description': f"{form['form_name']} - {form['functional_area']} documentation",
            'investment_id': f"INV-{(i % 15) + 1:02d}",
            'fiscal_year': 2025,
            'status': random.choice(['Active', 'Draft', 'In Review', 'Approved', 'Completed']),
            'risk_level': random.choice(['Low', 'Medium', 'High']),
            'owner': random.choice(names),
            'cpic_phase': form['cpic_phase'],
            'created_at': (base_date - timedelta(days=random.randint(10, 180))).strftime('%Y-%m-%d %H:%M:%S')
        })

    # Insert in batches
    batch_size = 50
    total_inserted = 0

    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]

        # Build VALUES
        values = []
        for row in batch:
            vals = []
            for v in row.values():
                if isinstance(v, int):
                    vals.append(str(v))
                else:
                    escaped = str(v).replace("'", "\\'")
                    vals.append(f"'{escaped}'")
            values.append(f"({', '.join(vals)})")

        cols = ', '.join(rows[0].keys())
        query = f"INSERT INTO `{table_id}` ({cols}) VALUES {', '.join(values)}"

        try:
            client.query(query).result()
            total_inserted += len(batch)
            print(f"  Inserted batch {i//batch_size + 1}: {len(batch)} forms")
        except Exception as e:
            print(f"  Error: {str(e)[:100]}")

    # Count final
    query = f"SELECT COUNT(*) as cnt FROM `{table_id}`"
    result = client.query(query).result()
    for row in result:
        print(f"\nTotal forms in cpic_forms table: {row.cnt}")

    # Also fix techstat_reviews
    print("\n" + "-" * 50)
    print("Adding records to techstat_reviews...")

    ts_table = f"{PROJECT_ID}.{DATASET_ID}.techstat_reviews"

    for i in range(16, 31):
        query = f"""
        INSERT INTO `{ts_table}` (review_id, investment_id, review_date, review_type, findings, action_items, status, next_review, reviewer)
        VALUES ('TSR-{i:03d}', 'INV-{(i % 15) + 1:02d}', '{(base_date - timedelta(days=random.randint(10, 90))).strftime('%Y-%m-%d')}',
                '{random.choice(['Quarterly', 'Monthly', 'Ad-hoc'])}', 'Findings for review {i}', '{random.randint(0, 5)}',
                '{random.choice(['Closed', 'Open', 'In Progress'])}', '{(base_date + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d')}',
                '{random.choice(names)}')
        """
        try:
            client.query(query).result()
        except Exception as e:
            pass

    query = f"SELECT COUNT(*) as cnt FROM `{ts_table}`"
    result = client.query(query).result()
    for row in result:
        print(f"Total techstat_reviews: {row.cnt}")

    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)

if __name__ == "__main__":
    main()
