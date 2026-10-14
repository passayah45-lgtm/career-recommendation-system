# Browse, filter and inspect every career in the dataset

import streamlit as st

from src.data.validation import CATEGORIES
from src.ui.components import SKILL_GAP_PAGE, chips, page_setup, sidebar_profile_summary
from src.ui.state import EXPLORER_CAREER_KEY, get_catalog, get_profile, select_career
from src.ui.views import career_label, career_rows, education_label, filter_careers

page_setup("Career Explorer")
catalog = get_catalog()
sidebar_profile_summary(get_profile())

f1, f2 = st.columns([2, 1])
categories = f1.multiselect("Categories", options=list(CATEGORIES), placeholder="All categories")
query = f2.text_input("Search by career title", placeholder="For example: analyst")

careers = filter_careers(catalog.careers, categories, query)
st.caption(f"Showing {len(careers)} of {len(catalog.careers)} careers.")

if not careers:
    st.info("No careers match these filters. Clear the search or choose other categories.")
    st.stop()

st.dataframe(career_rows(careers), hide_index=True, width="stretch")

ids = [c.career_id for c in careers]
by_id = {c.career_id: c for c in careers}
current = st.session_state.get(EXPLORER_CAREER_KEY)
career_id = st.selectbox("Career details", options=ids, index=ids.index(current) if current in ids else 0,
                         format_func=lambda cid: career_label(by_id[cid]))
st.session_state[EXPLORER_CAREER_KEY] = career_id
career = by_id[career_id]

with st.container(border=True):
    st.markdown(f"### {career.title}")
    st.caption(f"{career.category} | {career.career_id}")
    st.write(career.description)
    a, b = st.columns(2)
    with a:
        st.markdown(f"**Required skills:** {chips(career.required_skills)}")
        st.markdown(f"**Preferred skills (optional):** {chips(career.preferred_skills)}")
        st.markdown(f"**Interests:** {chips(career.interests)}")
    with b:
        st.markdown(f"**Typical entry education:** {education_label(career.education_level)}")
        st.caption("A simplified dataset estimate, not a legal or universal requirement.")
        st.markdown("**Learning goals**")
        st.markdown("\n".join(f"- {g}" for g in career.learning_goals))
    if career.source_url:
        st.markdown(f"Source: [O*NET OnLine occupation summary]({career.source_url})")
    else:
        st.caption("No matching O*NET occupation. This record is manually curated.")
    if st.button("Analyze my skill gap for this career", type="primary"):
        select_career(career.career_id)
        st.switch_page(SKILL_GAP_PAGE)
