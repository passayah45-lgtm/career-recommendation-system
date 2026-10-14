# Plain-language reasons built only from values used in the score
# Every sentence maps to one scoring component

from src.engine.scoring import EDUCATION, INTERESTS, PREFERRED_SKILLS, REQUIRED_SKILLS


def _join(items):
    return ", ".join(items)


def _required_reason(match):
    sk, career = match.skills, match.career
    total = len(career.required_skills)
    if sk.matched_required:
        return f"You have {len(sk.matched_required)} of {total} required skills: {_join(sk.matched_required)}."
    return f"You have none of the {total} required skills yet."


def _preferred_reason(match):
    sk, career = match.skills, match.career
    if not career.preferred_skills:
        return None
    if sk.matched_preferred:
        return (f"You have {len(sk.matched_preferred)} of {len(career.preferred_skills)} "
                f"preferred (optional) skills: {_join(sk.matched_preferred)}.")
    return None


def _interest_reason(match):
    total = len(match.career.interests)
    if match.matched_interests:
        return f"Your interests match {len(match.matched_interests)} of {total} for this career: {_join(match.matched_interests)}."
    return None


def _education_reason(match):
    edu = match.education
    if not edu.provided:
        return None
    if edu.meets_level:
        return (f"Your education level ({edu.learner_level}) meets the typical entry level "
                f"({edu.career_level}) recorded in this dataset.")
    return (f"Your education level ({edu.learner_level}) is {edu.gap} level(s) below the typical entry level "
            f"({edu.career_level}). Education has a small weight and is not a hard requirement.")


def build_reasons(match, score):
    # Reasons for the score, ordered by component weight in the default model
    reasons = [_required_reason(match)]
    for builder in (_preferred_reason, _interest_reason, _education_reason):
        text = builder(match)
        if text:
            reasons.append(text)
    return tuple(reasons)


def build_notes(match, score):
    # Limits on the result caused by missing input or the dataset itself
    notes = []
    if not score.component(REQUIRED_SKILLS).provided:
        notes.append("No recognized skills were provided, so both skill components scored 0.")
    if not score.component(INTERESTS).provided:
        notes.append("No recognized interests were provided, so the interest component scored 0.")
    if not score.component(EDUCATION).provided:
        notes.append("No education level was provided, so the education component scored 0.")
    if not score.component(PREFERRED_SKILLS).applicable:
        notes.append("This career lists no preferred skills, so that component was left out of the score.")
    if match.skills.missing_required:
        notes.append(f"Missing required skills: {_join(match.skills.missing_required)}.")
    return tuple(notes)
