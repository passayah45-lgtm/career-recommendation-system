# Compact skill picker for the assessment page: one grouped, searchable dropdown with chips and a live counter
# Display only: it saves the same catalogue skill names as before; typed skills still go through "Other skills"

from collections import defaultdict

import streamlit as st

from src.data.validation import CATEGORIES

SKILL_PICKER_KEY = "skill_picker"
# styles.css targets the open dropdown through this label, so both must change together
SKILL_PICKER_LABEL = "Skills you already have"
# Skills used by careers in more than one field get this group; it is derived from the data, not invented
SEVERAL_FIELDS = "Several fields"
# Select all would mark all 144 skills as known and give every career full skill points, so it is never offered
SELECT_ALL = False
FILTER_MODE = "contains"


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
    return f"{group} · {skill}" if group else skill


def skill_counter_text(n):
    noun = "skill" if n == 1 else "skills"
    return f"{n} {noun} selected from the list. Skills you type below are added when you save."


def render_skill_picker(catalog, saved_skills):
    # Returns the selected catalogue skills; outside any form, so the chips and counter update at once
    groups = skill_groups(catalog)
    options = ordered_skills(groups)
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
