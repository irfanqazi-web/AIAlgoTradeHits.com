# MarketingAI - Multi-User Social Media Content Creation Platform

**Date:** November 30, 2025
**Status:** DEPLOYED TO CLOUD RUN

## Service URL

https://marketingai-1075463475276.us-central1.run.app

## Application Overview

MarketingAI is a full-featured multi-user social media content creation platform based on the "Content Creation Command Center" artifact. It includes:

### Features

1. **User Authentication**
   - Registration with company name parameter
   - Login with JWT tokens
   - Role-based access (admin/user)
   - Session persistence

2. **Brand Management**
   - Create multiple brands per user
   - Custom color schemes (primary, secondary, accent)
   - Brand themes (modern, professional, playful, minimal, bold)
   - Logo URL support

3. **Content Designer**
   - Platform selector (Instagram, Facebook, YouTube, TikTok)
   - Content types (Carousel, Quote, Tips, etc.)
   - Color scheme selection
   - Font style options
   - Schedule date picker
   - Save as draft or schedule

4. **Templates Library**
   - Educational Carousels
   - Quote & Inspiration
   - Tips & Lists

5. **Content Calendar**
   - View scheduled content
   - Content ideas by category

6. **Dashboard**
   - Statistics overview
   - Recent activity
   - Quick brand access

7. **Workflow Guide**
   - 7-step content creation process
   - Best practices

8. **Tools Reference**
   - Design tools (Canva, Figma, Adobe Express)
   - Scheduling tools (Later, Buffer, Meta Business Suite)

## Application Structure

```
C:/1AITrading/Trading/marketingai_app/
├── Dockerfile              # Cloud Run container config
├── .gcloudignore          # Deploy ignore patterns
├── setup_bigquery_schema.py  # Database setup script
├── deploy_to_cloudrun.py   # Deployment script
├── backend/
│   ├── main.py            # Flask API with all endpoints
│   └── requirements.txt   # Python dependencies
└── frontend/
    └── index.html         # Single-page application
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user (requires name, company, email, password)
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info

### Brands
- `GET /api/brands` - Get user's brands
- `POST /api/brands` - Create new brand
- `PUT /api/brands/<id>` - Update brand
- `DELETE /api/brands/<id>` - Delete brand

### Content
- `GET /api/content` - Get user's content (filters: brand_id, platform, status)
- `POST /api/content` - Create new content
- `PUT /api/content/<id>` - Update content
- `DELETE /api/content/<id>` - Delete content

### Calendar
- `GET /api/calendar` - Get scheduled content for date range

### Templates & Platforms
- `GET /api/templates` - Get available templates
- `GET /api/platforms` - Get platform specifications

### Admin
- `GET /api/admin/users` - Get all users (admin only)
- `GET /api/admin/stats` - Get platform statistics (admin only)

## BigQuery Schema

**Dataset:** `aialgotradehits.marketingai_data`

**Tables:**
- `users` - User accounts with company name
- `brands` - Brand configurations
- `content` - Content items
- `templates` - Custom templates
- `activity_log` - User activity tracking

## Post-Deployment Steps

### 1. Enable Public Access (Required)

Log in as irfan.qazi@aialgotradehits.com and run:

```bash
gcloud beta run services add-iam-policy-binding \
    --region=us-central1 \
    --member=allUsers \
    --role=roles/run.invoker \
    marketingai \
    --project=aialgotradehits
```

Or via GCP Console:
1. Go to Cloud Run > marketingai
2. Click "Security" tab
3. Check "Allow unauthenticated invocations"

### 2. Create BigQuery Schema

From GCP Cloud Shell (logged in as irfan.qazi@aialgotradehits.com):

```bash
# Upload and run schema setup
gsutil cp gs://your-bucket/setup_bigquery_schema.py .
python setup_bigquery_schema.py
```

Or create manually in BigQuery console with the schema defined in `setup_bigquery_schema.py`

### 3. Admin User Credentials (After Schema Setup)

- **Email:** admin@marketingai.cloud
- **Password:** MarketingAI2025!
- **Role:** admin

## Technologies Used

- **Backend:** Python Flask
- **Database:** Google BigQuery
- **Auth:** JWT tokens with SHA-256 password hashing
- **Frontend:** Vanilla JavaScript SPA
- **Hosting:** Google Cloud Run
- **Container:** Python 3.11 slim + Gunicorn

## Company Integration

The platform supports company/organization name as a registration parameter. Users can:
- Register with their company name
- See company name in header
- Brand management per organization

## Estimated Costs

- Cloud Run: ~$5-10/month (depends on usage)
- BigQuery: ~$1-2/month (storage)
- Total: ~$7-12/month

---

## REMINDER

**Cancel Claude Max Plan by December 6, 2025**
- Personal account: haq.irfanul@gmail.com
- Billing page: https://claude.ai/settings/billing

---

*MarketingAI created and deployed by Claude Code*
*November 30, 2025*
