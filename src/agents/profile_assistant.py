# Career Assessment Assistant: suggests official skills and interests from a student's own description
# Pure Python and deterministic: no Streamlit, no network, no language model, no change to any profile
# Every suggestion is an existing catalogue entry; nothing here is added to the catalogue or to a profile
# The student reviews the suggestions; only confirmed selections ever reach the existing assessment logic

import re
from dataclasses import asdict, dataclass, field

from src.data.interest_taxonomy import (
    CURRENT_TAXONOMY, INTEREST_TERMS, LEGACY_TO_CURRENT, RETIRED_LEGACY, TERMS_BY_KEY,
)
from src.data.preprocessing import clean_skill_text

# Longer text is cut to this many characters before matching, and the result says so
MAX_TEXT_CHARS = 5000
# Punctuation and line breaks end a segment; catalogue names never cross a segment
SEGMENT_SPLIT = re.compile(r"[.,;:!?()\[\]\n\r]+")
# Words that join clauses; a clause is the unit reported as unmatched
CLAUSE_WORDS = frozenset({"and", "or", "also", "but", "plus", "et", "ou", "mais", "aussi"})
# Words that carry no skill or interest on their own, in English and French
FILLER_WORDS = frozenset("""
i im me my mine we our you a an the this that these those to of in on at for from by with about into as is am are
was were be been being have has had do does did can could will would should very really quite also just so too
enjoy enjoyed like liked love loved prefer interested interest interests passionate keen good great some much many
skill skills experience experienced knowledge know knowing learn learning learned studied study studying use using
used doing done make making work working worked job jobs field fields area areas things thing stuff other others
people person student students when while where which who what how want wish would like lot lots well
je j me moi mon ma mes nous notre vous le la les l un une des de du d en dans pour par avec sur au aux est suis
ai avons aime adore aimer bien beaucoup tres travail travailler travaille faire fait chose choses autres autre
veux voudrais souhaite peux sais
""".split())
# Words too common in interest names to count as evidence by themselves
GENERIC_STEMS = frozenset({"work", "with", "and", "other", "peopl", "infor", "syste", "kind", "thing"})
SUFFIXES = ("ations", "ation", "ments", "ment", "ings", "ing", "ical", "ers", "ies", "ed", "es", "al", "s")
MIN_OVERLAP = 2


def _stem(word):
    # Drops up to two common English endings, then keeps 5 characters: "mathematical" and "mathematics" meet
    for _ in range(2):
        for suffix in SUFFIXES:
            if word.endswith(suffix) and len(word) - len(suffix) >= 4:
                word = word[:-len(suffix)]
                break
    return word[:5]


@dataclass(frozen=True)
class Suggestion:
    kind: str           # "skill" or "interest"
    entry: str          # official catalogue form: canonical skill name or stored interest key
    label: str          # what to show the student
    phrase: str         # the student's words that triggered the match
    match: str          # how it matched, see MATCH_TYPES
    confidence: str     # "high", "medium" or "low"
    explanation: str


@dataclass
class AssistantResult:
    suggested_skills: list = field(default_factory=list)
    suggested_interests: list = field(default_factory=list)
    unmatched_phrases: list = field(default_factory=list)
    match_details: list = field(default_factory=list)
    text_truncated: bool = False

    def to_dict(self):
        return asdict(self)

    def profile_selection(self):
        # The official entries in the shape recommend() accepts; for use only after the student confirms them
        return {"skills": [s.entry for s in self.suggested_skills],
                "interests": [s.entry for s in self.suggested_interests]}


MATCH_TYPES = {
    "skill_name": ("high", "The words match the catalogue skill name."),
    "skill_alias": ("high", "The words match a recognised short or alternative name for this skill."),
    "interest_label": ("high", "The words match the full name of this interest."),
    "interest_french_label": ("high", "The words match the French draft name of this interest."),
    "interest_former_name": ("medium", "The words match a former interest name that now means this interest."),
    "interest_word_overlap": ("low", "Several key words of this interest's name appear in the same phrase."),
}


def _skill_lookup(catalog):
    # {cleaned words: canonical skill} from catalogue names and from aliases whose target is a catalogue skill
    known = catalog.known_skills
    lookup = {clean_skill_text(s): (s, "skill_name") for s in known}
    for alias, target in catalog.aliases.items():
        key = clean_skill_text(alias)
        if target in known and key and key not in lookup:
            lookup[key] = (target, "skill_alias")
    return lookup


def _interest_tables(catalog):
    # Interest triggers from the official definitions; only the current 23-term list has labels and former names
    vocabulary = set(catalog.interests)
    if catalog.interest_taxonomy != CURRENT_TAXONOMY:
        return {k: (k, "interest_label") for k in vocabulary}, {}, {}
    exact = {}
    for term in INTEREST_TERMS:
        if term.key in vocabulary:
            exact[term.key] = (term.key, "interest_label")
            exact.setdefault(clean_skill_text(term.label_fr_draft), (term.key, "interest_french_label"))
    former = {clean_skill_text(old): new for old, new in LEGACY_TO_CURRENT.items() if new in vocabulary}
    overlap = {}
    for term in INTEREST_TERMS:
        if term.key not in vocabulary:
            continue
        for label in (term.label, term.label_fr_draft):
            stems = {_stem(w) for w in clean_skill_text(label).split() if w not in FILLER_WORDS and len(w) >= 3}
            overlap.setdefault(term.key, []).append(stems - GENERIC_STEMS)
    return exact, former, overlap


def _find_ngrams(tokens, lookup, used, max_len):
    # Greedy longest match left to right; returns [(start, end, value)] and marks the tokens it used
    found, i = [], 0
    while i < len(tokens):
        hit = None
        for n in range(min(max_len, len(tokens) - i), 0, -1):
            if any(used[i:i + n]):
                continue
            key = " ".join(tokens[i:i + n])
            if key in lookup:
                hit = (i, i + n, lookup[key])
                break
        if hit:
            found.append(hit)
            for k in range(hit[0], hit[1]):
                used[k] = True
            i = hit[1]
        else:
            i += 1
    return found


def _clauses(tokens):
    # Splits a segment's tokens on joining words, keeping each clause's token positions
    clauses, current = [], []
    for i, tok in enumerate(tokens):
        if tok in CLAUSE_WORDS:
            if current:
                clauses.append(current)
            current = []
        else:
            current.append(i)
    if current:
        clauses.append(current)
    return clauses


def suggest_profile(text, catalog):
    # Returns an AssistantResult; it never changes the catalogue, the text's owner or any saved profile
    result = AssistantResult()
    raw = "" if text is None else str(text)
    if len(raw) > MAX_TEXT_CHARS:
        raw, result.text_truncated = raw[:MAX_TEXT_CHARS], True
    skills = _skill_lookup(catalog)
    max_skill = max((len(k.split()) for k in skills), default=1)
    exact, former, overlap = _interest_tables(catalog)
    max_interest = max((len(k.split()) for k in list(exact) + list(former)), default=1)
    retired = {clean_skill_text(k): v for k, v in RETIRED_LEGACY.items()}
    seen = set()

    def record(kind, entry, label, phrase, match):
        confidence, explanation = MATCH_TYPES[match]
        suggestion = Suggestion(kind, entry, label, phrase, match, confidence, explanation)
        duplicate = (kind, entry) in seen
        result.match_details.append({**asdict(suggestion), "duplicate": duplicate})
        if not duplicate:
            seen.add((kind, entry))
            (result.suggested_skills if kind == "skill" else result.suggested_interests).append(suggestion)

    for segment in SEGMENT_SPLIT.split(raw):
        tokens = clean_skill_text(segment).split()
        if not tokens:
            continue
        used = [False] * len(tokens)
        matched = [False] * len(tokens)
        # 1. Catalogue skill names and aliases, longest first
        for start, end, (skill, how) in _find_ngrams(tokens, skills, used, max_skill):
            record("skill", skill, skill, " ".join(tokens[start:end]), how)
            for k in range(start, end):
                matched[k] = True
        # 2. Full interest names (English or French draft), then former interest names, on the unused words
        for start, end, (key, how) in _find_ngrams(tokens, exact, used, max_interest):
            record("interest", key, TERMS_BY_KEY[key].label if key in TERMS_BY_KEY else key,
                   " ".join(tokens[start:end]), how)
            for k in range(start, end):
                matched[k] = True
        stem_lookup = {" ".join(_stem(w) for w in old.split()): new for old, new in former.items()}
        stemmed = [_stem(t) for t in tokens]
        for start, end, key in _find_ngrams(stemmed, stem_lookup, used, max_interest):
            record("interest", key, TERMS_BY_KEY[key].label, " ".join(tokens[start:end]), "interest_former_name")
            for k in range(start, end):
                matched[k] = True
        # 3. Key words of an interest's name inside one segment (names themselves contain "and" or "et")
        free = [i for i in range(len(tokens)) if not used[i] and tokens[i] not in FILLER_WORDS and len(tokens[i]) >= 3]
        free_stems = {}
        for i in free:
            free_stems.setdefault(stemmed[i], i)
        for key, stem_sets in overlap.items():
            for stems in stem_sets:
                hits = sorted(free_stems[st] for st in stems if st in free_stems)
                if len(hits) >= MIN_OVERLAP:
                    record("interest", key, TERMS_BY_KEY[key].label, " ".join(tokens[i] for i in hits),
                           "interest_word_overlap")
                    for i in hits:
                        matched[i] = True
                    break
        # 4. Clauses with no match at all, or with a retired interest name, for the student to review
        for clause in _clauses(tokens):
            words = " ".join(tokens[i] for i in clause)
            note = next((v for k, v in retired.items() if re.search(rf"\b{re.escape(k)}\b", words)), None)
            leftover = [i for i in clause if not matched[i] and tokens[i] not in FILLER_WORDS and len(tokens[i]) >= 3]
            if note and not any(matched[i] for i in clause):
                result.unmatched_phrases.append({"phrase": words, "reason": f"A former interest name that {note}."})
            elif leftover and not any(matched[i] for i in clause):
                result.unmatched_phrases.append({"phrase": " ".join(tokens[i] for i in leftover),
                                                 "reason": "No catalogue skill or official interest matches these "
                                                           "words. Review them or add them yourself."})
    return result
