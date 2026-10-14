# Browse, filter and inspect every career in the dataset

import streamlit as st

from src.data.validation import CATEGORIES
from src.ui.components import (
    SKILL_GAP_PAGE, badges, icon_heading, interest_badges, label, optional_badges, page_setup,
    sidebar_profile_summary,
)
from src.ui.state import EXPLORER_CAREER_KEY, get_catalog, get_profile, select_career
from src.ui.views import career_label, career_list_rows, education_label, filter_careers

TABLE_KEY = "explorer_table"

page_setup("Explore Careers", subtitle="Browse all careers, filter by category, or search for a specific role.")
catalog = get_catalog()
sidebar_profile_summary(get_profile())

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
    # A click on a list row selects that career for the details panel
    rows = st.session_state[TABLE_KEY].selection.rows
    if rows and rows[0] < len(ids):
        st.session_state[EXPLORER_CAREER_KEY] = ids[rows[0]]


list_col, detail_col = st.columns([1, 1.7])
with list_col, st.container(border=True, key="panel_list"):
    label("Careers")
    st.dataframe(career_list_rows(careers), hide_index=True, width="stretch", key=TABLE_KEY,
                 on_select=pick_from_table, selection_mode="single-row",
                 height=min(560, 36 * len(careers) + 40),
                 column_config={"Career": st.column_config.TextColumn(width="medium")})
    st.caption("Click a row to open its details.")

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

        e_col, c_col = st.columns(2)
        with e_col, st.container(border=True, key="card_edu", height="stretch"):
            icon_heading(":material/school:", "green", "####")
            st.caption("Typical entry education")
            st.markdown(f"**{education_label(career.education_level)}**")
        with c_col, st.container(border=True, key="card_cat", height="stretch"):
            icon_heading(":material/category:", "blue", "####")
            st.caption("Category")
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
        if st.button("Analyze my skill gap for this career", type="primary", icon=":material/school:"):
            select_career(career.career_id)
            st.switch_page(SKILL_GAP_PAGE)
