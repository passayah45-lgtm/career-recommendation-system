# Personalised skill development roadmap for one learner and one career
# Pure functions with plain-dictionary input and output, so a future T-Career API can call them unchanged
# The skill gap always comes from analyze_skill_gap(); a roadmap step never marks a skill as learned

from src.data.preprocessing import normalize_skill
from src.services.catalog import UnknownCareerError
from src.services.recommendations import recommend
from src.services.skill_gap import analyze_skill_gap

NOT_STARTED = "not_started"
IN_PROGRESS = "in_progress"
COMPLETED = "completed"
STATUSES = (NOT_STARTED, IN_PROGRESS, COMPLETED)
STATUS_LABELS = {NOT_STARTED: "Not started", IN_PROGRESS: "In progress", COMPLETED: "Completed"}
# Short codes for the page address; not started is the default and is never stored
STATUS_CODES = {IN_PROGRESS: "p", COMPLETED: "c"}
CODE_STATUSES = {v: k for k, v in STATUS_CODES.items()}
MAX_QUERY_LENGTH = 3000

REQUIRED = "required"
OPTIONAL = "optional"
PREREQUISITE = "prerequisite"

# The dataset has no verified prerequisite relationships, so none are assumed
# A future data source can pass {skill: [prerequisite skills]} to build_roadmap()
KNOWN_PREREQUISITES = {}

ORDER_NOTE = (
    "Suggested order, not a verified prerequisite chain: missing required skills come first, then optional skills. "
    "Within each group, skills required by more careers in the catalogue come first because they are useful for "
    "more careers; ties keep the order listed for the career."
)
MASTERY_NOTE = (
    "Completing a step means you marked it done. It does not prove you have mastered the skill. A skill only counts "
    "in your skill gap after you add it to your profile."
)


class RoadmapError(ValueError):
    pass


def skill_demand(catalog):
    # {skill: (careers requiring it, careers listing it at all)} from the career data
    demand = {}
    for career in catalog.careers:
        for skill in career.required_skills:
            req, total = demand.get(skill, (0, 0))
            demand[skill] = (req + 1, total + 1)
        for skill in career.preferred_skills:
            req, total = demand.get(skill, (0, 0))
            demand[skill] = (req, total + 1)
    return demand


def order_skills(skills, demand):
    # Most widely required first, then most widely listed, then the career's own listing order
    position = {s: i for i, s in enumerate(skills)}
    return sorted(dict.fromkeys(skills), key=lambda s: (-demand.get(s, (0, 0))[0], -demand.get(s, (0, 0))[1],
                                                        position[s]))


def apply_prerequisites(ordered, prerequisites, have):
    # Moves each missing prerequisite in front of the skill that needs it, keeping the rest of the order
    # Missing prerequisites that are not in the list are added as extra steps; cycles are ignored safely
    result, placed, visiting, added = [], set(), set(), {}

    def visit(skill, needed_by=None):
        if skill in placed or skill in visiting:
            return
        visiting.add(skill)
        for pre in prerequisites.get(skill, ()):
            if pre not in have:
                if pre not in ordered and pre not in added:
                    added[pre] = skill
                visit(pre, skill)
        visiting.discard(skill)
        placed.add(skill)
        result.append(skill)

    for skill in ordered:
        visit(skill)
    return result, added


def select_resources(skills, catalog):
    # One resource per skill from the dataset, avoiding a resource already chosen for an earlier skill
    chosen, used = {}, {}
    for index, skill in enumerate(skills, start=1):
        options = catalog.resources.for_skill(skill, catalog.aliases)
        if not options:
            chosen[skill] = {"resources": [], "note": "No learning resource for this skill in the catalogue yet."}
            continue
        fresh = [r for r in options if r.resource_id not in used]
        pick = fresh[0] if fresh else options[0]
        note = "" if fresh else f"Same resource as step {used[pick.resource_id]}; no alternative in the catalogue."
        used.setdefault(pick.resource_id, index)
        chosen[skill] = {"resources": [pick.to_dict()], "note": note, "alternatives": len(options) - 1}
    return chosen


def _why(skill, kind, career, demand, n_careers, needed_by=None):
    req, total = demand.get(skill, (0, 0))
    if kind == REQUIRED:
        lines = [f"Required for {career.title}: you need it to meet this career's skill requirements."]
    elif kind == OPTIONAL:
        lines = [f"Optional for {career.title}: it can improve your readiness but is not needed to meet the "
                 "requirements."]
    else:
        lines = [f"Listed as a prerequisite for {needed_by}."]
    if req:
        lines.append(f"Required by {req} of {n_careers} careers in the catalogue.")
    elif total:
        lines.append(f"Listed as optional by {total} of {n_careers} careers in the catalogue.")
    return lines


def progress_summary(steps):
    total = len(steps)
    counts = {s: sum(1 for step in steps if step["status"] == s) for s in STATUSES}
    return {
        "total_steps": total,
        "completed": counts[COMPLETED],
        "in_progress": counts[IN_PROGRESS],
        "not_started": counts[NOT_STARTED],
        "completion_percent": round(100.0 * counts[COMPLETED] / total, 1) if total else None,
    }


def build_roadmap(profile_data, career_id, catalog, progress=None, prerequisites=None):
    # profile_data may be None (no assessment): every skill then counts as missing
    # progress: {skill: status} for this career only; unknown skills and statuses are ignored
    # Raises RoadmapError for an unknown career and ProfileValidationError for an invalid profile
    try:
        career = catalog.get_career(career_id)
    except UnknownCareerError:
        raise RoadmapError(f"unknown career id '{career_id}'") from None
    profile = profile_data if profile_data else {"skills": []}
    gap = analyze_skill_gap(profile, career_id, catalog, include_resources=False)
    prerequisites = KNOWN_PREREQUISITES if prerequisites is None else prerequisites
    demand = skill_demand(catalog)
    n_careers = len(catalog.careers)
    have = set(gap["have_required_skills"]) | set(gap["have_preferred_skills"])
    learner_skills = {normalize_skill(s, catalog.aliases) for s in profile.get("skills", [])}
    have |= learner_skills

    required = order_skills(gap["missing_required_skills"], demand)
    optional = order_skills(gap["missing_preferred_skills"], demand)
    ordered, added = apply_prerequisites(required + optional, prerequisites, have)
    kinds = {s: REQUIRED for s in required} | {s: OPTIONAL for s in optional} | {s: PREREQUISITE for s in added}
    resources = select_resources(ordered, catalog)
    saved = progress or {}

    steps = []
    for number, skill in enumerate(ordered, start=1):
        pres = [{"skill": p, "have": p in have} for p in prerequisites.get(skill, ())]
        status = saved.get(skill, NOT_STARTED)
        steps.append({
            "step": number,
            "skill": skill,
            "kind": kinds[skill],
            "why": _why(skill, kinds[skill], career, demand, n_careers, added.get(skill)),
            "prerequisites": pres,
            "resources": resources[skill]["resources"],
            "resource_note": resources[skill]["note"],
            "status": status if status in STATUSES else NOT_STARTED,
        })

    fit = None
    if profile_data:
        recs = recommend(profile_data, catalog, top_k=None)["recommendations"]
        rec = next(r for r in recs if r["career_id"] == career_id)
        fit = {"score": rec["score"], "rank": rec["rank"], "careers_ranked": len(recs)}
    step_skills = {s["skill"] for s in steps}
    return {
        "career_id": career.career_id,
        "career_title": career.title,
        "category": career.category,
        "fit": fit,
        "have_required_skills": gap["have_required_skills"],
        "have_preferred_skills": gap["have_preferred_skills"],
        "missing_required_skills": required,
        "missing_preferred_skills": optional,
        "required_total": len(career.required_skills),
        "meets_all_required": gap["meets_all_required"],
        "steps": steps,
        "progress": progress_summary(steps),
        "saved_outside_steps": sorted(s for s in saved if s not in step_skills),
        "prerequisites_known": bool(prerequisites),
        "order_note": ORDER_NOTE if not prerequisites else ORDER_NOTE + " Known prerequisites are placed first.",
        "mastery_note": MASTERY_NOTE,
        "learning_goals": gap["learning_goals"],
    }


# Progress records: {career_id: {skill: status}}, only in progress and completed are stored

def clean_progress(raw, catalog):
    # Returns (clean progress, list of plain-language issues); never raises on bad data
    issues = []
    if raw is None:
        return {}, issues
    if not isinstance(raw, dict):
        return {}, ["Saved roadmap progress had an unexpected format and was ignored."]
    known_careers = {c.career_id for c in catalog.careers}
    known_skills = set(catalog.known_skills)
    clean = {}
    for cid, steps in raw.items():
        if cid not in known_careers:
            issues.append(f"Saved progress for an unknown career ({str(cid)[:20]}) was ignored.")
            continue
        if not isinstance(steps, dict):
            issues.append(f"Saved progress for {cid} had an unexpected format and was ignored.")
            continue
        kept = {}
        for skill, status in steps.items():
            if not isinstance(skill, str) or skill not in known_skills:
                issues.append(f"A saved step for {cid} refers to a skill that is no longer in the catalogue.")
            elif status not in (IN_PROGRESS, COMPLETED):
                if status != NOT_STARTED:
                    issues.append(f"A saved step for {cid} had an unknown status and was reset.")
            else:
                kept[skill] = status
        if kept:
            clean[cid] = dict(sorted(kept.items()))
    return dict(sorted(clean.items())), issues


def set_step_status(progress, career_id, skill, status):
    # Returns a new progress dict; not started removes the record
    if status not in STATUSES:
        raise RoadmapError(f"unknown status '{status}'")
    out = {cid: dict(steps) for cid, steps in (progress or {}).items()}
    steps = out.setdefault(career_id, {})
    if status == NOT_STARTED:
        steps.pop(skill, None)
    else:
        steps[skill] = status
    if not steps:
        out.pop(career_id)
    return out


def delete_roadmap(progress, career_id):
    return {cid: dict(steps) for cid, steps in (progress or {}).items() if cid != career_id}


def add_skill_to_profile(profile, skill, catalog):
    # Returns a new raw profile with the skill added once; the caller must have asked the learner to confirm
    profile = dict(profile or {})
    skills = list(profile.get("skills", []))
    if normalize_skill(skill, catalog.aliases) not in {normalize_skill(s, catalog.aliases) for s in skills}:
        skills.append(skill)
    profile["skills"] = skills
    return profile


def progress_to_query(progress):
    # "C001:python=c,sql=p;C003:git=p" with careers and skills sorted
    parts = []
    for cid in sorted(progress or {}):
        steps = ",".join(f"{skill}={STATUS_CODES[st]}" for skill, st in sorted(progress[cid].items())
                         if st in STATUS_CODES)
        if steps:
            parts.append(f"{cid}:{steps}")
    return ";".join(parts)


def progress_from_query(raw, catalog):
    if not isinstance(raw, str) or not raw or len(raw) > MAX_QUERY_LENGTH:
        return {}
    data = {}
    for part in raw.split(";"):
        cid, sep, steps = part.partition(":")
        if not sep:
            continue
        for item in steps.split(","):
            skill, sep, code = item.partition("=")
            if sep and code in CODE_STATUSES:
                data.setdefault(cid.strip(), {})[skill.strip()] = CODE_STATUSES[code]
    clean, _ = clean_progress(data, catalog)
    return clean
