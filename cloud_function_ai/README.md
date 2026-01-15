# AI Trading Intelligence Cloud Function

Python Cloud Function that provides AI-powered trading analysis using Anthropic Claude and GCP Vertex AI.

## Features

- **Price Predictions**: 1h, 24h, 7-day forecasts with confidence levels
- **Pattern Recognition**: Chart patterns, support/resistance levels
- **Trading Signals**: Buy/sell recommendations with entry/exit prices
- **Dual AI Providers**: Claude + Vertex AI with consensus analysis

## Quick Start

### 1. Set API Key

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your-api-key-here"
```

### 2. Deploy

```bash
python deploy.py
```

### 3. Test

```bash
curl "https://[YOUR-FUNCTION-URL]?pair=BTCUSD&type=prediction&ai_provider=both"
```

## API Endpoints

**Base URL**: Set after deployment

### Parameters

- `pair` (required): Trading pair (e.g., BTCUSD, ETHUSD)
- `type` (required): prediction | pattern | signal
- `timeframe` (optional): daily | hourly | 5min (default: daily)
- `ai_provider` (optional): claude | vertex | both (default: both)

### Examples

**Price Predictions:**
```bash
curl "[URL]?pair=BTCUSD&type=prediction&ai_provider=both"
```

**Pattern Analysis:**
```bash
curl "[URL]?pair=ETHUSD&type=pattern&ai_provider=claude"
```

**Trading Signals:**
```bash
curl "[URL]?pair=BTCUSD&type=signal&timeframe=hourly"
```

## Configuration

Edit `deploy.py` to change:
- Memory allocation (default: 2GB)
- Timeout (default: 540s)
- Region (default: us-central1)

## Dependencies

See `requirements.txt`:
- `anthropic`: Claude API client
- `google-cloud-aiplatform`: Vertex AI client
- `google-cloud-bigquery`: Data source
- `pandas`, `numpy`: Data processing
- `tensorflow`: Future ML models

## Cost

- Function execution: ~$30-40/month
- Claude API: ~$20-50/month
- Vertex AI: ~$10-30/month

**Total**: ~$60-120/month

## Monitoring

```bash
# View logs
gcloud functions logs read ai-trading-intelligence --project=cryptobot-462709 --limit=50

# Check status
gcloud functions describe ai-trading-intelligence --region=us-central1
```

## Security

- API keys stored as environment variables
- CORS enabled for frontend access
- Public function (required for HTTP trigger)
- No user data sent to AI providers

## Development

**Local Testing:**
```bash
functions-framework --target=ai_trading_intelligence --debug
```

**Update Function:**
```bash
python deploy.py
```

## Troubleshooting

**Issue**: "ANTHROPIC_API_KEY not set"
- Set environment variable before deploying

**Issue**: "Vertex AI not enabled"
```bash
gcloud services enable aiplatform.googleapis.com --project=cryptobot-462709
```

**Issue**: "No data available"
- Check BigQuery tables are populated
```bash
cd ..
python check_bigquery_counts.py
```

## Support

See main project documentation: `../AI_FEATURES_DEPLOYMENT_GUIDE.md`
