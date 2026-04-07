"""Tests for the synthetic data generator."""

import os
import sys
import tempfile

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data_generator import generate_v1_dataset, generate_v2_dataset, FEATURE_NAMES, ENGINEERED_FEATURES


def test_v1_dataset_shape():
    with tempfile.TemporaryDirectory() as tmpdir:
        df = generate_v1_dataset(output_dir=tmpdir)
        assert df.shape[0] == 50000
        assert df.shape[1] == len(FEATURE_NAMES) + 1  # +1 for is_fraud


def test_v2_dataset_shape():
    with tempfile.TemporaryDirectory() as tmpdir:
        df = generate_v2_dataset(output_dir=tmpdir)
        assert df.shape[0] == 50000
        expected_cols = len(FEATURE_NAMES) + len(ENGINEERED_FEATURES) + 1
        assert df.shape[1] == expected_cols


def test_v1_class_distribution():
    with tempfile.TemporaryDirectory() as tmpdir:
        df = generate_v1_dataset(output_dir=tmpdir)
        fraud_rate = df["is_fraud"].mean()
        # Fraud rate should be roughly 5-10% (make_classification with weights=[0.95, 0.05])
        assert 0.02 < fraud_rate < 0.15


def test_v2_class_distribution():
    with tempfile.TemporaryDirectory() as tmpdir:
        df = generate_v2_dataset(output_dir=tmpdir)
        fraud_rate = df["is_fraud"].mean()
        assert 0.02 < fraud_rate < 0.15


def test_no_nan_values():
    with tempfile.TemporaryDirectory() as tmpdir:
        df1 = generate_v1_dataset(output_dir=tmpdir)
        df2 = generate_v2_dataset(output_dir=tmpdir)
        assert df1.isna().sum().sum() == 0
        assert df2.isna().sum().sum() == 0


def test_v2_has_engineered_features():
    with tempfile.TemporaryDirectory() as tmpdir:
        df = generate_v2_dataset(output_dir=tmpdir)
        for feat in ENGINEERED_FEATURES:
            assert feat in df.columns, f"Missing engineered feature: {feat}"


def test_csv_written():
    with tempfile.TemporaryDirectory() as tmpdir:
        generate_v1_dataset(output_dir=tmpdir)
        generate_v2_dataset(output_dir=tmpdir)
        assert os.path.exists(os.path.join(tmpdir, "synthetic_transactions_v1.csv"))
        assert os.path.exists(os.path.join(tmpdir, "synthetic_transactions_v2.csv"))
