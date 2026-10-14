# Skill gap and learning resources from the Phase 3 analyze_skill_gap() service

import streamlit as st

from src.services.catalog import UnknownCareerError
from src.services.profiles import ProfileValidationError
from src.services.recommendations import recommend
from src.services.skill_gap import analyze_skill_gap
from src.ui.components import (
    ASSESSMENT_PAGE, badges, have_badges, label, missing_badges, optional_badges, page_setup, resource_card, ring,
    sidebar_profile_summary,
)
from src.ui.state import SELECTED_CAREER_KEY, get_catalog, get_profile, get_top_k, select_career
from src.ui.views import career_label, education_label, resource_rows

page_setup("Skill-Gap Analysis", eyebrow="Step 3 of 3",
           subtitle="See which skills you have, which ones are missing, and free resources to help you learn.")
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
have_req, miss_req = gap["have_required_skills"], gap["missing_required_skills"]
have_pref, miss_pref = gap["have_preferred_skills"], gap["missing_preferred_skills"]
n_req, n_pref = len(have_req) + len(miss_req), len(have_pref) + len(miss_pref)

st.markdown(f"#### {gap['career_title']}")
st.markdown(f"{badges([career.category], 'blue')} "
            f":gray-badge[:material/school: Typical entry {education_label(career.education_level)}]")


def coverage_card(column, key, title, value, have, total):
    # Ring, metric and an "x of y skills" line for one coverage figure
    with column, st.container(border=True, key=f"card_{key}", height="stretch"):
        with st.container(horizontal=True, vertical_alignment="center", gap="small"):
            st.metric(title, pct(value), width="content")
            ring(value, pct(value) if value is not None else "n/a", size=58, label_text=f"{title} {pct(value)}")
        st.caption(f"{have} of {total} skills" if total else "This career lists no such skills.")


with st.container(key="coverage"):
    c1, c2, c3, c4 = st.columns(4)
    coverage_card(c1, "required", "Required skill coverage", gap["required_coverage"], len(have_req), n_req)
    coverage_card(c2, "preferred", "Preferred skill coverage", gap["preferred_coverage"], len(have_pref), n_pref)
    coverage_card(c3, "overall", "Overall skill coverage", gap["overall_skill_coverage"],
                  len(have_req) + len(have_pref), n_req + n_pref)
    with c4, st.container(border=True, key="card_missing", height="stretch"):
        st.metric("Missing required skills", len(miss_req))
        st.caption("Optional preferred skills are not counted here.")

if gap["meets_all_required"]:
    st.success("You have every required skill for this career in the dataset.", icon=":material/check_circle:")
if gap["unknown_skills"]:
    st.caption(f"Not in the dataset, so not compared: {', '.join(gap['unknown_skills'])}.")

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
            st.markdown(f"{tag} :gray[{len(entry['resources'])} learning resource(s)]")
            if not entry["resources"]:
                st.caption("No resource in the catalogue for this skill yet.")
            for r in entry["resources"]:
                resource_card(r, f"{gap_type}_{r['resource_id']}")
    with st.expander("Table view"):
        st.dataframe(resource_rows(entries, gap_type), hide_index=True, width="stretch", column_config=TABLE_COLUMNS)


with st.container(border=True, key="panel_gaps"):
    required_tab, optional_tab, all_tab = st.tabs([
        f"Required skills ({len(miss_req)} missing)",
        f"Preferred skills ({len(miss_pref)} missing)",
        f"All skills ({n_req + n_pref})",
    ])
    with required_tab:
        st.markdown("**:red[:material/error:] Missing required skills**")
        st.caption("These skills are needed for this career and are not in your current profile.")
        resource_group(gap["resources"]["required"], "required", "No missing required skills.")
    with optional_tab:
        st.markdown("**:gray[:material/add_circle:] Missing preferred skills (optional)**")
        st.caption("Preferred skills help but are not essential for this career.")
        resource_group(gap["resources"]["preferred"], "preferred", "No missing preferred skills.")
    with all_tab:
        label("Skills you already have")
        st.markdown(have_badges(have_req + have_pref))
        label("Missing required skills")
        st.markdown(missing_badges(miss_req))
        label("Missing preferred skills (optional)")
        st.markdown(optional_badges(miss_pref))

st.info(gap["resource_note"], icon=":material/verified_user:")

if gap["learning_goals"]:
    with st.container(border=True, key="panel_goals"):
        label("What you would learn to do in this career")
        st.markdown("\n".join(f"- {g}" for g in gap["learning_goals"]))
