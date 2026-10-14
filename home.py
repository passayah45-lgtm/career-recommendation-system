# Home page, registered as the default page in app.py
# All matching and scoring comes from src/services.

import streamlit as st

from src.data.validation import CATEGORIES
from src.ui.components import (
    ANALYTICS_PAGE, ASSESSMENT_PAGE, EXPLORER_PAGE, RECOMMENDATIONS_PAGE, SKILL_GAP_PAGE, page_setup,
    score_disclaimer, sidebar_profile_summary,
)
from src.ui.state import get_catalog, get_profile

page_setup("Career Recommendation System")
catalog = get_catalog()
profile = get_profile()
sidebar_profile_summary(profile)

st.markdown(
    "Find careers that fit your current skills and interests, see exactly why each one was suggested, "
    "and get free learning resources for the skills you still need."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Careers", len(catalog.careers))
c2.metric("Categories", len(CATEGORIES))
c3.metric("Skills covered", len(catalog.known_skills))
c4.metric("Learning resources", len(catalog.resources))

st.subheader("How it works")
steps = [
    (ASSESSMENT_PAGE, "1. Career Assessment", "Enter your skills, interests and education level."),
    (RECOMMENDATIONS_PAGE, "2. Recommendations", "See your best-matching careers with a score and the reasons behind it."),
    (SKILL_GAP_PAGE, "3. Skill-Gap Analysis", "Compare your skills with one career and get learning resources."),
    (EXPLORER_PAGE, "4. Career Explorer", "Browse and filter all careers in the dataset."),
    (ANALYTICS_PAGE, "5. Analytics", "Charts about the dataset and about your own results."),
]
for page, label, text in steps:
    with st.container(border=True):
        st.page_link(page, label=label)
        st.caption(text)

if profile:
    st.success("Your assessment is saved for this browser session.")
    st.page_link(RECOMMENDATIONS_PAGE, label="Continue to your recommendations")
else:
    st.page_link(ASSESSMENT_PAGE, label="Start the assessment")

with st.expander("About the score and its limits"):
    score_disclaimer()
    st.markdown(
        "- The score combines required skills (55%), preferred skills (15%), interests (25%) and education (5%).\n"
        "- Skills are matched by name against a curated dataset of 50 careers. Related skills earn no partial credit.\n"
        "- Education levels are simplified estimates and carry a small weight. They are never a hard filter.\n"
        "- Many sources are from the US or UK, so some careers and resources may differ in your country.\n"
        "- Your answers stay in this browser session only. Nothing is saved to a database.\n\n"
        "Full details: `docs/recommendation_algorithm.md` and `docs/dataset_documentation.md` in the repository."
    )
