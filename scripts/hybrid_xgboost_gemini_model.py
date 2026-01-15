"""
Hybrid XGBoost + Gemini Ensemble Model for AIAlgoTradeHits.com
Based on: gemini-financial-analysis-modes.html

This model combines:
1. XGBoost for technical indicator-based quantitative predictions
2. Gemini LLM for sentiment analysis and qualitative insights
3. Weighted ensemble for final prediction
"""

from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import json
from datetime import datetime, timedelta
import pickle
import os

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
LOCATION = 'us-central1'
MODEL_DIR = 'C:/1AITrading/Trading/models'

os.makedirs(MODEL_DIR, exist_ok=True)

# Initialize clients
bq_client = bigquery.Client(project=PROJECT_ID)
vertexai.init(project=PROJECT_ID, location=LOCATION)


class HybridTradingModel:
    """Hybrid XGBoost + Gemini ensemble model for trading predictions"""

    def __init__(self, asset_type: str = 'stocks'):
        self.asset_type = asset_type
        self.table = 'stocks_daily_clean' if asset_type == 'stocks' else 'crypto_daily_clean'
        self.xgb_model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        # Use gemini-2.0-flash or fallback
        try:
            self.gemini_model = GenerativeModel("gemini-2.0-flash-001")
        except Exception:
            try:
                self.gemini_model = GenerativeModel("gemini-1.5-pro")
            except Exception:
                self.gemini_model = None

        # Ensemble weights
        self.xgb_weight = 0.6  # Technical analysis weight
        self.gemini_weight = 0.4  # Sentiment/qualitative weight

    def fetch_training_data(self, symbols: list = None, days: int = 365) -> pd.DataFrame:
        """Fetch training data from BigQuery"""

        symbol_filter = ""
        if symbols:
            symbol_list = "', '".join(symbols)
            symbol_filter = f"AND symbol IN ('{symbol_list}')"

        query = f"""
        SELECT
            symbol, datetime,
            open, high, low, close, volume,
            rsi, macd, macd_signal, macd_histogram,
            stoch_k, stoch_d, cci, williams_r, momentum,
            sma_20, sma_50, sma_200, ema_12, ema_26,
            bollinger_upper, bollinger_middle, bollinger_lower, bb_width,
            adx, plus_di, minus_di, atr, obv,
            golden_cross, death_cross, cycle_type, cycle_pnl_pct,
            buy_pressure_pct, sell_pressure_pct,
            hammer, shooting_star, bullish_engulfing, bearish_engulfing, doji,
            trend_regime, vol_regime
        FROM `{PROJECT_ID}.{DATASET_ID}.{self.table}`
        WHERE datetime >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY))
        {symbol_filter}
        AND close IS NOT NULL
        ORDER BY symbol, datetime
        """

        print(f"Fetching training data for {self.asset_type}...")
        df = bq_client.query(query).to_dataframe()
        print(f"  Loaded {len(df):,} records for {df['symbol'].nunique()} symbols")
        return df

    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepare features and targets for XGBoost"""

        # Define core feature columns (most likely to have data)
        self.feature_columns = [
            'rsi', 'macd', 'macd_signal',
            'adx', 'atr',
            'trend_regime', 'cycle_type',
        ]

        # Optional features - add only if they exist and have data
        optional_features = [
            'macd_histogram', 'stoch_k', 'stoch_d', 'cci', 'williams_r', 'momentum',
            'plus_di', 'minus_di', 'bb_width',
            'buy_pressure_pct', 'sell_pressure_pct',
            'vol_regime', 'golden_cross', 'death_cross',
            'hammer', 'shooting_star', 'bullish_engulfing', 'bearish_engulfing', 'doji'
        ]

        for col in optional_features:
            if col in df.columns and df[col].notna().sum() > len(df) * 0.3:  # At least 30% non-null
                self.feature_columns.append(col)

        # Calculate target: next day direction (1 = up, 0 = down/flat)
        df = df.copy()
        df = df.sort_values(['symbol', 'datetime'])
        df['next_close'] = df.groupby('symbol')['close'].shift(-1)
        df['target'] = (df['next_close'] > df['close']).astype(int)

        # Add derived features only if source columns exist
        if 'sma_20' in df.columns and df['sma_20'].notna().sum() > 0:
            df['price_vs_sma20'] = (df['close'] - df['sma_20']) / df['sma_20'].replace(0, np.nan) * 100
            self.feature_columns.append('price_vs_sma20')

        if 'sma_50' in df.columns and df['sma_50'].notna().sum() > 0:
            df['price_vs_sma50'] = (df['close'] - df['sma_50']) / df['sma_50'].replace(0, np.nan) * 100
            self.feature_columns.append('price_vs_sma50')

        if 'macd_histogram' in df.columns:
            df['macd_histogram_change'] = df.groupby('symbol')['macd_histogram'].diff()
            if df['macd_histogram_change'].notna().sum() > len(df) * 0.3:
                self.feature_columns.append('macd_histogram_change')

        if 'rsi' in df.columns:
            df['rsi_change'] = df.groupby('symbol')['rsi'].diff()
            if df['rsi_change'].notna().sum() > len(df) * 0.3:
                self.feature_columns.append('rsi_change')

        # Volume ratio
        df['volume_ratio'] = df['volume'] / df.groupby('symbol')['volume'].transform(
            lambda x: x.rolling(20, min_periods=1).mean()
        )
        if df['volume_ratio'].notna().sum() > len(df) * 0.3:
            self.feature_columns.append('volume_ratio')

        # Remove duplicates
        self.feature_columns = list(dict.fromkeys(self.feature_columns))

        # Fill NA values with 0 for feature columns
        for col in self.feature_columns:
            if col in df.columns:
                df[col] = df[col].fillna(0)

        # Only require target to be non-null
        df = df.dropna(subset=['target'])

        # Make sure we have at least some features
        available_features = [col for col in self.feature_columns if col in df.columns]
        self.feature_columns = available_features

        X = df[self.feature_columns].fillna(0)
        y = df['target']

        print(f"  Features used: {len(self.feature_columns)}")
        print(f"  Feature columns: {self.feature_columns[:10]}...")

        return X, y, df

    def train_xgboost(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train XGBoost model with time-series cross-validation"""

        print("\nTraining XGBoost model...")

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Time series split for validation
        tscv = TimeSeriesSplit(n_splits=5)
        scores = []

        for train_idx, val_idx in tscv.split(X_scaled):
            X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            # Train model
            model = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                objective='binary:logistic',
                eval_metric='logloss',
                random_state=42
            )

            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                verbose=False
            )

            # Evaluate
            y_pred = model.predict(X_val)
            accuracy = accuracy_score(y_val, y_pred)
            scores.append(accuracy)

        # Train final model on all data
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='binary:logistic',
            eval_metric='logloss',
            random_state=42
        )
        self.xgb_model.fit(X_scaled, y, verbose=False)

        # Get feature importance
        importance = dict(zip(self.feature_columns, self.xgb_model.feature_importances_))
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

        results = {
            'cv_accuracy': np.mean(scores),
            'cv_std': np.std(scores),
            'feature_importance': importance
        }

        print(f"  Cross-validation accuracy: {results['cv_accuracy']:.4f} (+/- {results['cv_std']:.4f})")
        print(f"  Top 5 features: {list(importance.keys())[:5]}")

        return results

    def get_xgb_prediction(self, features: pd.DataFrame) -> dict:
        """Get XGBoost prediction with probability"""

        if self.xgb_model is None:
            return {'direction': 'NEUTRAL', 'probability': 0.5, 'confidence': 'LOW'}

        X_scaled = self.scaler.transform(features)
        proba = self.xgb_model.predict_proba(X_scaled)[0]

        # Class 1 = UP, Class 0 = DOWN
        up_prob = proba[1]
        down_prob = proba[0]

        if up_prob > 0.6:
            direction = 'UP'
            confidence = 'HIGH' if up_prob > 0.7 else 'MEDIUM'
        elif down_prob > 0.6:
            direction = 'DOWN'
            confidence = 'HIGH' if down_prob > 0.7 else 'MEDIUM'
        else:
            direction = 'NEUTRAL'
            confidence = 'LOW'

        return {
            'direction': direction,
            'up_probability': float(up_prob),
            'down_probability': float(down_prob),
            'confidence': confidence
        }

    def get_gemini_analysis(self, symbol: str, market_data: dict) -> dict:
        """Get Gemini LLM analysis for qualitative insights"""

        prompt = f"""You are a professional financial analyst. Analyze the following market data for {symbol} and provide a trading prediction.

CURRENT MARKET DATA:
- Price: ${market_data.get('close', 0):.2f}
- RSI: {market_data.get('rsi', 50):.1f}
- MACD: {market_data.get('macd', 0):.4f} (Signal: {market_data.get('macd_signal', 0):.4f})
- ADX: {market_data.get('adx', 0):.1f}
- Trend Regime: {market_data.get('trend_regime', 0)} (1=bullish, -1=bearish, 0=neutral)
- Buy Pressure: {market_data.get('buy_pressure_pct', 50):.1f}%
- Sell Pressure: {market_data.get('sell_pressure_pct', 50):.1f}%
- Golden Cross: {market_data.get('golden_cross', 0)}
- Death Cross: {market_data.get('death_cross', 0)}

Respond in JSON format:
{{
    "direction": "UP" or "DOWN" or "NEUTRAL",
    "confidence": "HIGH" or "MEDIUM" or "LOW",
    "reasoning": "Brief explanation",
    "risk_level": "HIGH" or "MEDIUM" or "LOW",
    "key_factors": ["factor1", "factor2", "factor3"]
}}
"""

        try:
            response = self.gemini_model.generate_content(prompt)
            text = response.text.strip()

            # Parse JSON from response
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]

            result = json.loads(text)
            return result

        except Exception as e:
            print(f"  Gemini analysis error: {e}")
            return {
                'direction': 'NEUTRAL',
                'confidence': 'LOW',
                'reasoning': 'Unable to analyze',
                'risk_level': 'HIGH',
                'key_factors': []
            }

    def ensemble_prediction(self, xgb_pred: dict, gemini_pred: dict) -> dict:
        """Combine XGBoost and Gemini predictions with weighted ensemble"""

        # Convert directions to numeric scores
        direction_scores = {'UP': 1, 'NEUTRAL': 0, 'DOWN': -1}
        confidence_weights = {'HIGH': 1.0, 'MEDIUM': 0.7, 'LOW': 0.4}

        # XGBoost score
        xgb_score = direction_scores.get(xgb_pred['direction'], 0)
        xgb_conf = xgb_pred.get('up_probability', 0.5)
        if xgb_pred['direction'] == 'DOWN':
            xgb_conf = xgb_pred.get('down_probability', 0.5)

        # Gemini score
        gemini_score = direction_scores.get(gemini_pred['direction'], 0)
        gemini_conf = confidence_weights.get(gemini_pred['confidence'], 0.5)

        # Weighted ensemble
        ensemble_score = (
            self.xgb_weight * xgb_score * xgb_conf +
            self.gemini_weight * gemini_score * gemini_conf
        )

        # Determine final direction
        if ensemble_score > 0.2:
            final_direction = 'UP'
        elif ensemble_score < -0.2:
            final_direction = 'DOWN'
        else:
            final_direction = 'NEUTRAL'

        # Calculate confidence
        total_conf = (self.xgb_weight * xgb_conf + self.gemini_weight * gemini_conf)
        if total_conf > 0.7:
            final_confidence = 'HIGH'
        elif total_conf > 0.5:
            final_confidence = 'MEDIUM'
        else:
            final_confidence = 'LOW'

        return {
            'direction': final_direction,
            'confidence': final_confidence,
            'ensemble_score': float(ensemble_score),
            'xgb_prediction': xgb_pred,
            'gemini_prediction': gemini_pred,
            'weights': {
                'xgb': self.xgb_weight,
                'gemini': self.gemini_weight
            }
        }

    def predict(self, symbol: str) -> dict:
        """Get full prediction for a symbol"""

        # Fetch recent data for derived feature calculation
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{self.table}`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT 30
        """

        df = bq_client.query(query).to_dataframe()

        if df.empty:
            return {'error': f'No data found for {symbol}'}

        # Sort by datetime ascending for proper calculations
        df = df.sort_values('datetime')

        row = df.iloc[-1]  # Latest row
        market_data = row.to_dict()

        # Calculate derived features if needed
        if 'price_vs_sma20' in self.feature_columns and 'sma_20' in df.columns:
            df['price_vs_sma20'] = (df['close'] - df['sma_20']) / df['sma_20'].replace(0, np.nan) * 100
        if 'price_vs_sma50' in self.feature_columns and 'sma_50' in df.columns:
            df['price_vs_sma50'] = (df['close'] - df['sma_50']) / df['sma_50'].replace(0, np.nan) * 100
        if 'macd_histogram_change' in self.feature_columns and 'macd_histogram' in df.columns:
            df['macd_histogram_change'] = df['macd_histogram'].diff()
        if 'rsi_change' in self.feature_columns and 'rsi' in df.columns:
            df['rsi_change'] = df['rsi'].diff()
        if 'volume_ratio' in self.feature_columns and 'volume' in df.columns:
            df['volume_ratio'] = df['volume'] / df['volume'].rolling(20, min_periods=1).mean()

        # Use only available feature columns
        available_features = [col for col in self.feature_columns if col in df.columns]
        features = df[available_features].iloc[[-1]].fillna(0)

        # Pad missing features with zeros
        for col in self.feature_columns:
            if col not in features.columns:
                features[col] = 0

        # Ensure column order matches training
        features = features[self.feature_columns]

        # Get predictions
        xgb_pred = self.get_xgb_prediction(features)
        gemini_pred = self.get_gemini_analysis(symbol, market_data)

        # Combine predictions
        result = self.ensemble_prediction(xgb_pred, gemini_pred)

        # Add metadata
        result['symbol'] = symbol
        result['timestamp'] = datetime.now().isoformat()
        result['latest_price'] = float(row['close']) if pd.notna(row['close']) else None
        result['latest_date'] = row['datetime'].isoformat() if hasattr(row['datetime'], 'isoformat') else str(row['datetime'])

        return result

    def save_model(self, path: str = None):
        """Save trained model to disk"""

        if path is None:
            path = os.path.join(MODEL_DIR, f'hybrid_model_{self.asset_type}.pkl')

        model_data = {
            'xgb_model': self.xgb_model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'asset_type': self.asset_type,
            'weights': {
                'xgb': self.xgb_weight,
                'gemini': self.gemini_weight
            },
            'saved_at': datetime.now().isoformat()
        }

        with open(path, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"Model saved to: {path}")

    def load_model(self, path: str = None):
        """Load trained model from disk"""

        if path is None:
            path = os.path.join(MODEL_DIR, f'hybrid_model_{self.asset_type}.pkl')

        with open(path, 'rb') as f:
            model_data = pickle.load(f)

        self.xgb_model = model_data['xgb_model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.xgb_weight = model_data['weights']['xgb']
        self.gemini_weight = model_data['weights']['gemini']

        print(f"Model loaded from: {path}")


def train_and_evaluate_model(asset_type: str = 'stocks'):
    """Train and evaluate hybrid model"""

    print("=" * 80)
    print(f"TRAINING HYBRID XGBOOST + GEMINI MODEL FOR {asset_type.upper()}")
    print("=" * 80)
    print(f"Started: {datetime.now()}")

    # Initialize model
    model = HybridTradingModel(asset_type=asset_type)

    # Fetch training data
    if asset_type == 'stocks':
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META',
                   'SPY', 'QQQ', 'JPM', 'V', 'MA']
    else:
        symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'ADA/USD', 'DOGE/USD']

    df = model.fetch_training_data(symbols=symbols, days=365)

    # Prepare features
    X, y, df_processed = model.prepare_features(df)
    print(f"\nPrepared {len(X):,} training samples with {len(model.feature_columns)} features")

    # Train XGBoost
    xgb_results = model.train_xgboost(X, y)

    # Save model
    model.save_model()

    # Test prediction on a few symbols
    print("\n--- SAMPLE PREDICTIONS ---")
    test_symbols = symbols[:3]

    for symbol in test_symbols:
        print(f"\n{symbol}:")
        prediction = model.predict(symbol)

        if 'error' in prediction:
            print(f"  Error: {prediction['error']}")
        else:
            print(f"  Direction: {prediction['direction']} ({prediction['confidence']} confidence)")
            print(f"  Ensemble Score: {prediction['ensemble_score']:.4f}")
            print(f"  XGBoost: {prediction['xgb_prediction']['direction']}")
            print(f"  Gemini: {prediction['gemini_prediction']['direction']}")
            if prediction['gemini_prediction'].get('reasoning'):
                print(f"  Reasoning: {prediction['gemini_prediction']['reasoning'][:100]}...")

    # Summary
    print("\n" + "=" * 80)
    print("TRAINING SUMMARY")
    print("=" * 80)
    print(f"Asset type: {asset_type}")
    print(f"Training samples: {len(X):,}")
    print(f"XGBoost CV Accuracy: {xgb_results['cv_accuracy']:.4f}")
    print(f"Top features: {list(xgb_results['feature_importance'].keys())[:5]}")
    print(f"Model saved to: {MODEL_DIR}/hybrid_model_{asset_type}.pkl")
    print(f"Completed: {datetime.now()}")

    return model, xgb_results


def main():
    """Main function to train both stock and crypto models"""

    # Train stock model
    stock_model, stock_results = train_and_evaluate_model('stocks')

    print("\n")

    # Train crypto model
    crypto_model, crypto_results = train_and_evaluate_model('crypto')

    # Save results summary
    summary = {
        'stocks': {
            'cv_accuracy': stock_results['cv_accuracy'],
            'cv_std': stock_results['cv_std'],
            'top_features': list(stock_results['feature_importance'].keys())[:10]
        },
        'crypto': {
            'cv_accuracy': crypto_results['cv_accuracy'],
            'cv_std': crypto_results['cv_std'],
            'top_features': list(crypto_results['feature_importance'].keys())[:10]
        },
        'trained_at': datetime.now().isoformat()
    }

    with open(os.path.join(MODEL_DIR, 'training_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 80)
    print("ALL MODELS TRAINED SUCCESSFULLY")
    print("=" * 80)
    print(f"Models saved in: {MODEL_DIR}")
    print("Files created:")
    print("  - hybrid_model_stocks.pkl")
    print("  - hybrid_model_crypto.pkl")
    print("  - training_summary.json")


if __name__ == "__main__":
    main()
