# Feature construction, model training, ranking, reproducibility and failure cases for the ML rankers

import math

import numpy as np
import pytest

from src.evaluation import ml_experiments as mx
from src.evaluation.dataset import load_profiles
from src.ml import models as ml_models
from src.ml.features import FEATURE_NAMES, build_pair_dataset, pair_features, profile_matrix
from src.ml.ranker import NotTrainedError, TrainedRanker, rank_by_probability
from src.services.catalog import load_catalog
from src.services.recommendations import profile_from_input


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


@pytest.fixture(scope="module")
def profiles(catalog):
    return load_profiles([c.career_id for c in catalog.careers])


def test_feature_values_by_hand(catalog, profiles):
    p01 = next(p for p in profiles if p.profile_id == "P01")
    profile, _ = profile_from_input(p01.as_input(), catalog)
    row = pair_features(profile, catalog.get_career("C001"))
    expected = dict(required_coverage=1.0, required_matched=5, required_missing=0, required_total=5,
                    preferred_coverage=0.0, preferred_matched=0, interest_coverage=0.75, interest_matched=3,
                    education_value=1.0, education_gap=0, education_provided=1, learner_skill_count=5,
                    learner_skills_used_share=1.0)
    assert dict(zip(FEATURE_NAMES, row)) == pytest.approx(expected)


def test_pair_dataset_shape_and_labels(catalog, profiles):
    X, y, groups, ids = build_pair_dataset(profiles, catalog)
    assert len(X) == len(y) == len(groups) == len(ids) == 36 * 50
    assert sum(y) == 56
    assert all(len(row) == len(FEATURE_NAMES) for row in X)
    assert not any(math.isnan(v) for row in X for v in row)


def test_features_without_interests_or_education(catalog):
    ids, rows = profile_matrix({"skills": ["python"]}, catalog)
    assert len(ids) == 50
    by_name = dict(zip(FEATURE_NAMES, rows[0]))
    assert by_name["education_provided"] == 0.0 and by_name["education_gap"] == 0.0
    assert by_name["interest_matched"] == 0.0


def test_empty_profile_gives_zero_shares(catalog):
    _, rows = profile_matrix({}, catalog)
    assert all(dict(zip(FEATURE_NAMES, r))["learner_skills_used_share"] == 0.0 for r in rows)


def test_rank_by_probability_breaks_ties_by_id():
    assert rank_by_probability(["C003", "C001", "C002"], [0.5, 0.5, 0.9]) == ["C002", "C001", "C003"]


def test_unknown_model_name_is_rejected():
    with pytest.raises(ValueError):
        ml_models.make_model("svm")


def test_missing_xgboost_gives_clear_error(monkeypatch):
    monkeypatch.setattr(ml_models, "xgboost_available", lambda: False)
    with pytest.raises(ml_models.ModelUnavailableError):
        ml_models.make_model("xgboost")


def test_untrained_ranker_refuses_to_predict(catalog):
    with pytest.raises(NotTrainedError):
        TrainedRanker("logistic_regression").rank({"skills": ["python"]}, catalog)


def test_training_needs_both_classes(catalog, profiles):
    empty = [p for p in profiles if not p.relevant_career_ids]
    with pytest.raises(ValueError):
        TrainedRanker("logistic_regression").fit(empty, catalog)


@pytest.mark.parametrize("name", ["logistic_regression", "decision_tree", "random_forest"])
def test_training_is_reproducible_and_ranks_all_careers(catalog, profiles, name):
    params = {"n_estimators": 50} if name == "random_forest" else {}
    a = TrainedRanker(name, params).fit(profiles[:30], catalog)
    b = TrainedRanker(name, params).fit(profiles[:30], catalog)
    query = profiles[31].as_input()
    _, pa = a.predict_proba(query, catalog)
    _, pb = b.predict_proba(query, catalog)
    assert np.array_equal(pa, pb)
    ranking = a.rank(query, catalog)
    assert sorted(ranking) == sorted(c.career_id for c in catalog.careers)


@pytest.mark.skipif(not ml_models.xgboost_available(), reason="xgboost not installed")
def test_xgboost_trains(catalog, profiles):
    r = TrainedRanker("xgboost", {"n_estimators": 20}).fit(profiles, catalog)
    _, proba = r.predict_proba(profiles[0].as_input(), catalog)
    assert proba.shape == (50,) and np.all((proba >= 0) & (proba <= 1))


def test_model_recommendations_keep_explanations_and_skill_gaps(catalog, profiles):
    r = TrainedRanker("logistic_regression").fit(profiles, catalog)
    out = r.recommend(profiles[0].as_input(), catalog, top_k=5)
    assert len(out["recommendations"]) == 5 and out["ranking_model"] == "logistic_regression"
    first = out["recommendations"][0]
    assert first["rank"] == 1 and 0.0 <= first["model_probability"] <= 1.0
    for key in ("reasons", "score_components", "missing_required_skills", "missing_preferred_skills"):
        assert key in first


def test_outer_splits_never_share_a_profile(catalog, profiles):
    _, _, groups, _ = build_pair_dataset(profiles, catalog)
    g = np.asarray(groups)
    strata = np.asarray([p.primary_category for p in profiles for _ in catalog.careers])
    for tr, te in mx.outer_splits(g, strata, seed=0):
        assert not set(g[tr]) & set(g[te])


def test_small_experiment_is_deterministic(catalog, profiles):
    a = mx.run(catalog, profiles, models=["logistic_regression"], repeats=1)
    b = mx.run(catalog, profiles, models=["logistic_regression"], repeats=1)
    assert mx.to_json(a) == mx.to_json(b)
    assert a["methods"]["weighted_formula"]["ranking"]["average_precision"]["mean"] == pytest.approx(0.9714)
