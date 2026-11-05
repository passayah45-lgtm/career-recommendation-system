# Link repairs of 6 November 2026: a broken learning resource is replaced by a verified free one for the same skill
# The register data/resource_link_replacements.csv records every replacement with its old link and its evidence

import csv
import re
import shutil
from pathlib import Path

import pytest

from src.data.preprocessing import clean_skill_text
from src.data.validation import DEFAULT_DATA_DIR, is_valid_url
from src.services.catalog import load_catalog
from src.services.recommendations import recommend
from src.services.skill_gap import analyze_skill_gap

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data" / "resource_link_replacements.csv"
LIVE = DEFAULT_DATA_DIR / "resources.csv"
FROZEN = (ROOT / "data" / "evaluation" / "catalog_v1.2.0" / "resources.csv",
          ROOT / "data" / "evaluation" / "catalog_v1.3.0" / "resources.csv",
          ROOT / "data" / "evaluation" / "catalog_v1.4.0" / "resources.csv")
# "unsuitable": the old link worked but did not lead to the learning material itself (R120 pointed to source files)
REASONS = {"broken", "removed", "unrelated", "unavailable", "paid", "off_skill", "unsuitable"}
# Words that carry no skill meaning when a replacement title is compared with its skill
FILLER = {"and", "of", "the", "for", "to", "in", "a"}
HR_PROFILE = {"skills": ["communication"], "interests": [], "education_level": 3}
PROFILES = (
    {"skills": ["python", "sql"], "interests": ["analysing data and information"], "education_level": 3},
    {"skills": ["communication", "recruitment"], "interests": ["helping and supporting people"],
     "education_level": 2},
    {"skills": ["human resource management"], "interests": [], "education_level": None},
)


def read(path, key="resource_id"):
    with open(path, newline="", encoding="utf-8") as f:
        return {r[key]: r for r in csv.DictReader(f)}


def register():
    return read(REGISTER)


def stems(text):
    # Lower-case words without a final "s", so "resources" and "resource" compare equal
    return {w.rstrip("s") for w in re.findall(r"[a-z]+", clean_skill_text(text))} - FILLER


# ---------- The register ----------

def test_register_lists_the_repaired_resources():
    assert list(register()) == ["R048", "R120"]


@pytest.mark.parametrize("rid", list(register()))
def test_each_replacement_is_recorded_in_full(rid):
    fix = register()[rid]
    assert fix["reason"] in REASONS
    assert re.fullmatch(r"20\d\d-\d\d-\d\d", fix["replaced_on"])
    assert fix["evidence"].strip() and fix["new_title"].strip() and fix["new_provider"].strip()
    assert fix["old_url"] != fix["new_url"]


@pytest.mark.parametrize("rid", list(register()))
def test_replacement_url_is_a_valid_direct_https_link(rid):
    url = register()[rid]["new_url"]
    assert is_valid_url(url) and url.startswith("https://")
    assert url == url.strip() and " " not in url
    assert LIVE.read_text(encoding="utf-8").count(url) == 1, "the URL must be used by one resource only"


@pytest.mark.parametrize("rid", list(register()))
def test_live_row_carries_the_replacement_and_keeps_its_relationships(rid):
    fix, live = register()[rid], read(LIVE)[rid]
    assert (live["resource_title"], live["provider"], live["resource_url"]) == \
        (fix["new_title"], fix["new_provider"], fix["new_url"])
    assert live["verified_on"] == fix["replaced_on"]
    assert fix["old_url"] in live["notes"], "the earlier link stays on record in the notes"
    # R001 to R114 are in every frozen catalogue, R115 to R144 only from v1.3.0 onwards
    holding = [frozen for frozen in FROZEN if rid in read(frozen)]
    assert holding, f"{rid} is in no frozen catalogue"
    for frozen in holding:
        old = read(frozen)[rid]
        assert old["resource_url"] == fix["old_url"], f"{frozen} must keep the original link"
        for field in ("skill_name", "is_free", "resource_type", "level", "language"):
            assert live[field] == old[field], (rid, field)


@pytest.mark.parametrize("rid", list(register()))
def test_replacement_teaches_the_same_skill(rid):
    live = read(LIVE)[rid]
    # The title shares a word root with the skill ("geophysics" and "geophysical", "resources" and "resource")
    roots = {w[:7] for w in stems(live["skill_name"])}
    assert roots & {w[:7] for w in stems(live["resource_title"])}, live["resource_title"]
    # The recorded evidence must name the skill the new page teaches
    assert stems(live["skill_name"]) <= stems(register()[rid]["evidence"])


@pytest.mark.parametrize("rid", list(register()))
def test_a_free_label_is_backed_by_recorded_evidence(rid):
    fix, live = register()[rid], read(LIVE)[rid]
    assert live["is_free"] == "true"
    assert re.search(r"CC BY|Creative Commons|free|open educational", fix["evidence"], re.IGNORECASE)


def test_removed_or_paid_links_are_no_longer_offered_as_free():
    live_urls = {r["resource_url"] for r in read(LIVE).values()}
    for fix in register().values():
        assert fix["old_url"] not in live_urls, fix["resource_id"]


# ---------- Whole catalogue ----------

def test_resource_ids_are_unique_and_skill_mappings_are_preserved():
    with open(LIVE, newline="", encoding="utf-8") as f:
        ids = [r["resource_id"] for r in csv.DictReader(f)]
    assert len(ids) == len(set(ids)) == 144
    live = read(LIVE)
    frozen = read(FROZEN[-1])
    assert set(frozen) == set(live)
    assert {rid: r["skill_name"] for rid, r in live.items()} == {rid: r["skill_name"] for rid, r in frozen.items()}


def test_every_career_skill_still_has_its_resource():
    catalog = load_catalog()
    for career in catalog.careers:
        for skill in career.required_skills + career.preferred_skills:
            assert catalog.resources.for_skill(skill, catalog.aliases), (career.career_id, skill)


def test_skill_gap_offers_the_replacement_for_human_resource_management():
    catalog = load_catalog()
    gap = analyze_skill_gap(HR_PROFILE, "C033", catalog)
    offered = [r for e in gap["resources"]["required"] if e["skill"] == "human resource management"
               for r in e["resources"]]
    fix = register()["R048"]
    assert [(r["title"], r["provider"], r["url"], r["is_free"]) for r in offered] == \
        [(fix["new_title"], fix["new_provider"], fix["new_url"], True)]


def test_skill_gap_card_links_the_replacement_title_and_labels_it_free():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    from src.ui.components import FREE_RESOURCE_LABEL
    from src.ui.state import PROFILE_KEY, SELECTED_CAREER_KEY
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.session_state[PROFILE_KEY] = HR_PROFILE
    at.session_state[SELECTED_CAREER_KEY] = "C033"
    at.run()
    at.switch_page("pages/3_Skill_Gap_Analysis.py")
    at.run()
    assert not at.exception, at.exception
    fix = register()["R048"]
    page = " ".join(m.value for m in at.markdown)
    assert f'href="{fix["new_url"]}"' in page and f'>{fix["new_title"]}</a>' in page
    assert fix["old_url"] not in page
    assert f":material/lock_open: {FREE_RESOURCE_LABEL}" in page


# ---------- Recommendations ----------

def restored_copy(tmp_path):
    # The live catalogue with every repaired row put back to its frozen v1.4.0 version
    copy = tmp_path / "raw"
    shutil.copytree(DEFAULT_DATA_DIR, copy, ignore=shutil.ignore_patterns("processed"))
    frozen = read(FROZEN[-1])
    with open(LIVE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns, rows = reader.fieldnames, list(reader)
    rows = [frozen[r["resource_id"]] if r["resource_id"] in register() else r for r in rows]
    with open(copy / "resources.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return copy


@pytest.mark.parametrize("profile", PROFILES, ids=["data", "people", "hr"])
def test_recommendations_are_identical_with_and_without_the_repairs(tmp_path, profile):
    repaired = recommend(profile, load_catalog())
    original = recommend(profile, load_catalog(restored_copy(tmp_path)))
    assert repaired == original
