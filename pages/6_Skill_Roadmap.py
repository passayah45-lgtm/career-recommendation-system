# My Skill Development Roadmap: an ordered learning plan for one career, built from the existing skill gap

import streamlit as st

from src.services.profiles import ProfileValidationError
from src.services.roadmap import RoadmapError, build_roadmap
from src.ui.career_lists import show_flash
from src.ui.components import (
    ASSESSMENT_PAGE, RECOMMENDATIONS_PAGE, SKILL_GAP_PAGE, page_setup, session_data_panel, sidebar_profile_summary,
)
from src.ui.roadmap_view import career_options, roadmap_section
from src.ui.state import ROADMAP_CAREER_KEY, get_catalog, get_profile, get_progress, select_career

page_setup("My Skill Development Roadmap", eyebrow="Plan your learning",
           subtitle="An ordered plan from the skills you have to the skills a career needs, with a free resource "
                    "for each step.")
catalog = get_catalog()
profile = get_profile()
sidebar_profile_summary(profile)
show_flash()

if not profile:
    st.info("You have no saved assessment, so every skill counts as missing. Complete the assessment for a personal "
            "roadmap.", icon=":material/info:")

options = career_options(profile, catalog)
if not options:
    with st.container(border=True, key="panel_empty"):
        st.markdown("#### :material/route: Choose a career first")
        st.markdown("Complete the assessment to get recommendations, or mark careers as **Interested** on the "
                    "Recommendations page. They appear here as roadmap targets.")
        st.page_link(ASSESSMENT_PAGE, label="Go to the Career Assessment", icon=":material/arrow_forward:")
        st.page_link(RECOMMENDATIONS_PAGE, label="Back to my recommendations", icon=":material/insights:")
    st.stop()

titles = {c.career_id: c.title for c in catalog.careers}
ids = list(options)
current = st.session_state.get(ROADMAP_CAREER_KEY)
career_id = st.selectbox("Roadmap for", options=ids, index=ids.index(current) if current in ids else 0,
                         format_func=lambda cid: f"{titles[cid]} ({options[cid]})",
                         help="Interested careers come first, then your top recommendations and other saved roadmaps.")
st.session_state[ROADMAP_CAREER_KEY] = career_id

try:
    roadmap = build_roadmap(profile, career_id, catalog, get_progress().get(career_id))
except (RoadmapError, ProfileValidationError, ValueError) as exc:
    st.error(f"The roadmap could not be built: {exc}.", icon=":material/error:")
    st.stop()

roadmap_section(roadmap, has_profile=bool(profile))

with st.container(horizontal=True):
    st.page_link(RECOMMENDATIONS_PAGE, label="Back to my recommendations", icon=":material/arrow_back:")
    if st.button("Open the full skill-gap analysis", key="roadmap_to_gap", icon=":material/school:"):
        select_career(career_id)
        st.switch_page(SKILL_GAP_PAGE)

session_data_panel(profile, key="roadmap_session", allow_download=bool(profile))
