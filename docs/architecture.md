# Architecture

## System Overview

The pipeline processes transaction events in real-time through three stages:

1. **Ingestion** — Python producer generates synthetic transaction events and publishes them to a Kafka topic
2. **Scoring** — Java consumer reads events, applies a logistic regression model, and flags anomalies
3. **Output** — Flagged events are published to a separate Kafka topic for downstream consumption

## Data Flow

```
Synthetic Data Generator (Python)
        |
        | generates CSV / on-the-fly events
        v
Kafka Producer (Python)
        |
        | JSON events → topic: raw-events
        v
Kafka Broker (Confluent 7.5)
        |
        | batch poll (max.poll.records=500)
        v
Java Scoring Service
        |
        | loads model_weights.json at startup
        | for each event:
        |   1. Deserialize JSON → TransactionEvent
        |   2. Extract feature array in model's expected order
        |   3. Apply StandardScaler: (x - mean) / scale
        |   4. Compute: z = w · x_scaled + b
        |   5. Predict: p = sigmoid(z) = 1/(1+e^(-z))
        |   6. If p >= threshold → flag as anomaly
        |
        | flagged events → topic: flagged-anomalies
        v
Output Kafka Topic
```

## Model Scoring Logic

The Java scorer implements logistic regression natively to avoid PMML or Python runtime dependencies:

```
score(x) = sigmoid(w · scale(x) + b)

where:
  scale(x_i) = (x_i - mean_i) / std_i
  sigmoid(z) = 1 / (1 + exp(-z))
  w = model coefficients (18-dimensional vector)
  b = model intercept (scalar)
```

The model weights JSON file contains:
- `coefficients`: Weight vector from sklearn's `model.coef_[0]`
- `intercept`: Bias term from `model.intercept_[0]`
- `scaler.mean`: Feature means from `StandardScaler.mean_`
- `scaler.scale`: Feature standard deviations from `StandardScaler.scale_`
- `threshold`: Decision boundary (0.5 for v2)
- `feature_names`: Ordered list ensuring correct feature alignment

## Kafka Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `max.poll.records` | 500 | Batch processing for throughput |
| `fetch.min.bytes` | 50000 | Reduce broker round-trips |
| `fetch.max.wait.ms` | 200 | Bound latency on light load |
| `batch.size` (producer) | 16384 | Buffer small messages |
| `linger.ms` (producer) | 5 | Brief wait to fill batches |

## Event Schema

```json
{
  "event_id": 1234567890,
  "timestamp": 1700000000000,
  "amount": 150.5,
  "hour_of_day": 14.0,
  "day_of_week": 3.0,
  "merchant_category": 5.0,
  "distance_from_home": 12.3,
  "distance_from_last_txn": 8.1,
  "transaction_frequency": 2.5,
  "avg_transaction_amount": 75.0,
  "time_since_last_txn": 3600.0,
  "is_online": 1.0,
  "card_present": 0.0,
  "merchant_risk_score": 0.7,
  "account_age_days": 365.0,
  "num_failed_txns_24h": 0.0,
  "credit_utilization": 0.45,
  "amount_zscore": 1.2,
  "velocity_1h": 5.0,
  "is_foreign": 0.0
}
```

## Flagged Anomaly Schema

```json
{
  "event_id": 1234567890,
  "timestamp": 1700000000000,
  "fraud_score": 0.97,
  "amount": 150.5
}
```
