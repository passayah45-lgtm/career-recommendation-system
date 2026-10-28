# Browse, filter and inspect every career in the dataset

import streamlit as st

from src.data.validation import CATEGORIES
from src.ui.components import (
    SKILL_GAP_PAGE, badges, interest_badges, label, optional_badges, page_setup,
    sidebar_profile_summary,
)
from src.services.feedback import INTERESTED, NOT_FOR_ME
from src.ui.state import EXPLORER_CAREER_KEY, decide, get_catalog, get_feedback, get_profile, select_career
from src.ui.career_lists import show_flash
from src.ui.views import career_from_cell, career_label, career_list_rows, education_label, filter_careers

TABLE_KEY = "explorer_table"

page_setup("Explore Careers", subtitle="Browse all careers, filter by category, or search for a specific role.")
catalog = get_catalog()
sidebar_profile_summary(get_profile())
show_flash()

with st.container(border=True, key="toolbar"):
    f1, f2 = st.columns([1.4, 1])
    query = f1.text_input("Search by career title", placeholder="Search careers by title, for example analyst",
                          icon=":material/search:")
    categories = f2.multiselect("Categories", options=list(CATEGORIES), placeholder="All categories")

careers = filter_careers(catalog.careers, categories, query)
st.caption(f"Showing {len(careers)} of {len(catalog.careers)} careers.")

if not careers:
    with st.container(border=True, key="panel_empty"):
        st.markdown("#### :material/search_off: No careers match these filters")
        st.markdown("Clear the search or choose other categories.")
    st.stop()

ids = [c.career_id for c in careers]
by_id = {c.career_id: c for c in careers}


def pick_from_table():
    # A click on any cell opens that row's career; cell selection needs no checkbox column
    picked = career_from_cell(ids, st.session_state[TABLE_KEY].selection.cells)
    if picked:
        st.session_state[EXPLORER_CAREER_KEY] = picked


list_col, detail_col = st.columns([1.15, 1.45])
with list_col, st.container(border=True, key="panel_list"):
    label(f"Careers ({len(careers)})")
    st.dataframe(career_list_rows(careers), hide_index=True, width="stretch", key=TABLE_KEY,
                 on_select=pick_from_table, selection_mode="single-cell",
                 height=min(520, 35 * len(careers) + 38),
                 column_config={"Career": st.column_config.TextColumn(width=230),
                                "Category": st.column_config.TextColumn(width=115)})
    st.caption("Click a career to open its details.")

with detail_col:
    current = st.session_state.get(EXPLORER_CAREER_KEY)
    career_id = st.selectbox("Career details", options=ids, index=ids.index(current) if current in ids else 0,
                             format_func=lambda cid: career_label(by_id[cid]))
    st.session_state[EXPLORER_CAREER_KEY] = career_id
    career = by_id[career_id]

    with st.container(border=True, key="card_career"):
        title_col, link_col = st.columns([2, 1], vertical_alignment="center")
        with title_col:
            st.markdown(f"### {career.title}")
            st.markdown(f"{badges([career.category], 'blue')} :gray-badge[{career.career_id}]")
        with link_col:
            if career.source_url:
                st.markdown(f"[:material/open_in_new: View on O*NET]({career.source_url})")
            else:
                st.caption("Manually curated, no O*NET match.")
        st.markdown(career.description)

        # Two compact fact boxes side by side, stacked by Streamlit on narrow screens
        e_col, c_col = st.columns([1.4, 1])
        with e_col, st.container(border=True, key="card_edu", height="stretch", gap="small"):
            st.caption(":material/school: Typical entry education")
            st.markdown(f"**{education_label(career.education_level)}**")
        with c_col, st.container(border=True, key="card_cat", height="stretch", gap="small"):
            st.caption(":material/category: Category")
            st.markdown(f"**{career.category}**")
        st.caption("Education levels are simplified dataset estimates, not legal or universal requirements.")

        label(f"Required skills ({len(career.required_skills)})")
        st.markdown(badges(career.required_skills, "gray"))
        label(f"Preferred skills, optional ({len(career.preferred_skills)})")
        st.markdown(optional_badges(career.preferred_skills))
        label("Interests")
        st.markdown(interest_badges(career.interests))
        with st.expander("Learning goals"):
            st.markdown("\n".join(f"- {g}" for g in career.learning_goals))
        decision = get_feedback().get(career.career_id)
        with st.container(horizontal=True, vertical_alignment="center"):
            if decision == INTERESTED:
                st.markdown(":green-badge[:material/thumb_up: In your Interested list]")
            elif decision == NOT_FOR_ME:
                st.markdown(":gray-badge[:material/thumb_down: In your Not for me list]")
            if decision != INTERESTED:
                st.button("Interested", key="explorer_like", icon=":material/thumb_up:",
                          on_click=decide, args=(career.career_id, INTERESTED, career.title))
            if decision != NOT_FOR_ME:
                st.button("Not for me", key="explorer_dislike", icon=":material/thumb_down:",
                          on_click=decide, args=(career.career_id, NOT_FOR_ME, career.title))
            if decision is not None:
                st.button("Remove from list", key="explorer_remove", icon=":material/backspace:",
                          on_click=decide, args=(career.career_id, None, career.title))
        if st.button("Analyze my skill gap for this career", type="primary", icon=":material/school:"):
            select_career(career.career_id)
            st.switch_page(SKILL_GAP_PAGE)
