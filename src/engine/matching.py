# Compares one learner profile with one career
# Results keep the career's own skill order so output is stable

from dataclasses import dataclass
from typing import Optional

from src.engine.models import Career, LearnerProfile


@dataclass(frozen=True)
class SkillMatch:
    matched_required: tuple
    missing_required: tuple
    matched_preferred: tuple
    missing_preferred: tuple


@dataclass(frozen=True)
class EducationMatch:
    learner_level: Optional[int]
    career_level: int

    @property
    def provided(self):
        return self.learner_level is not None

    @property
    def gap(self):
        # Levels below the career level, 0 when met, None when not provided
        if self.learner_level is None:
            return None
        return max(0, self.career_level - self.learner_level)

    @property
    def meets_level(self):
        return None if self.gap is None else self.gap == 0


@dataclass(frozen=True)
class CareerMatch:
    career: Career
    skills: SkillMatch
    matched_interests: tuple
    education: EducationMatch


def _split(items, owned):
    matched = tuple(s for s in items if s in owned)
    missing = tuple(s for s in items if s not in owned)
    return matched, missing


def match_skills(skills, career):
    owned = frozenset(skills)
    m_req, x_req = _split(career.required_skills, owned)
    m_pref, x_pref = _split(career.preferred_skills, owned)
    return SkillMatch(m_req, x_req, m_pref, x_pref)


def match_interests(interests, career):
    owned = frozenset(interests)
    return tuple(i for i in career.interests if i in owned)


def match_education(level, career):
    return EducationMatch(learner_level=level, career_level=career.education_level)


def match_career(profile: LearnerProfile, career: Career):
    return CareerMatch(
        career=career,
        skills=match_skills(profile.skills, career),
        matched_interests=match_interests(profile.interests, career),
        education=match_education(profile.education_level, career),
    )
