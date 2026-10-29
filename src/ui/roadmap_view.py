# Streamlit presentation of the skill development roadmap; all calculations live in src/services/roadmap.py

import streamlit as st

from src.services.feedback import NOT_FOR_ME, split_lists
from src.services.recommendations import recommend
from src.services.roadmap import (
    COMPLETED, IN_PROGRESS, OPTIONAL, PREREQUISITE, REQUIRED, STATUS_LABELS, STATUSES, add_skill_to_profile,
    delete_roadmap, set_step_status,
)
from src.ui.components import badges, have_badges, label, missing_badges, optional_badges, resource_row
from src.ui.state import (
    FLASH_KEY, PROFILE_KEY, ROADMAP_CAREER_KEY, get_catalog, get_feedback, get_profile, get_progress, get_top_k,
    set_progress,
)

CONFIRM_SKILL_KEY = "roadmap_confirm_skill"
CONFIRM_DELETE_KEY = "roadmap_confirm_delete"
KIND_BADGES = {
    REQUIRED: ":orange-badge[:material/priority_high: Required]",
    OPTIONAL: ":gray-badge[:material/add: Optional]",
    PREREQUISITE: ":violet-badge[:material/account_tree: Prerequisite]",
}
STATUS_ICONS = {"not_started": ":material/radio_button_unchecked:", IN_PROGRESS: ":material/pending:",
                COMPLETED: ":material/check_circle:"}


def career_options(profile, catalog):
    # Ordered {career_id: group label}: Interested first, then recommendations, then other saved roadmaps
    feedback = get_feedback()
    interested, not_for_me = split_lists(feedback)
    options = {cid: "Interested" for cid in interested}
    if profile:
        try:
            recs = recommend(profile, catalog, top_k=None)["recommendations"]
        except ValueError:
            recs = []
        top = [r["career_id"] for r in recs if r["career_id"] not in feedback][:get_top_k()]
        for cid in top:
            options.setdefault(cid, "Recommended")
    for cid in get_progress():
        options.setdefault(cid, "Not for me, progress kept" if cid in not_for_me else "Saved roadmap")
    current = st.session_state.get(ROADMAP_CAREER_KEY)
    known = {c.career_id for c in catalog.careers}
    if current in known:
        options.setdefault(current, "Selected career")
    return options


def step_slug(career_id, skill):
    return f"{career_id}_{skill.replace(' ', '_')}"


def step_widget_key(career_id, skill):
    return f"status_{step_slug(career_id, skill)}"


def on_status_change(career_id, skill, key):
    set_progress(set_step_status(get_progress(), career_id, skill, st.session_state[key]))


def ask_confirm(career_id, skill):
    st.session_state[CONFIRM_SKILL_KEY] = (career_id, skill)


def cancel_confirm():
    st.session_state.pop(CONFIRM_SKILL_KEY, None)


def confirm_learned(skill):
    # Only reached through the explicit confirmation button; the existing pipeline then recalculates everything
    st.session_state[PROFILE_KEY] = add_skill_to_profile(get_profile(), skill, get_catalog())
    st.session_state.pop(CONFIRM_SKILL_KEY, None)
    st.session_state[FLASH_KEY] = f"{skill} added to your profile. Skill gaps and recommendations were recalculated."


def confirm_delete(career_id, title):
    set_progress(delete_roadmap(get_progress(), career_id))
    st.session_state.pop(CONFIRM_DELETE_KEY, None)
    st.session_state[FLASH_KEY] = f"Roadmap progress for {title} deleted."


def overview(roadmap):
    with st.container(border=True, key="card_roadmap_overview"):
        st.markdown(f"### {roadmap['career_title']}")
        st.markdown(badges([roadmap["category"]], "blue"))
        c1, c2, c3, c4 = st.columns(4)
        fit = roadmap["fit"]
        if fit:
            c1.metric("Compatibility score", f"{fit['score']:.1f} / 100",
                      help="Ranks careers by how well your profile matches the dataset. It is not a probability of "
                           "being hired or of success.")
        else:
            c1.metric("Compatibility score", "No assessment")
        c2.metric("Required skills you have", f"{len(roadmap['have_required_skills'])} of {roadmap['required_total']}")
        c3.metric("Required skills to learn", len(roadmap["missing_required_skills"]))
        c4.metric("Optional skills to learn", len(roadmap["missing_preferred_skills"]))
        if fit:
            st.caption(f"Rank {fit['rank']} of {fit['careers_ranked']} careers by the formula. The score is not a "
                       "probability of employment or success.")


def progress_panel(roadmap):
    p = roadmap["progress"]
    with st.container(border=True, key="card_roadmap_progress"):
        label("Roadmap progress")
        if not p["total_steps"]:
            st.success("You already have every required and optional skill listed for this career. There is nothing "
                       "to add to this roadmap.", icon=":material/check_circle:")
            return
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Steps", p["total_steps"])
        c2.metric("Completed", p["completed"])
        c3.metric("In progress", p["in_progress"])
        c4.metric("Not started", p["not_started"])
        st.progress(p["completion_percent"] / 100,
                    text=f"{p['completion_percent']:.0f}% of steps marked completed")
        st.caption(roadmap["mastery_note"])


def skill_groups(roadmap):
    have = roadmap["have_required_skills"] + roadmap["have_preferred_skills"]
    c1, c2, c3 = st.columns(3)
    with c1, st.container(border=True, key="card_group_have", height="stretch"):
        label(f"Skills I already have ({len(have)})")
        st.markdown(have_badges(have, empty="None of this career's skills yet"))
    with c2, st.container(border=True, key="card_group_required", height="stretch"):
        label(f"Required skills to learn ({len(roadmap['missing_required_skills'])})")
        st.markdown(missing_badges(roadmap["missing_required_skills"], empty="None, all required skills met"))
    with c3, st.container(border=True, key="card_group_optional", height="stretch"):
        label(f"Optional skills for later ({len(roadmap['missing_preferred_skills'])})")
        st.markdown(optional_badges(roadmap["missing_preferred_skills"], empty="None"))


def step_card(roadmap, step, has_profile):
    cid, skill = roadmap["career_id"], step["skill"]
    key, slug = step_widget_key(cid, skill), step_slug(cid, skill)
    with st.container(border=True, key=f"card_step_{slug}"):
        head, status_col = st.columns([1.6, 1.4], vertical_alignment="center")
        with head:
            st.markdown(f"#### {STATUS_ICONS[step['status']]} Step {step['step']}: {skill}")
            st.markdown(KIND_BADGES[step["kind"]])
        with status_col:
            # Set every run so the control always shows the saved status, then changed only by the learner
            st.session_state[key] = step["status"]
            st.segmented_control("Progress", options=list(STATUSES), key=key, required=True,
                                 format_func=lambda s: STATUS_LABELS[s], on_change=on_status_change,
                                 args=(cid, skill, key), width="stretch")
        label("Why it matters")
        st.markdown("\n".join(f"- {line}" for line in step["why"]))
        if step["prerequisites"]:
            parts = [f"{p['skill']} ({'you have it' if p['have'] else 'not yet'})" for p in step["prerequisites"]]
            st.caption(":material/account_tree: Prerequisites: " + ", ".join(parts))
        else:
            st.caption(":material/account_tree: Prerequisites: none recorded in the dataset.")
        label("Learning resource")
        if step["resources"]:
            for resource in step["resources"]:
                resource_row(resource)
        if step["resource_note"]:
            st.caption(f":material/info: {step['resource_note']}")
        pending = st.session_state.get(CONFIRM_SKILL_KEY) == (cid, skill)
        if pending:
            st.warning(f"Add **{skill}** to your profile? Your skill gaps and recommendations will be recalculated. "
                       "Confirm only if you can now use this skill.", icon=":material/help:")
            with st.container(horizontal=True):
                st.button("Yes, add it to my profile", key=f"yes_{slug}", type="primary", icon=":material/check:",
                          on_click=confirm_learned, args=(skill,))
                st.button("Cancel", key=f"cancel_{slug}", on_click=cancel_confirm)
        elif has_profile:
            with st.container(horizontal=True, horizontal_alignment="right"):
                st.button("I have learned this skill", key=f"learned_{slug}", icon=":material/verified:",
                          on_click=ask_confirm, args=(cid, skill),
                          help="Adds the skill to your profile after you confirm")
        else:
            st.caption("Complete the assessment to add learned skills to your profile.")


def manage_panel(roadmap):
    cid, title = roadmap["career_id"], roadmap["career_title"]
    if cid not in get_progress():
        return
    with st.expander(":material/settings: Manage this roadmap"):
        st.caption("Progress is kept even if you remove the career from your lists or mark it Not for me. Delete it "
                   "here only if you no longer want it.")
        if st.session_state.get(CONFIRM_DELETE_KEY) == cid:
            st.warning(f"Delete all saved progress for {title}? This cannot be undone.", icon=":material/warning:")
            with st.container(horizontal=True):
                st.button("Yes, delete progress", key="confirm_delete_roadmap", type="primary",
                          on_click=confirm_delete, args=(cid, title))
                st.button("Cancel", key="cancel_delete_roadmap",
                          on_click=lambda: st.session_state.pop(CONFIRM_DELETE_KEY, None))
        else:
            st.button("Delete this roadmap's progress", key="delete_roadmap", icon=":material/delete:",
                      on_click=lambda: st.session_state.__setitem__(CONFIRM_DELETE_KEY, cid))


def roadmap_section(roadmap, has_profile):
    if get_feedback().get(roadmap["career_id"]) == NOT_FOR_ME:
        st.info("You marked this career Not for me. Its roadmap and progress are kept until you delete them.",
                icon=":material/thumb_down:")
    overview(roadmap)
    progress_panel(roadmap)
    st.subheader("Current skills and skill gaps", anchor=False)
    skill_groups(roadmap)
    if roadmap["steps"]:
        st.subheader("Ordered learning plan", anchor=False)
        st.caption(f":material/route: {roadmap['order_note']}")
        for step in roadmap["steps"]:
            step_card(roadmap, step, has_profile)
    outside = roadmap["saved_outside_steps"]
    if outside:
        st.caption(f":material/history: Saved statuses kept for skills no longer in this plan, for example skills "
                   f"now in your profile: {', '.join(outside)}.")
    manage_panel(roadmap)
