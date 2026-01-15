# AI Training Data Documentation for Vertex AI and Gemini 3

## Overview

This document describes the comprehensive historical data warehouse built for developing Fintech AI models using Google Cloud Vertex AI and Gemini 3 technology.

## Data Summary

### Assets Collected

| Symbol | Asset Type | Records | Date Range | Description |
|--------|-----------|---------|------------|-------------|
| BTC/USD | Crypto | 4,086 | ~11 years | Bitcoin - Most traded cryptocurrency |
| NVDA | Stock | 5,000 | ~20 years | NVIDIA - AI/GPU leader stock |

### Storage Locations

**BigQuery Tables:**
- `cryptobot-462709.crypto_trading_data.btc_ai_training_daily`
- `cryptobot-462709.crypto_trading_data.nvda_ai_training_daily`

**Local CSV Files:**
- `btc_training_data.csv`
- `nvda_training_data.csv`

## Technical Indicators (50+ Features)

### Trend Indicators
| Feature | Description | Formula/Period |
|---------|-------------|----------------|
| sma_5 | Simple Moving Average | 5-day |
| sma_10 | Simple Moving Average | 10-day |
| sma_20 | Simple Moving Average | 20-day |
| sma_50 | Simple Moving Average | 50-day |
| sma_100 | Simple Moving Average | 100-day |
| sma_200 | Simple Moving Average | 200-day |
| ema_5 | Exponential Moving Average | 5-day |
| ema_10 | Exponential Moving Average | 10-day |
| ema_12 | Exponential Moving Average | 12-day |
| ema_20 | Exponential Moving Average | 20-day |
| ema_26 | Exponential Moving Average | 26-day |
| ema_50 | Exponential Moving Average | 50-day |

### MACD Family
| Feature | Description |
|---------|-------------|
| macd | MACD Line (EMA12 - EMA26) |
| macd_signal | Signal Line (9-day EMA of MACD) |
| macd_hist | MACD Histogram (MACD - Signal) |

### RSI Family
| Feature | Description |
|---------|-------------|
| rsi_7 | Relative Strength Index (7-day) |
| rsi_14 | Relative Strength Index (14-day) |
| rsi_21 | Relative Strength Index (21-day) |

### Stochastic Oscillator
| Feature | Description |
|---------|-------------|
| stoch_k | Stochastic %K (14-day) |
| stoch_d | Stochastic %D (3-day SMA of %K) |
| stoch_rsi | Stochastic RSI |

### Bollinger Bands
| Feature | Description |
|---------|-------------|
| bb_upper | Upper Band (SMA20 + 2*StdDev) |
| bb_middle | Middle Band (20-day SMA) |
| bb_lower | Lower Band (SMA20 - 2*StdDev) |
| bb_width | Band Width Percentage |
| bb_percent | %B (Price position within bands) |

### Volatility Indicators
| Feature | Description |
|---------|-------------|
| atr_7 | Average True Range (7-day) |
| atr_14 | Average True Range (14-day) |
| atr_percent | ATR as percentage of price |
| volatility_10 | 10-day annualized volatility |
| volatility_20 | 20-day annualized volatility |

### Momentum Indicators
| Feature | Description |
|---------|-------------|
| roc_5 | Rate of Change (5-day) |
| roc_10 | Rate of Change (10-day) |
| roc_20 | Rate of Change (20-day) |
| momentum_10 | Price Momentum (10-day) |
| williams_r | Williams %R (14-day) |

### Volume Indicators
| Feature | Description |
|---------|-------------|
| obv | On Balance Volume |
| volume_sma_20 | Volume 20-day SMA |
| volume_ratio | Current volume / 20-day average |

### Oscillators
| Feature | Description |
|---------|-------------|
| cci | Commodity Channel Index (20-day) |
| ppo | Percentage Price Oscillator |
| ultimate_osc | Ultimate Oscillator (7/14/28) |
| awesome_osc | Awesome Oscillator |
| adx | Average Directional Index |
| di_plus | Positive Directional Indicator |
| di_minus | Negative Directional Indicator |

### Price Action Features
| Feature | Description |
|---------|-------------|
| daily_return_pct | Daily return percentage |
| log_return | Logarithmic return |
| high_low_pct | High-Low range as % of close |
| body_size | Candlestick body size |
| upper_shadow | Upper shadow length |
| lower_shadow | Lower shadow length |

### Lagged Features (Time Series)
| Feature | Description |
|---------|-------------|
| close_lag_1 | Close price 1 day ago |
| close_lag_2 | Close price 2 days ago |
| close_lag_3 | Close price 3 days ago |
| close_lag_5 | Close price 5 days ago |
| close_lag_10 | Close price 10 days ago |
| return_lag_1 | Return 1 day ago |
| return_lag_2 | Return 2 days ago |
| return_lag_3 | Return 3 days ago |

### Target Variables (For Supervised Learning)
| Feature | Description |
|---------|-------------|
| target_return_1d | Next day return (%) |
| target_return_5d | 5-day future return (%) |
| target_return_10d | 10-day future return (%) |
| target_direction_1d | 1 = up, 0 = down (next day) |
| target_direction_5d | 1 = up, 0 = down (5-day) |

### Signal Categories
| Feature | Values |
|---------|--------|
| trend_signal | strong_bullish, bullish, neutral, bearish, strong_bearish |
| momentum_signal | overbought, bullish, bearish, oversold |
| volatility_signal | high, normal, low |
| volume_signal | high, normal, low |

### Time Features
| Feature | Description |
|---------|-------------|
| day_of_week | 0-6 (Monday-Sunday) |
| month | 1-12 |
| quarter | 1-4 |
| is_month_start | True if day <= 3 |
| is_month_end | True if day >= 28 |

## Usage with Vertex AI

### 1. Loading Data from BigQuery

```python
from google.cloud import bigquery

client = bigquery.Client(project='cryptobot-462709')

# Load BTC training data
query = """
SELECT *
FROM `cryptobot-462709.crypto_trading_data.btc_ai_training_daily`
ORDER BY date
"""
btc_df = client.query(query).to_dataframe()

# Load NVDA training data
query = """
SELECT *
FROM `cryptobot-462709.crypto_trading_data.nvda_ai_training_daily`
ORDER BY date
"""
nvda_df = client.query(query).to_dataframe()
```

### 2. Vertex AI AutoML Training

```python
from google.cloud import aiplatform

# Initialize Vertex AI
aiplatform.init(project='cryptobot-462709', location='us-central1')

# Create dataset from BigQuery
dataset = aiplatform.TabularDataset.create(
    display_name='btc_price_prediction',
    bq_source='bq://cryptobot-462709.crypto_trading_data.btc_ai_training_daily'
)

# Train AutoML model
job = aiplatform.AutoMLTabularTrainingJob(
    display_name='btc_direction_predictor',
    optimization_prediction_type='classification',
    column_transformations=[
        {'numeric': {'column_name': 'rsi_14'}},
        {'numeric': {'column_name': 'macd'}},
        {'numeric': {'column_name': 'bb_percent'}},
        # Add more features...
    ]
)

model = job.run(
    dataset=dataset,
    target_column='target_direction_1d',
    training_fraction_split=0.8,
    validation_fraction_split=0.1,
    test_fraction_split=0.1
)
```

### 3. Custom TensorFlow Model

```python
import tensorflow as tf
import pandas as pd

# Feature columns for training
feature_columns = [
    'sma_20', 'sma_50', 'sma_200',
    'ema_12', 'ema_26',
    'rsi_14', 'macd', 'macd_signal',
    'bb_percent', 'bb_width',
    'atr_percent', 'volatility_20',
    'stoch_k', 'stoch_d',
    'cci', 'ppo',
    'volume_ratio',
    'close_lag_1', 'close_lag_2', 'close_lag_3'
]

# Prepare data
X = btc_df[feature_columns].dropna()
y = btc_df.loc[X.index, 'target_direction_1d']

# Build LSTM model for time series
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(128, return_sequences=True, input_shape=(30, len(feature_columns))),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)
```

### 4. Gemini 3 Integration

```python
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize Vertex AI
vertexai.init(project='cryptobot-462709', location='us-central1')

# Load Gemini model
model = GenerativeModel('gemini-1.5-pro')

# Example: Use Gemini for market analysis
prompt = f"""
Analyze the following Bitcoin technical indicators and provide trading insights:

RSI: {btc_df.iloc[-1]['rsi_14']:.2f}
MACD: {btc_df.iloc[-1]['macd']:.2f}
MACD Signal: {btc_df.iloc[-1]['macd_signal']:.2f}
Bollinger %B: {btc_df.iloc[-1]['bb_percent']:.2f}%
ATR%: {btc_df.iloc[-1]['atr_percent']:.2f}%
Trend: {btc_df.iloc[-1]['trend_signal']}
Momentum: {btc_df.iloc[-1]['momentum_signal']}

Provide:
1. Current market sentiment
2. Key support/resistance levels
3. Trading recommendation
4. Risk assessment
"""

response = model.generate_content(prompt)
print(response.text)
```

## Model Use Cases

### 1. Price Direction Classification
- **Target:** `target_direction_1d` or `target_direction_5d`
- **Features:** All technical indicators
- **Model:** Random Forest, XGBoost, or Neural Network
- **Metric:** Accuracy, F1-Score, AUC-ROC

### 2. Price Regression
- **Target:** `target_return_1d`, `target_return_5d`, `target_return_10d`
- **Features:** All technical indicators + lagged features
- **Model:** LSTM, Transformer, or Gradient Boosting
- **Metric:** RMSE, MAE, R-squared

### 3. Volatility Prediction
- **Target:** Future `volatility_20` or `atr_percent`
- **Features:** Historical volatility, volume, price action
- **Model:** GARCH, LSTM
- **Use Case:** Options pricing, risk management

### 4. Pattern Recognition
- **Input:** OHLCV + candlestick features
- **Model:** CNN or Vision Transformer
- **Use Case:** Chart pattern detection (head & shoulders, triangles)

### 5. Anomaly Detection
- **Features:** All indicators
- **Model:** Autoencoder, Isolation Forest
- **Use Case:** Detect unusual market conditions

## Data Quality Notes

1. **BTC Data:** Starts from 2013, may have gaps during exchange downtime
2. **NVDA Data:** 20 years of stock market data (trading days only)
3. **Missing Values:** Some indicators require minimum data (e.g., SMA200 needs 200 days)
4. **Volume:** Crypto volume is 24/7, stock volume is trading hours only

## Daily Update Script

Run `fetch_btc_nvda_ai_training_data.py` to update with latest data:

```bash
cd Trading
python fetch_btc_nvda_ai_training_data.py
```

## Cost Considerations

- **Twelve Data API:** Free tier allows 800 calls/day
- **BigQuery Storage:** ~$0.02/GB/month
- **Vertex AI Training:** Varies by model type and compute
- **Gemini API:** Pay-per-token pricing

## Next Steps

1. **Expand Data:** Add more assets (ETH, AAPL, SPY)
2. **Feature Engineering:** Add sentiment data, on-chain metrics
3. **Model Training:** Start with AutoML, then custom models
4. **Backtesting:** Build evaluation framework
5. **Production:** Deploy models to Cloud Run endpoints
