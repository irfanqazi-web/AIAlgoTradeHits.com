# API Keys Reconciliation Document
Generated: December 5, 2025

## Summary of API Keys Found in Codebase

### 1. TwelveData API Key (Primary - $229/month Plan)
```
Key: 16ee060fd4d34a628a14bcb6f0167565
Plan: $229/month (Business Plan)
Rate Limit: 600 API credits/minute (approx 55 requests/minute for time_series)
```

**Files using this key:**
| File | Line | Status |
|------|------|--------|
| batch_weekly_data_fetcher.py | 23 | ACTIVE |
| weekly_batch_all_assets.py | 24 | ACTIVE |
| cloud_function_twelvedata/main.py | 34 | ACTIVE |
| cloud_function_twelvedata_stocks/main.py | 23 | ACTIVE |
| cloud_function_stocks_daily/main.py | 18 | ACTIVE |
| cloud_function_weekly_cryptos/main.py | 18 | ACTIVE |
| cloud_function_weekly_stocks/main.py | 18 | ACTIVE |
| local_twelvedata_fetcher.py | 22 | ACTIVE |
| fetch_sample_data.py | 17 | ACTIVE |
| fetch_all_stocks_basic.py | 21 | ACTIVE |
| fetch_all_historical_data.py | 30 | ACTIVE |
| fetch_additional_symbols.py | 27 | ACTIVE |
| fetch_fresh_twelvedata.py | 26 | ACTIVE |
| fetch_btc_nvda_ai_training_data.py | 42 | ACTIVE |
| fetch_historical_enhanced.py | 36 | ACTIVE |
| fetch_historical_extended.py | 34 | ACTIVE |
| fetch_today_data.py | 18 | ACTIVE |
| fetch_test_data.py | 25 | ACTIVE |
| backfill_historical_data.py | 38 | ACTIVE |
| explore_twelve_data_complete.py | 10 | ACTIVE |
| explore_twelve_data_news_sentiment.py | 10 | ACTIVE |
| test_twelve_data_api.py | 4 | ACTIVE |
| initialize_stocks_master_list.py | 27 | ACTIVE |

---

### 2. Finnhub API Key
```
Key: d4dg7t9r01qovljpm3g0d4dg7t9r01qovljpm3gg
Plan: Unknown (likely free tier)
```

**Files using this key:**
| File | Line | Status |
|------|------|--------|
| explore_finnhub_api.py | 16 | ACTIVE |

---

### 3. Anthropic API Key (Claude)
```
Key: Not set (placeholder only)
Status: Requires user to set environment variable
```

**Files referencing (placeholders only):**
- AI_FEATURES_DEPLOYMENT_GUIDE.md
- AI_FEATURES_IMPLEMENTATION_SUMMARY.md
- cloud_function_ai/README.md

---

### 4. Google Cloud Service Account
```
File: aialgotradehits-8863a22a9958.json
Project: aialgotradehits
```

---

## Incorrect/Old API Keys Found

### OLD TwelveData Key (NO LONGER VALID)
```
Key: 848dc760a3154cb0bf34f85b64845a57
Status: INVALID - was replaced
```
This key was previously in batch_weekly_data_fetcher.py but has been updated.

---

## Recommendations

### 1. Update Rate Limits for $229 Plan
Your TwelveData $229/month plan includes **600 API credits/minute**.

The current scripts use:
- `REQUESTS_PER_MINUTE = 8` (free tier limit)

Should be updated to:
- `REQUESTS_PER_MINUTE = 55` (paid tier - conservative estimate)

### 2. Files to Update Rate Limits:
- `weekly_batch_all_assets.py` - Line 28
- `batch_weekly_data_fetcher.py` - Line 29

### 3. Time Savings with Paid Plan:
| Scenario | Free Tier (8/min) | Paid Tier (55/min) | Improvement |
|----------|-------------------|--------------------| ------------|
| 20,000 stocks | ~42 hours | ~6 hours | 7x faster |
| All assets (1 week) | ~50 hours | ~7 hours | 7x faster |

---

## Action Required

Please confirm:
1. Is `16ee060fd4d34a628a14bcb6f0167565` your correct TwelveData API key for the $229/month plan?
2. Do you have any other API keys that should be added?
3. Should I update the rate limits to 55 requests/minute?
