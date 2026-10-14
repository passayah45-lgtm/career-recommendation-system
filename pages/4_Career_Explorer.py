# Browse, filter and inspect every career in the dataset

import streamlit as st

from src.data.validation import CATEGORIES, EDUCATION_LEVELS
from src.ui.components import (
    SKILL_GAP_PAGE, badges, interest_badges, label, optional_badges, page_setup, sidebar_profile_summary,
)
from src.ui.state import EXPLORER_CAREER_KEY, get_catalog, get_profile, select_career
from src.ui.views import career_label, career_rows, education_label, filter_careers

page_setup("Career Explorer", subtitle="Browse every career in the dataset. Filter by category or search by title, "
                                       "then open one for its skills, education and sources.")
catalog = get_catalog()
sidebar_profile_summary(get_profile())

with st.container(border=True, key="toolbar"):
    f1, f2 = st.columns([1.6, 1])
    categories = f1.multiselect("Categories", options=list(CATEGORIES), placeholder="All categories")
    query = f2.text_input("Search by career title", placeholder="For example: analyst", icon=":material/search:")

careers = filter_careers(catalog.careers, categories, query)
st.caption(f"Showing {len(careers)} of {len(catalog.careers)} careers.")

if not careers:
    with st.container(border=True, key="panel_empty"):
        st.markdown("#### :material/search_off: No careers match these filters")
        st.markdown("Clear the search or choose other categories.")
    st.stop()

TABLE_COLUMNS = {
    "Career": st.column_config.TextColumn(width="medium"),
    "Required skills": st.column_config.NumberColumn(help="Number of required skills"),
    "Preferred skills": st.column_config.NumberColumn(help="Number of optional, preferred skills"),
    "Entry education": st.column_config.NumberColumn(
        help="Typical entry level: " + ", ".join(f"{k} {v}" for k, v in sorted(EDUCATION_LEVELS.items()))),
}
st.dataframe(career_rows(careers), hide_index=True, width="stretch", column_config=TABLE_COLUMNS,
             height=min(400, 36 * len(careers) + 40))

ids = [c.career_id for c in careers]
by_id = {c.career_id: c for c in careers}
current = st.session_state.get(EXPLORER_CAREER_KEY)
career_id = st.selectbox("Career details", options=ids, index=ids.index(current) if current in ids else 0,
                         format_func=lambda cid: career_label(by_id[cid]))
st.session_state[EXPLORER_CAREER_KEY] = career_id
career = by_id[career_id]

with st.container(border=True, key="card_career"):
    st.markdown(f"{badges([career.category], 'gray')} :gray-badge[{career.career_id}]")
    st.markdown(f"### {career.title}")
    st.markdown(career.description)
    a, b = st.columns([1.4, 1])
    with a:
        label("Required skills")
        st.markdown(badges(career.required_skills, "gray"))
        label("Preferred skills (optional)")
        st.markdown(optional_badges(career.preferred_skills))
        label("Interests")
        st.markdown(interest_badges(career.interests))
    with b:
        label("Typical entry education")
        st.markdown(education_label(career.education_level))
        st.caption("A simplified dataset estimate, not a legal or universal requirement.")
        label("Source")
        if career.source_url:
            st.markdown(f"[O*NET OnLine occupation summary]({career.source_url})")
        else:
            st.caption("No matching O*NET occupation. This record is manually curated.")
    with st.expander("Learning goals"):
        st.markdown("\n".join(f"- {g}" for g in career.learning_goals))
    if st.button("Analyze my skill gap for this career", type="primary", icon=":material/school:"):
        select_career(career.career_id)
        st.switch_page(SKILL_GAP_PAGE)
