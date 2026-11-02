# Collects the learner profile and validates it through the service layer

import streamlit as st

from src.data.interest_taxonomy import (
    CURRENT_TAXONOMY, INTEREST_UPDATE_NOTICE, RIASEC_DESCRIPTIONS, SOFT_SELECTION_LIMIT, label_for, terms_by_group,
)
from src.data.validation import EDUCATION_LEVELS
from src.services.profiles import resolve_interests
from src.services.profiles import MAX_EXPERIENCE_YEARS, ProfileValidationError
from src.services.recommendations import profile_from_input
from src.ui.components import (
    RECOMMENDATIONS_PAGE, have_badges, page_setup, reset_button, section, session_data_panel,
    sidebar_profile_summary,
)
from src.ui.state import get_catalog, get_profile, set_profile
from src.ui.views import build_profile_input, education_label

page_setup("Career Assessment", eyebrow="Step 1 of 3",
           subtitle="Four short sections. Add at least one skill or one interest. "
                    "The more you add, the more useful your results will be.")
catalog = get_catalog()
saved = get_profile() or {}
session_data_panel(saved, key="assess_session", allow_download=bool(saved))

known_skills = sorted(catalog.known_skills)
saved_skills = saved.get("skills", [])
preselected = [s for s in saved_skills if s in catalog.known_skills]
other_text = ", ".join(s for s in saved_skills if s not in catalog.known_skills)
education_options = [None] + sorted(EDUCATION_LEVELS)
saved_level = saved.get("education_level")
# Saved answers may use old interest names; they are translated here so the form shows the current choices
saved_interests, _, saved_migrated, saved_retired = resolve_interests(saved.get("interests", []), catalog.interests)
grouped_interests = catalog.interest_taxonomy == CURRENT_TAXONOMY

with st.form("assessment_form"):
    section(1, "Your skills", f"Select from the {len(known_skills)} skills used by the careers, or type your own.",
            ":material/lightbulb:", "green")
    selected_skills = st.multiselect(
        "Skills you already have",
        options=known_skills,
        default=preselected,
        placeholder="Type to search, for example python or accounting",
        help="This list contains every skill used by the careers in the dataset.",
    )
    other_skills = st.text_area(
        "Other skills (optional)",
        value=other_text,
        placeholder="For example: ML, JS, CI/CD",
        height=80,
        help="Separate skills with commas. Common short names such as ML, JS, CI/CD and K8s are recognized. "
             "Skills that are not in the dataset are listed back to you and are not scored.",
    )

    st.divider()
    section(2, "Your interests", "Choose the kinds of work you enjoy or would like to do. You do not need the "
            "skills yet. Skills are asked separately. Interests carry 25% of the score.",
            ":material/favorite:", "red")
    if grouped_interests:
        st.info(INTEREST_UPDATE_NOTICE, icon=":material/new_releases:")
        st.caption(f"Choose up to {SOFT_SELECTION_LIMIT} that you enjoy most. Hover over the question mark next to "
                   "an interest for an explanation, an example and a related skill. The groups only help you read "
                   "the list. They do not change the score.")
        if saved_migrated or saved_retired:
            notes = [f"{old} became {label_for(new)}" for old, new in saved_migrated]
            notes += [f"{old} {note}" for old, note in saved_retired]
            st.info("Your saved answers used old interest names. " + ". ".join(notes) + ".",
                    icon=":material/update:")
        interests = []
        group_cols = st.columns(2)
        for n, (group, terms) in enumerate(terms_by_group().items()):
            with group_cols[n % 2]:
                st.markdown(f"**{group}**")
                st.caption(RIASEC_DESCRIPTIONS[group])
                for term in terms:
                    if st.checkbox(term.label, value=term.key in saved_interests, key=f"interest_{term.key}",
                                   help=f"{term.explanation}. Example: {term.example}. "
                                        f"Related skill (not the same thing): {term.related_skill}."):
                        interests.append(term.key)
    else:
        interests = st.multiselect(
            "Kinds of work that interest you",
            options=sorted(catalog.interests),
            default=[i for i in saved_interests if i in catalog.interests],
            placeholder="Type to search",
        )

    st.divider()
    section(3, "Education level", "Education has a 5% weight. It is never used to exclude a career.",
            ":material/school:", "blue")
    edu_col, scale_col = st.columns([1, 1.2])
    with edu_col:
        education = st.selectbox(
            "Highest education level completed",
            options=education_options,
            index=education_options.index(saved_level) if saved_level in education_options else 0,
            format_func=education_label,
        )
    with scale_col:
        st.caption("**Education scale**  \n" + "  \n".join(
            f"{level}: {meaning}" for level, meaning in sorted(EDUCATION_LEVELS.items())))
        st.caption("Equivalent experience counts. Levels describe typical entry in this dataset, "
                   "not legal requirements.")

    st.divider()
    section(4, "Work experience (optional, not scored)", "Shown for context only. It does not change the score.",
            ":material/work:", "orange")
    exp_col, note_col = st.columns([1, 1.2])
    with exp_col:
        experience = st.number_input(
            "Years of work experience",
            min_value=0, max_value=MAX_EXPERIENCE_YEARS, step=1,
            value=saved.get("experience_years"),
            placeholder="Leave empty if you prefer not to say",
        )
    with note_col:
        st.markdown(":gray-badge[:material/block: Not scored]")
        st.caption("The current dataset has no experience requirements, so this answer does not change the score.")

    submitted = st.form_submit_button("Save my assessment", type="primary", icon=":material/arrow_forward:",
                                      width="stretch")

with st.expander("Why there is no learning goals field"):
    st.markdown(
        "Each career lists learning goals, and you will see them in your results. "
        "They are written as free text, so the system cannot compare them reliably with your own goals. "
        "To keep the score honest, goals are shown but not matched."
    )

if submitted:
    raw = build_profile_input(selected_skills, other_skills, interests, education,
                              int(experience) if experience is not None else None)
    try:
        _, report = profile_from_input(raw, catalog)
    except ProfileValidationError as exc:
        st.error(f"Please check your answers: {exc}.", icon=":material/error:")
    else:
        if not report.recognized_skills and not report.recognized_interests:
            st.error("Add at least one skill from the list, or one interest, so the system has something to match.",
                     icon=":material/error:")
            if report.unknown_skills:
                st.warning(f"These skills are not in the dataset: {', '.join(report.unknown_skills)}.",
                           icon=":material/warning:")
        else:
            set_profile(raw)
            with st.container(border=True, key="panel_saved"):
                st.success("Assessment saved for this browser session.", icon=":material/check_circle:")
                st.markdown(f"**Recognized skills** {have_badges(report.recognized_skills)}")
                if len(report.recognized_interests) > SOFT_SELECTION_LIMIT:
                    st.warning(f"You chose {len(report.recognized_interests)} interests. Choosing more than "
                               f"{SOFT_SELECTION_LIMIT} gives points to many careers without narrowing your results. "
                               f"Consider keeping the {SOFT_SELECTION_LIMIT} you enjoy most. Your answers were saved.",
                               icon=":material/tune:")
                if report.unknown_skills:
                    st.warning(f"Not in the dataset, so not scored: {', '.join(report.unknown_skills)}.",
                               icon=":material/warning:")
                if report.duplicate_skills:
                    st.info(f"Counted once because they repeat another skill: {', '.join(report.duplicate_skills)}.",
                            icon=":material/content_copy:")
                st.page_link(RECOMMENDATIONS_PAGE, label="See my recommendations", icon=":material/arrow_forward:")
elif saved:
    st.info("You already have a saved assessment. Change the answers above and save again, or view your results.",
            icon=":material/info:")
    st.page_link(RECOMMENDATIONS_PAGE, label="See my recommendations", icon=":material/arrow_forward:")

if saved:
    reset_button(key="page_reset")

sidebar_profile_summary(get_profile())
