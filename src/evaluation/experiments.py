# Runs the labelled profiles through recommend() and compares weight configurations
# Run: python -m src.evaluation.experiments --output reports/evaluation_results.json
# Check that a saved report is still reproducible: python -m src.evaluation.experiments --check reports/evaluation_results.json

import argparse
import json
import sys
from pathlib import Path

from src.data.validation import CATEGORIES
from src.engine.scoring import DEFAULT_WEIGHTS, ScoringWeights
from src.evaluation import metrics as m
from src.evaluation.dataset import load_profiles
from src.services.catalog import load_catalog
from src.services.recommendations import recommend

K = 5
DECIMALS = 4
CONFIGURATIONS = {
    "A_baseline": DEFAULT_WEIGHTS,
    "B_required_heavy": ScoringWeights(required_skills=0.70, preferred_skills=0.10, interests=0.15, education=0.05),
    "C_strong_required": ScoringWeights(required_skills=0.75, preferred_skills=0.10, interests=0.10, education=0.05),
    # Ablation reference from the Phase 1 evaluation plan, not a production candidate
    "D_skills_only": ScoringWeights(required_skills=0.55, preferred_skills=0.15, interests=0.0, education=0.0),
}
BASELINE = "A_baseline"
METRIC_NAMES = (
    "precision_at_5", "attainable_precision_at_5", "recall_at_5", "f1_at_5", "hit_at_5",
    "reciprocal_rank", "r_precision", "average_precision",
)


def _r(value):
    return None if value is None else round(value, DECIMALS)


def full_ranking(profile, catalog, weights):
    result = recommend(profile.as_input(), catalog, top_k=None, weights=weights)
    return [rec["career_id"] for rec in result["recommendations"]], {
        rec["career_id"]: rec["score"] for rec in result["recommendations"]
    }


def evaluate_profile(profile, catalog, weights, k=K):
    ranking, scores = full_ranking(profile, catalog, weights)
    rel = profile.relevant_career_ids
    p = m.precision_at_k(ranking, rel, k)
    r = m.recall_at_k(ranking, rel, k)
    return {
        "profile_id": profile.profile_id,
        "primary_category": profile.primary_category,
        "profile_type": profile.profile_type,
        "relevant": list(rel),
        "top_k": ranking[:k],
        "top_k_scores": [scores[c] for c in ranking[:k]],
        "relevant_ranks": {c: ranking.index(c) + 1 for c in rel},
        "precision_at_5": _r(p),
        "attainable_precision_at_5": _r(m.attainable_precision_at_k(ranking, rel, k)),
        "recall_at_5": _r(r),
        "f1_at_5": _r(m.f1_score(p, r)),
        "hit_at_5": _r(m.hit_at_k(ranking, rel, k)),
        "reciprocal_rank": _r(m.reciprocal_rank(ranking, rel)),
        "r_precision": _r(m.r_precision(ranking, rel)),
        "average_precision": _r(m.average_precision(ranking, rel)),
    }


def aggregate(rows):
    out = {}
    for name in METRIC_NAMES:
        values = [row[name] for row in rows]
        mean, defined, undefined = m.mean_defined(values)
        ci = m.bootstrap_ci(values)
        out[name] = {
            "mean": _r(mean), "defined_profiles": defined, "undefined_profiles": undefined,
            "ci95": None if ci is None else [_r(ci[0]), _r(ci[1])],
        }
    return out


def evaluate_configuration(profiles, catalog, weights, k=K):
    rows = [evaluate_profile(p, catalog, weights, k) for p in profiles]
    category_of = {c.career_id: c.category for c in catalog.careers}
    top_lists = [row["top_k"] for row in rows]
    by_category = {}
    for cat in CATEGORIES:
        subset = [row for row in rows if row["primary_category"] == cat]
        if subset:
            by_category[cat] = {
                "profiles": len(subset),
                "f1_at_5": _r(m.mean_defined([row["f1_at_5"] for row in subset])[0]),
                "recall_at_5": _r(m.mean_defined([row["recall_at_5"] for row in subset])[0]),
                "reciprocal_rank": _r(m.mean_defined([row["reciprocal_rank"] for row in subset])[0]),
                "average_precision": _r(m.mean_defined([row["average_precision"] for row in subset])[0]),
            }
    distribution = m.category_distribution(top_lists, category_of)
    return {
        "weights": weights.as_dict(),
        "aggregate": aggregate(rows),
        "catalogue_coverage": _r(m.catalogue_coverage(top_lists, category_of)),
        "careers_recommended": len({c for lst in top_lists for c in lst}),
        "category_distribution": {c: {"count": v["count"], "share": _r(v["share"])} for c, v in distribution.items()},
        "by_primary_category": by_category,
        "per_profile": rows,
    }


def compare_to_baseline(results):
    # Per-profile wins, losses and ties on F1@5 and reciprocal rank, plus labelled-career rank changes
    base = {row["profile_id"]: row for row in results[BASELINE]["per_profile"]}
    comparison = {}
    for name, res in results.items():
        if name == BASELINE:
            continue
        summary = {metric: {"better": 0, "worse": 0, "same": 0}
                   for metric in ("f1_at_5", "reciprocal_rank", "r_precision", "average_precision")}
        changes = []
        for row in res["per_profile"]:
            b = base[row["profile_id"]]
            for metric in summary:
                if row[metric] is None or b[metric] is None:
                    continue
                key = "better" if row[metric] > b[metric] else "worse" if row[metric] < b[metric] else "same"
                summary[metric][key] += 1
            moved = {c: [b["relevant_ranks"][c], row["relevant_ranks"][c]] for c in row["relevant"]
                     if row["relevant_ranks"][c] != b["relevant_ranks"][c]}
            if moved or row["top_k"] != b["top_k"]:
                changes.append({"profile_id": row["profile_id"], "relevant_rank_changes": moved,
                                "baseline_top_k": b["top_k"], "top_k": row["top_k"]})
        comparison[name] = {"per_profile_vs_baseline": summary, "ranking_changes": changes}
    return comparison


def worked_example_check(results, profile_id="P21", career_id="C029"):
    # Tracks the Phase 3 concern: Financial Analyst rank for the worked-example skills
    out = {}
    for name, res in results.items():
        row = next(r for r in res["per_profile"] if r["profile_id"] == profile_id)
        ranking_top = row["top_k"]
        out[name] = {"top_k": ranking_top, "career_in_top_k": career_id in ranking_top,
                     "position": ranking_top.index(career_id) + 1 if career_id in ranking_top else None}
    return {"profile_id": profile_id, "career_id": career_id, "by_configuration": out}


def run(catalog=None, profiles=None):
    catalog = catalog or load_catalog()
    profiles = profiles or load_profiles([c.career_id for c in catalog.careers])
    results = {name: evaluate_configuration(profiles, catalog, w) for name, w in CONFIGURATIONS.items()}
    types = {}
    cats = {}
    for p in profiles:
        types[p.profile_type] = types.get(p.profile_type, 0) + 1
        cats[p.primary_category] = cats.get(p.primary_category, 0) + 1
    return {
        "note": "Synthetic-profile evaluation. Measures agreement with author-written reference labels, not real-world accuracy.",
        "k": K,
        "profiles": len(profiles),
        "profiles_by_category": dict(sorted(cats.items())),
        "profiles_by_type": dict(sorted(types.items())),
        "labelled_careers": len({c for p in profiles for c in p.relevant_career_ids}),
        "configurations": results,
        "comparison": compare_to_baseline(results),
        "worked_example_check": worked_example_check(results),
    }


def to_json(report):
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Evaluate recommendation quality on labelled synthetic profiles.")
    parser.add_argument("--output", help="write the JSON report to this path")
    parser.add_argument("--check", help="exit 1 if this saved report differs from a fresh run")
    args = parser.parse_args(argv)
    text = to_json(run())
    if args.check:
        saved = Path(args.check).read_text(encoding="utf-8") if Path(args.check).exists() else ""
        if saved != text:
            print(f"Evaluation results differ from {args.check}. Regenerate with --output.")
            return 1
        print(f"Evaluation results match {args.check}.")
        return 0
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
