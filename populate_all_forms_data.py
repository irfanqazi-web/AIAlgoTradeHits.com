"""
Populate all CPIC forms with realistic data
Solution A: 134 forms
Solution B: 185 forms
"""

import json
import random
from google.cloud import bigquery
from datetime import datetime, timedelta

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'cpic_data'

client = bigquery.Client(project=PROJECT_ID)

# Realistic form owners by functional area
OWNERS = {
    'Investment Planning': ['Jim Keith', 'Miji Mathews', 'Eric Markow'],
    'Financial Analysis': ['Craig Drake', 'Joe Gibbons', 'Rangam Subramanian'],
    'Risk Management': ['Houman Rasouli', 'Shelia Walker', 'Anthony Gillespie'],
    'Governance': ['Kaschit Pandya', 'Courtney Williams', 'Melissa Kaminin'],
    'Reporting': ['Lou Capece', 'Shelderick Bailey', 'Babu V.'],
    'Cybersecurity': ['Houman Rasouli', 'Anthony Gillespie', 'Jaret Trail'],
    'Enterprise Architecture': ['Rob King', 'George Contos', 'Brian Wright'],
    'Project Management': ['John Bursie', 'Lillie Wilburn', 'James Vergauwen'],
    'Acquisition': ['Tanya Chiaravalle', 'Kafi Grigsby', 'Dave Potock'],
    'Quality': ['Mike Donaldson', 'Greg Ellis', 'Pavan Vemuri'],
    'Compliance': ['Eric R. Smith', 'Mohan Vasa', 'Larry Bullock'],
    'Operations': ['Lou Ferraro', 'Val Mance', 'Haren Punatar'],
    'Development': ['Erek Borowski', 'Shane Smith', 'Tony Antonious'],
    'Infrastructure': ['Lou Capece', 'Shelderick Bailey', 'Lou Ferraro'],
    'Training': ['Folashade Pullen', 'LaShawndra Bills', 'Ajeesh Cherian'],
    'Strategy': ['Courtney Williams', 'Melissa Kaminin', 'Gbemi Acholonu'],
    'Resource Management': ['Andrew Hanna', 'Tony Early', 'Dave Potock'],
    'Change Management': ['John Bursie', 'James Vergauwen', 'Lillie Wilburn'],
    'Privacy': ['Houman Rasouli', 'Shelia Walker', 'Anthony Gillespie'],
    'Data Management': ['Rob King', 'George Contos', 'Brian Wright'],
    'Performance': ['Miji Mathews', 'Craig Drake', 'Joe Gibbons'],
    'Evaluation': ['Courtney Williams', 'Kaschit Pandya', 'Melissa Kaminin'],
}

STATUSES = ['Draft', 'In Review', 'Pending', 'Approved', 'Active', 'Completed', 'Submitted']
RISK_LEVELS = ['Low', 'Medium', 'High']

def get_random_owner(functional_area):
    owners = OWNERS.get(functional_area, list(OWNERS.values())[0])
    return random.choice(owners)

def get_random_budget():
    # Return budget in millions with realistic distribution
    budgets = [0, 0.5, 1.0, 2.5, 5.0, 10.0, 15.0, 25.0, 50.0, 75.0, 100.0, 150.0, 200.0]
    weights = [30, 15, 15, 10, 8, 6, 5, 4, 3, 2, 1, 0.5, 0.5]
    return random.choices(budgets, weights=weights)[0]

def get_deadline():
    # Random deadline within next 90 days
    days_ahead = random.randint(7, 90)
    return (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')

def populate_solution_a_forms():
    """Populate all 134 forms for Solution A"""
    print("Loading Solution A data...")
    with open('solution_a_data.json', 'r') as f:
        data = json.load(f)

    # Clear existing forms
    print("Clearing existing forms...")
    client.query(f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.cpic_forms` WHERE 1=1").result()

    print(f"Inserting {len(data['forms'])} forms with realistic data...")

    for i, form in enumerate(data['forms']):
        func_area = form['functional_area']
        owner = get_random_owner(func_area)
        budget = get_random_budget()
        status = random.choice(STATUSES)
        risk = random.choice(RISK_LEVELS)
        deadline = get_deadline()

        # Create description based on form type
        desc = f"{form['form_name']} for {form['cpic_phase']} phase - {func_area} documentation. "
        desc += f"FY{form['fiscal_year']} submission managed by {owner}."

        query = f"""
            INSERT INTO `{PROJECT_ID}.{DATASET_ID}.cpic_forms`
            (form_id, form_name, form_code, functional_area, investment_id, fiscal_year,
             status, risk_level, cpic_phase, description, owner, budget_millions, submission_deadline)
            VALUES (@form_id, @form_name, @form_code, @func_area, @inv_id, @fy,
                    @status, @risk, @phase, @desc, @owner, @budget, @deadline)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("form_id", "STRING", form['form_id']),
                bigquery.ScalarQueryParameter("form_name", "STRING", form['form_name']),
                bigquery.ScalarQueryParameter("form_code", "STRING", form['form_code']),
                bigquery.ScalarQueryParameter("func_area", "STRING", func_area),
                bigquery.ScalarQueryParameter("inv_id", "STRING", form['investment_id']),
                bigquery.ScalarQueryParameter("fy", "INT64", int(form['fiscal_year'])),
                bigquery.ScalarQueryParameter("status", "STRING", status),
                bigquery.ScalarQueryParameter("risk", "STRING", risk),
                bigquery.ScalarQueryParameter("phase", "STRING", form['cpic_phase']),
                bigquery.ScalarQueryParameter("desc", "STRING", desc),
                bigquery.ScalarQueryParameter("owner", "STRING", owner),
                bigquery.ScalarQueryParameter("budget", "FLOAT64", budget),
                bigquery.ScalarQueryParameter("deadline", "STRING", deadline),
            ]
        )
        client.query(query, job_config=job_config).result()

        if (i + 1) % 20 == 0:
            print(f"  Inserted {i + 1}/{len(data['forms'])} forms...")

    print(f"Solution A: Inserted {len(data['forms'])} forms")
    return len(data['forms'])

def populate_solution_b_forms():
    """Generate and populate 185 forms for Solution B"""
    print("\nGenerating Solution B forms (185 total)...")

    # Solution B has 15 investments (5 MAJOR + 5 SIGNIFICANT + 5 INFRASTRUCTURE)
    investments_b = {
        'MAJOR': ['MAJ-01', 'MAJ-02', 'MAJ-03', 'MAJ-04', 'MAJ-05'],
        'SIGNIFICANT': ['SIG-01', 'SIG-02', 'SIG-03', 'SIG-04', 'SIG-05'],
        'INFRASTRUCTURE': ['INF-01', 'INF-02', 'INF-03', 'INF-04', 'INF-05']
    }

    # Form templates by category
    major_forms = [
        ("OMB Exhibit 300 Business Case", "MAJ-300", "Investment Planning", "Annual"),
        ("Monthly Status Report", "MAJ-STS", "Reporting", "Monthly"),
        ("Earned Value Management Report", "MAJ-EVM", "Financial Analysis", "Monthly"),
        ("Risk Assessment & Mitigation", "MAJ-RSK", "Risk Management", "Quarterly"),
        ("Baseline Change Request", "MAJ-BCR", "Change Management", "As Needed"),
        ("Quality Gate Certification", "MAJ-QAG", "Quality", "Per Milestone"),
        ("Security Compliance Report", "MAJ-SEC", "Cybersecurity", "Quarterly"),
        ("Vendor Performance Report", "MAJ-VND", "Acquisition", "Quarterly"),
        ("Post-Implementation Review", "MAJ-PIR", "Evaluation", "Per Release"),
        ("CIO Rating Self-Assessment", "MAJ-CIO", "Governance", "Monthly"),
        ("TechStat Preparation Package", "MAJ-TST", "Governance", "As Needed"),
        ("GAO Audit Support Package", "MAJ-GAO", "Compliance", "As Needed"),
        ("Budget Execution Report", "MAJ-BUD", "Financial Analysis", "Monthly"),
    ]

    significant_forms = [
        ("Exhibit 53 IT Investment", "SIG-E53", "Investment Planning", "Annual"),
        ("Project Status Report", "SIG-STS", "Reporting", "Monthly"),
        ("Cost Performance Report", "SIG-CPR", "Financial Analysis", "Monthly"),
        ("Risk Register Update", "SIG-RSK", "Risk Management", "Monthly"),
        ("Scope Change Request", "SIG-SCR", "Change Management", "As Needed"),
        ("Testing Status Report", "SIG-TST", "Quality", "Weekly"),
        ("Security Assessment", "SIG-SEC", "Cybersecurity", "Quarterly"),
        ("Contract Performance", "SIG-CNT", "Acquisition", "Monthly"),
        ("Benefits Tracking", "SIG-BEN", "Evaluation", "Quarterly"),
        ("Manager Review Package", "SIG-MGR", "Governance", "Monthly"),
        ("Compliance Checklist", "SIG-CMP", "Compliance", "Quarterly"),
        ("Resource Allocation", "SIG-RES", "Resource Management", "Monthly"),
    ]

    infrastructure_forms = [
        ("Technical Budget Request", "INF-BUD", "Financial Analysis", "Annual"),
        ("Capacity Report", "INF-CAP", "Infrastructure", "Monthly"),
        ("Performance Metrics", "INF-PER", "Operations", "Weekly"),
        ("Security Posture Report", "INF-SEC", "Cybersecurity", "Monthly"),
        ("Change Advisory Board", "INF-CAB", "Change Management", "Weekly"),
        ("Incident Report", "INF-INC", "Operations", "As Needed"),
        ("Disaster Recovery Test", "INF-DRT", "Operations", "Quarterly"),
        ("Vendor SLA Report", "INF-SLA", "Acquisition", "Monthly"),
        ("Configuration Status", "INF-CFG", "Infrastructure", "Monthly"),
        ("Availability Report", "INF-AVL", "Operations", "Daily"),
        ("Network Status", "INF-NET", "Infrastructure", "Weekly"),
        ("Storage Utilization", "INF-STG", "Infrastructure", "Monthly"),
    ]

    forms_b = []
    form_counter = 1

    # Generate MAJOR forms (5 investments x 13 forms = 65)
    for inv_id in investments_b['MAJOR']:
        for form_template in major_forms:
            form_name, code_prefix, func_area, frequency = form_template
            forms_b.append({
                'form_id': f'CPIC-B{form_counter:03d}',
                'form_name': form_name,
                'form_code': f'{code_prefix}-{inv_id[-2:]}',
                'functional_area': func_area,
                'category': 'MAJOR',
                'investment_id': inv_id,
                'fiscal_year': 2025,
                'frequency': frequency,
                'cpic_phase': 'Control',
                'exhibit_300_required': True,
                'cio_rating_applicable': True
            })
            form_counter += 1

    # Generate SIGNIFICANT forms (5 investments x 12 forms = 60)
    for inv_id in investments_b['SIGNIFICANT']:
        for form_template in significant_forms:
            form_name, code_prefix, func_area, frequency = form_template
            forms_b.append({
                'form_id': f'CPIC-B{form_counter:03d}',
                'form_name': form_name,
                'form_code': f'{code_prefix}-{inv_id[-2:]}',
                'functional_area': func_area,
                'category': 'SIGNIFICANT',
                'investment_id': inv_id,
                'fiscal_year': 2025,
                'frequency': frequency,
                'cpic_phase': 'Control',
                'exhibit_53_required': True
            })
            form_counter += 1

    # Generate INFRASTRUCTURE forms (5 investments x 12 forms = 60)
    for inv_id in investments_b['INFRASTRUCTURE']:
        for form_template in infrastructure_forms:
            form_name, code_prefix, func_area, frequency = form_template
            forms_b.append({
                'form_id': f'CPIC-B{form_counter:03d}',
                'form_name': form_name,
                'form_code': f'{code_prefix}-{inv_id[-2:]}',
                'functional_area': func_area,
                'category': 'INFRASTRUCTURE',
                'investment_id': inv_id,
                'fiscal_year': 2025,
                'frequency': frequency,
                'cpic_phase': 'Control'
            })
            form_counter += 1

    print(f"Generated {len(forms_b)} forms for Solution B")

    # Save Solution B forms to JSON
    with open('solution_b_forms_complete.json', 'w') as f:
        json.dump({'forms': forms_b}, f, indent=2)

    # Insert into BigQuery (separate table for Solution B or update main forms table)
    print(f"Inserting {len(forms_b)} Solution B forms...")

    for i, form in enumerate(forms_b):
        func_area = form['functional_area']
        owner = get_random_owner(func_area)
        budget = get_random_budget()
        status = random.choice(STATUSES)
        risk = random.choice(RISK_LEVELS)
        deadline = get_deadline()

        desc = f"{form['form_name']} for {form['category']} investment {form['investment_id']}. "
        desc += f"{form['frequency']} submission - {func_area}. Managed by {owner}."

        query = f"""
            INSERT INTO `{PROJECT_ID}.{DATASET_ID}.cpic_forms`
            (form_id, form_name, form_code, functional_area, category, investment_id, fiscal_year,
             status, risk_level, cpic_phase, description, owner, budget_millions, submission_deadline,
             frequency, exhibit_300_required, exhibit_53_required, cio_rating_applicable)
            VALUES (@form_id, @form_name, @form_code, @func_area, @category, @inv_id, @fy,
                    @status, @risk, @phase, @desc, @owner, @budget, @deadline,
                    @frequency, @ex300, @ex53, @cio)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("form_id", "STRING", form['form_id']),
                bigquery.ScalarQueryParameter("form_name", "STRING", form['form_name']),
                bigquery.ScalarQueryParameter("form_code", "STRING", form['form_code']),
                bigquery.ScalarQueryParameter("func_area", "STRING", func_area),
                bigquery.ScalarQueryParameter("category", "STRING", form.get('category', '')),
                bigquery.ScalarQueryParameter("inv_id", "STRING", form['investment_id']),
                bigquery.ScalarQueryParameter("fy", "INT64", int(form['fiscal_year'])),
                bigquery.ScalarQueryParameter("status", "STRING", status),
                bigquery.ScalarQueryParameter("risk", "STRING", risk),
                bigquery.ScalarQueryParameter("phase", "STRING", form['cpic_phase']),
                bigquery.ScalarQueryParameter("desc", "STRING", desc),
                bigquery.ScalarQueryParameter("owner", "STRING", owner),
                bigquery.ScalarQueryParameter("budget", "FLOAT64", budget),
                bigquery.ScalarQueryParameter("deadline", "STRING", deadline),
                bigquery.ScalarQueryParameter("frequency", "STRING", form.get('frequency', '')),
                bigquery.ScalarQueryParameter("ex300", "BOOL", form.get('exhibit_300_required', False)),
                bigquery.ScalarQueryParameter("ex53", "BOOL", form.get('exhibit_53_required', False)),
                bigquery.ScalarQueryParameter("cio", "BOOL", form.get('cio_rating_applicable', False)),
            ]
        )
        client.query(query, job_config=job_config).result()

        if (i + 1) % 20 == 0:
            print(f"  Inserted {i + 1}/{len(forms_b)} forms...")

    print(f"Solution B: Inserted {len(forms_b)} forms")
    return len(forms_b)

def verify_data():
    """Verify the data in BigQuery"""
    print("\n=== Verifying BigQuery Data ===")

    # Count forms
    result = client.query(f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.cpic_forms`").result()
    total_forms = list(result)[0].cnt
    print(f"Total forms in BigQuery: {total_forms}")

    # Count by phase
    result = client.query(f"""
        SELECT cpic_phase, COUNT(*) as cnt
        FROM `{PROJECT_ID}.{DATASET_ID}.cpic_forms`
        GROUP BY cpic_phase
    """).result()
    print("\nForms by Phase:")
    for row in result:
        print(f"  {row.cpic_phase}: {row.cnt}")

    # Count by category (Solution B)
    result = client.query(f"""
        SELECT category, COUNT(*) as cnt
        FROM `{PROJECT_ID}.{DATASET_ID}.cpic_forms`
        WHERE category IS NOT NULL AND category != ''
        GROUP BY category
    """).result()
    print("\nForms by Category (Solution B):")
    for row in result:
        print(f"  {row.category}: {row.cnt}")

    # Count by status
    result = client.query(f"""
        SELECT status, COUNT(*) as cnt
        FROM `{PROJECT_ID}.{DATASET_ID}.cpic_forms`
        GROUP BY status
        ORDER BY cnt DESC
    """).result()
    print("\nForms by Status:")
    for row in result:
        print(f"  {row.status}: {row.cnt}")

if __name__ == "__main__":
    print("=" * 60)
    print("CPIC Forms Data Population")
    print("=" * 60)

    # Populate Solution A forms
    count_a = populate_solution_a_forms()

    # Populate Solution B forms
    count_b = populate_solution_b_forms()

    # Verify
    verify_data()

    print("\n" + "=" * 60)
    print(f"COMPLETE: {count_a + count_b} total forms populated")
    print("=" * 60)
    print("\nTo view all forms:")
    print("Solution A: https://irs-cpic-solution-a-252370699783.us-central1.run.app")
    print("Solution B: https://irs-cpic-solution-b-252370699783.us-central1.run.app")
    print("\nNavigate to: CPIC Forms > View All Forms")
    print("Or use API: /api/cpic-forms")
