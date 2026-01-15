# IRS CPIC Management System - Deployment Complete

**Date:** November 30, 2025
**Status:** DEPLOYED TO CLOUD RUN

## Service URL

**https://irs-cpic-1075463475276.us-central1.run.app**

## Application Overview

The IRS CPIC (Capital Planning & Investment Control) Management System is a comprehensive multi-user application for managing federal IT investments. Built from the documentation in `C:\Users\irfan\OneDrive\Khaja\IRS`.

### Features

1. **User Authentication & Authorization**
   - Multi-role system: Admin, CIO, Coordinating Director, Portfolio Manager, Investment Coordinator
   - Organization-based access
   - JWT token authentication

2. **Investment Management**
   - Create new investments (4-step workflow)
   - Track UII (Unique Investment Identifier): 015-XXXXXXXXX format
   - Investment types: Major IT, Non-Major IT, Non-IT
   - Classifications: Major (Part 7), Non-Major (Streamlined)
   - Lifecycle stages: Initiate, Select, Control, Evaluate

3. **Monthly Reports (Due 19th of each month)**
   - Cost performance tracking
   - Schedule variance monitoring
   - Risk assessment (High/Medium/Low)
   - Executive summary
   - Submission workflow with approvals

4. **Dashboard & Analytics**
   - Portfolio overview statistics
   - Investment health status (Green/Yellow/Red)
   - Budget tracking
   - Deadline countdown

5. **SPIKE Tool Integration**
   - Treasury's SharePoint Investment Knowledge Exchange
   - Sync status tracking
   - Federal IT Dashboard reporting

6. **Calendar & Deadlines**
   - CPIC reporting calendar
   - Baseline approval tracking
   - Review meeting schedules

## Application Structure

```
C:/1AITrading/Trading/irs_cpic_app/
├── Dockerfile
├── .gcloudignore
├── setup_bigquery_schema.py
├── backend/
│   ├── main.py                 # Flask API
│   └── requirements.txt        # Python dependencies
└── frontend/
    └── index.html              # CPIC Management UI
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Investments
- `GET /api/investments` - List investments
- `POST /api/investments` - Create investment
- `GET /api/investments/<id>` - Get investment details
- `PUT /api/investments/<id>` - Update investment

### Monthly Reports
- `GET /api/monthly-reports` - List reports
- `POST /api/monthly-reports` - Create report

### Dashboard
- `GET /api/dashboard/stats` - Get statistics

### Calendar
- `GET /api/calendar/events` - Get calendar events

### SPIKE
- `GET /api/spike/status` - Get SPIKE sync status

### Admin
- `GET /api/admin/users` - List all users
- `POST /api/admin/approve-investment/<id>` - Approve investment

## BigQuery Schema

**Dataset:** `aialgotradehits.cpic_data`

**Tables:**
- `users` - User accounts and roles
- `investments` - Investment portfolio
- `monthly_reports` - Monthly status reports
- `projects` - Investment projects
- `risks` - Risk tracking

## User Roles

| Role | Permissions |
|------|-------------|
| admin | Full access, user management |
| cio | View all, approve investments |
| coordinating_director | Approve investments, view all |
| portfolio_manager | Manage assigned investments |
| investment_coordinator | Edit assigned investments |

## Default Users (After Schema Setup)

| Email | Password | Role |
|-------|----------|------|
| admin@irs.gov | CPIC2025Admin! | admin |
| khaja.syed@irs.gov | Portfolio2025! | portfolio_manager |

## Post-Deployment Steps

### 1. Enable Public Access

Log in as irfan.qazi@aialgotradehits.com:
1. Go to Cloud Run > irs-cpic
2. Click "Security" tab
3. Check "Allow unauthenticated invocations"

Or run:
```bash
gcloud beta run services add-iam-policy-binding \
    --region=us-central1 \
    --member=allUsers \
    --role=roles/run.invoker \
    irs-cpic \
    --project=aialgotradehits
```

### 2. Create BigQuery Schema

From GCP Cloud Shell:
```bash
python setup_bigquery_schema.py
```

## Source Documentation

The app was built using documentation from:
- `C:\Users\irfan\OneDrive\Khaja\IRS\`
- IRS CPIC - Detailed Workflow Specifications.pdf
- IRS CPIC - Detailed Form Templates & Field Specifications.pdf
- IRS CPIC - Developer Handoff Document.pdf
- Treasury CPIC Briefing.pdf
- full-operational-cpic-app.html
- irs-cpic-complete-system.tsx

## CPIC Reporting Timeline

1. **15th of month** - Data collection deadline
2. **17th of month** - Portfolio Manager review
3. **18th of month** - CIO review & comments
4. **19th of month** - Reports due to Treasury

---

## REMINDER

**Cancel Claude Max Plan by December 6, 2025**
- Personal account: haq.irfanul@gmail.com
- Billing page: https://claude.ai/settings/billing

---

*IRS CPIC Management System created and deployed by Claude Code*
*November 30, 2025*
