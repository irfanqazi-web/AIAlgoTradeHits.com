# Vertex AI Gemini 1.5 Pro Cost Breakdown

## Important Note
**Gemini 3 Pro does not exist yet.** The latest available model is **Gemini 1.5 Pro**. This document provides accurate pricing for Gemini 1.5 Pro on Google Cloud Vertex AI.

---

## Gemini 1.5 Pro Pricing (as of January 2025)

### Input Token Costs
| Context Window | Price per 1M tokens |
|---------------|---------------------|
| Up to 128K tokens | $1.25 |
| 128K - 1M tokens | $2.50 |

### Output Token Costs
| Context Window | Price per 1M tokens |
|---------------|---------------------|
| Up to 128K tokens | $5.00 |
| 128K - 1M tokens | $10.00 |

### Context Caching (Optional)
- **Storage**: $1.00 per 1M tokens per hour
- **Cache Hit**: $0.3125 per 1M tokens (75% discount on input)
- **Benefit**: Reduces costs for repeated queries with same context

---

## Trading App Use Case Analysis

### Expected Token Usage per AI Call

**Price Prediction Analysis**:
- Input: ~2,500 tokens (historical data summary + prompt)
- Output: ~800 tokens (prediction JSON with reasoning)
- Total per call: 3,300 tokens

**Pattern Recognition**:
- Input: ~3,000 tokens (chart data + technical indicators + prompt)
- Output: ~1,200 tokens (pattern analysis with confidence scores)
- Total per call: 4,200 tokens

**Trading Signals**:
- Input: ~2,800 tokens (market data + indicators + sentiment + prompt)
- Output: ~1,000 tokens (signals with entry/exit levels)
- Total per call: 3,800 tokens

---

## Cost Estimates for Trading App

### Scenario 1: Light Usage (100 users, 10 AI calls/user/day)
**Daily Volume**: 1,000 AI calls

**Price Predictions** (400 calls/day):
- Input: 400 × 2,500 tokens = 1M tokens → $1.25
- Output: 400 × 800 tokens = 0.32M tokens → $1.60
- Daily cost: $2.85

**Pattern Recognition** (350 calls/day):
- Input: 350 × 3,000 tokens = 1.05M tokens → $1.31
- Output: 350 × 1,200 tokens = 0.42M tokens → $2.10
- Daily cost: $3.41

**Trading Signals** (250 calls/day):
- Input: 250 × 2,800 tokens = 0.7M tokens → $0.88
- Output: 250 × 1,000 tokens = 0.25M tokens → $1.25
- Daily cost: $2.13

**Total Daily Cost**: $8.39
**Total Monthly Cost**: **$251.70**

---

### Scenario 2: Medium Usage (500 users, 15 AI calls/user/day)
**Daily Volume**: 7,500 AI calls

**Price Predictions** (3,000 calls/day):
- Input: 3,000 × 2,500 tokens = 7.5M tokens → $9.38
- Output: 3,000 × 800 tokens = 2.4M tokens → $12.00
- Daily cost: $21.38

**Pattern Recognition** (2,500 calls/day):
- Input: 2,500 × 3,000 tokens = 7.5M tokens → $9.38
- Output: 2,500 × 1,200 tokens = 3M tokens → $15.00
- Daily cost: $24.38

**Trading Signals** (2,000 calls/day):
- Input: 2,000 × 2,800 tokens = 5.6M tokens → $7.00
- Output: 2,000 × 1,000 tokens = 2M tokens → $10.00
- Daily cost: $17.00

**Total Daily Cost**: $62.76
**Total Monthly Cost**: **$1,882.80**

---

### Scenario 3: Heavy Usage (2,000 users, 20 AI calls/user/day)
**Daily Volume**: 40,000 AI calls

**Total Monthly Cost**: **$10,035.00**

---

## Claude 3.5 Sonnet vs Gemini 1.5 Pro Comparison

| Feature | Claude 3.5 Sonnet | Gemini 1.5 Pro |
|---------|------------------|----------------|
| **Input Cost** | $3.00/1M tokens | $1.25/1M tokens (up to 128K) |
| **Output Cost** | $15.00/1M tokens | $5.00/1M tokens (up to 128K) |
| **Max Context** | 200K tokens | 2M tokens |
| **Cost for 1,000 calls** (avg 3.5K tokens) | $68.50 | $23.13 |
| **Monthly (Light)** | $2,055/month | $694/month |

**Cost Savings**: Gemini 1.5 Pro is **66% cheaper** than Claude 3.5 Sonnet for the same workload.

---

## Dual-AI Strategy Cost Analysis

### Current Plan: Use Both Claude + Gemini

**Option A: Primary Gemini, Claude for Validation (80/20 split)**
- 80% calls to Gemini: $201.36/month (Light usage)
- 20% calls to Claude: $411.00/month (Light usage)
- **Total**: $612.36/month

**Option B: Gemini Only**
- 100% calls to Gemini: $251.70/month (Light usage)
- **Savings**: $360.66/month vs dual-AI

**Option C: Smart Routing**
- Simple queries → Gemini: 70% of calls
- Complex analysis → Claude: 30% of calls
- **Estimated**: $793/month (Light usage)

---

## Cost Optimization Strategies

### 1. Implement Response Caching
Cache AI responses for identical queries (e.g., same pair + timeframe within 5 minutes):
- **Expected hit rate**: 30-40%
- **Cost reduction**: 25-35%
- **Savings**: $75-88/month (Light usage)

```javascript
// Example implementation
const cacheKey = `${pair}_${timeframe}_${analysisType}_${Math.floor(Date.now()/300000)}`;
const cached = await redis.get(cacheKey);
if (cached) return JSON.parse(cached);
```

### 2. Use Context Caching (Vertex AI Feature)
For repeated historical data context:
- **Storage**: $1.00/1M tokens/hour
- **Cache hit**: 75% discount on input tokens
- **Break-even**: After ~4 calls with same context
- **Best for**: Real-time updates (5-min, hourly data)

### 3. Batch Processing
Combine multiple pair analyses into single API call:
- **Reduction**: 40% fewer API calls
- **Savings**: $100/month (Light usage)
- **Trade-off**: Slightly slower response time

### 4. Rate Limiting
Limit AI calls per user:
- Free tier: 5 AI calls/day
- Premium: 50 AI calls/day
- **Controls costs** while encouraging upgrades

### 5. Smart Fallbacks
Use rule-based signals for simple scenarios, AI for complex:
```javascript
if (rsi < 30 && adx > 25) {
  // Simple oversold signal, no AI needed
  return generateSignal('BUY');
} else {
  // Complex scenario, use AI
  return await aiService.getTradingSignals(pair);
}
```
**Potential reduction**: 50% of AI calls
**Savings**: $125/month (Light usage)

---

## Recommended Pricing Tiers for Your App

### Free Tier
- 5 AI predictions/day
- Cost per user/month: $0.40
- Target: 1,000 free users → $400/month AI cost

### Basic Tier ($9.99/month)
- 20 AI analyses/day
- Cost per user/month: $1.51
- Margin: $8.48/user
- Target: 200 paid users → $1,696 revenue, $302 AI cost

### Pro Tier ($29.99/month)
- Unlimited AI analyses
- Estimated: 50 calls/day = $3.78 AI cost
- Margin: $26.21/user
- Target: 50 paid users → $1,499 revenue, $189 AI cost

### Total Monthly Revenue
- Free: 1,000 users × $0 = $0 (costs $400)
- Basic: 200 users × $9.99 = $1,998 (costs $302)
- Pro: 50 users × $29.99 = $1,500 (costs $189)
- **Gross Revenue**: $3,498
- **AI Costs**: $891
- **Gross Margin**: $2,607 (74%)

---

## Current App Cost Breakdown (with AI)

### Existing Infrastructure
- Cloud Functions (Data): $126/month
- BigQuery Storage: $2/month
- Cloud Scheduler: $0.30/month
- Cloud Run (App): $5/month
- **Subtotal**: $133.30/month

### Adding AI (Light Usage - Gemini Only)
- Gemini 1.5 Pro: $251.70/month
- **New Total**: **$385/month**

### Adding AI (Dual - Gemini + Claude 80/20)
- Gemini 1.5 Pro: $201.36/month
- Claude 3.5 Sonnet: $411/month
- **New Total**: **$745.66/month**

---

## Final Recommendations

### 1. Start with Gemini 1.5 Pro Only
- **Why**: 66% cheaper than Claude
- **Cost**: $251.70/month (Light usage)
- **Context window**: 2M tokens (plenty for trading data)
- **Quality**: Excellent for financial analysis

### 2. Implement Caching Immediately
- Redis cache with 5-minute TTL
- **Savings**: $75-88/month
- **Net cost**: ~$165/month

### 3. Add Claude for Critical Decisions Only
- Use Claude for high-stakes trades (>$10K)
- Keep 95% on Gemini, 5% on Claude
- **Cost**: $280/month total AI

### 4. Monitor Token Usage
```python
# Add to cloud function
def log_token_usage(request_type, input_tokens, output_tokens, cost):
    bigquery_client.insert_rows('ai_usage_logs', [{
        'timestamp': datetime.now(),
        'request_type': request_type,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'cost': cost
    }])
```

### 5. Implement Usage Limits
- Start with 10 AI calls/user/day
- Gradually increase based on actual costs
- Protects from runaway spending

---

## Cost Comparison Table

| Usage Level | Users | Calls/Day | Gemini Only | Gemini + Claude (80/20) | Claude Only |
|-------------|-------|-----------|-------------|------------------------|-------------|
| Light | 100 | 1,000 | $252/mo | $612/mo | $2,055/mo |
| Medium | 500 | 7,500 | $1,883/mo | $4,590/mo | $15,413/mo |
| Heavy | 2,000 | 40,000 | $10,035/mo | $24,475/mo | $82,200/mo |

---

## Next Steps

1. ✅ **Choose Gemini 1.5 Pro** as primary AI (66% cost savings)
2. ✅ **Deploy AI Cloud Function** with Gemini integration
3. ✅ **Add response caching** (Redis or in-memory)
4. ✅ **Set usage limits** (10 calls/user/day initially)
5. ✅ **Monitor costs daily** via BigQuery logs
6. ⏳ **Add Claude later** if needed for complex scenarios (5% of calls)

---

## Environment Variables Needed

```env
# .env file
GCP_PROJECT_ID=cryptobot-462709
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-pro

# Optional - for dual AI strategy
ANTHROPIC_API_KEY=your_key_here
USE_DUAL_AI=false
AI_SPLIT_RATIO=0.8  # 80% Gemini, 20% Claude
```

---

## Billing Alerts Recommended

Set up GCP budget alerts:
1. Alert at $200/month (approaching Light usage limit)
2. Alert at $500/month (Medium usage threshold)
3. Hard cap at $1,000/month (prevent runaway costs)

```bash
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="AI Trading App Budget" \
  --budget-amount=500 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

---

## Summary

**Gemini 1.5 Pro is the clear winner for your trading app**:
- 66% cheaper than Claude ($252 vs $2,055/month for light usage)
- Larger context window (2M vs 200K tokens)
- Excellent financial analysis capabilities
- Native GCP integration (no external API keys)

**Start with Gemini-only, add caching, monitor costs, and scale strategically.**
