# Literature review

Supporting document for the research plan. Every reference below was opened, and its authors, venue, year and DOI were checked on 26 October 2026. IEEE style. This is a starting set, not a systematic review; the plan describes the full search protocol.

Research question: How accurately does a transparent, skill-gap-aware career recommender rank careers that independent reviewers judge suitable for real students, compared with simpler and semantic baselines, and how useful do students find its explanations and gap recommendations?

## 1. Occupational knowledge bases

| Ref | Main point | Relation to the RQ |
|---|---|---|
| [1], [2] | O*NET 31.0 covers 1,016 O*NET-SOC titles (923 data-level) described through a Content Model of worker and job descriptors, licensed CC BY 4.0 and updated quarterly. | Reference taxonomy for the 46 linked careers; source for checking skill lists and education levels. |
| [3] | Peterson et al. describe the design and research uses of O*NET. | Background for describing O*NET in the paper. |
| [4] | Handel reviews O*NET's strengths and limitations, including gaps, duplication and vague item wording. | Supports the limitations section and the caution against treating O*NET ratings as exact. |
| [5], [6], [7] | ESCO is the European multilingual taxonomy (v1.2 in May 2024, v1.2.1 in December 2025) with an official crosswalk to O*NET. | Second taxonomy for cross-dataset validation of skill lists. |

## 2. Job and career recommender systems

| Ref | Main point | Relation to the RQ |
|---|---|---|
| [8] | Challenge-based survey of e-recruitment recommenders, organised by open problems including evaluation. | Frames evaluation as an open problem; positions the project as content-based. |
| [9] | Review of job recommender systems and their methods (preprint). | Background on method families. |
| [10] | Skill-based occupation similarity from job ads, used to recommend job transitions. | Closest skills-based approach; shows a data-driven alternative to hand-curated skill lists. |
| [11] | CareerBERT embeds resumes and ESCO jobs in one space for job recommendation. | Basis for a semantic baseline; shows the field moving to embeddings. |
| [12] | Implicit skill extraction from text with document embeddings for job recommendation. | Supports handling free-text learner input. |

## 3. Skill identification and semantic matching

| Ref | Main point | Relation to the RQ |
|---|---|---|
| [13] | Survey of methods for identifying skills in online job ads. | Methods for building or checking skill lists. |
| [14] | Sentence-BERT produces sentence embeddings suited to semantic similarity. | Concrete method for baseline B4 (semantic skill matching). |

## 4. Explainable recommendation

| Ref | Main point | Relation to the RQ |
|---|---|---|
| [15] | Survey of explainable recommendation methods and evaluation. | Vocabulary for describing the system's component-level explanations. |
| [16] | Explanations serve aims such as transparency, trust and effectiveness, and must be evaluated with users. | Defines what the user study measures. |
| [17] | ResQue: a user-centric questionnaire framework for recommender systems. | Source for questionnaire items. |

## 5. Evaluation methodology

| Ref | Main point | Relation to the RQ |
|---|---|---|
| [18] | Recommender Systems Handbook: standard offline and online evaluation practice. | General methodology. |
| [19] | NDCG: graded-gain evaluation of rankings. | Co-primary metric once graded labels exist. |
| [20] | Comparison of significance tests for IR evaluation (t-test, Wilcoxon, randomisation, bootstrap, sign test). | Justifies the paired tests chosen. |
| [21] | Cohen's kappa for agreement between two raters. | Inter-rater agreement for independent labels. |
| [22] | User simulation as a way to evaluate recommenders, alongside real users. | Positions synthetic profiles as a complement, not a substitute, for real users. |

## Gap supported by this review

Occupational databases describe jobs but do not rank careers for learners [1], [4]. Recommenders rank occupations, increasingly with embeddings [10], [11], while surveys treat evaluation as an open challenge [8] and explanation research requires user testing [16]. The project's contribution should therefore be framed as a transparent, reproducible evaluation with independent labels and a user study, not as a new algorithm. Before submission, a full search must confirm that no study already reports this for student career guidance.

## Search still to do

- Databases: ACM Digital Library, IEEE Xplore, Scopus, Google Scholar.
- Terms: career recommender, job recommender, skill gap, course recommendation for skills, explainable recommendation, occupational taxonomy, user simulation, India.
- Include peer-reviewed work from 2010 onward plus foundational papers; log queries and screening decisions.
- Candidate found but not yet verified (authors and DOI not confirmed): "Recommender System in Academic Choices of Higher Education: A Systematic Review," IEEE Access, 2024 (IEEE Xplore document 10444757). Verify before citing.

## References

[1] National Center for O*NET Development, "O*NET 31.0 Database." [Online]. Available: https://www.onetcenter.org/database.html

[2] National Center for O*NET Development, "The O*NET Content Model." [Online]. Available: https://www.onetcenter.org/content.html

[3] N. G. Peterson, M. D. Mumford, W. C. Borman, P. R. Jeanneret et al., "Understanding work using the Occupational Information Network (O*NET): Implications for practice and research," Personnel Psychology, vol. 54, no. 2, pp. 451-492, 2001, doi: 10.1111/j.1744-6570.2001.tb00100.x.

[4] M. J. Handel, "The O*NET content model: Strengths and limitations," Journal for Labour Market Research, vol. 49, no. 2, pp. 157-176, 2016, doi: 10.1007/s12651-016-0199-8.

[5] European Commission, "ESCO v1.2." [Online]. Available: https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/esco-v12

[6] European Commission, "The crosswalk between ESCO and O*NET (Technical Report)," Sep. 2022. [Online]. Available: https://esco.ec.europa.eu/en/about-esco/publications/publication/crosswalk-between-esco-and-onet-technical-report

[7] M. le Vrang, A. Papantoniou, E. Pauwels, P. Fannes, D. Vandensteen, and J. De Smedt, "ESCO: Boosting job matching in Europe with semantic interoperability," Computer, vol. 47, no. 10, pp. 57-64, 2014, doi: 10.1109/MC.2014.283.

[8] Y. Mashayekhi, N. Li, B. Kang, J. Lijffijt, and T. De Bie, "A challenge-based survey of e-recruitment recommendation systems," ACM Computing Surveys, vol. 56, no. 10, pp. 1-33, 2024, doi: 10.1145/3659942.

[9] C. de Ruijt and S. Bhulai, "Job recommender systems: A review," arXiv:2111.13576, 2021. Preprint.

[10] N. Dawson, M.-A. Williams, and M.-A. Rizoiu, "Skill-driven recommendations for job transition pathways," PLOS ONE, vol. 16, no. 8, Art. no. e0254722, 2021, doi: 10.1371/journal.pone.0254722.

[11] J. Rosenberger, L. Wolfrum, S. Weinzierl, M. Kraus, and P. Zschech, "CareerBERT: Matching resumes to ESCO jobs in a shared embedding space for generic job recommendations," Expert Systems with Applications, vol. 275, Art. no. 127043, 2025, doi: 10.1016/j.eswa.2025.127043.

[12] A. Gugnani and H. Misra, "Implicit skills extraction using document embedding and its use in job recommendation," in Proc. AAAI Conf. Artificial Intelligence, vol. 34, no. 08, pp. 13286-13293, 2020, doi: 10.1609/aaai.v34i08.7038.

[13] I. Khaouja, I. Kassou, and M. Ghogho, "A survey on skill identification from online job ads," IEEE Access, vol. 9, pp. 118134-118153, 2021, doi: 10.1109/ACCESS.2021.3106120.

[14] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using Siamese BERT-networks," in Proc. EMNLP-IJCNLP, 2019, pp. 3980-3990, doi: 10.18653/v1/D19-1410.

[15] Y. Zhang and X. Chen, "Explainable recommendation: A survey and new perspectives," Foundations and Trends in Information Retrieval, vol. 14, no. 1, 2020, doi: 10.1561/1500000066.

[16] N. Tintarev and J. Masthoff, "Evaluating the effectiveness of explanations for recommender systems," User Modeling and User-Adapted Interaction, vol. 22, no. 4-5, pp. 399-439, 2012, doi: 10.1007/s11257-011-9117-5.

[17] P. Pu, L. Chen, and R. Hu, "A user-centric evaluation framework for recommender systems," in Proc. 5th ACM Conf. Recommender Systems, 2011, pp. 157-164, doi: 10.1145/2043932.2043962.

[18] F. Ricci, L. Rokach, and B. Shapira, Eds., Recommender Systems Handbook, 3rd ed. New York, NY, USA: Springer, 2022, doi: 10.1007/978-1-0716-2197-4.

[19] K. Jarvelin and J. Kekalainen, "Cumulated gain-based evaluation of IR techniques," ACM Transactions on Information Systems, vol. 20, no. 4, pp. 422-446, 2002, doi: 10.1145/582415.582418.

[20] M. D. Smucker, J. Allan, and B. Carterette, "A comparison of statistical significance tests for information retrieval evaluation," in Proc. 16th ACM Conf. Information and Knowledge Management, 2007, pp. 623-632, doi: 10.1145/1321440.1321528.

[21] J. Cohen, "A coefficient of agreement for nominal scales," Educational and Psychological Measurement, vol. 20, no. 1, pp. 37-46, 1960, doi: 10.1177/001316446002000104.

[22] S. Zhang and K. Balog, "Evaluating conversational recommender systems via user simulation," in Proc. 26th ACM SIGKDD Conf. Knowledge Discovery and Data Mining, 2020, doi: 10.1145/3394486.3403202.
