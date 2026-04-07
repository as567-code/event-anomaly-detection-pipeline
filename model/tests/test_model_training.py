"""Tests for model training and evaluation."""

import json
import os
import sys

import joblib

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Artifacts live under model/ (where training scripts run from)
MODEL_DIR = os.path.join(PROJECT_ROOT, "model", "artifacts")
METRICS_DIR = os.path.join(PROJECT_ROOT, "model", "metrics")


def test_v1_model_exists():
    assert os.path.exists(os.path.join(MODEL_DIR, "model_v1.joblib"))


def test_v2_model_exists():
    assert os.path.exists(os.path.join(MODEL_DIR, "model_v2.joblib"))


def test_v1_model_loads():
    model = joblib.load(os.path.join(MODEL_DIR, "model_v1.joblib"))
    assert hasattr(model, "predict")
    assert hasattr(model, "predict_proba")


def test_v2_model_loads():
    artifact = joblib.load(os.path.join(MODEL_DIR, "model_v2.joblib"))
    assert "model" in artifact
    assert "scaler" in artifact
    assert hasattr(artifact["model"], "predict")


def test_v1_weights_json():
    path = os.path.join(MODEL_DIR, "model_v1_weights.json")
    assert os.path.exists(path)
    with open(path) as f:
        weights = json.load(f)
    assert weights["version"] == "v1"
    assert len(weights["coefficients"]) == weights["n_features"]
    assert "intercept" in weights
    assert "threshold" in weights


def test_v2_weights_json():
    path = os.path.join(MODEL_DIR, "model_weights.json")
    assert os.path.exists(path)
    with open(path) as f:
        weights = json.load(f)
    assert weights["version"] == "v2"
    assert len(weights["coefficients"]) == weights["n_features"]
    assert "scaler" in weights
    assert len(weights["scaler"]["mean"]) == weights["n_features"]
    assert len(weights["scaler"]["scale"]) == weights["n_features"]


def test_v1_precision_range():
    with open(os.path.join(METRICS_DIR, "v1_metrics.json")) as f:
        m = json.load(f)
    assert m["precision"] > 0.80, f"V1 precision {m['precision']} too low"


def test_v2_precision_target():
    with open(os.path.join(METRICS_DIR, "v2_metrics.json")) as f:
        m = json.load(f)
    assert m["precision"] >= 0.91, f"V2 precision {m['precision']} below 0.91 target"
