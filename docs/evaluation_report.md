# Evaluation Report

Version: 1.0.0 (Phase 5)
Date: 2026-10-14
Type: synthetic-profile evaluation

All results in this report measure agreement between the engine and reference labels written by the project author for 36 synthetic learner profiles. They are not real-world accuracy, hiring probability or evidence that the recommendations help real learners.

Results file: reports/evaluation_results.json. Reproduce with:

```bash
python -m src.evaluation.experiments --output reports/evaluation_results.json
python -m src.evaluation.experiments --check reports/evaluation_results.json
```

A test (tests/test_evaluation.py) fails if the saved file and a fresh run differ, so every table below is traceable to code.

## 1. Objectives

1. Measure how often the engine ranks independently labelled relevant careers near the top.
2. Test the Phase 3 concern that Financial Analyst ranks third for the worked-example profile with 1 of 3 required skills.
3. Compare the baseline weights with two required-skill-heavy alternatives and a skills-only ablation, without tuning to the data.
4. Find failure cases and their causes.
5. Build a reusable HTTP link checker, run it, and report link status honestly.

## 2. Evaluation dataset

File: data/evaluation/labelled_profiles.json (36 profiles).

### 2.1 Construction

1. Each profile describes a plausible learner (student, career changer, self-taught learner) in one or two sentences.
2. Skills are written the way a learner might type them, including aliases (ML, OOP, SIEM, SEO, TEFL, counselling), mixed case and 3 skills outside the catalogue (pandas, blender, blockchain and solidity).
3. Relevant careers were chosen with written rules L1 to L5 (section 2.3), using what each occupation does, not the overlap count the engine uses.
4. The labels were committed in d93b46b, 47 minutes after the engine code (d29ecaa), and have not changed since. The author states they were written before the engine was run on any profile; git history cannot confirm that part.

### 2.2 Distribution

| Primary category | Profiles |
|---|---|
| Business | 5 |
| Cybersecurity | 4 |
| Data and AI | 5 |
| Design | 4 |
| Education | 5 |
| Engineering | 4 |
| Healthcare | 4 |
| Software | 5 |

| Profile type | Profiles |
|---|---|
| strong match | 21 |
| career transition | 5 |
| mixed skills | 3 |
| missing information | 3 |
| limited skills | 2 |
| overlapping interests | 2 |

56 relevant labels in total, covering 42 distinct careers. 35 profiles have 1 to 3 relevant careers (mean 1.6). One profile (P35) has none on purpose.

### 2.3 Labelling rules

| Rule | Meaning |
|---|---|
| L1 Core work | A career is relevant when the skills cover the central daily work of the occupation |
| L2 Credible next step | For changers and early learners, relevant when current skills are a realistic entry point in the stated direction |
| L3 Generic skills | Communication, Excel or Git alone never make a career relevant |
| L4 Education and interests | Education never removes relevance. Interests support but do not create it |
| L5 Binary | Each career is relevant or not. 0 to 3 per profile. Several relevant careers are listed as an unordered set |

## 3. Metrics

All metrics use the full ranking returned by recommend() with top_k=None, the same service the app uses. K = 5.

| Metric | Definition |
|---|---|
| Precision@5 | Relevant careers in the top 5 / number shown (5, or fewer if fewer careers exist) |
| Attainable precision@5 | Relevant in top 5 / min(5, number relevant). Reaches 1.0 when every relevant career fits in the top 5 |
| Recall@5 | Relevant in top 5 / number relevant |
| F1@5 | 2PR / (P + R) from the two above. 0 when both are 0 |
| Hit@5 | 1 if any relevant career is in the top 5 |
| MRR | Mean of 1 / rank of the first relevant career |
| R-precision | Relevant in the top R / R, where R is the number relevant. Order-sensitive |
| MAP | Mean average precision over the full ranking. Order-sensitive |
| Catalogue coverage | Share of the 50 careers that appear in at least one top-5 list |

Undefined values: when a profile has no relevant careers, every relevance metric is undefined. It is recorded as null and left out of the mean (P35). Means are macro averages over the 35 defined profiles. 95% intervals are percentile bootstrap intervals (2,000 resamples, fixed seed 42).

## 4. Configurations

| Config | Required | Preferred | Interests | Education | Sum |
|---|---|---|---|---|---|
| A baseline (production) | 0.55 | 0.15 | 0.25 | 0.05 | 1.00 |
| B required-heavy | 0.70 | 0.10 | 0.15 | 0.05 | 1.00 |
| C strong required | 0.75 | 0.10 | 0.10 | 0.05 | 1.00 |
| D skills only (ablation) | 0.55 | 0.15 | 0.00 | 0.00 | 0.70 |

All four pass ScoringWeights validation (finite, non-negative, positive sum). The engine divides by the sum of applicable weights, so all give scores from 0 to 100. D sums to 0.70 and is rescaled by the same rule. Every real career has preferred skills, so no other renormalization happens. Education stays at 0.05 in A, B and C.

D is not a candidate for production. It is the "skill match only" comparison promised in the Phase 1 evaluation plan (docs/requirements.md section 8) and shows what interests and education add.

## 5. Results

### 5.1 Aggregate metrics (mean and 95% bootstrap interval, 35 profiles)

| Metric | A baseline | B required-heavy | C strong required | D skills only (ablation) |
|---|---|---|---|---|
| Precision@5 | 0.320 [0.280, 0.366] | 0.320 [0.280, 0.366] | 0.320 [0.280, 0.366] | 0.320 [0.280, 0.366] |
| Attainable precision@5 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] |
| Recall@5 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] |
| F1@5 | 0.469 [0.422, 0.520] | 0.469 [0.422, 0.520] | 0.469 [0.422, 0.520] | 0.469 [0.422, 0.520] |
| Hit@5 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] |
| MRR | 0.986 [0.957, 1.000] | 0.981 [0.943, 1.000] | 0.981 [0.943, 1.000] | 0.967 [0.914, 1.000] |
| R-precision | 0.933 [0.857, 0.991] | 0.929 [0.857, 0.986] | 0.919 [0.843, 0.986] | 0.900 [0.800, 0.971] |
| MAP | 0.971 [0.936, 0.998] | 0.961 [0.915, 0.995] | 0.957 [0.909, 0.991] | 0.946 [0.890, 0.991] |
| Catalogue coverage | 1.00 (50 of 50) | 1.00 (50 of 50) | 1.00 (50 of 50) | 1.00 (50 of 50) |

How to read these numbers:

1. Every labelled career appears in the top 5 for every profile (Recall@5 = 1.0).
2. Precision@5 of 0.320 is the maximum possible. Profiles have 1.6 relevant careers on average, so 5 slots can hold at most 56 hits out of 175. Low precision here does not mean wrong recommendations. It means the labels are sparse. Attainable precision@5 corrects for this and is 1.0.
3. The top-5 metrics are saturated. They cannot separate the configurations. Only the order-sensitive metrics (MRR, R-precision, MAP) move.

### 5.2 Per-profile comparison with the baseline

| Config | MAP better / same / worse | R-precision better / same / worse | MRR better / same / worse |
|---|---|---|---|
| B | 1 / 31 / 3 | 1 / 33 / 1 | 0 / 34 / 1 |
| C | 1 / 30 / 4 | 1 / 32 / 2 | 0 / 34 / 1 |
| D (ablation) | 1 / 30 / 4 | 1 / 32 / 2 | 0 / 33 / 2 |

Profiles whose order changed:

| Profile | Baseline relevant ranks | B | C | Effect |
|---|---|---|---|---|
| P01 statistics student | C001:1, C002:2, C006:3 | same | C006 drops to 5 | Worse under C |
| P03 Excel only | C002:2 | C002:3 | C002:3 | Worse |
| P09 security student | C018:1, C017:2 | C017:3 | C017:3 | Worse |
| P33 CAD hobbyist | C026:1, C047:3 | C047:5 | C047:5 | Worse |
| P34 accountant to data | C029:1, C002:2, C030:4 | C030:3 | C030:3 | Better |
| P36 teacher building course sites | C036:1 | same | same | Under D only, C036 drops to 2 behind Web Developer |

Under D the changes match B and C for P03, P09, P33 and P34, plus the P36 drop. Without interests, HTML and CSS pull a teacher's profile toward Web Developer. D also concentrates recommendations in Data and AI (45 of 180 slots, against 35 for A).

### 5.3 The Financial Analyst concern

Profile P21 has the same skills as the Phase 3 worked example. Its labels are Data Scientist and Data Analyst. Financial Analyst is not labelled because the profile has no accounting or finance skills.

| Config | P21 top 5 | Financial Analyst position |
|---|---|---|
| A | C001, C002, C029, C031, C006 | 3 |
| B | C001, C002, C031, C029, C003 | 4 |
| C | C001, C002, C031, C029, C003 | 4 |
| D (ablation) | C002, C001, C031, C029, C003 | 4 |

Both relevant careers rank 1 and 2 under every configuration, so the metrics for P21 do not change. Required-heavy weights move Financial Analyst down only one place.

The more serious case is P03 (Excel only). Financial Analyst ranks first under all three configurations, above the labelled Data Analyst. Cause: Excel is 1 of 3 required skills for Financial Analyst (coverage 0.33) but 1 of 4 for Data Analyst (0.25). Coverage divides by the length of the required list, so careers with short lists gain more from one shared skill. Raising the required weight makes this worse, which is why B and C push Data Analyst from rank 2 to rank 3 for P03.

### 5.4 Category results (baseline)

| Primary category | Profiles | F1@5 | MRR | MAP |
|---|---|---|---|---|
| Business | 5 | 0.512 | 1.000 | 0.983 |
| Cybersecurity | 4 | 0.512 | 1.000 | 1.000 |
| Data and AI | 5 | 0.595 | 0.900 | 0.900 |
| Design | 4 | 0.393 | 1.000 | 0.938 |
| Education | 5 | 0.428 | 1.000 | 1.000 |
| Engineering | 4 | 0.452 | 1.000 | 0.958 |
| Healthcare | 4 | 0.333 | 1.000 | 1.000 |
| Software | 5 | 0.497 | 1.000 | 1.000 |

F1@5 differences between categories mostly reflect how many careers were labelled per profile, not quality. Data and AI has the lowest MRR and MAP because of P03.

Category share of all 180 recommended slots (36 profiles x 5), per configuration:

| Category | A | B | C | D |
|---|---|---|---|---|
| Business | 28 (15.6%) | 27 (15.0%) | 26 (14.4%) | 26 (14.4%) |
| Cybersecurity | 19 (10.6%) | 18 (10.0%) | 18 (10.0%) | 16 (8.9%) |
| Data and AI | 35 (19.4%) | 36 (20.0%) | 38 (21.1%) | 45 (25.0%) |
| Design | 17 (9.4%) | 19 (10.6%) | 19 (10.6%) | 17 (9.4%) |
| Education | 17 (9.4%) | 17 (9.4%) | 18 (10.0%) | 16 (8.9%) |
| Engineering | 14 (7.8%) | 12 (6.7%) | 12 (6.7%) | 13 (7.2%) |
| Healthcare | 23 (12.8%) | 22 (12.2%) | 21 (11.7%) | 20 (11.1%) |
| Software | 27 (15.0%) | 29 (16.1%) | 28 (15.6%) | 27 (15.0%) |

Data and AI receives the most slots. Its careers share common skills (python, sql, statistics) with Business and Software profiles.

### 5.5 Per-profile results (baseline)

| Profile | Category | Type | Relevant | Baseline top 5 | Relevant ranks | F1@5 | AP |
|---|---|---|---|---|---|---|---|
| P01 | Data and AI | strong match | C001, C002, C006 | C001, C002, C006, C031, C007 | C001:1, C002:2, C006:3 | 0.750 | 1.000 |
| P02 | Data and AI | strong match | C004, C002 | C002, C004, C028, C031, C029 | C002:1, C004:2 | 0.571 | 1.000 |
| P03 | Data and AI | limited skills | C002 | C029, C002, C004, C028, C031 | C002:2 | 0.333 | 0.500 |
| P04 | Data and AI | missing information | C003, C007, C001 | C003, C007, C001, C005, C015 | C001:3, C003:1, C007:2 | 0.750 | 1.000 |
| P05 | Software | strong match | C010 | C010, C012, C009, C015, C013 | C010:1 | 0.333 | 1.000 |
| P06 | Software | strong match | C009, C015 | C015, C009, C013, C010, C008 | C009:2, C015:1 | 0.571 | 1.000 |
| P07 | Software | career transition | C013, C020, C014 | C013, C020, C014, C008, C018 | C013:1, C014:3, C020:2 | 0.750 | 1.000 |
| P08 | Software | strong match | C012 | C012, C010, C009, C015, C024 | C012:1 | 0.333 | 1.000 |
| P09 | Cybersecurity | strong match | C018, C017 | C018, C017, C020, C022, C008 | C017:2, C018:1 | 0.571 | 1.000 |
| P10 | Cybersecurity | strong match | C017, C019 | C017, C019, C018, C022, C021 | C017:1, C019:2 | 0.571 | 1.000 |
| P11 | Cybersecurity | career transition | C020, C021 | C020, C021, C014, C018, C008 | C020:1, C021:2 | 0.571 | 1.000 |
| P12 | Cybersecurity | limited skills | C022 | C022, C017, C018, C019, C001 | C022:1 | 0.333 | 1.000 |
| P13 | Design | strong match | C023 | C023, C027, C025, C026, C010 | C023:1 | 0.333 | 1.000 |
| P14 | Design | career transition | C024 | C024, C026, C010, C012, C023 | C024:1 | 0.333 | 1.000 |
| P15 | Design | strong match | C027 | C027, C026, C036, C043, C003 | C027:1 | 0.333 | 1.000 |
| P16 | Design | mixed skills | C025, C026 | C025, C046, C023, C026, C021 | C025:1, C026:4 | 0.571 | 0.750 |
| P17 | Business | strong match | C030, C029 | C030, C029, C004, C028, C032 | C029:2, C030:1 | 0.571 | 1.000 |
| P18 | Business | strong match | C034 | C034, C033, C002, C004, C016 | C034:1 | 0.333 | 1.000 |
| P19 | Business | strong match | C032, C028 | C032, C028, C030, C033, C011 | C028:2, C032:1 | 0.571 | 1.000 |
| P20 | Business | strong match | C033 | C033, C038, C016, C028, C032 | C033:1 | 0.333 | 1.000 |
| P21 | Data and AI | mixed skills | C001, C002 | C001, C002, C029, C031, C006 | C001:1, C002:2 | 0.571 | 1.000 |
| P22 | Education | strong match | C035, C037 | C035, C037, C038, C033, C036 | C035:1, C037:2 | 0.571 | 1.000 |
| P23 | Education | strong match | C037, C035 | C037, C035, C038, C039, C033 | C035:2, C037:1 | 0.571 | 1.000 |
| P24 | Education | career transition | C036 | C036, C039, C027, C035, C010 | C036:1 | 0.333 | 1.000 |
| P25 | Education | mixed skills | C039 | C039, C007, C015, C006, C001 | C039:1 | 0.333 | 1.000 |
| P26 | Healthcare | strong match | C040 | C040, C045, C041, C044, C042 | C040:1 | 0.333 | 1.000 |
| P27 | Healthcare | strong match | C042 | C042, C044, C049, C041, C002 | C042:1 | 0.333 | 1.000 |
| P28 | Healthcare | strong match | C043 | C043, C041, C030, C004, C040 | C043:1 | 0.333 | 1.000 |
| P29 | Healthcare | strong match | C044 | C044, C045, C040, C041, C042 | C044:1 | 0.333 | 1.000 |
| P30 | Engineering | strong match | C046 | C046, C047, C048, C050, C049 | C046:1 | 0.333 | 1.000 |
| P31 | Engineering | overlapping interests | C048, C050 | C048, C050, C045, C040, C044 | C048:1, C050:2 | 0.571 | 1.000 |
| P32 | Engineering | strong match | C049 | C049, C042, C044, C041, C046 | C049:1 | 0.333 | 1.000 |
| P33 | Engineering | missing information | C047, C026 | C026, C046, C047, C050, C025 | C026:1, C047:3 | 0.571 | 0.833 |
| P34 | Business | career transition | C002, C030, C029 | C029, C002, C031, C030, C004 | C002:2, C029:1, C030:4 | 0.750 | 0.917 |
| P35 | Software | missing information | none | C003, C005, C007, C008, C009 | none | undefined | undefined |
| P36 | Education | overlapping interests | C036 | C036, C010, C024, C035, C039 | C036:1 | 0.333 | 1.000 |

## 6. Failure cases and anomalies

1. List-length bias (P03, P16, P33). One shared skill counts more for careers with 3 required skills than for careers with 4 or 5. P03: Financial Analyst above Data Analyst. P16: Civil Engineer (C046) ranks above the labelled Industrial Designer through shared CAD and project management. P33: the labelled Mechanical Engineer ranks third, behind Civil Engineer, which shares only CAD.
2. Interest-only filler (P15, P35). After the clearly matched careers, the remaining top-5 slots go to careers that match only an interest. P15 (3D artist) receives Medical Records Specialist at rank 4 through the "technology" interest. P35 (only unknown skills) receives five technology careers with very low scores, listed in id order. The scores make the weak fit visible, but a learner may still read the list as advice.
3. Unknown skills are lost. pandas, blender, blockchain and solidity are reported back to the learner but add nothing. For P15, "blender" is the tool the learner uses most.
4. Generic skills and interests spread recommendations. Communication is a required skill in 8 careers and an interest in several more, so profiles that mention it receive HR, counselling or analysis careers in lower slots (P18, P20).

## 7. Decision on the scoring formula

Recommendation: keep the baseline (A). The production formula is unchanged.

Reasons:

1. Neither alternative improves any top-5 metric. On order-sensitive metrics both are slightly worse: MAP 0.961 (B) and 0.957 (C) against 0.971 (A). B is worse on 3 profiles and better on 1. C is worse on 4 and better on 1.
2. The skills-only ablation (D) is the weakest on MAP (0.946), R-precision (0.900) and MRR (0.967). The trend from A to D suggests the interest component helps on these profiles, and that moving weight from interests to required skills costs a little.
3. The differences are small and the bootstrap intervals overlap heavily. With 35 profiles and one labeller, this evidence cannot justify a change in either direction.
4. The required-heavy configurations do not fix the Financial Analyst concern. They move it from rank 3 to rank 4 for P21 and do not change P03, where the real cause is list-length normalization.

Worth testing later instead of new weights:

1. A length-robust skill measure, for example smoothed coverage (matched + a) / (required + b), or a small bonus per matched skill. This targets the cause found in section 6.
2. A minimum required-skill threshold before interest-only careers are shown, or a visible "weak match" label below a score cut-off.

Neither change is made in this phase, because both need fresh, independently labelled profiles to evaluate without overfitting to these 36.

## 8. Resource URL verification

Tool: src/data/url_checker.py, run as python -m src.data.url_checker.

Behaviour:

1. Reads all 114 resource URLs and 46 career source URLs from the CSV files.
2. Sends HEAD first. Retries with GET when HEAD returns 400, 403, 404, 405, 406, 429, 500, 501, 502 or 503, because many servers mishandle HEAD.
3. Follows redirects and records the final URL.
4. Waits Retry-After (at most 30 seconds) once after a 429.
5. Runs one request at a time with at least 1.5 seconds between requests to the same host, and a 15-second timeout.
6. Outcomes: reachable (2xx or 3xx), failed (404 or 410 only), blocked (401, 403, 429, 451, 999), inconclusive (timeouts, TLS and connection errors, 5xx, other codes). A blocked or inconclusive result never counts as missing and never counts as verified.
7. Writes a JSON report with URL, record type and ID, status code, final URL, method, outcome, error and UTC timestamp.
8. With --apply, it changes only reachable resource rows to http_checked with today's date, and appends "Earlier status: search_index_confirmed on 2026-10-14." to notes. Other rows stay unchanged.

Tests: 22 tests with a mocked transport (tests/test_url_checker.py). The CI workflow never runs the checker.

### 8.1 Real HTTP check results (2026-10-14)

The checker was run by the project author on a Windows laptop (Python 3.12.7) on a home network in India. Three runs were made the same day:

| Run | Time (UTC) | Reachable | Blocked | Inconclusive | Failed | Report file |
|---|---|---|---|---|---|---|
| 0 | afternoon | 149 | 9 | 1 | 1 | not kept (overwritten by run 1). Numbers copied from the console |
| 1 | 17:02 | 118 | 9 | 33 | 0 | reports/url_check.json |
| 2 | 17:18 | 150 | 9 | 1 | 0 | reports/url_check_run2.json |

Run 2 is the reference result. The 33 inconclusive results in run 1 were all timeouts ("timed out" or "read operation timed out") caused by a weak connection at that time. The same sites answered in run 2.

Run 2 in detail (160 URLs):

| Group | Count | Outcome |
|---|---|---|
| Career source URLs (O*NET) | 46 | all reachable |
| Resource URLs | 104 | reachable, now marked http_checked |
| Resource URLs | 9 | blocked with HTTP 403 |
| Resource URLs | 1 | inconclusive (timeout) |

Blocked resources (HTTP 403 to the checker):

| Site | Resources |
|---|---|
| open.edu (The Open University) | R008, R013, R022, R031, R033, R038 |
| open.lib.umn.edu (University of Minnesota) | R020, R048 |
| pressbooks.pub | R041 |

These sites use bot protection. A 403 means the checker was refused, not that the page is missing. They keep the status search_index_confirmed. Checking them by hand in a browser is still recommended before the demonstration.

Inconclusive: R050 Inkscape tutorials. The checker timed out, and opening the page in Chrome at the same time showed "502 Bad Gateway" from the Inkscape server. This is a server-side fault, so the link keeps search_index_confirmed and should be checked again before submission.

Failed and replaced: in run 0, R045 (GCFGlobal "Beginning Graphic Design: Layout and Composition") returned HTTP 404 on both HEAD and GET. The page no longer appeared in search results either. It was replaced with Canva Design School "Graphic design basics" (commit 4f4ab0b). The author opened the new page in Chrome and confirmed the course loads. It was reachable in runs 1 and 2.

Redirects worth noting (run 2): the GOV.UK content design guide (R021) now redirects to guidance.publishing.service.gov.uk, and the GCFGlobal Excel course (R040) redirects to learnfree.org. Both load the intended content, so the stored URLs were kept.

### 8.2 Effect on the dataset

| url_verification | Resources |
|---|---|
| http_checked (2026-10-14) | 104 |
| search_index_confirmed (2026-10-14) | 10 (9 blocked, 1 inconclusive) |
| unverified | 0 |

Every http_checked row keeps its earlier status in notes ("Earlier status: search_index_confirmed on 2026-10-14."). No row was marked verified without a successful HTTP response.

### 8.3 How to repeat the check

```powershell
cd career-recommendation-system
.venv\Scripts\activate
python -m src.data.url_checker --output reports\url_check.json --apply
python -m src.data.validation
python -m pytest -q
```

Run each command separately. --apply is safe to repeat: it only promotes reachable rows and never downgrades a row. Use a stable connection, because timeouts are reported as inconclusive. Commit the report and resources.csv afterwards.

## 9. Learner experience review

Automated (Streamlit AppTest, tests/test_app.py):

| Check | Status |
|---|---|
| Assessment saves normalized input, reports unknown and duplicate skills | Automated, passing |
| Assessment rejects empty answers | Automated, passing |
| Recommendations need a profile, show service scores and the disclaimer | Automated, passing |
| Unknown-skill warning, invalid saved profile message | Automated, passing |
| Top K slider | Automated, passing |
| Recommendation button opens the skill gap for that career | Automated, passing |
| Explorer to Skill-Gap for a career outside the recommendations keeps that career and selects "All careers" | Automated, passing (new in Phase 5) |
| Skill gap from a recommended career stays on "My recommended careers" | Automated, passing (new in Phase 5) |
| Skill-gap coverage, resource table and verification label | Automated, passing |
| Explorer category filter and title search | Automated, passing |
| Analytics with and without a profile | Automated, passing |
| Reset clears the assessment | Automated, passing |
| Missing data folder shows an error instead of crashing | Automated, passing |

The Explorer to Skill-Gap behaviour was handled in Phase 4. This phase adds the tests that prove it. No new defects were found in this review.

Not verified, manual browser checks still required (I have not opened the app in a browser):

1. Layout and readability at laptop and phone widths.
2. Chart legibility and colours.
3. Resource links open in a new tab.
4. Sidebar navigation labels and page order.
5. The full flow by a person who has not seen the app before.

## 10. Limitations, bias and generalization

1. Single author. The same person built the dataset, wrote the engine and wrote the labels. Labels were written before running the engine, but they still share the author's view of each career, which inflates agreement.
2. Shared vocabulary. Profiles mostly use the catalogue's own skill names, so exact matching works far better here than it would on free text from real learners.
3. Easy profiles. 21 of 36 profiles are strong matches. The top-5 metrics are saturated (Recall@5 = 1.0) and cannot separate configurations.
4. Small sample. 35 profiles with defined metrics give wide intervals. A difference of 0.01 in MAP is not meaningful.
5. Binary labels. Partly relevant careers are treated as irrelevant, which lowers precision and hides graded quality.
6. Regional bias. Careers come from O*NET (United States) and several resources are US or UK specific. Results may not carry over to learners in India or Guinea.
7. No outcome data. Nothing here says whether a learner who follows a recommendation will be hired, succeed or be satisfied.

## 11. Future evaluation work

1. Ask 2 or 3 independent labellers (for example lecturers or career advisers) to label the same profiles, and report inter-rater agreement (Cohen's kappa).
2. Collect free-text profiles from consenting classmates, anonymized, to test normalization on real input.
3. Add graded relevance (0, 1, 2) and report nDCG@5.
4. Add harder profiles: more transitions and more profiles with limited or ambiguous skills.
5. Hold out profiles: design formula changes on one set and report results only on a separate set.
6. Run the URL checker before each release and track link failures over time. Recheck R050 (Inkscape) and the 9 blocked links by hand before submission.
