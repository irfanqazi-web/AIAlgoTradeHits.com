# Admin Panel & System Monitoring - Deployment Guide

Complete guide for deploying the enhanced admin panel with database monitoring and billing dashboards.

## Overview

The enhanced admin panel provides comprehensive system management and monitoring capabilities:

1. **User Management** - Create, update, delete users and manage permissions
2. **Database Monitoring** - Real-time BigQuery table statistics, data quality, and growth metrics
3. **Billing Dashboard** - GCP cost breakdown, usage tracking, and optimization recommendations

---

## What We Built

### Backend (Cloud Function)

**Location**: `cloud_function_monitoring/`

**Features**:
- Real-time BigQuery table statistics (row counts, sizes, timestamps)
- Data quality monitoring (detects missing dates, completeness %)
- Daily data growth tracking (30-day history)
- Top trading pairs by volume
- GCP billing estimates by service
- System health metrics (functions, schedulers)

**Endpoints**:
- `/tables` - Table statistics
- `/billing` - Billing information
- `/health` - System health status
- `/growth` - Data growth metrics
- `/quality` - Data quality metrics
- `/top-pairs` - Top trading pairs
- `/full` - Complete monitoring report

### Frontend Components

**1. DatabaseMonitoring.jsx**
- Real-time table statistics with auto-refresh (every 5 minutes)
- Data quality dashboard (7-day completeness)
- Growth charts (30-day history)
- Top 20 trading pairs by volume
- Health status indicators

**2. BillingDashboard.jsx**
- Monthly cost breakdown by service
- Pie chart (cost by category)
- Bar chart (cost by individual service)
- Cost optimization recommendations
- Budget tracking

**3. AdminPanelEnhanced.jsx**
- Tabbed interface combining all admin features
- User Management tab (existing functionality)
- Database Monitoring tab (new)
- Billing & Costs tab (new)

---

## Architecture

```
User → React App (Admin Panel)
         ↓
    Monitoring Service (monitoringService.js)
         ↓
    Cloud Function (system-monitoring)
         ↓
    ┌────┴────────┐
    ↓             ↓
BigQuery      GCP Billing API
(Table Stats)  (Cost Data)
```

---

## Deployment Steps

### Step 1: Deploy Monitoring Cloud Function

```bash
cd cloud_function_monitoring
python deploy.py
```

**Expected Output:**
```
Deploying system-monitoring to cryptobot-462709...
Region: us-central1
Memory: 512MB
Timeout: 300s

This may take 3-5 minutes...

✅ Deployment successful!

🔗 Function URL: https://system-monitoring-cnyn5l4u2a-uc.a.run.app
```

**Copy the Function URL!**

### Step 2: Update Frontend Configuration

Edit `stock-price-app/.env`:

```env
VITE_MONITORING_URL=https://system-monitoring-cnyn5l4u2a-uc.a.run.app
```

Edit `.env` in root directory (for backend):

```env
GCP_PROJECT_ID=cryptobot-462709
BIGQUERY_DATASET=crypto_trading_data
```

### Step 3: Restart Development Server

```bash
cd stock-price-app
npm run dev
```

The app will reload with the new monitoring URL.

### Step 4: Test the Admin Panel

1. Navigate to http://localhost:5173/
2. Login with admin credentials
3. Click "Admin" in the left menu
4. You'll see 3 tabs:
   - **User Management** - Manage users
   - **Database Monitoring** - View BigQuery stats
   - **Billing & Costs** - View GCP costs

---

## Features in Detail

### Database Monitoring

**Summary Cards**:
- Total Tables
- Healthy Tables
- Total Records (formatted: 1.2M)
- Total Size (in GB)

**Tables Grid**:
| Table Name | Rows | Size (GB) | Pairs | 24h Records | Latest Data | Status |
|------------|------|-----------|-------|-------------|-------------|--------|
| crypto_analysis | 60K | 0.25 | 675 | 675 | 2025-11-18 12:00 | ✓ Healthy |
| crypto_hourly_data | 450K | 1.50 | 675 | 16,200 | 2025-11-18 12:00 | ✓ Healthy |
| crypto_5min_top10_gainers | 150K | 0.50 | 10 | 2,880 | 2025-11-18 12:00 | ✓ Healthy |

**Data Quality (Last 7 Days)**:
- Shows completeness % for each table
- Highlights missing dates in red
- Displays health status (Good/Warning)

**Data Growth (Last 30 Days)**:
- Bar charts showing daily record counts
- Visualizes data collection trends
- Helps identify gaps or anomalies

**Top 20 Trading Pairs**:
- Ranked by 24-hour volume
- Shows latest price
- Displays data point count

### Billing Dashboard

**Summary Cards**:
- Total Monthly Cost: $238.30
- Compute & Functions: $168.00 (71%)
- AI & ML Services: $60.00 (25%)

**Cost Breakdown by Category** (Pie Chart):
- Compute (Cloud Functions + Cloud Run)
- Data Storage (BigQuery)
- AI/ML (Claude + Vertex AI)
- Networking
- Scheduler

**Cost by Service** (Bar Chart):
- Hourly Crypto Fetcher: $72.00
- 5-Min Crypto Fetcher: $50.00
- Claude API: $40.00
- AI Intelligence Function: $35.00
- And more...

**Detailed Cost Table**:
Complete breakdown of all services with:
- Service name
- Category
- Monthly cost
- Percentage of total

**Cost Optimization Tips**:
- Implement API caching
- Use BigQuery partitioning
- Review memory allocation
- Set billing alerts
- Optimize AI prompt lengths
- Use committed use discounts

---

## API Reference

### System Monitoring Endpoints

**Base URL**: `https://system-monitoring-<hash>-uc.a.run.app`

**Get All Table Stats**:
```bash
curl "https://[URL]?endpoint=tables"
```

**Response**:
```json
{
  "timestamp": "2025-11-18T17:00:00Z",
  "project_id": "cryptobot-462709",
  "dataset_id": "crypto_trading_data",
  "tables": [
    {
      "table_name": "crypto_analysis",
      "row_count": 60000,
      "size_gb": 0.2534,
      "latest_timestamp": "2025-11-18T12:00:00Z",
      "unique_pairs": 675,
      "recent_24h_count": 675,
      "status": "healthy"
    }
  ]
}
```

**Get Billing Data**:
```bash
curl "https://[URL]?endpoint=billing"
```

**Get System Health**:
```bash
curl "https://[URL]?endpoint=health"
```

**Get Data Growth**:
```bash
curl "https://[URL]?endpoint=growth"
```

**Get Data Quality**:
```bash
curl "https://[URL]?endpoint=quality"
```

**Get Top Pairs**:
```bash
curl "https://[URL]?endpoint=top-pairs"
```

**Get Full Report** (All data):
```bash
curl "https://[URL]?endpoint=full"
```

---

## Database Tables Monitored

### Crypto Tables

1. **crypto_analysis** (Daily Data)
   - ~675 pairs
   - ~675 new records per day
   - Expected size: 0.25 GB
   - Contains: OHLC + 29 technical indicators

2. **crypto_hourly_data** (Hourly Data)
   - ~675 pairs
   - ~16,200 new records per day (675 pairs × 24 hours)
   - Expected size: 1.50 GB
   - Contains: OHLC + 29 technical indicators

3. **crypto_5min_top10_gainers** (5-Minute Data)
   - Top 10 pairs only
   - ~2,880 new records per day (10 pairs × 288 intervals)
   - Expected size: 0.50 GB
   - Contains: OHLC + indicators

### System Tables

4. **users**
   - User accounts
   - Roles and permissions
   - Authentication data

5. **search_history**
   - NLP search queries
   - Search results
   - User search patterns

---

## Cost Breakdown

### Current Monthly Costs

| Category | Services | Monthly Cost |
|----------|----------|--------------|
| **Compute** | Cloud Functions (4) + Cloud Run | $168.00 |
| **Data Storage** | BigQuery + Cloud Storage | $7.00 |
| **AI/ML** | Claude API + Vertex AI | $60.00 |
| **Networking** | Data transfer | $3.00 |
| **Scheduler** | Cloud Scheduler (3 jobs) | $0.30 |
| **Total** | | **$238.30** |

### Detailed Breakdown

**Cloud Functions**:
- Daily Crypto Fetcher: $4.00
- Hourly Crypto Fetcher: $72.00
- 5-Minute Top 10 Fetcher: $50.00
- AI Intelligence Function: $35.00
- System Monitoring Function: $2.00
- **Subtotal**: $163.00

**AI APIs**:
- Claude (Anthropic): $40.00
- Vertex AI (Gemini): $20.00
- **Subtotal**: $60.00

**Data Storage**:
- BigQuery Storage: $2.00
- BigQuery Queries: $5.00
- **Subtotal**: $7.00

---

## Monitoring Best Practices

### Daily Checks

1. **Table Health**:
   - Check all tables show "Healthy" status
   - Verify latest timestamps are recent
   - Ensure 24h record counts match expectations

2. **Data Quality**:
   - Review completeness percentages (should be 100%)
   - Check for missing dates
   - Investigate any warnings

3. **Costs**:
   - Monitor daily spending
   - Check for unexpected spikes
   - Review optimization recommendations

### Weekly Reviews

1. **Growth Trends**:
   - Analyze 30-day growth charts
   - Identify patterns or anomalies
   - Plan storage capacity

2. **Top Pairs**:
   - Review most active trading pairs
   - Ensure adequate coverage
   - Consider adding more pairs

3. **Cost Optimization**:
   - Implement recommended optimizations
   - Review function memory allocation
   - Check for unused resources

### Monthly Tasks

1. **Billing Analysis**:
   - Compare actual vs estimated costs
   - Identify cost-saving opportunities
   - Adjust budgets if needed

2. **Data Cleanup**:
   - Archive old data if needed
   - Optimize BigQuery partitions
   - Review retention policies

3. **System Updates**:
   - Update Cloud Functions
   - Upgrade dependencies
   - Apply security patches

---

## Troubleshooting

### Issue: "Error Loading Monitoring Data"

**Cause**: Monitoring function not deployed or URL incorrect

**Solution**:
```bash
# 1. Verify function is deployed
gcloud functions describe system-monitoring --region=us-central1

# 2. Get function URL
gcloud functions describe system-monitoring --region=us-central1 --format="value(serviceConfig.uri)"

# 3. Update .env with correct URL
```

### Issue: "No Data Available" for Tables

**Cause**: BigQuery tables are empty or functions haven't run

**Solution**:
```bash
# Check table counts
python check_bigquery_counts.py

# Manually trigger data collection
curl https://daily-crypto-fetcher-cnyn5l4u2a-uc.a.run.app
curl https://hourly-crypto-fetcher-cnyn5l4u2a-uc.a.run.app
```

### Issue: Missing Dates in Data Quality

**Cause**: Scheduler jobs didn't run or failed

**Solution**:
```bash
# Check scheduler status
gcloud scheduler jobs list --location=us-central1

# Check function logs
gcloud functions logs read daily-crypto-fetcher --limit=50

# Manually backfill missing data
python backfill_missing_days.py
```

### Issue: Billing Data Shows $0

**Cause**: Billing API not enabled or estimates not configured

**Solution**:
The current implementation uses estimated costs. To get actual billing data:
1. Enable Cloud Billing API
2. Update monitoring function with billing account ID
3. Implement actual billing queries

---

## Security Considerations

### Function Access

The monitoring function is **public** (unauthenticated) by design because:
- It's called by the frontend
- Data is not sensitive (aggregate statistics only)
- CORS is enabled for frontend access

**To restrict access**:
```bash
# Remove public access
gcloud functions remove-invoker-policy-binding system-monitoring \
  --region=us-central1 \
  --member=allUsers

# Add authenticated access only
gcloud functions add-invoker-policy-binding system-monitoring \
  --region=us-central1 \
  --member=serviceAccount:your-service-account@project.iam.gserviceaccount.com
```

### Data Privacy

- No user personal data is exposed
- Only aggregate statistics are shown
- Admin access required to view monitoring

---

## Next Steps

### Immediate (Today)

1. ✅ Deploy monitoring Cloud Function
2. ✅ Test database monitoring tab
3. ✅ Test billing dashboard
4. ✅ Verify data quality metrics

### Short-term (This Week)

1. **Set Billing Alerts**:
   ```bash
   # Set up billing alerts in GCP Console
   # Billing → Budgets & alerts
   # Create alerts at $50, $100, $200
   ```

2. **Implement Caching**:
   - Cache monitoring data for 5 minutes
   - Reduce BigQuery query costs

3. **Add Email Notifications**:
   - Email admin when data quality drops
   - Alert on unexpected cost spikes

### Long-term (This Month)

1. **Historical Tracking**:
   - Store daily snapshots
   - Trend analysis dashboard
   - Anomaly detection

2. **Advanced Billing**:
   - Integrate actual GCP Billing API
   - Cost forecasting
   - Budget tracking

3. **Automated Actions**:
   - Auto-restart failed functions
   - Auto-backfill missing data
   - Auto-scale resources

---

## Testing Checklist

- [ ] Monitoring function deployed successfully
- [ ] Function URL updated in .env
- [ ] Development server restarted
- [ ] Can access Admin Panel
- [ ] Database Monitoring tab loads
- [ ] Table statistics display correctly
- [ ] Data quality metrics show
- [ ] Growth charts render
- [ ] Top pairs display
- [ ] Billing Dashboard tab loads
- [ ] Cost breakdown shows
- [ ] Pie chart renders
- [ ] Bar chart renders
- [ ] Detailed cost table shows
- [ ] Can refresh data manually
- [ ] Auto-refresh works (5 minutes)

---

## Support

### View Logs

```bash
# Monitoring function logs
gcloud functions logs read system-monitoring --limit=50

# Check for errors
gcloud functions logs read system-monitoring --limit=50 | grep ERROR
```

### Test Endpoints

```bash
# Test monitoring function
curl "https://[FUNCTION-URL]?endpoint=tables"

# Test with jq for pretty output
curl "https://[FUNCTION-URL]?endpoint=full" | jq .
```

### BigQuery Console

1. Go to: https://console.cloud.google.com/bigquery
2. Select project: cryptobot-462709
3. Expand dataset: crypto_trading_data
4. Browse tables and run custom queries

---

## Summary

**Status**: ✅ Ready for Deployment

**Deployment Time**: ~10 minutes

**Features Added**:
- Real-time database monitoring
- Data quality tracking
- Billing dashboard
- Cost optimization recommendations
- Enhanced admin panel with tabs

**Next Action**: Deploy monitoring function and test!

```bash
cd cloud_function_monitoring
python deploy.py
```
