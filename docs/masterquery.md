# Claude Code Master Query - Trading System
## AIAlgoTradeHits.com Configuration & Deployment Guide
**Version:** 5.0
**Last Updated:** January 13, 2026
**Location:** `/Trading/masterquery.md`
**Status:** TypeScript Architecture Refactoring Complete ✅

---

## 🎯 IMPLEMENTATION STATUS

### Live Production System
| Component | Status | Details |
|-----------|--------|---------|
| Trading API | ✅ Live | `https://trading-api-1075463475276.us-central1.run.app` |
| BigQuery ML | ✅ Active | Dataset: `aialgotradehits.ml_models` |
| XGBoost Model | ✅ Trained | `direction_predictor_xgboost` |
| AI Endpoints | ✅ Working | 7 endpoints operational |
| Feature Tables | ✅ Created | 53,867+ records in daily_features_24 |

### Current Model Performance (Nested Multi-Timeframe)
```
UP Accuracy:   66.2%  (Target achieved!)
DOWN Accuracy: 70.6%
ROC AUC:       0.777
F1 Score:      68.4%
```

---

## 🏗️ TYPESCRIPT ARCHITECTURE (v5.0 REFACTORING)

### Architecture Overview - SSOT Layer Cake Pattern

The trading application has been refactored to follow the **Single Source of Truth (SSOT)** and **Layer Cake Architecture** patterns for improved maintainability, type safety, and separation of concerns.

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER CAKE ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│  CONFIG (SSOT)     Trading thresholds, API endpoints, UI config │
│         ↓                                                        │
│  ENGINES (Pure)    Growth score, signals, nested ML calculations│
│         ↓                                                        │
│  SERVICES          Market data, trading signal orchestration    │
│         ↓                                                        │
│  HOOKS             React integration (useMarketData, useSignals)│
│         ↓                                                        │
│  COMPONENTS        Feature-based UI organization                │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
stock-price-app/src/
├── lib/                          # Core business logic
│   ├── config/                   # SSOT Configuration Layer
│   │   ├── trading-config.ts     # Indicators, thresholds, ML params
│   │   ├── api-config.ts         # Endpoints, rate limits
│   │   ├── ui-config.ts          # Colors, themes, chart config
│   │   └── index.ts              # Re-exports
│   │
│   ├── engines/                  # Pure Calculation Functions
│   │   ├── growth-score-engine.ts    # Growth score calculations
│   │   ├── signal-engine.ts          # Trade signal generation
│   │   ├── nested-ml-engine.ts       # Multi-timeframe ML logic
│   │   └── index.ts
│   │
│   ├── services/                 # Service Orchestration Layer
│   │   ├── market-data-service.ts    # Market data with caching
│   │   ├── trading-signal-service.ts # Signal orchestration
│   │   └── index.ts
│   │
│   ├── hooks/                    # React Integration Layer
│   │   ├── useMarketData.ts      # Market data hooks
│   │   ├── useTradingSignals.ts  # Signal hooks
│   │   └── index.ts
│   │
│   └── index.ts                  # Single entry point
│
├── types/                        # TypeScript Definitions
│   ├── trading.ts                # 50+ type definitions
│   └── index.ts
│
├── components/                   # Feature-Based Components
│   ├── dashboard/                # Dashboard components
│   │   ├── TradingDashboard.jsx
│   │   ├── SmartDashboard.jsx
│   │   └── BillingDashboard.jsx
│   ├── charts/                   # Chart components
│   │   ├── ProfessionalChart.jsx
│   │   ├── TradingViewChart.jsx
│   │   └── WalkForwardCharts.jsx
│   ├── signals/                  # Signal components
│   │   ├── NestedSignals.jsx
│   │   ├── AITradeSignals.jsx
│   │   ├── MultiTimeframeTrader.jsx
│   │   └── WalkForwardValidation.jsx
│   ├── admin/                    # Admin components
│   │   ├── AdminPanelEnhanced.jsx
│   │   ├── SchedulerMonitoring.jsx
│   │   └── DatabaseMonitoring.jsx
│   ├── data/                     # Data components
│   │   ├── DataExportDownload.jsx
│   │   └── MLTestDataDownload.jsx
│   ├── analytics/                # Analytics components
│   │   ├── ETFAnalytics.jsx
│   │   └── StrategyDashboard.jsx
│   ├── portfolio/                # Portfolio components
│   │   ├── PortfolioTracker.jsx
│   │   └── PriceAlerts.jsx
│   ├── content/                  # Content components
│   │   └── DocumentsLibrary.jsx
│   └── shared/                   # Shared components
│       ├── Navigation.jsx
│       ├── SmartSearchBar.jsx
│       └── Login.jsx
│
└── services/                     # Legacy services (API calls)
    └── marketData.js
```

### SSOT Configuration (trading-config.ts)

```typescript
// Master configuration - Single Source of Truth
export const LOGIC_VERSION = "3.0.0";

export const INDICATOR_THRESHOLDS = {
  RSI: { oversold: 30, overbought: 70, sweet_spot: [50, 70] },
  MACD: { signal_cross: 0, histogram_threshold: 0 },
  ADX: { weak: 20, strong: 25, very_strong: 40 },
  MFI: { oversold: 20, overbought: 80 },
  STOCH: { oversold: 20, overbought: 80 },
  VOLUME_RATIO: { high: 1.5, very_high: 2.0 },
};

export const NESTED_SIGNAL_THRESHOLDS = {
  ULTRA_BUY: { aligned_pct: 60, min_scores: { daily: 5, hourly: 6, fivemin: 5 }},
  STRONG_BUY: { aligned_pct: 55, min_scores: { daily: 4, hourly: 5, fivemin: 4 }},
  BUY: { aligned_pct: 50, min_scores: { daily: 3, hourly: 4, fivemin: 3 }},
  WEAK_BUY: { aligned_pct: 45, min_scores: { daily: 2, hourly: 3, fivemin: 2 }},
  NEUTRAL: { aligned_pct: 40 },
};

export const ML_MODEL_PARAMS = {
  UP_ACCURACY: 66.2,
  DOWN_ACCURACY: 70.6,
  ROC_AUC: 0.777,
  CONFIDENCE_THRESHOLD: 0.55,
  LOOKBACK_PERIODS: { daily: 200, hourly: 100, fivemin: 50 },
};
```

### Pure Engine Functions (No I/O, No Side Effects)

```typescript
// growth-score-engine.ts
export function calculateGrowthScore(data: {
  rsi_14?: number;
  macd_histogram?: number;
  adx?: number;
  close?: number;
  sma_200?: number;
}): number {
  let score = 0;
  const { rsi_14, macd_histogram, adx, close, sma_200 } = data;
  const { RSI, MACD, ADX } = INDICATOR_THRESHOLDS;

  if (rsi_14 !== undefined && rsi_14 >= RSI.sweet_spot[0] && rsi_14 <= RSI.sweet_spot[1]) {
    score += 25;
  }
  if (macd_histogram !== undefined && macd_histogram > MACD.histogram_threshold) {
    score += 25;
  }
  if (adx !== undefined && adx > ADX.strong) {
    score += 25;
  }
  if (close !== undefined && sma_200 !== undefined && close > sma_200) {
    score += 25;
  }
  return score;
}

// signal-engine.ts
export function classifyTrendRegime(
  close: number,
  sma50: number,
  sma200: number,
  adx: number
): TrendRegime {
  if (close > sma50 && sma50 > sma200 && adx > 25) return 'STRONG_UPTREND';
  if (close > sma50 && close > sma200) return 'WEAK_UPTREND';
  if (close < sma50 && sma50 < sma200 && adx > 25) return 'STRONG_DOWNTREND';
  if (close < sma50 && close < sma200) return 'WEAK_DOWNTREND';
  return 'CONSOLIDATION';
}

// nested-ml-engine.ts
export function classifyNestedSignal(scores: TimeframeScores): NestedSignal {
  const { daily, hourly, fivemin } = scores;
  const alignedPct = calculateAlignedPercentage(scores);

  for (const [signal, threshold] of Object.entries(NESTED_SIGNAL_THRESHOLDS)) {
    if (alignedPct >= threshold.aligned_pct &&
        daily >= threshold.min_scores?.daily &&
        hourly >= threshold.min_scores?.hourly &&
        fivemin >= threshold.min_scores?.fivemin) {
      return signal as NestedSignal;
    }
  }
  return 'NEUTRAL';
}
```

### TypeScript Path Aliases

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/components/*": ["./src/components/*"],
      "@/types/*": ["./src/types/*"]
    }
  }
}
```

### Import Examples

```typescript
// Using path aliases
import { INDICATOR_THRESHOLDS, ML_MODEL_PARAMS } from '@/lib/config';
import { calculateGrowthScore, classifyNestedSignal } from '@/lib/engines';
import { marketDataService, tradingSignalService } from '@/lib/services';
import { useMarketData, useTradingSignals } from '@/lib/hooks';
import type { TradingSignal, NestedSignal, Candle } from '@/types';
```

### Components Deleted (Redundant)
The following 14 components (~5,373 lines) were removed as duplicates or unused:
- AdminPanel.jsx (replaced by AdminPanelEnhanced.jsx)
- AdvancedChart.jsx (replaced by ProfessionalChart.jsx)
- AdvancedTradingChart.jsx (replaced by TradingViewChart.jsx)
- AIAlgoTradeHits.jsx (replaced by TradingDashboard.jsx)
- AIAlgoTradeHitsReal.jsx (duplicate)
- DataDownloadControl.jsx (replaced by DataExportDownload.jsx)
- DataDownloadWizard.jsx (replaced by DataExportDownload.jsx)
- EnhancedDashboard.jsx (replaced by SmartDashboard.jsx)
- FundamentalsView.jsx (unused)
- MultiPanelChart.jsx (replaced by ProfessionalChart.jsx)
- NLPSearch.jsx (replaced by SmartSearchBar.jsx)
- WeeklyAnalysis.jsx (replaced by StrategyDashboard.jsx)
- WeeklyDashboard.jsx (replaced by SmartDashboard.jsx)
- WeeklyReconciliation.jsx (replaced by DataReconciliation.jsx)

---

## 🤖 AI TRADING API ENDPOINTS

**Base URL:** `https://trading-api-1075463475276.us-central1.run.app`

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/ai/trading-signals` | GET | Generate buy/sell signals | ✅ Working |
| `/api/ai/rise-cycle-candidates` | GET | EMA crossover cycle detection | ✅ Working |
| `/api/ai/ml-predictions` | GET | Growth score predictions | ✅ Working |
| `/api/ai/growth-screener` | GET | High growth score scanner | ✅ Working |
| `/api/ai/text-to-sql` | POST | Natural language queries | ✅ Working |
| `/api/ai/analyze-symbol` | GET | AI symbol analysis | ✅ Working |
| `/api/ai/market-summary` | GET | AI market overview | ✅ Working |
| `/api/ai/nested-signals` | GET | Multi-timeframe nested signals | ✅ Working |
| `/api/ai/nested-summary` | GET | Nested signal statistics | ✅ Working |
| `/api/ai/nested-signals/execute` | GET | Top EXECUTE action signals | ✅ Working |
| `/api/ai/nested-signals/ready` | GET | Top READY action signals | ✅ Working |
| `/api/ai/nested-signals/watch` | GET | Top WATCH action signals | ✅ Working |

### Example API Calls
```bash
# Get rise cycle candidates
curl "https://trading-api-1075463475276.us-central1.run.app/api/ai/rise-cycle-candidates"

# Get ML predictions with growth scores
curl "https://trading-api-1075463475276.us-central1.run.app/api/ai/ml-predictions?limit=20"

# Screen for high growth scores
curl "https://trading-api-1075463475276.us-central1.run.app/api/ai/growth-screener?min_score=75"

# Natural language query
curl -X POST "https://trading-api-1075463475276.us-central1.run.app/api/ai/text-to-sql" \
  -H "Content-Type: application/json" \
  -d '{"query": "show me oversold cryptos with high volume"}'
```

---

## 📊 BIGQUERY ML INFRASTRUCTURE

### Dataset: `aialgotradehits.ml_models`

| Table | Records | Description |
|-------|---------|-------------|
| `daily_features_24` | 53,867+ | 24 indicators per masterquery spec |
| `hourly_features_12` | Created | 12 indicators for cycle timing |
| `fivemin_features_8` | Created | 8 indicators for execution |
| `direction_predictor_xgboost` | Trained | XGBoost classifier model |
| `v_daily_predictions` | View | Real-time ML predictions |

### Feature Table Schema (daily_features_24)
```sql
-- Core OHLCV
symbol STRING, datetime TIMESTAMP, open FLOAT64, high FLOAT64, 
low FLOAT64, close FLOAT64, volume INT64,

-- Momentum Indicators (6)
rsi_14 FLOAT64, macd FLOAT64, macd_signal FLOAT64, macd_histogram FLOAT64,
stoch_k FLOAT64, stoch_d FLOAT64,

-- Trend Indicators (10)
sma_20 FLOAT64, sma_50 FLOAT64, sma_200 FLOAT64,
ema_12 FLOAT64, ema_20 FLOAT64, ema_26 FLOAT64, ema_50 FLOAT64, ema_200 FLOAT64,
ichimoku_tenkan FLOAT64, ichimoku_kijun FLOAT64,

-- Volatility (4)
atr_14 FLOAT64, bb_upper FLOAT64, bb_middle FLOAT64, bb_lower FLOAT64,

-- Trend Strength (3)
adx FLOAT64, plus_di FLOAT64, minus_di FLOAT64,

-- Volume Flow (2)
mfi FLOAT64, cmf FLOAT64,

-- Computed Signals
growth_score INT64, trend_regime STRING, in_rise_cycle BOOL,
golden_cross BOOL, death_cross BOOL
```

---

## 📈 GROWTH SCORE CALCULATION (0-100)

The Growth Score is a composite metric indicating bullish momentum strength.

### Formula
```sql
growth_score = 
  CASE WHEN rsi_14 BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
  CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
  CASE WHEN adx > 25 THEN 25 ELSE 0 END +
  CASE WHEN close > sma_200 THEN 25 ELSE 0 END
```

### Component Breakdown
| Component | Points | Condition | Rationale |
|-----------|--------|-----------|-----------|
| RSI Sweet Spot | +25 | RSI between 50-70 | Bullish momentum, not overbought |
| MACD Positive | +25 | MACD histogram > 0 | Momentum acceleration |
| Strong Trend | +25 | ADX > 25 | Trending market (not ranging) |
| Above 200 MA | +25 | Close > SMA_200 | Long-term bullish context |

### Score Interpretation
| Score | Classification | Action |
|-------|---------------|--------|
| 100 | Perfect Setup | STRONG_BUY signal |
| 75 | High Probability | BUY signal |
| 50 | Moderate | HOLD / Wait for confirmation |
| 25 | Weak | Caution |
| 0 | Bearish | AVOID / Consider SHORT |

### Sample Results (Live System)
```
Symbol: LOW   | Growth Score: 100 | RISE_CYCLE_START | STRONG_UPTREND
Symbol: CSCO  | Growth Score: 100 | STRONG_BUY signal
Symbol: WMT   | Growth Score: 100 | RSI: 63.1
Symbol: QQQ   | Growth Score: 75  | Up probability: 51.9%
Symbol: AIG   | Growth Score: 75  | In Rise Cycle: TRUE
```

---

## 🔄 EMA CYCLE DETECTION

### Rise/Fall Cycle Logic
```sql
-- Rise Cycle Detection
in_rise_cycle = (ema_12 > ema_26)

-- Rise Cycle Start (crossover)
rise_cycle_start = (ema_12 > ema_26) AND (LAG(ema_12) <= LAG(ema_26))

-- Fall Cycle Start (crossunder)
fall_cycle_start = (ema_12 < ema_26) AND (LAG(ema_12) >= LAG(ema_26))
```

### Supporting Confirmations
```sql
-- Volume Confirmation
volume_confirmed = (volume > AVG(volume) OVER (ORDER BY datetime ROWS 20 PRECEDING) * 1.2)

-- RSI Confirmation
rsi_bullish = (rsi_14 > 50)
rsi_bearish = (rsi_14 < 50)

-- Full Rise Signal
rise_signal = rise_cycle_start AND volume_confirmed AND rsi_bullish
```

---

## 📊 TREND REGIME CLASSIFICATION

### Regime States
```sql
trend_regime = CASE
  WHEN close > sma_50 AND sma_50 > sma_200 AND adx > 25 THEN 'STRONG_UPTREND'
  WHEN close > sma_50 AND close > sma_200 THEN 'WEAK_UPTREND'
  WHEN close < sma_50 AND sma_50 < sma_200 AND adx > 25 THEN 'STRONG_DOWNTREND'
  WHEN close < sma_50 AND close < sma_200 THEN 'WEAK_DOWNTREND'
  ELSE 'CONSOLIDATION'
END
```

### Golden/Death Cross Detection
```sql
-- Golden Cross (Bullish)
golden_cross = (sma_50 > sma_200) AND (LAG(sma_50) <= LAG(sma_200))

-- Death Cross (Bearish)
death_cross = (sma_50 < sma_200) AND (LAG(sma_50) >= LAG(sma_200))
```

---

## 🧠 ML INDICATOR FRAMEWORK BY TIMEFRAME

### Timeframe-Specific Indicator Counts
| Timeframe | Indicators | Purpose | Latency Target |
|-----------|------------|---------|----------------|
| Daily | 24 (full) | Strategic screening | <5 seconds |
| Hourly | 12 | Cycle timing | <1 second |
| 5-Minute | 8 | Trade execution | <200ms |
| 1-Minute | 5 | Scalping (optional) | <50ms |

### Daily (24 Indicators)
**Momentum:** RSI, MACD, ROC, Stoch_K, Stoch_D, MFI  
**Trend:** SMA_20/50/200, EMA_12/20/26/50/200, Ichimoku_Tenkan/Kijun  
**Volatility:** ATR, BB_Upper/Middle/Lower  
**Strength:** ADX, Plus_DI, Minus_DI  
**Flow:** MFI, CMF

### Hourly (12 Indicators)
```yaml
cycle_detection: [EMA_9, EMA_21]
momentum: [RSI_14, MACD, MACD_Histogram]
volume: [Volume_Ratio, VWAP]
volatility: [ATR_14, BB_Percent_B]
trend_context: [SMA_50, ADX]
flow: [MFI]
```

### 5-Minute (8 Indicators)
```yaml
signal: [EMA_9, EMA_21]
momentum: [RSI_14, MACD_Histogram]
volume: [Volume_Ratio, VWAP]
risk: [ATR_14, Price_vs_VWAP]
```

### 1-Minute (5 Indicators)
```yaml
signal: [EMA_5, EMA_13]
momentum: [RSI_7]
volume: [Volume_Spike]
reference: [VWAP_Distance_Pct]
```

---

## 🔐 CONFIGURATION MANAGEMENT

### Core Rules
1. **NEVER hardcode any variables** - All values from config/env files
2. **Centralized config management** - All `.env` files via admin panel
3. **Environment separation** - Strict Dev/Prod isolation
4. **Admin control** - Config changes require authentication

### Directory Layout
```
/config/
├── .env.dev                 # Development environment
├── .env.prod                # Production environment
├── .env.shared              # Shared across environments
├── config.yaml              # Main configuration file
├── secrets.yaml             # Encrypted secrets (gitignored)
├── ml/
│   ├── indicator_groups.yaml
│   └── timeframe_indicators.yaml
├── nl2sql/
│   ├── gemini_config.yaml
│   ├── query_patterns.yaml
│   └── symbol_mappings.yaml
└── admin/
    ├── config_editor.py
    └── permissions.yaml
```

---

## 🌍 ENVIRONMENT FILES

### Production (`.env.prod`)
```bash
ENVIRONMENT=production
APP_NAME=AIAlgoTradeHits
APP_VERSION=4.0.0

# Cloud Run - Production
PROD_CLOUD_RUN_URL=https://trading-api-1075463475276.us-central1.run.app
PROD_MIN_INSTANCES=1
PROD_MAX_INSTANCES=100

# GCP
GCP_PROJECT_ID=aialgotradehits
GCP_REGION=us-central1
BIGQUERY_DATASET=ml_models

# AI Models
CLAUDE_MODEL=claude-sonnet-4-20250514
VERTEX_AI_MODEL=gemini-2.5-pro
AI_TEMPERATURE=0.1
```

### Shared (`.env.shared`)
```bash
# Technical Indicators
DEFAULT_RSI_PERIOD=14
DEFAULT_MACD_FAST=12
DEFAULT_MACD_SLOW=26
DEFAULT_MACD_SIGNAL=9
DEFAULT_BB_PERIOD=20

# Growth Score Thresholds
GROWTH_RSI_MIN=50
GROWTH_RSI_MAX=70
GROWTH_ADX_MIN=25

# Timeframes
SUPPORTED_TIMEFRAMES=1min,5min,hourly,daily
```

---

## 🚀 DEPLOYMENT

### Current Production URL
```
https://trading-api-1075463475276.us-central1.run.app
```

### Deploy Commands
```bash
# Deploy to production
gcloud run deploy trading-api \
  --project=aialgotradehits \
  --region=us-central1 \
  --source=.

# Check status
gcloud run services describe trading-api --region=us-central1
```

---

## 📋 QUICK REFERENCE

### API Testing
```bash
# Health check
curl https://trading-api-1075463475276.us-central1.run.app/health

# Get top growth candidates
curl https://trading-api-1075463475276.us-central1.run.app/api/ai/growth-screener?min_score=75

# Rise cycle detection
curl https://trading-api-1075463475276.us-central1.run.app/api/ai/rise-cycle-candidates
```

### BigQuery Queries
```sql
-- Top growth score symbols
SELECT symbol, growth_score, trend_regime, in_rise_cycle
FROM `aialgotradehits.ml_models.daily_features_24`
WHERE growth_score >= 75
ORDER BY growth_score DESC, datetime DESC
LIMIT 20;

-- Rise cycle candidates
SELECT symbol, datetime, close, ema_12, ema_26, rsi_14, volume
FROM `aialgotradehits.ml_models.daily_features_24`
WHERE ema_12 > ema_26
  AND rsi_14 BETWEEN 50 AND 70
ORDER BY datetime DESC;

-- ML Predictions
SELECT * FROM `aialgotradehits.ml_models.v_daily_predictions`
WHERE predicted_direction = 'UP'
  AND probability > 0.55;
```

---

## ⚠️ CRITICAL RULES

1. **NEVER commit `.env.prod` to git**
2. **NEVER hardcode API keys or URLs**
3. **All config changes must be audited**
4. **Test in dev before prod deployment**
5. **Model retraining: Weekly for daily, Daily for hourly**

---

## 🎯 NEXT STEPS (Model Improvement)

Current accuracy (52.8%) needs improvement to reach 66-72% target:

1. **Add Feature Interactions**
   - RSI × Volume_Ratio
   - MACD × ATR
   - ADX × Trend_Direction

2. **Add Lagged Features**
   - RSI_t-1, RSI_t-5
   - Price momentum over 5, 10, 20 periods

3. **Improve Training Data**
   - More historical data
   - Better label definition (>1% moves only)
   - Class balancing

4. **Hyperparameter Tuning**
   - XGBoost max_depth, learning_rate
   - Early stopping optimization

---

## 🔌 MULTI-SOURCE DATA INTEGRATION

### Data Sources Configured (1 AM Daily Fetch)

| Source | API Key | Rate Limit | Data Types | Status |
|--------|---------|------------|------------|--------|
| **TwelveData** | `16ee060fd4d34a628a14bcb6f0167565` | 800 calls/min ($229/mo) | Stocks, Crypto, ETFs, Forex, Indices | ✅ Active |
| **Kraken Pro** | Public API | 40 calls/min | Crypto OHLCV + Buy/Sell Volume | ✅ Active |
| **FRED** | `608f96800c8a5d9bdb8d53ad059f06c1` | 120 req/min | Economic Indicators | ✅ Active |
| **Finnhub** | `d4dg7t9r01qovljpm3g0d4dg7t9r01qovljpm3gg` | 60 calls/min | Analyst Recommendations | ✅ Active |
| **CoinMarketCap** | `059474ae48b84628be6f4a94f9840c30` | 333 calls/day | Crypto Rankings, Market Cap | ✅ Active |

### Buy/Sell Volume & Trade Count (Kraken)

```yaml
# New Fields from Kraken API
buy_volume:      # Total buy volume in period
sell_volume:     # Total sell volume in period
buy_count:       # Number of buy trades
sell_count:      # Number of sell trades
trade_count:     # Total number of trades in period
buy_sell_ratio:  # buy_volume / sell_volume
buy_pressure:    # buy_volume / (buy_volume + sell_volume) - 0.0 to 1.0
```

### Sentiment Score (0.00 - 1.00)

Composite sentiment based on technical indicators + volume data:

| Component | Weight | Condition |
|-----------|--------|-----------|
| RSI | 0.125 | Oversold (30-50) = bullish, Overbought (70+) = bearish |
| MACD Histogram | 0.125 | Positive = bullish, Negative = bearish |
| MACD Cross | 0.100 | Bullish cross +0.1, Bearish cross -0.1 |
| ADX Strength | 0.075 | ADX > 25 = trending market bonus |
| SMA 200 | 0.100 | Above = bullish, Below = bearish |
| Pivot Flags | 0.075 | Pivot low = bounce potential, Pivot high = reversal |
| MFI | 0.100 | Money flow index (volume-weighted RSI) |
| Buy Pressure | 0.100 | From Kraken buy/sell data |

**Sentiment Interpretation:**
| Score Range | Meaning |
|-------------|---------|
| 0.70 - 1.00 | Strong Bullish |
| 0.55 - 0.69 | Bullish |
| 0.45 - 0.54 | Neutral |
| 0.30 - 0.44 | Bearish |
| 0.00 - 0.29 | Strong Bearish |

### Buy/Sell/Hold Recommendation

```yaml
STRONG_BUY:  sentiment >= 0.70 AND RSI 40-70 AND MACD_Histogram > 0
BUY:         sentiment 0.55-0.69 AND (MACD > 0 OR RSI < 50)
HOLD:        sentiment 0.45-0.54 (neutral zone)
SELL:        sentiment 0.30-0.44 AND (MACD < 0 OR RSI > 70)
STRONG_SELL: sentiment <= 0.30 AND MACD_Histogram < 0
```

### Economic Data from FRED

| Series ID | Description | Frequency |
|-----------|-------------|-----------|
| DGS10 | 10-Year Treasury Yield | Daily |
| DGS2 | 2-Year Treasury Yield | Daily |
| DGS30 | 30-Year Treasury Yield | Daily |
| T10Y2Y | 10Y-2Y Spread (Yield Curve) | Daily |
| FEDFUNDS | Federal Funds Rate | Monthly |
| VIXCLS | VIX Volatility Index | Daily |
| SP500 | S&P 500 Index | Daily |
| UNRATE | Unemployment Rate | Monthly |
| CPIAUCSL | Consumer Price Index | Monthly |
| MORTGAGE30US | 30-Year Mortgage Rate | Weekly |

### 1 AM Scheduler Configuration

```bash
# Scheduler: multi-source-daily-1am
# Schedule: 0 1 * * * (1 AM daily, America/New_York)
# Timeout: 30 minutes
# Data fetched:
#   - 200+ Stocks from TwelveData (5000 records each)
#   - 50+ Cryptos from TwelveData
#   - 20+ Cryptos with Buy/Sell Volume from Kraken
#   - 50+ ETFs from TwelveData (includes Top 20 by AUM)
#   - 20+ Forex pairs from TwelveData
#   - Economic indicators from FRED
#   - Analyst recommendations from Finnhub
#   - Crypto rankings from CoinMarketCap
# Target: 2M+ records per day
```

### API Rate Limiting

```python
# TwelveData: $229/month plan
TWELVEDATA_RATE = 55  # Conservative for 800/min capacity

# Kraken: Free public API
KRAKEN_RATE = 40  # 1.5 seconds between calls

# FRED: Free tier
FRED_RATE = 100

# Finnhub: Free tier
FINNHUB_RATE = 50

# CoinMarketCap: Free tier (333/day limit)
CMC_RATE = 10  # Conservative daily usage
```

---

## 📊 COMPLETE FIELD SCHEMA

### Crypto Daily Clean Table (97+ Fields)

```yaml
# Core OHLCV
symbol, datetime, open, high, low, close, volume

# Moving Averages (6)
sma_20, sma_50, sma_200, ema_12, ema_26, ema_50

# RSI Family (5)
rsi, rsi_overbought, rsi_oversold, rsi_slope, rsi_zscore

# MACD Family (4)
macd, macd_signal, macd_histogram, macd_cross

# Bollinger Bands (4)
bb_upper, bb_middle, bb_lower, bb_percent

# Volatility (2)
atr, bb_width

# ADX Family (3)
adx, plus_di, minus_di

# Oscillators (4)
cci, mfi, momentum, awesome_osc

# Stochastic (2)
stoch_k, stoch_d

# Other Indicators (4)
williams_r, roc, obv, vwap_daily

# Pivot Flags (2)
pivot_high_flag, pivot_low_flag

# Buy/Sell Volume (Kraken) (6)
buy_volume, sell_volume, buy_count, sell_count, trade_count, buy_sell_ratio

# Sentiment & Recommendation (3)
buy_pressure, sentiment_score, recommendation

# Computed (2)
growth_score, asset_type

# Metadata (2)
source, fetch_timestamp
```

---

## 🤖 AGENTIC AI ARCHITECTURE (7-STEP FRAMEWORK)

This section defines the complete Agentic AI system for AIAlgoTradeHits.com and all Claude.ai subscription projects, based on the Claude Code + GCP Cloud Run methodology.

### Architecture Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENTIC AI ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│  STEP 1: System Prompt  →  STEP 2: LLM (Claude)                 │
│           ↓                         ↓                            │
│  STEP 3: Tools/APIs     ←  STEP 5: Orchestration                │
│           ↓                         ↓                            │
│  STEP 4: Memory         →  STEP 6: UI (React/FastAPI)           │
│           ↓                         ↓                            │
│  STEP 7: AI Evals       →  Continuous Improvement               │
└─────────────────────────────────────────────────────────────────┘
```

### Step 1: System Prompts (By Project)

#### Trading Agent (AIAlgoTradeHits.com)
```python
TRADING_SYSTEM_PROMPT = """You are an expert AI trading advisor for AIAlgoTradeHits.com.

GOALS:
- Analyze market data using 24+ technical indicators
- Generate Growth Scores (0-100) for asset screening
- Detect EMA rise/fall cycles for timing
- Provide actionable trading signals

ROLE:
- Professional trading analyst
- Risk-aware recommendations
- Data-driven insights

INSTRUCTIONS:
1. Use get_market_data tool for real-time prices
2. Calculate Growth Score per formula
3. Detect trend regime (STRONG_UPTREND/CONSOLIDATION/etc.)
4. Check EMA cycle status before recommendations
5. Always include risk warnings
6. Store trading insights in memory
"""
```

#### Financial AI Agent (HomeFranchise)
```python
FRANCHISE_SYSTEM_PROMPT = """You are a franchise business advisor AI.

GOALS:
- Analyze franchise opportunities and ROI projections
- Evaluate market viability for locations
- Generate business plans and financial forecasts

ROLE: Business consultant with franchise expertise
"""
```

#### Agricultural AI Agent (KaamyabPakistan)
```python
AGRICULTURE_SYSTEM_PROMPT = """You are an agricultural advisor for Pakistan.

GOALS:
- Provide crop recommendations based on region/season
- Analyze aeroponic farming feasibility
- Generate Urdu/English bilingual reports

ROLE: Agricultural scientist with local expertise
"""
```

### Step 2: LLM Configuration

| Agent | Model | Temperature | Max Tokens |
|-------|-------|-------------|------------|
| Trading Agent | Claude Sonnet 4.5 | 0.3 | 4096 |
| Analysis Agent | Claude Opus 4.5 | 0.5 | 8192 |
| Support Agent | Claude Haiku 4.5 | 0.7 | 2048 |
| Code Agent | Claude Sonnet 4.5 | 0.1 | 16384 |

```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

AGENT_CONFIGS = {
    "trading": {"model": "claude-sonnet-4-5-20250929", "temperature": 0.3},
    "analysis": {"model": "claude-opus-4-5-20251101", "temperature": 0.5},
    "support": {"model": "claude-haiku-4-5-20250514", "temperature": 0.7}
}
```

### Step 3: Tools & Function Calling

#### Trading Agent Tools
```python
TRADING_TOOLS = [
    {
        "name": "get_market_data",
        "description": "Fetch real-time market data for stocks/crypto",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "interval": {"type": "string", "enum": ["1day", "1h", "5min"]}
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "calculate_growth_score",
        "description": "Calculate Growth Score (0-100) for a symbol",
        "input_schema": {
            "type": "object",
            "properties": {"symbol": {"type": "string"}},
            "required": ["symbol"]
        }
    },
    {
        "name": "detect_rise_cycle",
        "description": "Check EMA 12/26 crossover cycle status",
        "input_schema": {
            "type": "object",
            "properties": {"symbol": {"type": "string"}},
            "required": ["symbol"]
        }
    },
    {
        "name": "query_bigquery",
        "description": "Execute SQL query on trading data",
        "input_schema": {
            "type": "object",
            "properties": {"sql": {"type": "string"}},
            "required": ["sql"]
        }
    },
    {
        "name": "send_alert",
        "description": "Send trading alert notification",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "signal": {"type": "string", "enum": ["BUY", "SELL", "HOLD"]},
                "message": {"type": "string"}
            },
            "required": ["symbol", "signal", "message"]
        }
    }
]
```

### Step 4: Memory Systems

```python
class AgentMemory:
    """Multi-layer memory system for AI agents"""

    def __init__(self, user_id: str, project: str):
        self.user_id = user_id
        self.project = project

        # Episodic (conversation history)
        self.conversation = []

        # Working (current task context)
        self.working = {}

        # Long-term (BigQuery/Firestore)
        self.db = firestore.Client()
        self.bq = bigquery.Client()

    def store_insight(self, insight: str, category: str):
        """Store important trading insight"""
        self.db.collection(f'{self.project}_insights').add({
            'user_id': self.user_id,
            'insight': insight,
            'category': category,
            'timestamp': firestore.SERVER_TIMESTAMP
        })

    def get_context_for_llm(self) -> dict:
        """Compile memory context for LLM call"""
        return {
            "recent_conversation": self.conversation[-10:],
            "current_task": self.working,
            "user_preferences": self.get_user_prefs()
        }
```

### Step 5: Orchestration

```python
class TradingOrchestrator:
    """Multi-agent orchestrator for trading workflows"""

    def __init__(self):
        self.agents = {}
        self.workflows = {}

    def register_agents(self):
        self.agents = {
            "market_scanner": MarketScannerAgent(),
            "technical_analyst": TechnicalAnalysisAgent(),
            "risk_assessor": RiskAssessmentAgent(),
            "signal_generator": SignalGeneratorAgent()
        }

    def define_trading_workflow(self):
        """Define the trading analysis workflow"""
        self.workflows["full_analysis"] = [
            {"agent": "market_scanner", "action": "scan_markets"},
            {"agent": "technical_analyst", "action": "analyze_technicals"},
            {"agent": "risk_assessor", "action": "assess_risk"},
            {"agent": "signal_generator", "action": "generate_signals"}
        ]

    async def execute_workflow(self, workflow_name: str, params: dict):
        steps = self.workflows[workflow_name]
        context = params.copy()

        for step in steps:
            agent = self.agents[step["agent"]]
            result = await agent.execute(step["action"], context)
            context[f"{step['agent']}_result"] = result

        return context
```

### Step 6: User Interface (FastAPI + WebSocket)

```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AIAlgoTradeHits Agentic API")

app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.post("/api/agent/chat")
async def agent_chat(request: ChatRequest):
    """REST endpoint for agent interaction"""
    memory = AgentMemory(request.user_id, "trading")
    response = await run_agent_with_tools(request.message, memory)
    return {"response": response}

@app.websocket("/ws/agent")
async def agent_websocket(websocket: WebSocket):
    """WebSocket for streaming responses"""
    await websocket.accept()
    async for token in stream_agent_response():
        await websocket.send_json({"type": "token", "content": token})

@app.get("/api/agent/trading-signals")
async def get_trading_signals():
    """Get current trading signals from agent"""
    orchestrator = TradingOrchestrator()
    result = await orchestrator.execute_workflow("full_analysis", {})
    return result
```

### Step 7: AI Evaluations

```python
class AgentEvaluator:
    """Monitor and evaluate agent performance"""

    def __init__(self):
        self.metrics = []

    def log_interaction(self, response_time, tool_calls, success):
        self.metrics.append({
            "timestamp": datetime.now(),
            "response_time": response_time,
            "tool_calls": tool_calls,
            "success": success
        })

    def analyze_performance(self, window=100):
        recent = self.metrics[-window:]
        return {
            "avg_response_time": np.mean([m["response_time"] for m in recent]),
            "success_rate": sum(m["success"] for m in recent) / len(recent),
            "avg_tool_calls": np.mean([m["tool_calls"] for m in recent])
        }
```

---

## 🚀 GCP CLOUD RUN DEPLOYMENT

### Dockerfile (Production)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Deploy Command
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/aialgotradehits/trading-agent

gcloud run deploy trading-agent \
    --image gcr.io/aialgotradehits/trading-agent \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --set-env-vars ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

### CI/CD (cloudbuild.yaml)
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/trading-agent:$COMMIT_SHA', '.']

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/trading-agent:$COMMIT_SHA']

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'trading-agent'
      - '--image'
      - 'gcr.io/$PROJECT_ID/trading-agent:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
```

---

## 📊 MULTI-PROJECT AGENT ARCHITECTURE

### AIAlgoTradeHits.com Projects

| Project | Agent Type | Primary Tools | Status |
|---------|------------|---------------|--------|
| **Trading App** | Trading Agent | Market Data, BigQuery, Alerts | ✅ Active |
| **HomeFranchise** | Business Agent | Financial Analysis, Reporting | 🔧 Ready |
| **KaamyabPakistan** | Agricultural Agent | Crop Data, PDFs, Urdu NLP | 🔧 Ready |
| **IRS CPIC** | Tax Agent | Form Processing, Compliance | 🔧 Ready |
| **MarketingAI** | Marketing Agent | Content Generation, Analytics | 🔧 Ready |
| **KidsAI** | Educational Agent | Phonics, Games, Learning | 🔧 Ready |
| **NoCodeAI** | Builder Agent | Code Generation, Deployment | ⏳ Basic |
| **YouInvent** | Invention Agent | Patent Search, Prototyping | ⏳ Basic |

### Shared Agent Infrastructure
```
┌────────────────────────────────────────────────────────────────┐
│                   SHARED AGENT LAYER                            │
├────────────────────────────────────────────────────────────────┤
│  Claude API Client  │  Memory System  │  Tool Registry         │
│  BigQuery Access    │  Firestore      │  Cloud Storage          │
│  Pub/Sub Messaging  │  Cloud Run      │  Cloud Scheduler        │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│              PROJECT-SPECIFIC AGENTS                            │
├────────┬─────────┬─────────┬────────┬─────────┬───────────────┤
│Trading │Franchise│Agricult │Tax     │Marketing│Educational    │
│Agent   │Agent    │Agent    │Agent   │Agent    │Agent          │
└────────┴─────────┴─────────┴────────┴─────────┴───────────────┘
```

---

## 📋 IMPLEMENTATION PLAN

### Phase 1: Core Agent Framework (Week 1)
- [ ] Create `shared_ai_modules/` with base agent classes
- [ ] Implement AgentMemory with BigQuery/Firestore
- [ ] Build tool registry with 10+ trading tools
- [ ] Deploy base Trading Agent to Cloud Run

### Phase 2: Trading Agent Enhancement (Week 2)
- [ ] Integrate all 24 indicators into agent tools
- [ ] Add Growth Score calculation tool
- [ ] Implement EMA cycle detection tool
- [ ] Add real-time alert system

### Phase 3: Multi-Project Agents (Week 3)
- [ ] Deploy HomeFranchise agent
- [ ] Deploy KaamyabPakistan agent
- [ ] Deploy IRS CPIC agent
- [ ] Create project-specific tool sets

### Phase 4: Orchestration & Evaluation (Week 4)
- [ ] Build multi-agent orchestrator
- [ ] Implement agent-to-agent communication
- [ ] Add AI evaluation dashboard
- [ ] Create CI/CD automation

---

*Platform: AIAlgoTradeHits.com*
*Agentic AI Framework Version: 1.0*
*TypeScript Architecture Version: 3.0.0*
*Maintained by: Trading Infrastructure Team*
*Last Updated: January 13, 2026*

---

## 📝 CHANGELOG

### v5.0 (January 13, 2026)
- **TypeScript Migration**: Converted core business logic to TypeScript
- **SSOT Architecture**: Implemented Single Source of Truth pattern
- **Layer Cake Pattern**: Config → Engines → Services → Hooks → Components
- **Feature-Based Components**: Reorganized 50+ components into feature folders
- **Deleted Redundant Code**: Removed 14 duplicate components (~5,373 lines)
- **Nested ML Model**: Achieved 66.2% UP accuracy with multi-timeframe alignment
- **New API Endpoints**: Added 5 nested signal endpoints

### v4.0 (December 13, 2025)
- Initial ML model training with 52.8% accuracy
- BigQuery ML infrastructure setup
- 24 technical indicators implementation
- Multi-source data integration (TwelveData, Kraken, FRED, Finnhub, CoinMarketCap)
