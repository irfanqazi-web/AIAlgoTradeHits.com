"""
LLM Training Data Generator for AIAlgoTradeHits.com
Generates fine-tuning data for Gemini LLM from BigQuery stock/crypto data

Based on Document: llm-model-development-process-aialgotradehits.html
"""

from google.cloud import bigquery
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os

def safe_val(value, default=0):
    """Safely get numeric value, return default if NA"""
    return default if pd.isna(value) else value

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
OUTPUT_DIR = 'C:/1AITrading/Trading/llm_training_data'

client = bigquery.Client(project=PROJECT_ID)

def fetch_stock_data(symbol: str, days: int = 365) -> pd.DataFrame:
    """Fetch stock data with all indicators from BigQuery"""
    query = f"""
    SELECT
        datetime, symbol, open, high, low, close, volume,
        rsi, macd, macd_signal, macd_histogram,
        stoch_k, stoch_d, cci, williams_r, momentum,
        sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
        bollinger_upper, bollinger_middle, bollinger_lower, bb_width,
        adx, plus_di, minus_di, atr, obv,
        golden_cross, death_cross, cycle_type, cycle_pnl_pct,
        buy_pressure_pct, sell_pressure_pct,
        hammer, shooting_star, bullish_engulfing, bearish_engulfing, doji,
        trend_regime, vol_regime
    FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
    WHERE symbol = '{symbol}'
    ORDER BY datetime DESC
    LIMIT {days}
    """
    df = client.query(query).to_dataframe()
    return df.sort_values('datetime')


def generate_market_context(row: pd.Series, lookback_data: pd.DataFrame) -> str:
    """Generate a rich market context description for the LLM"""

    # Price action summary
    price_change = ((row['close'] - lookback_data['close'].iloc[0]) / lookback_data['close'].iloc[0]) * 100

    # Trend analysis
    if row['trend_regime'] == 1:
        trend = "bullish uptrend"
    elif row['trend_regime'] == -1:
        trend = "bearish downtrend"
    else:
        trend = "sideways consolidation"

    # RSI interpretation
    if row['rsi'] > 70:
        rsi_state = "overbought territory"
    elif row['rsi'] < 30:
        rsi_state = "oversold territory"
    else:
        rsi_state = "neutral zone"

    # MACD interpretation
    if row['macd'] > row['macd_signal']:
        macd_state = "bullish momentum with MACD above signal"
    else:
        macd_state = "bearish momentum with MACD below signal"

    # Bollinger Bands position
    if row['close'] > row['bollinger_upper']:
        bb_state = "trading above upper Bollinger Band"
    elif row['close'] < row['bollinger_lower']:
        bb_state = "trading below lower Bollinger Band"
    else:
        bb_state = "within Bollinger Bands"

    # Volume analysis
    if row['buy_pressure_pct'] and row['buy_pressure_pct'] > 60:
        volume_state = "strong buying pressure"
    elif row['sell_pressure_pct'] and row['sell_pressure_pct'] > 60:
        volume_state = "strong selling pressure"
    else:
        volume_state = "balanced volume"

    # Candlestick patterns (handle NA values)
    patterns = []
    if pd.notna(row.get('hammer')) and row['hammer'] == 1:
        patterns.append("hammer (bullish reversal)")
    if pd.notna(row.get('shooting_star')) and row['shooting_star'] == 1:
        patterns.append("shooting star (bearish reversal)")
    if pd.notna(row.get('bullish_engulfing')) and row['bullish_engulfing'] == 1:
        patterns.append("bullish engulfing")
    if pd.notna(row.get('bearish_engulfing')) and row['bearish_engulfing'] == 1:
        patterns.append("bearish engulfing")
    if pd.notna(row.get('doji')) and row['doji'] == 1:
        patterns.append("doji (indecision)")

    pattern_text = ", ".join(patterns) if patterns else "no significant patterns"

    # MA crossovers (handle NA values)
    if pd.notna(row.get('golden_cross')) and row['golden_cross'] == 1:
        crossover = "Golden cross just occurred - bullish signal"
    elif pd.notna(row.get('death_cross')) and row['death_cross'] == 1:
        crossover = "Death cross just occurred - bearish signal"
    elif pd.notna(row.get('cycle_type')) and row['cycle_type'] == 1:
        crossover = "Currently in rise cycle"
    elif pd.notna(row.get('cycle_type')) and row['cycle_type'] == -1:
        crossover = "Currently in fall cycle"
    else:
        crossover = "No recent crossover"

    context = f"""
Market Analysis for {row['symbol']} as of {row['datetime'].strftime('%Y-%m-%d')}:

PRICE ACTION:
- Current price: ${row['close']:.2f}
- {abs(price_change):.1f}% {'gain' if price_change > 0 else 'loss'} over analysis period
- High: ${row['high']:.2f}, Low: ${row['low']:.2f}
- Trading volume: {row['volume']:,.0f} shares

TECHNICAL INDICATORS:
- Trend: The stock is in a {trend}
- RSI ({row['rsi']:.1f}): Currently in {rsi_state}
- MACD: {macd_state} (MACD: {row['macd']:.2f}, Signal: {row['macd_signal']:.2f})
- Stochastic: %K={row['stoch_k']:.1f}, %D={row['stoch_d']:.1f}
- ADX ({row['adx']:.1f}): {'Strong trend' if row['adx'] > 25 else 'Weak trend'}
- ATR: ${row['atr']:.2f} (volatility measure)

MOVING AVERAGES:
- Price vs SMA20: {'Above' if row['close'] > row['sma_20'] else 'Below'} (SMA20: ${row['sma_20']:.2f})
- Price vs SMA50: {'Above' if row['close'] > row['sma_50'] else 'Below'} (SMA50: ${row['sma_50']:.2f})
- Price vs SMA200: {'Above' if row['close'] > row['sma_200'] else 'Below'} (SMA200: ${row['sma_200']:.2f})

BOLLINGER BANDS:
- Currently {bb_state}
- Upper: ${row['bollinger_upper']:.2f}, Middle: ${row['bollinger_middle']:.2f}, Lower: ${row['bollinger_lower']:.2f}
- Band Width: {row['bb_width']:.2f}%

VOLUME ANALYSIS:
- {volume_state}
- Buy pressure: {row['buy_pressure_pct']:.1f}% of last 20 candles
- Sell pressure: {row['sell_pressure_pct']:.1f}% of last 20 candles

CANDLESTICK PATTERNS:
- {pattern_text}

MA CROSSOVER SIGNALS:
- {crossover}
- Cycle P&L: {row['cycle_pnl_pct']:.2f}% since last crossover
"""
    return context.strip()


def generate_prediction_prompt(context: str) -> str:
    """Generate the prompt for the LLM"""
    return f"""You are a professional stock market analyst. Based on the following technical analysis, predict the most likely price movement for tomorrow.

{context}

Provide your analysis and prediction in the following format:
1. SUMMARY: Brief summary of the current market state
2. KEY SIGNALS: List the most important bullish and bearish signals
3. PREDICTION: UP, DOWN, or NEUTRAL
4. CONFIDENCE: HIGH, MEDIUM, or LOW
5. REASONING: Explain your prediction
"""


def generate_training_example(row: pd.Series, lookback_data: pd.DataFrame,
                               next_day_return: float) -> dict:
    """Generate a single training example in JSONL format"""

    context = generate_market_context(row, lookback_data)
    prompt = generate_prediction_prompt(context)

    # Determine the actual outcome
    if next_day_return > 0.005:  # >0.5% gain
        actual_direction = "UP"
        confidence = "HIGH" if next_day_return > 0.02 else "MEDIUM"
    elif next_day_return < -0.005:  # >0.5% loss
        actual_direction = "DOWN"
        confidence = "HIGH" if next_day_return < -0.02 else "MEDIUM"
    else:
        actual_direction = "NEUTRAL"
        confidence = "LOW"

    # Generate the ideal response
    response = f"""1. SUMMARY: Based on the technical analysis, {row['symbol']} is showing {'bullish' if actual_direction == 'UP' else 'bearish' if actual_direction == 'DOWN' else 'mixed'} signals with the price currently in a {'strong uptrend' if row['trend_regime'] == 1 else 'downtrend' if row['trend_regime'] == -1 else 'consolidation phase'}.

2. KEY SIGNALS:
BULLISH:
- {"RSI in oversold territory suggesting potential bounce" if row['rsi'] < 30 else "Price above key moving averages" if row['close'] > row['sma_50'] else "Bullish candlestick patterns forming"}
- {"Golden cross signal" if row['golden_cross'] == 1 else "Strong buying pressure" if row['buy_pressure_pct'] > 60 else "MACD showing bullish momentum" if row['macd'] > row['macd_signal'] else "Volume supporting the move"}

BEARISH:
- {"RSI in overbought territory" if row['rsi'] > 70 else "Price below key moving averages" if row['close'] < row['sma_50'] else "Bearish candlestick patterns"}
- {"Death cross signal" if row['death_cross'] == 1 else "Strong selling pressure" if row['sell_pressure_pct'] > 60 else "MACD showing bearish momentum" if row['macd'] < row['macd_signal'] else "Weak volume"}

3. PREDICTION: {actual_direction}

4. CONFIDENCE: {confidence}

5. REASONING: The combination of {'bullish' if actual_direction == 'UP' else 'bearish' if actual_direction == 'DOWN' else 'mixed'} technical indicators, {'oversold RSI' if row['rsi'] < 30 else 'overbought RSI' if row['rsi'] > 70 else 'neutral RSI'}, and {'strong buying' if row['buy_pressure_pct'] > 60 else 'strong selling' if row['sell_pressure_pct'] > 60 else 'balanced'} pressure suggests a {'positive' if actual_direction == 'UP' else 'negative' if actual_direction == 'DOWN' else 'sideways'} move is likely. The {'strong' if row['adx'] > 25 else 'weak'} trend strength (ADX: {row['adx']:.1f}) {'supports' if row['adx'] > 25 else 'tempers'} this prediction."""

    return {
        "text_input": prompt,
        "output": response
    }


def generate_training_dataset(symbols: list, output_file: str,
                               lookback_days: int = 20, max_examples: int = 5000):
    """Generate complete training dataset for multiple symbols"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    examples = []

    for symbol in symbols:
        print(f"Processing {symbol}...")

        try:
            df = fetch_stock_data(symbol, days=1000)

            if len(df) < lookback_days + 10:
                print(f"  Skipping {symbol}: insufficient data")
                continue

            # Calculate next day return for labeling
            df['next_day_return'] = df['close'].shift(-1) / df['close'] - 1

            # Generate examples for each valid row
            for i in range(lookback_days, len(df) - 1):
                row = df.iloc[i]
                lookback_data = df.iloc[i-lookback_days:i]
                next_day_return = df.iloc[i]['next_day_return']

                if pd.isna(next_day_return):
                    continue

                # Skip rows with too many missing values
                if row.isna().sum() > 10:
                    continue

                example = generate_training_example(row, lookback_data, next_day_return)
                examples.append(example)

            print(f"  Generated {len(examples)} examples so far")

            if len(examples) >= max_examples:
                break

        except Exception as e:
            print(f"  Error processing {symbol}: {e}")
            continue

    # Save to JSONL file
    output_path = os.path.join(OUTPUT_DIR, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example) + '\n')

    print(f"\nGenerated {len(examples)} training examples")
    print(f"Saved to: {output_path}")

    # Also create train/validation split
    np.random.shuffle(examples)
    split_idx = int(len(examples) * 0.9)

    train_examples = examples[:split_idx]
    val_examples = examples[split_idx:]

    train_path = os.path.join(OUTPUT_DIR, 'train.jsonl')
    val_path = os.path.join(OUTPUT_DIR, 'validation.jsonl')

    with open(train_path, 'w', encoding='utf-8') as f:
        for example in train_examples:
            f.write(json.dumps(example) + '\n')

    with open(val_path, 'w', encoding='utf-8') as f:
        for example in val_examples:
            f.write(json.dumps(example) + '\n')

    print(f"Train set: {len(train_examples)} examples -> {train_path}")
    print(f"Validation set: {len(val_examples)} examples -> {val_path}")

    return examples


def main():
    """Main function to generate training data"""

    print("=" * 80)
    print("LLM TRAINING DATA GENERATOR FOR AIALGOTRADEHITS.COM")
    print("=" * 80)
    print(f"Started: {datetime.now()}")

    # Get top symbols from BigQuery
    query = """
    SELECT DISTINCT symbol
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
    WHERE symbol IN ('AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META',
                     'JPM', 'V', 'MA', 'HD', 'DIS', 'NFLX', 'AMD', 'INTC',
                     'SPY', 'QQQ', 'IWM', 'DIA')
    ORDER BY symbol
    """
    result = client.query(query).result()
    symbols = [row.symbol for row in result]

    print(f"\nProcessing {len(symbols)} symbols: {', '.join(symbols)}")

    # Generate training data
    examples = generate_training_dataset(
        symbols=symbols,
        output_file='stock_prediction_training.jsonl',
        lookback_days=20,
        max_examples=10000
    )

    print(f"\nCompleted: {datetime.now()}")
    print("=" * 80)


if __name__ == "__main__":
    main()
