"""
Load all available KaamyabPakistan projects to BigQuery
Combines data from:
1. kaamyab-projects-database.json (CSV format, 240 projects, serial 1-240)
2. projects_401_512.csv (67 projects, serial 410-512 with gaps)
3. kaamyab-combined-csv.txt (107 projects, fills gaps)
"""

import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
import csv

PROJECT_ID = 'aialgotradehits'
DATASET = 'kaamyabpakistan_data'

def load_projects():
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{DATASET}.projects"

    # Schema for projects table
    schema = [
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
    ]

    # Drop and recreate table
    print("Dropping existing projects table...")
    try:
        client.delete_table(table_id)
        print("  Table deleted")
    except Exception as e:
        print(f"  Table didn't exist: {e}")

    print("Creating new projects table...")
    table = bigquery.Table(table_id, schema=schema)
    client.create_table(table)
    print("  Table created")

    all_projects = {}  # Use dict to prevent duplicates by serial_number

    # Helper to parse integer safely
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

    # Load from main database file (240 projects, serial 1-240)
    print("\n1. Reading kaamyab-projects-database.json (CSV format)...")
    with open('kaamyabpakistan_app/kaamyab-projects-database.json', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                serial = safe_int(row.get('serial_number'))
                if serial == 0:
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
                all_projects[serial] = project
                count += 1
            except Exception as e:
                print(f"  Warning: Skipping row due to error: {e}")

    print(f"   Loaded {count} projects (serial 1-240)")

    # Load from projects_401_512.csv (67 projects)
    print("\n2. Reading projects_401_512.csv...")
    with open('kaamyabpakistan_app/projects_401_512.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                serial = safe_int(row.get('serial_number'))
                if serial == 0 or serial in all_projects:
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
                all_projects[serial] = project
                count += 1
            except Exception as e:
                print(f"  Warning: Skipping row due to error: {e}")

    print(f"   Added {count} new projects")

    # Load from combined file (fills gaps) - has different column names
    print("\n3. Reading kaamyab-combined-csv.txt...")
    with open('kaamyabpakistan_app/kaamyab-combined-csv.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                # This file uses 'serial' instead of 'serial_number'
                serial = safe_int(row.get('serial'))
                if serial == 0 or serial in all_projects:
                    continue

                project = {
                    'project_id': row.get('project_id', ''),
                    'serial_number': serial,
                    'project_name': row.get('name', ''),
                    'category': row.get('category', ''),
                    'subcategory': row.get('subcategory', ''),
                    'project_type': row.get('type', ''),
                    'short_description': row.get('short_description', ''),
                    'detailed_description': row.get('detailed_description', ''),
                    'jobs_per_project': safe_int(row.get('jobs_per_project')),
                    'jobs_per_postal_code': safe_int(row.get('jobs_per_postal')),
                    'capital_requirement_usd': safe_int(row.get('min_investment_pkr')),  # Different name
                    'roi_percentage': safe_int(row.get('monthly_revenue_pkr')),  # Different name
                    'payback_months': safe_int(row.get('roi_months')),  # Different name
                    'feasibility_score': safe_float(row.get('feasibility_score')),
                    'complexity': row.get('complexity', ''),
                    'required_skills': row.get('skills_required', ''),  # Different name
                    'target_regions': row.get('target_regions', ''),
                    'export_potential': row.get('export_potential', ''),
                }
                all_projects[serial] = project
                count += 1
            except Exception as e:
                print(f"  Warning: Skipping row due to error: {e}")

    print(f"   Added {count} new projects")

    # Convert to sorted list
    projects_list = [all_projects[k] for k in sorted(all_projects.keys())]

    print(f"\n{'='*50}")
    print(f"Total unique projects: {len(projects_list)}")
    print(f"Serial number range: {projects_list[0]['serial_number']} to {projects_list[-1]['serial_number']}")

    # Get unique categories
    categories = set(p['category'] for p in projects_list)
    print(f"Unique categories: {len(categories)}")
    for cat in sorted(categories):
        count = len([p for p in projects_list if p['category'] == cat])
        print(f"  - {cat}: {count} projects")

    # Load to BigQuery in batches
    print("\nLoading to BigQuery...")
    batch_size = 100
    for i in range(0, len(projects_list), batch_size):
        batch = projects_list[i:i+batch_size]
        errors = client.insert_rows_json(table_id, batch)
        if errors:
            print(f"  Batch {i//batch_size + 1}: Errors: {errors[:2]}...")
        else:
            print(f"  Batch {i//batch_size + 1}: Loaded {len(batch)} projects")

    # Verify
    print("\nVerifying...")
    query = f"SELECT COUNT(*) as count FROM `{table_id}`"
    result = list(client.query(query).result())[0]
    print(f"Total projects in BigQuery: {result.count}")

    # Update categories table
    print("\nUpdating categories table...")
    categories_table_id = f"{PROJECT_ID}.{DATASET}.categories"

    # Get category stats
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

    # Category names in Urdu and icons
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
        print(f"  Loaded {len(category_rows)} categories")

    # Show missing serial numbers
    print("\n" + "="*50)
    print("MISSING SERIAL NUMBERS (need to be added later):")
    all_serials = set(range(1, 513))
    loaded_serials = set(all_projects.keys())
    missing = sorted(all_serials - loaded_serials)

    if missing:
        # Group consecutive missing numbers
        ranges = []
        start = missing[0]
        end = missing[0]
        for s in missing[1:]:
            if s == end + 1:
                end = s
            else:
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{end}")
                start = s
                end = s
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")
        print(f"  Missing ranges: {', '.join(ranges)}")
        print(f"  Total missing: {len(missing)} projects")
    else:
        print("  None - all 512 projects loaded!")

    print("\n" + "="*50)
    print("LOAD COMPLETE!")
    print("="*50)

if __name__ == '__main__':
    load_projects()
