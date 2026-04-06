"""Compare v1 and v2 model metrics and validate improvement targets."""

import json
import os
import sys


def load_metrics(path):
    with open(path) as f:
        return json.load(f)


def evaluate():
    v1 = load_metrics("metrics/v1_metrics.json")
    v2 = load_metrics("metrics/v2_metrics.json")

    v1_fp = v1["false_positives"]
    v2_fp = v2["false_positives"]
    fp_reduction = (v1_fp - v2_fp) / v1_fp * 100 if v1_fp > 0 else 0

    print("=" * 60)
    print("MODEL COMPARISON: v1 (baseline) vs v2 (improved)")
    print("=" * 60)
    print(f"{'Metric':<25} {'v1':>10} {'v2':>10} {'Delta':>10}")
    print("-" * 60)
    print(f"{'Precision':<25} {v1['precision']:>10.4f} {v2['precision']:>10.4f} {v2['precision'] - v1['precision']:>+10.4f}")
    print(f"{'Recall':<25} {v1['recall']:>10.4f} {v2['recall']:>10.4f} {v2['recall'] - v1['recall']:>+10.4f}")
    print(f"{'F1 Score':<25} {v1['f1']:>10.4f} {v2['f1']:>10.4f} {v2['f1'] - v1['f1']:>+10.4f}")
    print(f"{'False Positives':<25} {v1_fp:>10d} {v2_fp:>10d} {v2_fp - v1_fp:>+10d}")
    print(f"{'True Positives':<25} {v1['true_positives']:>10d} {v2['true_positives']:>10d} {v2['true_positives'] - v1['true_positives']:>+10d}")
    print(f"{'FP Reduction':<25} {'':>10} {'':>10} {fp_reduction:>+9.1f}%")
    print("=" * 60)

    # Validation
    passed = True
    checks = [
        ("v2 precision >= 0.91", v2["precision"] >= 0.91),
        ("FP reduction >= 25%", fp_reduction >= 25.0),
    ]

    print("\nVALIDATION CHECKS:")
    for name, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
        if not ok:
            passed = False

    # Write METRICS.md
    write_metrics_md(v1, v2, fp_reduction)

    if not passed:
        print("\nSome validation checks FAILED.")
        sys.exit(1)
    else:
        print("\nAll validation checks PASSED.")

    return {"v1": v1, "v2": v2, "fp_reduction": fp_reduction}


def write_metrics_md(v1, v2, fp_reduction):
    content = f"""# Model Evaluation Metrics

## Summary

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Precision (v2) | 91% | {v2['precision'] * 100:.1f}% | {'PASS' if v2['precision'] >= 0.91 else 'FAIL'} |
| FP Reduction | 25% | {fp_reduction:.1f}% | {'PASS' if fp_reduction >= 25.0 else 'FAIL'} |

## V1 Baseline Model

- **Precision:** {v1['precision']:.4f}
- **Recall:** {v1['recall']:.4f}
- **F1 Score:** {v1['f1']:.4f}
- **Confusion Matrix:**

|  | Predicted Legit | Predicted Fraud |
|--|-----------------|-----------------|
| Actual Legit | {v1['true_negatives']} | {v1['false_positives']} |
| Actual Fraud | {v1['false_negatives']} | {v1['true_positives']} |

## V2 Improved Model

- **Precision:** {v2['precision']:.4f}
- **Recall:** {v2['recall']:.4f}
- **F1 Score:** {v2['f1']:.4f}
- **Confusion Matrix:**

|  | Predicted Legit | Predicted Fraud |
|--|-----------------|-----------------|
| Actual Legit | {v2['true_negatives']} | {v2['false_positives']} |
| Actual Fraud | {v2['false_negatives']} | {v2['true_positives']} |

## False Positive Reduction

- V1 FP: {v1['false_positives']}
- V2 FP: {v2['false_positives']}
- **Reduction: {fp_reduction:.1f}%**
- Formula: `(v1_FP - v2_FP) / v1_FP * 100`
"""
    with open("METRICS.md", "w") as f:
        f.write(content)
    print("Metrics written to METRICS.md")


if __name__ == "__main__":
    evaluate()
