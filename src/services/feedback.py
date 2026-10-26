# Session-only relevance feedback: re-ranks careers from one learner's own reactions
# The formula score is never changed; a separate, explained adjustment is added on top
# Nothing here is stored or shared between learners

INTERESTED = 1
NOT_FOR_ME = -1
FEEDBACK_VALUES = (INTERESTED, NOT_FOR_ME)

# At most this many points move towards or away from one rated career at full similarity
POINTS_PER_RATING = 10.0
# The total adjustment for one career stays within this range
MAX_ADJUSTMENT = 15.0
SKILL_WEIGHT = 0.6
CATEGORY_WEIGHT = 0.4
# Similarities below this are ignored so unrelated careers do not move
MIN_SIMILARITY = 0.15


def _skills(career):
    return set(career.required_skills) | set(career.preferred_skills)


def career_similarity(a, b):
    # 0.6 x Jaccard overlap of all skills + 0.4 x same category, between 0 and 1
    sa, sb = _skills(a), _skills(b)
    jaccard = len(sa & sb) / len(sa | sb) if (sa or sb) else 0.0
    same_category = 1.0 if a.category == b.category else 0.0
    return SKILL_WEIGHT * jaccard + CATEGORY_WEIGHT * same_category


def clean_feedback(feedback, career_ids):
    # Keeps only known careers with a valid value
    known = set(career_ids)
    return {cid: v for cid, v in (feedback or {}).items() if cid in known and v in FEEDBACK_VALUES}


def adapt_recommendations(recommendations, catalog, feedback):
    # recommendations: the full list from recommend(top_k=None), already in formula order
    # Returns (shown, hidden): careers re-ranked by adjusted score, and careers marked not for me
    by_id = {c.career_id: c for c in catalog.careers}
    feedback = clean_feedback(feedback, by_id)
    rated = [(by_id[cid], v) for cid, v in sorted(feedback.items())]
    shown, hidden = [], []
    for order, rec in enumerate(recommendations):
        cid = rec["career_id"]
        career = by_id[cid]
        reasons, total = [], 0.0
        if cid not in feedback:
            for other, value in rated:
                sim = career_similarity(career, other)
                if sim < MIN_SIMILARITY:
                    continue
                points = value * POINTS_PER_RATING * sim
                total += points
                mark = "you are interested in" if value == INTERESTED else "you marked not for me"
                reasons.append((abs(points), f"{points:+.1f}: similar to {other.title}, which {mark}"))
        capped = max(-MAX_ADJUSTMENT, min(MAX_ADJUSTMENT, total))
        if capped != total:
            reasons.append((0.0, f"Total limited to {capped:+.1f} points"))
        total = capped
        adjusted = max(0.0, min(100.0, rec["score"] + total))
        out = dict(rec)
        out["formula_score"] = rec["score"]
        out["feedback_adjustment"] = round(total, 1)
        out["adjusted_score"] = round(adjusted, 1)
        out["feedback_reasons"] = [text for _, text in sorted(reasons, key=lambda t: -t[0])]
        out["user_feedback"] = feedback.get(cid)
        out["_order"] = order
        (hidden if feedback.get(cid) == NOT_FOR_ME else shown).append(out)
    shown.sort(key=lambda r: (-r["adjusted_score"], r["_order"]))
    for rank, rec in enumerate(shown, start=1):
        rec["rank"] = rank
        rec.pop("_order")
    for rec in hidden:
        rec.pop("_order")
        rec["rank"] = None
    return shown, hidden
