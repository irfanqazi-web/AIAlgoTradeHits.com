"""
KaamyabPakistan Complete Migration Script
Migrates all data from CSV and JSON to aialgotradehits BigQuery
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import json
from google.cloud import bigquery

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'kaamyabpakistan_data'

client = bigquery.Client(project=PROJECT_ID)

def create_all_tables():
    """Create all required tables"""
    print("=" * 60)
    print("Creating BigQuery Tables")
    print("=" * 60)

    # Categories table
    categories_schema = [
        bigquery.SchemaField("category_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("category_name", "STRING"),
        bigquery.SchemaField("category_name_urdu", "STRING"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("icon", "STRING"),
        bigquery.SchemaField("color", "STRING"),
        bigquery.SchemaField("project_count", "INTEGER"),
    ]

    # Programs table
    programs_schema = [
        bigquery.SchemaField("program_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("name_urdu", "STRING"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("max_loan_amount", "FLOAT"),
        bigquery.SchemaField("min_loan_amount", "FLOAT"),
        bigquery.SchemaField("interest_rate", "FLOAT"),
        bigquery.SchemaField("max_tenure_months", "INTEGER"),
        bigquery.SchemaField("eligibility_criteria", "STRING"),
        bigquery.SchemaField("is_active", "BOOLEAN"),
    ]

    # Opportunities table (from old CSV)
    opportunities_schema = [
        bigquery.SchemaField("id", "STRING"),
        bigquery.SchemaField("sub_id", "STRING"),
        bigquery.SchemaField("franchise", "STRING"),
        bigquery.SchemaField("type", "STRING"),
        bigquery.SchemaField("members", "STRING"),
        bigquery.SchemaField("foreign_jobs", "STRING"),
        bigquery.SchemaField("domestic_jobs", "STRING"),
        bigquery.SchemaField("export_market_size", "STRING"),
        bigquery.SchemaField("domestic_market_rs", "STRING"),
        bigquery.SchemaField("problem_statement", "STRING"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("people_impact", "STRING"),
        bigquery.SchemaField("financial_impact", "STRING"),
    ]

    # Success stories table
    success_stories_schema = [
        bigquery.SchemaField("story_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("beneficiary_name", "STRING"),
        bigquery.SchemaField("location", "STRING"),
        bigquery.SchemaField("business_type", "STRING"),
        bigquery.SchemaField("loan_amount", "FLOAT"),
        bigquery.SchemaField("monthly_income_before", "FLOAT"),
        bigquery.SchemaField("monthly_income_after", "FLOAT"),
        bigquery.SchemaField("story_text", "STRING"),
        bigquery.SchemaField("story_text_urdu", "STRING"),
        bigquery.SchemaField("is_featured", "BOOLEAN"),
    ]

    tables = [
        ("categories", categories_schema),
        ("programs", programs_schema),
        ("opportunities", opportunities_schema),
        ("success_stories", success_stories_schema),
    ]

    for table_name, schema in tables:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        table = bigquery.Table(table_id, schema=schema)
        try:
            client.create_table(table, exists_ok=True)
            print(f"  Created/verified table: {table_name}")
        except Exception as e:
            print(f"  Error with {table_name}: {e}")

def load_projects_from_json():
    """Load 512 projects from JSON file"""
    print("\n" + "=" * 60)
    print("Loading Projects from JSON")
    print("=" * 60)

    json_path = "C:/1AITrading/Trading/kaamyabpakistan_app/kaamyab-projects-database.json"

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            # Read as CSV since it's actually CSV format
            pass
    except:
        pass

    # The JSON file is actually in CSV format, let's read it as CSV
    csv_path = json_path  # It's actually CSV format based on earlier read

    # Read the JSON file differently - it might be newline-delimited JSON
    try:
        # First try to read as CSV (since the content looks like CSV)
        df = pd.read_csv(json_path)
        print(f"  Loaded {len(df)} projects from file")

        # Clean up data
        df = df.fillna('')

        # Convert numeric columns
        numeric_cols = ['serial_number', 'jobs_per_project', 'jobs_per_postal_code',
                       'capital_requirement_usd', 'roi_percentage', 'payback_months']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        if 'feasibility_score' in df.columns:
            df['feasibility_score'] = pd.to_numeric(df['feasibility_score'], errors='coerce').fillna(0.0)

        # Upload to BigQuery
        table_id = f"{PROJECT_ID}.{DATASET_ID}.projects"
        job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()

        table = client.get_table(table_id)
        print(f"  Loaded {table.num_rows} projects to BigQuery")
        return table.num_rows

    except Exception as e:
        print(f"  Error loading projects: {e}")
        return 0

def load_opportunities_from_csv():
    """Load opportunities from old CSV file"""
    print("\n" + "=" * 60)
    print("Loading Opportunities from CSV")
    print("=" * 60)

    csv_path = "C:/1AITrading/Trading/sub_project_description.csv"

    try:
        df = pd.read_csv(csv_path)
        print(f"  Loaded {len(df)} rows from CSV")

        # Remove duplicate header rows and invalid entries
        df = df[df['id'] != 'id']
        df = df[df['id'] != 'undefined']
        df = df.dropna(subset=['franchise'])

        # Select only the columns we need
        cols = ['id', 'sub_id', 'franchise', 'type', 'members', 'foreign_jobs',
                'domestic_jobs', 'export_market_size', 'domestic_market_rs',
                'problem_statement', 'description', 'people_impact', 'financial_impact']

        # Handle column name variations
        if 'export_market_rs' in df.columns and 'export_market_size' not in df.columns:
            df['export_market_size'] = df['export_market_rs']
        if 'domestic_markets_rs' in df.columns and 'domestic_market_rs' not in df.columns:
            df['domestic_market_rs'] = df['domestic_markets_rs']

        available_cols = [c for c in cols if c in df.columns]
        df = df[available_cols]

        # Fill NaN
        df = df.fillna('')

        # Convert all columns to string
        for col in df.columns:
            df[col] = df[col].astype(str)

        print(f"  Cleaned data: {len(df)} valid records")

        # Upload in chunks of 100
        table_id = f"{PROJECT_ID}.{DATASET_ID}.opportunities"
        chunk_size = 100
        total_loaded = 0

        job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()

        table = client.get_table(table_id)
        print(f"  Loaded {table.num_rows} opportunities to BigQuery")
        return table.num_rows

    except Exception as e:
        print(f"  Error loading opportunities: {e}")
        import traceback
        traceback.print_exc()
        return 0

def load_reference_data():
    """Load categories and programs reference data"""
    print("\n" + "=" * 60)
    print("Loading Reference Data")
    print("=" * 60)

    # Categories
    categories = [
        {"category_id": "AGR", "category_name": "Agriculture", "category_name_urdu": "زراعت",
         "description": "Farming, livestock, and agricultural value chain", "icon": "leaf", "color": "#22c55e", "project_count": 44},
        {"category_id": "IT", "category_name": "Information Technology", "category_name_urdu": "انفارمیشن ٹیکنالوجی",
         "description": "Software, digital services, and tech solutions", "icon": "laptop", "color": "#3b82f6", "project_count": 54},
        {"category_id": "ELEC", "category_name": "Electronics", "category_name_urdu": "الیکٹرانکس",
         "description": "Electronic manufacturing and services", "icon": "cpu", "color": "#8b5cf6", "project_count": 50},
        {"category_id": "ENERGY", "category_name": "Energy", "category_name_urdu": "توانائی",
         "description": "Renewable energy and power solutions", "icon": "zap", "color": "#f59e0b", "project_count": 45},
        {"category_id": "CONST", "category_name": "Construction", "category_name_urdu": "تعمیرات",
         "description": "Building materials and construction", "icon": "home", "color": "#6366f1", "project_count": 60},
        {"category_id": "FOOD", "category_name": "Food Processing", "category_name_urdu": "فوڈ پروسیسنگ",
         "description": "Food manufacturing and processing", "icon": "utensils", "color": "#ec4899", "project_count": 55},
        {"category_id": "GARM", "category_name": "Garments", "category_name_urdu": "ملبوسات",
         "description": "Textile and garment manufacturing", "icon": "scissors", "color": "#14b8a6", "project_count": 65},
        {"category_id": "MECH", "category_name": "Mechanical", "category_name_urdu": "مکینیکل",
         "description": "Machinery and mechanical work", "icon": "settings", "color": "#64748b", "project_count": 50},
        {"category_id": "HEALTH", "category_name": "Healthcare", "category_name_urdu": "صحت",
         "description": "Health products and herbal medicine", "icon": "heart", "color": "#ef4444", "project_count": 45},
        {"category_id": "SERV", "category_name": "Services", "category_name_urdu": "خدمات",
         "description": "Various service businesses", "icon": "users", "color": "#06b6d4", "project_count": 44},
    ]

    table_id = f"{PROJECT_ID}.{DATASET_ID}.categories"
    errors = client.insert_rows_json(table_id, categories)
    if errors:
        print(f"  Categories errors: {errors}")
    else:
        print(f"  Loaded {len(categories)} categories")

    # Programs
    programs = [
        {"program_id": "P001", "name": "Gharelu Karobar", "name_urdu": "گھریلو کاروبار",
         "description": "Home-based business loans for women", "max_loan_amount": 100000.0, "min_loan_amount": 10000.0,
         "interest_rate": 0.0, "max_tenure_months": 12, "eligibility_criteria": "Women with home-based business idea", "is_active": True},
        {"program_id": "P002", "name": "Zari Karobar", "name_urdu": "زرعی کاروبار",
         "description": "Agricultural business loans", "max_loan_amount": 200000.0, "min_loan_amount": 25000.0,
         "interest_rate": 5.0, "max_tenure_months": 18, "eligibility_criteria": "Farmers with land or livestock", "is_active": True},
        {"program_id": "P003", "name": "Hunarmand Pakistan", "name_urdu": "ہنرمند پاکستان",
         "description": "Skilled trades and vocational business loans", "max_loan_amount": 150000.0, "min_loan_amount": 20000.0,
         "interest_rate": 0.0, "max_tenure_months": 24, "eligibility_criteria": "Trained skilled workers", "is_active": True},
        {"program_id": "P004", "name": "Naujawan Pakistan", "name_urdu": "نوجوان پاکستان",
         "description": "Youth entrepreneurship loans", "max_loan_amount": 300000.0, "min_loan_amount": 50000.0,
         "interest_rate": 3.0, "max_tenure_months": 36, "eligibility_criteria": "Age 18-35 with business idea", "is_active": True},
        {"program_id": "P005", "name": "Khawateen Entrepreneurs", "name_urdu": "خواتین انٹرپرینیورز",
         "description": "Women entrepreneurs program", "max_loan_amount": 250000.0, "min_loan_amount": 30000.0,
         "interest_rate": 3.0, "max_tenure_months": 24, "eligibility_criteria": "Women with business experience", "is_active": True},
    ]

    table_id = f"{PROJECT_ID}.{DATASET_ID}.programs"
    errors = client.insert_rows_json(table_id, programs)
    if errors:
        print(f"  Programs errors: {errors}")
    else:
        print(f"  Loaded {len(programs)} programs")

    # Success stories
    success_stories = [
        {"story_id": "S001", "beneficiary_name": "Fatima Bibi", "location": "Lahore", "business_type": "Tailoring",
         "loan_amount": 50000.0, "monthly_income_before": 8000.0, "monthly_income_after": 35000.0,
         "story_text": "Started tailoring business from home, now employs 3 women",
         "story_text_urdu": "گھر سے سلائی کا کاروبار شروع کیا، اب 3 خواتین کو روزگار دیتی ہیں", "is_featured": True},
        {"story_id": "S002", "beneficiary_name": "Muhammad Ali", "location": "Multan", "business_type": "Vegetable Cart",
         "loan_amount": 30000.0, "monthly_income_before": 5000.0, "monthly_income_after": 25000.0,
         "story_text": "Purchased vegetable cart, now supplies to local shops",
         "story_text_urdu": "سبزی کا ریڑھا خریدا، اب مقامی دکانوں کو سپلائی کرتے ہیں", "is_featured": True},
        {"story_id": "S003", "beneficiary_name": "Nasreen Akhtar", "location": "Faisalabad", "business_type": "Embroidery",
         "loan_amount": 40000.0, "monthly_income_before": 6000.0, "monthly_income_after": 30000.0,
         "story_text": "Traditional embroidery business now exports to Dubai",
         "story_text_urdu": "روایتی کڑھائی کا کاروبار اب دبئی برآمد کرتا ہے", "is_featured": True},
    ]

    table_id = f"{PROJECT_ID}.{DATASET_ID}.success_stories"
    errors = client.insert_rows_json(table_id, success_stories)
    if errors:
        print(f"  Success stories errors: {errors}")
    else:
        print(f"  Loaded {len(success_stories)} success stories")

def verify_migration():
    """Verify all data loaded correctly"""
    print("\n" + "=" * 60)
    print("Verifying Migration")
    print("=" * 60)

    tables = ['projects', 'opportunities', 'categories', 'programs', 'success_stories']

    for table in tables:
        query = f"SELECT COUNT(*) as count FROM `{PROJECT_ID}.{DATASET_ID}.{table}`"
        try:
            result = list(client.query(query).result())[0]
            print(f"  {table}: {result.count} records")
        except Exception as e:
            print(f"  {table}: Error - {e}")

def main():
    print("\n" + "=" * 60)
    print("KaamyabPakistan Complete Migration")
    print(f"Target: {PROJECT_ID}.{DATASET_ID}")
    print("=" * 60)

    # Step 1: Create tables
    create_all_tables()

    # Step 2: Load projects from JSON/CSV
    load_projects_from_json()

    # Step 3: Load opportunities from old CSV
    load_opportunities_from_csv()

    # Step 4: Load reference data
    load_reference_data()

    # Step 5: Verify
    verify_migration()

    print("\n" + "=" * 60)
    print("Migration Complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
