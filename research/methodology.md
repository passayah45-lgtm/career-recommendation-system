# System design and methodology

Describes the implemented system as of 26 October 2026 (commit 3f8d67b plus the local changes listed in `supervisor_review_package.md`). Facts were checked in the source code; file paths are given so the lecturer can verify each one.

Three things are kept separate throughout: the **dataset** (CSV files), the **recommendation algorithm** (engine and services) and the **deployed application** (Streamlit app).

## 1. Architecture

| Layer | Modules | Responsibility |
|---|---|---|
| Interface | `app.py`, `pages/` | Six Streamlit pages; display only, no scoring |
| UI helpers | `src/ui/` | State, components, charts |
| Services | `src/services/recommendations.py`, `skill_gap.py`, `profiles.py`, `catalog.py`, `learning_resources.py` | `recommend()` and `analyze_skill_gap()` take and return plain dictionaries |
| Engine | `src/engine/matching.py`, `scoring.py`, `ranking.py`, `explanations.py` | Matching, scoring, deterministic ranking, explanations; no Streamlit or network imports |
| Data | `data/raw/*.csv`, `src/data/validation.py` | Catalogue files and a validator that never repairs data |

Each layer calls only the one below it. The services return plain dictionaries, so the same functions can later sit behind a REST API for the T-Career platform without changing the engine.

## 2. Dataset

| File | Rows | Content |
|---|---|---|
| `careers.csv` | 50 | Id, title, category (8), description, required skills (3 to 5), preferred skills, education level (0 to 4), interests, 3 learning goals, O*NET code and URL |
| `resources.csv` | 114 | One free learning resource per canonical skill, with verification status |
| `skill_aliases.csv` | 37 | Alternative names mapped to canonical skills |

Vocabulary: 102 unique required skills and 48 preferred skills (114 unique in total); 20 controlled interest terms. 47 careers link to an O*NET-SOC occupation and 3 do not. The O*NET link records occupation identity only; skills, interests, education levels and descriptions are curated by the author. Per-career mapping types are in `research/data/onet_mapping_audit.csv`, and the full comparison is in `dataset_comparison.md`.

## 3. Profile processing

`src/services/profiles.py`:

1. Skills and interests arrive as lists of free text; education as an optional integer from 0 to 4.
2. Each skill is cleaned (lowercase, single spaces, punctuation removed) and mapped through the alias file to a canonical name.
3. Unrecognised skills and interests are set aside and reported back to the learner, never silently dropped.
4. Duplicates are removed, keeping first-seen order.

## 4. Matching

`src/engine/matching.py`. For each career:

- Required and preferred skills are split into matched and missing by exact membership after normalisation.
- Interests are matched by exact membership in the career's interest list.
- Education gap = career level minus learner level, floored at 0; undefined if the learner gives no level.

## 5. Scoring formula

`src/engine/scoring.py`. Four component values, each between 0 and 1:

| Component | Value | Weight |
|---|---|---|
| Required skills | matched required / number of required skills | 0.55 |
| Preferred skills | matched preferred / number of preferred skills | 0.15 |
| Interests | matched interests / number of career interests | 0.25 |
| Education | 1 minus 0.25 per level below the career level, floored at 0; 0 if no level is given | 0.05 |

Score = 100 × Σ (w_c × v_c) / Σ w_c, where the sums run over applicable components.

A component is not applicable only when the career has nothing to compare (for example no preferred skills). Missing learner input stays applicable and scores 0, so it never counts as a match. Scores are clamped to the range 0 to 100.

**Worked example** (from `docs/recommendation_algorithm.md`, reproduced by the engine): a learner with Python, SQL, Excel, machine learning and statistics, interests in analysis and mathematics, and a bachelor's degree scores 61.5 for Data Scientist. That is 0.80 × 55 = 44.0 for required skills, 0 for preferred, 0.50 × 25 = 12.5 for interests and 5.0 for education.

## 6. Weighting strategy

The weights were set by the author from the structure of the data, before any evaluation, and were not tuned on the profiles:

- Skills carry 0.70 in total because required skills define whether a person can do the work.
- Interests carry 0.25 as a secondary signal for fit and motivation.
- Education carries 0.05 because 42 of 50 careers share level 3, so it separates careers very little; the documentation states it must never act as a hard filter.

Evidence so far (`results_and_analysis.md`): on synthetic profiles, alternative weightings and single-component removals change MAP by at most 0.030, and no difference is significant after correction. The weights should be presented as a transparent, reasonable choice, not an optimised one.

## 7. Ranking

`src/engine/ranking.py`. Careers are sorted by:

1. Score, descending (rounded to 9 decimals).
2. Required-skill coverage, descending.
3. Number of matched required skills, descending.
4. Career id, ascending.

The same input therefore always gives the same ranking.

## 8. Explanations

`src/engine/explanations.py`. Each recommendation carries:

- The four component values, weights and point contributions.
- The matched and missing required and preferred skills.
- The matched interests.
- Notes for unknown skills or missing input.

Explanations are built only from values used in the calculation. They have not yet been evaluated with users.

## 9. Skill-gap analysis

`src/services/skill_gap.py`, `analyze_skill_gap(profile, career_id)` returns:

- The skills the learner has and lacks, separately for required and preferred skills.
- Required, preferred and overall coverage, and whether all required skills are met.
- Unknown skills and the career's learning goals.
- For each missing skill, its free resource from `resources.csv`, grouped as required or preferred.

## 10. Evaluation code

| Module | Purpose |
|---|---|
| `src/evaluation/metrics.py` | P@K, attainable P@K, R@K, F1, Hit@K, MRR, R-precision, AP, NDCG@K, bootstrap CI, sign-flip randomisation test, Holm correction |
| `src/evaluation/experiments.py` | Original study: weight configurations A to D, output `reports/evaluation_results.json` |
| `src/evaluation/research_experiments.py` | Baselines and ablations, output `reports/research_results.json` |
| `tests/test_evaluation.py`, `tests/test_research_experiments.py` | Hand-checked metric values and byte-for-byte reproducibility of both reports |

## 11. Session feedback (per-student adaptation)

Added 27 October 2026. The app adapts one student's ranking during their visit, without storing anything.

- **Input:** on the Recommendations page the student marks careers as *Interested* or *Not for me*.
- **Similarity** between two careers: 0.6 × Jaccard overlap of their required and preferred skills + 0.4 × (same category), between 0 and 1. Pairs below 0.15 are ignored.
- **Adjustment** for each unrated career: the sum over rated careers of (+1 or -1) × 10 points × similarity, limited to ±15 points. The adjusted score is the formula score plus the adjustment, kept between 0 and 100.
- **Ranking:** careers are re-ranked by adjusted score. Since 28 October 2026, careers marked *Interested* or *Not for me* leave the main list and appear in two separate lists with counts, where the student can open details and skill gaps, switch lists or remove the mark. The main list is renumbered from 1 and shows only careers not rated yet.
- **Explanation:** each card shows the formula score, the adjustment and one line per rated career that caused it. The formula score itself is never changed.
- **Privacy:** answers and feedback live only in the Streamlit session. The two lists are also written to the page address as career ids (`?interested=...&not_for_me=...`), so a refresh restores them; unknown ids and ids in both lists are dropped. No server-side storage is used and no answers go into the address. The student can download a `career_session.json` file and upload it later. The file is validated (format, version, size, known careers and values) before use.
- **Code and tests:** `src/services/feedback.py`, `src/services/session_data.py`, `tests/test_feedback.py`, and interaction tests in `tests/test_app.py`.

This is relevance feedback within one session. It does not retrain the machine-learning models and is not evaluated with real students yet.

## 12. Live model comparison (demonstration only)

Added 28 October 2026. The Model comparison tab on the Analytics page ranks the learner's saved answers with the weighted formula and with Logistic Regression, Decision Tree and Random Forest, and shows each method's top 5 with scores and explanations. The formula is labelled as the primary method; the models are labelled as comparison only. All methods use the same 50 careers and 13 features. The models are trained once per server process on the 1,800 labelled synthetic pairs and reused. XGBoost stays offline. Full setup, explanation methods, measured times and limits are in `ml_experiments.md`, sections 8 and 9.
