# Independent 64-career evaluation (eval64_v1): data validation, metrics, bootstrap, coverage and integrity

import hashlib
import json
from pathlib import Path

import pytest

from src.evaluation import independent_64_evaluation as ev
from src.evaluation.agreement import weighted_kappa
from src.evaluation.bootstrap import profile_bootstrap
from src.evaluation.eval64_data import (
    CATALOG_FILES, EVAL64_DIR, LABEL_COLUMNS, PROFILE_COLUMNS, Eval64DataError, parse_labels, parse_profiles,
    read_manifest, relevant_set, verify_frozen,
)
from src.evaluation.snapshot import verify_snapshot

from tests.conftest import EVAL64_LABELS_AVAILABLE, needs_eval64_labels  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_SHA256 = {
    "reports/evaluation_results.json": "0982d9d4c91a9de8889df2ffa7eee101a5c09cc2f3e1cb491909ea15918bfb28",
    "reports/research_results.json": "8b169c33e3d97899470132bb269b4e969b39b7776dab0d49a8e42fac19ced805",
    "reports/ml_results.json": "14705ab23a5fc5802a42abc1a7991f7f59e31d1b79d13d496bb61ebd3a622377",
    "reports/ml_interpretation.json": "434ce2333115704ba441b64783bd653d76ead8d83f72a4fcab7462c97f31e917",
    "reports/ml_sensitivity.json": "f0d66500518dcd3c843f40badbc41e29e7d1d3fedcec8d8fede91d815be17d02",
    "data/evaluation/labelled_profiles.json": "293e114523d2f7035c7c6f4c847fe1b296cbd5fd6b24db4d6e84678490987bf3",
}


def sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def frozen():
    return ev.load_frozen()


@pytest.fixture(scope="module")
def run(frozen):
    catalog, profiles, labels = frozen
    rows, ranking_rows = ev.run_profiles(catalog, profiles, labels)
    return rows, ranking_rows


def profile_row(**overrides):
    row = {"profile_id": "T1", "primary_category": "Law", "profile_type": "strong_match", "learner_stage": "masters",
           "education_level": "4", "experience_years": "", "skills": "contract law|legal research",
           "interests": "writing", "learning_goal": "Lawyer", "description": "Test profile"}
    row.update(overrides)
    return row


def label_row(**overrides):
    row = {"profile_id": "T1", "career_id": "C057", "relevance_label": "3", "justification": "Core work",
           "occupational_basis": "author judgement", "reviewer": "tester", "confidence": "high"}
    row.update(overrides)
    return row


# ---------- Integrity of the original study ----------

def test_original_snapshot_reports_and_labels_unchanged():
    assert verify_snapshot() == []
    for rel, digest in ORIGINAL_SHA256.items():
        assert sha(rel) == digest, rel


def test_frozen_eval64_files_unchanged_and_complete():
    if EVAL64_LABELS_AVAILABLE:
        assert verify_frozen() == []
    else:
        recorded = read_manifest()["sha256"]
        for name, digest in recorded.items():
            if name != "relevance_labels.csv":
                assert hashlib.sha256((EVAL64_DIR / name).read_bytes()).hexdigest() == digest, name
    manifest = read_manifest()
    assert manifest["study_id"] == "eval64_v1" and manifest["frozen_before_engine_run"] is True
    assert manifest["second_reviewer"] is None
    assert set(manifest["sha256"]) == set(CATALOG_FILES) | {"profiles.csv", "relevance_labels.csv"}


@needs_eval64_labels
def test_frozen_catalogue_is_the_live_64_career_catalogue(frozen):
    catalog = frozen[0]
    assert len(catalog.careers) == 64 and len({c.title for c in catalog.careers}) == 64
    assert len({c.category for c in catalog.careers}) == 10
    live_manifest = json.loads((ROOT / "data" / "raw" / "dataset_manifest.json").read_text(encoding="utf-8"))
    # While the live catalogue is still v1.3.0, the frozen copy must be byte-identical to it
    if live_manifest["dataset_version"] == "1.3.0":
        for name in CATALOG_FILES:
            assert (ROOT / "data" / "raw" / name).read_bytes() == (EVAL64_DIR / name).read_bytes(), name


# ---------- Profile and label datasets ----------

@needs_eval64_labels
def test_profile_dataset_coverage(frozen):
    _, profiles, labels = frozen
    assert len(profiles) >= 100
    counts = {}
    for p in profiles:
        counts[p.primary_category] = counts.get(p.primary_category, 0) + 1
    assert len(counts) == 10 and min(counts.values()) >= 10
    relevant_careers = {c for grades in labels.values() for c in relevant_set(grades)}
    assert len(relevant_careers) == 64


@needs_eval64_labels
def test_labels_cover_every_profile_and_use_valid_grades(frozen):
    _, profiles, labels = frozen
    assert set(labels) == {p.profile_id for p in profiles}
    assert sum(len(v) for v in labels.values()) == read_manifest()["explicit_labels"]
    assert all(g in (0, 1, 2, 3) for grades in labels.values() for g in grades.values())


@pytest.mark.parametrize("overrides, message", [
    ({"primary_category": "Arts"}, "unknown primary_category"),
    ({"profile_type": "ideal"}, "unknown profile_type"),
    ({"learner_stage": "expert"}, "unknown learner_stage"),
    ({"learning_goal": ""}, "learning_goal is required"),
    ({"education_level": "7"}, "education_level"),
    ({"skills": "", "interests": ""}, "at least one skill or interest"),
])
def test_invalid_profiles_are_rejected(overrides, message):
    with pytest.raises(Eval64DataError, match=message):
        parse_profiles([profile_row(**overrides)])


def test_duplicate_profile_ids_are_rejected():
    with pytest.raises(Eval64DataError, match="duplicate profile_id"):
        parse_profiles([profile_row(), profile_row()])


def test_blank_education_is_allowed_and_omitted_from_input():
    profile = parse_profiles([profile_row(education_level="")])[0]
    assert profile.education_level is None and "education_level" not in profile.as_input()


@pytest.mark.parametrize("rows, message", [
    ([label_row(career_id="C999")], "unknown career_id"),
    ([label_row(profile_id="T9")], "unknown profile"),
    ([label_row(), label_row()], "duplicate label"),
    ([label_row(relevance_label="4")], "relevance_label"),
    ([label_row(relevance_label="high")], "relevance_label"),
    ([label_row(justification="")], "justification is required"),
    ([label_row(reviewer="")], "reviewer is required"),
    ([label_row(confidence="certain")], "confidence"),
])
def test_invalid_labels_are_rejected(rows, message):
    with pytest.raises(Eval64DataError, match=message):
        parse_labels(rows, ["T1"], {"C057", "C058"})


def test_column_sets_are_documented():
    assert "justification" in LABEL_COLUMNS and "occupational_basis" in LABEL_COLUMNS
    assert "learning_goal" in PROFILE_COLUMNS


# ---------- Metrics ----------

def test_profile_metrics_on_a_worked_example():
    ranking = ["A", "B", "C", "D", "E", "F"]
    grades = {"B": 3, "D": 2, "F": 1}
    m = ev.profile_metrics(ranking, grades)
    assert m["precision_at_1"] == 0.0
    assert m["precision_at_3"] == pytest.approx(1 / 3)
    assert m["precision_at_5"] == pytest.approx(2 / 5)
    assert m["recall_at_5"] == 1.0
    assert m["f1_at_5"] == pytest.approx(2 * 0.4 / 1.4)
    assert m["reciprocal_rank"] == 0.5
    assert m["average_precision"] == pytest.approx((1 / 2 + 2 / 4) / 2)
    import math
    dcg = 3 / math.log2(3) + 2 / math.log2(5)
    idcg = 3 / math.log2(2) + 2 / math.log2(3) + 1 / math.log2(4)
    assert m["ndcg_at_5"] == pytest.approx(dcg / idcg)


def test_profile_without_relevant_career_is_undefined_not_zero():
    m = ev.profile_metrics(["A", "B"], {"A": 1})
    assert all(m[name] is None for name in ev.BINARY_METRICS)
    assert m["ndcg_at_5"] == 1.0


def test_threshold_changes_the_relevant_set():
    grades = {"A": 3, "B": 2, "C": 1, "D": 0}
    assert relevant_set(grades) == {"A", "B"}
    assert relevant_set(grades, 1) == {"A", "B", "C"}
    assert relevant_set(grades, 3) == {"A"}


# ---------- Bootstrap and agreement ----------

def test_bootstrap_is_reproducible_and_brackets_the_mean():
    rows = [{"x": v, "y": None if i % 4 == 0 else v} for i, v in enumerate([0.1, 0.4, 0.5, 0.9, 1.0, 0.3, 0.7])]
    a = profile_bootstrap(rows, ["x", "y"], n_resamples=500, seed=7)
    b = profile_bootstrap(rows, ["x", "y"], n_resamples=500, seed=7)
    assert a == b
    assert a["x"]["ci_low"] <= a["x"]["mean"] <= a["x"]["ci_high"]
    assert a["y"]["defined_profiles"] == 5 and a["y"]["undefined_profiles"] == 2


def test_bootstrap_resamples_whole_profiles():
    # Two perfectly correlated metrics must give identical intervals when profiles are drawn jointly
    rows = [{"a": v, "b": v} for v in (0.0, 0.2, 0.5, 0.8, 1.0)]
    out = profile_bootstrap(rows, ["a", "b"], n_resamples=300, seed=1)
    assert (out["a"]["ci_low"], out["a"]["ci_high"]) == (out["b"]["ci_low"], out["b"]["ci_high"])


def test_bootstrap_needs_two_profiles():
    out = profile_bootstrap([{"a": 0.5}], ["a"], n_resamples=100)
    assert out["a"]["mean"] == 0.5 and out["a"]["ci_low"] is None


def test_weighted_kappa():
    assert weighted_kappa([(0, 0), (1, 1), (2, 2), (3, 3)]) == pytest.approx(1.0)
    assert weighted_kappa([(0, 1), (1, 0)], categories=(0, 1), weighting="linear") == pytest.approx(-1.0)
    assert weighted_kappa([]) is None


# ---------- Run, aggregation and coverage ----------

@needs_eval64_labels
def test_every_career_is_ranked_for_every_profile(run, frozen):
    rows, ranking_rows = run
    assert all(len(r["ranking"]) == 64 and len(set(r["ranking"])) == 64 for r in rows)
    assert len(ranking_rows) == 64 * len(frozen[1])


@needs_eval64_labels
def test_profiles_without_relevant_labels_are_reported(run):
    rows, _ = run
    missing = [r for r in rows if r["relevant_count"] == 0]
    assert len(missing) == 10
    assert all(r["precision_at_5"] is None and r["ndcg_at_5"] is not None for r in missing)


@needs_eval64_labels
def test_category_aggregation_counts_every_profile(run):
    rows, _ = run
    groups = ev.group_metrics(rows, "primary_category", sorted({r["primary_category"] for r in rows}))
    assert sum(g["profiles"] for g in groups) == len(rows)
    for g in groups:
        s = g["stats"]["precision_at_5"]
        assert s["defined_profiles"] + s["undefined_profiles"] == g["profiles"]


@needs_eval64_labels
def test_career_coverage_is_consistent(run, frozen):
    rows, _ = run
    coverage = ev.career_coverage(rows, frozen[0])
    assert len(coverage) == 64
    assert sum(c["top5_appearances"] for c in coverage) == 5 * len(rows)
    assert sum(c["top1_appearances"] for c in coverage) == len(rows)
    assert sum(c["relevant_labels"] for c in coverage) == sum(r["relevant_count"] for r in rows)
    for c in coverage:
        assert c["never_in_top5"] == (c["top5_appearances"] == 0)


@needs_eval64_labels
def test_engine_checks(run, frozen):
    checks = ev.engine_checks(frozen[0], run[0])
    assert checks["every_career_ranked_for_every_profile"] and checks["earth_science_trio_separate_records"]
    assert checks["max_score_empty_profile"] < 100 and checks["max_score_unknown_skills_only"] < 100
    assert checks["duplicate_titles"] == 0


@needs_eval64_labels
def test_saved_outputs_reproduce_exactly():
    assert ev.check_outputs(ROOT / "reports" / "evaluation_64") == []


def test_saved_summary_states_limits():
    summary = json.loads((ROOT / "reports" / "evaluation_64" / "evaluation_summary.json").read_text(encoding="utf-8"))
    assert summary["data"]["inter_rater_agreement"] is None
    assert "not real-world accuracy" in summary["note"]
    assert summary["original_study"]["report"] == "reports/evaluation_results.json"
    assert summary["configuration"]["weights"] == {"required_skills": 0.55, "preferred_skills": 0.15,
                                                   "interests": 0.25, "education": 0.05}
