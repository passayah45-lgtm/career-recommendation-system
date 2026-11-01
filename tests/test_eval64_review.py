# eval64_v1 review tasks: vocabulary, profile types, exposure, ties and the second-review analysis
# Review-analysis tests build temporary fixture sheets in tmp_path; they are never saved or reported as review data

import csv
import re
import json
from pathlib import Path

import pytest

from src.evaluation import eval64_diagnostics as dg
from src.evaluation import independent_64_evaluation as ev
from src.evaluation.eval64_data import EVAL64_DIR, read_manifest, verify_frozen
from src.evaluation.eval64_review_analysis import BLANK_SHEET, REVIEW_COLUMNS, ReviewSheetError, analyse, load_review

from tests.conftest import EVAL64_LABELS_AVAILABLE, needs_eval64_labels  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "evaluation_64"


@pytest.fixture(scope="module")
def frozen():
    return ev.load_frozen()


def _read(name):
    with open(OUT / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------- Vocabulary ----------

@needs_eval64_labels
def test_vocabulary_uses_one_documented_denominator(frozen):
    catalog, profiles, _ = frozen
    rows, zero, _ = dg.vocabulary_analysis(catalog, profiles)
    total = rows[0]
    assert total["scope"] == "all profiles"
    assert total["skill_entries"] == sum(len(p.skills) for p in profiles) == 480
    assert total["unrecognised_entries"] == 269 and total["unrecognised_share"] == pytest.approx(0.5604)
    assert total["profiles_no_skill_recognised"] == len(zero) == 22
    assert total["profiles_without_skills"] == 3
    # Type rows partition the profiles and the skill entries
    types = [r for r in rows if r["scope"].startswith("type: ")]
    assert sum(r["profiles"] for r in types) == 111 and sum(r["skill_entries"] for r in types) == 480


@needs_eval64_labels
def test_zero_recognised_profiles_really_have_no_known_skill(frozen):
    catalog, profiles, _ = frozen
    from src.services.recommendations import profile_from_input
    _, zero, _ = dg.vocabulary_analysis(catalog, profiles)
    by_id = {p.profile_id: p for p in profiles}
    for z in zero:
        profile, _ = profile_from_input(by_id[z["profile_id"]].as_input(), catalog)
        assert profile.skills == () or list(profile.skills) == []


def test_reports_carry_no_conflicting_vocabulary_share():
    bias = _read("bias_analysis.csv")
    shares = {r["group"]: r["value"] for r in bias if r["analysis"] == "unrecognised_skill_share"}
    assert shares["all profiles"] == "0.5604"
    assert "other profiles" not in shares
    for doc in ("independent_64_evaluation_results.md", "independent_64_evaluation_risks.md"):
        text = (ROOT / "docs" / doc).read_text(encoding="utf-8")
        assert "54%" not in text and "0.544" not in text


# ---------- Profile types ----------

def test_profile_type_table_covers_all_types_with_sample_status():
    rows = _read("profile_type_metrics.csv")
    assert len(rows) == 12 and sum(int(r["profiles"]) for r in rows) == 111
    status = {r["profile_type"]: r["sample_status"] for r in rows}
    assert status["strong_match"].startswith("reported") and status["french_vocabulary"].startswith("reported")
    assert status["minimal_input"].startswith("insufficient")
    assert dg.sample_status(4).startswith("insufficient") and dg.sample_status(9).startswith("indicative")


# ---------- Exposure ----------

def test_exposure_tables_are_consistent():
    cats = _read("exposure_by_category.csv")
    careers = _read("exposure_by_career.csv")
    assert sum(int(r["top5_slots"]) for r in cats) == 555 == sum(int(r["top5_appearances"]) for r in careers)
    for r in cats:
        assert int(r["slots_from_own_category_profiles"]) + int(r["slots_from_other_profiles"]) == int(r["top5_slots"])
        assert (int(r["relevant_slots_grade2plus"]) + int(r["weak_slots_grade1"])
                + int(r["not_relevant_slots_grade0"])) == int(r["top5_slots"])
    c004 = next(r for r in careers if r["career_id"] == "C004")
    if EVAL64_LABELS_AVAILABLE:
        assert len(_read("exposure_examples_C004.csv")) == int(c004["top5_appearances"])


# ---------- Ties ----------

@needs_eval64_labels
def test_tie_analysis_follows_the_engine_sort_key(frozen):
    catalog, profiles, labels = frozen
    summary, rows, groups = dg.tie_analysis(catalog, profiles, labels)
    values = {s["measure"]: s["value"] for s in summary}
    assert len(rows) == 111
    assert values["new-before-original pairs decided by career id, any rank"] == 0
    resolved = sum(values[k] for k in values if k.startswith("rank 5/6 tie resolved by"))
    assert resolved == values["total-score tie at rank 5/6 (engine precision)"]
    for g in groups:
        assert g["careers_in_top5"] and g["careers_outside_top5"]
        # Inside an id tie, every career in the top 5 has a lower id than every career outside it
        assert max(g["careers_in_top5"].split("|")) < min(g["careers_outside_top5"].split("|"))


# ---------- Second review ----------

def _sheet(path, grade_for, reviewer="Fixture reviewer", blank_row=None):
    with open(BLANK_SHEET, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=REVIEW_COLUMNS, lineterminator="\n")
        w.writeheader()
        for i, r in enumerate(rows):
            grade = "" if i == blank_row else str(grade_for(r["profile_id"], r["career_id"]))
            w.writerow({**r, "relevance_label": grade, "justification": "fixture", "reviewer": reviewer,
                        "confidence": "medium"})
    return path


def test_review_analysis_refuses_blank_and_incomplete_sheets(tmp_path):
    with pytest.raises(ReviewSheetError, match="blank sheet"):
        load_review(BLANK_SHEET)
    with pytest.raises(ReviewSheetError, match="no grade"):
        load_review(_sheet(tmp_path / "partial.csv", lambda p, c: 1, blank_row=3))
    with pytest.raises(ReviewSheetError, match="reviewer is required"):
        load_review(_sheet(tmp_path / "anon.csv", lambda p, c: 1, reviewer=""))
    with pytest.raises(ReviewSheetError, match="grade must be"):
        load_review(_sheet(tmp_path / "bad.csv", lambda p, c: 5))


@needs_eval64_labels
def test_review_analysis_on_fixture_sheets(tmp_path, frozen):
    _, _, labels = frozen
    same = analyse(_sheet(tmp_path / "same.csv", lambda p, c: labels[p].get(c, 0)))
    agree = same["agreement"]
    assert agree["explicit_label_stratum"]["quadratic_weighted_kappa"] == 1.0 and same["disagreements"] == []
    assert agree["explicit_label_stratum"]["pairs"] == 363
    assert agree["all_pairs_design_weighted"]["estimates"]["quadratic_weighted_kappa"]["estimate"] == 1.0
    assert agree["unlisted_stratum"]["estimates"]["share_reviewer_grade_1plus"]["estimate"] == 0.0
    assert agree["review_sample_unweighted"]["pairs"] == 585
    assert "NOT representative" in agree["review_sample_unweighted"]["applies_to"]
    assert same["metrics"]["reviewer_labels"] == same["metrics"]["original_labels"]
    shifted = analyse(_sheet(tmp_path / "shifted.csv", lambda p, c: min(3, labels[p].get(c, 0) + 1)))
    assert shifted["agreement"]["review_sample_unweighted"]["exact_agreement"] < 1.0
    unlisted = shifted["agreement"]["unlisted_stratum"]
    # Every unlisted pair was graded 1 by the fixture, so the estimate covers all 6,741 unlisted pairs
    assert unlisted["estimates"]["share_reviewer_grade_1plus"]["estimate"] == 1.0
    assert unlisted["estimates"]["share_reviewer_grade_1plus"]["estimated_pairs_of_6741"] == 6741
    assert unlisted["reviewer_grade_counts"]["1"] == 222
    assert sum(r["pairs"] for r in shifted["by_category"]) == 585
    assert all(r["reviewer_lower"] == 0 for r in shifted["by_career"])


def test_no_reviewer_data_or_agreement_exists_yet():
    review_dir = EVAL64_DIR / "review"
    completed = [p for p in review_dir.glob("*.csv") if p.name != "second_reviewer_sheet.csv"]
    assert completed == []
    assert not (ROOT / "reports" / "evaluation_64_review").exists()
    assert read_manifest()["second_reviewer"] is None
    summary = json.loads((OUT / "evaluation_summary.json").read_text(encoding="utf-8"))
    assert summary["data"]["inter_rater_agreement"] is None


def test_blank_sheet_and_packet_carry_no_grades():
    with open(BLANK_SHEET, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 585 and all(not r["relevance_label"] for r in rows)
    packet = (EVAL64_DIR / "review" / "reviewer_packet.md").read_text(encoding="utf-8")
    assert "relevance_label" not in packet
    assert len(re.findall(r"^\| C\d{3} \|", packet, flags=re.M)) == 585
    if EVAL64_LABELS_AVAILABLE:
        assert verify_frozen() == []


# ---------- Handover readiness ----------

def _rewrite(src, dst, transform):
    with open(src, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows = transform(rows)
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=REVIEW_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return dst


@pytest.mark.parametrize("transform, message", [
    (lambda rows: rows[:-1], "exactly the pairs"),
    (lambda rows: rows + rows[:1], "exactly the pairs"),
    (lambda rows: [{**rows[0], "career_id": "C063" if rows[0]["career_id"] != "C063" else "C064"}] + rows[1:],
     "exactly the pairs"),
    (lambda rows: [{**rows[0], "justification": ""}] + rows[1:], "justification is required"),
    (lambda rows: [{**rows[0], "confidence": ""}] + rows[1:], "confidence"),
])
def test_altered_sheets_are_refused(tmp_path, transform, message):
    complete = _sheet(tmp_path / "complete.csv", lambda p, c: 1)
    with pytest.raises(ReviewSheetError, match=message):
        load_review(_rewrite(complete, tmp_path / "altered.csv", transform))


def test_command_line_needs_confirmation_and_a_real_reviewer(tmp_path, capsys):
    from src.evaluation import eval64_review_analysis as ra
    sheet = _sheet(tmp_path / "s.csv", lambda p, c: 1)
    assert ra.main([str(sheet)]) == 1
    assert "Refused" in capsys.readouterr().out
    # A fixture or first-labeller name is refused even with the flag, so no agreement is computed
    assert ra.main([str(sheet), "--confirm-independent-reviewer", "--output", str(tmp_path / "out")]) == 1
    assert not (tmp_path / "out").exists()
    claude = _sheet(tmp_path / "c.csv", lambda p, c: 1, reviewer="Claude")
    assert ra.main([str(claude), "--confirm-independent-reviewer", "--output", str(tmp_path / "out2")]) == 1
    assert ra.main([str(BLANK_SHEET), "--confirm-independent-reviewer"]) == 1
    assert not (tmp_path / "out2").exists()


def test_insufficient_information_rows_are_counted(tmp_path):
    complete = _sheet(tmp_path / "complete.csv", lambda p, c: 0)
    flagged = _rewrite(complete, tmp_path / "flagged.csv", lambda rows: [
        {**r, "justification": "INSUFFICIENT: no skills given", "confidence": "low"} if i < 7 else r
        for i, r in enumerate(rows)])
    _, _, notes = load_review(flagged)
    assert notes["insufficient_information_rows"] == 7 and notes["confidence"]["low"] == 7


def test_packet_gives_enough_information_and_no_labels():
    packet = (EVAL64_DIR / "review" / "reviewer_packet.md").read_text(encoding="utf-8")
    if EVAL64_LABELS_AVAILABLE:
        with open(EVAL64_DIR / "relevance_labels.csv", newline="", encoding="utf-8") as f:
            labels = list(csv.DictReader(f))
        assert not [l for l in labels if l["justification"] in packet]
    # Profile types, scores and positions from the app never appear; the header only says they are absent
    for word in ("strong_match", "no_clear_fit", "profile_type", "score", "top 5", "| rank"):
        assert word not in packet.lower()
    profiles = re.split(r"^## ", packet, flags=re.M)[1:]
    assert len(profiles) == 111
    for block in profiles:
        for field in ("- Learner:", "- Goal:", "- Skills typed:", "- Interests:", "- Education:"):
            assert field in block
    assert "INSUFFICIENT:" in packet and "O*NET" in packet
    rows = re.findall(r"^\| C\d{3} \|.*$", packet, flags=re.M)
    assert len(rows) == 585 and all(r.count("|") == 7 for r in rows)


def test_handover_documents_cover_the_required_points():
    handover = (ROOT / "docs" / "reviewer_handover.md").read_text(encoding="utf-8")
    for phrase in ("Purpose", "The work", "Independence and confidentiality", "Submission", "Reviewer declaration",
                   "--confirm-independent-reviewer", "INSUFFICIENT:"):
        assert phrase in handover
    guide = (ROOT / "docs" / "independent_64_second_review_guide.md").read_text(encoding="utf-8")
    assert "When the information is not enough" in guide and "| 3 | Strong |" in guide



# ---------- Sampling design and anonymisation ----------

@needs_eval64_labels
def test_sampling_procedure_reproduces_the_frozen_sheet():
    from src.evaluation import eval64_review_sampling as rs
    assert rs.verify_sheet()
    design = rs.design()
    assert len(design) == 585 and len({(d["profile_id"], d["career_id"]) for d in design}) == 585
    assert sum(d["stratum"] == rs.EXPLICIT for d in design) == 363
    assert sum(d["stratum"] == rs.UNLISTED for d in design) == 222
    assert {d["inclusion_probability"] for d in design if d["stratum"] == rs.EXPLICIT} == {1.0}
    assert abs(sum(d["design_weight"] for d in design) - 7104) < 1e-3
    assert len({d["career_id"] for d in design}) == 64 and len({d["profile_id"] for d in design}) == 111
    assert rs.population_counts() == {"pairs": 7104, "explicit": 363, "unlisted": 6741}
    assert rs.main(["--check", str(ROOT / "reports" / "evaluation_64_review_design")]) == 0


def test_weighted_kappa_with_sample_weights():
    from src.evaluation.agreement import weighted_kappa
    pairs = [(0, 0), (1, 1), (2, 1), (3, 3)]
    assert weighted_kappa(pairs, sample_weights=[1, 1, 1, 1]) == weighted_kappa(pairs)
    # Doubling a pair's weight equals duplicating it
    assert weighted_kappa(pairs, sample_weights=[1, 1, 2, 1]) == pytest.approx(weighted_kappa(pairs + [(2, 1)]))
    with pytest.raises(ValueError):
        weighted_kappa(pairs, sample_weights=[1, 1])


# The private key is git-ignored, so tests that need it run only where the key exists (never in public CI)
from src.evaluation.eval64_anonymise import MAPPING as _PRIVATE_KEY
needs_private_key = pytest.mark.skipif(not _PRIVATE_KEY.exists(), reason="private anonymisation key is not published")


def test_anonymised_copy_hides_ids_and_is_blank():
    from src.evaluation import eval64_anonymise as an
    sheet = an.ANON_SHEET.read_text(encoding="utf-8")
    packet = an.ANON_PACKET.read_text(encoding="utf-8")
    for text in (sheet, packet):
        assert not re.search(r"E64-|\bC0\d\d\b|\bC064\b", text)
        assert "O*NET" not in text and "onetonline" not in text
    rows = list(csv.DictReader(open(an.ANON_SHEET, newline="", encoding="utf-8")))
    assert len(rows) == 585 and all(not r[c] for r in rows for c in ("relevance_label", "justification",
                                                                    "reviewer", "confidence"))
    assert len({(r["profile_code"], r["career_code"]) for r in rows}) == 585
    assert len({r["profile_code"] for r in rows}) == 111 and len({r["career_code"] for r in rows}) == 64
    if EVAL64_LABELS_AVAILABLE:
        with open(EVAL64_DIR / "relevance_labels.csv", newline="", encoding="utf-8") as f:
            assert not [l for l in csv.DictReader(f) if l["justification"] in packet]


@needs_private_key
def test_private_key_maps_the_anonymised_copy_exactly():
    from src.evaluation import eval64_anonymise as an
    assert an.verify() == []
    rows = list(csv.DictReader(open(an.ANON_SHEET, newline="", encoding="utf-8")))
    mapping = an.read_mapping()
    assert len(mapping["profiles"]) == 111 and len(mapping["careers"]) == 64
    assert len({r["career_code"] for r in rows}) == 64
    # Codes carry no order: profile order is not the original category order
    order = [mapping["profiles"][c] for c in dict.fromkeys(r["profile_code"] for r in rows)]
    assert order != sorted(order)


@needs_private_key
def test_anonymised_sheet_round_trip(tmp_path, frozen):
    from src.evaluation import eval64_anonymise as an
    from src.evaluation.eval64_review_analysis import _deanonymise
    _, _, labels = frozen
    m = an.read_mapping()
    rows = list(csv.DictReader(open(an.ANON_SHEET, newline="", encoding="utf-8")))
    completed = tmp_path / "anon_completed.csv"
    with open(completed, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=an.ANON_COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            g = labels[m["profiles"][r["profile_code"]]].get(m["careers"][r["career_code"]], 0)
            w.writerow({**r, "relevance_label": g, "justification": "fixture", "reviewer": "Fixture reviewer",
                        "confidence": "high"})
    result = analyse(_deanonymise(completed))
    assert result["agreement"]["explicit_label_stratum"]["quadratic_weighted_kappa"] == 1.0
    # The blank anonymised sheet cannot produce statistics
    with pytest.raises(ReviewSheetError):
        load_review(_deanonymise(an.ANON_SHEET))


@needs_private_key
def test_anonymised_build_refuses_to_replace_the_mapping():
    from src.evaluation import eval64_anonymise as an
    with pytest.raises(SystemExit):
        an.write()
