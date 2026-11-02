# Skills and interests audit (catalogue v1.3.0)

Audit date: 2 November 2026. Repository state: commit 593b87e on `main`. **Audit only.** No production data, scoring, recommendation logic or interface file was changed. This document is not committed.

## 1. Summary

The catalogue keeps skills and interests in separate fields, and the skill side is sound. The interest side mixes three different kinds of term in one 20-word list:

- work activities (research, teaching, writing, building software);
- work fields or domains (technology, healthcare, business, environment, science, security), several of which are the career categories under another name;
- personal abilities (problem solving, communication, leadership, organization, mathematics, analysis).

**Main findings:**
1. **One exact duplicate:** "communication" is both a selectable skill and a selectable interest. Five careers list it in both fields, so the same concept counts in the skill share (55% or 15%) and again in the interest share (25%).
2. **The same concept counted twice:** in 40 careers (54 interest-skill pairs), an interest repeats a concept already in that career's skills. For example, "mathematics" with "engineering mathematics" or "statistics" (12 careers), and "design" with "graphic design" or "ui design" (8 careers).
3. **Category names used as interests:** seven of the ten categories have a matching interest term (business, healthcare, engineering, design, security, teaching, building software). Data and AI, Law and Social Sciences have none.
4. **Generic terms that barely separate careers:** "technology" is on 26 of 64 careers. "Organization", "problem solving", "analysis" and "business" are on 14 to 15 each. Only 50 of 64 careers have a distinct interest set: for example, Nurse, Pharmacist, Dietitian and Physical Therapist share an identical set, as do the three teaching careers.
5. **A scoring gap in the interface:** a learner can select all 20 interests. Every career then gets the full 25 interest points, and the ranking becomes exactly the skills-only ranking (verified). Nothing in the form discourages this.
6. **Origin bias:** 12 careers have four interests, 11 of them added in v1.3.0. Each matched interest is worth 6.25 points for them, against 8.3 for three-interest careers, so the new careers are systematically disadvantaged.
7. **Labelling errors:** Mechanical Engineer (C047) has the interest "building software". The term "design" covers both visual design and technical design.

The proposed fix is a 21-term interest taxonomy, written as work activities and grouped under the six Holland (RIASEC) interest types, with exactly three interests per career and no category names or abilities. This needs your approval (section 10) and would change all 64 career records, including the original 50.

## 2. Scope and method

| Task | How it was checked |
|---|---|
| 1 to 2: catalogue, required and preferred skills | All 64 rows of `data/raw/careers.csv`: 144 distinct skills (required and preferred) |
| 3: interest data | Controlled vocabulary `INTERESTS` in `src/data/validation.py` (20 terms) and the `interests` column of every career |
| 4: assessment interface | `pages/1_Career_Assessment.py`, `src/services/profiles.py` |
| 5 to 7: duplicates, abilities as interests | Term-by-term review against the definitions below, plus a scripted check of each career's interests against its own skills |
| 8: missing, inconsistent or generic interests | Frequency of each term, identical interest sets, comparison of similar careers |
| 9: categories as interests | Each category compared with the interest terms, with coverage counted inside and outside the category |
| 10: score effect | `src/engine/scoring.py` read, then direct runs of `recommend()` |

Definitions used (from your brief):
- **Skill:** an ability, knowledge or competency a person has or develops.
- **Interest:** a work activity, professional environment or task a person enjoys and prefers.
- A concept may legitimately appear in both when the meaning differs.

## 3. Current state

### 3.1 Interest vocabulary and use (20 terms, 3 or 4 per career)

| Interest | Careers | Kind of term | Assessment |
|---|---|---|---|
| technology | 26 | Domain | Too broad; on 41% of careers |
| organization | 15 | Ability, ambiguous | Reads as "being organised" or "an organisation" |
| analysis | 14 | Ability or activity | Acceptable only as a work activity ("analysing data") |
| business | 14 | Domain and category name | Duplicates the Business category |
| problem solving | 14 | Ability | Generic; nearly every job involves it |
| mathematics | 13 | Subject or ability | Overlaps the skills "engineering mathematics", "statistics", "linear algebra" |
| helping people | 12 | Activity | Good |
| engineering | 11 | Domain and category name | Duplicates the Engineering category |
| science | 11 | Domain | Broad |
| research | 10 | Activity | Good; legitimately differs from the skill "research methods" |
| building software | 10 | Activity | Good, but used for Mechanical Engineer (C047) |
| design | 10 | Activity, ambiguous | Mixes visual and technical design |
| healthcare | 8 | Domain and category name | Duplicates the Healthcare category |
| communication | 7 | Ability; exact skill duplicate | Also a selectable skill |
| environment | 7 | Work environment | Good as "fieldwork and the natural environment" |
| leadership | 5 | Ability or activity | Acceptable as "leading people and projects" |
| teaching | 5 | Activity, close to a category | Good as an activity |
| security | 4 | Domain, close to a category | Cybersecurity under another name |
| visual arts | 4 | Activity or field | Good as "creating visual art" |
| writing | 4 | Activity | Good; differs from the skills "technical writing" and "content writing" |

### 3.2 Assessment interface

- **Skills:** a multiselect of all 144 catalogue skills, plus a free-text box for other skills (aliases recognised; unknown skills are listed back and not scored).
- **Interests:** a multiselect of the 20 bare terms, labelled "Kinds of work that interest you", with the note "Interests carry 25% of the score". There are no descriptions or examples, no grouping, and no limit on how many can be selected.
- The form never explains the difference between a skill and an interest. "communication" can be picked in both lists.

### 3.3 How interests affect the score

- **Interest value** = matched interests ÷ the number of interests listed for the career, then weighted at 0.25. A three-interest career earns 8.33 points per match; a four-interest career earns 6.25.
- **Learner interest count:** the number of interests the learner selects never reduces the score. Selecting all 20 gives every career the full 25 points (verified: the interest value is 1.0 for all 64 careers, and the full ranking is identical to the skills-only ranking).
- **No interests given:** the component stays applicable and scores 0. It is not re-weighted.
- **One generic interest:** "technology" alone gives points to 26 careers, and the top five are then decided by the career-ID tie-break (all score 13.3).
- **Measured effect** (eval64 sensitivity analysis): interests matter a lot. Without them, NDCG@5 falls from 0.759 to 0.560, and 45% of top-five places are filled on interests and education alone. Normalising for list length (fixed unit or cosine) changed the metrics by 0.011 or less.

## 4. Findings

### F1. Exact duplicate: "communication"

"communication" is a catalogue skill (required or preferred in 24 careers) and an interest (7 careers). Five careers list it in both fields: C033, C035, C037, C038, C064. A learner who selects it in both places is credited twice for one concept.

### F2. The same concept in a career's interests and its skills (54 pairs in 40 careers)

| Interest | Careers where a skill repeats the concept |
|---|---|
| mathematics | C001, C003, C006, C007, C029, C046, C047, C048, C051, C055, C056, C060 (statistics, linear algebra, probability, engineering mathematics) |
| design | C012, C023, C024, C025, C026, C027, C036, C054 (ui design, graphic design, design thinking, product design, instructional design, reinforced concrete design) |
| research | C006, C007, C031, C039, C060, C063 (research methods, market research, qualitative research) |
| leadership | C032, C058, C059, C061, C064 (project management, business management) |
| communication | C033, C035, C037, C038, C064 |
| writing | C034, C057, C058, C063 (content writing, technical writing) |
| building software | C003, C009, C015 (software engineering, object oriented programming, algorithms) |
| security | C017, C018, C022 (network security, security monitoring, security compliance) |
| visual arts | C023, C025, C027 (graphic design, color theory, illustration, animation) |
| teaching | C035, C037, C039 (lesson planning, classroom management, english language teaching) |
| analysis | C028, C029 (business analysis, financial analysis) |

Not every case is an error. "Research" as an interest (enjoying investigation) and "research methods" as a skill (knowing how) legitimately differ. The problem is that the current terms are bare nouns that read as abilities, so learners will often pick them for what they can do rather than what they enjoy.

### F3. Abilities listed as interests

These terms describe what a person can do rather than work they prefer: **problem solving, communication, leadership, organization, mathematics, analysis**.
- "Problem solving" is the clearest case. It is a general competence, it is on 14 careers, and almost any learner would tick it.
- "Analysis", "leadership" and "organization" become legitimate interests only when phrased as activities ("analysing data and information", "leading people and projects", "organising information, records and processes").

### F4. Technical abilities listed as interests

No narrow technical skill (Python, SQL and so on) appears as an interest. The closest cases are "mathematics", which is a school subject and a skill, and "building software", which is acceptable as an activity but overlaps programming skills in C003, C009 and C015.

### F5. Category names used as interests

| Category | Interest used as its name | Category careers carrying it | Missing in category | Used outside the category |
|---|---|---|---|---|
| Business | business | 9 of 10 | C064 | C002, C004, C016, C057, C060 |
| Healthcare | healthcare | 7 of 7 | none | C050 |
| Engineering | engineering | 10 of 11 | C056 | C026 |
| Design | design | 5 of 5 | none | C010, C012, C021, C036, C054 |
| Cybersecurity | security | 4 of 6 | C020, C021 | none |
| Education | teaching | 5 of 5 | none | none |
| Software | building software | 6 of 8 | C011, C016 | C003, C005, C022, C047 |
| Data and AI, Law, Social Sciences | none | not applicable | not applicable | not applicable |

- A learner who picks a category word gets points across that whole category.
- Learners interested in law, society or data have no matching word.
- Law careers rely on "analysis", "writing" and "business", which they share with accountants and analysts.
- The Career Explorer already filters by category, so a domain choice belongs there rather than in the score.

### F6. Missing, inconsistent or generic interest information

| Issue | Careers |
|---|---|
| Wrong interest: "building software" for a mechanical engineer | C047 |
| "design" means visual design here | C023, C024, C025, C026, C027 |
| "design" means technical or structural design here | C010, C012, C021, C036, C054 |
| "organization" with unclear meaning | C004, C005, C008, C011, C014, C020, C021, C025, C030, C032, C043, C054, C059, C061, C062 |
| "technology" as a catch-all (26 careers), including careers that are not technology jobs | C024, C027, C036, C039, C043 among the 26 |
| Four interests instead of three, giving 6.25 instead of 8.33 points per match | C001, C051, C052, C055, C056, C057, C058, C059, C060, C062, C063, C064 |
| No interest expresses law or justice | C057, C058 |
| No interest expresses society or communities | C063, C064 |
| Identical interest sets: interests cannot tell these careers apart | C040 = C041 = C044 = C045; C035 = C037 = C038; C009 = C013 = C015; C008 = C011 = C020; C002 = C028; C005 = C014; C010 = C012; C017 = C018; C032 = C061 |

### F7. Interface

- There are no definitions or examples for skills against interests, and the interests are bare one- or two-word labels.
- There is no limit on how many interests can be chosen, so selecting all 20 removes the effect of interests entirely (section 3.3).
- The same word ("communication") appears in both lists.
- Saved session files and the API carry interest names. A vocabulary change needs a migration (section 10).

## 5. Inconsistencies by career

| ID | Career | Issues |
|---|---|---|
| C001 | Data Scientist | four interests; "mathematics" repeats statistics |
| C002, C004 | Data Analyst, BI Analyst | "business" as domain outside Business; C002 identical to C028 |
| C003 | Machine Learning Engineer | "building software" and "mathematics" repeat skills |
| C005, C014 | Data Engineer, Cloud Engineer | identical interest sets; "organization" ambiguous |
| C006, C007 | Statistician, AI Research Scientist | "mathematics" and "research" repeat skills |
| C008, C011, C020 | DBA, QA Tester, Network Administrator | identical interest sets; "organization" ambiguous |
| C009, C013, C015 | Software Developer, DevOps, Programmer | identical sets; C009 and C015 "building software" repeats programming skills |
| C010, C012 | Web and Mobile Developer | identical sets; "design" means technical design |
| C016 | Computer Systems Analyst | "business" as domain outside Business |
| C017, C018 | Security Analyst, Penetration Tester | identical sets; "security" repeats skills |
| C020, C021 | Network Administrator, Network Architect | in Cybersecurity without the "security" interest |
| C021 | Computer Network Architect | "design" means technical design |
| C022 | Information Security Engineer | "security" repeats skills |
| C023 to C027 | Design careers | "design" and "visual arts" repeat design skills |
| C028, C029 | Management and Financial Analyst | "analysis" repeats analysis skills; C029 "mathematics" repeats statistics |
| C031 | Market Research Analyst | "research" repeats market research |
| C032, C061 | Project Manager, Business Administration | identical sets; "leadership" repeats management skills |
| C033 | Human Resources Specialist | "communication" in both fields |
| C034 | Digital Marketing Specialist | "writing" repeats content writing |
| C035, C037, C038 | Teacher, ESL Teacher, Counselor | identical sets; "communication" in both fields; "teaching" repeats teaching skills |
| C036 | Instructional Designer | "design" repeats instructional design |
| C039 | Computer Science Lecturer | "research" and "teaching" repeat skills |
| C040, C041, C044, C045 | Nurse, Pharmacist, Dietitian, Physical Therapist | identical sets (healthcare, helping people, science) |
| C043 | Medical Records Specialist | "technology" as catch-all |
| C046 to C048, C051, C055 | Engineering careers | "mathematics" repeats engineering mathematics |
| C047 | Mechanical Engineer | "building software" is wrong |
| C050 | Biomedical Engineer | "healthcare" category word outside Healthcare (appropriate in meaning) |
| C051, C052, C055, C056 | Earth-science careers | four interests |
| C054 | Building Engineer | "design" repeats reinforced concrete design |
| C056 | Geophysicist | four interests; "mathematics" repeats linear algebra |
| C057, C058 | Law careers | four interests; no law-related interest; "writing" repeats technical writing; C058 "leadership" repeats project management |
| C059 | MIAGE | four interests; "leadership" repeats project management |
| C060 | Economist | four interests; "mathematics" and "research" repeat skills; "business" outside Business |
| C062 | Laboratory Technician | four interests |
| C063 | Sociologist | four interests; "research" and "writing" repeat skills; no communities interest |
| C064 | Community Relations | four interests; "communication" in both fields; "leadership" repeats project management |

## 6. Proposed interest taxonomy (21 terms)

**Design rules:**
- Every term describes work a person enjoys doing, or a work setting.
- No term is a catalogue skill, a career category or a personal ability.
- Terms are grouped by the six Holland (RIASEC) types that O*NET uses for occupational interests, so they can later be checked against O*NET interest profiles for the 52 careers with an O*NET code.
- Each career gets exactly three.

| Group | Proposed interest | Short description for the form | Not to be confused with (skill) |
|---|---|---|---|
| Investigative | analysing data and information | Finding patterns and answers in data, figures or documents | statistics, data visualization |
| Investigative | researching and investigating | Asking questions and finding out how things work | research methods |
| Investigative | working with numbers and models | Calculations, formulas and quantitative models | engineering mathematics, statistics |
| Investigative | scientific and laboratory work | Experiments, samples and scientific methods | chemistry, laboratory techniques |
| Investigative / Conventional | protecting systems and investigating threats | Keeping systems and data safe, tracing incidents | network security |
| Realistic | building and maintaining technical systems | Setting up, running and fixing networks, servers and equipment | linux, networking |
| Realistic | hands-on and physical work | Working with your hands, tools, machines, structures or the body | cad, patient care |
| Realistic | fieldwork and the natural environment | Working outdoors, on sites, with land, water or ecosystems | geology, environmental science |
| Realistic / Investigative | writing software and building apps | Creating programs, apps and digital products | python, java |
| Artistic | creating visual art and graphics | Drawing, illustration, animation, visual style | graphic design, illustration |
| Artistic / Realistic | designing products, spaces and systems | Shaping how a product, building, interface or system works | ui design, product design |
| Artistic | writing and editing | Producing clear texts, stories or arguments | technical writing, content writing |
| Social | teaching and training others | Explaining, coaching and helping people learn | lesson planning |
| Social | caring for people's health | Supporting patients and people's wellbeing | patient care, pharmacology |
| Social | helping and advising people | Listening, guiding and supporting individuals | counseling |
| Social | working with communities | Engaging groups, communities and the public | community development |
| Enterprising | leading people and projects | Taking charge, coordinating teams and deadlines | project management |
| Enterprising | running and growing a business | Commercial decisions, customers, markets and profit | business management |
| Enterprising | presenting, persuading and negotiating | Pitching ideas, convincing others, reaching agreements | communication |
| Conventional | organising information, records and processes | Keeping data, files and procedures accurate and orderly | data modeling, medical coding |
| Conventional | interpreting laws, rules and policies | Applying regulations, standards and legal texts | contract law, taxation |

**Retired as interests:**
- "problem solving", "communication" and "mathematics" are abilities or skills.
- "technology", "business", "healthcare", "engineering", "science" and "security" are domains or category names.
- Their meaning moves into activity terms (section 7) or into the category filter.

## 7. Mapping from existing to proposed interests

| Existing | Proposed | Rule |
|---|---|---|
| analysis | analysing data and information | Default. For law careers use interpreting laws, rules and policies; for forensics use protecting systems and investigating threats |
| building software | writing software and building apps | Default. C047 Mechanical Engineer: drop (error), use hands-on and physical work |
| business | running and growing a business | Commercial careers only. Remove where it only names the domain (C002, C016, C057, C060) |
| communication | presenting, persuading and negotiating | Only where the job centres on persuading or presenting (C023, C034, C064). Otherwise drop, because "communication" stays a skill |
| design | creating visual art and graphics, or designing products, spaces and systems | Visual meaning (C023, C025, C027) or product, technical and structural meaning (C010, C012, C021, C024, C026, C036, C054) |
| engineering | designing products, spaces and systems; building and maintaining technical systems; hands-on and physical work; fieldwork and the natural environment | By the career's real work; the category word is retired |
| environment | fieldwork and the natural environment | Direct |
| healthcare | caring for people's health | Direct; the category word is retired |
| helping people | helping and advising people | Default. Health careers use caring for people's health; community careers use working with communities |
| leadership | leading people and projects | Direct |
| mathematics | working with numbers and models | Direct (activity, not subject) |
| organization | organising information, records and processes | Direct |
| problem solving | (retired) | Replaced by the career-specific activity: analysing, investigating, protecting or building systems |
| research | researching and investigating | Direct |
| science | scientific and laboratory work | Direct |
| security | protecting systems and investigating threats | Direct; also added to C020 and C021 |
| teaching | teaching and training others | Direct |
| technology | (retired) | Replaced by writing software, building and maintaining technical systems, analysing data, or dropped for careers that are not technology jobs |
| visual arts | creating visual art and graphics | Direct |
| writing | writing and editing | Direct |
| (new) | interpreting laws, rules and policies | Law careers, accountancy, HR, records, forensics |
| (new) | working with communities | Sociologist, community relations, school counselor |

## 8. Effect of the draft assignments (appendix)

The appendix gives a draft set of three proposed interests for every career. It is the author's judgement, not checked against O*NET interest profiles.

| Measure | Current | Draft |
|---|---|---|
| Interest terms | 20 | 21 |
| Interests per career | 3 (52 careers) or 4 (12) | 3 for all 64 |
| Most frequent term | technology, 26 careers | designing products, spaces and systems, 18 careers |
| Distinct interest sets | 50 of 64 | 58 of 64 |
| Groups of careers with identical sets | 9 | 6 pairs (C005 and C013, C006 and C060, C008 and C020, C023 and C025, C032 and C061, C048 and C053) |
| Category words used as interests | 7 | 0 |
| Exact skill duplicates | 1 (communication) | 0 |

"Designing products, spaces and systems" is still broad (18 careers). It could be split into "designing digital products" and "designing buildings and physical products" if you want more separation.

## 9. Recommendations for the assessment interface

1. **Explain the difference** above the two sections: "Skills: what you can already do or know" and "Interests: the kinds of work you enjoy, even if you have not learned the skills yet". Give one example of each.
2. **Show interests as described choices** grouped under the six types, each with its one-line description (section 6), instead of a bare word list.
3. **Limit the selection to between 1 and 5 interests** (Streamlit `max_selections`), with the hint "Pick the ones you enjoy most". This removes the select-all loophole without touching the formula.
4. **Remove "communication" from interests.** It stays a skill; persuading and presenting become an interest.
5. **Warn on overlap.** If a learner picks an interest that mirrors one of their selected skills, show a note that interests are about enjoyment and do not have to match skills.
6. **Keep domains out of the score.** Point learners to the Career Explorer category filter for fields such as healthcare or law.
7. **Show the interest contribution** on each recommendation with the matched interest names (already partly shown), so learners see why a career appeared.
8. **Accept old interest names** when a saved session or link is loaded, mapping them with section 7, and tell the learner if a saved interest was replaced.

## 10. Changes requiring your approval

| # | Change | Files affected | Impact |
|---|---|---|---|
| A1 | Adopt the 21-term taxonomy (section 6) as the controlled interest vocabulary | `src/data/validation.py` (INTERESTS), `docs/dataset_documentation.md` | Dataset becomes v1.4.0 |
| A2 | Re-assign interests for all 64 careers, three each, starting from the appendix draft | `data/raw/careers.csv` (interests column only) | **Changes interest data of the original 50 career records** (their skills, titles, categories and IDs stay). The frozen evaluation snapshots keep the old data |
| A3 | Optionally check each career's assignment against its O*NET interest profile (52 careers) before finalising | Research note | No fabricated values; careers without O*NET stay author-judged |
| A4 | Interface changes in section 9 (definitions, grouped and described interests, 1 to 5 limit, no "communication" interest, overlap note) | `pages/1_Career_Assessment.py`, `src/ui/*` | No formula change; changes what learners can enter |
| A5 | Migration of old interest names in saved sessions, page links and API input | `src/services/profiles.py`, `docs/integration_api.md` | Old inputs keep working; affects T-Career integration |
| A6 | Update tests and documents that use old interest terms | `tests/conftest.py`, `tests/test_profiles.py`, `tests/test_african_expansion.py`, `docs/requirements.md`, `docs/dataset_documentation.md` | Test expectations change with the data |
| A7 | Evaluation follow-up: the eval64 profiles use the old vocabulary. After A1 and A2, run a new, separate evaluation (for example eval64_v2) with profiles mapped through section 7 | New files only | eval64_v1, the original 50-career study and all saved reports stay frozen and unchanged |
| A8 | Out of scope now, listed for later: whether the score should normalise for the number of interests a learner selects | Separate experiment only | Formula unchanged in this work |

Recommended order: A1 and A2 together with A6, then A4 and A5, then A7. A3 can run before A2 if you want the assignments checked against O*NET first.

## Appendix: draft interests per career

Draft for review, not applied. Current interests are from `data/raw/careers.csv` (v1.3.0).

| ID | Career | Category | Current interests | Proposed interests (draft) |
|---|---|---|---|---|
| C001 | Data Scientist | Data and AI | analysis, mathematics, research, technology | analysing data and information; writing software and building apps; working with numbers and models |
| C002 | Data Analyst | Data and AI | analysis, business, problem solving | analysing data and information; organising information, records and processes; presenting, persuading and negotiating |
| C003 | Machine Learning Engineer | Data and AI | technology, building software, mathematics | writing software and building apps; building and maintaining technical systems; working with numbers and models |
| C004 | Business Intelligence Analyst | Data and AI | analysis, business, organization | analysing data and information; organising information, records and processes; running and growing a business |
| C005 | Data Engineer | Data and AI | technology, building software, organization | building and maintaining technical systems; writing software and building apps; organising information, records and processes |
| C006 | Statistician | Data and AI | mathematics, research, analysis | working with numbers and models; researching and investigating; analysing data and information |
| C007 | AI Research Scientist | Data and AI | research, mathematics, technology | researching and investigating; working with numbers and models; writing software and building apps |
| C008 | Database Administrator | Data and AI | technology, organization, problem solving | building and maintaining technical systems; organising information, records and processes; protecting systems and investigating threats |
| C009 | Software Developer | Software | building software, technology, problem solving | writing software and building apps; building and maintaining technical systems; researching and investigating |
| C010 | Web Developer | Software | building software, design, technology | writing software and building apps; designing products, spaces and systems; creating visual art and graphics |
| C011 | Software Quality Assurance Tester | Software | technology, problem solving, organization | organising information, records and processes; building and maintaining technical systems; researching and investigating |
| C012 | Mobile App Developer | Software | building software, design, technology | writing software and building apps; designing products, spaces and systems; building and maintaining technical systems |
| C013 | DevOps Engineer | Software | technology, building software, problem solving | building and maintaining technical systems; writing software and building apps; organising information, records and processes |
| C014 | Cloud Engineer | Software | technology, building software, organization | building and maintaining technical systems; writing software and building apps; protecting systems and investigating threats |
| C015 | Computer Programmer | Software | building software, problem solving, technology | writing software and building apps; working with numbers and models; organising information, records and processes |
| C016 | Computer Systems Analyst | Software | business, technology, problem solving | analysing data and information; designing products, spaces and systems; running and growing a business |
| C017 | Information Security Analyst | Cybersecurity | security, technology, problem solving | protecting systems and investigating threats; analysing data and information; researching and investigating |
| C018 | Penetration Tester | Cybersecurity | security, problem solving, technology | protecting systems and investigating threats; researching and investigating; writing software and building apps |
| C019 | Digital Forensics Analyst | Cybersecurity | security, research, analysis | protecting systems and investigating threats; researching and investigating; interpreting laws, rules and policies |
| C020 | Network and Systems Administrator | Cybersecurity | technology, organization, problem solving | building and maintaining technical systems; protecting systems and investigating threats; organising information, records and processes |
| C021 | Computer Network Architect | Cybersecurity | technology, design, organization | designing products, spaces and systems; building and maintaining technical systems; protecting systems and investigating threats |
| C022 | Information Security Engineer | Cybersecurity | security, technology, building software | protecting systems and investigating threats; writing software and building apps; designing products, spaces and systems |
| C023 | Graphic Designer | Design | design, visual arts, communication | creating visual art and graphics; presenting, persuading and negotiating; designing products, spaces and systems |
| C024 | UX Designer | Design | design, helping people, technology | designing products, spaces and systems; researching and investigating; helping and advising people |
| C025 | Interior Designer | Design | design, visual arts, organization | creating visual art and graphics; designing products, spaces and systems; presenting, persuading and negotiating |
| C026 | Industrial Designer | Design | design, engineering, visual arts | designing products, spaces and systems; hands-on and physical work; creating visual art and graphics |
| C027 | Animator | Design | visual arts, design, technology | creating visual art and graphics; writing and editing; designing products, spaces and systems |
| C028 | Management Analyst | Business | business, problem solving, analysis | analysing data and information; running and growing a business; presenting, persuading and negotiating |
| C029 | Financial Analyst | Business | business, mathematics, analysis | working with numbers and models; analysing data and information; running and growing a business |
| C030 | Accountant | Business | business, organization, mathematics | working with numbers and models; organising information, records and processes; interpreting laws, rules and policies |
| C031 | Market Research Analyst | Business | business, research, analysis | researching and investigating; analysing data and information; running and growing a business |
| C032 | Project Manager | Business | leadership, organization, business | leading people and projects; organising information, records and processes; running and growing a business |
| C033 | Human Resources Specialist | Business | helping people, business, communication | helping and advising people; organising information, records and processes; interpreting laws, rules and policies |
| C034 | Digital Marketing Specialist | Business | business, communication, writing | presenting, persuading and negotiating; writing and editing; analysing data and information |
| C035 | Secondary School Teacher | Education | teaching, helping people, communication | teaching and training others; helping and advising people; presenting, persuading and negotiating |
| C036 | Instructional Designer | Education | teaching, design, technology | teaching and training others; designing products, spaces and systems; writing and editing |
| C037 | English as a Second Language Teacher | Education | teaching, helping people, communication | teaching and training others; helping and advising people; writing and editing |
| C038 | School Counselor | Education | helping people, teaching, communication | helping and advising people; teaching and training others; working with communities |
| C039 | Computer Science Lecturer | Education | teaching, technology, research | teaching and training others; researching and investigating; writing software and building apps |
| C040 | Registered Nurse | Healthcare | healthcare, helping people, science | caring for people's health; helping and advising people; organising information, records and processes |
| C041 | Pharmacist | Healthcare | healthcare, science, helping people | caring for people's health; scientific and laboratory work; helping and advising people |
| C042 | Medical Laboratory Technologist | Healthcare | science, healthcare, analysis | scientific and laboratory work; analysing data and information; caring for people's health |
| C043 | Medical Records Specialist | Healthcare | healthcare, organization, technology | organising information, records and processes; caring for people's health; interpreting laws, rules and policies |
| C044 | Dietitian and Nutritionist | Healthcare | healthcare, helping people, science | caring for people's health; helping and advising people; teaching and training others |
| C045 | Physical Therapist | Healthcare | healthcare, helping people, science | caring for people's health; hands-on and physical work; helping and advising people |
| C046 | Civil Engineer | Engineering | engineering, mathematics, environment | designing products, spaces and systems; fieldwork and the natural environment; working with numbers and models |
| C047 | Mechanical Engineer | Engineering | engineering, mathematics, building software | designing products, spaces and systems; hands-on and physical work; working with numbers and models |
| C048 | Electrical Engineer | Engineering | engineering, mathematics, technology | building and maintaining technical systems; working with numbers and models; designing products, spaces and systems |
| C049 | Environmental Engineer | Engineering | environment, engineering, science | fieldwork and the natural environment; scientific and laboratory work; designing products, spaces and systems |
| C050 | Biomedical Engineer | Engineering | engineering, healthcare, science | designing products, spaces and systems; caring for people's health; scientific and laboratory work |
| C051 | Mining Engineer | Engineering | engineering, environment, mathematics, problem solving | fieldwork and the natural environment; hands-on and physical work; working with numbers and models |
| C052 | Geological Engineer | Engineering | engineering, science, environment, research | fieldwork and the natural environment; scientific and laboratory work; researching and investigating |
| C053 | Telecommunications Engineer | Engineering | engineering, technology, problem solving | building and maintaining technical systems; designing products, spaces and systems; working with numbers and models |
| C054 | Building Engineer | Engineering | engineering, design, organization | designing products, spaces and systems; hands-on and physical work; leading people and projects |
| C055 | Geotechnical Engineer | Engineering | engineering, science, environment, mathematics | fieldwork and the natural environment; scientific and laboratory work; working with numbers and models |
| C056 | Geophysicist | Engineering | science, research, mathematics, environment | researching and investigating; working with numbers and models; fieldwork and the natural environment |
| C057 | Private Law Specialist | Law | analysis, writing, business, problem solving | interpreting laws, rules and policies; writing and editing; presenting, persuading and negotiating |
| C058 | Public Law Specialist | Law | analysis, writing, leadership, helping people | interpreting laws, rules and policies; writing and editing; helping and advising people |
| C059 | Management Information Systems Specialist (MIAGE) | Business | technology, business, organization, leadership | organising information, records and processes; building and maintaining technical systems; leading people and projects |
| C060 | Economist | Social Sciences | analysis, mathematics, research, business | analysing data and information; working with numbers and models; researching and investigating |
| C061 | Business Administration Specialist | Business | business, leadership, organization | running and growing a business; leading people and projects; organising information, records and processes |
| C062 | Laboratory Technician | Healthcare | science, analysis, organization, healthcare | scientific and laboratory work; organising information, records and processes; hands-on and physical work |
| C063 | Sociologist | Social Sciences | research, helping people, writing, analysis | researching and investigating; working with communities; writing and editing |
| C064 | Community Relations Specialist | Business | communication, helping people, leadership, environment | working with communities; presenting, persuading and negotiating; fieldwork and the natural environment |
