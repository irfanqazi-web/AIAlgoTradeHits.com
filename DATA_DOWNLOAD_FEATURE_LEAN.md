# DATA DOWNLOAD FEATURE - LEAN VERSION (ML Training Focus)

**For:** Irfan Saheb
**From:** Saleem Ahmad / AI Trading System Team  
**Date:** December 11, 2025
**Priority:** High - ML Training Enabler
**Version:** 1.0 LEAN

---

## PURPOSE

Build a simple data download interface focused on ML training needs:
- Download 5+ years of daily data for multiple stocks
- Select specific indicators (avoid downloading unnecessary data)
- Export as CSV for ML model training
- Protect system with download limits

**Phase 1 Scope:** Desktop UI, CSV export, daily data only

---

## USER FLOW (4 STEPS)

```
┌─────────────────────────────────────────────┐
│  STEP 1: Select Stocks                      │
│  • Search: Type symbol (SPY, QQQ, AAPL)    │
│  • Or choose: S&P 500 / Nasdaq 100 lists   │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│  STEP 2: Select Date Range                  │
│  • Calendar picker OR                       │
│  • Quick buttons: [Last Year] [Last 5 Years]│
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│  STEP 3: Select Indicators                  │
│  • OHLCV (always included)                  │
│  • Check boxes for 64 indicators (grouped)  │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│  STEP 4: Download                           │
│  • Preview summary                          │
│  • Download CSV button                      │
└─────────────────────────────────────────────┘
```

---

## STEP 1: SELECT STOCKS

### Interface
```
┌──────────────────────────────────────┐
│  Search for stocks:                  │
│  [____________] 🔍                   │
│                                       │
│  Or choose a list:                   │
│  [ ] S&P 500 (500 stocks)           │
│  [ ] Nasdaq 100 (100 stocks)        │
│  [ ] Dow Jones 30 (30 stocks)       │
│  [ ] Crypto Top 50 (50 coins)       │
│                                       │
│  Selected (5):                       │
│  [SPY ✕] [QQQ ✕] [AAPL ✕]          │
│  [MSFT ✕] [GOOGL ✕]                │
│                                       │
│  5 of 10 symbols allowed             │
│  [Clear All] [Next Step →]          │
└──────────────────────────────────────┘
```

### Features
- Search with auto-complete (shows symbol + company name)
- Click to add, click X to remove
- Show count: "5 of 10 allowed" (based on user tier)
- Predefined lists for quick selection

### Backend
```python
# Symbol search
GET /api/symbols/search?q=apple
Response: [
    {"symbol": "AAPL", "name": "Apple Inc.", "type": "stock"},
    {"symbol": "APLE", "name": "Apple Hospitality", "type": "stock"}
]

# Predefined lists stored in database
predefined_lists = {
    'sp500': ['AAPL', 'MSFT', 'GOOGL', ...],  # 500 symbols
    'nasdaq100': ['AAPL', 'MSFT', 'TSLA', ...],  # 100 symbols
    'dow30': ['AAPL', 'MSFT', 'JPM', ...],  # 30 symbols
}
```

---

## STEP 2: SELECT DATE RANGE

### Interface
```
┌──────────────────────────────────────┐
│  Select Date Range:                  │
│                                       │
│  Start Date: [📅 2020-01-01]        │
│  End Date:   [📅 2025-12-11]        │
│                                       │
│  Or use quick select:                │
│  [Last Month] [Last Year]            │
│  [Last 2 Years] [Last 5 Years]       │
│                                       │
│  Range: 5 years, 345 days            │
│  Timeframe: Daily only (Phase 1)     │
│                                       │
│  [← Back] [Next Step →]             │
└──────────────────────────────────────┘
```

### Quick Select Logic
```python
def get_date_range(quick_select):
    today = datetime.now()
    
    ranges = {
        'last_month': timedelta(days=30),
        'last_year': timedelta(days=365),
        'last_2_years': timedelta(days=730),
        'last_5_years': timedelta(days=1825)
    }
    
    start = today - ranges[quick_select]
    return start.date(), today.date()
```

### Validation
- Start date < End date
- Cannot select future dates
- Show warning if date range exceeds user limits

---

## STEP 3: SELECT INDICATORS

### Interface
```
┌──────────────────────────────────────────────┐
│  Select Data Columns                         │
├──────────────────────────────────────────────┤
│  ☑ OHLCV Data (Always Included)             │
│    datetime, open, high, low, close, volume  │
├──────────────────────────────────────────────┤
│  Select Indicators:                          │
│                                               │
│  [Select All] [Deselect All]                 │
│                                               │
│  Momentum (9):                               │
│  ☐ RSI        ☐ MACD       ☐ Stochastic     │
│  ☐ CCI        ☐ Williams %R ☐ Momentum      │
│                                               │
│  Moving Averages (9):                        │
│  ☐ SMA 20     ☐ SMA 50     ☐ SMA 200        │
│  ☐ EMA 12     ☐ EMA 20     ☐ EMA 26         │
│  ☐ EMA 50     ☐ EMA 200    ☐ KAMA           │
│                                               │
│  Trend & Volatility (10):                    │
│  ☐ Bollinger Bands (3)  ☐ BB Width           │
│  ☐ ADX        ☐ +DI       ☐ -DI              │
│  ☐ ATR        ☐ TRIX      ☐ Ultimate Osc    │
│                                               │
│  Volume (3):                                  │
│  ☐ OBV        ☐ PVO       ☐ PPO              │
│                                               │
│  Institutional (13):                          │
│  ☐ VWAP Daily    ☐ VWAP Weekly               │
│  ☐ Volume Profile (POC, VAH, VAL)            │
│  ☐ MFI        ☐ CMF       ☐ ROC              │
│  ☐ Ichimoku (5 components)                   │
│                                               │
│  ML Features (22):                            │
│  ☐ Returns (log, 2w, 4w)                     │
│  ☐ Relative Positions (vs SMAs)              │
│  ☐ Slopes & Z-scores                         │
│  ☐ Regime Detection                          │
│                                               │
│  Selected: 6 OHLCV + 15 indicators = 21 cols │
│                                               │
│  [← Back] [Next Step →]                     │
└──────────────────────────────────────────────┘
```

### Indicator Groups Data Structure
```python
INDICATORS = {
    'momentum': {
        'name': 'Momentum',
        'count': 9,
        'fields': ['rsi', 'macd', 'macd_signal', 'macd_histogram', 
                   'stoch_k', 'stoch_d', 'cci', 'williams_r', 'momentum']
    },
    'moving_averages': {
        'name': 'Moving Averages',
        'count': 9,
        'fields': ['sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_20', 
                   'ema_26', 'ema_50', 'ema_200', 'kama']
    },
    'trend_volatility': {
        'name': 'Trend & Volatility',
        'count': 10,
        'fields': ['bollinger_upper', 'bollinger_middle', 'bollinger_lower', 
                   'bb_width', 'adx', 'plus_di', 'minus_di', 'atr', 
                   'trix', 'ultimate_osc']
    },
    'volume': {
        'name': 'Volume',
        'count': 3,
        'fields': ['obv', 'pvo', 'ppo']
    },
    'institutional': {
        'name': 'Institutional (NEW)',
        'count': 13,
        'fields': ['vwap_daily', 'vwap_weekly', 'volume_profile_poc', 
                   'volume_profile_vah', 'volume_profile_val', 'mfi', 'cmf', 
                   'roc', 'ichimoku_tenkan', 'ichimoku_kijun', 
                   'ichimoku_senkou_a', 'ichimoku_senkou_b', 'ichimoku_chikou']
    },
    'ml_features': {
        'name': 'ML Features',
        'count': 22,
        'fields': ['log_return', 'return_2w', 'return_4w', 
                   'close_vs_sma20_pct', 'close_vs_sma50_pct', 
                   'close_vs_sma200_pct', 'rsi_slope', 'rsi_zscore', 
                   'ema20_slope', 'ema50_slope', 'atr_zscore', 'atr_slope',
                   'volume_zscore', 'volume_ratio', 'pivot_high_flag',
                   'pivot_low_flag', 'dist_to_pivot_high', 'dist_to_pivot_low',
                   'trend_regime', 'vol_regime', 'regime_confidence', 'macd_cross']
    }
}
```

---

## STEP 4: DOWNLOAD

### Summary & Preview
```
┌──────────────────────────────────────────────┐
│  Download Summary                            │
├──────────────────────────────────────────────┤
│  Symbols:    5 (SPY, QQQ, AAPL, MSFT, GOOGL)│
│  Date Range: 2020-01-01 to 2025-12-11       │
│              (5 years, 345 days)             │
│  Timeframe:  Daily                           │
│  Columns:    27 (6 OHLCV + 21 indicators)   │
│                                               │
│  Estimated:                                   │
│    Rows:     6,300                           │
│    Size:     2.8 MB (CSV) / 1.9 MB (Excel)  │
│    Time:     ~15 seconds                     │
└──────────────────────────────────────────────┘

Preview: First 10 rows of SPY
┌────────────┬────────┬────────┬────────┬───────┬────────┐
│ datetime   │ close  │ rsi    │ macd   │ sma_20│ volume │
├────────────┼────────┼────────┼────────┼───────┼────────┤
│ 2020-01-02 │ 324.87 │ 65.23  │ 2.45   │ 320.5 │ 89329K │
│ 2020-01-03 │ 324.34 │ 64.87  │ 2.38   │ 321.2 │ 80235K │
│ ...        │ ...    │ ...    │ ...    │ ...   │ ...    │
└────────────┴────────┴────────┴────────┴───────┴────────┘

Select File Format:
○ CSV (2.8 MB) - Single file, all symbols
● Excel (1.9 MB) - Separate sheet per symbol

File Name: download_2025-12-11_5symbols_daily.xlsx

[← Back] [🔽 DOWNLOAD]
```

### Download Process
```
After clicking Download:

1. Show progress indicator:
   [████████████░░░] 75%
   Processing: SPY (3 of 5 symbols)
   Estimated time: 5 seconds

2. Generate CSV file

3. Start browser download automatically
```

---

## DOWNLOAD LIMITS

### User Tiers

**Regular User (Free):**
- Max 10 symbols per download
- Max 2 years date range
- Daily data only
- 5 downloads per hour

**Power User (Paid):**
- Max 100 symbols per download
- Max 5 years date range
- All timeframes (future: 1-min, hourly, etc.)
- 20 downloads per hour

**Admin (Unlimited):**
- No limits

### Enforcement
```python
def check_limits(user, request):
    limits = get_user_limits(user.tier)
    
    # Check symbol count
    if len(request.symbols) > limits.max_symbols:
        return False, f"Limit: {limits.max_symbols} symbols max"
    
    # Check date range
    days = (request.end_date - request.start_date).days
    if days > limits.max_days:
        return False, f"Limit: {limits.max_days} days max"
    
    # Check rate limit
    recent = count_recent_downloads(user.id, hours=1)
    if recent >= limits.hourly_limit:
        return False, f"Rate limit: {limits.hourly_limit}/hour"
    
    return True, "OK"
```

### Display Limits to User
```
❌ Download Blocked

Reason: Too many symbols
Your Tier: Regular User
Requested: 15 symbols
Allowed: 10 symbols

Options:
- Reduce to 10 symbols
- [Upgrade to Power User] (100 symbols)
```

---

## BACKEND IMPLEMENTATION

### Database Query
```python
def generate_download(symbols, start_date, end_date, columns):
    """
    Query database and return CSV data
    """
    # Build column list
    all_columns = ['datetime', 'symbol'] + columns
    
    # Build SQL query
    query = f"""
        SELECT {', '.join(all_columns)}
        FROM stocks_daily_clean
        WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
          AND datetime >= '{start_date}'
          AND datetime <= '{end_date}'
        ORDER BY symbol, datetime
    """
    
    # Execute query
    results = db.execute(query)
    
    return results
```

### CSV Generation
```python
def create_csv_file(data, filename):
    """
    Convert query results to CSV file
    """
    import pandas as pd
    
    df = pd.DataFrame(data)
    
    # Save to temp location
    output_path = f'/tmp/downloads/{filename}'
    df.to_csv(output_path, index=False)
    
    return output_path
```

### Excel Generation
```python
def create_excel_file(data, symbols, filename):
    """
    Convert query results to Excel file with one sheet per symbol
    """
    import pandas as pd
    
    output_path = f'/tmp/downloads/{filename}'
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for symbol in symbols:
            # Filter data for this symbol
            symbol_data = [row for row in data if row['symbol'] == symbol]
            df = pd.DataFrame(symbol_data)
            
            # Remove symbol column (redundant in separate sheets)
            df = df.drop('symbol', axis=1)
            
            # Write to sheet named after symbol
            df.to_excel(writer, sheet_name=symbol, index=False)
    
    return output_path
```

### File Delivery
```python
from flask import send_file

@app.route('/api/download', methods=['POST'])
def download_data():
    # Get request parameters
    symbols = request.json['symbols']
    start_date = request.json['start_date']
    end_date = request.json['end_date']
    columns = request.json['columns']
    file_format = request.json.get('format', 'csv')  # 'csv' or 'excel'
    
    # Check limits
    allowed, message = check_limits(current_user, request.json)
    if not allowed:
        return {'error': message}, 403
    
    # Generate data
    data = generate_download(symbols, start_date, end_date, columns)
    
    # Create file based on format
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if file_format == 'excel':
        filename = f"download_{timestamp}.xlsx"
        filepath = create_excel_file(data, symbols, filename)
    else:  # csv
        filename = f"download_{timestamp}.csv"
        filepath = create_csv_file(data, filename)
    
    # Send file to user
    return send_file(filepath, as_attachment=True, download_name=filename)
```

---

## ERROR HANDLING

### Invalid Symbols
```
❌ Error: Invalid Symbols

The following symbols were not found:
- INVALIDX
- TESTXYZ

Please check spelling or remove these symbols.
```

### No Data Available
```
⚠️ Warning: Incomplete Data

AAPL: 98.2% complete (1,237 of 1,260 days)
Missing 23 days between 2020-2025

Continue with available data? [Yes] [No]
```

### File Too Large
```
⚠️ Large Download Warning

Estimated file size: 450 MB
Generation time: 5-10 minutes

Recommendations:
- Select fewer symbols
- Reduce date range
- Select fewer indicators

[Continue Anyway] [Go Back]
```

---

## ADMIN CONTROLS

### Limits Configuration Panel
```
┌──────────────────────────────────────────────┐
│  Download Limits Configuration               │
├──────────────────────────────────────────────┤
│  Regular User:                               │
│    Max Symbols: [10        ]                 │
│    Max Days:    [730       ] (2 years)       │
│    Hourly Limit:[5         ]                 │
│                                               │
│  Power User:                                  │
│    Max Symbols: [100       ]                 │
│    Max Days:    [1825      ] (5 years)       │
│    Hourly Limit:[20        ]                 │
│                                               │
│  [Save Changes]                              │
└──────────────────────────────────────────────┘
```

### Usage Monitoring
```
Download Activity (Last 24 Hours):

User Tier    | Downloads | Avg Size | Total Data
-------------|-----------|----------|------------
Regular      | 145       | 2.1 MB   | 304.5 MB
Power        | 23        | 15.3 MB  | 351.9 MB
Admin        | 5         | 128.7 MB | 643.5 MB

Top Users:
1. saleem@ai.com - 12 downloads (24.5 MB)
2. irfan@ai.com - 8 downloads (18.2 MB)
```

---

## TESTING CHECKLIST

Before deployment:

**Functional Tests:**
- [ ] Single symbol download works
- [ ] Multiple symbols download works
- [ ] Date range selection works
- [ ] Indicator selection works
- [ ] CSV file downloads correctly
- [ ] Excel file downloads correctly
- [ ] Excel has separate sheet per symbol
- [ ] Preview shows accurate data

**Limit Tests:**
- [ ] Regular user blocked at 11 symbols
- [ ] Regular user blocked at 3 years
- [ ] Rate limiting works (6th download blocked)
- [ ] Power user can download 100 symbols
- [ ] Admin has no restrictions

**Edge Cases:**
- [ ] Invalid symbols handled
- [ ] Empty date ranges rejected
- [ ] Future dates rejected
- [ ] All indicators selected works
- [ ] No indicators selected (OHLCV only) works

**Performance:**
- [ ] 10 symbols, 5 years: < 30 seconds
- [ ] 100 symbols, 2 years: < 2 minutes
- [ ] Preview loads < 3 seconds

---

## DEPLOYMENT TIMELINE

### Week 1: Core UI
- [ ] Step 1: Symbol selection interface
- [ ] Step 2: Date range picker
- [ ] Step 3: Indicator checkboxes
- [ ] Step 4: Summary & download button

### Week 2: Backend & Integration
- [ ] Database query builder
- [ ] CSV generation
- [ ] Download limits enforcement
- [ ] Admin controls panel

### Week 3: Testing & Polish
- [ ] Functional testing
- [ ] Limit testing
- [ ] Error handling
- [ ] UI polish

**Total: 3 weeks for complete feature**

---

## SUCCESS METRICS

Track after deployment:

1. **Adoption:** % of users who download data
   - Target: 30% within first month

2. **Most Popular:**
   - Which symbols downloaded most?
   - Which indicators selected most?
   - Common date ranges?

3. **Performance:**
   - Average download time
   - Target: < 30 seconds for typical download

4. **Upgrade Conversion:**
   - % of users who upgrade after hitting limits
   - Target: 5% conversion

---

## FUTURE ENHANCEMENTS (Phase 2+)

**After Phase 1 is working:**

1. **Intraday Data** (1-min, 5-min, hourly)
2. **Download History** (repeat previous downloads)
3. **ML-Ready Format** (train/val/test split) - **OPTION B**
4. **Smart Presets** (Day Trading Pack, etc.)
5. **Bulk CSV Upload** (upload list of 100 symbols)
6. **API Access** (programmatic downloads)
7. **Mobile Support**

---

## QUESTIONS FOR SALEEM

Before implementation:

1. **Pricing:** What should Power User tier cost?
2. **Priority:** Deploy before or after indicator corrections?
   - **Recommendation:** After corrections (users get accurate data)
3. **Storage:** Where to save CSV files temporarily?

---

## SUMMARY

**Phase 1 delivers:**
✓ Simple 4-step wizard
✓ CSV & Excel export of daily data
✓ Excel: Separate sheet per symbol
✓ Multiple stocks & indicators
✓ Download limits to protect system
✓ Perfect for ML training & trader analysis

**Estimated: 3 weeks implementation**

**Deploy after indicator corrections are complete.**

---

**Ready for Irfan to begin once indicator work is done!**
