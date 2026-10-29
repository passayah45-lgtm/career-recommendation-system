# Streamlit session state and cached catalog loading
# Session state only holds the current learner's temporary input, nothing is stored on disk

import os

import streamlit as st

from src.services.catalog import DatasetError, load_catalog
from src.services.feedback import (
    INTERESTED, NOT_FOR_ME, QUERY_INTERESTED, QUERY_NOT_FOR_ME, feedback_from_query, feedback_to_query,
)
from src.services.roadmap import progress_from_query, progress_to_query

DATA_DIR_ENV = "CAREER_DATA_DIR"
PROFILE_KEY = "profile_input"
TOP_K_KEY = "top_k"
SELECTED_CAREER_KEY = "selected_career_id"
EXPLORER_CAREER_KEY = "explorer_career_id"
FEEDBACK_KEY = "career_feedback"
# Roadmap progress {career_id: {skill: status}} and the career shown on the roadmap page
ROADMAP_KEY = "roadmap_progress"
ROADMAP_CAREER_KEY = "roadmap_career_id"
QUERY_PROGRESS = "progress"
# Which list the Recommendations page shows: new careers, Interested or Not for me
LIST_VIEW_KEY = "career_list_view"
LIST_VIEWS = ("recommendations", "interested", "not_for_me")
FLASH_KEY = "career_flash"
# Set after the first run of a session, so the lists are read from the address bar only once
URL_CHECKED_KEY = "feedback_url_checked"
DEFAULT_TOP_K = 5
STATE_KEYS = (PROFILE_KEY, TOP_K_KEY, SELECTED_CAREER_KEY, EXPLORER_CAREER_KEY, FEEDBACK_KEY, ROADMAP_KEY,
              ROADMAP_CAREER_KEY)


@st.cache_resource(show_spinner="Loading career data...")
def _cached_catalog(data_dir):
    # The Catalog is read-only, so one shared copy per data folder is safe
    return load_catalog(data_dir or None)


def get_catalog():
    # Returns the catalog, or shows an error and stops the page when the data cannot be used
    data_dir = os.environ.get(DATA_DIR_ENV, "")
    try:
        catalog = _cached_catalog(data_dir)
    except DatasetError as exc:
        st.error("The career data could not be loaded, so the app cannot run. "
                 "Run `python -m src.data.validation` to see what is wrong.")
        st.caption(str(exc))
        st.stop()
    sync_feedback_with_url([c.career_id for c in catalog.careers], catalog)
    return catalog


def sync_feedback_with_url(career_ids, catalog=None):
    # A refreshed tab starts a new session: its first run restores the lists from the address bar
    # Every run then writes the current lists back, because switching pages clears the address bar
    if not st.session_state.get(URL_CHECKED_KEY):
        st.session_state[URL_CHECKED_KEY] = True
        if FEEDBACK_KEY not in st.session_state:
            restored = feedback_from_query({k: st.query_params.get(k) for k in (QUERY_INTERESTED, QUERY_NOT_FOR_ME)},
                                           career_ids)
            if restored:
                st.session_state[FEEDBACK_KEY] = restored
        if catalog is not None and ROADMAP_KEY not in st.session_state:
            progress = progress_from_query(st.query_params.get(QUERY_PROGRESS), catalog)
            if progress:
                st.session_state[ROADMAP_KEY] = progress
    wanted = feedback_to_query(get_feedback())
    encoded = progress_to_query(get_progress())
    if encoded:
        wanted[QUERY_PROGRESS] = encoded
    for name in (QUERY_INTERESTED, QUERY_NOT_FOR_ME, QUERY_PROGRESS):
        if name in wanted and st.query_params.get(name) != wanted[name]:
            st.query_params[name] = wanted[name]
        elif name not in wanted and name in st.query_params:
            del st.query_params[name]


@st.cache_resource(show_spinner="Training the comparison models (once per server)...")
def _cached_live_models(data_dir):
    # Trained once per server process and shared read-only by every visitor, never retrained per view
    from src.evaluation.dataset import load_profiles
    from src.ml.comparison import train_live_models
    catalog = _cached_catalog(data_dir)
    profiles = load_profiles([c.career_id for c in catalog.careers])
    return train_live_models(profiles, catalog)


def get_live_models():
    # Returns (models, None) or (None, error message); the rest of the page keeps working on failure
    try:
        return _cached_live_models(os.environ.get(DATA_DIR_ENV, "")), None
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


def get_profile():
    return st.session_state.get(PROFILE_KEY)


def set_profile(profile):
    st.session_state[PROFILE_KEY] = profile


def get_feedback():
    # Career id to 1 (interested) or -1 (not for me), for this session only
    return dict(st.session_state.get(FEEDBACK_KEY, {}))


def set_feedback(career_id, value):
    feedback = get_feedback()
    if value is None:
        feedback.pop(career_id, None)
    else:
        feedback[career_id] = value
    st.session_state[FEEDBACK_KEY] = feedback


def decide(career_id, value, title=None):
    # Button callback: moves a career into a list, to the other list, or out of both
    set_feedback(career_id, value)
    name = title or career_id
    if value == INTERESTED:
        st.session_state[FLASH_KEY] = f"{name} moved to Interested."
    elif value == NOT_FOR_ME:
        st.session_state[FLASH_KEY] = f"{name} moved to Not for me."
    else:
        st.session_state[FLASH_KEY] = f"{name} removed from your lists."


def show_list(view):
    # Button callback for links to one of the lists on the Recommendations page
    st.session_state[LIST_VIEW_KEY] = view


def get_progress():
    # Roadmap progress for every career, for this session only
    return {cid: dict(steps) for cid, steps in st.session_state.get(ROADMAP_KEY, {}).items()}


def set_progress(progress):
    st.session_state[ROADMAP_KEY] = {cid: dict(steps) for cid, steps in progress.items()}


def replace_session(profile, feedback, roadmaps=None):
    st.session_state[PROFILE_KEY] = profile
    st.session_state[FEEDBACK_KEY] = dict(feedback)
    if roadmaps is not None:
        set_progress(roadmaps)


def get_top_k():
    return st.session_state.get(TOP_K_KEY, DEFAULT_TOP_K)


def select_career(career_id):
    st.session_state[SELECTED_CAREER_KEY] = career_id


def reset_assessment():
    for key in STATE_KEYS:
        st.session_state.pop(key, None)
