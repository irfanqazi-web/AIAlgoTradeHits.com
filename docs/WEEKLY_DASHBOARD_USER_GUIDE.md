# Weekly Dashboard User Guide

## Overview

The Weekly Dashboard provides a comprehensive view of all 6 asset types in a single unified interface. This dashboard is designed for investors and traders who want to quickly assess market conditions across multiple asset classes on a weekly basis.

## Asset Types Covered

### 1. Stocks (US Equities)
- **Coverage**: S&P 500 components, market cap weighted
- **Total Symbols**: 500+ US stocks
- **Key Metrics**: Price, weekly change %, volume, market cap, sector
- **Data Source**: Twelve Data API

### 2. Cryptocurrencies
- **Coverage**: Top 100 cryptocurrencies by market cap
- **Total Symbols**: 100 crypto pairs (vs USD)
- **Key Metrics**: Price, 24h change, 7d change, market cap, volume
- **Data Source**: Twelve Data API

### 3. ETFs (Exchange-Traded Funds)
- **Coverage**: Major US ETFs across all sectors
- **Total Symbols**: 100+ ETFs
- **Key Metrics**: Price, weekly change, AUM, expense ratio, category
- **Data Source**: Twelve Data API

### 4. Forex (Currency Pairs)
- **Coverage**: Major and minor currency pairs
- **Total Symbols**: 30+ forex pairs
- **Key Metrics**: Price, daily change, bid/ask spread, pip value
- **Data Source**: Twelve Data API

### 5. Indices (Market Indices)
- **Coverage**: Global market indices
- **Total Symbols**: 20+ indices
- **Key Metrics**: Price, daily change, 52-week high/low
- **Includes**: S&P 500, NASDAQ, DOW, Russell 2000, VIX

### 6. Commodities
- **Coverage**: Precious metals, energy, agriculture
- **Total Symbols**: 18 commodities
- **Key Metrics**: Price, daily change, contract specs
- **Categories**: Metals, Energy, Grains, Soft commodities

## Dashboard Layout

### Top Section: Asset Type Selector
Six clickable tabs at the top allow instant switching between asset types:

```
[Stocks] [Cryptos] [ETFs] [Forex] [Indices] [Commodities]
```

### Middle Section: Summary Cards
Quick statistics for the selected asset type:
- **Total Assets**: Number of tracked instruments
- **Top Gainer**: Best performing asset this week
- **Top Loser**: Worst performing asset this week
- **Average Change**: Market-wide performance indicator

### Main Section: Data Table
Sortable, filterable table with columns:

| Column | Description |
|--------|-------------|
| Symbol | Ticker symbol |
| Name | Full asset name |
| Price | Current price |
| Change % | Weekly percentage change |
| Volume | Trading volume |
| High/Low | 52-week or 7-day range |
| Trend | Visual trend indicator |
| Action | Quick action buttons |

### Bottom Section: Mini Chart
Click any row to display a mini price chart showing:
- 7-day price history
- Volume bars
- Key support/resistance levels

## Navigation Guide

### Accessing the Weekly Dashboard
1. Log in to the trading application
2. Click "Weekly" in the left navigation menu
3. Or navigate to "Analysis" > "Weekly Dashboard"

### Filtering Data
- **Search**: Type in the search box to filter by symbol or name
- **Sort**: Click any column header to sort ascending/descending
- **Category Filter**: Use dropdown to filter by sector/category

### Time Period Selection
- **1 Week**: Default view showing weekly data
- **1 Month**: Monthly comparison view
- **YTD**: Year-to-date performance
- **1 Year**: 52-week performance data

## Technical Indicators Available

Each asset displays calculated technical indicators:

### Trend Indicators
- SMA (20, 50, 200-day)
- EMA (12, 26-day)
- MACD with Signal Line
- ADX (Average Directional Index)

### Momentum Indicators
- RSI (14-day)
- Stochastic Oscillator
- Williams %R
- Rate of Change (ROC)

### Volatility Indicators
- Bollinger Bands (20, 2)
- ATR (14-day)
- Standard Deviation

### Volume Indicators
- OBV (On Balance Volume)
- Volume Moving Average
- Volume Ratio

## Signal Categories

The dashboard provides categorical signals for quick analysis:

### Trend Signal
| Signal | Meaning |
|--------|---------|
| Strong Bullish | Price > SMA50 > SMA200, strong uptrend |
| Bullish | Price above SMA50, moderate uptrend |
| Neutral | Price near moving averages |
| Bearish | Price below SMA50, downtrend |
| Strong Bearish | Price < SMA50 < SMA200, strong downtrend |

### Momentum Signal
| Signal | RSI Range | Meaning |
|--------|-----------|---------|
| Overbought | > 70 | Potential reversal down |
| Bullish | 50-70 | Positive momentum |
| Bearish | 30-50 | Negative momentum |
| Oversold | < 30 | Potential reversal up |

### Volatility Signal
| Signal | Threshold | Meaning |
|--------|-----------|---------|
| High | > 40% annualized | High risk/opportunity |
| Normal | 20-40% | Standard market conditions |
| Low | < 20% | Low volatility, consolidation |

## Data Refresh Schedule

### Automated Updates
- **Weekly Summary**: Every Saturday at 6:30 AM ET
- **Stocks**: Saturday at 6:00 AM ET
- **Cryptos**: Saturday at 6:30 AM ET
- **ETFs**: Saturday at 6:15 AM ET
- **Forex**: Saturday at 6:00 AM ET
- **Indices**: Saturday at 6:15 AM ET
- **Commodities**: Saturday at 6:30 AM ET

### Manual Refresh
Click the refresh icon in the top-right corner to fetch latest data.

## BigQuery Data Storage

All weekly data is stored in Google BigQuery for analysis:

### Table Structure
```
Project: cryptobot-462709
Dataset: crypto_trading_data

Tables:
- stocks_weekly_summary
- cryptos_weekly_summary
- etfs_weekly_summary
- forex_weekly_summary
- indices_weekly_summary
- commodities_weekly_summary
```

### Schema Fields
Each weekly summary table contains 40+ fields including:
- Basic OHLCV data
- Technical indicators
- Signal categories
- Performance metrics
- Metadata (fetch timestamp, data source)

## Export Options

### Download Data
- **CSV Export**: Download current view as CSV
- **Excel Export**: Download with formatting
- **JSON Export**: Raw data for API integration

### Share View
- **Copy Link**: Share current filtered view
- **Email Report**: Send weekly summary email
- **PDF Report**: Generate formatted PDF report

## Troubleshooting

### Common Issues

**No Data Displayed**
- Check your internet connection
- Verify API status in Admin Panel
- Wait for scheduled data refresh

**Stale Data**
- Click manual refresh button
- Check Cloud Scheduler status
- Verify Cloud Function logs

**Slow Loading**
- Reduce number of visible columns
- Use search filter to narrow results
- Check browser performance

### Support Contacts
- Technical Issues: Check admin panel
- API Issues: Review Twelve Data status
- Feature Requests: Contact development team

## Best Practices

### Weekly Analysis Workflow
1. **Monday Review**: Check weekend data updates
2. **Compare Sectors**: Use asset type tabs to compare
3. **Identify Trends**: Look for strong bullish/bearish signals
4. **Set Alerts**: Configure price alerts for opportunities
5. **Document Insights**: Export findings for records

### Risk Management
- Never rely solely on automated signals
- Always verify data quality before trading
- Use multiple timeframes for confirmation
- Set stop-loss levels based on ATR

## API Endpoints

### Weekly Summary API
```
GET /api/weekly/{asset_type}
```

Parameters:
- `asset_type`: stocks, cryptos, etfs, forex, indices, commodities
- `limit`: Number of records (default: 100)
- `sort`: Sort field (default: weekly_change_percent)
- `order`: asc or desc (default: desc)

### Example Response
```json
{
  "status": "success",
  "asset_type": "stocks",
  "count": 100,
  "data": [
    {
      "symbol": "NVDA",
      "name": "NVIDIA Corporation",
      "current_price": 500.25,
      "weekly_change_percent": 5.42,
      "rsi_weekly": 65.3,
      "trend_signal": "bullish",
      "momentum_signal": "bullish"
    }
  ]
}
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Nov 2025 | Initial release with 6 asset types |
| 1.1 | Nov 2025 | Added 50+ technical indicators |
| 1.2 | Nov 2025 | BigQuery historical data integration |

## Related Documentation

- AI Training Data Documentation
- Technical Indicators Reference
- API Documentation
- Cloud Function Deployment Guide
- Admin Panel User Guide
