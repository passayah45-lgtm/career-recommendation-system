# Interest taxonomy 2.0: implementation (dataset v1.4.0)

Implemented 3 November 2026 from commit b861aed on `main`.

## 1. Approval status

| Item | Status |
|---|---|
| Decision basis | **Owner-authorized implementation pending lecturer feedback.** The project owner authorized implementation on 3 November 2026 using the recommendations in `docs/skills_interests_audit.md`, `docs/interest_taxonomy_second_review.md` and `docs/lecturer_review/` |
| Lecturer feedback | **Not yet received.** The decision checklist in `docs/lecturer_review/lecturer_decision_checklist.md` is still blank. No lecturer comment, approval or signature exists, and none is implied here |
| Academic validation | None. The taxonomy is a research proposal implemented for evaluation, not an academically validated instrument |
| If the lecturer asks for changes | The vocabulary, descriptions and assignments live in two places (`src/data/interest_taxonomy.py` and the `interests` column of `data/raw/careers.csv`). A change means a new dataset version and a new evaluation. The frozen v1.4.0 snapshot stays as it is |

How the seven decisions were settled for this implementation (owner's instruction, second review's recommendation):

| # | Decision | Implemented |
|---|---|---|
| 1 | 23 interest terms | All 23 terms of the second review, wording unchanged. The second review has 12 retained terms, not 11 |
| 2 | Career-interest assignments | All 64 assignments of section C, exactly three per career |
| 3 | 12 provisional careers | Implemented as proposed and still flagged provisional in the documentation: C002, C003, C012, C053, C054, C055, C057, C058, C059, C061, C062, C064 |
| 4 | RIASEC grouping | Display only, as in section D. Not used in scoring |
| 5 | Descriptions and French | English descriptions from the second review. French names are **draft translations** written for this implementation (neither audit has French wording). They are accepted as input but not shown in the interface until reviewed |
| 6 | Selection limit | Soft warning above 5 interests, no hard cap (second review's recommendation) |
| 7 | O*NET validation | List-page evidence used as it stands, with its limits stated. No spot-check against the O*NET database files yet |

## 2. What changed

### Data

- `data/raw/careers.csv`: only the `interests` column changed, for all 64 careers. IDs, titles, categories, descriptions, skills, education levels, learning goals, O*NET codes and source URLs are byte-for-byte the same (checked by tests).
- `data/raw/dataset_manifest.json`: `dataset_version` 1.4.0 and a new field `"interest_taxonomy": "2.0"`.
- New frozen snapshot `data/evaluation/catalog_v1.4.0/` with SHA-256 values in its `evaluation_manifest.json`.

### Vocabulary and stored form

- The 23 terms, their explanations, examples, related skills and RIASEC groups are in `src/data/interest_taxonomy.py`, copied from the second review.
- **Stored form.** The catalogue only accepts lowercase words separated by single spaces, so each interest is stored as its name lowercased with punctuation removed (for example "Caring for people's health" is stored as `caring for peoples health`). Learners and API callers always see the exact name and can send either form.
- `src/data/validation.py`: `INTERESTS` is now the 23-term vocabulary. A catalogue folder chooses its vocabulary through the manifest field `interest_taxonomy`. A folder without that field uses the old 20-term vocabulary, so the frozen v1.2.0 and v1.3.0 snapshots stay valid without being edited. With taxonomy 2.0 every career must have exactly three interests.

### Scoring

Unchanged: required skills 0.55, preferred skills 0.15, interests 0.25, education 0.05. The interest value is still matched interests divided by the career's listed interests. The ranking and the career-ID tie-break are unchanged. RIASEC is not used in any calculation.

### Interface

- The interest section explains that interests are work the learner enjoys, without needing the skills yet, and that skills are asked separately.
- The 23 interests are shown as checkboxes under the six RIASEC headings, with a one-line description of each group. Each interest has a help tooltip with its explanation, example and related skill.
- Saving more than 5 interests shows a warning. All of them are still saved and scored. The API adds the same warning.
- The Recommendations page, Career Explorer and explanations show the full interest names.

### API output

`recommend()` keeps `matched_interests` and `career_interests` (stored forms) and adds `matched_interest_labels` and `career_interest_labels` (full names). The profile report adds `migrated_interests` and `retired_interests`.

## 3. Migration of old interest names

Applied when a profile is built against the v1.4.0 catalogue, so it covers the assessment form, uploaded session files (versions 1 and 2) and API input. It is never applied to the frozen snapshots.

| Old interest | New interest |
|---|---|
| analysis | Analysing data and information |
| building software | Writing software and building apps |
| business | Running and growing a business |
| environment | Working outdoors and with the natural environment |
| healthcare | Caring for people's health |
| helping people | Helping and advising people |
| leadership | Leading people and projects |
| mathematics | Working with numbers and calculations |
| organization | Keeping information, records and procedures in order |
| research | Researching and investigating |
| science | Scientific and laboratory work |
| security | Keeping computer systems and data safe |
| teaching | Teaching and training others |
| visual arts | Creating visual art and graphics |
| writing | Writing and editing |

These follow the default rules in the first audit, section 7. Five old terms have no single replacement and are **retired, not guessed**: communication (now a skill only), design (split into three possible terms), engineering (a category name), problem solving (an ability), technology (too broad). They are not scored, and the learner is told which interests to choose instead.

Other accepted inputs: the exact name, the stored form, any capitalisation, and the draft French name. Unknown values are listed back as before. Duplicates after migration count once.

The session file format is unchanged (version 2). Old files load, the form ticks the migrated interests and shows a note naming the old terms, and a new download writes the current stored forms.

## 4. New evaluation (eval_v1.4.0_taxonomy)

### Method

- Code: `src/evaluation/taxonomy_v140_evaluation.py`. Outputs: `reports/evaluation_v1_4_0/`. Reproduce with `python -m src.evaluation.taxonomy_v140_evaluation --check reports/evaluation_v1_4_0`.
- Data: the frozen eval64_v1 profiles (111) and labels (363, single author, no second review yet), read in place and checked against their SHA-256 values. Nothing is copied or rewritten.
- Three conditions, same profiles and labels, same metrics and bootstrap as eval64_v1 (2,000 profile-level resamples, seed 64. Differences use a paired bootstrap):
  - **A**: v1.3.0 catalogue, original profiles. This is the frozen eval64_v1 configuration, and it reproduces the frozen means exactly.
  - **A2**: v1.3.0 catalogue, profiles without the five retired old terms. This isolates the loss caused by retiring terms.
  - **B**: v1.4.0 catalogue, profile interests migrated with the rules in section 3.
- Published outputs are aggregate only. Per-profile and per-pair results stay unpublished, like eval64_v1, until the second review is complete.

### Results

| Metric | A (v1.3.0) | A2 (retired removed) | B (v1.4.0, 95% CI) | B minus A (95% CI) | B minus A2 (95% CI) |
|---|---|---|---|---|---|
| precision_at_1 | 0.8119 | 0.7921 | 0.7426 (0.6531 to 0.828) | -0.0693 (-0.1373 to 0.0) | -0.0495 (-0.1146 to 0.0099) |
| precision_at_3 | 0.4125 | 0.396 | 0.3927 (0.3498 to 0.4369) | -0.0198 (-0.0533 to 0.0131) | -0.0033 (-0.03 to 0.0227) |
| precision_at_5 | 0.303 | 0.2911 | 0.2772 (0.248 to 0.3068) | -0.0257 (-0.044 to -0.0083) | -0.0139 (-0.03 to 0.002) |
| recall_at_5 | 0.901 | 0.8597 | 0.8168 (0.7492 to 0.881) | -0.0842 (-0.1414 to -0.0317) | -0.0429 (-0.09 to 0.0017) |
| f1_at_5 | 0.437 | 0.4187 | 0.3989 (0.3618 to 0.4353) | -0.0381 (-0.0642 to -0.0132) | -0.0198 (-0.0431 to 0.0023) |
| hit_at_5 | 1.0 | 0.9307 | 0.9109 (0.85 to 0.9612) | -0.0891 (-0.15 to -0.0388) | -0.0198 (-0.068 to 0.0208) |
| reciprocal_rank | 0.8843 | 0.8511 | 0.8151 (0.7488 to 0.8776) | -0.0692 (-0.1214 to -0.0199) | -0.036 (-0.0847 to 0.0082) |
| average_precision | 0.7948 | 0.7709 | 0.7264 (0.6602 to 0.7908) | -0.0684 (-0.1164 to -0.0256) | -0.0445 (-0.085 to -0.0103) |
| ndcg_at_5 | 0.7592 | 0.7303 | 0.6774 (0.6193 to 0.7326) | -0.0818 (-0.1214 to -0.0441) | -0.053 (-0.0861 to -0.0217) |

Binary metrics use the 101 profiles with at least one relevant label. NDCG@5 uses all 111.

| Category of the profile | Profiles | NDCG@5 A | NDCG@5 B | Top-5 slot share A | Top-5 slot share B |
|---|---|---|---|---|---|
| Data and AI | 11 | 0.8304 | 0.8096 | 0.227 | 0.2523 |
| Software | 11 | 0.7201 | 0.7237 | 0.1063 | 0.1189 |
| Cybersecurity | 11 | 0.61 | 0.4831 | 0.0757 | 0.0667 |
| Design | 11 | 0.735 | 0.5569 | 0.0919 | 0.0919 |
| Business | 11 | 0.7087 | 0.6914 | 0.1441 | 0.1477 |
| Education | 11 | 0.8147 | 0.8141 | 0.0703 | 0.0847 |
| Healthcare | 11 | 0.8098 | 0.7921 | 0.0919 | 0.1135 |
| Engineering | 14 | 0.8241 | 0.714 | 0.1063 | 0.0775 |
| Law | 10 | 0.7092 | 0.4431 | 0.0378 | 0.0144 |
| Social Sciences | 10 | 0.8122 | 0.7181 | 0.0486 | 0.0324 |

Category values rest on 10 to 14 profiles each and are indicative only.

### Interpretation

1. **On the eval64 profiles, condition B scores lower than the frozen result.** NDCG@5 falls from 0.759 to 0.677 (paired difference -0.082, 95% CI -0.121 to -0.044). 105 of 111 profiles get a different top 5. 24 profiles improve on NDCG@5, 50 get worse and 37 are unchanged.
2. **About a third of the fall comes from retiring old terms.** The eval64 profiles hold 269 interests. 72 of them are retired terms (technology 30, engineering 16, design 12, problem solving 9, communication 5), so after migration 10 profiles have no interest left. Removing those terms alone (A2) lowers NDCG@5 by 0.029.
3. **The rest is largely a measurement artefact of migration.** 8 of the 23 new interests cannot be reached from any old interest name:
   - Setting up and running computer systems and networks
   - Working with tools, machines and equipment
   - Designing apps, websites and user experiences
   - Designing buildings, structures and physical products
   - Persuading, presenting and negotiating
   - Working with communities
   - Working with laws, rules and regulations
   - Managing money and financial information

   12 careers have only one reachable interest. The losses concentrate where those terms matter: Law (NDCG@5 0.709 to 0.443), Design, Cybersecurity, Engineering and Social Sciences. A learner using the new form could select those interests, but a migrated old profile cannot.
4. **What this evaluation does and does not show.** It shows how profiles written in the old vocabulary are ranked after migration. It does not show whether the new taxonomy is better or worse for learners who choose from the 23 terms. That needs new profiles written with the new vocabulary, ideally by someone other than the author, with the analysis planned in advance (eval64_v2).
5. **Practical consequence.** Saved sessions and API calls that still use the old names will get somewhat worse results until the learner reselects their interests. The interface tells them which old terms were retired, and the API returns the same warning.

## 5. Frozen studies

| Study | Status |
|---|---|
| Original 50-career evaluation (`data/evaluation/catalog_v1.2.0/`, five saved reports) | Unchanged. SHA-256 checks pass |
| eval64_v1 (`data/evaluation/catalog_v1.3.0/`, `reports/evaluation_64/`, sensitivity and review-design reports) | Unchanged. SHA-256 checks pass and `--check` reproduces every output |
| Labels | Not changed, not copied, still withheld |

One code change touches the eval64_v1 reproduction check. The frozen summary records `live_catalogue_matches_frozen: true`, a fact about the live catalogue on the day of freezing, which can no longer be recomputed once the live catalogue is v1.4.0. The check now requires the saved value to be exactly `true` and the recomputed value to be exactly `false` before it sets that one field aside, so an edit of the saved value is reported. Every metric and every other field is compared exactly. In addition, `tests/test_frozen_report_hashes.py` pins the SHA-256 of all 35 published files in `reports/evaluation_64/`, `reports/evaluation_64_sensitivity/` and `reports/evaluation_64_review_design/`, so public CI protects them even though the label-dependent reproduction tests are skipped there.

## 6. Known limitations

1. Lecturer feedback has not been received. The taxonomy is not lecturer-approved or academically validated.
2. O*NET interest codes describe US occupations. 12 careers have no O*NET code and their assignments are provisional.
3. The evaluation uses synthetic profiles and single-author labels. Its numbers describe agreement with those labels, not real-world recommendation accuracy.
4. The evaluation profiles were written in the old vocabulary and migrated mechanically (section 4), so the before-and-after comparison is confounded.
5. The French names are unreviewed drafts and are not shown to learners.
6. The 5-interest soft limit has not been tested with real or realistic profiles.
7. The RIASEC grouping is the second review's interpretation, with six uncertain placements (`docs/lecturer_review/riasec_classification_review.md`).

## 7. Implementation risks

| Risk | Mitigation |
|---|---|
| Lecturer requests changes after implementation | Everything is versioned: a change means dataset v1.5.0, a new snapshot and a new evaluation. v1.4.0 stays frozen |
| Old-vocabulary inputs rank worse (section 4) | Retired terms are reported, never guessed. Learners are asked to reselect. T-Career should send the new names |
| Eight new interests cannot be produced by migration | Documented. Migrated profiles get a note. New learners choose from all 23 |
| Stored form differs from the display name | One function (`label_for`) maps stored forms to names. The API returns both |
| Broad records term (18 careers) and Conventional-heavy IT terms may favour IT and business careers | Exposure is reported per category in the evaluation. Data and AI top-5 share moved from 22.7% to 25.2% under B |
| Career-ID tie-break still decides ties | Unchanged by design. A separate, pre-registered tie-break study is still needed |
| Synthetic results read as accuracy | Stated in the evaluation summary, this document and the reports |

## 8. Career assignment changes (v1.3.0 to v1.4.0)

Every career changed, because the whole vocabulary changed. The last column marks the 18 careers where the second review changed the first audit's draft beyond renaming.

| Career ID | Career title | Category | Interests in v1.3.0 | Interests in v1.4.0 | Confidence | Changed from the first audit draft |
|---|---|---|---|---|---|---|
| C001 | Data Scientist | Data and AI | analysis, mathematics, research, technology | Analysing data and information / Working with numbers and calculations / Writing software and building apps | High | No |
| C002 | Data Analyst | Data and AI | analysis, business, problem solving | Analysing data and information / Keeping information, records and procedures in order / Persuading, presenting and negotiating | Provisional | No |
| C003 | Machine Learning Engineer | Data and AI | technology, building software, mathematics | Writing software and building apps / Working with numbers and calculations / Setting up and running computer systems and networks | Provisional | No |
| C004 | Business Intelligence Analyst | Data and AI | analysis, business, organization | Analysing data and information / Keeping information, records and procedures in order / Running and growing a business | High | No |
| C005 | Data Engineer | Data and AI | technology, building software, organization | Setting up and running computer systems and networks / Writing software and building apps / Keeping information, records and procedures in order | Medium | No |
| C006 | Statistician | Data and AI | mathematics, research, analysis | Working with numbers and calculations / Researching and investigating / Analysing data and information | High | No |
| C007 | AI Research Scientist | Data and AI | research, mathematics, technology | Researching and investigating / Working with numbers and calculations / Writing software and building apps | Medium | No |
| C008 | Database Administrator | Data and AI | technology, organization, problem solving | Setting up and running computer systems and networks / Keeping information, records and procedures in order / Keeping computer systems and data safe | High | No |
| C009 | Software Developer | Software | building software, technology, problem solving | Writing software and building apps / Designing apps, websites and user experiences / Researching and investigating | Medium | Yes |
| C010 | Web Developer | Software | building software, design, technology | Writing software and building apps / Designing apps, websites and user experiences / Setting up and running computer systems and networks | Medium | Yes |
| C011 | Software Quality Assurance Tester | Software | technology, problem solving, organization | Researching and investigating / Keeping information, records and procedures in order / Setting up and running computer systems and networks | High | No |
| C012 | Mobile App Developer | Software | building software, design, technology | Writing software and building apps / Designing apps, websites and user experiences / Creating visual art and graphics | Provisional | Yes |
| C013 | DevOps Engineer | Software | technology, building software, problem solving | Setting up and running computer systems and networks / Writing software and building apps / Keeping information, records and procedures in order | Medium | No |
| C014 | Cloud Engineer | Software | technology, building software, organization | Setting up and running computer systems and networks / Writing software and building apps / Keeping computer systems and data safe | Medium | No |
| C015 | Computer Programmer | Software | building software, problem solving, technology | Writing software and building apps / Working with numbers and calculations / Keeping information, records and procedures in order | High | No |
| C016 | Computer Systems Analyst | Software | business, technology, problem solving | Analysing data and information / Researching and investigating / Keeping information, records and procedures in order | High | Yes |
| C017 | Information Security Analyst | Cybersecurity | security, technology, problem solving | Keeping computer systems and data safe / Analysing data and information / Researching and investigating | High | No |
| C018 | Penetration Tester | Cybersecurity | security, problem solving, technology | Keeping computer systems and data safe / Researching and investigating / Writing software and building apps | High | No |
| C019 | Digital Forensics Analyst | Cybersecurity | security, research, analysis | Keeping computer systems and data safe / Researching and investigating / Working with laws, rules and regulations | Medium | No |
| C020 | Network and Systems Administrator | Cybersecurity | technology, organization, problem solving | Setting up and running computer systems and networks / Keeping computer systems and data safe / Keeping information, records and procedures in order | High | No |
| C021 | Computer Network Architect | Cybersecurity | technology, design, organization | Setting up and running computer systems and networks / Keeping computer systems and data safe / Researching and investigating | Medium | Yes |
| C022 | Information Security Engineer | Cybersecurity | security, technology, building software | Keeping computer systems and data safe / Writing software and building apps / Setting up and running computer systems and networks | High | Yes |
| C023 | Graphic Designer | Design | design, visual arts, communication | Creating visual art and graphics / Designing apps, websites and user experiences / Persuading, presenting and negotiating | Medium | No |
| C024 | UX Designer | Design | design, helping people, technology | Designing apps, websites and user experiences / Researching and investigating / Helping and advising people | Medium | No |
| C025 | Interior Designer | Design | design, visual arts, organization | Creating visual art and graphics / Designing buildings, structures and physical products / Persuading, presenting and negotiating | High | No |
| C026 | Industrial Designer | Design | design, engineering, visual arts | Designing buildings, structures and physical products / Creating visual art and graphics / Working with tools, machines and equipment | High | No |
| C027 | Animator | Design | visual arts, design, technology | Creating visual art and graphics / Writing and editing / Designing apps, websites and user experiences | Medium | No |
| C028 | Management Analyst | Business | business, problem solving, analysis | Analysing data and information / Running and growing a business / Keeping information, records and procedures in order | High | Yes |
| C029 | Financial Analyst | Business | business, mathematics, analysis | Managing money and financial information / Analysing data and information / Working with numbers and calculations | High | Yes |
| C030 | Accountant | Business | business, organization, mathematics | Managing money and financial information / Keeping information, records and procedures in order / Working with laws, rules and regulations | High | Yes |
| C031 | Market Research Analyst | Business | business, research, analysis | Researching and investigating / Analysing data and information / Running and growing a business | High | No |
| C032 | Project Manager | Business | leadership, organization, business | Leading people and projects / Keeping information, records and procedures in order / Running and growing a business | High | No |
| C033 | Human Resources Specialist | Business | helping people, business, communication | Persuading, presenting and negotiating / Keeping information, records and procedures in order / Helping and advising people | High | Yes |
| C034 | Digital Marketing Specialist | Business | business, communication, writing | Persuading, presenting and negotiating / Writing and editing / Analysing data and information | Medium | No |
| C035 | Secondary School Teacher | Education | teaching, helping people, communication | Teaching and training others / Helping and advising people / Persuading, presenting and negotiating | High | No |
| C036 | Instructional Designer | Education | teaching, design, technology | Teaching and training others / Designing apps, websites and user experiences / Writing and editing | Medium | No |
| C037 | English as a Second Language Teacher | Education | teaching, helping people, communication | Teaching and training others / Helping and advising people / Writing and editing | High | No |
| C038 | School Counselor | Education | helping people, teaching, communication | Helping and advising people / Teaching and training others / Working with communities | Medium | No |
| C039 | Computer Science Lecturer | Education | teaching, technology, research | Teaching and training others / Researching and investigating / Writing software and building apps | High | No |
| C040 | Registered Nurse | Healthcare | healthcare, helping people, science | Caring for people's health / Helping and advising people / Keeping information, records and procedures in order | High | No |
| C041 | Pharmacist | Healthcare | healthcare, science, helping people | Scientific and laboratory work / Caring for people's health / Keeping information, records and procedures in order | High | Yes |
| C042 | Medical Laboratory Technologist | Healthcare | science, healthcare, analysis | Scientific and laboratory work / Analysing data and information / Working with tools, machines and equipment | High | Yes |
| C043 | Medical Records Specialist | Healthcare | healthcare, organization, technology | Keeping information, records and procedures in order / Working with laws, rules and regulations / Analysing data and information | High | Yes |
| C044 | Dietitian and Nutritionist | Healthcare | healthcare, helping people, science | Caring for people's health / Helping and advising people / Scientific and laboratory work | High | Yes |
| C045 | Physical Therapist | Healthcare | healthcare, helping people, science | Caring for people's health / Teaching and training others / Helping and advising people | Medium | Yes |
| C046 | Civil Engineer | Engineering | engineering, mathematics, environment | Designing buildings, structures and physical products / Working outdoors and with the natural environment / Working with numbers and calculations | High | No |
| C047 | Mechanical Engineer | Engineering | engineering, mathematics, building software | Designing buildings, structures and physical products / Working with tools, machines and equipment / Working with numbers and calculations | Medium | No |
| C048 | Electrical Engineer | Engineering | engineering, mathematics, technology | Working with tools, machines and equipment / Working with numbers and calculations / Designing buildings, structures and physical products | Medium | No |
| C049 | Environmental Engineer | Engineering | environment, engineering, science | Working outdoors and with the natural environment / Scientific and laboratory work / Designing buildings, structures and physical products | High | No |
| C050 | Biomedical Engineer | Engineering | engineering, healthcare, science | Designing buildings, structures and physical products / Scientific and laboratory work / Caring for people's health | Medium | No |
| C051 | Mining Engineer | Engineering | engineering, environment, mathematics, problem solving | Working outdoors and with the natural environment / Working with tools, machines and equipment / Working with numbers and calculations | Medium | No |
| C052 | Geological Engineer | Engineering | engineering, science, environment, research | Working outdoors and with the natural environment / Scientific and laboratory work / Researching and investigating | Medium | No |
| C053 | Telecommunications Engineer | Engineering | engineering, technology, problem solving | Setting up and running computer systems and networks / Working with tools, machines and equipment / Working with numbers and calculations | Provisional | Yes |
| C054 | Building Engineer | Engineering | engineering, design, organization | Designing buildings, structures and physical products / Leading people and projects / Working with tools, machines and equipment | Provisional | No |
| C055 | Geotechnical Engineer | Engineering | engineering, science, environment, mathematics | Working outdoors and with the natural environment / Scientific and laboratory work / Working with numbers and calculations | Provisional | No |
| C056 | Geophysicist | Engineering | science, research, mathematics, environment | Researching and investigating / Working with numbers and calculations / Working outdoors and with the natural environment | Medium | No |
| C057 | Private Law Specialist | Law | analysis, writing, business, problem solving | Working with laws, rules and regulations / Writing and editing / Persuading, presenting and negotiating | Provisional | No |
| C058 | Public Law Specialist | Law | analysis, writing, leadership, helping people | Working with laws, rules and regulations / Writing and editing / Working with communities | Provisional | Yes |
| C059 | Management Information Systems Specialist (MIAGE) | Business | technology, business, organization, leadership | Keeping information, records and procedures in order / Setting up and running computer systems and networks / Leading people and projects | Provisional | No |
| C060 | Economist | Social Sciences | analysis, mathematics, research, business | Analysing data and information / Working with numbers and calculations / Researching and investigating | High | No |
| C061 | Business Administration Specialist | Business | business, leadership, organization | Running and growing a business / Leading people and projects / Managing money and financial information | Provisional | Yes |
| C062 | Laboratory Technician | Healthcare | science, analysis, organization, healthcare | Scientific and laboratory work / Keeping information, records and procedures in order / Working with tools, machines and equipment | Provisional | No |
| C063 | Sociologist | Social Sciences | research, helping people, writing, analysis | Researching and investigating / Working with communities / Writing and editing | High | No |
| C064 | Community Relations Specialist | Business | communication, helping people, leadership, environment | Working with communities / Persuading, presenting and negotiating / Working outdoors and with the natural environment | Provisional | No |

## 9. Deployment decision

On 3 November 2026 the project owner authorized committing v1.4.0 to `main` and deploying it to the live application, after reading the final pre-commit review (`docs/interest_taxonomy_final_precommit_review.md`). That review had recommended waiting for lecturer feedback and eval64_v2. The deployment is the owner's decision. Lecturer feedback is still pending, and eval64_v2 has not been run.

Before deployment, a notice was added above the interest list. It explains that the list changed in November 2026, that scores can differ, and that learners with a saved session should review and reselect their interests. A notice for integrators is in `docs/integration_api.md`.
