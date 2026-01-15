@echo off
echo ======================================================================
echo COMPLETING CRYPTOBOT-462709 DEPLOYMENT
echo ======================================================================
echo.

echo Step 1: Making Cloud Functions publicly accessible...
echo.
gcloud functions add-invoker-policy-binding daily-crypto-fetcher --region=us-central1 --member=allUsers --project=cryptobot-462709
gcloud functions add-invoker-policy-binding hourly-crypto-fetcher --region=us-central1 --member=allUsers --project=cryptobot-462709
gcloud functions add-invoker-policy-binding fivemin-top10-fetcher --region=us-central1 --member=allUsers --project=cryptobot-462709

echo.
echo Step 2: Manually triggering functions to populate tables...
echo.
echo Triggering Daily Function (this may take 15-20 minutes)...
curl https://daily-crypto-fetcher-cnyn5l4u2a-uc.a.run.app

echo.
echo Waiting 30 seconds...
timeout /t 30 /nobreak

echo.
echo Triggering Hourly Function (this may take 12-15 minutes)...
curl https://hourly-crypto-fetcher-cnyn5l4u2a-uc.a.run.app

echo.
echo Waiting 30 seconds...
timeout /t 30 /nobreak

echo.
echo Triggering 5-Minute Function (this may take 5-7 minutes)...
curl https://fivemin-top10-fetcher-cnyn5l4u2a-uc.a.run.app

echo.
echo ======================================================================
echo Functions triggered! They will run in the background.
echo Wait 20-30 minutes, then check BigQuery tables for data.
echo ======================================================================
echo.

pause
