# Expansion evaluation plan (future stage, not started)

The 14 careers added in dataset v1.3.0 have **not** been evaluated. No result in `reports/` describes them.

## What exists today

| Item | Covers | Status |
|---|---|---|
| `data/evaluation/catalog_v1.2.0/` | Original 50 careers | Frozen, SHA-256 checked |
| `data/evaluation/labelled_profiles.json` | 36 synthetic profiles, author labels for the 50 careers | Unchanged |
| Five saved reports | 50-career catalogue only | Unchanged; tests check their fingerprints |

None of the 36 profiles targets mining, law, social science or community relations. Using those profiles on the 64-career catalogue would treat every new career as "not relevant" by default. It would also lower Precision@5, Recall@5, MAP and R-precision for reasons unrelated to quality.

## What the current recommendation tests show, and what they do not

`tests/test_african_expansion.py` has three kinds of recommendation test for the 14 new careers.

| Test | Profile | What it shows |
|---|---|---|
| `test_each_career_is_recommended_for_a_matching_profile` | Every required and preferred skill of the career, its interests and its level | The score of 100 follows from the formula, so it only shows the data loads correctly. The useful part is the rank: no other career beats the target on its own profile, and a tie can only be with other careers that also score 100 |
| `test_partial_learner_profile_ranks_target_first` | 3 of 4 required skills, typed in mixed case and partly in French, 2 interests, no preferred skills | The career ranks first with a margin of at least 5 points, the missing skill is reported, and aliases and accents reach the right skill |
| `test_earth_science_trio_is_distinguished` and `test_new_careers_do_not_crowd_unrelated_profiles` | Partial trio profiles; software and nursing profiles | Mining, Geological and Geotechnical Engineer separate on their own skills. No new career enters the top 5 for the two unrelated profiles |

Limitations:

1. **Circular profiles.** Every test profile was written by the same author, from the same curated skill lists the engine scores against. The tests show that the data and the engine are consistent. They do not show that a real mining or law student would enter these skills, or that the careers suit them.
2. **Shared vocabulary.** The profiles use skill names the catalogue knows, including the new aliases. A learner who describes the same knowledge in other words ("droit des affaires", "topographie") gets an unknown-skill message, not a match.
3. **Few contrasts.** Only two unrelated profiles are tested for crowding. Overlaps such as Laboratory Technician against Medical Laboratory Technologist, or MIAGE against Computer Systems Analyst, have one partial profile each.
4. **No relevance labels.** No test says which careers *should* rank highly for a learner. That needs the independent labels in the plan below.

## Plan

1. **Ethics.** Obtain KIIT ethics approval before recruiting any person (see `research/experimental_protocol.md`, Part B).
2. **Profiles.** Collect new profiles that cover all 10 categories, including at least 5 each for mining and earth sciences, law, social sciences and community relations. Adult volunteers only, anonymised, with consent.
3. **Independent labels.**
   - Three reviewers who are not the project author grade every pooled career for each profile (0, 1 or 2).
   - Reviewers include someone familiar with Guinean or West African employment.
   - Report agreement with Fleiss' kappa before adjudication.
4. **Freeze.** Tag the commit and copy `data/raw/` to `data/evaluation/catalog_v1.3.0/` with SHA-256 values. The `.gitattributes` rule `data/evaluation/catalog_*/** -text` already protects it.
5. **Run.** Use the same metrics and scripts, pointed at the v1.3.0 snapshot, and write new report files (for example `reports/evaluation_results_v1.3.0.json`). Never overwrite the v1.2.0 reports.
6. **Report.** Present the 64-career results as a new study, alongside the 50-career results, never merged with them.
7. **ML models.** Retrain only on the new independent labels; until then the live comparison keeps training on the v1.2.0 labels and says so.

## What must not be claimed before this plan is done

- That the new careers are recommended accurately.
- That the 50-career MAP (0.971) or any other saved metric applies to the 64-career catalogue.
