"""Validate v2 model meets precision, recall, and F1 targets."""

import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
METRICS_PATH = os.path.join(PROJECT_ROOT, "metrics", "v2_metrics.json")


def load_v2_metrics():
    with open(METRICS_PATH) as f:
        return json.load(f)


def test_precision_meets_target():
    m = load_v2_metrics()
    assert m["precision"] >= 0.91, f"Precision {m['precision']} < 0.91"


def test_recall_reasonable():
    m = load_v2_metrics()
    assert m["recall"] >= 0.50, f"Recall {m['recall']} < 0.50"


def test_f1_reasonable():
    m = load_v2_metrics()
    assert m["f1"] >= 0.60, f"F1 {m['f1']} < 0.60"
