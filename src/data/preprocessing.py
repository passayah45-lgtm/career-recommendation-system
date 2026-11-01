# Explicit, testable cleaning helpers for skill names
# The validator uses them only to check that aliases cannot collide; raw data must already be clean
# The engine will use them later to normalize learner input

import re
import unicodedata

SEPARATORS = re.compile(r"[/_\-]+")
NON_TOKEN = re.compile(r"[^a-z0-9 ]+")
SPACES = re.compile(r"\s+")


def fold_accents(text):
    # "Géologie" -> "Geologie": splits accented letters (NFKD) and drops the combining marks
    # Plain ASCII text is returned unchanged, so English matching is not affected
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def clean_skill_text(text):
    # Lowercase, fold accents, turn separators into spaces, drop other symbols, collapse spaces
    if text is None:
        return ""
    value = fold_accents(str(text).strip().lower())
    value = SEPARATORS.sub(" ", value)
    value = NON_TOKEN.sub("", value)
    return SPACES.sub(" ", value).strip()


def normalize_skill(text, aliases=None):
    # Returns the canonical skill name for free text, using the alias map when given
    # Order: exact alias (accents kept), then the cleaned and accent-folded text, then folded alias keys,
    # so "Géologie", "géologie" and "geologie" all reach the same alias
    aliases = aliases or {}
    raw = "" if text is None else str(text).strip().lower()
    if raw in aliases:
        return aliases[raw]
    cleaned = clean_skill_text(text)
    if cleaned in aliases:
        return aliases[cleaned]
    for alias, target in aliases.items():
        if clean_skill_text(alias) == cleaned and cleaned:
            return target
    return cleaned


def normalize_skill_list(values, aliases=None):
    # Normalizes a list of skills, drops empties and keeps first-seen order
    seen = []
    for v in values or []:
        skill = normalize_skill(v, aliases)
        if skill and skill not in seen:
            seen.append(skill)
    return seen
