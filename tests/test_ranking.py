# Ranking order, determinism, top-K and tie-breaking on controlled careers

import pytest

from src.engine.models import LearnerProfile
from src.engine.ranking import rank_careers
from src.engine.scoring import ScoringWeights
from tests.conftest import make_career

CAREERS = [
    make_career("C003", ["accounting", "excel"], interests=("business",)),
    make_career("C001", ["python", "sql"], ["git"], interests=("technology",)),
    make_career("C002", ["python", "linux", "docker", "git"], interests=("technology",)),
]


def ids(ranked):
    return [r.match.career.career_id for r in ranked]


def test_expected_order_and_ranks():
    profile = LearnerProfile(skills=("python", "sql"), interests=("technology",), education_level=3)
    ranked = rank_careers(profile, CAREERS)
    assert ids(ranked) == ["C001", "C002", "C003"]
    assert [r.rank for r in ranked] == [1, 2, 3]
    totals = [r.score.total for r in ranked]
    assert totals == sorted(totals, reverse=True)


def test_ranking_is_deterministic_and_input_order_independent():
    profile = LearnerProfile(skills=("python",), interests=("technology",), education_level=3)
    first = [(r.match.career.career_id, r.score.total) for r in rank_careers(profile, CAREERS)]
    again = [(r.match.career.career_id, r.score.total) for r in rank_careers(profile, list(reversed(CAREERS)))]
    assert first == again


def test_top_k_limits_results_without_changing_data():
    profile = LearnerProfile(skills=("python",))
    before = list(CAREERS)
    assert len(rank_careers(profile, CAREERS, top_k=2)) == 2
    assert len(rank_careers(profile, CAREERS, top_k=10)) == 3
    assert CAREERS == before


@pytest.mark.parametrize("bad", [0, -1, 2.5, "3", True])
def test_invalid_top_k(bad):
    with pytest.raises(ValueError):
        rank_careers(LearnerProfile(), CAREERS, top_k=bad)


def test_full_ties_break_by_career_id():
    careers = [make_career(cid, ["python", "sql"]) for cid in ("C009", "C002", "C005")]
    ranked = rank_careers(LearnerProfile(skills=("python",)), careers)
    assert len({r.score.total for r in ranked}) == 1
    assert ids(ranked) == ["C002", "C005", "C009"]


def test_equal_total_breaks_by_required_coverage_before_id():
    # With equal skill weights both careers score 75, but C002 covers all its required skills
    weights = ScoringWeights(required_skills=0.5, preferred_skills=0.5, interests=0, education=0)
    a = make_career("C001", ["python", "sql"], ["git"])
    b = make_career("C002", ["python"], ["docker", "git"])
    ranked = rank_careers(LearnerProfile(skills=("python", "git")), [a, b], weights=weights)
    assert [r.score.total for r in ranked] == [pytest.approx(75.0), pytest.approx(75.0)]
    assert ids(ranked) == ["C002", "C001"]


def test_higher_total_wins_over_lower_career_id():
    a = make_career("C001", ["java", "kotlin"])
    b = make_career("C002", ["python", "sql"])
    assert ids(rank_careers(LearnerProfile(skills=("python",)), [a, b])) == ["C002", "C001"]


def test_empty_profile_lists_careers_in_id_order_with_zero_scores():
    ranked = rank_careers(LearnerProfile(), CAREERS, skills_provided=False, interests_provided=False)
    assert ids(ranked) == ["C001", "C002", "C003"]
    assert all(r.score.total == 0.0 for r in ranked)


def test_education_alone_cannot_reorder_skill_matches():
    skilled = make_career("C001", ["python", "sql"], education=4)
    unskilled = make_career("C002", ["java", "kotlin"], education=0)
    profile = LearnerProfile(skills=("python",), education_level=0)
    assert ids(rank_careers(profile, [unskilled, skilled])) == ["C001", "C002"]


def test_interest_match_reorders_equal_skill_matches():
    a = make_career("C001", ["python", "sql"], interests=("business",))
    b = make_career("C002", ["python", "sql"], interests=("technology",))
    profile = LearnerProfile(skills=("python",), interests=("technology",))
    assert ids(rank_careers(profile, [a, b])) == ["C002", "C001"]
