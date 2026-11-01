# Review diagnostics for eval64_v1: vocabulary, profile types, exposure and ties
# Read-only use of the production engine; nothing here changes scoring or ranking

from collections import Counter, defaultdict

from src.engine.ranking import rank_careers, sort_key
from src.evaluation.bootstrap import profile_bootstrap
from src.evaluation.eval64_data import DEFAULT_THRESHOLD, PROFILE_TYPES
from src.services.recommendations import profile_from_input, recommend

K = 5
DECIMALS = 4
NEW_CAREERS = frozenset(f"C{i:03d}" for i in range(51, 65))
EXPOSURE_EXAMPLE_CAREER = "C004"
# Profile-type sample sizes: below 5 nothing is interpreted, 5 to 9 is indicative, 10 or more is reported as a result
SMALL_SAMPLE, ADEQUATE_SAMPLE = 5, 10
TYPE_METRICS = ("precision_at_1", "precision_at_5", "recall_at_5", "reciprocal_rank", "average_precision",
                "ndcg_at_5")


def _r(value):
    return None if value is None else round(value, DECIMALS)


def _share(part, whole):
    return _r(part / whole) if whole else None


def sample_status(n):
    if n < SMALL_SAMPLE:
        return "insufficient (fewer than 5 profiles)"
    if n < ADEQUATE_SAMPLE:
        return "indicative only (5 to 9 profiles)"
    return "reported (10 or more profiles)"


# ---------- Vocabulary ----------

def vocabulary_analysis(catalog, profiles):
    # Denominator: every skill entry typed in profiles.csv (480 entries; no profile repeats a skill)
    per_profile = []
    unknown_terms = Counter()
    for p in profiles:
        _, report = profile_from_input(p.as_input(), catalog)
        unknown = list(report.unknown_skills)
        unknown_terms.update(u.lower() for u in unknown)
        per_profile.append({"profile": p, "entries": len(p.skills), "unknown": len(unknown)})
    rows = []

    def add(scope, group):
        entries = sum(x["entries"] for x in group)
        unknown = sum(x["unknown"] for x in group)
        with_skills = [x for x in group if x["entries"]]
        rows.append({
            "scope": scope, "profiles": len(group), "profiles_with_skills": len(with_skills),
            "skill_entries": entries, "unrecognised_entries": unknown, "recognised_entries": entries - unknown,
            "unrecognised_share": _share(unknown, entries),
            "profiles_no_skill_recognised": sum(1 for x in with_skills if x["unknown"] == x["entries"]),
            "profiles_without_skills": len(group) - len(with_skills),
        })

    add("all profiles", per_profile)
    for t in PROFILE_TYPES:
        group = [x for x in per_profile if x["profile"].profile_type == t]
        if group:
            add(f"type: {t}", group)
    for cat in sorted({x["profile"].primary_category for x in per_profile}):
        add(f"category: {cat}", [x for x in per_profile if x["profile"].primary_category == cat])
    zero = [{"profile_id": x["profile"].profile_id, "profile_type": x["profile"].profile_type,
             "primary_category": x["profile"].primary_category, "skill_entries": x["entries"],
             "skills": "|".join(x["profile"].skills)}
            for x in per_profile if x["entries"] and x["unknown"] == x["entries"]]
    terms = [{"term": t, "profiles": n} for t, n in sorted(unknown_terms.items(), key=lambda kv: (-kv[1], kv[0]))]
    return rows, zero, terms


# ---------- Profile types ----------

def profile_type_table(rows):
    out = []
    for t in PROFILE_TYPES:
        group = [r for r in rows if r["profile_type"] == t]
        if not group:
            continue
        stats = profile_bootstrap(group, TYPE_METRICS)
        row = {"profile_type": t, "profiles": len(group),
               "defined_profiles": stats["precision_at_5"]["defined_profiles"],
               "excluded_no_relevant": stats["precision_at_5"]["undefined_profiles"],
               "sample_status": sample_status(len(group))}
        for name in TYPE_METRICS:
            row[name] = _r(stats[name]["mean"])
        row["ndcg_at_5_ci_low"] = _r(stats["ndcg_at_5"]["ci_low"])
        row["ndcg_at_5_ci_high"] = _r(stats["ndcg_at_5"]["ci_high"])
        out.append(row)
    return out


# ---------- Exposure ----------

def _slot_driver(rec):
    skills = len(rec["matched_required_skills"]) + len(rec["matched_preferred_skills"])
    if skills:
        return "skills matched"
    if rec["matched_interests"]:
        return "interests only"
    return "education only"


def exposure_analysis(catalog, profiles, labels):
    category_of = {c.career_id: c.category for c in catalog.careers}
    careers_per_cat = Counter(category_of.values())
    profiles_per_cat = Counter(p.primary_category for p in profiles)
    slots = []
    for p in profiles:
        recs = recommend(p.as_input(), catalog, top_k=K)["recommendations"]
        for rec in recs:
            cid = rec["career_id"]
            slots.append({"profile": p, "rec": rec, "category": category_of[cid],
                          "grade": labels[p.profile_id].get(cid, 0), "driver": _slot_driver(rec)})
    total = len(slots)
    cat_rows = []
    for cat in sorted(careers_per_cat):
        mine = [s for s in slots if s["category"] == cat]
        own = [s for s in mine if s["profile"].primary_category == cat]
        cat_rows.append({
            "category": cat, "profile_share": _share(profiles_per_cat[cat], len(profiles)),
            "career_share": _share(careers_per_cat[cat], len(category_of)),
            "top5_slots": len(mine), "slot_share": _share(len(mine), total),
            "slots_from_own_category_profiles": len(own), "slots_from_other_profiles": len(mine) - len(own),
            "relevant_slots_grade2plus": sum(1 for s in mine if s["grade"] >= DEFAULT_THRESHOLD),
            "weak_slots_grade1": sum(1 for s in mine if s["grade"] == 1),
            "not_relevant_slots_grade0": sum(1 for s in mine if s["grade"] == 0),
            "slots_skills_matched": sum(1 for s in mine if s["driver"] == "skills matched"),
            "slots_interests_only": sum(1 for s in mine if s["driver"] == "interests only"),
        })
    examples = []
    for s in slots:
        rec = s["rec"]
        if rec["career_id"] != EXPOSURE_EXAMPLE_CAREER:
            continue
        comp = rec["score_components"]
        examples.append({
            "profile_id": s["profile"].profile_id, "primary_category": s["profile"].primary_category,
            "profile_type": s["profile"].profile_type, "rank": rec["rank"], "score": rec["score"],
            "grade": s["grade"], "driver": s["driver"],
            "matched_required": "|".join(rec["matched_required_skills"]),
            "matched_preferred": "|".join(rec["matched_preferred_skills"]),
            "matched_interests": "|".join(rec["matched_interests"]),
            "required_points": comp["required_skills"]["contribution"],
            "preferred_points": comp["preferred_skills"]["contribution"],
            "interest_points": comp["interests"]["contribution"],
            "education_points": comp["education"]["contribution"],
        })
    career_rows = []
    by_career = defaultdict(list)
    for s in slots:
        by_career[s["rec"]["career_id"]].append(s)
    interest_freq = Counter(i for p in profiles for i in p.interests)
    for c in catalog.careers:
        mine = by_career.get(c.career_id, [])
        career_rows.append({
            "career_id": c.career_id, "career_title": c.title, "category": c.category,
            "career_interests": "|".join(c.interests), "interest_count": len(c.interests),
            "profiles_sharing_an_interest": sum(1 for p in profiles if set(p.interests) & set(c.interests)),
            "points_per_matched_interest": _r(25 / len(c.interests)) if c.interests else None,
            "top5_appearances": len(mine),
            "relevant_appearances": sum(1 for s in mine if s["grade"] >= DEFAULT_THRESHOLD),
            "grade0_appearances": sum(1 for s in mine if s["grade"] == 0),
            "interests_only_appearances": sum(1 for s in mine if s["driver"] == "interests only"),
        })
    interest_rows = [{"interest": i, "profiles": n} for i, n in sorted(interest_freq.items(), key=lambda kv: (-kv[1], kv[0]))]
    driver_rows = [{"driver": d, "slots": n, "share": _share(n, total)}
                   for d, n in sorted(Counter(s["driver"] for s in slots).items())]
    return cat_rows, career_rows, examples, interest_rows, driver_rows


# ---------- Ties ----------

def tie_analysis(catalog, profiles, labels):
    # Uses the engine's own sort key: total score (9 decimals), required coverage, matched required count, career id
    rows, groups_out = [], []
    totals = Counter()
    for p in profiles:
        prof, report = profile_from_input(p.as_input(), catalog)
        ranked = rank_careers(prof, catalog.careers, skills_provided=report.skills_provided,
                              interests_provided=report.interests_provided)
        keys = [sort_key((r.match, r.score)) for r in ranked]
        ids = [r.match.career.career_id for r in ranked]
        display = [round(r.score.total, 1) for r in ranked]
        k5, k6 = keys[K - 1], keys[K]
        score_tie = k5[0] == k6[0]
        if not score_tie:
            resolved_by = "no tie"
        elif k5[1] != k6[1]:
            resolved_by = "required-skill coverage"
        elif k5[2] != k6[2]:
            resolved_by = "number of matched required skills"
        else:
            resolved_by = "career id"
        totals[resolved_by] += 1
        groups = defaultdict(list)
        for position, (key, cid) in enumerate(zip(keys, ids), start=1):
            groups[key[:3]].append((position, cid))
        for members in groups.values():
            if len(members) < 2:
                continue
            original = [(pos, c) for pos, c in members if c not in NEW_CAREERS]
            new = [(pos, c) for pos, c in members if c in NEW_CAREERS]
            inside = [c for pos, c in members if pos <= K]
            outside = [c for pos, c in members if pos > K]
            straddles = bool(inside and outside)
            new_out = [c for pos, c in new if pos > K]
            orig_in = [c for pos, c in original if pos <= K]
            excluded = new_out if (straddles and orig_in) else []
            relevant_excluded = [c for c in excluded if labels[p.profile_id].get(c, 0) >= DEFAULT_THRESHOLD]
            # Any relevant career left outside the top 5 inside a group that crosses the cut-off lost its place on id
            relevant_out = [c for c in outside if straddles and labels[p.profile_id].get(c, 0) >= DEFAULT_THRESHOLD]
            totals["relevant_careers_pushed_out_of_top5_by_id"] += len(relevant_out)
            totals["relevant_original_pushed_out_of_top5_by_id"] += sum(1 for c in relevant_out if c not in NEW_CAREERS)
            totals["id_tie_groups"] += 1
            totals["id_tie_original_ahead_of_new_pairs"] += sum(1 for po, _ in original for pn, _ in new if po < pn)
            totals["id_tie_new_ahead_of_original_pairs"] += sum(1 for po, _ in original for pn, _ in new if pn < po)
            totals["id_tie_pairs_touching_top5"] += sum(1 for po, _ in original for pn, _ in new if min(po, pn) <= K)
            totals["id_tie_groups_straddling_rank5"] += straddles
            totals["new_careers_pushed_out_of_top5_by_id"] += len(excluded)
            totals["relevant_new_careers_pushed_out_of_top5_by_id"] += len(relevant_excluded)
            if straddles:
                groups_out.append({
                    "profile_id": p.profile_id, "positions": f"{members[0][0]}-{members[-1][0]}",
                    "careers_in_top5": "|".join(inside), "careers_outside_top5": "|".join(outside),
                    "new_careers_pushed_out": "|".join(excluded),
                    "relevant_new_pushed_out": "|".join(relevant_excluded),
                    "relevant_pushed_out": "|".join(relevant_out),
                    "score": round(keys[members[0][0] - 1][0] * -1, 4),
                })
        rows.append({"profile_id": p.profile_id, "score_tie_at_rank5": score_tie,
                     "display_tie_at_rank5": display[K - 1] == display[K], "resolved_by": resolved_by,
                     "tied_with_rank5_total_score": sum(1 for key in keys if key[0] == k5[0])})
    summary = [
        {"measure": "profiles", "value": len(profiles)},
        {"measure": "display-score tie at rank 5/6 (one decimal, as shown to users)",
         "value": sum(r["display_tie_at_rank5"] for r in rows)},
        {"measure": "total-score tie at rank 5/6 (engine precision)", "value": sum(r["score_tie_at_rank5"] for r in rows)},
        {"measure": "rank 5/6 tie resolved by required-skill coverage", "value": totals["required-skill coverage"]},
        {"measure": "rank 5/6 tie resolved by number of matched required skills",
         "value": totals["number of matched required skills"]},
        {"measure": "rank 5/6 tie resolved by career id", "value": totals["career id"]},
        {"measure": "career-id tie groups (equal on all three score keys), any rank", "value": totals["id_tie_groups"]},
        {"measure": "original-before-new pairs decided by career id, any rank",
         "value": totals["id_tie_original_ahead_of_new_pairs"]},
        {"measure": "original-before-new pairs decided by career id, at least one in top 5",
         "value": totals["id_tie_pairs_touching_top5"]},
        {"measure": "career-id tie groups crossing the rank 5 cut-off", "value": totals["id_tie_groups_straddling_rank5"]},
        {"measure": "new careers kept out of the top 5 by career id", "value": totals["new_careers_pushed_out_of_top5_by_id"]},
        {"measure": "relevant (grade 2+) new careers kept out of the top 5 by career id",
         "value": totals["relevant_new_careers_pushed_out_of_top5_by_id"]},
        {"measure": "relevant (grade 2+) careers of any kind kept out of the top 5 by career id",
         "value": totals["relevant_careers_pushed_out_of_top5_by_id"]},
        {"measure": "of which original careers", "value": totals["relevant_original_pushed_out_of_top5_by_id"]},
        {"measure": "new-before-original pairs decided by career id, any rank",
         "value": totals["id_tie_new_ahead_of_original_pairs"]},
    ]
    return summary, rows, groups_out
