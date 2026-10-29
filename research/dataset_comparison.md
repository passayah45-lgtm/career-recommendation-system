# Dataset comparison: the project vs O*NET

Checked on 26 October 2026 against the repository and official O*NET pages. A longer, editable version was shared with the supervisor separately. This file reflects one correction made afterwards: DevOps Engineer is now mapped to O*NET 15-1252.00.

Convention: **Verified** means checked directly in the repository or on an official page. **Analysis** means the author's interpretation.

## 1. Summary

O*NET is a national occupational database. The project is a personalised recommender built on a small curated catalogue that links to O*NET for 47 of its 50 careers. O*NET describes occupations in depth; the project turns a much thinner description into a ranked, explained answer for one learner. Neither replaces the other, and the smaller dataset is not claimed to be better.

## 2. O*NET in brief (Verified)

| Attribute | Official description |
|---|---|
| Current release | O*NET 31.0; site updated 6 October 2026; 208 occupations updated in this release [1] |
| Occupations | 1,016 O*NET-SOC titles [1], of which 923 are data-level occupations [5] |
| Content Model | Worker characteristics (abilities, interests, work styles), worker requirements (skills, knowledge, education), experience requirements, occupational requirements (work activities, context), occupation-specific information (tasks, titles), workforce characteristics [2] |
| Collection | Job incumbents, occupation experts, analyst ratings, employer job postings, machine learning and other sources [3] |
| Establishment survey | Two-stage sample of U.S. establishments, then workers; target of at least 20 respondents per domain questionnaire [4] |
| Skill and ability ratings | Produced by trained occupational analysts; 35 skill constructs [8] |
| Updates | Quarterly, main update in the third quarter [1] |
| Licence | CC BY 4.0, with stated exceptions [1] |

Each occupation has its own provenance record. For Data Scientists (15-2051.00), for example, tasks come from occupation experts (2026), abilities from analysts (2026) and software skills from job postings (2026) [6].

## 3. The project dataset (Verified)

| Item | Value |
|---|---|
| Careers | 50 in 8 categories |
| Skills | 102 unique required, 48 preferred, 114 unique in total; 3 to 5 required per career |
| Aliases | 37 |
| Interests | 20-term controlled vocabulary |
| Education | Levels 0 to 4; 42 careers at level 3, 7 at level 4, 1 at level 2 |
| Learning goals | 3 per career |
| Resources | 114, one free resource per skill; 104 HTTP-checked on 14 October 2026 |
| O*NET link | Code and URL for 47 careers; none for 3 |
| Evaluation profiles | 36 synthetic, author-written and author-labelled |

## 4. Provenance and mapping

The project uses O*NET to identify occupations, not as a data source. No O*NET data file is downloaded or stored. Only a code and a URL are recorded per career.

| Field | Origin |
|---|---|
| title, onet_code, source_url | Sourced: matched to an O*NET occupation, and the URL agrees with the code (enforced by the validator) |
| description, skills, interests, education, learning goals | Curated by the author; no O*NET identifier appears in these fields |

Mapping types (Analysis; per career in `research/data/onet_mapping_audit.csv`):

| Type | Count | Careers |
|---|---|---|
| Same or close occupation | 40 | for example Data Scientist to 15-2051.00 |
| Nearest broader occupation | 7 | Data Engineer, AI Research Scientist, DevOps Engineer, Cloud Engineer, UX Designer, Digital Marketing Specialist, Instructional Designer |
| No O*NET occupation | 3 | Data Analyst, Machine Learning Engineer, Mobile App Developer |

The DevOps correction is Verified: O*NET OnLine lists "DevOps Engineer" as a reported job title of 15-1252.00 Software Developers [7]. The three unmatched careers still need checking (Section 8).

A valid link shows that a career corresponds to an O*NET occupation. It does not show that the record's skills, interests or education came from O*NET.

## 5. Comparison table

| Dimension | O*NET 31.0 | Career Recommendation System |
|---|---|---|
| Artefact type | Occupational database and taxonomy | Curated dataset, scoring algorithm and deployed app |
| Purpose | Describe the U.S. world of work [1], [9] | Rank careers for one learner and show which skills to learn next |
| Users | Researchers, counsellors, employers, developers, job seekers | Students and early-career learners |
| Occupations | 1,016 titles, 923 data-level | 50 careers |
| Skills | 35 rated constructs plus software skills from job postings | 114 short names; required vs preferred |
| Skill representation | Importance and level ratings | Binary membership |
| Interests | Career interest types and specific interest areas [2], [5] | 20 terms, binary |
| Education | Education and training data, Job Zones [2] | One integer per career, author-assigned |
| Geography | United States | U.S. occupations via O*NET; users in India and Guinea |
| Collection | Surveys, experts, analysts, postings [3], [4] | Single author, general knowledge, web search |
| Updates | Quarterly | Manual; dataset v1.2.0 |
| Personalisation | None in the database | Learner profile of skills, interests and education |
| Ranking | Not provided | Weighted 0 to 100 score with deterministic ties |
| Explanations | Not applicable | Component breakdown; matched and missing items |
| Skill gaps | Not computed | Required and optional gaps per career |
| Learning resources | Not linked to skills | One free resource per skill |
| Ground truth | None for recommendation quality | 36 synthetic profiles (preliminary) |
| Licence | CC BY 4.0 | No licence file yet |

## 6. Limitations of O*NET for this purpose

Limitations of the dataset itself:

1. U.S.-only sampling frame [4]; occupations, education routes and wages may differ in India and Guinea.
2. Coarse coverage of new roles: no dedicated occupation was found for Data Analyst, ML Engineer or Mobile App Developer.
3. Generic skill constructs [8]. They are too general to point to a course, and software skills list tools, not methods.
4. Mixed provenance and data vintages across domains and occupations [5], [6].
5. Measurement concerns in the Content Model: gaps, duplication, vague wording [10].

Limitations of using O*NET as the basis of a personalised recommender:

1. No learner model, no ranking function and no ground truth for fit.
2. Gaps need a threshold on importance or level ratings, which O*NET does not define.
3. No link from skills to learning resources.
4. Learners type tools ("python", "ML"), while O*NET skills are constructs.

The project fills the second group by hand. It does not fix the first group, and its own skill lists are less evidence-based than O*NET's ratings.

## 7. Strengths and limitations of the project's approach

| Strengths | Limitations |
|---|---|
| Every score splits into four named components | One author curated skills, interests and education without field-level sources |
| Deterministic, tested (275 tests), reproducible evaluation | 50 careers out of 923 O*NET data-level occupations |
| Required and optional gaps, each with a free resource | Binary skill lists ignore importance and level |
| Labels fixed in commit d93b46b and never changed; the author states they were written before running the engine | Same author for careers, engine and labels; 91% of profile skills are exact catalogue names |
| Links carry verification status | Education not checked against Job Zones; no licence file |

## 8. Missing information

- Data Analyst, ML Engineer, Mobile App Developer: confirm in O*NET OnLine whether a reported title exists, and record the nearest parent.
- Skill lists: record which O*NET tasks, skills or technology items informed each list, or state that none did.
- Education levels: compare each with its O*NET Job Zone.
- Record the O*NET release used for the links (31.0 is current).
- O*NET occupation titles in the audit file were written from the O*NET-SOC 2019 taxonomy as known to the author. They were not checked programmatically, because O*NET downloads were blocked in the workspace.

## 9. Secondary dataset: ESCO

ESCO (European Commission) is published in 28 languages [11] and has an official crosswalk to O*NET [12]. It could serve to cross-check skill lists and to test ranking stability. It is European-centred, so it does not remove the regional bias.

## 10. Research gap

See `research_problem_and_gap.md`. In short, it is an evaluation gap, not an algorithmic one.

## References

[1] National Center for O*NET Development, "O*NET 31.0 Database." https://www.onetcenter.org/database.html

[2] National Center for O*NET Development, "The O*NET Content Model." https://www.onetcenter.org/content.html

[3] National Center for O*NET Development, "O*NET Data Collection Overview." https://www.onetcenter.org/dataCollection.html

[4] National Center for O*NET Development, "O*NET Data Collection Program, Supporting Statement Part B," 2024. https://www.onetcenter.org/dl_files/omb2024/Supporting_StatementB.pdf

[5] National Center for O*NET Development, "Appendix 4. O*NET Database Release Notes," 30.3 Data Dictionary. https://www.onetcenter.org/dictionary/30.3/text/appendix_updates.html

[6] National Center for O*NET Development, "Data updates: 15-2051.00 Data Scientists." https://www.onetcenter.org/dataUpdates/occupations/15-2051.00

[7] O*NET OnLine, "15-1252.00 Software Developers." https://www.onetonline.org/link/custom/15-1252.00

[8] S. Tsacoumis and S. Willison, "O*NET Analyst Occupational Skills Ratings: Procedures," HumRRO, Mar. 2010. https://www.onetcenter.org/reports/AOSkills_Proc.html

[9] N. G. Peterson, M. D. Mumford, W. C. Borman, P. R. Jeanneret et al., "Understanding work using the Occupational Information Network (O*NET)," Personnel Psychology, vol. 54, no. 2, pp. 451-492, 2001, doi: 10.1111/j.1744-6570.2001.tb00100.x.

[10] M. J. Handel, "The O*NET content model: Strengths and limitations," Journal for Labour Market Research, vol. 49, no. 2, pp. 157-176, 2016, doi: 10.1007/s12651-016-0199-8.

[11] European Commission, "ESCO v1.2.1." https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/esco-v121

[12] European Commission, "The crosswalk between ESCO and O*NET (Technical Report)," Sep. 2022. https://esco.ec.europa.eu/en/about-esco/publications/publication/crosswalk-between-esco-and-onet-technical-report

All URLs opened on 26 October 2026.
