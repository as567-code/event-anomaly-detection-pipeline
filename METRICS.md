# Model Evaluation Metrics

## Summary

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Throughput | 10K events/sec | 12,334 events/sec (live Kafka end-to-end) | PASS |
| Precision (v2) | 91% | 95.0% | PASS |
| FP Reduction | 25% | 66.2% | PASS |

## V1 Baseline Model

- **Precision:** 0.8257
- **Recall:** 0.3934
- **F1 Score:** 0.5329
- **Confusion Matrix:**

|  | Predicted Legit | Predicted Fraud |
|--|-----------------|-----------------|
| Actual Legit | 9152 | 65 |
| Actual Fraud | 475 | 308 |

## V2 Improved Model

- **Precision:** 0.9502
- **Recall:** 0.7131
- **F1 Score:** 0.8147
- **Confusion Matrix:**

|  | Predicted Legit | Predicted Fraud |
|--|-----------------|-----------------|
| Actual Legit | 9389 | 22 |
| Actual Fraud | 169 | 420 |

## False Positive Reduction

- V1 FP: 65
- V2 FP: 22
- **Reduction: 66.2%**
- Formula: `(v1_FP - v2_FP) / v1_FP * 100`

## Throughput Benchmark

**Live Kafka end-to-end test** (Docker Compose, single partition, 2026-04-08)

- **Producer rate:** 12,720-14,570 events/sec (Python, flood mode)
- **Scorer rate:** 12,334 events/sec average (Java, sustained over 70s)
- **Peak scorer interval rate:** 12,650 events/sec (10s window)
- **Total events scored:** 1,334,655 in ~110 seconds
- **Anomalies flagged:** 60,514

Scorer per-interval breakdown:
```
Interval    Events     Rate
10-20s      126,504    12,650/s
20-30s      125,916    12,592/s
30-40s      122,409    12,241/s
40-50s      124,320    12,432/s
50-60s      122,724    12,272/s
60-70s      118,188    11,819/s
```

Configuration: `max.poll.records=500`, `fetch.min.bytes=50000`, single Kafka partition, Docker Desktop on macOS.

Command to reproduce:
```bash
docker compose up -d && sleep 70 && docker compose logs scorer
```
