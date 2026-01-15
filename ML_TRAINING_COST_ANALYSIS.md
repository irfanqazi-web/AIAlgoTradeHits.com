# ML Walk-Forward Validation Cost Analysis

## Current System Architecture

### BigQuery ML Training Costs

**Per Model Training (XGBoost Classifier)**
- Training Data: ~1,000-5,000 rows per symbol
- BigQuery ML: $5.00 per TB processed
- Estimated per model: ~$0.005-0.02 per training

**Walk-Forward Validation Costs**

| Configuration | Models Trained | Est. Cost |
|---------------|----------------|-----------|
| 1 symbol, 20 days, weekly retrain | 4 models | ~$0.08 |
| 1 symbol, 252 days, weekly retrain | 50 models | ~$1.00 |
| 5 symbols, 252 days, weekly retrain | 250 models | ~$5.00 |

**Cloud Function Execution Costs**
- Memory: 4GB
- Timeout: 540s max
- Cost: ~$0.000016/GB-second
- Per 9-minute execution: ~$0.0035

### Total Estimated Costs Per Validation Run

| Run Type | BigQuery ML | Cloud Function | Total |
|----------|-------------|----------------|-------|
| Quick Test (1 symbol, 15 days) | $0.06 | $0.01 | ~$0.07 |
| Standard (1 symbol, 252 days) | $1.00 | $0.10 | ~$1.10 |
| Multi-Symbol (5 symbols, 252 days) | $5.00 | $0.50 | ~$5.50 |

## Cost Optimization Recommendations

### 1. Reduce Model Training Frequency
- **Weekly retrain**: 50 models/year/symbol (~$1.00)
- **Monthly retrain**: 12 models/year/symbol (~$0.24) - 76% savings
- **Recommendation**: Use monthly for production, weekly for backtesting

### 2. Pre-train and Cache Models
Instead of training models on-demand:
- Train models once per day via scheduled job
- Store trained model references in BigQuery
- Predictions use cached models
- **Savings**: 80-90% reduction in training costs

### 3. Batch Predictions
- Current: Individual predictions per day
- Optimized: Batch predict 30 days at once
- **Savings**: Reduced BigQuery queries by 30x

### 4. Use Smaller Feature Sets
- Current: 16 features
- Optimized: Top 8 most important features
- **Savings**: 50% reduction in processing time

### 5. Efficient Cloud Function
- Use Cloud Run instead (up to 60 min timeout)
- Async processing with Pub/Sub
- Store progress in Redis/Memorystore

## Monthly Cost Projections

### Low Usage (Development)
- 10 validation runs/month
- Mixed single/multi-symbol
- **Estimated Cost: $15-25/month**

### Medium Usage (Production)
- 50 validation runs/month
- Daily automated validations
- **Estimated Cost: $50-100/month**

### High Usage (Enterprise)
- 200+ validation runs/month
- Multiple timeframes, all symbols
- **Estimated Cost: $200-400/month**

## LLM Integration Cost Considerations

If integrating LLM for analysis:

### Vertex AI Gemini Pro
- Input: $0.00025/1K characters
- Output: $0.0005/1K characters
- Per analysis report (~2K input, 1K output): ~$0.001

### Claude API (for comparison)
- Input: $0.003/1K tokens
- Output: $0.015/1K tokens
- Per analysis report: ~$0.02

### Recommendation
- Use BigQuery ML for predictions (cheaper, faster)
- Use LLM only for generating human-readable reports
- Cache LLM responses for similar queries

## Implementation Priority

1. **Immediate**: Monthly retraining (saves 76%)
2. **Short-term**: Pre-trained model caching (saves 80%)
3. **Medium-term**: Batch predictions (saves query costs)
4. **Long-term**: Migrate to Cloud Run for longer runs

## Conclusion

The walk-forward validation system is cost-effective:
- Single validation: ~$1-5
- Monthly production: ~$50-100
- BigQuery ML is 10-100x cheaper than external ML APIs
- LLM integration adds minimal cost if used wisely
