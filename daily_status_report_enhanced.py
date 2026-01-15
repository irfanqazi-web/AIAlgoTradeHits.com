#!/usr/bin/env python3
"""
Enhanced Daily Status Report
=============================
Generates a comprehensive daily status report after asset downloads at 1 AM including:
1. Record counts by asset type
2. Date ranges (start/end dates)
3. Sector/Category breakdown
4. Industry classification summary
5. Sentiment data summary
6. Trump/Political sentiment impact

This script should be run after the daily data download (1 AM scheduler).
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from google.cloud import bigquery
from datetime import datetime, timedelta
import json

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
ML_DATASET = 'ml_models'

bq_client = bigquery.Client(project=PROJECT_ID)

def generate_daily_status_report():
    """Generate comprehensive daily status report"""

    report_date = datetime.now().strftime('%Y-%m-%d')
    report_time = datetime.now().strftime('%H:%M:%S')

    print("=" * 80)
    print("ENHANCED DAILY STATUS REPORT")
    print("=" * 80)
    print(f"Report Date: {report_date}")
    print(f"Report Time: {report_time}")

    report = {
        'report_date': report_date,
        'report_time': report_time,
        'sections': {}
    }

    # =========================================================================
    # SECTION 1: Asset Record Counts and Date Ranges
    # =========================================================================
    print("\n" + "-" * 80)
    print("[1] ASSET RECORD COUNTS & DATE RANGES")
    print("-" * 80)

    asset_query = f"""
    WITH asset_stats AS (
        SELECT
            'stocks_daily' as table_name,
            'Stocks' as asset_type,
            COUNT(*) as record_count,
            COUNT(DISTINCT symbol) as unique_symbols,
            MIN(DATE(datetime)) as start_date,
            MAX(DATE(datetime)) as end_date,
            SUM(CASE WHEN DATE(datetime) = CURRENT_DATE() - 1 THEN 1 ELSE 0 END) as yesterday_records
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`

        UNION ALL

        SELECT
            'crypto_daily' as table_name,
            'Crypto' as asset_type,
            COUNT(*) as record_count,
            COUNT(DISTINCT symbol) as unique_symbols,
            MIN(DATE(datetime)) as start_date,
            MAX(DATE(datetime)) as end_date,
            SUM(CASE WHEN DATE(datetime) = CURRENT_DATE() - 1 THEN 1 ELSE 0 END) as yesterday_records
        FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`

        UNION ALL

        SELECT
            'stocks_hourly' as table_name,
            'Stocks Hourly' as asset_type,
            COUNT(*) as record_count,
            COUNT(DISTINCT symbol) as unique_symbols,
            MIN(DATE(datetime)) as start_date,
            MAX(DATE(datetime)) as end_date,
            SUM(CASE WHEN DATE(datetime) = CURRENT_DATE() - 1 THEN 1 ELSE 0 END) as yesterday_records
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_hourly_clean`

        UNION ALL

        SELECT
            'crypto_hourly' as table_name,
            'Crypto Hourly' as asset_type,
            COUNT(*) as record_count,
            COUNT(DISTINCT symbol) as unique_symbols,
            MIN(DATE(datetime)) as start_date,
            MAX(DATE(datetime)) as end_date,
            SUM(CASE WHEN DATE(datetime) = CURRENT_DATE() - 1 THEN 1 ELSE 0 END) as yesterday_records
        FROM `{PROJECT_ID}.{DATASET_ID}.crypto_hourly_clean`
    )
    SELECT * FROM asset_stats
    ORDER BY table_name
    """

    try:
        results = list(bq_client.query(asset_query).result())
        print(f"\n{'Asset Type':<20} | {'Records':>15} | {'Symbols':>10} | {'Start Date':>12} | {'End Date':>12} | {'Yesterday':>10}")
        print("-" * 95)

        asset_data = []
        total_records = 0
        for row in results:
            print(f"{row.asset_type:<20} | {row.record_count:>15,} | {row.unique_symbols:>10,} | {row.start_date} | {row.end_date} | {row.yesterday_records:>10,}")
            total_records += row.record_count
            asset_data.append({
                'table': row.table_name,
                'asset_type': row.asset_type,
                'records': row.record_count,
                'symbols': row.unique_symbols,
                'start_date': str(row.start_date),
                'end_date': str(row.end_date),
                'yesterday': row.yesterday_records
            })

        print(f"\n  Total Records: {total_records:,}")
        report['sections']['assets'] = asset_data
    except Exception as e:
        print(f"  Error: {e}")

    # =========================================================================
    # SECTION 2: Sector/Category Breakdown
    # =========================================================================
    print("\n" + "-" * 80)
    print("[2] SECTOR/CATEGORY BREAKDOWN")
    print("-" * 80)

    sector_query = f"""
    SELECT
        COALESCE(sc.sector, sd.sector, 'Unknown') as sector,
        COUNT(DISTINCT sd.symbol) as stock_count,
        COUNT(*) as record_count,
        SUM(CASE WHEN DATE(sd.datetime) = CURRENT_DATE() - 1 THEN 1 ELSE 0 END) as yesterday_records,
        ROUND(AVG(sd.rsi), 1) as avg_rsi,
        ROUND(AVG(sd.adx), 1) as avg_adx,
        ROUND(AVG(CASE WHEN sd.close > sd.sma_200 THEN 100.0 ELSE 0.0 END), 1) as pct_above_200ma
    FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean` sd
    LEFT JOIN `{PROJECT_ID}.{ML_DATASET}.stock_sector_classification` sc
        ON sd.symbol = sc.symbol
    WHERE sd.datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    GROUP BY sector
    ORDER BY stock_count DESC
    """

    try:
        results = list(bq_client.query(sector_query).result())
        print(f"\n{'Sector':<30} | {'Stocks':>8} | {'Records':>12} | {'Yesterday':>10} | {'Avg RSI':>8} | {'Above 200MA':>12}")
        print("-" * 95)

        sector_data = []
        for row in results:
            print(f"{row.sector:<30} | {row.stock_count:>8,} | {row.record_count:>12,} | {row.yesterday_records:>10,} | {row.avg_rsi or 0:>8.1f} | {row.pct_above_200ma or 0:>11.1f}%")
            sector_data.append({
                'sector': row.sector,
                'stocks': row.stock_count,
                'records': row.record_count,
                'yesterday': row.yesterday_records,
                'avg_rsi': float(row.avg_rsi or 0),
                'pct_above_200ma': float(row.pct_above_200ma or 0)
            })

        report['sections']['sectors'] = sector_data
    except Exception as e:
        print(f"  Error: {e}")

    # =========================================================================
    # SECTION 3: Industry Classification Summary
    # =========================================================================
    print("\n" + "-" * 80)
    print("[3] INDUSTRY CLASSIFICATION SUMMARY (Top 15)")
    print("-" * 80)

    industry_query = f"""
    SELECT
        COALESCE(sc.industry, sd.industry, 'Unknown') as industry,
        COALESCE(sc.sector, sd.sector, 'Unknown') as sector,
        COUNT(DISTINCT sd.symbol) as stock_count,
        COUNT(*) as record_count
    FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean` sd
    LEFT JOIN `{PROJECT_ID}.{ML_DATASET}.stock_sector_classification` sc
        ON sd.symbol = sc.symbol
    WHERE sd.datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    GROUP BY industry, sector
    ORDER BY stock_count DESC
    LIMIT 15
    """

    try:
        results = list(bq_client.query(industry_query).result())
        print(f"\n{'Industry':<35} | {'Sector':<25} | {'Stocks':>8} | {'Records':>12}")
        print("-" * 90)

        industry_data = []
        for row in results:
            industry_name = row.industry[:33] if row.industry else 'Unknown'
            sector_name = row.sector[:23] if row.sector else 'Unknown'
            print(f"{industry_name:<35} | {sector_name:<25} | {row.stock_count:>8,} | {row.record_count:>12,}")
            industry_data.append({
                'industry': row.industry,
                'sector': row.sector,
                'stocks': row.stock_count,
                'records': row.record_count
            })

        report['sections']['industries'] = industry_data
    except Exception as e:
        print(f"  Error: {e}")

    # =========================================================================
    # SECTION 4: Sector Sentiment Summary
    # =========================================================================
    print("\n" + "-" * 80)
    print("[4] SECTOR SENTIMENT SUMMARY (Latest)")
    print("-" * 80)

    sentiment_query = f"""
    SELECT
        sector,
        date,
        ROUND(market_sentiment, 3) as market_sentiment,
        ROUND(fear_greed_index, 1) as fear_greed,
        ROUND(news_sentiment, 3) as news_sentiment,
        news_volume,
        ROUND(positive_news_pct, 1) as positive_pct,
        ROUND(negative_news_pct, 1) as negative_pct
    FROM `{PROJECT_ID}.{ML_DATASET}.sector_sentiment`
    WHERE date = (SELECT MAX(date) FROM `{PROJECT_ID}.{ML_DATASET}.sector_sentiment`)
    ORDER BY market_sentiment DESC
    """

    try:
        results = list(bq_client.query(sentiment_query).result())
        print(f"\n{'Sector':<30} | {'Sentiment':>10} | {'Fear/Greed':>11} | {'News':>10} | {'Pos%':>6} | {'Neg%':>6}")
        print("-" * 90)

        sentiment_data = []
        for row in results:
            sentiment_str = f"{row.market_sentiment:+.3f}"
            print(f"{row.sector:<30} | {sentiment_str:>10} | {row.fear_greed:>11.1f} | {row.news_sentiment:>+10.3f} | {row.positive_pct:>5.1f}% | {row.negative_pct:>5.1f}%")
            sentiment_data.append({
                'sector': row.sector,
                'sentiment': float(row.market_sentiment),
                'fear_greed': float(row.fear_greed),
                'news_sentiment': float(row.news_sentiment),
                'positive_pct': float(row.positive_pct),
                'negative_pct': float(row.negative_pct)
            })

        report['sections']['sentiment'] = sentiment_data
    except Exception as e:
        print(f"  Error: {e}")

    # =========================================================================
    # SECTION 5: Trump/Political Sentiment Impact
    # =========================================================================
    print("\n" + "-" * 80)
    print("[5] TRUMP/POLITICAL SENTIMENT IMPACT")
    print("-" * 80)

    political_query = f"""
    SELECT
        sector,
        ROUND(AVG(trump_mention_impact), 4) as avg_trump_impact,
        ROUND(AVG(political_sentiment), 4) as avg_political_sentiment,
        ROUND(MAX(trump_mention_impact), 4) as max_trump_impact,
        ROUND(MIN(trump_mention_impact), 4) as min_trump_impact
    FROM `{PROJECT_ID}.{ML_DATASET}.sector_sentiment`
    WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    GROUP BY sector
    ORDER BY ABS(avg_trump_impact) DESC
    """

    try:
        results = list(bq_client.query(political_query).result())
        print(f"\n{'Sector':<30} | {'Avg Trump Impact':>16} | {'Political Sent':>14} | {'Max':>10} | {'Min':>10}")
        print("-" * 90)

        political_data = []
        for row in results:
            print(f"{row.sector:<30} | {row.avg_trump_impact:>+16.4f} | {row.avg_political_sentiment:>+14.4f} | {row.max_trump_impact:>+10.4f} | {row.min_trump_impact:>+10.4f}")
            political_data.append({
                'sector': row.sector,
                'avg_trump_impact': float(row.avg_trump_impact or 0),
                'political_sentiment': float(row.avg_political_sentiment or 0),
                'max_impact': float(row.max_trump_impact or 0),
                'min_impact': float(row.min_trump_impact or 0)
            })

        report['sections']['political'] = political_data
    except Exception as e:
        print(f"  Error: {e}")

    # =========================================================================
    # SECTION 6: ML Model Performance Summary
    # =========================================================================
    print("\n" + "-" * 80)
    print("[6] ML MODEL PERFORMANCE (Sector Models)")
    print("-" * 80)

    ml_query = f"""
    SELECT
        sector,
        ROUND(validate_accuracy, 1) as accuracy,
        ROUND(high_conf_accuracy, 1) as high_conf_accuracy,
        validate_records,
        training_date
    FROM `{PROJECT_ID}.{ML_DATASET}.sector_model_results`
    WHERE status = 'ACTIVE'
    ORDER BY validate_accuracy DESC
    """

    try:
        results = list(bq_client.query(ml_query).result())
        if results:
            print(f"\n{'Sector':<30} | {'Accuracy':>10} | {'High-Conf':>10} | {'Records':>12}")
            print("-" * 70)

            ml_data = []
            for row in results:
                status = "GOOD" if row.accuracy >= 55 else "FAIR" if row.accuracy >= 50 else "NEEDS_WORK"
                print(f"{row.sector:<30} | {row.accuracy:>9.1f}% | {row.high_conf_accuracy or 0:>9.1f}% | {row.validate_records:>12,}  [{status}]")
                ml_data.append({
                    'sector': row.sector,
                    'accuracy': float(row.accuracy or 0),
                    'high_conf': float(row.high_conf_accuracy or 0),
                    'records': row.validate_records
                })

            report['sections']['ml_models'] = ml_data
        else:
            print("  No sector models trained yet")
    except Exception as e:
        print(f"  Error: {e}")

    # =========================================================================
    # SECTION 7: Data Quality Alerts
    # =========================================================================
    print("\n" + "-" * 80)
    print("[7] DATA QUALITY ALERTS")
    print("-" * 80)

    alerts = []

    # Check for missing yesterday data
    missing_query = f"""
    SELECT
        asset_type,
        SUM(CASE WHEN DATE(datetime) = CURRENT_DATE() - 1 THEN 1 ELSE 0 END) as yesterday_count
    FROM (
        SELECT datetime, 'stocks' as asset_type FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        UNION ALL
        SELECT datetime, 'crypto' as asset_type FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
    )
    GROUP BY asset_type
    """

    try:
        results = list(bq_client.query(missing_query).result())
        for row in results:
            if row.yesterday_count == 0:
                alert = f"WARNING: No {row.asset_type} data for yesterday!"
                alerts.append(alert)
                print(f"  {alert}")
            elif row.yesterday_count < 50:
                alert = f"WARNING: Low {row.asset_type} data count for yesterday ({row.yesterday_count} records)"
                alerts.append(alert)
                print(f"  {alert}")
    except Exception as e:
        alerts.append(f"Error checking data quality: {e}")

    if not alerts:
        print("  All data quality checks passed!")
        alerts.append("All checks passed")

    report['sections']['alerts'] = alerts

    # =========================================================================
    # Save Report to BigQuery
    # =========================================================================
    print("\n" + "=" * 80)
    print("SAVING REPORT")
    print("=" * 80)

    save_query = f"""
    INSERT INTO `{PROJECT_ID}.{ML_DATASET}.deployment_log`
    (deployment_id, component, component_name, version, status, details)
    VALUES (
        GENERATE_UUID(),
        'DAILY_STATUS_REPORT',
        'enhanced_daily_report',
        '{report_date}',
        'COMPLETED',
        '{json.dumps(report).replace("'", "''")}'
    )
    """

    try:
        bq_client.query(save_query).result()
        print(f"  Report saved to deployment_log")
    except Exception as e:
        print(f"  Error saving report: {e}")

    print("\n" + "=" * 80)
    print("DAILY STATUS REPORT COMPLETE")
    print("=" * 80)
    print(f"Completed: {datetime.now()}")

    return report


if __name__ == "__main__":
    generate_daily_status_report()
