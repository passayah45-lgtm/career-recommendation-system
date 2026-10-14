# Reusable Streamlit building blocks shared by the pages
# Every page calls page_setup() first, which applies the shared theme, logo and stylesheet

from html import escape
from pathlib import Path

import streamlit as st

from src.services.recommendations import SCORE_DISCLAIMER
from src.ui.state import SELECTED_CAREER_KEY, get_catalog, reset_assessment
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
    st.set_page_config(page_title=f"{title} | Career Recommendation System", page_icon=str(LOGO_ICON),
                       layout="wide")
    apply_theme()
    header = st.container(border=True, key="hero") if hero else st.container()
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


def section(number, title, help_text=None):
    help_html = f'<div class="crs-section-help">{escape(help_text)}</div>' if help_text else ""
    st.markdown(
        f'<div class="crs-section"><span class="crs-step-num">{number}</span>'
        f'<div><div class="crs-section-title">{escape(title)}</div>{help_html}</div></div>',
        unsafe_allow_html=True,
    )


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


def resource_card(resource, key):
    with st.container(border=True, key=f"res_{key}"):
        st.markdown(f'<div class="crs-res-title"><a href="{escape(resource["url"], quote=True)}" target="_blank" '
                    f'rel="noopener">{escape(resource["title"])}</a></div>'
                    f'<div class="crs-res-meta">{escape(resource["provider"])} | '
                    f'{escape(resource["resource_type"])} | {escape(resource["level"])}</div>',
                    unsafe_allow_html=True)
        access = (":blue-badge[:material/lock_open: Free]" if resource["is_free"]
                  else ":gray-badge[:material/payments: Paid or partly paid]")
        st.markdown(f"{access} {verification_badge(resource['url_verification'], resource.get('verified_on', ''))}",
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
