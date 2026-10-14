# Requirements Specification

Project: Career Recommendation System
Author: Issa Toure
Course: MSc Computer Science and Data Analysis, KIIT University
Submission deadline: 30 October 2026

## 1. Problem statement

Students and early-career learners pick careers with little structured guidance. They do not know which careers fit their current skills, or which skills they lack for a target career. This system takes a learner profile, ranks careers by fit, explains each match, and lists the missing skills with learning resources.

## 2. Objectives

1. Build a content-based recommender that ranks careers against a learner profile.
2. Explain every recommendation in plain language.
3. Show the skill gap between the learner and each recommended career.
4. Evaluate recommendation quality with documented test profiles and Precision@K.
5. Keep the engine independent from the user interface so T-Career can reuse it.

## 3. Users

| User | Need |
|---|---|
| Student | Find careers that fit current skills and interests |
| Career switcher | See which skills to learn for a new field |
| Lecturer (assessor) | Run the demo and inspect method and results |
| T-Career (future) | Call the engine through an API |

## 4. Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| FR1 | The user enters skills, interests, education level, experience years and career goal | Must |
| FR2 | The system validates inputs and rejects empty or invalid profiles with a clear message | Must |
| FR3 | The system computes a score from 0 to 100 for every career | Must |
| FR4 | The system shows the top K careers (default 5) in ranked order | Must |
| FR5 | Each result shows matched skills, missing skills and a short explanation | Must |
| FR6 | The skill-gap page lists missing skills with at least one learning resource each | Must |
| FR7 | The career explorer lets the user browse and filter all careers | Should |
| FR8 | The analytics page shows the score breakdown per component in a chart | Should |
| FR9 | The user downloads results as CSV | Could |

## 5. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR1 | Recommendations return in under 2 seconds for a dataset of up to 500 careers |
| NFR2 | The same profile always returns the same ranking (deterministic) |
| NFR3 | The engine runs without Streamlit installed (UI separation) |
| NFR4 | No personal learner data is stored in the repository |
| NFR5 | Automated tests cover validation, scoring, ranking and skill gap |
| NFR6 | The app runs on Streamlit Community Cloud free tier |

## 6. Data model

Phase 2 replaced the draft schema below with the implemented one. The full field definitions live in docs/dataset_documentation.md. This section keeps a summary.

### Career record (careers.csv)

| Field | Type | Example |
|---|---|---|
| career_id | string | C002 |
| career_title | string | Data Analyst |
| category | string | Data and AI |
| description | string | Collects, cleans and analyses data |
| required_skills | list (pipe separated) | sql\|excel\|data visualization\|statistics |
| preferred_skills | list (pipe separated, optional) | python\|power bi\|communication |
| education_level | integer 0 to 4 | 3 |
| interests | list (pipe separated, controlled vocabulary) | analysis\|business\|problem solving |
| learning_goals | list (pipe separated) | write analytical sql queries\|build dashboards |
| onet_code | string (optional) | 15-2051.00 |
| source_url | string (optional) | O*NET OnLine summary page |

Education scale (Phase 2): 0 no formal qualification specified, 1 secondary, 2 certificate or diploma, 3 bachelor's or equivalent, 4 master's or higher. Levels are simplified typical-entry categories, not hard requirements.

Changes from the Phase 1 draft: title became career_title, goals became learning_goals, preferred_skills, onet_code and source_url were added, and min_experience_years was removed because no reliable per-career source was available.

### Learner profile (runtime input, not stored)

| Field | Type |
|---|---|
| skills | list of strings (normalized with data/raw/skill_aliases.csv) |
| interests | list of strings from the controlled vocabulary |
| education_level | integer 0 to 4 |
| experience_years | integer (shown to the user, not scored in version 1) |
| goals | list of strings |

### Learning resource record (resources.csv)

| Field | Type |
|---|---|
| resource_id | string |
| skill_name | string |
| resource_title | string |
| provider | string |
| resource_url | string |
| is_free | boolean |
| resource_type | book, course, documentation, guide, standard, tutorial |
| level | beginner, intermediate or advanced |
| language | ISO 639-1 code |
| url_verification | search_index_confirmed, http_checked or unverified |

## 7. Algorithm design

Implemented in Phase 3. The full specification is docs/recommendation_algorithm.md. Summary:

S = 100 * (w_req * S_req + w_pref * S_pref + w_int * S_int + w_edu * S_edu) / (sum of applicable weights)

| Component | Method | Range |
|---|---|---|
| S_req required skills | Matched required skills divided by total required skills | 0 to 1 |
| S_pref preferred skills | Matched preferred skills divided by total preferred skills | 0 to 1 |
| S_int interests | Matched career interests divided by total career interests | 0 to 1 |
| S_edu education | 1 when the learner meets the career level, minus 0.25 per level below | 0 to 1 |

Weights: w_req = 0.55, w_pref = 0.15, w_int = 0.25, w_edu = 0.05. Phase 5 compared two required-heavy alternatives and kept these weights (docs/evaluation_report.md).

Changes from the Phase 1 draft: preferred skills became a separate component, interest matching uses coverage of the career's interests instead of Jaccard, education weight dropped from 0.15 to 0.05 because 42 of 50 careers share level 3, and the goal component was removed because learning goals are free text with no reliable way to compare them.

Text normalisation: the Phase 2 normalize_skill function with data/raw/skill_aliases.csv.

Tie-break rule: total score, then required-skill coverage, then matched required count, then career_id. This keeps rankings deterministic.

The score is a ranking signal. It is not a probability of hiring or career success.

## 8. Evaluation plan

1. Write 20 test learner profiles with expected relevant careers, labelled before running the engine. Done in Phase 5 with 36 profiles (data/evaluation/labelled_profiles.json).
2. Compute Precision@5 and Recall@5 against these labels. Done, plus F1@5, MRR, R-precision and MAP.
3. Compare the weighted model against a baseline that ranks by skill match only. Done as ablation D.
4. Report real results only. Record limitations, such as small dataset and self-labelled ground truth. See docs/evaluation_report.md.

## 9. Acceptance criteria

| ID | Criterion |
|---|---|
| AC1 | A valid profile returns 5 ranked careers with scores and explanations |
| AC2 | An empty skills list returns a validation message, not a crash |
| AC3 | A profile matching all skills of a career ranks that career in the top 3 |
| AC4 | Every missing skill shown has a linked learning resource or a "no resource yet" label |
| AC5 | All pytest tests pass in GitHub Actions |
| AC6 | The app loads from a public link on submission day |

## 10. Out of scope for the assignment

User accounts, persistent databases, collaborative filtering, and the T-Career API. These move to Phase 7.
