# Interest picker helpers (Phase A interface): grouping, search, duplicates, counter and soft warning

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


def test_search_never_drops_a_selected_interest():
    chosen = ["writing and editing"]
    options = ip.picker_options("zzzz", chosen)
    assert options == chosen
    options = ip.picker_options("mine", chosen)
    assert "writing and editing" in options and "working outdoors and with the natural environment" in options


def test_duplicates_and_unknown_values_are_removed():
    assert ip.unique_known(["writing and editing", "writing and editing", "analysis", "x"]) == ["writing and editing"]


def test_search_caption_grammar():
    assert ip.search_caption(1, " mine ") == '1 interest matches "mine". Clear the search to see all 23.'
    assert ip.search_caption(0, "zz").startswith("0 interests match")


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
    fake = {ip.PICKER_KEY: ["writing and editing"], ip.SEARCH_KEY: "mine"}
    monkeypatch.setattr(st, "session_state", fake)
    monkeypatch.setattr(state, "set_progress", lambda roadmaps: None)
    state.replace_session({"interests": ["teaching and training others"]}, {})
    assert ip.PICKER_KEY not in fake and ip.SEARCH_KEY not in fake
    fake.update({ip.PICKER_KEY: ["writing and editing"]})
    state.reset_assessment()
    assert ip.PICKER_KEY not in fake


# ---------- Mobile readability styles (scoped to the interest picker) ----------

STYLES = (ip.__file__.rsplit("/", 1)[0] + "/styles.css")


def _picker_css():
    css = open(STYLES, encoding="utf-8").read()
    return css[css.index("/* Interest picker readability"):]


def test_mobile_styles_target_only_the_interest_picker():
    css = _picker_css()
    selectors = [line.strip() for line in css.splitlines() if line.strip().endswith("{") and "@media" not in line]
    assert selectors
    for sel in selectors:
        assert (f".st-key-{ip.PICKER_KEY}" in sel or f'aria-label="{ip.PICKER_LABEL}"' in sel
                or ".st-key-card_selected_interests" in sel), sel
    # The skills dropdown keeps Streamlit's default style: no rule names it or styles every listbox
    assert "Skills you already have" not in css
    assert not any(sel.startswith('[role="listbox"] ') for sel in selectors)


def test_chips_wrap_and_dropdown_options_fit_two_lines_on_phones():
    css = _picker_css()
    assert '[aria-label="Selected values"] > span > span' in css and "text-overflow: clip" in css
    phone = css[css.index("@media (max-width: 640px)"):]
    assert f'aria-label="{ip.PICKER_LABEL}"' in phone and "-webkit-line-clamp: 2" in phone
    assert "white-space: normal" in phone


def test_full_names_stay_available_to_assistive_technology():
    # Chips are named by their option label, which keeps the exact interest name after the group word
    for key in ip.ordered_keys():
        assert ip.option_label(key).endswith(next(t.label for t in INTEREST_TERMS if t.key == key))
