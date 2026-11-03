# Compact skill picker for the assessment page: one grouped, searchable dropdown with chips and a live counter
# Display only: it saves the same catalogue skill names as before; typed skills still go through "Other skills"
# Since the exchange of 4 November 2026 (owner decision) this list is shown in the Interests section; choices from
# the list are still saved and scored as skills, and text a student types there is saved as an interest

from collections import defaultdict

import streamlit as st

from src.data.interest_taxonomy import TERMS_BY_KEY
from src.data.preprocessing import clean_skill_text
from src.data.validation import CATEGORIES

SKILL_PICKER_KEY = "skill_picker"
# styles.css targets the open dropdown through this label, so both must change together
SKILL_PICKER_LABEL = "Skills you already have"
# Label used when the list is shown in the Interests section; styles.css targets it as well
INTERESTS_SECTION_LABEL = "Kinds of work you enjoy"
# Skills used by careers in more than one field get this group; it is derived from the data, not invented
SEVERAL_FIELDS = "Several fields"
# Select all would mark all 144 skills as known and give every career full skill points, so it is never offered
SELECT_ALL = False
FILTER_MODE = "contains"
# Group words for official interests restored from older sessions into the Interests section
_INTEREST_GROUP_WORDS = {
    "Realistic": "Practical", "Investigative": "Analytical", "Artistic": "Creative",
    "Social": "People", "Enterprising": "Leading", "Conventional": "Organised",
}


def skill_groups(catalog):
    # {skill: group}: the career field that uses the skill, or "Several fields" when careers in two or more use it
    fields = defaultdict(set)
    for career in catalog.careers:
        for skill in career.required_skills + career.preferred_skills:
            fields[skill].add(career.category)
    return {skill: (next(iter(cats)) if len(cats) == 1 else SEVERAL_FIELDS) for skill, cats in fields.items()}


def group_order():
    return list(CATEGORIES) + [SEVERAL_FIELDS]


def ordered_skills(groups):
    # Every catalogue skill once, grouped by field in the catalogue's category order, alphabetical inside a group
    order = {g: i for i, g in enumerate(group_order())}
    return sorted(groups, key=lambda s: (order.get(groups[s], len(order)), s))


def skill_label(skill, groups):
    group = groups.get(skill)
    if group:
        return f"{group} · {skill}"
    term = TERMS_BY_KEY.get(skill)
    # An official interest saved by an older session keeps its readable name; typed text is shown as typed
    return f"{_INTEREST_GROUP_WORDS[term.riasec]} · {term.label}" if term else skill


def skill_counter_text(n):
    noun = "skill" if n == 1 else "skills"
    return f"{n} {noun} selected from the list. Skills you type below are added when you save."


def interests_counter_text(n, typed=0):
    noun = "skill" if n == 1 else "skills"
    text = f"{n} {noun} selected from the list. They count as skills you have."
    if typed:
        typed_noun = "interest" if typed == 1 else "interests"
        text += (f" Plus {typed} {typed_noun} you typed, saved but only scored when they name one of the 23 "
                 "interests in section 1.")
    return text


def split_entries(values, groups):
    # Returns (catalogue skills, other entries); typed text naming a catalogue skill becomes that skill
    # Duplicates are dropped, ignoring capitalisation and extra spaces; other entries keep the student's text
    by_clean = {clean_skill_text(s): s for s in groups}
    listed, other, seen = [], [], set()
    for value in values or ():
        text = value if value in groups or value in TERMS_BY_KEY else " ".join(str(value).split())
        if not text:
            continue
        skill = text if text in groups else by_clean.get(clean_skill_text(text))
        if skill:
            if skill not in listed:
                listed.append(skill)
            continue
        fold = clean_skill_text(text) or text.casefold()
        if fold not in seen:
            seen.add(fold)
            other.append(text)
    return listed, other


def _tidy_entries(groups):
    listed, other = split_entries(st.session_state.get(SKILL_PICKER_KEY, []), groups)
    st.session_state[SKILL_PICKER_KEY] = listed + other


def render_skill_picker(catalog, saved_skills, as_interests=False):
    # Returns the selected catalogue skills; outside any form, so the chips and counter update at once
    # as_interests=True: the list is shown in the Interests section (exchange of 4 November 2026); choices from the
    # list are skills, typed entries are the student's own interests; the page saves each in its own field
    groups = skill_groups(catalog)
    options = ordered_skills(groups)
    if not as_interests:
        if SKILL_PICKER_KEY not in st.session_state:
            st.session_state[SKILL_PICKER_KEY] = [s for s in dict.fromkeys(saved_skills) if s in groups]
        picked = st.multiselect(
            SKILL_PICKER_LABEL,
            options=options,
            format_func=lambda s: skill_label(s, groups),
            key=SKILL_PICKER_KEY,
            placeholder="Type to search, for example python or accounting",
            filter_mode=FILTER_MODE,
            select_all=SELECT_ALL,
            wrap=True,
            help="This list contains every skill used by the careers in the dataset. Each skill shows the career "
                 "field that uses it, or Several fields when careers in different fields use it. "
                 "Remove a choice with the x on its chip.",
        )
        st.caption(skill_counter_text(len(picked)))
        return list(dict.fromkeys(picked))

    if SKILL_PICKER_KEY not in st.session_state:
        listed, other = split_entries(saved_skills, groups)
        st.session_state[SKILL_PICKER_KEY] = listed + other
    selection = st.multiselect(
        INTERESTS_SECTION_LABEL,
        options=options,
        format_func=lambda s: skill_label(s, groups),
        key=SKILL_PICKER_KEY,
        placeholder="Choose a skill or type an interest, for example python or farming",
        filter_mode=FILTER_MODE,
        select_all=SELECT_ALL,
        accept_new_options=True,
        wrap=True,
        on_change=_tidy_entries,
        args=(groups,),
        help="This list shows the 144 skills used by the careers, grouped by the career field that uses them. "
             "Each choice counts as a skill you have. To add an interest of your own, type it and press Enter. "
             "Remove a choice with the x on its chip.",
    )
    listed, other = split_entries(selection, groups)
    st.caption(interests_counter_text(len(listed), len(other)))
    return listed + other
