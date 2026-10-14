# Skill-gap analysis for one learner and one career
# Required and preferred gaps stay separate: a missing preferred skill is optional

from src.engine.matching import match_skills
from src.engine.scoring import coverage
from src.services.recommendations import profile_from_input

RESOURCE_NOTE = (
    "Resource links were confirmed in web search results on the verified_on date. "
    "They were not HTTP-checked, so a link may have moved since then."
)


def _round(value):
    return None if value is None else round(value, 4)


def analyze_skill_gap(profile_data, career_id, catalog, include_resources=True):
    # Raises UnknownCareerError for an unknown id and ProfileValidationError for bad input
    career = catalog.get_career(career_id)
    profile, report = profile_from_input(profile_data, catalog)
    sk = match_skills(profile.skills, career)

    req_cov = coverage(len(sk.matched_required), len(career.required_skills))
    pref_cov = coverage(len(sk.matched_preferred), len(career.preferred_skills))
    all_skills = len(career.required_skills) + len(career.preferred_skills)
    all_cov = coverage(len(sk.matched_required) + len(sk.matched_preferred), all_skills)

    result = {
        "career_id": career.career_id,
        "career_title": career.title,
        "category": career.category,
        "have_required_skills": list(sk.matched_required),
        "missing_required_skills": list(sk.missing_required),
        "have_preferred_skills": list(sk.matched_preferred),
        "missing_preferred_skills": list(sk.missing_preferred),
        "required_coverage": _round(req_cov),
        "preferred_coverage": _round(pref_cov),
        "overall_skill_coverage": _round(all_cov),
        "meets_all_required": not sk.missing_required,
        "unknown_skills": list(report.unknown_skills),
        "learning_goals": list(career.learning_goals),
    }
    if include_resources:
        result["resources"] = {
            "required": catalog.resources.for_skills(sk.missing_required, catalog.aliases),
            "preferred": catalog.resources.for_skills(sk.missing_preferred, catalog.aliases),
        }
        result["resource_note"] = RESOURCE_NOTE
    return result
