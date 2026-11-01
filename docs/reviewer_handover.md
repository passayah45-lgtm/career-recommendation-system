# Reviewer handover: Career Recommendation System, independent label review

Thank you for agreeing to review. This page explains what the review is for, what you receive, what to do, and how to return your work.

## Purpose

The project has a career recommendation system with 64 careers. Its evaluation uses 111 invented learner profiles. One labeller, an AI assistant working for the project author, judged how relevant careers are to each profile. Before anyone relies on those judgements, a person outside the project should make the same judgements independently. Comparing the two shows how far the labels can be trusted.

Your grades will not change the system or the original labels. They will be compared with them.

## What you will grade

There are 111 profiles × 64 careers = 7,104 possible profile-career pairs. **You will grade 585 selected pairs, not all 7,104.** Each profile shows between 4 and 9 careers.

How the pairs were selected:
- For each profile, the sheet includes every career the first labeller considered for that profile.
- It also includes 2 more careers drawn at random from the remaining careers.
- The careers are then shuffled.

You are not told which careers came from which part. Some will look clearly unrelated; grade them like any other row. Codes such as PR-017 and JOB-K7Q2 are random labels with no meaning.

## What you receive

| File | What it is |
|---|---|
| `reviewer_handover.md` | This page |
| `second_review_guide.md` | The full guide: the 0 to 3 scale, the rules, what to do when information is missing, and worked examples |
| `reviewer_packet.md` | Each profile with its careers: title, job description and usual entry level |
| `reviewer_sheet.csv` | The blank sheet you fill in (585 rows) |

## The work

1. Read the guide, sections 3 to 6, including the section on missing information (about 15 minutes).
2. Copy `reviewer_sheet.csv` to `reviewer_sheet_<your initials>.csv`.
3. For each row, give the career a grade for that profile:
   - **3 Strong:** the learner fits the job's central work now, or after an ordinary step such as finishing their degree.
   - **2 Moderate:** a realistic option that needs more study or experience, but no change of field.
   - **1 Weak:** related or adjacent; it needs major retraining or goes against the learner's goal.
   - **0 Not relevant:** no realistic link.
4. Fill four columns: `relevance_label` (0 to 3), `justification` (one short sentence), `reviewer` (your name or role, the same on every row) and `confidence` (high, medium or low). Do not change the codes or titles.
5. If a profile gives too little information, grade only what it states, use confidence `low`, and start the justification with `INSUFFICIENT:`. Never leave a row blank.

Expected time: about 3 to 4 hours. You can work in several sittings.

## Independence and confidentiality

Your judgement is only useful if it is your own.

- Do not open the project repository, the original labels, the evaluation results or reports, or the app, and do not enter these profiles into the app, until you have submitted.
- Do not discuss individual grades with the project author or with any other reviewer before you submit.
- Do not use an AI assistant or any tool to suggest grades. Public occupational descriptions (O*NET, ESCO, national frameworks) are fine.
- The profiles are invented and contain no personal data. Your completed sheet will be stored with the project under the name you give in the `reviewer` column. Use a role (for example "Lecturer, KIIT") if you prefer not to be named.

## Submission

Return two things to the project author:

1. your completed `reviewer_sheet_<initials>.csv`, with all 585 rows filled;
2. the declaration below, completed. A reply to the author's email containing it is enough.

> **Reviewer declaration**
> I graded every row myself, using the guide. Before submitting, I did not see the original labels, the evaluation results, the project repository or the app's output for these profiles, and I did not use an AI tool to suggest grades.
> Name or role: ____________________ Date: ____________

## What happens next

The project author maps the codes back with a private key that is not in your files. The author then checks that the sheet is complete and runs the agreement analysis, confirming your declaration:

```
python -m src.evaluation.eval64_review_analysis <your sheet> --anonymised --confirm-independent-reviewer
```

Because the 585 pairs are a selected sample, agreement is reported separately for:
- the careers the first labeller considered;
- the randomly drawn careers;
- a weighted estimate for all 7,104 pairs.

It also shows where you disagree, by category and by career, and how the evaluation results change with your labels. Disagreements are expected and useful: they show where the labels are uncertain, not that either labeller is wrong. You will be offered the summary.

Contact: the project author, Issa Toure (KIIT University).
