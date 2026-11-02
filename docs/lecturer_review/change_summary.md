# Summary of key changes proposed by the second review

Source: `docs/interest_taxonomy_second_review.md`. Each figure below was checked by counting rows in that report's own tables (section B2 for terms, section C for careers). Where a figure in the request for this package or in the report text does not match the tables, the difference is stated and not silently corrected.

Nothing listed here has been applied. The production data, scoring formula, recommendation engine and assessment interface are unchanged.

## 1. Verified figures

| Item | Figure requested | Figure in the report's tables | Status |
|---|---|---|---|
| Interest terms in the revised vocabulary | 23 | 23 (section B2, and 23 distinct terms used in section C) | Confirmed |
| Retained terms | 11 | **12** (12 "Retain" rows in section B2) | **Does not match.** See section 2 |
| Renamed terms | 6 | 6 (5 "Rename" rows and 1 "Rename (order only)") | Confirmed |
| Split or replaced concepts | 3 | 3 first-audit terms (2 "Split", 1 "Replace"), giving 4 new terms | Confirmed, with the note that 3 concepts produce 4 terms |
| New financial interest | 1 | 1 ("Add": Managing money and financial information) | Confirmed |
| Interests per career | 3 | 3 for all 64 careers | Confirmed |
| Careers with substantive assignment changes | 18 | 18 (section C2 list, and the same 18 found by mapping each draft term through the renames and splits) | Confirmed |
| Provisional careers | 12 | 12 (section C confidence column) | Confirmed |
| Distinct interest combinations | 58 of 64 | 58 of 64 | Confirmed |
| Identical combinations | Remaining pairs among related careers | 6 pairs (section 4 below) | Confirmed |

Arithmetic of the vocabulary: 12 retained + 6 renamed + 4 from splits and replacements + 1 new = 23. With 11 retained the total would be 22.

## 2. Discrepancies found

1. **Retained terms: 12, not 11.** The second review's decision table has 12 "Retain" rows: analysing data and information, researching and investigating, scientific and laboratory work, writing software and building apps, creating visual art and graphics, writing and editing, teaching and training others, caring for people's health, helping and advising people, working with communities, leading people and projects, running and growing a business. The figure 11 in the request for this package does not match the report. This package uses 12.
2. **Renamed terms: "five" in the executive findings, six in the decision table.** Section A, point 1, says five terms "should be renamed". Section B2 has five renames plus one word-order change ("Persuading, presenting and negotiating"). Both statements are true if the word-order change is counted separately. This package counts 6, as the decision table does.
3. **"9 of its 21 terms need work."** Section A lists 5 renames, 3 splits or replacements and 1 missing interest. The missing interest is not one of the 21 terms. Counted from section B2, the 21 first-audit terms split into 12 retained and 9 changed (5 renamed, 1 reordered, 2 split, 1 replaced), so the figure 9 is correct, but the list beside it in section A mixes in the new term and leaves out the reordered one.
4. **Secondary type for science.** The second review's agreement check treated "Scientific and laboratory work" as Investigative with a Realistic secondary type. Section D does not state that secondary link. It has no effect on the result, because every coded career with that interest has an Investigative code.

## 3. Changes in detail

**Vocabulary (21 first-audit terms to 23):**

| Change | First-audit term | Proposed term |
|---|---|---|
| Renamed | working with numbers and models | Working with numbers and calculations |
| Renamed | protecting systems and investigating threats | Keeping computer systems and data safe |
| Renamed | fieldwork and the natural environment | Working outdoors and with the natural environment |
| Renamed (order only) | presenting, persuading and negotiating | Persuading, presenting and negotiating |
| Renamed | organising information, records and processes | Keeping information, records and procedures in order |
| Renamed | interpreting laws, rules and policies | Working with laws, rules and regulations |
| Split | building and maintaining technical systems | Setting up and running computer systems and networks (the equipment part moves to "Working with tools, machines and equipment") |
| Replaced | hands-on and physical work | Working with tools, machines and equipment |
| Split | designing products, spaces and systems | Designing apps, websites and user experiences, and Designing buildings, structures and physical products |
| New | (none) | Managing money and financial information |

The 12 retained terms keep their wording.

**Compared with the current production vocabulary (20 terms):** the current terms mix work activities, domains that repeat category names (business, healthcare, engineering, security), and personal abilities (problem solving, communication, mathematics). The first audit retired those. Neither audit has been applied.

**Careers with a substantive change (18):** C009, C010, C012, C016, C021, C022, C028, C029, C030, C033, C041, C042, C043, C044, C045, C053, C058, C061. The other 46 keep the first audit's draft apart from the renamed and split terms.

Examples of the reasons:
- Medical Laboratory Technologist (C042) and Medical Records Specialist (C043) lose "Caring for people's health", because they do not provide patient care (O*NET IRC and CI).
- Web Developer (C010) loses "Creating visual art and graphics", because O*NET gives CI.
- Financial Analyst (C029), Accountant (C030) and Business Administration Specialist (C061) gain the new money interest.

**Confidence:** 31 High, 21 Medium, 12 Provisional.

**The 12 provisional careers** (no O*NET code): C002 Data Analyst, C003 Machine Learning Engineer, C012 Mobile App Developer, C053 Telecommunications Engineer, C054 Building Engineer, C055 Geotechnical Engineer, C057 Private Law Specialist, C058 Public Law Specialist, C059 Management Information Systems Specialist (MIAGE), C061 Business Administration Specialist, C062 Laboratory Technician, C064 Community Relations Specialist.

## 4. Remaining identical combinations

| Careers | Shared interests | Second review's assessment |
|---|---|---|
| C004 Business Intelligence Analyst, C028 Management Analyst | Analysing, records, business | Identical O*NET code (CIE). Accept |
| C005 Data Engineer, C013 DevOps Engineer | Computer systems, software, records | Both build and run data or delivery pipelines. Accept |
| C006 Statistician, C060 Economist | Numbers, research, analysing | Both IC or ICE. The economist's Enterprising element is not captured. Accept |
| C008 Database Administrator, C020 Network and Systems Administrator | Computer systems, safe, records | Both run and secure infrastructure (CI, CRI). Accept |
| C014 Cloud Engineer, C022 Information Security Engineer | Computer systems, software, safe | Overlapping cloud and security engineering. Accept |
| C047 Mechanical Engineer, C048 Electrical Engineer | Tools, numbers, physical design | Both Realistic-first engineering design. Accept |

The second review also reports 66 same-category pairs that share two of three interests, and treats that as expected. No interest was added only to make a career unique.

## 5. Differences between the first audit and the second review

| Topic | First audit (`skills_interests_audit.md`) | Second review |
|---|---|---|
| Vocabulary size | 21 terms | 23 terms |
| Design | One term, "designing products, spaces and systems", with a suggestion that it "could be split" | Split into a digital design term and a physical design term |
| Technical and hands-on work | "building and maintaining technical systems" and "hands-on and physical work" | Replaced by "Setting up and running computer systems and networks" and "Working with tools, machines and equipment" |
| Money | No money-related term | New term "Managing money and financial information" |
| RIASEC label for software | Realistic / Investigative | Investigative / Conventional (O*NET gives IC or CI for developers and programmers) |
| RIASEC label for system protection | Investigative / Conventional (listed under Investigative) | Conventional primary, Investigative secondary |
| RIASEC label for design | Artistic / Realistic (one term) | Digital design Artistic (secondary Investigative). Physical design Realistic (secondary Artistic) |
| O*NET check | Draft "not checked against O*NET interest profiles" | Checked for the 52 careers with an O*NET code (48 full codes, 4 first type only) |
| Records term | On 16 careers in the draft | On 18 careers |
| Identical pairs | C005/C013, C006/C060, C008/C020, C023/C025, C032/C061, C048/C053 | C004/C028, C005/C013, C006/C060, C008/C020, C014/C022, C047/C048 |
| Selection limit | Recommends a 1 to 5 limit in the form ("Streamlit `max_selections`") | Recommends a soft warning above 5 first, and a hard cap only after a separate experiment |
| Assignments changed against the draft | Not applicable | 18 careers |

Both reports agree on these points:
- interests should describe work activities, not abilities or category names.
- every career should have exactly three interests.
- "communication" stays a skill only.
- the formula should not change.
- any change needs dataset version 1.4.0, a migration of old interest names, and a new separate evaluation, with the frozen data left untouched.

## 6. What the changes would affect if approved later

- The `interests` column of all 64 career records in `data/raw/careers.csv`, including the original 50. IDs, titles, categories and skills would not change.
- The controlled vocabulary `INTERESTS` in `src/data/validation.py`.
- The interest section of the assessment form (descriptions, grouping, selection limit).
- Saved sessions, page links and API input that carry interest names (a migration would be needed).
- Rankings for every profile. A new evaluation would be required. The frozen eval64_v1 and the original 50-career evaluation would stay unchanged.

None of these changes will be made before the lecturer's feedback and the final taxonomy are approved.
