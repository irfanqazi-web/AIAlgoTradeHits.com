# ML Sector Training, Testing & Validation Plan

## Executive Summary

This document outlines the comprehensive ML training strategy for walk-forward validation across key market sectors. The plan prioritizes high-growth sectors: Semiconductors, AI/Cloud, Defense/Aerospace, Nuclear Energy, and Quantum Computing.

## Sector Classification

### 1. SEMICONDUCTORS (19 Stocks)

| Sub-Industry | Symbols | Description |
|--------------|---------|-------------|
| **Chip Makers** | NVDA, AMD, INTC, AVGO, QCOM, MU, MRVL | GPU, CPU, memory manufacturers |
| **Equipment** | ASML, LRCX, AMAT, KLAC | Lithography, etch, deposition |
| **Design/EDA** | SNPS, CDNS, ADI, MCHP, TXN, NXPI, ON | Chip design software, analog chips |
| **AI Servers** | SMCI | AI infrastructure hardware |

**Total: 19 stocks**

### 2. AI & CLOUD (16 Stocks)

| Sub-Industry | Symbols | Description |
|--------------|---------|-------------|
| **AI Leaders** | NVDA, MSFT, GOOGL, META, AMZN | Major AI platforms |
| **Enterprise AI** | CRM, NOW, PANW, CRWD | Business AI applications |
| **AI Infrastructure** | PLTR, PATH, DDOG, MDB, TEAM | Data platforms, automation |
| **Quantum/Emerging** | IONQ | Quantum computing |

**Total: 16 stocks**

### 3. DEFENSE & AEROSPACE (6 Stocks)

| Sub-Industry | Symbols | Description |
|--------------|---------|-------------|
| **Prime Contractors** | LMT, RTX, NOC, GD | Defense systems |
| **Space/Drones** | RKLB, JOBY | Space launch, eVTOL |

**Total: 6 stocks**

### 4. NUCLEAR & CLEAN ENERGY (4 Stocks)

| Sub-Industry | Symbols | Description |
|--------------|---------|-------------|
| **Nuclear** | CEG | Nuclear power generation |
| **Solar** | ENPH, FSLR | Solar inverters, panels |
| **Utilities** | NEE | Clean energy utility |

**Total: 4 stocks**

## Training Configuration

### Model Parameters
- **Algorithm**: XGBoost Classifier (BigQuery ML)
- **Features**: Essential 8 (optimized for cost/performance)
  - rsi, macd, macd_histogram, momentum, mfi, cci, rsi_zscore, macd_cross
- **Retraining**: Monthly (21 trading days)
- **Validation Period**: 60-252 trading days

### Cost Optimization
| Optimization | Savings |
|-------------|---------|
| Monthly retraining | 76% vs weekly |
| Essential 8 features | 50% faster |
| Model caching | 80% reuse |
| Batch predictions | 30x fewer queries |

### Estimated Costs
| Batch | Stocks | Est. Cost |
|-------|--------|-----------|
| Semiconductors | 19 | ~$3.00 |
| AI & Cloud | 16 | ~$2.50 |
| Defense | 6 | ~$1.00 |
| Energy | 4 | ~$0.75 |
| **Total** | **45** | **~$7.25** |

## Validation Schedule

### Phase 1: Quick Validation (15 days)
- Purpose: Rapid model quality check
- Duration: ~10 min per batch
- Output: Accuracy metrics per sector

### Phase 2: Standard Validation (60 days)
- Purpose: Robust performance assessment
- Duration: ~30 min per batch
- Output: Detailed accuracy, up/down splits

### Phase 3: Full Backtest (252 days)
- Purpose: Annual performance analysis
- Duration: ~2 hours per batch
- Output: Comprehensive performance report

## Expected Metrics

| Metric | Target |
|--------|--------|
| Overall Accuracy | > 95% |
| Up Prediction Accuracy | > 50% |
| Down Prediction Accuracy | > 95% |
| Sharpe Ratio | > 1.0 |

## API Endpoints

### Run Validation
```
GET https://ml-training-service-1075463475276.us-central1.run.app
    ?action=run
    &symbols=NVDA,AMD,INTC
    &test_start=2025-01-01
    &walk_forward_days=60
    &retrain_frequency=monthly
    &features_mode=essential_8
```

### Check Status
```
GET ?action=status&run_id=<run_id>
```

### Resume Failed Run
```
GET ?action=resume&run_id=<run_id>
```

## Execution Plan

1. **Generate PDF Report** (this document)
2. **Run Semiconductor Batch** (19 stocks, 60 days)
3. **Run AI/Cloud Batch** (16 stocks, 60 days)
4. **Run Defense Batch** (6 stocks, 60 days)
5. **Run Energy Batch** (4 stocks, 60 days)
6. **Compile Final Results Report**

## Service Information

- **Cloud Run Service**: ml-training-service
- **Timeout**: 60 minutes
- **Memory**: 4GB
- **Region**: us-central1
- **Project**: aialgotradehits

---
Generated: 2026-01-10
