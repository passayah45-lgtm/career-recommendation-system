# Career Assessment Assistant panel on the assessment page (Phase 3, behind a feature flag, off by default)
# Uses the Phase 2 matcher in src/agents/profile_assistant.py; free, local Python only: no model, no network
# Suggestions never change anything until the student confirms them, and confirmed entries are only added to the
# two existing dropdowns; saving still happens through the unchanged "Save my assessment" button

import os
from dataclasses import asdict

import streamlit as st

from src.agents.profile_assistant import MAX_TEXT_CHARS, suggest_profile
from src.services.profiles import resolve_interests
from src.ui.interest_picker import PICKER_KEY
from src.ui.skill_picker import SKILL_PICKER_KEY
from src.ui.state import get_profile
from src.ui.text import plain_markdown

# Set to 1, true, yes or on to show the assistant; unset everywhere by default, including the live app
ASSISTANT_ENV = "CRS_ASSESSMENT_ASSISTANT"
TITLE = "Career Assessment Assistant"
DESCRIPTION = ("Describe your skills and interests in your own words. The assistant will suggest matching catalogue "
               "entries for you to review.")
# Every key the assistant keeps in session state starts with this prefix, so it can all be cleared together
STATE_PREFIX = "assistant_"
TEXT_KEY = "assistant_text"
RESULT_KEY = "assistant_result"
ROUND_KEY = "assistant_round"
FLASH_KEY = "assistant_flash"
ERROR_KEY = "assistant_error"
# Set by a reset or an upload; the description box is emptied at the start of the next run, before it is drawn,
# because the browser keeps a text box's value even after its session-state key is deleted
CLEAR_PENDING_KEY = "assistant_clear_pending"
# Entries already offered by low-confidence key-word matches start unticked; the student decides
PRESELECT = ("high", "medium")
CONFIDENCE_WORDS = {"high": "High confidence", "medium": "Medium confidence", "low": "Low confidence"}


def assistant_enabled():
    return os.environ.get(ASSISTANT_ENV, "").strip().lower() in ("1", "true", "yes", "on")


def clear_assistant_state():
    # Called when the assessment is reset or a saved session is uploaded: the description, the suggestions and the
    # ticks belong to the assessment being replaced, so nothing of them may stay visible (shared computers)
    for key in [k for k in st.session_state if str(k).startswith(STATE_PREFIX)]:
        del st.session_state[key]
    if assistant_enabled():
        st.session_state[CLEAR_PENDING_KEY] = True


def _already_chosen(widget, kind, catalog):
    # The dropdown's current choices; right after a reset or upload the panel is drawn before the dropdowns refill,
    # so their choices are then read from the saved answers exactly as the dropdowns restore them
    if widget in st.session_state:
        return list(st.session_state[widget])
    saved = get_profile() or {}
    if kind == "skill":
        return [s for s in saved.get("skills", []) if s in catalog.known_skills]
    return list(resolve_interests(saved.get("interests", []), catalog.interests)[0])


def _choice_key(round_id, kind, entry):
    return f"assistant_pick_{round_id}_{kind}_{entry}"


def _suggest(catalog):
    # Button callback: runs the matcher on the current text; the text itself is never stored anywhere else
    st.session_state.pop(FLASH_KEY, None)
    st.session_state.pop(ERROR_KEY, None)
    text = st.session_state.get(TEXT_KEY, "") or ""
    try:
        result = suggest_profile(text, catalog)
    except Exception:  # noqa: BLE001
        st.session_state.pop(RESULT_KEY, None)
        st.session_state[ERROR_KEY] = ("The assistant could not read this description. Your answers below are "
                                       "unchanged. You can still choose skills and interests yourself.")
        return
    st.session_state[ROUND_KEY] = st.session_state.get(ROUND_KEY, 0) + 1
    st.session_state[RESULT_KEY] = {
        "skills": [asdict(s) for s in result.suggested_skills],
        "interests": [asdict(s) for s in result.suggested_interests],
        "unmatched": list(result.unmatched_phrases),
        "truncated": result.text_truncated,
        "empty": not text.strip(),
    }


def _confirm():
    # Button callback: adds the ticked entries to the existing dropdowns, keeping everything already chosen
    result = st.session_state.get(RESULT_KEY)
    if not result:
        return
    round_id = st.session_state.get(ROUND_KEY, 0)
    # Section 1 lists the official interests, section 2 the catalogue skills (dropdown exchange of 4 November 2026)
    targets = {"interests": PICKER_KEY, "skills": SKILL_PICKER_KEY}
    added = {"skills": 0, "interests": 0}
    for group, widget in targets.items():
        current = list(st.session_state.get(widget, []))
        for item in result[group]:
            kind = "skill" if group == "skills" else "interest"
            if st.session_state.get(_choice_key(round_id, kind, item["entry"])) and item["entry"] not in current:
                current.append(item["entry"])
                added[group] += 1
        st.session_state[widget] = current
    # The description and the suggestions are cleared once used; nothing of them is kept
    st.session_state.pop(RESULT_KEY, None)
    st.session_state[TEXT_KEY] = ""
    st.session_state[FLASH_KEY] = added


def _count(n, noun):
    return f"{n} {noun}" + ("" if n == 1 else "s")


def _clear():
    st.session_state.pop(RESULT_KEY, None)
    st.session_state.pop(FLASH_KEY, None)
    st.session_state.pop(ERROR_KEY, None)
    st.session_state[TEXT_KEY] = ""


def _choices(items, kind, already, round_id):
    for item in items:
        key = _choice_key(round_id, kind, item["entry"])
        chosen = item["entry"] in already
        if key not in st.session_state:
            st.session_state[key] = (not chosen) and item["confidence"] in PRESELECT
        label = item["label"] + (" (already in your answers)" if chosen else "")
        st.checkbox(label, key=key, disabled=chosen)
        st.caption(f'{CONFIDENCE_WORDS[item["confidence"]]}. From your words "{plain_markdown(item["phrase"])}". '
                   f'{item["explanation"]}')


def render_assessment_assistant(catalog):
    # Draws nothing unless the feature flag is on, so the assessment page is unchanged by default
    if not assistant_enabled():
        return
    if st.session_state.pop(CLEAR_PENDING_KEY, False):
        st.session_state[TEXT_KEY] = ""
    with st.expander(f":material/auto_awesome: {TITLE}", expanded=False):
        with st.container(key="card_assessment_assistant"):
            st.markdown(DESCRIPTION)
            st.caption("Your description stays in this page only. It is not saved, sent anywhere or added to your "
                       "session file. Nothing changes until you confirm.")
            st.text_area("Your description", key=TEXT_KEY, max_chars=MAX_TEXT_CHARS, height=110,
                         placeholder="For example: I enjoy analysing data, teaching people Python and working with "
                                     "machine learning.")
            with st.container(horizontal=True, gap="small"):
                st.button("Suggest skills and interests", key="assistant_suggest", icon=":material/search:",
                          on_click=_suggest, args=(catalog,))
                st.button("Clear", key="assistant_clear", icon=":material/close:", on_click=_clear)

            if st.session_state.get(ERROR_KEY):
                st.error(st.session_state[ERROR_KEY], icon=":material/error:")
            flash = st.session_state.pop(FLASH_KEY, None)
            if flash is not None:
                st.success(f"Added {_count(flash['skills'], 'skill')} and {_count(flash['interests'], 'interest')} "
                           "to your answers below. Nothing is saved until you press Save my assessment.",
                           icon=":material/check_circle:")

            result = st.session_state.get(RESULT_KEY)
            if not result:
                return
            if result["empty"]:
                st.info("Write a few words about your skills and interests first.", icon=":material/edit:")
                return
            if result["truncated"]:
                st.warning(f"Only the first {MAX_TEXT_CHARS} characters were read.", icon=":material/warning:")
            round_id = st.session_state.get(ROUND_KEY, 0)
            if result["skills"]:
                st.markdown("**Suggested skills** :gray[(added to the list in section 2)]")
                _choices(result["skills"], "skill", _already_chosen(SKILL_PICKER_KEY, "skill", catalog), round_id)
            if result["interests"]:
                st.markdown("**Suggested interests** :gray[(added to the list in section 1)]")
                _choices(result["interests"], "interest", _already_chosen(PICKER_KEY, "interest", catalog),
                         round_id)
            if result["unmatched"]:
                st.markdown("**Words the assistant could not match**")
                for item in result["unmatched"]:
                    st.caption(f'"{plain_markdown(item["phrase"])}": {plain_markdown(item["reason"])}')
            if not result["skills"] and not result["interests"]:
                st.info("No catalogue skills or interests were found. You can still choose them yourself below.",
                        icon=":material/info:")
                return
            st.button("Add the ticked suggestions to my answers", key="assistant_confirm", type="primary",
                      icon=":material/playlist_add_check:", on_click=_confirm)
