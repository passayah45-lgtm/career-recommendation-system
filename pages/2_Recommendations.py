# Shows ranked careers from the Phase 3 recommend() service

import streamlit as st

from src.services.profiles import ProfileValidationError
from src.services.recommendations import recommend
from src.ui.components import (
    EXPLORER_PAGE, SKILL_GAP_PAGE, badges, have_badges, interest_badges, label, missing_badges,
    need_profile_message, optional_badges, page_setup, ring, score_disclaimer, show_profile_warnings,
    sidebar_profile_summary,
)
from src.ui.state import EXPLORER_CAREER_KEY, TOP_K_KEY, get_catalog, get_profile, get_top_k, select_career
from src.ui.views import education_label

page_setup("Your Career Recommendations", eyebrow="Step 2 of 3",
           subtitle="The careers that best match your profile, with explanations and skill analysis.")
catalog = get_catalog()
profile = get_profile()
sidebar_profile_summary(profile)

if not profile:
    need_profile_message()
    st.stop()

with st.container(border=True, key="toolbar"):
    slider_col, info_col = st.columns([1.3, 1], vertical_alignment="center")
    top_k = slider_col.slider("Number of careers to show", min_value=1, max_value=len(catalog.careers),
                              value=min(get_top_k(), len(catalog.careers)), key="top_k_slider")
    with info_col:
        score_disclaimer()
st.session_state[TOP_K_KEY] = top_k

try:
    result = recommend(profile, catalog, top_k=top_k)
except (ProfileValidationError, ValueError) as exc:
    st.error(f"Your saved assessment could not be used: {exc}. Please complete the assessment again.",
             icon=":material/error:")
    st.stop()

show_profile_warnings(result["warnings"])

recommendations = result["recommendations"]
if not recommendations:
    st.info("No careers were returned. Try adding more skills or interests.", icon=":material/info:")
    st.stop()

COMPONENT_LABELS = {
    "required_skills": "Required skills",
    "preferred_skills": "Preferred skills",
    "interests": "Interests",
    "education": "Education",
}
BREAKDOWN_COLUMNS = {
    "Match (0 to 1)": st.column_config.NumberColumn(format="%.2f"),
    "Weight": st.column_config.NumberColumn(format="%.2f"),
    "Points": st.column_config.NumberColumn(format="%.1f"),
}

for rec in recommendations:
    cid = rec["career_id"]
    top = rec["rank"] == 1
    with st.container(border=True, key="rec_top" if top else f"rec_card_{cid}"):
        head, score_col = st.columns([2.6, 1.2], vertical_alignment="center")
        with head:
            tags = badges([rec["category"]], "blue")
            if top:
                tags = ":orange-badge[:material/star: Highest score for your answers] " + tags
            st.markdown(tags)
            st.markdown(f"### {rec['rank']}. {rec['career_title']}")
        with score_col, st.container(horizontal=True, vertical_alignment="center", gap="small"):
            ring(rec["score"] / 100, f"{rec['score']:.1f}", size=62,
                 label_text=f"Compatibility score {rec['score']:.1f} out of 100")
            st.metric("Compatibility score", f"{rec['score']:.1f} / 100", width="content")

        matched_col, missing_col = st.columns(2)
        with matched_col:
            label("Matched skills")
            st.markdown(have_badges(rec["matched_required_skills"] + rec["matched_preferred_skills"],
                                    empty="No matched skills yet"))
        with missing_col:
            label("Missing skills")
            st.markdown(f"{missing_badges(rec['missing_required_skills'], empty='No required skill missing')} "
                        f"{optional_badges(rec['missing_preferred_skills'], empty='')}".strip())
            if rec["missing_preferred_skills"]:
                st.caption("Gray tags are optional preferred skills.")

        label("Why this career")
        st.markdown("\n".join(f"- {r}" for r in rec["reasons"]))
        st.markdown(f"{interest_badges(rec['matched_interests'], empty='No matched interests')} "
                    f":gray-badge[:material/school: Typical entry {education_label(rec['education']['career_level'])}]")
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
            st.dataframe(rows, hide_index=True, width="stretch", column_config=BREAKDOWN_COLUMNS)
            st.caption("Points add up to the compatibility score.")

        with st.container(horizontal=True, horizontal_alignment="right"):
            if st.button("View career details", key=f"explore_{cid}", icon=":material/open_in_new:"):
                st.session_state[EXPLORER_CAREER_KEY] = cid
                st.switch_page(EXPLORER_PAGE)
            if st.button("Analyze my skill gap", key=f"gap_{cid}", type="primary", icon=":material/school:"):
                select_career(cid)
                st.switch_page(SKILL_GAP_PAGE)
