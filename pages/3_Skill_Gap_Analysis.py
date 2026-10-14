# Skill gap and learning resources from the Phase 3 analyze_skill_gap() service

import streamlit as st

from src.services.catalog import UnknownCareerError
from src.services.profiles import ProfileValidationError
from src.services.recommendations import recommend
from src.services.skill_gap import analyze_skill_gap
from src.ui.charts import coverage_chart
from src.ui.components import ASSESSMENT_PAGE, chips, page_setup, sidebar_profile_summary
from src.ui.state import SELECTED_CAREER_KEY, get_catalog, get_profile, get_top_k, select_career
from src.ui.views import career_label, resource_rows

page_setup("Skill-Gap Analysis")
catalog = get_catalog()
profile = get_profile()
sidebar_profile_summary(profile)
careers_by_id = {c.career_id: c for c in catalog.careers}

if not profile:
    st.info("You have no saved assessment, so every skill is shown as missing. "
            "Complete the assessment for a personal analysis.")
    st.page_link(ASSESSMENT_PAGE, label="Go to the Career Assessment")

recommended_ids = []
if profile:
    try:
        recs = recommend(profile, catalog, top_k=get_top_k())["recommendations"]
        recommended_ids = [r["career_id"] for r in recs]
    except (ProfileValidationError, ValueError) as exc:
        st.error(f"Your saved assessment could not be used: {exc}.")

current = st.session_state.get(SELECTED_CAREER_KEY)
choices = ["My recommended careers", "All careers"] if recommended_ids else ["All careers"]
start_on_all = current is not None and current in careers_by_id and current not in recommended_ids
source = st.radio("Choose from", choices, horizontal=True, index=len(choices) - 1 if start_on_all else 0)
option_ids = recommended_ids if source == "My recommended careers" else [c.career_id for c in catalog.careers]

if current not in option_ids:
    current = option_ids[0]
career_id = st.selectbox("Career", options=option_ids, index=option_ids.index(current),
                         format_func=lambda cid: career_label(careers_by_id[cid]))
select_career(career_id)

try:
    gap = analyze_skill_gap(profile or {}, career_id, catalog)
except (UnknownCareerError, ProfileValidationError) as exc:
    st.error(f"The skill gap could not be calculated: {exc}")
    st.stop()


def pct(value):
    return "Not applicable" if value is None else f"{value * 100:.0f}%"


m1, m2, m3 = st.columns(3)
m1.metric("Required skill coverage", pct(gap["required_coverage"]))
m2.metric("Preferred skill coverage", pct(gap["preferred_coverage"]))
m3.metric("Missing required skills", len(gap["missing_required_skills"]))

if gap["meets_all_required"]:
    st.success("You have every required skill for this career in the dataset.")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**Skills you already have**")
    st.markdown(chips(gap["have_required_skills"] + gap["have_preferred_skills"]))
with c2:
    st.markdown("**Missing required skills**")
    st.markdown(chips(gap["missing_required_skills"]))
with c3:
    st.markdown("**Missing preferred skills (optional)**")
    st.markdown(chips(gap["missing_preferred_skills"]))
    st.caption("Preferred skills help but are not essential for this career.")

if gap["unknown_skills"]:
    st.caption(f"Not in the dataset, so not compared: {', '.join(gap['unknown_skills'])}.")

st.plotly_chart(coverage_chart(gap), width="stretch")

COLUMNS = {
    "URL": st.column_config.LinkColumn("Link", display_text="Open resource"),
    "Free": st.column_config.CheckboxColumn("Free"),
}


def resource_table(title, entries, gap_type, empty_text):
    st.subheader(title)
    if not entries:
        st.caption(empty_text)
        return
    st.dataframe(resource_rows(entries, gap_type), hide_index=True, width="stretch", column_config=COLUMNS)


resource_table("Resources for missing required skills", gap["resources"]["required"], "required",
               "No missing required skills.")
resource_table("Resources for missing preferred skills (optional)", gap["resources"]["preferred"], "preferred",
               "No missing preferred skills.")
st.info(gap["resource_note"] + " A link status of 'search index confirmed' means the page was found in search "
        "results, not that it was opened.")

if gap["learning_goals"]:
    st.markdown("**What you would learn to do in this career**")
    st.markdown("\n".join(f"- {g}" for g in gap["learning_goals"]))
