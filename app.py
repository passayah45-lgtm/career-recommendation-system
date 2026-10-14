# Streamlit entry point: start with `streamlit run app.py`
# st.navigation gives every page an explicit sidebar title and icon, so the home page is not labelled "app"

import streamlit as st

from src.ui.components import (
    ANALYTICS_PAGE, ASSESSMENT_PAGE, EXPLORER_PAGE, HOME_PAGE, RECOMMENDATIONS_PAGE, SKILL_GAP_PAGE,
)
from src.ui.theme import PAGE_ICONS

PAGES = [
    st.Page(HOME_PAGE, title="Home", icon=PAGE_ICONS["Home"], default=True),
    st.Page(ASSESSMENT_PAGE, title="Career Assessment", icon=PAGE_ICONS["Career Assessment"]),
    st.Page(RECOMMENDATIONS_PAGE, title="Recommendations", icon=PAGE_ICONS["Recommendations"]),
    st.Page(SKILL_GAP_PAGE, title="Skill-Gap Analysis", icon=PAGE_ICONS["Skill-Gap Analysis"]),
    st.Page(EXPLORER_PAGE, title="Career Explorer", icon=PAGE_ICONS["Career Explorer"]),
    st.Page(ANALYTICS_PAGE, title="Analytics", icon=PAGE_ICONS["Analytics"]),
]

st.navigation(PAGES).run()
