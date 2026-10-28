# Streamlit session state and cached catalog loading
# Session state only holds the current learner's temporary input, nothing is stored on disk

import os

import streamlit as st

from src.services.catalog import DatasetError, load_catalog

DATA_DIR_ENV = "CAREER_DATA_DIR"
PROFILE_KEY = "profile_input"
TOP_K_KEY = "top_k"
SELECTED_CAREER_KEY = "selected_career_id"
EXPLORER_CAREER_KEY = "explorer_career_id"
FEEDBACK_KEY = "career_feedback"
DEFAULT_TOP_K = 5
STATE_KEYS = (PROFILE_KEY, TOP_K_KEY, SELECTED_CAREER_KEY, EXPLORER_CAREER_KEY, FEEDBACK_KEY)


@st.cache_resource(show_spinner="Loading career data...")
def _cached_catalog(data_dir):
    # The Catalog is read-only, so one shared copy per data folder is safe
    return load_catalog(data_dir or None)


def get_catalog():
    # Returns the catalog, or shows an error and stops the page when the data cannot be used
    data_dir = os.environ.get(DATA_DIR_ENV, "")
    try:
        return _cached_catalog(data_dir)
    except DatasetError as exc:
        st.error("The career data could not be loaded, so the app cannot run. "
                 "Run `python -m src.data.validation` to see what is wrong.")
        st.caption(str(exc))
        st.stop()


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


def replace_session(profile, feedback):
    st.session_state[PROFILE_KEY] = profile
    st.session_state[FEEDBACK_KEY] = dict(feedback)


def get_top_k():
    return st.session_state.get(TOP_K_KEY, DEFAULT_TOP_K)


def select_career(career_id):
    st.session_state[SELECTED_CAREER_KEY] = career_id


def reset_assessment():
    for key in STATE_KEYS:
        st.session_state.pop(key, None)
