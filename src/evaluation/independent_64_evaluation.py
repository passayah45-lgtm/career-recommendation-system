# Independent evaluation of the 64-career catalogue (eval64_v1) with frozen profiles and graded labels
# The production formula is used unchanged; the original 50-career study and its reports are never touched
# Run: python -m src.evaluation.independent_64_evaluation --output reports/evaluation_64
# Check that saved outputs are reproducible: python -m src.evaluation.independent_64_evaluation --check reports/evaluation_64

import argparse
import csv
import io
import json
import platform
import statistics
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import date
from importlib import metadata
from pathlib import Path

from src.data.validation import CATEGORIES, DEFAULT_DATA_DIR
from src.engine.scoring import DEFAULT_WEIGHTS
from src.evaluation import metrics as m
from src.evaluation import eval64_diagnostics as diag
from src.evaluation.bootstrap import DEFAULT_RESAMPLES, DEFAULT_SEED, profile_bootstrap
from src.evaluation.eval64_data import (
    CATALOG_FILES, DEFAULT_THRESHOLD, EVAL64_DIR, Eval64DataError, load_eval64, read_manifest, relevant_set,
    sha256_of, verify_frozen,
)
from src.services.catalog import load_catalog
from src.services.recommendations import profile_from_input, recommend

ROOT = Path(__file__).resolve().parents[2]
STUDY_ID = "eval64_v1"
K = 5
DECIMALS = 4
NEW_CAREERS = tuple(f"C{i:03d}" for i in range(51, 65))
METRICS = ("precision_at_1", "precision_at_3", "precision_at_5", "recall_at_5", "f1_at_5", "hit_at_5",
           "reciprocal_rank", "average_precision", "ndcg_at_5")
BINARY_METRICS = tuple(n for n in METRICS if n != "ndcg_at_5")
SENSITIVITY_THRESHOLDS = (1, 3)
ORIGINAL_REPORT = ROOT / "reports" / "evaluation_results.json"
# French aliases added in dataset v1.3.0, used by robustness condition 5
FRENCH_ALIASES = ("géologie", "mécanique des sols", "mécanique des roches", "méthodes géophysiques",
                  "droit des contrats", "droit constitutionnel", "droit administratif", "droit ohada",
                  "finances publiques", "économie", "sociologie", "gestion des conflits")
UNKNOWN_SKILLS = ("underwater basket weaving", "quantum origami")
COMMON_SKILLS = ("communication", "excel", "project management", "git", "technical writing", "python",
                  "sql", "statistics", "research methods", "data visualization")
# Condition 10: interests from a distant field, chosen by category
CONFLICTING_INTERESTS = {
    "Data and AI": ("visual arts", "helping people"), "Software": ("healthcare", "visual arts"),
    "Cybersecurity": ("visual arts", "teaching"), "Design": ("mathematics", "security"),
    "Business": ("science", "visual arts"), "Education": ("security", "engineering"),
    "Healthcare": ("building software", "business"), "Engineering": ("teaching", "healthcare"),
    "Law": ("engineering", "science"), "Social Sciences": ("building software", "engineering"),
}
SUMMARY_FILE = "evaluation_summary.json"
OUTPUT_FILES = ("overall_metrics.csv", "confidence_intervals.csv", "category_metrics.csv", "profile_type_metrics.csv",
                "career_coverage.csv", "profile_results.csv", "ranking_rows.csv", "robustness_results.csv",
                "threshold_sensitivity.csv", "bias_analysis.csv", SUMMARY_FILE)


def _r(value):
    return None if value is None else round(value, DECIMALS)


def load_frozen():
    # Refuses to run on a modified freeze
    changed = verify_frozen()
    if changed:
        raise Eval64DataError(f"Frozen eval64 files were modified: {', '.join(changed)}")
    catalog = load_catalog(EVAL64_DIR)
    profiles, labels = load_eval64([c.career_id for c in catalog.careers])
    return catalog, profiles, labels


def rank(profile_input, catalog):
    result = recommend(profile_input, catalog, top_k=None, weights=DEFAULT_WEIGHTS)["recommendations"]
    return [r["career_id"] for r in result], {r["career_id"]: r["score"] for r in result}


def profile_metrics(ranking, grades, threshold=DEFAULT_THRESHOLD):
    rel = relevant_set(grades, threshold)
    p5, r5 = m.precision_at_k(ranking, rel, 5), m.recall_at_k(ranking, rel, 5)
    return {
        "precision_at_1": m.precision_at_k(ranking, rel, 1),
        "precision_at_3": m.precision_at_k(ranking, rel, 3),
        "precision_at_5": p5,
        "recall_at_5": r5,
        "f1_at_5": m.f1_score(p5, r5),
        "hit_at_5": m.hit_at_k(ranking, rel, 5),
        "reciprocal_rank": m.reciprocal_rank(ranking, rel),
        "average_precision": m.average_precision(ranking, rel),
        "ndcg_at_5": m.ndcg_at_k(ranking, rel, 5, grades={c: g for c, g in grades.items() if g > 0}),
    }


def _ties(ranking, scores):
    top = [scores[c] for c in ranking[:K]]
    boundary = scores[ranking[K - 1]] == scores[ranking[K]]
    return {"tie_within_top5": len(set(top)) < len(top), "tie_at_rank5_boundary": boundary,
            "tied_at_rank5": sum(1 for c in ranking if scores[c] == scores[ranking[K - 1]])}


def run_profiles(catalog, profiles, labels):
    rows, ranking_rows = [], []
    for p in profiles:
        ranking, scores = rank(p.as_input(), catalog)
        grades = labels[p.profile_id]
        _, report = profile_from_input(p.as_input(), catalog)
        met = profile_metrics(ranking, grades)
        rel = relevant_set(grades)
        row = {
            "profile_id": p.profile_id, "primary_category": p.primary_category, "profile_type": p.profile_type,
            "learner_stage": p.learner_stage, "education_level": p.education_level,
            "skills_entered": len(p.skills), "unknown_skills": len(report.unknown_skills),
            "relevant_count": len(rel), "grade3_count": sum(1 for g in grades.values() if g == 3),
            "top5": ranking[:K], "top5_scores": [scores[c] for c in ranking[:K]],
            "relevant_ranks": {c: ranking.index(c) + 1 for c in sorted(rel)},
            "grades": grades, "ranking": ranking, "scores": scores,
            **_ties(ranking, scores), **met,
        }
        rows.append(row)
        for position, cid in enumerate(ranking, start=1):
            ranking_rows.append({"profile_id": p.profile_id, "rank": position, "career_id": cid,
                                 "score": scores[cid], "grade": grades.get(cid, 0)})
    return rows, ranking_rows


def aggregate(rows, n_resamples=DEFAULT_RESAMPLES, seed=DEFAULT_SEED):
    return profile_bootstrap(rows, METRICS, n_resamples, seed)


def group_metrics(rows, key, order):
    out = []
    for value in order:
        group = [r for r in rows if r[key] == value]
        if not group:
            continue
        stats = profile_bootstrap(group, METRICS)
        out.append({"group": value, "profiles": len(group), "stats": stats})
    return out


def career_coverage(rows, catalog):
    top5_count, top1_count, relevant_count, hits, grade3 = Counter(), Counter(), Counter(), Counter(), Counter()
    ranks = defaultdict(list)
    for r in rows:
        for c in r["top5"]:
            top5_count[c] += 1
        top1_count[r["top5"][0]] += 1
        for c, g in r["grades"].items():
            if g == 3:
                grade3[c] += 1
            if g >= DEFAULT_THRESHOLD:
                relevant_count[c] += 1
                position = r["ranking"].index(c) + 1
                ranks[c].append(position)
                if position <= K:
                    hits[c] += 1
    shared = skill_overlap(catalog)
    out = []
    for c in catalog.careers:
        cid = c.career_id
        n_rel = relevant_count[cid]
        out.append({
            "career_id": cid, "career_title": c.title, "category": c.category,
            "added_in_v1_3_0": cid in NEW_CAREERS, "education_level": c.education_level,
            "relevant_labels": n_rel, "grade3_labels": grade3[cid],
            "top5_appearances": top5_count[cid], "top1_appearances": top1_count[cid],
            "relevant_found_in_top5": hits[cid],
            "career_recall_at_5": _r(hits[cid] / n_rel) if n_rel else None,
            "median_rank_when_relevant": statistics.median(ranks[cid]) if ranks[cid] else None,
            "never_in_top5": top5_count[cid] == 0,
            "careers_sharing_a_skill": shared[cid],
            "sample_note": "too few labels for a per-career conclusion" if n_rel < 3 else "",
        })
    return out


def skill_overlap(catalog):
    # Number of other careers that share at least one required or preferred skill
    skills = {c.career_id: set(c.required_skills + c.preferred_skills) for c in catalog.careers}
    return {a: sum(1 for b in skills if b != a and skills[a] & skills[b]) for a in skills}


def _avg_ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for t in range(i, j + 1):
            ranks[order[t]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def spearman(x, y):
    # Spearman rank correlation with average ranks for ties; descriptive only
    if len(x) < 3:
        return None
    rx, ry = _avg_ranks(x), _avg_ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx) ** 0.5
    vy = sum((b - my) ** 2 for b in ry) ** 0.5
    return None if vx == 0 or vy == 0 else cov / (vx * vy)


def bias_analysis(rows, coverage, catalog):
    level = {c.career_id: c.education_level for c in catalog.careers}
    out = []

    # Skill overlap against exposure: do careers that share skills with many others reach more top-5 lists?
    out.append({"analysis": "overlap_vs_top5_appearances", "group": "all 64 careers", "n": len(coverage),
                "value": _r(spearman([c["careers_sharing_a_skill"] for c in coverage],
                                     [c["top5_appearances"] for c in coverage])),
                "unit": "Spearman rho", "note": "Descriptive; no significance test"})
    labelled = [c for c in coverage if c["relevant_labels"]]
    out.append({"analysis": "overlap_vs_top5_appearances_minus_relevant", "group": "careers with labels",
                "n": len(labelled),
                "value": _r(spearman([c["careers_sharing_a_skill"] for c in labelled],
                                     [c["top5_appearances"] - c["relevant_labels"] for c in labelled])),
                "unit": "Spearman rho", "note": "Exposure beyond the number of profiles that need the career"})

    # Education: relevant careers whose entry level is above the learner's level
    below, meets = [], []
    for r in rows:
        if r["education_level"] is None:
            continue
        for c, position in r["relevant_ranks"].items():
            (below if level[c] > r["education_level"] else meets).append(position)
    for name, values in (("learner_below_career_level", below), ("learner_meets_career_level", meets)):
        out.append({"analysis": "education_rank_of_relevant", "group": name, "n": len(values),
                    "value": _r(statistics.mean(values)) if values else None, "unit": "mean rank",
                    "note": "Relevant pairs with known learner education"})
        out.append({"analysis": "education_top5_rate_of_relevant", "group": name, "n": len(values),
                    "value": _r(sum(1 for v in values if v <= K) / len(values)) if values else None,
                    "unit": "share in top 5", "note": ""})

    # New careers against original careers: share of relevant pairs found in the top 5
    for name, ids in (("added_in_v1_3_0", set(NEW_CAREERS)), ("original_50", None)):
        pairs = [(r, c) for r in rows for c in r["relevant_ranks"]
                 if (c in ids if ids is not None else c not in NEW_CAREERS)]
        found = sum(1 for r, c in pairs if r["relevant_ranks"][c] <= K)
        out.append({"analysis": "relevant_pairs_found_in_top5", "group": name, "n": len(pairs),
                    "value": _r(found / len(pairs)) if pairs else None, "unit": "share in top 5", "note": ""})

    # Vocabulary: unrecognised share of skill entries (denominator: entries typed, see vocabulary_analysis.csv)
    for name, types in (("all profiles", None), ("french_vocabulary", {"french_vocabulary"}),
                        ("unfamiliar_vocabulary", {"unfamiliar_vocabulary"})):
        group = [r for r in rows if types is None or r["profile_type"] in types]
        entered = sum(r["skills_entered"] for r in group)
        out.append({"analysis": "unrecognised_skill_share", "group": name, "n": entered,
                    "value": _r(sum(r["unknown_skills"] for r in group) / entered) if entered else None,
                    "unit": "unrecognised skill entries / skill entries typed",
                    "note": f"{len(group)} profiles"})
        hits = [r["hit_at_5"] for r in group if r["hit_at_5"] is not None]
        out.append({"analysis": "hit_at_5_by_vocabulary", "group": name, "n": len(hits),
                    "value": _r(sum(hits) / len(hits)) if hits else None, "unit": "Hit@5", "note": "defined profiles"})

    # Ties
    out.append({"analysis": "ties", "group": "tie at the rank 5 boundary", "n": len(rows),
                "value": sum(1 for r in rows if r["tie_at_rank5_boundary"]), "unit": "profiles",
                "note": "Display scores (one decimal); engine-precision analysis in tie_summary.csv"})
    out.append({"analysis": "ties", "group": "tie inside the top 5", "n": len(rows),
                "value": sum(1 for r in rows if r["tie_within_top5"]), "unit": "profiles", "note": ""})
    return out


def _jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 1.0


def _variants(p, catalog):
    # Yields (condition, input or None when the condition does not apply to this profile)
    base = p.as_input()
    reverse_fr = {}
    for alias in FRENCH_ALIASES:
        target = catalog.aliases.get(alias)
        if target:
            reverse_fr.setdefault(target, alias)
    skills = list(p.skills)
    yield "1_missing_skills", ({**base, "skills": skills[::2]} if len(skills) >= 2 else None)
    yield "2_interests_only", ({**base, "skills": []} if skills and p.interests else None)
    yield "3_education_removed", ({k: v for k, v in base.items() if k != "education_level"}
                                  if p.education_level is not None else None)
    yield "4_unknown_skills_added", ({**base, "skills": skills + list(UNKNOWN_SKILLS)} if skills else None)
    lowered = [s.lower() for s in skills]
    swapped = [reverse_fr.get(s, s) for s in lowered]
    yield "5_french_aliases", ({**base, "skills": swapped} if swapped != lowered else None)
    yield "6_mixed_case", ({**base, "skills": [s.upper() if i % 2 else s.title() for i, s in enumerate(skills)]}
                           if skills else None)
    yield "8_very_few_inputs", ({**base, "skills": skills[:1], "interests": list(p.interests[:1])}
                                if len(skills) + len(p.interests) > 2 else None)
    extra = [g for g in COMMON_SKILLS if g not in lowered]
    yield "9_many_inputs", ({**base, "skills": skills + extra} if extra else None)
    yield "10_conflicting_interests", ({**base, "interests": list(CONFLICTING_INTERESTS[p.primary_category])}
                                       if p.interests else None)


def robustness(catalog, profiles, labels, rows):
    by_id = {r["profile_id"]: r for r in rows}
    results = defaultdict(list)
    for p in profiles:
        original = by_id[p.profile_id]
        grade3 = [c for c, g in labels[p.profile_id].items() if g == 3]
        for condition, data in _variants(p, catalog):
            if data is None:
                continue
            ranking, scores = rank(data, catalog)
            results[condition].append({
                "jaccard": _jaccard(original["top5"], ranking[:K]),
                "top1_same": original["top5"][0] == ranking[0],
                "rank_change": [ranking.index(c) - original["ranking"].index(c) for c in grade3],
                "ndcg_before": original["ndcg_at_5"],
                "ndcg_after": profile_metrics(ranking, labels[p.profile_id])["ndcg_at_5"],
                "top1_score_change": scores[ranking[0]] - original["scores"][original["top5"][0]],
            })
    out = []
    for condition in sorted(results, key=lambda c: int(c.split("_")[0])):
        res = results[condition]
        changes = [d for r in res for d in r["rank_change"]]
        before = [r["ndcg_before"] for r in res if r["ndcg_before"] is not None]
        after = [r["ndcg_after"] for r in res if r["ndcg_after"] is not None]
        out.append({
            "condition": condition, "profiles": len(res),
            "mean_top5_jaccard": _r(statistics.mean(r["jaccard"] for r in res)),
            "top1_unchanged_share": _r(sum(r["top1_same"] for r in res) / len(res)),
            "grade3_pairs": len(changes),
            "mean_grade3_rank_change": _r(statistics.mean(changes)) if changes else None,
            "mean_ndcg_at_5_before": _r(statistics.mean(before)) if before else None,
            "mean_ndcg_at_5_after": _r(statistics.mean(after)) if after else None,
            "mean_top1_score_change": _r(statistics.mean(r["top1_score_change"] for r in res)),
        })
    # Condition 7 uses the labelled transferable-skill and career-change profiles as they are
    group = [r for r in rows if r["profile_type"] in ("transferable_skills", "career_change")]
    ndcg = [r["ndcg_at_5"] for r in group if r["ndcg_at_5"] is not None]
    out.insert(6, {
        "condition": "7_transferable_skills", "profiles": len(group), "mean_top5_jaccard": None,
        "top1_unchanged_share": None, "grade3_pairs": sum(r["grade3_count"] for r in group),
        "mean_grade3_rank_change": None, "mean_ndcg_at_5_before": None,
        "mean_ndcg_at_5_after": _r(statistics.mean(ndcg)) if ndcg else None, "mean_top1_score_change": None,
    })
    return out


def threshold_sensitivity(rows):
    out = []
    for threshold in (DEFAULT_THRESHOLD,) + SENSITIVITY_THRESHOLDS:
        per = [profile_metrics(r["ranking"], r["grades"], threshold) for r in rows]
        for name in ("precision_at_5", "recall_at_5", "hit_at_5", "reciprocal_rank", "average_precision"):
            values = [x[name] for x in per if x[name] is not None]
            out.append({"threshold": f"grade >= {threshold}", "metric": name,
                        "mean": _r(statistics.mean(values)) if values else None,
                        "defined_profiles": len(values), "excluded_profiles": len(per) - len(values)})
    return out


def engine_checks(catalog, rows):
    empty = recommend({}, catalog, top_k=None)["recommendations"]
    unknown = recommend({"skills": list(UNKNOWN_SKILLS)}, catalog, top_k=None)["recommendations"]
    trio = {"C051", "C052", "C055"}
    return {
        "every_career_ranked_for_every_profile": all(len(r["ranking"]) == len(catalog.careers) for r in rows),
        "careers_in_catalogue": len(catalog.careers),
        "max_score_empty_profile": max(r["score"] for r in empty),
        "max_score_unknown_skills_only": max(r["score"] for r in unknown),
        "earth_science_trio_separate_records": len(trio & {c.career_id for c in catalog.careers}) == 3,
        "duplicate_titles": len(catalog.careers) - len({c.title for c in catalog.careers}),
    }


def original_study():
    # Headline values read from the saved original report; nothing is recomputed or rewritten
    data = json.loads(ORIGINAL_REPORT.read_text(encoding="utf-8"))
    agg = data["configurations"]["A_baseline"]["aggregate"]
    return {
        "report": "reports/evaluation_results.json", "careers": 50, "profiles": data["profiles"],
        "labelled_careers": data["labelled_careers"], "label_type": "binary, at most 3 relevant per profile",
        "metrics": {name: {"mean": agg[name]["mean"], "ci95": agg[name]["ci95"],
                           "defined_profiles": agg[name]["defined_profiles"]}
                    for name in ("precision_at_5", "recall_at_5", "f1_at_5", "hit_at_5", "reciprocal_rank",
                                 "average_precision")},
    }


def _package_versions():
    names = ("scikit-learn", "numpy", "pandas", "streamlit", "matplotlib")
    out = {}
    for name in names:
        try:
            out[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            out[name] = None
    return out


def _csv_text(rows, columns):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    w.writeheader()
    for row in rows:
        w.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in columns})
    return buf.getvalue()


def _stats_rows(label, stats, extra=None):
    return [{**(extra or {}), "scope": label, "metric": name, "mean": _r(s["mean"]), "ci_low": _r(s["ci_low"]),
             "ci_high": _r(s["ci_high"]), "defined_profiles": s["defined_profiles"],
             "excluded_profiles": s["undefined_profiles"], "resamples": s["resamples"]}
            for name, s in stats.items()]


def build_outputs(catalog, profiles, labels, manifest):
    rows, ranking_rows = run_profiles(catalog, profiles, labels)
    overall = aggregate(rows)
    by_cat = group_metrics(rows, "primary_category", CATEGORIES)
    coverage = career_coverage(rows, catalog)
    bias = bias_analysis(rows, coverage, catalog)
    robust = robustness(catalog, profiles, labels, rows)
    sens = threshold_sensitivity(rows)
    checks = engine_checks(catalog, rows)
    category_of = {c.career_id: c.category for c in catalog.careers}
    top5_lists = [r["top5"] for r in rows]
    shown = {c for lst in top5_lists for c in lst}
    no_relevant = [r["profile_id"] for r in rows if r["relevant_count"] == 0]
    top1 = [r["top5_scores"][0] for r in rows]
    top5_all = [s for r in rows for s in r["top5_scores"]]
    relevant_positions = [pos for r in rows for pos in r["relevant_ranks"].values()]

    files = {}
    files["overall_metrics.csv"] = _csv_text(_stats_rows("all profiles", overall),
                                             ["scope", "metric", "mean", "ci_low", "ci_high", "defined_profiles",
                                              "excluded_profiles", "resamples"])
    ci_rows = _stats_rows("all profiles", overall)
    for g in by_cat:
        ci_rows += _stats_rows(f"category: {g['group']}", g["stats"])
    files["confidence_intervals.csv"] = _csv_text(ci_rows, ["scope", "metric", "mean", "ci_low", "ci_high",
                                                            "defined_profiles", "excluded_profiles", "resamples"])
    cat_rows = []
    slots = Counter(category_of[c] for lst in top5_lists for c in lst)
    for g in by_cat:
        row = {"category": g["group"], "profiles": g["profiles"],
               "excluded_no_relevant": g["stats"]["precision_at_5"]["undefined_profiles"],
               "careers_in_category": sum(1 for c in catalog.careers if c.category == g["group"]),
               "top5_slots": slots[g["group"]],
               "top5_slot_share": _r(slots[g["group"]] / (K * len(rows)))}
        row.update({name: _r(g["stats"][name]["mean"]) for name in METRICS})
        cat_rows.append(row)
    files["category_metrics.csv"] = _csv_text(cat_rows, ["category", "profiles", "excluded_no_relevant",
                                                         "careers_in_category", "top5_slots", "top5_slot_share",
                                                         *METRICS])
    files["career_coverage.csv"] = _csv_text(coverage, list(coverage[0]))
    prof_cols = ["profile_id", "primary_category", "profile_type", "learner_stage", "education_level",
                 "skills_entered", "unknown_skills", "relevant_count", "grade3_count", "top5", "top5_scores",
                 "relevant_ranks", "tie_within_top5", "tie_at_rank5_boundary", *METRICS]
    prof_rows = []
    for r in rows:
        out = {k: r[k] for k in prof_cols}
        out["top5"] = "|".join(r["top5"])
        out["top5_scores"] = "|".join(f"{s:.1f}" for s in r["top5_scores"])
        out["relevant_ranks"] = "|".join(f"{c}:{p}" for c, p in r["relevant_ranks"].items())
        out.update({name: _r(r[name]) for name in METRICS})
        prof_rows.append(out)
    files["profile_results.csv"] = _csv_text(prof_rows, prof_cols)
    files["ranking_rows.csv"] = _csv_text(ranking_rows, ["profile_id", "rank", "career_id", "score", "grade"])
    files["robustness_results.csv"] = _csv_text(robust, list(robust[0]))
    files["threshold_sensitivity.csv"] = _csv_text(sens, list(sens[0]))
    files["bias_analysis.csv"] = _csv_text(bias, ["analysis", "group", "n", "value", "unit", "note"])

    vocab, zero, terms = diag.vocabulary_analysis(catalog, profiles)
    files["vocabulary_analysis.csv"] = _csv_text(vocab, list(vocab[0]))
    files["vocabulary_zero_recognised.csv"] = _csv_text(zero, ["profile_id", "profile_type", "primary_category",
                                                               "skill_entries", "skills"])
    files["vocabulary_unrecognised_terms.csv"] = _csv_text(terms, ["term", "profiles"])
    type_table = diag.profile_type_table(rows)
    files["profile_type_metrics.csv"] = _csv_text(type_table, list(type_table[0]))
    exp_cat, exp_career, examples, interest_freq, drivers = diag.exposure_analysis(catalog, profiles, labels)
    tie_summary, tie_profiles, tie_groups = diag.tie_analysis(catalog, profiles, labels)
    won_on_id = Counter(c for g in tie_groups for c in g["careers_in_top5"].split("|") if c)
    for row in exp_career:
        row["top5_appearances_won_on_career_id"] = won_on_id[row["career_id"]]
    files["exposure_by_category.csv"] = _csv_text(exp_cat, list(exp_cat[0]))
    files["exposure_by_career.csv"] = _csv_text(exp_career, list(exp_career[0]))
    files["exposure_examples_C004.csv"] = _csv_text(examples, list(examples[0]))
    files["exposure_interest_frequency.csv"] = _csv_text(interest_freq, ["interest", "profiles"])
    files["exposure_slot_drivers.csv"] = _csv_text(drivers, ["driver", "slots", "share"])
    files["tie_summary.csv"] = _csv_text(tie_summary, ["measure", "value"])
    files["tie_profiles.csv"] = _csv_text(tie_profiles, list(tie_profiles[0]))
    files["tie_groups_crossing_rank5.csv"] = _csv_text(tie_groups, list(tie_groups[0]))

    summary = {
        "study_id": STUDY_ID,
        "note": ("Synthetic profiles with single-author graded labels written before any engine run. Measures "
                 "agreement with those labels, not real-world accuracy, employment outcomes or suitability for "
                 "regulated professions. Separate from the original 50-career study."),
        "configuration": {
            "weights": {"required_skills": DEFAULT_WEIGHTS.required_skills,
                        "preferred_skills": DEFAULT_WEIGHTS.preferred_skills,
                        "interests": DEFAULT_WEIGHTS.interests, "education": DEFAULT_WEIGHTS.education},
            "k": K, "binary_threshold": DEFAULT_THRESHOLD, "sensitivity_thresholds": list(SENSITIVITY_THRESHOLDS),
            "bootstrap": {"type": "profile-level percentile", "resamples": DEFAULT_RESAMPLES, "seed": DEFAULT_SEED,
                          "confidence": 0.95},
            "ndcg_gain": "grade (0 to 3), log2(rank + 1) discount, ideal from the profile's labels",
            "unlisted_pairs": "grade 0 (rule R8)",
        },
        "data": {
            "dataset_version": manifest["dataset_version"], "careers": len(catalog.careers),
            "categories": len({c.category for c in catalog.careers}), "profiles": len(profiles),
            "explicit_labels": sum(len(v) for v in labels.values()),
            "labels_by_grade": {str(g): sum(1 for v in labels.values() for x in v.values() if x == g)
                                for g in (0, 1, 2, 3)},
            "labeller": manifest["labeller"], "second_reviewer": manifest["second_reviewer"],
            "inter_rater_agreement": None,
            "sha256": manifest["sha256"],
            "frozen_files_verified": True,
            "live_catalogue_matches_frozen": all(
                sha256_of(DEFAULT_DATA_DIR / n) == manifest["sha256"][n] for n in CATALOG_FILES),
        },
        "exclusions": {"count": len(no_relevant),
                       "profile_ids": "withheld until the second review; listed in profile_results.csv",
                       "effect": "Excluded from binary metrics only; included in NDCG@5 and coverage"},
        "overall": {name: {k: _r(v) if isinstance(v, float) else v for k, v in s.items()}
                    for name, s in overall.items()},
        "coverage": {
            "careers_with_relevant_label": sum(1 for c in coverage if c["relevant_labels"]),
            "categories_with_relevant_label": len({c["category"] for c in coverage if c["relevant_labels"]}),
            "careers_in_any_top5": len(shown), "careers_never_in_top5": len(catalog.careers) - len(shown),
            "careers_never_in_top5_ids": sorted(set(category_of) - shown),
            "top5_career_coverage": _r(len(shown) / len(catalog.careers)),
            "categories_in_any_top5": len({category_of[c] for c in shown}),
            "profiles_with_relevant_in_top5_share": _r(overall["hit_at_5"]["mean"]),
        },
        "scores": {
            "top1_mean": _r(statistics.mean(top1)), "top1_median": _r(statistics.median(top1)),
            "top5_mean": _r(statistics.mean(top5_all)), "top5_median": _r(statistics.median(top5_all)),
            "relevant_rank_median": statistics.median(relevant_positions),
            "relevant_in_top5_share": _r(sum(1 for x in relevant_positions if x <= K) / len(relevant_positions)),
            "relevant_pairs": len(relevant_positions),
        },
        "engine_checks": checks,
        "original_study": original_study(),
        "comparison_note": ("Separate studies with different profiles, labelling procedures, label granularity and "
                            "catalogue size. Differences are not evidence that the expansion improved or reduced "
                            "accuracy."),
    }
    files[SUMMARY_FILE] = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    return files, summary


def execution_block():
    return {"date": date.today().isoformat(), "python": platform.python_version(),
            "platform": platform.system(), "packages": _package_versions()}


def write_outputs(out_dir):
    catalog, profiles, labels = load_frozen()
    files, summary = build_outputs(catalog, profiles, labels, read_manifest())
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        if name == SUMMARY_FILE:
            data = json.loads(text)
            data["execution"] = execution_block()
            text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        (out / name).write_text(text, encoding="utf-8")
    return summary


def _live_version():
    path = DEFAULT_DATA_DIR / "dataset_manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))["dataset_version"]


LIVE_FIELD = "live_catalogue_matches_frozen"


def _live_field_issues(saved, recomputed):
    # LIVE_FIELD records the live catalogue at freezing time, when it was v1.3.0 and identical, so it is saved as true
    # While the live catalogue is still v1.3.0 the field is compared like any other
    # After the live catalogue moves on, the recomputed value must be false and the saved value must still be
    # exactly true; any other combination is reported, and only then is the field set aside for the full comparison
    if _live_version() == read_manifest()["dataset_version"]:
        return []
    old, new = saved.get("data", {}).pop(LIVE_FIELD, None), recomputed.get("data", {}).pop(LIVE_FIELD, None)
    issues = []
    if old is not True:
        issues.append(f"{SUMMARY_FILE}: saved {LIVE_FIELD} is {old!r}, expected the frozen value True")
    if new is not False:
        issues.append(f"{SUMMARY_FILE}: recomputed {LIVE_FIELD} is {new!r}, expected False for a later live catalogue")
    return issues


def check_outputs(saved_dir):
    # Recomputes everything and compares with the saved files; the execution block is ignored
    catalog, profiles, labels = load_frozen()
    files, _ = build_outputs(catalog, profiles, labels, read_manifest())
    saved_dir = Path(saved_dir)
    diffs = []
    for name, text in files.items():
        path = saved_dir / name
        if not path.exists():
            diffs.append(f"{name}: missing")
            continue
        saved = path.read_text(encoding="utf-8")
        if name == SUMMARY_FILE:
            a, b = json.loads(saved), json.loads(text)
            a.pop("execution", None)
            diffs += _live_field_issues(a, b)
            if a != b:
                diffs.append(f"{name}: differs")
        elif saved != text:
            diffs.append(f"{name}: differs")
    return diffs


def main(argv=None):
    parser = argparse.ArgumentParser(description="Independent 64-career evaluation (eval64_v1).")
    parser.add_argument("--output", help="directory for the outputs, e.g. reports/evaluation_64")
    parser.add_argument("--check", help="saved output directory to compare against")
    args = parser.parse_args(argv)
    if args.check:
        diffs = check_outputs(args.check)
        if diffs:
            print("Differences found:\n" + "\n".join(diffs))
            return 1
        print(f"eval64 outputs match {args.check}.")
        return 0
    out = args.output or tempfile.mkdtemp(prefix="eval64_")
    summary = write_outputs(out)
    o = summary["overall"]
    print(f"Wrote {out}: {summary['data']['profiles']} profiles, NDCG@5 {o['ndcg_at_5']['mean']}, "
          f"P@5 {o['precision_at_5']['mean']}, R@5 {o['recall_at_5']['mean']}, MAP {o['average_precision']['mean']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
