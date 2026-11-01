# Accent folding for French skill input; English matching and aliases must behave exactly as before

import pytest

from src.data.preprocessing import clean_skill_text, fold_accents, normalize_skill
from src.data.validation import ALIAS_COLUMNS, validate_aliases
from src.services.catalog import load_catalog
from src.services.recommendations import profile_from_input


@pytest.mark.parametrize("text", ["Géologie", "géologie", "GÉOLOGIE", "geologie", "  Géologie  "])
def test_accented_and_plain_forms_clean_the_same(text):
    assert clean_skill_text(text) == "geologie"


def test_fold_accents_leaves_ascii_unchanged():
    for text in ("python", "ci cd", "machine learning", "C++", "3d modeling"):
        assert fold_accents(text) == text
    assert fold_accents("mécanique des sols") == "mecanique des sols"
    assert fold_accents("naïve façade") == "naive facade"


@pytest.mark.parametrize("aliases", [{"géologie": "geology"}, {"geologie": "geology"}])
@pytest.mark.parametrize("text", ["Géologie", "géologie", "geologie", "GEOLOGIE"])
def test_aliases_match_with_or_without_accents(aliases, text):
    assert normalize_skill(text, aliases) == "geology"


def test_existing_english_aliases_are_unchanged():
    catalog = load_catalog()
    for alias, target in catalog.aliases.items():
        assert normalize_skill(alias, catalog.aliases) == target
        assert normalize_skill(alias.upper(), catalog.aliases) == target
    assert normalize_skill("CI/CD", catalog.aliases) == "ci cd"
    assert normalize_skill("Python", catalog.aliases) == "python"
    assert normalize_skill("unknown thing", catalog.aliases) == "unknown thing"


def test_profile_reports_french_skill_as_typed():
    # Unknown skills are reported back exactly as the learner typed them
    profile, report = profile_from_input({"skills": ["Cartographie", "Python"]}, load_catalog())
    assert list(report.unknown_skills) == ["Cartographie"]
    assert list(profile.skills) == ["python"]


@pytest.mark.parametrize("text", ["Géologie", "géologie", "geologie", "GÉOLOGIE", "GEOLOGIE"])
def test_french_geology_reaches_the_live_skill(text):
    # The live alias file maps géologie to the geology skill added in dataset v1.3.0
    catalog = load_catalog()
    profile, report = profile_from_input({"skills": [text]}, catalog)
    assert list(profile.skills) == ["geology"] and list(report.unknown_skills) == []


@pytest.mark.parametrize("text, skill", [
    ("Mécanique des sols", "soil mechanics"), ("mecanique des sols", "soil mechanics"),
    ("Droit administratif", "administrative law"), ("ÉCONOMIE", "economics"), ("Sociologie", "sociology"),
    ("RF engineering", "radio frequency engineering"), ("ML", "machine learning"),
])
def test_new_french_and_english_aliases(text, skill):
    assert normalize_skill(text, load_catalog().aliases) == skill


def test_colliding_folded_aliases_are_rejected():
    rows = [{"alias": "géologie", "canonical_skill": "python"}, {"alias": "geologie", "canonical_skill": "sql"}]
    issues = validate_aliases(rows, ALIAS_COLUMNS, {"python", "sql"})
    assert any("fold to the same text" in i.message for i in issues)
    shadow = [{"alias": "pythön", "canonical_skill": "sql"}]
    issues = validate_aliases(shadow, ALIAS_COLUMNS, {"python", "sql"})
    assert any("different canonical skill" in i.message for i in issues)
