# Skill development roadmap

Added 29 October 2026. Page: **Skill Roadmap** in the sidebar, titled "My Skill Development Roadmap".

## What is implemented

| Part | Where |
|---|---|
| Roadmap generation, skill ordering, resource selection, progress maths, saved-data cleaning | `src/services/roadmap.py` (no Streamlit imports) |
| Session file with roadmap progress (version 2, version 1 still loads) | `src/services/session_data.py` |
| Session state, page-address sync | `src/ui/state.py` (`get_progress`, `set_progress`, `sync_feedback_with_url`) |
| Presentation | `src/ui/roadmap_view.py`, `pages/6_Skill_Roadmap.py` |
| Links to the roadmap | "Plan my learning" on Interested cards, "Plan my learning for this career" on the Skill-Gap page |
| Tests | `tests/test_roadmap.py` (14), roadmap tests in `tests/test_app.py` (9) |

The learner picks a career from, in this order: Interested careers, the top recommendations not yet rated, saved roadmaps (including careers now marked Not for me) and a career opened from another page. For each career the page shows:

- **Overview:** name, category, formula compatibility score and rank (only with an assessment), required skills owned, required and optional skills still to learn. The score is labelled as not a probability of employment or success.
- **Skill groups:** skills I already have, required skills to learn, optional skills for later.
- **Ordered learning plan:** one step per missing skill with why it matters, required or optional, prerequisites, the learning resource and a status (Not started, In progress, Completed) that the learner sets.
- **Progress:** total steps, completed, in progress, not started and the completion percentage.
- **Manage:** delete the roadmap's progress, with a confirmation.

## How the roadmap is generated

1. `analyze_skill_gap()` gives the missing required and optional skills. It is the only source of truth for the gap; no second algorithm exists.
2. Missing required skills come first, then optional skills.
3. Within each group, skills are sorted by how many of the 50 careers require them, then by how many list them at all, then by the order in `careers.csv`. This is a transparent suggestion: widely used skills help with more careers. It is shown on the page as "Suggested order, not a verified prerequisite chain".
4. If prerequisite data is passed (`prerequisites={skill: [skills]}`), each missing prerequisite is moved in front of the skill that needs it, and a missing prerequisite outside the career's lists is added as a "Prerequisite" step. Cycles cannot create duplicates.
5. Each skill appears once. The same career always produces the same roadmap.

**Prerequisites.** The dataset contains no verified prerequisite relationships, so `KNOWN_PREREQUISITES` is empty and every step says "Prerequisites: none recorded in the dataset." No prerequisite was invented. The ordering code is tested with injected prerequisites, so a verified source can be added later without changing the page.

**Why it matters.** Built only from data: whether the skill is required or optional for the career, and how many careers require or list it.

## How resources are selected

- From `data/raw/resources.csv` through `ResourceCatalog.for_skill()`, beginner level first.
- A resource already chosen for an earlier step is skipped when another exists; otherwise the step says it is the same resource as step N.
- A skill without a resource says "No learning resource for this skill in the catalogue yet."
- Each resource shows the free or paid flag and the link-check status recorded in the dataset (`http_checked` on 2026-10-14 for 104 of 114 links). No URL, duration, certificate or outcome is generated.
- Today every skill has exactly one resource and no URL repeats, so there are no alternatives to rotate yet.

## Progress, completion and mastery

- Status is set by the learner only. Opening a resource does not change it.
- Completion percentage = completed steps / roadmap steps × 100, for that career only. With no steps it is not shown.
- **Completing a step is not mastery.** A skill counts in the skill gap, the score and the recommendations only after the learner clicks "I have learned this skill" and then confirms. Confirming adds the skill to the profile; the existing pipeline recalculates everything on the next run. The step's saved status is kept and listed as "Saved statuses kept for skills no longer in this plan".
- Nothing in the app verifies that a learner can use a skill.

## How progress is stored

| Place | Content | Lifetime |
|---|---|---|
| Streamlit session state | `{career_id: {skill: "in_progress" or "completed"}}` | Until the tab closes |
| Page address | `?progress=C001:git=c,sql=p;C009:git=p` (career ids, skill names, status codes) | Survives a refresh of the same address |
| Session file (download) | Profile, feedback and roadmaps, JSON version 2 | As long as the learner keeps the file |

- Progress per career is separate. Marking a career Not for me, or removing it from Interested, never deletes its roadmap. Only the explicit delete does.
- Saved data is cleaned on every load: unknown careers, skills no longer in the catalogue, unknown statuses and malformed structures are dropped (`clean_progress()`), and the address value is limited to 3,000 characters.
- "Start a new assessment" clears answers, lists and roadmaps.

**Limits.** There are no accounts. Progress does not survive opening the app from a fresh link, does not sync across browsers or devices, and is not kept on the server. Anyone given the page address can see the career ids, skill names and statuses in it, and the address stays in browser history. No answers, names or contact details are stored. Because there are no accounts, one user's progress cannot reach another user except by sharing the address.

## Deployment and performance

- No new dependency and no database. Works on Streamlit Community Cloud as before.
- Building one roadmap took 1.3 ms on average over the 50 careers in the development container (one run, Python 3.13.16).

## Interfaces for a future T-Career API

```python
build_roadmap(profile: dict | None, career_id: str, catalog, progress: dict | None = None,
              prerequisites: dict | None = None) -> dict            # raises RoadmapError, ProfileValidationError
set_step_status(progress: dict, career_id: str, skill: str, status: str) -> dict
delete_roadmap(progress: dict, career_id: str) -> dict
add_skill_to_profile(profile: dict, skill: str, catalog) -> dict     # call only after the learner confirms
clean_progress(raw, catalog) -> (dict, list[str])
progress_summary(steps: list) -> dict
```

Assumptions an API must keep:

- Progress belongs to one authenticated learner; T-Career must key it by user id and never return it to anyone else.
- Statuses are exactly `not_started`, `in_progress`, `completed`; not started is the default and is not stored.
- Progress is keyed by career id and canonical skill name, so renamed skills must be migrated or they are dropped by `clean_progress()`.
- The gap comes from `analyze_skill_gap()`; a completed step must never be treated as an acquired skill.
- The API should replace the page address and file with server storage after authentication exists.

## Risks report

| Risk | Effect | Mitigation now | Future improvement |
|---|---|---|---|
| No verified prerequisites | Order may not match how a skill is best learned | Labelled as a suggested order; code accepts verified data | Add prerequisites from a curated, cited source |
| One resource per skill | No choice when a resource does not suit the learner | Shows provider, level, cost flag and link status | Add alternative resources per skill |
| Links can break after 2026-10-14 | A step may point to a dead page | Link-check status shown; `src/data/url_checker.py` can recheck | Scheduled link checks |
| Completion mistaken for mastery | Learner or reviewer over-reads progress | Notes on the page; skill added only after confirmation | Assessments or evidence of skill |
| Self-reported skills | A confirmed skill may not be real | Same as all profile input | Verified credentials |
| Address-based storage | Shared links reveal progress; lost on a fresh link | Only ids, skill names and statuses; file download | Accounts and server storage in T-Career |
| Dataset changes | Saved records refer to removed careers or skills | `clean_progress()` drops them safely | Versioned migrations |
| Demand-based ordering | Common skills first may not suit every learner | Explained on the page; required before optional | User study of the order |

Not implemented and not claimed: accounts, server-side storage, sync across devices, verified prerequisites, course durations, certificates, and any check of skill mastery.
