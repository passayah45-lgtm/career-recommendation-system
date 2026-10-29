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
    # 3 dataset charts, 1 model comparison chart, plus 2 personal charts when a profile exists
    at = open_page("pages/5_Analytics.py")
    assert len(at.get("plotly_chart")) == 4
    at = open_page("pages/5_Analytics.py", profile=WORKED_EXAMPLE)
    assert len(at.get("plotly_chart")) == 6


def test_analytics_model_comparison_tab_shows_saved_results():
    at = open_page("pages/5_Analytics.py")
    text = text_of(at)
    assert "No trained model ranked careers better than the formula" in text
    assert "36 synthetic profiles" in text
    assert len(at.dataframe) == 1


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
    next(b for b in at.button if b.label == "Analyze my skill gap for this career").click().run()
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
    assert titles == ["Home", "Career Assessment", "Recommendations", "Skill-Gap Analysis", "Skill Roadmap",
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


def test_skill_gap_empty_state_has_no_one_option_selector():
    # Without an assessment the page is still valid: all skills missing, career picker only
    at = open_page("pages/3_Skill_Gap_Analysis.py", **{SELECTED_CAREER_KEY: "C001"})
    assert len(at.radio) == 0
    assert at.selectbox[0].value == "C001"
    assert "every skill is shown as missing" in text_of(at)


def test_skill_gap_labels_required_and_optional_resources_differently():
    at = open_page("pages/3_Skill_Gap_Analysis.py", profile=WORKED_EXAMPLE, **{SELECTED_CAREER_KEY: "C001"})
    texts = [m.value for m in at.markdown]
    required = [t for t in texts if "Required]" in t]
    optional = [t for t in texts if "Optional]" in t]
    assert required == [":orange-badge[:material/priority_high: Required] **data visualization**"]
    assert {t.split("**")[1] for t in optional} == {"deep learning", "cloud computing", "git"}


def test_explorer_list_shows_title_and_category_only():
    at = open_page("pages/4_Career_Explorer.py")
    assert list(at.dataframe[0].value.columns) == ["Career", "Category"]
    assert len(at.dataframe[0].value) == 50


def test_feedback_adapts_the_recommendation_list():
    from src.ui.state import FEEDBACK_KEY
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE, top_k=10)
    assert "Tell the app what you think" in text_of(at)
    at.button(key="like_C002").click().run()
    assert not at.exception
    assert at.session_state[FEEDBACK_KEY] == {"C002": 1}
    text = text_of(at)
    assert "Adapted to your feedback" in text
    assert "similar to Data Analyst, which you are interested in" in text
    at.button(key="dislike_C029").click().run()
    assert at.session_state[FEEDBACK_KEY] == {"C002": 1, "C029": -1}
    at.button(key="clear_feedback").click().run()
    assert FEEDBACK_KEY not in at.session_state


def test_session_download_is_offered_and_reset_clears_feedback():
    from src.ui.state import FEEDBACK_KEY
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE, **{FEEDBACK_KEY: {"C002": 1}})
    assert len(at.get("download_button")) == 1
    at.button(key="sidebar_reset").click().run()
    assert FEEDBACK_KEY not in at.session_state and PROFILE_KEY not in at.session_state


def test_model_rankings_section_needs_a_profile():
    at = open_page("pages/5_Analytics.py")
    text = text_of(at)
    assert "How the Models Rank Your Careers" in text
    assert "Complete the career assessment to see how each method ranks" in text


def test_model_rankings_section_shows_four_methods_for_the_profile():
    at = open_page("pages/5_Analytics.py", profile=WORKED_EXAMPLE)
    text = text_of(at)
    for label in ("Weighted formula", "Logistic Regression", "Decision Tree", "Random Forest"):
        assert f"#### {label}" in text
    assert "Primary method, used by this app" in text
    assert text.count("Trained model, comparison only") == 3
    assert "1. **Data Scientist** :gray[61.5 / 100]" in text
    assert "not your chance of success" in text
    assert "Offline evaluation results" in text
    assert "measured on this server" in text.lower()


def test_model_rankings_section_survives_a_training_failure(monkeypatch):
    import src.ui.state as state
    monkeypatch.setattr(state, "_cached_live_models", lambda _: (_ for _ in ()).throw(OSError("no labels")))
    at = open_page("pages/5_Analytics.py", profile=WORKED_EXAMPLE)
    text = text_of(at)
    assert "The model comparison is not available right now" in text
    assert "No trained model ranked careers better than the formula" in text


def button_keys(at):
    return {b.key for b in at.button}


def open_list(at, view):
    at.button_group(key="career_list_view").set_value(view).run()
    assert not at.exception
    return at


def test_interested_career_moves_to_its_own_list():
    from src.ui.state import FEEDBACK_KEY
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE)
    assert "like_C002" in button_keys(at)
    at.button(key="like_C002").click().run()
    assert not at.exception
    assert at.session_state[FEEDBACK_KEY] == {"C002": 1}
    # Gone from the main list, which is renumbered and still shows five new careers
    assert "like_C002" not in button_keys(at)
    assert len([k for k in button_keys(at) if k and k.startswith("like_")]) == 5
    assert "Data Analyst moved to Interested." in [t.value for t in at.toast]
    open_list(at, "interested")
    keys = button_keys(at)
    assert {"to_not_C002", "remove_C002", "saved_explore_C002", "saved_gap_C002"} <= keys
    assert "#### Data Analyst" in text_of(at)
    assert "Rank 2 by the formula" in text_of(at)


def test_not_for_me_career_moves_to_its_own_list():
    from src.ui.state import FEEDBACK_KEY
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE)
    at.button(key="dislike_C029").click().run()
    assert at.session_state[FEEDBACK_KEY] == {"C029": -1}
    assert "dislike_C029" not in button_keys(at)
    open_list(at, "not_for_me")
    assert {"to_int_C029", "remove_C029"} <= button_keys(at)
    open_list(at, "interested")
    assert "No careers yet" in text_of(at)


def test_changing_a_decision_moves_the_career_without_duplicates():
    from src.ui.state import FEEDBACK_KEY
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE, **{FEEDBACK_KEY: {"C002": 1}})
    open_list(at, "interested")
    at.button(key="to_not_C002").click().run()
    assert at.session_state[FEEDBACK_KEY] == {"C002": -1}
    # The open list stays open after the move, and the career is now only in the other list
    assert at.session_state["career_list_view"] == "interested"
    assert "to_not_C002" not in button_keys(at)
    open_list(at, "not_for_me")
    assert "to_int_C002" in button_keys(at)
    at.button(key="to_int_C002").click().run()
    assert at.session_state[FEEDBACK_KEY] == {"C002": 1}
    assert "to_int_C002" not in button_keys(at)


def test_removing_feedback_returns_the_career_to_recommendations():
    from src.ui.state import FEEDBACK_KEY
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE, **{FEEDBACK_KEY: {"C002": 1}})
    open_list(at, "interested")
    at.button(key="remove_C002").click().run()
    assert at.session_state[FEEDBACK_KEY] == {}
    assert "Data Analyst removed from your lists." in [t.value for t in at.toast]
    open_list(at, "recommendations")
    assert "like_C002" in button_keys(at)


def test_list_counts_on_the_page_dashboard_and_sidebar():
    from src.ui.state import FEEDBACK_KEY
    feedback = {"C002": 1, "C003": 1, "C029": -1}
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE, **{FEEDBACK_KEY: feedback})
    control = at.button_group(key="career_list_view")
    assert [o.strip() for o in control.options] == ["Recommendations (5)", "Interested (2)", "Not for me (1)"]
    labels = [b.label for b in at.button]
    assert "Interested (2)" in labels and "Not for me (1)" in labels
    at = open_page(None, profile=WORKED_EXAMPLE, **{FEEDBACK_KEY: feedback})
    assert at.button(key="home_lists_interested").label == "Interested (2)"
    assert at.button(key="home_lists_not_for_me").label == "Not for me (1)"


def test_dashboard_button_opens_the_list():
    from src.ui.state import FEEDBACK_KEY
    at = open_page(None, profile=WORKED_EXAMPLE, **{FEEDBACK_KEY: {"C029": -1}})
    at.button(key="home_lists_not_for_me").click().run()
    assert not at.exception
    assert at.session_state["career_list_view"] == "not_for_me"
    assert "to_int_C029" in button_keys(at)


def test_lists_are_written_to_the_address_bar():
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE)
    at.button(key="like_C002").click().run()
    at.button(key="dislike_C029").click().run()
    assert at.query_params["interested"] in ("C002", ["C002"])
    assert at.query_params["not_for_me"] in ("C029", ["C029"])
    at.button(key="clear_feedback").click().run()
    assert "interested" not in at.query_params and "not_for_me" not in at.query_params


def test_lists_survive_a_page_refresh():
    # A refresh starts a new session with the same address, but without the answers
    from src.ui.state import FEEDBACK_KEY
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.query_params["interested"] = "C002,C003"
    at.query_params["not_for_me"] = "C029"
    at.run()
    at.switch_page("pages/2_Recommendations.py")
    at.run()
    assert not at.exception
    assert at.session_state[FEEDBACK_KEY] == {"C002": 1, "C003": 1, "C029": -1}
    assert [o.strip() for o in at.button_group(key="career_list_view").options] == ["Interested (2)",
                                                                                     "Not for me (1)"]
    assert {"to_not_C002", "to_not_C003"} <= button_keys(at)
    assert "Complete the assessment to see your score." in text_of(at)


def test_bad_address_values_are_ignored():
    from src.ui.state import FEEDBACK_KEY
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.query_params["interested"] = "C002,C999,<script>"
    at.query_params["not_for_me"] = "C002,C029"
    at.run()
    assert not at.exception
    assert at.session_state[FEEDBACK_KEY] == {"C029": -1}


def test_cleared_lists_are_not_restored_in_the_same_session():
    from src.ui.state import FEEDBACK_KEY
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.query_params["interested"] = "C002"
    at.session_state[PROFILE_KEY] = WORKED_EXAMPLE
    at.run()
    at.switch_page("pages/2_Recommendations.py")
    at.run()
    at.button(key="clear_feedback").click().run()
    at.run()
    assert FEEDBACK_KEY not in at.session_state


def test_explorer_can_change_the_decision():
    from src.ui.state import EXPLORER_CAREER_KEY, FEEDBACK_KEY
    at = open_page("pages/4_Career_Explorer.py", **{EXPLORER_CAREER_KEY: "C040"})
    at.button(key="explorer_like").click().run()
    assert at.session_state[FEEDBACK_KEY] == {"C040": 1}
    assert "In your Interested list" in text_of(at)
    at.button(key="explorer_dislike").click().run()
    assert at.session_state[FEEDBACK_KEY] == {"C040": -1}
    at.button(key="explorer_remove").click().run()
    assert at.session_state[FEEDBACK_KEY] == {}


def test_saved_list_links_open_details_and_skill_gap():
    from src.ui.state import EXPLORER_CAREER_KEY, FEEDBACK_KEY
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE, **{FEEDBACK_KEY: {"C040": 1}})
    open_list(at, "interested")
    at.button(key="saved_gap_C040").click().run()
    assert not at.exception
    assert at.session_state[SELECTED_CAREER_KEY] == "C040"
    assert any("Missing required skills" == m.label for m in at.metric)
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE, **{FEEDBACK_KEY: {"C040": 1}})
    open_list(at, "interested")
    at.button(key="saved_explore_C040").click().run()
    assert at.session_state[EXPLORER_CAREER_KEY] == "C040"
    assert "### Registered Nurse" in text_of(at)


def test_analytics_and_model_comparison_work_with_saved_lists():
    from src.ui.state import FEEDBACK_KEY
    at = open_page("pages/5_Analytics.py", profile=WORKED_EXAMPLE, **{FEEDBACK_KEY: {"C002": 1, "C029": -1}})
    assert "How the Models Rank Your Careers" in text_of(at)
    assert "#### Random Forest" in text_of(at)


ROADMAP = "pages/6_Skill_Roadmap.py"


def test_roadmap_without_any_career_explains_how_to_choose():
    at = open_page(ROADMAP)
    text = text_of(at)
    assert "My Skill Development Roadmap" in text
    assert "Choose a career first" in text


def test_roadmap_offers_interested_careers_first_and_recommendations():
    from src.ui.state import FEEDBACK_KEY
    at = open_page(ROADMAP, profile=WORKED_EXAMPLE, **{FEEDBACK_KEY: {"C040": 1, "C001": -1}})
    options = at.selectbox[0].options
    assert options[0] == "Registered Nurse (Interested)"
    assert any("(Recommended)" in o for o in options)
    assert not any(o.startswith("Data Scientist") for o in options)
    labels = {m.label: m.value for m in at.metric}
    assert labels["Steps"] == str(len([k for k in button_keys(at) if k and k.startswith("learned_")]))
    assert "Ordered learning plan" in text_of(at)


def test_roadmap_status_updates_and_progress():
    from src.ui.state import ROADMAP_CAREER_KEY, ROADMAP_KEY
    at = open_page(ROADMAP, profile=WORKED_EXAMPLE, **{ROADMAP_CAREER_KEY: "C001"})
    control = at.button_group(key="status_C001_git")
    control.set_value("in_progress").run()
    assert not at.exception
    assert at.session_state[ROADMAP_KEY] == {"C001": {"git": "in_progress"}}
    at.button_group(key="status_C001_git").set_value("completed").run()
    assert at.session_state[ROADMAP_KEY] == {"C001": {"git": "completed"}}
    labels = {m.label: m.value for m in at.metric}
    assert labels["Completed"] == "1" and labels["Steps"] == "4"
    assert len(at.get("progress")) == 1
    assert "Completing a step means you marked it done" in text_of(at)
    # Completing a step does not add the skill to the profile
    assert "git" not in [s.lower() for s in at.session_state["profile_input"]["skills"]]


def test_roadmap_progress_is_separate_per_career_and_survives_not_for_me():
    from src.ui.state import FEEDBACK_KEY, ROADMAP_CAREER_KEY, ROADMAP_KEY
    progress = {"C001": {"git": "completed"}, "C009": {"git": "in_progress"}}
    at = open_page(ROADMAP, profile=WORKED_EXAMPLE, **{ROADMAP_KEY: progress, FEEDBACK_KEY: {"C001": 1},
                                                       ROADMAP_CAREER_KEY: "C001"})
    assert at.button_group(key="status_C001_git").value == "completed"
    at.switch_page("pages/2_Recommendations.py")
    at.run()
    at.button_group(key="career_list_view").set_value("interested").run()
    at.button(key="to_not_C001").click().run()
    at.switch_page(ROADMAP)
    at.run()
    assert at.session_state[ROADMAP_KEY] == progress
    options = at.selectbox[0].options
    assert "Data Scientist (Not for me, progress kept)" in options
    at.selectbox[0].set_value("C001").run()
    assert "You marked this career Not for me" in text_of(at)
    at.selectbox[0].set_value("C009").run()
    assert at.button_group(key="status_C009_git").value == "in_progress"


def test_learned_skill_needs_confirmation_and_recalculates():
    from src.ui.state import ROADMAP_CAREER_KEY
    at = open_page(ROADMAP, profile=WORKED_EXAMPLE, **{ROADMAP_CAREER_KEY: "C001"})
    at.button(key="learned_C001_data_visualization").click().run()
    assert "data visualization" not in at.session_state[PROFILE_KEY]["skills"]
    at.button(key="cancel_C001_data_visualization").click().run()
    assert "data visualization" not in at.session_state[PROFILE_KEY]["skills"]
    at.button(key="learned_C001_data_visualization").click().run()
    at.button(key="yes_C001_data_visualization").click().run()
    assert not at.exception
    assert "data visualization" in at.session_state[PROFILE_KEY]["skills"]
    labels = {m.label: m.value for m in at.metric}
    assert labels["Required skills you have"] == "5 of 5" and labels["Compatibility score"] != "61.5 / 100"
    assert "learned_C001_data_visualization" not in button_keys(at)


def test_deleting_a_roadmap_needs_confirmation():
    from src.ui.state import ROADMAP_CAREER_KEY, ROADMAP_KEY
    at = open_page(ROADMAP, profile=WORKED_EXAMPLE, **{ROADMAP_KEY: {"C001": {"git": "completed"}},
                                                       ROADMAP_CAREER_KEY: "C001"})
    at.button(key="delete_roadmap").click().run()
    assert at.session_state[ROADMAP_KEY] == {"C001": {"git": "completed"}}
    at.button(key="confirm_delete_roadmap").click().run()
    assert at.session_state[ROADMAP_KEY] == {}


def test_roadmap_progress_survives_a_refresh_and_bad_values_are_ignored():
    from src.ui.state import ROADMAP_KEY
    at = open_page(ROADMAP, profile=WORKED_EXAMPLE, roadmap_career_id="C001")
    at.button_group(key="status_C001_git").set_value("completed").run()
    assert at.query_params["progress"] in ("C001:git=c", ["C001:git=c"])
    fresh = AppTest.from_file(APP, default_timeout=TIMEOUT)
    fresh.query_params["progress"] = "C001:git=c,unknown skill=c;C999:git=p"
    fresh.run()
    assert not fresh.exception
    assert fresh.session_state[ROADMAP_KEY] == {"C001": {"git": "completed"}}


def test_each_session_has_its_own_roadmap():
    # There are no accounts: progress lives in each browser session and is never shared
    from src.ui.state import ROADMAP_KEY
    a = open_page(ROADMAP, profile=WORKED_EXAMPLE, roadmap_career_id="C001")
    a.button_group(key="status_C001_git").set_value("completed").run()
    b = open_page(ROADMAP, profile=WORKED_EXAMPLE, roadmap_career_id="C001")
    assert ROADMAP_KEY not in b.session_state
    assert b.button_group(key="status_C001_git").value == "not_started"


def test_interested_list_and_skill_gap_link_to_the_roadmap():
    from src.ui.state import FEEDBACK_KEY, ROADMAP_CAREER_KEY
    at = open_page("pages/2_Recommendations.py", profile=WORKED_EXAMPLE, **{FEEDBACK_KEY: {"C040": 1}})
    at.button_group(key="career_list_view").set_value("interested").run()
    at.button(key="saved_plan_C040").click().run()
    assert not at.exception
    assert at.session_state[ROADMAP_CAREER_KEY] == "C040"
    assert at.selectbox[0].value == "C040"
    at = open_page(SKILL_GAP_PAGE_PATH, profile=WORKED_EXAMPLE)
    at.button(key="gap_to_roadmap").click().run()
    assert not at.exception and "Ordered learning plan" in text_of(at)


SKILL_GAP_PAGE_PATH = "pages/3_Skill_Gap_Analysis.py"
