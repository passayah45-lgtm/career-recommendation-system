# Regression protection for the iPhone "TypeError: Importing a module script failed." error (4 November 2026)
# Cause: a shared Streamlit widget file failed to download, and the browser keeps that failure until a reload.
# Every page installs a small handler for Streamlit's vite:preloadError event; these tests keep it working.

import re
import shutil
import subprocess
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
import streamlit  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

from src.ui import recovery  # noqa: E402
from src.ui.state import FEEDBACK_KEY, PROFILE_KEY  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app.py")
CSS = (ROOT / "src" / "ui" / "styles.css").read_text(encoding="utf-8")
PAGES = (None, "pages/1_Career_Assessment.py", "pages/2_Recommendations.py", "pages/3_Skill_Gap_Analysis.py",
         "pages/4_Career_Explorer.py", "pages/5_Analytics.py", "pages/6_Skill_Roadmap.py")
PROFILE = {"skills": ["python"], "interests": ["analysing data and information"], "education_level": 3}


def scripts(at):
    return [h.proto for h in at.get("html") if "vite:preloadError" in h.proto.body]


def open_page(page, **state):
    at = AppTest.from_file(APP, default_timeout=60)
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    if page:
        at.switch_page(page)
        at.run()
    assert not at.exception, at.exception
    return at


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p or "home")
def test_every_page_installs_the_recovery_handler_once(page):
    found = scripts(open_page(page, **{PROFILE_KEY: PROFILE}))
    assert len(found) == 1
    assert found[0].unsafe_allow_javascript is True


def test_streamlit_still_announces_failed_widget_files_with_the_event_the_handler_listens_for():
    # A future Streamlit upgrade that renames or drops this event would silently disable the recovery
    js = Path(streamlit.__file__).parent / "static" / "static" / "js"
    helpers = [p for p in js.glob("preload-helper.*.js") if "vite:preloadError" in p.read_text(encoding="utf-8")]
    assert helpers, "Streamlit no longer dispatches vite:preloadError; review src/ui/recovery.py"


def test_page_reloads_by_itself_only_when_no_answers_would_be_lost():
    empty = scripts(open_page(None))[0].body
    assert "window.__crsHasSessionData = false;" in empty
    for state in ({PROFILE_KEY: PROFILE}, {FEEDBACK_KEY: {"C001": 1}}):
        body = scripts(open_page(None, **state))[0].body
        assert "window.__crsHasSessionData = true;" in body
    # With answers the handler shows the message and returns before the automatic reload (the last reload call;
    # the first one belongs to the button the student presses)
    body = recovery.recovery_script(True)
    handler = body[body.index("function handleFailure()"):body.index("function scan()")]
    stop = handler.index("if (window.__crsHasSessionData) { showNotice(); return; }")
    assert stop < handler.index("reloadPage();")


def test_automatic_reload_is_limited_so_it_can_never_loop():
    body = recovery.recovery_script(False)
    assert recovery.RELOAD_GUARD_SECONDS >= 10
    assert f"now - last < {recovery.RELOAD_GUARD_SECONDS * 1000}" in body
    # Without browser storage the page never reloads by itself, because the guard could not be kept
    assert body.count("catch (e) { showNotice(); return; }") == 2
    assert body.count("window.__crsChunkRecovery = true;") == 1


def test_message_is_plain_and_contains_no_student_text():
    for text in (recovery.NOTICE_TEXT, recovery.NOTICE_TEXT_WITH_DATA):
        assert "TypeError" not in text and "module" not in text
        assert "Reload" in text or "reload" in text
    assert "Your session data" in recovery.NOTICE_TEXT_WITH_DATA
    # Only fixed app text is placed in the script, and it is set with textContent, never as HTML
    body = recovery.recovery_script(True)
    assert "innerHTML" not in body
    assert "text.textContent = " in body and "button.textContent = " in body


def test_the_script_is_valid_javascript():
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed")
    for flag in (True, False):
        js = re.search(r"<script>(.*)</script>", recovery.recovery_script(flag), re.S).group(1)
        result = subprocess.run([node, "--check", "-"], input=js, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stderr


def test_the_hidden_wrapper_adds_no_space_to_the_page():
    assert f".st-key-{recovery.RECOVERY_KEY}," in CSS
    assert f'[data-testid="stLayoutWrapper"]:has(> .st-key-{recovery.RECOVERY_KEY})' in CSS


def test_long_typed_entries_wrap_inside_their_chip_in_both_dropdowns():
    rule = CSS[CSS.index('.st-key-interest_picker [role="group"][aria-label="Selected values"] > span > span,'):]
    rule = rule[:rule.index("}")]
    assert ".st-key-skill_picker" in rule
    assert "overflow-wrap: anywhere" in rule and "word-break: break-word" in rule


def test_failures_before_the_script_loaded_are_found_on_the_page_and_handled_once():
    body = recovery.recovery_script(False)
    # The page is checked when the script starts and twice more, for failures that came before it
    assert "scan(); setTimeout(scan, 1500); setTimeout(scan, 5000);" in body
    assert 'document.querySelectorAll(\'[data-testid="stAlertContentError"]\')' in body
    # Several failing files, or the event and a scan together, still give a single response
    assert "if (handled) { return; }" in body and body.count("handled = true;") == 1
    assert 'window.addEventListener("vite:preloadError", handleFailure);' in body


def test_failure_pattern_matches_each_browser_wording_and_nothing_the_app_writes():
    pattern = re.compile(recovery.FAILURE_PATTERN, re.I)
    for text in ("TypeError: Importing a module script failed.",
                 "TypeError: Failed to fetch dynamically imported module: https://x/static/js/A.js",
                 "TypeError: error loading dynamically imported module: https://x/static/js/A.js"):
        assert pattern.search(text), text
    for text in ("Please check your answers: skills must be a list of text values.",
                 "Add at least one skill from the list, or one interest, so the system has something to match.",
                 "Your saved assessment could not be used: unknown career. Please complete the assessment again."):
        assert not pattern.search(text), text


def test_message_stays_clear_of_bottom_corner_badges_and_has_a_large_button():
    body = recovery.recovery_script(False)
    assert "top:68px" in body and "bottom:" not in body
    assert "min-height:44px" in body


def test_every_reload_first_downloads_the_module_files_again_without_the_cache():
    # WebKit (iPhone Safari and Chrome) keeps a failed file through a normal reload, a new visit and a new query
    # string; only downloading it again with the cache bypassed replaced it (WebKitGTK 2.52, 4 November 2026)
    body = recovery.recovery_script(False)
    refresh = body[body.index("function reloadPage()"):body.index("function handleFailure()")]
    assert 'document.querySelectorAll(\'link[rel="modulepreload"]\')' in refresh
    assert 'fetch(links[i].href, { cache: "reload", credentials: "same-origin" })' in refresh
    # The reload always happens, even when a download hangs or fails
    assert ".catch(function () { return null; })" in refresh
    assert f"setTimeout(done, {recovery.REFRESH_TIMEOUT_SECONDS * 1000})" in refresh
    assert "Promise.race([Promise.all(jobs), limit]).then(function () { window.location.reload(); });" in refresh
    # The page is only ever reloaded through this function: once by itself, or by the student's button
    assert body.count("location.reload()") == 1
    button = body[body.index('button.addEventListener("click"'):body.index("box.appendChild(text);")]
    assert "reloadPage();" in button and "button.disabled = true;" in button
