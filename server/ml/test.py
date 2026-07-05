import pandas as pd
import sys
import json
import joblib
import os

from sklearn.metrics import accuracy_score

# TEST DATASET FROM NODE.JS
test_file = sys.argv[1]

# HIDDEN LABEL FILE
labels_file = os.path.join(
    os.path.dirname(__file__),
    "data",
    "test_labels.csv"
)

# LOAD MODEL + FEATURES
model = joblib.load("models/model.pkl")
features = joblib.load("models/features.pkl")

# LOAD TEST DATA
if test_file.lower().endswith(".csv"):
    df = pd.read_csv(test_file)
else:
    df = pd.read_excel(test_file)

# DROP UNUSED COLUMNS
df = df.drop(
    ["Detected_Rhythm", "Source_File"],
    axis=1,
    errors="ignore"
)

# ENSURE SAME FEATURE ORDER
X = df[features]

# PREDICT
pred = model.predict(X)

# CHECK WHETHER LABEL FILE EXISTS
if not os.path.exists(labels_file):
    print(json.dumps({
        "error": "test_labels.csv not found",
        "expected_path": labels_file
    }))
    sys.exit(1)

# LOAD TRUE LABELS
labels_df = pd.read_csv(labels_file)

y_true = labels_df["Detected_Rhythm"]

# CHECK SAME NUMBER OF ROWS
if len(y_true) != len(pred):
    print(json.dumps({
        "error": "Test data and label count do not match",
        "test_rows": len(pred),
        "label_rows": len(y_true)
    }))
    sys.exit(1)

# CALCULATE TEST ACCURACY
acc = accuracy_score(y_true, pred)

# RETURN RESULT
result = {
    "predictions": pred.tolist(),
    "accuracy": float(acc)
}

print(json.dumps(result))