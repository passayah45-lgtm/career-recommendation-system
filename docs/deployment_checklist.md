# Deployment Checklist

Target: Streamlit Community Cloud (https://share.streamlit.io)
Repository: passayah45-lgtm/career-recommendation-system, branch main, main file app.py, Python 3.12
Live app URL: https://t-career-recommendation-2026.streamlit.app (deployed 2026-10-14 from branch main)

Status values: **verified locally**, **verified in CI**, **verified live**, **pending**. An item is only marked verified when the check was actually run.

## 1. Repository readiness

| Check | Status | Evidence |
|---|---|---|
| Entry point is app.py at the repository root | verified locally | Fresh clone of commit b0baea6 from GitHub, `streamlit run app.py` served HTTP 200 |
| requirements.txt in the root, all versions pinned | verified locally | 6 pinned packages, installed with uv on Python 3.12.3 in 28 seconds |
| Python 3.12 compatible | verified in CI | GitHub Actions runs on Python 3.12 |
| No system packages needed (no packages.txt) | verified locally | All packages installed from wheels |
| Data loaded with repository-relative paths | verified locally | Paths built from the module location (src/data/validation.py), no absolute paths in src, pages or app.py |
| No secrets, virtual environments or caches committed | verified locally | `git ls-files` and a secret-pattern search found none |
| App needs no secrets | verified locally | No st.secrets or environment variable is required. CAREER_DATA_DIR is optional |
| Tests and data validation pass | verified in CI | 247 tests, 0 validation errors, evaluation check reproducible (run 38622396327 on commit 715aa66) |

## 2. Automated checks (run on every push)

| Check | Status | Where |
|---|---|---|
| Every page starts without an exception | verified in CI | tests/test_app.py (Streamlit AppTest) |
| Assessment saves normalized input, reports unknown and duplicate skills | verified in CI | tests/test_app.py |
| Empty assessment is rejected | verified in CI | tests/test_app.py |
| Recommendations show service scores, reasons and the score disclaimer | verified in CI | tests/test_app.py |
| Top K slider changes the number of careers | verified in CI | tests/test_app.py |
| Skill gap shows coverage, resources and link status | verified in CI | tests/test_app.py |
| Explorer to Skill-Gap keeps a career outside the recommendations | verified in CI | tests/test_app.py |
| Explorer category filter and title search | verified in CI | tests/test_app.py |
| Analytics charts with and without a profile | verified in CI | tests/test_app.py |
| Reset clears the assessment | verified in CI | tests/test_app.py |
| Missing data shows an error message instead of a crash | verified in CI | tests/test_app.py |
| Sidebar titles are explicit (Home, not "app") | verified in CI | tests/test_app.py |

## 3. Local browser smoke test (headless Chromium, before deployment)

Run on 2026-10-14 against `streamlit run app.py` from a fresh clone of commit b0baea6, with Chromium through Playwright. This is a real browser, but on the development machine, not on Community Cloud.

| Check | Status | Notes |
|---|---|---|
| Home page renders with 50 careers, 8 categories, 114 skills, 114 resources | verified locally | Desktop 1366 x 900 |
| Sidebar shows Home, Career Assessment, Recommendations, Skill-Gap Analysis, Career Explorer, Analytics | verified locally | |
| Recommendations page without a profile shows guidance | verified locally | |
| Empty assessment shows "add at least one skill" | verified locally | |
| Assessment with "Python, SQL, Excel, ML, statistics, blockchain" saves and reports "blockchain" | verified locally | |
| Recommendations show Data Scientist 61.5, Data Analyst 59.6, Financial Analyst 55.0 with reasons | verified locally | Matches the documented worked example |
| "Analyze my skill gap" opens Data Scientist with 80% required coverage | verified locally | From screenshot |
| Resource table shows link status "http checked" and an "Open resource" link | verified locally | From screenshot |
| Coverage and analytics charts render | verified locally | 3 dataset charts drawn |
| Career Explorer search "nurse" shows 1 of 50 careers | verified locally | |
| Phone width 390 px: no horizontal page scroll, Explorer usable | verified locally | |
| No JavaScript errors in the page | verified locally | |

## 4. Live deployment checks (do these on the deployed URL)

Open the live URL in Chrome on your laptop, and once on your phone. Mark each item when done.

| # | Check | How | Status |
|---|---|---|---|
| L1 | App builds and starts | Deploy log ends without errors, home page appears | verified live (author's screenshot, 2026-10-14) |
| L2 | Home page | Title, four numbers (50, 8, 114, 114), five "How it works" links | verified live (title and 50, 8, 114, 114 seen in screenshot) |
| L3 | Sidebar | Six entries starting with Home | verified live (screenshot) |
| L4 | Assessment input | Add skills from the list, type "ML, JS" in Other skills, pick 2 interests, education 3, save | pending |
| L5 | Unknown skill warning | Add "blockchain" to Other skills, save, see it listed as not in the dataset | pending |
| L6 | Empty input | Clear everything, save, see "add at least one skill" | pending |
| L7 | Ranked recommendations | Five careers in score order, each with a score out of 100 | pending |
| L8 | Explanations | "Why this career" bullets and the score breakdown add up to the score | pending |
| L9 | Top K | Move the slider to 10, ten careers appear | pending |
| L10 | Skill gap from a recommendation | Click "Analyze my skill gap" on rank 2, the page opens on that career | pending |
| L11 | Resources | "Open resource" opens the learning page, link status shows "http checked" or "search index confirmed" | pending |
| L12 | Explorer filters | Pick Healthcare (6 careers), search "nurse" (1 career) | pending |
| L13 | Explorer to skill gap | Pick Registered Nurse, click the skill-gap button, "All careers" is selected with Registered Nurse | pending |
| L14 | Analytics | Dataset tab shows 3 charts, Your results tab shows 2 charts | pending |
| L15 | Reset | "Start a new assessment" in the sidebar clears the answers | pending |
| L16 | Direct page links | Open the live URL with /Career_Explorer at the end, the page loads (with an empty session) | pending |
| L17 | Phone layout | Open the URL on your phone, open the sidebar with the arrow, complete one assessment | pending |
| L18 | Sleep and wake | After 12 hours without visitors, open the link and click "Yes, get this app back up!" | pending |
| L19 | Logs visible | While signed in, "Manage app" shows the logs | pending |

## 5. Known behaviour to explain during the demonstration

1. Refreshing the browser or typing a page URL starts a new session, so the assessment must be filled in again. Use the sidebar to move between pages.
2. The score ranks careers against this dataset. It is not a probability of being hired.
3. 10 of 114 resources show "search index confirmed" because their sites block automated checks (9) or their server was down during the check (Inkscape).
4. The first visit after a long pause can take about a minute while the app wakes up.

## 6. Recovery steps

| Problem | Action |
|---|---|
| Build fails | Open Manage app, read the last error in the logs, see the troubleshooting table in README.md |
| "The career data could not be loaded" | Run `python -m src.data.validation` locally, fix, push |
| App over its resource limits | Manage app, then Reboot app |
| App unreachable before the demo | Check https://www.streamlitstatus.com. Backup: run `streamlit run app.py` on the laptop |

## 7. Phase 6 UI redesign (2026-10-15)

Local headless Chromium run against `streamlit run app.py` with the redesigned interface, before pushing.

| Check | Status | Notes |
|---|---|---|
| Full learner flow at 1440, 1280, 820 and 390 px wide | verified locally | Assessment, recommendations, skill gap, explorer search, analytics: 50 of 50 checks passed |
| Worked-example scores unchanged (61.5, 59.6, 55.0) | verified locally | Same values as before the redesign |
| No horizontal scroll on any page at any of the four widths | verified locally | |
| Resource cards show the stored verification status | verified locally | Also covered by tests/test_app.py and tests/test_theme.py |
| No JavaScript page errors | verified locally | |
| Redesign visible on the live URL | pending | Open the live URL after the automatic redeploy and compare with docs/design_system.md |
| Phone layout on a real phone | pending | Sidebar opens with the arrow, home statistics show two per row |

Second pass on 2026-10-15, following the six-page reference image: hero illustration, icon tiles, score and coverage rings, clickable explorer list, category colors and education donut. The same 50 browser checks passed at the four widths, and a row click in the explorer list opened that career. Live status stays pending until checked on the deployed URL.
