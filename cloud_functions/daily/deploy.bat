@echo off
REM Deploy Cloud Function for Daily Crypto Data Fetcher (Windows)
REM This script deploys the function to Google Cloud

echo Deploying daily-crypto-fetcher to Google Cloud...
echo.

gcloud functions deploy daily-crypto-fetcher ^
  --gen2 ^
  --runtime=python313 ^
  --region=us-central1 ^
  --source=. ^
  --entry-point=daily_crypto_fetch ^
  --trigger-http ^
  --allow-unauthenticated ^
  --timeout=540s ^
  --memory=512MB ^
  --project=molten-optics-310919

echo.
echo ========================================
echo Cloud Function deployed successfully!
echo ========================================
echo.
echo Copy the Function URL from above and paste it into setup_scheduler.bat
echo.
pause
