"""
Setup BigQuery tables for IRS CPIC Management System
Creates all necessary tables and populates with demo data
"""

import json
from google.cloud import bigquery
from datetime import datetime
import hashlib

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'cpic_data'

client = bigquery.Client(project=PROJECT_ID)

def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Create dataset if not exists
def create_dataset():
    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {dataset_ref} already exists")
    except:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"Created dataset {dataset_ref}")

# Create tables
def create_tables():
    tables = {
        'users': """
            CREATE TABLE IF NOT EXISTS `{project}.{dataset}.users` (
                user_id STRING NOT NULL,
                email STRING NOT NULL,
                password_hash STRING NOT NULL,
                name STRING,
                organization STRING,
                role STRING,
                title STRING,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                last_login TIMESTAMP,
                is_active BOOL DEFAULT TRUE
            )
        """,
        'investments': """
            CREATE TABLE IF NOT EXISTS `{project}.{dataset}.investments` (
                investment_id STRING NOT NULL,
                uii STRING,
                name STRING NOT NULL,
                short_name STRING,
                description STRING,
                category STRING,
                investment_type STRING,
                lifecycle_stage STRING,
                appropriation STRING,
                cd_owner STRING,
                cd_title STRING,
                owner STRING,
                portfolio_manager STRING,
                investment_coordinator STRING,
                status STRING DEFAULT 'active',
                approval_status STRING DEFAULT 'approved',
                health STRING DEFAULT 'green',
                budget_fy25 FLOAT64,
                actual_spend_ytd FLOAT64,
                cost_variance FLOAT64,
                schedule_days INT64,
                sub_projects INT64,
                cio_rating INT64,
                exhibit_300 BOOL,
                exhibit_53 BOOL,
                techstat_eligible BOOL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                updated_at TIMESTAMP,
                approved_by STRING,
                approved_at TIMESTAMP
            )
        """,
        'cpic_forms': """
            CREATE TABLE IF NOT EXISTS `{project}.{dataset}.cpic_forms` (
                form_id STRING NOT NULL,
                form_name STRING NOT NULL,
                form_code STRING,
                functional_area STRING,
                category STRING,
                description STRING,
                investment_id STRING,
                fiscal_year INT64,
                budget_millions FLOAT64,
                status STRING,
                risk_level STRING,
                owner STRING,
                cpic_phase STRING,
                frequency STRING,
                cio_rating_applicable BOOL,
                exhibit_300_required BOOL,
                exhibit_53_required BOOL,
                submission_deadline DATE,
                last_updated TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
            )
        """,
        'workflows': """
            CREATE TABLE IF NOT EXISTS `{project}.{dataset}.workflows` (
                workflow_id STRING NOT NULL,
                name STRING NOT NULL,
                phase STRING,
                duration STRING,
                description STRING,
                steps STRING,
                forms_required STRING,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
            )
        """,
        'projects': """
            CREATE TABLE IF NOT EXISTS `{project}.{dataset}.projects` (
                project_id STRING NOT NULL,
                name STRING NOT NULL,
                description STRING,
                investment_id STRING,
                status STRING,
                health STRING,
                start_date DATE,
                end_date DATE,
                budget FLOAT64,
                actual_spend FLOAT64,
                owner STRING,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
            )
        """,
        'risks': """
            CREATE TABLE IF NOT EXISTS `{project}.{dataset}.risks` (
                risk_id STRING NOT NULL,
                title STRING NOT NULL,
                description STRING,
                investment_id STRING,
                project_id STRING,
                category STRING,
                probability STRING,
                impact STRING,
                status STRING,
                mitigation STRING,
                owner STRING,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
            )
        """,
        'monthly_reports': """
            CREATE TABLE IF NOT EXISTS `{project}.{dataset}.monthly_reports` (
                report_id STRING NOT NULL,
                investment_id STRING,
                report_month STRING,
                fiscal_year INT64,
                status STRING,
                cost_variance FLOAT64,
                schedule_variance FLOAT64,
                cio_comments STRING,
                submitted_by STRING,
                submitted_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
            )
        """
    }

    for table_name, ddl in tables.items():
        query = ddl.format(project=PROJECT_ID, dataset=DATASET_ID)
        try:
            client.query(query).result()
            print(f"Created/verified table: {table_name}")
        except Exception as e:
            print(f"Error creating {table_name}: {e}")

# Insert demo users
def insert_users():
    users = [
        ("demo-002", "saleem@irs.gov", get_password_hash("cpic2025"), "M. Saleem Ahmad", "IRS", "admin", "System Administrator"),
        ("demo-003", "kaschit.pandya@irs.gov", get_password_hash("cpic2025"), "Kaschit Pandya", "IRS", "cio", "Chief Information Officer"),
        ("demo-004", "admin@irs.gov", get_password_hash("cpic2025"), "System Admin", "IRS", "admin", "Administrator"),
        ("cd-001", "jim.keith@irs.gov", get_password_hash("cpic2025"), "Jim Keith", "IRS", "coordinating_director", "CD - Taxpayer Services"),
        ("cd-002", "miji.mathews@irs.gov", get_password_hash("cpic2025"), "Miji Mathews", "IRS", "coordinating_director", "CD - Tax Processing"),
        ("cd-003", "eric.markow@irs.gov", get_password_hash("cpic2025"), "Eric Markow", "IRS", "coordinating_director", "CD - Compliance"),
        ("cd-004", "lou.capece@irs.gov", get_password_hash("cpic2025"), "Lou Capece", "IRS", "coordinating_director", "CD - Infrastructure"),
        ("cd-005", "houman.rasouli@irs.gov", get_password_hash("cpic2025"), "Houman Rasouli", "IRS", "coordinating_director", "CD - Cybersecurity"),
        ("pm-001", "john.bursie@irs.gov", get_password_hash("cpic2025"), "John Bursie", "IRS", "product_manager", "Product Manager"),
        ("re-001", "mike.donaldson@irs.gov", get_password_hash("cpic2025"), "Mike Donaldson", "IRS", "responsible_engineer", "Responsible Engineer"),
    ]

    # Clear existing users
    client.query(f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.users` WHERE 1=1").result()

    for user in users:
        query = f"""
            INSERT INTO `{PROJECT_ID}.{DATASET_ID}.users`
            (user_id, email, password_hash, name, organization, role, title, is_active)
            VALUES (@user_id, @email, @password_hash, @name, @org, @role, @title, TRUE)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user[0]),
                bigquery.ScalarQueryParameter("email", "STRING", user[1]),
                bigquery.ScalarQueryParameter("password_hash", "STRING", user[2]),
                bigquery.ScalarQueryParameter("name", "STRING", user[3]),
                bigquery.ScalarQueryParameter("org", "STRING", user[4]),
                bigquery.ScalarQueryParameter("role", "STRING", user[5]),
                bigquery.ScalarQueryParameter("title", "STRING", user[6]),
            ]
        )
        client.query(query, job_config=job_config).result()
    print(f"Inserted {len(users)} users")

# Insert investments from Solution A data
def insert_investments():
    with open('solution_a_data.json', 'r') as f:
        data = json.load(f)

    # Clear existing
    client.query(f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.investments` WHERE 1=1").result()

    for inv in data['investments']:
        query = f"""
            INSERT INTO `{PROJECT_ID}.{DATASET_ID}.investments`
            (investment_id, uii, name, short_name, description, category, investment_type,
             cd_owner, budget_fy25, health, cost_variance, schedule_days, status, approval_status)
            VALUES (@inv_id, @uii, @name, @short_name, @desc, @category, @inv_type,
                    @cd_owner, @budget, @health, @cost_var, @sched_days, 'active', 'approved')
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("inv_id", "STRING", inv['investment_id']),
                bigquery.ScalarQueryParameter("uii", "STRING", inv['uii']),
                bigquery.ScalarQueryParameter("name", "STRING", inv['name']),
                bigquery.ScalarQueryParameter("short_name", "STRING", inv['short_name']),
                bigquery.ScalarQueryParameter("desc", "STRING", inv['description']),
                bigquery.ScalarQueryParameter("category", "STRING", inv['category']),
                bigquery.ScalarQueryParameter("inv_type", "STRING", inv['investment_type']),
                bigquery.ScalarQueryParameter("cd_owner", "STRING", inv['cd_owner']),
                bigquery.ScalarQueryParameter("budget", "FLOAT64", float(inv['budget_fy25'])),
                bigquery.ScalarQueryParameter("health", "STRING", inv.get('health', 'green')),
                bigquery.ScalarQueryParameter("cost_var", "FLOAT64", float(inv.get('cost_variance', 0))),
                bigquery.ScalarQueryParameter("sched_days", "INT64", int(inv.get('schedule_days', 0))),
            ]
        )
        client.query(query, job_config=job_config).result()
    print(f"Inserted {len(data['investments'])} investments")

# Insert forms from Solution A data
def insert_forms():
    with open('solution_a_data.json', 'r') as f:
        data = json.load(f)

    # Clear existing
    client.query(f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.cpic_forms` WHERE 1=1").result()

    for form in data['forms']:
        query = f"""
            INSERT INTO `{PROJECT_ID}.{DATASET_ID}.cpic_forms`
            (form_id, form_name, form_code, functional_area, investment_id, fiscal_year,
             status, risk_level, cpic_phase, description)
            VALUES (@form_id, @form_name, @form_code, @func_area, @inv_id, @fy,
                    @status, @risk, @phase, @desc)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("form_id", "STRING", form['form_id']),
                bigquery.ScalarQueryParameter("form_name", "STRING", form['form_name']),
                bigquery.ScalarQueryParameter("form_code", "STRING", form['form_code']),
                bigquery.ScalarQueryParameter("func_area", "STRING", form['functional_area']),
                bigquery.ScalarQueryParameter("inv_id", "STRING", form['investment_id']),
                bigquery.ScalarQueryParameter("fy", "INT64", int(form['fiscal_year'])),
                bigquery.ScalarQueryParameter("status", "STRING", form['status']),
                bigquery.ScalarQueryParameter("risk", "STRING", form['risk_level']),
                bigquery.ScalarQueryParameter("phase", "STRING", form['cpic_phase']),
                bigquery.ScalarQueryParameter("desc", "STRING", f"{form['form_name']} - {form['functional_area']}"),
            ]
        )
        client.query(query, job_config=job_config).result()
    print(f"Inserted {len(data['forms'])} forms")

# Insert workflows
def insert_workflows():
    with open('solution_a_data.json', 'r') as f:
        data = json.load(f)

    # Clear existing
    client.query(f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.workflows` WHERE 1=1").result()

    for wf in data['workflows']:
        query = f"""
            INSERT INTO `{PROJECT_ID}.{DATASET_ID}.workflows`
            (workflow_id, name, phase, duration, description, steps)
            VALUES (@wf_id, @name, @phase, @duration, @desc, @steps)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("wf_id", "STRING", wf['id']),
                bigquery.ScalarQueryParameter("name", "STRING", wf['name']),
                bigquery.ScalarQueryParameter("phase", "STRING", wf['phase']),
                bigquery.ScalarQueryParameter("duration", "STRING", wf.get('duration', '')),
                bigquery.ScalarQueryParameter("desc", "STRING", wf.get('solution_a', '')),
                bigquery.ScalarQueryParameter("steps", "STRING", json.dumps(wf['steps'])),
            ]
        )
        client.query(query, job_config=job_config).result()
    print(f"Inserted {len(data['workflows'])} workflows")

if __name__ == "__main__":
    print("Setting up CPIC BigQuery tables...")
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print()

    create_dataset()
    create_tables()
    insert_users()
    insert_investments()
    insert_forms()
    insert_workflows()

    print()
    print("=== BigQuery Setup Complete ===")
    print(f"Tables created in {PROJECT_ID}.{DATASET_ID}")
