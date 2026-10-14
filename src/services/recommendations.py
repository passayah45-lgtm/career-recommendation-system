# Public entry point: raw profile in, ranked and explained careers out
# Output is plain dicts and lists so Streamlit and a future REST API can use it directly

from src.engine.explanations import build_notes, build_reasons
from src.engine.ranking import rank_careers
from src.engine.scoring import COMPONENT_ORDER, DEFAULT_WEIGHTS
from src.services.profiles import build_profile

DEFAULT_TOP_K = 5
SCORE_DECIMALS = 1
SCORE_DISCLAIMER = (
    "The compatibility score (0 to 100) ranks careers by how well your profile matches this dataset. "
    "It is not a probability of being hired or of success in the career."
)


def profile_from_input(profile_data, catalog):
    return build_profile(profile_data, catalog.known_skills, catalog.aliases, catalog.interests)


def _components_dict(score):
    return {
        c.name: {
            "value": round(c.value, 4),
            "weight": c.weight,
            "applicable": c.applicable,
            "provided": c.provided,
            "contribution": round(c.contribution, 2),
        }
        for c in score.components
    }


def recommendation_to_dict(ranked):
    match, score, career = ranked.match, ranked.score, ranked.match.career
    sk, edu = match.skills, match.education
    return {
        "rank": ranked.rank,
        "career_id": career.career_id,
        "career_title": career.title,
        "category": career.category,
        "score": round(score.total, SCORE_DECIMALS),
        "score_components": _components_dict(score),
        "matched_required_skills": list(sk.matched_required),
        "missing_required_skills": list(sk.missing_required),
        "matched_preferred_skills": list(sk.matched_preferred),
        "missing_preferred_skills": list(sk.missing_preferred),
        "matched_interests": list(match.matched_interests),
        "career_interests": list(career.interests),
        "education": {
            "learner_level": edu.learner_level,
            "career_level": edu.career_level,
            "meets_level": edu.meets_level,
            "levels_below": edu.gap,
        },
        "learning_goals": list(career.learning_goals),
        "reasons": list(build_reasons(match, score)),
        "notes": list(build_notes(match, score)),
        "source_url": career.source_url,
    }


def _profile_warnings(report):
    warnings = []
    if report.unknown_skills:
        warnings.append(f"These skills are not in the dataset and were not scored: {', '.join(report.unknown_skills)}.")
    if report.unknown_interests:
        warnings.append(f"These interests are not in the interest list and were not scored: {', '.join(report.unknown_interests)}.")
    if report.duplicate_skills:
        warnings.append(f"Repeated skills were counted once: {', '.join(report.duplicate_skills)}.")
    if len(report.missing_fields) == 3:
        warnings.append("The profile has no recognized skills, interests or education level. "
                        "All scores are 0 and careers are listed in career_id order.")
    elif report.missing_fields:
        warnings.append(f"Missing or unrecognized profile fields scored 0: {', '.join(report.missing_fields)}.")
    if report.ignored_fields:
        warnings.append(f"Unsupported fields were ignored: {', '.join(report.ignored_fields)}.")
    return warnings


def recommend(profile_data, catalog, top_k=DEFAULT_TOP_K, weights=DEFAULT_WEIGHTS):
    # Validates the profile, ranks all careers and returns the top_k with explanations
    profile, report = profile_from_input(profile_data, catalog)
    ranked = rank_careers(
        profile, catalog.careers, weights=weights, top_k=top_k,
        skills_provided=report.skills_provided, interests_provided=report.interests_provided,
    )
    return {
        "profile": {
            "skills": list(profile.skills),
            "interests": list(profile.interests),
            "education_level": profile.education_level,
            "experience_years": profile.experience_years,
            "report": report.to_dict(),
            "profile_complete": not report.missing_fields,
        },
        "weights": {name: weights.as_dict()[name] for name in COMPONENT_ORDER},
        "careers_scored": len(catalog.careers),
        "recommendations": [recommendation_to_dict(r) for r in ranked],
        "warnings": _profile_warnings(report),
        "disclaimer": SCORE_DISCLAIMER,
    }
