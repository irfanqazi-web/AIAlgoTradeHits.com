"""
Add missing KaamyabPakistan projects to BigQuery
Adds 173 missing projects (serial 196, 241-406, 433-438)
"""

import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
import csv

PROJECT_ID = 'aialgotradehits'
DATASET = 'kaamyabpakistan_data'

def add_missing_projects():
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{DATASET}.projects"

    # Helper functions
    def safe_int(val, default=0):
        if not val:
            return default
        try:
            return int(float(str(val).replace(',', '')))
        except:
            return default

    def safe_float(val, default=0.0):
        if not val:
            return default
        try:
            return float(str(val).replace(',', ''))
        except:
            return default

    # Get existing serial numbers
    print("Checking existing projects...")
    query = f"SELECT serial_number FROM `{table_id}`"
    existing = set(row.serial_number for row in client.query(query).result())
    print(f"  Found {len(existing)} existing projects")

    # Load missing projects
    print("\nReading kaamyab-missing-projects.txt...")
    new_projects = []
    with open('kaamyabpakistan_app/kaamyab-missing-projects.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                serial = safe_int(row.get('serial_number'))
                if serial == 0:
                    continue
                if serial in existing:
                    print(f"  Skipping serial {serial} - already exists")
                    continue

                project = {
                    'project_id': row.get('project_id', ''),
                    'serial_number': serial,
                    'project_name': row.get('project_name', ''),
                    'category': row.get('category', ''),
                    'subcategory': row.get('subcategory', ''),
                    'project_type': row.get('project_type', ''),
                    'short_description': row.get('short_description', ''),
                    'detailed_description': row.get('detailed_description', ''),
                    'jobs_per_project': safe_int(row.get('jobs_per_project')),
                    'jobs_per_postal_code': safe_int(row.get('jobs_per_postal_code')),
                    'capital_requirement_usd': safe_int(row.get('capital_requirement_usd')),
                    'roi_percentage': safe_int(row.get('roi_percentage')),
                    'payback_months': safe_int(row.get('payback_months')),
                    'feasibility_score': safe_float(row.get('feasibility_score')),
                    'complexity': row.get('complexity', ''),
                    'required_skills': row.get('required_skills', ''),
                    'target_regions': row.get('target_regions', ''),
                    'export_potential': row.get('export_potential', ''),
                }
                new_projects.append(project)
            except Exception as e:
                print(f"  Warning: Skipping row due to error: {e}")

    print(f"  Found {len(new_projects)} new projects to add")

    if not new_projects:
        print("No new projects to add!")
        return

    # Load to BigQuery
    print("\nLoading to BigQuery...")
    batch_size = 100
    for i in range(0, len(new_projects), batch_size):
        batch = new_projects[i:i+batch_size]
        errors = client.insert_rows_json(table_id, batch)
        if errors:
            print(f"  Batch {i//batch_size + 1}: Errors: {errors[:2]}...")
        else:
            print(f"  Batch {i//batch_size + 1}: Added {len(batch)} projects")

    # Verify total
    print("\nVerifying...")
    query = f"SELECT COUNT(*) as count FROM `{table_id}`"
    result = list(client.query(query).result())[0]
    print(f"Total projects in BigQuery: {result.count}")

    # Update categories table with new counts
    print("\nUpdating categories table...")
    categories_table_id = f"{PROJECT_ID}.{DATASET}.categories"

    query = f"""
    SELECT category, COUNT(*) as project_count
    FROM `{table_id}`
    GROUP BY category
    ORDER BY category
    """
    results = list(client.query(query).result())

    # Clear and reload categories
    try:
        client.delete_table(categories_table_id)
    except:
        pass

    categories_schema = [
        bigquery.SchemaField("category_id", "STRING"),
        bigquery.SchemaField("category_name", "STRING"),
        bigquery.SchemaField("category_name_urdu", "STRING"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("icon", "STRING"),
        bigquery.SchemaField("project_count", "INTEGER"),
    ]

    categories_table = bigquery.Table(categories_table_id, schema=categories_schema)
    client.create_table(categories_table)

    urdu_names = {
        'Agriculture': 'زراعت', 'IT': 'انفارمیشن ٹیکنالوجی', 'Tourism': 'سیاحت',
        'Media': 'میڈیا', 'Herbals': 'جڑی بوٹیاں', 'Chemical': 'کیمیکل',
        'Electronics': 'الیکٹرانکس', 'Business': 'کاروبار', 'Energy': 'توانائی',
        'Food': 'کھانا', 'BioTech': 'بائیو ٹیک', 'Garments': 'ملبوسات',
        'Construction': 'تعمیرات', 'Mechanical': 'مکینیکل', 'Legal': 'قانونی',
    }

    icons = {
        'Agriculture': 'fa-seedling', 'IT': 'fa-laptop-code', 'Tourism': 'fa-plane',
        'Media': 'fa-video', 'Herbals': 'fa-leaf', 'Chemical': 'fa-flask',
        'Electronics': 'fa-microchip', 'Business': 'fa-briefcase', 'Energy': 'fa-bolt',
        'Food': 'fa-utensils', 'BioTech': 'fa-dna', 'Garments': 'fa-tshirt',
        'Construction': 'fa-hard-hat', 'Mechanical': 'fa-cogs', 'Legal': 'fa-gavel',
    }

    category_rows = []
    for i, row in enumerate(results, 1):
        cat = row.category
        category_rows.append({
            'category_id': f'CAT_{i:03d}',
            'category_name': cat,
            'category_name_urdu': urdu_names.get(cat, cat),
            'description': f'{cat} projects and opportunities',
            'icon': icons.get(cat, 'fa-folder'),
            'project_count': row.project_count
        })

    errors = client.insert_rows_json(categories_table_id, category_rows)
    if errors:
        print(f"  Category errors: {errors}")
    else:
        print(f"  Updated {len(category_rows)} categories")

    # Check for any remaining missing serial numbers
    print("\nChecking completeness...")
    query = f"SELECT serial_number FROM `{table_id}` ORDER BY serial_number"
    loaded = set(row.serial_number for row in client.query(query).result())
    all_serials = set(range(1, 513))
    missing = sorted(all_serials - loaded)

    if missing:
        print(f"  Still missing {len(missing)} serial numbers: {missing[:10]}...")
    else:
        print("  ALL 512 PROJECTS LOADED!")

    print("\n" + "="*50)
    print("COMPLETE!")
    print("="*50)

if __name__ == '__main__':
    add_missing_projects()
