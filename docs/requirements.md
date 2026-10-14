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

### Career record (careers.csv)

| Field | Type | Example |
|---|---|---|
| career_id | string | C001 |
| title | string | Data Analyst |
| category | string | Data and AI |
| description | string | Analyses data to support business decisions |
| required_skills | list (pipe separated) | python\|sql\|excel\|statistics |
| interests | list (pipe separated) | analysis\|problem solving |
| min_education | integer 0 to 4 | 2 |
| min_experience_years | integer | 0 |
| goals | list (pipe separated) | remote work\|high salary |

Education scale: 0 secondary, 1 diploma, 2 bachelor, 3 master, 4 doctorate.

### Learner profile (runtime input, not stored)

| Field | Type |
|---|---|
| skills | list of strings |
| interests | list of strings |
| education_level | integer 0 to 4 |
| experience_years | integer |
| goals | list of strings |

### Learning resource record (resources.csv)

| Field | Type |
|---|---|
| skill | string |
| resource_title | string |
| provider | string |
| url | string |
| level | beginner, intermediate or advanced |

## 7. Algorithm design

Total score per career:

S = ws * Ss + wi * Si + we * Se + wg * Sg

| Component | Method | Range |
|---|---|---|
| Ss skill match | Matched required skills divided by total required skills | 0 to 1 |
| Si interest match | Jaccard similarity of learner and career interests | 0 to 1 |
| Se education and experience | 1 if both minimums met, partial credit per level below | 0 to 1 |
| Sg goal match | Jaccard similarity of goals | 0 to 1 |

Starting weights: ws = 0.50, wi = 0.25, we = 0.15, wg = 0.10. Weights sum to 1. Phase 5 tests alternative weight sets and documents the results.

Text normalisation: lowercase, trim spaces, map synonyms (for example "ml" to "machine learning") through a synonym dictionary.

Tie-break rule: higher skill match first, then alphabetical title. This keeps rankings deterministic.

The score is a ranking signal. It is not a probability of hiring or career success.

## 8. Evaluation plan

1. Write 20 test learner profiles with expected relevant careers, labelled before running the engine.
2. Compute Precision@5 and Recall@5 against these labels.
3. Compare the weighted model against a baseline that ranks by skill match only.
4. Report real results only. Record limitations, such as small dataset and self-labelled ground truth.

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
