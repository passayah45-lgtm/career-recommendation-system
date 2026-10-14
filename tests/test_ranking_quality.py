# Ranking-quality regressions on the real dataset and the labelled profiles

import pytest

from src.engine.scoring import DEFAULT_WEIGHTS, ScoringWeights
from src.evaluation.dataset import load_profiles
from src.evaluation.experiments import CONFIGURATIONS
from src.services.catalog import load_catalog
from src.services.recommendations import recommend
from src.services.skill_gap import analyze_skill_gap


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


@pytest.fixture(scope="module")
def profiles(catalog):
    return load_profiles([c.career_id for c in catalog.careers])


def test_baseline_weights_unchanged():
    assert DEFAULT_WEIGHTS == ScoringWeights(0.55, 0.15, 0.25, 0.05)
    assert CONFIGURATIONS["A_baseline"] is DEFAULT_WEIGHTS


def test_worked_example_baseline_output(catalog):
    profile = {"skills": ["Python", "SQL", "Excel", "ML", "statistics"], "interests": ["analysis", "mathematics"],
               "education_level": 3}
    recs = recommend(profile, catalog, top_k=5)["recommendations"]
    assert [(r["career_id"], r["score"]) for r in recs] == [
        ("C001", 61.5), ("C002", 59.6), ("C029", 55.0), ("C031", 50.8), ("C006", 41.7)]


def test_required_skills_drive_ranking(catalog):
    # Adding one required skill of a career must raise its score by at least 0.55 / 5 of the scale
    base = recommend({"skills": ["sql"]}, catalog, top_k=None)["recommendations"]
    more = recommend({"skills": ["sql", "excel"]}, catalog, top_k=None)["recommendations"]
    b = {r["career_id"]: r["score"] for r in base}
    a = {r["career_id"]: r["score"] for r in more}
    for career in catalog.careers:
        if "excel" in career.required_skills:
            assert a[career.career_id] - b[career.career_id] >= 55 / 5 - 0.1


def test_education_cannot_beat_a_required_skill(catalog):
    # A learner at level 0 with a career's skill outranks the same learner's education-only advantage
    for career in catalog.careers:
        skill = career.required_skills[0]
        with_skill = recommend({"skills": [skill], "education_level": 0}, catalog, top_k=None)["recommendations"]
        without = recommend({"education_level": 4}, catalog, top_k=None)["recommendations"]
        s_skill = next(r["score"] for r in with_skill if r["career_id"] == career.career_id)
        s_edu = next(r["score"] for r in without if r["career_id"] == career.career_id)
        assert s_skill > s_edu, career.career_id


def test_rankings_deterministic_unique_and_real(catalog, profiles):
    ids = {c.career_id for c in catalog.careers}
    for p in profiles:
        first = recommend(p.as_input(), catalog, top_k=10)
        second = recommend(p.as_input(), catalog, top_k=10)
        assert first == second
        top = [r["career_id"] for r in first["recommendations"]]
        assert len(top) == len(set(top)) == 10
        assert set(top) <= ids


def test_unknown_skills_never_match(catalog, profiles):
    for p in profiles:
        result = recommend(p.as_input(), catalog, top_k=None)
        unknown = {s.lower() for s in result["profile"]["report"]["unknown_skills"]}
        for rec in result["recommendations"]:
            matched = set(rec["matched_required_skills"]) | set(rec["matched_preferred_skills"])
            assert not matched & unknown


def test_missing_inputs_handled_consistently(catalog):
    for profile in ({}, {"skills": []}, {"interests": []}, {"education_level": None}, None):
        result = recommend(profile, catalog, top_k=3)
        assert [r["score"] for r in result["recommendations"]] == [0.0, 0.0, 0.0]
        assert [r["career_id"] for r in result["recommendations"]] == ["C001", "C002", "C003"]


def test_skill_gaps_match_career_requirements_and_resources(catalog, profiles):
    for p in profiles:
        for career in catalog.careers[::5]:
            gap = analyze_skill_gap(p.as_input(), career.career_id, catalog)
            assert set(gap["have_required_skills"]) | set(gap["missing_required_skills"]) == set(career.required_skills)
            assert set(gap["have_preferred_skills"]) | set(gap["missing_preferred_skills"]) == set(career.preferred_skills)
            assert [e["skill"] for e in gap["resources"]["required"]] == gap["missing_required_skills"]
            assert [e["skill"] for e in gap["resources"]["preferred"]] == gap["missing_preferred_skills"]
            for entry in gap["resources"]["required"] + gap["resources"]["preferred"]:
                assert entry["resources"] and all(r["skill_name"] == entry["skill"] for r in entry["resources"])


@pytest.mark.parametrize("bad", ["python", 42, ["python"], {"skills": [None]}, {"education_level": "high"}])
def test_malformed_inputs_raise_clear_errors(catalog, bad):
    from src.services.profiles import ProfileValidationError
    with pytest.raises(ProfileValidationError):
        recommend(bad, catalog)
