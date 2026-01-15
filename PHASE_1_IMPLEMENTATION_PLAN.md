# 🚀 Phase 1 ML Implementation Plan
## Mathematical Model Training for AIAlgoTradeHits.com

**Date:** December 6, 2025  
**For Review By:** Irfan Saheb  
**Prepared By:** AI Development Team

---

## 📋 Executive Summary

This document outlines the **Phase 1 implementation plan** for training ML models using mathematical features (not user-uploaded strategies). We will start with:

- **3 symbols:** BTC-USD, SPY, QQQ
- **5 features:** RSI, MACD, Volume Ratio, SMA-50, Close Price
- **1 timeframe:** Daily (1d)
- **Platform:** BigQuery ML + Vertex AI + Gemini 2.5 Pro

**Goal:** Achieve 55-58% directional accuracy baseline, then expand to 24 features in future phases.

---

## 🎯 What We're Building

### The Complete System Flow:

```
┌─────────────────────────────────────────────────┐
│  EXISTING: TwelveData API → BigQuery            │
│  (Already working - OHLCV data ingestion)       │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  NEW: Feature Calculation (SQL)                 │
│  - Calculate RSI, MACD, Volume, SMA             │
│  - Store in features_phase1 table               │
│  - Run daily after market close                 │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  NEW: Model Training (BigQuery ML)              │
│  - Train XGBoost classifier                     │
│  - Learn from historical patterns               │
│  - Retrain monthly                              │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  NEW: Daily Predictions (SQL)                   │
│  - Predict direction for BTC, SPY, QQQ          │
│  - Store in ml_predictions table                │
│  - Run daily                                    │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  NEW: Gemini Integration (Python)               │
│  - Read predictions from BigQuery               │
│  - Send to Gemini 2.5 Pro                       │
│  - Get natural language explanation             │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  WEBSITE: Display to Users                      │
│  - "BTC: 72% UP (High Confidence)"              │
│  - Gemini explanation                           │
│  - Feature breakdown                            │
└─────────────────────────────────────────────────┘
```

---

## 📦 Deliverables - What You'll Receive

We will create **6 files** for you:

### **File 1: `feature_calculation.sql`**
**Purpose:** Calculate the 5 features from OHLCV data  
**What it does:**
- Queries existing BigQuery OHLCV table
- Calculates RSI (14-period)
- Calculates MACD Histogram
- Calculates Volume Ratio (current volume / 20-day average)
- Calculates SMA-50
- Creates target variable (price up next day = 1, down = 0)
- Stores results in `features_phase1` table

**How to use:**
- Copy/paste into BigQuery Console
- Update project/dataset names
- Run it (creates new table)
- Schedule to run daily

**Output table example:**
```
symbol  | timestamp           | close | rsi_14d | macd_hist | vol_ratio | sma_50 | target
--------|---------------------|-------|---------|-----------|-----------|--------|--------
BTC-USD | 2024-12-01 00:00:00 | 48200 | 35.2    | 0.05      | 1.3       | 47800  | 1
BTC-USD | 2024-12-02 00:00:00 | 49100 | 42.8    | 0.12      | 1.8       | 48000  | 1
SPY     | 2024-12-01 00:00:00 | 450   | 55.3    | -0.02     | 0.9       | 448    | 0
QQQ     | 2024-12-01 00:00:00 | 380   | 48.2    | 0.08      | 1.1       | 378    | 1
```

---

### **File 2: `model_training.sql`**
**Purpose:** Train XGBoost ML model  
**What it does:**
- Takes `features_phase1` table from File 1
- Trains XGBoost classification model using BigQuery ML
- Evaluates model performance (accuracy, precision, recall)
- Saves trained model as `trading_model_phase1`

**How to use:**
- Run ONCE initially to train model
- Retrain monthly with new data
- Takes ~2-5 minutes to complete

**Output:**
```
Model created: project.dataset.trading_model_phase1

Evaluation Metrics:
├── Accuracy:  58.3%
├── Precision: 60.1%
├── Recall:    56.8%
├── AUC:       0.625
└── F1 Score:  0.584

Status: Training complete ✓
```

---

### **File 3: `make_predictions.sql`**
**Purpose:** Generate daily predictions  
**What it does:**
- Uses trained model from File 2
- Makes predictions on latest/today's features
- Assigns confidence level (HIGH/MEDIUM/LOW)
- Determines signal (BUY/SELL/HOLD)
- Stores in `ml_predictions` table

**How to use:**
- Run daily after market close
- Schedule as automated query
- Can run on-demand for testing

**Output table example:**
```
symbol  | timestamp           | prediction_proba | confidence | signal | top_feature
--------|---------------------|------------------|------------|--------|-------------
BTC-USD | 2024-12-06 00:00:00 | 0.72            | HIGH       | BUY    | rsi_14d
SPY     | 2024-12-06 00:00:00 | 0.45            | LOW        | HOLD   | volume_ratio
QQQ     | 2024-12-06 00:00:00 | 0.68            | MEDIUM     | BUY    | macd_histogram
```

---

### **File 4: `gemini_integration.py`**
**Purpose:** Connect predictions to Gemini for explanations  
**What it does:**
- Python script that runs on Cloud Functions/Cloud Run
- Reads predictions from BigQuery (`ml_predictions` table)
- Reads features from BigQuery (`features_phase1` table)
- Constructs prompt for Gemini 2.5 Pro
- Gets natural language explanation
- Returns to frontend

**How to use:**
- Deploy to Cloud Functions (recommended) or Cloud Run
- Call via HTTP API from your website
- Runs when user requests prediction explanation

**Example flow:**
```python
# Input
symbol = "BTC-USD"

# Script fetches from BigQuery:
prediction = {
    'confidence': 0.72,
    'signal': 'BUY',
    'top_feature': 'rsi_14d'
}

features = {
    'rsi_14d': 35.2,
    'macd_histogram': 0.05,
    'volume_ratio': 1.3,
    'sma_50': 47800
}

# Sends to Gemini:
prompt = f"""
BTC-USD ML Prediction:
- Probability: 72% UP
- Confidence: HIGH

Current Features:
- RSI: 35.2 (oversold)
- MACD Histogram: 0.05 (bullish)
- Volume Ratio: 1.3x average
- SMA-50: $47,800

Explain this prediction in simple terms for a trader.
"""

# Gemini returns:
"Bitcoin shows a 72% probability of upward movement with high 
confidence. The RSI at 35.2 indicates oversold conditions where 
price typically rebounds. The MACD histogram turned positive, 
showing bullish momentum building. Volume is 1.3x the average, 
confirming trader interest in the move. With price currently 
above the 50-day moving average support at $47,800, technical 
indicators are aligned for an upward move."
```

---

### **File 5: `README_PHASE1.md`**
**Purpose:** Complete step-by-step setup guide  
**What it includes:**
- Prerequisites checklist
- Day 1 implementation steps
- How to verify each step worked
- Troubleshooting common issues
- Expected results at each stage
- Next steps after Phase 1 success

---

### **File 6: `setup_instructions.md`**
**Purpose:** How to schedule automated queries  
**What it includes:**
- How to schedule File 1 (daily feature calculation)
- How to schedule File 3 (daily predictions)
- How to set up Cloud Function for File 4
- How to deploy and test
- Monitoring and alerts setup

---

## 🔧 Technical Requirements

### What We Need From You (Irfan Saheb)

#### **1. BigQuery Configuration**

Please provide the following details:

```
GCP Project ID: ______________________________
  Example: aialgotradehits-prod

Dataset Name: ________________________________
  Example: trading_data

OHLCV Table Name: ____________________________
  Example: ohlcv_data or market_data_daily
```

#### **2. Table Schema Confirmation**

Please run this query and share the results:

```sql
-- Check what columns exist in your OHLCV table
SELECT column_name, data_type
FROM `your-project.your-dataset.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'your-ohlcv-table'
ORDER BY ordinal_position;
```

**Common schemas (which one matches yours?):**

**Option A:**
```
timestamp (TIMESTAMP)
symbol (STRING)
open (FLOAT64)
high (FLOAT64)
low (FLOAT64)
close (FLOAT64)
volume (FLOAT64)
```

**Option B:**
```
date (DATE)
ticker (STRING)
open_price (FLOAT64)
high_price (FLOAT64)
low_price (FLOAT64)
close_price (FLOAT64)
volume (INT64)
```

**Or something else?** Please specify exact column names.

#### **3. Historical Data Check**

Please run this query and share the results:

```sql
-- Check date range and row counts for our 3 symbols
SELECT 
  symbol,
  MIN(timestamp) as earliest_date,
  MAX(timestamp) as latest_date,
  COUNT(*) as total_rows,
  COUNT(DISTINCT DATE(timestamp)) as unique_days
FROM `your-project.your-dataset.ohlcv_data`
WHERE symbol IN ('BTC-USD', 'SPY', 'QQQ')
GROUP BY symbol
ORDER BY symbol;
```

**Expected output (ideally):**
```
symbol  | earliest_date | latest_date | total_rows | unique_days
--------|---------------|-------------|------------|-------------
BTC-USD | 2021-12-01    | 2024-12-06  | 1095       | 1095
SPY     | 2021-12-01    | 2024-12-06  | 1095       | 1095
QQQ     | 2021-12-01    | 2024-12-06  | 1095       | 1095
```

**We need at least:**
- ✅ 2 years of data (730 days) - Minimum
- ✅ 3 years of data (1095 days) - Good
- ✅ 5 years of data (1825 days) - Ideal

**If less than 2 years:** We can still proceed but accuracy may be lower.

#### **4. Deployment Environment**

Where should the Python code (File 4) run?

**Option A: Cloud Functions** (Recommended)
- ✅ Serverless (no server management)
- ✅ Auto-scales
- ✅ Pay per use
- ✅ Easy to deploy
- Setup time: 15 minutes

**Option B: Cloud Run**
- ✅ More control
- ✅ Can run containers
- ✅ Good for complex apps
- Setup time: 30 minutes

**Option C: Existing Backend Server**
- ✅ Full control
- ✅ Can integrate with existing code
- ❌ Need to manage server
- Setup time: Depends on your setup

**Which do you prefer?** (If unsure, we recommend Cloud Functions)

#### **5. API Access Verification**

Please confirm these are enabled in your GCP project:

```
□ BigQuery API - Enabled
□ Vertex AI API - Enabled  
□ Cloud Functions API - Enabled (if using Option A above)
□ Cloud Run API - Enabled (if using Option B above)
□ Cloud Storage API - Enabled
```

**To check:**
1. Go to: https://console.cloud.google.com/apis/dashboard
2. Search for each API above
3. Verify "Enabled" status

If any are not enabled, we'll include setup instructions.

---

## 📊 Expected Results

### Phase 1 Success Metrics:

**Week 1 Completion:**
- ✅ All 4 SQL/Python files deployed
- ✅ Features calculating daily
- ✅ Model trained successfully
- ✅ Predictions generating daily
- ✅ Gemini explanations working

**Accuracy Targets:**
- **Baseline:** 55-58% directional accuracy
  - This beats random guessing (50%)
  - This is expected with only 5 features
  - Proves the pipeline works

**If we achieve 55-58% in Phase 1:**
- ✅ Proceed to Phase 2 (add 5 more features → 60-63% expected)
- ✅ System architecture validated
- ✅ Ready to scale to more symbols

**If accuracy is below 55%:**
- Check data quality (gaps, errors?)
- Verify feature calculations are correct
- May need more historical data
- Troubleshoot before expanding

---

## 📈 Phased Roadmap (After Phase 1)

### **Phase 1 (Weeks 1-2):** ← **WE ARE HERE**
- 3 symbols: BTC, SPY, QQQ
- 5 features: RSI, MACD, Volume, SMA, Close
- 1 timeframe: Daily
- Target: 55-58% accuracy
- Platform: BigQuery ML

### **Phase 2 (Weeks 3-4):**
- Same 3 symbols
- **10 features total** (add ATR, Bollinger, EMA, ADX, OBV)
- 1 timeframe: Daily
- Target: 60-63% accuracy
- Platform: BigQuery ML

### **Phase 3 (Weeks 5-6):**
- Same 3 symbols
- **15 features total** (add VWAP, Volume Profile, Fibonacci, Pivots, Regime)
- 1 timeframe: Daily
- Target: 65-68% accuracy
- Platform: BigQuery ML + Vertex AI

### **Phase 4 (Weeks 7-8):**
- Same 3 symbols
- **24 features total** (add Candlestick patterns, multi-timeframe, etc.)
- Multi-timeframe: 1h, 4h, 1d
- Target: 66-72% accuracy
- Platform: Vertex AI (Ensemble models)

### **Phase 5 (Weeks 9-10):**
- **Expand to 50+ symbols**
- All 24 features
- Multi-timeframe
- Multiple asset classes (Crypto, Stocks, ETFs)
- Production deployment

---

## 🎯 Phase 1 Implementation Timeline

### **Day 1 (2 hours):**
**Morning:**
- Irfan provides required information (see Section above)
- We customize all files with your project/dataset names
- We deliver the 6 files

**Afternoon:**
- You test File 1 (feature calculation)
- Verify `features_phase1` table created successfully
- Check data looks correct

### **Day 2 (2 hours):**
**Morning:**
- Run File 2 (model training)
- Wait ~5 minutes for training
- Review evaluation metrics

**Afternoon:**
- Run File 3 (predictions)
- Verify `ml_predictions` table created
- Check predictions for BTC, SPY, QQQ

### **Day 3 (3 hours):**
**All day:**
- Deploy File 4 (Gemini integration)
- Test Python script locally
- Deploy to Cloud Functions/Cloud Run
- Test end-to-end flow

### **Day 4 (2 hours):**
**Morning:**
- Schedule automated queries (Files 1 & 3)
- Set up daily runs

**Afternoon:**
- Integrate with frontend (your website)
- Display predictions to users
- Test user experience

### **Day 5 (1 hour):**
- Monitor first full day of automated predictions
- Validate accuracy next day
- Document any issues

---

## 💰 Cost Estimate (Phase 1)

### BigQuery:
- Storage: ~$0.02/GB/month
- Queries: ~$5/TB processed
- **Estimated:** $10-20/month for 3 symbols

### Vertex AI / Gemini:
- Gemini 2.5 Pro: $0.00125 per 1K input tokens
- Typical query: ~500 tokens
- If 1000 explanations/day: ~$0.63/day = $19/month
- **Estimated:** $20-30/month

### Cloud Functions (if used):
- First 2 million invocations free
- $0.40 per million after that
- **Estimated:** Free for Phase 1 volume

### **Total Phase 1 Monthly Cost:** $30-50/month

---

## ❓ Questions for Irfan Saheb

Please provide answers to these questions:

### **1. BigQuery Details:**
```
Project ID: _______________
Dataset: _______________
OHLCV Table: _______________
```

### **2. Table Schema:**
Please run the INFORMATION_SCHEMA query above and share:
- Exact column names
- Data types
- Any differences from "Option A" schema

### **3. Historical Data:**
Please run the date range query above and share:
- How many days of data do we have?
- Are there any gaps in the data?
- Any known data quality issues?

### **4. Deployment Preference:**
For File 4 (Python code), which option?
- □ Option A: Cloud Functions (Recommended)
- □ Option B: Cloud Run
- □ Option C: Existing server (please describe)

### **5. API Access:**
Are these APIs enabled in GCP?
- □ BigQuery API
- □ Vertex AI API
- □ Cloud Functions/Run API
- □ Cloud Storage API

### **6. Symbol Names Verification:**
In your BigQuery table, are the symbols exactly:
- "BTC-USD" or "BTCUSD" or "BTC" or something else?
- "SPY" or "SPY.US" or something else?
- "QQQ" or "QQQ.US" or something else?

### **7. Timezone:**
What timezone is your timestamp column in?
- UTC (recommended)
- US Eastern
- Other: _______________

### **8. Any Constraints or Requirements:**
- Any security/compliance requirements?
- Any preferred naming conventions?
- Any existing infrastructure to integrate with?
- Any budget constraints?

---

## 🚀 Next Steps

**Once Irfan provides the information above:**

1. **Within 24 hours:** We deliver customized Phase 1 files
2. **Days 1-3:** Implementation and testing (with our support)
3. **Days 4-5:** Automation and monitoring setup
4. **End of Week 1:** Phase 1 operational, generating predictions
5. **Week 2:** Monitor accuracy, gather feedback, plan Phase 2

---

## 📞 Support & Communication

**During Implementation:**
- We'll be available for questions/troubleshooting
- Screen sharing sessions if needed
- Documentation for every step

**Success Criteria:**
- ✅ Model trains without errors
- ✅ Predictions generate daily
- ✅ Accuracy ≥ 55%
- ✅ Gemini explanations working
- ✅ Team understands the system

---

## 📋 Summary

**What We're Building:**
- Mathematical ML model (not user strategies)
- Starting simple: 5 features, 3 symbols, daily timeframe
- BigQuery ML for ease of implementation
- Gemini for natural language explanations

**What We Need:**
- BigQuery configuration details
- Table schema confirmation
- Historical data verification
- Deployment preference
- API access confirmation

**What You'll Get:**
- 6 ready-to-use files
- Complete documentation
- Step-by-step implementation guide
- Support during deployment
- Working ML prediction system in ~5 days

**Timeline:**
- Information from Irfan: 1 day
- File customization: 1 day
- Implementation: 3 days
- **Total: ~5 business days to live system**

---

## ✅ Approval & Sign-Off

**For Review By:** Irfan Saheb  
**Please confirm:**
- □ I understand the Phase 1 plan
- □ I agree with the phased approach (5 → 10 → 15 → 24 features)
- □ I can provide the requested information
- □ Timeline is acceptable
- □ Ready to proceed

**Once approved, please provide:**
1. Answers to the 8 questions above
2. Any additional requirements or concerns
3. Best time to schedule implementation kickoff call

---

**Document Version:** 1.0  
**Date:** December 6, 2025  
**Status:** Awaiting Irfan's Feedback

---

*This is a living document and will be updated based on feedback and requirements.*
