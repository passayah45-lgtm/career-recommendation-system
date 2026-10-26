# Research problem and gap

## Problem

Students often choose a career path without seeing how their current skills fit it or what they would need to learn. Occupational databases such as O*NET describe more than 900 occupations in depth, but they do not rank careers for an individual or turn a skill gap into a learning step [1], [2]. Career and job recommenders do rank occupations. Yet surveys treat their evaluation as an open challenge [3], [4], and explanation research stresses that explanations must be tested with users rather than assumed to help [5].

The project offers a transparent alternative:

- a weighted score over skills, interests and education;
- a score breakdown for every result;
- required and optional skill gaps linked to free resources.

What it lacks is credible evidence. Its evaluation uses 36 synthetic profiles written by the same person who built the dataset, the engine and the labels.

## Research question

Proposed for the lecturer's review:

> How accurately does a transparent, skill-gap-aware career recommender rank careers that independent reviewers judge suitable for real students, compared with simpler and semantic baselines, and how useful do students find its explanations and gap recommendations?

## Sub-questions and hypotheses

| RQ | Question | Hypothesis | Status |
|---|---|---|---|
| RQ1 | How well does the system rank careers judged relevant by independent reviewers for real student profiles? | H1: higher MAP than skills only | Synthetic only: S 0.971 vs B1 0.946, not significant (Holm p = 0.133). Real-profile test proposed |
| RQ2 | Which components contribute? | H2a: removing interests lowers MAP. H2b: removing education or preferred skills changes MAP by less than 0.02 | Synthetic only: interests 0.030 lower, not significant; education 0.000; preferred 0.002 |
| RQ3 | Does semantic matching help on free-text input? | H3: semantic matching beats exact matching on real profiles | Not started; B4 not implemented |
| RQ4 | How far do synthetic results overstate real-profile results? | H4: synthetic MAP exceeds real-profile MAP | Needs real profiles |
| RQ5 | Do students find explanations and gap advice useful? | H5a: higher perceived transparency with explanations. H5b: gap usefulness above the scale midpoint | Instruments drafted; needs ethics approval |

## Proposed contributions

1. An independently labelled set of anonymised student profiles with graded career relevance and reported agreement. Proposed.
2. A controlled comparison of a transparent recommender with skills-only, interests-only, combined, random, popularity and (planned) semantic baselines, with ablations. Completed on synthetic profiles; real profiles proposed.
3. A measured gap between synthetic and real-profile performance. Proposed.
4. A user study of explanation and skill-gap usefulness. Proposed.
5. An open, reproducible artefact: dataset with O*NET mapping audit, code, evaluation scripts, fixed seeds. Largely completed; licence still missing.

## Research gap

Occupational databases describe jobs but do not personalise. Recommenders personalise, increasingly with embeddings [6], [7], but explanation and gap advice are seldom evaluated with real users.

**The gap is an evaluation gap.** There is little published evidence on whether a fully transparent, skill-gap-aware career recommender for students agrees with independent expert judgement, and whether its explanations and gap advice help students, when tested against simple and semantic baselines on the same catalogue.

This is not a claim of a new algorithm. Every component is known:

- content-based matching [8];
- skill-based occupation similarity [6];
- embedding-based matching [7];
- explanations [9].

A full literature search (see `literature_review.md`) must confirm that no existing study already does this for student career guidance before the gap is stated in a paper.

## References

[1] National Center for O*NET Development, "O*NET 31.0 Database." [Online]. Available: https://www.onetcenter.org/database.html

[2] M. J. Handel, "The O*NET content model: Strengths and limitations," Journal for Labour Market Research, vol. 49, no. 2, pp. 157-176, 2016, doi: 10.1007/s12651-016-0199-8.

[3] Y. Mashayekhi, N. Li, B. Kang, J. Lijffijt, and T. De Bie, "A challenge-based survey of e-recruitment recommendation systems," ACM Computing Surveys, vol. 56, no. 10, pp. 1-33, 2024, doi: 10.1145/3659942.

[4] C. de Ruijt and S. Bhulai, "Job recommender systems: A review," arXiv:2111.13576, 2021. Preprint.

[5] N. Tintarev and J. Masthoff, "Evaluating the effectiveness of explanations for recommender systems," User Modeling and User-Adapted Interaction, vol. 22, no. 4-5, pp. 399-439, 2012, doi: 10.1007/s11257-011-9117-5.

[6] N. Dawson, M.-A. Williams, and M.-A. Rizoiu, "Skill-driven recommendations for job transition pathways," PLOS ONE, vol. 16, no. 8, Art. no. e0254722, 2021, doi: 10.1371/journal.pone.0254722.

[7] J. Rosenberger, L. Wolfrum, S. Weinzierl, M. Kraus, and P. Zschech, "CareerBERT: Matching resumes to ESCO jobs in a shared embedding space for generic job recommendations," Expert Systems with Applications, vol. 275, Art. no. 127043, 2025, doi: 10.1016/j.eswa.2025.127043.

[8] F. Ricci, L. Rokach, and B. Shapira, Eds., Recommender Systems Handbook, 3rd ed. New York, NY, USA: Springer, 2022, doi: 10.1007/978-1-0716-2197-4.

[9] Y. Zhang and X. Chen, "Explainable recommendation: A survey and new perspectives," Foundations and Trends in Information Retrieval, vol. 14, no. 1, 2020, doi: 10.1561/1500000066.
