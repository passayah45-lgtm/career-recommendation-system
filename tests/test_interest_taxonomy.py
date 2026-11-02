# Interest taxonomy 2.0 (dataset v1.4.0): vocabulary, assignments, validation, migration, form and protections
# Expected values are read from docs/interest_taxonomy_second_review.md, so the data cannot drift from the report

import csv
import json
from collections import Counter
from pathlib import Path

import pytest

from src.data import interest_taxonomy as tx
from src.data.preprocessing import clean_skill_text
from src.data.validation import (
    CAREER_COLUMNS, DEFAULT_DATA_DIR, ERROR, INTERESTS, validate_all, validate_careers,
)
from src.engine.scoring import DEFAULT_WEIGHTS
from src.services.catalog import load_catalog
from src.services.recommendations import profile_from_input, recommend
from src.services.session_data import export_session, import_session_data
from tests.conftest import career_row

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "interest_taxonomy_second_review.md"
PROVISIONAL = ("C002", "C003", "C012", "C053", "C054", "C055", "C057", "C058", "C059", "C061", "C062", "C064")
SNAPSHOTS = (ROOT / "data" / "evaluation" / "catalog_v1.2.0", ROOT / "data" / "evaluation" / "catalog_v1.3.0")


def review_table(header_start):
    lines = REVIEW.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(header_start))
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


@pytest.fixture(scope="module")
def section_c():
    return {r[0]: r for r in review_table("| Career ID | Official title")}


# ---------- Vocabulary ----------

def test_vocabulary_is_the_23_terms_of_the_second_review():
    descriptions = review_table("| Interest | Short explanation")
    assert len(descriptions) == 23 == len(tx.INTEREST_TERMS) == len(INTERESTS)
    by_label = {t.label: t for t in tx.INTEREST_TERMS}
    for label, explanation, example, related in descriptions:
        term = by_label[label]
        assert (term.explanation, term.example, term.related_skill) == (explanation, example, related), label


def test_decision_counts_match_the_second_review():
    decisions = Counter(r[1] for r in review_table("| Proposed interest | Decision"))
    assert decisions["Retain"] == 12
    assert decisions["Rename"] + decisions["Rename (order only)"] == 6
    assert decisions["Split"] + decisions["Replace"] == 3 and decisions["Add"] == 1


def test_riasec_groups_follow_section_d():
    groups = {g: [t.label for t in terms] for g, terms in tx.terms_by_group().items()}
    assert list(groups) == list(tx.RIASEC_ORDER)
    assert {g: len(v) for g, v in groups.items()} == {
        "Realistic": 4, "Investigative": 5, "Artistic": 3, "Social": 4, "Enterprising": 3, "Conventional": 4}
    assert "Writing software and building apps" in groups["Investigative"]
    assert "Managing money and financial information" in groups["Conventional"]


def test_stored_keys_are_normalized_and_unique():
    keys = [t.key for t in tx.INTEREST_TERMS]
    assert len(set(keys)) == 23 and tuple(sorted(keys)) == tx.CURRENT_INTERESTS
    assert all(k == clean_skill_text(k) for k in keys)
    assert not set(keys) & set(tx.LEGACY_INTERESTS)
    assert tx.label_for("caring for peoples health") == "Caring for people's health"
    assert tx.label_for("technology") == "technology"


def test_french_names_are_complete_drafts_and_unambiguous():
    names = [t.label_fr_draft for t in tx.INTEREST_TERMS]
    assert all(names) and len(set(names)) == 23
    folded = {clean_skill_text(n) for n in names}
    assert len(folded) == 23 and not folded & set(tx.CURRENT_INTERESTS) and not folded & set(tx.LEGACY_INTERESTS)
    source = (ROOT / "src" / "data" / "interest_taxonomy.py").read_text(encoding="utf-8")
    assert "DRAFT translations" in source and "not yet reviewed" in source


# ---------- Catalogue v1.4.0 ----------

def test_live_catalogue_declares_taxonomy_2(catalog):
    manifest = json.loads((DEFAULT_DATA_DIR / "dataset_manifest.json").read_text(encoding="utf-8"))
    assert manifest["dataset_version"] == "1.4.0" and manifest["interest_taxonomy"] == tx.CURRENT_TAXONOMY
    assert catalog.interest_taxonomy == tx.CURRENT_TAXONOMY and catalog.interests == frozenset(INTERESTS)
    assert validate_all().ok


def test_every_career_has_exactly_three_known_interests(catalog):
    assert len(catalog.careers) == 64
    for career in catalog.careers:
        assert len(career.interests) == 3 == len(set(career.interests)), career.career_id
        assert set(career.interests) <= set(INTERESTS), career.career_id


def test_assignments_match_section_c_exactly(catalog, section_c):
    assert set(section_c) == {c.career_id for c in catalog.careers}
    for career in catalog.careers:
        row = section_c[career.career_id]
        assert career.title == row[1]
        assert career.interests == tuple(clean_skill_text(x) for x in row[4].split(";")), career.career_id


def test_provisional_careers_are_kept_and_flagged_in_the_report(catalog, section_c):
    assert sorted(cid for cid, r in section_c.items() if r[5] == "Provisional") == sorted(PROVISIONAL)
    ids = {c.career_id for c in catalog.careers}
    assert set(PROVISIONAL) <= ids


def test_differentiation_matches_the_report(catalog):
    sets = Counter(frozenset(c.interests) for c in catalog.careers)
    assert len(sets) == 58
    groups = sorted(sorted(c.career_id for c in catalog.careers if frozenset(c.interests) == s)
                    for s, n in sets.items() if n > 1)
    assert groups == [["C004", "C028"], ["C005", "C013"], ["C006", "C060"], ["C008", "C020"],
                      ["C014", "C022"], ["C047", "C048"]]


def test_only_the_interests_column_changed_from_v130(catalog):
    with open(SNAPSHOTS[1] / "careers.csv", newline="", encoding="utf-8") as f:
        frozen = {r["career_id"]: r for r in csv.DictReader(f)}
    with open(DEFAULT_DATA_DIR / "careers.csv", newline="", encoding="utf-8") as f:
        live = {r["career_id"]: r for r in csv.DictReader(f)}
    assert set(frozen) == set(live)
    for cid, row in frozen.items():
        assert {k: v for k, v in row.items() if k != "interests"} == \
            {k: v for k, v in live[cid].items() if k != "interests"}, cid


# ---------- Validation ----------

def current_rows(interests):
    return [career_row(1, interests=interests)]


def errors(rows, taxonomy):
    return [str(i) for i in validate_careers(rows, CAREER_COLUMNS, len(rows), taxonomy) if i.severity == ERROR]


def test_current_taxonomy_needs_exactly_three_terms():
    three = "analysing data and information|researching and investigating|writing and editing"
    assert errors(current_rows(three), tx.CURRENT_TAXONOMY) == []
    assert any("exactly 3" in e for e in errors(current_rows("analysing data and information|writing and editing"),
                                                  tx.CURRENT_TAXONOMY))
    assert any("exactly 3" in e for e in errors(current_rows(three + "|working with communities"), tx.CURRENT_TAXONOMY))


def test_current_taxonomy_rejects_old_terms_and_legacy_rejects_new_terms():
    assert any("not in the controlled" in e for e in errors(
        current_rows("analysis|researching and investigating|writing and editing"), tx.CURRENT_TAXONOMY))
    assert any("not in the controlled" in e for e in errors(current_rows("analysing data and information"),
                                                             tx.LEGACY_TAXONOMY))
    assert errors(current_rows("technology|problem solving"), tx.LEGACY_TAXONOMY) == []


def test_manifest_taxonomy_value_is_checked(tmp_path, dataset_dir):
    (dataset_dir / "dataset_manifest.json").write_text(json.dumps(
        {"dataset_version": "9.9.9", "careers": 2, "skills": 3, "resources": 3, "interest_taxonomy": "3.0"}))
    assert any(e.field == "interest_taxonomy" for e in validate_all(dataset_dir).errors)


def test_frozen_snapshots_still_load_with_the_legacy_vocabulary():
    for folder in SNAPSHOTS:
        assert validate_all(folder).ok, folder
        frozen = load_catalog(folder)
        assert frozen.interest_taxonomy == tx.LEGACY_TAXONOMY and frozen.interests == frozenset(tx.LEGACY_INTERESTS)
        # No migration inside frozen evaluations: old names match exactly, new names are unknown
        profile, report = profile_from_input({"interests": ["analysis", "Analysing data and information"]}, frozen)
        assert profile.interests == ("analysis",) and report.unknown_interests == ("Analysing data and information",)
        assert report.migrated_interests == () and report.retired_interests == ()


# ---------- Migration ----------

@pytest.mark.parametrize("old,new", sorted(tx.LEGACY_TO_CURRENT.items()))
def test_each_mapped_old_name_migrates(catalog, old, new):
    profile, report = profile_from_input({"interests": [old]}, catalog)
    assert profile.interests == (new,) and report.migrated_interests == ((old, new),)


@pytest.mark.parametrize("old", sorted(tx.RETIRED_LEGACY))
def test_retired_old_names_are_reported_not_guessed(catalog, old):
    profile, report = profile_from_input({"interests": [old]}, catalog)
    assert profile.interests == () and report.retired_interests[0][0] == old
    warnings = recommend({"interests": [old]}, catalog)["warnings"]
    assert any("no longer used" in w and old in w for w in warnings)


def test_every_old_name_is_either_mapped_or_retired():
    assert set(tx.LEGACY_TO_CURRENT) | set(tx.RETIRED_LEGACY) == set(tx.LEGACY_INTERESTS)
    assert not set(tx.LEGACY_TO_CURRENT) & set(tx.RETIRED_LEGACY)
    assert set(tx.LEGACY_TO_CURRENT.values()) <= set(tx.CURRENT_INTERESTS)


def test_labels_keys_and_french_drafts_are_all_accepted(catalog):
    term = tx.TERMS_BY_KEY["managing money and financial information"]
    for raw in (term.label, term.key, term.label.upper(), term.label_fr_draft):
        profile, report = profile_from_input({"interests": [raw]}, catalog)
        assert profile.interests == (term.key,) and report.unknown_interests == (), raw


def test_duplicates_after_migration_count_once(catalog):
    profile, report = profile_from_input(
        {"interests": ["mathematics", "Working with numbers and calculations", "gaming"]}, catalog)
    assert profile.interests == ("working with numbers and calculations",)
    assert report.unknown_interests == ("gaming",)


def test_migrated_input_scores_like_the_current_names(catalog):
    old = recommend({"skills": ["python"], "interests": ["analysis", "mathematics"]}, catalog, top_k=None)
    new = recommend({"skills": ["python"], "interests": ["Analysing data and information",
                                                          "Working with numbers and calculations"]},
                    catalog, top_k=None)
    assert [(r["career_id"], r["score"]) for r in old["recommendations"]] == \
        [(r["career_id"], r["score"]) for r in new["recommendations"]]
    assert any("Old interest names were updated" in w for w in old["warnings"])


def test_saved_session_files_with_old_interest_names_still_load(catalog):
    for version in (1, 2):
        raw = json.dumps({"format": "career-recommendation-session", "version": version,
                          "profile": {"skills": ["python"], "interests": ["analysis", "technology"],
                                      "education_level": 3},
                          "feedback": {"C001": 1}}).encode("utf-8")
        profile, feedback, _, _ = import_session_data(raw, catalog)
        assert feedback == {"C001": 1}
        migrated, report = profile_from_input(profile, catalog)
        assert migrated.interests == ("analysing data and information",)
        assert report.retired_interests[0][0] == "technology"


def test_export_round_trip_keeps_current_interests(catalog):
    profile = {"skills": ["python"], "interests": ["caring for peoples health"], "education_level": 2}
    loaded, _, _, _ = import_session_data(export_session(profile, {}), catalog)
    assert profile_from_input(loaded, catalog)[0].interests == ("caring for peoples health",)


# ---------- Output, warning and scoring protection ----------

def test_output_carries_keys_and_full_names(catalog):
    rec = recommend({"interests": ["Persuading, presenting and negotiating"]}, catalog, top_k=None)["recommendations"]
    c033 = next(r for r in rec if r["career_id"] == "C033")
    assert "persuading presenting and negotiating" in c033["matched_interests"]
    assert "Persuading, presenting and negotiating" in c033["matched_interest_labels"]
    assert '"Persuading, presenting and negotiating"' in " ".join(c033["reasons"])


def test_soft_warning_above_five_interests_with_no_cap(catalog):
    six = list(tx.CURRENT_INTERESTS[:6])
    result = recommend({"interests": six}, catalog)
    assert len(result["profile"]["interests"]) == 6
    assert any("6 interests were chosen" in w for w in result["warnings"])
    five = recommend({"interests": six[:5]}, catalog)
    assert not any("interests were chosen" in w for w in five["warnings"])


def test_scoring_formula_is_unchanged():
    assert DEFAULT_WEIGHTS.as_dict() == {"required_skills": 0.55, "preferred_skills": 0.15,
                                         "interests": 0.25, "education": 0.05}


def test_interest_value_is_still_matched_over_listed(catalog):
    career = catalog.get_career("C001")
    result = recommend({"interests": [tx.label_for(career.interests[0])]}, catalog, top_k=None)
    c001 = next(r for r in result["recommendations"] if r["career_id"] == "C001")
    assert c001["score"] == pytest.approx(round(100 * 0.25 / 3, 1))

