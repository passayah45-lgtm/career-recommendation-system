# Skill gap and learning resources from the Phase 3 analyze_skill_gap() service

import streamlit as st

from src.services.catalog import UnknownCareerError
from src.services.profiles import ProfileValidationError
from src.services.recommendations import recommend
from src.services.skill_gap import analyze_skill_gap
from src.ui.charts import coverage_chart
from src.ui.components import (
    ASSESSMENT_PAGE, badges, have_badges, label, missing_badges, optional_badges, page_setup, resource_card,
    sidebar_profile_summary,
)
from src.ui.state import SELECTED_CAREER_KEY, get_catalog, get_profile, get_top_k, select_career
from src.ui.views import career_label, education_label, resource_rows

page_setup("Skill-Gap Analysis", eyebrow="Step 3 of 3",
           subtitle="Compare your skills with one career, then close the gaps with free learning resources.")
catalog = get_catalog()
profile = get_profile()
careers_by_id = {c.career_id: c for c in catalog.careers}

if not profile:
    st.info("You have no saved assessment, so every skill is shown as missing. "
            "Complete the assessment for a personal analysis.", icon=":material/info:")
    st.page_link(ASSESSMENT_PAGE, label="Go to the Career Assessment", icon=":material/arrow_forward:")

recommended_ids = []
if profile:
    try:
        recs = recommend(profile, catalog, top_k=get_top_k())["recommendations"]
        recommended_ids = [r["career_id"] for r in recs]
    except (ProfileValidationError, ValueError) as exc:
        st.error(f"Your saved assessment could not be used: {exc}.", icon=":material/error:")

current = st.session_state.get(SELECTED_CAREER_KEY)
choices = ["My recommended careers", "All careers"] if recommended_ids else ["All careers"]
start_on_all = current is not None and current in careers_by_id and current not in recommended_ids

with st.container(border=True, key="toolbar"):
    src_col, career_col = st.columns([1, 1.6], vertical_alignment="bottom")
    source = src_col.radio("Choose from", choices, horizontal=True,
                           index=len(choices) - 1 if start_on_all else 0)
    option_ids = recommended_ids if source == "My recommended careers" else [c.career_id for c in catalog.careers]
    if current not in option_ids:
        current = option_ids[0]
    career_id = career_col.selectbox("Career", options=option_ids, index=option_ids.index(current),
                                     format_func=lambda cid: career_label(careers_by_id[cid]))
select_career(career_id)
sidebar_profile_summary(profile)

try:
    gap = analyze_skill_gap(profile or {}, career_id, catalog)
except (UnknownCareerError, ProfileValidationError) as exc:
    st.error(f"The skill gap could not be calculated: {exc}", icon=":material/error:")
    st.stop()


def pct(value):
    return "Not applicable" if value is None else f"{value * 100:.0f}%"


career = careers_by_id[career_id]
st.markdown(f"#### {gap['career_title']}")
st.markdown(f"{badges([career.category], 'gray')} "
            f":gray-badge[:material/school: Typical entry {education_label(career.education_level)}]")

with st.container():
    m1, m2, m3 = st.columns(3)
    with m1, st.container(border=True, key="card_required", height="stretch"):
        st.metric("Required skill coverage", pct(gap["required_coverage"]))
        st.progress(gap["required_coverage"] or 0.0)
    with m2, st.container(border=True, key="card_preferred", height="stretch"):
        st.metric("Preferred skill coverage", pct(gap["preferred_coverage"]))
        st.progress(gap["preferred_coverage"] or 0.0)
    with m3, st.container(border=True, key="card_missing", height="stretch"):
        st.metric("Missing required skills", len(gap["missing_required_skills"]))
        st.caption("Optional skills are not counted here.")

if gap["meets_all_required"]:
    st.success("You have every required skill for this career in the dataset.", icon=":material/check_circle:")

skills_col, chart_col = st.columns([1.4, 1])
with skills_col, st.container(border=True, key="panel_skills", height="stretch"):
    label("Skills you already have")
    st.markdown(have_badges(gap["have_required_skills"] + gap["have_preferred_skills"]))
    label("Missing required skills")
    st.markdown(missing_badges(gap["missing_required_skills"]))
    label("Missing preferred skills (optional)")
    st.markdown(optional_badges(gap["missing_preferred_skills"]))
    st.caption("Preferred skills help but are not essential for this career.")
    if gap["unknown_skills"]:
        st.caption(f"Not in the dataset, so not compared: {', '.join(gap['unknown_skills'])}.")
with chart_col, st.container(border=True, key="panel_chart", height="stretch"):
    st.plotly_chart(coverage_chart(gap, height=300), width="stretch", config={"displayModeBar": False})

st.subheader("Learning resources", anchor=False)
st.caption("Grouped by missing skill. Each card shows the provider, level, cost and how its link was checked.")

TABLE_COLUMNS = {
    "URL": st.column_config.LinkColumn("Link", display_text="Open resource"),
    "Free": st.column_config.CheckboxColumn("Free"),
}


def resource_group(entries, gap_type, empty_text):
    if not entries:
        st.caption(empty_text)
        return
    for entry in entries:
        with st.container(border=True, key=f"panel_{gap_type}_{entry['skill'].replace(' ', '_')}"):
            tag = missing_badges([entry["skill"]]) if gap_type == "required" else optional_badges([entry["skill"]])
            st.markdown(tag)
            if not entry["resources"]:
                st.caption("No resource in the catalogue for this skill yet.")
            for r in entry["resources"]:
                resource_card(r, f"{gap_type}_{r['resource_id']}")
    with st.expander("Table view"):
        st.dataframe(resource_rows(entries, gap_type), hide_index=True, width="stretch", column_config=TABLE_COLUMNS)


required_tab, optional_tab = st.tabs([
    f"Required gaps ({len(gap['resources']['required'])})",
    f"Optional gaps ({len(gap['resources']['preferred'])})",
])
with required_tab:
    resource_group(gap["resources"]["required"], "required", "No missing required skills.")
with optional_tab:
    resource_group(gap["resources"]["preferred"], "preferred", "No missing preferred skills.")

st.info(gap["resource_note"], icon=":material/verified_user:")

if gap["learning_goals"]:
    with st.container(border=True, key="panel_goals"):
        label("What you would learn to do in this career")
        st.markdown("\n".join(f"- {g}" for g in gap["learning_goals"]))
