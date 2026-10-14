# Home page, registered as the default page in app.py
# All counts come from the loaded catalog and the weights from the scoring engine

import streamlit as st

from src.data.validation import CATEGORIES
from src.engine.scoring import DEFAULT_WEIGHTS
from src.ui.components import (
    ANALYTICS_PAGE, ASSESSMENT_PAGE, EXPLORER_PAGE, RECOMMENDATIONS_PAGE, SKILL_GAP_PAGE, page_setup,
    score_disclaimer, sidebar_profile_summary,
)
from src.ui.state import get_catalog, get_profile

profile = get_profile()
hero = page_setup(
    "Career Recommendation System",
    subtitle="Match your skills and interests to careers, see exactly why each one was suggested, "
             "and get free learning resources for the skills you still need.",
    eyebrow="Transparent career guidance",
    hero=True,
)
catalog = get_catalog()
sidebar_profile_summary(profile)

with hero:
    a, b, _ = st.columns([1.2, 1.2, 2])
    if profile:
        if a.button("See my recommendations", type="primary", icon=":material/arrow_forward:", width="stretch"):
            st.switch_page(RECOMMENDATIONS_PAGE)
        if b.button("Edit my assessment", icon=":material/edit:", width="stretch"):
            st.switch_page(ASSESSMENT_PAGE)
    else:
        if a.button("Start career assessment", type="primary", icon=":material/arrow_forward:", width="stretch"):
            st.switch_page(ASSESSMENT_PAGE)
        if b.button("Browse all careers", icon=":material/explore:", width="stretch"):
            st.switch_page(EXPLORER_PAGE)
    st.caption("About two minutes. No account needed. Your answers stay in this browser session.")

with st.container(key="stats"):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Careers", len(catalog.careers), border=True)
    c2.metric("Categories", len(CATEGORIES), border=True)
    c3.metric("Unique skills", len(catalog.known_skills), border=True)
    c4.metric("Learning resources", len(catalog.resources), border=True)

st.subheader("How it works", anchor=False)
steps = [
    ("1", ASSESSMENT_PAGE, "Career Assessment", "Enter your skills, interests and education level."),
    ("2", RECOMMENDATIONS_PAGE, "Recommendations", "See your best-matching careers, each with a score and the reasons behind it."),
    ("3", SKILL_GAP_PAGE, "Skill-Gap Analysis", "Compare your skills with one career and get a learning resource for each gap."),
]
for col, (num, page, title, text) in zip(st.columns(3), steps):
    with col, st.container(border=True, key=f"step_{num}", height="stretch"):
        st.markdown(f'<span class="crs-step-num">{num}</span>', unsafe_allow_html=True)
        st.page_link(page, label=f"**{title}**", icon=":material/arrow_forward:")
        st.caption(text)

e1, e2 = st.columns(2)
with e1, st.container(border=True, key="card_explorer"):
    st.page_link(EXPLORER_PAGE, label="**Career Explorer**", icon=":material/explore:")
    st.caption(f"Browse and filter all {len(catalog.careers)} careers, with skills, education and sources.")
with e2, st.container(border=True, key="card_analytics"):
    st.page_link(ANALYTICS_PAGE, label="**Analytics**", icon=":material/monitoring:")
    st.caption("Charts about the dataset and about your own results.")

weights = DEFAULT_WEIGHTS.as_dict()
with st.container(border=True, key="note"):
    st.markdown("**:material/balance: How to read the score**")
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
            "Full details: `docs/recommendation_algorithm.md` and `docs/dataset_documentation.md` in the repository."
        )
