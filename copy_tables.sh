#!/bin/bash
SRC=cryptobot-462709:crypto_trading_data
DST=aialgotradehits:crypto_trading_data

echo "Copying crypto_analysis..."
bq cp --force $SRC.crypto_analysis $DST.crypto_analysis

echo "Copying crypto_hourly_data..."
bq cp --force $SRC.crypto_hourly_data $DST.crypto_hourly_data

echo "Copying crypto_5min_top10_gainers..."
bq cp --force $SRC.crypto_5min_top10_gainers $DST.crypto_5min_top10_gainers

echo "Copying stock_analysis..."
bq cp --force $SRC.stock_analysis $DST.stock_analysis

echo "Copying stock_hourly_data..."
bq cp --force $SRC.stock_hourly_data $DST.stock_hourly_data

echo "Copying stock_5min_top10_gainers..."
bq cp --force $SRC.stock_5min_top10_gainers $DST.stock_5min_top10_gainers

echo "Copying cryptos_weekly_summary..."
bq cp --force $SRC.cryptos_weekly_summary $DST.cryptos_weekly_summary

echo "Copying users..."
bq cp --force $SRC.users $DST.users

echo "Done!"
