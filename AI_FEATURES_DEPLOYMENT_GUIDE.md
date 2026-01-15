# AI Features Deployment Guide

Complete guide for deploying AI-powered trading intelligence features using Claude (Anthropic) and GCP Vertex AI.

## Overview

The AI trading intelligence system consists of:
- **Backend**: Python Cloud Function that interfaces with Claude and Vertex AI
- **Frontend**: React components to display AI predictions, patterns, and signals
- **Data Source**: BigQuery crypto trading data with technical indicators

## Architecture

```
User → React App → AI Cloud Function → Claude API
                                     → Vertex AI (Gemini)
                                     → BigQuery (Historical Data)
```

## Prerequisites

1. **GCP Project**: `cryptobot-462709` (already configured)
2. **Anthropic API Key**: Get from https://console.anthropic.com/
3. **Google Cloud SDK**: Already installed (`gcloud` command available)
4. **Python 3.11+**: Already installed (Python 3.13.7)
5. **Node.js**: For frontend development (already set up)

## Step 1: Get Your Anthropic API Key

1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-api03-...`)
6. Keep it secure - you'll need it for deployment

**Pricing**: Claude API is pay-as-you-go:
- ~$0.003 per prediction request
- Estimated monthly cost: $20-50 (depending on usage)

## Step 2: Set Environment Variables

### For Backend (Cloud Function)

Set the Anthropic API key as environment variable:

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your-api-key-here"

# Windows CMD
set ANTHROPIC_API_KEY=your-api-key-here
```

### For Frontend (.env file)

Update `stock-price-app/.env`:

```env
VITE_API_URL=http://localhost:8080
VITE_AI_FUNCTION_URL=https://ai-trading-intelligence-<will-be-set-after-deployment>-uc.a.run.app
VITE_ENABLE_AI_PREDICTIONS=true
VITE_ENABLE_AI_PATTERNS=true
VITE_ENABLE_AI_SIGNALS=true
```

## Step 3: Deploy AI Cloud Function

Navigate to the AI function directory and deploy:

```bash
cd cloud_function_ai
python deploy.py
```

The deployment process:
1. Packages the function code
2. Uploads to Google Cloud
3. Sets environment variables (including ANTHROPIC_API_KEY)
4. Creates HTTP endpoint
5. Takes 3-5 minutes

**Expected Output:**
```
Deploying ai-trading-intelligence to cryptobot-462709...
Region: us-central1
Memory: 2GB
Timeout: 540s

This may take 3-5 minutes...

✅ Deployment successful!

🔗 Function URL: https://ai-trading-intelligence-cnyn5l4u2a-uc.a.run.app
```

**Copy the Function URL** - you'll need it for the next step!

## Step 4: Update Frontend Configuration

Update the AI function URL in `stock-price-app/.env`:

```env
VITE_AI_FUNCTION_URL=https://ai-trading-intelligence-cnyn5l4u2a-uc.a.run.app
```

Restart the development server:

```bash
cd stock-price-app
npm run dev
```

## Step 5: Enable Vertex AI

Vertex AI uses Google Cloud's Application Default Credentials (already configured).

Enable the Vertex AI API:

```bash
gcloud services enable aiplatform.googleapis.com --project=cryptobot-462709
```

## Step 6: Test the AI Features

### Test Backend (Cloud Function)

**Test AI Predictions:**
```bash
curl "https://ai-trading-intelligence-cnyn5l4u2a-uc.a.run.app?pair=BTCUSD&type=prediction&ai_provider=claude"
```

**Test Pattern Recognition:**
```bash
curl "https://ai-trading-intelligence-cnyn5l4u2a-uc.a.run.app?pair=BTCUSD&type=pattern&ai_provider=vertex"
```

**Test Trading Signals:**
```bash
curl "https://ai-trading-intelligence-cnyn5l4u2a-uc.a.run.app?pair=BTCUSD&type=signal&ai_provider=both"
```

### Test Frontend

1. Navigate to http://localhost:5173/
2. Login with your credentials
3. Click on **AI Signals** in the left menu
4. Select **Predictions**, **Patterns**, or **Signals**
5. You should see AI-generated analysis!

## Available AI Features

### 1. AI Price Predictions
- **Endpoint**: `?type=prediction`
- **Features**:
  - 1-hour, 24-hour, and 7-day price forecasts
  - Confidence levels (0-100%)
  - Bullish/Bearish/Neutral trend analysis
  - Key factors influencing prediction
  - Risk level assessment
  - Buy/Sell/Hold recommendation

### 2. AI Pattern Recognition
- **Endpoint**: `?type=pattern`
- **Features**:
  - Detects classic chart patterns (head & shoulders, triangles, etc.)
  - Identifies support and resistance levels
  - Pattern reliability scoring
  - Breakout probability
  - Recommended trading actions

### 3. AI Trade Signals
- **Endpoint**: `?type=signal`
- **Features**:
  - Strong Buy/Buy/Hold/Sell/Strong Sell signals
  - Entry price recommendations
  - Multiple target prices (3 levels)
  - Stop-loss suggestions
  - Risk/reward ratio calculations
  - Trading timeframe recommendations

## AI Provider Options

Use the `ai_provider` parameter to select:
- `claude`: Use only Anthropic Claude
- `vertex`: Use only GCP Vertex AI (Gemini)
- `both`: Use both providers and get consensus (recommended)

**Example:**
```
?pair=BTCUSD&type=prediction&ai_provider=both
```

## Monitoring and Logs

### View Cloud Function Logs

```bash
gcloud functions logs read ai-trading-intelligence --project=cryptobot-462709 --limit=50
```

### Check Function Status

```bash
gcloud functions describe ai-trading-intelligence --region=us-central1 --project=cryptobot-462709
```

## Cost Estimation

### Monthly Operating Costs

**AI Cloud Function:**
- Invocations: ~10,000/month
- Memory: 2GB @ 540s timeout
- Estimated: $30-40/month

**Anthropic Claude API:**
- Sonnet 3.5: $3 per million input tokens, $15 per million output tokens
- Estimated: $20-50/month (depends on usage)

**Vertex AI (Gemini):**
- Gemini 1.5 Pro: $1.25 per million input tokens, $5 per million output tokens
- Estimated: $10-30/month

**Total AI Features Cost: ~$60-120/month**

Combined with existing infrastructure:
- **Total System Cost: ~$200-260/month**

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"
**Solution**: Set the environment variable before deploying:
```bash
$env:ANTHROPIC_API_KEY="your-key"
cd cloud_function_ai
python deploy.py
```

### Issue: "Vertex AI API not enabled"
**Solution**: Enable the API:
```bash
gcloud services enable aiplatform.googleapis.com --project=cryptobot-462709
```

### Issue: "No data available"
**Solution**: Ensure BigQuery tables are populated:
```bash
python check_bigquery_counts.py
```

### Issue: "CORS error in browser"
**Solution**: The function already includes CORS headers. Clear browser cache or try incognito mode.

### Issue: "Function timeout"
**Solution**: AI analysis can take 20-60 seconds. The timeout is set to 540s (9 minutes) to accommodate this.

## Security Best Practices

1. **API Keys**: Never commit API keys to git
2. **Function Access**: Keep function public for scheduler access, but implement rate limiting if needed
3. **Data Privacy**: No user data is sent to AI providers, only aggregated market data
4. **Audit Logs**: Enable Cloud Audit Logging for the function

## Next Steps

After deployment:

1. **Test all three AI features** (predictions, patterns, signals)
2. **Monitor costs** in GCP Console → Billing
3. **Check accuracy** by comparing predictions to actual price movements
4. **Add more pairs** by updating the symbol parameter
5. **Implement caching** to reduce API costs (cache predictions for 1 hour)
6. **Add rate limiting** to prevent abuse
7. **Build AI dashboard** to track prediction accuracy over time

## Advanced Configuration

### Add More Trading Pairs

Update the frontend to allow selecting different pairs:

```javascript
<AIPredictions symbol={selectedPair} timeframe="daily" />
```

### Add More Timeframes

Support hourly and 5-minute predictions:

```javascript
<AIPredictions symbol="BTCUSD" timeframe="hourly" />
```

### Implement Caching

Add Redis or Memcached to cache AI predictions for 1 hour:
- Reduces API costs by 90%+
- Improves response time
- Estimated additional cost: $10/month

## Support

For issues or questions:
1. Check GCP Cloud Function logs
2. Test the function endpoint directly with curl
3. Verify BigQuery data is available
4. Check Anthropic API usage dashboard

## API Endpoint Reference

**Base URL**: `https://ai-trading-intelligence-<hash>-uc.a.run.app`

**Parameters:**
- `pair` (required): Trading pair (e.g., BTCUSD, ETHUSD)
- `type` (required): prediction, pattern, or signal
- `timeframe` (optional): daily, hourly, 5min (default: daily)
- `ai_provider` (optional): claude, vertex, both (default: both)

**Example Requests:**

```bash
# Get price predictions using both AI providers
curl "https://[FUNCTION_URL]?pair=BTCUSD&type=prediction&ai_provider=both"

# Get pattern analysis using Claude
curl "https://[FUNCTION_URL]?pair=ETHUSD&type=pattern&ai_provider=claude"

# Get trading signals for hourly timeframe
curl "https://[FUNCTION_URL]?pair=BTCUSD&type=signal&timeframe=hourly"
```

**Response Format:**

```json
{
  "pair": "BTCUSD",
  "timeframe": "daily",
  "analysis_type": "prediction",
  "timestamp": "2025-11-18T16:00:00Z",
  "current_price": 95234.50,
  "claude_analysis": {
    "prediction_1h": 95450.00,
    "prediction_24h": 96200.00,
    "prediction_7d": 98500.00,
    "confidence": 78,
    "trend": "bullish",
    "key_factors": ["Strong RSI momentum", "Breaking resistance"],
    "risk_level": "medium",
    "recommendation": "buy"
  },
  "vertex_analysis": { ... },
  "consensus": {
    "providers_agree": true,
    "confidence": 85,
    "recommendation": "buy"
  }
}
```

---

## Deployment Checklist

- [ ] Get Anthropic API key
- [ ] Set ANTHROPIC_API_KEY environment variable
- [ ] Enable Vertex AI API
- [ ] Deploy AI Cloud Function
- [ ] Copy Function URL
- [ ] Update frontend .env with Function URL
- [ ] Test predictions endpoint
- [ ] Test patterns endpoint
- [ ] Test signals endpoint
- [ ] Verify frontend displays AI data
- [ ] Monitor costs in GCP Console
- [ ] Set up billing alerts

## Status

**Current Status**: Ready for deployment

**Deployment Time**: ~10 minutes total

**Next Action**: Run `cd cloud_function_ai && python deploy.py`
