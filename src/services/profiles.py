# Turns raw learner input into a validated LearnerProfile
# Skill names go through the Phase 2 normalize_skill function and the alias file

from collections.abc import Mapping
from dataclasses import dataclass

from src.data.preprocessing import clean_skill_text, normalize_skill
from src.engine.models import EDUCATION_MAX, EDUCATION_MIN, LearnerProfile

PROFILE_FIELDS = ("skills", "interests", "education_level", "experience_years")
MAX_EXPERIENCE_YEARS = 70
MAX_LIST_ITEMS = 200


class ProfileValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ProfileReport:
    # What happened to the raw input, so the interface can tell the learner
    recognized_skills: tuple = ()
    unknown_skills: tuple = ()
    duplicate_skills: tuple = ()
    recognized_interests: tuple = ()
    unknown_interests: tuple = ()
    missing_fields: tuple = ()
    ignored_fields: tuple = ()

    @property
    def skills_provided(self):
        return bool(self.recognized_skills)

    @property
    def interests_provided(self):
        return bool(self.recognized_interests)

    def to_dict(self):
        return {
            "recognized_skills": list(self.recognized_skills),
            "unknown_skills": list(self.unknown_skills),
            "duplicate_skills": list(self.duplicate_skills),
            "recognized_interests": list(self.recognized_interests),
            "unknown_interests": list(self.unknown_interests),
            "missing_fields": list(self.missing_fields),
            "ignored_fields": list(self.ignored_fields),
        }


def _as_text_list(value, name):
    if value is None:
        return []
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple, set, frozenset)):
        raise ProfileValidationError(f"{name} must be a list of text values")
    items = list(value)
    if len(items) > MAX_LIST_ITEMS:
        raise ProfileValidationError(f"{name} can hold at most {MAX_LIST_ITEMS} items")
    for item in items:
        if not isinstance(item, str):
            raise ProfileValidationError(f"every item in {name} must be text")
    if isinstance(value, (set, frozenset)):
        items = sorted(items)
    return items


def _as_optional_int(value, name, low, high):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProfileValidationError(f"{name} must be a whole number")
    if not low <= value <= high:
        raise ProfileValidationError(f"{name} must be between {low} and {high}")
    return value


def normalize_skills(raw_skills, known_skills, aliases):
    # Returns (recognized, unknown, duplicates) with first-seen order kept
    recognized, unknown, duplicates = [], [], []
    seen_unknown = set()
    for raw in raw_skills:
        canonical = normalize_skill(raw, aliases)
        if not canonical:
            continue
        if canonical in known_skills:
            if canonical in recognized:
                duplicates.append(raw.strip())
            else:
                recognized.append(canonical)
        elif canonical in seen_unknown:
            duplicates.append(raw.strip())
        else:
            seen_unknown.add(canonical)
            unknown.append(raw.strip())
    return tuple(recognized), tuple(unknown), tuple(duplicates)


def normalize_interests(raw_interests, known_interests):
    recognized, unknown = [], []
    for raw in raw_interests:
        value = clean_skill_text(raw)
        if not value:
            continue
        if value in known_interests:
            if value not in recognized:
                recognized.append(value)
        elif raw.strip() not in unknown:
            unknown.append(raw.strip())
    return tuple(recognized), tuple(unknown)


def build_profile(data, known_skills, aliases=None, known_interests=()):
    # Validates raw input and returns (LearnerProfile, ProfileReport)
    if data is None:
        data = {}
    if not isinstance(data, Mapping):
        raise ProfileValidationError("profile must be a mapping of field names to values")
    aliases = aliases or {}
    raw_skills = _as_text_list(data.get("skills"), "skills")
    raw_interests = _as_text_list(data.get("interests"), "interests")
    education = _as_optional_int(data.get("education_level"), "education_level", EDUCATION_MIN, EDUCATION_MAX)
    experience = _as_optional_int(data.get("experience_years"), "experience_years", 0, MAX_EXPERIENCE_YEARS)

    skills, unknown_skills, duplicates = normalize_skills(raw_skills, frozenset(known_skills), aliases)
    interests, unknown_interests = normalize_interests(raw_interests, frozenset(known_interests))

    missing = []
    if not skills:
        missing.append("skills")
    if not interests:
        missing.append("interests")
    if education is None:
        missing.append("education_level")
    ignored = tuple(sorted(k for k in data if k not in PROFILE_FIELDS))

    profile = LearnerProfile(skills=skills, interests=interests, education_level=education, experience_years=experience)
    report = ProfileReport(
        recognized_skills=skills, unknown_skills=unknown_skills, duplicate_skills=tuple(duplicates),
        recognized_interests=interests, unknown_interests=unknown_interests,
        missing_fields=tuple(missing), ignored_fields=ignored,
    )
    return profile, report
