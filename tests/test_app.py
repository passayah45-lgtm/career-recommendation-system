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
    assert "was not opened by the checker" in text_of(at)


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


def test_navigation_titles_and_home_page():
    # The entry point registers explicit titles, so the sidebar never shows the file name "app"
    import ast
    tree = ast.parse(Path(APP).read_text(encoding="utf-8"))
    titles = [kw.value.value for node in ast.walk(tree) if isinstance(node, ast.Call)
              for kw in node.keywords if kw.arg == "title"]
    assert titles == ["Home", "Career Assessment", "Recommendations", "Skill-Gap Analysis",
                      "Career Explorer", "Analytics"]
    at = open_page()
    assert at.title[0].value == "Career Recommendation System"


def test_home_offers_assessment_action_and_score_note():
    at = open_page()
    assert "Start career assessment" in [b.label for b in at.button]
    text = text_of(at)
    assert "not a probability" in text
    assert "required skills (55%)" in text and "interests (25%)" in text


def test_skill_gap_cards_show_the_real_verification_status():
    from src.services.catalog import load_catalog
    from src.ui.theme import VERIFICATION_BADGES
    at = open_page("pages/3_Skill_Gap_Analysis.py", profile=WORKED_EXAMPLE, **{SELECTED_CAREER_KEY: "C001"})
    resource = load_catalog().resources.for_skill("data visualization")[0]
    expected = VERIFICATION_BADGES[resource.url_verification][2]
    card = [m.value for m in at.markdown if resource.title in m.value]
    assert card, "resource card missing"
    assert any(expected in m.value for m in at.markdown)
    if resource.url_verification != "http_checked":
        assert not any("Link checked" in m.value for m in at.markdown)


def test_assessment_sidebar_shows_saved_state_after_submit():
    at = open_page("pages/1_Career_Assessment.py")
    at.multiselect[0].set_value(["python"])
    at.button[0].click().run()
    assert not at.exception
    assert any("Saved for this session" in c.value for c in at.sidebar.caption)


def test_skill_gap_shows_overall_coverage_and_counts():
    at = open_page("pages/3_Skill_Gap_Analysis.py", profile=WORKED_EXAMPLE, **{SELECTED_CAREER_KEY: "C001"})
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Overall skill coverage"] == "50%"
    assert metrics["Preferred skill coverage"] == "0%"
    assert "4 of 5 skills" in text_of(at)
