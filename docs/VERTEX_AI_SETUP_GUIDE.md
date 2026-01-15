# Vertex AI Setup Guide for Smart Search

## Current Status
- Smart Search function deployed: `https://smart-search-6pmz2y7ouq-uc.a.run.app`
- Vertex AI API enabled
- **NEEDS**: Service account permissions for Vertex AI

## Steps to Complete in GCP Console

### Step 1: Grant Vertex AI Permissions to Cloud Function

1. Go to [GCP Console](https://console.cloud.google.com)
2. Select project: **aialgotradehits**
3. Navigate to **IAM & Admin** > **IAM**
4. Find the service account: `1075463475276-compute@developer.gserviceaccount.com`
5. Click **Edit** (pencil icon)
6. Click **Add Another Role**
7. Add role: **Vertex AI User** (`roles/aiplatform.user`)
8. Click **Save**

### Step 2: Enable Public Access to Function (Optional)

If you want the function to be publicly accessible:

1. Go to **Cloud Run** in GCP Console
2. Click on **smart-search** service
3. Click **Security** tab
4. Under **Authentication**, select **Allow unauthenticated invocations**
5. Click **Save**

OR via Organization Policy Admin:
1. Go to **IAM & Admin** > **Organization Policies**
2. Find **Domain Restricted Sharing**
3. Customize to allow allUsers

### Step 3: Test the Function

After setting up permissions, test with:

```bash
# With authentication (current setup)
curl -X POST https://smart-search-6pmz2y7ouq-uc.a.run.app \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{"query": "show me oversold stocks"}'

# Or run Python test script
python test_smart_search.py
```

## Alternative: Use Google AI Studio API Key

If Vertex AI permissions are complex, we can use Google AI Studio (Gemini API) directly:

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Get an API key
3. Use the Gemini API directly (simpler, no IAM needed)

## Gemini Models Available

| Model | Use Case | Cost |
|-------|----------|------|
| gemini-1.5-flash | Fast, cheap | $0.075/1M tokens |
| gemini-1.5-pro | Balanced | $3.50/1M tokens |
| gemini-2.0-flash-exp | Latest, experimental | Free during preview |

## Quick Test After Setup

```python
import requests
import subprocess

token = subprocess.run(['gcloud', 'auth', 'print-identity-token'],
                       capture_output=True, text=True).stdout.strip()

response = requests.post(
    'https://smart-search-6pmz2y7ouq-uc.a.run.app',
    json={'query': 'show me oversold stocks'},
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
)

print(response.json())
```
