# Model audit

Audit of the machine-learning experiments, 29 October 2026, at commit 2485834 plus the changes listed in section 4. Every statement was checked in the code, the git history or a saved report, not in earlier documents.

## 1. Answers to the audit questions

| # | Question | Finding | Evidence |
|---|---|---|---|
| 1 | Are Logistic Regression, Decision Tree and Random Forest implemented and trained? | Yes. Each is fitted inside grouped nested cross-validation (`GridSearchCV.fit`) in every outer fold, 5 repeats. | `src/ml/models.py`, `src/evaluation/ml_experiments.py` (`run`) |
| 2 | Does XGBoost exist offline? | Yes, `XGBClassifier` from xgboost 3.4.1, research only. It is not in `requirements.txt` and is skipped when not installed. | `src/ml/models.py`, `requirements-research.txt` |
| 3 | Is the weighted formula the baseline? | Yes. `baseline_scores()` calls the production `recommend()`; the formula is the reference in every significance test. | `ml_experiments.py` (`BASELINE`) |
| 4 | Data, profiles, features, labels | 50 careers (`data/raw/careers.csv`); 36 synthetic profiles (`data/evaluation/labelled_profiles.json`); 1,800 learner-career pairs; 13 features from `src/ml/features.py`; binary label = career listed in the profile's `relevant_career_ids` (56 positives, 3.1%). | `reports/ml_results.json` (`data`) |
| 5 | Label provenance | Synthetic and manually assigned by the project author, using written rules L1 to L5. Not derived from the formula: no code writes labels, and the file has not changed since commit d93b46b. See section 2 for what git can and cannot confirm. | `git log -- data/evaluation/labelled_profiles.json` |
| 6 | Same profiles, candidates, labels and metrics for all methods? | Yes. Every method ranks the same 50 careers for the same 35 scorable profiles against the same labels, with the same metric code (`src/evaluation/metrics.py`). The formula needs no training and is scored on every profile; models are scored on held-out profiles only. | `ml_experiments.py` (`ranking_metrics`) |
| 7 | Leakage or circular evaluation? | No mechanical leakage found (section 3). Indirect circularity remains: one author wrote the careers, the profiles and the labels, and the features reuse the formula's matching. | Sections 2 and 3 |
| 8 | Does the live app use trained models? | Partly. Production ranking uses only the formula. The Analytics page also trains LR, DT and RF once per server on all labelled pairs and shows their top 5 next to the formula, labelled "comparison only". XGBoost is never used live. | `src/ml/comparison.py`, `src/ui/state.py` (`_cached_live_models`) |

## 2. Label provenance

- Engine code was committed in d29ecaa (14 Oct 2026, 08:23 UTC); the labels in d93b46b (14 Oct 2026, 09:10 UTC), 47 minutes later.
- The label file states: "Labels were written before the engine was run on any of these profiles." This is the author's own statement. Git can show the order of commits, not whether the engine was run locally before labelling, so it cannot be independently verified.
- Since d93b46b the label file, `src/engine/`, and `data/raw/skill_aliases.csv` are unchanged. `careers.csv` changed once (commit 4452484), only in the O*NET code and URL of C013, which are not used in matching.
- **Correction made:** six documents said the labels were committed "before the engine ran". They now give the commit order and say the "not run before labelling" part is the author's statement (`dataset_comparison.md`, `limitations_and_future_work.md`, `ml_experiments.md`, `experimental_protocol.md`, `supervisor_review_package.md`, `docs/evaluation_report.md`). The research paper (Word file, outside the repository) uses the old wording and should be updated the same way.

## 3. Leakage and validity checks

| Check | Method | Result | Conclusion |
|---|---|---|---|
| Profile overlap | Every outer split, 5 seeds | No profile in both training and test (test) | Grouping works |
| Preprocessing | `StandardScaler` inside the scikit-learn pipeline | Fitted on training folds only | No preprocessing leakage |
| Tuning | Inner `GroupKFold(3)` by profile on the outer training part | Test fold never used for tuning or thresholds | No tuning leakage |
| Identity features | Feature names | No career id, category or profile field | Models cannot memorise careers |
| Labels in features | Features rebuilt with permuted labels | Identical feature matrix (test) | Features do not see labels |
| Label permutation | Labels moved to other profiles, grouped CV, seed 0 | MAP: LR 0.120, DT 0.118, RF 0.112, formula 0.070; random ordering is 0.100 | A leak-free pipeline falls to chance, as it does here |
| Related profiles | Leave-one-category-out (8 folds) | MAP: LR 0.961, DT 0.934, RF 0.965, formula 0.971 | Models do not depend on seeing same-category profiles |
| Tie handling | Same predictions, ties broken at random (50 shuffles) instead of by career id | MAP change: DT 0.921 to 0.877, RF 0.973 to 0.960, LR 0.957 to 0.954, formula 0.971 to 0.968 | Career-id tie-breaking flattered the Decision Tree and slightly the Random Forest |

Sources: `reports/ml_sensitivity.json` and `tests/test_ml_audit.py`.

## 4. Changes made in this audit

1. `src/evaluation/ml_sensitivity.py` and `reports/ml_sensitivity.json`: random-tie, leave-one-category-out and label-permutation checks (scikit-learn models only, so CI can run them).
2. `tests/test_ml_audit.py` (7 tests): the saved LR, DT and formula results reproduce exactly; features ignore labels and identity; splits never share a profile; sensitivity helpers; saved sensitivity claims.
3. CI: a new step checks that `reports/ml_sensitivity.json` reproduces.
4. Provenance wording corrected (section 2) and the risk register updated (`risks_report.md`).

Not changed: the main experiment code and `reports/ml_results.json`. The full pipeline was rerun from a clean state and matched the saved report byte for byte (4 min 51 s, Python 3.13.16, scikit-learn 1.9.1, XGBoost 3.4.1). The production formula is unchanged: no evidence supports replacing it.

## 5. Open items

- The research paper (outside the repository) says the labels were "committed to the repository before the engine was run on any profile". It should use the corrected wording in section 2.
- The main report uses career-id tie-breaking. Results with random tie-breaking come from one repeat only (seed 0).
