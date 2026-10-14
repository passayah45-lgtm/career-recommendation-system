# Exact score calculations, ranges and weight validation

import math

import pytest

from src.engine.matching import match_career
from src.engine.models import LearnerProfile
from src.engine.scoring import (
    DEFAULT_WEIGHTS, EDUCATION, INTERESTS, PREFERRED_SKILLS, REQUIRED_SKILLS, ScoringWeights, coverage, score_match,
)
from tests.conftest import make_career

CAREER = make_career("C001", ["python", "sql", "statistics", "machine learning"], ["git", "docker"],
                     ["analysis", "technology", "research"], education=3)


def score(profile, career=CAREER, weights=DEFAULT_WEIGHTS, **kw):
    return score_match(match_career(profile, career), weights, **kw)


def test_default_weights_sum_to_one_and_favor_skills():
    w = DEFAULT_WEIGHTS.as_dict()
    assert math.isclose(sum(w.values()), 1.0)
    assert w[REQUIRED_SKILLS] > w[PREFERRED_SKILLS]
    assert w[REQUIRED_SKILLS] + w[PREFERRED_SKILLS] > 0.5
    assert w[EDUCATION] == min(w.values())


def test_exact_total_for_known_profile():
    profile = LearnerProfile(skills=("python", "sql", "git"), interests=("analysis",), education_level=3)
    s = score(profile)
    # 0.55*2/4 + 0.15*1/2 + 0.25*1/3 + 0.05*1 = 0.275 + 0.075 + 0.08333 + 0.05
    assert s.total == pytest.approx(48.3333, abs=1e-3)
    assert s.component(REQUIRED_SKILLS).value == 0.5
    assert s.component(PREFERRED_SKILLS).value == 0.5
    assert s.component(INTERESTS).value == pytest.approx(1 / 3)
    assert s.component(EDUCATION).value == 1.0
    assert sum(c.contribution for c in s.components) == pytest.approx(s.total)


def test_perfect_profile_scores_100():
    profile = LearnerProfile(skills=CAREER.required_skills + CAREER.preferred_skills,
                             interests=CAREER.interests, education_level=4)
    assert score(profile).total == pytest.approx(100.0)


def test_empty_profile_scores_zero_not_perfect():
    s = score(LearnerProfile(), skills_provided=False, interests_provided=False)
    assert s.total == 0.0
    assert all(c.value == 0.0 for c in s.components)
    assert not s.component(REQUIRED_SKILLS).provided
    assert not s.component(EDUCATION).provided


@pytest.mark.parametrize("learner,expected", [(4, 1.0), (3, 1.0), (2, 0.75), (1, 0.5), (0, 0.25)])
def test_education_partial_credit(learner, expected):
    s = score(LearnerProfile(education_level=learner))
    assert s.component(EDUCATION).value == pytest.approx(expected)


def test_education_never_outweighs_one_required_skill():
    # Largest education effect: 4 levels below versus meeting the level
    career = make_career("X", ["python", "sql"], ["git"], education=4)
    low = score(LearnerProfile(skills=("python",), education_level=0), career=career)
    high = score(LearnerProfile(skills=("python",), education_level=4), career=career)
    one_skill = score(LearnerProfile(skills=("python", "sql"), education_level=0), career=career)
    education_effect = high.total - low.total
    skill_effect = one_skill.total - low.total
    assert education_effect == pytest.approx(DEFAULT_WEIGHTS.education * 100)
    assert skill_effect > education_effect


def test_education_share_is_capped_when_preferred_component_is_absent():
    # Renormalization raises education to 0.05 / 0.85 of the score, still under 6 points
    career = make_career("X", ["python", "sql"], education=4)
    low = score(LearnerProfile(education_level=0), career=career)
    high = score(LearnerProfile(education_level=4), career=career)
    assert high.total - low.total == pytest.approx(100 * 0.05 / 0.85)


def test_required_and_preferred_are_scored_separately():
    req_only = score(LearnerProfile(skills=("python",)))
    pref_only = score(LearnerProfile(skills=("git",)))
    assert req_only.component(REQUIRED_SKILLS).value == 0.25
    assert req_only.component(PREFERRED_SKILLS).value == 0.0
    assert pref_only.component(REQUIRED_SKILLS).value == 0.0
    assert pref_only.component(PREFERRED_SKILLS).value == 0.5
    # One required skill (0.55/4) is worth more than one preferred skill (0.15/2)
    assert req_only.total > pref_only.total


def test_career_without_preferred_skills_renormalizes_weights():
    career = make_career("X", ["python"], preferred=(), interests=("technology",), education=3)
    profile = LearnerProfile(skills=("python",), interests=("technology",), education_level=3)
    s = score(profile, career=career)
    assert not s.component(PREFERRED_SKILLS).applicable
    assert s.total == pytest.approx(100.0)


def test_scores_stay_finite_and_in_range_for_unusual_weights():
    weights = ScoringWeights(required_skills=10, preferred_skills=0, interests=0, education=0)
    for profile in [LearnerProfile(), LearnerProfile(skills=("python",)), LearnerProfile(skills=CAREER.required_skills)]:
        s = score(profile, weights=weights)
        assert math.isfinite(s.total) and 0.0 <= s.total <= 100.0


@pytest.mark.parametrize("kwargs", [{"required_skills": -0.1}, {"interests": float("nan")}, {"education": float("inf")},
                                    {"required_skills": "high"}, {"preferred_skills": True},
                                    {"required_skills": 0, "preferred_skills": 0, "interests": 0, "education": 0}])
def test_invalid_weights_are_rejected(kwargs):
    with pytest.raises(ValueError):
        ScoringWeights(**kwargs)


def test_coverage_helper():
    assert coverage(0, 0) is None
    assert coverage(1, 4) == 0.25
