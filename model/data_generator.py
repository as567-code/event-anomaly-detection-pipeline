"""Synthetic transaction dataset generator for fraud detection training."""

import os
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification

FEATURE_NAMES = [
    "amount",
    "hour_of_day",
    "day_of_week",
    "merchant_category",
    "distance_from_home",
    "distance_from_last_txn",
    "transaction_frequency",
    "avg_transaction_amount",
    "time_since_last_txn",
    "is_online",
    "card_present",
    "merchant_risk_score",
    "account_age_days",
    "num_failed_txns_24h",
    "credit_utilization",
]

ENGINEERED_FEATURES = ["amount_zscore", "velocity_1h", "is_foreign"]


def generate_v1_dataset(output_dir="data"):
    """Generate v1 baseline dataset with intentionally noisier parameters."""
    X, y = make_classification(
        n_samples=50000,
        n_features=15,
        n_informative=8,
        n_redundant=3,
        class_sep=1.5,
        flip_y=0.06,
        weights=[0.95, 0.05],
        random_state=42,
    )

    df = pd.DataFrame(X, columns=FEATURE_NAMES)
    df["is_fraud"] = y

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "synthetic_transactions_v1.csv")
    df.to_csv(path, index=False)
    print(f"v1 dataset saved to {path}")
    print(f"  Shape: {df.shape}")
    print(f"  Fraud rate: {y.mean():.4f}")
    return df


def generate_v2_dataset(output_dir="data"):
    """Generate v2 dataset with cleaner separation and engineered features."""
    X, y = make_classification(
        n_samples=50000,
        n_features=15,
        n_informative=10,
        n_redundant=2,
        class_sep=2.5,
        flip_y=0.02,
        weights=[0.95, 0.05],
        random_state=42,
    )

    df = pd.DataFrame(X, columns=FEATURE_NAMES)

    # Engineered features
    amount = df["amount"]
    df["amount_zscore"] = (amount - amount.mean()) / amount.std()
    df["velocity_1h"] = df["transaction_frequency"] * np.abs(df["time_since_last_txn"])
    df["is_foreign"] = (df["distance_from_home"] > df["distance_from_home"].quantile(0.9)).astype(float)

    df["is_fraud"] = y

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "synthetic_transactions_v2.csv")
    df.to_csv(path, index=False)
    print(f"v2 dataset saved to {path}")
    print(f"  Shape: {df.shape}")
    print(f"  Fraud rate: {y.mean():.4f}")
    return df


if __name__ == "__main__":
    generate_v1_dataset()
    generate_v2_dataset()
