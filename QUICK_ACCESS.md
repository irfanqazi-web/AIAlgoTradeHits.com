# Quick Access - Trading App

## Live Application URLs

### Main Trading Application
🌐 **https://crypto-trading-app-252370699783.us-central1.run.app**

**Features:**
- Toggle between Crypto and Stock markets
- View Daily, Hourly, and 5-Minute timeframes
- Expand any timeframe for detailed analytics
- Access Admin Panel for user management

### Backend API
🔌 **https://trading-api-cnyn5l4u2a-uc.a.run.app**

**Quick Test Endpoints:**
```bash
# Health Check
curl https://trading-api-cnyn5l4u2a-uc.a.run.app/health

# Get 5 crypto records
curl "https://trading-api-cnyn5l4u2a-uc.a.run.app/api/crypto/daily?limit=5"

# Get 5 stock records
curl "https://trading-api-cnyn5l4u2a-uc.a.run.app/api/stocks?limit=5"

# Crypto market summary
curl "https://trading-api-cnyn5l4u2a-uc.a.run.app/api/summary/crypto"

# Stock market summary
curl "https://trading-api-cnyn5l4u2a-uc.a.run.app/api/summary/stock"
```

---

## Data Pipeline Status

### Cloud Functions (Data Collection)
```bash
# Check if functions are running
gcloud functions list --project=cryptobot-462709

# Trigger manual data collection
curl https://daily-crypto-fetcher-cnyn5l4u2a-uc.a.run.app
curl https://hourly-crypto-fetcher-cnyn5l4u2a-uc.a.run.app
curl https://fivemin-top10-fetcher-cnyn5l4u2a-uc.a.run.app
```

### BigQuery Tables
```bash
# Check data counts
python check_bigquery_counts.py

# Query latest crypto data
bq query --use_legacy_sql=false \
  'SELECT pair, close, rsi, macd, datetime
   FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`
   ORDER BY datetime DESC LIMIT 10'

# Query latest stock data
bq query --use_legacy_sql=false \
  'SELECT symbol, company_name, close, rsi, macd, datetime
   FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
   ORDER BY datetime DESC LIMIT 10'
```

---

## Deployment Commands

### Redeploy Backend API
```bash
cd cloud_function_api
python deploy_api.py
```

### Redeploy Frontend
```bash
cd stock-price-app
gcloud run deploy crypto-trading-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project cryptobot-462709
```

---

## Monitoring

### View Logs
```bash
# API logs
gcloud run services logs read trading-api --project=cryptobot-462709 --limit=20

# Frontend logs
gcloud run services logs read crypto-trading-app --project=cryptobot-462709 --limit=20

# Cloud Function logs
gcloud functions logs read daily-crypto-fetcher --project=cryptobot-462709 --limit=20
```

### Service Info
```bash
# API service details
gcloud run services describe trading-api --region=us-central1 --project=cryptobot-462709

# Frontend service details
gcloud run services describe crypto-trading-app --region=us-central1 --project=cryptobot-462709
```

---

## Project Structure

```
Trading/
├── cloud_function_api/          # Backend API (Flask + BigQuery)
│   ├── main.py                  # API endpoints
│   ├── requirements.txt
│   └── deploy_api.py           # Deployment script
│
├── stock-price-app/            # Frontend React App
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── AIAlgoTradeHitsReal.jsx  # Main dashboard
│   │   │   └── AdminPanel.jsx           # User management
│   │   └── services/
│   │       └── api.js          # API service layer
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── cloud_function_daily/       # Daily crypto data collection
├── cloud_function_hourly/      # Hourly crypto data collection
├── cloud_function_5min/        # 5-min top gainers collection
├── cloud_function_daily_stocks/  # Daily stock data collection
│
└── Documentation/
    ├── CLAUDE.md               # Project overview
    ├── QUICK_START_GUIDE.md
    ├── FINAL_DEPLOYMENT_STATUS.md
    ├── TRADING_APP_DEPLOYMENT_COMPLETE.md
    └── QUICK_ACCESS.md         # This file
```

---

## GCP Console Links

- **Cloud Run:** https://console.cloud.google.com/run?project=cryptobot-462709
- **BigQuery:** https://console.cloud.google.com/bigquery?project=cryptobot-462709
- **Cloud Functions:** https://console.cloud.google.com/functions?project=cryptobot-462709
- **Cloud Scheduler:** https://console.cloud.google.com/cloudscheduler?project=cryptobot-462709
- **Logs Explorer:** https://console.cloud.google.com/logs?project=cryptobot-462709

---

## Quick Troubleshooting

### Problem: App shows "Loading..." forever
**Solution:**
1. Check API health: `curl https://trading-api-cnyn5l4u2a-uc.a.run.app/health`
2. Check BigQuery has data: `python check_bigquery_counts.py`
3. View API logs for errors

### Problem: No data in BigQuery
**Solution:**
1. Manually trigger data collection functions
2. Check Cloud Scheduler jobs are enabled
3. Review function logs for errors

### Problem: API returns errors
**Solution:**
1. Check BigQuery tables exist and have correct schema
2. Verify service account permissions
3. Review API logs: `gcloud run services logs read trading-api`

---

## API Reference

### Crypto Data Endpoints
- `GET /api/crypto/daily?limit=100` - Daily OHLC + indicators
- `GET /api/crypto/hourly?limit=100` - Hourly OHLC + indicators
- `GET /api/crypto/5min?limit=100` - 5-min top gainers data

### Stock Data Endpoints
- `GET /api/stocks?limit=100` - Daily stock OHLC + indicators

### Summary Endpoints
- `GET /api/summary/crypto` - Crypto market statistics
- `GET /api/summary/stock` - Stock market statistics

### User Management (Admin)
- `GET /api/users` - List all users
- `POST /api/users` - Create user (body: {email, name, role})
- `PUT /api/users/{id}` - Update user (body: {name, role, is_active})
- `DELETE /api/users/{id}` - Soft delete user

---

*Last Updated: November 11, 2025*
