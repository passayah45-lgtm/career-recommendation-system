# Link check of the 30 new resources (R115 to R144)

Checked 1 November 2026. Raw checker output: `research/data/url_check_expansion_2026-11-01.json`.

## 1. Project link checker (`src/data/url_checker.py`)

The checker ran on all 30 URLs with its normal settings (HEAD, then GET, 15 s timeout, 1.5 s between requests to one host).

| Outcome | Count | Meaning |
|---|---|---|
| reachable | 0 | |
| failed (404 or 410) | 0 | No URL was shown to be gone |
| blocked | 1 | R120 (github.com): HTTP 403 from the workspace proxy |
| inconclusive | 29 | "Tunnel connection failed: 403 Forbidden": the workspace network policy refused the connection before it reached the site |

All 30 results come from the network policy of the environment the check ran in, not from the sites. The checker could not test these links from here, so no row was changed to `http_checked`. The links stay `search_index_confirmed`.

**To finish this check,** run the checker from a machine with normal internet access:

```
python -m src.data.url_checker --output reports/url_check.json
```

Add `--apply` to mark reachable resources as `http_checked`.

## 2. Secondary check with a web tool

Each URL was opened with a web-fetching tool the same day. That tool reads the page, so it shows whether the page exists and what it contains. It is not the project checker and does not replace it.

| ID | Skill | Page loaded | Title seen | Notes |
|---|---|---|---|---|
| R115 | rock mechanics | Yes | Mechanical Properties of Rocks (MIT OCW 12.524) | Free lecture notes |
| R116 | mine safety | Yes | Code of practice on safety and health in opencast mines (ILO) | PDF 3.46 MB, no login |
| R117 | mine planning | Yes | Module 9: Surface Mining, MNG 230 (Penn State) | |
| R118 | geology | Yes | Physical Geology 2nd Edition (BCcampus) | CC BY 4.0 |
| R119 | soil mechanics | Yes | Advanced Soil Mechanics (MIT OCW 1.361) | Graduate level |
| R120 | geophysical methods | Yes | Repository geoscixyz/gpg, "Geophysics for Practicing Geoscientists" | The stored URL (github.com/ubcgif/gpg) now redirects to geoscixyz/gpg. CC BY 4.0 |
| R121 | foundation design | Yes | Basics of Foundation Design, electronic edition March 2023 (Fellenius) | PDF |
| R122 | physics | Yes | University Physics Volume 1 preface (OpenStax) | CC BY-NC-SA 4.0 |
| R123 | telecommunication systems | Yes | 6.02 Digital Communication Systems lecture notes (MIT OCW) | |
| R124 | signal processing | Yes | 6.003 Signals and Systems (MIT OCW) | |
| R125 | radio frequency engineering | Yes | Radio Systems Engineering, Revised First Edition (Ellingson, Virginia Tech) | CC BY-NC 4.0 |
| R126 | construction management | Yes | Introduction to Construction Project Management (McGary) | CC BY 4.0 |
| R127 | reinforced concrete design | Yes | 1.054 Mechanics and Design of Concrete Structures lecture notes (MIT OCW) | |
| R128 | legal research | Yes | Sources of American Law, preface (CALI) | CC BY-SA 4.0; no bot check this time |
| R129 | contract law | Yes | Business Law I Essentials 2e, ch. 7 (OpenStax) | |
| R130 | constitutional law | Yes | Business Law I Essentials, ch. 4 (OpenStax) | First edition page; no redirect to 2e |
| R131 | administrative law | Yes | Business Law I Essentials 2e, ch. 10 (OpenStax) | |
| R132 | ohada business law | Yes | OHADA.com, OHADA Uniform Acts | 11 current and 7 repealed acts, each with a PDF download; page partly in French |
| R133 | public finance | Yes | 13: Government Budgets and Fiscal Policy (LibreTexts) | CC BY 4.0 |
| R134 | information systems management | Yes | Foundations of Management Information Systems (UH Libraries) | CC BY-NC-SA 4.0 |
| R135 | economics | Yes | Principles of Economics 3e preface (OpenStax) | CC BY-NC-SA 4.0 |
| R136 | business management | Yes | Principles of Management preface (OpenStax) | CC BY-NC-SA 4.0 |
| R137 | laboratory safety | Yes | Laboratory biosafety manual, 4th edition (WHO) | Download 3 MB. The stored URL uses "/I/" in capitals; it loads as it is |
| R138 | quality control | Yes | Laboratory quality management system: handbook (WHO) | Download 5.9 MB |
| R139 | sociology | Yes | Introduction to Sociology 3e preface (OpenStax) | CC BY-NC-SA 4.0 |
| R140 | qualitative research | Yes | Introduction to Qualitative Research Methods (Hurst, Oregon State) | CC BY-SA 4.0 |
| R141 | stakeholder engagement | Yes | Stakeholder Engagement: A Good Practice Handbook (IFC, 2007) | PDF |
| R142 | community development | Yes | Community Development Practice (Centennial College) | CC BY-NC-SA |
| R143 | conflict resolution | Yes | Navigating the Space Between Us (Gould, Portland State) | The page names both CC BY-NC 4.0 and CC BY-NC-SA 4.0; the notes now say to treat it as CC BY-NC-SA 4.0 |
| R144 | social impact assessment | Yes | Social Impact Assessment Guidance (IAIA, 2015) | PDF download; the page calls the IAIA library open access but does not say "free" on the PDF itself; notes corrected |

## 3. Result

- No link was found to be broken, so no link was replaced.
- Notes for all 30 rows now record both checks. The notes for R143 and R144 were also corrected.
- **Unresolved:** all 30 links still need a run of the project link checker from a machine with normal internet access. R120 works only through a redirect and R137 uses an unusual capital letter in its path. Neither is broken, but both should be watched at that run.
