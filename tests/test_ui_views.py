# Pure UI helpers: input parsing, filtering, table rows and chart data

import pytest

from src.services.catalog import load_catalog
from src.services.recommendations import recommend
from src.services.skill_gap import analyze_skill_gap
from src.ui.charts import bar_chart, contribution_chart, coverage_chart
from src.ui.views import (
    build_profile_input, career_list_rows, career_rows, category_counts, contribution_rows, education_counts, education_label, filter_careers,
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
    assert all(r["Link status"] in ("search index confirmed", "http checked") for r in rows)
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


def test_career_rows_are_compact_and_complete(catalog):
    rows = career_rows(catalog.careers)
    assert len(rows) == 50
    assert list(rows[0]) == ["Career", "Category", "Required skills", "Preferred skills", "Entry education", "ID"]
    first = catalog.careers[0]
    assert rows[0]["Required skills"] == len(first.required_skills)


def test_career_list_rows_follow_filtered_order(catalog):
    careers = filter_careers(catalog.careers, ["Healthcare"])
    rows = career_list_rows(careers)
    assert [r["Career"] for r in rows] == [c.title for c in careers]
    assert set(rows[0]) == {"Career", "Category"}


def test_donut_and_colored_bars_use_dataset_values(catalog):
    from src.ui.charts import donut_chart
    donut = donut_chart(education_counts(catalog.careers), "Level", "Careers", "t")
    assert sum(donut.data[0].values) == 50
    bars = bar_chart(category_counts(catalog.careers), "Category", "Careers", "t", colors=["#111111", "#222222"])
    assert list(bars.data[0].marker.color)[:3] == ["#111111", "#222222", "#111111"]
    assert list(bars.data[0].y) == [r["Careers"] for r in category_counts(catalog.careers)]


def test_career_from_cell_maps_clicked_row_to_id():
    from src.ui.views import career_from_cell
    ids = ["C001", "C002", "C003"]
    assert career_from_cell(ids, [(2, "Career")]) == "C003"
    assert career_from_cell(ids, [[0, "Category"]]) == "C001"
    assert career_from_cell(ids, [{"row": 1, "column": "Career"}]) == "C002"
    assert career_from_cell(ids, []) is None and career_from_cell(ids, None) is None
    assert career_from_cell(ids, [(7, "Career")]) is None and career_from_cell(ids, [(-1, "Career")]) is None


def test_model_comparison_rows_match_saved_report():
    from src.ui.views import load_ml_report, model_comparison_rows
    report = load_ml_report()
    rows = model_comparison_rows(report)
    assert [r["Method"] for r in rows][0].startswith("Weighted formula")
    assert len(rows) == 5
    formula = rows[0]
    assert formula["MAP"] == round(report["methods"]["weighted_formula"]["ranking"]["average_precision"]["mean"], 3)
    assert formula["p vs formula (Holm)"] == "reference"
    assert all(isinstance(r["p vs formula (Holm)"], str) for r in rows)
    assert not formula["Trained model"] and all(r["Trained model"] for r in rows[1:])


def test_missing_or_broken_model_report_is_handled(tmp_path):
    from src.ui.views import load_ml_report, model_comparison_rows
    assert load_ml_report(tmp_path / "missing.json") is None
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert load_ml_report(bad) is None
    assert model_comparison_rows(None) == [] and model_comparison_rows({}) == []
