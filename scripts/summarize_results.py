"""Summarize the KNIME Results in results/ (confusion matrices exported by the Scorers).

Per-class metrics are recomputed from the confusion matrices, whose rows are the
true Target values and whose columns are the predictions.

    python3 scripts/summarize_results.py
"""
import csv
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "results"


def confusion(name):
    rows = list(csv.reader(open(RESULTS / f"{name}_confusion.csv")))
    labels = rows[0]
    m = [[int(v) for v in r] for r in rows[1:]]
    return labels, m


def kappa(m):
    n = sum(map(sum, m))
    po = sum(m[i][i] for i in range(len(m))) / n
    pe = sum(sum(m[i]) * sum(r[i] for r in m) for i in range(len(m))) / n ** 2
    return (po - pe) / (1 - pe)


for name in ["wine_knn", "wine_rf", "adult_knn", "adult_rf"]:
    labels, m = confusion(name)
    n = sum(map(sum, m))
    correct = sum(m[i][i] for i in range(len(m)))
    actual = [sum(r) for r in m]
    predicted = [sum(r[i] for r in m) for i in range(len(m))]
    print(f"## {name}: n={n} accuracy={correct / n:.4f} kappa={kappa(m):.4f} "
          f"majority baseline={max(actual) / n:.4f}")
    f1s = []
    for i, lab in sorted(enumerate(labels), key=lambda x: x[1]):
        rec = m[i][i] / actual[i] if actual[i] else float("nan")
        prec = m[i][i] / predicted[i] if predicted[i] else float("nan")
        f1 = 2 * rec * prec / (rec + prec) if predicted[i] and actual[i] and (rec + prec) else 0.0
        f1s.append(f1)
        print(f"   {lab:>6}: true={actual[i]:5d} predicted={predicted[i]:5d} "
              f"recall={rec:.3f} precision={prec:.3f} F1={f1:.3f}")
    print(f"   macro F1={sum(f1s) / len(f1s):.3f}")
