"""
Constraint-aware synthetic EGG feature generator.

Usage:
    python generate_synthetic.py path\to\eggfeatures.zip --per-class 500

Output:
    combined_real_egg_features.csv
    synthetic_egg_features.csv
    balanced_training_dataset.csv
    synthetic_validation_report.json

Important:
- With only one real seed for some classes, this is augmentation around observed
  examples plus domain/mathematical constraints; it is not evidence of learned
  population variability.
- Synthetic rows should not be used as an independent test set.
"""
import argparse, zipfile, tempfile, json
from pathlib import Path
import numpy as np
import pandas as pd

TARGET = "Detected_Rhythm"
RNG = np.random.default_rng(42)

def load_table(path):
    return pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)

def load_zip(zip_path):
    frames = []
    with tempfile.TemporaryDirectory() as td:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(td)
        for p in Path(td).rglob("*"):
            if p.is_file() and p.suffix.lower() in {".csv", ".xlsx", ".xls"}:
                try:
                    d = load_table(p)
                    d.columns = d.columns.astype(str).str.strip()
                    d["Source_File"] = p.name
                    frames.append(d)
                except Exception:
                    pass
    if not frames:
        raise ValueError("No readable CSV/Excel feature files found in ZIP")
    return pd.concat(frames, ignore_index=True)

def robust_scale(s):
    s = pd.to_numeric(s, errors="coerce").dropna()
    if len(s) >= 4:
        q1, q3 = s.quantile([0.25, 0.75])
        scale = (q3-q1)/1.349
    elif len(s) >= 2:
        scale = s.std(ddof=1)
    else:
        scale = abs(s.iloc[0])*0.05 if len(s) else 0.01
    if not np.isfinite(scale) or scale == 0:
        center = abs(s.median()) if len(s) else 1.0
        scale = max(center*0.03, 1e-8)
    return float(scale)

def synthesize(real, per_class):
    numeric_cols = real.select_dtypes(include=[np.number]).columns.tolist()
    rows = []
    global_scales = {c: robust_scale(real[c]) for c in numeric_cols}

    for label, grp in real.groupby(TARGET):
        grp = grp.reset_index(drop=True)
        for _ in range(per_class):
            seed = grp.iloc[RNG.integers(0, len(grp))].copy()
            row = seed.copy()

            for c in numeric_cols:
                val = pd.to_numeric(pd.Series([seed[c]]), errors="coerce").iloc[0]
                if pd.isna(val):
                    val = pd.to_numeric(real[c], errors="coerce").median()
                # Conservative jitter: class scale when possible, otherwise global scale.
                class_scale = robust_scale(grp[c])
                scale = class_scale if len(grp) >= 2 else global_scales[c]
                row[c] = float(val + RNG.normal(0, 0.08 * scale))

            row[TARGET] = label
            row["Source_File"] = "synthetic"
            row["Synthetic"] = True
            rows.append(row)

    syn = pd.DataFrame(rows)

    # ---- Enforce exact/near-exact mathematical relationships ----
    if {"Maximum","Minimum","Peak_to_Peak"}.issubset(syn.columns):
        syn["Peak_to_Peak"] = syn["Maximum"] - syn["Minimum"]
    if {"Maximum","Minimum","Signal_Range"}.issubset(syn.columns):
        syn["Signal_Range"] = syn["Maximum"] - syn["Minimum"]
    if {"Standard_Deviation","Variance"}.issubset(syn.columns):
        syn["Standard_Deviation"] = syn["Standard_Deviation"].abs()
        syn["Variance"] = syn["Standard_Deviation"] ** 2
    if {"Mean","RMS"}.issubset(syn.columns):
        syn["RMS"] = np.maximum(syn["RMS"].abs(), syn["Mean"].abs())
    if {"Energy","Signal_Length","Power"}.issubset(syn.columns):
        syn["Signal_Length"] = np.maximum(np.rint(syn["Signal_Length"]), 1)
        syn["Energy"] = syn["Energy"].clip(lower=0)
        syn["Power"] = syn["Energy"] / syn["Signal_Length"]
    if {"Dominant_Frequency_CPM","Dominant_Frequency_Hz"}.issubset(syn.columns):
        syn["Dominant_Frequency_CPM"] = syn["Dominant_Frequency_CPM"].clip(lower=0)
        syn["Dominant_Frequency_Hz"] = syn["Dominant_Frequency_CPM"] / 60.0

    # Non-negative quantities
    nonnegative_tokens = ("Energy","Power","Variance","STD","Deviation","RMS","Amplitude",
                          "Activity","Mobility","Complexity","Entropy","Count","Length",
                          "Area","Spread","Flatness","Ratio","RollOff","Flux","IQR")
    for c in syn.select_dtypes(include=[np.number]).columns:
        if any(t.lower() in c.lower() for t in nonnegative_tokens):
            syn[c] = syn[c].clip(lower=0)

    # Integer-like columns
    for c in ["Signal_Length","Peak_Count","Zero_Crossing","Mean_Crossing"]:
        if c in syn.columns:
            syn[c] = np.maximum(np.rint(syn[c]), 0).astype(int)

    return syn

def validation_report(real, syn):
    num = [c for c in real.select_dtypes(include=[np.number]).columns if c in syn.columns]
    mean_rel_errors = {}
    for c in num:
        rm = pd.to_numeric(real[c], errors="coerce").mean()
        sm = pd.to_numeric(syn[c], errors="coerce").mean()
        denom = max(abs(rm), 1e-9)
        mean_rel_errors[c] = float(abs(sm-rm)/denom)
    return {
        "real_rows": int(len(real)),
        "synthetic_rows": int(len(syn)),
        "real_class_distribution": {str(k): int(v) for k,v in real[TARGET].value_counts().items()},
        "synthetic_class_distribution": {str(k): int(v) for k,v in syn[TARGET].value_counts().items()},
        "median_relative_mean_error": float(np.median(list(mean_rel_errors.values()))),
        "per_feature_relative_mean_error": mean_rel_errors,
        "warning": "Synthetic data augments scarce observations; do not claim it represents independent real subjects."
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zip_path")
    ap.add_argument("--per-class", type=int, default=500)
    ap.add_argument("--output-dir", default="generated_data")
    args = ap.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    real = load_zip(args.zip_path)
    real.columns = real.columns.astype(str).str.strip()
    if TARGET not in real.columns:
        raise ValueError(f"Missing target column {TARGET}")

    real["Synthetic"] = False
    syn = synthesize(real, args.per_class)

    # Balanced training set = all synthetic rows plus real rows.
    balanced = pd.concat([real, syn], ignore_index=True, sort=False)

    real.to_csv(out/"combined_real_egg_features.csv", index=False)
    syn.to_csv(out/"synthetic_egg_features.csv", index=False)
    balanced.to_csv(out/"balanced_training_dataset.csv", index=False)

    report = validation_report(real, syn)
    (out/"synthetic_validation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "message": "Synthetic EGG data generated successfully",
        "real_rows": len(real),
        "synthetic_rows": len(syn),
        "training_rows": len(balanced),
        "output_dir": str(out)
    }))

if __name__ == "__main__":
    main()
