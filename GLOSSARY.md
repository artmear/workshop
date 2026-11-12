# KNIME workshop: KNN vs Random Forest

A comparison of two classification algorithms (KNN and Random Forest) on two datasets with different characteristics, to discuss why each algorithm does better or worse on each one.

## Datasets

**Wine**:
The Wine Quality dataset with red and white wines combined into one table, where the wine type is just another Attribute.
_Avoid_: wine red / wine white (as separate datasets), wines

**Adult**:
The Adult census income dataset, using only the `adult.data` file (read as `adult.csv`).
_Avoid_: adults, census

**Attribute**:
An input column used to predict the Target; either numeric or categorical.
_Avoid_: feature, variable, column (when talking about inputs)

**Target**:
The column the model predicts: `quality` in Wine (multiclass, grades 3–9) and `income` in Adult (binary, `<=50K` / `>50K`).
_Avoid_: label, class (for the column itself)

**Missing value**:
A cell with no value; in Adult it is written as `?`. Rows with a Missing value are removed.
_Avoid_: null, NA

## Evaluation

**Partition**:
The split of a dataset into 70% training and 30% test, stratified by the Target and shared by both algorithms on that dataset.
_Avoid_: split, cross-validation

**Result**:
The confusion matrix plus metrics (accuracy, Cohen's kappa) produced by the Scorer for one dataset × algorithm combination.
_Avoid_: output, score

**Baseline**:
The accuracy of always predicting the most frequent Target value of the test Partition; a model is only useful if it beats it.
_Avoid_: majority classifier, ZeroR, dummy model
