# Interest taxonomy v1.4.0: pre-commit review

Review date: 3 November 2026. Scope: the uncommitted v1.4.0 implementation on `main` (base commit b861aed). **Audit only.** No production file, frozen file or report was changed during this review. This document is the only file written by the review. Nothing was committed, pushed or deployed.

Status of the implementation: owner-authorized, pending lecturer feedback. No lecturer approval exists.

## Summary of findings

| Severity | Count | Issues |
|---|---|---|
| Critical | 0 | None |
| High | 2 | H1 pushing to `main` redeploys the live app. H2 the evaluation neither supports nor refutes the new taxonomy |
| Medium | 5 | M1 one frozen-check field is skipped. M2 eval64 reproduction is not checked in public CI. M3 old saved sessions and API clients get different, often lower, rankings. M4 pre-existing Pillow advisories. M5 exposure shifts between categories |
| Low | 7 | L1 to L7 (section 8) |

**Recommendation in one line:** the code is ready to commit, but do not push it to `main` yet. Either keep it on a separate branch, or wait for the lecturer's feedback and a fair evaluation, because a push to `main` changes the live application.

## 1. Git status

| Check | Result |
|---|---|
| Branch | `main` |
| Local and GitHub | Both at b861aed (fetched during the review) |
| Staged files | None |
| Deleted files | None |
| Frozen data, frozen reports, audit reports, lecturer package | No changes (`git diff` is empty for `data/evaluation/`, `reports/`, `docs/skills_interests_audit.md`, `docs/interest_taxonomy_second_review.md`, `docs/lecturer_review/`) |
| Engine scoring and ranking files | No changes (`src/engine/scoring.py`, `ranking.py`, `matching.py`, `models.py`) |
| Dependencies and CI | No changes (`requirements*.txt`, `.github/`, `.gitignore`, `.gitattributes`) |
| Size | 19 tracked files modified (+331, -128 lines), 7 new paths |

All changes belong to the v1.4.0 implementation. No unrelated change was found.

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

**Added (7 paths, 14 files):**
- `data/evaluation/catalog_v1.4.0/` (5 files: careers.csv, resources.csv, skill_aliases.csv, dataset_manifest.json, evaluation_manifest.json)
- `reports/evaluation_v1_4_0/` (4 files: taxonomy_evaluation_summary.json, metric_comparison.csv, category_exposure.csv, profile_interest_migration.csv)
- `src/data/interest_taxonomy.py`
- `src/evaluation/taxonomy_v140_evaluation.py`
- `tests/test_interest_taxonomy.py`
- `tests/test_taxonomy_v140_evaluation.py`
- `docs/interest_taxonomy_implementation.md`

## 2. Security findings

The full diff and every new file were scanned. Secret values are not reproduced here.

| Check | Result |
|---|---|
| API keys, AWS credentials, GitHub tokens, private keys | None found |
| Passwords | None. One match is the interest example "Finding a weak password policy and fixing it" |
| "token" matches | All refer to the existing `check_token_list` function |
| Personal information (names, emails, roll number) | None in the diff or new files |
| Private anonymisation key | Not in the diff, still git-ignored (`.gitignore` line 13) |
| Relevance labels | Not copied, not staged, still git-ignored (`.gitignore` line 18). The label-dependent per-pair outputs of eval64 remain ignored |
| New evaluation outputs | Aggregate figures only. No grade, career ranking or per-pair column. The per-profile file lists only public profile fields (ID, category, old and new interests, counts) |
| Label file hash | The new snapshot manifest records the SHA-256 of `relevance_labels.csv`. The same value is already public in the committed eval64 manifest. A hash of a long text file reveals nothing usable |
| Unsafe file handling | No new file input from users. Session upload code is unchanged. Interest input is still limited to lists of up to 200 text items before the new resolver runs. The evaluation's `freeze` refuses to overwrite an existing snapshot |
| Authentication and authorization | The application has no accounts, and none were added or changed |
| Dependencies | No dependency changed. `pip-audit` on `requirements.txt` reports 39 advisories, all for Pillow 12.3.0, a transitive dependency of Streamlit (fixed in 13.0.0). This existed before v1.4.0 (M4) |

No security issue is introduced by v1.4.0.

## 3. Frozen evaluation integrity (M1, M2)

### What changed

- **File:** `src/evaluation/independent_64_evaluation.py`, function `check_outputs`.
- **Used by:**
  - `tests/test_eval64.py::test_saved_outputs_reproduce_exactly`
  - `tests/test_eval64_sensitivity.py::test_experiments_leave_the_primary_evaluation_untouched`
  - the `--check` command.
- **Field:** `data.live_catalogue_matches_frozen` in `reports/evaluation_64/evaluation_summary.json`.
- **Change:** when the live dataset version differs from the frozen version (1.3.0), that one field is removed from both the saved and the recomputed summary before they are compared. No test file was changed for this, and no frozen file was touched.

### Why it was necessary

The field is not a metric. When the summary is built, it records whether the live catalogue in `data/raw/` was byte-identical to the frozen v1.3.0 copy. That was true on the day of freezing and is saved as `true`. Once the live catalogue became v1.4.0, recomputing it gives `false`. The check then reported "evaluation_summary.json: differs" even though every metric was identical.

### Does it weaken protection?

Slightly, and only for that field.
- Every metric, interval, count, label tally, configuration value and the SHA-256 block are still compared exactly.
- All ten CSV outputs are still compared byte for byte.
- Re-running `--check` during this review reproduced every output.
- The weakness: while the live catalogue is not v1.3.0, a manual edit of that single saved boolean would not be detected by `check_outputs`. Git would still show such an edit as a modification of a tracked file.

### Independent verification

The frozen evidence can still be verified without relying on the changed function:
- `verify_frozen()` checks the SHA-256 of all six frozen eval64 input files against `evaluation_manifest.json`. Result: no changes.
- `verify_snapshot()` checks the original 50-career snapshot (v1.2.0). Result: no changes.
- `tests/test_eval64.py` pins the SHA-256 of the five original 50-career reports and `labelled_profiles.json`. They pass.
- The CI commands `experiments --check` and `ml_sensitivity --check` pass.
- Condition A of the new evaluation recomputes eval64_v1 independently and matches every frozen mean exactly.
- `git diff` shows no change under `reports/evaluation_64/`.

### Related gap (M2, existed before v1.4.0)

Both tests that call `check_outputs` need the withheld labels, so they are skipped in public CI. On GitHub, the eval64 reports are therefore protected only by Git history. No test pins their SHA-256 the way the original 50-career reports are pinned.

### Safer alternative (recommended, not implemented)

1. Replace the silent removal with an explicit expectation. When the live version differs from the frozen one, require the saved field to be exactly `true` (its frozen value) and the recomputed field to be exactly `false`. Only then remove it before comparing. Any edit to the saved value would then fail.
2. Add a test that pins the SHA-256 of every published file in `reports/evaluation_64/` and `reports/evaluation_64_sensitivity/`. That would run in public CI without needing the labels, as is already done for the original reports.

Both changes touch only code and tests, not frozen files. **Waiting for your approval before implementing them.**

## 4. Test results

| Item | Result |
|---|---|
| Full suite (Python 3.13, labels present) | 630 collected, 630 passed, 0 failed, 0 skipped |
| Expected in public CI (labels withheld) | 16 label-dependent tests skip (9 in test_eval64, 5 in test_eval64_review, 2 in test_taxonomy_v140_evaluation), plus the whole sensitivity module |
| Lint (CI rules F, E9) | All checks passed |
| CI commands | Data validation 0 errors (12 existing "no source URL" warnings). Evaluation report check matches. ML sensitivity check matches within 0.0005 |
| Warnings | 10 ResourceWarnings (unclosed files in tests). 5 come from the new test files (L2) and 5 existed before |
| Python 3.12 (CI version) | Not run locally: the 3.12 interpreter here has no project packages. No 3.13-only syntax was used (L7) |

### Modified tests: were assertions weakened?

Five old assertion lines were replaced. 19 assertion lines were added.

| Test | Change | Assessment |
|---|---|---|
| test_app worked example, model rankings, compatibility score | 61.5 became 65.7 and 41.7 became 44.2. The profile now uses the new interest names | Same strictness. The new value was checked by hand: C001 matches 2 of 3 interests, 44.0 + 0 + 16.7 + 5.0 = 65.7 |
| test_app assessment form | Ticks a checkbox instead of a dropdown | Stronger: also asserts the saved interests |
| test_roadmap fit | 61.5 became 65.7 | Same strictness |
| test_recommendations worked example | New names and values. Fifth place is now C060 Economist (44.2) instead of C006 | Same strictness. Old names are covered by a new test that requires identical scores for old and new names |
| test_recommendations schema | Two new output keys added to the exact key set | Same strictness |
| test_expansion_readiness original 50 | Compares every field except interests | **Narrower by design**, because the interests change was authorized. Covered by two new tests: all non-interest fields of all 64 careers match v1.3.0, and all interests match the second review's section C exactly |
| test_expansion_readiness new-career fixture | Interests changed to three current terms | Same strictness. The test is about count enforcement |

No test was removed or skipped, and no tolerance was loosened.

## 5. Evaluation interpretation

### Results

| Condition | NDCG@5 | Hit@5 | Recall@5 |
|---|---|---|---|
| A: v1.3.0 catalogue, original profiles (= frozen eval64_v1) | 0.759 | 1.000 | 0.901 |
| A2: v1.3.0 catalogue, retired old terms removed from profiles | 0.730 | 0.931 | 0.860 |
| B: v1.4.0 catalogue, profiles migrated | 0.677 | 0.911 | 0.817 |

- **B minus A (NDCG@5):** -0.082, 95% CI -0.121 to -0.044 (paired, 111 profiles). 24 profiles improve, 50 get worse and 37 are unchanged. 105 of 111 profiles get a different top 5.
- **Retired names.** The profiles hold 269 interests. 72 are retired terms: technology 30, engineering 16, design 12, problem solving 9, communication 5. Removing them alone costs 0.029 (A2 minus A). After migration, 10 profiles have no interest left, so their interest component scores 0.
- **New terms.** 8 of the 23 new interests cannot be produced from any old name: computer systems, tools, both design terms, persuading, communities, laws and money. 12 careers have only one reachable interest. B minus A2 is -0.053 (CI -0.086 to -0.022), and the loss concentrates where those terms matter.
- **Category effects (NDCG@5, A to B, 10 to 14 profiles each, indicative only):**
  - Law 0.709 to 0.443
  - Design 0.735 to 0.557
  - Cybersecurity 0.610 to 0.483
  - Engineering 0.824 to 0.714
  - Social Sciences 0.812 to 0.718
  - Software, Education and Business are almost unchanged.
- **Top-5 share:**
  - Data and AI rises from 22.7% to 25.2% (M5).
  - Law falls from 3.8% to 1.4%.
  - Engineering falls from 10.6% to 7.8%.

### Is the comparison fair?

No, not as a comparison of the two taxonomies. The profiles were written in the old vocabulary, and the labels were written by an author who knew the v1.3.0 catalogue. Condition B measures something narrower and still useful: how old-vocabulary input is ranked after migration. That is exactly the situation of old saved sessions and old API clients.

### Does it support deployment?

No. The evidence shows neither that v1.4.0 is better nor that it is worse for learners who choose from the 23 interests. It does show that old-vocabulary input gets lower agreement with the labels. Combined with the missing lecturer feedback, the results do not support replacing the live version yet.

### Recommended fair evaluation (eval64_v2)

1. **New profiles.** At least 111, balanced across the 10 categories and profile types, written by someone other than the author (for example volunteer students, with consent and no personal data).
2. **Both vocabularies.** Each profile author picks interests in the new form from the 23 described terms, and separately from the old 20-term list, without seeing either catalogue. Both versions can then be ranked for the same person, in a paired comparison.
3. **Blind labels.** Relevance labels by a reviewer who has not seen either catalogue's interest assignments, using the existing grading rules. Report agreement with a second reviewer.
4. **Pre-registration.** State before running: NDCG@5 as the primary metric, a paired bootstrap, the minimum difference that matters, category exposure, and tie diagnostics.
5. **Selection limit.** Include profiles that choose 6 to 8 interests, to test the soft limit.
6. **Separation.** Keep eval64_v1 and the v1.4.0 migration study frozen alongside it.

## 6. Catalogue and migration findings

| Check | Result |
|---|---|
| 64 careers present, same IDs | Yes |
| Exactly three interests per career | Yes, all 64, enforced by validation for taxonomy 2.0 |
| IDs, titles, categories, skills and all other fields | Byte-identical to v1.3.0 except the interests column (checked independently against HEAD). CRLF line endings kept |
| Assignments | Equal to the second review's section C for all 64 (test) |
| 12 provisional careers | Listed in `docs/interest_taxonomy_implementation.md` and in the lecturer package |
| Old names | 15 migrate through one table that follows the first audit's section 7 defaults. Behaviour is the same for the form, session files and API input |
| Retired names | communication, design, engineering, problem solving and technology are never scored or guessed. All five are reported to the learner and in the API |
| Frozen snapshots | Keep the old vocabulary and never migrate (test) |
| Saved sessions | Version 1 and version 2 files with old names load. The form ticks migrated interests and names the retired ones |
| API | Accepts the full name, the stored form, any capitalisation and the draft French names. Returns stored forms plus full names |
| French | Every term has a draft name, marked "DRAFT translations ... not yet reviewed" in the code. Drafts are accepted as input, not shown in the interface (test) |
| RIASEC | Used only in the taxonomy data and the form layout. Not referenced in `src/engine` or `src/services` |

### Recommendation engine integrity

- `src/engine/scoring.py`, `ranking.py`, `matching.py` and `models.py` are unchanged.
- The weights remain 0.55, 0.15, 0.25 and 0.05 (test).
- The interest value is still matched interests divided by the career's listed interests (test).
- The sort key and the career-ID tie-break are unchanged.
- `src/engine/explanations.py` changed only the text of the interest reason: it shows full names in quotes. It affects no number. For the old vocabulary the text is unchanged.

## 7. Deployment risks

| Question | Finding |
|---|---|
| Does a push to `main` deploy? | Yes. README: "Every push to the main branch redeploys the app automatically within a few minutes". The live app (https://t-career-recommendation-2026.streamlit.app) was deployed from `main` |
| Is the app technically ready? | Tests, lint, data validation and a local headless run of the assessment page all pass |
| Is v1.4.0 appropriate for the live app now? | Not yet: lecturer feedback is missing, and the evaluation does not support the change (section 5) |
| Will existing users see changes? | Yes. Every learner's scores change, because every career's interests changed. Old saved sessions keep working but may rank lower until interests are reselected. Learners who chose only retired terms lose all interest points. |
| API clients (T-Career) | Inputs keep working. Retired names are reported in the response, and rankings differ. Clients should move to the new names |
| Rollback | Straightforward: `git revert` of the commit restores the v1.3.0 data and code. The restored raw files would be byte-identical to the frozen `catalog_v1.3.0` copy. No migration of stored data is needed, because the app stores nothing on the server |

## 8. Issue list

| ID | Severity | Issue | Recommended action |
|---|---|---|---|
| H1 | High | Pushing to `main` redeploys the public app with an unapproved taxonomy whose evaluation does not support deployment | Do not push to `main` yet. Commit to a separate branch (for example `interest-taxonomy-v1.4.0`), which Community Cloud does not deploy, or wait |
| H2 | High | The before-and-after comparison is confounded by migration (72 retired interests, 10 profiles with none, 8 unreachable terms) | Report it only as an old-input compatibility result. Run eval64_v2 (section 5) before any claim about the taxonomy |
| M1 | Medium | `check_outputs` silently skips one environmental field when the live version differs | Explicit-expectation check (section 3). Awaiting approval |
| M2 | Medium | eval64 report reproduction is skipped in public CI (existed before v1.4.0) | Pin SHA-256 values of the published eval64 reports. Awaiting approval |
| M3 | Medium | Old sessions and API clients get different, often lower, rankings | Keep the migration notes. Tell T-Career to send new names. Announce the change in the app before going live |
| M4 | Medium | Pillow 12.3.0 (via Streamlit) has 39 advisories, fixed in 13.0.0. Existed before v1.4.0. Low exposure: the app accepts no image uploads | Separate task: pin a fixed Pillow version compatible with Streamlit 1.65 and run the full suite |
| M5 | Medium | Top-5 share shifts under migrated profiles: Data and AI 22.7% to 25.2%, Law 3.8% to 1.4%, Engineering 10.6% to 7.8% | Re-check exposure in eval64_v2. It may reflect migration rather than the taxonomy |
| L1 | Low | French names are unreviewed drafts (accepted as input, not displayed) | Review by a French speaker before display |
| L2 | Low | 5 ResourceWarnings from unclosed files in the new tests | Use `with open(...)` in those tests |
| L3 | Low | The labels file hash is republished in the v1.4.0 manifest (already public) | None needed |
| L4 | Low | The ML comparison models (trained on v1.2.0) now see careers that all have three interests. Their features are vocabulary-independent shares and counts | Note in the analytics documentation if the models are retrained |
| L5 | Low | A live folder whose manifest lost the `interest_taxonomy` field would fall back to the old vocabulary and fail validation loudly | Safe failure. None needed |
| L6 | Low | `docs/recommendation_algorithm.md` still shows `careers_scored: 50` in its output example (existed before v1.4.0) | Correct in a documentation pass |
| L7 | Low | The suite was run on Python 3.13, while CI uses 3.12 | CI will confirm on push. No version-specific syntax was used |

## 9. Recommended next actions

1. Decide on the safer frozen-check alternative (M1, M2). It needs your approval.
2. If you want the work saved on GitHub now, commit it to a separate branch rather than `main`, so the live app stays on v1.3.0.
3. Send the lecturer review package and wait for the seven decisions, above all the 12 provisional careers, the law and MIAGE assignments, and the French wording.
4. Plan eval64_v2 with profiles written for the 23-interest taxonomy (section 5) before claiming any improvement.
5. Before any push to `main`: add an in-app notice that interest names changed, and inform T-Career integrators.
6. Handle the Pillow advisories as a separate dependency task.

Nothing has been committed, pushed, deployed or changed in production during this review.

## Resolution of M1 and M2 (3 November 2026, owner-approved)

| ID | Change | Verification |
|---|---|---|
| M1 | `check_outputs` no longer drops `live_catalogue_matches_frozen` silently. While the live catalogue is v1.3.0 the field is compared as before. After that, the saved value must be exactly `true` and the recomputed value exactly `false`, otherwise the check reports it. Only then is the field set aside, and every other field is compared exactly | `--check reports/evaluation_64` matches. On a scratch copy with the saved value changed to `false`, the check reports the edit. Unit tests cover the expected pair, four tampering or drift cases, and the v1.3.0 case |
| M2 | New `tests/test_frozen_report_hashes.py` pins the SHA-256 of all 35 published files in the three eval64 report folders, taken from commit b861aed. A second test fails if a new tracked file appears in those folders without a pin. These tests need no labels, so they run in public CI | All pins match. No report file was changed |

No frozen file, report or snapshot was modified by these fixes.
