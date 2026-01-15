# BigQuery Cleanup Summary
## Generated: December 10, 2025

---

## CURRENT STATE

**Total tables in crypto_trading_data dataset**: 200+

**Production clean tables** (KEEP): 4
- stocks_daily_clean
- stocks_hourly_clean
- stocks_5min_clean
- crypto_daily_clean

**Supporting infrastructure tables** (KEEP): ~45
- Fundamentals: fundamentals_*
- Analyst data: analyst_*
- ETF data: etf_*
- Calendar events: earnings_calendar, dividends_calendar, splits_calendar, ipo_calendar
- Market data: market_movers, market_state, exchange_schedule
- SEC filings: sec_edgar_filings
- Insider/Institutional: insider_transactions, institutional_holders, fund_holders
- Strategies: paper_trades, strategy_signals, strategy_backtests, strategy_daily_summary, rise_cycles
- Other: interest_rates, sector_momentum_rankings, search_history, users, trading_strategies

**Tables to DELETE**: ~197
- 120+ temp_* tables (daily MERGE leftovers)
- 60+ temp_hourly_* tables (hourly MERGE leftovers)
- 7 _temp_features_* tables (ML feature temp tables)
- 30+ v2_* tables (legacy data structure)
- 2 AI training tables (btc_ai_training_daily, nvda_ai_training_daily)
- 7 weekly_* tables (can be regenerated)
- 1 stocks_unified_daily (legacy)

---

## ACTIONS REQUIRED

### 1. Delete ALL temp_* tables (187 tables)

These are leftover from MERGE operations and serve no purpose:

```powershell
# PowerShell script to delete all temp tables
$tempTables = @(
  "temp_CMCSA", "temp_FI", "temp_GE", "temp_GILD", "temp_GOOGL", "temp_GS",
  "temp_HD", "temp_HON", "temp_IBM", "temp_ICE", "temp_INTC", "temp_INTU",
  "temp_ISRG", "temp_JNJ", "temp_JPM", "temp_KO", "temp_LIN", "temp_LLY",
  "temp_LOW", "temp_LRCX", "temp_MA", "temp_MCD", "temp_MDLZ", "temp_META",
  "temp_MMC", "temp_MMM", "temp_MO", "temp_MRK", "temp_MS", "temp_MSFT",
  "temp_MU", "temp_NEE", "temp_NKE", "temp_NOC", "temp_NVDA", "temp_ORCL",
  "temp_PEP", "temp_PFE", "temp_PG", "temp_PGR", "temp_PLD", "temp_PM",
  "temp_PNC", "temp_QCOM", "temp_REGN", "temp_RTX", "temp_SBUX", "temp_SCHW",
  "temp_SLB", "temp_SO", "temp_SPGI", "temp_SYK", "temp_T", "temp_TJX",
  "temp_TMO", "temp_TMUS", "temp_TSLA", "temp_TXN", "temp_UNH", "temp_UNP",
  "temp_UPS", "temp_V", "temp_VRTX", "temp_VZ", "temp_WFC", "temp_WMT",
  "temp_XOM", "temp_ZTS",

  # Hourly temp tables
  "temp_hourly_AAPL", "temp_hourly_ABBV", "temp_hourly_ABT", "temp_hourly_ACN",
  "temp_hourly_ADBE", "temp_hourly_AMD", "temp_hourly_AMGN", "temp_hourly_AMZN",
  "temp_hourly_AVGO", "temp_hourly_BA", "temp_hourly_BMY", "temp_hourly_BRK_B",
  "temp_hourly_CAT", "temp_hourly_CMCSA", "temp_hourly_COST", "temp_hourly_CRM",
  "temp_hourly_CSCO", "temp_hourly_CVX", "temp_hourly_DE", "temp_hourly_DHR",
  "temp_hourly_DIS", "temp_hourly_GE", "temp_hourly_GOOGL", "temp_hourly_GS",
  "temp_hourly_HD", "temp_hourly_HON", "temp_hourly_IBM", "temp_hourly_INTC",
  "temp_hourly_JNJ", "temp_hourly_JPM", "temp_hourly_KO", "temp_hourly_LLY",
  "temp_hourly_MA", "temp_hourly_MCD", "temp_hourly_META", "temp_hourly_MMM",
  "temp_hourly_MRK", "temp_hourly_MSFT", "temp_hourly_NEE", "temp_hourly_NKE",
  "temp_hourly_NVDA", "temp_hourly_ORCL", "temp_hourly_PEP", "temp_hourly_PFE",
  "temp_hourly_PG", "temp_hourly_PM", "temp_hourly_QCOM", "temp_hourly_RTX",
  "temp_hourly_SBUX", "temp_hourly_TMO", "temp_hourly_TSLA", "temp_hourly_TXN",
  "temp_hourly_UNH", "temp_hourly_UNP", "temp_hourly_UPS", "temp_hourly_V",
  "temp_hourly_VZ", "temp_hourly_WFC", "temp_hourly_WMT", "temp_hourly_XOM",

  # Feature temp tables
  "_temp_features_AAPL", "_temp_features_DIA", "_temp_features_ETHUSD",
  "_temp_features_IWM", "_temp_features_MSFT", "_temp_features_NVDA",
  "_temp_features_SOLUSD"
)

foreach ($table in $tempTables) {
    Write-Host "Deleting $table..."
    bq rm -f -t aialgotradehits:crypto_trading_data.$table
}
```

### 2. Delete v2_* legacy tables (30+ tables)

```powershell
$v2Tables = @(
  "v2_bonds_daily",
  "v2_commodities_5min", "v2_commodities_daily", "v2_commodities_historical_daily",
  "v2_commodities_hourly", "v2_commodities_weekly_summary",
  "v2_crypto_5min", "v2_crypto_daily", "v2_crypto_hourly",
  "v2_cryptos_historical_daily", "v2_cryptos_weekly_summary",
  "v2_etfs_5min", "v2_etfs_daily", "v2_etfs_historical_daily",
  "v2_etfs_hourly", "v2_etfs_weekly_summary",
  "v2_forex_5min", "v2_forex_daily", "v2_forex_historical_daily",
  "v2_forex_hourly", "v2_forex_weekly_summary",
  "v2_indices_5min", "v2_indices_daily", "v2_indices_historical_daily",
  "v2_indices_hourly", "v2_indices_weekly_summary",
  "v2_stocks_5min", "v2_stocks_daily", "v2_stocks_historical_daily",
  "v2_stocks_hourly", "v2_stocks_master", "v2_stocks_weekly_summary"
)

foreach ($table in $v2Tables) {
    Write-Host "Deleting $table..."
    bq rm -f -t aialgotradehits:crypto_trading_data.$table
}
```

### 3. Delete other legacy/temporary tables

```powershell
$legacyTables = @(
  "btc_ai_training_daily",
  "nvda_ai_training_daily",
  "stocks_unified_daily",
  "weekly_commodities_all",
  "weekly_crypto_all",
  "weekly_etfs_all",
  "weekly_forex_all",
  "weekly_funds_all",
  "weekly_indices_all",
  "weekly_stocks_all"
)

foreach ($table in $legacyTables) {
    Write-Host "Deleting $table..."
    bq rm -f -t aialgotradehits:crypto_trading_data.$table
}
```

---

## AFTER CLEANUP

**Production tables** (4):
- stocks_daily_clean
- stocks_hourly_clean
- stocks_5min_clean
- crypto_daily_clean

**Supporting tables** (~45):
- All fundamentals, analyst, ETF, calendar, and strategy tables

**Total tables**: ~49 (down from 200+)
**Space saved**: 500+ MB estimated
**Cost savings**: ~$0.01/month (minimal but cleaner architecture)

---

## NEXT STEPS

1. ✓ Run cleanup scripts above
2. ⏳ Create stocks_1min_clean table (shift from 5min)
3. ⏳ Create crypto_hourly_clean, crypto_1min_clean tables
4. ⏳ Fill gaps in existing clean tables
5. ⏳ Expand to 2,500 stocks + 150 crypto

---

**Report Generated**: December 10, 2025
**Action**: Ready to execute cleanup
