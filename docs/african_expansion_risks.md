# African career expansion: risks report

Dataset v1.3.0. Updated 1 November 2026 after the final checks. Unresolved issues are listed, not hidden.

| # | Area | Risk | Severity | Current state | Mitigation or next step |
|---|---|---|---|---|---|
| 1 | Occupational overlap | Mining, Geological and Geotechnical Engineer share rock mechanics, geology and gis. O*NET treats mining and geological engineering as one occupation | Medium | Kept separate as instructed. Different required skills, and partial profiles for each rank the right one first among the three (tested) | Explain the difference in the Explorer descriptions; review after user feedback |
| 2 | Occupational overlap | Laboratory Technician (C062) is close to Medical Laboratory Technologist (C042); Building Engineer is close to Civil Engineer (C046); MIAGE is close to Computer Systems Analyst (C016); Business Administration Specialist is close to Management Analyst (C028) | Medium | Separate records with different skills and education levels. One partial profile each ranks the new career first (tested) | Monitor rankings where both appear; refine descriptions if learners are confused |
| 3 | Category fit | Geophysicist is in Engineering and Laboratory Technician in Healthcare, because no Natural Sciences category was created | Low to medium | Reasons documented | Revisit if the lecturer wants a Natural Sciences category |
| 4 | Limited African occupational data | Occupation references are O*NET (US), BLS (US) and ESCO (Europe). No African national framework was used | High | Documented per career | Seek national classifications (for example Guinean or ECOWAS frameworks) |
| 5 | Qualifications | All 14 education levels are the author's estimates. 5 agree with a US reference (O*NET or BLS); 9 have no reference. Geophysicist's level 3 is the most common US answer, but 44% of US respondents report a graduate degree | Medium | Split recorded per career in `research/data/expansion_education_basis.csv` and checked by a test | Validate with Guinean universities and professional bodies |
| 6 | Country-specific legal requirements | Practising law needs national bar or professional admission. Law resources are US texts plus OHADA Uniform Acts (OHADA states only) | High | Notes in each resource row and in the documentation | Add French-language, Guinea-specific legal resources when verified free sources are found |
| 7 | Link checking | The project link checker ran on all 30 new links, but the workspace network policy refused every connection (29 inconclusive, 1 blocked). A web tool loaded all 30 pages and found no broken link | Medium | Status stays `search_index_confirmed`; results in `docs/african_expansion_link_check.md` and `research/data/url_check_expansion_2026-11-01.json` | Run `python -m src.data.url_checker --apply` from a machine with normal internet access |
| 8 | Link stability | R120 works only through a redirect (github.com/ubcgif/gpg to geoscixyz/gpg). R137 has "/I/" in capitals in its WHO path | Low | Both load today; not replaced because neither is broken | Recheck both on the next checker run; switch R120 to the target URL if the redirect stops |
| 9 | Resource level and fit | Two resources are graduate level (MIT 12.524, 1.361). The geophysics link is a source repository. The OHADA texts come from a private association, not the official OHADA site | Medium | Noted in each resource row | Replace with beginner resources when found |
| 10 | Resource access conditions | Several resources are free to read but non-commercial (CC BY-NC or BY-NC-SA). R143 names two different licences. The WHO quality handbook states no licence. OpenStax pages forbid use of the books for training language models | Low | Licence noted per row; R143 noted as BY-NC-SA | Recheck terms before any commercial T-Career use |
| 11 | Skill gaps | Econometrics, legal writing, engineering geology, mineral processing, fiber optics, building codes, erp systems and sample preparation are missing because no free resource was verified | Medium | Documented in `docs/african_expansion_sources.md` | Add each skill together with a verified resource |
| 12 | Recommendation tests are partly circular | Test profiles are written from the same curated skill lists that the engine scores against. The full-match test scores 100 by construction | Medium | Partial, mixed-case, French-alias profiles, a trio test and two unrelated-profile tests were added. Limits documented in `docs/expansion_evaluation_plan.md` | Independent profiles and labels (evaluation plan) |
| 13 | Recommendation bias | New careers mostly use new skills, so learners who enter only the original vocabulary rarely see them. In exact ties, new ids (C051 to C064) rank after older careers | Medium | Partial profiles rank each new career first with a margin of at least 5 points (tested) | Review alias coverage, especially French terms |
| 14 | Recommendation bias | The law and social science careers require level 4, so learners at level 3 lose up to 1.25 points on those careers (education weight 0.05) | Low | Formula unchanged | Accept; document |
| 15 | Evaluation limits | The saved evaluation covers only the original 50 careers; no labels exist for the new careers | High | Frozen snapshot; report fingerprints tested; captions say the results do not cover careers added later | Follow `docs/expansion_evaluation_plan.md` |
| 16 | Live ML comparison | The models train on the 50-career labels and rank 64 careers, so their rankings of new careers are untested | Medium | The page states the training catalogue | Retrain only on independent labels |
| 17 | Technical | Counts, categories and colours changed in several places | Low | Manifest-driven counts, 10 colours, Analytics and filter tests pass | None beyond the existing tests |
| 18 | Technical | Accented French aliases rely on accent folding | Low | Tests cover accented, unaccented and capital forms | Keep the alias-collision rule in the validator |
| 19 | Data integrity | Edits on Windows could change line endings in the CSV files | Low | `.gitattributes` keeps the bytes; the original file bytes are an exact prefix of each live CSV (checked) | None |

## Unresolved resource links

No link is known to be broken. These remain open:

| Item | IDs | What is missing |
|---|---|---|
| Project link checker not completed | R115 to R144 (all 30) | A run of `src/data/url_checker.py` from a machine with normal internet access |
| Redirect | R120 | Stored URL redirects to github.com/geoscixyz/gpg |
| Unusual path | R137 | WHO URL with "/I/" in capitals |
| Licence unclear | R143 (two licences named), R138 (no licence stated) | Confirmation from the publisher |
