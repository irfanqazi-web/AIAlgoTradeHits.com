# Overnight Indicator Calculation - State Documentation

**Started:** December 9, 2025 @ 12:18 AM EST
**Process ID:** 38080e (background bash process)
**Estimated Completion:** 1.5-2 hours (by ~2:00 AM EST)

---

## WHAT'S RUNNING

### Process Details:
- **Script:** `C:\1AITrading\Trading\calculate_all_indicators.py`
- **Command:** `python calculate_all_indicators.py 2>&1 | tee indicator_calculation.log`
- **Log File:** `C:\1AITrading\Trading\indicator_calculation.log`
- **Background Process:** YES (can check with bash_id: 38080e)

### Task:
Calculating 58 technical indicator fields for ALL data in `stocks_daily_clean` table:
- **Total Rows:** 1,141,844
- **Symbols:** 262
- **Date Range:** 1998-2025 (27 years)

---

## TABLE INFORMATION

### BigQuery Table:
**Project:** aialgotradehits
**Dataset:** crypto_trading_data
**Table:** stocks_daily_clean

### Current Schema (85 fields):
- **✅ Populated (27 fields):** datetime, symbol, OHLCV, basic calcs, metadata
- **⏳ Calculating (58 fields):** All technical indicators and ML features

### Table Configuration:
- **Partitioning:** MONTH (not DAY - we have 27 years)
- **Clustering:** symbol, sector, exchange
- **Total Rows:** 1,141,844
- **Symbols:** 262 (NASDAQ & NYSE only)

---

## INDICATOR FIELDS BEING CALCULATED

### Momentum Indicators (9):
- rsi, macd, macd_signal, macd_histogram
- stoch_k, stoch_d, cci, williams_r, momentum

### Moving Averages (9):
- sma_20, sma_50, sma_200
- ema_12, ema_20, ema_26, ema_50, ema_200, kama

### Trend & Volatility (10):
- bollinger_upper, bollinger_middle, bollinger_lower, bb_width
- adx, plus_di, minus_di, atr, trix, roc

### Volume Indicators (3):
- obv, pvo, ppo

### Advanced Oscillators (2):
- ultimate_osc, awesome_osc

### ML Features - Returns (3):
- log_return, return_2w, return_4w

### ML Features - Relative Positions (3):
- close_vs_sma20_pct, close_vs_sma50_pct, close_vs_sma200_pct

### ML Features - Indicator Dynamics (11):
- rsi_slope, rsi_zscore, rsi_overbought, rsi_oversold, macd_cross
- ema20_slope, ema50_slope, atr_zscore, atr_slope
- volume_zscore, volume_ratio

### ML Features - Market Structure (4):
- pivot_high_flag, pivot_low_flag
- dist_to_pivot_high, dist_to_pivot_low

### ML Features - Regime Detection (3):
- trend_regime, vol_regime, regime_confidence

**Total: 58 fields**

---

## HOW IT WORKS

### Processing Strategy:
1. **Fetch all symbols** from table (262 symbols)
2. **Process each symbol sequentially:**
   - Fetch all historical data for symbol
   - Calculate all 58 indicators using pandas_ta
   - Create temp table with calculated data
   - MERGE back to main table (UPDATE)
   - Drop temp table
3. **Progress tracking:** Prints "[X/262] SYMBOL - OK (rows, time)"
4. **Error handling:** Continues on error, logs failed symbols
5. **Final validation:** Counts rows with indicators

### Estimated Performance:
- **Per Symbol:** 20-30 seconds average
- **Total Time:** 262 symbols × 25s = 1.5-2 hours
- **Peak:** ~2:00 AM EST completion

---

## HOW TO CHECK PROGRESS

### Method 1: Check Log File
```bash
tail -20 C:\1AITrading\Trading\indicator_calculation.log
```

### Method 2: Check Background Process (if using Claude Code)
```
Use BashOutput tool with bash_id: 38080e
```

### Method 3: Query BigQuery
```sql
SELECT
    COUNT(*) as total_rows,
    COUNTIF(rsi IS NOT NULL) as rows_with_rsi,
    COUNTIF(macd IS NOT NULL) as rows_with_macd,
    COUNTIF(rsi IS NOT NULL) * 100.0 / COUNT(*) as pct_complete
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
```

### Method 4: Check Process (Windows)
```bash
tasklist | findstr python
```

---

## IF PROCESS FAILS/CRASHES

### Recovery Steps:

1. **Check what completed:**
```sql
SELECT
    symbol,
    COUNT(*) as total_rows,
    COUNTIF(rsi IS NOT NULL) as rows_with_indicators
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
GROUP BY symbol
HAVING rows_with_indicators > 0
ORDER BY symbol
```

2. **Get list of symbols that failed:**
```sql
SELECT DISTINCT symbol
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE rsi IS NULL
ORDER BY symbol
```

3. **Resume from failed symbols:**
   - Edit `calculate_all_indicators.py`
   - Modify line to skip completed symbols:
   ```python
   # Add after getting symbols list:
   completed_query = """
   SELECT DISTINCT symbol
   FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
   WHERE rsi IS NOT NULL
   """
   completed = [row.symbol for row in client.query(completed_query).result()]
   symbols = [s for s in symbols if s not in completed]
   ```
   - Re-run: `python calculate_all_indicators.py`

---

## EXPECTED OUTPUT

### Success Indicators:
```
[1/262] AAPL     - OK (5,010 rows, 25.3s) | Elapsed: 0.4m | ETA: 109.1m
[2/262] ABBV     - OK (4,852 rows, 23.8s) | Elapsed: 0.8m | ETA: 108.3m
...
[262/262] ZTS    - OK (3,421 rows, 18.2s) | Elapsed: 112.5m | ETA: 0.0m

====================================================================================================
CALCULATION COMPLETE!
====================================================================================================
Finished: 2025-12-09 02:10:32
Total time: 112.5 minutes
Processed: 262/262 symbols
Failed: 0 symbols

Validating results...
Total rows: 1,141,844
Symbols: 262
Rows with RSI: 1,139,234 (99.8%)
Rows with MACD: 1,138,892 (99.7%)
Rows with SMA200: 1,135,678 (99.5%)
Rows with Bollinger: 1,138,445 (99.7%)
====================================================================================================
ALL DONE!
```

---

## VALIDATION QUERIES (FOR MORNING)

### 1. Check Overall Completion
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

### 2. Check Sample Data (AAPL latest)
```sql
SELECT
    datetime, symbol, close,
    rsi, macd, sma_50, sma_200,
    bollinger_upper, bollinger_lower,
    trend_regime, vol_regime
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE symbol = 'AAPL'
ORDER BY datetime DESC
LIMIT 10;
```

### 3. Find Any Missing Indicators
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

---

## FILES CREATED

1. `calculate_all_indicators.py` - Main calculation script
2. `indicator_calculation.log` - Real-time progress log
3. `OVERNIGHT_RUN_STATE.md` - This state documentation
4. `MIGRATION_COMPLETE_SUMMARY.md` - Migration summary
5. `STOCK_MIGRATION_SUMMARY.md` - Pre-migration plan
6. `stocks_daily_clean_sample_1000.csv` - Sample data (before indicators)

---

## MORNING CHECKLIST

### When You Wake Up:

✅ **1. Check if process completed**
```bash
tail -50 C:\1AITrading\Trading\indicator_calculation.log
```
Look for: "ALL DONE!" message

✅ **2. Validate indicators in BigQuery**
Run validation queries above

✅ **3. Sample a few stocks**
Check AAPL, MSFT, GOOGL have indicators

✅ **4. If failed:**
- Check which symbols completed
- Identify failed symbols
- Resume with recovery script

✅ **5. If successful:**
- Export new sample with indicators
- Update frontend to use new table
- Celebrate! 🎉

---

## CONFIGURATION SUMMARY

### GCP Project:
- **Project ID:** aialgotradehits
- **Region:** us-central1
- **Service Account:** Default

### Python Environment:
- **Python:** 3.13
- **Key Libraries:** pandas, pandas_ta, google-cloud-bigquery, numpy
- **Location:** C:\Users\irfan\AppData\Local\Programs\Python\Python313

### Data Sources (Consolidated From):
1. v2_stocks_daily (106 symbols, 2023-2025)
2. stocks_unified_daily (316 symbols, 1998-2025)
3. v2_stocks_historical_daily (302 symbols, 1998-2025)

### Exchange Filters Applied:
- ✅ NASDAQ: XNAS, XNGS, XNCM, XNMS
- ✅ NYSE: XNYS, ARCX, XASE
- ✅ CBOE: BATS, CBOE, XCBO
- ❌ OTC: Rejected (PINX, PSGM, OTCB, etc.)
- ❌ Pink Sheets: Rejected

---

## CONTACT/RESUME INFO

### If You Need to Resume This Session:
- **Working Directory:** C:\1AITrading\Trading
- **Main Table:** aialgotradehits.crypto_trading_data.stocks_daily_clean
- **Process Log:** indicator_calculation.log
- **State File:** OVERNIGHT_RUN_STATE.md (this file)

### Key Context:
- Consolidated 3 source tables → 1 clean table
- 1.14M rows, 262 symbols, 27 years (1998-2025)
- 85-field schema (27 populated, 58 calculating overnight)
- MONTH partitioning, clustered by symbol/sector/exchange

---

**GOOD NIGHT! Check status in the morning.**

**Expected completion:** ~2:00 AM EST
**Check first thing:** `tail -50 indicator_calculation.log`

---

**END OF STATE DOCUMENTATION**
