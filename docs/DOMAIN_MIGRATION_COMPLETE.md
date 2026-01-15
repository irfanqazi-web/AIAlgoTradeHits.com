# Domain Services Migration Complete

**Date:** November 29, 2025
**Status:** COMPLETED

## Migration Summary

All domain website services have been successfully migrated from personal GCP projects to the business project (aialgotradehits).

## Sites Migrated from Personal to Business

| # | Domain | Service | Source Project | Status |
|---|--------|---------|----------------|--------|
| 1 | AIAlgoTradeHits.com | trading-app | cryptobot-462709 | MIGRATED |
| 2 | KaamyabPakistan.org | kaamyabpakistan | molten-optics-310919 | MIGRATED |
| 3 | YouInvent.Tech | youinvent-tech | molten-optics-310919 | MIGRATED |
| 4 | HomeFranchise.Biz | homefranchise-biz | molten-optics-310919 | MIGRATED |
| 5 | IoTMotorz.com | iotmotorz-com | molten-optics-310919 | MIGRATED |
| 6 | NoCodeAI.cloud | nocodeai-cloud | NEW (placeholder) | CREATED |
| 7 | HerbalHomeo (API) | herbalhomeo-api | cryptobot-462709 | MIGRATED |
| 8 | HerbalHomeo (Frontend) | herbalhomeo-frontend | cryptobot-462709 | MIGRATED |

## Cloud Run Services - Business Account (aialgotradehits)

| Service | URL | Purpose |
|---------|-----|---------|
| trading-app | https://trading-app-6pmz2y7ouq-uc.a.run.app | AIAlgoTradeHits.com Main App |
| crypto-trading-api | https://crypto-trading-api-6pmz2y7ouq-uc.a.run.app | Trading API Backend |
| ai-trading-intelligence | https://ai-trading-intelligence-6pmz2y7ouq-uc.a.run.app | AI/ML Services |
| smart-search | https://smart-search-6pmz2y7ouq-uc.a.run.app | NLP Search API |
| twelvedata-fetcher | https://twelvedata-fetcher-6pmz2y7ouq-uc.a.run.app | Market Data Fetcher |
| kaamyabpakistan | https://kaamyabpakistan-6pmz2y7ouq-uc.a.run.app | KaamyabPakistan.org |
| youinvent-tech | https://youinvent-tech-6pmz2y7ouq-uc.a.run.app | YouInvent.Tech |
| homefranchise-biz | https://homefranchise-biz-6pmz2y7ouq-uc.a.run.app | HomeFranchise.Biz |
| iotmotorz-com | https://iotmotorz-com-6pmz2y7ouq-uc.a.run.app | IoTMotorz.com |
| herbalhomeo-api | https://herbalhomeo-api-6pmz2y7ouq-uc.a.run.app | HerbalHomeo API |
| herbalhomeo-frontend | https://herbalhomeo-frontend-6pmz2y7ouq-uc.a.run.app | HerbalHomeo Frontend |
| nocodeai-cloud | https://nocodeai-cloud-6pmz2y7ouq-uc.a.run.app | NoCodeAI.cloud |

**Total Services:** 12

## Account Details

### Business Account (Target - Keep Active)
- **Email:** irfan.qazi@aialgotradehits.com
- **GCP Project:** aialgotradehits
- **Project Number:** 1075463475276
- **Console:** https://console.cloud.google.com/home/dashboard?project=aialgotradehits

### Personal Accounts (Source - To Be Closed)
| Account | GCP Project | Status |
|---------|-------------|--------|
| haq.irfanul@gmail.com | cryptobot-462709 | Data still needed |
| haq.irfanul@gmail.com | molten-optics-310919 | Can be archived |

## Domain DNS Configuration (Interserver.net)

| Domain | Point To |
|--------|----------|
| aialgotradehits.com | https://trading-app-6pmz2y7ouq-uc.a.run.app |
| kaamyabpakistan.org | https://kaamyabpakistan-6pmz2y7ouq-uc.a.run.app |
| youinvent.tech | https://youinvent-tech-6pmz2y7ouq-uc.a.run.app |
| homefranchise.biz | https://homefranchise-biz-6pmz2y7ouq-uc.a.run.app |
| iotmotorz.com | https://iotmotorz-com-6pmz2y7ouq-uc.a.run.app |
| nocodeai.cloud | https://nocodeai-cloud-6pmz2y7ouq-uc.a.run.app |

## BigQuery Datasets

### Existing Datasets (aialgotradehits)
- `crypto_trading_data` - Main trading data
- `trading_data_unified` - Unified trading data

### Datasets to Create (via GCP Console)
Log in as irfan.qazi@aialgotradehits.com and create:
- `kaamyabpakistan_data`
- `youinvent_data`
- `homefranchise_data`
- `iotmotorz_data`
- `herbalhomeo_data`
- `nocodeai_data`

## Cloud Schedulers

25 Cloud Schedulers running in aialgotradehits for automated data collection:
- Daily fetchers (stocks, crypto, forex, ETFs, indices, commodities)
- Hourly fetchers (stocks, crypto, forex)
- 5-minute fetchers (top gainers)
- Weekly fetchers (all asset types)

## Pending Actions

### 1. Set IAM Policies (GCP Console)
- Log in as irfan.qazi@aialgotradehits.com
- Go to Cloud Run > each service > Security
- Allow unauthenticated invocations for all 12 services

### 2. Create BigQuery Datasets
- Log in to BigQuery console as business account
- Create datasets for each domain

### 3. Configure Custom Domains
- Go to Cloud Run > Manage Custom Domains
- Add custom domain mappings for each service

### 4. Update DNS at Interserver.net
- Point each domain to its Cloud Run URL

### 5. Close Personal Accounts
After verifying everything works:
- Remove haq.irfanul@gmail.com from aialgotradehits IAM
- Archive molten-optics-310919 project
- Keep cryptobot-462709 for BigQuery data access

---

## IMPORTANT: Claude.ai Subscription

**Personal Claude.ai (haq.irfanul@gmail.com):**
- **Plan:** Claude Max
- **Renewal Date:** 7th of each month
- **ACTION REQUIRED: CANCEL BY DECEMBER 6, 2025**
- Billing page: https://claude.ai/settings/billing

---

*Migration completed by Claude Code*
*Document generated: November 29, 2025*
