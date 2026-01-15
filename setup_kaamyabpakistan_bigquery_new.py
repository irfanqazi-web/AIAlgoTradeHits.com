"""
KaamyabPakistan BigQuery Setup Script
Creates dataset and tables for the 512 Projects Database
"""

from google.cloud import bigquery
import csv
import os

# Configuration - Update this to your personal project
PROJECT_ID = 'aialgotradehits'  # Change to your personal project if needed
DATASET_ID = 'kaamyabpakistan_data'
LOCATION = 'US'

def create_dataset(client):
    """Create the KaamyabPakistan dataset"""
    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = LOCATION
    dataset.description = "KaamyabPakistan 512 Projects Database - Microfinance and Social Impact Platform"

    try:
        dataset = client.create_dataset(dataset, exists_ok=True)
        print(f"Created dataset: {dataset_ref}")
    except Exception as e:
        print(f"Dataset creation: {e}")

    return dataset

def create_projects_table(client):
    """Create the main projects table with all 18 fields"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.projects"

    schema = [
        bigquery.SchemaField("project_id", "STRING", mode="REQUIRED", description="Unique project identifier (e.g., AGR_001, IT_001)"),
        bigquery.SchemaField("serial_number", "INTEGER", description="Sequential number 1-512"),
        bigquery.SchemaField("project_name", "STRING", description="Name of the project"),
        bigquery.SchemaField("category", "STRING", description="Main category (Agriculture, IT, Electronics, Energy, Construction, Food, Garments, Mechanical)"),
        bigquery.SchemaField("subcategory", "STRING", description="Subcategory within main category"),
        bigquery.SchemaField("project_type", "STRING", description="Type: Mushariqa, Database, Research_POC"),
        bigquery.SchemaField("short_description", "STRING", description="Brief one-line description"),
        bigquery.SchemaField("detailed_description", "STRING", description="Comprehensive project description"),
        bigquery.SchemaField("jobs_per_project", "INTEGER", description="Number of jobs created per project"),
        bigquery.SchemaField("jobs_per_postal_code", "INTEGER", description="Jobs created per postal code implementation"),
        bigquery.SchemaField("capital_requirement_usd", "INTEGER", description="Initial capital required in USD"),
        bigquery.SchemaField("roi_percentage", "INTEGER", description="Expected return on investment percentage"),
        bigquery.SchemaField("payback_months", "INTEGER", description="Months to recover investment"),
        bigquery.SchemaField("feasibility_score", "FLOAT", description="Feasibility score 1-10"),
        bigquery.SchemaField("complexity", "STRING", description="Low, Medium, or High"),
        bigquery.SchemaField("required_skills", "STRING", description="Skills needed, semicolon-separated"),
        bigquery.SchemaField("target_regions", "STRING", description="Target regions, semicolon-separated"),
        bigquery.SchemaField("export_potential", "STRING", description="Low, Medium, or High export potential"),
        bigquery.SchemaField("created_at", "TIMESTAMP", description="Record creation timestamp"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", description="Record update timestamp"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "512 Development Projects for Pakistan's Economic Growth"

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"Created table: {table_id}")
    except Exception as e:
        print(f"Table creation error: {e}")

    return table

def create_categories_table(client):
    """Create categories reference table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.categories"

    schema = [
        bigquery.SchemaField("category_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("category_name", "STRING"),
        bigquery.SchemaField("category_name_urdu", "STRING"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("icon", "STRING"),
        bigquery.SchemaField("color", "STRING"),
        bigquery.SchemaField("project_count", "INTEGER"),
        bigquery.SchemaField("total_jobs_potential", "INTEGER"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Project Categories Reference Table"

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"Created table: {table_id}")
    except Exception as e:
        print(f"Table creation error: {e}")

    return table

def create_beneficiaries_table(client):
    """Create beneficiaries/applications table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.beneficiaries"

    schema = [
        bigquery.SchemaField("beneficiary_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("cnic", "STRING"),
        bigquery.SchemaField("phone", "STRING"),
        bigquery.SchemaField("email", "STRING"),
        bigquery.SchemaField("location", "STRING"),
        bigquery.SchemaField("postal_code", "STRING"),
        bigquery.SchemaField("project_id", "STRING"),
        bigquery.SchemaField("loan_amount", "FLOAT"),
        bigquery.SchemaField("loan_status", "STRING"),
        bigquery.SchemaField("application_date", "TIMESTAMP"),
        bigquery.SchemaField("approval_date", "TIMESTAMP"),
        bigquery.SchemaField("family_size", "INTEGER"),
        bigquery.SchemaField("monthly_income", "FLOAT"),
        bigquery.SchemaField("skills", "STRING"),
        bigquery.SchemaField("notes", "STRING"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Beneficiaries and Loan Applications"

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"Created table: {table_id}")
    except Exception as e:
        print(f"Table creation error: {e}")

    return table

def create_success_stories_table(client):
    """Create success stories table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.success_stories"

    schema = [
        bigquery.SchemaField("story_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("beneficiary_id", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("location", "STRING"),
        bigquery.SchemaField("project_id", "STRING"),
        bigquery.SchemaField("business_name", "STRING"),
        bigquery.SchemaField("loan_amount", "FLOAT"),
        bigquery.SchemaField("monthly_income_before", "FLOAT"),
        bigquery.SchemaField("monthly_income_after", "FLOAT"),
        bigquery.SchemaField("story_text", "STRING"),
        bigquery.SchemaField("story_text_urdu", "STRING"),
        bigquery.SchemaField("image_url", "STRING"),
        bigquery.SchemaField("video_url", "STRING"),
        bigquery.SchemaField("published_date", "TIMESTAMP"),
        bigquery.SchemaField("is_featured", "BOOLEAN"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Success Stories from Beneficiaries"

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"Created table: {table_id}")
    except Exception as e:
        print(f"Table creation error: {e}")

    return table

def create_programs_table(client):
    """Create microfinance programs table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.programs"

    schema = [
        bigquery.SchemaField("program_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("name_urdu", "STRING"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("max_loan_amount", "FLOAT"),
        bigquery.SchemaField("min_loan_amount", "FLOAT"),
        bigquery.SchemaField("interest_rate", "FLOAT"),
        bigquery.SchemaField("max_tenure_months", "INTEGER"),
        bigquery.SchemaField("eligibility_criteria", "STRING"),
        bigquery.SchemaField("required_documents", "STRING"),
        bigquery.SchemaField("is_active", "BOOLEAN"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Microfinance Loan Programs"

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"Created table: {table_id}")
    except Exception as e:
        print(f"Table creation error: {e}")

    return table

def load_projects_from_csv(client, csv_file_path):
    """Load projects data from CSV file"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.projects"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=False,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        schema=[
            bigquery.SchemaField("project_id", "STRING"),
            bigquery.SchemaField("serial_number", "INTEGER"),
            bigquery.SchemaField("project_name", "STRING"),
            bigquery.SchemaField("category", "STRING"),
            bigquery.SchemaField("subcategory", "STRING"),
            bigquery.SchemaField("project_type", "STRING"),
            bigquery.SchemaField("short_description", "STRING"),
            bigquery.SchemaField("detailed_description", "STRING"),
            bigquery.SchemaField("jobs_per_project", "INTEGER"),
            bigquery.SchemaField("jobs_per_postal_code", "INTEGER"),
            bigquery.SchemaField("capital_requirement_usd", "INTEGER"),
            bigquery.SchemaField("roi_percentage", "INTEGER"),
            bigquery.SchemaField("payback_months", "INTEGER"),
            bigquery.SchemaField("feasibility_score", "FLOAT"),
            bigquery.SchemaField("complexity", "STRING"),
            bigquery.SchemaField("required_skills", "STRING"),
            bigquery.SchemaField("target_regions", "STRING"),
            bigquery.SchemaField("export_potential", "STRING"),
        ],
    )

    with open(csv_file_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_id, job_config=job_config)

    job.result()  # Wait for the job to complete

    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows into {table_id}")
    return table.num_rows

def load_categories_data(client):
    """Load category reference data"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.categories"

    categories = [
        {"category_id": "AGR", "category_name": "Agriculture", "category_name_urdu": "زراعت",
         "description": "Farming, livestock, and agricultural value chain projects", "icon": "🌾", "color": "#22c55e"},
        {"category_id": "IT", "category_name": "Information Technology", "category_name_urdu": "انفارمیشن ٹیکنالوجی",
         "description": "Software development, BPO, and digital services", "icon": "💻", "color": "#3b82f6"},
        {"category_id": "ELEC", "category_name": "Electronics", "category_name_urdu": "الیکٹرانکس",
         "description": "Electronic manufacturing and assembly", "icon": "🔌", "color": "#8b5cf6"},
        {"category_id": "ENERGY", "category_name": "Energy", "category_name_urdu": "توانائی",
         "description": "Renewable energy and power solutions", "icon": "⚡", "color": "#f59e0b"},
        {"category_id": "CONST", "category_name": "Construction", "category_name_urdu": "تعمیرات",
         "description": "Building materials and construction services", "icon": "🏗️", "color": "#6366f1"},
        {"category_id": "FOOD", "category_name": "Food Processing", "category_name_urdu": "فوڈ پروسیسنگ",
         "description": "Food manufacturing and processing", "icon": "🍲", "color": "#ec4899"},
        {"category_id": "GARM", "category_name": "Garments", "category_name_urdu": "ملبوسات",
         "description": "Textile and garment manufacturing", "icon": "👔", "color": "#14b8a6"},
        {"category_id": "MECH", "category_name": "Mechanical", "category_name_urdu": "مکینیکل",
         "description": "Machinery and mechanical manufacturing", "icon": "⚙️", "color": "#64748b"},
    ]

    errors = client.insert_rows_json(table_id, categories)
    if errors:
        print(f"Errors loading categories: {errors}")
    else:
        print(f"Loaded {len(categories)} categories")

def load_programs_data(client):
    """Load microfinance programs data"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.programs"

    programs = [
        {"program_id": "P001", "name": "Gharelu Karobar", "name_urdu": "گھریلو کاروبار",
         "description": "Home-based business loans for women", "max_loan_amount": 100000, "min_loan_amount": 10000,
         "interest_rate": 0, "max_tenure_months": 12, "eligibility_criteria": "Women with home-based business idea",
         "required_documents": "CNIC, Photo, Business Plan", "is_active": True},
        {"program_id": "P002", "name": "Zari Karobar", "name_urdu": "زرعی کاروبار",
         "description": "Agricultural business loans", "max_loan_amount": 200000, "min_loan_amount": 25000,
         "interest_rate": 5, "max_tenure_months": 18, "eligibility_criteria": "Farmers with land or livestock",
         "required_documents": "CNIC, Land Documents, Business Plan", "is_active": True},
        {"program_id": "P003", "name": "Hunarmand Pakistan", "name_urdu": "ہنرمند پاکستان",
         "description": "Skilled trades and vocational business loans", "max_loan_amount": 150000, "min_loan_amount": 20000,
         "interest_rate": 0, "max_tenure_months": 24, "eligibility_criteria": "Trained skilled workers",
         "required_documents": "CNIC, Skill Certificate, Business Plan", "is_active": True},
        {"program_id": "P004", "name": "Naujawan Pakistan", "name_urdu": "نوجوان پاکستان",
         "description": "Youth entrepreneurship loans", "max_loan_amount": 300000, "min_loan_amount": 50000,
         "interest_rate": 3, "max_tenure_months": 36, "eligibility_criteria": "Age 18-35 with business idea",
         "required_documents": "CNIC, Education Certificates, Business Plan", "is_active": True},
        {"program_id": "P005", "name": "Khawateen Entrepreneurs", "name_urdu": "خواتین انٹرپرینیورز",
         "description": "Women entrepreneurs program", "max_loan_amount": 250000, "min_loan_amount": 30000,
         "interest_rate": 3, "max_tenure_months": 24, "eligibility_criteria": "Women with business experience",
         "required_documents": "CNIC, Photo, Business Plan, References", "is_active": True},
    ]

    errors = client.insert_rows_json(table_id, programs)
    if errors:
        print(f"Errors loading programs: {errors}")
    else:
        print(f"Loaded {len(programs)} programs")

def main():
    """Main setup function"""
    print("=" * 60)
    print("KaamyabPakistan BigQuery Setup")
    print("=" * 60)

    client = bigquery.Client(project=PROJECT_ID)

    # Create dataset
    print("\n1. Creating dataset...")
    create_dataset(client)

    # Create tables
    print("\n2. Creating tables...")
    create_projects_table(client)
    create_categories_table(client)
    create_beneficiaries_table(client)
    create_success_stories_table(client)
    create_programs_table(client)

    # Load data
    print("\n3. Loading reference data...")
    load_categories_data(client)
    load_programs_data(client)

    # Load projects from CSV
    print("\n4. Loading projects data...")
    csv_path = os.path.join(os.path.dirname(__file__), 'kaamyabpakistan_app', 'kaamyab-projects-database.json')
    if os.path.exists(csv_path):
        rows = load_projects_from_csv(client, csv_path)
        print(f"Loaded {rows} projects")
    else:
        print(f"CSV file not found at: {csv_path}")
        print("Please load projects manually using: load_projects_from_csv(client, 'path/to/file.csv')")

    print("\n" + "=" * 60)
    print("Setup Complete!")
    print(f"Dataset: {PROJECT_ID}.{DATASET_ID}")
    print("Tables: projects, categories, beneficiaries, success_stories, programs")
    print("=" * 60)

if __name__ == '__main__':
    main()
