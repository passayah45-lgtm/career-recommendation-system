# The lecturer's 17 careers: 3 existing records kept, 14 new records (C051 to C064) in dataset v1.3.0

import hashlib
from collections import Counter
from pathlib import Path

import pytest

from src.data.preprocessing import normalize_skill
from src.data.validation import CATEGORIES, DEFAULT_DATA_DIR, read_csv
from src.services.catalog import load_catalog
from src.services.recommendations import recommend
from src.services.skill_gap import analyze_skill_gap
from src.ui.theme import CATEGORY_FALLBACK_COLOR, category_color
from src.ui.views import category_counts, filter_careers

ROOT = Path(__file__).resolve().parents[1]

OFFICIAL_TITLES = [
    "Mining Engineer", "Geological Engineer", "Telecommunications Engineer", "Civil Engineer", "Building Engineer",
    "Electrical Engineer", "Geotechnical Engineer", "Geophysicist", "Private Law Specialist", "Public Law Specialist",
    "Human Resources Specialist", "Management Information Systems Specialist (MIAGE)", "Economist",
    "Business Administration Specialist", "Laboratory Technician", "Sociologist", "Community Relations Specialist",
]
EXISTING = {"Civil Engineer": "C046", "Electrical Engineer": "C048", "Human Resources Specialist": "C033"}
NEW = {
    "C051": ("Mining Engineer", "Engineering"),
    "C052": ("Geological Engineer", "Engineering"),
    "C053": ("Telecommunications Engineer", "Engineering"),
    "C054": ("Building Engineer", "Engineering"),
    "C055": ("Geotechnical Engineer", "Engineering"),
    "C056": ("Geophysicist", "Engineering"),
    "C057": ("Private Law Specialist", "Law"),
    "C058": ("Public Law Specialist", "Law"),
    "C059": ("Management Information Systems Specialist (MIAGE)", "Business"),
    "C060": ("Economist", "Social Sciences"),
    "C061": ("Business Administration Specialist", "Business"),
    "C062": ("Laboratory Technician", "Healthcare"),
    "C063": ("Sociologist", "Social Sciences"),
    "C064": ("Community Relations Specialist", "Business"),
}
# Saved before the expansion; the expanded catalogue must never change them
REPORT_SHA256 = {
    "evaluation_results.json": "0982d9d4c91a9de8889df2ffa7eee101a5c09cc2f3e1cb491909ea15918bfb28",
    "research_results.json": "8b169c33e3d97899470132bb269b4e969b39b7776dab0d49a8e42fac19ced805",
    "ml_results.json": "14705ab23a5fc5802a42abc1a7991f7f59e31d1b79d13d496bb61ebd3a622377",
    "ml_interpretation.json": "434ce2333115704ba441b64783bd653d76ead8d83f72a4fcab7462c97f31e917",
    "ml_sensitivity.json": "f0d66500518dcd3c843f40badbc41e29e7d1d3fedcec8d8fede91d815be17d02",
}


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


def full_profile(career):
    return {"skills": list(career.required_skills + career.preferred_skills), "interests": list(career.interests),
            "education_level": career.education_level}


def test_catalogue_has_64_unique_careers(catalog):
    ids = [c.career_id for c in catalog.careers]
    titles = [c.title for c in catalog.careers]
    assert len(ids) == 64 and len(set(ids)) == 64 and len(set(titles)) == 64
    assert ids == [f"C{i:03d}" for i in range(1, 65)]


def test_all_17_official_titles_present_exactly_once(catalog):
    counts = Counter(c.title for c in catalog.careers)
    for title in OFFICIAL_TITLES:
        assert counts[title] == 1, title


def test_existing_three_keep_their_records(catalog):
    by_title = {c.title: c.career_id for c in catalog.careers}
    for title, cid in EXISTING.items():
        assert by_title[title] == cid


def test_new_records_ids_titles_and_categories(catalog):
    by_id = {c.career_id: c for c in catalog.careers}
    for cid, (title, category) in NEW.items():
        assert by_id[cid].title == title and by_id[cid].category == category


def test_mining_geological_and_geotechnical_are_separate(catalog):
    by_title = {c.title: c for c in catalog.careers}
    trio = [by_title["Mining Engineer"], by_title["Geological Engineer"], by_title["Geotechnical Engineer"]]
    assert len({c.career_id for c in trio}) == 3
    assert len({c.required_skills for c in trio}) == 3


def test_every_new_skill_has_a_resource_and_ids_are_unique(catalog):
    rows, _ = read_csv(DEFAULT_DATA_DIR / "resources.csv")
    ids = [r["resource_id"] for r in rows]
    assert len(ids) == len(set(ids)) == 144
    assert ids[-30:] == [f"R{i:03d}" for i in range(115, 145)]
    urls = [r["resource_url"] for r in rows]
    assert len(urls) == len(set(urls))
    skills = {s for c in catalog.careers for s in c.required_skills + c.preferred_skills}
    assert len(skills) == 144
    for skill in skills:
        assert catalog.resources.for_skill(skill, catalog.aliases), skill
    for r in rows[-30:]:
        assert r["url_verification"] in ("search_index_confirmed", "http_checked")
        assert r["is_free"] == "true" and r["resource_url"].startswith("https://")


def test_aliases_point_to_real_skills(catalog):
    for alias, target in catalog.aliases.items():
        assert target in catalog.known_skills
        assert normalize_skill(alias, catalog.aliases) == target


# Built from the career's own curated skills, so a score of 100 is expected by construction; the rank check is the real test
@pytest.mark.parametrize("cid", list(NEW) + list(EXISTING.values()))
def test_each_career_is_recommended_for_a_matching_profile(catalog, cid):
    career = catalog.get_career(cid)
    recs = recommend(full_profile(career), catalog, top_k=None)["recommendations"]
    rec = next(r for r in recs if r["career_id"] == cid)
    assert rec["score"] == 100.0
    assert rec["rank"] <= 3
    assert all(r["score"] == 100.0 for r in recs[:rec["rank"]])
    assert set(rec["matched_required_skills"]) == set(career.required_skills)
    assert set(rec["matched_preferred_skills"]) == set(career.preferred_skills)
    assert rec["missing_required_skills"] == []


# Partial profiles typed as a learner might: 3 of 4 required skills, mixed case, French aliases, 2 interests, no preferred skills
PARTIAL_PROFILES = {
    "C051": (["Mine planning", "mécanique des roches", "mine safety"], ["engineering", "environment"], 3),
    "C052": (["Géologie", "geomechanics", "méthodes géophysiques"], ["science", "engineering"], 3),
    "C053": (["telecommunications", "RF engineering", "networking"], ["technology", "engineering"], 3),
    "C054": (["construction management", "reinforced concrete design", "structural analysis"], ["engineering", "design"], 3),
    "C055": (["mécanique des sols", "foundation design", "rock mechanics"], ["engineering", "science"], 3),
    "C056": (["geophysical methods", "physics", "python"], ["science", "research"], 3),
    "C057": (["legal research", "droit des contrats", "droit ohada"], ["analysis", "writing"], 4),
    "C058": (["legal research", "droit constitutionnel", "droit administratif"], ["analysis", "writing"], 4),
    "C059": (["management information systems", "business analysis", "sql"], ["technology", "business"], 4),
    "C060": (["économie", "statistics", "R programming"], ["analysis", "research"], 4),
    "C061": (["business management", "accounting", "human resource management"], ["business", "leadership"], 3),
    "C062": (["laboratory techniques", "laboratory safety", "quality control"], ["science", "analysis"], 2),
    "C063": (["sociologie", "qualitative research", "survey design"], ["research", "helping people"], 4),
    "C064": (["stakeholder management", "community development", "gestion des conflits"], ["helping people", "communication"], 3),
}


@pytest.mark.parametrize("cid", list(PARTIAL_PROFILES))
def test_partial_learner_profile_ranks_target_first(catalog, cid):
    skills, interests, level = PARTIAL_PROFILES[cid]
    recs = recommend({"skills": skills, "interests": interests, "education_level": level}, catalog, top_k=None)
    recs = recs["recommendations"]
    assert recs[0]["career_id"] == cid
    assert len(recs[0]["missing_required_skills"]) == 1
    assert recs[0]["score"] < 100.0
    # A clear margin, not a tie broken by career id
    assert recs[0]["score"] - recs[1]["score"] >= 5.0


def test_earth_science_trio_is_distinguished(catalog):
    for cid in ("C051", "C052", "C055"):
        skills, interests, level = PARTIAL_PROFILES[cid]
        recs = recommend({"skills": skills, "interests": interests, "education_level": level}, catalog, top_k=None)
        trio = [r["career_id"] for r in recs["recommendations"] if r["career_id"] in ("C051", "C052", "C055")]
        assert trio[0] == cid


@pytest.mark.parametrize("profile", [
    {"skills": ["python", "javascript", "git", "sql"], "interests": ["technology"], "education_level": 3},
    {"skills": ["patient care", "infection control", "anatomy"], "interests": ["healthcare", "helping people"],
     "education_level": 3},
])
def test_new_careers_do_not_crowd_unrelated_profiles(catalog, profile):
    top = recommend(profile, catalog, top_k=5)["recommendations"]
    assert not {r["career_id"] for r in top} & set(NEW)


@pytest.mark.parametrize("cid", list(NEW))
def test_skill_gap_and_resources_for_new_careers(catalog, cid):
    career = catalog.get_career(cid)
    profile = {"skills": [career.required_skills[0]], "interests": [career.interests[0]], "education_level": 1}
    gap = analyze_skill_gap(profile, cid, catalog)
    assert gap["have_required_skills"] == [career.required_skills[0]]
    assert set(gap["missing_required_skills"]) == set(career.required_skills[1:])
    resources = gap["resources"]["required"] + gap["resources"]["preferred"]
    assert {e["skill"] for e in resources} == set(career.required_skills[1:] + career.preferred_skills)
    assert all(e["resources"] and e["resources"][0]["url"].startswith("https://") for e in resources)
    rec = next(r for r in recommend(profile, catalog, top_k=None)["recommendations"] if r["career_id"] == cid)
    assert rec["score_components"]["education"]["value"] < 1.0


def test_education_basis_file_matches_careers(catalog):
    rows, _ = read_csv(ROOT / "research" / "data" / "expansion_education_basis.csv")
    by_id = {c.career_id: c for c in catalog.careers}
    assert [r["career_id"] for r in rows] == list(NEW)
    for r in rows:
        assert r["career_title"] == by_id[r["career_id"]].title
        assert int(r["education_level"]) == by_id[r["career_id"]].education_level
        assert r["basis"] in ("estimate", "estimate_supported_by_us_reference")
        # A supported estimate must quote its evidence; a plain estimate must not claim any
        has_ref = bool(r["reference"] and r["reference_url"].startswith("https://") and r["reference_evidence"])
        assert has_ref == (r["basis"] == "estimate_supported_by_us_reference")
    supported = {r["career_id"] for r in rows if r["basis"] == "estimate_supported_by_us_reference"}
    assert supported == {"C051", "C052", "C056", "C060", "C063"}


def test_category_filters_and_colors_cover_all_ten(catalog):
    assert len(CATEGORIES) == 10
    for cat in CATEGORIES:
        assert filter_careers(catalog.careers, [cat]), cat
        assert category_color(cat) != CATEGORY_FALLBACK_COLOR
    rows = category_counts(catalog.careers)
    assert [r["Category"] for r in rows] == list(CATEGORIES)
    assert sum(r["Careers"] for r in rows) == 64


def test_saved_reports_are_unchanged():
    for name, digest in REPORT_SHA256.items():
        assert hashlib.sha256((ROOT / "reports" / name).read_bytes()).hexdigest() == digest, name
