# Provenance and design of the eval64_v1 second-review sample (585 of 7,104 profile-career pairs)
# The sheet was first built by this exact procedure in an inline session step; this module reproduces it byte for byte
# Verify and write design tables: python -m src.evaluation.eval64_review_sampling --output reports/evaluation_64_review_design
# Check: python -m src.evaluation.eval64_review_sampling --check reports/evaluation_64_review_design

import argparse
import csv
import hashlib
import io
import json
import random
import sys
from collections import Counter
from pathlib import Path

from src.evaluation.eval64_data import EVAL64_DIR, read_manifest

SAMPLING_SEED = 6464
EXTRA_PER_PROFILE = 2
SHEET = EVAL64_DIR / "review" / "second_reviewer_sheet.csv"
SHEET_COLUMNS = ("profile_id", "career_id", "relevance_label", "justification", "reviewer", "confidence")
EXPLICIT, UNLISTED = "explicit_label", "unlisted_random"


def _rows(name):
    with open(EVAL64_DIR / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def generate_pairs():
    # Stratum 1: every pair the first labeller listed (census). Stratum 2: 2 unlisted careers per profile drawn
    # uniformly without replacement (seed 6464). Order within each profile is then shuffled.
    labels = _rows("relevance_labels.csv")
    career_ids = [r["career_id"] for r in _rows("careers.csv")]
    profile_ids = [r["profile_id"] for r in _rows("profiles.csv")]
    rng = random.Random(SAMPLING_SEED)
    pairs = []
    for pid in profile_ids:
        mine = [l["career_id"] for l in labels if l["profile_id"] == pid]
        extra = rng.sample([c for c in career_ids if c not in mine], EXTRA_PER_PROFILE)
        chosen = mine + extra
        rng.shuffle(chosen)
        pairs += [(pid, c) for c in chosen]
    return pairs


def sheet_text(pairs):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(SHEET_COLUMNS)
    for pid, cid in pairs:
        w.writerow([pid, cid, "", "", "", ""])
    return buf.getvalue()


def verify_sheet():
    # True when the procedure reproduces the frozen blank sheet and its recorded SHA-256
    text = sheet_text(generate_pairs())
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    recorded = read_manifest()["instruments_sha256"]["review/second_reviewer_sheet.csv"]
    return digest == hashlib.sha256(SHEET.read_bytes()).hexdigest() == recorded


def design():
    # Per sampled pair: stratum, first-labeller grade, inclusion probability and design weight
    labels = _rows("relevance_labels.csv")
    careers = {r["career_id"]: r for r in _rows("careers.csv")}
    profiles = {r["profile_id"]: r for r in _rows("profiles.csv")}
    grade = {(l["profile_id"], l["career_id"]): int(l["relevance_label"]) for l in labels}
    listed = Counter(l["profile_id"] for l in labels)
    out = []
    for pid, cid in generate_pairs():
        explicit = (pid, cid) in grade
        unlisted_pool = len(careers) - listed[pid]
        prob = 1.0 if explicit else EXTRA_PER_PROFILE / unlisted_pool
        out.append({
            "profile_id": pid, "career_id": cid, "stratum": EXPLICIT if explicit else UNLISTED,
            "original_grade": grade.get((pid, cid), 0), "inclusion_probability": round(prob, 6),
            "design_weight": round(1 / prob, 6), "profile_category": profiles[pid]["primary_category"],
            "career_category": careers[cid]["category"],
            "career_added_in_v1_3_0": int(cid[1:]) >= 51,
        })
    return out


def population_counts():
    labels = _rows("relevance_labels.csv")
    n_profiles, n_careers = len(_rows("profiles.csv")), len(_rows("careers.csv"))
    total = n_profiles * n_careers
    return {"pairs": total, "explicit": len(labels), "unlisted": total - len(labels)}


def _csv(rows, columns):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def build_outputs():
    rows = design()
    pop = population_counts()
    by_grade = Counter((r["stratum"], r["original_grade"]) for r in rows)
    grade_rows = [{"stratum": s, "original_grade": g, "pairs": n} for (s, g), n in sorted(by_grade.items())]
    career_counts = Counter((r["career_id"], r["career_category"], r["stratum"]) for r in rows)
    career_rows = []
    for cid in sorted({r["career_id"] for r in rows}):
        cat = next(r["career_category"] for r in rows if r["career_id"] == cid)
        e, u = career_counts[(cid, cat, EXPLICIT)], career_counts[(cid, cat, UNLISTED)]
        career_rows.append({"career_id": cid, "career_category": cat, "explicit_pairs": e, "unlisted_pairs": u,
                            "total_pairs": e + u})
    cat_rows = []
    for key in ("profile_category", "career_category"):
        counts = Counter((r[key], r["stratum"]) for r in rows)
        for cat in sorted({r[key] for r in rows}):
            cat_rows.append({"grouping": key, "category": cat, "explicit_pairs": counts[(cat, EXPLICIT)],
                             "unlisted_pairs": counts[(cat, UNLISTED)],
                             "total_pairs": counts[(cat, EXPLICIT)] + counts[(cat, UNLISTED)]})
    probs = sorted({r["inclusion_probability"] for r in rows if r["stratum"] == UNLISTED})
    summary = {
        "sheet_reproduced_byte_for_byte": verify_sheet(),
        "seed": SAMPLING_SEED,
        "population": pop,
        "sample": {"pairs": len(rows), "explicit": sum(r["stratum"] == EXPLICIT for r in rows),
                   "unlisted": sum(r["stratum"] == UNLISTED for r in rows),
                   "careers_represented": len({r["career_id"] for r in rows}),
                   "profiles_represented": len({r["profile_id"] for r in rows})},
        "design": ("Stratified by first-labeller listing. Stratum explicit_label: all 363 listed pairs, inclusion "
                   "probability 1 (a census, chosen by the labeller, so enriched for relevant pairs). Stratum "
                   "unlisted_random: 2 pairs per profile drawn uniformly without replacement from that profile's "
                   "unlisted careers, inclusion probability 2 / (64 - listed careers of the profile)."),
        "unlisted_inclusion_probabilities": probs,
        "sum_of_design_weights": round(sum(r["design_weight"] for r in rows), 3),
    }
    return {
        "review_sample_pairs.csv": _csv(rows, list(rows[0])),
        "review_sample_by_grade.csv": _csv(grade_rows, ["stratum", "original_grade", "pairs"]),
        "review_sample_by_career.csv": _csv(career_rows, list(career_rows[0])),
        "review_sample_by_category.csv": _csv(cat_rows, list(cat_rows[0])),
        "review_sample_design.json": json.dumps(summary, indent=2) + "\n",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Provenance and design of the eval64 second-review sample.")
    parser.add_argument("--output")
    parser.add_argument("--check")
    args = parser.parse_args(argv)
    files = build_outputs()
    if args.check:
        d = Path(args.check)
        diffs = [n for n, t in files.items() if not (d / n).exists() or (d / n).read_text(encoding="utf-8") != t]
        print("Differences: " + ", ".join(diffs) if diffs else f"Review-sample design outputs match {d}.")
        return 1 if diffs else 0
    out = Path(args.output or "reports/evaluation_64_review_design")
    out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
