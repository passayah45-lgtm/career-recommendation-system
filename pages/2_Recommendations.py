# Shows ranked careers from the Phase 3 recommend() service

import streamlit as st

from src.services.profiles import ProfileValidationError
from src.services.recommendations import recommend
from src.ui.components import (
    EXPLORER_PAGE, SKILL_GAP_PAGE, chips, need_profile_message, page_setup, score_disclaimer,
    show_profile_warnings, sidebar_profile_summary,
)
from src.ui.state import EXPLORER_CAREER_KEY, TOP_K_KEY, get_catalog, get_profile, get_top_k, select_career
from src.ui.views import education_label

page_setup("Career Recommendations")
catalog = get_catalog()
profile = get_profile()
sidebar_profile_summary(profile)

if not profile:
    need_profile_message()
    st.stop()

top_k = st.slider("Number of careers to show", min_value=1, max_value=len(catalog.careers),
                  value=min(get_top_k(), len(catalog.careers)), key="top_k_slider")
st.session_state[TOP_K_KEY] = top_k

try:
    result = recommend(profile, catalog, top_k=top_k)
except (ProfileValidationError, ValueError) as exc:
    st.error(f"Your saved assessment could not be used: {exc}. Please complete the assessment again.")
    st.stop()

show_profile_warnings(result["warnings"])
score_disclaimer()

recommendations = result["recommendations"]
if not recommendations:
    st.info("No careers were returned. Try adding more skills or interests.")
    st.stop()

COMPONENT_LABELS = {
    "required_skills": "Required skills",
    "preferred_skills": "Preferred skills",
    "interests": "Interests",
    "education": "Education",
}

for rec in recommendations:
    cid = rec["career_id"]
    with st.container(border=True):
        head, score_col = st.columns([3, 1])
        head.markdown(f"### {rec['rank']}. {rec['career_title']}")
        head.caption(f"{rec['category']} | {cid}")
        score_col.metric("Compatibility score", f"{rec['score']:.1f} / 100")
        score_col.progress(min(1.0, rec["score"] / 100))

        req_col, pref_col, int_col = st.columns(3)
        with req_col:
            st.markdown("**Required skills**")
            st.markdown(f"You have: {chips(rec['matched_required_skills'])}")
            st.markdown(f"Missing: {chips(rec['missing_required_skills'])}")
        with pref_col:
            st.markdown("**Preferred skills (optional)**")
            st.markdown(f"You have: {chips(rec['matched_preferred_skills'])}")
            st.markdown(f"Not yet: {chips(rec['missing_preferred_skills'])}")
        with int_col:
            st.markdown("**Interests**")
            st.markdown(f"Matched: {chips(rec['matched_interests'])}")
            edu = rec["education"]
            st.markdown(f"Typical entry: {education_label(edu['career_level'])}")

        st.markdown("**Why this career**")
        st.markdown("\n".join(f"- {r}" for r in rec["reasons"]))
        for note in rec["notes"]:
            st.caption(note)

        with st.expander("Score breakdown"):
            rows = [
                {
                    "Component": COMPONENT_LABELS.get(name, name),
                    "Match (0 to 1)": comp["value"],
                    "Weight": comp["weight"],
                    "Points": comp["contribution"],
                    "Used": comp["applicable"],
                }
                for name, comp in rec["score_components"].items()
            ]
            st.dataframe(rows, hide_index=True, width="stretch")
            st.caption("Points add up to the compatibility score.")

        b1, b2 = st.columns(2)
        if b1.button("Analyze my skill gap", key=f"gap_{cid}", type="primary"):
            select_career(cid)
            st.switch_page(SKILL_GAP_PAGE)
        if b2.button("View career details", key=f"explore_{cid}"):
            st.session_state[EXPLORER_CAREER_KEY] = cid
            st.switch_page(EXPLORER_PAGE)
