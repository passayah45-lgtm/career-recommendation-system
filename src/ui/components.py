# Reusable Streamlit building blocks shared by the pages
# Every page calls page_setup() first, which applies the shared theme, logo and stylesheet

from html import escape
from pathlib import Path

import streamlit as st

from src.services.recommendations import SCORE_DISCLAIMER
from src.services.session_data import SessionFileError, export_session, import_session
from src.ui.illustrations import HERO_SVG, SIDEBAR_ART, initial_tile, ring_svg
from src.ui.state import SELECTED_CAREER_KEY, get_catalog, get_feedback, replace_session, reset_assessment
from src.ui.theme import UNVERIFIED_BADGE, VERIFICATION_BADGES

HOME_PAGE = "home.py"
ASSESSMENT_PAGE = "pages/1_Career_Assessment.py"
RECOMMENDATIONS_PAGE = "pages/2_Recommendations.py"
SKILL_GAP_PAGE = "pages/3_Skill_Gap_Analysis.py"
EXPLORER_PAGE = "pages/4_Career_Explorer.py"
ANALYTICS_PAGE = "pages/5_Analytics.py"

ROOT = Path(__file__).resolve().parents[2]
STYLESHEET = Path(__file__).with_name("styles.css")
LOGO = ROOT / "static" / "logo.svg"
LOGO_ICON = ROOT / "static" / "logo_icon.svg"


def apply_theme():
    # A style-only st.html block is applied without taking space on the page
    st.html(f"<style>{STYLESHEET.read_text(encoding='utf-8')}</style>")
    st.logo(str(LOGO), size="large", icon_image=str(LOGO_ICON))


def page_setup(title, subtitle=None, eyebrow=None, hero=False):
    # Returns the header container, so a page can add actions inside it
    # The hero variant adds an illustration on the right, hidden on phones by styles.css
    st.set_page_config(page_title=f"{title} | Career Recommendation System", page_icon=str(LOGO_ICON),
                       layout="wide")
    apply_theme()
    if hero:
        with st.container(border=True, key="hero"):
            text_col, art_col = st.columns([1.7, 1], vertical_alignment="center")
            with art_col, st.container(key="hero_art"):
                # st.image renders SVG markup, st.html would strip it
                st.image(HERO_SVG, width="stretch")
        header = text_col
    else:
        header = st.container()
    with header:
        if eyebrow:
            st.markdown(f'<div class="crs-eyebrow">{escape(eyebrow)}</div>', unsafe_allow_html=True)
        st.title(title, anchor=False)
        if subtitle:
            st.markdown(f'<p class="crs-subtitle">{escape(subtitle)}</p>', unsafe_allow_html=True)
    return header


def badges(items, color="gray", icon=None, empty="None"):
    # Skill and category tags as native Streamlit badges, with an icon so status never relies on color alone
    if not items:
        return f":gray[_{empty}_]"
    prefix = f"{icon} " if icon else ""
    return " ".join(f":{color}-badge[{prefix}{item}]" for item in items)


def have_badges(items, empty="None yet"):
    return badges(items, "green", ":material/check:", empty)


def missing_badges(items, empty="None"):
    return badges(items, "orange", ":material/close:", empty)


def optional_badges(items, empty="None"):
    return badges(items, "gray", ":material/add:", empty)


def interest_badges(items, empty="None"):
    return badges(items, "blue", None, empty)


def label(text):
    st.markdown(f'<div class="crs-label">{escape(text)}</div>', unsafe_allow_html=True)


def section(number, title, help_text=None, icon=":material/radio_button_checked:", color="primary"):
    # Numbered section heading with a colored icon, used by the assessment form
    st.markdown(f"#### :{color}[{icon}] {number}. {title}")
    if help_text:
        st.caption(help_text)


def icon_heading(icon, color, size="###"):
    # Large colored Material icon used as a tile on cards
    st.markdown(f"{size} :{color}[{icon}]")


def stat_card(column, label_text, value, icon, color, key):
    # Statistic card: colored icon, value and label, value read from the dataset by the caller
    with column, st.container(border=True, key=f"stat_{key}", height="stretch"):
        icon_heading(icon, color)
        st.metric(label_text, value)


def ring(fraction, center_text, size=64, label_text=""):
    st.image(ring_svg(fraction, center_text, size=size, label=label_text), width=size)


def sidebar_card():
    with st.sidebar, st.container(border=True, key="side_card"):
        st.markdown("**Your future starts with your skills.**")
        st.caption("Assess, compare and close the gaps.")
        st.image(SIDEBAR_ART, width="stretch")


def score_disclaimer():
    st.caption(f":material/info: {SCORE_DISCLAIMER}")


def need_profile_message():
    with st.container(border=True, key="panel_empty"):
        st.markdown("#### :material/assignment: No assessment yet")
        st.markdown("Complete the career assessment first. It takes about two minutes.")
        st.page_link(ASSESSMENT_PAGE, label="Go to the Career Assessment", icon=":material/arrow_forward:")


def show_profile_warnings(warnings):
    for w in warnings:
        st.warning(w, icon=":material/warning:")


def verification_badge(status, verified_on=""):
    # Only http_checked uses the success color, every other status stays neutral
    color, icon, text = VERIFICATION_BADGES.get(status, UNVERIFIED_BADGE)
    date = f" {verified_on}" if verified_on and status == "http_checked" else ""
    return f":{color}-badge[{icon} {text}{date}]"


def resource_row(resource):
    # One learning resource inside a skill card: provider tile, linked title, type, level, cost and link status
    with st.container(horizontal=True, vertical_alignment="center", gap="small"):
        st.html(initial_tile(resource["provider"]), width="content")
        with st.container(gap="small"):
            st.markdown(f'<div class="crs-res-title"><a href="{escape(resource["url"], quote=True)}" target="_blank" '
                        f'rel="noopener">{escape(resource["title"])}</a></div>'
                        f'<div class="crs-res-meta">{escape(resource["provider"])}</div>',
                        unsafe_allow_html=True)
            access = (":blue-badge[:material/lock_open: Free]" if resource["is_free"]
                      else ":gray-badge[:material/payments: Paid or partly paid]")
            st.markdown(f":violet-badge[{resource['resource_type'].capitalize()}] "
                        f":gray-badge[{resource['level'].capitalize()}] {access} "
                        f"{verification_badge(resource['url_verification'], resource.get('verified_on', ''))}",
                        help=resource.get("url_verification_meaning"))


def reset_button(key="reset"):
    if st.button("Start a new assessment", key=key, icon=":material/restart_alt:",
                 help="Clears your answers from this browser session"):
        reset_assessment()
        st.switch_page(ASSESSMENT_PAGE)


def sidebar_profile_summary(profile):
    # Assessment status and the career selected for skill-gap analysis, visible on every page
    with st.sidebar:
        st.markdown("**Your assessment**")
        if not profile:
            st.caption(":material/radio_button_unchecked: Not started")
            st.page_link(ASSESSMENT_PAGE, label="Start the assessment", icon=":material/arrow_forward:")
            sidebar_card()
            return
        level = profile.get("education_level")
        st.caption(f":material/check_circle: Saved for this session  \n"
                   f"Skills entered: {len(profile.get('skills', []))}  \n"
                   f"Interests: {len(profile.get('interests', []))}  \n"
                   f"Education level: {'not provided' if level is None else level}")
        selected = st.session_state.get(SELECTED_CAREER_KEY)
        titles = {c.career_id: c.title for c in get_catalog().careers}
        if selected in titles:
            st.caption(f":material/school: Skill-gap career: {titles[selected]}")
        reset_button(key="sidebar_reset")
    sidebar_card()


def session_data_panel(profile, key, allow_download=True):
    # Download, upload and clear the learner's own session; nothing is stored by the app
    with st.expander(":material/folder_shared: Your session data", expanded=False):
        st.caption("Your answers and career feedback are kept only while this page is open. They are not "
                   "saved in any database and disappear when you close the tab. Download them to continue later.")
        if allow_download and profile:
            st.download_button("Download my session", data=export_session(profile, get_feedback()),
                               file_name="career_session.json", mime="application/json",
                               icon=":material/download:", key=f"{key}_download")
        uploaded = st.file_uploader("Continue a saved session", type=["json"], key=f"{key}_upload",
                                    help="Upload a career_session.json file you downloaded earlier.")
        if uploaded is not None and st.button("Restore this session", key=f"{key}_restore",
                                              icon=":material/upload:"):
            try:
                saved_profile, saved_feedback = import_session(uploaded.getvalue(), get_catalog())
            except SessionFileError as exc:
                st.error(f"The file could not be used: {exc}.", icon=":material/error:")
            else:
                replace_session(saved_profile, saved_feedback)
                st.success("Session restored.", icon=":material/check_circle:")
                st.rerun()
