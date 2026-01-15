# Required GCP Permissions for AIAlgoTradeHits

## Service Account Permissions Needed

The Cloud Functions run using the default compute service account:
`1075463475276-compute@developer.gserviceaccount.com`

This service account needs the following roles to function properly:

### BigQuery Permissions
```bash
# Grant BigQuery Data Editor (to insert data)
gcloud projects add-iam-policy-binding aialgotradehits \
  --member="serviceAccount:1075463475276-compute@developer.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

# Grant BigQuery Job User (to run queries)
gcloud projects add-iam-policy-binding aialgotradehits \
  --member="serviceAccount:1075463475276-compute@developer.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"
```

### Vertex AI Permissions (for Smart Search)
```bash
# Grant Vertex AI User
gcloud projects add-iam-policy-binding aialgotradehits \
  --member="serviceAccount:1075463475276-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Alternative: GCP Console Method
1. Go to https://console.cloud.google.com/iam-admin/iam?project=aialgotradehits
2. Find service account: `1075463475276-compute@developer.gserviceaccount.com`
3. Click Edit (pencil icon)
4. Add the following roles:
   - BigQuery Data Editor
   - BigQuery Job User
   - Vertex AI User
5. Click Save

## Public Access (Optional)

The org policy restricts public access. To allow unauthenticated invocations:
1. Go to IAM & Admin > Organization Policies
2. Find "Domain Restricted Sharing" policy
3. Customize to allow allUsers

Or use Cloud Scheduler with service account authentication instead of public access.

## Current Cloud Functions
- `twelvedata-fetcher`: https://us-central1-aialgotradehits.cloudfunctions.net/twelvedata-fetcher
- `smart-search`: https://us-central1-aialgotradehits.cloudfunctions.net/smart-search

## Testing with Authentication
```bash
# Get identity token
TOKEN=$(gcloud auth print-identity-token)

# Test TwelveData fetcher
curl -H "Authorization: Bearer $TOKEN" \
  "https://us-central1-aialgotradehits.cloudfunctions.net/twelvedata-fetcher?asset_type=stocks&timeframe=daily&limit=3&test=true"

# Test Smart Search
curl -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "show me oversold stocks"}' \
  "https://us-central1-aialgotradehits.cloudfunctions.net/smart-search"
```
