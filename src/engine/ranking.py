# Deterministic ranking of careers for one profile
# Tie-break order: total score, required-skill coverage, matched required count, career_id

from dataclasses import dataclass

from src.engine.matching import CareerMatch, match_career
from src.engine.scoring import DEFAULT_WEIGHTS, REQUIRED_SKILLS, ScoreBreakdown, score_match

# Scores are compared after rounding so float noise cannot reorder equal scores
SCORE_PRECISION = 9


@dataclass(frozen=True)
class RankedCareer:
    rank: int
    match: CareerMatch
    score: ScoreBreakdown


def validate_top_k(top_k):
    if top_k is None:
        return None
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be a positive integer or None")
    return top_k


def sort_key(item):
    match, score = item
    req = score.component(REQUIRED_SKILLS)
    return (
        -round(score.total, SCORE_PRECISION),
        -round(req.value, SCORE_PRECISION),
        -len(match.skills.matched_required),
        match.career.career_id,
    )


def rank_careers(profile, careers, weights=DEFAULT_WEIGHTS, top_k=None,
                 skills_provided=True, interests_provided=True):
    # Scores every career and returns the top_k as RankedCareer objects
    top_k = validate_top_k(top_k)
    scored = []
    for career in careers:
        match = match_career(profile, career)
        scored.append((match, score_match(match, weights, skills_provided, interests_provided)))
    scored.sort(key=sort_key)
    if top_k is not None:
        scored = scored[:top_k]
    return [RankedCareer(rank=i, match=m, score=s) for i, (m, s) in enumerate(scored, start=1)]
