# Streamlit pages run through AppTest, starting from app.py like a real session

from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from src.ui.state import DATA_DIR_ENV, PROFILE_KEY, SELECTED_CAREER_KEY  # noqa: E402

TIMEOUT = 60
APP = str(Path(__file__).resolve().parents[1] / "app.py")
WORKED_EXAMPLE = {"skills": ["Python", "SQL", "Excel", "ML", "statistics"],
                  "interests": ["analysis", "mathematics"], "education_level": 3}


def text_of(at):
    parts = [e.value for e in at.markdown] + [e.value for e in at.caption] + [e.value for e in at.title]
    parts += [e.value for e in at.info] + [e.value for e in at.warning] + [e.value for e in at.error]
    parts += [e.value for e in at.success] + [e.value for e in at.subheader]
    return "\n".join(str(p) for p in parts)


def open_page(page=None, profile=None, **state):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    if profile is not None:
        at.session_state[PROFILE_KEY] = profile
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    if page:
        at.switch_page(page)
        at.run()
    assert not at.exception, at.exception
    return at


def test_home_page_starts_and_shows_dataset_size():
    at = open_page()
    assert at.title[0].value == "Career Recommendation System"
    assert [m.value for m in at.metric][:4] == ["50", "8", "114", "114"]


def test_assessment_saves_normalized_profile_and_reports_unknown_skills():
    at = open_page("pages/1_Career_Assessment.py")
    at.multiselect[0].set_value(["python", "sql"])
    at.text_area[0].input("ML, machine learning, blockchain")
    at.multiselect[1].set_value(["analysis"])
    at.selectbox[0].set_value(3)
    at.button[0].click().run()
    assert not at.exception
    saved = at.session_state[PROFILE_KEY]
    assert saved["skills"] == ["python", "sql", "ML", "machine learning", "blockchain"]
    assert saved["education_level"] == 3
    text = text_of(at)
    assert "blockchain" in text and "Assessment saved" in text
    assert "Counted once" in text


def test_assessment_rejects_empty_answers():
    at = open_page("pages/1_Career_Assessment.py")
    at.button[0].click().run()
    assert not at.exception
    assert PROFILE_KEY not in at.session_state
    assert any("at least one skill" in e.value for e in at.error)


def test_recommendations_need_a_profile():
    at = open_page("pages/2_Recommendations.py")
    assert "Complete the career assessment first" in text_of(at)


def test_recommendations_show_real_service_results():
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE)
    scores = [m.value for m in at.metric]
    assert scores[:5] == ["61.5 / 100", "59.6 / 100", "55.0 / 100", "50.8 / 100", "41.7 / 100"]
    text = text_of(at)
    assert "1. Data Scientist" in text
    assert "not a probability" in text
    assert "You have 4 of 5 required skills" in text


def test_recommendations_top_k_slider():
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE)
    at.slider[0].set_value(2).run()
    assert not at.exception
    assert len(at.metric) == 2


def test_recommendations_warn_about_unknown_skills():
    at = open_page("pages/2_Recommendations.py", profile={"skills": ["python", "blockchain"]})
    assert any("blockchain" in w.value for w in at.warning)


def test_recommendations_handle_invalid_saved_profile():
    at = open_page("pages/2_Recommendations.py", profile={"skills": ["python"], "education_level": 9})
    assert any("could not be used" in e.value for e in at.error)


def test_recommendation_button_opens_skill_gap_for_that_career():
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE)
    at.button(key="gap_C002").click().run()
    assert not at.exception
    assert at.session_state[SELECTED_CAREER_KEY] == "C002"


def test_skill_gap_shows_coverage_and_resources():
    at = open_page("pages/3_Skill_Gap_Analysis.py", profile=WORKED_EXAMPLE, **{SELECTED_CAREER_KEY: "C001"})
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Required skill coverage"] == "80%"
    assert metrics["Missing required skills"] == "1"
    table = at.dataframe[0].value
    assert list(table["Skill"]) == ["data visualization"]
    assert list(table["Link status"])[0] in ("search index confirmed", "http checked")
    assert "not HTTP-checked" in text_of(at)


def test_skill_gap_without_profile_shows_all_skills_missing():
    at = open_page("pages/3_Skill_Gap_Analysis.py", **{SELECTED_CAREER_KEY: "C040"})
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Required skill coverage"] == "0%"
    assert "every skill is shown as missing" in text_of(at)


def test_explorer_filters_by_category_and_search():
    at = open_page("pages/4_Career_Explorer.py")
    assert "Showing 50 of 50 careers." in text_of(at)
    at.multiselect[0].set_value(["Healthcare"]).run()
    assert "Showing 6 of 50 careers." in text_of(at)
    at.text_input[0].input("nurse").run()
    assert "Showing 1 of 50 careers." in text_of(at)
    assert "Registered Nurse" in text_of(at)
    at.text_input[0].input("zzz").run()
    assert "No careers match" in text_of(at)


def test_analytics_with_and_without_profile():
    at = open_page("pages/5_Analytics.py")
    assert len(at.get("plotly_chart")) == 3
    at = open_page("pages/5_Analytics.py", profile=WORKED_EXAMPLE)
    assert len(at.get("plotly_chart")) == 5


def test_reset_clears_the_assessment():
    at = open_page("pages/1_Career_Assessment.py", profile=WORKED_EXAMPLE)
    at.button(key="page_reset").click().run()
    assert not at.exception
    assert PROFILE_KEY not in at.session_state


def test_unavailable_data_shows_error_instead_of_crashing(tmp_path, monkeypatch):
    monkeypatch.setenv(DATA_DIR_ENV, str(tmp_path))
    at = AppTest.from_file(APP, default_timeout=TIMEOUT).run()
    assert not at.exception
    assert any("could not be loaded" in e.value for e in at.error)


def test_explorer_to_skill_gap_keeps_a_career_outside_the_recommendations():
    # C040 Registered Nurse is not in the worked example's top 5
    at = open_page("pages/4_Career_Explorer.py", profile=WORKED_EXAMPLE)
    at.selectbox[0].set_value("C040").run()
    at.button[0].click().run()
    assert not at.exception
    assert at.session_state[SELECTED_CAREER_KEY] == "C040"
    at.switch_page("pages/3_Skill_Gap_Analysis.py")
    at.run()
    assert not at.exception
    assert at.radio[0].value == "All careers"
    assert at.selectbox[0].value == "C040"
    assert any("Missing required skills" == m.label for m in at.metric)


def test_recommendation_to_skill_gap_stays_on_recommended_list():
    at = open_page("pages/3_Skill_Gap_Analysis.py", profile=WORKED_EXAMPLE, **{SELECTED_CAREER_KEY: "C002"})
    assert at.radio[0].value == "My recommended careers"
    assert at.selectbox[0].value == "C002"
