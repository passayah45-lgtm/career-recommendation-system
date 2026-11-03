# Career Assessment interests: interface and African relevance review

Review date: 3 November 2026. Live version: v1.4.0 (commit ead00a2). **Review only.** No application code, dataset, taxonomy, scoring rule, frozen file or deployment was changed. This document is uncommitted. Lecturer feedback is still pending, and nothing here claims lecturer approval.

Labels used:
- **[Verified]** checked in the code, by running it, or in a cited source.
- **[Proposal]** this review's recommendation.
- **[Unverified]** an assumption to confirm, for example with the lecturer.

Screenshots were taken from local runs of the previous version (b861aed), the current version, and two scratch prototypes. The prototypes are not part of the application.

## 1. Assessment of the current interface (v1.4.0)

[Verified] The interest section shows all 23 interests as permanent checkboxes in two columns, under six RIASEC headings. Each interest has a help tooltip with its explanation, example and related skill. Above the list are an update notice and two captions.

| Aspect | Finding |
|---|---|
| Screen space | The section is the largest part of the form. On a 1280 x 900 desktop it fills more than one full screen, and on a phone the two columns stack into one long list |
| Scanning | 23 long labels in two columns are hard to scan. The eye jumps between columns and headings |
| Descriptions | Hidden behind small question-mark icons. Hovering does not work on phones, where a tap is needed |
| Selection feedback | No count while choosing. The form only reacts on "Save", so the more-than-5 warning appears after saving |
| Group names | "Realistic", "Investigative", "Enterprising" and "Conventional" are Holland's technical terms. Many students will not know them |
| Strengths to keep | Plain-language interest names, explanations with examples, related skills, the skills-versus-interests explanation, the soft warning, migration notes for old sessions |

## 2. Comparison with the previous interface (up to b861aed)

[Verified from Git history] The previous interest section was a single `st.multiselect` labelled "Kinds of work that interest you". It listed 20 bare, lowercase words (analysis, business, design, technology and so on), searchable, with chips for the chosen items. It took about one line of height until opened.

| Aspect | Previous (v1.3.0) | Current (v1.4.0) |
|---|---|---|
| Component | One searchable dropdown | 23 checkboxes in two columns |
| Height when closed | One input row | More than one screen |
| Selected items | Chips with a remove button | Ticked boxes spread over the list |
| Search | Yes, by typing | No |
| Descriptions | None | Tooltip per interest |
| Grouping | None | Six RIASEC headings |
| Vocabulary | 20 vague words, some abilities or category names | 23 described activities |
| Select-all loophole | **Present.** Streamlit 1.65 adds a "Select all" option to every multiselect (visible in the screenshot), and selecting all interests makes every career score the full 25 interest points | Not possible with checkboxes, but the soft warning only appears after saving |

**Keep from the previous design:** the single compact dropdown, typing to search, chips with a remove button, and very little vertical space.

**Improve on it:**
- hide "Select all".
- show grouping and descriptions.
- add a live counter.
- keep the new vocabulary.

## 3. Interface options

| | Option 1: previous dropdown | Option 2: improved searchable multiselect (recommended) | Option 3: compact popover with grouped pills |
|---|---|---|---|
| What it is | The v1.3.0 `st.multiselect` with the new 23 names | One `st.multiselect` with a short group tag before each name ("Analytical · Analysing data and information"), "Select all" off, substring search, a live counter, the soft warning, a card describing each chosen interest, and an expander listing all 23 with descriptions | A "Choose interests" button that opens a panel of grouped clickable pills. The chosen items and a counter show below |
| Advantages | Smallest change, familiar | Compact. Searchable. Grouping is visible in each option. Descriptions are shown for what the student chose. Chips are removable. Works on phones. Uses built-in components only | Very compact when closed. Students can see all options by group in one click |
| Disadvantages | No grouping or descriptions. "Select all" is shown unless disabled | Long names make long options (truncated on phones unless wrapped). Group order is only a sort order, with no true headings inside the dropdown | When open, it shows every interest at once, close to the checkbox layout you rejected. Descriptions are harder to attach. Its behaviour inside the existing form needs testing |
| User experience | Fast but under-explained | Type or scroll, pick, read what you picked, adjust | Click, scan the pills, pick |
| Mobile | Good | Good: full-width dropdown and chips. Labels may be cut on a 390 px screen, which the `wrap` setting or dropping the group tag on small screens can address | Pills wrap well, but the open panel is tall |
| Accessibility | Keyboard and screen reader through Streamlit's standard widget | Same widget. The description cards are plain text, readable without hovering, which suits touch screens | Pills are keyboard-accessible. The popover adds one more step for screen readers |
| Complexity | Very low | Low to medium (see below) | Medium |

**[Proposal] Recommend option 2.** It returns to the dropdown you preferred and fixes its weaknesses. It also removes the scattered checkbox layout and puts the descriptions where students need them: next to what they chose.

**Implementation notes for option 2:**
1. Settings: `select_all=False`, which closes the loophole. `filter_mode="contains"`: the default fuzzy search returned "Researching and investigating" for "desig" in testing. `wrap=True` for the chips.
2. Group tags: plain words instead of RIASEC jargon, with RIASEC kept in the documentation. Practical (Realistic), Analytical (Investigative), Creative (Artistic), People (Social), Leading (Enterprising), Organised (Conventional). Options are sorted by group.
3. **Live counter and warning.** Widgets inside a Streamlit form do not react until the form is submitted. To update the counter, the description cards and the warning while the student chooses, the interest dropdown must sit outside the form. Alternatively, the form can be replaced by ordinary widgets and a Save button. The workflow (four sections, one save, the same saved profile and session file) stays the same.
4. The update notice can become a one-line caption, plus the migration note for old sessions only when it applies.
5. No change to stored values, scoring or ranking. The same interest keys are saved.

## 4. Proposed interest taxonomy: African and Guinean relevance

### 4.1 Context (sources in section 11)

| Fact | Source | Status |
|---|---|---|
| Agriculture is about 32% of Guinea's GDP and more than 60% of jobs | World Bank, Guinea Economic Update 2026 (press release, 7 October 2026) | [Verified] |
| 2025 growth was driven by mining, especially bauxite. Iron ore exports from Simandou are expected to raise growth in 2026 to 2028 | Same source | [Verified] |
| The World Bank calls for non-mining private sector growth: agri-food value chains, post-harvest logistics, SME finance, and local content linked to mining | Same source | [Verified] |
| Simandou 2040 targets infrastructure modernisation, industrialisation and value chains, economic diversification, and better living standards | AfDB announcement, as reported by Devdiscourse | [Verified] (secondary source) |
| Agenda 2063 frameworks include agricultural transformation (CAADP), education and TVET for youth employment, and science, technology and innovation (STISA) | African Union, "Africa's own development framework" page | [Verified] |
| ISCO-08 has 10 major groups, including group 6 "Skilled Agricultural, Forestry and Fishery Workers" | ILO, ILOSTAT classification page | [Verified] |
| Mobile money is widely used for payments in Guinea | Not checked in this review | [Unverified] |

**Distinction:**
- **International categories:** ISCO-08 occupation groups and O*NET interest types.
- **Guinea-specific context:** the World Bank and Simandou 2040 material. Using it to choose examples and new careers is this review's proposal.

### 4.2 Key finding: interests only work through careers

[Verified] An interest affects scores only if careers list it. The catalogue has 64 careers in 10 categories. Searching their titles, descriptions and skills finds:

| Area | Careers in the catalogue |
|---|---|
| Agriculture, agribusiness, livestock | None (one dietitian mentions food) |
| Fisheries | None |
| Energy and renewable energy | Electrical Engineer only |
| Public administration and governance | Public Law Specialist only |
| International development and NGOs | None |
| Public health | None |
| Banking, microfinance, mobile money | None (Accountant and Financial Analyst are general finance) |
| Translation and interpreting | None |
| Mining and geology | Mining, Geological and Geotechnical Engineers, Geophysicist, Community Relations Specialist |
| Telecommunications | Telecommunications Engineer |

Adding an interest such as "Growing food and farming" today would let students select it, but no career would gain a single point. That would mislead students. **[Proposal] New interests must be added together with careers that carry them.** This makes African relevance mainly a catalogue question. The interest list itself already covers most activities.

### 4.3 Review of the 23 interests

| Current interest | Issue | Proposed interest or change | African and Guinean relevance | Decision |
|---|---|---|---|---|
| Setting up and running computer systems and networks | Telecom networks are not named | Setting up and running computer and telecom networks | Mobile networks and digital infrastructure (Telecommunications Engineer exists) | Rename (label) |
| Working with tools, machines and equipment | Fine. Example is lab-centred | Keep. Example: "Maintaining a generator, a solar installation or a mining machine" | Mining, energy and maintenance work | Keep, local example |
| Working outdoors and with the natural environment | Does not mention farms, forests or the sea | Keep the name. Description: "on farms, sites, mines, in forests, rivers or at sea" | Agriculture, mining, environment, fisheries | Keep, wider description |
| Designing buildings, structures and physical products | Fine | Keep. Example: "Planning a road, a bridge or a school building" | Infrastructure (Simandou 2040 targets) | Keep, local example |
| Analysing data and information | Fine | Keep. Add a second example, for example "Studying which products sell best at a market" | Data and AI, business, agriculture | Keep |
| Researching and investigating | Fine | Keep | All sectors | Keep |
| Working with numbers and calculations | Fine | Keep | All sectors | Keep |
| Scientific and laboratory work | Fine | Keep. Example: "Testing the water quality of a town" | Public health, mining, environment | Keep, local example |
| Writing software and building apps | Fine | Keep. Example: "Building a mobile app for farmers or a school" | Digital transformation | Keep, local example |
| Creating visual art and graphics | Fine | Keep | Creative and cultural work | Keep |
| Designing apps, websites and user experiences | "User experiences" is hard for many readers | Keep the name, or use "Designing apps and websites that people find easy to use". Example: "Designing the screens of a mobile payment app" | Digital services | Keep, clarify (lecturer decision) |
| Writing and editing | Languages are not represented | Keep. See the "languages" candidate below | French and national languages, media | Keep |
| Teaching and training others | Fine | Keep. Example could include "training adults in a literacy programme" | Education, teacher training, TVET (Agenda 2063) | Keep |
| Caring for people's health | Public and community health is not visible | Keep. Description adds "or keeping communities healthy" | Public health | Keep, wider description |
| Helping and advising people | Fine | Keep | Counselling, social work | Keep |
| Working with communities | NGOs and development projects are not named | Keep. Description adds "development projects and associations". Example: "Organising a village water project with an NGO" | Community development, international development | Keep, local example |
| Leading people and projects | Fine | Keep | All sectors, NGOs | Keep |
| Running and growing a business | The example (online shop) does not reflect small and informal businesses | Starting and running a business. Example: "Running a small shop or trading business" | Entrepreneurship, SMEs (World Bank priority) | Rename (label), local example |
| Persuading, presenting and negotiating | Fine | Keep | Business, law, community relations | Keep |
| Keeping information, records and procedures in order | Fine | Keep | Administration, health records | Keep |
| Keeping computer systems and data safe | Fine | Keep | Digital transformation | Keep |
| Working with laws, rules and regulations | Public service is missing | Keep. See the "public services" candidate below | Law and justice, regulation, mining law | Keep |
| Managing money and financial information | Fine | Keep. Example: "Managing a savings group or a mobile money account" | Banking, microfinance, mobile money [Unverified] | Keep, local example |

**New interests worth considering, each only together with new careers:**

| Proposed interest | International basis | Guinea relevance | Careers that would carry it (examples to be approved) | Decision |
|---|---|---|---|---|
| Growing food, farming and working with animals | ISCO-08 major group 6, agronomists (ISCO 2132), O*NET Realistic | Agriculture is more than 60% of jobs (World Bank). Agri-food value chains are a stated growth priority | Agronomist, Agricultural Engineer, Agribusiness Manager, Veterinarian, Fisheries and Aquaculture Officer | **Add in the catalogue expansion** (highest priority) |
| Serving the public and improving public services | ISCO 1112 senior government officials, 2422 policy administration professionals | Public administration and decentralisation | Public Administration Officer, Policy Analyst, Local Government Officer | **Add in the catalogue expansion** |
| Working with languages and translation | ISCO 2643 translators, interpreters and other linguists | French plus national languages, regional and international organisations | Translator and Interpreter (ESL Teacher exists) | **Consider later** |

**Areas that need careers but no new interest:**

| Area | Existing interests that already describe the activity |
|---|---|
| Energy | tools, designing buildings and structures, outdoors |
| Banking and microfinance | money, persuading |
| NGOs and international development | communities, leading |
| Public health | caring for health, communities |
| Mining | outdoors, tools, laws |

**Avoiding stereotypes:**
- Interests describe activities, never nationality or background.
- Examples should mix urban and rural, local and international, and modern and traditional settings. For example, a mobile app as well as a market stall, a mining site as well as an office.
- Students should never be steered towards local or manual careers because of where they live.

### 4.4 International relevance

Every proposed interest describes an activity recognised in ISCO-08 or O*NET, so the taxonomy stays usable for students aiming at international careers. The changes are mostly local examples and wider descriptions. They do not narrow any interest to Guinea.

## 5. Impact on career recommendations

| Change | Effect on scores | Evidence or reasoning |
|---|---|---|
| Option 2 interface | **None.** The same values are saved and scored | [Verified] The interface only changes how the list is selected. Hiding "Select all" removes one way to defeat the interest component |
| New descriptions and examples | None | Descriptions are not used in scoring |
| Label renames (rows marked "Rename") | None if mapped one-to-one, but stored keys currently come from the labels | [Verified] in `src/data/interest_taxonomy.py`. **[Proposal]** First give each interest a fixed internal ID, so labels can change without touching `careers.csv`, sessions or the API |
| New interests without careers | None for any career, but misleading for students | Section 4.2 |
| New interests with new careers | Rankings change for every profile, because more careers compete | Needs a new dataset version, a new frozen snapshot and a new evaluation. eval64_v1 and the v1.4.0 study stay frozen |

The scoring weights stay 0.55, 0.15, 0.25 and 0.05. Ranking, tie-breaking and explanations are unchanged in every option.

## 6. Implementation roadmap

| Step | Content | Data or score change | Approval |
|---|---|---|---|
| A. v1.4.1 interface | Option 2 dropdown, plain group tags, "Select all" off, substring search, live counter, soft warning, cards for the chosen interests, expander with all descriptions. Tests updated | No | Your approval |
| B. Stable interest IDs | Internal IDs separate from labels, with migration kept | No | Your approval |
| C. v1.5.0 wording | Local examples, wider descriptions, the two label renames, plain group names. French drafts updated for review | No score change if mapped one-to-one | Lecturer (decisions 1, 4, 5) |
| D. v1.6.0 catalogue expansion | Agriculture and public-service careers with their skills, resources and three interests each, plus the two new interests | Yes | Lecturer, then a new evaluation (eval64_v2 design) |

## 7. Lecturer review requirements

1. Whether to add "Growing food, farming and working with animals" and "Serving the public and improving public services", and which careers carry them.
2. The renamed labels, the plain-language group names, and the local examples, including a check for stereotypes.
3. The list of new careers and their sources (ISCO-08 codes, and national references where available).
4. The French wording, reviewed by a qualified French speaker.
5. The evaluation plan for the expanded catalogue.

## 8. Recommended next steps

1. **[Proposal]** Approve step A, the option 2 interface. It answers your feedback without changing data or scores and can be released on its own.
2. **[Proposal]** Approve step B, so later wording changes are safe.
3. Send sections 4 and 7 to the lecturer with the existing review package.
4. Plan step D, the agriculture and public-service careers, once the lecturer agrees, followed by a new evaluation.

## 9. Files

- This document is the only file written in the repository (uncommitted).
- The scratch prototype and screenshots are outside the repository:
  - `/tmp/claude-0/-home-claude/c9a6a79c-1fcf-5964-b3a6-1708a08eb44d/scratchpad/proto/proto.py`
  - `/tmp/claude-0/-home-claude/c9a6a79c-1fcf-5964-b3a6-1708a08eb44d/scratchpad/shots/`

## 10. What was not done

No code, data, taxonomy, scoring, frozen file, commit, push or deployment changes. The live application was not opened from this workspace. The screenshots come from local runs of the same code.

## 11. Sources

- World Bank, Guinea Economic Update 2026 (press release, 7 October 2026): https://www.banquemondiale.org/fr/news/press-release/2026/10/07/guinea-economic-update-2026-natural-resource-wealth-private-sector-growth-jobs
- ILO, ILOSTAT, International Standard Classification of Occupations: https://ilostat.ilo.org/methods/concepts-and-definitions/classification-occupation/
- Devdiscourse, "AfDB Backs Guinea's $200bn Simandou 2040 Plan to Transform Economy": https://www.devdiscourse.com/article/arts/3778546-afdb-backs-guineas-200bn-simandou-2040-plan-to-transform-economy
- African Union, "Africa's own Development Framework – Agenda 2063": https://oau60.au.int/en/africas-own-development-framework-agenda-2063
- O*NET interest codes and ISCO references for existing careers: `docs/interest_taxonomy_second_review.md`, section E

## Follow-up

Step A (the option 2 interface) was approved by the owner and implemented locally on 3 November 2026. Details are in `docs/interest_taxonomy_implementation.md`, section 10. The taxonomy proposals in this review (sections 4 to 8) are not implemented.

