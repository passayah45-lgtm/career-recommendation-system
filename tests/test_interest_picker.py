# Interest picker helpers (Phase A interface): grouping, search, duplicates, counter and soft warning

import re

import pytest

from src.data.interest_taxonomy import CURRENT_INTERESTS, INTEREST_TERMS, RIASEC_ORDER, SOFT_SELECTION_LIMIT
from src.services.catalog import load_catalog
from src.services.recommendations import recommend
from src.ui import interest_picker as ip


def test_options_are_all_23_keys_grouped_in_riasec_order():
    keys = ip.ordered_keys()
    assert sorted(keys) == sorted(CURRENT_INTERESTS) and len(set(keys)) == 23
    groups = [next(t.riasec for t in INTEREST_TERMS if t.key == k) for k in keys]
    assert groups == sorted(groups, key=RIASEC_ORDER.index)


def test_option_labels_keep_the_exact_interest_names():
    for term in INTEREST_TERMS:
        assert ip.option_label(term.key) == f"{ip.GROUP_WORDS[term.riasec]} · {term.label}"
    assert set(ip.GROUP_WORDS) == set(RIASEC_ORDER) and len(set(ip.GROUP_WORDS.values())) == 6


def test_select_all_is_disabled():
    assert ip.SELECT_ALL is False and ip.FILTER_MODE == "contains"


@pytest.mark.parametrize("query,expected", [
    ("mine", "working outdoors and with the natural environment"),
    ("patients", "caring for peoples health"),
    ("budget", "managing money and financial information"),
    ("Python", "writing software and building apps"),
    ("village", "working with communities"),
    ("Organised", "keeping information records and procedures in order"),
    ("santé", "caring for peoples health"),
])
def test_search_matches_names_and_descriptions(query, expected):
    assert expected in ip.search_keys(query)


def test_search_needs_every_word_and_empty_query_keeps_all():
    assert ip.search_keys("") == ip.ordered_keys() and ip.search_keys("   ") == ip.ordered_keys()
    assert ip.search_keys("money budget") == ["managing money and financial information"]
    assert ip.search_keys("zzzz") == []


def test_suggestions_come_from_descriptions_and_skip_chosen_interests():
    # Replaces the separate search box (removed 3 November 2026, owner decision)
    assert ip.suggestions("mine")[0] == "working outdoors and with the natural environment"
    assert "caring for peoples health" in ip.suggestions("patients")
    assert "writing software and building apps" in ip.suggestions("code")
    assert "working with communities" in ip.suggestions("Community leadership")
    assert "leading people and projects" in ip.suggestions("Community leadership")
    assert "running and growing a business" in ip.suggestions("Rural entrepreneurship")
    assert "working with communities" not in ip.suggestions("Community leadership", exclude=["working with communities"])
    assert ip.suggestions("zzzz") == [] and ip.suggestions("a an") == []
    assert len(ip.suggestions("working with people")) <= ip.MAX_SUGGESTIONS


def test_duplicates_and_unknown_values_are_removed():
    assert ip.unique_known(["writing and editing", "writing and editing", "analysis", "x"]) == ["writing and editing"]


def test_own_interest_note_explains_they_are_not_scored():
    note = ip.custom_note(["Agricultural development", "Rural entrepreneurship"])
    assert '"Agricultural development"' in note and "do not change the score" in note


def test_counter_and_soft_warning():
    assert ip.counter_text(1).startswith("1 interest selected")
    assert ip.counter_text(3).startswith("3 interests selected")
    assert ip.soft_warning(SOFT_SELECTION_LIMIT) is None
    assert "You chose 6 interests" in ip.soft_warning(SOFT_SELECTION_LIMIT + 1)
    assert "still be saved and scored" in ip.soft_warning(9)


def test_interest_scores_follow_the_selection_not_its_order():
    catalog = load_catalog()
    chosen = ip.ordered_keys()[:4]
    a = recommend({"interests": chosen}, catalog, top_k=None)["recommendations"]
    b = recommend({"interests": list(reversed(chosen)) + chosen[:1]}, catalog, top_k=None)["recommendations"]
    assert [(r["career_id"], r["score"], r["score_components"]["interests"]["value"]) for r in a] == \
        [(r["career_id"], r["score"], r["score_components"]["interests"]["value"]) for r in b]


def test_selecting_everything_is_still_scored_by_the_unchanged_formula():
    # Without Select all a student can still pick all 23 by hand; the formula itself is unchanged by design
    catalog = load_catalog()
    recs = recommend({"interests": ip.ordered_keys()}, catalog, top_k=None)["recommendations"]
    assert all(r["score_components"]["interests"]["value"] == 1.0 for r in recs)
    assert all(r["score_components"]["interests"]["weight"] == 0.25 for r in recs)


def test_restoring_or_resetting_a_session_reseeds_the_picker(monkeypatch):
    import streamlit as st
    from src.ui import state
    from src.ui.skill_picker import SKILL_PICKER_KEY
    fake = {ip.PICKER_KEY: ["writing and editing"], SKILL_PICKER_KEY: ["python"]}
    monkeypatch.setattr(st, "session_state", fake)
    monkeypatch.setattr(state, "set_progress", lambda roadmaps: None)
    state.replace_session({"interests": ["teaching and training others"]}, {})
    assert ip.PICKER_KEY not in fake and SKILL_PICKER_KEY not in fake
    fake.update({ip.PICKER_KEY: ["writing and editing"]})
    state.reset_assessment()
    assert ip.PICKER_KEY not in fake


# ---------- Mobile readability styles (scoped to the interest and skill pickers) ----------

STYLES = (ip.__file__.rsplit("/", 1)[0] + "/styles.css")


def _picker_css():
    css = open(STYLES, encoding="utf-8").read()
    return css[css.index("/* Interest and skill picker readability"):]


def _selectors(css):
    # Every selector of every rule, split on commas, ignoring comments and @media lines
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = []
    for head in re.findall(r"([^{}]+)\{", css):
        head = head.strip()
        if head.startswith("@media"):
            continue
        out += [part.strip() for part in head.split(",") if part.strip()]
    return out


def test_mobile_styles_target_only_the_two_pickers():
    # Since 3 November 2026 the skills dropdown uses the same picker design (owner decision)
    from src.ui.skill_picker import SKILL_PICKER_KEY, SKILL_PICKER_LABEL
    selectors = _selectors(_picker_css())
    assert selectors
    allowed = (f".st-key-{ip.PICKER_KEY}", f'aria-label="{ip.PICKER_LABEL}"', f".st-key-{SKILL_PICKER_KEY}",
               f'aria-label="{SKILL_PICKER_LABEL}"', ".st-key-card_selected_interests", ".st-key-card_own_interests")
    for sel in selectors:
        assert any(a in sel for a in allowed), sel
    # No rule styles every dropdown in the app
    assert not any(sel.startswith('[role="listbox"] ') or sel.startswith("[role=\"option\"]") for sel in selectors)
    # Both pickers get the same chip and phone rules
    assert sum(f".st-key-{SKILL_PICKER_KEY}" in sel for sel in selectors) == \
        sum(f".st-key-{ip.PICKER_KEY}" in sel for sel in selectors)


def test_chips_wrap_and_dropdown_options_fit_two_lines_on_phones():
    css = _picker_css()
    assert '[aria-label="Selected values"] > span > span' in css and "text-overflow: clip" in css
    phone = css[css.index("@media (max-width: 640px)"):]
    assert f'aria-label="{ip.PICKER_LABEL}"' in phone and "-webkit-line-clamp: 2" in phone
    assert 'aria-label="Skills you already have"' in phone
    assert "white-space: normal" in phone


def test_full_names_stay_available_to_assistive_technology():
    # Chips are named by their option label, which keeps the exact interest name after the group word
    for key in ip.ordered_keys():
        assert ip.option_label(key).endswith(next(t.label for t in INTEREST_TERMS if t.key == key))


# ---------- Students' own interests (3 November 2026) ----------

def test_own_interests_are_kept_trimmed_and_deduplicated():
    official, custom = ip.split_selection(
        ["  Agricultural   development ", "agricultural development", "Community leadership",
         "Rural entrepreneurship", "", "   "])
    assert official == []
    assert custom == ["Agricultural development", "Community leadership", "Rural entrepreneurship"]


def test_typed_official_names_become_official_interests():
    official, custom = ip.split_selection(
        ["Managing money and financial information", "caring for peoples health", "Gérer l'argent et les informations "
         "financières", "helping people", "writing and editing"])
    assert official == ["managing money and financial information", "caring for peoples health",
                        "helping and advising people", "writing and editing"]
    assert custom == []


def test_retired_old_names_stay_as_own_interests_and_are_never_guessed():
    official, custom = ip.split_selection(["technology", "writing and editing"])
    assert official == ["writing and editing"] and custom == ["technology"]


def test_own_interests_never_change_any_score():
    catalog = load_catalog()
    base = {"skills": ["python"], "interests": ["analysing data and information"], "education_level": 3}
    with_own = {**base, "interests": base["interests"] + ["Agricultural development", "Rural entrepreneurship"]}
    a = recommend(base, catalog, top_k=None)
    b = recommend(with_own, catalog, top_k=None)
    assert [(r["career_id"], r["score"]) for r in a["recommendations"]] == \
        [(r["career_id"], r["score"]) for r in b["recommendations"]]
    assert b["profile"]["report"]["unknown_interests"] == ["Agricultural development", "Rural entrepreneurship"]
    assert any("not scored" in w and "Agricultural development" in w for w in b["warnings"])


def test_suggestion_buttons_wrap_and_only_inside_the_own_interest_card():
    css = _picker_css()
    rules = [s for s in _selectors(css) if "st-key-suggestions_" in s]
    assert rules and all(s.startswith(".st-key-card_own_interests ") for s in rules)
    block = css[css.index("Suggestion buttons under own interests"):css.index("@media (max-width: 640px)")]
    assert "white-space: normal" in block and "text-overflow: clip" in block and "height: auto" in block
