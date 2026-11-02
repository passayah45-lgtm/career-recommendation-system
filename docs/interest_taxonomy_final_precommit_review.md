# Interest taxonomy v1.4.0: final pre-commit review

Review date: 3 November 2026. Base: `main` at b861aed, local and GitHub in sync. Scope: the uncommitted v1.4.0 implementation after the M1 and M2 fixes. Nothing was committed, pushed, merged or deployed.

Labels used in this document:
- **[Verified]** checked by running code or tests during this review.
- **[Recommendation]** a proposed action, not implemented.
- **[Unverified]** an assumption not checked here.
- **[Pending lecturer]** needs the lecturer's decision.

## 1. Executive summary

- **[Verified]** All tests pass:
  - Python 3.13.16: 673 passed, 0 failed, 0 skipped.
  - Python 3.12.3, the CI version, in a clean environment built from `requirements.txt`: 672 passed, 0 failed, 1 skipped. The skipped test needs the optional `xgboost` package, which CI does not install either.
- **[Verified]** Lint (CI rules F, E9) passes. Data validation reports 0 errors. Both CI reproduction checks match.
- **[Verified]** Frozen integrity holds:
  - the frozen reports, the eval64 inputs and the v1.2.0 and v1.4.0 snapshots match their hashes.
  - eval64_v1 and the v1.4.0 evaluation both reproduce exactly.
  - nothing frozen changed.
- **[Verified]** The scoring weights, ranking, tie-break and engine files are unchanged.
- **Commit readiness:** no item blocks a commit to a separate review branch.
- **Deployment readiness:** v1.4.0 is **not ready for `main`**, because a push to `main` redeploys the live app. Lecturer feedback, a fair evaluation, and a user-facing notice about the interest change are still missing.
- **Pillow:** the advisories exist before v1.4.0 and are not caused by it. Fixing them needs a separate Streamlit upgrade. A trial of that upgrade passed every test under Python 3.12 but was not applied.

## 2. Phase 1: M1 and M2 resolution

| ID | Resolution | Evidence |
|---|---|---|
| M1 | `check_outputs` no longer drops `live_catalogue_matches_frozen` silently. While the live catalogue is v1.3.0 the field is compared like any other. After that, the saved value must be exactly `true` and the recomputed value exactly `false`, otherwise the edit is reported. Every other field is compared exactly | [Verified] `--check reports/evaluation_64` reproduces. A scratch copy with the saved value set to `false` is reported. Unit tests cover the valid pair, four tampering or drift cases, and the v1.3.0 case |
| M2 | `tests/test_frozen_report_hashes.py` pins the SHA-256 of all 35 published files in `reports/evaluation_64/`, `reports/evaluation_64_sensitivity/` and `reports/evaluation_64_review_design/`, taken from commit b861aed. Another test fails if a tracked file appears there without a pin. None of these tests need the labels, so they run in public CI | [Verified] All pins match. These tests ran and passed under both Python versions |

## 3. Remaining findings and classification

Classes:
- **Review branch:** must fix before committing to a review branch.
- **Before main:** must fix before deployment to `main`.
- **After lecturer:** can wait until after lecturer feedback.
- **Later release:** can wait until a later release.

| # | Finding | Status | Class |
|---|---|---|---|
| 1 | Pillow 12.3.0 advisories (39, via Streamlit) | Exist before v1.4.0. Fix identified and trial-tested, not applied (section 4) | Later release, as a separate dependency change. Recommended soon, independent of v1.4.0 |
| 2 | Python 3.12 compatibility | [Verified] Full suite, validation and both CI checks pass under 3.12.3 | Resolved |
| 3 | French draft translations | Every term has a draft, marked as such in the code. Drafts are accepted as input and not displayed. No qualified review yet | After lecturer (decision 5). Must be reviewed before the drafts are shown to learners |
| 4 | ResourceWarnings | [Verified] The 5 warnings from new v1.4.0 tests are fixed with context managers, without changing any assertion. 4 remain, in files outside this change (`test_eval64_review.py` lines 301, 315, 330 and `test_url_checker.py` line 128) | Later release, for the remaining 4 |
| 5 | Documentation inconsistencies | Factual errors in files touched by v1.4.0 corrected (section 6). Historical research documents describing the 50-career study left as written | Resolved for v1.4.0 files. Later release for the historical documents, if wanted |
| 6 | Migration and compatibility risks | Old sessions and API inputs load. Rankings change for every learner. 5 retired names are not scored. 8 new interests cannot be reached from old names | Before main: in-app notice that interest names changed, and a note to T-Career integrators to send the new names |
| 7 | Category exposure changes | Under migrated old profiles: Data and AI top-5 share 22.7% to 25.2%, Law 3.8% to 1.4%, Engineering 10.6% to 7.8% | After lecturer, re-measured in eval64_v2. It may reflect migration rather than the taxonomy |
| 8 | Lecturer feedback and evaluation readiness | No lecturer feedback. The old-profile comparison is not a fair test of the new taxonomy | Before main: lecturer decisions and eval64_v2 (section 7) |

No finding blocks a commit to a review branch.

## 4. Dependency review

| Item | Finding |
|---|---|
| Dependency files | `requirements.txt` (pinned: streamlit 1.65.0, pandas 3.0.6, numpy 2.5.4, scikit-learn 1.9.1, plotly 7.1.0, pytest 9.1.1) and `requirements-research.txt` (adds xgboost 3.4.1). There is no lockfile (no poetry, Pipfile, pyproject or uv lock) |
| Pillow path | [Verified] Pillow is not pinned. It comes only through Streamlit. Streamlit 1.65.0 declares `pillow<13,>=7.1.0`, so pip resolves Pillow 12.3.0 |
| Advisories | [Verified] `pip-audit -r requirements.txt` reports 39 advisories, all for Pillow 12.3.0. All are fixed in 13.0.0. No other package is affected |
| Patched 12.x | [Verified] None. PyPI has no Pillow release between 12.3.0 and 13.0.0 |
| Pillow 13 with Streamlit 1.65.0 | **Not compatible.** Streamlit 1.65.0 forbids Pillow 13. Streamlit 1.66.0 also caps it below 13. Streamlit 1.66.1 allows `pillow<14` |
| Trial | [Verified] In a separate Python 3.12 environment with streamlit 1.66.1 and pillow 13.0.0 (all other pins unchanged): `pip check` is clean, `pip-audit` finds no known vulnerabilities, the full suite gives 672 passed and 1 skipped (xgboost), and the evaluation report check matches |
| Not verified | [Unverified] The look and behaviour of the live pages under Streamlit 1.66.1 in a real browser. The Streamlit 1.66 release notes were not reviewed. The behaviour on Community Cloud |
| Exposure | The app accepts no image uploads (session upload is JSON only), which limits practical exposure. [Unverified] whether Streamlit decodes untrusted images anywhere in this app's use |
| Decision | Not applied. It is unrelated to v1.4.0, and it is a framework upgrade that needs a visual check |

**[Recommendation]** Make a separate change that pins `streamlit==1.66.1` and adds `pillow==13.0.0` (or later within the allowed range), checks every page visually, and deploys it independently of v1.4.0. It could go to `main` before v1.4.0, because it does not change scoring or data.

## 5. Python 3.12 compatibility status

| Item | Finding |
|---|---|
| CI version | [Verified] `.github/workflows` uses Python 3.12 on ubuntu-latest. It installs `requirements.txt` only, then runs validation, pytest and two report checks |
| Local 3.12 run | [Verified] A clean Python 3.12.3 environment built from `requirements.txt` plus pytest. Validation: 0 errors. pytest: 672 passed, 1 skipped (xgboost, as in CI). `experiments --check` matches. `ml_sensitivity --check` matches within 0.0005 |
| Difference from CI | [Unverified] Two differences remain. The local run had the withheld eval64 labels, so label-dependent tests ran instead of skipping. CI also runs on GitHub's runner image. Expected public CI result: the label-dependent tests skip (16 marked tests plus the sensitivity module), and the rest should pass as locally |
| Python 3.12 issues | None found. No CI change is needed |

## 6. Documentation review

**Corrected (factual, supported by the implementation):**

| File | Correction |
|---|---|
| `docs/recommendation_algorithm.md` | "each of the 50 careers" became 64 careers (dataset v1.4.0) |
| `docs/recommendation_algorithm.md` | The normalisation rule said interests must belong to "the 20-value interest vocabulary". It now describes the 23-value live vocabulary, the legacy vocabulary for frozen snapshots, and migration |
| `docs/recommendation_algorithm.md` | Weight rationale "42 of 50 careers sit at level 3" became "50 of 64 (42 of the original 50)", counted from the catalogue |
| `docs/recommendation_algorithm.md` | Output example `careers_scored: 50` became 64 |
| `README.md` | Limitation 6 now names both evaluations: 36 profiles in the original study, 111 in eval64_v1 |

**Checked and consistent:**
- The dataset version is 1.4.0 in the manifest, the README, the dataset documentation, the algorithm document, the integration notes and the implementation document.
- Evaluation versions: eval64_v1 is frozen, and `eval_v1.4.0_taxonomy` is the new study.
- Career count 64 and interest counts 23 (current) and 20 (legacy).
- Migration rules are identical in the code, `docs/interest_taxonomy_implementation.md`, `docs/integration_api.md` and `docs/recommendation_algorithm.md`.
- The French names are described as drafts everywhere.

**Left unchanged (historical or outside this change):**
- `docs/deployment_checklist.md` keeps its October verification rows (50 careers, 61.5). A dated v1.4.0 row explains the new values.
- `research/` documents describe the 50-career v1.2.0 study and are historical.
- `docs/skill_roadmap.md` mentions "50 careers" in an algorithm sentence and a timing measurement. It is outside this change, so a later release.
- The audit reports, the lecturer package and the first pre-commit review were not rewritten. The first review received only an appended M1 and M2 resolution section.

**Deployment guidance:** the README says every push to `main` redeploys automatically. This review keeps that as the main deployment risk.

## 7. Evaluation readiness

**Why eval64_v1 stays frozen.** It is the record of how the v1.3.0 system performed against labels written before any engine run. Changing its profiles, labels or reports would remove the baseline every later study is compared with. Its labels also await an independent second review. It is now protected by hashes and by the stricter reproduction check.

**Why the old-profile comparison is not fair to the new taxonomy:**
- The 111 profiles were written in the 20-term vocabulary.
- After mechanical migration, 72 of their 269 interests are retired terms, and 10 profiles keep no interest.
- 8 of the 23 new interests cannot be produced from any old name, so careers carrying them cannot gain interest points.
- The labels were written by an author who knew the v1.3.0 catalogue.

The result (NDCG@5 0.759 to 0.677) measures old-vocabulary input after migration, not the new taxonomy. **[Verified]** These figures come from the saved and reproducible v1.4.0 evaluation outputs.

**[Recommendation] Requirements for eval64_v2:**

| Element | Requirement |
|---|---|
| Profiles | At least 120 new profiles: 12 per category across the 10 categories, so every category reaches the 10-profile level used for indicative category results. Spread across profile types (strong match, career changer, mixed interests, lower education, interests only, no clear fit). Include at least 20 profiles with 6 to 8 interests, to test the soft limit |
| Authors | Written by people other than the project author (for example consenting students), with no personal data. Authors use the interest descriptions as shown in the form |
| Paired design | Each profile author chooses interests twice, independently: from the 23-term list and from the old 20-term list. The same person can then be ranked by v1.3.0 and v1.4.0 |
| Blind labelling | Relevance grades 0 to 3 under the existing rules, by a labeller who has not seen either catalogue's interest assignments or any ranking. Career order shuffled per profile, with profile IDs anonymised |
| Independent reviewer | A second reviewer, not the author, re-grades all listed pairs plus a random sample of unlisted pairs, as in the existing review design. Report weighted kappa per stratum, settle disagreements by a written rule, and freeze labels before any engine run |
| Pre-registration | Written and frozen before running: NDCG@5 primary, with Precision@5, Recall@5, Hit@5 and MRR secondary. Paired profile-level bootstrap (2,000 resamples, fixed seed) for v1.4.0 minus v1.3.0. A minimum difference that matters (for example 0.03 NDCG@5). Category results labelled indicative |
| Diagnostics | Top-5 slot share per category and per career, careers never shown, ties at the rank-5 boundary and ties decided by career ID, and results by number of interests chosen |
| Separation | New folder and version (eval64_v2). eval64_v1 and the v1.4.0 migration study stay frozen |

## 8. Lecturer feedback status

**[Pending lecturer]** No lecturer feedback has been received. The decision checklist in `docs/lecturer_review/lecturer_decision_checklist.md` is blank and was not modified. No approval, comment or signature exists or is implied. Decisions still needed:
1. the 23 terms.
2. the 64 assignments.
3. the 12 provisional careers, especially C057 and C058 (law) and C059 (MIAGE).
4. the RIASEC grouping.
5. the descriptions and French wording.
6. the selection limit.
7. the O*NET validation approach.

## 9. Commit readiness

**[Verified] Ready for a commit to a separate review branch:**
- all tests pass under Python 3.12 and 3.13.
- lint passes.
- no secret, private key or label file is in the change, and the label and key files remain git-ignored.
- frozen material is unchanged and protected.

**[Recommendation]** Use a branch such as `review/interest-taxonomy-v1.4.0`. Community Cloud deploys from `main` only (README, deployment checklist). [Unverified] that no other branch is configured on the Community Cloud dashboard.

## 10. Deployment readiness

**Not ready for `main`.** Before deployment:
1. lecturer decisions on the seven items.
2. eval64_v2, or at least a documented decision to deploy without it.
3. an in-app notice that interest names changed.
4. a note to T-Career integrators.
5. ideally the separate Streamlit and Pillow upgrade first.

Rollback after deployment is straightforward: a `git revert` restores v1.3.0 exactly (the v1.3.0 data equals the frozen `catalog_v1.3.0` copy byte for byte).

## 11. Exact files changed (against b861aed)

**Modified (19):**
- Data: `data/raw/careers.csv` (interests column only), `data/raw/dataset_manifest.json`.
- Code:
  - `pages/1_Career_Assessment.py`
  - `src/data/validation.py`
  - `src/engine/explanations.py`
  - `src/evaluation/independent_64_evaluation.py`
  - `src/services/catalog.py`
  - `src/services/profiles.py`
  - `src/services/recommendations.py`
  - `src/ui/components.py`
- Tests: `tests/test_app.py`, `tests/test_expansion_readiness.py`, `tests/test_recommendations.py`, `tests/test_roadmap.py`.
- Documentation: `README.md`, `docs/dataset_documentation.md`, `docs/deployment_checklist.md`, `docs/integration_api.md`, `docs/recommendation_algorithm.md`.

**Added:**
- `data/evaluation/catalog_v1.4.0/` (5 files)
- `reports/evaluation_v1_4_0/` (4 files)
- `src/data/interest_taxonomy.py`
- `src/evaluation/taxonomy_v140_evaluation.py`
- `tests/test_interest_taxonomy.py`
- `tests/test_taxonomy_v140_evaluation.py`
- `tests/test_frozen_report_hashes.py`
- `docs/interest_taxonomy_implementation.md`
- `docs/interest_taxonomy_precommit_review.md`
- `docs/interest_taxonomy_final_precommit_review.md` (this file)

**Deleted:** none.

**Unchanged and checked:**
- `data/evaluation/catalog_v1.2.0/` and `catalog_v1.3.0/`
- every file under `reports/` except the new `evaluation_v1_4_0/`
- both audit reports and the lecturer package
- `requirements*.txt` and `.github/`
- `src/engine/scoring.py`, `ranking.py`, `matching.py` and `models.py`

Tracked diff: 19 files, +351 and -133 lines.

Changes made in this phase:
- the M1 fix and M2 tests.
- closing files in the two new test files (no assertion changed).
- the five documentation corrections in section 6.
- the appended resolution section in the first review.
- this document.

## 12. Recommended next action

1. **[Recommendation]** If you want the work saved on GitHub, authorize a commit and push to a new branch (for example `review/interest-taxonomy-v1.4.0`), not to `main`.
2. **[Pending lecturer]** Send the lecturer review package and collect the seven decisions.
3. **[Recommendation]** Make the Streamlit 1.66.1 and Pillow 13 upgrade as its own change, with a visual check of every page.
4. **[Recommendation]** Plan and pre-register eval64_v2 (section 7).
5. Deploy v1.4.0 to `main` only after items 2 and 4, plus the in-app notice and the T-Career note.

Nothing has been committed, pushed, merged or deployed.

## Owner decision after this review (3 November 2026)

The project owner authorized committing to `main` and deploying v1.4.0. Of the "before main" items in section 10, these were done before the commit: the in-app notice (shown above the interest list) and the integrator notice (`docs/integration_api.md`). Still open: lecturer decisions and eval64_v2. The Streamlit and Pillow upgrade was not included, because it is a separate dependency change.
