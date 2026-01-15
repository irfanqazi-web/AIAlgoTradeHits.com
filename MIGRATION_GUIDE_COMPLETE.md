# Complete Migration Guide
## From Personal Account to AIAlgoTradeHits.com Business Account

**Document Version:** 1.0
**Date:** November 29, 2025
**Prepared For:** Irfan Qazi

---

## Executive Summary

This document provides a comprehensive step-by-step guide for migrating all services, subscriptions, and resources from the personal account (haq.irfanul@gmail.com) to the business account (irfan.qazi@aialgotradehits.com).

**Goal:** Consolidate all technology infrastructure under AIAlgoTradeHits.com as the holding company for multiple business ventures.

---

## Current State Assessment

### Accounts Overview

| Account | Email | Purpose | Status |
|---------|-------|---------|--------|
| Personal | haq.irfanul@gmail.com | Current primary | To be retired |
| Business | irfan.qazi@aialgotradehits.com | Future primary | Active |

### Services to Migrate

| Service | Personal Account Status | Business Account Status |
|---------|------------------------|------------------------|
| Google Cloud Platform (GCP) | 5 projects, active billing | 1 project, needs billing |
| Claude AI | Pro subscription | Needs subscription |
| Google Workspace | Gmail (free) | Workspace (paid) |

---

## GCP Projects Inventory

### Projects Under haq.irfanul@gmail.com

| Project ID | Project Name | Cloud Run Services | Schedulers | BigQuery Tables | Action |
|------------|--------------|-------------------|------------|-----------------|--------|
| cryptobot-462709 | Cryptobot | 24 services | 24 jobs | 75+ tables | Migrate |
| molten-optics-310919 | KaamyabPakistan | TBD | TBD | TBD | Migrate |
| fine-effect-271218 | My First Project | 0 | 0 | 0 | Delete |
| vertical-orbit-271201 | My First Project | 0 | 0 | 0 | Delete |

### Projects Under irfan.qazi@aialgotradehits.com

| Project ID | Project Name | Cloud Run Services | Status |
|------------|--------------|-------------------|--------|
| aialgotradehits | aialgotradehits | 4 services | Active |

### Cloud Run Services in cryptobot-462709 (To Migrate)

**Data Fetchers:**
- daily-crypto-fetcher
- hourly-crypto-fetcher
- fivemin-top10-fetcher
- daily-stock-fetcher
- stock-hourly-fetcher
- stock-5min-fetcher
- twelvedata-unified-fetcher
- interest-rates-fetcher

**Weekly Fetchers:**
- weekly-crypto-fetcher
- weekly-stock-fetcher
- weekly-forex-fetcher
- weekly-etf-fetcher
- weekly-indices-fetcher
- weekly-commodities-fetcher

**Applications:**
- crypto-trading-app
- crypto-trading-api
- crypto-app
- crypto-core
- trading-api
- trading-analytics-app
- system-monitoring

**Other Projects:**
- herbalhomeo-api
- herbalhomeo-frontend

### Cloud Schedulers in cryptobot-462709 (24 Jobs)

| Scheduler Name | Schedule | Target |
|---------------|----------|--------|
| daily-crypto-fetch-job | 0 0 * * * | daily-crypto-fetcher |
| hourly-crypto-fetch-job | 0 * * * * | hourly-crypto-fetcher |
| fivemin-top10-fetch-job | */5 * * * * | fivemin-top10-fetcher |
| stock-daily-fetch-job | 0 0 * * * | stock-daily-fetcher |
| stock-hourly-fetch-job | 0 * * * * | stock-hourly-fetcher |
| stock-5min-fetch-job | */5 * * * * | stock-5min-fetcher |
| twelvedata-stocks-daily | 0 6 * * * | twelvedata-unified-fetcher |
| twelvedata-stocks-hourly | 30 * * * * | twelvedata-unified-fetcher |
| twelvedata-crypto-daily | 5 6 * * * | twelvedata-unified-fetcher |
| twelvedata-crypto-hourly | 32 * * * * | twelvedata-unified-fetcher |
| twelvedata-forex-daily | 10 6 * * * | twelvedata-unified-fetcher |
| twelvedata-forex-hourly | 34 * * * * | twelvedata-unified-fetcher |
| twelvedata-etfs-daily | 15 6 * * * | twelvedata-unified-fetcher |
| twelvedata-indices-daily | 20 6 * * * | twelvedata-unified-fetcher |
| twelvedata-commodities-daily | 25 6 * * * | twelvedata-unified-fetcher |
| twelvedata-all-weekly | 0 8 * * 0 | twelvedata-unified-fetcher |
| interest-rates-daily | 0 7 * * * | interest-rates-fetcher |
| interest-rates-hourly | 45 * * * * | interest-rates-fetcher |
| weekly-crypto-fetch-job | 30 4 * * 6 | weekly-crypto-fetcher |
| weekly-stock-fetch-job | 0 4 * * 6 | weekly-stock-fetcher |
| weekly-forex-fetch-job | 30 5 * * 6 | weekly-forex-fetcher |
| weekly-etf-fetch-job | 0 5 * * 6 | weekly-etf-fetcher |
| weekly-indices-fetch-job | 0 6 * * 6 | weekly-indices-fetcher |
| weekly-commodities-fetch-job | 30 6 * * 6 | weekly-commodities-fetcher |

---

## Phase 1: Prepare AIAlgoTradeHits.com Environment

### Step 1.1: Login to Business Account

```bash
# Open terminal/command prompt
gcloud auth login irfan.qazi@aialgotradehits.com

# Set as default account
gcloud config set account irfan.qazi@aialgotradehits.com

# Set default project
gcloud config set project aialgotradehits

# Verify
gcloud config list
```

### Step 1.2: Enable Required GCP APIs

```bash
# Enable all required APIs
gcloud services enable cloudresourcemanager.googleapis.com --project=aialgotradehits
gcloud services enable bigquery.googleapis.com --project=aialgotradehits
gcloud services enable run.googleapis.com --project=aialgotradehits
gcloud services enable cloudfunctions.googleapis.com --project=aialgotradehits
gcloud services enable cloudscheduler.googleapis.com --project=aialgotradehits
gcloud services enable aiplatform.googleapis.com --project=aialgotradehits
gcloud services enable storage.googleapis.com --project=aialgotradehits
gcloud services enable secretmanager.googleapis.com --project=aialgotradehits
```

### Step 1.3: Set Up Billing

1. Go to: https://console.cloud.google.com/billing?project=aialgotradehits
2. Click "Link a billing account"
3. Create new billing account if needed:
   - Account name: AIAlgoTradeHits Billing
   - Country: United States (or your country)
   - Payment method: Add credit card
4. Link to aialgotradehits project

### Step 1.4: Add Personal Account as Collaborator (Temporary)

```bash
# Add haq.irfanul@gmail.com as editor (temporary for migration)
gcloud projects add-iam-policy-binding aialgotradehits \
  --member="user:haq.irfanul@gmail.com" \
  --role="roles/editor"
```

---

## Phase 2: Migrate BigQuery Data

### Step 2.1: Create BigQuery Dataset in aialgotradehits

```bash
# Create dataset if not exists
bq mk --project_id=aialgotradehits --dataset crypto_trading_data

# Set location
bq mk --project_id=aialgotradehits --location=US crypto_trading_data
```

### Step 2.2: Option A - Cross-Project Access (Recommended)

Grant aialgotradehits read access to cryptobot-462709 data:

```bash
# Grant BigQuery Data Viewer role to aialgotradehits service account
gcloud projects add-iam-policy-binding cryptobot-462709 \
  --member="serviceAccount:1075463475276-compute@developer.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"
```

### Step 2.3: Option B - Full Data Migration

Create migration bucket and copy data:

```bash
# Create storage bucket for migration
gsutil mb -p aialgotradehits -l US gs://aialgotradehits-data-migration

# Export each table (repeat for all tables)
bq extract --destination_format=AVRO \
  'cryptobot-462709:crypto_trading_data.stocks_daily' \
  'gs://aialgotradehits-data-migration/stocks_daily/*.avro'

# Import to aialgotradehits
bq load --source_format=AVRO \
  'aialgotradehits:crypto_trading_data.stocks_daily' \
  'gs://aialgotradehits-data-migration/stocks_daily/*.avro'
```

### Step 2.4: Key Tables to Migrate

| Table Name | Records | Priority |
|------------|---------|----------|
| stocks_historical_daily | 1,483,191 | High |
| stocks_daily | 92,375 | High |
| crypto_daily | 47,661 | High |
| etfs_historical_daily | 527,277 | Medium |
| forex_historical_daily | 100,000+ | Medium |
| users | 5 | High |

---

## Phase 3: Migrate Cloud Run Services

### Step 3.1: Update Source Code

For each Cloud Function, update the PROJECT_ID:

**Files to update:**
- `cloud_function_daily/main.py`: Change `PROJECT_ID = 'cryptobot-462709'` to `PROJECT_ID = 'aialgotradehits'`
- `cloud_function_hourly/main.py`: Same change
- `cloud_function_5min/main.py`: Same change
- `cloud_function_api/main.py`: Already set to 'aialgotradehits'

### Step 3.2: Deploy Services

```bash
# Set project
gcloud config set project aialgotradehits

# Deploy daily crypto fetcher
cd C:\1AITrading\Trading\cloud_function_daily
gcloud run deploy daily-crypto-fetcher \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --timeout=540

# Deploy hourly crypto fetcher
cd C:\1AITrading\Trading\cloud_function_hourly
gcloud run deploy hourly-crypto-fetcher \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --timeout=540

# Deploy 5-min fetcher
cd C:\1AITrading\Trading\cloud_function_5min
gcloud run deploy fivemin-top10-fetcher \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --timeout=300

# Deploy API
cd C:\1AITrading\Trading\cloud_function_api
gcloud run deploy crypto-trading-api \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=1Gi \
  --timeout=300
```

### Step 3.3: Verify Deployments

```bash
# List all services
gcloud run services list --project=aialgotradehits

# Test each endpoint
curl https://daily-crypto-fetcher-XXXXX-uc.a.run.app/health
curl https://crypto-trading-api-XXXXX-uc.a.run.app/health
```

---

## Phase 4: Migrate Cloud Schedulers

### Step 4.1: Create Schedulers in aialgotradehits

```bash
# Daily Crypto Fetch
gcloud scheduler jobs create http daily-crypto-fetch-job \
  --project=aialgotradehits \
  --location=us-central1 \
  --schedule="0 0 * * *" \
  --uri="https://daily-crypto-fetcher-XXXXX-uc.a.run.app" \
  --http-method=GET \
  --time-zone="America/New_York"

# Hourly Crypto Fetch
gcloud scheduler jobs create http hourly-crypto-fetch-job \
  --project=aialgotradehits \
  --location=us-central1 \
  --schedule="0 * * * *" \
  --uri="https://hourly-crypto-fetcher-XXXXX-uc.a.run.app" \
  --http-method=GET \
  --time-zone="America/New_York"

# 5-Minute Fetch
gcloud scheduler jobs create http fivemin-top10-fetch-job \
  --project=aialgotradehits \
  --location=us-central1 \
  --schedule="*/5 * * * *" \
  --uri="https://fivemin-top10-fetcher-XXXXX-uc.a.run.app" \
  --http-method=GET \
  --time-zone="America/New_York"
```

### Step 4.2: Pause Old Schedulers

```bash
# Pause schedulers in cryptobot-462709 (don't delete yet)
gcloud scheduler jobs pause daily-crypto-fetch-job --project=cryptobot-462709 --location=us-central1
gcloud scheduler jobs pause hourly-crypto-fetch-job --project=cryptobot-462709 --location=us-central1
gcloud scheduler jobs pause fivemin-top10-fetch-job --project=cryptobot-462709 --location=us-central1
# ... repeat for all 24 schedulers
```

---

## Phase 5: Claude AI Migration

### Step 5.1: Document Current Claude Settings

From haq.irfanul@gmail.com Claude account:
1. Go to https://claude.ai/settings
2. Screenshot or note:
   - Custom instructions
   - Memory settings
   - Preferences
   - API keys (if any)

### Step 5.2: Set Up Claude for Business Account

1. Go to https://claude.ai
2. Sign up/login with irfan.qazi@aialgotradehits.com
3. Subscribe to Claude Pro ($20/month)
4. Configure same settings as personal account

### Step 5.3: Migrate Claude Code CLI

```bash
# Logout from personal account
claude logout

# Login with business account
claude login
# Enter: irfan.qazi@aialgotradehits.com
# Complete authentication in browser
```

### Step 5.4: Update CLAUDE.md Files

Ensure all project CLAUDE.md files reference the new project:
- Update PROJECT_ID references from 'cryptobot-462709' to 'aialgotradehits'

---

## Phase 6: Google Workspace Migration

### Step 6.1: Verify Google Workspace for AIAlgoTradeHits.com

1. Go to https://admin.google.com
2. Login with irfan.qazi@aialgotradehits.com
3. Verify Workspace is active

### Step 6.2: Add Domain Aliases

In Google Workspace Admin Console:

1. Go to: Account > Domains > Manage domains
2. Add each domain as an alias:
   - kaamyabpakistan.org
   - nocodeai.cloud
   - youinvent.tech
   - homefranchise.biz
   - iotmotorz.com

3. Verify DNS for each domain:
   - Add TXT record for verification
   - Add MX records for email

### Step 6.3: Create Email Aliases

For each domain, create appropriate email aliases:
- admin@kaamyabpakistan.org → irfan.qazi@aialgotradehits.com
- hello@nocodeai.cloud → irfan.qazi@aialgotradehits.com
- etc.

### Step 6.4: Migrate Google Drive Data

**Option A: Google Takeout**
1. Go to https://takeout.google.com (logged in as haq.irfanul@gmail.com)
2. Select Google Drive
3. Export as ZIP
4. Upload to irfan.qazi@aialgotradehits.com Drive

**Option B: Share and Copy**
1. Share folders with irfan.qazi@aialgotradehits.com
2. Make copies in new account
3. Remove sharing after verification

---

## Phase 7: Domain Configuration

### Step 7.1: Configure AIAlgoTradeHits.com Domain

**DNS Settings for Cloud Run:**

| Type | Name | Value |
|------|------|-------|
| A | @ | (Cloud Run IP) |
| CNAME | www | ghs.googlehosted.com |

**Domain Mapping:**
```bash
gcloud beta run domain-mappings create \
  --service=trading-app \
  --domain=aialgotradehits.com \
  --project=aialgotradehits \
  --region=us-central1
```

### Step 7.2: SSL Certificate

Cloud Run automatically provisions SSL certificates for mapped domains.

---

## Phase 8: Verification and Testing

### Step 8.1: Test All Services

```bash
# Test frontend
curl -I https://trading-app-XXXXX-uc.a.run.app

# Test API
curl https://crypto-trading-api-XXXXX-uc.a.run.app/health

# Test data fetchers
curl https://daily-crypto-fetcher-XXXXX-uc.a.run.app/health
```

### Step 8.2: Verify Data Flow

```bash
# Check BigQuery for new data
bq query --project_id=aialgotradehits --use_legacy_sql=false \
  "SELECT MAX(datetime) FROM crypto_trading_data.stocks_daily"
```

### Step 8.3: Test Schedulers

```bash
# Manually trigger a scheduler
gcloud scheduler jobs run daily-crypto-fetch-job \
  --project=aialgotradehits \
  --location=us-central1

# Check logs
gcloud run logs read daily-crypto-fetcher --project=aialgotradehits --limit=20
```

---

## Phase 9: Cleanup Personal Account

### Step 9.1: Remove Collaborator Access

```bash
# Remove personal account from business project
gcloud projects remove-iam-policy-binding aialgotradehits \
  --member="user:haq.irfanul@gmail.com" \
  --role="roles/editor"
```

### Step 9.2: Delete Unused GCP Projects

```bash
# Delete unused projects (IRREVERSIBLE - be careful!)
gcloud projects delete fine-effect-271218
gcloud projects delete vertical-orbit-271201

# Archive or delete cryptobot-462709 after full verification
# gcloud projects delete cryptobot-462709
```

### Step 9.3: Cancel Subscriptions

1. **Claude Pro (haq.irfanul@gmail.com)**
   - Go to https://claude.ai/settings/billing
   - Cancel subscription

2. **GCP Billing**
   - Go to https://console.cloud.google.com/billing
   - Close billing account after all projects deleted

3. **Google Workspace (if any)**
   - Cancel any paid services on personal account

### Step 9.4: Set Up Email Forwarding

1. In Gmail (haq.irfanul@gmail.com):
   - Go to Settings > Forwarding
   - Forward all mail to irfan.qazi@aialgotradehits.com

---

## Cost Summary

### Before Migration (Personal Account)
| Service | Monthly Cost |
|---------|-------------|
| GCP (cryptobot-462709) | ~$135 |
| Claude Pro | $20 |
| **Total** | **~$155** |

### After Migration (Business Account)
| Service | Monthly Cost |
|---------|-------------|
| GCP (aialgotradehits) | ~$135 |
| Claude Pro | $20 |
| Google Workspace | $12 |
| **Total** | **~$167** |

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Prepare Environment | 1 hour | None |
| Phase 2: Migrate BigQuery | 2-4 hours | Phase 1 |
| Phase 3: Migrate Cloud Run | 2-3 hours | Phase 2 |
| Phase 4: Migrate Schedulers | 1 hour | Phase 3 |
| Phase 5: Claude Migration | 30 minutes | None |
| Phase 6: Workspace Migration | 2-4 hours | None |
| Phase 7: Domain Config | 1-2 hours | Phase 3 |
| Phase 8: Verification | 2 hours | All above |
| Phase 9: Cleanup | 1 hour | Phase 8 |

**Total Estimated Time: 1-2 days**

---

## Support and Resources

- **GCP Documentation:** https://cloud.google.com/docs
- **Claude Documentation:** https://docs.anthropic.com
- **Google Workspace Admin:** https://admin.google.com

---

*Document prepared by Claude Code*
*Last updated: November 29, 2025*
