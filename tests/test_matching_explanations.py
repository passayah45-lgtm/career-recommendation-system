# Skill, interest and education matching plus explanation content

from src.engine.explanations import build_notes, build_reasons
from src.engine.matching import match_career, match_education, match_interests, match_skills
from src.engine.models import LearnerProfile
from src.engine.scoring import score_match
from tests.conftest import make_career

CAREER = make_career("C001", ["python", "sql", "statistics"], ["git", "docker"], ["analysis", "technology", "research"], education=3)


def test_skill_match_keeps_career_order_and_splits_lists():
    m = match_skills(("sql", "git", "rust"), CAREER)
    assert m.matched_required == ("sql",)
    assert m.missing_required == ("python", "statistics")
    assert m.matched_preferred == ("git",)
    assert m.missing_preferred == ("docker",)


def test_interest_and_education_matching():
    assert match_interests(("research", "art", "analysis"), CAREER) == ("analysis", "research")
    assert match_education(2, CAREER).gap == 1
    assert match_education(4, CAREER).meets_level is True
    assert match_education(None, CAREER).gap is None
    assert match_education(None, CAREER).meets_level is None


def explain(profile, **kw):
    match = match_career(profile, CAREER)
    score = score_match(match, **kw)
    return build_reasons(match, score), build_notes(match, score)


def test_reasons_reflect_actual_matches_only():
    reasons, notes = explain(LearnerProfile(skills=("python", "git"), interests=("analysis",), education_level=2))
    text = " ".join(reasons)
    assert "1 of 3 required skills: python" in text
    assert "1 of 2 preferred (optional) skills: git" in text
    assert "1 of 3 for this career: analysis" in text
    assert "1 level(s) below" in text
    assert "Missing required skills: sql, statistics." in notes


def test_no_invented_reasons_for_unmatched_components():
    reasons, notes = explain(LearnerProfile(skills=("rust",)), interests_provided=False)
    assert reasons == ("You have none of the 3 required skills yet.",)
    assert any("No recognized interests" in n for n in notes)
    assert any("No education level" in n for n in notes)


def test_empty_profile_notes():
    _, notes = explain(LearnerProfile(), skills_provided=False, interests_provided=False)
    assert any("No recognized skills" in n for n in notes)
