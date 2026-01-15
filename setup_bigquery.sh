#!/bin/bash
PROJECT="aialgotradehits"
DATASET="crypto_trading_data"

echo "Creating BigQuery tables..."

# Create crypto_analysis
echo '[{"name":"pair","type":"STRING"},{"name":"altname","type":"STRING"},{"name":"base","type":"STRING"},{"name":"quote","type":"STRING"},{"name":"open","type":"FLOAT"},{"name":"high","type":"FLOAT"},{"name":"low","type":"FLOAT"},{"name":"close","type":"FLOAT"},{"name":"volume","type":"FLOAT"},{"name":"vwap","type":"FLOAT"},{"name":"count","type":"INTEGER"},{"name":"timestamp","type":"INTEGER"},{"name":"datetime","type":"TIMESTAMP"},{"name":"rsi","type":"FLOAT"},{"name":"macd","type":"FLOAT"},{"name":"macd_signal","type":"FLOAT"},{"name":"macd_histogram","type":"FLOAT"},{"name":"sma_20","type":"FLOAT"},{"name":"sma_50","type":"FLOAT"},{"name":"sma_200","type":"FLOAT"},{"name":"ema_12","type":"FLOAT"},{"name":"ema_26","type":"FLOAT"},{"name":"ema_50","type":"FLOAT"},{"name":"bollinger_upper","type":"FLOAT"},{"name":"bollinger_middle","type":"FLOAT"},{"name":"bollinger_lower","type":"FLOAT"},{"name":"atr","type":"FLOAT"},{"name":"adx","type":"FLOAT"},{"name":"obv","type":"FLOAT"},{"name":"roc","type":"FLOAT"},{"name":"momentum","type":"FLOAT"},{"name":"stoch_k","type":"FLOAT"},{"name":"stoch_d","type":"FLOAT"},{"name":"willr","type":"FLOAT"},{"name":"cci","type":"FLOAT"},{"name":"ppo","type":"FLOAT"},{"name":"pvo","type":"FLOAT"},{"name":"kama","type":"FLOAT"},{"name":"trix","type":"FLOAT"},{"name":"ultimate_oscillator","type":"FLOAT"},{"name":"awesome_oscillator","type":"FLOAT"},{"name":"fetch_timestamp","type":"TIMESTAMP"}]' > /tmp/schema1.json
bq mk --table $PROJECT:$DATASET.crypto_analysis /tmp/schema1.json
echo "Created crypto_analysis"

# Create crypto_hourly_data
echo '[{"name":"pair","type":"STRING"},{"name":"altname","type":"STRING"},{"name":"base","type":"STRING"},{"name":"quote","type":"STRING"},{"name":"open","type":"FLOAT"},{"name":"high","type":"FLOAT"},{"name":"low","type":"FLOAT"},{"name":"close","type":"FLOAT"},{"name":"volume","type":"FLOAT"},{"name":"vwap","type":"FLOAT"},{"name":"count","type":"INTEGER"},{"name":"timestamp","type":"INTEGER"},{"name":"datetime","type":"TIMESTAMP"},{"name":"rsi","type":"FLOAT"},{"name":"macd","type":"FLOAT"},{"name":"macd_signal","type":"FLOAT"},{"name":"macd_histogram","type":"FLOAT"},{"name":"sma_20","type":"FLOAT"},{"name":"sma_50","type":"FLOAT"},{"name":"sma_200","type":"FLOAT"},{"name":"ema_12","type":"FLOAT"},{"name":"ema_26","type":"FLOAT"},{"name":"ema_50","type":"FLOAT"},{"name":"bollinger_upper","type":"FLOAT"},{"name":"bollinger_middle","type":"FLOAT"},{"name":"bollinger_lower","type":"FLOAT"},{"name":"atr","type":"FLOAT"},{"name":"adx","type":"FLOAT"},{"name":"obv","type":"FLOAT"},{"name":"roc","type":"FLOAT"},{"name":"momentum","type":"FLOAT"},{"name":"stoch_k","type":"FLOAT"},{"name":"stoch_d","type":"FLOAT"},{"name":"willr","type":"FLOAT"},{"name":"cci","type":"FLOAT"},{"name":"ppo","type":"FLOAT"},{"name":"pvo","type":"FLOAT"},{"name":"kama","type":"FLOAT"},{"name":"trix","type":"FLOAT"},{"name":"ultimate_oscillator","type":"FLOAT"},{"name":"awesome_oscillator","type":"FLOAT"},{"name":"fetch_timestamp","type":"TIMESTAMP"},{"name":"hour","type":"INTEGER"}]' > /tmp/schema2.json
bq mk --table $PROJECT:$DATASET.crypto_hourly_data /tmp/schema2.json
echo "Created crypto_hourly_data"

# Create crypto_5min_top10_gainers
echo '[{"name":"pair","type":"STRING"},{"name":"open","type":"FLOAT"},{"name":"high","type":"FLOAT"},{"name":"low","type":"FLOAT"},{"name":"close","type":"FLOAT"},{"name":"volume","type":"FLOAT"},{"name":"vwap","type":"FLOAT"},{"name":"count","type":"INTEGER"},{"name":"timestamp","type":"INTEGER"},{"name":"datetime","type":"TIMESTAMP"},{"name":"rsi","type":"FLOAT"},{"name":"macd","type":"FLOAT"},{"name":"macd_signal","type":"FLOAT"},{"name":"macd_histogram","type":"FLOAT"},{"name":"sma_20","type":"FLOAT"},{"name":"sma_50","type":"FLOAT"},{"name":"ema_12","type":"FLOAT"},{"name":"ema_26","type":"FLOAT"},{"name":"bollinger_upper","type":"FLOAT"},{"name":"bollinger_middle","type":"FLOAT"},{"name":"bollinger_lower","type":"FLOAT"},{"name":"atr","type":"FLOAT"},{"name":"adx","type":"FLOAT"},{"name":"obv","type":"FLOAT"},{"name":"roc","type":"FLOAT"},{"name":"momentum","type":"FLOAT"},{"name":"stoch_k","type":"FLOAT"},{"name":"stoch_d","type":"FLOAT"},{"name":"willr","type":"FLOAT"},{"name":"cci","type":"FLOAT"},{"name":"ppo","type":"FLOAT"},{"name":"pvo","type":"FLOAT"},{"name":"kama","type":"FLOAT"},{"name":"trix","type":"FLOAT"},{"name":"ultimate_oscillator","type":"FLOAT"},{"name":"awesome_oscillator","type":"FLOAT"},{"name":"fetch_timestamp","type":"TIMESTAMP"},{"name":"hourly_gain_pct","type":"FLOAT"},{"name":"rank","type":"INTEGER"}]' > /tmp/schema3.json
bq mk --table $PROJECT:$DATASET.crypto_5min_top10_gainers /tmp/schema3.json
echo "Created crypto_5min_top10_gainers"

# Create stock_analysis
echo '[{"name":"symbol","type":"STRING"},{"name":"name","type":"STRING"},{"name":"sector","type":"STRING"},{"name":"industry","type":"STRING"},{"name":"open","type":"FLOAT"},{"name":"high","type":"FLOAT"},{"name":"low","type":"FLOAT"},{"name":"close","type":"FLOAT"},{"name":"volume","type":"FLOAT"},{"name":"datetime","type":"TIMESTAMP"},{"name":"date","type":"DATE"},{"name":"rsi","type":"FLOAT"},{"name":"macd","type":"FLOAT"},{"name":"macd_signal","type":"FLOAT"},{"name":"macd_histogram","type":"FLOAT"},{"name":"sma_20","type":"FLOAT"},{"name":"sma_50","type":"FLOAT"},{"name":"sma_200","type":"FLOAT"},{"name":"ema_12","type":"FLOAT"},{"name":"ema_26","type":"FLOAT"},{"name":"ema_50","type":"FLOAT"},{"name":"bollinger_upper","type":"FLOAT"},{"name":"bollinger_middle","type":"FLOAT"},{"name":"bollinger_lower","type":"FLOAT"},{"name":"atr","type":"FLOAT"},{"name":"adx","type":"FLOAT"},{"name":"obv","type":"FLOAT"},{"name":"roc","type":"FLOAT"},{"name":"momentum","type":"FLOAT"},{"name":"stoch_k","type":"FLOAT"},{"name":"stoch_d","type":"FLOAT"},{"name":"willr","type":"FLOAT"},{"name":"cci","type":"FLOAT"},{"name":"ppo","type":"FLOAT"},{"name":"pvo","type":"FLOAT"},{"name":"kama","type":"FLOAT"},{"name":"trix","type":"FLOAT"},{"name":"ultimate_oscillator","type":"FLOAT"},{"name":"awesome_oscillator","type":"FLOAT"},{"name":"fetch_timestamp","type":"TIMESTAMP"}]' > /tmp/schema4.json
bq mk --table $PROJECT:$DATASET.stock_analysis /tmp/schema4.json
echo "Created stock_analysis"

# Create stock_hourly_data
echo '[{"name":"symbol","type":"STRING"},{"name":"name","type":"STRING"},{"name":"sector","type":"STRING"},{"name":"open","type":"FLOAT"},{"name":"high","type":"FLOAT"},{"name":"low","type":"FLOAT"},{"name":"close","type":"FLOAT"},{"name":"volume","type":"FLOAT"},{"name":"datetime","type":"TIMESTAMP"},{"name":"rsi","type":"FLOAT"},{"name":"macd","type":"FLOAT"},{"name":"macd_signal","type":"FLOAT"},{"name":"macd_histogram","type":"FLOAT"},{"name":"sma_20","type":"FLOAT"},{"name":"sma_50","type":"FLOAT"},{"name":"ema_12","type":"FLOAT"},{"name":"ema_26","type":"FLOAT"},{"name":"bollinger_upper","type":"FLOAT"},{"name":"bollinger_middle","type":"FLOAT"},{"name":"bollinger_lower","type":"FLOAT"},{"name":"atr","type":"FLOAT"},{"name":"adx","type":"FLOAT"},{"name":"obv","type":"FLOAT"},{"name":"fetch_timestamp","type":"TIMESTAMP"}]' > /tmp/schema5.json
bq mk --table $PROJECT:$DATASET.stock_hourly_data /tmp/schema5.json
echo "Created stock_hourly_data"

# Create stock_5min_top10_gainers
echo '[{"name":"symbol","type":"STRING"},{"name":"open","type":"FLOAT"},{"name":"high","type":"FLOAT"},{"name":"low","type":"FLOAT"},{"name":"close","type":"FLOAT"},{"name":"volume","type":"FLOAT"},{"name":"datetime","type":"TIMESTAMP"},{"name":"rsi","type":"FLOAT"},{"name":"macd","type":"FLOAT"},{"name":"macd_signal","type":"FLOAT"},{"name":"macd_histogram","type":"FLOAT"},{"name":"sma_20","type":"FLOAT"},{"name":"sma_50","type":"FLOAT"},{"name":"ema_12","type":"FLOAT"},{"name":"ema_26","type":"FLOAT"},{"name":"bollinger_upper","type":"FLOAT"},{"name":"bollinger_middle","type":"FLOAT"},{"name":"bollinger_lower","type":"FLOAT"},{"name":"atr","type":"FLOAT"},{"name":"adx","type":"FLOAT"},{"name":"obv","type":"FLOAT"},{"name":"fetch_timestamp","type":"TIMESTAMP"},{"name":"hourly_gain_pct","type":"FLOAT"},{"name":"rank","type":"INTEGER"}]' > /tmp/schema6.json
bq mk --table $PROJECT:$DATASET.stock_5min_top10_gainers /tmp/schema6.json
echo "Created stock_5min_top10_gainers"

# Create cryptos_weekly_summary
echo '[{"name":"symbol","type":"STRING"},{"name":"name","type":"STRING"},{"name":"category","type":"STRING"},{"name":"market_cap_category","type":"STRING"},{"name":"volatility_category","type":"STRING"},{"name":"week_open","type":"FLOAT"},{"name":"week_high","type":"FLOAT"},{"name":"week_low","type":"FLOAT"},{"name":"week_close","type":"FLOAT"},{"name":"week_volume","type":"FLOAT"},{"name":"price_change_pct","type":"FLOAT"},{"name":"avg_rsi","type":"FLOAT"},{"name":"trend_direction","type":"STRING"},{"name":"support_level","type":"FLOAT"},{"name":"resistance_level","type":"FLOAT"},{"name":"fetch_timestamp","type":"TIMESTAMP"}]' > /tmp/schema7.json
bq mk --table $PROJECT:$DATASET.cryptos_weekly_summary /tmp/schema7.json
echo "Created cryptos_weekly_summary"

# Create scheduler_execution_log
echo '[{"name":"scheduler_name","type":"STRING"},{"name":"execution_date","type":"DATE"},{"name":"execution_time","type":"TIMESTAMP"},{"name":"status","type":"STRING"},{"name":"records_processed","type":"INTEGER"},{"name":"error_message","type":"STRING"},{"name":"duration_seconds","type":"FLOAT"}]' > /tmp/schema8.json
bq mk --table $PROJECT:$DATASET.scheduler_execution_log /tmp/schema8.json
echo "Created scheduler_execution_log"

# Create search_history
echo '[{"name":"user_id","type":"STRING"},{"name":"query","type":"STRING"},{"name":"asset_type","type":"STRING"},{"name":"results_count","type":"INTEGER"},{"name":"search_timestamp","type":"TIMESTAMP"}]' > /tmp/schema9.json
bq mk --table $PROJECT:$DATASET.search_history /tmp/schema9.json
echo "Created search_history"

# Create users
echo '[{"name":"user_id","type":"STRING"},{"name":"email","type":"STRING"},{"name":"username","type":"STRING"},{"name":"password_hash","type":"STRING"},{"name":"role","type":"STRING"},{"name":"first_login_completed","type":"BOOLEAN"},{"name":"created_at","type":"TIMESTAMP"},{"name":"last_login","type":"TIMESTAMP"},{"name":"token","type":"STRING"}]' > /tmp/schema10.json
bq mk --table $PROJECT:$DATASET.users /tmp/schema10.json
echo "Created users"

echo ""
echo "✅ All tables created!"
bq ls $PROJECT:$DATASET
