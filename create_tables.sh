#!/bin/bash
# Create all BigQuery tables for aialgotradehits project

PROJECT="aialgotradehits"
DATASET="crypto_trading_data"

echo "Creating tables in $PROJECT:$DATASET..."

# 1. crypto_analysis (daily crypto data)
bq mk --table $PROJECT:$DATASET.crypto_analysis \
  pair:STRING,altname:STRING,base:STRING,quote:STRING,open:FLOAT,high:FLOAT,low:FLOAT,close:FLOAT,volume:FLOAT,vwap:FLOAT,count:INTEGER,timestamp:INTEGER,datetime:TIMESTAMP,rsi:FLOAT,macd:FLOAT,macd_signal:FLOAT,macd_histogram:FLOAT,sma_20:FLOAT,sma_50:FLOAT,sma_200:FLOAT,ema_12:FLOAT,ema_26:FLOAT,ema_50:FLOAT,bollinger_upper:FLOAT,bollinger_middle:FLOAT,bollinger_lower:FLOAT,atr:FLOAT,adx:FLOAT,obv:FLOAT,roc:FLOAT,momentum:FLOAT,stoch_k:FLOAT,stoch_d:FLOAT,willr:FLOAT,cci:FLOAT,ppo:FLOAT,pvo:FLOAT,kama:FLOAT,trix:FLOAT,ultimate_oscillator:FLOAT,awesome_oscillator:FLOAT,fetch_timestamp:TIMESTAMP

echo "Created crypto_analysis"

# 2. crypto_hourly_data
bq mk --table $PROJECT:$DATASET.crypto_hourly_data \
  pair:STRING,altname:STRING,base:STRING,quote:STRING,open:FLOAT,high:FLOAT,low:FLOAT,close:FLOAT,volume:FLOAT,vwap:FLOAT,count:INTEGER,timestamp:INTEGER,datetime:TIMESTAMP,rsi:FLOAT,macd:FLOAT,macd_signal:FLOAT,macd_histogram:FLOAT,sma_20:FLOAT,sma_50:FLOAT,sma_200:FLOAT,ema_12:FLOAT,ema_26:FLOAT,ema_50:FLOAT,bollinger_upper:FLOAT,bollinger_middle:FLOAT,bollinger_lower:FLOAT,atr:FLOAT,adx:FLOAT,obv:FLOAT,roc:FLOAT,momentum:FLOAT,stoch_k:FLOAT,stoch_d:FLOAT,willr:FLOAT,cci:FLOAT,ppo:FLOAT,pvo:FLOAT,kama:FLOAT,trix:FLOAT,ultimate_oscillator:FLOAT,awesome_oscillator:FLOAT,fetch_timestamp:TIMESTAMP,hour:INTEGER

echo "Created crypto_hourly_data"

# 3. crypto_5min_top10_gainers
bq mk --table $PROJECT:$DATASET.crypto_5min_top10_gainers \
  pair:STRING,open:FLOAT,high:FLOAT,low:FLOAT,close:FLOAT,volume:FLOAT,vwap:FLOAT,count:INTEGER,timestamp:INTEGER,datetime:TIMESTAMP,rsi:FLOAT,macd:FLOAT,macd_signal:FLOAT,macd_histogram:FLOAT,sma_20:FLOAT,sma_50:FLOAT,ema_12:FLOAT,ema_26:FLOAT,bollinger_upper:FLOAT,bollinger_middle:FLOAT,bollinger_lower:FLOAT,atr:FLOAT,adx:FLOAT,obv:FLOAT,roc:FLOAT,momentum:FLOAT,stoch_k:FLOAT,stoch_d:FLOAT,willr:FLOAT,cci:FLOAT,ppo:FLOAT,pvo:FLOAT,kama:FLOAT,trix:FLOAT,ultimate_oscillator:FLOAT,awesome_oscillator:FLOAT,fetch_timestamp:TIMESTAMP,hourly_gain_pct:FLOAT,rank:INTEGER

echo "Created crypto_5min_top10_gainers"

# 4. stock_analysis (daily stock data)
bq mk --table $PROJECT:$DATASET.stock_analysis \
  symbol:STRING,name:STRING,sector:STRING,industry:STRING,open:FLOAT,high:FLOAT,low:FLOAT,close:FLOAT,volume:FLOAT,datetime:TIMESTAMP,date:DATE,rsi:FLOAT,macd:FLOAT,macd_signal:FLOAT,macd_histogram:FLOAT,sma_20:FLOAT,sma_50:FLOAT,sma_200:FLOAT,ema_12:FLOAT,ema_26:FLOAT,ema_50:FLOAT,bollinger_upper:FLOAT,bollinger_middle:FLOAT,bollinger_lower:FLOAT,atr:FLOAT,adx:FLOAT,obv:FLOAT,roc:FLOAT,momentum:FLOAT,stoch_k:FLOAT,stoch_d:FLOAT,willr:FLOAT,cci:FLOAT,ppo:FLOAT,pvo:FLOAT,kama:FLOAT,trix:FLOAT,ultimate_oscillator:FLOAT,awesome_oscillator:FLOAT,fetch_timestamp:TIMESTAMP

echo "Created stock_analysis"

# 5. stock_hourly_data
bq mk --table $PROJECT:$DATASET.stock_hourly_data \
  symbol:STRING,name:STRING,sector:STRING,open:FLOAT,high:FLOAT,low:FLOAT,close:FLOAT,volume:FLOAT,datetime:TIMESTAMP,rsi:FLOAT,macd:FLOAT,macd_signal:FLOAT,macd_histogram:FLOAT,sma_20:FLOAT,sma_50:FLOAT,ema_12:FLOAT,ema_26:FLOAT,bollinger_upper:FLOAT,bollinger_middle:FLOAT,bollinger_lower:FLOAT,atr:FLOAT,adx:FLOAT,obv:FLOAT,fetch_timestamp:TIMESTAMP

echo "Created stock_hourly_data"

# 6. stock_5min_top10_gainers
bq mk --table $PROJECT:$DATASET.stock_5min_top10_gainers \
  symbol:STRING,open:FLOAT,high:FLOAT,low:FLOAT,close:FLOAT,volume:FLOAT,datetime:TIMESTAMP,rsi:FLOAT,macd:FLOAT,macd_signal:FLOAT,macd_histogram:FLOAT,sma_20:FLOAT,sma_50:FLOAT,ema_12:FLOAT,ema_26:FLOAT,bollinger_upper:FLOAT,bollinger_middle:FLOAT,bollinger_lower:FLOAT,atr:FLOAT,adx:FLOAT,obv:FLOAT,fetch_timestamp:TIMESTAMP,hourly_gain_pct:FLOAT,rank:INTEGER

echo "Created stock_5min_top10_gainers"

# 7. cryptos_weekly_summary
bq mk --table $PROJECT:$DATASET.cryptos_weekly_summary \
  symbol:STRING,name:STRING,category:STRING,market_cap_category:STRING,volatility_category:STRING,week_open:FLOAT,week_high:FLOAT,week_low:FLOAT,week_close:FLOAT,week_volume:FLOAT,price_change_pct:FLOAT,avg_rsi:FLOAT,trend_direction:STRING,support_level:FLOAT,resistance_level:FLOAT,fetch_timestamp:TIMESTAMP

echo "Created cryptos_weekly_summary"

# 8. scheduler_execution_log
bq mk --table $PROJECT:$DATASET.scheduler_execution_log \
  scheduler_name:STRING,execution_date:DATE,execution_time:TIMESTAMP,status:STRING,records_processed:INTEGER,error_message:STRING,duration_seconds:FLOAT

echo "Created scheduler_execution_log"

# 9. search_history
bq mk --table $PROJECT:$DATASET.search_history \
  user_id:STRING,query:STRING,asset_type:STRING,results_count:INTEGER,search_timestamp:TIMESTAMP

echo "Created search_history"

# 10. users table
bq mk --table $PROJECT:$DATASET.users \
  user_id:STRING,email:STRING,username:STRING,password_hash:STRING,role:STRING,first_login_completed:BOOLEAN,created_at:TIMESTAMP,last_login:TIMESTAMP,token:STRING

echo "Created users"

echo ""
echo "✅ All tables created successfully!"
echo ""
echo "Verify at: https://console.cloud.google.com/bigquery?project=$PROJECT"
