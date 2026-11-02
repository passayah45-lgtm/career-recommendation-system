# Evaluation of dataset v1.4.0 (interest taxonomy 2.0) on the frozen eval64_v1 profiles and labels
# Separate study: it reads eval64_v1 and the frozen v1.3.0 snapshot but never writes to them
# Run from the project root:
#   python -m src.evaluation.taxonomy_v140_evaluation --freeze            (once, copies the live v1.4.0 catalogue)
#   python -m src.evaluation.taxonomy_v140_evaluation --output reports/evaluation_v1_4_0
#   python -m src.evaluation.taxonomy_v140_evaluation --check reports/evaluation_v1_4_0

import argparse
import csv
import io
import json
import random
import shutil
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from src.data.interest_taxonomy import (
    CURRENT_INTERESTS, CURRENT_TAXONOMY, LEGACY_TO_CURRENT, RETIRED_LEGACY, label_for, migrate_interest_list,
)
from src.data.preprocessing import clean_skill_text
from src.data.validation import CATEGORIES, DEFAULT_DATA_DIR
from src.evaluation import independent_64_evaluation as ev
from src.evaluation.bootstrap import DEFAULT_RESAMPLES, DEFAULT_SEED, profile_bootstrap
from src.evaluation.eval64_data import (
    CATALOG_FILES, EVAL64_DIR, LABELS_FILE, PROFILES_FILE, load_eval64, read_manifest as read_eval64_manifest,
    sha256_of, verify_frozen,
)
from src.services.catalog import load_catalog

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = ROOT / "data" / "evaluation" / "catalog_v1.4.0"
MANIFEST_FILE = "evaluation_manifest.json"
SUMMARY_FILE = "taxonomy_evaluation_summary.json"
COMPARISON_FILE = "metric_comparison.csv"
CATEGORY_FILE = "category_exposure.csv"
MIGRATION_FILE = "profile_interest_migration.csv"
OUTPUT_FILES = (SUMMARY_FILE, COMPARISON_FILE, CATEGORY_FILE, MIGRATION_FILE)
STUDY_ID = "eval_v1.4.0_taxonomy"
METRICS = ev.METRICS
K = ev.K

# A: frozen v1.3.0 catalogue with the original profiles (must reproduce the frozen eval64_v1 means)
# A2: v1.3.0 catalogue, profiles with the five retired old interests removed (isolates that loss)
# B: v1.4.0 catalogue, profile interests migrated to taxonomy 2.0 (the new result)
CONDITIONS = {
    "A_v130_original": "v1.3.0 catalogue, original eval64 profiles (frozen eval64_v1 configuration)",
    "A2_v130_retired_removed": "v1.3.0 catalogue, profiles without the five retired old interest names",
    "B_v140_migrated": "v1.4.0 catalogue, profile interests migrated to interest taxonomy 2.0",
}


class SnapshotError(RuntimeError):
    pass


def freeze(snapshot_dir=SNAPSHOT_DIR):
    # Copies the live catalogue once and records SHA-256 values; refuses to overwrite an existing snapshot
    snapshot_dir = Path(snapshot_dir)
    if (snapshot_dir / MANIFEST_FILE).exists():
        raise SnapshotError(f"{snapshot_dir} is already frozen; it is never overwritten")
    live = json.loads((DEFAULT_DATA_DIR / "dataset_manifest.json").read_text(encoding="utf-8"))
    if live.get("dataset_version") != "1.4.0" or live.get("interest_taxonomy") != CURRENT_TAXONOMY:
        raise SnapshotError("the live catalogue is not dataset v1.4.0 with interest taxonomy 2.0")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for name in CATALOG_FILES:
        shutil.copyfile(DEFAULT_DATA_DIR / name, snapshot_dir / name)
    eval64 = read_eval64_manifest()
    manifest = {
        "study_id": STUDY_ID,
        "frozen_on": date.today().isoformat(),
        "note": "Frozen copy of the v1.4.0 catalogue (interest taxonomy 2.0, owner-authorized pending lecturer "
                "feedback). Profiles and labels are not copied: they are read from eval64_v1, whose SHA-256 "
                "values are recorded below and checked before every run. Never edit these files.",
        "sha256": {name: sha256_of(snapshot_dir / name) for name in CATALOG_FILES},
        "eval64_inputs": {"directory": "data/evaluation/catalog_v1.3.0",
                          "sha256": {n: eval64["sha256"][n] for n in (PROFILES_FILE, LABELS_FILE)}},
        "profile_interest_migration": "src.data.interest_taxonomy.migrate_interest_list",
    }
    (snapshot_dir / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                              encoding="utf-8")
    return manifest


def verify_snapshot(snapshot_dir=SNAPSHOT_DIR):
    # Returns the names of changed files: snapshot catalogue files and the eval64 inputs it relies on
    snapshot_dir = Path(snapshot_dir)
    manifest = json.loads((snapshot_dir / MANIFEST_FILE).read_text(encoding="utf-8"))
    changed = [n for n, h in manifest["sha256"].items() if sha256_of(snapshot_dir / n) != h]
    for name, h in manifest["eval64_inputs"]["sha256"].items():
        path = EVAL64_DIR / name
        if path.exists() and sha256_of(path) != h:
            changed.append(f"eval64 {name}")
    return changed


def migrate_profile(p):
    # Returns (input for the v1.4.0 catalogue, migration record)
    data = p.as_input()
    keys, migrated, retired, unknown = migrate_interest_list(p.interests)
    data["interests"] = list(keys)
    record = {"profile_id": p.profile_id, "primary_category": p.primary_category,
              "old_interests": "|".join(p.interests), "new_interests": "|".join(keys),
              "migrated": len(migrated), "retired": len(retired), "unknown": len(unknown),
              "interests_before": len(p.interests), "interests_after": len(keys)}
    return data, record


def without_retired(p):
    data = p.as_input()
    data["interests"] = [i for i in p.interests if clean_skill_text(i) not in RETIRED_LEGACY]
    return data


def run_condition(catalog, inputs, profiles, labels):
    rows = []
    for p in profiles:
        ranking, scores = ev.rank(inputs[p.profile_id], catalog)
        grades = labels[p.profile_id]
        rows.append({"profile_id": p.profile_id, "primary_category": p.primary_category,
                     "top5": ranking[:K], "ranking": ranking, "scores": scores,
                     **ev._ties(ranking, scores), **ev.profile_metrics(ranking, grades)})
    return rows


def paired_difference(rows_a, rows_b, n_resamples=DEFAULT_RESAMPLES, seed=DEFAULT_SEED):
    # Profile-level paired bootstrap of mean(B) minus mean(A); undefined profiles are skipped per metric
    out = {}
    rng = random.Random(seed)
    n = len(rows_a)
    picks = [[rng.randrange(n) for _ in range(n)] for _ in range(n_resamples)]
    for name in METRICS:
        pairs = [(a[name], b[name]) for a, b in zip(rows_a, rows_b)]
        diffs = [b - a for a, b in pairs if a is not None and b is not None]
        means = []
        for pick in picks:
            d = [pairs[i][1] - pairs[i][0] for i in pick if pairs[i][0] is not None and pairs[i][1] is not None]
            if d:
                means.append(sum(d) / len(d))
        means.sort()
        out[name] = {
            "mean_difference": sum(diffs) / len(diffs) if diffs else None,
            "ci_low": means[int(0.025 * len(means))] if means else None,
            "ci_high": means[min(len(means) - 1, int(0.975 * len(means)))] if means else None,
            "profiles_better": sum(1 for d in diffs if d > 0), "profiles_worse": sum(1 for d in diffs if d < 0),
            "profiles_unchanged": sum(1 for d in diffs if d == 0), "defined_profiles": len(diffs),
        }
    return out


def exposure(rows, catalog):
    category_of = {c.career_id: c.category for c in catalog.careers}
    slots = Counter(category_of[c] for r in rows for c in r["top5"])
    total = K * len(rows)
    shown = {c for r in rows for c in r["top5"]}
    return {
        "category_slot_share": {cat: ev._r(slots[cat] / total) for cat in CATEGORIES},
        "careers_ever_in_top5": len(shown),
        "profiles_with_tie_at_rank5_boundary": sum(1 for r in rows if r["tie_at_rank5_boundary"]),
        "profiles_with_tie_within_top5": sum(1 for r in rows if r["tie_within_top5"]),
    }


def _csv_text(rows, columns):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def build_outputs():
    if verify_frozen():
        raise SnapshotError("frozen eval64_v1 files were modified")
    if verify_snapshot():
        raise SnapshotError(f"the v1.4.0 snapshot was modified: {', '.join(verify_snapshot())}")
    old_catalog = load_catalog(EVAL64_DIR)
    new_catalog = load_catalog(SNAPSHOT_DIR)
    if new_catalog.interest_taxonomy != CURRENT_TAXONOMY:
        raise SnapshotError("the v1.4.0 snapshot does not use interest taxonomy 2.0")
    profiles, labels = load_eval64([c.career_id for c in old_catalog.careers])
    if {c.career_id for c in new_catalog.careers} != {c.career_id for c in old_catalog.careers}:
        raise SnapshotError("the two catalogues do not hold the same careers")

    migrated, records = {}, []
    for p in profiles:
        data, record = migrate_profile(p)
        migrated[p.profile_id] = data
        records.append(record)
    inputs = {
        "A_v130_original": (old_catalog, {p.profile_id: p.as_input() for p in profiles}),
        "A2_v130_retired_removed": (old_catalog, {p.profile_id: without_retired(p) for p in profiles}),
        "B_v140_migrated": (new_catalog, migrated),
    }
    rows = {name: run_condition(cat, data, profiles, labels) for name, (cat, data) in inputs.items()}
    stats = {name: profile_bootstrap(r, METRICS) for name, r in rows.items()}
    frozen = json.loads((ROOT / "reports" / "evaluation_64" / "evaluation_summary.json").read_text(encoding="utf-8"))
    reproduces = all(ev._r(stats["A_v130_original"][n]["mean"]) == frozen["overall"][n]["mean"] for n in METRICS)
    diff_b_a = paired_difference(rows["A_v130_original"], rows["B_v140_migrated"])
    diff_b_a2 = paired_difference(rows["A2_v130_retired_removed"], rows["B_v140_migrated"])
    diff_a2_a = paired_difference(rows["A_v130_original"], rows["A2_v130_retired_removed"])
    changed_top5 = sum(1 for a, b in zip(rows["A_v130_original"], rows["B_v140_migrated"]) if a["top5"] != b["top5"])

    comparison = []
    for n in METRICS:
        row = {"metric": n}
        for name in CONDITIONS:
            s = stats[name][n]
            row[f"{name}_mean"], row[f"{name}_ci_low"], row[f"{name}_ci_high"] = (
                ev._r(s["mean"]), ev._r(s["ci_low"]), ev._r(s["ci_high"]))
        for label, d in (("B_minus_A", diff_b_a), ("B_minus_A2", diff_b_a2), ("A2_minus_A", diff_a2_a)):
            row[f"{label}"] = ev._r(d[n]["mean_difference"])
            row[f"{label}_ci_low"], row[f"{label}_ci_high"] = ev._r(d[n]["ci_low"]), ev._r(d[n]["ci_high"])
        row["defined_profiles"] = stats["B_v140_migrated"][n]["defined_profiles"]
        comparison.append(row)

    exp = {name: exposure(rows[name], cat) for name, (cat, _) in inputs.items()}
    cat_ndcg = {name: {g["group"]: g["stats"]["ndcg_at_5"]["mean"] for g in ev.group_metrics(r, "primary_category", CATEGORIES)}
                for name, r in rows.items()}
    cat_rows = [{"category": c, "profiles": sum(1 for p in profiles if p.primary_category == c),
                 **{f"{name}_top5_slot_share": exp[name]["category_slot_share"][c] for name in CONDITIONS},
                 **{f"{name}_ndcg_at_5": ev._r(cat_ndcg[name].get(c)) for name in CONDITIONS}}
                for c in CATEGORIES]
    # New interests that no old interest name maps to: migrated profiles can never select them
    reachable = set(LEGACY_TO_CURRENT.values())
    unreachable = sorted(set(CURRENT_INTERESTS) - reachable)
    career_reach = Counter(sum(1 for i in c.interests if i in reachable) for c in new_catalog.careers)
    unreachable_by_category = {cat: sum(1 for c in new_catalog.careers if c.category == cat
                                        for i in c.interests if i not in reachable) for cat in CATEGORIES}
    before = Counter(r["interests_before"] for r in records)
    after = Counter(r["interests_after"] for r in records)
    summary = {
        "study_id": STUDY_ID,
        "status": "Owner-authorized implementation pending lecturer feedback. Separate from eval64_v1 and from the "
                  "original 50-career study; neither is changed.",
        "conditions": CONDITIONS,
        "data": {
            "profiles": len(profiles), "explicit_labels": sum(len(v) for v in labels.values()),
            "labels_source": "eval64_v1 (single author, no second review yet)",
            "snapshot_sha256": json.loads((SNAPSHOT_DIR / MANIFEST_FILE).read_text(encoding="utf-8"))["sha256"],
            "a_reproduces_frozen_eval64_v1": reproduces,
        },
        "profile_interest_migration": {
            "interests_before": sum(r["interests_before"] for r in records),
            "interests_after": sum(r["interests_after"] for r in records),
            "migrated": sum(r["migrated"] for r in records), "retired": sum(r["retired"] for r in records),
            "unknown": sum(r["unknown"] for r in records),
            "profiles_by_interest_count_before": {str(k): before[k] for k in sorted(before)},
            "profiles_by_interest_count_after": {str(k): after[k] for k in sorted(after)},
            "profiles_left_without_interests": sum(1 for r in records if r["interests_before"] and not r["interests_after"]),
            "retired_terms_seen": dict(sorted(Counter(
                i for p in profiles for i in p.interests if clean_skill_text(i) in RETIRED_LEGACY).items())),
        },
        "overall": {name: {n: {k: ev._r(v) if isinstance(v, float) else v for k, v in s[n].items()} for n in METRICS}
                    for name, s in stats.items()},
        "paired_differences": {
            label: {n: {k: ev._r(v) if isinstance(v, float) else v for k, v in d[n].items()} for n in METRICS}
            for label, d in (("B_minus_A", diff_b_a), ("B_minus_A2", diff_b_a2), ("A2_minus_A", diff_a2_a))},
        "exposure": exp,
        "migration_reachability": {
            "note": "Interests a migrated profile can hold. Careers whose interests are unreachable cannot earn "
                    "interest points from any migrated profile, which biases condition B against them.",
            "unreachable_new_interests": [label_for(k) for k in unreachable],
            "careers_by_reachable_interest_count": {str(k): career_reach[k] for k in sorted(career_reach)},
            "unreachable_career_interest_slots_by_category": unreachable_by_category,
        },
        "profiles_with_changed_top5_A_to_B": changed_top5,
        "configuration": {"k": K, "binary_threshold": ev.DEFAULT_THRESHOLD, "bootstrap": {
            "type": "profile-level percentile, paired for differences", "resamples": DEFAULT_RESAMPLES,
            "seed": DEFAULT_SEED}, "weights": {"required_skills": 0.55, "preferred_skills": 0.15,
                                                "interests": 0.25, "education": 0.05}},
        "limitations": [
            "Synthetic profiles and single-author labels; results describe agreement with those labels, not "
            "real-world recommendation accuracy.",
            "The eval64 profiles were written with the old 20-term vocabulary and were migrated mechanically; "
            "a learner choosing from the new 23 terms could choose differently.",
            "8 of the 23 new interests cannot be reached from any old interest name, so careers that carry them "
            "(for example law, money, community and equipment work) cannot gain interest points in condition B.",
            "Five old terms are retired rather than guessed, so migrated profiles lose 72 of 269 interests and "
            "10 profiles keep none.",
            "The labels were written while the author knew the v1.3.0 catalogue.",
            "Exploratory comparison designed after the taxonomy was chosen; not pre-registered.",
            "The interest taxonomy has not yet received lecturer approval.",
        ],
    }
    files = {
        SUMMARY_FILE: json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        COMPARISON_FILE: _csv_text(comparison, list(comparison[0])),
        CATEGORY_FILE: _csv_text(cat_rows, list(cat_rows[0])),
        MIGRATION_FILE: _csv_text(records, list(records[0])),
    }
    return files, summary


def write_outputs(out_dir):
    files, summary = build_outputs()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        if name == SUMMARY_FILE:
            data = json.loads(text)
            data["execution"] = ev.execution_block()
            text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        (out / name).write_text(text, encoding="utf-8")
    return summary


def check_outputs(saved_dir):
    files, _ = build_outputs()
    diffs = []
    for name, text in files.items():
        path = Path(saved_dir) / name
        if not path.exists():
            diffs.append(f"{name}: missing")
            continue
        saved = path.read_text(encoding="utf-8")
        if name == SUMMARY_FILE:
            a = json.loads(saved)
            a.pop("execution", None)
            if a != json.loads(text):
                diffs.append(f"{name}: differs")
        elif saved != text:
            diffs.append(f"{name}: differs")
    return diffs


def main(argv=None):
    parser = argparse.ArgumentParser(description="Evaluation of dataset v1.4.0 (interest taxonomy 2.0).")
    parser.add_argument("--freeze", action="store_true", help="copy the live v1.4.0 catalogue into the snapshot")
    parser.add_argument("--output", help="directory for the outputs, e.g. reports/evaluation_v1_4_0")
    parser.add_argument("--check", help="saved output directory to compare against")
    args = parser.parse_args(argv)
    if args.freeze:
        print(json.dumps(freeze()["sha256"], indent=2))
    if args.output:
        s = write_outputs(args.output)
        print(json.dumps({n: s["overall"][n]["ndcg_at_5"]["mean"] for n in CONDITIONS}, indent=2))
    if args.check:
        diffs = check_outputs(args.check)
        print("\n".join(diffs) if diffs else "All outputs reproduce exactly.")
        return 1 if diffs else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
