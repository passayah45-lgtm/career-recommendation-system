# Streamlit entry point: start with `streamlit run app.py`
# st.navigation gives every page an explicit sidebar title and icon, so the home page is not labelled "app"

import streamlit as st

from src.ui.freshness import drop_stale_modules, remember_loaded_modules

# Must run before the other src imports: reloads modules changed by a hot update on Community Cloud
if drop_stale_modules():
    st.cache_resource.clear()

from src.ui.components import (  # noqa: E402
    ANALYTICS_PAGE, ASSESSMENT_PAGE, EXPLORER_PAGE, HOME_PAGE, RECOMMENDATIONS_PAGE, SKILL_GAP_PAGE,
)
from src.ui.theme import PAGE_ICONS  # noqa: E402

PAGES = [
    st.Page(HOME_PAGE, title="Home", icon=PAGE_ICONS["Home"], default=True),
    st.Page(ASSESSMENT_PAGE, title="Career Assessment", icon=PAGE_ICONS["Career Assessment"]),
    st.Page(RECOMMENDATIONS_PAGE, title="Recommendations", icon=PAGE_ICONS["Recommendations"]),
    st.Page(SKILL_GAP_PAGE, title="Skill-Gap Analysis", icon=PAGE_ICONS["Skill-Gap Analysis"]),
    st.Page(EXPLORER_PAGE, title="Career Explorer", icon=PAGE_ICONS["Career Explorer"]),
    st.Page(ANALYTICS_PAGE, title="Analytics", icon=PAGE_ICONS["Analytics"]),
]

try:
    st.navigation(PAGES).run()
finally:
    # Also runs when a page stops or switches, so every imported module gets a baseline
    remember_loaded_modules()
