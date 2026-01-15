"""
AI Trading Intelligence Service - Google Cloud AI Integration
Comprehensive AI features for AIAlgoTradeHits Trading Platform

Integrates:
- Vertex AI for ML model training and predictions
- Gemini 2.5 Pro for conversational AI and market analysis
- Text-to-SQL for natural language trading queries
- Predictive signals generation

Author: Claude Code
Date: December 2025
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Vertex AI SDK
import vertexai
from vertexai.generative_models import GenerativeModel

# Try to import GenerationConfig, fall back to None if not available
try:
    from vertexai.generative_models import GenerationConfig
except ImportError:
    GenerationConfig = None

# BigQuery
from google.cloud import bigquery

# Configuration
PROJECT_ID = 'aialgotradehits'
LOCATION = 'us-central1'
DATASET_ID = 'crypto_trading_data'

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Model Configuration - Use models verified working in production
MODELS = {
    'gemini_pro': 'gemini-2.5-pro',           # Primary model for complex analysis
    'gemini_flash': 'gemini-2.5-flash',       # Fast responses
    'gemini_fallback': 'gemini-1.5-flash',    # Fallback
}

# Clean table mappings
CLEAN_TABLES = {
    'stocks_daily_clean': {
        'description': 'Daily stock price data with 97 fields including OHLCV and 30+ technical indicators (Saleem corrections applied)',
        'asset_type': 'stocks',
        'key_columns': ['symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume', 'rsi', 'macd', 'macd_signal', 'adx', 'atr', 'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'bollinger_upper', 'bollinger_lower', 'stoch_k', 'stoch_d', 'cci', 'williams_r', 'obv', 'mfi']
    },
    'crypto_daily_clean': {
        'description': 'Daily cryptocurrency data with 97 fields and technical indicators',
        'asset_type': 'crypto',
        'key_columns': ['symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume', 'rsi', 'macd', 'adx', 'atr']
    },
    'etfs_daily_clean': {
        'description': 'Daily ETF data with technical indicators',
        'asset_type': 'etfs',
        'key_columns': ['symbol', 'datetime', 'close', 'volume', 'rsi', 'macd', 'adx']
    },
    'forex_daily_clean': {
        'description': 'Daily forex pair data (no volume)',
        'asset_type': 'forex',
        'key_columns': ['symbol', 'datetime', 'close', 'rsi', 'macd', 'atr']
    },
    'indices_daily_clean': {
        'description': 'Daily market index data',
        'asset_type': 'indices',
        'key_columns': ['symbol', 'datetime', 'close', 'rsi', 'macd', 'adx']
    },
    'commodities_daily_clean': {
        'description': 'Daily commodity data',
        'asset_type': 'commodities',
        'key_columns': ['symbol', 'datetime', 'close', 'rsi', 'macd', 'atr']
    }
}

# Trading terminology for AI understanding
TRADING_CONTEXT = """
TRADING TERMINOLOGY:
- "oversold" = RSI < 30 (potential buy signal)
- "overbought" = RSI > 70 (potential sell signal)
- "strong trend" = ADX > 25
- "weak trend" = ADX < 20
- "bullish MACD" = MACD > MACD_SIGNAL and MACD > 0
- "bearish MACD" = MACD < MACD_SIGNAL and MACD < 0
- "golden cross" = SMA_50 > SMA_200 (bullish)
- "death cross" = SMA_50 < SMA_200 (bearish)
- "volatility squeeze" = Bollinger Band width narrowing (bb_width < 0.1)
- "breakout" = Close > Bollinger Upper
- "breakdown" = Close < Bollinger Lower

INDICATOR FORMULAS (Saleem's Corrections):
- RSI: Wilder's RMA with alpha=1/14, period=14
- Stochastic: Slow Stochastic (14,3,3) - %K smoothed with SMA(3)
- ROC: 10-period Rate of Change
- Bollinger: Population std dev (ddof=0), 20 periods, 2 std devs
- ATR: Wilder's RMA with alpha=1/14
- ADX: Wilder's smoothing for DI+, DI-, DX
"""


class AITradingService:
    """Comprehensive AI service for trading intelligence"""

    def __init__(self):
        self.bq_client = bigquery.Client(project=PROJECT_ID)
        self.pro_model = GenerativeModel(MODELS['gemini_pro'])
        self.flash_model = GenerativeModel(MODELS['gemini_flash'])

    def generate_response(self, prompt: str, system_instruction: str = None,
                          use_pro: bool = True, max_tokens: int = 4096,
                          temperature: float = 0.7) -> Dict[str, Any]:
        """Generate AI response using Gemini"""
        model = self.pro_model if use_pro else self.flash_model

        # Create config if GenerationConfig is available
        config = None
        if GenerationConfig is not None:
            config = GenerationConfig(max_output_tokens=max_tokens, temperature=temperature)

        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            if config:
                response = model.generate_content(full_prompt, generation_config=config)
            else:
                response = model.generate_content(full_prompt)
            return {
                'text': response.text,
                'success': True,
                'model': MODELS['gemini_pro'] if use_pro else MODELS['gemini_flash']
            }
        except Exception as e:
            return {'text': None, 'error': str(e), 'success': False}

    def text_to_sql(self, natural_query: str) -> Dict[str, Any]:
        """Convert natural language to SQL query"""

        system_prompt = f"""You are an expert SQL analyst for a trading platform.
Convert user questions to BigQuery SQL.

DATABASE: `{PROJECT_ID}.{DATASET_ID}`

AVAILABLE TABLES:
{json.dumps(CLEAN_TABLES, indent=2)}

{TRADING_CONTEXT}

RULES:
1. ALWAYS use fully qualified table names: `{PROJECT_ID}.{DATASET_ID}.table_name`
2. Use DATE(datetime) for date filtering
3. For "latest" data, use: WHERE DATE(datetime) = (SELECT MAX(DATE(datetime)) FROM table)
4. Return ONLY the SQL query, no explanations
5. Limit results to 100 unless user specifies otherwise
6. Always ORDER BY datetime DESC unless user specifies otherwise
"""

        result = self.generate_response(
            f"Convert this to SQL: {natural_query}",
            system_prompt,
            use_pro=True,
            temperature=0.1
        )

        if result['success']:
            sql = result['text'].strip()
            # Clean up SQL
            if '```sql' in sql:
                sql = sql.split('```sql')[1].split('```')[0]
            elif '```' in sql:
                sql = sql.split('```')[1].split('```')[0]
            result['sql'] = sql.strip()

        return result

    def execute_nl_query(self, natural_query: str) -> Dict[str, Any]:
        """Execute natural language query and return results"""

        # Generate SQL
        sql_result = self.text_to_sql(natural_query)
        if not sql_result['success']:
            return sql_result

        sql = sql_result.get('sql', '')

        try:
            # Execute query
            query_job = self.bq_client.query(sql)
            results = [dict(row) for row in query_job.result()]

            # Convert datetime objects to strings
            for row in results:
                for key, value in row.items():
                    if hasattr(value, 'isoformat'):
                        row[key] = value.isoformat()

            return {
                'success': True,
                'sql': sql,
                'data': results,
                'count': len(results)
            }
        except Exception as e:
            return {
                'success': False,
                'sql': sql,
                'error': str(e)
            }

    def analyze_symbol(self, symbol: str, asset_type: str = 'stocks') -> Dict[str, Any]:
        """Comprehensive AI analysis for a symbol"""

        # Determine table
        table_map = {
            'stocks': 'stocks_daily_clean',
            'crypto': 'crypto_daily_clean',
            'etfs': 'etfs_daily_clean',
            'forex': 'forex_daily_clean',
            'indices': 'indices_daily_clean',
            'commodities': 'commodities_daily_clean'
        }
        table = table_map.get(asset_type, 'stocks_daily_clean')

        # Fetch recent data
        sql = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT 30
        """

        try:
            query_job = self.bq_client.query(sql)
            results = [dict(row) for row in query_job.result()]

            if not results:
                return {'success': False, 'error': f'No data found for {symbol}'}

            # Get AI analysis
            latest = results[0]
            data_summary = {
                'symbol': symbol,
                'latest_close': latest.get('close'),
                'rsi': latest.get('rsi'),
                'macd': latest.get('macd'),
                'macd_signal': latest.get('macd_signal'),
                'adx': latest.get('adx'),
                'atr': latest.get('atr'),
                'sma_20': latest.get('sma_20'),
                'sma_50': latest.get('sma_50'),
                'sma_200': latest.get('sma_200'),
                'bollinger_upper': latest.get('bollinger_upper'),
                'bollinger_lower': latest.get('bollinger_lower'),
                'volume': latest.get('volume'),
                'obv': latest.get('obv')
            }

            system_prompt = f"""You are Saleem, an expert quantitative trader with 20+ years of experience.
Analyze this trading data and provide:
1. SIGNAL: BUY, SELL, or HOLD
2. CONFIDENCE: 1-100 score
3. KEY REASONS: 3 bullet points
4. RISK LEVEL: Low/Medium/High
5. PRICE TARGETS: Support and resistance levels

{TRADING_CONTEXT}

Return as JSON with keys: signal, confidence, reasons, risk_level, support, resistance, summary
"""

            analysis_result = self.generate_response(
                f"Analyze this trading data:\n{json.dumps(data_summary, indent=2)}",
                system_prompt,
                use_pro=True,
                temperature=0.3
            )

            if analysis_result['success']:
                # Parse JSON response
                text = analysis_result['text']
                try:
                    if '```json' in text:
                        text = text.split('```json')[1].split('```')[0]
                    elif '```' in text:
                        text = text.split('```')[1].split('```')[0]
                    analysis = json.loads(text.strip())
                except:
                    analysis = {'raw_text': analysis_result['text']}

                return {
                    'success': True,
                    'symbol': symbol,
                    'data': data_summary,
                    'analysis': analysis
                }

            return analysis_result

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_trading_signals(self, asset_type: str = 'stocks',
                                  signal_type: str = 'all') -> Dict[str, Any]:
        """Generate AI-powered trading signals for multiple assets"""

        table_map = {
            'stocks': 'stocks_daily_clean',
            'crypto': 'crypto_daily_clean',
            'etfs': 'etfs_daily_clean'
        }
        table = table_map.get(asset_type, 'stocks_daily_clean')

        # Query for potential signals based on technical indicators
        conditions = []
        if signal_type in ['buy', 'all']:
            conditions.append("(rsi < 35 AND adx > 20)")  # Oversold with trend
            conditions.append("(macd > macd_signal AND rsi < 50)")  # MACD crossover
        if signal_type in ['sell', 'all']:
            conditions.append("(rsi > 65 AND adx > 20)")  # Overbought with trend
            conditions.append("(macd < macd_signal AND rsi > 50)")  # MACD cross down

        where_clause = " OR ".join(conditions) if conditions else "rsi < 30"

        sql = f"""
        WITH latest_data AS (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
            WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        )
        SELECT symbol, close, rsi, macd, macd_signal, adx, atr, volume,
               CASE
                   WHEN rsi < 30 THEN 'OVERSOLD'
                   WHEN rsi > 70 THEN 'OVERBOUGHT'
                   WHEN macd > macd_signal AND rsi < 50 THEN 'BULLISH_MACD'
                   WHEN macd < macd_signal AND rsi > 50 THEN 'BEARISH_MACD'
                   ELSE 'NEUTRAL'
               END as signal_type
        FROM latest_data
        WHERE rn = 1 AND ({where_clause})
        ORDER BY rsi ASC
        LIMIT 20
        """

        try:
            query_job = self.bq_client.query(sql)
            results = [dict(row) for row in query_job.result()]

            # Convert decimals to floats for JSON
            for row in results:
                for key, value in row.items():
                    if hasattr(value, 'isoformat'):
                        row[key] = value.isoformat()
                    elif isinstance(value, (int, float)):
                        row[key] = float(value) if '.' in str(value) else value

            return {
                'success': True,
                'asset_type': asset_type,
                'signal_type': signal_type,
                'signals': results,
                'count': len(results),
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def chat(self, message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Conversational AI for trading assistance"""

        system_prompt = f"""You are an expert trading AI assistant named TradingGPT, powered by Google Gemini 2.5 Pro.
You help traders with:
1. Market analysis and technical indicator interpretation
2. Trading strategy development
3. Risk management advice
4. Natural language queries about trading data

{TRADING_CONTEXT}

You have access to:
- 424,894 daily stock records (110 symbols)
- 94,048 daily crypto records (46 symbols)
- ETFs, Forex, Indices, Commodities data
- Real-time news and analyst recommendations from Finnhub

Be helpful, accurate, and provide actionable insights. Always mention relevant indicators and their values.
If asked about specific data, offer to run a query.
"""

        # Build conversation context
        context = ""
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = "User" if msg.get('role') == 'user' else "Assistant"
                context += f"{role}: {msg.get('content', '')}\n\n"

        full_prompt = f"{context}User: {message}\n\nAssistant:"

        result = self.generate_response(full_prompt, system_prompt, use_pro=True, temperature=0.7)

        return {
            'success': result['success'],
            'response': result.get('text', ''),
            'model': result.get('model'),
            'error': result.get('error')
        }

    def get_market_summary(self) -> Dict[str, Any]:
        """Generate AI market summary"""

        # Fetch summary data
        sql = """
        WITH stock_summary AS (
            SELECT
                COUNT(DISTINCT symbol) as total_stocks,
                AVG(rsi) as avg_rsi,
                SUM(CASE WHEN rsi < 30 THEN 1 ELSE 0 END) as oversold_count,
                SUM(CASE WHEN rsi > 70 THEN 1 ELSE 0 END) as overbought_count,
                SUM(CASE WHEN macd > macd_signal THEN 1 ELSE 0 END) as bullish_macd,
                SUM(CASE WHEN adx > 25 THEN 1 ELSE 0 END) as strong_trend_count
            FROM (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
                FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
                WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            )
            WHERE rn = 1
        )
        SELECT * FROM stock_summary
        """

        try:
            query_job = self.bq_client.query(sql)
            results = [dict(row) for row in query_job.result()]
            summary_data = results[0] if results else {}

            # Generate AI summary
            system_prompt = """You are a market analyst. Based on the market data, provide:
1. MARKET SENTIMENT: Bullish/Bearish/Neutral
2. KEY OBSERVATIONS: 3 bullet points
3. TOP OPPORTUNITIES: What to watch
4. RISK FACTORS: What to avoid
Keep it concise (under 200 words)."""

            analysis = self.generate_response(
                f"Market Summary Data:\n{json.dumps(summary_data, indent=2)}",
                system_prompt,
                use_pro=False,  # Use flash for speed
                temperature=0.5
            )

            return {
                'success': True,
                'data': summary_data,
                'analysis': analysis.get('text', ''),
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}


    def get_rise_cycle_candidates(self, asset_type: str = 'stocks',
                                     timeframe: str = 'daily', limit: int = 20) -> Dict[str, Any]:
        """Get assets starting rise cycles per masterquery.md EMA crossover strategy

        Rise Cycle Detection (masterquery.md):
        - Rise cycle: EMA_12 > EMA_26 (or EMA_9 > EMA_21 for hourly)
        - Rise cycle START: EMA crosses above (crossover)
        - Growth Score: RSI 50-70 (25pts) + MACD_histogram > 0 (25pts) + ADX > 25 (25pts) + close > SMA_200 (25pts)
        """

        table_map = {
            ('stocks', 'daily'): 'stocks_daily_clean',
            ('stocks', 'hourly'): 'stocks_hourly_clean',
            ('crypto', 'daily'): 'crypto_daily_clean',
            ('crypto', 'hourly'): 'crypto_hourly_clean',
            ('etfs', 'daily'): 'etfs_daily_clean',
        }
        table = table_map.get((asset_type, timeframe), 'stocks_daily_clean')

        # Use EMA_12/EMA_26 for daily, concept of EMA_9/EMA_21 approximated with existing columns
        sql = f"""
        WITH cycle_data AS (
            SELECT
                symbol,
                datetime,
                open,
                high,
                low,
                close,
                volume,
                rsi,
                macd,
                macd_signal,
                macd_histogram,
                adx,
                atr,
                sma_20,
                sma_50,
                sma_200,
                ema_12,
                ema_26,
                bollinger_upper,
                bollinger_lower,
                stoch_k,
                williams_r,
                obv,
                -- Lag values for crossover detection
                LAG(ema_12) OVER (PARTITION BY symbol ORDER BY datetime) as prev_ema_12,
                LAG(ema_26) OVER (PARTITION BY symbol ORDER BY datetime) as prev_ema_26,
                LAG(sma_50) OVER (PARTITION BY symbol ORDER BY datetime) as prev_sma_50,
                LAG(sma_200) OVER (PARTITION BY symbol ORDER BY datetime) as prev_sma_200
            FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
            WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 14 DAY)
        )
        SELECT
            symbol,
            datetime,
            close,
            volume,
            rsi,
            macd,
            macd_histogram,
            adx,
            atr,
            ema_12,
            ema_26,
            sma_50,
            sma_200,
            bollinger_upper,
            bollinger_lower,

            -- Cycle Status per masterquery.md
            CASE
                WHEN ema_12 > ema_26 AND prev_ema_12 <= prev_ema_26 THEN 'RISE_CYCLE_START'
                WHEN ema_12 < ema_26 AND prev_ema_12 >= prev_ema_26 THEN 'FALL_CYCLE_START'
                WHEN ema_12 > ema_26 THEN 'IN_RISE_CYCLE'
                ELSE 'IN_FALL_CYCLE'
            END as cycle_status,

            -- In Rise Cycle (binary)
            CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,

            -- Golden Cross Detection
            CASE
                WHEN sma_50 > sma_200 AND prev_sma_50 <= prev_sma_200 THEN 'GOLDEN_CROSS'
                WHEN sma_50 < sma_200 AND prev_sma_50 >= prev_sma_200 THEN 'DEATH_CROSS'
                WHEN sma_50 > sma_200 THEN 'ABOVE_200'
                ELSE 'BELOW_200'
            END as ma_status,

            -- Growth Score (0-100) per masterquery.md
            (CASE WHEN rsi BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
             CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
             CASE WHEN adx > 25 THEN 25 ELSE 0 END +
             CASE WHEN close > sma_200 THEN 25 ELSE 0 END) as growth_score,

            -- Trend Regime
            CASE
                WHEN close > sma_50 AND sma_50 > sma_200 THEN 'STRONG_UPTREND'
                WHEN close < sma_50 AND sma_50 < sma_200 THEN 'STRONG_DOWNTREND'
                WHEN close > sma_200 THEN 'WEAK_UPTREND'
                ELSE 'CONSOLIDATION'
            END as trend_regime,

            -- Volatility metrics
            SAFE_DIVIDE(atr, close) * 100 as atr_pct,
            SAFE_DIVIDE(bollinger_upper - bollinger_lower, close) * 100 as bb_width_pct

        FROM cycle_data
        WHERE
            -- Focus on cycle transitions and high growth scores
            (ema_12 > ema_26 AND prev_ema_12 <= prev_ema_26)  -- Rise start
            OR (ema_12 < ema_26 AND prev_ema_12 >= prev_ema_26)  -- Fall start
            OR (sma_50 > sma_200 AND prev_sma_50 <= prev_sma_200)  -- Golden cross
            OR (
                ema_12 > ema_26 AND rsi BETWEEN 50 AND 70 AND macd_histogram > 0
            )  -- Strong rise with momentum
        ORDER BY
            CASE WHEN ema_12 > ema_26 AND prev_ema_12 <= prev_ema_26 THEN 0 ELSE 1 END,
            (CASE WHEN rsi BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
             CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
             CASE WHEN adx > 25 THEN 25 ELSE 0 END +
             CASE WHEN close > sma_200 THEN 25 ELSE 0 END) DESC
        LIMIT {limit}
        """

        try:
            query_job = self.bq_client.query(sql)
            results = [dict(row) for row in query_job.result()]

            # Convert for JSON
            for row in results:
                for key, value in row.items():
                    if hasattr(value, 'isoformat'):
                        row[key] = value.isoformat()
                    elif value is not None and not isinstance(value, (str, int, bool)):
                        row[key] = float(value)

            return {
                'success': True,
                'asset_type': asset_type,
                'timeframe': timeframe,
                'candidates': results,
                'count': len(results),
                'methodology': 'EMA_12/EMA_26 crossover with growth scoring per masterquery.md',
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_ml_predictions(self, asset_type: str = 'stocks', limit: int = 20) -> Dict[str, Any]:
        """Get ML model predictions from BigQuery ML

        Uses XGBoost direction predictor trained on:
        - RSI, MACD, ADX, Bollinger Position, Volume Ratio
        - Rise cycle status, Momentum, ATR%, Growth Score
        """

        # Check if ML model exists, if not return feature-based predictions
        sql = f"""
        WITH latest_features AS (
            SELECT
                symbol,
                datetime,
                close,
                rsi,
                macd,
                macd_histogram,
                adx,
                atr,
                ema_12,
                ema_26,
                sma_50,
                sma_200,
                volume,
                bollinger_upper,
                bollinger_lower,

                -- EMA Cycle
                CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,

                -- Growth Score
                (CASE WHEN rsi BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
                 CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
                 CASE WHEN adx > 25 THEN 25 ELSE 0 END +
                 CASE WHEN close > sma_200 THEN 25 ELSE 0 END) as growth_score,

                -- BB Position
                SAFE_DIVIDE(close - bollinger_lower, bollinger_upper - bollinger_lower) as bb_position,

                -- ATR %
                SAFE_DIVIDE(atr, close) * 100 as atr_pct,

                ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn

            FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
            WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        )
        SELECT
            symbol,
            datetime,
            close,
            rsi,
            macd_histogram,
            adx,
            in_rise_cycle,
            growth_score,
            bb_position,
            atr_pct,

            -- Rule-based prediction (until ML model is trained)
            CASE
                WHEN in_rise_cycle = 1 AND growth_score >= 75 AND rsi BETWEEN 50 AND 70 THEN 'STRONG_BUY'
                WHEN in_rise_cycle = 1 AND growth_score >= 50 THEN 'BUY'
                WHEN in_rise_cycle = 0 AND growth_score <= 25 AND rsi > 70 THEN 'SELL'
                WHEN in_rise_cycle = 0 AND growth_score <= 50 THEN 'WEAK_SELL'
                ELSE 'HOLD'
            END as prediction,

            -- Confidence based on indicator alignment
            CASE
                WHEN growth_score >= 75 THEN 'HIGH'
                WHEN growth_score >= 50 THEN 'MEDIUM'
                ELSE 'LOW'
            END as confidence

        FROM latest_features
        WHERE rn = 1 AND growth_score >= 50  -- Focus on higher potential
        ORDER BY growth_score DESC, rsi ASC
        LIMIT {limit}
        """

        try:
            query_job = self.bq_client.query(sql)
            results = [dict(row) for row in query_job.result()]

            for row in results:
                for key, value in row.items():
                    if hasattr(value, 'isoformat'):
                        row[key] = value.isoformat()
                    elif value is not None and not isinstance(value, (str, int, bool)):
                        row[key] = float(value)

            return {
                'success': True,
                'predictions': results,
                'count': len(results),
                'model': 'rule_based_v1',  # Will change to 'xgboost_direction_predictor' when ML model is deployed
                'methodology': 'Growth score + EMA cycle + RSI momentum alignment',
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}


# Flask route integration functions
def handle_ai_chat(message: str, history: List = None) -> Dict:
    """Handle chat endpoint"""
    service = AITradingService()
    return service.chat(message, history)


def handle_nl_query(query: str) -> Dict:
    """Handle natural language query endpoint"""
    service = AITradingService()
    return service.execute_nl_query(query)


def handle_symbol_analysis(symbol: str, asset_type: str = 'stocks') -> Dict:
    """Handle symbol analysis endpoint"""
    service = AITradingService()
    return service.analyze_symbol(symbol, asset_type)


def handle_trading_signals(asset_type: str = 'stocks', signal_type: str = 'all') -> Dict:
    """Handle trading signals endpoint"""
    service = AITradingService()
    return service.generate_trading_signals(asset_type, signal_type)


def handle_market_summary() -> Dict:
    """Handle market summary endpoint"""
    service = AITradingService()
    return service.get_market_summary()


# Test function
if __name__ == '__main__':
    service = AITradingService()

    print("=" * 60)
    print("AI TRADING SERVICE TEST")
    print("=" * 60)

    # Test NL Query
    print("\n1. Testing Natural Language Query...")
    result = service.execute_nl_query("Show me top 5 oversold stocks with strong trends")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"SQL: {result.get('sql', '')[:100]}...")
        print(f"Results: {len(result.get('data', []))} rows")

    # Test Symbol Analysis
    print("\n2. Testing Symbol Analysis...")
    result = service.analyze_symbol("NVDA")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Signal: {result.get('analysis', {}).get('signal', 'N/A')}")

    # Test Chat
    print("\n3. Testing Chat...")
    result = service.chat("What's the best strategy for volatile markets?")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Response: {result.get('response', '')[:200]}...")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
