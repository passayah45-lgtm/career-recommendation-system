# Negative and positive tests for the career dataset rules

import pytest

from src.data.validation import CAREER_COLUMNS, ERROR, WARNING, validate_careers
from tests.conftest import career_row


def errors_for(rows, columns=CAREER_COLUMNS, expected_count=None):
    count = len(rows) if expected_count is None else expected_count
    return [i for i in validate_careers(rows, columns, count) if i.severity == ERROR]


def test_valid_rows_have_no_errors(valid_careers):
    assert errors_for(valid_careers) == []


def test_wrong_career_count_is_an_error(valid_careers):
    errors = errors_for(valid_careers, expected_count=50)
    assert any(e.field == "row count" and "found 2" in e.message for e in errors)


def test_duplicate_career_ids(valid_careers):
    rows = valid_careers + [career_row(1, career_title="Another Title")]
    errors = errors_for(rows)
    assert any(e.field == "career_id" and e.record == "C001" for e in errors)


def test_duplicate_titles_with_different_spelling():
    rows = [career_row(1, career_title="Data Analyst"), career_row(2, career_title="data-analyst")]
    errors = errors_for(rows)
    assert any(e.field == "career_title" for e in errors)


def test_missing_required_column(valid_careers):
    columns = [c for c in CAREER_COLUMNS if c != "category"]
    errors = errors_for(valid_careers, columns=columns)
    assert any(e.record == "header" and e.field == "category" for e in errors)


@pytest.mark.parametrize("field", ["career_title", "description", "required_skills", "interests", "learning_goals"])
def test_empty_required_field(field):
    errors = errors_for([career_row(1, **{field: "  "})])
    assert any(e.field == field and "missing or empty" in e.message for e in errors)


def test_invalid_category():
    errors = errors_for([career_row(1, category="Arts")])
    assert any(e.field == "category" and "Arts" in e.message for e in errors)


@pytest.mark.parametrize("value", ["-1", "5", "3.5", "three", " 3"])
def test_invalid_education_levels(value):
    errors = errors_for([career_row(1, education_level=value)])
    assert any(e.field == "education_level" for e in errors)


@pytest.mark.parametrize("value", ["0", "4"])
def test_education_bounds_are_valid(value):
    assert errors_for([career_row(1, education_level=value)]) == []


@pytest.mark.parametrize("skills", ["Python|sql", "python |sql", "python|sql  server", "machine_learning|sql", "c++|sql"])
def test_unnormalized_skill_names(skills):
    errors = errors_for([career_row(1, required_skills=skills)])
    assert any(e.field == "required_skills" and "not normalized" in e.message for e in errors)


@pytest.mark.parametrize("skills", ["python||sql", "|python", "python|", "python,sql|"])
def test_empty_tokens_and_malformed_lists(skills):
    errors = errors_for([career_row(1, required_skills=skills)])
    assert any(e.field == "required_skills" for e in errors)


def test_repeated_skill_in_list():
    errors = errors_for([career_row(1, required_skills="python|python")])
    assert any("repeated" in e.message for e in errors)


def test_skill_cannot_be_both_required_and_preferred():
    errors = errors_for([career_row(1, preferred_skills="python")])
    assert any(e.field == "preferred_skills" and "also a required skill" in e.message for e in errors)


def test_preferred_skills_may_be_empty():
    assert errors_for([career_row(1, preferred_skills="")]) == []


def test_malformed_preferred_skills():
    errors = errors_for([career_row(1, preferred_skills="Git||docker")])
    assert any(e.field == "preferred_skills" for e in errors)


def test_interest_outside_vocabulary():
    errors = errors_for([career_row(1, interests="technology|gaming")])
    assert any(e.field == "interests" and "gaming" in e.message for e in errors)


@pytest.mark.parametrize("url", ["onetonline.org/link/summary/15-1252.00", "ftp://example.org/x", "https://exa mple.org", "https://localhost/x"])
def test_invalid_source_url(url):
    errors = errors_for([career_row(1, source_url=url)])
    assert any(e.field == "source_url" for e in errors)


def test_source_url_must_match_onet_code():
    errors = errors_for([career_row(1, onet_code="15-1251.00")])
    assert any(e.field == "source_url" and "does not match" in e.message for e in errors)


def test_invalid_onet_code():
    errors = errors_for([career_row(1, onet_code="151252", source_url="")])
    assert any(e.field == "onet_code" for e in errors)


def test_missing_source_is_a_warning_not_an_error():
    issues = validate_careers([career_row(1, onet_code="", source_url="")], CAREER_COLUMNS, 1)
    assert not [i for i in issues if i.severity == ERROR]
    assert any(i.severity == WARNING and i.field == "source_url" for i in issues)
