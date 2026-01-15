# Localhost Testing Guide - Enhanced Admin Panel

## ✅ Deployment Complete!

Your enhanced admin panel with database monitoring and billing dashboards is now ready for testing on localhost.

---

## 🎯 What's Deployed

### Backend
✅ **Monitoring Cloud Function**: https://system-monitoring-cnyn5l4u2a-uc.a.run.app
- Status: ACTIVE
- Region: us-central1
- Memory: 512MB
- Timeout: 5 minutes

### Frontend
✅ **Development Server**: http://localhost:5173/
- Status: Running
- Auto-restarted with new .env configuration
- Connected to monitoring function

---

## 🧪 Testing Steps

### Step 1: Access the Application

1. Open your browser
2. Navigate to: **http://localhost:5173/**
3. You should see the login page

### Step 2: Login as Admin

Use your admin credentials:
- **Email**: (your admin email)
- **Password**: (your admin password)

**Note**: You need admin role to access the admin panel!

### Step 3: Open Admin Panel

1. After login, look at the left navigation menu
2. Click on **"Admin"** (should be near the bottom)
3. The enhanced admin panel will open

### Step 4: Test User Management Tab (Existing Feature)

**What to test:**
- [ ] User list displays correctly
- [ ] Can see all users with their details
- [ ] "Create New User" button works
- [ ] Can create a new user
- [ ] Can edit user details (click Edit icon)
- [ ] Can send invitation email (click Mail icon)
- [ ] Can delete user (click Trash icon)

**Expected:**
- Clean table layout with user information
- Status badges (Active/Inactive)
- Role badges (User/Admin)
- Action buttons for each user

### Step 5: Test Database Monitoring Tab (NEW!)

1. Click on the **"Database Monitoring"** tab

**What to test:**

**Summary Cards** (top row):
- [ ] Total Tables count displays
- [ ] Healthy Tables count displays
- [ ] Total Records count shows (formatted: e.g., "660K")
- [ ] Total Size shows in GB

**Tables Grid:**
- [ ] All BigQuery tables are listed:
  - crypto_analysis
  - crypto_hourly_data
  - crypto_5min_top10_gainers
  - users
  - search_history
- [ ] Each table shows:
  - Row count (formatted)
  - Size in GB
  - Unique pairs (for crypto tables)
  - 24-hour record count
  - Latest timestamp
  - Health status badge (Green = Healthy)

**Data Quality Section:**
- [ ] Shows completeness % for crypto tables
- [ ] Displays "Last 7 Days" quality metrics
- [ ] Green status badges indicate good quality
- [ ] Any missing dates are highlighted in red

**View Selector:**
- [ ] Can switch between "Overview", "Data Growth", "Top Pairs"

**Data Growth View:**
- [ ] Click "Data Growth" tab
- [ ] Bar charts show 30-day record history
- [ ] One chart per crypto table
- [ ] Charts are interactive (hover shows values)

**Top Pairs View:**
- [ ] Click "Top Pairs" tab
- [ ] Shows top 20 trading pairs by volume
- [ ] Displays latest price
- [ ] Shows average 24h volume
- [ ] Data points count

**Refresh Button:**
- [ ] Click "Refresh" button
- [ ] Data reloads
- [ ] "Last refresh" timestamp updates

**Auto-refresh:**
- [ ] Wait 5 minutes
- [ ] Data should auto-refresh
- [ ] Timestamp updates automatically

### Step 6: Test Billing Dashboard Tab (NEW!)

1. Click on the **"Billing & Costs"** tab

**What to test:**

**Summary Cards** (top row):
- [ ] Total Monthly Cost displays (~$238.30)
- [ ] Compute & Functions cost shows
- [ ] AI & ML Services cost shows
- [ ] Percentages are calculated correctly

**Cost Breakdown Pie Chart:**
- [ ] Pie chart renders
- [ ] Shows categories:
  - COMPUTE
  - DATA_STORAGE
  - AI_ML
  - NETWORKING
  - SCHEDULER
- [ ] Hovering shows exact values
- [ ] Percentages add up to 100%

**Cost by Service Bar Chart:**
- [ ] Bar chart renders
- [ ] Shows top 10 services by cost
- [ ] Bars are color-coded (green)
- [ ] X-axis labels are readable
- [ ] Hovering shows service name and cost

**Detailed Cost Table:**
- [ ] Complete list of all services
- [ ] Each row shows:
  - Service name
  - Category badge
  - Monthly cost
  - Percentage of total
- [ ] Table is sortable
- [ ] Total row at bottom matches summary
- [ ] All percentages add to 100%

**Cost Optimization Tips:**
- [ ] Orange box at bottom displays
- [ ] 6 optimization recommendations shown
- [ ] Tips are readable and actionable

### Step 7: Test Navigation Between Tabs

**What to test:**
- [ ] Can switch from Users → Database → Billing
- [ ] Can switch from Billing → Users → Database
- [ ] Active tab is highlighted in green
- [ ] Inactive tabs are gray/transparent
- [ ] No errors when switching tabs
- [ ] Each tab maintains its state

### Step 8: Test Close Button

**What to test:**
- [ ] Click "Close" button (red, top right)
- [ ] Admin panel closes
- [ ] Returns to dashboard view
- [ ] Can reopen admin panel
- [ ] Previous tab selection is remembered (or resets to Users)

---

## 📊 Expected Results

### Database Monitoring Tab

**Summary Cards should show approximately:**
```
Total Tables: 5
Healthy Tables: 5
Total Records: 660K (or more depending on how long you've been collecting)
Total Size: 2.25 GB (approximately)
```

**Tables should show:**
```
crypto_analysis:
- Rows: 60,000+ (depends on how many days of data)
- Size: 0.25 GB
- Pairs: 675
- 24h Records: 675 (one per pair per day)

crypto_hourly_data:
- Rows: 450,000+
- Size: 1.50 GB
- Pairs: 675
- 24h Records: 16,200 (675 pairs × 24 hours)

crypto_5min_top10_gainers:
- Rows: 150,000+
- Size: 0.50 GB
- Pairs: 10
- 24h Records: 2,880 (10 pairs × 288 five-min intervals)

users:
- Rows: 1-10 (your users)
- Size: < 0.01 GB
- Pairs: N/A

search_history:
- Rows: varies
- Size: < 0.01 GB
- Pairs: N/A
```

**Data Quality should show:**
```
crypto_analysis: 100.0% (or close to it)
crypto_hourly_data: 100.0% (or close to it)

If any missing dates, they'll be listed in red.
```

### Billing Dashboard

**Should show:**
```
Total Monthly Cost: $238.30

Breakdown:
- Compute & Functions: $168.00 (71%)
- AI & ML Services: $60.00 (25%)
- Data Storage: $7.00 (3%)
- Other: $3.30 (1%)

Top Services:
1. Hourly Crypto Fetcher: $72.00
2. 5-Min Crypto Fetcher: $50.00
3. Claude API: $40.00
4. AI Intelligence: $35.00
... and more
```

---

## 🐛 Troubleshooting

### Issue: "Error Loading Monitoring Data"

**Cause**: Frontend can't reach monitoring function

**Check:**
1. Monitoring function URL is correct in `.env`
2. Function is deployed and active:
   ```bash
   gcloud functions describe system-monitoring --region=us-central1
   ```
3. Function is publicly accessible:
   ```bash
   gcloud functions get-iam-policy system-monitoring --region=us-central1
   ```

**Solution:**
```bash
# Make function public
gcloud functions add-invoker-policy-binding system-monitoring \
  --region=us-central1 \
  --member=allUsers \
  --project=cryptobot-462709
```

### Issue: "No Data Available" or Empty Tables

**Cause**: BigQuery tables are empty

**Check:**
```bash
# Check table counts
python check_bigquery_counts.py
```

**Solution:**
```bash
# Trigger data collection
curl https://daily-crypto-fetcher-cnyn5l4u2a-uc.a.run.app
curl https://hourly-crypto-fetcher-cnyn5l4u2a-uc.a.run.app
```

### Issue: Admin Tab Not Showing

**Cause**: User is not admin

**Check**: Your user role in the database

**Solution**: Update your user role to 'admin' in BigQuery users table

### Issue: Charts Not Rendering

**Cause**: Missing Recharts library or data format issue

**Check**: Browser console for errors (F12 → Console)

**Solution**:
```bash
cd stock-price-app
npm install recharts
```

### Issue: Billing Shows $0 or Wrong Amounts

**Cause**: Using estimated costs (not actual GCP billing)

**Note**: Current implementation uses cost estimates. To get actual billing:
1. Enable Cloud Billing API
2. Update monitoring function with billing account access

**For now**: Estimated costs are shown for planning purposes

### Issue: Auto-refresh Not Working

**Cause**: Background tab or browser throttling

**Check**: Keep tab active for 5+ minutes

**Note**: Browser may throttle timers in background tabs

---

## ✅ Testing Checklist

Use this checklist to verify everything works:

### Basic Functionality
- [ ] Can access localhost:5173
- [ ] Can login successfully
- [ ] Admin menu item is visible
- [ ] Can open admin panel
- [ ] Admin panel overlay covers screen
- [ ] Three tabs are visible

### User Management Tab
- [ ] User list loads
- [ ] Can create user
- [ ] Can edit user
- [ ] Can delete user
- [ ] Can send invitation

### Database Monitoring Tab
- [ ] Summary cards display
- [ ] Tables grid populates
- [ ] All 5 tables shown
- [ ] Row counts are reasonable
- [ ] Latest timestamps are recent
- [ ] Status badges show "Healthy"
- [ ] Data quality section displays
- [ ] Can switch to Growth view
- [ ] Growth charts render
- [ ] Can switch to Top Pairs view
- [ ] Top pairs list displays
- [ ] Refresh button works
- [ ] Last refresh time updates

### Billing Dashboard Tab
- [ ] Summary cards display
- [ ] Total cost shows ~$238
- [ ] Pie chart renders
- [ ] Bar chart renders
- [ ] Detailed table displays
- [ ] All services listed
- [ ] Percentages calculated
- [ ] Total matches sum
- [ ] Optimization tips show

### Navigation & UX
- [ ] Can switch between tabs smoothly
- [ ] Active tab is highlighted
- [ ] No console errors
- [ ] No visual glitches
- [ ] Close button works
- [ ] Can reopen admin panel

---

## 📸 What You Should See

### Admin Panel Header
```
┌────────────────────────────────────────────────────────────┐
│  ⚙️ Admin Dashboard                              [X] Close │
├────────────────────────────────────────────────────────────┤
│  [👥 User Management] [💾 Database Monitoring] [$💵 Billing]│
└────────────────────────────────────────────────────────────┘
```

### Database Monitoring - Overview
```
┌─────────┬─────────┬─────────┬─────────┐
│ Total   │ Healthy │ Total   │ Total   │
│ Tables  │ Tables  │ Records │ Size    │
│   5     │   5     │  660K   │ 2.25 GB │
└─────────┴─────────┴─────────┴─────────┘

BigQuery Tables
──────────────────────────────────────────────────
Table               Rows    Size    Status
──────────────────────────────────────────────────
crypto_analysis     60K     0.25GB  ✓ Healthy
crypto_hourly       450K    1.50GB  ✓ Healthy
crypto_5min         150K    0.50GB  ✓ Healthy
users               5       0.00GB  ✓ Healthy
search_history      100     0.00GB  ✓ Healthy
──────────────────────────────────────────────────
```

### Billing Dashboard
```
┌─────────────────────────────────────────────┐
│  💵 Total Monthly Cost: $238.30             │
├─────────────────────────────────────────────┤
│  Compute: $168 │ AI/ML: $60 │ Storage: $7  │
└─────────────────────────────────────────────┘

[Pie Chart showing cost breakdown]

[Bar Chart showing costs by service]

Detailed Cost Breakdown
─────────────────────────────────────
Service              Category   Cost    %
─────────────────────────────────────
Hourly Fetcher       Compute   $72.00  30%
5-Min Fetcher        Compute   $50.00  21%
Claude API           AI/ML     $40.00  17%
...
─────────────────────────────────────
TOTAL                          $238.30 100%
```

---

## 🎯 Key Testing Points

### Performance
- [ ] Tabs switch instantly (<100ms)
- [ ] Charts render within 1-2 seconds
- [ ] Data loads within 3-5 seconds
- [ ] No lag when scrolling tables
- [ ] Refresh completes within 5 seconds

### Data Accuracy
- [ ] Row counts match BigQuery console
- [ ] Timestamps are current (within minutes)
- [ ] Costs add up correctly (total = sum)
- [ ] Percentages add to 100%
- [ ] Pair counts are correct (675 for full crypto)

### Visual Quality
- [ ] All text is readable
- [ ] Colors are consistent
- [ ] Badges are styled properly
- [ ] Charts have proper labels
- [ ] Tables are well-formatted
- [ ] No overlapping elements

### Error Handling
- [ ] Loading states display
- [ ] Error messages are clear
- [ ] Retry buttons work
- [ ] Graceful degradation (partial data)

---

## 📝 Test Report Template

After testing, fill this out:

### Date: _____________
### Tester: _____________

#### User Management Tab
- Status: ✅ Pass / ❌ Fail
- Notes: _________________________________

#### Database Monitoring Tab
- Status: ✅ Pass / ❌ Fail
- Summary Cards: ✅ / ❌
- Tables Grid: ✅ / ❌
- Data Quality: ✅ / ❌
- Growth Charts: ✅ / ❌
- Top Pairs: ✅ / ❌
- Refresh: ✅ / ❌
- Notes: _________________________________

#### Billing Dashboard Tab
- Status: ✅ Pass / ❌ Fail
- Summary Cards: ✅ / ❌
- Pie Chart: ✅ / ❌
- Bar Chart: ✅ / ❌
- Detailed Table: ✅ / ❌
- Notes: _________________________________

#### Overall Rating
- Functionality: __ / 10
- Performance: __ / 10
- Visual Quality: __ / 10
- User Experience: __ / 10

#### Issues Found
1. _________________________________
2. _________________________________
3. _________________________________

#### Recommendations
1. _________________________________
2. _________________________________

---

## 🚀 Next Steps After Testing

### If Everything Works:
1. ✅ Document test results
2. ✅ Take screenshots for reference
3. ✅ Consider deploying to production
4. ✅ Set up billing alerts in GCP
5. ✅ Schedule weekly monitoring reviews

### If Issues Found:
1. 📝 Document all issues clearly
2. 🔍 Check browser console for errors
3. 📊 Verify data in BigQuery directly
4. 🛠️ Report issues for fixing
5. 🔄 Retest after fixes

---

## 📞 Support

### View Logs
```bash
# Monitoring function logs
gcloud functions logs read system-monitoring --limit=50 --project=cryptobot-462709

# Check for errors
gcloud functions logs read system-monitoring --limit=50 --project=cryptobot-462709 | findstr ERROR
```

### Test Function Directly
```bash
# Test monitoring endpoint (PowerShell)
Invoke-WebRequest -Uri "https://system-monitoring-cnyn5l4u2a-uc.a.run.app?endpoint=tables"

# Or in browser
https://system-monitoring-cnyn5l4u2a-uc.a.run.app?endpoint=full
```

### Check BigQuery
1. Go to: https://console.cloud.google.com/bigquery
2. Project: cryptobot-462709
3. Dataset: crypto_trading_data
4. Browse tables and verify data

---

## ✨ Success Criteria

Your testing is successful when:

✅ All three tabs load without errors
✅ Database monitoring shows correct table counts
✅ Billing dashboard shows cost breakdown
✅ Charts render properly
✅ Refresh button works
✅ Navigation between tabs is smooth
✅ No console errors
✅ Data is recent (timestamps within last hour for hourly, last day for daily)
✅ Performance is good (loads in < 5 seconds)
✅ Visual quality is professional

---

## 🎓 Ready to Test!

**Your app is running at: http://localhost:5173/**

**Steps to start testing:**
1. Open http://localhost:5173/
2. Login as admin
3. Click "Admin" in left menu
4. Test each tab systematically
5. Use the checklist above
6. Report any issues

**Good luck with testing!** 🚀
