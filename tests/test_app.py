# Streamlit pages run through AppTest, starting from app.py like a real session

from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from src.ui.state import DATA_DIR_ENV, PROFILE_KEY, SELECTED_CAREER_KEY  # noqa: E402
from tests.conftest import live_counts  # noqa: E402

N_CAREERS = live_counts()["careers"]

TIMEOUT = 60
APP = str(Path(__file__).resolve().parents[1] / "app.py")
# Interest assignments changed in dataset v1.4.0 (taxonomy 2.0), so the scores below changed with them
WORKED_EXAMPLE = {"skills": ["Python", "SQL", "Excel", "ML", "statistics"],
                  "interests": ["Analysing data and information", "Working with numbers and calculations"],
                  "education_level": 3}


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
    from src.services.catalog import load_catalog
    counts, catalog = live_counts(), load_catalog()
    categories = len({c.category for c in catalog.careers})
    expected = [str(counts["careers"]), str(categories), str(counts["skills"]), str(counts["resources"])]
    assert [m.value for m in at.metric][:4] == expected


def test_assessment_saves_normalized_profile_and_reports_unknown_skills():
    at = open_page("pages/1_Career_Assessment.py")
    at.multiselect[0].set_value(["python", "sql"])
    at.text_area[0].input("ML, machine learning, blockchain")
    at.multiselect(key="interest_picker").select("analysing data and information").run()
    at.selectbox[0].set_value(3)
    at.button(key="save_assessment").click().run()
    assert not at.exception
    saved = at.session_state[PROFILE_KEY]
    assert saved["skills"] == ["python", "sql", "ML", "machine learning", "blockchain"]
    assert saved["interests"] == ["analysing data and information"]
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
    assert scores[:5] == ["65.7 / 100", "59.6 / 100", "55.0 / 100", "50.8 / 100", "44.2 / 100"]
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
    # The general link-check notice was removed on 3 November 2026; the per-resource status above stays
    assert "was not opened by the checker" not in text_of(at)


def test_skill_gap_without_profile_shows_all_skills_missing():
    at = open_page("pages/3_Skill_Gap_Analysis.py", **{SELECTED_CAREER_KEY: "C040"})
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Required skill coverage"] == "0%"
    assert "every skill is shown as missing" in text_of(at)


def test_explorer_filters_by_category_and_search():
    at = open_page("pages/4_Career_Explorer.py")
    assert f"Showing {N_CAREERS} of {N_CAREERS} careers." in text_of(at)
    at.multiselect[0].set_value(["Healthcare"]).run()
    assert f"Showing 7 of {N_CAREERS} careers." in text_of(at)
    at.text_input[0].input("nurse").run()
    assert f"Showing 1 of {N_CAREERS} careers." in text_of(at)
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
    assert len(at.dataframe[0].value) == N_CAREERS


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
    assert "1. **Data Scientist** :gray[65.7 / 100]" in text
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
    assert labels["Required skills you have"] == "5 of 5" and labels["Compatibility score"] != "65.7 / 100"
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


@pytest.mark.parametrize("content", [None, "{not json", '{"data": {"profiles": 36}}'])
def test_analytics_survives_a_missing_or_broken_results_file(tmp_path, monkeypatch, content):
    import src.ui.views as views
    path = tmp_path / "ml_results.json"
    if content is not None:
        path.write_text(content, encoding="utf-8")
    monkeypatch.setattr(views, "ML_REPORT_PATH", path)
    at = open_page("pages/5_Analytics.py", profile=WORKED_EXAMPLE)
    text = text_of(at)
    assert "The saved model comparison results are not available" in text
    assert "How the Models Rank Your Careers" in text
    assert len(at.dataframe) == 0


def test_analytics_caption_without_counts(tmp_path, monkeypatch):
    import json as _json

    import src.ui.views as views
    saved = _json.loads(views.ML_REPORT_PATH.read_text(encoding="utf-8"))
    saved.pop("data")
    path = tmp_path / "ml_results.json"
    path.write_text(_json.dumps(saved), encoding="utf-8")
    monkeypatch.setattr(views, "ML_REPORT_PATH", path)
    at = open_page("pages/5_Analytics.py")
    text = text_of(at)
    assert "These results come from synthetic profiles" in text and "the original catalogue" in text
    assert len(at.dataframe) == 1


def test_expanded_catalogue_in_the_interface():
    at = open_page()
    assert [m.value for m in at.metric][:2] == ["64", "10"]
    at = open_page("pages/4_Career_Explorer.py")
    at.multiselect[0].set_value(["Law"]).run()
    assert "Showing 2 of 64 careers." in text_of(at)
    at.multiselect[0].set_value(["Social Sciences"]).run()
    assert "Showing 2 of 64 careers." in text_of(at)


def test_analytics_category_chart_has_all_ten_categories():
    at = open_page("pages/5_Analytics.py")
    assert not at.exception
    chart = at.get("plotly_chart")[0]
    import json as _json
    spec = _json.loads(chart.proto.spec)
    labels = spec["data"][0]["y"]
    assert len(labels) == 10 and {"Law", "Social Sciences"} <= set(labels)
    colors = spec["data"][0]["marker"]["color"]
    assert len(set(colors)) == 10


def test_new_career_recommendation_and_skill_gap_pages():
    law_profile = {"skills": ["legal research", "contract law", "ohada business law", "communication"],
                   "interests": ["analysis", "writing", "business"], "education_level": 4}
    at = open_page("pages/2_Recommendations.py", profile=law_profile)
    assert "### 1. Private Law Specialist" in text_of(at)
    at = open_page("pages/3_Skill_Gap_Analysis.py", profile={"skills": ["geology"], "interests": ["science"]},
                   **{SELECTED_CAREER_KEY: "C056"})
    assert not at.exception
    text = text_of(at)
    assert "Geophysicist" in text and "Geophysics for Practicing Geoscientists" in text


# ---------- Interest taxonomy 2.0 in the assessment form ----------

def picker(at):
    return at.multiselect(key="interest_picker")


def test_assessment_offers_the_23_interests_in_one_grouped_dropdown():
    from src.data.interest_taxonomy import INTEREST_TERMS
    from src.ui.interest_picker import GROUP_WORDS, ordered_keys
    at = open_page("pages/1_Career_Assessment.py")
    assert len(at.checkbox) == 0
    widget = picker(at)
    labels = list(widget.options)
    assert len(labels) == 23 == len(set(labels))
    # Grouped: every option starts with its plain group word, and the groups appear in order
    words = [label.split(" · ")[0] for label in labels]
    assert set(words) == set(GROUP_WORDS.values())
    assert words == sorted(words, key=list(dict.fromkeys(words)).index)
    assert labels[0] == f"Practical · {INTEREST_TERMS[0].label}" and len(ordered_keys()) == 23
    text = text_of(at)
    assert "You do not need the skills yet" in text
    assert any(e.label == "Browse all 23 interests with descriptions" for e in at.expander)
    assert not any(t.label_fr_draft in text for t in INTEREST_TERMS)


def test_dropdown_never_offers_select_all_and_searches_by_substring():
    at = open_page("pages/1_Career_Assessment.py")
    proto = picker(at).proto
    # 0 hides the option; the skills dropdown keeps Streamlit's default, which shows it, so the check is sensitive
    assert proto.select_all == 0 and at.multiselect[0].proto.select_all > 0
    mode = proto.DESCRIPTOR.fields_by_name["filter_mode"].enum_type.values_by_number[proto.filter_mode].name
    assert mode == "FILTER_MODE_CONTAINS" and proto.wrap is True


def test_selecting_updates_chips_counter_and_descriptions_at_once():
    at = open_page("pages/1_Career_Assessment.py")
    picker(at).select("managing money and financial information").run()
    picker(at).select("working with communities").run()
    assert not at.exception
    assert picker(at).value == ["managing money and financial information", "working with communities"]
    text = text_of(at)
    assert "2 interests selected" in text and "Your selected interests" in text
    assert "Planning a budget for an event" in text and "Related skill, not the same thing: Accounting" in text
    assert PROFILE_KEY not in at.session_state


def test_removing_a_chip_updates_the_counter():
    at = open_page("pages/1_Career_Assessment.py")
    picker(at).set_value(["writing and editing", "teaching and training others"]).run()
    picker(at).unselect("writing and editing").run()
    assert picker(at).value == ["teaching and training others"]
    assert "1 interest selected" in text_of(at)


def test_more_than_five_interests_warns_live_and_saves_all():
    from src.ui.interest_picker import ordered_keys
    at = open_page("pages/1_Career_Assessment.py")
    picker(at).set_value(ordered_keys()[:5]).run()
    assert not any("You chose" in w.value for w in at.warning)
    picker(at).set_value(ordered_keys()[:6]).run()
    assert any("You chose 6 interests" in w.value for w in at.warning)
    assert "6 interests selected" in text_of(at)
    at.button(key="save_assessment").click().run()
    assert not at.exception
    assert at.session_state[PROFILE_KEY]["interests"] == ordered_keys()[:6]


def test_description_search_narrows_options_and_keeps_choices():
    at = open_page("pages/1_Career_Assessment.py")
    picker(at).select("writing and editing").run()
    at.text_input(key="interest_search").input("mine").run()
    labels = list(picker(at).options)
    assert "Practical · Working outdoors and with the natural environment" in labels
    assert "Creative · Writing and editing" in labels
    assert len(labels) < 23
    assert picker(at).value == ["writing and editing"]
    at.text_input(key="interest_search").input("").run()
    assert len(picker(at).options) == 23


def test_saved_old_interest_names_are_preselected_after_migration():
    at = open_page("pages/1_Career_Assessment.py", profile={"interests": ["mathematics", "technology"]})
    assert picker(at).value == ["working with numbers and calculations"]
    assert any("old interest names" in i.value and "technology" in i.value for i in at.info)


def test_dropdown_and_direct_input_give_identical_recommendations():
    from src.services.catalog import load_catalog
    from src.services.recommendations import recommend
    chosen = ["running and growing a business", "analysing data and information", "working with communities"]
    at = open_page("pages/1_Career_Assessment.py")
    at.multiselect[0].set_value(["python", "excel"])
    picker(at).set_value(chosen).run()
    at.selectbox[0].set_value(3)
    at.button(key="save_assessment").click().run()
    saved = at.session_state[PROFILE_KEY]
    assert saved["interests"] == chosen
    catalog = load_catalog()
    via_form = recommend(saved, catalog, top_k=None)["recommendations"]
    direct = recommend({"skills": ["python", "excel"], "interests": list(reversed(chosen)), "education_level": 3},
                       catalog, top_k=None)["recommendations"]
    assert [(r["career_id"], r["score"]) for r in via_form] == [(r["career_id"], r["score"]) for r in direct]


def test_explorer_shows_full_interest_names():
    at = open_page("pages/4_Career_Explorer.py")
    assert not at.exception
    assert "Analysing data and information" in text_of(at)


def test_outdated_interest_update_notice_is_gone():
    # The November 2026 notice (blue box and one-line caption) was removed at the owner's request on 3 November 2026
    for profile in (None, {"interests": ["writing and editing"]}, {"interests": ["mathematics", "technology"]}):
        at = open_page("pages/1_Career_Assessment.py", profile=profile)
        page = "\n".join(str(e.value) for e in list(at.info) + list(at.caption) + list(at.markdown))
        assert "interest list was updated" not in page and "old list of 20 short words" not in page
        # Everything else in the interest section is still there
        assert picker(at).proto.select_all == 0 and len(picker(at).options) == 23
        assert "You do not need the skills yet" in page


def test_old_session_note_still_explains_migrated_names():
    at = open_page("pages/1_Career_Assessment.py", profile={"interests": ["mathematics", "technology"]})
    notes = [i.value for i in at.info if "old interest names" in i.value]
    assert notes and "mathematics became Working with numbers and calculations" in notes[0]
    assert "technology" in notes[0]

