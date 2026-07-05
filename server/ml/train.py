import pandas as pd
import sys
import json
import joblib

from sklearn.ensemble import RandomForestClassifier

file_path = sys.argv[1]

# LOAD TRAIN DATA
if file_path.endswith(".csv"):
    df = pd.read_csv(file_path)
else:
    df = pd.read_excel(file_path)

# TARGET LABEL
y = df["Detected_Rhythm"]

# DROP LABEL + UNUSED COLUMNS
X = df.drop(
    ["Detected_Rhythm", "Source_File"],
    axis=1,
    errors="ignore"
)

# KEEP NUMERIC FEATURES ONLY
X = X.select_dtypes(include="number")

# MODEL
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

# TRAIN
model.fit(X, y)

# SAVE MODEL + FEATURES
joblib.dump(model, "models/model.pkl")
joblib.dump(X.columns.tolist(), "models/features.pkl")

print(json.dumps({
    "message": "Training Completed"
}))