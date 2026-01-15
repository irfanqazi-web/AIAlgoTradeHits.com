# ML Walk-Forward Validation System
## Gap Analysis & Implementation Plan

**Date:** January 9, 2026
**Document Version:** 1.0
**Status:** PENDING IRFAN APPROVAL

---

## EXECUTIVE SUMMARY

This document analyzes the ML Walk-Forward Validation System specification against current implementation, identifies gaps, and proposes an implementation plan.

**Current State:** ~60% Complete
**Estimated Remaining Effort:** 20-30 hours

---

## PART 1: GAP ANALYSIS

### Already Implemented (What We Have)

| # | Component | Status | Notes |
|---|-----------|--------|-------|
| 1 | XGBoost Model Training | ✅ DONE | Using BigQuery ML |
| 2 | Walk-Forward 3-Period Split | ✅ DONE | Train/Test/Validate |
| 3 | Prediction Storage | ✅ DONE | walk_forward_predictions_v2 |
| 4 | Sector-Specific Models | ✅ DONE | 86.4% avg accuracy (5 sectors) |
| 5 | Model Drift Detection | ✅ DONE | ml_phase5_model_monitoring.py |
| 6 | Real-time Inference | ✅ DONE | ml_phase6_realtime_inference.py |
| 7 | Backtesting Framework | ✅ DONE | ml_phase7_backtesting_framework.py |
| 8 | Basic ML API Endpoints | ✅ DONE | /api/ml/predictions, etc. |
| 9 | Cloud Schedulers | ✅ DONE | Daily inference, monitoring |
| 10 | Sector Classification | ✅ DONE | 346 stocks, 11 sectors |
| 11 | Sentiment Integration | ✅ DONE | 12,155 records |

### Missing Components (Gaps)

| # | Component | Priority | Effort | Description |
|---|-----------|----------|--------|-------------|
| 1 | **Interactive Dashboard UI** | P0 | 12-16 hrs | React component for walk-forward config & results |
| 2 | **Walk-Forward Cloud Function** | P0 | 8-10 hrs | Dedicated function with progress tracking |
| 3 | **The 16 Validated Features** | P0 | 2 hrs | Verify/add specific features from spec |
| 4 | **Walk-Forward API Endpoints** | P0 | 4-6 hrs | Full CRUD for runs |
| 5 | **model_versions Table** | P1 | 1 hr | Track all model versions |
| 6 | **walk_forward_runs Table** | P1 | 1 hr | Run-level summaries |
| 7 | **Confidence Threshold Filters** | P1 | 2 hrs | 50%, 60%, 70%, 80% filtering |
| 8 | **Rolling Accuracy Charts** | P1 | 3 hrs | 30-day rolling accuracy viz |
| 9 | **Multi-Ticker Support** | P2 | 3 hrs | 1-5 tickers per run |
| 10 | **CSV Export** | P2 | 1 hr | Export results |
| 11 | **Progress Tracking** | P2 | 2 hrs | Real-time progress updates |
| 12 | **Cancellation Support** | P3 | 1 hr | Cancel long runs |
| 13 | **A/B Testing Framework** | P3 | 4 hrs | Compare feature sets |
| 14 | **Model Artifact Storage** | P3 | 2 hrs | Store .pkl in GCS |

---

## PART 2: DETAILED GAP ANALYSIS

### Gap 1: Interactive Dashboard UI (P0)

**Current State:** No dedicated walk-forward UI component exists in Trading App

**Required:**
- Configuration panel with:
  - Asset class dropdown (Equity, FX, Crypto, Commodities)
  - Ticker multi-select (max 5)
  - Feature selection toggle (16 default vs 97 advanced)
  - Date range pickers (Train start, Test start)
  - Validation window dropdown (6 months, 1 year, 2 years)
  - Walk-forward days slider (1-500)
  - Retraining frequency dropdown (daily, weekly, monthly)
  - Confidence threshold slider
- Results display:
  - Summary cards (accuracy metrics)
  - Equity curve chart
  - Rolling accuracy chart
  - Detailed results table (sortable, filterable)
- Run controls:
  - RUN VALIDATION button
  - Progress indicator
  - Cancel button

**Files to Create:**
- `stock-price-app/src/components/WalkForwardValidation.jsx`
- `stock-price-app/src/components/WalkForwardResults.jsx`
- `stock-price-app/src/components/WalkForwardCharts.jsx`

---

### Gap 2: Walk-Forward Cloud Function (P0)

**Current State:** Basic backtesting exists, but not the full walk-forward engine

**Required:**
- Dedicated Cloud Function/Run for walk-forward validation
- Day-by-day prediction loop
- Configurable retraining (daily, weekly, monthly)
- Progress tracking in BigQuery
- Support for 500-day runs
- Batch result insertion

**Files to Create:**
- `cloud_function_walk_forward/main.py`
- `cloud_function_walk_forward/requirements.txt`

---

### Gap 3: The 16 Validated Features (P0)

**Current State:** Using different feature set (rsi, macd, adx, etc.)

**Specified 16 Features:**
```
1. pivot_low_flag      2. pivot_high_flag
3. rsi                 4. rsi_slope
5. rsi_zscore          6. rsi_overbought
7. rsi_oversold        8. macd
9. macd_signal        10. macd_histogram
11. macd_cross        12. momentum
13. mfi               14. cci
15. awesome_osc       16. vwap_daily
```

**Action:** Verify these columns exist in BigQuery tables and update model training

---

### Gap 4: Walk-Forward API Endpoints (P0)

**Current Endpoints:**
- GET /api/ml/predictions ✅
- GET /api/ml/high-confidence-signals ✅
- GET /api/ml/walk-forward-summary ✅

**Missing Endpoints:**
- POST /api/ml/walk-forward/run (start validation)
- GET /api/ml/walk-forward/runs (list all runs)
- GET /api/ml/walk-forward/runs/{run_id} (run details)
- GET /api/ml/walk-forward/runs/{run_id}/results (daily results)
- DELETE /api/ml/walk-forward/runs/{run_id} (cancel run)
- GET /api/ml/features (list available features)
- GET /api/ml/tickers/{asset_class} (list tickers)
- GET /api/ml/models/versions (model versions)
- POST /api/ml/alerts/{alert_id}/acknowledge

---

### Gap 5: BigQuery Schema Updates (P1)

**Existing Tables:**
- walk_forward_predictions_v2 ✅
- model_drift_alerts ✅
- stock_sector_features ✅
- sector_model_results ✅

**Missing Tables:**

**Table: ml_models.walk_forward_runs**
```sql
CREATE TABLE ml_models.walk_forward_runs (
    run_id STRING NOT NULL,
    run_timestamp TIMESTAMP,
    user_id STRING,
    symbols STRING,
    asset_class STRING,
    train_start DATE,
    validation_window_days INT64,
    test_start DATE,
    walk_forward_days INT64,
    retrain_frequency STRING,
    features_mode STRING,
    overall_accuracy FLOAT64,
    up_accuracy FLOAT64,
    down_accuracy FLOAT64,
    status STRING,
    progress_pct FLOAT64,
    error_message STRING
)
```

**Table: ml_models.model_versions**
```sql
CREATE TABLE ml_models.model_versions (
    version_id STRING NOT NULL,
    created_at TIMESTAMP,
    model_path STRING,
    features_used STRING,
    train_samples INT64,
    validation_accuracy FLOAT64,
    is_active BOOL
)
```

---

## PART 3: IMPLEMENTATION PLAN

### Phase 1: Core Backend (Week 1)

| Task | Hours | Owner |
|------|-------|-------|
| Create walk_forward_runs table | 0.5 | Claude |
| Create model_versions table | 0.5 | Claude |
| Verify 16 validated features | 1 | Claude |
| Create walk-forward Cloud Function | 8 | Claude |
| Add API endpoints to Trading API | 4 | Claude |
| **Subtotal** | **14 hrs** | |

### Phase 2: Dashboard UI (Week 2)

| Task | Hours | Owner |
|------|-------|-------|
| WalkForwardValidation.jsx (config) | 6 | Claude |
| WalkForwardResults.jsx (results) | 4 | Claude |
| WalkForwardCharts.jsx (charts) | 4 | Claude |
| Integration testing | 2 | Claude |
| **Subtotal** | **16 hrs** | |

### Phase 3: Advanced Features (Week 3)

| Task | Hours | Owner |
|------|-------|-------|
| Confidence threshold filtering | 2 | Claude |
| Rolling accuracy calculation | 2 | Claude |
| CSV export | 1 | Claude |
| Progress tracking | 2 | Claude |
| Multi-ticker support | 3 | Claude |
| **Subtotal** | **10 hrs** | |

### Phase 4: Testing & Deployment (Week 4)

| Task | Hours | Owner |
|------|-------|-------|
| End-to-end testing | 4 | Claude/Saleem |
| 500-day validation runs | 2 | Claude |
| Bug fixes | 4 | Claude |
| Documentation | 2 | Claude |
| **Subtotal** | **12 hrs** | |

---

## PART 4: QUESTIONS FOR IRFAN

### Q1: Cloud Infrastructure
**Options:**
- A) Cloud Function Gen2 (60-min timeout) - Good for runs up to 200 days
- B) Cloud Run Jobs (24-hour timeout) - Required for 500-day runs

**Recommendation:** Cloud Run Jobs for flexibility

### Q2: Model Storage Bucket
**Suggested:** `gs://aialgotradehits-ml-models/`

### Q3: Priority Order
Should we implement in this order?
1. Core Backend (Cloud Function + API)
2. Dashboard UI
3. Advanced Features

Or different priority?

### Q4: Multi-Ticker Mode
**Options:**
- A) Individual mode only (train separate model per ticker)
- B) Combined mode only (single model for all tickers)
- C) Both modes (user selects)

**Recommendation:** Start with Individual mode, add Combined later

---

## PART 5: COST ESTIMATES

### Development Cost (One-Time)
| Item | Hours | Rate | Cost |
|------|-------|------|------|
| Backend Development | 14 | $0 (Claude) | $0 |
| UI Development | 16 | $0 (Claude) | $0 |
| Advanced Features | 10 | $0 (Claude) | $0 |
| Testing | 12 | $0 (Claude) | $0 |
| **Total Dev** | **52 hrs** | | **$0** |

### Infrastructure Cost (Monthly Incremental)
| Resource | Usage | Cost/Month |
|----------|-------|------------|
| Cloud Run Jobs | ~50 runs @ 30 min | $15-25 |
| BigQuery Storage | ~5 GB new tables | $0.10 |
| BigQuery Queries | ~200 GB scanned | $1.00 |
| Cloud Storage | ~500 MB models | $0.01 |
| **Total** | | **~$20-30** |

---

## PART 6: SUMMARY

### What's Already Done
- ✅ XGBoost model training (BigQuery ML)
- ✅ 3-period walk-forward validation
- ✅ Sector-specific models (86.4% avg accuracy)
- ✅ Model drift detection & monitoring
- ✅ Basic ML API endpoints
- ✅ Cloud schedulers for automation

### What's Missing
- ❌ Interactive Dashboard UI
- ❌ Dedicated Walk-Forward Cloud Function
- ❌ The exact 16 validated features
- ❌ Full API endpoint suite
- ❌ model_versions & walk_forward_runs tables
- ❌ Confidence threshold filtering UI
- ❌ CSV export
- ❌ Progress tracking

### Estimated Completion
- **Total Remaining Effort:** 52 hours
- **Timeline:** 4 weeks
- **Monthly Cost Increase:** ~$20-30

---

## APPROVAL REQUIRED

Please confirm:

1. [ ] Implementation priority order is correct
2. [ ] Cloud Run Jobs for long-running validation
3. [ ] Model storage bucket name
4. [ ] Start with Individual multi-ticker mode

**Once approved, implementation will begin immediately.**

---

*Document prepared by: Claude (AI)*
*For: Irfan Qazi*
*Date: January 9, 2026*
