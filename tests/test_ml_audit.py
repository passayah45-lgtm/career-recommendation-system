# Audit checks for the ML comparison: reproducibility, leakage guards and the sensitivity helpers

import json
import random
from pathlib import Path

import numpy as np
import pytest

from src.evaluation.dataset import load_profiles
from src.evaluation.ml_experiments import outer_splits, run
from src.evaluation.ml_sensitivity import evaluate, permuted_profiles, random_tie_ranking
from src.ml.features import FEATURE_NAMES, build_pair_dataset
from src.services.catalog import load_catalog

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


@pytest.fixture(scope="module")
def profiles(catalog):
    return load_profiles([c.career_id for c in catalog.careers])


def test_saved_results_reproduce_for_scikit_learn_models(catalog, profiles):
    # The full report needs xgboost; the scikit-learn models and the formula are checked here in CI
    saved = json.loads((ROOT / "reports" / "ml_results.json").read_text(encoding="utf-8"))
    fresh = run(catalog, profiles, models=["logistic_regression", "decision_tree"])
    for name in ("logistic_regression", "decision_tree", "weighted_formula"):
        assert fresh["methods"][name]["ranking"] == saved["methods"][name]["ranking"]
        assert (fresh["methods"][name]["classification_mean_over_repeats"]
                == saved["methods"][name]["classification_mean_over_repeats"])
    assert fresh["data"] == saved["data"]


def test_features_carry_no_identity_and_ignore_labels(catalog, profiles):
    assert not any(word in name for name in FEATURE_NAMES for word in ("career_id", "category", "profile"))
    X, y, _, _ = build_pair_dataset(profiles, catalog)
    Xp, yp, _, _ = build_pair_dataset(permuted_profiles(profiles), catalog)
    assert np.array_equal(np.asarray(X), np.asarray(Xp))
    assert not np.array_equal(np.asarray(y), np.asarray(yp))


def test_every_outer_split_keeps_profiles_and_categories_apart(catalog, profiles):
    _, _, groups, _ = build_pair_dataset(profiles, catalog)
    groups = np.asarray(groups)
    strata = np.asarray([p.primary_category for p in profiles for _ in catalog.careers])
    for seed in range(5):
        for tr, te in outer_splits(groups, strata, seed):
            assert not set(groups[tr]) & set(groups[te])


def test_permutation_is_a_derangement_and_deterministic(profiles):
    a, b = permuted_profiles(profiles), permuted_profiles(profiles)
    assert [p.relevant_career_ids for p in a] == [p.relevant_career_ids for p in b]
    assert sorted(map(tuple, (p.relevant_career_ids for p in a))) == sorted(
        map(tuple, (p.relevant_career_ids for p in profiles)))
    moved = sum(x.relevant_career_ids != y.relevant_career_ids for x, y in zip(a, profiles))
    assert moved >= len(profiles) - 5


def test_random_ties_only_reorder_equal_scores():
    ids = ["A", "B", "C", "D"]
    scores = [0.5, 0.9, 0.5, 0.1]
    seen = {tuple(random_tie_ranking(ids, scores, random.Random(s))) for s in range(20)}
    assert seen == {("B", "A", "C", "D"), ("B", "C", "A", "D")}


def test_evaluate_matches_hand_values(catalog, profiles):
    subset = [p for p in profiles if p.relevant_career_ids][:1]
    n = len(catalog.careers)
    ids = [c.career_id for c in catalog.careers]
    perfect = np.asarray([1.0 if cid in subset[0].relevant_career_ids else 0.0 for cid in ids])
    formula = [(ids, [0.0] * n)]
    out = evaluate(subset, catalog, {"model": perfect}, formula)
    assert out["model"]["average_precision"]["mean"] == 1.0
    assert out["model"]["reciprocal_rank"]["mean"] == 1.0


def test_saved_sensitivity_report_supports_the_audit_claims():
    report = json.loads((ROOT / "reports" / "ml_sensitivity.json").read_text(encoding="utf-8"))
    perm = report["label_permutation"]["results"]
    assert all(perm[name]["average_precision"]["mean"] < 0.2 for name in perm)
    loco = report["leave_one_category_out"]["results"]
    assert all(loco[name]["average_precision"]["mean"] > 0.9 for name in loco)
    ids_ = report["grouped_cv_seed0_career_id_ties"]["results"]["decision_tree"]["average_precision"]["mean"]
    rnd = report["grouped_cv_seed0_random_ties"]["results"]["decision_tree"]["average_precision"]["mean"]
    assert rnd < ids_
