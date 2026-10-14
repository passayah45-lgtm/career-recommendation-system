# Collects the learner profile and validates it through the service layer

import streamlit as st

from src.data.validation import EDUCATION_LEVELS
from src.services.profiles import MAX_EXPERIENCE_YEARS, ProfileValidationError
from src.services.recommendations import profile_from_input
from src.ui.components import RECOMMENDATIONS_PAGE, chips, page_setup, reset_button, sidebar_profile_summary
from src.ui.state import get_catalog, get_profile, set_profile
from src.ui.views import build_profile_input, education_label

page_setup("Career Assessment")
catalog = get_catalog()
saved = get_profile() or {}
sidebar_profile_summary(saved)

st.markdown(
    "Answer four short sections. You need **at least one skill or one interest**. "
    "The more you add, the more useful your results will be."
)

known_skills = sorted(catalog.known_skills)
saved_skills = saved.get("skills", [])
preselected = [s for s in saved_skills if s in catalog.known_skills]
other_text = ", ".join(s for s in saved_skills if s not in catalog.known_skills)
education_options = [None] + sorted(EDUCATION_LEVELS)
saved_level = saved.get("education_level")

with st.form("assessment_form"):
    st.subheader("1. Skills")
    selected_skills = st.multiselect(
        "Skills you already have",
        options=known_skills,
        default=preselected,
        placeholder="Type to search, for example python or accounting",
        help="This list contains every skill used by the careers in the dataset.",
    )
    other_skills = st.text_area(
        "Other skills (optional)",
        value=other_text,
        placeholder="For example: ML, JS, CI/CD",
        help="Separate skills with commas. Common short names such as ML, JS, CI/CD and K8s are recognized. "
             "Skills that are not in the dataset are listed back to you and are not scored.",
    )

    st.subheader("2. Interests")
    interests = st.multiselect(
        "Kinds of work that interest you",
        options=sorted(catalog.interests),
        default=[i for i in saved.get("interests", []) if i in catalog.interests],
    )

    st.subheader("3. Education")
    education = st.selectbox(
        "Highest education level completed",
        options=education_options,
        index=education_options.index(saved_level) if saved_level in education_options else 0,
        format_func=education_label,
    )
    st.caption("Education has a 5% weight. It is never used to exclude a career.")

    st.subheader("4. Work experience (optional)")
    experience = st.number_input(
        "Years of work experience",
        min_value=0, max_value=MAX_EXPERIENCE_YEARS, step=1,
        value=saved.get("experience_years"),
        placeholder="Leave empty if you prefer not to say",
    )
    st.caption("Shown for context only. The current dataset has no experience requirements, so it does not change the score.")

    submitted = st.form_submit_button("Save my assessment", type="primary")

with st.expander("What the education levels mean"):
    for level, meaning in sorted(EDUCATION_LEVELS.items()):
        st.markdown(f"- **{level}**: {meaning}")
    st.caption("Equivalent experience counts. Levels describe typical entry in this dataset, not legal requirements.")

with st.expander("Why there is no learning goals field"):
    st.markdown(
        "Each career lists learning goals, and you will see them in your results. "
        "They are written as free text, so the system cannot compare them reliably with your own goals. "
        "To keep the score honest, goals are shown but not matched."
    )

if submitted:
    raw = build_profile_input(selected_skills, other_skills, interests, education,
                              int(experience) if experience is not None else None)
    try:
        _, report = profile_from_input(raw, catalog)
    except ProfileValidationError as exc:
        st.error(f"Please check your answers: {exc}.")
    else:
        if not report.recognized_skills and not report.recognized_interests:
            st.error("Add at least one skill from the list, or one interest, so the system has something to match.")
            if report.unknown_skills:
                st.warning(f"These skills are not in the dataset: {', '.join(report.unknown_skills)}.")
        else:
            set_profile(raw)
            st.success("Assessment saved for this browser session.")
            st.markdown(f"**Recognized skills:** {chips(report.recognized_skills)}")
            if report.unknown_skills:
                st.warning(f"Not in the dataset, so not scored: {', '.join(report.unknown_skills)}.")
            if report.duplicate_skills:
                st.info(f"Counted once because they repeat another skill: {', '.join(report.duplicate_skills)}.")
            st.page_link(RECOMMENDATIONS_PAGE, label="See my recommendations")
elif saved:
    st.info("You already have a saved assessment. Change the answers above and save again, or view your results.")
    st.page_link(RECOMMENDATIONS_PAGE, label="See my recommendations")

if saved:
    reset_button(key="page_reset")
