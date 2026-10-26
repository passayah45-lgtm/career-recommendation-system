# Research implementation roadmap

Status update, 26 October 2026: items 2 (configurations), 3 (random and popularity baselines), the NDCG part of item 4, and item 5 (paired test and Holm, numpy-free, in `src/evaluation/metrics.py`) are done in `src/evaluation/research_experiments.py`. The DevOps fix from item 1 is done in `careers.csv`; the mapping-type column is kept in `research/data/onet_mapping_audit.csv` instead of the data schema. Still open: graded labels, separate evaluation sets, freeze tag, licences, semantic baseline.

The smallest changes needed for a credible study, based on the code as of commit 3f8d67b. No change to the production scoring weights or the app is required. All new methods are added as evaluation configurations or separate modules, so the 268 existing tests keep passing.

## 1. Completed and verified

| Item | Evidence |
|---|---|
| Curated catalogue: 50 careers, 114 skills, 114 resources, 37 aliases | `data/raw/*.csv`; validator reports 0 errors |
| Weighted scoring with component breakdown | `src/engine/scoring.py` (`ScoringWeights`, `score_match`) |
| Required and optional skill gaps with resources | `src/services/skill_gap.py`, `src/services/learning_resources.py` |
| Synthetic evaluation with MRR, R-precision, MAP, P@5, R@5, coverage, bootstrap CIs | `src/evaluation/metrics.py`, `src/evaluation/experiments.py` |
| Reproducibility check | `python -m src.evaluation.experiments --check reports/evaluation_results.json`; enforced by `tests/test_evaluation.py` |
| Weight configurations A, B, C and the skills-only ablation D | `CONFIGURATIONS` in `src/evaluation/experiments.py` |

## 2. Partially implemented

| Item | What exists | What is missing |
|---|---|---|
| O*NET provenance | `onet_code`, `source_url` for 47 careers (DevOps added); mapping types in `research/data/onet_mapping_audit.csv` | O*NET release recorded; 3 unmatched careers checked |
| Ablations | D removes interests and education together | Separate removal of interests, education and preferred skills |
| Labels | 36 binary author labels | Graded labels; independent reviewers; held-out set |
| Statistics | Bootstrap CIs | Paired significance tests, effect sizes, multiple-comparison correction |

## 3. Required for research validity (in order)

1. **Provenance columns** (data only). Add `onet_mapping` (exact, nearest_broader, none) and `onet_release` to `careers.csv`; set C013 DevOps Engineer to 15-1252.00 as nearest_broader, or document why not; mark C007 as nearest_broader. Update the validator's schema and `docs/dataset_documentation.md`. Why: reviewers will ask exactly what came from O*NET.
2. **More configurations** (no new engine code). `ScoringWeights` already accepts zero weights as long as one is positive, so add to `CONFIGURATIONS`: interests only (0, 0, 1, 0); skills and interests (0.35, 0.15, 0.5, 0); no interests (0.55, 0.15, 0, 0.05); no education (0.55, 0.15, 0.25, 0); no preferred (0.55, 0, 0.25, 0.05). Keep A as the reference. Why: baselines B2, B3 and single-component ablations.
3. **Random baseline** (small module). `src/evaluation/baselines.py` returning a seeded random ranking and a popularity ranking computed from Track A labels only. Why: sanity floor.
4. **Graded labels and NDCG@5** (metrics). Extend `labelled_profiles.json` loader to accept `relevance_grades` (0, 1, 2) alongside the current list; add `ndcg_at_k` to `metrics.py` with unit tests. Why: Track B uses graded labels.
5. **Paired tests** (metrics). Add Wilcoxon signed-rank, paired randomisation test and Holm correction. scipy is not in `requirements.txt`; either add it to a separate `requirements-research.txt` or implement the randomisation test with numpy only. Why: hypotheses H1 to H3.
6. **Separate evaluation sets** (data layout). `data/evaluation/track_a_dev.json` (current 36), `track_a_holdout.json` (new, written before any change) and a private, git-ignored `track_b/` folder for real profiles and reviewer labels. Why: leakage control.
7. **Freeze tag and pre-registration.** Tag the commit that fixes all methods before Track B labels are opened. Why: credibility of the main results.
8. **Licences.** Add `LICENSE` (code) and a data licence note with O*NET attribution (CC BY 4.0). Why: required to release the artefact.

## 4. Optional future improvements

| Item | Note |
|---|---|
| Semantic baseline B4 | New `src/engine/semantic.py` using a sentence-embedding model; threshold tuned on Track A only; model name and version pinned. Larger dependency footprint, so keep it outside the app's requirements |
| ESCO cross-check | Map careers through the ESCO and O*NET crosswalk and compare skill lists |
| Free-text profile parser | Needed if Track B collects skills as free text without B4 |
| Diversity metric | Distinct categories per top 5 |
| Docker file | For exact environment reproduction |

## Changes that should not be made before the study

- Do not change the production weights in `DEFAULT_WEIGHTS` or tune them on any profile set.
- Do not add aliases or skills after reading Track B profiles.
- Do not edit `labelled_profiles.json` labels; add new sets instead.
