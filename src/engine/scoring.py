# Transparent weighted scoring
# Each component is a value from 0 to 1, the total is a 0 to 100 compatibility score
# The score ranks careers for one learner. It is not a probability of hiring or success.

import math
from dataclasses import dataclass, fields

from src.engine.matching import CareerMatch
from src.engine.models import EDUCATION_MAX, EDUCATION_MIN

REQUIRED_SKILLS = "required_skills"
PREFERRED_SKILLS = "preferred_skills"
INTERESTS = "interests"
EDUCATION = "education"
COMPONENT_ORDER = (REQUIRED_SKILLS, PREFERRED_SKILLS, INTERESTS, EDUCATION)

# Score lost per education level below the career level
EDUCATION_GAP_PENALTY = 1 / (EDUCATION_MAX - EDUCATION_MIN)


@dataclass(frozen=True)
class ScoringWeights:
    required_skills: float = 0.55
    preferred_skills: float = 0.15
    interests: float = 0.25
    education: float = 0.05

    def __post_init__(self):
        for f in fields(self):
            value = getattr(self, f.name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"weight '{f.name}' must be a number")
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"weight '{f.name}' must be finite and not negative")
        if sum(self.as_dict().values()) <= 0:
            raise ValueError("at least one weight must be positive")

    def as_dict(self):
        return {name: float(getattr(self, name)) for name in COMPONENT_ORDER}


DEFAULT_WEIGHTS = ScoringWeights()


@dataclass(frozen=True)
class ComponentScore:
    name: str
    value: float
    weight: float
    applicable: bool
    provided: bool
    contribution: float = 0.0


@dataclass(frozen=True)
class ScoreBreakdown:
    components: tuple
    total: float

    def component(self, name):
        for c in self.components:
            if c.name == name:
                return c
        raise KeyError(name)


def coverage(matched, total):
    # Share of items covered, None when there is nothing to cover
    if total <= 0:
        return None
    return matched / total


def education_value(match):
    gap = match.education.gap
    if gap is None:
        return 0.0
    return max(0.0, 1.0 - gap * EDUCATION_GAP_PENALTY)


def _raw_components(match: CareerMatch, skills_provided, interests_provided):
    # Returns (name, value or None, provided) for each component
    sk = match.skills
    career = match.career
    req = coverage(len(sk.matched_required), len(career.required_skills))
    pref = coverage(len(sk.matched_preferred), len(career.preferred_skills))
    inter = coverage(len(match.matched_interests), len(career.interests))
    return (
        (REQUIRED_SKILLS, req, skills_provided),
        (PREFERRED_SKILLS, pref, skills_provided),
        (INTERESTS, inter, interests_provided),
        (EDUCATION, education_value(match), match.education.provided),
    )


def score_match(match: CareerMatch, weights: ScoringWeights = DEFAULT_WEIGHTS,
                skills_provided=True, interests_provided=True):
    # A component is not applicable when the career has nothing to compare, for example no preferred skills
    # Missing learner input stays applicable and scores 0, so it never counts as a match
    w = weights.as_dict()
    raw = _raw_components(match, skills_provided, interests_provided)
    applicable_weight = sum(w[name] for name, value, _ in raw if value is not None)
    parts = []
    for name, value, provided in raw:
        applicable = value is not None
        v = float(value) if applicable else 0.0
        share = (w[name] / applicable_weight) if applicable and applicable_weight > 0 else 0.0
        parts.append(ComponentScore(name, v, w[name], applicable, provided, share * v * 100))
    total = sum(p.contribution for p in parts)
    total = min(100.0, max(0.0, total))
    return ScoreBreakdown(components=tuple(parts), total=total)
