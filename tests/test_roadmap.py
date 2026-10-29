# Skill development roadmap: generation, ordering, resources, progress and saved-data handling

import json
from dataclasses import replace

import pytest

from src.services.catalog import load_catalog
from src.services.learning_resources import ResourceCatalog
from src.services.recommendations import recommend
from src.services.roadmap import (
    COMPLETED, IN_PROGRESS, NOT_STARTED, OPTIONAL, PREREQUISITE, REQUIRED, RoadmapError, add_skill_to_profile,
    build_roadmap, clean_progress, delete_roadmap, order_skills, progress_from_query, progress_summary,
    progress_to_query, select_resources, set_step_status, skill_demand,
)
from src.services.session_data import SessionFileError, export_session, import_session, import_session_data

PROFILE = {"skills": ["python", "sql", "excel", "machine learning", "statistics"],
           "interests": ["analysis", "mathematics"], "education_level": 3}


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


def skills_of(roadmap):
    return [s["skill"] for s in roadmap["steps"]]


def test_roadmap_for_a_valid_career_uses_the_skill_gap(catalog):
    rm = build_roadmap(PROFILE, "C001", catalog)
    career = catalog.get_career("C001")
    assert rm["career_title"] == "Data Scientist" and rm["category"] == "Data and AI"
    assert rm["fit"] == {"score": 61.5, "rank": 1, "careers_ranked": 50}
    assert rm["missing_required_skills"] == ["data visualization"]
    assert sorted(rm["missing_preferred_skills"]) == sorted(career.preferred_skills)
    assert skills_of(rm)[0] == "data visualization"
    assert [s["kind"] for s in rm["steps"]] == [REQUIRED, OPTIONAL, OPTIONAL, OPTIONAL]
    assert [s["step"] for s in rm["steps"]] == [1, 2, 3, 4]
    for step in rm["steps"]:
        assert step["status"] == NOT_STARTED
        assert step["why"] and step["prerequisites"] == []
        urls = {r.url for r in catalog.resources.for_skill(step["skill"], catalog.aliases)}
        assert step["resources"] and step["resources"][0]["url"] in urls
    assert "not a verified prerequisite chain" in rm["order_note"]


def test_required_before_optional_and_most_required_first(catalog):
    demand = skill_demand(catalog)
    rm = build_roadmap(None, "C001", catalog)
    kinds = [s["kind"] for s in rm["steps"]]
    assert kinds == sorted(kinds, key=lambda k: k != REQUIRED)
    req = [s["skill"] for s in rm["steps"] if s["kind"] == REQUIRED]
    counts = [demand[s][0] for s in req]
    assert counts == sorted(counts, reverse=True)
    assert rm["fit"] is None


def test_career_with_no_missing_required_skills(catalog):
    career = catalog.get_career("C001")
    rm = build_roadmap({"skills": list(career.required_skills)}, "C001", catalog)
    assert rm["meets_all_required"] and rm["missing_required_skills"] == []
    assert all(s["kind"] == OPTIONAL for s in rm["steps"])
    full = build_roadmap({"skills": list(career.required_skills + career.preferred_skills)}, "C001", catalog)
    assert full["steps"] == [] and full["progress"]["completion_percent"] is None


def test_missing_resource_is_reported(catalog):
    kept = [r for items in catalog.resources._index.values() for r in items if r.skill_name != "git"]
    thin = replace(catalog, resources=ResourceCatalog(kept))
    rm = build_roadmap(PROFILE, "C001", thin)
    git = next(s for s in rm["steps"] if s["skill"] == "git")
    assert git["resources"] == [] and "No learning resource" in git["resource_note"]


class _FakeResources:
    def __init__(self, table):
        self.table = table

    def for_skill(self, skill, aliases=None):
        return self.table.get(skill, ())


class _FakeCatalog:
    def __init__(self, table):
        self.resources, self.aliases = _FakeResources(table), {}


def test_resources_are_not_repeated_when_an_alternative_exists(catalog):
    a, b = catalog.resources.for_skill("python")[0], catalog.resources.for_skill("sql")[0]
    chosen = select_resources(["x", "y"], _FakeCatalog({"x": (a, b), "y": (a, b)}))
    assert chosen["x"]["resources"][0]["resource_id"] == a.resource_id
    assert chosen["y"]["resources"][0]["resource_id"] == b.resource_id
    shared = select_resources(["x", "y"], _FakeCatalog({"x": (a,), "y": (a,)}))
    assert "Same resource as step 1" in shared["y"]["note"]


def test_known_prerequisites_are_respected(catalog):
    rm = build_roadmap(PROFILE, "C001", catalog, prerequisites={"data visualization": ["git"]})
    order = skills_of(rm)
    assert order.index("git") < order.index("data visualization")
    dv = next(s for s in rm["steps"] if s["skill"] == "data visualization")
    assert dv["prerequisites"] == [{"skill": "git", "have": False}]
    extra = build_roadmap(PROFILE, "C001", catalog, prerequisites={"data visualization": ["linux", "python"]})
    linux = next(s for s in extra["steps"] if s["skill"] == "linux")
    assert linux["kind"] == PREREQUISITE and skills_of(extra).index("linux") < skills_of(extra).index(
        "data visualization")
    assert "python" not in skills_of(extra)
    assert "Known prerequisites" in extra["order_note"]


def test_no_duplicate_steps_even_with_cycles_or_repeats(catalog):
    demand = skill_demand(catalog)
    assert order_skills(["git", "sql", "git"], demand).count("git") == 1
    rm = build_roadmap(PROFILE, "C001", catalog, prerequisites={"git": ["deep learning"], "deep learning": ["git"]})
    assert len(skills_of(rm)) == len(set(skills_of(rm)))
    assert build_roadmap(PROFILE, "C001", catalog) == build_roadmap(PROFILE, "C001", catalog)


def test_progress_percentages(catalog):
    steps = [{"status": COMPLETED}, {"status": IN_PROGRESS}, {"status": NOT_STARTED}, {"status": COMPLETED}]
    assert progress_summary(steps) == {"total_steps": 4, "completed": 2, "in_progress": 1, "not_started": 1,
                                       "completion_percent": 50.0}
    assert progress_summary([{"status": COMPLETED}] * 3)["completion_percent"] == 100.0
    assert progress_summary([])["completion_percent"] is None


def test_step_status_moves_through_the_three_states(catalog):
    p = set_step_status({}, "C001", "git", IN_PROGRESS)
    assert p == {"C001": {"git": IN_PROGRESS}}
    p = set_step_status(p, "C001", "git", COMPLETED)
    rm = build_roadmap(PROFILE, "C001", catalog, p["C001"])
    assert next(s for s in rm["steps"] if s["skill"] == "git")["status"] == COMPLETED
    assert rm["progress"]["completed"] == 1 and rm["progress"]["completion_percent"] == 25.0
    assert set_step_status(p, "C001", "git", NOT_STARTED) == {}
    with pytest.raises(RoadmapError):
        set_step_status(p, "C001", "git", "mastered")


def test_progress_stays_separate_between_careers(catalog):
    p = set_step_status({}, "C001", "git", COMPLETED)
    p = set_step_status(p, "C009", "git", IN_PROGRESS)
    a = build_roadmap(PROFILE, "C001", catalog, p.get("C001"))
    b = build_roadmap(PROFILE, "C009", catalog, p.get("C009"))
    assert next(s for s in a["steps"] if s["skill"] == "git")["status"] == COMPLETED
    assert next(s for s in b["steps"] if s["skill"] == "git")["status"] == IN_PROGRESS
    assert delete_roadmap(p, "C001") == {"C009": {"git": IN_PROGRESS}}


def test_confirmed_profile_update_recalculates_gap_and_score(catalog):
    p = set_step_status({}, "C001", "data visualization", COMPLETED)
    before = build_roadmap(PROFILE, "C001", catalog, p["C001"])
    # Completing a step alone never changes the skill gap
    assert "data visualization" in before["missing_required_skills"]
    updated = add_skill_to_profile(PROFILE, "data visualization", catalog)
    assert add_skill_to_profile(updated, "Data Visualization", catalog) == updated
    after = build_roadmap(updated, "C001", catalog, p["C001"])
    assert after["meets_all_required"] and "data visualization" not in skills_of(after)
    assert after["fit"]["score"] > before["fit"]["score"]
    assert after["saved_outside_steps"] == ["data visualization"]
    new_score = next(r["score"] for r in recommend(updated, catalog, top_k=None)["recommendations"]
                     if r["career_id"] == "C001")
    assert new_score == after["fit"]["score"]
    assert PROFILE["skills"] == ["python", "sql", "excel", "machine learning", "statistics"]


def test_invalid_career_and_malformed_progress(catalog):
    with pytest.raises(RoadmapError):
        build_roadmap(PROFILE, "C999", catalog)
    clean, issues = clean_progress({"C999": {"git": COMPLETED}, "C001": {"git": COMPLETED, "old skill": COMPLETED,
                                    "sql": "done", "docker": NOT_STARTED}, "C002": ["git"]}, catalog)
    assert clean == {"C001": {"git": COMPLETED}}
    assert len(issues) == 4
    assert clean_progress("nonsense", catalog)[0] == {}
    assert clean_progress(None, catalog) == ({}, [])
    rm = build_roadmap(PROFILE, "C001", catalog, {"git": "weird"})
    assert next(s for s in rm["steps"] if s["skill"] == "git")["status"] == NOT_STARTED


def test_progress_query_round_trip_and_bad_values(catalog):
    p = {"C009": {"git": IN_PROGRESS}, "C001": {"git": COMPLETED, "deep learning": IN_PROGRESS}}
    text = progress_to_query(p)
    assert text == "C001:deep learning=p,git=c;C009:git=p"
    assert progress_from_query(text, catalog) == {"C001": {"deep learning": IN_PROGRESS, "git": COMPLETED},
                                                   "C009": {"git": IN_PROGRESS}}
    assert progress_from_query("C999:git=c;C001:nope=c,git=x;garbage", catalog) == {}
    assert progress_from_query("C001:git=c;" * 400, catalog) == {}
    assert progress_from_query(None, catalog) == {}


def test_session_file_keeps_roadmaps_and_reads_version_one(catalog):
    p = {"C001": {"git": COMPLETED}}
    raw = export_session(PROFILE, {"C001": 1}, p)
    assert json.loads(raw)["version"] == 2
    profile, feedback, roadmaps, issues = import_session_data(raw, catalog)
    assert (profile, feedback, roadmaps, issues) == (PROFILE, {"C001": 1}, p, [])
    old = json.dumps({"format": "career-recommendation-session", "version": 1, "profile": PROFILE,
                      "feedback": {"C002": 1}}).encode()
    assert import_session(old, catalog) == (PROFILE, {"C002": 1})
    assert import_session_data(old, catalog)[2] == {}
    bad = json.dumps({"format": "career-recommendation-session", "version": 2, "profile": PROFILE,
                      "roadmaps": {"C001": {"git": "x"}, "C999": {}}}).encode()
    _, _, roadmaps, issues = import_session_data(bad, catalog)
    assert roadmaps == {} and len(issues) == 2
    with pytest.raises(SessionFileError):
        import_session(json.dumps({"format": "career-recommendation-session", "version": True,
                                   "profile": PROFILE}).encode(), catalog)
