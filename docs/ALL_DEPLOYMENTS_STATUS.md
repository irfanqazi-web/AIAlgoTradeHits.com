# All Domain Sites & MarketingAI - Deployment Status

**Date:** November 30, 2025
**Project:** aialgotradehits (Business Account)

---

## MarketingAI - DEPLOYED ✅

**Service URL:** https://marketingai-1075463475276.us-central1.run.app

Full multi-user social media content creation platform with:
- User registration/login with company name
- Brand management
- Content designer with platform-specific dimensions
- Templates library
- Content calendar
- Dashboard with statistics

**Post-Deployment Required:**
1. Enable public access via GCP Console (Security tab)
2. Create BigQuery schema for user data
3. Default admin: admin@marketingai.cloud / MarketingAI2025!

---

## Enhanced Domain Sites - DEPLOYED ✅

All sites have professional landing pages and were deployed to Cloud Run:

| Domain | Cloud Run URL | Status |
|--------|---------------|--------|
| KaamyabPakistan.org | https://kaamyabpakistan-6pmz2y7ouq-uc.a.run.app | ✅ Deployed |
| YouInvent.Tech | https://youinvent-tech-6pmz2y7ouq-uc.a.run.app | ✅ Deployed |
| HomeFranchise.Biz | https://homefranchise-biz-1075463475276.us-central1.run.app | ✅ Deployed |
| IoTMotorz.com | https://iotmotorz-com-1075463475276.us-central1.run.app | ✅ Deployed |
| NoCodeAI.cloud | https://nocodeai-cloud-6pmz2y7ouq-uc.a.run.app | ✅ Deployed |

---

## Source Code Locations

```
C:/1AITrading/Trading/
├── marketingai_app/        # MarketingAI Platform
│   ├── backend/main.py     # Flask API
│   ├── frontend/index.html # SPA Frontend
│   ├── Dockerfile
│   └── setup_bigquery_schema.py
│
├── kaamyabpakistan_app/    # KaamyabPakistan.org
├── youinvent_app/          # YouInvent.Tech
├── homefranchise_app/      # HomeFranchise.Biz
├── iotmotorz_app/          # IoTMotorz.com
└── nocodeai_app/           # NoCodeAI.cloud
```

---

## Post-Deployment Checklist (GCP Console)

### 1. Enable Public Access for All Services
Log in as irfan.qazi@aialgotradehits.com:
1. Go to Cloud Run in GCP Console
2. For each service:
   - Click on service name
   - Go to "Security" tab
   - Check "Allow unauthenticated invocations"

### 2. Create MarketingAI BigQuery Schema
From Cloud Shell:
```bash
# Clone the setup script and run it
python setup_bigquery_schema.py
```

### 3. Configure Custom Domains
For each domain:
1. Cloud Run > Manage Custom Domains
2. Add domain mapping
3. Update DNS at Interserver.net

---

## DNS Configuration (Interserver.net)

Create CNAME records pointing to Cloud Run URLs:

| Domain | Record Type | Value |
|--------|-------------|-------|
| kaamyabpakistan.org | CNAME | kaamyabpakistan-6pmz2y7ouq-uc.a.run.app |
| youinvent.tech | CNAME | youinvent-tech-6pmz2y7ouq-uc.a.run.app |
| homefranchise.biz | CNAME | homefranchise-biz-*.a.run.app |
| iotmotorz.com | CNAME | iotmotorz-com-*.a.run.app |
| nocodeai.cloud | CNAME | nocodeai-cloud-6pmz2y7ouq-uc.a.run.app |

---

## REMINDER

**Cancel Claude Max Plan by December 6, 2025**
- Personal account: haq.irfanul@gmail.com
- Billing page: https://claude.ai/settings/billing

---

*Sites created and deployed by Claude Code*
*November 30, 2025*
