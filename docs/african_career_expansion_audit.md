# African career expansion audit (Phase 8, audit only)

Audit date: 1 November 2026. Repository state: commit c71b445 on `main`. No dataset, code, test or evaluation file was changed. This report is the only new file, and it is not committed.

**How to read this report.** Each statement is marked as one of:

- **[Sourced]**: taken from a cited source.
- **[Repo]**: checked in this repository's code or data.
- **[Proposal]**: my recommendation or estimate. Not sourced, and needs your or the lecturer's review.

## A. Executive summary

1. **Not all 17 requested titles can be added as new careers.** Three already exist in the catalogue: Civil Engineer (C046), Electrical Engineer (C048) and Human Resources Specialist (C033) **[Repo]**. The validator rejects duplicate titles, so they would fail the data check (`validate_careers`, "duplicate or near-duplicate title") **[Repo]**. The realistic target is **64 careers (50 + 14)**, not 67.
2. **Of the 14 distinct additions:**
   - 7 can be added largely as requested: Mining Engineer, Telecommunications Engineer, Geotechnical Engineer, Geophysicist, Economist, Sociologist and Community Relations Specialist.
   - 6 need refinement first, because the title is a degree name, a country-specific term or overlaps an existing career: Building Engineer, Private Law Specialist, Public Law Specialist, Management Information Systems Specialist (MIAGE), Business Administration Specialist and Laboratory Technician.
   - Geological Engineer needs further research. O*NET combines it with mining engineering in one occupation **[Sourced]**, and it overlaps heavily with Geotechnical Engineer.
3. **The scoring engine supports new careers without any change to the scoring code.** Matching, scoring, ranking, skill gaps and resource lookup are all driven by the CSV files **[Repo]**.
4. **The data files, counts and supporting code do need changes:**
   - The expected count of 50 is hard-coded.
   - The category list is fixed at 8.
   - The Analytics chart colours are defined for exactly 8 categories, so a ninth category would crash the page.
   - Every new skill must have a learning resource.
   - Several tests check counts of 50 careers, 114 skills and 1,800 pairs.
5. **The proposed skill lists need 44 new skills** (114 rising to 158), and so **44 new learning resources**, one per skill as the validator requires. They reuse 23 existing skills. In this audit I found a free candidate resource for 22 of the 44 skills; two of those (physics, signal processing) are known open titles I did not search. 22 still need research.
6. **Existing evaluation results must not be presented as covering the new careers.** The 36 labelled profiles were labelled against the 50 current careers only. The saved results are tied to those 50, and all four reproducibility checks would fail once careers are added. Section G explains this.
7. **Categories:** the least disruptive honest option is to keep the 8 categories and add 2, Law and Social Sciences, following the ILO ISCO-08 groupings. That gives 10 categories. Section 6 sets out the options.

## B. Career-by-career assessment

Column notes:

- Skills, interests and education levels are all **[Proposal]**.
- The education scale is the repository's 0 to 4 scale **[Repo]**: 2 means certificate or diploma, 3 a bachelor's degree, 4 a master's degree or higher.
- "Source" is the evidence for the occupation itself, not for my skill lists.

| # | Proposed title | Category | Overlap with existing careers | Required skills | Preferred skills | Education | Source availability | Resource availability | Recommendation |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Mining Engineer | Engineering | Low. Shares engineering mathematics and CAD with other engineers | mine planning, rock mechanics, mine safety, engineering mathematics | mineral processing, cad, gis, project management | 3 | Supported: O*NET 17-2151.00; ISCO-08 2146 | Partial: mine safety has an ILO code; mine planning, mineral processing and rock mechanics need research | **Add** |
| 2 | Geological Engineer | Engineering | High with #1 (same O*NET code) and #7 | geology, engineering geology, rock mechanics, gis | soil mechanics, geophysical methods, technical writing | 3 | Partial: no separate O*NET occupation | Partial: geology yes; engineering geology needs research | **Research further**; merge candidate |
| 3 | Telecommunications Engineer | Engineering | Medium with Computer Network Architect (C021) and Network and Systems Administrator (C020) | telecommunication systems, signal processing, networking, radio frequency engineering | fiber optics, engineering mathematics, project management | 3 | Supported: O*NET 15-1241.01; ISCO-08 2153 | Partial: MIT and ITU candidates; fiber optics needs research | **Add**, focused on transmission and radio |
| 4 | Civil Engineer | Engineering | **Exists as C046** | (existing) | (existing) | (existing) | Supported: O*NET 17-2051.00 | Existing | **Merge**: keep C046 |
| 5 | Building Engineer, refined to **Building Construction Engineer** | Engineering | High with Civil Engineer (C046) and Project Manager (C032) | construction management, structural analysis, cad, building codes | reinforced concrete design, quantity surveying, project management | 3 | Partial: ESCO "construction engineer", mapped to ISCO-08 2142 | Weak: building codes are national; others need research | **Refine** |
| 6 | Electrical Engineer | Engineering | **Exists as C048** | (existing) | (existing) | (existing) | Supported: O*NET 17-2071.00 | Existing | **Merge**: keep C048; consider a separate power or energy role later |
| 7 | Geotechnical Engineer | Engineering | Medium with Civil Engineer (C046); high with #2 | soil mechanics, rock mechanics, foundation design, engineering mathematics | geology, cad, gis | 3 | Partial: no separate O*NET occupation; ESCO "mining geotechnical engineer" under ISCO-08 2142; Australia's ANZSCO 233212 | Partial: MIT soil mechanics (advanced level); foundation design needs research | **Add**, as a civil engineering specialisation |
| 8 | Geophysicist | Engineering (see Section 6) | Low | geophysical methods, geology, physics, python | signal processing, gis, linear algebra | 3 (master's common) | Supported: O*NET 19-2042.00 lists "Project Geophysicist"; ISCO-08 2114 | Good: UBC geophysics resource, open geology textbook, OpenStax physics | **Add** |
| 9 | Private Law Specialist | Law (new) | None | legal research, legal writing, contract law, commercial law | ohada business law, labour law, communication | 4 | Partial: O*NET 23-1011.00 Lawyers and ISCO-08 2611 cover lawyers, not "private law" | Weak: free legal content is country-specific | **Refine**, for example as "Legal Officer, Private and Business Law" |
| 10 | Public Law Specialist | Law (new) | Low with #9 | legal research, legal writing, constitutional law, administrative law | public finance, public procurement, communication | 4 | Partial, as #9 | Weak, as #9 | **Refine**, for example as "Legal Officer, Public Law and Administration" |
| 11 | Human Resources Specialist | Business | **Exists as C033** | (existing) | (existing) | (existing) | Supported: O*NET 13-1071.00 | Existing | **Merge**: keep C033 |
| 12 | MIS Specialist (MIAGE), refined to **Information Systems Manager** | Business | High with Computer Systems Analyst (C016); medium with BI Analyst (C004) and Project Manager (C032) | information systems management, business analysis, project management, sql | erp systems, data modeling, it governance | 4 | Partial: MIAGE is a French degree, not an occupation; closest O*NET is 11-3021.00 | Partial: ERP vendor course; IT governance needs research | **Refine** |
| 13 | Economist | Social Sciences (new) | Low with Financial Analyst (C029) and Statistician (C006) | economics, econometrics, statistics, research methods | python, r programming, data visualization | 4 | Supported: O*NET 19-3011.00; ISCO-08 2631 | Good: OpenStax economics; free econometrics book | **Add** |
| 14 | Business Administration Specialist, refined to **Operations Manager** | Business | High with Management Analyst (C028), Project Manager (C032), Accountant (C030) and HR (C033) | operations management, business management, accounting, communication | excel, project management, human resource management | 3 | Not sufficiently defined: "business administration" is a degree field. O*NET 11-1021.00 is only a candidate | Partial: OpenStax management; operations management needs research | **Refine**, after the lecturer confirms the intended job |
| 15 | Laboratory Technician, refined to **Chemical Laboratory Technician** | Engineering (see Section 6) | High with Medical Laboratory Technologist (C042) if medical | laboratory techniques, chemistry, laboratory safety, quality control | sample preparation, statistics, technical writing | 2 | Supported for the refined title: O*NET 19-4031.00; ISCO-08 3111 | Partial: WHO manuals fit biological and clinical labs better than chemical labs | **Refine**: confirm medical or chemical/industrial first |
| 16 | Sociologist | Social Sciences (new) | Low | sociology, research methods, qualitative research, survey design | statistics, r programming, technical writing | 4 | Supported: O*NET 19-3041.00; ISCO-08 2632 | Good: OpenStax sociology; open qualitative methods text | **Add** |
| 17 | Community Relations Specialist | Business | Low; some with Market Research Analyst (C031) on survey design | stakeholder engagement, communication, community development, conflict resolution | social impact assessment, project management, survey design | 3 | Partial: O*NET 27-3031.00 Public Relations Specialists; ISCO-08 2432 | Partial: IFC handbook and IAIA guidance; community development and conflict resolution need research | **Add**, defined as community relations for mining and infrastructure projects |

Every career keeps 3 or 4 required skills, matching the existing 3 to 5 **[Repo]**. No skill appears as both required and preferred in the same career, which the validator also rejects **[Repo]**.

### Proposed interests (controlled vocabulary only) [Proposal]

| Career | Interests |
|---|---|
| Mining Engineer | engineering, environment, mathematics, problem solving |
| Geological Engineer | engineering, science, environment, research |
| Telecommunications Engineer | engineering, technology, problem solving |
| Building Construction Engineer | engineering, design, organization |
| Geotechnical Engineer | engineering, science, environment, mathematics |
| Geophysicist | science, research, mathematics, environment |
| Private and Public Law | analysis, writing, problem solving; plus business (private) or leadership and helping people (public) |
| Information Systems Manager | technology, business, organization, leadership |
| Economist | analysis, mathematics, research, business |
| Operations Manager | business, leadership, organization |
| Chemical Laboratory Technician | science, analysis, organization |
| Sociologist | research, helping people, writing, analysis |
| Community Relations Specialist | communication, helping people, leadership, environment |

The 20-term interest vocabulary has no "law" or "society" term **[Repo]**. Law careers can still be matched through general interests. Adding new interest terms is optional, but it changes the assessment form.

### Notes on the hard cases

**Private Law and Public Law Specialists.**

- "Droit privé" and "droit public" are the two main tracks of law degrees in French-tradition systems, including Guinea, which follows the civil-law tradition **[Proposal; needs a cited source before implementation]**.
  - Private law covers civil, commercial, labour and family law.
  - Public law covers constitutional, administrative, public finance and international law.
- These are specialisations within one occupation (Lawyers, O*NET 23-1011.00; ISCO-08 2611 Legal professionals), not separate occupations.
- The practising professions (advocate, notary, magistrate, in-house legal officer) each have their own national admission rules: a bar examination, a magistrates' school or a notarial qualification.
  - Examples to verify per country, not checked in this audit: the Nigerian Law School and call to the bar, the Kenya School of Law Advocates Training Programme, the Ghana School of Law, and admission as an attorney or advocate in South Africa.
  - The 0 to 4 education scale cannot represent licensing, so the app must not imply that a degree alone qualifies someone to practise.
- **OHADA** (Organisation for the Harmonization of Business Law in Africa) publishes uniform business-law acts that apply in its member states, including Guinea **[Sourced: [OHADA](https://en.wikipedia.org/wiki/OHADA), [ohada.org](https://www.ohada.org/en/?p=38677)]**. That makes "ohada business law" a relevant skill for francophone West and Central Africa, but not for Nigeria, Ghana, Kenya or South Africa.

**MIAGE.**

- MIAGE (Méthodes Informatiques Appliquées à la Gestion des Entreprises) is a French university degree that mixes computing and management **[Sourced: [Université Paris-Saclay](https://www.universite-paris-saclay.fr/formation/master/methodes-informatiques-appliquees-la-gestion-des-entreprises-miage)]**.
  - At Paris-Saclay its teaching is about 25% computing, 20% information-systems engineering and management, and 20% management of organisations.
  - Its listed target jobs include information-systems project manager, information-systems consultant or auditor, business-intelligence engineer, data analyst and database administrator.
- So MIAGE is a training route into several existing careers (C016, C004, C008, C032), not one occupation.
- "Management Information Systems", "IS management", "business analysis" and "IT management" overlap but are not identical.
- Recommendation: add one management-level career (Information Systems Manager, closest O*NET 11-3021.00) and record "MIAGE" as a training-route note or alias, not as the job title. The O*NET occupation usually requires work experience **[Proposal; not verified in this audit]**.

**Building Engineer.**

- The title changes meaning by country **[Sourced: [Wikipedia, Building engineer](https://en.wikipedia.org/wiki/Building_engineer)]**:
  - UK: a chartered profession (CABE) covering design, compliance and maintenance of buildings.
  - United States and Australia: architectural engineering or building services.
  - Nigeria: commonly known as "builder".
- Many US job adverts use "building engineer" for facility maintenance **[Proposal, from search listings; not a formal source]**.
- ESCO's "construction engineer" (ISCO-08 2142, Civil Engineers) is the closest international definition **[Sourced: [ESCO via World of Taxonomy](https://worldoftaxonomy.com/codes/esco_occupations/2a914d26-42aa-46b5-acf3-097d51ba4617)]**.
- In francophone Africa "ingénieur bâtiment" usually means building-focused civil and construction engineering **[Proposal]**.
- Recommendation: use "Building Construction Engineer", focused on building construction, codes and site management, as distinct from Civil Engineer (C046), which centres on structural analysis and wider infrastructure.

**Geological Engineer vs Mining vs Geotechnical.**

- O*NET's single occupation 17-2151.00 is "Mining and Geological Engineers, Including Mining Safety Engineers" **[Sourced: [O*NET](https://www.onetonline.org/link/summary/17-2151.00)]**.
  - Its reported job titles are mining, planning, project and safety engineers.
  - It is Job Zone Four, with 79% of new hires needing a bachelor's degree.
- ESCO places "mining geotechnical engineer" under ISCO-08 2142 **[Sourced: [ESCO via World of Taxonomy](https://worldoftaxonomy.com/codes/esco_occupations/efc75d4e-dfbf-4178-929c-0ae198801c36)]**.
- Adding all three risks near-duplicate careers with the same skills: rock mechanics, geology and soil mechanics.
- Recommendation: add Mining and Geotechnical first. Keep Geological Engineer only if the lecturer confirms a distinct local role, such as engineering geology and site investigation.

**Laboratory Technician.**

- The catalogue already has Medical Laboratory Technologist (C042, Healthcare) **[Repo]**.
- A chemical or industrial laboratory technician (mining assay labs, water and quality control; O*NET 19-4031.00 Chemical Technicians) is distinct. It is relevant to mining economies such as Guinea's **[Proposal]**.
- A medical laboratory technician would be a lower-education variant of C042 and would score almost identically to it.

## African employment relevance [Proposal unless cited]

- **Mining and geology:**
  - Guinea's bauxite exports rose to about 183 million tonnes in 2025 **[Sourced: [China Global South](https://chinaglobalsouth.com/2026/01/26/guinea-bauxite-exports-china-2025/), [Engineering News](https://www.engineeringnews.co.za/article/guineas-bauxite-exports-jump-25-to-183-million-tons-in-2025-on-chinese-demand-2026-01-26)]**.
  - The Simandou iron-ore project began output in late 2025 **[Sourced: [Mining.com](https://www.mining.com/web/mass-layoffs-overshadow-guineas-simandou-mega-mine-as-output-accelerates/)]**. The same reports describe mass layoffs once construction ended, so demand is cyclical.
  - Mining, geotechnical, geophysics, chemical laboratory and community relations roles are linked to this sector.
- **Community relations:** mining and infrastructure financed by development lenders follow stakeholder-engagement and social-impact practice such as IFC guidance. This creates "community relations" and "social performance" roles.
- **Construction, telecoms and energy:** infrastructure, mobile-network expansion and electrification are broad regional themes. I found no country-level employment data in this audit, so these should not be stated as quantified demand.
- **Law and public administration:** relevance is high, but content is national. OHADA applies only in its member states.
- **Regional limits of resources:** most free resources found are from the US, Canada, the UK or international bodies. ILO, WHO, IFC, IAIA, ITU and OHADA material is international or Africa-relevant. OpenStax and MIT examples are US-centred.

## C. Skills impact

44 new canonical skills would be needed [Proposal; counted by script from the lists in Section B]:

- **Engineering and earth sciences (18):** building codes, construction management, engineering geology, fiber optics, foundation design, geology, geophysical methods, mine planning, mine safety, mineral processing, physics, quantity surveying, radio frequency engineering, reinforced concrete design, rock mechanics, signal processing, soil mechanics, telecommunication systems.
- **Law (9):** administrative law, commercial law, constitutional law, contract law, labour law, legal research, legal writing, ohada business law, public procurement.
- **Business, IS and social sciences (17):**
  - Business and IS: business management, erp systems, information systems management, it governance, operations management, public finance.
  - Economics and sociology: econometrics, economics, qualitative research, sociology.
  - Laboratory: laboratory safety, quality control, sample preparation.
  - Community relations: community development, conflict resolution, social impact assessment, stakeholder engagement.

23 existing skills are reused [Repo]: accounting, business analysis, cad, chemistry, communication, data modeling, data visualization, engineering mathematics, excel, gis, human resource management, laboratory techniques, linear algebra, networking, project management, python, r programming, research methods, sql, statistics, structural analysis, survey design, technical writing.

### Aliases to consider [Proposal]

| Type | Aliases |
|---|---|
| English | geomechanics → rock mechanics; rf engineering → radio frequency engineering; telecoms → telecommunication systems; erp → erp systems; mis → information systems management; stakeholder management → stakeholder engagement; sia → social impact assessment; ohada law → ohada business law; employment law → labour law; labor law → labour law |
| French, for Guinea | géologie → geology; mécanique des sols → soil mechanics; droit des affaires → commercial law; droit administratif → administrative law; droit constitutionnel → constitutional law |

None of these clashes with an existing alias or canonical skill [Repo, checked by script].

Two cautions on aliases:

- "quality assurance" must not become an alias for quality control, because it already means software QA in the catalogue.
- **French input needs a code fix.** `clean_skill_text` drops accented letters, so "Géologie" becomes "gologie" [Repo, tested]. An alias written with its accent still matches, because the raw lowercase text is looked up first. But unaccented or mis-accented typing will not match. Accent folding in `src/data/preprocessing.py` is recommended before French aliases are relied on.

## D. Learning resources impact

The validator needs a resource for every required and preferred skill [Repo], so 44 new resources are needed (114 rising to 158). "Found" below means the page was located by web search during this audit. It does not mean it passed the project's HTTP link checker, which must be run before adding. "Free" is as stated by the publisher.

| Skill | Candidate free resource | Notes |
|---|---|---|
| geology | [Physical Geology, 2nd ed. (Earle, BCcampus)](https://opentextbc.ca/physicalgeology2ed/) | Open textbook; Canadian examples |
| geophysical methods | [Geophysics for Practising Geoscientists (UBC)](https://www.eoas.ubc.ca/courses/eosc350/content/home.htm) | Open course material; confirm the current URL |
| soil mechanics | [MIT OCW 1.361 Advanced Soil Mechanics](https://ocw.mit.edu/courses/1-361-advanced-soil-mechanics-fall-2004/resources/) | Advanced level; a beginner alternative is preferable |
| mine safety | [ILO Code of practice on safety and health in opencast mines](https://www.ilo.org/resource/code-practice-safety-and-health-opencast-mines) | International; a French edition is listed in the ILO repository |
| telecommunication systems | [MIT OCW 6.02 Digital Communication Systems](https://ocw.mit.edu/courses/6-02-introduction-to-eecs-ii-digital-communication-systems-fall-2012/pages/lecture-notes/) | Free |
| radio frequency engineering | [ITU Academy: Introduction to spectrum management](https://academy.itu.int/training-courses/full-catalogue/introduction-spectrum-management) | **Fee status not confirmed**; must be checked |
| economics | [OpenStax Principles of Economics 3e](https://openstax.org/books/principles-economics-3e/pages/preface) | US examples |
| econometrics | [Introduction to Econometrics with R (University of Duisburg-Essen)](https://oek.wiwi.uni-due.de/en/research/publications/introduction-to-econometrics-with-r-14613) | Free online book; confirm the book URL |
| sociology | [OpenStax Introduction to Sociology 3e](https://openstax.org/books/introduction-sociology-3e/pages/preface) | US-centred |
| qualitative research | [Introduction to Qualitative Research Methods (Oregon State, open)](https://open.oregonstate.education/qualresearchmethods/) | Open textbook |
| business management | [OpenStax Principles of Management](https://openstax.org/books/principles-management/pages/preface) | US examples |
| laboratory safety | [WHO Laboratory biosafety manual, 4th ed.](https://www.who.int/publications/i/item/9789240011311) | Biological labs; **partial fit** for chemical labs |
| quality control | [WHO Laboratory quality management system handbook](https://www.who.int/publications/i/item/9789241548274) | Clinical labs; **partial fit** |
| stakeholder engagement | [IFC Stakeholder Engagement handbook](https://www.ifc.org/content/dam/ifc/doc/mgrt/ifc-stakeholderengagement.pdf) | Written for emerging markets |
| social impact assessment | [IAIA Social Impact Assessment Guidance](https://iaia.org/social-impact-assessment-guidance/) | International |
| ohada business law | [OHADA official site](https://www.ohada.org/en/?p=38677) | Official legal texts, not a course; mainly French |
| construction management | [Building Construction and Materials OER (LBCC)](https://lbcc.pressbooks.pub/buildingconstruction/) | US practice; covers materials more than management, **partial fit** |
| erp systems | [SAP Learning: Executing basic ERP processes with SAP S/4HANA](https://learning.sap.com/courses/executing-basic-erp-processes-with-sap-s-4hana) | Vendor course; **free status to confirm** |
| legal research, legal writing | [OpenLearn law courses](https://www.open.edu/openlearn/society-politics-law/starting-law/altformat-epub) | England, Wales and Scotland law; **jurisdiction mismatch** |
| physics, signal processing | OpenStax University Physics; MIT OCW 6.003 Signals and Systems | Known open titles, **not searched in this audit**; URLs to confirm |

**Still needing research (22 skills):** mine planning, mineral processing, rock mechanics, engineering geology, foundation design, fiber optics, building codes, reinforced concrete design, quantity surveying, contract law, commercial law, labour law, constitutional law, administrative law, public finance, public procurement, information systems management, it governance, operations management, sample preparation, community development, conflict resolution. The two law candidates above (legal research, legal writing) also need jurisdiction-appropriate replacements.

Notes on these skills:

- The existing resource for business information systems could serve information systems management. Reusing a URL across skills is only a validator warning [Repo], but a separate resource is cleaner.
- Building codes and all law skills are country-specific. For Guinea, official French-language national sources will be needed, and they should be marked as region-specific in the resource `notes` field.

**Reliable free sources to search first:**

- International bodies: ILO, WHO, IFC/World Bank, ITU Academy and IAIA.
- Open textbooks and courseware: OpenStax, BCcampus Open Textbooks, MIT OpenCourseWare and OpenLearn.
- The OHADA site for business law.
- National government portals, for national law and building regulations.

## E. Recommendation engine compatibility

| Component | Supports new careers without code change? | Evidence |
|---|---|---|
| Required and preferred skill matching | Yes | Exact matching against CSV skill lists (`src/engine/matching.py`) [Repo] |
| Interest matching | Yes, if only existing interest terms are used | Controlled vocabulary of 20 terms (`INTERESTS`) [Repo] |
| Education scoring | Yes | 0 to 4 scale; small weight (0.05) [Repo] |
| Normalisation and aliases | Yes for English | Alias file only. **French accents are dropped** (Section C) [Repo] |
| Unknown-skill handling | Yes | Skills not in the catalogue are reported back to the learner [Repo] |
| Ranking and tie-breaking | Yes | Score, coverage, matched count, then career id. New ids C051 to C064 lose exact ties to older careers [Repo] |
| Skill gap and roadmap | Yes | Driven by catalogue data. Roadmap texts such as "Required by N of 50 careers" update automatically [Repo] |
| Resource matching | Yes, once each new skill has a resource | `ResourceCatalog.for_skill` [Repo] |
| Session feedback similarity | Yes | Uses skills and category; new categories have no similar careers yet [Repo] |
| Live ML comparison | Runs, but numbers change | Models train on 36 × N pairs; career-agnostic features [Repo] |

**List-length bias.** Careers with 3 required skills gain more from one matched skill than careers with 4 or 5 [Repo, documented in `docs/evaluation_report.md`]. Every proposed career uses 4 required skills, so the additions do not worsen that bias.

## F. Dataset and validation impact

These changes would be needed at implementation time [Repo]:

- **Data:**
  - `data/raw/careers.csv`: 14 rows, C051 to C064.
  - `data/raw/resources.csv`: 44 rows, R115 to R158.
  - `data/raw/skill_aliases.csv`: optional aliases.
- **Validation:** in `src/data/validation.py`, change `EXPECTED_CAREER_COUNT` from 50 to 64 and add new categories to `CATEGORIES` if approved. Interests are unchanged unless new terms are approved.
- **UI:**
  - Analytics colours: `src/ui/theme.py` defines `CATEGORY_PALETTE` with exactly 8 colours, and `pages/5_Analytics.py` looks up a colour per category. A ninth category without a colour raises a KeyError and breaks the Analytics page.
  - The home page shows the counts (50, 8, 114, 114).
  - `src/ui/model_rankings.py` says "the same 50 careers".
- **Evaluation code:** `src/evaluation/experiments.py` loops over `CATEGORIES`. New categories change `reports/evaluation_results.json` even before any profile changes.
- **Tests with hard-coded counts:**
  - `tests/test_app.py`: 50 careers, 8 categories, 114 skills, 114 resources, "Showing 50 of 50".
  - `tests/test_ui_views.py`: 50.
  - `tests/test_recommendations.py`: 50 and 114.
  - `tests/test_url_checker.py`: 114.
  - `tests/test_ml.py`: 50.
  - `tests/test_model_comparison.py`: 1,800 pairs.
  - `tests/test_data_validation.py`: 50.
  - `tests/test_roadmap.py`: 50 careers ranked.
  - Tests for theme and category count.
- **Docs:** `docs/dataset_documentation.md`, `README.md`, `docs/recommendation_algorithm.md` and `research/methodology.md` (dataset table). Also the O*NET mapping audit `research/data/onet_mapping_audit.csv`, which would grow from 50 rows to 64.

## G. Evaluation impact

The 36 labelled profiles were labelled against the 50 current careers [Repo]. Adding careers affects the metrics as follows:

| Metric | Effect |
|---|---|
| Labels | No profile has a label for any new career. A new career that suits a profile is treated as not relevant, which is a false negative in the labels. |
| Precision@5 | Can only stay the same or fall: a new career entering a top 5 takes a slot from a labelled one. The ceiling (about 0.32) does not change. |
| Recall@5 | Can fall if a new career pushes a labelled career out of the top 5. It is 1.000 today for the formula. |
| MAP and R-precision | Can fall whenever a new career outranks a labelled one. Any rise would come only from tie-breaking changes. |
| Catalogue coverage | The denominator grows from 50 to 64. No profile targets law, social science or mining, so the new careers would be untested. |
| Reproducibility checks | The evaluation, research, ML and sensitivity checks all rebuild results from the current catalogue, so all four `--check` commands, including the CI ones, would fail once careers are added. |

**The existing evaluation results must not be presented as evaluating the expanded catalogue.** They measure agreement with labels for 50 careers only. Applying them to 64 careers would claim evidence that does not exist. Also, the new careers are concentrated in sectors (mining, law, social science) that no evaluation profile represents.

**What implementation needs:**

1. Freeze the original evaluation on the 50-career catalogue. Either keep a versioned copy of the v1.2.0 data or limit evaluation to C001 to C050, so the published results stay reproducible.
2. Add new labelled profiles for the new sectors. Ideally independent reviewers label them, which also addresses the single-author risk.
3. Report the 64-career evaluation separately, as a new study.

## H. Implementation plan [Proposal]

1. **Decisions before any record is added:**
   - Confirm the 3 merges.
   - Confirm the refined titles (Building Construction Engineer, the two law titles, Information Systems Manager, Operations Manager, Chemical Laboratory Technician).
   - Decide on Geological Engineer.
   - Approve the category option.
2. **Freeze the evaluation:** keep the 50-career catalogue snapshot used by the four saved reports, and make the evaluation scripts load it explicitly. Then run all four checks, which should still match.
3. **Code preparation without new careers:**
   - Extend `CATEGORY_PALETTE` and `CATEGORIES`, if approved.
   - Make the expected count configurable.
   - Add accent folding to preprocessing.
   - Update count-based tests to read from the data where sensible.
4. **First batch (best evidence, 7 careers):** Mining Engineer, Telecommunications Engineer, Geotechnical Engineer, Geophysicist, Economist, Sociologist and Community Relations Specialist. Add their resources first, run the link checker, then add the career rows.
5. **Second batch (after refinement):** the 6 refined careers, and Geological Engineer if confirmed. Law resources need country-specific sources.
6. **Then:** aliases, documentation, the O*NET and ISCO mapping audit, and a new labelled-profile set for a separate 64-career evaluation.
7. **At each step:** validate the data, run the full test suite, open the app at desktop and phone width, and leave the original 50 career rows unchanged.

## I. Risks report

| # | Area | Risk | Severity | Mitigation |
|---|---|---|---|---|
| 1 | Occupation overlap | Duplicate titles (Civil, Electrical, HR) | High | Merge; the validator already blocks duplicates |
| 2 | Occupation overlap | Mining, Geological and Geotechnical are near-duplicates | Medium | Distinct skill lists; decide on Geological Engineer |
| 3 | Occupation overlap | MIAGE, Business Administration and Laboratory Technician duplicate existing careers if added literally | Medium | Refined titles in Section B |
| 4 | Definition | "Business Administration Specialist" and "Building Engineer" are not well-defined occupations | High | Lecturer confirmation of the intended job |
| 5 | Regional relevance | Law content and building codes are national; OHADA is regional | High | Country-specific resources, marked as such; avoid claiming general applicability |
| 6 | Education estimation | 0 to 4 levels are estimates; licensing (bar, engineering registration) is not represented | Medium | Label as estimates; add a licensing note in descriptions |
| 7 | Source reliability | Most occupation sources are US (O*NET) or European (ESCO) | Medium | Add ISCO-08 codes; seek African national frameworks where available |
| 8 | Resources | 22 of 44 new skills have no candidate free resource yet; some candidates have unconfirmed fees | High | Do not add a career until all its skills have checked resources |
| 9 | Resources | Some candidates fit only partly (WHO lab manuals for chemical labs; OpenLearn law for Guinea) | Medium | Note the limitation in the resource notes, or find a better source |
| 10 | Input handling | Accented French skills are dropped by normalisation | Medium | Accent folding before relying on French aliases |
| 11 | Ranking | New careers win or lose exact ties by career id; new categories have no similar careers for feedback | Low | Accept and document |
| 12 | Evaluation | Existing results do not cover the new careers; reproducibility checks will fail | High | Freeze the 50-career evaluation; evaluate the expansion separately |
| 13 | UI | Analytics page crashes with more than 8 categories unless the palette is extended | High | Extend the palette in the same change as the categories |
| 14 | Market claims | Employment relevance stated without labour-market data | Medium | Cite sector sources (as for Guinea mining); avoid demand figures without data |

## 6. Category options

| Option | Advantages | Disadvantages |
|---|---|---|
| Keep 8 | No code change for categories; chart colours fit | Law, economics and sociology would be mislabelled (for example as Business or Education). Explorer filters and feedback similarity would mislead |
| **Keep 8 + add Law and Social Sciences (10) (recommended)** | Smallest honest change; follows ISCO-08 (261 Legal professionals; 263 Social professionals, which include economists and sociologists) | Palette, `CATEGORIES` and tests need updating. Geophysicist and Chemical Laboratory Technician go into Engineering, which ISCO-08 justifies only at a broad level (science and engineering share sub-major groups 21 and 31) |
| Keep 8 + Law, Social Sciences and Natural Sciences (11) | Most accurate for Geophysicist and Chemical Laboratory Technician | One more category with only 2 careers |
| Broad categories with specialisations | Scales to many careers | Changes existing assignments and the evaluation strata; most disruptive |

Under the recommended option, Community Relations Specialist stays in Business (ISCO-08 2432 Public relations professionals). Economist moves to Social Sciences (ISCO-08 2631). Existing category assignments are not changed.

## Sources

- O*NET OnLine:
  - [17-2151.00 Mining and Geological Engineers](https://www.onetonline.org/link/summary/17-2151.00)
  - [19-2042.00 Geoscientists](https://www.onetonline.org/link/custom/19-2042.00)
  - [15-1241.01 Telecommunications Engineering Specialists](https://onetonline.org/link/custom/15-1241.01)
  - [27-3031.00 Public Relations Specialists](https://www.onetonline.org/link/summary/27-3031.00)
  - [11-3021.00 Computer and Information Systems Managers](https://www.onetonline.org/link/summary/11-3021.00)
  - [19-4031.00 Chemical Technicians](https://www.onetonline.org/link/details/19-4031.00)
  - Lawyers 23-1011.00, Economists 19-3011.00 and Sociologists 19-3041.00 were located via search; their pages should be checked when the rows are written.
- ESCO and ISCO:
  - [mining geotechnical engineer](https://worldoftaxonomy.com/codes/esco_occupations/efc75d4e-dfbf-4178-929c-0ae198801c36)
  - [construction engineer](https://worldoftaxonomy.com/codes/esco_occupations/2a914d26-42aa-46b5-acf3-097d51ba4617)
  - [ISCO-08 2114](https://www.worldoftaxonomy.com/codes/isco_08/2114)
  - [ISCO-08 2146](https://worldoftaxonomy.com/codes/isco_08/2146)
  - [ANZSCO 233212 Geotechnical Engineers](https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles/occupations/233212-geotechnical-engineers)
- MIAGE: [Université Paris-Saclay](https://www.universite-paris-saclay.fr/formation/master/methodes-informatiques-appliquees-la-gestion-des-entreprises-miage)
- Building engineer: [Wikipedia](https://en.wikipedia.org/wiki/Building_engineer)
- OHADA: [Wikipedia](https://en.wikipedia.org/wiki/OHADA), [ohada.org](https://www.ohada.org/en/?p=38677)
- Guinea mining: [China Global South](https://chinaglobalsouth.com/2026/01/26/guinea-bauxite-exports-china-2025/), [Mining.com](https://www.mining.com/web/mass-layoffs-overshadow-guineas-simandou-mega-mine-as-output-accelerates/)
- Resources: as linked in Section D.
