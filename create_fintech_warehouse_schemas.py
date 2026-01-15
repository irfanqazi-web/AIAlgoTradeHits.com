"""
Fintech Data Warehouse Schema Creator
Creates all BigQuery tables for the expanded data warehouse
"""

import sys
import io
from google.cloud import bigquery
from datetime import datetime

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

client = bigquery.Client(project=PROJECT_ID)

print("=" * 80)
print("FINTECH DATA WAREHOUSE SCHEMA CREATOR")
print(f"Project: {PROJECT_ID}")
print(f"Dataset: {DATASET_ID}")
print(f"Timestamp: {datetime.now().isoformat()}")
print("=" * 80)

# ============================================================================
# SECTION 1: OHLCV EXPANSION TABLES
# ============================================================================

OHLCV_EXPANSION_TABLES = {
    "v2_forex_daily": """
        datetime TIMESTAMP,
        symbol STRING,
        currency_base STRING,
        currency_quote STRING,
        open FLOAT64,
        high FLOAT64,
        low FLOAT64,
        close FLOAT64,
        -- Technical Indicators
        percent_change FLOAT64,
        rsi FLOAT64,
        macd FLOAT64,
        macd_signal FLOAT64,
        macd_histogram FLOAT64,
        bollinger_upper FLOAT64,
        bollinger_middle FLOAT64,
        bollinger_lower FLOAT64,
        sma_20 FLOAT64,
        sma_50 FLOAT64,
        sma_200 FLOAT64,
        ema_12 FLOAT64,
        ema_26 FLOAT64,
        atr FLOAT64,
        adx FLOAT64,
        stoch_k FLOAT64,
        stoch_d FLOAT64,
        cci FLOAT64,
        williams_r FLOAT64,
        momentum FLOAT64,
        roc FLOAT64,
        fetch_timestamp TIMESTAMP
    """,
    "v2_forex_hourly": """
        datetime TIMESTAMP,
        symbol STRING,
        currency_base STRING,
        currency_quote STRING,
        open FLOAT64,
        high FLOAT64,
        low FLOAT64,
        close FLOAT64,
        percent_change FLOAT64,
        rsi FLOAT64,
        macd FLOAT64,
        macd_signal FLOAT64,
        macd_histogram FLOAT64,
        bollinger_upper FLOAT64,
        bollinger_middle FLOAT64,
        bollinger_lower FLOAT64,
        sma_20 FLOAT64,
        sma_50 FLOAT64,
        ema_12 FLOAT64,
        ema_26 FLOAT64,
        atr FLOAT64,
        adx FLOAT64,
        stoch_k FLOAT64,
        stoch_d FLOAT64,
        momentum FLOAT64,
        fetch_timestamp TIMESTAMP
    """,
    "v2_commodities_daily": """
        datetime TIMESTAMP,
        symbol STRING,
        name STRING,
        exchange STRING,
        open FLOAT64,
        high FLOAT64,
        low FLOAT64,
        close FLOAT64,
        volume FLOAT64,
        percent_change FLOAT64,
        rsi FLOAT64,
        macd FLOAT64,
        macd_signal FLOAT64,
        macd_histogram FLOAT64,
        bollinger_upper FLOAT64,
        bollinger_middle FLOAT64,
        bollinger_lower FLOAT64,
        sma_20 FLOAT64,
        sma_50 FLOAT64,
        sma_200 FLOAT64,
        ema_12 FLOAT64,
        ema_26 FLOAT64,
        atr FLOAT64,
        adx FLOAT64,
        stoch_k FLOAT64,
        stoch_d FLOAT64,
        cci FLOAT64,
        williams_r FLOAT64,
        obv FLOAT64,
        momentum FLOAT64,
        roc FLOAT64,
        fetch_timestamp TIMESTAMP
    """,
    "v2_bonds_daily": """
        datetime TIMESTAMP,
        symbol STRING,
        name STRING,
        country STRING,
        yield_value FLOAT64,
        open FLOAT64,
        high FLOAT64,
        low FLOAT64,
        close FLOAT64,
        percent_change FLOAT64,
        sma_20 FLOAT64,
        sma_50 FLOAT64,
        sma_200 FLOAT64,
        fetch_timestamp TIMESTAMP
    """,
    "v2_indices_daily": """
        datetime TIMESTAMP,
        symbol STRING,
        name STRING,
        exchange STRING,
        open FLOAT64,
        high FLOAT64,
        low FLOAT64,
        close FLOAT64,
        volume FLOAT64,
        percent_change FLOAT64,
        rsi FLOAT64,
        macd FLOAT64,
        macd_signal FLOAT64,
        macd_histogram FLOAT64,
        bollinger_upper FLOAT64,
        bollinger_middle FLOAT64,
        bollinger_lower FLOAT64,
        sma_20 FLOAT64,
        sma_50 FLOAT64,
        sma_200 FLOAT64,
        ema_12 FLOAT64,
        ema_26 FLOAT64,
        atr FLOAT64,
        adx FLOAT64,
        stoch_k FLOAT64,
        stoch_d FLOAT64,
        cci FLOAT64,
        williams_r FLOAT64,
        momentum FLOAT64,
        roc FLOAT64,
        fetch_timestamp TIMESTAMP
    """,
    "v2_indices_hourly": """
        datetime TIMESTAMP,
        symbol STRING,
        name STRING,
        exchange STRING,
        open FLOAT64,
        high FLOAT64,
        low FLOAT64,
        close FLOAT64,
        volume FLOAT64,
        percent_change FLOAT64,
        rsi FLOAT64,
        macd FLOAT64,
        macd_signal FLOAT64,
        macd_histogram FLOAT64,
        sma_20 FLOAT64,
        sma_50 FLOAT64,
        ema_12 FLOAT64,
        ema_26 FLOAT64,
        atr FLOAT64,
        adx FLOAT64,
        momentum FLOAT64,
        fetch_timestamp TIMESTAMP
    """
}

# ============================================================================
# SECTION 2: FUNDAMENTAL DATA TABLES
# ============================================================================

FUNDAMENTAL_TABLES = {
    "fundamentals_company_profile": """
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
        asset_type STRING,
        fetch_timestamp TIMESTAMP
    """,
    "fundamentals_statistics": """
        symbol STRING,
        datetime TIMESTAMP,
        market_cap FLOAT64,
        enterprise_value FLOAT64,
        trailing_pe FLOAT64,
        forward_pe FLOAT64,
        peg_ratio FLOAT64,
        price_to_sales FLOAT64,
        price_to_book FLOAT64,
        enterprise_to_revenue FLOAT64,
        enterprise_to_ebitda FLOAT64,
        profit_margin FLOAT64,
        operating_margin FLOAT64,
        return_on_assets FLOAT64,
        return_on_equity FLOAT64,
        revenue_ttm FLOAT64,
        revenue_per_share FLOAT64,
        quarterly_revenue_growth FLOAT64,
        gross_profit_ttm FLOAT64,
        ebitda FLOAT64,
        net_income_ttm FLOAT64,
        diluted_eps FLOAT64,
        quarterly_earnings_growth FLOAT64,
        total_cash FLOAT64,
        total_cash_per_share FLOAT64,
        total_debt FLOAT64,
        debt_to_equity FLOAT64,
        current_ratio FLOAT64,
        book_value_per_share FLOAT64,
        operating_cash_flow FLOAT64,
        levered_free_cash_flow FLOAT64,
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
    """,
    "fundamentals_income_statement": """
        symbol STRING,
        fiscal_date DATE,
        period STRING,
        currency STRING,
        total_revenue FLOAT64,
        cost_of_revenue FLOAT64,
        gross_profit FLOAT64,
        research_development FLOAT64,
        selling_general_admin FLOAT64,
        operating_expenses FLOAT64,
        operating_income FLOAT64,
        interest_expense FLOAT64,
        interest_income FLOAT64,
        other_income_expense FLOAT64,
        income_before_tax FLOAT64,
        income_tax_expense FLOAT64,
        net_income FLOAT64,
        net_income_common FLOAT64,
        basic_eps FLOAT64,
        diluted_eps FLOAT64,
        basic_shares_outstanding INT64,
        diluted_shares_outstanding INT64,
        ebitda FLOAT64,
        ebit FLOAT64,
        fetch_timestamp TIMESTAMP
    """,
    "fundamentals_balance_sheet": """
        symbol STRING,
        fiscal_date DATE,
        period STRING,
        currency STRING,
        total_assets FLOAT64,
        current_assets FLOAT64,
        cash_and_equivalents FLOAT64,
        short_term_investments FLOAT64,
        accounts_receivable FLOAT64,
        inventory FLOAT64,
        other_current_assets FLOAT64,
        non_current_assets FLOAT64,
        property_plant_equipment FLOAT64,
        goodwill FLOAT64,
        intangible_assets FLOAT64,
        long_term_investments FLOAT64,
        total_liabilities FLOAT64,
        current_liabilities FLOAT64,
        accounts_payable FLOAT64,
        short_term_debt FLOAT64,
        accrued_liabilities FLOAT64,
        non_current_liabilities FLOAT64,
        long_term_debt FLOAT64,
        total_equity FLOAT64,
        common_stock FLOAT64,
        retained_earnings FLOAT64,
        treasury_stock FLOAT64,
        fetch_timestamp TIMESTAMP
    """,
    "fundamentals_cash_flow": """
        symbol STRING,
        fiscal_date DATE,
        period STRING,
        currency STRING,
        operating_cash_flow FLOAT64,
        net_income FLOAT64,
        depreciation_amortization FLOAT64,
        stock_based_compensation FLOAT64,
        change_in_working_capital FLOAT64,
        change_in_receivables FLOAT64,
        change_in_inventory FLOAT64,
        change_in_payables FLOAT64,
        investing_cash_flow FLOAT64,
        capital_expenditures FLOAT64,
        acquisitions FLOAT64,
        purchases_of_investments FLOAT64,
        sales_of_investments FLOAT64,
        financing_cash_flow FLOAT64,
        debt_repayment FLOAT64,
        common_stock_issued FLOAT64,
        common_stock_repurchased FLOAT64,
        dividends_paid FLOAT64,
        net_change_in_cash FLOAT64,
        beginning_cash FLOAT64,
        ending_cash FLOAT64,
        free_cash_flow FLOAT64,
        fetch_timestamp TIMESTAMP
    """
}

# ============================================================================
# SECTION 3: ANALYST DATA TABLES
# ============================================================================

ANALYST_TABLES = {
    "analyst_recommendations": """
        symbol STRING,
        datetime TIMESTAMP,
        strong_buy INT64,
        buy INT64,
        hold INT64,
        sell INT64,
        strong_sell INT64,
        total_analysts INT64,
        consensus_rating STRING,
        consensus_score FLOAT64,
        fetch_timestamp TIMESTAMP
    """,
    "analyst_price_targets": """
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
    """,
    "analyst_earnings_estimates": """
        symbol STRING,
        datetime TIMESTAMP,
        period STRING,
        eps_avg FLOAT64,
        eps_high FLOAT64,
        eps_low FLOAT64,
        number_of_analysts INT64,
        revenue_avg FLOAT64,
        revenue_high FLOAT64,
        revenue_low FLOAT64,
        growth_estimate FLOAT64,
        fetch_timestamp TIMESTAMP
    """,
    "analyst_eps_trend": """
        symbol STRING,
        datetime TIMESTAMP,
        period STRING,
        current_estimate FLOAT64,
        estimate_7_days_ago FLOAT64,
        estimate_30_days_ago FLOAT64,
        estimate_60_days_ago FLOAT64,
        estimate_90_days_ago FLOAT64,
        fetch_timestamp TIMESTAMP
    """
}

# ============================================================================
# SECTION 4: CORPORATE ACTIONS TABLES
# ============================================================================

CORPORATE_ACTIONS_TABLES = {
    "earnings_calendar": """
        symbol STRING,
        name STRING,
        currency STRING,
        exchange STRING,
        mic_code STRING,
        country STRING,
        earnings_time STRING,
        earnings_date DATE,
        eps_estimate FLOAT64,
        eps_actual FLOAT64,
        eps_surprise FLOAT64,
        eps_surprise_percent FLOAT64,
        revenue_estimate FLOAT64,
        revenue_actual FLOAT64,
        revenue_surprise FLOAT64,
        fetch_timestamp TIMESTAMP
    """,
    "dividends_calendar": """
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
        dividend_type STRING,
        frequency STRING,
        fetch_timestamp TIMESTAMP
    """,
    "splits_calendar": """
        symbol STRING,
        name STRING,
        exchange STRING,
        split_date DATE,
        from_factor INT64,
        to_factor INT64,
        split_ratio FLOAT64,
        description STRING,
        fetch_timestamp TIMESTAMP
    """,
    "ipo_calendar": """
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
        status STRING,
        fetch_timestamp TIMESTAMP
    """
}

# ============================================================================
# SECTION 5: INSIDER & INSTITUTIONAL TABLES
# ============================================================================

INSIDER_INSTITUTIONAL_TABLES = {
    "insider_transactions": """
        symbol STRING,
        filing_date DATE,
        transaction_date DATE,
        owner_name STRING,
        owner_title STRING,
        transaction_type STRING,
        shares INT64,
        price_per_share FLOAT64,
        total_value FLOAT64,
        shares_owned_after INT64,
        is_direct_owner BOOLEAN,
        sec_form STRING,
        fetch_timestamp TIMESTAMP
    """,
    "institutional_holders": """
        symbol STRING,
        holder_name STRING,
        shares INT64,
        value FLOAT64,
        percent_held FLOAT64,
        change_shares INT64,
        change_percent FLOAT64,
        date_reported DATE,
        fetch_timestamp TIMESTAMP
    """,
    "fund_holders": """
        symbol STRING,
        fund_name STRING,
        shares INT64,
        value FLOAT64,
        percent_of_fund FLOAT64,
        change_shares INT64,
        change_percent FLOAT64,
        date_reported DATE,
        fetch_timestamp TIMESTAMP
    """
}

# ============================================================================
# SECTION 6: ETF ANALYTICS TABLES
# ============================================================================

ETF_TABLES = {
    "etf_profile": """
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
    """,
    "etf_holdings": """
        etf_symbol STRING,
        holding_symbol STRING,
        holding_name STRING,
        weight FLOAT64,
        shares INT64,
        sector STRING,
        asset_class STRING,
        fetch_timestamp TIMESTAMP
    """,
    "etf_performance": """
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
    """,
    "etf_risk": """
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
    """
}

# ============================================================================
# SECTION 7: MUTUAL FUND TABLES
# ============================================================================

MUTUAL_FUND_TABLES = {
    "mutual_fund_profile": """
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
    """,
    "mutual_fund_performance": """
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
    """,
    "mutual_fund_ratings": """
        symbol STRING,
        datetime TIMESTAMP,
        overall_rating INT64,
        risk_rating STRING,
        return_rating STRING,
        morningstar_rating INT64,
        analyst_rating STRING,
        sustainability_rating STRING,
        fetch_timestamp TIMESTAMP
    """
}

# ============================================================================
# SECTION 8: MARKET DATA TABLES
# ============================================================================

MARKET_DATA_TABLES = {
    "market_movers": """
        datetime TIMESTAMP,
        market STRING,
        category STRING,
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
    """,
    "market_state": """
        datetime TIMESTAMP,
        exchange STRING,
        market_type STRING,
        state STRING,
        next_state STRING,
        next_state_time TIMESTAMP,
        fetch_timestamp TIMESTAMP
    """,
    "exchange_schedule": """
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
    """
}

# ============================================================================
# SECTION 9: SEC FILINGS TABLE
# ============================================================================

SEC_TABLES = {
    "sec_edgar_filings": """
        symbol STRING,
        company_name STRING,
        cik STRING,
        form_type STRING,
        filing_date DATE,
        accepted_date TIMESTAMP,
        filing_url STRING,
        document_count INT64,
        primary_document STRING,
        size_bytes INT64,
        fetch_timestamp TIMESTAMP
    """
}

# ============================================================================
# CREATE ALL TABLES
# ============================================================================

def create_table(table_name, schema_str):
    """Create a BigQuery table with the given schema"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Parse schema string into SchemaField objects
    schema_fields = []
    for line in schema_str.strip().split('\n'):
        line = line.strip().rstrip(',')
        if line and not line.startswith('--'):
            parts = line.split()
            if len(parts) >= 2:
                field_name = parts[0]
                field_type = parts[1]
                schema_fields.append(bigquery.SchemaField(field_name, field_type))

    table = bigquery.Table(table_id, schema=schema_fields)

    try:
        table = client.create_table(table)
        print(f"  Created: {table_name}")
        return True
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"  Already exists: {table_name}")
            return True
        else:
            print(f"  ERROR creating {table_name}: {e}")
            return False

def main():
    all_tables = {}

    print("\n" + "=" * 80)
    print("SECTION 1: OHLCV EXPANSION TABLES")
    print("=" * 80)
    for name, schema in OHLCV_EXPANSION_TABLES.items():
        create_table(name, schema)

    print("\n" + "=" * 80)
    print("SECTION 2: FUNDAMENTAL DATA TABLES")
    print("=" * 80)
    for name, schema in FUNDAMENTAL_TABLES.items():
        create_table(name, schema)

    print("\n" + "=" * 80)
    print("SECTION 3: ANALYST DATA TABLES")
    print("=" * 80)
    for name, schema in ANALYST_TABLES.items():
        create_table(name, schema)

    print("\n" + "=" * 80)
    print("SECTION 4: CORPORATE ACTIONS TABLES")
    print("=" * 80)
    for name, schema in CORPORATE_ACTIONS_TABLES.items():
        create_table(name, schema)

    print("\n" + "=" * 80)
    print("SECTION 5: INSIDER & INSTITUTIONAL TABLES")
    print("=" * 80)
    for name, schema in INSIDER_INSTITUTIONAL_TABLES.items():
        create_table(name, schema)

    print("\n" + "=" * 80)
    print("SECTION 6: ETF ANALYTICS TABLES")
    print("=" * 80)
    for name, schema in ETF_TABLES.items():
        create_table(name, schema)

    print("\n" + "=" * 80)
    print("SECTION 7: MUTUAL FUND TABLES")
    print("=" * 80)
    for name, schema in MUTUAL_FUND_TABLES.items():
        create_table(name, schema)

    print("\n" + "=" * 80)
    print("SECTION 8: MARKET DATA TABLES")
    print("=" * 80)
    for name, schema in MARKET_DATA_TABLES.items():
        create_table(name, schema)

    print("\n" + "=" * 80)
    print("SECTION 9: SEC FILINGS TABLE")
    print("=" * 80)
    for name, schema in SEC_TABLES.items():
        create_table(name, schema)

    # Count total tables
    total_tables = (
        len(OHLCV_EXPANSION_TABLES) +
        len(FUNDAMENTAL_TABLES) +
        len(ANALYST_TABLES) +
        len(CORPORATE_ACTIONS_TABLES) +
        len(INSIDER_INSTITUTIONAL_TABLES) +
        len(ETF_TABLES) +
        len(MUTUAL_FUND_TABLES) +
        len(MARKET_DATA_TABLES) +
        len(SEC_TABLES)
    )

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total new tables created: {total_tables}")
    print(f"Dataset: {DATASET_ID}")
    print(f"Project: {PROJECT_ID}")
    print("=" * 80)

if __name__ == "__main__":
    main()
