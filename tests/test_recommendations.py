# Service-level recommendation output, catalog loading and real Phase 2 data integration

import csv

import pytest

from src.data.validation import CAREER_COLUMNS
from src.services.catalog import DatasetError, build_catalog, load_catalog
from src.services.learning_resources import ResourceCatalog
from src.services.recommendations import SCORE_DISCLAIMER, recommend
from src.services.skill_gap import analyze_skill_gap
from tests.conftest import make_career

OUTPUT_KEYS = {
    "rank", "career_id", "career_title", "category", "score", "score_components", "matched_required_skills",
    "missing_required_skills", "matched_preferred_skills", "missing_preferred_skills", "matched_interests",
    "career_interests", "education", "learning_goals", "reasons", "notes", "source_url",
}


def test_output_schema_and_order(mini_catalog):
    result = recommend({"skills": ["python", "sql", "ML"], "interests": ["analysis"], "education_level": 3}, mini_catalog, top_k=2)
    recs = result["recommendations"]
    assert [r["career_id"] for r in recs] == ["C001", "C004"]
    assert set(recs[0]) == OUTPUT_KEYS
    assert recs[0]["matched_required_skills"] == ["python", "sql", "machine learning"]
    assert recs[0]["missing_required_skills"] == ["statistics"]
    assert result["careers_scored"] == 4
    assert result["disclaimer"] == SCORE_DISCLAIMER
    assert "probability" not in " ".join(recs[0]["reasons"]).lower()


def test_unknown_skill_warning_and_no_match(mini_catalog):
    result = recommend({"skills": ["cobol"]}, mini_catalog)
    assert result["profile"]["report"]["unknown_skills"] == ["cobol"]
    assert any("cobol" in w for w in result["warnings"])
    assert all(r["matched_required_skills"] == [] for r in result["recommendations"])


def test_empty_profile_result(mini_catalog):
    result = recommend({}, mini_catalog, top_k=3)
    assert [r["score"] for r in result["recommendations"]] == [0.0, 0.0, 0.0]
    assert result["profile"]["profile_complete"] is False
    assert any("career_id order" in w for w in result["warnings"])


def test_recommend_does_not_change_catalog(mini_catalog):
    before = mini_catalog.careers
    recommend({"skills": ["python"]}, mini_catalog, top_k=1)
    assert mini_catalog.careers == before and len(mini_catalog.careers) == 4


def test_build_catalog_rejects_bad_data():
    with pytest.raises(DatasetError):
        build_catalog([], ResourceCatalog([]))
    with pytest.raises(DatasetError):
        build_catalog([make_career("C001", ["python"]), make_career("C001", ["sql"])], ResourceCatalog([]))
    with pytest.raises(DatasetError):
        build_catalog([make_career("C001", [])], ResourceCatalog([]))


def test_load_catalog_refuses_invalid_files(tmp_path):
    with pytest.raises(DatasetError):
        load_catalog(tmp_path)
    with open(tmp_path / "careers.csv", "w", newline="") as f:
        csv.writer(f).writerow(CAREER_COLUMNS)
    with pytest.raises(DatasetError):
        load_catalog(tmp_path)


def test_load_catalog_accepts_small_valid_dataset(dataset_dir):
    catalog = load_catalog(dataset_dir, expected_count=2)
    assert len(catalog.careers) == 2
    assert catalog.aliases["py"] == "python"
    assert catalog.known_skills == {"python", "sql", "git"}


@pytest.fixture(scope="module")
def real_catalog():
    return load_catalog()


def test_real_catalog_loads(real_catalog):
    assert len(real_catalog.careers) == 50
    assert len(real_catalog.known_skills) == 114
    assert real_catalog.resources.skills == real_catalog.known_skills


def test_real_data_worked_example(real_catalog):
    # Same illustrative profile as docs/recommendation_algorithm.md
    profile = {"skills": ["Python", "SQL", "Excel", "ML", "statistics"], "interests": ["analysis", "mathematics"], "education_level": 3}
    recs = recommend(profile, real_catalog, top_k=5)["recommendations"]
    assert [(r["career_id"], r["score"]) for r in recs] == [
        ("C001", 61.5), ("C002", 59.6), ("C029", 55.0), ("C031", 50.8), ("C006", 41.7),
    ]
    assert recs[0]["missing_required_skills"] == ["data visualization"]


def test_real_data_ranking_is_repeatable(real_catalog):
    profile = {"skills": ["html", "css", "js"], "interests": ["design"]}
    first = recommend(profile, real_catalog, top_k=10)
    second = recommend(profile, real_catalog, top_k=10)
    assert first == second
    assert first["recommendations"][0]["career_id"] == "C010"


def test_real_data_every_gap_skill_has_a_resource(real_catalog):
    for career in real_catalog.careers:
        gap = analyze_skill_gap({}, career.career_id, real_catalog)
        entries = gap["resources"]["required"] + gap["resources"]["preferred"]
        assert all(e["has_resources"] for e in entries), career.career_id
        assert len(entries) == len(career.required_skills) + len(career.preferred_skills)
