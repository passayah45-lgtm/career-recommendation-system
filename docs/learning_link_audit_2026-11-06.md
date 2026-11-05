# Learning link audit, 6 November 2026

Scope: the 40 resources marked search_index_confirmed (never opened by src/data/url_checker.py) and R093 (Microsoft Learn, possible paid labs). Requested by the project owner. Lecturer review pending.

## Method

1. Each URL was opened with a web tool. The workspace shell cannot reach external sites, and the web tool opens only URLs that appeared in a web search result, so each URL was first found by search.
2. For each page: did it load, is it the intended material, is it free, is registration needed, are there paid extras, does it teach the skill.
3. A resource was replaced only if the replacement policy applied (broken, removed, unrelated, unavailable, paid core material, off skill). Working resources were kept.
4. A URL the tool could not open is reported for manual review. Nothing was guessed.

## Summary

| Result | Count | Resources |
|---|---|---|
| Checked | 41 | 40 previously unopened plus R093 |
| Verified working, kept | 37 | 36 of the 40, plus R093 |
| Broken or removed, replaced | 1 | R048 |
| Unsuitable, replaced | 1 | R120 |
| Kept, needs manual review | 2 | R125, R127 |

The second pass (6 November 2026, after provisional approval) moved R013 to verified, replaced R120 and pointed R048 to a teaching chapter instead of the book's introduction page.

## Replacements

Both are recorded in data/resource_link_replacements.csv. The frozen catalogues in data/evaluation/ still hold the original links. IDs, skills, free status, types and levels are unchanged.

### R048 human resource management (book, beginner): removed

| | Before | After |
|---|---|---|
| Title | Human Resource Management | Human Resources Management: The Role of Human Resources |
| Provider | University of Minnesota Libraries Publishing | Lumen Learning (LibreTexts, Citrus College) |
| URL | https://open.lib.umn.edu/humanresourcemanagement/ | https://biz.libretexts.org/Courses/Citrus_College/Human_Resources_Management/01%3A_The_Role_of_Human_Resources |
| Evidence | Page says "This textbook has been removed from the University of Minnesota Libraries collection" | Chapter 1 of an open HR management textbook remixed from Lumen Learning, CC BY 4.0, shown without sign-in or paywall. Lessons 1.1 to 1.10: defining HRM, HR today, functions of HRM, metrics, training and development, working in HR |

The first candidate (the Lumen book's "About This Course" page) was rejected: it only introduces the course and holds no teaching content.

### R120 geophysical methods (book, intermediate): unsuitable

| | Before | After |
|---|---|---|
| Title | Geophysics for Practicing Geoscientists (GPG) source | Geophysics for Practicing Geoscientists (GPG) |
| Provider | University of British Columbia Geophysical Inversion Facility | University of British Columbia Geophysical Inversion Facility (GeoSci.xyz) |
| URL | https://github.com/ubcgif/gpg | https://gpg.geosci.xyz/ |
| Evidence | Source files of the book on GitHub, not the readable book. The link also redirected to github.com/geoscixyz/gpg | The same book, "a learning resource for applied geophysics", CC BY 4.0, no sign-in or paywall. Chapters: Foundations, Physical Properties, Magnetics, Seismic, Ground Penetrating Radar, Electromagnetic Methods, DC Resistivity, Induced Polarization, Gravity |

## R093 Microsoft Learn: kept

Catalogue skill: security monitoring (not general cloud computing).

- Learning path "Create detections and perform investigations using Microsoft Sentinel" loads: 8 modules, intermediate, no price for the learning content. The reading is free.
- The free Microsoft Learn sandbox is no longer offered. Two Microsoft Q&A threads say so (12 February 2026 and 26 May 2026, community members and a volunteer moderator). The official Learn FAQ could not be opened with the tool.
- Hands-on practice therefore needs the learner's own Azure subscription. Microsoft's Sentinel billing page: "the first 10 GB/day ingested using the Analytics logs plan is free for 31 days". Automation and machine learning charges "are still applicable during the free trial".
- Azure for Students: "$100 credit to use on Azure services within 12 months", "No credit card required", for full-time university students. With it, an eligible student can do the labs at no cost. It is not available to everyone, and one learner reported that Azure sign-up was not offered in their country.
- Free alternative for hands-on security monitoring: Security Onion, "a free and open platform built by defenders for defenders" (network visibility, host visibility, log management, case management). Documentation under CC BY 4.0. A paid Pro edition, appliances and training exist, but the platform and documentation are free. Not added to the catalogue, because the catalogue keeps one resource per skill.
- Decision: the core learning is free, so R093 stays under the policy. Its existing note already says the labs may need an Azure subscription. The row was not edited because it is compared field by field with the frozen original.

## Kept, needs manual review

| ID | Skill | What was verified | What could not be verified |
|---|---|---|---|
| R125 | radio frequency engineering | The same book's Open Textbook Library page (open.umn.edu/opentextbooks/textbooks/radio-systems-engineering) loads: "made freely available", CC BY-NC 4.0 | The catalogue URL ending textbooks/1542 could not be opened and never appears in search results. Option: relink to the verified page of the same record |
| R127 | reinforced concrete design | The older address of the same page (ocw.mit.edu/courses/civil-and-environmental-engineering/1-054-.../lecture-notes/) loads the 1.054 lecture notes: 26 sessions from design criteria for reinforced concrete to seismic retrofit. The course resources page loads with a Creative Commons licence | The current-format catalogue URL ending pages/lecture-notes/ could not be opened. Low risk: OCW serves its pages at this format |

## Resolved in the second pass

| ID | Skill | Evidence |
|---|---|---|
| R013 | career development | The exact catalogue URL loads the course page "Careers education and guidance": "Free statement of participation on completion", can start "without signing-up", Level 2, 8 hours of study. It is the course description page with links to the sections, the same pattern as R033 and R038 |

## Verified working, kept

| ID | Skill | Evidence of free access |
|---|---|---|
| R008 | assessment design | OpenLearn "Free course", can start without signing up, free statement of participation |
| R020 | communication | University of Minnesota open textbook, CC BY-NC-SA 4.0 |
| R022 | counseling | OpenLearn Create study session, CC BY-NC-SA 2.0 |
| R031 | design thinking | OpenLearn free course, no sign-up to start |
| R033 | digital marketing | OpenLearn free course |
| R038 | environmental science | OpenLearn free course, free account to track progress |
| R041 | exercise science | Pressbooks open textbook, CC BY-NC 4.0 |
| R050 | illustration | Official Inkscape tutorials, no sign-in or payment |
| R115 | rock mechanics | MIT OCW 12.524 lecture notes and problem sets |
| R116 | mine safety | ILO code of practice, free PDF |
| R117 | mine planning | Penn State MNG 230 lesson 9.1 Mine Planning, CC BY-NC-SA 4.0 |
| R118 | geology | BCcampus "Download for free", CC BY 4.0 |
| R119 | soil mechanics | MIT OCW 1.361 lecture notes |
| R121 | foundation design | Author's free PDF (2023), copying encouraged |
| R122 | physics | OpenStax "for free in web view or PDF", CC BY-NC-SA |
| R123 | telecommunication systems | MIT OCW 6.02: 23 lecture note PDFs on channel coding, modulation, networks |
| R124 | signal processing | MIT OCW 6.003: notes, videos, problem sets, CC BY-NC-SA 4.0 |
| R126 | construction management | Pressbooks open textbook (Metropolitan State University of Denver), CC BY 4.0 |
| R128 | legal research | CALI open textbook, CC BY-SA 4.0 |
| R129 | contract law | OpenStax "This free textbook", chapter 7 contract law |
| R130 | constitutional law | OpenStax free textbook, chapter 4 Constitution. Points to the first edition while R129 and R131 use 2e; kept because it works |
| R131 | administrative law | OpenStax free textbook, chapter 10 administrative law and regulatory agencies |
| R132 | ohada business law | OHADA Uniform Acts with direct download links in English, no paywall |
| R133 | public finance | LibreTexts chapter 13 from OpenStax, CC BY 4.0 |
| R134 | information systems management | University of Houston Pressbooks, CC BY-NC-SA 4.0 |
| R135 | economics | OpenStax "for free in web view or PDF", CC BY-NC-SA 4.0 |
| R136 | business management | OpenStax "for free in web view or PDF", CC BY-NC-SA 4.0 |
| R137 | laboratory safety | WHO manual, download 3 MB, CC BY-NC-SA 3.0 IGO |
| R138 | quality control | WHO handbook, download 5.9 MB, no fee. No licence named on the page |
| R139 | sociology | OpenStax "for free in web view or PDF", CC BY-NC-SA 4.0 |
| R140 | qualitative research | Oregon State open textbook, CC BY-SA 4.0 |
| R141 | stakeholder engagement | IFC PDF (2007), IFC "encourages use and distribution" |
| R142 | community development | Centennial College open educational resource, CC BY-NC-SA |
| R143 | conflict resolution | Portland State "open access textbook", CC BY-NC 4.0 |
| R144 | social impact assessment | IAIA guidance page with a PDF download, no payment or membership stated |

## What did not change

- Recommendation scoring, weights (55/15/25/5), ranking and tie-breaks.
- Career, skill and interest identifiers, and every career-to-skill link.
- Resource IDs, skill mappings, free status, types and levels.
- Frozen evaluation catalogues and reports.
- The "Free learning resource" label. Verification dates stay in the data and are not shown on cards.
- The assistant feature flag, off by default.
