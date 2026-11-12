"""Convert UCI adult.data to a CSV with a header row and trimmed values.

Missing values stay as "?" so the KNIME Row Filter can drop them.
"""
import csv
import sys

COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education-num", "marital-status",
    "occupation", "relationship", "race", "sex", "capital-gain", "capital-loss",
    "hours-per-week", "native-country", "income",
]

src, dst = sys.argv[1], sys.argv[2]
rows = 0
with open(src, newline="") as fin, open(dst, "w", newline="") as fout:
    w = csv.writer(fout, lineterminator="\n")
    w.writerow(COLUMNS)
    for line in fin:
        line = line.strip()
        if not line:
            continue
        values = [v.strip() for v in line.split(",")]
        if len(values) != len(COLUMNS):
            sys.exit(f"line {rows + 1}: expected {len(COLUMNS)} values, got {len(values)}")
        w.writerow(values)
        rows += 1
print(f"wrote {rows} rows to {dst}")
