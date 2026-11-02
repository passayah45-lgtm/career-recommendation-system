# Interest taxonomy: second review (catalogue v1.3.0)

Review date: 2 November 2026. Repository state: commit 593b87e on `main`. Reviews the 21-interest taxonomy and the draft assignments in `docs/skills_interests_audit.md` (first audit). **Audit and research only.** No production data, engine, formula, interface, career record, frozen dataset or report was changed. This document is not committed.

The formula is unchanged throughout: required skills 0.55, preferred skills 0.15, interests 0.25, education 0.05.

**Evidence levels** used in this report:
- **[O*NET]** official occupational interest data from O*NET OnLine, read on 2 November 2026 (section E);
- **[Interpretation]** a research-based reading of that data, for example linking an interest code to an activity;
- **[Proposal]** this review's own classification or assignment.

## A. Executive findings

1. **The first audit's direction is sound, but 9 of its 21 terms need work.**
   - Five should be renamed for clarity: "working with numbers and models", "protecting systems and investigating threats", "fieldwork and the natural environment", "organising information, records and processes", "interpreting laws, rules and policies".
   - Three should be split or replaced:
     - "designing products, spaces and systems" (on 18 careers, mixing app design with building design);
     - "building and maintaining technical systems" (mixing computer networks with electrical equipment);
     - "hands-on and physical work" (mixing patients, machines and building sites).
   - One is missing: nothing covers money and finance, so accountants and financial analysts were described only by numbers and business.
   - Result: a revised vocabulary of **23 interests** (section B).
2. **18 of 64 careers need a substantive change** beyond renaming:
   - The remaining 46 draft assignments hold up.
   - Several changes come from checking O*NET. Medical Records Specialist (C043) and Medical Laboratory Technologist (C042) are not patient-care work. Web Developer (C010) has no artistic interest in O*NET (code CI).
3. **The O*NET check is broadly positive** [O*NET + Interpretation]:
   - For the 48 careers with a full O*NET interest code, the recommended interests agree with that code on all three interests for 41 careers, and on two of three for the other 7.
   - For 4 careers only the first interest type (Realistic) could be confirmed.
   - 12 careers have no O*NET code, and their assignments are provisional.
4. **Differentiation:**
   - 58 distinct interest sets among 64 careers, with 6 identical pairs.
   - All 6 pairs are closely related careers, and two of them share an identical O*NET code (BI Analyst and Management Analyst: CIE). They are natural overlap, not errors.
   - No interest was added only to make a career unique.
5. **One term is broad:** "Keeping information, records and procedures in order" is on 18 careers. O*NET's Conventional type supports 15 of them, and the other 3 have no O*NET code. It should stay, but with a sharp description.
6. **Three interests per career is right**, with two known gaps:
   - nothing captures the physical, active side of physical therapy;
   - O*NET's Social element of engineering is not captured.
7. **A limit of 1 to 5 interests is reasonable but untested.**
   - No synthetic profile in either evaluation uses more than 4 interests, so the limit was never exercised.
   - A simulation shows that picking more than 5 interests adds points to more careers without narrowing the best-matching group.
   - It needs a separate experiment before a hard cap is introduced.

## B. Interest taxonomy review

### B1. Each proposed interest against the ten questions

Key: **Y** yes, **P** partly, **N** no. Careers = careers assigned the term in the first audit's draft.

| # | First-audit interest | 1 Preference | 2 Clear | 3 Overlaps another interest | 4 Overlaps a skill | 5 Activity or setting | 6 Careers | 7 Distinguishes | 8 Accessible | 9 Specific | 10 Clear without help |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | analysing data and information | Y | Y | P (numbers, research) | P (statistics) | Y | 12 | Y | Y | P | Y |
| 2 | researching and investigating | Y | Y | P (analysing) | P (research methods) | Y | 14 | Y | Y | Y | Y |
| 3 | working with numbers and models | Y | P ("models") | P | P (mathematics skills) | Y | 15 | Y | P | P | P |
| 4 | scientific and laboratory work | Y | Y | N | P (chemistry) | Y | 7 | Y | Y | Y | Y |
| 5 | protecting systems and investigating threats | Y | P | P ("investigating") | P (security skills) | Y | 8 | Y | P | Y | P |
| 6 | building and maintaining technical systems | Y | P | P (software, hands-on) | P | Y | 13 | P (IT and electrical mixed) | P | N | P |
| 7 | hands-on and physical work | Y | P | P | N | Y | 6 | N (patients, machines, sites) | Y | N | P |
| 8 | fieldwork and the natural environment | Y | P ("fieldwork") | N | N | Y | 7 | Y | P | Y | P |
| 9 | writing software and building apps | Y | Y | P (design of apps) | P (programming) | Y | 13 | Y | Y | Y | Y |
| 10 | creating visual art and graphics | Y | Y | P (design) | P (graphic design) | Y | 5 | Y | Y | Y | Y |
| 11 | designing products, spaces and systems | Y | P | P (visual art) | P (design skills) | Y | 18 | N (apps, buildings, networks) | P | N | P |
| 12 | writing and editing | Y | Y | N | P (technical writing) | Y | 7 | Y | Y | Y | Y |
| 13 | teaching and training others | Y | Y | P (helping) | P (lesson planning) | Y | 6 | Y | Y | Y | Y |
| 14 | caring for people's health | Y | Y | P (helping) | P (patient care) | Y | 7 | Y | Y | Y | Y |
| 15 | helping and advising people | Y | Y | P (caring, teaching) | P (counseling) | Y | 10 | Y | Y | P | Y |
| 16 | working with communities | Y | Y | P (helping) | P (community development) | Y | 3 | Y | Y | Y | Y |
| 17 | leading people and projects | Y | Y | N | P (project management) | Y | 4 | Y | Y | Y | Y |
| 18 | running and growing a business | Y | Y | N | P (business management) | Y | 7 | Y | Y | Y | Y |
| 19 | presenting, persuading and negotiating | Y | Y | N | P (communication) | Y | 8 | Y | Y | P (three activities) | Y |
| 20 | organising information, records and processes | Y | P ("processes") | N | P (data modeling, coding) | Y | 16 | P (broad) | P | P | P |
| 21 | interpreting laws, rules and policies | Y | P ("interpreting") | N | P (law skills) | Y | 6 | Y | P | Y | P |

Every term passes question 1: the first audit removed the abilities and domain words. The weaknesses are clarity, breadth and the mixing of different work in one term.

### B2. Decisions

| Proposed interest | Decision | Reason | Suggested improvement |
|---|---|---|---|
| analysing data and information | Retain | Clear activity; well supported by O*NET Investigative codes | Description must separate it from numbers and research |
| researching and investigating | Retain | Clear, common preference | None |
| working with numbers and models | Rename | "Models" is unclear to many students | **Working with numbers and calculations** |
| scientific and laboratory work | Retain | Clear; covers lab and field science | None |
| protecting systems and investigating threats | Rename | Too long; "investigating" duplicates the research term | **Keeping computer systems and data safe** |
| building and maintaining technical systems | Split | Mixed computer networks with electrical and telecom equipment | **Setting up and running computer systems and networks**; equipment goes to the next term |
| hands-on and physical work | Replace | Mixed patient care, machines and building sites; did not separate careers | **Working with tools, machines and equipment** |
| fieldwork and the natural environment | Rename | "Fieldwork" is jargon for many students | **Working outdoors and with the natural environment** |
| writing software and building apps | Retain | Clear | None |
| creating visual art and graphics | Retain | Clear | None |
| designing products, spaces and systems | Split | On 18 careers; app design and building design attract different people | **Designing apps, websites and user experiences** and **Designing buildings, structures and physical products** |
| writing and editing | Retain | Clear | None |
| teaching and training others | Retain | Clear | None |
| caring for people's health | Retain | Clear | None |
| helping and advising people | Retain | Clear; individual support | Description separates it from caring and teaching |
| working with communities | Retain | Few careers (4), but the only term for law, social science and community work with groups | Description: groups and the public, not individuals |
| leading people and projects | Retain | Clear | None |
| running and growing a business | Retain | Clear | None |
| presenting, persuading and negotiating | Rename (order only) | Lead with the most recognisable word | **Persuading, presenting and negotiating** |
| organising information, records and processes | Rename | "Processes" is abstract; broad term needs plain words | **Keeping information, records and procedures in order** |
| interpreting laws, rules and policies | Rename | "Interpreting" is harder for international students | **Working with laws, rules and regulations** |
| (none) | Add | Accountants, financial analysts and business administrators had no money-related interest; finance is a common, distinct preference | **Managing money and financial information** |

Revised vocabulary: **23 interests**. No term was merged away, and no term from the first audit was kept only because it was proposed.

## C. Career assignment review

Exactly three recommended interests per career.

**Confidence levels:**
- **High:** O*NET close match, and the recommendation agrees with its interest code.
- **Medium:** O*NET broader occupation, only the first interest type confirmed, or partial agreement.
- **Provisional:** no O*NET code; author judgement from the career record.

The "Evidence" column gives the O*NET code, how closely it matches, and the O*NET interest code read on 2 November 2026.

| Career ID | Official title | Proposed interests (first audit) | Assessment | Recommended interests | Confidence |
|---|---|---|---|---|---|
| C001 | Data Scientist | analysing data and information; writing software and building apps; working with numbers and models | Draft accurate; matches O*NET IC. Evidence: O*NET 15-2051.00 (close): IC | Analysing data and information; Working with numbers and calculations; Writing software and building apps | High |
| C002 | Data Analyst | analysing data and information; organising information, records and processes; presenting, persuading and negotiating | Draft reasonable; presenting findings is real work; no O*NET code. Evidence: No O*NET code | Analysing data and information; Keeping information, records and procedures in order; Persuading, presenting and negotiating | Provisional |
| C003 | Machine Learning Engineer | writing software and building apps; building and maintaining technical systems; working with numbers and models | Draft reasonable; 'technical systems' narrowed to running computer systems (model deployment). Evidence: No O*NET code | Writing software and building apps; Working with numbers and calculations; Setting up and running computer systems and networks | Provisional |
| C004 | Business Intelligence Analyst | analysing data and information; organising information, records and processes; running and growing a business | Draft accurate; matches CIE; identical to C028 by design (same O*NET code). Evidence: O*NET 15-2051.01 (close): CIE | Analysing data and information; Keeping information, records and procedures in order; Running and growing a business | High |
| C005 | Data Engineer | building and maintaining technical systems; writing software and building apps; organising information, records and processes | Draft accurate; matches CI. Evidence: O*NET 15-1243.01 (broader): CI | Setting up and running computer systems and networks; Writing software and building apps; Keeping information, records and procedures in order | Medium |
| C006 | Statistician | working with numbers and models; researching and investigating; analysing data and information | Draft accurate; matches IC; shares set with C060 (natural overlap). Evidence: O*NET 15-2041.00 (close): IC | Working with numbers and calculations; Researching and investigating; Analysing data and information | High |
| C007 | AI Research Scientist | researching and investigating; working with numbers and models; writing software and building apps | Draft accurate. Evidence: O*NET 15-1221.00 (broader): IC | Researching and investigating; Working with numbers and calculations; Writing software and building apps | Medium |
| C008 | Database Administrator | building and maintaining technical systems; organising information, records and processes; protecting systems and investigating threats | Draft accurate; matches CI. Evidence: O*NET 15-1242.00 (close): CI | Setting up and running computer systems and networks; Keeping information, records and procedures in order; Keeping computer systems and data safe | High |
| C009 | Software Developer | writing software and building apps; building and maintaining technical systems; researching and investigating | Draft 'technical systems' weak for general developers; design of apps fits better. Evidence: O*NET 15-1252.00 (close): IC | Writing software and building apps; Designing apps, websites and user experiences; Researching and investigating | Medium |
| C010 | Web Developer | writing software and building apps; designing products, spaces and systems; creating visual art and graphics | Draft 'visual art' not supported (O*NET CI); replaced by running web systems. Evidence: O*NET 15-1254.00 (close): CI | Writing software and building apps; Designing apps, websites and user experiences; Setting up and running computer systems and networks | Medium |
| C011 | Software Quality Assurance Tester | organising information, records and processes; building and maintaining technical systems; researching and investigating | Draft accurate; matches ICR. Evidence: O*NET 15-1253.00 (close): ICR | Researching and investigating; Keeping information, records and procedures in order; Setting up and running computer systems and networks | High |
| C012 | Mobile App Developer | writing software and building apps; designing products, spaces and systems; building and maintaining technical systems | Visual work in app interfaces kept; no O*NET code. Evidence: No O*NET code | Writing software and building apps; Designing apps, websites and user experiences; Creating visual art and graphics | Provisional |
| C013 | DevOps Engineer | building and maintaining technical systems; writing software and building apps; organising information, records and processes | Draft accurate. Evidence: O*NET 15-1252.00 (broader): IC | Setting up and running computer systems and networks; Writing software and building apps; Keeping information, records and procedures in order | Medium |
| C014 | Cloud Engineer | building and maintaining technical systems; writing software and building apps; protecting systems and investigating threats | Draft accurate; identical to C022 (related infrastructure security work). Evidence: O*NET 15-1299.08 (broader): CIR | Setting up and running computer systems and networks; Writing software and building apps; Keeping computer systems and data safe | Medium |
| C015 | Computer Programmer | writing software and building apps; working with numbers and models; organising information, records and processes | Draft accurate; matches CI. Evidence: O*NET 15-1251.00 (close): CI | Writing software and building apps; Working with numbers and calculations; Keeping information, records and procedures in order | High |
| C016 | Computer Systems Analyst | analysing data and information; designing products, spaces and systems; running and growing a business | Draft designing and business replaced: O*NET IC; investigating requirements and documenting systems. Evidence: O*NET 15-1211.00 (close): IC | Analysing data and information; Researching and investigating; Keeping information, records and procedures in order | High |
| C017 | Information Security Analyst | protecting systems and investigating threats; analysing data and information; researching and investigating | Draft accurate. Evidence: O*NET 15-1212.00 (close): CI | Keeping computer systems and data safe; Analysing data and information; Researching and investigating | High |
| C018 | Penetration Tester | protecting systems and investigating threats; researching and investigating; writing software and building apps | Draft accurate. Evidence: O*NET 15-1299.04 (close): ICR | Keeping computer systems and data safe; Researching and investigating; Writing software and building apps | High |
| C019 | Digital Forensics Analyst | protecting systems and investigating threats; researching and investigating; interpreting laws, rules and policies | Draft accurate; legal evidence is real work. Evidence: O*NET 15-1299.06 (close): IC | Keeping computer systems and data safe; Researching and investigating; Working with laws, rules and regulations | Medium |
| C020 | Network and Systems Administrator | building and maintaining technical systems; protecting systems and investigating threats; organising information, records and processes | Draft accurate; matches CRI. Evidence: O*NET 15-1244.00 (close): CRI | Setting up and running computer systems and networks; Keeping computer systems and data safe; Keeping information, records and procedures in order | High |
| C021 | Computer Network Architect | designing products, spaces and systems; building and maintaining technical systems; protecting systems and investigating threats | Draft 'designing' no longer fits after the design split. Evidence: O*NET 15-1241.00 (close): ICR | Setting up and running computer systems and networks; Keeping computer systems and data safe; Researching and investigating | Medium |
| C022 | Information Security Engineer | protecting systems and investigating threats; writing software and building apps; designing products, spaces and systems | Draft 'designing' replaced by running systems. Evidence: O*NET 15-1299.05 (close): CIR | Keeping computer systems and data safe; Writing software and building apps; Setting up and running computer systems and networks | High |
| C023 | Graphic Designer | creating visual art and graphics; presenting, persuading and negotiating; designing products, spaces and systems | Draft accurate; digital design replaces generic design. Evidence: O*NET 27-1024.00 (close): AC | Creating visual art and graphics; Designing apps, websites and user experiences; Persuading, presenting and negotiating | Medium |
| C024 | UX Designer | designing products, spaces and systems; researching and investigating; helping and advising people | Draft accurate. Evidence: O*NET 15-1255.00 (broader): IAC | Designing apps, websites and user experiences; Researching and investigating; Helping and advising people | Medium |
| C025 | Interior Designer | creating visual art and graphics; designing products, spaces and systems; presenting, persuading and negotiating | Draft accurate; spaces move to the buildings design term. Evidence: O*NET 27-1025.00 (close): AR | Creating visual art and graphics; Designing buildings, structures and physical products; Persuading, presenting and negotiating | High |
| C026 | Industrial Designer | designing products, spaces and systems; hands-on and physical work; creating visual art and graphics | Draft 'hands-on' clarified as tools and machines (prototyping). Evidence: O*NET 27-1021.00 (close): ARI | Designing buildings, structures and physical products; Creating visual art and graphics; Working with tools, machines and equipment | High |
| C027 | Animator | creating visual art and graphics; writing and editing; designing products, spaces and systems | Draft accurate; storytelling kept. Evidence: O*NET 27-1014.00 (close): AR | Creating visual art and graphics; Writing and editing; Designing apps, websites and user experiences | Medium |
| C028 | Management Analyst | analysing data and information; running and growing a business; presenting, persuading and negotiating | Draft 'persuading' replaced by records (O*NET CIE). Evidence: O*NET 13-1111.00 (close): CIE | Analysing data and information; Running and growing a business; Keeping information, records and procedures in order | High |
| C029 | Financial Analyst | working with numbers and models; analysing data and information; running and growing a business | Draft accurate; money now explicit. Evidence: O*NET 13-2051.00 (close): CEI | Managing money and financial information; Analysing data and information; Working with numbers and calculations | High |
| C030 | Accountant | working with numbers and models; organising information, records and processes; interpreting laws, rules and policies | Draft accurate; money now explicit. Evidence: O*NET 13-2011.00 (close): CEI | Managing money and financial information; Keeping information, records and procedures in order; Working with laws, rules and regulations | High |
| C031 | Market Research Analyst | researching and investigating; analysing data and information; running and growing a business | Draft accurate. Evidence: O*NET 13-1161.00 (close): ECI | Researching and investigating; Analysing data and information; Running and growing a business | High |
| C032 | Project Manager | leading people and projects; organising information, records and processes; running and growing a business | Draft accurate. Evidence: O*NET 13-1082.00 (close): EC | Leading people and projects; Keeping information, records and procedures in order; Running and growing a business | High |
| C033 | Human Resources Specialist | helping and advising people; organising information, records and processes; interpreting laws, rules and policies | Draft 'laws' replaced by persuading (O*NET ECS: recruitment and negotiation). Evidence: O*NET 13-1071.00 (close): ECS | Persuading, presenting and negotiating; Keeping information, records and procedures in order; Helping and advising people | High |
| C034 | Digital Marketing Specialist | presenting, persuading and negotiating; writing and editing; analysing data and information | Draft accurate. Evidence: O*NET 13-1161.01 (broader): ECI | Persuading, presenting and negotiating; Writing and editing; Analysing data and information | Medium |
| C035 | Secondary School Teacher | teaching and training others; helping and advising people; presenting, persuading and negotiating | Draft accurate. Evidence: O*NET 25-2031.00 (close): S | Teaching and training others; Helping and advising people; Persuading, presenting and negotiating | High |
| C036 | Instructional Designer | teaching and training others; designing products, spaces and systems; writing and editing | Draft accurate; digital design term. Evidence: O*NET 25-9031.00 (broader): SEI | Teaching and training others; Designing apps, websites and user experiences; Writing and editing | Medium |
| C037 | English as a Second Language Teacher | teaching and training others; helping and advising people; writing and editing | Draft accurate. Evidence: O*NET 25-3011.00 (close): SA | Teaching and training others; Helping and advising people; Writing and editing | High |
| C038 | School Counselor | helping and advising people; teaching and training others; working with communities | Draft accurate. Evidence: O*NET 21-1012.00 (close): SCE | Helping and advising people; Teaching and training others; Working with communities | Medium |
| C039 | Computer Science Lecturer | teaching and training others; researching and investigating; writing software and building apps | Draft accurate. Evidence: O*NET 25-1021.00 (close): SI | Teaching and training others; Researching and investigating; Writing software and building apps | High |
| C040 | Registered Nurse | caring for people's health; helping and advising people; organising information, records and processes | Draft accurate; matches SCI. Evidence: O*NET 29-1141.00 (close): SCI | Caring for people's health; Helping and advising people; Keeping information, records and procedures in order | High |
| C041 | Pharmacist | caring for people's health; scientific and laboratory work; helping and advising people | Draft 'helping' replaced by records (O*NET ISC; checking prescriptions). Evidence: O*NET 29-1051.00 (close): ISC | Scientific and laboratory work; Caring for people's health; Keeping information, records and procedures in order | High |
| C042 | Medical Laboratory Technologist | scientific and laboratory work; analysing data and information; caring for people's health | Draft 'caring' replaced by equipment (O*NET IRC; not patient-facing). Evidence: O*NET 29-2011.00 (close): IRC | Scientific and laboratory work; Analysing data and information; Working with tools, machines and equipment | High |
| C043 | Medical Records Specialist | organising information, records and processes; caring for people's health; interpreting laws, rules and policies | Draft 'caring' removed: records work is not patient care. Evidence: O*NET 29-2072.00 (close): CI | Keeping information, records and procedures in order; Working with laws, rules and regulations; Analysing data and information | High |
| C044 | Dietitian and Nutritionist | caring for people's health; helping and advising people; teaching and training others | Draft 'teaching' replaced by science (O*NET SI). Evidence: O*NET 29-1031.00 (close): SI | Caring for people's health; Helping and advising people; Scientific and laboratory work | High |
| C045 | Physical Therapist | caring for people's health; hands-on and physical work; helping and advising people | Draft 'hands-on' removed (term now means tools); exercise coaching added. Evidence: O*NET 29-1123.00 (close): SIR | Caring for people's health; Teaching and training others; Helping and advising people | Medium |
| C046 | Civil Engineer | designing products, spaces and systems; fieldwork and the natural environment; working with numbers and models | Draft accurate; matches RIC. Evidence: O*NET 17-2051.00 (close): RIC | Designing buildings, structures and physical products; Working outdoors and with the natural environment; Working with numbers and calculations | High |
| C047 | Mechanical Engineer | designing products, spaces and systems; hands-on and physical work; working with numbers and models | Draft accurate; identical to C048 (natural overlap). Evidence: O*NET 17-2141.00 (close): R (first type only) | Designing buildings, structures and physical products; Working with tools, machines and equipment; Working with numbers and calculations | Medium |
| C048 | Electrical Engineer | building and maintaining technical systems; working with numbers and models; designing products, spaces and systems | Draft 'technical systems' replaced by equipment (power, not computer, systems). Evidence: O*NET 17-2071.00 (close): R (first type only) | Working with tools, machines and equipment; Working with numbers and calculations; Designing buildings, structures and physical products | Medium |
| C049 | Environmental Engineer | fieldwork and the natural environment; scientific and laboratory work; designing products, spaces and systems | Draft accurate. Evidence: O*NET 17-2081.00 (close): IRC | Working outdoors and with the natural environment; Scientific and laboratory work; Designing buildings, structures and physical products | High |
| C050 | Biomedical Engineer | designing products, spaces and systems; caring for people's health; scientific and laboratory work | Draft accurate. Evidence: O*NET 17-2031.00 (close): IRC | Designing buildings, structures and physical products; Scientific and laboratory work; Caring for people's health | Medium |
| C051 | Mining Engineer | fieldwork and the natural environment; hands-on and physical work; working with numbers and models | Draft accurate. Evidence: O*NET 17-2151.00 (close): R (first type only) | Working outdoors and with the natural environment; Working with tools, machines and equipment; Working with numbers and calculations | Medium |
| C052 | Geological Engineer | fieldwork and the natural environment; scientific and laboratory work; researching and investigating | Draft accurate; O*NET first type is Realistic for the combined occupation. Evidence: O*NET 17-2151.00 (close): R (first type only) | Working outdoors and with the natural environment; Scientific and laboratory work; Researching and investigating | Medium |
| C053 | Telecommunications Engineer | building and maintaining technical systems; designing products, spaces and systems; working with numbers and models | Draft 'designing' replaced by equipment; no O*NET code. Evidence: No O*NET code | Setting up and running computer systems and networks; Working with tools, machines and equipment; Working with numbers and calculations | Provisional |
| C054 | Building Engineer | designing products, spaces and systems; hands-on and physical work; leading people and projects | Draft accurate; no O*NET code. Evidence: No O*NET code | Designing buildings, structures and physical products; Leading people and projects; Working with tools, machines and equipment | Provisional |
| C055 | Geotechnical Engineer | fieldwork and the natural environment; scientific and laboratory work; working with numbers and models | Draft accurate; no O*NET code. Evidence: No O*NET code | Working outdoors and with the natural environment; Scientific and laboratory work; Working with numbers and calculations | Provisional |
| C056 | Geophysicist | researching and investigating; working with numbers and models; fieldwork and the natural environment | Draft accurate; matches IRC. Evidence: O*NET 19-2042.00 (broader): IRC | Researching and investigating; Working with numbers and calculations; Working outdoors and with the natural environment | Medium |
| C057 | Private Law Specialist | interpreting laws, rules and policies; writing and editing; presenting, persuading and negotiating | Draft accurate; no O*NET code. Evidence: No O*NET code | Working with laws, rules and regulations; Writing and editing; Persuading, presenting and negotiating | Provisional |
| C058 | Public Law Specialist | interpreting laws, rules and policies; writing and editing; helping and advising people | Draft 'helping' replaced by communities (public service). Evidence: No O*NET code | Working with laws, rules and regulations; Writing and editing; Working with communities | Provisional |
| C059 | Management Information Systems Specialist (MIAGE) | organising information, records and processes; building and maintaining technical systems; leading people and projects | Draft accurate; no O*NET code. Evidence: No O*NET code | Keeping information, records and procedures in order; Setting up and running computer systems and networks; Leading people and projects | Provisional |
| C060 | Economist | analysing data and information; working with numbers and models; researching and investigating | Draft accurate; matches ICE. Evidence: O*NET 19-3011.00 (close): ICE | Analysing data and information; Working with numbers and calculations; Researching and investigating | High |
| C061 | Business Administration Specialist | running and growing a business; leading people and projects; organising information, records and processes | Draft identical to C032; money added. Evidence: No O*NET code | Running and growing a business; Leading people and projects; Managing money and financial information | Provisional |
| C062 | Laboratory Technician | scientific and laboratory work; organising information, records and processes; hands-on and physical work | Draft accurate; 'hands-on' clarified as equipment. Evidence: No O*NET code | Scientific and laboratory work; Keeping information, records and procedures in order; Working with tools, machines and equipment | Provisional |
| C063 | Sociologist | researching and investigating; working with communities; writing and editing | Draft accurate; matches ISA. Evidence: O*NET 19-3041.00 (close): ISA | Researching and investigating; Working with communities; Writing and editing | High |
| C064 | Community Relations Specialist | working with communities; presenting, persuading and negotiating; fieldwork and the natural environment | Draft accurate; outdoors kept for site-based work (uncertain). Evidence: No O*NET code | Working with communities; Persuading, presenting and negotiating; Working outdoors and with the natural environment | Provisional |

### C2. What changed from the first audit

- **Careers with a substantive change (18):** C009, C010, C012, C016, C021, C022, C028, C029, C030, C033, C041, C042, C043, C044, C045, C053, C058, C061.
- **The other 46** keep their draft assignment, apart from renamed terms.
- **By confidence:** 31 High, 21 Medium, 12 Provisional. All 12 provisional careers lack an O*NET code: C002, C003, C012, C053, C054, C055, C057, C058, C059, C061, C062, C064.
- **Special-attention groups:**

| Group | Finding |
|---|---|
| Data and AI (C001 to C008) | Assignments fit O*NET (Investigative and Conventional). C006 and C060, and C004 and C028, share sets: natural overlap |
| Software and Cybersecurity (C009 to C022) | The draft over-used "technical systems" and "designing". O*NET gives no Artistic or Realistic-first type for developers (IC or CI). Security careers share "Keeping computer systems and data safe" and differ in their second and third interest |
| Healthcare (C040 to C045, C062) | The draft gave patient care to two careers that do not provide it (C042 laboratory, C043 records). The four clinical careers now differ: nurse (records), pharmacist (science, records), dietitian (science), physical therapist (teaching) |
| Engineering (C046 to C056) | O*NET supports Realistic and Investigative. Only the first type could be read for C047, C048, C051 and C052. C053, C054 and C055 have no O*NET code |
| Law (C057, C058) | No O*NET code was mapped. Assignments are provisional and share two interests (laws, writing); they differ on persuasion against communities |
| Social Sciences (C060, C063) | Both fit their O*NET codes (ICE, ISA) |
| 14 careers added in v1.3.0 | 5 have O*NET codes. 9 are provisional, against 3 of the original 50 |

## Career differentiation

Count of distinct interest sets: 58 of 64 under the recommendation, and 58 under the first audit's draft, but with different pairs. That level is appropriate: careers that do similar work should be able to share interests, and the skill component (70% of the weight) separates them.

| Careers | Interests shared | Assessment | Action |
|---|---|---|---|
| C004 BI Analyst, C028 Management Analyst | all 3 (analysing, records, business) | Identical O*NET code (CIE) [O*NET] | Accept |
| C005 Data Engineer, C013 DevOps Engineer | all 3 (systems, software, records) | Both build and run data or delivery pipelines | Accept |
| C006 Statistician, C060 Economist | all 3 (numbers, research, analysing) | Both IC or ICE [O*NET]; economist's Enterprising element is not captured | Accept; possible future fourth interest is not recommended |
| C008 Database Administrator, C020 Network Administrator | all 3 (systems, safe, records) | Both run and secure infrastructure (CI, CRI) | Accept |
| C014 Cloud Engineer, C022 Security Engineer | all 3 (systems, software, safe) | Overlapping cloud and security engineering | Accept |
| C047 Mechanical Engineer, C048 Electrical Engineer | all 3 (equipment, numbers, physical design) | Both Realistic-first engineering design | Accept |
| C057 Private Law, C058 Public Law | 2 of 3 | Differ on persuasion against communities; both provisional | Review with a law lecturer |
| C040, C041, C044, C045 health careers | 2 of 3 among several pairs | Differences follow real work and O*NET second letters | Accept |
| C017, C018, C019, C021, C022 security careers | 2 of 3 among several pairs | All share "safe"; they differ on analysis, investigation, software, law or systems | Accept |
| Engineering C046 to C056 | 2 of 3 among many pairs | Natural for related engineering work; skills separate them | Accept |
| C032 Project Manager, C059 MIAGE, C061 Business Administration | 2 of 3 | C061 changed from identical to C032 by adding money | Accept |

There are 66 same-category pairs that share two of three interests. That is expected within categories and needs no action beyond the rows above.

## D. RIASEC classification

The six Holland types are official O*NET constructs [O*NET]. Placing this project's interests under them is this review's interpretation [Interpretation and Proposal]. Each interest has one primary type for display; secondary types are shown where the work clearly spans two.

| Type | Interests (primary) | Secondary links and uncertainty |
|---|---|---|
| Realistic | Setting up and running computer systems and networks; Working with tools, machines and equipment; Working outdoors and with the natural environment; Designing buildings, structures and physical products | Systems and networks also fit Conventional (O*NET gives CRI for network administrators). Physical design also fits Artistic (industrial designers ARI) |
| Investigative | Analysing data and information; Researching and investigating; Working with numbers and calculations; Scientific and laboratory work; Writing software and building apps | Numbers also fit Conventional. Software is **not** Realistic: O*NET gives IC or CI for developers and programmers, so the first audit's "Realistic/Investigative" label is corrected to Investigative/Conventional |
| Artistic | Creating visual art and graphics; Designing apps, websites and user experiences; Writing and editing | App design also fits Investigative (web and digital interface designers IAC). Writing also appears in Social and Enterprising work |
| Social | Teaching and training others; Caring for people's health; Helping and advising people; Working with communities | Communities also fits Enterprising (public engagement) |
| Enterprising | Leading people and projects; Running and growing a business; Persuading, presenting and negotiating | None |
| Conventional | Keeping information, records and procedures in order; Keeping computer systems and data safe; Working with laws, rules and regulations; Managing money and financial information | Systems safety also fits Investigative (information security analysts CI). Laws and money also fit Enterprising. The laws classification is uncertain: no O*NET lawyer code was mapped in this catalogue |

## E. Occupational evidence

### Sources used

| Source | What was used | Access on 2 November 2026 |
|---|---|---|
| [O*NET OnLine: Browse by Career Interest Types](https://www.onetonline.org/find/descriptor/browse/1.B.1/1) | Entry page to the six type lists | Read |
| [Investigative](https://www.onetonline.org/explore/interests/Investigative), [Realistic](https://www.onetonline.org/explore/interests/Realistic), [Artistic](https://www.onetonline.org/explore/interests/Artistic), [Social](https://www.onetonline.org/explore/interests/Social), [Enterprising](https://www.onetonline.org/explore/interests/Enterprising), [Conventional](https://www.onetonline.org/explore/interests/Conventional) | Interest code per occupation, read from table rows | Read with a web tool. Each code below was found in a quoted table row |
| [O*NET Web Services reference: occupation interests](https://services.onetcenter.org/reference/online/occupation/summary/interests) | Definition of the high-point code (interests with a standardized score of 50 or higher) | Read. The page does not define letter order |
| My Next Move profiles: [17-2051.00](https://www.mynextmove.org/profile/summary/17-2051.00), [17-2141.00](https://www.mynextmove.org/profile/summary/17-2141.00), [17-2071.00](https://www.mynextmove.org/profile/summary/17-2071.00), [17-2151.00](https://www.mynextmove.org/vets/profile/summary/17-2151.00) | Plain-language first interest | Read |
| `research/data/onet_mapping_audit.csv` (project file) | Which O*NET occupation each career maps to, and whether it is close or broader | Read |

### Interest codes found [O*NET]

| Code found | Careers |
|---|---|
| IC | C001 (15-2051.00), C006 (15-2041.00), C007 (15-1221.00), C009 and C013 (15-1252.00), C016 (15-1211.00), C019 (15-1299.06) |
| CI | C005 (15-1243.01), C008 (15-1242.00), C010 (15-1254.00), C015 (15-1251.00), C017 (15-1212.00), C043 (29-2072.00) |
| CIE | C004 (15-2051.01), C028 (13-1111.00) |
| CIR | C014 (15-1299.08), C022 (15-1299.05) |
| CRI | C020 (15-1244.00) |
| CEI | C029 (13-2051.00), C030 (13-2011.00) |
| ICR | C011 (15-1253.00), C018 (15-1299.04), C021 (15-1241.00) |
| ICE | C060 (19-3011.00) |
| IRC | C042 (29-2011.00), C049 (17-2081.00), C050 (17-2031.00), C056 (19-2042.00) |
| ISC | C041 (29-1051.00) |
| ISA | C063 (19-3041.00) |
| IAC | C024 (15-1255.00) |
| AC | C023 (27-1024.00) |
| AR | C025 (27-1025.00), C027 (27-1014.00) |
| ARI | C026 (27-1021.00) |
| ECI | C031 (13-1161.00), C034 (13-1161.01) |
| EC | C032 (13-1082.00) |
| ECS | C033 (13-1071.00) |
| S | C035 (25-2031.00) |
| SA | C037 (25-3011.00) |
| SEI | C036 (25-9031.00) |
| SCE | C038 (21-1012.00) |
| SI | C039 (25-1021.00), C044 (29-1031.00) |
| SCI | C040 (29-1141.00) |
| SIR | C045 (29-1123.00) |
| RIC | C046 (17-2051.00) |
| First type Realistic only | C047 (17-2141.00), C048 (17-2071.00), C051 and C052 (17-2151.00). My Next Move describes all three with the sentence it uses for Civil Engineers, whose code is RIC: "practical, hands-on problems and solutions" |

### Method notes and limits

- The type lists were read with a web-fetching tool. Its summaries sometimes wrongly reported codes as absent, so only codes confirmed in a quoted table row are used here. Scores were not available, only letters.
- O*NET defines the code as the high-point code (interests scoring 50 or higher). The pages read do not say what the letter order means. This review treats the first letter as the strongest by common convention, but the agreement check counts any letter in the code, not order.
- 8 careers map to a broader occupation (C005, C007, C013, C014, C024, C034, C036, C056); 44 map to a close match. The broader evidence is weaker, so those careers are Medium at best.
- O*NET describes US occupations. Interest patterns for the same job title in Guinea or elsewhere in Africa may differ. No African occupational interest data was found or used.

### Which assignments rely on what

| Basis | Careers |
|---|---|
| Recommendation agrees with all letters checked in a close O*NET match [O*NET + Interpretation] | 31 careers rated High |
| Broader O*NET match, first type only, or partial agreement [O*NET + Interpretation] | 21 careers rated Medium |
| No O*NET code; author judgement from the career record [Proposal] | C002, C003, C012, C053, C054, C055, C057, C058, C059, C061, C062, C064 |

## Interest descriptions (for the assessment form)

Each description is written so that a student can enjoy an activity without already having the professional skill. Suggested introduction for the form: *"Choose the kinds of work you enjoy or would like to do. You do not need the skills yet. Skills are asked separately."*

| Interest | Short explanation | Example | Related skill (not the same thing) |
|---|---|---|---|
| Analysing data and information | You enjoy looking at facts and figures to find patterns and answers | Finding out why sales went down from a table of numbers | Statistics, data visualization |
| Researching and investigating | You enjoy asking questions and finding out how or why things happen | Reading studies and testing an idea | Research methods |
| Working with numbers and calculations | You enjoy solving problems with numbers and formulas | Working out costs, measurements or probabilities | Engineering mathematics, statistics |
| Scientific and laboratory work | You enjoy experiments, samples and scientific tests | Testing water or soil samples in a lab | Chemistry, laboratory techniques |
| Keeping computer systems and data safe | You enjoy protecting computers and information from attacks and mistakes | Finding a weak password policy and fixing it | Network security |
| Setting up and running computer systems and networks | You enjoy installing, connecting and keeping computers and networks working | Setting up a school's Wi-Fi and servers | Linux, networking |
| Working with tools, machines and equipment | You enjoy practical work with tools, instruments or machines | Testing an electrical circuit or a prototype | CAD, laboratory techniques |
| Working outdoors and with the natural environment | You enjoy working outside, on sites, with land, rocks, water or nature | Visiting a mine or a river to take measurements | Geology, environmental science |
| Writing software and building apps | You enjoy writing code to make programs and apps | Building a small app that tracks homework | Python, Java |
| Creating visual art and graphics | You enjoy drawing, illustration, animation or visual style | Designing a poster or an animated character | Graphic design, illustration |
| Designing apps, websites and user experiences | You enjoy planning how a digital product looks and how people use it | Sketching screens for a banking app | UI design, user research |
| Designing buildings, structures and physical products | You enjoy planning how a building, structure or object is shaped and works | Drawing a bridge or a better chair | Product design, structural analysis |
| Writing and editing | You enjoy putting ideas into clear words | Writing a report, story or article | Technical writing, content writing |
| Teaching and training others | You enjoy explaining things and helping people learn | Tutoring a classmate in maths | Lesson planning |
| Caring for people's health | You enjoy looking after people who are ill or want to stay healthy | Helping patients recover | Patient care, pharmacology |
| Helping and advising people | You enjoy listening to people and helping them with problems or decisions | Advising a friend on which course to choose | Counseling |
| Working with communities | You enjoy working with groups, villages, neighbourhoods or the public | Organising a meeting about a local project | Community development, stakeholder engagement |
| Leading people and projects | You enjoy taking charge, planning and getting a team to finish on time | Leading a student club event | Project management |
| Running and growing a business | You enjoy commercial decisions, customers, markets and profit | Starting a small online shop | Business management |
| Persuading, presenting and negotiating | You enjoy convincing others, presenting ideas and reaching agreements | Pitching an idea to a panel | Communication |
| Keeping information, records and procedures in order | You enjoy accurate, well-organised files, data and step-by-step procedures | Keeping a club's membership records correct | Data modeling, medical coding |
| Working with laws, rules and regulations | You enjoy reading rules and laws and applying them to real cases | Checking whether a contract is fair | Contract law, taxation |
| Managing money and financial information | You enjoy budgets, accounts and decisions about money | Planning a budget for an event | Accounting, financial analysis |

Language check: no idioms, short sentences, common words. "User experiences" and "regulations" are the hardest terms; both are explained by the example. A French version would help many users in Guinea and should be produced with the interface work.

## Selection limit (1 to 5 interests)

| Question | Assessment |
|---|---|
| Why a limit | Today a learner can select all interests. Every career then scores the full 25 interest points, and the ranking equals the skills-only ranking (verified in the first audit). A limit removes that loophole without changing the formula |
| Do five interests differentiate | In a simulation with the recommended assignments (5,000 random selections), picking 5 interests gives at least one match to about 35 of 64 careers and leaves about 4.9 careers tied at the best interest match. Picking 8 touches about 48 careers and leaves the best-match group the same size (about 4.9). Picking 3 leaves about 6.8 tied at the top. Beyond 5, interests add points widely without narrowing the top. Random selections are only a rough guide; real learners choose related interests |
| Strongest first | The engine treats all selected interests equally, so ranking them in the interface would suggest an effect that does not exist. Recommended wording: "Choose up to 5 that you enjoy most" |
| Bias for diverse users | A learner with many genuine interests must leave some out, and careers linked only to the dropped interests lose up to 8.3 points each. With 23 interests across six types, 5 choices can still cover five types |
| Need for an experiment | Yes. No synthetic profile in either evaluation has more than 4 interests (eval64: 2 profiles with 1, 61 with 2, 47 with 3, 1 with 4), so the limit was never exercised. Before a hard cap, test real or realistic profiles with more interests, and compare a hard cap, a soft warning above 5, and no limit |

Recommendation: a soft limit first, with a gentle warning above 5. Use a hard cap only after the experiment. Not implemented.

## F. Remaining risks

| Risk | Concern | Mitigation or next step |
|---|---|---|
| Cultural and regional bias | O*NET interest codes describe US workers. Interest wording ("startup", "user experience") and job content may differ in Guinea and West Africa | Treat O*NET as a consistency check only; review assignments with a Guinean lecturer or career adviser; seek national occupational frameworks |
| Occupational classification differences | 8 careers map to broader O*NET occupations, 12 have none, and law careers have no mapping | Confidence column; provisional flag; lecturer review of law, MIAGE and the new engineering careers |
| Overlapping career interests | 6 identical pairs and many 2-of-3 overlaps within categories | Accepted as natural; skills (70% of weight) separate them; monitor recommendation ties |
| Vocabulary accessibility | Some terms remain long; international students may misread "regulations", "user experiences" | Descriptions with examples; French translation; usability test with students |
| Recommendation bias | Changing interests changes rankings for all 64 careers; the broad records term (18 careers) and the Conventional-heavy IT terms may favour IT and business careers for organised learners; the career-ID tie-break still decides many ties | New evaluation after any change (eval64_v2); exposure and tie diagnostics rerun; tie-break question handled separately |
| Evidence quality | Codes were read through a web tool from list pages; no scores; letter order undefined on the pages read | Spot-check a sample against the O*NET database files before implementation |
| Scope of change | Applying this changes the interest data of the original 50 career records | Frozen snapshots keep the old data; dataset version 1.4.0; your explicit approval |

## G. Approval checklist

| # | Decision | Options |
|---|---|---|
| 1 | Final interest vocabulary | Approve the 23 interests in section B2, or amend specific terms (for example drop "Managing money and financial information", or keep the first audit's single design term) |
| 2 | Final career-interest assignments | Approve the 64 recommendations in section C, possibly approving High and Medium now and holding the 12 provisional careers for lecturer review |
| 3 | RIASEC grouping | Approve the grouping in section D for display only (it does not affect scoring), or show interests ungrouped |
| 4 | Interest descriptions | Approve the wording in the descriptions table, and decide whether to add a French version |
| 5 | Selection limit | Soft warning above 5 (recommended), hard cap of 5, or no limit; in every case a separate experiment before a hard cap |
| 6 | O*NET validation strategy | Accept the list-page evidence as is, or first spot-check codes against the O*NET database files, and decide whether to seek African occupational sources |
| 7 | Migration approach | Map old interest names to new ones in saved sessions, links and API input (first audit section 7, updated with this review's renames and splits); bump the dataset to v1.4.0; leave frozen snapshots and reports untouched; run a new separate evaluation afterwards |

Nothing has been implemented. The formula, the engine, the interface, all career records and all frozen evaluation data and reports are unchanged.
