# MASTER QUERY IMPROVEMENTS - Suggestions for Enhanced Claude Code Prompt

**Based on:** Current codebase analysis in `C:\1AITrading\Trading`
**For:** Irfan Saheb / AI Trading System Team
**Date:** December 11, 2025

---

## RECOMMENDED ADDITIONS TO MASTER QUERY

### 1. ADD: Project Context Clarification

**Current Issue:** Master query references `cryptobot-462709` but actual project is `aialgotradehits`

```markdown
## GCP PROJECT CONFIGURATION

**PRIMARY PROJECT:** aialgotradehits (Main production)
**LEGACY PROJECT:** cryptobot-462709 (Migration source)

When deploying, ALWAYS use:
- Project: aialgotradehits
- Dataset: crypto_trading_data
- Region: us-central1
```

---

### 2. ADD: Actual Table Schema Reference

**Why:** Claude needs to know exact table structures to write efficient queries

```markdown
## BIGQUERY TABLE SCHEMA

### Clean Data Tables (Primary)
| Table | Records | Fields | Use Case |
|-------|---------|--------|----------|
| stocks_daily_clean | 424,894 | 97 | Daily stock OHLCV + indicators |
| crypto_daily_clean | 94,048 | 97 | Daily crypto OHLCV + indicators |
| stocks_hourly_clean | TBD | 97 | Hourly stock data |
| crypto_hourly_clean | TBD | 97 | Hourly crypto data |

### Key Fields (97-Field Schema)
```python
CORE_FIELDS = ['symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume']

MOMENTUM_INDICATORS = ['rsi', 'macd', 'macd_signal', 'macd_histogram',
                       'stoch_k', 'stoch_d', 'cci', 'williams_r', 'momentum', 'roc']

MOVING_AVERAGES = ['sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_20',
                   'ema_26', 'ema_50', 'ema_200', 'kama']

VOLATILITY = ['bollinger_upper', 'bollinger_middle', 'bollinger_lower',
              'bb_width', 'atr', 'adx', 'plus_di', 'minus_di']

VOLUME_INDICATORS = ['obv', 'pvo', 'ppo', 'mfi', 'cmf']

ICHIMOKU = ['ichimoku_tenkan', 'ichimoku_kijun', 'ichimoku_senkou_a',
            'ichimoku_senkou_b', 'ichimoku_chikou']
```
```

---

### 3. ADD: Indicator Calculation Standards (Saleem's Corrections)

**Why:** Ensures consistent indicator calculations matching TradingView

```markdown
## INDICATOR CALCULATION STANDARDS

All indicators must match TradingView/Industry standards:

### Wilder's RMA (NOT simple EMA)
```python
# Use for: RSI, ATR, ADX, +DI, -DI
ewm(alpha=1/period, adjust=False, min_periods=period)
```

### Slow Stochastic (NOT Fast)
```python
# Smooth %K with SMA(3) before calculating %D
raw_k = 100 * (close - lowest_low) / (highest_high - lowest_low)
k = raw_k.rolling(3).mean()  # Smoothed %K
d = k.rolling(3).mean()      # %D
```

### ROC Period = 10 (NOT 12)
```python
roc = ((close - close.shift(10)) / close.shift(10)) * 100
```

### Bollinger Bands: Population Std Dev
```python
std = series.rolling(20).std(ddof=0)  # ddof=0 NOT ddof=1
```

### Ichimoku: Forward Shift
```python
senkou_a = senkou_a_raw.shift(26)  # Shift forward 26 periods
senkou_b = senkou_b_raw.shift(26)  # Shift forward 26 periods
```
```

---

### 4. ADD: Cloud Run Deployment Commands

**Why:** Quick reference for deploying API and frontend

```markdown
## CLOUD RUN DEPLOYMENT

### API Deployment
```bash
cd cloud_function_api
gcloud run deploy trading-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 540 \
  --project aialgotradehits
```

### Frontend Deployment
```bash
cd stock-price-app
npm run build
gcloud run deploy crypto-trading-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project aialgotradehits
```

### Current Live URLs
- **API:** https://trading-api-1075463475276.us-central1.run.app
- **Frontend:** https://crypto-trading-app-1075463475276.us-central1.run.app
```

---

### 5. ADD: API Endpoints Reference

**Why:** Quick lookup for available endpoints

```markdown
## API ENDPOINTS REFERENCE

### Data Endpoints
```
GET /api/stocks/history?symbol=NVDA&limit=500
GET /api/crypto/daily/history?pair=BTC/USD&limit=500
GET /api/stocks/15min/history?symbol=NVDA
GET /api/crypto/5min/history?pair=ETH/USD
```

### Download Endpoints (NEW)
```
GET  /api/download/indicators          - List indicator groups
GET  /api/download/symbol-lists        - Predefined lists (S&P 500, Nasdaq, etc.)
GET  /api/download/symbols/search?q=   - Symbol autocomplete
GET  /api/download/limits?tier=        - User tier limits
POST /api/download/preview             - Estimate size/rows
POST /api/download/data                - Generate CSV/Excel
```

### AI Endpoints
```
POST /api/ai/chat                      - Conversational AI
POST /api/ai/nlp-query                 - Natural language to SQL
GET  /api/ai/training-docs             - ML training documentation
```

### Admin Endpoints
```
GET  /api/admin/scheduler-status       - Scheduler monitoring
POST /api/admin/trigger-scheduler      - Manual trigger
GET  /api/admin/table-counts           - Database stats
```
```

---

### 6. ADD: React Component Structure

**Why:** Quick reference for frontend components

```markdown
## REACT COMPONENT REFERENCE

### Key Components (stock-price-app/src/components/)
| Component | Purpose |
|-----------|---------|
| TradingDashboard.jsx | Main dashboard with charts |
| DataDownloadWizard.jsx | 4-step ML data export wizard |
| SmartSearchBar.jsx | Symbol search with autocomplete |
| ProfessionalChart.jsx | TradingView-style charts |
| NLPSearch.jsx | Natural language query interface |
| DatabaseMonitoring.jsx | Admin data health dashboard |
| SchedulerMonitoring.jsx | Scheduler status viewer |

### Environment Variables
```bash
VITE_API_BASE_URL=https://trading-api-1075463475276.us-central1.run.app
```
```

---

### 7. ADD: Symbol Coverage

**Why:** Know what data is available

```markdown
## DATA COVERAGE

### Stocks (110 symbols)
Top holdings from S&P 500, Nasdaq 100, Dow 30:
AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, BRK.B, UNH, XOM,
JNJ, JPM, V, PG, MA, HD, CVX, MRK, ABBV, LLY... (full 110)

### Crypto (46 symbols)
BTC, ETH, BNB, XRP, ADA, SOL, DOGE, DOT, AVAX, SHIB,
MATIC, LTC, TRX, LINK, ATOM, UNI, XLM, ALGO... (full 46)

### Data Depth
- Daily: Up to 20 years historical
- Hourly: Up to 2 years
- 5-min: 30 days rolling
```

---

### 8. ADD: User Tier System

**Why:** Understand access control for features

```markdown
## USER TIER SYSTEM

| Tier | Max Symbols | Max Years | Downloads/Hour |
|------|-------------|-----------|----------------|
| Regular | 10 | 2 | 5 |
| Power | 100 | 5 | 20 |
| Admin | Unlimited | Unlimited | Unlimited |

### Tier Detection
```python
user.subscription_tier  # 'regular', 'power', 'admin'
```
```

---

### 9. ADD: Common BigQuery Patterns

**Why:** Efficient queries specific to this schema

```markdown
## BIGQUERY QUERY PATTERNS

### Get latest data per symbol
```sql
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY symbol ORDER BY datetime DESC
  ) as rn
  FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
)
WHERE rn = 1
```

### Find oversold stocks with strong trend
```sql
SELECT symbol, close, rsi, adx, sma_200
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND rsi < 30 AND adx > 25 AND close > sma_200
ORDER BY rsi ASC
```

### MACD crossover signals
```sql
SELECT symbol, datetime, close, macd, macd_signal,
  CASE WHEN macd > macd_signal
       AND LAG(macd) OVER (PARTITION BY symbol ORDER BY datetime) < LAG(macd_signal) OVER (PARTITION BY symbol ORDER BY datetime)
  THEN 'BUY' ELSE NULL END as signal
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE symbol = 'AAPL' AND datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
```
```

---

### 10. ADD: Error Handling Standards

**Why:** Consistent error handling across codebase

```markdown
## ERROR HANDLING STANDARDS

### Python (Cloud Functions)
```python
try:
    result = client.query(query).result()
    return jsonify({'success': True, 'data': [sanitize_row(r) for r in result]})
except Exception as e:
    logger.error(f"Query error: {str(e)}")
    return jsonify({'success': False, 'error': str(e)}), 500
```

### Float Sanitization (Required for JSON)
```python
def safe_float(val):
    if val is None: return None
    f = float(val)
    return None if math.isinf(f) or math.isnan(f) else f
```

### BigQuery Row Sanitization
```python
def sanitize_row(row):
    row_dict = dict(row)
    for key, value in row_dict.items():
        if hasattr(value, 'isoformat'):
            row_dict[key] = value.isoformat()
        elif isinstance(value, float):
            row_dict[key] = safe_float(value)
    return row_dict
```
```

---

## SUGGESTED NEW MASTER QUERY STRUCTURE

```markdown
# CLAUDE CODE MASTER PROMPT v2.0
## AIAlgoTradeHits.com - Trading Intelligence Platform

[Copy entire prompt at session start]

---

## 1. PROJECT CONTEXT
- Platform: AIAlgoTradeHits.com
- Primary GCP Project: aialgotradehits
- Dataset: crypto_trading_data
- Region: us-central1

## 2. API SUBSCRIPTIONS
[Keep existing TwelveData, Kraken, CMC, Finnhub sections]

## 3. BIGQUERY SCHEMA
[Add table structures and 97-field reference]

## 4. INDICATOR STANDARDS
[Add Saleem's calculation corrections]

## 5. DEPLOYMENT COMMANDS
[Add Cloud Run deploy commands]

## 6. API ENDPOINTS
[Add full endpoint reference]

## 7. REACT COMPONENTS
[Add component quick reference]

## 8. OPTIMIZATION RULES
[Keep existing parallel processing guidelines]

## 9. QUERY PATTERNS
[Add common BigQuery patterns]

## 10. ERROR HANDLING
[Add sanitization standards]

---

*Last Updated: December 2025*
*Version: 2.0*
```

---

## ITEMS TO REMOVE/UPDATE

1. **Update Project ID:** Change `cryptobot-462709` to `aialgotradehits` throughout
2. **Update Model References:** Change `gemini-2.0-pro` to `gemini-2.5-pro` (latest)
3. **Add Cloud Run URLs:** Include actual production URLs
4. **Add User Tier System:** For download limits enforcement

---

## SUMMARY

These additions will make the master query more useful by:
1. Clarifying the correct GCP project
2. Providing exact schema references
3. Documenting indicator calculation standards
4. Adding deployment commands
5. Including API endpoint reference
6. Providing BigQuery query patterns
7. Standardizing error handling

**Estimated improvement:** 40% faster context-building for Claude sessions
