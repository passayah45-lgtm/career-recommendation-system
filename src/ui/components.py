# Reusable Streamlit building blocks shared by the pages

import streamlit as st

from src.services.recommendations import SCORE_DISCLAIMER
from src.ui.state import reset_assessment

HOME_PAGE = "home.py"
ASSESSMENT_PAGE = "pages/1_Career_Assessment.py"
RECOMMENDATIONS_PAGE = "pages/2_Recommendations.py"
SKILL_GAP_PAGE = "pages/3_Skill_Gap_Analysis.py"
EXPLORER_PAGE = "pages/4_Career_Explorer.py"
ANALYTICS_PAGE = "pages/5_Analytics.py"


def page_setup(title):
    st.set_page_config(page_title=f"{title} | Career Recommendation System", layout="wide")
    st.title(title)


def chips(items, empty="None"):
    # Skills shown as inline code chips, readable and copyable
    if not items:
        return f"_{empty}_"
    return " ".join(f"`{i}`" for i in items)


def score_disclaimer():
    st.caption(SCORE_DISCLAIMER)


def need_profile_message():
    st.info("Complete the career assessment first. It takes about two minutes.")
    st.page_link(ASSESSMENT_PAGE, label="Go to the Career Assessment")


def show_profile_warnings(warnings):
    for w in warnings:
        st.warning(w)


def reset_button(key="reset"):
    if st.button("Start a new assessment", key=key, help="Clears your answers from this browser session"):
        reset_assessment()
        st.switch_page(ASSESSMENT_PAGE)


def sidebar_profile_summary(profile):
    with st.sidebar:
        st.subheader("Your assessment")
        if not profile:
            st.caption("No assessment yet.")
            return
        st.caption(f"Skills entered: {len(profile.get('skills', []))}")
        st.caption(f"Interests: {len(profile.get('interests', []))}")
        level = profile.get("education_level")
        st.caption(f"Education level: {'not provided' if level is None else level}")
        reset_button(key="sidebar_reset")
