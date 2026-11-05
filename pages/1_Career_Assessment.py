# Collects the learner profile and validates it through the service layer

import streamlit as st

from src.data.interest_taxonomy import CURRENT_TAXONOMY, SOFT_SELECTION_LIMIT, TERMS_BY_KEY, label_for
from src.data.validation import EDUCATION_LEVELS
from src.services.profiles import resolve_interests
from src.services.profiles import MAX_EXPERIENCE_YEARS, ProfileValidationError
from src.services.recommendations import profile_from_input
from src.ui.assessment_assistant import render_assessment_assistant
from src.ui.components import (
    RECOMMENDATIONS_PAGE, have_badges, page_setup, reset_button, section, session_data_panel,
    sidebar_profile_summary,
)
from src.ui.interest_picker import render_interest_picker, split_selection
from src.ui.skill_picker import render_skill_picker, skill_groups, split_entries
from src.ui.state import get_catalog, get_profile, set_profile
from src.ui.text import plain_markdown
from src.ui.views import SKILL_TEXT_SPLIT, build_profile_input, education_label

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
saved_interests, saved_custom, saved_migrated, saved_retired = resolve_interests(saved.get("interests", []),
                                                                                 catalog.interests)
grouped_interests = catalog.interest_taxonomy == CURRENT_TAXONOMY
# Exchange of 4 November 2026 (owner decision): with the current interest list, the Skills section shows the 23
# official interests and the Interests section shows the 144 skills. The section never decides what a value is:
# every choice is saved by the catalogue it comes from, so interests stay interests and skills stay skills, and the
# engine, the weights and the saved session format are unchanged. Typed text keeps the meaning of its section:
# typed under Skills it is a skill (aliases apply), typed under Interests it is the student's own interest
exchanged = grouped_interests
if exchanged:
    groups = skill_groups(catalog)
    # Restore: catalogue skills go back to the Interests dropdown, other saved skills to the Other skills box,
    # official interests (including old names) to the Skills dropdown and the student's own interests, kept
    # exactly as saved, to the Interests dropdown as typed chips
    restore_skills = [s for s in dict.fromkeys(saved_skills) if s in groups]
    # A typed skill that contains a comma, semicolon or line break would be split by the Other skills box when the
    # answers are saved again, so it returns to section 1 as a chip and stays exactly as typed
    restore_typed_skills = [s for s in dict.fromkeys(saved_skills) if s not in groups and SKILL_TEXT_SPLIT.search(s)]
    other_text = ", ".join(s for s in saved_skills if s not in groups and s not in restore_typed_skills)
    restore_own_interests = list(saved_custom) + [old for old, _ in saved_retired]
    # Optional assistant (feature flag CRS_ASSESSMENT_ASSISTANT, off by default); draws nothing when it is off
    render_assessment_assistant(catalog)

# A bordered panel instead of a form: the interest picker must react while the student chooses
with st.container(border=True, key="panel_assessment"):
    if exchanged:
        section(1, "Your skills", f"This list shows the {len(TERMS_BY_KEY)} interests (kinds of work you enjoy). "
                "Each choice counts as an interest, 25% of the score. Type a skill and press Enter to add it as a "
                "skill, or use the Other skills box. Skills count for 70% of the score.",
                ":material/lightbulb:", "green")
        if saved_migrated or saved_retired:
            notes = [f"{old} became {label_for(new)}" for old, new in saved_migrated]
            notes += [f"{old} {note}" for old, note in saved_retired]
            st.info("Your saved answers used old interest names. " + ". ".join(notes) + ".",
                    icon=":material/update:")
        section1 = render_interest_picker(saved_interests, restore_typed_skills, as_skills=True)
        # Choices from the list are interests; text typed here is a skill
        section1_interests, section1_skills = split_selection(section1)
    else:
        section(1, "Your skills", f"Select from the {len(known_skills)} skills used by the careers, or type your own.",
                ":material/lightbulb:", "green")
        selected_skills = render_skill_picker(catalog, preselected)
    other_skills = st.text_area(
        "Other skills (optional)",
        value=other_text,
        placeholder="For example: ML, JS, CI/CD",
        height=80,
        help="Separate skills with commas. Common short names such as ML, JS, CI/CD and K8s are recognized. "
             "Skills that are not in the dataset are listed back to you and are not scored.",
    )

    st.divider()
    if exchanged:
        section(2, "Your interests", f"This list shows the {len(groups)} skills used by the careers, grouped by "
                "career field. Each choice counts as a skill you have. Type your own interest and press Enter: it "
                "is saved, and scored only when it names one of the interests in section 1.",
                ":material/favorite:", "red")
        section2 = render_skill_picker(catalog, restore_skills + restore_own_interests, as_interests=True)
        # Choices from the list are skills; text typed here is the student's own interest
        section2_skills, section2_typed = split_entries(section2, groups)
        typed_official, own_interests = split_selection(section2_typed)
        selected_skills = section2_skills + section1_skills
        interests = list(dict.fromkeys(section1_interests + typed_official)) + own_interests
    else:
        # Legacy interest list (older data folders): the original layout, unchanged
        section(2, "Your interests", "Choose the kinds of work you enjoy or would like to do. You do not need the "
                "skills yet. Skills are asked separately. Interests carry 25% of the score.",
                ":material/favorite:", "red")
        interests = st.multiselect(
            "Kinds of work that interest you",
            options=sorted(catalog.interests),
            default=[i for i in saved_interests if i in catalog.interests],
            placeholder="Type to search",
            select_all=False,
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

    submitted = st.button("Save my assessment", type="primary", icon=":material/arrow_forward:",
                          width="stretch", key="save_assessment")

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
                # Typed text is shown as plain characters, never as a link or image
                unknown = ", ".join(map(plain_markdown, report.unknown_skills))
                st.warning(f"These skills are not in the dataset: {unknown}.",
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
                    unknown = ", ".join(map(plain_markdown, report.unknown_skills))
                    st.warning(f"Not in the dataset, so not scored: {unknown}.",
                               icon=":material/warning:")
                if report.unknown_interests:
                    own = ", ".join(plain_markdown(i) for i in report.unknown_interests)
                    st.info(f"Your own interests were saved but are not scored: {own}.",
                            icon=":material/edit_note:")
                if report.duplicate_skills:
                    repeated = ", ".join(map(plain_markdown, report.duplicate_skills))
                    st.info(f"Counted once because they repeat another skill: {repeated}.",
                            icon=":material/content_copy:")
                st.page_link(RECOMMENDATIONS_PAGE, label="See my recommendations", icon=":material/arrow_forward:")
elif saved:
    st.info("You already have a saved assessment. Change the answers above and save again, or view your results.",
            icon=":material/info:")
    st.page_link(RECOMMENDATIONS_PAGE, label="See my recommendations", icon=":material/arrow_forward:")

if saved:
    reset_button(key="page_reset")

sidebar_profile_summary(get_profile())
