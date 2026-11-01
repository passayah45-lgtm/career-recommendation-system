# African career expansion: records, sources and gaps (dataset v1.3.0)

Implemented 1 November 2026 from the lecturer's official list of 17 careers. The official titles are used exactly as given.

**Labels used in this document:**

- **[Sourced]**: the statement comes from the cited source.
- **[Curated]**: the author's estimate. This covers every description, skill list, interest list, education level and learning goal. None of them is copied from an occupational database.

## 1. The 17 official titles

| Official title | Record | Status |
|---|---|---|
| Mining Engineer | C051 | New |
| Geological Engineer | C052 | New |
| Telecommunications Engineer | C053 | New |
| Civil Engineer | C046 | Already existed, unchanged |
| Building Engineer | C054 | New |
| Electrical Engineer | C048 | Already existed, unchanged |
| Geotechnical Engineer | C055 | New |
| Geophysicist | C056 | New |
| Private Law Specialist | C057 | New |
| Public Law Specialist | C058 | New |
| Human Resources Specialist | C033 | Already existed, unchanged |
| Management Information Systems Specialist (MIAGE) | C059 | New |
| Economist | C060 | New |
| Business Administration Specialist | C061 | New |
| Laboratory Technician | C062 | New |
| Sociologist | C063 | New |
| Community Relations Specialist | C064 | New |

The catalogue grows from 50 to 64 careers. Mining Engineer, Geological Engineer and Geotechnical Engineer are separate records with different required skills, as instructed.

## 2. Categories and reasoning

| Career | Category | Reason |
|---|---|---|
| C051 to C055 | Engineering | Engineering occupations (ISCO-08 sub-major group 21, "Science and engineering professionals") |
| C056 Geophysicist | Engineering | No Natural Sciences category was created, as instructed. Earth-science professionals share ISCO-08 sub-major group 21 with engineers, and the career sits with the mining, geological and geotechnical careers it works alongside |
| C057, C058 | **Law** (new) | Legal professionals (ISCO-08 261); no existing category fits |
| C059 MIAGE | Business | Information-systems management in organisations; Computer Systems Analyst (C016, Software) stays the technical counterpart |
| C060 Economist, C063 Sociologist | **Social Sciences** (new) | ISCO-08 263 groups economists (2631) and sociologists (2632) |
| C061 Business Administration Specialist | Business | Administration and management of organisations |
| C062 Laboratory Technician | Healthcare | Medical and clinical laboratories are a main employer of laboratory technicians (ISCO-08 3212), and the record sits next to C042 Medical Laboratory Technologist. The description also covers routine testing in other laboratories, which is noted as a limitation in the risks report |
| C064 Community Relations Specialist | Business | A corporate function close to public relations (ISCO-08 2432) |

The validator now allows 10 categories. `PLANNED_CATEGORIES` is empty.

## 3. Occupational references

| Career | O*NET code in the record | Evidence |
|---|---|---|
| Mining Engineer | 17-2151.00 | [Sourced] O*NET "Mining and Geological Engineers, Including Mining Safety Engineers": reported titles include Mining Engineer; Job Zone Four, 79% of new hires need a bachelor's degree ([O*NET](https://www.onetonline.org/link/summary/17-2151.00)) |
| Geological Engineer | 17-2151.00 | [Sourced] The same O*NET occupation names geological engineers in its title |
| Geophysicist | 19-2042.00 | [Sourced] O*NET "Geoscientists, Except Hydrologists and Geographers" lists "Project Geophysicist" among its reported titles ([O*NET](https://www.onetonline.org/link/custom/19-2042.00)) |
| Economist | 19-3011.00 | [Sourced] O*NET occupation Economists |
| Sociologist | 19-3041.00 | [Sourced] O*NET occupation Sociologists |
| Other nine | none | The closest occupations are recorded in `research/data/onet_mapping_audit.csv` but not put in the career row, because none matches the official title closely enough. Examples: 15-1241.01 for Telecommunications Engineer, 23-1011.00 Lawyers for the law careers, 11-3021.00 for MIAGE, 27-3031.00 for Community Relations |

Further context:

- [Sourced] ESCO places "construction engineer" and "mining geotechnical engineer" under ISCO-08 2142, Civil Engineers ([construction engineer](https://worldoftaxonomy.com/codes/esco_occupations/2a914d26-42aa-46b5-acf3-097d51ba4617), [mining geotechnical engineer](https://worldoftaxonomy.com/codes/esco_occupations/efc75d4e-dfbf-4178-929c-0ae198801c36)).
- [Sourced] MIAGE (Méthodes Informatiques Appliquées à la Gestion des Entreprises) is a French university degree that combines computing and management ([Université Paris-Saclay](https://www.universite-paris-saclay.fr/formation/master/methodes-informatiques-appliquees-la-gestion-des-entreprises-miage)).
- [Sourced] The title "Building Engineer" means different things in different countries ([Wikipedia](https://en.wikipedia.org/wiki/Building_engineer)).

## 4. Education levels

Every level is the author's estimate. For 5 careers a US occupational reference agrees with the estimate. The same split is stored per career in `research/data/expansion_education_basis.csv`, and a test checks that file against `careers.csv`.

| Career | Level | Basis | Reference evidence (checked 2026-11-01) |
|---|---|---|---|
| Mining Engineer | 3 | **Estimate, supported by US reference** | [Sourced] O*NET 17-2151.00, Job Zone Four: 79% of respondents say a new hire needs a bachelor's degree, 17% a post-baccalaureate certificate, 3% a master's |
| Geological Engineer | 3 | **Estimate, supported by US reference** | [Sourced] The same O*NET occupation (17-2151.00), which combines mining and geological engineers |
| Geophysicist | 3 | **Estimate, supported by US reference** | [Sourced] O*NET 19-2042.00, Job Zone Four: 48% bachelor's, 37% master's, 7% doctoral. Bachelor's is the most common answer, but 44% report a graduate degree |
| Economist | 4 | **Estimate, supported by US reference** | [Sourced] O*NET 19-3011.00: "Most of these occupations require graduate school." BLS: typical entry-level education is a master's degree |
| Sociologist | 4 | **Estimate, supported by US reference** | [Sourced] O*NET 19-3041.00, Job Zone Five: "Most of these occupations require graduate school." BLS: typical entry-level education is a master's degree |
| Telecommunications Engineer | 3 | **Estimate** [Curated] | None. No O*NET occupation matches the title |
| Building Engineer | 3 | **Estimate** [Curated] | None. The title means different things in different countries |
| Geotechnical Engineer | 3 | **Estimate** [Curated] | None |
| Private Law Specialist | 4 | **Estimate** [Curated] | None |
| Public Law Specialist | 4 | **Estimate** [Curated] | None |
| MIAGE | 4 | **Estimate** [Curated] | None. Follows the MIAGE master's route; other entry routes exist |
| Business Administration Specialist | 3 | **Estimate** [Curated] | None |
| Laboratory Technician | 2 | **Estimate** [Curated] | None. Medical and chemical technician routes differ |
| Community Relations Specialist | 3 | **Estimate** [Curated] | None |

- "Supported" means a US source agrees with the estimate. It does not mean the level was copied from that source.
- Requirements in Guinea and other African countries were not verified for any career.
- Practising law, and some engineering titles, need national professional admission or registration. The 0 to 4 scale does not represent this.

Sources: [O*NET 17-2151.00](https://www.onetonline.org/link/summary/17-2151.00), [O*NET 19-2042.00](https://www.onetonline.org/link/summary/19-2042.00), [O*NET Job Zone 19-3011.00](https://www.onetonline.org/skills/zone/19-3011.00), [O*NET Job Zone 19-3041.00](https://www.onetonline.org/skills/zone/19-3041.00), [BLS Economists](https://www.bls.gov/ooh/life-physical-and-social-science/economists.htm), [BLS Sociologists](https://www.bls.gov/ooh/life-physical-and-social-science/sociologists.htm).

## 5. African relevance

- [Sourced] Guinea's bauxite exports rose to about 183 million tonnes in 2025 ([China Global South](https://chinaglobalsouth.com/2026/01/26/guinea-bauxite-exports-china-2025/)).
- [Sourced] The Simandou iron-ore project began output in late 2025. The same reports describe mass layoffs after construction ended ([Mining.com](https://www.mining.com/web/mass-layoffs-overshadow-guineas-simandou-mega-mine-as-output-accelerates/)).
- [Sourced] OHADA business law applies in its member states. The texts of its Uniform Acts are published online ([OHADA](https://en.wikipedia.org/wiki/OHADA), [ohada.org](https://www.ohada.org/en/?p=38677)).
- No employment, salary or demand figures are stated for any career, because none were verified.

## 6. New skills and learning resources

30 new skills, each with one resource (R115 to R144). For every resource I opened the page with a web tool on 2026-11-01 and read its access terms. The status is `search_index_confirmed`: the exact URL appeared in search results. The project's link checker (`src/data/url_checker.py`) ran on all 30 links the same day, but the workspace network policy refused every connection, so the result is inconclusive. A second pass with the web tool loaded all 30 pages. Details: `docs/african_expansion_link_check.md`.

| Skill | Resource | Access and limits |
|---|---|---|
| rock mechanics | MIT OCW 12.524 Mechanical Properties of Rocks | Free; graduate level |
| mine safety | ILO Code of practice on safety and health in opencast mines (2018) | Free PDF; also in French |
| mine planning | Penn State MNG 230, Surface Mining module | CC BY-NC-SA 4.0; US examples |
| geology | Physical Geology 2nd ed. (BCcampus) | CC BY 4.0 |
| soil mechanics | MIT OCW 1.361 Advanced Soil Mechanics | Free; graduate level |
| geophysical methods | Geophysics for Practicing Geoscientists (GitHub source) | CC BY 4.0; source repository with a link to the site |
| foundation design | Fellenius, Basics of Foundation Design (2023) | Author states free download |
| physics | OpenStax University Physics Vol. 1 | CC BY-NC-SA 4.0 |
| telecommunication systems | MIT OCW 6.02 Digital Communication Systems | CC BY-NC-SA 4.0 |
| signal processing | MIT OCW 6.003 Signals and Systems | CC BY-NC-SA 4.0 |
| radio frequency engineering | Radio Systems Engineering (Virginia Tech, Open Textbook Library) | CC BY-NC 4.0 |
| construction management | Introduction to Construction Project Management (Pressbooks) | CC BY 4.0; US practice |
| reinforced concrete design | MIT OCW 1.054 Mechanics and Design of Concrete Structures | CC BY-NC-SA 4.0; design codes differ by country |
| legal research | Sources of American Law (CALI) | CC BY-SA 4.0; **US law** |
| contract law | OpenStax Business Law I Essentials 2e, ch. 7 | CC BY-NC-SA; **US law** |
| constitutional law | OpenStax Business Law I Essentials, ch. 4 | CC BY-NC-SA 4.0; **US constitution** |
| administrative law | OpenStax Business Law I Essentials 2e, ch. 10 | CC BY-NC-SA; **US law** |
| ohada business law | OHADA Uniform Acts texts (ohada.com, UNIDA Association) | Free PDFs; private association, not the official site |
| public finance | Principles of Macroeconomics ch. 13 (LibreTexts, OpenStax content) | CC BY 4.0; US examples |
| information systems management | Foundations of Management Information Systems (UH Libraries) | CC BY-NC-SA 4.0 |
| economics | OpenStax Principles of Economics 3e | CC BY-NC-SA 4.0 |
| business management | OpenStax Principles of Management | CC BY-NC-SA 4.0 |
| laboratory safety | WHO Laboratory biosafety manual, 4th ed. | CC BY-NC-SA 3.0 IGO; biological laboratories |
| quality control | WHO Laboratory quality management system handbook | Download offered; clinical laboratories |
| sociology | OpenStax Introduction to Sociology 3e | CC BY-NC-SA 4.0 |
| qualitative research | Introduction to Qualitative Research Methods (Oregon State) | CC BY-SA 4.0 |
| stakeholder engagement | IFC Stakeholder Engagement handbook (2007) | IFC encourages distribution with credit |
| community development | Community Development Practice (Centennial College) | CC BY-NC-SA |
| conflict resolution | Navigating the Space Between Us (Portland State) | CC BY-NC 4.0 |
| social impact assessment | IAIA Social Impact Assessment Guidance (2015) | Free PDF |

**Gaps.** These skills would describe the careers well, but no free resource could be verified, so they were **not** added. The validator requires one resource per skill.

| Skill | Career | What was found |
|---|---|---|
| econometrics | Economist | The free online book could not be opened with the web tool; an archive copy was blocked |
| legal writing | Law careers | Candidate open textbooks are US-focused and could not be confirmed |
| engineering geology | Geological Engineer | No open textbook found |
| mineral processing | Mining Engineer | No open course confirmed |
| fiber optics | Telecommunications Engineer | Only copyrighted books found |
| building codes | Building Engineer | National codes; none free and relevant to Guinea confirmed |
| erp systems | MIAGE | Free status of vendor courses not confirmed |
| sample preparation | Laboratory Technician | No dedicated free resource confirmed |

Existing skills were reused where they fit: engineering mathematics, cad, gis, project management, networking, cloud computing, structural analysis, technical writing, communication, environmental science, python, linear algebra, accounting, risk management, business analysis, sql, data modeling, data warehousing, statistics, research methods, r programming, data visualization, excel, human resource management, organizational behavior, laboratory techniques, chemistry, microbiology, infection control and survey design.

## 7. Aliases added (19)

French: géologie, mécanique des sols, mécanique des roches, méthodes géophysiques, droit des contrats, droit constitutionnel, droit administratif, droit ohada, finances publiques, économie, sociologie, gestion des conflits.

English: geomechanics, rf engineering, telecommunications, ohada law, management information systems, stakeholder management, sia.

Accent folding means each French alias also matches when typed without accents or in capitals. Tests cover this.
