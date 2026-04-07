"""Kafka producer that streams synthetic transaction events."""

import json
import os
import sys
import time

import numpy as np
import pandas as pd
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
TOPIC = os.environ.get("KAFKA_TOPIC", "raw-events")
EVENTS_PER_SECOND = int(os.environ.get("EVENTS_PER_SECOND", "0"))  # 0 = flood mode
DATA_PATH = os.environ.get("DATA_PATH", "data/synthetic_transactions_v2.csv")

FEATURE_NAMES = [
    "amount", "hour_of_day", "day_of_week", "merchant_category",
    "distance_from_home", "distance_from_last_txn", "transaction_frequency",
    "avg_transaction_amount", "time_since_last_txn", "is_online",
    "card_present", "merchant_risk_score", "account_age_days",
    "num_failed_txns_24h", "credit_utilization", "amount_zscore",
    "velocity_1h", "is_foreign",
]


def create_producer(retries=10, delay=5):
    for attempt in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                batch_size=16384,
                linger_ms=5,
                buffer_memory=33554432,
                acks=1,
            )
            print(f"Connected to Kafka at {BOOTSTRAP_SERVERS}")
            return producer
        except NoBrokersAvailable:
            print(f"Kafka not ready (attempt {attempt + 1}/{retries}), retrying in {delay}s...")
            time.sleep(delay)
    print("Failed to connect to Kafka")
    sys.exit(1)


def generate_events():
    """Generate events from CSV or on-the-fly."""
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        feature_cols = [c for c in df.columns if c != "is_fraud"]
        # Pre-convert to list of dicts (much faster than iterrows)
        records = df[feature_cols].to_dict("records")
        for rec in records:
            rec["event_id"] = int(np.random.randint(0, 2**31))
            rec["timestamp"] = int(time.time() * 1000)
            yield rec
    else:
        print(f"Data file not found: {DATA_PATH}, generating on-the-fly")
        while True:
            event = {name: float(np.random.randn()) for name in FEATURE_NAMES}
            event["event_id"] = int(np.random.randint(0, 2**31))
            event["timestamp"] = int(time.time() * 1000)
            yield event


def run():
    producer = create_producer()
    count = 0
    start = time.time()
    last_log = start

    print(f"Producing to topic '{TOPIC}' (rate={'flood' if EVENTS_PER_SECOND == 0 else str(EVENTS_PER_SECOND) + '/s'})")

    try:
        while True:
            for event in generate_events():
                producer.send(TOPIC, value=event)
                count += 1

                if EVENTS_PER_SECOND > 0 and count % EVENTS_PER_SECOND == 0:
                    time.sleep(1.0)

                now = time.time()
                if now - last_log >= 5.0:
                    elapsed = now - start
                    rate = count / elapsed
                    print(f"Sent {count:,} events ({rate:,.0f} events/sec)")
                    last_log = now
    except KeyboardInterrupt:
        pass
    finally:
        producer.flush()
        producer.close()
        elapsed = time.time() - start
        print(f"\nTotal: {count:,} events in {elapsed:.1f}s ({count/elapsed:,.0f} events/sec)")


if __name__ == "__main__":
    run()
