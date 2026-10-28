# Research package

Prepared on 26 October 2026 for the lecturer's review. The lecturer will decide the final paper structure and manage publication through KIIT. This folder is local and not committed.

**Start with `supervisor_review_package.md`.**

## Documents

| File | Purpose |
|---|---|
| `supervisor_review_package.md` | One-document summary: abstract draft, RQs, results, questions for the lecturer, checklist |
| `dataset_comparison.md` | Project vs O*NET: provenance, comparison table, limitations |
| `research_problem_and_gap.md` | Problem, research questions, hypotheses, contributions, gap |
| `methodology.md` | Architecture, dataset, matching, scoring formula, weights, ranking, explanations, skill gap |
| `experimental_protocol.md` | Reproducible protocol: completed synthetic experiments and proposed human studies |
| `results_and_analysis.md` | Results copied from the saved experiment outputs, with analysis |
| `ml_experiments.md` | Logistic Regression, Decision Tree, Random Forest and XGBoost vs the formula: features, labels, protocol, results, decision, and the live "How the Models Rank Your Careers" demonstration |
| `literature_review.md` | Verified references by theme and their relation to the research question |
| `limitations_and_future_work.md` | Limitations, validity threats, ethics, future work |
| `risks_report.md` | Risks with severity, evidence, effect, mitigation and status |
| `implementation_roadmap.md` | What is done in code and what remains |
| `data/onet_mapping_audit.csv` | Mapping type for each of the 50 careers |
| `instruments/` | Draft consent form, profile form, reviewer guide and questionnaire; for use only after ethics approval |

## Reproduce the evidence

```bash
python -m pytest -q                                                   # 291 passed
python -m src.data.validation --quiet-warnings                        # 0 errors, 3 warnings
python -m src.evaluation.experiments --check reports/evaluation_results.json
python -m src.evaluation.research_experiments --check reports/research_results.json
pip install -r requirements-research.txt                              # adds xgboost for the ML study
python -m src.evaluation.ml_experiments --check reports/ml_results.json
```

## Verified, preliminary, proposed

| Category | Items |
|---|---|
| Verified | Dataset statistics; O*NET facts from official pages; DevOps mapping to 15-1252.00; code behaviour; both result files reproduce |
| Preliminary | All metric values, which come from 36 author-written synthetic profiles (35 scorable) |
| Proposed | Independent labels, real student profiles, user study, semantic baseline, held-out set |
| Future work | ESCO validation, Indian labour data, graded skills, more languages, T-Career API |

No real participants, reviewer judgements or real-world effectiveness results exist.

Editable versions of some documents were shared with the supervisor separately. Where they differ from these files, these files are newer: DevOps is now mapped, and venue selection is no longer part of the plan.
