# Second-review guide for eval64_v1

This guide is for a person who will grade career relevance independently of the first labeller. No reviewer grades exist yet. No agreement statistic has been calculated, and none will be until a real reviewer completes the sheet.

## 1. Who can review

- A lecturer, career adviser, or someone who knows the occupations in a category well. Several reviewers may each take a full sheet; do not split one sheet between people.
- The reviewer must not have seen the original labels, the evaluation results, the project repository, or the app's output for these profiles.
- The first labeller (Claude, the AI assistant) cannot be the second reviewer.

## 2. Materials

The reviewer receives an anonymised bundle:

| File | Use |
|---|---|
| `reviewer_handover.md` | Purpose, independence rules, submission and declaration |
| `second_review_guide.md` | This guide |
| `reviewer_packet.md` | Each profile, then its careers with title, job description and usual entry level. Profiles and careers carry random codes (PR-001, JOB-K7Q2) |
| `reviewer_sheet.csv` | Blank sheet, 585 rows: profile code, career code, career title, and four columns to fill |

**Do not open** the project repository, the original labels, the evaluation results or the app for these profiles before you finish.

## 3. What you are grading

- There are 111 profiles × 64 careers = 7,104 possible pairs. **You grade 585 selected pairs, not all 7,104.** Each profile lists between 4 and 9 careers.
- **How the pairs were chosen:** for each profile, every career the first labeller considered, plus 2 careers drawn at random from the others. The careers were then shuffled, and profiles and careers were given random codes.
- You are not told which careers came from which part. Some listed careers will look clearly unrelated; grade them like any other row (usually 0).
- The selection over-represents careers the first labeller thought about, so your results are analysed with that design in mind (section 7).

## 4. The task

1. Copy `reviewer_sheet.csv` to a new file, for example `reviewer_sheet_AB.csv` (your initials).
2. For each profile in the packet, read the learner, the goal, the skills, interests, education and experience.
3. For each career listed under that profile, decide how relevant the career is **for that learner**, using the scale below.
4. In your copy, fill four columns on that row, without changing the codes or titles:
   - `relevance_label`: 0, 1, 2 or 3
   - `justification`: one short sentence, in your own words
   - `reviewer`: your name or role, the same on every row
   - `confidence`: high, medium or low
5. Fill every row. A partly completed sheet is rejected by the analysis.

Expected time: about 3 to 4 hours for 585 rows.

## 5. Scale

| Grade | Name | Use it when |
|---|---|---|
| 3 | Strong | The learner's skills, education and goal fit the central work of the occupation. They could apply now, or after an ordinary step such as finishing their current degree |
| 2 | Moderate | A realistic option: substantial overlap with the job's central work, or a stated goal plus a solid partial foundation. Needs more study or experience, but not a change of field |
| 1 | Weak | Related or adjacent. Some skills transfer, or only the interest matches. Reaching the job needs major retraining, or it goes against the learner's goal |
| 0 | Not relevant | No realistic link, or a link that would mislead |

## 6. Rules

1. **Judge the occupation's real work,** not word overlap. A learner who typed "routing and switching" knows networking, even if the words differ from a job description.
2. **A goal alone is not enough.** A stated goal can raise a career to 2 or 3 only when the learner also has a real foundation for it. A goal with no foundation is at most 1.
3. **Generic skills do not create relevance.** Communication, Excel, Git or teamwork alone never justify 2 or 3.
4. **Education lowers by at most one grade.** Education below the usual entry level lowers a grade by at most one step, and never makes a career 0 on its own.
5. **Licensed professions.** Nurse, pharmacist, physical therapist and lawyer stay at 1 or below when the learner has no training in that profession.
6. **Current job.** For a career changer, the job they are leaving is at most 1 if their goal is to leave it.
7. **Any number of relevant careers.** A learner may have several careers at 2 or 3, or none.
8. **Use your own knowledge** of the occupation and, where useful, public occupational descriptions you look up yourself (O*NET, ESCO, national frameworks). Note the source in the justification if you used one.
9. **Confidence:** choose low when a qualified colleague could reasonably pick the grade next to yours.

### When the information is not enough

Some profiles are short on purpose: a learner with only interests, one skill, or vague goals. Do not guess what the learner might also know.

1. Grade on what the profile states. Unstated skills count as absent.
2. If you still cannot choose between two grades, choose the lower one.
3. Set `confidence` to `low`.
4. Begin the justification with `INSUFFICIENT:` and say what is missing, for example `INSUFFICIENT: no skills given; interest in security only`.
5. Never leave a row blank. The analysis counts the `INSUFFICIENT:` rows separately, so they are visible in the results.

Other things to know:
- The "usual entry level" shown for each career is the catalogue's value. For some careers it is an estimate. Treat it as a guide, not a rule.
- Codes are random. They carry no category, order or meaning.
- The order of profiles, and of careers within each profile, is random.

### Worked examples (invented, not from the sheet)

| Learner | Career | Grade | Why |
|---|---|---|---|
| Final-year accounting student, goal: auditor | Accountant | 3 | Accounting and audit are the core of the job; the degree is nearly complete |
| Same student | Financial Analyst | 2 | Strong accounting base; needs valuation and modelling |
| Same student | Data Analyst | 1 | Spreadsheets transfer, but analysis and statistics are missing |
| Same student | Registered Nurse | 0 | Licensed profession with no nursing training |
| Secondary-school leaver who likes drawing, goal: designer | Graphic Designer | 2 | Real creative base; education below usual entry lowers it one step |

## 7. After the review (for the project author)

The project author receives the completed sheet and the signed declaration, then runs:

```
python -m src.evaluation.eval64_review_analysis reviewer_sheet_AB.csv --anonymised --confirm-independent-reviewer
```

- `--anonymised` maps the codes back with the private mapping (`data/evaluation/catalog_v1.3.0/review/private/anonymisation_map.json`), which is never sent to reviewers.
- `--confirm-independent-reviewer` records that a real person outside the project completed the sheet and signed the declaration.

The analysis refuses:
- the blank sheet;
- any missing grade, reviewer, justification or confidence;
- missing, extra, duplicated or changed rows, or unknown codes;
- a reviewer name that identifies the first labeller (Claude) or a test fixture;
- any run without the confirmation flag.

**Sampling design and how agreement is reported.** The 585 pairs are a stratified sample of the 7,104:

| Stratum | Pairs in population | Pairs reviewed | Inclusion probability | Design weight |
|---|---|---|---|---|
| Listed: pairs the first labeller graded explicitly | 363 | 363 (all) | 1 | 1 |
| Unlisted: pairs the first labeller did not list (grade 0 by rule R8) | 6,741 | 222 (2 per profile, random, seed 6464) | 2 / (64 − listed careers of the profile), 0.0323 to 0.0351 | 28.5 to 31 |

The sample is enriched: listed pairs are 5.1% of all pairs but 62% of the sheet. An ordinary weighted kappa on the 585 pairs therefore describes this enriched sample only, not the 7,104 pairs. The analysis reports:

| Statistic | Population it applies to |
|---|---|
| Weighted kappa (quadratic and linear), exact and within-one agreement, binary kappa at grade 2, on the listed stratum | The 363 listed pairs (a census of that set, so no pair-sampling error) |
| Share of unlisted pairs the reviewer grades 1+, 2+ and 3 (design-weighted), with an estimate of how many of the 6,741 that implies | The 6,741 unlisted pairs. Kappa is undefined here because the first labeller's grade is always 0 |
| Design-weighted kappa and agreement over all pairs, each reviewed pair weighted by 1 / inclusion probability | All 7,104 pairs. About 95% of the weight is unlisted pairs, so it mostly measures agreement on "not relevant" |
| Unweighted kappa on the 585 pairs | The review sample only. Reported for transparency, never as representative |

- Confidence intervals use a percentile bootstrap that resamples whole profiles (2,000 resamples, seed 64), because pairs from one profile are not independent.
- The listed stratum was chosen by the first labeller, not at random. Agreement there describes agreement on that labeller's judgements; it says nothing about pairs the labeller might have missed. The unlisted stratum covers those.

Outputs, in `reports/evaluation_64_review/<sheet name>/`:

| Output | Content |
|---|---|
| `review_summary.json` | All statistics above with their populations, confusion matrices, reviewer notes (`INSUFFICIENT:` rows, confidence counts), and the main metrics recomputed with the original labels, the reviewer's labels and a conservative consensus (the lower grade). Reviewer labels exist only for reviewed pairs; unreviewed unlisted pairs stay 0 |
| `review_by_category.csv` | Agreement and disagreement counts per profile category |
| `review_by_career.csv` | Agreement and disagreement counts per career |
| `review_disagreements.csv` | Every pair where the grades differ, for discussion |

- The analysis never overwrites `relevance_labels.csv`. Adjudicated labels, if wanted, become a new labelled version (`eval64_v2`) with its own manifest and reports.
- Per-category and per-career figures rest on few pairs (3 to 19 per career). Treat them as items to discuss, not as conclusions.
