# EXPLORATORY, POST-HOC sensitivity analysis for eval64_v1: tie-breaking and interest scoring
# Nothing here is deployed. Production scoring (src/engine/scoring.py) and ranking (src/engine/ranking.py) are
# only read; alternatives are re-implemented locally and checked to reproduce production exactly in the baseline case.
# Run: python -m src.evaluation.eval64_sensitivity --output reports/evaluation_64_sensitivity
# Check: python -m src.evaluation.eval64_sensitivity --check reports/evaluation_64_sensitivity

import argparse
import csv
import hashlib
import io
import json
import math
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

from src.engine.matching import match_career
from src.engine.scoring import DEFAULT_WEIGHTS, coverage, education_value
from src.evaluation import independent_64_evaluation as ev
from src.evaluation.bootstrap import profile_bootstrap
from src.evaluation.eval64_data import DEFAULT_THRESHOLD
from src.services.recommendations import profile_from_input

K = 5
DECIMALS = 4
PRECISION = 9
NEW_CAREERS = frozenset(f"C{i:03d}" for i in range(51, 65))
METRICS = ("precision_at_5", "recall_at_5", "average_precision", "ndcg_at_5")
RANDOM_RUNS = 200
RANDOM_BASE_SEED = 2026
FIXED_INTEREST_UNIT = 3
SUMMARY_FILE = "sensitivity_summary.json"
LABEL = "Exploratory, post-hoc sensitivity analysis. Not deployed; production formula and ranking unchanged."


def _r(value):
    return None if value is None else round(value, DECIMALS)


# ---------- Local scoring replica (baseline must equal production) ----------

def interest_value(match, profile, rule):
    matched = len(match.matched_interests)
    listed = len(match.career.interests)
    if rule == "current":
        return coverage(matched, listed)
    if rule == "none":
        return coverage(matched, listed)
    if rule == "fixed_unit":
        # Every matched interest is worth the same, whatever the career's list length (3 or 4 here)
        return None if listed == 0 else min(matched, FIXED_INTEREST_UNIT) / FIXED_INTEREST_UNIT
    if rule == "cosine":
        # Binary cosine similarity: neutral to the length of both the career's and the learner's interest lists
        n = len(profile.interests)
        return None if listed == 0 else (matched / math.sqrt(listed * n) if n else 0.0)
    raise ValueError(rule)


def score(match, profile, rule="current"):
    # Mirrors score_match(): applicable components share the weight, values 0 to 1, total 0 to 100
    w = DEFAULT_WEIGHTS.as_dict()
    if rule == "none":
        w["interests"] = 0.0
    sk, career = match.skills, match.career
    req = coverage(len(sk.matched_required), len(career.required_skills))
    values = {
        "required_skills": req,
        "preferred_skills": coverage(len(sk.matched_preferred), len(career.preferred_skills)),
        "interests": interest_value(match, profile, rule),
        "education": education_value(match),
    }
    applicable = sum(w[n] for n, v in values.items() if v is not None)
    total = sum((w[n] / applicable) * v * 100 for n, v in values.items() if v is not None and applicable > 0)
    return min(100.0, max(0.0, total)), (req or 0.0), len(sk.matched_required)


def _hash_key(profile_id, career_id):
    return hashlib.sha256(f"{profile_id}|{career_id}".encode("utf-8")).hexdigest()


def rank(profile_id, profile, catalog, rule="current", tie="career_id", rng=None):
    scored = []
    for career in catalog.careers:
        total, req, n_req = score(match_career(profile, career), profile, rule)
        if tie == "career_id":
            last = career.career_id
        elif tie == "hash":
            last = _hash_key(profile_id, career.career_id)
        elif tie == "random":
            last = rng.random()
        else:
            raise ValueError(tie)
        scored.append(((-round(total, PRECISION), -round(req, PRECISION), -n_req, last), career.career_id))
    scored.sort()
    return [cid for _, cid in scored]


# ---------- Comparison against the production ranking ----------

def _profiles(catalog, profiles):
    out = []
    for p in profiles:
        prof, _ = profile_from_input(p.as_input(), catalog)
        out.append((p, prof))
    return out


def compare(base, alt, labels, category_of):
    # base, alt: {profile_id: full ranking}
    changed_profiles = positions = entered = left = 0
    base_new = alt_new = 0
    cat_base, cat_alt = Counter(), Counter()
    for pid in base:
        b, a = base[pid][:K], alt[pid][:K]
        if set(b) != set(a):
            changed_profiles += 1
        positions += sum(1 for x, y in zip(b, a) if x != y)
        rel = {c for c, g in labels[pid].items() if g >= DEFAULT_THRESHOLD}
        entered += len((set(a) - set(b)) & rel)
        left += len((set(b) - set(a)) & rel)
        base_new += sum(1 for c in b if c in NEW_CAREERS)
        alt_new += sum(1 for c in a if c in NEW_CAREERS)
        cat_base.update(category_of[c] for c in b)
        cat_alt.update(category_of[c] for c in a)
    return {"profiles_with_top5_membership_change": changed_profiles, "top5_positions_changed": positions,
            "relevant_entering_top5": entered, "relevant_leaving_top5": left,
            "new_career_top5_slots_before": base_new, "new_career_top5_slots_after": alt_new,
            "category_slots_before": dict(cat_base), "category_slots_after": dict(cat_alt)}


def metric_rows(rankings, labels):
    return {pid: ev.profile_metrics(r, labels[pid]) for pid, r in rankings.items()}


def metric_summary(base_rows, alt_rows):
    # Means and a paired, profile-level bootstrap interval of the difference (alternative minus current)
    pids = list(base_rows)
    diffs = []
    for pid in pids:
        d = {}
        for name in METRICS:
            a, b = alt_rows[pid][name], base_rows[pid][name]
            d[name] = None if a is None or b is None else a - b
        diffs.append(d)
    boot = profile_bootstrap(diffs, METRICS)
    out = {}
    for name in METRICS:
        base_vals = [base_rows[p][name] for p in pids if base_rows[p][name] is not None]
        alt_vals = [alt_rows[p][name] for p in pids if alt_rows[p][name] is not None]
        out[name] = {"current": _r(statistics.mean(base_vals)), "alternative": _r(statistics.mean(alt_vals)),
                     "difference": _r(boot[name]["mean"]), "diff_ci_low": _r(boot[name]["ci_low"]),
                     "diff_ci_high": _r(boot[name]["ci_high"]), "profiles": boot[name]["defined_profiles"]}
    return out


def tie_break_experiment(catalog, prepared, labels, production):
    category_of = {c.career_id: c.category for c in catalog.careers}
    base = {p.profile_id: rank(p.profile_id, prof, catalog) for p, prof in prepared}
    if base != production:
        raise AssertionError("local replica does not reproduce the production ranking")
    base_rows = metric_rows(base, labels)
    hashed = {p.profile_id: rank(p.profile_id, prof, catalog, tie="hash") for p, prof in prepared}
    results = {"career_id_current": {"comparison": compare(base, base, labels, category_of),
                                     "metrics": metric_summary(base_rows, base_rows)},
               "hash_deterministic": {"comparison": compare(base, hashed, labels, category_of),
                                      "metrics": metric_summary(base_rows, metric_rows(hashed, labels))}}
    runs = []
    for i in range(RANDOM_RUNS):
        rng = random.Random(RANDOM_BASE_SEED + i)
        alt = {p.profile_id: rank(p.profile_id, prof, catalog, tie="random", rng=rng) for p, prof in prepared}
        comp = compare(base, alt, labels, category_of)
        rows = metric_rows(alt, labels)
        means = {n: statistics.mean(v[n] for v in rows.values() if v[n] is not None) for n in METRICS}
        runs.append({"run": i, "seed": RANDOM_BASE_SEED + i,
                     **{k: v for k, v in comp.items() if not k.startswith("category")},
                     "data_and_ai_top5_slots": comp["category_slots_after"].get("Data and AI", 0),
                     **{n: _r(means[n]) for n in METRICS}})
    summary = {}
    for key in ("profiles_with_top5_membership_change", "top5_positions_changed", "relevant_entering_top5",
                "relevant_leaving_top5", "new_career_top5_slots_after", "data_and_ai_top5_slots", *METRICS):
        values = sorted(r[key] for r in runs)
        summary[key] = {"mean": _r(statistics.mean(values)), "p2_5": values[int(0.025 * len(values))],
                        "p97_5": values[min(len(values) - 1, int(0.975 * len(values)))],
                        "min": values[0], "max": values[-1]}
    results["random_seeded"] = {"runs": RANDOM_RUNS, "base_seed": RANDOM_BASE_SEED, "summary": summary}
    return results, runs


def interest_experiment(catalog, prepared, labels, production):
    category_of = {c.career_id: c.category for c in catalog.careers}
    titles = {c.career_id: c.title for c in catalog.careers}
    rankings = {}
    for rule in ("current", "none", "fixed_unit", "cosine"):
        rankings[rule] = {p.profile_id: rank(p.profile_id, prof, catalog, rule=rule) for p, prof in prepared}
    if rankings["current"] != production:
        raise AssertionError("local replica does not reproduce the production ranking")
    base_rows = metric_rows(rankings["current"], labels)
    results, career_rows, category_rows = {}, [], []
    total_slots = K * len(prepared)
    for rule, ranks in rankings.items():
        results[rule] = {"comparison": compare(rankings["current"], ranks, labels, category_of),
                         "metrics": metric_summary(base_rows, metric_rows(ranks, labels))}
        slots = Counter(c for r in ranks.values() for c in r[:K])
        for cat in sorted(set(category_of.values())):
            category_rows.append({"rule": rule, "category": cat,
                                  "top5_slots": sum(n for c, n in slots.items() if category_of[c] == cat),
                                  "slot_share": _r(sum(n for c, n in slots.items() if category_of[c] == cat)
                                                   / total_slots)})
        for cid in sorted(category_of):
            relevant = [pid for pid in ranks if labels[pid].get(cid, 0) >= DEFAULT_THRESHOLD]
            career_rows.append({
                "rule": rule, "career_id": cid, "career_title": titles[cid], "category": category_of[cid],
                "top5_appearances": slots[cid],
                "relevant_top5": sum(1 for pid in relevant if cid in ranks[pid][:K]),
                "relevant_labels": len(relevant),
                "median_rank_when_relevant": (statistics.median(ranks[pid].index(cid) + 1 for pid in relevant)
                                              if relevant else None),
            })
    return results, category_rows, career_rows


def _csv_text(rows, columns):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    w.writeheader()
    for row in rows:
        w.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in columns})
    return buf.getvalue()


def _flat(results, experiment):
    rows = []
    for method, res in results.items():
        if "comparison" not in res:
            continue
        comp = res["comparison"]
        for name, m in res["metrics"].items():
            rows.append({"experiment": experiment, "method": method, "metric": name, **m,
                         **{k: v for k, v in comp.items() if not k.startswith("category")}})
    return rows


def build_outputs():
    catalog, profiles, labels = ev.load_frozen()
    production, _ = ev.run_profiles(catalog, profiles, labels)
    production = {r["profile_id"]: r["ranking"] for r in production}
    prepared = _profiles(catalog, profiles)
    tie, runs = tie_break_experiment(catalog, prepared, labels, production)
    interest, cat_rows, career_rows = interest_experiment(catalog, prepared, labels, production)
    flat_cols = ["experiment", "method", "metric", "current", "alternative", "difference", "diff_ci_low",
                 "diff_ci_high", "profiles", "profiles_with_top5_membership_change", "top5_positions_changed",
                 "relevant_entering_top5", "relevant_leaving_top5", "new_career_top5_slots_before",
                 "new_career_top5_slots_after"]
    files = {
        "tie_break_results.csv": _csv_text(_flat(tie, "tie_break"), flat_cols),
        "tie_break_random_runs.csv": _csv_text(runs, list(runs[0])),
        "interest_results.csv": _csv_text(_flat(interest, "interest_scoring"), flat_cols),
        "interest_category_exposure.csv": _csv_text(cat_rows, ["rule", "category", "top5_slots", "slot_share"]),
        "interest_career_exposure.csv": _csv_text(career_rows, list(career_rows[0])),
    }
    summary = {
        "label": LABEL, "study_id": ev.STUDY_ID, "profiles": len(profiles),
        "replica_reproduces_production": True,
        "tie_break": {"methods": {
            "career_id_current": "production: score, required coverage, matched required count, career id",
            "hash_deterministic": "same first three keys, then SHA-256 of 'profile_id|career_id'",
            "random_seeded": f"same first three keys, then a seeded random number; {RANDOM_RUNS} runs, seeds "
                             f"{RANDOM_BASE_SEED} to {RANDOM_BASE_SEED + RANDOM_RUNS - 1}"},
            "results": tie},
        "interest_scoring": {"rules": {
            "current": "matched interests / career's listed interests, weight 0.25",
            "none": "interest weight 0; other weights share the total as in production",
            "fixed_unit": f"min(matched, {FIXED_INTEREST_UNIT}) / {FIXED_INTEREST_UNIT}: each matched interest worth the same for every career",
            "cosine": "matched / sqrt(career interests x learner interests): neutral to both list lengths"},
            "tie_break": "production (career id) for every rule, to isolate the interest effect",
            "results": interest},
        "bootstrap": "paired, profile-level, 2,000 resamples, seed 64, on the per-profile difference",
    }
    files[SUMMARY_FILE] = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    return files


def main(argv=None):
    parser = argparse.ArgumentParser(description="Exploratory tie-break and interest-scoring sensitivity (eval64_v1).")
    parser.add_argument("--output")
    parser.add_argument("--check")
    args = parser.parse_args(argv)
    files = build_outputs()
    if args.check:
        d = Path(args.check)
        diffs = [n for n, t in files.items() if not (d / n).exists() or (d / n).read_text(encoding="utf-8") != t]
        print("Differences: " + ", ".join(diffs) if diffs else f"Sensitivity outputs match {d}.")
        return 1 if diffs else 0
    out = Path(args.output or "reports/evaluation_64_sensitivity")
    out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
