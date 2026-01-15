# Morning Todo List - December 9, 2025 @ 8:00 AM

## PRIORITY 1: Check Overnight Process

### ✅ Step 1: Check if indicator calculation completed
```bash
tail -50 C:\1AITrading\Trading\indicator_calculation.log
```

**Look for:**
- "ALL DONE!" message
- "Processed: X/262 symbols"
- "Failed: X symbols"
- Completion timestamp

### ✅ Step 2: Run recovery check
```bash
python C:\1AITrading\Trading\resume_if_failed.py
```

**Expected output if successful:**
```
✅ ALL SYMBOLS COMPLETE! No recovery needed.
```

---

## PRIORITY 2: Validate Results

### ✅ Step 3: Check overall completion in BigQuery
```sql
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT symbol) as symbols,
    COUNTIF(rsi IS NOT NULL) as with_rsi,
    COUNTIF(macd IS NOT NULL) as with_macd,
    COUNTIF(sma_200 IS NOT NULL) as with_sma200,
    COUNTIF(bollinger_upper IS NOT NULL) as with_bbands,
    COUNTIF(rsi IS NOT NULL) * 100.0 / COUNT(*) as pct_complete
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`;
```

**Expected results:**
- Total rows: 1,141,844
- Symbols: 262
- Completion: ~99.5-99.8%

### ✅ Step 4: Sample AAPL data with indicators
```sql
SELECT
    datetime, symbol, close,
    rsi, macd, macd_signal,
    sma_20, sma_50, sma_200,
    bollinger_upper, bollinger_lower,
    trend_regime, vol_regime,
    volume_ratio
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE symbol = 'AAPL'
ORDER BY datetime DESC
LIMIT 10;
```

**Verify:**
- All indicator fields have values (not NULL)
- RSI between 0-100
- Trend_regime is 1, -1, or 0
- Vol_regime is 0 or 1

### ✅ Step 5: Check for any missing indicators
```sql
SELECT
    symbol,
    COUNT(*) as total_rows,
    COUNTIF(rsi IS NULL) as missing_rsi,
    COUNTIF(macd IS NULL) as missing_macd,
    COUNTIF(sma_200 IS NULL) as missing_sma200
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
GROUP BY symbol
HAVING missing_rsi > 0 OR missing_macd > 0
ORDER BY missing_rsi DESC;
```

**Expected:**
- Only early rows (< 200 days) may be missing indicators
- All recent data (2023-2025) should have indicators

---

## PRIORITY 3: Export & Document

### ✅ Step 6: Export sample data with indicators
```bash
bq query --project_id=aialgotradehits --use_legacy_sql=false --format=csv --max_rows=1000 "
SELECT *
FROM \`aialgotradehits.crypto_trading_data.stocks_daily_clean\`
WHERE symbol IN ('AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA')
  AND DATE(datetime) >= '2025-11-01'
ORDER BY symbol, datetime DESC
LIMIT 1000
" > C:\\1AITrading\\Trading\\stocks_daily_clean_WITH_INDICATORS_sample_1000.csv
```

### ✅ Step 7: Create completion summary document
- Total time taken
- Success/failure stats
- Validation results
- Sample queries demonstrating indicators
- Next steps

---

## PRIORITY 4: Recovery Actions (If Needed)

### If Process Failed or Incomplete:

**Option A: Resume failed symbols**
```bash
# Modify calculate_all_indicators.py to skip completed symbols
python calculate_all_indicators.py
```

**Option B: Recalculate specific symbols**
```python
# Edit script to only process specific symbols
symbols = ['SYMBOL1', 'SYMBOL2', ...]
```

**Option C: Start fresh (if major issues)**
```bash
# Clear all indicators and restart
# (only if absolutely necessary)
```

---

## PRIORITY 5: Next Steps

### Immediate Next Steps (Today):
1. ✅ Validate all indicators working correctly
2. ✅ Test sample queries
3. ✅ Update API endpoints to use stocks_daily_clean
4. ✅ Update frontend dashboard to display indicators
5. ✅ Create indicator-based alert system

### Phase 3 Planning (This Week):
1. **Expand Symbol Coverage:**
   - Add Russell 2000 small-cap stocks (~2000 symbols)
   - Add liquid ETFs (SPY, QQQ, IWM, etc. ~100 ETFs)
   - Complete S&P 500 coverage (~350 more symbols)

2. **Automated Daily Updates:**
   - Create Cloud Function to fetch daily data
   - Calculate indicators for new data automatically
   - Schedule to run after market close

3. **API Enhancement:**
   - Add indicator-based screening endpoints
   - Add technical pattern detection
   - Add backtesting endpoints

### Phase 4 Planning (Next Week):
1. **ML Model Training:**
   - Use 27 years of data with indicators
   - Train price prediction models
   - Train trend classification models

2. **Trading Signal Generation:**
   - Implement signal strategies using indicators
   - Backtest against historical data
   - Deploy signal alerts

3. **Advanced Analytics:**
   - Correlation analysis across indicators
   - Sector rotation strategies
   - Risk management tools

---

## TROUBLESHOOTING GUIDE

### Issue 1: Process crashed or stopped
**Solution:** Run `python resume_if_failed.py` to identify which symbols need processing

### Issue 2: Indicators look incorrect
**Solution:** Check a few symbols manually, verify calculation logic in script

### Issue 3: Some symbols missing indicators
**Solution:** Normal for early data points (< 200 days), verify recent data has indicators

### Issue 4: BigQuery errors
**Solution:** Check quotas, verify table permissions, restart client connection

### Issue 5: pandas_ta errors
**Solution:** Check column naming issues (Bollinger Bands), add error handling

---

## QUICK REFERENCE

### Key Files:
- **Main table:** `aialgotradehits.crypto_trading_data.stocks_daily_clean`
- **Log file:** `C:\1AITrading\Trading\indicator_calculation.log`
- **State doc:** `C:\1AITrading\Trading\OVERNIGHT_RUN_STATE.md`
- **Recovery script:** `C:\1AITrading\Trading\resume_if_failed.py`

### Key Metrics:
- **Total Rows:** 1,141,844
- **Symbols:** 262
- **Date Range:** 1998-2025 (27 years)
- **Indicator Fields:** 58
- **Total Fields:** 85

### Process Info:
- **Started:** December 9, 2025 @ 12:18 AM EST
- **Expected Complete:** ~2:00 AM EST
- **Duration:** ~1.5-2 hours
- **Process ID:** 38080e

---

## SUCCESS CRITERIA

Process is successful if:
- ✅ All 262 symbols processed
- ✅ >99% of rows have RSI indicator
- ✅ >99% of rows have MACD indicator
- ✅ >99% of rows have SMA200 indicator
- ✅ Recent data (2023-2025) 100% complete
- ✅ Sample queries return expected results
- ✅ No major errors in log file

---

**START HERE AT 8:00 AM:** Run Step 1 to check completion status!

---

**END OF MORNING TODO LIST**
