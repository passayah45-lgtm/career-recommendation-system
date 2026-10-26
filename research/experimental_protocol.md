# Experimental protocol

Version 1.0, 26 October 2026. This protocol separates three things: experiments already run (Part A), a reproducible procedure for re-running them, and studies proposed but not started (Parts B and C). Parts B and C involve people and must not begin before KIIT ethics approval.

## Part A. Synthetic-profile experiments (completed)

### A.1 Data

| Item | File | Notes |
|---|---|---|
| Career catalogue | `data/raw/careers.csv` (dataset v1.2.0) | 50 careers; DevOps O*NET mapping added 26 Oct 2026, which does not affect scores |
| Skill aliases | `data/raw/skill_aliases.csv` | 37 aliases |
| Profiles and labels | `data/evaluation/labelled_profiles.json` | 36 author-written profiles, binary labels, committed before the engine was run (commit d93b46b); 35 have at least one relevant career |

### A.2 Methods compared

All methods rank the same 50 careers from the same parsed profile (normalisation and alias lookup are shared).

| ID | Method | Weights (required, preferred, interests, education) | Tie-break |
|---|---|---|---|
| S | Full system (production) | 0.55, 0.15, 0.25, 0.05 | Engine: required coverage, matched count, career id |
| B1 | Skills only | 0.55, 0.15, 0, 0 | Engine |
| B2 | Interests only | 0, 0, 1, 0 | Career id only, so no skill information enters |
| B3 | Skills and interests, equal halves | 0.39, 0.11, 0.50, 0 | Engine |
| B5 | Random | none | Mean over 100 seeded permutations (seeds 0 to 99) |
| B6 | Popularity, leave-one-out | none | Careers ordered by how often they are labelled relevant in the other 35 profiles; ties by id |
| AB-I | No interests | 0.55, 0.15, 0, 0.05 | Engine |
| AB-E | No education | 0.55, 0.15, 0.25, 0 | Engine |
| AB-P | No preferred skills | 0.55, 0, 0.25, 0.05 | Engine |
| W-B | Required-heavy weights | 0.70, 0.10, 0.15, 0.05 | Engine |
| W-C | Strong-required weights | 0.75, 0.10, 0.10, 0.05 | Engine |

The engine divides by the sum of applicable weights, so every weighted method yields scores from 0 to 100. B3's skill weights keep the production ratio of required to preferred (0.55 to 0.15), rounded to two decimals. A semantic-matching baseline (B4) is proposed but not implemented (Part C).

### A.3 Metrics

Computed on the full ranking with K = 5 (`src/evaluation/metrics.py`):

- Primary: mean average precision (MAP).
- Co-primary: NDCG@5. Labels are binary, so each relevant career has gain 1.
- Secondary: MRR, R-precision, Precision@5, Recall@5, Hit@5.
- Means are macro averages over the 35 profiles with defined values; P35 (no relevant career) is excluded from every mean.
- 95% intervals: percentile bootstrap, 2,000 resamples, seed 42.

### A.4 Statistical tests

- Paired two-sided sign-flip randomisation test on per-profile differences (S minus method), 10,000 resamples, seed 42.
- Tested metrics: average precision and NDCG@5.
- Holm correction within two families, separately for each metric: baselines (B1, B2, B3, B5, B6) and ablations (AB-I, AB-E, AB-P, W-B, W-C).
- A difference is called significant only if the Holm-adjusted p-value is below 0.05.

These tests were chosen before the results were seen, but they were not formally pre-registered. Report them as exploratory.

### A.5 How to reproduce

From the repository root, Python 3.12, packages from `requirements.txt`:

```bash
python -m pytest -q
python -m src.data.validation --quiet-warnings
python -m src.evaluation.experiments --check reports/evaluation_results.json
python -m src.evaluation.research_experiments --check reports/research_results.json
```

Expected on 26 October 2026: 275 tests passed; validation 0 errors and 3 warnings (the 3 careers without an O*NET code); both checks report "match". To regenerate a report after a deliberate change, use `--output` instead of `--check`. `tests/test_research_experiments.py` fails if the saved research report and a fresh run differ.

## Part B. Independent-label study (proposed, requires ethics approval)

1. **Approval first.** Submit this protocol and the instruments in `research/instruments/` to the KIIT ethics committee. No recruitment before written approval.
2. **Freeze.** Before any reviewer label is opened, tag the commit that fixes every method, weight, alias and threshold. Any later change reruns Part B and is reported as a deviation.
3. **Profiles.** About 70 anonymised profiles from consenting KIIT students aged 18 or older, collected with `profile_collection_form.md`, spread across at least four schools so that more than two career categories are represented.
4. **Pooling.** For each profile, pool the top 15 careers from every method. Present the pool to reviewers in alphabetical order, without scores or method names.
5. **Labelling.** Three independent reviewers (for example a career counsellor and two faculty members from different schools) grade each pooled career 0, 1 or 2 with `reviewer_labelling_guide.md`, after a calibration round on 5 practice profiles. The author does not label.
6. **Agreement.** Fleiss' kappa across the three reviewers, Cohen's kappa per pair and quadratic-weighted kappa, reported before adjudication. Target at least 0.6; below 0.4, revise the guide and relabel a fresh subset.
7. **Final label.** Median grade; ties resolved by a reserve reviewer.
8. **Analysis.** Same methods and metrics as Part A, plus graded NDCG@5. Primary hypothesis H1: S has higher MAP than B1 (skills only).
9. **Sample size.** To detect a mean MAP difference of 0.05 with an assumed standard deviation of differences of 0.12 (d of about 0.42) at 80% power with a two-sided Wilcoxon test: about 47 profiles at alpha 0.05, about 70 at the strictest Holm level (0.01 for five comparisons). The standard deviation is an assumption; re-estimate it after 15 labelled profiles and log any change.
10. **Storage.** Profiles and labels in an encrypted, git-ignored folder (`data/evaluation/track_b/`, to be created); only anonymised data released, and only with consent.

## Part C. User study and remaining baselines (proposed)

- **User study** (requires ethics approval): about 35 students, within-subject comparison of the list with and without explanations, counterbalanced, using `user_study_questionnaire.md`. 35 gives 80% power for a medium paired effect (d = 0.5) at alpha 0.05.
- **B4 semantic matching** (no approval needed): sentence-embedding similarity between learner and career skills, with the similarity threshold tuned on Part A profiles only and the model name and version pinned. Not implemented.
- **Held-out synthetic set**: a new set of profiles written before any further method change, so that Part A has a development set and a test set.

## Leakage rules

1. Part A data never evaluates Part B; Part B data never chooses weights, thresholds or aliases.
2. Reviewers never see method outputs; the author never labels Part B.
3. The production weights in `src/engine/scoring.py` are not tuned on any profile set.
4. Labels in `labelled_profiles.json` are never edited; new sets are added as new files.
