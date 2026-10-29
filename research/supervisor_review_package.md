# Supervisor review package

**Project:** Career Recommendation System with Skill-Gap Analysis
**Student:** Issa TOURE (25141006), MSc Computer Science and Data Analysis, KIIT University
**Prepared:** 26 October 2026, for the lecturer's review
**Code:** https://github.com/passayah45-lgtm/career-recommendation-system (the changes listed in Section 12 are local and not yet pushed)
**Live app:** https://t-career-recommendation-2026.streamlit.app

Status labels used throughout: **Verified** (reproduced from code or checked at the source), **Preliminary** (synthetic profiles only), **Proposed** (not started), **Future work**.

## 1. Title and abstract draft

**Working title:** Explainable Skill-Gap-Aware Career Recommendation for Students: A Transparent Baseline and Its Evaluation

**Abstract draft (preliminary; to be revised after the independent-label study):**

Students often choose careers without seeing how their skills fit or what they would need to learn. Occupational databases such as O*NET describe occupations in depth but do not rank careers for an individual. We present a transparent, content-based career recommender over a curated catalogue of 50 careers, 47 of them linked to O*NET occupations. It scores each career as a weighted combination of required-skill coverage, preferred-skill coverage, interest overlap and education fit. It explains every score by component, and it lists required and optional missing skills, each linked to a free learning resource. On 35 synthetic learner profiles labelled by the author (labels committed after the engine code and never changed since), the system reached MAP 0.971 and NDCG@5 0.983. It far exceeded random and popularity baselines. Its advantage over a skills-only baseline (MAP 0.946) was not statistically significant, and removing education changed no ranking. Because the profiles and labels share one author and one vocabulary, these results are preliminary. We describe a protocol for evaluation with independent reviewers and real students, and release the code, data and evaluation scripts.

## 2. Research problem and motivation

See `research_problem_and_gap.md`. In short: occupational databases do not personalise, and career recommenders are rarely evaluated with independent labels or with users. The project has a working, transparent system but only self-labelled synthetic evidence.

## 3. Research questions and contributions

| RQ | Question | Status |
|---|---|---|
| RQ1 | Does the system rank independently judged relevant careers better than skills-only? | Preliminary (synthetic, not significant); real-profile test proposed |
| RQ2 | Which components contribute? | Preliminary (interests small and not significant; education none; preferred skills negligible) |
| RQ3 | Does semantic matching help on free text? | Proposed |
| RQ4 | How much do synthetic results overstate real ones? | Proposed |
| RQ5 | Are explanations and gap advice useful to students? | Proposed; instruments drafted |

Contributions:

1. A transparent, reproducible system with a skill-gap module. Verified.
2. A baseline and ablation comparison. Preliminary.
3. An O*NET mapping audit. Verified, with open items.
4. An independently labelled benchmark and user study. Proposed.

## 4. Dataset comparison and research gap

See `dataset_comparison.md`.

- O*NET 31.0 covers 1,016 occupations, 923 of them data-level. It is surveyed, rated by analysts, U.S.-based and CC BY 4.0.
- The project uses O*NET only for occupation identity: 40 careers map to the same or a close occupation, 7 to a broader one, and 3 have none. Every skill, interest and education value is curated by the author.

The research gap is an evaluation gap, not a new algorithm (`research_problem_and_gap.md`).

## 5. System design and methodology

See `methodology.md`. Four-layer architecture (interface, UI helpers, services, engine plus data). Exact matching after normalisation and 37 aliases.

Score = 100 × weighted mean of four shares, with weights 0.55 (required skills), 0.15 (preferred skills), 0.25 (interests) and 0.05 (education). Ties break deterministically. Explanations come from the computed values.

## 6. Experimental setup and metrics

See `experimental_protocol.md`.

- 11 methods: the full system, 5 baselines and 5 ablations or weight variants.
- Primary metric MAP, co-primary NDCG@5, with MRR, R-precision, P@5 and R@5 as secondary.
- Bootstrap 95% intervals.
- Paired sign-flip randomisation tests with Holm correction.
- One command reproduces each report.

## 7. Verified results (synthetic profiles, preliminary)

From `reports/research_results.json`; full tables in `results_and_analysis.md`.

| Method | MAP [95% CI] | NDCG@5 | Holm p vs full system (MAP) |
|---|---|---|---|
| Full system | 0.971 [0.936, 0.998] | 0.983 | reference |
| Skills only | 0.946 [0.890, 0.991] | 0.965 | 0.133 |
| Interests only | 0.793 [0.700, 0.881] | 0.827 | 0.003 |
| Skills and interests, equal halves | 0.941 [0.896, 0.979] | 0.956 | 0.133 |
| Random | 0.100 | 0.065 | 0.0005 |
| Popularity (leave-one-out) | 0.135 | 0.118 | 0.0005 |
| No interests | 0.941 | 0.958 | 0.327 |
| No education | 0.971 | 0.983 | 1.000 |
| No preferred skills | 0.969 | 0.981 | 1.000 |

The original study's figures (MRR 0.986, R-precision 0.933, MAP 0.971, P@5 0.320, R@5 1.000) are unchanged and still reproduce.

## 8. Discussion and limitations

Skills drive almost all of the ranking. Interests give a small gain that was not significant. Education has no effect on these profiles. The system is far above trivial baselines.

All of this is agreement with the author's own labels on author-written profiles that mostly use catalogue vocabulary (91% exact matches). See `limitations_and_future_work.md` and `risks_report.md`.

## 9. References (verified 26 October 2026)

Full, annotated list in `literature_review.md`. Key references:

1. National Center for O*NET Development, "O*NET 31.0 Database." https://www.onetcenter.org/database.html
2. M. J. Handel, "The O*NET content model: Strengths and limitations," J. Labour Market Research, vol. 49, no. 2, pp. 157-176, 2016, doi: 10.1007/s12651-016-0199-8.
3. Y. Mashayekhi et al., "A challenge-based survey of e-recruitment recommendation systems," ACM Computing Surveys, vol. 56, no. 10, 2024, doi: 10.1145/3659942.
4. N. Dawson, M.-A. Williams, and M.-A. Rizoiu, "Skill-driven recommendations for job transition pathways," PLOS ONE, vol. 16, no. 8, e0254722, 2021, doi: 10.1371/journal.pone.0254722.
5. J. Rosenberger et al., "CareerBERT: Matching resumes to ESCO jobs in a shared embedding space for generic job recommendations," Expert Systems with Applications, vol. 275, 127043, 2025, doi: 10.1016/j.eswa.2025.127043.
6. N. Tintarev and J. Masthoff, "Evaluating the effectiveness of explanations for recommender systems," UMUAI, vol. 22, no. 4-5, pp. 399-439, 2012, doi: 10.1007/s11257-011-9117-5.
7. Y. Zhang and X. Chen, "Explainable recommendation: A survey and new perspectives," Foundations and Trends in IR, vol. 14, no. 1, 2020, doi: 10.1561/1500000066.
8. P. Pu, L. Chen, and R. Hu, "A user-centric evaluation framework for recommender systems," RecSys 2011, pp. 157-164, doi: 10.1145/2043932.2043962.
9. K. Jarvelin and J. Kekalainen, "Cumulated gain-based evaluation of IR techniques," ACM TOIS, vol. 20, no. 4, pp. 422-446, 2002, doi: 10.1145/582415.582418.
10. M. D. Smucker, J. Allan, and B. Carterette, "A comparison of statistical significance tests for information retrieval evaluation," CIKM 2007, pp. 623-632, doi: 10.1145/1321440.1321528.

## 10. Decisions and questions for the lecturer

1. **Paper type.** An evaluation-focused paper (recommended, but it needs the human studies) or a system description with preliminary results?
2. **Ethics.** Who submits to the KIIT ethics committee, and which form applies? Can the drafts in `research/instruments/` be the starting point?
3. **Reviewers.** Who can serve as the three independent reviewers (for example a career counsellor and two faculty members)?
4. **Recruitment.** Which schools and student groups may be approached, and how?
5. **Education component.** It changed no ranking. Keep it with a discussion, drop it from the model, or test it on purposely varied profiles?
6. **Semantic baseline.** Is B4 required for the first paper, given the extra dependency and time?
7. **Unmatched careers.** Accept nearest-broader O*NET mappings for Data Analyst, ML Engineer and Mobile App Developer, or keep them unmatched?
8. **Pre-registration.** Should hypotheses be registered (for example on OSF) before the human studies?
9. **Licence.** Which licence for code and data?
10. **Authorship and affiliation** on the paper.
11. **Scope of the comparison dataset.** O*NET as the primary comparison, with ESCO as future work: is this acceptable?

## 11. Completion checklist

| Item | Status |
|---|---|
| System, dataset, explanations, skill-gap module | Complete, verified (275 tests pass) |
| O*NET comparison and mapping audit | Complete; 3 careers unresolved; audit titles not machine-checked |
| DevOps mapping correction | Complete (dataset v1.2.0) |
| Baselines B1, B2, B3, B5, B6 | Complete, reproducible |
| Ablations (interests, education, preferred) and weight variants | Complete, reproducible |
| NDCG, randomisation test, Holm correction | Complete, unit-tested |
| Results report from actual outputs | Complete (`results_and_analysis.md`) |
| Logistic Regression, Decision Tree, Random Forest, XGBoost (grouped nested CV) | Complete, reproducible; none beats the formula (`ml_experiments.md`) |
| Semantic baseline B4 | Not started |
| Held-out synthetic profile set | Not started |
| Ethics application | Not started (lecturer guidance needed) |
| Consent form, profile form, reviewer guide, questionnaire | Drafted, need review |
| Independent labels from real profiles | Not started (needs approval) |
| User study | Not started (needs approval) |
| Full systematic literature search | Not started; starting set verified |
| Licence file | Missing |
| Editable versions shared with the supervisor | Exist; the venue section of the earlier research plan is no longer needed, because the lecturer manages publication |

## 12. Local changes made for this package (not committed)

| File | Change |
|---|---|
| `data/raw/careers.csv` | C013 DevOps Engineer: onet_code 15-1252.00 and its O*NET OnLine URL (one line) |
| `docs/dataset_documentation.md` | Version 1.2.0; 47 mapped careers; DevOps and AI Research Scientist listed as nearest-broader |
| `tests/test_url_checker.py` | Expected career source URLs 46 to 47 |
| `src/evaluation/metrics.py` | Added `ndcg_at_k`, `paired_randomization_test`, `holm_adjust` |
| `src/evaluation/research_experiments.py` | New: baselines, ablations, tests |
| `tests/test_research_experiments.py` | New: 7 tests |
| `reports/research_results.json` | New: saved results |
| `src/ml/` | New: features, models, `TrainedRanker` (not used by the app) |
| `src/evaluation/ml_experiments.py`, `ml_interpretation.py` | New: ML comparison and interpretation |
| `tests/test_ml.py` | New: 16 tests |
| `reports/ml_results.json`, `reports/ml_interpretation.json` | New: saved ML results |
| `requirements-research.txt` | New: xgboost for research only |
| `research/` | All documents, instruments and the mapping audit |

Unchanged: production scoring weights, the scoring and ranking code, the labelled profiles, the original evaluation report and its results file, and the app.
