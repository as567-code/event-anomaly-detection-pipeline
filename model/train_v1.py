"""Train v1 baseline logistic regression model — balanced weights, no scaling."""

import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from data_generator import generate_v1_dataset

THRESHOLD = 0.80


def train_v1():
    data_path = "data/synthetic_transactions_v1.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
    else:
        df = generate_v1_dataset()

    feature_cols = [c for c in df.columns if c != "is_fraud"]
    X = df[feature_cols].values
    y = df["is_fraud"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = LogisticRegression(
        C=1.0, max_iter=1000, class_weight="balanced", random_state=42
    )
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    y_pred = (proba >= THRESHOLD).astype(int)

    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    print("=== V1 Baseline Model Results ===")
    print(f"Threshold: {THRESHOLD}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"Confusion Matrix:\n{cm}")

    os.makedirs("artifacts", exist_ok=True)
    joblib.dump(model, "artifacts/model_v1.joblib")

    weights = {
        "version": "v1",
        "n_features": len(feature_cols),
        "feature_names": feature_cols,
        "coefficients": model.coef_[0].tolist(),
        "intercept": model.intercept_[0],
        "threshold": THRESHOLD,
    }
    with open("artifacts/model_v1_weights.json", "w") as f:
        json.dump(weights, f, indent=2)

    os.makedirs("metrics", exist_ok=True)
    metrics = {
        "version": "v1",
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "test_samples": len(y_test),
        "threshold": THRESHOLD,
    }
    with open("metrics/v1_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nModel saved to artifacts/model_v1.joblib")
    print(f"Metrics saved to metrics/v1_metrics.json")
    return metrics


if __name__ == "__main__":
    train_v1()
