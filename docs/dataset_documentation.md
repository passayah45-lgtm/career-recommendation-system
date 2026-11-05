# Dataset Documentation

Version: 1.4.0 (document structure from 1.2.0; dataset changes listed in section 16)
Last updated: 2026-11-03
Phase: 2 (Dataset Engineering and Validation)

## 1. Purpose and scope

The dataset supports three later features:

1. Career recommendations: match a learner profile against career requirements.
2. Skill-gap analysis: list the skills a learner lacks for a career.
3. Learning resources: point each missing skill to at least one learning resource.

Scope (dataset v1.4.0): 64 careers in 10 categories, 144 unique skills, 144 learning resources, 56 skill aliases. The original v1.2.0 dataset (50 careers, 8 categories, 114 skills, 114 resources, 37 aliases) is frozen in data/evaluation/catalog_v1.2.0/ and is the only dataset the saved evaluation reports describe. The v1.3.0 dataset is frozen in data/evaluation/catalog_v1.3.0/ (eval64_v1) and v1.4.0 in data/evaluation/catalog_v1.4.0/. v1.4.0 differs from v1.3.0 only in the interests column. The data is an academic MVP dataset. It is not a labour market database.

## 2. Files

| File | Rows | Purpose |
|---|---|---|
| data/raw/careers.csv | 64 | Career records |
| data/raw/resources.csv | 144 | One learning resource per skill |
| data/raw/skill_aliases.csv | 56 | Alternative names that map to a canonical skill, including French forms |
| data/raw/dataset_manifest.json | n/a | Expected counts (careers, unique skills, resources) that the validator enforces |
| data/evaluation/catalog_v1.2.0/ | n/a | Frozen copy of the 50-career dataset (v1.2.0) used by every saved evaluation report; never edited, checked by SHA-256 |

All files are UTF-8 CSV with a header row.

## 3. Categories and record counts

| Category | Careers (v1.3.0) | Of which added in v1.3.0 |
|---|---|---|
| Engineering | 11 | 6 |
| Business | 10 | 3 |
| Data and AI | 8 | 0 |
| Software | 8 | 0 |
| Healthcare | 7 | 1 |
| Cybersecurity | 6 | 0 |
| Design | 5 | 0 |
| Education | 5 | 0 |
| Law | 2 | 2 (new category) |
| Social Sciences | 2 | 2 (new category) |
| Total | 64 | 14 |

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
| interests | list | yes | Values from the controlled interest vocabulary (section 7), exactly three per career from v1.4.0 |
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

Distribution (v1.3.0, 64 careers): level 2 has 2 careers, level 3 has 50, level 4 has 12. The original 50 careers keep their v1.2.0 distribution: level 2 has 1, level 3 has 42, level 4 has 7.

For the 14 careers added in v1.3.0, `research/data/expansion_education_basis.csv` labels each level either `estimate` (9 careers) or `estimate_supported_by_us_reference` (5 careers, with the O*NET or BLS evidence quoted). No level was taken from an African source.

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

Controlled interest vocabulary (interest taxonomy 2.0, dataset v1.4.0, 23 values, exactly three per career). Owner-authorized implementation pending lecturer feedback; details in docs/interest_taxonomy_implementation.md. Names, descriptions, examples, related skills and RIASEC display groups are in src/data/interest_taxonomy.py. Each value is stored as its name in lowercase with punctuation removed (rule 3 above), for example "Caring for people's health" is stored as caring for peoples health:

| RIASEC group (display only) | Interests (full names) |
|---|---|
| Realistic | Setting up and running computer systems and networks. Working with tools, machines and equipment. Working outdoors and with the natural environment. Designing buildings, structures and physical products |
| Investigative | Analysing data and information. Researching and investigating. Working with numbers and calculations. Scientific and laboratory work. Writing software and building apps |
| Artistic | Creating visual art and graphics. Designing apps, websites and user experiences. Writing and editing |
| Social | Teaching and training others. Caring for people's health. Helping and advising people. Working with communities |
| Enterprising | Leading people and projects. Running and growing a business. Persuading, presenting and negotiating |
| Conventional | Keeping information, records and procedures in order. Keeping computer systems and data safe. Working with laws, rules and regulations. Managing money and financial information |

The manifest field interest_taxonomy ("2.0") selects this vocabulary. A folder without the field uses the legacy 20-value vocabulary of datasets 1.0.0 to 1.3.0 (analysis, building software, business, communication, design, engineering, environment, healthcare, helping people, leadership, mathematics, organization, problem solving, research, science, security, teaching, technology, visual arts, writing), which keeps the frozen snapshots valid.

Cleaning is explicit and separate from validation. src/data/preprocessing.py holds clean_skill_text and normalize_skill, which are covered by tests. The validator never repairs data.

Accents: learner input is accent-folded before matching (Unicode NFKD with combining marks removed), so "Géologie", "géologie" and "geologie" all give "geologie". Alias lookup tries the exact text first, then the folded text, then folded alias keys. The validator rejects aliases whose folded forms would point to two different skills or shadow another canonical skill.

## 8. Skill statistics

| Measure | Count |
|---|---|
| Unique required skills | 131 |
| Unique preferred skills | 62 |
| Preferred skills that are never required | 13 |
| Unique skills needing a resource | 144 |
| Skills without a resource | 0 |
| Average required skills per career | 3.81 |

Most common required skills in v1.3.0: communication (12 careers). In v1.2.0: communication (8 careers), python, sql, excel, linux (6 each), git, network security, cad (5 each).

## 9. Sources and collection method

### Career records

1. Occupation mapping: 47 of the original 50 careers map to an O*NET-SOC occupation; 5 of the 14 careers added in v1.3.0 do (52 of 64). See docs/african_expansion_sources.md for the new careers. The source_url points to the O*NET OnLine summary page for that code. O*NET is maintained for the U.S. Department of Labor.
2. Careers without a matching O*NET occupation: Data Analyst, Machine Learning Engineer and Mobile App Developer. Their onet_code and source_url are empty. The validator reports them as warnings.
3. Nearest-occupation mappings: some titles map to a broader O*NET occupation. Data Engineer maps to Data Warehousing Specialists (15-1243.01), Cloud Engineer to Computer Systems Engineers/Architects (15-1299.08), Instructional Designer to Instructional Coordinators (25-9031.00), Digital Marketing Specialist to Search Marketing Strategists (13-1161.01), UX Designer to Web and Digital Interface Designers (15-1255.00), DevOps Engineer to Software Developers (15-1252.00, where O*NET OnLine lists "DevOps Engineer" as a reported job title, checked 2026-10-26), AI Research Scientist to Computer and Information Research Scientists (15-1221.00).

What is sourced and what is curated:

| Field | Origin |
|---|---|
| career_title, onet_code, source_url | Sourced: the O*NET occupation and URL were confirmed |
| description | Curated: written by the project author as a short summary. Not quoted from O*NET |
| required_skills, preferred_skills | Curated: selected by the project author to fit the occupation and the resource catalogue |
| interests | v1.4.0: from docs/interest_taxonomy_second_review.md, checked against O*NET interest codes for the 52 careers with an O*NET code (12 careers provisional). Not lecturer-approved yet |
| learning_goals | Curated: written for the recommender, not taken from O*NET |
| education_level | Curated: see section 6 |

### Resource records

Each resource was found by targeted web search for the specific skill. Selection rules:

1. Prefer official documentation (Python, PostgreSQL, MDN, Kubernetes), open textbooks (OpenStax, BCcampus, University of Minnesota), universities (MIT OpenCourseWare, Harvard, Carnegie Mellon), government bodies (NIST, CDC, GOV.UK, IRS) and recognised professional organisations.
2. Prefer a page that teaches the skill over a provider home page.
3. One resource per skill in version 1.0, with no URL reused across skills.

## 10. Free access assessment

is_free is true only when the learning content itself is available at no cost. All 144 rows are currently true. Conditions that do not change the value but are recorded in notes:

1. A free account is required: MATLAB Onramp, Cisco Networking Academy, Saylor Academy, PortSwigger labs, British Council courses, CDC lab training.
2. The software is free: Blender, FreeCAD, Inkscape, QGIS, DaVinci Resolve (free edition).
3. Optional payment: Practical Typography asks readers for voluntary payment.
4. Vendor platform: Microsoft Learn labs, Microsoft Sentinel and Power BI service features may need a paid subscription. The reading material is free.

The free status was assessed from the provider's own description of the resource. It was not tested by completing each course, so a provider may change its terms.

## 11. URL verification method and limits

Two methods were used, both on 2026-10-14.

Search index check (all 160 URLs, during Phase 2):

1. The project workspace had no direct internet access, so each URL was confirmed by checking that the exact URL appeared in web search results with a matching page title. These rows were marked search_index_confirmed.

HTTP check (Phase 5, src/data/url_checker.py, run from the author's laptop):

1. 150 of 160 URLs answered successfully, including all 46 career source URLs.
2. 104 resources are now marked http_checked. Their notes keep the earlier status.
3. 9 resources (open.edu, open.lib.umn.edu, pressbooks.pub) refused the checker with HTTP 403 and 1 (Inkscape) timed out while its server showed "502 Bad Gateway". These 10 keep search_index_confirmed.
4. One resource returned HTTP 404 and was replaced: R045 graphic design now points to Canva Design School "Graphic design basics".
5. Link repair audit, 2026-11-06: the 40 resources never opened by the checker and R093 were opened with a web tool. Two resources were relinked. R048 human resource management: the University of Minnesota book was removed from its collection, so it now points to chapter 1 of the Lumen Learning "Human Resources Management" open textbook on LibreTexts (CC BY 4.0). R120 geophysical methods: the link pointed to the book's source files on GitHub, so it now points to the readable book at gpg.geosci.xyz (CC BY 4.0). Both are recorded in data/resource_link_replacements.csv. Full evidence: docs/learning_link_audit_2026-11-06.md.

Full results: docs/evaluation_report.md section 8, reports/url_check.json and reports/url_check_run2.json.

Limits:

1. http_checked means the server returned a 2xx or 3xx response on that date. It does not prove the content is unchanged or free of a login wall.
2. search_index_confirmed means the page existed in the search index. It does not prove the page returns HTTP 200.
3. Some URLs point to a version that can change: "latest" Blender and Spark manuals, "current" PostgreSQL documentation, QGIS 3.44.

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
2. Pick a category from the approved values (CATEGORIES in src/data/validation.py). Law and Social Sciences are planned but not yet approved.
3. Write skills, interests and goals with the normalisation rules in section 7. Reuse existing skill names where possible.
4. Add onet_code and source_url when an O*NET occupation matches. Leave both empty otherwise.
5. Update the counts in data/raw/dataset_manifest.json (careers, skills, resources) in the same change, and update this document. Never edit data/evaluation/catalog_v1.2.0/, which keeps the original evaluation reproducible.
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
| 1.1.0 | 2026-10-14 | HTTP link check: 104 resources http_checked, R045 replaced after a 404 |
| 1.2.0 | 2026-10-26 | C013 DevOps Engineer mapped to O*NET 15-1252.00 as a nearest-broader occupation; AI Research Scientist recorded as nearest-broader. Its source URL is the same page already checked for C009 on 2026-10-14 |
| 1.3.0 | 2026-11-01 | African career expansion from the lecturer's list: 14 careers added (C051 to C064), 30 skills with 30 resources (R115 to R144), 19 aliases including French forms, categories Law and Social Sciences. Civil Engineer, Electrical Engineer and Human Resources Specialist already existed (C046, C048, C033) and were not duplicated. The 50 original rows are unchanged. Sources and gaps: docs/african_expansion_sources.md |
| 1.4.0 | 2026-11-03 | Interest taxonomy 2.0: the interests column of all 64 careers replaced with the second review's assignments (23-term vocabulary, exactly three per career); manifest field interest_taxonomy added. No other column changed. Owner-authorized pending lecturer feedback. Details: docs/interest_taxonomy_implementation.md |
| 1.4.0 (link repair) | 2026-11-06 | R048 relinked to a verified free open textbook for the same skill after the original book was removed. R120 relinked from the book's source files to the readable book. Skill, free status, type, level and language unchanged, so the dataset version is not changed. Frozen catalogues unchanged. Details: docs/learning_link_audit_2026-11-06.md |
