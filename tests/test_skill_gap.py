# Skill-gap analysis and learning-resource retrieval on a controlled catalog

import pytest

from src.services.catalog import UnknownCareerError
from src.services.learning_resources import LearningResource, ResourceCatalog
from src.services.profiles import ProfileValidationError
from src.services.skill_gap import analyze_skill_gap


def test_gap_splits_required_and_preferred(mini_catalog):
    gap = analyze_skill_gap({"skills": ["python", "ML", "git"]}, "C001", mini_catalog)
    assert gap["have_required_skills"] == ["python", "machine learning"]
    assert gap["missing_required_skills"] == ["sql", "statistics"]
    assert gap["have_preferred_skills"] == ["git"]
    assert gap["missing_preferred_skills"] == ["docker"]
    assert gap["required_coverage"] == 0.5
    assert gap["preferred_coverage"] == 0.5
    assert gap["overall_skill_coverage"] == pytest.approx(0.5)
    assert gap["meets_all_required"] is False


def test_full_coverage(mini_catalog):
    gap = analyze_skill_gap({"skills": ["html", "css", "js", "react"]}, "C002", mini_catalog)
    assert gap["required_coverage"] == 1.0 and gap["preferred_coverage"] == 1.0
    assert gap["meets_all_required"] is True
    assert gap["resources"] == {"required": [], "preferred": []}


def test_empty_profile_gap_is_all_missing(mini_catalog):
    gap = analyze_skill_gap({}, "C003", mini_catalog)
    assert gap["required_coverage"] == 0.0
    assert gap["missing_required_skills"] == ["accounting", "excel", "taxation"]


def test_resources_only_for_missing_skills_and_kept_separate(mini_catalog):
    gap = analyze_skill_gap({"skills": ["python"]}, "C001", mini_catalog)
    required = {e["skill"] for e in gap["resources"]["required"]}
    preferred = {e["skill"] for e in gap["resources"]["preferred"]}
    assert required == {"sql", "statistics", "machine learning"}
    assert preferred == {"git", "docker"}
    for entry in gap["resources"]["required"] + gap["resources"]["preferred"]:
        assert all(r["skill_name"] == entry["skill"] for r in entry["resources"])
    assert "not HTTP-checked" in gap["resource_note"]


def test_multiple_resources_sorted_by_level_with_verification(mini_catalog):
    gap = analyze_skill_gap({}, "C001", mini_catalog)
    sql = next(e for e in gap["resources"]["required"] if e["skill"] == "sql")
    assert [r["level"] for r in sql["resources"]] == ["beginner", "advanced"]
    assert sql["resources"][1]["url_verification"] == "unverified"
    assert sql["resources"][1]["is_free"] is False
    assert "not HTTP-checked" in sql["resources"][0]["url_verification_meaning"]


def test_unknown_career_and_invalid_input(mini_catalog):
    with pytest.raises(UnknownCareerError):
        analyze_skill_gap({}, "C999", mini_catalog)
    with pytest.raises(UnknownCareerError):
        analyze_skill_gap({}, 1, mini_catalog)
    with pytest.raises(ProfileValidationError):
        analyze_skill_gap({"skills": "python"}, "C001", mini_catalog)


def test_resource_catalog_lookup_rules():
    r1 = LearningResource("R002", "sql", "B", "P", "https://e.org/b", "course", "intermediate", True, "en", "search_index_confirmed")
    r2 = LearningResource("R001", "sql", "A", "P", "https://e.org/a", "guide", "beginner", True, "en", "search_index_confirmed")
    cat = ResourceCatalog([r1, r2])
    assert [r.resource_id for r in cat.for_skill("SQL")] == ["R001", "R002"]
    assert cat.for_skill("sql", level="intermediate") == (r1,)
    assert cat.for_skill("cobol") == ()
    assert cat.for_skill("postgres", aliases={"postgres": "sql"}) == (r2, r1)
    entries = cat.for_skills(["sql", "SQL", "cobol"])
    assert [e["skill"] for e in entries] == ["sql", "cobol"]
    assert entries[1] == {"skill": "cobol", "has_resources": False, "resources": []}
    with pytest.raises(ValueError):
        cat.for_skill("sql", level="expert")
