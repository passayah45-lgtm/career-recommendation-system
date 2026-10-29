# The learner's Interested and Not for me lists, shown apart from the main recommendations
# Display only; the lists live in session state and in the address bar (src/ui/state.py)

import streamlit as st

from src.services.feedback import INTERESTED, NOT_FOR_ME, split_lists
from src.ui.components import EXPLORER_PAGE, ROADMAP_PAGE, SKILL_GAP_PAGE, badges
from src.ui.state import (
    EXPLORER_CAREER_KEY, FLASH_KEY, LIST_VIEW_KEY, LIST_VIEWS, ROADMAP_CAREER_KEY, decide, select_career,
)
from src.ui.views import saved_list_rows

LIST_TITLES = {
    "recommendations": "Recommendations",
    "interested": "Interested",
    "not_for_me": "Not for me",
}
LIST_ICONS = {
    "recommendations": ":material/insights:",
    "interested": ":material/thumb_up:",
    "not_for_me": ":material/thumb_down:",
}
EMPTY_TEXT = {
    "interested": "No careers yet. Click Interested on a recommendation to keep it here.",
    "not_for_me": "No careers yet. Careers you mark Not for me are kept here, so you can reconsider them later.",
}


def show_flash():
    # Confirms the last move once, after the rerun that applied it
    message = st.session_state.pop(FLASH_KEY, None)
    if message:
        st.toast(message, icon=":material/check_circle:")


def list_view_control(counts, views=LIST_VIEWS):
    # Keyed control, so it keeps the open list when the counts in its labels change
    if st.session_state.get(LIST_VIEW_KEY) not in views:
        st.session_state[LIST_VIEW_KEY] = views[0]
    return st.segmented_control(
        "Your careers", options=list(views), key=LIST_VIEW_KEY, required=True, width="stretch",
        format_func=lambda v: f"{LIST_ICONS[v]} {LIST_TITLES[v]} ({counts[v]})",
    )


def open_details(career_id):
    st.session_state[EXPLORER_CAREER_KEY] = career_id
    st.switch_page(EXPLORER_PAGE)


def open_skill_gap(career_id):
    select_career(career_id)
    st.switch_page(SKILL_GAP_PAGE)


def saved_card(row, kind, has_profile):
    cid = row["career_id"]
    with st.container(border=True, key=f"card_saved_{cid}"):
        text_col, score_col = st.columns([2.4, 1.2], vertical_alignment="center")
        with text_col:
            st.markdown(f"#### {row['title']}")
            st.markdown(badges([row["category"]], "blue") + (" :green-badge[:material/thumb_up: Interested]"
                        if kind == "interested" else " :gray-badge[:material/thumb_down: Not for me]"))
        with score_col:
            if row["formula_score"] is not None:
                st.metric("Compatibility score", f"{row['formula_score']:.1f} / 100", width="content")
                st.caption(f"Rank {row['formula_rank']} by the formula, {row['matched_required']} of "
                           f"{row['required_total']} required skills")
            elif has_profile:
                st.caption("No score available.")
            else:
                st.caption("Complete the assessment to see your score.")
        with st.container(horizontal=True, horizontal_alignment="right"):
            if kind == "interested":
                st.button("Move to Not for me", key=f"to_not_{cid}", icon=":material/thumb_down:",
                          on_click=decide, args=(cid, NOT_FOR_ME, row["title"]))
            else:
                st.button("Move to Interested", key=f"to_int_{cid}", icon=":material/thumb_up:",
                          on_click=decide, args=(cid, INTERESTED, row["title"]))
            st.button("Remove from list", key=f"remove_{cid}", icon=":material/backspace:",
                      on_click=decide, args=(cid, None, row["title"]))
            if st.button("View career details", key=f"saved_explore_{cid}", icon=":material/open_in_new:"):
                open_details(cid)
            if st.button("Analyze my skill gap", key=f"saved_gap_{cid}", icon=":material/school:"):
                open_skill_gap(cid)
            if kind == "interested" and st.button("Plan my learning", key=f"saved_plan_{cid}", type="primary",
                                                  icon=":material/route:"):
                st.session_state[ROADMAP_CAREER_KEY] = cid
                st.switch_page(ROADMAP_PAGE)


def saved_list(kind, feedback, catalog, formula_recommendations=None, has_profile=False):
    interested, not_for_me = split_lists(feedback)
    ids = interested if kind == "interested" else not_for_me
    rows = saved_list_rows(ids, catalog, formula_recommendations)
    if not rows:
        st.info(EMPTY_TEXT[kind], icon=LIST_ICONS[kind])
        return
    if kind == "interested":
        st.caption("Careers you want to look at more closely. Open the details or the skill gap to check skills, "
                   "requirements and free learning resources.")
    else:
        st.caption("Careers you set aside. They no longer appear in your recommendations, and similar careers "
                   "move down a little.")
    for row in rows:
        saved_card(row, kind, has_profile)


def list_counts(feedback, new_count=0):
    interested, not_for_me = split_lists(feedback)
    return {"recommendations": new_count, "interested": len(interested), "not_for_me": len(not_for_me)}
