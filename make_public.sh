#!/bin/bash
gcloud run services add-iam-policy-binding daily-crypto-fetcher --region=us-central1 --member=allUsers --role=roles/run.invoker --project=aialgotradehits
