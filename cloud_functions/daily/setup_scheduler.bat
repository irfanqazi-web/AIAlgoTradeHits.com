@echo off
REM Setup Google Cloud Scheduler to trigger the Cloud Function daily at midnight
REM Run this AFTER deploying the Cloud Function

REM Configuration
set PROJECT_ID=molten-optics-310919
set REGION=us-central1
set JOB_NAME=daily-crypto-fetch-job
set FUNCTION_URL=YOUR_CLOUD_FUNCTION_URL

echo ========================================
echo Setting up Cloud Scheduler
echo ========================================
echo.

if "%FUNCTION_URL%"=="YOUR_CLOUD_FUNCTION_URL" (
    echo ERROR: Please edit this file and replace YOUR_CLOUD_FUNCTION_URL with your actual Cloud Function URL
    echo.
    pause
    exit /b 1
)

echo Creating scheduler job for daily midnight runs...
echo.

gcloud scheduler jobs create http %JOB_NAME% ^
  --location=%REGION% ^
  --schedule="0 0 * * *" ^
  --uri=%FUNCTION_URL% ^
  --http-method=GET ^
  --time-zone="America/New_York" ^
  --project=%PROJECT_ID%

echo.
echo ========================================
echo Cloud Scheduler job created successfully!
echo ========================================
echo.
echo Job will run daily at midnight (00:00) Eastern Time
echo.
echo To manually trigger the job, run:
echo gcloud scheduler jobs run %JOB_NAME% --location=%REGION%
echo.
echo To view job details:
echo gcloud scheduler jobs describe %JOB_NAME% --location=%REGION%
echo.
pause
