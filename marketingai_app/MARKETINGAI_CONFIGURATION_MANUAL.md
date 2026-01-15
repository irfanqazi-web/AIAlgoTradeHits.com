# MarketingAI Platform - Configuration Manual

**Version:** 1.0
**GCP Project:** aialgotradehits (ID: 1075463475276)
**Last Updated:** December 10, 2025

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Infrastructure Architecture](#infrastructure-architecture)
3. [GCP Setup & Configuration](#gcp-setup--configuration)
4. [BigQuery Database Schema](#bigquery-database-schema)
5. [API Configuration](#api-configuration)
6. [AI Services Integration](#ai-services-integration)
7. [Deployment Procedures](#deployment-procedures)
8. [Environment Variables](#environment-variables)
9. [Security Configuration](#security-configuration)
10. [Monitoring & Logging](#monitoring--logging)
11. [Backup & Recovery](#backup--recovery)
12. [Troubleshooting](#troubleshooting)

---

## System Overview

### Technology Stack

**Backend:**
- Python 3.11
- Flask web framework
- Gunicorn WSGI server
- JWT authentication
- Google Cloud Client Libraries

**Frontend:**
- HTML5 / CSS3 / JavaScript (ES6+)
- Single Page Application (SPA) architecture
- Responsive design (mobile-first)
- No external framework dependencies

**Cloud Platform:**
- Google Cloud Platform (GCP)
- Cloud Run (container orchestration)
- BigQuery (data warehouse)
- Cloud Build (CI/CD)
- Cloud Storage (media files)
- Vertex AI (AI/ML services)

**AI Services:**
- Gemini 2.0 Pro (text generation)
- Imagen 3 (image generation)
- Veo 2 (video generation)
- Natural Language API (sentiment analysis)

### System Requirements

**Development Environment:**
- Python 3.11+
- pip package manager
- Google Cloud SDK
- Git version control
- Code editor (VS Code recommended)

**Production Environment:**
- GCP Project with billing enabled
- Cloud Run API enabled
- BigQuery API enabled
- Vertex AI API enabled
- Cloud Build API enabled

---

## Infrastructure Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Client Layer                           │
│  (Web Browsers, Mobile Devices, API Clients)                 │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                     Cloud Run Service                         │
│  ┌────────────────┐        ┌──────────────────┐             │
│  │  Flask Backend │◄──────►│ Frontend (SPA)   │             │
│  │  (API Endpoints)│        │ (HTML/CSS/JS)    │             │
│  └────────┬───────┘        └──────────────────┘             │
└───────────┼──────────────────────────────────────────────────┘
            │
            │ API Calls
            ▼
┌──────────────────────────────────────────────────────────────┐
│                    GCP Services Layer                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  BigQuery   │  │  Vertex AI   │  │Cloud Storage │       │
│  │  (Database) │  │  (AI Models) │  │   (Media)    │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

### Component Details

**Cloud Run Service:**
- Region: us-central1
- Service Name: marketingai
- Min Instances: 0 (scales to zero)
- Max Instances: 10
- CPU: 1
- Memory: 512 MB
- Timeout: 300 seconds
- Port: 8080
- Concurrency: 80 requests per instance

**BigQuery Dataset:**
- Project: aialgotradehits
- Dataset: marketingai_data
- Location: US (multi-region)
- Tables: users, brands, content, scheduled_posts, campaigns, analytics_events

**Cloud Storage Bucket:**
- Bucket Name: marketingai-media-aialgotradehits
- Location: us-central1
- Storage Class: Standard
- Public Access: Disabled
- Uniform bucket-level access: Enabled

---

## GCP Setup & Configuration

### Initial GCP Project Setup

**Step 1: Create GCP Project**
```bash
# Already created: aialgotradehits (ID: 1075463475276)
gcloud config set project aialgotradehits
```

**Step 2: Enable Required APIs**
```bash
# Enable Cloud Run
gcloud services enable run.googleapis.com

# Enable BigQuery
gcloud services enable bigquery.googleapis.com

# Enable Vertex AI
gcloud services enable aiplatform.googleapis.com

# Enable Cloud Build
gcloud services enable cloudbuild.googleapis.com

# Enable Cloud Storage
gcloud services enable storage-api.googleapis.com

# Enable Natural Language API
gcloud services enable language.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled
```

**Step 3: Set Up Service Account**
```bash
# Create service account for MarketingAI
gcloud iam service-accounts create marketingai-sa \
    --description="MarketingAI Platform Service Account" \
    --display-name="MarketingAI Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding aialgotradehits \
    --member="serviceAccount:marketingai-sa@aialgotradehits.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding aialgotradehits \
    --member="serviceAccount:marketingai-sa@aialgotradehits.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding aialgotradehits \
    --member="serviceAccount:marketingai-sa@aialgotradehits.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

**Step 4: Create Service Account Key**
```bash
gcloud iam service-accounts keys create marketingai-key.json \
    --iam-account=marketingai-sa@aialgotradehits.iam.gserviceaccount.com

# Store key securely and reference in environment variables
```

### BigQuery Setup

**Step 1: Create Dataset**
```bash
bq mk --dataset \
    --location=US \
    --description="MarketingAI Platform Data" \
    aialgotradehits:marketingai_data
```

**Step 2: Set Data Retention Policy**
```bash
bq update --default_table_expiration=31536000 \
    aialgotradehits:marketingai_data
# 31536000 seconds = 365 days
```

**Step 3: Configure Access Controls**
```bash
# Grant service account access
bq update --dataset \
    --set_label environment:production \
    aialgotradehits:marketingai_data
```

### Cloud Storage Setup

**Step 1: Create Storage Bucket**
```bash
gsutil mb -p aialgotradehits \
    -c STANDARD \
    -l us-central1 \
    gs://marketingai-media-aialgotradehits/
```

**Step 2: Set Bucket Permissions**
```bash
# Enable uniform bucket-level access
gsutil uniformbucketlevelaccess set on gs://marketingai-media-aialgotradehits/

# Grant service account access
gsutil iam ch serviceAccount:marketingai-sa@aialgotradehits.iam.gserviceaccount.com:objectAdmin \
    gs://marketingai-media-aialgotradehits/
```

**Step 3: Configure CORS (if needed)**
```bash
# Create cors.json file
cat > cors.json <<EOF
[
  {
    "origin": ["https://marketingai-1075463475276.us-central1.run.app"],
    "method": ["GET", "POST", "PUT", "DELETE"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF

# Apply CORS configuration
gsutil cors set cors.json gs://marketingai-media-aialgotradehits/
```

---

## BigQuery Database Schema

### Dataset Structure

**Dataset Name:** marketingai_data
**Location:** US (multi-region)
**Tables:** 6 primary tables

### Table: users

**Purpose:** Store user account information

**Schema:**
```sql
CREATE TABLE `aialgotradehits.marketingai_data.users` (
    user_id STRING NOT NULL,
    email STRING NOT NULL,
    password_hash STRING NOT NULL,
    name STRING,
    role STRING NOT NULL DEFAULT 'user',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    last_login TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    settings JSON
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

**Field Descriptions:**
- `user_id`: Unique identifier (UUID)
- `email`: User email (unique, used for login)
- `password_hash`: Bcrypt hashed password
- `name`: User display name
- `role`: User role (admin, user, viewer)
- `created_at`: Account creation timestamp
- `last_login`: Last successful login
- `is_active`: Account status (active/deactivated)
- `settings`: User preferences (JSON)

**Sample Query:**
```sql
-- Get all active users
SELECT user_id, email, name, role, last_login
FROM `aialgotradehits.marketingai_data.users`
WHERE is_active = TRUE
ORDER BY last_login DESC;
```

### Table: brands

**Purpose:** Store brand profiles and settings

**Schema:**
```sql
CREATE TABLE `aialgotradehits.marketingai_data.brands` (
    brand_id STRING NOT NULL,
    user_id STRING NOT NULL,
    brand_name STRING NOT NULL,
    industry STRING,
    target_audience STRING,
    brand_voice STRING DEFAULT 'professional',
    keywords ARRAY<STRING>,
    website_url STRING,
    social_media JSON,
    brand_colors JSON,
    logo_url STRING,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Indexes
CREATE INDEX idx_brands_user ON brands(user_id);
CREATE INDEX idx_brands_name ON brands(brand_name);
```

**Field Descriptions:**
- `brand_id`: Unique identifier (UUID)
- `user_id`: Foreign key to users table
- `brand_name`: Brand display name
- `industry`: Industry category
- `target_audience`: Audience description
- `brand_voice`: Tone (casual, professional, friendly, authoritative)
- `keywords`: Array of brand keywords
- `website_url`: Brand website
- `social_media`: Social media handles (JSON)
- `brand_colors`: Primary/secondary colors (JSON)
- `logo_url`: Brand logo URL
- `created_at`: Brand creation timestamp
- `updated_at`: Last update timestamp
- `is_active`: Brand status

**Sample Query:**
```sql
-- Get all brands for a user
SELECT brand_id, brand_name, industry, brand_voice, created_at
FROM `aialgotradehits.marketingai_data.brands`
WHERE user_id = 'USER_ID_HERE'
  AND is_active = TRUE
ORDER BY created_at DESC;
```

### Table: content

**Purpose:** Store all generated content

**Schema:**
```sql
CREATE TABLE `aialgotradehits.marketingai_data.content` (
    content_id STRING NOT NULL,
    brand_id STRING NOT NULL,
    user_id STRING NOT NULL,
    content_type STRING NOT NULL,
    title STRING,
    body TEXT NOT NULL,
    platform STRING,
    media_urls ARRAY<STRING>,
    hashtags ARRAY<STRING>,
    keywords ARRAY<STRING>,
    tone STRING,
    status STRING NOT NULL DEFAULT 'draft',
    ai_model_used STRING,
    generation_params JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    published_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_content_brand ON content(brand_id);
CREATE INDEX idx_content_type ON content(content_type);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_created ON content(created_at DESC);
```

**Field Descriptions:**
- `content_id`: Unique identifier (UUID)
- `brand_id`: Foreign key to brands table
- `user_id`: Foreign key to users table
- `content_type`: Type (social_post, blog_article, email, ad_copy)
- `title`: Content title/headline
- `body`: Main content text
- `platform`: Target platform (twitter, facebook, instagram, linkedin)
- `media_urls`: Array of image/video URLs
- `hashtags`: Array of hashtags
- `keywords`: Array of SEO keywords
- `tone`: Content tone
- `status`: Status (draft, scheduled, published, failed)
- `ai_model_used`: AI model name
- `generation_params`: AI generation parameters (JSON)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `published_at`: Publication timestamp

**Sample Query:**
```sql
-- Get all published content for a brand
SELECT content_id, title, content_type, platform, published_at
FROM `aialgotradehits.marketingai_data.content`
WHERE brand_id = 'BRAND_ID_HERE'
  AND status = 'published'
ORDER BY published_at DESC
LIMIT 20;
```

### Table: scheduled_posts

**Purpose:** Content scheduling and calendar

**Schema:**
```sql
CREATE TABLE `aialgotradehits.marketingai_data.scheduled_posts` (
    schedule_id STRING NOT NULL,
    content_id STRING NOT NULL,
    brand_id STRING NOT NULL,
    user_id STRING NOT NULL,
    platform STRING NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    timezone STRING NOT NULL DEFAULT 'America/New_York',
    status STRING NOT NULL DEFAULT 'scheduled',
    published_at TIMESTAMP,
    error_message STRING,
    retry_count INT64 DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- Indexes
CREATE INDEX idx_scheduled_brand ON scheduled_posts(brand_id);
CREATE INDEX idx_scheduled_time ON scheduled_posts(scheduled_time);
CREATE INDEX idx_scheduled_status ON scheduled_posts(status);
```

**Field Descriptions:**
- `schedule_id`: Unique identifier (UUID)
- `content_id`: Foreign key to content table
- `brand_id`: Foreign key to brands table
- `user_id`: Foreign key to users table
- `platform`: Publishing platform
- `scheduled_time`: When to publish
- `timezone`: User timezone
- `status`: Status (scheduled, published, failed, cancelled)
- `published_at`: Actual publication time
- `error_message`: Error details if failed
- `retry_count`: Number of retry attempts
- `created_at`: Schedule creation timestamp
- `updated_at`: Last update timestamp

**Sample Query:**
```sql
-- Get upcoming scheduled posts for today
SELECT s.schedule_id, c.title, s.platform, s.scheduled_time
FROM `aialgotradehits.marketingai_data.scheduled_posts` s
JOIN `aialgotradehits.marketingai_data.content` c ON s.content_id = c.content_id
WHERE DATE(s.scheduled_time) = CURRENT_DATE()
  AND s.status = 'scheduled'
ORDER BY s.scheduled_time ASC;
```

### Table: campaigns

**Purpose:** Campaign management and tracking

**Schema:**
```sql
CREATE TABLE `aialgotradehits.marketingai_data.campaigns` (
    campaign_id STRING NOT NULL,
    brand_id STRING NOT NULL,
    user_id STRING NOT NULL,
    campaign_name STRING NOT NULL,
    campaign_goal STRING NOT NULL,
    platforms ARRAY<STRING>,
    start_date DATE NOT NULL,
    end_date DATE,
    budget FLOAT64,
    target_audience STRING,
    content_themes ARRAY<STRING>,
    status STRING NOT NULL DEFAULT 'draft',
    total_impressions INT64 DEFAULT 0,
    total_reach INT64 DEFAULT 0,
    total_engagement INT64 DEFAULT 0,
    total_conversions INT64 DEFAULT 0,
    total_spend FLOAT64 DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- Indexes
CREATE INDEX idx_campaigns_brand ON campaigns(brand_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_dates ON campaigns(start_date, end_date);
```

**Field Descriptions:**
- `campaign_id`: Unique identifier (UUID)
- `brand_id`: Foreign key to brands table
- `user_id`: Foreign key to users table
- `campaign_name`: Campaign name
- `campaign_goal`: Goal (awareness, leads, sales, engagement)
- `platforms`: Array of platforms
- `start_date`: Campaign start date
- `end_date`: Campaign end date
- `budget`: Total budget
- `target_audience`: Audience description
- `content_themes`: Array of content themes
- `status`: Status (draft, active, paused, completed)
- `total_impressions`: Cumulative impressions
- `total_reach`: Cumulative reach
- `total_engagement`: Cumulative engagement
- `total_conversions`: Cumulative conversions
- `total_spend`: Cumulative spend
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Sample Query:**
```sql
-- Get active campaigns with performance metrics
SELECT
    campaign_id,
    campaign_name,
    campaign_goal,
    total_impressions,
    total_reach,
    total_engagement,
    ROUND(total_engagement / total_reach * 100, 2) as engagement_rate
FROM `aialgotradehits.marketingai_data.campaigns`
WHERE status = 'active'
  AND end_date >= CURRENT_DATE()
ORDER BY total_engagement DESC;
```

### Table: analytics_events

**Purpose:** Track user interactions and performance events

**Schema:**
```sql
CREATE TABLE `aialgotradehits.marketingai_data.analytics_events` (
    event_id STRING NOT NULL,
    event_type STRING NOT NULL,
    brand_id STRING,
    content_id STRING,
    campaign_id STRING,
    platform STRING,
    metric_name STRING NOT NULL,
    metric_value FLOAT64 NOT NULL,
    metadata JSON,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- Partitioning by date for performance
CREATE TABLE IF NOT EXISTS `aialgotradehits.marketingai_data.analytics_events`
PARTITION BY DATE(timestamp);

-- Indexes
CREATE INDEX idx_events_type ON analytics_events(event_type);
CREATE INDEX idx_events_content ON analytics_events(content_id);
CREATE INDEX idx_events_timestamp ON analytics_events(timestamp DESC);
```

**Field Descriptions:**
- `event_id`: Unique identifier (UUID)
- `event_type`: Event type (impression, click, share, like, comment, conversion)
- `brand_id`: Foreign key to brands table
- `content_id`: Foreign key to content table
- `campaign_id`: Foreign key to campaigns table
- `platform`: Platform where event occurred
- `metric_name`: Metric name
- `metric_value`: Metric value
- `metadata`: Additional event data (JSON)
- `timestamp`: Event timestamp

**Sample Query:**
```sql
-- Get engagement metrics for last 7 days
SELECT
    event_type,
    COUNT(*) as event_count,
    SUM(metric_value) as total_value
FROM `aialgotradehits.marketingai_data.analytics_events`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND event_type IN ('like', 'comment', 'share')
GROUP BY event_type
ORDER BY total_value DESC;
```

### Database Initialization Script

**File:** `backend/init_database.py`

```python
from google.cloud import bigquery

def create_all_tables(project_id='aialgotradehits', dataset_id='marketingai_data'):
    """Create all MarketingAI BigQuery tables"""

    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id)

    # Table schemas
    tables = {
        'users': [
            bigquery.SchemaField('user_id', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('email', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('password_hash', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('name', 'STRING'),
            bigquery.SchemaField('role', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('created_at', 'TIMESTAMP', mode='REQUIRED'),
            bigquery.SchemaField('last_login', 'TIMESTAMP'),
            bigquery.SchemaField('is_active', 'BOOLEAN', mode='REQUIRED'),
            bigquery.SchemaField('settings', 'JSON')
        ],
        'brands': [
            bigquery.SchemaField('brand_id', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('user_id', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('brand_name', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('industry', 'STRING'),
            bigquery.SchemaField('target_audience', 'STRING'),
            bigquery.SchemaField('brand_voice', 'STRING'),
            bigquery.SchemaField('keywords', 'STRING', mode='REPEATED'),
            bigquery.SchemaField('website_url', 'STRING'),
            bigquery.SchemaField('social_media', 'JSON'),
            bigquery.SchemaField('brand_colors', 'JSON'),
            bigquery.SchemaField('logo_url', 'STRING'),
            bigquery.SchemaField('created_at', 'TIMESTAMP', mode='REQUIRED'),
            bigquery.SchemaField('updated_at', 'TIMESTAMP', mode='REQUIRED'),
            bigquery.SchemaField('is_active', 'BOOLEAN', mode='REQUIRED')
        ],
        # ... (other tables)
    }

    for table_name, schema in tables.items():
        table_ref = dataset_ref.table(table_name)
        table = bigquery.Table(table_ref, schema=schema)

        try:
            client.create_table(table)
            print(f"Created table: {table_name}")
        except Exception as e:
            print(f"Table {table_name} already exists or error: {e}")

if __name__ == '__main__':
    create_all_tables()
```

---

## API Configuration

### API Endpoints

**Base URL:** `https://marketingai-1075463475276.us-central1.run.app`

### Authentication Endpoints

**POST /api/login**
- Description: User login
- Request Body:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- Response:
  ```json
  {
    "success": true,
    "token": "JWT_TOKEN_HERE",
    "user": {
      "id": "user_id",
      "email": "user@example.com",
      "name": "User Name",
      "role": "user"
    }
  }
  ```

**POST /api/logout**
- Description: User logout
- Headers: `Authorization: Bearer JWT_TOKEN`
- Response:
  ```json
  {
    "success": true,
    "message": "Logged out successfully"
  }
  ```

**POST /api/register**
- Description: Create new user account (admin only)
- Headers: `Authorization: Bearer JWT_TOKEN`
- Request Body:
  ```json
  {
    "email": "newuser@example.com",
    "password": "password123",
    "name": "New User",
    "role": "user"
  }
  ```

### Brand Management Endpoints

**GET /api/brands**
- Description: Get all brands for user
- Headers: `Authorization: Bearer JWT_TOKEN`
- Response:
  ```json
  {
    "success": true,
    "brands": [
      {
        "brand_id": "brand_123",
        "brand_name": "My Brand",
        "industry": "Technology",
        "brand_voice": "professional",
        "created_at": "2025-12-10T10:00:00Z"
      }
    ]
  }
  ```

**POST /api/brands**
- Description: Create new brand
- Headers: `Authorization: Bearer JWT_TOKEN`
- Request Body:
  ```json
  {
    "brand_name": "New Brand",
    "industry": "Retail",
    "target_audience": "Young adults 18-35",
    "brand_voice": "casual",
    "keywords": ["fashion", "sustainable", "trendy"]
  }
  ```

**PUT /api/brands/{brand_id}**
- Description: Update brand
- Headers: `Authorization: Bearer JWT_TOKEN`
- Request Body: Same as POST /api/brands

**DELETE /api/brands/{brand_id}**
- Description: Delete brand
- Headers: `Authorization: Bearer JWT_TOKEN`

### Content Creation Endpoints

**POST /api/content/generate**
- Description: Generate AI content
- Headers: `Authorization: Bearer JWT_TOKEN`
- Request Body:
  ```json
  {
    "brand_id": "brand_123",
    "content_type": "social_post",
    "platform": "twitter",
    "topic": "New product launch",
    "tone": "excited",
    "keywords": ["innovation", "technology"]
  }
  ```
- Response:
  ```json
  {
    "success": true,
    "content": {
      "content_id": "content_456",
      "title": "Generated Title",
      "body": "Generated content text...",
      "variations": [
        "Variation 1...",
        "Variation 2...",
        "Variation 3..."
      ]
    }
  }
  ```

**POST /api/content/image/generate**
- Description: Generate AI image
- Headers: `Authorization: Bearer JWT_TOKEN`
- Request Body:
  ```json
  {
    "prompt": "Modern office workspace with laptop",
    "style": "photorealistic",
    "aspect_ratio": "square"
  }
  ```

**POST /api/content/video/generate**
- Description: Generate AI video
- Headers: `Authorization: Bearer JWT_TOKEN`
- Request Body:
  ```json
  {
    "script": "Video script here...",
    "duration": 30,
    "style": "professional"
  }
  ```

**GET /api/content**
- Description: Get all content for user
- Headers: `Authorization: Bearer JWT_TOKEN`
- Query Parameters:
  - `brand_id` (optional): Filter by brand
  - `content_type` (optional): Filter by type
  - `status` (optional): Filter by status
  - `limit` (optional): Results limit (default 20)
  - `offset` (optional): Pagination offset

### Scheduling Endpoints

**POST /api/schedule**
- Description: Schedule content for publishing
- Headers: `Authorization: Bearer JWT_TOKEN`
- Request Body:
  ```json
  {
    "content_id": "content_456",
    "platform": "twitter",
    "scheduled_time": "2025-12-15T14:00:00Z",
    "timezone": "America/New_York"
  }
  ```

**GET /api/schedule/calendar**
- Description: Get scheduled content calendar
- Headers: `Authorization: Bearer JWT_TOKEN`
- Query Parameters:
  - `start_date`: Calendar start date (YYYY-MM-DD)
  - `end_date`: Calendar end date (YYYY-MM-DD)
  - `brand_id` (optional): Filter by brand

**DELETE /api/schedule/{schedule_id}**
- Description: Cancel scheduled post
- Headers: `Authorization: Bearer JWT_TOKEN`

### Campaign Endpoints

**POST /api/campaigns**
- Description: Create new campaign
- Headers: `Authorization: Bearer JWT_TOKEN`
- Request Body:
  ```json
  {
    "brand_id": "brand_123",
    "campaign_name": "Holiday Sale 2025",
    "campaign_goal": "sales",
    "platforms": ["facebook", "instagram"],
    "start_date": "2025-12-15",
    "end_date": "2025-12-31",
    "budget": 5000
  }
  ```

**GET /api/campaigns/{campaign_id}/analytics**
- Description: Get campaign analytics
- Headers: `Authorization: Bearer JWT_TOKEN`

### Analytics Endpoints

**GET /api/analytics/dashboard**
- Description: Get dashboard analytics
- Headers: `Authorization: Bearer JWT_TOKEN`
- Query Parameters:
  - `start_date`: Analysis start date
  - `end_date`: Analysis end date
  - `brand_id` (optional): Filter by brand

**GET /api/analytics/content/{content_id}**
- Description: Get specific content analytics
- Headers: `Authorization: Bearer JWT_TOKEN`

### API Rate Limiting

**Current Limits:**
- 100 requests per minute per user
- 10 AI generation requests per minute per user
- 5 video generation requests per hour per user

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1702234567
```

**Rate Limit Response (429):**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 45
}
```

---

## AI Services Integration

### Gemini 2.0 Pro Configuration

**Purpose:** Text generation for content creation

**Model:** `gemini-2.0-pro`
**Location:** us-central1

**Configuration File:** `backend/ai_services.py`

```python
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel

# Initialize Vertex AI
aiplatform.init(
    project='aialgotradehits',
    location='us-central1'
)

# Gemini model configuration
gemini_config = {
    'temperature': 0.8,
    'top_p': 0.95,
    'top_k': 40,
    'max_output_tokens': 2048,
}

def generate_content(prompt, model_name='gemini-2.0-pro'):
    """Generate content using Gemini"""
    model = GenerativeModel(model_name)

    response = model.generate_content(
        prompt,
        generation_config=gemini_config
    )

    return response.text
```

**Temperature Settings:**
- Social Posts: 0.8 (creative)
- Blog Articles: 0.7 (balanced)
- Email Campaigns: 0.6 (professional)
- Ad Copy: 0.9 (very creative)

### Imagen 3 Configuration

**Purpose:** Image generation

**Model:** `imagegeneration@006`

**Configuration:**
```python
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

def generate_image(prompt, aspect_ratio='square'):
    """Generate image using Imagen 3"""

    model = ImageGenerationModel.from_pretrained("imagegeneration@006")

    response = model.generate_images(
        prompt=prompt,
        number_of_images=4,
        aspect_ratio=aspect_ratio,  # square, landscape, portrait
        safety_filter_level="block_some",
        person_generation="allow_all"
    )

    return [img.url for img in response.images]
```

**Aspect Ratios:**
- `square`: 1:1 (1080x1080)
- `landscape`: 16:9 (1920x1080)
- `portrait`: 9:16 (1080x1920)

### Veo 2 Configuration

**Purpose:** Video generation

**Model:** `veo-2`

**Configuration:**
```python
from vertexai.preview.vision_models import VideoGenerationModel

def generate_video(prompt, duration=30):
    """Generate video using Veo 2"""

    model = VideoGenerationModel.from_pretrained("veo-2")

    response = model.generate_video(
        prompt=prompt,
        duration=duration,  # seconds
        resolution="1080p",
        fps=30
    )

    return response.video_url
```

**Video Specifications:**
- Resolution: 1080p (1920x1080)
- Frame Rate: 30 FPS
- Duration: 6-60 seconds
- Format: MP4

### Natural Language API Configuration

**Purpose:** Sentiment analysis and entity extraction

**Configuration:**
```python
from google.cloud import language_v1

def analyze_sentiment(text):
    """Analyze sentiment using Natural Language API"""

    client = language_v1.LanguageServiceClient()

    document = language_v1.Document(
        content=text,
        type_=language_v1.Document.Type.PLAIN_TEXT
    )

    sentiment = client.analyze_sentiment(
        request={'document': document}
    ).document_sentiment

    return {
        'score': sentiment.score,  # -1.0 to 1.0
        'magnitude': sentiment.magnitude
    }
```

### Cost Management

**Daily Budget Limits:**
- Gemini: $50/day
- Imagen: $30/day
- Veo: $20/day

**Monitoring:**
```python
# Track AI usage
def log_ai_usage(model, tokens, cost):
    """Log AI service usage to BigQuery"""
    from google.cloud import bigquery

    client = bigquery.Client()
    table_id = 'aialgotradehits.marketingai_data.ai_usage'

    rows_to_insert = [{
        'timestamp': datetime.utcnow().isoformat(),
        'model': model,
        'tokens': tokens,
        'cost': cost
    }]

    client.insert_rows_json(table_id, rows_to_insert)
```

---

## Deployment Procedures

### Local Development Setup

**Step 1: Clone Repository**
```bash
cd C:\1AITrading\Trading\marketingai_app
```

**Step 2: Create Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

**Step 3: Install Dependencies**
```bash
pip install -r backend/requirements.txt
```

**Step 4: Set Environment Variables**
```bash
# Create .env file
cat > .env <<EOF
GOOGLE_CLOUD_PROJECT=aialgotradehits
BIGQUERY_DATASET=marketingai_data
JWT_SECRET_KEY=your-secret-key-here
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
ENV=development
EOF
```

**Step 5: Run Development Server**
```bash
cd backend
python main.py
# Server runs on http://localhost:8080
```

### Production Deployment to Cloud Run

**Method 1: Deploy from Source**

```bash
cd C:\1AITrading\Trading\marketingai_app

# Deploy to Cloud Run
gcloud run deploy marketingai \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars GOOGLE_CLOUD_PROJECT=aialgotradehits,BIGQUERY_DATASET=marketingai_data,ENV=production \
    --service-account marketingai-sa@aialgotradehits.iam.gserviceaccount.com \
    --project aialgotradehits
```

**Method 2: Deploy with Dockerfile**

**File:** `Dockerfile`

```dockerfile
# Multi-stage build for production
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --user -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Set environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run gunicorn
CMD exec gunicorn --bind :$PORT --workers 2 --threads 8 --timeout 300 backend.main:app
```

**Deploy with Docker:**
```bash
# Build and submit to Cloud Build
gcloud builds submit --tag gcr.io/aialgotradehits/marketingai

# Deploy to Cloud Run
gcloud run deploy marketingai \
    --image gcr.io/aialgotradehits/marketingai \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --project aialgotradehits
```

### Continuous Deployment Setup

**File:** `cloudbuild.yaml`

```yaml
steps:
  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/marketingai', '.']

  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/marketingai']

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'marketingai'
      - '--image'
      - 'gcr.io/$PROJECT_ID/marketingai'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/marketingai'
```

**Trigger Builds:**
```bash
# Manual trigger
gcloud builds submit --config cloudbuild.yaml

# Automatic trigger on git push (setup once)
gcloud builds triggers create github \
    --repo-name=Trading \
    --repo-owner=YOUR_GITHUB_USERNAME \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml \
    --project=aialgotradehits
```

### Deployment Verification

**Step 1: Check Service Status**
```bash
gcloud run services describe marketingai \
    --region us-central1 \
    --project aialgotradehits
```

**Step 2: Test Endpoints**
```bash
# Health check
curl https://marketingai-1075463475276.us-central1.run.app/

# Login test
curl -X POST https://marketingai-1075463475276.us-central1.run.app/api/login \
    -H "Content-Type: application/json" \
    -d '{"email":"waqasulhaq2004@gmail.com","password":"waqas123"}'
```

**Step 3: Monitor Logs**
```bash
gcloud run services logs read marketingai \
    --region us-central1 \
    --project aialgotradehits \
    --limit 50
```

### Rollback Procedure

**Step 1: List Revisions**
```bash
gcloud run revisions list \
    --service marketingai \
    --region us-central1 \
    --project aialgotradehits
```

**Step 2: Rollback to Previous Revision**
```bash
gcloud run services update-traffic marketingai \
    --to-revisions REVISION_NAME=100 \
    --region us-central1 \
    --project aialgotradehits
```

---

## Environment Variables

### Required Variables

**Application Variables:**
```bash
# GCP Configuration
GOOGLE_CLOUD_PROJECT=aialgotradehits
BIGQUERY_DATASET=marketingai_data
CLOUD_STORAGE_BUCKET=marketingai-media-aialgotradehits

# Authentication
JWT_SECRET_KEY=your-long-random-secret-key-here
JWT_EXPIRATION_HOURS=24

# Environment
ENV=production  # or development

# Service Account
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**AI Service Variables:**
```bash
# Vertex AI
VERTEX_AI_LOCATION=us-central1
GEMINI_MODEL=gemini-2.0-pro
IMAGEN_MODEL=imagegeneration@006
VEO_MODEL=veo-2

# AI Generation Limits
MAX_DAILY_GEMINI_CALLS=1000
MAX_DAILY_IMAGEN_CALLS=500
MAX_DAILY_VEO_CALLS=100
```

**Optional Variables:**
```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_AI_PER_MINUTE=10

# Session Management
SESSION_TIMEOUT_HOURS=2
MAX_CONCURRENT_SESSIONS=3
```

### Setting Variables in Cloud Run

**Method 1: via gcloud CLI**
```bash
gcloud run services update marketingai \
    --set-env-vars GOOGLE_CLOUD_PROJECT=aialgotradehits,BIGQUERY_DATASET=marketingai_data,JWT_SECRET_KEY=your-secret \
    --region us-central1 \
    --project aialgotradehits
```

**Method 2: via Console**
1. Go to Cloud Run Console
2. Select `marketingai` service
3. Click "Edit & Deploy New Revision"
4. Go to "Variables & Secrets" tab
5. Add environment variables
6. Click "Deploy"

**Method 3: via YAML**

**File:** `service.yaml`
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: marketingai
spec:
  template:
    spec:
      containers:
        - image: gcr.io/aialgotradehits/marketingai
          env:
            - name: GOOGLE_CLOUD_PROJECT
              value: aialgotradehits
            - name: BIGQUERY_DATASET
              value: marketingai_data
            - name: JWT_SECRET_KEY
              value: your-secret-key
```

```bash
gcloud run services replace service.yaml \
    --region us-central1 \
    --project aialgotradehits
```

---

## Security Configuration

### JWT Authentication

**Configuration:**
```python
import jwt
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps

JWT_SECRET = os.environ.get('JWT_SECRET_KEY')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 24  # hours

def generate_token(user_id, email, role):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401

        token = token.replace('Bearer ', '')
        payload = verify_token(token)

        if not payload:
            return jsonify({'error': 'Invalid token'}), 401

        request.user = payload
        return f(*args, **kwargs)

    return decorated
```

### Password Hashing

**Configuration:**
```python
import bcrypt

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed.encode('utf-8')
    )
```

### CORS Configuration

**Configuration:**
```python
from flask_cors import CORS

app = Flask(__name__)

# Production CORS settings
if os.environ.get('ENV') == 'production':
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "https://marketingai-1075463475276.us-central1.run.app"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
else:
    # Development: Allow all origins
    CORS(app)
```

### API Key Management

**For External Integrations:**

```python
import secrets

def generate_api_key():
    """Generate secure API key"""
    return secrets.token_urlsafe(32)

def verify_api_key(api_key):
    """Verify API key from request"""
    # Query BigQuery for valid API key
    from google.cloud import bigquery
    client = bigquery.Client()

    query = f"""
    SELECT user_id, permissions
    FROM `aialgotradehits.marketingai_data.api_keys`
    WHERE api_key = '{api_key}'
      AND is_active = TRUE
      AND expiration_date > CURRENT_TIMESTAMP()
    """

    results = list(client.query(query))
    return results[0] if results else None
```

### Security Headers

**Configuration:**
```python
from flask import make_response

@app.after_request
def set_security_headers(response):
    """Set security headers"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

### Input Validation

**Configuration:**
```python
from wtforms import Form, StringField, validators

class BrandForm(Form):
    """Brand input validation"""
    brand_name = StringField('Brand Name', [
        validators.Length(min=2, max=100),
        validators.DataRequired()
    ])
    industry = StringField('Industry', [
        validators.Length(max=50)
    ])
    website_url = StringField('Website', [
        validators.URL(),
        validators.Optional()
    ])

def validate_brand_input(data):
    """Validate brand input"""
    form = BrandForm(data=data)
    if not form.validate():
        return {'valid': False, 'errors': form.errors}
    return {'valid': True, 'data': form.data}
```

---

## Monitoring & Logging

### Cloud Logging Setup

**Configuration:**
```python
import google.cloud.logging
from google.cloud.logging import Client

# Initialize logging client
logging_client = Client(project='aialgotradehits')
logging_client.setup_logging()

import logging

# Use standard Python logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Log examples
logger.info('User logged in', extra={'user_id': user_id})
logger.error('Content generation failed', extra={'error': str(e)})
```

### Custom Metrics

**Track Key Metrics:**
```python
from google.cloud import monitoring_v3
import time

def log_metric(metric_type, value, labels=None):
    """Log custom metric to Cloud Monitoring"""

    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/aialgotradehits"

    series = monitoring_v3.TimeSeries()
    series.metric.type = f"custom.googleapis.com/{metric_type}"
    series.resource.type = "cloud_run_revision"

    if labels:
        for key, value in labels.items():
            series.metric.labels[key] = value

    point = monitoring_v3.Point()
    point.value.double_value = value
    point.interval.end_time.seconds = int(time.time())
    series.points = [point]

    client.create_time_series(name=project_name, time_series=[series])

# Usage
log_metric('content_generation_time', 2.5, {'model': 'gemini'})
log_metric('api_requests', 1, {'endpoint': '/api/brands'})
```

### Application Performance Monitoring

**Setup Cloud Trace:**
```python
from google.cloud import trace_v1

tracer = trace_v1.TraceServiceClient()

def trace_function(func):
    """Decorator to trace function execution"""
    def wrapper(*args, **kwargs):
        with tracer.span(name=func.__name__):
            return func(*args, **kwargs)
    return wrapper

@trace_function
def generate_content_with_ai(prompt):
    """Traced content generation"""
    # Function implementation
    pass
```

### Error Tracking

**Error Logging:**
```python
import traceback
from google.cloud import error_reporting

error_client = error_reporting.Client(project='aialgotradehits')

def log_error(error, context=None):
    """Log error to Cloud Error Reporting"""
    error_client.report_exception(
        http_context=context
    )
    logger.error(f"Error: {str(error)}", extra={
        'traceback': traceback.format_exc()
    })

# Usage in exception handler
try:
    generate_ai_content(prompt)
except Exception as e:
    log_error(e, context=request.environ)
    return jsonify({'error': 'Content generation failed'}), 500
```

### Monitoring Dashboard

**Access Dashboards:**
- Cloud Run Metrics: https://console.cloud.google.com/run/detail/us-central1/marketingai
- Cloud Logging: https://console.cloud.google.com/logs/query
- Cloud Trace: https://console.cloud.google.com/traces
- Error Reporting: https://console.cloud.google.com/errors

**Key Metrics to Monitor:**
- Request latency (p50, p95, p99)
- Error rate
- Request count
- CPU utilization
- Memory utilization
- Active instances
- AI service usage and costs

---

## Backup & Recovery

### BigQuery Backup Strategy

**Automated Backups:**
- BigQuery automatically retains data for 7 days (time-travel)
- Daily exports to Cloud Storage for long-term retention

**Export Script:**
```python
from google.cloud import bigquery

def export_table_to_gcs(table_id, bucket_name, destination_filename):
    """Export BigQuery table to Cloud Storage"""

    client = bigquery.Client(project='aialgotradehits')
    destination_uri = f"gs://{bucket_name}/{destination_filename}"

    table_ref = client.dataset('marketingai_data').table(table_id)

    extract_job = client.extract_table(
        table_ref,
        destination_uri,
        location='US'
    )

    extract_job.result()
    print(f"Exported {table_id} to {destination_uri}")

# Run daily backups
tables = ['users', 'brands', 'content', 'scheduled_posts', 'campaigns', 'analytics_events']
bucket = 'marketingai-backups-aialgotradehits'

for table in tables:
    filename = f"backups/{table}/{datetime.now().strftime('%Y-%m-%d')}.json"
    export_table_to_gcs(table, bucket, filename)
```

**Schedule Backup Job:**
```bash
# Create Cloud Scheduler job for daily backups
gcloud scheduler jobs create http bigquery-backup-job \
    --schedule="0 2 * * *" \
    --uri="https://marketingai-1075463475276.us-central1.run.app/api/admin/backup" \
    --http-method=POST \
    --headers="Authorization=Bearer SERVICE_ACCOUNT_TOKEN" \
    --location=us-central1 \
    --project=aialgotradehits
```

### Point-in-Time Recovery

**Restore from Time Travel:**
```sql
-- Restore table to state from 2 days ago
CREATE OR REPLACE TABLE `aialgotradehits.marketingai_data.users` AS
SELECT * FROM `aialgotradehits.marketingai_data.users`
FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY);
```

**Restore from Cloud Storage:**
```python
from google.cloud import bigquery

def restore_table_from_gcs(table_id, bucket_name, source_filename):
    """Restore BigQuery table from Cloud Storage backup"""

    client = bigquery.Client(project='aialgotradehits')
    source_uri = f"gs://{bucket_name}/{source_filename}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    table_ref = client.dataset('marketingai_data').table(table_id)

    load_job = client.load_table_from_uri(
        source_uri,
        table_ref,
        job_config=job_config
    )

    load_job.result()
    print(f"Restored {table_id} from {source_uri}")
```

### Disaster Recovery Plan

**Recovery Time Objective (RTO):** 4 hours
**Recovery Point Objective (RPO):** 24 hours

**Recovery Steps:**
1. Assess extent of data loss
2. Identify last good backup
3. Create new BigQuery dataset (if needed)
4. Restore tables from Cloud Storage
5. Redeploy Cloud Run service
6. Verify data integrity
7. Update DNS (if needed)
8. Notify users of restoration

---

## Troubleshooting

### Common Issues

**Issue: Cloud Run Service Won't Start**

**Symptoms:**
- 503 errors when accessing URL
- Logs show container startup failures

**Solutions:**
```bash
# Check service status
gcloud run services describe marketingai --region us-central1

# View recent logs
gcloud run services logs read marketingai --region us-central1 --limit 100

# Common causes:
# 1. Missing environment variables
# 2. Port mismatch (must be 8080)
# 3. Service account permissions

# Fix environment variables
gcloud run services update marketingai \
    --set-env-vars GOOGLE_CLOUD_PROJECT=aialgotradehits \
    --region us-central1
```

**Issue: BigQuery Access Denied**

**Symptoms:**
- "Access Denied" errors in logs
- Cannot read/write to BigQuery

**Solutions:**
```bash
# Check service account permissions
gcloud projects get-iam-policy aialgotradehits \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:marketingai-sa@aialgotradehits.iam.gserviceaccount.com"

# Grant BigQuery permissions
gcloud projects add-iam-policy-binding aialgotradehits \
    --member="serviceAccount:marketingai-sa@aialgotradehits.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"
```

**Issue: AI Generation Timing Out**

**Symptoms:**
- AI requests fail with timeout errors
- 504 Gateway Timeout

**Solutions:**
```bash
# Increase Cloud Run timeout
gcloud run services update marketingai \
    --timeout 300 \
    --region us-central1

# Check Vertex AI quotas
gcloud ai quotas list --project aialgotradehits

# Review AI service logs
gcloud logging read "resource.type=cloud_run_revision AND textPayload:vertex" \
    --project aialgotradehits \
    --limit 20
```

**Issue: High Costs**

**Symptoms:**
- Unexpected GCP billing charges
- AI usage exceeding budget

**Solutions:**
```bash
# Check AI usage
bq query --use_legacy_sql=false \
"SELECT
  DATE(timestamp) as date,
  model,
  COUNT(*) as calls,
  SUM(cost) as total_cost
FROM \`aialgotradehits.marketingai_data.ai_usage\`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY date, model
ORDER BY date DESC, total_cost DESC"

# Implement usage caps in code
# Set daily budget alerts in GCP Console
```

### Debug Mode

**Enable Debug Logging:**
```python
# In main.py
import logging

if os.environ.get('ENV') == 'development':
    logging.basicConfig(level=logging.DEBUG)
    app.config['DEBUG'] = True
```

**Test Locally:**
```bash
# Set debug environment
export ENV=development
export LOG_LEVEL=DEBUG

# Run Flask development server
python backend/main.py

# Access at http://localhost:8080
```

### Support Contacts

**Technical Support:**
- Email: irfan.qazi@aialgotradehits.com
- Platform: https://marketingai-1075463475276.us-central1.run.app

**Emergency Contacts:**
- Production Issues: irfan.qazi@aialgotradehits.com
- Security Incidents: irfan.qazi@aialgotradehits.com

**Documentation:**
- User Manual: MARKETINGAI_USER_MANUAL.md
- This Configuration Manual
- GCP Documentation: https://cloud.google.com/docs

---

## Appendix

### Service URLs

- Production App: https://marketingai-1075463475276.us-central1.run.app
- Cloud Run Console: https://console.cloud.google.com/run/detail/us-central1/marketingai
- BigQuery Console: https://console.cloud.google.com/bigquery?project=aialgotradehits
- Logs: https://console.cloud.google.com/logs/query?project=aialgotradehits

### Required Permissions

**Service Account Roles:**
- roles/bigquery.dataEditor
- roles/aiplatform.user
- roles/storage.objectAdmin
- roles/logging.logWriter
- roles/cloudtrace.agent

**User Roles:**
- Admin: All permissions
- User: Content creation, brand management
- Viewer: Read-only access

### Version History

**Version 1.0** (December 10, 2025)
- Initial configuration documentation
- Complete GCP setup procedures
- BigQuery schema documentation
- API configuration
- Deployment procedures
- Security configuration
- Monitoring setup
- Backup procedures

---

**Document Maintained By:** AIAlgoTradeHits.com
**Contact:** irfan.qazi@aialgotradehits.com
**Last Updated:** December 10, 2025
