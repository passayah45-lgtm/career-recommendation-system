# Profile validation, alias normalization, duplicates and unknown inputs

import pytest

from src.services.profiles import ProfileValidationError, build_profile

KNOWN = {"python", "sql", "machine learning", "ci cd", "javascript"}
ALIASES = {"ml": "machine learning", "ci/cd": "ci cd", "js": "javascript"}
INTERESTS = {"analysis", "problem solving", "technology"}


def build(data):
    return build_profile(data, KNOWN, ALIASES, INTERESTS)


def test_aliases_and_case_resolve_to_canonical_names():
    profile, report = build({"skills": ["ML", "  Python ", "CI/CD", "js"]})
    assert profile.skills == ("machine learning", "python", "ci cd", "javascript")
    assert report.unknown_skills == ()


def test_alias_and_canonical_name_count_once():
    profile, report = build({"skills": ["machine learning", "ML", "Machine_Learning"]})
    assert profile.skills == ("machine learning",)
    assert len(report.duplicate_skills) == 2


def test_unknown_skills_are_reported_not_matched():
    profile, report = build({"skills": ["python", "Blockchain", "blockchain"]})
    assert profile.skills == ("python",)
    assert report.unknown_skills == ("Blockchain",)
    assert report.duplicate_skills == ("blockchain",)


def test_only_unknown_skills_means_skills_missing():
    profile, report = build({"skills": ["cobol"]})
    assert profile.skills == ()
    assert "skills" in report.missing_fields
    assert not report.skills_provided


def test_interests_are_normalized_and_unknown_reported():
    profile, report = build({"interests": ["Problem-Solving", "technology", "gaming", "TECHNOLOGY"]})
    assert profile.interests == ("problem solving", "technology")
    assert report.unknown_interests == ("gaming",)


def test_empty_and_none_profiles():
    for data in (None, {}, {"skills": [], "interests": [" ", ""]}):
        profile, report = build(data)
        assert profile.skills == () and profile.interests == () and profile.education_level is None
        assert set(report.missing_fields) == {"skills", "interests", "education_level"}


def test_unsupported_fields_are_ignored_and_reported():
    _, report = build({"skills": ["python"], "salary": 100})
    assert report.ignored_fields == ("salary",)


@pytest.mark.parametrize("data", [
    "python", ["python"], {"skills": "python, sql"}, {"skills": [1, 2]}, {"interests": "technology"},
    {"education_level": 5}, {"education_level": -1}, {"education_level": "3"}, {"education_level": 2.5},
    {"education_level": True}, {"experience_years": -2}, {"experience_years": 200},
    {"skills": ["x"] * 201},
])
def test_invalid_inputs_raise(data):
    with pytest.raises(ProfileValidationError):
        build(data)


def test_valid_education_and_experience():
    profile, report = build({"skills": ["sql"], "interests": ["analysis"], "education_level": 0, "experience_years": 0})
    assert profile.education_level == 0 and profile.experience_years == 0
    assert report.missing_fields == ()
