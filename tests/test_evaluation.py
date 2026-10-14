# Evaluation metrics, labelled dataset checks and reproducibility of the saved report

import json
import math
from pathlib import Path

import pytest

from src.engine.scoring import ScoringWeights
from src.evaluation import metrics as m
from src.evaluation.dataset import EvaluationDataError, load_profiles, parse_profiles
from src.evaluation.experiments import CONFIGURATIONS, evaluate_profile, run, to_json
from src.services.catalog import load_catalog

REPORT = Path(__file__).resolve().parents[1] / "reports" / "evaluation_results.json"
RANKING = ["C001", "C002", "C003", "C004", "C005", "C006"]


def test_precision_recall_f1_by_hand():
    rel = {"C002", "C006"}
    assert m.precision_at_k(RANKING, rel, 5) == pytest.approx(1 / 5)
    assert m.attainable_precision_at_k(RANKING, rel, 5) == pytest.approx(1 / 2)
    assert m.recall_at_k(RANKING, rel, 5) == pytest.approx(1 / 2)
    assert m.f1_score(0.2, 0.5) == pytest.approx(2 * 0.2 * 0.5 / 0.7)
    assert m.f1_score(0.0, 0.0) == 0.0
    assert m.hit_at_k(RANKING, rel, 5) == 1.0


def test_order_sensitive_metrics_by_hand():
    rel = {"C002", "C006"}
    assert m.reciprocal_rank(RANKING, rel) == pytest.approx(1 / 2)
    assert m.r_precision(RANKING, rel) == pytest.approx(1 / 2)
    assert m.average_precision(RANKING, rel) == pytest.approx((1 / 2 + 2 / 6) / 2)
    assert m.reciprocal_rank(RANKING, {"C999"}) == 0.0


def test_fewer_items_than_k_uses_items_shown():
    assert m.precision_at_k(["C001", "C002"], {"C001"}, 5) == pytest.approx(1 / 2)
    assert m.precision_at_k([], {"C001"}, 5) is None


def test_undefined_metrics_are_none_and_excluded_from_means():
    for fn in (m.recall_at_k, m.precision_at_k, m.hit_at_k):
        assert fn(RANKING, set(), 5) is None
    assert m.reciprocal_rank(RANKING, set()) is None
    assert m.f1_score(None, 0.5) is None
    assert m.mean_defined([1.0, None, 0.0]) == (0.5, 2, 1)
    assert m.mean_defined([None]) == (None, 0, 1)


def test_bootstrap_is_reproducible_and_brackets_mean():
    values = [0.0, 0.5, 1.0, 1.0, 0.25]
    ci = m.bootstrap_ci(values, seed=7)
    assert ci == m.bootstrap_ci(values, seed=7)
    assert ci[0] <= sum(values) / len(values) <= ci[1]
    assert m.bootstrap_ci([1.0]) is None


def test_coverage_and_category_distribution():
    lists = [["C001", "C002"], ["C002", "C003"]]
    assert m.catalogue_coverage(lists, ["C001", "C002", "C003", "C004"]) == 0.75
    dist = m.category_distribution(lists, {"C001": "A", "C002": "A", "C003": "B"})
    assert dist == {"A": {"count": 3, "share": 0.75}, "B": {"count": 1, "share": 0.25}}


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


@pytest.fixture(scope="module")
def profiles(catalog):
    return load_profiles([c.career_id for c in catalog.careers])


def test_labelled_dataset_covers_all_categories_and_types(profiles):
    assert len(profiles) >= 30
    assert {p.primary_category for p in profiles} == {
        "Data and AI", "Software", "Cybersecurity", "Design", "Business", "Education", "Healthcare", "Engineering"}
    types = {p.profile_type for p in profiles}
    assert {"strong match", "career transition", "limited skills", "missing information", "mixed skills",
            "overlapping interests"} <= types
    assert any(not p.relevant_career_ids for p in profiles)


@pytest.mark.parametrize("change,message", [
    (lambda d: d["profiles"].append(dict(d["profiles"][0])), "duplicate"),
    (lambda d: d["profiles"][0].update(relevant_career_ids=["C999"]), "not in the catalogue"),
    (lambda d: d["profiles"][0].update(primary_category="Arts"), "primary_category"),
    (lambda d: d["profiles"][0].update(skills="python"), "list of text"),
    (lambda d: d["profiles"][0].update(relevant_career_ids=["C001", "C002", "C003", "C004"]), "more than"),
    (lambda d: d["profiles"][0].update(relevance_explanation=""), "relevance_explanation"),
])
def test_invalid_labelled_data_is_rejected(catalog, change, message):
    data = json.loads((REPORT.parents[1] / "data" / "evaluation" / "labelled_profiles.json").read_text())
    change(data)
    with pytest.raises(EvaluationDataError, match=message):
        parse_profiles(data, {c.career_id for c in catalog.careers})


def test_missing_file_is_reported(tmp_path):
    with pytest.raises(EvaluationDataError):
        load_profiles(["C001"], tmp_path / "missing.json")


def test_every_configuration_is_valid_and_normalized():
    for name, weights in CONFIGURATIONS.items():
        assert isinstance(weights, ScoringWeights)
        if name == "D_skills_only":
            assert weights.interests == 0 and weights.education == 0
            continue
        assert math.isclose(sum(weights.as_dict().values()), 1.0), name
        assert weights.education == 0.05


def test_every_configuration_gives_valid_scores(catalog, profiles):
    for weights in CONFIGURATIONS.values():
        for p in profiles:
            row = evaluate_profile(p, catalog, weights)
            assert len(row["top_k"]) == 5 and len(set(row["top_k"])) == 5
            assert all(0.0 <= s <= 100.0 and math.isfinite(s) for s in row["top_k_scores"])
            assert row["top_k_scores"] == sorted(row["top_k_scores"], reverse=True)


def test_profile_without_labels_has_undefined_metrics(catalog, profiles):
    p = next(p for p in profiles if not p.relevant_career_ids)
    row = evaluate_profile(p, catalog, CONFIGURATIONS["A_baseline"])
    assert row["recall_at_5"] is None and row["f1_at_5"] is None and row["reciprocal_rank"] is None


def test_saved_report_is_reproducible(catalog, profiles):
    # The report in reports/ must match a fresh run exactly, so docs tables are traceable
    assert REPORT.read_text(encoding="utf-8") == to_json(run(catalog, profiles))
