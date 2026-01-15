"""
Setup BigQuery Tables for HomeFranchise.Biz
Creates dataset and tables for franchise management
"""

from google.cloud import bigquery
import sys, io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'homefranchise_data'

client = bigquery.Client(project=PROJECT_ID)

# Create dataset if not exists
def create_dataset():
    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {DATASET_ID} already exists")
    except:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"Created dataset {DATASET_ID}")

# Table schemas
TABLES = {
    'franchises': [
        bigquery.SchemaField('franchise_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('business_name', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('category', 'STRING'),
        bigquery.SchemaField('description', 'STRING'),
        bigquery.SchemaField('franchise_fee', 'FLOAT'),
        bigquery.SchemaField('total_investment', 'STRING'),
        bigquery.SchemaField('royalty_fee', 'FLOAT'),
        bigquery.SchemaField('locations', 'STRING'),
        bigquery.SchemaField('support', 'STRING'),
        bigquery.SchemaField('contact_email', 'STRING'),
        bigquery.SchemaField('contact_phone', 'STRING'),
        bigquery.SchemaField('owner_user_id', 'INTEGER'),
        bigquery.SchemaField('is_verified', 'BOOLEAN'),
        bigquery.SchemaField('is_active', 'BOOLEAN'),
        bigquery.SchemaField('created_at', 'TIMESTAMP'),
        bigquery.SchemaField('updated_at', 'TIMESTAMP'),
    ],

    'applications': [
        bigquery.SchemaField('application_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('franchise_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('user_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('applicant_name', 'STRING'),
        bigquery.SchemaField('applicant_email', 'STRING'),
        bigquery.SchemaField('applicant_phone', 'STRING'),
        bigquery.SchemaField('message', 'STRING'),
        bigquery.SchemaField('investment_ready', 'FLOAT'),
        bigquery.SchemaField('status', 'STRING'),  # pending, approved, rejected
        bigquery.SchemaField('created_at', 'TIMESTAMP'),
        bigquery.SchemaField('updated_at', 'TIMESTAMP'),
    ],

    'users': [
        bigquery.SchemaField('user_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('username', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('email', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('password_hash', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('role', 'STRING'),  # franchiser, franchisee, admin
        bigquery.SchemaField('phone', 'STRING'),
        bigquery.SchemaField('is_active', 'BOOLEAN'),
        bigquery.SchemaField('created_at', 'TIMESTAMP'),
        bigquery.SchemaField('updated_at', 'TIMESTAMP'),
    ],

    'categories': [
        bigquery.SchemaField('category_id', 'INTEGER', mode='REQUIRED'),
        bigquery.SchemaField('name', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('description', 'STRING'),
        bigquery.SchemaField('icon', 'STRING'),
        bigquery.SchemaField('is_active', 'BOOLEAN'),
        bigquery.SchemaField('created_at', 'TIMESTAMP'),
    ],
}

def create_tables():
    for table_name, schema in TABLES.items():
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        try:
            client.get_table(table_ref)
            print(f"Table {table_name} already exists")
        except:
            table = bigquery.Table(table_ref, schema=schema)
            client.create_table(table)
            print(f"Created table {table_name}")

def insert_sample_data():
    """Insert sample franchise categories"""
    categories = [
        {'category_id': 1, 'name': 'Food & Beverage', 'description': 'Restaurants, cafes, food delivery', 'icon': 'fa-utensils', 'is_active': True, 'created_at': 'AUTO'},
        {'category_id': 2, 'name': 'Retail', 'description': 'Retail stores and shops', 'icon': 'fa-store', 'is_active': True, 'created_at': 'AUTO'},
        {'category_id': 3, 'name': 'Services', 'description': 'Business and consumer services', 'icon': 'fa-concierge-bell', 'is_active': True, 'created_at': 'AUTO'},
        {'category_id': 4, 'name': 'Education', 'description': 'Training and education centers', 'icon': 'fa-graduation-cap', 'is_active': True, 'created_at': 'AUTO'},
        {'category_id': 5, 'name': 'Healthcare', 'description': 'Health and wellness services', 'icon': 'fa-heartbeat', 'is_active': True, 'created_at': 'AUTO'},
        {'category_id': 6, 'name': 'Technology', 'description': 'Tech services and products', 'icon': 'fa-laptop-code', 'is_active': True, 'created_at': 'AUTO'},
        {'category_id': 7, 'name': 'Home Services', 'description': 'Home maintenance and cleaning', 'icon': 'fa-home', 'is_active': True, 'created_at': 'AUTO'},
    ]

    from datetime import datetime
    now = datetime.utcnow().isoformat()

    rows = []
    for cat in categories:
        cat['created_at'] = now
        rows.append(cat)

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.categories"
    try:
        # Check if data exists
        query = f"SELECT COUNT(*) as cnt FROM `{table_ref}`"
        result = list(client.query(query).result())
        if result[0].cnt > 0:
            print("Categories already populated")
            return
    except:
        pass

    errors = client.insert_rows_json(table_ref, rows)
    if errors:
        print(f"Errors inserting categories: {errors}")
    else:
        print("Inserted sample categories")

def insert_sample_franchises():
    """Insert sample franchise listings"""
    from datetime import datetime
    now = datetime.utcnow().isoformat()

    franchises = [
        {
            'franchise_id': 1,
            'business_name': 'Fresh Juice Bar',
            'category': 'Food & Beverage',
            'description': 'Premium fresh juice franchise with organic ingredients',
            'franchise_fee': 15000.0,
            'total_investment': '30000 - 50000',
            'royalty_fee': 5.0,
            'locations': 'Pakistan, UAE, Saudi Arabia',
            'support': 'Full training, marketing support, equipment supply',
            'contact_email': 'franchise@freshjuice.com',
            'contact_phone': '+92 300 1234567',
            'owner_user_id': 1,
            'is_verified': True,
            'is_active': True,
            'created_at': now,
            'updated_at': now
        },
        {
            'franchise_id': 2,
            'business_name': 'Tech Repair Hub',
            'category': 'Technology',
            'description': 'Mobile and computer repair franchise',
            'franchise_fee': 10000.0,
            'total_investment': '20000 - 40000',
            'royalty_fee': 4.0,
            'locations': 'Pakistan, India',
            'support': 'Technical training, parts supply chain',
            'contact_email': 'franchise@techrepair.com',
            'contact_phone': '+92 321 9876543',
            'owner_user_id': 1,
            'is_verified': True,
            'is_active': True,
            'created_at': now,
            'updated_at': now
        },
        {
            'franchise_id': 3,
            'business_name': 'Home Cleaning Pro',
            'category': 'Home Services',
            'description': 'Professional home cleaning services franchise',
            'franchise_fee': 8000.0,
            'total_investment': '15000 - 25000',
            'royalty_fee': 6.0,
            'locations': 'Pakistan',
            'support': 'Training, equipment, marketing',
            'contact_email': 'franchise@cleaningpro.com',
            'contact_phone': '+92 311 5551234',
            'owner_user_id': 1,
            'is_verified': True,
            'is_active': True,
            'created_at': now,
            'updated_at': now
        },
        {
            'franchise_id': 4,
            'business_name': 'Language Academy',
            'category': 'Education',
            'description': 'English language and programming courses',
            'franchise_fee': 20000.0,
            'total_investment': '40000 - 70000',
            'royalty_fee': 5.0,
            'locations': 'Pakistan, Bangladesh, Sri Lanka',
            'support': 'Curriculum, teacher training, certification',
            'contact_email': 'franchise@langacademy.com',
            'contact_phone': '+92 333 7778899',
            'owner_user_id': 1,
            'is_verified': True,
            'is_active': True,
            'created_at': now,
            'updated_at': now
        },
        {
            'franchise_id': 5,
            'business_name': 'Healthy Meals Delivery',
            'category': 'Food & Beverage',
            'description': 'Healthy meal prep and delivery service',
            'franchise_fee': 12000.0,
            'total_investment': '25000 - 45000',
            'royalty_fee': 5.0,
            'locations': 'Pakistan, UAE',
            'support': 'Recipes, packaging, delivery logistics',
            'contact_email': 'franchise@healthymeals.com',
            'contact_phone': '+92 345 6667788',
            'owner_user_id': 1,
            'is_verified': True,
            'is_active': True,
            'created_at': now,
            'updated_at': now
        },
        {
            'franchise_id': 6,
            'business_name': 'Digital Marketing Agency',
            'category': 'Services',
            'description': 'Full-service digital marketing franchise',
            'franchise_fee': 15000.0,
            'total_investment': '20000 - 35000',
            'royalty_fee': 4.0,
            'locations': 'Worldwide',
            'support': 'Tools, training, client acquisition support',
            'contact_email': 'franchise@digitalagency.com',
            'contact_phone': '+92 300 4445566',
            'owner_user_id': 1,
            'is_verified': True,
            'is_active': True,
            'created_at': now,
            'updated_at': now
        },
    ]

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.franchises"
    try:
        query = f"SELECT COUNT(*) as cnt FROM `{table_ref}`"
        result = list(client.query(query).result())
        if result[0].cnt > 0:
            print("Franchises already populated")
            return
    except:
        pass

    errors = client.insert_rows_json(table_ref, franchises)
    if errors:
        print(f"Errors inserting franchises: {errors}")
    else:
        print(f"Inserted {len(franchises)} sample franchises")

if __name__ == '__main__':
    print("Setting up HomeFranchise.Biz BigQuery tables...")
    print("=" * 50)
    create_dataset()
    create_tables()
    insert_sample_data()
    insert_sample_franchises()
    print("=" * 50)
    print("Setup complete!")
