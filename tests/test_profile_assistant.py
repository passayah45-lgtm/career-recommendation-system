# Career Assessment Assistant (Phase 2): catalogue-only suggestions from a student's description
# The assistant never changes a profile, the catalogue or the scores; these tests keep it that way

import random
import string

import pytest

from src.agents.profile_assistant import MATCH_TYPES, MAX_TEXT_CHARS, AssistantResult, suggest_profile
from src.data.interest_taxonomy import INTEREST_TERMS, LEGACY_TO_CURRENT, TERMS_BY_KEY
from src.services.catalog import load_catalog
from src.services.recommendations import recommend

CATALOG = load_catalog()
EXAMPLE = ("I enjoy analysing data, solving mathematical problems, teaching people Python, "
           "and working with machine learning.")


def skills(result):
    return [s.entry for s in result.suggested_skills]


def interests(result):
    return [s.entry for s in result.suggested_interests]


def unmatched(result):
    return [u["phrase"] for u in result.unmatched_phrases]


def assert_only_catalogue_entries(result, catalog=CATALOG):
    assert set(skills(result)) <= catalog.known_skills
    assert set(interests(result)) <= set(catalog.interests)
    for detail in result.match_details:
        known = catalog.known_skills if detail["kind"] == "skill" else set(catalog.interests)
        assert detail["entry"] in known


# ---------- The example from the Phase 2 brief ----------

def test_brief_example_gives_skills_interests_and_explanations():
    result = suggest_profile(EXAMPLE, CATALOG)
    assert skills(result) == ["python", "machine learning"]
    assert interests(result) == ["analysing data and information", "working with numbers and calculations",
                                 "teaching and training others"]
    assert unmatched(result) == []
    for s in result.suggested_skills + result.suggested_interests:
        assert s.phrase and s.explanation and s.confidence in ("high", "medium", "low")
        assert (s.confidence, s.explanation) == MATCH_TYPES[s.match]
    assert result.suggested_interests[0].label == "Analysing data and information"


# ---------- Skills ----------

def test_exact_catalogue_skill_names_match_including_names_with_and():
    result = suggest_profile("I know SQL, project management and algorithms and data structures.", CATALOG)
    assert skills(result) == ["sql", "project management", "algorithms and data structures"]
    assert {s.match for s in result.suggested_skills} == {"skill_name"}


def test_existing_skill_aliases_are_recognised():
    result = suggest_profile("ML, K8s, CI/CD, MS Excel and pentesting", CATALOG)
    assert skills(result) == ["machine learning", "kubernetes", "ci cd", "excel", "penetration testing"]
    alias = {s.entry: s.match for s in result.suggested_skills}
    assert alias["machine learning"] == "skill_alias" and alias["kubernetes"] == "skill_alias"


def test_longest_name_wins_over_a_shorter_one_inside_it():
    result = suggest_profile("I studied engineering mathematics", CATALOG)
    assert skills(result) == ["engineering mathematics"]


def test_matching_ignores_case_and_accents():
    lower = suggest_profile("python, machine learning, geologie", CATALOG)
    upper = suggest_profile("PYTHON, Machine LEARNING, GÉOLOGIE", CATALOG)
    assert skills(lower) == skills(upper) == ["python", "machine learning", "geology"]


def test_duplicates_are_suggested_once_and_every_trigger_is_kept_in_the_details():
    result = suggest_profile("ML, ml, Machine Learning and machine-learning", CATALOG)
    assert skills(result) == ["machine learning"]
    details = [d for d in result.match_details if d["entry"] == "machine learning"]
    assert len(details) == 4 and [d["duplicate"] for d in details] == [False, True, True, True]


# ---------- Interests ----------

def test_full_interest_names_match_in_english_and_french():
    for term in INTEREST_TERMS:
        english = suggest_profile(f"I like {term.label.lower()}.", CATALOG)
        assert term.key in interests(english), term.label
        french = suggest_profile(f"J'aime {term.label_fr_draft}.", CATALOG)
        assert term.key in interests(french), term.label_fr_draft


def test_former_interest_names_point_to_their_current_interest():
    for old, new in LEGACY_TO_CURRENT.items():
        result = suggest_profile(f"I am interested in {old}.", CATALOG)
        assert new in interests(result), old
        match = next(s for s in result.suggested_interests if s.entry == new)
        assert match.match in ("interest_former_name", "interest_label", "interest_word_overlap")


def test_key_words_of_an_interest_name_in_one_sentence_suggest_it_with_low_confidence():
    result = suggest_profile("I enjoy keeping records in order.", CATALOG)
    key = "keeping information records and procedures in order"
    match = next(s for s in result.suggested_interests if s.entry == key)
    assert match.match == "interest_word_overlap" and match.confidence == "low"
    assert match.phrase == "keeping records order"


def test_one_generic_word_is_not_enough_for_an_interest():
    # "working" and "machine" alone must not suggest "Working with tools, machines and equipment"
    result = suggest_profile("I am working with machine learning.", CATALOG)
    assert interests(result) == [] and skills(result) == ["machine learning"]


def test_retired_former_names_are_reported_not_guessed():
    result = suggest_profile("Problem solving and technology", CATALOG)
    assert interests(result) == []
    reasons = {u["phrase"]: u["reason"] for u in result.unmatched_phrases}
    assert "problem solving" in reasons and "technology" in reasons
    assert "former interest name" in reasons["problem solving"]


# ---------- French and African-context terms the catalogue supports ----------

def test_french_and_ohada_terms_use_the_existing_aliases():
    result = suggest_profile("J'aime la géologie, la mécanique des roches et le droit OHADA. "
                             "Je veux enseigner et former les adultes.", CATALOG)
    assert skills(result) == ["geology", "rock mechanics", "ohada business law"]
    assert interests(result) == ["teaching and training others"]


# ---------- Empty, irrelevant and unknown input ----------

@pytest.mark.parametrize("text", [None, "", "   ", "\n\n", "...", "I like it."])
def test_empty_or_filler_only_input_gives_nothing(text):
    result = suggest_profile(text, CATALOG)
    assert result.to_dict() == AssistantResult().to_dict()


def test_irrelevant_and_unknown_words_are_reported_for_review():
    result = suggest_profile("I like football, cooking and quantum origami.", CATALOG)
    assert skills(result) == [] and interests(result) == []
    assert unmatched(result) == ["football", "cooking", "quantum origami"]
    assert all("Review them" in u["reason"] for u in result.unmatched_phrases)


def test_mixed_description_separates_skills_interests_and_unknown_words():
    result = suggest_profile("I use Python and SQL, I enjoy helping people and running a business, "
                             "and I also love farming.", CATALOG)
    assert skills(result) == ["python", "sql"]
    assert interests(result) == ["helping and advising people", "running and growing a business"]
    assert unmatched(result) == ["farming"]


def test_very_long_text_is_cut_and_says_so():
    result = suggest_profile("python " + "x" * (MAX_TEXT_CHARS + 100), CATALOG)
    assert result.text_truncated is True and skills(result) == ["python"]


# ---------- Never invents entries, always deterministic, never touches a profile ----------

def test_random_text_never_produces_an_entry_outside_the_catalogue():
    rng = random.Random(7)
    words = [w for t in INTEREST_TERMS for w in t.label.split()] + sorted(CATALOG.known_skills)[:40]
    words += ["".join(rng.choices(string.ascii_lowercase, k=rng.randint(2, 9))) for _ in range(200)]
    for _ in range(300):
        text = " ".join(rng.choices(words, k=rng.randint(1, 25))) + rng.choice([".", ",", " and ", ""])
        assert_only_catalogue_entries(suggest_profile(text, CATALOG))


def test_the_same_text_always_gives_the_same_result():
    first = suggest_profile(EXAMPLE, CATALOG).to_dict()
    assert all(suggest_profile(EXAMPLE, CATALOG).to_dict() == first for _ in range(5))


def test_the_catalogue_and_the_input_are_not_changed():
    before = (CATALOG.known_skills, dict(CATALOG.aliases), CATALOG.interests, len(TERMS_BY_KEY))
    text = EXAMPLE
    suggest_profile(text, CATALOG)
    assert (CATALOG.known_skills, dict(CATALOG.aliases), CATALOG.interests, len(TERMS_BY_KEY)) == before
    assert text == EXAMPLE


def test_legacy_catalogues_only_match_their_own_interest_words():
    from src.evaluation.snapshot import load_evaluation_catalog
    legacy = load_evaluation_catalog()
    result = suggest_profile("I enjoy analysis, teaching and python", legacy)
    assert_only_catalogue_entries(result, legacy)
    assert set(interests(result)) <= set(legacy.interests)


# ---------- Scoring equivalence ----------

def _ranking(profile):
    recs = recommend(profile, CATALOG, top_k=None)["recommendations"]
    return [(r["career_id"], r["score"], r["score_components"]) for r in recs]


@pytest.mark.parametrize("text", [
    EXAMPLE,
    "J'aime la géologie et le droit OHADA. Je veux enseigner et former les adultes.",
    "ML, K8s, SQL, helping people and running a business",
])
def test_confirmed_suggestions_score_exactly_like_the_same_manual_profile(text):
    selection = suggest_profile(text, CATALOG).profile_selection()
    # The same official entries chosen by hand, in a different order
    manual = {"skills": sorted(selection["skills"]), "interests": sorted(selection["interests"]),
              "education_level": 3}
    assisted = {**selection, "education_level": 3}
    assert selection["skills"] or selection["interests"]
    assert _ranking(assisted) == _ranking(manual)
