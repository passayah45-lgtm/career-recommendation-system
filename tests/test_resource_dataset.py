# Negative and positive tests for the learning resource dataset rules

import pytest

from src.data.validation import ERROR, RESOURCE_COLUMNS, WARNING, validate_aliases, validate_resources
from tests.conftest import resource_row

REQUIRED = {"python", "sql"}
PREFERRED = {"git"}


def issues_for(rows, columns=RESOURCE_COLUMNS, required=REQUIRED, preferred=PREFERRED):
    return validate_resources(rows, columns, required, preferred)


def errors_for(rows, **kwargs):
    return [i for i in issues_for(rows, **kwargs) if i.severity == ERROR]


def test_valid_resources_have_no_errors(valid_resources):
    assert errors_for(valid_resources) == []


def test_missing_resource_for_required_skill(valid_resources):
    rows = [r for r in valid_resources if r["skill_name"] != "sql"]
    errors = errors_for(rows)
    assert any(e.record == "sql" and "required skill has no learning resource" in e.message for e in errors)


def test_missing_resource_for_preferred_skill(valid_resources):
    rows = [r for r in valid_resources if r["skill_name"] != "git"]
    errors = errors_for(rows)
    assert any(e.record == "git" and "preferred skill has no learning resource" in e.message for e in errors)


def test_resource_for_unknown_skill(valid_resources):
    rows = valid_resources + [resource_row(4, "cobol")]
    errors = errors_for(rows)
    assert any(e.field == "skill_name" and "cobol" in e.message for e in errors)


def test_unnormalized_resource_skill(valid_resources):
    rows = valid_resources + [resource_row(4, "Python")]
    errors = errors_for(rows)
    assert any(e.field == "skill_name" and "not normalized" in e.message for e in errors)


@pytest.mark.parametrize("value", ["True", "yes", "1", "partly"])
def test_invalid_boolean(valid_resources, value):
    valid_resources[0]["is_free"] = value
    errors = errors_for(valid_resources)
    assert any(e.field == "is_free" and e.record == "R001" for e in errors)


@pytest.mark.parametrize("url", ["docs.python.org/3/tutorial", "http//bad", "https://exa mple.org/x", "mailto:a@b.org"])
def test_invalid_resource_url(valid_resources, url):
    valid_resources[0]["resource_url"] = url
    errors = errors_for(valid_resources)
    assert any(e.field == "resource_url" and e.record == "R001" for e in errors)


def test_duplicate_resource_ids(valid_resources):
    valid_resources[1]["resource_id"] = "R001"
    errors = errors_for(valid_resources)
    assert any(e.field == "resource_id" and e.record == "R001" for e in errors)


def test_duplicate_resource_for_same_skill(valid_resources):
    copy = dict(valid_resources[0], resource_id="R009")
    errors = errors_for(valid_resources + [copy])
    assert any("listed 2 times" in e.message for e in errors)


def test_reused_url_across_skills_is_a_warning(valid_resources):
    valid_resources[1]["resource_url"] = valid_resources[0]["resource_url"]
    issues = issues_for(valid_resources)
    assert not [i for i in issues if i.severity == ERROR]
    assert any(i.severity == WARNING and "reused" in i.message for i in issues)


@pytest.mark.parametrize("field,value", [("resource_type", "video"), ("level", "expert"), ("language", "english"), ("url_verification", "maybe"), ("verified_on", "14/10/2026")])
def test_undocumented_values(valid_resources, field, value):
    valid_resources[0][field] = value
    errors = errors_for(valid_resources)
    assert any(e.field == field for e in errors)


def test_unverified_url_is_a_warning(valid_resources):
    valid_resources[0]["url_verification"] = "unverified"
    issues = issues_for(valid_resources)
    assert not [i for i in issues if i.severity == ERROR]
    assert any(i.severity == WARNING and i.field == "url_verification" for i in issues)


def test_empty_title_is_an_error(valid_resources):
    valid_resources[0]["resource_title"] = ""
    errors = errors_for(valid_resources)
    assert any(e.field == "resource_title" for e in errors)


def test_missing_resource_column(valid_resources):
    columns = [c for c in RESOURCE_COLUMNS if c != "is_free"]
    errors = errors_for(valid_resources, columns=columns)
    assert any(e.record == "header" and e.field == "is_free" for e in errors)


def test_alias_rules():
    columns = ["alias", "canonical_skill"]
    rows = [
        {"alias": "py", "canonical_skill": "python"},
        {"alias": "python", "canonical_skill": "python"},
        {"alias": "pg", "canonical_skill": "postgres"},
        {"alias": "Py3", "canonical_skill": "python"},
    ]
    errors = [i for i in validate_aliases(rows, columns, {"python", "sql"}) if i.severity == ERROR]
    messages = " ".join(e.message for e in errors)
    assert "already a canonical skill" in messages
    assert "'postgres' is not a canonical skill" in messages
    assert "lowercase" in messages
    assert not [e for e in errors if e.record == "py"]
