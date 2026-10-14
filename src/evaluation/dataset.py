# Loads and checks the labelled synthetic evaluation profiles

import json
from dataclasses import dataclass
from pathlib import Path

from src.data.validation import CATEGORIES

DEFAULT_PROFILES_PATH = Path(__file__).resolve().parents[2] / "data" / "evaluation" / "labelled_profiles.json"
PROFILE_TYPES = (
    "strong match", "mixed skills", "career transition", "limited skills",
    "missing information", "overlapping interests",
)
MAX_RELEVANT = 3


class EvaluationDataError(ValueError):
    pass


@dataclass(frozen=True)
class LabelledProfile:
    profile_id: str
    primary_category: str
    profile_type: str
    description: str
    skills: tuple
    interests: tuple
    education_level: object
    relevant_career_ids: tuple
    relevance_explanation: str

    def as_input(self):
        # The raw profile dict exactly as a learner would submit it
        data = {"skills": list(self.skills), "interests": list(self.interests)}
        if self.education_level is not None:
            data["education_level"] = self.education_level
        return data


def _check(condition, message):
    if not condition:
        raise EvaluationDataError(message)


def parse_profiles(data, career_ids):
    # Validates the JSON structure and returns LabelledProfile objects
    _check(isinstance(data, dict) and isinstance(data.get("profiles"), list), "file must hold a 'profiles' list")
    profiles, seen = [], set()
    for raw in data["profiles"]:
        pid = raw.get("profile_id")
        _check(isinstance(pid, str) and pid, "every profile needs a profile_id")
        _check(pid not in seen, f"{pid}: duplicate profile_id")
        seen.add(pid)
        _check(raw.get("primary_category") in CATEGORIES, f"{pid}: unknown primary_category")
        _check(raw.get("profile_type") in PROFILE_TYPES, f"{pid}: unknown profile_type")
        for field in ("skills", "interests", "relevant_career_ids"):
            _check(isinstance(raw.get(field), list) and all(isinstance(x, str) for x in raw[field]),
                   f"{pid}: {field} must be a list of text")
        relevant = raw["relevant_career_ids"]
        _check(len(relevant) == len(set(relevant)), f"{pid}: repeated relevant career")
        _check(len(relevant) <= MAX_RELEVANT, f"{pid}: more than {MAX_RELEVANT} relevant careers")
        unknown = [c for c in relevant if c not in career_ids]
        _check(not unknown, f"{pid}: relevant careers not in the catalogue: {unknown}")
        _check(bool(raw.get("relevance_explanation")), f"{pid}: relevance_explanation is required")
        _check(bool(raw.get("rationale")), f"{pid}: rationale is required")
        profiles.append(LabelledProfile(
            profile_id=pid, primary_category=raw["primary_category"], profile_type=raw["profile_type"],
            description=raw.get("description", ""), skills=tuple(raw["skills"]), interests=tuple(raw["interests"]),
            education_level=raw.get("education_level"), relevant_career_ids=tuple(relevant),
            relevance_explanation=raw["relevance_explanation"],
        ))
    _check(profiles, "no profiles found")
    return tuple(profiles)


def load_profiles(career_ids, path=None):
    path = Path(path) if path else DEFAULT_PROFILES_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationDataError(f"cannot read {path}: {exc}") from exc
    return parse_profiles(data, set(career_ids))
