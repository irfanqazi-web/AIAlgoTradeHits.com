-- Create 6 new tables with correct naming convention
-- Run in BigQuery console or via bq command

-- 1. CRYPTO DAILY
CREATE TABLE IF NOT EXISTS `cryptobot-462709.crypto_trading_data.daily_crypto`
AS SELECT * FROM `cryptobot-462709.crypto_trading_data.crypto_analysis`;

-- 2. CRYPTO HOURLY
CREATE TABLE IF NOT EXISTS `cryptobot-462709.crypto_trading_data.hourly_crypto`
AS SELECT * FROM `cryptobot-462709.crypto_trading_data.crypto_hourly_data`;

-- 3. CRYPTO 5-MINUTE
CREATE TABLE IF NOT EXISTS `cryptobot-462709.crypto_trading_data.5min_crypto`
AS SELECT * FROM `cryptobot-462709.crypto_trading_data.crypto_5min_top10_gainers`;

-- 4. STOCK DAILY
CREATE TABLE IF NOT EXISTS `cryptobot-462709.crypto_trading_data.daily_stock`
AS SELECT * FROM `cryptobot-462709.crypto_trading_data.stock_analysis`;

-- 5. STOCK HOURLY (empty table, copy schema)
CREATE TABLE IF NOT EXISTS `cryptobot-462709.crypto_trading_data.hourly_stock`
AS SELECT * FROM `cryptobot-462709.crypto_trading_data.stock_hourly_data`
WHERE FALSE;  -- Copy schema only, no data

-- 6. STOCK 5-MINUTE (empty table, copy schema)
CREATE TABLE IF NOT EXISTS `cryptobot-462709.crypto_trading_data.5min_stock`
AS SELECT * FROM `cryptobot-462709.crypto_trading_data.stock_5min_top10_gainers`
WHERE FALSE;  -- Copy schema only, no data
