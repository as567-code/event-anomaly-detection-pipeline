"""Benchmark throughput of the scoring pipeline."""

import json
import os
import re
import subprocess
import sys
import time


def benchmark_docker(duration_seconds=60):
    """Run full pipeline via docker-compose and measure throughput from scorer logs."""
    print(f"Starting throughput benchmark ({duration_seconds}s)...")

    result = subprocess.run(
        ["docker", "compose", "up", "-d"],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    if result.returncode != 0:
        print(f"docker compose up failed: {result.stderr}")
        sys.exit(1)

    print(f"Pipeline running. Collecting logs for {duration_seconds}s...")
    time.sleep(duration_seconds)

    logs = subprocess.run(
        ["docker", "compose", "logs", "scorer"],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ).stdout

    # Parse throughput from scorer logs: "Processed X events (Y events/sec)"
    rates = re.findall(r"(\d+) events/sec", logs)
    rates = [int(r) for r in rates]

    subprocess.run(
        ["docker", "compose", "down"],
        capture_output=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    if rates:
        avg_rate = sum(rates) / len(rates)
        max_rate = max(rates)
        print(f"\nThroughput Results:")
        print(f"  Average: {avg_rate:,.0f} events/sec")
        print(f"  Peak:    {max_rate:,} events/sec")
        print(f"  Target:  10,000 events/sec")
        print(f"  Status:  {'PASS' if max_rate >= 10000 else 'FAIL'}")
        return max_rate
    else:
        print("No throughput data found in logs")
        return 0


def benchmark_local(model_weights_path="artifacts/model_weights.json", n_events=100000):
    """Benchmark model scoring throughput locally (no Kafka)."""
    import numpy as np

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "model"))

    # Simulate scoring in Python for reference
    with open(model_weights_path) as f:
        weights = json.load(f)

    coef = np.array(weights["coefficients"])
    intercept = weights["intercept"]
    has_scaler = "scaler" in weights
    if has_scaler:
        mean = np.array(weights["scaler"]["mean"])
        scale = np.array(weights["scaler"]["scale"])

    n_features = len(coef)
    events = np.random.randn(n_events, n_features)

    start = time.time()
    if has_scaler:
        scaled = (events - mean) / scale
    else:
        scaled = events
    z = scaled @ coef + intercept
    scores = 1.0 / (1.0 + np.exp(-z))
    elapsed = time.time() - start

    rate = n_events / elapsed
    print(f"Python scoring benchmark: {n_events:,} events in {elapsed:.2f}s ({rate:,.0f} events/sec)")
    return rate


if __name__ == "__main__":
    if "--docker" in sys.argv:
        benchmark_docker()
    else:
        benchmark_local()
