# Explicit, testable cleaning helpers for skill names
# The validator never calls these: raw data must already be clean
# The engine will use them later to normalize learner input

import re

SEPARATORS = re.compile(r"[/_\-]+")
NON_TOKEN = re.compile(r"[^a-z0-9 ]+")
SPACES = re.compile(r"\s+")


def clean_skill_text(text):
    # Lowercase, turn separators into spaces, drop other symbols, collapse spaces
    if text is None:
        return ""
    value = str(text).strip().lower()
    value = SEPARATORS.sub(" ", value)
    value = NON_TOKEN.sub("", value)
    return SPACES.sub(" ", value).strip()


def normalize_skill(text, aliases=None):
    # Returns the canonical skill name for free text, using the alias map when given
    aliases = aliases or {}
    raw = "" if text is None else str(text).strip().lower()
    if raw in aliases:
        return aliases[raw]
    cleaned = clean_skill_text(text)
    return aliases.get(cleaned, cleaned)


def normalize_skill_list(values, aliases=None):
    # Normalizes a list of skills, drops empties and keeps first-seen order
    seen = []
    for v in values or []:
        skill = normalize_skill(v, aliases)
        if skill and skill not in seen:
            seen.append(skill)
    return seen
