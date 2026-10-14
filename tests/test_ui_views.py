# Pure UI helpers: input parsing, filtering, table rows and chart data

import pytest

from src.services.catalog import load_catalog
from src.services.recommendations import recommend
from src.services.skill_gap import analyze_skill_gap
from src.ui.charts import bar_chart, contribution_chart, coverage_chart
from src.ui.views import (
    build_profile_input, category_counts, contribution_rows, education_counts, education_label, filter_careers,
    parse_skill_text, required_skill_frequency, resource_rows,
)


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


def test_parse_skill_text_splits_without_normalizing():
    assert parse_skill_text("ML, Python;\n CI/CD ,, ") == ["ML", "Python", "CI/CD"]
    assert parse_skill_text("") == [] and parse_skill_text(None) == []


def test_build_profile_input_shape():
    assert build_profile_input(["python"], "ML", ["analysis"], 3, 2) == {
        "skills": ["python", "ML"], "interests": ["analysis"], "education_level": 3, "experience_years": 2,
    }
    assert build_profile_input() == {"skills": [], "interests": []}


def test_education_label():
    assert education_label(None) == "Not provided"
    assert education_label(3) == "3: Bachelor's degree or equivalent"


def test_filter_careers_on_real_data(catalog):
    assert len(filter_careers(catalog.careers)) == 50
    healthcare = filter_careers(catalog.careers, ["Healthcare"])
    assert len(healthcare) == 6 and {c.category for c in healthcare} == {"Healthcare"}
    analysts = filter_careers(catalog.careers, query="  ANALYST ")
    assert analysts and all("analyst" in c.title.lower() for c in analysts)
    assert filter_careers(catalog.careers, ["Design"], "nurse") == []


def test_dataset_counts_match_catalog(catalog):
    assert sum(r["Careers"] for r in category_counts(catalog.careers)) == 50
    edu = {r["Level"]: r["Careers"] for r in education_counts(catalog.careers)}
    assert edu[education_label(3)] == 42
    top = required_skill_frequency(catalog.careers, limit=3)
    assert top[0] == {"Skill": "communication", "Careers": 8}


def test_resource_rows_keep_verification_and_gap_type(catalog):
    gap = analyze_skill_gap({"skills": ["python"]}, "C001", catalog)
    rows = resource_rows(gap["resources"]["required"], "required")
    assert {r["Gap"] for r in rows} == {"required"}
    assert all(r["Link status"] == "search index confirmed" for r in rows)
    assert all(r["URL"].startswith("https://") for r in rows)
    empty = resource_rows([{"skill": "x", "has_resources": False, "resources": []}], "preferred")
    assert empty[0]["Resource"] == "No resource in catalogue" and empty[0]["URL"] is None


def test_contribution_rows_add_up_to_service_score(catalog):
    result = recommend({"skills": ["python", "sql"], "interests": ["analysis"]}, catalog, top_k=3)
    rows = contribution_rows(result["recommendations"])
    for rec in result["recommendations"]:
        label = f"{rec['rank']}. {rec['career_title']}"
        total = sum(r["Points"] for r in rows if r["Career"] == label)
        assert total == pytest.approx(rec["score"], abs=0.1)


def test_charts_use_given_data(catalog):
    fig = bar_chart(category_counts(catalog.careers), "Category", "Careers", "t")
    assert list(fig.data[0].y)[0] == 8
    result = recommend({"skills": ["python"]}, catalog, top_k=2)
    stacked = contribution_chart(contribution_rows(result["recommendations"]))
    assert len(stacked.data) == 4
    gap = analyze_skill_gap({"skills": ["python"]}, "C001", catalog, include_resources=False)
    cov = coverage_chart(gap)
    assert list(cov.data[0].y)[0] == pytest.approx(gap["required_coverage"] * 100, abs=0.1)
