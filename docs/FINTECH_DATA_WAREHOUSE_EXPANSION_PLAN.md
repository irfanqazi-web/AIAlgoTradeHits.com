# Fintech Data Warehouse Expansion Plan
## Maximum Data Collection from TwelveData API

**Created:** December 7, 2025
**Deadline:** December 18, 2025
**Testing Period:** December 18 - January 2, 2026

---

## EXECUTIVE SUMMARY

This plan expands the AIAlgoTradeHits data warehouse to include ALL available data from TwelveData API, creating a comprehensive fintech data platform for ML training and trading analysis.

### Current State (December 7, 2025)
- 9 OHLCV tables (v2_crypto/stocks/etfs × daily/hourly/5min)
- 25+ Cloud Schedulers running
- Basic technical indicators calculated

### Target State (December 18, 2025)
- 35+ data tables
- Fundamental data for all US stocks
- Analyst ratings and estimates
- ETF/Mutual fund analytics
- Market movers and trends
- Earnings and dividends calendars
- Insider transactions
- Full technical indicator suite

---

## SECTION 1: OHLCV DATA (Existing + Expansion)

### Currently Implemented
| Table | Status | Records |
|-------|--------|---------|
| v2_crypto_daily | ACTIVE | 10+ years |
| v2_crypto_hourly | ACTIVE | 1 month |
| v2_crypto_5min | ACTIVE | 1 week |
| v2_stocks_daily | ACTIVE | 10+ years |
| v2_stocks_hourly | ACTIVE | 1 month |
| v2_stocks_5min | ACTIVE | 1 week |
| v2_etfs_daily | ACTIVE | 10+ years |
| v2_etfs_hourly | ACTIVE | 1 month |
| v2_etfs_5min | ACTIVE | 1 week |

### New OHLCV Tables to Add
| Table | Assets | Schedule | Priority |
|-------|--------|----------|----------|
| v2_forex_daily | 20 major USD pairs | Daily 6 AM | HIGH |
| v2_forex_hourly | 20 major USD pairs | Hourly | HIGH |
| v2_forex_5min | 10 major pairs | Every 5 min | MEDIUM |
| v2_commodities_daily | 40 commodities | Daily 6 AM | HIGH |
| v2_commodities_hourly | 20 commodities | Hourly | MEDIUM |
| v2_bonds_daily | 5 US Treasury | Daily 6 AM | HIGH |
| v2_indices_daily | 10 US indices | Daily 6 AM | HIGH |
| v2_indices_hourly | 5 major indices | Hourly | MEDIUM |

---

## SECTION 2: FUNDAMENTAL DATA (NEW)

### Table: fundamentals_company_profile
**Endpoint:** `/profile`
**Schedule:** Weekly (Sundays)
**Assets:** S&P 500 + Top 200 additional stocks

```sql
CREATE TABLE IF NOT EXISTS fundamentals_company_profile (
  symbol STRING,
  name STRING,
  exchange STRING,
  mic_code STRING,
  sector STRING,
  industry STRING,
  employees INT64,
  website STRING,
  description STRING,
  ceo STRING,
  address STRING,
  city STRING,
  zip STRING,
  state STRING,
  country STRING,
  phone STRING,
  logo_url STRING,
  type STRING,
  fetch_timestamp TIMESTAMP
);
```

### Table: fundamentals_statistics
**Endpoint:** `/statistics`
**Schedule:** Daily at 7 AM
**Assets:** S&P 500

```sql
CREATE TABLE IF NOT EXISTS fundamentals_statistics (
  symbol STRING,
  datetime TIMESTAMP,
  -- Valuation Measures
  market_cap FLOAT64,
  enterprise_value FLOAT64,
  trailing_pe FLOAT64,
  forward_pe FLOAT64,
  peg_ratio FLOAT64,
  price_to_sales FLOAT64,
  price_to_book FLOAT64,
  enterprise_to_revenue FLOAT64,
  enterprise_to_ebitda FLOAT64,
  -- Profitability
  profit_margin FLOAT64,
  operating_margin FLOAT64,
  return_on_assets FLOAT64,
  return_on_equity FLOAT64,
  -- Income Statement
  revenue_ttm FLOAT64,
  revenue_per_share FLOAT64,
  quarterly_revenue_growth FLOAT64,
  gross_profit_ttm FLOAT64,
  ebitda FLOAT64,
  net_income_ttm FLOAT64,
  diluted_eps FLOAT64,
  quarterly_earnings_growth FLOAT64,
  -- Balance Sheet
  total_cash FLOAT64,
  total_cash_per_share FLOAT64,
  total_debt FLOAT64,
  debt_to_equity FLOAT64,
  current_ratio FLOAT64,
  book_value_per_share FLOAT64,
  -- Cash Flow
  operating_cash_flow FLOAT64,
  levered_free_cash_flow FLOAT64,
  -- Stock Info
  beta FLOAT64,
  fifty_two_week_low FLOAT64,
  fifty_two_week_high FLOAT64,
  fifty_day_ma FLOAT64,
  two_hundred_day_ma FLOAT64,
  shares_outstanding INT64,
  shares_float INT64,
  shares_short INT64,
  short_ratio FLOAT64,
  fetch_timestamp TIMESTAMP
);
```

### Table: fundamentals_income_statement
**Endpoint:** `/income_statement`
**Schedule:** Weekly (Saturdays)
**Period:** Annual and Quarterly

```sql
CREATE TABLE IF NOT EXISTS fundamentals_income_statement (
  symbol STRING,
  fiscal_date DATE,
  period STRING,  -- 'annual' or 'quarterly'
  currency STRING,
  -- Revenue
  total_revenue FLOAT64,
  cost_of_revenue FLOAT64,
  gross_profit FLOAT64,
  -- Operating Expenses
  research_development FLOAT64,
  selling_general_admin FLOAT64,
  operating_expenses FLOAT64,
  operating_income FLOAT64,
  -- Non-Operating
  interest_expense FLOAT64,
  interest_income FLOAT64,
  other_income_expense FLOAT64,
  -- Earnings
  income_before_tax FLOAT64,
  income_tax_expense FLOAT64,
  net_income FLOAT64,
  net_income_common FLOAT64,
  -- Per Share
  basic_eps FLOAT64,
  diluted_eps FLOAT64,
  basic_shares_outstanding INT64,
  diluted_shares_outstanding INT64,
  -- Metrics
  ebitda FLOAT64,
  ebit FLOAT64,
  fetch_timestamp TIMESTAMP
);
```

### Table: fundamentals_balance_sheet
**Endpoint:** `/balance_sheet`
**Schedule:** Weekly (Saturdays)

```sql
CREATE TABLE IF NOT EXISTS fundamentals_balance_sheet (
  symbol STRING,
  fiscal_date DATE,
  period STRING,
  currency STRING,
  -- Assets
  total_assets FLOAT64,
  current_assets FLOAT64,
  cash_and_equivalents FLOAT64,
  short_term_investments FLOAT64,
  accounts_receivable FLOAT64,
  inventory FLOAT64,
  other_current_assets FLOAT64,
  -- Non-Current Assets
  non_current_assets FLOAT64,
  property_plant_equipment FLOAT64,
  goodwill FLOAT64,
  intangible_assets FLOAT64,
  long_term_investments FLOAT64,
  -- Liabilities
  total_liabilities FLOAT64,
  current_liabilities FLOAT64,
  accounts_payable FLOAT64,
  short_term_debt FLOAT64,
  accrued_liabilities FLOAT64,
  non_current_liabilities FLOAT64,
  long_term_debt FLOAT64,
  -- Equity
  total_equity FLOAT64,
  common_stock FLOAT64,
  retained_earnings FLOAT64,
  treasury_stock FLOAT64,
  fetch_timestamp TIMESTAMP
);
```

### Table: fundamentals_cash_flow
**Endpoint:** `/cash_flow`
**Schedule:** Weekly (Saturdays)

```sql
CREATE TABLE IF NOT EXISTS fundamentals_cash_flow (
  symbol STRING,
  fiscal_date DATE,
  period STRING,
  currency STRING,
  -- Operating Activities
  operating_cash_flow FLOAT64,
  net_income FLOAT64,
  depreciation_amortization FLOAT64,
  stock_based_compensation FLOAT64,
  change_in_working_capital FLOAT64,
  change_in_receivables FLOAT64,
  change_in_inventory FLOAT64,
  change_in_payables FLOAT64,
  -- Investing Activities
  investing_cash_flow FLOAT64,
  capital_expenditures FLOAT64,
  acquisitions FLOAT64,
  purchases_of_investments FLOAT64,
  sales_of_investments FLOAT64,
  -- Financing Activities
  financing_cash_flow FLOAT64,
  debt_repayment FLOAT64,
  common_stock_issued FLOAT64,
  common_stock_repurchased FLOAT64,
  dividends_paid FLOAT64,
  -- Summary
  net_change_in_cash FLOAT64,
  beginning_cash FLOAT64,
  ending_cash FLOAT64,
  free_cash_flow FLOAT64,
  fetch_timestamp TIMESTAMP
);
```

---

## SECTION 3: ANALYST DATA (NEW)

### Table: analyst_recommendations
**Endpoint:** `/recommendations`
**Schedule:** Daily at 8 AM

```sql
CREATE TABLE IF NOT EXISTS analyst_recommendations (
  symbol STRING,
  datetime TIMESTAMP,
  strong_buy INT64,
  buy INT64,
  hold INT64,
  sell INT64,
  strong_sell INT64,
  total_analysts INT64,
  consensus_rating STRING,  -- 'Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'
  consensus_score FLOAT64,  -- 1-5 scale
  fetch_timestamp TIMESTAMP
);
```

### Table: analyst_price_targets
**Endpoint:** `/price_target`
**Schedule:** Daily at 8 AM

```sql
CREATE TABLE IF NOT EXISTS analyst_price_targets (
  symbol STRING,
  datetime TIMESTAMP,
  target_high FLOAT64,
  target_low FLOAT64,
  target_mean FLOAT64,
  target_median FLOAT64,
  current_price FLOAT64,
  upside_percent FLOAT64,
  number_of_analysts INT64,
  fetch_timestamp TIMESTAMP
);
```

### Table: analyst_earnings_estimates
**Endpoint:** `/earnings_estimate`
**Schedule:** Weekly

```sql
CREATE TABLE IF NOT EXISTS analyst_earnings_estimates (
  symbol STRING,
  datetime TIMESTAMP,
  period STRING,  -- 'current_quarter', 'next_quarter', 'current_year', 'next_year'
  eps_avg FLOAT64,
  eps_high FLOAT64,
  eps_low FLOAT64,
  number_of_analysts INT64,
  revenue_avg FLOAT64,
  revenue_high FLOAT64,
  revenue_low FLOAT64,
  growth_estimate FLOAT64,
  fetch_timestamp TIMESTAMP
);
```

### Table: analyst_eps_trend
**Endpoint:** `/eps_trend`
**Schedule:** Weekly

```sql
CREATE TABLE IF NOT EXISTS analyst_eps_trend (
  symbol STRING,
  datetime TIMESTAMP,
  period STRING,
  current_estimate FLOAT64,
  estimate_7_days_ago FLOAT64,
  estimate_30_days_ago FLOAT64,
  estimate_60_days_ago FLOAT64,
  estimate_90_days_ago FLOAT64,
  fetch_timestamp TIMESTAMP
);
```

---

## SECTION 4: CORPORATE ACTIONS (NEW)

### Table: earnings_calendar
**Endpoint:** `/earnings_calendar`
**Schedule:** Daily at 6 AM

```sql
CREATE TABLE IF NOT EXISTS earnings_calendar (
  symbol STRING,
  name STRING,
  currency STRING,
  exchange STRING,
  mic_code STRING,
  country STRING,
  time STRING,  -- 'Before Market Open', 'After Market Close', 'During Market Hours'
  earnings_date DATE,
  eps_estimate FLOAT64,
  eps_actual FLOAT64,
  eps_surprise FLOAT64,
  eps_surprise_percent FLOAT64,
  revenue_estimate FLOAT64,
  revenue_actual FLOAT64,
  revenue_surprise FLOAT64,
  fetch_timestamp TIMESTAMP
);
```

### Table: dividends_calendar
**Endpoint:** `/dividends_calendar`
**Schedule:** Daily at 6 AM

```sql
CREATE TABLE IF NOT EXISTS dividends_calendar (
  symbol STRING,
  name STRING,
  exchange STRING,
  mic_code STRING,
  currency STRING,
  declaration_date DATE,
  ex_date DATE,
  record_date DATE,
  payment_date DATE,
  amount FLOAT64,
  dividend_type STRING,  -- 'Cash', 'Stock', 'Special'
  frequency STRING,  -- 'Quarterly', 'Semi-Annual', 'Annual', 'Monthly'
  fetch_timestamp TIMESTAMP
);
```

### Table: splits_calendar
**Endpoint:** `/splits_calendar`
**Schedule:** Daily at 6 AM

```sql
CREATE TABLE IF NOT EXISTS splits_calendar (
  symbol STRING,
  name STRING,
  exchange STRING,
  split_date DATE,
  from_factor INT64,
  to_factor INT64,
  split_ratio FLOAT64,
  description STRING,
  fetch_timestamp TIMESTAMP
);
```

### Table: ipo_calendar
**Endpoint:** `/ipo_calendar`
**Schedule:** Daily at 6 AM

```sql
CREATE TABLE IF NOT EXISTS ipo_calendar (
  symbol STRING,
  name STRING,
  exchange STRING,
  currency STRING,
  ipo_date DATE,
  price_range_low FLOAT64,
  price_range_high FLOAT64,
  offer_price FLOAT64,
  shares_offered INT64,
  deal_size FLOAT64,
  underwriters STRING,
  status STRING,  -- 'Upcoming', 'Priced', 'Withdrawn'
  fetch_timestamp TIMESTAMP
);
```

---

## SECTION 5: INSIDER & INSTITUTIONAL (NEW)

### Table: insider_transactions
**Endpoint:** `/insider_transactions`
**Schedule:** Daily at 9 AM

```sql
CREATE TABLE IF NOT EXISTS insider_transactions (
  symbol STRING,
  filing_date DATE,
  transaction_date DATE,
  owner_name STRING,
  owner_title STRING,
  transaction_type STRING,  -- 'Purchase', 'Sale', 'Gift', 'Option Exercise'
  shares INT64,
  price_per_share FLOAT64,
  total_value FLOAT64,
  shares_owned_after INT64,
  is_direct_owner BOOLEAN,
  sec_form STRING,  -- 'Form 4', 'Form 3', 'Form 5'
  fetch_timestamp TIMESTAMP
);
```

### Table: institutional_holders
**Endpoint:** `/institutional_holders`
**Schedule:** Weekly (Sundays)

```sql
CREATE TABLE IF NOT EXISTS institutional_holders (
  symbol STRING,
  holder_name STRING,
  shares INT64,
  value FLOAT64,
  percent_held FLOAT64,
  change_shares INT64,
  change_percent FLOAT64,
  date_reported DATE,
  fetch_timestamp TIMESTAMP
);
```

### Table: fund_holders
**Endpoint:** `/fund_holders`
**Schedule:** Weekly (Sundays)

```sql
CREATE TABLE IF NOT EXISTS fund_holders (
  symbol STRING,
  fund_name STRING,
  shares INT64,
  value FLOAT64,
  percent_of_fund FLOAT64,
  change_shares INT64,
  change_percent FLOAT64,
  date_reported DATE,
  fetch_timestamp TIMESTAMP
);
```

---

## SECTION 6: ETF ANALYTICS (NEW)

### Table: etf_profile
**Endpoint:** `/etf_summary`
**Schedule:** Weekly

```sql
CREATE TABLE IF NOT EXISTS etf_profile (
  symbol STRING,
  name STRING,
  fund_family STRING,
  fund_type STRING,
  currency STRING,
  exchange STRING,
  inception_date DATE,
  expense_ratio FLOAT64,
  total_assets FLOAT64,
  nav FLOAT64,
  average_volume INT64,
  category STRING,
  benchmark STRING,
  investment_strategy STRING,
  fetch_timestamp TIMESTAMP
);
```

### Table: etf_holdings
**Endpoint:** `/etf_composition`
**Schedule:** Weekly

```sql
CREATE TABLE IF NOT EXISTS etf_holdings (
  etf_symbol STRING,
  holding_symbol STRING,
  holding_name STRING,
  weight FLOAT64,
  shares INT64,
  sector STRING,
  asset_class STRING,
  fetch_timestamp TIMESTAMP
);
```

### Table: etf_performance
**Endpoint:** `/etf_performance`
**Schedule:** Daily

```sql
CREATE TABLE IF NOT EXISTS etf_performance (
  symbol STRING,
  datetime TIMESTAMP,
  return_1d FLOAT64,
  return_1w FLOAT64,
  return_1m FLOAT64,
  return_3m FLOAT64,
  return_6m FLOAT64,
  return_ytd FLOAT64,
  return_1y FLOAT64,
  return_3y FLOAT64,
  return_5y FLOAT64,
  return_10y FLOAT64,
  return_since_inception FLOAT64,
  fetch_timestamp TIMESTAMP
);
```

### Table: etf_risk
**Endpoint:** `/etf_risk`
**Schedule:** Weekly

```sql
CREATE TABLE IF NOT EXISTS etf_risk (
  symbol STRING,
  datetime TIMESTAMP,
  alpha FLOAT64,
  beta FLOAT64,
  r_squared FLOAT64,
  standard_deviation FLOAT64,
  sharpe_ratio FLOAT64,
  treynor_ratio FLOAT64,
  max_drawdown FLOAT64,
  upside_capture FLOAT64,
  downside_capture FLOAT64,
  fetch_timestamp TIMESTAMP
);
```

---

## SECTION 7: MUTUAL FUNDS (NEW)

### Table: mutual_fund_profile
**Endpoint:** `/mf_summary`
**Schedule:** Weekly

```sql
CREATE TABLE IF NOT EXISTS mutual_fund_profile (
  symbol STRING,
  name STRING,
  fund_family STRING,
  fund_type STRING,
  category STRING,
  currency STRING,
  inception_date DATE,
  expense_ratio FLOAT64,
  total_assets FLOAT64,
  nav FLOAT64,
  minimum_investment FLOAT64,
  load_front FLOAT64,
  load_back FLOAT64,
  turnover_ratio FLOAT64,
  manager_name STRING,
  manager_tenure INT64,
  fetch_timestamp TIMESTAMP
);
```

### Table: mutual_fund_performance
**Endpoint:** `/mf_performance`
**Schedule:** Daily

```sql
CREATE TABLE IF NOT EXISTS mutual_fund_performance (
  symbol STRING,
  datetime TIMESTAMP,
  return_1d FLOAT64,
  return_1w FLOAT64,
  return_1m FLOAT64,
  return_3m FLOAT64,
  return_6m FLOAT64,
  return_ytd FLOAT64,
  return_1y FLOAT64,
  return_3y FLOAT64,
  return_5y FLOAT64,
  return_10y FLOAT64,
  category_rank INT64,
  category_count INT64,
  fetch_timestamp TIMESTAMP
);
```

### Table: mutual_fund_ratings
**Endpoint:** `/mf_ratings`
**Schedule:** Weekly

```sql
CREATE TABLE IF NOT EXISTS mutual_fund_ratings (
  symbol STRING,
  datetime TIMESTAMP,
  overall_rating INT64,
  risk_rating STRING,
  return_rating STRING,
  morningstar_rating INT64,
  analyst_rating STRING,
  sustainability_rating STRING,
  fetch_timestamp TIMESTAMP
);
```

---

## SECTION 8: MARKET DATA (NEW)

### Table: market_movers
**Endpoint:** `/market_movers/{market}`
**Schedule:** Every 30 minutes during market hours

```sql
CREATE TABLE IF NOT EXISTS market_movers (
  datetime TIMESTAMP,
  market STRING,  -- 'stocks', 'crypto', 'forex', 'etf'
  category STRING,  -- 'gainers', 'losers', 'most_active'
  rank INT64,
  symbol STRING,
  name STRING,
  exchange STRING,
  price FLOAT64,
  change FLOAT64,
  percent_change FLOAT64,
  volume INT64,
  market_cap FLOAT64,
  fetch_timestamp TIMESTAMP
);
```

### Table: market_state
**Endpoint:** `/market_state`
**Schedule:** Every 5 minutes

```sql
CREATE TABLE IF NOT EXISTS market_state (
  datetime TIMESTAMP,
  exchange STRING,
  market_type STRING,
  state STRING,  -- 'open', 'closed', 'pre-market', 'post-market'
  next_state STRING,
  next_state_time TIMESTAMP,
  fetch_timestamp TIMESTAMP
);
```

### Table: exchange_schedule
**Endpoint:** `/exchange_schedule`
**Schedule:** Daily at 5 AM

```sql
CREATE TABLE IF NOT EXISTS exchange_schedule (
  date DATE,
  exchange STRING,
  is_open BOOLEAN,
  pre_market_start TIMESTAMP,
  pre_market_end TIMESTAMP,
  market_open TIMESTAMP,
  market_close TIMESTAMP,
  post_market_start TIMESTAMP,
  post_market_end TIMESTAMP,
  is_holiday BOOLEAN,
  holiday_name STRING,
  fetch_timestamp TIMESTAMP
);
```

---

## SECTION 9: SEC FILINGS (NEW)

### Table: sec_edgar_filings
**Endpoint:** `/edgar_filings_archive`
**Schedule:** Daily at 10 AM

```sql
CREATE TABLE IF NOT EXISTS sec_edgar_filings (
  symbol STRING,
  company_name STRING,
  cik STRING,
  form_type STRING,  -- '10-K', '10-Q', '8-K', '4', '13F', etc.
  filing_date DATE,
  accepted_date TIMESTAMP,
  filing_url STRING,
  document_count INT64,
  primary_document STRING,
  size_bytes INT64,
  fetch_timestamp TIMESTAMP
);
```

---

## IMPLEMENTATION SCHEDULE

### Week 1 (Dec 7-13): Core Expansion
| Day | Tasks | Tables |
|-----|-------|--------|
| Dec 7 | Create BigQuery schemas | All fundamental tables |
| Dec 8 | Deploy fundamentals fetchers | company_profile, statistics |
| Dec 9 | Deploy financial statements fetchers | income, balance, cash_flow |
| Dec 10 | Deploy analyst data fetchers | recommendations, price_targets |
| Dec 11 | Deploy corporate actions fetchers | earnings, dividends, splits |
| Dec 12 | Deploy insider/institutional fetchers | insider, institutional |
| Dec 13 | Deploy ETF analytics fetchers | etf_profile, holdings, performance |

### Week 2 (Dec 14-18): Complete & Test
| Day | Tasks | Tables |
|-----|-------|--------|
| Dec 14 | Deploy mutual fund fetchers | mf_profile, performance, ratings |
| Dec 15 | Deploy market data fetchers | market_movers, market_state |
| Dec 16 | Deploy OHLCV expansions | forex, commodities, bonds |
| Dec 17 | Integration testing | All tables |
| Dec 18 | Documentation & handoff | Final validation |

---

## CLOUD FUNCTIONS TO CREATE

### New Cloud Functions (Priority Order)

1. **fundamentals-profile-fetcher**
   - Schedule: Weekly Sundays 7 AM
   - Assets: 700 stocks
   - Endpoint: /profile

2. **fundamentals-statistics-fetcher**
   - Schedule: Daily 7 AM
   - Assets: 500 stocks
   - Endpoint: /statistics

3. **fundamentals-financials-fetcher**
   - Schedule: Weekly Saturdays 8 AM
   - Assets: 500 stocks
   - Endpoints: /income_statement, /balance_sheet, /cash_flow

4. **analyst-ratings-fetcher**
   - Schedule: Daily 8 AM
   - Assets: 500 stocks
   - Endpoints: /recommendations, /price_target

5. **analyst-estimates-fetcher**
   - Schedule: Weekly Mondays 8 AM
   - Assets: 500 stocks
   - Endpoints: /earnings_estimate, /eps_trend

6. **earnings-calendar-fetcher**
   - Schedule: Daily 6 AM
   - Endpoint: /earnings_calendar

7. **dividends-calendar-fetcher**
   - Schedule: Daily 6 AM
   - Endpoint: /dividends_calendar

8. **splits-ipo-calendar-fetcher**
   - Schedule: Daily 6 AM
   - Endpoints: /splits_calendar, /ipo_calendar

9. **insider-transactions-fetcher**
   - Schedule: Daily 9 AM
   - Assets: 500 stocks
   - Endpoint: /insider_transactions

10. **institutional-holders-fetcher**
    - Schedule: Weekly Sundays 10 AM
    - Assets: 500 stocks
    - Endpoints: /institutional_holders, /fund_holders

11. **etf-analytics-fetcher**
    - Schedule: Daily 7 AM
    - Assets: 200 ETFs
    - Endpoints: /etf_summary, /etf_performance, /etf_risk

12. **etf-holdings-fetcher**
    - Schedule: Weekly Saturdays 7 AM
    - Assets: 200 ETFs
    - Endpoint: /etf_composition

13. **mutual-fund-fetcher**
    - Schedule: Weekly Sundays 8 AM
    - Assets: 100 funds
    - Endpoints: /mf_summary, /mf_performance, /mf_ratings

14. **market-movers-fetcher**
    - Schedule: Every 30 min during market hours
    - Markets: stocks, crypto, forex
    - Endpoint: /market_movers

15. **market-state-fetcher**
    - Schedule: Every 5 min
    - Endpoint: /market_state

16. **sec-filings-fetcher**
    - Schedule: Daily 10 AM
    - Assets: 500 stocks
    - Endpoint: /edgar_filings_archive

17. **forex-ohlcv-fetcher**
    - Schedule: Daily/Hourly
    - Assets: 20 major USD pairs
    - Endpoint: /time_series

18. **commodities-ohlcv-fetcher**
    - Schedule: Daily 6 AM
    - Assets: 40 commodities
    - Endpoint: /time_series

19. **bonds-ohlcv-fetcher**
    - Schedule: Daily 6 AM
    - Assets: 5 US Treasury
    - Endpoint: /time_series

20. **indices-ohlcv-fetcher**
    - Schedule: Daily/Hourly
    - Assets: 10 indices
    - Endpoint: /time_series

---

## API CREDIT ESTIMATION

### Daily API Credit Usage

| Data Type | Symbols | Credits/Symbol | Total Daily |
|-----------|---------|----------------|-------------|
| OHLCV (existing) | 800 | 3 timeframes | 2,400 |
| Forex OHLCV | 20 | 3 timeframes | 60 |
| Commodities OHLCV | 40 | 1 timeframe | 40 |
| Bonds OHLCV | 5 | 1 timeframe | 5 |
| Indices OHLCV | 10 | 2 timeframes | 20 |
| Statistics | 500 | 1 | 500 |
| Analyst Ratings | 500 | 2 endpoints | 1,000 |
| Earnings Calendar | 1 | 1 | 50 |
| Dividends Calendar | 1 | 1 | 50 |
| Insider Trans | 500 | 1 | 500 |
| ETF Analytics | 200 | 3 endpoints | 600 |
| Market Movers | 3 markets | 48 calls/day | 144 |
| **Daily Total** | | | **~5,400** |

### Monthly Total: ~162,000 credits
### Pro Plan Limit: 4,780,800 credits/month
### Utilization: ~3.4%

**Conclusion:** Well within API limits with significant headroom for expansion.

---

## COST IMPACT

### Additional Monthly Costs

| Component | Cost |
|-----------|------|
| 20 new Cloud Functions | ~$80/month |
| BigQuery Storage (additional 50GB) | ~$5/month |
| BigQuery Queries | ~$10/month |
| **Additional Total** | **~$95/month** |

### New Total Monthly Cost
Current: ~$195/month
Additional: ~$95/month
**New Total: ~$290/month**

---

## SUCCESS METRICS

### Data Warehouse Complete When:
- [ ] All 35+ tables created in BigQuery
- [ ] All 20 Cloud Functions deployed
- [ ] All Cloud Schedulers configured
- [ ] Data flowing for all asset types
- [ ] No errors in function logs
- [ ] Frontend can query all data types

### Quality Metrics:
- [ ] >99% API success rate
- [ ] <1% duplicate records
- [ ] <5% null values in required fields
- [ ] All financial data within 24 hours

---

## NEXT ACTIONS

### Immediate (Dec 7-8):
1. Create all BigQuery table schemas
2. Start with fundamentals fetchers
3. Deploy company_profile and statistics

### This Week (Dec 9-13):
4. Complete all fundamental data fetchers
5. Deploy analyst and corporate actions fetchers
6. Add ETF and mutual fund analytics

### Final Push (Dec 14-18):
7. Deploy market data fetchers
8. Expand OHLCV to forex, commodities, bonds
9. Integration testing
10. Documentation for Saleem

---

*Document Created: December 7, 2025*
*Target Completion: December 18, 2025*
