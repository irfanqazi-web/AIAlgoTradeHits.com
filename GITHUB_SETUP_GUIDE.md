# GitHub Setup Guide for Trading Project

## Why GitHub Desktop Doesn't Work Directly with Claude

GitHub deprecated password authentication in 2021. To push code programmatically, you need a **Personal Access Token (PAT)**.

## Step 1: Create a Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** > **"Generate new token (classic)"**
3. Give it a name like "Trading Project"
4. Set expiration to 90 days or "No expiration"
5. Select scopes:
   - `repo` (Full control of private repositories)
6. Click **"Generate token"**
7. **IMPORTANT**: Copy and save the token immediately - you won't see it again!

## Step 2: Create the Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `Trading`
3. Description: "AI Trading Application - Crypto and Stock Data Pipeline"
4. Set to Public or Private
5. Do NOT initialize with README
6. Click **"Create repository"**

## Step 3: Push Code to GitHub

Open Command Prompt in the Trading folder and run:

```bash
cd "C:\Users\irfan\OneDrive - Aretec, Inc\Desktop\1AITrading\Trading"

# Update remote URL with your token
git remote set-url origin https://YOUR_GITHUB_TOKEN@github.com/irfanulhaqqazi/Trading.git

# Push to GitHub
git push -u origin main
```

Replace `YOUR_GITHUB_TOKEN` with the token you created in Step 1.

## Step 4: Use GitHub Desktop (Alternative)

If you prefer GitHub Desktop:
1. Open GitHub Desktop
2. Go to File > Add Local Repository
3. Select `C:\Users\irfan\OneDrive - Aretec, Inc\Desktop\1AITrading\Trading`
4. Click "Publish repository" to create on GitHub and push

## Current Commit Ready to Push

The following files have been committed and are ready to push:
- `.gitignore` - Excludes node_modules, env files, build artifacts
- `CLAUDE.md` - Project documentation
- `cloud_function_api/` - Trading API backend
- `cloud_function_monitoring/` - System monitoring
- `stock-price-app/src/components/TradingDashboard.jsx` - Dashboard with data source indicators
- `stock-price-app/src/services/marketData.js` - Market data service

## One-Click Deploy Script

Until GitHub is set up, use the deploy script on your Desktop:

```bash
python C:\Users\irfan\Desktop\deploy_frontend.py
```

This handles the OneDrive timestamp issues and deploys directly to Cloud Run.

## Frontend URL

https://crypto-trading-app-252370699783.us-central1.run.app

## GCP Backup

Your project is backed up to: `gs://trading-project-backup-irfan/`
