# 🚀 Production Deployment Guide
## ML Model Deployment for Trading Platform

================================================================================
OVERVIEW
================================================================================

This guide covers deploying your trained ML models to production using
Google Vertex AI and Cloud infrastructure.

**Deployment Options:**
1. **Google Vertex AI** (Recommended) - Fully managed, scalable
2. **Cloud Run** - Containerized inference API
3. **Cloud Functions** - Lightweight, event-driven
4. **On-Premise** - Full control, higher maintenance

**Expected Latency:**
- Vertex AI: 50-200ms per prediction
- Cloud Run: 100-300ms per prediction
- Local inference: 10-50ms per prediction

================================================================================
PART 1: VERTEX AI DEPLOYMENT (RECOMMENDED)
================================================================================

## Step 1: Prepare Model for Vertex AI

### 1.1 Export Model in SavedModel Format

```python
import tensorflow as tf
from google.cloud import aiplatform

# For XGBoost/Scikit-learn models, wrap in SavedModel format
import joblib
import numpy as np

# Load your trained model
model = joblib.load('trained_models/xgboost_model.pkl')
scaler = joblib.load('trained_models/feature_scaler.pkl')

# Create a wrapper class
class ModelWrapper(tf.Module):
    def __init__(self, model, scaler, feature_names):
        super().__init__()
        self.model = model
        self.scaler = scaler
        self.feature_names = feature_names
    
    @tf.function(input_signature=[
        tf.TensorSpec(shape=[None, len(feature_names)], dtype=tf.float32)
    ])
    def __call__(self, inputs):
        # Scale inputs
        scaled_inputs = self.scaler.transform(inputs.numpy())
        
        # Predict
        predictions = self.model.predict_proba(scaled_inputs)
        
        return {
            'predictions': tf.constant(predictions[:, 1], dtype=tf.float32),
            'classes': tf.constant(self.model.predict(scaled_inputs), dtype=tf.int32)
        }

# Save as SavedModel
wrapper = ModelWrapper(model, scaler, feature_names)
tf.saved_model.save(wrapper, 'saved_model_dir')
```

### 1.2 Upload Model to Google Cloud Storage

```bash
# Set your GCP project
export PROJECT_ID="your-project-id"
export BUCKET_NAME="your-bucket-name"

# Create bucket if needed
gsutil mb -p $PROJECT_ID -l us-central1 gs://$BUCKET_NAME

# Upload model
gsutil -m cp -r saved_model_dir gs://$BUCKET_NAME/models/xgboost_trading_v1/
```

### 1.3 Deploy to Vertex AI Endpoint

```python
from google.cloud import aiplatform

# Initialize Vertex AI
aiplatform.init(
    project='your-project-id',
    location='us-central1'
)

# Upload model
model = aiplatform.Model.upload(
    display_name='trading_model_xgboost_v1',
    artifact_uri=f'gs://{BUCKET_NAME}/models/xgboost_trading_v1/',
    serving_container_image_uri='us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-6:latest'
)

# Create endpoint
endpoint = aiplatform.Endpoint.create(
    display_name='trading_predictions_endpoint'
)

# Deploy model to endpoint
endpoint.deploy(
    model=model,
    deployed_model_display_name='trading_model_v1',
    machine_type='n1-standard-4',
    min_replica_count=1,
    max_replica_count=5,
    traffic_percentage=100
)

print(f"Model deployed to endpoint: {endpoint.resource_name}")
```

## Step 2: Make Predictions from Your Application

```python
from google.cloud import aiplatform

def predict_trading_signal(features, endpoint_id, project_id, location):
    """
    Make prediction using Vertex AI endpoint
    
    Args:
        features: Dict of feature values
        endpoint_id: Vertex AI endpoint ID
        project_id: GCP project ID
        location: GCP location (e.g., 'us-central1')
    
    Returns:
        Prediction probability
    """
    
    # Initialize endpoint
    endpoint = aiplatform.Endpoint(
        endpoint_name=f'projects/{project_id}/locations/{location}/endpoints/{endpoint_id}'
    )
    
    # Prepare input
    instances = [[features[col] for col in feature_names]]
    
    # Make prediction
    response = endpoint.predict(instances=instances)
    
    return {
        'probability': response.predictions[0],
        'signal': 'BUY' if response.predictions[0] > 0.6 else 'HOLD'
    }

# Example usage
features = {
    'rsi_14d': 35.2,
    'macd_histogram': 0.05,
    'distance_from_vwap_pct': -1.2,
    'volume_ratio': 1.8,
    # ... all other features
}

prediction = predict_trading_signal(
    features=features,
    endpoint_id='your-endpoint-id',
    project_id='your-project-id',
    location='us-central1'
)

print(f"Prediction: {prediction['signal']} (probability: {prediction['probability']:.2%})")
```

## Step 3: Batch Predictions for Multiple Symbols

```python
from google.cloud import aiplatform

def batch_predict(input_data_uri, output_data_uri, model_name):
    """
    Run batch predictions for multiple symbols
    
    Args:
        input_data_uri: GCS URI with input data (JSONL format)
        output_data_uri: GCS URI for output predictions
        model_name: Full model resource name
    
    Returns:
        Batch prediction job
    """
    
    # Create batch prediction job
    batch_prediction_job = aiplatform.BatchPredictionJob.create(
        job_display_name='trading_batch_predictions',
        model_name=model_name,
        instances_format='jsonl',
        predictions_format='jsonl',
        gcs_source=input_data_uri,
        gcs_destination_prefix=output_data_uri,
        machine_type='n1-standard-4'
    )
    
    # Wait for completion
    batch_prediction_job.wait()
    
    return batch_prediction_job

# Example usage
batch_predict(
    input_data_uri='gs://your-bucket/batch_inputs/predictions_20241206.jsonl',
    output_data_uri='gs://your-bucket/batch_outputs/',
    model_name='projects/123/locations/us-central1/models/456'
)
```

================================================================================
PART 2: CLOUD RUN DEPLOYMENT (ALTERNATIVE)
================================================================================

## Step 1: Create Inference API

Create `app.py`:

```python
from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load model and scaler at startup
model = joblib.load('xgboost_model.pkl')
scaler = joblib.load('feature_scaler.pkl')

with open('feature_names.txt', 'r') as f:
    feature_names = [line.strip() for line in f]

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict trading signal
    
    Request body:
    {
        "features": {
            "rsi_14d": 35.2,
            "macd_histogram": 0.05,
            ...
        }
    }
    
    Response:
    {
        "probability": 0.75,
        "signal": "BUY",
        "confidence": "HIGH"
    }
    """
    try:
        data = request.json
        features = data['features']
        
        # Convert to array in correct order
        feature_array = np.array([[features[col] for col in feature_names]])
        
        # Scale
        feature_scaled = scaler.transform(feature_array)
        
        # Predict
        proba = model.predict_proba(feature_scaled)[0, 1]
        
        # Determine signal
        if proba > 0.7:
            signal = 'STRONG_BUY'
            confidence = 'HIGH'
        elif proba > 0.6:
            signal = 'BUY'
            confidence = 'MEDIUM'
        elif proba < 0.3:
            signal = 'STRONG_SELL'
            confidence = 'HIGH'
        elif proba < 0.4:
            signal = 'SELL'
            confidence = 'MEDIUM'
        else:
            signal = 'HOLD'
            confidence = 'LOW'
        
        return jsonify({
            'probability': float(proba),
            'signal': signal,
            'confidence': confidence
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

## Step 2: Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy model files
COPY xgboost_model.pkl .
COPY feature_scaler.pkl .
COPY feature_names.txt .
COPY app.py .

# Expose port
EXPOSE 8080

# Run app
CMD ["python", "app.py"]
```

## Step 3: Deploy to Cloud Run

```bash
# Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/trading-api

# Deploy to Cloud Run
gcloud run deploy trading-api \
  --image gcr.io/$PROJECT_ID/trading-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10

# Get service URL
gcloud run services describe trading-api --region us-central1 --format 'value(status.url)'
```

## Step 4: Call API from Your Application

```python
import requests

def get_trading_signal(symbol, features, api_url):
    """
    Get trading signal from API
    
    Args:
        symbol: Trading symbol
        features: Dict of feature values
        api_url: Cloud Run service URL
    
    Returns:
        Prediction dict
    """
    
    response = requests.post(
        f'{api_url}/predict',
        json={'features': features},
        timeout=5
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API error: {response.text}")

# Example usage
api_url = 'https://trading-api-abc123-uc.a.run.app'

features = {
    'rsi_14d': 35.2,
    'macd_histogram': 0.05,
    'distance_from_vwap_pct': -1.2,
    'volume_ratio': 1.8,
    # ... all features
}

signal = get_trading_signal('BTC-USD', features, api_url)
print(signal)
# Output: {'probability': 0.75, 'signal': 'BUY', 'confidence': 'HIGH'}
```

================================================================================
PART 3: MONITORING AND MAINTENANCE
================================================================================

## Set Up Model Monitoring

```python
from google.cloud import aiplatform_v1beta1 as aiplatform

# Create monitoring job
monitoring_config = {
    'alert_config': {
        'email_alert_config': {
            'user_emails': ['your-email@example.com']
        }
    },
    'skew_detection_config': {
        'data_skew_detection_config': {
            'skew_thresholds': {
                'rsi_14d': {'value': 0.1},
                'macd_histogram': {'value': 0.1}
            }
        }
    },
    'drift_detection_config': {
        'drift_thresholds': {
            'rsi_14d': {'value': 0.05},
            'macd_histogram': {'value': 0.05}
        }
    }
}

# Apply monitoring
endpoint.update(
    monitoring_config=monitoring_config
)
```

## Set Up Logging

```python
import logging
from google.cloud import logging as cloud_logging

# Setup Cloud Logging
client = cloud_logging.Client()
client.setup_logging()

logger = logging.getLogger('trading_model')

# Log predictions
def log_prediction(symbol, features, prediction, timestamp):
    """Log prediction for monitoring and debugging"""
    
    logger.info(
        'Prediction made',
        extra={
            'symbol': symbol,
            'prediction': prediction,
            'timestamp': timestamp,
            'features': features
        }
    )
```

## Automated Retraining Pipeline

```python
from google.cloud import aiplatform
from datetime import datetime, timedelta

def retrain_model_monthly():
    """
    Automated monthly retraining pipeline
    """
    
    # 1. Fetch new data (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 2. Load historical model performance
    # Compare current vs new model
    
    # 3. Train new model
    # (Use your training pipeline)
    
    # 4. Validate new model
    # If new_model_accuracy > current_model_accuracy + 0.02:
    #     Deploy new model
    
    # 5. Archive old model
    # Keep for rollback if needed
    
    pass

# Schedule with Cloud Scheduler
# gcloud scheduler jobs create http retrain-model \
#   --schedule="0 0 1 * *" \
#   --uri="https://your-cloud-function-url.cloudfunctions.net/retrain" \
#   --http-method=POST
```

================================================================================
PART 4: PERFORMANCE OPTIMIZATION
================================================================================

## Caching Predictions

```python
from functools import lru_cache
import hashlib
import json

@lru_cache(maxsize=1000)
def cached_prediction(features_hash):
    """Cache predictions for frequently requested features"""
    # Decode hash and make prediction
    # Return cached result if available
    pass

def get_features_hash(features):
    """Create hash of features for caching"""
    return hashlib.md5(json.dumps(features, sort_keys=True).encode()).hexdigest()
```

## Model Quantization

```python
import tensorflow as tf

# For neural network models, quantize to reduce size and latency
converter = tf.lite.TFLiteConverter.from_saved_model('saved_model_dir')
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save quantized model
with open('model_quantized.tflite', 'wb') as f:
    f.write(tflite_model)

# 40-60% size reduction, 2-3x faster inference
```

## Load Balancing

```yaml
# kubernetes deployment config
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: trading-api
  template:
    metadata:
      labels:
        app: trading-api
    spec:
      containers:
      - name: trading-api
        image: gcr.io/project/trading-api:latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

================================================================================
PART 5: COST OPTIMIZATION
================================================================================

## Estimated Costs (Google Cloud)

**Vertex AI Endpoint:**
- n1-standard-4 (4 vCPU, 15GB RAM): $0.27/hour
- 1 replica running 24/7: ~$200/month
- Auto-scaling 1-5 replicas: $200-1000/month

**Cloud Run:**
- $0.00002400 per vCPU-second
- $0.00000250 per GiB-second
- Typical: $50-150/month for moderate traffic

**BigQuery:**
- Storage: $0.02 per GB/month
- Queries: $5 per TB processed
- Typical: $100-300/month for 10GB data

**Total Estimated Monthly Cost:**
- Small deployment: $300-500/month
- Medium deployment: $500-1500/month
- Large deployment: $1500-5000/month

## Cost Reduction Strategies

1. **Use Cloud Run instead of Vertex AI** for low-traffic applications
2. **Implement caching** to reduce redundant predictions
3. **Use batch predictions** for non-real-time analysis
4. **Set up auto-scaling** with minimum replicas = 0
5. **Use committed use discounts** for predictable workloads

================================================================================
NEXT STEPS
================================================================================

1. ✅ Train your models using the training pipeline
2. ✅ Test predictions locally before deploying
3. ✅ Deploy to Vertex AI or Cloud Run
4. ✅ Set up monitoring and alerts
5. ✅ Implement automated retraining
6. ✅ Optimize for performance and cost

**Resources:**
- Vertex AI Documentation: https://cloud.google.com/vertex-ai/docs
- Cloud Run Documentation: https://cloud.google.com/run/docs
- Best Practices: Check /project/ documentation

**Support:**
Contact the development team for deployment assistance.

Happy Deploying! 🚀
================================================================================
