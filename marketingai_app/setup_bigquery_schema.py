"""
Setup BigQuery schema for MarketingAI
Creates dataset and tables for users, brands, content, and calendar
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'marketingai_data'

def setup_schema():
    client = bigquery.Client(project=PROJECT_ID)

    # Create dataset
    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"
    dataset.description = "MarketingAI - Multi-user social media content creation platform"

    try:
        dataset = client.create_dataset(dataset, exists_ok=True)
        print(f"✅ Dataset {DATASET_ID} created/verified")
    except Exception as e:
        print(f"❌ Dataset error: {e}")
        return

    # Users table
    users_schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED", description="Unique user ID"),
        bigquery.SchemaField("email", "STRING", mode="REQUIRED", description="User email"),
        bigquery.SchemaField("password_hash", "STRING", mode="REQUIRED", description="SHA-256 password hash"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED", description="Full name"),
        bigquery.SchemaField("company", "STRING", mode="NULLABLE", description="Company/Organization name"),
        bigquery.SchemaField("role", "STRING", mode="REQUIRED", description="User role: admin, user"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED", description="Account creation time"),
        bigquery.SchemaField("last_login", "TIMESTAMP", mode="NULLABLE", description="Last login time"),
        bigquery.SchemaField("is_active", "BOOLEAN", mode="REQUIRED", description="Account active status"),
        bigquery.SchemaField("subscription_tier", "STRING", mode="NULLABLE", description="Subscription: free, pro, enterprise"),
        bigquery.SchemaField("subscription_expires", "TIMESTAMP", mode="NULLABLE", description="Subscription expiry"),
    ]

    users_table = bigquery.Table(f"{dataset_ref}.users", schema=users_schema)
    try:
        client.create_table(users_table, exists_ok=True)
        print("✅ Users table created/verified")
    except Exception as e:
        print(f"❌ Users table error: {e}")

    # Brands table
    brands_schema = [
        bigquery.SchemaField("brand_id", "STRING", mode="REQUIRED", description="Unique brand ID"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED", description="Owner user ID"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED", description="Brand name"),
        bigquery.SchemaField("description", "STRING", mode="NULLABLE", description="Brand description"),
        bigquery.SchemaField("primary_color", "STRING", mode="NULLABLE", description="Primary brand color hex"),
        bigquery.SchemaField("secondary_color", "STRING", mode="NULLABLE", description="Secondary brand color hex"),
        bigquery.SchemaField("accent_color", "STRING", mode="NULLABLE", description="Accent color hex"),
        bigquery.SchemaField("text_color", "STRING", mode="NULLABLE", description="Text color hex"),
        bigquery.SchemaField("logo_url", "STRING", mode="NULLABLE", description="Logo image URL"),
        bigquery.SchemaField("theme", "STRING", mode="NULLABLE", description="Brand theme style"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED", description="Creation time"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE", description="Last update time"),
    ]

    brands_table = bigquery.Table(f"{dataset_ref}.brands", schema=brands_schema)
    try:
        client.create_table(brands_table, exists_ok=True)
        print("✅ Brands table created/verified")
    except Exception as e:
        print(f"❌ Brands table error: {e}")

    # Content table
    content_schema = [
        bigquery.SchemaField("content_id", "STRING", mode="REQUIRED", description="Unique content ID"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED", description="Owner user ID"),
        bigquery.SchemaField("brand_id", "STRING", mode="NULLABLE", description="Associated brand ID"),
        bigquery.SchemaField("platform", "STRING", mode="REQUIRED", description="Target platform: instagram, facebook, youtube, tiktok"),
        bigquery.SchemaField("content_type", "STRING", mode="REQUIRED", description="Content type: carousel, quote, tips, etc."),
        bigquery.SchemaField("title", "STRING", mode="REQUIRED", description="Content title/heading"),
        bigquery.SchemaField("body", "STRING", mode="NULLABLE", description="Content body text"),
        bigquery.SchemaField("color_scheme", "STRING", mode="NULLABLE", description="Color scheme used"),
        bigquery.SchemaField("font_style", "STRING", mode="NULLABLE", description="Font style used"),
        bigquery.SchemaField("slide_count", "INT64", mode="NULLABLE", description="Number of slides for carousels"),
        bigquery.SchemaField("image_urls", "STRING", mode="REPEATED", description="Generated image URLs"),
        bigquery.SchemaField("scheduled_date", "TIMESTAMP", mode="NULLABLE", description="Scheduled publish date"),
        bigquery.SchemaField("published_at", "TIMESTAMP", mode="NULLABLE", description="Actual publish time"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED", description="Status: draft, scheduled, published"),
        bigquery.SchemaField("hashtags", "STRING", mode="REPEATED", description="Associated hashtags"),
        bigquery.SchemaField("caption", "STRING", mode="NULLABLE", description="Post caption"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED", description="Creation time"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE", description="Last update time"),
    ]

    content_table = bigquery.Table(f"{dataset_ref}.content", schema=content_schema)
    try:
        client.create_table(content_table, exists_ok=True)
        print("✅ Content table created/verified")
    except Exception as e:
        print(f"❌ Content table error: {e}")

    # Templates table (for custom user templates)
    templates_schema = [
        bigquery.SchemaField("template_id", "STRING", mode="REQUIRED", description="Unique template ID"),
        bigquery.SchemaField("user_id", "STRING", mode="NULLABLE", description="Owner user ID (null for system templates)"),
        bigquery.SchemaField("brand_id", "STRING", mode="NULLABLE", description="Associated brand ID"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED", description="Template name"),
        bigquery.SchemaField("category", "STRING", mode="REQUIRED", description="Template category"),
        bigquery.SchemaField("platform", "STRING", mode="NULLABLE", description="Target platform"),
        bigquery.SchemaField("layout_config", "STRING", mode="NULLABLE", description="JSON layout configuration"),
        bigquery.SchemaField("style_config", "STRING", mode="NULLABLE", description="JSON style configuration"),
        bigquery.SchemaField("is_public", "BOOLEAN", mode="REQUIRED", description="Is template public"),
        bigquery.SchemaField("use_count", "INT64", mode="NULLABLE", description="Number of times used"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED", description="Creation time"),
    ]

    templates_table = bigquery.Table(f"{dataset_ref}.templates", schema=templates_schema)
    try:
        client.create_table(templates_table, exists_ok=True)
        print("✅ Templates table created/verified")
    except Exception as e:
        print(f"❌ Templates table error: {e}")

    # Activity log table
    activity_schema = [
        bigquery.SchemaField("activity_id", "STRING", mode="REQUIRED", description="Unique activity ID"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED", description="User ID"),
        bigquery.SchemaField("action", "STRING", mode="REQUIRED", description="Action type"),
        bigquery.SchemaField("resource_type", "STRING", mode="NULLABLE", description="Resource type: brand, content, template"),
        bigquery.SchemaField("resource_id", "STRING", mode="NULLABLE", description="Resource ID"),
        bigquery.SchemaField("details", "STRING", mode="NULLABLE", description="JSON details"),
        bigquery.SchemaField("ip_address", "STRING", mode="NULLABLE", description="Client IP"),
        bigquery.SchemaField("user_agent", "STRING", mode="NULLABLE", description="Browser user agent"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED", description="Activity time"),
    ]

    activity_table = bigquery.Table(f"{dataset_ref}.activity_log", schema=activity_schema)
    try:
        client.create_table(activity_table, exists_ok=True)
        print("✅ Activity log table created/verified")
    except Exception as e:
        print(f"❌ Activity log table error: {e}")

    print("\n" + "="*50)
    print("MarketingAI BigQuery Schema Setup Complete!")
    print("="*50)

    # Create admin user
    print("\nCreating admin user...")
    import hashlib
    import secrets
    from datetime import datetime

    admin_user_id = secrets.token_hex(16)
    admin_email = "admin@marketingai.cloud"
    admin_password_hash = hashlib.sha256("MarketingAI2025!".encode()).hexdigest()
    now = datetime.utcnow().isoformat()

    insert_admin = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_ID}.users`
        (user_id, email, password_hash, name, company, role, created_at, last_login, is_active, subscription_tier)
        VALUES ('{admin_user_id}', '{admin_email}', '{admin_password_hash}', 'Admin', 'AIAlgoTradeHits', 'admin', '{now}', '{now}', TRUE, 'enterprise')
    """

    try:
        # Check if admin exists
        check_query = f"SELECT email FROM `{PROJECT_ID}.{DATASET_ID}.users` WHERE email = '{admin_email}'"
        results = list(client.query(check_query).result())

        if not results:
            client.query(insert_admin).result()
            print(f"✅ Admin user created: {admin_email}")
            print(f"   Password: MarketingAI2025!")
        else:
            print(f"ℹ️  Admin user already exists: {admin_email}")
    except Exception as e:
        print(f"❌ Admin user error: {e}")

    print("\n✅ Setup complete!")


if __name__ == '__main__':
    setup_schema()
