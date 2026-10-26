# Shows ranked careers from the Phase 3 recommend() service

import streamlit as st

from src.services.feedback import INTERESTED, NOT_FOR_ME, adapt_recommendations
from src.services.profiles import ProfileValidationError
from src.services.recommendations import recommend
from src.ui.components import (
    EXPLORER_PAGE, SKILL_GAP_PAGE, badges, have_badges, interest_badges, label, missing_badges,
    need_profile_message, optional_badges, page_setup, ring, score_disclaimer, session_data_panel,
    show_profile_warnings, sidebar_profile_summary,
)
from src.ui.state import (
    EXPLORER_CAREER_KEY, FEEDBACK_KEY, TOP_K_KEY, get_catalog, get_feedback, get_profile, get_top_k, select_career,
    set_feedback,
)
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
    result = recommend(profile, catalog, top_k=None)
except (ProfileValidationError, ValueError) as exc:
    st.error(f"Your saved assessment could not be used: {exc}. Please complete the assessment again.",
             icon=":material/error:")
    st.stop()

show_profile_warnings(result["warnings"])

feedback = get_feedback()
ranked, hidden = adapt_recommendations(result["recommendations"], catalog, feedback)
recommendations = ranked[:top_k]
if not recommendations:
    st.info("No careers were returned. Try adding more skills or interests.", icon=":material/info:")
    st.stop()

liked = sum(1 for v in feedback.values() if v == INTERESTED)
with st.container(border=True, key="feedback_bar"):
    if feedback:
        info_col, clear_col = st.columns([3, 1], vertical_alignment="center")
        info_col.markdown(f":material/tune: **Adapted to your feedback:** {liked} interested, {len(hidden)} not for me. "
                          "Similar careers move up or down, and each card shows by how much.")
        if clear_col.button("Clear my feedback", key="clear_feedback", icon=":material/backspace:"):
            st.session_state.pop(FEEDBACK_KEY, None)
            st.rerun()
    else:
        st.markdown(":material/tune: **Tell the app what you think.** Mark careers as *Interested* or *Not for me* "
                    "and the list adapts to you during this visit. Nothing is stored after you leave.")

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
            shown_score = rec["adjusted_score"]
            ring(shown_score / 100, f"{shown_score:.1f}", size=62,
                 label_text=f"Compatibility score {shown_score:.1f} out of 100")
            delta = f"{rec['feedback_adjustment']:+.1f} from your feedback" if rec["feedback_adjustment"] else None
            st.metric("Compatibility score", f"{shown_score:.1f} / 100", delta=delta, width="content")

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

        if rec["feedback_reasons"]:
            label("How your feedback changed this score")
            st.markdown("\n".join(f"- {r}" for r in rec["feedback_reasons"]))
            st.caption(f"Formula score {rec['formula_score']:.1f} plus feedback {rec['feedback_adjustment']:+.1f} "
                       f"gives {rec['adjusted_score']:.1f}.")

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
            st.caption("Points add up to the formula score. Feedback adjustments are shown above the breakdown.")

        with st.container(horizontal=True, horizontal_alignment="right"):
            if rec["user_feedback"] == INTERESTED:
                st.markdown(":green-badge[:material/thumb_up: You are interested]")
                st.button("Undo", key=f"undo_{cid}", icon=":material/undo:", on_click=set_feedback, args=(cid, None))
            else:
                st.button("Interested", key=f"like_{cid}", icon=":material/thumb_up:",
                          on_click=set_feedback, args=(cid, INTERESTED))
                st.button("Not for me", key=f"dislike_{cid}", icon=":material/thumb_down:",
                          on_click=set_feedback, args=(cid, NOT_FOR_ME))
            if st.button("View career details", key=f"explore_{cid}", icon=":material/open_in_new:"):
                st.session_state[EXPLORER_CAREER_KEY] = cid
                st.switch_page(EXPLORER_PAGE)
            if st.button("Analyze my skill gap", key=f"gap_{cid}", type="primary", icon=":material/school:"):
                select_career(cid)
                st.switch_page(SKILL_GAP_PAGE)

if hidden:
    with st.expander(f":material/visibility_off: Careers you marked not for me ({len(hidden)})"):
        for rec in hidden:
            name_col, undo_col = st.columns([3, 1], vertical_alignment="center")
            name_col.markdown(f"**{rec['career_title']}** :gray-badge[{rec['category']}]")
            undo_col.button("Show again", key=f"unhide_{rec['career_id']}", icon=":material/undo:",
                            on_click=set_feedback, args=(rec["career_id"], None))

session_data_panel(profile, key="rec_session")
