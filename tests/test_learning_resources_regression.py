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
# Owner-requested link repairs (6 November 2026): each row names one resource and its exact old and new link
REPLACEMENTS = ROOT / "data" / "resource_link_replacements.csv"
PROFILE = {"skills": ["python", "sql"], "interests": ["analysing data and information"], "education_level": 3}
LINK = re.compile(r'href="(https?://[^"]+)"')
# The "Free learning resource" badge as written in Markdown, with its link to the resource (Streamlit opens it in a new tab)
FREE_LABEL_LINK = re.compile(r":blue-badge\[:material/lock_open: \[Free learning resource\]\(<(https?://[^>]+)>\)\]")


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
    # A link may differ from the frozen copy only when data/resource_link_replacements.csv records that exact change
    live = read_resources(DEFAULT_DATA_DIR / "resources.csv")
    replaced = read_resources(REPLACEMENTS)
    for rid, row in read_resources(snapshot).items():
        assert rid in live, f"{rid} was removed"
        assert live[rid]["skill_name"] == row["skill_name"], rid
        if rid in replaced:
            assert (row["resource_url"], live[rid]["resource_url"]) == \
                (replaced[rid]["old_url"], replaced[rid]["new_url"]), rid
        else:
            assert live[rid]["resource_url"] == row["resource_url"], rid
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
        # Since 6 November 2026 the free label itself links to the resource
        label_links = [url for m in tab.markdown for url in FREE_LABEL_LINK.findall(m.value)]
        assert sorted(label_links) == sorted(r["url"] for _, r in resources if r["is_free"]), group
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


def test_link_check_notice_is_gone_but_verification_stays():
    # The block notice explaining link checks was removed from the page at the owner's request on 3 November 2026
    catalog = load_catalog()
    gap = analyze_skill_gap(PROFILE, "C001", catalog)
    at = open_page("pages/3_Skill_Gap_Analysis.py", profile=PROFILE, **{SELECTED_CAREER_KEY: "C001"})
    page = "\n".join(str(e.value) for e in list(at.info) + list(at.markdown) + list(at.caption))
    assert "Each resource shows how its link was checked" not in page
    assert gap["resource_note"] not in page
    # Verification data remains: the service note, every resource's status and date, and the table column
    assert "was not opened by the checker" in gap["resource_note"]
    # Since 6 November 2026 (owner decision) the cards show "Free learning resource" instead of the link check
    # badge and its date, so students never see internal verification dates
    cards = [m.value for m in at.markdown if ":violet-badge[" in m.value]
    assert cards and all("Link checked" not in v and "Found in search" not in v for v in cards)
    assert not any(re.search(r"20\d\d-\d\d-\d\d", v) for v in cards)
    resources = [r for group in ("required", "preferred") for e in gap["resources"][group] for r in e["resources"]]
    assert all(r["url_verification"] and r["url_verification_meaning"] for r in resources)
    assert all(r.get("verified_on") for r in resources if r["url_verification"] == "http_checked")
    assert set(at.dataframe[0].value["Link status"]) <= {"http checked", "search index confirmed", "unverified"}


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


# ---------- Student-facing resource cards (6 November 2026, owner decision) ----------
# Cards show the title as a direct link, the provider, type, level and "Free learning resource"; verification
# badges and dates are no longer shown to students

DATE = re.compile(r"20\d\d-\d\d-\d\d")
VERIFICATION_WORDS = ("Link checked", "Found in search", "Not verified")


def resource_cards(at):
    return [m.value for m in at.markdown if ":violet-badge[" in m.value]


@pytest.mark.parametrize("page,state", [
    ("pages/3_Skill_Gap_Analysis.py", {SELECTED_CAREER_KEY: "C001"}),
    ("pages/6_Skill_Roadmap.py", {ROADMAP_CAREER_KEY: "C001"}),
], ids=["skill_gap", "roadmap"])
def test_cards_show_one_free_label_per_resource_and_no_verification_dates(page, state):
    at = open_page(page, profile=PROFILE, **state)
    cards = resource_cards(at)
    links = page_links(at)
    assert cards and len(cards) == len(links)
    for card in cards:
        assert card.count("Free learning resource") == 1
        assert not any(word in card for word in VERIFICATION_WORDS) and not DATE.search(card)
    # No verification wording or date anywhere in the visible text of the cards' markdown
    titles = [m.value for m in at.markdown if 'class="crs-res-title"' in m.value]
    assert len(titles) == len(links) and all(not DATE.search(t) for t in titles)


def test_every_card_title_links_directly_to_its_catalogue_url():
    catalog = load_catalog()
    gap = analyze_skill_gap(PROFILE, "C001", catalog)
    at = open_page("pages/3_Skill_Gap_Analysis.py", profile=PROFILE, **{SELECTED_CAREER_KEY: "C001"})
    expected = {r["url"]: r["title"]
                for g in ("required", "preferred") for e in gap["resources"][g] for r in e["resources"]}
    shown = {}
    for m in at.markdown:
        found = re.search(r'<a href="([^"]+)" target="_blank" rel="noopener">([^<]+)</a>', m.value)
        if found:
            shown[found.group(1)] = found.group(2)
    assert shown == {url: title.replace("&", "&amp;") for url, title in expected.items()}


@pytest.mark.parametrize("page,state", [
    ("pages/3_Skill_Gap_Analysis.py", {SELECTED_CAREER_KEY: "C001"}),
    ("pages/6_Skill_Roadmap.py", {ROADMAP_CAREER_KEY: "C001"}),
], ids=["skill_gap", "roadmap"])
def test_free_label_links_to_the_same_catalogue_url_as_its_title(page, state):
    # Owner request, 6 November 2026: students can open the resource from the label as well as from the title
    at = open_page(page, profile=PROFILE, **state)
    titles = [LINK.findall(m.value)[0] for m in at.markdown if 'class="crs-res-title"' in m.value]
    labels = [FREE_LABEL_LINK.findall(m.value) for m in at.markdown if ":violet-badge[" in m.value]
    assert titles and len(titles) == len(labels)
    # Each card's label link is the same catalogue URL as the title link drawn just above it
    assert labels == [[url] for url in titles]
    catalogue = {r["resource_url"] for r in read_resources(DEFAULT_DATA_DIR / "resources.csv").values()}
    assert set(titles) <= catalogue


def test_title_link_still_opens_in_a_new_tab_next_to_the_linked_label():
    def card():
        from src.ui.components import resource_row
        resource_row({"provider": "Example", "url": "https://example.org/a_(b)", "title": "Example course",
                      "is_free": True, "resource_type": "course", "level": "beginner"})
    at = AppTest.from_function(card)
    at.run()
    text = "\n".join(m.value for m in at.markdown)
    assert '<a href="https://example.org/a_(b)" target="_blank" rel="noopener">Example course</a>' in text
    assert FREE_LABEL_LINK.findall(text) == ["https://example.org/a_(b)"]
    assert not DATE.search(text)


def test_a_resource_that_is_not_free_is_still_labelled_honestly():
    def card():
        from src.ui.components import resource_row
        resource_row({"provider": "Example", "url": "https://example.org/course", "title": "Example course",
                      "is_free": False, "resource_type": "course", "level": "beginner"})
    at = AppTest.from_function(card)
    at.run()
    text = "\n".join(m.value for m in at.markdown)
    assert "Paid or partly paid" in text and "Free learning resource" not in text
    # The paid label stays plain text; the title still links to the resource
    assert '<a href="https://example.org/course" target="_blank" rel="noopener">Example course</a>' in text
