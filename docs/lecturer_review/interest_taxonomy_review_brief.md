# Career interest taxonomy: academic review brief

Prepared for lecturer review, November 2026. Repository: https://github.com/passayah45-lgtm/career-recommendation-system (commit 593b87e on `main`).

This brief summarises two research reports and asks for decisions. It proposes changes but does not make them. The proposed taxonomy has not been approved by a lecturer and is not academically validated.

## Documents in this package

| Document | Content |
|---|---|
| `interest_taxonomy_review_brief.md` | This brief |
| `proposed_interest_taxonomy.md` | The 23 proposed interests with explanations, examples, related skills, RIASEC group and status |
| `career_interest_assignments.md` | Three proposed interests for each of the 64 careers, with confidence and O*NET reference. The 12 provisional careers are listed first |
| `riasec_classification_review.md` | How RIASEC is used, what the O*NET evidence supports, and what remains uncertain |
| `lecturer_decision_checklist.md` | Seven decisions, with space for comments and approval status |
| `change_summary.md` | Verified figures, discrepancies found, and differences between the two reports |

Source reports (in `docs/`): `skills_interests_audit.md` (first audit) and `interest_taxonomy_second_review.md` (second review, the main source for this package).

## 1. Project background

The Career Recommendation System is a Streamlit application built for a KIIT MSc assignment, designed for later integration with T-Career. A student enters skills, interests and education level. The system ranks 64 careers in 10 categories (catalogue v1.3.0) with a fixed, explainable formula:

| Component | Weight |
|---|---|
| Required skills | 0.55 |
| Preferred skills | 0.15 |
| Interests | 0.25 |
| Education | 0.05 |

The application also shows the skill gap for each recommended career. The catalogue began with 50 careers and was expanded to 64, with 14 careers added for African contexts (for example Mining Engineer, Geotechnical Engineer, Private and Public Law, MIAGE).

Two evaluations exist and are frozen:
- the original 50-career evaluation.
- an independent 64-career evaluation (eval64_v1: 111 synthetic profiles and 363 graded labels).

Both use synthetic profiles labelled by one author. The second independent review of the labels has not yet been done.

## 2. Purpose of career interests in the system

Interests carry a quarter of the score. For each career, the interest value is the share of that career's listed interests that the student selected.

The frozen sensitivity analysis on eval64_v1 shows that interests matter a lot: without them, NDCG@5 falls from 0.759 to 0.560. Interests let the system suggest careers whose skills a student does not yet have. This matters for a skill-gap tool aimed at students.

## 3. Difference between skills and interests

The first audit used these definitions:
- **Skill:** an ability, knowledge or competency a person has or develops (for example Python, statistics, patient care).
- **Interest:** a work activity, professional environment or task a person enjoys and prefers (for example "Analysing data and information").

A concept may appear on both sides only when the meaning differs. Enjoying research is an interest. Knowing research methods is a skill.

## 4. Problems in the current taxonomy

The current vocabulary has 20 terms. The first audit found:

1. **An exact duplicate.** "communication" is both a skill and an interest. Five careers (C033, C035, C037, C038, C064) list it in both, so one concept is counted twice.
2. **The same concept on both sides.** In 40 careers (54 pairs), an interest repeats a skill, for example "mathematics" with "statistics".
3. **Category names used as interests.** Seven of the ten categories have a matching interest word (business, healthcare, engineering, design, security, teaching, building software).
4. **Abilities listed as interests.** Problem solving, communication, leadership, organization, mathematics, analysis.
5. **Weak differentiation.** "technology" is on 26 of 64 careers. Only 50 of 64 careers have a distinct interest set. For example, Nurse, Pharmacist, Dietitian and Physical Therapist share one set.
6. **A loophole in the form.** A student can select all 20 interests. Every career then gets the full 25 points, and the ranking equals the skills-only ranking.
7. **Unequal list lengths.** 12 careers have four interests (6.25 points per match) and 52 have three (8.33 points per match). 11 of the 12 were added in v1.3.0.
8. **Labelling errors.** Mechanical Engineer has the interest "building software". "design" covers both visual and technical design.

## 5. Proposed improvements

- Interests written as work activities, with no category names or abilities.
- A vocabulary of 23 interests, each with a short explanation, an example and a related skill to show the difference.
- Exactly three interests per career.
- Interests grouped under the six RIASEC types on the form, for display only.
- A selection limit in the form, so that selecting everything no longer works.
- The formula stays the same.

## 6. Summary of the second review

The second review re-examined the first audit's 21-term proposal and checked every career against O*NET OnLine interest codes (read on 2 November 2026).

| Finding | Detail |
|---|---|
| Vocabulary | 23 terms: 12 retained, 6 renamed (one only reordered), 3 first-audit terms split or replaced into 4 terms, 1 new money term |
| Assignments | 18 of 64 careers changed substantively. The other 46 keep the draft apart from renamed terms |
| O*NET agreement | Of 48 careers with a full O*NET code, 41 agree on all three interests and 7 on two of three |
| Confidence | 31 High, 21 Medium, 12 Provisional (no O*NET code) |
| Differentiation | 58 distinct combinations of 64. 6 identical pairs, all between closely related careers |
| Broad term | "Keeping information, records and procedures in order" is on 18 careers |
| Selection limit | 1 to 5 is reasonable but untested. Recommended: a soft warning above 5, then an experiment before any hard cap |

Full figures and the discrepancies found are in `change_summary.md`. For example, the request for this package said 11 retained terms, but the report's table has 12.

## 7. Effect on the student assessment interface (proposed, not implemented)

- A short explanation above the form: skills are what you can do, interests are work you enjoy, even without the skills yet.
- 23 interests, each with a one-line explanation, shown under six RIASEC headings.
- A selection limit (form and size to be decided, see decision 6).
- "communication" removed from the interest list. It stays a skill.
- Old interest names in saved sessions and links mapped to the new names.
- A French version of the descriptions, recommended but not yet written.

## 8. Academic limitations

1. **O*NET reflects US occupational classifications.** Interest patterns for the same job title in Guinea or West Africa may differ. No African occupational interest data was found.
2. **Some careers lack verified O*NET codes.**
   - 12 careers have no O*NET code.
   - 8 map only to a broader O*NET occupation.
   - For 4, only the first interest type (Realistic) could be read.
   - Codes were read from O*NET list pages with a web tool, with letters only and no scores. The pages do not define letter order.
3. **The career assignments require lecturer review.** All 64 assignments, and above all the 12 provisional ones, are the author's proposals.
4. **Synthetic evaluation results do not establish real-world accuracy.** eval64_v1 uses invented profiles labelled by one author, with no second reviewer yet. Its metrics measure agreement with those labels, not employment or study outcomes.
5. **The interest taxonomy has not received independent lecturer approval.** It is a research proposal and must not be described as validated.
6. **The selection limit needs further evaluation.** No synthetic profile in either evaluation uses more than 4 interests, so no limit has been tested. The simulation in the second review uses random selections, which are only a rough guide.
7. **The RIASEC grouping is an interpretation.** O*NET classifies occupations, not this project's interest terms. Several placements are uncertain (see `riasec_classification_review.md`).
8. **The proposed changes would alter the original 50 career records.** Only their interest data would change, not IDs, titles, categories or skills. The frozen evaluations keep the old data, and a new, separate evaluation would be needed.

## 9. Decisions required from the lecturer

Details, options and space for comments are in `lecturer_decision_checklist.md`.

1. Approval of the proposed 23 interest terms.
2. Approval of the career-interest assignments.
3. Review of the 12 provisional careers.
4. Approval of the RIASEC groupings.
5. Approval of the interest descriptions and French translations.
6. Approval of the interest selection limit.
7. Approval of the O*NET validation approach.

No implementation will start until the lecturer's feedback and the final taxonomy are approved.
