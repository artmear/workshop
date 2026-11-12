"""Cross-check the KNIME Results with scikit-learn on the same preparation.

For each dataset this replicates the KNIME pipeline (Adult: drop rows with '?', one-hot
the categorical Attributes; Wine: red + white combined, type one-hot), uses a 70/30
stratified Partition and min-max normalization fitted on the training part, then runs:

- KNN with k = 3 (same as the KNIME node)
- a forest built with the settings the KNIME 5.12 Random Forest Learner actually saved:
  no bootstrap (every tree sees every training row), one fixed random set of sqrt(m)
  Attributes per tree, fully grown trees, hard majority vote
- a real random forest: bootstrap rows, a new random set of sqrt(m) Attributes at every
  split, 100 trees (scikit-learn RandomForestClassifier, entropy criterion)

The Partition is not the same rows as in KNIME, so numbers are close but not identical.

    python3 scripts/python_reference.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, cohen_kappa_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier

DATA = Path(__file__).resolve().parent.parent / "datasets"
SEED = 1


def load_adult():
    df = pd.read_csv(DATA / "adults" / "adult.csv")
    df = df[(df.workclass != "?") & (df.occupation != "?") & (df["native-country"] != "?")]
    cat = ["workclass", "education", "marital-status", "occupation", "relationship",
           "race", "sex", "native-country"]
    X = pd.get_dummies(df.drop(columns="income"), columns=cat, dtype=float)
    return X, df.income.to_numpy()


def load_wine():
    red = pd.read_csv(DATA / "wines" / "winequality-red.csv", sep=";").assign(red=1.0, white=0.0)
    white = pd.read_csv(DATA / "wines" / "winequality-white.csv", sep=";").assign(red=0.0, white=1.0)
    df = pd.concat([red, white])
    return df.drop(columns="quality"), df.quality.astype(str).to_numpy()


def knime_saved_forest(Xtr, ytr, Xte, n_trees=100):
    """No bootstrap, one fixed sqrt(m) Attribute set per tree, hard majority vote."""
    rng = np.random.default_rng(SEED)
    k = int(np.sqrt(Xtr.shape[1]))
    votes = []
    for i in range(n_trees):
        cols = rng.choice(Xtr.shape[1], k, replace=False)
        tree = DecisionTreeClassifier(random_state=i).fit(Xtr[:, cols], ytr)
        votes.append(tree.predict(Xte[:, cols]))
    votes = np.array(votes)
    out = []
    for column in votes.T:
        values, counts = np.unique(column, return_counts=True)
        out.append(values[counts.argmax()])
    return np.array(out)


for name, (X, y) in [("Wine", load_wine()), ("Adult", load_adult())]:
    Xtr, Xte, ytr, yte = train_test_split(X, y, train_size=0.7, stratify=y, random_state=SEED)
    scaler = MinMaxScaler().fit(Xtr)
    Xtr, Xte = scaler.transform(Xtr), scaler.transform(Xte)
    values, counts = np.unique(yte, return_counts=True)
    print(f"{name}: {X.shape[1]} attributes after one-hot, sqrt = {int(np.sqrt(X.shape[1]))}, "
          f"test rows = {len(yte)}, majority baseline = {counts.max() / len(yte):.4f}")
    models = {
        "KNN (k=3)": lambda: KNeighborsClassifier(3).fit(Xtr, ytr).predict(Xte),
        "forest with KNIME's saved settings": lambda: knime_saved_forest(Xtr, ytr, Xte),
        "real random forest": lambda: RandomForestClassifier(
            100, criterion="entropy", max_features="sqrt", random_state=SEED, n_jobs=-1
        ).fit(Xtr, ytr).predict(Xte),
    }
    for label, run in models.items():
        p = run()
        print(f"  {label:36s} accuracy {accuracy_score(yte, p):.4f}  kappa {cohen_kappa_score(yte, p):.4f}")
