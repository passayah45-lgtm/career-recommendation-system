# Builds one feature row per learner-career pair from the same matching the engine uses
# Only facts available at recommendation time are used: no career id, category or profile metadata

from src.engine.matching import match_career
from src.engine.scoring import education_value
from src.services.recommendations import profile_from_input

FEATURE_NAMES = (
    "required_coverage",
    "required_matched",
    "required_missing",
    "required_total",
    "preferred_coverage",
    "preferred_matched",
    "interest_coverage",
    "interest_matched",
    "education_value",
    "education_gap",
    "education_provided",
    "learner_skill_count",
    "learner_skills_used_share",
)


def _share(part, whole):
    return part / whole if whole else 0.0


def pair_features(profile, career):
    # profile is a validated LearnerProfile; returns a list aligned with FEATURE_NAMES
    m = match_career(profile, career)
    sk = m.skills
    req_total = len(career.required_skills)
    pref_total = len(career.preferred_skills)
    gap = m.education.gap
    used = len(sk.matched_required) + len(sk.matched_preferred)
    n_skills = len(profile.skills)
    return [
        _share(len(sk.matched_required), req_total),
        float(len(sk.matched_required)),
        float(len(sk.missing_required)),
        float(req_total),
        _share(len(sk.matched_preferred), pref_total),
        float(len(sk.matched_preferred)),
        _share(len(m.matched_interests), len(career.interests)),
        float(len(m.matched_interests)),
        float(education_value(m)),
        float(gap) if gap is not None else 0.0,
        1.0 if gap is not None else 0.0,
        float(n_skills),
        _share(used, n_skills),
    ]


def profile_matrix(profile_data, catalog):
    # Returns (career_ids, rows) for one raw profile against every career, careers in catalogue order
    profile, _ = profile_from_input(profile_data, catalog)
    ids, rows = [], []
    for career in catalog.careers:
        ids.append(career.career_id)
        rows.append(pair_features(profile, career))
    return ids, rows


def build_pair_dataset(profiles, catalog):
    # Stacks all labelled profiles into X, y and a profile group id per row
    X, y, groups, career_ids = [], [], [], []
    for p in profiles:
        ids, rows = profile_matrix(p.as_input(), catalog)
        relevant = set(p.relevant_career_ids)
        for cid, row in zip(ids, rows):
            X.append(row)
            y.append(1 if cid in relevant else 0)
            groups.append(p.profile_id)
            career_ids.append(cid)
    return X, y, groups, career_ids
