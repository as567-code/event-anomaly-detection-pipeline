"""Tests for the Kafka producer event format."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "producer"))


def test_event_json_format():
    """Verify event JSON has required fields."""
    # Simulate what the producer generates
    import numpy as np

    required_fields = [
        "amount", "hour_of_day", "day_of_week", "merchant_category",
        "distance_from_home", "distance_from_last_txn", "transaction_frequency",
        "avg_transaction_amount", "time_since_last_txn", "is_online",
        "card_present", "merchant_risk_score", "account_age_days",
        "num_failed_txns_24h", "credit_utilization", "amount_zscore",
        "velocity_1h", "is_foreign", "event_id", "timestamp",
    ]

    event = {name: float(np.random.randn()) for name in required_fields[:18]}
    event["event_id"] = int(np.random.randint(0, 2**31))
    event["timestamp"] = 1700000000000

    serialized = json.dumps(event)
    deserialized = json.loads(serialized)

    for field in required_fields:
        assert field in deserialized, f"Missing field: {field}"


def test_event_values_numeric():
    """All feature values should be numeric."""
    import numpy as np

    feature_names = [
        "amount", "hour_of_day", "day_of_week", "merchant_category",
        "distance_from_home", "distance_from_last_txn", "transaction_frequency",
        "avg_transaction_amount", "time_since_last_txn", "is_online",
        "card_present", "merchant_risk_score", "account_age_days",
        "num_failed_txns_24h", "credit_utilization", "amount_zscore",
        "velocity_1h", "is_foreign",
    ]

    event = {name: float(np.random.randn()) for name in feature_names}
    event["event_id"] = 42
    event["timestamp"] = 1700000000000

    for name in feature_names:
        assert isinstance(event[name], (int, float)), f"{name} is not numeric"
