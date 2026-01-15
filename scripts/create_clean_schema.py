import pandas as pd

# Create the deduplicated schema
data = {
    'S#': list(range(1, 86)),
    'Field Name': [
        # CORE (1-2)
        'datetime', 'symbol',
        # OHLCV (3-8)
        'open', 'high', 'low', 'close', 'previous_close', 'volume',
        # PRICE STATS (9-15)
        'average_volume', 'change', 'percent_change', 'high_low', 'pct_high_low', 'week_52_high', 'week_52_low',
        # MOMENTUM (16-24)
        'rsi', 'macd', 'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'cci', 'williams_r', 'momentum',
        # MOVING AVERAGES (25-33)
        'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_20', 'ema_26', 'ema_50', 'ema_200', 'kama',
        # TREND & VOLATILITY (34-43)
        'bollinger_upper', 'bollinger_middle', 'bollinger_lower', 'bb_width', 'adx', 'plus_di', 'minus_di', 'atr', 'trix', 'roc',
        # VOLUME (44-46)
        'obv', 'pvo', 'ppo',
        # ADVANCED OSCILLATORS (47-48)
        'ultimate_osc', 'awesome_osc',
        # RETURNS (49-51)
        'log_return', 'return_2w', 'return_4w',
        # RELATIVE POSITIONS (52-54)
        'close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct',
        # INDICATOR DYNAMICS (55-65)
        'rsi_slope', 'rsi_zscore', 'rsi_overbought', 'rsi_oversold', 'macd_cross', 'ema20_slope', 'ema50_slope', 'atr_zscore', 'atr_slope', 'volume_zscore', 'volume_ratio',
        # MARKET STRUCTURE (66-69)
        'pivot_high_flag', 'pivot_low_flag', 'dist_to_pivot_high', 'dist_to_pivot_low',
        # REGIME (70-72)
        'trend_regime', 'vol_regime', 'regime_confidence',
        # METADATA (73-81)
        'name', 'sector', 'industry', 'asset_type', 'exchange', 'mic_code', 'country', 'currency', 'type',
        # SYSTEM (82-85)
        'timestamp', 'data_source', 'created_at', 'updated_at'
    ],
    'Type': [
        # CORE
        'TIMESTAMP', 'STRING',
        # OHLCV
        'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'INTEGER',
        # PRICE STATS
        'INTEGER', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT',
        # MOMENTUM
        'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT',
        # MOVING AVERAGES
        'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT',
        # TREND & VOLATILITY
        'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT',
        # VOLUME
        'FLOAT', 'FLOAT', 'FLOAT',
        # ADVANCED OSCILLATORS
        'FLOAT', 'FLOAT',
        # RETURNS
        'FLOAT', 'FLOAT', 'FLOAT',
        # RELATIVE POSITIONS
        'FLOAT', 'FLOAT', 'FLOAT',
        # INDICATOR DYNAMICS
        'FLOAT', 'FLOAT', 'INTEGER', 'INTEGER', 'INTEGER', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT',
        # MARKET STRUCTURE
        'INTEGER', 'INTEGER', 'FLOAT', 'FLOAT',
        # REGIME
        'INTEGER', 'INTEGER', 'FLOAT',
        # METADATA
        'STRING', 'STRING', 'STRING', 'STRING', 'STRING', 'STRING', 'STRING', 'STRING', 'STRING',
        # SYSTEM
        'INTEGER', 'STRING', 'TIMESTAMP', 'TIMESTAMP'
    ],
    'Full Name': [
        # CORE
        'Market DateTime', 'Stock Ticker Symbol',
        # OHLCV
        'Opening Price', 'Highest Price', 'Lowest Price', 'Closing Price', 'Previous Closing Price', 'Trading Volume',
        # PRICE STATS
        'Average Trading Volume', 'Price Change (Absolute)', 'Price Change (Percentage)', 'High-Low Range (Absolute)', 'High-Low Range vs Low (%)', '52-Week High', '52-Week Low',
        # MOMENTUM
        'Relative Strength Index', 'MACD Line', 'MACD Signal Line', 'MACD Histogram', 'Stochastic %K', 'Stochastic %D', 'Commodity Channel Index', 'Williams %R', 'Momentum Indicator',
        # MOVING AVERAGES
        'Simple Moving Average (20-day)', 'Simple Moving Average (50-day)', 'Simple Moving Average (200-day)', 'Exponential Moving Average (12-day)', 'Exponential Moving Average (20-day)', 'Exponential Moving Average (26-day)', 'Exponential Moving Average (50-day)', 'Exponential Moving Average (200-day)', 'Kaufman Adaptive Moving Average',
        # TREND & VOLATILITY
        'Bollinger Band (Upper)', 'Bollinger Band (Middle)', 'Bollinger Band (Lower)', 'Bollinger Band Width', 'Average Directional Index', 'Plus Directional Indicator (+DI)', 'Minus Directional Indicator (-DI)', 'Average True Range', 'TRIX Indicator', 'Rate of Change',
        # VOLUME
        'On-Balance Volume', 'Percentage Volume Oscillator', 'Percentage Price Oscillator',
        # ADVANCED OSCILLATORS
        'Ultimate Oscillator', 'Awesome Oscillator',
        # RETURNS
        'Logarithmic Return (1-day)', 'Forward Return (2-week)', 'Forward Return (4-week)',
        # RELATIVE POSITIONS
        'Close vs SMA20 (Percentage)', 'Close vs SMA50 (Percentage)', 'Close vs SMA200 (Percentage)',
        # INDICATOR DYNAMICS
        'RSI Slope (Rate of Change)', 'RSI Z-Score', 'RSI Overbought Flag', 'RSI Oversold Flag', 'MACD Crossover Signal', 'EMA20 Slope', 'EMA50 Slope', 'ATR Z-Score', 'ATR Slope', 'Volume Z-Score', 'Volume Ratio',
        # MARKET STRUCTURE
        'Pivot High Flag', 'Pivot Low Flag', 'Distance to Last Pivot High', 'Distance to Last Pivot Low',
        # REGIME
        'Trend Regime Classification', 'Volatility Regime Classification', 'Regime Classification Confidence',
        # METADATA
        'Company/Asset Full Name', 'Economic Sector', 'Industry Classification', 'Asset Type', 'Exchange Name', 'Market Identifier Code', 'Country Code', 'Trading Currency', 'Security Type',
        # SYSTEM
        'Unix Timestamp', 'Data Source Provider', 'Record Creation Timestamp', 'Record Update Timestamp'
    ],
    'Mode': ['REQUIRED', 'REQUIRED'] + ['NULLABLE'] * 83
}

df = pd.DataFrame(data)
output_path = r'C:\Users\irfan\Downloads\Stockfieldsequence_CLEAN.xlsx'
df.to_excel(output_path, index=False)

print('[OK] Clean schema saved to:', output_path)
print(f'Total fields: {len(df)} (down from 89)')
print(f'\nDuplicates removed (5):')
print('  - week_52_high (duplicate at original S# 13)')
print('  - momentum (duplicate at original S# 37)')
print('  - williams_r (duplicate at original S# 38)')
print('  - ema_50 (duplicate at original S# 39)')
print('  - obv (duplicate at original S# 42)')
print(f'\nField names fixed (2):')
print('  - high-low → high_low')
print('  - pct_high-low → pct_high_low')
