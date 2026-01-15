# Stock Data Pipeline - Deployment Guide

## Overview

This guide covers the deployment and usage of the daily stock data collection system with Elliott Wave theory and Fibonacci analysis for major US stocks, mirroring the crypto data pipeline.

## What's Included

### 1. Stock Coverage
- **100+ major US stocks** across sectors:
  - Tech Giants (FAANG+): AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, NFLX
  - Financial: JPM, BAC, WFC, GS, MS, C, V, MA
  - Healthcare: JNJ, UNH, PFE, ABBV, TMO, MRK
  - Energy: XOM, CVX, COP, SLB, EOG
  - Consumer: WMT, HD, MCD, NKE, SBUX
  - Industrial: BA, CAT, HON, UNP, UPS
  - ETFs: SPY, QQQ, DIA, IWM, VTI, VOO

### 2. Technical Indicators (81 Total Fields)

**Same comprehensive indicators as crypto:**

#### Price & Volume Data
- OHLC (Open, High, Low, Close)
- Volume, Dividends, Stock Splits

#### Moving Averages
- SMA (20, 50, 200)
- EMA (12, 26, 50)

#### Momentum Indicators
- RSI, MACD, ROC, Momentum
- Stochastic Oscillator, Williams %R

#### Volatility
- Bollinger Bands, ATR

#### Trend Indicators
- ADX, +DI, -DI

#### Oscillators
- CCI, PPO, Ultimate Oscillator, Awesome Oscillator

#### Volume Indicators
- OBV, PVO

#### Advanced Indicators
- KAMA, TRIX

### 3. Elliott Wave Analysis
- **wave_degree**: Classification (Minute, Minor, Intermediate, Primary, Cycle)
- **wave_position**: Current wave (1-5)
- **impulse_wave_count**: Impulse waves detected
- **corrective_wave_count**: Corrective waves detected
- **wave_1_high** through **wave_5_high**: Wave peak prices
- **trend_direction**: 1 (up), -1 (down), 0 (sideways)
- **trend_strength**: ADX-based strength
- **volatility_regime**: low, normal, high

### 4. Fibonacci Analysis

**Retracement Levels:**
- fib_0, fib_236, fib_382, fib_500, fib_618, fib_786, fib_100

**Extension Levels:**
- fib_ext_1272, fib_ext_1618, fib_ext_2618

**Distance Metrics:**
- dist_to_fib_236, dist_to_fib_382, dist_to_fib_500, dist_to_fib_618

### 5. Additional Fields
- **Price Changes**: 1d, 5d, 20d percentage changes
- **Company Info**: sector, industry, exchange
- **Helper Fields**: swing_high, swing_low, local_maxima, local_minima

## Deployment Steps

### Option A: Automated Setup (Recommended)

Run the complete setup script:

```bash
python setup_stock_pipeline.py
```

This will automatically:
1. Create BigQuery table
2. Fetch 6 months historical data
3. Upload with technical indicators
4. Deploy Cloud Function
5. Set up Cloud Scheduler

### Option B: Manual Step-by-Step Setup

#### Step 1: Install Dependencies

```bash
pip install yfinance pandas numpy google-cloud-bigquery
```

#### Step 2: Create BigQuery Table

```bash
python create_stock_bigquery_schema.py
```

Verify table creation:
```bash
bq show cryptobot-462709:crypto_trading_data.stock_analysis
```

#### Step 3: Fetch Historical Data (6 Months)

```bash
python stock_data_fetcher_6months.py
```

This creates:
- `stock_6month_ohlc_data.csv` - Raw OHLC data
- `stock_6month_summary.csv` - Summary statistics
- `stock_symbols_list.csv` - Stock symbols list

#### Step 4: Upload Historical Data to BigQuery

```bash
python upload_stocks_to_bigquery.py
```

This processes each stock:
- Calculates 81 technical indicators
- Computes Elliott Wave patterns
- Calculates Fibonacci levels
- Uploads to BigQuery

#### Step 5: Deploy Cloud Function

```bash
cd cloud_function_daily_stocks
python deploy_via_api.py
```

Or use gcloud directly:
```bash
gcloud functions deploy daily-stock-fetcher \
  --gen2 \
  --runtime python311 \
  --region us-central1 \
  --source . \
  --entry-point daily_stock_fetch \
  --trigger-http \
  --allow-unauthenticated \
  --timeout 540 \
  --memory 2Gi \
  --project cryptobot-462709
```

#### Step 6: Set Up Cloud Scheduler

```bash
gcloud scheduler jobs create http daily-stock-fetch-job \
  --location us-central1 \
  --schedule "0 0 * * *" \
  --uri https://us-central1-cryptobot-462709.cloudfunctions.net/daily-stock-fetcher \
  --http-method GET \
  --time-zone America/New_York \
  --project cryptobot-462709 \
  --description "Daily stock data fetch with technical indicators"
```

## Verification Steps

### 1. Test Cloud Function Manually

```bash
curl https://us-central1-cryptobot-462709.cloudfunctions.net/daily-stock-fetcher
```

### 2. Check BigQuery Data

```sql
-- Count records by symbol
SELECT
  symbol,
  company_name,
  sector,
  COUNT(*) as days,
  MIN(date) as first_date,
  MAX(date) as last_date
FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
GROUP BY symbol, company_name, sector
ORDER BY days DESC;
```

### 3. Verify Elliott Wave Data

```sql
SELECT
  symbol,
  company_name,
  close,
  elliott_wave_degree,
  wave_position,
  trend_direction,
  fib_618,
  fib_500,
  rsi,
  macd
FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND elliott_wave_degree IS NOT NULL
ORDER BY close DESC
LIMIT 20;
```

### 4. Check Fibonacci Levels

```sql
SELECT
  symbol,
  close,
  fib_618,
  fib_500,
  fib_382,
  dist_to_fib_618,
  dist_to_fib_500,
  trend_direction
FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND ABS(dist_to_fib_618) < 3  -- Within 3% of golden ratio
ORDER BY ABS(dist_to_fib_618) ASC
LIMIT 10;
```

## Example Trading Queries

### Find Stocks in Wave 3 (Strong Uptrend)

```sql
SELECT
  symbol,
  company_name,
  sector,
  close,
  wave_position,
  wave_3_high,
  trend_direction,
  rsi,
  adx,
  macd
FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND wave_position = 3
  AND trend_direction = 1
  AND rsi < 70  -- Not overbought
  AND adx > 25  -- Strong trend
ORDER BY adx DESC
LIMIT 10;
```

### Find Stocks at Fibonacci Support

```sql
SELECT
  symbol,
  company_name,
  sector,
  close,
  fib_618,
  fib_500,
  dist_to_fib_618,
  rsi,
  macd,
  trend_direction
FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND ABS(dist_to_fib_618) < 2  -- Within 2% of 61.8% level
  AND rsi < 40  -- Oversold
  AND trend_direction = 1
ORDER BY rsi ASC
LIMIT 10;
```

### Tech Stocks with Best Momentum

```sql
SELECT
  symbol,
  company_name,
  close,
  price_change_1d,
  price_change_5d,
  price_change_20d,
  rsi,
  macd,
  adx,
  volume
FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
WHERE DATE(datetime) = CURRENT_DATE() - 1
  AND sector = 'Technology'
  AND price_change_1d > 0
  AND rsi > 50
  AND macd > macd_signal
ORDER BY price_change_5d DESC
LIMIT 15;
```

### Combine Elliott Wave + Fibonacci + Technicals

```sql
WITH analysis AS (
  SELECT
    symbol,
    company_name,
    sector,
    close,
    elliott_wave_degree,
    wave_position,
    trend_direction,
    fib_618,
    fib_500,
    dist_to_fib_618,
    dist_to_fib_500,
    rsi,
    macd,
    macd_signal,
    adx,
    volume
  FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
  WHERE DATE(datetime) = CURRENT_DATE() - 1
)
SELECT *
FROM analysis
WHERE
  -- Elliott Wave: Wave 3 or early Wave 4
  wave_position IN (3, 4)
  -- Fibonacci: Near key retracement
  AND (ABS(dist_to_fib_500) < 3 OR ABS(dist_to_fib_618) < 3)
  -- Trend: Uptrend
  AND trend_direction = 1
  -- RSI: Not overbought
  AND rsi BETWEEN 40 AND 70
  -- MACD: Positive
  AND macd > macd_signal
  -- ADX: Strong trend
  AND adx > 25
ORDER BY adx DESC, rsi ASC
LIMIT 20;
```

## Monitoring

### Check Function Logs

```bash
gcloud functions logs read daily-stock-fetcher \
  --project cryptobot-462709 \
  --limit 50
```

### Verify Scheduler

```bash
gcloud scheduler jobs describe daily-stock-fetch-job \
  --location us-central1 \
  --project cryptobot-462709
```

### Manually Trigger Scheduler

```bash
gcloud scheduler jobs run daily-stock-fetch-job \
  --location us-central1 \
  --project cryptobot-462709
```

### Check Data Freshness

```sql
SELECT
  DATE(datetime) as date,
  COUNT(DISTINCT symbol) as unique_stocks,
  COUNT(*) as total_records,
  COUNTIF(elliott_wave_degree IS NOT NULL) as with_elliott_wave,
  COUNTIF(fib_618 IS NOT NULL) as with_fibonacci
FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
WHERE DATE(datetime) >= CURRENT_DATE() - 7
GROUP BY date
ORDER BY date DESC;
```

## Cost Estimates

Monthly costs for stock pipeline:

- **Cloud Functions**: ~$4/month
  - Executions: ~30/month (daily)
  - Duration: ~3 minutes per run
  - Memory: 2GB

- **BigQuery Storage**: ~$2/month
  - 100 stocks × 81 fields × 365 days

- **Cloud Scheduler**: $0.10/month

**Total Estimated Cost**: ~$6-7/month

Combined with crypto pipeline: ~$13-17/month total

## Troubleshooting

### Issue: Yahoo Finance Rate Limiting

If you encounter rate limiting:
1. Increase sleep time in `fetch_daily_stock_data()` to 1-2 seconds
2. Split stock list into batches

### Issue: Elliott Wave Not Detected

Some stocks may not have enough volatility:
- Requires minimum 13 daily candles
- Needs identifiable swing highs/lows
- Check `swing_high` and `swing_low` fields

### Issue: Schema Mismatch

If schema errors occur:
```bash
# Drop and recreate table
bq rm -f cryptobot-462709:crypto_trading_data.stock_analysis
python create_stock_bigquery_schema.py
```

### Issue: Function Timeout

If function times out:
1. Increase timeout to 540s (already set)
2. Reduce number of stocks in STOCK_SYMBOLS list
3. Split into multiple functions by sector

## Integration with Trading App

The stock data is now available alongside crypto data:

```javascript
// Query stock data from BigQuery
const stockQuery = `
  SELECT * FROM \`cryptobot-462709.crypto_trading_data.stock_analysis\`
  WHERE DATE(datetime) = CURRENT_DATE() - 1
  ORDER BY symbol
`;
```

Display Elliott Wave and Fibonacci levels on stock charts alongside crypto charts.

## Files Created

```
Trading/
├── stock_data_fetcher_6months.py          # Historical data fetcher
├── create_stock_bigquery_schema.py        # BigQuery table setup
├── upload_stocks_to_bigquery.py           # Upload with indicators
├── setup_stock_pipeline.py                # Automated setup script
├── cloud_function_daily_stocks/
│   ├── main.py                            # Cloud Function code
│   ├── requirements.txt                   # Dependencies
│   └── deploy_via_api.py                  # Deployment script
└── STOCK_DEPLOYMENT_GUIDE.md             # This file
```

## Next Steps

1. **Test the pipeline**:
   ```bash
   python setup_stock_pipeline.py
   ```

2. **Verify data**:
   ```bash
   bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM crypto_trading_data.stock_analysis'
   ```

3. **Integrate into trading app**: Add stock charts alongside crypto

4. **Set up alerts**: Create alerts when stocks hit Fibonacci levels or complete wave patterns

5. **Backfill more history** (optional): Extend to 1+ years for better Elliott Wave detection

---

**Last Updated**: 2025-11-07
**Version**: 1.0
**Project**: cryptobot-462709
**Data Source**: Yahoo Finance (yfinance)
