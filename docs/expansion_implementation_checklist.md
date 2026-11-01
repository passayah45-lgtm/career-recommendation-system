# Catalogue expansion: preparation and checklist

Prepared on 1 November 2026, starting from commit c71b445. It follows `docs/african_career_expansion_audit.md`. **No career, skill, resource, alias or category was added.** The live catalogue still holds the original 50 careers, 114 skills and 114 resources.

## 1. How the original 50-career evaluation stays separate

| Item | Original evaluation (frozen) | Expanded catalogue (future) |
|---|---|---|
| Data | `data/evaluation/catalog_v1.2.0/` (exact copies of `careers.csv`, `resources.csv` and `skill_aliases.csv` at c71b445) | `data/raw/` |
| Integrity | SHA-256 of each file in `data/evaluation/catalog_v1.2.0/dataset_manifest.json`; checked by `verify_snapshot()` and by tests | Counts in `data/raw/dataset_manifest.json`, enforced by the validator |
| Loaded by | `src/evaluation/snapshot.py` (`load_evaluation_catalog()`), the default in all five evaluation scripts | `load_catalog()` (app, services) |
| Categories in reports | `EVALUATION_CATEGORIES` (the original 8), fixed | `CATEGORIES` in `src/data/validation.py` |
| Labels | 36 profiles in `data/evaluation/labelled_profiles.json`, written for the 50 careers | New profile set needed (not created) |
| Reports | `reports/evaluation_results.json`, `research_results.json`, `ml_results.json`, `ml_interpretation.json`, `ml_sensitivity.json`, all unchanged | New files with new names, for example `reports/evaluation_results_v2.json` |
| Live model comparison | Models are trained on the snapshot, because labels exist only for its 50 careers | The same models rank every live career; new careers are never treated as negatives |

Rules:

1. Never edit the files in `data/evaluation/catalog_v1.2.0/`. Any change fails `tests/test_expansion_readiness.py`.
2. Never overwrite the five saved reports with results computed on the expanded catalogue.
3. Label any 64-career result as a new study, with its own profiles, labels and report files.

## 2. What changed in this preparation phase

| Area | Files | Change |
|---|---|---|
| Evaluation snapshot | `data/evaluation/catalog_v1.2.0/*` (new), `src/evaluation/snapshot.py` (new) | Frozen copy of the 50-career data with SHA-256 manifest and a loader that refuses a modified copy |
| Evaluation scripts | `src/evaluation/experiments.py`, `research_experiments.py`, `ml_experiments.py`, `ml_sensitivity.py`, `ml_interpretation.py` | Load the snapshot by default; `experiments.py` reports per category from the fixed original 8 |
| Live comparison | `src/ui/state.py`, `src/ml/comparison.py`, `src/ui/model_rankings.py` | Trains on the snapshot and records how many careers training used; the text shows the live career count and names the original 50-career catalogue |
| Validation | `src/data/validation.py`, `src/services/catalog.py`, `data/raw/dataset_manifest.json` (new) | Expected career, skill and resource counts come from the folder's manifest (50, 114, 114 today). A malformed manifest or any count mismatch is an error. Without a manifest the old fixed count of 50 applies. New rule: aliases whose accent-folded forms collide are rejected. `PLANNED_CATEGORIES` lists Law and Social Sciences, which are **not** yet allowed |
| French input | `src/data/preprocessing.py` | `fold_accents()` (Unicode NFKD, combining marks removed) inside `clean_skill_text()`. Alias lookup tries the exact text, then the folded text, then folded alias keys |
| Colors | `src/ui/theme.py`, `pages/5_Analytics.py` | `CATEGORY_COLORS` by name (original 8 colors unchanged, plus Law and Social Sciences) and `category_color()` with a neutral fallback, so an unexpected category can never break the chart |
| Live counts in the UI | `home.py`, `pages/5_Analytics.py` | Home shows the number of categories actually used; the offline-results caption reads profile and career counts from `ml_results.json` and says it does not cover later careers |
| Tests | 12 existing test files and 2 new test files | Live-catalogue counts come from the manifest; evaluation tests use the snapshot; new tests below |

## 3. Implementation checklist (after approval)

**Decisions first**

- [ ] Lecturer confirms the 14 titles, including the open decisions in section 4.
- [ ] Lecturer approves Law and Social Sciences.

**Code (already prepared, switch on when approved)**

- [ ] Move Law and Social Sciences from `PLANNED_CATEGORIES` into `CATEGORIES` in `src/data/validation.py`.
- [ ] Check that every category has a color: `tests/test_expansion_readiness.py` does this.
- [ ] Optionally add interest terms. This changes the assessment form, so it needs a separate decision.

**Data, batch 1 (7 careers)**

- [ ] For each new skill, add one resource to `data/raw/resources.csv` (R115 onwards), with a real URL, provider, level and verification status.
- [ ] Run `python -m src.data.url_checker` on the new links.
- [ ] Add the career rows (C051 onwards) to `data/raw/careers.csv`, with O*NET code and URL only when verified.
- [ ] Update `data/raw/dataset_manifest.json` (careers, skills, resources) in the same change.
- [ ] Add aliases, including French forms, to `data/raw/skill_aliases.csv`.
- [ ] Run `python -m src.data.validation`, then `python -m pytest -q`, then the four `--check` commands. All four must still match.

**Data, batch 2 (refined careers)**

- [ ] Repeat the batch 1 steps. Law resources must be jurisdiction-specific and say so in `notes`.

**After the data**

- [ ] Update `docs/dataset_documentation.md`, `README.md`, `research/methodology.md` and `research/data/onet_mapping_audit.csv`.
- [ ] Write new labelled profiles for the new sectors, ideally labelled by independent reviewers.
- [ ] Run a separate 64-career evaluation into new report files.
- [ ] Check the app at desktop and phone width: home counts, Explorer filters, Analytics category chart, Recommendations, Roadmap.

The target after both batches is 64 careers, 158 skills and 158 resources, if the proposed skill lists are approved unchanged.

## 4. Decisions that need lecturer approval

1. **Geological Engineer:** keep as a distinct career (engineering geology and site investigation), or merge into Mining or Geotechnical Engineer. O*NET combines mining and geological engineering in one occupation (17-2151.00).
2. **Operations Manager:** confirm that "Business Administration Specialist" means an operations or general management job. Business administration is a degree field, not an occupation.
3. **Chemical Laboratory Technician:** confirm whether "Laboratory Technician" means a chemical or industrial laboratory (mining assay, water, quality control) or a medical laboratory. The medical version would duplicate C042 Medical Laboratory Technologist.
4. **Building Construction Engineer:** confirm this title in place of "Building Engineer".
5. **Law titles:** the wording for the private-law and public-law careers, and whether OHADA business law (francophone Africa only) is acceptable as a skill.
6. **Information Systems Manager:** confirm this title for the MIAGE request, with MIAGE recorded as a training route.
7. **Categories:** add Law and Social Sciences (recommended), or also add Natural Sciences for Geophysicist and Chemical Laboratory Technician.
8. **Skill lists and education levels:** all are estimates in the audit and need review.

## 5. Risks

| Type | Risk | Mitigation in place or planned |
|---|---|---|
| Technical | A new category without a color breaks Analytics | Fixed: name-based colors with fallback; test covers planned categories |
| Technical | Count assumptions spread across code and tests | Counts moved to the manifest; tests read it; validator enforces it |
| Technical | Accent folding changes how non-ASCII input is cleaned | ASCII input is unchanged (tests); unknown skills are still reported as typed; colliding folded aliases are rejected |
| Compatibility | The snapshot and the manifest add files that must stay in the repository | Tests fail if either is missing or changed |
| Compatibility | Session files and page-address lists hold career ids only, so new ids work with no format change | None needed |
| Data quality | Duplicate titles (Civil, Electrical, HR) | Validator rejects them; tested for all three |
| Data quality | Near-duplicate careers (Mining, Geological, Geotechnical) | Open decision 1 |
| Evaluation | Results on 50 careers mistaken for results on 64 | Snapshot, separate report names, captions in the app, section 1 rules |
| Evaluation | New careers have no labels and no matching profiles | New labelled profile set before any 64-career claim |
| Evaluation | Live models see new careers they were never trained on | Features describe the match, not the career; models still learned only from 50 careers, as the page states |
| Resource availability | 22 of 44 proposed new skills have no candidate free resource yet | No career is added until all its skills have checked resources (the validator enforces one resource per skill) |
| Resource availability | Some candidates fit only partly or have unconfirmed fees | Record limits in `notes`; confirm before adding |
| Regional relevance | Law and building codes are national; OHADA covers only its member states | Jurisdiction noted per resource; avoid general claims |
| Regional relevance | Occupation sources are mostly US (O*NET) or European (ESCO) | Add ISCO-08 codes; look for African national frameworks |
