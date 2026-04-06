"""Compare metrics across v1 and v2 model releases."""

import json
import os
import sys


def compare():
    metrics_dir = os.path.join(os.path.dirname(__file__), "..", "metrics")

    v1_path = os.path.join(metrics_dir, "v1_metrics.json")
    v2_path = os.path.join(metrics_dir, "v2_metrics.json")

    if not os.path.exists(v1_path) or not os.path.exists(v2_path):
        print("Missing metrics files. Run train_v1.py and train_v2.py first.")
        sys.exit(1)

    with open(v1_path) as f:
        v1 = json.load(f)
    with open(v2_path) as f:
        v2 = json.load(f)

    fp_reduction = (v1["false_positives"] - v2["false_positives"]) / v1["false_positives"] * 100

    print(f"{'Metric':<20} {'v1':>10} {'v2':>10} {'Change':>10}")
    print("-" * 55)
    print(f"{'Precision':<20} {v1['precision']:>10.4f} {v2['precision']:>10.4f} {v2['precision']-v1['precision']:>+10.4f}")
    print(f"{'Recall':<20} {v1['recall']:>10.4f} {v2['recall']:>10.4f} {v2['recall']-v1['recall']:>+10.4f}")
    print(f"{'F1':<20} {v1['f1']:>10.4f} {v2['f1']:>10.4f} {v2['f1']-v1['f1']:>+10.4f}")
    print(f"{'False Positives':<20} {v1['false_positives']:>10d} {v2['false_positives']:>10d} {v2['false_positives']-v1['false_positives']:>+10d}")
    print(f"{'FP Reduction':<20} {'':>10} {'':>10} {fp_reduction:>+9.1f}%")


if __name__ == "__main__":
    compare()
