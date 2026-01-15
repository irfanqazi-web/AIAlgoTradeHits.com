# INDICATOR VALIDATION SCRIPT - USAGE GUIDE

## What It Does
Automatically validates all 64 indicators by:
1. Recalculating them using pandas_ta library
2. Comparing against your database values
3. Reporting matches/mismatches with specific percentages

## Installation

```bash
# Install required library
pip install pandas_ta openpyxl
```

## How to Run

### Basic Usage:
```bash
python validate_indicators.py <your_file.xlsx>
```

### Examples:
```bash
# Validate SPY data
python validate_indicators.py SPY_97_fields_complete.xlsx

# Validate QQQ data
python validate_indicators.py QQQ_97_fields_complete.xlsx

# Validate any symbol
python validate_indicators.py AAPL_data.xlsx
```

## What You'll See

### Output Example:
```
================================================================================
INDICATOR VALIDATION SCRIPT
================================================================================

File: SPY_97_fields_complete.xlsx
Validation samples: 100
Tolerance: 0.1%

Symbol: SPY
Total rows: 5000
Date range: 2006-01-27 to 2025-12-10

Starting validation...
1. Validating RSI...
2. Validating MACD...
3. Validating Moving Averages...
...

VALIDATION RESULTS
================================================================================

Total Indicators Tested: 24
✓ Passed: 11
✗ Failed: 13
Success Rate: 45.8%

DETAILED RESULTS:
--------------------------------------------------------------------------------
Indicator                 Tested     Match      MaxDiff%     Status    
--------------------------------------------------------------------------------
RSI                       100        0          42.069       ✗ FAIL      
MACD                      100        100        0.000        ✓ PASS      
MFI (NEW)                 100        100        0.000        ✓ PASS      
CMF (NEW)                 100        100        0.000        ✓ PASS      
...
```

## Interpreting Results

### ✓ PASS = Perfect Match
- Indicator calculated correctly
- Database value matches pandas_ta within 0.1%
- No action needed

### ✗ FAIL = Mismatch
- Database calculation differs from standard
- Could be:
  1. **Different parameters** (e.g., RSI-14 vs RSI-20)
  2. **Different formula** (e.g., Wilder's smoothing vs EMA)
  3. **Bug in calculation**
  4. **Data issue** (missing values causing offset)

## What the Results Mean

### Good News (✓ PASS):
- **MACD**: 100% match - calculated correctly
- **All SMAs/EMAs**: Perfect - moving averages correct
- **MFI, CMF (NEW)**: Perfect - new indicators working!

### Issues Found (✗ FAIL):
- **RSI**: 42% difference - likely different parameters or Wilder's vs EMA smoothing
- **ADX/DI**: Large differences - different smoothing method
- **Stochastic**: Different parameters (%K period)
- **ROC**: Wrong period (using 10 vs different period)
- **Ichimoku**: Small differences - timing/shifting issue

## Next Steps After Running

### If Many Failures:
1. **Check indicator parameters** - Compare your settings vs pandas_ta defaults
2. **Review calculation method** - Some indicators have multiple valid formulas
3. **Check with Irfan** - Ask which library/formula he used

### If Few Failures:
1. **Document the differences** - Note which indicators use custom parameters
2. **Decide if acceptable** - Some differences are intentional (custom periods)
3. **Update validation script** - Adjust parameters to match your implementation

## Key Findings from Your SPY Test

### ✓ Working Perfectly (11/24):
- MACD, All SMAs, Most EMAs
- **MFI (NEW)** ✓
- **CMF (NEW)** ✓
- Bollinger Middle

### ⚠️ Need Investigation (13/24):
- RSI (different smoothing method)
- ADX/+DI/-DI (Wilder's smoothing)
- Stochastic (different %K/%D periods)
- ROC (different period)
- ATR (smoothing method)
- Ichimoku (shift timing)
- Bollinger Bands (different std calculation)

## Customizing the Script

### Change Sample Size:
```python
# In the script, line 349:
results = validate_indicators(file_path, num_samples=100)  # Test 100 rows

# Change to test more:
results = validate_indicators(file_path, num_samples=500)  # Test 500 rows
```

### Change Tolerance:
```python
# In the script, line 11:
TOLERANCE_PCT = 0.1  # 0.1% tolerance

# Change to be more lenient:
TOLERANCE_PCT = 1.0  # 1% tolerance
```

### Add More Indicators:
Follow the pattern in the script:
```python
# Example: Add CCI validation
if 'cci' in df.columns:
    df['cci_calc'] = ta.cci(df['high'], df['low'], df['close'], length=20)
    result = compare_indicator(df, 'cci', 'cci_calc', sample_indices)
    # Add to results...
```

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'pandas_ta'"
**Solution:** `pip install pandas_ta`

### Issue: "File not found"
**Solution:** Make sure you're in the same directory as the Excel file, or use full path

### Issue: "Most indicators failing"
**Solution:** This is NORMAL if your implementation uses different parameters than pandas_ta defaults. Document the differences.

### Issue: "Script takes too long"
**Solution:** Reduce sample size: `num_samples=50` instead of 100

## What to Tell Irfan

"Run this validation script on your indicator calculations. It will show:
1. Which indicators match standard libraries (pandas_ta)
2. Which use custom parameters or formulas
3. Where bugs might exist

It's NOT a failure if indicators don't match 100% - just means we're using different parameters. But we should DOCUMENT those differences."

## Output Files

The script generates:
- **Console output**: Immediate results you see on screen
- **Excel file**: `<filename>_validation_results.xlsx` with detailed comparison

## Bottom Line

**This script is a diagnostic tool, not a pass/fail test.**

Some differences are expected and intentional:
- Custom RSI periods
- Different ADX smoothing
- Custom Ichimoku parameters

The goal is to:
1. ✓ Confirm indicators are calculated (not NULL)
2. ✓ Identify systematic errors (all values wrong)
3. ✓ Document intentional differences
4. ✓ Find and fix bugs

**Your results show indicators ARE being calculated - now document which use custom parameters.**
