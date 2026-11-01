# Independent 64-career evaluation: methodology

Study ID: `eval64_v1`. Catalogue: dataset v1.3.0 (64 careers, 10 categories). Written on 1 November 2026, **before** any relevance label was assigned and before the engine was run on any evaluation profile.

This study is separate from the original 50-career evaluation (`data/evaluation/labelled_profiles.json`, `data/evaluation/catalog_v1.2.0/`, the five reports in `reports/`). Nothing from that study is reused as a result here, and nothing in it is changed.

## 1. Objective

Measure how well the unchanged recommendation engine (weights 0.55, 0.15, 0.25, 0.05) ranks careers that a documented, rule-based judgement marks as relevant, across varied synthetic learner profiles, on the 64-career catalogue.

The study measures agreement with author-written labels. It does **not** measure real-world accuracy, employment outcomes, career success or suitability for regulated professions.

## 2. Sequence

| Stage | What happens | Engine used? |
|---|---|---|
| 1 | Design profiles (`profiles.csv`) | No |
| 2 | Assign relevance labels (`relevance_labels.csv`) under the rules in section 4 | No |
| 3 | Validate both files, then freeze them with SHA-256 values in `evaluation_manifest.json`, together with a byte copy of the v1.3.0 catalogue | No |
| 4 | Run `recommend()` on every profile, full ranking of all 64 careers | Yes |
| 5 to 9 | Metrics, bootstrap intervals, category and coverage analysis, robustness experiments, reports | Yes |

Labels are never edited after stage 3. A correction would create a new labelled version (`eval64_v2`) with its own manifest and reports.

## 3. Learner profiles

- At least 100 synthetic profiles, at least 10 with each of the 10 categories as primary category.
- No personal data. Every profile is invented.
- Fields: `profile_id`, `primary_category`, `profile_type`, `learner_stage`, `education_level` (blank when unknown), `experience_years`, `skills`, `interests`, `learning_goal`, `description`.
- `skills` are written as a learner would type them. They are **not** copied from the catalogue's skill lists. Some are unknown to the catalogue, some are French, some are mixed case.
- `interests` mostly use the 20 terms the interface offers, because the assessment form presents them as a list. A few profiles use other words on purpose.
- `learning_goal` and `experience_years` inform the labels. The engine does not score them (experience is recorded, not weighted).

Profile types:

| Type | Meaning |
|---|---|
| strong_match | Skills and goal point clearly to one occupation |
| incomplete_skills | Correct direction, important skills missing |
| career_change | Experienced in one field, aiming at another |
| transferable_skills | Skills from a different field that partly carry over |
| mixed_interests | Interests or skills span two categories |
| unfamiliar_vocabulary | Real skills written in words the catalogue may not know |
| french_vocabulary | Skills written in French |
| interests_only | No skills entered |
| minimal_input | One or two inputs |
| many_inputs | Long skill and interest lists |
| no_clear_fit | No career in the catalogue is a good fit |
| lower_education | Education below the usual entry level for the goal |

## 4. Relevance labels

### 4.1 Scale

| Grade | Name | Rule |
|---|---|---|
| 3 | Strong | The profile's skills, education and stated goal match the central work of the occupation. The learner could apply now, or after a short, ordinary step (for example finishing the current degree) |
| 2 | Moderate | A realistic option: substantial overlap with the central work, or a stated goal plus a solid partial foundation. Needs further study or experience, but not a change of field |
| 1 | Weak | Related or adjacent: some skills transfer, or only the interest matches. Reaching the occupation needs major retraining, or it conflicts with the stated goal |
| 0 | Not relevant | No realistic link, or a link that would mislead (for example a licensed profession with no matching training) |

### 4.2 Rules

- **R1 Occupation first.** A grade describes the occupation's real work, judged from occupational knowledge (the O*NET occupation where `careers.csv` gives a code, otherwise general occupational knowledge stated in the justification). It is never derived from counting overlaps with the catalogue's skill list.
- **R2 No engine input.** Labels are written before any engine run on the profiles. Engine output never creates, removes or changes a label.
- **R3 Goal counts.** A stated goal raises a career to grade 2 or 3 only when the profile also has a real foundation for it. A goal alone gives at most grade 1.
- **R4 Generic skills do not create relevance.** Communication, Excel, Git or teamwork alone never justify grade 2 or above.
- **R5 Education.** Education below the usual entry level lowers a grade by at most one step and never makes a career grade 0 on its own. Licensed professions (nurse, pharmacist, physical therapist, lawyer) stay at grade 1 or below when the profile has no training in that profession.
- **R6 Current occupation.** A career-changer's current occupation is graded at most 1 when the goal is to leave it.
- **R7 Variable count.** A profile may have any number of relevant careers, including none at grade 2 or above.
- **R8 Explicit zeros.** Careers a reader could plausibly confuse with a relevant one get an explicit grade 0 with a reason. Every career not listed for a profile is grade 0 by the rule "reviewed against the full catalogue, no realistic link". This implicit 0 is part of the label set and is counted in the metrics.
- **R9 Confidence.** Each label is marked `high`, `medium` or `low`. Low means a qualified reviewer could reasonably choose a neighbouring grade.

### 4.3 Label record

`profile_id, career_id, relevance_label, justification, occupational_basis, reviewer, confidence`

`occupational_basis` names the O*NET code from `careers.csv` when there is one, or says that no occupational code exists for that career.

### 4.4 Reviewers

- All labels are written by one labeller: Claude, an AI assistant, working for the project author. The labeller also wrote the 14 career records added in v1.3.0, so the labels are **not independent of the catalogue author**.
- The labeller has seen the catalogue's skill lists. Blind labelling was not possible.
- A blank second-reviewer sheet (`second_reviewer_sheet.csv`) lists the same profile and career pairs without grades. Agreement (Cohen's weighted kappa) is computed only from a completed sheet by a real second reviewer. **No agreement value is reported in this study.**

### 4.5 Binary relevance

- Main threshold: grade 2 or 3 is relevant.
- Sensitivity check: grade 1 or higher, and grade 3 only.
- A profile with no career at or above the threshold has undefined precision, recall, F1, reciprocal rank and average precision. It is excluded from those means, and the number excluded is reported. It still counts for NDCG when it has any grade-1 label, and for coverage metrics.

## 5. Metrics

Let `R` be the full ranking of 64 careers for a profile, `Rel` the set of careers at or above the threshold, and `g(c)` the grade.

| Metric | Definition |
|---|---|
| Precision@k (k = 1, 3, 5) | Relevant careers in the top k, divided by k |
| Recall@5 | Relevant careers in the top 5, divided by the size of Rel |
| F1@5 | Harmonic mean of Precision@5 and Recall@5 for each profile, then averaged |
| MRR | Mean of 1 / rank of the first relevant career in the full ranking (0 if none) |
| MAP | Mean of average precision over the full ranking |
| NDCG@5 | DCG@5 / ideal DCG@5 with gain g(c) (0 to 3) and discount log2(rank + 1); ideal from that profile's labels |
| Hit@5 | Share of profiles with at least one relevant career in the top 5 |

All profile-level means are macro averages over defined profiles.

Coverage metrics:

| Metric | Definition |
|---|---|
| Career label coverage | Careers with at least one label at or above the threshold, out of 64 |
| Category label coverage | Categories with at least one such career, out of 10 |
| Top-5 career coverage | Careers that appear in at least one top 5, out of 64 |
| Never in top 5 | Careers that appear in no top 5, out of 64 |
| Category top-5 coverage | Categories with at least one career in some top 5 |

Score analysis: mean, median and distribution of the top-1 and top-5 scores, and the rank of every relevant career.

## 6. Uncertainty

- Profile-level percentile bootstrap: 2,000 resamples, seed 64.
- Each resample draws profiles with replacement. All metrics in one resample use the same profiles.
- Within a resample, a profile with an undefined metric is skipped for that metric only.
- Reported: mean, 95% interval, profiles included, resamples.
- Per-category intervals use about 10 profiles each and are reported as indicative only.
- No significance tests between categories are reported.

## 7. Comparison with the original study

The original and new evaluations are separate studies. They have different profiles, a different labeller procedure (binary against graded), a different number of careers and different label coverage. They are shown side by side, and differences are described, not attributed to the expansion. A controlled comparison would need the same profiles labelled independently for both catalogue versions. That design is described in the results document but not run.

## 8. Robustness experiments

Run with the production formula, on profiles derived from frozen evaluation profiles, without labels:

1. missing skills (half the skills removed), 2. interests only, 3. education removed, 4. unknown skill names added, 5. French aliases, 6. mixed case, 7. transferable skills, 8. very few inputs, 9. many inputs, 10. conflicting interests.

For each condition: change in top-5 overlap (Jaccard) and in the rank of grade-3 careers against the original profile, and, where labels apply, the change in NDCG@5. Conditions that change the profile's meaning (for example removing skills) are reported as behaviour, not as accuracy.

## 9. Reproducibility

`reports/evaluation_64/evaluation_summary.json` records the Python and package versions, seeds, dataset version, SHA-256 values of the profiles, labels and catalogue files, the configuration and the execution date. Raw per-profile outputs (`profile_results.csv`, `ranking_rows.csv`) are kept separate from aggregates. `python -m src.evaluation.independent_64_evaluation --check reports/evaluation_64` recomputes everything and compares it with the saved files.

## 10. Review-stage diagnostics (added 2 November 2026, after the first results)

These definitions were written after the first results were seen, in answer to the review. They use the same frozen data and rankings and add no labels. Their outputs are explanatory, not pre-registered tests.

| Diagnostic | Definition | Output |
|---|---|---|
| Unrecognised skill share | Skill entries reported unknown by the engine's input parser, divided by skill entries typed in `profiles.csv` (480; no profile repeats a skill). "Recognised" means mapped to any catalogue skill, directly or through an alias | `vocabulary_analysis.csv` |
| Profile with no recognised skill | A profile that lists at least one skill and has none recognised. Interests-only profiles are counted separately | `vocabulary_zero_recognised.csv` |
| Profile-type sample status | Fewer than 5 profiles: insufficient, not interpreted. 5 to 9: indicative only. 10 or more: reported | `profile_type_metrics.csv` |
| Slot driver | For each top-5 slot: "skills matched" if any required or preferred skill matched, otherwise "interests only" (or "education only") | `exposure_slot_drivers.csv`, `exposure_by_category.csv` |
| Exposure | Top-5 slots per category and career, split by the receiving profile's category and by the label grade of the slot | `exposure_by_category.csv`, `exposure_by_career.csv`, `exposure_examples_C004.csv` |
| Score tie at rank 5 | Ranks 5 and 6 have equal total score at the engine's precision (9 decimals). Also reported at display precision (1 decimal) | `tie_profiles.csv`, `tie_summary.csv` |
| Tie resolution | The first key of the engine's sort key (`src/engine/ranking.py`) that separates ranks 5 and 6: required-skill coverage, number of matched required skills, or career ID | `tie_summary.csv` |
| Career-ID tie group | Careers equal on the first three sort keys, so their order depends only on career ID. A group "crosses the cut-off" when it has members on both sides of rank 5 | `tie_groups_crossing_rank5.csv` |
| Slot won on career ID | A career in the top 5 that belongs to a career-ID tie group crossing the cut-off | `exposure_by_career.csv` |

## 11. Second review

- The blank sheet (585 pairs) and a readable packet are in `data/evaluation/catalog_v1.3.0/review/`, separate from the original labels. Instructions: `docs/independent_64_second_review_guide.md`.
- `src/evaluation/eval64_review_analysis.py` accepts only a completed sheet with exactly the blank sheet's pairs, a grade, justification, reviewer and confidence on every row. From the command line it also requires `--confirm-independent-reviewer`, given only after the reviewer has signed the declaration in `docs/reviewer_handover.md`, and it refuses reviewer names that identify the first labeller or a test fixture. It refuses the blank sheet. Rows whose justification begins `INSUFFICIENT:` are counted and reported.
- It reports:
  - exact and within-one agreement;
  - quadratic and linear weighted Cohen's kappa over the 585 pairs, with unlisted first-labeller pairs counted as grade 0 (rule R8);
  - binary kappa at grade 2;
  - the confusion matrix;
  - disagreements by profile category and by career;
  - the main metrics recomputed with the original labels, the reviewer's labels and a conservative consensus (the lower grade of the two).
- The original labels are never overwritten. Adjudicated labels would form `eval64_v2`.

## 12. Exploratory sensitivity analysis (added 2 November 2026, post-hoc)

`src/evaluation/eval64_sensitivity.py` compares alternative tie-breaks (career ID, per-profile SHA-256 hash, seeded random over 200 runs with seeds 2026 to 2225) and interest rules (current, no interests, fixed unit, cosine).

- It uses a local replica of scoring and ranking. With production settings the replica reproduces the production ranking exactly (tested).
- Deterministic alternatives are compared with a paired profile-level bootstrap of the per-profile difference (2,000 resamples, seed 64).
- The analysis is exploratory and post-hoc. It is kept out of the primary evaluation outputs and deploys nothing.
- Report: `docs/independent_64_sensitivity_analysis.md`.

## 13. Second-review sampling design and agreement inference (added 2 November 2026)

**Provenance.** The blank sheet was first built by an inline step on 1 November 2026. `src/evaluation/eval64_review_sampling.py` holds the same procedure and reproduces the frozen sheet byte for byte (SHA-256 checked against the manifest).

**Design.** The sample is stratified and enriched, with known inclusion probabilities.

| Stratum | Population | Sampled | Selection | Inclusion probability |
|---|---|---|---|---|
| Listed | 363 pairs the first labeller graded explicitly | 363 | Census: all included, by the labeller's own choice of which careers to list | 1 |
| Unlisted | 6,741 pairs not listed (grade 0 by rule R8) | 222 | 2 per profile, uniform without replacement within the profile's unlisted careers, seed 6464 | 2 / (64 − k), where k is the profile's listed careers (2 to 7): 0.0323 to 0.0351 |

- Selection probability is not equal across pairs, careers or profiles. Listed pairs are certain; unlisted pairs have about a 1 in 30 chance.
- Careers therefore appear 3 to 19 times. Profiles carry 4 to 9 pairs; Engineering profiles contribute more because there are 14 of them.
- Design weights (1 / inclusion probability) sum to 7,104. Distribution tables: `reports/evaluation_64_review_design/`.

**Inference.**
1. An ordinary weighted kappa on the 585 pairs describes the enriched sample only. Kappa depends on how often each grade occurs, and the sample holds far more grade 1 to 3 pairs (353 of 585) than the population (353 of 7,104). It must not be presented as agreement over all pairs.
2. The primary agreement statistic is weighted kappa on the listed stratum. Its population is the 363 listed pairs, which form a census, so no design weighting is needed within it.
3. For the unlisted stratum, kappa is undefined (the first labeller's grade is constant). The analysis estimates the share of unlisted pairs the reviewer finds relevant, which is a check on relevance the labeller missed, using design weights.
4. A design-weighted kappa over all 7,104 pairs is also reported. It is about 95% weighted toward unlisted pairs and rests on 222 sampled ones, so it is imprecise and mostly reflects agreement on "not relevant".
5. All intervals use a profile-clustered percentile bootstrap (2,000 resamples, seed 64).

**Anonymisation.**
- `src/evaluation/eval64_anonymise.py` builds the reviewer copy in `review/anonymised/`:
  - profile codes PR-001 to PR-111 in a random profile order;
  - career codes JOB-xxxx drawn from a system random source, so they cannot be rebuilt from a seed;
  - career order within each profile re-randomised;
  - no O*NET column, because O*NET coverage differs between the original 50 and the new 14 careers and would hint which is which.
- Titles, descriptions and entry levels are unchanged.
- The mapping is in `review/private/anonymisation_map.json`, outside the reviewer bundle. It records SHA-256 values of the source sheet and the anonymised files, and `--verify` checks them.
- The analysis maps a completed anonymised sheet back with `--anonymised` and then applies the same checks as for the original sheet.
