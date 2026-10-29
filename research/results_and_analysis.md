# Results and analysis

Every number here is copied from the saved experiment outputs `reports/evaluation_results.json` (original study, 14 October 2026), `reports/research_results.json` (baselines and ablations, 26 October 2026), `reports/ml_results.json` (machine-learning comparison, 26 October 2026) and `reports/ml_sensitivity.json` (audit checks, 29 October 2026). All reproduce exactly from code (see `experimental_protocol.md`, A.5 and A.6).

**Scope of every result below.** These are preliminary, synthetic-profile results. They measure how closely the rankings agree with labels that the project author wrote for 36 author-written profiles (35 scorable). They are not evidence of effectiveness for real learners, and they are not hiring predictions.

## 1. Status of results

| Category | Content |
|---|---|
| Verified (reproduced from code) | All tables in Sections 2 to 4, 7 and 8 |
| Preliminary findings | Interpretations in Sections 5 and 9, limited to synthetic profiles |
| Proposed experiments, no results yet | Independent labels, real profiles, user study, semantic baseline B4 |

## 2. Original evaluation (configurations A to D)

From `reports/evaluation_results.json`, mean with 95% bootstrap interval, 35 profiles:

| Metric | A baseline (production) | B required-heavy | C strong required | D skills only |
|---|---|---|---|---|
| MRR | 0.986 [0.957, 1.000] | 0.981 [0.943, 1.000] | 0.981 [0.943, 1.000] | 0.967 [0.914, 1.000] |
| R-precision | 0.933 [0.857, 0.991] | 0.929 [0.857, 0.986] | 0.919 [0.843, 0.986] | 0.900 [0.800, 0.971] |
| MAP | 0.971 [0.936, 0.998] | 0.961 [0.915, 0.995] | 0.957 [0.909, 0.991] | 0.946 [0.890, 0.991] |
| Precision@5 | 0.320 | 0.320 | 0.320 | 0.320 |
| Recall@5 | 1.000 | 1.000 | 1.000 | 1.000 |
| F1@5 | 0.469 | 0.469 | 0.469 | 0.469 |
| Catalogue coverage | 50 of 50 | 50 of 50 | 50 of 50 | 50 of 50 |

Precision@5 of 0.320 is the maximum possible: profiles have 1.6 relevant careers on average, so five slots can hold at most 56 hits out of 175. The top-5 metrics are saturated and cannot separate configurations.

## 3. Baselines and ablations (new)

From `reports/research_results.json`, mean with 95% bootstrap interval, 35 profiles. S is identical to configuration A above; B1 is identical to configuration D.

| Method | MAP | NDCG@5 | MRR | R-precision | Recall@5 |
|---|---|---|---|---|---|
| S Full system | 0.971 [0.936, 0.998] | 0.983 [0.958, 0.999] | 0.986 | 0.933 | 1.000 |
| B1 Skills only | 0.946 [0.890, 0.991] | 0.965 [0.925, 0.995] | 0.967 | 0.900 | 1.000 |
| B2 Interests only | 0.793 [0.700, 0.881] | 0.827 [0.742, 0.902] | 0.868 | 0.691 | 0.895 |
| B3 Skills and interests, equal halves | 0.941 [0.896, 0.979] | 0.956 [0.923, 0.985] | 0.971 | 0.886 | 0.981 |
| B5 Random (100 seeds) | 0.100 [0.095, 0.105] | 0.065 [0.059, 0.070] | 0.117 | 0.033 | 0.096 |
| B6 Popularity, leave-one-out | 0.135 [0.060, 0.223] | 0.118 [0.037, 0.215] | 0.180 | 0.110 | 0.110 |
| AB-I No interests | 0.941 [0.887, 0.986] | 0.958 [0.917, 0.990] | 0.967 | 0.890 | 0.991 |
| AB-E No education | 0.971 [0.936, 0.998] | 0.983 [0.958, 0.999] | 0.986 | 0.933 | 1.000 |
| AB-P No preferred skills | 0.969 [0.936, 0.995] | 0.981 [0.958, 0.998] | 0.986 | 0.929 | 1.000 |
| W-B Required-heavy | 0.961 [0.915, 0.995] | 0.976 [0.943, 0.998] | 0.981 | 0.929 | 1.000 |
| W-C Strong required | 0.957 [0.909, 0.991] | 0.974 [0.942, 0.996] | 0.981 | 0.919 | 1.000 |

## 4. Significance tests

Paired sign-flip randomisation test, S minus method, 10,000 resamples, Holm-adjusted within each family. "Changed" counts profiles where average precision differs from S.

| Family | Method | Mean AP difference | Changed profiles | p (AP) | p Holm (AP) | p Holm (NDCG@5) | Significant |
|---|---|---|---|---|---|---|---|
| Baselines | B1 Skills only | 0.025 | 5 | 0.130 | 0.133 | 0.133 | No |
| Baselines | B2 Interests only | 0.178 | 16 | 0.001 | 0.003 | 0.002 | Yes |
| Baselines | B3 Skills and interests | 0.031 | 5 | 0.067 | 0.133 | 0.133 | No |
| Baselines | B5 Random | 0.872 | 35 | 0.0001 | 0.0005 | 0.0005 | Yes |
| Baselines | B6 Popularity | 0.837 | 34 | 0.0001 | 0.0005 | 0.0005 | Yes |
| Ablations | AB-I No interests | 0.030 | 6 | 0.065 | 0.327 | 0.327 | No |
| Ablations | AB-E No education | 0.000 | 0 | 1.000 | 1.000 | 1.000 | No |
| Ablations | AB-P No preferred | 0.002 | 2 | 1.000 | 1.000 | 1.000 | No |
| Ablations | W-B Required-heavy | 0.011 | 4 | 0.258 | 0.775 | 0.775 | No |
| Ablations | W-C Strong required | 0.015 | 5 | 0.130 | 0.520 | 0.520 | No |

Profiles whose average precision changes when interests are removed (AB-I): P01 (1.000 to 0.833), P03 (0.500 to 0.333), P09 (1.000 to 0.833), P33 (0.833 to 0.700), P36 (1.000 to 0.500), and P34, which improves (0.917 to 1.000).

## 5. Analysis (preliminary)

1. **The system is far above trivial baselines.** Random and popularity orderings reach MAP 0.100 and 0.135. This confirms the profiles and labels carry signal the scoring uses; it does not show real-world quality.
2. **Skills carry most of the ranking.** Skills only (B1) reaches MAP 0.946, close to the full system's 0.971, and the difference is not significant (Holm p = 0.133). Interests only (B2) is significantly worse (MAP 0.793).
3. **Interests add a small, unconfirmed gain.** Removing interests lowers MAP in 5 of 35 profiles and raises it in 1. The average drop (0.030) is not significant after correction. With 35 profiles and only 6 changed rankings, the study has little power to detect an effect of this size.
4. **Education makes no difference on these profiles.** Removing it changes no ranking. The likely reason is the data: 42 of 50 careers share education level 3, so the component barely separates careers. This suggests either dropping education from the claims or testing it on profiles where education differs.
5. **Preferred skills matter little.** Removing them changes 2 profiles (one worse, one better).
6. **Giving interests more weight does not help.** B3 (interests at 0.50) scores below S (MAP 0.941), and Recall@5 drops to 0.981.
7. **Weight choice is not decisive.** The required-heavy variants are slightly lower than S but not significantly. The production weights should be described as a reasonable choice, not an optimised one.
8. **Known failure pattern.** As documented in `docs/evaluation_report.md` section 6, careers with three required skills gain more from one shared skill than careers with four or five (list-length bias), for example P03, P16 and P33.

## 6. What these results do not show

- Whether the rankings agree with anyone other than the author.
- Whether the method works on free-text input from real students; 129 of 142 profile skills are already exact catalogue names.
- Whether explanations or gap advice help anyone.
- Any effect on career outcomes.

The independent-label study and the user study (`experimental_protocol.md`, Parts B and C) are needed for those claims.

## 7. Machine-learning models vs the formula (grouped nested CV, 5 repeats)

Source: `reports/ml_results.json`. Ranking metrics are macro means over 35 scorable profiles; classification metrics are means over the 5 repeats (standard deviation in brackets).

| Method | MAP [95% CI] | NDCG@5 | MRR | R-prec | P@5 | R@5 | ROC-AUC | PR-AUC | F1 |
|---|---|---|---|---|---|---|---|---|---|
| Weighted formula | 0.971 [0.936, 0.998] | 0.983 | 0.986 | 0.933 | 0.320 | 1.000 | 0.991 (0.000) | 0.897 (0.000) | 0.823 (0.019) |
| Random Forest | 0.965 [0.933, 0.991] | 0.979 | 0.986 | 0.917 | 0.319 | 0.997 | 0.992 (0.003) | 0.901 (0.011) | 0.829 (0.019) |
| Logistic Regression | 0.962 [0.925, 0.991] | 0.977 | 0.985 | 0.912 | 0.319 | 0.998 | 0.991 (0.011) | 0.928 (0.009) | 0.839 (0.007) |
| XGBoost | 0.959 [0.922, 0.988] | 0.974 | 0.986 | 0.913 | 0.318 | 0.994 | 0.992 (0.009) | 0.903 (0.019) | 0.810 (0.007) |
| Decision Tree | 0.936 [0.886, 0.979] | 0.949 | 0.983 | 0.909 | 0.301 | 0.954 | 0.967 (0.018) | 0.818 (0.046) | 0.785 (0.027) |

P@5 cannot exceed about 0.32 here because profiles have only 1.6 relevant careers on average.

Paired randomisation test, model minus formula (Holm over four models):

| Model | AP difference | Holm p (AP) | NDCG@5 difference | Holm p (NDCG@5) |
|---|---|---|---|---|
| Random Forest | -0.006 | 1.000 | -0.004 | 1.000 |
| Logistic Regression | -0.010 | 0.249 | -0.006 | 0.249 |
| XGBoost | -0.013 | 1.000 | -0.008 | 1.000 |
| Decision Tree | -0.036 | 0.588 | -0.034 | 0.382 |

No model ranks better than the formula and no difference is significant.

## 8. Audit checks (one repeat, seed 0)

Source: `reports/ml_sensitivity.json`. Logistic Regression, Decision Tree and Random Forest only.

| Check | Formula | Logistic Regression | Decision Tree | Random Forest |
|---|---|---|---|---|
| Grouped CV, ties by career id (MAP) | 0.971 | 0.957 | 0.921 | 0.973 |
| Same predictions, random ties (MAP) | 0.968 | 0.954 | 0.877 | 0.960 |
| Leave-one-category-out (MAP) | 0.971 | 0.961 | 0.934 | 0.965 |
| Labels permuted across profiles (MAP) | 0.070 | 0.120 | 0.118 | 0.112 |

Random ordering reaches MAP 0.100 (Section 3).

## 9. Analysis of the machine-learning results (preliminary)

1. **The models are genuinely trained and do learn the labels.** On held-out profiles they reach MAP 0.936 to 0.965, and with labels moved to the wrong profiles they fall to 0.112 to 0.120, close to random (0.100). The pipeline therefore does not leak labels into features or folds.
2. **No model beats the formula.** In the 5-repeat study the formula has the highest MAP, NDCG@5 and R-precision. In one seed-0 repeat Random Forest is 0.001 above the formula (0.9725 vs 0.9714) with career-id ties but 0.008 below it with random ties, so single runs should not be over-read.
3. **Tie-breaking matters for the Decision Tree.** It gives many careers the same probability. Ordering those ties by career id raised its MAP from 0.877 (random ties) to 0.921 in the seed-0 run. Its reported 0.936 is therefore optimistic; its true expected ranking quality is lower.
4. **Related profiles do not inflate the models.** Holding out a whole career category at a time leaves MAP almost unchanged (LR 0.961, RF 0.965, DT 0.934). The features describe the match, not the career, so models transfer across categories.
5. **Logistic Regression is best on pooled classification (PR-AUC 0.928, F1 0.839)** but not on per-learner ranking, which is what a learner sees.
6. **What this does not show.** All labels come from the author, and the features reuse the formula's matching, so agreement here cannot be read as real-world accuracy. The formula is kept in production.
