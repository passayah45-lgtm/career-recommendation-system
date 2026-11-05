# Career Assessment Assistant on the assessment page (Phase 3): flag, suggestions, confirmation and routing
# The assistant only adds confirmed entries to the existing dropdowns; saving and scoring stay unchanged

import re
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from src.services.catalog import load_catalog  # noqa: E402
from src.services.recommendations import recommend  # noqa: E402
from src.services.session_data import export_session  # noqa: E402
from src.ui import assessment_assistant as aa  # noqa: E402
from src.ui.state import PROFILE_KEY  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app.py")
PAGE = "pages/1_Career_Assessment.py"
EXAMPLE = ("I enjoy analysing data, solving mathematical problems, teaching people Python, "
           "and working with machine learning.")
MARKDOWN = "![x](https://example.com/t.png) [link](https://example.com) <b>bold</b>"


@pytest.fixture
def enabled(monkeypatch):
    monkeypatch.setenv(aa.ASSISTANT_ENV, "1")


def open_page(profile=None):
    at = AppTest.from_file(APP, default_timeout=60)
    if profile is not None:
        at.session_state[PROFILE_KEY] = profile
    at.run()
    at.switch_page(PAGE)
    at.run()
    assert not at.exception, at.exception
    return at


def suggest(at, text):
    at.text_area(key=aa.TEXT_KEY).input(text).run()
    at.button(key="assistant_suggest").click().run()
    assert not at.exception, at.exception
    return at


def boxes(at):
    return {c.label: c for c in at.checkbox}


def section1(at):
    return at.multiselect(key="interest_picker").value


def section2(at):
    return at.multiselect(key="skill_picker").value


def text_of(at):
    return "\n".join(str(e.value) for e in list(at.markdown) + list(at.caption) + list(at.info) + list(at.success)
                     + list(at.warning) + list(at.error))


# ---------- Feature flag ----------

@pytest.mark.parametrize("value", [None, "", "0", "false", "off", "no"])
def test_assistant_is_hidden_unless_the_flag_is_on(monkeypatch, value):
    if value is None:
        monkeypatch.delenv(aa.ASSISTANT_ENV, raising=False)
    else:
        monkeypatch.setenv(aa.ASSISTANT_ENV, value)
    at = open_page()
    assert not any(aa.TITLE in e.label for e in at.expander)
    assert len(at.text_area) == 1 and at.text_area[0].label == "Other skills (optional)"


@pytest.mark.parametrize("value", ["1", "true", "TRUE", " yes ", "on"])
def test_flag_values_that_turn_the_assistant_on(monkeypatch, value):
    monkeypatch.setenv(aa.ASSISTANT_ENV, value)
    assert aa.assistant_enabled()


def test_assistant_appears_with_its_title_and_description_and_the_form_stays(enabled):
    at = open_page()
    assert any(aa.TITLE in e.label for e in at.expander)
    assert aa.DESCRIPTION in text_of(at)
    # The original assessment is still all there
    assert at.multiselect(key="interest_picker").label == "Skills you already have"
    assert at.multiselect(key="skill_picker").label == "Kinds of work you enjoy"
    assert any(b.label == "Save my assessment" for b in at.button)


# ---------- Suggestions ----------

def test_suggestions_show_skills_interests_confidence_and_unmatched_words(enabled):
    at = suggest(open_page(), EXAMPLE + " I also love farming.")
    assert list(boxes(at)) == ["python", "machine learning", "Analysing data and information",
                               "Working with numbers and calculations", "Teaching and training others"]
    text = text_of(at)
    assert 'High confidence. From your words "python".' in text
    assert "Medium confidence" in text and '"farming": No catalogue skill' in text
    # Nothing changes before the student confirms
    assert section1(at) == [] and section2(at) == []


def test_low_confidence_suggestions_start_unticked(enabled):
    at = suggest(open_page(), "I enjoy keeping records in order and I know SQL.")
    checks = boxes(at)
    assert checks["sql"].value is True
    assert checks["Keeping information, records and procedures in order"].value is False


def test_empty_and_irrelevant_descriptions_are_handled(enabled):
    at = suggest(open_page(), "   ")
    assert "Write a few words about your skills and interests first." in text_of(at)
    assert not at.checkbox
    at = suggest(open_page(), "football and cooking")
    assert not at.checkbox and "No catalogue skills or interests were found" in text_of(at)
    assert '"football"' in text_of(at) and not any(b.key == "assistant_confirm" for b in at.button)


def test_long_descriptions_are_limited_to_the_matcher_length(enabled):
    from src.agents.profile_assistant import MAX_TEXT_CHARS
    box = open_page().text_area(key=aa.TEXT_KEY)
    assert box.max_chars == MAX_TEXT_CHARS == 5000
    # A long description still gives suggestions
    at = suggest(open_page(), ("I use Python. " * 300)[:MAX_TEXT_CHARS])
    assert list(boxes(at)) == ["python"]


def test_typed_markdown_in_the_description_is_shown_as_plain_text(enabled):
    at = suggest(open_page(), f"python, {MARKDOWN}")
    shown = [e.value for e in list(at.caption) if "example" in e.value]
    assert shown and all("](" not in v and not re.search(r"(?<!\\)<", v) for v in shown), shown


def test_a_failing_matcher_shows_an_error_and_keeps_the_assessment(enabled, monkeypatch):
    def broken(text, catalog):
        raise RuntimeError("boom")
    monkeypatch.setattr(aa, "suggest_profile", broken)
    at = open_page()
    at.multiselect(key="skill_picker").set_value(["sql"]).run()
    at = suggest(at, EXAMPLE)
    assert any("could not read this description" in e.value for e in at.error)
    assert section2(at) == ["sql"] and any(b.label == "Save my assessment" for b in at.button)


# ---------- Confirmation and routing ----------

def test_confirmed_entries_go_to_the_right_dropdowns_and_keep_existing_choices(enabled):
    at = open_page()
    at.multiselect(key="interest_picker").set_value(["writing and editing"]).run()
    at.multiselect(key="skill_picker").set_value(["sql"]).run()
    at = suggest(at, EXAMPLE)
    boxes(at)["machine learning"].uncheck().run()
    at.button(key="assistant_confirm").click().run()
    assert not at.exception
    # Official interests go to section 1, catalogue skills to section 2 (the exchanged lists)
    assert section1(at) == ["writing and editing", "analysing data and information",
                            "working with numbers and calculations", "teaching and training others"]
    assert section2(at) == ["sql", "python"]
    assert "Added 1 skill and 3 interests" in text_of(at)
    # The description and the suggestions are cleared once used
    assert at.text_area(key=aa.TEXT_KEY).value == "" and not at.checkbox


def test_suggestions_already_chosen_are_not_added_twice(enabled):
    at = open_page()
    at.multiselect(key="skill_picker").set_value(["python"]).run()
    at = suggest(at, "I use Python and SQL")
    checks = boxes(at)
    already = checks["python (already in your answers)"]
    assert already.disabled and already.value is False
    at.button(key="assistant_confirm").click().run()
    assert section2(at) == ["python", "sql"]


def test_confirming_nothing_changes_nothing(enabled):
    at = open_page()
    at.multiselect(key="skill_picker").set_value(["sql"]).run()
    at = suggest(at, EXAMPLE)
    for box in at.checkbox:
        box.uncheck()
    at.run()
    at.button(key="assistant_confirm").click().run()
    assert section1(at) == [] and section2(at) == ["sql"]
    assert "Added 0 skills and 0 interests" in text_of(at)


def test_repeated_submissions_replace_the_previous_suggestions(enabled):
    at = suggest(open_page(), "I use Python")
    assert list(boxes(at)) == ["python"]
    boxes(at)["python"].uncheck().run()
    at = suggest(at, "I use SQL and I enjoy writing and editing")
    assert list(boxes(at)) == ["sql", "Writing and editing"]
    # A new round starts with fresh ticks
    assert all(c.value for c in at.checkbox)
    at = suggest(at, "I use SQL and I enjoy writing and editing")
    assert list(boxes(at)) == ["sql", "Writing and editing"]


def test_clear_removes_the_description_and_suggestions(enabled):
    at = suggest(open_page(), EXAMPLE)
    at.button(key="assistant_clear").click().run()
    assert at.text_area(key=aa.TEXT_KEY).value == "" and not at.checkbox


# ---------- Saving, scoring and privacy ----------

def test_saving_after_the_assistant_scores_exactly_like_the_same_manual_choices(enabled):
    at = suggest(open_page(), EXAMPLE)
    at.button(key="assistant_confirm").click().run()
    at.selectbox[0].set_value(3)
    at.button(key="save_assessment").click().run()
    saved = at.session_state[PROFILE_KEY]
    assert saved == {"skills": ["python", "machine learning"],
                     "interests": ["analysing data and information", "working with numbers and calculations",
                                   "teaching and training others"], "education_level": 3}
    manual = open_page()
    manual.multiselect(key="skill_picker").set_value(["python", "machine learning"]).run()
    manual.multiselect(key="interest_picker").set_value(saved["interests"]).run()
    manual.selectbox[0].set_value(3)
    manual.button(key="save_assessment").click().run()
    assert manual.session_state[PROFILE_KEY] == saved
    catalog = load_catalog()
    ranked = recommend(saved, catalog, top_k=None)["recommendations"]
    direct = recommend({"skills": ["machine learning", "python"], "interests": list(reversed(saved["interests"])),
                        "education_level": 3}, catalog, top_k=None)["recommendations"]
    assert [(r["career_id"], r["score"]) for r in ranked] == [(r["career_id"], r["score"]) for r in direct]


def test_the_description_never_reaches_the_profile_or_the_session_file(enabled):
    secret = "My private story about quantum origami"
    at = suggest(open_page(), f"{secret}. I use Python.")
    at.button(key="assistant_confirm").click().run()
    at.button(key="save_assessment").click().run()
    saved = at.session_state[PROFILE_KEY]
    exported = export_session(saved, {}).decode("utf-8")
    assert "origami" not in exported and "private story" not in exported
    assert saved == {"skills": ["python"], "interests": []}


def test_a_restored_session_keeps_its_answers_with_the_assistant_on(enabled):
    profile = {"skills": ["python", "ML"], "interests": ["writing and editing", "Community leadership"],
               "education_level": 2}
    at = open_page(profile)
    assert section1(at) == ["writing and editing"]
    assert section2(at) == ["python", "Community leadership"]
    at = suggest(at, "I use SQL")
    at.button(key="assistant_confirm").click().run()
    at.button(key="save_assessment").click().run()
    saved = at.session_state[PROFILE_KEY]
    assert saved["skills"] == ["python", "sql", "ML"]
    assert saved["interests"] == ["writing and editing", "Community leadership"]


def test_the_assistant_module_uses_no_network_model_or_paid_service():
    source = (ROOT / "src" / "ui" / "assessment_assistant.py").read_text(encoding="utf-8")
    source += (ROOT / "src" / "agents" / "profile_assistant.py").read_text(encoding="utf-8")
    for word in ("requests", "urllib", "http", "openai", "anthropic", "ollama", "api_key", "socket", "eval(", "exec("):
        assert word not in source.lower(), word


# ---------- Reset and session upload clear the assistant (Phase 3.1, 5 November 2026) ----------
# Found in the readiness audit: the assessment reset or was replaced, but the previous student's description and
# suggestions stayed in the panel, a privacy risk on shared computers

PENDING = "My private notes: I use SQL and Python and I enjoy writing and editing"
OLD_PROFILE = {"skills": ["python", "patient care", "ML", "my own skill"],
               "interests": ["writing and editing", "mathematics", "Rural entrepreneurship"], "education_level": 2}


def assistant_state(at):
    return {k: at.session_state[k] for k in at.session_state if str(k).startswith(aa.STATE_PREFIX)}


def assistant_is_clear(at):
    # Nothing left in the panel, in the text box or in session state, apart from the empty description box
    return (not at.checkbox and at.text_area(key=aa.TEXT_KEY).value in ("", None)
            and "private notes" not in text_of(at)
            and set(assistant_state(at)) <= {aa.TEXT_KEY, "assistant_suggest", "assistant_clear"})


def upload(at, profile):
    raw = export_session(profile, {})
    at.get("file_uploader")[0].upload("career_session.json", raw, "application/json").run()
    at.button(key="assess_session_restore").click().run()
    assert not at.exception, at.exception
    return at


def test_starting_a_new_assessment_clears_the_assistant_and_the_form(enabled):
    at = open_page({"skills": ["sql"], "interests": ["writing and editing"], "education_level": 3})
    at = suggest(at, PENDING)
    assert at.checkbox and "private notes" in at.text_area(key=aa.TEXT_KEY).value
    at.button(key="page_reset").click().run()
    assert not at.exception, at.exception
    assert assistant_is_clear(at)
    # The existing reset still clears the assessment
    assert PROFILE_KEY not in at.session_state
    assert section1(at) == [] and section2(at) == []
    assert next(t for t in at.text_area if t.label == "Other skills (optional)").value == ""


def test_uploading_a_session_clears_the_assistant_and_restores_every_field(enabled):
    at = suggest(open_page(), PENDING)
    assert at.checkbox
    at = upload(at, OLD_PROFILE)
    assert assistant_is_clear(at)
    # Restored exactly as before
    assert section1(at) == ["writing and editing", "working with numbers and calculations"]
    assert section2(at) == ["python", "patient care", "Rural entrepreneurship"]
    assert next(t for t in at.text_area if t.label == "Other skills (optional)").value == "ML, my own skill"
    assert at.selectbox[0].value == 2


def test_after_an_upload_restored_entries_show_as_already_chosen_and_are_not_added_twice(enabled):
    at = upload(suggest(open_page(), PENDING), OLD_PROFILE)
    at = suggest(at, "I use Python and SQL and I enjoy writing and editing")
    checks = boxes(at)
    for label in ("python (already in your answers)", "Writing and editing (already in your answers)"):
        assert checks[label].disabled and checks[label].value is False
    at.button(key="assistant_confirm").click().run()
    assert section1(at) == ["writing and editing", "working with numbers and calculations"]
    # Confirmed entries are added after the restored ones
    assert section2(at) == ["python", "patient care", "Rural entrepreneurship", "sql"]
    at.button(key="save_assessment").click().run()
    saved = at.session_state[PROFILE_KEY]
    assert saved["skills"].count("python") == 1 and saved["interests"].count("writing and editing") == 1


def test_saved_answers_are_recognised_before_the_dropdowns_refill(enabled):
    # Leaving the page and coming back: Streamlit drops the dropdowns' state, and the panel is drawn before they
    # restore their choices, so it must read the saved answers to treat them as already chosen
    at = open_page({"skills": ["python"], "interests": ["writing and editing"]})
    at = suggest(at, "I use Python and SQL and I enjoy writing and editing")
    at.switch_page("pages/2_Recommendations.py").run()
    at.switch_page(PAGE).run()
    assert not at.exception, at.exception
    checks = boxes(at)
    assert checks["python (already in your answers)"].disabled
    assert checks["Writing and editing (already in your answers)"].disabled
    assert not checks["sql"].disabled


def test_a_new_round_after_a_reset_starts_with_fresh_ticks(enabled):
    at = suggest(open_page({"skills": ["sql"]}), "I use Python")
    boxes(at)["python"].uncheck().run()
    at.button(key="page_reset").click().run()
    at = suggest(at, "I use Python")
    assert boxes(at)["python"].value is True


def test_reset_and_upload_work_as_before_with_the_assistant_off(monkeypatch):
    monkeypatch.delenv(aa.ASSISTANT_ENV, raising=False)
    at = open_page({"skills": ["sql"], "interests": ["writing and editing"], "education_level": 3})
    at.button(key="page_reset").click().run()
    assert not at.exception and PROFILE_KEY not in at.session_state
    assert section1(at) == [] and section2(at) == [] and assistant_state(at) == {}
    at = upload(at, OLD_PROFILE)
    assert section1(at) == ["writing and editing", "working with numbers and calculations"]
    assert section2(at) == ["python", "patient care", "Rural entrepreneurship"]
    assert assistant_state(at) == {} and len(at.text_area) == 1
