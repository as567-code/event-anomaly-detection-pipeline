"""Validate model scoring throughput meets target."""

import json
import os
import time

import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WEIGHTS_PATH = os.path.join(PROJECT_ROOT, "artifacts", "model_weights.json")


def test_python_scoring_throughput():
    """Test that vectorized Python scoring exceeds 10K events/sec (reference benchmark)."""
    with open(WEIGHTS_PATH) as f:
        weights = json.load(f)

    coef = np.array(weights["coefficients"])
    intercept = weights["intercept"]
    has_scaler = "scaler" in weights
    if has_scaler:
        mean = np.array(weights["scaler"]["mean"])
        scale = np.array(weights["scaler"]["scale"])

    n_events = 100000
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
    assert rate >= 10000, f"Throughput {rate:.0f} events/sec < 10,000 target"


def test_scoring_produces_valid_probabilities():
    """Verify all scored probabilities are in [0, 1]."""
    with open(WEIGHTS_PATH) as f:
        weights = json.load(f)

    coef = np.array(weights["coefficients"])
    intercept = weights["intercept"]

    events = np.random.randn(1000, len(coef))
    if "scaler" in weights:
        mean = np.array(weights["scaler"]["mean"])
        scale = np.array(weights["scaler"]["scale"])
        events = (events - mean) / scale

    z = events @ coef + intercept
    scores = 1.0 / (1.0 + np.exp(-z))

    assert np.all(scores >= 0.0)
    assert np.all(scores <= 1.0)
