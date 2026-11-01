# Loads and validates the frozen profiles and graded labels of the independent 64-career evaluation (eval64_v1)
# Separate from src/evaluation/dataset.py, which serves the original 50-career study and is unchanged

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from src.data.validation import CATEGORIES

EVAL64_DIR = Path(__file__).resolve().parents[2] / "data" / "evaluation" / "catalog_v1.3.0"
PROFILES_FILE = "profiles.csv"
LABELS_FILE = "relevance_labels.csv"
MANIFEST_FILE = "evaluation_manifest.json"
CATALOG_FILES = ("careers.csv", "resources.csv", "skill_aliases.csv", "dataset_manifest.json")
FROZEN_FILES = CATALOG_FILES + (PROFILES_FILE, LABELS_FILE)

PROFILE_COLUMNS = ("profile_id", "primary_category", "profile_type", "learner_stage", "education_level",
                   "experience_years", "skills", "interests", "learning_goal", "description")
LABEL_COLUMNS = ("profile_id", "career_id", "relevance_label", "justification", "occupational_basis",
                 "reviewer", "confidence")
PROFILE_TYPES = ("strong_match", "incomplete_skills", "career_change", "transferable_skills", "mixed_interests",
                 "unfamiliar_vocabulary", "french_vocabulary", "interests_only", "minimal_input", "many_inputs",
                 "no_clear_fit", "lower_education")
LEARNER_STAGES = ("beginner", "intermediate", "advanced", "undergraduate", "masters", "professional")
GRADES = (0, 1, 2, 3)
CONFIDENCE = ("high", "medium", "low")
# Main binary threshold: grade 2 or 3 counts as relevant
DEFAULT_THRESHOLD = 2


class Eval64DataError(ValueError):
    pass


@dataclass(frozen=True)
class EvalProfile:
    profile_id: str
    primary_category: str
    profile_type: str
    learner_stage: str
    education_level: object
    experience_years: object
    skills: tuple
    interests: tuple
    learning_goal: str
    description: str

    def as_input(self):
        # The profile exactly as a learner would submit it; education is omitted when unknown
        data = {"skills": list(self.skills), "interests": list(self.interests)}
        if self.education_level is not None:
            data["education_level"] = self.education_level
        if self.experience_years is not None:
            data["experience_years"] = self.experience_years
        return data


def _read(path, columns):
    path = Path(path)
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            header = tuple(reader.fieldnames or ())
            rows = list(reader)
    except OSError as exc:
        raise Eval64DataError(f"cannot read {path}: {exc}") from exc
    if header != columns:
        raise Eval64DataError(f"{path.name}: columns must be {', '.join(columns)}")
    return rows


def _optional_int(value, field, pid, low, high):
    if value == "":
        return None
    if not value.isdigit() or not low <= int(value) <= high:
        raise Eval64DataError(f"{pid}: {field} must be blank or a whole number from {low} to {high}")
    return int(value)


def _split(value):
    return tuple(x.strip() for x in value.split("|") if x.strip())


def parse_profiles(rows):
    profiles, seen = [], set()
    for r in rows:
        pid = (r.get("profile_id") or "").strip()
        if not pid:
            raise Eval64DataError("every profile needs a profile_id")
        if pid in seen:
            raise Eval64DataError(f"{pid}: duplicate profile_id")
        seen.add(pid)
        for field in ("primary_category", "profile_type", "learner_stage", "learning_goal", "description"):
            if not (r.get(field) or "").strip():
                raise Eval64DataError(f"{pid}: {field} is required")
        if r["primary_category"] not in CATEGORIES:
            raise Eval64DataError(f"{pid}: unknown primary_category '{r['primary_category']}'")
        if r["profile_type"] not in PROFILE_TYPES:
            raise Eval64DataError(f"{pid}: unknown profile_type '{r['profile_type']}'")
        if r["learner_stage"] not in LEARNER_STAGES:
            raise Eval64DataError(f"{pid}: unknown learner_stage '{r['learner_stage']}'")
        skills, interests = _split(r["skills"]), _split(r["interests"])
        if not skills and not interests:
            raise Eval64DataError(f"{pid}: a profile needs at least one skill or interest")
        profiles.append(EvalProfile(
            profile_id=pid, primary_category=r["primary_category"], profile_type=r["profile_type"],
            learner_stage=r["learner_stage"],
            education_level=_optional_int(r["education_level"], "education_level", pid, 0, 4),
            experience_years=_optional_int(r["experience_years"], "experience_years", pid, 0, 60),
            skills=skills, interests=interests, learning_goal=r["learning_goal"], description=r["description"],
        ))
    if not profiles:
        raise Eval64DataError("no profiles found")
    return tuple(profiles)


def parse_labels(rows, profile_ids, career_ids):
    # Returns {profile_id: {career_id: grade}}; careers not listed for a profile are grade 0 by rule R8
    labels = {pid: {} for pid in profile_ids}
    for r in rows:
        pid, cid = (r.get("profile_id") or "").strip(), (r.get("career_id") or "").strip()
        if pid not in labels:
            raise Eval64DataError(f"label for unknown profile '{pid}'")
        if cid not in career_ids:
            raise Eval64DataError(f"{pid}: unknown career_id '{cid}'")
        if cid in labels[pid]:
            raise Eval64DataError(f"{pid}: duplicate label for {cid}")
        value = (r.get("relevance_label") or "").strip()
        if not value.isdigit() or int(value) not in GRADES:
            raise Eval64DataError(f"{pid} {cid}: relevance_label must be one of {GRADES}")
        for field in ("justification", "occupational_basis", "reviewer"):
            if not (r.get(field) or "").strip():
                raise Eval64DataError(f"{pid} {cid}: {field} is required")
        if r.get("confidence") not in CONFIDENCE:
            raise Eval64DataError(f"{pid} {cid}: confidence must be one of {CONFIDENCE}")
        labels[pid][cid] = int(value)
    return labels


def relevant_set(grades, threshold=DEFAULT_THRESHOLD):
    return {cid for cid, g in grades.items() if g >= threshold}


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_manifest(data_dir=EVAL64_DIR):
    return json.loads((Path(data_dir) / MANIFEST_FILE).read_text(encoding="utf-8"))


def verify_frozen(data_dir=EVAL64_DIR):
    # Files whose bytes differ from the SHA-256 values in the manifest
    expected = read_manifest(data_dir).get("sha256", {})
    return [name for name in FROZEN_FILES if expected.get(name) != sha256_of(Path(data_dir) / name)]


def load_eval64(career_ids, data_dir=EVAL64_DIR):
    data_dir = Path(data_dir)
    profiles = parse_profiles(_read(data_dir / PROFILES_FILE, PROFILE_COLUMNS))
    labels = parse_labels(_read(data_dir / LABELS_FILE, LABEL_COLUMNS), [p.profile_id for p in profiles],
                          set(career_ids))
    return profiles, labels
