# Live comparison of the formula with Logistic Regression, Decision Tree and Random Forest for one profile

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from src.evaluation.dataset import load_profiles
from src.ml.comparison import (
    FORMULA,
    LIVE_MODELS,
    LIVE_PARAMS,
    ComparisonUnavailableError,
    compare_methods,
    explain_random_forest,
    format_condition,
    train_live_models,
    tree_contributions,
)
from src.ml.features import FEATURE_NAMES, profile_matrix
from src.services.catalog import load_catalog
from src.services.profiles import ProfileValidationError
from src.services.recommendations import recommend

ROOT = Path(__file__).resolve().parents[1]
PROFILE = {"skills": ["python", "sql", "excel", "machine learning", "statistics"],
           "interests": ["analysis", "mathematics"], "education_level": 3}


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


@pytest.fixture(scope="module")
def profiles(catalog):
    return load_profiles([c.career_id for c in catalog.careers])


@pytest.fixture(scope="module")
def models(profiles, catalog):
    return train_live_models(profiles, catalog)


@pytest.fixture(scope="module")
def result(models, catalog):
    return compare_methods(PROFILE, catalog, models)


def test_live_models_load_with_the_saved_settings(models):
    assert tuple(models.rankers) == LIVE_MODELS
    assert "xgboost" not in models.rankers
    report = json.loads((ROOT / "reports" / "ml_interpretation.json").read_text(encoding="utf-8"))
    for name in LIVE_MODELS:
        assert report["models"][name]["params"] == LIVE_PARAMS[name]
    assert models.info["pairs"] == 1800 and models.info["relevant_pairs"] == 56
    assert models.info["features"] == len(FEATURE_NAMES)


def test_live_comparison_runs_without_xgboost():
    # xgboost is research-only, so the live path must work when it cannot be imported
    code = ("import sys; sys.modules['xgboost'] = None\n"
            "from src.services.catalog import load_catalog\n"
            "from src.evaluation.dataset import load_profiles\n"
            "from src.ml.comparison import train_live_models, compare_methods\n"
            "c = load_catalog(); m = train_live_models(load_profiles([x.career_id for x in c.careers]), c)\n"
            "r = compare_methods({'skills': ['python']}, c, m)\n"
            "assert all(len(r['methods'][k]['careers']) == 5 for k in r['order'])\n")
    done = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True,
                          timeout=300, check=False)
    assert done.returncode == 0, done.stderr


def test_training_is_reproducible(models, profiles, catalog):
    again = train_live_models(profiles, catalog)
    _, rows = profile_matrix(PROFILE, catalog)
    X = np.asarray(rows, dtype=float)
    for name in LIVE_MODELS:
        a = models.rankers[name].estimator.predict_proba(X)
        b = again.rankers[name].estimator.predict_proba(X)
        assert np.array_equal(a, b)


def test_every_method_returns_a_top_five(result):
    assert result["order"] == [FORMULA, *LIVE_MODELS]
    for method in result["order"]:
        entry = result["methods"][method]
        assert entry["error"] is None
        assert [r["rank"] for r in entry["careers"]] == [1, 2, 3, 4, 5]
        assert len({r["career_id"] for r in entry["careers"]}) == 5
        assert all(r["explanation"] for r in entry["careers"])
    assert result["methods"][FORMULA]["primary"] is True
    assert not any(result["methods"][m]["primary"] for m in LIVE_MODELS)


def test_formula_column_matches_the_recommendations_page(result, catalog):
    expected = recommend(PROFILE, catalog, top_k=5)["recommendations"]
    got = result["methods"][FORMULA]["careers"]
    assert [(r["career_id"], r["score"]) for r in got] == [(r["career_id"], r["score"]) for r in expected]


def test_models_rank_by_their_own_scores(result, models, catalog):
    _, rows = profile_matrix(PROFILE, catalog)
    for name in LIVE_MODELS:
        proba = models.rankers[name].estimator.predict_proba(np.asarray(rows, dtype=float))[:, 1]
        top = models.rankers[name].rank(PROFILE, catalog)[:5]
        assert [r["career_id"] for r in result["methods"][name]["careers"]] == top
        scores = [r["score"] for r in result["methods"][name]["careers"]]
        assert scores == sorted(scores, reverse=True)
        assert scores[0] == pytest.approx(float(max(proba)), abs=5e-4)
        assert all(0.0 <= s <= 1.0 for s in scores)


def test_all_methods_share_candidates_and_features(result, catalog):
    assert result["candidates"] == [c.career_id for c in catalog.careers]
    assert result["feature_names"] == list(FEATURE_NAMES)
    for name in LIVE_MODELS:
        assert result["methods"][name]["careers"][0]["career_id"] in result["candidates"]


def test_formula_rank_and_overlap_are_consistent(result):
    formula_ids = [r["career_id"] for r in result["methods"][FORMULA]["careers"]]
    for name in LIVE_MODELS:
        entry = result["methods"][name]
        assert entry["shared_with_formula"] == sum(r["career_id"] in formula_ids for r in entry["careers"])
        for r in entry["careers"]:
            if r["career_id"] in formula_ids:
                assert r["formula_rank"] == formula_ids.index(r["career_id"]) + 1


def test_logistic_explanation_sums_to_the_log_odds(models, catalog):
    est = models.rankers["logistic_regression"].estimator
    _, rows = profile_matrix(PROFILE, catalog)
    from src.ml.comparison import explain_logistic
    _, contributions = explain_logistic(est, rows[0])
    logit = est.decision_function(np.asarray([rows[0]], dtype=float))[0]
    assert sum(contributions.values()) + est.named_steps["clf"].intercept_[0] == pytest.approx(logit)


def test_tree_contributions_add_up_to_the_model_score(models, catalog):
    _, rows = profile_matrix(PROFILE, catalog)
    tree = models.rankers["decision_tree"].estimator
    bias, contributions, _ = tree_contributions(tree.tree_, rows[0])
    assert bias + contributions.sum() == pytest.approx(tree.predict_proba([rows[0]])[0, 1])
    forest = models.rankers["random_forest"].estimator
    _, detail = explain_random_forest(forest, rows[0])
    total = detail["bias"] + sum(v for k, v in detail.items() if k != "bias")
    assert total == pytest.approx(forest.predict_proba([rows[0]])[0, 1])


def test_decision_tree_explanation_reports_training_counts(result):
    for r in result["methods"]["decision_tree"]["careers"]:
        assert r["explanation"][0].startswith("Decision path:")
        assert "learner-career pairs" in r["explanation"][1]


def test_split_conditions_use_plain_words():
    assert format_condition("required_coverage", 0.583, True) == "required-skill coverage above 58%"
    assert format_condition("required_matched", 0.5, True) == "required skills you have at least 1"
    assert format_condition("required_missing", 2.5, False) == "required skills missing at most 2"
    assert format_condition("education_provided", 0.5, False) == "education level given: no"


@pytest.mark.parametrize("profile", [
    {"skills": ["python"]},
    {"skills": ["python", "blockchain wizardry"], "interests": ["not an interest"]},
    {"skills": [], "interests": []},
])
def test_missing_and_unseen_inputs_are_handled(profile, models, catalog):
    out = compare_methods(profile, catalog, models)
    for method in out["order"]:
        assert out["methods"][method]["error"] is None
        assert len(out["methods"][method]["careers"]) == 5


def test_invalid_profile_raises_like_recommend(models, catalog):
    with pytest.raises((ProfileValidationError, ValueError)):
        compare_methods({"skills": "python"}, catalog, models)


def test_a_failing_model_does_not_stop_the_others(models, catalog, monkeypatch):
    broken = models.rankers["decision_tree"].estimator

    def boom(_):
        raise RuntimeError("broken model")

    monkeypatch.setattr(broken, "predict_proba", boom)
    out = compare_methods(PROFILE, catalog, models)
    assert "broken model" in out["methods"]["decision_tree"]["error"]
    assert out["methods"]["decision_tree"]["careers"] == []
    assert len(out["methods"]["random_forest"]["careers"]) == 5
    assert len(out["methods"][FORMULA]["careers"]) == 5


def test_training_needs_both_classes(profiles, catalog):
    from dataclasses import replace
    no_positives = [replace(p, relevant_career_ids=()) for p in profiles]
    with pytest.raises(ComparisonUnavailableError):
        train_live_models(no_positives, catalog)


def test_unknown_model_is_rejected(profiles, catalog):
    with pytest.raises(ValueError):
        train_live_models(profiles, catalog, models=("xgboost",))
