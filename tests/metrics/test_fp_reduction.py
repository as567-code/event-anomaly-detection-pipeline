"""Validate false-positive reduction between v1 and v2 meets target."""

import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
METRICS_DIR = os.path.join(PROJECT_ROOT, "metrics")


def load_metrics():
    with open(os.path.join(METRICS_DIR, "v1_metrics.json")) as f:
        v1 = json.load(f)
    with open(os.path.join(METRICS_DIR, "v2_metrics.json")) as f:
        v2 = json.load(f)
    return v1, v2


def test_fp_reduction_meets_target():
    v1, v2 = load_metrics()
    v1_fp = v1["false_positives"]
    v2_fp = v2["false_positives"]
    assert v1_fp > 0, "V1 has zero false positives — can't compute reduction"
    fp_reduction = (v1_fp - v2_fp) / v1_fp * 100
    assert fp_reduction >= 25.0, f"FP reduction {fp_reduction:.1f}% < 25%"


def test_v2_has_fewer_fp():
    v1, v2 = load_metrics()
    assert v2["false_positives"] < v1["false_positives"], \
        f"V2 FP ({v2['false_positives']}) should be less than V1 FP ({v1['false_positives']})"
