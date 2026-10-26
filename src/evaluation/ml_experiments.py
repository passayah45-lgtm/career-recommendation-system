# Compares trained classifiers with the weighted scoring formula on the labelled synthetic profiles
# Grouped nested cross-validation: no profile appears in both training and test, tuning uses inner folds only
# Run: python -m src.evaluation.ml_experiments --output reports/ml_results.json
# Check: python -m src.evaluation.ml_experiments --check reports/ml_results.json

import argparse
import json
import platform
import sys
from pathlib import Path

import numpy as np
import sklearn
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, GroupKFold, StratifiedGroupKFold

from src.evaluation import metrics as m
from src.evaluation.dataset import load_profiles
from src.ml.features import FEATURE_NAMES, build_pair_dataset
from src.ml.models import MODEL_NAMES, make_model, xgboost_available
from src.ml.ranker import rank_by_probability
from src.services.catalog import load_catalog
from src.services.recommendations import recommend

K = 5
DECIMALS = 4
OUTER_FOLDS = 5
INNER_FOLDS = 3
REPEATS = 5
TEST_RESAMPLES = 10000
BASELINE = "weighted_formula"
RANK_METRICS = ("average_precision", "ndcg_at_5", "reciprocal_rank", "r_precision", "precision_at_5", "recall_at_5")


def _r(value):
    return None if value is None else round(float(value), DECIMALS)


def ranking_metrics(ranking, relevant):
    return {
        "average_precision": m.average_precision(ranking, relevant),
        "ndcg_at_5": m.ndcg_at_k(ranking, relevant, K),
        "reciprocal_rank": m.reciprocal_rank(ranking, relevant),
        "r_precision": m.r_precision(ranking, relevant),
        "precision_at_5": m.precision_at_k(ranking, relevant, K),
        "recall_at_5": m.recall_at_k(ranking, relevant, K),
    }


def best_f1_threshold(y, scores):
    # Threshold on training-fold scores that maximises F1; ties take the higher threshold
    best_t, best_f = None, -1.0
    for t in sorted(set(np.round(scores, 9)), reverse=True):
        f = f1_score(y, (scores >= t).astype(int), zero_division=0)
        if f > best_f:
            best_t, best_f = t, f
    return best_t


def baseline_scores(profiles, catalog):
    # Engine score per pair, in the same row order as build_pair_dataset
    out = []
    order = [c.career_id for c in catalog.careers]
    for p in profiles:
        recs = recommend(p.as_input(), catalog, top_k=None)["recommendations"]
        score = {r["career_id"]: r["score"] for r in recs}
        rank = [r["career_id"] for r in recs]
        out.append((rank, [score[cid] / 100.0 for cid in order]))
    return out


def outer_splits(groups_arr, strata, seed):
    splitter = StratifiedGroupKFold(n_splits=OUTER_FOLDS, shuffle=True, random_state=seed)
    return list(splitter.split(np.zeros(len(groups_arr)), strata, groups_arr))


def run(catalog=None, profiles=None, models=None, repeats=REPEATS):
    catalog = catalog or load_catalog()
    profiles = profiles or load_profiles([c.career_id for c in catalog.careers])
    models = [n for n in (models or MODEL_NAMES) if n != "xgboost" or xgboost_available()]
    X, y, groups, career_ids = build_pair_dataset(profiles, catalog)
    X, y = np.asarray(X, dtype=float), np.asarray(y)
    groups_arr = np.asarray(groups)
    strata = np.asarray([p.primary_category for p in profiles for _ in catalog.careers])
    n_careers = len(catalog.careers)
    pid_index = {p.profile_id: i for i, p in enumerate(profiles)}
    base = baseline_scores(profiles, catalog)
    base_pair_scores = np.asarray([s for _, ss in base for s in ss])

    per_profile = {name: {p.profile_id: [] for p in profiles} for name in models + [BASELINE]}
    classif = {name: [] for name in models + [BASELINE]}
    chosen = {name: [] for name in models}

    for rep in range(repeats):
        pooled = {name: np.zeros(len(y)) for name in models}
        pooled_label = {name: np.zeros(len(y), dtype=int) for name in models + [BASELINE]}
        for tr, te in outer_splits(groups_arr, strata, seed=rep):
            spw = float((y[tr] == 0).sum()) / float(max(1, (y[tr] == 1).sum()))
            t_base = best_f1_threshold(y[tr], base_pair_scores[tr])
            pooled_label[BASELINE][te] = (base_pair_scores[te] >= t_base).astype(int)
            for name in models:
                est, grid = make_model(name, seed=42, scale_pos_weight=spw)
                search = GridSearchCV(est, grid, scoring="average_precision", cv=GroupKFold(n_splits=INNER_FOLDS),
                                      refit=True, n_jobs=1)
                search.fit(X[tr], y[tr], groups=groups_arr[tr])
                chosen[name].append({k: (v if v is None or isinstance(v, (int, float, str)) else str(v))
                                     for k, v in search.best_params_.items()})
                proba_tr = search.predict_proba(X[tr])[:, 1]
                t = best_f1_threshold(y[tr], proba_tr)
                proba_te = search.predict_proba(X[te])[:, 1]
                pooled[name][te] = proba_te
                pooled_label[name][te] = (proba_te >= t).astype(int)
        for name in models + [BASELINE]:
            scores = base_pair_scores if name == BASELINE else pooled[name]
            labels = pooled_label[name]
            classif[name].append({
                "roc_auc": roc_auc_score(y, scores),
                "pr_auc": average_precision_score(y, scores),
                "precision": precision_score(y, labels, zero_division=0),
                "recall": recall_score(y, labels, zero_division=0),
                "f1": f1_score(y, labels, zero_division=0),
            })
            for p in profiles:
                if not p.relevant_career_ids:
                    continue
                i = pid_index[p.profile_id]
                if name == BASELINE:
                    ranking = base[i][0]
                else:
                    sl = slice(i * n_careers, (i + 1) * n_careers)
                    ranking = rank_by_probability(career_ids[sl], scores[sl])
                per_profile[name][p.profile_id].append(ranking_metrics(ranking, p.relevant_career_ids))

    methods = {}
    profile_means = {}
    for name in models + [BASELINE]:
        rows = []
        for p in profiles:
            runs = per_profile[name][p.profile_id]
            if not runs:
                continue
            rows.append({"profile_id": p.profile_id,
                         **{k: _r(sum(r[k] for r in runs) / len(runs)) for k in RANK_METRICS}})
        profile_means[name] = rows
        agg = {}
        for k in RANK_METRICS:
            vals = [r[k] for r in rows]
            mean, n, _ = m.mean_defined(vals)
            ci = m.bootstrap_ci(vals)
            agg[k] = {"mean": _r(mean), "ci95": None if ci is None else [_r(ci[0]), _r(ci[1])], "profiles": n}
        cls = {k: _r(np.mean([c[k] for c in classif[name]])) for k in ("roc_auc", "pr_auc", "precision", "recall", "f1")}
        cls_sd = {k: _r(np.std([c[k] for c in classif[name]])) for k in ("roc_auc", "pr_auc", "f1")}
        methods[name] = {"ranking": agg, "classification_mean_over_repeats": cls,
                         "classification_sd_over_repeats": cls_sd, "per_profile_mean_over_repeats": rows}
        if name in chosen:
            methods[name]["chosen_hyperparameters"] = chosen[name]

    ref = profile_means[BASELINE]
    tests = {}
    for metric in ("average_precision", "ndcg_at_5"):
        raw = {name: m.paired_randomization_test([r[metric] for r in profile_means[name]], [r[metric] for r in ref],
                                                 n_resamples=TEST_RESAMPLES) for name in models}
        adj = m.holm_adjust([raw[n]["p_value"] for n in models]) if models else []
        tests[metric] = {n: {"mean_difference_model_minus_formula": _r(raw[n]["mean_difference"]),
                             "nonzero_pairs": raw[n]["nonzero_pairs"], "p_value": _r(raw[n]["p_value"]),
                             "p_holm": _r(a), "significant_at_0_05": bool(a < 0.05)}
                         for n, a in zip(models, adj)}

    return {
        "note": ("Synthetic-profile study. Labels are the author's binary relevance labels for 36 author-written "
                 "profiles. Features are derived from the same matching the formula uses. Results measure agreement "
                 "with those labels, not real-world career-guidance quality."),
        "data": {"pairs": int(len(y)), "positives": int(y.sum()), "profiles": len(profiles),
                 "scorable_profiles": sum(1 for p in profiles if p.relevant_career_ids), "careers": n_careers,
                 "features": list(FEATURE_NAMES)},
        "protocol": {"outer": f"StratifiedGroupKFold({OUTER_FOLDS}) by profile, strata = primary category",
                     "inner": f"GroupKFold({INNER_FOLDS}) by profile, GridSearchCV scoring average_precision",
                     "repeats": repeats, "outer_seeds": list(range(repeats)), "model_seed": 42,
                     "threshold": "F1-maximising threshold chosen on each outer training fold",
                     "ranking": "careers sorted by predicted probability, ties by career id",
                     "per_profile_metric": "mean over repeats, then macro mean over scorable profiles",
                     "test": f"paired sign-flip randomisation vs formula, {TEST_RESAMPLES} resamples, Holm over models"},
        "software": {"python": platform.python_version(), "scikit_learn": sklearn.__version__,
                     "numpy": np.__version__, "xgboost": _xgb_version()},
        "methods": methods,
        "significance_vs_formula": tests,
    }


def _xgb_version():
    if not xgboost_available():
        return None
    import xgboost
    return xgboost.__version__


def to_json(report):
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Train and compare ML rankers with the weighted formula.")
    parser.add_argument("--output", help="write the JSON report to this path")
    parser.add_argument("--check", help="exit 1 if this saved report differs from a fresh run")
    args = parser.parse_args(argv)
    text = to_json(run())
    if args.check:
        saved = Path(args.check).read_text(encoding="utf-8") if Path(args.check).exists() else ""
        if saved != text:
            print(f"ML results differ from {args.check}. Regenerate with --output.")
            return 1
        print(f"ML results match {args.check}.")
        return 0
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
