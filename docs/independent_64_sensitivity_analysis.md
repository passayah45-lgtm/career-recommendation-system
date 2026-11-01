# Tie-break and interest-scoring sensitivity (eval64_v1)

**Exploratory and post-hoc.** These experiments were designed after the evaluation results and the review findings were known. They test alternatives in a separate script (`src/evaluation/eval64_sensitivity.py`) and deploy nothing. The production formula (`src/engine/scoring.py`), the production ranking (`src/engine/ranking.py`), the frozen profiles and labels, the original 50-career snapshot and the five original reports are unchanged. Outputs: `reports/evaluation_64_sensitivity/`.

## 1. Method

- **Profiles and labels:** the 111 frozen eval64_v1 profiles and their 363 labels (grade 2 or higher counts as relevant).
- **Replica:** the script re-implements scoring and ranking locally. With the production settings it reproduces the production ranking exactly for all 111 profiles, and the scores match to 1e-9 (tests in `tests/test_eval64_sensitivity.py`). Each alternative then changes one thing.
- **Comparison:** each alternative is compared with the production ranking:
  - profiles whose top-5 membership changes;
  - top-5 positions that hold a different career;
  - relevant careers entering or leaving the top 5;
  - new-career (C051 to C064) top-5 slots;
  - category slot shares;
  - Precision@5, Recall@5, MAP and NDCG@5.
- **Uncertainty:**
  - For deterministic alternatives, the 95% interval is a paired profile-level bootstrap of the per-profile difference (2,000 resamples, seed 64).
  - For the random tie-break, it is the 2.5th and 97.5th percentile over 200 seeded runs (seeds 2026 to 2225).
- **Multiple comparisons:** several alternatives and metrics were examined after seeing the data, so no difference is called significant.

## 2. Tie-breaking

The alternatives keep the engine's first three keys (total score, required-skill coverage, number of matched required skills) and replace only the last one, the career ID.

| Method | Last key |
|---|---|
| Current | career ID, ascending (favours C001 to C050) |
| Deterministic alternative | SHA-256 of `profile_id|career_id`: a fixed order that is different for every profile and unrelated to career age |
| Seeded random | a random number per career, 200 runs |

| Measure | Current | Deterministic alternative | Seeded random (mean, 95% range) |
|---|---|---|---|
| Profiles with top-5 membership change | 0 | 54 | 54.2 (50 to 59) |
| Top-5 positions changed (of 555) | 0 | 219 | 208.6 (189 to 225) |
| Relevant careers entering the top 5 | 0 | 1 | 1.8 (0 to 4) |
| Relevant careers leaving the top 5 | 0 | 3 | 2.8 (1 to 5) |
| New-career top-5 slots | 100 | 107 | 106.8 (103 to 111) |
| Data and AI top-5 slots | 126 (22.7%) | 81 (14.6%) | 82.8 (77 to 89) |
| Precision@5 | 0.303 | 0.299, difference −0.004 [−0.012, 0.004] | 0.301 (0.295 to 0.307) |
| Recall@5 | 0.901 | 0.886, difference −0.015 [−0.044, 0.005] | 0.894 (0.881 to 0.911) |
| MAP | 0.795 | 0.776, difference −0.019 [−0.045, 0.006] | 0.785 (0.768 to 0.804) |
| NDCG@5 | 0.759 | 0.747, difference −0.013 [−0.032, 0.005] | 0.752 (0.740 to 0.766) |

**Findings:**
1. **The tie-break is the main cause of the Data and AI over-exposure.** Removing the preference for low career IDs cuts Data and AI top-5 slots from 126 to about 81 or 83, close to their share of careers (12.5%) and profiles (9.9%).
2. **New careers gain a little exposure:** about 7 more top-5 slots in 555 (from 100 to about 107).
3. **Accuracy does not change measurably.** Every metric interval for the deterministic alternative includes zero, and every current value lies inside the random-run range. The ID order neither clearly helps nor clearly harms agreement with the labels. It mainly decides who fills the low-scoring places at the end of a top 5.
4. About half of all profiles (54) change their top 5 under any of these rules, so the bottom of a typical top 5 is decided by a rule that has nothing to do with the learner. This is a transparency issue more than an accuracy issue.

## 3. Interest scoring

Every rule uses the production tie-break, so only the interest effect changes.

| Rule | Interest value (0 to 1) |
|---|---|
| Current | matched interests / interests listed for the career (3 or 4), weight 0.25 |
| No interests | interest weight 0; the other weights share the total, as production does for any missing component |
| Fixed unit | min(matched, 3) / 3: each matched interest worth the same for every career |
| Cosine | matched / sqrt(career interests × learner interests): neutral to the length of both lists |

| Measure | Current | No interests | Fixed unit | Cosine |
|---|---|---|---|---|
| Profiles with top-5 membership change | 0 | 98 | 27 | 5 |
| Top-5 positions changed | 0 | 382 | 96 | 39 |
| Relevant entering / leaving the top 5 | 0 / 0 | 2 / 35 | 0 / 2 | 1 / 1 |
| New-career top-5 slots | 100 | 67 | 104 | 102 |
| Data and AI slot share | 22.7% | 55.3% | 24.1% | 22.5% |
| Precision@5 (difference [95% interval]) | 0.303 | 0.238 (−0.065 [−0.087, −0.043]) | 0.299 (−0.004 [−0.010, 0.000]) | 0.303 (0.000 [0.000, 0.000]) |
| Recall@5 | 0.901 | 0.687 (−0.215 [−0.290, −0.143]) | 0.891 (−0.010 [−0.025, 0.000]) | 0.901 (0.000 [0.000, 0.000]) |
| MAP | 0.795 | 0.653 (−0.141 [−0.199, −0.085]) | 0.806 (+0.011 [−0.001, 0.029]) | 0.803 (+0.009 [0.002, 0.017]) |
| NDCG@5 | 0.759 | 0.560 (−0.200 [−0.255, −0.144]) | 0.761 (+0.002 [−0.007, 0.012]) | 0.764 (+0.005 [0.000, 0.010]) |

Category shares under each rule are in `interest_category_exposure.csv`, and career-level results in `interest_career_exposure.csv`. For example, Business Intelligence Analyst appears 26 times under the current rule, 44 with no interests, 22 with fixed units and 26 with cosine. Its 3 relevant appearances stay in the top 5 under every rule.

**Findings:**
1. **Interests carry much of the engine's agreement with the labels in this profile set.** Without them, Recall@5 falls by 0.21 and NDCG@5 by 0.20. Data and AI careers then take 55% of slots, because the recognised skills (Python, SQL, Excel) concentrate in those careers and ties among low-scoring careers are again decided by career ID. Interests partly correct for the vocabulary gap.
2. **Interest-list length is not a material cause of the exposure imbalance.** Making each matched interest worth the same for every career (fixed unit) changes the Data and AI share from 22.7% to 24.1%, and cosine to 22.5%. The section 16.3 statement in the results report has been corrected accordingly.
3. **Normalising for list length changes accuracy very little.** The cosine MAP difference (+0.009) has an interval just above zero, but this is one of several post-hoc comparisons and is not treated as evidence for a change.

## 4. What this does and does not support

- It supports one conclusion: the career-ID tie-break, not interest-list length, drives the over-exposure of Data and AI careers. Replacing it would make exposure fairer without a measurable accuracy cost on these profiles.
- It does not support deploying any alternative. The profiles and labels are single-author, synthetic and already used to find these effects. A change would need its own pre-registered evaluation on a new profile set (eval64_v2), with second-review labels.
- Nothing was deployed. Production behaviour is unchanged.

## 5. Reproducibility

```
python -m src.evaluation.eval64_sensitivity --check reports/evaluation_64_sensitivity
```

The analysis is deterministic. It uses bootstrap seed 64 and random tie-break seeds 2026 to 2225, and runs in about 20 seconds.
