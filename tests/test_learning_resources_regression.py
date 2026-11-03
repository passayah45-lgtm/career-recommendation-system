# Regression protection for the free learning resources: the catalogue, the Skill-Gap page, the roadmap and navigation
# Existing learning resource functionality must never disappear silently (owner rule, 3 November 2026)

import csv
import re
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from src.data.validation import DEFAULT_DATA_DIR  # noqa: E402
from src.services.catalog import load_catalog  # noqa: E402
from src.services.roadmap import build_roadmap  # noqa: E402
from src.services.skill_gap import analyze_skill_gap  # noqa: E402
from src.ui.state import PROFILE_KEY, ROADMAP_CAREER_KEY, SELECTED_CAREER_KEY  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app.py")
# Frozen copies of earlier catalogues; every resource they hold must still exist with the same skill and link
SNAPSHOT_RESOURCES = (ROOT / "data" / "evaluation" / "catalog_v1.2.0" / "resources.csv",
                      ROOT / "data" / "evaluation" / "catalog_v1.4.0" / "resources.csv")
PROFILE = {"skills": ["python", "sql"], "interests": ["analysing data and information"], "education_level": 3}
LINK = re.compile(r'href="(https?://[^"]+)"')


def read_resources(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {r["resource_id"]: r for r in csv.DictReader(f)}


def open_page(page, profile=None, **state):
    at = AppTest.from_file(APP, default_timeout=60)
    if profile is not None:
        at.session_state[PROFILE_KEY] = profile
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    at.switch_page(page)
    at.run()
    assert not at.exception, at.exception
    return at


def page_links(at):
    return [url for m in at.markdown for url in LINK.findall(m.value)]


# ---------- Catalogue ----------

@pytest.mark.parametrize("snapshot", SNAPSHOT_RESOURCES, ids=["v1.2.0", "v1.4.0"])
def test_no_learning_resource_was_removed_or_relinked(snapshot):
    live = read_resources(DEFAULT_DATA_DIR / "resources.csv")
    for rid, row in read_resources(snapshot).items():
        assert rid in live, f"{rid} was removed"
        assert (live[rid]["skill_name"], live[rid]["resource_url"]) == (row["skill_name"], row["resource_url"]), rid
        assert live[rid]["is_free"] == row["is_free"], rid


def test_every_resource_belongs_to_a_skill_some_career_uses():
    # The other direction (every career skill has a resource) is covered in tests/test_recommendations.py
    catalog = load_catalog()
    skills = {s for c in catalog.careers for s in c.required_skills + c.preferred_skills}
    orphans = sorted(r["resource_id"] for r in read_resources(DEFAULT_DATA_DIR / "resources.csv").values()
                     if r["skill_name"] not in skills)
    assert orphans == []


def test_free_resources_remain_the_majority():
    rows = read_resources(DEFAULT_DATA_DIR / "resources.csv").values()
    assert len(rows) >= 144
    assert sum(r["is_free"] == "true" for r in rows) / len(rows) > 0.5


# ---------- Skill-Gap Analysis page ----------

def test_skill_gap_page_shows_every_resource_the_service_returns():
    catalog = load_catalog()
    gap = analyze_skill_gap(PROFILE, "C001", catalog)
    expected = [r["url"] for group in ("required", "preferred") for e in gap["resources"][group] for r in e["resources"]]
    assert expected
    at = open_page("pages/3_Skill_Gap_Analysis.py", profile=PROFILE, **{SELECTED_CAREER_KEY: "C001"})
    assert sorted(page_links(at)) == sorted(expected)


def test_each_tab_shows_its_own_resources_with_free_badges_and_table():
    catalog = load_catalog()
    gap = analyze_skill_gap(PROFILE, "C001", catalog)
    at = open_page("pages/3_Skill_Gap_Analysis.py", profile=PROFILE, **{SELECTED_CAREER_KEY: "C001"})
    for tab, group in zip(at.tabs, ("required", "preferred")):
        resources = [(e["skill"], r) for e in gap["resources"][group] for r in e["resources"]]
        assert resources, group
        links = [url for m in tab.markdown for url in LINK.findall(m.value)]
        assert sorted(links) == sorted(r["url"] for _, r in resources), group
        free_badges = sum(":material/lock_open: Free" in m.value for m in tab.markdown)
        assert free_badges == sum(r["is_free"] for _, r in resources), group
        table = tab.dataframe[0].value
        assert sorted(zip(table["Skill"], table["URL"], table["Free"])) == \
            sorted((skill, r["url"], r["is_free"]) for skill, r in resources), group


def test_skill_gap_page_keeps_all_its_features():
    at = open_page("pages/3_Skill_Gap_Analysis.py", profile=PROFILE, **{SELECTED_CAREER_KEY: "C001"})
    assert [s.value for s in at.subheader] == ["Learning resources"]
    assert [t.label.split(" (")[0] for t in at.tabs] == ["Required skills", "Optional skills"]
    assert len(at.dataframe) == 2
    assert {"Required skill coverage", "Preferred skill coverage", "Overall skill coverage",
            "Missing required skills"} <= {m.label for m in at.metric}
    assert any(b.label == "Plan my learning for this career" for b in at.button)
    assert any(e.label == "Table view" for e in at.expander)
    text = "\n".join(str(x.value) for x in list(at.markdown) + list(at.info) + list(at.caption))
    assert "What you would learn to do in this career" in text


def test_skill_gap_without_an_assessment_still_lists_resources():
    at = open_page("pages/3_Skill_Gap_Analysis.py", **{SELECTED_CAREER_KEY: "C040"})
    assert page_links(at)


def test_plan_my_learning_opens_the_roadmap_for_that_career():
    at = open_page("pages/3_Skill_Gap_Analysis.py", profile=PROFILE, **{SELECTED_CAREER_KEY: "C001"})
    next(b for b in at.button if b.label == "Plan my learning for this career").click().run()
    assert not at.exception
    assert at.session_state[ROADMAP_CAREER_KEY] == "C001"


# ---------- Skill Roadmap ----------

def test_roadmap_gives_a_free_resource_link_for_each_step():
    catalog = load_catalog()
    roadmap = build_roadmap(PROFILE, "C001", catalog)
    assert roadmap["steps"] and all(step["resources"] for step in roadmap["steps"])
    at = open_page("pages/6_Skill_Roadmap.py", profile=PROFILE, **{ROADMAP_CAREER_KEY: "C001"})
    shown = set(page_links(at))
    assert {step["resources"][0]["url"] for step in roadmap["steps"]} <= shown
    labels = {b.label for b in at.button}
    assert "Open the full skill-gap analysis" in labels and "I have learned this skill" in labels


# ---------- Navigation ----------

def test_learning_pages_stay_in_the_navigation():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    for title in ("Skill-Gap Analysis", "Skill Roadmap", "Career Assessment", "Recommendations",
                  "Career Explorer", "Analytics"):
        assert f'title="{title}"' in source, title
