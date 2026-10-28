# Session feedback re-ranking and the downloadable session file

import json

import pytest

from src.services.catalog import load_catalog
from src.services.feedback import (
    INTERESTED, MAX_ADJUSTMENT, NOT_FOR_ME, adapt_recommendations, career_similarity, clean_feedback,
)
from src.services.recommendations import recommend
from src.services.session_data import MAX_BYTES, SessionFileError, export_session, import_session

PROFILE = {"skills": ["python", "sql", "excel", "machine learning", "statistics"],
           "interests": ["analysis", "mathematics"], "education_level": 3}


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


@pytest.fixture(scope="module")
def recs(catalog):
    return recommend(PROFILE, catalog, top_k=None)["recommendations"]


def ids(rows):
    return [r["career_id"] for r in rows]


def test_similarity_bounds_and_symmetry(catalog):
    a, b = catalog.get_career("C001"), catalog.get_career("C002")
    assert career_similarity(a, a) == pytest.approx(1.0)
    assert career_similarity(a, b) == pytest.approx(career_similarity(b, a))
    assert 0.0 <= career_similarity(a, catalog.get_career("C040")) < 0.15


def test_no_feedback_keeps_formula_order_and_scores(catalog, recs):
    shown, hidden = adapt_recommendations(recs, catalog, {})
    assert ids(shown) == ids(recs) and hidden == []
    assert all(r["adjusted_score"] == r["formula_score"] == r["score"] for r in shown)
    assert all(r["feedback_adjustment"] == 0 and r["feedback_reasons"] == [] for r in shown)


def test_interest_moves_similar_careers_up_with_reasons(catalog, recs):
    base_rank = ids(recs).index("C006")
    shown, _ = adapt_recommendations(recs, catalog, {"C002": INTERESTED})
    stat = next(r for r in shown if r["career_id"] == "C006")
    assert stat["feedback_adjustment"] > 0
    assert ids(shown).index("C006") <= base_rank
    assert stat["adjusted_score"] > stat["formula_score"]
    assert any(ids(shown).index(c) < ids(recs).index(c) for c in ids(recs)[:15])
    assert any("Data Analyst" in reason for reason in stat["feedback_reasons"])
    liked = next(r for r in shown if r["career_id"] == "C002")
    assert liked["user_feedback"] == INTERESTED and liked["feedback_adjustment"] == 0


def test_not_for_me_hides_career_and_lowers_similar_ones(catalog, recs):
    shown, hidden = adapt_recommendations(recs, catalog, {"C029": NOT_FOR_ME})
    assert ids(hidden) == ["C029"] and "C029" not in ids(shown)
    assert hidden[0]["rank"] is None
    business = [r for r in shown if r["category"] == "Business"]
    assert all(r["feedback_adjustment"] <= 0 for r in business)
    assert [r["rank"] for r in shown] == list(range(1, len(shown) + 1))


def test_formula_score_is_never_changed(catalog, recs):
    shown, hidden = adapt_recommendations(recs, catalog, {"C002": INTERESTED, "C029": NOT_FOR_ME})
    by_id = {r["career_id"]: r["score"] for r in recs}
    assert all(r["formula_score"] == by_id[r["career_id"]] for r in shown + hidden)


def test_adjustment_is_capped(catalog, recs):
    feedback = {c.career_id: INTERESTED for c in catalog.careers if c.category == "Data and AI" and c.career_id != "C001"}
    shown, _ = adapt_recommendations(recs, catalog, feedback)
    top = next(r for r in shown if r["career_id"] == "C001")
    assert top["feedback_adjustment"] == MAX_ADJUSTMENT
    assert any("limited" in reason for reason in top["feedback_reasons"])
    assert all(0 <= r["adjusted_score"] <= 100 for r in shown)


def test_invalid_feedback_entries_are_ignored(catalog, recs):
    assert clean_feedback({"C001": 1, "C999": 1, "C002": 5}, [c.career_id for c in catalog.careers]) == {"C001": 1}
    shown, hidden = adapt_recommendations(recs, catalog, {"C999": 1, "C002": 0})
    assert ids(shown) == ids(recs) and hidden == []


def test_adaptation_is_deterministic(catalog, recs):
    fb = {"C002": INTERESTED, "C029": NOT_FOR_ME}
    assert adapt_recommendations(recs, catalog, fb) == adapt_recommendations(recs, catalog, fb)


def test_session_file_round_trip(catalog):
    raw = export_session(PROFILE, {"C002": 1, "C029": -1})
    data = json.loads(raw)
    assert data["format"] == "career-recommendation-session" and data["version"] == 1
    profile, feedback = import_session(raw, catalog)
    assert profile == PROFILE and feedback == {"C002": 1, "C029": -1}


@pytest.mark.parametrize("raw, message", [
    (b"", "empty"),
    (b"{not json", "not valid JSON"),
    (json.dumps({"format": "other"}).encode(), "not a session file"),
    (json.dumps({"format": "career-recommendation-session", "version": 9, "profile": {}}).encode(), "version"),
    (json.dumps({"format": "career-recommendation-session", "version": 1, "profile": {"password": "x"}}).encode(),
     "unexpected format"),
    (json.dumps({"format": "career-recommendation-session", "version": 1, "profile": {"skills": "python"}}).encode(),
     "not valid"),
    (json.dumps({"format": "career-recommendation-session", "version": 1, "profile": {"skills": ["python"]},
                 "feedback": {"C999": 1}}).encode(), "unknown career"),
    (json.dumps({"format": "career-recommendation-session", "version": 1, "profile": {"skills": ["python"]},
                 "feedback": {"C001": True}}).encode(), "unknown career or value"),
])
def test_bad_session_files_are_rejected(catalog, raw, message):
    with pytest.raises(SessionFileError, match=message):
        import_session(raw, catalog)


def test_oversized_session_file_is_rejected(catalog):
    with pytest.raises(SessionFileError, match="too large"):
        import_session(b" " * (MAX_BYTES + 1), catalog)


def test_lists_are_split_and_never_overlap():
    from src.services.feedback import split_lists
    assert split_lists({"C003": 1, "C001": 1, "C029": -1}) == (["C001", "C003"], ["C029"])
    assert split_lists({}) == ([], [])


def test_query_round_trip_and_validation(catalog):
    from src.services.feedback import feedback_from_query, feedback_to_query
    ids_ = [c.career_id for c in catalog.careers]
    fb = {"C002": INTERESTED, "C001": INTERESTED, "C029": NOT_FOR_ME}
    params = feedback_to_query(fb)
    assert params == {"interested": "C001,C002", "not_for_me": "C029"}
    assert feedback_from_query(params, ids_) == fb
    assert feedback_to_query({}) == {}
    assert feedback_from_query({"interested": "C001,C999", "not_for_me": "C001,C029"}, ids_) == {"C029": NOT_FOR_ME}
    assert feedback_from_query({"interested": "C001," * 400}, ids_) == {}
    assert feedback_from_query({"interested": None}, ids_) == {}
