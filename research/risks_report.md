# Research risks report

Updated 26 October 2026 after the baselines, ablations and DevOps mapping fix. Severity reflects how much each risk would weaken the paper if it is not addressed.

| # | Risk | Severity | Evidence | Effect on the paper | Mitigation | Status |
|---|---|---|---|---|---|---|
| 1 | Synthetic-data bias | High | All 36 profiles author-written; 21 "strong match"; Recall@5 = 1.0 for most methods | Results read as a self-test | Independent-label study with real profiles; label synthetic results as preliminary | Protocol and instruments drafted; needs ethics approval |
| 2 | Indirect circularity (one author) | High | One author for careers, engine and labels; 91% of profile skills are exact catalogue names; labels not engine-generated (commit d93b46b) | Inflated agreement | Three blinded independent reviewers; kappa | Proposed |
| 3 | Overclaiming quality | High | MAP 0.971 and MRR 0.986 are synthetic only; S vs skills-only is not significant | Common reason for rejection | Always state "agreement with author labels on synthetic profiles"; report non-significant results as such | Documents updated |
| 4 | Privacy and consent | High for human studies | Real student data planned | No approval means no usable human data | Ethics approval, consent, adults only, anonymisation, encryption | Instruments drafted |
| 5 | Low statistical power | Medium | 35 profiles; 5 or 6 changed rankings per ablation; no ablation significant | Non-significant results are inconclusive | Power analysis; about 70 real profiles | Proposed |
| 6 | Evaluation leakage | Medium | No held-out set; weights set with domain knowledge | Optimistic estimates | Freeze tag; held-out set; tune thresholds on synthetic data only | Proposed |
| 7 | Small career coverage | Medium | 50 careers vs 923 O*NET data-level occupations | Seen as a toy catalogue | Present as a controlled catalogue; report coverage | Documented |
| 8 | Missing O*NET matches | Medium, reduced | 3 careers unmatched; 7 nearest-broader; DevOps fixed | Provenance questioned | Audit table; check remaining three | Partly done |
| 9 | Skill-mapping errors | Medium | Skill lists curated without field-level sources | Wrong gap advice | Compare with O*NET and ESCO skills; gap ratings in user study | Proposed |
| 10 | Geographic bias | Medium | O*NET samples U.S. establishments | Fit for India and Guinea uncertain | State limitation; ESCO and local data later | Documented |
| 11 | Weak external validity | Medium | One university; English only | Limits generalisation | State scope | Documented |
| 12 | Education component adds nothing | Low to medium | Removing education changed no ranking | A reviewer may ask why it is in the model | Discuss openly, or test on profiles where education differs | Documented |
| 13 | Citation risk | Low | All references opened and checked on 26 October 2026; one candidate review excluded as unverified | Wrong citations damage credibility | Recheck DOIs before submission | Done for now |
| 14 | Licensing | Low to medium | No LICENSE file; O*NET is CC BY 4.0 | Release non-compliant | Add code and data licences with attribution | Lecturer decision |
| 15 | Mapping-audit titles not machine-checked | Low | O*NET titles in `research/data/onet_mapping_audit.csv` written from the 2019 taxonomy | Small title errors possible | Check against the O*NET Occupation Data file | Open |

## Machine-learning risks (added after the ML experiments, 26 October 2026)

| # | Category | Risk | Severity | Evidence | Mitigation | Status |
|---|---|---|---|---|---|---|
| 16 | Methodological | Models learn the author's labelling habits, not career suitability | High | Labels from one author; features from the same matching as the formula | Retrain only on independent real-learner labels; never report as real-world accuracy | Documented |
| 17 | Data quality | Too few positives to train reliably | High | 56 positive pairs from 35 profiles; about 15 positives per inner validation fold | Collect more labelled profiles (hundreds) before revisiting | Documented |
| 18 | Methodological | Overfitting by flexible models | Medium | Decision Tree weakest (MAP 0.936) and least stable; Random Forest picks unlimited depth | Grouped nested CV; report variance over 5 repeats | Mitigated in protocol |
| 19 | Methodological | Leakage between training and test | Medium, controlled | Pairs of one profile are correlated | Grouped outer and inner splits by profile; test checks no overlap | Mitigated |
| 20 | Methodological | Pooled classification metrics mislead | Medium | Logistic Regression has better PR-AUC and F1 but lower per-learner ranking quality | Treat ranking metrics as primary; label pooled metrics as secondary | Documented |
| 21 | Implementation | Extra dependency (xgboost) breaks deployment | Medium | xgboost wheel is large; pip pulled a GPU library by default | Kept out of `requirements.txt`; separate `requirements-research.txt`; app does not import `src/ml` | Mitigated |
| 22 | Reproducibility | Library version changes alter results | Low to medium | Results depend on scikit-learn 1.9.1, XGBoost 3.4.1 | Versions recorded in the report; `--check` mode; fixed seeds and n_jobs 1 | Mitigated |
| 23 | Deployment | A trained model replaces the formula and loses explanations | Medium | Tree ensembles are not self-explaining | Formula kept in production; `TrainedRanker` keeps engine explanations alongside any model ranking | Mitigated |
| 24 | Reporting | Paper overstates the ML contribution | Medium | Popular model names attract attention | Paper states no model beat the formula and no difference is significant | Mitigated |
