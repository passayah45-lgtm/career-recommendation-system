# Export and import of one learner's session as a JSON file the learner keeps
# The app never stores this file; the learner downloads it and may upload it again later

import json

from src.services.feedback import FEEDBACK_VALUES
from src.services.recommendations import profile_from_input
from src.services.roadmap import clean_progress

FORMAT = "career-recommendation-session"
# Version 2 adds roadmap progress; version 1 files still load
VERSION = 2
SUPPORTED_VERSIONS = (1, 2)
MAX_BYTES = 100_000
PROFILE_FIELDS = ("skills", "interests", "education_level", "experience_years")


class SessionFileError(ValueError):
    pass


def export_session(profile, feedback, roadmaps=None):
    # Returns UTF-8 JSON bytes with the raw answers, the feedback and the roadmap progress
    data = {
        "format": FORMAT,
        "version": VERSION,
        "profile": {k: profile[k] for k in PROFILE_FIELDS if profile and k in profile},
        "feedback": dict(sorted((feedback or {}).items())),
        "roadmaps": {cid: dict(sorted(steps.items())) for cid, steps in sorted((roadmaps or {}).items())},
    }
    return json.dumps(data, indent=2).encode("utf-8")


def import_session(raw, catalog):
    # Validates an uploaded file and returns (profile, feedback); raises SessionFileError with a plain message
    profile, feedback, _, _ = import_session_data(raw, catalog)
    return profile, feedback


def import_session_data(raw, catalog):
    # Returns (profile, feedback, roadmap progress, issues); bad roadmap entries are dropped and listed in issues
    if raw is None or len(raw) == 0:
        raise SessionFileError("the file is empty")
    if len(raw) > MAX_BYTES:
        raise SessionFileError("the file is too large to be a session file")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise SessionFileError("the file is not valid JSON") from None
    if not isinstance(data, dict) or data.get("format") != FORMAT:
        raise SessionFileError("this is not a session file from this app")
    if data.get("version") not in SUPPORTED_VERSIONS or isinstance(data.get("version"), bool):
        raise SessionFileError("this session file version is not supported")
    profile = data.get("profile")
    if not isinstance(profile, dict) or set(profile) - set(PROFILE_FIELDS):
        raise SessionFileError("the saved answers have an unexpected format")
    try:
        profile_from_input(profile, catalog)
    except ValueError as exc:
        raise SessionFileError(f"the saved answers are not valid ({exc})") from None
    feedback = data.get("feedback", {})
    if not isinstance(feedback, dict):
        raise SessionFileError("the saved feedback has an unexpected format")
    known = {c.career_id for c in catalog.careers}
    for cid, value in feedback.items():
        if cid not in known or isinstance(value, bool) or value not in FEEDBACK_VALUES:
            raise SessionFileError("the saved feedback refers to an unknown career or value")
    roadmaps, issues = clean_progress(data.get("roadmaps", {}), catalog)
    return profile, dict(feedback), roadmaps, issues
