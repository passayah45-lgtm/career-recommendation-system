# Second-review analysis for eval64_v1. Runs ONLY on a sheet completed by a real independent reviewer.
# The original labels in data/evaluation/catalog_v1.3.0/relevance_labels.csv are never changed.
# Run: python -m src.evaluation.eval64_review_analysis data/evaluation/catalog_v1.3.0/review/second_reviewer_<initials>.csv
#      (writes to reports/evaluation_64_review/<sheet name>/)

import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

from src.evaluation import independent_64_evaluation as ev
from src.evaluation.agreement import weighted_kappa
from src.evaluation.bootstrap import profile_bootstrap
from src.evaluation.eval64_data import CONFIDENCE, DEFAULT_THRESHOLD, EVAL64_DIR, GRADES
from src.evaluation.eval64_review_sampling import EXPLICIT, UNLISTED, design, population_counts

BLANK_SHEET = EVAL64_DIR / "review" / "second_reviewer_sheet.csv"
REVIEW_COLUMNS = ("profile_id", "career_id", "relevance_label", "justification", "reviewer", "confidence")
DEFAULT_OUT = ev.ROOT / "reports" / "evaluation_64_review"
DECIMALS = 4
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 64
# Reviewer names that identify the first labeller or a test fixture; such sheets are not independent review data
NOT_INDEPENDENT = ("claude", "assistant", "fixture", "test", "first labeller", "anthropic")
INSUFFICIENT_PREFIX = "INSUFFICIENT:"


class ReviewSheetError(ValueError):
    pass


def _r(value):
    return None if value is None else round(value, DECIMALS)


def _read_pairs(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if tuple(reader.fieldnames or ()) != REVIEW_COLUMNS:
            raise ReviewSheetError(f"{Path(path).name}: columns must be {', '.join(REVIEW_COLUMNS)}")
        return list(reader)


def load_review(path, blank_path=BLANK_SHEET):
    # Returns ({(profile_id, career_id): grade}, reviewers, notes); refuses a blank, partial or altered sheet
    if Path(path).resolve() == Path(blank_path).resolve():
        raise ReviewSheetError("this is the blank sheet; save the reviewer's copy under a new name")
    blank = [(r["profile_id"], r["career_id"]) for r in _read_pairs(blank_path)]
    rows = _read_pairs(path)
    pairs = [(r["profile_id"], r["career_id"]) for r in rows]
    if sorted(pairs) != sorted(blank) or len(set(pairs)) != len(pairs):
        raise ReviewSheetError("the sheet must contain exactly the pairs of the blank sheet, each once")
    grades, reviewers = {}, set()
    notes = {"insufficient_information_rows": 0, "confidence": {c: 0 for c in CONFIDENCE}}
    for r in rows:
        key = (r["profile_id"], r["career_id"])
        value = (r["relevance_label"] or "").strip()
        if not value:
            raise ReviewSheetError(f"{key}: no grade; agreement needs a completed sheet")
        if not value.isdigit() or int(value) not in GRADES:
            raise ReviewSheetError(f"{key}: grade must be one of {GRADES}")
        if not (r["reviewer"] or "").strip():
            raise ReviewSheetError(f"{key}: reviewer is required")
        if r["confidence"] not in CONFIDENCE:
            raise ReviewSheetError(f"{key}: confidence must be one of {CONFIDENCE}")
        if not (r["justification"] or "").strip():
            raise ReviewSheetError(f"{key}: justification is required")
        reviewers.add(r["reviewer"].strip())
        grades[key] = int(value)
        notes["confidence"][r["confidence"]] += 1
        notes["insufficient_information_rows"] += r["justification"].strip().upper().startswith(INSUFFICIENT_PREFIX)
    return grades, sorted(reviewers), notes


def check_independent(reviewers):
    # Command-line guard: a sheet signed by the first labeller or a fixture is never treated as review data
    for name in reviewers:
        if any(word in name.lower() for word in NOT_INDEPENDENT):
            raise ReviewSheetError(f"reviewer '{name}' is not an independent human reviewer")


def agreement(pairs):
    # pairs: list of (original_grade, reviewer_grade)
    n = len(pairs)
    matrix = [[sum(1 for a, b in pairs if a == i and b == j) for j in GRADES] for i in GRADES]
    binary = [(int(a >= DEFAULT_THRESHOLD), int(b >= DEFAULT_THRESHOLD)) for a, b in pairs]
    return {
        "pairs": n,
        "exact_agreement": _r(sum(1 for a, b in pairs if a == b) / n),
        "within_one_grade": _r(sum(1 for a, b in pairs if abs(a - b) <= 1) / n),
        "quadratic_weighted_kappa": _r(weighted_kappa(pairs)),
        "linear_weighted_kappa": _r(weighted_kappa(pairs, weighting="linear")),
        "binary_kappa_grade2plus": _r(weighted_kappa(binary, categories=(0, 1), weighting="linear")),
        "binary_agreement_grade2plus": _r(sum(1 for a, b in binary if a == b) / n),
        "confusion_matrix_rows_original_cols_reviewer": matrix,
    }


def _weighted_stats(records):
    # Design-weighted agreement over all 7,104 pairs: every record carries its inverse inclusion probability
    pairs = [(r["original"], r["reviewer"]) for r in records]
    w = [r["design_weight"] for r in records]
    binary = [(int(a >= DEFAULT_THRESHOLD), int(b >= DEFAULT_THRESHOLD)) for a, b in pairs]
    total = sum(w)
    return {
        "quadratic_weighted_kappa": weighted_kappa(pairs, sample_weights=w),
        "linear_weighted_kappa": weighted_kappa(pairs, weighting="linear", sample_weights=w),
        "binary_kappa_grade2plus": weighted_kappa(binary, categories=(0, 1), weighting="linear", sample_weights=w),
        "exact_agreement": sum(wi for (a, b), wi in zip(pairs, w) if a == b) / total,
    }


def _unlisted_stats(records):
    # Ratio estimates over the 6,741 unlisted pairs from the 222 sampled ones
    rows = [r for r in records if r["stratum"] == UNLISTED]
    total = sum(r["design_weight"] for r in rows)
    out = {}
    for t in (1, 2, 3):
        share = sum(r["design_weight"] for r in rows if r["reviewer"] >= t) / total if total else None
        out[f"share_reviewer_grade_{t}plus"] = share
    return out


def _cluster_bootstrap(records, statistic):
    # Resamples whole profiles with replacement, because pairs from one profile are not independent
    by_profile = defaultdict(list)
    for r in records:
        by_profile[r["profile_id"]].append(r)
    ids = sorted(by_profile)
    rng = random.Random(BOOTSTRAP_SEED)
    draws = defaultdict(list)
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [r for _ in ids for r in by_profile[ids[rng.randrange(len(ids))]]]
        for name, value in statistic(sample).items():
            if value is not None:
                draws[name].append(value)
    point = statistic(records)
    out = {}
    for name, value in point.items():
        d = sorted(draws[name])
        out[name] = {"estimate": _r(value),
                     "ci95": [_r(d[int(0.025 * len(d))]), _r(d[min(len(d) - 1, int(0.975 * len(d)))])] if d else None}
    return out


def design_based_agreement(records):
    pop = population_counts()
    explicit = [r for r in records if r["stratum"] == EXPLICIT]
    unlisted = [r for r in records if r["stratum"] == UNLISTED]
    unlisted_boot = _cluster_bootstrap(records, _unlisted_stats)
    for name, value in list(unlisted_boot.items()):
        if value["estimate"] is not None:
            unlisted_boot[name]["estimated_pairs_of_6741"] = round(value["estimate"] * pop["unlisted"])
    return {
        "explicit_label_stratum": {
            "applies_to": f"the {pop['explicit']} pairs the first labeller listed (a census of that set)",
            **agreement([(r["original"], r["reviewer"]) for r in explicit]),
        },
        "unlisted_stratum": {
            "applies_to": (f"the {pop['unlisted']} pairs the first labeller did not list (grade 0 by rule R8), "
                           f"estimated from {len(unlisted)} randomly sampled pairs"),
            "reviewer_grade_counts": {str(g): sum(1 for r in unlisted if r["reviewer"] == g) for g in GRADES},
            "estimates": unlisted_boot,
            "note": "Kappa is undefined here because the first labeller's grade is constant (0)",
        },
        "all_pairs_design_weighted": {
            "applies_to": (f"all {pop['pairs']} profile-career pairs, using design weights; dominated by unlisted "
                           f"pairs ({pop['unlisted']} of {pop['pairs']})"),
            "estimates": _cluster_bootstrap(records, _weighted_stats),
        },
        "review_sample_unweighted": {
            "applies_to": "the 585 reviewed pairs only; enriched for listed pairs, NOT representative of all pairs",
            **agreement([(r["original"], r["reviewer"]) for r in records]),
        },
        "bootstrap": f"profile-clustered percentile, {BOOTSTRAP_RESAMPLES} resamples, seed {BOOTSTRAP_SEED}",
    }


def disagreement_table(records, key):
    groups = defaultdict(list)
    for rec in records:
        groups[rec[key]].append(rec)
    out = []
    for name in sorted(groups):
        g = groups[name]
        out.append({
            key: name, "pairs": len(g),
            "exact_agreement": _r(sum(1 for x in g if x["original"] == x["reviewer"]) / len(g)),
            "mean_absolute_difference": _r(sum(abs(x["original"] - x["reviewer"]) for x in g) / len(g)),
            "binary_disagreements": sum(1 for x in g if (x["original"] >= DEFAULT_THRESHOLD)
                                        != (x["reviewer"] >= DEFAULT_THRESHOLD)),
            "reviewer_higher": sum(1 for x in g if x["reviewer"] > x["original"]),
            "reviewer_lower": sum(1 for x in g if x["reviewer"] < x["original"]),
        })
    return out


def rescored_metrics(rows, label_sets):
    # Recomputes the main metrics on the frozen rankings with each alternative label set
    out = {}
    for name, labels in label_sets.items():
        per = [ev.profile_metrics(r["ranking"], labels[r["profile_id"]]) for r in rows]
        stats = profile_bootstrap(per, ev.METRICS)
        out[name] = {m: {"mean": _r(s["mean"]), "ci_low": _r(s["ci_low"]), "ci_high": _r(s["ci_high"]),
                         "defined_profiles": s["defined_profiles"]} for m, s in stats.items()}
    return out


def analyse(review_path, blank_path=BLANK_SHEET):
    catalog, profiles, labels = ev.load_frozen()
    review, reviewers, notes = load_review(review_path, blank_path)
    category = {p.profile_id: p.primary_category for p in profiles}
    title = {c.career_id: c.title for c in catalog.careers}
    plan = {(d["profile_id"], d["career_id"]): d for d in design()}
    records = [{"profile_id": pid, "career_id": cid, "career_title": title[cid], "category": category[pid],
                "stratum": plan[(pid, cid)]["stratum"], "design_weight": plan[(pid, cid)]["design_weight"],
                "original": labels[pid].get(cid, 0), "reviewer": g} for (pid, cid), g in sorted(review.items())]
    reviewer_labels = {p.profile_id: {} for p in profiles}
    for (pid, cid), g in review.items():
        reviewer_labels[pid][cid] = g
    # Conservative consensus: the lower of the two grades, so a career is relevant only if both agree
    consensus = {pid: {c: min(labels[pid].get(c, 0), reviewer_labels[pid].get(c, 0))
                       for c in set(labels[pid]) | set(reviewer_labels[pid])} for pid in labels}
    rows, _ = ev.run_profiles(catalog, profiles, labels)
    return {
        "study_id": ev.STUDY_ID, "review_sheet": str(review_path), "reviewers": reviewers,
        "note": ("Agreement between the first labeller and an independent human reviewer. The 585 pairs are a stratified, "
                 "enriched sample of 7,104; read each statistic with the population it applies to."),
        "agreement": design_based_agreement(records),
        "reviewer_notes": notes,
        "by_category": disagreement_table(records, "category"),
        "by_career": disagreement_table(records, "career_id"),
        "metrics": rescored_metrics(rows, {"original_labels": labels, "reviewer_labels": reviewer_labels,
                                           "consensus_min_grade": consensus}),
        "metrics_note": ("Reviewer labels exist only for the 585 sampled pairs; the 6,519 unsampled unlisted pairs stay "
                         "grade 0 in every label set, so reviewer-found relevance outside the sample is not counted."),
        "disagreements": [x for x in records if x["original"] != x["reviewer"]],
    }


def write(result, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "review_summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name in ("by_category", "by_career", "disagreements"):
        rows = result[name]
        if not rows:
            continue
        with open(out / f"review_{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)


def _deanonymise(path):
    # Writes the completed anonymised sheet back in the original columns to a temporary file
    import tempfile
    from src.evaluation.eval64_anonymise import to_original_rows
    try:
        rows = to_original_rows(path)
    except (ValueError, KeyError) as exc:
        raise ReviewSheetError(f"anonymised sheet not usable: {exc}") from exc
    tmp = Path(tempfile.mkdtemp(prefix="eval64_review_")) / "deanonymised.csv"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=REVIEW_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return tmp


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analyse a completed second-reviewer sheet for eval64_v1.")
    parser.add_argument("review_sheet")
    parser.add_argument("--output", help="output directory (default reports/evaluation_64_review/<sheet name>)")
    parser.add_argument("--confirm-independent-reviewer", action="store_true",
                        help="confirm that a real person outside the project completed the sheet and signed the declaration")
    parser.add_argument("--anonymised", action="store_true",
                        help="the sheet is the anonymised reviewer copy; codes are mapped back with the private mapping")
    args = parser.parse_args(argv)
    path = Path(args.review_sheet)
    if not path.exists():
        print(f"No such file: {path}")
        return 2
    if not args.confirm_independent_reviewer:
        print("Refused: pass --confirm-independent-reviewer only for a sheet completed by a real independent reviewer.")
        return 1
    source = path
    try:
        if args.anonymised:
            path = _deanonymise(path)
        _, reviewers, _ = load_review(path)
        check_independent(reviewers)
        result = analyse(path)
        result["review_sheet"] = str(source)
    except ReviewSheetError as exc:
        print(f"Review sheet not usable: {exc}")
        return 1
    out = Path(args.output) if args.output else DEFAULT_OUT / source.stem
    write(result, out)
    a = result["agreement"]["explicit_label_stratum"]
    print(f"Wrote {out}: listed-pair stratum ({a['pairs']} pairs) quadratic weighted kappa {a['quadratic_weighted_kappa']}; "
          "see review_summary.json for the unlisted stratum and the design-weighted estimates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
