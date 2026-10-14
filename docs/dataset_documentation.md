# Dataset Documentation

Version: 1.0.0
Last updated: 2026-10-14
Phase: 2 (Dataset Engineering and Validation)

## 1. Purpose and scope

The dataset supports three later features:

1. Career recommendations: match a learner profile against career requirements.
2. Skill-gap analysis: list the skills a learner lacks for a career.
3. Learning resources: point each missing skill to at least one learning resource.

Scope: 50 careers in 8 categories, 114 unique skills, 114 learning resources, 37 skill aliases. The data is an academic MVP dataset. It is not a labour market database.

## 2. Files

| File | Rows | Purpose |
|---|---|---|
| data/raw/careers.csv | 50 | Career records |
| data/raw/resources.csv | 114 | One learning resource per skill |
| data/raw/skill_aliases.csv | 37 | Alternative names that map to a canonical skill |

All files are UTF-8 CSV with a header row.

## 3. Categories and record counts

| Category | Careers |
|---|---|
| Data and AI | 8 |
| Software | 8 |
| Business | 7 |
| Cybersecurity | 6 |
| Healthcare | 6 |
| Design | 5 |
| Education | 5 |
| Engineering | 5 |
| Total | 50 |

The split is not equal. Data and AI and Software have more careers because they are closest to the T-Career audience. Every category has at least 5 careers.

## 4. Career schema (careers.csv)

| Field | Type | Required | Allowed values and rules |
|---|---|---|---|
| career_id | string | yes | C followed by three digits, for example C001. Stable, never reused |
| career_title | string | yes | Unique after ignoring case and punctuation |
| category | string | yes | One of the 8 approved categories |
| description | string | yes | At least 6 words |
| required_skills | list | yes | Canonical skill names, pipe separated |
| preferred_skills | list | no | Same rules as required_skills. No skill may appear in both lists |
| education_level | integer | yes | 0 to 4, see section 6 |
| interests | list | yes | Values from the controlled interest vocabulary (section 7) |
| learning_goals | list | yes | Short outcomes a learner can work towards, pipe separated |
| onet_code | string | no | O*NET-SOC code such as 15-2051.00 |
| source_url | string | no | O*NET OnLine summary page for onet_code |

## 5. Resource schema (resources.csv)

| Field | Type | Required | Allowed values and rules |
|---|---|---|---|
| resource_id | string | yes | R followed by three digits |
| skill_name | string | yes | Exact canonical skill name used in careers.csv |
| resource_title | string | yes | Title as published by the provider |
| provider | string | yes | Publisher, university, organisation or platform |
| resource_url | string | yes | Direct http(s) URL to the resource |
| is_free | boolean | yes | true or false (lowercase) |
| resource_type | string | yes | book, course, documentation, guide, standard, tutorial |
| level | string | yes | beginner, intermediate, advanced |
| language | string | yes | ISO 639-1 two-letter code, currently en for all rows |
| url_verification | string | yes | search_index_confirmed, http_checked, unverified |
| verified_on | date | no | ISO date of the last verification |
| notes | string | no | Access conditions, regional scope or relevance limits |

Resource type definitions:

| Type | Meaning |
|---|---|
| book | Open textbook or free online book |
| course | Structured course with lessons, from a university or training platform |
| documentation | Official product or language documentation |
| guide | Practical guidance article or handbook |
| standard | Formal standard or framework, for example a NIST publication |
| tutorial | Short hands-on lesson series |

## 6. Education level scale

| Level | Meaning |
|---|---|
| 0 | No formal qualification specified |
| 1 | Secondary education or equivalent |
| 2 | Certificate, vocational training or diploma |
| 3 | Bachelor's degree or equivalent |
| 4 | Master's degree or higher |

Distribution: level 2 has 1 career, level 3 has 42, level 4 has 7.

Interpretation rules:

1. The level is a simplified dataset category for typical entry. It is not a universal or legal requirement.
2. Many careers in this dataset accept equivalent experience, portfolios or certifications instead of a degree. The engine must treat education as one weighted signal, never as a hard filter.
3. The levels were assigned by the project author from general knowledge of typical entry requirements. They were not checked field by field against O*NET Job Zones in this phase. See section 12.

## 7. Normalisation rules

Lists:

1. Lists use the pipe character | as delimiter, with no spaces around it.
2. An empty optional list is an empty string.
3. A token may not repeat inside one list.

Skill names (and interests and learning goals):

1. Lowercase letters a to z and digits 0 to 9 only.
2. Words separated by exactly one space. No leading or trailing spaces.
3. No punctuation. Symbols are written as words or removed: "CI/CD" becomes "ci cd", "3D" stays "3d".
4. US spelling for canonical names: "modeling", "visualization", "counseling", "behavior".

Aliases: data/raw/skill_aliases.csv maps other names to the canonical skill, for example ml to machine learning, ci/cd to ci cd, data visualisation to data visualization. An alias may not be a canonical skill itself, and every target must exist in careers.csv. The alias file is for normalising learner input in later phases. It does not add skills.

Controlled interest vocabulary (20 values): analysis, building software, business, communication, design, engineering, environment, healthcare, helping people, leadership, mathematics, organization, problem solving, research, science, security, teaching, technology, visual arts, writing.

Cleaning is explicit and separate from validation. src/data/preprocessing.py holds clean_skill_text and normalize_skill, which are covered by tests. The validator never repairs data.

## 8. Skill statistics

| Measure | Count |
|---|---|
| Unique required skills | 102 |
| Unique preferred skills | 48 |
| Preferred skills that are never required | 12 |
| Unique skills needing a resource | 114 |
| Skills without a resource | 0 |
| Average required skills per career | 3.76 |

Most common required skills: communication (8 careers), python, sql, excel, linux (6 each), git, network security, cad (5 each).

## 9. Sources and collection method

### Career records

1. Occupation mapping: 46 of 50 careers map to an O*NET-SOC occupation. The source_url points to the O*NET OnLine summary page for that code. O*NET is maintained for the U.S. Department of Labor.
2. Careers without a matching O*NET occupation: Data Analyst, Machine Learning Engineer, Mobile App Developer and DevOps Engineer. Their onet_code and source_url are empty. The validator reports them as warnings.
3. Nearest-occupation mappings: some titles map to a broader O*NET occupation. Data Engineer maps to Data Warehousing Specialists (15-1243.01), Cloud Engineer to Computer Systems Engineers/Architects (15-1299.08), Instructional Designer to Instructional Coordinators (25-9031.00), Digital Marketing Specialist to Search Marketing Strategists (13-1161.01), UX Designer to Web and Digital Interface Designers (15-1255.00).

What is sourced and what is curated:

| Field | Origin |
|---|---|
| career_title, onet_code, source_url | Sourced: the O*NET occupation and URL were confirmed |
| description | Curated: written by the project author as a short summary. Not quoted from O*NET |
| required_skills, preferred_skills | Curated: selected by the project author to fit the occupation and the resource catalogue |
| interests, learning_goals | Curated: written for the recommender, not taken from O*NET interest profiles |
| education_level | Curated: see section 6 |

### Resource records

Each resource was found by targeted web search for the specific skill. Selection rules:

1. Prefer official documentation (Python, PostgreSQL, MDN, Kubernetes), open textbooks (OpenStax, BCcampus, University of Minnesota), universities (MIT OpenCourseWare, Harvard, Carnegie Mellon), government bodies (NIST, CDC, GOV.UK, IRS) and recognised professional organisations.
2. Prefer a page that teaches the skill over a provider home page.
3. One resource per skill in version 1.0, with no URL reused across skills.

## 10. Free access assessment

is_free is true only when the learning content itself is available at no cost. All 114 rows are currently true. Conditions that do not change the value but are recorded in notes:

1. A free account is required: MATLAB Onramp, Cisco Networking Academy, Saylor Academy, PortSwigger labs, British Council courses, CDC lab training.
2. The software is free: Blender, FreeCAD, Inkscape, QGIS, DaVinci Resolve (free edition).
3. Optional payment: Practical Typography asks readers for voluntary payment.
4. Vendor platform: Microsoft Learn labs, Microsoft Sentinel and Power BI service features may need a paid subscription. The reading material is free.

The free status was assessed from the provider's own description of the resource. It was not tested by completing each course, so a provider may change its terms.

## 11. URL verification method and limits

Method used on 2026-10-14:

1. The project workspace has no direct internet access, so HTTP status codes could not be checked.
2. Each URL was confirmed by running a web search and checking that the exact URL appeared in the results with a matching page title. These rows are marked search_index_confirmed.
3. All 46 career source URLs and all 114 resource URLs passed this check. No URL is marked unverified.

Limits:

1. search_index_confirmed means the page existed in the search index. It does not prove the page returns HTTP 200 today, or that it has no login wall.
2. Some URLs point to a version that can change: "latest" Blender and Spark manuals, "current" PostgreSQL documentation, QGIS 3.44.
3. Recommended next step: run an HTTP check from a machine with internet access and record the result as http_checked.

## 12. Assumptions, biases and gaps

1. Regional bias: O*NET, IRS, HHS (HIPAA), CDC (ICD-10-CM) and GOV.UK are US or UK sources. Tax rules, health privacy law and medical coding differ in India, Guinea and other countries.
2. Language: all resources are English. The language column supports adding French and other languages later.
3. Education levels are curated, not sourced (section 6).
4. Skills are curated, not taken from O*NET skill or technology lists.
5. Resource fit gaps, recorded in notes:
   - No free resource dedicated to interior design could be verified. The Interior Designer record uses "design thinking" as its design-process skill instead.
   - risk management uses the NIST Cybersecurity Framework, which covers project risk only in part.
   - engineering mathematics uses a calculus textbook only.
   - counseling uses a health education module, not a school counselling course.
   - business analysis and systems analysis use general information systems and software engineering material.
6. One resource per skill gives limited choice of format and level.
7. The dataset has no learner interaction data, so it supports content-based matching only.

## 13. How to add a career

1. Add a row to data/raw/careers.csv with the next free id (C051). Never reuse or renumber ids.
2. Pick a category from the 8 approved values.
3. Write skills, interests and goals with the normalisation rules in section 7. Reuse existing skill names where possible.
4. Add onet_code and source_url when an O*NET occupation matches. Leave both empty otherwise.
5. Change EXPECTED_CAREER_COUNT in src/data/validation.py and update this document.
6. Run validation. If a new skill has no resource, add one (next section).

## 14. How to add a skill or resource

1. Use the canonical skill name exactly as written in careers.csv.
2. Add a row to data/raw/resources.csv with the next free id (R115).
3. Verify the URL. Use search_index_confirmed or http_checked, or unverified if neither was possible.
4. Set is_free to true only when the content is fully free. Record conditions in notes.
5. If the skill has common alternative names, add them to data/raw/skill_aliases.csv.

## 15. Running validation and tests

From the project root:

```bash
python -m src.data.validation              # full report, exit code 1 on any error
python -m src.data.validation --quiet-warnings
python -m pytest -q
```

Errors stop the GitHub Actions workflow. Warnings (missing optional source URL, unverified URL, URL reused across skills) are printed but do not fail the build.

## 16. Change log

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-10-14 | First release: 50 careers, 114 resources, 37 aliases, validator and tests |
