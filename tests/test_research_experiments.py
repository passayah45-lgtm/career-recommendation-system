# New research metrics, baselines and reproducibility of the saved research report

import math
from pathlib import Path

import pytest

from src.evaluation import metrics as m
from src.evaluation import research_experiments as rx
from src.evaluation.dataset import load_profiles
from src.services.catalog import load_catalog

REPORT = Path(__file__).resolve().parents[1] / "reports" / "research_results.json"
RANKING = ["C001", "C002", "C003", "C004", "C005", "C006"]


def test_ndcg_by_hand():
    rel = {"C002", "C006"}
    expected = (1 / math.log2(3)) / (1 + 1 / math.log2(3))
    assert m.ndcg_at_k(RANKING, rel, 5) == pytest.approx(expected)
    assert m.ndcg_at_k(["C002", "C006"], rel, 5) == pytest.approx(1.0)
    assert m.ndcg_at_k(RANKING, set(), 5) is None


def test_ndcg_with_grades():
    grades = {"C001": 1, "C002": 2}
    ideal = 2 + 1 / math.log2(3)
    actual = 1 + 2 / math.log2(3)
    assert m.ndcg_at_k(RANKING, set(), 5, grades=grades) == pytest.approx(actual / ideal)


def test_randomization_test_edge_cases():
    assert m.paired_randomization_test([None], [0.5]) is None
    same = m.paired_randomization_test([0.5, 0.7], [0.5, 0.7])
    assert same["p_value"] == 1.0 and same["nonzero_pairs"] == 0
    strong = m.paired_randomization_test([1.0] * 20, [0.0] * 20, n_resamples=2000)
    assert strong["p_value"] < 0.01 and strong["mean_difference"] == pytest.approx(1.0)


def test_holm_adjust_by_hand():
    assert m.holm_adjust([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert m.holm_adjust([0.5, 0.9]) == pytest.approx([1.0, 1.0])


def test_reference_method_uses_production_weights():
    from src.engine.scoring import DEFAULT_WEIGHTS
    assert rx.WEIGHTED_METHODS[rx.REFERENCE] == DEFAULT_WEIGHTS


def test_popularity_baseline_leaves_the_profile_out():
    catalog = load_catalog()
    ids = sorted(c.career_id for c in catalog.careers)
    profiles = load_profiles(ids)
    target = profiles[0]
    ranking = rx.popularity_ranking(target, profiles, ids)
    counts = {cid: 0 for cid in ids}
    for p in profiles[1:]:
        for cid in p.relevant_career_ids:
            counts[cid] += 1
    assert ranking[0] == min(ids, key=lambda c: (-counts[c], c))
    assert sorted(ranking) == ids


def test_saved_research_report_is_reproducible():
    assert REPORT.exists(), "run: python -m src.evaluation.research_experiments --output reports/research_results.json"
    assert REPORT.read_text(encoding="utf-8") == rx.to_json(rx.run())
