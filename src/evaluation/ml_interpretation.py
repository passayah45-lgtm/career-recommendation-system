# Refits each model on all labelled pairs with its most often chosen hyperparameters, for interpretation only
# These full-data fits are never used to report accuracy
# Run: python -m src.evaluation.ml_interpretation --output reports/ml_interpretation.json

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.tree import export_text

from src.evaluation.dataset import load_profiles
from src.ml.features import FEATURE_NAMES, build_pair_dataset
from src.ml.models import MODEL_NAMES, make_model, xgboost_available
from src.services.catalog import load_catalog

DECIMALS = 4


def most_common_params(chosen):
    key = Counter(json.dumps(c, sort_keys=True) for c in chosen).most_common(1)[0][0]
    return json.loads(key)


def run(ml_report_path="reports/ml_results.json"):
    report = json.loads(Path(ml_report_path).read_text(encoding="utf-8"))
    catalog = load_catalog()
    profiles = load_profiles([c.career_id for c in catalog.careers])
    X, y, _, _ = build_pair_dataset(profiles, catalog)
    X, y = np.asarray(X, dtype=float), np.asarray(y)
    spw = float((y == 0).sum()) / float((y == 1).sum())
    out = {"note": "Fitted on all 1,800 pairs for interpretation only; not an accuracy estimate.", "models": {}}
    for name in MODEL_NAMES:
        if name == "xgboost" and not xgboost_available():
            continue
        params = most_common_params(report["methods"][name]["chosen_hyperparameters"])
        est, _ = make_model(name, seed=42, scale_pos_weight=spw)
        est.set_params(**params)
        est.fit(X, y)
        entry = {"params": params}
        if name == "logistic_regression":
            coef = est.named_steps["clf"].coef_[0]
            entry["standardised_coefficients"] = {f: round(float(c), DECIMALS) for f, c in zip(FEATURE_NAMES, coef)}
        else:
            imp = est.feature_importances_
            entry["feature_importance"] = {f: round(float(v), DECIMALS) for f, v in zip(FEATURE_NAMES, imp)}
        if name == "decision_tree":
            entry["rules"] = export_text(est, feature_names=list(FEATURE_NAMES), decimals=3)
            entry["depth"] = int(est.get_depth())
            entry["leaves"] = int(est.get_n_leaves())
        out["models"][name] = entry
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description="Interpret the trained models.")
    parser.add_argument("--output", help="write the JSON report to this path")
    args = parser.parse_args(argv)
    text = json.dumps(run(), indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
