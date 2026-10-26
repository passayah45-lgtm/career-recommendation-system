# Baselines and ablations for the research study, run on the labelled synthetic profiles
# The production weights and the existing evaluation report are not changed by this module
# Run: python -m src.evaluation.research_experiments --output reports/research_results.json
# Check: python -m src.evaluation.research_experiments --check reports/research_results.json

import argparse
import json
import random
import sys
from pathlib import Path

from src.engine.scoring import DEFAULT_WEIGHTS, ScoringWeights
from src.evaluation import metrics as m
from src.evaluation.dataset import load_profiles
from src.services.catalog import load_catalog
from src.services.recommendations import recommend

K = 5
DECIMALS = 4
RANDOM_SEEDS = 100
TEST_RESAMPLES = 10000
REFERENCE = "S_full_system"

# Weight-based methods ranked by the engine, including its tie-break on required-skill coverage
WEIGHTED_METHODS = {
    "S_full_system": DEFAULT_WEIGHTS,
    "B1_skills_only": ScoringWeights(required_skills=0.55, preferred_skills=0.15, interests=0.0, education=0.0),
    "B3_skills_and_interests": ScoringWeights(required_skills=0.39, preferred_skills=0.11, interests=0.50, education=0.0),
    "AB_no_interests": ScoringWeights(required_skills=0.55, preferred_skills=0.15, interests=0.0, education=0.05),
    "AB_no_education": ScoringWeights(required_skills=0.55, preferred_skills=0.15, interests=0.25, education=0.0),
    "AB_no_preferred": ScoringWeights(required_skills=0.55, preferred_skills=0.0, interests=0.25, education=0.05),
    "W_required_heavy": ScoringWeights(required_skills=0.70, preferred_skills=0.10, interests=0.15, education=0.05),
    "W_strong_required": ScoringWeights(required_skills=0.75, preferred_skills=0.10, interests=0.10, education=0.05),
}
# Interests-only uses the engine score but breaks ties by career id, so no skill information leaks in
INTERESTS_ONLY = ScoringWeights(required_skills=0.0, preferred_skills=0.0, interests=1.0, education=0.0)
BASELINE_FAMILY = ("B1_skills_only", "B2_interests_only", "B3_skills_and_interests", "B5_random", "B6_popularity_loo")
ABLATION_FAMILY = ("AB_no_interests", "AB_no_education", "AB_no_preferred", "W_required_heavy", "W_strong_required")
METRICS = ("reciprocal_rank", "r_precision", "average_precision", "ndcg_at_5", "precision_at_5", "recall_at_5", "hit_at_5")
TESTED_METRICS = ("average_precision", "ndcg_at_5")


def _r(value):
    return None if value is None else round(value, DECIMALS)


def profile_metrics(ranking, relevant, k=K):
    return {
        "reciprocal_rank": m.reciprocal_rank(ranking, relevant),
        "r_precision": m.r_precision(ranking, relevant),
        "average_precision": m.average_precision(ranking, relevant),
        "ndcg_at_5": m.ndcg_at_k(ranking, relevant, k),
        "precision_at_5": m.precision_at_k(ranking, relevant, k),
        "recall_at_5": m.recall_at_k(ranking, relevant, k),
        "hit_at_5": m.hit_at_k(ranking, relevant, k),
    }


def engine_ranking(profile, catalog, weights):
    result = recommend(profile.as_input(), catalog, top_k=None, weights=weights)
    return [rec["career_id"] for rec in result["recommendations"]]


def interests_only_ranking(profile, catalog):
    result = recommend(profile.as_input(), catalog, top_k=None, weights=INTERESTS_ONLY)
    recs = sorted(result["recommendations"], key=lambda r: (-round(r["score"], 6), r["career_id"]))
    return [rec["career_id"] for rec in recs]


def popularity_ranking(profile, profiles, career_ids):
    # Leave-one-out: counts labels in the other profiles only, ties broken by career id
    counts = {cid: 0 for cid in career_ids}
    for other in profiles:
        if other.profile_id != profile.profile_id:
            for cid in other.relevant_career_ids:
                counts[cid] += 1
    return sorted(career_ids, key=lambda cid: (-counts[cid], cid))


def random_metrics(profile, career_ids):
    # Mean of each metric over seeded random permutations
    sums = {name: 0.0 for name in METRICS}
    defined = True
    for seed in range(RANDOM_SEEDS):
        order = list(career_ids)
        random.Random(seed).shuffle(order)
        values = profile_metrics(order, profile.relevant_career_ids)
        if values["average_precision"] is None:
            defined = False
            break
        for name in METRICS:
            sums[name] += values[name]
    if not defined:
        return {name: None for name in METRICS}
    return {name: sums[name] / RANDOM_SEEDS for name in METRICS}


def per_profile_rows(profiles, ranking_fn):
    rows = []
    for p in profiles:
        ranking = ranking_fn(p)
        values = profile_metrics(ranking, p.relevant_career_ids)
        rows.append({"profile_id": p.profile_id, "top_k": ranking[:K],
                     **{name: _r(values[name]) for name in METRICS}})
    return rows


def aggregate(rows):
    out = {}
    for name in METRICS:
        values = [row[name] for row in rows]
        mean, defined, _ = m.mean_defined(values)
        ci = m.bootstrap_ci(values)
        out[name] = {"mean": _r(mean), "ci95": None if ci is None else [_r(ci[0]), _r(ci[1])], "profiles": defined}
    return out


def significance(results, family):
    # Paired sign-flip tests against the full system, Holm-adjusted within the family and metric
    out = {}
    ref = results[REFERENCE]["per_profile"]
    for metric in TESTED_METRICS:
        tests = {}
        for name in family:
            other = results[name]["per_profile"]
            tests[name] = m.paired_randomization_test([r[metric] for r in ref], [r[metric] for r in other],
                                                     n_resamples=TEST_RESAMPLES)
        names = list(tests)
        adjusted = m.holm_adjust([tests[n]["p_value"] for n in names])
        out[metric] = {
            n: {"n": tests[n]["n"], "mean_difference_full_minus_method": _r(tests[n]["mean_difference"]),
                "nonzero_pairs": tests[n]["nonzero_pairs"], "p_value": _r(tests[n]["p_value"]),
                "p_holm": _r(adj), "significant_at_0_05": adj < 0.05}
            for n, adj in zip(names, adjusted)
        }
    return out


def run(catalog=None, profiles=None):
    catalog = catalog or load_catalog()
    career_ids = sorted(c.career_id for c in catalog.careers)
    profiles = profiles or load_profiles(career_ids)
    results = {}
    for name, weights in WEIGHTED_METHODS.items():
        rows = per_profile_rows(profiles, lambda p, w=weights: engine_ranking(p, catalog, w))
        results[name] = {"weights": weights.as_dict(), "aggregate": aggregate(rows), "per_profile": rows}
    rows = per_profile_rows(profiles, lambda p: interests_only_ranking(p, catalog))
    results["B2_interests_only"] = {"weights": INTERESTS_ONLY.as_dict(), "tie_break": "career_id",
                                    "aggregate": aggregate(rows), "per_profile": rows}
    rows = per_profile_rows(profiles, lambda p: popularity_ranking(p, profiles, career_ids))
    results["B6_popularity_loo"] = {"definition": "leave-one-out label counts, ties by career id",
                                    "aggregate": aggregate(rows), "per_profile": rows}
    rows = [{"profile_id": p.profile_id, **{k: _r(v) for k, v in random_metrics(p, career_ids).items()}}
            for p in profiles]
    results["B5_random"] = {"definition": f"mean over {RANDOM_SEEDS} seeded permutations",
                            "aggregate": aggregate(rows), "per_profile": rows}
    return {
        "note": ("Synthetic-profile study. Measures agreement with author-written reference labels. "
                 "Not real-world accuracy. Labels are binary, so NDCG@5 uses gain 1 per relevant career."),
        "k": K,
        "profiles": len(profiles),
        "reference_method": REFERENCE,
        "test": {"type": "paired sign-flip randomization, two-sided", "resamples": TEST_RESAMPLES, "seed": 42,
                 "correction": "Holm within family and metric", "metrics": list(TESTED_METRICS)},
        "methods": dict(sorted(results.items())),
        "significance": {"baselines": significance(results, BASELINE_FAMILY),
                         "ablations": significance(results, ABLATION_FAMILY)},
    }


def to_json(report):
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run research baselines and ablations on the labelled profiles.")
    parser.add_argument("--output", help="write the JSON report to this path")
    parser.add_argument("--check", help="exit 1 if this saved report differs from a fresh run")
    args = parser.parse_args(argv)
    text = to_json(run())
    if args.check:
        saved = Path(args.check).read_text(encoding="utf-8") if Path(args.check).exists() else ""
        if saved != text:
            print(f"Research results differ from {args.check}. Regenerate with --output.")
            return 1
        print(f"Research results match {args.check}.")
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
