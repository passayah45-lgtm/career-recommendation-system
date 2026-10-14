# Home page, registered as the default page in app.py
# All counts come from the loaded catalog and the weights from the scoring engine

import streamlit as st

from src.data.validation import CATEGORIES
from src.engine.scoring import DEFAULT_WEIGHTS
from src.ui.components import (
    ASSESSMENT_PAGE, EXPLORER_PAGE, RECOMMENDATIONS_PAGE, SKILL_GAP_PAGE, icon_heading, page_setup,
    score_disclaimer, sidebar_profile_summary, stat_card,
)
from src.ui.state import get_catalog, get_profile

profile = get_profile()
hero = page_setup(
    "Career Recommendation System",
    subtitle="Find careers that fit your skills and interests, see why each one is recommended, "
             "and get free learning resources to build the skills you still need.",
    eyebrow="Welcome to the",
    hero=True,
)
catalog = get_catalog()
sidebar_profile_summary(profile)

with hero:
    with st.container(horizontal=True):
        if profile:
            if st.button("See my recommendations", type="primary", icon=":material/arrow_forward:"):
                st.switch_page(RECOMMENDATIONS_PAGE)
            if st.button("Edit my assessment", icon=":material/edit:"):
                st.switch_page(ASSESSMENT_PAGE)
        else:
            if st.button("Start career assessment", type="primary", icon=":material/arrow_forward:"):
                st.switch_page(ASSESSMENT_PAGE)
            if st.button("Browse all careers", icon=":material/explore:"):
                st.switch_page(EXPLORER_PAGE)
    st.caption("About two minutes. No account needed. Your answers stay in this browser session.")

with st.container(key="stats"):
    c1, c2, c3, c4 = st.columns(4)
    stat_card(c1, "Careers", len(catalog.careers), ":material/work:", "blue", "careers")
    stat_card(c2, "Categories", len(CATEGORIES), ":material/category:", "violet", "categories")
    stat_card(c3, "Unique skills", len(catalog.known_skills), ":material/lightbulb:", "green", "skills")
    stat_card(c4, "Learning resources", len(catalog.resources), ":material/menu_book:", "orange", "resources")

st.subheader("How it works", anchor=False)
steps = [
    (ASSESSMENT_PAGE, ":material/assignment:", "blue", "Career Assessment",
     "Enter your skills, interests and education level."),
    (RECOMMENDATIONS_PAGE, ":material/insights:", "violet", "Get Recommendations",
     "See your top matching careers with clear explanations."),
    (SKILL_GAP_PAGE, ":material/target:", "green", "Analyse Skill Gaps",
     "Identify missing skills and open free learning resources."),
    (EXPLORER_PAGE, ":material/map:", "orange", "Explore and Learn",
     f"Browse all {len(catalog.careers)} careers and plan your next steps."),
]
for col, (page, icon, color, title, text) in zip(st.columns(4), steps):
    with col, st.container(border=True, key=f"step_{color}", height="stretch"):
        icon_heading(icon, color)
        st.page_link(page, label=f"**{title}**")
        st.caption(text)

weights = DEFAULT_WEIGHTS.as_dict()
with st.container(border=True, key="note"):
    icon_col, text_col = st.columns([0.06, 1], vertical_alignment="top")
    with icon_col:
        icon_heading(":material/info:", "blue", "####")
    with text_col:
        st.markdown("**About the compatibility score**")
        score_disclaimer()
        st.markdown(
            f"The score combines required skills ({weights['required_skills']:.0%}), "
            f"preferred skills ({weights['preferred_skills']:.0%}), interests ({weights['interests']:.0%}) "
            f"and education ({weights['education']:.0%}). Every recommendation shows this breakdown."
        )
        with st.expander("Limits of this system"):
            st.markdown(
                "- Skills are matched by name against a curated dataset. Related skills earn no partial credit.\n"
                "- Education levels are simplified estimates with a small weight. They never exclude a career.\n"
                "- Many sources are from the US or UK, so some careers and resources may differ in your country.\n"
                "- Your answers stay in this browser session only. Nothing is saved to a database.\n\n"
                "Full details: `docs/recommendation_algorithm.md` and `docs/dataset_documentation.md` "
                "in the repository."
            )
