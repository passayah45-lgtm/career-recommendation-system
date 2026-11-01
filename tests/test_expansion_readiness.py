# Guards for the planned catalogue expansion: frozen evaluation snapshot, original records, counts and colors

import csv
import json
import shutil

import pytest

from src.data.validation import (
    CATEGORIES, DEFAULT_DATA_DIR, MANIFEST_FILE, PLANNED_CATEGORIES, validate_all,
)
from src.evaluation.snapshot import (
    EVALUATION_CATALOG_DIR, EVALUATION_CATEGORIES, load_evaluation_catalog, snapshot_manifest, verify_snapshot,
)
from src.ui.theme import CATEGORY_COLORS, CATEGORY_FALLBACK_COLOR, category_color
from src.ui.views import category_counts

ORIGINAL_COLORS = ["#0F9D94", "#3B82F6", "#8B5CF6", "#F59E0B", "#14213D", "#7DD3C8", "#EC4899", "#64748B"]


def rows(path, key):
    with open(path, newline="", encoding="utf-8") as f:
        return {r[key]: r for r in csv.DictReader(f)}


def test_snapshot_is_intact_and_holds_the_original_catalogue():
    assert verify_snapshot() == []
    m = snapshot_manifest()
    assert (m["careers"], m["skills"], m["resources"]) == (50, 114, 114)
    assert validate_all(EVALUATION_CATALOG_DIR).ok
    catalog = load_evaluation_catalog()
    assert [c.career_id for c in catalog.careers] == [f"C{i:03d}" for i in range(1, 51)]
    assert {c.category for c in catalog.careers} == set(EVALUATION_CATEGORIES)


def test_original_50_careers_are_unchanged_in_the_live_catalogue():
    snapshot = rows(EVALUATION_CATALOG_DIR / "careers.csv", "career_id")
    live = rows(DEFAULT_DATA_DIR / "careers.csv", "career_id")
    assert len(snapshot) == 50
    for cid, row in snapshot.items():
        assert live.get(cid) == row, f"{cid} differs from the frozen original"


def test_original_resources_and_aliases_are_unchanged_in_the_live_catalogue():
    snap_res = rows(EVALUATION_CATALOG_DIR / "resources.csv", "resource_id")
    live_res = rows(DEFAULT_DATA_DIR / "resources.csv", "resource_id")
    for rid, row in snap_res.items():
        assert live_res.get(rid) == row, f"{rid} differs from the frozen original"
    snap_alias = rows(EVALUATION_CATALOG_DIR / "skill_aliases.csv", "alias")
    live_alias = rows(DEFAULT_DATA_DIR / "skill_aliases.csv", "alias")
    for alias, row in snap_alias.items():
        assert live_alias.get(alias) == row


def test_a_modified_snapshot_is_detected(tmp_path):
    copy = tmp_path / "snap"
    shutil.copytree(EVALUATION_CATALOG_DIR, copy)
    with open(copy / "careers.csv", "a", encoding="utf-8") as f:
        f.write("\n")
    assert verify_snapshot(copy) == ["careers.csv"]


def test_evaluation_scripts_default_to_the_snapshot():
    import inspect

    from src.evaluation import experiments, ml_experiments, ml_interpretation, ml_sensitivity, research_experiments
    for module in (experiments, research_experiments, ml_experiments, ml_sensitivity, ml_interpretation):
        source = inspect.getsource(module)
        assert "load_evaluation_catalog()" in source and "load_catalog(" not in source, module.__name__
    assert "for cat in EVALUATION_CATEGORIES" in inspect.getsource(experiments)


def live_copy(tmp_path):
    copy = tmp_path / "raw"
    shutil.copytree(DEFAULT_DATA_DIR, copy, ignore=shutil.ignore_patterns("processed"))
    return copy


def append_career(path, **values):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns, data = reader.fieldnames, list(reader)
    data.append({c: values.get(c, "") for c in columns})
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)


def set_manifest(path, **counts):
    m = json.loads((path / MANIFEST_FILE).read_text(encoding="utf-8"))
    m.update(counts)
    (path / MANIFEST_FILE).write_text(json.dumps(m), encoding="utf-8")


NEW_CAREER = {
    "career_id": "C051", "career_title": "Test Expansion Career", "category": "Engineering",
    "description": "A test career that reuses existing skills to check the expansion path.",
    "required_skills": "engineering mathematics|cad|gis", "preferred_skills": "project management",
    "education_level": "3", "interests": "engineering|environment", "learning_goals": "plan a site|draw a map",
}


def test_live_validation_follows_the_manifest(tmp_path):
    assert validate_all(DEFAULT_DATA_DIR).ok
    data = live_copy(tmp_path)
    append_career(data / "careers.csv", **NEW_CAREER)
    errors = [str(e) for e in validate_all(data).errors]
    assert any("expected 50 careers, found 51" in e for e in errors)
    set_manifest(data, careers=51)
    assert validate_all(data).ok


def test_counts_for_skills_and_resources_are_enforced(tmp_path):
    data = live_copy(tmp_path)
    set_manifest(data, skills=158, resources=158)
    errors = [str(e) for e in validate_all(data).errors]
    assert any("expected 158 unique skills, found 114" in e for e in errors)
    assert any("expected 158 resources, found 114" in e for e in errors)


def test_malformed_manifest_is_an_error(tmp_path):
    data = live_copy(tmp_path)
    (data / MANIFEST_FILE).write_text('{"careers": "fifty"}', encoding="utf-8")
    assert any(e.dataset == "manifest" for e in validate_all(data).errors)


@pytest.mark.parametrize("title", ["Civil Engineer", "Electrical Engineer", "Human Resources Specialist",
                                   "civil-engineer"])
def test_duplicate_existing_titles_are_rejected(tmp_path, title):
    data = live_copy(tmp_path)
    append_career(data / "careers.csv", **{**NEW_CAREER, "career_title": title})
    set_manifest(data, careers=51)
    assert any(e.field == "career_title" and "duplicate" in e.message for e in validate_all(data).errors)


def test_unapproved_categories_and_bad_skills_are_rejected(tmp_path):
    data = live_copy(tmp_path)
    append_career(data / "careers.csv", **{**NEW_CAREER, "category": "Law",
                                           "required_skills": "legal research|cad|gis",
                                           "preferred_skills": "cad"})
    set_manifest(data, careers=51)
    messages = [e.message for e in validate_all(data).errors]
    assert any("'Law' is not an approved category" in msg for msg in messages)
    assert any("'cad' is also a required skill" in msg for msg in messages)
    assert any("required skill has no learning resource" in msg for msg in messages)


def test_category_colors_are_safe_for_current_and_planned_categories():
    assert list(CATEGORY_COLORS.values())[:8] == ORIGINAL_COLORS
    assert [category_color(c) for c in CATEGORIES] == ORIGINAL_COLORS
    wanted = list(CATEGORIES) + list(PLANNED_CATEGORIES)
    colors = [category_color(c) for c in wanted]
    assert CATEGORY_FALLBACK_COLOR not in colors
    assert len(set(colors)) == len(wanted)
    assert category_color("A Category Nobody Planned") == CATEGORY_FALLBACK_COLOR
    assert set(PLANNED_CATEGORIES).isdisjoint(CATEGORIES)


def test_category_chart_rows_get_a_color_for_every_category():
    from tests.conftest import make_career
    careers = [make_career("C001", ["python"], category="Software"),
               make_career("C002", ["contract law"], category="Law")]
    chart_rows = category_counts(careers)
    assert all(category_color(r["Category"]) for r in chart_rows)
    assert category_color("Law") != CATEGORY_FALLBACK_COLOR
