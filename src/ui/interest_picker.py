# Compact interest picker for the assessment page: one searchable dropdown, chips, live counter and descriptions
# Display only: it saves the same interest keys as before and never changes the taxonomy or the score
# Students can also type their own interests; those are saved as text and never scored (like unmatched custom skills)

import streamlit as st

from src.data.interest_taxonomy import (
    CURRENT_INTERESTS, INTEREST_TERMS, RIASEC_DESCRIPTIONS, RIASEC_ORDER, SOFT_SELECTION_LIMIT, TERMS_BY_KEY,
    resolve_interest,
)
from src.data.preprocessing import clean_skill_text
from src.ui.text import plain_markdown

PICKER_KEY = "interest_picker"
# styles.css targets the open dropdown through this label, so both must change together
PICKER_LABEL = "Kinds of work you enjoy"
# Since the exchange of 4 November 2026 (owner decision) this list is shown in the Skills section under this label
SKILLS_SECTION_LABEL = "Skills you already have"
# The separate description search box was replaced by suggestions under custom interests (owner decision, 3 Nov 2026)
MAX_SUGGESTIONS = 3
# Plain group words shown to students; the RIASEC names stay in the data and in the browse list
GROUP_WORDS = {
    "Realistic": "Practical", "Investigative": "Analytical", "Artistic": "Creative",
    "Social": "People", "Enterprising": "Leading", "Conventional": "Organised",
}
# Select all would give every career the full interest score, so the picker never offers it
SELECT_ALL = False
FILTER_MODE = "contains"


def ordered_keys():
    # All 23 keys, grouped in RIASEC order and in the second review's order inside each group
    return [t.key for g in RIASEC_ORDER for t in INTEREST_TERMS if t.riasec == g]


def option_label(key):
    # Official interests show their group word; a student's own interest is shown exactly as typed
    term = TERMS_BY_KEY.get(key)
    return f"{GROUP_WORDS[term.riasec]} · {term.label}" if term else key


def _search_text(term):
    # Everything a student might type: name, group words, explanation, example, related skill, draft French name
    parts = (term.label, term.riasec, GROUP_WORDS[term.riasec], term.explanation, term.example,
             term.related_skill, term.label_fr_draft)
    return clean_skill_text(" ".join(parts))


def search_keys(query, keys=None):
    # Keys whose name or description contains every word of the query; an empty query keeps all
    keys = list(keys) if keys is not None else ordered_keys()
    words = clean_skill_text(query).split()
    if not words:
        return keys
    return [k for k in keys if all(w in _search_text(TERMS_BY_KEY[k]) for w in words)]


def normalize_custom(text):
    # One consistent form for a typed interest: trimmed, single spaces, original capitalisation kept
    return " ".join(str(text).split())


def split_selection(values):
    # Returns (official keys, own interests); typed text that names an official interest becomes that interest
    # Official names, stored forms, draft French names and old names with a direct match count as official
    # Duplicates are dropped, ignoring capitalisation and extra spaces
    official, custom, seen_custom = [], [], set()
    for value in values or ():
        if value in TERMS_BY_KEY:
            key = value
        else:
            text = normalize_custom(value)
            if not text:
                continue
            resolved = resolve_interest(text, CURRENT_INTERESTS)
            key = resolved.key if resolved.status in ("recognized", "migrated") else None
            if key is None:
                fold = clean_skill_text(text) or text.casefold()
                if fold not in seen_custom:
                    seen_custom.add(fold)
                    custom.append(text)
                continue
        if key not in official:
            official.append(key)
    return official, custom


SUFFIXES = ("ship", "ment", "ing", "ers", "ies", "er", "al", "s")


def _stem(word):
    # Drops up to two common English endings so "leadership" meets "leading" and "development" meets "developing"
    for _ in range(2):
        for suffix in SUFFIXES:
            if word.endswith(suffix) and len(word) - len(suffix) >= 4:
                word = word[:-len(suffix)]
                break
    return word[:5]


def suggestions(text, exclude=()):
    # Official interests whose name or description shares words with a typed interest, best match first
    stems = [_stem(w) for w in clean_skill_text(text).split() if len(w) >= 4]
    if not stems:
        return []
    scored = []
    for i, key in enumerate(ordered_keys()):
        if key in exclude:
            continue
        hits = sum(stem in _search_text(TERMS_BY_KEY[key]) for stem in stems)
        if hits:
            scored.append((-hits, i, key))
    return [key for _, _, key in sorted(scored)[:MAX_SUGGESTIONS]]


def custom_note(custom, as_skills=False):
    # Typed text is escaped so Markdown or HTML in it shows as plain characters, never as a link or image
    names = ", ".join(f'"{plain_markdown(c)}"' for c in custom)
    if as_skills:
        return (f"Skills you typed: {names}. They are saved as skills and count toward the skill part of the "
                "score when they are in the dataset. Short names such as ML are recognized. Skills that are not in "
                "the dataset are listed back to you and are not scored.")
    return (f"Your own interests: {names}. They are saved with your assessment but do not change the score, "
            "because no career lists them.")


def _tidy_selection():
    # Runs when the dropdown changes: maps typed official names, trims spaces and removes duplicates
    official, custom = split_selection(st.session_state.get(PICKER_KEY, []))
    st.session_state[PICKER_KEY] = official + custom


def _add_official(key):
    current = list(st.session_state.get(PICKER_KEY, []))
    if key not in current:
        st.session_state[PICKER_KEY] = current + [key]


def unique_known(keys):
    # Keeps the first occurrence of each known key; the dropdown already prevents duplicates
    seen, out = set(), []
    for k in keys:
        if k in TERMS_BY_KEY and k not in seen:
            seen.add(k)
            out.append(k)
    return out


def counter_text(n):
    noun = "interest" if n == 1 else "interests"
    return f"{n} {noun} selected. Choosing up to {SOFT_SELECTION_LIMIT} you enjoy most works best."


def soft_warning(n):
    if n <= SOFT_SELECTION_LIMIT:
        return None
    return (f"You chose {n} interests. More than {SOFT_SELECTION_LIMIT} gives points to many careers without "
            f"narrowing your results. All of them will still be saved and scored.")


def render_interest_picker(saved_keys, saved_custom=(), as_skills=False):
    # Returns official keys followed by the student's own entries; outside any form, so everything updates at once
    # as_skills=True: the list is shown in the Skills section (exchange of 4 November 2026); choices from the list
    # are still saved and scored as interests, and text the student types here is saved as a skill
    if PICKER_KEY not in st.session_state:
        official, custom = split_selection(list(saved_keys) + list(saved_custom))
        st.session_state[PICKER_KEY] = official + custom

    if as_skills:
        help_text = ("This list shows the 23 interests (kinds of work), grouped as Practical, Analytical, Creative, "
                     "People, Leading and Organised. Each choice counts as an interest. To add a skill, type it and "
                     "press Enter, or use the Other skills box. Remove a choice with the x on its chip.")
        placeholder = "Choose an interest or type a skill, for example data or python"
    else:
        help_text = ("Options are grouped: Practical, Analytical, Creative, People, Leading and Organised. "
                     "Not in the list? Type your own interest and press Enter. Your own interests are saved but not "
                     "scored. Remove a choice with the x on its chip.")
        placeholder = "Choose or type, for example data, health, business"
    selection = st.multiselect(
        SKILLS_SECTION_LABEL if as_skills else PICKER_LABEL,
        options=ordered_keys(),
        format_func=option_label,
        key=PICKER_KEY,
        placeholder=placeholder,
        filter_mode=FILTER_MODE,
        select_all=SELECT_ALL,
        accept_new_options=True,
        wrap=True,
        on_change=_tidy_selection,
        help=help_text,
    )
    picked, custom = split_selection(selection)

    counter = counter_text(len(picked))
    if as_skills:
        counter = counter.replace(" selected.", " selected from the list. They count as interests.", 1)
    if custom:
        counter += (f" Plus {len(custom)} {'skill' if len(custom) == 1 else 'skills'} you typed." if as_skills
                    else f" Plus {len(custom)} of your own, saved but not scored.")
    st.caption(counter)
    warning = soft_warning(len(picked))
    if warning:
        st.warning(warning, icon=":material/tune:")

    if custom:
        with st.container(border=True, key="card_own_interests"):
            st.markdown(custom_note(custom, as_skills))
            for i, text in enumerate(custom):
                close = suggestions(text, exclude=picked)
                if not close:
                    continue
                scored = " (they count as interests)" if as_skills else " (these are scored)"
                st.caption(f'Official interests with similar words to "{plain_markdown(text)}"{scored}:')
                with st.container(horizontal=True, gap="small", key=f"suggestions_{i}"):
                    for key in close:
                        st.button(f"Add {TERMS_BY_KEY[key].label}", key=f"suggest_{i}_{key}",
                                  icon=":material/add:", on_click=_add_official, args=(key,))

    if picked:
        with st.container(border=True, key="card_selected_interests"):
            st.markdown("**Interests chosen from this list**" if as_skills else "**Your selected interests**")
            for k in picked:
                t = TERMS_BY_KEY[k]
                st.markdown(f"**{t.label}** :gray[({GROUP_WORDS[t.riasec]})]  \n"
                            f"{t.explanation}. Example: {t.example}.  \n"
                            f":gray[Related skill, not the same thing: {t.related_skill}]")

    with st.expander("Browse all 23 interests with descriptions"):
        for g in RIASEC_ORDER:
            st.markdown(f"**{GROUP_WORDS[g]}** :gray[({g}): {RIASEC_DESCRIPTIONS[g]}]")
            st.markdown("\n".join(f"- **{t.label}**: {t.explanation}. Example: {t.example}."
                                  for t in INTEREST_TERMS if t.riasec == g))
    return picked + custom
