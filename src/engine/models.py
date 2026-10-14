# Immutable data types shared by the engine
# The engine reads these objects and never changes them

from dataclasses import dataclass
from typing import Optional

EDUCATION_MIN = 0
EDUCATION_MAX = 4


@dataclass(frozen=True)
class Career:
    # One row of careers.csv with list fields stored as tuples
    career_id: str
    title: str
    category: str
    description: str
    required_skills: tuple
    preferred_skills: tuple
    education_level: int
    interests: tuple
    learning_goals: tuple = ()
    source_url: str = ""


@dataclass(frozen=True)
class LearnerProfile:
    # A validated profile: skills are canonical names that exist in the dataset
    skills: tuple = ()
    interests: tuple = ()
    education_level: Optional[int] = None
    experience_years: Optional[int] = None

    @property
    def skill_set(self):
        return frozenset(self.skills)

    @property
    def interest_set(self):
        return frozenset(self.interests)
