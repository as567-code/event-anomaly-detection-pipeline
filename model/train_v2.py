"""Train v2 improved logistic regression model with scaling and engineered features."""

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
from sklearn.preprocessing import StandardScaler

from data_generator import generate_v2_dataset

THRESHOLD = 0.5


def train_v2():
    data_path = "data/synthetic_transactions_v2.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
    else:
        df = generate_v2_dataset()

    feature_cols = [c for c in df.columns if c != "is_fraud"]
    X = df[feature_cols].values
    y = df["is_fraud"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(C=0.5, max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)

    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    print("=== V2 Improved Model Results ===")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"Confusion Matrix:\n{cm}")

    os.makedirs("artifacts", exist_ok=True)
    joblib.dump({"model": model, "scaler": scaler}, "artifacts/model_v2.joblib")

    weights = {
        "version": "v2",
        "n_features": len(feature_cols),
        "feature_names": feature_cols,
        "coefficients": model.coef_[0].tolist(),
        "intercept": model.intercept_[0],
        "threshold": THRESHOLD,
        "scaler": {
            "mean": scaler.mean_.tolist(),
            "scale": scaler.scale_.tolist(),
        },
    }
    with open("artifacts/model_weights.json", "w") as f:
        json.dump(weights, f, indent=2)

    os.makedirs("metrics", exist_ok=True)
    metrics = {
        "version": "v2",
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
    with open("metrics/v2_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nModel saved to artifacts/model_v2.joblib")
    print(f"Weights saved to artifacts/model_weights.json")
    print(f"Metrics saved to metrics/v2_metrics.json")
    return metrics


if __name__ == "__main__":
    train_v2()
