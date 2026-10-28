# Live comparison of the weighted formula with three trained models for one learner profile
# The models are trained once per server process from the labelled synthetic profiles and then reused
# Every method sees the same 50 candidate careers and the same 13 features; the formula stays the primary method
# Explanations come only from the fitted models: coefficients, decision paths and tree contributions

import math
import time

import numpy as np
import sklearn

from src.ml.features import FEATURE_NAMES, build_pair_dataset, profile_matrix
from src.ml.models import make_model
from src.ml.ranker import TrainedRanker, rank_by_probability
from src.services.recommendations import recommend

FORMULA = "formula"
LIVE_MODELS = ("logistic_regression", "decision_tree", "random_forest")
METHOD_LABELS = {
    FORMULA: "Weighted formula",
    "logistic_regression": "Logistic Regression",
    "decision_tree": "Decision Tree",
    "random_forest": "Random Forest",
}
# Most often chosen settings in the grouped nested cross-validation (reports/ml_interpretation.json)
# tests/test_model_comparison.py checks these against that report
LIVE_PARAMS = {
    "logistic_regression": {"clf__C": 0.01},
    "decision_tree": {"max_depth": 4, "min_samples_leaf": 5},
    "random_forest": {"max_depth": None, "min_samples_leaf": 1},
}
SEED = 42
TOP_K = 5

FEATURE_LABELS = {
    "required_coverage": "required-skill coverage",
    "required_matched": "required skills you have",
    "required_missing": "required skills missing",
    "required_total": "required skills listed",
    "preferred_coverage": "preferred-skill coverage",
    "preferred_matched": "preferred skills you have",
    "interest_coverage": "interest coverage",
    "interest_matched": "matching interests",
    "education_value": "education match",
    "education_gap": "education levels below the career",
    "education_provided": "education level given",
    "learner_skill_count": "number of your skills",
    "learner_skills_used_share": "share of your skills this career uses",
}
SHARE_FEATURES = {"required_coverage", "preferred_coverage", "interest_coverage", "education_value",
                  "learner_skills_used_share"}
YES_NO_FEATURES = {"education_provided"}


class ComparisonUnavailableError(RuntimeError):
    pass


def format_value(name, value):
    if name in SHARE_FEATURES:
        return f"{value * 100:.0f}%"
    if name in YES_NO_FEATURES:
        return "yes" if value >= 0.5 else "no"
    return f"{value:.0f}"


def format_condition(name, threshold, above):
    # Turns a tree split into plain words; count features use whole numbers
    label = FEATURE_LABELS[name]
    if name in YES_NO_FEATURES:
        return f"{label}: {'yes' if above else 'no'}"
    if name in SHARE_FEATURES:
        pct = f"{threshold * 100:.0f}%"
        return f"{label} above {pct}" if above else f"{label} {pct} or less"
    whole = math.floor(threshold)
    return f"{label} at least {whole + 1}" if above else f"{label} at most {whole}"


class LiveModels:
    # Holds the three fitted rankers plus what the explanations need from training

    def __init__(self, rankers, leaf_stats, info):
        self.rankers = rankers
        self.leaf_stats = leaf_stats
        self.info = info


def train_live_models(profiles, catalog, models=LIVE_MODELS):
    # Fits each model once on all labelled pairs with fixed settings and seed, so results are reproducible
    start = time.perf_counter()
    X, y, groups, _ = build_pair_dataset(profiles, catalog)
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    if len(y) == 0 or y.sum() == 0 or y.sum() == len(y):
        raise ComparisonUnavailableError("the labelled profiles need both relevant and non-relevant pairs")
    if not np.isfinite(X).all():
        raise ComparisonUnavailableError("the training features contain missing values")
    spw = float((y == 0).sum()) / float((y == 1).sum())
    rankers, leaf_stats = {}, {}
    for name in models:
        if name not in LIVE_PARAMS:
            raise ValueError(f"'{name}' is not available in the live comparison")
        est, _ = make_model(name, seed=SEED, scale_pos_weight=spw)
        est.set_params(**LIVE_PARAMS[name])
        est.fit(X, y)
        ranker = TrainedRanker(name, LIVE_PARAMS[name], seed=SEED)
        ranker.estimator = est
        rankers[name] = ranker
        if name == "decision_tree":
            leaves = est.apply(X)
            leaf_stats[name] = {int(leaf): (int((leaves == leaf).sum()), int(y[leaves == leaf].sum()))
                                for leaf in np.unique(leaves)}
    info = {
        "profiles": len(set(groups)),
        "pairs": len(y),
        "relevant_pairs": int(y.sum()),
        "features": len(FEATURE_NAMES),
        "seconds": round(time.perf_counter() - start, 3),
        "sklearn_version": sklearn.__version__,
    }
    return LiveModels(rankers, leaf_stats, info)


def _top_contributions(names, values, contributions, digits):
    # Two largest pushes up and the largest pull down, skipping near-zero effects
    order = np.argsort(contributions)
    ups = [i for i in order[::-1] if contributions[i] > 1e-6][:2]
    downs = [i for i in order if contributions[i] < -1e-6][:1]
    fmt = f"{{:+.{digits}f}}"

    def words(i):
        return f"{FEATURE_LABELS[names[i]]} {format_value(names[i], values[i])} ({fmt.format(contributions[i])})"

    return [words(i) for i in ups], [words(i) for i in downs]


def explain_logistic(estimator, row):
    # Each feature's share of the log-odds: coefficient x standardised value, relative to the average training pair
    scaler, clf = estimator.named_steps["scale"], estimator.named_steps["clf"]
    z = (np.asarray(row) - scaler.mean_) / scaler.scale_
    contributions = clf.coef_[0] * z
    ups, downs = _top_contributions(FEATURE_NAMES, row, contributions, 2)
    lines = []
    if ups:
        lines.append("Pushed up by " + "; ".join(ups) + ".")
    if downs:
        lines.append("Pulled down by " + "; ".join(downs) + ".")
    if not lines:
        lines.append("No feature moves this career away from the average training pair.")
    return lines, {FEATURE_NAMES[i]: float(contributions[i]) for i in range(len(FEATURE_NAMES))}


def _node_positive(tree, node):
    value = tree.value[node][0]
    total = float(value.sum())
    return float(value[1]) / total if total else 0.0


def tree_contributions(tree, row):
    # Path decomposition: start value at the root plus the change at every split, per feature
    # The start value plus all contributions equals the tree's own score for this row
    node, contributions = 0, np.zeros(len(FEATURE_NAMES))
    bias = _node_positive(tree, 0)
    while tree.children_left[node] != -1:
        f = tree.feature[node]
        child = tree.children_left[node] if row[f] <= tree.threshold[node] else tree.children_right[node]
        contributions[f] += _node_positive(tree, child) - _node_positive(tree, node)
        node = child
    return bias, contributions, node


def explain_decision_tree(estimator, row, leaf_stats):
    tree = estimator.tree_
    node, bounds = 0, {}
    while tree.children_left[node] != -1:
        f = tree.feature[node]
        above = row[f] > tree.threshold[node]
        name = FEATURE_NAMES[f]
        # Keeps only the tightest condition per feature and direction
        lo, hi = bounds.get(name, (None, None))
        if above:
            lo = tree.threshold[node] if lo is None else max(lo, tree.threshold[node])
        else:
            hi = tree.threshold[node] if hi is None else min(hi, tree.threshold[node])
        bounds[name] = (lo, hi)
        node = tree.children_right[node] if above else tree.children_left[node]
    parts = []
    for name, (lo, hi) in bounds.items():
        if lo is not None:
            parts.append(format_condition(name, lo, True))
        if hi is not None:
            parts.append(format_condition(name, hi, False))
    lines = ["Decision path: " + ("; ".join(parts) if parts else "the tree has no splits") + "."]
    stats = leaf_stats.get(int(node))
    if stats:
        n, pos = stats
        lines.append(f"In training, {pos} of {n} learner-career pairs that end on this path were labelled relevant.")
    return lines, {"leaf": int(node), "conditions": parts}


def explain_random_forest(estimator, row):
    biases, totals = [], np.zeros(len(FEATURE_NAMES))
    for tree_est in estimator.estimators_:
        bias, contributions, _ = tree_contributions(tree_est.tree_, row)
        biases.append(bias)
        totals += contributions
    n = len(estimator.estimators_)
    bias, contributions = float(np.mean(biases)), totals / n
    ups, downs = _top_contributions(FEATURE_NAMES, row, contributions, 2)
    lines = []
    if ups:
        lines.append("Pushed up by " + "; ".join(ups) + ".")
    if downs:
        lines.append("Pulled down by " + "; ".join(downs) + ".")
    return lines, {"bias": bias, **{FEATURE_NAMES[i]: float(contributions[i]) for i in range(len(FEATURE_NAMES))}}


def formula_lines(rec):
    parts = []
    for key, label in (("required_skills", "required skills"), ("preferred_skills", "preferred skills"),
                       ("interests", "interests"), ("education", "education")):
        comp = rec["score_components"].get(key)
        if comp and comp["applicable"] and comp["contribution"] > 0:
            parts.append(f"{label} {comp['contribution']:.1f}")
    lines = list(rec.get("reasons", [])[:1])
    lines.append("Points: " + (", ".join(parts) if parts else "no component scored above 0") + ".")
    return lines


def _career_row(rank, rec, score, formula_rank):
    return {
        "rank": rank,
        "career_id": rec["career_id"],
        "career_title": rec["career_title"],
        "category": rec["category"],
        "score": score,
        "formula_rank": formula_rank,
    }


def compare_methods(profile_data, catalog, live_models, top_k=TOP_K):
    # Returns the formula's top careers and each model's top careers for one raw profile
    # A model that fails is reported with an error message; the other methods still return results
    # Raises ProfileValidationError or ValueError for an invalid profile, like recommend()
    start = time.perf_counter()
    base = recommend(profile_data, catalog, top_k=None)
    recs = base["recommendations"]
    by_id = {r["career_id"]: r for r in recs}
    formula_rank = {r["career_id"]: r["rank"] for r in recs}
    ids, rows = profile_matrix(profile_data, catalog)
    X = np.asarray(rows, dtype=float)
    if not np.isfinite(X).all():
        raise ValueError("the profile produced missing feature values")
    formula_top = []
    for rec in recs[:top_k]:
        row = _career_row(rec["rank"], rec, rec["score"], rec["rank"])
        row["explanation"] = formula_lines(rec)
        formula_top.append(row)
    results = {FORMULA: {"method": FORMULA, "label": METHOD_LABELS[FORMULA], "primary": True,
                         "score_name": "Formula score (0 to 100)", "careers": formula_top, "error": None}}
    formula_ids = {r["career_id"] for r in formula_top}
    for name, ranker in live_models.rankers.items():
        entry = {"method": name, "label": METHOD_LABELS[name], "primary": False,
                 "score_name": "Model score (0 to 1)", "careers": [], "error": None}
        try:
            est = ranker.estimator
            proba = est.predict_proba(X)[:, 1]
            if not np.isfinite(proba).all():
                raise ValueError("the model returned missing scores")
            order = rank_by_probability(ids, proba)
            p_of = dict(zip(ids, proba))
            row_of = dict(zip(ids, rows))
            for rank, cid in enumerate(order[:top_k], start=1):
                row = _career_row(rank, by_id[cid], round(float(p_of[cid]), 3), formula_rank[cid])
                if name == "logistic_regression":
                    row["explanation"], row["detail"] = explain_logistic(est, row_of[cid])
                elif name == "decision_tree":
                    row["explanation"], row["detail"] = explain_decision_tree(
                        est, row_of[cid], live_models.leaf_stats.get(name, {}))
                else:
                    row["explanation"], row["detail"] = explain_random_forest(est, row_of[cid])
                entry["careers"].append(row)
            # Careers outside the top list with exactly the same score as the last one shown
            # Their order comes only from the career id tie-break, so the list is partly arbitrary
            cutoff = round(float(p_of[order[top_k - 1]]), 9) if len(order) > top_k else None
            entry["tied_outside"] = (sum(1 for cid in order[top_k:] if round(float(p_of[cid]), 9) == cutoff)
                                     if cutoff is not None else 0)
            entry["shared_with_formula"] = sum(1 for r in entry["careers"] if r["career_id"] in formula_ids)
        except Exception as exc:  # noqa: BLE001
            entry["careers"] = []
            entry["error"] = f"{type(exc).__name__}: {exc}"
        results[name] = entry
    return {
        "methods": results,
        "order": [FORMULA, *live_models.rankers],
        "candidates": list(ids),
        "feature_names": list(FEATURE_NAMES),
        "warnings": base["warnings"],
        "seconds": round(time.perf_counter() - start, 4),
    }
