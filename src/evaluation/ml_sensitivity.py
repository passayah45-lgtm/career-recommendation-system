# Sensitivity and sanity checks for the ML comparison in src/evaluation/ml_experiments.py
# 1. Grouped CV (one repeat) with ties broken at random instead of by career id
# 2. Leave-one-category-out: profiles that share a primary category never sit on both sides of a split
# 3. Label permutation: each profile gets another profile's labels; a leak-free pipeline should fall to chance
# Uses only scikit-learn models so it runs in CI without xgboost
# Run: python -m src.evaluation.ml_sensitivity --output reports/ml_sensitivity.json
# Check: python -m src.evaluation.ml_sensitivity --check reports/ml_sensitivity.json

import argparse
import json
import random
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import sklearn
from sklearn.model_selection import GridSearchCV, GroupKFold, LeaveOneGroupOut

from src.evaluation import metrics as m
from src.evaluation.dataset import load_profiles
from src.evaluation.ml_experiments import INNER_FOLDS, RANK_METRICS, _r, baseline_scores, outer_splits, ranking_metrics
from src.ml.features import build_pair_dataset
from src.ml.models import make_model
from src.ml.ranker import rank_by_probability
from src.services.catalog import load_catalog

MODELS = ("logistic_regression", "decision_tree", "random_forest")
BASELINE = "weighted_formula"
TIE_SHUFFLES = 50
PERMUTATION_SEED = 7
MODEL_SEED = 42


def out_of_fold_scores(X, y, groups, splits, models):
    # Nested CV: hyperparameters chosen by GroupKFold on each training part, scores predicted on the held-out part
    scores = {name: np.zeros(len(y)) for name in models}
    for tr, te in splits:
        spw = float((y[tr] == 0).sum()) / float(max(1, (y[tr] == 1).sum()))
        for name in models:
            est, grid = make_model(name, seed=MODEL_SEED, scale_pos_weight=spw)
            search = GridSearchCV(est, grid, scoring="average_precision", cv=GroupKFold(n_splits=INNER_FOLDS),
                                  refit=True, n_jobs=1)
            search.fit(X[tr], y[tr], groups=groups[tr])
            scores[name][te] = search.predict_proba(X[te])[:, 1]
    return scores


def random_tie_ranking(ids, scores, rng):
    keys = [rng.random() for _ in ids]
    order = sorted(range(len(ids)), key=lambda i: (-round(float(scores[i]), 9), keys[i]))
    return [ids[i] for i in order]


def summarise(per_profile):
    out = {}
    for k in RANK_METRICS:
        vals = [r[k] for r in per_profile]
        mean, n, _ = m.mean_defined(vals)
        ci = m.bootstrap_ci(vals)
        out[k] = {"mean": _r(mean), "ci95": None if ci is None else [_r(ci[0]), _r(ci[1])], "profiles": n}
    return out


def evaluate(profiles, catalog, scores, formula, ties="career_id"):
    # Per-profile ranking metrics for every model and the formula; ties="random" averages over seeded shuffles
    n = len(catalog.careers)
    ids = [c.career_id for c in catalog.careers]
    results = {}
    for name in [*scores, BASELINE]:
        rows = []
        for i, p in enumerate(profiles):
            if not p.relevant_career_ids:
                continue
            sl = slice(i * n, (i + 1) * n)
            vec = formula[i][1] if name == BASELINE else scores[name][sl]
            if ties == "random":
                rng = random.Random(f"{name}-{p.profile_id}")
                runs = [ranking_metrics(random_tie_ranking(ids, vec, rng), p.relevant_career_ids)
                        for _ in range(TIE_SHUFFLES)]
                rows.append({k: sum(r[k] for r in runs) / len(runs) for k in RANK_METRICS})
            else:
                ranking = formula[i][0] if name == BASELINE else rank_by_probability(ids, vec)
                rows.append(ranking_metrics(ranking, p.relevant_career_ids))
        results[name] = summarise(rows)
    return results


def permuted_profiles(profiles, seed=PERMUTATION_SEED):
    # A derangement of the label sets: no profile keeps its own labels
    rng = random.Random(seed)
    idx = list(range(len(profiles)))
    while True:
        rng.shuffle(idx)
        if all(i != j for i, j in enumerate(idx)):
            break
    return [replace(p, relevant_career_ids=profiles[j].relevant_career_ids) for p, j in zip(profiles, idx)]


def run(catalog=None, profiles=None, models=MODELS):
    catalog = catalog or load_catalog()
    profiles = list(profiles or load_profiles([c.career_id for c in catalog.careers]))
    X, y, groups, _ = build_pair_dataset(profiles, catalog)
    X, y, groups = np.asarray(X, dtype=float), np.asarray(y), np.asarray(groups)
    n = len(catalog.careers)
    strata = np.asarray([p.primary_category for p in profiles for _ in range(n)])
    formula = baseline_scores(profiles, catalog)
    models = list(models)

    grouped = out_of_fold_scores(X, y, groups, outer_splits(groups, strata, seed=0), models)
    loco_splits = list(LeaveOneGroupOut().split(X, y, strata))
    loco = out_of_fold_scores(X, y, groups, loco_splits, models)

    shuffled = permuted_profiles(profiles)
    Xp, yp, gp, _ = build_pair_dataset(shuffled, catalog)
    Xp, yp, gp = np.asarray(Xp, dtype=float), np.asarray(yp), np.asarray(gp)
    perm = out_of_fold_scores(Xp, yp, gp, outer_splits(gp, strata, seed=0), models)

    return {
        "note": ("Sensitivity checks on the 36 author-labelled synthetic profiles. They test the protocol, not "
                 "real-world career-guidance quality."),
        "settings": {"models": models, "model_seed": MODEL_SEED, "inner": f"GroupKFold({INNER_FOLDS}) by profile",
                     "tie_shuffles": TIE_SHUFFLES, "permutation_seed": PERMUTATION_SEED},
        # Python version left out so CI (3.12) and local runs (3.13) produce the same file
        "software": {"scikit_learn": sklearn.__version__, "numpy": np.__version__},
        "grouped_cv_seed0_career_id_ties": {
            "split": "StratifiedGroupKFold(5) by profile, strata = primary category, seed 0, one repeat",
            "results": evaluate(profiles, catalog, grouped, formula)},
        "grouped_cv_seed0_random_ties": {
            "split": "same predictions; ties broken at random, mean over shuffles; formula ties also random",
            "results": evaluate(profiles, catalog, grouped, formula, ties="random")},
        "leave_one_category_out": {
            "split": f"LeaveOneGroupOut over primary category ({len(loco_splits)} folds)",
            "results": evaluate(profiles, catalog, loco, formula)},
        "label_permutation": {
            "split": "labels moved to other profiles (derangement), then grouped CV seed 0",
            "results": evaluate(shuffled, catalog, perm, baseline_scores(shuffled, catalog))},
    }


def to_json(report):
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Sensitivity checks for the ML comparison.")
    parser.add_argument("--output")
    parser.add_argument("--check")
    args = parser.parse_args(argv)
    text = to_json(run())
    if args.check:
        saved = Path(args.check).read_text(encoding="utf-8") if Path(args.check).exists() else ""
        if saved != text:
            print(f"Sensitivity results differ from {args.check}. Regenerate with --output.")
            return 1
        print(f"Sensitivity results match {args.check}.")
        return 0
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
