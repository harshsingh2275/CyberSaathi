"""
Reproducible URL phishing classifier training pipeline — T-02.

Dataset:  Hannousse & Yahiouche, "Towards a Benchmark of Machine Learning
          Methods for Phishing Websites Detection" (2021).
          File: data/raw/hannousse/dataset_B_05_2020.csv
          License: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
          Source:  https://data.mendeley.com/datasets/c2gw7fy2j4/3

Reproducibility:
    python ml/train_url_model.py

Outputs:
    ml/artifacts/url_model.joblib      — trained sklearn Pipeline
    ml/artifacts/feature_schema.json   — feature names, version, schema
    ml/artifacts/training_report.json  — seed, split sizes, provenance
    ml/reports/evaluation_report.json  — precision, recall, F1, confusion matrix, etc.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "raw" / "hannousse" / "dataset_B_05_2020.csv"
ARTIFACTS_DIR = REPO_ROOT / "ml" / "artifacts"
REPORTS_DIR = REPO_ROOT / "ml" / "reports"

# ── Reproducibility ───────────────────────────────────────────────────────────
RANDOM_SEED = 42
TEST_SIZE = 0.15   # 15% held-out test set
VAL_SIZE = 0.15    # 15% validation set (from the remaining 85%)
# Final split: ~70% train / ~15% val / ~15% test

# ── URL-only feature columns ──────────────────────────────────────────────────
# These 53 features can all be computed from the URL string alone.
# Page-content features (nb_hyperlinks, login_form, etc.) and
# external-service features (whois, dns_record, web_traffic, etc.) are excluded.
FEATURE_NAMES: list[str] = [
    "length_url",
    "length_hostname",
    "ip",
    "nb_dots",
    "nb_hyphens",
    "nb_at",
    "nb_qm",
    "nb_and",
    "nb_or",
    "nb_eq",
    "nb_underscore",
    "nb_tilde",
    "nb_percent",
    "nb_slash",
    "nb_star",
    "nb_colon",
    "nb_comma",
    "nb_semicolumn",
    "nb_dollar",
    "nb_space",
    "nb_www",
    "nb_com",
    "nb_dslash",
    "http_in_path",
    "https_token",
    "ratio_digits_url",
    "ratio_digits_host",
    "punycode",
    "port",
    "tld_in_path",
    "tld_in_subdomain",
    "abnormal_subdomain",
    "nb_subdomains",
    "prefix_suffix",
    "random_domain",
    "shortening_service",
    "path_extension",
    "length_words_raw",
    "char_repeat",
    "shortest_words_raw",
    "shortest_word_host",
    "shortest_word_path",
    "longest_words_raw",
    "longest_word_host",
    "longest_word_path",
    "avg_words_raw",
    "avg_word_host",
    "avg_word_path",
    "phish_hints",
    "domain_in_brand",
    "brand_in_subdomain",
    "brand_in_path",
    "suspecious_tld",
]

assert len(FEATURE_NAMES) == 53


def load_and_validate_dataset(path: Path) -> pd.DataFrame:
    """Load CSV, validate expected columns, drop duplicates, return clean frame."""
    if not path.exists():
        sys.exit(f"ERROR: Dataset not found at {path}")

    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows from {path}")

    # Validate required columns
    missing = [c for c in FEATURE_NAMES + ["url", "status"] if c not in df.columns]
    if missing:
        sys.exit(f"ERROR: Missing columns: {missing}")

    # Label check
    labels = df["status"].unique().tolist()
    print(f"Labels: {labels}")
    expected = {"legitimate", "phishing"}
    unexpected = set(labels) - expected
    if unexpected:
        sys.exit(f"ERROR: Unexpected label values: {unexpected}")

    # Class distribution
    dist = df["status"].value_counts().to_dict()
    print(f"Class distribution: {dist}")

    # Duplicate check
    full_dups = df.duplicated().sum()
    url_dups = df["url"].duplicated().sum()
    print(f"Full-row duplicates: {full_dups}")
    print(f"Duplicate URLs: {url_dups}")

    # Drop duplicate rows (same URL, same label — safe dedup)
    if url_dups > 0:
        df = df.drop_duplicates(subset=["url"], keep="first")
        print(f"After dedup: {len(df)} rows")

    # Missing values in feature columns
    n_missing = df[FEATURE_NAMES].isnull().sum().sum()
    print(f"Missing values in feature columns: {n_missing}")
    if n_missing > 0:
        sys.exit("ERROR: Unexpected missing values in feature columns")

    return df


def build_split(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Leakage-aware stratified split.
    Split happens BEFORE any preprocessing is fit.
    Returns (train_df, val_df, test_df).
    """
    # First carve out the held-out test set
    train_val_df, test_df = train_test_split(
        df, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=df["status"]
    )
    # Then split remaining into train / val
    # Adjust val_size relative to train_val_df
    val_size_adjusted = VAL_SIZE / (1.0 - TEST_SIZE)
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=val_size_adjusted,
        random_state=RANDOM_SEED,
        stratify=train_val_df["status"],
    )
    print(
        f"Split: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}"
    )
    print(
        f"  Train labels: {train_df['status'].value_counts().to_dict()}"
    )
    print(
        f"  Val labels:   {val_df['status'].value_counts().to_dict()}"
    )
    print(
        f"  Test labels:  {test_df['status'].value_counts().to_dict()}"
    )
    return train_df, val_df, test_df


def encode_labels(series: pd.Series) -> np.ndarray:
    """Encode: 'phishing' → 1, 'legitimate' → 0."""
    return (series == "phishing").astype(int).values


def build_pipeline() -> Pipeline:
    """
    Build scikit-learn Pipeline: StandardScaler → RandomForestClassifier.

    RandomForest is robust to feature scale but StandardScaler is included
    for future model swaps.  Preprocessing is fit on training data only.
    """
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            min_samples_leaf=2,
            random_state=RANDOM_SEED,
            n_jobs=-1,
            class_weight="balanced",
        )),
    ])


def evaluate(
    pipeline: Pipeline,
    X: np.ndarray,
    y_true: np.ndarray,
    split_name: str,
) -> dict:
    """Run evaluation and return metrics dict."""
    y_pred = pipeline.predict(X)
    y_prob = pipeline.predict_proba(X)[:, 1]

    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average=None, labels=[0, 1]
    )
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", labels=[0, 1]
    )
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist()
    report = classification_report(
        y_true, y_pred, target_names=["legitimate", "phishing"], output_dict=True
    )

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    metrics = {
        "split": split_name,
        "n_samples": int(len(y_true)),
        "n_phishing": int(y_true.sum()),
        "n_legitimate": int((y_true == 0).sum()),
        "precision_legitimate": float(prec[0]),
        "recall_legitimate": float(rec[0]),
        "f1_legitimate": float(f1[0]),
        "precision_phishing": float(prec[1]),
        "recall_phishing": float(rec[1]),
        "f1_phishing": float(f1[1]),
        "precision_macro": float(prec_macro),
        "recall_macro": float(rec_macro),
        "f1_macro": float(f1_macro),
        "accuracy": float((y_pred == y_true).mean()),
        "confusion_matrix": {
            "labels": ["legitimate", "phishing"],
            "matrix": cm,
            "tn": int(tn), "fp": int(fp),
            "fn": int(fn), "tp": int(tp),
        },
        "false_positive_rate": float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0,
        "false_negative_rate": float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0,
        "classification_report": report,
    }
    return metrics


def main() -> None:
    print("=" * 60)
    print("CyberSaathi URL Phishing Classifier — T-02 Training Pipeline")
    print(f"Random seed: {RANDOM_SEED}")
    print(f"Dataset: {DATA_PATH}")
    print("=" * 60)

    # ── 1. Load and validate ───────────────────────────────────────────────────
    df = load_and_validate_dataset(DATA_PATH)

    # ── 2. Leakage-aware split (BEFORE any preprocessing) ─────────────────────
    train_df, val_df, test_df = build_split(df)

    X_train = train_df[FEATURE_NAMES].values.astype(float)
    y_train = encode_labels(train_df["status"])

    X_val = val_df[FEATURE_NAMES].values.astype(float)
    y_val = encode_labels(val_df["status"])

    X_test = test_df[FEATURE_NAMES].values.astype(float)
    y_test = encode_labels(test_df["status"])

    # ── 3. Build and fit pipeline (fit only on training data) ─────────────────
    print("\nFitting pipeline on training data ...")
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    print("Fitting complete.")

    # ── 4. Evaluate on all splits ─────────────────────────────────────────────
    print("\nEvaluating on validation set ...")
    val_metrics = evaluate(pipeline, X_val, y_val, "validation")
    print(f"  Val accuracy:   {val_metrics['accuracy']:.4f}")
    print(f"  Val F1 macro:   {val_metrics['f1_macro']:.4f}")
    print(f"  Val FPR:        {val_metrics['false_positive_rate']:.4f}")
    print(f"  Val FNR:        {val_metrics['false_negative_rate']:.4f}")

    print("\nEvaluating on held-out test set ...")
    test_metrics = evaluate(pipeline, X_test, y_test, "test")
    print(f"  Test accuracy:  {test_metrics['accuracy']:.4f}")
    print(f"  Test F1 macro:  {test_metrics['f1_macro']:.4f}")
    print(f"  Test FPR:       {test_metrics['false_positive_rate']:.4f}")
    print(f"  Test FNR:       {test_metrics['false_negative_rate']:.4f}")
    print("\nTest confusion matrix:")
    print(f"  [TN={test_metrics['confusion_matrix']['tn']:4d}  FP={test_metrics['confusion_matrix']['fp']:4d}]")
    print(f"  [FN={test_metrics['confusion_matrix']['fn']:4d}  TP={test_metrics['confusion_matrix']['tp']:4d}]")

    # ── 5. Save artifacts ──────────────────────────────────────────────────────
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    model_path = ARTIFACTS_DIR / "url_model.joblib"
    schema_path = ARTIFACTS_DIR / "feature_schema.json"
    training_report_path = ARTIFACTS_DIR / "training_report.json"
    eval_report_path = REPORTS_DIR / "evaluation_report.json"

    # Model
    joblib.dump(pipeline, model_path)
    print(f"\nModel saved: {model_path}")

    # Feature schema
    feature_schema = {
        "schema_version": "1.0.0",
        "feature_count": len(FEATURE_NAMES),
        "feature_names": FEATURE_NAMES,
        "label_encoding": {"legitimate": 0, "phishing": 1},
        "notes": (
            "All features are URL-only: computed from the URL string with no "
            "network requests, DNS lookups, WHOIS queries, or page-content access. "
            "Feature definitions match data/raw/hannousse/scripts/url_features.py "
            "and ml/url_features.py."
        ),
    }
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(feature_schema, f, indent=2)
    print(f"Feature schema saved: {schema_path}")

    # Training report (provenance + reproducibility)
    training_report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "random_seed": RANDOM_SEED,
        "test_size": TEST_SIZE,
        "val_size": VAL_SIZE,
        "dataset": {
            "file": "data/raw/hannousse/dataset_B_05_2020.csv",
            "source": "https://data.mendeley.com/datasets/c2gw7fy2j4/3",
            "authors": "Hannousse, Abdelhak; Yahiouche, Salima",
            "title": (
                "Towards a Benchmark of Machine Learning Methods for "
                "Phishing Websites Detection"
            ),
            "license": "CC BY 4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "total_rows_raw": len(df),
            "total_rows_after_dedup": len(df),
            "class_distribution_full": df["status"].value_counts().to_dict(),
        },
        "split_sizes": {
            "train": len(train_df),
            "val": len(val_df),
            "test": len(test_df),
        },
        "model": {
            "type": "sklearn.ensemble.RandomForestClassifier",
            "pipeline_steps": ["StandardScaler", "RandomForestClassifier"],
            "n_estimators": 200,
            "max_depth": "None (unlimited)",
            "min_samples_leaf": 2,
            "class_weight": "balanced",
            "random_state": RANDOM_SEED,
        },
        "feature_schema_version": "1.0.0",
        "feature_count": len(FEATURE_NAMES),
        "command": "python ml/train_url_model.py",
    }
    with open(training_report_path, "w", encoding="utf-8") as f:
        json.dump(training_report, f, indent=2)
    print(f"Training report saved: {training_report_path}")

    # Evaluation report
    eval_report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "random_seed": RANDOM_SEED,
        "dataset_provenance": {
            "file": "data/raw/hannousse/dataset_B_05_2020.csv",
            "source": "https://data.mendeley.com/datasets/c2gw7fy2j4/3",
            "license": "CC BY 4.0",
        },
        "feature_schema_version": "1.0.0",
        "feature_names": FEATURE_NAMES,
        "feature_type": "URL-only (no network access required for inference)",
        "validation": val_metrics,
        "test": test_metrics,
        "limitations": [
            "Features are URL-only. Page-content and external-service features "
            "were excluded to enable local inference without network access.",
            "The random_domain feature uses a simple vowel/digit heuristic rather "
            "than the NLP model used in the original paper. This may differ from "
            "the training set's precomputed values.",
            "Dataset was collected in 2020. Phishing techniques evolve; results "
            "may not generalise to current attacks.",
            "Brand list (allbrands.txt, 257 entries) may miss newer brands.",
            "The model is a phishing-URL classifier, not a general malware detector.",
            "A low-risk prediction is not a safety guarantee.",
        ],
    }
    with open(eval_report_path, "w", encoding="utf-8") as f:
        json.dump(eval_report, f, indent=2)
    print(f"Evaluation report saved: {eval_report_path}")

    print("\n" + "=" * 60)
    print("Training complete. Summary:")
    print(f"  Test accuracy:          {test_metrics['accuracy']:.4f}")
    print(f"  Test F1 (phishing):     {test_metrics['f1_phishing']:.4f}")
    print(f"  Test F1 (legitimate):   {test_metrics['f1_legitimate']:.4f}")
    print(f"  Test F1 macro:          {test_metrics['f1_macro']:.4f}")
    print(f"  Test precision (phish): {test_metrics['precision_phishing']:.4f}")
    print(f"  Test recall (phish):    {test_metrics['recall_phishing']:.4f}")
    print(f"  False positive rate:    {test_metrics['false_positive_rate']:.4f}")
    print(f"  False negative rate:    {test_metrics['false_negative_rate']:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
