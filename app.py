# Streamlit entry point: start with `streamlit run app.py`
# st.navigation gives every page an explicit sidebar title, so the home page is not labelled "app"

import streamlit as st

from src.ui.components import (
    ANALYTICS_PAGE, ASSESSMENT_PAGE, EXPLORER_PAGE, HOME_PAGE, RECOMMENDATIONS_PAGE, SKILL_GAP_PAGE,
)

PAGES = [
    st.Page(HOME_PAGE, title="Home", default=True),
    st.Page(ASSESSMENT_PAGE, title="Career Assessment"),
    st.Page(RECOMMENDATIONS_PAGE, title="Recommendations"),
    st.Page(SKILL_GAP_PAGE, title="Skill-Gap Analysis"),
    st.Page(EXPLORER_PAGE, title="Career Explorer"),
    st.Page(ANALYTICS_PAGE, title="Analytics"),
]

st.navigation(PAGES).run()
